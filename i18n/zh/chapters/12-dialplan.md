# 拨号计划高级功能

第 3 章讨论了拨号计划的基础。出于教学考虑，我们并未解释所有功能，而只挑选了最重要的几项。本章将更深入地探讨拨号计划，描述高级技术、新的应用以及相关概念。

## Objectives

通过本章学习，您应该能够：

- 简化分机条目
- 处理拨号计划的安全性并过滤分机
- 使用 IVR 菜单接收来电
- 使用子例程避免不必要的重写
- 使用 “Include” 实现部分拨号计划安全
- 使用 AsteriskDB 实现呼叫转移（follow-me）
- 在 PBX 中实现非工作时间的行为
- 使用 switch 命令转接到另一台 PBX
- 实现隐私管理器
- 实现语音信箱
- 实现企业目录

## 简化您的拨号计划

您可以使用关键字 “same” 来定义分机，从而简化您的拨号计划。这应该可以减少拨号计划中的拼写错误。请查看下面的示例：

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## 拨号计划安全

在 Asterisk 拨号计划中发现了一个缺陷，允许用户向您的拨号计划注入一个新通道和拨号号码。假设您在服务器 `exten=>_X.,1,Dial(PJSIP/${EXTEN})` 中有以下行，而某个恶意用户在软电话中拨打了号码 `3000&DAHDI/1/011551123456789`。SIP 协议默认接受任何字母数字字符，因此实际拨出的分机将触发两个呼叫：一个是通道 PJSIP/3000，另一个是通道 DAHDI/011551123456789，这是一个国际号码。因此，任何拥有分机访问权限的用户实际上都可以拨打全球任意地点。避免此行为的最简方法是在调用 dial 应用之前过滤号码。FILTER() 函数非常方便。示例：

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

filter 应用将允许您过滤拨号号码中除 0 到 9 之外的所有字符。更多信息请参阅 Asterisk 提供的文件 README‑SERIOUSLY.bestpractices.txt。

## 使用 IVR 菜单接收来电。

在上一节中，您通过 DID 或转接到接线员接听了所有来电。现在，您将学习如何实现 IVR 菜单以及创建自动接待服务。在深入细节之前，让我们先看看一些新应用。我们在下面放置了命令 `core show application` 的输出，仅为方便读者。您可以使用 `core show application <application_name>` 自行获取这些描述。

### Background() 应用程序

此应用将在等待呼叫通道拨入分机号时播放给定的文件列表。若在此应用播放完文件后仍需继续等待数字，应使用 WaitExten 应用。`langoverride` 选项明确指定要尝试使用的语言，以获取请求的声音文件。任何指定的 context 将是此应用在退出到已拨入的分机时使用的 dialplan context。如果请求的声音文件之一不存在，呼叫处理将被终止。选项：

- s - 如果通道未处于“up”状态（即尚未被接听），则跳过消息的播放。如果发生这种情况，应用程序将立即返回。  
- n - 在播放文件之前不要接听通道。  
- m - 仅当按下的数字匹配目标上下文中的一位分机时才中断。

### Record() 应用程序

此应用程序将从通道录制到指定的文件名。如果文件已存在，它将被覆盖。

![10-dialplan-advanced-features 图 1](../images/10-dialplan-advanced-features-img01.png)

- ‘format’ 是要记录的文件类型的格式（wav、gsm 等）。
- ‘silence’ 是在返回之前允许的静默秒数。
- ‘maxduration’ 是最大录音时长（秒）；如果缺失或为零，则没有最大限制。
- ‘options’ 可以包含以下任意字母：
    - `a` — 追加到已有录音而不是替换
    - `n` — 不接听，但如果线路尚未接通仍进行录音
    - `q` — 静音（不播放提示音）
    - `s` — 如果线路尚未接通则跳过录音
    - `t` — 使用备用的 `*` 终止键（DTMF）而不是默认的 `#`
    - `x` — 忽略所有终止键（DTMF），并持续录音直至挂断

如果文件名包含 %d，这些字符将在每次录制文件时被替换为递增的数字。使用 core show file formats 查看系统上可用的格式。用户可以按 # 结束录音并继续下一个优先级。如果用户在录音期间挂断，所有数据将会丢失，应用程序将终止。

