# Import necessary libraries
import os
from flask import Flask, request, jsonify, send_file, render_template
import requests
import io

# Initialize Flask app
app = Flask(__name__)

# Microservice URLs (replace with your actual URLs)
TRANSCRIBE_SERVICE_URL = "http://localhost:5001/transcribe"
TTS_SERVICE_URL = "http://localhost:5002/generate_audio"
SUMMARY_API_URL = "http://localhost:5003/summarize"

# Placeholder for your existing code (e.g., user interface logic)
# ...

@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML template


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


@app.route('/summarize', methods=['POST'])
def summarize():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    if "text" not in data:
        return jsonify({'error': 'Missing "text" field in request body'}), 400

    text = data["text"]

    try:
        summary = requests.post(SUMMARY_API_URL, json={'text': text}).json()['text']
        return jsonify({'summary': summary})
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return jsonify({'error': 'Error during summarization'}), 500


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
