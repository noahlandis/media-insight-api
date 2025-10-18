from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from functools import lru_cache

class Config(BaseSettings):
    google_client_id: SecretStr
    google_client_secret: SecretStr
    openai_api_key: SecretStr
    oauth_secret_key: SecretStr
    reddit_client_id: SecretStr
    reddit_client_secret: SecretStr
    frontend_url: str
    redis_db: int
    redis_host: str
    redis_port: int
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
