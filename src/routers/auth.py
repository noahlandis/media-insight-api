from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from src.config.settings import Settings
from src.config.oauth_manager import OAuthManager
from enum import Enum
from src.dependencies import get_settings, get_redis, get_oauth_manager
import secrets
import json
 
router = APIRouter(
    prefix="/auth"
)

class Platform(str, Enum):
    google = "google"
    reddit = "reddit"

def session_key(session_id) -> str:
    return f"session:{session_id}"

async def get_session_key(request: Request, redis = Depends(get_redis)):
    session_id = request.session.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    if not await redis.exists(f"session:{session_id}"):
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return session_key(session_id)

@router.get("/connected_platforms")
async def get_connected_platforms(session_key = Depends(get_session_key), redis = Depends(get_redis)):
    connected_platforms = await redis.json().objkeys(session_key, "$")
    return connected_platforms[0]

@router.get("/{platform}")
async def auth(platform: Platform, request: Request, oauth: OAuthManager = Depends(get_oauth_manager)):
    client = oauth.create_client(platform.value)
    if client is None:
        return RedirectResponse(f"{frontend_url}?error=unknown_provider")
    redirect_uri = request.url_for("auth_callback", platform=platform.value)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/{platform}/callback")
async def auth_callback(platform: Platform, request: Request, settings: Settings = Depends(get_settings), oauth: OAuthManager = Depends(get_oauth_manager), redis = Depends(get_redis)):
    frontend_url = settings.frontend_url
    client = oauth.create_client(platform.value)

    try:
        provider_response = await client.authorize_access_token(request)
    except OAuthError as e:
        return RedirectResponse(f"{frontend_url}?error=oauth_failed")


    if 'session_id' in request.session:
        sid = request.session.get('session_id')
    else:
        sid = secrets.token_urlsafe(32)
        request.session['session_id'] = sid

       
    key = f"session:{sid}"
    await redis.json().merge(key, "$", {platform.value: {"access_token": provider_response.get("access_token")}})
    return RedirectResponse(frontend_url)

@router.get("/test/redis")
async def test_redis(redis = Depends(get_redis)):
    value = await redis.get("foo")
    return {"foo": value}