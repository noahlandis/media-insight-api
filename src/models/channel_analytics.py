from datetime import date
from typing import Literal, Optional, Set

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

ANALYTICS_FIELD_MAPPING = {
    "total_view_count": "views",
    "comment_count": "comments",
    "like_count": "likes",
    "dislike_count": "dislikes",
    "estimated_minutes_watched": "estimatedMinutesWatched",
    "average_view_duration": "averageViewDuration",
    "subscribers_gained": "subscribersGained",
    "subscribers_lost": "subscribersLost",
}


class ChannelAnalyticsRequest(BaseModel):

    data: Set[Literal[*tuple(ANALYTICS_FIELD_MAPPING.keys())]] = Field(description="the data the user wishes to see")

    start_date: Optional[date] = Field(
        description="start date for the analytics window",
        default=date(2005, 10, 1),
    )

    end_date: Optional[date] = Field(
        description="end date for the analytics window",
        default_factory=date.today,
    )

    @property
    def metrics(self) -> str:
        return ",".join(ANALYTICS_FIELD_MAPPING[field] for field in self.data)

class ChannelAnalyticsResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda field_name: ANALYTICS_FIELD_MAPPING[field_name]
    )
    total_view_count: Optional[NonNegativeInt] = Field(description="the total number of views the channel has from all videos (public + private + unlisted)", default=None)
    comment_count: Optional[NonNegativeInt] = Field(description="the number of comments the channel has", default=None)
    like_count: Optional[NonNegativeInt] = Field(description="the number of likes the channel has", default=None)
    dislike_count: Optional[NonNegativeInt] = Field(description="the number of dislikes the channel has", default=None)
    estimated_minutes_watched: Optional[NonNegativeInt] = Field(description="the channel's estimated watch time in minutes", default=None)
    average_view_duration: Optional[NonNegativeInt] = Field(description="the channel's average view duration in minutes", default=None)
    subscribers_gained: Optional[NonNegativeInt] = Field(description="the number of subscribers the channel has gained", default=None)
    subscribers_lost: Optional[NonNegativeInt] = Field(description="the number of subscribers the channel has lost", default=None)


