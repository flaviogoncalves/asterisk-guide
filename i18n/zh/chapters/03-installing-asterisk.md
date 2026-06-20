# Installing Asterisk 22

在第一章中，我们简要了解了 Asterisk 在电话环境中的用途。本章将介绍如何下载和安装 Asterisk。开始之前，必须学习如何编译和安装它。对于传统的 Microsoft™ Windows™ 用户来说，编译过程可能显得奇怪，但在 Linux™ 环境中相当常见。编译 Asterisk 时可以为你的硬件生成优化的代码，这正是我们将在此进行的操作。Asterisk 可以运行在多种操作系统上，但我们将保持简单，只使用一种：Linux。我们选择 **Ubuntu 24.04 LTS**，因为它的依赖项易于安装，并且是一款稳定、得到良好支持且占用资源少的服务器发行版。如果你更喜欢其他发行版，请相应地调整软件包名称。

本版针对 **Asterisk 22 LTS**（发布于 2024-10-16；完整支持至 2028-10-16，安全修复至 2029-10-16）。Asterisk 22 是当前的长期支持版本。需要注意的是，Digium 于 2018 年被 **Sangoma** 收购，Asterisk 现由 Sangoma 赞助——本章中出现的 “Digium” 皆指其历史品牌及硬件。

## 目标

- 确定 Asterisk 的硬件需求；
- 在 Linux 上安装所需的依赖；
- 通过 HTTPS 下载稳定版本；
- 编译 Asterisk；并
- 了解如何在启动时启动 Asterisk。

## Minimum Hardware Required

Asterisk 并不需要大量硬件即可运行，但在选择最适合您需求的硬件时有一些建议。选择硬件时应考虑以下主要因素：

- 注册用户的总数。确定您需要支持的每秒注册次数
- 同时通话的总数。确定您需要在网络适配器和 Asterisk 服务器上处理的网络会话数量
- 需要支持的编解码器。高复杂度编解码器会在服务器上消耗大量 CPU/FPU 资源；例如，iLBC 的创建者（Global IP Sound）测得其在 TI C54x DSP 上每通道 30 ms 帧约需 18 MIPS（20 ms 帧约需 15 MIPS）
- 回声消除。回声消除可能会占用大量 CPU/FPU，在某些情况下您应使用电话接口卡中的 DSP 进行硬件回声消除
- 可用性。使用 RAID1 或 RAID5 提高可用性。请记住，Asterisk 是 24x7 应用。

Asterisk 服务器的主要组件是网络适配器。建议使用优质的服务器网络适配器。CPU 在需要支持高复杂度编解码器（如 g.729、iLBC）和回声消除时尤为重要。您可以选择将这些任务交给专用 DSP：Sangoma（前 Digium）提供的 DSP 卡 TC400B 能够支持 120 条 g.729 同时通话。

最佳实践是从知名厂商处选购全新、服务器级别的计算机。要准确了解特定机器能够支持多少同时通话或多少注册用户，您应使用压力测试工具（如 SIPP（http://sipp.sourceforge.net））对硬件进行测试。一些硬件厂商（如 Xorcom（http://www.xorcom.com））会在其网站上公布测试结果。

> **注意**：某些 Asterisk 应用（如 ConfBridge 和 hold music）需要内部计时源。在现代 Linux 上，这由内置的`res_timing_timerfd`模块自动提供——无需电话硬件。（旧的`dahdi_dummy`软件计时器已不再存在；其功能已合并到 DAHDI Linux 2.3.0 中的主`dahdi`内核模块。）您可以使用 CLI 命令`timing test`确认活动计时器。

### Hardware configuration

Asterisk 硬件不需要太复杂。您不需要昂贵的显卡或大量外设。以下是硬件配置的一些建议：

