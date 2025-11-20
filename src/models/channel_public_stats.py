from enum import StrEnum, auto
from pydantic import BaseModel, Field, NonNegativeInt, AliasPath
from typing import Literal, Set, Optional
from pydantic.alias_generators import to_camel

class ChannelPartType(StrEnum):
    SNIPPET = auto()
    STATISTICS = auto()

# used to determine the 'part' param to use when calling the youtube/channels API
CHANNEL_PART = {
    "public_view_count": ChannelPartType.STATISTICS,
    "subscriber_count": ChannelPartType.STATISTICS,
    "video_count": ChannelPartType.STATISTICS,

    "published_at": ChannelPartType.SNIPPET,
    "name": ChannelPartType.SNIPPET,
    "description": ChannelPartType.SNIPPET,
}

def channel_alias_path(part: ChannelPartType, field_name: str) -> AliasPath:
    """
    Returns an alias path for a given field

    Args:
        part (ChannelPartType): "snippet" or "statistics"
        field_name (str): "the field to extract from the json response"
    """
    return AliasPath("items", 0, part, to_camel(field_name))


class ChannelPublicStatsRequest(BaseModel):
    data: Set[Literal[*tuple(CHANNEL_PART.keys())]] = Field(description="the data the user wishes to see")

    @property
    def part(self) -> str:
        return ",".join(CHANNEL_PART[field] for field in self.data)



class ChannelPublicStatsResponse(BaseModel):
    public_view_count: Optional[NonNegativeInt] = Field(description="the number of views the channel has from public videos only", default=None, alias=channel_alias_path(ChannelPartType.STATISTICS, "viewCount"))

    subscriber_count: Optional[NonNegativeInt] = Field(
        description="the number of subscribers the channel has",
        default=None,
        alias=channel_alias_path(ChannelPartType.STATISTICS, "subscriber_count"),
    )

    video_count: Optional[NonNegativeInt] = Field(
        description="the number of videos the channel has uploaded",
        default=None,
        alias=channel_alias_path(ChannelPartType.STATISTICS, "video_count"),
    )

    published_at: Optional[str] = Field(
        description="the date the channel was created",
        default=None,
        alias=channel_alias_path(ChannelPartType.SNIPPET, "published_at"),
    )

    name: Optional[str] = Field(
        description="the name of the channel",
        default=None,
        alias=channel_alias_path(ChannelPartType.SNIPPET, "title"),
    )

    description: Optional[str] = Field(
        description="the description of the channel",
        default=None,
        alias=channel_alias_path(ChannelPartType.SNIPPET, "description"),
    )