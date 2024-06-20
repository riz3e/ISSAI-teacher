import io
import torch
import scipy.io.wavfile
from transformers import VitsModel, AutoTokenizer
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse
from concurrent.futures import ThreadPoolExecutor
import requests
import asyncio
import logging

app = FastAPI()

# Load the text-to-speech model and tokenizer
tts_model = VitsModel.from_pretrained("facebook/mms-tts-kaz")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kaz")
logging.basicConfig(level=logging.DEBUG)

executor = ThreadPoolExecutor(max_workers=4)

def generate_audio_sync(text: str) -> io.BytesIO:
    try:
        inputs = tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            output = tts_model(**inputs).waveform

        # Prepare the audio file for download
        sample_rate = tts_model.config.sampling_rate
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, rate=sample_rate, data=output.squeeze().numpy())
        buffer.seek(0)

        return buffer

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during audio generation: {str(e)}")

@app.post("/generate_audio")
async def generate_audio(text: str = Form(...)):
    try:
        loop = asyncio.get_event_loop()
        buffer = await loop.run_in_executor(executor, generate_audio_sync, text)

        # Send the audio to the second server
        response = requests.post(
            "http://localhost:5004/a2f",
            files={"file": ("output.wav", buffer, "audio/wav")},
        )

        if response.status_code != 200:
            print("failed to send audio to a2f")
        #     raise HTTPException(status_code=response.status_code, detail="Failed to send audio to server")

        # Return the streaming response
        buffer.seek(0)  # Reset buffer position to the beginning
        return StreamingResponse(buffer, media_type="audio/wav", headers={"Content-Disposition": "attachment; filename=output.wav"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during audio generation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
