# Asterisk PBX 简介

近年来，FreePBX 和 Issabel 等开箱即用的发行版日益流行。在本书中，我们将介绍经典的 Asterisk，它是理解这些发行版的基石。Asterisk PBX 是一款开源软件，能够将普通的 PC 转换为功能强大的多协议 PBX。在本章中，我们将了解这项新技术的功能及其基本架构。

## 学习目标

学完本章后，你应该能够：

- 解释什么是 Asterisk 以及它的作用；
- 描述 Digium™ 及其继任者 Sangoma 的角色；
- 识别 Asterisk 的基本架构及其组件；
- 指出几种使用场景；以及
- 确定获取信息和帮助的来源。

## 什么是 Asterisk

Asterisk 是一款开源 PBX 软件，一旦安装在 PC 硬件上并配备正确的接口，即可作为家庭用户、企业、VoIP 服务提供商和电话公司的全功能 PBX 使用。Asterisk 既是一个开源社区，也是一个由 Sangoma Technologies（于 2018 年收购了 Digium）赞助的项目。你可以自由使用和修改 Asterisk 以满足你的需求。Asterisk 允许 PSTN 和 VoIP 网络之间的实时连接。由于 Asterisk 不仅仅是一个 PBX，你不仅可以对现有的 PBX 进行卓越的升级，还可以在电话通信领域实现新的功能，例如：

- 通过宽带互联网将居家办公的员工连接到办公室 PBX；
- 通过 IP 网络、专用网络甚至互联网本身连接不同地点的多个办公室；
- 为员工提供与 Web 和电子邮件集成的 voicemail；
- 构建诸如 IVR 之类的应用程序，以允许连接到你的订单系统或其他应用程序；
- 让出差用户通过简单的宽带或 VPN 连接从任何地方访问公司 PBX；以及
- 更多功能……

Asterisk 包含了一些以前仅在高端系统中才能找到的多种高级资源，例如：

- 为在呼叫队列中等待的客户提供保持音乐，支持媒体流和 MP3 文件；
- 呼叫队列，团队座席可以接听电话并监控队列；
- 与文本转语音和语音识别的集成；
- 传输到文本文件和 SQL 数据库的详细记录；以及
- 通过数字和模拟线路进行的 PSTN 连接。

## 什么是 AsteriskNOW（历史）和 FreePBX

以最纯粹形式存在的 Asterisk，也被称为“经典 Asterisk”（Debian 软件包命名），与其说是一个成品，不如说是一个开发工具。AsteriskNOW 曾是一项旨在将 Asterisk 转换为软电器的计划。该发行版包括作为操作系统的 CentOS 和作为图形界面的 FreePBX。AsteriskNOW 此后已停止更新。

如今，标准的交钥匙 Asterisk 发行版是 **FreePBX**（由 Sangoma 维护），它将 Asterisk 与基于 Web 的管理 GUI 和模块生态系统捆绑在一起。FreePBX 根据 GPL 授权，可以从 www.freepbx.org 免费下载。对于商业部署，Sangoma 还提供 **FreePBX Distro**（完整的 Linux 镜像）及其商业产品 **PBXact**。

## Digium™ 和 Sangoma 的角色

Digium 是一家位于阿拉巴马州亨茨维尔的公司，自 1999 年成立以来，一直是 Asterisk 的创始者和主要开发者。除了作为 Asterisk 开发的主要赞助商外，Digium 还生产用于 Asterisk PBX 的电话接口卡和其他硬件，并创建了诸如 Switchvox（针对 SMB 市场）等商业产品。2018 年，Digium 被加拿大统一通信公司 **Sangoma Technologies** 收购。自收购以来，Sangoma 继续赞助 Asterisk 的开发，并担任其主要管理者，在 www.asterisk.org 维护该开源项目。

从历史上看，Digium 在三种类型的许可协议下提供 Asterisk：

