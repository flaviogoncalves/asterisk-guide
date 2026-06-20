# Designing a VoIP network

Voice over IP is quickly growing in the telephony market. The convergence paradigm is changing the way in which we communicate, reducing costs and enhancing the way in which we trade information. Voice is just the beginning of a full multimedia communication era, including voice, video, and presence. In the future, we are not going to transport people to work, but work to people because it is cleaner, faster, and cheaper. VoIP is just part of this revolution. Our challenge in this chapter is to design a VoIP network. To do this, we will have to understand concepts such as session protocols and codecs as well as how to dimension the number of circuits and bandwidth.

## 目标

- 理解 VoIP 的优势
- 描述 Asterisk 如何处理 VoIP
- 描述 SIP 和 IAX 通道的概念
- 为特定数据通道选择最合适的协议
- 为特定数据通道选择最合适的编解码器
- 估算所需的通道数量
- 计算所需的带宽

## VoIP benefits

为什么要关注 VoIP？VoIP 为公司和个人都提供了好处。成本降低无疑是其中之一，但在某些环境下，VoIP 还能简化计算机系统的集成。以下详细列出几项好处：

### Convergence

VoIP 的主要好处是将数据网络和语音网络合并以降低成本（convergence）。然而，仅仅分析语音通话费用可能不足以证明采用 VoIP 的合理性。运营商出售的通话分钟费用正迅速下降，这一点在决定采用 VoIP 前必须考虑。

### Infrastructure costs

使用单一网络基础设施可以降低新增、删除和变更相关的成本。随着 IP 的普及，VoIP 相关技术已被引入到多种新设备中，如手机、PDA、嵌入式系统和笔记本电脑。

### Open Standards

最后，VoIP 所基于的开放标准提供了选择不同供应商的自由。这一单一优势使得客户成为王者，而不再是 TELCOS 和 PBX 制造商的附属。

### Computer Telephony Integration

电话技术远早于计算技术。传统电话 PBX 基于电路交换，通常只有一台计算机用于监督。使用 VoIP，电话系统从底层就基于计算机标准构建。这使得计算机电话应用的使用比旧模式更便宜、更容易。您可以快速创建基于 Asterisk 的大量电话应用。您可以在传统 PBX 所需时间的一小部分内开发 IVR、ACD、CTI、拨号器、弹屏以及其他应用。

## Asterisk VoIP 架构

Asterisk 的架构如下所示。Asterisk 将所有 VoIP 协议视为通道。您可以使用任何编解码器或任何协议。这里需要学习的概念是，Asterisk 能够将任意类型的通道桥接到其他通道。因此，您可以在不同的编解码器之间相互转换信令协议，例如 SIP 和 IAX。举例来说，您可以将使用 G.711 编解码器的本地局域网内 SIP 电话的呼叫，转换为使用 G.729 编解码器的 SIP 中继，以连接到您的 VoIP 提供商。接下来的章节中，我们将详细说明 SIP 和 IAX 的架构。通过 chan_ooh323 插件提供的 H.323 支持仍然可用，但已日益少见；SIP/PJSIP 是现代部署的标准。

![Asterisk 的模块化架构：应用程序和通道通过 API 连接到 PBX 交换核心，动态加载编解码器转换和文件格式模块。](../images/06-voip-network-fig01.png)

## VoIP 协议与网络层次结构

VoIP 使用一组相互协作的不同协议。将它们对应到七层 OSI 参考模型上是很诱人的做法，许多较早的图示也正是如此——把 SIP 和 H.323 放在“会话”层，编解码器放在“表示”层。这种映射一直存在争议。标准化 SIP 的 IETF 并不使用 OSI 模型；它遵循更早的四层 TCP/IP（DoD）模型，RFC 3261 将 **SIP 定义为应用层协议**。媒体也遵循相同的模式：RTP 和编解码器位于应用负载中，通过 UDP 在传输层传输。下表将主要的 VoIP 协议映射到 IETF 实际使用的 TCP/IP 模型，并仅为参考给出大致的 OSI 等价层。

