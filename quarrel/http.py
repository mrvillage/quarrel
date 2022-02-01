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

import asyncio
import datetime
import sys
from typing import TYPE_CHECKING

import aiohttp

from . import __version__
from .errors import (
    BadRequest,
    Forbidden,
    HTTPException,
    MethodNotAllowed,
    NotFound,
    ServerError,
    Unauthorized,
)
from .missing import MISSING

__all__ = ("HTTP",)

if TYPE_CHECKING:
    from typing import (
        Any,
        ClassVar,
        Coroutine,
        Dict,
        Mapping,
        Optional,
        Sequence,
        Type,
        TypeVar,
        Union,
    )

    from .file import File
    from .missing import Missing
    from .types.interactions import ApplicationCommand, PartialApplicationCommand

    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]


class Bucket:
    __slots__ = (
        "http",
        "key",
        "release_immediately",
        "lock",
        "limit",
        "remaining",
        "reset",
        "reset_after",
        "bucket",
    )

    def __init__(self, http: HTTP, key: str, /) -> None:
        self.http: HTTP = http
        self.key: str = key
        self.release_immediately: bool = True
        self.lock: asyncio.Lock = asyncio.Lock()
        self.limit: Optional[int] = None
        self.remaining: Optional[int] = None
        self.reset: Optional[float] = None
        self.reset_after: Optional[float] = None
        self.bucket: Optional[str] = None

    async def __aenter__(self) -> Bucket:
        await self.lock.acquire()
        if self.http.global_ratelimit.is_set():
            await self.http.global_ratelimit.wait()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        if self.release_immediately:
            self.release()

    def delay_amount(self) -> float:
        utc = datetime.timezone.utc
        now = datetime.datetime.now(utc)
        if self.reset_after is None and self.reset is None:
            return 0
        return (
            self.reset_after
            or (
                datetime.datetime.fromtimestamp(
                    # self.reset will never be None here
                    float(self.reset),  # type: ignore
                    utc,
                )
                - now
            ).total_seconds()
        )

    def delay_release(self) -> None:
        self.release_immediately = False
        self.http.loop.call_later(self.delay_amount(), self.release)

    def release(self) -> None:
        self.lock.release()
        if not self.lock._waiters and not self.lock.locked():  # type: ignore
            if self.delay_amount() > 0:
                self.http.loop.call_later(self.delay_amount(), self.expire)
            else:
                self.expire()

    def expire(self) -> None:
        if not self.lock._waiters and not self.lock.locked():  # type: ignore
            del self.http.buckets[self.key]

    @staticmethod
    def bucket_key(
        path: str,
        channel_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        webhook_id: Optional[int] = None,
        webhook_token: Optional[str] = None,
    ) -> str:
        return f"{path}/{channel_id}/{guild_id}/{webhook_id}/{webhook_token}"

    @classmethod
    def from_major_parameters(
        cls,
        http: HTTP,
        path: str,
        /,
        channel_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        webhook_id: Optional[int] = None,
        webhook_token: Optional[str] = None,
    ) -> Bucket:
        key = cls.bucket_key(
            path,
            channel_id=channel_id,
            guild_id=guild_id,
            webhook_id=webhook_id,
            webhook_token=webhook_token,
        )
        bucket = http.buckets.get(key)
        if bucket is None:
            bucket = cls(http, key)
            http.buckets[key] = bucket
        return bucket

    async def handle_ratelimit(
        self, response: aiohttp.ClientResponse, data: Union[str, Dict[str, Any]], /
    ) -> None:
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None:
            self.remaining = int(remaining)
        limit = response.headers.get("X-RateLimit-Limit")
        if limit is not None:
            self.limit = int(limit)
        reset = response.headers.get("X-RateLimit-Reset")
        if reset is not None:
            self.reset = float(reset)
        reset_after = response.headers.get("X-RateLimit-Reset-After")
        if reset_after is not None:
            self.reset_after = float(reset_after)
        bucket = response.headers.get("X-RateLimit-Bucket")
        if bucket is not None:
            self.bucket = bucket
        if self.remaining == 0:
            self.delay_release()
        if response.status == 429:
            if isinstance(data, str):
                raise HTTPException(response, data)
            global_ = response.headers.get(
                "X-RateLimit-Global"
            ) is not None and data.get("global")
            if global_:
                self.http.global_ratelimit.set()
            await asyncio.sleep(data["retry_after"])
            if global_:
                self.http.global_ratelimit.clear()


