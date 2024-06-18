from fastapi import FastAPI, Form, HTTPException
import google.generativeai as genai
import logging

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)


API_KEY = ""
genai.configure(api_key=API_KEY)

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

def cyrillic_to_latin(text):
  """
  This function translates Cyrillic Kazakh characters to their Latin equivalents.

  **Note:** This script uses a basic mapping and might not cover all edge cases.

  Args:
      text: The text in Cyrillic Kazakh.

  Returns:
      The text in Latin Kazakh (if possible).
  """
  mapping = {
      "А": "A", "ә": "a", "Б": "B", "В": "V", "Г": "G", "Ғ": "Ğ",
      "Д": "D", "Е": "E", "Ё": "ÍO", "Ж": "J", "З": "Z", "И": "İ",
      "Й": "İ", "К": "K", "Қ": "Q", "Л": "L", "М": "M", "Н": "N",
      "Ң": "Ñ", "О": "O", "Ө": "Ö", "П": "P", "Р": "R", "С": "S",
      "Т": "T", "У": "U", "Ұ": "Ū", "Ү": "Ū", "Ф": "F", "Х": "H",
      "Һ": "Ḥ", "Ц": "Ts", "Ч": "Ş", "Ш": "Ş", "Щ": "Sc", "Ъ": "",
      "Ы": "Y", "І": "I", "Э": "E", "Ю": "IU", "Я": "Yа"
  }
  latin_text = ""
  for char in text:
    if char in mapping:
      latin_text += mapping[char]
    else:
      latin_text += char  # Keep characters not in the mapping
  return latin_text



@app.post("/summarize")
async def summarize(text: str = Form(...)):
    try:
        logging.debug(f"Received text: {text}")
        
        if not text:
            raise HTTPException(status_code=400, detail="No text provided for summarization")
        
        translated_text = cyrillic_to_latin(text)
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
