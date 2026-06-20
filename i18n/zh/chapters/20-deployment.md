# 部署、监控与扩展

让 Asterisk 在实验室里接听电话是一回事；让它作为一个能够在崩溃、重启、升级和攻击者攻击下仍然存活的服务运行——并且可以被观察、备份和扩展——则是另一回事。本章讨论的是 *dialplan* 正常工作之后的所有内容。我们先从保持 Asterisk 活跃的监督程序（systemd）说起，接着将其打包进容器（使用本书自己的 Docker 实验作为示例），随后覆盖配置管理与备份、监控与可观测性，最后介绍在单台服务器不足以支撑时的模式：高可用性与扩展，以及在云端托管的实际情况。

所有示例均已在本书的 Asterisk 22 实验环境`lab/`中验证——即你在全书中一直在构建的同一容器。

## Objectives

By the end of this chapter, you should be able to:

- Run Asterisk 22 reliably under systemd, as a non-root user, with automatic restart
- Containerize Asterisk with Docker and understand the networking trade-offs
- Keep `/etc/asterisk` in version control and back up the right state
- Monitor a running system through the CLI, CDR/CEL, AMI/ARI and metrics
- Apply active/standby high availability and horizontal scaling patterns
- Host Asterisk in the cloud safely behind NAT and a firewall

## 在 systemd 下运行 Asterisk

在所有当前的 Linux 发行版——Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9——服务管理器都是 **systemd**。安装章节展示了`make config`步骤（在`make install`期间运行）会安装一个发行版的 init 脚本（Debian 上的`/etc/init.d/asterisk`、RedHat 上的`rc.d`脚本），systemd 会自动将其包装为服务；Asterisk 还在`contrib/systemd/asterisk.service`下提供了一个原生 systemd 单元，您可以用它来替代，以获得更细粒度的控制。  
无论哪种方式，systemd 都是受支持的、生产环境下运行 Asterisk 的方式。交叉参考 *Installing Asterisk 22* 了解构建本身；这里我们关注服务提供的功能以及如何操作它。

### 服务单元及其生命周期

一旦`make config`安装了服务，生命周期就是普通的 systemd：

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

一些操作注意事项：

- **`restart` 与优雅重载的区别。** `systemctl restart` 会终止进程并挂断所有通话。对于配置更改，您几乎从不希望这样——请使用 Asterisk CLI：`asterisk -rx 'core reload'`（或特定模块的重载，例如`pjsip reload`）。将`systemctl restart`保留用于升级或卡死的进程。
- **附加到正在运行的守护进程。** 当 Asterisk 作为服务运行时，使用`asterisk -r`（或用于详细输出的`asterisk -rvvv`）打开其控制台。这会通过控制套接字连接到已经在运行的守护进程；它不会启动第二个副本。

### `Restart=` 替代 safe_asterisk

历史上 Asterisk 是通过 **safe_asterisk** 包装器启动的，这是一个在 Asterisk 崩溃后重新生成进程的 shell 脚本。在 systemd 下，这项工作属于单元的`Restart=`指令——systemd 会检测进程退出并将其重新启动，重启间隔由`RestartSec=`控制，崩溃循环保护由`StartLimitIntervalSec=`/`StartLimitBurst=`实现。因此在 systemd 主机上 **safe_asterisk 已被取代**，通常也不再需要。如果您使用的单元尚未设置它，使用 drop‑in 覆盖是添加失败重启而不修改包装文件的干净方式：

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

使用`systemctl daemon-reload && systemctl restart asterisk`应用它。采用 drop‑in（而不是编辑已安装的单元）意味着将来的`make config`不会覆盖您的更改。

### 以非 root 用户运行

在生产环境中，Asterisk 不应以 root 身份运行——以 root 运行的进程出现远程代码执行漏洞会导致整个主机被攻破，而相同的漏洞在非特权进程中则受到限制。此规则在两个互补的地方得到强制：

