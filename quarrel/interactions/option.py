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

from ..enums import ApplicationCommandOptionType
from ..errors import ConversionError
from ..missing import MISSING

__all__ = ("Option", "Options")

if TYPE_CHECKING:
    from enum import Enum, EnumMeta
    from typing import (
        Any,
        Callable,
        Coroutine,
        List,
        Sequence,
        Type,
        TypeVar,
        Union,
        cast,
    )

    from ..enums import ChannelType
    from ..missing import Missing
    from ..types.interactions import Option as OptionData
    from .command import SlashCommand
    from .interaction import Interaction

    OptionType = Union["Option", "SlashCommand"]
    NO = TypeVar("NO", bound="Options")
    Converter = Callable[[Interaction, "Options", Any], Coroutine[Any, Any, Any]]


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
                    return m
                if r := interaction.get_role_from_resolver(id):
                    return r
            if u := interaction.get_user_from_resolved(id):
                return u
        elif self.type is ApplicationCommandOptionType.CHANNEL:
            id = int(value)
            if c := interaction.get_channel_from_resolved(id):
                return c
        elif self.type is ApplicationCommandOptionType.USER:
            id = int(value)
            if m := interaction.get_member_from_resolved(id):
                return m
            if u := interaction.get_user_from_resolved(id):
                return u
        elif self.type is ApplicationCommandOptionType.ROLE:
            id = int(value)
            if r := interaction.get_role_from_resolver(id):
                return r
        elif self.type is ApplicationCommandOptionType.STRING and self.converters:
            errors: List[Exception] = []
            for converter in self.converters:
                try:
                    return await converter(interaction, options, value)
                except Exception as e:
                    errors.append(e)
            raise ConversionError(self, value, errors)
        else:
            return value


class Options:
    ...
