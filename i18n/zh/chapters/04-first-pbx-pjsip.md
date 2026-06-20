# 构建您的第一个基于 PJSIP 的 PBX

在本章中，您将学习如何执行基本的 Asterisk PBX 配置。此处的主要目标是让 PBX 第一次运行，能够在分机之间拨号、拨打正在播放的语音提示，以及拨打单个模拟或 SIP 中继。本章的理念是确保您的 Asterisk 能尽快启动并运行。完成本章的工作后，您将拥有足够的背景知识，为后续章节做好准备，在这些章节中我们将更深入地探讨配置细节。

## 目标

By the end of this chapter, you should be able to:

- Understand and edit configuration files;
- Install softphones based on SIP;
- Install and configure a SIP trunk;
- Install and configure an analog connection;
- Dial between extensions;
- Dial between phones and external destinations; and
- Configure an auto attendant.

## 理解配置文件

Asterisk 由位于 /etc/asterisk 的文本配置文件控制。文件格式类似于 Windows 的 “.ini” 文件。分号用作注释字符，符号 “=” 和 “=>” 等价，空格会被忽略。

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk 以相同的方式解释 “=” 和 “=>”。语法差异用于区分对象和变量。当你想声明变量时使用 “=”，而指定对象时使用 “=>”。所有文件的语法相同，但如下面所述，使用了三种语法类型。

## 语法

| 语法 | 对象的创建方式 | 配置文件 | 示例 |
|---------|---------------------------|------------|---------|
| 简单组 | 同一行内 | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| 选项继承 | 先定义选项，对象继承这些选项 | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| 复杂实体 | 每个实体获得一个上下文 | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### 简单组

在`extensions.conf`和`voicemail.conf`中使用的简单组格式是最基本的语法。每个对象在同一行内声明选项。示例：

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

在此示例中，对象 1 使用选项 op1、op2 和 op3 创建，而对象 2 使用选项 op1、op2 和 op3 创建。

### 对象选项继承语法

此格式用于文件 chan_dahdi.conf 和 agents.conf，这些文件中有大量可用选项，并且大多数接口和对象共享相同的选项。通常，一个或多个节包含对象和通道的声明。对象的选项在对象上方声明，并且可以更改为另一个对象。虽然这个概念不易理解，但使用起来非常简单。示例：

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

前两行将选项 op1 和 op2 的值分别配置为 “bas” 和 “adv”。当实例化对象 1 时，它使用 op1 为 “bas”、op2 为 “adv”。在定义对象 1 后，我们将 op1 改为 “int”。接着创建对象 2，使用 op1 为 “int”、op2 为 “adv”。

### 复杂实体对象

此格式用于 pjsip.conf、iax.conf 以及其他包含大量实体和众多选项的配置文件。通常，这种格式并不共享大量公共配置。每个实体获得一个上下文。有时会存在保留的上下文，例如用于全局配置的 [general]。选项在上下文声明中声明。示例：

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

实体 [entity1] 对选项 op1 和 op2 的值分别为 “value1” 和 “value2”。实体 [entity2] 对选项 op1 和 op2 的值分别为 “value3” 和 “value4”。

## Options to build a LAB for Asterisk

要配置 PBX，您需要一些基本硬件。它并不难也不贵，但有几种选项需要考虑。您只需要两部电话和一条公共网络连接。创建实验室时可以有多种选项和组合，下面将进行讨论。

### Option 1: Complete LAB

使用完整的 LAB，您可以测试所有可用场景，并比较 ATA、IP‑phones 和 softphones 等方案。您还可以了解模拟和 SIP trunk。您将需要：

- A SIP analog telephone adapter (ATA)
- An IP phone
- A dedicated server for Asterisk
- A workstation with a softphone
- An analog interface card with at least two interfaces (1 FXO and 1 FXS)
- A VoIP provider account

### Option 2: Economy LAB

使用经济型 LAB，我们会稍作简化。我们使用通常比 IP‑phone 更便宜的 ATA，以及一块非常廉价的单 FXO 卡。我们将无法直接将模拟电话连接到服务器，但这在实际中并不常见。您将需要：

- A SIP analog telephone adapter (ATA)
- A dedicated server for Asterisk
- A workstation for the softphone
- An analog interface card with 1 FXO
- An account with a VoIP provider

### Option 3: Super economy lab

第三种 LAB 在学生自己的笔记本上使用虚拟化服务器。此模型的问题在于 UDP 端口冲突。有时 Asterisk 服务器和 softphone 会尝试访问同一端口，导致 Asterisk 无法绑定该地址端口。另一个问题是通话质量；虚拟环境并不适合实时应用如 Asterisk。使用免费 softphone 作为服务器和工作站，并通过 SIP provider 进行 trunk 连接。您将需要：

- A laptop running a softphone
- A virtual machine (VirtualBox, VMware, or similar) to install Asterisk
- An account with a VoIP provider

## 安装顺序

为了帮助您了解安装顺序，我们概述了安装和配置 Asterisk 所需的步骤。

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. 分机配置
   - a. SIP 分机（ATA、软电话、IP 电话）
   - b. IAX 分机
   - c. FXS 分机
2. 中继配置
   - a. SIP 中继的配置
   - b. FXO 中继的配置
