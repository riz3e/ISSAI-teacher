import io
import os
import numpy as np
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse
from concurrent.futures import ThreadPoolExecutor
import requests
import asyncio
import logging
import gpt
import uuid
import random

app = FastAPI()
client = gpt.client

logging.basicConfig(level=logging.DEBUG)

executor = ThreadPoolExecutor(max_workers=4)

def generate_audio_sync(text: str) -> io.BytesIO:
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=text
        )

        buffer = io.BytesIO()

        # Write the response content to the buffer
        for chunk in response.iter_bytes():
            buffer.write(chunk)
        
        buffer.seek(0)

        return buffer

    except Exception as e:
        logging.error(f"Error during audio generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during audio generation: {str(e)}")

@app.post("/generate_audio")
async def generate_audio(text: str = Form(...)):
    try:

        if text == "No response from GPT":
            raise HTTPException(status_code=500, detail=f"no resp from gpt")
        loop = asyncio.get_event_loop()
        buffer = await loop.run_in_executor(executor, generate_audio_sync, text)

        media_type = "audio/mp3"
        filename = f"output{str(uuid.uuid4())}.mp3"

        # Write the buffer to a local file
        local_file_path = fr"web\Full\uploads\{filename}"  # Replace with the desired local path
        with open(local_file_path, "wb") as f:
            f.write(buffer.getbuffer())

        logging.info(f"File saved locally at {local_file_path}")

        # Send the audio to the second server
        with open(local_file_path, "rb") as f:
            response = requests.post(
                "http://localhost:5005/receive_audio",
                files={"file": (filename, f, media_type)},
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
