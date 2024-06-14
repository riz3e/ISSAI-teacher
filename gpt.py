import os
from typing import List
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from logger import log

load_dotenv()

SECRET_KEY = "SMTN"
GPT_MODEL = "gpt-3.5-turbo"


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


class ConversationHistory(BaseModel):
    history: List[dict] = []


Router = APIRouter()

client = create_openai_client()


@Router.post("/chat")
async def chat(
    request: ConversationRequest,
    session_data: ConversationHistory
):
    try:
        conversation_history = session_data.history
        log.info(f"User input: {request.user_input}")

        conversation_history.append({"role": "user", "content": request.user_input})

        gpt_response = get_gpt_response(conversation_history, client=client)
        conversation_history.append({"role": "assistant", "content": gpt_response})

        log.info(f"GPT-4 response: {gpt_response}")

        return {"response": gpt_response}
    except Exception as e:
        log.error(f"An error occurred in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    conversation_history = []

    print("Start a conversation with GPT-3.5 (type 'exit' to stop):")
    try:
        client = create_openai_client()

        while True:
            user_input = input("You: ")

            if user_input.lower() == 'exit':
                print("Ending conversation.")
                break

            conversation_history.append({"role": "user", "content": user_input})

            gpt_response = get_gpt_response(conversation_history, client=client)
            conversation_history.append({"role": "assistant", "content": gpt_response})

            print(f"GPT-3.5: {gpt_response}")
    except Exception as e:
        log.error(f"An error occurred: {str(e)}")
        raise e


if __name__ == "__main__":
    main()
