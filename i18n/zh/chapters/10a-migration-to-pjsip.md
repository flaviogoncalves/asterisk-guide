# 从 chan_sip 迁移到 PJSIP：实战指南

如果您正在阅读本章，且您的 Asterisk 13、16 或 18 系统仍在生产环境运行，那么您已经面临最后期限。`chan_sip`——通过 `sip.conf` 配置的原始 SIP 通道驱动程序——在 **Asterisk 17 中被弃用，在 Asterisk 19 的默认构建中被移除，并在 Asterisk 21 中被彻底删除**。它在 Asterisk 22 LTS 中已不存在。没有任何标志可以重新开启它，没有 `noload` 可以规避，也没有软件包可以安装。Asterisk 22 中唯一的 SIP 通道驱动程序是 **PJSIP**（`res_pjsip` 加上 `chan_pjsip`），通过 `pjsip.conf` 进行配置。

因此，对于大多数站点而言，升级到 Asterisk 22 不仅仅是版本更新，更是一个 *SIP 迁移项目*。好消息是，线路上的协议并没有改变——昨天可以注册和通话的电话，明天依然可以注册和通话——而且 Asterisk 提供了一个转换工具，可以为您完成 80% 的转换工作。本章是一份实用的操作指南：概念映射、转换脚本、针对您实际情况的 `sip.conf` → `pjsip.conf` 并排翻译、迁移带来的 dialplan 和 CLI 变更、realtime（数据库）迁移，以及一份检查清单和容易踩的坑。

此处的所有内容均已针对本书的 Asterisk 22.10.0 实验环境进行了验证。关于 `chan_sip` 本身的深度遗留资料，以及多设备 `sip.conf` 的完整端到端转换示例，请参阅 *Legacy channels* 一章；本章是其专注的、食谱式的配套指南。

## 目标

读完本章后，您应该能够：

- 解释为什么 `chan_sip` 在 Asterisk 22 中被移除以及它的替代方案是什么
- 将 `sip.conf` 的 peer/user/friend 模型映射到 PJSIP 对象模型（endpoint + aor + auth + identify + transport + registration）
- 运行 `sip_to_pjsip.py` 转换脚本并批判性地审查其输出
- 手动将常见设备类型（注册电话、入站 trunk、出站注册）从 `sip.conf` 翻译为 `pjsip.conf`
- 逐项迁移 NAT、媒体、DTMF、codec 和身份验证设置
- 更新 dialplan（`SIP/` → `PJSIP/`）和 CLI（`sip show` → `pjsip show`）
- 将 realtime/ARA 部署从 `sippeers`/`sipregs` 迁移到 Sorcery `ps_*` 表
- 执行迁移检查清单并避免经典陷阱

## 为什么要迁移

`chan_sip` 为 Asterisk 服务了近二十年，但它背负着架构债务：单一的单体模块、每个设备一个配置块、薄弱的多传输支持，以及一个落后于 RFC 标准的 SIP 栈。**PJSIP**——基于 Teluu 成熟的 pjproject 栈并于 Asterisk 12 引入——是彻底的替代品。到 Asterisk 21 时，Asterisk 项目完成了这项工作并从代码树中移除了 `chan_sip`。

您可以在任何 Asterisk 22 系统上确认这一情况：

