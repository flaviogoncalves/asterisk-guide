# Dial Plan 高级功能

第 3 章讨论了 dial plan 的基础知识。出于教学原因，我们没有解释所有功能，只介绍了一些最重要的功能。本章将深入探讨 dial plan，描述高级技术、新的应用程序和概念。

## 目标

读完本章后，您应该能够：

- 简化您的 extension 条目
- 处理 dial plan 安全性和过滤 extension
- 使用 IVR 菜单接收呼叫
- 使用子程序以避免不必要的重写
- 使用 “Include” 实现一些 dial plan 安全性
- 使用 AsteriskDB 实现呼叫转移（follow-me）
- 在您的 PBX 中实现下班后行为
- 使用 switch 命令转移到另一个 PBX
- 实现隐私管理器（privacy manager）
- 实现语音信箱（voicemail）
- 实现企业通讯录

## 简化您的 Dial Plan

您可以使用关键字 “same” 来定义 extension，从而简化 dial plan。这应该能减少 dial plan 中的拼写错误。请查看下面的示例：

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Dial Plan 安全性

在 Asterisk dial plan 中发现了一个漏洞，允许用户注入一个新的 channel 并拨打号码到您的 dial plan 中。假设您的服务器中有以下行 `exten=>_X.,1,Dial(PJSIP/${EXTEN})`，并且某个恶意用户在 softphone 中拨打了号码 `3000&DAHDI/1/011551123456789`。SIP 协议默认接受任何字母数字字符，因此拨打的 extension 实际上会触发两个呼叫：一个用于 channel PJSIP/3000，另一个用于 channel DAHDI/011551123456789（这是一个国际号码）。因此，任何有权访问 extension 的用户实际上都可以拨打世界上的任何地方。避免这种行为的最简单方法是在调用 dial 应用程序之前过滤号码。FILTER() 函数对此非常方便。示例：

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

filter 应用程序允许您过滤掉拨打号码中除 0 到 9 以外的所有字符。更多信息可以在 Asterisk 提供的文件 README-SERIOUSLY.bestpractices.txt 中找到。

## 使用 IVR 菜单接收呼叫。

在上一节中，您通过 DID 或转接到接线员接收了所有呼叫。现在，您将学习如何实现 IVR 菜单以及创建自动总机服务。在进入具体细节之前，让我们检查一些新的应用程序。我们将 show application 命令的输出放在下面，只是为了方便读者阅读。您可以使用 show application application_name 获取这些描述。 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### Background() 应用程序

此应用程序将播放给定的文件列表，同时等待呼叫 channel 拨打 extension。要在该应用程序播放完文件后继续等待数字，应使用 WaitExten 应用程序。langoverride 选项明确指定了尝试为请求的声音文件使用的语言。指定的任何 context 都将是此应用程序在退出到拨打的 extension 时使用的 dial plan context。如果请求的声音文件不存在，呼叫处理将被终止。选项：

- s - 如果 channel 不处于 'up' 状态（即尚未接听），则跳过消息的播放。如果发生这种情况，应用程序将立即返回。
- n - 在播放文件之前不要接听 channel。
- m - 仅当拨号匹配目标 context 中的一位数 extension 时才中断。

### Record() 应用程序

此应用程序将 channel 的内容录制到给定的文件名中。如果文件存在，它将被覆盖。

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' 是要录制的文件类型格式（wav, gsm 等）。
- 'silence' 是返回前允许的静音秒数。
- 'maxduration' 是最大录制时长（以秒为单位）；如果缺失或为零，则没有最大值。
- 'options' 可能包含以下任何字母：
    - `a` — 追加到现有录音而不是替换它
    - `n` — 不接听，但如果线路尚未接听则仍进行录制
    - `q` — 静音（不播放蜂鸣音）
    - `s` — 如果线路尚未接听则跳过录制
    - `t` — 使用替代的 `*` 终止键 (DTMF) 代替默认的 `#`
    - `x` — 忽略所有终止键 (DTMF) 并持续录制直到挂断

