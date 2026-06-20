# Asterisk Security

自始至终，Asterisk 的安全问题都是至关重要的。根据 CERT.BR 的统计，SIP（Session Initiation Protocol）是互联网上最常受到攻击的协议。任何运行蜜罐的人都可以证实这一点。互联网收入分成欺诈（Revenue Share Fraud）问题非常严重，可能导致数十万美元以上的损失。绝不能在未采取适当安全措施的情况下将 Asterisk 服务器直接连接到互联网。在本章中，您将学习如何识别可能遭受的主要攻击类型，以及如何通过恰当的安全策略加以防范。最后，您还将学习如何实现本文建议的安全策略。

本章针对 **Asterisk 22 LTS**，其中 PJSIP（`res_pjsip` / `chan_pjsip`）是唯一的 SIP 通道。（旧的 `chan_sip` 驱动已在 Asterisk 21 中移除——如果您正在迁移旧系统，请参阅 *Legacy Channels* 章节。）一个与安全相关的后果是：失败的认证现在通过 Asterisk **security event framework** 和专用的 `security` 日志通道发出，这会改变 Fail2Ban 的配置方式（将在本章后面介绍）。

## 目标

通过本章学习，您应该能够：

- 识别常见的针对 Asterisk 服务器的攻击类型
- 制定有效的安全策略
- 实施安全策略
- 为 Asterisk 安装并配置 IPTABLES
- 为 Asterisk 安装并配置 Fail2Ban
- 为加密安装并配置 TLS 和 SRTP

## IP 电话的主要攻击

IP电话的主要攻击可以分为 DOS/DDOS、服务盗用/计费欺诈和窃听。某些名称可能会让人困惑，不同来源有时会为同一种攻击使用不同的名称。服务盗用、计费欺诈、互联网收入分成欺诈、电话欺诈是黑客利用您的 PBX 向高价号码发送流量并从运营商获取返利的不同叫法。

### DDoS/DOS

拒绝服务（Denial of Service）和分布式拒绝服务（Distributed Denial of Service）是针对任何 IT 基础设施的常见攻击。SIP 以及其他基于 IP 的语音协议也不例外。分布式拒绝服务通常由僵尸网络（botnet）实施，而普通的 DOS 则可能仅由单台计算机发起。2011 年 2 月，Sality 僵尸网络对整个 IPv4 地址空间进行了一次隐蔽且协调的扫描，以寻找易受攻击的 SIP 服务器——观察 UCSD 网络望远镜的研究人员将其归因于大约三百万个不同的源 IP，对 UDP 5060 端口进行探测，最可能的目的是对 SIP 账户进行暴力破解以进行计费欺诈。[^sality]

[^sality]: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![一个点对点僵尸网络向服务器发起数千次 SIP 注册尝试](../images/19-security-fig01.png)

DOS 通常通过模糊测试和洪水攻击等技术实现。洪水攻击可以使用 SIP、IAX、RTP 等协议。它们可能会完全停止服务或降低语音质量。如果端口对 Internet 开放，这类攻击非常难以缓解。以下是攻击者使用的一些工具

**模糊测试：**

- **PROTOS Test Suite (c07-sip)** — 来自芬兰奥卢大学 OUSPG。发送数千个畸形数据包，以触发诸如导致软件停止的缓冲区溢出等故障。  
- **Voiper** — 生成超过 200,000 条测试，覆盖所有 SIP 属性，并验证您的服务器是否能够有效处理这些消息。 <http://voiper.sourceforge.net/>

**洪水攻击：**

- **INVITE Flooder** — 对服务器进行 SIP INVITE 请求的洪水攻击。 <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — 对服务器进行 IAX2 流量的洪水攻击。 <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — 对活跃的媒体会话发送 RTP 包，以降低语音质量。 <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### DoS/DDoS 缓解技术

我的建议是

1. 不要在互联网公开你的 Asterisk 服务器，除非在必要且有适当保护的情况下（SBC）
2. 在内部网络中为语音使用虚拟局域网，尤其当你在用户数量众多的大学、学院时。
3. 对外访问请使用 VPN 或 TLS。

