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

from typing import TYPE_CHECKING, List

from .. import utils
from ..missing import MISSING

__all__ = ("Emoji",)

if TYPE_CHECKING:
    from typing import Optional

    from ..missing import Missing
    from ..state import State
    from ..types.emoji import Emoji as EmojiData
    from .guild import Guild
    from .role import Role
    from .user import User


class Emoji:
    __slots__ = (
        "guild",
        "_state",
        "id",
        "name",
        "roles",
        "user",
        "require_colons",
        "managed",
        "animated",
        "available",
    )

    def __init__(self, data: EmojiData, guild: Guild, state: State) -> None:
        self.guild: Guild = guild
        self._state: State = state
        self.id: Optional[int] = utils.get_int_or_none(data["id"])
        self.update(data)

    def update(self, data: EmojiData) -> Emoji:
        self.name: Optional[str] = data["name"]

        self.roles: List[Role] = [
            r
            for i in data.get("roles", [])
            if (r := self.guild.get_role(int(i))) is not None
        ]
        self.user: Missing[User] = (
            u
            if (ud := data.get("user", MISSING)) is not MISSING
            and (u := self._state.get_user(int(ud["id"]))) is not None
            else MISSING
        )
        self.require_colons: Missing[bool] = data.get("require_colons", MISSING)
        self.managed: Missing[bool] = data.get("managed", MISSING)
        self.animated: Missing[bool] = data.get("animated", MISSING)
        self.available: Missing[bool] = data.get("available", MISSING)
        return self
