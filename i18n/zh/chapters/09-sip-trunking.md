# SIP trunking, DID & the PSTN

一个只能呼叫自身的 PBX 用处不大。迟早每个系统都需要连接到外部世界——公共交换电话网络 (PSTN)、SIP 提供商或另一个 PBX。承载这些呼叫的链路称为 **trunk**（中继）。在 TDM 时代，中继是一条物理电路：T1/E1 PRI 或一束模拟 FXO 线路。如今，它几乎总是 **SIP trunk**——一种通过与其它业务相同的 IP 网络承载的、连接到互联网电话服务提供商 (ITSP) 的逻辑连接。

本章将展示如何使用 PJSIP 将 Asterisk 22 连接到 ITSP，如何在基于注册的中继和基于 IP 的中继之间进行选择，如何将入站 DID 号码路由到正确的目的地，如何发送带有正确主叫号码和 E.164 格式的出站呼叫，以及如何跨多个中继构建故障转移和最低成本路由。最后，我们将介绍中继的 NAT 处理，并进行一个实验：搭建第二个 Asterisk（和 SIPp）作为模拟 ITSP，以便您可以跨中继拨打真实呼叫。

此处的所有内容均已针对本书的 Asterisk 22.10.0 实验环境进行了验证；中继对象模式与《Building your first PBX with PJSIP》和《SIP & PJSIP in depth》中介绍的模式相同。

## 目标

读完本章后，您应该能够：

- 使用 PJSIP 将 Asterisk 22 连接到 ITSP
- 在基于注册的中继和基于 IP（静态）的中继之间进行选择
- 将入站 DID 路由到正确的 extension、IVR 或队列
- 使用正确的主叫号码和 E.164 格式路由出站呼叫
- 使用 `${DIALSTATUS}` 构建中继故障转移和最低成本路由
- 处理传输层和 endpoint 上的中继 NAT 问题

## 什么是 SIP trunk

SIP trunk 是您的 PBX 与另一个 SIP 系统之间的逻辑语音路径。实际上，“另一个系统”通常是以下两者之一：

- **ITSP (Internet Telephony Service Provider)。** 一家商业运营商，向您出售呼叫发起和终止服务，通常还提供一组电话号码 (DID)。您将 Asterisk 指向提供商的信令主机，提供商会将您的呼叫连接到更广泛的 PSTN。这是大多数现代系统连接电话网络的方式——无需电信硬件。
- **PSTN 网关。** 一种拥有物理 PSTN 接口（PRI 卡、模拟 FXO 端口或 GSM/4G 网关）的设备（或另一个 Asterisk），它将这些接口作为 SIP 呈现给您的 PBX。网关执行 TDM 到 SIP 的转换；从 Asterisk 的角度来看，它只是另一个 SIP trunk。

无论哪种方式，在 PJSIP 中，中继都**只是一个 endpoint**。您用于电话的同一对象系列——`endpoint`、`auth`、`aor`，可选的 `identify` 和 `registration`——即可构建中继。区别在于细节：中继进行*出站*认证（您是客户端，因此凭据放入 `outbound_auth`，而不是 `auth`），它通常不会向您注册用户代理（您注册到*它*，或者它从已知的 IP 向您发送流量），并且它将入站呼叫落地在专门的 context 中，例如 `from-pstn`，而不是 `from-internal`。

> **与旧式 TDM 中继的比较。** PRI 为您提供固定数量的 B 通道（T1 上 23 个，E1 上 30 个），并通过专用的 D 通道进行呼叫建立信令（参见《Legacy channels》一章）。SIP trunk 没有固定的通道数——容量取决于您的带宽、提供商的策略以及任何 `max_contacts`/并发呼叫限制。过去在 ISDN 信息元素中传输的主叫号码、DID 和呼叫进度，现在通过 SIP 头部和 SDP 传输。

ITSP 与您交换流量的方式有两种，它们决定了您如何构建中继：**基于注册 (registration-based)** 和 **基于 IP (IP-based/static)**。我们将依次介绍这两种方式。

## 基于注册的中继