### Playback() 应用程序

此应用程序回放给定的文件名（不要包含扩展名）。选项也可以在管道符号后面加入。'skip' 选项在通道未处于 'up' 状态（即尚未接通）时会跳过消息的播放。

![10-dialplan-advanced-features 图 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features 图 3](../images/10-dialplan-advanced-features-img03.png)

如果指定了 'skip'，当通道未摘机时，应用程序将立即返回。否则，除非指定了 'noanswer'，通道将在播放声音之前被接听。并非所有通道都支持在仍然挂机状态下播放消息。如果指定了 'j'，当文件不存在时（如果提供），应用程序将跳转到优先级 n+101。此应用程序在完成后会设置以下通道变量：

- PLAYBACKSTATUS — 播放尝试的状态，作为文本字符串，可能的值包括：
    - `SUCCESS`
    - `FAILED`

### Read() 应用程序

此应用程序从用户读取预定数量的字符串数字，重复若干次，存入给定变量。

- filename -- 在使用 i 选项读取数字或音调之前播放的文件
- maxdigits -- 可接受的最大数字数量。输入达到 maxdigits 后停止读取（无需用户按 # 键）。默认值为 0 - 无限制 - 等待用户按 # 键。任何小于 0 的值意义相同。最大可接受值为 255.

![10-dialplan-advanced-features 图 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features 图 5](../images/10-dialplan-advanced-features-img05.png)

- option -- 选项为 `s`, `i`, `n`:
    - `s` — 如果线路未接通，立即返回
    - `i` — 从你的 `indications.conf` 播放文件名作为指示音
    - `n` — 即使线路未接通也读取数字
- attempts -- 如果大于 1，则在未输入数据的情况下将进行的尝试次数
- timeout -- 整数秒数，等待数字响应。如果大于 0，该值将覆盖默认超时。

如果函数失败或出错，read() 应用程序应断开连接。

### Gotoif() 应用程序

此应用程序将在评估给定条件后，使呼叫通道跳转到 dial plan 中的指定位置。如果条件为真，通道将在 labeliftrue 处继续；如果条件为假，则在 'labeliffalse' 处继续。标签的指定语法与 Goto 应用程序中使用的相同。如果条件选择的标签被省略，则不会执行跳转，而是继续执行 dial plan 中的下一个优先级。

### Lab: 逐步构建 IVR 菜单

让我们创建一个具有以下功能的IVR菜单。拨打时，IVR播放一段音频文件，内容为“欢迎致电XYZ公司；按1获取销售，按2获取技术支持，按3获取培训，或等待与客服代表通话。”数字将来电者路由如下：

- `1` — 转接到销售 (PJSIP/4001)
- `2` — 转接到技术支持 (PJSIP/4002)
- `3` — 转接到培训 (PJSIP/4003)
- 未按数字键 — 转接到接线员 (PJSIP/4000)

**步骤 1 – 记录提示**

让我们创建一个用于录制提示音的分机。要录制提示音，请从软电话拨打 `9003<filename>`（例如，`9003welcome`）。当听到提示音时，开始录音；按 `#` 停止。您会听到提示音，系统将回放录制的提示音。

**步骤 2 – 创建菜单逻辑**

When dialing the 9004 extension, processing jumps to the menu in the `s` extension, priority 1.

### 拨号时匹配

这是一个用于接收来电的公司设置菜单。 `Background()` 应用程序播放欢迎提示音，然后等待数字输入，将来电者拨打的号码与当前上下文中定义的分机进行匹配。

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

当您拨打这家公司时，首先播放欢迎信息。随后，Asterisk 等待用户输入一个数字：

| 拨号号码 | Asterisk 动作 |
|---------------|-----------------|
| 1 | 立即呼叫 `Dial(DAHDI/1)` |
| 2 | 等待超时后，呼叫 `Dial(DAHDI/2)` |
| 21 | 立即呼叫 `Dial(DAHDI/3)` |
| 22 | 立即呼叫 `Dial(DAHDI/4)` |
| 3 | 等待超时后，挂断 |
| 31 | 立即呼叫 `Dial(DAHDI/5)` |
| 32 | 立即呼叫 `Dial(DAHDI/6)` |

