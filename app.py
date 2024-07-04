from flask import Flask, render_template, request, send_file
from moviepy.editor import AudioFileClip
import os
import re
import logging
from yt_dlp import YoutubeDL

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

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
            app.logger.debug("Invalid YouTube URL: %s", url)
            return "Invalid YouTube URL"

        try:
            app.logger.debug("Received URL: %s", url)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            app.logger.debug("Download complete.")

            # Extract audio from the specified timeframe
            audio_clip = AudioFileClip('temp.mp3').subclip(start_time, end_time)
            audio_clip.write_audiofile('output.mp3')
            app.logger.debug("Audio extraction complete.")

            # Clean up
            os.remove('temp.mp3')
            app.logger.debug("Temporary file removed.")

            return send_file('output.mp3', as_attachment=True)

        except Exception as e:
            app.logger.error("Error: %s", e)
            return f"An error occurred: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
