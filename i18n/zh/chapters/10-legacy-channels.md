# Legacy channels: analog, TDM & IAX2

在 2026 年的纯 VoIP 世界中，本章涉及的通道类型日益罕见：大多数新部署都是基于以太网的 SIP 中继和 PJSIP 端点，根本不使用任何电话硬件。Asterisk 22 仍然完整支持它们中的大多数。模拟（FXO/FXS）和数字 TDM（E1/T1/ISDN PRI/BRI）连接通过 DAHDI 提供——这是一套最初由 Digium 开发的驱动程序栈，Digium 于 2018 年被 Sangoma 收购，此前因商标争议而将早期的 Zaptel 驱动改名。服务器间的 IAX2 连接由 `chan_iax2` 提供，虽然仍在发布并受支持，但现已明确成为遗留协议。

本章还收录了 **legacy SIP** 内容：旧的 `chan_sip` 驱动及其 `sip.conf` 配置——已在 Asterisk 21 中移除，在 Asterisk 22 中彻底消失——以及将现有 `sip.conf` 系统迁移到 PJSIP 的完整指南。如果你在 PJSIP 上运行的是纯 SIP 环境，没有电话卡、没有 IAX2 中继，也没有需要转换的 legacy `sip.conf`，则可以安全地跳过本章。

## 目标

在本章结束时，你应该能够：

- 使用 DAHDI 将 Asterisk 通过 FXO/FXS 接口连接到模拟线路和电话；
- 识别数字 TDM 连接（E1/T1、ISDN PRI/BRI）以及其配置方式；
- 为服务器间中继配置 IAX2（`chan_iax2`），并了解其为何已成为遗留技术；
- 识别已废弃的 `chan_sip` 驱动以及你仍可能遇到的 `sip.conf` 语法；
- 将现有的 `chan_sip`/`sip.conf` 系统迁移到 PJSIP。

## 模拟通道 (FXO/FXS)

截至 Asterisk 22，DAHDI 和模拟电话卡仍然得到完整支持，且 DAHDI 仍然可以针对当前内核进行构建。不过，大多数新部署仍然是纯 VoIP（SIP 中继、PJSIP），因此模拟/TDM 硬件现在是一种小众选择——主要出现在传统环境、农村 PSTN 连接或受监管的市场中。以下内容仍然适用于这些场景。

连接公共交换电话网 (PSTN) 有多种方式。最佳方式取决于当地电话公司提供的接入方式。最简单的方式是使用模拟线路，类似于家庭使用的线路。在本节中，我们将展示如何配置来自 Sangoma™（前身为 Digium™）和 Xorcom™ 的模拟卡。

### 目标

本章结束时，你应该能够：

- 识别主要的电话术语和缩写；
- 理解何时使用数字电路和模拟电路；
- 区分 FXS 与 FXO 的区别；以及
- 为 FXS 和 FXO 配置 Asterisk。

### 电话基础

大多数模拟实现使用一对称为 tip 和 ring 的铜线。当回路闭合时，电话会从电信交换机（或私有 PBX）收到拨号音。最常用的信令是环路启动；还有其他不太常见的信令类型，包括在一些国家使用的地线启动。信令分为三类：

- 监督信令
- 地址信令
- 信息信令

#### 监督信令

主要的监督信令包括 on-hook、off-hook 和 ringing。

- **On-Hook** – 当用户将电话挂在挂钩上时，PBX 中断并阻止电流通过。在此状态下，电路被称为 on-hook。此时，仅响铃器处于激活状态。
- **Off-Hook** – 在开始通话之前，电话需要切换到 off-hook 状态。将听筒从挂钩上取下会闭合回路，并向 PBX 表示用户意图拨打电话。收到此指示后，PBX 产生拨号音，提示用户可以输入目的地址（即电话号码）。
- **Ringing** – 当用户呼叫另一部电话时，会向响铃器发送电压，以提醒对方有来电。信令因国家而异，不同国家使用不同的音调。

你可以通过修改 `indications.conf` 文件来为你的国家自定义 Asterisk 音调。例如：

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

您可以使用两种信令方式进行拨号。第一种也是最常用的是双音多频（dtmf），另一种是脉冲拨号（用于老式旋转拨号电话）。电话有一个拨号键盘，每个按键对应两个频率：一个高频和一个低频。在 dtmf 信令的情况下，这些音调的组合指示所按的数字。MFC/R2 使用一种不同于 dtmf 的多频音调。

#### 信息信令

信息信令显示通话的进展和不同的事件。

- 拨号音
- 占线音
- 回铃音
- 拥塞音
- 无效号码
- 确认音

### PSTN 接口

正如旧式 PBX 的情况，通常需要将 Asterisk PBX 连接到 PSTN。这里我们将展示如何实现。通常你有三种电话线路选项。

- Analog: 最常见的家庭和小型企业形式，通常通过一对金属铜线提供。
- Digital: 在需要多条线路时使用。数字线路通常由 CSU/DSU 或光纤复用器提供。用户端连接器通常是 RJ45。在某些国家，E1 线路使用两个同轴 BNC 连接器提供；在这种情况下，您需要一个转接头将 RJ45 插孔连接到电话板。
- SIP: 此选项是最近开发的。电话线路通过带有 SIP 信令（VoIP）的数据连接提供。这是与 Asterisk 配合使用的好选项，因为您无需购买电话卡。电话直接传输到以太网端口。另一个优势是通过避免编解码器转码，您可能能够释放 CPU 资源。

### 模拟 FXS、FXO 和 E&M 接口

几种模拟接口可供选择。了解这些接口之间的差异对于学习如何连接电话网络以及其他 PBX 至关重要。在本节中，我们将向您展示 E&M 接口。虽然该接口目前不再支持 Asterisk，且已被多家厂商停产，但您仍可能在路由器和 PBX 上遇到此类接口，因此了解它的工作原理会更有帮助。

#### 外部交换 (FX) 接口

FX 接口是模拟的。术语 “Foreign eXchange” 用于指向 PSTN 中央局（CO）的接入中继。Foreign eXchange Office (FXO)

![Asterisk 在模拟电话（FXS）和电信线路（FXO）之间：FXS 端向电话提供拨号音和振铃，而 FXO 端从中心局获取拨号音。](../images/10-legacy-fig01.png)

FXO 接口用于连接到中心局（CO）或其他 PBX 的分机。它直接与来自 PSTN 的电话线路通信。另一种选择是将 FXO 接口连接到现有的 PBX，从而实现 Asterisk 与传统 PBX 之间的通信。将 Asterisk 连接到 PBX 端口并通过 VoIP 提供远程分机通常称为 off‑promises extension（OPX）。FXO 接口接收拨号音。  

Foreign eXchange Station（FXS）  
FXS 接口为模拟电话、调制解调器或传真机供电。FXS 提供拨号音和电话电源。

#### 中继信令

- 循环启动
- 接地启动
- 酷启动

在 Asterisk 中使用 kewlstart 信令几乎是默认的。kewlstart 本身不是信令，而是通过监控对端的情况为电路添加智能。kewlstart 基于 loop-start。大多数交换机不支持此功能，该功能用于获取挂断通知。

- Loopstart: 用于大多数模拟线路，它允许电话指示“on-hook”和“off-hook”，并让交换机指示“ring”和“no-ring”。这可能是大多数人在家中使用的方式。名称来源于线路始终保持打开状态。当你闭合回路时，交换机会提供拨号音。来电通过在打开的对线上施加100V的振铃电压来信号。

![Asterisk 作为 VoIP 网关运行：FXO 端口连接到传统 PBX 分机，而远程 Asterisk 通过 IP 将该线路传递给模拟电话，使用 FXS 端口（离站分机，或 OPX）。](../images/10-legacy-fig02.png)

- Groundstart: 类似于 Loopstart。当您想发起呼叫时，线路的一侧被短路。当交换机识别到此状态时，它会通过打开的对线反向电压，然后回路闭合。因此，线路会先变为占线，然后才提供给呼叫方。
- Kewlstart: 为电路添加智能，允许监控对端。Kewlstart 融合了许多来自 loop-start 的优势。

### Asterisk 电话通道设置

要配置电话接口卡，需要完成多个步骤。在本章中，我们将展示三种最常见的场景：

- 使用 FXS 的模拟连接
- 使用 FXO 的模拟连接
- 使用 FXS 和 FXO 接口的 Astribank™ 连接

### Configuration Procedure (valid in both cases)

在为 Asterisk 选择硬件之前，您应当考虑将要安装和启用的并发通话数量、服务以及编解码器。Asterisk 是一个对 CPU 需求很高的应用，这也是我们建议为 Asterisk 配置专用机器的原因。计算机内部可安装的接口卡数量受限于可用的插槽和中断数。通常更倾向于安装一块拥有八个语音接口的单卡，而不是两块各四个接口的卡。另一种选择是使用 USB 通道板，例如 Xorcom Astribank。最近，一些厂商（如 CIANET）开始生产 TDMoE 通道板，使得连接数十个模拟接口变得更加简便。

![Xorcom Astribank：一款19英寸机架式USB通道卡，提供数十个FXS/FXO端口（此处为32端口单元），且不占用主机的PCI插槽。](../images/10-legacy-fig03.png)

#### 示例 1：一个 FXO，一个 FXS 安装

在本例中，我们将使用一块 Sangoma TDM400 电话接口卡（以前以 Digium TDM400 销售），配备一个 FXS 模块和一个 FXO 模块。所需的步骤列在下面：

1. 安装模拟卡 FXS、FXO，或两者皆装。  
2. 配置文件 `/etc/dahdi/system.conf`（以前是 `/etc/zaptel.conf`）。  
3. 使用 `dahdi_genconf` 生成配置文件。  
4. 加载 DAHDI 接口的驱动。  
5. 执行 `dahdi_test` 以验证中断丢失。  
6. 执行 `dahdi_cfg` 配置驱动。  
7. 在 `chan_dahdi.conf` 文件中配置 DAHDI 通道，然后加载 Asterisk。

##### Step 1: 安装 TDM400 板

TDM404P 卡包含 FXS 和 FXO 模块。连接 FXS（S110M，绿色）和 FXO（X100M，红色）模块。如果使用 FXS 模块，请使用 molex 连接器将卡直接连接到电源。处理接口卡之前请佩戴防静电保护，以免损坏硬件。Sangoma（前身为 Digium）模拟卡还支持硬件回声消除模块 VPMADT032。

##### Step 2: 使用 dahdi_genconf 生成配置

关于配置的好消息是新的实用工具 `dahdi_genconf`, 它会自动检测并生成 DAHDI 接口的配置。该实用工具会生成两个文件：

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (使用 `users` 选项)
- 所有这些文件使用 `chan_dahdi full` 选项

在执行`dahdi_genconf`之前，重要的是配置文件`genconf_parameters`（通常称为`gen_parameters.conf`）：

![Sangoma/Digium TDM404P模拟卡：最多四个FXS或FXO模块插入编号端口，可选硬件回声消除子卡以及为FXS模块提供专用的12 V电源连接器。](../images/10-legacy-fig04.png)

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

The `genconf_parameters` file lets you customize your configuration. The most important parameters for analog lines are:

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

警告：必须为通道至少配置回声消除算法。base_exten 参数定义了 FXS 分机的基本拨号计划。在这种情况下，第一个 FXS 通道将获得分机号 4000，第二个 4001，依此类推。创建线路（context_phones）和中继（context_lines）的 context 非常重要。生成文件后，您应该在文件 `/etc/asterisk/chan_dahdi.conf`中包含文件 `/etc/asterisk/dahdi-channels.conf`：

