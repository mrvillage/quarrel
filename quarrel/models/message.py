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

__all__ = ("Message",)

if TYPE_CHECKING:
    from typing import List, Optional

    from ..interactions import Grid
    from ..missing import Missing
    from ..state import State
    from ..structures.embed import Embed
    from ..types import requests
    from ..types.message import Message as MessageData
    from .channel import Channel


class Message:
    __slots__ = ("channel", "_state", "id", "channel_id")

    def __init__(
        self, data: MessageData, channel: Missing[Channel], state: State
    ) -> None:
        self.channel: Missing[Channel] = channel
        self._state: State = state
        self.id: int = int(data["id"])
        self.channel_id: int = int(data["channel_id"])
        self.update(data)

    def update(self, data: MessageData, *, partial: bool = False) -> Message:
        return self

    async def edit_message(
        self,
        *,
        content: Missing[Optional[str]] = MISSING,
        embed: Missing[Optional[Embed]] = MISSING,
        embeds: Missing[Optional[List[Embed]]] = MISSING,
        # allowed_mentions: Missing[AllowedMentions] = MISSING,
        # attachments: Missing[Attachment] = MISSING,
        grid: Missing[Grid] = MISSING,
        # files: Missing[List[File]] = MISSING,
    ) -> Message:
        data: requests.EditMessage = {}
        if content is not MISSING:
            data["content"] = content
        if embed is not MISSING:
            data["embeds"] = [embed.to_payload()] if embed is not None else None
        if embeds is not MISSING:
            data["embeds"] = (
                [i.to_payload() for i in embeds] if embeds is not None else None
            )
        if grid is not MISSING:
            data["components"] = grid.to_payload()
        message = Message(
            await self._state.bot.http.edit_message(self.channel_id, self.id, data),
            self.channel,
            self._state,
        )
        if grid is not MISSING:
            grid.store(self._state.bot)
        return message
