# 使用 PJSIP 构建您的第一个 PBX

在本章中，您将学习如何执行基本的 Asterisk PBX 配置。这里的主要目标是让 PBX 首次运行，能够实现分机间拨号、拨打播放消息，以及拨打单个模拟或 SIP trunk。本章的宗旨是确保您的 Asterisk 能够尽快启动并运行。完成本章的工作后，您将具备足够的背景知识，为后续章节做好准备，届时我们将深入探讨配置细节。

## 目标

在本章结束时，您应该能够：

- 理解并编辑配置文件；
- 安装基于 SIP 的软电话；
- 安装并配置 SIP trunk；
- 安装并配置模拟连接；
- 在分机之间拨号；
- 在电话和外部目的地之间拨号；以及
- 配置自动总机。

## 理解配置文件

Asterisk 由位于 /etc/asterisk 中的文本配置文件控制。文件格式类似于 Windows 的“.ini”文件。分号用作注释字符，“=”和“=>”符号是等效的，空格会被忽略。

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk 以相同的方式解释“=”和“=>”。语法上的差异用于区分对象和变量。当您想要声明变量时使用“=”，而指定对象时使用“=>”。所有文件之间的语法相同，但使用了三种类型的语法，如下所述。

## 语法

| 语法 | 对象创建方式 | 配置文件 | 示例 |
|---------|---------------------------|------------|---------|
| 简单组 | 全部在同一行 | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| 选项继承 | 先定义选项，对象继承这些选项 | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| 复杂实体 | 每个实体接收一个 context | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### 简单组

extensions.conf、meetme.conf 和 voicemail.conf 中使用的简单组格式是最基本的语法。每个对象及其选项都在同一行中声明。示例：

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

在此示例中，对象 1 使用选项 op1、op2 和 op3 创建，而对象 2 使用选项 op1、op2 和 op3 创建。

### 对象选项继承语法

此格式由 chan_dahdi.conf 和 agents.conf 文件使用，其中有大量可用选项，且大多数接口和对象共享相同的选项。通常，一个或多个部分包含对象和通道声明。对象的选项在对象上方声明，并可以更改为另一个对象。虽然这个概念很难理解，但使用起来非常容易。示例：

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

前两行分别将选项 op1 和 op2 的值配置为“bas”和“adv”。当实例化对象 1 时，它使用选项 1 作为“bas”和选项 2 作为“adv”创建。定义对象 1 后，我们将选项 1 更改为“int”。接下来，我们创建对象 2，其选项 1 为“int”，选项 2 为“adv”。

### 复杂实体对象

此格式由 pjsip.conf、iax.conf 以及存在许多带有大量选项的实体的其他配置文件使用。通常，此格式不会共享大量通用配置。每个实体接收一个 context。有时存在保留的 context，例如用于全局配置的 [general]。选项在 context 声明中声明。示例：

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

实体 [entity1] 的选项 op1 和 op2 的值分别为“value1”和“value2”。实体 [entity2] 的选项 op1 和 op2 的值分别为“value3”和“value4”。

## 构建 Asterisk 实验室的选项

要配置 PBX，您需要一些基本硬件。这并不困难也不昂贵，但有一些选项需要考虑。您只需要两部电话和到公共网络的连接。在创建实验室时，有几种选项和组合是可能的，我们将在下面讨论。

### 选项 1：完整实验室

通过完整实验室，可以测试所有可用场景并比较 ATA、IP 电话和软电话等解决方案。您还可以了解模拟和 SIP trunk。您将需要：

- 一个 SIP 模拟电话适配器 (ATA)
- 一部 IP 电话
- 一台专用的 Asterisk 服务器
- 一台带有软电话的工作站
- 一块至少有两个接口（1 个 FXO 和 1 个 FXS）的模拟接口卡
- 一个 VoIP 提供商账户

### 选项 2：经济型实验室

通过经济型实验室，我们简化了一些。我们使用通常比 IP 电话便宜的 ATA，以及非常便宜的单 FXO 卡。我们将无法使用直接连接到服务器的模拟电话，但这在实践中并不常见。您将需要：

- 一个 SIP 模拟电话适配器 (ATA)
- 一台专用的 Asterisk 服务器
- 一台用于软电话的工作站
- 一块带有 1 个 FXO 的模拟接口卡
- 一个 VoIP 提供商账户

### 选项 3：超经济型实验室

第三个实验室在学生自己的笔记本电脑上使用虚拟化服务器。这种模式的问题在于 UDP 端口产生的冲突。有时 Asterisk 服务器和软电话都试图访问同一个端口，导致 Asterisk 无法绑定地址端口。另一个问题是通话质量；虚拟环境不适合实时应用，例如 Asterisk。为服务器和工作站使用免费的软电话，并使用到 SIP 提供商的 trunk 连接。您将需要：

- 一台运行软电话的笔记本电脑
- 一台用于安装 Asterisk 的虚拟机 (VirtualBox、VMware 或类似软件)
- 一个 VoIP 提供商账户

## 安装顺序

为了帮助您理解安装顺序，我们概述了安装和配置 Asterisk 所需的步骤序列。

![参考实验室布局：SIP/IAX 软电话、一部 IP 电话和作为分机的模拟适配器 (1)，带有 ETH0/FXO/FXS 接口的 Asterisk 服务器 (3)，以及通过 VoIP 提供商或宽带链路连接到 PSTN 的 trunk (2)。](../images/04-first-pbx-fig01.png)

1. 分机配置 a. SIP 分机 (ATA, 软电话, IP 电话) b. IAX 分机 c. FXS 分机 2. Trunk 配置 a. SIP trunk 配置 b. FXO trunk 配置 3. 构建基本 dialplan a. 分机间拨号 b. 拨打外部目的地 c. 从操作员分机接听电话 d. 在自动总机中接听电话

