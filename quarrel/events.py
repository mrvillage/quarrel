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
import inspect
from typing import TYPE_CHECKING

from .interactions import Interaction
from .models import Guild, User

__all__ = ("EventHandler",)

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Tuple

    from .bot import Bot
    from .state import State
    from .types.gateway import GuildMembersChunk
    from .types.guild import Guild as GuildData
    from .types.interactions import Interaction as InteractionData


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

        if self.chunk_guilds:
            asyncio.create_task(self.async_handle_guild_create(guild))
        else:
            self.dispatch("guild_create", guild)

    async def async_handle_guild_create(self, guild: Guild) -> None:
        await guild.chunk()
        self.dispatch("guild_create", guild)

    def handle_guild_members_chunk(self, chunk: GuildMembersChunk) -> None:
        queue = self.chunks_queue[(int(chunk["guild_id"]), chunk.get("nonce", ""))]
        queue.put_nowait(chunk)

    def handle_interaction_create(self, data: InteractionData) -> None:
        self.dispatch("interaction_create", Interaction(data, self.state))
