# The Asterisk REST Interface (ARI)

前一章介绍了 AMI 和 AGI，这两种将外部逻辑接入 Asterisk 的经典方式。它们都早于现代 Web：AMI 通过 TCP 套接字提供原始的、面向行的事件流，AGI 在通话期间将单个通道交给脚本。它们都不是为今天人们构建的那种有状态、异步、多通道的应用而设计的——与 Web 服务交互的 IVR、点击呼叫仪表板、会议控制器，或将音频流式传输到语音引擎的 voicebot。

ARI —— Asterisk REST Interface —— 在 Asterisk 12 中引入，以填补这一空白，而在 Asterisk 22 中，它已成为构建新电话应用的推荐接口。ARI 背后的理念是清晰的关注点分离：**Asterisk 成为媒体引擎**（它接听通道、混合桥接、播放和录制音频、发送 DTMF），**你的应用通过 REST（HTTP）API 和 WebSocket 事件流提供所有呼叫控制逻辑**。

## Objectives

By the end of this chapter, the reader should be able to:

- Explain what ARI is and how it differs from AMI and AGI
- Decide when ARI is the right interface for a project
- Configure `ari.conf` and `http.conf` to enable ARI and create a user
- Connect to the ARI WebSocket event stream
- Describe the Stasis dialplan application and the `StasisStart`/`StasisEnd` events
- Describe the ARI resource model: channels, bridges, playbacks, recordings, endpoints, and device states
- Write a minimal Stasis application in Python that answers a channel, plays a sound, and hangs up
- Explain what the `externalMedia` channel is and why it matters for AI and voicebot integrations

## What ARI is, and when to use it

ARI is built on two transports working together:

- **A REST (HTTP) API** that your application calls to *do* things — originate a channel, answer it, play a sound, create a bridge, start a recording, hang up. These are ordinary HTTP requests (`GET`, `POST`, `DELETE`) against `http://asterisk-host:8088/ari/...`.
- **A WebSocket event stream** over which Asterisk *tells* your application what is happening — a channel was created, a DTMF digit arrived, a playback finished, a channel left your application. Events are delivered as JSON objects.

The pattern is asynchronous: you make a request, and the *result* of that request usually comes back later as an event. For example, you `POST` a request to play a sound; Asterisk answers immediately with a `Playback` object, and some seconds later you receive a `PlaybackFinished` event when the audio is done.

Choose ARI over AMI and AGI when:

- You need **fine-grained control of channels and bridges** — building conferences, parking, queues, or custom call flows from primitives instead of relying on dialplan applications.
- Your application is **stateful and long-lived**, holding several channels at once and reacting to events across all of them.
- You want to integrate with **web services, message buses, or AI/speech engines** and prefer JSON over HTTP to a line protocol or a stdin/stdout script.
- You are starting a **new project** and want the interface the Asterisk project actively recommends.

AMI is still the right tool when you only need to *observe* the system or fire occasional commands (dialers, wallboards, monitoring). AGI is still convenient for a quick, self-contained IVR script. But for anything that orchestrates calls, ARI is the modern answer.

> ARI does not replace the dialplan — it complements it. A channel runs in the dialplan as usual until it reaches the `Stasis()` application, at which point control is handed to your ARI application. When your application is done, the channel can be sent back into the dialplan or hung up.

## 启用 ARI：http.conf 与 ari.conf

ARI 基于 Asterisk 内置的 HTTP 服务器，因此涉及两个配置文件：`http.conf`用于启用 Web 服务器，`ari.conf`用于启用 ARI 并定义其用户。

### http.conf

必须启用 HTTP 服务器并绑定到地址和端口。约定的 ARI 端口是 **8088**。

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

在生产环境中应将 ARI 放在 TLS 之下。Asterisk 可以直接提供 HTTPS（`tlsenable=yes`、`tlsbindaddr`、`tlscertfile`、`tlsprivatekey`），也可以在 8088 端口前的反向代理中终止 TLS。使用 TLS 时，URL 变为 `https://` 和 `wss://` 而不是 `http://` 和 `ws://`。

