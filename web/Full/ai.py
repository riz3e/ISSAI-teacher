from fastapi import FastAPI, Form, HTTPException
import google.generativeai as genai
import logging
import os
from dotenv import load_dotenv
from concurrent.futures import Executor, ThreadPoolExecutor
import asyncio

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

executor = ThreadPoolExecutor(max_workers=4)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
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
)
chat_session = model.start_chat(history=[])

kazakh_to_iso9 = {
    'А': 'A', 'Ә': 'Á', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Ғ': 'Ǵ', 'Д': 'D',
    'Е': 'E', 'Ё': 'Ë', 'Ж': 'Ž', 'З': 'Z', 'И': 'I', 'Й': 'J', 'К': 'K',
    'Қ': 'Q', 'Л': 'L', 'М': 'M', 'Н': 'N', 'Ң': 'Ń', 'О': 'O', 'Ө': 'Ö',
    'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ұ': 'Ú', 'Ү': 'Ü',
    'Ф': 'F', 'Х': 'H', 'Һ': 'Ḩ', 'Ц': 'C', 'Ч': 'Č', 'Ш': 'Š', 'Щ': 'Ŝ',
    'Ъ': 'ʺ', 'Ы': 'Y', 'І': 'Ì', 'Ь': 'ʹ', 'Э': 'È', 'Ю': 'Û', 'Я': 'Â',
    'а': 'a', 'ә': 'á', 'б': 'b', 'в': 'v', 'г': 'g', 'ғ': 'ǵ', 'д': 'd',
    'е': 'e', 'ё': 'ë', 'ж': 'ž', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k',
    'қ': 'q', 'л': 'l', 'м': 'm', 'н': 'n', 'ң': 'ń', 'о': 'o', 'ө': 'ö',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ұ': 'ú', 'ү': 'ü',
    'ф': 'f', 'х': 'h', 'һ': 'ḩ', 'ц': 'c', 'ч': 'č', 'ш': 'š', 'щ': 'ŝ',
    'ъ': 'ʺ', 'ы': 'y', 'і': 'ì', 'ь': 'ʹ', 'э': 'è', 'ю': 'û', 'я': 'â'
}

def translate_to_iso9(kazakh_text):
    # Translate each character in the input text
    translated_text = ''.join(kazakh_to_iso9.get(char, char) for char in kazakh_text)
    return translated_text

def summarize_sync(text: str) -> str:
    try:
        logging.debug(f"Received text: {text}")

        if not text:
            raise HTTPException(status_code=400, detail="No text provided for summarization")

        translated_text = f"{translate_to_iso9(text)}. Answer like its a real human dialogue."
        logging.debug(f"Translated text: {translated_text}")

        response = chat_session.send_message(translated_text)
        logging.debug(f"API response: {response}")

        if not response or not response.text:
            raise HTTPException(status_code=500, detail="Failed to get a valid response from the API")

        summary = response.text
        logging.debug(f"Summary: {summary}")

        return summary

    except Exception as e:
        logging.error(f"Error during summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during summarization: {str(e)}")

@app.post("/summarize")
async def summarize(text: str = Form(...)):
    try:
        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(executor, summarize_sync, text)
        return {"summary": summary}
    
    except Exception as e:
        logging.error(f"Error during summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during summarization: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
