import json
import abc
import functools
import sys
import asyncio
from typing import Callable, Dict, Any, Optional

import aiohttp
from quart import websocket as event_ws
from quart.wrappers.request import Websocket


class Error(Exception):
    def __init__(self, status_code: int, retcode: int = None):
        self.status_code = status_code
        self.retcode = retcode


class Api:
    def __getattr__(self, item: str) -> Callable:
        return functools.partial(self.call_action, item)

    @abc.abstractmethod
    async def call_action(self, action: str, **params) -> \
            Optional[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def _is_available(self) -> bool:
        pass

    @property
    def is_available(self) -> bool:
        return self._is_available()


class HttpApi(Api):
    def __init__(self, api_root: Optional[str], access_token: Optional[str],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_root = api_root.rstrip('/') if api_root else None
        self._access_token = access_token

    async def call_action(self, action: str, **params) -> \
            Optional[Dict[str, Any]]:
        if not self._is_available():
            return

        headers = {}
        if self._access_token:
            headers['Authorization'] = 'Token ' + self._access_token

        async with aiohttp.request('POST', self._api_root + '/' + action,
                                   json=params, headers=headers) as resp:
            if 200 <= resp.status < 300:
                data = json.loads(await resp.text())
                if data.get('status') == 'failed':
                    raise Error(resp.status, data.get('retcode'))
                return data.get('data')
            raise Error(resp.status)

    def _is_available(self) -> bool:
        return bool(self._api_root)


class _SequenceGenerator:
    _seq = 1

    @classmethod
    def next(cls) -> int:
        s = cls._seq
        cls._seq = (cls._seq + 1) % sys.maxsize
        return s


class ResultStore:
    _futures = {}  # key: seq, value: asyncio.Future

    @classmethod
    def add(cls, result: Dict[str, Any]):
        if isinstance(result.get('echo'), dict) and \
                isinstance(result['echo'].get('seq'), int):
            future = cls._futures.get(result['echo']['seq'])
            if future:
                future.set_result(result)

    @classmethod
    async def fetch(cls, seq: int) -> Dict[str, Any]:
        future = asyncio.get_event_loop().create_future()
        cls._futures[seq] = future
        result = await future
        del cls._futures[seq]
        return result


class WebSocketReverseApi(Api):
    def __init__(self, connected_clients: Dict[str, Websocket],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected_clients = connected_clients

    async def call_action(self, action: str, **params) -> \
            Optional[Dict[str, Any]]:
        if not self._is_available():
            return

        api_ws = self._connected_clients.get(
            event_ws.headers.get('X-Self-ID', '*'))
        if api_ws:
            seq = _SequenceGenerator.next()
            await api_ws.send(json.dumps({
                'action': action,
                'params': params,
                'echo': {
                    'seq': seq
                }
            }))
            return await ResultStore.fetch(seq)

    def _is_available(self) -> bool:
        # available only when current event ws has a corresponding api ws
        return event_ws and event_ws.headers.get(
            'X-Self-ID', '*') in self._connected_clients


class UnifiedApi(Api):
    def __init__(self, *args,
                 http_api: Api = None,
                 ws_reverse_api: Api = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._http_api = http_api
        self._ws_reverse_api = ws_reverse_api

    async def call_action(self, action: str, **params) -> \
            Optional[Dict[str, Any]]:
        if self._ws_reverse_api and self._ws_reverse_api.is_available:
            # WebSocket is preferred
            return await self._ws_reverse_api.call_action(action, **params)
        elif self._http_api and self._http_api.is_available:
            return await self._http_api.call_action(action, **params)

    def _is_available(self) -> bool:
        return self._ws_reverse_api and self._ws_reverse_api.is_available or \
               self._http_api and self._http_api.is_available
