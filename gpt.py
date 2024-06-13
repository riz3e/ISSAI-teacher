import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # This is the default and can be comitted
    api_key=os.getenv('OPENAI_API_KEY')
)

def convo(msg: str ="", ):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": msg,
            }
        ],
        model="gpt-3.5-turbo",
    )


if __name__ == "__main__":
    convo(input("Your prompt: "))