- 通用公共许可证 (GPL) Asterisk。这是使用最广泛的版本。它包含所有功能，并可根据 GPL 许可条款免费使用和修改。
- Asterisk Business Edition 是 Asterisk 的商业版本。一些公司使用商业版是因为他们不想或不能使用 GPL 许可——通常是因为他们不想将其源代码与 Asterisk 一起发布。**注意：** Asterisk Business Edition 已停止提供；如今 Asterisk 仅在 GPL 下分发。
- Asterisk OEM 许可。在 Digium 停止零售 Asterisk Business Edition 后，它继续向 OEM 客户（希望在 Asterisk 之上构建专有产品而不根据 GPL 发布其源代码的设备供应商）授权该商业版本。

### Zapata 项目及其与 Asterisk 的关系

Zapata 项目由 Jim Dixon 开发，他同时也负责 Asterisk 所使用的革命性硬件设计。该硬件也是开源的；因此，任何公司都可以使用它，如今有几家制造商生产与此架构兼容的卡。

Zapata 项目产生了一种名为 Zaptel 的架构，后来更名为 DAHDI（Digium/Asterisk Hardware Device Interface）。该架构的主要优势之一是能够利用 PC CPU 来处理媒体流、回声消除和转码。相比之下，大多数现有卡使用数字信号处理器 (DSP) 来执行这些任务。使用 PC CPU 代替专用 DSP 极大地降低了板卡价格。因此，这些卡比其他制造商以前提供的接口便宜得多。另一方面，这些卡需要大量的 CPU 资源；滥用 PC CPU 会显著影响语音质量。最近，Digium 推出了一款使用 DSP 对 G.729 和 G.723 进行编码和解码的协处理器卡，从而为大量通道提供了更好的可扩展性。

## 为什么选择 Asterisk？

我记得我第一次接触 Asterisk 的情景。通常，对新事物的最初反应——尤其是那些与你已知事物竞争的事物——是拒绝它！这正是 2003 年发生的事情。当时 Asterisk 正在与我向客户销售的一种解决方案（4 E1 VoIP Gateway）竞争，而且它的价格比我当时所知的解决方案便宜十倍。这种不成比例的价格促使我开始研究 Asterisk，以找出潜在的陷阱和缺点。例如，我发现当时的 PC CPU 无法支持 120 个 G.729 同时通话，最终，我凭借我的 Gateway 解决方案赢得了提案。然而，这次练习让我发现 Asterisk 可以为我的客户群解决各种非常昂贵的问题。我们当时正为 IVR、统一消息、通话录音和拨号器的昂贵报价而苦恼；通过适当的维度设计，CPU 问题是可以解决的。事实上，仅仅三年时间，Asterisk 就成为了我公司的旗舰产品（我实际上决定专门为 Asterisk 业务开设了另一家公司）。在我看来，Asterisk 是电信领域的一场革命，它对 IP 电话的意义正如 Apache 对 Web 服务的意义。

### 极致的成本削减

如果你将传统 PBX 与 Asterisk 在数字接口和电话方面进行比较，Asterisk 比那些 PBX 稍微便宜一些。然而，当你添加 voicemail、ACD、IVR 和 CTI 等高级功能时，Asterisk 的优势才真正显现出来。有了这些高级功能，Asterisk 比传统 PBX 便宜得多。事实上，将 Asterisk PBX 与低端模拟 PBX 进行比较是不公平的，因为 Asterisk 提供了许多低端模拟系统所不具备的功能。

### 电话系统控制和独立性

客户最常提到的 Asterisk 的好处之一是它提供的独立性。当今的一些制造商甚至不向客户提供系统密码或配置文档。通过 Asterisk 的“自己动手”方法，用户获得了完全的自由；作为奖励，用户还可以访问标准接口。

### 简单快速的开发环境

Asterisk 可以使用 PHP 和 Perl 等脚本语言通过 AMI 和 AGI 接口进行扩展。Asterisk 是开源的，其源代码可以由用户修改。源代码主要使用 ANSI C 编程语言编写。

### 功能丰富

Asterisk 具有许多传统 PBX 中不存在或作为可选功能的特性（例如，voicemail、CTI、ACD、IVR、内置保持音乐和录音）。在某些平台上，这些功能的成本甚至超过了平台本身的价格。

### 电话上的动态内容

