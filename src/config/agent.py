from pydantic_ai import Agent, RunContext
from src.dependencies import get_settings
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

_config = get_settings()

roulette_agent = Agent(  
    model = OpenAIChatModel(
        "gpt-5",
        provider=OpenAIProvider(api_key=_config.openai_api_key.get_secret_value()),
    ),
    deps_type=int,
    output_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:  
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'