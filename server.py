import uvicorn
from fastapi import FastAPI


# from database import engine, Base
# from routers import user as UserRouter
from web.Full.gpt import Router as ChatGPTRouter

# Base.metadata.create_all(bind=engine)



app = FastAPI()
app.include_router(ChatGPTRouter, prefix="/gpt")
# app.include_router(tes.router, prefix="/test")
# app.include_router(OauthRouter.router, prefix="")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8080, reload=True, workers=3)