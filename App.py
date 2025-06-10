from flask import Flask, request, jsonify
import os
import subprocess
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
import uuid

app = Flask(__name__)

# Load whisper model once (small model is fast & uses low memory)
model = WhisperModel("base", compute_type="int8")  # or "tiny" for ultra-low resource

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "YouTube URL is required."}), 400

    try:
        audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': "ffmpeg"  # adjust if needed
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        segments, info = model.transcribe(audio_filename)
        full_text = " ".join([segment.text for segment in segments])

        os.remove(audio_filename)

        return jsonify({"transcript": full_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

