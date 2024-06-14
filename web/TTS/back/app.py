from flask import Flask, request, send_file, render_template
from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile
import io

app = Flask(__name__)

# Load model and tokenizer once
model = VitsModel.from_pretrained("facebook/mms-tts-kaz")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kaz")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    text = request.form['text']
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs).waveform

    # Save the waveform to a bytes buffer
    sample_rate = model.config.sampling_rate
    buffer = io.BytesIO()
    scipy.io.wavfile.write(buffer, rate=sample_rate, data=output.squeeze().numpy())
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='output.wav', mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
