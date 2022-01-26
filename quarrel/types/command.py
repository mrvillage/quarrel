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

from typing import List, TypedDict, Union

__all__ = ("ApplicationCommand",)


class _ApplicationCommandOptional(TypedDict, total=False):
    options: List[Union[ApplicationCommand, Option]]


class ApplicationCommand(_ApplicationCommandOptional):
    name: str
    description: str
    type: int  # enum


class _ChoiceOptional(TypedDict, total=False):
    ...


class Choice(_ChoiceOptional):
    name: str
    value: Union[str, int, float]


class _OptionOptional(TypedDict, total=False):
    required: bool
    choices: List[Choice]
    options: List[Option]
    channel_types: List[int]  # List[enum]
    min_value: float
    max_value: float
    autocomplete: bool


class Option(_OptionOptional):
    type: int  # enum
    name: str
    description: str
