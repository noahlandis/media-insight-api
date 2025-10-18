from authlib.integrations.starlette_client import OAuth
from config.settings import Settings
from dataclasses import dataclass

@dataclass(frozen=True)
class OAuthManager:
    settings: Settings
    oauth: OAuth = OAuth()

    def __post_init__(self):
        self.oauth.register(
            name='google',
            client_id=self.settings.google_client_id.get_secret_value(),
            client_secret=self.settings.google_client_secret.get_secret_value(),
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly",
            },
        )

        self.oauth.register(
            name="reddit",
            client_id=self.settings.reddit_client_id.get_secret_value(),
            client_secret=self.settings.reddit_client_secret.get_secret_value(),
            access_token_url="https://www.reddit.com/api/v1/access_token",
            authorize_url="https://www.reddit.com/api/v1/authorize",
            api_base_url="https://oauth.reddit.com",
            client_kwargs={
                "scope": "identity read",
                "token_endpoint_auth_method": "client_secret_basic",
            },
        )
    




