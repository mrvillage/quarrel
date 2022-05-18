from __future__ import annotations

from typing import List, TypedDict

from ..embed import Embed
from ..interactions import Component
from ..snowflake import Snowflake

__all__ = ("CreateMessage",)


class _CreateMessageOptional(TypedDict, total=False):
    content: str
    tts: bool
    embeds: List[Embed]
    # allowed_mentions: AllowedMentions
    # message_reference: MessageReference
    components: List[Component]
    sticker_ids: List[Snowflake]
    # files: List[File]
    # attachments: List[Attachment]
    flags: int  # flags


class CreateMessage(_CreateMessageOptional):
    ...
