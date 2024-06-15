from vosk import Model, KaldiRecognizer
import wave
import json

# Load Vosk model
vosk_model = Model("vosk/vosk-model-kz-0.15")

def transcribe_audio(audio_path):
    recognizer = KaldiRecognizer(vosk_model, 16000)
    wf = wave.open(audio_path, "rb")
    recognizer.AcceptWaveform(wf.readframes(wf.getnframes()))
    result = recognizer.Result()
    text_result = json.loads(result).get('text', '')
    return text_result
