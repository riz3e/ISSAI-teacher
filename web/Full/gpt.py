import os

import requests
from dotenv import load_dotenv
from fastapi import HTTPException, FastAPI
from openai import OpenAI
from pydantic import BaseModel
from logger import log
import json

load_dotenv()

SECRET_KEY = "SMTN"
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

summarizerClient = create_openai_client()


async def translateText(text: str, From: str, to: str) -> str:
    # Define the URL and the parameters
    url = "https://issai.nu.edu.kz/tilmash/"
    params = {
        'translate': 'true',
        'from': From, #   'kaz_Cyrl'
        'to': to,   #   'eng_Latn'
        'text': text
    }

    try:
        # Send the GET request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Return the response text
            return response.text
        else:
            # Return an error message
            return f"Error: Unable to translate text. Status code: {response.status_code}"
    except requests.RequestException as e:
        # Return an error message if there was an exception
        return f"Error: An exception occurred - {e}"


@app.post("/chat")
async def chat(
    request: ConversationRequest,
):
    try:


        conversation_history = request.conversation_history
        
        user_input = await translateText(request.user_input, 'kaz_Cyrl', 'eng_Latn')

        log.info(f"User input: {request.user_input}")

        conversation_history.append({"role": "user", "content": user_input})

        gpt_response = get_gpt_response(conversation_history, client=client)
        gpt_response_content = json.loads(gpt_response)
        conversation_history.append({"role": "assistant", "content": gpt_response})

        log.info(f"GPT-4 response: {gpt_response}")

        translated_resp_user = await translateText(gpt_response_content["resp_user"], "eng_Latn", 'kaz_Cyrl')
        print("respuserss", gpt_response_content["resp_user"])
        gpt_response_content["resp_user"] = translated_resp_user

        gpt_response = json.dumps(gpt_response_content)
        return {"response": gpt_response,
                'conversation_history': conversation_history}
    except Exception as e:
        log.error(f"An error occurred in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# def main():
#     conversation_history = []
#
#     print("Start a conversation with GPT-3.5 (type 'exit' to stop):")
#     try:
#         client = create_openai_client()
#
#         while True:
#             user_input = input("You: ")
#
#             if user_input.lower() == 'exit':
#                 print("Ending conversation.")
#                 break
#
#             conversation_history.append({"role": "user", "content": user_input})
#
#             gpt_response = get_gpt_response(conversation_history, client=client)
#             conversation_history.append({"role": "assistant", "content": gpt_response})
#
#             print(f"GPT-3.5: {gpt_response}")
#     except Exception as e:
#         log.error(f"An error occurred: {str(e)}")
#         raise e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5004)
