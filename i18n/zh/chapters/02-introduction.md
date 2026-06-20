# Asterisk PBX 简介

近年来，FreePBX 和 Issabel 等即装即用发行版的受欢迎程度不断提升。在本书中，我们将重点讲解经典的 Asterisk，它是理解这些发行版的基础。Asterisk PBX 是开源软件，能够将普通 PC 转变为功能强大的多协议 PBX。在本章中，我们将了解这项新技术的可能性及其基本架构。

## 目标

通过本章学习，您应该能够：

- 解释 Asterisk 是什么以及它的功能；
- 描述 Digium™ 及其继任者 Sangoma 的角色；
- 认识 Asterisk 的基本架构及其组件；
- 指出几种使用场景；以及
- 确认信息来源和求助渠道。

## 什么是 Asterisk

Asterisk 是开源 PBX 软件，可将普通计算机转变为功能齐全的 PBX，适用于家庭用户、企业、VoIP 服务提供商和电话公司。Asterisk 也是一个开源社区，并且是由 Sangoma Technologies（该公司于 2018 年收购了 Digium）赞助的项目。您可以自由使用和修改 Asterisk 以满足您的需求。Asterisk 允许 PSTN 与 VoIP 网络之间的实时连接。由于 Asterisk 远不止是一个 PBX，您不仅可以对现有 PBX 进行卓越升级，还可以在电话领域实现新功能，例如：

- 将在家工作的员工通过宽带互联网连接到办公室 PBX；
- 将位于不同地点的多个办公室通过 IP 网络、专用网络，甚至直接通过互联网进行连接；
- 为员工提供与网页和电子邮件集成的语音信箱；
- 构建诸如 IVR 的应用程序，以便连接到您的订单系统或其他应用；
- 为出差的用户提供只需简单宽带或 VPN 连接即可随时访问公司 PBX 的方式；以及
- 更多功能……

Asterisk 包含了以前仅在高端系统中才能找到的多项高级资源，例如：

- 为在呼叫队列中等待的客户提供音乐保持，支持媒体流和 MP3 文件；
- 呼叫队列，团队坐席可以接听电话并监控队列；
- 与文本转语音和语音识别的集成；
- 将详细记录转存至文本文件和 SQL 数据库；以及
- 通过数字和模拟线路实现 PSTN 连接。

## 什么是 AsteriskNOW（历史）和 FreePBX

Asterisk 在最纯粹的形式下，也被称为“经典 asterisk”（Debian 包名称），被视为一种开发工具，而不是一个完整的产品本身。AsteriskNOW 是将 Asterisk 转变为软设备的倡议。该发行版包含 CentOS 作为操作系统，并使用 FreePBX 作为图形界面。AsteriskNOW 已经停止维护。

如今，标准的即插即用 Asterisk 发行版是 **FreePBX**（由 Sangoma 维护），它将 Asterisk 与基于 Web 的管理 GUI 和模块生态系统捆绑在一起。FreePBX 根据 GPL 授权，可自由从 www.freepbx.org 下载。对于商业部署，Sangoma 还提供 **FreePBX Distro**（完整的 Linux 镜像）以及其商业产品 **PBXact**。

## Role of Digium™ and Sangoma

Digium，一家位于阿拉巴马州亨茨维尔的公司，自1999年成立以来一直是 Asterisk 的创始者和主要开发者。除了作为 Asterisk 开发的主要赞助商外，Digium 还为 Asterisk PBX 生产电话接口卡及其他硬件，并推出了面向 SMB 市场的商业产品 Switchvox。2018 年，Digium 被 **Sangoma Technologies** 收购，后者是一家加拿大统一通信公司。收购后，Sangoma 继续赞助 Asterisk 开发，并作为其主要维护者，在 www.asterisk.org 上维护开源项目。

历史上，Digium 以三种许可协议提供 Asterisk：

