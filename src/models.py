from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, Set


class ResourceType(str, Enum):
    video_list = 'video_list'
    channel = 'channel'

class VideoList(BaseModel):
    resource_type: Literal[ResourceType.VideoList]

class Channel(BaseModel):
    resource_type: Literal[ResourceType.Channel]

class MediaRequest(BaseModel):
    resource: Union[VideoList, Channel] = Field(..., discriminator='resource_type')
    visibility_scopes: Set[Literal["public", "private", "unlisted"]]
