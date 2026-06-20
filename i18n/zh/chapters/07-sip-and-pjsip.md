# SIP 与 PJSIP 深入解析

SIP 是协议；PJSIP 是 Asterisk 22 使用的实现方式。**PJSIP**（`chan_pjsip`, 通过 `pjsip.conf` 配置）是 Asterisk 22 LTS 中唯一的 SIP 通道驱动。本章介绍 SIP 协议基础（属于协议层面，始终 100% 有效）以及您日常使用的 PJSIP 对象模型和配置。已废弃的旧版驱动及迁移指南请参见 *Legacy channels* 一章。

## Objectives

By the end of this chapter, you should be able to:

- Explain the role of the SIP user agents, proxies, registrar, and gateways;
- Follow a basic SIP call flow (REGISTER, INVITE, provisional and final responses, ACK, BYE) and read a SIP message;
- Describe how SDP negotiates the media session and how NAT affects SIP signaling and RTP;
- Map the PJSIP object model — `endpoint`, `auth`, `aor`, `transport`, `identify`, and `registration` — and how the objects reference one another;
- Configure SIP phones and trunks in `pjsip.conf`, including the NAT-traversal options; and
- Verify and troubleshoot endpoints with the `pjsip show …` CLI commands.

## SIP 协议基础

Session Initiation Protocol (SIP) 是一种基于文本的协议，类似于 HTTP 和 SMTP，旨在初始化、保持和终止用户之间的交互式通信会话。这些会话可能包括语音、视频、聊天、互动游戏等。SIP 由 IETF 定义，已成为语音通信的事实标准。了解 SIP 的工作原理非常重要。在 Asterisk 22 中，SIP 配置位于 `pjsip.conf` 中，这是基于 SIP 的系统中最常编辑的文件之一（仅次于 `extensions.conf`）。

### 工作原理

SIP 是一种信令协议，包含以下组件：User Agent Client、User Agent Servers、SIP Proxies 和 SIP Gateways。下图描绘了这些组件之间的关系。

- UAC（user agent client）– 初始化 SIP 信令的客户端或终端。  
- UAS（user agent server）– 响应来自 UAC 的 SIP 信令的服务器。  
- UA（user agent）– 包含 UAC 和 UAS 的 SIP 终端（电话或网关）。  
- Proxy Server – 接收来自 UA 的请求，并在特定站点不在其管理范围时转发给其他 SIP Proxy。  
- Redirect Server – 接收请求并将其连同目标数据返回给 UA，而不是直接转发到目标。  
- Location Server – 接收来自 UA 的请求，并使用这些信息更新位置数据库。

通常，代理、重定向和定位服务器托管在同一硬件上，并使用同一套软件，我们称之为 **SIP 代理**。SIP 代理负责定位数据库的维护、连接的建立以及会话的终止。

![主要的 SIP 组件：用户代理 (UAC/UAS/UA)、注册/代理/重定向服务器，以及连接 PSTN 的网关，RTP 媒体直接在端点之间流动](../images/07-sip-and-pjsip-fig01.png)

#### SIP 注册过程

在电话能够接收来电之前，需要先在位置数据库中进行注册。在位置数据库中，IP 地址将与名称绑定。在下面的示例中，分机 8500 将绑定到 IP 地址 200.180.1.1。并不一定必须使用电话号码。在 SIP 架构中，已注册的分机也可以是 flavio@voip.school。

