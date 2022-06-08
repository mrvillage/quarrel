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

from ..enums import PermissionOverwriteType
from ..flags import Permissions
from ..missing import MISSING

__all__ = ("PermissionOverwrite",)

if TYPE_CHECKING:
    from .. import Missing
    from ..models import Member, Role
    from ..types.channel import PermissionOverwrite as PermissionOverwriteData


class PermissionOverwrite:
    __slots__ = ("id", "type", "allow", "deny")

    def __init__(self, data: PermissionOverwriteData) -> None:
        self.id: int = int(data["id"])
        self.type: PermissionOverwriteType = PermissionOverwriteType(data["type"])
        self.allow: Permissions = Permissions(int(data["allow"]))
        self.deny: Permissions = Permissions(int(data["deny"]))

    @classmethod
    def from_role(
        cls,
        role: Role,
        *,
        allow: Missing[Permissions] = MISSING,
        deny: Missing[Permissions] = MISSING,
    ) -> PermissionOverwrite:
        return PermissionOverwrite(
            # incompatible types
            {  # type: ignore
                "id": role.id,
                "type": PermissionOverwriteType.ROLE.value,
                "allow": allow.value,
                "deny": deny.value,
            }
        )

    @classmethod
    def from_member(
        cls,
        member: Member,
        *,
        allow: Missing[Permissions] = MISSING,
        deny: Missing[Permissions] = MISSING,
    ) -> PermissionOverwrite:
        return PermissionOverwrite(
            # incompatible types
            {  # type: ignore
                "id": member.id,
                "type": PermissionOverwriteType.MEMBER.value,
                "allow": allow.value,
                "deny": deny.value,
            }
        )

    def to_payload(self) -> PermissionOverwriteData:
        return {
            "id": self.id,
            "type": self.type.value,
            "allow": str(self.allow.value),
            "deny": str(self.deny.value),
        }
