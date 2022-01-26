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

from typing import TYPE_CHECKING, Generic, TypeVar

from .. import utils
from ..enums import ChannelType
from ..missing import MISSING

__all__ = (
    "Channel",
    "TextChannel",
    "DMChannel",
    "VoiceChannel",
    "CategoryChannel",
    "Thread",
    "StageChannel",
    "GuildChannel",
    "Channels",
    "ChannelFactory",
)

if TYPE_CHECKING:
    from typing import List, Optional, Union

    from ..state import State
    from ..types.channel import CategoryChannel as CategoryChannelData
    from ..types.channel import Channel as ChannelData
    from ..types.channel import DMChannel as DMChannelData
    from ..types.channel import NewsChannel as NewsChannelData
    from ..types.channel import StageChannel as StageChannelData
    from ..types.channel import StoreChannel as StoreChannelData
    from ..types.channel import TextChannel as TextChannelData
    from ..types.channel import Thread as ThreadData
    from ..types.channel import VoiceChannel as VoiceChannelData
    from ..types.permissions import PermissionOverwrite
    from .guild import Guild

T = TypeVar("T", bound="Union[TextChannel, VoiceChannel]")


class Channel(Generic[T]):
    def __new__(cls, data: ChannelData, guild: Optional[Guild], state: State) -> T:
        type = data["type"]
        if type in {0, 5}:
            return TextChannel(data, guild, state)  # type: ignore
        elif type == 1:
            return DMChannel(data, state)  # type: ignore
        elif type == 2:
            return VoiceChannel(data, guild, state)  # type: ignore
        elif type == 4:
            return CategoryChannel(data, guild, state)  # type: ignore
        elif type == 6:
            return StoreChannel(data, guild, state)  # type: ignore
        elif type in {10, 11, 12}:
            return Thread(data, guild, state)  # type: ignore
        elif type == 13:
            return StageChannel(data, guild, state)  # type: ignore
        raise TypeError(f"type {type} does not match known channel types")


class TextChannel:
    def __init__(
        self, data: Union[TextChannelData, NewsChannelData], guild: Guild, state: State
    ) -> None:
        self.id: int = int(data["id"])
        self.type: ChannelType = ChannelType(data["type"])
        self.guild_id: int = int(data["guild_id"])

        self.position: int = data.get("position", MISSING)
        self.permission_overwrites: List[PermissionOverwrite] = data.get(
            "permission_overwrites", []
        )
        self.name: str = data.get("name", MISSING)
        self.nsfw: bool = data.get("nsfw", MISSING)
        self.parent_id: Optional[int] = utils.get_int_or_none_or_missing(
            data.get("parent_id", MISSING)
        )


class DMChannel:
    def __init__(self, data: DMChannelData, state: State) -> None:
        ...


class VoiceChannel:
    def __init__(self, data: VoiceChannelData, guild: Guild, state: State) -> None:
        ...


class CategoryChannel:
    def __init__(self, data: CategoryChannelData, guild: Guild, state: State) -> None:
        ...


class StoreChannel:
    def __init__(self, data: StoreChannelData, guild: Guild, state: State) -> None:
        ...


class Thread:
    def __init__(self, data: ThreadData, guild: Guild, state: State) -> None:
        ...


class StageChannel:
    def __init__(self, data: StageChannelData, sguild: Guild, tate: State) -> None:
        ...


GuildChannel = Union[
    TextChannel, VoiceChannel, CategoryChannel, StoreChannel, Thread, StageChannel
]


Channels = Union[TextChannel, VoiceChannel]
ChannelFactory = Channel[Channels]
