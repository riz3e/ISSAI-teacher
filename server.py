import uvicorn
from fastapi import FastAPI

# from database import engine, Base
# from routers import user as UserRouter
# from routers import oauth as OauthRouter

# Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(UserRouter.router, prefix="/user")
# app.include_router(tes.router, prefix="/test")
app.include_router(OauthRouter.router, prefix="")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, workers=3)