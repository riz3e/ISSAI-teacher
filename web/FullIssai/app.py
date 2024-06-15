from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
from utils.audio_conversion import convert_audio_to_wav
from utils.speech_to_text import transcribe_audio
from utils.text_to_speech import generate_speech

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    text = request.form['text']
    audio_path = generate_speech(text)
    return send_file(audio_path, as_attachment=True)

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    temp_audio = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_audio.name)

    wav_path = convert_audio_to_wav(temp_audio.name)
    text_result = transcribe_audio(wav_path)

    os.remove(temp_audio.name)
    os.remove(wav_path)

    return jsonify({'text': text_result})

if __name__ == '__main__':
    app.run(debug=True)
