from fastapi import APIRouter, Depends, status
from src.dependencies import get_redis, get_session_key, get_settings, get_oauth_manager
from pydantic import BaseModel, StringConstraints
from typing import Annotated
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from src.config.oauth_manager import OAuthManager
from src.config.agent import agent
router = APIRouter(
    prefix="/api"
)

class PromptRequest(BaseModel):
    prompt: Annotated[str, StringConstraints(max_length=100)]


@router.get("/connected_platforms", status_code=status.HTTP_200_OK)
async def get_connected_platforms(session_key = Depends(get_session_key), redis = Depends(get_redis)):
    connected_platforms = await redis.json().objkeys(session_key, "$") # this is safe since get_session_key already checks that the key exists 
    return connected_platforms[0]


@router.post("/prompt", status_code=status.HTTP_200_OK)
async def prompt(promptRequest: PromptRequest, settings = Depends(get_settings), redis = Depends(get_redis), session_key = Depends(get_session_key), oauth: OAuthManager = Depends(get_oauth_manager)):
    record = await redis.json().get(session_key, '$.google')
    session_data = record[0]
    # creds = Credentials(
    #     token=session_data['access_token'],
    #     refresh_token=session_data['refresh_token'],
    #     token_uri = "https://oauth2.googleapis.com/token",
    #     client_id=settings.google_client_id,
    #     client_secret=settings.google_client_secret,
    #     scopes=oauth.google.client_kwargs.get('scope')
    # )
    # youtube_service = build("youtube", "v3", credentials=creds)
    # print(youtube_service.channels().list(part="snippet,statistics", mine=True).execute())
    # # youtube_analytics_service = build("youtubeAnalytics", "v2")
    # print(session_data)


    # resp = await oauth.google.get('youtube/v3/channels', params={'mine': True, 'part': 'snippet,statistics'}, token=session_data)
    # print(resp.json())
    # print(promptRequest.prompt)


    # Run the agent
    success_number = 18  
    result = await agent.run('Launch a salad')
    print(result.output)  
    #> True

    result = await agent.run('Launch a burger')
    print(result.output)


    result = await agent.run('Launch a potato')
    print(result.output)
    #> False


