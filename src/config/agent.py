from pydantic_ai import Agent, RunContext, Tool, ToolDefinition, ModelMessage, ModelResponse, TextPart
from src.dependencies import get_settings
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from dataclasses import dataclass
import redis
from src.config.oauth_manager import OAuthManager
from pydantic import BaseModel, ConfigDict
import datetime
from pydantic_ai.models.function import AgentInfo, FunctionModel

from src.models.channel_public_stats import ChannelPublicStatsRequest, ChannelPublicStatsResponse
from src.models.channel_analytics import ChannelAnalyticsRequest, ChannelAnalyticsResponse

_config = get_settings()



@dataclass
class AgentDeps:
    redis: redis.Redis
    oauth: OAuthManager
    session_key: str

# async def filter_out_tools_by_name(
#     ctx: RunContext[AgentDeps], tool_defs: list[ToolDefinition]
# ) -> list[ToolDefinition] | None:
#     session = await ctx.deps.redis.json().get(ctx.deps.session_key)
#     google = session.get("google")
#     reddit = session.get("reddit")

#     allowed_tools = []
#     for tool_def in tool_defs:
#         if "youtube" in tool_def.name and not google:
#             continue
#         if "reddit" in tool_def.name and not reddit:
#             continue
#         allowed_tools.append(tool_def)
    
#     print("allowed tools")
#     for tool_def in allowed_tools:
#         print(tool_def.name)
#     return allowed_tools

agent = Agent(  
    model = OpenAIChatModel(
        "gpt-4o-mini",
        provider=OpenAIProvider(api_key=_config.openai_api_key.get_secret_value()),
    ),
    deps_type=str,
    instructions=(
        """
        You are an assistant for YouTube analytics.
        
        - Always use tools to fetch data about the user's channel.
        - Do not ask for parameters that have default values.
        - Never ask for channel IDs or channel names - the tools automatically use the authenticated account.
        - When the user asks for multiple metrics, you MUST call a single tool and include all requested metrics in its `data` array.

        Examples of correct tool usage:

        - "How many subscribers do I have?"
            → get_channel_public_stats({"data": ["subscriber_count"]})
        
        - "How many views does my channel have from public videos only?"
            → get_channel_public_stats({"data": ["public_view_count"]})
        
        - "When was my channel created and how many videos do i have?"
            → get_channel_public_stats({"data": ["published_at", "video_count"]})
        
        -"How many subscribers do I have and what's my public view count and how many videos do i have?" 
            → get_channel_public_stats({"data": ["subscriber_count", "public_view_count", "video_count]})

        - "How many views does my channel have?"
            → get_channel_analytics({"data": ["total_view_count"]})

        """
    ),
    retries=0,
)

# agent = Agent()

@agent.tool
async def get_channel_public_stats(ctx: RunContext[AgentDeps], request: ChannelPublicStatsRequest) -> ChannelPublicStatsResponse:  
    session = await ctx.deps.redis.json().get(ctx.deps.session_key)
    google = session.get("google")
    result = await ctx.deps.oauth.google.get('youtube/v3/channels', params={'mine': True, 'part': request.part}, token=google)
    payload = result.json()
    return ChannelPublicStatsResponse.model_validate(payload)

@agent.tool
async def get_channel_analytics(ctx: RunContext[AgentDeps], request: ChannelAnalyticsRequest) -> ChannelAnalyticsResponse:  
    session = await ctx.deps.redis.json().get(ctx.deps.session_key)
    google = session.get("google")
    result = await ctx.deps.oauth.google.get(
        'https://youtubeanalytics.googleapis.com/v2/reports',
        params={
            'ids': 'channel==MINE',
            'startDate': '2005-10-01',
            'endDate': '2025-11-11',
            "metrics": request.metrics,
        },
        token=google
    )

    payload = result.json()

    if not payload.get("rows"):
        return {}

    headers = [h["name"] for h in payload["columnHeaders"]]
    row = payload["rows"][0]
    result_table = dict(zip(headers, row))
    
    return ChannelAnalyticsResponse.model_validate(result_table)


def print_schema(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    tool = info.function_tools[0]
    print(tool.description)
    #> Get me foobar.
    print(tool.parameters_json_schema)
    """
    {
        'additionalProperties': False,
        'properties': {
            'a': {'description': 'apple pie', 'type': 'integer'},
            'b': {'description': 'banana cake', 'type': 'string'},
            'c': {
                'additionalProperties': {'items': {'type': 'number'}, 'type': 'array'},
                'description': 'carrot smoothie',
                'type': 'object',
            },
        },
        'required': ['a', 'b', 'c'],
        'type': 'object',
    }
    """
    return ModelResponse(parts=[TextPart('foobar')])


# @agent.tool
# async def youtube_video_count(ctx: RunContext[AgentDeps]):  
#     """Returns number of youtube videos"""
#     session = await ctx.deps.redis.json().get(ctx.deps.session_key)
#     google = session.get("google")
#     result = await ctx.deps.oauth.google.get('youtube/v3/channels', params={'mine': True, 'part': 'snippet,statistics'}, token=google)
#     return result.json()



# @agent.tool
# async def youtube_comments(ctx: RunContext[AgentDeps]) -> str:  
#     """Returns youtube comments"""
#     return 'Here are your youtube comments'



# @agent.tool
# async def reddit_karma(ctx: RunContext[AgentDeps]) -> str:  
#     """Returns reddit karma"""
#     return 'Here is your reddit karma'


# @agent.tool
# async def reddit_posts(ctx: RunContext[AgentDeps]) -> str:  
#     """Returns reddit posts"""
#     return 'Here is your reddit posts'


