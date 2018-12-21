import asyncio
import hmac
import json
import logging
from typing import Dict, Any, Optional, AnyStr, Callable, Union, List

from quart import Quart, request, abort, jsonify, websocket

from .api import HttpApi, WebSocketReverseApi, UnifiedApi, ResultStore
from .bus import EventBus
from .exceptions import *
from .message import MessageSegment


def _deco_maker(post_type: str) -> Callable:
    def deco_deco(self, arg: Optional[Union[str, Callable]] = None,
                  *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            if isinstance(arg, str):
                e = [post_type + '.' + e for e in [arg] + list(events)]
                self.on(*e)(func)
            else:
                self.on(post_type)(func)
            return func

        if isinstance(arg, Callable):
            return deco(arg)
        return deco

    return deco_deco


class CQHttp:
    def __init__(self,
                 api_root: Optional[str] = None,
                 access_token: Optional[str] = None,
                 secret: Optional[AnyStr] = None,
                 enable_http_post: bool = True,
                 message_class: type = None,
                 *args, **kwargs):
        self._access_token = access_token
        self._secret = secret
        self._bus = EventBus()
        self._server_app = Quart(__name__)

        if enable_http_post:
            self._server_app.route('/', methods=['POST'])(
                self._handle_http_event)

        self._server_app.websocket('/ws/')(self._handle_ws_reverse)
        self._server_app.websocket('/ws/event/')(self._handle_ws_reverse_event)
        self._server_app.websocket('/ws/api/')(self._handle_ws_reverse_api)
        self._connected_ws_reverse_api_clients = {}

        self._api = UnifiedApi(http_api=HttpApi(api_root, access_token),
                               ws_reverse_api=WebSocketReverseApi(
                                   self._connected_ws_reverse_api_clients))

        self._message_class = message_class

    @property
    def asgi(self) -> Quart:
        return self._server_app

    @property
    def server_app(self) -> Quart:
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        return self._server_app.logger

    def subscribe(self, event: str, func: Callable) -> None:
        self._bus.subscribe(event, func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        self._bus.unsubscribe(event, func)

    def on(self, *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            for event in events:
                self.subscribe(event, func)
            return func

        return deco

    on_message = _deco_maker('message')
    on_notice = _deco_maker('notice')
    on_request = _deco_maker('request')
    on_meta_event = _deco_maker('meta_event')

    async def _handle_http_event(self):
        if self._secret:
            if 'X-Signature' not in request.headers:
                abort(401)

            sec = self._secret
            sec = sec.encode('utf-8') if isinstance(sec, str) else sec
            sig = hmac.new(sec, await request.get_data(), 'sha1').hexdigest()
            if request.headers['X-Signature'] != 'sha1=' + sig:
                abort(403)

        payload = await request.json
        if not isinstance(payload, dict):
            abort(400)

        response = await self._handle_event_payload(payload)
        return jsonify(response) if isinstance(response, dict) else ''

    async def _handle_ws_reverse(self):
        self._validate_ws_reverse_access_token()

        role = websocket.headers.get('X-Client-Role', '').lower()
        if role == 'event':
            await self._handle_ws_reverse_event()
        elif role == 'api':
            await self._handle_ws_reverse_api()
        elif role == 'universal':
            await self._handle_ws_reverse_universal()

    def _validate_ws_reverse_access_token(self):
        if not self._access_token:
            return

        if websocket:
            auth = websocket.headers.get('Authorization', '')
            if not auth.startswith('Token ') and not auth.startswith('token '):
                abort(401)

            token_given = auth[len('Token '):].strip()
            if not token_given:
                abort(401)
            if token_given != self._access_token:
                abort(403)

    async def _handle_ws_reverse_event(self):
        try:
            while True:
                try:
                    payload = json.loads(await websocket.receive())
                except json.JSONDecodeError:
                    payload = None

                if not isinstance(payload, dict):
                    # ignore invalid payload
                    continue

                asyncio.ensure_future(
                    self._handle_event_payload_with_response(payload))
        finally:
            pass

    async def _handle_ws_reverse_api(self):
        self._add_ws_reverse_api_connection()
        try:
            while True:
                try:
                    ResultStore.add(json.loads(await websocket.receive()))
                except json.JSONDecodeError:
                    pass
        finally:
            self._remove_ws_reverse_api_connection()

    async def _handle_ws_reverse_universal(self):
        self._add_ws_reverse_api_connection()
        try:
            while True:
                try:
                    payload = json.loads(await websocket.receive())
                except json.JSONDecodeError:
                    payload = None

                if isinstance(payload, dict) and 'post_type' in payload:
                    # is a event
                    asyncio.ensure_future(
                        self._handle_event_payload_with_response(payload))
                elif payload:
                    # is a api result
                    ResultStore.add(payload)
        finally:
            self._remove_ws_reverse_api_connection()

    def _add_ws_reverse_api_connection(self) -> None:
        # noinspection PyProtectedMember
        ws = websocket._get_current_object()
        self_id = websocket.headers.get('X-Self-ID', '*')
        self._connected_ws_reverse_api_clients[self_id] = ws

    def _remove_ws_reverse_api_connection(self) -> None:
        self_id = websocket.headers.get('X-Self-ID', '*')
        if self_id in self._connected_ws_reverse_api_clients:
            # we must check the existence here,
            # because we allow wildcard ws connections,
            # that is, the self_id may be '*'
            del self._connected_ws_reverse_api_clients[self_id]

    async def _handle_event_payload(self, payload: Dict[str, Any]) -> Any:
        post_type = payload.get('post_type')
        detailed_type = payload.get('{}_type'.format(post_type))
        if not post_type or not detailed_type:
            return

        event = post_type + '.' + detailed_type
        if payload.get('sub_type'):
            event += '.' + payload['sub_type']

        context = payload.copy()
        if self._message_class and 'message' in context:
            context['message'] = self._message_class(context['message'])
        results = list(filter(lambda r: r is not None,
                              await self._bus.emit(event, context)))
        # return the first non-none result
        return results[0] if results else None

    async def _handle_event_payload_with_response(
            self, payload: Dict[str, Any]) -> None:
        response = await self._handle_event_payload(payload)
        if isinstance(response, dict):
            try:
                await self._api.call_action(
                    action='.handle_quick_operation_async',
                    context=payload, operation=response
                )
            except Error:
                pass

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def call_action(self, action: str, **params) -> Any:
        return await self._api.call_action(action=action, **params)

    def __getattr__(self, item) -> Callable:
        return self._api.__getattr__(item)

    async def send(self, context: Dict[str, Any],
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs) -> Optional[Dict[str, Any]]:
        at_sender = kwargs.pop('at_sender', False) and 'user_id' in context

        context = context.copy()
        context['message'] = message
        context.update(kwargs)
        if 'message_type' not in context:
            if 'group_id' in context:
                context['message_type'] = 'group'
            elif 'discuss_id' in context:
                context['message_type'] = 'discuss'
            elif 'user_id' in context:
                context['message_type'] = 'private'

        if at_sender and context['message_type'] != 'private':
            context['message'] = MessageSegment.at(context['user_id']) + \
                                 MessageSegment.text(' ') + context['message']

        return await self.send_msg(**context)