- 禁用未使用的 USB、串口和并口，以避免不必要的中断消耗。
- 可靠的网络接口卡是必不可少的。
- 如果使用电话接口卡，请格外注意。有些卡使用 3.3 V PCI 总线，相关主板不易寻找。如今，PCI Express 更为常见。
- 密切关注硬盘，PBX 需要在 24x7 环境下运行，而桌面电脑通常是 8x5。不要使用桌面硬件作为 PBX，硬盘往往在第一年内就会失效。建议使用服务器机器或专为 24x7 应用设计的设备。

### IRQ sharing (legacy PCI cards only)

此问题仅在您安装物理 PCI/PCI‑Express 电话卡（DAHDI 硬件）时**才**需要考虑。这类卡会产生大量中断，在旧的单 CPU 系统上，与其他设备共享 IRQ 线可能导致驱动程序被饿死，从而降低语音质量。如果使用电话卡，请将机器专用于 Asterisk，在 BIOS 中禁用所有未使用的板载设备，并使用`cat /proc/interrupts`检查分配的中断。现代多核服务器使用 MSI/MSI‑X 中断，使 IRQ 共享在实践中不再是问题，而纯 VoIP 部署（无卡）则根本无需担心此事。

## 选择 Linux 发行版

Asterisk 最初是为 Linux 开发的。不过，它也可以在 BSD Unix 或 macOS 上运行。如果你是 Asterisk 新手，建议先使用 Linux，因为它更容易上手。Asterisk 官方支持的目标平台包括 RHEL 系列（CentOS/RHEL/Fedora）、Ubuntu 和 Debian。如今的实用选择有 **Debian 12**、**Ubuntu 22.04 LTS / 24.04 LTS**，以及 **Rocky Linux 9 / AlmaLinux 9** ——CentOS Linux 已经停止维护，因此在 RHEL 系列系统上更倾向于使用 Rocky 或 AlmaLinux。本书使用 Ubuntu 24.04 LTS。请从下面的官方发布目录下载最新的 24.04 点发行版服务器镜像（完整文件名包含当前的点发行版，例如 `ubuntu-24.04.4-live-server-amd64.iso`）：

```
https://releases.ubuntu.com/24.04/
```

### 为 Asterisk 准备 Linux

在编译 Asterisk 之前，你需要一套已安装构建软件包的可用 Linux 系统。请在虚拟机或专用机器上安装 **Ubuntu 24.04 LTS Server**（使用 64 位镜像；本书所有内容均为 64 位，尽管 Asterisk 本身仍支持 32 位 x86）。我们在本次培训中使用 VirtualBox；你可以从 <https://releases.ubuntu.com/24.04> 下载镜像。Linux 的安装超出本书范围 —— 需要具备基本的 Linux 知识。Linux 安装完成后，你将添加 Asterisk 的构建依赖（见下文 *Installing dependencies*），随后编译 Asterisk。

## 安装用于 Asterisk 的 Linux

像往常一样安装 Linux，且不需要图形桌面。在安装过程中，还要启用邮件传输代理（我们使用 **exim4**）——Asterisk 稍后在本书中会需要它来发送语音信箱到电子邮件的通知。**注意：** 安装操作系统会擦除目标磁盘。如果在实体硬件上安装，请先备份数据；在虚拟机中安装则不会影响宿主机。使用 Ubuntu Server ISO（或虚拟机的虚拟光驱）启动安装程序并按照提示进行操作——大多数步骤都很直接。

## Installing dependencies

要安装 Asterisk 和 DAHDI，您必须安装许多软件依赖项。 在 Asterisk 22 中，推荐的做法是使用随源码树一起提供的脚本，它能够识别每个受支持发行版的正确软件包名称。 下载并解压 Asterisk 源码（参见下文 “Compiling Asterisk”）后，运行：

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. 以 root 身份登录（或使用 `sudo`）。
2. 如果您想在 Debian/Ubuntu 系统上手动安装依赖项，对应的软件包列表如下：

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

请注意，Asterisk 源码现已托管在 Git 上，因而 `subversion` 已不再需要，现代的 Debian/Ubuntu 提供 `libncurses-dev` 而不是带版本号的 `libncurses5-dev`。 建议使用 `./contrib/scripts/install_prereq install` 而不是手动维护的列表，因为该脚本始终会跟踪您发行版的正确软件包名称。

