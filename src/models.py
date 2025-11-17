from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, Set, Union

class MediaRequest(BaseModel):
    visibility_scopes: Set[Literal["public", "private", "unlisted"]] = Field(default_factory=lambda: {"public"}, min_length=1)

class ChannelRequest(MediaRequest):
    pass

class VideoRequest(MediaRequest):
    pass
