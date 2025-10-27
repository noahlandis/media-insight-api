from src.config.settings import Settings
from src.config.oauth_manager import OAuthManager
from fastapi import Request, Depends, status, HTTPException
from functools import lru_cache
from src.utils import session_key

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_oauth_manager() -> OAuthManager:
    return OAuthManager(get_settings()).oauth

async def get_redis(request: Request):
    return request.app.state.redis

async def get_session_key(request: Request, redis = Depends(get_redis)):
    session_id = request.session.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated")
    key = session_key(session_id)
    if not await redis.exists(key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated")
    return key