```
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

`chan_sip` 返回 *0 modules loaded*——它根本不存在。除了 PJSIP，没有其他可迁移的目标，所以唯一真正的问题是 *如何* 迁移，而不是 *是否* 迁移。

## 概念映射：不存在单一的 "peer"

对于所有从 `sip.conf` 迁移过来的人来说，最容易产生误解的思维转变是：**PJSIP 没有 `[peer]`。** 在 `sip.conf` 中，一个带括号的块——一个 `peer`、一个 `user` 或一个 `friend`——描述了关于设备的一切：它的凭据、在哪里联系它、它的 codec、它的 NAT 行为、它的 dialplan context。PJSIP 有意将那个单一的块拆分为几个更小的、单一用途的对象，每个对象都用 `type=` 标记，并 *通过名称相互引用*：

| PJSIP 对象 (`type=`) | 职责 |
| --- | --- |
| `endpoint` | 设备的呼叫处理身份：codec、context、DTMF、媒体、NAT，以及对 `auth`/`aors`/`transport` 的引用 |
| `aor` (Address of Record) | *在哪里* 联系设备——注册或静态联系人、`max_contacts`、qualify |
| `auth` | 用于入站和/或出站身份验证的凭据（用户名/密码） |
| `identify` | 通过 **源 IP** 而不是 `From` 用户名将入站请求匹配到 endpoint |
| `transport` | 监听套接字：协议、绑定地址/端口、NAT/外部地址 |
| `registration` | 从 Asterisk 到服务商的 **出站** REGISTER |

`friend`/`peer`/`user` 的区别完全消失了——在 PJSIP 中，一切都是一个 `endpoint`。因此，一个单一的 `sip.conf` friend 通常会变成三个共享名称并相互指向的对象（`endpoint` + `auth` + `aor`）：

```
                sip.conf                              pjsip.conf
            ┌──────────────┐              ┌──────────┐   ┌──────┐   ┌─────┐
            │   [2000]     │   becomes    │ endpoint │──▶│ auth │   │ aor │
            │ type=friend  │  ─────────▶  │  [2000]  │   │[2000]│   │[2000]│
            │ host=dynamic │              │  auth=───┼──▶└──────┘   └──────┘
            │ secret=...   │              │  aors=───┼───────────────▶ ▲
            └──────────────┘              └────┬─────┘
                                               │ transport=
                                               ▼
                                          ┌───────────┐
                                          │ transport │  (shared by all endpoints)
                                          └───────────┘
```

endpoint 是粘合剂。它命名一个 `transport`（或继承默认值）、一个 `auth` 对象以及一个或多个 `aors`。对象模型在 *SIP & PJSIP in depth* 中有深入介绍；在这里，我们只需要将其作为每次翻译的目标。

## `sip_to_pjsip.py` 转换工具

Asterisk 提供了一个 Python 脚本，用于读取现有的 `sip.conf` 并写入 `pjsip.conf`。它不是作为 CLI 命令运行的——它位于 **Asterisk 源代码树** 中，而不是已安装的二进制文件中：

```
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

在实验室的 Asterisk 22.10.0 上，完整路径例如为 `/usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py`。同一个目录中还包含 `sip_to_pjsql.py`（realtime/SQL 变体，稍后介绍）以及辅助模块 `astconfigparser.py`、 `astdicts.py` 和 `sqlconfigparser.py`。

### 运行脚本

该脚本接受可选的位置参数——`[input-file [output-file]]`——默认为当前目录下的 `sip.conf` 和 `pjsip.conf`：

```
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

它仅有的几个选项是：

```
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

它读取输入，打印 `Converting to PJSIP...`，并写入输出文件。在内部，它会遍历每个 `sip.conf` 部分，并为每个设备生成匹配的 `endpoint`、 `auth`、 `aor`、 `registration` 以及（在可以推断出的情况下） `transport` 对象，自动应用下一节中的选项映射。

### 它的作用及其局限性

请将输出视为 **初稿，而非最终文件。** 该脚本对其自身的缺陷非常坦诚：任何无法清晰映射的内容都会被写入输出文件顶部的一个清晰的围栏块中：

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[zoiper]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

注意在那个真实的片段中，来自 `sip.conf` peer 的 `qualify = yes` 落入了 *未映射* 块中——因为 PJSIP 是通过 `qualify_frequency`（秒）在 **aor** 上进行 qualify 的，而不是设备上的布尔值，所以脚本将其留给您自行设置。需要规划的实际局限性包括：