### DAHDI

DAHDI（Digium/Sangoma Asterisk Hardware Device Interface）是模拟和数字卡的驱动架构。 在安装 Asterisk 之前，如果您计划使用模拟或数字接口，务必先安装 DAHDI。 DAHDI 仍然用于模拟/数字电话卡，但其使用场景日益小众——大多数现代部署都是纯 VoIP，可以完全跳过本节。 仅在拥有物理电话接口硬件时才安装 DAHDI。 使用以下方式获取源码文件：

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

使用以下方式解压文件：

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

您需要编译 DAHDI 模块。 多年前引入的 ./configure 和 make menuselect 命令用于此目的。 后者可以让您选择要构建的实用程序和模块。 以下命令将完成此操作：

```
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version downloaded
make
make install
cd ../tools
autoreconf -i
./configure
make
make install
```

make install-config DAHDI 已配置完成。 如果您有任何 DAHDI 硬件，建议现在编辑 /etc/dahdi/modules，仅加载系统中实际安装的 DAHDI 硬件支持。 默认情况下，DAHDI 启动时会加载所有硬件支持。 我认为您系统上的 DAHDI 硬件是：usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware。 上图（如上）要求您修改文件 /etc/dahdi/modules，只加载特定配置所需的驱动并显示检测到的硬件。 编辑文件 /etc/dahdi/modules，仅加载所需硬件。 以我为例，我使用的是一台配有 Xorcom Astribank 6FXS 和 2FXO 的测试机器。 文件如下所示。

```
# Contains the list of modules to be loaded / unloaded by /etc/init.d/dahdi.
#
# NOTE:  Please add/edit /etc/modprobe.d/dahdi or /etc/modprobe.conf if you
#        would like to add any module parameters.
#
# Format of this file: list of modules, each in its own line.
# Anything after a '#' is ignore, likewise trailing and leading
# whitespaces and empty lines.
# Digium TE205P/TE207P/TE210P/TE212P: PCI dual-port T1/E1/J1
# Digium TE405P/TE407P/TE410P/TE412P: PCI quad-port T1/E1/J1
# Digium TE220: PCI-Express dual-port T1/E1/J1
# Digium TE420: PCI-Express quad-port T1/E1/J1
#wct4xxp
# Digium TE120P: PCI single-port T1/E1/J1
# Digium TE121: PCI-Express single-port T1/E1/J1
# Digium TE122: PCI single-port T1/E1/J1
#wcte12xp
# Digium T100P: PCI single-port T1
# Digium E100P: PCI single-port E1
#wct1xxp
# Digium TE110P: PCI single-port T1/E1/J1
#wcte11xp
# Digium TDM2400P/AEX2400: up to 24 analog ports
# Digium TDM800P/AEX800: up to 8 analog ports
# Digium TDM410P/AEX410: up to 4 analog ports
#wctdm24xxp
# X100P - Single port FXO interface
# X101P - Single port FXO interface
#wcfxo
# Digium TDM400P: up to 4 analog ports
#wctdm
# Xorcom Astribank Devices
xpp_usb
```

重新启动计算机并验证驱动程序是否正确加载。

## 哪个版本值得选择

一般来说，你应该使用具备所需功能的版本。Asterisk 采用交替的 LTS（长期支持）和标准发布模式。在本版出版时，**Asterisk 22 是当前的 LTS 发行版**（2024 年 10 月发布；最新的点版本是 22.10.0），因此它是目前最好的选择。Asterisk 20 是之前的 LTS，而版本 16（在第一版中使用）已进入生命周期结束。对于生产系统，始终选择 LTS 发行版。

## 编译 Asterisk

如果您之前已经编译过软件，编译 Asterisk 将是一件轻松的事。运行以下命令来编译并安装 Asterisk。请记住，您可以使用 make menuselect 选择要构建的应用程序和模块。步骤 1：下载源代码

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

