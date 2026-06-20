# WebRTC with Asterisk

WebRTC（Web 实时通信）让网页浏览器能够在无需插件和外部软电话的情况下拨打和接收电话——只需 JavaScript、麦克风以及到 Asterisk 的安全连接。自 Asterisk 11 起，Asterisk 已能够充当 WebRTC 服务器；自 PJSIP 栈（`res_pjsip`）在 Asterisk 12 中引入后，它成为推荐的实现方式；在 Asterisk 22 中，配置已归结为少数几个易于理解的选项。本章展示如何将 PJSIP 端点转换为浏览器电话，安全媒体路径的工作原理，以及何时应使用 Asterisk 内置的 WebRTC 支持而不是专用网关。

本章的所有内容均已在本书的 Asterisk 22 实验中验证；所示配置与 `lab/asterisk/etc` 中的相同。

## Objectives

By the end of this chapter, you should be able to:

- Explain what WebRTC adds to Asterisk and when to use it
- Describe how WebRTC media security (DTLS-SRTP) and ICE differ from plain SIP
- Enable the Asterisk HTTP server and the secure WebSocket (`wss`) endpoint
- Configure a `wss` PJSIP transport and a WebRTC endpoint with `webrtc=yes`
- Connect a browser softphone (SIP.js) and place a call
- Decide between Asterisk-native WebRTC and a media gateway such as Janus

## Why WebRTC with Asterisk

A WebRTC endpoint is, from Asterisk's point of view, just another PJSIP endpoint.
What changes is *how* the browser reaches it and how media is secured. Typical
uses include:

- **Click-to-call** on a website — a visitor calls a queue or an extension from a
  web page.
- **Web-based agents** — a contact-center agent works entirely in the browser, no
  desktop softphone to install or update.
- **Embedded calling** in your own web application — for example, the SipPulse web
  softphone talking to Asterisk.
- **Zero-install internal phones** — staff use a browser tab instead of a hardware
  phone or installed client.

The big advantage is reach: every modern browser already speaks WebRTC. The cost
is that WebRTC is strict — it *requires* encrypted media and a secure transport,
so there is more to configure than a plain UDP SIP phone.

## WebRTC 与普通 SIP 的区别

普通的 SIP 电话通过 UDP/TCP 进行信令，通常使用普通 RTP 传输音频。WebRTC 浏览器客户端在三个重要方面有所不同，Asterisk 必须对应每一点：

- **信令通过 WebSocket 传输。** 浏览器不再使用 UDP 5060 端口的 SIP，而是打开一个安全的 WebSocket（`wss://`）连接到 Asterisk 内置的 HTTP 服务器。SIP 消息在该 WebSocket 内部传递。
- **媒体始终使用 DTLS‑SRTP 加密。** 浏览器不接受普通 RTP。双方进行 DTLS 握手（通过 SDP 中交换的证书指纹进行认证），并从中派生 SRTP 密钥。
- **连接性通过 ICE 协商。** 与假设可达的 IP 和端口不同，双方会收集候选地址（主机、STUN 反射、TURN 中继），并对其进行探测直至找到可用的。RTP 和 RTCP 通常在单一端口上复用（`rtcp_mux`）。

好消息是：在 Asterisk 22 中，只需使用一个端点选项`webrtc=yes`即可开启上述全部功能，并使用合理的默认值。我们将看到它具体设置了哪些参数。

## Step 1 — the HTTP server and the WebSocket

WebRTC signaling is served by Asterisk's built-in HTTP server (`res_http_websocket`
exposes the `/ws` path on it). Browsers require a *secure* WebSocket, so we enable
TLS. Edit `http.conf`:

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

Reload (`module reload res_http_websocket` or restart) and confirm:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

The browser will connect to `wss://your-asterisk:8089/ws`.

### About the certificate

