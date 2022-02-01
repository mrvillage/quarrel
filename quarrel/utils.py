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
import sys
import traceback
from typing import TYPE_CHECKING

from .missing import MISSING

__all__ = (
    "get_int_or_none",
    "get_int_or_missing",
    "get_int_or_none_or_missing",
    "get_datetime_or_missing",
    "get_datetime_or_none",
    "print_exception_with_header",
    "print_exception",
)

if TYPE_CHECKING:
    from typing import Any, Optional

    from .missing import Missing


def get_int_or_none(value: Optional[Any]) -> Optional[int]:
    return None if value is None else int(value)


def get_int_or_missing(value: Any) -> Missing[int]:
    return MISSING if value is MISSING else int(value)


def get_int_or_none_or_missing(value: Optional[Any]) -> Missing[Optional[int]]:
    if value is MISSING:
        return MISSING
    if value is None:
        return None
    return int(value)


def get_datetime_or_missing(value: Any) -> Missing[datetime.datetime]:
    if value is MISSING:
        return MISSING
    return datetime.datetime.fromisoformat(value)


def get_datetime_or_none(value: Optional[Any]) -> Optional[datetime.datetime]:
    return None if value is None else datetime.datetime.fromisoformat(value)


def print_exception_with_header(header: str, error: Exception) -> None:
    print(header, file=sys.stderr)
    print_exception(error)


def print_exception(error: Exception) -> None:
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