如果文件名包含 %d，则每次录制文件时，这些字符将被递增 1 的数字替换。使用 core show file formats 查看系统上可用的格式。用户可以按 # 键终止录制并继续执行下一个优先级。如果用户在录制过程中挂断，所有数据都将丢失，应用程序将终止。

### Playback() 应用程序

此应用程序回放给定的文件名（不包括扩展名）。选项也可以包含在管道符号之后。'skip' 选项会导致如果 channel 不处于 'up' 状态（即尚未接听），则跳过消息的播放。

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

如果指定了 'skip'，且 channel 未摘机，应用程序将立即返回。否则，除非指定了 'noanswer'，否则 channel 将在播放声音之前被接听。并非所有 channel 都支持在未摘机时播放消息。如果指定了 'j'，当文件不存在时，应用程序将跳转到优先级 n+101（如果存在）。此应用程序在完成后设置以下 channel 变量：

- PLAYBACKSTATUS — 播放尝试的状态，作为文本字符串，为以下之一：
    - `SUCCESS`
    - `FAILED`

### Read() 应用程序

此应用程序从用户那里读取预定数量的字符串数字，读取一定次数，并存入给定的变量中。

- filename -- 在读取数字或使用选项 i 的音调之前播放的文件
- maxdigits -- 可接受的最大数字位数。在输入 maxdigits 后停止读取（无需用户按 # 键）。默认为 0 - 无限制 - 等待用户按 # 键。任何低于 0 的值含义相同。最大可接受值为 255。

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- 选项为 `s`, `i`, `n`：
    - `s` — 如果线路未接通则立即返回
    - `i` — 将 filename 作为来自您的 `indications.conf` 的提示音播放
    - `n` — 即使线路未接通也读取数字
- attempts -- 如果大于 1，则表示在未输入数据的情况下将进行的尝试次数
- timeout -- 等待数字响应的整数秒数。如果大于 0，该值将覆盖默认超时。

如果函数失败或出错，read() 应用程序应该断开连接。

### Gotoif() 应用程序

此应用程序将根据给定条件的评估结果，使呼叫 channel 跳转到 dial plan 中的指定位置。如果条件为真，channel 将在 labeliftrue 继续执行；如果条件为假，则在 'labeliffalse' 继续执行。标签的指定语法与 Goto 应用程序中使用的语法相同。如果条件选择的标签被省略，则不执行跳转；而是继续执行 dial plan 中的下一个优先级。

### 实验：逐步构建 IVR 菜单

让我们创建一个具有以下功能的 IVR 菜单。拨打时，IVR 会播放一个音频文件，内容为“欢迎致电 XYZ 公司；按 1 转销售部，按 2 转技术支持，按 3 转培训部，或等待与代表通话。”数字将呼叫者路由如下：

- `1` — 转接至销售部 (PJSIP/4001)
- `2` — 转接至技术支持 (PJSIP/4002)
- `3` — 转接至培训部 (PJSIP/4003)
- 未按数字 — 转接至接线员 (PJSIP/4000)

**第 1 步 – 录制提示音**

让我们创建一个 extension 来录制提示音。要录制提示音，请从 softphone 拨打 `9003<filename>`（例如，`9003welcome`）。听到蜂鸣声后，开始录制；按 `#` 停止。您将听到一声蜂鸣，系统将回放录制的提示音。

**第 2 步 – 创建菜单逻辑**

拨打 9004 extension 时，处理跳转到 `s` extension 的菜单，优先级为 1。

### 拨号时匹配

这是一个用于接收呼叫的公司设置菜单。background 应用程序读取当前的 context 并为任何可能的组合定义每个号码的最大长度。

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

当您拨打此公司电话时，首先会播放欢迎消息。之后，Asterisk 等待拨入数字。拨打的号码 Asterisk 动作 立即调用 Dial(DAHDI/1) 等待超时，然后转到 Dial(DAHDI/2) 立即调用 (DAHDI/3) 立即调用 (DAHDI/4) 等待超时，然后断开连接 立即调用 Dial(DAHDI/5) 立即调用 Dial(DAHDI/6) 立即断开连接。避免菜单中的歧义非常重要。每个人都希望被快速接听。因此，您不应使用数字 2、21 或 22。

