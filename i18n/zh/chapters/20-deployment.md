# 部署、监控与扩展

让 Asterisk 在实验室环境中接通电话是一回事；而将其作为一项能够抵御崩溃、重启、升级和攻击，并且能够被观测、备份和扩展的服务来运行，则是另一回事。本章将探讨 dialplan 正常工作*之后*发生的一切。我们首先介绍保持 Asterisk 运行的守护进程（systemd），接着介绍如何将其打包进容器（使用本书自带的 Docker 实验室作为示例），然后涵盖配置管理与备份、监控与可观测性，最后介绍当单台服务器不足以支撑时所采用的模式：高可用性与扩展，以及在云端托管的现实情况。

文中展示的所有内容均已在本书的 Asterisk 22 实验室环境`lab/`中进行了验证——这与您在全书学习过程中构建的容器完全一致。

## 目标

读完本章，您应该能够：

- 在 systemd 下以非 root 用户身份可靠地运行 Asterisk 22，并实现自动重启
- 使用 Docker 容器化 Asterisk 并理解网络方面的权衡
- 将`/etc/asterisk`纳入版本控制并备份正确的状态
- 通过 CLI、CDR/CEL、AMI/ARI 和指标监控运行中的系统
- 应用主/备高可用性和水平扩展模式
- 在 NAT 和防火墙之后安全地托管 Asterisk

## 在 systemd 下运行 Asterisk

在当前所有的 Linux 发行版上——Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9——服务管理器都是 **systemd**。安装章节展示了`make config`步骤（在`make install`期间运行）会安装一个发行版初始化脚本（Debian 上的`/etc/init.d/asterisk`，RedHat 上的`rc.d`脚本），systemd 会自动将其封装为服务；Asterisk 还在`contrib/systemd/asterisk.service`下提供了一个原生的 systemd 单元文件，您可以将其替换安装以获得更精细的控制。
无论哪种方式，systemd 都是运行 Asterisk 的受支持的生产级方式。有关构建本身的内容，请参阅*安装 Asterisk 22*；此处我们重点关注该服务为您提供了什么以及如何操作它。

### 服务单元及其生命周期

一旦`make config`安装了该服务，其生命周期就是普通的 systemd 操作：

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

几点操作说明：

- **`restart`与优雅重载。**`systemctl restart`会终止进程并丢弃所有通话。对于配置更改，您几乎永远不希望这样做——请改用 Asterisk CLI：`asterisk -rx 'core reload'`（或特定模块的重载，如`pjsip reload`）。仅在升级或进程卡死时才使用`systemctl restart`。
- **附加到运行中的守护进程。**当 Asterisk 作为服务运行时，使用`asterisk -r`（或`asterisk -rvvv`以获取详细输出）打开其控制台。这会通过控制套接字连接到已运行的守护进程；它不会启动第二个副本。

### `Restart=`取代了 safe_asterisk

历史上，Asterisk 是通过 **safe_asterisk** 包装器启动的，这是一个在 Asterisk 崩溃时负责重启它的 shell 脚本。在 systemd 下，这项工作属于单元文件的`Restart=`指令——systemd 会检测到进程退出并将其拉起，其退避策略由`RestartSec=`控制，崩溃循环保护由`StartLimitIntervalSec=`/`StartLimitBurst=`控制。因此，在 systemd 主机上，**safe_asterisk 已被取代**，通常是不必要的。如果您的安装包未预设此项，使用 drop-in 覆盖文件是添加“失败后重启”功能的简洁方式，无需编辑打包好的文件：

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

使用`systemctl daemon-reload && systemctl restart asterisk`应用它。使用 drop-in（而不是编辑已安装的单元文件）意味着未来的`make config`不会覆盖您的更改。

### 以非 root 用户身份运行

Asterisk 在生产环境中不应以 root 身份运行——运行在 root 权限下的进程如果存在远程代码漏洞，会导致整个主机被攻破，而同样的漏洞在非特权进程中则会被限制。有两个互补的地方可以强制执行此操作：

