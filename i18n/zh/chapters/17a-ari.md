# Asterisk REST Interface (ARI)

上一章介绍了 AMI 和 AGI，这是将外部逻辑挂载到 Asterisk 上的两种经典方式。两者都早于现代 Web 技术：AMI 通过 TCP 套接字提供原始的、面向行的事件流，而 AGI 则在通话期间将单个通道交给脚本处理。这两种方式都不是为当今人们构建的那种有状态、异步、多通道的应用程序而设计的——例如与 Web 服务交互的 IVR、点击拨号仪表板、会议控制器，或将音频流传输到语音引擎的语音机器人。

ARI（Asterisk REST Interface）在 Asterisk 12 中被引入以填补这一空白，而在 Asterisk 22 中，它是构建新电话应用程序的推荐接口。ARI 背后的理念是清晰的关注点分离：**Asterisk 成为媒体引擎**（它负责应答通道、混合桥接、播放和录制音频、发送 DTMF），而**你的应用程序通过 REST (HTTP) API 和 WebSocket 事件流的组合提供所有的呼叫控制逻辑**。

## 目标

读完本章后，读者应该能够：

- 解释什么是 ARI，以及它与 AMI 和 AGI 的区别
- 决定何时为项目选择 ARI 接口
- 配置 `ari.conf` 和 `http.conf` 以启用 ARI 并创建用户
- 连接到 ARI WebSocket 事件流
- 描述 Stasis dialplan 应用程序以及 `StasisStart`/`StasisEnd` 事件
- 描述 ARI 资源模型：通道、桥接、播放、录音、endpoint 和设备状态
- 使用 Python 编写一个最小化的 Stasis 应用程序，实现应答通道、播放声音并挂断
- 解释什么是 `externalMedia` 通道，以及它对于 AI 和语音机器人集成的重要性

## 什么是 ARI，以及何时使用它

ARI 构建在两个协同工作的传输层之上：

- **REST (HTTP) API**：你的应用程序调用它来*执行*操作——发起通道、应答、播放声音、创建桥接、开始录音、挂断。这些是对 `http://asterisk-host:8088/ari/...` 发起的普通 HTTP 请求（`GET`、`POST`、`DELETE`）。
- **WebSocket 事件流**：Asterisk 通过它*告诉*你的应用程序正在发生什么——通道已创建、收到 DTMF 数字、播放结束、通道离开了你的应用程序。事件以 JSON 对象形式交付。

这种模式是异步的：你发出一个请求，该请求的*结果*通常稍后作为事件返回。例如，你 `POST` 一个播放声音的请求；Asterisk 立即返回一个 `Playback` 对象，几秒钟后，当音频播放完毕时，你会收到一个 `PlaybackFinished` 事件。

在以下情况下选择 ARI 而非 AMI 和 AGI：

- 你需要**对通道和桥接进行细粒度控制**——构建会议、呼叫驻留、队列或自定义呼叫流程，而不是依赖 dialplan 应用程序。
- 你的应用程序是**有状态且长寿命的**，同时持有多个通道并对所有通道的事件做出反应。
- 你希望与** Web 服务、消息总线或 AI/语音引擎**集成，并且更喜欢使用 JSON over HTTP 而不是行协议或 stdin/stdout 脚本。
- 你正在启动一个**新项目**，并且想要 Asterisk 项目积极推荐的接口。

当你只需要*观察*系统或触发偶尔的命令（拨号器、墙板、监控）时，AMI 仍然是正确的工具。对于快速、独立的 IVR 脚本，AGI 仍然很方便。但对于任何编排呼叫的任务，ARI 都是现代化的解决方案。

> ARI 并不取代 dialplan，而是对其进行补充。通道像往常一样在 dialplan 中运行，直到它到达 `Stasis()` 应用程序，此时控制权被移交给你的 ARI 应用程序。当你的应用程序完成任务后，通道可以被送回 dialplan 或挂断。

## 启用 ARI：http.conf 和 ari.conf

ARI 运行在 Asterisk 内置的 HTTP 服务器之上，因此涉及两个配置文件：`http.conf` 用于启用 Web 服务器，`ari.conf` 用于启用 ARI 并定义其用户。

### http.conf

必须启用 HTTP 服务器并将其绑定到地址和端口。传统的 ARI 端口是 **8088**。

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

在生产环境中，你应该将 ARI 放在 TLS 之后。Asterisk 可以直接提供 HTTPS 服务（`tlsenable=yes`、`tlsbindaddr`、`tlscertfile`、`tlsprivatekey`），或者你可以在 8088 端口前的反向代理中终止 TLS。通过 TLS，URL 将变为 `https://` 和 `wss://`，而不是 `http://` 和 `ws://`。

