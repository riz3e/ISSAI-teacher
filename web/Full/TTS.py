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
from convert_to_mp3 import convert_wav_to_mp3

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
        logging.error(f"Error during audio generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during audio generation: {str(e)}")

@app.post("/generate_audio")
async def generate_audio(text: str = Form(...), format: str = Form("wav")):
    try:
        loop = asyncio.get_event_loop()
        buffer = await loop.run_in_executor(executor, generate_audio_sync, text)

        # Convert to MP3 if requested
        if format == "mp3":
            buffer = await loop.run_in_executor(executor, convert_wav_to_mp3, buffer)
            media_type = "audio/mpeg"
            filename = "output.mp3"
        else:
            media_type = "audio/wav"
            filename = "output.wav"

        # Reset buffer position to the beginning
        buffer.seek(0)

        # Send the audio to the second server
        response = requests.post(
            "http://localhost:5005/receive_audio",
            files={"file": (filename, buffer, media_type)},
        )

        if response.status_code != 200:
            logging.error("Failed to send audio to server")
            raise HTTPException(status_code=response.status_code, detail="Failed to send audio to server")

        # Return the streaming response
        buffer.seek(0)  # Reset buffer position to the beginning
        return StreamingResponse(buffer, media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})

    except Exception as e:
        logging.error(f"Error during audio generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during audio generation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
