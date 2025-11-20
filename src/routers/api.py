from fastapi import APIRouter, Depends, status, HTTPException
from src.dependencies import get_redis, get_session_key, get_settings, get_oauth_manager
from pydantic import BaseModel, StringConstraints
from typing import Annotated
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from src.config.oauth_manager import OAuthManager
from src.config.agent import agent, AgentDeps
from src.services.youtube import get_channel_overview, get_channel_stats, get_videos, get_video_details, get_public_videos, get_channel_overview_analytics, get_top_viewed_video_ids_analytics, get_public_videos_search_api, get_video_count_playlist_api, get_video_count_search_api, get_all_videos_search_api, get_public_videos_sort_test
import json
from authlib.integrations.base_client.errors import OAuthError
from pydantic_ai.models.function import AgentInfo, FunctionModel

from src.models.channel_public_stats import ChannelPublicStatsRequest, ChannelPublicStatsResponse
from src.models.channel_analytics import ChannelAnalyticsRequest, ChannelAnalyticsResponse

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

    try:
        stripped_prompt = promptRequest.prompt.strip() # remove leading and trailing whitespace before passing it to LLM
        result = await agent.run(stripped_prompt, deps=AgentDeps(redis, oauth, session_key))
        return {"result": result.output}

    except OAuthError as e:
        if e.error == "invalid_grant":
            # destroy stale session
            await redis.delete(google_session.get('refresh_token'))
            await redis.json().delete(session_key, ".google")
            raise HTTPException(
                status_code=401,
                detail="Your Google connection has expired or been revoked. Please reconnect your account.",
            )
    




