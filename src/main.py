from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers import auth
from settings import config

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=config.oauth_secret_key,
    same_site="lax",       
    https_only=False,
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}