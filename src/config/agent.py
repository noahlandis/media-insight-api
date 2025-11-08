from pydantic_ai import Agent, RunContext, Tool, ToolDefinition
from src.dependencies import get_settings
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from dataclasses import dataclass
import redis
from src.config.oauth_manager import OAuthManager

_config = get_settings()

@dataclass
class AgentDeps:
    redis: redis.Redis
    oauth: OAuthManager
    session_key: str



async def filter_out_tools_by_name(
    ctx: RunContext[AgentDeps], tool_defs: list[ToolDefinition]
) -> list[ToolDefinition] | None:
    print("printing session key from ctx")
    print(ctx.deps.session_key)
    return [tool_def for tool_def in tool_defs if tool_def.name != 'launch_potato']

agent = Agent(  
    model = OpenAIChatModel(
        "gpt-4o-mini",
        provider=OpenAIProvider(api_key=_config.openai_api_key.get_secret_value()),
    ),
    deps_type=str,
    system_prompt=(
        'Use one of the `launch` functions to launch the desired food'
    ),
    prepare_tools=filter_out_tools_by_name
)

@agent.tool
async def launch_potato(ctx: RunContext[int]) -> str:  
    """Launches a potato"""
    return 'Just launched a potato'



@agent.tool
async def launch_salad(ctx: RunContext[int]) -> str:  
    """Launches a salad"""
    return 'Just launched a salad'



@agent.tool
async def launch_burger(ctx: RunContext[int]) -> str:  
    """Launches a burger"""
    return 'Just launched a burger'

