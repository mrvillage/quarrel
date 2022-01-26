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

from typing import List, Literal, Optional, TypedDict, Union

from .permissions import PermissionOverwrite
from .snowflake import Snowflake
from .threads import ThreadMember, ThreadMetadata
from .user import User

__all__ = (
    "TextChannel",
    "DMChannel",
    "VoiceChannel",
    "GroupDMChannel",
    "CategoryChannel",
    "NewsChannel",
    "StoreChannel",
    "NewsThread",
    "PublicThread",
    "PrivateThread",
    "StageChannel",
    "Thread",
    "GuildChannel",
    "Channel",
)


class _BaseChannel(TypedDict):
    id: Snowflake


class _BaseGuildChannelOptional(TypedDict, total=False):
    position: int
    permissions_overwrites: List[PermissionOverwrite]
    name: str
    nsfw: bool
    parent_id: Optional[Snowflake]


class _BaseGuildChannel(_BaseChannel, _BaseGuildChannelOptional):
    guild_id: Snowflake


class _TextChannelOptional(TypedDict, total=False):
    topic: str
    last_message_id: Optional[Snowflake]
    last_pin_timestamp: Optional[str]
    rate_limit_per_user: int
    default_auto_archive_duration: int  # union type


class TextChannel(_BaseGuildChannel, _TextChannelOptional):
    type: Literal[0]


class _DMChannelOptional(TypedDict, total=False):
    last_message_id: Optional[Snowflake]
    recipients: List[User]
    last_pin_timestamp: Optional[str]


class DMChannel(_BaseChannel, _DMChannelOptional):
    type: Literal[1]


class _VoiceChannelOptional(TypedDict, total=False):
    bitrate: int
    user_limit: int
    rtc_region: Optional[str]
    video_quality_mode: int  # enum


class VoiceChannel(_BaseGuildChannel, _VoiceChannelOptional):
    type: Literal[2]


class _GroupDMChannelOptional(TypedDict, total=False):
    name: str
    last_message_id: Optional[Snowflake]
    recipients: List[User]
    icon: Optional[str]
    owner_id: Snowflake
    last_pin_timestamp: Optional[str]


class GroupDMChannel(_BaseChannel, _GroupDMChannelOptional):
    type: Literal[3]


class _CategoryChannelOptional(TypedDict, total=False):
    ...


class CategoryChannel(_BaseGuildChannel, _CategoryChannelOptional):
    type: Literal[4]


class _NewsChannelOptional(TypedDict, total=False):
    ...


class NewsChannel(_BaseGuildChannel, _NewsChannelOptional):
    type: Literal[5]


class _StoreChannelOptional(TypedDict, total=False):
    ...


class StoreChannel(_BaseGuildChannel, _StoreChannelOptional):
    type: Literal[6]


class _BaseThreadOptional(TypedDict, total=False):
    last_message_id: Optional[Snowflake]
    rate_limit_per_user: int
    owner_id: Snowflake
    # will never be None in a thread, type checker
    # does not allow overriding
    parent_id: Snowflake  # type: ignore
    last_pin_timestamp: str
    message_count: int
    member_count: int
    thread_metadata: ThreadMetadata
    member: ThreadMember


class _BaseThread(_BaseGuildChannel, _BaseThreadOptional):
    ...


class NewsThread(_BaseThread):
    type: Literal[10]


class PublicThread(_BaseThread):
    type: Literal[11]


class PrivateThread(_BaseThread):
    type: Literal[12]


class _StageChannelOptional(TypedDict, total=False):
    topic: str
    bitrate: int
    user_limit: int
    rtc_region: Optional[str]


class StageChannel(_BaseGuildChannel, _StageChannelOptional):
    type: Literal[13]


Thread = Union[NewsThread, PublicThread, PrivateThread]

GuildChannel = Union[
    TextChannel,
    VoiceChannel,
    CategoryChannel,
    NewsChannel,
    StoreChannel,
    Thread,
    StageChannel,
]
Channel = Union[DMChannel, GroupDMChannel, GuildChannel]
