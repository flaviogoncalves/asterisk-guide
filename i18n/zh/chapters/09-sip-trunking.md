# SIP trunking, DID & the PSTN

一个只能给自己打电话的 PBX 并不是很有用。迟早每个系统都必须能够联系到外部世界——公共交换电话网络（PSTN）、SIP 提供商或其他 PBX。承载这些通话的链接称为 **trunk**。在 TDM 时代，trunk 是一条物理电路：T1/E1 PRI 或一束模拟 FXO 线路。如今它几乎总是 **SIP trunk**——一种逻辑连接，连接到互联网电话服务提供商（ITSP），并通过与其他所有流量相同的 IP 网络传输。

本章展示了如何使用 PJSIP 将 Asterisk 22 连接到 ITSP，如何在基于注册的 trunk 与基于 IP 的 trunk 之间进行选择，如何将入站 DID 号码路由到正确的目的地，如何使用正确的 caller-ID 和 E.164 格式发送出站呼叫，以及如何在多个 trunk 之间构建故障转移和最低费用路由。我们还将介绍 trunk 的 NAT 处理，并提供一个实验，搭建第二个 Asterisk（以及 SIPp）作为模拟 ITSP，以便你能够通过 trunk 进行真实通话。

这里的所有内容均已在本书的 Asterisk 22.10.0 实验中验证；trunk 对象模式与 *Building your first PBX with PJSIP* 和 *SIP & PJSIP in depth* 中介绍的相同。

## 目标

通过本章学习，您应该能够：

- 将 Asterisk 22 连接到使用 PJSIP 的 ITSP
- 在基于注册的和基于 IP（静态）的中继之间进行选择
- 将入站 DID 路由到正确的分机、IVR 或队列
- 使用正确的来电显示号码和 E.164 格式路由出站呼叫
- 使用 `${DIALSTATUS}` 构建中继故障转移和最小费用路由
- 在传输层和端点上处理中继的 NAT

## What is a SIP trunk

A SIP trunk is a logical voice path between your PBX and another SIP system. In
practice that "other system" is one of two things:

- **An ITSP (Internet Telephony Service Provider).** A commercial carrier that
  sells you call origination and termination and, usually, a block of phone
  numbers (DIDs). You point Asterisk at the provider's signalling host, and the
  provider connects your calls to the wider PSTN. This is how most modern systems
  reach the phone network — no telephony hardware required.
- **A PSTN gateway.** A device (or another Asterisk) that has physical PSTN
  interfaces — a PRI card, analog FXO ports, or a GSM/4G gateway — and presents
  them to your PBX as SIP. The gateway does the TDM-to-SIP conversion; from
  Asterisk's point of view it is just another SIP trunk.

Either way, in PJSIP a trunk is **just an endpoint**. The same object family you
used for a phone — `endpoint`, `auth`, `aor`, optionally `identify` and
`registration` — builds a trunk. The differences are in the details: a trunk
authenticates *outbound* (you are the client, so credentials go in
`outbound_auth`, not `auth`), it usually does not register a user agent to you
(you register to *it*, or it sends you traffic from a known IP), and it lands
inbound calls in a dedicated context such as `from-pstn` instead of
`from-internal`.

> **Compared with the old TDM trunk.** A PRI gave you a fixed number of B-channels
> (23 on a T1, 30 on an E1) and signalled call setup over a dedicated D-channel
> (see the *Legacy channels* chapter). A SIP trunk has no fixed channel count —
> capacity is whatever your bandwidth, your provider's policy, and any
> `max_contacts`/concurrent-call limits allow. Caller-ID, DID, and call progress
> that used to ride ISDN information elements now ride SIP headers and SDP.

There are two ways an ITSP will agree to exchange traffic with you, and they
determine how you build the trunk: **registration-based** and **IP-based
(static)**. We cover each in turn.

## 基于注册的中继

