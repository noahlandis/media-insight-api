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

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return user

@router.get("/connected_platforms")
def get_connected_platforms(user = Depends(get_current_user)):
    return user['connected_platforms']

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

    if 'user' not in request.session:
        request.session['user'] = {}
        request.session['user']['connected_platforms'] = []
        request.session['user']['session_id'] = None

    sid = request.session['user']['session_id'] or secrets.token_urlsafe(32)

    
    request.session['user']['session_id'] = sid

    if platform.value not in request.session['user']['connected_platforms']:
        request.session['user']['connected_platforms'].append(platform.value)
       
    key = f"session:{sid}"
    await redis.json().merge(key, "$", {platform.value: {"access_token": provider_response.get("access_token")}})
    return RedirectResponse(frontend_url)

@router.get("/test/redis")
async def test_redis(redis = Depends(get_redis)):
    value = await redis.get("foo")
    return {"foo": value}