- **单元 / asterisk.conf。** 打包的单元通常以`asterisk`用户和组运行 Asterisk。您也可以（或改为）在`asterisk.conf`的`[options]`节中设置`runuser`和`rungroup`，守护进程在绑定后降权时会遵循这些设置：

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **文件所有权。** 运行时目录必须对该用户可写。创建账户后，确保所有权：

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

由于 SIP（5060）和 RTP（10000+）都是高端口，Asterisk **不需要** root 权限来绑定它们——只有类似 25 号端口的特权端口才需要 root，而 Asterisk 并不使用这些端口。因此以非特权方式运行是完全自由的。（安全章节进一步阐述了这点的重要性；参见 *Asterisk Security*。）

## 容器化 Asterisk

容器将 Asterisk 及其精确的依赖打包成一个不可变的镜像，这样你测试的内容与交付的内容在字节上完全一致。权衡在于实时媒体：SIP 服务器对延迟敏感，需要一组可从外部访问的宽范围、可预测的 UDP 端口，而容器网络可能会成为障碍。本节其余部分将通过本书自己的实验室——`lab/Dockerfile`和`lab/docker-compose.yml`——作为具体可行的示例进行演示，然后解释每个人都会遇到的一个陷阱：RTP 与桥接网络。

### 镜像：从源码构建 Asterisk

实验室的`Dockerfile`在 Debian 12 上从源码构建 Asterisk 22。即使你从未自己动手构建，阅读它的结构也很有价值：

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

Three things to call out:

- **The version is pinned** (`ARG ASTERISK_VERSION=22.10.0`). Reproducibility is the
  whole point of containerizing — bump it deliberately, rebuild, retest.
- **`--with-pjproject-bundled` and `--with-jansson-bundled`** build the SIP stack
  version-matched to Asterisk, so you depend on fewer apt packages and never fight a
  distro PJSIP that is out of step.
- **`CMD ["asterisk", "-f", "-vvv"]`** runs Asterisk in the *foreground* (`-f`, "do not
  fork"). This is the key difference from a systemd host: a container's main process
  must not daemonize, or the container would exit immediately. So in a container you do
  **not** use the systemd unit at all — the container runtime (Docker, plus `restart:`
  policy) becomes the supervisor that the unit's `Restart=` was on a VM.

### Bind-mounting `/etc/asterisk`

The image deliberately contains **no** configuration. Instead `docker-compose.yml`
bind-mounts the host's config directory in:

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

`./asterisk/etc:/etc/asterisk:ro` 将受版本控制的 `lab/asterisk/etc`  
目录映射到容器的 `/etc/asterisk`，只读（`:ro`）。收益很大：  
镜像保持不可变且可复用，而配置则位于主机上，  
可以编辑，并且关键是可以放入 git（下一节）。要应用配置更改，只需  
编辑文件并重新加载——`docker compose exec asterisk asterisk -rx 'core reload'`——  
无需重新构建。`restart: unless-stopped` 是 compose 级别等同于  
systemd 的 `Restart=`：Docker 在 Asterisk 退出时会重启容器，但在你  
手动停止时则不会。

### 主机网络 vs. 桥接网络 — RTP 问题

这是容器化 Asterisk 最常见的故障，因此值得  
精确理解。默认情况下 Docker 将容器放在 **桥接** 网络上，  
并使用 `ports:` 发布单个端口。信令没有问题——5060 是一个端口。  
问题出在媒体上：RTP 使用一段 UDP 端口（实验室的 `rtp.conf` 设置了  
`rtpstart=10000` / `rtpend=10100`），并且 **每个** 可能携带音频的端口都必须  
被发布。

实验室正是这样做的：

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Note the RTP publish range (`10000-10100`) matches `rtp.conf` exactly. Get this wrong —
publish too few ports, or a different range than `rtp.conf` — and calls connect but
have **one-way or no audio**, because the RTP packets land on a port Docker is not
forwarding. Two further cautions with bridged mode:

- **Publishing thousands of ports is slow and heavy.** A production RTP range is
  typically 10000–20000. Docker creating ~10000 userland proxy forwards is expensive at
  start-up and adds a hop in the media path. The lab keeps a deliberately small
  100-port range because it only ever runs one or two test calls.
- **NAT in the SDP.** Behind the bridge, Asterisk sees its private container IP and may
  advertise it in SDP. On a public host you must tell PJSIP its external address with
  `external_media_address` / `external_signaling_address` on the transport (and set
  `local_net`), exactly as you would behind any NAT — see *Cloud hosting* below.

The alternative is **host networking** (`network_mode: host`), which removes the bridge
entirely: the container shares the host's network stack, so 5060 and the whole RTP
range are reachable with no port publishing and no extra media hop. This is the
recommended mode for a real Asterisk container — it sidesteps the RTP-range problem
completely. Its cost is isolation: the container can bind any host port and you lose
compose's per-service network. (Host networking is a Linux feature; on Docker Desktop
for macOS/Windows it behaves differently, which is partly why this teaching lab uses
explicit published ports instead.)

