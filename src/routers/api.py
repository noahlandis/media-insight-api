from fastapi import APIRouter, Depends, status
from src.dependencies import get_redis, get_session_key
from pydantic import BaseModel


router = APIRouter(
    prefix="/api"
)

class PromptRequest(BaseModel):
    prompt: str


@router.get("/connected_platforms", status_code=status.HTTP_200_OK)
async def get_connected_platforms(session_key = Depends(get_session_key), redis = Depends(get_redis)):
    connected_platforms = await redis.json().objkeys(session_key, "$") # this is safe since get_session_key already checks that the key exists 
    return connected_platforms[0]




@router.post("/prompt", status_code=status.HTTP_200_OK)
async def prompt(promptRequest: PromptRequest):
    print(promptRequest.prompt)
