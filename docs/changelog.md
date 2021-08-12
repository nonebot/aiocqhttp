# 更新日志

## master

- 修复从 `str` 构造 `Message` 时无法正确去转义参数 [#57](https://github.com/nonebot/aiocqhttp/issues/57)

## v1.4.1

- 修复上一版本中 `ActionFailed` 的不兼容更新 [#53](https://github.com/nonebot/aiocqhttp/issues/53)

## v1.4.0

- 调整 `ActionFailed` 错误信息格式 [#44](https://github.com/nonebot/aiocqhttp/pull/44)
- 修复多个 WebSocket 同时存在时可能引发的 bug [#43](https://github.com/nonebot/aiocqhttp/pull/43)
- 提升 Quart 依赖至 0.14. 如升级 aiocqhttp 后遇到错误请升级依赖
- 更新消息段 (`MessageSegment`) 和 API stub 至 OneBot v11 标准。调整 `api` 和 `api_impl` 的继承关系
- 调整消息 `+=` 的处理方式 [#48](https://github.com/nonebot/aiocqhttp/issues/48)

## v1.3.0

- `CQHttp` 类新增 `on_startup` 装饰器，用于注册 bot 对象启动时钩子函数
- `CQHttp` 类新增 `on_websocket_connection` 装饰器，用于注册 WebSocket 连接事件处理函数
- `CQHttp` 类新增 `before_*` 装饰器（`before`、`before_message` 等），用于注册事件处理前的钩子函数，使用方式同 `on_*` 装饰器
- `CQHttp` 类新增 `before_sending` 装饰器，用于注册发送消息前的钩子函数
- 修复 `Message` 对象拼接运算的 bug [#32](https://github.com/nonebot/aiocqhttp/pull/32)

## v1.2.5

- 修复使用 Quart app 时，无法找到模板文件夹等问题
- `CQHttp` 类新增位置参数 `import_name`，通常应不传入（保持默认）或传入 `__name__`
- `CQHttp` 类新增 `server_app_kwargs` 参数，用于配置 Quart 对象，将以命名参数的形式传入其初始化函数

## v1.2.3

- 新增 `CQHttp.run_task` 方法，运行产生 coroutine 而不是直接启动事件循环

## v1.2.2

- `CQHttp` 类新增 `api_timeout_sec` 参数，用于设置 CQHTTP API 请求的超时时间（单位秒）
- 默认关闭 Quart 的 reloader（监测文件变更，自动重启）
- 修复 `api` 模块 stub 文件缺少 `self_id` 参数问题
- 修复多个 CQHTTP 连接同一后端时，通过 `self_id` 指定机器人无效的问题

## v1.2.1

- 修复 `api` 模块 stub 文件返回类型问题

## v1.2.0

- 提升 Quart 依赖包版本到 0.11，另外，v1.1.0 及更早的版本不兼容 Quart 0.11，需手动安装或降级至 0.10
- 替换 aiohttp 为 httpx，便于在同步函数中使用

## v1.1.0

- 新增 `typing` 模块，提供一些类型提示的定义
- 调整 `api` 模块的继承关系，移动 API 实现类到单独的 `api_impl` 模块，并为 `api` 模块提供 stub 文件，以便编辑器进行自动补全

## v1.0.1

- 修复与 NoneBot v1 的兼容性问题
- `CQHttp` 类初始化器参数全部改为命名参数

## v1.0.0

- `on_*` 装饰器支持将同步函数注册为事件处理函数，将在 asyncio 的默认 executor 中运行（可通过 `loop.set_default_executor` 修改）
- `CQHttp` 类新增 `sync` 属性，可用于在同步函数中调用 CQHTTP API
- 新增默认 `CQHttp` 实例 `aiocqhttp.default.default_bot`，可通过 `aiocqhttp.default.on_message` 等装饰器直接注册事件处理函数、通过 `aiocqhttp.default.run` 运行实例、通过 `aiocqhttp.default.send` 发送消息、通过 `aiocqhttp.default.api` 调用 CQHTTP API 等
- 事件处理函数的唯一参数改为 `aiocqhttp.Event` 类，提供属性方便获取事件数据，此类基于 `dict`，因此兼容现有代码
- `CQHttp` 类初始化器移除 `enable_http_post` 命名参数
- 不再支持 CQHTTP v4.0~4.7，请升级至 v4.8 或更新版本
- 代码中添加大量注释，便于查阅

## v0.7.0

- 修复 WebSocket URI 结尾必须带 `/` 的问题，现在能够正确处理 `/ws` 等
- 更新依赖版本（Quart、aiohttp）
- 提升最低 Python 版本要求至 3.7

## v0.6.8

- 修复反向 WebSocket API 和 Event 独立连接时没有校验 access token 的问题

## v0.6.7

- 修复使用反向 WebSocket 的 Universal 客户端时，事件回调函数返回的快速操作不能正确执行的问题
- `CQHttp.send()` 方法新增 `at_sender` 命名参数（默认 `False`），可在发送消息时 at 发送者（只在群组和讨论组有效，私聊会忽略此参数）

## v0.6.6

- 支持反向 WebSocket 的 Universal 客户端，无须作任何特殊配置

## v0.6.5

- `MessageSegment` 类支持互相加法运算，运算结果为 `Message` 类
- `Message` 类的 `append()` 和 `extend()` 方法现返回 `self`，以便链式调用

## v0.6.4

- 支持插件 v4.5.0 的 `meta_event` 上报
- `CQHttp` 类新增 `server_app` 属性，以明确获得内部的 `Quart` 对象，和原来的 `asgi` 属性等价

## v0.6.3

- 修复 `bot.send()` 在非消息事件处理函数中发送失败的 bug

## v0.6.2

- 支持插件 v4.4.0 新增的反向 WebSocket 共用 URL 特性

## v0.6.1

- 当 WebSocket 只有一个 API 连接时，调用 `call_action()` 时不必传入 `self_id` 也可以自动选择使用唯一的连接来发送
