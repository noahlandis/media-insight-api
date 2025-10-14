from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    openai_api_key: str
    oauth_secret_key: str
    frontend_url: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')



config: Settings = Settings()