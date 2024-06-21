import shutil
import soundfile as sf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from audio2face_streaming_utils import push_audio_track
import librosa

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
            speech_array = resample_audio(speech_array, sampling_rate, 16000)
            sampling_rate = 16000

        # Send the audio to audio2face
        audio2face(speech_array, sampling_rate)

        # Prepare the response
        response = {
            "audio_buffer": speech_array.tolist(),  # Convert numpy array to list for JSON serialization
            "sampling_rate": sampling_rate
        }

        return JSONResponse(content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during audio reception: {str(e)}")

def resample_audio(audio, orig_freq, new_freq):
    resampled_audio = librosa.resample(audio, orig_freq, new_freq)
    return resampled_audio

def audio2face(audio_buffer, sample_rate):
    a2f_url = '127.0.0.1:50051'  # a2f URL, default one
    a2f_avatar_instance = '/World/audio2face/PlayerStreaming'  # Streaming instance in a2f

    push_audio_track(a2f_url, audio_buffer, sample_rate, a2f_avatar_instance)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
