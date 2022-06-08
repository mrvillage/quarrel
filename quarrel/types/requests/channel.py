from __future__ import annotations

from typing import List, Optional, TypedDict

from ..embed import Embed
from ..interactions import Component
from ..snowflake import Snowflake

__all__ = ("CreateMessage", "EditMessage", "CreateGuildChannel", "EditChannel")


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


class _EditMessageOptional(TypedDict, total=False):
    content: Optional[str]
    embeds: Optional[List[Embed]]
    flags: Optional[int]
    # allowed_mentions: Optional[AllowedMentions]
    components: Optional[List[Component]]
    # files: Optional[List[File]]
    # attachments: Optional[List[Attachment]]


class EditMessage(_EditMessageOptional):
    ...


class _CreateGuildChannelOptional(TypedDict, total=False):
    type: int  # enum
    topic: str
    parent_id: Snowflake


class CreateGuildChannel(_CreateGuildChannelOptional):
    name: str


class _EditChannel(TypedDict, total=False):
    name: str
    parent_id: int
    topic: str


class EditChannel(_EditChannel):
    ...
