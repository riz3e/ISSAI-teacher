import logging
import os
import io
import soundfile as sf
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)


# Load the speech-to-text model and processor
processor = Wav2Vec2Processor.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")
model = Wav2Vec2ForCTC.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")

executor = ThreadPoolExecutor(max_workers=4)

class TranscriptionResult(BaseModel):
    transcription: str

def transcribe_audio_sync(file_path: str) -> str:
    try:
        # Load audio file using soundfile
        speech_array, sampling_rate = sf.read(file_path)

        if sampling_rate != 16000:
            # Resample audio to 16000 Hz if necessary
            resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=16000)
            speech_tensor = torch.tensor(speech_array, dtype=torch.float32).unsqueeze(0)
            speech_array = resampler(speech_tensor).squeeze().numpy()
            sampling_rate = 16000

        # Transcribe audio
        inputs = processor(speech_array, sampling_rate=16000, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]

        return transcription

    finally:
        os.remove(file_path)  # Clean up the temporary file

@app.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(file: UploadFile = File(...)):
    logging.info(f"Received file: {file.filename}")
    try:
        # Create the uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)

        # Save the uploaded file temporarily
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as audio_file:
            audio_file.write(await file.read())

        loop = asyncio.get_event_loop()
        transcription = await loop.run_in_executor(executor, transcribe_audio_sync, file_path)

        return {"transcription": transcription}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
