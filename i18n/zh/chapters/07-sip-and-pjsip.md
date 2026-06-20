# SIP 与 PJSIP 深入解析

SIP 是协议；PJSIP 是 Asterisk 22 使用该协议的方式。**PJSIP**（`chan_pjsip`，通过 `pjsip.conf` 配置）是 Asterisk 22 LTS 中唯一的 SIP 通道驱动程序。本章涵盖了 SIP 协议的基础知识（这些属于协议层面，且 100% 有效）以及您日常使用的 PJSIP 对象模型和配置。已停用的旧版驱动程序和迁移指南将在*Legacy channels*一章中介绍。

## SIP 协议基础

会话发起协议（Session Initiation Protocol，SIP）是一种类似于 HTTP 和 SMTP 的文本协议，旨在初始化、保持和终止用户之间的交互式通信会话。这些会话可能包括语音、视频、聊天、交互式游戏等。SIP 由 IETF 定义，已成为语音通信的事实标准。理解 SIP 的工作原理非常重要。在 Asterisk 22 上，SIP 配置位于 `pjsip.conf`，这是基于 SIP 的系统中最常编辑的文件之一（仅次于 `extensions.conf`）。

### 操作理论

SIP 是一种信令协议，包含以下组件：用户代理客户端（User Agent Client）、用户代理服务器（User Agent Servers）、SIP 代理（SIP Proxies）和 SIP 网关（SIP Gateways）。下图描绘了这些组件之间的关系。

- UAC (user agent client) – 初始化 SIP 信令的客户端或终端。
- UAS (user agent server) – 响应来自 UAC 的 SIP 信令的服务器。
- UA (user agent) – SIP 终端（包含 UAC 和 UAS 的电话或网关）。
- Proxy Server – 接收来自 UA 的请求，如果特定站点不在其管理范围内，则将其转发给其他 SIP 代理。
- Redirect Server – 接收请求并将其连同目标数据一起发回给 UA，而不是直接将请求转发给目标。
- Location Server – 接收来自 UA 的请求，并使用此信息更新位置数据库。

通常，代理、重定向和位置服务器托管在同一硬件中，并使用同一软件，我们称之为 SIP 代理。SIP 代理负责位置数据库维护、连接建立和会话终止。

![主要的 SIP 组件：用户代理 (UAC/UAS/UA)、注册/代理/重定向服务器以及通往 PSTN 的网关，RTP 媒体流直接在端点之间传输](../images/07-sip-and-pjsip-fig01.png)

#### SIP 注册过程

在电话能够接收呼叫之前，它需要注册到位置数据库。在位置数据库中，IP 地址将与名称绑定。在以下示例中，分机 8500 将绑定到 IP 地址 200.180.1.1。您不一定非要使用电话号码。在 SIP 架构中，注册的分机也可以是 flavio@voip.school。