避免菜单产生歧义非常重要。每个人都希望快速得到响应。因此，不应使用数字 2、21 或 22。

### 实验：使用 Read() 应用

请使用 read() 应用完成实验。Read 接受用户输入的数字并将其存入指定变量；随后您可以使用 gotoif 应用将通话重定向。

## Context inclusion

上下文可以包含另一个上下文的内容。在上面的示例中，任何通道都可以拨打 internal 上下文中的任意分机，但只有 4003 通道可以拨打国际分机。您可以使用上下文包含来简化 dial plan 的创建。通过上下文包含，您可以控制谁可以访问哪些分机。

### Troubleshooting the message “number not found”

收到 “number not found” 提示是非常常见的。大多数人会混淆包含上下文的概念，因为它确实不直观。经验法则是，首先查看入站通道配置文件，例如 `pjsip.conf`、`chan_dahdi.conf` 和 `iax.conf`，确定当前的上下文。然后，转到 extensions.conf 文件中的 dial plan，检查所拨号码是否在该上下文中。如果没有，则您的 dial plan 有问题。上下文的黄金规则是：1. 通道只能拨打与该通道位于同一上下文中的号码。2. 处理通话的上下文在入站通道配置文件（`chan_dahdi.conf`、`iax.conf`、`pjsip.conf`）中定义。

## 使用 switch 语句

您可以使用 switch 命令将 dial plan 处理发送到另一台服务器。您需要该服务器的名称和密钥。context 是目标 context。

![10-dialplan-advanced-features 图 6](../images/10-dialplan-advanced-features-img06.png)

## Dial plan processing order

当 Asterisk 接收到来电时，它会在通道定义的 context 中查找。某些情况下，如果有多个模式匹配被拨打的号码，Asterisk 可能无法以你预期的方式处理呼叫。你可以使用 `dialplan show` CLI 命令查看匹配顺序。例如：假设你想把拨打 912 的呼叫路由到模拟中继 (DAHDI/1)，而所有以 9 开头的其他号码路由到另一个模拟中继 (DAHDI/2)。你可以这样写：

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

如果两个模式匹配同一个 extension，你可以通过包含的 contexts 来控制哪个 extension 先被处理。包含的 context 的处理顺序在同一 context 中的模式之后。

## #INCLUDE 语句

我们应该使用一个大文件还是多个小文件？您可以使用 #include <filename> 语句在 extensions.conf 中包含其他文件。例如，我们可以为本地用户创建 users.conf，为特殊服务创建 services.conf。请注意不要把 #include <filename> 与的混淆

```
include=>context statement.
```

## 子程序与 GOSUB

在较早的 Asterisk 版本中，你会使用 Macro 命令。该命令早已被弃用，转而使用 GOSUB。我们将在此演示如何以简洁有序的方式创建用于语音信箱处理的子程序。命令格式：

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

自 Asterisk 1.6 起，GOSUB 命令已可用，并支持传递参数（在子程序内部可通过 `${ARG1}`、`${ARG2}` 等方式访问）。有了参数后，完全可以取代旧的 Macro 命令。Macro（`app_macro`）已在 Asterisk 21 中移除；子程序必须使用 GOSUB。

### 创建子程序

定义方式非常相似。下面示例定义了一个名为 stdexten 的语音信箱子程序（你可以自行选择名称）。在调用 Dial 命令并传入第一个参数（通道名称）后，我们检查 ${DIALSTATUS}，以将呼叫逻辑转到下一步。

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### 调用子程序

调用子程序时请注意在参数前使用括号。

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## 使用 Asterisk DB

为了实现呼叫转移和黑名单，我们需要一种存储和恢复数据的方式。幸运的是，Asterisk 提供了一个内置数据库 AstDB 用于存储和检索数据。在现代 Asterisk（包括 Asterisk 22）中，AstDB 由 **SQLite3**（文件 `/var/lib/asterisk/astdb.sqlite3`）支持；Asterisk 1.8 及更早版本使用 Berkeley DB v1。这类似于 Windows 注册表数据库，使用 family 和 key 的层次概念。数据在 Asterisk 重启之间保持持久。family/key API 与旧的后端保持不变；仅磁盘存储格式发生了变化。

