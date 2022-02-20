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

from typing import TYPE_CHECKING, Union

from .. import utils
from ..enums import ApplicationCommandOptionType, ApplicationCommandType
from ..errors import CheckError, ConversionError, OptionError
from ..missing import MISSING

__all__ = (
    "ApplicationCommand",
    "SlashCommand",
    "UserCommand",
    "MessageCommand",
    "Option",
    "Options",
)

if TYPE_CHECKING:
    from enum import Enum, EnumMeta
    from typing import (
        Any,
        Callable,
        Coroutine,
        Dict,
        Final,
        List,
        Optional,
        Sequence,
        Type,
        TypeVar,
        cast,
    )

    from ..enums import ChannelType
    from ..missing import Missing
    from ..models import Member, Message, User
    from ..types.interactions import Option as OptionData
    from ..types.interactions import PartialApplicationCommand as ApplicationCommandData
    from .interaction import Interaction

    SlashCommandCheck = Callable[
        ["SlashCommand", Interaction, "Options"], Coroutine[Any, Any, Any]
    ]
    UserCommandCheck = Callable[
        ["UserCommand", Interaction, Union[User, Member]],
        Coroutine[Any, Any, Any],
    ]
    MessageCommandCheck = Callable[
        ["MessageCommand", Interaction, Message], Coroutine[Any, Any, Any]
    ]

    SCC = TypeVar("SCC", bound=SlashCommandCheck)
    UCC = TypeVar("UCC", bound=UserCommandCheck)
    MCC = TypeVar("MCC", bound=MessageCommandCheck)
    OptionType = Union["Option", "Type[SlashCommand]"]
    NO = TypeVar("NO", bound="Options")
    Converter = Callable[[Interaction, "Options", Any], Coroutine[Any, Any, Any]]

ApplicationCommand = Union["SlashCommand", "UserCommand", "MessageCommand"]


def check(
    *,
    requires: Missing[Union[str, List[str]]] = MISSING,
    after_options: bool = True,
) -> Callable[[SCC], SCC]:
    if requires is MISSING:
        requires = []
    elif isinstance(requires, str):
        requires = [requires]
    __check_requires__ = requires
    __check_after_options__ = after_options

    def decorator(
        func: SCC,
    ) -> SCC:
        setattr(func, "__check_requires__", __check_requires__)
        setattr(func, "__check_after_options__", __check_after_options__)
        return func

    return decorator