你可以从 CLI 确认 HTTP 服务器是否已启动：

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` 包含一个 `[general]` 部分，以及每个用户一个部分。

```ini
[general]
enabled=yes
pretty=yes              ; pretty-print JSON responses (handy while learning)

[asterisk]
type=user
read_only=no            ; set to yes for a user that may only issue GET requests
password=secret
password_format=plain   ; "plain" (default) or "crypt"
```

关于这些选项的几点说明：

- `enabled` 全局开启或关闭 ARI。
- `pretty` 将 JSON 响应格式化为人类可读；在生产环境中请将其关闭。
- 每个用户都是一个带有 `type=user` 的命名部分。
- `read_only=yes` 将该用户限制为只读 (GET) 请求。
- `password_format` 可以是 `plain`（密码为明文）或 `crypt`（使用 `mkpasswd -m sha-512` 生成的哈希密码）。
- `permit`、`deny` 和 `acl` 允许按用户进行 IP 限制，遵循与 `acl.conf` 相同的规则。

编辑文件后，重新加载相关模块（`module reload res_ari.so` 和 `module reload http.so`）或重启 Asterisk。你可以通过以下命令验证 ARI 是否正在运行：

```
asterisk*CLI> module show like res_ari
res_ari.so          Asterisk RESTful Interface          Running
res_ari_channels.so RESTful API module - Channel res... Running
res_ari_bridges.so  RESTful API module - Bridge reso... Running
...

asterisk*CLI> ari show apps
Application Name
=========================
```

`ari show apps` 列出了当前由已连接客户端注册的 Stasis 应用程序。在客户端连接之前它是空的，这正是我们接下来要做的。

### WebSocket 事件 URL

客户端通过打开一个到 `/ari/events` endpoint 的 WebSocket 来订阅事件流，指定它实现的 Stasis 应用程序名称并传递其凭据：

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

查询参数包括：

- `app`——你的 Stasis 应用程序名称。这是你在 dialplan 的 `Stasis()` 调用中使用的相同名称。你可以传递多个以逗号分隔的名称。
- `api_key`——凭据，格式为 `username:password`，与 `ari.conf` 中的用户匹配。
- `subscribeAll`——可选的布尔值（默认 `false`）；当为 `true` 时，应用程序接收所有事件，而不仅仅是它拥有的资源的事件。

相同的 `user:pass` 凭据在 REST 调用中用作 HTTP Basic auth（或者也可以在那里作为 `api_key` 查询参数附加）。

## Stasis：将通道交给你的应用程序

dialplan 和 ARI 之间的桥梁是 **`Stasis()`** dialplan 应用程序（底层框架也称为 Stasis）。当通道到达 `Stasis(appname[,args])` 时，Asterisk 将该通道交给在 `appname` 下注册的 ARI 应用程序，并停止为其执行 dialplan。控制权现在属于你的代码。

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

当通道进入应用程序时，每个订阅了 `hello` 的已连接客户端都会通过 WebSocket 收到一个 **`StasisStart`** 事件，其中包含完整的通道对象（其 ID、名称、主叫 ID、状态以及传递给 `Stasis()` 的任何参数）。这是你开始控制通道的信号。

当通道离开应用程序时——因为你的代码使用 `continueInDialplan` 将其移回 dialplan，或者因为它被挂断——你会收到一个 **`StasisEnd`** 事件。在 `Stasis()` 返回到 dialplan 后，它会设置 `STASISSTATUS` 通道变量（`SUCCESS` 或 `FAILED`），以便 dialplan 可以根据结果进行分支处理。

## ARI 资源模型

ARI 将 Asterisk 的内部结构暴露为一小组 REST 资源。每个资源都位于 `/ari/<resource>` 下，并使用标准的 HTTP 方法进行操作。最重要的资源如下：

| 资源 | 代表什么 | 示例操作 |
|----------|--------------------|--------------------|
| **channels** | 单个呼叫链路 | originate, answer, play, record, hangup |
| **bridges** | 连接通道的混合点 | create, add/remove channels, play to the bridge |
| **playbacks** | 正在进行的媒体播放 | get status, stop, pause/unpause |
| **recordings** | 实时和已存储的录音 | start, stop, list stored, delete |
| **endpoints** | 已配置的对端 (PJSIP 等) | list, get state, send a message |
| **deviceStates** | 自定义设备状态 | list, get, set, delete |

一些具体的 REST 调用（路径显示为在线路上出现的 `/ari` 前缀）：

```
# Channels
POST   /ari/channels                          # originate a new channel
POST   /ari/channels/{channelId}/answer       # answer an incoming channel
POST   /ari/channels/{channelId}/play         # play media (body: media=sound:hello-world)
POST   /ari/channels/{channelId}/record       # record the channel
DELETE /ari/channels/{channelId}              # hang up the channel