### 函数、应用和 CLI 命令

有一些函数、应用和 CLI 命令可用于操作 AstDB：

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

示例：

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

一些应用可以用于操作 AstDB：

- DB_DELETE(<family/key>) — 返回并删除单个键的函数
- DBdeltree(<family>) — 删除整个 family/子树的应用

旧的 `DBdel()` 应用在 Asterisk 22 中已不再存在。使用 `DB_DELETE()` dialplan 函数删除单个键，例如 `Set(x=${DB_DELETE(family/key)})` 或作为写操作的 `Set(DB_DELETE(family/key)=)`。`DBdeltree()` （删除整个 family/子树）仍然是一个应用。

也可以使用 CLI 命令来设置和删除键：

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### 实现呼叫转移、勿扰和黑名单

在本示例中，您将学习如何实现即时呼叫转移和忙碌时呼叫转移。我们将使用 *21* 编程即时呼叫转移，使用 *61* 编程忙碌时呼叫转移。要取消编程，分别使用 #21# 和 #61#。使用上述示例填充数据库。使用的 families：

- CFIM – 即时呼叫转移
- CFBS – 忙碌时呼叫转移
- DND – 勿扰模式

尝试通过拨号填充数据库：

- *21*（即时呼叫转移的目标分机）
- *61*（忙碌时呼叫转移的目标分机）
- *41*（设置勿扰的分机）

使用 CLI 命令 database show 查看已添加的 families、keys 和 values。

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### 呼叫转移、黑名单、勿扰

子例程检查数据库是否包含对应 CFIM、CFBS 或 DND 的 key:value 对，然后相应处理。以下子例程调用拨号例程：

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## 使用黑名单

旧的 `LookupBlacklist()` 应用已 **从 Asterisk 中移除**（它随同传统的 “priority+101 跳转” 机制一起消失）。在 Asterisk 22 中，你可以直接使用 `DB_EXISTS()` 函数（该函数既会测试键是否存在，又会在找到时将其值暴露在 `${DB_RESULT}` 中）加上 `GotoIf` 来构建黑名单。将每个被阻止的号码作为键存入 `blacklist` 家族，然后在入站 context 的顶部检查来电号码：

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

当来电号码存在于数据库中时，`DB_EXISTS(blacklist/${CALLERID(num)})` 返回 `1`（将呼叫发送到 `blocked` context），否则返回 `0` ，因此呼叫会继续进入正常的 `Dial()`。

要向黑名单中插入号码，可以使用与之前相同的资源，使用 *31* 加上要加入黑名单的分机号。要从黑名单中移除号码，应使用 #31# 加上要移除的号码。

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

你也可以使用控制台 CLI 将号码插入黑名单：

```
*CLI>database put blacklist <name/number> 1
```

注意：任何值都可以与键关联。 `DB_EXISTS()` 测试搜索的是键，而不是值。要从黑名单中擦除号码，可以使用：

```
*CLI>database del blacklist <name/number>
```

## 基于时间的上下文

在下图中，我们有一个包含三个上下文的拨号计划。`[incoming]` 上下文是通常接收来电的地方。我们加入了四行，根据系统时间改变行为，如下所示：

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

现代 Asterisk（包括 22）使用**逗号**而不是管道来分隔 time-include 字段。旧式的管道形式（`include => context|times|weekdays|mdays|months`）会被解析为普通的文字上下文名，并且会悄悄地导致时间条件失效。

在正常工作时间内，处理将被重定向到 `mainmenu`，在那里可能会调用 IVR 来处理来电。如果来电发生在下班时间，它将呼叫 `${SECURITY}` 变量中定义的安全分机。如果安全分机未接听，通话将被转到操作员的语音信箱。

![10-dialplan-advanced-features 图 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features 图 12](../images/10-dialplan-advanced-features-img12.png)

## 使用 gotoiftime() 的基于时间的消息

