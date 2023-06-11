"""
此模块提供了 OneBot (CQHTTP) API 相关的实现类。
"""

import asyncio
import sys
from typing import Callable, Dict, Any, Optional, Set, Union, Awaitable

from .api import Api, AsyncApi, SyncApi

try:
    import ujson as json
except ImportError:
    import json

import httpx
from quart import websocket as event_ws
from quart.wrappers.websocket import Websocket

from .exceptions import ActionFailed, ApiNotAvailable, HttpFailed, NetworkError
from .utils import sync_wait

__pdoc__ = {
    'ResultStore': False,
}


def _handle_api_result(result: Optional[Dict[str, Any]]) -> Any:
    """
    Retrieve 'data' field from the API result object.

    :param result: API result that received from OneBot
    :return: the 'data' field in result object
    :raise ActionFailed: the 'status' field is 'failed'
    """
    if isinstance(result, dict):
        if result['status'] == 'failed':
            raise ActionFailed(result=result)
        return result.get('data')


class HttpApi(AsyncApi):
    """
    HTTP API 实现类。

    实现通过 HTTP 调用 OneBot API。
    """

    def __init__(self, api_root: Optional[str], access_token: Optional[str],
                 timeout_sec: float):
        super().__init__()
        self._api_root = api_root.rstrip('/') + '/' if api_root else None
        self._access_token = access_token
        self._timeout_sec = timeout_sec

    async def call_action(self, action: str, **params) -> Any:
        if not self._api_root:
            raise ApiNotAvailable

        headers = {}
        if self._access_token:
            headers['Authorization'] = 'Bearer ' + self._access_token

        try:
            async with httpx.AsyncClient(timeout=self._timeout_sec) as client:
                resp = await client.post(self._api_root + action,
                                         json=params,
                                         headers=headers)
            if 200 <= resp.status_code < 300:
                return _handle_api_result(json.loads(resp.text))
            raise HttpFailed(resp.status_code)
        except httpx.InvalidURL:
            raise NetworkError('API root url invalid')
        except httpx.HTTPError:
            raise NetworkError('HTTP request failed')


class _SequenceGenerator:
    _seq = 1

    @classmethod
    def next(cls) -> int:
        s = cls._seq
        cls._seq = (cls._seq + 1) % sys.maxsize
        return s


class ResultStore:
    _futures: Dict[int, asyncio.Future] = {}

    @classmethod
    def add(cls, result: Dict[str, Any]):
        if isinstance(result.get('echo'), dict) and \
                isinstance(result['echo'].get('seq'), int):
            future = cls._futures.get(result['echo']['seq'])
            if future:
                future.set_result(result)

    @classmethod
    async def fetch(cls, seq: int, timeout_sec: float) -> Dict[str, Any]:
        future = asyncio.get_event_loop().create_future()
        cls._futures[seq] = future
        try:
            return await asyncio.wait_for(future, timeout_sec)
        except asyncio.TimeoutError:
            # haven't received any result until timeout,
            # we consider this API call failed with a network error.
            raise NetworkError('WebSocket API call timeout')
        finally:
            # don't forget to remove the future object
            del cls._futures[seq]


class WebSocketReverseApi(AsyncApi):
    """
    反向 WebSocket API 实现类。

    实现通过反向 WebSocket 调用 OneBot API。
    """

    def __init__(self, connected_api_clients: Dict[str, Websocket],
                 connected_event_clients: Set[Websocket],
                 timeout_sec: float):
        super().__init__()
        self._api_clients = connected_api_clients
        self._event_clients = connected_event_clients
        self._timeout_sec = timeout_sec

    async def call_action(self, action: str, **params) -> Any:
        api_ws = None
        if params.get('self_id'):
            # 明确指定
            api_ws = self._api_clients.get(str(params['self_id']))
        elif event_ws and event_ws in self._event_clients:
            # 没有指定，但在事件处理函数中
            api_ws = self._api_clients.get(event_ws.headers['X-Self-ID'])
        elif len(self._api_clients) == 1:
            # 没有指定，不在事件处理函数中，但只有一个连接
            api_ws = tuple(self._api_clients.values())[0]

        if not api_ws:
            raise ApiNotAvailable

        seq = _SequenceGenerator.next()
        await api_ws.send(
            json.dumps({
                'action': action,
                'params': params,
                'echo': {
                    'seq': seq
                }
            }))
        return _handle_api_result(await
                                  ResultStore.fetch(seq, self._timeout_sec))


class UnifiedApi(AsyncApi):
    """
    统一 API 实现类。

    同时维护 `HttpApi` 和 `WebSocketReverseApi` 对象，根据可用情况，选择两者中的某个使用。
    """

    def __init__(self,
                 http_api: Optional[AsyncApi] = None,
                 wsr_api: Optional[AsyncApi] = None):
        super().__init__()
        self._http_api = http_api
        self._wsr_api = wsr_api

    async def call_action(self, action: str, **params) -> Any:
        result = None
        succeeded = False

        if self._wsr_api:
            # WebSocket is preferred
            try:
                result = await self._wsr_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded and self._http_api:
            try:
                result = await self._http_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded:
            raise ApiNotAvailable
        return result


class SyncWrapperApi(SyncApi):
    """
    封装 `AsyncApi` 对象，使其可同步地调用。
    """

    def __init__(self, async_api: AsyncApi,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        `async_api` 参数为 `AsyncApi` 对象，`loop` 参数为用来执行 API
        调用的 event loop。
        """
        self._async_api = async_api
        self._loop = loop or asyncio.get_event_loop()

    def call_action(self, action: str, **params) -> Any:
        """同步地调用 OneBot API。"""
        return sync_wait(coro=self._async_api.call_action(action, **params),
                         loop=self._loop)


class LazyApi(Api):
    """
    延迟获取 `aiocqhttp.api.Api` 对象。
    """

    def __init__(self, api_getter: Callable[[], Api]):
        self._api_getter = api_getter

    def call_action(self, action: str, **params) -> Union[Awaitable[Any], Any]:
        """获取 `Api` 对象，并调用 OneBot API。"""
        api = self._api_getter()
        return api.call_action(action, **params)