3. 构建基本拨号计划
   - a. 分机之间的拨号
   - b. 拨打外部目的地
   - c. 在运营员分机中接听来电
   - d. 在自动应答系统中接听来电

## Configuration of the extensions

分机可以是连接到 FXS 端口的 SIP、IAX 或模拟电话。要配置分机，需要编辑与通道相关的配置文件（pjsip.conf、iax.conf、chan_dahdi.conf）。

### SIP extensions

在 Asterisk 22 中，PJSIP（`res_pjsip`栈，在`/etc/asterisk/pjsip.conf`中配置）是 SIP 通道驱动。它支持每个端点的多传输，维护活跃，并且是平台唯一随附的 SIP 驱动。（原始`chan_sip`驱动已在 Asterisk 21 中移除——如果需要迁移旧配置，请参见 *Legacy channels* 章节。）

这里的目标是配置一个简单的 PBX。（后续章节将提供完整的 SIP/PJSIP 会话及所有细节。）PJSIP 在`/etc/asterisk/pjsip.conf`中配置，保存所有与 SIP 电话和 VoIP 提供商相关的参数。必须先配置 SIP 客户端，才能进行呼叫和接收呼叫。

#### The transport

在 PJSIP 中，监听器配置（绑定地址、端口、协议）位于一个`transport`对象中。Asterisk 内置了防止用户名猜测的保护——对未知和已知用户始终返回相同的认证挑战，并且对同一 IP 的重复未识别请求通过`[global]`选项`unidentified_request_count`/`unidentified_request_period`进行速率限制。传输的主要选项有：

- protocol: 传输协议——`udp`、`tcp`、`tls`、`ws`或`wss`。
- bind: 监听器绑定的地址和端口。如果将地址设为`0.0.0.0`, 则绑定所有接口；SIP 端口默认对 UDP/TCP 为 5060。

最小的 UDP 传输：

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

编解码器选择（`disallow`/`allow`）和默认`context`在每个`endpoint`（如下所示）上配置，而不是在传输上。匿名/访客呼叫由名为`anonymous`的`endpoint`处理。注册计时器通过`maximum_expiration`/`default_expiration`在每个 AOR 上控制。

#### SIP clients

完成传输部分后，就该设置 SIP 客户端了。再次提醒读者，书后面会有完整的 SIP/PJSIP 章节。现在先专注基础，细节留待以后。

在 PJSIP 中，SIP 客户端由一组相关对象构成，通过名称引用绑定在一起：

- `endpoint`：呼叫行为——编解码器（`allow`/`disallow`）、dialplan `context`以及使用的`auth`和`aors`。
- `auth`：凭证。`username`是 SIP 认证用户，`password`是用于认证设备的密钥。
- `aor`：“记录地址”——端点可达的位置。可以是静态`contact=`（用于固定 IP 的设备）或`max_contacts=`以允许设备动态注册。

> **警告**：使用强密码，至少 8 位字符，包含字母、数字以及至少一个符号。邮件列表中已有服务器被攻击的报告，针对 SIP 的暴力破解工具对脚本小子来说很容易获取。电话诈骗给消费者和提供商造成数千美元的损失。

端点 6000 是固定 IP 设备，因此其 AOR 包含静态`contact`而不允许注册。端点 6001 是会注册的设备，其 AOR 允许注册（`max_contacts=1`）：

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
auth_type=digest
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
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP 允许`endpoint`、`auth`和`aor`节共享相同的节名（例如上面的两个`[6001]`块，通过它们的`type=`区分）；许多管理员为了可读性会在后缀添加（`[6001]`、`[6001-auth]`、`[6001]`aor）。对于会注册的设备，联系信息在电话注册时动态学习，因此 AOR 不需要静态`contact`。

## IAX Extensions

`chan_iax2`仍然随 Asterisk 22 一起发布，但已成为遗留功能；对于新部署，首选协议是 SIP/PJSIP。

您也可以创建 IAX 分机。该协议是 Asterisk 原生支持的，我们将在本书后面的章节专门讨论它。现在，让我们使用该协议创建几个分机。作为要配置的第一个部分，[general] 部分有若干参数需要设置。主要选项包括：

- allow/disallow：定义将使用哪些 codec。
- bindaddr：IAX2 监听器绑定的地址。如果将其设置为 0.0.0.0（默认），则会绑定所有接口。
- context：为所有客户端设置默认 context，除非在客户端部分另行更改。出于安全考虑，我们使用 dummy。未认证的用户在 allowguest 选项设为 yes 时会进入此 context。
- bindport：IAX2 UDP 监听端口（默认 4569）。
- delayreject：设为 yes 时，会延迟对 REGREQ 或 AUTHREQ 的认证拒绝，从而提升对暴力密码攻击的防御能力。
- bandwidth：设为 high 时，允许选择高带宽 codec，例如 g711 的 ulaw 和 alaw 变体。

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

### IAX Clients

完成 general 部分后，接下来设置 IAX 客户端。

- `[name]`：该节名称即为 IAX 对等体/用户名称；传入的 IAX 连接会通过名称匹配到此节。
- `type`：连接类别——`peer`、`user`或`friend`：
  - `peer`：Asterisk 向对等体发送呼叫。
  - `user`：Asterisk 从用户接收呼叫。
  - `friend`：同时支持双向呼叫。