### 持久化卷用于 spool 和 voicemail

A container's writable layer is **ephemeral** — destroy the container and anything it
wrote is gone. For Asterisk that means voicemail, recordings, the outgoing call spool
and the local database would vanish on every `docker compose up --build`. Configuration
survives because it is bind-mounted from the host; *state* needs the same treatment.
Inside the container the relevant trees are:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

（实验室运行的容器正好显示这些——`/var/spool/asterisk`包含
`voicemail`、`monitor`、`outgoing`、`recording`；`/var/lib/asterisk`保存
`astdb.sqlite3`。）为了保留它们，请为保存状态的目录挂载具名卷
您关心的状态：

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

The teaching lab omits these on purpose — it is stateless and reproducible by design,
so every `up` is a clean slate — but a production container **must** have them, or you
will lose voicemail on the first redeploy.

## Configuration management and backups

The bind-mount above hints at the right model: treat `/etc/asterisk` as **code** and
the rest as **data**.

### Keep `/etc/asterisk` in version control

The config directory is a flat set of text files with no secrets that cannot be
templated — it is ideal for git. Initialise a repo in `/etc/asterisk` (or, as the lab
does, keep the config alongside the project and bind-mount it). Benefits:

- Every change is reviewable and revertible (`git diff`, `git revert`).
- You have an audit trail of who changed what and when.
- Combined with a container image, a known-good config commit plus a pinned image tag
  fully describes a deployment.

A couple of cautions specific to Asterisk config:

- **Secrets.** `pjsip.conf` (and `manager.conf`, `ari.conf`) contain passwords. Do not
  commit real secrets to a shared repo in clear text — template them (one file per
  environment, or a secrets manager / environment substitution at deploy time) and keep
  only placeholders in git. The lab's trivial `Lab-6001-secret` style passwords are fine
  *only* because they live on a private Docker subnet.
- **Per-environment templating.** The realtime values that differ between dev, staging
  and production (bind addresses, external IPs, trunk credentials, database URLs) are
  exactly the lines you templatize, keeping the bulk of the config identical across
  environments.

### What to back up

Configuration in git covers the dialplan and endpoints, but a live PBX accumulates
*state* that is not in any config file. A complete backup is:

