from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, Set, Union, Optional

# used to determine the 'part' param to use when calling the youtube/channels API
CHANNEL_PART = {
    "view_count": "statistics",
    "subscriber_count": "statistics",
    "video_count": "statistics",

    "published_at": "snippet",
    "name": "snippet",
    "description": "snippet",
}

class MediaRequest(BaseModel):
    visibility_scopes: Optional[Set[Literal["public", "private", "unlisted"]]] = Field(default_factory=lambda: {"public"}, description="the visibility level to filter the requested resource by", min_length=1)

class ChannelRequest(MediaRequest):
    data: Set[Literal["name", "description", "published_at", "video_count", "view_count", "subscriber_count"]] = Field(description="the data the user wishes to see")

    @property
    def part(self) -> str:
        return ",".join({CHANNEL_PART[field] for field in self.data})



class VideoRequest(MediaRequest):
    pass