- General Public License (GPL) Asterisk。此版本使用最广，包含所有功能，且可根据 GPL 许可证的条款免费使用和修改。
- Asterisk Business Edition 是 Asterisk 的商业版本。部分公司使用该商业版是因为他们不想或不能使用 GPL 许可证——通常是因为不想将自己的源代码与 Asterisk 一起发布。**Note:** Asterisk Business Edition 已停止发行；如今 Asterisk 仅以 GPL 方式发布。
- Asterisk OEM licensing。在 Digium 停止零售销售 Asterisk Business Edition 后，仍向 OEM 客户——即希望在 Asterisk 基础上构建专有产品而不将自己的源代码以 GPL 方式发布的设备供应商——提供该商业版的授权。

### The Zapata project and its relationship with Asterisk

Zapata 项目由 Jim Dixon 开发，他同样负责用于 Asterisk 的革命性硬件设计。该硬件也是开源的；因此，任何公司都可以使用，今天已有多家制造商生产兼容该架构的卡。

Zapata 项目推出了名为 Zaptel 的架构，后更名为 DAHDI（Digium/Asterisk Hardware Device Interface）。该架构的主要优势之一是能够使用 PC CPU 处理媒体流、回声消除和转码。相比之下，大多数现有卡使用数字信号处理器（DSP）来完成这些任务。使用 PC CPU 代替专用 DSP 可大幅降低板卡成本。因此，这些卡的价格显著低于其他厂商之前提供的接口。另一方面，这些卡需要大量 CPU 资源；不当使用 PC CPU 会显著影响语音质量。近期，Digium 推出了一款使用 DSP 编码和解码 G.729 与 G.723 的协处理器卡，为大量通道提供了更好的可扩展性。

## Why Asterisk?

我记得第一次接触 Asterisk。通常，对新事物——尤其是与已有认知竞争的东西——的第一反应是拒绝！这正是 2003 年发生的情况。Asterisk 与我向客户销售的解决方案（4 条 E1 VoIP 网关）竞争，而它的价格是我当时已知方案的十分之一。这种巨大的价格差让我开始研究 Asterisk，以识别潜在的陷阱和缺点。例如，我发现当时的 PC CPU 无法支持 120 条 g.729 同时会话，最终我还是凭借我的网关方案赢得了投标。

然而，这次尝试让我发现 Asterisk 能为我的客户群解决各种高成本问题。我们在 IVR、统一消息、通话录音和拨号器方面的报价非常昂贵；通过适当的容量规划，CPU 问题可以得到规避。事实上，仅三年时间，Asterisk 就成为了我公司旗舰产品（我甚至决定另开一家专门做 Asterisk 业务的公司）。在我看来，Asterisk 是电信领域的一场革命，正如 Apache 对 Web 服务的意义一样。

### Extreme cost reduction

如果仅比较传统 PBX 与 Asterisk 在数字接口和电话方面的成本，Asterisk 稍微便宜一些。但当加入语音信箱、ACD、IVR 和 CTI 等高级功能时，Asterisk 的性价比优势就非常明显。事实上，将 Asterisk PBX 与低端模拟 PBX 作比较并不公平，因为 Asterisk 提供了许多低端模拟系统根本没有的功能。

### Telephony system control and independence

客户最常提到的 Asterisk 好处之一是它提供的独立性。如今一些厂商甚至不给客户系统密码或配置文档。采用 Asterisk 的“自己动手”方式，用户可以获得完全自由；另外，用户还能使用标准接口。

### Easy and rapid development environment

Asterisk 可以通过 PHP、Perl 等脚本语言以及 AMI、AGI 接口进行扩展。Asterisk 是开源的，用户可以修改其源代码。源代码主要使用 ANSI C 编写。

### Feature rich

Asterisk 拥有许多传统 PBX 没有或仅可选的功能（如语音信箱、CTI、ACD、IVR、内置音乐保持和录音）。在某些平台上，这些功能的成本甚至超过平台本身的价格。

### Dynamic content on the phone

Asterisk 使用 C 语言以及当今开发环境中常见的其他语言编写。提供动态内容的可能性几乎是无限的。

### Flexible and powerful dial plan

