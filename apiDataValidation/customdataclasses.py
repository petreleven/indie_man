from dataclasses import dataclass
from typing import Optional


@dataclass
class StreamerValidation:
    name: str
    email: Optional[str] = None
    twitter: Optional[str] = None
    twitter_followers: Optional[int] = None
    instagram: Optional[str] = None
    instagram_followers: Optional[int] = None
    twitch_url: Optional[str] = None
    twitch_subs: Optional[str] = None
    youtube_url: Optional[str] = None
    youtube_subs: Optional[int] = None
    country: Optional[str] = None


@dataclass
class TestValid:
    name: str
    email: str | None