- **传输方式是猜测的，而非设计的。** 脚本会从 `bindport`/`bindaddr` 生成一个基本的 `transport-udp`，但它无法获知您的 TLS 证书、TCP 需求或多绑定布局。请审查并重写传输配置。
- **NAT 和外部地址需要人工干预。** `externaddr`/`localnet` 可能无法完美保留；请手动确认传输上的 `external_media_address`、 `external_signaling_address` 和 `local_net`。
- **`qualify`、自定义计时器和少数选项会落入 "non-mapped" 中。** 请从头到尾阅读该块并逐一决定。
- **Codec 列表、context 和安全性需要审查。** 验证 `disallow`/`allow`、dialplan `context`，并确保没有设备被无意中暴露。

因此，工作流程是：将脚本运行到 *临时* 文件中，进行 diff 和审查，将好的部分合并到您的真实 `pjsip.conf` 中，然后在投入生产前进行详尽测试。

## 并排翻译

以下是操作指南。左侧是 `sip.conf`，右侧是经过验证的 `pjsip.conf` 等效项（此处为适应页面宽度而堆叠）。右侧的每个选项名称和值都已使用 Asterisk 22 实验室环境进行了 `config show help res_pjsip ...` 验证。

### 注册电话 (`host=dynamic`)

最常见的设备：使用密码登录并注册其自身位置的桌面电话或软电话。

**遗留 `sip.conf`：**

```
[2000]
type=friend
host=dynamic
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmfmode=rfc2833
secret=Sup3rSecret
qualify=yes
```

**Asterisk 22 `pjsip.conf`：**

```
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
auth=2000
aors=2000

[2000]
type=auth
auth_type=digest
username=2000
password=Sup3rSecret

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

关键步骤：`host=dynamic` 变为带有 `max_contacts` 的 `aor`（设备 REGISTER 以填充其联系人）；`secret=` 变为 `type=auth` 内的 `password=`；`qualify=yes` 变为 **aor** 上的 `qualify_frequency=60`（秒），而不是 endpoint 上的。仅当您确实希望同一账号同时在多个设备上使用时，才将 `max_contacts` 设置为大于 1 的值。

### 入站 trunk (`host=<ip>` / `type=peer`)

从已知 IP 地址向您发送呼叫的服务商。这里没有注册——您使用 `identify` 通过 *源 IP 对运营商的流量进行身份验证*。

**遗留 `sip.conf`：**

```
[itsp-in]
type=peer
host=203.0.113.10
context=from-pstn
disallow=all
allow=ulaw
insecure=invite
```

**Asterisk 22 `pjsip.conf`：**

```
[itsp-in]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw

[itsp-in]
type=aor
contact=sip:203.0.113.10:5060

[itsp-in]
type=identify
endpoint=itsp-in
match=203.0.113.10
```

关键的翻译是 **`insecure=invite` → `identify`**。在 `chan_sip` 中，`insecure=invite` 告诉 Asterisk “不要对来自此 peer 的入站 INVITE 进行身份验证质询。” PJSIP 通过使用 `type=identify`/`match=` 将源 IP 匹配到 endpoint 来实现相同的效果，这既更明确也更安全。静态的 `host=` 变为 `aor` 上的永久 `contact=`，以便您也可以向运营商拨出电话。`match=` 接受 IP、CIDR 范围或主机名（在配置加载时解析——如果服务商的 IP 发生变化，请重新加载）。

### 出站注册 (`register =>`)

当服务商希望 *您* 登录到 *他们* 时，`chan_sip` 在 `[general]` 中使用单行 `register =>`。PJSIP 用专用的 `type=registration` 对象加上一个 `outbound_auth` 来替换它。

**遗留 `sip.conf`：**

```
[general]
register => 1020:supersecret@sip.example.com:5600/9999

[itsp]
type=peer
host=sip.example.com
port=5600
defaultuser=1020
secret=supersecret
fromuser=1020
fromdomain=sip.example.com
context=from-pstn
```

**Asterisk 22 `pjsip.conf`：**

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
outbound_auth=itsp-auth
aors=itsp-aor
from_user=1020
from_domain=sip.example.com

[itsp-auth]
type=auth
auth_type=digest
username=1020
password=supersecret

[itsp-aor]
type=aor
contact=sip:sip.example.com:5600

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:sip.example.com:5600
client_uri=sip:1020@sip.example.com:5600
contact_user=9999
retry_interval=60
```

