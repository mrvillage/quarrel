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
    from typing import Any, Dict, List, Union

    from ..bot import Bot
    from ..enums import InteractionCallbackType
    from ..missing import Missing
    from ..models import Channel, Guild
    from ..state import State
    from ..structures.embed import Embed
    from ..types.interactions import Choice
    from ..types.interactions import Interaction as InteractionData
    from ..types.interactions import InteractionCallbackData
    from ..types.interactions import InteractionData as InteractionDataData
    from .component import Grid


class Interaction:
    __slots__ = (
        "_state",
        "bot",
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
        "target_id",
    )

    def __init__(self, data: InteractionData, state: State) -> None:
        self._state: State = state
        self.bot: Bot = state.bot
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
        guild = self.guild
        if member is not MISSING and guild is not None:
            member = Member(member, MISSING, guild, state)
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
                        value["user"] = users[key]
                        self.resolved["members"][int(key)] = guild.parse_member(
                            value, self.resolved["users"][int(key)], partial=True
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
            self.target_id: Missing[int] = utils.get_int_or_missing(
                self.data.get("target_id", MISSING)
            )

    @property
    def channel(self) -> Channel:
        ...

    @property
    def guild(self) -> Optional[Guild]:
        if self.guild_id is MISSING:
            return None
        return self._state.get_guild(self.guild_id)

    def get_user_from_resolved(self, id: int) -> Optional[User]:
        return self.resolved["users"].get(id)

    def get_member_from_resolved(self, id: int) -> Optional[Member]:
        return self.resolved["members"].get(id)

    def get_role_from_resolver(self, id: int) -> Optional[Role]:
        return self.resolved["roles"].get(id)

    def get_channel_from_resolved(self, id: int) -> Optional[Channel]:
        return self.resolved["channels"].get(id)

    def get_message_from_resolved(self, id: int) -> Optional[Message]:
        return self.resolved["messages"].get(id)

    async def respond(
        self,
        type: InteractionCallbackType,
        *,
        content: Missing[str] = MISSING,
        embed: Missing[Embed] = MISSING,
        embeds: Missing[List[Embed]] = MISSING,
        # allowed_mentions: Missing[AllowedMentions] = MISSING,
        ephemeral: Missing[bool] = MISSING,
        # attachments: Missing[Attachment] = MISSING,
        tts: Missing[bool] = MISSING,
        grid: Missing[Grid] = MISSING,
        choices: Missing[List[Choice]] = MISSING,
        # modal: Missing[Modal] = MISSING,
    ) -> None:
        data: InteractionCallbackData = {}
        if content is not MISSING:
            data["content"] = content
        if embed is not MISSING:
            data["embeds"] = [embed.to_payload()]
        if embeds is not MISSING:
            data["embeds"] = [i.to_payload() for i in embeds]
        if ephemeral is not MISSING:
            data["flags"] = 64
        if tts is not MISSING:
            data["tts"] = tts
        if grid is not MISSING:
            data["components"] = grid.to_payload()
        if choices is not MISSING:
            data["choices"] = choices
        await self.bot.http.create_interaction_response(
            self.id, self.token, {"type": type.value, "data": data}
        )
        if grid is not MISSING:
            grid.store(self.bot)

    async def get_original_response(self) -> Message:
        return Message(
            await self.bot.http.get_original_interaction_response(self.token),
            self.channel,
            self._state,
        )

    async def edit_original_response(
        self,
        *,
        content: Missing[str] = MISSING,
        embed: Missing[Embed] = MISSING,
        embeds: Missing[List[Embed]] = MISSING,
        # allowed_mentions: Missing[AllowedMentions] = MISSING,
        grid: Missing[Grid] = MISSING,
        # files: Missing[List[File]] = MISSING,
        # attachments: Missing[Attachment] = MISSING,
    ) -> Message:
        # TODO proper typing for editing
        data: Any = {}
        if content is not MISSING:
            data["content"] = content
        if embed is not MISSING:
            data["embeds"] = [embed.to_payload()]
        if embeds is not MISSING:
            data["embeds"] = [i.to_payload() for i in embeds]
        if grid is not MISSING:
            data["components"] = grid.to_payload()
        message = Message(
            await self.bot.http.edit_original_interaction_response(self.token, data),
            self.channel,
            self._state,
        )
        if grid is not MISSING:
            grid.store(self.bot)
        return message

    async def delete_original_response(self) -> None:
        return await self.bot.http.delete_original_interaction_response(self.token)

    async def send_followup(
        self,
        *,
        content: Missing[str],
        embed: Missing[Embed] = MISSING,
        embeds: Missing[List[Embed]] = MISSING,
        # allowed_mentions: Missing[AllowedMentions] = MISSING,
        ephemeral: Missing[bool] = MISSING,
        # attachments: Missing[Attachment] = MISSING,
        tts: Missing[bool] = MISSING,
        grid: Missing[Grid] = MISSING,
        # files: Missing[List[File]] = MISSING,
    ) -> Message:
        data: Any = {}
        if content is not MISSING:
            data["content"] = content
        if embed is not MISSING:
            data["embeds"] = [embed.to_payload()]
        if embeds is not MISSING:
            data["embeds"] = [i.to_payload() for i in embeds]
        if ephemeral is not MISSING:
            data["flags"] = 64
        if tts is not MISSING:
            data["tts"] = tts
        if grid is not MISSING:
            data["components"] = grid.to_payload()
        message = Message(
            await self.bot.http.create_followup_message(self.token, data),
            self.channel,
            self._state,
        )
        if grid is not MISSING:
            grid.store(self.bot)
        return message

    async def get_followup_message(self, message_id: int) -> Message:
        return Message(
            await self.bot.http.get_followup_message(self.token, message_id),
            self.channel,
            self._state,
        )

    async def edit_followup_message(
        self,
        message_id: int,
        *,
        content: Missing[str] = MISSING,
        embed: Missing[Embed] = MISSING,
        embeds: Missing[List[Embed]] = MISSING,
        # allowed_mentions: Missing[AllowedMentions] = MISSING,
        grid: Missing[Grid] = MISSING,
        # files: Missing[List[File]] = MISSING,
        # attachments: Missing[Attachment] = MISSING,
    ) -> Message:
        # TODO proper typing for editing
        data: Any = {}
        if content is not MISSING:
            data["content"] = content
        if embed is not MISSING:
            data["embeds"] = [embed.to_payload()]
        if embeds is not MISSING:
            data["embeds"] = [i.to_payload() for i in embeds]
        if grid is not MISSING:
            data["components"] = grid.to_payload()
        message = Message(
            await self.bot.http.edit_followup_message(self.token, message_id, data),
            self.channel,
            self._state,
        )
        if grid is not MISSING:
            grid.store(self.bot)
        return message

    async def delete_followup_message(self, message_id: int) -> None:
        return await self.bot.http.delete_followup_message(self.token, message_id)
