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

from ..missing import MISSING
from .user import User

__all__ = ("Member",)

if TYPE_CHECKING:
    from typing import Union

    from ..missing import Missing
    from ..state import State
    from ..types.member import Member as MemberData
    from ..types.member import MemberWithUser as MemberWithUser
    from .guild import Guild


class Member:
    __slots__ = (
        "guild",
        "_state",
        "id",
        "joined_at",
        "deaf",
        "mute",
        "nickname",
        "_avatar",
        "premium_since",
        "pending",
        "user",
    )

    def __init__(
        self,
        data: Union[MemberData, MemberWithUser],
        guild: Guild,
        state: State,
        id: int = 0,
    ) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id = user_id if (user_id := int(data.get("user", {"id": 0})["id"])) else id

        self.update(data)

    def update(self, data: Union[MemberData, MemberWithUser]) -> Member:
        self.joined_at: str = data["joined_at"]
        self.deaf: bool = data["deaf"]
        self.mute: bool = data["mute"]

        self.nickname: Missing[Optional[str]] = data.get("nick", MISSING)
        self._avatar: Missing[Optional[str]] = data.get("avatar", MISSING)
        self.premium_since: Missing[Optional[str]] = data.get("premium_since", MISSING)
        self.pending: Missing[bool] = data.get("pending", MISSING)

        # only included when in an interaction object
        # self.permissions

        if (user := data.get("user", MISSING)) is not MISSING:
            self.user: Missing[User] = self._state.parse_user(user)
        else:
            self.user: Missing[User] = MISSING
        return self
