from fastapi import HTTPException
import vosk
import wave
import json

def transcribe_audio(file_path: str, model: vosk.Model) -> str:
    try:
        wf = wave.open(file_path, "rb")
    except wave.Error as e:
        raise HTTPException(status_code=400, detail=f"Error opening audio file: {e}")

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 44100, 48000]:
        raise HTTPException(status_code=400, detail="Audio file must be WAV format mono PCM with a supported sample rate.")

    rec = vosk.KaldiRecognizer(model, wf.getframerate())

    result = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result.append(json.loads(rec.Result()))

    result.append(json.loads(rec.FinalResult()))
    transcription = " ".join([res["text"] for res in result if "text" in res])

    return transcription
