# 遗留通道：模拟、TDM 和 IAX2

在 2026 年的纯 VoIP 世界中，本章介绍的通道类型已日益罕见：大多数新部署都是基于以太网的 SIP trunk 和 PJSIP endpoint，完全不涉及任何电话硬件。尽管如此，Asterisk 22 仍然全面支持其中的大多数。模拟 (FXO/FXS) 和数字 TDM (E1/T1/ISDN PRI/BRI) 连接通过 DAHDI 提供——这是最初由 Digium 开发的驱动程序栈，Digium 于 2018 年被 Sangoma 收购，此前由于商标纠纷，早期的 Zaptel 驱动程序被更名。基于 IAX2 的服务器间连接由 `chan_iax2` 提供，它仍然在发布和支持中，但现在已明确属于遗留协议。本章还收集了 **遗留 SIP** 的相关资料：旧的 `chan_sip` 驱动程序及其 `sip.conf` 配置（已在 Asterisk 21 中移除，并在 Asterisk 22 中彻底消失），以及将现有 `sip.conf` 系统迁移到 PJSIP 的完整指南。如果您运行的是基于 PJSIP 的纯 SIP 环境，没有电话卡、没有 IAX2 trunk，也没有需要转换的遗留 `sip.conf`，则可以安全地跳过本章。

## 模拟通道 (FXO/FXS)

截至 Asterisk 22，DAHDI 和模拟电话卡仍然得到全面支持，且 DAHDI 依然可以针对当前内核进行构建。尽管如此，大多数新部署仍为纯 VoIP（SIP trunk，PJSIP），因此模拟/TDM 硬件现在已成为一种小众选择——主要存在于遗留环境、农村 PSTN 连接或受监管的市场中。以下所有内容仍然适用于这些场景。

连接公共交换电话网 (PSTN) 的方式有多种。最佳方式取决于电话公司在您所在地区提供的连接方式。最简单的方法是使用模拟线路，类似于您在家中使用的线路。在本节中，我们将向您展示如何配置来自 Sangoma™（前身为 Digium™）和 Xorcom™ 的模拟卡。

### 目标

读完本章后，您应该能够：

- 识别主要的电话术语和缩写；
- 理解何时使用数字电路和模拟电路；
- 识别 FXS 和 FXO 之间的区别；以及
- 为 FXS 和 FXO 配置 Asterisk。

### 电话基础知识

大多数模拟实现使用一对称为 tip 和 ring 的铜线。当回路闭合时，电话会从电信交换机（或专用 PBX）接收拨号音。最常用的信令是环路启动 (loop-start)；其他不太常见的信令包括接地启动 (ground start)，这在一些国家使用。信令分为三类：

- 监控信令
- 地址信令
- 信息信令

#### 监控信令

主要的监控信令包括挂机 (on-hook)、摘机 (off-hook) 和振铃 (ringing)。挂机 (On-Hook) – 当用户将电话放回听筒时，PBX 会中断连接并不允许电流通过。在这种状态下，电路称为挂机。在此位置，只有振铃器处于活动状态。摘机 (Off-Hook) – 在开始通话之前，电话需要进入摘机状态。从挂钩上取下听筒会闭合回路，并向 PBX 指示用户打算拨打电话。收到此指示后，PBX 会产生拨号音，向用户指示它已准备好接收目标地址（即电话号码）。振铃 (Ringing) – 当用户呼叫另一部电话时，它会产生电压到振铃器，提醒对方有来电。信令因国家/地区而异，不同国家有不同的音调。您可以通过修改 indications.conf 文件将 Asterisk 的音调个性化为您的国家/地区。例如：

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### 地址信令

您可以使用两种信令进行拨号。第一种也是最常见的是双音多频 (dtmf)，另一种是脉冲拨号（用于旧式旋转拨号电话）。电话有用于拨号的键盘，每个按钮关联两个频率：一个高频和一个低频。在 dtmf 信令的情况下，这些音调的组合指示正在按下的数字。MFC/R2 使用与 dtmf 不同的多频音调。

#### 信息信令

信息信令显示呼叫的进度和不同事件。

- 拨号音
- 忙音
- 回铃音
- 拥塞
- 无效号码
- 确认音

### PSTN 接口

与旧式 PBX 一样，通常需要将 Asterisk PBX 连接到 PSTN。在这里，我们将向您展示如何操作。通常，您有三种电话线路选项。

- 模拟：家庭和小型企业最常见的形式，通常通过一对金属铜线提供。
- 数字：在需要多条线路时使用。数字线路通常由 CSU/DSU 或光纤多路复用器提供。最终用户连接器通常是 RJ45。在某些国家/地区，E1 线路使用两个同轴 BNC 连接器提供；在这种情况下，您需要一个巴伦 (balun) 来连接 RJ45 插孔到电话板。
- SIP：此选项是最近开发的。电话线路通过带有 SIP 信令的数据连接（VoIP）提供。这是与 Asterisk 一起使用的好选择，因为您无需购买电话卡。电话呼叫将直接传送到以太网端口。另一个优点是，通过避免编解码器转码，您可以释放 CPU 资源。

### 模拟 FXS、FXO 和 E&M 接口

有多种类型的模拟接口可用。了解这些接口之间的差异对于学习如何连接到电话网络以及其他 PBX 至关重要。在这里，我们将向您展示 E&M 接口。虽然它目前不适用于 Asterisk 且已被多家供应商停产，但您可能会发现带有此类接口的路由器和 PBX，因此了解您正在处理的内容会更好。

#### 外汇 (FX) 接口

FX 接口是模拟的。术语“Foreign eXchange”适用于访问 PSTN 中心局 (CO) 的中继线。外汇局 (FXO)

![Asterisk 位于模拟电话 (FXS) 和电信线路 (FXO) 之间：FXS 端为电话提供拨号音和振铃，而 FXO 端从中心局获取拨号音。](../images/10-legacy-fig01.png)

FXO 接口用于连接到中心局 (CO) 或其他 PBX 的分机。它直接与来自 PSTN 的电话线通信。另一个选项是将 FXO 接口连接到现有的 PBX，允许 Asterisk 和遗留 PBX 之间的通信。将 Asterisk 连接到 PBX 端口并使用 VoIP 提供远程分机通常称为异地分机 (OPX)。FXO 接口接收拨号音。外汇站 (FXS) FXS 接口为模拟电话、调制解调器或传真机供电。FXS 为电话提供拨号音和电源。

#### 中继信令

- 环路启动 (Loop-Start)
- 接地启动 (Ground-Start)
- 挂机监控 (Kewlstart)

在 Asterisk 中使用 kewlstart 信令几乎是默认设置。Kewlstart 本身不是信令，但通过监控另一端发生的情况增加了电路的智能性。Kewlstart 基于环路启动。大多数交换机不支持此功能，该功能用于获取挂机通知。

- 环路启动 (Loopstart)：用于大多数模拟线路，它允许电话指示“挂机”和“摘机”，并允许交换机指示“振铃”和“无振铃”。这可能是大多数人家里有的。这个名字来源于线路总是处于打开状态的事实。当您闭合回路时，交换机会为您提供拨号音。来电通过开路对上的 100V 振铃电压发出信号。

![Asterisk 作为 VoIP 网关运行：FXO 端口连接到遗留 PBX 分机，而远程 Asterisk 通过 FXS 端口通过 IP 将该线路传送到模拟电话（异地分机，或 OPX）。](../images/10-legacy-fig02.png)

- 接地启动 (Groundstart)：类似于环路启动。当您想拨打电话时，线路的一侧会短路。当交换机识别出此状态时，它会通过开路对反转电压，然后闭合回路。因此，线路在提供给呼叫者之前首先被占用。
- 挂机监控 (Kewlstart)：增加了电路的智能性，允许监控另一端。Kewlstart 结合了环路启动的许多优点。

### Asterisk 电话通道设置

要配置电话接口卡，需要执行几个步骤。在本章中，我们将展示三个最常见的场景：

- 使用 FXS 的模拟连接
- 使用 FXO 的模拟连接
- 连接带有 FXS 和 FXO 接口的 Astribank™

### 配置过程（两种情况均有效）

在为 Asterisk 选择硬件之前，您应该考虑将要安装和启用的并发呼叫数、服务和编解码器。Asterisk 是一个 CPU 密集型应用程序，这就是为什么我们建议为 Asterisk 使用专用机器的原因。计算机内安装的接口卡数量受可用插槽和中断数量的限制。安装一张带有 8 个语音接口的卡比安装两张带有 4 个接口的卡更可取。另一个选择是使用 USB 通道库，例如 Xorcom Astribank。最近，一些制造商（例如 CIANET）已经开始生产 TDMoE 通道库，使得连接数十个模拟接口变得更加容易。

![Xorcom Astribank：一种 19 英寸机架式 USB 通道库，可提供数十个 FXS/FXO 端口（此处为 32 端口单元），而不会消耗主机中的 PCI 插槽。](../images/10-legacy-fig03.png)

#### 示例 1：一个 FXO，一个 FXS 安装

在此示例中，我们将使用带有 1 个 FXS 和 1 个 FXO 模块的 Sangoma TDM400 电话接口卡（以前作为 Digium TDM400 出售）。所需步骤如下：

1. 安装模拟卡 FXS、FXO 或两者。
2. 配置文件 `/etc/dahdi/system.conf`（以前为 `/etc/zaptel.conf`）。
3. 使用 `dahdi_genconf` 生成配置文件。
4. 加载 DAHDI 接口的驱动程序。
5. 执行 `dahdi_test` 以验证中断丢失。
6. 执行 `dahdi_cfg` 以配置驱动程序。
7. 在 `chan_dahdi.conf` 文件中配置 DAHDI 通道，然后加载 Asterisk。

##### 第 1 步：安装 TDM400 板

TDM404P 卡包含 FXS 和 FXO 模块。连接 FXS (S110M, 绿色) 和 FXO (X100M, 红色) 模块。如果您使用的是 FXS 模块，请使用 molex 连接器将卡直接连接到电源。在处理接口卡之前，请佩戴静电防护装置，以免损坏硬件。Sangoma (前身为 Digium) 模拟卡还支持硬件回声消除模块 VPMADT032。

##### 第 2 步：使用 dahdi_genconf 生成配置

