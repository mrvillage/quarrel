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

__all__ = ("State",)

if TYPE_CHECKING:
    from typing import Dict, List, Optional

    from .bot import Bot
    from .models import Guild, User


class State:
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self._guilds: Dict[int, Guild] = {}
        self._users: Dict[int, User] = {}

    @property
    def guilds(self) -> List[Guild]:
        return list(self._guilds.values())

    def add_guild(self, guild: Guild, /) -> None:
        self._guilds[guild.id] = guild

    def get_guild(self, guild_id: int, /) -> Optional[Guild]:
        return self._guilds.get(guild_id)

    def remove_guild(self, guild: Guild, /) -> None:
        self._guilds.pop(guild.id)

    @property
    def users(self) -> List[User]:
        return list(self._users.values())

    def add_user(self, user: User, /) -> None:
        self._users[user.id] = user

    def get_user(self, user_id: int, /) -> Optional[User]:
        return self._users.get(user_id)

    def remove_user(self, user: User, /) -> None:
        self._users.pop(user.id)

    def try_add_user(self, user: User, /) -> User:
        if user.id not in self._users:
            self.add_user(user)
        return user
