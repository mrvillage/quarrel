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

from typing import TYPE_CHECKING, Generic, TypeVar, Union

from .. import utils
from ..enums import ChannelType
from ..missing import MISSING

__all__ = (
    "RootChannel",
    "TextChannel",
    "DMChannel",
    "VoiceChannel",
    "CategoryChannel",
    "Thread",
    "StageChannel",
    "GuildChannel",
    "Channel",
    "ChannelFactory",
    "MessageGuildChannel",
    "MessageChannel",
    "TalkGuildChannel",
    "TalkChannel",
)

if TYPE_CHECKING:
    from typing import List, Optional

    from ..bot import Bot
    from ..interactions import Grid
    from ..missing import Missing
    from ..state import State
    from ..structures import Embed
    from ..types import requests
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
    from .message import Message

T = TypeVar("T", bound="Channel")


class RootChannel(Generic[T]):
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


class _BaseChannel:
    id: int
    _state: State
    bot: Bot
    __slots__ = ()

    async def create_message(
        self,
        *,
        content: Missing[str] = MISSING,
        embed: Missing[Embed] = MISSING,
        embeds: Missing[List[Embed]] = MISSING,
        # allowed_mentions: Missing[AllowedMentions] = MISSING,
        # attachments: Missing[Attachment] = MISSING,
        tts: Missing[bool] = MISSING,
        grid: Missing[Grid] = MISSING,
        # files: Missing[List[File]] = MISSING,
    ) -> Message:
        data: requests.CreateMessage = {}
        if content is not MISSING:
            data["content"] = content
        if embed is not MISSING:
            data["embeds"] = [embed.to_payload()]
        if embeds is not MISSING:
            data["embeds"] = [i.to_payload() for i in embeds]
        if tts is not MISSING:
            data["tts"] = tts
        if grid is not MISSING:
            data["components"] = grid.to_payload()
        message = Message(
            await self.bot.http.create_message(self.id, data),
            # BaseChannel will never be directly instantiated
            self,  # type: ignore
            self._state,
        )
        if grid is not MISSING:
            grid.store(self.bot)
        return message

    async def edit_message(
        self,
        message_id: int,
        *,
        content: Missing[Optional[str]] = MISSING,
        embed: Missing[Optional[Embed]] = MISSING,
        embeds: Missing[Optional[List[Embed]]] = MISSING,
        # allowed_mentions: Missing[AllowedMentions] = MISSING,
        # attachments: Missing[Attachment] = MISSING,
        grid: Missing[Grid] = MISSING,
        # files: Missing[List[File]] = MISSING,
    ) -> Message:
        data: requests.EditMessage = {}
        if content is not MISSING:
            data["content"] = content
        if embed is not MISSING:
            data["embeds"] = [embed.to_payload()] if embed is not None else None
        if embeds is not MISSING:
            data["embeds"] = (
                [i.to_payload() for i in embeds] if embeds is not None else None
            )
        if grid is not MISSING:
            data["components"] = grid.to_payload()
        message = Message(
            await self._state.bot.http.edit_message(self.id, message_id, data),
            # BaseChannel will never be directly instantiated
            self,  # type: ignore
            self._state,
        )
        if grid is not MISSING:
            grid.store(self._state.bot)
        return message


class TextChannel(_BaseChannel):
    __slots__ = (
        "guild",
        "_state",
        "id",
        "type",
        "guild_id",
        "position",
        "permission_overwrites",
        "name",
        "nsfw",
        "parent_id",
    )

    def __init__(
        self, data: Union[TextChannelData, NewsChannelData], guild: Guild, state: State
    ) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id: int = int(data["id"])
        self.guild_id: int = guild.id
        self.update(data)

    def update(
        self, data: Union[TextChannelData, NewsChannelData], /, *, partial: bool = False
    ) -> TextChannel:
        self.type: ChannelType = ChannelType(data["type"])

        self.position: Missing[int] = data.get("position", MISSING)
        self.permission_overwrites: List[PermissionOverwrite] = data.get(
            "permission_overwrites", []
        )
        self.name: Missing[str] = data.get("name", MISSING)
        self.nsfw: Missing[bool] = data.get("nsfw", MISSING)
        self.parent_id: Missing[Optional[int]] = utils.get_int_or_none_or_missing(
            data.get("parent_id", MISSING)
        )
        return self


class DMChannel(_BaseChannel):
    __slots__ = ("_state", "id")

    def __init__(self, data: DMChannelData, state: State) -> None:
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(self, data: DMChannelData, /, *, partial: bool = False) -> DMChannel:
        return self


class VoiceChannel(_BaseChannel):
    __slots__ = ("guild", "_state", "id")

    def __init__(self, data: VoiceChannelData, guild: Guild, state: State) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(
        self, data: VoiceChannelData, /, *, partial: bool = False
    ) -> VoiceChannel:
        return self


class CategoryChannel(_BaseChannel):
    __slots__ = ("guild", "_state", "id")

    def __init__(self, data: CategoryChannelData, guild: Guild, state: State) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(
        self, data: CategoryChannelData, /, *, partial: bool = False
    ) -> CategoryChannel:
        return self


class StoreChannel(_BaseChannel):
    __slots__ = ("guild", "_state", "id")

    def __init__(self, data: StoreChannelData, guild: Guild, state: State) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(
        self, data: StoreChannelData, /, *, partial: bool = False
    ) -> StoreChannel:
        return self


class Thread(_BaseChannel):
    __slots__ = ("guild", "_state", "id")

    def __init__(self, data: ThreadData, guild: Guild, state: State) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(self, data: ThreadData, /, *, partial: bool = False) -> Thread:
        return self


class StageChannel(_BaseChannel):
    __slots__ = ("guild", "_state", "id")

    def __init__(self, data: StageChannelData, guild: Guild, state: State) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(
        self, data: StageChannelData, /, *, partial: bool = False
    ) -> StageChannel:
        return self


GuildChannel = Union[
    TextChannel, VoiceChannel, CategoryChannel, StoreChannel, Thread, StageChannel
]
Channel = Union[GuildChannel, DMChannel]
ChannelFactory = RootChannel[Channel]
GuildChannelFactory = RootChannel[GuildChannel]
MessageGuildChannel = Union[TextChannel, VoiceChannel, Thread]
MessageChannel = Union[MessageGuildChannel, DMChannel]
TalkGuildChannel = Union[VoiceChannel, StageChannel]
TalkChannel = Union[TalkGuildChannel, DMChannel]
