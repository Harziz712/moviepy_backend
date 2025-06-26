from flask import Flask, request, send_file
from moviepy.editor import *
import os, tempfile, requests

app = Flask(__name__)

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.json
    image_urls = data.get("images", [])
    voice_url = data.get("voice_url", "")
    video_title = data.get("title", "video")

    # Download voiceover
    voice_path = os.path.join(tempfile.gettempdir(), "voice.mp3")
    with open(voice_path, "wb") as f:
        f.write(requests.get(voice_url).content)

    audio = AudioFileClip(voice_path)
    duration = audio.duration

    # Download and create clips from images
    clips = []
    per_image_duration = duration / len(image_urls)

    for i, url in enumerate(image_urls):
        img_path = os.path.join(tempfile.gettempdir(), f"img_{i}.jpg")
        with open(img_path, "wb") as f:
            f.write(requests.get(url).content)
        clip = (ImageClip(img_path)
                .set_duration(per_image_duration)
                .resize(height=720)
                .set_position("center"))
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    output_path = os.path.join(tempfile.gettempdir(), f"{video_title}.mp4")
    video.write_videofile(output_path, fps=24, codec='libx264')

    return send_file(output_path, mimetype='video/mp4', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