- **单元文件 / asterisk.conf。**打包好的单元文件通常以`asterisk`用户和组身份运行 Asterisk。您也可以（或改为）在`asterisk.conf`的`[options]`部分设置`runuser`和`rungroup`，守护进程在绑定后放弃特权时会遵循这些设置：

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **文件所有权。**运行时目录必须对该用户可写。创建账户后，确保所有权正确：

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

由于 SIP (5060) 和 RTP (10000+) 都是高位端口，Asterisk **不需要** root 权限来绑定它们——只有像 port-25 那样的特权端口才需要，而 Asterisk 不使用这些端口。因此，以非特权身份运行是免费的。（安全章节详细阐述了为何这很重要；请参阅*Asterisk 安全*。）

## 容器化 Asterisk

容器将 Asterisk 及其精确的依赖项打包成一个不可变的镜像，因此您测试的内容与您发布的内容在字节层面完全一致。其代价是实时媒体：SIP 服务器对延迟敏感，并且需要从外部可访问的广泛且可预测的 UDP 端口范围，而容器网络可能会造成阻碍。本节的其余部分将通过本书自带的实验室环境——`lab/Dockerfile`和`lab/docker-compose.yml`——作为一个具体的、可工作的示例，然后解释每个人都会遇到的一个陷阱：RTP 和桥接网络。

### 镜像：从源码构建 Asterisk

实验室的`Dockerfile`在 Debian 12 上从源码构建 Asterisk 22。即使您从不自己编写，阅读其结构也是值得的：

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

需要强调三点：

- **版本已锁定**（`ARG ASTERISK_VERSION=22.10.0`）。可重复性是容器化的全部意义所在——谨慎地升级版本、重新构建、重新测试。
- **`--with-pjproject-bundled`和`--with-jansson-bundled`**构建与 Asterisk 版本匹配的 SIP 栈，因此您依赖的 apt 包更少，且永远不必处理与系统 PJSIP 不兼容的问题。
- **`CMD ["asterisk", "-f", "-vvv"]`**在前台运行 Asterisk（`-f`，“不 fork”）。这是与 systemd 主机的关键区别：容器的主进程绝不能守护进程化，否则容器会立即退出。因此，在容器中您**不**使用 systemd 单元文件——容器运行时（Docker，加上`restart:`策略）成为了守护进程，取代了虚拟机上单元文件的`Restart=`功能。

### 绑定挂载`/etc/asterisk`

