# 使用 PBX 功能

在 SIP 系统中，大多数电话功能都是在 endpoint 中实现的。市面上存在各种各样的 SIP 电话和制造商，因此互操作性无法得到保证。Asterisk 开发团队在 PBX 本身中实现了大部分功能，做得非常出色，使得 Asterisk 几乎不依赖于特定的 endpoint。然而，有时你会发现电话和 Asterisk 本身都在执行相同的功能。电话与 PBX 的集成是可用性方面的下一个前沿领域，也是目前专有系统关注的重点。在本章中，你将学习如何使用这些功能中的大部分。

## 目标

学完本章后，你将能够理解并使用：

- 呼叫驻留 (Call Parking)
- 呼叫代答 (Call Pickup)
- 呼叫转移 (Call Transfer)
- 电话会议 (ConfBridge)
- 呼叫录音 (Call Recording)
- 保持音乐 (Music on hold)

## 功能的实现位置

首先，理解 PBX 功能是在何时执行的，以及何时由电话完成所有工作，这一点非常重要。例如，你可以使用电话上的 TRANSFER 按钮转移呼叫，也可以通过拨打 #（由 PBX 本身执行的无条件转移）来转移。

## 由 Asterisk 实现的功能

这些功能由 Asterisk 代码在 PBX 中实现：

- 保持音乐
- 呼叫驻留
- 呼叫代答
- 呼叫录音
- ConfBridge 会议室
- 呼叫转移（盲转和咨询转移）

## 通常由 dialplan 实现的功能

这些功能需要在 Asterisk dialplan (extensions.conf) 中进行编程：

- 遇忙呼叫前转
- 立即呼叫前转
- 无应答呼叫前转
- 呼叫过滤（黑名单）
- 免打扰
- 重拨

## 通常由电话实现的功能

这些功能由电话的固件实现：

![PBX 功能通常的实现位置：在 Asterisk 本身、dialplan 中，或在电话中](../images/13-pbx-features-fig01.png)

- 呼叫保持
- 盲转
- 咨询转移
- 三方会议
- 消息等待指示灯

## 功能配置文件

本章介绍的一些功能是在 features.conf 配置文件中配置的。通过修改此文件，可以更改某些功能的行为。我们在下方包含了相关的摘录。在本章的后续部分，我们将介绍每个功能。示例文件摘录（Asterisk 22）

![features.conf 的 `[featuremap]` 部分，包含默认的 DTMF 功能代码](../images/13-pbx-features-fig02.png)

> **[第二版注]** 从 Asterisk 12+ 开始，呼叫驻留功能已从 `features.conf`/`app_features` 移出，进入其自己的模块 `res_parking`，并在 `res_parking.conf` 中进行配置。下方的 parking-lot 块（parkext、parkpos、context、parkingtime 等）位于 `res_parking.conf` 中，并使用 Asterisk 22 `res_parking.conf.sample` 中的语法显示。 `[featuremap]` 部分（DTMF 功能代码，包括 `parkcall`）保留在 `features.conf` 中。

parking-lot 选项位于 `res_parking.conf`。即使配置文件中不存在，名为 `default` 的 parking lot 也始终存在。以下摘录取自 Asterisk 22 `res_parking.conf.sample`：

```
; res_parking.conf
[default]                       ; Default Parking Lot
parkext => 700                  ; What extension to dial to park. (optional; if
                                ; specified, extensions will be created for parkext and
                                ; the whole range of parkpos)
parkpos => 701-720              ; What range of parking spaces to use - must be numeric.
                                ; Creates these spaces as extensions if parkext is set.
context => parkedcalls          ; Which context parked calls and the default park
                                ; extension are created in
;parkingtime => 45             ; Number of seconds a call can be parked before returning
;comebacktoorigin = yes        ; When a parked call times out, attempt to send it back to
                               ; the peer that parked it (default is yes)
;courtesytone = beep           ; Sound file to play when someone picks up a parked call
;parkedplay = caller           ; Who to play courtesytone to: parked, caller, both (default caller)
;parkedcalltransfers = caller  ; Enable DTMF transfers when picking up a parked call (default no)
;parkedcallreparking = caller  ; Enable DTMF parking when picking up a parked call (default no)
;parkedcallhangup = caller     ; Enable DTMF hangups when picking up a parked call (default no)
;findslot => next              ; 'next' uses the next space after the most recently used one;
                               ; 'first' (default) uses the lowest-numbered space available
;parkedmusicclass = default    ; MOH class to use for the parked channel
```