关于配置的好消息是新的实用程序 `dahdi_genconf`，它会自动检测并生成 DAHDI 接口的配置。该实用程序生成两个文件：

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf`（带有 `users` 选项）
- 所有这些文件都使用选项 `chan_dahdi full`

在执行 `dahdi_genconf` 之前，配置文件 `genconf_parameters`（通常称为 `gen_parameters.conf`）非常重要：

![Sangoma/Digium TDM404P 模拟卡：最多四个 FXS 或 FXO 模块插入编号端口，带有可选的硬件回声消除子卡和用于 FXS 模块的专用 12 V 电源连接器。](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

`genconf_parameters` 文件允许您自定义配置。模拟线路最重要的参数是：

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

警告：要求您至少为通道配置回声消除算法。base_exten 参数定义了 FXS 分机的基本拨号方案。在这种情况下，第一个 FXS 通道将接收分机号码 4000，第二个接收 4001，依此类推。创建线路 (context_phones) 和中继线 (context_lines) 的上下文非常重要。生成文件后，您应该在 `/etc/asterisk/chan_dahdi.conf` 文件中包含 `/etc/asterisk/dahdi-channels.conf` 文件：

```
#include dahdi-channels.conf
```

注意：模拟信令有点令人困惑；它总是与卡相反。FXS 卡用 FXO 发送信令，而 FXO 卡用 FXS 发送信令。Asterisk 与这些设备通信，就好像它在对面一样。

##### 第 3 步：加载内核驱动程序

现在您必须加载 chan_dahdi 模块和相关的卡内核驱动程序。使用 dahdi_hardware 检测您的卡和驱动程序名称。例如：

- 卡 驱动程序 描述
- TE410P wct4xxp 4xE1/T1-3.3V PCI
- TE405P wct4xxp 4xE1/T1-5V PCI
- TDM400P wctdm 4 FXS/FXO
- T100P wct1xxp 1 T1 E100P wctlxxp 1 E1 X100P wcfxo 1 FXO

加载驱动程序的命令：

```
modprobe dahdi
modprobe wctdm
```

##### 第 4 步：使用 dahdi_test 实用程序

一个重要的实用程序是 dahdi_test，它用于验证 DAHDI 卡中的中断丢失。音频质量问题通常与中断冲突有关。要验证您的 DAHDI 卡没有与其他卡共享中断，请使用以下命令：

```
#cat /proc/interrupts
```

您可以使用随 DAHDI 卡编译的 dahdi_test 实用程序验证中断丢失的数量。低于 99.987% 的数字表示可能存在问题。

##### 第 5 步：使用 dahdi_cfg 实用程序配置驱动程序

DAHDI 有一个不寻常的驱动程序加载系统。首先配置 /etc/dahdi/system.conf，然后使用 dahdi_cfg 将这些配置应用到 DAHDI 驱动程序。在这种情况下，dahdi_cfg 用于配置 FX 接口的信令。要查看结果，您可以将“-vvvvv”附加到命令以获取详细信息。

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

如果通道加载成功，您将看到类似于上面显示的输出。用户经常错误地配置 chan_dahdi.conf，导致通道之间的信令反转。如果发生这种情况，您将看到如下所示的消息：

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

成功配置硬件后，您可以继续进行 Asterisk 配置。

##### 第 6 步：配置 /etc/asterisk/chan_dahdi.conf 文件

听起来很奇怪，但在配置 /etc/dahdi/system.conf 后，您就配置了卡本身。DAHDI 可用于其他目的，如路由和 SS7。要将其与 Asterisk 一起使用，您必须配置 Asterisk DAHDI 通道。Asterisk 中的每个通道都必须定义；SIP/PJSIP 通道在 pjsip.conf 中定义（注意：chan_sip 和 sip.conf 已在 Asterisk 21 中移除），而 TDM 通道在 chan_dahdi.conf 中定义。这创建了要在您的拨号方案中使用的逻辑 TDM 通道。

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### 配置选项

chan_dahdi.conf 文件中有多个选项可用。描述所有选项会很无聊且适得其反；相反，我们将专注于主要选项组，以便于理解。

#### 常规选项（通道独立）

这些选项适用于任何通道：context：定义传入上下文。

```
context=default
```

channel：定义通道或通道范围。每个通道定义将继承声明之前定义的选项。通道可以单独标识，也可以通过逗号分隔在同一行中标识。范围可以使用“-”定义。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group：允许将通道作为组处理。如果您拨打组号而不是通道号，则使用第一个可用的通道。如果通道是电话，当您呼叫组时，所有电话将同时响铃。使用逗号，您可以为同一通道指定多个组。

```
group=1
group=3,5
```

language：开启国际化并配置语言。此功能将为特定语言配置系统消息。英语是通过标准安装提供的唯一具有完整提示的语言。musiconhold：选择保持音乐类。

#### 来电显示选项

有许多 callerid 选项。有些可以禁用，尽管大多数默认启用。usecallerid：启用或禁用后续通道的 callerid 传输（是/否）。注意：如果您的系统在应答前有两个振铃，请尝试禁用此功能。它应该立即应答。hidecallerid：定义是否隐藏传出的 callerid（是/否）。callerid：为特定通道配置 callerid 字符串。呼叫者可以配置为 asreceived。这主要用于中继接口以指示传入的 callerid。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid：支持呼叫等待期间的 callerid。useincomingcalleridondahditransfer：在转移中使用传入的 callerid。

#### 呼叫等待

Asterisk 支持 FXS 通道中的呼叫等待。如果有人尝试分机，用户将收到等待音。要启用呼叫等待：

```
callwaiting=yes
```

要在呼叫等待中支持 callerid：

```
callwaitingcallerid=yes
```

#### 音频质量选项

调整回声消除既是技术活，也是艺术活。这些选项调整某些影响 DAHDI 通道音频质量的 Asterisk 参数。它们可以帮助改善模拟接口中的音频质量。

#### fxotune 实用程序

fxotune 是一个用于微调 FXO 模块某些参数的实用程序。这种微调对于调整由混合电路引起的阻抗失配是必需的。该实用程序有三种操作模式：

- 检测 (-i)：检测并修复现有的 FXO 通道并将配置保存到

```
fxotune.conf
```

- 转储模式 (-d)：生成波形文件到 fxotune_dump.vals
- 启动模式 (-s)：读取文件 fxotune.conf 并将其应用于 FXO 模块

重要的是要了解，在启动 Asterisk 之前，您必须在系统加载中插入指令 fxotune –s：

```
#modprobe dahdi
#modprobe wctdm
#fxotune-s
```

### 回声消除

大多数回声消除算法通过生成接收信号的多个副本来工作，其中每个副本都延迟特定的时间量。滤波器的抽头 (taps) 数量决定了需要消除的回声延迟大小。然后调整这些延迟的副本并从接收信号中减去。诀窍是仅调整延迟信号以消除回声，而不使用过多的 CPU 周期。从用户的角度来看，选择合适的回声消除算法很重要。默认是 MG2；但是，还有其他两个选项：来自 Sangoma (前身为 Digium) 的高性能回声消除 (HPEC) 和由 David Rowe 开发的开源回声消除 (OSLEC)。

OSLEC (https://www.rowetel.com/?page_id=454) 已合并到 Linux 内核中——它位于内核的 `drivers/staging/echo` 区域——DAHDI 是针对它构建的，而不是单独发布下载。要更改回声消除算法，请设置 `/etc/dahdi/system.conf` 中的 `echo_can` 参数。例如：

```
echo_can=oslec
```

Asterisk 中的回声消除由 /etc/asterisk/chan- 中的三个参数控制

```
dahdi.conf.
```

echocancel：禁用或启用回声消除。您应该保持此功能启用。它接受“yes”或抽头数量。解释：回声消除是如何工作的？大多数回声消除算法通过生成接收信号的多个副本来工作，每个副本都延迟一小段时间。这个小流程称为“抽头”。抽头数量决定了可以消除的回声延迟。这些副本被延迟、调整并从原始信号中减去。诀窍是将延迟信号调整到消除回声所需的精确程度。echocancelwhenbridged：在纯 TDM 通话期间启用或禁用回声消除器。这通常是不必要的。rxgain：调整音频接收增益以增加或减少接收音量（-100% 到 100%）。txgain：调整音频传输增益以增加或减少传输音量（-100% 到 100%）。例如：

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 计费选项

这些选项更改呼叫信息在呼叫详细记录 (CDR) 数据库中的记录方式。amaflags：配置影响 CDR 分类的 AMA 标志。它接受以下值：

- billing
- documentation
- omit
- default

accountcode：为特定通道配置帐户代码。它可以包含任何字母数字值——通常是部门或用户名。

```
accountcode=finance
amaflags=billing
```

### 呼叫进度选项

这些项目用于获取有关呼叫进度的信息。在公共接口中，检测呼叫进度并确定它是已应答还是忙碌可能很有用。忙音检测是高度实验性的，并受特定参数的调节。

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

这些参数（上文）指定接口是否会尝试检测忙音、成功检测需要多少音调以及忙音模式是什么。忙音检测在很大程度上是实验性的，可以在 Makefile 中更改一些附加参数。要检测呼叫的应答（这对于精确计费至关重要），可以使用极性反转来发出精确应答时间的信号。如果您计划对呼叫收费或只是希望进行精确计费以进行比较，这一点很重要。通常，您必须联系电话公司请求此服务。

```
answeronpolarityswitch=yes
```

在某些国家/地区，也可以使用极性反转来检测呼叫的挂断。

```
hanguponpolarityswitch=yes
```

#### 电话选项

这些选项用于连接到 FXS 接口的电话。直接连接到 DAHDI 接口的模拟电话所提供的所有功能均由 Asterisk 控制。Adsi (模拟显示服务接口)：这是一组电信标准，被一些电信公司用于提供购票等服务。cancallforward：启用或禁用呼叫转移（*72 启用，*73 禁用）。calleridcallwaiting：启用在呼叫等待指示期间接收的 callerid（是/否）。immediate：在立即模式下，通道不会提供拨号音，而是立即跳转到定义上下文中的“s”分机。这用于创建热线。threewaycalling：启用或禁用三方会议。mailbox：警告用户有可用的语音邮件。它可以是声音信号或视觉指示器（如果电话支持此功能）。参数是邮箱号码。callgroup：对电话进行分组以拨打或接听。pickupgroup：用于呼叫接听的电话组。

### 有用的 DAHDI CLI 命令

一旦 Asterisk 运行并加载了 DAHDI 通道，您就可以从 Asterisk CLI 检查通道状态。这些命令在 Asterisk 22 中仍然有效：

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDI 通道格式

DAHDI 通道在拨号方案中使用以下格式：

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

例如：

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
```

## 数字通道 (E1/T1/PRI / TDM)

截至 Asterisk 22，DAHDI 和 libpri 仍然得到全面支持，但 TDM 数字中继线 (E1/T1/ISDN PRI) 在新部署中正日益被 SIP 中继线取代。本节在需要 TDM 连接的地方仍然完全适用；在新建环境中，SIP 中继（第 3 章）通常提供相同的通道密度，而无需电话硬件。

数字通道非常普遍，因此如果您想专注于大客户，则需要学习如何实现这些通道。当通道数量较多（通常超过 8 个）时，使用 T1/E1/J1 等数字接口相当普遍。T1 在美国非常普遍，而 E1 在欧洲普遍，J1 在日本普遍。这些类型的通道允许良好的电路密度——每个 T1 通道 24 个，E1 通道 30 个。在拉丁美洲、中国和非洲，通常使用一种称为 MFC/R2 的随路信令 (CAS) 通道。本章将研究如何使用库 OpenR2 实现 MFC/R2。在美国和欧洲，综合业务数字网 (ISDN) PRI 是最常见的信令。本章还将讨论 ISDN 基群速率接口 (BRI)，它在欧洲的中端应用中非常普遍。本书中的所有示例都集中在 DAHDI 通道上。有些卡是使用专有通道实现的，因此请与您的制造商联系，以获取有关如何配置特定卡的更多详细信息。

### 目标

读完本章后，您将能够：

- 识别数字电话中使用的主要术语
- 区分 CAS 和 CCS 信令
- 区分 R2 和 ISDN 信令
- 配置带有 ISDN 信令的接口
- 配置带有 R2 信令的接口

### E1/T1 数字线路

当您需要实现大量通道时，数字线路 E1/T1 是一个选择。单个 E1 电路能够进行 30 次并发呼叫，并且您可以拥有直接拨入 (DID)、来电显示 (Caller ID) 和高级信令等功能。E1/T1 线路可能会通过双绞线、光纤和微波以多种方式到达您的公司，具体取决于您所在的国家/地区。数字线路使用 UTP、光纤或微波传送到您的公司。调制解调器和多路复用器 (MUX) 用于传送物理线路。到 T1 线路的连接始终基于 RJ45 连接器。但是，E1 线路也可以使用 BNC 提供。提前了解您将要接收的连接器类型非常重要，主要是在 E1 线路中。通常，直到 RJ45 的所有设备都由电信公司提供。

![E1/T1 电路是如何配置的：电信公司可以通过 UTP 铜线（用于 E1 的 HDSL 调制解调器，或用于 T1 的直接卡连接）、通过光多路复用器的光纤或通过微波无线电链路提供中继线。](../images/10-legacy-fig05.png)

![UTP 还是 BNC？大多数数字卡使用 RJ45 (UTP) 连接器，但一些 E1 线路是在双 BNC 同轴电缆上提供的，在这种情况下，需要一个巴伦来使同轴对适应卡的 RJ45 插孔。](../images/10-legacy-fig06.png)

#### 语音是如何转换为比特的？

模拟信号每秒采样 8,000 次以创建模拟语音的数字版本。这种编码称为脉冲编码调制 (PCM)。在美国和日本，信号使用 law 编码（在 Asterisk 中称为 ulaw）。在世界其他地区，编码为 alaw。

![脉冲编码调制 (PCM)：4 kHz 模拟语音信号每秒采样 8,000 次（奈奎斯特），并编码为 64 Kbps 的数字比特流。](../images/10-legacy-fig07.png)

#### 时分复用

当您只需要几个通道时，模拟线路是有意义的。使用时分复用 (TDM) 时，可以将多个通道填充到单个数据连接中。当您需要大量电路时，电话公司通常会为您提供数字中继线，这是一种数据电路，其中语音以使用 PCM 的数字格式传输。每个时隙使用 64 Kbps 的带宽来传输单个语音通道。

