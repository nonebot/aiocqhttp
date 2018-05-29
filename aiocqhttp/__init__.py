import hmac
import json
from collections import defaultdict
from functools import wraps

import aiohttp

from quart import Quart, request, abort, jsonify


class Error(Exception):
    def __init__(self, status_code, retcode=None):
        self.status_code = status_code
        self.retcode = retcode


def _api_client(url, access_token=None):
    async def do_call(**kwargs):
        headers = {}
        if access_token:
            headers['Authorization'] = 'Token ' + access_token
        async with aiohttp.request('POST', url,
                                   json=kwargs, headers=headers) as resp:
            if 200 <= resp.status < 300:
                data = json.loads(await resp.text())
                if data.get('status') == 'failed':
                    raise Error(resp.status, data.get('retcode'))
                return data.get('data')
            raise Error(resp.status)

    return do_call


def _deco_maker(post_type):
    def deco_decorator(self, *types):
        def decorator(func):
            @wraps(func)
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
    def __init__(self, api_root=None, access_token=None, secret=None):
        self._api_root = api_root.rstrip('/') if api_root else None
        self._access_token = access_token
        self._secret = secret
        self._handlers = defaultdict(dict)
        self._server_app = Quart(__name__)
        self._server_app.route('/', methods=['POST'])(self._handle)

    on_message = _deco_maker('message')
    on_notice = _deco_maker('notice')
    on_request = _deco_maker('request')

    async def _handle(self):
        if self._secret:
            if 'X-Signature' not in request.headers:
                abort(401)

            sec = self._secret
            sec = sec.encode('utf-8') if isinstance(sec, str) else sec
            sig = hmac.new(sec, await request.get_data(), 'sha1').hexdigest()
            if request.headers['X-Signature'] != 'sha1=' + sig:
                abort(403)

        payload = await request.json
        post_type = payload.get('post_type')

        type_key = payload.get({'message': 'message_type',
                                'notice': 'notice_type',
                                'request': 'request_type'}.get(post_type))
        if not type_key:
            abort(400)

        handler = self._handlers[post_type].get(
            type_key, self._handlers[post_type].get('*'))
        if handler:
            response = await handler(payload)
            return jsonify(response) if isinstance(response, dict) else ''

    def run(self, host=None, port=None, **kwargs):
        self._server_app.run(host=host, port=port, **kwargs)

    async def send(self, context, message, **kwargs):
        context = context.copy()
        context['message'] = message
        context.update(kwargs)
        return await self.send_msg(**context)

    def __getattr__(self, item):
        if self._api_root:
            return _api_client(self._api_root + '/' + item, self._access_token)
