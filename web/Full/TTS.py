import io
import torch
import scipy.io.wavfile
from transformers import VitsModel, AutoTokenizer
from fastapi import FastAPI, Form, HTTPException

app = FastAPI()

# Load the text-to-speech model and tokenizer
tts_model = VitsModel.from_pretrained("facebook/mms-tts-kaz")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kaz")

@app.post("/generate_audio")
async def generate_audio(text: str = Form(...)):
    try:
        inputs = tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            output = tts_model(**inputs).waveform

        # Prepare the audio file for download
        sample_rate = tts_model.config.sampling_rate
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, rate=sample_rate, data=output.squeeze().numpy())
        buffer.seek(0)

        return {"audio": buffer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during audio generation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
