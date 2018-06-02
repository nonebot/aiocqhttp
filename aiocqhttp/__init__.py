import hmac
import json
import functools
from collections import defaultdict
from typing import Dict, Any, Optional, AnyStr, Callable

from quart import Quart, request, abort, jsonify, websocket

from . import api
from .api import HttpApi, WebSocketReverseApi, UnifiedApi

ApiError = api.Error


def _deco_maker(post_type: str):
    def deco_decorator(self, *types):
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            if types:
                for t in types:
                    self._handlers[post_type][t] = wrapper
            else:
                self._handlers[post_type]['*'] = wrapper
            return wrapper

        return decorator

    return deco_decorator


class CQHttp:
    def __init__(self,
                 api_root: Optional[str] = None,
                 access_token: Optional[str] = None,
                 secret: Optional[AnyStr] = None):
        self._secret = secret
        self._handlers = defaultdict(dict)
        self._server_app = Quart(__name__)

        self._server_app.route('/', methods=['POST'])(self._handle_http_event)

        self._server_app.websocket('/ws/event/')(self._handle_ws_reverse_event)
        self._server_app.websocket('/ws/api/')(self._handle_ws_reverse_api)
        self._connected_ws_reverse_api_clients = set()

        self.api = UnifiedApi(
            http_api=HttpApi(api_root, access_token),
            ws_reverse_api=WebSocketReverseApi(
                self._connected_ws_reverse_api_clients)
        )

    on_message = _deco_maker('message')
    on_notice = _deco_maker('notice')
    on_request = _deco_maker('request')

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

                await self._handle_event_payload(payload)
        finally:
            pass

    async def _handle_ws_reverse_api(self):
        # noinspection PyProtectedMember
        ws = websocket._get_current_object()
        self._connected_ws_reverse_api_clients.add(ws)
        try:
            while True:
                print(await websocket.receive())
        finally:
            self._connected_ws_reverse_api_clients.remove(ws)

    async def _handle_event_payload(self, payload: Dict[str, Any]):
        post_type = payload.get('post_type')
        type_key = payload.get({'message': 'message_type',
                                'notice': 'notice_type',
                                'request': 'request_type'}.get(post_type))
        handler = self._handlers[post_type].get(
            type_key, self._handlers[post_type].get('*'))
        if handler:
            return await handler(payload)

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    def __getattr__(self, item):
        return self.api.__getattr__(item)

    async def send(self, context, message, **kwargs):
        context = context.copy()
        context['message'] = message
        context.update(kwargs)
        return await self.send_msg(**context)
