import subprocess
from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil

app = FastAPI()

def execute_command(audio_path: str):
    command = f"python test_audio.py {audio_path} abrikos"
    subprocess.run(command, shell=True)

@app.post("/receive_audio")
async def receive_audio(file: UploadFile = File(...)):
    try:
        file_location = f"received_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Execute the command with the audio file path
        execute_command(file_location)

        # Return a success message
        return {"message": "Audio received successfully and command executed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during audio reception: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
