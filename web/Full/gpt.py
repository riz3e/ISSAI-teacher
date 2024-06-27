import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException, FastAPI
from openai import OpenAI
from pydantic import BaseModel
from logger import log
import json

load_dotenv()

GPT_MODEL = "gpt-4o"

def create_openai_client():
    return OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )

def get_gpt_response(conversation_history: list, client):
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=conversation_history
    )
    return response.to_dict()['choices'][0]['message']['content']

class ConversationRequest(BaseModel):
    user_input: str
    conversation_history: list

app = FastAPI()
client = create_openai_client()

async def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    url = "https://issai.nu.edu.kz/tilmash/"
    params = {
        'translate': 'true',
        'from': from_lang,
        'to': to_lang,
        'text': text
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.text
        else:
            log.error(f"Translation error: Status code {response.status_code}")
            return f"Error: Unable to translate text. Status code: {response.status_code}"
    except requests.RequestException as e:
        log.error(f"Translation exception: {e}")
        return f"Error: An exception occurred - {e}"

@app.post("/chat")
async def chat(request: ConversationRequest):
    try:
        conversation_history = request.conversation_history
        user_input = await translate_text(request.user_input, 'kaz_Cyrl', 'eng_Latn')

        log.info(f"User input: {request.user_input}")

        conversation_history.append({"role": "user", "content": user_input})
        gpt_response_raw = get_gpt_response(conversation_history, client=client)

        try:
            gpt_response_content = json.loads(gpt_response_raw.replace('json', '').replace('`', ''))
        except json.JSONDecodeError as e:
            log.error(f"JSON decoding error: {e}")
            log.error(gpt_response_raw)
            raise HTTPException(status_code=500, detail="Error decoding GPT response")

        log.info(f"GPT-4 response: {gpt_response_content}")

        translated_resp_user = await translate_text(gpt_response_content.get("resp_user", ""), "eng_Latn", 'kaz_Cyrl')
        gpt_response_content["resp_user"] = translated_resp_user

        gpt_response_json = json.dumps(gpt_response_content, ensure_ascii=False)

        return {
            "response": gpt_response_json,
            'conversation_history': conversation_history
        }
    except Exception as e:
        log.error(f"An error occurred in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5004)