将 `register =>` 字段一一对应：`1020:supersecret` 凭据变为 `auth` 对象（引用为 `outbound_auth`）；`@sip.example.com:5600` 变为 `server_uri`；`/9999` 后缀——服务商将入站呼叫发送到的用户部分——变为 `contact_user=9999`。`defaultuser`/`fromuser` 和 `fromdomain` 变为 endpoint 上的 `from_user` 和 `from_domain`。注意 `outbound_auth` 出现了 *两次*：注册使用它进行 REGISTER，endpoint 使用它来应答出站 INVITE 上的 `407` 质询。

## 逐项迁移参考

当您手动翻译（或审计脚本输出）时，此表是查询手册。每个 PJSIP 选项名称及其位置（endpoint / aor / auth / transport）均已针对 Asterisk 22 实验室环境进行了验证。

| 遗留 `sip.conf` | Asterisk 22 `pjsip.conf` | 位置 |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (设备 REGISTER) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `username=` / `defaultuser=` | `username=` | auth |
| `secret=` (auth 方法) | `auth_type=digest` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `disallow=` / `allow=` | `disallow=` / `allow=` (相同语法) | endpoint |
| `context=` | `context=` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | 省略 auth；使用 `type=identify` + `match=` | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

### 关于 `secret` → `auth` 和 `auth_type` 的说明

`chan_sip` 的 `secret=` 变为 `type=auth` 对象的 `password=` 字段。**身份验证方法** 通过 `auth_type` 设置。请使用 `auth_type=digest`。较旧的值 `userpass` 和 `md5` 仍然有效，但已被 **弃用并静默转换为 `digest`**——直接从实验室验证：

```
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

您会在旧配置和转换脚本的输出中（以及本书的前几章中）看到 `auth_type=userpass`。它没有危害，但在任何新配置中请写入 `digest`。

### NAT、媒体和 DTMF 详解

这三项是大多数迁移后出现“可以注册但没有音频”工单的原因。`chan_sip` 的简写 `nat=force_rport,comedia` 将三种行为打包到一个选项中；PJSIP 将它们拆分，以便您可以分别进行配置：

```
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

对于 **媒体**，`directmedia` 变为 `direct_media`（下划线是唯一的改变）；只要呼叫必须锚定在 Asterisk 上——跨越 NAT，或进行录音/转码/转接——就保留 `direct_media=no`。对于 **DTMF**，RFC 编号已更新：`chan_sip` 的 `dtmfmode=rfc2833` 是 PJSIP 的 `dtmf_mode=rfc4733`（相同的带外 telephone-event 机制，当前的 RFC 编号）。实验室确认有效的 `dtmf_mode` 值为 `rfc4733`、 `inband`、 `info`、 `auto` 和 `auto_info`，默认为 `rfc4733`。

对于 **codec**，没有任何改变：`disallow=all` 后跟 `allow=ulaw`（等）在 PJSIP endpoint 上使用相同的语法。

## Dialplan 和 CLI 变更

迁移并不止于 `pjsip.conf`。日常使用的两件事发生了变化。

### 通道字符串：`SIP/` → `PJSIP/`

`extensions.conf` 中每个命名旧技术的 `Dial()` 和通道引用都必须更新：

```
; Before (chan_sip)
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

Trunk 拨号字符串遵循相同的模式——`Dial(SIP/${EXTEN}@itsp)` 变为 `Dial(PJSIP/${EXTEN}@itsp)`。PJSIP 还添加了 `PJSIP_DIAL_CONTACTS()` 函数来同时呼叫绑定到 AOR 的所有联系人，以及 `PJSIP_HEADER()` / `PJSIP_MEDIA_OFFER()` dialplan 函数；请在您的 dialplan 中搜索 `SIP/`、 `SIPPEER`、 `SIPCHANINFO` 和 `CHANNEL(...)` SIP 引用并逐一翻译。

### CLI：`sip show ...` → `pjsip show ...`

整个 `sip ...` 命令树随着驱动程序的移除而消失。替代方案：

| `chan_sip` 命令 | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (或 `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (或 `core reload`) |

