from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from config.settings import Settings
from config.oauth_manager import OAuthManager
from enum import Enum
from dependencies import get_settings, get_redis, get_oauth_manager

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
async def auth(platform: Platform, request: Request, oauth: OAuthManager = Depends(get_oauth_manager)):
    client = oauth.create_client(platform.value)
    if client is None:
        return RedirectResponse(f"{frontend_url}?error=unknown_provider")
    redirect_uri = request.url_for("auth_callback", platform=platform.value)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/{platform}/callback")
async def auth_callback(platform: Platform, request: Request, settings: Settings = Depends(get_settings), oauth: OAuthManager = Depends(get_oauth_manager)):
    frontend_url = settings.frontend_url
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