# Bridges
POST   /ari/bridges                           # create a bridge (e.g. type=mixing)
POST   /ari/bridges/{bridgeId}/addChannel     # add a channel (param: channel=<id>)
POST   /ari/bridges/{bridgeId}/play           # play media to everyone in the bridge
DELETE /ari/bridges/{bridgeId}                # destroy the bridge

# Read-only resources
GET    /ari/endpoints
GET    /ari/deviceStates
GET    /ari/recordings/stored
GET    /ari/playbacks/{playbackId}
```

`play` 请求上的 `media` 参数接受一个媒体 URI。最常见的形式是命名内置声音的 `sound:` URI，例如 `sound:hello-world` 或 `sound:tt-monkeys`。当音频播放结束时，Asterisk 会为该播放 ID 发出一个 `PlaybackFinished` 事件，这就是你的应用程序知道可以继续下一步的方式。

通道和桥接是你组合起来创建呼叫流程的两个构建块。例如，要连接两个呼叫者，你可以发起或接受两个通道，使用 `POST /ari/bridges` 创建一个 `mixing` 桥接，并使用 `POST /ari/bridges/{bridgeId}/addChannel` 将两个通道添加到其中。要构建会议，你只需不断向同一个桥接添加通道即可。

## 工作示例：最小化的 Stasis 应用程序

让我们构建一个最小的有用 ARI 应用程序。当拨打任何 extension 时，呼叫进入我们的 Stasis 应用程序，它会应答呼叫，播放经典的 `hello-world` 提示音，然后挂断。

### dialplan

在 `extensions.conf` 中，将通道发送到 Stasis：

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

应用程序名称 `hello` 与我们连接时使用的 `app=hello` 相匹配。

### Python 客户端

此客户端使用两个众所周知的库：`requests` 用于 REST 调用，`websocket-client` 用于事件流。使用 `pip install requests websocket-client` 安装它们。

```python
#!/usr/bin/env python3
"""Minimal ARI Stasis app: answer, play hello-world, hang up."""
import json
import requests
from websocket import create_connection

ARI_HOST = "127.0.0.1"
ARI_PORT = 8088
ARI_USER = "asterisk"
ARI_PASS = "secret"
APP = "hello"

BASE = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

def answer(channel_id):
    requests.post(f"{BASE}/channels/{channel_id}/answer", auth=AUTH)

def play(channel_id, media):
    # Returns the Playback object; we could track its id to await PlaybackFinished.
    r = requests.post(
        f"{BASE}/channels/{channel_id}/play",
        params={"media": media},
        auth=AUTH,
    )
    return r.json()

def hangup(channel_id):
    requests.delete(f"{BASE}/channels/{channel_id}", auth=AUTH)

def main():
    ws_url = (
        f"ws://{ARI_HOST}:{ARI_PORT}/ari/events"
        f"?app={APP}&api_key={ARI_USER}:{ARI_PASS}"
    )
    ws = create_connection(ws_url)
    print(f"Connected to ARI, waiting for calls into Stasis app '{APP}'...")

    # Track which channel each playback belongs to, so we hang up when it ends.
    playback_owner = {}

    while True:
        event = json.loads(ws.recv())
        kind = event["type"]

        if kind == "StasisStart":
            channel_id = event["channel"]["id"]
            print(f"StasisStart on channel {channel_id}")
            answer(channel_id)
            pb = play(channel_id, "sound:hello-world")
            playback_owner[pb["id"]] = channel_id

        elif kind == "PlaybackFinished":
            pb_id = event["playback"]["id"]
            channel_id = playback_owner.pop(pb_id, None)
            if channel_id:
                print(f"Playback done, hanging up {channel_id}")
                hangup(channel_id)

        elif kind == "StasisEnd":
            print(f"StasisEnd on channel {event['channel']['id']}")

if __name__ == "__main__":
    main()
