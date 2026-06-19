# 使用 PBX 功能

在 SIP 系统中，大多数电话功能都是在 endpoint 中实现的。市面上存在各种各样的 SIP 电话和制造商，其互操作性无法得到保证。Asterisk 开发团队在 PBX 本身中实现了大部分功能，做得非常出色，使得 Asterisk 几乎不依赖于特定的 endpoint。然而，有时你会发现电话和 Asterisk 本身都在执行相同的功能。电话与 PBX 的集成是可用性方面的下一个前沿领域，也是目前私有系统关注的重点。在本章中，你将学习如何使用这些功能中的大多数。

## 目标

读完本章后，你将能够理解并使用：

- 呼叫驻留 (Call Parking)
- 呼叫代答 (Call Pickup)
- 呼叫转移 (Call Transfer)
- 电话会议 (ConfBridge)
- 呼叫录音 (Call Recording)
- 保持音乐 (Music on hold)

## 功能的实现位置

首先，理解 PBX 功能是在何时执行，以及何时由电话完成所有工作，这一点非常重要。例如，你可以使用电话上的 TRANSFER 按钮转移呼叫，也可以通过拨打 #（由 PBX 本身执行的无条件转移）来转移。

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

![PBX 功能通常的实现位置：在 Asterisk 本身、在 dialplan 中，或在电话中](../images/13-pbx-features-fig01.png)

- 呼叫保持
- 盲转
- 咨询转移
- 三方会议
- 消息等待指示灯

## 功能配置文件

本章介绍的一些功能是在 features.conf 配置文件中配置的。通过修改此文件，可以更改某些功能的行为。我们在下方包含了相关的摘录。在本章的后续部分，我们将描述每个功能。示例文件摘录（Asterisk 22）

![features.conf 的 `[featuremap]` 部分，包含默认的 DTMF 功能码](../images/13-pbx-features-fig02.png)

从 Asterisk 12 开始，呼叫驻留功能已从 `features.conf` 移出，成为其自己的模块 `res_parking`，并在 `res_parking.conf` 中进行配置。下方的 parking-lot 块（`parkext`、`parkpos`、`context`、`parkingtime`等）位于 `res_parking.conf` 中。而 `[featuremap]` 部分（DTMF 功能码，包括 `parkcall`）保留在 `features.conf` 中。

parking-lot 选项位于 `res_parking.conf`。即使配置文件中不存在，名为 `default` 的 parking lot 也始终存在。下方的摘录取自 Asterisk 22 的 `res_parking.conf.sample`：

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

DTMF 功能码（包括一步式 `parkcall`）保留在 `features.conf` 的 `[featuremap]` 部分中：

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t
option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option
in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## 呼叫转移

呼叫转移可以由电话、ATA 或 Asterisk 本身实现。请参阅你的电话手册以了解如何转移呼叫。如果你的电话不支持呼叫转移，你可以使用 Asterisk 来完成此任务。呼叫转移有两种实现方式。第一种方式是使用盲转功能：拨打 #，后跟要转移到的号码。有时你会使用 IP 电话或 IP softphone 的转移功能。你可以通过编辑 features.conf 文件中的 blindxfer 参数来更改转移字符。你可以通过删除 features.conf 文件中 atxfer 参数前的 ; 来启用 Asterisk 中的辅助转移。在通话过程中，你可以按 *2。Asterisk 会说“transfer”并给你拨号音。呼叫者会被置于保持音乐中。在你与目标人员通话并挂断电话后，系统会将呼叫者桥接到目标。

