# 常见主题

## 消息处理

为了方便地处理消息，本 SDK 提供了 `Message` 和 `MessageSegment` 类，用于解析和构造消息中的 CQ 码，例如：

```python
from aiocqhttp import Message, MessageSegment

@bot.on_message
async def handle_msg(event):
    msg = Message(event.message)
    for seg in msg:
        if seg == MessageSegment.at(event.self_id):
            await bot.send(event, 'at 我干啥')
            break

    img = MessageSegment.image('http://example.com/somepic.png')
    await bot.send(event, img + '\n上面这是一张图')
```

如果觉得手动从 `event.message` 构造 `Message` 对象不够方便，可以在 bot 对象初始化时传入 `message_class` 参数，例如：

```python
from aiocqhttp import CQHttp, Message
bot = CQHttp(message_class=Message)
```

这会使 SDK 在收到消息事件后，使用形如 `event.message = Message(event.message)` 的方式构造 `Message` 对象。

当然，如果内置的 `Message` 类不符合你的需求，你也可以自己编写消息类，同样可以传入 `message_class`。

## 默认 bot 对象

如果你只是开发一些简单的功能，或临时做测试等，可以不用自己创建 bot 对象，而直接使用 SDK 内置的默认 bot 对象，例如：

```python
from aiocqhttp.default import on_message, send, api, run

@on_message
async def handle_msg(event):
    await send(event, event.message)
    await api.send_private_msg(user_id=event.user_id, message='。。。')

run(host='127.0.0.1', port=8080)
```

如需修改 `CQHttp` 初始化的参数，可使用 `reconfigure_default_bot` 函数，例如：

```python
from aiocqhttp.default import reconfigure_default_bot
reconfigure_default_bot(api_root='http://127.0.0.1:8080')
```

## 同步和异步

通常情况下，建议在 bot 中全部使用异步操作，例如使用 [aiofiles] 读写文件、使用 [aiohttp]、[`httpx.AsyncClient`] 等进行网络请求、使用 [aiomysql]、[asyncpg]、[aioredis]、[Motor] 等访问数据库。

[aiofiles]: https://github.com/Tinche/aiofiles
[aiohttp]: https://github.com/aio-libs/aiohttp
[`httpx.AsyncClient`]: https://www.python-httpx.org/async/
[aiomysql]: https://github.com/aio-libs/aiomysql
[asyncpg]: https://github.com/MagicStack/asyncpg
[aioredis]: https://github.com/aio-libs/aioredis
[Motor]: https://github.com/mongodb/motor

但如果出于某些原因，你更偏好或不得不使用同步函数，SDK 也提供了原生支持，例如：

```python
@bot.on_message
def sync_handle_msg(event):
    time.sleep(5)  # 模拟耗时 I/O
    # 使用 bot.sync 进行 API 调用
    bot.sync.send_private_msg(user_id=event.user_id, message='处理完毕')
```

`sync_handle_msg` 会在 asyncio loop 的默认 executor（多线程，需注意线程安全）里运行，可通过 `loop.set_default_executor` 修改。

## 日志

本 SDK 直接使用了内部 Quart 对象的日志器，是一个 `logging.Logger` 对象，可通过 `bot.logger` 获得，例如：

```python
bot.logger.info('初始化成功')
```

如果你需要对 logger 进行配置，直接修改它即可（但不可给它赋值），但更建议的方式是在你的项目中自己创建新的 logger。

## 部署

默认情况下，`bot.run` 以 debug 模式运行，可通过 `bot.run(..., debug=False)` 关闭。

在实际部署环境中，不建议使用 `bot.run`，而应该使用专业的 ASGI 服务器，例如 [Uvicorn]、[Daphne]、[Hypercorn] 等。这里给出使用 Uvicorn 部署的例子：

```python
# main.py
from aiocqhttp import CQHttp
bot = CQHttp()
```

```bash
uvicorn --host 127.0.0.1 --port 8080 main:bot.asgi
```

[Uvicorn]: https://github.com/encode/uvicorn
[Daphne]: https://github.com/django/daphne
[Hypercorn]: https://gitlab.com/pgjones/hypercorn

## 添加路由

SDK 注册了 `/`、`/ws`、`/ws/api`、`/ws/event` 这几个路由，以便向 CQHTTP 提供服务。有时你可能想要注册其它自定义的路由，例如接收 webhook 推送、展示机器人状态、提供管理控制台等，可以直接操作 Quart 对象来做到，例如：

```python
@bot.server_app.route('/webhook')
async def webhook():
    pass
```

## 在已有事件循环中运行

通过 `CQHttp.run_task` 方法可以将 bot 运行在已有的事件循环中，参数同 `CQHttp.run`，例如：

```python
bot = CQHttp()

loop = asyncio.new_event_loop()
loop.create_task(bot.run_task(host='127.0.0.1', port=8080))
loop.run_forever()
```
