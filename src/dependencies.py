from config import Config
from fastapi import Request
from functools import lru_cache

@lru_cache
def get_config() -> Config:
    return Config()


async def get_redis(request: Request):
    return request.app.state.redis