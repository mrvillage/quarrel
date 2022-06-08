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

from enum import Enum

__all__ = (
    "GuildDefaultMessageNotificationLevel",
    "GuildExplicitContentFilter",
    "GuildMFALevel",
    "GuildVerificationLevel",
    "GuildNSFWLevel",
    "GuildPremiumTier",
    "StickerType",
    "StickerFormat",
    "ChannelType",
    "ApplicationCommandOptionType",
    "ApplicationCommandType",
    "InteractionType",
    "ComponentType",
    "ButtonStyle",
    "InteractionCallbackType",
    "Color",
    "TextInputStyle",
    "PermissionOverwriteType",
)


class GuildDefaultMessageNotificationLevel(Enum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class GuildExplicitContentFilter(Enum):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class GuildMFALevel(Enum):
    NONE = 0
    ELEVATED = 1


class GuildVerificationLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class GuildNSFWLevel(Enum):
    NONE = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class GuildPremiumTier(Enum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class StickerType(Enum):
    STANDARD = 1
    GUILD = 2


class StickerFormat(Enum):
    PNG = 1
    APNG = 2
    LOTTIE = 3


class ChannelType(Enum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class ApplicationCommandOptionType(Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10


class ApplicationCommandType(Enum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


class InteractionType(Enum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class ComponentType(Enum):
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3
    TEXT_INPUT = 4


class ButtonStyle(Enum):
    PRIMARY = 1
    BLURPLE = 1
    SECONDARY = 2
    GRAY = 2
    GREY = 2
    SUCCESS = 3
    GREEN = 3
    DANGER = 4
    RED = 4
    LINK = 5


class InteractionCallbackType(Enum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESPONSE = 8
    MODAL = 9


class Color(Enum):
    TEAL = 0x1ABC9C
    DARK_TEAL = 0x11806A
    BRAND_GREEN = 0x57F287
    GREEN = 0x2ECC71
    DARK_GREEN = 0x1F8B4C
    BLUE = 0x3498DB
    DARK_BLUE = 0x206694
    PURPLE = 0x9B59B6
    DARK_PURPLE = 0x71368A
    MAGENTA = 0xE91E63
    DARK_MAGENTA = 0xAD1457
    GOLD = 0xF1C40F
    DARK_GOLD = 0xC27C0E
    ORANGE = 0xE67E22
    DARK_ORANGE = 0xA84300
    BRAND_RED = 0xED4245
    RED = 0xE74C3C
    DARK_RED = 0x992D22
    LIGHT_GRAY = 0x979C9F
    LIGHT_GREY = LIGHT_GRAY
    DARK_GRAY = 0x607D8B
    DARK_GREY = DARK_GRAY
    OG_BLURPLE = 0x7289DA
    BLURPLE = 0x5865F2
    YELLOW = 0xFEE75C


class TextInputStyle(Enum):
    SHORT = 1
    PARAGRAPH = 2


class PermissionOverwriteType(Enum):
    ROLE = 0
    MEMBER = 1