该镜像特意包含**没有**任何配置。相反，`docker-compose.yml`将主机的配置目录绑定挂载进来：

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro`将版本控制下的`lab/asterisk/etc`目录映射到容器的`/etc/asterisk`，且为只读（`:ro`）。其收益巨大：镜像保持不可变且可重用，而配置保留在主机上，可以在那里进行编辑，最重要的是，可以存放在 git 中（下一节）。要应用配置更改，您只需编辑文件并重载——`docker compose exec asterisk asterisk -rx 'core reload'`——无需重新构建。`restart: unless-stopped`是 compose 级别等同于 systemd 的`Restart=`的功能：如果 Asterisk 退出，Docker 会重启容器，但如果您是主动停止它，则不会重启。

### 主机网络与桥接网络——RTP 问题

这是容器化 Asterisk 最常见的故障，因此值得精确理解。默认情况下，Docker 将容器置于**桥接**网络上，您通过`ports:`发布单个端口。信令没问题——5060 是一个端口。麻烦在于媒体：RTP 使用一个 UDP 端口*范围*（实验室的`rtp.conf`设置了`rtpstart=10000`/`rtpend=10100`），并且**每一个**可能承载音频的端口都必须被发布。

实验室正是这样做的：

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

请注意，RTP 发布范围（`10000-10100`）与`rtp.conf`完全匹配。如果弄错了——发布的端口太少，或者范围与`rtp.conf`不同——通话可以接通但会出现**单向音频或无音频**，因为 RTP 数据包落在了 Docker 未转发的端口上。在桥接模式下还有两个注意事项：

- **发布数千个端口既缓慢又沉重。**生产环境的 RTP 范围通常是 10000–20000。Docker 创建约 10000 个用户态代理转发在启动时开销很大，并且在媒体路径中增加了一跳。实验室特意保持了 100 个端口的小范围，因为它只运行一两个测试通话。
- **SDP 中的 NAT。**在网桥后面，Asterisk 会看到其私有的容器 IP，并可能在 SDP 中通告它。在公共主机上，您必须通过传输层上的`external_media_address`/`external_signaling_address`告知 PJSIP 其外部地址（并设置`local_net`），就像在任何 NAT 后面一样——请参阅下文的*云托管*。

另一种选择是**主机网络**（`network_mode: host`），它完全移除了网桥：容器共享主机的网络栈，因此 5060 和整个 RTP 范围无需端口发布且无需额外的媒体跳转即可访问。这是真正的 Asterisk 容器推荐的模式——它完全避开了 RTP 范围问题。其代价是隔离性：容器可以绑定任何主机端口，并且您失去了 compose 的按服务网络功能。（主机网络是 Linux 的一项功能；在 macOS/Windows 的 Docker Desktop 上其行为不同，这也是本教学实验室使用显式发布端口的部分原因。）

### 用于 spool 和 voicemail 的持久卷

容器的可写层是**短暂的**——销毁容器，它写入的任何内容都会消失。对于 Asterisk 而言，这意味着语音信箱、录音、外呼 spool 和本地数据库会在每次`docker compose up --build`时消失。配置之所以能存活是因为它是从主机绑定挂载的；*状态*也需要同样的待遇。在容器内部，相关的目录树为：

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

（实验室运行中的容器显示了这些——`/var/spool/asterisk`包含`voicemail`、`monitor`、`outgoing`、`recording`；`/var/lib/asterisk`持有`astdb.sqlite3`。）为了保留它们，请为存储您关心的状态的目录挂载命名卷：

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

教学实验室特意省略了这些——它被设计为无状态且可重复的，因此每次`up`都是一个全新的开始——但生产环境的容器**必须**拥有它们，否则您会在第一次重新部署时丢失语音信箱。

## 配置管理与备份

上面的绑定挂载暗示了正确的模型：将`/etc/asterisk`视为**代码**，其余部分视为**数据**。

### 将`/etc/asterisk`纳入版本控制

配置目录是一组扁平的文本文件，没有无法模板化的秘密——它是 git 的理想选择。在`/etc/asterisk`中初始化一个仓库（或者，像实验室那样，将配置与项目放在一起并绑定挂载它）。好处包括：

- 每次更改都是可审查和可回滚的（`git diff`、`git revert`）。
- 您拥有谁在何时更改了什么的审计追踪。
- 结合容器镜像，一个已知的良好配置提交加上一个锁定的镜像标签，完整地描述了一个部署。

针对 Asterisk 配置的几点注意事项：

- **秘密。**`pjsip.conf`（以及`manager.conf`、`ari.conf`）包含密码。不要将真实的秘密以明文形式提交到共享仓库——请模板化它们（每个环境一个文件，或在部署时使用秘密管理器/环境变量替换），并仅在 git 中保留占位符。实验室琐碎的`Lab-6001-secret`风格密码之所以可以，*仅仅*是因为它们位于私有的 Docker 子网中。
- **环境模板化。**在开发、测试和生产环境之间不同的实时值（绑定地址、外部 IP、中继凭据、数据库 URL）正是您需要模板化的行，从而保持大部分配置在各环境间完全一致。

### 备份什么

git 中的配置涵盖了 dialplan 和 endpoint，但运行中的 PBX 会积累不属于任何配置文件的*状态*。完整的备份包括：

| 内容 | 位置 | 原因 |
|------|-------|-----|
| 配置 | `/etc/asterisk/` | dialplan, endpoints (也在 git 中) |
| 语音信箱与录音 | `/var/spool/asterisk/` | 用户数据 — 不可替代 |
| 内部数据库 | `/var/lib/asterisk/astdb.sqlite3` | `DB()` 键值, 设备状态 |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` 或 SQL 存储 | 计费与历史记录 |
| 外部数据库 | 您的 MySQL/PostgreSQL | realtime, CDR, 语音信箱 |

**astdb** 值得一提：它是 Asterisk 内置的小型键值存储（位于`/var/lib/asterisk/astdb.sqlite3`的 SQLite 文件），被`DB()` dialplan 函数、设备状态、呼叫转移设置等使用。您可以从 CLI 转储它以进行检查或备份：