## 分机配置

分机是连接到 FXS 端口的 SIP、IAX 或模拟电话。要配置分机，您应该编辑与通道相关的配置文件 (pjsip.conf, iax.conf, chan_dahdi.conf)

### SIP 分机

在 Asterisk 22 上，PJSIP（`res_pjsip` 栈，在 `/etc/asterisk/pjsip.conf` 中配置）是 SIP 通道驱动程序。它支持每个 endpoint 多个传输，处于活跃维护状态，并且是平台附带的唯一 SIP 驱动程序。（原始的 `chan_sip` 驱动程序已在 Asterisk 21 中移除 — 如果您需要迁移旧配置，请参阅 *Legacy channels* 章节。）

这里的想法是配置一个简单的 PBX。（后续章节提供了完整的 SIP/PJSIP 会话以及所有细节。）PJSIP 在 `/etc/asterisk/pjsip.conf` 中配置，并包含与 SIP 电话和 VoIP 提供商相关的所有参数。必须先配置 SIP 客户端，然后才能拨打和接听电话。

#### 传输

在 PJSIP 中，监听器配置（绑定地址、端口、协议）位于 `transport` 对象中。Asterisk 具有针对用户名猜测的内置保护 — 它始终为未知和已知用户返回相同的身份验证质询，并且来自同一 IP 的重复未识别请求通过 `[global]` 选项 `unidentified_request_count`/`unidentified_request_period` 进行速率限制。传输的主要选项是：

- protocol: 传输协议 — `udp`, `tcp`, `tls`, `ws`, 或 `wss`。
- bind: 监听器绑定的地址和端口。如果您将地址设置为 `0.0.0.0`，它将绑定到所有接口；SIP 端口默认为 UDP/TCP 的 5060。

最小 UDP 传输：

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

编解码器选择 (`disallow`/`allow`) 和默认 `context` 在每个 `endpoint`（如下所示）上配置，而不是在传输上配置。匿名/访客呼叫由名为 `anonymous` 的 `endpoint` 处理。注册计时器通过 `maximum_expiration`/`default_expiration` 按 AOR 进行控制。

#### SIP 客户端

完成传输部分后，是时候设置 SIP 客户端了。我想再次提醒读者，我们稍后会在书中有一个完整的 SIP/PJSIP 章节。现在，让我们专注于基础知识，将细节留到以后。

在 PJSIP 中，SIP 客户端由一组相关的对象构建，并通过名称引用连接在一起：

- `endpoint`: 呼叫行为 — 编解码器 (`allow`/`disallow`)、dialplan `context`，以及它使用的 `auth` 和 `aors`。
- `auth`: 凭据。`username` 是 SIP 身份验证用户，`password` 是用于对设备进行身份验证的密钥。
- `aor`: "地址记录" (AOR) — 可以到达 endpoint 的位置。可以是静态 `contact=`（用于固定 IP 的设备），也可以是 `max_contacts=` 以允许设备动态注册。

警告：使用强密码，至少 8 个字符，包含字母数字和数字字符，并至少包含一个符号。邮件列表中出现了服务器被黑的报告，并且针对 SIP 的暴力破解密码工具很容易被脚本小子获取。电信欺诈给消费者和提供商造成了数千美元的损失。

Endpoint 6000 是固定 IP 上的设备，因此其 AOR 携带静态 `contact` 而不是允许注册。Endpoint 6001 是注册的设备，因此其 AOR 允许它注册 (`max_contacts=1`)：

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=userpass
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=userpass
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP 允许 `endpoint`、`auth` 和 `aor` 部分共享相同的节名称（例如上面的两个 `[6001]` 块，通过它们的 `type=` 区分）；许多管理员改为使用后缀（`[6001]`, `[6001-auth]`, `[6001]` aor）以提高可读性。对于注册的设备，联系人是在电话注册时动态学习的，因此 AOR 不需要静态 `contact`。

## IAX 分机

`chan_iax2` 仍然随 Asterisk 22 提供，但现在已是遗留协议；SIP/PJSIP 是新部署的首选协议。

您也可以创建 IAX 分机。此协议是 Asterisk 原生的，我们将在本书后面专门用一整节来介绍它。现在，让我们使用该协议创建几个分机。作为第一个要配置的部分，[general] 部分有一些参数需要配置。主要选项是：

- allow/disallow: 定义将使用哪些编解码器。
- bindaddr: 绑定到 Asterisk SIP 监听器的地址。如果您将其设置为 0.0.0.0（默认），它将绑定到所有接口。
- context: 为所有客户端设置默认 context，除非在客户端部分中更改。出于安全原因，我们使用了 dummy。当选项 allowguest 设置为 yes 时，未经身份验证的用户会进入此 context。
- bindport: 监听的 SIP UDP 端口。
- delayreject: 当设置为 yes 时，会延迟发送 REGREQ 或 AUTHREQ 的身份验证拒绝，这提高了针对暴力破解密码攻击的安全性。
- bandwidth: 当设置为 high 时，它允许选择高带宽编解码器，例如 g711 的 ulaw 和 alaw 变体。

以下是 iax.conf 文件中 [general] 部分的示例。

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### IAX 客户端

完成常规部分后，是时候设置 IAX 客户端了。

- [name]: 当 SIP 设备连接到 Asterisk 时，它使用 SIP URI 的用户名部分来查找 peer/user。
- type: 配置连接类。选项有 peer、user 和 friend。o peer: Asterisk 向 peer 发送呼叫。o user: Asterisk 从 user 接收呼叫。o friend: 两者同时发生。
- host: IP 地址或主机名。最常见的选项是 dynamic，用于主机注册到 Asterisk 时。
- secret: 用于验证 peer 和 user 的密码。

