from fastapi import FastAPI, Body, Form
import google.generativeai as genai

# Replace with your actual API key
API_KEY = ""

app = FastAPI()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')


@app.post("/summarize")
async def summarize_text(text: str = Form(...)):
    """Summarizes a given text using the loaded GenerativeAI model."""
    try:
        if not text:
            return {"error": "No text provided for summarization"}
        summary = model.generate_content(text)
        return {"text": summary.text}
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return {"error": f"Error during summarization: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
