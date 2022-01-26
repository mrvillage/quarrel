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

from typing import TYPE_CHECKING, Generic

from ..enums import ApplicationCommandOptionType, ApplicationCommandType
from ..missing import MISSING

__all__ = ("ApplicationCommand", "SlashCommand", "UserCommand", "MessageCommand")

if TYPE_CHECKING:
    from typing import Any, Final, List, Optional, Type, TypeVar, Union

    from ..models import Member, Message, User
    from ..types.command import ApplicationCommand as ApplicationCommandData
    from .interaction import Interaction
    from .option import Options, OptionType

    SlashCommandOptional = Optional["Type[SlashCommand[Options, SlashCommandOptional]]"]
    SlashCommandType = Type["SlashCommand[Options, SlashCommandOptional]"]
    O = TypeVar("O", bound="Options")
    P = TypeVar("P", bound=SlashCommandOptional)


class ApplicationCommand:
    type: ApplicationCommandType
    name: str
    description: str

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        ...


class SlashCommand(ApplicationCommand, Generic[O, P]):
    type: Final = ApplicationCommandType.CHAT_INPUT
    name: str
    description: str
    options: List[OptionType]
    parent: Optional[P]

    def __init_subclass__(
        cls,
        name: str,
        description: str,
        options: List[OptionType] = MISSING,
        parent: Optional[P] = None,
    ) -> None:
        cls.name = name
        cls.description = description
        cls.options = options or []
        cls.parent = parent

    @classmethod
    async def run_command(cls, interaction: Interaction) -> None:
        instance = cls()
        options = ...
        try:
            await instance.callback(interaction, options)
        except Exception as e:
            raise e

    async def callback(self, interaction: Interaction, options: O) -> Any:
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


class UserCommand(ApplicationCommand, Generic[O, P]):
    type: Final = ApplicationCommandType.USER
    name: str
    description: str

    def __init_subclass__(
        cls,
        name: str,
        description: str,
    ) -> None:
        cls.name = name
        cls.description = description

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


class MessageCommand(ApplicationCommand, Generic[O, P]):
    type: Final = ApplicationCommandType.USER
    name: str
    description: str

    def __init_subclass__(
        cls,
        name: str,
        description: str,
    ) -> None:
        cls.name = name
        cls.description = description

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
