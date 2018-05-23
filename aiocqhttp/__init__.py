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


class _ApiClient(object):
    def __init__(self, api_root=None, access_token=None):
        self._url = api_root.rstrip('/') if api_root else None
        self._access_token = access_token

    def __getattr__(self, item):
        if self._url:
            return _ApiClient(
                api_root=self._url + '/' + item,
                access_token=self._access_token
            )

    async def __call__(self, *args, **kwargs):
        headers = {}
        if self._access_token:
            headers['Authorization'] = 'Token ' + self._access_token
        async with aiohttp.request('POST', self._url,
                                   json=kwargs, headers=headers) as resp:
            if 200 <= resp.status < 300:
                data = json.loads(await resp.text())
                if data.get('status') == 'failed':
                    raise Error(resp.status, data.get('retcode'))
                return data.get('data')
            raise Error(resp.status)


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


class CQHttp(_ApiClient):
    def __init__(self, api_root=None, access_token=None, secret=None):
        super().__init__(api_root, access_token)
        self._secret = secret
        self._handlers = defaultdict(dict)
        self._app = Quart(__name__)
        self._app.route('/', methods=['POST'])(self._handle)

    on_message = _deco_maker('message')
    on_notice = _deco_maker('notice')
    on_request = _deco_maker('request')

    async def _handle(self):
        headers = request.headers
        if self._secret:
            # check signature
            if 'X-Signature' not in headers:
                abort(401)

            sec = self._secret
            if isinstance(sec, str):
                sec = sec.encode('utf-8')
            sig = hmac.new(sec, await request.get_data(), 'sha1').hexdigest()
            if headers['X-Signature'] != 'sha1=' + sig:
                abort(403)

        payload = await request.json

        post_type = payload.get('post_type')
        if post_type not in ('message', 'notice', 'request'):
            abort(400)

        handler_key = None
        for pk_pair in (('message', 'message_type'),
                        ('notice', 'notice_type'),
                        ('request', 'request_type')):
            if post_type == pk_pair[0]:
                handler_key = payload.get(pk_pair[1])
                if not handler_key:
                    abort(400)
                else:
                    break

        if not handler_key:
            abort(400)

        handler = self._handlers[post_type].get(handler_key)
        if not handler:
            handler = self._handlers[post_type].get('*')  # try wildcard
        if handler:
            assert callable(handler)
            response = await handler(payload)
            return jsonify(response) if isinstance(response, dict) else ''
        return ''

    def run(self, host=None, port=None, **kwargs):
        self._app.run(host=host, port=port, **kwargs)

    async def echo(self, context, **kwargs):
        context = context.copy()
        context.update(kwargs)
        return await self.send_msg(**context)

    async def send(self, context, message, **kwargs):
        context = context.copy()
        context['message'] = message
        context.update(kwargs)
        return await self.send_msg(**context)
