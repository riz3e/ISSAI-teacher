import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

load_dotenv()

GPT_MODEL = "gpt-3.5-turbo"
HISTORY_FILE = "conversation_history.json"

def createOperAIClient():
    return OpenAI(
        # This is the default and can be comitted
        api_key=os.getenv('OPENAI_API_KEY')
    )


def get_gpt_response(conversation_history: list, client):
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=conversation_history
    )
    # print(response)
    response = response.to_dict()
    # print(json.dumps(response, indent=4))
    return response['choices'][0]['message']['content']



def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    return []

def save_conversation_history(conversation_history):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(conversation_history, file)

class ConversationRequest(BaseModel):
    user_input: str

# Create an OpenAI client once and reuse it
client = createOperAIClient()

# Assume this FastAPI app already exists in your code
Router = APIRouter()

@Router.post("/chat")
async def chat(request: ConversationRequest):
    try:
        # Load the conversation history from the local storage
        conversation_history = load_conversation_history()

        # Append user input to the conversation history
        conversation_history.append({"role": "user", "content": request.user_input})

        # Get GPT response
        gpt_response = get_gpt_response(conversation_history, client=client)

        # Append GPT response to conversation history
        conversation_history.append({"role": "assistant", "content": gpt_response})

        # Save the updated conversation history back to the local storage
        save_conversation_history(conversation_history)

        return {"response": gpt_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    conversation_history = []

    print("Start a conversation with GPT-4 (type 'exit' to stop):")
    try:
        client = createOperAIClient()

        while True:
            # Get user input
            user_input = input("You: ")

            if user_input.lower() == 'exit':
                print("Ending conversation.")
                break

            # Append user input to conversation history
            conversation_history.append({"role": "user", "content": user_input})

            # Get GPT response
            gpt_response = get_gpt_response(conversation_history, client=client)

            # Append GPT response to conversation history
            conversation_history.append({"role": "assistant", "content": gpt_response})

            # Print GPT response
            print(f"GPT-4: {gpt_response}")
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
