from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import wave
import json
import os

app = FastAPI()

# Load the Vosk model
model_path = r"C:\Users\user2\Desktop\avatar\vosk\vosk-model-kz-0.15"
vosk_model = Model(model_path)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save the uploaded file
    audio_path = f"temp/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(file.file.read())

    # Convert audio to wav format if necessary
    if file.filename.endswith(".mp3"):
        try:
            audio = AudioSegment.from_mp3(audio_path)
            audio_path = audio_path.replace(".mp3", ".wav")
            audio.export(audio_path, format="wav")
        except Exception as e:
            return {"error": f"Failed to convert MP3 to WAV: {str(e)}"}

    # Ensure the file exists before attempting to transcribe
    if not os.path.exists(audio_path):
        return {"error": "Uploaded file does not exist"}

    # Transcribe the wav audio file
    transcription = transcribe_wav(audio_path)

    # Clean up the temporary file
    os.remove(audio_path)

    return {"transcription": transcription}

def transcribe_wav(wav_path):
    # Open the wav file
    wf = wave.open(wav_path, "rb")
    recognizer = KaldiRecognizer(vosk_model, wf.getframerate())

    # Transcription result
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


if __name__ == "__main__":
    import uvicorn
    os.makedirs("temp", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=5001)
