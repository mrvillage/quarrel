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

from typing import TYPE_CHECKING

from ..enums import ApplicationCommandOptionType, ApplicationCommandType
from ..missing import MISSING
from .option import Options

__all__ = ("ApplicationCommand", "SlashCommand", "UserCommand", "MessageCommand")

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Coroutine,
        Dict,
        Final,
        List,
        Optional,
        TypeVar,
        Union,
    )

    from ..missing import Missing
    from ..models import Member, Message, User
    from ..types.interactions import Option as OptionData
    from ..types.interactions import PartialApplicationCommand as ApplicationCommandData
    from .interaction import Interaction
    from .option import Option, Options, OptionType

    Check = Callable[
        ["ApplicationCommand", Interaction, Options], Coroutine[Any, Any, Any]
    ]

    T = TypeVar("T", bound=Check)


def check(
    *,
    requires: Missing[Union[str, List[str]]] = MISSING,
    after_options: bool = True,
) -> Callable[[T], T]:
    if requires is MISSING:
        requires = []
    elif isinstance(requires, str):
        requires = [requires]
    __check_requires__ = requires
    __check_after_options__ = after_options

    def decorator(
        func: T,
    ) -> T:
        setattr(func, "__check_requires__", __check_requires__)
        setattr(func, "__check_after_options__", __check_after_options__)
        return func

    return decorator


class ApplicationCommand:
    type: ApplicationCommandType
    name: str
    description: str
    guilds: List[int]
    global_: bool

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        ...

    @classmethod
    def to_payload(cls) -> ApplicationCommandData:
        ...


class SlashCommand(ApplicationCommand):
    type: Final = ApplicationCommandType.CHAT_INPUT
    name: str
    description: str
    options: List[OptionType]
    parent: Optional[SlashCommand]
    checks: List[Check]

    def __init_subclass__(
        cls,
        name: str,
        description: str,
        options: Missing[List[OptionType]] = MISSING,
        parent: Optional[SlashCommand] = None,
        checks: Missing[List[Check]] = MISSING,
        guilds: Missing[List[int]] = MISSING,
        global_: Missing[bool] = MISSING,
    ) -> None:
        cls.name = name
        cls.description = description
        cls.options = options or []
        cls.parent = parent
        cls.checks = checks or []
        cls.guilds = guilds or []
        cls.global_ = global_ if global_ is not MISSING else not bool(guilds)

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        self = cls()
        arguments: Dict[str, OptionData] = {i.name: i for i in interaction.data.get("options", [])}  # type: ignore
        parameters: Dict[str, Option] = {i.name: i for i in cls.options}  # type: ignore
        options = Options()
        for check in cls.checks:
            requires: List[str] = getattr(check, "__check_requires__", [])
            for name in requires:
                if hasattr(options, name):
                    continue
                value = arguments.get(name, MISSING)
                if value is MISSING:
                    default = parameters[name].default
                    if callable(default):
                        default = await default(interaction, options)
                    else:
                        setattr(options, name, default)
                else:
                    setattr(
                        options,
                        name,
                        await parameters[name].parse(interaction, options, value),
                    )
            if not await check(self, interaction, options):
                return
        for name, param in parameters.items():
            if hasattr(options, name):
                continue
            value = arguments.get(name, MISSING)
            if value is MISSING:
                default = param.default
                if callable(default):
                    default = await default(interaction, options)
                else:
                    setattr(options, name, default)
            else:
                setattr(
                    options,
                    name,
                    await param.parse(interaction, options, value),
                )
        try:
            await self.callback(interaction, options)
        except Exception as e:
            raise e

    async def callback(self, interaction: Interaction, options: Options) -> Any:
        ...

    async def on_error(
        self, interaction: Interaction, options: Options, error: Exception
    ) -> None:
        ...

    @classmethod
    def to_payload(cls) -> ApplicationCommandData:
        options = [option.to_payload() for option in cls.options]
        return {
            "name": cls.name,
            "description": cls.description,
            "options": options,
            "type": cls.type.value
            if cls.parent is None
            else ApplicationCommandOptionType.SUB_COMMAND_GROUP.value
            if any(
                option["type"] == ApplicationCommandOptionType.SUB_COMMAND.value
                for option in options
            )
            else ApplicationCommandOptionType.SUB_COMMAND.value,
        }


class UserCommand(ApplicationCommand):
    type: Final = ApplicationCommandType.USER
    name: str
    description: str
    checks: List[Check]

    def __init_subclass__(
        cls,
        name: str,
        description: str,
        checks: Missing[List[Check]] = MISSING,
        guilds: Missing[List[int]] = MISSING,
        global_: Missing[bool] = MISSING,
    ) -> None:
        cls.name = name
        cls.description = description
        cls.checks = checks or []
        cls.guilds = guilds or []
        cls.global_ = global_ if global_ is not MISSING else not bool(guilds)

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        instance = cls()
        try:
            await instance.callback(interaction, user)
        except Exception as e:
            raise e

    async def callback(
        self, interaction: Interaction, user: Union[User, Member]
    ) -> Any:
        ...

    @classmethod
    def to_payload(cls) -> ApplicationCommandData:
        return {
            "name": cls.name,
            "description": cls.description,
            "type": cls.type.value,
        }


class MessageCommand(ApplicationCommand):
    type: Final = ApplicationCommandType.USER
    name: str
    description: str
    checks: List[Check]

    def __init_subclass__(
        cls,
        name: str,
        description: str,
        checks: Missing[List[Check]] = MISSING,
        guilds: Missing[List[int]] = MISSING,
        global_: Missing[bool] = MISSING,
    ) -> None:
        cls.name = name
        cls.description = description
        cls.checks = checks or []
        cls.guilds = guilds or []
        cls.global_ = global_ if global_ is not MISSING else not bool(guilds)

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        instance = cls()
        try:
            await instance.callback(interaction, message)
        except Exception as e:
            raise e

    async def callback(self, interaction: Interaction, message: Message) -> Any:
        ...

    @classmethod
    def to_payload(cls) -> ApplicationCommandData:
        return {
            "name": cls.name,
            "description": cls.description,
            "type": cls.type.value,
        }
