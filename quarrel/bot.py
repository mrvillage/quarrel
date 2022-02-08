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
from typing import TYPE_CHECKING, Type

import aiohttp

from .enums import InteractionType
from .events import EventHandler
from .gateway import GatewayClosure, GatewayHandler, UnknownGatewayMessageType
from .http import HTTP
from .missing import MISSING
from .state import State

__all__ = ("Bot",)

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, TypeVar

    from .flags import Intents
    from .gateway import Gateway
    from .interactions import ApplicationCommand, Interaction
    from .missing import Missing
    from .models import User
    from .types.interactions import ApplicationCommandInteractionData

    CoroutineFunction = Callable[..., Coroutine[Any, Any, Any]]
    AC = TypeVar("AC", bound=Type[ApplicationCommand])
    CF = TypeVar("CF", bound=CoroutineFunction)


class Bot:
    def __init__(
        self,
        application_id: int,
        token: str,
        intents: Intents,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.application_id: int = application_id
        self.token: str = token
        self.intents: Intents = intents

        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.http: HTTP = HTTP(self.session, token, self.application_id, self.loop)
        self.listeners: Dict[str, Set[CoroutineFunction]] = {}
        self.state: State = State(self)
        self.user: Missing[User] = MISSING
        self.commands: Set[Type[ApplicationCommand]] = set()
        self.registered_commands: Dict[int, Type[ApplicationCommand]] = {}

    @property
    def gateway(self) -> Gateway:
        return self.gateway_handler.gateway

    async def connect(self):
        self.gateway_handler = await GatewayHandler.connect(self)
        self.event_handler = EventHandler(self, self.loop)
        while True:
            try:
                async for message in self.gateway_handler:
                    self.event_handler.handle(message["t"], message["d"])
            except UnknownGatewayMessageType:
                pass
            except GatewayClosure as e:
                if e.close_code not in {
                    4000,
                    4001,
                    4002,
                    4003,
                    4005,
                    4007,
                    4008,
                    4009,
                }:
                    raise
                self.state.clear_for_reconnect()
                await self.gateway_handler.reconnect()

    async def run(self):
        await self.register_application_commands()
        await self.connect()

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        try:
            coro = getattr(self, f"on_{event}")
            self.loop.create_task(coro(*args, **kwargs))
        except AttributeError:
            pass
        if listeners := self.listeners.get(event):
            for listener in listeners:
                self.loop.create_task(self._dispatch(event, listener, *args, **kwargs))

    async def _dispatch(
        self, event: str, coro: CoroutineFunction, *args: Any, **kwargs: Any
    ) -> None:
        try:
            await coro(*args, **kwargs)
        except Exception as e:
            self.dispatch("event_error", event, e, *args, **kwargs)

    def listener(self, name: Missing[str] = MISSING) -> Callable[[CF], CF]:
        def decorator(coro: CF) -> CF:
            if not asyncio.iscoroutinefunction(coro):
                raise TypeError("Decorated function must be a coroutine function")
            if not name and not coro.__name__.startswith("on_"):
                raise ValueError(
                    "Decorated function must have a name starting with 'on_'"
                )
            event = name or coro.__name__[3:]
            if listeners := self.listeners.get(event):
                listeners.add(coro)
            else:
                self.listeners[event] = {coro}
            return coro

        return decorator

    def event(self, coro: CF) -> CF:
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("Decorated function must be a coroutine function")
        if not coro.__name__.startswith("on_"):
            raise ValueError("Decorated function must have a name starting with 'on_'")
        setattr(self, coro.__name__, coro)
        return coro

    def command(self, command: AC) -> AC:
        self.add_command(command)
        return command

    def add_command(self, command: Type[ApplicationCommand]) -> Bot:
        self.commands.add(command)
        return self

    async def register_application_commands(self) -> None:
        commands = {i.name: i for i in self.commands if i.global_}
        if commands:
            registered = await self.http.bulk_upsert_global_application_commands(
                [i.to_payload() for i in commands.values()]
            )
            for command in registered:
                self.registered_commands[int(command["id"])] = commands[command["name"]]
        guild_commands: Dict[int, List[Type[ApplicationCommand]]] = {}
        for command in self.commands:
            for guild in command.guilds:
                if (commands_ := guild_commands.get(guild)) is None:
                    guild_commands[guild] = [command]
                else:
                    commands_.append(command)
        commands = {(j, i.name): i for i in self.commands for j in i.guilds}
        for guild, commands_ in guild_commands.items():
            registered = await self.http.bulk_upsert_guild_application_commands(
                guild, [i.to_payload() for i in commands_]
            )
            for command in registered:
                self.registered_commands[int(command["id"])] = commands[
                    (int(command.get("guild_id", 0)), command["name"])
                ]

    async def on_interaction_create(self, interaction: Interaction) -> None:
        await self.process_interaction(interaction)

    async def process_interaction(self, interaction: Interaction) -> None:
        if interaction.type is InteractionType.APPLICATION_COMMAND:
            data: ApplicationCommandInteractionData = interaction.data  # type: ignore
            command = self.registered_commands.get(int(data["id"]))
            if command is not None:
                await command.run_command(interaction)
        elif interaction.type is InteractionType.MESSAGE_COMPONENT:
            ...
        elif interaction.type is InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
            ...
