# WebRTC with Asterisk

WebRTC (Web Real-Time Communication) 让 Web 浏览器无需插件或外部 softphone 即可拨打和接听电话——只需要 JavaScript、麦克风以及与 Asterisk 的安全连接。自 Asterisk 11 起，Asterisk 就能够充当 WebRTC 服务器，而自 Asterisk 12 引入 PJSIP 栈（`res_pjsip`）以来，这已成为推荐的实现方式；在 Asterisk 22 中，配置已简化为少数几个易于理解的选项。本章将展示如何将 PJSIP endpoint 转换为浏览器电话，安全媒体路径的工作原理，以及何时应该选择 Asterisk 内置的 WebRTC 支持，何时应该选择专用的网关。

本章中的所有内容均已针对本书的 Asterisk 22 实验环境进行了验证；所展示的配置与 `lab/asterisk/etc` 中的配置相同。

## 目标

读完本章后，您应该能够：

- 解释 WebRTC 为 Asterisk 增加了什么功能以及何时使用它
- 描述 WebRTC 媒体安全 (DTLS-SRTP) 和 ICE 与普通 SIP 有何不同
- 启用 Asterisk HTTP 服务器和安全 WebSocket (`wss`) endpoint
- 使用 `webrtc=yes` 配置 `wss` PJSIP transport 和 WebRTC endpoint
- 连接浏览器 softphone (SIP.js) 并拨打电话
- 在 Asterisk 原生 WebRTC 和诸如 Janus 之类的媒体网关之间做出选择

## 为什么要在 Asterisk 中使用 WebRTC

从 Asterisk 的角度来看，WebRTC endpoint 只是另一个 PJSIP endpoint。不同之处在于浏览器如何连接到它以及如何保护媒体安全。典型的应用场景包括：

- 网站上的 **Click-to-call**（点击通话）——访客从网页拨打队列或 extension。
- **基于 Web 的座席**——联络中心座席完全在浏览器中工作，无需安装或更新桌面 softphone。
- 在您自己的 Web 应用程序中 **嵌入呼叫功能**——例如，SipPulse Web softphone 与 Asterisk 通信。
- **零安装内部电话**——员工使用浏览器标签页代替硬件电话或已安装的客户端。

最大的优势是覆盖范围：每种现代浏览器都已经支持 WebRTC。代价是 WebRTC 非常严格——它 *要求* 加密媒体和安全传输，因此比普通的 UDP SIP 电话需要更多的配置。

## WebRTC 与普通 SIP 的区别

普通的 SIP 电话通过 UDP/TCP 进行信令传输，通常以普通 RTP 格式承载音频。WebRTC 浏览器客户端在三个重要方面有所不同，Asterisk 必须匹配每一个方面：

- **信令通过 WebSocket 传输。** 浏览器不是通过 UDP 端口 5060 进行 SIP 通信，而是向 Asterisk 的内置 HTTP 服务器打开一个安全 WebSocket (`wss://`)。SIP 消息在 WebSocket 内部传输。
- **媒体始终使用 DTLS-SRTP 加密。** 浏览器拒绝普通 RTP。双方执行 DTLS 握手（通过 SDP 中交换的证书指纹进行身份验证）并从中派生 SRTP 密钥。
- **连接通过 ICE 进行协商。** 双方不是假设一个可达的 IP 和端口，而是收集候选地址（主机、STUN 反射、TURN 中继）并进行探测，直到找到一个可用的地址。RTP 和 RTCP 通常在单个端口上进行多路复用 (`rtcp_mux`)。

好消息是：在 Asterisk 22 中，一个单一的 endpoint 选项 `webrtc=yes` 可以通过合理的默认设置开启所有这些功能。我们将确切地看到它设置了什么。

## 第 1 步 — HTTP 服务器和 WebSocket