### 实验：使用 Read() 应用程序

请尝试使用 read() 应用程序进行实验。Read 接受来自用户的数字并将其插入到指定的变量中；然后您可以使用 gotoif 应用程序来重定向呼叫。

## Context 包含

一个 context 可以包含另一个 context 的内容。在上面的示例中，任何 channel 都可以拨打 internal context 中的任何 extension，但只有 4003 channel 可以拨打国际 extension。您可以使用 context 包含来简化 dial plan 的创建。通过 context 包含，您可以控制谁有权访问哪些 extension。

### 排查“number not found”消息

收到“number not found”消息非常常见。大多数人混淆了包含 context 的概念，因为它确实不直观。根据经验，首先转到传入 channel 的配置文件，例如 `pjsip.conf`, `chan_dahdi.conf` 和 `iax.conf`，并确定当前的 context。然后，转到 extensions.conf 文件中的 dial plan，检查拨打的号码是否可以在该 context 中找到。如果没有，说明您的 dial plan 有问题。Context 的黄金法则是：1. 一个 channel 只能拨打与该 channel 处于同一 context 内的号码。2. 呼叫处理所在的 context 是在传入 channel 的配置文件（`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`）中定义的。

## 使用 switch 语句

您可以使用 switch 命令将 dial plan 处理发送到另一台服务器。您需要另一台服务器的名称和密钥。Context 是目标 context。

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Dial plan 处理顺序

当 Asterisk 收到传入呼叫时，它会查看 channel 定义的 context。在某些情况下，如果多个模式匹配拨打的号码，Asterisk 可能无法按照您认为应该的方式处理呼叫。您可以使用 dialplan show CLI 命令查看匹配顺序。示例：假设您想拨打 912 以路由到模拟 trunk (DAHDI/1)，并将所有其他以 9 开头的号码路由到另一个模拟 trunk (DAHDI/2)。您可以这样写：

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

如果两个模式匹配一个 extension，您可以使用包含的 context 来控制哪个 extension 先被处理。包含的 context 的处理优先级低于同一 context 中的模式。

## #INCLUDE 语句

我们应该使用一个大文件还是多个文件？您可以使用 #include <filename> 语句在 extensions.conf 中包含其他文件。例如，我们可以创建一个 users.conf 用于本地用户，创建一个 services.conf 用于特殊服务。小心不要将 #include <filename> 与

```
include=>context statement.
```

## 使用 GOSUB 的子程序

在旧版本的 Asterisk 中，您有 Macro 命令。该命令很久以前就被弃用，转而支持 GOSUB。我们将在此演示如何以简单且有序的方式创建用于语音信箱处理的子程序。命令格式：

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

GOSUB 命令自 Asterisk 1.6 起可用，并支持传递参数（在子程序内可用作 `${ARG1}`, `${ARG2}` 等）。有了参数，现在可以完全替换旧的 Macro 命令。Macros (`app_macro`) 已在 Asterisk 21 中移除；您必须使用 GOSUB 来实现子程序。

### 创建子程序

定义非常相似。看看下面为语音信箱定义的名为 stdexten 的子程序（选择您喜欢的名称）。在调用带有第一个参数（channel 名称）的 Dial 命令后，我们检查 ${DIALSTATUS} 以将呼叫逻辑发送到下一步。

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

调用子程序时，请注意在参数前使用括号。

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## 使用 Asterisk DB

为了实现呼叫转移和黑名单，我们需要一种存储和恢复数据的方法。幸运的是，Asterisk 提供了一种用于从名为 AstDB 的内置数据库中存储和检索数据的机制。在现代 Asterisk（包括 Asterisk 22）中，AstDB 由 **SQLite3**（文件 `/var/lib/asterisk/astdb.sqlite3`）支持；Asterisk 1.8 及更早版本使用 Berkeley DB v1。这类似于使用 family 和 key 分层概念的 Windows 注册表数据库。数据在 Asterisk 重启后仍然存在。Family/key API 与旧的后端相比没有变化；只有磁盘上的存储格式发生了变化。

