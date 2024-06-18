from fastapi import FastAPI, Form, HTTPException
import google.generativeai as genai

app = FastAPI()

API_KEY = "AIzaSyAgBt0ro1rQQsKCjcMm1lmjJVAIT4B_ecM"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/generate_audio")
async def generate_audio(text: str = Form(...)):
    try:
        if not text:
            raise HTTPException(status_code=400, detail="No text provided for summarization")
        
        summary = model.generate_content(text)
        return {"text": summary.text}
    
    except Exception as e:
        return {"error": f"Error during summarization: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
