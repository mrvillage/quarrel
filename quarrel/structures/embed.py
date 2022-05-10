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

from ..enums import Color
from ..missing import MISSING

__all__ = (
    "Embed",
    "EmbedFooter",
    "EmbedImage",
    "EmbedThumbnail",
    "EmbedVideo",
    "EmbedProvider",
    "EmbedAuthor",
    "EmbedField",
)

if TYPE_CHECKING:
    import datetime
    from typing import Any, List, Union

    from ..missing import Missing
    from ..types.embed import Embed as EmbedData
    from ..types.embed import EmbedAuthor as EmbedAuthorData
    from ..types.embed import EmbedField as EmbedFieldData
    from ..types.embed import EmbedFooter as EmbedFooterData
    from ..types.embed import EmbedImage as EmbedImageData
    from ..types.embed import EmbedProvider as EmbedProviderData
    from ..types.embed import EmbedThumbnail as EmbedThumbnailData
    from ..types.embed import EmbedVideo as EmbedVideoData


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
        color: Missing[Union[int, Color]] = MISSING,
    ) -> None:
        self.title: Missing[str] = title
        self.type: str = type or "rich"
        self.description: Missing[str] = description
        self.url: Missing[str] = url
        self.timestamp: Missing[datetime.datetime] = timestamp
        self.color: Missing[Union[int, Color]] = color
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

    def to_payload(self) -> EmbedData:
        payload: EmbedData = {"type": self.type}
        if self.title is not MISSING:
            payload["title"] = self.title
        if self.description is not MISSING:
            payload["description"] = self.description
        if self.url is not MISSING:
            payload["url"] = self.url
        if self.timestamp is not MISSING:
            payload["timestamp"] = str(self.timestamp)
        if self.color is not MISSING:
            if isinstance(self.color, Color):
                payload["color"] = self.color.value
            else:
                payload["color"] = self.color
        if self.footer:
            payload["footer"] = self.footer.to_payload()
        if self.image:
            payload["image"] = self.image.to_payload()
        if self.thumbnail:
            payload["thumbnail"] = self.thumbnail.to_payload()
        if self.video:
            payload["video"] = self.video.to_payload()
        if self.provider:
            payload["provider"] = self.provider.to_payload()
        if self.author:
            payload["author"] = self.author.to_payload()
        if self.fields:
            payload["fields"] = [i.to_payload() for i in self.fields]
        return payload


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

    def to_payload(self) -> EmbedFooterData:
        payload: EmbedFooterData = {}
        if self.text is not MISSING:
            payload["text"] = self.text
        if self.icon_url is not MISSING:
            payload["icon_url"] = self.icon_url
        if self.proxy_icon_url is not MISSING:
            payload["proxy_icon_url"] = self.proxy_icon_url
        return payload


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

    def to_payload(self) -> EmbedImageData:
        payload: EmbedImageData = {}
        if self.url is not MISSING:
            payload["url"] = self.url
        if self.proxy_url is not MISSING:
            payload["proxy_url"] = self.proxy_url
        if self.height is not MISSING:
            payload["height"] = self.height
        if self.width is not MISSING:
            payload["width"] = self.width
        return payload


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

    def to_payload(self) -> EmbedThumbnailData:
        payload: EmbedThumbnailData = {}
        if self.url is not MISSING:
            payload["url"] = self.url
        if self.proxy_url is not MISSING:
            payload["proxy_url"] = self.proxy_url
        if self.height is not MISSING:
            payload["height"] = self.height
        if self.width is not MISSING:
            payload["width"] = self.width
        return payload


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

    def to_payload(self) -> EmbedVideoData:
        payload: EmbedVideoData = {}
        if self.url is not MISSING:
            payload["url"] = self.url
        if self.proxy_url is not MISSING:
            payload["proxy_url"] = self.proxy_url
        if self.height is not MISSING:
            payload["height"] = self.height
        if self.width is not MISSING:
            payload["width"] = self.width
        return payload


class EmbedProvider:
    __slots__ = ("name", "url")

    def __init__(
        self, *, name: Missing[str] = MISSING, url: Missing[str] = MISSING
    ) -> None:
        self.name: Missing[str] = name
        self.url: Missing[str] = url

    def __bool__(self) -> bool:
        return self.name is not MISSING or self.url is not MISSING

    def to_payload(self) -> EmbedProviderData:
        payload: EmbedProviderData = {}
        if self.name is not MISSING:
            payload["name"] = self.name
        if self.url is not MISSING:
            payload["url"] = self.url
        return payload


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
        self.url: Missing[str] = url
        self.icon_url: Missing[str] = icon_url
        self.proxy_icon_url: Missing[str] = proxy_icon_url

    def __bool__(self) -> bool:
        return self.name is not MISSING

    def to_payload(self) -> EmbedAuthorData:
        payload: EmbedAuthorData = {}
        if self.name is not MISSING:
            payload["name"] = self.name
        if self.url is not MISSING:
            payload["url"] = self.url
        if self.icon_url is not MISSING:
            payload["icon_url"] = self.icon_url
        if self.proxy_icon_url is not MISSING:
            payload["proxy_icon_url"] = self.proxy_icon_url
        return payload


class EmbedField:
    __slots__ = ("name", "value", "inline")

    def __init__(
        self,
        *,
        name: Missing[Any] = MISSING,
        value: Missing[Any] = MISSING,
        inline: Missing[bool] = MISSING,
    ) -> None:
        self.name: Missing[str] = str(name) if name is not MISSING else MISSING
        self.value: Missing[str] = str(value) if value is not MISSING else MISSING
        self.inline: Missing[bool] = inline

    def __bool__(self) -> bool:
        return self.name is not MISSING and self.value is not MISSING

    def to_payload(self) -> EmbedFieldData:
        payload: EmbedFieldData = {}
        if self.name is not MISSING:
            payload["name"] = self.name
        if self.value is not MISSING:
            payload["value"] = self.value
        if self.inline is not MISSING:
            payload["inline"] = self.inline
        return payload
