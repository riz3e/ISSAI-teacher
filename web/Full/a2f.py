import shutil
import soundfile as sf
import torch
import torchaudio
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from audio2face_streaming_utils import push_audio_track

app = FastAPI()

@app.post("/receive_audio")
async def receive_audio(file: UploadFile = File(...)):
    try:
        # Create a temporary file to save the uploaded file
        file_location = f"received_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            

        # Load audio file using soundfile
        speech_array, sampling_rate = sf.read(file_location)

        # Resample audio to 16000 Hz if necessary
        if sampling_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=16000)
            speech_tensor = torch.tensor(speech_array, dtype=torch.float32).unsqueeze(0)
            speech_array = resampler(speech_tensor).squeeze().numpy()
            sampling_rate = 16000

        # Execute the command with the audio file path (optional)
        # execute_command(file_location)
        audio2face(speech_array, sampling_rate)

        # Prepare the response
        response = {
            "audio_buffer": speech_array.tolist(),  # Convert numpy array to list for JSON serialization
            "sampling_rate": sampling_rate
        }

        return JSONResponse(content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during audio reception: {str(e)}")

def audio2face(audio_buffer, sample_rate):
    # HARDCODEEEEEE

    a2f_url = '127.0.0.1:50051' # a2f url, default one
    a2f_avatar_instance = '/World/audio2face/PlayerStreaming' # Streaming instance in a2f

    push_audio_track(a2f_url, audio_buffer, sample_rate, a2f_avatar_instance)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)