| What | Where | Why |
|------|-------|-----|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (also in git) |
| Voicemail & recordings | `/var/spool/asterisk/` | user data — irreplaceable |
| Internal database | `/var/lib/asterisk/astdb.sqlite3` | `DB()` keys, device state |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` or SQL store | billing & history |
| External databases | your MySQL/PostgreSQL | realtime, CDR, voicemail |

The **astdb** deserves a note: it is Asterisk's small built-in key/value store (a
SQLite file at `/var/lib/asterisk/astdb.sqlite3`) used by `DB()` dialplan functions,
device states, follow-me settings and similar. You can dump it for inspection or backup
from the CLI:

```
asterisk -rx 'database show'
```

If your CDR/CEL or voicemail or PJSIP config lives in an external database (see
*Asterisk Real-Time* and *Asterisk Call Detail Records*), that database is now the
source of truth for that data and must be in your normal database backup rotation —
backing up `/etc/asterisk` alone is not enough.

## 监控与可观测性

你无法管理看不见的东西。Asterisk 在四个层面公开其状态，从快速的人眼查看到指标管道：**CLI**、**CDR/CEL** 记录、**AMI/ARI** 事件以及 **metrics exporters**。

### CLI 健康检查

最快的“是否健康？”检查就是 CLI。下面的命令在实验环境中实时运行。首先是通道：

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` 在安静的系统上是正常的；在繁忙的系统上这就是你的实时并发。 `core show uptime` 确认该进程没有在你之下重新启动：

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

