from fastapi import APIRouter, Depends, status
from src.dependencies import get_redis, get_session_key, get_settings, get_oauth_manager
from pydantic import BaseModel, StringConstraints
from typing import Annotated
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from src.config.oauth_manager import OAuthManager
from src.config.agent import agent, AgentDeps, Channel
from src.services.youtube import get_channel_overview, get_channel_stats, get_videos, get_video_count, get_video_details, get_public_videos, get_channel_overview_analytics
import json

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
    google_record = await redis.json().get(session_key, '$.google')
    google_session = google_record[0]

    print("TESTING FUNCTIONS")
    print("channel overview data api")
    await get_channel_overview(oauth.google, google_session)
    print()
    print("channel stats data api")
    await get_channel_stats(oauth.google, google_session)
    print()

    # await get_videos(oauth.google, google_session)
    # print()
    # await get_video_count(oauth.google, google_session)
    # print()
    # videos = await get_video_details(oauth.google, google_session)
    print()
    print("channel overview analytics api")
    await get_channel_overview_analytics(oauth.google, google_session)
    print()



    # print(promptRequest.prompt)


    # Run the agent
    # success_number = 18  
    # result = await agent.run('Launch a salad')
    # print(result.output)  
    # #> True

    # print("get yt likes")
    # result = await agent.run('Show me my Youtube likes', deps=AgentDeps(redis, oauth, session_key))
    # print(result.output)

    # print("get yt video count")
    # # result = await agent.run('Show me how many videos i have on my channel', deps=AgentDeps(redis, oauth, session_key))
    # print(result.output)

    # print("get yt comments")
    # result = await agent.run('Show me my Youtube comments', deps=AgentDeps(redis, oauth, session_key))
    # print(result.output)

    # print("get reddit karm")
    # result = await agent.run('Show me my Reddit karma', deps=AgentDeps(redis, oauth, session_key))
    # print(result.output)

    


    # result = await agent.run('Launch a potato')
    # print(result.output)
    #> False