![SIP 注册：电话发送一个将分机 8500 绑定到其 IP 地址的 REGISTER 请求，注册服务器将联系信息存储在位置数据库中，并回复 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### 代理操作

当作为 SIP 代理运行时，SIP 服务器位于信令的中间，能够进行高级路由和计费。基于实时传输协议（RTP）的媒体流仍然直接在端点之间传输。

![代理操作：SIP 代理保持在信令路径 (INVITE/200 OK) 中，并在位置服务器中查找被叫方，而 RTP 媒体流直接在两个端点之间传输](../images/07-sip-and-pjsip-fig03.png)

#### 重定向操作

在重定向时，SIP 服务器只需向用户代理发送一条消息（例如 302 moved temporarily），然后退出后续消息的路径。在资源使用方面，它非常轻量，但您完全无法控制。重定向有时用于负载均衡设计。

![重定向操作：重定向服务器用携带联系信息的 302 Moved Temporarily 响应 INVITE，然后退出，呼叫者直接向新位置重新发送 INVITE/ACK](../images/07-sip-and-pjsip-fig04.png)

#### Asterisk 如何处理 SIP

重要的是要理解 Asterisk 既不是 SIP 代理也不是 SIP 重定向器。Asterisk 可以执行注册服务器和位置服务器的角色；但是，它只将两个 UAC 连接到自身。因此，Asterisk 被视为背靠背用户代理（B2BUA）。换句话说，它连接两个 SIP 通道，并将它们桥接在一起。Asterisk 具有一种重新邀请（re-invite）机制，可以使 SIP 通道直接相互通话，而不是通过 Asterisk。在 PJSIP 端点上，这由参数 `direct_media` 控制。使用 `direct_media=yes` 时，RTP 流直接从一个端点传输到另一个端点，从而释放服务器资源。

#### direct_media=yes 时的 SIP 操作

![directmedia=yes 时的 SIP 操作：SIP 信令流经 Asterisk，而 RTP 音频直接在两部电话之间传输，从而释放服务器资源](../images/07-sip-and-pjsip-fig05.png)

但是，如果您需要使用 Asterisk 转移或录制呼叫，可以使用参数 `direct_media=no` 强制 RTP 流经 Asterisk 服务器。

#### direct_media=no 时的 SIP 操作

![directmedia=no 时的 SIP 操作：SIP 信令和 RTP 音频都通过 Asterisk 锚定，允许其录制、转码或转移呼叫](../images/07-sip-and-pjsip-fig06.png)

#### SIP 消息

基本的 SIP 消息包括：

- INVITE – 连接建立
- ACK – 确认
- BYE – 连接终止
- CANCEL – 终止未建立的呼叫
- REGISTER – 将 UAC 注册到 SIP 代理
- OPTIONS – 可用于检查可用性
- REFER – 将 SIP 呼叫转移给他人
- SUBSCRIBE – 订阅通知事件
- NOTIFY – 发送通道信息
- INFO – 发送各种消息（例如 DTMF）
- MESSAGE – 发送即时消息

SIP 响应采用文本格式，易于阅读（类似于 HTTP 消息）。最重要的响应包括：

- 1XX – 信息性消息（100–trying, 180–ringing, 183–progress）
- 2XX – 请求成功完成（200 – OK）
- 3XX – 呼叫重定向，请求必须定向到其他地方（302 – moved temporarily, 305 – use proxy）
- 4XX – 错误（403 – Forbidden）
- 5XX – 服务器错误（500 – Internal Server Error; 501 – Not implemented）
- 6XX – 全局失败（606 – Not acceptable）

例如：

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### 会话描述协议 (SDP)

SDP 最初定义在 IETF RFC 2327 中，现已被 RFC 4566 取代。它旨在描述多媒体会话，用于会话公告、会话邀请和其他形式的多媒体会话初始化。SDP 包括：

- 传输协议 (RTP/UDP/IP)
- 媒体类型 (text, audio, video)
- 媒体格式或 codec (H.261 video, g.711 audio 等)
- 接收这些媒体所需的信息 (地址, 端口等)

以下示例是描述两部电话之间呼叫的 SDP 转录。

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### SIP NAT 穿透

网络地址转换（NAT）是大多数网络用于节省 Internet IP 地址的功能。通常，公司会收到一小块 IP 地址，而最终用户在连接到 Internet 时会动态获得一个 IP 地址。NAT 通过将内部地址映射到外部地址来解决寻址问题。它在内存中存储内部到外部地址的映射。此映射在特定时间内有效，之后映射将被丢弃。映射使用 IP:端口对作为内部和外部地址。存在四种 NAT：

- Full Cone
- Restricted Cone
- Port Restricted Cone
- Symmetric

下方的 NAT 理论——四种 NAT 类型、Contact 头部问题、保持连接（keep-alives）以及强制媒体流经服务器——属于协议层面，适用于任何 SIP 实现。您在 Asterisk 22 (PJSIP) 上配置每种行为的方式将在本章后面的 *Nat traversal on res_pjsip* 部分介绍。

#### Full Cone

第一种 NAT，全锥型（Full Cone），表示从外部 IP:端口对到内部 IP:端口对的静态映射。任何外部计算机都可以使用该外部 IP:端口对连接到它。这是在通过过滤器实现的无状态防火墙中的情况。

![Full Cone NAT：内部主机 (10.0.0.1:8000) 被静态映射到外部对 200.180.4.168:1234，因此任何外部计算机都可以向该对发送数据包并到达内部主机](../images/07-sip-and-pjsip-fig11.png)

#### Restricted Cone

在受限锥型（Restricted Cone）场景中，外部 IP:端口对仅在内部计算机向外部地址发送数据时才打开。但是，受限锥型 NAT 会阻止来自不同地址的任何传入数据包。换句话说，内部计算机必须先向外部计算机发送数据，然后才能接收来自该计算机的数据。

#### Port Restricted Cone

端口受限锥型（Port Restricted Cone）防火墙与受限锥型几乎相同。唯一的区别是，现在传入的数据包必须来自与发送数据包完全相同的 IP 和端口。

#### Symmetric

最后一种 NAT 类型称为对称型（Symmetric）。它与前三种不同，因为它对每个外部地址都执行特定的映射。只有特定的外部地址才被允许通过 NAT 映射返回。无法预测 NAT 设备将使用的外部 IP:端口对。其他三种 NAT 类型允许使用外部服务器来发现用于通信的外部 IP 地址。对于对称型 NAT，即使您可以连接到外部服务器，发现的地址也不能用于除此服务器之外的任何其他设备。

![Symmetric NAT：为每个目的地分配不同的外部源端口，因此向一个服务器发现的映射不能被另一个主机重用，这会破坏基于 STUN 的穿透](../images/07-sip-and-pjsip-fig12.png)

#### NAT 防火墙表

下表总结了四种 NAT 类型。

| NAT 类型 | 必须先发送数据 | 能否确定返回数据包的外部 IP:端口 | 是否限制传入数据包到目标 IP:端口 |
| --- | --- | --- | --- |
| Full Cone | 否 | 是 | 否 |
| Restricted Cone | 是 | 是 | 仅 IP |
| Port Restricted Cone | 是 | 是 | 是 |
| Symmetric | 是 | 否 | 是 |

#### NAT 上的 SIP 信令和 RTP

NAT 穿透中的一些最大问题是您必须解决两个问题：SIP 信令和音频（RTP）。大多数单向音频问题都与 NAT 有关。关于 SIP 的一个有趣之处在于，当 UAC 发送数据包时，它会将 IP 地址嵌入到 SIP “Contact” 头部字段中。通常这是一个内部 (RFC1918) 地址；对该数据包的响应无法通过 Internet 路由回 UAC。概念上的修复总是相同的：

- **忽略 Contact/Via 地址，并回复到数据包实际来源的地址。** 这是 RFC 3581 (`rport`) 中定义的行为。在 PJSIP 上是 `force_rport=yes`，而 `rewrite_contact=yes` 会将存储的联系地址重写为源地址。
- **将媒体发送回 RTP 实际到达的地址**（对称 RTP，历史上称为 *comedia*）。在 PJSIP 上是 `rtp_symmetric=yes`。
- **保持 NAT 映射打开。** 如果映射超时，Asterisk 将无法再向 UAC 发送 INVITE —— 电话可以拨打电话但无法接听。发送周期性的 OPTIONS（即 *qualify*）可以保持针孔打开。在 PJSIP 上，这是 AOR 上的 `qualify_frequency=`。

如果用户的 NAT 是对称型的，则无法直接从一个 UAC 向另一个 UAC 发送数据包；在这种情况下，您必须使用 `direct_media=no` 强制 RTP 流经 Asterisk。这些配置适用于大多数情况。可以使用高级技术（如 STUN）来优化流量，这对于全锥型、受限锥型和端口受限锥型以及应用层网关 (ALG) 非常有用。不幸的是，当今大多数防火墙——甚至是家庭 DSL/电缆路由器——都是对称型的，这使得 STUN 无法使用。ALG 本可以解决这个问题，但在大多数情况下它不受支持、未实现或存在错误。

#### NAT 后面的 Asterisk

有时 Asterisk 服务器本身部署在带有 NAT 的防火墙后面——这在云端部署时是非常常见的情况。在这种情况下，需要进行一些额外的配置，以便 Asterisk 在 SIP 和 SDP 头部中通告其 **公共** 地址，而不是其私有地址。

从概念上讲，有三个步骤：

- 将防火墙的 SIP 信令端口（默认 UDP 5060）转发到 Asterisk 服务器。
- 将防火墙的 RTP 媒体端口范围（默认 UDP 10000–20000，在 `rtp.conf` 中设置）转发到 Asterisk 服务器。
- 告诉 Asterisk 其外部地址以及哪个网络是本地网络，以便它知道何时将公共地址替换到头部中。

在 PJSIP 上，后两项映射到 **传输（transport）** 上的 `external_media_address` / `external_signaling_address` 和 `local_net=`，而 RTP 端口范围仍在 `rtp.conf` 中配置：

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

NAT 后面的 Asterisk 服务器的完整 PJSIP 配置将在本章后面的 *Asterisk Server behind NAT* 部分给出。

### SIP 限制

Asterisk 使用传入的 RTP 流来同步传出的流。如果传入流中断（静音抑制），保持音乐（music-on-hold）将会被切断。换句话说，您不应在带有 Asterisk 的电话或提供商中使用静音抑制。

## PJSIP：SIP 通道

PJSIP 是 Asterisk 中的 SIP 通道。它首次在 Asterisk 12 中引入，经过多年的开发，成为默认且推荐的 SIP 通道，并且在 Asterisk 22（当前的 LTS 版本）中，它是唯一的 SIP 通道驱动程序。PJSIP 基于 Teluu 的项目 pjproject。pjproject 栈被许多软电话和商业 SIP 实现所采用。它是一个通用且成熟的 SIP 栈。

### 为什么要使用 PJSIP

PJSIP 是对 Asterisk 如何使用 SIP 的彻底重新设计，了解使其成为标准的特性是值得的。

#### 特性

该通道支持许多特性，其中一些值得在此提及：

- 多重注册：您可以使用连接到同一记录地址（Address of Record）的多部电话。换句话说，您可以将两部电话连接到同一个端点。
- 友好的应用程序接口 (API)：API 是模块化的且易于扩展，由许多小的协作模块构建，而不是一个大的代码块。
- 多重传输：使用 PJSIP 时，您可以监听多个地址、端口和传输协议。您不仅限于为所有设备使用单个绑定地址。PJSIP 非常灵活。

#### 关于配置的说明

PJSIP 配置更加冗长：它需要多一点的努力和更多的配置行，因为每个设备由几个相关的对象描述，而不是一个对等体（peer）块。这种额外的结构赋予了 PJSIP 灵活性，而配置向导（稍后介绍）使日常配置保持简短。

### PJSIP 模块

PJSIP 通道由下面描述的许多模块实现：

#### res_pjsip

这是 PJSIP 的基础层和主要模块。它负责一些主要服务。

#### res_pjsip_session

该模块负责媒体会话、会话描述协议处理和一些插件。

#### res_pjsip_messaging

处理 SIP 消息并解析 SIP 头部。

#### res_pjsip_registrar

负责处理 SIP 注册。

#### res_pjsip_pubsub

负责处理订阅、通知和发布。这些消息负责处理 SIP 状态和 BLF（忙灯场）。

### PJSIP 配置

PJSIP 有许多不同的部分。部分的格式为：

```
[Section Name]
Option = Value
Option = Value
```

#### 端点（End point）部分

最重要的配置对象是端点（endpoint）。端点配置具有核心功能，并且必须与 AOR 和传输（Transport）部分相关联。示例：

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

如果您查看上面的示例，端点是一种将所有部分连接在一起的粘合剂。它指定了传输、记录地址和电话的身份验证。还定义了 dialplan 中最重要的部分，即上下文入口点。

#### 记录地址 (AOR)

此对象告诉 Asterisk 在哪里联系端点。它存储联系地址。它还允许配置邮箱。示例：

```
[softphone]
type=aor
max_contacts=2
```

#### 身份验证 (Authentication)

此部分负责入站和出站身份验证。文档可以在示例文件 pjsip.conf 中找到。示例：

```
[softphone]
type=auth
auth_type=userpass
username=softphone
password=#supersecret#
```

#### 传输 (Transport)

传输部分允许您定义 IPV4 和 IPV6 地址以及传输协议，如 TCP、UDP、TLS、Websockets 等。您也可以在此部分配置 NAT 地址。您可以创建多个传输，但它们不能共享相同的 IP 和端口，并且您不能绑定同一 IP 版本的多个 TCP 或 TLS 传输。示例：

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### 注册 (Registration)

此对象用于配置出站注册。示例：

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### 标识 (Identify)

此对象控制哪个 SIP 请求属于哪个端点。如果您没有标识部分，系统会将“From”头部的内容与端点名称进行匹配。使用此部分，您可以将特定的 IP 地址分配给特定的端点，通过用户名或 IP 进行标识。示例：

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

ACL 对象允许您配置具有端点访问权限的特定网络。现在 ACL 在特定部分或 acl.conf 中定义。示例：

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### 实体之间的关系

配置对象之间的关系为配置提供了极大的灵活性。然而，对于初学者来说，它看起来有点复杂。

![PJSIP 配置对象之间的关系：端点链接到传输、身份验证和 AOR（包含联系人）；注册绑定到传输和身份验证；标识指向端点，而 ACL 和域别名是独立的](../images/07-sip-and-pjsip-fig14.png)

上图意味着：

#### 关系：

- ENDPOINT/AOR 多对多
- ENDPOINT/AUTH 零到多对零到一
- ENDPOINT/IDENTIFY 零到多对一
- ENDPOINT/AUTH 零到多对一
- ENDPOINT/TRANSPORT 零到多对至少一
- REGISTRATION/AUTH 零到多对零到一
- REGISTRATION/TRANSPORT 零到多对至少一
- AOR/CONTACT 多对多，ACL、DOMAIN_ALIAS 没有关系配置

### 配置软电话

要配置软电话，您必须定义许多不同的部分。下面是一个如何配置软电话的示例。对于客户端，您可以使用 SipPulse Softphone (https://www.sippulse.com/produtos/softphone)，您可以下载并针对下面的端点进行注册。

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=userpass
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

上面的配置为端口 5060 上的 UDP 设置了传输，然后定义了一个端点、其用户名和密码的身份验证，以及带有最多两个联系人的记录地址。

### 配置 SIP 中继 (SIP trunk)

要配置 SIP 中继，您需要拥有 SIP 中继的 IP 地址或主机名、名称和密码。您必须为此目的创建一个新的注册部分。

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=userpass
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### res_pjsip 上的 NAT 穿透

网络地址转换是在很久以前创建的，作为解决 IP 版本 4 地址短缺的一种方式。许多人还将 NAT 用作一种安全功能，将网络的内部地址隐藏在公共 Internet 之外。有时您必须处理 NAT 穿透。在某些情况下，服务器可能位于 NAT 后面，例如当您在云端部署服务器时。如果您在云端部署，通常您的用户也会位于 NAT 路由器后面。为了整理思路，我们将此分为两部分。第一部分是 NAT 后面的 Asterisk 服务器，例如在云部署中。在第二部分中，我们将介绍如何使用 res_pjsip 支持 NAT 后面的客户端。

#### NAT 后面的 Asterisk 服务器

当 Asterisk 服务器位于 NAT 后面时，您应该在传输部分中通知外部和内部本地地址。我们将有以下指令。

##### direct_media

媒体是直接在对等体之间流动还是通过服务器流动？对于 NAT，它应该通过服务器流动。对于 NAT，选择 no。示例：

```
direct_media=no
```

##### external_media_address

用于处理外部 RTP 的媒体地址。通常与 external_signaling_address 相同。使用服务器的公共 IP 地址进行媒体和信令传输。示例：

```
external_media_address=54.232.1.20
```

##### external_signaling_address

接收消息的外部 SIP 地址。示例：

```
external_signaling_address=54.232.1.20
```

##### local_net

您认为是本地网络的网络。示例：

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### NAT 后面的 Asterisk 服务器的完整传输示例

要使用 NAT 后面的 Asterisk 服务器，您必须执行两个步骤。第一，定义 NAT 后面的传输。第二，将此传输关联到端点。

##### 创建 NAT 后面的传输

要在 pjsip.conf 文件中创建 NAT 后面的传输，请创建如下部分。

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

将传输关联到端点

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

对于 SIP 中继，您还应该将传输关联到注册部分，如下所示。

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### 将 Asterisk 与 NAT 后面的客户端一起使用

要使用 NAT 后面的电话，您必须为每个端点配置一些额外的参数。

##### direct_media

媒体是直接在对等体之间流动还是通过服务器流动？对于 NAT，它应该通过服务器流动。示例：

```
direct_media=no
```

##### rtp_symmetric

这就是我们所说的 comedia。它不是像 SIP 中通常那样依赖于 SDP 头部中定义的地址，而是使用您接收第一个 RTP 数据包的地址，并从同一地址发回。示例：

```
rtp_symmetric=yes
```

##### force_rport

这是 RFC3581 中定义的行为。它不是使用 VIA 头部中的地址，而是从请求来源的地址发回响应。示例：

```
force_rport=yes
```

##### qualify_frequency

此设置必须应用于 AOR（而不是端点）。还有最后一步，即配置 qualify 选项。您应该始终有一些数据包 ping 目标以保持 NAT 映射打开。这在 AOR 部分中设置。示例：

- qualify_frequency=15

服务器和客户端都位于 NAT 后面的端点的完整示例

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### 通道命名

像往常一样，通道的重要方面之一是其命名，PJSIP 有一些有趣的细节。您使用 `PJSIP/` 技术拨打 PJSIP 端点：

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

一个有用的特性是能够一次拨打注册到 AOR 的所有联系人。函数 PJSIP_DIAL_CONTACTS 将被转换为要拨打的联系人列表。

```
exten=>6000,dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

拨打中继略有不同。假设中继不会注册到您的平台，或者没有与您的 AOR 记录地址关联的 IP 地址。您可以直接在行中指定中继的地址。以国际拨号为例。

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

如果您更喜欢在 AOR 部分中指定中继的地址，您也可以使用。

```
exten=>9011.,Dial(PJSIP/${EXTEN:1}@siptrunk
```

### PJSIP 配置向导

PJSIP 功能强大但配置冗长：许多不同的部分和模板起初可能会令人困惑。好消息是 PJSIP 配置向导。通过在几行中定义每个通道，它允许您创建模板并简化新设备的配置。使用文件 pjsip_wizard.conf 进行配置。您仍然必须在 pjsip.conf 文件中定义传输和全局部分。个人而言，我更喜欢仅将向导用于电话，对于 SIP 中继，通常数量不多，您可以直接在 pjsip 中配置。向导的最大优势是可以使用模板并快速创建电话。

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### 加载和卸载 PJSIP

PJSIP 是 Asterisk 22 中唯一的 SIP 通道，其模块默认加载。在极少数情况下，您可能仍希望从 modules.conf 文件控制模块加载 —— 例如，在仅使用 IAX2 或 DAHDI 的服务器上禁用 PJSIP。

#### 禁用 PJSIP

编辑 modules.conf 文件并添加以下行。

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
noload => res_pjsip_log_forwarder.so
```

### 控制台命令

现在您已经配置了 PJSIP 端点，是时候看看如何检查您的配置了。有许多控制台命令可以帮助您完成此任务。编辑 pjsip.conf 后，使用以下命令重新加载配置：

```
module reload res_pjsip.so
```

普通的 `reload`（或 `core reload`）会重新加载所有模块，包括 PJSIP。（注意没有纯粹的 `pjsip reload` 命令 —— `pjsip reload` 仅以 `pjsip reload qualify aor|endpoint` 的形式存在。）您可以使用 `help pjsip` 列出所有可用的 PJSIP 控制台命令。

#### pjsip show endpoints

此命令显示可用的端点。在下图中，我们有一个截图。您可以看到软电话端点的地址，并看到它是可用的。

![`pjsip show endpoints` 的输出，列出了 blink、siptrunk 和 softphone 端点及其 AOR、身份验证、传输和可用性 —— 软电话联系人已注册 (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

使用上面的命令，您可以查看端点的每个参数。下面的列表被截断为当前参数的一半不到。

![`pjsip show endpoint softphone` 的输出，显示单个端点的完整参数列表，从 100rel 和 allow=(ulaw) 一直到 callerid 和 connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

此命令列出已配置的记录地址对象及其联系人，以便您可以确认 Asterisk 将为每个端点发送呼叫的位置。

#### pjsip show registrations

下面的命令显示了我们自己的服务器进行的注册。

![`pjsip show registrations` 的输出：出站注册 siptrunk/sip:1020@sip.flagonc.com:5600 显示状态为 Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

list 命令更友好一些，显示的数据更少，但结构更好。列出端点：

![`pjsip list endpoints` 的输出：紧凑的每个端点一行列表（blink、siptrunk、softphone），显示其状态和通道计数](../images/07-sip-and-pjsip-fig18.png)

列出联系人：

![`pjsip list contacts` 的输出，显示 siptrunk 和 softphone 联系人 URI 及其哈希和 qualify 状态](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

最有用的故障排除命令是 SIP 数据包记录器。它会在控制台上打印发送或接收的每个 SIP 请求和回复，这在诊断注册和呼叫设置问题时非常宝贵。

```
pjsip set logger on
pjsip set logger off
```

您还可以使用 `pjsip set logger host <ip>` 将日志记录限制为单个主机。

#### pjsip set history on

PJSIP 的一个伟大补充是历史记录的概念。您可以轻松地实时捕获和分析 SIP 请求和回复。要开始历史记录，请使用以下命令。

![运行 `pjsip set history on` 返回 "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

现在您可以显示历史记录：

![`pjsip show history` 的输出：捕获的 SIP 消息的编号表 —— REGISTER, 401 Unauthorized, REGISTER, 200 OK —— 带有时间戳、方向和地址](../images/07-sip-and-pjsip-fig21.png)

然后要查看特定的请求或回复，请显示历史记录项：

![`pjsip show history entry` 的输出：单个捕获的 SIP 消息的全文 —— 这里是 Asterisk 22 对 OPTIONS 探测的 `404 Not Found` 回复 —— 显示 Via (带有 `rport`/`received`)、Call-ID、From、To 和 CSeq 头部，`Allow`/`Supported` 能力，以及 `Server: Asterisk PBX 22.10.0` 头部](../images/07-sip-and-pjsip-fig22.png)

非常简单，不是吗？您也可以随时使用 `pjsip set history clear` 清除历史记录。

> **正在迁移现有的 chan_sip/sip.conf 系统？** 旧版 `chan_sip`
> 驱动程序和完整的 **sip.conf → pjsip.conf 迁移指南**（包括
> 概念映射表和 `sip_to_pjsip.py` 转换脚本）在 *Legacy channels* 一章中介绍。

## 测验

1. 在 SIP 架构中，哪个组件接收请求并用携带新位置的重定向响应（例如 `302 Moved Temporarily`）回答它，然后退出后续消息的路径？
   - A. 代理服务器
   - B. 重定向服务器
   - C. 位置服务器
   - D. 注册服务器

2. 当 Asterisk 处理两部电话之间的 SIP 呼叫时，它扮演什么角色？
   - A. 仅保持在信令路径中的 SIP 代理
   - B. SIP 重定向服务器
   - C. 桥接两个 SIP 通道的背靠背用户代理 (B2BUA)
   - D. 无状态 SIP 负载均衡器

3. 电话使用哪种 SIP 方法来告诉注册服务器其当前 IP 地址，以便以后可以接收呼叫？
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. 对或错：在 Asterisk 22 中，`chan_sip` 和 `sip.conf` 仍然作为 PJSIP 旁边的旧版回退可用。

5. 端点必须与哪些配置对象关联，以便 Asterisk 知道要使用的监听套接字以及将呼叫发送到该设备的位置？（选择所有适用项。）
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. 在 PJSIP `aor` 对象中，哪个设置通过定期 qualify 联系人来保持 NAT 映射打开，它的单位是什么？
   - A. `qualify=yes` (布尔值)
   - B. `qualify_frequency` (秒)
   - C. `rtp_timeout` (毫秒)
   - D. `nat=force_rport`

7. 填空：要使 Asterisk 通过源 IP 地址（而不是通过 `From` 头部）将入站 SIP 请求匹配到特定端点，您需要创建一个带有 `type=________` 的部分。

8. 哪个 PJSIP 对象用于配置从 Asterisk 到 SIP 中继提供商的 **出站** 注册？
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. 在 Asterisk 22 CLI 上，哪个命令启用了将每个 SIP 请求和回复打印到控制台的 SIP 数据包记录器？
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. 在服务于对称 NAT 后面的电话的 PJSIP 端点上，哪一对设置使 Asterisk 回复请求的源地址 (RFC 3581) 并将媒体发送回 RTP 实际到达的地方？
    - A. `direct_media=yes` 和 `srvlookup=yes`
    - B. `force_rport=yes` 和 `rtp_symmetric=yes`
    - C. `allowguest=yes` 和 `insecure=invite`
    - D. `qualify=yes` 和 `nat=no`

**答案：** 1 — B · 2 — C · 3 — D · 4 — 错 · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