### 函数、应用程序和 CLI 命令

有一些函数、应用程序和 CLI 命令可以与 AstDB 一起使用：

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

示例：

```
exten=_*21*XXXX,1,set(DB(CFBS/${CALLERID(num)}=${EXTEN:4}))
exten=s,1,set(temp=${DB(CFBS/${EXTEN})})
```

一些应用程序可用于操作 AstDB：

- DB_DELETE(<family/key>) — 返回并删除单个 key 的函数
- DBdeltree(<family>) — 删除整个 family/子树的应用程序

旧的 `DBdel()` 应用程序在 Asterisk 22 中已不存在。使用 `DB_DELETE()` dialplan 函数删除单个 key — 例如 `Set(x=${DB_DELETE(family/key)})`，或者作为写操作，`Set(DB_DELETE(family/key)=)`。`DBdeltree()`（删除整个 family/子树）仍然是一个应用程序。

也可以使用 CLI 命令来设置和删除 key：

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### 实现呼叫转移、DND 和黑名单

在此示例中，您将学习如何实现立即呼叫转移和遇忙呼叫转移。我们将使用 *21* 来编程立即呼叫转移，使用 *61* 来编程遇忙呼叫转移。要取消编程，请分别使用 #21# 和 #61#。使用上面的示例来填充数据库。使用的 family：

- CFIM – 立即呼叫转移
- CFBS – 遇忙呼叫转移
- DND – 请勿打扰

尝试通过拨号填充数据库：

- *21* (用于立即呼叫转移的目标 extension)
- *61* (用于遇忙呼叫转移的目标 extension)
- *41* (设置为请勿打扰的 extension)

使用 CLI 命令 database show 查看添加的 family、key 和值。

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### 呼叫转移、黑名单、DND

上面的子程序验证数据库是否包含对应于 CFIM、CFBS 或 DND 的 key:value 对，然后适当地处理它们。follow 子程序调用拨号例程：

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## 使用黑名单

旧的 `LookupBlacklist()` 应用程序已从 Asterisk 中**移除**（它与传统的“priority+101 跳转”机制一起消失了）。在 Asterisk 22 中，您直接使用 `DB_EXISTS()` 函数（它既测试 key，又在找到时将其值暴露在 `${DB_RESULT}` 中）加上 `GotoIf` 来构建黑名单。将每个被阻止的号码存储为 `blacklist` family 中的一个 key，然后在传入 context 的顶部检查呼叫者 ID：

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

当呼叫者的号码存在于数据库中时，`DB_EXISTS(blacklist/${CALLERID(num)})` 返回 `1`（将呼叫发送到 `blocked` context），否则返回 `0`，因此呼叫继续进行正常的 `Dial()`。

要将号码插入黑名单，我们可以使用与之前相同的资源，使用 *31* 后跟要列入黑名单的 extension。要从黑名单中删除号码，您应该使用 #31# 后跟要删除的号码。

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

您还可以使用控制台 CLI 将号码插入黑名单：

```
CLI>database put blacklist <name/number> 1
```

注意：任何值都可以与 key 相关联。`DB_EXISTS()` 测试搜索的是 key，而不是值。要从黑名单中清除号码，您可以使用：

```
CLI>database del blacklist <name/number>
```

## 基于时间的 context

在下图中，我们有一个带有三个 context 的 dial plan。[incoming] context 是通常接收呼叫的地方。我们包含了四行根据系统时间改变行为的代码，如下例所示：

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

现代 Asterisk（包括 22）使用**逗号**而不是管道来分隔时间包含字段。旧的管道形式（`include => context|times|weekdays|mdays|months`）被解析为普通的字面 context 名称，并且静默地无法应用任何时间条件。

在正常工作时间内，处理将被重定向到 mainmenu，它可能会调用一个 IVR 来处理传入呼叫。如果呼叫发生在下班后，它将调用 ${SECURITY} 变量中定义的安全 extension。如果安全 extension 没有接听呼叫，它将被发送到接线员的语音信箱。

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## 使用 gotoiftime() 的基于时间的消息