当提供商期望*您*登录到*他们*时，使用基于注册的中继模型。您的 Asterisk 会定期向提供商发送 SIP `REGISTER`，并使用用户名和密码进行认证，这与电话注册到您的 PBX 的方式完全相同。当您的公网 IP 是动态的、您位于 NAT 之后，或者提供商仅通过 SIP 凭据而非 IP 地址识别客户时，这种方式很常见。

在 PJSIP 中，出站登录位于专门的 `registration` 对象中。它取代了已移除的 `chan_sip` 驱动程序在 `sip.conf` 中使用的单个 `register =>` 行。以下是一个连接到虚构提供商的完整注册中继，遵循前面章节中验证过的模式——注意 `outbound_auth`（不是 `auth`）、`server_uri`/`client_uri`（不是 `server`/`client`）、endpoint 上的 `from_user`/`from_domain` 以及 `dtmf_mode=rfc4733`：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

需要注意的几点：

- **`auth_type=digest`，而不是 `userpass`。** 两者都产生相同的摘要认证，但在 Asterisk 22 中，`userpass`（以及旧的 `md5`）已被**弃用并静默转换为 `digest`**。在新的配置中请优先使用 `digest`；您仍然会在旧文件和本书的前几章中看到 `userpass`。
- **endpoint 和注册上的 `outbound_auth`。** 注册使用它来认证 `REGISTER`；endpoint 使用它来应答提供商发送回出站 `INVITE` 的 `407 Proxy Authentication Required`。它们可以共享同一个 `auth` 对象。
- **`from_user` / `from_domain`。** 许多提供商会拒绝那些 `From` 头部未携带您的账号和其域名的呼叫。这两个选项设置的正是这些内容。
- **`contact_user=4830001000`。** 这将成为您注册的 `Contact` 的用户部分，以便提供商知道将入站呼叫发送到哪个号码。它是旧式 `register =>` 行上 `/9999` 后缀的现代等效项。
- **`retry_interval=60`。** 如果注册失败，每 60 秒重试一次。

重新加载后，使用 `pjsip show registrations` 确认注册。在实验环境中——其中 `itsp.example.com` 实际上并不应答——表格如下所示：

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

`(exp. Ns)` 后缀会倒计时直到下一次尝试；一旦归零，它会短暂显示 `(exp. Ns ago)`，然后触发重试。在真实的提供商环境下，`Status` 列会显示 `Registered`，即距离下一次刷新的剩余秒数。`Rejected`（或 `Unregistered`）意味着提供商未接受登录——开启 `pjsip set logger on` 并查看 `401`/`403` 回复，这通常是错误的用户名、密码或 `client_uri` 域名。

## 基于 IP (静态) 的中继

第二种模型根本不需要注册。提供商知道您的公网 IP 地址并直接向其发送呼叫；反过来，您将呼叫发送到提供商已知的信令 IP。认证方式是**源 IP 地址**，而不是 SIP 凭据。这对于您控制的两个服务器之间的中继，或者双方都有静态地址的企业中继来说很典型。

关键对象是 `identify`。它告诉 Asterisk：“任何从*此* IP 到达的 SIP 请求都属于*那个* endpoint。” 如果没有它，PJSIP 会尝试通过 `From` 用户将入站请求匹配到 endpoint，而运营商的流量无法满足这一点——因此呼叫将被拒绝或落入 `anonymous` endpoint。

