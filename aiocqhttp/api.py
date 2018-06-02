import json
import abc
import functools
import sys
from typing import Set, Callable, Dict, Any, Optional

import aiohttp
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


class WebSocketReverseApi(Api):
    def __init__(self, connected_clients: Set[Websocket], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected_clients = connected_clients
        self._seq = 1

    async def call_action(self, action: str, **params) -> \
            Optional[Dict[str, Any]]:
        for ws in self._connected_clients:
            await ws.send(json.dumps({
                'action': action,
                'params': params,
                'echo': {
                    'seq': self._seq
                }
            }))
        self._seq = (self._seq + 1) % sys.maxsize

    def _is_available(self) -> bool:
        return bool(self._connected_clients)


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
