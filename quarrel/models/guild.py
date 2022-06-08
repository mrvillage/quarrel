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

import asyncio
import secrets
from typing import TYPE_CHECKING, Set

from .. import utils
from ..asset import Asset
from ..enums import (
    GuildDefaultMessageNotificationLevel,
    GuildExplicitContentFilter,
    GuildMFALevel,
    GuildNSFWLevel,
    GuildPremiumTier,
    GuildVerificationLevel,
)
from ..flags import SystemChannelFlags
from ..missing import MISSING
from .channel import GuildChannel, GuildChannelFactory
from .emoji import Emoji
from .member import Member
from .role import Role
from .sticker import Sticker
from .user import User
from .voice_state import VoiceState

__all__ = ("Guild",)

if TYPE_CHECKING:
    import datetime
    from typing import Dict, List, Optional

    from ..enums import ChannelType
    from ..missing import Missing
    from ..state import State
    from ..structures import PermissionOverwrite
    from ..types import requests
    from ..types.channel import GuildChannel as GuildChannelData
    from ..types.gateway import GuildMembersChunk
    from ..types.guild import Guild as GuildData
    from ..types.guild import GuildFeature
    from ..types.member import Member as MemberData
    from ..types.role import Role as RoleData
    from .channel import CategoryChannel


