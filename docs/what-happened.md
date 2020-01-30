# 发生了什么

本节围绕 [开始使用](/getting-started) 中的最小实例，来解释它如何工作。

先贴出代码：

```python
# bot.py

from aiocqhttp import CQHttp, Event

bot = CQHttp()  # M1


@bot.on_message('private')  # M2
async def _(event: Event):  # M3
    await bot.send(event, '你发了：')  # M4
    return {'reply': event.message}  # M5


bot.run(host='127.0.0.1', port=8080)  # M6
```

## `CQHttp` 类

M1 处首先创建了 `aiocqhttp.CQHttp` 类的对象 `bot`。

该类是本 SDK 的主体，内部封装了 [Quart](https://pgjones.gitlab.io/quart/) 对象作为 web 服务器。其中添加了 `/`、`/ws/` 等路由，从而使 CQHTTP 能够通过 HTTP 或 WebSocket 协议连接 `bot`。

使用 HTTP 通信时，需要传入 `api_root` 参数是因为 `bot.send` 需要主动调用 CQHTTP API，它需要知道 CQHTTP「在哪」。

使用反向 WebSocket 通信时，可以有多个 CQHTTP 同时连接到一个 `bot`，`bot.send` 会自动选择对应的账号发送。

## 事件处理

M2 处通过 `@bot.on_message('private')` 装饰器注册了 [私聊消息事件](https://cqhttp.cc/docs/#/Post?id=私聊消息) 的处理函数。

除了 `bot.on_message`，还有类似的 `bot.on_notice`、`bot.on_request`、`bot.on_meta_event`，它们分别用于注册消息、通知、请求、元事件这四种事件类型（对应 [CQHTTP 事件](https://cqhttp.cc/docs/#/Post) 的 `post_type` 字段）的处理函数。

这些装饰器可以带参数，也可以不带参数，参数可以有多个，对应 CQHTTP 事件的 `?_type` 字段，这里 `?_type` 根据事件类型的不同，分别为 `message_type`、`notice_type`、`request_type`、`meta_event_type`。

M3 处定义了事件处理函数，它必须接受一个 `Event` 对象作为唯一的参数。`Event` 对象是对 CQHTTP 事件数据的简单封装，提供了属性以方便获取其中的字段，例如 `event.message`、`event.user_id` 等。

## API 调用

M4 处调用了 `bot.send` 方法，该方法是对 [CQHTTP API](https://cqhttp.cc/docs/#/API) 中 [`send_msg`](https://cqhttp.cc/docs/#/API?id=send_msg-发送消息) 的简单封装，它会向 `event` 对应的主体发送消息（由第二个参数指定），本例中这个主体是「发私聊消息来的人」。

除此之外，你可以在 `bot` 对象上直接调用任何 CQHTTP API，见 [API 列表](https://cqhttp.cc/docs/#/API?id=api-列表)，所需参数通过命名参数传递，例如：

```python
friends = await bot.get_friend_list()

await bot.set_group_ban(group_id=10010, user_id=10001000)

credentials = await bot.get_credentials(domain='qun.qq.com')
```

<Note>

如果有多个 CQHTTP 连接，可能需要在调用 API 时增加 `self_id` 参数以指定要调用的机器人账号，例如：

```python
await bot.get_friend_list(self_id=event.self_id)
```

</Note>

调用 API 时需向 CQHTTP 发出请求，这一步可能出错：

- 如果 API 当前不可用（例如没有任何连接了的 CQHTTP、或未配置 `api_root`），抛出 `aiocqhttp.ApiNotAvailable`
- 如果 API 可用，但网络无法连接或连接出现错误，抛出 `aiocqhttp.NetworkError`

一旦请求成功，SDK 会判断 HTTP 响应状态码是否为 2xx：

- 如果不是，抛出 `aiocqhttp.HttpFailed`，在这个异常中可通过 `status_code` 获取 HTTP 响应状态码
- 如果是，则进一步查看响应 JSON 的 `status` 字段，如果 `status` 字段为 `failed`，抛出 `aiocqhttp.ActionFailed`，在这个异常中可通过 `retcode` 获取 API 调用的返回码

以上异常全都继承自 `aiocqhttp.Error`。

如果 `status` 为 `ok` 或 `async`，则不抛出异常，函数返回 CQHTTP API 响应数据的 `data` 字段（有可能为 `None`）。

HTTP 响应状态码和 `retcode` 的具体含义，见 [响应说明](https://cqhttp.cc/docs/#/API?id=响应说明)。

## 快速操作

M5 处事件处理函数返回了一个字典，这会被 SDK 序列化为 JSON 并返回给 CQHTTP，作为 [CQHTTP 事件上报的响应](https://cqhttp.cc/docs/#/Post?id=上报请求的响应数据格式)（通过 HTTP 响应正文或 WebSocket 传送）。这称为「快速操作」，可用于对事件进行一些简单的操作，本例中对事件进行了「回复」操作，对于群聊等事件，快速操作还包括「禁言」「撤回」等，具体请见 [事件列表](https://cqhttp.cc/docs/#/Post?id=事件列表) 的「响应数据」。

快速操作不是必须的，事件处理函数可以不返回任何值。

## 运行

M6 处调用 `bot.run` 运行了 bot 后端，该方法是 Quart 对象的 `run` 方法的简单封装，可直接传入更多参数，参数会直接进入 [`Quart.run`](https://pgjones.gitlab.io/quart/source/quart.html#quart.Quart.run)。

## 更多

更丰富的例子见 [`demo.py`](https://github.com/cqmoe/python-aiocqhttp/blob/master/demo.py)。

本节所提到的类、方法、函数等，均可在右上角「模块 API」中找到更详细的说明。
