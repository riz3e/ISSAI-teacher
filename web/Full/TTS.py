# tts_service.py
import os
from flask import Flask, request, send_file
import torch
from transformers import VitsModel, AutoTokenizer
import scipy.io.wavfile
import io

app = Flask(__name__)

tts_model = VitsModel.from_pretrained("facebook/mms-tts-kaz")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kaz")

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    text = request.form['text']
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = tts_model(**inputs).waveform

    sample_rate = tts_model.config.sampling_rate
    buffer = io.BytesIO()
    scipy.io.wavfile.write(buffer, rate=sample_rate, data=output.squeeze().numpy())
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='output.wav', mimetype='audio/wav')

if __name__ == '__main__':
    app.run(port=5002)  # Choose a different port from the transcription service
