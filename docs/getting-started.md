# 开始使用

## 安装

首先安装 `aiocqhttp` 包：

```bash
pip install aiocqhttp
```

<Note>

可能需要将 `pip` 换成 `pip3`。

</Note>

默认情况下将安装必要依赖 `Quart` 和 `aiocqhttp`。若要安装可选依赖，可使用：

```bash
pip install aiocqhttp[all]
```

这将会额外安装 `ujson`。

## 最小实例

新建 Python 文件（这里假设名为 `bot.py`），内容如下：

```python
# bot.py

from aiocqhttp import CQHttp, Event

bot = CQHttp()


@bot.on_message('private')
async def _(event: Event):
    await bot.send(event, '你发了：')
    return {'reply': event.message}


bot.run(host='127.0.0.1', port=8080)
```

<Note>

如果需要在不同主机上运行此 bot 后端和 酷Q（CQHTTP），则此处 `host` 应该为 bot 后端所在主机的 IP 或 `0.0.0.0`。

如果你在使用 VPS，应确保在安全组中开放 8080 端口。

</Note>

运行该文件，看到如下输出即为启动成功：

```
Running on http://127.0.0.1:8080 (CTRL + C to quit)
[2020-01-29 19:27:57,133] Running on 127.0.0.1:8080 over http (CTRL + C to quit)
```

<Note>

如果没有启动成功，建议检查 Python 版本是否过旧、端口是否被占用等。

</Note>

## 配置 CQHTTP

### 使用反向 WebSocket

在 CQHTTP 配置文件中，填写 `ws_reverse_url` 值为 `ws://127.0.0.1:8080/ws/`，这里 `127.0.0.1:8080` 应根据情况改为 `bot.py` 中传给 `bot.run` 的 `host` 和 `port` 参数。

然后，如果有的话，删掉 `ws_reverse_event_url` 和 `ws_reverse_api_url` 这两个配置项。

接着设置 `use_ws_reverse` 为 `true`。

最后重启 CQHTTP。

### 使用 HTTP

修改 `bot.py` 中创建 `bot` 对象部分的代码为：

```python
bot = CQHttp(api_root='http://127.0.0.1:5700')
```

这里 `127.0.0.1:5700` 应根据情况改为 CQHTTP 所监听的 IP 和端口（由 CQHTTP 配置中的 `host` 和 `port` 指定）。

然后在 CQHTTP 配置文件中，填写 `post_url` 为 `http://127.0.0.1:8080/`，这里 `127.0.0.1:8080` 应根据情况改为 `bot.py` 中传给 `bot.run` 的 `host` 和 `port` 参数。

接着设置 `use_http` 为 `true`（默认就是 `true`）。

最后重启 CQHTTP。

## 测试对话

给你的机器人发一段私聊消息，如果一切正常，ta 应该会回复你。

<Note>

如果没有回复，请检查 `bot.py` 运行是否报错、酷Q 日志是否报错。如果都没有报错，则可能是机器人账号被腾讯风控，需要在同一环境中多登录一段时间。

</Note>
