"""
此模块主要提供了 `CQHttp` 类（类似于 Flask 的 `Flask` 类和 Quart 的 `Quart`
类）；除此之外，还从 `message`、`event`、`exceptions`
模块导入了一些常用的类、模块变量和函数，以便于使用。
"""

import asyncio
import hmac
import logging
import re
from typing import Dict, Any, Optional, AnyStr, Callable, Union, Awaitable, Coroutine

try:
    import ujson as json
except ImportError:
    import json

from quart import Quart, request, abort, jsonify, websocket, Response

from .api import AsyncApi, SyncApi
from .api_impl import (
    SyncWrapperApi,
    HttpApi,
    WebSocketReverseApi,
    UnifiedApi,
    ResultStore,
)
from .bus import EventBus
from .exceptions import Error, TimingError
from .event import Event
from .message import Message, MessageSegment
from .utils import ensure_async, run_async_funcs
from .typing import Message_T

from . import exceptions
from .exceptions import *  # noqa: F401, F403

__all__ = [
    "CQHttp",
    "Event",
    "Message",
    "MessageSegment",
]
__all__ += exceptions.__all__

__pdoc__ = {}


def _deco_maker(deco_method: Callable, type_: str) -> Callable:
    def deco_deco(
        self, arg: Optional[Union[str, Callable]] = None, *sub_event_names: str
    ) -> Callable:
        def deco(func: Callable) -> Callable:
            if isinstance(arg, str):
                e = [type_ + "." + e for e in [arg] + list(sub_event_names)]
                # self.on(*e)(func)
                deco_method(self, *e)(func)
            else:
                # self.on(type_)(func)
                deco_method(self, type_)(func)
            return func

        if callable(arg):
            return deco(arg)
        return deco

    return deco_deco


