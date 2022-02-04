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
import json
import random
import sys
import time
import zlib
from typing import TYPE_CHECKING

import aiohttp

from .errors import InvalidSessionError
from .missing import MISSING

__all__ = ("GatewayHandler",)

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union
    from zlib import _Decompress  # type: ignore

    from .bot import Bot
    from .missing import Missing
    from .models import Guild
    from .types.gateway import (
        GatewayDispatch,
        IdentifyPayloadData,
        RequestGuildMembersPayloadData,
        ResumePayloadData,
    )
    from .types.snowflake import Snowflake


class GatewayClosure(Exception):
    def __init__(self, close_code: Optional[int]) -> None:
        self.close_code: Optional[int] = close_code


class UnknownGatewayMessageType(Exception):
    ...


class Heartbeat:
    def __init__(self, handler: GatewayHandler, interval: float):
        self.handler: GatewayHandler = handler
        self.socket: aiohttp.ClientWebSocketResponse = handler.gateway.socket
        self.interval: float = interval
        self.stop_event: asyncio.Event = asyncio.Event()
        self.last_send: float = time.perf_counter()

    async def send(self) -> None:
        if not self.handler.acked:
            self.stop()
            await self.handler.close_and_resume()
        await self.handler.gateway.socket.send_json(
            {"op": 1, "d": self.handler.sequence}
        )

    async def task(self) -> None:
        while True:
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                await self.send()
                self.last_send = time.perf_counter()
            else:
                break

    def start(self) -> None:
        self.handler.loop.create_task(self.task())

    def stop(self) -> None:
        self.stop_event.set()


class GatewayRatelimiter:
    def __init__(self):
        self.start: float = 0
        self.sent: int = 0
        self.amount: int = 120
        self.lock: asyncio.Lock = asyncio.Lock()

    async def __aenter__(self) -> GatewayRatelimiter:
        await self.lock.acquire()
        now = time.perf_counter()
        if self.start + 60 < now:
            self.start = now
            self.sent = 0
        if self.sent > self.amount:
            await asyncio.sleep(self.start + 60 - now)
        self.sent += 1
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.lock.release()


class Gateway:
    def __init__(self, socket: aiohttp.ClientWebSocketResponse):
        self.socket: aiohttp.ClientWebSocketResponse = socket
        self.ratelimiter: GatewayRatelimiter = GatewayRatelimiter()
        self._buffer: bytearray = bytearray()
        self._decompress: _Decompress = zlib.decompressobj()

    def __aiter__(self) -> Gateway:
        return self

    async def __anext__(self) -> GatewayDispatch:
        return await self.receive()

    @classmethod
    async def connect(
        cls, session: aiohttp.ClientSession, url: str, user_agent: str, /
    ) -> Gateway:
        return cls(
            await session.ws_connect(
                f"{url}?v=9&encoding=json&compress=zlib-stream",
                max_msg_size=0,
                autoclose=False,
                timeout=30,
                headers={"User-Agent": user_agent},
            )
        )

    async def receive(self) -> GatewayDispatch:
        try:
            message = await self.socket.receive()
            if message.type in {  # type: ignore
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
                aiohttp.WSMsgType.CLOSE,
            }:
                raise GatewayClosure(self.socket.close_code)
            elif message.type in {aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY}:  # type: ignore
                return self.parse_gateway_message(message.data)  # type: ignore
            raise UnknownGatewayMessageType(message)
        except (asyncio.TimeoutError, GatewayClosure):
            raise

    async def send(self, op: int, data: Any) -> None:
        async with self.ratelimiter:
            try:
                await self.socket.send_json({"op": op, "d": data})
            except Exception:
                if self.socket.closed:
                    raise GatewayClosure(self.socket.close_code)

    def parse_gateway_message(
        self, data: Union[bytes, str]
    ) -> Optional[GatewayDispatch]:
        if type(data) is bytes:
            self._buffer.extend(data)
            if len(data) < 4 or data[-4:] != b"\x00\x00\xff\xff":
                return
            data = self._decompress.decompress(self._buffer)
            data = data.decode("utf-8")
            self._buffer = bytearray()
        return json.loads(data)

    async def close(self, code: int, message: Missing[str] = MISSING) -> None:
        await self.socket.close(code=code, message=(message or "").encode())


