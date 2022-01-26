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

import datetime
from typing import TYPE_CHECKING

from .missing import MISSING

__all__ = ("get_int_or_none", "get_int_or_missing", "get_int_or_none_or_missing", "get_datetime_or_missing", "get_datetime_or_none")

if TYPE_CHECKING:
    from typing import Any, Optional


def get_int_or_none(value: Optional[Any]) -> Optional[int]:
    if value is None:
        return None
    return int(value)


def get_int_or_missing(value: Any) -> int:
    if value is MISSING:
        return MISSING
    return int(value)


def get_int_or_none_or_missing(value: Optional[Any]) -> Optional[int]:
    if value is MISSING:
        return MISSING
    if value is None:
        return None
    return int(value)


def get_datetime_or_missing(value: Any) -> datetime.datetime:
    if value is MISSING:
        return MISSING
    return datetime.datetime.fromisoformat(value)


def get_datetime_or_none(value: Optional[Any]) -> Optional[datetime.datetime]:
    if value is None:
        return None
    return datetime.datetime.fromisoformat(value)
