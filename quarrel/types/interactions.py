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

from typing import Dict, List, Literal, TypedDict, Union

from .channel import GuildChannel
from .emoji import Emoji
from .member import Member, MemberWithUser
from .message import Message
from .role import Role
from .snowflake import Snowflake
from .user import User

__all__ = (
    "InteractionData",
    "Interaction",
    "SelectOption",
    "PartialApplicationCommand",
    "ApplicationCommand",
    "Choice",
    "Option",
)


class _InteractionDataResolvedOptional(TypedDict, total=False):
    users: Dict[Snowflake, User]
    members: Dict[Snowflake, Member]
    roles: Dict[Snowflake, Role]
    channels: Dict[Snowflake, GuildChannel]
    messages: Dict[Snowflake, Message]


class InteractionDataResolved(_InteractionDataResolvedOptional):
    ...


class _InteractionDataApplicationCommandOptionOptional(TypedDict, total=False):
    value: Union[str, float]
    options: List[InteractionDataApplicationCommandOption]
    focused: bool


class InteractionDataApplicationCommandOption(
    _InteractionDataApplicationCommandOptionOptional
):
    name: str
    type: int  # enum


class _ApplicationCommandInteractionDataOptional(TypedDict, total=False):
    resolved: InteractionDataResolved
    options: List[InteractionDataApplicationCommandOption]


class ApplicationCommandInteractionData(_ApplicationCommandInteractionDataOptional):
    id: Snowflake
    name: str
    type: int  # enum


class _ComponentInteractionDataOptional(TypedDict, total=False):
    values: List[str]


class ComponentInteractionData(_ComponentInteractionDataOptional):
    custom_id: str
    component_type: int  # enum


class UserMessageCommandInteractionData(ApplicationCommandInteractionData):
    target_id: Snowflake


InteractionData = Union[
    ApplicationCommandInteractionData,
    ComponentInteractionData,
    UserMessageCommandInteractionData,
]


class _InteractionOptional(TypedDict, total=False):
    data: InteractionData
    guild_id: Snowflake
    channel_id: Snowflake
    member: MemberWithUser
    user: User
    message: Message
    locale: str
    guild_locale: str


class Interaction(_InteractionOptional):
    id: Snowflake
    application_id: Snowflake
    type: int  # enum
    token: str
    version: int


class _SelectOptionOptional(TypedDict, total=False):
    description: str
    emoji: Emoji
    default: bool


class SelectOption(_SelectOptionOptional):
    label: str
    value: str


class _PartialApplicationCommandOptional(TypedDict, total=False):
    options: List[Union[PartialApplicationCommand, Option]]


class PartialApplicationCommand(_PartialApplicationCommandOptional):
    type: int  # enum
    name: str
    description: str


class _ApplicationCommandOptional(TypedDict, total=False):
    guild_id: Snowflake
    default_permission: bool


class ApplicationCommand(PartialApplicationCommand, _ApplicationCommandOptional):
    id: Snowflake
    application_id: int
    version: Snowflake


class _ChoiceOptional(TypedDict, total=False):
    ...


class Choice(_ChoiceOptional):
    name: str
    value: Union[str, int, float]


class _OptionOptional(TypedDict, total=False):
    required: bool
    choices: List[Choice]
    options: List[Option]
    channel_types: List[int]  # List[enum]
    min_value: float
    max_value: float
    autocomplete: bool


class Option(_OptionOptional):
    type: int  # enum
    name: str
    description: str


class _ActionRowOptional(TypedDict, total=False):
    ...


class ActionRow(_ActionRowOptional):
    type: Literal[1]
    components: List[Component]


class _ButtonOptional(TypedDict, total=False):
    label: str
    emoji: Emoji
    custom_id: str
    url: str
    disabled: bool


class Button(_ButtonOptional):
    type: Literal[2]
    style: int  # enum


class _SelectMenuOptional(TypedDict, total=False):
    placeholder: str
    min_values: int
    max_values: int
    disabled: bool


class SelectMenu(_SelectMenuOptional):
    type: Literal[3]
    custom_id: str
    options: List[SelectOption]


Component = Union[ActionRow, Button, SelectMenu]