警告：使用强密码，至少 8 个字符，包含字母数字和数字字符，并至少包含一个符号。邮件列表中出现了服务器被黑的报告，并且针对 SIP md5 哈希的暴力破解密码工具可供脚本小子使用。电信欺诈给消费者和提供商造成了数千美元的损失。示例：

```
[guest]
type=user
context=dummy
callerid=”Guest IAX User”
[6003]
context=from-internal
type=friend
secret=#sup3rs3cr3t#
host=dynamic
context=from-internal
[6004]
context=from-internal
type=friend
secret=#s3cr3ts3cr3t#
host=dynamic
context=from-internal
```

## 配置 SIP 设备

在 Asterisk 配置文件中定义电话后，是时候配置电话本身了。在此示例中，我们将展示如何配置免费的软电话 — SipPulse Softphone（从 https://www.sippulse.com/produtos/softphone 下载）。检查您设备的说明书以了解您电话的参数。第 1 步：将电话配置为使用分机 6000。执行安装程序。执行后，打开账户/SIP 设置并添加一个新的 SIP 账户。填写所需信息。

![SipPulse Softphone 账户屏幕 — 输入服务器（您的 Asterisk IP 或域名）、用户名、密码和显示名称，然后选择传输（UDP、TCP 或 TLS）。](../images/softphone/sipphone-account.png){width=35%}

显示名称：6000 用户名：6000 密码：#MySecret1#7 授权用户名：6000 域名：ip_of_your_server。使用控制台命令 `pjsip show endpoints`（或 `pjsip show endpoint 6000` 查看详细信息；`pjsip show contacts` 显示已注册的 AOR 联系人）确认您的电话已注册。对电话 6001 重复此配置。

![已注册的 SipPulse Softphone — 绿点和账户行 (`1001@softphone.sippulse.com.br`) 确认注册；从键盘或呼叫/视频按钮拨打电话。](../images/softphone/sipphone-registered.png){width=35%}

## 配置 IAX 设备

IAX2 是一个遗留协议（请参阅 *Legacy channels* 章节），而 SipPulse Softphone 仅支持 SIP，因此它无法注册 IAX 账户。如果您需要测试 IAX2，请使用仍然支持它的软电话。创建一个新的 IAX 账户，

3. 选择新的 IAX 账户。 4. 插入 6003 电话的相关选项，并可选择为 6004 插入选项。 5. 保存配置并使用 iax2 show peers 检查电话是否已注册。重要：为 SIP 使用一个账户，为 IAX 使用另一个账户。如果您想将系统配置为同时响铃 IAX 和 SIP，我们将在 dialplan 部分向您展示如何操作。

### 配置 PSTN 接口

要连接到 PSTN，您需要一个外汇局 (FXO) 接口和一条电话线。您也可以使用现有的 PBX 分机。您可以从多家制造商处获得带有 FXO 接口的电话接口卡。在此示例中，我们将向您展示如何安装 DAHDI 接口卡。

![FXS 和 FXO 端口：FXS 端口驱动模拟电话（提供拨号音和振铃），而 FXO 端口将 Asterisk 连接到电信线路。](../images/04-first-pbx-fig02.png)

### 使用 DAHDI 的模拟线路

您可以从多家制造商处购买与 DAHDI 兼容的模拟卡。X100P 是 Digium 的首批卡之一，现已停产。一些制造商仍在生产类似的克隆产品。除了 X100P 的价格外，我们发现这些卡与新主板之间存在一些问题，因此请谨慎使用。在我看来，X100P 不是生产环境的理想选择。任何与 DAHDI 兼容的卡都应该可以工作。感谢 DAHDI 开发人员团队，我们现在有了一个几乎可以自动检测和配置接口卡的工具。如果您刚刚安装了 DAHDI 驱动程序，请不要忘记运行 make config 并重启机器以自动加载它。您可以使用以下命令来检测和配置您的卡。第 1 步：要检测您的硬件，请使用：

```
dahdi_hardware.
```

第 2 步：要配置，请使用：

```
dahdi_genconf.
```

上面的命令将生成两个文件 /etc/dahdi/system.conf 和 /etc/asterisk/dahdi-channels.conf。dahdi_genconf 的默认参数通常很好，但您可以在文件 /etc/dahdi/genconf_parameters 中更改它们。默认情况下，它会将线路 (FXO) 插入到 context from-pstn 中，并将电话 (FXS) 插入到 context from-internal 中。第 3 步：运行 dahdi_genconf 后，在文件 /etc/asterisk/chan_dahdi.conf 的最后一行插入以下行：

```
#include dahdi-channels.conf
```

第 4 步：编辑文件 /etc/dahdi/modules 并注释掉所有未使用的驱动程序。在继续之前重启，并使用以下命令检查通道是否被识别：

```
CLI>dahdi show channels
```

### 使用 VoIP 提供商连接到 PSTN

如果您的预算非常有限，您可以配置一个 SIP trunk 来连接到 PSTN。这无疑是连接到 PSTN 最经济实惠的方式。全球有成千上万的 VoIP 提供商。要连接到其中一个，您需要一些参数。SIP 提供商提供的参数。

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs:g729, ilbc, alaw

有两个参数应由您确定。

- 接听电话的分机 — 在这种情况下：9999
- context: from-sip

在 PJSIP 中，注册 SIP trunk 是由用于 endpoint 的相同对象系列构建的，外加显式的 `registration` 和 `identify` 对象。`registration` 对象告诉 Asterisk 注册到提供商，`identify` 对象将来自提供商 IP 的入站流量匹配到 endpoint（PJSIP 通过源 IP 对入站 INVITE 进行身份验证），而 `outbound_auth` 为出站呼叫和注册提供凭据：

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=userpass
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

