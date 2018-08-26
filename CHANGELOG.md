# 更新日志

## v0.6.1

- 当 WebSocket 只有一个 API 连接时，调用 `call_action()` 时不必传入 `self_id` 也可以自动选择使用唯一的连接来发送
