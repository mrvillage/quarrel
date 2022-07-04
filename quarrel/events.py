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

import asyncio
import copy
import inspect
from typing import TYPE_CHECKING

from . import utils
from .interactions import Interaction
from .missing import MISSING
from .models import Guild, Member, Role, User
from .models.channel import GuildChannelFactory

__all__ = ("EventHandler",)

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Tuple

    from .bot import Bot
    from .models.channel import GuildChannel, Thread
    from .state import State
    from .types.channel import Channel as ChannelData
    from .types.channel import Thread as ThreadData
    from .types.gateway import GuildMembersChunk
    from .types.guild import Guild as GuildData
    from .types.interactions import Interaction as InteractionData
    from .types.member import Member as MemberData
    from .types.presence import PartialPresenceUpdate as PartialPresenceUpdateData
    from .types.role import Role as RoleData
    from .types.user import User as UserData


class EventHandler:
    def __init__(
        self, bot: Bot, loop: asyncio.AbstractEventLoop, *, chunk_guilds: bool = True
    ) -> None:
        self.bot: Bot = bot
        self.state: State = bot.state
        self.loop: asyncio.AbstractEventLoop = loop

        self.handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {
            name[7:].upper(): func
            for name, func in inspect.getmembers(self)
            if name.startswith("handle_")
        }

        self.guild_queue: Optional[asyncio.Queue[Guild]] = None
        self.chunk_guilds: bool = chunk_guilds
        self.chunks_queue: Dict[Tuple[int, str], asyncio.Queue[GuildMembersChunk]] = {}

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        self.bot.dispatch(event, *args, **kwargs)

    def handle(self, event: str, data: Dict[str, Any]):
        if event == "READY":
            self.bot.gateway_handler.session_id = data["session_id"]
        elif event == "RESUMED":
            ...

        handler = self.handlers.get(event)
        if handler is not None:
            handler(data)

    def handle_ready(self, data: Dict[str, Any]) -> None:
        self.bot.user = User(data["user"], self.state)
        self.state.add_user(self.bot.user)
        if self.guild_queue is None:
            self.guild_queue = asyncio.Queue()
        self.bot.loop.create_task(self.async_handle_ready(data))

    async def async_handle_ready(self, data: Dict[str, Any]) -> None:
        if self.guild_queue is None:
            self.guild_queue = asyncio.Queue()
        num_guilds = len(data.get("guilds", []))
        queue = self.guild_queue
        guilds: List[Guild] = []

        while True:
            try:
                guild = await asyncio.wait_for(queue.get(), timeout=15)
            except asyncio.TimeoutError:
                break
            if self.chunk_guilds:
                asyncio.create_task(guild.chunk())
            guilds.append(guild)
            if len(guilds) == num_guilds:
                break
        for guild in guilds:
            await guild.wait_until_chunked()
            self.state.add_guild(guild)
            self.dispatch("guild_available", guild)

        self.guild_queue = None
        self.dispatch("ready")

    def handle_resumed(self, data: Dict[str, Any]) -> None:
        ...

    def handle_guild_create(self, data: GuildData) -> None:
        if self.guild_queue is not None and data.get("unavailable") is False:
            self.guild_queue.put_nowait(Guild(data, self.state))
            return

        if data.get("unavailable") is True:
            return

        guild = Guild(data, self.state)
        self.state.add_guild(guild)

        if self.chunk_guilds:
            asyncio.create_task(self.async_handle_guild_create(guild))
        else:
            self.dispatch("guild_create", guild)

    def handle_guild_delete(self, data: GuildData) -> None:
        guild = self.state.get_guild(int(data["id"]))
        if guild is not None:
            self.state.remove_guild(guild)
            self.dispatch("guild_remove", guild)

    def handle_guild_update(self, data: GuildData) -> None:
        guild = self.state.get_guild(int(data["id"]))
        if guild is not None:
            guild.update(data)
            self.dispatch("guild_update", guild)

    async def async_handle_guild_create(self, guild: Guild) -> None:
        await guild.chunk()
        self.dispatch("guild_create", guild)

    def handle_guild_members_chunk(self, chunk: GuildMembersChunk) -> None:
        queue = self.chunks_queue[(int(chunk["guild_id"]), chunk.get("nonce", ""))]
        queue.put_nowait(chunk)

    def handle_interaction_create(self, data: InteractionData) -> None:
        self.dispatch("interaction_create", Interaction(data, self.state))

    def handle_user_update(self, data: UserData) -> None:
        if self.bot.user:
            self.bot.user.update(data)
            self.dispatch("user_update", self.bot.user)

    def handle_channel_create(self, data: ChannelData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            channel = GuildChannelFactory(data, guild, self.state)
            if channel is not None:
                guild._channels[channel.id] = channel
                self.dispatch("channel_create", channel)

    def handle_channel_delete(self, data: ChannelData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            channel = guild._channels.pop(int(data["id"]), None)
            if channel is not None:
                self.dispatch("channel_delete", channel)

    def handle_channel_update(self, data: ChannelData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            channel: Optional[GuildChannel] = guild._channels.get(int(data["id"]))
            if channel is not None:
                old = copy.copy(channel)
                # complaining about various missing fields because it's a union
                channel.update(data)  # type: ignore
                self.dispatch("channel_update", old, channel)

    def handle_thread_create(self, data: ThreadData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            channel = GuildChannelFactory(data, guild, self.state)
            if channel is not None:
                already_has = guild.get_channel(channel.id)
                guild._channels[channel.id] = channel
                if not already_has:
                    self.dispatch("thread_create", channel)

    def handle_thread_delete(self, data: ThreadData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            channel = guild._channels.pop(int(data["id"]), None)
            if channel is not None:
                self.dispatch("thread_delete", channel)

    def handle_thread_update(self, data: ThreadData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            # guild.get_channel union issues again
            channel: Optional[Thread] = guild.get_channel(int(data["id"]))  # type: ignore
            if channel is not None:
                old = copy.copy(channel)
                channel.update(data)
                self.dispatch("thread_update", old, channel)

    def handle_guild_member_add(self, data: MemberData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            member = Member(data, MISSING, guild, self.state)
            guild._members[member.id] = member
            self.dispatch("member_join", member)

    def handle_guild_member_remove(self, data: MemberData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            member = guild._members.pop(int(data.get("user", {"id": 0})["id"]), None)
            if member is not None:
                self.dispatch("member_remove", member)

    def handle_guild_member_update(self, data: MemberData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            member = guild.get_member(int(data.get("user", {"id": 0})["id"]))
            if member is not None:
                old = copy.copy(member)
                member.update(data)
                self.dispatch("member_update", old, member)

    def handle_guild_role_create(self, data: RoleData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            role = Role(data, guild, self.state)
            guild._roles[role.id] = role
            self.dispatch("role_create", role)

    def handle_guild_role_delete(self, data: RoleData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            role = guild._roles.pop(int(data["id"]), None)
            if role is not None:
                self.dispatch("role_delete", role)

    def handle_guild_role_update(self, data: RoleData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            role = guild._roles.get(int(data["id"]))
            if role is not None:
                old = copy.copy(role)
                role.update(data)
                self.dispatch("role_update", old, role)

    def handle_presence_update(self, data: PartialPresenceUpdateData) -> None:
        guild_id = utils.get_int_or_missing(data.get("guild_id", MISSING))
        guild = self.state.get_guild(guild_id or 0)
        if guild is not None:
            user_id = int(data["user"]["id"])
            member = guild.get_member(user_id)
            if member is not None:
                old = copy.copy(member.user)
                user = member.user.update_all_optional(data["user"])
                self.dispatch("user_update", old, user)
