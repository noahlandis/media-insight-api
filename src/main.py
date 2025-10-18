from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from routers import auth
from config import get_config

app = FastAPI()

_config = get_config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[_config.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=_config.oauth_secret_key.get_secret_value(),
    same_site="none",       
    https_only=True,
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}