from fastapi import FastAPI, Body
import google.generativeai as genai

# Replace with your actual API key
API_KEY = "api here"

app = FastAPI()

# Configure the generative AI library with your API key
genai.configure(api_key=API_KEY)

# Load the desired summarization model (replace with your model name)
model_name = "gemini-1.5-flash"
model = genai.GenerativeModel(model_name=model_name)

@app.post("/summarize")
async def summarize_text(text: str = Body(...)):
    """Summarizes a given text using the loaded GenerativeAI model."""

    try:
        summary = model.generate_content([text])
        return {"text": summary}
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return {"error": "Error during summarization"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)