对于 SIP 健康，`pjsip show endpoints`显示每个 endpoint 以及其已注册的 contacts 是否可达。来自实验室：

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` 在此仅表示当前没有电话注册到这些端点（实验室没有实时客户端）——一旦软电话注册并且 `qualify` 确认后，状态会显示该联系人可达。伴随命令：`pjsip show contacts`（当前注册及往返时间）、`pjsip show transports` 和 `pjsip show aor <name>`（针对单个 AOR）。这些是日常排查 “为什么分机 X 无法接通？” 的工具。

### CDR and CEL

每一次通话都会生成 **Call Detail Record**（CDR）；**Channel Event Logging**（CEL）则提供更细粒度的每通道事件。请确认 CDR 已启用并且了解哪个后端存储了它：

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

The lab shows `(none)` under registered backends because the minimal lab config loads
no CDR storage module — so records are computed but written nowhere. In production you
load a backend (CSV, or `cdr_odbc`/`cdr_adaptive_odbc` into MySQL/PostgreSQL) and that
becomes your billing and history source. CEL is **disabled by default** (`cel show
status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` only
when you need event-level detail. Both are covered in depth in *Asterisk Call Detail
Records*; for monitoring, the point is that CDR/CEL are your *historical* record, where
the CLI is your *live* view.

### AMI and ARI events

For programmatic, real-time monitoring you want a push feed of events rather than
polling the CLI:

- **AMI (Asterisk Manager Interface)** is the long-standing TCP event/command protocol
  (`manager.conf`). Subscribe and you receive `Newchannel`, `Hangup`, `DialBegin`,
  `BridgeEnter`, `PeerStatus` and similar events as calls happen — the backbone of wallboards
  and call-accounting tools. In the lab AMI is disabled by default (`manager show settings`
  reports `Manager (AMI): No`); you enable and lock it down in `manager.conf`.
- **ARI (Asterisk REST Interface)** is the modern HTTP + WebSocket interface
  (`ari.conf`, served by the built-in HTTP server). It gives a JSON event stream and
  fine-grained call control — the right choice for new integrations.

Both are detailed in *Extending Asterisk with AMI and AGI* and *The Asterisk REST
Interface (ARI)*. The deployment-relevant
warning: **AMI and ARI are powerful and must never be exposed to the internet.** Bind the
HTTP server to localhost or a management network, use strong unique secrets, and
firewall the ports — see *Asterisk Security*.

### Metrics: Prometheus and Grafana

For dashboards and alerting, Asterisk 22 ships a Prometheus exporter,
**`res_prometheus.so`** (a module with *extended* support level), which exposes metrics
on an HTTP endpoint that a Prometheus server scrapes. Alongside core process metrics it
ships pluggable providers covering channels, calls, endpoints, bridges and PJSIP
outbound registrations:

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

您可以确认该模块已包含在实验构建中：

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

它显示 `Not Running` 因为实验室没有配置或加载它；启用它（`prometheus.conf` 加上 HTTP 服务器）会将 Asterisk 变成 Prometheus 的目标。将 Prometheus 指向抓取端点，将 Grafana 指向 Prometheus，即可获得时间序列仪表板（并发呼叫、注册、ASR/ACD 趋势）和告警（例如 “活跃呼叫降至零” 或 “注册失败激增”）。对于已经在运行 Prometheus/Grafana 的团队来说，这是将 Asterisk 融入现有可观测性体系的自然方式，而不是解析 CLI 输出。

### 值得关注的 SIP 响应码

无论使用何种管道，少数 SIP 结果会提示问题并值得进行告警：持续的 `401`/`407` 挑战失败或 `403 Forbidden` 表明存在暴力破解或凭证配置错误的风暴（在 *Asterisk Security* 中交叉引用 Fail2Ban）；`503 Service Unavailable` 指向服务器或 trunk 过载或拥塞；以及 `408 Request Timeout`/`480 Temporarily Unavailable` 的激增通常意味着端点已不可达（NAT 超时、qualify 失败）。

## High availability and scaling

One Asterisk server is a single point of failure and has a finite call ceiling. The two
problems — *staying up* and *getting bigger* — have different answers.

### Active/standby with a floating IP

The classic, well-trodden HA pattern for Asterisk is **active/standby** (not
active/active — call state in Asterisk is hard to share live). Two identical servers,
one active, one standby, share a **floating (virtual) IP** managed by a cluster manager
such as **keepalived** (VRRP) or **Pacemaker/Corosync**. Phones and trunks register to
the floating IP, not to either real host. If the active node fails its health check, the
floating IP moves to the standby, which takes over.

The honest caveat: an IP failover **drops calls in progress** — Asterisk does not
replicate live channel state between nodes, so anyone mid-call must redial. Registrations
re-establish within a qualify/registration cycle. What failover buys you is that the
*service* recovers in seconds without manual intervention, which for most PBXs is exactly
the goal. To make the standby genuinely able to take over, both nodes need the same
configuration (your git'd `/etc/asterisk`, deployed identically) and the same *state* —
which is the next point.

### Externalize state with PJSIP Realtime

Active/standby only works if the standby knows about the same endpoints and
registrations as the active node. The way to achieve that is to **stop keeping state in
flat files on one box** and move it to a shared database both nodes read. **PJSIP
Realtime** (Sorcery backed by a database) does exactly this: endpoints, AORs, auths —
and, importantly, **registrations** (the `ps_contacts` table) — live in MySQL/PostgreSQL
instead of `pjsip.conf` and local memory. Both Asterisk nodes point at the same database,
so a phone registered through one node is visible to the other. This is covered in
*Asterisk Real-Time* (the PJSIP Realtime / Sorcery section); here the deployment point is
that **externalizing state is the prerequisite for both HA and horizontal scaling** —
without it, each node is an island.

Apply the same logic to the rest of your state: CDR/CEL into a shared SQL store, voicemail
on shared/replicated storage (or `ODBC_STORAGE`), and the astdb keys you depend on into a
database. Once state is external, the Asterisk nodes become closer to interchangeable
front-ends.

### SIP proxies in front (OpenSIPS)

To scale *beyond* one server's capacity you put a **SIP proxy/load balancer** in front of
a pool of Asterisk media servers. **OpenSIPS** is a purpose-built, very
high-throughput SIP proxy (they handle hundreds of thousands of registrations and route
signaling without touching media). The proxy presents a single SIP address to the world,
maintains the registration/location service, and distributes calls across the Asterisk
back-ends. This separation — a lightweight proxy tier doing registration and routing, a
horizontally-scalable Asterisk tier doing the actual call processing (IVR, queues,
conferences, transcoding) — is how large deployments grow past a single box. (The SipPulse
platform itself uses OpenSIPS in front of its media/application servers for exactly this
reason.)

### Media scaling

The proxy distributes *signaling* cheaply; **media is the expensive resource**. RTP
relaying, and especially transcoding between codecs (e.g. Opus ↔ G.711) or running large
conferences, is CPU-bound and is what actually caps a server. Strategies:

- **Avoid transcoding** wherever possible — negotiate a common codec end-to-end so
  Asterisk bridges natively (pass-through) instead of transcoding. This is the single
  biggest media-capacity win.
- **Scale media horizontally** by adding Asterisk nodes behind the proxy; each carries a
  share of the concurrent calls.
- **Offload browser media** to a dedicated WebRTC gateway (e.g. Janus) so the PBX is not
  also terminating and relaying every browser's DTLS-SRTP stream — see *WebRTC with
  Asterisk*, which discusses exactly this Asterisk-plus-gateway split.

Size capacity by **concurrent calls and transcoding load**, not by registered users —
10,000 registered phones that are mostly idle are far cheaper than 200 simultaneous
transcoded conferences.

## Cloud hosting

在云 VM（AWS、GCP、Azure、VPS）上运行 Asterisk 很常见且效果良好，但默认情况下**网络被 NAT 并防火墙保护**，这会与 SIP 冲突。以下是部署特有的注意事项。

### NAT and the SDP

云 VM 几乎总是拥有一个**私有**IP 在其网卡上，以及一个由提供商 NAT 到该私有 IP 的**公共**IP。如果 Asterisk 在 SDP 中广播私有 IP，远程电话会把 RTP 发送到黑洞——这就是经典的单向/无音频现象。告诉 PJSIP 它在传输层使用的公共身份：

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` 使 Asterisk 将它向公共对等方广播的地址改写为公共地址，而
`local_net` 告诉它哪些对等方是本地的（不应被改写）。这与上文讨论的桥接 Docker 网络的 NAT 处理相同——云 VM 实际上位于 NAT 之后。

