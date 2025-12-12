from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status

from src.config.oauth_manager import OAuthManager
from src.config.settings import Settings
from src.utils import session_key
from enum import StrEnum, auto
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated


@lru_cache
def get_settings() -> Settings:
    return Settings()

async def get_redis(request: Request):
    return request.app.state.redis

def get_oauth_manager(request: Request, redis = Depends(get_redis)):
    oauth_manager = OAuthManager(get_settings(), redis=redis)
    return oauth_manager.oauth


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_session_key(request: Request, redis = Depends(get_redis), token: Annotated[str, Depends(oauth2_scheme)] = None):
    session_id = request.session.get("session_id") or token
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated")
    key = session_key(session_id)
    if not await redis.exists(key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated")
    return key

class Source(StrEnum):
    WEB = auto()
    MOBILE = auto()

def get_source(source: Source = Source.WEB) -> Source:
    return source

def get_client_origin_url(source: Source = Depends(get_source), settings: Settings = Depends(get_settings)) -> str:
    # since we're using the Source ENUM, we can assume that if it's not web, the source will be mobile (as other values will throw an error)
    return settings.web_url if source == Source.WEB else settings.mobile_url