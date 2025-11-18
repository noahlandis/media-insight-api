from enum import Enum
from pydantic import BaseModel, Field, NonNegativeInt, AliasPath, AliasChoices
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
    visibility_scopes: Optional[Set[Literal["public", "private", "unlisted"]]] = Field(default_factory=lambda: {"public"}, description="the visibility level to filter the requested resource by")

class ChannelRequest(MediaRequest):
    data: Set[Literal["name", "description", "published_at", "video_count", "view_count", "subscriber_count"]] = Field(description="the data the user wishes to see")

    @property
    def part(self) -> str:
        return ",".join({CHANNEL_PART[field] for field in self.data})

class ChannelResponse(BaseModel):
    view_count: Optional[NonNegativeInt] = Field(description="the number of views the channel has", default=None, alias=AliasChoices(
        "viewCount",
        AliasPath("items", 0, "statistics", "viewCount"),
    ))
    subscriber_count: Optional[NonNegativeInt] = Field(description="the number of subscribers the channel has", default=None, alias=AliasChoices(
        "subscriberCount",
        AliasPath("items", 0, "statistics", "subscriberCount"),
    ))
    video_count: Optional[NonNegativeInt] = Field(description="the number of videos the channel has uploaded", default=None,alias=AliasChoices(
        "videoCount",
        AliasPath("items", 0, "statistics", "videoCount"),
    ))

    published_at: Optional[str] = Field(description="the date the channel was created", default=None,alias=AliasChoices(
        "publishedAt",
        AliasPath("items", 0, "snippet", "publishedAt"),
    ))

    name: Optional[str] = Field(description="the name of the channel", default=None,alias=AliasChoices(
        "title",
        AliasPath("items", 0, "snippet", "title"),
    ))

    description: Optional[str] = Field(description="the description of the channel", default=None,alias=AliasChoices(
        "description",
        AliasPath("items", 0, "snippet", "description"),
    ))




class VideoRequest(MediaRequest):
    pass