```
asterisk -rx 'database show'
```

如果您的 CDR/CEL、语音信箱或 PJSIP 配置位于外部数据库中（请参阅*Asterisk 实时*和*Asterisk 呼叫详细记录*），那么该数据库现在就是该数据的真实来源，必须纳入您的常规数据库备份轮换中——仅备份`/etc/asterisk`是不够的。

## 监控与可观测性

您无法操作您看不见的东西。Asterisk 在四个层面上暴露其状态，从人类快速浏览到指标流水线：**CLI**、**CDR/CEL** 记录、**AMI/ARI** 事件以及**指标导出器**。

### CLI 健康检查

最快的“它健康吗？”检查是 CLI。下面的命令是针对实验室环境实时运行的。首先是通道：

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

在安静的系统上`0 active calls`是正常的；在繁忙的系统上，这是您的实时并发量。`core show uptime`确认进程没有在您不知情的情况下重启：

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

对于 SIP 健康状况，`pjsip show endpoints`显示每个 endpoint 以及其注册的联系人是否可达。来自实验室：

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

此处的`Unavailable`仅表示当前没有电话注册到这些 endpoint（实验室没有实时客户端）——一旦软电话注册且`qualify`确认它，状态就会显示联系人为可达。配套命令：`pjsip show contacts`（当前注册和往返时间）、`pjsip show transports`以及针对单个 AOR 的`pjsip show aor <name>`。这些是日常“为什么分机 X 无法接通？”的工具。

### CDR 和 CEL

每次通话都会留下**呼叫详细记录**（CDR）；**通道事件日志**（CEL）增加了更细致的每通道事件。确认 CDR 已激活以及哪个后端存储它：

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

实验室在已注册后端下显示`(none)`，因为最小化的实验室配置没有加载任何 CDR 存储模块——因此记录会被计算但不会写入任何地方。在生产环境中，您会加载一个后端（CSV，或`cdr_odbc`/`cdr_adaptive_odbc`到 MySQL/PostgreSQL），那将成为您的计费和历史记录来源。CEL **默认禁用**（`cel show status` 显示` reports `CEL Logging: Disabled` in the lab) and you enable it in `），仅在需要事件级详细信息时在 `cel.conf` 中启用。两者在*Asterisk 呼叫详细记录*中有深入介绍；对于监控，重点在于 CDR/CEL 是您的*历史*记录，而 CLI 是您的*实时*视图。

### AMI 和 ARI 事件

对于程序化的实时监控，您需要一个事件推送流，而不是轮询 CLI：

- **AMI (Asterisk Manager Interface)** 是长期存在的 TCP 事件/命令协议（`manager.conf`）。订阅它，您会在通话发生时收到`Newchannel`、`Hangup`、`DialBegin`、`BridgeEnter`、`PeerStatus`等事件——这是墙板和呼叫计费工具的骨干。在实验室中，AMI 默认禁用（`manager show settings`报告`Manager (AMI): No`）；您可以在`manager.conf`中启用并锁定它。
- **ARI (Asterisk REST Interface)** 是现代的 HTTP + WebSocket 接口（`ari.conf`，由内置的 HTTP 服务器提供服务）。它提供 JSON 事件流和细粒度的呼叫控制——这是新集成的正确选择。

两者在*使用 AMI 和 AGI 扩展 Asterisk* 和 *Asterisk REST 接口 (ARI)* 中有详细说明。与部署相关的警告：**AMI 和 ARI 功能强大，绝不能暴露在互联网上。**将 HTTP 服务器绑定到 localhost 或管理网络，使用强且唯一的秘密，并防火墙端口——请参阅*Asterisk 安全*。

### 指标：Prometheus 和 Grafana

对于仪表板和告警，Asterisk 22 提供了一个 Prometheus 导出器，**`res_prometheus.so`**（一个具有*扩展*支持级别的模块），它在 HTTP 端点上暴露指标，供 Prometheus 服务器抓取。除了核心进程指标外，它还提供可插拔的提供程序，涵盖通道、通话、endpoint、桥接和 PJSIP 出站注册：

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