class HTTP:
    BASE_URL: ClassVar[str] = "https://discord.com/api/v9"
    USER_AGENT: ClassVar[str] = f"DiscordBot (https://github.com/mrvillage/quarrel {__version__}) Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}"  # type: ignore

    def __init__(
        self,
        session: aiohttp.ClientSession,
        token: str,
        application_id: int,
        loop: asyncio.AbstractEventLoop,
        /,
    ) -> None:
        self.session: aiohttp.ClientSession = session
        self.token: str = token
        self.application_id: int = application_id
        self.loop: asyncio.AbstractEventLoop = loop

        self.buckets: Dict[str, Bucket] = {}
        self.global_ratelimit: asyncio.Event = asyncio.Event()
        self.headers = {
            "User-Agent": self.USER_AGENT,
            "Authorization": f"Bot {self.token}",
        }

    async def request(
        self,
        method: str,
        path: str,
        route_parameters: Missing[Mapping[str, Any]] = MISSING,
        files: Missing[Sequence[File]] = MISSING,
        **kwargs: Any,
    ) -> Any:
        route_parameters = route_parameters or {}
        if files is not MISSING:
            form_data = aiohttp.FormData()
            form_data.add_field(name="payload_json", value=kwargs.pop("json"))
            for index, file in enumerate(files):
                form_data.add_field(
                    name=f"file{index}",
                    value=file.buffer,
                    filename=file.name,
                    content_type="application/octet-stream",
                )
            kwargs["form"] = form_data
        url = f"{self.BASE_URL}{path.format_map(route_parameters)}"
        async with Bucket.from_major_parameters(
            self,
            path,
            channel_id=route_parameters.get("channel_id"),
            guild_id=route_parameters.get("guild_id"),
            webhook_id=route_parameters.get("webhook_id"),
            webhook_token=route_parameters.get("webhook_token"),
        ) as bucket:
            response = None
            data = None
            for try_ in range(3):
                async with self.session.request(
                    method, url, headers=self.headers, **kwargs
                ) as response:
                    if response.headers["content-type"] == "application/json":
                        data = await response.json()
                    else:
                        data = await response.text()
                    await bucket.handle_ratelimit(response, data)
                    if 300 > response.status >= 200:
                        return data
                    if response.status == 400:
                        raise BadRequest(response, data)
                    if response.status == 401:
                        raise Unauthorized(response, data)
                    if response.status == 403:
                        raise Forbidden(response, data)
                    if response.status == 404:
                        raise NotFound(response, data)
                    if response.status == 405:
                        raise MethodNotAllowed(response, data)
                    if response.status in {500, 502, 504}:
                        await asyncio.sleep(1 + try_)
                        continue
                    if response.status >= 500:
                        raise ServerError(response, data)
                    raise HTTPException(response, data)
            if response is not None:
                if response.status >= 500:
                    raise ServerError(response, data)
                raise HTTPException(response, data)

    async def get_gateway_bot(
        self, encoding: str = "json", compress: bool = True, v: int = 9
    ) -> str:
        data = await self.request("GET", "/gateway/bot")
        if compress:
            return f"{data['url']}?encoding={encoding}&v={v}&compress=zlib-stream"
        else:
            return f"{data['url']}?encoding={encoding}&v={v}"

    def bulk_upsert_global_application_commands(
        self, commands: Sequence[PartialApplicationCommand]
    ) -> Response[Sequence[ApplicationCommand]]:
        return self.request(
            "PUT",
            "/applications/{application_id}/commands",
            {"application_id": self.application_id},
            json=commands,
        )

    def bulk_upsert_guild_application_commands(
        self, guild_id: int, commands: Sequence[PartialApplicationCommand]
    ) -> Response[Sequence[ApplicationCommand]]:
        return self.request(
            "PUT",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            {"application_id": self.application_id, "guild_id": guild_id},
            json=commands,
        )