要访问此 trunk，我们将使用通道名称 `PJSIP/siptrunk`。`dtmf_mode=rfc4733` 设置在带外携带 DTMF（RFC 4733 废弃了较旧的 RFC 2833；有效载荷相同）。`identify`/`match` 选项接受 IP 地址、CIDR 或主机名，但主机名仅在配置加载时解析一次，因此对于 IP 经常更改的提供商，请明确列出信令 IP。使用 `pjsip show registrations` 确认注册。

## Dialplan 简介

Dialplan 就像 Asterisk 的心脏。它定义了 Asterisk 如何处理 PBX 的每一个呼叫。它由分机组成，这些分机为 Asterisk 制定了要遵循的指令列表。指令由从通道或应用程序接收到的数字触发。为了成功配置 Asterisk，理解 dialplan 至关重要。大部分 dialplan 包含在 /etc/asterisk 目录下的 extensions.conf 文件中。此文件使用简单组语法，并具有四个主要概念：

- 分机 (Extensions)
- 优先级 (Priorities)
- 应用程序 (Applications)
- Contexts

让我们创建一个基本的 dialplan。在本书的后续部分，我将专门用一章来介绍 dialplan。如果您安装了示例文件 (make samples)，extensions.conf 已经存在。将其另存为其他名称并从空白文件开始。

## extensions.conf 文件的结构

extensions.conf 文件分为多个部分。第一部分是 [general] 部分，后面是 [globals] 部分。每个部分的开头以其名称定义（即 [default]）开始，并在创建另一个部分时结束。

### [general] 部分

general 部分位于文件顶部。在开始配置 dialplan 之前，了解控制某些 dialplan 行为的常规选项很有帮助。这些选项是：

- static 和 write protect: 如果 static=yes 且 writeprotect=no，您可以使用 CLI

```
command save dialplan.
```

警告：如果您从 CLI 发出 save dialplan 命令，您最终会丢失文件中的所有备注和注释。

- autofallthrough: 如果设置了 autofallthrough，那么如果分机无事可做，它将根据 Asterisk 的最佳猜测以 BUSY、CONGESTION 或 HANGUP 终止呼叫。这是默认设置。如果未设置 autofallthrough，那么如果分机无事可做，Asterisk 将等待拨打新的分机。
- clearglobalvars: 如果设置了 clearglobalvars，全局变量将在 dialplan reload 或 Asterisk reload 时被清除并重新解析。如果未设置 clearglobalvars，则全局变量将在重新加载期间持续存在 — 即使从 extensions.conf 或其包含的文件之一中删除，它们也将保持设置为先前的值。
- extenpatternmatchnew: 使用更快的模式匹配算法，当您有大量分机时，这会有明显的帮助。默认为 no。
- userscontext: 这是来自 users.conf 的条目注册的 context。

### [globals] 部分

在 [globals] 部分，您将定义全局变量及其初始值。您可以使用 ${GLOBAL(variable)} 在 dialplan 中访问该变量。您甚至可以使用 ${ENV(variable)} 访问 linux/unix 环境中定义的变量。全局变量不区分大小写。一些示例可能是：

```
INCOMING>DAHDI/8&DAHDI/9
RINGTIME=>3
```

在以下示例中，您可以在 dialplan 中设置和测试全局变量。

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contexts

Context 是 dialplan 的命名分区。在 [general] 和 [globals] 部分之后，dialplan 是一组 context，其中每个 context 有多个分机，每个分机有多个优先级，每个优先级调用一个带有多个参数的应用程序。

![Asterisk 呼叫流：每个呼叫都作为入站呼叫段到达通道（IAX、SIP 等）；通道的 context — 在通道配置文件中全局设置或按通道设置 — 决定了在呼叫离开出站段之前，extensions.conf 中的哪个 context 处理该呼叫。](../images/04-first-pbx-fig03.png)

![呼叫处理：为通道定义的 `context=`（在 chan_dahdi.conf 或 pjsip.conf 中）命名了 extensions.conf 中的匹配 context，dialplan 在该 context 中处理呼叫。](../images/04-first-pbx-fig04.png)

您可以构建一个简单的 dialplan 来连接其他电话和 PSTN。然而，Asterisk 的功能远不止于此。我们的目标是教您更多关于 dialplan 中可能实现的细节。

## 分机 (Extensions)

与传统的 PBX 不同，传统 PBX 中的分机与电话、接口、菜单等相关联，在 Asterisk 中，分机是当触发特定分机号码或名称时要处理的命令列表。命令按优先级顺序处理。

![分机语法：`exten => number(name),{priority|label}[(alias)],application`。分机可以是数字、字母数字、带有来电显示的数字、模式或标准分机，如 `s`；优先级可以是数字、`n` (next)、`s` (same)、偏移量或 `hint`。](../images/04-first-pbx-fig05.png)

分机可以是字面量、标准或特殊的。标准分机仅包含数字或名称以及字符 * 和 #；12#89* 是有效的字面量分机。名称也可用于分机匹配。分机区分大小写。但是，您不能创建两个名称相同但大小写不同的分机。拨打分机时，执行优先级为 1 的命令，然后执行优先级为 2 的命令，依此类推。这种情况一直持续到呼叫断开或某个命令返回数字 1，表示失败。当执行最后一个优先级时 Asterisk 的行为由参数 autofallthrough 调节。请参阅本章中的 [general] 部分。示例：

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

上面您找到了拨打分机 123 时要处理的指令列表。第一个优先级是应答通道（当通道处于振铃状态时是必要的：例如 FXO 通道）。第二个优先级是播放名为 tt-weasels 的音频文件。第三个优先级挂断通道。另一个选项是根据来电显示处理呼叫。您可以使用 / 字符来指定要处理的来电显示。示例：

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