GotoIfTime() 语法如下所示。

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

在 Asterisk 22 中，字段分隔符是 **逗号**，而不是管道符（管道形式已在 Asterisk 1.6 中弃用）。支持可选的 `timezone` 字段，并且每个分支标签使用常规的 `[[context,]extension,]priority` 形式。

此应用程序可以替代基于时间的 context，并且看起来更易于理解和阅读。您可以按如下方式指定时间：

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=number from 1 to 31
- <hour>=number from 0 to 23
- <minute>=number from 0 to 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

日期和月份的名称不区分大小写。

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

前面的语句将在通话时间为周一至周五的上午 08:00 到下午 06:00 之间时，将处理转移到 normalhours context 中的分机 s。

## 使用 DISA 获取新的拨号音

DISA，或称 “direct inward system access”，是一种允许用户获得第二个拨号音的系统。它允许用户再次拨号到其他目的地。技术人员常在周末进行技术支持的长途呼叫时使用它；他们不是直接从家里拨打目的地，而是先拨打办公室的 DISA 号码，收到拨号音后再拨打目的地。长途费用由公司承担，而不是家庭电话。

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

示例：

```
exten => s,1,DISA(no-password,default)
```

使用前面的语句，用户拨打 PBX——无需任何密码——即可收到拨号音。任何使用 DISA 的呼叫都将使用 `default` 上下文进行处理。此应用的参数包括全局密码或文件中的单独密码。如果未指定上下文，则默认使用 `disa` 上下文。如果使用密码文件，必须指定完整路径。也可以为 DISA 的外部拨号指定来电显示。示例：

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 使用逗号作为参数分隔符（在 1.6 版中已弃用管道形式）。第一个参数可以是单个密码或密码文件的路径，当未提供参数时默认上下文为 `disa`。

## 限制同时通话

GROUP() 函数允许您统计同一组中同时处于活动状态的通道数量。例如：您在里约热内卢有一个分支，电话使用模式 “_214X”。该地点使用租用线路，保留 64K 作为语音带宽。在这种情况下，允许的最大通话数为 2（G.729，每通话约 31.2K）。要将里约的通话限制为两路：

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail 是一种计算机化的电话答录系统，记录来电语音信息，将其保存到磁盘或通过电子邮件发送。有时它还有一个目录，您可以按名称查找语音信箱。过去，语音信箱系统非常昂贵。现在，随着 IP 语音的普及，语音信箱正成为标准功能。

要配置语音信箱，您应按以下步骤进行。

**Step 1: Edit `voicemail.conf` and set the general parameters.**

- `format` — 用于录制信息的 codec（例如 wav49、wav、gsm）
- `serveremail` — 电子邮件通知的发件人显示方式
- `maxmsg` — 信箱中最大消息数量；超过此阈值后，消息将被丢弃
- `maxsecs` — 语音信箱消息的最大时长（秒）
- `minsecs` — 消息的最短时长（秒）；低于此阈值时，不会录制消息
- `maxsilence` — 将多少秒的静音视为消息结束

**Step 2: Edit `voicemail.conf` and create the users’ mailboxes.**

### Voicemail.conf

一个信箱使用每行一条的方式定义，格式为：

```
mailboxID => pincode,fullname,email,pager-email,options
```

字段说明：

- **MailboxID** — 通常为分机号
- **Pincode** — 访问语音信箱系统的密码
- **Full name** — 目录应用使用的全名
- **E-mail** — 语音信箱通知的电子邮件地址
- **Pager e-mail** — 通过 SMS 网关或呼叫器发送通知的电子邮件地址
- **Options** — 每个信箱的选项（与 `[general]` 中相同的选项，但应用于此信箱）

语音信箱有多个选项可控制其行为。目前我们使用默认选项，重点关注信箱定义。在文件的 `[general]` 部分之后，您可以开始配置每个上下文中的信箱 ID。例如：

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

请在文件 `voicemail.conf` 中查阅高级选项。

**Step 3: Configure the file `extensions.conf`.**

