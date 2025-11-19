from enum import StrEnum, auto
from pydantic import BaseModel, Field, NonNegativeInt, AliasPath, AliasChoices, ConfigDict
from typing import Literal, Set, Union, Optional
from pydantic.alias_generators import to_camel

class ChannelPartType(StrEnum):
    SNIPPET = auto()
    STATISTICS = auto()

# used to determine the 'part' param to use when calling the youtube/channels API
CHANNEL_PART = {
    "view_count": ChannelPartType.STATISTICS,
    "subscriber_count": ChannelPartType.STATISTICS,
    "video_count": ChannelPartType.STATISTICS,

    "published_at": ChannelPartType.SNIPPET,
    "name": ChannelPartType.SNIPPET,
    "description": ChannelPartType.SNIPPET,
}

class MediaRequest(BaseModel):
    visibility_scopes: Optional[Set[Literal["public", "private", "unlisted"]]] = Field(default_factory=lambda: {"public"}, description="the visibility level to filter the requested resource by")

class ChannelRequest(MediaRequest):
    data: Set[Literal["name", "description", "published_at", "video_count", "view_count", "subscriber_count"]] = Field(description="the data the user wishes to see")

    @property
    def part(self) -> str:
        return ",".join(CHANNEL_PART[field] for field in self.data)




def channel_alias_path(part: ChannelPartType, field_name: str) -> AliasPath:
    """
    Returns an alias path for a given field

    Args:
        part (ChannelPartType): "snippet" or "statistics"
        field_name (str): "the field to extract from the json response"
    """
    return AliasPath("items", 0, part, to_camel(field_name))

class ChannelResponse(BaseModel):
    view_count: Optional[NonNegativeInt] = Field(description="the number of views the channel has", default=None, alias=channel_alias_path(ChannelPartType.STATISTICS, "view_count"))

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

ANALYTICS_FIELD_MAPPING = {
    "view_count": "views",
    "comment_count": "comments",
    "like_count": "likes",
    "dislike_count": "dislikes",
    "estimated_minutes_watched": "estimatedMinutesWatched",
    "average_view_duration": "averageViewDuration",
    "subscribers_gained": "subscribersGained",
    "subscribers_lost": "subscribersLost",
}


class ChannelOverviewRequest(MediaRequest):

    # data: Set[Literal[ANALYTICS_FIELD_MAPPING.keys()]] = Field(description="the data the user wishes to see")
    data: Set[Literal[*tuple(ANALYTICS_FIELD_MAPPING.keys())]] = Field(description="the data the user wishes to see")

    @property
    def metrics(self) -> str:
        return ",".join(ANALYTICS_FIELD_MAPPING[field] for field in self.data)

class ChannelOverviewResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda field_name: ANALYTICS_FIELD_MAPPING[field_name]
    )
    view_count: Optional[NonNegativeInt] = Field(description="the number of views the channel has", default=None)
    comment_count: Optional[NonNegativeInt] = Field(description="the number of comments the channel has", default=None)
    like_count: Optional[NonNegativeInt] = Field(description="the number of likes the channel has", default=None)
    dislike_count: Optional[NonNegativeInt] = Field(description="the number of dislikes the channel has", default=None)
    estimated_minutes_watched: Optional[NonNegativeInt] = Field(description="the channel's estimated watch time in minutes", default=None)
    average_view_duration: Optional[NonNegativeInt] = Field(description="the channel's average view duration in minutes", default=None)
    subscribers_gained: Optional[NonNegativeInt] = Field(description="the number of subscribers the channel has gained", default=None)
    subscribers_lost: Optional[NonNegativeInt] = Field(description="the number of subscribers the channel has lost", default=None)











class VideoRequest(MediaRequest):
    pass
