# transcription_service.py
import os
from flask import Flask, request, jsonify
import torch
import torchaudio
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import scipy.io.wavfile
import io

app = Flask(__name__)

processor = Wav2Vec2Processor.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")
model = Wav2Vec2ForCTC.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio-file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['audio-file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    try:
        transcription = transcribe_audio(file_path)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(file_path)

    return jsonify({'transcription': transcription})

def transcribe_audio(audio_file):
    try:
        speech_array, sampling_rate = sf.read(audio_file)
        if sampling_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=16000)
            speech_tensor = torch.tensor(speech_array, dtype=torch.float32).unsqueeze(0)
            speech_array = resampler(speech_tensor).squeeze().numpy()
            sampling_rate = 16000

    except Exception as e:
        print(f"Error loading audio file: {e}")
        return str(e), 400

    inputs = processor(speech_array, sampling_rate=16000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    return transcription

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(port=5001)  # Choose a port different from your main application
