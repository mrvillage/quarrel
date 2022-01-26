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

from typing import Any, Dict, List, TypedDict, Union

from .member import MemberWithUser
from .presence import PresenceUpdate
from .snowflake import Snowflake

__all__ = (
    "GatewayDispatch",
    "IdentifyPayloadData",
    "ResumePayloadData",
    "RequestGuildMembersPayloadData",
    "GuildMembersChunk",
)


class GatewayDispatch(TypedDict):
    op: int
    d: Dict[str, Any]
    s: int
    t: str


class _IdentifyPayloadDataOptional(TypedDict, total=False):
    shard: List[int]


class IdentifyPayloadData(_IdentifyPayloadDataOptional):
    token: str
    properties: Dict[str, str]
    compress: bool
    large_threshold: int
    # presence:
    intents: int


class ResumePayloadData(TypedDict):
    seq: int
    session_id: str
    token: str


class _RequestGuildMembersPayloadDataOptional(TypedDict, total=False):
    presences: bool
    nonce: str
    user_ids: Union[Snowflake, List[Snowflake]]
    query: str


class RequestGuildMembersPayloadData(_RequestGuildMembersPayloadDataOptional):
    guild_id: Snowflake
    limit: int


class _GuildMembersChunkOptional(TypedDict, total=False):
    not_found: List[Snowflake]
    presences: List[PresenceUpdate]
    nonce: str


class GuildMembersChunk(_GuildMembersChunkOptional):
    guild_id: Snowflake
    members: List[MemberWithUser]
    chunk_index: int
    chunk_count: int
