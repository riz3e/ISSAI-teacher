from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import wave
import json
import os

app = FastAPI()

# Load the Vosk model
MODEL_PATH = r"web/Full/utils/vosk/vosk_model_inners_here"
vosk_model = Model(MODEL_PATH)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_path = save_uploaded_file(file)
    if not audio_path:
        return JSONResponse(content={"error": "Failed to save uploaded file"}, status_code=500)

    if file.filename.endswith(".mp3"):
        audio_path = convert_mp3_to_wav(audio_path)
        if not audio_path:
            return JSONResponse(content={"error": "Failed to convert MP3 to WAV"}, status_code=500)

    if not os.path.exists(audio_path):
        return JSONResponse(content={"error": "Uploaded file does not exist"}, status_code=400)

    transcription = transcribe_wav(audio_path)
    clean_up_file(audio_path)

    return {"transcription": transcription}

def save_uploaded_file(file: UploadFile) -> str:
    try:
        os.makedirs("temp", exist_ok=True)
        audio_path = f"temp/{file.filename}"
        with open(audio_path, "wb") as f:
            f.write(file.file.read())
        return audio_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def convert_mp3_to_wav(mp3_path: str) -> str:
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        wav_path = mp3_path.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")
        os.remove(mp3_path)  # Clean up the original MP3 file
        return wav_path
    except Exception as e:
        print(f"Error converting MP3 to WAV: {e}")
        return None

def transcribe_wav(wav_path: str) -> str:
    try:
        with wave.open(wav_path, "rb") as wf:
            recognizer = KaldiRecognizer(vosk_model, wf.getframerate())
            transcription = []

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get("text"):
                        transcription.append(result["text"])

            return "\n".join(transcription)
    except Exception as e:
        print(f"Error transcribing WAV file: {e}")
        return ""

def clean_up_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
