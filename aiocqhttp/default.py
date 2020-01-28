from . import CQHttp

__all__ = [
    'default_bot', 'default_server_app',
    'on_message', 'on_notice', 'on_request', 'on_meta_event', 'on',
    'run', 'send', 'api', 'reconfigure_default_bot'
]

default_bot = CQHttp()
default_server_app = default_bot.server_app
on_message = default_bot.on_message
on_notice = default_bot.on_notice
on_request = default_bot.on_request
on_meta_event = default_bot.on_meta_event
on = default_bot.on
run = default_bot.run
send = default_bot.send
api = default_bot.api

reconfigure_default_bot = default_bot._configure
