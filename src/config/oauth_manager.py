from authlib.integrations.starlette_client import OAuth
from src.config.settings import Settings
from redis.asyncio import Redis
from typing import Optional

class OAuthManager:
    def __init__(self, settings: Settings, redis: Optional[Redis] = None):
        self.settings = settings
        self.redis = redis

        async def update_token(name, token, refresh_token=None, access_token=None):
            if self.redis:
                print("old token")
                print(access_token)
                print("new token")
                print(token['access_token'])

                print()

                print("old token refresh")
                print(refresh_token)
                print("new token refresh")
                print(token['refresh_token'])

                session_key = await self.redis.get(refresh_token)
                await self.redis.json().merge(session_key, "$.google", {"access_token": token.get("access_token"), "refresh_token": token.get("refresh_token"), "expires_at": token.get("expires_at")})

        self.oauth = OAuth(update_token=update_token)

        self._register_providers()

    def _register_providers(self):
        self.oauth.register(
            name='google',
            client_id=self.settings.google_client_id.get_secret_value(),
            client_secret=self.settings.google_client_secret.get_secret_value(),
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            api_base_url="https://www.googleapis.com",  

            authorize_params={"access_type": "offline", "prompt": "consent"},
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
    




