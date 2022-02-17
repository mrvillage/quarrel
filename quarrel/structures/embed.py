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

from ..missing import MISSING

__all__ = ("Embed",)

if TYPE_CHECKING:
    import datetime
    from typing import List

    from ..missing import Missing


class Embed:
    __slots__ = (
        "title",
        "type",
        "description",
        "url",
        "timestamp",
        "color",
        "footer",
        "image",
        "thumbnail",
        "video",
        "provider",
        "author",
        "fields",
    )

    def __init__(
        self,
        *,
        title: Missing[str] = MISSING,
        type: Missing[str] = MISSING,
        description: Missing[str] = MISSING,
        url: Missing[str] = MISSING,
        timestamp: Missing[datetime.datetime] = MISSING,
        color: Missing[int],
    ) -> None:
        self.title: Missing[str] = title
        self.type: str = type or "rich"
        self.description: Missing[str] = description
        self.url: Missing[str] = url
        self.timestamp: Missing[datetime.datetime] = timestamp
        self.color: Missing[int] = color
        self.footer: EmbedFooter = EmbedFooter()
        self.image: EmbedImage = EmbedImage()
        self.thumbnail: EmbedThumbnail = EmbedThumbnail()
        self.video: EmbedVideo = EmbedVideo()
        self.provider: EmbedProvider = EmbedProvider()
        self.author: EmbedAuthor = EmbedAuthor()
        self.fields: List[EmbedField] = []

    def add_field(
        self, name: str, value: str, inline: Missing[bool] = MISSING
    ) -> Embed:
        self.fields.append(EmbedField(name=name, value=value, inline=inline))
        return self


class EmbedFooter:
    __slots__ = ("text", "icon_url", "proxy_icon_url")

    def __init__(
        self,
        *,
        text: Missing[str] = MISSING,
        icon_url: Missing[str] = MISSING,
        proxy_icon_url: Missing[str] = MISSING,
    ) -> None:
        self.text: Missing[str] = text
        self.icon_url: Missing[str] = icon_url
        self.proxy_icon_url: Missing[str] = proxy_icon_url

    def __bool__(self) -> bool:
        return self.text is not MISSING


class EmbedImage:
    __slots__ = ("url", "proxy_url", "height", "width")

    def __init__(
        self,
        *,
        url: Missing[str] = MISSING,
        proxy_url: Missing[str] = MISSING,
        height: Missing[int] = MISSING,
        width: Missing[int] = MISSING,
    ) -> None:
        self.url: Missing[str] = url
        self.proxy_url: Missing[str] = proxy_url
        self.height: Missing[int] = height
        self.width: Missing[int] = width

    def __bool__(self) -> bool:
        return self.url is not MISSING


class EmbedThumbnail:
    __slots__ = ("url", "proxy_url", "height", "width")

    def __init__(
        self,
        *,
        url: Missing[str] = MISSING,
        proxy_url: Missing[str] = MISSING,
        height: Missing[int] = MISSING,
        width: Missing[int] = MISSING,
    ) -> None:
        self.url: Missing[str] = url
        self.proxy_url: Missing[str] = proxy_url
        self.height: Missing[int] = height
        self.width: Missing[int] = width

    def __bool__(self) -> bool:
        return self.url is not MISSING


class EmbedVideo:
    __slots__ = ("url", "proxy_url", "height", "width")

    def __init__(
        self,
        *,
        url: Missing[str] = MISSING,
        proxy_url: Missing[str] = MISSING,
        height: Missing[int] = MISSING,
        width: Missing[int] = MISSING,
    ) -> None:
        self.url: Missing[str] = url
        self.proxy_url: Missing[str] = proxy_url
        self.height: Missing[int] = height
        self.width: Missing[int] = width

    def __bool__(self) -> bool:
        return (
            self.url is not MISSING
            or self.proxy_url is not MISSING
            or self.height is not MISSING
            or self.width is not MISSING
        )


class EmbedProvider:
    __slots__ = ("name", "url")

    def __init__(
        self, *, name: Missing[str] = MISSING, url: Missing[str] = MISSING
    ) -> None:
        self.name: Missing[str] = name
        self.url: Missing[str] = url

    def __bool__(self) -> bool:
        return self.name is not MISSING or self.url is not MISSING


class EmbedAuthor:
    __slots__ = ("name", "url", "icon_url", "proxy_icon_url")

    def __init__(
        self,
        *,
        name: Missing[str] = MISSING,
        url: Missing[str] = MISSING,
        icon_url: Missing[str] = MISSING,
        proxy_icon_url: Missing[str] = MISSING,
    ) -> None:
        self.name: Missing[str] = name
        self.url: Missing[str] = MISSING
        self.icon_url: Missing[str] = icon_url
        self.proxy_icon_url: Missing[str] = proxy_icon_url

    def __bool__(self) -> bool:
        return self.name is not MISSING


class EmbedField:
    __slots__ = ("name", "value", "inline")

    def __init__(
        self,
        *,
        name: Missing[str] = MISSING,
        value: Missing[str] = MISSING,
        inline: Missing[bool] = MISSING,
    ) -> None:
        self.name: Missing[str] = name
        self.value: Missing[str] = value
        self.inline: Missing[bool] = inline

    def __bool__(self) -> bool:
        return self.name is not MISSING and self.value is not MISSING
