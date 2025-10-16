from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from routers import auth
from settings import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config.oauth_secret_key.get_secret_value(),
    same_site="none",       
    https_only=True,
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}