静态中继去掉了 `registration` 对象并添加了 `identify`：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
```

`match` 接受 IP 地址、CIDR 范围或主机名。**主机名仅在配置加载时解析一次**，因此如果提供商的 IP 发生变化，您必须重新加载。对于发布了多个媒体网关的运营商，请列出每个信令 IP——您可以重复 `match` 或提供一个 CIDR：

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

使用 `pjsip show identifies` 验证 Asterisk 将接受的内容。从实验环境中捕获（`sipp-identify` 行是实验环境中预先存在的 SIPp endpoint）：

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### 安全隐患

没有认证的基于 IP 的中继是一扇门，而 `identify`/`match` 是它上面唯一的锁。如果您 `match` 的范围太广——或者攻击者可以伪造源 IP——呼叫将未经认证地落入您的 `from-pstn` context。两种防御措施结合使用：

- **匹配尽可能精确。** 优先使用特定的主机 IP 而不是宽泛的 CIDR。只有提供商真实的信令 IP 才应放入 `match`。
- **配合 ACL 使用。** PJSIP 可以使用 `type=acl` 对象（或 `acl.conf`）在 SIP 层到达 endpoint 之前丢弃流量：

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

在全局部分（`acl=itsp-acl` 在 `[global]`/`type=global` 中）引用它，或按传输层应用。原则与 SIP 一章中的相同：拒绝所有，只允许您信任的。无论您的中继 context 做什么，**在没有明确的、经过认证的规则的情况下，永远不要让它到达可以拨回 PSTN 的 context**——这是经典的电信欺诈漏洞。

> **我应该使用哪种模型？** 如果提供商为您提供用户名和密码，请使用 **注册 (registration)** 中继。如果他们要求您的 IP 地址并给您他们的 IP，请使用 **标识 (identify)** 中继。有些提供商两者都支持；许多真实的中继结合了注册（以便提供商能找到您）和标识（以便来自提供商媒体网关的入站 INVITE 即使在它们从非注册服务器的 IP 到达时也能被匹配）。

## 入站路由和 DID 处理

一旦入站呼叫到达，它们会落入 endpoint 的 `context`——此处为 `from-pstn`。**DID**（直接拨入号码）只是提供商在请求 URI 中交给您的拨入号码。您在 dialplan 中的工作是将每个 DID 映射到目的地：单个 extension、IVR、队列或振铃组。

提供商发送的号码在 `from-pstn` 中作为 `${EXTEN}` 进行匹配。您能看到多少取决于提供商——有些发送完整的 E.164 号码（`+4830001000`），有些发送国家/地区号码，有些只发送最后几位数字。在编写模式之前，使用 `pjsip set logger on` 检查真实的入站呼叫并查看请求 URI。

### 一个 DID 到一个 extension

最简单的情况——单个 DID 直接路由到一部电话：

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### 一个 DID 到一个 IVR（自动总机）

一个应该以菜单应答而不是响铃电话的主号码：

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` 是您在 dialplan 章节中构建的自动总机 context（`Background()` + `WaitExten()`）。路由 DID 只是一个 `Goto`。

### 一个 DID 到一个队列

应该进入呼叫队列的支持热线：

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### 同时处理多个 DID

当您购买了一组号码时，模式可以保持 dialplan 的简洁。假设您的 DID 范围是 `4830003000`–`4830003099`，且提供商发送完整号码；将每个 DID 的最后两位映射到 extension `60xx`：

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` 取最后两位数字（负偏移量从右侧开始计数），因此 `4830003007` 会振铃 `PJSIP/6007`。使用 `GoSub` 或 Asterisk 数据库（`AstDB`/`func_odbc`）构建的 `did => extension` 查找表可以进一步扩展，但对于少数号码，显式模式是最清晰的。

> **捕获未匹配的 DID。** 向 `from-pstn` 添加一个 `i` (invalid) extension，这样路由错误的入站号码会播放公告或呼叫接线员，而不是静默丢弃：
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## 出站路由、主叫号码和 E.164

出站呼叫的流程相反：内部电话拨打号码，您的 dialplan 匹配它，剥离任何访问前缀，设置提供商期望的主叫号码，并使用 `Dial(PJSIP/<number>@itsp)` 将呼叫交给中继 endpoint。

### 将呼叫发送到中继

中继的通道语法是 `PJSIP/<number>@<endpoint>`：`@` 之前的部分成为出站请求 URI 的用户部分，`@` 之后的部分命名其 `aor` `contact` 提供目标主机的 endpoint。一个经典的“拨 9 拨打外线”规则：

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` 在发送号码之前剥离前导的 `9` 访问码。模式 `_9NXXXXXXXXX` 匹配 `9` 加上一个首位为 2–9 的 10 位数字；请根据您的拨号方案进行调整。

### 出站呼叫上的主叫号码

大多数 ITSP 会忽略——或主动拒绝——非您拥有的主叫号码。在 `Dial()` 之前，使用 `CALLERID(num)` 函数将出站主叫号码设置为您的 DID 之一，如上所示。您还可以设置名称：

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