### 互联网收入分成欺诈

这类欺诈有点难以理解。关键是要了解国际增值费号码（International premium rate number，IPRN）的概念。

![互联网收入分成欺诈的三个步骤：购买高价号码，找到易受攻击的VoIP设备并拨打该号码，然后收取付款](../images/19-security-fig02.png)

IPRN 是一种可以在某些特定互联网电话公司免费分配的号码。搜索 “Internet Premium Rate Number Providers”，你会找到一大批提供商。在这种运营商中，你可以分配例如在 Iridium 卫星网络上的号码，呼叫者每分钟需支付数十分之一美元的费用。IPRN 提供商会将收入的一定比例（10% 到 20%）返还给你。

![IPRN提供商价目表，显示各国付款率和测试号码](../images/19-security-fig03.png)

在分配阶段之后，黑客尝试寻找任何能够拨打已分配 IPRN 的开放 Asterisk 服务器。受害者的 PBX 在黑客的控制下，会向该 IPRN 号码发起数百个呼叫，为黑客产生巨额回报，同时给受害者带来巨额电话费用。很多情况下，单个周末的费用甚至超过数十万美元。

黑客攻击 PBX 时使用的主要工具：

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious 是一套易于使用的安全工具。其主要目标是识别易受攻击的 PBX 并通过暴力破解攻击来破解 SIP 密码。最常用的工具是 svcrack。该工具能够每秒测试数千个密码。  
2. **Phone vulnerabilities**。黑客常用的另一攻击向量是电话本身。许多安装 Asterisk 的用户没有更改电话网页界面的默认密码。这些电话一旦在 Internet 上开放，黑客就可以尝试使用默认的界面密码下载配置文件，进而常常找到隐藏的 SIP 密码。

#### TFTP盗窃:

如果您使用 TFTP 自动配置电话，您可能会对这种攻击方式敞开大门。TFTP 是一种简单且不安全的文件传输协议。