class Guild:
    __slots__ = (
        "_state",
        "id",
        "name",
        "icon",
        "_splash",
        "_discovery_splash",
        "owner_id",
        "afk_channel_id",
        "afk_timeout",
        "verification_level",
        "default_message_notifications",
        "explicit_content_filter",
        "features",
        "mfa_level",
        "application_id",
        "system_channel_id",
        "system_channel_flags",
        "rules_channel_id",
        "vanity_url_code",
        "description",
        "_banner",
        "premium_tier",
        "premium_subscription_count",
        "preferred_locale",
        "public_updates_channel_id",
        "nsfw_level",
        "icon_hash",
        "widget_enabled",
        "widget_channel_id",
        "joined_at",
        "large",
        "unavailable",
        "member_count",
        "max_presences",
        "max_members",
        "max_video_channel_users",
        "approximate_member_count",
        "approximate_presence_count",
        "premium_progress_bar_enabled",
        "_roles",
        "_emojis",
        "_voice_states",
        "_members",
        "_channels",
        "_stickers",
        "_chunk_event",
    )

    def __init__(self, data: GuildData, state: State) -> None:
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(self, data: GuildData) -> Guild:
        self.name: str = data["name"]
        icon = data["icon"]
        self.icon: Optional[Asset] = (
            Asset.guild_icon(self.id, icon, http=self._state.bot.http)
            if icon is not MISSING and icon is not None
            else icon
        )
        self._splash: Optional[str] = data["splash"]
        self._discovery_splash: Optional[str] = data["discovery_splash"]
        self.owner_id: int = int(data["owner_id"])
        self.afk_channel_id: Optional[int] = utils.get_int_or_none(
            data["afk_channel_id"]
        )
        self.afk_timeout: int = data["afk_timeout"]
        self.verification_level: GuildVerificationLevel = GuildVerificationLevel(
            data["verification_level"]
        )
        self.default_message_notifications: GuildDefaultMessageNotificationLevel = (
            GuildDefaultMessageNotificationLevel(data["default_message_notifications"])
        )
        self.explicit_content_filter: GuildExplicitContentFilter = (
            GuildExplicitContentFilter(data["explicit_content_filter"])
        )
        self.features: List[GuildFeature] = data["features"]
        self.mfa_level: GuildMFALevel = GuildMFALevel(data["mfa_level"])
        self.application_id: Optional[int] = utils.get_int_or_none(
            data["application_id"]
        )
        self.system_channel_id: Optional[int] = utils.get_int_or_none(
            data["system_channel_id"]
        )
        self.system_channel_flags: SystemChannelFlags = SystemChannelFlags(
            data["system_channel_flags"]
        )
        self.rules_channel_id: Optional[int] = utils.get_int_or_none(
            data["rules_channel_id"]
        )
        self.vanity_url_code: Optional[str] = data["vanity_url_code"]
        self.description: Optional[str] = data["description"]
        self._banner: Optional[str] = data["banner"]
        self.premium_tier: GuildPremiumTier = GuildPremiumTier(data["premium_tier"])
        self.premium_subscription_count: int = data["premium_subscription_count"]
        self.preferred_locale: str = data["preferred_locale"]
        self.public_updates_channel_id: Optional[int] = utils.get_int_or_none(
            data["public_updates_channel_id"]
        )
        self.nsfw_level: GuildNSFWLevel = GuildNSFWLevel(data["nsfw_level"])

        self.icon_hash: Missing[Optional[str]] = data.get("icon_hash", MISSING)
        # self.owner
        # self.permissions
        self.widget_enabled: Missing[bool] = data.get("widget_enabled", MISSING)
        self.widget_channel_id: Missing[
            Optional[int]
        ] = utils.get_int_or_none_or_missing(data.get("widget_channel_id", MISSING))
        self.joined_at: Missing[datetime.datetime] = utils.get_datetime_or_missing(
            data.get("joined_at", MISSING)
        )
        self.large: Missing[bool] = data.get("large", MISSING)
        self.unavailable: Missing[bool] = data.get("unavailable", MISSING)
        self.member_count: Missing[int] = data.get("member_count", MISSING)
        self.max_presences: Missing[Optional[int]] = data.get("max_presences", MISSING)
        self.max_members: Missing[int] = data.get("max_members", MISSING)
        self.max_video_channel_users: Missing[int] = data.get(
            "max_video_channel_users", MISSING
        )
        self.approximate_member_count: Missing[int] = data.get(
            "approximate_member_count", MISSING
        )
        self.approximate_presence_count: Missing[int] = data.get(
            "approximate_presence_count", MISSING
        )
        # self.welcome_screen
        self.premium_progress_bar_enabled: bool = data["premium_progress_bar_enabled"]

        roles = [Role(i, self, self._state) for i in data["roles"]]
        self._roles: Dict[int, Role] = {r.id: r for r in roles}
        emojis = [Emoji(i, self, self._state) for i in data["emojis"]]
        self._emojis: Dict[int, Emoji] = {e.id: e for e in emojis if e.id is not None}

        voice_states = [
            VoiceState(i, self._state) for i in data.get("voice_states", [])
        ]
        self._voice_states: Dict[int, VoiceState] = {v.user_id: v for v in voice_states}
        members = [
            Member(i, MISSING, self, self._state) for i in data.get("members", [])
        ]
        self._members: Dict[int, Member] = {m.id: m for m in members}
        channels = [
            GuildChannelFactory(i, self, self._state)
            for i in [*data.get("channels", []), *data.get("threads", [])]
        ]
        self._channels: Dict[int, GuildChannel] = {c.id: c for c in channels if c}
        # self.presences
        # self.stage_instances
        stickers = [Sticker(i, self, self._state) for i in data.get("stickers", [])]
        self._stickers: Dict[int, Sticker] = {s.id: s for s in stickers}
        # self.guild_scheduled_events
        return self

    async def chunk(self) -> None:
        self._chunk_event = asyncio.Event()
        nonce = secrets.token_hex(16)
        await self._state.bot.gateway_handler.request_guild_members(
            self, nonce=nonce, presences=self._state.bot.intents.presences
        )
        queue: asyncio.Queue[GuildMembersChunk] = asyncio.Queue()
        self._state.bot.event_handler.chunks_queue[(self.id, nonce)] = queue
        chunks: List[GuildMembersChunk] = []
        while True:
            try:
                chunk = await asyncio.wait_for(queue.get(), timeout=15)
            except asyncio.TimeoutError:
                break
            chunks.append(chunk)
            if len(chunks) == chunk["chunk_count"]:
                break

        self._state.bot.event_handler.chunks_queue.pop((self.id, nonce))

        for chunk in chunks:
            for member in chunk["members"]:
                mem = Member(member, MISSING, self, self._state)
                self._members[mem.id] = mem
        self._chunk_event.set()
        self._chunk_event = None

    @property
    def chunked(self) -> bool:
        count = getattr(self, "_member_count", None)
        if count is None:
            return False
        return count == len(self._members)

    @property
    def chunking(self) -> bool:
        return self._chunk_event is not None

    async def wait_until_chunked(self) -> None:
        if self.chunked or self._chunk_event is None:
            return
        await self._chunk_event.wait()

    @property
    def channels(self) -> Set[GuildChannel]:
        return set(self._channels.values())

    def get_channel(self, id: int, /) -> Optional[GuildChannel]:
        return self._channels.get(id)

    def parse_channel(
        self, data: GuildChannelData, /, *, partial: bool = False
    ) -> Optional[GuildChannel]:
        id = int(data["id"])
        if (channel := self.get_channel(id)) is not None:
            return channel.update(data, partial=partial)  # type: ignore
        channel = GuildChannelFactory(data, self, self._state)
        if channel is not None:
            self._channels[channel.id] = channel
        return channel

    @property
    def emojis(self) -> Set[Emoji]:
        return set(self._emojis.values())

    def get_emoji(self, id: int, /) -> Optional[Emoji]:
        return self._emojis.get(id)

    @property
    def members(self) -> Set[Member]:
        return set(self._members.values())

    def get_member(self, id: int, /) -> Optional[Member]:
        return self._members.get(id)

    def parse_member(
        self,
        data: MemberData,
        user: Missing[User],
        /,
        *,
        id: Missing[int] = MISSING,
        partial: bool = False,
    ) -> Member:
        id = id or int(data.get("user", {"id": 0})["id"])
        if (member := self.get_member(id)) is not None:
            return member.update(data, partial=partial)  # type: ignore
        member = Member(data, user, self, self._state, id)
        self._members[member.id] = member
        return member

    @property
    def roles(self) -> Set[Role]:
        return set(self._roles.values())

    def get_role(self, id: int, /) -> Optional[Role]:
        return self._roles.get(id)

    def parse_role(self, data: RoleData, /, *, partial: bool = False) -> Role:
        id = int(data["id"])
        if (role := self.get_role(id)) is not None:
            return role.update(data, partial=partial)  # type: ignore
        role = Role(data, self, self._state)
        self._roles[role.id] = role
        return role

    async def create_channel(
        self,
        type: ChannelType,
        name: str,
        *,
        topic: Missing[str] = MISSING,
        parent: Missing[CategoryChannel] = MISSING,
        overwrites: Missing[List[PermissionOverwrite]] = MISSING,
    ) -> GuildChannel:
        data: requests.CreateGuildChannel = {"type": type.value, "name": name}
        if topic is not MISSING:
            data["topic"] = topic
        if parent is not MISSING:
            data["parent_id"] = parent.id
        if overwrites is not MISSING:
            data["permission_overwrites"] = [i.to_payload() for i in overwrites]
        channel = GuildChannelFactory(
            await self._state.bot.http.create_guild_channel(
                self.id,
                data,
            ),
            self,
            self._state,
        )
        if channel is not None:
            self._channels[channel.id] = channel
            return channel
        raise ValueError("Channel created with unknown type")