可以在 CLI 中确认 HTTP 服务器已启动：

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf`包含一个 `[general]` 部分以及每个用户对应的一个部分。

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

- `enabled`全局打开或关闭 ARI。
- `pretty`将 JSON 响应格式化为可读的形式；在生产环境中请关闭。
- 每个用户都是一个具名的部分，使用 `type=user`。
- `read_only=yes`将该用户限制为只读（GET）请求。
- `password_format`可以是 `plain`（密码为明文）或 `crypt`（使用 `mkpasswd -m sha-512` 生成的哈希密码）。
- `permit`、`deny`和`acl`允许对用户进行 IP 限制，规则与 `acl.conf` 相同。

编辑完文件后，重新加载相关模块（`module reload res_ari.so`和`module reload http.so`）或重启 Asterisk。可以通过以下方式验证 ARI 是否在运行：

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

`ari show apps`列出当前已由已连接客户端注册的 Stasis 应用。它在客户端连接之前为空，这正是我们接下来要做的。

### WebSocket 事件 URL

客户端通过打开指向 `/ari/events` 端点的 WebSocket、指定其实现的 Stasis 应用并传递凭证来订阅事件流：

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

查询参数如下：

- `app`——你的 Stasis 应用名称。这与在 dialplan 中的 `Stasis()` 调用使用的名称相同。可以传递多个用逗号分隔的名称。
- `api_key`——凭证，形式为 `username:password` ，对应 `ari.conf` 中的用户。
- `subscribeAll`——可选布尔值（默认 `false`）；当 `true` 时，应用会接收所有事件，而不仅限于其拥有的资源的事件。

相同的 `user:pass` 凭证在 REST 调用中作为 HTTP Basic 认证使用（或同样作为 `api_key` 查询参数附加）。

## Stasis：将通道交给您的应用程序

The bridge between the dialplan and ARI is the **`Stasis()`** dialplan application (the underlying framework is also called Stasis). When a channel reaches `Stasis(appname[,args])`, Asterisk hands that channel to the ARI application registered under `appname` and stops executing the dialplan for it. Control now belongs to your code.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

When the channel enters the application, every connected client subscribed to `hello` receives a **`StasisStart`** event over the WebSocket, carrying the full channel object (its ID, name, caller ID, state, and any arguments passed to `Stasis()`). This is your cue to start controlling the channel.

When the channel leaves the application — because your code moved it back to the dialplan with `continueInDialplan`, or because it was hung up — you receive a **`StasisEnd`** event. After `Stasis()` returns to the dialplan it sets the `STASISSTATUS` channel variable (`SUCCESS` or `FAILED`), so the dialplan can branch on the outcome.

## The ARI resource model

ARI exposes Asterisk's internals as a small set of REST resources. Each resource lives under `/ari/<resource>` and is manipulated with standard HTTP methods. The most important ones:

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | 单个通话腿 | originate, answer, play, record, hangup |
| **bridges** | 将通道连接在一起的混音点 | create, add/remove channels, play to the bridge |
| **playbacks** | 正在进行的媒体播放 | get status, stop, pause/unpause |
| **recordings** | 实时和已存储的录音 | start, stop, list stored, delete |
| **endpoints** | 已配置的对等体 (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | 自定义设备状态 | list, get, set, delete |

Some concrete REST calls (paths shown with the `/ari` prefix that appears on the wire):

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

The `media` parameter on a `play` request takes a media URI. The most common form is a `sound:` URI naming a built-in sound, e.g. `sound:hello-world` or `sound:tt-monkeys`. When the audio finishes, Asterisk emits a `PlaybackFinished` event for that playback ID, which is how your application knows it can move on.

Channels and bridges are the two building blocks you combine to make call flows. To connect two callers, for instance, you originate or accept two channels, create a `mixing` bridge with `POST /ari/bridges`, and add both channels to it with `POST /ari/bridges/{bridgeId}/addChannel`. To build a conference, you simply keep adding channels to the same bridge.

## 一个完整示例：最小的 Stasis 应用

让我们构建最小的实用 ARI 应用。当拨打任何分机时，呼叫会进入我们的 Stasis 应用，应用接听电话，播放经典的 `hello-world` 提示音，然后挂断。

### dialplan

在 `extensions.conf` 中，将通道发送到 Stasis：

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

应用名称 `hello` 与我们连接时使用的 `app=hello` 相匹配。

### Python 客户端

此客户端使用两个广为人知的库：用于 REST 调用的 `requests` 和用于事件流的 `websocket-client`。使用 `pip install requests websocket-client` 安装它们。

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

运行脚本，然后从已注册的 endpoint 拨打任意号码。你应该听到 “Hello, world”，随后呼叫被释放。在 Asterisk 控制台上，`ari show apps` 现在会列出 `hello` ，而客户端保持连接状态。

下面的流程值得追踪一次：

1. dialplan 运行 `Stasis(hello)`；Asterisk 将通道交给我们的应用并发送一个 `StasisStart` 事件。  
2. 我们接听通道，然后让 Asterisk 播放 `sound:hello-world`。Asterisk 返回一个 `Playback` 对象，我们记住其 `id` 。  
3. 当音频播放结束时，Asterisk 发送 `PlaybackFinished`，其中包含该播放的 `id`；我们查找通道并将其挂断。  
4. 挂断导致通道离开 Stasis，产生一个 `StasisEnd` 事件。

> **关于客户端库的说明。** 有一个更高级的包装器 `ari-py` （`ari` 包），但它已不再维护，且是为较早的 Python 版本和 Swagger 工具编写的。对于 Asterisk 22 的新项目，建议使用上面展示的显式 `requests` + WebSocket 方式，或在需要并发时使用 asyncio 库如 `asyncari`。原始方式让你更贴近实际的 REST 调用和事件，这正是学习 ARI 时所需要的。

## externalMedia: the door to AI and voicebots

The resources above let you play and record *files*. But modern voice applications — speech-to-text transcription, AI voicebots, real-time analytics — need the *live audio stream* of a call delivered to an external process, and they need to inject audio back.

ARI provides this through the **`externalMedia` channel**. A `POST /ari/channels/externalMedia` request creates a special channel that, instead of talking to a phone, streams the call's RTP media to (and from) an external host. You bridge this channel with the caller's channel, and now your external program is in the audio path: it receives the caller's audio as RTP and can send synthesized audio back.

The request requires only:

- `app` — the Stasis application that owns the new channel.
- `format` — the audio format, e.g. `ulaw` or `slin16`.

`external_host` (the `host:port` of your media application) is optional in the schema — it may be empty for a WebSocket-server-style connection — but for a classic RTP voicebot you will supply it. The `encapsulation` parameter defaults to `rtp` and `transport` to `udp`, which is exactly what you want for a streaming media endpoint.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

This single feature is what turns Asterisk into a front-end for AI: the telephone network terminates on Asterisk, ARI orchestrates the call, and `externalMedia` pipes the audio to a speech/AI engine and back. This is the mechanism on which AI services and voicebots are built.

## Summary

ARI 是在 Asterisk 22 上构建电话应用的现代、推荐的接口。它将工作清晰地分离：Asterisk 负责媒体引擎，而你的应用——通过 HTTP 上的 JSON 和 WebSocket——提供呼叫控制逻辑。你可以通过`http.conf`（内置的 8088 端口网页服务器）和`ari.conf`（打开 ARI 并定义用户）来启用它。

`Stasis()` dialplan 应用将通道交给你的应用，当通道进入时触发`StasisStart`，离开时触发`StasisEnd`。此后，你可以操作一小组 REST 资源——channels、bridges、playbacks、recordings、endpoints 和 device states——来接听、播放、录音、桥接以及挂断。

我们构建了一个最小的 Python Stasis 应用，它接听来电、播放提示音并挂断，并且我们看到`externalMedia`通道将实时 RTP 流式传输到外部程序——这为 AI 和语音机器人集成奠定了基础。

## 测验

1. ARI 是在 Asterisk 的哪个版本中引入的？
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. 在 ARI 模型中，Asterisk 充当媒体引擎，而外部应用提供呼叫控制逻辑。
   - A. 正确
   - B. 错误
3. ARI 同时使用两种传输方式。哪一对是正确的？
   - A. 用于发送命令的 REST/HTTP API 与用于接收事件的 WebSocket 流
   - B. TCP 行协议和 stdin/stdout 脚本
   - C. SNMP 和 SMTP
   - D. 两个独立的 UDP 套接字
4. 必须设置哪两个配置文件才能启用 ARI？
   - A. `manager.conf` and `agi.conf`
   - B. `http.conf` and `ari.conf`
   - C. `sip.conf` and `rtp.conf`
   - D. `modules.conf` and `cdr.conf`
5. Asterisk HTTP 服务器（因此也是 ARI）的常规 TCP 端口是 ____。
6. 哪个 dialplan 应用将通道交给 ARI 应用？
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. 当通道进入 Stasis 应用时，哪个事件会发送给已连接的客户端？
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. 哪个 ARI 请求会创建一个混音点，以便将两个或更多通道合并在一起？
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. 要在通道上播放内置提示音，哪个事件告诉您的应用音频已结束，从而可以继续？
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. `externalMedia`通道主要用于：
    - A. 将通话录制到本地 WAV 文件
    - B. 将通话的实时音频（RTP）流式传输到外部应用，例如 AI/语音引擎
    - C. 注册一个 PJSIP 端点
    - D. 重新加载 dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