```

运行脚本，然后从已注册的 endpoint 拨打任何号码。你应该会听到 "Hello, world"，之后呼叫被释放。在 Asterisk 控制台上，`ari show apps` 现在将列出 `hello`，同时客户端处于连接状态。

这个流程值得追踪一次：

1. dialplan 运行 `Stasis(hello)`；Asterisk 将通道交给我们的应用程序并发送一个 `StasisStart` 事件。
2. 我们应答通道，然后要求 Asterisk 播放 `sound:hello-world`。Asterisk 返回一个 `Playback` 对象，我们记住了它的 `id`。
3. 当音频播放结束时，Asterisk 发送带有该播放 `id` 的 `PlaybackFinished`；我们查找该通道并将其挂断。
4. 挂断导致通道离开 Stasis，产生一个 `StasisEnd` 事件。

> **关于客户端库的说明。** 存在一个名为 `ari-py`（`ari` 包）的高级封装，但它已不再维护，是为旧时代的 Python 和 Swagger 工具编写的。对于 Asterisk 22 上的新工作，请优先使用上面展示的显式 `requests` + WebSocket 方法，或者如果你需要并发性，可以使用像 `asyncari` 这样的 asyncio 库。原始方法让你更接近实际的 REST 调用和事件，这正是你在学习 ARI 时所需要的。

## externalMedia：通往 AI 和语音机器人之门

上面的资源让你能够播放和录制*文件*。但现代语音应用程序——语音转文字转录、AI 语音机器人、实时分析——需要将呼叫的*实时音频流*传送到外部进程，并且需要注入音频。

ARI 通过 **`externalMedia` 通道**提供此功能。`POST /ari/channels/externalMedia` 请求创建一个特殊的通道，它不是与电话通话，而是将呼叫的 RTP 媒体流传输到（并从）外部主机。你将此通道与呼叫者的通道进行桥接，现在你的外部程序就处于音频路径中：它接收呼叫者的音频作为 RTP，并可以发回合成音频。

该请求仅需要：

- `app`——拥有新通道的 Stasis 应用程序。
- `format`——音频格式，例如 `ulaw` 或 `slin16`。

`external_host`（你的媒体应用程序的 `host:port`）在模式中是可选的——对于 WebSocket 服务器风格的连接，它可以为空——但对于经典的 RTP 语音机器人，你将提供它。`encapsulation` 参数默认为 `rtp`，`transport` 默认为 `udp`，这正是你对流媒体 endpoint 所需要的。

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

这个单一特性就是将 Asterisk 转变为 AI 前端的关键：电话网络在 Asterisk 上终止，ARI 编排呼叫，而 `externalMedia` 将音频传送到语音/AI 引擎并传回。这就是 AI 服务和语音机器人构建的机制。

## 总结

ARI 是在 Asterisk 22 上构建电话应用程序的现代化推荐接口。它清晰地分工：Asterisk 是媒体引擎，而你的应用程序——通过 HTTP 和 WebSocket 使用 JSON 通信——提供呼叫控制逻辑。你通过 `http.conf`（端口 8088 上的内置 Web 服务器）和 `ari.conf`（开启 ARI 并定义用户）来启用它。`Stasis()` dialplan 应用程序将通道交给你的应用程序，在进入时引发 `StasisStart`，在离开时引发 `StasisEnd`。从那里，你操作一小组 REST 资源——通道、桥接、播放、录音、endpoint 和设备状态——来应答、播放、录制、桥接和挂断。我们构建了一个最小化的 Python Stasis 应用程序，它应答呼叫、播放提示音并挂断，并且我们看到了 `externalMedia` 通道如何将实时 RTP 流传输到外部程序——这是 AI 和语音机器人集成的基础。

## 测验

1. ARI 是在哪个 Asterisk 版本中引入的？
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. 在 ARI 模型中，Asterisk 作为媒体引擎，而你的外部应用程序提供呼叫控制逻辑。
   - A. 正确
   - B. 错误
3. ARI 同时使用两个传输层。哪一对是正确的？
   - A. 用于发送命令的 REST/HTTP API 和用于接收事件的 WebSocket 流
   - B. TCP 行协议和 stdin/stdout 脚本
   - C. SNMP 和 SMTP
   - D. 两个独立的 UDP 套接字
4. 必须设置哪两个配置文件才能启用 ARI？
   - A. `manager.conf` 和 `agi.conf`
   - B. `http.conf` 和 `ari.conf`
   - C. `sip.conf` 和 `rtp.conf`
   - D. `modules.conf` 和 `cdr.conf`
5. Asterisk HTTP 服务器（因此也是 ARI）的传统 TCP 端口是 ____。
6. 哪个 dialplan 应用程序将通道移交给 ARI 应用程序？
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. 当通道进入 Stasis 应用程序时，哪个事件被发送到已连接的客户端？
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. 哪个 ARI 请求创建了一个可以连接两个或多个通道的混合点？
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. 要在通道上播放内置提示音，哪个事件告诉你的应用程序音频已结束，以便它可以继续下一步？
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. `externalMedia` 通道主要用于：
    - A. 将呼叫录制到本地 WAV 文件
    - B. 将呼叫的实时音频 (RTP) 流传输到外部应用程序（例如 AI/语音引擎）并从中接收音频
    - C. 注册 PJSIP endpoint
    - D. 重新加载 dialplan

**答案：** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
