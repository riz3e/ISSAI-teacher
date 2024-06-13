import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # This is the default and can be comitted
    api_key=os.getenv('OPENAI_API_KEY')
)

msg = str(input("Enter Prompt: "))

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": msg,
        }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion.choices[0].message.content)