前面（在 *Subroutines with GOSUB* 下）展示的 `stdexten` 子例程正是您此处需要的呼叫/语音信箱处理程序：它拨打分机并使用通道变量 `${DIALSTATUS}` 的值将呼叫流程重定向到相应的语音信箱问候语（忙碌时的 `b`，不可用时的 `u`）。在 `extensions.conf` 中的每个分机上使用 `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` 调用它。

## 使用 VoiceMailMain() 应用程序

应用程序 voicemailmain() 用于配置语音信箱。用户可以拨打该应用程序，录制问候语，并收听自己的语音邮件。要在 dialplan 中调用该应用程序，请使用：

```
exten=>9000,1,VoiceMailMain()
```

下面列出了该应用程序可用的选项。

### Voicemail 应用程序语法

此应用程序允许呼叫方为指定的邮箱列表留下消息。当指定多个邮箱时，问候语将取自第一个指定的邮箱。如果指定的邮箱不存在，dialplan 执行将停止。语法如下所示：

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

在所有情况下，beep.gsm 文件将在录音开始前播放。语音邮件将存储在 inbox 目录中。

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

如果呼叫者在公告期间按下 0（零），将转到语音邮件当前上下文中的 ‘o’（out）分机。这可用于转接到接线员。如果在录音期间呼叫者按下 # 或静音限制超时，录音将停止，呼叫转到下一个优先级。确保在播放语音邮件后处理呼叫，如下所示。

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### 将语音邮件标记为紧急

您可以将某些消息标记为 “紧急”。有两种方法可实现：

- 在应用程序 voicemail() 中传递选项 ‘U’
- 在文件 voicemail.conf 中指定 review=yes。使用此选项时，用户将在录制语音指令后能够将消息标记为紧急。

## Sending voicemail to e-mail

在某些情况下（比如我的情况），我们根本不使用 voicemailmain() 应用来读取电子邮件。将所有语音邮件以音频附件的形式发送到电子邮件更简单、更实用。使用参数 **attach** 和 **delete**，即可将所有邮件发送到电子邮件并从邮箱中删除。

```
attach=yes
delete=yes
```

要将语音邮件发送到电子邮件，voicemail 应用会使用消息传输代理（MTA），即操作系统的一个组件。Debian 使用 Exim 作为 MTA。发送电子邮件的应用在 **mailcmd** 参数中定义。

```
mailcmd =/usr/sbin/sendmail -t
```

在 Debian 发行版的 Linux 中，MTA 是 Exim。要在 Debian 中配置 Exim，请使用：

```
dpkg-reconfigure exim4-config
```

您可以选择让 MTA 直接通过 SMTP 发送电子邮件，或通过 smarthost（通常是贵公司的邮件服务器）发送。请与您的电子邮件管理员确认从 Asterisk 服务器向您的邮件服务器发送电子邮件的最佳方式。

## 定制电子邮件内容

您可以通过设置以下变量来控制邮件的发送方式：用于电子邮件主题和正文的变量：

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

电子邮件的正文和主题是根据您在 `[general]` 部分的 `voicemail.conf` 中设置的模板生成的。您可以修改正文和主题，但消息的大小限制为 512 字节。在模板中， `\n` 插入换行符， `\t` 插入制表符。

下面的 `emailsubject` 示例非常直接。 `emailbody` 示例与默认设置非常接近；默认情况下，当 CIDNAME 不为空时只显示 CIDNAME，否则显示 CIDNUM，若两者均为空则显示 “an unknown caller”。 

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Voicemail Web interface

There is a Perl script in the source distribution called `vmail.cgi`, located at `contrib/scripts/vmail.cgi` in the Asterisk source tree (it still ships with Asterisk 22). The command `make install` does not install this interface; you must run `make webvmail` from the source directory. This script requires the Perl command interpreter and a web server (such as Apache) to be installed on the server.

```
make webvmail
```

The `make webvmail` target installs the script (setuid root) into your web server's CGI directory (`HTTP_CGIDIR`) and copies the supporting images from `images/*.gif` into `HTTP_DOCSDIR/_asterisk` (by default `/var/www/html/_asterisk`). If those paths do not match your web server layout, edit the `HTTP_CGIDIR` and `HTTP_DOCSDIR` variables in the top-level `Makefile` before running the target.