旧命令不仅行为不同——它们根本不存在了。在实验室中，`sip show peers` 返回 *No such command*，而 `pjsip show endpoints`、 `pjsip show aors`、 `pjsip show auths`、 `pjsip show contacts`、 `pjsip show registrations` 和 `pjsip show identifies` 都存在。最有用的故障排除命令——那个使用 `sip set debug` 打印每条消息的 SIP 数据包记录器——现在是 **`pjsip set logger on`**（使用 `pjsip set logger host <ip>` 来聚焦于一个 peer）。

## Realtime (ARA) 迁移

如果您从数据库（Asterisk Realtime Architecture）运行 `chan_sip`，您的设备位于 `sippeers` 表中，注册位于 `sipregs` 中。PJSIP 使用完全不同的存储层——**Sorcery**——每个对象类型对应一个表。映射如下：

| `chan_sip` realtime 表 | PJSIP / Sorcery 表 |
| --- | --- |
| `sippeers` | `ps_endpoints`、 `ps_aors`、 `ps_auths`（各一行，拆分） |
| `sipregs` | `ps_contacts` (动态注册) |
| — (出站 `register=>`) | `ps_registrations` |
| — (IP 匹配) | `ps_endpoint_id_ips` (`identify` 对象) |
| — (域别名) | `ps_domain_aliases` |

概念上的拆分与平面文件情况相同：一行 `sippeers` 变为三张表中的 *三行*（`ps_endpoints` + `ps_aors` + `ps_auths`），它们通过 endpoint 名称相互引用。

两件事使这变得可行：

- **模式为您自动生成。** Asterisk 在 `contrib/ast-db-manage/` 下提供了 Alembic 迁移脚本，用于创建每个 `ps_*` 表。针对 `config` 数据库运行 `alembic upgrade head` 来构建当前的 PJSIP 模式，而不是手动编写 DDL。
- **有一个 SQL 转换脚本。** 与 `sip_to_pjsip.py` 一起，在同一个 `contrib/scripts/sip_to_pjsip/` 目录中存在 **`sip_to_pjsql.py`**；它重用了相同的 `convert()` 逻辑，但为 `ps_*` 表生成了一个 `INSERT` 语句的 `pjsip.sql` 文件，而不是平面配置文件。与平面文件工具一样，在加载前请审查输出。

最后，将 `sorcery.conf` 指向您的数据库，以便 PJSIP 从 `ps_*` 表（通过 `res_config_odbc` / `res_pjsip_realtime`）读取 endpoint、aor、auth 和联系人，就像 `extconfig.conf` 曾经将 `sippeers` 指向数据库以获取 `chan_sip` 一样。Realtime 机制在 *Realtime* 一章中介绍；迁移特定的要点仅仅是 *哪些表映射到哪些表*。

## 迁移检查清单

生产环境切换的操作顺序：

1. **盘点。** 列出 `sip.conf`（或每个 `sippeers`/`sipregs` 行）中的每个设备、trunk 和 `register =>`。记录自定义的 NAT、codec 和 DTMF 设置。
2. **将转换器运行到临时文件中。** `sip_to_pjsip.py sip.conf pjsip_generated.conf`。**不要**将其指向您的实时 `pjsip.conf`。
3. **阅读输出顶部的 "Non mapped elements" 块** 并解决每一行——特别是 `qualify`、计时器和任何与 NAT 相关的内容。
4. **手动设计传输层。** 每个 IP/端口一个传输；根据需要添加 TLS/TCP；为云/NAT 盒子设置 `external_*_address` 和 `local_net`。
5. **验证身份验证。** 确认每个 `auth` 对象上的 `auth_type=digest`、用户名和密码。
6. **验证 NAT/媒体/DTMF。** 根据需要为每个 endpoint 设置 `force_rport`/`rewrite_contact`/`rtp_symmetric`、 `direct_media`、 `dtmf_mode=rfc4733`。
7. **更新 dialplan。** 到处将 `SIP/` 替换为 `PJSIP/`；检查 `SIP*` 函数和通道变量。
8. **更新脚本和监控。** 任何解析 `sip show ...` 输出的工具或 AMI 消费者必须迁移到 `pjsip show ...` / PJSIP AMI 操作。
9. **重新加载并验证。** `module reload res_pjsip.so`，然后是 `pjsip show endpoints`、 `pjsip show registrations`、 `pjsip show identifies`。
10. **使用数据包记录器进行测试。** `pjsip set logger on`；进行一次注册、一次入站呼叫和一次出站呼叫，并端到端读取 SIP 交换。