GotoIfTime() 语法如下所示。

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

在 Asterisk 22 中，字段分隔符是**逗号**，而不是管道（管道形式在 Asterisk 1.6 中已被弃用）。支持可选的 `timezone` 字段，每个分支标签使用通常的 `[[context,]extension,]priority` 形式。

此应用程序可以替换基于时间的 context，并且看起来更容易理解和阅读。您可以按如下方式指定时间：

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=1 到 31 之间的数字
- <hour>=0 到 23 之间的数字
- <minute>=0 到 59 之间的数字
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

日期和月份的名称不区分大小写。

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

如果呼叫是在周一至周五的 08:00 AM 到 06:00 PM 之间，则上述语句将处理转移到 normalhours context 中的 extension s。

## 使用 DISA 获取新的拨号音

DISA 或“直接内线系统访问”是一个允许用户接收第二个拨号音的系统。它允许用户再次拨打另一个目的地。它经常被技术人员在周末拨打长途电话进行技术支持时使用；他们不是直接从家中拨打目的地，而是拨打办公室的 DISA 号码，接收拨号音，然后拨打目的地。长途费用由公司承担，而不是由家庭电话承担。

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

示例：

```
exten => s,1,DISA(no-password,default)
```

使用上述语句，用户拨打 PBX，并且无需任何密码即可接收拨号音。任何使用 DISA 的呼叫都将使用 `default` context 进行处理。此应用程序的参数包括全局密码或文件中的个人密码。如果未指定 context，则假定为 `disa` context。如果您使用密码文件，则必须指定完整路径。也可以为 DISA 外部拨号指定呼叫者 ID。示例：

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 使用逗号作为参数分隔符（管道形式在 1.6 中已被弃用）。第一个参数是单个密码或密码文件的路径，当未给出时，默认 context 为 `disa`。

## 限制并发呼叫

GROUP() 函数允许您计算同一时间在一个组中拥有的活动 channel 数量。示例：您在里约热内卢有一个分支机构，那里的电话遵循模式 “_214X”。该位置由租用线路提供服务，保留 64K 用于语音带宽。在这种情况下，允许的最大呼叫数为 2（G.729，每个呼叫 30r.2K）。要将里约的呼叫限制为两个：

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## 语音信箱

语音信箱是一种计算机化的电话应答系统，它记录传入的语音消息，将它们保存在磁盘上或通过电子邮件发送。有时它有一个通讯录，您可以在其中按名称查找语音信箱。过去，语音信箱系统非常昂贵。现在，随着 IP 电话的普及，语音信箱已成为一项标准功能。

要配置语音信箱，您应该执行以下步骤。

**第 1 步：编辑 `voicemail.conf` 并设置常规参数。**

- `format` — 用于录制消息的 codec（例如，wav49, wav, gsm）
- `serveremail` — 电子邮件通知应显示来自谁
- `maxmsg` — 邮箱中的最大消息数；超过此阈值后，消息将被丢弃
- `maxsecs` — 语音信箱消息的最大长度（以秒为单位）
- `minsecs` — 消息的最小长度（以秒为单位）；低于此阈值，则不录制消息
- `maxsilence` — 将多少秒的静音视为消息结束

**第 2 步：编辑 `voicemail.conf` 并创建用户的邮箱。**

### Voicemail.conf

邮箱定义为每个邮箱一行，格式为：

```
mailboxID => pincode,fullname,email,pager-email,options
```

字段为：

- **MailboxID** — 通常是 extension 号码
- **Pincode** — 访问语音信箱系统的密码
- **Full name** — 由通讯录应用程序使用
- **E-mail** — 用于语音信箱通知的地址
- **Pager e-mail** — 通过 SMS 网关或寻呼机进行通知的地址
- **Options** — 每个邮箱的选项（与 `[general]` 中的选项相同，但应用于此邮箱）

语音信箱有几个控制其行为的选项。目前，我们将坚持使用默认选项，并专注于邮箱定义。在文件中的 `[general]` 部分之后，您开始配置邮箱 ID，每个都在其自己的 context 中。示例：

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