WebRTC 信令由 Asterisk 的内置 HTTP 服务器提供服务（`res_http_websocket` 在其上公开了 `/ws` 路径）。浏览器需要 *安全* 的 WebSocket，因此我们启用 TLS。编辑 `http.conf`：

```
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088

; TLS / WSS for WebRTC. Browsers require a secure WebSocket (wss://).
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.crt
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

重新加载（`module reload res_http_websocket` 或重启）并确认：

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

浏览器将连接到 `wss://your-asterisk:8089/ws`。

### 关于证书

此处的 TLS 证书用于保护 *WebSocket*（信令通道）。在实验环境中，自签名证书即可——您只需在浏览器中接受一次。在生产环境中，请使用真实的证书（例如 Let's Encrypt），其名称必须与浏览器连接的主机名匹配，否则浏览器将拒绝 WebSocket。

> **[第二版注]** 实验环境附带 `lab/make-certs.sh`，它使用 `CN=localhost` 生成自签名证书。对于公共部署，请记录 Let's Encrypt 的流程，并将 `tlscertfile`/`tlsprivatekey` 指向颁发的证书文件。

此证书 **不是** 用于加密媒体的 DTLS 证书——正如我们将看到的，Asterisk 会自动生成该证书。

## 第 2 步 — WSS transport

PJSIP 需要一个类型为 `wss` 的 transport。将其添加到 `pjsip.conf`：

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

验证它已加载：

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

> **[第二版注]** `wss` transport 会打印一个 `0.0.0.0:5060` 绑定地址，即使实际的 WebSocket 是由端口 8089 上的 HTTP 服务器提供的。这是预期的：`wss` transport 只是 `res_http_websocket` 之上的一个薄层；其上的 `bind` 行实际上是装饰性的。值得在最终文本中说明，以免读者对端口感到困惑。

## 第 3 步 — WebRTC endpoint

现在是 endpoint 本身。关键是 `webrtc=yes`：

```
[webrtc-1000]
type=endpoint
context=internal
disallow=all
allow=opus,ulaw
webrtc=yes
transport=transport-wss
aors=webrtc-1000
auth=webrtc-1000

[webrtc-1000]
type=auth
auth_type=userpass
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` 是一个便捷开关。它等同于手动设置所有 WebRTC 所需的选项。您可以确认它确切开启了哪些功能：

```
*CLI> pjsip show endpoint webrtc-1000
 dtls_auto_generate_cert            : Yes
 dtls_fingerprint                   : SHA-256
 dtls_setup                         : actpass
 ice_support                        : true
 media_encryption                   : dtls
 rtcp_mux                           : true
 use_avpf                           : true
 webrtc                             : yes
```

读取该输出：

- `media_encryption: dtls` 和 `dtls_auto_generate_cert: Yes`——媒体是 DTLS-SRTP，且 Asterisk 会自动生成 DTLS 证书，因此您 **无需** 自己创建。指纹在 SDP (`SHA-256`) 中通告。
- `ice_support: true`——Asterisk 收集并协商 ICE 候选地址。
- `rtcp_mux: true`——RTP 和 RTCP 共享一个端口，正如浏览器所预期的那样。
- `use_avpf: true`——AVPF RTP 配置文件（反馈），这是 WebRTC 所必需的。

建议使用 `allow=opus`——Opus 是浏览器首选的 codec。Asterisk 22 在核心中内置了 Opus *透传*（`res_format_attr_opus` 模块），这足以在两个支持 Opus 的链路之间中继 Opus，而无需重新编码。将 Opus *转码* 为其他 codec 需要单独的 `codec_opus` 模块，官方 WebRTC 指南将其列为可选但强烈推荐，您可以在基础构建之上安装它；请参阅《设计 VoIP 网络》中的 codec 讨论。保留 `ulaw` 作为桥接到无法使用 Opus 的非 WebRTC 链路的后备方案。

## 第 4 步 — ICE、STUN 和 TURN