您可以确认该模块是否存在于实验室构建中：

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

它显示`Not Running`，因为实验室没有配置或加载它；启用它（```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```加上 HTTP 服务器）会将 Asterisk 变成一个 Prometheus 目标。将 Prometheus 指向抓取端点，将 Grafana 指向 Prometheus，您就可以获得时间序列仪表板（并发通话、注册、ASR/ACD 趋势）和告警（例如“活跃通话降至零”或“注册失败激增”）。对于已经运行 Prometheus/Grafana 的团队来说，这是将 Asterisk 纳入现有可观测性的自然方式，而不是解析 CLI 输出。

### 值得关注的 SIP 响应代码

无论流水线如何，一些 SIP 结果预示着麻烦，值得告警：持续的`401`/`407`挑战失败或`403 Forbidden`暗示了暴力破解或配置错误的凭据风暴（请参阅*Asterisk 安全*中的 Fail2Ban）；`503 Service Unavailable`指向过载或拥塞的服务器或中继；`408 Request Timeout`/`480 Temporarily Unavailable`的激增通常意味着 endpoint 已变得不可达（NAT 超时、qualify 失败）。

## 高可用性与扩展

单台 Asterisk 服务器是一个单点故障，并且有有限的通话上限。这两个问题——*保持运行*和*变得更大*——有不同的答案。

### 带浮动 IP 的主/备模式

Asterisk 经典的、久经考验的 HA 模式是**主/备**（不是主/主——Asterisk 中的呼叫状态很难实时共享）。两台相同的服务器，一台主用，一台备用，共享一个由集群管理器（如 **keepalived** (VRRP) 或 **Pacemaker/Corosync**）管理的**浮动（虚拟）IP**。电话和中继注册到浮动 IP，而不是任何一台真实主机。如果主节点健康检查失败，浮动 IP 会移动到备用节点，由其接管。

诚实的警告：IP 故障转移会**丢弃正在进行的通话**——Asterisk 不会在节点间复制实时通道状态，因此任何通话中的人必须重拨。注册会在 qualify/注册周期内重新建立。故障转移为您带来的是*服务*在几秒钟内无需人工干预即可恢复，对于大多数 PBX 而言，这正是目标。为了使备用节点真正能够接管，两个节点都需要相同的配置（您 git 中的`/etc/asterisk`，部署方式相同）和相同的*状态*——这就是下一点。

### 使用 PJSIP Realtime 外部化状态

主/备模式只有在备用节点知道与主节点相同的 endpoint 和注册信息时才有效。实现这一目标的方法是**停止将状态保存在单台机器的扁平文件中**，并将其移动到两个节点都能读取的共享数据库中。**PJSIP Realtime**（由数据库支持的 Sorcery）正是这样做的：endpoint、AOR、认证——以及重要的是，**注册**（`ps_contacts`表）——存在于 MySQL/PostgreSQL 中，而不是`pjsip.conf`和本地内存中。两个 Asterisk 节点都指向同一个数据库，因此通过一个节点注册的电话对另一个节点也是可见的。这在*Asterisk 实时*（PJSIP Realtime / Sorcery 部分）中有介绍；此处的部署重点是**外部化状态是 HA 和水平扩展的先决条件**——没有它，每个节点都是一座孤岛。

将同样的逻辑应用于您的其余状态：CDR/CEL 存入共享 SQL 存储，语音信箱存入共享/复制存储（或`ODBC_STORAGE`），以及您依赖的 astdb 键值存入数据库。一旦状态外部化，Asterisk 节点就更接近于可互换的前端。

### 前置 SIP 代理 (OpenSIPS)

要扩展到*超过*单台服务器的容量，您可以在一组 Asterisk 媒体服务器前面放置一个 **SIP 代理/负载均衡器**。**OpenSIPS** 是一个专门构建的、极高吞吐量的 SIP 代理（它们处理数十万次注册并路由信令，而不触及媒体）。代理向世界呈现一个单一的 SIP 地址，维护注册/位置服务，并将呼叫分发到 Asterisk 后端。这种分离——一个负责注册和路由的轻量级代理层，一个负责实际呼叫处理（IVR、队列、会议、转码）的水平可扩展 Asterisk 层——就是大型部署如何超越单台机器的方式。（SipPulse 平台本身正是出于这个原因在媒体/应用服务器前面使用了 OpenSIPS。）