| TCP/IP (IETF) 层 | 协议 | 大致 OSI 等价层 |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

QoS 机制如 DiffServ 在 IP 层运行，以对语音数据包进行优先级排序并提升通话质量。以下是一些协议的具体说明：

- **SIP** 使用 UDP 或 TCP 的 5060 端口（TLS 使用 5061）来传输信令。音频则通过 RTP 在可配置的 UDP 端口范围内单独传输（Asterisk 附带的 `rtp.conf` 示例使用 10000 到 20000），并使用如 G.711 的编解码器进行编码。
- **H.323** 通过 TCP（H.225 信令使用 1720 端口）传输呼叫信令，而 H.225 RAS 通道使用 UDP 的 1719 端口；RTP 负责音频传输。
- **IAX2** 较为特殊：它在单一 UDP 端口（4569）上复用信令和媒体，这简化了 NAT 和防火墙的穿透。


## How to choose a protocol

鉴于协议众多，如何为你的网络选择最佳方案？本节将重点介绍每种协议的优势与不足。

### SIP - Session Initiated Protocol

SIP 是由 Internet Engineering Task Force (IETF) 制定的开放标准，主要定义在 RFC 3261 中。大多数现代 VoIP 提供商使用 SIP；事实上，它正成为最流行的 VoIP 标准。SIP 的优势在于它是基于 IETF 的标准。与较旧的 H.323 相比，SIP 更轻量。SIP 的主要弱点是 NAT 穿透——这对大多数 SIP VoIP 提供商来说是一个挑战。IETF 创建 SIP 时并未考虑计费，而是面向对等方的开放通信。计费通常是 VoIP 提供商关注的问题。

### IAX – Inter Asterisk eXchange

IAX 是一种最初由 Digium（现为 Sangoma）开发的开放协议。IAX 是一种“一体化”协议，因为它通过同一个 UDP 端口（4569）传输信令和媒体。Mark Spencer 将 IAX 设计为二进制协议，以降低带宽占用。IAX 的主要优势是其降低的带宽使用（它不使用 RTP）；由于只使用一个 UDP 端口（4569），它也非常容易实现 NAT 和防火墙穿透。

如果传统 PBX 厂商创建了 IAX，可能会把该协议宣传为“自冰激凌以来最好的东西”；在某些情况下，IAX 在中继模式下可以将语音带宽使用降低三分之一。IAX2（版本 2）仍通过 `chan_iax2` 模块随 Asterisk 22 提供，并在 Asterisk‑to‑Asterisk 中继、IAX2 电话以及 IAX 服务提供商中仍然有用，尽管它被视为遗留技术；新部署更倾向于使用 SIP/PJSIP。IAX2 在 [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456)（信息性）中有规范。

### MGCP – Media Gateway Control Protocol

MGCP 是一种与 H.323、SIP 和 IAX 配合使用的协议。其最大优势是可扩展性。它在呼叫代理而非网关上进行配置，从而简化了配置过程并实现集中管理。然而，Asterisk 对该协议的实现并不完整，且使用者并不多。

### H.323

H.323 在 VoIP 中仍被广泛使用。它是最早的 VoIP 协议之一，对连接基于网关的旧有 VoIP 基础设施至关重要。H.323 仍是网关市场的标准，尽管市场正逐步向 SIP 迁移。H.323 的优势包括广泛的市场采纳和成熟度。其劣势则与实现复杂性以及标准组织相关的成本有关。

### Protocol comparison table

以下表格概括了会话协议之间的差异。

| Protocol | Standard body | Asterisk 22 module / status | Used for |
|----------|---------------|-----------------------------|----------|
| SIP | IETF standard | `chan_pjsip` (core; the only SIP driver — `chan_sip` was removed in Asterisk 21) | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; still shipped, considered legacy) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | `chan_ooh323` (external community add-on, not in the base build) | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | (legacy MGCP phones) |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | (legacy Cisco phones) |

## One endpoint per device

