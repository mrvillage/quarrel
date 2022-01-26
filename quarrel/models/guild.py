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
from typing import TYPE_CHECKING

from .. import utils
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
from .emoji import Emoji
from .member import Member
from .role import Role
from .sticker import Sticker
from .voice_state import VoiceState

__all__ = ("Guild",)

if TYPE_CHECKING:
    import datetime
    from typing import Dict, List, Optional

    from ..state import State
    from ..types.gateway import GuildMembersChunk
    from ..types.guild import Guild as GuildData
    from ..types.guild import GuildFeature


class Guild:
    def __init__(self, data: GuildData, state: State) -> None:
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self._icon: Optional[str] = data["icon"]
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

        self.icon_hash: Optional[str] = data.get("icon_hash", MISSING)
        # self.owner
        # self.permissions
        self.widget_enabled: bool = data.get("widget_enabled", MISSING)
        self.widget_channel_id: Optional[int] = utils.get_int_or_none_or_missing(
            data.get("widget_channel_id", MISSING)
        )
        self.joined_at: datetime.datetime = utils.get_datetime_or_missing(
            data.get("joined_at", MISSING)
        )
        self.large: bool = data.get("large", MISSING)
        self.unavailable: bool = data.get("unavailable", MISSING)
        self.member_count: int = data.get("member_count", MISSING)
        self.max_presences: Optional[int] = data.get("max_presences", MISSING)
        self.max_members: int = data.get("max_members", MISSING)
        self.max_video_channel_users: int = data.get("max_video_channel_users", MISSING)
        self.approximate_member_count: int = data.get(
            "approximate_member_count", MISSING
        )
        self.approximate_presence_count: int = data.get(
            "approximate_presence_count", MISSING
        )
        # self.welcome_screen
        self.premium_progress_bar_enabled: bool = data["premium_progress_bar_enabled"]

        roles = [Role(i, self, state) for i in data["roles"]]
        self._roles: Dict[int, Role] = {r.id: r for r in roles}
        emojis = [Emoji(i, self, state) for i in data["emojis"]]
        self._emojis: Dict[int, Emoji] = {e.id: e for e in emojis if e.id is not None}

        voice_states = [VoiceState(i, state) for i in data.get("voice_states", [])]
        self.voice_states: Dict[int, VoiceState] = {v.user_id: v for v in voice_states}
        members = [Member(i, self, state) for i in data.get("members", [])]
        self._members: Dict[int, Member] = {m.id: m for m in members}
        # self.channels
        # self.threads
        # self.presences
        # self.stage_instances
        stickers = [Sticker(i, self, state) for i in data.get("stickers", [])]
        self.stickers: Dict[int, Sticker] = {s.id: s for s in stickers}
        # self.guild_scheduled_events

        self._state: State = state

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
                chunk = await queue.get()
            except asyncio.TimeoutError:
                break
            chunks.append(chunk)
            if len(chunks) == chunk["chunk_count"]:
                break

        self._state.bot.event_handler.chunks_queue.pop((self.id, nonce))

        for chunk in chunks:
            for member in chunk["members"]:
                mem = Member(member, self, self._state)
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
    def emojis(self) -> List[Emoji]:
        return list(self._emojis.values())

    def get_emoji(self, id: int, /) -> Optional[Emoji]:
        return self._emojis.get(id)

    @property
    def members(self) -> List[Member]:
        return list(self._members.values())

    def get_member(self, id: int, /) -> Optional[Member]:
        return self._members.get(id)

    @property
    def roles(self) -> List[Role]:
        return list(self._roles.values())

    def get_role(self, id: int, /) -> Optional[Role]:
        return self._roles.get(id)