![E1 和 T1 中的时分复用：E1 帧在 2048 Kbps 下承载 32 个时隙（DS0 #0 用于帧同步，DS0 #16 用于信令），而 T1 帧在 1544 Kbps 下承载 24 个时隙，使用一位用于同步，并使用一种窃位方案用于信令。](../images/10-legacy-fig08.png)

在美国，最常见的数字中继线是 T1，它有 24 条可用线路；在欧洲和拉丁美洲，E1 中继线有 30 条线路。一些公司提供通道较少的零碎 T1/E1。窃位信令 (Robbed bit signaling) 有时 T1 中继线使用一种窃位方案，其中一位被借用于信令。在 T1 中继线上，数据/语音通道在每个时隙上以 56 Kbps 传输。正如您可能观察到的，当您使用窃位时，T1 电路不会损失两个时隙用于同步和信令。

#### T1/E1 线路编码

T1 和 E1 实际上是数据电路，并且具有确定比特解释方式的数据编码。对于 E1，最常见的线路编码是用于第 1 层的 HDB3 和用于第 2 层的 CCS。了解数字中继线配置方式的最简单方法是向电信公司询问此信息。您将需要此信息来配置 /etc/dahdi/system.conf 文件。

#### T1/E1 信令

重要的是要了解 T1/E1 线路可以使用不同类型的信令提供，例如：

- 带有窃位信令的 T1
- 带有 ISDN 信令的 T1
- 带有 MFC/R2 的 E1 (CAS - 随路信令)
- 带有 ISDN 信令的 E1

ISDN 常用于欧洲和美国。它是一个数字语音网络，由国际电信联盟 (ITU) 于 1984 年标准化。ISDN 提供两种类型的通道：

- 承载通道 o 语音 o 数据
- 数据通道 o 带外信令 o LAPD 信令 o Q.931

通常，ISDN 线路通过两种物理方式提供：

- 基群速率接口 (BRI) o 称为 2B+D o 两个承载 (64K) 通道和一个数据 (16K) 通道 o 使用一对 148Kbps 的铜线。
- 基群速率接口 (PRI) o 使用 T1/E1 中继线提供 o T1 为 23B+D o E1 为 30B+D

有时，E1 电路使用一种称为 MFC/R2 的 CAS 信令方案，该方案由 ITU 定义为称为 Q.421/Q441 的标准。这在拉丁美洲和亚洲经常见到。这些国家的几家电话公司使用 MFC/R2 的定制变体。因此，您需要知道正确的国家/地区变体才能使其工作。

### ISDN BRI

使用 ISDN BRI 信令的通道在欧洲非常流行。大多数用于 Asterisk 的 ISDN BRI 卡支持带有 NT 和 TE 功能的 S/T 接口。TE（终端）连接用于连接到电信公司或配置为网络终端 (NT) 的其他 PBX。NT 用于连接配置为 TE 的电话和 PBX。ISDN BRI 提供两个数据/语音通道和一个信令通道。ISDN BRI 卡可从多家 Asterisk 接口卡供应商处获得。

### 为您的 Asterisk 服务器选择电话卡

有几家制造商生产与 Asterisk 兼容的数字卡。卡的选择取决于以下一些因素：

#### 数据总线

您的 PC 上有多种类型的总线。为您的服务器配备正确的卡非常重要。以下概述了最常用的卡：

- 32 位 PCI 5V，存在于大多数计算机中，包括台式机 o Sangoma (前身为 Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, 和 TC400 o Sangoma A101, A102, 和 A104
- 32/64 位 PCI 3.3V，主要存在于服务器中 o Sangoma (前身为 Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, 和 TC400
- PCI Express，存在于台式机和服务器中 o Sangoma (前身为 Digium) TE420, TE220, TE121, AEX2400, 和 AEX800 o Sangoma A101, A102, 和 A104

这些卡系列起源于 Digium，Sangoma 于 2018 年收购了该公司；它们现在以 Sangoma 品牌销售和支持。此处列出的许多旧 SKU 已停产，因此在购买前请在 www.sangoma.com 上确认当前型号的可用性。

- MiniPCI，存在于嵌入式系统中 o OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI), 和 B400M(ISDN BRI)
- USB 2.0，存在于大多数现代 PC 中。基于 USB 的解决方案允许大量的模拟和数字通道。此总线支持 480 Mbps，每个语音通道占用 64 Kbps。使用 USB 集线器时，可以在单个端口中获得高达一千个模拟端口的密度。 o Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- 以太网。以太网最大的优势是允许卡由多台服务器连接。高可用性解决方案通常是这些设备的核心应用。此解决方案的优势在于使用没有空闲 PCI 插槽的服务器或刀片服务器。 o Redfone FoneBridge (最多四个 E1 电路)

### 使用硬件回声消除

硬件回声消除减少了主机 CPU 的负载。对于具有多个 E1 接口的卡，硬件回声消除可以帮助减轻处理器的负担。新的增强型软件回声消除器（如 OSLEC）正在减少对硬件回声消除器的需求。要在硬件和软件回声消除器之间进行选择，您应该考虑服务器中可用的处理能力和 E1 电路的数量。使用 OSLEC 时，回声消除过程每个语音通道最多可使用 9 MIPS（每秒百万条指令），振幅为 128 个抽头（参考：Xorcom Ltd.）。如果您考虑每条指令 1 个 CPU 周期（基于处理器和软件实现本身并不总是正确的），我们谈论的是四个 E1 的 1.080 Ghz。

#### 信令类型

选择信令类型（例如，T1 CAS、T1 PRI、E1 CAS R2 或 E1 CAS ISDN）并非易事。这实际上取决于您所在地区可用的内容以及价格。公共信道信令 (CCS) 通常比随路信令 (CAS) 更好。但是，它通常不可用。在美国，您通常可以选择，因为大多数电信公司为普通用户提供 T1 CAS，为高级用户（例如呼叫中心）提供 T1 PRI。在拉丁美洲，E1 CAS R2 很普遍，但在一些城市可以使用 ISDN PRI。

![DAHDI 软件架构：Asterisk 与 `chan_dahdi` 通道驱动程序通信，该驱动程序依次加载协议库 libpri (ISDN)、libopenr2 (MFC/R2) 和 libss7 (SS7)；这些位于 `/dev/dahdi` 接口、DAHDI 内核驱动程序和卡特定接口内核驱动程序之上。](../images/10-legacy-fig09.png)

实现 R2 需要安装一个名为 OpenR2 (www.libopenr2.org) 的库，该库由 Moises Silva 开发，并在安装前修补 Asterisk——本章稍后将展示一个简单的过程。该库已通过多项测试，并在我们的几个客户中投入生产。在我看来，如果可用，ISDN 始终是最佳选择。一些提供商可以访问 7 号信令系统 (SS7)，这是电话公司之间可用的 CCS 信令。SS7 有专有和开源解决方案。库 libss7 用于支持 Asterisk 上的 SS7。

### Asterisk 电话通道设置

配置电话接口卡涉及几个必要的步骤。在本章中，我们将展示三个最常见的场景：

- 使用 ISDN PRI 的数字连接
- 使用 ISDN BRI 的数字连接
- 使用 MFC/R2 的数字连接

有两种方法可以配置 DAHDI 通道。第一种是手动配置，完全控制所有参数。第二种是使用实用程序 dahdi_genconf 来检测和配置卡。

#### 自动检测和配置

感谢 DAHDI 开发团队，我们现在有了卡的自动检测和配置。第 1 步：要自动生成配置，请使用实用程序 dahdi_genconf，它将检测卡并生成文件 /etc/dahdi/system.conf 和 dahdi-channels.conf。

```
dahdi_genconf
```

第 2 步：在 chan_dahdi.conf 文件的最后一行，包含文件 dahdi-channels.conf

```
#include dahdi_channels.conf
```

第 3 步：注释掉模块文件中的所有未使用模块，或者直接使用：

```
dahdi_genconf modules
```

#### 手动配置

另一个选项是手动配置接口。以下是 DAHDI 通道配置的一些示例。

##### 示例 #1 – 使用 ISDN 的两个 T1/ E1 通道

所需步骤：

1. TE205P 或 TE210P 安装
2. `/etc/dahdi/system.conf` 文件配置
3. DAHDI 驱动程序加载
4. `dahdi_test` 实用程序
5. `dahdi_cfg` 实用程序
6. `chan_dahdi.conf` 文件配置
7. Asterisk 加载和测试

第 1 步：TE205P 安装。在安装 TE205P 之前，了解 TE205P 和 TE210P 卡之间的区别非常重要。TE210P 卡使用由 3.3 伏供电的 64 位总线，几乎只存在于服务器的主板中。如果您指定此接口卡，请务必小心；确保您的硬件支持 64 位、3.3V 总线。TE205P 卡使用 5V PCI，这在台式计算机中很常见。我们在此示例中选择了带有两个跨度的 TE205P 接口卡，因为它更容易将其减少为单跨度卡或将其扩展为四跨度卡。这些卡现在以 Sangoma 品牌（前身为 Digium）销售。

![Sangoma/Digium TE205P 双跨度 E1/T1 卡：两个 RJ45 端口接受数字中继线，板载跳线（E1/T1/J1 选择器）设置线路标准。](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

TDM 数字卡的配置与模拟卡的配置略有不同。首先，我们需要配置板跨度，然后配置通道。跨度根据卡的识别顺序按顺序编号。换句话说，如果您有多个接口卡，很难知道哪个跨度属于哪一个。使用 dahdi_hardware 检查每个跨度上安装了什么硬件。示例 #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

示例 #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

示例 #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

第 3 步：加载内核驱动程序 使用 dahdi_hardware 检查您需要安装的驱动程序。

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

要加载，请使用：

```
modprobe dahdi
modprobe wct2xxp
```

第 4 步：使用 dahdi_test，检查丢失的中断 您可以使用随 DAHDI 卡编译的 dahdi_test 实用程序验证中断丢失的数量。低于 99.987% 的数字表示可能存在问题。您将在以下位置找到 dahdi_test

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

第 5 步：使用 dahdi_cfg 实用程序 这是 dahdi_cfg 对于一个零碎 E1 (15 端口) 跨度和两个 FXO 端口的正确输出。

```
#./dahdi_cfg –vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

第 6 步：将 DAHDI 配置到 /etc/asterisk/chan_dahdi.conf 文件中 示例 #1 (2xT1)

```
callerid=”John Doe”<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

示例 #2 (2xE1)

```
callerid=”Flavio Eduardo” <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

示例 #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

对于点对多点 BRI，使用 signaling=bri_cpe_ptmp。目前，BRI 点对多点在 NT 模式下不受支持。

#### 加载内核驱动程序

配置驱动程序后，您可以简单地重新启动服务器。如果您已使用 make config 安装了 DAHDI，则无需执行任何额外操作。内核驱动程序将自动加载和配置。但是，有时手动加载和卸载驱动程序很有用。示例：

```
modprobe wct11xp
dahdi_cfg –vvvvv
```

第一个命令加载驱动程序，第二个命令 dahdi_cfg 将配置应用到内核驱动程序。

### 故障排除

有时事情第一次无法正常工作。让我们检查一些用于 DAHDI 故障排除的资源。第 1 步：检查操作系统是否识别了该卡。Sangoma/Digium 卡通常被识别为 ISDN 调制解调器。

```
lspci –v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

第 2 步：使用以下命令检查内核驱动程序是否正确加载：

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

第 3 步：验证与连接物理层相关的警报状态。要验证 E1 连接的物理层，您可以使用以下 Asterisk CLI 命令。

```
dahdi show status
```

警报指示端口存在问题：红色警报：无法与远程交换机保持同步。这通常是物理问题，例如线路编码或帧不匹配。黄色警报：信号表明远程交换机处于红色警报状态。这表明远程交换机没有收到您的传输。蓝色警报：在所有时隙上接收所有未成帧的 1；dahdi_tool 目前无法检测到蓝色警报。环回：端口处于本地或远程环回状态

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

第 4 步：要检测 Asterisk 服务器上 DAHDI 的问题，首先使用以下命令检查通道是否被识别：

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

第 5 步：检查 ISDN 第 3 层（也称为 q.931）的状态。您可以使用 `pri show spans`（列出所有跨度）或 `pri show span <n>`（针对特定跨度）检查 ISDN 第 3 层是否已启动：

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

使用 `pri show spans`（复数）一次列出所有已配置 PRI 跨度的状态。

检查特定通道。dahdi show channel x：

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1*CLI>
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x：如果一切之后您仍然有问题，请开始调试 pri 跨度。此命令启用 ISDN 呼叫的详细调试。当您认为某些内容不正确时，这是一个重要的命令。您可以检测拨错的数字和其他问题。下面我们展示成功呼叫的调试输出示例。如果您需要将不成功的呼叫与没有问题的呼叫进行比较，请参考此示例。一个技巧是使用 core set verbose=0 仅接收 ISDN q.931 消息。

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]fice*CLI>
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### chan_dahdi.conf 中的配置选项

文件 chan_dahdi.conf 中有多个选项可用。描述所有选项会很无聊且适得其反。在这里，我们将详细说明主要选项组，以便更好地理解。

#### 常规选项（通道独立）

context：定义传入上下文。

```
context=default
```

channel：定义通道或通道范围。每个通道定义将继承声明之前定义的选项。通道可以单独标识，也可以通过逗号分隔在同一行中标识。范围可以使用“-”定义。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group：允许将通道作为组处理。如果您拨打组号而不是通道号，则使用第一个可用的通道。如果通道是电话，当您呼叫组时，所有电话将同时响铃。使用逗号，您可以为同一通道指定多个组。

```
group=1
group=3,5
```

language：开启国际化并配置语言。此功能将为特定语言配置系统消息。英语是通过标准安装提供的唯一具有完整提示的语言。musiconhold：选择保持音乐类。

#### ISDN 选项

switchtype：取决于所使用的 PBX 或交换机。在欧洲和拉丁美洲，EuroISDN 很常见。

- 5ess：Lucent 5ESS
- euroisdn：EuroISDN
- national：National ISDN
- dms100：Nortel DMS100
- 4ess：AT&T 4ESS
- Qsig：Q.SIG

```
switchtype = EuroISDN
```

pridialplan：某些需要拨号方案规范的交换机需要此项。此选项被许多交换机忽略。有效选项为 private、national、international 和 unknown。

```
pridialplan = unknown
```

prilocaldialplan：某些交换机所必需的，通常为 unknown。

```
prilocaldialplan = unknown
```

overlapdial：当您在连接建立后传递数字时，使用重叠拨号。您可以使用块模式编号 (overlapdial=no) 或数字模式 (overlapdial=yes)。块模式通常由运营商使用。signaling：配置后续通道的信令类型。这些参数应与 chan_dahdi.conf 文件中的参数相对应。正确的选择基于可用的通道。对于 ISDN，您可以选择五个选项：

- pri_cpe：当设备是 CPE 时使用，有时称为客户端、用户或从属设备。这是最简单且最常用的信令形式。有时，当您尝试连接到专用 PBX 时，PBX 通常也被配置为 CPE。在这种情况下，在 Asterisk 中使用 pri_net 信令。
- pri_net：当 Asterisk 连接到配置为 CPE 的专用 PBX 时使用。该信令通常称为主机、主控或网络。
- bri_cpe：当 Asterisk 作为 CPE 连接到 ISDN BRI 中继线时使用
- bri_net：当 Asterisk 连接到配置为终端 (TE) 的 ISDN 电话或 PBX 时使用。
- bri_cpe_ptmp：与 bri_cpe 相同，但在点对多点架构中。

#### CallerID 选项

有许多 Caller ID 选项可用。有些可以禁用，尽管大多数默认启用。usecallerid：启用或禁用后续通道的 Caller ID 传输（是/否）。注意：如果您的系统在应答前需要两个振铃，请尝试禁用此功能，以便它立即应答。hidecallerid：隐藏 Caller ID（是/否）。calleridcallwaiting：启用在呼叫等待指示期间接收 Caller ID（是/否）。callerid：为特定通道配置 Caller ID 字符串。呼叫者可以在中继接口中配置为“asreceived”以向前传递 Caller ID。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

注意：大多数电信公司要求您配置正确的 caller ID。如果您没有传递正确的 caller ID，您将无法通过电信公司拨出。另一方面，即使不配置 caller ID，您也可以接听电话。

#### 音频质量选项

这些选项调整某些影响 DAHDI 通道音频质量的 Asterisk 参数。echocancel：禁用或启用回声消除。您应该保持此功能启用。它接受“yes”或抽头数量。解释：回声消除是如何工作的？大多数回声消除算法通过生成接收信号的多个副本来工作，每个副本都延迟一小段时间。这个小流程称为“抽头”。抽头数量决定了可以消除的回声延迟。这些副本被延迟、调整并从原始信号中减去。诀窍是将延迟信号调整到消除回声所需的精确程度。echocancelwhenbridged：在纯 TDM 通话期间启用或禁用回声消除器。这通常是不需要的。rxgain：调整音频接收增益以增加或减少接收音量（-100% 到 100%）。txgain：调整音频传输增益以增加或减少传输音量（-100% 到 100%）。示例：

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 计费选项

这些选项更改呼叫信息在呼叫详细记录 (CDR) 数据库中的记录方式。amaflags：影响 CDR 的分类。它接受这些值：

- billing
- documentation
- omit
- default

accountcode：它为特定通道配置帐户代码。它可以包含任何字母数字值，通常是部门或用户名。

```
accountcode=finance
amaflags=billing
```

### MFC/R2 配置

MFC/R2 用于拉丁美洲、中国和非洲的几个国家以及一些欧洲国家。如果您的地区可用，ISDN 更优越且更受青睐。

#### 理解问题

用于发送 MFC/R2 信令的卡与用于发送 ISDN 信令的卡相同。可以使用名为 libopenR2 (www.libopenr2.com) 的库在 DAHDI 通道上使用 MFC/R2。此库不是 1.6.2 之前版本的 Asterisk 的一部分。

##### 理解 MFC/R2 协议

MFC/R2 协议结合了带内和带外信令。地址信令使用一组音调在带内转发，而通道信息作为带外信令在时隙 16 上传输。

**线路信令 (ITU-T Q.421)。** 在时隙 16 中，每个语音通道使用四个 ABCD 位来发出其状态和呼叫控制信号。C 和 D 位很少使用。在一些国家，它们可以用于计量（用于计费的脉冲计量）。在正常对话中，我们有双方在工作：呼叫方和被呼叫方。来自呼叫方的信令称为前向信令，而被呼叫方使用后向信令。我们将指定 Af 和 Bf 用于前向信令，Ab 和 Bb 用于后向信令。

| 状态 | ABCD 前向 | ABCD 后向 |
| --- | --- | --- |
| 空闲/释放 | 1001 | 1001 |
| 占用 | 0001 | 1001 |
| 占用确认 | 0001 | 1101 |
| 已应答 | 0001 | 0101 |
| 清除后向 | 0001 | 1101 |
| 清除前向（在清除后向之前） | 1001 | 0101 |
| 清除前向（断开确认） | 1001 | 1001 |
| 阻塞 | 1001 | 1101 |

MFC/R2 由 ITU 定义。不幸的是，几个国家根据自己的需要定制了该标准。结果，国家之间的标准出现了差异。

**寄存器间信号 (ITU-T Q.441)。** MFC/R2 信令使用两个音调的组合。下表显示了 ITU 标准。

信号组 I（前向）：

| 描述 | 前向信号 |
| --- | --- |
| 数字 1 | I-1 |
| 数字 2 | I-2 |
| 数字 3 | I-3 |
| 数字 4 | I-4 |
| 数字 5 | I-5 |
| 数字 6 | I-6 |
| 数字 7 | I-7 |
| 数字 8 | I-8 |
| 数字 9 | I-9 |
| 数字 0 | I-10 |
| 国家代码指示器，需要传出半回声抑制器 | I-11 |
| 国家代码指示器，不需要回声抑制器 | I-12 |
| 测试呼叫指示器 | I-13 |
| 国家代码指示器，插入传出半回声抑制器 | I-14 |
| 未使用 | I-15 |

信号组 II（前向）：

| 描述 | 前向信号 |
| --- | --- |
| 无优先级的用户 | II-1 |
| 有优先级的用户 | II-2 |
| 维护设备 | II-3 |
| 备用 | II-4 |
| 操作员 | II-5 |
| 数据传输 | II-6 |
| 没有前向传输设施的用户或操作员 | II-7 |
| 数据传输 | II-8 |
| 有优先级的用户 | II-9 |
| 带有前向传输设施的操作员 | II-10 |
| 备用 | II-11 |
| 备用 | II-12 |
| 备用 | II-13 |
| 备用 | II-14 |
| 备用 | II-15 |

信号组 A（后向）：

| 描述 | 后向信号 |
| --- | --- |
| 发送下一个数字 (n+1) | A-1 |
| 发送倒数第二个数字 (n-1) | A-2 |
| 地址完成，切换到接收 B 组信号 | A-3 |
| 国家网络拥塞 | A-4 |
| 发送主叫方类别 | A-5 |
| 地址完成，收费，设置通话条件 | A-6 |
| 发送倒数第三个数字 (n-2) | A-7 |
| 发送倒数第四个数字 (n-3) | A-8 |
| 备用 | A-9 |
| 备用 | A-10 |
| 发送国家代码指示器 | A-11 |
| 发送语言或辨别数字 | A-12 |
| 发送电路性质 | A-13 |
| 请求有关回声抑制器使用的信息 | A-14 |
| 国际交换机或其输出端的拥塞 | A-15 |

信号组 B（后向）：

| 描述 | 后向信号 |
| --- | --- |
| 备用 | B-1 |
| 发送特殊信息音 | B-2 |
| 用户线路忙 | B-3 |
| 拥塞（A 组切换到 B 组后） | B-4 |
| 未分配号码 | B-5 |
| 用户线路空闲，收费 | B-6 |
| 用户线路空闲，不收费 | B-7 |
| 用户线路故障 | B-8 |
| 备用 | B-9 |
| 备用 | B-10 |
| 备用 | B-11 |
| 备用 | B-12 |
| 备用 | B-13 |
| 备用 | B-14 |
| 备用 | B-15 |

#### MFC/R2 序列

以下序列说明了从 Asterisk 分机发起到 PSTN 中终端的呼叫。PSTN 挂断呼叫并结束通信。

![Asterisk 和电信公司之间的完整 MFC/R2 呼叫流程：线路信令（空闲、占用、占用确认、应答、清除后向、清除前向）在时隙 16 中交换，拨打的数字和后向“发送下一个数字”信号（I/A/B 组）在带内传输，可听音调到达用户。](../images/10-legacy-fig11.png)

### 如何使用驱动程序 libopenr2

Moises Silva 发起的项目灵感来自 Steve Underwood 编写的 Unicall 通道驱动程序。OpenR2 库目前是 Asterisk 最稳定的软件解决方案。通过此解决方案，我们可以使用任何与 DAHDI 兼容的数字卡。以前，MFC/R2 只有专有解决方案可用，我使用过的最好的解决方案之一是 Khomp 提供的，www.khomp.com.br。在 Asterisk 22 中，当库在编译时存在时，通过 libopenR2 的 MFC/R2 支持是内置的——不需要外部补丁。以下步骤显示了历史手动安装以供参考；在现代系统上，在运行 `./configure` 之前从您的发行版包管理器安装 `libopenr2-dev`，然后在 `make menuselect` 中启用 `chan_dahdi`。

以下步骤从其当前的 Git 存储库构建 openr2 和 Asterisk。它们被保留作为从源代码构建的站点的参考；在现代发行版上，您通常可以通过安装 `libopenr2-dev` 包和打包的 Asterisk 22 构建来完全跳过它们，因为 `chan_dahdi` 直接针对 libopenr2 编译 R2 支持，而无需外部补丁。

第 1 步：安装您需要的构建工具。

```
apt-get install git
```

第 2 步：克隆 openr2 库和 Asterisk 源代码。Asterisk 22 上不需要特殊的修补树——只要 libopenr2 存在，库存检出就会构建 R2 支持。

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

第 3 步：编译和安装 请在继续之前备份您的服务器。

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

注意：不要执行“make samples”以避免覆盖您的配置文件。

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

假设您有一张带有 1 个 E1 接口的卡。

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

第 5 步：运行命令 dahdi_cfg 以将更改应用到驱动程序：

```
dahdi_cfg –vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

第 5 步：更改文件 chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

第 6 步：更改 extensions.conf 文件中的拨号方案

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

注意：一些电信公司不接受没有 caller ID 的呼叫。请将 caller ID 设置为运营商分配的 DID 号码之一。在某些国家/地区，不需要此步骤。第 7 步：测试解决方案：现在，使用上下文 from-internal 中的分机，拨打任何号码并观察控制台。检查是否有任何错误发生。 -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### 调试 OpenR2

要检测呼叫中的错误，您可以激活调试。为此，请按照以下步骤操作。第 1 步：编辑文件 chan_dahdi.conf 并将以下三行添加到配置中：

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

第 2 步：重新启动 Asterisk 服务器 第 3 步：测试呼叫并检查 /var/log/asterisk/mfcr2/span1 处的呼叫文件 下面是正常呼叫的跟踪。将其与您在呼叫中收到的内容进行比较。

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### MFC/R2 配置

选项记录在文件 chan_dahdi.conf 中。这里详细说明了一些最重要的选项。强制参数：mfcr2_variant, mfcr2_max_ani 和 mfcr2_max_dnis。mfcr2_variant：国家/地区变体。

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani：要请求的最大 ANI 数字量 mfcr2_max_dnis：要请求的最大 DNIS 数字量 mfcr2_get_ani_first：是否在 DNIS 之前获取 ANI（某些电信公司要求）mfcr2_category：呼叫者类别。您可以在开始呼叫前设置变量 MFCR2_CATEGORY mfcr2_logdir：记录呼叫文件的目录。(/var/log/asterisk/mfcr2/directory) mfcr2_call_files：是否记录呼叫

- mfcr2_logging：日志记录值
- cas – 用于 tx 和 rx 的 ABCD 位
- mf – 多频音调
- stack – 通道和上下文堆栈的详细输出
- all – 所有活动
- nothing – 不记录任何内容

mfcr2_mfback_timeout：此值值得一提。有时，如果您正在呼叫手机或任何需要很长时间才能完成的呼叫，此参数可能会超时，因此它通常用于微调。如果您的某些呼叫未完成，这是您应该首先更改的参数。mfcr2_metering_pulse_timeout：一些 R2 变体使用脉冲来指示成本 mfcr2_allow_collect_calls：在巴西，音调 II-8 用于指示对方付费呼叫；此参数允许您阻止对方付费呼叫。mfcr2_double_answer：也用于在需要双重应答时避免对方付费呼叫。使用 double_answer=yes，您实际上阻止了对方付费呼叫。mfcr2_immediate_accept：允许您跳过 B/II 组信号的使用并直接进入接受状态。mfcr2_forced_release：允许您加快呼叫的释放；适用于巴西变体。

#### ANI 和 DNIS

自动号码识别 (ANI) 是呼叫者的号码。拨号号码识别服务 (DNIS) 是被呼叫的号码，或者换句话说，是拨打的号码。当收到呼叫时，通常最后四位数字会传递给 PBX，这个过程称为直接拨入 (DID)。ANI 号码实际上是 Caller ID。拨号时，ANI 将拥有呼叫者的分机，而 DNIS 将包含呼叫目标。正确配置这些参数非常重要。一些交换机只发送最后四位数字，而另一些则发送完整号码。

### DAHDI 通道格式

DAHDI 通道在拨号方案中使用以下格式：

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

示例：

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
[g] – Group identifier
[c] – Answer confirmation; A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

## IAX2 协议

在本章中，我们将了解 Inter-Asterisk eXchange (IAX) 协议，包括其优势和劣势。还将涵盖中继模式和两个 Asterisk 服务器的互连等详细信息。本文档中的所有参考资料均对应 IAX 版本 2。IAX 协议为语音和视频提供媒体传输和信令。IAX 非常创新；它在中继模式下节省带宽，并且在需要遍历 NAT 时比 SIP 简单得多。IAX 目前的主要用途是互连 Asterisk 服务器。IAX 最初是为语音创建的，但它也可以容纳视频和其他多媒体流。IAX 的灵感来自其他 VoIP 协议，例如 SIP 和 MGCP。IAX 没有使用两个独立的协议进行信令和媒体传输，而是将它们统一起来，形成了一个独特的协议。IAX 不使用 RTP 进行媒体传输；相反，它将媒体嵌入到同一个 UDP 连接中。

**Asterisk 22 中的状态。** `chan_iax2` 在 Asterisk 22 LTS 中仍然包含并得到全面支持，因此本节中的所有内容仍然有效。然而，IAX2 是一种遗留协议，几乎没有新的部署：该行业已在很大程度上收敛于 SIP（通过 Asterisk 22 中的 `chan_pjsip`），用于提供商中继和服务器互连。IAX2 剩下的主要优势是其单端口设计——所有信令和媒体都通过单个 UDP 端口（默认情况下为 4569）流动，与 SIP 及其独立的 RTP 流相比，这简化了防火墙和 NAT 配置。对于 NAT 不受关注的新 Asterisk 到 Asterisk 中继，PJSIP 中继是推荐的现代方法；此处涵盖 IAX2 是因为它仍然是一个有效的选择，特别是在只能通过防火墙打开一个 UDP 端口的情况下。

### 目标

读完本章后，您应该能够：

- 识别 IAX 协议的优势和劣势
- 描述 IAX 协议的使用场景
- 描述 IAX 中继模式的优势
- 为电话配置 iax.conf
- 配置 iax.conf 以连接到 VoIP 提供商
- 配置 iax.conf 以进行 Asterisk 互连
- 理解 IAX 身份验证

### IAX 设计

IAX 设计的主要目标是：

- 减少媒体传输和信令所需的带宽
- 提供 NAT 透明度
- 能够传输拨号方案信息
- 支持寻呼和对讲的高效使用

IAX 是一种点对点信令和媒体协议，类似于不使用 RTP 的 SIP。基本方法是在两个主机之间的单个 UDP 连接上多路复用多媒体流。这种方法最大的好处是它在遍历 NAT 上的连接时非常简单，这在 xDSL 调制解调器中很常见。IAX 使用单个端口（默认情况下为 UDP 4569），然后使用带有 15 位的呼叫号码来多路复用所有流。IAX 协议使用类似于 SIP 协议的注册和身份验证过程。可以在 http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt 找到该协议的描述

![IAX 协议在单个 UDP 端口（默认 4569）上多路复用两个端点之间的许多呼叫，使用 15 位呼叫号码来保持流分开——这使得 NAT 遍历变得简单。](../images/10-legacy-fig12.png)

### 带宽使用

VoIP 网络中使用的带宽受多种因素影响；编解码器和协议头是最重要的。IAX 协议有一个令人惊讶的功能，称为中继模式，它使用单个报头多路复用多个呼叫。通过使用 Asterisk 带宽计算器，您将看到 IAX 中继如何通过多次呼叫为您节省高达 80% 的流量。

![比较 IAX 和 SIP 开销：两个 SIP/RTP 呼叫需要两个数据包（在 156 字节开销下承载 40 字节有效载荷），而 IAX2 中继模式通过在许多微帧之间共享一个 IP/UDP 报头，在单个数据包中承载两个呼叫（在仅 66 字节开销下承载 40 字节有效载荷）。](../images/10-legacy-fig13.png)

### 通道命名

了解通道命名约定非常重要，因为在拨号方案中指定通道时将使用这些名称。用于出站通道的 IAX 通道名称格式为：

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

<user> 远程对等体上的 UserID，或 iax.conf 中配置的客户端名称 <secret> 密码。或者，它可以是 RSA 密钥的文件名，不带尾随扩展名（.key 或 .pub），并用方括号括起来 <peer> 要连接的服务器名称 <portno> 连接的端口号 <exten> 远程 Asterisk 服务器中的分机 <context> 远程 Asterisk 服务器中的上下文 <options> 可用的唯一选项是 ‘a’，表示‘请求自动应答’

#### 出站通道示例：

出站通道在 Asterisk 控制台中可见。IAX2/8590:secret@myserver/8590@default 呼叫 myserver 中的 8590 分机。它使用 8590:secret 作为名称/密码对

IAX2/iaxphone 呼叫 "iaxphone" IAX2/judy:[judyrsa]@somewhere.com 使用 judy 作为用户名和 RSA 密钥进行身份验证来呼叫 somewhere.com

#### 传入 IAX 通道的格式为：

入站通道在 Asterisk 控制台中可见。

```
IAX2/[<username>@]<host>]-<callno>
```

<username> 用户名（如果已知） <host> 连接的主机 <callno> 本地呼叫号码 传入通道示例：IAX2[flavio@8.8.30.34]/10 来自 IP 地址 8.8.30.34 的呼叫号码 10，使用 flavio 作为用户。IAX2[8.8.30.50]/11 来自 IP 地址 8.8.30.50 的呼叫号码 11。

### 使用 IAX

您可以以多种方式使用 IAX。在本节中，我们将向您展示如何为多种场景配置 IAX，包括：

- 使用 IAX 连接软电话
- 使用 IAX 将 IAX 连接到 VoIP 提供商
- 使用 IAX 连接两台服务器
- 使用 IAX 以中继模式连接两台服务器
- 调试 IAX 连接
- 使用 RSA 对密钥进行身份验证

#### 使用 IAX 连接软电话

Asterisk 支持基于 IAX 的 IP 电话，例如 ATCOM 和 Digium 的旧式 ATA（称为 IAXy），以及仍然实现 IAX2 协议的软电话。软电话、ATA 和硬电话的过程类似。要配置 IAX 设备，您需要编辑 /etc/asterisk 中的 iax.conf 文件

```
directory.
```

我们将以支持 IAX2 的软电话为例。第 1 步：备份原始 iax.conf 文件：

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

第 2 步：开始编辑新的 iax.conf 文件：

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; 非常重要的参数，它会更改可用的编解码器

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

我尝试保留示例文件的默认（非注释）行。修改了以下参数：

```
bandwidth=high
```

此行影响编解码器选择。使用 high 设置允许选择高带宽和高质量编解码器，例如由 ulaw 关键字定义的 g.711。如果您保留默认参数，您将无法选择 ulaw。在这种情况下，Asterisk 将为您提供“no codec available”消息，用于下面的配置。

```
disallow=all
allow=ulaw
```

在上述命令中，我们禁用了所有编解码器并仅启用了 ulaw。在局域网中，大多数人更喜欢使用 ulaw，因为它不是处理器密集型的，并且可以节省 CPU 周期。即使使用更多带宽，此编解码器也是可取的，因为在局域网中，您通常拥有 100 兆位以太网甚至千兆位。使用 ulaw 的语音呼叫从您的网络中使用了近 100 kbps 的带宽，这对当今的高速局域网来说是非常轻的使用。在广域网或互联网网络中，您通常会禁用 ulaw，通过语音压缩交换一些可用的 CPU 周期以获得更好的带宽使用。编解码器 gsm、g729 和 ilbc 也提供了良好的压缩系数。

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

在上述命令中，我们定义了一个名为 [2003] 的朋友。上下文是 default（在最初的实验室中，我们总是使用 default 上下文以避免混淆；此上下文将在第 9 章中全面解释）。“host=dynamic”行提供了电话 IP 地址的动态注册。第 3 步：下载并安装支持 IAX2 的软电话。您可以选择任何仍然支持 IAX2 协议的软电话进行实验室操作。第 4 步：在客户端中配置 IAX 帐户（通常为 *Add account* → IAX）。请注意，SipPulse Softphone 仅支持 SIP，无法通过 IAX2 注册，因此对于 IAX 测试，您需要一个仍然支持该协议的客户端。

第 5 步：配置 extensions.conf 文件以测试您的 IAX 设备。

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

现在，您可以在第 3 章中创建的 SIP 电话和实验室中创建的 IAX 电话之间拨号。

#### 使用 IAX 连接到 VoIP 提供商

少数 VoIP 提供商支持 IAX。您可以通过搜索“IAX providers”轻松找到 IAX 提供商。使用 IAX 提供商非常有意义，因为 IAX 可以节省大量带宽，轻松遍历 NAT，并且可以使用 RSA 密钥对进行身份验证。

![客户的 Asterisk 通过互联网上的 IAX 中继线连接到 VoIP 提供商：单个中继线承载往返提供商的所有呼叫。](../images/10-legacy-fig14.png)

在过去几个 Asterisk 版本中，支持 IAX 的商业 VoIP 提供商数量急剧下降；大多数提供商现在仅提供 SIP/PJSIP 中继线。在承诺使用 IAX 提供商之前，请确认他们积极维护其 IAX 基础设施。对于新的提供商集成，PJSIP 中继（第 3 章）是推荐的替代方案。

#### 使用 IAX 连接到提供商

第 1 步：在您最喜欢的提供商处开设一个帐户。您的提供商将为您提供三件事。

- 名称
- 密码
- IP 地址或主机名
- RSA 公钥

第 2 步：配置 iax.conf 文件以将您的 Asterisk 注册到您的提供商。将以下行添加到文件的 [general] 部分。

```
[general]
register=>name:secret@hostname/2003
```

在上述说明中，您使用您的帐户和密码向您的提供商注册。当您收到呼叫时，它将被转发到 2003 分机。

```
[name]
```

- ; 您的帐户名称或号码

```
type=peer
secret=secret
; Your password
host=hostname
```

在上述说明中，我们创建了一个对应于提供商的对等体，用于拨号目的。

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

这是 RSA 身份验证所必需的。使用来自提供商的公钥可以让您确定收到的呼叫确实来自真正的提供商。如果其他人尝试使用相同的路径，他们将无法对其进行身份验证，因为他们没有相应的私钥。第 4 步：尝试连接。要测试连接，请拨打任何号码。一些供应商提供回声测试。为此，请编辑 extensions.conf 文件。

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

转到 Asterisk CLI 并发出 reload。要验证 Asterisk 是否已向提供商注册，请使用下一个命令。

```
CLI>reload
CLI>iax2 show register
```

现在只需在连接到 Asterisk 服务器的软电话上拨打 *98。

#### 通过 IAX 中继线连接两台 Asterisk 服务器

将一台服务器连接到另一台服务器非常容易。您不需要注册它们，因为 IP 地址是已知的。您必须在 iax.conf 文件中创建对等体和用户。总部站点的所有分机都以 20 开头，后跟两位数字（例如 2000）。在分支机构中，所有分机都以 22 开头，后跟两位数字（例如 2200）。我们将使用中继线。您需要一个 DAHDI 定时源来启用此功能。第 1 步：编辑分支服务器中的 iax.conf 文件。

![使用 IAX 中继线连接两台 Asterisk 服务器：总部服务器（192.168.1.1，分机 20xx）和分支服务器（192.168.1.2，分机 22xx）通过单个 IAX 中继线相互连接——无需注册，因为两个 IP 地址都是固定的且已知的。](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

第 2 步：配置分支服务器中的 extensions.conf 文件

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

第 3 步：配置总部服务器中的 iax.conf 文件

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

第 4 步：配置总部服务器中的 extensions.conf 文件。

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

第 5 步：测试从总部服务器上的 2000 电话到分支服务器上的 2200 电话的呼叫。

### IAX 身份验证

现在让我们从实际角度分析 IAX 身份验证过程，以帮助您为每个特定需求选择最佳方法。

#### 传入连接

![传入呼叫的 IAX 身份验证决策流程：Asterisk 根据是否提供用户名、它是否匹配部分、源 IP 是否被允许以及密码（明文、MD5 或 RSA）是否匹配进行分支——接受带有该部分上下文和对等选项的呼叫，或拒绝它。](../images/10-legacy-fig16.png)

当 Asterisk 收到传入连接时，初始信息可以包括用户名（来自字段“username=”）或不包括。传入连接也有一个 IP 地址，Asterisk 也使用该地址进行身份验证。如果提供了用户，Asterisk：1. 在 iax.conf 中搜索 type=user（或 type=friend，且部分名称与用户名匹配）的条目。如果找不到，Asterisk 将拒绝连接。2. 如果找到的条目有 deny/allow 配置，它会比较呼叫者的 IP 地址，以确定是接受还是拒绝呼叫，具体取决于 deny/allow 子句。3. 它使用明文、md5 或 RSA 检查密码（secret）。4. 它接受连接并将呼叫发送到 iax.conf 文件中“context=”行中指定的上下文。如果未提供用户名，Asterisk：1. 在 iax.conf 文件中搜索包含 type=user（或 type=friend）且未指定 secret 的条目。它也会检查 deny/allow 子句。如果找到条目，则接受连接，并将部分名称用作用户的名称。2. 在 iax.conf 文件中搜索包含 type=user（或 type=friend）且指定了 secret 或 RSA 密钥的条目。它也会检查 deny/allow 子句。如果找到条目，它会尝试使用指定的 secret 对呼叫者进行身份验证；如果匹配，则接受连接。部分名称是用户的名称。假设您的 iax.conf 文件有以下条目：

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

如果呼叫有指定的用户名，例如：

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk 将尝试仅使用 iax.conf 文件中的相应条目对呼叫进行身份验证。如果指定了任何其他名称，呼叫将被拒绝。如果未指定用户，Asterisk 将尝试将连接验证为 guest。但是，如果 guest 不存在，它将尝试任何其他具有匹配 secret 的连接。换句话说，如果您在 iax.conf 文件中没有 guest 部分，恶意用户可以通过不指定用户名来尝试猜测任何匹配的 secret。IP 地址的 deny/allow 限制也适用。避免 secret 猜测的一个好方法是使用 RSA 身份验证。另一种方法是限制允许呼叫的 IP 地址。

#### IP 地址限制

permit = <ipaddr>/<netmask> 规则按顺序解释，并且全部进行评估（此概念不同于路由器和防火墙中通常找到的 ACL deny = <ipaddr>/<netmask>）。示例 #1 permit=0.0.0.0/0.0.0.0 deny=192.168.0.0/255.255.255.0 将拒绝来自 192.168.0.0/24 网络的所有数据包 示例 #2 deny=192.168.0.0/255.255.255.0 permit=0.0.0.0/0.0.0.0 它将允许任何数据包。最后一条指令取代第一条。

#### 出站连接

出站连接使用以下方法获取身份验证信息：

- dial() 应用程序传递的 IAX2 通道描述。
- iax.conf 文件中带有 type=peer 或 type=friend 的条目。
- 两种方法的组合。

#### 使用 RSA 密钥连接两台 Asterisk 服务器

可以使用带有非对称 RSA 密钥的强身份验证来使用 IAX。根据源代码 (res_krypto.c)，Asterisk 使用带有 SHA-1 算法的消息摘要的 RSA 密钥，而不是较弱的 MD5。以下是使用 RSA 密钥设置两台服务器的分步指南。

##### 为分支机构配置服务器

第 1 步：在分支服务器中生成 RSA 密钥

```
astgenkey -n
```

询问时，使用密钥名称 branch。我们使用了参数 –n 以避免在 Asterisk 重新初始化时传递密码。如果您想提高安全性，请不要使用 –n 并使用 asterisk -i 启动 Asterisk 第 2 步：将密钥复制到目录 /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

第 3 步：将公钥复制到总部服务器

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

第 4 步：编辑分支服务器中的 iax.conf 文件。

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

第 8 步：配置分支服务器中的 extensions.conf 文件

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### 为总部配置服务器

第 1 步：在总部服务器中生成 RSA 密钥

```
astgenkey -n
```

询问时，使用密钥名称 hq。第 2 步：将密钥复制到目录 /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

第 3 步：将公钥复制到 BRANCH 服务器

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

第 4 步：配置总部服务器中的 iax.conf 文件

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

第 10 步：配置总部服务器中的 extensions.conf 文件。

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

第 11 步：测试从总部服务器上的 2000 电话到分支服务器上的 2200 电话的呼叫。

### iax.conf 文件配置

文件 iax.conf 有多个参数；逐个讨论每个参数会很无聊且适得其反。所有参数以及描述都可以在示例文件中找到。在 wiki www.voip-info.org 中，您将找到关于每个参数的详细信息。在这里，我们将展示一些用于配置常规部分、对等体和用户的重要参数。

#### [General] 部分

服务器地址 bindport = <portnum> 配置 IAX UDP 端口。默认值为 4569。bindaddr = <ipaddr> 使用 0.0.0.0 将 Asterisk 绑定到所有接口，或指定特定接口的 IP 地址。编解码器选择 bandwidth = [low|medium|high] High = 所有编解码器 Medium = 除 ulaw 和 alaw 外的所有编解码器 Low = 低带宽编解码器 allow/disallow = 编解码器选择微调 [alaw|ulaw|gsm|g.729| 等]

### 抖动缓冲区 (Jitter buffer)

抖动是数据包之间的延迟变化。它是影响语音质量的最重要因素。抖动缓冲区用于补偿延迟变化。它以牺牲延迟为代价来换取更低的抖动。您可以将抖动缓冲区与水箱进行类比。两者都可以以不规则的间隔接收数据包或水，但最终会提供稳定的流量。

![作为水箱的抖动缓冲区：数据包从网络不规则地到达并填充缓冲区，然后缓冲区以稳定的速率释放它们以产生平滑的语音流。缓冲区大小（以毫秒为单位）以一点延迟换取更低的抖动；过量缓冲区带让 Asterisk 随着网络条件的变化增加或减少缓冲区。](../images/10-legacy-fig17.png)

小的抖动（即低于 20 毫秒）通常是难以察觉的。但是，高于此水平的抖动是令人讨厌的。延迟应保持在 150 毫秒以下。创建抖动缓冲区将牺牲一些延迟以获得更低的抖动——这被称为“延迟预算”的概念。您可以使用以下参数影响抖动缓冲区：

- Jitterbuffer=<yes/no> – 启用或禁用
- Dropcount=<number> - 在最后两秒内应该延迟的最大帧数。推荐设置为 3（1.5% 的丢帧）
- Maxjitterbuffer=<ms> - 通常低于 100 毫秒
- Maxexcessbuffer=<ms> - 如果网络延迟改善，抖动缓冲区可能会过大。因此，Asterisk 将尝试减少它。
- Minexcessbuffer=<ms> - 一旦过量缓冲区降至此值，Asterisk 开始增加缓冲区大小。

### 帧标记

下面的参数标记服务字段类型中的 IP 数据包。路由器可以读取此标签，从而优先处理流量。Asterisk 为此字段使用 DSCP 代码 (RFC 2474)。允许的值为 CS0、CS1、CS2、CS3、CS4、CS5、CS6、CS7、AF11、AF12、AF13、AF21、AF22、AF23、AF31、AF32、AF33、AF41、AF42、AF43 和 ef（即加速转发）。

```
tos=ef
```

### IAX2 加密

IAX 支持使用对称密钥、128 位分组密码（称为 AES，高级加密标准）进行呼叫加密。激活 IAX 中继之间的加密非常简单。在 iax.conf 文件中使用：

```
encryption=yes
```

强制加密：

```
forceencryption=yes
```

为了保证与旧版本的兼容性，您可能需要使用以下命令禁用密钥轮换：

```
keyrotate=no
```

### IAX2 调试命令

以下是 Asterisk 的一些最重要的故障排除控制台命令。

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

查看此输出，识别呼叫的开始和结束。观察使用 poke 和 pong 数据包获得的延迟和抖动信息。这些数据包有助于创建“iax2 show netstats”命令的输出。

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

要关闭调试，请使用：

```
vtsvoffice*CLI>iax2 no debug
```

### 总结

本章回顾了 IAX 协议的优势和劣势。它演示了 IAX 在多种场景下的工作方式，例如软电话和两台 Asterisk 服务器之间的中继线。中继模式允许您通过在单个数据包中承载多个呼叫来节省带宽。最后，您学习了可用于检查状态和调试协议的控制台命令。

## 遗留 SIP：chan_sip 和 sip.conf（在 Asterisk 21+ 中移除）

> **遗留/历史：** 本节中的所有内容都使用旧的 `chan_sip`
> 驱动程序及其 `sip.conf` 配置文件。 `chan_sip` 已被弃用多个版本，并 **在 Asterisk 21 中移除**，因此它 **在 Asterisk 22 中不存在**。以下所有 `sip.conf` 示例都无法在当前系统上运行——它们保留在此处仅用于记录遗留部署的工作方式并帮助您迁移它们。对于执行任何此操作的现代、受支持的方式，请参阅 *SIP & PJSIP in depth* 章节的 *PJSIP: the SIP channel* 部分。SIP *协议* 理论（方法、注册、代理/重定向、SDP、NAT 类型）是协议级的，存在于该章节中；以下纯粹是已移除的 `chan_sip` **配置**。

在 Asterisk 20 之前的遗留系统上，SIP 是在 `/etc/asterisk/sip.conf` 中配置的，它曾经是更改次数第二多的文件（仅次于 `extensions.conf`）。以下部分展示了 `chan_sip` 如何将 Asterisk 连接到 SIP 提供商，如何使用 SIP 将两个 Asterisk 连接在一起，域支持、状态、编解码器/DTMF/QoS 选项、身份验证和 NAT——随后是迁移所有内容到 PJSIP 的指南。

### 将 Asterisk 连接到 SIP 提供商 (sip.conf)

Asterisk 通常用于连接到 SIP VoIP 提供商。与传统提供商相比，VoIP 提供商通常具有更好的电话呼叫费率。VoIP 提供商的另一个有趣且吸引人的点是可以在其他城市甚至外国购买 DID 号码的可能性。这些是使用 VoIP 进行电信的好理由。在本节中，您将学习遗留 `chan_sip` 如何将 Asterisk 连接到 VoIP 提供商。将 Asterisk 连接到 SIP 提供商需要三个步骤。可以通过与您最喜欢的提供商建立帐户来进行测试。第 1 步：在 sip.conf 中向 SIP 提供商注册 要连接到 SIP 提供商，您将需要提供商提供的以下信息：

![Asterisk 通过互联网或专用 WAN 连接到 VoIP 服务提供商，本地 SIP 电话注册到 Asterisk 服务器](../images/07-sip-and-pjsip-fig07.png)

- 用户名
- 密码和远程密码（使用 secret 验证入站请求，使用 remotesecret 验证出站请求）
- 主机名
- 域
- 允许的编解码器

此配置将允许您的提供商定位 Asterisk 的 IP 地址。在以下语句中，我们告诉 Asterisk 注册到由主机名定义的 SIP 提供商，并通知提供商 Asterisk 的 IP 地址。该语句表示您希望在分机 4100 接收呼叫。在 sip.conf 文件的 [general] 部分中，输入以下行：

```
register=>name:secret@hostname/4100
```

第 2 步：在 sip.conf 中配置 [peer] 创建一个 peer 类型的条目到所需的提供商，以简化 Asterisk 的拨号。

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

第 3 步：在拨号方案中创建到提供商的路由 我们将选择数字 010 作为到提供商的目标路由。要拨打提供商内部的 #610000，只需拨打 010610000。

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)=”Flavio Gonçalves”)
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### 特定于提供商场景的 SIP 选项

以下讨论检查了 sip.conf 文件中用于连接到 VoIP 提供商的选项的详细信息。

```
register=>username:password@hostname/4100
```

sip.conf 文件中注册的指令用于向提供商注册。注册事务使用名称和密码进行身份验证。您可以使用斜杠 (“/”) 为传入呼叫提供分机。从技术上讲，分机将放置在 SIP 请求的“Contact”头字段中。注册行为可以由某些参数控制：

```
registertimeout=20
registerattempts=10
```

要检查注册是否成功，遗留控制台命令是 `sip show registry`。在 Asterisk 22 上，等效命令是 `pjsip show registrations`（出站注册）和 `pjsip show endpoints`（端点状态）。

参数“username”用于身份验证摘要。摘要是使用用户名、密码和领域计算的：

```
username=username
```

Host 定义 VoIP 提供商地址或名称：

```
host=hostname
```

参数 Fromuser 和 Fromdomain 有时是身份验证所必需的。这些参数用于 SIP From 头字段：

```
fromuser=username
fromdomain=hostname
```

当您连接到 VoIP 提供商时，需要凭据。初始邀请后，提供商会向您发送一条名为“407 Proxy Authentication Required”的消息；您在随后的 INVITE 消息中提供凭据。对于传入呼叫，您的 Asterisk 服务器将询问提供商的凭据。显然，提供商没有您的 Asterisk 服务器的有效凭据。当您使用 insecure=invite 时，您是在告诉 Asterisk 不要向提供商发送“407 Proxy Authentication Required”并接受传入呼叫。您还可以使用 insecure=port, invite 根据 IP 地址匹配对等体，而不匹配端口号。

```
insecure=invite, port
```

### 使用 SIP 将两台 Asterisk 服务器连接在一起 (sip.conf)

您可以使用 SIP 将两台 Asterisk 盒子互连。在继续此配置之前，注意拨号方案非常重要。用户通常希望以最小的努力连接其他 PBX。这里的想法是仅使用分机号码连接到另一个 PBX。第 1 步：编辑服务器 A 中的 sip.conf 文件：

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

第 2 步：编辑服务器 B 中的 sip.conf 文件：

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![使用 SIP 连接两台 Asterisk 服务器：服务器 A（分机 4400/4401）和服务器 B（分机 4500/4501）交换 SIP 信令，以便每个 PBX 上的用户都可以拨打另一个](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

第 3 步：编辑服务器 A 中的 extensions.conf 文件：

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

第 4 步：编辑服务器 B 中的 extensions.conf 文件：

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk 域支持 (sip.conf)

SIP 协议遵循互联网架构。配置 SIP 之前要做的第一件事是正确设置 DNS 服务器。在 SIP 环境中，您可以呼叫位于任何 SIP 代理中的用户，其他用户也可以使用您的 SIP 统一资源标识符 (URI) 呼叫您。要为 SIP 设置 DNS 服务器，您必须将 SRV 记录添加到您的 DNS 服务器。

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

配置 DNS 后，您可以使用指向 SIP 用户、SIP 电话或电话分机的 URI。SIP URI 看起来类似于电子邮件地址（例如，sip:chuck@yourpartnerdomain.com）。使用 SIP URI，无需电话号码即可从一部 SIP 电话拨打到另一部。要拨打外部用户，只需使用如下所示的语句。

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

某些参数可以控制域行为。

```
srvlookup=yes
```

此参数在出站呼叫上启用 DNS SRV 查找。使用此参数，可以使用基于域的 SIP 名称拨打电话。

```
allowguest=yes
```

此参数允许在不进行身份验证的情况下处理外部邀请。它在 general 部分或域语句中定义的上下文中处理呼叫。警告：如果您在 general 部分定义了一个可以访问 PSTN 的上下文，外部用户可以通过您的 PBX 拨打 PSTN。在这种情况下，您将承担任何费用。仅允许您自己的分机在 general 部分定义的上下文中。

![通过域连接到其他 SIP 服务器：youdomain.com 和 yourpartnerdomain.com 交换 SIP 信令，因此 lee 和 bruce 等用户可以使用 SIP URI 呼叫 chuck 和 norris](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

域命令允许您在 Asterisk 中处理多个域。如果呼叫来自特定域，它将被定向到特定上下文。

```
;autodomain=yes
```

此参数在允许的域中包含本地 IP 和主机名。

```
;allowexternaldomains=no
```

默认值为 yes。取消注释该行以禁止呼叫外部域。

### SIP 高级配置 (sip.conf)

本节解释了遗留 SIP 通道的一些高级参数，例如状态、编解码器选择、DTMF 选项和 QoS 数据包标记。这些 **概念**（BLF/状态、编解码器协商、DTMF 模式、DSCP 标记）延续到 PJSIP，但此处显示的 `sip.conf` 参数名称在 Asterisk 22 中 **不存在**。在 PJSIP 上，DTMF 模式是端点上的 `dtmf_mode=`，编解码器使用 `allow=`/`disallow=` 设置。

#### SIP 状态 (Presence)

SIP 状态在 Asterisk 中是部分实现的。Asterisk 支持 SUBSCRIBE 和 NOTIFY 用户等请求，具体取决于通道的状态。Asterisk 不支持 SIP 方法 PUBLISH。换句话说，您可以订阅通道的状态（忙碌、空闲和振铃），但不能发布“离开”或“请勿打扰”等信息。状态最常见的场景是忙灯场 (BLF)，其中您模拟具有每个分机和中继线灯的 KS 系统的行为。用于状态的 SIP 参数：

- allowsubscribe=yes：允许 SIP 订阅方法
- subscribecontext=sip_subscribers：查找提示的上下文
- notifyring=yes：在振铃时发送 SIP NOTIFY
- notifyhold=yes：在保持时发送 SIP NOTIFY
- counteronpeer（从 Asterisk 1.4.x 的 limitonpeer 重命名）：仅在对等端应用计数器
- callcounter=yes：在设备中启用呼叫计数器。
- busylevel=1：将设备视为忙碌的呼叫数量阈值。

例如：第 1 步：使用 Asterisk 测试 SIP 状态并不难。首先，让我们配置文件 sip.conf 和 extensions.conf。

在文件 sip.conf 中

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

第 2 步：现在配置软电话以使用状态。我们将向您展示如何配置 SipPulse Softphone。

- 序列：右键单击->SIP 帐户设置->属性->状态
- 将状态模型从点对点更改为状态代理，这将使软电话订阅 Asterisk 以获取 SIP 事件。

第 3 步：将联系人添加到其他软电话。在此示例中，SipPulse Softphone 是帐户 2000，因此我们将为帐户 2001 添加一个联系人。序列：打开右侧面板（软电话中的状态面板）->单击联系人->添加联系人。填写名称 2001。显示为 2001，不要忘记选中框显示此联系人的可用性。

第 4 步：现在拨打分机 2001 并检查右侧面板中电话的状态。使用控制台命令 `core show hints` 查看服务器中状态的变化（在遗留 chan_sip 中，`sip show inuse` 显示了您在每条线路上有多少呼叫）。在 Asterisk 22 上，使用 `pjsip show endpoints` 检查端点和通道状态。状态/BLF 状态出现在软电话的联系人或 BLF 面板中——它显示的确切方式取决于客户端。

#### 编解码器配置

编解码器配置简单直接。您可以在 [general] 部分或对等体/用户部分设置单词 allow 和 disallow。最佳实践是标准化编解码器以避免转码，这是处理器密集型的。请对消息和提示使用相同的编解码器。

```
[general]
disallow=all
allow=g729
```

#### DTMF 选项

在某些情况下，您会将数字传递给语音邮件或交互式语音应答 (IVR) 等应用程序。正确传递 DTMF 很重要。传递 DTMF 的最简单方法称为 inband。它在 sip.conf 文件的 [general] 或对等体/用户部分中设置。当您设置 dtmfmode=inband 时，DTMF 音调作为音频通道中的声音生成。此方法的主要问题是，当您使用 g729 等编解码器压缩音频通道时，声音会失真，并且 DTMF 音调无法正确识别。如果您计划使用 dtmfmode=inband，请使用 g.711 编解码器（ulaw 和 alaw）。

```
dtmfmode=inband
```

另一种方法是使用 RFC2833，它允许您将 DTMF 音调作为 RTP 数据包中的命名事件传递。

```
dtmfmode=rfc2833
```

最后，您可以在 SIP 数据包中传递 DTMF 数字，而不是 RTP 数据包。此方法在 RFC3265（信令事件）和 RFC2976 中定义。

```
dtmfmode=info
```

继 1.2 版本发布后，现在可以使用：

```
dtmfmode=auto
```

这尝试使用 RFC2833；如果不可能，则使用带内音调。

#### 服务质量 (QoS) 标记配置

QoS 是一组负责语音质量的技术。QoS 的实现旨在减少带宽、延迟和抖动。QoS 在交换机和路由器中实现，而不是由 Asterisk 本身实现。但是，Asterisk 可以通过标记数据包以进行快速交付来帮助路由器和交换机。标记是使用 RFC 2474 和 RFC2475 中定义的区分服务代码点 (DSCP) 完成的。

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

从 1.4 版本开始，您可以为信令 (SIP)、音频 (RTP) 和视频 (RTP) 指定不同的代码。

### SIP 身份验证 (sip.conf)

当遗留 `chan_sip` 收到 SIP 呼叫时，它遵循下图中描述的规则。三个参数在 SIP 身份验证中发挥了重要作用。在 Asterisk 22 上，身份验证改为使用 PJSIP `auth` 对象（`type=auth`、`auth_type=userpass`、`username=`、`password=`）配置，这些对象由端点引用，IP 访问控制在端点上通过 `permit=`/`deny=` 或通过 `acl` 完成。

![遗留 chan_sip 身份验证决策流程：Asterisk 根据 sip.conf 检查 From 头，尝试匹配 type=user/peer 部分和 MD5 凭据，并回退到 insecure=invite 或 allowguest，然后再允许或拒绝呼叫](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

此参数控制没有相应对等体的用户是否可以在没有名称和密码的情况下进行身份验证。我们在域支持部分讨论了此参数。

```
insecure=invite,port
```

当我们使用 insecure=invite 时，Asterisk 不会生成消息“407 Proxy Authentication Required”。没有此消息，用户可以在不进行身份验证的情况下拨打电话。这通常用于连接到 VoIP 服务提供商。来自 VoIP 服务提供商的呼叫通常不进行身份验证。

```
autocreatepeer=yes/no
```

当 Asterisk 连接到 SIP 代理时，使用此命令。它为每个呼叫动态创建一个对等体。启用此选项后，任何 UAC 都可以连接到 Asterisk 服务器。将 IP 连接限制为 SIP 代理非常重要。SIP 代理反过来负责访问控制。对等体配置基于常规选项以及 SIP 数据包的“Contact”头字段。警告：请极其谨慎地使用此功能，因为它完全打开了 Asterisk。

```
secret=secret, remotesecret=secret
```

此参数配置用于身份验证的密码，使用 secret 进行入站请求，使用 remotesecret 进行出站请求。如果您不想在文本文件中显示密码，可以使用 md5secret 包含哈希而不是密码。要生成 MD5 密码，您可以使用：

```
echo –n “username:realm:secret” |md5sum
```

然后使用以下语句：

```
md5secret=0b0e5d467890....
```

警告：不要忘记使用 –n 参数；回车符将用于 md5 计算。

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

上述语句将拒绝所有 IP 地址，并仅允许来自本地网络 (192.168.1.0/24) 的 UAC。

#### RTP 选项

可以控制一些 RTP 参数。

```
rtptimeout=60
```

当不在保持状态时，这会终止超过 60 秒没有 RTP 活动的呼叫。

```
rtpholdtimeout=120
```

即使在保持状态下，这也会终止没有 RTP 活动的呼叫（应该大于 rtptimeout）。

### SIP NAT 遍历 (sip.conf)

NAT *理论*（四种 NAT 类型、Contact 头问题、保持连接以及强制媒体通过服务器）是协议级的，在 *SIP & PJSIP in depth* 章节中介绍。此处显示的 `sip.conf` 参数（`nat=`、`qualify=`、`directmedia=`、`externaddr=`、`localnet=`）是 **遗留 chan_sip**，已在 Asterisk 21+ 中移除。在 PJSIP 上，这些映射到传输/端点设置，例如传输上的 `rewrite_contact=yes`、`force_rport=yes`、`rtp_symmetric=yes`、`direct_media=no`、`external_media_address`、`external_signaling_address` 和 `local_net=`，加上 AOR 上的 `qualify_frequency=`。

在遗留 chan_sip 中，参数 `nat` 有五个选项：

- nat = no — 不做除 RFC3581 之外的特殊 NAT 处理
- nat = force_rport — 假装有一个 rport 参数，即使没有
- nat = comedia — 将媒体发送到 Asterisk 接收它的端口，无论 SDP 说发送到哪里
- nat = auto_force_rport — 如果 Asterisk 检测到 NAT，则设置 force_rport 选项（默认）
- nat = auto_comedia — 如果 Asterisk 检测到 NAT，则设置 comedia 选项

当您在 sip.conf 文件中放入语句“nat=force_rport”时，您是在告诉 Asterisk 忽略 SIP 头中“Contact”头字段包含的地址，并使用数据包 IP 头中的源 IP 地址和端口，并将媒体发送回接收它的地址，忽略 SDP 头的内容。

```
nat=force_rport,comedia
```

有必要保持 NAT 映射打开。如果 NAT 超时，Asterisk 无法向 UAC 发送邀请。UAC 可以发送呼叫，但不能接收任何呼叫。以下语句可用于保持 NAT 打开。

```
qualify=yes
```

Qualify 将定期使用 OPTIONS 方法发送 SIP 数据包，这将有助于保持 NAT 打开。Qualify 每 60 秒发送一次 OPTIONS，当主机不可达时每 10 秒发送一次。您可以使用“sip show peers”查看对等体的延迟。如果用户的 NAT 是对称类型的，则无法直接从一个 UAC 发送数据包到另一个；在这种情况下，您必须使用以下命令强制 RTP 通过 Asterisk：

```
directmedia=no
```

#### Asterisk 在 NAT 后面 (sip.conf)

所有以前的场景都假设 Asterisk 服务器具有外部（有效）互联网地址。有时 Asterisk 服务器是在带有 NAT 的防火墙后面实现的。在这种情况下，有必要进行一些额外的配置。

![Asterisk 在 NAT 后面：防火墙将公共地址 200.180.4.168 映射到内部 Asterisk 服务器 (192.168.1.100)，在 UDP 5060 上转发 SIP，并在 rtp.conf 中定义的 RTP 范围 UDP 10000–20000 上转发](../images/07-sip-and-pjsip-fig13.png)

第 1 步：配置防火墙以将 UDP 端口 5060 静态重定向到 Asterisk 服务器。第 2 步：配置防火墙以静态重定向从 10000 到 20000 的 UDP 端口。如果您想限制打开的端口数量，您可以编辑 rtp.conf 文件以更改 RTP 端口范围。另一种方法是使用支持 SIP 协议的智能防火墙来动态打开 RTP 端口。

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

第 3 步：配置 Asterisk 以在 SIP 数据包的头字段中包含外部地址，包括会话描述协议 (SDP)。您可以通过将以下两个语句添加到 sip.conf 文件中来实现这一点：

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

第一个参数 externaddr 告诉 Asterisk 在 SIP 头中包含外部 IP 地址以用于外部目标。第二个参数 localnet 允许 Asterisk 区分外部地址和内部地址。可选地，如果您在服务器上使用带有 DHCP 地址的动态 DNS，则可以使用 externhost。

### SIP 拨号字符串 (chan_sip)

下面显示的 `SIP/...` 拨号字符串技术是已移除的 chan_sip 驱动程序。在 Asterisk 22 上使用 `PJSIP/...` 技术代替——例如 `Dial(PJSIP/2000)` 或 `Dial(PJSIP/${EXTEN}@provider)`。形式和含义在其他方面是类似的。

您可以使用不同的拨号字符串呼叫遗留 SIP 目标：

```
SIP/peer
```

- ; 需要在 sip.conf 中定义对等体

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

示例包括：

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## 将遗留 chan_sip 系统迁移到 PJSIP

由于 `chan_sip` 已在 Asterisk 21 中移除，并且在 Asterisk 22 中消失，因此任何
现有的 `sip.conf` 部署都必须迁移到 PJSIP。最大的概念转变是单个 `sip.conf` `[peer]` 或 `[friend]` 被拆分为多个 PJSIP 对象，每个对象都有一个 `type=`：一个 **endpoint**（呼叫/编解码器/媒体设置），一个或多个 **aor** 对象（设备可以到达/注册的地方），一个 **auth** 对象（凭据），以及一个共享的 **transport**（监听套接字，NAT 地址）。下表映射了最常见的概念。

| 遗留 sip.conf 概念 | PJSIP 等效项 (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` 块 | `type=endpoint` + `type=aor` + `type=auth`（通过 `auth=` 和 `aors=` 引用） |
| `type=friend` / `type=peer` / `type=user` | 单个 `type=endpoint`（PJSIP 没有 friend/peer/user 区别） |
| `host=dynamic`（设备注册） | 带有 `max_contacts=1` 的 `type=aor`；设备 REGISTER 以更新其联系人 |
| `host=<ip/hostname>`（静态） | 带有静态 `contact=sip:host:port` 的 `type=aor` |
| `register=>user:secret@host/ext`（出站） | `type=registration`（`server_uri=`、`client_uri=`、`outbound_auth=`） |
| `secret=` / `username=` | `type=auth`、`auth_type=userpass`、`username=`、`password=` |
| `context=` | 端点上的 `context=` |
| `disallow=all` / `allow=ulaw` | 端点上的 `disallow=all` / `allow=ulaw`（语法相同） |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — 还有 `inband`、`info`、`auto` |
| `directmedia=yes/no` | 端点上的 `direct_media=yes/no` |
| `nat=force_rport,comedia` | `force_rport=yes`、`rewrite_contact=yes`、`rtp_symmetric=yes`（端点） |
| `qualify=yes` | **aor** 上的 `qualify_frequency=`（秒） |
| `externaddr=` | **transport** 上的 `external_media_address=` 和 `external_signaling_address=` |
| `localnet=` | **transport** 上的 `local_net=` |
| `insecure=invite`（提供商，无身份验证） | 省略 `auth=`/`outbound_auth=` 并使用 `identify`（`type=identify`、`match=`） |
| `allowguest=yes` | `anonymous` 端点 + `allow_unauthenticated_options`（谨慎使用） |
| `tos_sip` / `tos_audio` | 端点上的 `tos_audio` / `tos_video`（以及 `cos_audio` / `cos_video`） |

在遗留 `sip.conf` 中看起来像这样的注册分机：

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

在 Asterisk 22 上的 `pjsip.conf` 中变为以下内容：

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### sip_to_pjsip.py 转换脚本

Asterisk 发布了一个辅助脚本 **`sip_to_pjsip.py`**，它读取现有的
`sip.conf` 并生成 `pjsip.conf`。您可以直接在
/etc/asterisk 目录中运行它。该实用程序位于 Asterisk 源代码树下的
`contrib/scripts/sip_to_pjsip/`，其中 `${PATH_TO_ASTERISK_SOURCE}` 是找到 Asterisk 源代码文件的路径
（通常为 /usr/src/asterisk-22.x.y/）：

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

如果您使用 `--help` 选项运行它，您将看到它的选项：

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

它还接受可选的位置参数——`[input-file [output-file]]`，
默认为当前目录中的 `sip.conf` 和 `pjsip.conf`。

将其输出视为 **起点**：审查每个生成的对象，
特别是传输、NAT 设置和编解码器列表，并在投入生产前进行彻底测试。

让我们迁移 VoIP School Blackbelt (voip.school) 配套实验室中的 sip.conf

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.api4com.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.api4com.com
fromuser=1020
fromdomain=sip.api4com.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.api4com.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.api4com.com
client_uri = sip:1020@sip.api4com.com:5600
server_uri = sip:sip.api4com.com:5600
[auth_reg_sip.api4com.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.api4com.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.api4com.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.api4com.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

虽然转换看起来没问题，但我们可以看到 qualify=yes 等一些元素无法直接映射。要修复，您必须在 aor 部分添加命令 qualify_frequency=time（以秒为单位）。示例如下。

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

完整的 PJSIP 配置在 *SIP & PJSIP in depth* 章节中介绍，docs.asterisk.org 上的官方文档有完整的通道覆盖。在我们的配套实验室 voip.school 中，实验室 5 让您可以练习刚刚学到的内容。

## 测验

1. 关于两个模拟外汇接口，标记正确的陈述（选择所有适用项）：
   - A. FXO 接口连接到公共交换电话网 (PSTN) 中心局并从中获取拨号音。
   - B. FXS 接口为标准模拟电话、传真或调制解调器提供拨号音和振铃电源。
   - C. FXS 接口是将 Asterisk 连接到电信线路的正确方式。
   - D. FXO 接口也可以连接到遗留 PBX 的分机端口。
2. 模拟线路上的监控信令包括以下哪些（选择所有适用项）？
   - A. 挂机
   - B. 摘机
   - C. 振铃
   - D. DTMF
3. DAHDI 模拟卡上的回声、爆音和噪音通常是由以下原因引起的：
   - A. Asterisk 的编译方式
   - B. PCI 中断冲突
   - C. 不正确的 SIP 编解码器
   - D. 缺失的拨号方案
4. 为了在模拟通道上进行精确计费，您必须准确检测远端何时应答。您在 Asterisk 上激活（并向电信公司请求）什么功能来执行此操作？
   - A. 应答反转
   - B. 计费反转
   - C. 极性反转
   - D. 拨号音生成
5. DAHDI 硬件独立于 Asterisk：物理卡在 `/etc/dahdi/system.conf` 中配置，而 `chan_dahdi.conf` 定义 Asterisk 通道，而不是硬件本身。
   - A. 正确
   - B. 错误
6. 关于数字中继线容量和信令，标记正确的陈述（选择所有适用项）：
   - A. E1 中继线承载 30 个语音通道，T1 中继线承载 24 个。
   - B. ISDN PRI 在 E1 上使用 30B+D，在 T1 上使用 23B+D。
   - C. ISDN 是 CCS 信令的一个示例，而 MFC/R2 是 CAS 信令的一个示例。
   - D. T1 是欧洲和拉丁美洲最常用的数字中继线。
7. 哪个实用程序会自动检测 DAHDI 卡并生成 `/etc/dahdi/system.conf` 和 `dahdi-channels.conf`？
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. 将遗留 `sip.conf` `[friend]` 迁移到 PJSIP 时，单个块必须拆分为多个对象。哪一组 PJSIP `type=` 对象通常替换一个注册的 `[friend]`？
   - A. `type=endpoint`、`type=aor` 和 `type=auth`
   - B. `type=peer` 和 `type=user`
   - C. 仅 `type=sip`
   - D. `type=channel` 和 `type=device`
9. 在两台 Asterisk 服务器之间使用 IAX2 中继模式的主要实际优势是什么？
   - A. 它默认使用 TLS 加密每个呼叫
   - B. 它在单个报头下承载多个呼叫，节省带宽
   - C. 它消除了对任何编解码器的需求
   - D. 它为每个呼叫分配一个单独的 UDP 端口以获得更好的质量
10. RSA 密钥可用于 IAX2 身份验证。您必须保密哪个密钥，并将哪个密钥提供给另一台服务器？
    - A. 对公钥保密；共享私钥
    - B. 对私钥保密；共享公钥
    - C. 对共享密钥保密；共享私钥
    - D. 两个密钥都必须共享

**答案：** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