步骤 2：安装构建所需的前置条件（参见上文“安装依赖项”）

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

步骤 3：配置构建

```
./configure
```

步骤 4：选择要构建的模块

```
make menuselect
```

使用 make menuselect 只安装必要的模块。在 Asterisk 22 中，SIP 通道是 **chan_pjsip**（默认构建）；旧的 **chan_sip** 已在 Asterisk 21 中移除，不再存在。Opus *pass-through* 开箱即用（树内的 `res_format_attr_opus` 模块处理 SDP 协商），但 **codec_opus** 转码模块仍是来自 Sangoma/Digium 的外部闭源二进制文件——在 menuselect 中选择它会从 Digium 的服务器下载该二进制文件。该二进制文件免费提供。有关详细信息，请参见下文的“使用 menuselect 选择模块”。

步骤 5：构建并安装 Asterisk，然后创建默认配置和示例文件

```
make
make install
make samples
make config
ldconfig
```

`make install` 安装二进制文件和模块，`make samples` 将示例配置文件写入 `/etc/asterisk`、`make config` 为您检测到的发行版安装 SysV init 启动脚本（例如 Debian/Ubuntu 上的 `/etc/init.d/asterisk`），并且 `ldconfig` 刷新共享库缓存。源代码树中还提供了一个 systemd 单元，位于 `contrib/systemd/asterisk.service`，但 `make config` 并不会自动安装它——如果您希望在 systemd 下运行 Asterisk，请自行复制到相应位置（见下文）。

### 使用 menuselect 选择模块

`make menuselect` 打开一个基于文本的菜单，您可以在其中精确选择要构建的应用程序、编解码器、通道和资源。以下是针对 Asterisk 22 的一些说明：

- **chan_pjsip**（在 *Channel Drivers* 下）是现代 SIP 通道，默认启用；它是 Asterisk 22 中唯一的 SIP 通道。
- **codec_opus**（在 *Codec Translators* 下）是一个 **外部** 模块（其 menuselect 条目显示为 “Download the Opus codec from Digium”）；启用它会让 `make` 从 Sangoma/Digium 获取免费、闭源的二进制文件。Opus pass-through 本身不需要额外模块。Sangoma 的 **codec_g729** 模块也可用——二进制文件可免费下载，但合法的 G.729 转码需要购买每通道许可证。
- 在 *Core Sound Packages*、*Music On Hold File Packages* 和 *Extras Sound Packages* 菜单中选择您需要的声音格式和语言；您在此处勾选的任何内容都会在 `make install` 期间自动下载并安装。

完成选择后，选择 **Save & Exit** 并继续执行 `make`。

## 启动和停止 Asterisk

使用此最小配置，即可成功启动 Asterisk。为了学习和调试，您可以在前台并附加到控制台的方式启动 Asterisk：

```
/usr/sbin/asterisk -vvvgc
```

使用 CLI 命令 `core stop now` 关闭 Asterisk：

```
*CLI> core stop now
```

### 使用 systemd 启动 Asterisk

在现代 Linux 发行版（Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9）中，系统服务管理器是 **systemd**。Asterisk 在源码树的 `contrib/systemd/asterisk.service` 处提供了一个 systemd 单元文件；将其复制到 `/etc/systemd/system/asterisk.service` 并运行 `systemctl daemon-reload`。安装完成后，生产环境中推荐通过 `systemctl` 运行 Asterisk：

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Asterisk 作为服务运行后，可使用 `asterisk -r`（连接）或 `asterisk -rvvv`（带详细输出的连接）附加到其 CLI。

在较旧的系统中，Asterisk 通过传统的 SysV init 脚本（`/etc/init.d/asterisk`）和 **safe_asterisk** 包装器启动，后者在 Asterisk 崩溃时会自动重启。使用 systemd 时，自动重启由单元文件的 `Restart=` 指令处理，因此 `safe_asterisk` 通常不再需要。传统的 init/`safe_asterisk` 方法仍可使用，但在基于 systemd 的发行版上已被弃用。

