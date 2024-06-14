import os
from typing import List
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.session_verifier import SessionVerifier
from openai import OpenAI

from pydantic import BaseModel

from logger import log


load_dotenv()

SECRET_KEY = "SMTN"  # not so important
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


class ConversationRequest(BaseModel):
    user_input: str


## old
# class SessionData(BaseModel):
#     username: str
#
# class ConversationHistory(SessionData):
#     history: List[dict]

# new
class ConversationHistory(BaseModel):
    history: List[dict] = []


# Assume this FastAPI app already exists in your code
Router = APIRouter()

SessionId = UUID  # Define SessionId as a string for simplicity

cookie_params = CookieParameters()

backend = InMemoryBackend[UUID, ConversationHistory]()
cookie = SessionCookie(
    cookie_name="session",
    secret_key=SECRET_KEY,
    identifier="general_verifier",
    auto_error=True,
    cookie_params=cookie_params,
)


class BasicVerifier(SessionVerifier[UUID, ConversationHistory]):
    def __init__(
            self,
            *,
            identifier: str,
            auto_error: bool,
            backend: InMemoryBackend[UUID, ConversationHistory],
            auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: ConversationHistory) -> bool:
        """If the session exists, it is valid"""
        return True


# class Verifier(BasicVerifier[SessionId, ConversationHistory]):
#     identifier = "general_verifier",
#     auto_error = True,
#     backend = backend,
#     auth_http_exception = HTTPException(status_code=403, detail="invalid session"),


verifier =BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="Invalid session"),
)
# Create an OpenAI client once and reuse it
client = createOperAIClient()


@Router.post("/chat")
async def chat(
        request: ConversationRequest,
        session_data: ConversationHistory = Depends(verifier)
):
    try:
        # Load conversation history from session
        conversation_history = session_data.history

        # Append user input to conversation history
        conversation_history.append({"role": "user", "content": request.user_input})

        # Get GPT response
        gpt_response = get_gpt_response(conversation_history, client=client)

        # Append GPT response to conversation history
        conversation_history.append({"role": "assistant", "content": gpt_response})

        # Save the updated conversation history back to the session
        session_data.history = conversation_history
        await backend.update(session_data.session_id, session_data)

        return {"response": gpt_response}
    except Exception as e:
        log.error(f"An error occurred in chat endpoint: {str(e)}")
        print(1)
        raise HTTPException(status_code=500, detail=str(e))


@Router.get("/create_session")
# async def create_session(response: JSONResponse):
#     session_id = os.urandom(16).hex()
#     data = ConversationHistory(session_id=session_id, history=[])
#     await backend.create(session_id, data)
#     frontend.attach_to_response(response, session_id)
#     return {"message": "Session created",
#             "session": session_id}
async def create_session(response: Response):
    session = uuid4()
    data = ConversationHistory()

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return {"message": "OK"}


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