![呼叫转移：盲转（通话期间按 #）和咨询转移（按 *2）的步骤](../images/13-pbx-features-fig03.png)

### 配置任务列表

1. 对于 PJSIP endpoint，请确保选项 `direct_media` 设置为 `no`（以便媒体流经 Asterisk 且功能码可被检测到），或者在 `Dial()` 应用程序中使用 `t`/`T` 选项。

## 呼叫驻留

此功能用于驻留呼叫。例如，当你不在房间内接听电话，但想将呼叫转回你的办公桌时，这很有帮助。你可以通过将呼叫驻留在某个 extension 来实现这一点。当你回到办公桌时，只需拨打驻留 extension 的号码即可恢复呼叫。

![呼叫驻留：拨打 700 将呼叫驻留到第一个空闲槽位（701–720）；Asterisk 会播报槽位，你可以从任何电话拨打该槽位以取回呼叫](../images/13-pbx-features-fig04.png)

默认情况下，700 extension 用于驻留呼叫。在通话过程中，按 # 将呼叫转移到 700 extension。现在 Asterisk 将播报你的驻留 extension，例如 701 或 702。挂断电话，呼叫者将被置于保持状态。走到你的办公桌电话旁，拨打播报的驻留 extension 即可恢复呼叫。如果呼叫者被驻留时间过长，超时功能将触发，最初拨打的 extension 将再次振铃。

### 配置任务列表

按照以下步骤启用呼叫驻留。第 1 步：使 parking lot 可从你的 dialplan 访问（必需）。默认 parking lot 的 `context` 是 `parkedcalls`（在 `res_parking.conf` 中设置）。将该 context 包含在你的电话拨号所在的 context 中，即 `extensions.conf`：

```
include => parkedcalls
```

第 2 步：通过拨打 #700 测试呼叫驻留功能。注意：

- 驻留 extension 不会显示在 dialplan show CLI 命令中。
- 修改驻留配置文件后，必须重新加载驻留模块：`module reload res_parking.so`。对于 features.conf 的更改，使用 `module reload features.so`。
- 要驻留呼叫，你需要转移到 #700。验证 `Dial()` 应用程序中的 `t` 和 `T` 选项。

## 呼叫代答

呼叫代答允许你代接同一呼叫组中同事的电话。例如，这有助于避免必须起身去接听房间里另一个人的电话，而那个人恰好不在。通过拨打 *8，你可以代接呼叫组内的呼叫。此号码可以在

```
features.conf file.
```

![呼叫代答：成员只能代接组内的呼叫；操作员（pickupgroup=1,2,3）可以代接来自每个组的呼叫](../images/13-pbx-features-fig05.png)

### 配置任务列表

按照以下步骤配置呼叫代答功能。第 1 步：为你的 extensions 配置一个呼叫组。这是在通道配置文件（pjsip.conf, iax.conf, chan_dahdi.conf）中完成的。对于 PJSIP endpoints，在 `pjsip.conf` 的 endpoint 部分设置 `call_group` 和 `pickup_group`（pjsip.conf 使用 snake_case 选项名称）。此任务是必需的。

对于 PJSIP (pjsip.conf)：
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


第 2 步：更改呼叫代答功能号码（可选）。这是在 `features.conf` 的 `[general]` 部分设置的，而不是在 `pjsip.conf` 中：

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## 会议（电话会议）

在 Asterisk 上实现会议有多种方法。第一个选项是简单地使用电话的三方会议功能。通过在电话上使用此功能，你不需要服务器端的任何支持。但是，当你需要超过 3 人的会议时，你应该运行一个会议室。Asterisk 的现代会议应用程序是 ConfBridge (`app_confbridge`)。

ConfBridge 支持高清语音会议和视频会议。视频会议有一些限制，例如不支持转码——所有参与者必须使用相同的 codec 和配置文件。视频会议使用“跟随发言者”模式，显示最后发言人的图像。你可以在 ConfBridge 中轻松配置新的 DTMF 菜单。

ConfBridge 取代了旧的 MeetMe 应用程序，后者在 Asterisk 19 中被弃用，并在 Asterisk 21 中被移除。与 MeetMe 不同，ConfBridge **不**需要 DAHDI 或硬件定时源：它依赖于 Asterisk 内置的定时接口（Linux 上的 `res_timing_timerfd`，或 `res_timing_pthread`），因此不需要 `dahdi_dummy` 模块。如果你是从使用 `MeetMe()` 和 `meetme.conf` 的旧系统迁移而来，请按照下文所述将其替换为 `ConfBridge()` 和 `confbridge.conf`。

### ConfBridge

要启动会议室，语法如下所示。

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

要获取该命令的完整描述，你可以使用 core show application confbridge。

![`core show application confbridge` 的输出，显示概要、语法以及 bridge_profile、user_profile 和 menu 参数](../images/13-pbx-features-fig06.png)

> **[第二版注]** 此处如果有一个 ConfBridge 图表会有所帮助：展示多个 SIP endpoints 通过 `ConfBridge()` 加入同一个命名会议（例如 `101`），其中一名参与者被标记为管理员，并标注混合/定时由 `res_confbridge` + 内置 `res_timing_*` 定时器处理（无 DAHDI）。

如上所示，有三个重要的参数，每个参数映射到 `confbridge.conf` 中的一个部分类型。**bridge_profile**（一个 `type=bridge` 部分）：在这里你可以选择最大参与者人数（`max_members`）、录音（`record_conference`）、`video_mode`以及许多其他桥接范围的参数。

在这里复制整个示例文件没有意义，所以让我给出一个关于如何在 confbridge.conf 文件中配置 bridge_profile 的简单示例。

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile**（一个 `type=user` 部分）：在这里你定义特定于用户的选项，例如用户是否为管理员（`admin=yes`）、他们是否静音进入（`startmuted=yes`）、保持音乐以及许多其他按用户设置的选项。示例：

```
[admin_user]
type=user
admin=yes
```

**menu**（一个 `type=menu` 部分）：在这里你定义会议的键盘 (DTMF) 映射——例如哪个键切换静音、调节音量或离开会议。查看 `confbridge.conf.sample` 文件以了解所有可用操作。示例：

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

会议桥选项可以使用 CONFBRIDGE() 函数在 dialplan 中动态传递。请参阅以下示例：

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge 管理命令及从 MeetMe 迁移

如果你来自 MeetMe，你之前通过 `MeetMeAdmin()` 和 `a` (admin) 选项使用的管理功能，现在通过 **admin user profile** (`admin=yes`) 加上 **menu** 操作来表达。加入时带有 admin profile 和包含管理操作菜单的管理员，可以从键盘实时锁定房间、踢出用户和静音参与者。`confbridge.conf` 中的相关菜单操作包括：

- `admin_kick_last` -- 踢出最后加入的用户
- `admin_toggle_mute_participants` -- 静音/取消静音所有非管理员参与者
- `toggle_mute` -- 静音/取消静音你自己
- `participant_count` -- 播报参与者人数
- `leave_conference` -- 离开桥接并继续执行 dialplan

这些取代了 MeetMe 的 `MeetMe()` 选项标志（`a`、`A`、`m`、`M`、`l`、`x`……）和 `MeetMeAdmin()` 命令（`k`、`K`、`L`、`M`、`N`……）。Asterisk 22 中没有 `meetme.conf`；所有会议配置都位于 `confbridge.conf` 中，更改通过 `module reload res_confbridge.so` 应用。

### ConfBridge 示例

要在 extension 500 处创建可访问的会议室，请在 `extensions.conf` 中设置：

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

第一个拨打 500 的呼叫者创建会议 `101`；后续呼叫者加入该会议。此处引用的配置文件和菜单（`default_bridge`、`default_user`、`sample_user_menu`）在 `confbridge.conf` 中定义。要要求 PIN 码，请在 user profile 中设置 `pin=`；要使参与者成为会议管理员，请为其提供带有 `admin=yes` 的 user profile。

## 呼叫录音

在 Asterisk 中录制呼叫有多种方法。你可以使用 `MixMonitor()` 应用程序轻松录制呼叫。（较旧的 `Monitor` 应用程序会录制两个单独的文件，现已被移除；请改用 `MixMonitor`。）

### 使用 MixMonitor 应用程序

`MixMonitor` 应用程序将当前通道中的音频录制到指定文件。如果文件名是绝对路径，它将使用该路径。否则，它会在 asterisk.conf 中配置的监控目录中创建文件。

![MixMonitor() 应用程序：将通道的音频录制并混合到一个文件中，具有追加、仅桥接和音量调节选项](../images/13-pbx-features-fig09.png)

### MixMonitor()

录制呼叫并在录制过程中混合音频。语法：`MixMonitor(filename.extension[,options[,command]])`。将当前通道上的音频录制到指定文件。有效选项：

- a - 追加到文件而不是覆盖它。
- b - 仅在通道被桥接时保存音频到文件。
- 注意：不包括会议。
- v(<x>) - 将可听音量调整 <x> 倍（范围从 -4 到 4）
- V(<x>) - 将说话音量调整 <x> 倍（范围从 -4 到 4）
- W(<x>) - 将可听音量和说话音量同时调整 <x> 倍（范围从 -4 到 4）
- <command> 将在录制结束时执行。任何匹配 ^{X} 的字符串都将被取消转义为 ${X}，并且所有变量都将在那时进行评估。变量 MIXMONITOR_FILENAME 将包含用于录制的文件名。

一个有趣的资源是一键录音功能 `automixmon`，它允许一方在通话期间拨打 DTMF 码（默认 `*3`）以立即开始（并切换关闭）录音。它基于 MixMonitor 构建，因此它写入单个混合文件。示例：

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

`X` 和 `x` 选项分别为呼叫者和被叫者启用一键 MixMonitor 功能。因为 MixMonitor 录制单个混合文件，所以不需要事后合并单独的 IN/OUT 文件（旧的 `automon`/`Monitor` 方法，即为 `soxmix` 产生两个文件，已与 `Monitor` 应用程序一起被移除）。

如果你不想在 Dial() 应用程序之前使用 Set()，你可以在 globals 部分设置：

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### 保持音乐

保持音乐 (MOH) 在 1.0、1.2 和 1.4 版本之间发生了多次变化。在最新版本中，MOH 默认为“FILE-BASED”。换句话说，Asterisk 将提供 g729、alaw、ulaw 和 gsm 等格式的 MOH 文件。因此，在将音乐发送到通道之前，无需对其进行转码。这节省了处理器时间，对于那些在生产系统上工作的人来说，这是一个受欢迎的修改。在旧版本中，MOH 通常由 MP3 提供（仍然可以那样配置）。使用 MP3 提供 MOH 会迫使 Asterisk 进行转码，在此过程中消耗宝贵的 CPU 功率。新的配置文件如下所示。请注意，默认类现在使用原生文件格式 mode=files。所有其他模式都被注释掉了。每个部分都是一个类。此时唯一未注释的类是 default。如果你想为不同的文件设置不同的类，你需要创建新的部分（类）。

![musiconhold.conf 示例配置，列出了有效的 MOH 模式（quietmp3, mp3, custom, files, …）](../images/13-pbx-features-fig10.png)

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

现在，要使用保持音乐，请在通道配置文件（chan_dahdi.conf, pjsip.conf, iax.conf 等）中设置 MOH 类。对于 PJSIP endpoints，在 `pjsip.conf` 的 endpoint 部分设置 `moh_suggest`（旧版 `musicclass` 选项名称适用于 chan_dahdi 和其他通道驱动程序，不适用于 PJSIP）。安装的 freeplay 音乐现在为 wav 格式。在安装时，你可以选择（使用 make menuselect）可用的 MOH 文件格式。如果你想添加新的 MOH 文件，你必须以所需的格式提供它们。例如：

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

在 dialplan 中，你可以使用 `StartMusicOnHold` 在通道上启动保持音乐（并使用 `StopMusicOnHold` 停止它）：

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

要播放保持音乐固定时间作为快速测试，请使用带有持续时间（以秒为单位）的 `MusicOnHold` 应用程序：

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## 应用程序映射 (Application Maps)

应用程序映射允许你通过使用 features.conf 文件的 `[applicationmap]` 部分来添加新功能。假设你需要向呼叫中心标识你正在接听的客户类型。你可以为每种客户类型创建一个应用程序映射，它可以统计每种类型的已接听客户数量。

## 测验

1. 关于呼叫驻留，哪些陈述是正确的？
   - A. 默认情况下，extension 800 用于呼叫驻留。
   - B. 当你不在办公桌旁并接到电话时，你可以将其驻留；系统会播报驻留槽位，你可以从任何电话拨打该槽位以取回呼叫。
   - C. 默认情况下，extension 700 驻留呼叫，呼叫被驻留在 701–720 槽位中。
   - D. 你拨打 700 以取回驻留的呼叫。
2. 要使用呼叫代答功能，所有 extensions 必须在同一个 ___ 中。对于 DAHDI 通道，这是在 ___ 文件中配置的。
3. 转移呼叫时，你可以在 ___ 转移（不先咨询目标）和 ___ 转移（在完成转移前与目标通话）之间进行选择。
4. 要进行咨询转移，你使用 ___ 序列；对于盲转，你使用 ___。
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. 要在 Asterisk 22 中托管电话会议，你使用 ___ 应用程序。
6. 在 ConfBridge 中，通过在用户的 user profile (`confbridge.conf`) 中设置 ___，可以授予参与者管理员权限（踢人、静音他人、锁定房间）：
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. 保持音乐的最佳格式是 MP3，因为它在 Asterisk 服务器上使用的处理能力非常小。
   - A. 正确
   - B. 错误
8. 要从特定的呼叫组代答呼叫，你必须在匹配的 ___ 组中。
9. 你可以使用 MixMonitor() 应用程序或一键录音 (`automixmon`) 功能录制呼叫。默认情况下，`automixmon` 使用 ___ DTMF 序列。
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. 在 ConfBridge 中，哪个 `confbridge.conf` user-profile 选项使参与者静音加入（他们可以听到会议但无法被听到，直到取消静音）？
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**答案：** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