### Firewall and the RTP range

云 VM 通常会有两个防火墙：**提供商**的安全组/网络 ACL，以及**主机**的 iptables。两者必须打开相同的端口，策略遵循《Security》章节的内容。已恢复的第一版规则集（`docs/legacy-labs/configs/Lab7/rules.v4`）概括了其形态——接受 SIP 和 RTP 范围，接受已建立/相关的连接，丢弃其余流量：

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

《Security》章节中对这里重要的两点修正：如果使用 SIP/TLS，**在 TCP 上打开 5061 端口**（而不是 UDP），并且记住防火墙中的 RTP UDP 范围必须与`rtpstart`/`rtpend`在`rtp.conf`中发布的范围完全一致——即容器中公布的同一范围。不要在此重复 iptables/Fail2Ban 的构建；**遵循 *Asterisk Security* 中防火墙、Fail2Ban 和 TLS/SRTP 部分的做法**（Fail2Ban 监视实验已在`logger.conf`中启用的 `security` 日志通道），并在*主机防火墙*和云安全组中都应用该策略。

### Latency, region and the SBC

- **选择靠近用户的区域。** 语音对延迟敏感——单向口到耳的延迟超过约 150 ms 就会被察觉。将 VM 部署在大多数电话和中继所在的最近区域；跨洲的媒体传输听感更差。
- **为任何面向互联网的部署放置 SBC。** **Session Border Controller** 在边缘终止 SIP/RTP，隐藏你的拓扑结构，规范 NAT，并在流量到达 Asterisk 之前吸收 DoS 与扫描流量。《Security》章节的核心建议——*不要将原始 Asterisk 暴露在互联网*——在云环境中更为重要，因为你的 VM 公共 IP 在启动几分钟内就会被扫描。SBC（或至少像 OpenSIPS 加 Fail2Ban 这样的加固 SIP 代理）是标准的边缘方案。

## Summary

