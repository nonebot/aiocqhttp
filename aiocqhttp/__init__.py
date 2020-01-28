import asyncio
import hmac
import logging
import re
from typing import Dict, Any, Optional, AnyStr, Callable, Union, List

try:
    import ujson as json
except ImportError:
    import json

from quart import Quart, request, abort, jsonify, websocket, Response

from .api import HttpApi, WebSocketReverseApi, UnifiedApi, ResultStore
from .bus import EventBus
from .exceptions import *
from .message import Message, MessageSegment
from .event import Event
from .utils import ensure_async

__all__ = [
    'CQHttp', 'Message', 'MessageSegment', 'Event'
]


def _deco_maker(type_: str) -> Callable:
    def deco_deco(self, arg: Optional[Union[str, Callable]] = None,
                  *sub_event_names: str) -> Callable:
        def deco(func: Callable) -> Callable:
            handler = ensure_async(func)
            if isinstance(arg, str):
                e = [type_ + '.' + e for e in [arg] + list(sub_event_names)]
                self.on(*e)(handler)
            else:
                self.on(type_)(handler)
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
                 message_class: Optional[type] = None):
        self.api = UnifiedApi()  # TODO: rename to _api
        self._bus = EventBus()
        self._loop = None

        self._server_app = Quart(__name__)
        self._server_app.before_serving(self._before_serving)
        self._server_app.add_url_rule('/', methods=['POST'],
                                      view_func=self._handle_http_event)
        for p in ('/ws', '/ws/event', '/ws/api'):
            self._server_app.add_websocket(p, strict_slashes=False,
                                           view_func=self._handle_wsr)

        self._configure(api_root, access_token, secret, message_class)

    def _configure(self,
                   api_root: Optional[str] = None,
                   access_token: Optional[str] = None,
                   secret: Optional[AnyStr] = None,
                   message_class: Optional[type] = None):
        self._access_token = access_token
        self._secret = secret
        self._message_class = message_class
        self._wsr_api_clients = {}  # connected wsr api clients
        self.api._http_api = HttpApi(api_root, access_token)
        self.api._wsr_api = WebSocketReverseApi(self._wsr_api_clients)

    def _before_serving(self):
        self._loop = asyncio.get_running_loop()

    @property
    def asgi(self) -> Quart:
        return self._server_app

    @property
    def server_app(self) -> Quart:
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        return self._server_app.logger

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    def subscribe(self, event_name: str, func: Callable) -> None:
        self._bus.subscribe(event_name, func)

    def unsubscribe(self, event_name: str, func: Callable) -> None:
        self._bus.unsubscribe(event_name, func)

    def on(self, *event_names: str) -> Callable:
        def deco(func: Callable) -> Callable:
            for name in event_names:
                self.subscribe(name, func)
            return func

        return deco

    on_message = _deco_maker('message')
    on_notice = _deco_maker('notice')
    on_request = _deco_maker('request')
    on_meta_event = _deco_maker('meta_event')

    async def _handle_http_event(self) -> Response:
        if self._secret:
            if 'X-Signature' not in request.headers:
                self.logger.warning('signature header is missed')
                abort(401)

            sec = self._secret
            sec = sec.encode('utf-8') if isinstance(sec, str) else sec
            sig = hmac.new(sec, await request.get_data(), 'sha1').hexdigest()
            if request.headers['X-Signature'] != 'sha1=' + sig:
                self.logger.warning('signature header is invalid')
                abort(403)

        payload = await request.json
        if not isinstance(payload, dict):
            abort(400)

        if request.headers['X-Self-ID'] in self._wsr_api_clients:
            self.logger.warning(
                'there is already a reverse websocket api connection, '
                'so the event may be handled twice.')

        response = await self._handle_event(payload)
        if isinstance(response, dict):
            return jsonify(response)
        return Response('', 204)

    async def _handle_wsr(self) -> None:
        if self._access_token:
            auth = websocket.headers.get('Authorization', '')
            m = re.fullmatch(r'(?:[Tt]oken|[Bb]earer) (?P<token>\S+)', auth)
            if not m:
                self.logger.warning('authorization header is missed')
                abort(401)

            token_given = m.group('token').strip()
            if token_given != self._access_token:
                self.logger.warning('authorization header is invalid')
                abort(403)

        role = websocket.headers['X-Client-Role'].lower()
        if role == 'event':
            await self._handle_wsr_event()
        elif role == 'api':
            await self._handle_wsr_api()
        elif role == 'universal':
            await self._handle_wsr_universal()

    async def _handle_wsr_event(self) -> None:
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
            pass

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
        try:
            while True:
                try:
                    payload = json.loads(await websocket.receive())
                except ValueError:
                    payload = None

                if not isinstance(payload, dict):
                    # ignore invalid payload
                    continue

                if 'post_type' in payload:
                    # is a event
                    asyncio.create_task(
                        self._handle_event_with_response(payload))
                elif payload:
                    # is a api result
                    ResultStore.add(payload)
        finally:
            self._remove_wsr_api_client()

    def _add_wsr_api_client(self) -> None:
        ws = websocket._get_current_object()
        self_id = websocket.headers['X-Self-ID']
        self._wsr_api_clients[self_id] = ws

    def _remove_wsr_api_client(self) -> None:
        self_id = websocket.headers['X-Self-ID']
        if self_id in self._wsr_api_clients:
            # we must check the existence here,
            # because we allow wildcard ws connections,
            # that is, the self_id may be '*'
            del self._wsr_api_clients[self_id]

    async def _handle_event(self, payload: Dict[str, Any]) -> Any:
        ev = Event.from_payload(payload)
        if not ev:
            return

        event_name = ev.name
        self.logger.info(f'received event: {event_name}')

        if self._message_class and 'message' in ev:
            ev['message'] = self._message_class(ev['message'])
        results = list(filter(lambda r: r is not None,
                              await self._bus.emit(event_name, ev)))
        # return the first non-none result
        return results[0] if results else None

    async def _handle_event_with_response(
            self, payload: Dict[str, Any]) -> None:
        response = await self._handle_event(payload)
        if isinstance(response, dict):
            payload.pop('message', None)  # avoid wasting bandwidth
            payload.pop('raw_message', None)
            payload.pop('comment', None)
            payload.pop('sender', None)
            try:
                await self.api.call_action(
                    self_id=payload['self_id'],
                    action='.handle_quick_operation_async',
                    context=payload, operation=response
                )
            except Error:
                pass

    def run(self, host: str = None, port: int = None, *args, **kwargs) -> None:
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def call_action(self, action: str, **params) -> Any:
        return await self.api.call_action(action=action, **params)

    def __getattr__(self, item) -> Callable:
        return self.api.__getattr__(item)

    async def send(self, event: Event,
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs) -> Optional[Dict[str, Any]]:
        at_sender = kwargs.pop('at_sender', False) and 'user_id' in event

        params = event.copy()
        params['message'] = message
        params.pop('raw_message', None)  # avoid wasting bandwidth
        params.pop('comment', None)
        params.pop('sender', None)
        params.update(kwargs)

        if 'message_type' not in params:
            if 'group_id' in params:
                params['message_type'] = 'group'
            elif 'discuss_id' in params:
                params['message_type'] = 'discuss'
            elif 'user_id' in params:
                params['message_type'] = 'private'

        if at_sender and params['message_type'] != 'private':
            params['message'] = MessageSegment.at(params['user_id']) + \
                                MessageSegment.text(' ') + params['message']

        return await self.send_msg(**params)


from . import default
from .default import *

__all__ += default.__all__
