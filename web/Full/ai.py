from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from pathlib import Path

app = FastAPI()

class TranscriptionRequest(BaseModel):
    string: str

@app.post("/saved")
async def send_file_to_transcribe(request: TranscriptionRequest):
    if request.string != "saved":
        return {"detail": "File not sent"}
    
    file_path = Path(r"C:\Users\admin\Documents\recordings\recording.wav")  # Replace with the correct path
    
    # Check if the file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Read the file content
    with file_path.open("rb") as file:
        file_content = file.read()
    
    # Prepare the file for uploading
    files = {'file': ('recording.wav', file_content, 'audio/wav')}
    
    # Send the file to localhost:5001/transcribe
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:5001/transcribe", files=files)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to transcribe file")
    
    return {"detail": "File sent for transcription"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)