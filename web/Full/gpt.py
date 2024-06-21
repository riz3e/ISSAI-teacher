import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from logger import log

# Load environment variables from .env file
load_dotenv()

# Ensure you have set OPENAI_API_KEY in your .env file
GPT_MODEL = "gpt-4"

# Function to create OpenAI client
def create_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    return OpenAI(api_key=api_key)

# Function to get response from GPT model
def get_gpt_response(conversation_history: list, client):
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=conversation_history
    )
    return response.choices[0].message['content']

# Define the request model
class ConversationRequest(BaseModel):
    user_input: str
    conversation_history: list

# Initialize FastAPI app
app = FastAPI()

# Create OpenAI client
client = create_openai_client()

@app.post("/chat")
async def chat(request: ConversationRequest):
    try:
        conversation_history = request.conversation_history
        user_input = request.user_input

        # Log user input
        log.info(f"User input: {user_input}")

        # Append user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Get response from GPT model
        gpt_response = get_gpt_response(conversation_history, client=client)
        
        # Append GPT response to conversation history
        conversation_history.append({"role": "assistant", "content": gpt_response})

        # Log GPT response
        log.info(f"GPT-4 response: {gpt_response}")

        return {"response": gpt_response, 'conversation_history': conversation_history}
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

            # Append user input to conversation history
            conversation_history.append({"role": "user", "content": user_input})

            # Get response from GPT model
            gpt_response = get_gpt_response(conversation_history, client=client)
            
            # Append GPT response to conversation history
            conversation_history.append({"role": "assistant", "content": gpt_response})

            print(f"GPT-4: {gpt_response}")
    except Exception as e:
        log.error(f"An error occurred: {str(e)}")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5004)