请查看文件 `voicemail.conf` 中的高级选项。

**第 3 步：配置文件 `extensions.conf`。**

下面，您有创建子程序和调用的说明，这些说明在 `extensions.conf` 中实现了语音信箱。我们使用 channel 变量 `${DIALSTATUS}` 的值将呼叫流重定向到适当的语音信箱菜单。

### 语音信箱子程序

## 使用 Voicemailmain() 应用程序

应用程序 voicemailmain() 用于配置语音信箱邮箱。用户可以拨打该应用程序，录制他们的问候语，并收听他们的语音信箱。要在 dial plan 中调用该应用程序，请使用：

```
exten=>9000,1,VoiceMailMain()
```

在下面，您将找到该应用程序可用的选项列表。

### 语音信箱应用程序语法

此应用程序允许呼叫方为指定的邮箱列表留言。当指定多个邮箱时，问候语将取自第一个指定的邮箱。如果指定的邮箱不存在，dial plan 执行将停止。语法如下所示：

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

在所有情况下，beep.gsm 文件将在录制开始前播放。语音信箱消息将存储在 inbox 目录中。

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

如果呼叫者在公告期间按 0（零），它将被移动到语音信箱当前 context 中的 ‘o’（out）extension。这可用于退出到接线员。如果呼叫者在录制期间按 # 或静音限制超时，录制将停止，呼叫将转到下一个优先级。确保在播放语音信箱后处理呼叫，如下所示。

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### 将语音信箱消息标记为紧急

您可以将某些消息标记为“紧急”。有两种方法可用于此：

- 在应用程序 voicemail() 中传递选项 ‘U’
- 在文件 voicemail.conf 中指定 review=yes。如果使用此选项，用户可以在录制语音说明后将消息标记为紧急。

## 将语音信箱发送到电子邮件

在某些情况下（比如我的情况），我们根本不使用 voicemailmain() 应用程序来阅读电子邮件。将所有消息发送到电子邮件并附上音频更简单、更实用。使用参数 ‘attach’ 和 ‘delete’，您可以将所有邮件发送到电子邮件并从邮箱中删除它们。

```
attach=yes
delete=yes
```

为了将语音信箱发送到电子邮件，语音信箱应用程序使用消息传输代理 (MTA)，这是您操作系统的一个组件。Debian 使用 Exim 作为 MTA。发送电子邮件的应用程序在 ‘mailcmd’ 参数中定义。

```
mailcmd =/usr/sbin/sendmail -t
```

在 Linux 的 Debian 发行版中，MTA 是 Exim。要在 Debian 中配置 Exim，请使用：

```
dpkg-reconfigure exim4-config
```

您可以选择让您的 MTA 直接通过 SMTP 或 smarthost（通常是您公司的邮件服务器）发送电子邮件。与您的电子邮件管理员确认从 Asterisk 服务器发送电子邮件到您的电子邮件服务器的最佳方式。

## 自定义电子邮件消息

您可以通过设置以下变量来控制消息的发送方式。电子邮件主题和电子邮件正文的变量：

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

电子邮件正文和主题是根据您在 `[general]` 的 `voicemail.conf` 部分中设置的模板构建的。您可以修改正文和主题，但消息的大小限制为 512 字节。在模板中，`\n` 插入换行符，`\t` 插入制表符。

下面的 `emailsubject` 示例很简单。`emailbody` 示例非常接近默认值；默认值仅在 CIDNAME 不为空时显示它，否则显示 CIDNUM，或者当两者都为空时显示“an unknown caller”。

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## 语音信箱 Web 界面

在源代码分发中有一个名为 `vmail.cgi` 的 Perl 脚本，位于 Asterisk 源代码树中的 `contrib/scripts/vmail.cgi`（它仍然随 Asterisk 22 一起提供）。命令 `make install` 不会安装此界面；您必须从源代码目录运行 `make webvmail`。此脚本需要安装 Perl 命令解释器和 Web 服务器（如 Apache）。

```
make webvmail
```