### 媒体扩展

代理廉价地分发*信令*；**媒体是昂贵的资源**。RTP 中继，特别是编解码器之间的转码（例如 Opus ↔ G.711）或运行大型会议，是 CPU 密集型的，这才是真正限制服务器的原因。策略：

- **尽可能避免转码**——协商端到端的通用编解码器，以便 Asterisk 原生桥接（透传）而不是转码。这是媒体容量提升最大的一点。
- **通过在代理后面添加 Asterisk 节点来水平扩展媒体**；每个节点承载一部分并发通话。
- **将浏览器媒体卸载到专用的 WebRTC 网关**（例如 Janus），这样 PBX 就不会同时终止和中继每个浏览器的 DTLS-SRTP 流——请参阅*使用 Asterisk 的 WebRTC*，其中讨论了这种 Asterisk 加网关的拆分。

按**并发通话和转码负载**来衡量容量，而不是按注册用户数——10,000 个大部分时间处于空闲状态的注册电话远比 200 个同时进行的转码会议便宜。

## 云托管

在云虚拟机（AWS、GCP、Azure、VPS）上运行 Asterisk 很常见且效果良好，但云网络**默认是 NAT 和防火墙保护的**，这与 SIP 冲突。以下是部署特定的关注点。

### NAT 和 SDP

云虚拟机几乎总是在其网卡上有一个**私有** IP，以及一个提供商 NAT 到它的独立**公共** IP。如果 Asterisk 在 SDP 中通告私有 IP，远程电话会将 RTP 发送到黑洞——经典的单向/无音频症状。在传输层上告知 PJSIP 其公共身份：



`external_*`使 Asterisk 重写它向公共对等方通告的地址，而`local_net`告知它哪些对等方是本地的（且*不应*被重写）。这与上面讨论的桥接 Docker 网络的 NAT 处理相同——云虚拟机实际上处于 NAT 后面。

### 防火墙和 RTP 范围

云虚拟机上通常有两个防火墙：**提供商的**安全组/网络 ACL，以及**主机的** iptables。两者都必须打开相同的端口，策略是安全章节中的策略。保存的第 1 版规则集（`docs/legacy-labs/configs/Lab7/rules.v4`）捕捉了其形态——接受 SIP 和 RTP 范围，接受已建立/相关的连接，丢弃其余部分：

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

安全章节在此处做出的两个重要修正：如果您运行 SIP/TLS，请打开 **TCP 上的 5061**（而不是 UDP），并记住防火墙中的 RTP UDP 范围必须与`rtp.conf`中的`rtpstart`/`rtpend`完全匹配——这与您在容器上发布的范围相同。不要在此处重复 iptables/Fail2Ban 构建；**请遵循*Asterisk 安全*中的防火墙、Fail2Ban 和 TLS/SRTP 部分**（Fail2Ban 监视实验室已经在`logger.conf`中启用的`security`记录器通道），并在主机防火墙和云安全组中应用该策略。

### 延迟、区域和 SBC

- **选择靠近用户的区域。**语音对延迟敏感——超过 ~150 毫秒的单向口耳延迟是明显的。将虚拟机托管在离您的大多数电话和中继最近的区域；跨洲媒体明显更差。
- **对于任何面向互联网的部署，在前面放置一个 SBC。****会话边界控制器 (SBC)** 在边缘终止 SIP/RTP，隐藏您的拓扑，规范化 NAT，并在流量到达 Asterisk 之前吸收 DoS 和扫描流量。安全章节的核心建议——*不要将原始 Asterisk 暴露在互联网上*——在云端加倍适用，因为您的虚拟机公共 IP 在启动后几分钟内就会被扫描。SBC（或至少是像 OpenSIPS 这样加固的 SIP 代理加上 Fail2Ban）是标准的边缘配置。

## 总结

