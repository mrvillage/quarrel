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

from ..missing import MISSING

__all__ = ("User",)

if TYPE_CHECKING:
    from typing import Optional

    from ..state import State
    from ..types.user import User as UserData


class User:
    def __init__(self, data: UserData, state: State) -> None:
        self.id: int = int(data["id"])
        self.username: str = data["username"]
        self.discriminator: str = data["discriminator"]
        self.avatar: Optional[str] = data["avatar"]

        self.bot: bool = data.get("bot", MISSING)
        self.system: bool = data.get("system", MISSING)
        self.banner: Optional[str] = data.get("banner", MISSING)
        self.accent_color: Optional[int] = data.get("accent_color", MISSING)
        self.verified: bool = data.get("verified", MISSING)
        self.email: Optional[str] = data.get("email", MISSING)
        self.public_flags: int = data.get("public_flags", 0)

        self._state: State = state