`make webvmail` 目标将脚本（setuid root）安装到您的 Web 服务器的 CGI 目录（`HTTP_CGIDIR`）中，并将支持图像从 `images/*.gif` 复制到 `HTTP_DOCSDIR/_asterisk`（默认情况下为 `/var/www/html/_asterisk`）。如果这些路径与您的 Web 服务器布局不匹配，请在运行目标之前编辑顶级 `Makefile` 中的 `HTTP_CGIDIR` 和 `HTTP_DOCSDIR` 变量。

## 语音信箱通知

您可以配置语音信箱，以便在您有新的语音信箱时向您的手机发送通知消息。在 Asterisk 22 中，消息等待指示 (MWI) 适用于 PJSIP 和 SIP 电话以及 DAHDI 电话。为了指示未听的语音信箱，指示灯可能会闪烁，或者电话可能会播放快门音。您需要在相应的 channel 配置文件中配置邮箱。示例：`pjsip.conf`（在 endpoint 部分）：

```
mailboxes=8590
```

在 PJSIP 中，邮箱提示是在 `pjsip.conf` 的 endpoint 部分内使用 `mailboxes` 选项设置的，而不是旧的 `sip.conf` 的 `mailbox=`。MWI 订阅由 `res_pjsip_mwi` 模块处理。

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### 实验：电话中的消息通知

此实验是使用 SIP softphone 进行测试的。1. 编辑 `pjsip.conf` 并在名为 4401 的设备的 endpoint 部分中添加 `mailboxes=4401`。2. 编辑 extensions.conf 并创建一个 extension 以将语音信箱录制到 4401 extensions。

```
exten=9008,n,voicemail(b4401)
```

3. 转到 CLI > 控制台并重新加载。4. 在 SipPulse Softphone 中，打开 SIP 帐户设置并启用帐户的语音信箱（消息等待）检查。5. 拨打 9008 并留言。6. 观察电话上的消息图标。

## 使用 directory 应用程序

此应用程序允许您快速找到要拨打的用户。名称和相应 extension 的列表是从语音信箱配置文件 voicemail.conf 中检索的。该应用程序的语法可以使用 core show application directory 显示：

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

### 实验：使用 directory 应用程序

1. 编辑 voicemail.conf 文件以在 dial plan 中添加两个 extension

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. 在您的 dial plan 中创建这些 extension

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. 转到控制台并重新加载 4. 拨打 9006 并为每个 extension (4400, 4401) 录制一个名称 5. 拨打 9007 并为其中一个 extension 选择姓氏的三个字母 (Eas=327)。如果这是正确的选项，请按 ‘1’ 转接到该名称。

## 实验：综合应用

到目前为止，您已经学习了几个 dial plan 概念。让我们将所有的应用程序、函数和概念放在一个 dial plan 示例中，以便您了解它们是如何一起使用的。让我们引导您完成下面场景的整个 PBX 配置。

- 4 个模拟 trunk
- 16 个基于 SIP 的 extension
- 3 个服务等级：
    - restrict（内部、本地和 1-800）
    - ld（长途）
    - ldi（国际）
- 下班后消息
- 自动总机

### 第 1 步 – 配置 channel

模拟 trunk (chan_dahdi.conf) 首先，我们将在 DAHDI channel 配置文件 chan_dahdi.conf 中配置模拟 trunk。在这种情况下，我们将使用带有 4 个 FXO 接口的 T400P Digium 卡。假设驱动程序已经加载，并且驱动程序配置文件 (/etc/dahdi/system.conf) 已正确配置。

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

SIP channel (pjsip.conf) 我们选择了从 2000 到 2099 的 dial plan 编号。将使用两个 codec：G.729 和 G.711 ulaw。前者将用于通过 Internet 或 WAN 使用 Asterisk 的电话，而后者将用于使用本地网络的电话。在 `pjsip.conf` 中，我们将仲裁哪些设备将属于每个服务等级（restrict, ld, ldi）。为了减少对暴力破解攻击的脆弱性，我们将使用电话的 MAC 地址作为设备名称。我强烈建议您使用强密码以避免暴力破解攻击！