class CQHttp(AsyncApi):
    """
    OneBot (CQHTTP) 机器人的主类，负责控制整个机器人的运行、事件处理函数的注册、OneBot
    API 的调用等。

    内部维护了一个 `Quart` 对象作为 web 服务器，提供 HTTP 协议的 ``/`` 和 WebSocket
    协议的 ``/ws/``、``/ws/api/``、``/ws/event/`` 端点供 OneBot 连接。

    由于基类 `api.AsyncApi` 继承了 `api.Api` 的 `__getattr__`
    魔术方法，因此可以在 bot 对象上直接调用 OneBot API，例如：

    ```py
    await bot.send_private_msg(user_id=10001000, message='你好')
    friends = await bot.get_friend_list()
    ```

    也可以通过 `CQHttp.call_action` 方法调用 API，例如：

    ```py
    await bot.call_action('set_group_whole_ban', group_id=10010)
    ```

    两种调用 API 的方法最终都通过 `CQHttp.api` 属性来向 OneBot
    发送请求并获取调用结果。
    """

    def __init__(
        self,
        import_name: str = "",
        *,
        api_root: Optional[str] = None,
        access_token: Optional[str] = None,
        secret: Optional[AnyStr] = None,
        message_class: Optional[type] = None,
        api_timeout_sec: Optional[float] = None,
        server_app_kwargs: Optional[dict] = None,
        **kwargs,
    ):
        """
        ``import_name`` 参数为当前模块（使用 `CQHttp` 的模块）的导入名，通常传入
        ``__name__`` 或不传入。

        ``api_root`` 参数为 OneBot API 的 URL，``access_token`` 和
        ``secret`` 参数为 OneBot 配置中填写的对应项。

        ``message_class`` 参数为要用来对 `Event.message` 进行转换的消息类，可使用
        `Message`，例如：

        ```py
        from aiocqhttp import CQHttp, Message

        bot = CQHttp(message_class=Message)

        @bot.on_message
        async def handler(event):
            # 这里 event.message 已经被转换为 Message 对象
            assert isinstance(event.message, Message)
        ```

        ``api_timeout_sec`` 参数用于设置 OneBot API 请求的超时时间，单位是秒。

        ``server_app_kwargs`` 参数用于配置 `Quart` 对象，将以命名参数形式传给入其初始化函数。
        """
        self._api = UnifiedApi()
        self._sync_api = None
        self._bus = EventBus()
        self._before_sending_funcs = set()
        self._loop = None

        self._server_app = Quart(import_name, **(server_app_kwargs or {}))
        self._server_app.before_serving(self._before_serving)
        self._server_app.add_url_rule(
            "/", methods=["POST"], view_func=self._handle_http_event
        )
        for p in ("/ws", "/ws/event", "/ws/api"):
            self._server_app.add_websocket(
                p, strict_slashes=False, view_func=self._handle_wsr
            )

        self._configure(api_root, access_token, secret, message_class, api_timeout_sec)

    def _configure(
        self,
        api_root: Optional[str] = None,
        access_token: Optional[str] = None,
        secret: Optional[AnyStr] = None,
        message_class: Optional[type] = None,
        api_timeout_sec: Optional[float] = None,
    ):
        self._message_class = message_class
        api_timeout_sec = api_timeout_sec or 60  # wait for 60 secs by default
        self._access_token = access_token
        self._secret = secret
        self._api._http_api = HttpApi(api_root, access_token, api_timeout_sec)
        self._wsr_api_clients = {}  # connected wsr api clients
        self._wsr_event_clients = set()
        self._api._wsr_api = WebSocketReverseApi(
            self._wsr_api_clients, self._wsr_event_clients, api_timeout_sec
        )

    async def _before_serving(self):
        self._loop = asyncio.get_running_loop()

    @property
    def asgi(self) -> Callable[[dict, Callable, Callable], Awaitable]:
        """ASGI app 对象，可使用支持 ASGI 的 web 服务器软件部署。"""
        return self._server_app

    @property
    def server_app(self) -> Quart:
        """Quart app 对象，可用来对 Quart 的运行做精细控制，或添加新的路由等。"""
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        """Quart app 的 logger，等价于 ``bot.server_app.logger``。"""
        return self._server_app.logger

    @property
    def loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """Quart app 所在的 event loop，在 app 运行之前为 `None`。"""
        return self._loop

    @property
    def api(self) -> AsyncApi:
        """`api.AsyncApi` 对象，用于异步地调用 OneBot API。"""
        return self._api

    @property
    def sync(self) -> SyncApi:
        """
        `api.SyncApi` 对象，用于同步地调用 OneBot API，例如：

        ```py
        @bot.on_message('group')
        def sync_handler(event):
            user_info = bot.sync.get_group_member_info(
                group_id=event.group_id, user_id=event.user_id
            )
            ...
        ```
        """
        if not self._sync_api:
            if not self._loop:
                raise TimingError("attempt to access sync api " "before bot is running")
            self._sync_api = SyncWrapperApi(self._api, self._loop)
        return self._sync_api

    def run(self, host: str = "127.0.0.1", port: int = 8080, *args, **kwargs) -> None:
        """运行 bot 对象，实际就是运行 Quart app，参数与 `Quart.run` 一致。"""
        if "use_reloader" not in kwargs:
            kwargs["use_reloader"] = False
        self._server_app.run(host=host, port=port, *args, **kwargs)

    def run_task(
        self, host: str = "127.0.0.1", port: int = 8080, *args, **kwargs
    ) -> Coroutine[None, None, None]:
        if "use_reloader" not in kwargs:
            kwargs["use_reloader"] = False
        return self._server_app.run_task(host=host, port=port, *args, **kwargs)

    async def call_action(self, action: str, **params) -> Any:
        """
        通过内部维护的 `api.AsyncApi` 具体实现类调用 OneBot API，``action``
        为要调用的 API 动作名，``**params`` 为 API 所需参数。
        """
        return await self._api.call_action(action=action, **params)

    async def send(
        self, event: Event, message: Message_T, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        向触发事件的主体发送消息。

        ``event`` 参数为事件对象，``message`` 参数为要发送的消息。可额外传入 ``at_sender``
        命名参数用于控制是否 at 事件的触发者，默认为 `False`。其它命名参数作为
        OneBot API ``send_msg`` 的参数直接传递。
        """
        msg = message if isinstance(message, Message) else Message(message)
        await run_async_funcs(self._before_sending_funcs, event, msg, kwargs)

        at_sender = kwargs.pop("at_sender", False) and ("user_id" in event)

        keys = {"message_type", "user_id", "group_id", "discuss_id"}
        params = {k: v for k, v in event.items() if k in keys}
        params["message"] = msg
        params.update(kwargs)

        if "message_type" not in params:
            if "group_id" in params:
                params["message_type"] = "group"
            elif "discuss_id" in params:
                params["message_type"] = "discuss"
            elif "user_id" in params:
                params["message_type"] = "private"

        if at_sender and params["message_type"] != "private":
            params["message"] = (
                MessageSegment.at(params["user_id"])
                + MessageSegment.text(" ")
                + params["message"]
            )

        return await self.send_msg(**params)

    def before_sending(self, func: Callable) -> Callable:
        """
        注册发送消息前的钩子函数，用作装饰器，例如：

        ```py
        @bot.before_sending
        async def hook(event: Event, message: Message, kwargs: Dict[str, Any]):
            message.clear()
            message.append(MessageSegment.text('hooked!'))
        ```

        该钩子函数在刚进入 `CQHttp.send` 函数时运行，用户可在钩子函数中修改要发送的
        ``message`` 和发送参数 ``kwargs``。
        """
        self._before_sending_funcs.add(ensure_async(func))
        return func

    def subscribe(self, event_name: str, func: Callable) -> None:
        """注册事件处理函数。"""
        self._bus.subscribe(event_name, ensure_async(func))

    def unsubscribe(self, event_name: str, func: Callable) -> None:
        """取消注册事件处理函数。"""
        self._bus.unsubscribe(event_name, func)

    def on(self, *event_names: str) -> Callable:
        """
        注册事件处理函数，用作装饰器，例如：

        ```py
        @bot.on('notice.group_decrease', 'notice.group_increase')
        async def handler(event):
            pass
        ```

        参数为要注册的事件名，格式是点号分割的各级事件类型，见 `Event.name`。

        可以多次调用，一个函数可作为多个事件的处理函数，一个事件也可以有多个处理函数。

        可以按不同粒度注册处理函数，例如：

        ```py
        @bot.on('message')
        async def handle_message(event):
            pass

        @bot.on('message.private')
        async def handle_private_message(event):
            pass

        @bot.on('message.private.friend')
        async def handle_friend_private_message(event):
            pass
        ```

        当收到好友私聊消息时，会首先运行 ``handle_friend_private_message``，然后运行
        ``handle_private_message``，最后运行 ``handle_message``。
        """

        def deco(func: Callable) -> Callable:
            for name in event_names:
                self.subscribe(name, func)
            return func

        return deco

    on_message = _deco_maker(on, "message")
    __pdoc__[
        "CQHttp.on_message"
    ] = """
    注册消息事件处理函数，用作装饰器，例如：

    ```py
    @bot.on_message('private')
    async def handler(event):
        pass
    ```

    这等价于：

    ```py
    @bot.on('message.private')
    async def handler(event):
        pass
    ```

    也可以不加参数，表示注册为所有消息事件的处理函数，例如：

    ```py
    @bot.on_message
    async def handler(event):
        pass
    ```
    """

    on_notice = _deco_maker(on, "notice")
    __pdoc__["CQHttp.on_notice"] = "注册通知事件处理函数，用作装饰器，用法同上。"

    on_request = _deco_maker(on, "request")
    __pdoc__["CQHttp.on_request"] = "注册请求事件处理函数，用作装饰器，用法同上。"

    on_meta_event = _deco_maker(on, "meta_event")
    __pdoc__["CQHttp.on_meta_event"] = "注册元事件处理函数，用作装饰器，用法同上。"

    def hook_before(self, event_name: str, func: Callable) -> None:
        """注册事件处理前的钩子函数。"""
        self._bus.hook_before(event_name, ensure_async(func))

    def unhook_before(self, event_name: str, func: Callable) -> None:
        """取消注册事件处理前的钩子函数。"""
        self._bus.unhook_before(event_name, func)

    def before(self, *event_names: str) -> Callable:
        """
        注册事件处理前的钩子函数，用作装饰器，例如：

        ```py
        @bot.before('notice.group_decrease', 'notice.group_increase')
        async def hook(event):
            pass
        ```

        参数为要注册的事件名，格式是点号分割的各级事件类型，见 `Event.name`。

        钩子函数的注册方法和事件处理函数几乎完全一致，只需将 ``on`` 改为 ``before``。

        各级 before 钩子函数全部运行完成后，才会运行事件处理函数。
        """

        def deco(func: Callable) -> Callable:
            for name in event_names:
                self.hook_before(name, func)
            return func

        return deco

    before_message = _deco_maker(before, "message")
    __pdoc__[
        "CQHttp.before_message"
    ] = """
    注册消息事件处理前的钩子函数，用作装饰器，例如：

    ```py
    @bot.before_message('private')
    async def hook(event):
        pass
    ```

    这等价于：

    ```py
    @bot.before('message.private')
    async def hook(event):
        pass
    ```

    也可以不加参数，表示注册为所有消息事件处理前的钩子函数，例如：

    ```py
    @bot.before_message
    async def hook(event):
        pass
    ```
    """

    before_notice = _deco_maker(before, "notice")
    __pdoc__["CQHttp.before_notice"] = "注册通知事件处理前的钩子函数，用作装饰器，用法同上。"

    before_request = _deco_maker(before, "request")
    __pdoc__["CQHttp.before_request"] = "注册请求事件处理前的钩子函数，用作装饰器，用法同上。"

    before_meta_event = _deco_maker(before, "meta_event")
    __pdoc__["CQHttp.before_meta_event"] = "注册元事件处理前的钩子函数，用作装饰器，用法同上。"

    def on_startup(self, func: Callable) -> Callable:
        """
        注册 bot 启动时钩子函数，用作装饰器，例如：

        ```py
        @bot.on_startup
        async def startup():
            await db.init()
        ```
        """
        return self.server_app.before_serving(func)

    def on_websocket_connection(self, func: Callable) -> Callable:
        """
        注册 WebSocket 连接元事件处理函数，等价于 ``on_meta_event('lifecycle.connect')``，例如：

        ```py
        @bot.on_websocket_connection
        async def handler(event):
            global groups
            groups = await bot.get_group_list(self_id=event.self_id)
        ```
        """
        return self.on_meta_event("lifecycle.connect")(func)

    async def _handle_http_event(self) -> Response:
        if self._secret:
            if "X-Signature" not in request.headers:
                self.logger.warning("signature header is missed")
                abort(401)

            sec = self._secret
            sec = sec.encode("utf-8") if isinstance(sec, str) else sec
            sig = hmac.new(sec, await request.get_data(), "sha1").hexdigest()
            if request.headers["X-Signature"] != "sha1=" + sig:
                self.logger.warning("signature header is invalid")
                abort(403)

        payload = await request.json
        if not isinstance(payload, dict):
            abort(400)

        if request.headers["X-Self-ID"] in self._wsr_api_clients:
            self.logger.warning(
                "there is already a reverse websocket api connection, "
                "so the event may be handled twice."
            )

        response = await self._handle_event(payload)
        if isinstance(response, dict):
            return jsonify(response)
        return Response("", 204)

    async def _handle_wsr(self) -> None:
        if self._access_token:
            auth = websocket.headers.get("Authorization", "")
            m = re.fullmatch(r"(?:[Tt]oken|[Bb]earer) (?P<token>\S+)", auth)
            if not m:
                self.logger.warning("authorization header is missed")
                abort(401)

            token_given = m.group("token").strip()
            if token_given != self._access_token:
                self.logger.warning("authorization header is invalid")
                abort(403)

        role = websocket.headers["X-Client-Role"].lower()
        if role == "event":
            await self._handle_wsr_event()
        elif role == "api":
            await self._handle_wsr_api()
        elif role == "universal":
            await self._handle_wsr_universal()

    async def _handle_wsr_event(self) -> None:
        self._add_wsr_event_client()
        try:
            while True:
                try:
                    payload = json.loads(await websocket.receive())
                except ValueError:
                    payload = None

                if not isinstance(payload, dict):
                    # ignore invalid payload
                    continue

                asyncio.create_task(self._handle_event_with_response(payload))
        finally:
            self._remove_wsr_event_client()

    async def _handle_wsr_api(self) -> None:
        self._add_wsr_api_client()
        try:
            while True:
                try:
                    ResultStore.add(json.loads(await websocket.receive()))
                except ValueError:
                    pass
        finally:
            self._remove_wsr_api_client()

    async def _handle_wsr_universal(self) -> None:
        self._add_wsr_api_client()
        self._add_wsr_event_client()
        try:
            while True:
                try:
                    payload = json.loads(await websocket.receive())
                except ValueError:
                    payload = None

                if not isinstance(payload, dict):
                    # ignore invalid payload
                    continue

                if "post_type" in payload:
                    # is a event
                    asyncio.create_task(self._handle_event_with_response(payload))
                elif payload:
                    # is a api result
                    ResultStore.add(payload)
        finally:
            self._remove_wsr_event_client()
            self._remove_wsr_api_client()

    def _add_wsr_api_client(self) -> None:
        ws = websocket._get_current_object()
        self_id = websocket.headers["X-Self-ID"]
        self._wsr_api_clients[self_id] = ws

    def _remove_wsr_api_client(self) -> None:
        self_id = websocket.headers["X-Self-ID"]
        if self_id in self._wsr_api_clients:
            # we must check the existence here,
            # because we allow wildcard ws connections,
            # that is, the self_id may be '*'
            del self._wsr_api_clients[self_id]

    def _add_wsr_event_client(self) -> None:
        ws = websocket._get_current_object()
        self._wsr_event_clients.add(ws)

    def _remove_wsr_event_client(self) -> None:
        ws = websocket._get_current_object()
        self._wsr_event_clients.discard(ws)

    async def _handle_event(self, payload: Dict[str, Any]) -> Any:
        ev = Event.from_payload(payload)
        if not ev:
            return

        event_name = ev.name
        self.logger.info(f"received event: {event_name}")

        if self._message_class and "message" in ev:
            ev["message"] = self._message_class(ev["message"])
        results = list(
            filter(lambda r: r is not None, await self._bus.emit(event_name, ev))
        )
        # return the first non-none result
        return results[0] if results else None

    async def _handle_event_with_response(self, payload: Dict[str, Any]) -> None:
        response = await self._handle_event(payload)
        if isinstance(response, dict):
            payload.pop("message", None)  # avoid wasting bandwidth
            payload.pop("raw_message", None)
            payload.pop("comment", None)
            payload.pop("sender", None)
            try:
                await self._api.call_action(
                    self_id=payload["self_id"],
                    action=".handle_quick_operation_async",
                    context=payload,
                    operation=response,
                )
            except Error:
                pass