The TLS certificate here secures the *WebSocket* (the signaling channel). In a lab
a self-signed certificate is fine — you accept it once in the browser. In
production use a real certificate (for example Let's Encrypt) whose name matches
the host the browser connects to, otherwise the browser will refuse the WebSocket.

For the lab, `lab/make-certs.sh` generates a self-signed certificate with
`CN=localhost` (plus `localhost`/`127.0.0.1` SANs) and writes it to
`asterisk/etc/keys/`. For a public deployment, obtain a real certificate instead — for
example with Let's Encrypt:

```
certbot certonly --standalone -d voip.example.com
```

Then point `http.conf` at the issued files and reload `res_http_websocket`:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Make sure the certificate name matches the host the browser connects to, and renew it
(certbot's timer does this automatically) before it expires, or the WebSocket will fail.

This certificate is **not** the same as the DTLS certificate used to encrypt the
media — Asterisk generates that one automatically, as we will see.

## 第2步 — WSS 传输

PJSIP 需要一种类型为 `wss` 的传输。将其添加到 `pjsip.conf`：

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

不要被显示在 `wss` 传输上的 `0.0.0.0:5060` 所误导——WebSocket **不** 在 5060 端口提供服务。WebRTC 信令由您在第 1 步中配置的 HTTP 服务器提供（`wss` 使用的端口为 8089）。PJSIP `wss` 传输是对 `res_http_websocket` 的薄层封装，因此为其打印的 `bind` 地址仅是表面信息，可以忽略；真正重要的端口是 `tlsbindaddr`，位于 `http.conf`。

## 第三步 — WebRTC 端点

现在是端点本身。关键是 `webrtc=yes`：

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
auth_type=digest
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` 是一个便利开关。它相当于手动设置所有 WebRTC 所需的选项。你可以确认它到底打开了哪些：

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

阅读该输出：

- `media_encryption: dtls` 和 `dtls_auto_generate_cert: Yes` — 媒体使用 DTLS‑SRTP，且 Asterisk 自动生成 DTLS 证书，因此你 **不需要** 自行创建。指纹在 SDP（`SHA-256`）中公布。
- `ice_support: true` — Asterisk 收集并协商 ICE 候选。
- `rtcp_mux: true` — RTP 和 RTCP 共享同一个端口，符合浏览器的期望。
- `use_avpf: true` — AVPF RTP 配置文件（反馈），WebRTC 所必需。

`allow=opus` 是推荐的选择 — Opus 是浏览器偏好的 codec。Asterisk 22 在核心中提供 Opus *直通*（`res_format_attr_opus`模块），足以在两个支持 Opus 的链路之间转发 Opus 而无需重新编码。将 Opus *转码* 为其他 codec 需要单独的 `codec_opus`模块，官方 WebRTC 指南将其列为可选但强烈推荐，并且需要在基础构建之上安装；请参阅《Designing a VoIP network》中的 codec 讨论。保留 `ulaw` 作为桥接到无法使用 Opus 的非 WebRTC 链路的后备方案。

## Step 4 — ICE, STUN and TURN

在平坦的局域网中，使用带有主机候选的 ICE 已足够，无需其他操作。跨越互联网时，通常会添加一个 STUN 服务器，以便 Asterisk 和浏览器能够发现它们的公网地址，并在直接媒体不可用的情况下（对称 NAT、受限防火墙）使用 TURN 服务器。将 Asterisk 指向它们在`rtp.conf`中：

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

浏览器在 JavaScript 中使用自己的 ICE 服务器（`RTCPeerConnection` `iceServers` 列表）进行配置。对于纯内部部署，可以完全跳过 STUN/TURN。

`turnaddr`接受一个可选端口（默认`3478`）；`turnusername`和`turnpassword`对中继进行身份验证。STUN 仅帮助对等方*发现*其公网地址——当双方都位于对称 NAT 或受限防火墙后面时，直接媒体不可行，只有 TURN 中继才能使音频流通。

**生产环境建议：** 公共 STUN 服务器（例如 Google 的）用于地址发现是可以的，但**不要**依赖公共 TURN 进行真实流量——TURN 中继会转发所有媒体，因此应由您自行控制。运行您自己的 [coturn](https://github.com/coturn/coturn) 服务器。一个带有长期凭证的最小`/etc/turnserver.conf` 如下所示：

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

然后在`rtp.conf`中将 Asterisk 指向它：

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

在浏览器的`iceServers`列表中提供相同的 TURN 服务器，以便两端都能进行中继。对于在移动网络或企业防火墙后面的用户的生产环境，部署自托管的 coturn 实际上是必需的。

## 第5步 — 浏览器客户端

任何 WebRTC SIP 库都可以；两种广泛使用的是 **SIP.js** 和 **JsSIP**。实验包含了一个位于 `lab/webrtc/index.html` 的最小化 SIP.js 软电话。关键部分是传输 URL 和凭证：

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

- **安全上下文。** `getUserMedia`（麦克风访问）仅在 `https://` 页面或 `http://localhost` 上工作。生产环境请通过 HTTPS 提供页面。
- **一次性接受证书。** 使用实验自签名证书时，先在同一浏览器中访问 `https://your-asterisk:8089/ws` 并接受警告，否则 WebSocket 将静默失败。

SipPulse Web 软电话是基于这些相同原语构建的生产级参考客户端。

## 验证 WebRTC 呼叫

在浏览器注册后，`pjsip show contacts`显示动态联系信息，呼叫会点亮通道：

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

如果音频是单向的或根本没有，几乎总是 ICE 或证书的问题——请参见下面的故障排除。

## Asterisk WebRTC 与媒体网关

Asterisk 可以直接终止 WebRTC，但它并不总是最佳工具：

- **Use Asterisk-native WebRTC** 当浏览器在你的 PBX 上充当 *phone* —— 一个坐席、内部分机、或点击拨号后进入你的 dialplan 的呼叫。浏览器只是另一个 endpoint，所有功能（queues、voicemail、IVR）都能正常工作。
- **Use a dedicated gateway (e.g. Janus)** 当你需要在不受 call control 限制的情况下扩展大量浏览器会话、为大型会议/流媒体进行 selective forwarding，或将媒体平面与 PBX 分离时。网关将 WebRTC 桥接到普通 SIP，Asterisk 随后看到的是普通的 SIP leg。

许多实际系统会同时使用两者：Asterisk 负责 call control，网关负责浏览器侧的媒体扩展。（这就是 SipPulse 自己平台背后的架构。）

## 故障排除

- **WebSocket won't connect:** 浏览器拒绝了 TLS 证书。直接打开 `https://host:8089/ws` 并接受，或安装受信任的证书。  
- **Registers but no audio:** ICE 失败 — 添加 STUN，如果跨 NAT 还需添加 TURN。检查 `pjsip set logger on` 并查看 SDP 候选。  
- **One-way audio:** 通常是一侧的 NAT/ICE，或编解码器没有共同匹配 — 确保 `allow=opus,ulaw`。  
- **Call drops at answer:** DTLS 握手失败；确认 `dtls_auto_generate_cert` 为 `Yes` 且系统时钟正确（证书对时间敏感）。

## 实验

1. 运行 `./lab.sh up`, 然后 `bash lab/make-certs.sh` 并重启 Asterisk。  
2. 提供 `lab/webrtc/index.html`（来自 `lab/webrtc` 的 `python3 -m http.server`）并打开它；在 `https://localhost:8089/ws` 接受证书。  
3. 以 `webrtc-1000` 注册并呼叫 `600`（回声测试）——你应该能听到自己的声音。  
4. 在注册为 `6001` 的 SipPulse Softphone 上，拨打 `1000` 使浏览器响铃。  
5. 检查协商过程： `pjsip set logger on`, 发起通话，并在 SDP 中找到 DTLS 指纹和 ICE 候选。

## Summary

WebRTC 将浏览器转变为一等的 Asterisk 端点。实现方法很简短但严格：启用带 TLS 的 HTTP 服务器，以便浏览器能够打开安全的 WebSocket，添加一个 `wss` PJSIP 传输，并在端点上设置 `webrtc=yes` —— 这会开启 DTLS‑SRTP（使用自动生成的证书）、ICE、RTP/RTCP 多路复用以及 AVPF 配置文件。跨越 NAT 时添加 STUN/TURN，使用 HTTPS 提供页面，并将 SIP.js（或 JsSIP）客户端指向 `wss://asterisk:8089/ws`。对于 PBX 上的浏览器电话，原生 Asterisk WebRTC 是最简便的路径；对于大规模媒体，则将其与网关配合使用。

## Quiz

1. Which transport does a WebRTC browser client use to carry SIP signaling to
   Asterisk?
   - A. Plain UDP on port 5060
   - B. A secure WebSocket (`wss://`) to Asterisk's HTTP server
   - C. TLS on port 5061
   - D. A raw TCP socket on port 8088

2. WebRTC media between the browser and Asterisk is encrypted using which mechanism?
   - A. SDES-SRTP (keys exchanged in the SDP)
   - B. DTLS-SRTP (keys derived from a DTLS handshake)
   - C. IPsec
   - D. Plain RTP — WebRTC does not encrypt media

3. True or false: when you set `webrtc=yes`, you must manually generate and install
   the DTLS certificate used to encrypt the media.

4. On which port does the lab's Asterisk HTTP server expose the **secure** WebSocket
   for WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Which of the following does `webrtc=yes` turn on by default? (Choose all that
   apply.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Fill in the blank: WebRTC negotiates connectivity by having both sides gather and
   probe candidate addresses (host, STUN-reflexive, TURN-relayed) using the
   ________ framework.

7. In `rtp.conf`, which two settings point Asterisk at an external server so it can
   discover its public address and relay media when direct paths fail? (Choose all
   that apply.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. The URL path that Asterisk's `res_http_websocket` exposes for WebRTC signaling is
   ________.

9. According to the chapter, when should you reach for a dedicated media gateway
   (such as Janus) instead of Asterisk-native WebRTC?
   - A. Whenever any browser needs to make a call
   - B. When you must scale many browser media sessions independently of call
     control, do selective forwarding for large conferences, or keep the media plane
     separate from the PBX
   - C. Only when the browser does not support DTLS
   - D. When you want voicemail and IVR to work for the browser endpoint

10. True or false: `getUserMedia` (microphone access) works on any `http://` page, so
    serving the browser softphone over HTTPS is optional.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
