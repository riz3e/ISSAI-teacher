# import openai

# openai.api_key = "YOUR_GPT_API_KEY"

# def get_response(msg):
#     model = "gpt-3.5-turbo"
#     prompt = msg

#     response = openai.completion.create(
#         model=model,
#         prompt=prompt,
#         max_tokens=100  # Adjust the number of tokens based on your needs
#     )

#     return response.choices[0].text.strip()


# msg = str(input("Enter Prompt: "))
# print(get_response(msg))

import os
from openai import OpenAI

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