在扁平的局域网中，带有主机候选地址的 ICE 就足够了，不需要其他任何东西。在互联网上，您通常需要添加一个 STUN 服务器，以便 Asterisk 和浏览器可以发现它们的公网地址，并添加一个 TURN 服务器，用于无法实现直接媒体连接的情况（对称 NAT、限制性防火墙）。在 `rtp.conf` 中将 Asterisk 指向它们：

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

浏览器在 JavaScript 中配置了自己的 ICE 服务器（`RTCPeerConnection` `iceServers` 列表）。对于纯内部部署，您可以完全跳过 STUN/TURN。

> **[第二版注]** 验证是否建议在生产环境中使用自托管的 coturn（大多数实际部署需要 TURN）。如果是，请添加一个简短的 coturn 配置示例。

## 第 5 步 — 浏览器客户端

任何 WebRTC SIP 库都可以使用；两个广泛使用的库是 **SIP.js** 和 **JsSIP**。实验环境在 `lab/webrtc/index.html` 包含了一个最小化的 SIP.js softphone。关键部分是传输 URL 和凭据：

```javascript
const ua = new SIP.UserAgent({
  uri: SIP.UserAgent.makeURI('sip:webrtc-1000@your-asterisk'),
  transportOptions: { server: 'wss://your-asterisk:8089/ws' },
  authorizationUsername: 'webrtc-1000',
  authorizationPassword: 'Lab-webrtc-secret',
});
await ua.start();
await new SIP.Registerer(ua).register();
// place a call to the echo test
const inviter = new SIP.Inviter(ua, SIP.UserAgent.makeURI('sip:600@your-asterisk'));
await inviter.invite();
```

需要记住的两个浏览器现实：

- **安全上下文。** `getUserMedia`（麦克风访问）仅在 `https://` 页面或 `http://localhost` 上有效。在生产环境中，请通过 HTTPS 提供页面。
- **接受一次证书。** 使用自签名实验证书时，请先在同一浏览器中访问 `https://your-asterisk:8089/ws` 并接受警告，否则 WebSocket 将静默失败。

SipPulse Web softphone 是一个基于这些相同原语构建的生产级参考客户端。

## 验证 WebRTC 呼叫

浏览器注册后，`pjsip show contacts` 会显示动态联系人，呼叫会点亮通道：

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

如果音频是单向的或缺失，通常是 ICE 或证书问题——请参阅下方的故障排除。

## Asterisk WebRTC 与媒体网关

Asterisk 可以直接终止 WebRTC，但这并不总是正确的工具：

- **使用 Asterisk 原生 WebRTC**：当浏览器是您 PBX 上的 *电话* 时——例如座席、内部 extension、进入 dialplan 的点击通话。浏览器只是另一个 endpoint，所有功能（队列、voicemail、IVR）都能正常工作。
- **使用专用网关（例如 Janus）**：当您需要独立于呼叫控制扩展许多浏览器会话、为大型会议/流媒体进行选择性转发，或保持媒体平面与 PBX 分离时。网关将 WebRTC 桥接到普通 SIP，然后 Asterisk 看到的是一个普通的 SIP 链路。

许多实际系统结合了两者：Asterisk 用于呼叫控制，网关用于浏览器端的媒体扩展。（这就是 SipPulse 自身栈背后的架构。）

## 故障排除

- **WebSocket 无法连接：** 浏览器拒绝了 TLS 证书。直接打开 `https://host:8089/ws` 并接受它，或安装受信任的证书。
- **已注册但没有音频：** ICE 失败——添加 STUN，如果跨越 NAT 则添加 TURN。检查 `pjsip set logger on` 并查看 SDP 候选地址。
- **单向音频：** 通常是一侧的 NAT/ICE 问题，或者是没有共同匹配的 codec——确保 `allow=opus,ulaw`。
- **应答时呼叫掉线：** DTLS 握手失败；确认 `dtls_auto_generate_cert` 为 `Yes` 且系统时钟正确（证书对时间敏感）。