Asterisk 使用 C 语言以及当今开发环境中常见的其他语言进行编程。提供动态内容的可能性几乎是无限的。

### 灵活且强大的 dialplan

Asterisk 的另一个突破是其强大的 dialplan。在传统 PBX 中，即使是像最小成本路由 (LCR) 这样简单的功能，要么不可行，要么是可选的。使用 Asterisk，选择最佳路由既简单又清晰。

### 运行在 Linux 之上的开源软件

Asterisk 最伟大的特性之一是它的社区。有多种资源可用，包括官方 Asterisk 文档 (docs.asterisk.org)、社区维护的 VoIP-Info wiki (www.voip-info.org <http://www.voip-info.org>)、电子邮件分发列表和论坛。随着 Asterisk 的日益普及，漏洞被迅速发现并修复。凭借庞大的用户群和活跃的开发团队，Asterisk 是世界上测试最广泛的 PBX 平台之一，这有助于保持代码库的稳定和成熟。

### Asterisk 架构的局限性

Asterisk 的一些局限性源于 Zapata 电话设计的使用。在这种设计中，Asterisk 使用 PC CPU 来处理语音通道，而不是其他平台中常见的专用数字信号处理器 (DSP)。虽然这极大地降低了硬件接口的成本，但系统变得依赖于 PC CPU。我的建议是在专用机器上运行 Asterisk，并在硬件维度设计上保持保守。你也可以在单独的 VLAN 中使用 Asterisk，以避免消耗 CPU 的过多广播（由环路或病毒引起的广播风暴）。来自多家供应商的一些较新的接口卡现在开始包含用于处理回声消除、codec 和其他功能的 DSP，这将使 Asterisk 变得更好。

## 对 Asterisk PBX 的主要异议

听到对采用 Asterisk 的异议是很常见的，我们将在这里一一解决。

### Asterisk 的市场份额太小

市场份额通常通过销售的 PBX 数量来衡量。这些统计数据通常是从最大的分销商那里获取的。Asterisk 是免费软件，可以在没有任何销售记录的情况下下载和部署，因此在这些数字中被系统性地低估了。即便如此，Asterisk 仍在全球范围内拥有庞大的装机量——从单服务器办公室 PBX 到大型运营商和联络中心部署——并且仍然是开源 PBX 生态系统（包括 FreePBX 等交钥匙发行版）背后的主导引擎。

### 如果它是免费的，制造商如何生存？

实际上，传统意义上并没有所谓的开源软件制造商。Digium 自 1999 年以来开发了 Asterisk，通过销售电话接口卡、Switchvox 等商业 PBX 产品以及相关软件来维持自身。2018 年，Sangoma Technologies 收购了 Digium。Sangoma 继续资助 Asterisk 的开发，并通过商业产品（FreePBX 商业模块、PBXact、Switchvox）、硬件销售和专业服务产生收入。

### 很难找到技术支持！

Sangoma 通过其合作伙伴生态系统并直接通过其产品供应为 Asterisk 提供商业技术支持。全球认证专业人员网络提供一线支持和专业服务。社区支持通过 www.asterisk.org 上的 Asterisk 论坛和邮件列表保持活跃。

### Asterisk 支持超过 200 个 extension 吗？

是的，绝对支持。单个维度设计合理的 Asterisk 服务器可以处理大量的 extension，并且 Asterisk 通过在多台服务器上分配用户并进行负载均衡和故障转移来进一步扩展，从而允许大型多站点部署。

### 只有“极客”才能安装 Asterisk

有了 FreePBX（可作为 Sangoma 的独立发行版提供），即使是对 Linux 了解有限的专业人员也能够安装和配置中等复杂程度的 PBX。在 GUI 的帮助下，只需几个小时即可配置整个 PBX。

### 如果服务器故障怎么办？

Asterisk 的主要优势之一是其在容错系统中运行的能力。拥有两台并行运行的服务器相对简单且成本低廉。我敢让你在传统 PBX 上尝试一下！

### 我们公司不使用开源软件

你的公司可能在不知不觉中就在使用开源软件。许多设备使用 Linux 作为其操作系统。此外，Sangoma 及其认证合作伙伴网络还提供商业支持和托管部署。

### 不建议使用 PC 的 CPU 来处理信令和媒体

Asterisk 使用服务器的 CPU 来处理语音通道的信令和媒体，而不是拥有专用的 DSP。虽然这允许将成本降低多达五倍，但它使系统依赖于主 CPU 的性能。通过正确的维度设计，Asterisk 能够处理大量的流量。如果你仍然想将主 CPU 从这些任务中解放出来，你也可以使用硬件回声消除甚至转码卡，例如基于 DSP 的 Sangoma（前身为 Digium）TC400B。

## Asterisk 架构

本节将解释 Asterisk 的架构是如何工作的。下图显示了基本的 Asterisk 架构。接下来，我们将解释与架构相关的概念，包括通道、codec 和应用程序。

![Asterisk 架构](../images/01-introduction-fig01.png)

### 通道

通道相当于电话线，但采用数字格式。它通常由模拟或数字 (TDM) 信令系统，或者 codec 和信令协议的组合（例如，SIP-GSM，IAX-uLaw）组成。最初，所有的电话连接都是模拟的，容易受到回声和噪声的影响。后来，大多数系统被转换为数字系统，在大多数情况下，模拟声音使用脉冲编码调制 (PCM) 转换为数字格式。这种格式允许在不压缩的情况下以 64 kbps 的速度进行语音传输。

与公共交换电话网 (PSTN) 接口的通道：

- `chan_dahdi`：来自 Sangoma（前身为 Digium）、Xorcom 等公司的模拟 (FXO/FXS) 和数字 (E1/T1/PRI) TDM 卡。针对 DAHDI 分别构建——请参阅 *Legacy channels* 一章。

与 Voice over IP 接口的通道：

- `chan_pjsip`：SIP——Asterisk 22 LTS 中主要且唯一的 SIP 通道驱动程序。拨号字符串：`PJSIP/endpoint_name`。（**注意：** 旧的 `chan_sip` 已在 Asterisk 21 中移除，在 Asterisk 22 中不存在。有关配置，请参阅 *Building your first PBX with PJSIP*。）
- `chan_iax2`：IAX2 协议——仍随 Asterisk 22 发布，但属于 legacy；SIP/PJSIP 是新部署的首选。拨号字符串：`IAX2/peer`。
- `chan_unistim`：Nortel/Avaya UNISTIM 电话。仍然可用（扩展支持），但很少使用。

较旧的 VoIP 通道不再是标准 Asterisk 22 构建的一部分：`chan_h323` (H.323) 仅作为社区 `ooh323` 插件存在，而 `chan_mgcp` (MGCP) 和 `chan_skinny` (Cisco SCCP) 已被弃用并从现代通道集中删除。如果你必须与这些协议互通，通常的做法是在 Asterisk 前面放置一个网关。

其他通道：

- **Local**：一种伪通道（内置于核心中），它回环到不同 context 中的 dialplan——对于递归路由和将呼叫分发到多个目的地非常有用。拨号字符串：`Local/extension@context`。

### Codec 和 codec 转换

我们通常尝试在数据网络中放置尽可能多的语音连接。Codec 在数字语音中启用了新功能，包括压缩，这是最重要的功能之一，因为它允许大于 8 比 1 的压缩率。许多 codec 还定义了诸如语音活动检测（静音抑制）、丢包隐藏和舒适噪声生成等功能，尽管 Asterisk 本身并不生成舒适噪声或执行静音抑制。Asterisk 有多种 codec 可用，并且可以透明地从一种转换为另一种。在内部，当 Asterisk 需要从一种 codec 转换为另一种时，它使用 slinear 作为流格式。Asterisk 中的某些 codec 仅在透传模式下受支持；这些 codec 无法转换。要验证你的系统中安装了哪些 codec，你可以使用控制台命令：

```
CLI>core show translation
```

支持以下 codec：

- G.711 ulaw (USA) - (64 Kbps)。
- G.711 alaw (Europe) - (64 Kbps)。
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - 仅透传模式
- G.726 - (16/24/32/40kbps)
- G.729 - 由 Sangoma 分发的二进制 codec 模块；下载是免费的，但合法使用需要购买每通道许可 (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### 协议

只要数据能自行找到通往另一部电话的路径，将数据从一部电话发送到另一部电话应该是很容易的。不幸的是，情况并非如此，为了在电话之间建立连接、发现终端设备并实现电话信令，必须使用信令协议。SIP 是现代部署中的主导信令协议，也是 Asterisk 22 LTS 中唯一可用的 SIP 通道（通过 chan_pjsip）。IAX2 仍然可用，但被视为 legacy。Asterisk 支持以下协议。

- SIP — 通过 `chan_pjsip`
- IAX2 — legacy，仍随 Asterisk 22 发布
- UNISTIM — Nortel/Avaya 电话（扩展支持）
- H.323、MGCP 和 SCCP (Cisco Skinny) — legacy 协议，不再包含在标准 Asterisk 22 构建中（H.323 仅通过社区 `ooh323` 插件提供）

### 应用程序

要将呼叫从一部电话桥接到另一部电话，使用应用程序 dial()。大多数 Asterisk 功能（例如，voicemail 和会议）都是作为应用程序实现的。你可以通过使用 core show applications 控制台命令查看可用的 Asterisk 应用程序。

```
CLI>core show applications
```

你可以从 Asterisk 插件、第三方提供商添加应用程序，甚至可以开发自己的应用程序。

## Asterisk 系统概述

Asterisk 是一款开源 PBX，其作用类似于混合 PBX，集成了 TDM 和 IP 电话等技术。Asterisk 已准备好实现交互式语音应答 (IVR) 和自动呼叫分配 (ACD) 等功能；此外，如前所述，它对开发新应用程序是开放的。此图显示了 Asterisk 如何使用模拟和数字接口连接到 PSTN 和现有 PBX，并支持模拟和 IP 电话。它可以充当软交换、媒体网关、voicemail 和音频会议，并具有内置的保持音乐功能。

![Asterisk 系统概述](../images/01-introduction-fig02.png)

## 比较旧世界和新世界

在旧的软交换模型中，所有组件都是单独销售的，这意味着你必须分别购买每个组件，然后集成到 PBX 或软交换环境中。成本和风险很高，而且大多数设备都是专有的。

![旧世界：组件分别购买和集成](../images/01-introduction-fig03.png)

### 使用 Asterisk 的电话通信

所有功能都集成在 Asterisk 平台中，根据维度设计在相同或不同的盒子中，并且全部采用 GPL 许可。有时安装 Asterisk 比许可某些主流 IP-PBX 更容易。

![使用 Asterisk 的电话通信：功能已集成](../images/01-introduction-fig04.png)

## 构建测试系统

在实施 Asterisk 解决方案时，我们的第一步通常是构建一台测试机器。最简单的测试机器是 1x1 PBX，包括至少一部电话和一条线路。有几种方法可以做到这一点。

![简单的 Asterisk 测试系统](../images/01-introduction-fig05.png)

### 一个 FXO，一个 FXS

构建测试机器的第一种也是最简单的方法是购买一张带有一个 FXO 和一个 FXS 接口的卡。将 FXO 端口连接到现有线路，并将一个 FXS 连接到模拟电话。这样，你就拥有了一个 1x1 PBX。

### VoIP 服务提供商：ATA

这是 VoIP 选项。在这种情况下，你将与语音服务提供商签约以获得 SIP trunk，并且必须购买 SIP 模拟电话适配器。如果你已经有了 PC，你可能花费不到一百美元。

### 廉价的 FXO 卡或 ATA

我从一张廉价的 FXO 卡开始。一些廉价的 V.90 传真/调制解调器可以作为 FXO 卡与 Asterisk 一起使用。一些早期的 Digium 卡就是使用这些卡创建的（例如，X100P 和 X101P），它们是基于 Motorola 和 Intel 芯片组的旧调制解调器（已知 Motorola 68202-51、Intel 537PU、Intel 537PG 和 Intel Ambient MD3200 可以工作）。这些调制解调器通常与新主板不兼容。最近，一些制造商开始将这些卡作为 X100P 克隆版销售。一些不兼容问题可以使用补丁解决，更多信息可以在以下网址找到：

- http://www.voip.school/mediawiki/index.php/Asterisk_patch_for_the_X100P_card

## Asterisk 场景

Asterisk 可用于多种不同的场景。我们将列出其中一些，并解释每种场景的优势和可能的局限性。

### IP PBX

最常见的场景是安装新的 PBX 或更换现有的 PBX。如果你将 Asterisk 与其他一些替代方案进行比较，你会发现它比目前市场上大多数 PBX 更便宜，功能更丰富。现在有几家公司正在将其规范更改为 Asterisk，而不是其他品牌的 PBX。

![Asterisk 作为 IP PBX](../images/01-introduction-fig06.png)

### 为传统 PBX 启用 IP 功能

下图说明了最常用的设置之一。大公司通常在投资新技术时不想承担重大风险，同时希望保留对传统设备的投资。为传统 PBX 启用 IP 功能可能非常昂贵；因此，使用 T1/E1 线路连接 Asterisk PBX 对于注重成本的客户来说可能是一个不错的选择。另一个好处是可以连接到具有更好电话费率的 VoIP 服务提供商。

![为传统 PBX 启用 IP 功能](../images/01-introduction-fig07.png)

### 话费旁路 (Toll Bypass)

VoIP 的一个非常有用的应用是通过互联网或 WAN 连接分支机构。使用现有的数据连接可以让你绕过总部和分支机构之间电信连接产生的话费。

![通过 WAN 在办公室之间进行话费旁路](../images/01-introduction-fig08.png)

### 应用程序服务器（IVR、会议、Voicemail）

Asterisk 可以用作现有 PBX 的应用程序服务器，或者直接连接到 PSTN。Asterisk 提供诸如 voicemail、传真接收、通话录音、连接到数据库的 IVR 以及音频会议服务器等服务。如果你将 voicemail 和传真集成到现有的电子邮件服务器中，你将拥有一个统一消息系统，这通常是一个昂贵的解决方案。与其他解决方案相比，将 Asterisk 用作应用程序服务器可提供极大的成本削减。

![Asterisk 作为应用程序服务器](../images/01-introduction-fig09.png)

### 媒体网关

大多数 VoIP 服务提供商使用 SIP 代理来托管所有 SIP 用户的注册、位置和身份验证。他们仍然必须直接将呼叫发送到 PSTN，或者使用 SIP 或 H.323 VoIP 连接通过批发呼叫终止提供商进行路由。Asterisk 可以充当背靠背用户代理 (B2BUA) 或媒体网关，取代非常昂贵的软交换或媒体网关。比较一下主要市场制造商的四 E1/T1 网关的价格与 Asterisk 的价格。Asterisk 解决方案的成本可能比其他解决方案低几倍，并且能够转换信令协议（H.323、SIP、IAX……）和 codec（G.711、G.729……）。

![Asterisk 作为媒体网关](../images/01-introduction-fig10.png)

### 联络中心平台

联络中心是一个非常复杂的解决方案，结合了多种技术，例如自动呼叫分配 (ACD)、交互式语音应答 (IVR) 和呼叫监督。基本上，有三种类型的联络中心：入站、出站和混合。入站联络中心非常复杂，通常需要 ACD、IVR、CTI、录音、监督和报告。Asterisk 具有内置的 ACD 来对呼叫进行排队。IVR 可以使用 Asterisk Gateway Interface (AGI) 或内部机制（例如应用程序 background()）来完成。计算机电话集成 (CTI) 使用 Asterisk Manager Interface (AMI) 实现；录音和报告内置于 Asterisk 中。对于出站联络中心，预测拨号器或自动拨号器是主要组件之一。虽然有几个拨号器可用于开源 Asterisk，但如果你愿意，为该平台构建自己的拨号器并不难。混合联络中心允许同时进行入站和出站操作，通过确保更好地利用座席的时间来节省资金。可以使用 Asterisk 及其 ACD 机制来实现混合解决方案。

![Asterisk 联络中心平台](../images/01-introduction-fig11.png)

## 寻找信息和帮助

本节将提供一些与 Asterisk 相关的主要信息来源。

- Asterisk 官方网站：<https://www.asterisk.org> 在这里你可以找到关于以下方面的信息：
- 文档和 Wiki -> <https://docs.asterisk.org>
- 社区论坛 -> <https://community.asterisk.org>
- 漏洞跟踪 -> <https://github.com/asterisk/asterisk/issues>
- Wiki（legacy，大部分已被 docs.asterisk.org 取代） -> <https://wiki.asterisk.org>

### 社区论坛

Asterisk 社区论坛在很大程度上取代了旧的邮件列表，是提问的地方。在发帖之前，尽量收集尽可能多的信息。如果你没有做功课，没有人会帮助你——至少尝试一次自己解决问题。

- <https://community.asterisk.org>

## 总结

Asterisk 是一款根据 GPL 授权的软件，它使普通 PC 能够充当强大的 IP PBX 平台。Digium 的 Mark Spencer 在 20 世纪 90 年代末创建了 Asterisk，Digium 通过销售与 Asterisk 相关的硬件和商业产品来维持自身。Digium 于 2018 年被 Sangoma Technologies 收购；Sangoma 现在赞助 Asterisk 的开发。硬件接口设计起源于 Jim Dixon 开发的 Zapata 项目，该项目催生了 DAHDI。

Asterisk 架构具有以下主要组件：

- 通道：模拟、数字或 VoIP。在 Asterisk 22 LTS 中，SIP 仅由 chan_pjsip 处理。
- 协议：通信协议，负责呼叫信令，包括 SIP（通过 PJSIP）、H323、MGCP 和 IAX2。
- Codec：转换语音的数字格式，允许压缩和丢包隐藏。请注意，Asterisk 本身不执行静音抑制（语音活动检测）或舒适噪声生成；当 endpoint 使用 VAD 时，应在客户端禁用舒适噪声。
- 应用程序：负责 Asterisk PBX 功能。会议、voicemail 和传真是 Asterisk 应用程序的示例。

Asterisk 可用于各种场景，从小型 IP PBX 到复杂的联络中心。你可以轻松地在 www.asterisk.org 和 docs.asterisk.org 找到帮助。

## 测验

1. 哪家公司在 2018 年收购了 Digium，现在担任 Asterisk 开源项目的主要管理者？
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. 在 Asterisk 22 LTS 中，哪个通道驱动程序提供 SIP 连接？
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. 对或错：`chan_sip` 通道驱动程序已在 Asterisk 21 中移除，并且不存在于标准 Asterisk 22 构建中。

4. 以下哪些通道/协议**不再**是标准 Asterisk 22 构建的一部分？（选择所有适用项。）
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`，仅作为社区 `ooh323` 插件存在)

5. Zapata 项目的硬件架构，最初称为 Zaptel，后来更名为 ____。
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. 当 Asterisk 必须将音频从一种 codec 转换为另一种时，它通过哪种内部流格式进行转换？
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. 根据本章，Sangoma 分发的 G.729 codec 模块的许可情况如何？
   - A. 它是 GPL 的，完全免费供任何使用。
   - B. 下载是免费的，但合法使用需要购买每通道许可。
   - C. 不购买 Asterisk Business Edition 根本无法获得。
   - D. 它仅在透传模式下工作，无法安装。

8. 哪个 Asterisk 应用程序用于将呼叫从一部电话桥接到另一部电话？
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Asterisk 中的 `Local` 通道是什么？
   - A. 用于模拟电话的硬件 FXS 接口。
   - B. 到本地服务提供商的 SIP trunk。
   - C. 一种伪通道，将呼叫回环到不同 context 中的 dialplan。
   - D. 用于网内呼叫的 codec。

10. 在哪种使用场景中，Asterisk 充当背靠背用户代理 (B2BUA)，在信令协议和 codec 之间进行转换以取代昂贵的软交换？
    - A. 为传统 PBX 启用 IP 功能
    - B. 话费旁路
    - C. 媒体网关
    - D. 联络中心平台

**答案：** 1 — B · 2 — C · 3 — 对 · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
