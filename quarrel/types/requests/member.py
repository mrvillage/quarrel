from __future__ import annotations

from typing import List, Optional, TypedDict

from ..snowflake import Snowflake

__all__ = ("EditGuildMember",)


class _EditGuildMemberOptional(TypedDict, total=False):
    nick: Optional[str]
    roles: Optional[List[Snowflake]]
    mute: Optional[bool]
    deaf: Optional[bool]
    channel_id: Optional[Snowflake]
    communication_disabled_until: Optional[str]


class EditGuildMember(_EditGuildMemberOptional):
    ...