在 Asterisk 22 中，PJSIP 堆栈将每部电话、干线或网关建模为`pjsip.conf`中的单个 **endpoint** 对象。一个 endpoint 既可以发起呼叫也可以接收呼叫；它的凭证存放在`auth`对象中，已注册的地址在`aor`中，网络路径在`transport`中。您为每个设备配置一个 endpoint 并附加它所需的各个部分——不存在需要区分的 “user” 与 “peer” 角色。（完整的对象模型在 *SIP & PJSIP in depth* 中有详细说明。）

## Codecs and codec translation

您将使用编解码器将模拟波形的语音转换为数字信号。编解码器在音质、压缩率、带宽和计算需求等方面各不相同。服务、电话和网关通常支持这些方面的多种组合。G.729 编解码器非常流行。它不是标准 Asterisk 22 构建的一部分；而是作为外部附加模块（`codec_g729`）提供，需从 Digium（现为 Sangoma）下载。Asterisk 的`menuselect`源码将其列在`support_level=external`中，并明确说明：“从 Digium 下载 g729a 编解码器。此编解码器必须购买许可证。” 换言之，合法使用 G.729 需要为每个通道购买许可证。（还有一个开源替代方案`bcg729`。）

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 支持以下编解码器（以及其他）：

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — 标准 PSTN 质量；ulaw 在北美常用，alaw 在欧洲和拉美常用
- ITU G.722: 64 Kbps — 宽带（高清语音），在与 G.711 相同的带宽下提供良好音质
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — 从 Digium/Sangoma 下载的外部`codec_g729`二进制模块（`support_level=external`；使用前必须购买许可证）
- Speex: 2.15 to 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps，可变 — 现代宽带/全频段编解码器；音质卓越且抗丢包；作为外部`codec_opus`二进制模块从 Digium/Sangoma 下载（`support_level=external`；不像 G.729 那样需要购买许可证）；推荐用于 WebRTC 和现代 SIP 端点。（GitHub 上还有开源构建替代方案。）

此外，Asterisk 允许在编解码器之间进行转换。在某些情况下，这不可行，例如 g723，仅支持直通模式。将一种编解码器转换为另一种会消耗大量 CPU 资源。因此，尽可能避免此类转换。

## How to choose a Codec

Codec selection depends on several options, such as:

- Sound quality
- Licensing costs
- CPU-processing consumption
- Bandwidth requirements
- Packet-loss concealment
- Availability for Asterisk and phone devices

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## 协议头部导致的开销

尽管编解码器几乎不占用带宽，但我们必须考虑以太网、IP、UDP 和 RTP 等协议头部带来的开销。因此，实际消耗的带宽取决于所使用的头部。在以太网网络上，需求高于 PPP 网络，因为 PPP 头部比以太网头部更短。例如，一个 G.729 语音包仅携带 20 字节的有效负载，却被大约 58 字节的以太网、IP、UDP 和 RTP 头部所包裹——因此是头部而非编解码器主导了带宽（见下图）。