### Asterisk 运行时选项

Asterisk 的启动过程非常简单。如果不带任何参数运行 Asterisk，它将以守护进程方式启动。

```
/sbin/asterisk
```

您可以通过执行以下命令访问 Asterisk 控制台。请注意，可以同时运行多个控制台进程。

```
/sbin/asterisk -r
```

### Asterisk 可用的运行时选项

您可以使用 `asterisk -h` 显示可用的运行时选项

```text
sipast:/usr/src/asterisk-22.x.y# asterisk -h
Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others.
Usage: asterisk [OPTIONS]
Valid Options:
   -V              Display version number and exit
   -C <configfile> Use an alternate configuration file
   -G <group>      Run as a group other than the caller
   -U <user>       Run as a user other than the caller
   -c              Provide console CLI
   -d              Increase debugging (multiple d's = more debugging)
   -f              Do not fork
   -F              Always fork
   -g              Dump core in case of a crash
   -h              This help screen
   -i              Initialize crypto keys at startup
   -L <load>       Limit the maximum load average before rejecting new calls
   -M <value>      Limit the maximum number of calls to the specified value
   -m              Mute debugging and console output on the console
   -n              Disable console colorization. Can be used only at startup.
   -p              Run as pseudo-realtime thread
   -q              Quiet mode (suppress output)
   -r              Connect to Asterisk on this machine
   -R              Same as -r, except attempt to reconnect if disconnected
   -s <socket>     Connect to Asterisk via socket <socket> (only valid with -r)
   -t              Record soundfiles in /var/tmp and move them where they
                   belong after they are done
   -T              Display the time in [Mmm dd hh:mm:ss] format for each line
                   of output to the CLI. Cannot be used with remote console mode.
   -v              Increase verbosity (multiple v's = more verbose)
   -x <cmd>        Execute command <cmd> (implies -r)
   -X              Enable use of #exec in asterisk.conf
   -W              Adjust terminal colors to compensate for a light background
```

## 安装目录

Asterisk 安装在多个目录中，这些目录可以在 asterisk.conf 文件中进行修改。出于培训目的，我会把 verbose 从 3 改为 15，生产环境则保持为 3。选项 `maxcalls` 和 `maxload` 是防止系统过载的良好设置。

### asterisk.conf（摘录）

`[directories]` 部分定义了 Asterisk 保存其配置、模块、数据、spool 和日志的位置：

```
[directories](!) ; remove the (!) to enable this
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk
astsbindir => /usr/sbin
```

`[options]` 部分保存运行时调优。下面显示了最常用的选项（取消注释即可启用）；该文件还包含许多其他选项，每个选项都有内联注释进行说明：

```
[options]
;verbose = 3      ; Console verbosity (raise to 15 for training, keep 3 in production)
;debug = 3        ; Debug level
;maxcalls = 10    ; Maximum number of simultaneous calls allowed
;maxload = 0.9    ; Stop accepting new calls when load average exceeds this
;maxfiles = 1000  ; Maximum number of open files
;runuser = asterisk   ; The user to run as
;rungroup = asterisk  ; The group to run as
```

## 日志文件和日志轮转

Asterisk PBX 将其消息记录在 `/var/log/asterisk` 中。日志记录由 `logger.conf` 控制。关键部分是 `[logfiles]` 部分，其中每行定义一个日志通道及其捕获的消息级别（摘录）：

```ini
; logger.conf (excerpt)
[general]
;dateformat = %F %T.%3q          ; ISO 8601 timestamps, with milliseconds

[logfiles]
; <logger_name> => [formatter]<levels>
console  => notice,warning,error
messages => notice,warning,error
full     => notice,warning,error,verbose,dtmf,fax
security => security              ; PJSIP/auth security events (used by Fail2Ban)
```

编辑后，使用 `logger reload` 应用更改，并通过 `logger show channels` 确认通道：

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