如果提供商仍然剥离或覆盖您的主叫号码名称，那是他们的策略——许多运营商根据号码从他们自己的 CNAM 数据库中获取显示的名称，而不是从您的 `From` 头部获取。

两个 endpoint 选项与此交互：

- **`from_user`** 在 SIP 层设置 `From` 头部，一些提供商使用它来识别您的账户，而不管 `CALLERID(num)` 如何。
- **`trust_id_outbound`**（默认 `no`）控制 Asterisk 是否发送隐私敏感的身份头部（`P-Asserted-Identity`/`P-Preferred-Identity`）。除非您的提供商明确要求 PAI，否则请保持关闭，如果需要，请设置 `trust_id_outbound=yes` 和 `send_pai=yes`。

### 规范化为 E.164

E.164 是国际号码格式：前导 `+`、国家代码，然后是国家/地区号码，没有空格或标点符号（例如 `+5548999990000` 或 `+14155550100`）。运营商越来越期望——或要求——中继上使用 E.164。与其将格式化分散在 dialplan 中，不如在出站 context 中统一规范化。

一个北美示例，它接受 10 位本地号码、11 位 `1` 前缀号码或已经是 E.164 的号码，并始终向中继呈现 `+1…`：

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

有些提供商需要 `+`；有些则需要纯数字。如果您的提供商拒绝 `+`，请在 `Dial` 中使用 `${EXTEN:1}` 将其剥离。重点是所有格式知识都集中在一个地方，因此切换提供商——或添加第二个提供商——只需修改一行代码。

## 故障转移和最低成本路由

只有一个中继时，提供商中断意味着无法拨打出站呼叫。拥有两个或更多中继时，您可以自动进行故障转移，甚至可以根据目的地选择最便宜的路由——*最低成本路由* (LCR)。

### 使用 `${DIALSTATUS}` 进行故障转移

`Dial()` 在返回时设置 `${DIALSTATUS}` 通道变量。您在故障转移中关心的值是 `CHANUNAVAIL`（根本无法到达中继）和 `CONGESTION`（呼叫被拒绝，例如所有电路忙）。尝试主中继；如果它无法承载呼叫，则回退到备份：

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

请注意，我们特意选择**不**在 `BUSY` 或 `NOANSWER` 上进行故障转移——这些意味着*被叫方*已收到呼叫并拒绝了，因此在另一个中继上重试会再次拨打一个已经拒绝的电话（并且可能会导致您产生第二次呼叫费用）。仅在*中继本身*失败时才重新路由。

### 可重用的路由子程序

为每个拨号模式重复该逻辑很容易出错。将其封装到一个 `GoSub` 子程序中，该子程序接收目标号码并按顺序尝试每个中继：