class SlashCommand:
    type: Final = ApplicationCommandType.CHAT_INPUT
    name: str
    description: str
    guilds: List[int]
    global_: bool
    options: List[OptionType]
    parent: Optional[Type[SlashCommand]]
    checks: List[SlashCommandCheck]

    __slots__ = ()

    def __init_subclass__(
        cls,
        name: Missing[str] = MISSING,
        description: Missing[str] = MISSING,
        options: Missing[List[OptionType]] = MISSING,
        parent: Missing[Type[SlashCommand]] = MISSING,
        checks: Missing[List[SlashCommandCheck]] = MISSING,
        guilds: Missing[List[int]] = MISSING,
        global_: Missing[bool] = MISSING,
    ) -> None:
        cls.name = name or ""
        cls.description = description or ""
        cls.options = options or []
        # pyright has issues unpacking Unions with Type inside
        cls.parent = parent or None  # type: ignore
        if cls.parent is not None:
            cls.parent.options.append(cls)
        cls.checks = checks or []
        cls.guilds = guilds or []
        cls.global_ = global_ if global_ is not MISSING else not bool(guilds)

    @classmethod
    async def run_command(
        cls, interaction: Interaction, options_: Missing[List[OptionType]] = MISSING
    ) -> None:
        options_ = options_ or interaction.data.get("options", [])  # type: ignore
        if cls.options and cls.options[0].type is ApplicationCommandType.CHAT_INPUT:
            parameters: Dict[str, SlashCommand] = {i.name: i for i in cls.options}  # type: ignore
            await parameters[options_[0]["name"]].run_command(interaction, options_[0].get("options", []))  # type: ignore
        self = cls()
        arguments: Dict[str, OptionData] = {i.name: i for i in options_}  # type: ignore
        parameters: Dict[str, Option] = {i.name: i for i in cls.options}  # type: ignore
        options = Options()
        for check in cls.checks:
            requires: List[str] = getattr(check, "__check_requires__", [])
            for name in requires:
                if hasattr(options, name):
                    continue
                value = arguments.get(name, MISSING)
                option = parameters[name]
                try:
                    if value is MISSING:
                        default = option.default
                        if callable(default):
                            default = await default(interaction, options)
                        else:
                            setattr(options, name, default)
                    else:
                        setattr(
                            options,
                            name,
                            await option.parse(interaction, options, value),
                        )
                except Exception as e:
                    return await self.on_option_error(
                        interaction, options, e, option, value
                    )
            try:
                if not await check(self, interaction, options):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, options, e)
        for name, param in parameters.items():
            if hasattr(options, name):
                continue
            value = arguments.get(name, MISSING)
            try:
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
            except Exception as e:
                return await self.on_option_error(interaction, options, e, param, value)
        try:
            await self.callback(interaction, options)
        except Exception as e:
            return await self.on_error(interaction, options, e)

    async def callback(self, interaction: Interaction, options: Options) -> Any:
        ...

    async def on_error(
        self, interaction: Interaction, options: Options, error: Exception
    ) -> None:
        if isinstance(error, CheckError):
            utils.print_exception_with_header(
                f"Ignoring exception in check of command {self.name}:", error.error
            )
        if isinstance(error, OptionError):
            e = error.error
            if isinstance(e, ConversionError):
                es = e.errors
                utils.print_exception_with_header(
                    f"Ignoring exceptions while converting option {error.option.name} of command {self.name}:",
                    es[0],
                )
                for e in es[1:]:
                    utils.print_exception(e)
            else:
                utils.print_exception_with_header(
                    f"Ignoring exception while converting option {error.option.name} of command {self.name}:",
                    error,
                )
        else:
            utils.print_exception_with_header(
                f"Ignoring exception in command {self.name}:", error
            )

    async def on_option_error(
        self,
        interaction: Interaction,
        options: Options,
        error: Exception,
        option: Option,
        value: Missing[Any],
    ) -> None:
        await self.on_error(interaction, options, OptionError(option, value, error))

    async def on_check_error(
        self, interaction: Interaction, options: Options, error: Exception
    ) -> None:
        await self.on_error(interaction, options, CheckError(error))

    @classmethod
    def to_payload(cls) -> ApplicationCommandData:
        if not cls.name or not cls.description:
            raise ValueError("Command must have a name and description")
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

    @classmethod
    def add_check(
        cls,
        func: SlashCommandCheck,
        *,
        requires: Missing[Union[str, List[str]]] = MISSING,
        after_options: bool = True,
    ) -> Type[ApplicationCommand]:
        if requires is MISSING:
            requires = []
        elif isinstance(requires, str):
            requires = [requires]
        setattr(func, "__check_requires__", requires)
        setattr(func, "__check_after_options__", after_options)
        cls.checks.append(func)
        return cls

    @classmethod
    def check(
        cls,
        *,
        requires: Missing[Union[str, List[str]]] = MISSING,
        after_options: bool = True,
    ) -> Callable[[SCC], SCC]:
        def decorator(
            func: SCC,
        ) -> SCC:
            cls.add_check(func, requires=requires, after_options=after_options)
            return func

        return decorator