基于注册的中继是当提供商期望*您*登录*他们*时使用的模型。您的 Asterisk 定期向提供商发送 SIP `REGISTER`进行身份验证，使用用户名和密码，方式与电话向您的 PBX 注册完全相同。当您的公网 IP 为动态、您位于 NAT 后面，或提供商仅通过 SIP 凭证而非 IP 地址识别客户时，这种方式很常见。

在 PJSIP 中，出站登录位于专用的 `registration` 对象中。它取代了已移除的 `chan_sip` 驱动在 `sip.conf` 中使用的单行 `register =>`。下面是一个完整的向虚构提供商注册的中继示例，遵循前面章节验证过的模式——注意 `outbound_auth`（而非 `auth`），`server_uri`/`client_uri`（而非 `server`/`client`），端点上的 `from_user`/`from_domain`以及 `dtmf_mode=rfc4733`：

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

- **`auth_type=digest`，而非 `userpass`。** 两者产生相同的摘要认证，但在 Asterisk 22 中 `userpass`（以及旧的 `md5`）已 **不推荐使用并被静默转换为 `digest`**。在新配置中请使用 `digest`；在较旧的文件和本书前面的章节中仍会看到 `userpass`。
- **在端点和注册上都使用 `outbound_auth`。** 注册使用它来验证 `REGISTER`；端点使用它来响应提供商返回给出站 `INVITE` 的 `407 Proxy Authentication Required`。它们可以共享同一个 `auth` 对象。
- **`from_user` / `from_domain`。** 许多提供商会拒绝那些在 `From` 头部未携带您的账号和其域名的呼叫。这两个选项正是用于设置这些信息。
- **`contact_user=4830001000`。** 这将成为您注册的 `Contact` 的用户部分，使提供商知道将入站呼叫送达哪个号码。它相当于旧 `register =>` 行上 `/9999` 后缀的现代写法。
- **`retry_interval=60`。** 如果注册失败，则每 60 秒重试一次。

重新加载后，使用 `pjsip show registrations` 确认注册状态。在实验室环境——因为 `itsp.example.com` 实际上并未应答——表格显示如下：

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

`(exp. Ns)` 后缀会倒计时至下一次尝试；一旦倒计时到零，它会短暂显示 `(exp. Ns ago)` 然后触发重试。对真实提供商而言，`Status` 列会显示 `Registered`，以及距下一次刷新剩余的秒数。 `Rejected`（或 `Unregistered`）表示提供商未接受登录——打开 `pjsip set logger on` 并读取 `401`/`403` 回复，几乎总是用户名、密码错误或 `client_uri` 域名错误。

## IP-based (static) trunks

第二种模型根本不需要注册。提供商知道你的公网 IP 地址，并直接向其发送呼叫；而你则向提供商已知的信令 IP 发送呼叫。认证方式是**源 IP 地址**，而不是 SIP 凭证。这通常用于你控制的两台服务器之间的中继，或双方都有静态地址的企业中继。

关键对象是 `identify`。它告诉 Asterisk：“任何来自*此* IP 的 SIP 请求都属于*该*端点。”如果没有它，PJSIP 会尝试通过 `From` 用户来匹配入站请求，而运营商的流量通常不满足这一条件——于是呼叫会被拒绝或落到 `anonymous` 端点。

静态中继会去掉 `registration` 对象并添加 `identify`：

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

`match` 接受 IP 地址、CIDR 范围或主机名。**主机名在配置加载时解析一次**，因此如果提供商的 IP 发生变化，你必须重新加载。对于发布多个媒体网关的运营商，列出每个信令 IP——你可以重复使用 `match` 或给出一个 CIDR：

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

使用 `pjsip show identifies` 验证 Asterisk 将接受的内容。以下摘自实验室（`sipp-identify` 行是实验室预先存在的 SIPp 端点）：

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

### The security implication

基于 IP 且没有认证的中继相当于一扇门，而 `identify`/`match` 是唯一的锁。如果你 `match` 的范围过宽——或者攻击者能够伪造源 IP——呼叫会在你的 `from-pstn` 上下文中未经认证地进入。两种防御措施，需同时使用：