class GatewayHandler:
    def __init__(
        self,
        bot: Bot,
        gateway_url: str,
        gateway: Gateway,
        loop: asyncio.AbstractEventLoop,
        /,
        *,
        shard_id: Optional[int] = None,
        shard_count: Optional[int] = None,
        sequence: Optional[int] = None,
    ):
        self.bot: Bot = bot
        self.gateway_url: str = gateway_url
        self.gateway: Gateway = gateway
        self.loop: asyncio.AbstractEventLoop = loop
        self.shard_id: Optional[int] = shard_id
        self.shard_count: Optional[int] = shard_count
        self.sequence: Optional[int] = sequence
        self.heartbeat: Optional[Heartbeat] = None
        self.session_id: Optional[str] = None
        self.acked: bool = True

    async def __aenter__(self) -> GatewayHandler:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.gateway.socket.close()

    def __aiter__(self) -> GatewayHandler:
        return self

    async def __anext__(self) -> GatewayDispatch:
        while True:
            message = await self.receive()
            result = await self.handle_message(message)
            if result is not None:
                return result

    @classmethod
    async def connect(cls, bot: Bot) -> GatewayHandler:
        gateway_url = await bot.http.get_gateway_bot()
        gateway = await Gateway.connect(bot.session, gateway_url, bot.http.USER_AGENT)
        gateway_handler = cls(bot, gateway_url, gateway, bot.loop)
        await gateway_handler.handle_message(await gateway_handler.receive())
        await gateway_handler.identify()
        return gateway_handler

    async def reconnect(self) -> None:
        self.gateway = await Gateway.connect(
            self.bot.session, self.gateway_url, self.bot.http.USER_AGENT
        )
        await self.handle_message(await self.receive())
        await self.identify()

    async def handle_message(
        self, message: GatewayDispatch
    ) -> Optional[GatewayDispatch]:
        op = message["op"]
        data = message["d"]
        sequence = message.get("s")

        if sequence is not None:
            self.sequence = sequence

        # keep alive

        # Dispatch
        if op == 0:
            return message

        # Heartbeat
        if op == 1:
            return await self.handle_heartbeat(data)

        # Reconnect
        if op == 7:
            return await self.handle_reconnect(data)

        # Invalid Session
        if op == 9:
            return await self.handle_invalid_session(data)  # type: ignore

        # Hello
        if op == 10:
            return await self.handle_hello(data)

        # Heartbeat ACK
        if op == 11:
            return await self.handle_heartbeat_ack(data)

    async def handle_heartbeat(self, data: Dict[str, Any]) -> None:
        if self.heartbeat is None:
            return
        await self.heartbeat.send()

    async def handle_reconnect(self, data: Dict[str, Any]) -> None:
        await self.close_and_resume()

    async def handle_invalid_session(self, data: bool) -> None:
        if data:
            await self.close_and_resume()
        else:
            raise InvalidSessionError

    async def handle_hello(self, data: Dict[str, Any]) -> None:
        self.heartbeat_interval: float = data["heartbeat_interval"] / 1000
        self.heartbeat = Heartbeat(self, self.heartbeat_interval)
        await asyncio.sleep(self.heartbeat_interval * random.random())
        await self.heartbeat.send()
        self.heartbeat.start()

    async def handle_heartbeat_ack(self, data: Dict[str, Any]) -> None:
        self.acked = True

    async def resume(self) -> None:
        if TYPE_CHECKING:
            assert self.session_id is not None and self.sequence is not None
        data: ResumePayloadData = {
            "seq": self.sequence,
            "session_id": self.session_id,
            "token": self.bot.token,
        }
        await self.send(6, data)

    async def identify(self) -> None:
        data: IdentifyPayloadData = {
            "token": self.bot.token,
            "properties": {
                "$os": sys.platform,
                "$browser": "quarrel",
                "$device": "quarrel",
            },
            "compress": True,
            "large_threshold": 250,
            "intents": self.bot.intents.value,
        }
        if self.shard_id is not None and self.shard_count is not None:
            data["shard"] = [self.shard_id, self.shard_count]
        await self.send(2, data)

    async def send(self, op: int, data: Any) -> None:
        await self.gateway.send(op, data)

    async def receive(self) -> GatewayDispatch:
        return await self.gateway.receive()

    async def request_guild_members(
        self,
        guild: Guild,
        /,
        limit: int = 0,
        presences: bool = False,
        nonce: Optional[str] = None,
        user_ids: Union[Snowflake, Optional[List[Snowflake]]] = None,
        query: Optional[str] = None,
    ) -> None:
        data: RequestGuildMembersPayloadData = {
            "guild_id": guild.id,
            "limit": limit,
        }
        if presences:
            data["presences"] = presences
        if nonce:
            data["nonce"] = nonce
        if user_ids:
            data["user_ids"] = user_ids
        if query is not None:
            data["query"] = query
        if query is None and not user_ids:
            data["query"] = ""

        await self.send(8, data)

    async def close_and_resume(self) -> None:
        await self.gateway.close(1002)
        self.gateway = await Gateway.connect(
            self.bot.session, self.gateway_url, self.bot.http.USER_AGENT
        )
        await self.resume()
