from fastapi import FastAPI, File, UploadFile
from typing import Optional
import torch
import torchaudio
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

app = FastAPI()

# Load the speech-to-text model and processor
processor = Wav2Vec2Processor.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")
model = Wav2Vec2ForCTC.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Load audio file using soundfile
        audio_data, sample_rate = await get_audio_data(file)
        
        if sample_rate != 16000:
            # Resample audio to 16000 Hz
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            audio_tensor = torch.tensor(audio_data, dtype=torch.float32).unsqueeze(0)  # Convert to tensor and add batch dimension
            audio_data = resampler(audio_tensor).squeeze().numpy()  # Resample and convert back to numpy array
            sample_rate = 16000

        # Process the audio
        inputs = processor(audio_data, sampling_rate=sample_rate, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        return {"transcription": transcription}
    except Exception as e:
        return {"error": str(e)}

async def get_audio_data(file: UploadFile):
    audio_file = await file.read()
    audio_data, sample_rate = sf.read(io.BytesIO(audio_file))
    return audio_data, sample_rate
