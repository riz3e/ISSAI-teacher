from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()

@app.post("/saved")
async def send_file_to_transcribe():
    file_path = "documents/recordings/recording.wav"  # ROFL CODE
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Read the file content
    with open(file_path, "rb") as file:
        file_content = file.read()
    
    # Prepare the file for uploading
    files = {'file': ('recording.wav', file_content, 'audio/wav')}
    
    # Send the file to localhost:5001/transcribe
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:5001/transcribe", files=files)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to transcribe file")
    
    return {"detail": "File sent for transcription"}