![单个 g.729 语音包在以太网中的情况：20 字节的有效负载被 58 字节的以太网、IP、UDP 和 RTP 头部包裹——一次 g.729 通话消耗 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

您可以使用在线 VoIP 带宽计算器（如 <https://www.voip.school/bandcalc/bandcalc.php>）轻松计算其他带宽需求。


## 流量工程

VoIP 网络设计中的主要问题是为特定目的地（如远程办公室或服务提供商）确定线路数量和所需带宽。同时，还需确定 Asterisk 的并发通话数量（这是 Asterisk 规模化的主要参数）。

### 简化

最常用的简化方法是按用户类型估算通话数量。例如：

- 企业 PBX（每五个分机对应一个并发通话）
- 家庭用户（每十六个用户对应一个并发通话）

示例 #1 公司总部有 120 个分机，另外有两个分支机构——第一个分支有 30 个分机，第二个分支有 15 个分机。我们的目标是为总部的 E1 中继线路以及 Frame‑Relay 网络所需的带宽进行容量规划。

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a T1 线路数量

- 使用 T1 线路的分机总数：120+30+15=165 条
- 按企业使用每五个分机使用一条中继计算
- 总线路数 = 33 条，约为 2 条 T1 线路

1b 带宽需求 我们选择 g.729 编解码器，因为它在带宽需求、音质和中等 CPU 消耗之间取得了平衡。

每五个分机使用一条中继时：

- 分支 #1（Frame‑relay）所需带宽：26.8*6=160.8 Kbps
- 分支 #2（Frame‑relay）所需带宽：26.8*3= 80.4 Kbps

### Erlang B 方法

当拥有历史数据时，可以更科学地对中继进行容量规划，而不是使用简化方法。我们将使用 Agner Karup Erlang（哥本哈根电话公司，1909 年）的工作，他提出了计算两城之间中继组线路数量的公式。

**Erlang** 是电信中常用的流量计量单位；它描述了一小时内的流量量。例如，假设一小时内产生 20 通电话，每通平均通话 5 分钟：

- 小时内的通话分钟数：20 × 5 = 100 分钟
- 小时内的流量小时数：100 / 60 = **1.66 Erlangs**

可以从通话记录器中读取这些度量，并用它们来设计网络和计算所需线路数。确定线路数后，即可计算带宽需求。

**Erlang B** 是计算中继组线路数量最常用的方法。它假设通话随机到达（泊松分布），且被阻塞的通话会立即被清除。该方法要求已知 **Busy Hour Traffic (BHT)**，可以从通话记录器获取，或按简化方式估算：BHT = 一天通话分钟数的 17%。

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

另一个重要变量是服务等级（Grade of Service，GoS），它定义了因线路不足导致的阻塞通话概率。通常取 0.05（5% 通话丢失）或 0.01（1% 通话丢失）。示例 #1：使用本节前面介绍的总部与两个分支的示例，我们提供一些流量模式数据。从通话记录器中得到以下数据（通话分钟数和 BHT）：

- 总部到分支 #1 = 2,000 分钟，BHT = 300 分钟
- 总部到分支 #2 = 1,000 分钟，BHT = 170 分钟
- 分支 #1 到分支 #2 = 0，BHT=0

设定 GoS=0.01

- 总部到分支 #1 - BHT=300 分钟/60 = 5 Erlangs
- 总部到分支 #2 – BHT=170 分钟/60 = 2.83 Erlangs

使用如 <https://www.erlang.com> 的 Erlang 

## 减少 VoIP 所需带宽

可以使用三种方法来降低 VoIP 通话所需的带宽：

- RTP 头部压缩
- IAX Trunked
- VoIP 负载

### RTP 头部压缩

在 Frame-Relay 和 PPP 网络中，可以使用 RTP 头部压缩。RTP 头部压缩在 RFC 2508 中定义，是一种在多种路由器上可用的 IETF 标准。不过需要注意，有些路由器需要不同的功能集才能使用此资源。使用 RTP 头部压缩的效果非常显著，在我们的示例中，它将每段语音对话所需的带宽从 26.8 Kbps 降至 11.2 Kbps，降低了 58.2%！

### IAX2 trunk mode

如果你正在连接两台 Asterisk 服务器，可以在 trunk 模式下使用 IAX2 协议。这项革命性技术不需要任何特殊路由器，且可应用于任何类型的数据链路。

![IAX2 trunk mode on Ethernet: a single g.729 call needs its full header stack (31.2 Kbps), but a second call shares those headers and adds only a small IAX2 miniframe, averaging about 9.6 Kbps of extra bandwidth per additional call.](../images/06-voip-network-fig08.png)

IAX2 trunk mode 复用第二通话及以后通话的相同头部。使用 g729 在 PPP 链路上时，第一通话将消耗 30 Kbps 带宽，而第二通话使用与第一通话相同的头部，将额外通话所需的带宽降低到 9.6 Kbps。我们可以按如下方式计算 trunk 模式下的所需带宽：Branch #1 (11 calls) Bandwidth = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Branch #2 (8 calls) Bandwidth = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps 第一次通话使用 31.2 Kbps，随后每次增加 9.6 Kbps，依此类推。

### 增大语音负载

在通过 Internet 使用 VoIP 网关时，这种方法非常常见。使用更大的负载会牺牲时延，以换取带宽的降低。你可以通过在 allow 指令中为编解码器追加帧大小来更改 RTP 包化方式。

![Increasing the voice payload: packing 60 bytes of g.729 payload into one packet (instead of 20) amortizes the 58 bytes of headers across more voice, dropping bandwidth to about 16.05 Kbps per call at the cost of added latency.](../images/06-voip-network-fig09.png)

示例：

```
allow=ulaw:30
```

冒号后的数字是以毫秒为单位的包化间隔——每个 RTP 包中携带多少语音。更大的数值会将固定的头部开销摊分到更多音频上（带宽更低），但会增加时延。每种编解码器都有自己的最小、最大和默认帧大小；例如 G.711（`ulaw`/`alaw`）默认是 20 ms。

## Summary

在本章中，您了解到 Asterisk 使用通道来处理 VoIP。它支持 SIP（通过 `chan_pjsip` 在 Asterisk 22 中）和 IAX2；H.323 仅通过社区 `ooh323` 插件提供，较旧的 MGCP 和 SCCP（Skinny）通道已不再是标准 Asterisk 22 构建的一部分。您比较并学习了如何为 VoIP 通道选择信令协议和 codec。IAX2 在带宽利用上更高效，并且可以轻松穿越 NAT。SIP/PJSIP 是第三方电话和网关厂商支持最广的协议，也是 Asterisk 22 中唯一的 SIP 通道驱动。H.323 协议是最早的协议，应用于连接传统 VoIP 基础设施。在流量工程章节中，我们学习了如何设计和评估 VoIP 网络的规模。

## Quiz

1. Which of the following are benefits of VoIP described in this chapter (check all that apply)?
   - A. Convergence of data and voice networks to reduce cost
   - B. Lower infrastructure cost for additions, removals, and changes
   - C. Open standards that free you from a single vendor
   - D. Easier and cheaper Computer Telephony Integration
   - E. Guaranteed lower per-minute calling rates than any phone company
2. Convergence is the integration of voice, data, and video in a single network; its primary benefit is cost reduction in the implementation and maintenance of separate networks.
   - A. False
   - B. True
3. Asterisk treats every VoIP protocol as a channel and can bridge any channel type to any other, transcoding between codecs when needed.
   - A. False
   - B. True
4. In Asterisk 22, SIP is handled by which channel driver?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In the TCP/IP (IETF) model that SIP is actually defined against in RFC 3261, the signaling protocols SIP, H.323, and IAX2 operate at the ___ layer.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP is the most adopted protocol for IP phones and is an open standard largely defined by the IETF in RFC 3261.
   - A. False
   - B. True
7. IAX2 transports both signaling and media over a single UDP port, which makes it efficient and easy to traverse NAT. Which UDP port does IAX2 use?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX was originally developed by Digium (now Sangoma). Despite limited adoption by phone vendors, IAX is excellent when you need (check all that apply):
   - A. To reduce bandwidth usage (it does not use RTP)
   - B. A video media format
   - C. Easy NAT and firewall traversal
   - D. Trunk mode to combine many Asterisk-to-Asterisk calls and amortize header overhead
9. In Asterisk 22, a device is configured as a single PJSIP `endpoint` object that both places and receives calls — there is no separate "user" or "peer" role.
   - A. False
   - B. True
10. Regarding codecs in Asterisk 22, check all the true statements:
    - A. G.711 is equivalent to PCM and uses 64 Kbps of bandwidth.
    - B. Sangoma's codec_g729 module is free to download, but lawful use requires a purchased per-channel license.
    - C. GSM is popular because it uses about 13 Kbps and needs no license.
    - D. G.711 u-law is common in North America, while a-law is common in Europe and Latin America.
    - E. G.729 is light and uses very few CPU resources to encode and decode compared with G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
