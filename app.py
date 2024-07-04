from flask import Flask, render_template, request, send_file
from pytube import YouTube
from moviepy.editor import AudioFileClip
import os
import re

app = Flask(__name__)

def is_valid_youtube_url(url):
    regex = re.compile(
        r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$')
    return re.match(regex, url) is not None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        start_time = int(request.form['start_time'])
        end_time = int(request.form['end_time'])

        if not is_valid_youtube_url(url):
            return "Invalid YouTube URL"

        try:
            print(f"Received URL: {url}")

            yt = YouTube(url)
            print(f"Video Title: {yt.title}")

            video = yt.streams.filter(only_audio=True).first()
            print(f"Downloading audio stream: {video.url}")

            video.download(filename='temp.mp4')
            print("Download complete.")

            # Extract audio from the specified timeframe
            audio_clip = AudioFileClip('temp.mp4').subclip(start_time, end_time)
            audio_clip.write_audiofile('output.mp3')
            print("Audio extraction complete.")

            # Clean up
            os.remove('temp.mp4')
            print("Temporary file removed.")

            return send_file('output.mp3', as_attachment=True)

        except Exception as e:
            print(f"Error: {e}")
            return f"An error occurred: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