class UserCommand:
    type: Final = ApplicationCommandType.USER
    name: str
    guilds: List[int]
    global_: bool
    checks: List[UserCommandCheck]

    __slots__ = ()

    def __init_subclass__(
        cls,
        name: Missing[str] = MISSING,
        checks: Missing[List[UserCommandCheck]] = MISSING,
        guilds: Missing[List[int]] = MISSING,
        global_: Missing[bool] = MISSING,
    ) -> None:
        cls.name = name or ""
        cls.checks = checks or []
        cls.guilds = guilds or []
        cls.global_ = global_ if global_ is not MISSING else not guilds

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        self = cls()
        # for performance, just using type: ignore instead
        # of checks since the Member or User will be present
        user = interaction.get_member_from_resolved(interaction.target_id)  # type: ignore
        for check in cls.checks:
            try:
                if not await check(self, interaction, user):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, user, e)
        if user is None:
            user: User = interaction.get_user_from_resolved(interaction.target_id)  # type: ignore
        try:
            await self.callback(interaction, user)
        except Exception as e:
            return await self.on_error(interaction, user, e)

    async def callback(
        self, interaction: Interaction, user: Union[User, Member]
    ) -> Any:
        ...

    @classmethod
    def to_payload(cls) -> ApplicationCommandData:
        if not cls.name:
            raise ValueError("Command must have a name")
        return {
            "name": cls.name,
            "description": "",
            "type": cls.type.value,
        }

    async def on_error(
        self, interaction: Interaction, user: User, error: Exception
    ) -> None:
        if isinstance(error, CheckError):
            utils.print_exception_with_header(
                f"Ignoring exception in check of command {self.name}:", error.error
            )
        else:
            utils.print_exception_with_header(
                f"Ignoring exception in command {self.name}:", error
            )

    async def on_check_error(
        self, interaction: Interaction, user: User, error: Exception
    ) -> None:
        await self.on_error(interaction, user, CheckError(error))

    @classmethod
    def add_check(cls, func: UserCommandCheck) -> Type[ApplicationCommand]:
        cls.checks.append(func)
        return cls

    @classmethod
    def check(cls) -> Callable[[UCC], UCC]:
        def decorator(
            func: UCC,
        ) -> UCC:
            cls.add_check(func)
            return func

        return decorator


class MessageCommand:
    type: Final = ApplicationCommandType.USER
    name: str
    guilds: List[int]
    global_: bool
    checks: List[MessageCommandCheck]

    __slots__ = ()

    def __init_subclass__(
        cls,
        name: Missing[str] = MISSING,
        checks: Missing[List[MessageCommandCheck]] = MISSING,
        guilds: Missing[List[int]] = MISSING,
        global_: Missing[bool] = MISSING,
    ) -> None:
        cls.name = name or ""
        cls.checks = checks or []
        cls.guilds = guilds or []
        cls.global_ = global_ if global_ is not MISSING else not bool(guilds)

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        self = cls()
        # for performance, just using type: ignore instead
        # of checks since the Message will be present
        message: Message = interaction.get_message_from_resolved(interaction.target_id)  # type: ignore
        for check in cls.checks:
            try:
                if not await check(self, interaction, message):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, message, e)
        try:
            await self.callback(interaction, message)
        except Exception as e:
            return await self.on_error(interaction, message, e)

    async def callback(self, interaction: Interaction, message: Message) -> Any:
        ...

    @classmethod
    def to_payload(cls) -> ApplicationCommandData:
        if not cls.name:
            raise ValueError("Command must have a name")
        return {
            "name": cls.name,
            "description": "",
            "type": cls.type.value,
        }

    async def on_error(
        self, interaction: Interaction, message: Message, error: Exception
    ) -> None:
        if isinstance(error, CheckError):
            utils.print_exception_with_header(
                f"Ignoring exception in check of command {self.name}:", error.error
            )
        else:
            utils.print_exception_with_header(
                f"Ignoring exception in command {self.name}:", error
            )

    async def on_check_error(
        self, interaction: Interaction, message: Message, error: Exception
    ) -> None:
        await self.on_error(interaction, message, CheckError(error))

    @classmethod
    def add_check(cls, func: MessageCommandCheck) -> Type[ApplicationCommand]:
        cls.checks.append(func)
        return cls

    @classmethod
    def check(cls) -> Callable[[MCC], MCC]:
        def decorator(
            func: MCC,
        ) -> MCC:
            cls.add_check(func)
            return func

        return decorator