![SIP 注册：电话向其 IP 地址发送 REGISTER，绑定分机 8500，注册服务器将联系人存储在位置数据库中并回复 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### 代理操作

When operating as a SIP proxy, the SIP server stays in the middle of the signaling and is capable of advanced routing and billing. The media flow, based on the real time protocol (RTP) still goes directly between the endpoints.

![代理操作：SIP 代理保持在信令路径（INVITE/200 OK）中，并在位置服务器中查找被叫方，而 RTP 媒体直接在两个端点之间流动】(../images/07-sip-and-pjsip-fig03.png)

#### 重定向操作

在重定向时，SIP 服务器仅向用户代理发送一条消息（例如 302 moved temporarily），并且不再参与新消息的路径。它在资源使用方面非常轻量，但你完全没有控制权。重定向有时在负载均衡设计中使用。

![重定向操作：重定向服务器用 302 Moved Temporarily 响应 INVITE 并携带 contact，然后在呼叫者直接向新位置重新发送 INVITE/ACK 时让位】(../images/07-sip-and-pjsip-fig04.png)

#### Asterisk 如何处理 SIP

了解 Asterisk 既不是 SIP 代理也不是 SIP 重定向器非常重要。Asterisk 可以充当注册服务器和位置服务器的角色；然而，它仅将两个 UAC 连接到自身。因此，Asterisk 被视为后背对后用户代理（B2BUA）。换句话说，它连接两个 SIP 通道，将它们桥接在一起。Asterisk 具有重新邀请机制，能够让 SIP 通道直接相互通信，而不是通过 Asterisk 传递。在 PJSIP 端点上，这由参数 `direct_media` 控制。使用 `direct_media=yes` 时，RTP 流直接从一个端点流向另一个端点，释放服务器资源。

#### SIP 操作（direct_media=yes）

![使用 directmedia=yes 的 SIP 操作：SIP 信令通过 Asterisk 传递，而 RTP 音频直接在两部电话之间传输，释放服务器资源](../images/07-sip-and-pjsip-fig05.png)

然而，如果您需要使用 Asterisk 转移或录制通话，您可以使用参数 `direct_media=no`强制将 RTP 流经由 Asterisk 服务器。

#### SIP 操作（direct_media=no）

![使用 directmedia=no 的 SIP 操作：SIP 信令和 RTP 音频均通过 Asterisk 锚定，使其能够录音、转码或转接通话](../images/07-sip-and-pjsip-fig06.png)

#### SIP 消息

基本的 SIP 消息有：

- INVITE – 建立连接  
- ACK – 确认  
- BYE – 终止连接  
- CANCEL – 终止未建立的呼叫  
- REGISTER – 将 UAC 注册到 SIP 代理  
- OPTIONS – 可用于检查可用性  
- REFER – 将 SIP 呼叫转接给其他人  
- SUBSCRIBE – 订阅通知事件  
- NOTIFY – 发送通道信息  
- INFO – 发送各种消息（例如 DTMF）  
- MESSAGE – 发送即时消息

SIP 响应采用文本格式，易于阅读（类似于 HTTP 消息）。最重要的响应有：

- 1XX – 信息消息 (100–trying, 180–ringing, 183–progress)
- 2XX – 请求成功完成 (200 – OK)
- 3XX – 呼叫重定向，请求必须指向其他位置 (302 – moved temporarily, 305 – use proxy)
- 4XX – 错误 (403 – Forbidden)
- 5XX – 服务器错误 (500 – Internal Server Error; 501 – Not implemented)
- 6XX – 全局失败 (606 – Not acceptable)

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

SDP 最初在 IETF RFC 2327 中定义，现已被 RFC 4566 取代。它用于描述多媒体会话，以便进行会话公告、会话邀请以及其他形式的多媒体会话发起。SDP 包括：

- 传输协议 (RTP/UDP/IP)
- 媒体类型 (text, audio, video)
- 媒体格式或编解码器 (H.261 video, g.711 audio, 等)
- 接收这些媒体所需的信息 (地址、端口等)

以下示例是对描述两部电话之间通话的 SDP 的转录。

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

### SIP NAT 穿越

网络地址转换（NAT）是大多数网络用来节省 Internet IP 地址的功能。通常，公司只会获得一小段 IP 地址块，而终端用户在连接到 Internet 时会动态获取一个 IP 地址。NAT 通过将内部地址映射到外部地址来解决地址问题。它在内存中存储内部地址到外部地址的映射关系。该映射在特定时间长度后失效并被丢弃。映射使用 IP:端口 对来表示内部和外部地址。NAT 有四种类型：

- 完全锥形  
- 受限锥形  
- 端口受限锥形  
- 对称  

NAT 理论如下——四种 NAT 类型、Contact 头部问题、保活以及强制媒体通过服务器——属于协议层面，适用于任何 SIP 实现。如何在 Asterisk 22（PJSIP）上配置这些行为将在本章后面的 *Nat traversal on res_pjsip* 中介绍。

#### 全锥形

第一个 NAT，完整锥形，表示从外部 IP:端口 对到内部 IP:端口 对的静态映射。任何外部计算机都可以使用该外部 IP:端口 对进行连接。在使用过滤器实现的无状态防火墙中就是这种情况。

![全锥形 NAT：内部主机 (10.0.0.1:8000) 被静态映射到外部对 200.180.4.168:1234，因此任何外部计算机都可以向该对发送数据包并到达内部主机](../images/07-sip-and-pjsip-fig11.png)

#### 受限锥形

在受限锥形 NAT 场景中，只有当内部计算机向外部地址发送数据时，外部 IP:端口 对才会被打开。然而，受限锥形 NAT 会阻止来自不同地址的任何入站数据包。换句话说，内部计算机必须先向外部计算机发送数据，才能收到返回的数据。

#### 端口受限锥形

端口受限锥形防火墙几乎与受限锥形防火墙相同。唯一的区别是，现在，传入的数据包必须来自与发送的数据包完全相同的 IP 和端口。

#### 对称

最后一种 NAT 类型称为对称型。它与前面三种不同，因为它会对每个外部地址进行特定的映射。只有特定的外部地址才能通过 NAT 映射返回。无法预测 NAT 设备将使用的外部 IP:端口 对。其他三种 NAT 类型允许使用外部服务器来发现用于通信的外部 IP 地址。而在对称型 NAT 中，即使能够连接到外部服务器，发现的地址也只能用于该服务器，不能用于其他任何设备。

![对称 NAT：为每个目的地分配不同的外部源端口，因此针对一个服务器发现的映射不能被另一个主机重复使用，这会破坏基于 STUN 的穿透](../images/07-sip-and-pjsip-fig12.png)

#### NAT 防火墙表

The following table summarizes the four types of NAT.

| NAT 类型 | 必须先发送数据 | 能够确定返回数据包的外部 IP:端口 | 限制传入数据包到目标 IP:端口 |
| --- | --- | --- | --- |
| 全锥形 | 否 | 是 | 否 |
| 受限锥形 | 是 | 是 | 仅 IP |
| 端口受限锥形 | 是 | 是 | 是 |
| 对称型 | 是 | 否 | 是 |

#### SIP 信令和 RTP 通过 NAT

一些在 NAT 穿越中最大的問題在於必須同時解決兩個問題：SIP 信令和音頻（RTP）。大多數單向音頻的問題都與 NAT 有關。關於 SIP 有一個有趣的現象，當 UAC 發送封包時，它會在 SIP 的 “Contact” 標頭欄位中嵌入 IP 位址。通常這是內部（RFC1918）位址；對該封包的回應無法透過 Internet 路由回到 UAC。概念上的解決方案始終是相同的：

- **忽略 Contact/Via 地址并回复到数据包实际来源的地址。** 这是一种在 RFC 3581（`rport`）中定义的行为。在 PJSIP 上它是 `force_rport=yes` ，并且 `rewrite_contact=yes` 将存储的 contact 重写为源地址。  
- **将媒体发送回 RTP 实际到达的地址**（对称 RTP，历史上称为 *comedia*）。在 PJSIP 上这对应 `rtp_symmetric=yes`。  
- **保持 NAT 映射打开。** 如果映射超时，Asterisk 将无法向 UAC 发送 INVITE —— 电话可以发起呼叫但无法接收呼叫。定期发送 OPTIONS（*qualify*）可以保持穿孔打开。在 PJSIP 上这对应 AOR 上的 `qualify_frequency=`。

如果用户的 NAT 属于对称类型，则无法直接从一个 UAC 向另一个 UAC 发送数据包；在这种情况下必须使用 `direct_media=no` 强制将 RTP 通过 Asterisk 传输。这些配置适用于大多数情况。可以使用诸如 UDP 穿越 NAT 的简单遍历（STUN）等高级技术来优化流量，这在全锥形、受限锥形和端口受限锥形以及应用层网关（ALG）环境中都很有用。遗憾的是，如今大多数防火墙——甚至是家庭 DSL/有线路由器——都是对称的，使得 STUN 无法使用。ALG 本可以解决此问题，但在大多数情况下要么不受支持，要么未实现，或者存在 bug。

#### Asterisk 在 NAT 后面

Sometimes the Asterisk server itself is implemented behind a firewall with NAT — a very common situation when you deploy in the cloud. In this case it is necessary to do some extra configuration so that Asterisk advertises its **public** address in the SIP and SDP headers instead of its private one.

概念上有三个步骤：

- 转发 SIP 信令端口（默认 UDP 5060）从防火墙到 Asterisk 服务器。  
- 转发 RTP 媒体端口范围（默认 UDP 10000–20000，在 `rtp.conf` 中设置）从防火墙到 Asterisk 服务器。  
- 告诉 Asterisk 它的外部地址以及哪个网络是本地的，以便它在报头中替换公共地址。

在 PJSIP 中，这最后两个项目映射到 `external_media_address` / `external_signaling_address` 和 `local_net=` 在 **transport** 上，RTP 端口范围仍然在 `rtp.conf` 中配置。

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

The complete, worked PJSIP configuration for an Asterisk server behind NAT is given later in this chapter under *Asterisk Server behind NAT*.

### SIP 限制

Asterisk 使用传入的 RTP 流来同步传出的流。如果传入的流被中断（静音抑制），保持音乐将被切断。换句话说，您不应在使用 Asterisk 的电话或运营商上启用静音抑制。

## PJSIP: the SIP channel

PJSIP 是 Asterisk 中的 SIP 通道。它首次在 Asterisk 12 中引入，经过多年开发后，成为默认且推荐的 SIP 通道；在 Asterisk 22（当前 LTS）中，它是唯一的 SIP 通道驱动。PJSIP 基于 Teluu 的项目 pjproject。pjproject 协议栈被许多软电话和商业 SIP 实现所采用，是一个功能丰富且成熟的 SIP 栈。

### Why to use PJSIP

PJSIP 是对 Asterisk 处理 SIP 的方式进行的全新设计，了解其成为标准的特性非常重要。

#### Features

该通道支持许多特性，以下几项值得一提

- Multiple registrations: You may use more than one phone connected to the same Address of Record. In other words, you can connect two phones to the same endpoint.
- Friendly Application Program Interface (API). The API is modular and easy to extend, built from many small cooperating modules rather than one large block of code.
- Multiple transports: You can listen to multiple addresses, ports and transports when using PJSIP. You are not limited to a single bind address for all your devices. PJSIP is very flexible.

#### A note on configuration

PJSIP configuration is more verbose: it requires a little more effort and more lines of configuration, since each device is described by several related objects instead of one peer block. That extra structure is what gives PJSIP its flexibility, and the configuration wizard (covered later) keeps day-to-day provisioning short.

### PJSIP modules

The PJSIP channel is implemented by many modules described below:

#### res_pjsip

This is the base layer of PJSIP and the main module. It is responsible for some of the main services.

#### res_pjsip_session

This module is responsible for media sessions, session description protocol processing and some addons

#### res_pjsip_messaging

Process SIP messages and parse SIP headers.

#### res_pjsip_registrar

Responsible to handle SIP registrations

#### res_pjsip_pubsub

Responsible to process subscribe, notify and publish. These messages are responsible to handle SIP presence and BLF (Busy Lamp Field).

### PJSIP configuration

PJSIP has many different sections. The format of the section are:

```
[Section Name]
Option = Value
Option = Value
```

#### End point section

The most important configuration object is the endpoint. The endpoint configuration has core functionality and has to be associated with an AOR and Transport section. Example:

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

如果查看上面的示例，endpoint 是将所有部分连接在一起的粘合剂。它指定了传输方式、地址记录以及电话的认证方式。它还定义了最重要的部分——dialplan 中的 context 入口点。

#### Address of Record (AOR)

此对象告诉 Asterisk 如何联系 endpoint。它存储联系地址。它还允许配置邮箱。示例：

```
[softphone]
type=aor
max_contacts=2
```

#### Authentication

本节负责入站和出站的身份验证。文档位于示例文件 pjsip.conf 中。示例：

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### 传输

该传输部分允许您定义 IPV4 和 IPV6 地址以及传输协议，如 TCP、UDP、TLS、Websockets 等。您还可以在此部分配置 NAT 后的地址。您可以创建多个传输，但它们不能共享相同的 IP 和端口，并且同一 IP 版本下不能绑定多个 TCP 或 TLS 传输。示例：

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### 注册

此对象用于配置出站注册。示例：

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### 标识

此对象控制每个 endpoint 属于哪个 SIP 请求。如果没有 identify 部分，系统将把 “From” 头部的内容与 endpoint 名称匹配。使用此部分，您可以将特定 IP 地址分配给特定的 endpoint，依据用户名或 IP 进行标识。示例：

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

ACL 对象允许您为端点配置具有访问权限的特定网络。现在，ACL 在特定节或在 acl.conf 中定义。示例：

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### 实体之间的关系

配置对象之间的关系提供了极大的灵活性。然而，对于刚入门的人来说可能显得有些复杂。

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

上图的含义是：

#### 关系：

| Objects | Cardinality |
| --- | --- |
| ENDPOINT / AOR | many to many |
| ENDPOINT / AUTH | zero to many, to zero to one |
| ENDPOINT / IDENTIFY | zero to one |
| ENDPOINT / TRANSPORT | zero to many, to at least one |
| REGISTRATION / AUTH | zero to many, to zero to one |
| REGISTRATION / TRANSPORT | zero to many, to at least one |
| AOR / CONTACT | many to many |

ACL 和 DOMAIN_ALIAS 与其他对象没有直接的配置关系。

### 配置软电话

要配置软电话，需要定义许多不同的章节。下面是一个配置软电话的示例。客户端可以使用 SipPulse Softphone (https://www.sippulse.com/produtos/softphone)，您可以下载并在下面的 endpoint 上注册。

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
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

上述配置为 UDP 端口 5060 设置了一个传输，然后定义了一个端点、其通过用户名和密码进行的身份验证，以及最多两个联系人的地址记录（Address of Record）。

### 配置 SIP 中继

要配置 SIP 中继，您需要拥有 SIP 中继的 IP 地址或主机名、名称和密码。您必须为此创建一个新的注册（registration）段落。

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
auth_type=digest
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

### Nat traversal on res_pjsip

网络地址转换（NAT）最初是为了解决 IPv4 地址短缺而创建的。许多人也将 NAT 用作一种安全特性，用来隐藏网络内部地址，使其不被公共互联网看到。有时你必须处理 NAT 穿越问题。在某些情况下，服务器可能位于 NAT 后面，例如在云端部署服务器时。很多情况下，如果你在云端部署，用户也会位于 NAT 路由器之后。为了条理清晰，我们将把内容分为两部分。第一部分讨论位于 NAT 后的 Asterisk 服务器（如云部署）。第二部分则介绍如何使用 res_pjsip 支持位于 NAT 后的客户端。

#### Asterisk Server behind NAT

当 Asterisk 服务器位于 NAT 后时，需要在 transport 部分声明外部和内部本地地址。我们将使用以下指令。

##### direct_media

媒体是直接在对等点之间传输，还是通过服务器转发？对于 NAT 场景，应该通过服务器转发。对于 NAT 请选择 no。示例：

```
direct_media=no
```

##### external_media_address

用于处理外部 RTP 的媒体地址。通常与 external_signaling_address 相同。使用服务器的公共 IP 地址作为媒体和信令。示例：

```
external_media_address=54.232.1.20
```

##### external_signaling_address

External SIP address where to receive messages. Example:

```
external_signaling_address=54.232.1.20
```

##### local_net

您认为是本地网络的网络。例如：

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### 完整示例：在 NAT 后面的 Asterisk 服务器的传输配置

要在 NAT 后使用 Asterisk 服务器，需要完成两步。首先，定义一个位于 NAT 后的传输。其次，将该传输关联到 endpoint。

##### 在 NAT 后创建传输

要在 `pjsip.conf` 文件中创建位于 NAT 后的传输，请按如下方式添加一个节。

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

对于 SIP 中继，您还应将传输关联到注册部分，如下所示。

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### 在 NAT 后面的客户端使用 Asterisk

要在 NAT 环境下使用电话，必须为每个 endpoint 配置一些额外的参数。

##### direct_media

媒体是直接在对等点之间传输，还是通过服务器转发？在 NAT 环境下应当通过服务器转发。示例：

```
direct_media=no
```

##### rtp_symmetric

这就是我们所说的“comedia”。不再使用 SDP 头部中通常定义的地址，而是使用收到的第一个 RTP 包的来源地址，并从同一地址回送。 示例：

```
rtp_symmetric=yes
```

##### force_rport

这是 RFC3581 中定义的行为。与其使用 VIA 头中的地址，不如从请求来源的地址返回响应。示例：

```
force_rport=yes
```

##### qualify_frequency

此设置必须应用于 AOR（而非 endpoint）。还有最后一步，需要配置 qualify 选项。您应始终让一些数据包 ping 目标，以保持 NAT 映射打开。此项在 AOR 部分设置。示例：

- qualify_frequency=15

完整示例：服务器和客户端都位于 NAT 后面的 endpoint

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

如往常一样，通道的一个重要方面是其命名，PJSIP 有一些有趣的细节。您使用 `PJSIP/` 技术拨打 PJSIP 端点：

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

一个有用的功能是能够一次拨打注册到 AOR 的所有联系人。函数 PJSIP_DIAL_CONTACTS 将被转换为要拨打的联系人列表。

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

拨打中继略有不同。假设中继不会注册到您的平台或没有与您的 AOR 记录地址关联的 IP 地址。您可以在线路中直接指定中继的地址。以国际拨号为例。

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

如果您更喜欢在 AOR 部分指定中继的地址，也可以使用。

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### PJSIP 配置向导

PJSIP 功能强大，但配置起来比较繁琐：有许多不同的节，而且模板一开始可能会让人困惑。好消息是有 PJSIP 配置向导。通过在几行中定义每个通道，它允许您创建模板并简化新设备的配置。使用文件 **pjsip_wizard.conf** 进行配置。您仍然需要在 **pjsip.conf** 文件中定义 transport 和 global 节。就个人而言，我倾向于仅将向导用于电话，而对于 sip trunk 通常数量不大，可以直接在 pjsip 中配置。向导的最大优势是可以使用模板，快速创建电话。

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

PJSIP 是 Asterisk 22 中唯一的 SIP 通道，其模块默认已加载。在极少数情况下，您可能仍希望通过 modules.conf 文件来控制模块的加载——例如，在仅使用 IAX2 或 DAHDI 的服务器上禁用 PJSIP。

#### 禁用 PJSIP

编辑 modules.conf 文件并添加以下行。

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### 控制台命令

既然您已经配置了您的 PJSIP 端点，现在是查看如何检查配置的时候了。 有许多控制台命令可以帮助您完成此任务。 编辑 pjsip.conf 后，使用以下命令重新加载配置：

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

#### pjsip show registrations

The command below shows the registrations made by our own server.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listing contacts:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems.

```
pjsip set logger on
pjsip set logger off
```

You can also restrict the logging to a single host with `pjsip set logger host <ip>`.

#### pjsip set history on

A great addition to PJSIP is the concept of history. You can capture and analyse SIP request and replies in real time in an easy way. To start history use the command below.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Now you can show the history:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

Then to see a specific request or reply, show the history item:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

Very easy, isn’t it? You may also clear the history whenever you want using `pjsip set history clear`.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Summary

SIP 是 IETF 的信令协议，用于建立、修改和拆除媒体会话。它的用户代理、代理、注册服务器和网关交换基于文本的消息——REGISTER、INVITE、临时和最终响应、ACK 以及 BYE——而 SDP 协商编解码器，RTP 传输媒体。该协议理论是永恒的，适用于任何 SIP 实现。

在 Asterisk 22 中，你通过 **PJSIP**（`chan_pjsip`）使用 SIP，配置位于 `pjsip.conf`。不再使用单一的整体 peer，而是将设备建模为一组小的、相互引用的对象：`endpoint`（呼叫行为和编解码器）、`auth`（凭证）、`aor`（可达位置）和 `transport`（监听器），以及用于服务提供商的 `identify`（按 IP 匹配 trunk）和 `registration`（注册出站）。你已经看到这些对象如何组合在一起，如何配置电话和 trunk，NAT 穿透选项（`force_rport`、`rewrite_contact`、`rtp_symmetric`、`direct_media`以及传输的 `external_*`/`local_net`）如何解决实际部署中的问题，以及如何使用 `pjsip show endpoints`、`aors`、`contacts`和 `registrations`进行检查。

## 小测验

1. 在 SIP 架构中，哪个组件接收请求并用携带新位置的重定向响应（例如 `302 Moved Temporarily`）作答，然后退出后续消息的路径？
   - A. 代理服务器
   - B. 重定向服务器
   - C. 位置服务器
   - D. 注册服务器

2. 当 Asterisk 处理两部电话之间的 SIP 呼叫时，它扮演什么角色？
   - A. 仅停留在信令路径中的 SIP 代理
   - B. SIP 重定向服务器
   - C. 将两个 SIP 通道桥接的后端用户代理 (B2BUA)
   - D. 无状态 SIP 负载均衡器

3. 哪个 SIP 方法被电话用来告诉注册服务器它当前的 IP 地址，以便以后接收呼叫？
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. 判断对错：在 Asterisk 22 中，`chan_sip`和`sip.conf`仍然作为传统回退选项与 PJSIP 并存。

5. 为了让 Asterisk 知道要使用的监听套接字以及将呼叫发送到该设备的去向，端点必须关联哪些配置对象？（请选择所有适用项。）
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. 在 PJSIP `aor` 对象中，哪个设置通过定期确认联系来保持 NAT 映射打开，它的单位是什么？
   - A. `qualify=yes`（布尔值）
   - B. `qualify_frequency`（秒）
   - C. `rtp_timeout`（毫秒）
   - D. `nat=force_rport`

7. 填空：要让 Asterisk 通过源 IP 地址（而不是通过 `From` 头）将入站 SIP 请求匹配到特定端点，需要创建一个包含 `type=________` 的节。

8. 哪个 PJSIP 对象用于配置 **出站** 注册，从 Asterisk 到 SIP 中继提供商？
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. 在 Asterisk 22 CLI 上，哪个命令启用 SIP 包记录器，将每个 SIP 请求和响应打印到控制台？
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. 在为位于对称 NAT 后面的电话服务的 PJSIP 端点上，哪一对设置使 Asterisk 回复请求的源地址（RFC 3581）并将媒体发送回 RTP 实际到达的地方？
    - A. `direct_media=yes` 和 `srvlookup=yes`
    - B. `force_rport=yes` 和 `rtp_symmetric=yes`
    - C. `allowguest=yes` 和 `insecure=invite`
    - D. `qualify=yes` 和 `nat=no`

**答案：** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