此示例将触发分机 123，并且仅在来电显示为 100 时执行以下选项。这也可以通过使用下面描述的模式来完成：

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: 将分机映射到通道。它用于监控通道状态。它与 presence 结合使用。电话必须支持它。

#### 模式 (Patterns)

您可以在 dialplan 中使用模式和字面量。模式对于减小 dialplan 大小非常有用。所有模式都以“_”字符开头。以下字符可用于定义模式。该图标识了可与 Asterisk 一起使用的模式。

![模式匹配字符：`_` 开始一个模式，`.` 匹配一个或多个字符，`!` 匹配零个或多个，`[123-7]` 匹配任何列出的数字或范围，`X` 是 0-9，`Z` 是 1-9，而 `N` 是 2-9 — 带有映射办公室分机范围的示例。](../images/04-first-pbx-fig06.png)

### 特殊分机

Asterisk 使用一些分机名称作为标准分机。

![Asterisk 特殊分机：`i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (在语音信箱中按下 `*`), `fax` (传真检测), 和 `Talk` (与 BackgroundDetect 一起使用)。](../images/04-first-pbx-fig07.png)

描述：s: Start。它用于在没有拨打号码时处理呼叫。它对于 FXO trunk 和菜单内处理非常有用。t: Timeout。它用于呼叫在提示音播放后保持不活动状态时。它也用于挂断不活动的线路。T: AbsoluteTimeout。如果您使用 `TIMEOUT(absolute)` dialplan 函数建立呼叫限制，一旦呼叫超过定义的限制，它将被发送到 T 分机。h: Hangup。它在用户断开呼叫后被调用。i: Invalid。当您在 context 中拨打不存在的分机时触发。使用这些分机可能会影响 CDR 记录的内容 — 具体来说，dst 不包含拨打的号码。o: Operator。它用于在用户在语音信箱期间按下“0”时转到操作员。使用这些分机可能会更改计费记录 (CDR) 的内容 — 特别是，字段 dst 将没有拨打的号码。为了解决这个问题，您应该在 dial() 应用程序中使用选项 g，并考虑函数 resetcdr(w) 和/或 nocdr()

## 变量

在 Asterisk PBX 中，变量可以是全局的、通道特定的和环境特定的。您可以使用 NoOP() 应用程序在控制台中查看变量的内容。它可以使用全局变量或通道特定变量作为应用程序参数。变量可以像以下示例中那样引用，其中 varname 是变量的名称。

```
${varname}
```

变量名称可以是以字母开头的字母数字字符串。全局变量名称不区分大小写。但是，系统变量（Asterisk 定义的是通道定义的）区分大小写。因此，变量 ${EXTEN} 与 ${exten} 不同。

### 全局变量

全局变量可以在 extensions.conf 文件的 [global] 部分中配置，或者使用应用程序：

```
set(Global(variable)=content)
```

### 通道特定变量

通道特定变量使用应用程序 set() 配置。每个通道接收其自己的变量空间。不同通道的变量之间没有冲突的可能性。通道特定变量在通道挂断时被销毁。一些最常用的变量是：

- ${EXTEN} 拨打的分机
- ${CONTEXT} 当前 context
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} 当前来电显示
- ${PRIORITY} 当前优先级

其他通道特定变量均为大写。您可以使用 dumpchan() 应用程序查看多个变量的内容。以下是 dump-channel 变量的简单摘录。

```
exten=9001,1,dumnpchan()
exten=9001,n,echo()
exten=9001,n,hangup()
```

Dumpchan 输出：

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

上面的字段布局是 Asterisk 22 `DumpChan` 输出（真实的 `PJSIP/...` 通道名称，`CallerIDNum`/`ConnectedLineID` 字段，以及 PJSIP 通道填充的 `Raw*`/`Transcode`/`BridgeID` 行）。与旧驱动程序不同，PJSIP 通道不会自动设置 `SIPCALLID`/`SIPUSERAGENT` 通道变量；等效的 SIP 细节通过 `PJSIP_HEADER()` 和 `CHANNEL()` dialplan 函数按需读取 — 例如 `${CHANNEL(pjsip,call-id)}`、`${PJSIP_HEADER(read,User-Agent)}` 和 `${CHANNEL(rtp,dest)}` 用于远程 RTP 地址。

### 环境特定变量

环境特定变量可用于访问操作系统中定义的变量。您可以使用函数 ENV() 设置环境特定变量。例如：

```
${ENV(LANG)}
Set(ENV(LANG))=en_US
```

### 应用程序特定变量

一些应用程序使用变量进行数据输入和输出。您可以在调用应用程序之前设置变量，或者在应用程序执行后检索变量。例如：Dial 应用程序返回以下变量：

- ${DIALEDTIME} -> 这是从拨打通道到断开连接的时间。
- ${ANSWEREDTIME} -> 这是实际通话的时间。
- ${DIALSTATUS} 这是呼叫的状态：o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> 呼叫的错误消息。

## 表达式

表达式在 dialplan 中非常有用。它们用于操作字符串并执行数学和逻辑运算。

![Asterisk 表达式概述 — `$[expression1 operator expression2]` — 分组了 dialplan 中可用的数学、逻辑、比较、正则表达式和条件运算符。](../images/04-first-pbx-fig08.png)

表达式语法定义如下：

```
$[expression1 operator expression2]
```

假设我们有一个名为“I”的变量，我们想给该变量加 100：

```
$[${I}+100]
```

当 Asterisk 在 dialplan 中找到表达式时，它会将整个表达式更改为结果值。

### 运算符

以下运算符可用于构建表达式。观察运算符优先级很重要。 1. 圆括号 “()” 2. 一元运算符 “! -“ 3. 正则表达式 “: =~ 4. 乘法运算符 “* / %” 5. 加法运算符 “+ -“ 6. 比较运算符 7. 逻辑运算符 8. 条件运算符

#### 数学运算符

- 加法 (+)
- 减法 (-)
- 乘法 (*)
- 除法 (/)
- 取模 (%)

#### 逻辑运算符

- 逻辑 “AND” (&)
- 逻辑 “OR” (|)
- 逻辑一元补码 (!)

#### 正则表达式运算符

- 正则表达式匹配 (:)
- 正则表达式精确匹配 (=~)

正则表达式是用于描述搜索模式的特殊文本字符串。您可以将正则表达式视为通配符。正则表达式用于将字符串与模式匹配以检查匹配。如果匹配成功且正则表达式包含至少一个匹配项，则返回第一个匹配项；否则，结果是匹配的字符数。

#### 比较运算符

如果关系为真，则比较的结果为 1，如果为假，则为 0。

- = 等于
- != 不等于
- < 小于
- > 大于
- <= 小于或等于
- >= 大于或等于

### 实验室。评估以下表达式：

将这些表达式放入您的 dialplan 中，并使用 NoOP() 应用程序评估表达式。拨打 9002 并在 Asterisk 控制台中检查结果。使用 verbose 15 显示结果。

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## 函数

一些应用程序已被函数取代，这些函数允许以比仅使用表达式更高级的方式处理变量。您可以通过发出以下控制台命令查看函数的完整列表：

```
CLI>core show functions
```

字符串长度：${LEN(string)} 返回字符串长度

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

在第一个操作中，系统显示 5 作为结果（单词“fruit”中的字母数）。第二个返回数字 4（单词“pear”中的字母数）。子字符串：返回子字符串，从“offset”参数定义的位置开始，长度由“length”参数定义。如果偏移量为负，则从右到左开始，从字符串末尾开始。如果省略长度或长度为负，则取从偏移量开始的整个字符串。

```
${string:offset:length }
```

示例 #1：多个子字符串

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

示例 #2：从前三位数字中获取区号。

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

示例 #3：从变量 ${EXTEN} 中获取所有数字，区号除外。

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### 字符串连接

要连接两个字符串，只需将它们写在一起即可。

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## 应用程序

要构建 dialplan，我们需要理解应用程序的概念。您将在 dialplan 中使用应用程序来处理通道。应用程序在多个模块中实现。可用应用程序取决于模块。您可以使用控制台命令显示所有 Asterisk 应用程序：

```
CLI>core show applications
```

或者，您可以使用以下示例显示特定应用程序的详细信息：

```
CLI>core show application dial
```

要构建简单的 dialplan，您需要了解一些应用程序。我们将在本书后面讨论更高级的示例。

![构建简单 dialplan 所需的少数应用程序：Answer（应答通道）、Dial（呼叫另一个通道）、Hangup（挂断通道）、Playback（播放音频文件）和 Goto（跳转到优先级、分机或 context）。](../images/04-first-pbx-fig09.png)

我们将使用这些应用程序（上图）为两个基本 PBX 创建一个简单的 dialplan。

### Answer()

[概要] 如果正在振铃则应答通道 [描述] Answer([delay]): 如果呼叫尚未应答，应用程序将应答它。否则，它对呼叫没有影响。如果指定了延迟，Asterisk 将在应答呼叫之前等待“delay”中指定的毫秒数。

### Dial()

以下描述可以通过在 dialplan 中发出 show application dial 获得。为了便于搜索，它在下面转载。Dial 应用程序的语法也显示在下面：

```
;dial to a single channel
Dial(type/identifier,timeout,options, URL)
;Dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...][|timeout][|options][|URL]):
```

此应用程序将呼叫拨打到一个或多个指定的通道。一旦请求的通道之一应答，原始通道将被应答 — 如果它尚未应答。这两个通道随后将在桥接呼叫中处于活动状态。所有其他请求的通道随后将被挂断。除非指定了超时，否则 Dial 应用程序将无限期等待，直到被呼叫的通道之一应答、用户挂断，或者所有被呼叫的通道都忙或不可用。如果无法呼叫请求的通道或超时过期，dialplan 的执行将继续。此应用程序在完成后设置以下通道变量：

- DIALEDTIME - 这是从拨打通道到断开连接的时间。
- ANSWEREDTIME - 这是实际通话的时间。
- DIALSTATUS - 这是呼叫的状态：o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

对于隐私和筛选模式，如果被叫方选择将呼叫方发送到“Go Away”脚本，DIALSTATUS 变量将被设置为 DONTCALL。如果被叫方想将呼叫方发送到“torture”脚本，DIALSTATUS 变量将被设置为 TORTURE。如果原始通道挂断，或者呼叫被桥接且桥接中的任何一方结束呼叫，此应用程序将报告正常终止。如果通道支持，可选的 URL 将发送给被叫方。如果设置了 OUTBOUND_GROUP 变量，此应用程序创建的所有对等通道都将包含在该组中（如在

```
Set(GROUP()=...).
```

下表总结了 Dial 应用程序最常用的一些选项。有关完整列表，请使用控制台命令 `core show application Dial`。在 Asterisk 22 中，这些选项通过逗号与通道和超时分隔 — 例如 `Dial(PJSIP/2000,20,tTm)`。

| 选项 | 描述 |
|--------|-------------|
| `A(x)` | 使用 `x` 作为文件向被叫方播放公告。 |
| `C` | 重置此呼叫的 CDR。 |
| `d` | 允许呼叫用户在等待呼叫应答时拨打 1 位分机。如果该分机在当前 context 中存在，则退出到该分机，或者如果存在，则退出到 `EXITCONTEXT` 变量中定义的 context。 |
| `D([called][:calling])` | 在被叫方应答后但在呼叫桥接之前发送指定的 DTMF 字符串。`called` 字符串发送给被叫方，`calling` 字符串发送给呼叫方。任一参数都可以单独使用。 |
| `f` | 强制将呼叫通道的来电显示设置为通过 dialplan `hint` 与通道关联的分机。在 PSTN 不允许任意来电显示的情况下很有用。 |
| `g` | 如果目标通道挂断，则在当前分机处继续执行 dialplan。 |
| `G(context^exten^pri)` | 如果呼叫被应答，将呼叫方转移到指定的优先级，将被叫方转移到优先级+1。可以选择指定分机（或分机和 context）；否则使用当前分机。 |
| `h` | 允许被叫方通过发送 `*` DTMF 数字来挂断。 |
| `H` | 允许呼叫方通过发送 `*` DTMF 数字来挂断。 |
| `L(x[:y][:z])` | 将呼叫限制为 `x` 毫秒，当剩余 `y` 毫秒时播放警告，并每隔 `z` 毫秒重复警告。请参阅下面的 `LIMIT_*` 变量。 |
| `m([class])` | 在请求的通道应答之前，向呼叫方提供保持音乐。可以指定特定的 MusicOnHold 类。 |
| `r` | 向呼叫方指示振铃，并且在被叫通道应答之前不传递音频。 |
| `S(x)` | 在被叫方应答 `x` 秒后挂断呼叫。 |
| `t` | 允许被叫方通过发送 `features.conf` 中定义的 DTMF 序列来转移呼叫方。 |
| `T` | 允许呼叫方通过发送 `features.conf` 中定义的 DTMF 序列来转移被叫方。 |
| `w` | 允许被叫方通过发送 `features.conf` 中定义的 DTMF 序列来启用一键录音。 |
| `W` | 允许呼叫方通过发送 `features.conf` 中定义的 DTMF 序列来启用一键录音。 |
| `k` | 允许被叫方通过发送 `features.conf` 中定义的呼叫驻留 DTMF 序列来驻留呼叫。 |
| `K` | 允许呼叫方通过发送 `features.conf` 中定义的呼叫驻留 DTMF 序列来驻留呼叫。 |

`L(x[:y][:z])` 选项可以使用以下特殊变量进行调整：

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (默认 `yes`): 为呼叫方播放声音。
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: 为被叫方播放声音。
- `LIMIT_TIMEOUT_FILE` — 时间到时要播放的文件。
- `LIMIT_CONNECT_FILE` — 呼叫开始时要播放的文件。
- `LIMIT_WARNING_FILE` — 定义 `y` 时作为警告播放的文件。默认是说剩余时间。

示例：

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

在上面的示例中，应用程序将拨打相应的 PJSIP 通道。呼叫方和被叫方都可以转移呼叫 (Tt)。将听到保持音乐而不是回铃音。如果 20 秒内无人应答，分机将转到下一个优先级。

### Hangup()

挂断呼叫通道 [描述] Hangup([causecode]): 此应用程序将挂断呼叫通道。如果给出了原因代码，通道的挂断原因将被设置为给定的值。

### Goto()

跳转到特定的优先级、分机或 context [描述] Goto([[context|]extension|]priority): 此应用程序将导致呼叫通道在指定的优先级继续执行 dialplan。如果未指定特定的分机（或分机和 context），此应用程序将跳转到当前分机的指定优先级。如果跳转到 dialplan 中其他位置的尝试不成功，通道将在当前分机的下一个优先级继续。

## 构建 dialplan

要构建简单的 dialplan，您需要通过创建 context 和分机来处理所有入站和出站呼叫。在本节中，我们将向您展示如何构建最常见的分机。

### 分机间拨号

要启用分机间拨号，我们可以使用通道变量 ${EXTEN}，它指的是拨打的分机。例如，如果分机范围在 4000 到 4999 之间，并且所有分机都使用 SIP，我们可以采用以下命令：

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### 拨打外部目的地

要拨打外部目的地，您可以在拨打的号码前加上路由。在北美，通常使用 9 后跟要拨打的外部号码。如果您使用模拟或数字通道连接到 PSTN，命令应如下所示：如果您想使用 SIP trunk 而不是 DAHDI，请使用 `Dial(PJSIP/number@siptrunk,...)` 通道。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

上面的行将允许您拨打 9 和所需的号码。在给出的示例中，您将使用第一个 DAHDI 通道 (DAHDI/1)。如果您有多条线路且此线路忙，呼叫将无法完成。但是，您可以使用以下行自动选择第一个可用的 DAHDI 通道。或者，您可以使用 SIP trunk 代替 DAHDI。在 PJSIP 形式  中，拨打的号码是用户部分，`siptrunk` 是上面配置的 endpoint。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

“g1”参数将在组中搜索第一个可用通道，允许使用所有通道。使用下面一行，您可以拨打长途号码。

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### 拨打 9 获取 PSTN 线路

如果您对外部拨号没有任何限制，您可以简化并使用以下内容：

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### 在操作员分机接听电话

在以下示例中，操作员分机是 4000。PSTN 线路连接到 FXO 接口。在 chan_dahdi.conf 文件中，指定的 context 是 from-pstn。任何来自 PSTN 的呼叫都将被路由到 dialplan 中的 context from-pstn。此线路没有直接拨入 (DID)；因此，我们将不得不通过“s”分机接听电话。如果从 SIP trunk 接听，请使用 context [from-sip]。

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### 使用直接拨入 (DID) 接听电话

如果您有数字线路，您将收到拨打的分机。在这种情况下，您不需要将呼叫转发给操作员；相反，您可以直接将呼叫转发到目的地。假设您的 DID 范围是从 3028550 到 3028599，并且最后四位数字在 DID 中传递。配置将如下例所示：

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### 同时播放多个分机

您可以设置 Asterisk 拨打一个分机，如果无人应答，则同时拨打其他几个分机，如下例所示：

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

在此示例中，当有人拨打操作员时，首先尝试通道 DAHDI/1。如果 15 秒（超时）后无人应答，通道 DAHDI/1、DAHDI/2 和 DAHDI/3 将同时振铃另外 15 秒。

### 按来电显示路由

在此示例中，您可以根据来电显示给予不同的处理，这对于呼叫垃圾邮件发送者可能很有用。例如：

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

在此示例中，我们添加了一条特殊规则，如果来电显示是 4832518888，则播放之前录制的文件“I-have-moved-to-china”中的消息。其他呼叫照常接受。

### 在 dialplan 中使用变量

Asterisk 可以在 dialplan 中使用全局和通道变量作为某些应用程序的参数。看看以下示例：

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

使用变量使未来的更改更容易。如果您更改变量，所有引用都会立即更改。

### 录制公告

在本节后面讨论的某些选项中，我们将使用录制的提示音。在这里，我们向您展示一种录制它们的简单方法。我们将使用应用程序 Record() 来使用自己的电话保存公告。

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

这些指令允许您从软电话录制任何消息。示例：从软电话拨打 recordmenu 指令将调用带有变量 ${EXTEN:6} 的录音，而不带前六个字母。换句话说，该指令等同于 record(menu:gsm)。您所要做的就是拨打 record + 要录制的文件名，按 # 完成录音，并等待听到录音。

### 在数字接待员中接听电话

现在我们有了一些简单的示例，让我们扩展关于应用程序 background() 和 goto() 的学习。Asterisk 中交互式系统的关键是应用程序 background()，它允许您执行一个音频文件，当呼叫者按下某个键时，该文件会被中断，以便将呼叫发送到拨打的分机。background() 应用程序的语法：

```
exten=>extension, priority, background(filename)
```

另一个非常有用的应用程序是 goto()。顾名思义，它跳转到指定的 context、分机和优先级。应用程序 goto() 的语法：

```
exten=>extension, priority,goto(context, extension, priority)
```

goto() 命令的有效格式：

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

在以下示例中，我们将创建一个数字接待员。编辑 extensions.conf 文件并配置以下分机非常简单：

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

SIP 分机使用 `PJSIP/`，IAX 分机使用 `IAX2/` — 两个驱动程序都随 Asterisk 22 提供，尽管 `chan_iax2` 现在被认为是遗留的，并且首选 SIP/PJSIP。

在文件 menu1.gsm 中，录制消息“press the extension or wait for the operator”。当用户拨打号码 6000 时，他将被发送到分机 6000。此时，您应该清楚地了解多个应用程序的使用，包括 answer()、background()、goto()、hangup() 和 playback()。如果您没有清楚地了解，请再次阅读本章，直到您对内容感到满意为止。您将非常频繁地使用 background 应用程序。一旦您了解了分机、优先级和应用程序的基础知识，创建简单的 dialplan 就会很容易。这些概念将在本书后面更深入地探讨，您将看到 dialplan 将变得更加强大。

## 总结

在本章中，您了解到配置文件存储在 /etc/asterisk 目录中。要使用 Asterisk，首先必须配置通道（例如 pjsip、dahdi、iax）。配置文件存在三种不同的语法：简单组、对象继承和复杂实体。Dialplan 在 extensions.conf 文件中创建，是一组 context 和分机。在 dialplan 中，每个分机触发一个应用程序。您学会了使用 playback、background、dial、goto、hangup 和 answer 应用程序。

## 测验

1. 通道配置文件是（选择所有适用项）：
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. 在 Asterisk 22 上，单个 `chan_sip` peer `[6001]` (`type=friend`/`host=dynamic`) 在 `pjsip.conf` 中被哪一组相关对象取代？
   - A. 一个 `type=peer` 和一个 `type=user`
   - B. 一个 `type=endpoint`、一个 `type=auth` 和一个 `type=aor`
   - C. 单个 `type=friend`
   - D. 一个 `type=transport` 和一个 `type=global`
3. 在通道配置文件中定义 context 很重要，因为它设置了来自该通道的呼叫的入站 context — 来自该通道的呼叫在 `extensions.conf` 中的匹配 context 中处理。
   - A. True
   - B. False
4. `Playback()` 和 `Background()` 应用程序之间的主要区别是（选择两项）：
   - A. Playback 播放提示音但不等待数字。
   - B. Background 播放提示音但不等待数字。
   - C. Background 播放消息并等待按下数字。
   - D. Playback 播放消息并等待按下数字。
5. 当呼叫通过没有 DID 的电话接口卡 (FXO) 进入 Asterisk 时，它在特殊分机中处理：
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. `Goto()` 应用程序的有效格式是（选择三项）：
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. 模式 `_7[1-5]XX` 匹配（选择所有适用项）：
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. 在 `Dial(PJSIP/${EXTEN},20,tTm)` 中，`m` 选项的作用是什么？
   - A. 将呼叫限制为最大持续时间。
   - B. 在通道应答之前向呼叫方提供保持音乐而不是回铃音。
   - C. 在被叫方应答后发送 DTMF 数字。
   - D. 使用 dialplan hint 强制来电显示。
9. 在 `chan_dahdi.conf` 使用的选项继承语法中，您：
   - A. 在单行中定义对象。
   - B. 先定义选项，并在定义的选项下方声明对象。
   - C. 为每个对象定义一个单独的 context。
10. 分机中的优先级必须按顺序编号 (1, 2, 3, …) 且不能使用 `n`。
    - A. True
    - B. False

**答案：** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