```
#include dahdi-channels.conf
```

注意：模拟信令有点令人困惑；它始终与卡的类型相反。FXS 卡使用 FXO 信令，而 FXO 卡使用 FXS 信令。Asterisk 与这些设备通信时，好像它位于相反的一侧。

##### 第3步：加载内核驱动程序

现在你必须加载 chan_dahdi 模块以及相关的卡内核驱动。使用 dahdi_hardware 检测你的卡和驱动名称。例如：

| 卡 | 驱动程序 | 描述 |
| --- | --- | --- |
| TE410P | wct4xxp | 4路E1/T1 - 3.3V PCI |
| TE405P | wct4xxp | 4路E1/T1 - 5V PCI |
| TDM400P | wctdm | 4个FXS/FXO |
| T100P | wct1xxp | 1个T1 |
| E100P | wct1xxp | 1个E1 |
| X100P | wcfxo | 1个FXO |

加载驱动程序的命令：

```
modprobe dahdi
modprobe wctdm
```

##### 步骤 4：使用 dahdi_test 实用工具

一个重要的实用工具是 dahdi_test，用于验证 DAHDI 卡的中断丢失。音频质量问题通常与中断冲突有关。要确认您的 DAHDI 卡没有与其他卡共享中断，请使用以下命令：

```
#cat /proc/interrupts
```

您可以使用随 DAHDI 卡编译的 dahdi_test 实用程序来验证中断丢失的数量。低于 99.987% 的数值表明可能存在问题。

##### 第 5 步：使用 dahdi_cfg 实用程序配置驱动

DAHDI 采用一种不寻常的驱动加载系统。首先配置 /etc/dahdi/system.conf，然后使用 dahdi_cfg 将这些配置应用到 DAHDI 驱动。在本例中，dahdi_cfg 用于配置 FX 接口的信令。要查看结果，您可以在命令后追加 “-vvvvv” 以获得详细输出。

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

如果通道成功加载，您将看到类似上面所示的输出。用户经常错误地在 `chan_dahdi.conf` 中配置了通道之间的信号颠倒。如果出现这种情况，您会看到如下所示的消息：

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

在成功配置硬件后，您可以继续进行 Asterisk 的配置。

##### 第 6 步：配置 /etc/asterisk/chan_dahdi.conf 文件

这听起来很奇怪，但在配置了 /etc/dahdi/system.conf 之后，您已经配置了卡本身。DAHDI 还能用于其他用途，例如路由和 SS7。要在 Asterisk 中使用它，必须配置 Asterisk 的 DAHDI 通道。Asterisk 中的每个通道都必须被定义；SIP/PJSIP 通道在 pjsip.conf 中定义（注意：chan_sip 和 sip.conf 已在 Asterisk 21 中移除），而 TDM 通道则在 chan_dahdi.conf 中定义。这会创建用于您拨号计划的逻辑 TDM 通道。

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

Several options are available in the chan_dahdi.conf file. A description of all options would be boring and counterproductive; instead, we will focus on the main option groups available for easy understanding.

#### 常规选项（通道独立）

These options work for any channel: context: Defines the incoming context.

```
context=default
```

channel: 定义通道或通道范围。每个通道定义将继承在声明之前定义的选项。通道可以单独标识，或在同一行通过逗号分隔。范围可以使用 “-” 定义。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: 允许将通道作为一个组进行处理。如果您拨打的是组号而不是通道号，则使用第一个可用的通道。如果通道是电话，当您呼叫一个组时，所有电话会同时响铃。使用逗号，您可以为同一通道指定多个组。

```
group=1
group=3,5
```

language: 打开国际化并配置语言。此功能将为特定语言配置系统消息。English 是唯一在标准安装中提供完整提示的语言。musiconhold: 选择保持音乐类。

#### Caller ID options

有许多 callerid 选项。某些可以被禁用，尽管大多数默认已启用。usecallerid: 为后续通道启用或禁用 callerid 传输（Yes/No）。注意：如果您的系统在接听前出现两次振铃，请尝试禁用此功能。它应立即接听。hidecallerid: 定义是否隐藏外发 callerid（Yes/No）。callerid: 为特定通道配置 callerid 字符串。caller 可以使用 asreceived 进行配置。这主要在 trunk 接口中用于指示来入 callerid。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Supports callerid during call waiting. useincomingcalleridondahditransfer: Uses the incoming callerid in a transfer.

#### Call Waiting

Asterisk 在 FXS 通道中支持呼叫等待。如果有人尝试该分机，用户将收到等待音。要启用呼叫等待：

```
callwaiting=yes
```

要在呼叫等待中支持来电显示：

```
callwaitingcallerid=yes
```

#### 音频质量选项

调整回声消除既是技术活也是艺术。这些选项会调整影响 DAHDI 通道音频质量的某些 Asterisk 参数。它们可以帮助改善模拟接口的音频质量。

#### fxotune 实用工具

fxotune 是用于对 FXO 模块的某些参数进行微调的实用工具。此微调用于校正由混合器引起的阻抗不匹配。该实用工具有三种操作模式：

- Detection (-i)：检测并修复现有的 FXO 通道，并将配置保存到

```
fxotune.conf
```

- Dump mode (-d)：生成波形文件到 fxotune_dump.vals
- Startup mode (-s)：读取文件 fxotune.conf 并将其应用到 FXO 模块

重要的是要了解，您必须在启动 Asterisk 之前的系统加载中插入指令 fxotune –s：

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### 回声消除

大多数回声消除算法通过生成接收信号的多个副本来工作，每个副本都延迟特定的时间量。滤波器的抽头数量决定了需要消除的回声延迟的大小。然后将这些延迟的副本进行调整并从接收信号中减去。关键在于只调整延迟信号以去除回声，同时不使用过多的 CPU 周期。从用户的角度来看，选择合适的回声消除算法非常重要。默认算法是 MG2；不过，还有另外两种可选方案：Sangoma（前身为 Digium）提供的高性能回声消除（High Performance Echo Cancellation，HPEC）以及 David Rowe 开发的开源回声消除（OSLEC）。

