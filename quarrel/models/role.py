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

__all__ = ("Role",)

if TYPE_CHECKING:
    from ..state import State
    from ..types.role import Role as RoleData
    from ..types.role import RoleTags
    from .guild import Guild


class Role:
    def __init__(self, data: RoleData, guild: Guild, state: State) -> None:
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self._color: int = data["color"]
        self.hoist: bool = data["hoist"]
        self.position: int = data["position"]
        self._permissions: int = int(data["permissions"])
        self.managed: bool = data["managed"]
        self.mentionable: bool = data["mentionable"]

        self._icon: Optional[str] = data.get("icon", MISSING)
        self._unicode_emoji: Optional[str] = data.get("unicode_emoji", MISSING)
        self._tags: RoleTags = data.get("tags", MISSING)

        self.guild: Guild = guild
        self._state: State = state
