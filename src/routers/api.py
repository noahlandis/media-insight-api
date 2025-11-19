from fastapi import APIRouter, Depends, status, HTTPException
from src.dependencies import get_redis, get_session_key, get_settings, get_oauth_manager
from pydantic import BaseModel, StringConstraints
from typing import Annotated
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from src.config.oauth_manager import OAuthManager
from src.config.agent import agent, AgentDeps, print_schema
from src.services.youtube import get_channel_overview, get_channel_stats, get_videos, get_video_details, get_public_videos, get_channel_overview_analytics, get_top_viewed_video_ids_analytics, get_public_videos_search_api, get_video_count_playlist_api, get_video_count_search_api, get_all_videos_search_api, get_public_videos_sort_test
import json
from authlib.integrations.base_client.errors import OAuthError
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

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
        # await agent.run('hello', model=FunctionModel(print_schema))
        # result = await get_channel_overview(oauth.google, google_session)
        # print(result)

        # channel = ChannelOverviewRequest.model_validate({"data": ["view_count", "comment_count", "subscribers_gained"]})
        # print(channel)
        # print(channel.requested_fields)


        # result = await get_channel_overview_analytics(oauth.google, google_session)
        # print(result)
        # channel_response = ChannelOverviewResponse.model_validate(result)
        # print("channel response")
        # print(channel_response)

        # stats = result['items'][0]['statistics']
        # channel = ChannelRequest.model_validate({"data": ["name", "view_count"]})
        # print(channel.part)

        # print(overview['items'][0]['snippet'])
        # test_model = TestModel()

        # result = await agent.run('How many comments does my channel have', deps=AgentDeps(redis, oauth, session_key), model=test_model)
        # print(test_model.last_model_request_parameters.function_tools)

        # # for msg in result.all_messages():
        # #     print("MSG:", msg)


        result = await agent.run('How many subscribers does my channel have and how many public views does it have', deps=AgentDeps(redis, oauth, session_key))

        print(result.output)


    except OAuthError as e:
        if e.error == "invalid_grant":
            # destroy stale session
            await redis.delete(google_session.get('refresh_token'))
            await redis.json().delete(session_key, ".google")
            raise HTTPException(
                status_code=401,
                detail="Your Google connection has expired or been revoked. Please reconnect your account.",
            )
    print()
    # print("channel stats data api")
    # await get_channel_stats(oauth.google, google_session)
    # print()

    # await get_videos(oauth.google, google_session)
    # print()

    # print("get video count playlist api")
    # await get_video_count_playlist_api(oauth.google, google_session)
    # print()
    # print("get video details")
    # videos = await get_video_details(oauth.google, google_session)
    # print()
    # print("channel overview analytics api")
    # await get_channel_overview_analytics(oauth.google, google_session)
    # print()

    # print("top viewed video ids analytics api")
    # await get_top_viewed_video_ids_analytics(oauth.google, google_session)

    # print("PLAYLIST ITEMS API")
    # playlist_items_videos = await get_videos(oauth.google, google_session)
    # print()
    # print()
    # print()
    # print()
    # print("Showing all public videos")
    # search_items_videos = await get_public_videos_sort_test(oauth.google, google_session)

    # print()


    # print()
    # print("GET VIDEOS SORT")
    # search_items_videos = await get_videos_sort(oauth.google, google_session, 'viewCount')
    # print()





    # print(promptRequest.prompt)


    # Run the agent
    # success_number = 18  
    # result = await agent.run('Launch a salad')
    # print(result.output)  
    # #> True

    # print("get yt likes")
    # result = await agent.run('Show me my Youtube Channel Stats', deps=AgentDeps(redis, oauth, session_key))
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