OSLEC (https://www.rowetel.com/?page_id=454) 已合并到 Linux 内核——它位于内核的 `drivers/staging/echo` 区域——并且 DAHDI 是基于它构建的，而不是提供单独的下载。要更改回声消除算法，请在 `/etc/dahdi/system.conf` 中设置 `echo_can` 参数。例如：

```
echo_can=oslec
```

Asterisk 中的回声消除由文件 /etc/asterisk/chan- 中的三个参数控制。

```
dahdi.conf.
```

- **echocancel**：禁用或启用回声消除。建议保持此功能开启。它接受 “yes” 或 tap 的数量。（解释：回声消除是如何工作的？大多数回声消除算法通过生成接收信号的多个副本来工作，每个副本都延迟一个很小的时间间隔。这个小的延迟称为 “tap”。tap 的数量决定了可以消除的回声延迟。这些副本被延迟、调整后从原始信号中减去。关键在于将延迟的信号精确调整到足以消除回声的程度。）
- **echocancelwhenbridged**：在纯 TDM 呼叫期间启用或禁用回声消除器。通常没有必要使用此选项。
- **rxgain**：调节音频接收增益，以增大或减小接收音量（-100% 到 100%）。
- **txgain**：调节音频发送增益，以增大或减小发送音量（-100% 到 100%）。

例如：

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 计费选项

这些选项会更改通话信息在通话详细记录（CDR）数据库中的记录方式。amaflags：配置影响 CDR 分类的 AMA 标志。它接受以下值：

- billing
- documentation
- omit
- default

accountcode：为特定通道配置账户代码。它可以包含任意字母数字值——通常是部门或用户名。

```
accountcode=finance
amaflags=billing
```

### 呼叫进度选项

这些项目用于获取有关呼叫进度的信息。在公共接口中，检测呼叫进度并确定是否已接通或占线可能很有用。占线检测仍属高度实验性，并受特定参数的约束。

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

这些参数（如上）指定接口是否尝试检测忙音、用于成功检测的音调数量以及忙音的模式。忙音检测仍属实验性功能，某些额外参数可以在 Makefile 中进行修改。为了检测通话的接通时间（这对精确计费至关重要），可以使用极性反转来标记确切的接通时刻。如果您计划对通话收费或仅希望拥有用于对比的精确计费信息，这一点尤为重要。通常需要联系电话公司请求此项服务。

```
answeronpolarityswitch=yes
```

在某些国家，也可以使用极性反转来检测通话的挂断。

```
hanguponpolarityswitch=yes
```

#### Options for phones

这些选项用于连接到 FXS 接口的电话。所有直接连接到 DAHDI 接口的模拟电话所提供的功能均由 Asterisk 控制。

- **adsi** (Analog Display Services Interface)：这是一套电信标准，部分运营商用来提供如购票等服务。
- **cancallforward**：启用或禁用呼叫转移（*72 启用，*73 禁用）。
- **calleridcallwaiting**：在来电等待提示期间显示来电者 ID（是/否）。
- **immediate**：在即时模式下，通道不提供拨号音，而是直接跳转到已定义上下文中的 “s” 分机。此方式用于创建热线。
- **threewaycalling**：启用或禁用三方会议。
- **mailbox**：提醒用户有可用的语音邮件。可以是声音提示或视觉指示（如果电话支持此功能）。参数为邮箱号码。
- **callgroup**：将电话分组以便拨号或抢接。
- **pickupgroup**：用于呼叫抢接的电话组。

### Useful DAHDI CLI commands

一旦 Asterisk 运行并加载了 DAHDI 通道，您可以在 Asterisk CLI 中检查通道状态。这些命令在 Asterisk 22 中仍然有效。

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDI 通道格式

DAHDI 通道在 dialplan 中使用以下格式：

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

例如：

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## 数字通道（E1/T1/PRI / TDM）

截至 Asterisk 22，DAHDI 和 libpri 仍然得到完全支持，但 TDM 数字中继 (E1/T1/ISDN PRI) 正在新部署中越来越多地被 SIP 中继取代。本节在需要 TDM 连接的情况下仍然完全适用；在全新环境中，SIP 中继（Chapter 3）通常能够在不使用电话硬件的情况下提供相同的通道密度。

数字通道非常常见，如果您想专注于大型客户，就需要学习如何实现这些通道。当通道数量较多——通常超过 8 条时，使用 T1/E1/J1 等数字接口是相当常见的。T1 在美国非常普遍，E1 在欧洲常见，J1 则在日本使用。这类通道能够提供较高的电路密度——每个 T1 通道可容纳 24 条线路，E1 通道可容纳 30 条线路。

在拉丁美洲、中国和非洲，常用一种称为 MFC/R2 的通道关联信令（CAS）。本章将研究如何使用库 OpenR2 实现 MFC/R2。在美国和欧洲，集成服务数字网（ISDN）PRI 是最常见的信令。章节还将讨论 ISDN 基本速率接口（BRI），它在欧洲的中等规模应用中非常常见。

All examples in the book concentrate on DAHDI channels. Some cards are implemented using proprietary channels, so please check with your manufacturer for further details on how to configure your specific card.

### 目标

在本章结束时，您将能够：

- 识别数字电话中使用的主要术语  
- 区分 CAS 和 CCS 信令  
- 区分 R2 和 ISDN 信令  
- 使用 ISDN 信令配置接口  
- 使用 R2 信令配置接口

### E1/T1 数字线路

数字线路 E1/T1 是在需要实现大量通道时的一个选项。单个 E1 电路能够支持 30 条同时通话，并且您可以使用诸如直接入站拨号（DID）、来电显示（caller identification）以及高级信令等功能。E1/T1 线路可以通过双绞线、光纤和微波等多种方式抵达贵公司，具体取决于所在国家。数字线路通过 UTP、光纤或微波传输到贵公司。调制解调器和复用器（MUX）用于传输物理线路。连接到 T1 线路始终使用 RJ45 接口。然而，E1 线路也可以使用 BNC 接口进行配置。提前了解您将收到的接口类型非常重要，尤其是对于 E1 线路。通常，直到 RJ45 接口之前的所有设备均由电信运营商提供。

![E1/T1 电路的配置方式：运营商可以通过 UTP 铜线（E1 使用 HDSL 调制解调器，或 T1 使用直接卡连接）、光纤通过光复用器，或微波无线链路提供中继。](../images/10-legacy-fig05.png)

![UTP或BNC？大多数数字卡使用RJ45（UTP）连接器，但某些E1线路采用双BNC同轴电缆，在这种情况下需要使用balun将同轴对适配到卡的RJ45插口】(../images/10-legacy-fig06.png)

#### 语音是如何转换为比特的？

模拟信号以每秒 8,000 次的采样率进行采样，以创建模拟语音的数字版本。此编码称为脉冲编码调制 (PCM)。在美国和日本，信号使用 law 编码（在 Asterisk 中称为 ulaw）。在世界其他地区，使用 alaw 编码。

![脉冲编码调制（PCM）：4 kHz 模拟语音信号以每秒 8,000 次的采样率（奈奎斯特）进行采样，并编码为 64 Kbps 的数字比特流。](../images/10-legacy-fig07.png)

#### 时分复用

模拟线路在只需要少量通道时是合理的。使用时分复用（TDM）时，可以将多个通道塞入单个数据连接。当需要大量电路时，电话公司通常会提供数字中继（digital trunk），这是一种数据电路，语音以 PCM 的数字格式传输。每个时隙使用 64 Kbps 带宽来传输单个语音通道。

![时间分复用在E1和T1中的应用：E1帧携带32个时隙，速率为2048 Kbps（DS0 #0用于帧同步，DS0 #16用于信令），而T1帧携带24个时隙，速率为1544 Kbps，使用一位进行同步并采用抢位方案进行信令](../images/10-legacy-fig08.png)

在美国，最常见的数字中继是 T1，拥有 24 条可用线路；在欧洲和拉丁美洲，E1 中继有 30 条线路。一些公司提供通道数更少的分数 T1/E1。  
抢位信令 有时 T1 中继使用抢位方案，即借用一个比特进行信令。在 T1 中继上，数据/语音通道在每个时隙上以 56 Kbps 传输。正如您可能观察到的，当使用抢位时，T1 电路并不会因为同步和信令而失去两个时隙。

#### T1/E1 线路代码

T1s 和 E1s 实际上是数据电路，并且有一种数据编码决定位的解释方式。对于 E1，最常用的线路编码是第 1 层的 HDB3 和第 2 层的 CCS。了解您的数字中继是如何配置的最简单方法是向电信公司询问此信息。您需要这些信息来配置文件 /etc/dahdi/system.conf。

#### T1/E1 信令

重要的是要了解，T1/E1 线路可能使用不同类型的信令进行传输，例如：

- T1 带抢位信令
- T1 带 ISDN 信令
- E1 带 MFC/R2（CAS - 通道关联信令）
- E1 带 ISDN 信令

ISDN 在欧洲和美国经常使用。它是一种数字语音网络，由国际电信联盟（ITU）于 1984 年标准化。ISDN 提供两种通道：

- 承载通道
  - 语音
  - 数据
- 数据通道
  - 带外信令
  - LAPD 信令
  - Q.931

通常，ISDN 线路通过两种物理方式提供：

- Basic rate interface (BRI)
  - 又称 2B+D
  - 两个承载 (64K) 信道和一个数据 (16K) 信道
  - 使用一对铜线，速率为 148Kbps。
- Primary rate interface (PRI)
  - 通过 T1/E1 中继提供
  - T1 使用 23B+D
  - E1 使用 30B+D

Sometimes, E1 circuits use a CAS signaling scheme called MFC/R2, which was defined by the ITU as a standard known as Q.421/Q441. This is frequently found in Latin America and Asia. Several telephony companies in these countries use customized variants of MFC/R2. Hence, you will need to know the correct country variation in order to make it work.

### ISDN BRI

Channels using ISDN BRI signalling are very popular in Europe. Most ISDN BRI cards for Asterisk supports an S/T interface with NT and TE capabilities. The TE (terminal) connection is the one used to connect to the TELCO or to other PBXs configured as network termination (NT). The NT is used to connect phones and PBXs configured as TE. ISDN BRI provides two data/voice channels and one signalling channel. ISDN BRI cards are available from several vendors of interface cards for Asterisk.

### 为您的 Asterisk 服务器选择电话卡

有几家制造商提供与 Asterisk 兼容的数字卡。选择卡片时取决于以下一些因素：

#### 数据总线

您的电脑上有多种总线类型。为服务器选择合适的卡非常重要。以下概述列出了最常用的卡：

- 32 位 PCI 5V，常见于大多数计算机，包括台式机
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
  - Sangoma A101, A102, and A104
- 32/64 位 PCI 3.3V，基本上出现在服务器上
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
- PCI Express，出现在台式机和服务器上
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, and AEX800
  - Sangoma A101, A102, and A104

这些卡系列最初由 Digium 开发，Sangoma 于 2018 年收购；它们现在在 Sangoma 品牌下销售和支持。此处列出的许多旧 SKU 已停产，购买前请在 www.sangoma.com 确认当前型号的可用性。

- MiniPCI 在嵌入式系统中可用
  - OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI), and B400M(ISDN BRI)
- USB 2.0 在大多数现代 PC 中可用。基于 USB 的解决方案能够实现极高密度的模拟和数字通道。该总线支持 480 Mbps，每个语音通道占用 64 Kbps。使用 USB hubs 时，单个端口可实现高达千个模拟端口的密度。
  - Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet。Ethernet 的最大优势是允许卡由多个服务器连接。高可用性解决方案通常是这些设备的核心应用。该方案的优势在于可以使用没有空余 PCI slots 的服务器或 blade servers。
  - Redfone FoneBridge (up to four E1 circuits)

### 使用硬件回声消除

硬件回声消除可以减轻主机 CPU 的负载。对于拥有多个 E1 接口的卡，硬件回声消除能够帮助缓解处理器的压力。新型的增强软件回声消除器（如 OSLEC）正在降低对硬件回声消除器的需求。要在硬件和软件回声消除器之间做出选择，您应当考虑服务器可用的处理能力以及 E1 电路的数量。使用 OSLEC（参考：Xorcom Ltd.）进行 128 taps 振幅的回声消除时，每个语音通道的回声消除过程可能会消耗高达九 MIPS（每秒数百万条指令）。如果假设每条指令对应一个 CPU 周期（这并不总是基于处理器和软件实现本身的正确假设），那么四个 E1 大约需要 1.080 GHz 的处理能力。

#### 信令类型

选择信令类型（例如 T1 CAS、T1 PRI、E1 CAS R2 或 E1 CAS ISDN）并非易事。这实际上取决于您所在地区的可用资源以及价格。公共信道信令（CCS）通常优于信道关联信令（CAS），但它往往不可用。在美国，您通常可以自行选择，因为大多数电信公司为普通用户提供 T1 CAS，为高级用户（例如呼叫中心）提供 T1 PRI。在拉丁美洲，E1 CAS R2 较为普遍，但在部分城市也可以使用 ISDN PRI。

![DAHDI 软件架构：Asterisk 与 `chan_dahdi` 通道驱动程序通信，该驱动程序随后加载协议库 libpri（ISDN）、libopenr2（MFC/R2）和 libss7（SS7）；这些位于 `/dev/dahdi` 接口、DAHDI 内核驱动以及特定卡的接口内核驱动之上。】(../images/10-legacy-fig09.png)

实现 R2 对于安装名为 OpenR2（www.libopenr2.org）的库是必要的，该库由 Moises Silva 开发，并且在安装前需要对 Asterisk 进行补丁——本章后面会展示一个简单的步骤。该库已经通过了多项测试，并在我们的多个客户的生产环境中使用。个人认为，只要可用，ISDN 总是最佳选择。某些运营商可以访问信令系统 7（SS7），这是一种在电话公司之间可用的 CCS 信令。SS7 有专有和开源的解决方案可供选择。库 libss7 用于在 Asterisk 上支持 SS7。

### Asterisk 电话通道设置

配置电话接口卡涉及多个必要步骤。在本章中，我们将展示三种最常见的场景：

- 使用 ISDN PRI 的数字连接
- 使用 ISDN BRI 的数字连接
- 使用 MFC/R2 的数字连接

有两种方式配置 DAHDI 通道。第一种是手动配置，完全控制所有参数。第二种是使用实用程序 dahdi_genconf 来检测并配置卡。

#### 自动检测和配置

感谢 DAHDI 开发团队，我们现在拥有卡的自动检测和配置。步骤 1：要自动生成配置，请使用实用程序 dahdi_genconf，它将检测卡并生成文件 /etc/dahdi/system.conf 和 dahdi-channels.conf。

```
dahdi_genconf
```

步骤 2：在文件 chan_dahdi.conf 的最后一行，包含文件 dahdi-channels.conf

```
#include dahdi_channels.conf
```

步骤 3：在文件 modules 中对所有未使用的模块进行注释，或直接使用：

```
dahdi_genconf modules
```

#### 手动配置

另一种方式是手动配置接口。下面是一些 DAHDI 通道配置的示例。

##### 示例 #1 – 使用 ISDN 的两个 T1/E1 通道

所需步骤：

1. TE205P 或 TE210P 安装
2. `/etc/dahdi/system.conf` 文件配置
3. DAHDI 驱动加载
4. `dahdi_test` 实用工具
5. `dahdi_cfg` 实用工具
6. `chan_dahdi.conf` 文件配置
7. Asterisk 加载与测试

步骤 1：TE205P 安装。在安装 TE205P 之前，了解 TE205P 与 TE210P 卡之间的差异非常重要。TE210P 卡使用 64 位总线，供电为 3.3 伏，几乎只在服务器主板上出现。如果指定此接口卡，请确保您的硬件支持 64 位、3.3V 总线。TE205P 卡使用 5V PCI，常见于台式电脑。我们在本示例中选择了带有两个 span 的 TE205P 接口卡，因为它更容易降为单 span 卡或扩展为四 span 卡。这些卡目前已在 Sangoma 品牌下销售（原 Digium）。

![Sangoma/Digium TE205P 双 span E1/T1 卡：两个 RJ45 端口用于数字中继，板载跳线（E1/T1/J1 选择器）设置线路标准](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

TDM 数字卡的配置与其模拟对应卡的配置略有不同。首先，我们需要配置板卡的 span，然后再配置通道。span 按照卡的识别顺序依次编号。换句话说，如果你有多块接口卡，就很难确定每个 span 属于哪一块卡。使用 `dahdi_hardware` 来检查每个 span 上安装了哪些硬件。示例 #1（2×T1 PRI）

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

# 示例 #2 (2xE1 PRI)

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

Step 3: 加载内核驱动 使用 dahdi_hardware 检查您需要安装的驱动程序。

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

要加载，请使用：

```
modprobe dahdi
modprobe wct2xxp
```

步骤 4：使用 dahdi_test，检查中断丢失  
您可以使用随 DAHDI 卡编译的 dahdi_test 实用程序验证中断丢失的数量。低于 99.987% 的数值表明可能存在问题。您将在以下位置找到 dahdi_test  

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

步骤 5：使用 dahdi_cfg 实用程序 这是针对一个分数 E1（15 端口）跨度和两个 FXO 端口的 dahdi_cfg 正确输出。

```
#./dahdi_cfg -vvvv
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

步骤 6：在文件 /etc/asterisk/chan_dahdi.conf 中配置 DAHDI 示例 #1（2xT1）

```
callerid="John Doe"<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

# 示例 #2 (2xE1)

```
callerid="Flavio Eduardo" <4830258580>
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

Use signaling=bri_cpe_ptmp for point to multipoint BRI. Currently, BRI point to multipoint is not supported in NT mode.

#### 加载内核驱动

After configuring the drivers, you may simply restart the server. If you have installed DAHDI with make config, you won’t need to do anything extra. The kernel driver will be automatically loaded and configured. However, sometimes it is useful to load and unload the drivers manually. Example:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

The first command loads the driver and the second, dahdi_cfg, applies the configuration to the kernel driver.

### 故障排除

有时第一次会出现问题。让我们检查一些用于排查 DAHDI 的资源。步骤 1：检查操作系统是否已识别该卡。Sangoma/Digium 卡通常被识别为 ISDN 调制解调器。

```
lspci -v
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

步骤 2：检查内核驱动是否正确加载，使用：

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

Step 3: 验证与连接物理层相关的告警状态。要验证 E1 连接的物理层，您可以使用以下 Asterisk CLI 命令。

```
dahdi show status
```

警报指示端口存在问题：Red Alarm：无法与远程交换机保持同步。这通常是物理问题，例如线路编码或帧格式不匹配。Yellow alarm：表示远程交换机处于 Red Alarm 状态。这说明远程交换机未收到您的传输。Blue Alarm：在所有时隙上接收全部未成帧的 1；dahdi_tool 目前无法检测到 Blue Alarm。Loopback：端口处于本地或远程环回状态。

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Step 4: 要检测 Asterisk 服务器上 DAHDI 的问题，首先使用以下方式检查通道是否被识别：

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

Step 5: 检查 ISDN 第 3 层的状态，也称为 q.931。您可以使用 `pri show spans`（列出所有 span）或 `pri show span <n>`（针对特定 span）来检查 ISDN 第 3 层是否已启动：

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

Use `pri show spans` (plural) 一次列出所有已配置的 PRI span 的状态。

Check a specific channel. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
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

debug pri span x: 如果在完成所有操作后仍然有问题，请开始调试 pri span。此命令启用对 ISDN 呼叫的详细调试。当你认为某些情况不正确时，它是一个重要的命令。你可以检测到拨错的数字以及其他问题。下面我们展示一个成功呼叫的调试输出示例。若需要将未成功的呼叫与没有问题的呼叫进行比较，请参考此示例。一个技巧是使用 core set verbose=0 只接收 ISDN q.931 消息。

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
> [a1]
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

文件 chan_dahdi.conf 提供了多种选项。对所有选项进行逐一描述既枯燥又适得其反。这里我们将重点说明主要的选项组，以帮助更好地理解。

#### 通用选项（与通道无关）

context: 定义入站 context。

```
context=default
```

channel: 定义通道或通道范围。每个通道定义将继承在声明之前定义的选项。通道可以单独标识，也可以在同一行使用逗号分隔。范围可以使用 “-” 定义。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: 允许将通道视为一个组。如果您拨打组号而不是通道号，将使用第一个可用的通道。如果通道是电话，当您呼叫一个组时，所有电话会同时响铃。使用逗号，您可以为同一通道指定多个组。

```
group=1
group=3,5
```

language: 打开国际化并配置语言。此功能将为特定语言配置系统消息。英语是标准安装中唯一提供完整提示的语言。musiconhold: 选择保持音乐类。

#### ISDN 选项

switchtype: 取决于所使用的 PBX 或交换机。在欧洲和拉丁美洲，EuroISDN 很常见。

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: 必需用于某些需要拨号计划规范的交换机。许多交换机会忽略此选项。有效的选项有 private、national、international 和 unknown。

```
pridialplan = unknown
```

prilocaldialplan：对某些交换机是必需的，通常未知。

```
prilocaldialplan = unknown
```

overlapdial: Overlap dialing 用于在连接建立后传递数字。您可以使用块模式编号（overlapdial=no）或数字模式（overlapdial=yes）。块模式通常由操作员使用。  
signaling: 为后续通道配置信令类型。这些参数应与 chan_dahdi.conf 文件中的对应项相匹配。正确的选择取决于可用的通道。对于 ISDN，您可能需要选择以下五个选项：

- pri_cpe: 当设备是 CPE（有时称为 client、user 或 slave）时使用。这是最简单、使用最广泛的信令形式。有时，当您尝试连接到私有 PBX 时，PBX 也常被配置为 CPE。在这种情况下，请在 Asterisk 中使用 pri_net 信令。  
- pri_net: 当 Asterisk 连接到配置为 CPE 的私有 PBX 时使用。该信令常被称为 host、master 或 network。  
- bri_cpe: 当 Asterisk 作为 CPE 连接到 ISDN BRI 中继时使用。  
- bri_net: 当 Asterisk 连接到配置为终端（TE）的 ISDN 电话或 PBX 时使用。  
- bri_cpe_ptmp: 与 bri_cpe 相同，但用于点对多点架构。

#### CallerID options

可用的 Caller ID 选项很多。有些可以禁用，尽管大多数默认是启用的。  
usecallerid: 为后续通道启用或禁用 Caller ID 传输（Yes/No）。注意：如果您的系统在应答前需要两次振铃，请尝试禁用此功能，以便立即应答。  
hidecallerid: 隐藏 Caller ID（Yes/No）。  
calleridcallwaiting: 在呼叫等待提示期间启用接收 Caller ID（Yes/No）。  
callerid: 为特定通道配置 Caller ID 字符串。可以在 trunk 接口中使用 “asreceived” 将 Caller ID 直接转发。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

注意：大多数电信运营商要求您配置正确的来电显示号码。如果未传递正确的来电显示号码，您将无法通过运营商拨出电话。另一方面，即使未配置来电显示号码，您仍然可以接收来电。

#### 音频质量选项

这些选项会调整影响 DAHDI 通道音频质量的某些 Asterisk 参数。

- **echocancel**：禁用或启用回声消除。建议保持此功能启用。它接受 “yes” 或 tap 数量。（解释：回声消除是如何工作的？大多数回声消除算法通过生成接收信号的多个副本来工作，每个副本都会延迟一个小间隔。这个小的延迟称为 “tap”。tap 的数量决定了可以消除的回声延迟。这些副本被延迟、调整后从原始信号中减去。关键在于将延迟信号精确调整到消除回声所需的程度。）
- **echocancelwhenbridged**：在纯 TDM 通话期间启用或禁用回声消除器。通常不需要此功能。
- **rxgain**：调节音频接收增益，以增加或降低接收音量（-100% 到 100%）。
- **txgain**：调节音频发送增益，以增加或降低发送音量（-100% 到 100%）。

示例：

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 计费选项

这些选项改变了在通话详细记录（CDR）数据库中记录通话信息的方式。amaflags：影响 CDR 的分类。它接受以下值：

- billing
- documentation
- omit
- default

accountcode：它为特定通道配置一个账户代码。它可以包含任意字母数字值，通常是部门或用户名。

```
accountcode=finance
amaflags=billing
```

### MFC/R2 配置

MFC/R2 在拉丁美洲的多个国家、中国、非洲以及一些欧洲国家使用。如果您所在地区有 ISDN，建议使用 ISDN，因为它更优越且更受青睐。

#### 理解问题

用于信令 MFC/R2 的卡与用于信令 ISDN 的卡相同。可以在 DAHDI 通道上使用名为 libopenR2 (www.libopenr2.com) 的库来实现 MFC/R2。该库在 Asterisk 1.6.2 之前的版本中不存在。

##### Understanding the MFC/R2 protocol

MFC/R2 协议将 in-band 和 out-of-band 信令相结合。地址信令通过 in-band 使用一组音调转发，而通道信息则通过 timeslot 16 以 out-of-band 信令方式传输。

**Line Signaling (ITU-T Q.421).** 在时隙 16 中，每个语音通道使用四个 ABCD 位来指示其状态和呼叫控制。C 位和 D 位很少使用。在某些国家，它们可用于计量（计费用的脉冲计量）。在正常对话中，双方都在工作：主叫方和被叫方。来自主叫方的信令称为前向信令，而被叫方使用后向信令。我们将前向信令标记为 Af 和 Bf，后向信令标记为 Ab 和 Bb。

| 状态 | ABCD 前向 | ABCD 后向 |
| --- | --- | --- |
| 空闲/已释放 | 1001 | 1001 |
| 已占用 | 0001 | 1001 |
| 占用确认 | 0001 | 1101 |
| 已应答 | 0001 | 0101 |
| 清除后向 | 0001 | 1101 |
| 清除前向（在清除后向之前） | 1001 | 0101 |
| 清除前向（断开确认） | 1001 | 1001 |
| 已阻塞 | 1001 | 1101 |

MFC/R2 是由 ITU 定义的。遗憾的是，多个国家根据自身需求对该标准进行了定制。因此，各国之间的标准出现了差异。

**互登记信号 (ITU-T Q.441).** MFC/R2 信令使用两种音调的组合。下表显示了 ITU 标准。

Signal group I（前向）:

| Description | Forward signal |
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
| 国家代码指示符，需要外发半回声抑制器 | I-11 |
| 国家代码指示符，不需要回声抑制器 | I-12 |
| 测试呼叫指示符 | I-13 |
| 国家代码指示符，已插入外发半回声抑制器 | I-14 |
| 未使用 | I-15 |

信号组 II（前向）：

| Description | Forward signal |
| --- | --- |
| 无优先级的用户 | II-1 |
| 有优先级的用户 | II-2 |
| 维护设备 | II-3 |
| 备用 | II-4 |
| 操作员 | II-5 |
| 数据传输 | II-6 |
| 无前向转移功能的用户或操作员 | II-7 |
| 数据传输 | II-8 |
| 有优先级的用户 | II-9 |
| 有前向转移功能的操作员 | II-10 |
| 备用 | II-11 |
| 备用 | II-12 |
| 备用 | II-13 |
| 备用 | II-14 |
| 备用 | II-15 |

Signal group A（向后）：

| Description | Backward signal |
| --- | --- |
| 发送下一个数字 (n+1) | A-1 |
| 发送倒数第二个数字 (n-1) | A-2 |
| 地址完成，切换到接收 Group B 信号 | A-3 |
| 国家网络拥塞 | A-4 |
| 发送主叫方类别 | A-5 |
| 地址完成，计费，设置通话条件 | A-6 |
| 发送倒数第三个数字 (n-2) | A-7 |
| 发送倒数第四个数字 (n-3) | A-8 |
| 备用 | A-9 |
| 备用 | A-10 |
| 发送国家代码指示符 | A-11 |
| 发送语言或区分数字 | A-12 |
| 发送电路性质 | A-13 |
| 请求回声抑制器使用信息 | A-14 |
| 国际交换中心或其输出处拥塞 | A-15 |

Signal group B（反向）：

| Description | Backward signal |
| --- | --- |
| 备用 | B-1 |
| 发送特殊信息音 | B-2 |
| 用户线路忙 | B-3 |
| 拥塞（从 A 组切换到 B 组后） | B-4 |
| 未分配号码 | B-5 |
| 用户线路空闲，计费 | B-6 |
| 用户线路空闲，免费 | B-7 |
| 用户线路故障 | B-8 |
| 备用 | B-9 |
| 备用 | B-10 |
| 备用 | B-11 |
| 备用 | B-12 |
| 备用 | B-13 |
| 备用 | B-14 |
| 备用 | B-15 |

#### MFC/R2 序列

以下序列展示了从 Asterisk 的分机发起到 PSTN 终端的呼叫。PSTN 终止了呼叫并结束了通信。

![Asterisk 与电信之间完整的 MFC/R2 呼叫流程：线路信令（Idle、Seized、Seize Ack、Answer、Clearback、Clear Forward）在时隙 16 中交换，拨出的数字和向后“发送下一个数字”信号（groups I/A/B）在带内传输，可听音调传递给用户.](../images/10-legacy-fig11.png)

### 如何使用驱动 libopenr2

项目由 Moises Silva 发起，灵感来源于 Steve Underwood 编写的 Unicall 通道驱动。OpenR2 库目前是 Asterisk 最稳定的软件解决方案。使用该方案，我们可以使用任何兼容 DAHDI 的数字卡。以前，MFC/R2 只能使用专有解决方案，我使用过的最佳方案之一是 Khomp 提供的，www.khomp.com.br。在 Asterisk 22 中，只要在编译时存在该库，libopenR2 的 MFC/R2 支持就已内置——无需外部补丁。下面的步骤展示了历史手动安装过程供参考；在现代系统上，请先通过发行版的包管理器安装 `libopenr2-dev` 再运行 `./configure`，然后在 `make menuselect` 中启用 `chan_dahdi`。

以下步骤从当前的 Git 仓库构建 openr2 和 Asterisk。它们作为从源码构建的站点的参考保留；在现代发行版上，通常可以通过安装 `libopenr2-dev` 包和已打包的 Asterisk 22 构建来完全跳过这些步骤，因为 `chan_dahdi` 直接针对 libopenr2 编译 R2 支持，无需外部补丁。

步骤 1：安装所需的构建工具。

```
apt-get install git
```

步骤 2：克隆 openr2 库和 Asterisk 源码。Asterisk 22 不需要任何特殊的补丁树——只要存在 libopenr2，标准检出即可构建 R2 支持。

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

步骤 3：编译并安装 请在继续之前备份您的服务器。

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note: Do not execute “make samples” to avoid overwriting your configuration files.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

假设您有一块带有一个 E1 接口的卡。

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

步骤 5：运行命令 dahdi_cfg 以将更改应用到驱动程序：

```
dahdi_cfg -vvvvvvvv
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

步骤 5：更改文件 chan_dahdi.conf

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

步骤 6：更改文件 extensions.conf 中的拨号计划

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

注意：某些运营商不接受没有来电显示的呼叫。请将来电显示设置为运营商分配的 DID 号码之一。在某些国家，这一步不是必需的。步骤 7：测试解决方案：现在，在 from-internal 上下文中的分机，拨打任意号码并观察控制台。检查是否出现任何错误。-- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### 调试 OpenR2

要检测呼叫中的错误，可以激活调试。请按以下步骤操作。

1. 编辑文件 `chan_dahdi.conf` 并在配置中添加以下三行：

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. 重启 Asterisk 服务器
3. 测试呼叫并检查位于 `/var/log/asterisk/mfcr2/span1` 的呼叫文件

下面是一次正常呼叫的跟踪。将其与您在呼叫中收到的进行比较。

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

这些选项记录在文件 chan_dahdi.conf 中。这里详细说明了一些最重要的选项。必需的参数：mfcr2_variant、mfcr2_max_ani 和 mfcr2_max_dnis。mfcr2_variant：国家变体。

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

mfcr2_max_ani: 要求的最大 ANI 位数  
mfcr2_max_dnis: 要求的最大 DNIS 位数  
mfcr2_get_ani_first: 是否在 DNIS 之前获取 ANI（某些电信运营商要求）  
mfcr2_category: 呼叫者类别。可以在呼叫开始前设置变量 MFCR2_CATEGORY  
mfcr2_logdir: 用于记录通话文件的目录。（/var/log/asterisk/mfcr2/directory）  
mfcr2_call_files: 是否记录通话  

- mfcr2_logging: 日志记录选项  
- cas – 用于发送和接收的 ABCD 位  
- mf – 多频音调  
- stack – 通道和上下文栈的详细输出  
- all – 所有活动  
- nothing – 不记录任何内容  

mfcr2_mfback_timeout: 这个值值得一提。有时如果您拨打的是手机或任何需要较长时间才能完成的通话，此参数可能会超时，因此常常需要进行微调。如果某些通话未能完成，请首先修改此参数。  
mfcr2_metering_pulse_timeout: 脉冲用于某些 R2 变体以指示费用  
mfcr2_allow_collect_calls: 在巴西，使用 II-8 音调表示收费电话；此参数允许您阻止收费电话。  
mfcr2_double_answer: 也用于在需要双重应答时避免收费电话。将 double_answer=yes 实际上会阻止收费电话。  
mfcr2_immediate_accept: 允许跳过使用 B/II 组信号，直接进入已接受状态。  
mfcr2_forced_release: 允许加速通话释放；适用于巴西变体。  

#### ANI and DNIS

自动号码识别（ANI）是呼叫者的号码。拨号号码识别服务（DNIS）是被叫号码，换句话说，就是拨出的号码。当收到呼叫时，通常会将最后四位数字通过直接入线拨号（DID）传递给 PBX。ANI 实际上就是来电显示（Caller ID）。在拨号时，ANI 将包含呼叫者的分机号，而 DNIS 将包含呼叫目的地。正确配置这些参数非常重要。有些交换机只发送最后四位数字，而其他交换机则发送完整号码。  

### DAHDI channel format

DAHDI channels use the following format in the dial plan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

示例：

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## The IAX2 protocol

在本章中，我们将学习 Inter-Asterisk eXchange（IAX）协议，包括它的优势和劣势。还会涉及 trunk 模式以及两台 Asterisk 服务器的互连等细节。本文档中的所有引用均对应 IAX 版本 2。

IAX 协议提供语音和视频的媒体传输与信令。IAX 非常创新；在 trunk 模式下可节省带宽，并且在需要穿越 NAT 时比 SIP 简单得多。如今 IAX 的主要用途是互连 Asterisk 服务器。IAX 最初是为语音而创建的，但它也能容纳视频和其他多媒体流。

IAX 的灵感来源于其他 VoIP 协议，如 SIP 和 MGCP。它没有像传统做法那样使用两套独立的协议来处理信令和媒体，而是将二者统一为一种独特的协议。IAX 不使用 RTP 进行媒体传输；相反，它将媒体嵌入同一个 UDP 连接中。

**Status in Asterisk 22.** `chan_iax2`仍然包含在 Asterisk 22 LTS 中并得到完整支持，因此本节的内容仍然有效。IAX2 仍是一个遗留协议，新的部署相对较少：业界已基本统一使用 SIP（通过 `chan_pjsip` 在 Asterisk 22 中）来实现提供商 trunk 和服务器互连。IAX2 目前唯一剩余的主要优势是其单端口设计——所有信令和媒体都通过单个 UDP 端口（默认 4569）流动，这比 SIP 加上其独立的 RTP 流更易于防火墙和 NAT 配置。对于不涉及 NAT 的新建 Asterisk‑to‑Asterisk trunk，推荐使用 PJSIP trunk 这一现代方案；之所以在此仍讨论 IAX2，是因为它在只能打开单个 UDP 端口的防火墙环境下仍是有效选择。

### Objectives

本章结束时，你应该能够：

- 识别 IAX 协议的优势和劣势
- 描述 IAX 协议的使用场景
- 阐述 IAX trunk 模式的优势
- 为电话配置 iax.conf
- 为连接 VoIP 提供商配置 iax.conf
- 为 Asterisk 互连配置 iax.conf
- 理解 IAX 认证

### IAX design

IAX 设计的主要目标是：

- 减少媒体传输和信令所需的带宽
- 提供 NAT 透明性
- 能够传输 dialplan 信息
- 支持高效的广播和对讲

IAX 是一种点对点的信令和媒体协议，类似于 SIP，但不使用 RTP。其基本思路是将多媒体流复用到两台主机之间的单个 UDP 连接上。这种方式在穿越常见于 xDSL 调制解调器的 NAT 时尤为简洁。IAX 使用单一端口，默认 UDP 4569，并使用 15 位的呼叫号来复用所有流。IAX 协议的注册和认证过程类似于 SIP。协议的详细描述可参见 http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![The IAX protocol multiplexes many calls between two endpoints over a single UDP port (4569 by default), using a 15-bit call number to keep the streams apart — which makes NAT traversal simple.](../images/10-legacy-fig12.png)

### Bandwidth usage

VoIP 网络的带宽受多种因素影响；编解码器和协议头是最关键的。IAX 协议拥有一个令人惊讶的特性——trunk 模式，它通过单一头部复用多个呼叫。使用 Asterisk 带宽计算器，你会看到 IAX trunk 在多路呼叫情况下可节省高达 80% 的流量。

![Comparing IAX and SIP overhead: two SIP/RTP calls need two packets (40 bytes of payload carried under 156 bytes of overhead), while IAX2 trunk mode carries both calls in a single packet (40 bytes of payload under just 66 bytes of overhead) by sharing one IP/UDP header across many mini-frames.](../images/10-legacy-fig13.png)

### Channel naming

了解通道命名约定非常重要，因为在 dialplan 中指定通道时需要使用这些名称。用于出站通道

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — 远程对等方的 UserID，或在 iax.conf 中配置的客户端名称  
- `<secret>` — 密码。也可以是 RSA 密钥文件名（不含后缀 .key 或 .pub），并用方括号括起  
- `<peer>` — 要连接的服务器名称  
- `<portno>` — 连接的端口号  
- `<exten>` — 远程 Asterisk 服务器上的分机号  
- `<context>` — 远程 Asterisk 服务器中的 context  
- `<options>` — 唯一可用的选项是 ‘a’，表示 ‘request autoanswer’  

#### Outbound channels example:

Outbound channels are seen in the Asterisk console.

- `IAX2/8590:secret@myserver/8590@default` — 呼叫 myserver 中的 8590 分机。使用 8590:secret 作为名称/密码对  
- `IAX2/iaxphone` — 呼叫 “iaxphone”  
- `IAX2/judy:[judyrsa]@somewhere.com` — 使用 judy 作为用户名并使用 RSA 密钥进行身份验证，呼叫 somewhere.com  

#### The format of an incoming IAX channel is:

Inbound channels are seen in the Asterisk console.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — 如果已知的用户名  
- `<host>` — 正在连接的主机  
- `<callno>` — 本地呼叫号码  

Incoming channel example:

- `IAX2[flavio@8.8.30.34]/10` — 呼叫号码 10，来自 IP 地址 8.8.30.34，使用用户 flavio。  
- `IAX2[8.8.30.50]/11` — 呼叫号码 11，来自 IP 地址 8.8.30.50。  

### 使用 IAX

您可以通过多种方式使用 IAX。本节将展示如何为多种场景配置 IAX，包括：

- 使用 IAX 连接软电话  
- 使用 IAX 将 IAX 连接到 VoIP 提供商  
- 使用 IAX 连接两台服务器  
- 使用 IAX 在中继模式下连接两台服务器  
- 调试 IAX 连接  
- 使用 RSA 密钥对进行身份验证  

#### 使用 IAX 连接软电话

Asterisk 支持基于 IAX 的 IP 电话，例如 ATCOM 和 Digium 的旧 ATA（称为 IAXy），以及仍实现 IAX2 协议的软电话。软电话、ATA 和硬电话的配置过程类似。要配置 IAX 设备，需要编辑位于 /etc/asterisk 的 iax.conf 文件

```
directory.
```

我们将使用一个支持 IAX2 的软电话作为示例。

1. 使用以下方式备份原始 `iax.conf` 文件：

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. 开始编辑一个新的 `iax.conf` 文件：

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; 非常重要的参数，它会改变可用的编解码器

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

我已尽量保留示例文件中默认（未注释）的行。以下参数已被修改：

```
bandwidth=high
```

此行影响编解码器的选择。使用 high 设置可以选择高带宽和高质量的编解码器，例如由 ulaw 关键字定义的 g.711。如果保持默认参数，您将无法选择 ulaw。在这种情况下，Asterisk 将为下面的配置给出 “no codec available” 消息。

```
disallow=all
allow=ulaw
```

在上面描述的命令中，我们禁用了所有编解码器，只启用了 ulaw。在局域网中，大多数人倾向于使用 ulaw，因为它对处理器的负担较小，能够节省 CPU 周期。即使使用更多的带宽，这种编解码器仍然更受青睐，因为在局域网中通常拥有 100 兆位以太网甚至千兆网。使用 ulaw 的语音通话大约会占用网络 100 千比特每秒的带宽，这对于当今高速局域网来说是非常轻的负载。在广域网或互联网网络中，通常会禁用 ulaw，通过语音压缩来换取一些可用的 CPU 周期，以获得更好的带宽利用率。编解码器 gsm、g729 和 ilbc 也能提供良好的压缩比例。

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

在上述命令中，我们定义了一个名为 [2003] 的好友。上下文使用默认值（在前面的实验中我们始终使用默认上下文以避免混淆；当我们讲解 dial plan 时会完整解释此上下文）。行 “host=dynamic” 为电话的 IP 地址提供了动态注册。

3. 下载并安装支持 IAX2 的软电话。您可以选择任何仍然支持 IAX2 协议的软电话来完成本实验。  
4. 在客户端中配置 IAX 账户（通常为 *Add account* → IAX）。请注意，SipPulse Softphone 仅支持 SIP，无法通过 IAX2 注册，因此进行 IAX 测试时需要使用仍支持该协议的客户端。

5. 配置 `extensions.conf` 文件以测试您的 IAX 设备。

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

现在您可以在第 3 章创建的 SIP 电话和实验中创建的 IAX 电话之间进行拨号。

#### 使用 IAX 连接到 VoIP 提供商

一些 VoIP 提供商支持 IAX。通过搜索 “IAX providers” 您可以轻松找到 IAX 提供商。使用 IAX 很有意义，因为 IAX 可以节省大量带宽，轻松穿越 NAT，并且可以使用 RSA 密钥对进行身份验证。

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

在过去的几个 Asterisk 发行版中，支持 IAX 的商业 VoIP 提供商数量急剧下降；大多数提供商现在仅提供 SIP/PJSIP 中继。在决定使用 IAX 提供商之前，请确认他们仍在积极维护其 IAX 基础设施。对于新提供商的集成，推荐使用 PJSIP 中继（第 3 章）作为替代方案。

#### 使用 IAX 连接到提供商

步骤 1：在您喜欢的提供商处开设账户。您的提供商会提供三项信息。

- Name
- Secret
- IP address or Host name
- RSA public key

步骤 2：配置 iax.conf 文件，以在提供商处注册您的 Asterisk。将以下行添加到文件的 [general] 部分。

```
[general]
register=>name:secret@hostname/2003
```

在上述说明中，您使用账户和密码向提供商注册。您一旦收到来电，系统会将其转接到 2003 分机。

```
[name]
```

- ; 您的账户名称或号码

```
type=peer
secret=secret
; Your password
host=hostname
```

在上述说明中，我们已经创建了一个对应于提供商的对等体，用于拨号目的。

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

这对于 RSA 认证是必需的。使用来自提供商的公钥可以确保收到的呼叫确实来自真实的提供商。如果其他人尝试使用相同的路径，他们将无法进行认证，因为他们没有相应的私钥。步骤 4：尝试连接。要测试连接，拨打任意号码。有些供应商提供回声测试。为实现此目的，请编辑文件 extensions.conf。

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

转到 Asterisk CLI 并执行 reload。要验证 Asterisk 是否已向提供商注册，请使用下面的命令。

```
*CLI>reload
*CLI>iax2 show register
```

现在只需在连接到 Asterisk 服务器的软电话上拨打 *98。

#### 通过 IAX 中继连接两台 Asterisk 服务器

连接一台服务器到另一台非常容易。由于 IP 地址已经确定，无需进行注册。您需要在 iax.conf 文件中创建对等点和用户。总部站点的所有分机号以 20 开头，后跟两位数字（例如，2000）。在分支机构，所有分机号以 22 开头，后跟两位数字（例如，2200）。我们将使用中继。您需要一个 DAHDI 时钟源来启用此功能。步骤 1：编辑分支服务器上的 iax.conf 文件。

![Connecting two Asterisk servers with an IAX trunk: the HQ server (192.168.1.1, extensions 20xx) and the Branch server (192.168.1.2, extensions 22xx) reach each other over a single IAX trunk — no registration is needed because both IP addresses are fixed and known.](../images/10-legacy-fig15.png)

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

步骤 2：在 Branch 服务器上配置 extensions.conf 文件

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

步骤 3：在总部服务器上配置 iax.conf 文件

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

步骤 4：在 HQ 服务器上配置 extensions.conf 文件。

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

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

现在让我们从实际角度分析 IAX 认证过程，以帮助您为每个具体需求选择最佳方法。

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

当 Asterisk 接收到一个入站连接时，初始信息可能包含用户名（来自字段 `username=`）也可能不包含。入站连接同样带有 IP 地址，Asterisk 也会使用该地址进行认证。

如果提供了用户名，Asterisk：

1. 在 `iax.conf` 中搜索 `type=user`（或 `type=friend` 且节名与用户名匹配）的条目。如果未找到，Asterisk 拒绝连接。
2. 如果找到的条目包含 `deny/allow` 配置，Asterisk 会比较来电者的 IP 地址，以决定是否根据 `deny/allow` 子句接受呼叫。
3. 使用明文、md5 或 RSA 检查密码（secret）。
4. 接受连接并将呼叫发送到 `iax.conf` 文件中 `context=` 行指定的上下文。

如果未提供用户名，Asterisk：

1. 在 `iax.conf` 中搜索不带指定 secret 的 `type=user`（或 `type=friend`）条目，并检查 `deny/allow` 子句。如果找到条目，接受连接并使用节名作为用户名称。
2. 在 `iax.conf` 中搜索带有 secret 或 RSA 密钥的 `type=user`（或 `type=friend`）条目，并检查 `deny/allow` 子句。如果找到条目，尝试使用指定的 secret 对来电者进行认证；如果匹配，则接受连接。节名即为用户名称。

假设您的 `iax.conf` 文件包含以下条目：

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

如果呼叫指定了用户名，例如：

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk 将仅使用 iax.conf 文件中对应的条目尝试对呼叫进行身份验证。如果指定了其他任何名称，呼叫将被拒绝。如果未指定用户，Asterisk 将尝试将连接作为 guest 进行身份验证。然而，如果 guest 不存在，它将尝试使用任何其他具有匹配 secret 的连接。换句话说，如果您的 iax.conf 文件中没有 guest 部分，恶意用户可以通过不指定用户名来尝试猜测任何匹配的 secret。IP 地址的 deny/allow 限制同样适用。避免 secret 猜测的一个好方法是使用 RSA 身份验证。另一种方法是限制允许呼叫的 IP 地址。

#### IP address restrictions

访问通过 `permit` 和 `deny` 行进行控制：

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

规则按顺序解释，并且全部都会被评估（此概念不同于路由器和防火墙中常见的 ACL）。最后匹配的指令会覆盖之前的指令。

示例 #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

This will deny any packet from the 192.168.0.0/24 network.

Example #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

这将允许任何数据包，因为最后的指令覆盖了第一条。

#### 出站连接

出站连接使用以下方法获取认证信息：

- 由 `dial()` 应用程序传递的 IAX2 通道描述。
- `iax.conf` 文件中 `type=peer` 或 `type=friend` 的条目。
- 两种方法的组合。

#### 使用 RSA 密钥连接两个 Asterisk 服务器

可以使用非对称 RSA 密钥对 IAX 进行强认证。根据源代码（`res_krypto.c`），Asterisk 使用带有 SHA-1 算法的 RSA 密钥进行消息摘要，而不是较弱的 MD5。以下是使用 RSA 密钥设置两台服务器的分步指南。

##### 为分支配置服务器

步骤 1：在分支服务器上生成 RSA 密钥

```
astgenkey -n
```

当被询问时，使用密钥名称 branch。我们使用了参数 –n 来避免在 Asterisk 重新初始化时传递密码短语。如果您想提高安全性，请不要使用 –n，并使用 asterisk -i 启动 Asterisk。步骤 2：将密钥复制到目录 /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

Step 3: 将公钥复制到总部服务器

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Step 4：编辑 Branch 服务器上的 iax.conf 文件。

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

步骤 8：在 Branch 服务器上配置 extensions.conf 文件

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### 为总部配置服务器

步骤 1：在总部服务器上生成 RSA 密钥

```
astgenkey -n
```

当被要求时使用密钥名称 hq。步骤 2：将密钥复制到目录 /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

Step 3: 将公钥复制到 BRANCH 服务器

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

步骤 4：在总部服务器上配置 iax.conf 文件

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

步骤 10：在 HQ 服务器上配置 extensions.conf 文件。

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### IAX2 加密

IAX 支持使用对称密钥、128 位块密码 AES（Advanced Encryption Standard）进行通话加密。 在 IAX 中继之间激活加密非常简单。 在文件 iax.conf 中使用：

```
encryption=yes
```

强制加密：

```
forceencryption=yes
```

为了确保与旧版本的兼容性，您可能需要使用以下方式禁用密钥轮换：

```
keyrotate=no
```

### IAX2 调试命令

以下是一些最重要的 Asterisk 故障排除控制台命令。

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

查看此输出，确定通话的开始和结束。观察使用 poke 和 pong 包获取的延迟和抖动信息。这些包帮助生成 “iax2 show netstats” 命令的输出。

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

### Summary

本章回顾了 IAX 协议的优势与劣势。演示了 IAX 在多种场景中的工作方式，例如软电话以及两台 Asterisk 服务器之间的中继。中继模式通过在单个数据包中承载多个呼叫来节省带宽。最后，您学习了可用于检查状态和调试该协议的控制台命令。

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

步骤 2：在 sip.conf 上配置 [peer] 为所需的提供商创建一个 peer 类型的条目，以简化 Asterisk 的拨号。

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

步骤 3：在拨号计划中创建到提供商的路由  
我们将选择数字 010 作为到提供商的目标路由。  
要在提供商内部拨打 #610000，只需拨打 010610000。

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### 针对提供商场景的 SIP 选项

以下讨论检查在 sip.conf 文件中为连接到 VoIP 提供商设置的选项细节。

```
register=>username:password@hostname/4100
```

在 sip.conf 文件中注册的指令用于向提供商注册。register 事务使用 name 和 secret 进行认证。您可以使用斜杠（“/”）为呼入电话提供分机。技术上讲，分机会被放置在 SIP 请求的 “Contact” 头字段中。可以通过某些参数来控制注册行为：

```
registertimeout=20
registerattempts=10
```

要检查注册是否成功，旧的控制台命令是 `sip show registry`。在 Asterisk 22 中等效的命令是 `pjsip show registrations`（出站注册）和 `pjsip show endpoints`用于端点状态。

参数 “username” 用于认证摘要。摘要是使用 username、secret 和 realm 计算的：

```
username=username
```

Host 定义 VoIP 提供商的地址或名称：

```
host=hostname
```

参数 Fromuser 和 Fromdomain 有时在身份验证时是必需的。这些参数用于 SIP 的 From 头字段：

```
fromuser=username
fromdomain=hostname
```

当您连接到 VoIP 提供商时，需要提供凭证。在初始 INVITE 之后，提供商会发送一条称为 “407 Proxy Authentication Required” 的消息；您在后续的 INVITE 消息中提供凭证。对于来电，您的 Asterisk 服务器会向提供商请求凭证。显然，提供商并没有您 Asterisk 服务器的有效凭证。当您使用 insecure=invite 时，您告诉 Asterisk 不向提供商发送 “407 Proxy Authentication Required”，并接受来电。您也可以使用 insecure=port,invite，通过仅匹配 IP 地址而不匹配端口号来匹配对等方。

```
insecure=invite, port
```

### 使用 SIP (sip.conf) 连接两台 Asterisk 服务器

您可以使用 SIP 将两台 Asterisk 服务器互联。在进行此配置之前，务必注意拨号计划。用户通常希望以最小的工作量连接其他 PBX。这里的思路是仅使用一个分机号即可连接到另一台 PBX。步骤 1：编辑服务器 A 上的 sip.conf 文件：

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

步骤 2：编辑 server B 上的 sip.conf 文件：

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

![使用 SIP 连接两台 Asterisk 服务器：服务器 A（分机 4400/4401）和服务器 B（分机 4500/4501）交换 SIP 信令，使每个 PBX 的用户能够相互拨号](../images/07-sip-and-pjsip-fig08.png)

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

步骤 3：编辑 server A 上的 extensions.conf 文件:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Step 4: 编辑 server B 上的 extensions.conf 文件：

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk domain support (sip.conf)

SIP 协议遵循 Internet 架构。在配置 SIP 之前，首先要正确设置 DNS 服务器。在 SIP 环境中，您可以呼叫位于任何 SIP 代理的用户，其他用户也可以使用您的 SIP 统一资源标识符 (URI) 呼叫您。要为 SIP 设置 DNS 服务器，必须在 DNS 服务器上添加 SRV 记录。

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

在配置完 DNS 后，您可以使用指向 SIP 用户、SIP 电话或电话分机的 URI。SIP URI 看起来类似于电子邮件地址（例如，sip:chuck@yourpartnerdomain.com）。使用 SIP URI，无需电话号码即可从一个 SIP 电话拨打到另一个 SIP 电话。要拨打外部用户，只需使用如下所示的语句。

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Certain parameters can control domain behavior.

```
srvlookup=yes
```

此参数在外呼时启用 DNS SRV 查询。使用此参数，可以基于域名使用 SIP 名称拨打电话。

```
allowguest=yes
```

This parameter allows an external invite to be processed without authentication. It processes the call within the context defined in the general section or in the domain statement. Warning: If you define a context in the general section with access to PSTN, an external user can dial the PSTN over your PBX. In this case, you will incur any charges. Allow only your own extensions in the context defined in the general section.

![通过域连接到其他 SIP 服务器：youdomain.com 和 yourpartnerdomain.com 交换 SIP 信令，用户如 lee 和 bruce 可以使用 SIP URI 呼叫 chuck 和 norris](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

domain 命令允许您在 Asterisk 中处理多个域。如果呼叫来自特定域，它将被定向到特定的 context。

```
;autodomain=yes
```

此参数将在允许的域中包含本地 IP 和主机名。

```
;allowexternaldomains=no
```

默认值为 yes。取消注释该行可禁止呼叫外部域。

### SIP advanced configurations (sip.conf)

本节说明传统 SIP 通道的一些高级参数，如 presence、codec 选择、DTMF 选项和 QoS 包标记。**概念**（BLF/presence、codec 协商、DTMF 模式、DSCP 标记）在 PJSIP 中同样适用，但此处显示的 `sip.conf` 参数名在 Asterisk 22 中 **不存在**。在 PJSIP 上，DTMF 模式通过 `dtmf_mode=` 在 endpoint 上设置，codec 则使用 `allow=`/`disallow=` 设置。

#### SIP Presence

SIP presence 在 Asterisk 中部分实现。Asterisk 支持根据通道状态向用户发送 SUBSCRIBE 和 NOTIFY 请求。Asterisk 不支持 SIP 方法 PUBLISH。换句话说，你可以订阅通道的状态（busy、idle、ringing），但不能发布诸如 “away” 或 “do not disturb” 的信息。最常见的 presence 场景是 busy lamp field（BLF），即模拟 KS 系统为每个分机和中继提供灯光指示。SIP 参数用于 presence：

- allowsubscribe=yes: 允许 SIP 订阅方法
- subscribecontext=sip_subscribers: 查找 hints 的 context
- notifyring=yes: 在响铃时发送 SIP NOTIFY
- notifyhold=yes: 在保持时发送 SIP NOTIFY
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): 仅在对等端应用计数器
- callcounter=yes: 在设备上启用呼叫计数器
- busylevel=1: 将设备视为忙碌的呼叫数量阈值

例如：步骤 1：测试 SIP presence 并不困难。首先，配置文件 sip.conf 和 extensions.conf。

在文件 sip.conf

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

Step 2: 现在配置软电话以使用 presence。我们将演示如何配置 SipPulse Softphone。

- Sequence: right-click->SIP Account Settings->Properties->Presence
- Change the presence model from peer-to-peer to presence agent, which will make the softphone subscribe Asterisk for SIP events.

Step 3: 添加联系人到其他软电话。在本例中，SipPulse Softphone 的账号是 2000，所以我们将为账号 2001 添加联系人。Sequence: Open the right panel (presence panel in the softphone)->Click in Contacts->Add a contact. Fill the name 2001. Display as 2001 and don’t forget to check the box Show this contact’s availability.

Step 4: 现在呼叫分机 2001 并检查软电话右侧面板中电话的状态。使用控制台命令 `core show hints` 查看服务器上 presence 状态的变化（在 legacy chan_sip 中，`sip show inuse` 显示了每条线路上的通话数量）。在 Asterisk 22 上，使用 `pjsip show endpoints` 检查 endpoint 和 channel 状态。presence/BLF 状态出现在软电话的 contacts 或 BLF 面板中——具体显示方式取决于客户端。

#### Codec configuration

Codec configuration is simple and straightforward. You can set the words allow and disallow in the [general] section or peer/user section. The best practice is to standardize the codec to avoid transcoding, which is processor intensive. Please use the same codec for messages and prompts.

```
[general]
disallow=all
allow=g729
```

#### DTMF 选项

在某些情况下，您需要向诸如 voicemail 或交互式语音应答（IVR）之类的应用程序传递数字。正确传递 DTMF 非常重要。传递 DTMF 最简单的方法称为 inband。它在 sip.conf 文件的 [general] 或 peer/user 部分设置。当您将 dtmfmode=inband 设置时，DTMF 音调会作为音频通道中的声音生成。此方法的主要问题是，当使用如 g729 之类的编解码器压缩音频通道时，声音会失真，DTMF 音调无法被正确识别。如果您计划使用 dtmfmode=inband，请使用 g.711 编解码器（ulaw 和 alaw）。

```
dtmfmode=inband
```

另一种方法是使用 RFC2833，它允许您在 RTP 包中将 DTMF 音调作为命名事件传递。

```
dtmfmode=rfc2833
```

Finally, you can pass DTMF digits inside SIP packets, instead of RTP packets. This method is defined in the RFC3265 (signaling events) and RFC2976.

```
dtmfmode=info
```

在版本 1.2 发布之后，现在可以使用：

```
dtmfmode=auto
```

这尝试使用 RFC2833；如果不可行，则使用音带音调。

#### 服务质量 (QoS) 标记配置

QoS 是一组负责语音质量的技术。QoS 的实现方式是降低带宽、延迟和抖动。主要的 QoS 功能包括数据包调度、分片和报头压缩。QoS 在交换机和路由器中实现，而不是由 Asterisk 本身实现。然而，Asterisk 可以通过为数据包标记以实现快速传输，从而帮助路由器和交换机。标记使用在 RFC 2474 和 RFC2475 中定义的差分服务代码点 (DSCP)。

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

Starting from version 1.4, you can specify different codes for signaling (SIP), audio (RTP), and video (RTP).

### SIP authentication (sip.conf)

When legacy `chan_sip` received a SIP call, it followed the rules described in the following diagram. Three parameters played an important role in SIP authentication. On Asterisk 22, authentication is configured instead with PJSIP `auth` objects (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenced by an endpoint, and IP access control is done with `permit=`/`deny=` on the endpoint or via an `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

此参数控制是否可以让没有对应对等体的用户在没有名称和密钥的情况下进行身份验证。我们在域支持章节中讨论了此参数。

```
insecure=invite,port
```

当我们使用 `insecure=invite` 时，Asterisk 不会生成 “407 Proxy Authentication Required” 消息。没有此消息，用户即可在不进行身份验证的情况下发起呼叫。这通常用于连接 VoIP 服务提供商。来自 VoIP 服务提供商的呼叫通常不需要身份验证。

```
autocreatepeer=yes/no
```

此命令在 Asterisk 连接到 SIP 代理时使用。它会为每个呼叫动态创建一个 peer。启用此选项后，任何 UAC 都可以连接到 Asterisk 服务器。重要的是要限制对 SIP 代理的 IP 连接。SIP 代理随后负责访问控制。peer 配置基于通用选项以及 SIP 包的 “Contact” 头字段。警告：请极其谨慎地使用此功能，因为它会完全开放 Asterisk。

```
secret=secret, remotesecret=secret
```

此参数配置用于身份验证的 secret，针对入站请求使用 secret，针对出站请求使用 remotesecret。如果您不想在文本文件中显示 secret，可以使用 md5secret 来包含哈希而不是 secret。要生成 MD5 secret，您可以使用：

```
echo -n "username:realm:secret" |md5sum
```

然后使用以下语句：

```
md5secret=0b0e5d467890....
```

Warning: Do not forget to use the –n parameter; the carriage return will be used in the md5 computation.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

上述语句将拒绝所有 IP 地址，并仅允许来自本地网络 (192.168.1.0/24) 的 UAC。

#### RTP 选项

可以控制某些 RTP 参数。

```
rtptimeout=60
```

当通话未被保持且 RTP 活动超过 60 秒时，系统会终止该通话。

```
rtpholdtimeout=120
```

这会在没有 RTP 活动时终止通话，即使在保持状态下（应大于 rtptimeout）。

### SIP NAT 穿越 (sip.conf)

NAT *理论*（四种 NAT 类型、Contact 头部问题、保活以及强制媒体通过服务器）属于协议层内容，已在 *SIP & PJSIP in depth* 章节中说明。此处显示的 `sip.conf` 参数（`nat=`、`qualify=`、`directmedia=`、`externaddr=`、`localnet=`）是 **legacy chan_sip**，在 Asterisk 21+ 中已被移除。 在 PJSIP 中，这些对应于传输/端点设置，如传输上的 `rewrite_contact=yes`、`force_rport=yes`、`rtp_symmetric=yes`、`direct_media=no`、`external_media_address`、`external_signaling_address`、`local_net=`以及 AOR 上的 `qualify_frequency=`。

在 legacy chan_sip 中，参数 `nat` 有五个选项：

- nat = no — 除 RFC3581 外不进行特殊 NAT 处理
- nat = force_rport — 即使不存在 rport 参数也假装有该参数
- nat = comedia — 将媒体发送到 Asterisk 接收到的端口，而不管 SDP 中指示的发送位置
- nat = auto_force_rport — 如果 Asterisk 检测到 NAT，则设置 force_rport 选项（默认）
- nat = auto_comedia — 如果 Asterisk 检测到 NAT，则设置 comedia 选项

当您在 sip.conf 文件中写入 “nat=force_rport” 语句时，您告诉 Asterisk 忽略 SIP 头部中 “Contact” 字段所包含的地址，而使用数据包 IP 头部中的源 IP 地址和端口，并且将媒体返回到接收它的地址，忽略 SDP 头部的内容。

```
nat=force_rport,comedia
```

有必要保持 NAT 映射打开。如果 NAT 超时，Asterisk 无法向 UAC 发送邀请。UAC 能够发起呼叫，但无法接收任何呼叫。可以使用以下语句来保持 NAT 打开。

```
qualify=yes
```

Qualify 将定期使用 OPTIONS 方法发送 SIP 包，这有助于保持 NAT 端口打开。Qualify 每 60 秒发送一次 OPTIONS，并在主机不可达时每第 10 秒发送一次 OPTIONS。您可以使用 “sip show peers” 查看对等体的延迟。如果用户的 NAT 为对称型，则无法直接从一个 UAC 向另一个 UAC 发送数据包；在这种情况下，必须强制通过 Asterisk 传输 RTP，方法如下：

```
directmedia=no
```

#### Asterisk behind NAT (sip.conf)

所有前面的场景都假设 Asterisk 服务器拥有外部（有效）的 Internet 地址。有时 Asterisk 服务器部署在带有 NAT 的防火墙之后。在这种情况下，需要进行一些额外的配置。

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. 将防火墙配置为将 UDP 端口 5060 静态重定向到 Asterisk 服务器。
2. 将防火墙配置为将 UDP 端口 10000 到 20000 静态重定向。

如果想限制打开的端口数量，可以编辑 `rtp.conf` 文件来更改 RTP 端口范围。另一种方法是使用支持 SIP 协议的智能防火墙，动态打开 RTP 端口。

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

步骤 3：配置 Asterisk，使其在 SIP 包的头字段中包含外部地址，包括会话描述协议 (SDP)。您可以通过向 sip.conf 文件添加以下两条语句来实现此目的：

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

The first parameter externaddr tells Asterisk to include the external IP address inside the SIP headers for external destinations. The second parameter localnet allows Asterisk to differentiate between external and internal addresses. Optionally, you can use externhost if you use a Dynamic DNS with a DHCP address on the server.

### SIP dial strings (chan_sip)

The `SIP/...` dial-string technology shown below is the removed chan_sip driver. On Asterisk 22 use the `PJSIP/...` technology instead — for example `Dial(PJSIP/2000)` or `Dial(PJSIP/${EXTEN}@provider)`. The forms and meaning are otherwise analogous.

You can call a legacy SIP destination using different dial strings:

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

## 将遗留的 chan_sip 系统迁移到 PJSIP

因为 `chan_sip` 在 Asterisk 21 中已被移除，并且在 Asterisk 22 中彻底消失，任何现有的 `sip.conf` 部署都必须迁移到 PJSIP。最大的概念性转变在于，一个单一的 `sip.conf` `[peer]` 或 `[friend]` 被拆分为多个 PJSIP 对象，每个对象都有一个 `type=`：一个 **endpoint**（呼叫/编解码器/媒体设置），一个或多个 **aor** 对象（设备可达/注册位置），一个 **auth** 对象（凭证），以及一个共享的 **transport**（监听套接字、NAT 地址）。下表映射了最常见的概念。

| Legacy sip.conf concept | PJSIP equivalent (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (referenced via `auth=` and `aors=`) |
| `type=friend` / `type=peer` / `type=user` | a single `type=endpoint` (PJSIP has no friend/peer/user distinction) |
| `host=dynamic` (device registers) | `type=aor` with `max_contacts=1`; the device REGISTERs to update its contact |
| `host=<ip/hostname>` (static) | `type=aor` with a static `contact=sip:host:port` |
| `register=>user:secret@host/ext` (outbound) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` on the endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` on the endpoint (same syntax) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — also `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` on the endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (seconds) on the **aor** |
| `externaddr=` | `external_media_address=` and `external_signaling_address=` on the **transport** |
| `localnet=` | `local_net=` on the **transport** |
| `insecure=invite` (provider, no auth) | omit `auth=`/`outbound_auth=` and use `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (use with care) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (and `cos_audio` / `cos_video`) on the endpoint |

一个在遗留 `sip.conf` 中看起来像这样的注册扩展：

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

在 Asterisk 22 中，它变为以下`pjsip.conf`：

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

Asterisk 附带一个辅助脚本 **`sip_to_pjsip.py`**，它读取现有的 `sip.conf` 并生成一个 `pjsip.conf`。您可以直接在 /etc/asterisk 目录中运行它。该实用程序位于 Asterisk 源代码树的 `contrib/scripts/sip_to_pjsip/` 下，其中 `${PATH_TO_ASTERISK_SOURCE}` 是 Asterisk 源文件所在的路径（通常是 /usr/src/asterisk-22.x.y/）：

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

如果使用`--help`选项运行它，您将看到它的选项：

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

它也接受可选的位置参数 — `[input-file [output-file]]`,
默认在当前目录下为 `sip.conf` 和 `pjsip.conf`。

将其输出视为**起点**：审查每个生成的对象，尤其是传输、NAT 设置和编解码器列表，并在投入生产前进行彻底测试。

让我们在 VoIP School Blackbelt (voip.school) 的配套实验中迁移 sip.conf

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
register=>1020:supersecret@sip.flagonc.com:5600/9999
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
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
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
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
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
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
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
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

虽然转换看起来还可以，但我们可以看到某些元素如 qualify=yes 不能直接映射。要解决此问题，必须在 aor 部分添加命令 qualify_frequency=time（单位为秒）。示例如下。

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

完整的 PJSIP 配置已在 *SIP & PJSIP in depth* 章节中介绍，官方文档位于 docs.asterisk.org，全面覆盖该通道。在我们的配套实验 voip.school 中，实验 5 让您练习刚刚学到的内容。

## Summary

本章汇总了早于当今纯 VoIP 部署的通道技术，但这些技术仍被 Asterisk 22 支持。你已经了解了 **模拟** 线路和电话如何通过 DAHDI 上的 **FXO/FXS** 接口连接，**数字 TDM** 链路（E1/T1 和 ISDN PRI/BRI）如何配置，以及 **IAX2**（`chan_iax2`）仍然作为一种高效、对 NAT 友好的服务器间中继使用，尽管它现在已经是彻底的遗留技术。你还重新审视了已废弃的 **`chan_sip`** 驱动及其 `sip.conf` 语法——在旧系统中仍会遇到，但在 Asterisk 22 中已不复存在——并通过概念映射表和 `sip_to_pjsip.py` 脚本完成了将此类系统迁移到 PJSIP 的过程。经验法则是：只有在真实硬件或现有遗留系统迫使你这样做时才使用本章中的内容；所有全新部署均应使用基于 IP 的 PJSIP。

## Quiz

1. 关于两个模拟 Foreign eXchange 接口，标记正确的陈述（可多选）：
   - A. FXO 接口连接到公共交换电话网（PSTN）中心局，并从中获取拨号音。
   - B. FXS 接口向标准模拟电话、传真或调制解调器提供拨号音和振铃电源。
   - C. FXS 接口是将 Asterisk 连接到电信线路的正确方式。
   - D. FXO 接口也可以连接到传统 PBX 的分机端口。
2. 模拟线路的监督信令包括以下哪些（可多选）？
   - A. 挂机
   - B. 摘机
   - C. 振铃
   - D. DTMF
3. DAHDI 模拟卡上的回声、噼啪声和噪声最常见的原因是：
   - A. Asterisk 的编译方式
   - B. PCI 中断冲突
   - C. 不正确的 SIP 编解码器
   - D. 缺失的拨号计划
4. 为了在模拟通道上实现精确计费，必须准确检测对端何时接听。您需要在 Asterisk 上激活（并向电信运营商请求）哪项功能？
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial-tone generation
5. DAHDI 硬件独立于 Asterisk：物理卡在 `/etc/dahdi/system.conf` 中配置，而 `chan_dahdi.conf` 定义 Asterisk 通道，而不是硬件本身。
   - A. 正确
   - B. 错误
6. 关于数字中继容量和信令，标记正确的陈述（可多选）：
   - A. E1 中继携带 30 条语音通道，T1 中继携带 24 条。
   - B. ISDN PRI 在 E1 上使用 30B+D，在 T1 上使用 23B+D。
   - C. ISDN 是 CCS 信令的例子，而 MFC/R2 是 CAS 信令的例子。
   - D. T1 是欧洲和拉丁美洲最常用的数字中继。
7. 哪个实用工具会自动检测 DAHDI 卡并生成 `/etc/dahdi/system.conf` 和 `dahdi-channels.conf`？
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. 将传统 `sip.conf` `[friend]` 迁移到 PJSIP 时，需要将单个块拆分为多个对象。哪组 PJSIP `type=` 对象通常取代一个注册 `[friend]`？
   - A. `type=endpoint`、`type=aor`和`type=auth`
   - B. `type=peer`和`type=user`
   - C. 仅 `type=sip`
   - D. `type=channel`和`type=device`
9. 在两台 Asterisk 服务器之间使用 IAX2 中继模式的主要实际优势是什么？
   - A. 默认使用 TLS 加密每个通话
   - B. 在单个报头下承载多个通话，节省带宽
   - C. 消除对任何编解码器的需求
   - D. 为每个通话分配单独的 UDP 端口以获得更好质量
10. RSA 密钥可用于 IAX2 认证。哪把密钥必须保密，哪把密钥需要提供给对方服务器？
    - A. 保密公钥；共享私钥
    - B. 保密私钥；共享公钥
    - C. 保密共享密钥；共享私钥
    - D. 两把密钥都必须共享

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