部署是将可工作的 dialplan 变成可靠服务的阶段。在 VM 上，以 **非 root** 用户在 **systemd** 下运行 Asterisk，让单元的 `Restart=` 保持其存活（safe_asterisk 已被取代），并使用 `core reload` 而不是 `systemctl restart` 来应用配置更改。使用 Docker 进行 **容器化**——正如本书实验所示——可以得到一个不可变、固定的镜像，并通过 **绑定挂载** 将配置从 git 的 `/etc/asterisk` 中加载；关键在于媒体处理，因此要么使用 **主机网络**，要么发布一个 **完全匹配 `rtp.conf`** 的 RTP 端口范围，并挂载 **持久卷** 用于 spool/voicemail/astdb，以便状态在重新部署后仍然保留。将配置视为代码并 **备份状态**（配置本身不包含的内容）：voicemail、录音、`astdb.sqlite3`以及 CDR/CEL。**观察** 系统的四个层面——CLI（`core show channels`、`pjsip show endpoints`）用于实时视图，**CDR/CEL** 用于历史记录，**AMI/ARI** 用于编程事件，以及 **`res_prometheus`** 导出器到 Grafana 用于仪表盘和告警——同时保持 AMI/ARI 不暴露在公共互联网。要 **保持可用**，使用 **浮动 IP** 实现主动/备份（接受故障转移会中断实时通话）；要 **扩展**，使用 **PJSIP Realtime** 将状态外部化，使用 **OpenSIPS** 前置一池媒体服务器，并尽量减少转码，因为 **媒体——而非注册——是限制服务器的关键**。最后，在 **云** 环境中，将 VM 视为位于 NAT 后（`external_media_address`、`local_net`），按照安全章节在主机和提供商的安全组中打开防火墙，选择低延迟地区，并且永远不要直接暴露原始 Asterisk——在边缘放置一个 **SBC**。

## Quiz

1. 在 systemd 主机上，什么取代了旧的 `safe_asterisk` 包装器用于重新启动崩溃的 Asterisk 的工作？
   - A. 一个 cron 任务
   - B. 单元文件的 `Restart=` 指令
   - C. `systemctl enable`
   - D. astdb
2. 要在运行中的 Asterisk **不掉线**的情况下应用配置更改，您应该：
   - A. `systemctl restart asterisk`
   - B. 重启服务器
   - C. `asterisk -rx 'core reload'`
   - D. 重建容器镜像
3. 一个容器化（桥接网络）的 Asterisk 能连接通话但 **没有音频**。最可能的原因是：
   - A. dialplan 错误
   - B. 发布的 RTP UDP 端口范围与 `rtpstart`/`rtpend` 在 `rtp.conf` 中不匹配
   - C. CDR 被禁用
   - D. CLI 无法访问
4. 哪些目录必须挂载为 **持久卷**，以免容器重新部署时丢失状态？（全部选中）
   - A. `/var/spool/asterisk` （voicemail，recordings）
   - B. `/var/lib/asterisk` （astdb）
   - C. `/etc/asterisk` （已从主机绑定挂载）
   - D. `/usr/sbin`
5. 哪条 CLI 命令可以实时获取活动通话的计数？
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. 在 Asterisk 22 中，向 Prometheus/Grafana 堆栈公开呼叫/通道指标的支持方式是：
   - A. 解析 `full` 日志文件
   - B. `res_prometheus.so` 模块
   - C. AGI 脚本
   - D. 没有此功能
7. 对于 HA 故障转移和跨多个 Asterisk 节点的水平扩展，两者的前提条件是什么？
   - A. 以 root 身份运行
   - B. 将状态外部化（例如在共享数据库中的 PJSIP Realtime 注册）
   - C. 禁用 CDR
   - D. 使用桥接网络
8. 哪项资源最直接限制单个 Asterisk 服务器能够处理的并发通话数量？
   - A. 注册用户的数量
   - B. 媒体处理，尤其是转码
   - C. `/etc/asterisk` 的大小
   - D. CDR 后端
9. 在云 VM 上，哪些 `pjsip.conf` 传输设置使 Asterisk 广播其公网地址，从而远程音频能够工作？（全部选中）
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. 对于面向互联网的云部署，Security 章节的核心规则是：
    - A. 始终使用两块 NIC
    - B. 永不直接将原始 Asterisk 暴露到互联网；在边缘放置 SBC（或加固的代理 + Fail2Ban）
    - C. 只使用 UDP
    - D. 禁用 TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
