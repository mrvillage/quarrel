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

from .missing import MISSING, Missing

__all__ = ("Asset",)

if TYPE_CHECKING:
    from .http import HTTP


class Asset:
    __slots__ = ("path", "animated", "file_type", "size", "http")

    def __init__(
        self,
        path: str,
        animated: bool = False,
        file_type: str = "png",
        size: int = 0,
        *,
        http: HTTP,
    ) -> None:
        self.path: str = path
        self.animated: bool = animated
        self.file_type: str = file_type
        self.size: int = size
        self.http: HTTP = http

    @property
    def url(self) -> str:
        if self.size:
            return f"https://cdn.discordapp.com/{self.path}.{self.file_type}?size={self.size}"
        return f"https://cdn.discordapp.com/{self.path}.{self.file_type}"

    def clone(
        self, *, file_type: Missing[str] = MISSING, size: Missing[int] = MISSING
    ) -> Asset:
        return Asset(
            self.path,
            self.animated,
            file_type or self.file_type,
            size or self.size,
            http=self.http,
        )

    @classmethod
    def custom_emoji(cls, emoji_id: int, animated: bool, /, *, http: HTTP) -> Asset:
        return cls(
            f"emojis/{emoji_id}", animated, "gif" if animated else "png", 0, http=http
        )

    @classmethod
    def guild_icon(cls, guild_id: int, hash: str, /, *, http: HTTP) -> Asset:
        animated = hash.startswith("a_")
        return cls(
            f"icons/{guild_id}/{hash}",
            animated,
            "gif" if animated else "png",
            0,
            http=http,
        )

    @classmethod
    def guild_splash(cls, guild_id: int, hash: str, /, *, http: HTTP) -> Asset:
        return cls(f"splashes/{guild_id}/{hash}", http=http)

    @classmethod
    def guild_discovery_splash(
        cls, guild_id: int, hash: str, /, *, http: HTTP
    ) -> Asset:
        return cls(f"splashes/{guild_id}/{hash}", http=http)

    @classmethod
    def guild_banner(cls, guild_id: int, hash: str, /, *, http: HTTP) -> Asset:
        return cls(f"banners/{guild_id}/{hash}", http=http)

    @classmethod
    def user_banner(cls, user_id: int, hash: str, /, *, http: HTTP) -> Asset:
        animated = hash.startswith("a_")
        return cls(
            f"banners/{user_id}/{hash}",
            animated,
            "gif" if animated else "png",
            http=http,
        )

    @classmethod
    def default_user_avatar(cls, discriminator: int, /, *, http: HTTP) -> Asset:
        return cls(f"avatars/{discriminator%5}", http=http)

    @classmethod
    def user_avatar(cls, user_id: int, hash: str, /, *, http: HTTP) -> Asset:
        animated = hash.startswith("a_")
        return cls(
            f"avatars/{user_id}/{hash}",
            animated,
            "gif" if animated else "png",
            http=http,
        )

    @classmethod
    def guild_member_avatar(
        cls, guild_id: int, user_id: int, hash: str, /, *, http: HTTP
    ) -> Asset:
        animated = hash.startswith("a_")
        return cls(
            f"guilds/{guild_id}/users/{user_id}avatars/{hash}",
            animated,
            "gif" if animated else "png",
            http=http,
        )

    @classmethod
    def application_icon(
        cls, application_id: int, hash: str, /, *, http: HTTP
    ) -> Asset:
        animated = hash.startswith("a_")
        return cls(
            f"app-icons/{application_id}/{hash}",
            animated,
            "gif" if animated else "png",
            http=http,
        )

    @classmethod
    def application_cover_image(
        cls, application_id: int, hash: str, /, *, http: HTTP
    ) -> Asset:
        return cls(f"app-icons/{application_id}/{hash}", http=http)

    @classmethod
    def application_asset(
        cls, application_id: int, hash: str, /, *, http: HTTP
    ) -> Asset:
        return cls(f"app-assets/{application_id}/{hash}", http=http)

    @classmethod
    def achievement_icon(
        cls, application_id: int, achievement_id: int, hash: str, /, *, http: HTTP
    ) -> Asset:
        return cls(
            f"app-assets/{application_id}/achievements/{achievement_id}/icons/{hash}",
            http=http,
        )

    @classmethod
    def sticker_pack_banner(cls, banner_id: int, /, *, http: HTTP) -> Asset:
        return cls(f"app-assets/710982414301790216/store/{banner_id}", http=http)

    @classmethod
    def team_icon(cls, team_id: int, hash: str, /, *, http: HTTP) -> Asset:
        return cls(f"team-icons/{team_id}/{hash}", http=http)

    @classmethod
    def sticker(cls, sticker_id: int, /, *, http: HTTP) -> Asset:
        return cls(f"stickers/{sticker_id}", http=http)

    @classmethod
    def role_icon(cls, role_id: int, hash: str, /, *, http: HTTP) -> Asset:
        return cls(f"roles/{role_id}/{hash}", http=http)

    @classmethod
    def guild_scheduled_event_cover(
        cls, event_id: int, hash: str, /, *, http: HTTP
    ) -> Asset:
        return cls(f"scheduled-events/{event_id}/{hash}", http=http)

    async def read(self) -> bytes:
        async with self.http.session.request("GET", self.url) as response:
            return await response.read()
