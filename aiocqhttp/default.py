from . import CQHttp
from .api import LazyApi

__all__ = [
    'default_bot', 'default_server_app', 'reconfigure_default_bot',
    'on', 'on_message', 'on_notice', 'on_request', 'on_meta_event',
    'run', 'send', 'api', 'sync_api'
]

default_bot = CQHttp()
default_server_app = default_bot.server_app
reconfigure_default_bot = default_bot._configure

on = default_bot.on
on_message = default_bot.on_message
on_notice = default_bot.on_notice
on_request = default_bot.on_request
on_meta_event = default_bot.on_meta_event
run = default_bot.run
send = default_bot.send
api = default_bot.api
sync_api = LazyApi(lambda: default_bot.sync)
