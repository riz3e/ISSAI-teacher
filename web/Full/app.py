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
        files = {'file': (file.filename, file.stream, file.content_type)}
        response = requests.post(TRANSCRIBE_SERVICE_URL, files=files)
        response.raise_for_status()
        transcription = response.json().get('transcription', '')
    except requests.RequestException as e:
        return jsonify({'error': f'Error during request to transcription service: {str(e)}'}), 500
    except KeyError:
        return jsonify({'error': 'Invalid response from transcription service'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'transcription': transcription})


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': "Empty!"}), 400

    try:
        response = requests.post(SUMMARY_API_URL, data={'text': text})
        response.raise_for_status()
        response_data = response.json()
        summary_text = response_data.get("text")

        print(summary_text)
       
    except requests.RequestException as e:
        return jsonify({'error': f'Error during request to Summary service: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'summary': summary_text})


@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    text = request.form['text']

    try:
        # Forward the request to the text-to-speech microservice
        response = requests.post(TTS_SERVICE_URL, data={'text': text})
        response.raise_for_status()
        audio_data = response.content
    except requests.RequestException as e:
        return jsonify({'error': f'Error during request to TTS service: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(io.BytesIO(audio_data), as_attachment=True, download_name='output.wav', mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
