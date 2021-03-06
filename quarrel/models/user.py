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

from .. import utils
from ..asset import Asset
from ..missing import MISSING

__all__ = ("User",)

if TYPE_CHECKING:
    from typing import Optional

    from ..missing import Missing
    from ..state import State
    from ..types.user import PartialUser as PartialUserData
    from ..types.user import User as UserData


class User:
    __slots__ = (
        "_state",
        "id",
        "username",
        "discriminator",
        "avatar",
        "bot",
        "system",
        "banner",
        "accent_color",
        "verified",
        "email",
        "public_flags",
    )

    def __init__(self, data: UserData, state: State) -> None:
        self._state: State = state
        self.id: int = int(data["id"])
        self.update(data)

    def update(self, data: UserData) -> User:
        self.username: str = data["username"]
        self.discriminator: str = data["discriminator"]
        avatar = data["avatar"]
        self.avatar: Optional[Asset] = (
            Asset.user_avatar(self.id, avatar, http=self._state.bot.http)
            if avatar is not None
            else None
        )

        self.bot: Missing[bool] = data.get("bot", MISSING)
        self.system: Missing[bool] = data.get("system", MISSING)
        self.banner: Missing[Optional[str]] = data.get("banner", MISSING)
        self.accent_color: Missing[Optional[int]] = data.get("accent_color", MISSING)
        self.verified: Missing[bool] = data.get("verified", MISSING)
        self.email: Missing[Optional[str]] = data.get("email", MISSING)
        self.public_flags: int = data.get("public_flags", 0)
        return self

    def update_all_optional(self, data: PartialUserData) -> User:
        self.username: str = utils.update_or_current(
            data.get("username", MISSING), self.username  # type: ignore
        )
        self.discriminator: str = utils.update_or_current(
            data.get("discriminator", MISSING), self.discriminator  # type: ignore
        )
        if "avatar" in data:
            avatar = data["avatar"]
            self.avatar: Optional[Asset] = (
                Asset.user_avatar(self.id, avatar, http=self._state.bot.http)
                if avatar is not None
                else None
            )

        self.bot: Missing[bool] = utils.update_or_current(
            data.get("bot", MISSING), self.bot
        )
        self.system: Missing[bool] = utils.update_or_current(
            data.get("system", MISSING), self.system
        )
        self.banner: Missing[Optional[str]] = utils.update_or_current(
            data.get("banner", MISSING), self.banner
        )
        self.accent_color: Missing[Optional[int]] = utils.update_or_current(
            data.get("accent_color", MISSING), self.accent_color
        )
        self.verified: Missing[bool] = utils.update_or_current(
            data.get("verified", MISSING), self.verified
        )
        self.email: Missing[Optional[str]] = utils.update_or_current(
            data.get("email", MISSING), self.email
        )
        self.public_flags: int = utils.update_or_current(
            data.get("public_flags", 0), self.public_flags
        )
        return self

    @property
    def display_avatar(self) -> Asset:
        return self.avatar or Asset.default_user_avatar(
            int(self.discriminator), http=self._state.bot.http
        )

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    @property
    def name(self) -> str:
        return f"{self.username}#{self.discriminator}"
