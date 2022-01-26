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
from ..enums import InteractionType
from ..missing import MISSING
from ..models import Member, Message, User

__all__ = ("Interaction",)

if TYPE_CHECKING:
    from typing import Union

    from ..models import Channels, Guild
    from ..state import State
    from ..types.interactions import Interaction as InteractionData
    from ..types.interactions import InteractionData as InteractionDataData


class Interaction:
    __slots__ = ()

    def __init__(self, data: InteractionData, state: State) -> None:
        self.id: int = int(data["id"])
        self.application_id: int = int(data["application_id"])
        self.type: InteractionType = InteractionType(data["type"])
        self.token: str = data["token"]

        self.data: InteractionDataData = data.get("data", MISSING)
        self.guild_id: int = utils.get_int_or_missing(data.get("guild_id", MISSING))
        self.channel_id: int = utils.get_int_or_missing(data.get("channel_id", MISSING))
        message = data.get("message", MISSING)
        member = data.get("member", MISSING)
        if member is not MISSING:
            member = Member(member, self.guild, state)
            self.user: Union[Member, User] = member
        else:
            user = User(data.get("user", MISSING), state)
            self.user: Union[Member, User] = user
        self.message: Message = (
            Message(message, self.channel, state) if message is not MISSING else MISSING
        )
        self.locale: str = data.get("locale", MISSING)
        self.guild_locale: str = data.get("guild_locale", MISSING)
        self._state: State = state

    @property
    def channel(self) -> Channels:
        ...

    @property
    def guild(self) -> Guild:
        ...
