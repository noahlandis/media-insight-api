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

oauth.register(
    name="reddit",
    client_id=config.reddit_client_id.get_secret_value(),
    client_secret=config.reddit_client_secret.get_secret_value(),
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

@router.get("/google")
async def google(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    frontend_url = config.frontend_url
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            request.session['user'] = {}
            request.session['user']['google'] = token
    except OAuthError as e:
        return RedirectResponse(f"{frontend_url}?error=oauth_failed")
    return RedirectResponse(frontend_url)


@router.get("/reddit")
async def reddit(request: Request):
    redirect_uri = request.url_for("reddit_callback")
    return await oauth.reddit.authorize_redirect(request, redirect_uri, duration="permanent")




@router.get("/reddit/callback")
async def reddit_callback(request: Request):
    return {"message": "hi. reddit callback hit"}  
    

@router.get("/x")
async def x():
    return {"message": "welcome to x"}

@router.get("/me")
async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return {"message": "no user found"}

    return user

@router.get("/youtube-test")
async def get_youtube_data():
    pass