- `host`：IP 地址或主机名。最常见的取值是`dynamic`，用于设备向 Asterisk 注册时。
- `secret`：用于验证对等体和用户的密码。

**警告**：请使用至少 8 位、包含字母、数字以及至少一个符号的强密码。邮件列表中已经出现了被攻击服务器的报告，针对 IAX md5 哈希的暴力破解工具也已面向脚本小子公开。电话欺诈给消费者和运营商造成了数千美元的损失。示例：

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Configuring the SIP devices

After defining the phones in the Asterisk configuration file, it is time to configure the phone itself. In this example, we will show how to configure a free softphone — the SipPulse Softphone (download it from https://www.sippulse.com/produtos/softphone). Check your device’s manual to understand the parameters of your phone. Step 1: Configure the phone to use the extension 6000. Execute the installation program. After the execution, open the account/SIP settings and add a new SIP account. Fill in the required information.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Confirm that your phone is registered using the console command `pjsip show endpoints` (or `pjsip show endpoint 6000` for detail; `pjsip show contacts` shows the registered AOR contacts). Repeat the configuration for the phone 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## 配置 IAX 设备

IAX2 是一种遗留协议（参见 *Legacy channels* 一章），而 SipPulse Softphone 仅支持 SIP，因而无法注册 IAX 账户。如果需要测试 IAX2，请使用仍然支持该协议的软电话。创建一个新的 IAX 账户，

3. 选择新建 IAX 账户。  
4. 为 6003 电话插入相关选项，并可选地为 6004 插入。  
5. 保存配置，并使用 `iax2 show peers` 检查电话是否已注册。

重要提示：SIP 使用一个账户，IAX 使用另一个账户。如果希望系统同时响铃 IAX 和 SIP，我们将在 dial plan 部分展示相应的配置方法。

### 配置 PSTN 接口

要连接 PSTN，需要一个外线（FXO）接口和一条电话线。也可以使用现有的 PBX 分机。您可以从多家厂商处获得带有 FXO 接口的电话接口卡。本例中，我们将演示如何安装 DAHDI 接口卡。

![FXS and FXO ports: the FXS port drives an analog phone (supplies dial tone and ring), while the FXO port connects Asterisk to the Telco line.](../images/04-first-pbx-fig02.png)

### 使用 DAHDI 的模拟线路

您可以从多家厂商处购买兼容 DAHDI 的模拟卡。X100P 是 Digium 最早的卡之一，现已停产。部分厂商仍在生产类似的克隆卡。除了 X100P 的价格外，我们还发现这些卡与新主板之间存在若干问题，使用时需谨慎。个人认为 X100P 并不是生产环境的理想选择。任何兼容 DAHDI 的卡都应该可以工作。得益于 DAHDI 开发团队的努力，我们现在拥有几乎自动检测和配置接口卡的工具。如果您刚刚安装了 DAHDI 驱动，请务必运行 make config 并重启机器以自动加载。您可以使用以下命令检测并配置您的卡。步骤 1：要检测硬件，使用：

```
dahdi_hardware
```

步骤 2：要配置，请使用：

```
dahdi_genconf
```

上述命令将生成两个文件 /etc/dahdi/system.conf 和 /etc/asterisk/dahdi-channels.conf。dahdi_genconf 的默认参数通常已经足够，但您可以在文件 /etc/dahdi/genconf_parameters 中进行更改。默认情况下，它会在上下文 from-pstn 中插入 (FXO) 行，在上下文 from-internal 中插入 (FXS) 行。步骤 3：运行 dahdi_genconf 后，在文件 /etc/asterisk/chan_dahdi.conf 的最后一行插入以下内容：

```
#include dahdi-channels.conf
```

步骤 4：编辑文件 /etc/dahdi/modules 并注释掉所有未使用的驱动程序。继续之前请重启，并使用以下方式检查通道是否被识别：

```
*CLI> dahdi show channels
```

### 通过 VoIP 提供商连接到 PSTN

如果预算非常有限，您可以配置 SIP 中继来连接 PSTN。这无疑是连接 PSTN 最经济的方式。全球有成千上万的 VoIP 提供商。要连接其中一家，您需要一些参数。参数由 SIP 提供商提供。

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

有两个参数需要您自行确定。

- Extension to receive calls—in this case: 9999
- context: from-sip

In PJSIP, a registering SIP trunk is built from the same object family used for an endpoint, plus explicit `registration` and `identify` objects. The `registration` object tells Asterisk to register to the provider, the `identify` object matches inbound traffic from the provider's IP to the endpoint (PJSIP authenticates inbound INVITEs by source IP), and `outbound_auth` supplies the credentials for outbound calls and registration:

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
auth_type=digest
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

要访问此中继，我们将使用通道名称 `PJSIP/siptrunk`。 `dtmf_mode=rfc4733` 设置以带外方式传输 DTMF（RFC 4733 已取代较旧的 RFC 2833；负载相同）。 `identify`/`match` 选项接受 IP 地址、CIDR 或主机名，但主机名仅在配置加载时解析一次，因此对于 IP 变化的提供商，请显式列出信令 IP。 使用 `pjsip show registrations` 确认注册。

## Dial plan 介绍

Dial plan 就像 Asterisk 的心脏。它定义了 Asterisk 如何处理每一个进入 PBX 的呼叫。它由一系列 extension 组成，这些 extension 为 Asterisk 提供了一份指令列表。指令由从通道或应用收到的数字触发。要成功配置 Asterisk，理解 dial plan 至关重要。大部分 dial plan 内容位于 /etc/asterisk 目录下的 extensions.conf 文件中。该文件使用简单的分组语法，并包含四个主要概念：

- Extensions
- Priorities
- Applications
- Contexts

让我们创建一个基本的 dial plan。在本书后续章节中，我将专门用一章来深入讲解 dial plan。如果你已经安装了示例文件（make samples），extensions.conf 已经存在。将其另存为其他名称，然后从空文件开始。

## The structure of the file extensions.conf

extensions.conf 文件被划分为多个章节。第一章是 [general] 章节，随后是 [globals] 章节。每个章节的开始以其名称定义（例如，[default]）标记，直到创建另一个章节为止。

### The section [general]

general 章节位于文件的顶部。在开始配置 dialplan 之前，了解控制某些 dialplan 行为的通用选项是很有帮助的。这些选项包括：

- static and write protect: If `static=yes` and `writeprotect=no`, you can save the running dial plan back to disk with the CLI command:

```
*CLI> dialplan save
```

Warning: If you issue a `dialplan save` command from the CLI, you will lose any remarks and comments in the file.

- autofallthrough: If autofallthrough is set, then if an extension runs out of things to do, it will terminate the call with BUSY, CONGESTION, or HANGUP depending on Asterisk's best guess. This is the default. If autofallthrough is not set, then if an extension runs out of things to do, Asterisk will wait for a new extension to be dialed.
- clearglobalvars: If clearglobalvars is set, global variables will be cleared and reparsed into an dialplan reload or Asterisk reload. If clearglobalvars is not set, then global variables will persist through reloads and—even if deleted from the extensions.conf or one of its included files—they will remain set to the previous value.
- extenpatternmatchnew: Uses a faster pattern-matching algorithm, which helps noticeably when you have a large number of extensions. Defaults to no.
- userscontext: This is the context where the entries from the users.conf are registered.

### The section [globals]

在 [globals] 章节中，您将定义全局变量及其初始值。可以在 dialplan 中使用 `${GLOBAL(variable)}` 访问该变量。甚至可以使用 `${ENV(variable)}` 访问 linux/unix 环境中定义的变量。全局变量不区分大小写。几个示例可能是：

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

在下面的示例中，您可以在 dialplan 中设置并测试全局变量。

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contexts

Context 是 dial plan 的命名分区。在 [general] 和 [globals] 部分之后，dial plan 由一组 contexts 组成，每个 context 包含若干 extensions，每个 extension 包含若干 priorities，而每个 priority 调用一个带有多个参数的 application。

![Asterisk call flow: every call arrives on a channel (IAX, SIP, and others) as an incoming call leg; the channel's context — set globally or per-channel in the channel config file — decides which context in extensions.conf processes the call before it leaves on the outgoing leg.](../images/04-first-pbx-fig03.png)

![Call processing: the `context=` defined for a channel (in chan_dahdi.conf or pjsip.conf) names the matching context in extensions.conf where the dial plan handles the call.](../images/04-first-pbx-fig04.png)

您可以构建一个简单的 dial plan 来呼叫其他电话和 PSTN。然而，Asterisk 的功能远不止这些。我们的目标是向您介绍 dial plan 中更多可能实现的细节。

## 扩展

与传统 PBX 不同，传统 PBX 中扩展号通常与电话、接口、菜单等关联，而在 Asterisk 中，扩展号是一组在特定扩展号或名称被触发时要处理的命令。这些命令按优先级顺序处理。

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

扩展号可以是文字、标准或特殊。标准扩展号仅包含数字或名称以及字符 * 和 #；例如 12#89* 是合法的文字扩展号。名称也可以用于扩展匹配。扩展号区分大小写。不过，不能创建两个名称相同但大小写不同的扩展号。当拨打扩展号时，首先执行优先级为 1 的命令，然后执行优先级为 2 的命令，依此类推。此过程会一直进行，直到通话被挂断或某个命令返回数字一，表示失败。Asterisk 在执行最后一个优先级时的行为受参数 autofallthrough 控制。参见本章的 [general] 部分。示例：

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

上面列出了在拨打扩展号 123 时要处理的指令列表。第一个优先级是应答通道（当通道处于振铃状态时必须应答，例如 FXO 通道）。第二个优先级是播放名为 tt-weasels 的音频文件。第三个优先级挂断通道。另一种方式是根据来电显示处理呼叫。可以使用 / 字符指定要处理的来电显示。示例：

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

此示例将在来电显示为 100 时触发扩展号 123 并执行以下选项。这也可以通过下面描述的模式实现：

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: 将扩展号映射到通道。用于监控通道状态。与 presence 配合使用。电话必须支持此功能。

#### 模式

可以在 dialplan 中使用模式和文字。模式对于缩减 dialplan 大小非常有用。所有模式均以 “_” 字符开头。以下字符可用于定义模式。图中标识了可在 Asterisk 中使用的模式。

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### 特殊扩展号

Asterisk 将某些扩展号名称用作标准扩展号。

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

描述：

- **s**：Start。用于在没有拨号的情况下处理呼叫。对 FXO 中继和菜单内处理很有用。
- **t**：Timeout。用于在提示播放后呼叫仍保持不活动时触发，也用于挂断不活动的线路。
- **T**：AbsoluteTimeout。如果使用 `TIMEOUT(absolute)` dialplan 函数设定了通话时长限制，一旦通话超过该限制，就会转到 T 扩展号。
- **h**：Hangup。用户挂断通话后调用。
- **i**：Invalid。当在上下文中拨打不存在的扩展号时触发。使用这些扩展号会影响 CDR 记录的内容——具体来说，dst 字段将不包含实际拨打的号码。
- **o**：Operator。当用户在语音信箱期间按 “0” 时，用于转接到接线员。

使用这些扩展号会改变

## Variables

在 Asterisk PBX 中，变量可以是全局的、通道特定的和环境特定的。您可以使用 NoOP() 应用程序在控制台上查看变量的内容。它可以使用全局变量或通道特定变量作为应用程序参数。变量可以像下面的示例中那样引用，其中 varname 是变量的名称。

```
${varname}
```

变量名可以是以字母开头的字母数字字符串。全局变量名不区分大小写。然而，系统变量（Asterisk 定义的或通道定义的）区分大小写。因此，变量 ${EXTEN} 与 ${exten} 是不同的。

### Global variables

全局变量可以在 extensions.conf 文件的 [global] 部分配置，或使用以下应用程序：

```
set(Global(variable)=content)
```

### Channel-specific variables

通道特定变量使用 set() 应用程序配置。每个通道都有自己的变量空间。不同通道的变量之间不会发生冲突。通道特定变量在通道挂断时被销毁。最常用的一些变量包括：

- ${EXTEN} 已拨号的分机
- ${CONTEXT} 当前上下文
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} 当前来电显示
- ${PRIORITY} 当前优先级

其他通道特定变量全部使用大写。您可以使用 dumpchan() 应用程序查看多个变量的内容。下面是 dump-channel 变量的一个简单摘录。

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Dumpchan output:

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

上面的字段布局是 Asterisk 22 `DumpChan` 输出（真实的 `PJSIP/...` 通道名称、`CallerIDNum`/`ConnectedLineID` 字段以及 PJSIP 通道填充的 `Raw*`/`Transcode`/`BridgeID` 行）。与旧驱动不同，PJSIP 通道不会自动设置 `SIPCALLID`/`SIPUSERAGENT` 通道变量；等效的 SIP 细节会在需要时通过 `PJSIP_HEADER()` 和 `CHANNEL()` dialplan 函数读取——例如 `${CHANNEL(pjsip,call-id)}`、`${PJSIP_HEADER(read,User-Agent)}` 和 `${CHANNEL(rtp,dest)}` 用于远程 RTP 地址。

### Environment-specific variables

环境特定变量可用于访问操作系统中定义的变量。您可以使用函数 ENV() 设置环境特定变量。例如：

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

某些应用程序使用变量进行数据输入和输出。您可以在调用应用程序之前设置变量，或在应用程序执行后检索变量。例如：Dial 应用程序返回以下变量：

- ${DIALEDTIME} -> 从拨号通道到通道断开之间的时间。
- ${ANSWEREDTIME} -> 实际通话的时长。
- ${DIALSTATUS} 通话状态：o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> 通话的错误信息。

## Expressions

Expressions can be very useful in the dial plan. They are used to manipulate strings and perform math and logical operations.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

The expression syntax is defined as follows:

```
$[expression1 operator expression2]
```

Let’s suppose that we have a variable called “I” and we want to add 100 to the variable:

```
$[${I}+100]
```

When Asterisk finds an expression in the dial plan, it changes the entire expression by the resulting value.

### Operators

The following operators can be used to build expressions. It is important to observe operator precedence.

1. Parentheses “()”
2. Unary operators “! -“
3. Regular expression “: =~
4. Multiplicative operators “* / %”
5. Additive operators “+ -“
6. Comparison operators
7. Logical operators
8. Conditional operators

#### Math Operators

- Addition (+)
- Subtraction (-)
- Multiplication(*)
- Division (/)
- Modulus (%)

#### Logical Operators

- Logical “AND” (&)
- Logical “OR” (|)
- Logical Unary Complement (!)

#### Regular expression operators

- Regular expression matching (:)
- Regular expression exact matching (=~)

A regular expression is a special text string used to describe a search pattern. You can think of regular expressions as wildcards. Regular expressions are used to match a string to a pattern to check the matching. If the match succeeds and the regular expression contains at least one match, the first match is returned; otherwise, the result is the number of characters matched.

#### Comparison operators

The result of a comparison is 1 if the relation is true or 0 if it is false.

- = equal
- != not equal
- < less than
- > greater than
- <= less than or equal to
- >= greater than or equal to

### LAB. Evaluate the following expressions:

Put these expressions in your dial plan and use the NoOP() application to evaluate the expressions. Dial 9002 and examine the results in the Asterisk console. Use verbose 15 to show the results.

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

## Functions

一些应用已被函数取代，函数允许以比仅使用表达式更高级的方式处理变量。您可以通过执行以下控制台命令查看函数的完整列表：

```
*CLI> core show functions
```

字符串长度：${LEN(string)} 返回字符串的长度

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

在第一次操作中，系统显示 5 作为结果（单词 “fruit” 的字母数）。第二次返回数字 4（单词 “pear” 的字母数）。子串：返回子串，从 “offset” 参数定义的位置开始，长度由 “length” 参数定义。如果 offset 为负，则从右向左开始，从字符串末尾开始。如果省略 length 或 length 为负，则从 offset 开始取整条字符串。

```
${string:offset:length }
```

示例 #1：多个子串

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

示例 #3：从变量 ${EXTEN} 中取出除区号外的所有数字。

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### String concatenation

要连接两个字符串，只需将它们写在一起。

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## 应用程序

要构建拨号计划，我们需要了解应用程序的概念。您将在拨号计划中使用应用程序来处理通道。应用程序在多个模块中实现。可用的应用程序取决于模块。您可以使用控制台命令显示所有 Asterisk 应用程序：

```
*CLI> core show applications
```

或者，您可以使用以下示例显示特定应用程序的详细信息：

```
*CLI> core show application Dial
```

要构建一个简单的拨号计划，您需要了解几个应用程序。我们将在本书后面的章节中讨论更高级的示例。

![构建简单拨号计划所需的少量应用程序：Answer（应答通道）、Dial（呼叫另一个通道）、Hangup（挂断通道）、Playback（播放音频文件）和Goto（跳转到优先级、分机或上下文）。](../images/04-first-pbx-fig09.png)

我们将使用上述这些应用程序为两个基本的 PBX 创建一个简单的拨号计划。

### Answer()

[Synopsis] 当有来电响铃时应答通道  
[Description] Answer([delay]): 如果呼叫尚未被接听，应用程序将接听它。否则，对呼叫没有任何影响。如果指定了延迟，Asterisk 将在接听呼叫之前等待 ‘delay’ 中指定的毫秒数。

### Dial()

以下描述可以通过在拨号计划中执行 `show application dial` 获得。为方便检索，已在下方重新列出。Dial 应用程序的语法也在下方显示：

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

该应用程序将向一个或多个指定的通道发起呼叫。只要其中一个请求的通道应答，发起通道就会应答——如果它尚未应答的话。这两个通道随后将在桥接通话中保持活动状态。所有其他请求的通道随后将被挂断。除非指定了超时时间，否则 Dial 应用程序将无限期等待，直到被叫通道中的某一个应答、用户挂断，或所有被叫通道均忙或不可用。如果无法呼叫任何请求的通道或超时到期，dialplan 的执行将继续。该应用程序在完成后会设置以下通道变量：

- DIALEDTIME - 从拨号到通道断开的时间。
- ANSWEREDTIME - 实际通话的时长。
- DIALSTATUS - 通话状态：o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

对于隐私和筛选模式，如果被叫方选择将呼叫方发送到 “Go Away” 脚本，DIALSTATUS 变量将被设为 DONTCALL。如果被叫方想将呼叫方发送到 “torture” 脚本，DIALSTATUS 变量将被设为 TORTURE。该应用程序将在发起通道挂断或通话已桥接且桥接中的任一方结束通话时报告正常终止。如果通道支持，可将可选的 URL 发送给被叫方。如果设置了 OUTBOUND_GROUP 变量，则该应用程序创建的所有对等通道都将被包含在该组中（如在）

```
Set(GROUP()=...).
```

以下表格概述了应用 Dial 最常用的一些选项。完整列表请使用控制台命令 `core show application Dial`。在 Asterisk 22 中，这些选项与通道和超时之间用逗号分隔——例如 `Dial(PJSIP/2000,20,tTm)`。

| Option | Description |
|--------|-------------|
| `A(x)` | 向被叫方播放公告，使用 `x` 作为文件。 |
| `C` | 重置此通话的 CDR。 |
| `d` | 允许呼叫用户在等待通话接通时拨打 1 位分机。如果该分机在当前 context 中存在，则跳转到该分机；如果不存在，则跳转到 `EXITCONTEXT` 变量中定义的 context（如果该变量存在）。 |
| `D([called][:calling])` | 在被叫方接听后、通话桥接前发送指定的 DTMF 字符串。 `called` 字符串发送给被叫方， `calling` 字符串发送给呼叫方。任一参数均可单独使用。 |
| `f` | 强制将呼叫通道的来电显示设置为通过 dial plan `hint` 与该通道关联的分机。适用于 PSTN 不允许任意来电显示的情况。 |
| `g` | 如果目标通道挂断，则在当前分机继续执行 dial plan。 |
| `G(context^exten^pri)` | 若通话被接听，将呼叫方转移到指定的 priority，将被叫方转移到 priority+1。可选地指定一个分机（或分机和 context）；否则使用当前分机。 |
| `h` | 允许被叫方通过发送 `*` DTMF 数字挂断。 |
| `H` | 允许呼叫方通过发送 `*` DTMF 数字挂断。 |
| `L(x[:y][:z])` | 将通话限制为 `x` 毫秒，当剩余 `y` 毫秒时播放警告，并每隔 `z` 毫秒重复警告。参见下方的 `LIMIT_*` 变量。 |
| `m([class])` | 为呼叫方提供保持音乐，直至请求的通道接通。可指定特定的 MusicOnHold 类。 |
| `r` | 向呼叫方指示振铃，并在被叫通道接通前不传递音频。 |
| `S(x)` | 在被叫方接通后 `x` 秒挂断通话。 |
| `t` | 允许被叫方通过发送 `features.conf` 中定义的 DTMF 序列转移呼叫方。 |
| `T` | 允许呼叫方通过发送 `features.conf` 中定义的 DTMF 序列转移被叫方。 |
| `w` | 允许被叫方通过发送 `features.conf` 中定义的 DTMF 序列启用一键录音。 |
| `W` | 允许呼叫方通过发送 `features.conf` 中定义的 DTMF 序列启用一键录音。 |
| `k` | 允许被叫方通过发送 `features.conf` 中为通话停放定义的 DTMF 序列将通话停放。 |
| `K` | 允许呼叫方通过发送 `features.conf` 中为通话停放定义的 DTMF 序列将通话停放。 |

`L(x[:y][:z])` 选项可以通过以下特殊变量进行调节：

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no`（默认 `yes`）：为呼叫方播放声音。
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`：为被叫方播放声音。
- `LIMIT_TIMEOUT_FILE` — 时间到时播放的文件。
- `LIMIT_CONNECT_FILE` — 通话开始时播放的文件。
- `LIMIT_WARNING_FILE` — 当定义了 `y` 时作为警告播放的文件。默认是朗读剩余时间。

示例：

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

在上面的示例中，应用程序将拨打相应的 PJSIP 通道。呼叫方和被叫方都可以转移通话 (Tt)。此时会听到保持音乐，而不是回铃。如果在 20 秒内无人应答，分机将进入下一个优先级。

### Hangup()

挂断呼叫通道 [Description] Hangup([causecode]): 此应用程序将挂断呼叫通道。如果提供了原因代码，通道的挂断原因将被设置为给定的值。

### Goto()

跳转到特定的优先级、分机或上下文 [Description] Goto([[context|]extension|]priority): 此应用程序会使呼叫通道在指定的优先级继续执行 dialplan。如果未指定具体的分机（或分机和上下文），则该应用程序会跳转到当前分机的指定优先级。如果跳转到 dialplan 中的其他位置失败，通道将继续在当前分机的下一个优先级执行。

## 构建拨号计划

要构建一个简单的拨号计划，您需要通过创建 context 和 extension 来处理所有进出电话。在本节中，我们将向您展示如何构建最常用的 extension。

### 在 extension 之间拨号

要实现 extension 之间的拨号，我们可以使用通道变量 ${EXTEN}，它指代被拨出的 extension。例如，如果 extension 范围在 4000 到 4999 之间且所有 extension 都使用 SIP，我们可以采用以下命令：

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### 拨打外部目的地

要拨打外部目的地，可以在拨出的号码前加上一个路由。在北美，通常使用 9 开头后接要外部拨出的号码。如果使用模拟或数字通道连接 PSTN，命令应如下所示：如果想使用 SIP trunk 而不是 DAHDI，请使用 `PJSIP/...@siptrunk` 通道。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

上述行将允许您拨打 9 和所需的号码。在给出的示例中，您将使用第一个 DAHDI 通道（DAHDI/1）。如果您有多条线路且此线路忙碌，呼叫将无法完成。不过，您可以使用以下行来自动选择第一个可用的 DAHDI 通道。也可以选择使用 SIP trunk 代替 DAHDI。在 PJSIP 表单 `Dial(PJSIP/number@siptrunk,...)` 中，拨打的号码是用户部分，`siptrunk` 是上面配置的 endpoint。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

The “g1” 参数将搜索组中第一个可用的通道，允许使用所有通道。使用下面的行，您可以拨打长途号码。

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### 拨打 9 以获取 PSTN 线路

如果您对外部拨号没有任何限制，您可以简化并使用如下：

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### 接听运营员分机的来电

在下面的示例中，运营员分机是 4000。PSTN 线路连接到 FXO 接口。在 `chan_dahdi.conf` 文件中，指定的 context 为 `from-pstn`。任何来自 PSTN 的呼叫都将被路由到 dialplan 中的 `from-pstn` context。该线路没有直接的入站拨号（DID）；因此，我们必须通过 “s” 分机来接收呼叫。如果是从 SIP trunk 接收，请使用 context `from-sip`。

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

### 使用直接呼入拨号 (DID) 接收呼叫

如果您拥有数字线路，您将收到被拨打的分机。当出现这种情况时，您无需将呼叫转接给接线员；相反，您可以直接将呼叫转接到目标。假设您的 DID 范围是 3028550 到 3028599，且 DID 中传递了后四位数字。配置将如下示例所示：

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### 同时呼叫多个分机

您可以设置 Asterisk 拨打一个分机，如果未被接听，则同时拨打其他多个分机，如下例所示：

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

在本示例中，当有人拨打运营商时，首先尝试通道 **DAHDI/1**。如果在 15 秒后无人接听（超时），通道 **DAHDI/1、DAHDI/2** 和 **DAHDI/3** 将同时响铃，再持续 15 秒。

### 按来电号码路由

在本示例中，您可以根据来电号码提供不同的处理方式，这对防止呼叫骚扰者非常有用。例如：

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

在本例中，我们添加了一条特殊规则，如果来电显示为 4832518888，则播放先前录制的文件 “I-have-moved-to-china” 中的语音。其他来电照常接受。

### 在 dial plan 中使用变量

Asterisk 可以在 dial plan 中将全局变量和通道变量用作某些应用程序的参数。请看下面的示例：

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

使用变量可以让以后更改更容易。如果更改变量，所有引用会立即更新。

### 录制公告

在本节后面讨论的某些选项中，我们将使用已录制的提示音。这里向您展示一种简便的录制方法。我们将使用 Record() 应用程序，通过自己的电话保存公告。

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

这些说明允许您从软电话录制任何消息。例如：从软电话拨打 recordmenu。说明将使用变量 ${EXTEN:6} 调用录音，去掉前六个字母。换句话说，该说明等同于 record(menu:gsm)。您只需拨打 record + 要录制的文件名，按 # 完成录音，然后等待听到录音。

### 在数字接待员中接收来电

现在我们有了一些简单的示例，让我们进一步学习应用程序 background() 和 goto()。在 Asterisk 中交互式系统的关键是应用程序 background()，它允许您执行一个音频文件，当呼叫者按下键时，音频会被中断，以便将通话发送到所拨的分机。background() 应用程序的语法：

```
exten=>extension, priority, background(filename)
```

另一个非常有用的应用是 goto()。正如其名称所示，它跳转到指示的 context、extension 和 priority。goto() 应用的语法：

```
exten=>extension, priority,goto(context, extension, priority)
```

Valid formats for the goto() command: 翻译为：“goto() 命令的有效格式：”。

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

在下面的示例中，我们将创建一个数字接待员。编辑文件 extensions.conf 并配置以下分机非常简单：

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

SIP 分机使用 `PJSIP/` 而 IAX 分机使用 `IAX2/` —— 两者的驱动程序都随 Asterisk 22 提供，尽管 `chan_iax2` 现在已被视为遗留技术，推荐使用 SIP/PJSIP。

在文件 menu1.gsm 中，录制提示信息 “press the extension or wait for the operator”。当用户拨打号码 6000 时，他将被送至分机 6000。此时，你应该已经清楚了解多个应用的使用，包括 answer()、background()、goto()、hangup() 和 playback()。如果仍不够清晰，请重新阅读本章，直至对内容感到满意。你将会频繁使用 background 应用。一旦掌握了分机、优先级和应用的基础知识，创建一个简单的 dial plan 将变得轻而易举。这些概念将在本书后续章节中深入探讨，你会看到 dial plan 的功能会变得更加强大。

## 摘要

在本章中，你已经了解到配置文件存放在 /etc/asterisk 目录下。要使用 Asterisk，首先需要配置通道（例如 pjsip、dahdi、iax）。配置文件有三种不同的语法：简单组、对象继承和复杂实体。dial plan 在 extensions.conf 文件中创建，是一组 context 和 extension 的集合。在 dial plan 中，每个 extension 会触发一个 application。你已经学会使用 playback、background、dial、goto、hangup 和 answer 这些 application。

## Quiz

1. The channel configuration files are (choose all that apply):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. On Asterisk 22, the single `chan_sip` peer `[6001]` (`type=friend`/`host=dynamic`) is replaced in `pjsip.conf` by which set of related objects?
   - A. A `type=peer` and a `type=user`
   - B. A `type=endpoint`, a `type=auth`, and a `type=aor`
   - C. A single `type=friend`
   - D. A `type=transport` and a `type=global`
3. Defining a context in the channel configuration file matters because it sets the incoming context for calls from that channel — a call from the channel is processed in the matching context in `extensions.conf`.
   - A. True
   - B. False
4. The main differences between the `Playback()` and `Background()` applications are (choose two):
   - A. Playback plays a prompt but does not wait for digits.
   - B. Background plays a prompt but does not wait for digits.
   - C. Background plays a message and waits for digits to be pressed.
   - D. Playback plays a message and waits for digits to be pressed.
5. When a call enters Asterisk through a telephony interface card (FXO) with no DID, it is handled in the special extension:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Valid formats for the `Goto()` application are (choose three):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. The pattern `_7[1-5]XX` matches (choose all that apply):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. In `Dial(PJSIP/${EXTEN},20,tTm)`, what does the `m` option do?
   - A. Limits the call to a maximum duration.
   - B. Provides music on hold to the caller instead of ringback until the channel answers.
   - C. Sends DTMF digits after the called party answers.
   - D. Forces the caller ID using a dial plan hint.
9. In the option-inheritance grammar used by `chan_dahdi.conf`, you:
   - A. Define the object in a single line.
   - B. Define options first and declare the objects below the defined options.
   - C. Define a separate context for each object.
10. Priorities in an extension must be numbered consecutively (1, 2, 3, …) and cannot use `n`.
    - A. True
    - B. False

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