## 实验

1. 运行 `./lab.sh up`，然后运行 `bash lab/make-certs.sh` 并重启 Asterisk。
2. 提供 `lab/webrtc/index.html`（`lab/webrtc` 中的 `python3 -m http.server`）并打开它；在 `https://localhost:8089/ws` 接受证书。
3. 以 `webrtc-1000` 身份注册并拨打 `600`（回声测试）——您应该能听到自己的声音。
4. 从注册为 `6001` 的 SipPulse Softphone 拨打 `1000` 以呼叫浏览器。
5. 检查协商过程：`pjsip set logger on`，拨打电话，并在 SDP 中查找 DTLS 指纹和 ICE 候选地址。

## 总结

WebRTC 将浏览器变成了 Asterisk 的一等 endpoint。方法很简单但很严格：启用带有 TLS 的 HTTP 服务器以便浏览器可以打开安全 WebSocket，添加一个 `wss` PJSIP transport，并在 endpoint 上设置 `webrtc=yes`——这将开启 DTLS-SRTP（使用自动生成的证书）、ICE、RTP/RTCP 多路复用和 AVPF 配置文件。跨越 NAT 时添加 STUN/TURN，通过 HTTPS 提供页面，并将 SIP.js（或 JsSIP）客户端指向 `wss://asterisk:8089/ws`。对于 PBX 上的浏览器电话，Asterisk 原生 WebRTC 是最简单的路径；对于大规模媒体，请将其与网关配对。

## 测验

1. WebRTC 浏览器客户端使用哪种传输方式将 SIP 信令传送到 Asterisk？
   - A. 端口 5060 上的普通 UDP
   - B. 到 Asterisk HTTP 服务器的安全 WebSocket (`wss://`)
   - C. 端口 5061 上的 TLS
   - D. 端口 8088 上的原始 TCP 套接字

2. 浏览器和 Asterisk 之间的 WebRTC 媒体使用哪种机制加密？
   - A. SDES-SRTP（在 SDP 中交换密钥）
   - B. DTLS-SRTP（从 DTLS 握手中派生密钥）
   - C. IPsec
   - D. 普通 RTP——WebRTC 不加密媒体

3. 对或错：设置 `webrtc=yes` 时，您必须手动生成并安装用于加密媒体的 DTLS 证书。

4. 实验环境的 Asterisk HTTP 服务器在哪个端口上为 WebRTC 公开 **安全** WebSocket？
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. `webrtc=yes` 默认开启了以下哪些功能？（多选）
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. 填空：WebRTC 通过让双方使用 ________ 框架收集和探测候选地址（主机、STUN 反射、TURN 中继）来协商连接。

7. 在 `rtp.conf` 中，哪两个设置将 Asterisk 指向外部服务器，以便它能够发现其公网地址并在直接路径失败时中继媒体？（多选）
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. Asterisk 的 `res_http_websocket` 为 WebRTC 信令公开的 URL 路径是 ________。

9. 根据本章，何时应该选择专用媒体网关（如 Janus）而不是 Asterisk 原生 WebRTC？
   - A. 任何浏览器需要拨打电话时
   - B. 当您需要独立于呼叫控制扩展许多浏览器媒体会话、为大型会议进行选择性转发，或保持媒体平面与 PBX 分离时
   - C. 仅当浏览器不支持 DTLS 时
   - D. 当您希望 voicemail 和 IVR 对浏览器 endpoint 有效时

10. 对或错：`getUserMedia`（麦克风访问）在任何 `http://` 页面上都有效，因此通过 HTTPS 提供浏览器 softphone 是可选的。

**答案：** 1 — B · 2 — B · 3 — 错（Asterisk 自动生成 DTLS 证书；`dtls_auto_generate_cert: Yes`） · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — 错（需要安全上下文：`getUserMedia` 仅在 `https://` 或 `http://localhost` 上有效）