- **尽可能精确匹配。** 优先使用具体的主机 IP 而不是宽泛的 CIDR。只有提供商真实的信令 IP 才应出现在 `match` 中。
- **配合 ACL 使用。** PJSIP 可以在 SIP 层面丢弃流量，在它到达任何端点之前使用 `type=acl` 对象（或 `acl.conf`）：

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

一个 `type=acl` 部分不需要引用：`res_pjsip_acl` 会在所有入站 SIP 流量到达任何端点之前，对每个此类对象应用 *全部*。 (对象上的 `acl` 和 `contact_acl` 选项会从 `acl.conf` 中拉取已命名的规则列表，而不是像上面那样内联列出 `permit`/`deny`)。其原理与 SIP 章节相同：先拒绝所有，然后只允许你信任的流量。而且无论你的中继上下文做什么，**绝不要让它在没有明确、已认证规则的情况下进入能够拨回 PSTN 的上下文**——这就是经典的计费欺诈漏洞。

> **Which model should I use?** 如果提供商给你用户名和密码，使用**registration** 中继。如果他们要求你的 IP 地址并提供他们的 IP，使用**identify** 中继。一些提供商同时支持两者；许多真实的中继会将 registration（让提供商能够找到你）与 identify（即使来自非注册器的 IP，也能匹配提供商媒体网关的 inbound INVITE）结合使用。

## Inbound routing and DID handling

一旦入站呼叫到达，它们会落在端点的 `context` —— 在这里 `from-pstn`。**DID**（直拨号码）只是提供商在请求 URI 中交给你的被拨号码。你在 dialplan 中的工作是将每个 DID 映射到一个目的地：单个分机、IVR、队列或振铃组。

提供商发送的号码在 `from-pstn` 中作为 `${EXTEN}` 进行匹配。你能看到多少取决于提供商——有的发送完整的 E.164 号码（`+4830001000`），有的发送国内号码，有的只发送最后几位数字。使用 `pjsip set logger on` 检查真实的入站呼叫，并在编写模式之前查看请求 URI。

### One DID to one extension

最简单的情况——单个 DID 直接路由到一部电话：

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### One DID to an IVR (auto attendant)

一个主号码应答时提供菜单而不是响铃：

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` 是你在 dialplan 章节（`Background()` + `WaitExten()`）中构建的自动接线员上下文。将 DID 路由过去只需一个 `Goto`。

### One DID to a queue

一个支持线路应进入呼叫队列：

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Many DIDs at once

当你购买一整块号码时，使用模式可以保持 dialplan 简洁。假设你的 DID 范围是 `4830003000`–`4830003099` 且提供商发送完整号码；将每个 DID 的后两位映射到分机 `60xx`：

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` 取出后两位（负偏移从右侧计数），因此 `4830003007` 响铃 `PJSIP/6007`。使用 `GoSub` 或 Asterisk 数据库（`AstDB`/`func_odbc`）构建的 `did => extension` 查找表可以进一步扩展，但对于少量号码，显式模式是最清晰的。

> **Catch the unmatched DID.** 添加一个 `i`（无效）分机到 `from-pstn` 以便当入站号码路由错误时，播放提示音或响铃给操作员，而不是静默掉线：
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## 出站路由、来电显示和 E.164

出站呼叫的流程相反：内部电话拨打一个号码，您的 dialplan
匹配它，去除任何接入前缀，设置提供商期望的来电显示，并
将呼叫交给带有 `Dial(PJSIP/<number>@itsp)` 的 trunk endpoint。

### 将呼叫发送到 trunk

