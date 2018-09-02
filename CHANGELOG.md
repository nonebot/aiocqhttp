# 更新日志

## v0.6.2

- 支持插件 v4.4.0 新增的反向 WebSocket 共用 URL 特性

## v0.6.1

- 当 WebSocket 只有一个 API 连接时，调用 `call_action()` 时不必传入 `self_id` 也可以自动选择使用唯一的连接来发送
