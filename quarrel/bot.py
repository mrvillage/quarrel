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
import contextlib
from typing import TYPE_CHECKING, Type

import aiohttp

from . import utils
from .enums import InteractionType
from .events import EventHandler
from .gateway import GatewayClosure, GatewayHandler, UnknownGatewayMessageType
from .http import HTTP
from .missing import MISSING
from .models.message import Message
from .state import State

__all__ = ("Bot",)

if TYPE_CHECKING:
    import re
    from typing import (
        Any,
        Callable,
        Coroutine,
        Dict,
        List,
        Optional,
        Set,
        TypeVar,
        Union,
    )

    from .flags import Intents
    from .gateway import Gateway
    from .interactions import (
        ApplicationCommand,
        Component,
        Interaction,
        MessageCommand,
        Modal,
        UserCommand,
    )
    from .interactions.component import Grid
    from .missing import Missing
    from .models import Guild, User
    from .structures.embed import Embed
    from .types import requests
    from .types.interactions import (
        ApplicationCommandInteractionData,
        ComponentInteractionData,
        ModalSubmitInteractionData,
    )

    Command = Union[
        Type[ApplicationCommand[Any]], Type[UserCommand], Type[MessageCommand]
    ]
    CoroutineFunction = Callable[..., Coroutine[Any, Any, Any]]
    COM = TypeVar("COM", bound=Command)
    CF = TypeVar("CF", bound=CoroutineFunction)
    C = TypeVar("C", bound=Component)
    M = TypeVar("M", bound=Modal[Any])


def _get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.get_event_loop_policy().get_event_loop()


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

        self.loop: asyncio.AbstractEventLoop = loop or _get_event_loop()
        self.session: aiohttp.ClientSession
        self.http: HTTP
        self.listeners: Dict[str, Set[CoroutineFunction]] = {}
        self.state: State = State(self)
        self.user: Missing[User] = MISSING
        self.commands: Set[Command] = set()
        self.registered_commands: Dict[int, Command] = {}
        self.components: Dict[str, Component] = {}
        self.regex_components: Dict[re.Pattern[str], Component] = {}
        self.modals: Dict[str, Modal[Any]] = {}
        self.regex_modals: Dict[re.Pattern[str], Modal[Any]] = {}

    @property
    def gateway(self) -> Gateway:
        return self.gateway_handler.gateway

    async def connect(self) -> None:
        self.gateway_handler = await GatewayHandler.connect(self)
        self.event_handler = EventHandler(self, self.loop)
        while True:
            try:
                async for message in self.gateway_handler:
                    self.event_handler.handle(message["t"], message["d"])
            except UnknownGatewayMessageType:
                pass
            except GatewayClosure as e:
                if e.close_code in {
                    4004,
                    4010,
                    4011,
                    4012,
                    4013,
                    4014,
                }:
                    raise
                self.state.clear_for_reconnect()
                await self.gateway_handler.reconnect()

    async def run(self) -> None:
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.http: HTTP = HTTP(self.session, self.token, self.application_id, self.loop)
        await self.register_application_commands()
        await self.connect()

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        with contextlib.suppress(AttributeError):
            coro = getattr(self, f"on_{event}")
            self.loop.create_task(coro(*args, **kwargs))
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

    def command(self, command: COM) -> COM:
        self.add_command(command)
        return command

    def add_command(self, command: Command) -> Bot:
        self.commands.add(command)
        return self

    def component(self, component: Type[C]) -> Type[C]:
        self.add_component_from_class(component)
        return component

    def add_component(self, component: Component) -> Bot:
        if component.pattern is not MISSING:
            self.regex_components[component.pattern] = component
        elif component.custom_id is not MISSING:
            self.components[component.custom_id] = component
            component.start_timeout(self)
        return self

    def add_component_from_class(self, component: Type[C]) -> Type[C]:
        self.add_component(component())
        return component

    def modal(self, modal: Type[M]) -> Type[M]:
        self.add_modal_from_class(modal)
        return modal

    def add_modal(self, modal: Modal[Any]) -> Bot:
        if modal.pattern is not MISSING:
            self.regex_modals[modal.pattern] = modal
        elif modal.custom_id is not MISSING:
            self.modals[modal.custom_id] = modal
            modal.start_timeout(self)
        return self

    def add_modal_from_class(self, modal: Type[M]) -> Type[M]:
        # should pass no arguments to the init method
        self.add_modal(modal())  # type: ignore
        return modal

    async def register_application_commands(self) -> None:
        commands = {i.name: i for i in self.commands if i.global_}
        if commands:
            registered = await self.http.bulk_upsert_global_application_commands(
                [i.to_payload() for i in commands.values()]
            )
            for command in registered:
                self.registered_commands[int(command["id"])] = commands[command["name"]]
        guild_commands: Dict[int, List[Command]] = {}
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
            # will be an application command data, for some reason the type
            # checker things it is a component when the component processing
            # section is uncommented
            data: ApplicationCommandInteractionData = interaction.data  # type: ignore
            command = self.registered_commands.get(int(data["id"]))  # type: ignore
            if command is not None:
                try:
                    await command.run_command(interaction)
                except Exception as e:
                    utils.print_exception_with_header(
                        f"Ignoring exception while running command {command.name}:", e
                    )
        elif interaction.type is InteractionType.MESSAGE_COMPONENT:
            data: ComponentInteractionData = interaction.data  # type: ignore
            custom_id = data["custom_id"]
            component = self.components.get(custom_id)
            if component is not None:
                try:
                    return await component.run_component(interaction, {})
                except Exception as e:
                    return utils.print_exception_with_header(
                        f"Ignoring exception while processing component {component}:", e
                    )
            for pattern, component in self.regex_components.items():
                match = pattern.match(custom_id)
                if match is not None:
                    try:
                        return await component.run_component(
                            interaction, match.groupdict()
                        )
                    except Exception as e:
                        return utils.print_exception_with_header(
                            f"Ignoring exception while processing component {component}:",
                            e,
                        )
        elif interaction.type is InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
            ...
        elif interaction.type is InteractionType.MODAL_SUBMIT:
            data: ModalSubmitInteractionData = interaction.data  # type: ignore
            custom_id = data["custom_id"]
            modal = self.modals.get(custom_id)
            if modal is not None:
                try:
                    return await modal.run_modal(interaction, {})
                except Exception as e:
                    return utils.print_exception_with_header(
                        f"Ignoring exception while processing modal {modal}:", e
                    )
            for pattern, modal in self.regex_modals.items():
                match = pattern.match(custom_id)
                if match is not None:
                    try:
                        return await modal.run_modal(interaction, match.groupdict())
                    except Exception as e:
                        return utils.print_exception_with_header(
                            f"Ignoring exception while processing modal {modal}:", e
                        )

    async def edit_message(
        self,
        channel_id: int,
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
            await self.http.edit_message(channel_id, message_id, data),
            # BaseChannel will never be directly instantiated
            MISSING,  # type: ignore
            self.state,
        )
        if grid is not MISSING:
            grid.store(self)
        return message

    def get_guild(self, guild_id: int, /) -> Optional[Guild]:
        return self.state.get_guild(guild_id)

    def get_user(self, user_id: int, /) -> Optional[User]:
        return self.state.get_user(user_id)
