from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import vosk
import tempfile
import uvicorn
import shutil
import subprocess

from transcribe import transcribe_audio

app = FastAPI()

model = vosk.Model("../vosk-model-kz-0.15")

app.mount("/static", StaticFiles(directory="../front/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    with open("../front/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.post("/upload/{user_id}")
async def upload_file(user_id: str, file: UploadFile = File(...)):
    if file.content_type not in ['audio/mpeg', 'audio/wav']:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an MP3 or WAV file.")

    temp_dir = tempfile.gettempdir()
    user_dir = os.path.join(temp_dir, user_id)
    os.makedirs(user_dir, exist_ok=True)
    input_file_path = os.path.join(user_dir, file.filename)

    with open(input_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.content_type == 'audio/mpeg':
        output_file_path = os.path.join(user_dir, "converted.wav")
        subprocess.run(["ffmpeg", "-i", input_file_path, output_file_path], check=True)
    else:
        output_file_path = input_file_path

    # Transcribe the audio file
    transcription = transcribe_audio(file_path=output_file_path, model=model)

    return {"message": "File uploaded and transcribed successfully", "transcription": transcription}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