```
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

现在每个出站模式只需一个 `GoSub` 调用，且中继顺序定义在一个地方。

### 按目的地进行最低成本路由

真正的 LCR 根据呼叫去向选择中继。一种常见的形式是匹配目的地前缀，并将每类呼叫发送到对其最便宜的提供商——例如，国际长途呼叫发送到批发运营商，本地/国内呼叫发送到您的主运营商：

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

对于超过几个前缀的情况，请将路由表存储在数据库（`func_odbc`/`AstDB`）中，并按前缀查找中继，而不是硬编码模式。Dialplan 保持精简，费率存储在您可以编辑而无需重新加载逻辑的表中。

## NAT 和中继

NAT 是导致中继问题的最常见原因——通常表现为单向音频，或者中继注册成功但从未收到入站呼叫。原因与电话相同（在《SIP & PJSIP in depth》和《Designing a VoIP network》中介绍）：Asterisk 在 SIP 和 SDP 中通告其自身的地址，而在 NAT 之后，这是一个提供商无法路由回的私有 RFC 1918 地址。

对于中继，修复有两个部分——**传输层 (transport)** 设置（您的公网地址）和 **endpoint** 设置（如何处理提供商的媒体）。

### 在传输层上——您的公网地址

当 Asterisk 服务器本身位于 NAT 之后（具有私有 IP 和 1:1 公网 IP 的云端或本地盒子）时，请告知传输层其公网地址以及哪些网络是本地的。这些选项在 `transport` 上设置一次，并应用于其上的所有流量：

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** —— Asterisk 为 `local_net` 之外的目的地写入 SIP 头部（`Via`、`Contact`）的公网 IP。
- **`external_media_address`** —— Asterisk 写入 SDP `c=` 行的公网 IP，以便 RTP 返回到正确的位置。通常与信令地址相同。
- **`local_net`** —— Asterisk 视为内部的网络，因此它*不会*为 LAN 对等方重写地址。列出每个内部子网。

### 在 endpoint 上——提供商的媒体

另一半处理本身位于 NAT 之后的提供商，或者仅仅是从其 SDP 中声明的地址以外的地址发送媒体的情况。请按中继 endpoint 设置这些选项：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** —— 让媒体流经 Asterisk，而不是让两个端点直接通话。在 NAT 环境下必不可少，如果您想录音、转码或监控呼叫，也需要此项。
- **`rtp_symmetric=yes`** —— 经典的 *comedia* 行为：将 RTP 发送回媒体实际来源的地址，而不是 SDP 声称的地址。
- **`force_rport=yes`** —— 回复请求的源 IP/端口（RFC 3581），而不是信任 `Via` 头部。
- **`rewrite_contact=yes`** —— 在来自此 endpoint 的入站 SIP 消息上，将 `Contact` 头部（或适当的 `Record-Route` 头部）重写为数据包实际来源的源 IP 地址和端口。根据该选项的文档，这“有助于服务器与位于 NAT 之后的 endpoint 通信”，并“有助于重用可靠的传输连接，如 TCP 和 TLS”。

> **建议——电话 vs 中继。** `rewrite_contact` 几乎总是电话的正确选择，因为它们通告的联系地址通常是无法路由回的私有 RFC 1918 地址。在基于静态 IP 的中继上，提供商的联系地址通常已经是正确的公网地址，因此重写它通常是不必要的；一些运营商更喜欢在那里将其关闭，仅对注册中继和 NAT 后的电话启用。该选项记录的效果仅是上述入站 `Contact`/`Record-Route` 重写——因此，安全的做法是在静态中继上开启之前，先针对您的特定运营商进行测试。

您可以使用 `pjsip show endpoint <name>` 确认任何 endpoint 上的有效设置——`direct_media`、`rtp_symmetric`、`force_rport`、`rewrite_contact` 以及其余参数都会在转储中打印出来。

## 实验——使用第二个 Asterisk 和 SIPp 模拟 ITSP

您不需要付费中继即可练习。本书的实验环境已经在私有 `172.30.0.0/24` 网络上运行了一个 Asterisk 22.10.0 容器和一个 SIPp 容器；我们将把 SIPp 容器视为发起入站呼叫的“运营商”，并添加一个将这些呼叫落地到 `from-pstn` context 的中继 endpoint。

![Asterisk PBX 与 ITSP 之间的 SIP trunk：PBX 注册为一个账户，出站呼叫拨打 `PJSIP/<num>@trunk`，入站呼叫落入 `from-pstn` context。](../images/09-sip-trunking-fig01.png)

### 1. 添加中继 endpoint

向 `lab/asterisk/etc/pjsip.conf` 添加一个基于 IP 的中继，匹配实验环境的 SIPp 主机并将入站呼叫落地到 `from-pstn`：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. 路由入站 DID

在 `lab/asterisk/etc/extensions.conf` 中，添加一个 `from-pstn` context，应答模拟运营商将拨打的 DID 并回放，然后添加一条出站规则：

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

重新加载两个文件（`core reload`）并验证中继已加载：

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. 跨中继拨打入站呼叫

将 SIPp 场景指向 PBX，并将 DID 作为目标用户。实验环境已经附带了 `lab/sipp/uac_9000.xml`，它会 INVITE extension `9000`；将其复制到 `uac_did.xml` 并将请求 URI/`To` 用户从 `9000` 更改为 `4830001000`，然后从 SIPp 容器运行它：

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

观察呼叫到达 Asterisk 控制台上的 `from-pstn`（`pjsip set logger on` 显示入站 INVITE；`core show channels` 显示 `PJSIP/itsp-…` 通道正在播放 `demo-congrats`）。因为 SIPp 源 IP 匹配 `identify`，所以呼叫无需认证即可被接受——这正是静态运营商中继的行为方式。

### 4. 检查中继

捕获中继的完整配置以备记录：

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5.（进阶）将其设为注册中继

将*第二个* Asterisk 容器作为真实的注册服务器启动：为账户 `4830001000` 提供一个 `endpoint`+`auth`+`aor`，然后在 PBX 上将 `identify` 块替换为本章开头的 `registration` 块（将 `server_uri` 指向第二个容器的 IP）。使用 `pjsip show registrations` 确认状态显示为 `Registered`，然后双向拨打呼叫。

## 总结

SIP trunk 将您的 PBX 连接到外部世界，在 PJSIP 中，它只是一个由您已经熟悉的 `endpoint` + `auth` + `aor` 系列构建的 endpoint，外加一个 `identify` 或 `registration`。当提供商为您提供用户名和密码时，使用 **注册中继**（`type=registration` 配合 `outbound_auth`）；当通过源 IP 进行认证时，使用 **基于 IP 的中继**（`type=identify` 配合 `match`）——并使用严格的 `match` 和 `acl` 将后者锁定，因为未经认证的中继是电信欺诈的目标。入站时，提供商的 DID 作为 `${EXTEN}` 到达您的 `from-pstn` context，您可以在那里将其路由到 extension、IVR 或队列——模式和 `${EXTEN:-N}` 可以保持 DID 块的紧凑。出站时，将 `CALLERID(num)` 设置为您拥有的号码，在一个地方规范化为 E.164，并将呼叫交给 `PJSIP/<number>@trunk`。通过尝试多个中继并根据 `${DIALSTATUS}` 进行分支来构建弹性（`CHANUNAVAIL`/`CONGESTION` 表示重新路由；`BUSY`/`NOANSWER` 则不），并将最低成本路由放入 `GoSub` 表中。最后，中继的 NAT 是双向的：在 **传输层** 上设置 `external_media_address`/`external_signaling_address`/`local_net` 以获取您的公网地址，并在 **endpoint** 上设置 `direct_media=no`、`rtp_symmetric`、`force_rport` 和 `rewrite_contact` 以处理提供商的媒体。

## 测验

1. 在 PJSIP 中，用于认证到提供商的*出站*呼叫或注册的凭据通过以下方式引用：
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. 您应该在以下情况使用 `type=registration` 中继：
   - A. 提供商通过您的源 IP 地址识别您。
   - B. 提供商为您提供用户名和密码，并期望您登录。
   - C. 您从不希望 Asterisk 发送 `REGISTER`。
   - D. 中继位于您控制的两个静态 IP 服务器之间。
3. `identify` 对象的 `match` 选项接受（选择所有适用项）：
   - A. IP 地址
   - B. CIDR 范围
   - C. 主机名（在配置加载时解析）
   - D. 仅 SIP 用户名
4. 在 Asterisk 22 上，`auth_type=userpass` 是：
   - A. 唯一有效值
   - B. 已弃用并转换为 `digest`
   - C. 已移除并导致加载错误
   - D. 出站注册所必需的
5. 入站 DID 号码在 dialplan 中作为以下内容到达：
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}`，位于中继 endpoint 的 `context` 中
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. 要将拨入 DID `4830003007` 的最后两位数字发送到 extension，您将使用：
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. 在 `Dial()` 到中继后，您应该在哪些 `${DIALSTATUS}` 值上故障转移到备份中继（选择两个）？
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. 要在拨出之前设置呈现给提供商的主叫号码，请使用：
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. 当服务器位于 NAT 之后时，告知 Asterisk 其*公网*地址的选项设置在：
   - A. `endpoint`
   - B. `aor`
   - C. `transport`（`external_media_address` / `external_signaling_address`）
   - D. `registration`
10. 中继 endpoint 上的 `rtp_symmetric=yes` 会导致 Asterisk：
    - A. 使用 SRTP 加密 RTP
    - B. 将 RTP 发送回媒体实际到达的地址，忽略 SDP
    - C. 完全禁用 RTP
    - D. 强制 endpoint 之间直接媒体

**答案：** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
