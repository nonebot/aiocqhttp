# CQHttp Python SDK with Asynchronous I/O

[![License](https://img.shields.io/github/license/richardchien/python-aiocqhttp.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/aiocqhttp.svg)](https://pypi.python.org/pypi/aiocqhttp)

本项目为酷 Q 的 CoolQ HTTP API 插件的新一代 Python SDK，采用异步 I/O，封装了 web server 相关的代码，支持 HTTP API 插件的 HTTP 和反向 WebSocket 两种通信方式，让使用 Python 的开发者能方便地开发插件。仅支持 Python 3.6+ 及插件 v4.x，如果你使用较旧版本，请使用 [`python-cqhttp`](https://github.com/richardchien/python-cqhttp)。

关于 CoolQ HTTP API 插件，见 [richardchien/coolq-http-api](https://github.com/richardchien/coolq-http-api)；关于异步 I/O，见 [asyncio](https://docs.python.org/3/library/asyncio.html)。

## 建议

本 SDK 是一个基础 SDK，只是对 CoolQ HTTP API 插件的一层简单包装，如果你想快速地编写机器人的实际功能，建议优先考虑使用 [NoneBot](https://none.rclab.tk/)，这是一个基于本 SDK 的更高封装程度的机器人框架，可以让你的开发更方便。

## 基本用法

首先安装 `aiocqhttp` 包：

```bash
pip install aiocqhttp
```

注意可能需要把 `pip` 换成 `pip3`。

也可以 clone 本仓库之后用 `python setup.py install` 来安装。

然后新建 Python 文件，运行 CQHttp 后端：

```python
from aiocqhttp import CQHttp

bot = CQHttp(api_root='http://127.0.0.1:5700/',
             access_token='your-token',
             secret='your-secret')


@bot.on_message()
async def handle_msg(context):
    await bot.send(context, '你好呀，下面一条是你刚刚发的：')
    return {'reply': context['message']}


@bot.on_notice('group_increase')
async def handle_group_increase(context):
    await bot.send(context, message='欢迎新人～', auto_escape=True)


@bot.on_request('group', 'friend')
async def handle_request(context):
    return {'approve': True}


bot.run(host='127.0.0.1', port=8080)
```

上面的代码便实现了一个基于 HTTP 通信方式的最基本的 QQ 机器人后端，下面来做具体解释。

### `CQHttp` 类

首先需要创建一个 `CQHttp` 类的实例。有三种可行的用法：

#### 只使用反向 WebSocket

不需要传入 `api_root`、`secret`，但如果插件中配置了 `access_token`，仍需要传入 `access_token`。除此之外，还需要设置 `enable_http_post` 为 `False`，以禁用 HTTP 上报的入口。

这是最推荐的用法，因为相比 HTTP，反向 WebSocket 只在插件启动时建立连接，后续的事件上报和 API 调用全都走已经建立好的连接，可以大大提高响应速度，实际测试中有大约 1～2 倍的性能提升。

示例：

```python
bot = CQHttp(access_token='your-token',
             enable_http_post=False)
```

#### 只使用 HTTP

传入 `api_root`，即为酷 Q HTTP API 插件的监听地址，如果你不需要调用 API，也可以不传入。访问令牌（`access_token`）和签名密钥（`secret`）也在这里传入，如果没有配置插件的 `access_token` 或 `secret` 项，则不传。

示例：

```python
bot = CQHttp(api_root='http://127.0.0.1:5700/',
             access_token='your-token',
             secret='your-secret')
```

#### 混合使用 HTTP 和反向 WebSocket

混合使用时创建 `CQHttp` 类的方式和只用 HTTP 时一样，`CQHttp` 类会同时开启 HTTP 和反向 WebSocket 的入口，但需要注意的是，插件中**不应**同时配置 `post_url` 和 `ws_reverse_event_url`，否则事件将会被同一个函数处理两次，API 调用则不存在这个问题。

### 事件处理

`CQHttp` 类的实例的 `on_message`、`on_notice`、`on_request`、`on_meta_event` 装饰器分别对应插件的四种上报类型（`post_type`），括号中指出要处理的消息类型（`message_type`）、通知类型（`notice_type`）、请求类型（`request_type`）、元事件类型（`meta_event_type`），一次可指定多个，如果留空，则会处理所有这个上报类型的上报。在上面的例子中 `handle_msg` 函数将会在收到任意渠道的消息时被调用，`handle_group_increase` 函数会在群成员增加时调用。

上面装饰器装饰的函数，统一接受一个参数，即为上报的数据，具体数据内容见 [事件上报](https://cqhttp.cc/docs/#/Post)；函数可以不返回值，也可以返回一个字典，会被自动作为快速操作提供给 HTTP API 插件执行（要求插件版本在 4.2 以上），例如 `return {'reply': context['message']}` 将会让插件把收到的消息重新发出去，具体见 [上报请求的响应数据格式](https://cqhttp.cc/docs/#/Post?id=%E4%B8%8A%E6%8A%A5%E8%AF%B7%E6%B1%82%E7%9A%84%E5%93%8D%E5%BA%94%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F)。

无论使用 HTTP 和反向 WebSocket 方式来上报事件，都调用同样的事件处理函数，因此，如果插件同时配置了 `post_url` 和 `ws_reverse_event_url`，事件将会被处理两次。

### API 调用

创建实例时传入的 `api_root` 和当前已连接到反向 WebSocket API 入口的客户端都会被用于 API 调用，**如果同时可用，则优先使用反向 WebSocket**。

直接在 `CQHttp` 类的实例上就可以调用 API，例如 `bot.send_private_msg(user_id=123456, message='hello')`，这里的 `send_private_msg` 即为 [`/send_private_msg` 发送私聊消息](https://cqhttp.cc/docs/#/API?id=send_private_msg-%E5%8F%91%E9%80%81%E7%A7%81%E8%81%8A%E6%B6%88%E6%81%AF) 中的 `/send_private_msg`，**API 所需参数直接通过命名参数（keyword argument）传入**。其它 API 见 [API 列表](https://cqhttp.cc/docs/#/API?id=api-列表)。

为了简化发送消息的操作，提供了 `send(context, message)` 函数，这里的第一个参数 `context` 也就是上报数据，传入之后函数会自己判断当前需要发送到哪里（哪个好友，或哪个群），无需手动再指定，其它参数仍然可以从 keyword argument 指定，例如 `auto_escape=True`。

调用 API 时，如果 API 当前不可用（例如没有任何连接了的 WebSocket、或未配置 API root），则抛出 `aiocqhttp.ApiNotAvailable`；如果 API 可用，但网络无法连接或连接出现错误，会抛出 `aiocqhttp.NetworkError` 异常。而一旦请求成功，SDK 会判断 HTTP 响应状态码是否为 2xx，如果不是，则抛出 `aiocqhttp.HttpFailed` 异常，在这个异常中可通过 `status_code` 获取 HTTP 响应状态码；如果是 2xx，则进一步查看响应 JSON 的 `status` 字段，如果 `status` 字段为 `faild`，则抛出 `aiocqhttp.ActionFailed` 异常，在这个异常中可通过 `retcode` 获取 API 调用的返回码。以上各异常全都继承自 `aiocqhttp.Error`。**如果 `status` 为 `ok` 或 `async`，则不抛出异常，函数返回插件响应数据的 `data` 字段（有可能为 None）**。具体 HTTP 响应状态码和 `retcode` 的含义，见 [响应说明](https://cqhttp.cc/docs/#/API?id=%E5%93%8D%E5%BA%94%E8%AF%B4%E6%98%8E)。

### 运行实例

使用装饰器定义好处理函数之后，调用 `bot.run()` 即可运行。你需要传入 `host` 和 `port` 参数，来指定服务端需要运行在哪个地址。

后端运行了之后，需要配置 HTTP API 插件。对于 HTTP 事件上报，需要配置 `post_url` 为 `http://host:port/`；对于反向 WebSocket 事件上报和 API 调用，分别需要配置 `ws_reverse_event_url` 和 `ws_reverse_api_url` 为 `ws://host:port/ws/event/` 和 `ws://host:port/ws/api/`。其中 `host` 和 `port` 均为 `bot.run()` 运行时的相应参数。

## 高级用法

### 部署

`bot.run()` 只适用于开发环境，不建议用于生产环境，因此 SDK 提供 `bot.asgi` 属性以获取其内部的 ASGI 实例，从而可以 [使用 ASGI 服务器来部署](https://pgjones.gitlab.io/quart/deployment.html)，例如：

```bash
hypercorn demo:bot.asgi
```

### 添加路由

`CQHttp` 内部使用 [Quart](https://pgjones.gitlab.io/quart/) 来提供 web server，默认添加了 bot 所需的 `/` 和 `/ws/` 路由（`enable_http_post=False` 时只添加了 `/ws/`），如需添加其它路由，例如在 `/admin/` 提供管理面板访问，可以通过 `bot.server_app` 访问内部的 `Quart` 实例来做到：

```python
app = bot.server_app

@app.route('/admin')
async def admin():
    return 'This is the admin page.'
```

目前 `bot.server_app` 和 `bot.asgi` 等价。

### 日志

通过 `bot.logger` 属性可以获取到 Quart 框架的 [app logger](https://pgjones.gitlab.io/quart/logging.html)，它是一个标准的 Python Logger，你可以根据自己的需求对其进行配置和使用。

### `message` 模块

可使用 `message` 模块来更方便地操作消息，主要提供 `Message` 和 `MessageSegment` 类，使用方法如下：

```python
from aiocqhttp import CQHttp
from aiocqhttp.message import Message, MessageSegment

bot = CQHttp(message_class=Message)  # message_class 默认为 None，即保持上报时的原样


@bot.on_message('group')
async def handle(context):
    # 如果设置了 message_class 参数，则这里断言就会成立
    # 该参数不影响后面发送消息时对 Message 类的使用
    assert isinstance(context['message'], Message)

    await bot.send(context, Message('你好！') + MessageSegment.at(context['user_id']))
    await bot.send(context, Message('你刚刚发了：') + context['message'].extract_plain_text())
```

相关 API 文档见 [`MessageSegment`](https://none.rclab.tk/api.html#class-messagesegment) 和 [`Message`](https://none.rclab.tk/api.html#class-message)。

## 更新日志

更新日志见 [CHANGELOG.md](CHANGELOG.md)。

## 遇到问题

如果在使用本 SDK 时遇到任何问题，请 [提交 issue](https://github.com/richardchien/python-aiocqhttp/issues/new)。
