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

from typing import TYPE_CHECKING, overload

__all__ = ("Intents", "SystemChannelFlags", "Permissions")

if TYPE_CHECKING:
    from typing import Any, Callable, Optional, Type, TypeVar

    T = TypeVar("T", bound="Flags")


class flag:  # noqa: N801
    def __init__(self, func: Callable[[Any], int]):
        self.flag: int = func(None)
        self.__doc__: Optional[str] = func.__doc__

    @overload
    def __get__(self, instance: None, owner: Type[T]) -> T:
        ...

    @overload
    def __get__(self, instance: Flags, owner: Type[T]) -> bool:
        ...

    def __get__(self, instance: Optional[Flags], owner: Type[T]) -> Any:
        return self if instance is None else bool(instance.value & self.flag)

    def __set__(self, instance: Flags, value: bool) -> None:
        if value:
            instance.value |= self.flag
        else:
            instance.value &= ~self.flag


class Flags:
    __slots__ = ("value",)

    def __init__(self, value: int = 0, **kwargs: bool) -> None:
        self.value: int = value

        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    @classmethod
    def from_kwargs(cls, **kwargs: bool) -> Flags:
        flags = cls(0)
        for flag, value in kwargs.items():
            setattr(flags, flag, value)
        return flags

    @classmethod
    def none(cls: Type[T]) -> T:
        return cls(0)

    @classmethod
    def all(cls: Type[T]) -> T:
        return cls(-1)


class Intents(Flags):
    @flag
    def guilds(self) -> int:
        return 1 << 0

    @flag
    def members(self) -> int:
        return 1 << 1

    @flag
    def bans(self) -> int:
        return 1 << 2

    @flag
    def emojis_and_stickers(self) -> int:
        return 1 << 3

    @flag
    def integrations(self) -> int:
        return 1 << 4

    @flag
    def webhooks(self) -> int:
        return 1 << 5

    @flag
    def invites(self) -> int:
        return 1 << 6

    @flag
    def voice_states(self) -> int:
        return 1 << 7

    @flag
    def presences(self) -> int:
        return 1 << 8

    @flag
    def guild_messages(self) -> int:
        return 1 << 9

    @flag
    def guild_reactions(self) -> int:
        return 1 << 10

    @flag
    def guild_typing(self) -> int:
        return 1 << 11

    @flag
    def direct_messages(self) -> int:
        return 1 << 12

    @flag
    def direct_message_reactions(self) -> int:
        return 1 << 13

    @flag
    def direct_message_typing(self) -> int:
        return 1 << 14

    @flag
    def message_content(self) -> int:
        return 1 << 15

    @flag
    def guild_scheduled_events(self) -> int:
        return 1 << 16


class SystemChannelFlags(Flags):
    @flag
    def suppress_join_notifications(self) -> int:
        return 1 << 0

    @flag
    def suppress_premium_subscriptions(self) -> int:
        return 1 << 1

    @flag
    def suppress_guild_reminder_notifications(self) -> int:
        return 1 << 2

    @flag
    def suppress_join_notification_replies(self) -> int:
        return 1 << 3


class Permissions(Flags):
    @flag
    def create_instant_invite(self) -> int:
        return 1 << 0

    @flag
    def kick_members(self) -> int:
        return 1 << 1

    @flag
    def ban_members(self) -> int:
        return 1 << 2

    @flag
    def administrator(self) -> int:
        return 1 << 3

    @flag
    def manage_channels(self) -> int:
        return 1 << 4

    @flag
    def manage_guild(self) -> int:
        return 1 << 5

    @flag
    def add_reactions(self) -> int:
        return 1 << 6

    @flag
    def view_audit_log(self) -> int:
        return 1 << 7

    @flag
    def priority_speaker(self) -> int:
        return 1 << 8

    @flag
    def stream(self) -> int:
        return 1 << 9

    @flag
    def view_channel(self) -> int:
        return 1 << 10

    @flag
    def send_messages(self) -> int:
        return 1 << 11

    @flag
    def send_tts_messages(self) -> int:
        return 1 << 12

    @flag
    def manage_messages(self) -> int:
        return 1 << 13

    @flag
    def embed_links(self) -> int:
        return 1 << 14

    @flag
    def attach_files(self) -> int:
        return 1 << 15

    @flag
    def read_message_history(self) -> int:
        return 1 << 16

    @flag
    def mention_everyone(self) -> int:
        return 1 << 17

    @flag
    def use_external_emojis(self) -> int:
        return 1 << 18

    @flag
    def view_guild_insights(self) -> int:
        return 1 << 19

    @flag
    def connect(self) -> int:
        return 1 << 20

    @flag
    def speak(self) -> int:
        return 1 << 21

    @flag
    def mute_members(self) -> int:
        return 1 << 22

    @flag
    def deafen_members(self) -> int:
        return 1 << 23

    @flag
    def move_members(self) -> int:
        return 1 << 24

    @flag
    def use_vad(self) -> int:
        return 1 << 25

    @flag
    def change_nickname(self) -> int:
        return 1 << 26

    @flag
    def manage_nicknames(self) -> int:
        return 1 << 27

    @flag
    def manage_roles(self) -> int:
        return 1 << 28

    @flag
    def manage_webhooks(self) -> int:
        return 1 << 29

    @flag
    def manage_emojis_and_stickers(self) -> int:
        return 1 << 30

    @flag
    def use_application_commands(self) -> int:
        return 1 << 31

    @flag
    def request_to_speak(self) -> int:
        return 1 << 32

    @flag
    def manage_events(self) -> int:
        return 1 << 33

    @flag
    def manage_threads(self) -> int:
        return 1 << 34

    @flag
    def create_public_threads(self) -> int:
        return 1 << 35

    @flag
    def create_private_threads(self) -> int:
        return 1 << 36

    @flag
    def use_external_stickers(self) -> int:
        return 1 << 37

    @flag
    def send_messages_in_threads(self) -> int:
        return 1 << 38

    @flag
    def use_embedded_activities(self) -> int:
        return 1 << 39

    @flag
    def moderate_members(self) -> int:
        return 1 << 40
