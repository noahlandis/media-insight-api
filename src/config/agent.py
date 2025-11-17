from pydantic_ai import Agent, RunContext, Tool, ToolDefinition
from src.dependencies import get_settings
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from dataclasses import dataclass
import redis
from src.config.oauth_manager import OAuthManager
from pydantic import BaseModel, ConfigDict
import datetime
from src.models import ChannelRequest, MediaRequest

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
        'Use one of the functions to provide the user with social media insights'
    ),
)

@agent.tool
async def get_channel_stats(ctx: RunContext[AgentDeps], request: ChannelRequest):  
    """Returns youtube channel stats"""
    session = await ctx.deps.redis.json().get(ctx.deps.session_key)
    google = session.get("google")
    result = await ctx.deps.oauth.google.get('youtube/v3/channels', params={'mine': True, 'part': 'snippet,statistics'}, token=google)
    return result.json()




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


