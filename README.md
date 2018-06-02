# CQHttp Python SDK with Asynchronous I/O

[![License](https://img.shields.io/pypi/l/aiocqhttp.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/aiocqhttp.svg)](https://pypi.python.org/pypi/aiocqhttp)

本项目为酷 Q 的 CoolQ HTTP API 插件的新一代 Python SDK，采用异步 I/O，封装了 web server 相关的代码，支持 HTTP API 插件的 HTTP 和反向 WebSocket 两种通信方式，让使用 Python 的开发者能方便地开发插件。仅支持 Python 3.6+ 及插件 v4.x，如果你使用 v3.x 或更旧版本，请使用 [`cqhttp`](https://github.com/richardchien/python-cqhttp)。

关于 CoolQ HTTP API 插件，见 [richardchien/coolq-http-api](https://github.com/richardchien/coolq-http-api)；关于异步 I/O，见 [asyncio](https://docs.python.org/3/library/asyncio.html)。

## 用法

首先安装 `aiocqhttp` 包：

```sh
pip install aiocqhttp
```

注意可能需要把 `pip` 换成 `pip3`。

也可以 clone 本仓库之后用 `python setup.py install` 来安装。

然后新建 Python 文件，运行 CQHttp 后端：

```py
from cqhttp import CQHttp

bot = CQHttp(api_root='http://127.0.0.1:5700/',
             access_token='your-token',
             secret='your-secret')


@bot.on_message()
async def handle_msg(context):
    await bot.send(context, '你好呀，下面一条是你刚刚发的：')
    return {'reply': context['message'], 'at_sender': False}


@bot.on_notice('group_increase')
async def handle_group_increase(context):
    await bot.send(context, message='欢迎新人～', is_raw=True)  # 发送欢迎新人


@bot.on_request('group', 'friend')
async def handle_request(context):
    return {'approve': True}  # 同意所有加群、加好友请求


bot.run(host='127.0.0.1', port=8080)
```

上面的代码便实现了一个基于 HTTP 通信方式的最基本的 QQ 机器人后端，下面来做具体解释。

### `CQHttp` 类

首先需要创建一个 `CQHttp` 类的实例。有三种可行的用法：

#### 只使用 HTTP

传入 `api_root`，即为酷 Q HTTP API 插件的监听地址，如果你不需要调用 API，也可以不传入。访问令牌（`access_token`）和签名密钥（`secret`）也在这里传入，如果没有配置插件的 `access_token` 或 `secret` 项，则不传。

示例：

```python
bot = CQHttp(api_root='http://127.0.0.1:5700/',
             access_token='your-token',
             secret='your-secret')
```

#### 只使用反向 WebSocket

不需要传入 `api_root`、`secret`，但如果插件中配置了 `access_token`，仍需要传入 `access_token`。除此之外，还需要设置 `enable_http_post` 为 `False`，以禁用 HTTP 上报的入口。

示例：

```python
bot = CQHttp(access_token='your-token',
             enable_http_post=False)
```

#### 混合使用 HTTP 和反向 WebSocket

混合使用时创建 `CQHttp` 类的方式和只用 HTTP 时一样，`CQHttp` 类会同时开启 HTTP 和反向 WebSocket 的入口，但需要注意的是，插件中**不应**同时配置 `post_url` 和 `ws_reverse_event_url`，否则事件将会被同一个函数处理两次，API 调用则不存在这个问题。

### 事件处理

`CQHttp` 类的实例的 `on_message`、`on_notice`、`on_request` 三个装饰器分别对应三个上报类型（`post_type`），括号中指出要处理的消息类型（`message_type`）、通知类型（`notice_type`）、请求类型（`request_type`），一次可指定多个，如果留空，则会处理所有这个上报类型的上报。在上面的例子中 `handle_msg` 函数将会在收到任意渠道的消息时被调用，`handle_group_increase` 函数会在群成员增加时调用。

上面三个装饰器装饰的函数，统一接受一个参数，即为上报的数据，具体数据内容见 [事件上报](https://richardchien.github.io/coolq-http-api/#/Post)；返回值可以是一个字典，会被自动作为 JSON 响应返回给 HTTP API 插件，具体见 [上报请求的响应数据格式](https://richardchien.github.io/coolq-http-api/#/Post?id=%E4%B8%8A%E6%8A%A5%E8%AF%B7%E6%B1%82%E7%9A%84%E5%93%8D%E5%BA%94%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F)。

无论使用 HTTP 和反向 WebSocket 方式来上报事件，都调用同样的事件处理函数，因此，如果插件同时配置了 `post_url` 和 `ws_reverse_event_url`，事件将会被处理两次。另外，对于 HTTP 上报，事件处理函数的返回值会被作为快速操作来返回给插件，例如 `return {'reply': context['message']}` 将会让插件把收到的消息重新发出去；反向 WebSocket 上报则会忽略处理函数的返回值。

### API 调用

创建实例时传入的 `api_root` 和当前已连接到反向 WebSocket API 入口的客户端都会被用于 API 调用，**如果同时可用，则优先使用反向 WebSocket**。

直接在 `CQHttp` 类的实例上就可以调用 API，例如 `bot.send_private_msg(user_id=123456, message='hello')`，这里的 `send_private_msg` 即为 [`/send_private_msg` 发送私聊消息](https://richardchien.github.io/coolq-http-api/#/API?id=send_private_msg-%E5%8F%91%E9%80%81%E7%A7%81%E8%81%8A%E6%B6%88%E6%81%AF) 中的 `/send_private_msg`，**API 所需参数直接通过命名参数（keyword argument）传入**。其它 API 见 [API 描述](https://richardchien.github.io/coolq-http-api/#/API)。

为了简化发送消息的操作，提供了 `send(context, message)` 函数，这里的第一个参数 `context` 也就是上报数据，传入之后函数会自己判断当前需要发送到哪里（哪个好友，或哪个群），无需手动再指定，其它参数仍然可以从 keyword argument 指定，例如 `auto_escape=True`。

每个 API 调用最后都会由 `aiohttp` 库来发出请求，如果网络无法连接或连接出现错误，它可能会抛出 `aiohttp.ClientConnectorError` 等异常，见 [Client exceptions](https://docs.aiohttp.org/en/stable/client_reference.html#client-exceptions)。而一旦请求成功，本 SDK 会判断 HTTP 响应状态码，只有当状态码为 200，且 `status` 字段为 `ok` 或 `async` 时，会返回 `data` 字段的内容，否则抛出 `cqhttp.ApiError` 异常，在这个异常中你可以通过 `status_code` 和 `retcode` 属性来获取 HTTP 状态码和插件的 `retcode`（如果状态码不为 200，则 `retcode` 为 None），具体响应状态码和 `retcode` 的含义，见 [响应说明](https://richardchien.github.io/coolq-http-api/#/API?id=%E5%93%8D%E5%BA%94%E8%AF%B4%E6%98%8E)。

如果 `api_root` 和已连接的反向 WebSocket 客户端**都不可用**，则调用会返回 `None`。

### 运行实例

使用装饰器定义好处理函数之后，调用 `bot.run()` 即可运行。你需要传入 `host` 和 `port` 参数，来指定服务端需要运行在哪个地址。

后端运行了之后，需要配置 HTTP API 插件。对于 HTTP 事件上报，需要配置 `post_url` 为 `http://host:port/`；对于反向 WebSocket 事件上报和 API 调用，分别需要配置 `ws_reverse_event_url` 和 `ws_reverse_api_url` 为 `ws://host:port/ws/event/` 和 `ws://host:port/ws/api/`。其中 `host` 和 `port` 均为 `bot.run()` 运行时的相应参数。

### 部署

`bot.run()` 只适用于开发环境，不建议用于生产环境，因此 SDK 从 0.1.0 版本开始提供 `bot.wsgi` 属性以获取其内部兼容 WSGI 的 app 对象，从而可以使用 Gunicorn、uWSGI 等软件来部署。

## 遇到问题

如果在使用本 SDK 时遇到任何问题，请 [提交 issue](https://github.com/richardchien/python-aiocqhttp/issues/new)。