![攻击者从 TFTP 服务器下载可猜测的 .cfg 文件，收集配置文件中的明文凭证】(../images/19-security-fig04.png)

配置文件的名称很容易通过 MAC 地址加上 .cfg（例如 001A2B3C4D5E.cfg）来猜测。聪明的黑客可以轻松编写一个实用程序，顺序尝试所有 MAC 地址，或直接下载工具来完成此操作。配置文件通常未加密，且其中包含秘密 SIP 密码。

#### 针对暴力攻击和 tftp 窃取的缓解措施

为了缓解这些攻击，您可以采用以下解决方案。

**暴力破解**：缓解暴力破解攻击的最佳方案是防止连续的未授权尝试。几乎所有的 Asterisk 安装程序都使用 fail2ban 实用工具。当 fail2ban 检测到多次使用错误密码或用户名的尝试时，它会在一定时间内封禁攻击者的 IP。针对暴力破解的第二项措施是使用强密码，长度超过 12 个字符，且至少包含一个特殊字符。

**TFTP 窃取**：为了防止 TFTPTheft，请将配置设置为使用 https 并配合用户名和密码。文件将在加密通道中传输，用户名和密码可以阻止攻击者尝试下载任何文件。

### 窃听

我们很少看到此类攻击，因为在大多数情况下它们根本没有被检测到。 在 IP 环境中，窃听非常难以发现。 像 UCsniff 这样免费提供的工具能够在大多数网络中窃听 VoIP 通话。 主要的技术是使用 ARP 欺骗，将流量强制通过运行 UCsniff 的计算机并记录通话。

#### 防止窃听的缓解措施

您可以通过加密 VoIP 流量来防止窃听。另一种方法是防止网络中的中间人（MITM）攻击。ARP 检查在第 2 层网络中防止 MITM 非常有效。请咨询您的网络技术支持，了解如何实施。稍后在本书中，我们将学习如何基于 TLS 和 SRTP 安装加密。您也可以使用 ARPWatch 来发现是否有人正在滥用 ARP 协议攻击您的网络。

## Security policy for Asterisk

实现安全的最佳方式是制定安全策略。针对本培训，我将为大多数 Asterisk 部署建议一套安全策略。请以此为基础，根据实际需求进行调整。以下是建议的安全策略：

1. 不打开任何不必要的 UDP/TCP 端口
2. 不在 Internet 上开放任何管理界面（SSH/HTTPS）的访问
3. 对于 SSH 和/或 HTTP/HTTPS 的访问，应在 IPTABLES 防火墙中设置明确的例外
4. 使用至少 12 位且包含特殊字符的强密码
5. 使用 Fail2ban 对认证失败超过 10 次的 IP 地址进行封禁
6. 国际呼叫需要密码确认
7. 将 SIP 端口的访问限制在已知的 IP 地址范围内

如果需要对 PBX 进行外部访问，有两种方案。可以使用 SBC（Session Border Controller）来防御 DOS/DDOS 攻击，或在需要外部访问时使用 VPN。如果在 Internet 上开放 5060 端口而未使用 SBC 或 VPN，则会面临 DOS/DDOS 攻击的风险，后果自负。

### PJSIP-era hardening (Asterisk 22)

除了防火墙和 Fail2Ban，Asterisk 22 的 PJSIP 栈还提供了若干配置层面的控制，应纳入安全策略。这些是对上述网络控制的补充（而非替代）：

- **Per-endpoint authentication.** 每个 endpoint 应引用一个专用的 `type=auth` 节，并使用强且唯一的 `password`（`auth_type=digest`）。切勿在不同 endpoint 之间复用凭证。
- **Anonymous handling is built in.** 当认证失败时，PJSIP 不会透露用户名是否存在。若要接受匿名呼叫，必须显式创建名为 `anonymous` 的 endpoint，并使用 `type=identify` 节（基于源 IP 匹配）将已知对等方映射到 endpoint。如果不希望匿名呼叫，只需不要创建 `anonymous` endpoint，未匹配的请求将被挑战/拒绝。
- **ACLs.** 使用 `/etc/asterisk/acl.conf` 命名的 ACL 限制能够访问 endpoint 的对象，在 endpoint 中通过 `acl=`（信令/源 ACL）和 `contact_acl=`（限制 contact/registration 地址）引用。也可以直接在 endpoint 上设置 permit/deny。
- **`qualify`.** 在 AOR 上设置 `qualify_frequency`（以及 `qualify_timeout`），使 Asterisk 主动监控已注册 contact 的可达性并清除失效的条目。
- **PJSIP transport hardening / DoS protection.** `type=transport` 并未提供每个传输的客户端上限，因此连接洪泛的防护依赖防火墙（本章节中的 iptables/Fail2Ban 规则），而非 PJSIP 选项。传输层能够提供的功能包括 TCP keep-alive 调优（`tcp_keepalive_enable`、`tcp_keepalive_idle_time`、`tcp_keepalive_interval_time`、`tcp_keepalive_probe_count`）以回收死连接/半开连接，以及 `local_net`/`external_*` 设置以实现正确的 NAT 处理。将这些与防火墙规则结合使用，可削弱连接洪泛攻击。
- **TLS + SRTP for media.** 在 endpoint 上使用 TLS 传输加密信令，使用 `media_encryption=sdes`（或 WebRTC 的 `dtls`）加密媒体——后文将详细说明。
- **AMI/ARI access control.** 将 Asterisk Manager Interface（`manager.conf`）和 ARI（`ari.conf` / `http.conf`）的访问限制在本地主机或受信任的管理网络，使用强且唯一的 secret，将 HTTP 服务器绑定到私有接口，切勿将其暴露到 Internet。

上述所有选项名称均已在 Asterisk 22.10 中确认：`type=transport` 节公开了 `tcp_keepalive_enable`、`tcp_keepalive_idle_time`、`tcp_keepalive_interval_time`、`tcp_keepalive_probe_count`、`tos`、`cos`、`local_net`以及 `external_*` 系列，但 **没有** `max_clients` 选项——连接洪泛防护来自防火墙，而非传输层。`acl`和`contact_acl` endpoint 选项从 `acl.conf` 中获取节名，未认证对等方的源 IP 匹配通过 `type=identify` 节（`match=`）实现。

### Removing unnecessary

```
netstat -pantu |grep asterisk
```

The output of the command is shown below.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

If you look at the output, you will discover that many ports are open. Do we need them? Not necessarily, 2727 is the MGCP protocol (chan_mgcp), 4569 is the IAX (chan_iax2). If you are not using these protocols, you can simply remove the module in the configuration file modules.conf.

You may notice Asterisk binding a high-numbered UDP port. This comes from `res_pjsip`'s resolver making outbound DNS queries (the source port is ephemeral, like any client DNS lookup), not from an inbound listener — your firewall only needs to allow **established/related** return traffic for it (the iptables `conntrack ESTABLISHED,RELATED` rule shown below already covers this). You do **not** need to open a wide inbound high-UDP range just for PJSIP DNS.

To remove the unnecessary ports, disable the modules you don't use. Edit the file modules.conf and add `noload` lines for the channels and protocols you are not using. **Do not** noload `res_pjsip`, `res_pjproject`, or `chan_pjsip` — those are required for SIP in Asterisk 22:

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

（在 Asterisk 22 中，您不再需要 noload `chan_mgcp`或 `chan_skinny`——这些驱动已在 Asterisk 21 中*移除*，并且不在标准的 22 构建中。）按照上述说明，我已删除所有不必要的通道，仅保留 PJSIP。您可以选择想要的任何协议模块，只需删除未使用的即可。结果如下截图所示——现在仅有由您的 PJSIP 传输绑定的 SIP 端口（5060）对外开放。

![禁用未使用模块后的 netstat 输出：仅有 UDP 端口 5060 被 Asterisk 绑定](../images/19-security-fig06.png)

### 使用 IPTABLES 实现安全策略

IPTABLES 或 netfilter 是大多数 Linux 发行版中标准的防火墙。本实验将配置 iptables 和 fail2ban。目标是实现 Asterisk 推荐的安全策略，阻止所有不必要的流量。按以下步骤操作：

1. 阻止所有外部流量  
2. 允许来自内部网络或单个主机的 SSH 流量  
3. 允许 UDP 和 TCP 的 SIP 流量，端口 5060  
4. 允许 UDP 媒体端口范围的 RTP 流量。没有单一的内置默认值——当未设置时，Asterisk 的 `rtp.conf` 会回退到 5000–31000 端口，但随附的 `rtp.conf.sample` 将 `rtpstart=10000` / `rtpend=20000` 配置为其他范围，因此这里使用该示例范围。请将防火墙规则匹配到您在 `rtp.conf` 中实际设置的 `rtpstart`/`rtpend`。

确保您可以通过控制台访问服务器，避免将自己锁在系统之外。小心操作。

1. 安装软件包 net-persistent。```
   sudo apt-get install iptables-persistent
   ```

2. 允许来自环回接口的所有流量```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. 允许已建立的连接```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

4. Allow SSH/HTTPS traffic from the network 192.168.0.0

--- END MARKDOWN ---```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. 插入 Asterisk 规则```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

请注意，端口 5061（SIP over TLS）使用 **TCP**，而不是 UDP。上面的规则在 UDP 和 TCP 上都打开了 5060，在 TCP 上打开了 5061。如果您只运行 TLS，可以完全删除普通的 5060 规则。仅打开您的 PJSIP 传输实际绑定的端口。

`-I` means PREPEND

6. 最后一个规则必须是 drop```
   sudo iptables -A INPUT -j DROP
   ```

`-A` 表示 APPEND。  
注意：在维护新规则时要小心，必须在 DROP 之前添加规则。使用 PREPEND 添加新规则 `-I`

7. 保存规则并重启 iptables```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### 使用 Fail2Ban 阻止多次身份验证失败尝试

Fail2Ban 几乎已经成为 Asterisk 的标准配置。大多数用户都会实现它以增强安全性。该工具会扫描 Asterisk 日志中的失败尝试并封禁攻击者的 IP 地址。下面提供 Fail2Ban 的安装说明。

在 Asterisk 22 中，PJSIP 通过 Asterisk **security event framework** 报告失败的身份验证和其他安全事件，这些事件写入专用的 **`security`** 记录通道。要使 Fail2Ban 工作，必须：

1. 在 `/etc/asterisk/logger.conf` 中启用安全通道。语法为 `<filename> => <levels>` ，因此要将安全级别写入名为 `security` 的文件，请写入：

```
[logfiles]
security => security
```

then run `logger reload` from the CLI. This produces `/var/log/asterisk/security` with one line per security event, in the form:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

The events Fail2Ban cares about are `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID`, and `FailedACL`, each carrying a `RemoteAddress="IPV4/UDP/<ip>/<port>"` field that identifies the offender. (Note the address is wrapped as `IPV4/UDP/.../...`, not a bare IP — your filter must extract the host from inside that string.)

2. Point the `asterisk` jail at that file (`logpath = /var/log/asterisk/security`) and use a filter that parses this security-event format.

Modern Fail2Ban ships an `asterisk` filter whose `failregex` already matches the events above and extracts `<HOST>` from the `RemoteAddress` field, for example:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX 发行版（FreePBX/Sangoma）提供等效的过滤器。优先使用包装好的过滤器，而不是手动编写，因为确切的事件字符串会随版本而变化。需要注意的一点是：一个已修补的安全通报（GHSA-5743-x3p5-3rg7）显示，构造的 PJSIP 流量可能注入伪造的日志行——请保持 Asterisk 和 Fail2Ban 过滤器均为最新。

下面提供 Fail2Ban 的安装说明

1. 在 Linux 上安装 fail2ban```
   sudo apt-get install fail2ban
   ```

## 2. 为 Asterisk 和 SSH 激活 fail2ban```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

   添加以下行以激活 fail2ban 对 ssh 和 asterisk 的保护

  ```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. 重启 fail2ban```
   /etc/init.d/fail2ban restart
   ```

4. 验证。更改软电话的密码并尝试重新注册 10 次。使用`iptables -L`检查软电话地址是否被列为阻止的地址。  
5. 将该地址从封禁中移除（假设地址为 192.168.0.5）```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

注意：在命令中将 192.168.0.5 替换为您手机的 IP 地址

### 实现 TLS 和 SRTP

我将本节分为两部分。第一部分我们将介绍用于加密信令的 TLS，第二部分则是用于加密媒体的 SRTP。此处的目标是为这些资源配置 Asterisk。

#### TLS

TLS（传输层安全）是为保护 SIP 信令而定义的加密机制。下表概括了 TLS 能防御的攻击类型：

| Type of attack | Protected? | Notes |
|----------------|-----------|-------|
| Signaling attacks | Yes | TLS assures the integrity of the messages |
| Man in the middle | Yes | TLS checks the server certificate |
| Eavesdropping | No | TLS encrypts signaling, not media |

对于媒体（语音/视频）加密，请使用 SRTP。

#### 自签名数字证书

证书有两种类型：自签名和商业证书。自签名证书由您自己的服务器签署，而商业证书则由外部机构签署。对于 VoIP，您可以自行充当证书颁发机构。无需使用 GoDaddy、Verisign 等外部证书，这会产生不必要的费用。我们将使用 `ast_tls_cert` 生成自己的证书。

#### 使用自签名证书配置 TLS

下面是一份逐步指南，说明如何实现 TLS。我们首先生成证书，然后配置 PJSIP TLS 传输（参见 “Configuring TLS with chan_pjsip”），最后在软电话中指向该传输。我们将使用 SipPulse Softphone，它原生支持 TLS 和 SRTP。（任何支持 TLS/SRTP 的 SIP 软电话都可以以相同方式使用。）

**Step 1.** 使用 3DES 加密、4096 位长度创建 RSA 私钥，用作我们的证书颁发机构。下面的命令位于 `/usr/src/asterisk-22.x.y/contrib/scripts`，将创建证书颁发机构和 Asterisk 证书。根据实际情况调整说明，版本和目录可能会变化。请注意您正在执行的操作。使用您的域名或 IP 地址作为 `-C` 选项的参数。`ast_tls_cert` 命令有三个选项。

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 2048 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

我不会生成客户端证书，因为我们不打算使用证书来对客户端进行身份验证。客户端不需要提供自己的证书。

**Step 2.** 配置 Asterisk 以在 TLS 上支持我们的客户端。这在 `pjsip.conf` 中完成（一个 TLS 传输加上端点设置）——完整配置在下一节 “Configuring TLS with chan_pjsip” 中展示。我们不使用证书进行身份验证，只是对流量进行加密。

**Step 3.** 安装支持 TLS 的 SIP 软电话（作者使用 SipPulse Softphone）。

**Step 4.** 将证书颁发机构复制到运行软电话的计算机上。安装后，如果使用自签名证书，将文件 `/etc/asterisk/keys/ca.crt` 复制到运行软电话的计算机（使用 scp，或在 Windows 上使用 WinSCP）。

**Step 5.** 在软电话中创建账户。在账户界面像其他 sip 账户一样正常添加账户。使用正确的密码，认证仍然基于密码。

**Step 6.** 在账户设置中将传输方式设为 TLS。在 SipPulse Softphone 账户界面（如下）中，选择 **TLS** 作为传输并使用 5061 端口。调整防火墙以打开 TCP 5061 端口。

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** 信任证书颁发机构。如果你的 Asterisk TLS 证书由公共 CA（例如 Let’s Encrypt —— 参见 *Deployment* 章节）签署，现代软电话如 SipPulse Softphone 会通过系统证书存储自动信任，无需手动导入。如果使用自签名证书，将其 CA（`/etc/asterisk/keys/ca.crt`）导入客户端或操作系统的信任存储，或在提示时接受它。

**Step 8.** 你 **不** 需要客户端证书。一个常见的误解是每部电话都需要自己的证书进行身份验证——事实并非如此。此时 Asterisk 只对会话进行 *加密*；认证仍然是用户名和密码。Asterisk 默认不验证客户端证书，因此无需分发每个客户端的证书。

**Step 9.** 更改证书或传输方式后，完全重启软电话（退出并重新启动，而不是仅关闭窗口），以便它通过新传输重新连接。

### Configuring TLS with chan_pjsip

现在让我们学习如何为 TLS 配置 PJSIP。PJSIP 是 Asterisk 22 中唯一的 SIP 通道，所以无需切换——只需确保 `res_pjsip`、`res_pjproject` 和 `chan_pjsip` 已加载。步骤 1：确认在 /etc/asterisk/modules.conf 中已启用 PJSIP。

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

步骤 2：配置 PJSIP 以支持 TLS。 在文件 /etc/asterisk/pjsip.conf 中添加 TLS 传输的章节

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

使用 `method=tlsv1_2`（如果您的 OpenSSL/PJSIP 构建支持，则使用 `tlsv1_3`）——TLS 1.0/1.1 已过时且不安全，不应使用。

步骤 3：为 blink 配置端点。编辑 `pjsip.conf` 并编辑 blink 部分。让 PJSIP 自动选择传输方式。

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

步骤 4：验证。要验证注册是否通过 TLS 进行，请在 Asterisk 控制台中使用以下命令。

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### 使用 SRTP 进行安全通话

负责媒体加密的协议是 RFC3711 中定义的 Secure Real Time Protocol (SRTP)。该协议的一个缺点是缺乏标准化的密钥交换方式。Asterisk 使用通过 TLS 提供的信令加密保护的 SDP 协议进行 SDES 密钥交换。还有其他方法，例如 MIKEY 和 ZRTP。ZRTP 由 Philipp Zimmermann 开发，是最复杂的密钥交换和媒体加密方法之一。一些软电话和硬电话支持 ZRTP。然而，标准方式仍然是 SDES，您几乎可以在市场上任何可用的电话中找到这种方法。下面是一个请求示例，其中在 SDP 的 a=crypto:1 和 a=crypto:2 行中定义了加密密钥。

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### 在 Asterisk 上配置 SRTP

要在 Asterisk 上配置 SRTP 非常简单。 在端点上设置 `media_encryption=sdes`；您也可以使用 `media_encryption_optimistic=no` 来强制要求，这样未加密的媒体将被拒绝，而不是被静默允许。 请注意，SDES 需要信令通过 TLS 进行，以防止密钥以明文方式传输。

**Step 1.** Asterisk 配置

在 `pjsip.conf` 中的 `type=endpoint` 部分设置以下内容：

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

**Step 2.** Softphone 配置

In the softphone, enable SRTP for the account media (set the **SRTP (Media Encryption)** option to *Mandatory*) so that voice is encrypted.

![SipPulse 软电话账户设置（下部）— 将 **Transport** 设置为 TLS 并将 **SRTP (Media Encryption)** 设置为 *Mandatory*，以便信令和媒体均被加密.](../images/softphone/sipphone-config.png){width=35%}

## 启用国际呼叫的双因素认证

有时最好的办法是根本不使用国际路由。不过，如果确实需要拨打国际电话，可以使用额外的密码。我们将使用 Asterisk 应用 vmauthenticate 在拨打国际电话前要求输入语音信箱密码。这在 extensions.conf 的 dialplan 中进行配置。请参见下面的示例。因此，即使黑客已经获取了对等密码或入侵了电话，仍然需要语音信箱密码才能拨打此目的地。

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate`仍然是 Asterisk 22 中的标准应用。上面的`Dial()`将呼叫通过 SIP/PJSIP 中继（`PJSIP/<number>@<trunk>`）路由，这也是大多数现代安装连接 PSTN 的方式——将`my_trunk`改为您自己的中继名称，并且仅在实际拥有 DAHDI span 时使用`DAHDI/g1/...`。在 dialplan 中的防止收费欺诈——像这样的第二因素，加上限制哪些 context 可以访问您的出站和国际路由——仍然是您可以部署的最重要的防护措施之一。

## 摘要

在本章中，您了解了将 IP PBX 连接到互联网所带来的风险。随后我们学习了如何通过实施安全策略来保护 PBX。在此安全策略中，我们实现了 iptables、fail2ban、TLS、SRTP 以及国际呼叫的双向认证。希望您喜欢本章内容。

## 测验

1. 防止互联网收入分成欺诈的最重要对策是什么？
   - A. 实施 SRTP
   - B. 保持 Asterisk 更新
   - C. 实施 TLS
   - D. 使用强密码
2. SIP 模糊测试的定义是：
   - A. 使用畸形请求和响应的 DoS 攻击
   - B. 通过暴力破解密码进行的服务盗窃
   - C. 对当前通话进行窃听
   - D. 使用大量 SIP 请求的 DDoS 攻击
3. 当服务器通过 TFTP 提供配置文件时会出现 TFTPTheft。可以通过以下方式避免：
   - A. FTP
   - B. HTTP
   - C. 使用用户名和密码的 HTTPS
   - D. SCP
4. 中间人攻击使用的技术称为：
   - A. TFTP theft
   - B. ARP 欺骗
   - C. MAC 中毒
   - D. dsniff
5. 对于 SRTP，Asterisk 使用以下系统交换密钥：
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. 在 `/usr/src/asterisk-22.x.y/contrib/scripts` 中找到的用于生成证书颁发机构和证书的实用工具是：
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. 防止窃听的有效策略（勾选所有适用项）：
   - A. 实施模拟窃听检测器
   - B. 使用 ARPwatch 实用工具检测 ARP 欺骗
   - C. 在交换机上启用 ARP 欺骗检测
   - D. 使用 SRTP
8. Asterisk 通过验证客户端证书支持强身份验证。（PJSIP TLS 传输可以要求并验证客户端的证书。）
   - A. 正确
   - B. 错误
9. 在 Asterisk 22 中，哪个 PJSIP 端点设置通过 SDP 中的（SDES）密钥开启 SRTP 媒体加密？
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. 在 Asterisk 22 中，Fail2Ban 必须从专用的 ________ 记录器通道读取 PJSIP 失败认证事件（在 `logger.conf` 中启用）。
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**答案：** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
