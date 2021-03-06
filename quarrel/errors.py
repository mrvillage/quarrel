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

__all__ = (
    "QuarrelException",
    "HTTPException",
    "BadRequest",
    "Unauthorized",
    "Forbidden",
    "NotFound",
    "MethodNotAllowed",
    "ServerError",
    "ConversionError",
    "OptionError",
    "CheckError",
)

if TYPE_CHECKING:
    from typing import Any, List

    from .interactions import Option
    from .missing import Missing


class QuarrelException(Exception):
    ...


class HTTPException(QuarrelException):
    ...


class BadRequest(HTTPException):
    ...


class Unauthorized(HTTPException):
    ...


class Forbidden(HTTPException):
    ...


class NotFound(HTTPException):
    ...


class MethodNotAllowed(HTTPException):
    ...


class ServerError(HTTPException):
    ...


class GatewayError(QuarrelException):
    ...


class InvalidSessionError(GatewayError):
    ...


class CommandError(QuarrelException):
    ...


class ConversionError(CommandError):
    def __init__(self, option: Option, value: Any, errors: List[Exception]) -> None:
        self.option: Option = option
        self.value: Missing[Any] = value
        self.errors: List[Exception] = errors


class OptionError(CommandError):
    def __init__(self, option: Option, value: Missing[Any], error: Exception) -> None:
        self.option: Option = option
        self.value: Missing[Any] = value
        self.error: Exception = error


class CheckError(CommandError):
    def __init__(self, error: Exception) -> None:
        self.error: Exception = error
