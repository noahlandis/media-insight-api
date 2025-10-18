from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from config import Config
from enum import Enum
from dependencies import get_config, get_redis

oauth = OAuth()
_config = get_config()

oauth.register(
    name='google',
    client_id=_config.google_client_id.get_secret_value(),
    client_secret=_config.google_client_secret.get_secret_value(),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly",
    },
)

oauth.register(
    name="reddit",
    client_id=_config.reddit_client_id.get_secret_value(),
    client_secret=_config.reddit_client_secret.get_secret_value(),
    access_token_url="https://www.reddit.com/api/v1/access_token",
    authorize_url="https://www.reddit.com/api/v1/authorize",
    api_base_url="https://oauth.reddit.com",
    client_kwargs={
        "scope": "identity read",
        "token_endpoint_auth_method": "client_secret_basic",
    },
)

router = APIRouter(
    prefix="/auth"
)

class Platform(str, Enum):
    google = "google"
    reddit = "reddit"

@router.get("/me")
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return {"message": "no user found"}

    return user

@router.get("/{platform}")
async def auth(platform: Platform, request: Request):
    client = oauth.create_client(platform.value)
    if client is None:
        return RedirectResponse(f"{frontend_url}?error=unknown_provider")
    redirect_uri = request.url_for("auth_callback", platform=platform.value)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/{platform}/callback")
async def auth_callback(platform: Platform, request: Request, config: Config = Depends(get_config)):
    frontend_url = config.frontend_url
    client = oauth.create_client(platform.value)

    try:
        token = await client.authorize_access_token(request)
    except OAuthError as e:
        return RedirectResponse(f"{frontend_url}?error=oauth_failed")

    if 'user' not in request.session:
        request.session['user'] = {}
    request.session['user'][platform.value] = None
    
    return RedirectResponse(frontend_url)

@router.get("/test/redis")
async def test_redis(redis = Depends(get_redis)):
    value = await redis.get("foo")
    return {"foo": value}