## 常见陷阱

- **`alwaysauthreject` 现在是内置的——不要寻找它。** `chan_sip` 需要 `alwaysauthreject=yes`，这样它就不会通过对错误的用户名做出不同的回复来泄露哪些分机存在。PJSIP 在设计上就做到了安全：它从不透露 endpoint 是否存在。没有 `alwaysauthreject` 选项可供设置。相关的保护——限制未识别的发送者——是全局的 `unidentified_request_count` / `unidentified_request_period`，默认开启。

- **`insecure=invite` 不是 PJSIP 选项——请使用 `identify`。** `pjsip.conf` 中没有 `insecure=`。接受来自已知运营商的未经身份验证的 INVITE 的方法是使用 `type=identify` / `match=` *通过源 IP 识别 endpoint*。匹配范围尽可能窄（特定的主机 IP，而不是宽泛的 CIDR），并辅以 `type=acl`——没有身份验证的 IP 匹配 trunk 是电话欺诈的目标。

- **每个 IP/端口一个传输。** 您不能将两个传输绑定到同一个 IP:端口，也不能绑定多个相同 IP 版本的 TCP 或 TLS 传输。转换脚本可能会生成与您已有的传输冲突的传输——请整合为一个经过深思熟虑的单一传输层。

- **`qualify=yes` 不会转换为布尔值。** 它作为 `qualify_frequency=<seconds>` 属于 **aor**。转换器将 `qualify=yes` 放入未映射块，正是因为 endpoint 上没有等效的布尔值。

- **`secret=` 不是 endpoint 选项。** 凭据仅存在于 endpoint *引用* 的 `type=auth` 对象中（`auth=` 用于入站，`outbound_auth=` 用于出站）。在 endpoint 上放置密码没有任何作用。

- **CLI 和任何抓取脚本会静默失败。** `sip show ...` 返回 "No such command"，而不是您的监控必然会捕获的错误。在切换前，审计每个 cron 任务、Nagios 检查和 AMI 客户端的 `sip ` 命令。

## 总结

迁移到 Asterisk 22 意味着放弃 `chan_sip`，因为该驱动程序在 Asterisk 21 中已被移除，而 PJSIP 是唯一保留的 SIP 通道。工作的核心是将每个 `sip.conf` `peer`/`user`/`friend`（将所有内容打包到一个块中）重新表达为一组协作的 PJSIP 对象：一个 `endpoint` 加上一个 `auth`、一个 `aor`，以及根据设备的不同，一个 `identify`（入站 trunk）、一个 `registration`（出站登录）和一个共享的 `transport`。位于 `contrib/scripts/sip_to_pjsip/` 的 `sip_to_pjsip.py` 脚本完成了大部分翻译工作，并诚实地在 "Non mapped elements" 块中标记了它无法映射的内容，但其输出只是初稿：请手动设计传输、NAT 和安全性，并在生产前进行测试。在配置周围，更新 dialplan（`SIP/` → `PJSIP/`）以及您的手指和脚本（`sip show` → `pjsip show`、 `sip set debug` → `pjsip set logger`）。Realtime 部署从 `sippeers`/`sipregs` 迁移到 Sorcery `ps_endpoints`/`ps_aors`/`ps_auths`/`ps_contacts` 表，并有 `sip_to_pjsql.py` 和 `contrib/ast-db-manage` 模式提供帮助。注意陷阱——`alwaysauthreject` 是内置的，`insecure=invite` 变为 `identify`，`qualify=yes` 变为 `qualify_frequency`，每个 IP/端口一个传输——切换将是机械的而非神秘的。

