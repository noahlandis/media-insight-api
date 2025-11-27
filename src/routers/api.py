from typing import Annotated

from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, StringConstraints

from src.config.agent import AgentDeps, agent
from src.config.oauth_manager import OAuthManager
from src.dependencies import get_oauth_manager, get_redis, get_session_key, get_settings

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
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your Google connection has expired or been revoked. Please reconnect your account.",
            )
    




