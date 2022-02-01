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

from typing import TYPE_CHECKING, List, Optional

from .. import utils
from ..enums import StickerFormat, StickerType
from ..missing import MISSING

__all__ = ("Sticker",)

if TYPE_CHECKING:
    from ..missing import Missing
    from ..state import State
    from ..types.sticker import Sticker as StickerData
    from .guild import Guild


class Sticker:
    def __init__(self, data: StickerData, guild: Guild, state: State) -> None:
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.description: Optional[str] = data["description"]
        self.tags: List[str] = data["tags"].split(",")
        self.type: StickerType = StickerType(data["type"])
        self.format_type: StickerFormat = StickerFormat(data["format_type"])

        self.pack_id: Missing[int] = utils.get_int_or_missing(data.get("pack_id", MISSING))
        self.available: Missing[bool] = data.get("available", MISSING)
        self.guild_id: Missing[int] = utils.get_int_or_missing(data.get("guild_id", MISSING))
        # self.user
        self.sort_value: Missing[int] = data.get("sort_value", MISSING)

        self.guild: Guild = guild
        self._state: State = state
