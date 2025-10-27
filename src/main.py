from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.routers import auth
from src.dependencies import get_settings
import redis.asyncio as redis
from contextlib import asynccontextmanager


_config = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.Redis(host=_config.redis_host, port=_config.redis_port, db=_config.redis_db, decode_responses=True)
    try:
        yield
    finally:
        await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)

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

