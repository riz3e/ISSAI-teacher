from fastapi import FastAPI, Form
import torch
from transformers import VitsModel, AutoTokenizer
import scipy.io.wavfile
import io

app = FastAPI()

# Load the text-to-speech model and tokenizer
tts_model = VitsModel.from_pretrained("facebook/mms-tts-kaz")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kaz")

@app.post("/generate_audio/")
async def generate_audio(text: str = Form(...)):
    try:
        inputs = tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            output = tts_model(**inputs).waveform

        # Save the waveform to a bytes buffer
        sample_rate = tts_model.config.sampling_rate
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, rate=sample_rate, data=output.squeeze().numpy())
        buffer.seek(0)

        return {"audio": buffer}
    except Exception as e:
        return {"error": str(e)}