Asterisk 的另一个突破是其强大的 dial plan。传统 PBX 中，连最基本的最小费用路由（LCR）都可能不可行或仅为可选项。使用 Asterisk，选择最佳路由既简单又清晰。

### Open-source running on top of Linux

Asterisk 最大的优势之一是其社区。可用资源丰富，包括官方 Asterisk 文档（docs.asterisk.org）、社区维护的 VoIP-Info wiki（www.voip-info.org <http://www.voip-info.org>）、邮件列表和论坛。随着 Asterisk 的日益普及，bug 能被快速发现并修复。凭借庞大的用户基数和活跃的开发团队，Asterisk 成为全球测试最广泛的 PBX 平台之一，这有助于保持代码库的稳定和成熟。

### Asterisk architecture limitations

Asterisk 的一些限制来源于 Zapata 电话设计。在该设计中，Asterisk 使用 PC CPU 处理语音通道，而不是其他平台常见的专用数字信号处理器（DSP）。虽然这大幅降低了硬件接口成本，但系统会依赖 PC CPU。我的建议是将 Asterisk 运行在专用机器上，并对硬件容量进行保守规划。也可以将 Asterisk 放在独立的 VLAN 中，以避免消耗 CPU 的过度广播（由环路或病毒引起的广播风暴）。一些供应商的新版接口卡已经开始内置 DSP，用于回声消除、编解码和其他功能，这将使 Asterisk 更加出色。

## 对 Asterisk PBX 的主要反对意见

人们常常会听到对采用 Asterisk 的反对声音，我们将在此进行回应。

### Asterisk 的市场份额太小

市场份额通常以售出的 PBX 数量来衡量。这些统计数据一般来自最大的分销商。Asterisk 是可以免费下载并部署的自由软件，因而在这些数字中会系统性地被低估。即便如此，Asterisk 在全球拥有非常庞大的装机基础——从单服务器办公室 PBX 到大型运营商和呼叫中心部署——并且仍是开源 PBX 生态系统背后占主导地位的引擎（包括 FreePBX 等一键式发行版）。

### 如果是免费的，制造商如何生存？

实际上，传统意义上并不存在“开源软件制造商”。Digium 自 1999 年起开发 Asterisk，通过销售电话接口卡、商业 PBX 产品（如 Switchvox）以及相关软件来维持自身运营。2018 年，Sangoma Technologies 收购了 Digium。Sangoma 继续资助 Asterisk 开发，并通过商业产品（FreePBX 商业模块、PBXact、Switchvox）、硬件销售和专业服务获取收入。

### 很难找到技术支持！

Sangoma 通过其合作伙伴生态系统以及直接的产品方案，为 Asterisk 提供商业技术支持。全球认证专业人员网络提供一线支持和专业服务。社区支持仍然活跃，用户可在 www.asterisk.org 的 Asterisk 论坛和邮件列表中获得帮助。

### Asterisk 能支持超过 200 个分机吗？

可以，绝对可以。单台配置合理的 Asterisk 服务器能够处理大量分机，且 Asterisk 还能通过负载均衡和故障转移将用户分布到多台服务器上，从而实现大规模多站点部署。

### 只有“极客”才能安装 Asterisk

使用 FreePBX（Sangoma 提供的独立发行版），即使是对 Linux 知识有限的专业人士也能安装并配置中等复杂度的 PBX。借助图形界面，只需几小时即可完成整个 PBX 的配置。

### 如果服务器故障怎么办？

Asterisk 的主要优势之一是能够在容错系统中运行。让两台服务器并行运行相对简单且成本低廉。我敢打赌，你很难在传统 PBX 上做到这一点！

### 我们公司不使用开源软件

贵公司可能在不自知的情况下已经在使用开源软件。许多设备的操作系统都是 Linux。此外，Sangoma 及其认证合作伙伴网络提供商业支持和托管部署服务。

### 不建议使用 PC 的 CPU 处理信令和媒体

