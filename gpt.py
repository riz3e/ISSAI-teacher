import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # This is the default and can be comitted
    api_key=os.getenv('OPENAI_API_KEY')
)


def get_response(msg: str = "", ):
    model = "gpt-3.5-turbo"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": msg,
            }
        ],
        model=model,
    )

    response_dict = chat_completion.to_dict()
    return response_dict['choices'][0]['message']['content'],


if __name__ == "__main__":
    answer = get_response(input("Your prompt: "))
    print(answer)
