# 更新日志

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
