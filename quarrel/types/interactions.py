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

from typing import Dict, List, TypedDict, Union

from discord import Emoji

from .channel import Channel
from .member import Member, MemberWithUser
from .message import Message
from .role import Role
from .snowflake import Snowflake
from .user import User

__all__ = ("Interaction",)


class _InteractionDataResolvedOptional(TypedDict, total=False):
    users: Dict[Snowflake, User]
    members: Dict[Snowflake, Member]
    roles: Dict[Snowflake, Role]
    channels: Dict[Snowflake, Channel]
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
    custom_id: str
    component_type: int  # enum
    values: List[str]


class ComponentInteractionData(_ComponentInteractionDataOptional):
    ...


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
