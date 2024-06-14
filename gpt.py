import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GPT_MODEL = "gpt-3.5-turbo"


def create_client():
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


def main():
    conversation_history = []

    print("Start a conversation with GPT-4 (type 'exit' to stop):")

    client = create_client()

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


if __name__ == "__main__":
    main()