## 测验

1. 为什么 Asterisk 22 部署必须使用 PJSIP 进行 SIP？
   - A. `chan_sip` 较慢但仍然可用
   - B. `chan_sip` 在 Asterisk 21 中被移除，在 Asterisk 22 中不存在
   - C. PJSIP 是默认的，但可以通过 `modules.conf` 加载 `chan_sip`
   - D. `chan_sip` 在 Asterisk 22 中仅适用于 TLS

2. 单个 `sip.conf` `type=friend` 块最常变成哪一组 PJSIP 对象？
   - A. 单个 `type=peer`
   - B. 仅 `type=endpoint`
   - C. `type=endpoint` + `type=auth` + `type=aor`
   - D. `type=transport` + `type=registration`

3. 在 `sip.conf` 中，`host=dynamic`（设备注册其自身位置）映射到：
   - A. 带有 `match=dynamic` 的 `type=identify`
   - B. 带有 `max_contacts` 的 `type=aor`（设备 REGISTER）
   - C. endpoint 上的 `direct_media=yes`
   - D. `type=registration`

4. `sip_to_pjsip.py` 转换脚本是：
   - A. 一个 CLI 命令：`asterisk -rx 'sip_to_pjsip'`
   - B. Asterisk 源代码树中 `contrib/scripts/sip_to_pjsip/` 下的一个 Python 脚本
   - C. 启动时加载的编译模块
   - D. `res_pjsip.so` 的一部分

5. 对或错：`sip_to_pjsip.py` 的输出是生产就绪的，无需审查即可加载。

6. `chan_sip` 简写 `nat=force_rport,comedia` 在 PJSIP endpoint 上翻译为哪三个选项？
   - A. `nat=yes`、 `qualify=yes`、 `directmedia=no`
   - B. `force_rport=yes`、 `rewrite_contact=yes`、 `rtp_symmetric=yes`
   - C. `external_media_address`、 `external_signaling_address`、 `local_net`
   - D. `insecure=invite`、 `identify`、 `match`

7. `sip.conf` 的 `dtmfmode=rfc2833` 变为哪个 PJSIP 设置？
   - A. `dtmf_mode=rfc2833`
   - B. `dtmf_mode=inband`
   - C. `dtmf_mode=rfc4733`
   - D. `dtmf_mode=info`

8. 在 Asterisk 22 上，`auth` 对象应该使用哪个 `auth_type`，以及 `userpass` 的状态是什么？
   - A. `auth_type=userpass`；它是唯一有效值
   - B. `auth_type=digest`；`userpass` 已被弃用并转换为 `digest`
   - C. `auth_type=md5`；`digest` 已被弃用
   - D. `auth_type=plaintext`；`digest` 已被移除

9. 带有 `insecure=invite`（接受来自已知 IP 的未经身份验证的 INVITE）的 `chan_sip` 服务商 peer 如何迁移到 PJSIP？
   - A. endpoint 上的 `insecure=invite`
   - B. `[global]` 中的 `allowguest=yes`
   - C. 带有 `match=<provider IP>` 的 `type=identify` 对象
   - D. `auth_type=anonymous`

10. 在 realtime 迁移中，`chan_sip` `sippeers` 表被哪些 PJSIP/Sorcery 表替换？
    - A. 单个 `pjsip_peers` 表
    - B. `ps_endpoints`、 `ps_aors` 和 `ps_auths`
    - C. `sipregs` 和 `voicemail`
    - D. 仅 `ps_contacts`

**答案：** 1 — B · 2 — C · 3 — B · 4 — B · 5 — 错 · 6 — B · 7 — C · 8 — B · 9 — C · 10 — B