Asterisk 使用服务器的 CPU 来处理语音通道的信令和媒体，而不是使用专用 DSP。虽然这可以将成本降低至原来的五分之一，但也使系统依赖于主 CPU 的性能。通过正确的规模规划，Asterisk 能够处理大流量。如果仍希望让主 CPU 免除这些任务，也可以使用硬件回声消除，甚至使用基于 DSP 的硬件转码卡，例如 Sangoma（前 Digium） 的 TC400B。

## Asterisk Architecture

本节将解释 Asterisk 的架构是如何工作的。下图展示了基本的 Asterisk 架构。接下来，我们将说明与架构相关的概念，包括通道、编解码器和应用程序。

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

通道相当于电话线，但以数字形式存在。它通常由模拟或数字（TDM）信令系统或编解码器与信令协议的组合构成（例如 SIP‑GSM、IAX‑uLaw）。最初，所有电话连接都是模拟的，容易出现回声和噪声。随后，大多数系统转为数字系统，模拟声音在大多数情况下使用脉冲编码调制（PCM）转换为数字格式。该格式允许在不压缩的情况下以 64 千比特/秒的速率传输语音。

与公共交换电话网（PSTN）接口的通道：

- `chan_dahdi`: 来自 Sangoma（前 Digium）、Xorcom 等厂商的模拟（FXO/FXS）和数字（E1/T1/PRI）TDM 卡。单独针对 DAHDI 构建——参见 *Legacy channels* 章节。

与 VoIP 接口的通道：

- `chan_pjsip`: SIP —— Asterisk 22 LTS 中的主要且唯一的 SIP 通道驱动。拨号字符串：`PJSIP/endpoint_name`。（**注意：** 旧的 `chan_sip` 已在 Asterisk 21 中移除，在 Asterisk 22 中不存在。请参见 *Building your first PBX with PJSIP* 了解配置。）
- `chan_iax2`: IAX2 协议 —— 仍随 Asterisk 22 提供，但已属遗留；新部署推荐使用 SIP/PJSIP。拨号字符串：`IAX2/peer`。
- `chan_unistim`: Nortel/Avaya UNISTIM 电话。仍可使用（扩展支持），但很少见。

较旧的 VoIP 通道已不再是标准 Asterisk 22 构建的一部分：`chan_h323`（H.323）仅作为社区 `ooh323` 插件存在，`chan_mgcp`（MGCP）和 `chan_skinny`（Cisco SCCP）已被弃用并从现代通道集合中移除。如果必须与这些协议互通，通常的做法是在 Asterisk 前部署网关。

其他通道：

- **Local**: 一个伪通道（内置于核心），在不同 context 中回环到拨号计划——用于递归路由以及将一次呼叫分发到多个目的地。拨号字符串：`Local/extension@context`。

### Codec and codec translation

我们通常尝试将尽可能多的语音连接放在数据网络中。编解码器为数字语音提供了新功能，包括压缩，这是最重要的特性之一，因为它可以实现超过 8:1 的压缩率。许多编解码器还定义了诸如语音活动检测（静音抑制）、丢包隐藏和舒适噪声生成等功能，尽管 Asterisk 本身不生成舒适噪声或执行静音抑制。Asterisk 提供多种编解码器，并可以在它们之间透明转换。内部在需要从一种编解码器转换到另一种时，Asterisk 使用 slinear 作为流格式。某些编解码器仅以直通模式受支持；这些编解码器无法转换。要验证系统中已安装的编解码器，可使用控制台命令：

```
CLI>core show translation
```

以下编解码器受支持：

