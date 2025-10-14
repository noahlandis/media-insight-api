from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

import os
oauth = OAuth()

oauth.register(
    name='google',
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
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
    google = oauth.google
    redirect_uri = request.url_for("google_callback")
    return await google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = user

    return RedirectResponse(os.environ["FRONTEND_URL"])

@router.get("/reddit")
async def reddit():
    return {"message": "welcome to Reddit"}

@router.get("/x")
async def reddit():
    return {"message": "welcome to x"}