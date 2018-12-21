import abc
import asyncio
import functools
import json
import sys
from typing import Callable, Dict, Any, Optional

import aiohttp
from quart import websocket as event_ws
from quart.wrappers.request import Websocket

from .exceptions import *


class Api:
    """API interface."""

    def __getattr__(self, item: str) -> Callable:
        """Get a callable that sends the actual API request internally."""
        return functools.partial(self.call_action, item)

    @abc.abstractmethod
    async def call_action(self, action: str, **params) -> \
            Optional[Dict[str, Any]]:
        """Send API request to call the specified action."""
        pass


def _handle_api_result(result: Optional[Dict[str, Any]]) -> Any:
    """
    Retrieve 'data' field from the API result object.

    :param result: API result that received from HTTP API
    :return: the 'data' field in result object
    :raise ActionFailed: the 'status' field is 'failed'
    """
    if isinstance(result, dict):
        if result.get('status') == 'failed':
            raise ActionFailed(retcode=result.get('retcode'))
        return result.get('data')


class HttpApi(Api):
    """Call APIs through HTTP."""

    def __init__(self, api_root: Optional[str], access_token: Optional[str],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_root = api_root.rstrip('/') if api_root else None
        self._access_token = access_token

    async def call_action(self, action: str, **params) -> Any:
        if not self._is_available():
            raise ApiNotAvailable

        headers = {}
        if self._access_token:
            headers['Authorization'] = 'Token ' + self._access_token

        try:
            async with aiohttp.request('POST', self._api_root + '/' + action,
                                       json=params, headers=headers) as resp:
                if 200 <= resp.status < 300:
                    return _handle_api_result(json.loads(await resp.text()))
                raise HttpFailed(resp.status)
        except aiohttp.InvalidURL:
            raise NetworkError('API root url invalid')
        except aiohttp.ClientError:
            raise NetworkError('HTTP request failed with client error')

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
        try:
            return await asyncio.wait_for(future, 60)  # wait for only 60 secs
        except asyncio.TimeoutError:
            # haven't received any result until timeout,
            # we consider this API call failed with a network error.
            raise NetworkError('WebSocket API call timeout')
        finally:
            # don't forget to remove the future object
            del cls._futures[seq]


class WebSocketReverseApi(Api):
    """Call APIs through reverse WebSocket."""

    def __init__(self, connected_clients: Dict[str, Websocket],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected_clients = connected_clients

    async def call_action(self, action: str, **params) -> Any:
        api_ws = None
        if self._is_available():
            api_ws = self._connected_clients.get(
                event_ws.headers.get('X-Self-ID', '*'))
        elif params.get('self_id'):
            api_ws = self._connected_clients.get(str(params['self_id']))
        elif len(self._connected_clients) == 1:
            api_ws = list(self._connected_clients.values())[0]

        if not api_ws:
            raise ApiNotAvailable

        seq = _SequenceGenerator.next()
        await api_ws.send(json.dumps({
            'action': action,
            'params': params,
            'echo': {
                'seq': seq
            }
        }))
        return _handle_api_result(await ResultStore.fetch(seq))

    def _is_available(self) -> bool:
        # available only when current event ws has a corresponding api ws
        return event_ws and event_ws.headers.get(
            'X-Self-ID', '*') in self._connected_clients


class UnifiedApi(Api):
    """
    Call APIs through different communication methods
    depending on availability.
    """

    def __init__(self, *args,
                 http_api: Api = None,
                 ws_reverse_api: Api = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._http_api = http_api
        self._ws_reverse_api = ws_reverse_api

    async def call_action(self, action: str, **params) -> Any:
        result = None
        succeeded = False

        if self._ws_reverse_api:
            # WebSocket is preferred
            try:
                result = await self._ws_reverse_api.call_action(
                    action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded and self._http_api:
            try:
                result = await self._http_api.call_action(
                    action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded:
            raise ApiNotAvailable
        return result