我们定义了一个传输和三个可重用的模板 — 一个带有共享 codec 的 endpoint 基础、一个 userpass 认证和一个单联系人 AOR — 然后将每个设备附加到模板，并仅覆盖不同的部分（其服务等级 context 和凭据）。`host=dynamic` 成为电话注册的 AOR，`directmedia` 成为 `direct_media`：

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

[auth-userpass](!)
type=auth
auth_type=userpass

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-userpass)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-userpass)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-userpass)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### 第 2 步 – 配置 dial plan

现在让我们开始配置 extensions.conf。定义内部 extension 和本地拨号

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

定义 LD（长途）

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

定义国际呼叫

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### 第 3 步 - 使用自动总机接收呼叫

要接收呼叫，请使用两个 context。第一个用于正常工作时间操作，呼叫将由自动总机接收。第二个用于下班后，呼叫者将收到一条消息，例如“您已致电 XYZ 公司，我们的正常工作时间是上午 08:00 到下午 06:00；如果您知道目标 extension 号码，您可以现在尝试拨打它或挂断。”菜单：正常工作时间、下班后在下面的菜单中，系统将播放一条消息，警告呼叫者在正常工作时间之后联系了公司，允许呼叫者拨打目标 extension 号码（可能有人在正常工作时间之后工作）。

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

菜单：主菜单和销售部在正常工作时间内，呼叫由自动总机菜单接听，收到一条消息，例如“欢迎致电 XYZ 公司；按 1 转销售部，按 2 转技术支持，按 3 转培训部，或拨打所需的 extension 号码”。

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

有了所有这些语句，您的拨号计划功能现在就准备好了。在下一节中，我们将演示如何操作 PBX。

## 总结

在本章中，您学习了如何使用 IVR 或自动总机接收呼叫。您研究了 context 包含的概念并实现了一些示例。子程序被用来避免重复输入，Asterisk 数据库（AstDB，在 Asterisk 22 中由 SQLite3 支持）被用于需要数据存储的功能（例如，呼叫转移、请勿打扰、黑名单）。最后，您学习了如何实现下班后行为，并使用这些概念实现了一个完整的 dial plan。

## 测验

1. 基于时间的 context 包含使用形式 `include => context,<times>,<weekdays>,<mdays>,<months>`。那么 `include => normalhours,08:00-18:00,mon-fri,*,*` 是做什么的？
   - A. 在周一至周五，08:00 到 18:00 执行 extension
   - B. 在所有月份的每一天执行选项
   - C. 什么也不做；格式无效
2. 在现代 Asterisk（包括 Asterisk 22）中，基于时间的 `include =>` 和 `GotoIfTime()` 的字段由哪个字符分隔？
   - A. 管道 `|`
   - B. 逗号 `,`
   - C. 分号 `;`
   - D. 斜杠 `/`
3. 要同时拨打多个 channel（同时响铃），您在 `Dial()` 中使用 ___ 字符将它们分隔开。
4. 在等待呼叫者拨打 extension 时播放提示音的语音菜单通常使用 ___ 应用程序创建。
5. 您可以使用 ___ 语句在 `extensions.conf` 中包含另一个文件的内容（注意：这与 `include =>` context 语句不同）。
6. 在 Asterisk 22 中，内置的 AstDB 数据库由以下哪项支持：
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. 当您使用 `Dial(type1/identifier1&type2/identifier2)` 时，Asterisk 会按顺序拨打每个 channel，并在它们之间等待 20 秒。
   - A. 错误
   - B. 正确
8. 使用 Background() 应用程序，您必须等待消息播放完毕，然后才能按 DTMF 数字选择选项。
   - A. 错误
   - B. 正确
9. 给定语法 `Goto([[context,]extension,]priority)`，以下哪些是 Goto() 应用程序的有效调用？（标记所有适用的项）
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. 要在 Asterisk 22 dial plan 中从 AstDB 中删除单个 key，您可以使用：
    - A. `DBdel()` 应用程序
    - B. `DB_DELETE()` 函数
    - C. `DBdeltree()` 应用程序
    - D. `LookupBlacklist()` 应用程序

**答案：** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