DTMF 功能代码（包括一步 `parkcall`）保留在 `features.conf` 的 `[featuremap]` 部分中：

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t
option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option
in the Dial() or Queue() app call!
;automon => *1                  ; One Touch Record a.k.a. Touch Monitor -- Make sure to set the W
and/or w option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## 呼叫转移

呼叫转移可以由电话、ATA 或 Asterisk 本身实现。请参阅你的电话手册以了解如何转移呼叫。如果你的电话不支持呼叫转移，你可以使用 Asterisk 来完成此任务。呼叫转移以两种不同的方式实现。第一种方式是使用盲转功能：拨打 #，后跟要转移到的号码。有时你会使用 IP 电话或 IP softphone 的转移功能。你可以通过编辑 features.conf 文件中的 blindxfer 参数来更改转移字符。你可以通过删除 features.conf 文件中 atxfer 参数前的 ; 来启用 Asterisk 中的辅助转移。在通话过程中，你可以按 *2。Asterisk 会说“transfer”并给你一个拨号音。呼叫者会被发送到保持音乐。在你与目标人员交谈并挂断电话后，系统会将呼叫者桥接到目标。

![呼叫转移：盲转（通话期间按 #）和咨询转移（按 *2）的步骤](../images/13-pbx-features-fig03.png)

### 配置任务列表

1. 如果电话是基于 SIP 的，请确保 directmedia 选项等于 no，或者在 dial() 应用程序中使用 t 或 T 选项

## 呼叫驻留

此功能用于驻留呼叫。例如，当你离开房间接听电话，并希望将呼叫转回你的办公桌时，这很有帮助。你可以通过将呼叫驻留在某个 extension 来实现这一点。当你到达办公桌时，只需拨打驻留 extension 的号码即可恢复呼叫。

![呼叫驻留：拨打 700 将呼叫驻留到第一个空闲槽位（701–720）；Asterisk 会播报槽位，你可以从任何电话拨打该槽位以取回呼叫](../images/13-pbx-features-fig04.png)

默认情况下，700 extension 用于驻留呼叫。在通话过程中，按 # 将呼叫转移到 700 extension。现在 Asterisk 将播报你的驻留 extension，例如 701 或 702。挂断电话，呼叫者将被置于保持状态。走到你的办公桌电话旁，拨打播报的驻留 extension 以恢复呼叫。如果呼叫者被驻留了很长时间，超时功能将触发，最初拨打的 extension 将再次响铃。

### 配置任务列表

按照以下步骤启用呼叫驻留。第 1 步：使 parking lot 可从你的 dialplan 访问（必需）。默认 parking lot 的 `context` 是 `parkedcalls`（在 `res_parking.conf` 中设置）。将该 context 包含在你电话拨出的 context 中，在 `extensions.conf` 中：

```
include => parkedcalls
```

第 2 步：通过拨打 #700 测试呼叫驻留功能。注意：

- 驻留 extension 不会显示在 dialplan show CLI 命令中。
- 修改 parking 配置文件后，必须重新加载 parking 模块：`module reload res_parking.so`。对于 features.conf 的更改，使用 `module reload features.so`。
- 要驻留呼叫，你需要转移到 #700。验证 dial() 应用程序中的 t 和 T 选项。

## 呼叫代答

呼叫代答允许你代接同一呼叫组中同事的呼叫。例如，这有助于避免必须起身去接听房间里另一个人的电话，而那个人不在场。通过拨打 *8，你可以代接呼叫组内的呼叫。此号码可以在

```
features.conf file.
```

![呼叫代答：成员只能代接自己组内的呼叫；操作员 (pickupgroup=1,2,3) 可以代接来自每个组的呼叫](../images/13-pbx-features-fig05.png)

### 配置任务列表

按照以下步骤配置呼叫代答功能。第 1 步：为你的 extensions 配置一个呼叫组。这是在通道配置文件 (pjsip.conf, iax.conf, chan_dahdi.conf) 中完成的。对于 PJSIP endpoints，在 `pjsip.conf` 的 endpoint 部分设置 `call_group` 和 `pickup_group`（pjsip.conf 使用 snake_case 选项名称）。此任务是必需的。

对于 PJSIP (pjsip.conf)：
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


第 2 步：更改呼叫代答功能号码（可选）。

```
pickupexten=*8; Configures the call pickup extension
```

## 会议（电话会议）

在 Asterisk 上实现会议有多种方法。第一个选项是简单地使用电话的三方会议功能。通过在电话中使用此功能，你不需要服务器本身的任何支持。但是，当你需要 3 人以上的会议时，你应该运行一个会议室。Asterisk 的现代会议应用程序是 ConfBridge (`app_confbridge`)。

ConfBridge 支持高清语音会议和视频会议。视频会议有一些限制，例如没有转码——所有参与者必须使用相同的 codec 和配置文件。视频会议使用“跟随发言者”模式，显示最后发言人的图像。你可以轻松地在 ConfBridge 中配置新的 DTMF 菜单。

> **[第二版注]** MeetMe (`app_meetme`) 在 **Asterisk 19 中被弃用**，并计划在 Asterisk 21 中移除，但该移除已被暂停（应 ViciDial 项目的要求）。模块源代码仍随 Asterisk 22 一起发布，但它需要 DAHDI，并且**不是由默认的 Asterisk 22 构建版本构建的**——标准安装没有 `app_meetme.so`，并且 `MeetMe()` 应用程序不可用。所有新的会议室部署必须使用 ConfBridge。下方的 MeetMe 部分仅供历史参考。

### Confbridge

要启动会议室，语法如下所示。

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

要获取该命令的完整描述，你可以使用 core show application confbridge。

![`core show application confbridge` 的输出，显示概要、语法以及 bridge_profile、user_profile 和 menu 参数](../images/13-pbx-features-fig06.png)

如上所示，有三个重要的部分：Bridge_profile：你在 confbridge.conf 文件中定义配置文件。在那里你可以选择最大参与者人数、录音、video_mode 以及许多其他 bridge 参数。

在这里重现整个示例文件没有意义，所以让我给你一个关于如何在 confbridge.conf 文件中配置 bridge_profile 的简单示例。

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

User_profile：在这里你定义特定于用户的选项，例如用户是否为管理员。保持音乐和许多其他选项可以按用户设置。示例：

```
[admin_user]
type=user
admin=yes
```

Menu：在 menu 部分，你可以定义应用程序的键盘映射，用于切换静音和取消静音。查看 confbridge.conf 文件以查看选项。示例：

```
[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
4=decrease_talking_volume
5=increase_talking_volume
6=leave_conference
```

#### Confbridge 函数

会议 bridge 选项可以使用 CONFBRIDGE() 函数在 dialplan 中动态传递。请参阅以下示例：

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

## Meetme（旧版——已弃用，Asterisk 22 默认不构建）

> **[第二版注]** `app_meetme` 在 Asterisk 19 中被弃用。其在 Asterisk 21 中的计划移除已被暂停，因此源代码仍随 Asterisk 22 一起发布，但该模块不是由默认的 Asterisk 22 构建版本构建的（它依赖于 DAHDI）。因此，标准的 Asterisk 22 安装没有 `MeetMe()` 应用程序。以下内容仅供历史参考，供从旧系统升级的读者使用。**对于新安装，请使用 ConfBridge（见上文）。** ConfBridge 不需要 DAHDI 依赖项和 `dahdi_dummy` 模块。

或者，在较旧的 Asterisk 版本中，你可以使用 meetme() 应用程序。Meetme 是一个非常易于使用的会议 bridge。请记住，meetme 在 Asterisk 19 中已被弃用，并依赖 DAHDI 模块进行同步。

![MeetMe 会议类型——单发言人、密码保护和动态会议——都需要 Zaptel/DAHDI 定时源](../images/13-pbx-features-fig07.png)

### meetme() 应用程序

使用 meetme show CLI 命令，你可以获得上述描述。要使用 meetme，你需要编译 DAHDI 驱动程序并至少加载一个 DAHDI 内核模块。如果你没有安装至少一张 DAHDI 卡，请加载 dahdi_dummy 内核模块以提供定时源。描述：

![MeetMe() 应用程序：语法 `MeetMe([confno][,[options][,pin]])` 及其主要选项标志](../images/13-pbx-features-fig08.png)

meetme() 应用程序将用户带入指定的 meetme 会议。如果省略会议号码，系统将提示用户输入一个。用户可以通过挂断电话离开会议，或者如果指定了 p 选项，则通过按 # 离开。请注意：必须存在 DAHDI 内核模块和至少一个硬件驱动程序（或 dahdi_dummy），会议才能正常运行。此外，必须加载 chan_dahdi 通道驱动程序，i 和 r 选项才能正常工作。

> **[第二版注]** 后续的选项标志和管理命令列表描述了旧版 `app_meetme` 接口，并反映了历史上的 `MeetMe()`/`MeetMeAdmin()` 文档。由于 `app_meetme` 不是由默认的 Asterisk 22 安装构建的，因此这些标志无法在运行的 Asterisk 22 系统上进行确认；它们是为维护旧部署的读者转载的。在 Asterisk 22 上，请使用 ConfBridge 和 `CONFBRIDGE()` dialplan 函数。

选项字符串可以包含零个、一个或多个以下字符：

- 'a' -- 设置管理员模式
- 'A' -- 设置标记模式
- 'b' – 运行 ${MEETME_AGI_BACKGROUND} 中指定的 AGI 脚本。默认：conf-background.agi（注意：这不适用于同一会议中的非 DAHDI 通道）
- 'c' -- 加入会议时播报用户人数
- 'd' -- 动态添加会议
- 'D' -- 动态添加会议，提示输入 PIN
- 'e' -- 选择一个空会议
- 'E' -- 选择一个无 PIN 的空会议
- 'i' -- 播报用户加入/离开，并进行审核
- 'I' -- 播报用户加入/离开，不进行审核
- 'l' -- 设置仅收听模式（仅收听，不能说话）
- 'm' -- 设置初始静音
- 'M' -- 当会议只有一个呼叫者时启用保持音乐
- 'o' -- 设置发言者优化，将未发言的发言者视为静音，这意味着 (a) 传输时不进行编码，并且 (b) 未注册为发言的接收音频被忽略，从而不会导致背景噪音堆积
- 'p' -- 允许用户通过按 '#' 退出会议
- 'P' -- 即使指定了 pin，也始终提示输入 pin
- 'q' -- 静音模式（不播放进入/离开声音）
- 'r' -- 录制会议（使用格式 ${MEETME_RECORDINGFORMAT} 录制为 ${MEETME_RECORDINGFILE}）。默认文件名为 meetme-conf-rec-${CONFNO}-${UNIQUEID}，默认格式为 wav。
- 's' -- 当收到 '*' 时显示菜单（用户或管理员）（'send' 到菜单）
- 't' -- 设置仅说话模式。（仅说话，不能收听）
- 'T' -- 设置发言者检测（发送到 manager 接口和 meetme 列表）
- 'w[(<secs>)]' -- 等待直到标记用户进入会议
- 'x' -- 当最后一个标记用户退出时关闭会议
- 'X' -- 允许用户通过输入有效的单数字 extension ${MEETME_EXIT_CONTEXT} 或当前 context（如果未定义该变量）来退出会议。
- '1' -- 当第一人进入时不播放消息

### Meetme 配置文件

此文件用于配置 meetme 应用程序。例如：

```
;
; Configuration file for MeetMe simple conference rooms for Asterisk of course.
;
; This configuration file is read every time you call app meetme()
[general]
;audiobuffers=32        ; The number of 20ms audio buffers to be used
                        ; when feeding audio frames from non-DAHDI channels
                        ; into the conference; larger numbers will allow
                        ; for the conference to 'de-jitter' audio that arrives
                        ; at different timing than the conference's timing
                        ; source, but can also allow for latency in hearing
                        ; the audio from the speaker. Minimum value is 2,
                        ; maximum value is 32.
;
[rooms]
;
; Usage is conf => confno[,pin][,adminpin]
;
conf=>9000
conf=>9001,123456
```

不需要使用 reload 或 restart 来让 Asterisk 查看 meetme.conf 文件中的更改。

### Meetme 相关应用程序

meetme() 应用程序还有两个其他支持应用程序。

```
MeetMeCount(confno[|var])
```

这会播放会议中的用户数量。如果指定了变量，它不会播放消息，而是将用户数量设置为该变量。

```
MeetMeAdmin(confno,command,[user]):
```

运行会议的管理命令：

- 'e' -- 踢出最后加入的用户
- 'k' -- 将一名用户踢出会议
- 'K' -- 将所有用户踢出会议
- 'l' -- 解锁会议
- 'L' -- 锁定会议
- 'm' -- 取消一名用户的静音
- 'M' -- 将一名用户静音
- 'n' -- 取消会议中所有用户的静音
- 'N' -- 将会议中所有非管理员用户静音
- 'r' -- 重置一名用户的音量设置
- 'R' -- 重置所有用户的音量设置
- 'r' -- 降低整个会议的说话音量
- 'S' -- 提高整个会议的说话音量
- 't' -- 降低一名用户的说话音量
- 'T' -- 降低所有用户的说话音量
- 'u' -- 降低一名用户的收听音量
- 'U' -- 降低所有用户的收听音量
- 'v' -- 降低整个会议的收听音量
- 'V' -- 提高整个会议的收听音量

### Meetme 配置任务列表

按照以下步骤配置 meetme 会议应用程序。第 1 步：选择 Meetme 会议室的 extension（必需）第 2 步：编辑 meetme.conf 文件以配置密码（可选）

### 示例

示例 #1：简单的 meetme 会议室 1。在 extensions.conf 文件中，创建会议室 101

```
exten=>500,1,MeetMe(101,,123456)
```

2. 在 meetme.conf 文件中，为会议室 101 建立密码。重要提示：meetme() 应用程序需要一个计时器才能工作。如果你没有安装和配置 Digium 硬件，请使用 dahdi_dummy 作为定时源。

## 呼叫录音

在 Asterisk 中录制呼叫有多种方法。你可以使用 mixmonitor() 应用程序轻松录制呼叫。

### 使用 mixmonitor 应用程序

mixmonitor 应用程序将当前通道中的音频录制到指定文件。如果文件名是绝对路径，它将使用该路径。否则，它会在 asterisk.conf 中配置的监控目录中创建文件。

![MixMonitor() 应用程序：将通道的音频录制并混合到文件中，具有追加、仅桥接和音量调整选项](../images/13-pbx-features-fig09.png)

### Mixmonitor()

录制呼叫并在录制期间混合音频 [描述] MixMonitor(<file>.<ext>[|<options>[|<command>]]) 将当前通道上的音频录制到指定文件。选项：a- 追加到文件而不是覆盖它。b-仅在通道被桥接时将音频保存到文件。注意：不包括会议。v(<x>) - 将听到的音量调整 <x> 倍 V(<x>) - 将说话的音量调整 <x> 倍 W(<x>) - 调整听到和说话的音量 有效选项：

- a - 追加到文件而不是覆盖它。
- b - 仅在通道被桥接时将音频保存到文件。
- 注意：不包括会议。
- v(<x>) - 将听到的音量调整 <x> 倍（范围从 -4 到 4）
- V(<x>) - 将说话的音量调整 <x> 倍（范围从 -4 到 4）
- W(<x>) - 将听到和说话的音量调整 <x> 倍（范围从 -4 到 4）
- <command> 将在录制结束时执行。任何匹配 ^{X} 的字符串都将被取消转义为 ${X}，并且所有变量都将在那时进行评估。变量 MIXMONITOR_FILENAME 将包含用于录制的文件名。

一个有趣的资源是 automon，它允许你只需拨打 *1 即可立即开始录制。示例：

```
exten=>_4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten=>_4XXX,2,Dial(PJSIP/${EXTEN},20,jtTwW);wW enables the recording.
```

音频通道分为输入 (IN) 和输出 (OUT)，并被分成两个不同的文件，位于目录 /var/spool/asterisk/monitor 中。这两个文件可以使用 sox 应用程序进行混合。

```
debian#soxmix *in.wav *out.wav output.wav
```

如果你不想在 Dial() 应用程序之前使用 Set()，你可以在 globals 部分设置它：

```
[globals]
DYNAMIC_FEATURES=>automon
```

### 保持音乐

保持音乐 (MOH) 在 1.0、1.2 和 1.4 版本之间发生了几次变化。在最新版本中，MOH 默认为“FILE-BASED”。换句话说，Asterisk 将以 g729、alaw、ulaw 和 gsm 等格式提供 MOH 文件。因此，在将音乐发送到通道之前，无需对其进行转码。这节省了处理器时间，对于那些在生产系统上工作的人来说，这是一个受欢迎的修改。在旧版本中，MOH 通常由 MP3 提供（仍然可以那样配置）。提供 MP3 格式的 MOH 会迫使 Asterisk 进行转码，在此过程中消耗宝贵的 CPU 资源。新的配置文件如下所示。请注意，默认类现在使用原生文件格式 mode=files。所有其他模式都被注释掉了。每个部分都是一个类。此时唯一未注释的类是 default。如果你想为不同的文件设置不同的类，你需要创建新的部分（类）。

![musiconhold.conf 示例配置，列出了有效的 MOH 模式（quietmp3、mp3、custom、files 等）](../images/13-pbx-features-fig10.png)

```
; Music on Hold -- Sample Configuration
;[samplemp3]
;mode=quietmp3
;directory=/var/lib/asterisk/mohmp3
;
; valid mode options:
; quietmp3      -- default
; mp3           -- loud
; mp3nb         -- unbuffered
; quietmp3nb    -- quiet unbuffered
; custom        -- run a custom application (See examples below)
; files         -- read files from a directory in any Asterisk supported
;                  media format. (See examples below)
;[manual]
;mode=custom
; Note that with mode=custom, a directory is not required, such as when reading
; from a stream.
;directory=/var/lib/asterisk/mohmp3
;application=/usr/bin/mpg123 -q -r 8000 -f 8192 -b 2048 --mono -s
;[ulawstream]
;mode=custom
;application=/usr/bin/streamplayer 192.168.100.52 888
;format=ulaw
; mpg123 on Solaris does not always exit properly; madplay may be a better
; choice
;[solaris]
;mode=custom
;directory=/var/lib/asterisk/mohmp3
;application=/site/sw/bin/madplay -Q -o raw:- --mono -R 8000 -a -12
;
;
; File-based (native) music on hold
;
; This plays files directly from the specified directory, no external
; processes are required. Files are played in normal sorting order
; (same as a sorted directory listing), and no volume or other
; sound adjustments are available. If the file is available in
; the same format as the channel's codec, then it will be played
; without transcoding (same as Playback would do in the dialplan).
; Files can be present in as many formats as you wish, and the
; 'best' format will be chosen at playback time.
;
; NOTE:
; If you are not using "autoload" in modules.conf, then you
; must ensure that the format modules for any formats you wish
; to use are loaded _before_ res_musiconhold. If you do not do
; this, res_musiconhold will skip the files it is not able to
; understand when it loads.
;
[default]
mode=files
directory=/var/lib/asterisk/moh
;
;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes     ; Play the files in a random order
```

### MOH 配置任务

现在，要使用保持音乐，请在通道配置文件（chan_dahdi.conf, pjsip.conf, iax.conf 等）中设置 MOH 类。对于 PJSIP endpoints，在 `pjsip.conf` 的 endpoint 部分设置 `moh_suggest`（旧版 `musicclass` 选项名称适用于 chan_dahdi 和其他通道驱动程序，不适用于 PJSIP）。安装的免费音乐现在采用 wav 格式。在安装时，你可以选择（使用 make menuselect）可用的 MOH 文件格式。如果你想添加新的 MOH 文件，你必须以所需的格式提供它们。例如：

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

在 dialplan 中，你可以使用以下示例听到 MOH：

```
Exten=>100,1,SetMusicOnHold(default)
Exten=>100,2,Dial(DAHDI/2)
```

要配置 extensions.conf 文件以测试 MOH：

```
[local]
exten => 6601,1,WaitMusicOnHold(30)
```

## 应用程序映射

应用程序映射允许你通过使用 features.conf 文件的 `[applicationmap]` 部分来添加新功能。假设你需要识别你正在接听呼叫中心的客户类型。你可以为每种客户类型创建一个应用程序映射，它可以计算每种类型的已应答客户数量。

## 测验

1. 关于呼叫驻留，哪些陈述是正确的？
   - A. 默认情况下，extension 800 用于呼叫驻留。
   - B. 当你离开办公桌并接到电话时，你可以驻留它；系统会播报驻留槽位，你可以从任何电话拨打该槽位以取回呼叫。
   - C. 默认情况下，extension 700 驻留呼叫，呼叫被驻留在槽位 701–720。
   - D. 你拨打 700 以取回驻留的呼叫。
2. 要使用呼叫代答功能，所有 extensions 必须在同一个 ___ 中。对于 DAHDI 通道，这是在 ___ 文件中配置的。
3. 转移呼叫时，你可以在 ___ 转移（不先咨询目标）和 ___ 转移（在完成之前与目标交谈）之间进行选择。
4. 要进行辅助（咨询）转移，你使用 ___ 序列；对于盲转，你使用 ___。
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. 要在 Asterisk 22 中托管电话会议，你使用 ___ 应用程序。
6. 在 ConfBridge 中，通过在用户配置文件（`confbridge.conf`）中设置 ___，授予参与者管理员权限（踢人、静音他人、锁定会议室）：
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. 保持音乐的最佳格式是 MP3，因为它在 Asterisk 服务器上使用的处理能力非常小。
   - A. 正确
   - B. 错误
8. 要从特定的呼叫组代答呼叫，你必须在匹配的 ___ 组中。
9. 你可以使用 MixMonitor() 应用程序或一键式 (automon) 功能录制呼叫。默认情况下，automon 使用 ___ DTMF 序列。
   - A. *1
   - B. *2
   - C. #3
   - D. #1
10. 在 ConfBridge 中，哪个 `confbridge.conf` 用户配置文件选项使参与者在加入时处于静音状态（他们可以听到会议，但在取消静音之前无法被听到）？
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**答案：** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — 盲转；咨询转移 · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — A · 10 — A
