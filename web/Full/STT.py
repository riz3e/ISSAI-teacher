import os
import io
import soundfile as sf
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI()

# Load the speech-to-text model and processor
processor = Wav2Vec2Processor.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")
model = Wav2Vec2ForCTC.from_pretrained("aismlv/wav2vec2-large-xlsr-kazakh")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as audio_file:
            audio_file.write(await file.read())

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

        return {"transcription": transcription}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

    finally:
        os.remove(file_path)  # Clean up the temporary file

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
