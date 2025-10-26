from src.config.settings import Settings
from src.config.oauth_manager import OAuthManager
from fastapi import Request
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_oauth_manager() -> OAuthManager:
    return OAuthManager(get_settings()).oauth

async def get_redis(request: Request):
    return request.app.state.redis