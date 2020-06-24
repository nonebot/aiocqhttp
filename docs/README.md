# 介绍

**aiocqhttp** 是 [酷Q](https://cqp.cc) 的 [CQHTTP 插件](https://cqhttp.cc) 的 Python SDK，采用异步 I/O，封装了 web 服务器相关的代码，支持 CQHTTP 的 HTTP 和反向 WebSocket 两种通信方式，让使用 Python 的开发者能方便地开发插件。

本 SDK 要求使用 Python 3.7 或更高版本、CQHTTP v4.8 或更高版本。

## 特点

- 基于 asyncio，异步 I/O 使程序运行效率更高
- 支持 CQHTTP 反向 WebSocket 通信方式，允许同时作为多个机器人账号的后端
- 接口类似 Flask，直观易懂，上手成本低
- 封装了消息类，便于进行消息处理和构造
