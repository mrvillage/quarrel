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

from typing import TYPE_CHECKING, Optional

from .. import utils
from ..enums import InteractionType
from ..missing import MISSING
from ..models import Member, Message, Role, User

__all__ = ("Interaction",)

if TYPE_CHECKING:
    from typing import Any, Dict, Union

    from ..missing import Missing
    from ..models import Channel, Guild
    from ..state import State
    from ..types.interactions import Interaction as InteractionData
    from ..types.interactions import InteractionData as InteractionDataData


class Interaction:
    __slots__ = (
        "id",
        "application_id",
        "type",
        "token",
        "data",
        "guild_id",
        "channel_id",
        "user",
        "message",
        "locale",
        "guild_locale",
        "resolved",
        "_state",
    )

    def __init__(self, data: InteractionData, state: State) -> None:
        self.id: int = int(data["id"])
        self.application_id: int = int(data["application_id"])
        self.type: InteractionType = InteractionType(data["type"])
        self.token: str = data["token"]

        self.data: Missing[InteractionDataData] = data.get("data", MISSING)
        self.guild_id: Missing[int] = utils.get_int_or_missing(
            data.get("guild_id", MISSING)
        )
        self.channel_id: Missing[int] = utils.get_int_or_missing(
            data.get("channel_id", MISSING)
        )
        message = data.get("message", MISSING)
        member = data.get("member", MISSING)
        self._state: State = state
        guild = self.guild
        if member is not MISSING and guild is not None:
            member = Member(member, guild, state)
            self.user: Union[Member, User] = member
        else:
            # there will always be a member or user included
            user = User(data["user"], state)  # type: ignore
            self.user: Union[Member, User] = user
        self.message: Missing[Message] = (
            Message(message, self.channel, state) if message is not MISSING else MISSING
        )
        self.locale: Missing[str] = data.get("locale", MISSING)
        self.guild_locale: Missing[str] = data.get("guild_locale", MISSING)
        self.resolved: Dict[str, Dict[int, Any]] = {
            "users": {},
            "members": {},
            "roles": {},
            "channels": {},
            "messages": {},
        }
        if self.data is not MISSING:
            resolved = self.data.get("resolved", {})
            if users := resolved.get("users", {}):
                for key, value in users.items():
                    self.resolved["users"][int(key)] = state.parse_user(value)
            if guild is not None:
                if members := resolved.get("members", {}):
                    for key, value in members.items():
                        self.resolved["members"][int(key)] = guild.parse_member(
                            value, partial=True
                        )
                if roles := resolved.get("roles", {}):
                    for key, value in roles.items():
                        self.resolved["roles"][int(key)] = guild.parse_role(value)
                if channels := resolved.get("channels", {}):
                    for key, value in channels.items():
                        self.resolved["channels"][int(key)] = guild.parse_channel(
                            value, partial=True
                        )
                if messages := resolved.get("messages", {}):
                    for key, value in messages.items():
                        channel = guild.get_channel(int(value["channel_id"])) or MISSING
                        self.resolved["messages"][int(key)] = state.parse_message(
                            channel, value, partial=True
                        )

    @property
    def channel(self) -> Channel:
        ...

    @property
    def guild(self) -> Optional[Guild]:
        if self.guild_id is MISSING:
            return None
        return self._state.get_guild(self.guild_id)

    def get_user_from_resolved(self, id: int) -> User:
        ...

    def get_member_from_resolved(self, id: int) -> Member:
        ...

    def get_role_from_resolver(self, id: int) -> Role:
        ...

    def get_channel_from_resolved(self, id: int) -> Channel:
        ...

    def get_message_from_resolved(self, id: int) -> Message:
        ...
