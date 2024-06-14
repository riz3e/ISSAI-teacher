from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import vosk
import tempfile
import uvicorn

from transcribe import transcribe_audio

app = FastAPI()

model = vosk.Model("path_to_vosk_model")

@app.post("/upload/{user_id}")
async def upload_file(user_id: str, file: UploadFile = File(...)):
    if file.content_type != 'audio/mpeg':
        raise HTTPException(status_code=400, detail="Invalid file type")

    temp_dir = tempfile.gettempdir()
    user_dir = os.path.join(temp_dir, user_id)
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Transcribe the audio file
    transcription = transcribe_audio(file_path=file_path, model=model)
    
    return {"message": "File uploaded and transcribed successfully", "transcription": transcription}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