## Voicemail notification

您可以配置语音信箱，在收到新语音邮件时向您的手机发送通知消息。在 Asterisk 22 中，消息等待指示（MWI）可用于 PJSIP、SIP 手机以及 DAHDI 手机。为了指示未听取的语音邮件，指示灯可能会闪烁，或手机会播放提示音。您需要在相应的通道配置文件中配置邮箱。例如：`pjsip.conf`（在 endpoint 部分）：

```
mailboxes=8590
```

在 PJSIP 中，邮箱提示通过`mailboxes`选项在`pjsip.conf`的 endpoint 部分设置，而不是旧的`mailbox=`的`sip.conf`。MWI 订阅由`res_pjsip_mwi`模块处理。

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Lab: Message Notification in the Phone

本实验使用 SIP 软电话进行测试。

1. 编辑`pjsip.conf`并在名为 4401 的设备的 endpoint 部分添加`mailboxes=4401`。
2. 编辑`extensions.conf`并创建一个分机，以将语音邮件记录到 4401 分机。

```
exten=9008,1,voicemail(4401,b)
```

3. 进入控制台并重新加载。
4. 在 SipPulse Softphone 中，打开 SIP 账户设置并为该账户启用语音邮件（message-waiting）检查。
5. 拨打 9008 并留下信息。
6. 观察手机上的消息图标。

## 使用 directory 应用

此应用允许您快速查找要拨打的用户。名称列表及相应分机号从 voicemail 配置文件 voicemail.conf 中获取。可以使用 `core show application directory` 来显示该应用的语法：

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### 实验：使用 directory 应用

1. 编辑 voicemail.conf 文件，在拨号计划中添加两个分机

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. 在您的拨号计划中创建这些分机

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. 前往控制台并重新加载  
4. 拨打 9006 并为每个分机录入姓名（4400，4401）  
5. 拨打 9007 并为一个分机选择姓氏的前三个字母（Eas=327）。如果这是正确的选项，按 ‘1’ 转接到该姓名。

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## 概要

在本章中，您学习了如何使用 IVR 或自动接线员接收来电。您研究了上下文包含的概念并实现了几个示例。子例程用于避免重复输入，Asterisk 数据库（AstDB，在 Asterisk 22 中由 SQLite3 支持）用于需要数据存储的功能（例如，呼叫转移、请勿打扰、黑名单）。最后，您学习了如何实现非工作时间的行为，并使用这些概念实现了完整的 dial plan。

## Quiz

1. A time-dependent context include uses the form `include => context,<times>,<weekdays>,<mdays>,<months>`. What does `include => normalhours,08:00-18:00,mon-fri,*,*` do?
   - A. Execute the extensions Monday to Friday, 08:00 to 18:00
   - B. Execute the options every day in all months
   - C. Nothing; the format is invalid
2. In modern Asterisk (including Asterisk 22), the fields of a time-based `include =>` and of `GotoIfTime()` are separated by which character?
   - A. The pipe `|`
   - B. The comma `,`
   - C. The semicolon `;`
   - D. The slash `/`
3. To dial several channels at once (ringing them simultaneously), you separate them inside `Dial()` with the ___ character.
4. A voice menu that plays a prompt while waiting for the caller to dial an extension is usually created with the ___ application.
5. You can include the contents of another file inside `extensions.conf` using the ___ statement (note: this is different from the `include =>` context statement).
6. In Asterisk 22, the built-in AstDB database is backed by:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. When you use `Dial(type1/identifier1&type2/identifier2)`, Asterisk dials each channel in sequence, waiting 20 seconds between them.
   - A. False
   - B. True
8. With the Background() application, you must wait until the message finishes playing before you can press a DTMF digit to choose an option.
   - A. False
   - B. True
9. Given the syntax `Goto([[context,]extension,]priority)`, which of the following are valid invocations of the Goto() application? (mark all that apply)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. To delete a single key from AstDB in the Asterisk 22 dial plan, you use:
    - A. The `DBdel()` application
    - B. The `DB_DELETE()` function
    - C. The `DBdeltree()` application
    - D. The `LookupBlacklist()` application

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
