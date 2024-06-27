import shutil
import soundfile as sf
import torch
import torchaudio
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from audio2face_streaming_utils import push_audio_track
import os

app = FastAPI()

@app.post("/receive_audio")
async def receive_audio(file: UploadFile = File(...)):
    try:
        file_location = save_uploaded_file(file)
        
        speech_array, sampling_rate = load_audio_file(file_location)
        if sampling_rate != 16000:
            speech_array, sampling_rate = resample_audio(speech_array, sampling_rate)

        audio2face(speech_array, sampling_rate)
        response = prepare_response(speech_array, sampling_rate)

        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during audio reception: {str(e)}")
    finally:
        clean_up_file(file_location)

def save_uploaded_file(file: UploadFile) -> str:
    file_location = f"received_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_location

def load_audio_file(file_location: str):
    speech_array, sampling_rate = sf.read(file_location)
    return speech_array, sampling_rate

def resample_audio(speech_array, sampling_rate):
    resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=16000)
    speech_tensor = torch.tensor(speech_array, dtype=torch.float32).unsqueeze(0)
    speech_array = resampler(speech_tensor).squeeze().numpy()
    return speech_array, 16000

def audio2face(audio_buffer, sample_rate):
    a2f_url = '127.0.0.1:50051'  # a2f URL
    a2f_avatar_instance = '/World/audio2face/PlayerStreaming'  # Streaming instance in a2f
    push_audio_track(a2f_url, audio_buffer, sample_rate, a2f_avatar_instance)

def prepare_response(speech_array, sampling_rate):
    response = {
        "audio_buffer": speech_array.tolist(),  # Convert numpy array to list for JSON serialization
        "sampling_rate": sampling_rate
    }
    return response

def clean_up_file(file_location: str):
    try:
        if os.path.exists(file_location):
            os.remove(file_location)
    except Exception as e:
        print(f"Error cleaning up file: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
