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
from ..missing import MISSING

__all__ = ("VoiceState",)

if TYPE_CHECKING:
    import datetime
    from typing import Optional

    from ..missing import Missing
    from ..state import State
    from ..types.voice_state import VoiceState as VoiceStateData


class VoiceState:
    def __init__(self, data: VoiceStateData, state: State) -> None:
        self.channel_id: Optional[int] = utils.get_int_or_none(data["channel_id"])
        self.user_id: int = int(data["user_id"])
        self.session_id: str = data["session_id"]
        self.deaf: bool = data["deaf"]
        self.mute: bool = data["mute"]
        self.self_deaf: bool = data["self_deaf"]
        self.self_mute: bool = data["self_mute"]
        self.self_video: bool = data["self_video"]
        self.suppress: bool = data["suppress"]
        self.request_to_speak_timestamp: Optional[
            datetime.datetime
        ] = utils.get_datetime_or_none(data["request_to_speak_timestamp"])

        self.guild_id: Missing[int] = utils.get_int_or_missing(
            data.get("guild_id", MISSING)
        )
        self.self_stream: Missing[bool] = data.get("self_stream", MISSING)
        self._state: State = state