trunk 的通道语法是 `PJSIP/<number>@<endpoint>`：`@` 前的部分
成为出站请求 URI 的用户部分，`@` 后的部分
指定其 `aor` `contact` 提供目标主机的 endpoint。一个经典的 “拨 9 以获取外线” 规则：

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` 在号码发送之前去除前导的 `9` 接入码。模式 `_9NXXXXXXXXX` 匹配 `9` 加上一个首位为
2–9 的 10 位号码；根据您的 dialplan 进行调整。

### 出站呼叫的来电显示

大多数 ITSP 会忽略——或主动拒绝——您不拥有的来电显示号码。
在 `Dial()` 之前使用 `CALLERID(num)` 函数将出站来电显示号码设置为您的某个 DID，如上所示。您也可以设置名称：

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

如果提供商仍然去除或覆盖您的来电显示名称，那是他们的
策略——许多运营商从其自己的 CNAM 数据库中根据号码获取显示名称，而不是从您的 `From` 头部获取。

两个 endpoint 选项与此相关：

- **`from_user`** 在 SIP 级别设置 `From` 头部的用户部分，
  某些提供商使用它来识别您的账户，而不管 `CALLERID(num)`。
- **`trust_id_outbound`**（默认 `no`）控制 Asterisk 是否会发送
  隐私敏感的身份头部（`P-Asserted-Identity`/`P-Preferred-Identity`）
  出站。除非您的提供商文档说明他们需要 PAI，否则保持关闭，
  如需开启请设置 `trust_id_outbound=yes` 和 `send_pai=yes`。

### 规范化为 E.164

E.164 是国际号码格式：一个前导的 `+`、国家代码，然后是
国内号码，不含空格或标点（例如 `+5548999990000` 或
`+14155550100`）。运营商越来越多地期望——或要求——在 trunk 上使用 E.164。
与其在 dialplan 中到处散布格式化，不如在出站
context 中一次性规范化。

一个接受 10 位本地号码、带有 11 位 `1` 前缀的号码，或已经是 E.164 号码，并始终向
trunk 提供 `+1…` 的北美示例：

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

有些提供商需要 `+`；其他则需要纯数字。如果您的提供商拒绝 `+`，
可以在 `Dial` 中使用 `${EXTEN:1}` 将其去除。关键是所有格式知识都集中在一个位置，这样切换提供商——或添加第二个——只需一行修改。

## Failover and least-cost routing

With one trunk, a provider outage means no outbound calls. With two or more, you
can fail over automatically and even pick the cheapest route per destination —
*least-cost routing* (LCR).

### Failover with `${DIALSTATUS}`

`Dial()` sets the `${DIALSTATUS}` channel variable when it returns. The values you
care about for failover are `CHANUNAVAIL` (the trunk could not be reached at all)
and `CONGESTION` (the call was rejected, e.g. all circuits busy). Try the primary
trunk; if it could not carry the call, fall through to the backup:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Note the deliberate choice **not** to fail over on `BUSY` or `NOANSWER` — those
mean the *called party* was reached and declined, so retrying on another trunk
would re-ring a phone that already said no (and could cost you a second call).
Only re-route when the *trunk itself* failed.

### A reusable routing subroutine

Repeating that logic for every dial pattern is error-prone. Factor it into a
`GoSub` routine that takes the destination number and tries each trunk in order:

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

Now every outbound pattern is one `GoSub` call, and the trunk order is defined in
exactly one place.

### Least-cost routing by destination

True LCR chooses the trunk by where the call is going. A common shape is to match
the destination prefix and send each class of call to the provider that is
cheapest for it — for example, international calls to a wholesale carrier and
local/national calls to your primary:

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

For more than a few prefixes, store the route table in a database
(`func_odbc`/`AstDB`) and look the trunk up by prefix instead of hard-coding
patterns. The dialplan stays small and the rates live in a table you can edit
without reloading logic.

## NAT and trunks

NAT 是导致 trunk 问题的最常见原因——通常表现为单向音频，或 trunk 能注册却从未收到入站呼叫。原因与电话相同（见 *SIP & PJSIP in depth* 和 *Designing a VoIP network*）：Asterisk 在 SIP 和 SDP 中公布了它自己的地址，而在 NAT 后面，这个地址是提供商无法回路的私有 RFC 1918 地址。

对于 trunk，解决方案分为两部分——**transport**（你的公网地址）的设置和 **endpoint**（如何处理提供商媒体）的设置。

### On the transport — your public address

当 Asterisk 服务器本身位于 NAT 后（云或本地机箱，拥有私有 IP 和 1:1 公网 IP）时，需要告诉 transport 其公网地址以及哪些网络是本地的。这些选项在 `transport` 上设置一次，适用于所有经过它的流量：

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

- **`external_signaling_address`** — Asterisk 在 SIP 头部（`Via`、`Contact`）中写入的公网 IP，用于 `local_net` 之外的目的地。
- **`external_media_address`** — Asterisk 在 SDP `c=` 行中写入的公网 IP，以便 RTP 回到正确的位置。通常与信令地址相同。
- **`local_net`** — Asterisk 将视为内部的网络，因此不会为 LAN 对等体重写地址。列出所有内部子网。

### On the endpoint — the provider's media

另一半处理的是提供商本身位于 NAT 后，或仅仅从其 SDP 中的地址之外发送媒体的情况。对每个 trunk endpoint 进行如下设置：

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

- **`direct_media=no`** — 保持媒体通过 Asterisk 传输，而不是让两端直接通话。跨 NAT 时必不可少，并且如果你想录音、转码或监控通话，也必须如此。
- **`rtp_symmetric=yes`** — 经典的 *comedia* 行为：将 RTP 发送回实际收到媒体的地址，而不是 SDP 声称的地址。
- **`force_rport=yes`** — 从请求的源 IP/端口回复 SIP（RFC 3581），而不是信任 `Via` 头部。
- **`rewrite_contact=yes`** — 对来自该 endpoint 的入站 SIP 消息，重写 `Contact` 头部（或相应的 `Record-Route` 头部）为数据包真实来源的 IP 地址和端口。根据该选项的文档，这“帮助服务器与位于 NAT 后的端点通信”，并且“帮助复用可靠的传输连接，如 TCP 和 TLS”。

> **Recommendation — phones vs trunks.** `rewrite_contact` 几乎总是手机的正确选择，因为它们公布的 contact 通常是不可路由回去的私有 RFC 1918 地址。对于基于静态 IP 的 trunk，提供商的 contact 通常已经是正确的公网地址，因此重写往往没有必要；一些运营商倾向于在注册 trunk 和 NAT 设备的手机上启用，而在静态 trunk 上关闭。该选项的文档效果仅是上述入站 `Contact`/`Record-Route` 重写——因此在对静态 trunk 启用之前，最好先在你的具体运营商环境中进行测试。

你可以使用 `pjsip show endpoint <name>` — `direct_media`、`rtp_symmetric`、`force_rport`、`rewrite_contact` 等命令确认任何 endpoint 的实际设置，剩余参数均在参数转储中打印。

## Lab — a mock ITSP with a second Asterisk and SIPp

You do not need a paid trunk to practise. The book's lab already runs an Asterisk
22.10.0 container and a SIPp container on a private `172.30.0.0/24` network; we
will treat the SIPp container as the "carrier" placing inbound calls, and add a
trunk endpoint that lands those calls in a `from-pstn` context.

![A SIP trunk between the Asterisk PBX and the ITSP: the PBX registers as one account, outbound calls dial `PJSIP/<num>@trunk`, and inbound calls land in the `from-pstn` context.](../images/09-sip-trunking-fig01.png)

### 1. Add the trunk endpoint

Add an IP-based trunk to `lab/asterisk/etc/pjsip.conf` that matches the lab's SIPp
host and lands inbound calls in `from-pstn`:

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

### 2. Route the inbound DID

In `lab/asterisk/etc/extensions.conf`, add a `from-pstn` context that answers the
DID the mock carrier will dial and plays it back, then add an outbound rule:

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

Reload both files (`core reload`) and verify the trunk loaded:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Place an inbound call across the trunk

Point a SIPp scenario at the PBX with the DID as the target user. The lab already
ships `lab/sipp/uac_9000.xml`, which INVITEs extension `9000`; copy it to
`uac_did.xml` and change the request-URI/`To` user from `9000` to `4830001000`,
then run it from the SIPp container:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Watch the call hit `from-pstn` on the Asterisk console (`pjsip set logger on`
shows the inbound INVITE; `core show channels` shows the `PJSIP/itsp-…` channel
playing `demo-congrats`). Because the SIPp source IP matches the `identify`, the
call is accepted with no authentication — exactly how a static carrier trunk
behaves.

### 4. Inspect the trunk

Capture the trunk's full configuration for your notes:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) make it a registration trunk

Stand up the *second* Asterisk container as a real registrar: give it an
`endpoint`+`auth`+`aor` for account `4830001000`, then on the PBX swap the
`identify` block for the `registration` block from the start of this chapter
(pointing `server_uri` at the second container's IP). Confirm with
`pjsip show registrations` that the status reads `Registered`, then place a call
in each direction.

## Summary

A SIP trunk connects your PBX to the outside world, and in PJSIP it is just an
endpoint built from the same `endpoint` + `auth` + `aor` family you already know,
plus an `identify` or a `registration`. Use a **registration trunk**
(`type=registration` with `outbound_auth`) when the provider gives you a username
and password; use an **IP-based trunk** (`type=identify` with `match`) when
authentication is by source IP — and lock the latter down with a narrow `match`
and an `acl`, because an unauthenticated trunk is a toll-fraud target. Inbound,
the provider's DID arrives as `${EXTEN}` in your `from-pstn` context, where you
route it to an extension, an IVR, or a queue — patterns and `${EXTEN:-N}` keep
DID blocks compact. Outbound, set `CALLERID(num)` to a number you own, normalize
to E.164 in one place, and hand the call to `PJSIP/<number>@trunk`. Build
resilience by trying multiple trunks and branching on `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` mean re-route; `BUSY`/`NOANSWER` do not), and put
least-cost routing in a `GoSub` table. Finally, NAT for trunks is two-sided:
`external_media_address`/`external_signaling_address`/`local_net` on the
**transport** for your public address, and `direct_media=no`, `rtp_symmetric`,
`force_rport`, and `rewrite_contact` on the **endpoint** for the provider's media.

## Quiz

1. 在 PJSIP 中，用于对 *outbound* 呼叫或向提供商注册进行身份验证的凭据引用为：
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. 当以下情况出现时，应使用 `type=registration` 中继：
   - A. 提供商通过您的源 IP 地址识别您。
   - B. 提供商给您一个用户名和密码，并期望您登录。
   - C. 您永不希望 Asterisk 发送 `REGISTER`。
   - D. 中继位于您控制的两台静态 IP 服务器之间。
3. `identify` 对象的 `match` 选项接受（请选择所有适用项）：
   - A. IP 地址
   - B. CIDR 范围
   - C. 主机名（在加载配置时解析）
   - D. 仅 SIP 用户名
4. 在 Asterisk 22 中，`auth_type=userpass`是：
   - A. 唯一有效的取值
   - B. 已废弃并转换为 `digest`
   - C. 已移除并导致加载错误
   - D. outbound 注册所必需的
5. 传入的 DID 号码在 dialplan 中表现为：
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` 在中继端点的 `context` 中
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. 若要将拨打的 DID `4830003007` 的后两位发送到一个分机，您应使用：
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. 在对中继进行 `Dial()` 后，您应切换到备份中继，并在其上设置 `${DIALSTATUS}` 值（请选择两个）？
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. 若要在拨出前设置向提供商呈现的来电号码（caller-ID），请使用：
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. 当服务器位于 NAT 后面时，告知 Asterisk 其 *public* 地址的选项设置在：
   - A. `endpoint`
   - B. `aor`
   - C. `transport`（`external_media_address` / `external_signaling_address`）
   - D. `registration`
10. 在中继端点上设置 `rtp_symmetric=yes` 会导致 Asterisk：
    - A. 使用 SRTP 加密 RTP
    - B. 将 RTP 发送回实际到达的地址，忽略 SDP
    - C. 完全禁用 RTP
    - D. 强制端点之间直接媒体

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
