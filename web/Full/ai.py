from fastapi import FastAPI, Form, HTTPException
import google.generativeai as genai
import logging
import os
from dotenv import load_dotenv

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)
chat_session = model.start_chat(
  history=[
  ]
)
# Define the translation mappings
translation_mapping = {
    'А': 'A', 'а': 'a', 'Ә': 'Ă', 'ә': 'ă', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g', 'Ғ': 'Gh', 'ғ': 'gh', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
    'Ё': 'Ë', 'ё': 'ë', 'Ж': 'Zh', 'ж': 'zh', 'З': 'Z', 'з': 'z', 'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k', 'Қ': 'Q', 'қ': 'q', 'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n', 'Ң': 'N͡g', 'ң': 'n͡g', 'О': 'O', 'о': 'o',
    'Ө': 'Ȯ', 'ө': 'ȯ', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r', 'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u', 'Ұ': 'Ū', 'ұ': 'ū', 'Ү': 'U̇', 'ү': 'u̇',
    'Ф': 'F', 'ф': 'f', 'Х': 'Kh', 'х': 'kh', 'Һ': 'Ḣ', 'һ': 'ḣ', 'Ц': 'T͡s', 'ц': 't͡s',
    'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Shch', 'щ': 'shch', 'Ъ': 'ʺ', 'ъ': 'ʺ',
    'Ы': 'Y', 'ы': 'y', 'І': 'Ī', 'і': 'ī', 'Ь': 'ʹ', 'ь': 'ʹ', 'Э': 'Ė', 'э': 'ė',
    'Ю': 'I͡u', 'ю': 'i͡u', 'Я': 'I͡a', 'я': 'i͡a'
}

def translate_to_iso(text):
    translated_text = ''
    for char in text:
        translated_text += translation_mapping.get(char, char)
    return translated_text




@app.post("/summarize")
async def summarize(text: str = Form(...)):
    try:
        logging.debug(f"Received text: {text}")
        
        if not text:
            raise HTTPException(status_code=400, detail="No text provided for summarization")
        
        translated_text = translate_to_iso(text)
        logging.debug(f"Translated text: {translated_text}")

        response = chat_session.send_message(translated_text)
        logging.debug(f"API response: {response}")

        if not response or not response.text:
            raise HTTPException(status_code=500, detail="Failed to get a valid response from the API")

        summary = response.text
        logging.debug(f"Summary: {summary}")

        return {"summary": summary}
    
    except Exception as e:
        logging.error(f"Error during summarization: {str(e)}")
        return {"error": f"Error during summarization: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
