from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import StreamingResponse
import io
#TODO Import KazTTS here
import synthesize 

app = FastAPI()

@app.post("/synthesize")
async def synthesize_text(text: str = Form(...)):

    #TODO: make it work
    # Synthesize audio from the text using the provided function
    audio_bytes = synthesize.synth(text)

    # Return the synthesized audio as a streaming response
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
