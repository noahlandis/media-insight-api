import secrets
from enum import StrEnum, auto

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from src.config.oauth_manager import OAuthManager
from src.config.settings import Settings
from src.dependencies import get_oauth_manager, get_redis, get_settings
from src.utils import session_key

router = APIRouter(
    prefix="/auth"
)

class Platform(StrEnum):
    GOOGLE = auto()
    REDDIT = auto()

@router.get("/{platform}")
async def auth(platform: Platform, request: Request, oauth: OAuthManager = Depends(get_oauth_manager), settings: Settings = Depends(get_settings)):
    client = oauth.create_client(platform)
    if client is None:
        return RedirectResponse(f"{settings.web_url}?error=unknown_provider")
    redirect_uri = request.url_for("auth_callback", platform=platform)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/{platform}/callback")
async def auth_callback(platform: Platform, request: Request, settings: Settings = Depends(get_settings), oauth: OAuthManager = Depends(get_oauth_manager), redis = Depends(get_redis)):
    web_url = settings.web_url
    client = oauth.create_client(platform)

    try:
        provider_response = await client.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(f"{web_url}?error=oauth_failed")


    if 'session_id' in request.session:
        sid = request.session.get('session_id')
    else:
        sid = secrets.token_urlsafe(32)
        request.session['session_id'] = sid

    print(provider_response)
       
    if platform == Platform.REDDIT:
        await redis.json().merge(session_key(sid), "$", {platform: {"access_token": provider_response.get("access_token")}})
    else:
        await redis.json().merge(session_key(sid), "$", {platform: {"access_token": provider_response.get("access_token"), "refresh_token": provider_response.get("refresh_token"), "expires_at": provider_response.get("expires_at")}})
        # we need to create an inverse mapping since the starlette update_token function isn't session scoped. Without this, we wouldn't know which redis record to update when the token is refreshed
        await redis.set(provider_response.get("refresh_token"), session_key(sid))
    return RedirectResponse(web_url)