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

from ..missing import MISSING

__all__ = ("Option",)

if TYPE_CHECKING:
    from typing import Any, List, Sequence, TypeVar, Union

    from ..enums import ApplicationCommandOptionType, ChannelType
    from ..types.command import Choice
    from ..types.command import Option as OptionData
    from .command import SlashCommand, SlashCommandOptional
    from .interaction import Interaction

    OptionType = Union["Option[Options]", "SlashCommand[Options, SlashCommandOptional]"]
    O = TypeVar("O", bound="Options")


class Option(Generic[O]):
    __slots__ = (
        "type",
        "name",
        "description",
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
        default: Any = MISSING,
        choices: List[Choice] = MISSING,
        channel_types: Sequence[ChannelType] = MISSING,
        min_value: float = MISSING,
        max_value: float = MISSING,
        autocomplete: bool = MISSING,
    ):
        self.type: ApplicationCommandOptionType = type
        self.name: str = name
        self.description: str = description
        self.default: Any = default
        self.choices: List[Choice] = choices
        self.channel_types: Sequence[ChannelType] = channel_types
        self.min_value: float = min_value
        self.max_value: float = max_value
        self.autocomplete: bool = autocomplete

    async def autocomplete_callback(self, interaction: Interaction, options: O) -> Any:
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
            payload["choices"] = self.choices
        if self.channel_types is not MISSING:
            payload["channel_types"] = [i.value for i in self.channel_types]
        if self.min_value is not MISSING:
            payload["min_value"] = self.min_value
        if self.max_value is not MISSING:
            payload["max_value"] = self.max_value
        if self.autocomplete is not MISSING:
            payload["autocomplete"] = self.autocomplete
        return payload


class Options:
    ...
