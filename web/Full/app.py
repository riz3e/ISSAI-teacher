# import os
from flask import Flask, request, jsonify, send_file, render_template
import requests  # Ensure requests module is imported for making HTTP requests
import io  # Import io module for working with byte streams

app = Flask(__name__)

# Your existing code...

TRANSCRIBE_SERVICE_URL = "http://localhost:5001/transcribe"
TTS_SERVICE_URL = "http://localhost:5002/generate_audio"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio-file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['audio-file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Forward the request to the transcribe microservice
        files = {'audio-file': (file.filename, file.stream, file.content_type)}
        response = requests.post(TRANSCRIBE_SERVICE_URL, files=files)
        transcription = response.json()['transcription']
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'transcription': transcription})

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    text = request.form['text']

    try:
        # Forward the request to the text-to-speech microservice
        response = requests.post(TTS_SERVICE_URL, data={'text': text})
        audio_data = response.content
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(io.BytesIO(audio_data), as_attachment=True, download_name='output.wav', mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
