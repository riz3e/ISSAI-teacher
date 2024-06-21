import os
from dotenv import load_dotenv
from fastapi import HTTPException, FastAPI
from flask import jsonify
from openai import OpenAI
from pydantic import BaseModel
from logger import log

load_dotenv()

SECRET_KEY = "SMTN"
GPT_MODEL = "gpt-4"

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

def summarize_conversation(conversation_history: list, client):
    summary_prompt = [
        {"role": "system", "content": "Summarize the following conversation briefly."},
        {"role": "user", "content": str(conversation_history)}
    ]
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=summary_prompt
    )
    return response.to_dict()['choices'][0]['message']['content']

class ConversationRequest(BaseModel):
    user_input: str
    conversation_history: list

app = FastAPI()

client = create_openai_client()

@app.post("/chat")
async def chat(request: ConversationRequest):
    try:
        conversation_history = request.conversation_history
        log.info(f"User input: {request.user_input}")

        # Summarize the conversation history
        summarized_history = summarize_conversation(conversation_history, client)
        log.info(f"Summarized conversation history: {summarized_history}")

        # Append new user message to the conversation history
        conversation_history.append({"role": "user", "content": request.user_input})

        gpt_response = get_gpt_response(conversation_history, client=client)
        conversation_history.append({"role": "assistant", "content": gpt_response})

        log.info(f"GPT-4 response: {gpt_response}")

        return {"response": gpt_response,
                'conversation_history': conversation_history}
    except Exception as e:
        log.error(f"An error occurred in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    conversation_history = []

    print("Start a conversation with GPT-4 (type 'exit' to stop):")
    try:
        client = create_openai_client()

        while True:
            user_input = input("You: ")

            if user_input.lower() == 'exit':
                print("Ending conversation.")
                break

            # Summarize the conversation history
            summarized_history = summarize_conversation(conversation_history, client)
            print(f"Summarized conversation history: {summarized_history}")

            # Append new user message to the conversation history
            conversation_history.append({"role": "user", "content": user_input})

            gpt_response = get_gpt_response(conversation_history, client=client)
            conversation_history.append({"role": "assistant", "content": gpt_response})

            print(f"GPT-4: {gpt_response}")
    except Exception as e:
        log.error(f"An error occurred: {str(e)}")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5004)