部署是将可工作的 dialplan 变为可靠服务的过程。在虚拟机上，以**非 root** 用户身份在 **systemd** 下运行 Asterisk，让单元文件的`Restart=`保持其运行（safe_asterisk 已被取代），并使用`core reload`而不是 `systemctl restart` 进行配置更改。使用 Docker 进行**容器化**——正如本书实验室所做的那样——为您提供了一个不可变的、锁定的镜像，其配置从 git 化的`/etc/asterisk`中**绑定挂载**；陷阱在于媒体，因此要么使用**主机网络**，要么发布与`rtp.conf`**完全匹配**的 RTP 端口范围，并为 spool/语音信箱/astdb 挂载**持久卷**，以便状态在重新部署后存活。将配置视为代码，并**备份**配置无法捕获的状态：语音信箱、录音、`astdb.sqlite3`和 CDR/CEL。在四个层面上**观测**系统——CLI（`core show channels`、`pjsip show endpoints`）用于实时视图，**CDR/CEL** 用于历史记录，**AMI/ARI** 用于程序化事件，以及 **`res_prometheus`** 导出器到 Grafana 用于仪表板和告警——同时保持 AMI/ARI 不在公共互联网上。为了**保持运行**，运行带**浮动 IP** 的主/备模式（接受故障转移会丢弃实时通话）；为了**增长**，使用 **PJSIP Realtime** 外部化状态，用 **OpenSIPS** 前置一组媒体服务器，并最小化转码，因为**媒体——而不是注册——才是限制服务器的因素**。最后，在**云端**，将虚拟机视为处于 NAT 后面（`external_media_address`、`local_net`），在主机和提供商安全组中按安全章节打开防火墙，选择低延迟区域，并且永远不要暴露原始 Asterisk——在边缘放置一个 **SBC**。

## 测验

1. 在 systemd 主机上，什么取代了旧的`safe_asterisk`包装器重启崩溃的 Asterisk 的工作？
   - A. 一个 cron 任务
   - B. 单元文件的`Restart=`指令
   - C. `systemctl enable`
   - D. astdb
2. 要在**不丢弃通话**的情况下对运行中的 Asterisk 应用配置更改，您应该：
   - A. `systemctl restart asterisk`
   - B. 重启服务器
   - C. `asterisk -rx 'core reload'`
   - D. 重新构建容器镜像
3. 容器化（桥接网络）的 Asterisk 可以接通通话但**没有音频**。最可能的原因是：
   - A. dialplan 错误
   - B. 发布的 RTP UDP 端口范围与`rtp.conf`中的`rtpstart`/`rtpend`不匹配
   - C. CDR 已禁用
   - D. CLI 不可达
4. 哪些目录必须挂载为**持久卷**，以便容器重新部署不会丢失状态？（多选）
   - A. `/var/spool/asterisk`（语音信箱、录音）
   - B. `/var/lib/asterisk`（astdb）
   - C. `/etc/asterisk`（已从主机绑定挂载）
   - D. `/usr/sbin`
5. 哪个 CLI 命令给出活跃通话的实时计数？
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. 在 Asterisk 22 中，将呼叫/通道指标暴露给 Prometheus/Grafana 栈的受支持方式是：
   - A. 解析`full`日志文件
   - B. `res_prometheus.so`模块
   - C. AGI 脚本
   - D. 没有这种方式
7. HA 故障转移和跨多个 Asterisk 节点水平扩展的先决条件是什么？
   - A. 以 root 身份运行
   - B. 外部化状态（例如共享数据库中的 PJSIP Realtime 注册）
   - C. 禁用 CDR
   - D. 使用桥接网络
8. 哪个资源最直接地限制了一台 Asterisk 服务器可以处理的并发通话数？
   - A. 注册用户数
   - B. 媒体处理，尤其是转码
   - C. `/etc/asterisk`的大小
   - D. CDR 后端
9. 在云虚拟机上，哪些`pjsip.conf`传输设置使 Asterisk 通告其公共地址以便远程音频工作？（多选）
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. 对于面向互联网的云部署，安全章节的核心规则是：
    - A. 始终运行两个网卡
    - B. 永远不要将原始 Asterisk 暴露在互联网上；在边缘放置一个 SBC（或加固的代理 + Fail2Ban）
    - C. 仅使用 UDP
    - D. 禁用 TLS

**答案：** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
