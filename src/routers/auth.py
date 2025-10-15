from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from settings import config

oauth = OAuth()

oauth.register(
    name='google',
    client_id=config.google_client_id.get_secret_value(),
    client_secret=config.google_client_secret.get_secret_value(),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        # include OIDC + your YouTube scopes
        "scope": "openid email profile https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly",
    },
)

router = APIRouter(
    prefix="/auth"
)

@router.get("/google")
async def google(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            request.session['user'] = user
    except OAuthError as e:
        return RedirectResponse(f"{config.frontend_url}?error=oauth_failed")
    return RedirectResponse(config.frontend_url)

@router.get("/reddit")
async def reddit():
    return {"message": "welcome to Reddit"}

@router.get("/x")
async def x():
    return {"message": "welcome to x"}