class Option:
    __slots__ = (
        "type",
        "name",
        "description",
        "converters",
        "default",
        "choices",
        "channel_types",
        "min_value",
        "max_value",
        "autocomplete",
    )

    def __init__(
        self,
        type: ApplicationCommandOptionType,
        name: str,
        description: str,
        converter: Missing[Converter] = MISSING,
        converters: Missing[List[Converter]] = MISSING,
        default: Any = MISSING,
        choices: Missing[EnumMeta] = MISSING,
        channel_types: Missing[Sequence[ChannelType]] = MISSING,
        min_value: Missing[float] = MISSING,
        max_value: Missing[float] = MISSING,
        autocomplete: Missing[bool] = MISSING,
    ):
        self.type: ApplicationCommandOptionType = type
        self.name: str = name
        self.description: str = description
        if (
            converter is not MISSING or converters is not MISSING
        ) and type is not ApplicationCommandOptionType.STRING:
            raise ValueError(
                "The converter and converters arguments are only valid for the STRING option type"
            )
        if converter is not MISSING and converters is not MISSING:
            raise ValueError("Only one of converter and converters can be specified")
        self.converters: List[Converter] = (
            [converter] if converter is not MISSING else converters
        ) or []

        self.default: Any = default
        self.choices: Missing[EnumMeta] = choices
        self.channel_types: Missing[Sequence[ChannelType]] = channel_types
        self.min_value: Missing[float] = min_value
        self.max_value: Missing[float] = max_value
        self.autocomplete: Missing[bool] = autocomplete

    async def autocomplete_callback(
        self, interaction: Interaction, options: Options
    ) -> Any:
        ...

    def to_payload(self) -> OptionData:
        payload: OptionData = {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
        }
        if self.default is not MISSING:
            payload["required"] = True
        if self.choices is not MISSING:
            if TYPE_CHECKING:
                self.choices = cast(Type[Enum], self.choices)
            payload["choices"] = [
                {"name": i.name, "value": i.value} for i in self.choices
            ]
        if self.channel_types is not MISSING:
            payload["channel_types"] = [i.value for i in self.channel_types]
        if self.min_value is not MISSING:
            payload["min_value"] = self.min_value
        if self.max_value is not MISSING:
            payload["max_value"] = self.max_value
        if self.autocomplete is not MISSING:
            payload["autocomplete"] = self.autocomplete
        return payload

    async def parse(
        self, interaction: Interaction, options: Options, value: Any
    ) -> Any:
        if self.type is ApplicationCommandOptionType.MENTIONABLE:
            id = int(value)
            if interaction.guild_id is not MISSING:
                if m := interaction.get_member_from_resolved(id):
                    value = m
                elif r := interaction.get_role_from_resolver(id):
                    value = r
            elif u := interaction.get_user_from_resolved(id):
                value = u
        elif self.type is ApplicationCommandOptionType.CHANNEL:
            id = int(value)
            if c := interaction.get_channel_from_resolved(id):
                value = c
        elif self.type is ApplicationCommandOptionType.USER:
            id = int(value)
            if m := interaction.get_member_from_resolved(id):
                value = m
            elif u := interaction.get_user_from_resolved(id):
                value = u
        elif self.type is ApplicationCommandOptionType.ROLE:
            id = int(value)
            if r := interaction.get_role_from_resolver(id):
                value = r
        if self.converters:
            errors: List[Exception] = []
            for converter in self.converters:
                try:
                    return await converter(interaction, options, value)
                except Exception as e:
                    errors.append(e)
            raise ConversionError(self, value, errors)
        return value


class Options:
    ...