日志文件可能会快速增长，因此使用系统 `logrotate` 守护进程进行轮转——在 `/etc/logrotate.d/` 下添加一个文件：

```text
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
       /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

可以使用以下方式获取有关 logrotate 的更多信息：

```
#man logrotate
```

## 卸载 Asterisk

要卸载 Asterisk，请使用：

```
make uninstall
```

要卸载 Asterisk 及所有配置文件，请使用：

```
make uninstall-all
```

## Asterisk 安装说明

本节将提供在安装 Asterisk 之前需要注意的一些问题的建议。

### 生产系统

如果在生产环境中安装 Asterisk，您应当关注系统设计。服务器必须进行优化，使得电话系统相对于其他系统进程拥有更高的优先级。Asterisk 不应与占用大量处理器资源的软件（如 X-Windows）共同运行。如果需要运行 CPU 密集型进程（例如大型数据库），请使用独立的服务器。一般而言，Asterisk 对硬件性能波动比较敏感。因此，尽量在 CPU 利用率不超过 40% 的硬件环境中运行 Asterisk。

### 网络技巧

如果计划使用 IP 电话，必须关注您的网络。语音协议对延迟甚至抖动具有很好的容忍度；然而，如果使用配置不当的局域网，语音质量将受到影响。只有在交换机和路由器上使用服务质量（QoS）才能保证良好的语音质量。局域网内的语音通常表现良好，但即使在 LAN 环境中，如果使用 10 Mbps 集线器且冲突过多，也会导致语音失真或质量差。请遵循以下建议，以确保尽可能最佳的语音质量：

- 如有可能或经济可行，使用端到端 QoS。采用端到端 QoS 时，语音质量完美。没有借口！
- 在生产环境中避免使用 10/100 Mbps 集线器进行语音传输。冲突会在网络上产生抖动。推荐使用全双工 10/100 Mbps，因为不会产生冲突。
- 使用 VLAN 将语音网络的不必要广播隔离开来。您不希望病毒通过 ARP 广播破坏语音网络。
- 教育用户对语音网络的期望。没有 QoS 时，不要声称语音会像大多数情况下那样完美。通常只能达到类似手机的语音质量。使用质量可靠的电话，因为固件和硬件设计问题很常见。

## 概要

在本章中，您已经了解了最低硬件需求以及如何下载、安装和编译 Asterisk。出于安全考虑，Asterisk 应以非 root 用户运行。在启动生产环境之前，您应检查网络环境。

## Quiz

1. 在 Asterisk 22 中，哪个通道驱动提供 SIP 支持，旧的 `chan_sip` 怎么了？
   - A. `chan_sip`仍然是默认的；`chan_pjsip`是可选的。
   - B. `chan_pjsip`是默认的 SIP 通道；`chan_sip`在 Asterisk 21 中被移除，已不再存在。
   - C. 两者默认都会构建，运行时可自行选择。
   - D. SIP 支持被完全移除，改用 IAX2。
2. Asterisk 的电话接口卡通常内置数字信号处理器（DSP），因此不需要 PC 提供太多 CPU。
   - A. 正确
   - B. 错误
3. 如果想要完美的语音质量，需要实现端到端的服务质量（QoS）。
   - A. 正确
   - B. 错误
4. 你应该始终选择最新的 Asterisk 版本，因为它是最稳定的。
   - A. 正确
   - B. 错误
5. 安装 Asterisk 22 的构建依赖的推荐方法是什么？
6. 如果没有 TDM 接口卡，你仍然会有一个由 Linux 上的 `res_timing_timerfd`模块提供的内部计时源用于同步。该计时被诸如 ________ 和 ________ 等应用使用。
7. 安装 Asterisk 时最好不要安装 GNOME 或 KDE 等桌面环境，因为图形界面会消耗 CPU 周期。
   - A. 正确
   - B. 错误
8. Asterisk 配置文件位于 ________ 目录。
9. 要安装 Asterisk 示例配置文件，输入命令： ________
10. 为什么以非 root 用户运行 Asterisk 很重要？

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