- G.711 ulaw (USA) - (64 Kbps)。
- G.711 alaw (Europe) - (64 Kbps)。
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - 仅透传模式
- G.726 - (16/24/32/40kbps)
- G.729 - 由 Sangoma 分发的二进制编解码器模块；下载免费，但合法使用需购买每通道许可证 (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocols

只要数据能够自行找到路径，电话之间的发送本应很简单。遗憾的是，实际并非如此，需要信令协议来在电话之间建立连接、发现终端设备并实现电话信令。SIP 是现代部署中占主导地位的信令协议，也是 Asterisk 22 LTS 中唯一可用的 SIP 通道（通过 chan_pjsip）。IAX2 仍然可用，但被视为遗留。Asterisk 支持以下协议。

- SIP — via `chan_pjsip`
- IAX2 — legacy，仍随 Asterisk 22 提供
- UNISTIM — Nortel/Avaya 电话（扩展支持）
- H.323、MGCP 和 SCCP（Cisco Skinny）— 传统协议，已不再包含在标准 Asterisk 22 构建中（H.323 仅通过社区 `ooh323` 插件）

### Applications

要将通话从一部电话桥接到另一部电话，使用应用 dial()。大多数 Asterisk 功能（例如 voicemail 和会议）都是以应用的形式实现的。您可以通过运行 core show applications 控制台命令查看可用的 Asterisk 应用。

```
CLI>core show applications
```

您可以添加来自 Asterisk 附加组件、第三方提供商，甚至是您自行开发的应用程序。

## Asterisk 系统概览

Asterisk 是一个开源 PBX，充当混合 PBX，集成了 TDM 和 IP 电话等技术。Asterisk 已准备好实现交互式语音应答 (IVR) 和自动呼叫分配 (ACD) 等功能；此外，如前所述，它对新应用的开发保持开放。下图展示了 Asterisk 如何使用模拟和数字接口连接到 PSTN 和现有 PBX，并支持模拟和 IP 电话。它可以充当软交换、媒体网关、voicemail、音频会议，并且内置 hold 音乐。

![Asterisk 系统概览](../images/01-introduction-fig02.png)

## 比较旧世界与新世界

在旧的软交换模型中，所有组件都是单独出售的，这意味着你必须分别购买每个组件，然后将它们集成到 PBX 或软交换环境中。成本和风险都很高，而且大多数设备都是专有的。

![The old world: components bought and integrated separately](../images/01-introduction-fig03.png)

### 使用 Asterisk 的电话系统

所有功能都集成在 Asterisk 平台中，依据规模可以部署在同一台或不同的服务器上，且全部采用 GPL 许可证。有时安装 Asterisk 比获取某些主流 IP‑PBX 的许可证更为简便。

![Telephony using Asterisk: the functions are integrated](../images/01-introduction-fig04.png)

## 构建测试系统

在实现 Asterisk 解决方案时，我们的第一步通常是构建一个测试系统。目标是一个最小的 **1×1 PBX** —— 一部电话可以呼叫另一部电话 —— 这样你就可以在触及生产环境之前尝试端点、dialplan 和功能。如今这完全是软件实现：不需要任何电话硬件。

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### 现代方式：软件实验室（推荐）

最快的测试系统是运行在容器或虚拟机中的 Asterisk 22，使用 **softphones** 作为端点，并可选地使用 **SIP trunk** 连接公共网络：

- **Asterisk 22** 运行在小型 Linux 机器、VM 或 Docker 容器上。本书提供了一个现成的 Docker 实验室（参见实验室指南），只需一条命令即可启动已完整配置的 Asterisk 22 —— 无需编译，无需硬件。
- **两个 softphones** 注册为 PJSIP 端点，这样你可以在它们之间进行真实通话。全书使用 **SipPulse Softphone**（免费下载：<https://www.sippulse.com/produtos/softphone>），支持桌面和移动端。
- **一个 SIP trunk**（可选），来自 VoIP 提供商，用于想要接入 PSTN 的情况。无需卡片和模拟线路 —— 只需凭证。

这就是本书所有示例的构建和验证方式，你可以在任何笔记本电脑上复现。

### 传统方式：模拟/数字卡

在 VoIP 之前，测试 PBX 需要物理接口：一个 **FXO** 端口用于连接现有电话线，一个 **FXS** 端口用于连接模拟电话，两者组合即可形成 1×1 PBX。单卡同时提供一个 FXO 和一个 FXS 接口是经典的入门套件。这些基于 DAHDI 的卡（来自 Sangoma，前身为 Digium）仍然存在于必须终止模拟或 T1/E1 线路的场景，但今天已属小众 —— 大多数部署都是纯 VoIP。如果你只需要连接模拟电话或线路，请参见 *Legacy Channels* 章节；否则可以完全省去电话硬件。

## Asterisk 场景

Asterisk 可以用于多种不同的场景。我们将列出其中一些并解释各自的优势和可能的限制。

### IP PBX

最常见的场景是新建或替换现有的 PBX。如果将 Asterisk 与其他一些替代方案进行比较，你会发现它比目前市场上大多数 PBX 更便宜且功能更丰富。许多公司现在正将规格从其他品牌 PBX 改为 Asterisk。

![Asterisk as an IP PBX](../images/01-introduction-fig06.png)

### 为传统 PBX 添加 IP 功能

下图展示了最常用的部署之一。大型企业通常不愿在新技术上承担重大风险，同时希望保留对传统设备的投资。为传统 PBX 添加 IP 功能可能非常昂贵；因此，使用 T1/E1 线路连接 Asterisk PBX 可以成为注重成本的客户的良好替代方案。另一个好处是可以连接到提供更优惠电话费率的 VoIP 服务提供商。

![IP-enabling a legacy PBX](../images/01-introduction-fig07.png)

### 费用绕行

VoIP 的一个非常有用的应用是通过互联网或 WAN 连接分支机构。使用现有的数据连接可以绕过总部与分支机构之间电信连接产生的通话费用。

![Toll bypass between offices over a WAN](../images/01-introduction-fig08.png)

### 应用服务器（IVR、会议、语音信箱）

Asterisk 可以作为现有 PBX 的应用服务器使用，或直接连接到 PSTN。Asterisk 提供语音信箱、传真接收、通话录音、连接数据库的 IVR 以及音频会议服务器等服务。如果将语音信箱和传真集成到现有的电子邮件服务器中，你将拥有统一的消息系统，这通常是一种昂贵的解决方案。使用 Asterisk 作为应用服务器相比其他方案可大幅降低成本。

![Asterisk as an application server](../images/01-introduction-fig09.png)

### 媒体网关

大多数 VoIP 服务提供商使用 SIP 代理来托管所有 SIP 用户的注册、定位和认证。他们仍需将通话直接发送到 PSTN，或通过 SIP 或 H.323 VoIP 连接路由到批发呼叫终止提供商。Asterisk 可以充当后端用户代理（B2BUA）或媒体网关，取代非常昂贵的软交换或媒体网关。将市场主流厂商的四路 E1/T1 网关价格与 Asterisk 进行比较，Asterisk 方案的成本可以低数倍，并且能够转换信令协议（H.323、SIP、IAX…）和编解码器（G.711、G.729…）。

![Asterisk as a media gateway](../images/01-introduction-fig10.png)

### 联系中心平台

联系中心是一个非常复杂的解决方案，结合了多种技术，如自动呼叫分配（ACD）、交互式语音应答（IVR）和呼叫监督。基本上，联系中心有三种类型：呼入、呼出和混合。

呼入联系中心非常复杂，通常需要 ACD、IVR、CTI、录音、监督和报告。Asterisk 内置 ACD 用于排队呼叫。IVR 可以使用 Asterisk Gateway Interface（AGI）或内部机制如应用 background() 实现。计算机电话集成（CTI）通过 Asterisk Manager Interface（AMI）实现；录音和报告功能已内置于 Asterisk。

对于呼出联系中心，预测拨号或强力拨号器是主要组件之一。虽然开源 Asterisk 已有多个拨号器可用，但如果需要，也可以自行构建。混合联系中心允许同时进行呼入和呼出操作，通过更好地利用坐席时间来节省费用。可以使用 Asterisk 及其 ACD 机制实现混合解决方案。

![An Asterisk contact-center platform](../images/01-introduction-fig11.png)

## 查找信息和帮助

本节将提供与 Asterisk 相关的主要信息来源。

- Asterisk 官方网站：<https://www.asterisk.org> 在这里您可以找到以下信息：
- 文档与 Wiki -> <https://docs.asterisk.org>
- 社区论坛 -> <https://community.asterisk.org>
- Bug 跟踪 -> <https://github.com/asterisk/asterisk/issues>
- Wiki（旧版，已基本被 docs.asterisk.org 取代） -> <https://wiki.asterisk.org>

### 社区论坛

Asterisk 社区论坛已经基本取代了旧的邮件列表，是提问的首选地点。发布前请尽可能收集信息。如果您没有做好功课，没人会帮助您——请至少尝试一次自行解决问题。

- <https://community.asterisk.org>

## Summary

Asterisk 是一款根据 GPL 许可发布的软件，使普通 PC 能够充当功能强大的 IP PBX 平台。Digium 的 Mark Spencer 在 1990 年代后期创建了 Asterisk，Digium 通过销售与 Asterisk 相关的硬件和商业产品维持运营。Digium 于 2018 年被 Sangoma Technologies 收购；Sangoma 现在赞助 Asterisk 的开发。硬件接口设计起源于 Jim Dixon 开发的 Zapata 项目，进而产生了 DAHDI。

Asterisk 架构包含以下主要组件：

- CHANNELS：模拟、数字或基于 IP 的语音。在 Asterisk 22 LTS 中，SIP 完全由 `chan_pjsip` 处理。
- PROTOCOLS：通信协议，负责呼叫信令，包括 SIP（通过 PJSIP）、H.323、MGCP 和 IAX2。
- CODECS：转换语音的数字格式，实现压缩和丢包隐藏。需要注意的是，Asterisk 本身不执行静音抑制（语音活动检测）或舒适噪声生成；当终端使用 VAD 时，舒适噪声应在客户端侧禁用。
- APPLICATIONS：负责 Asterisk PBX 功能。会议、语音信箱和传真是 Asterisk 应用的示例。

Asterisk 可用于各种场景，从小型 IP PBX 到复杂的联络中心。您可以轻松在 www.asterisk.org 和 docs.asterisk.org 获取帮助。

## 测验

1. 哪家公司在 2018 年收购了 Digium，并且现在成为 Asterisk 开源项目的主要维护者？
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. 在 Asterisk 22 LTS 中，哪个通道驱动提供 SIP 连接性？
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. 判断正误：在 Asterisk 21 中已移除 `chan_sip` 通道驱动，标准的 Asterisk 22 构建中不再包含它。

4. 以下哪些通道/协议 **不再** 是标准 Asterisk 22 构建的一部分？（请选择所有适用项。）
   - A. MGCP（`chan_mgcp`）
   - B. SCCP / Cisco Skinny（`chan_skinny`）
   - C. IAX2（`chan_iax2`）
   - D. H.323（`chan_h323`, 仅以社区 `ooh323` 插件形式存续）

5. Zapata 项目的硬件架构，最初称为 Zaptel，后来改名为 ____。
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. 当 Asterisk 必须将音频从一种编解码器转换为另一种时，它通过哪种内部流格式进行翻译？
   - A. G.711 ulaw
   - B. GSM
   - C. slinear（signed linear）
   - D. Opus

7. 根据本章内容，Sangoma 分发的 G.729 编解码器模块的授权情况是？
   - A. 它是 GPL 的，任何用途均完全免费。
   - B. 下载免费，但合法使用需购买每通道许可证。
   - C. 完全无法获取，除非购买 Asterisk Business Edition。
   - D. 只能以直通模式工作，无法安装。

8. 哪个 Asterisk 应用用于将通话从一部电话桥接到另一部电话？
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. 什么是 Asterisk 中的 `Local` 通道？
   - A. 用于模拟电话的硬件 FXS 接口。
   - B. 指向本地服务提供商的 SIP 中继。
   - C. 在不同 context 中将通话循环回 dialplan 的伪通道。
   - D. 用于内部通话的编解码器。

10. 在哪种使用场景下，Asterisk 充当后端用户代理（B2BUA），在信令协议和编解码器之间转换，以取代昂贵的软交换？
    - A. 为传统 PBX 提供 IP 化
    - B. 费用规避
    - C. 媒体网关
    - D. 联系中心平台

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
