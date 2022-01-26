"""
The MIT License (MIT)

Copyright (c) 2021-present Village

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from .channel import GuildChannel, Thread
from .emoji import Emoji
from .member import MemberWithUser
from .presence import PartialPresenceUpdate
from .role import Role
from .scheduled_events import GuildScheduledEvent
from .snowflake import Snowflake
from .stage_instance import StageInstance
from .sticker import Sticker
from .voice_state import VoiceState
from .welcome_screen import WelcomeScreen

__all__ = (
    "UnavailableGuild",
    "Guild",
)


class UnavailableGuild(TypedDict):
    id: Snowflake
    unavailable: bool


class _GuildOptional(TypedDict, total=False):
    icon_hash: Optional[str]
    owner: bool
    permissions: str
    widget_enabled: bool
    widget_channel_id: Optional[Snowflake]
    joined_at: str
    large: bool
    unavailable: bool
    member_count: int
    voice_states: List[VoiceState]
    members: List[MemberWithUser]
    channels: List[GuildChannel]
    threads: List[Thread]
    presence: List[PartialPresenceUpdate]
    max_presences: Optional[int]
    max_members: int
    max_video_channel_users: int
    approximate_member_count: int
    approximate_presence_count: int
    welcome_screen: WelcomeScreen
    stage_instances: List[StageInstance]
    stickers: List[Sticker]
    guild_scheduled_events: List[GuildScheduledEvent]


class Guild(_GuildOptional):
    id: Snowflake
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner_id: Snowflake
    afk_channel_id: Optional[Snowflake]
    afk_timeout: int
    verification_level: int  # enum
    default_message_notifications: int  # enum
    explicit_content_filter: int  # enum
    roles: List[Role]
    emojis: List[Emoji]
    features: List[GuildFeature]
    mfa_level: int  # enum
    application_id: Optional[Snowflake]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: Optional[Snowflake]
    vanity_url_code: Optional[str]
    description: Optional[str]
    banner: Optional[str]
    premium_tier: int  # enum
    premium_subscription_count: int
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]
    nsfw_level: int  # enum
    premium_progress_bar_enabled: bool


GuildFeature = Literal[
    "ANIMATED_ICON",
    "BANNER",
    "COMMERCE",
    "COMMUNITY",
    "DISCOVERABLE",
    "FEATUREABLE",
    "INVITE_SPLASH",
    "MEMBER_VERIFICATION_GATE_ENABLED",
    "MONETIZATION_ENABLED",
    "MORE_STICKERS",
    "NEWS",
    "PARTNERED",
    "PREVIEW_ENABLED",
    "PRIVATE_THREADS",
    "ROLE_ICONS",
    "SEVEN_DAY_THREAD_ARCHIVE",
    "THREE_DAY_THREAD_ARCHIVE",
    "VANITY_URL",
    "VERIFIED",
    "VIP_REGIONS",
    "WELCOME_SCREEN_ENABLED",
]
