from dotenv import load_dotenv
load_dotenv()
import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers import auth

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["OAUTH_SECRET_KEY"],
    same_site="lax",       
    https_only=False,
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}