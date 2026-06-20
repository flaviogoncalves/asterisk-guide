# Using PBX features

In SIP systems, most of the phone features are implemented in the endpoint. A variety of SIP phones and manufacturers exist, and the interoperability is not guaranteed. The Asterisk development team has done an amazing job of implementing most of the features in the PBX itself, making Asterisk almost endpoint independent. However, sometimes you will find the same function being done by both the phone and Asterisk itself. The integration of the phone and the PBX is the next frontier on usability and where proprietary systems are focusing right now. In this chapter, you will learn how to use most of these features.

## 目标

在本章结束时，您将能够理解并使用：

- Call Parking
- Call Pickup
- Call Transfer
- Call Conference (ConfBridge)
- Call Recording
- Music on hold

## 功能实现位置

首先，必须了解 PBX 功能何时被执行，以及何时由电话本身完成工作。例如，您可以在电话上使用 TRANSFER 按钮或拨打 # 来转接通话（无条件转接由 PBX 本身执行）。

## Asterisk 实现的功能

- 保持音乐
- 呼叫停车
- 呼叫抢答
- 通话录音
- ConfBridge 会议室
- 呼叫转接（盲转和咨询转接）

## 通常在拨号计划中实现的功能

- 忙时呼叫转移
- 立即呼叫转移
- 未接听时呼叫转移
- 呼叫过滤（黑名单）
- 请勿打扰
- 重新拨号

## Features usually implemented by the phone

These features are implemented by the phone’s firmware:

![PBX 功能通常实现的位置：在 Asterisk 本身、在 dialplan 中或在电话上】(../images/13-pbx-features-fig01.png)

- 保持通话
- 盲转接
- 咨询转接
- 三方会议
- 消息等待指示器

## The features configuration file

本章中介绍的一些功能在 **features.conf** 配置文件中进行配置。通过修改该文件可以改变某些功能的行为。下面给出了相关摘录。在本章的后续章节中，我们将逐一描述每个功能。摘自示例文件（Asterisk 22）

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

自 Asterisk 12 起，呼叫泊车已从 `features.conf` 移至其独立模块 `res_parking`，配置位于 `res_parking.conf`。下面的 parking-lot 块（`parkext`、`parkpos`、`context`、`parkingtime`等）位于 `res_parking.conf`。`[featuremap]` 部分（DTMF 功能代码，包括 `parkcall`）仍保留在 `features.conf`。

parking-lot 选项位于 `res_parking.conf`。即使配置文件中未出现，名为 `default` 的泊车场也始终存在。下面的摘录取自 Asterisk 22 `res_parking.conf.sample`：

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

DTMF 功能代码（包括一步 `parkcall`）仍位于 `[featuremap]` 部分的 `features.conf`：

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the Dial() or Queue()  app call!
;parkcall => #72                ; Park call (one step parking)  -- Make sure to set the K and/or k option in the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X and/or x option in the Dial() or Queue() app call!
```

## Call Transfer

呼叫转接可以由电话、ATA 或 Asterisk 本身实现。请参阅您的电话手册以了解如何进行呼叫转接。如果您的电话不支持呼叫转接，您可以使用 Asterisk 来完成此任务。呼叫转接有两种不同的实现方式。

第一种方式是使用盲转功能：拨号 # 后跟要转接的号码。有时您会使用 IP 电话或 IP 软电话的转接功能。您可以通过编辑 features.conf 文件中的 blindxfer 参数来更改转接字符。

您可以通过在 features.conf 文件中去掉 ; 前缀来启用受援转接（assisted transfer）参数 atxfer。通话期间，按 *2。Asterisk 会说 “transfer” 并给您一个拨号音。来电者被送入保持音乐。您与目标方通话后挂断电话，系统会将来电者桥接到目标方。

![Call transfer: the steps for a blind transfer (press # during the call) and an attended transfer (press *2)](../images/13-pbx-features-fig03.png)

### Configuration task list

1. 对于 PJSIP 端点，确保选项 `direct_media` 设置为 `no`（以便媒体通过 Asterisk 传输并检测功能代码），或在 `Dial()` 应用中使用 `t`/`T` 选项

## 呼叫停放

此功能用于停放通话。例如，当您在房间外接听电话并希望将通话转回您的桌面时，可通过将通话停放在一个分机来实现。到达桌面后，只需拨打停放分机的号码即可恢复通话。

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

默认情况下，使用 700 分机来停放通话。在通话进行中，按 # 将通话转移到 700 分机。此时 Asterisk 会播报您的停放分机号，例如 701 或 702。挂断电话后，来电者将被置于保持状态。到您的桌面电话上拨打播报的停放分机号即可恢复通话。如果来电者停放时间过长，超时功能将触发，原先拨打的分机将再次响铃。

### 配置任务列表

按照以下步骤启用呼叫停放。步骤 1：使停放区在您的 dialplan 中可达（必需）。默认停放区的 `context` 为 `parkedcalls`（在 `res_parking.conf` 中设置）。在 `extensions.conf` 中将该 context 包含在电话拨出的 context 中：

```
include => parkedcalls
```

步骤 2：通过拨打 #700 测试呼叫停放功能。注意：

- 停放分机不会出现在 dialplan show CLI 命令的输出中。
- 更改停放配置文件后需要重新加载停放模块： `module reload res_parking.so`。对于 features.conf 的更改， `module reload features.so`。
- 要停放通话，需要转移到 #700。请检查 `t` 和 `T` 选项在 `Dial()` 应用中的设置。

## 呼叫抢答

呼叫抢答允许您从同一呼叫组的同事那里接管通话。例如，您可以避免必须起床去接听正在您房间另一人手机上响铃的来电，而此人不在场。拨打 *8 即可在您的呼叫组内抢答通话。此号码可在 `features.conf` 文件中修改。

![Call pickup: members can only capture calls within their own group; the operator (pickupgroup=1,2,3) can pick up calls from every group](../images/13-pbx-features-fig05.png)

### 配置任务列表

按照以下步骤配置呼叫抢答功能。步骤 1：为您的分机配置呼叫组。这在通道配置文件（pjsip.conf、iax.conf、chan_dahdi.conf）中完成。对于 PJSIP 端点，在 `pjsip.conf` 的 endpoint 部分设置 `call_group` 和 `pickup_group`（pjsip.conf 使用 snake_case 选项名）。此任务为必需。

对于 PJSIP（pjsip.conf）：
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```

步骤 2：更改呼叫抢答功能号码（可选）。此设置位于 `features.conf` 的 `[general]` 部分，而不是 `pjsip.conf`：

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conference (call conference)

有多种方式在 Asterisk 上实现会议。第一种选项是直接使用电话的三方通话功能。通过在电话上使用此功能，服务器本身不需要任何支持。然而，当需要超过 3 人的会议时，应该运行会议室。Asterisk 的现代会议应用是 ConfBridge（`app_confbridge`）。

ConfBridge 支持高清语音会议和视频会议。视频会议有一些限制，例如不进行转码——所有参与者必须使用相同的 codec 和 profile。视频会议采用“跟随发言者”模式，显示最近发言者的画面。您可以轻松在 ConfBridge 中配置新的 DTMF 菜单。

ConfBridge 替代了旧的 MeetMe 应用，MeetMe 在 Asterisk 19 中已被弃用。MeetMe 仍然在 Asterisk 22 源码树中提供，但它依赖 DAHDI，默认情况下不会构建，因此在典型的 PJSIP 安装中根本不可用——ConfBridge 是受支持的会议应用。与 MeetMe 不同，ConfBridge **不** 需要 DAHDI 或硬件计时源：它依赖 Asterisk 内置的计时接口（`res_timing_timerfd` on Linux，或 `res_timing_pthread`），因此不需要 `dahdi_dummy` 模块。如果您正从使用 `MeetMe()` 和 `meetme.conf` 的旧系统迁移，请按照下文所述将其替换为 `ConfBridge()` 和 `confbridge.conf`。

### ConfBridge

要启动会议室，语法如下所示。

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

要获取该命令的完整描述，您可以使用 `core show application confbridge`。

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

如上所示，有三个重要参数，每个参数映射到 `confbridge.conf` 中的一个节类型。**bridge_profile**（一个 `type=bridge` 节）：在这里您可以选择最大参与者数量（`max_members`）、录音（`record_conference`）、`video_mode`以及许多其他全桥参数。

这里不适合在此处完整复制示例文件，所以让我给您一个简单示例，演示如何在 `confbridge.conf` 文件中配置 `bridge_profile`。

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (a `type=user` section): 在这里您定义针对每个用户的特定选项，例如用户是否是管理员（`admin=yes`），是否默认静音（`startmuted=yes`），保持音乐，以及许多其他针对用户的选项。示例：

```
[admin_user]
type=user
admin=yes
```

**menu** (a `type=menu` section): 在这里您定义会议的键盘（DTMF）映射——例如哪个键切换静音、调节音量或离开会议。检查 `confbridge.conf.sample` 文件以查看所有可用操作。示例：

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

#### Confbridge 功能

可以在 dialplan 中使用 CONFBRIDGE() 函数动态传递会议桥选项。请参见下面的示例：

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge 管理命令及从 MeetMe 的迁移

如果你之前使用 MeetMe，通过 `MeetMeAdmin()` 和 `a` (admin) 选项进行的管理功能，现在改为通过 **admin user profile**（`admin=yes`）加上 **menu** 动作来实现。使用管理员配置文件并包含管理员动作的菜单加入的管理员，可以通过键盘实时锁定房间、踢出用户以及静音参与者。 `confbridge.conf` 中相关的菜单动作如下：

- `admin_kick_last` -- 踢出最近加入的用户
- `admin_toggle_mute_participants` -- 静音/取消静音所有非管理员参与者
- `toggle_mute` -- 静音/取消静音自己
- `participant_count` -- 宣告参与者数量
- `leave_conference` -- 离开桥接并继续执行 dialplan

这些动作取代了 MeetMe `MeetMe()` 选项标志（`a`、`A`、`m`、`M`、`l`、`x`、…）以及 `MeetMeAdmin()` 命令（`k`、`K`、`L`、`M`、`N`、…）。在现代的 PJSIP 安装中，你根本不会加载 `app_meetme`；所有会议配置都存放在 `confbridge.conf` 中，修改通过 `module reload app_confbridge.so` 应用（ConfBridge 逻辑位于 `app_confbridge`；没有 `res_confbridge` 模块）。

### ConfBridge 示例

要在 `extensions.conf` 中创建一个可通过分机 500 访问的会议室：

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

第一个拨打 500 的来电者创建会议 `101`；后续来电者加入该会议。此处引用的配置文件和菜单（`default_bridge`、`default_user`、`sample_user_menu`）在 `confbridge.conf` 中定义。要要求 PIN，请在用户配置文件中设置 `pin=`；要将参与者设为会议管理员，请为其分配包含 `admin=yes` 的用户配置文件。

## Call Recording

有多种方式在 Asterisk 中录制通话。您可以使用 `MixMonitor()` 应用程序轻松录制通话。（较旧的 `Monitor` 应用程序会生成两个独立的文件，已被移除；请改用 `MixMonitor`）。

### Using the MixMonitor application

`MixMonitor` 应用程序将当前通道的音频记录到指定文件。如果文件名是绝对路径，则使用该路径；否则，它会在 asterisk.conf 中配置的 monitoring 目录下创建文件。

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

录制通话并在录制过程中混合音频。语法： `MixMonitor(filename.extension[,options[,command]])`。将当前通道的音频记录到指定文件。有效选项：

- a - 追加到文件而不是覆盖。
- b - 仅在通道已桥接时保存音频到文件。
- Note: does not include conferences.
- v(<x>) - 将可听音量按因子 <x> 调整（范围 -4 到 4）
- V(<x>) - 将说话音量按因子 <x> 调整（范围 -4 到 4）
- W(<x>) - 将可听音量和说话音量均按因子 <x> 调整（范围 -4 到 4）
- <command> 将在录音结束时执行。任何匹配 ^{X} 的字符串将被转义为 ${X}，所有变量将在那时求值。变量 MIXMONITOR_FILENAME 将包含用于录音的文件名。

一个有趣的资源是一键录音功能 `automixmon`，它允许通话双方在通话期间拨打 DTMF 代码（`features.conf` 示例建议使用 `*3`；没有内置默认值，需要自行设置）以立即开始（并可再次关闭）录音。它基于 MixMonitor 实现，因此会写入单个混合文件。示例：

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

The `X` and `x` options enable the one-touch MixMonitor feature for the caller and callee respectively. Because MixMonitor records a single mixed file, there is no need to combine separate IN/OUT files afterward (the old `automon`/`Monitor` approach, which produced two files for `soxmix`, was removed along with the `Monitor` application).

If you don’t want to use Set() before the Dial() application, you can set this in the globals section:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Music on hold

Music on hold (MOH) 已在 1.0、1.2 和 1.4 版本中多次更改。最新版本中，MOH 默认使用 “FILE-BASED”。换句话说，Asterisk 将提供 g729、alaw、ulaw 和 gsm 等格式的 MOH 文件。因此，无需在发送到通道之前对音乐进行转码。这可以节省处理器时间，对使用生产系统的用户来说是一个受欢迎的改进。

在较早的版本中，MOH 通常由 MP3 提供（仍然可以这样配置）。使用 MP3 提供 MOH 会迫使 Asterisk 进行转码，在此过程中消耗宝贵的 CPU 资源。

下面显示了新的配置文件。请注意，默认类现在使用本地文件格式 mode=files。所有其他模式均已被注释掉。每个章节都是一个类。目前唯一未被注释的类是 default。如果希望为不同的文件使用不同的类，需要创建新的章节（类）。

![musiconhold.conf 示例配置，列出有效的 MOH 模式（quietmp3、mp3、custom、files，…）](../images/13-pbx-features-fig10.png)

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

现在，要使用保持音乐，需要在通道配置文件（chan_dahdi.conf、pjsip.conf、iax.conf 等）中设置 MOH 类。对于 PJSIP 端点，在 `pjsip.conf` 的 endpoint 部分设置 `moh_suggest`（旧的 `musicclass` 选项名称适用于 chan_dahdi 和其他通道驱动程序，而不适用于 PJSIP）。现在安装的 freeplay 曲目为 wav 格式。安装时，您可以通过 (using make menuselect) 选择可用的 MOH 文件格式。如果想添加新的 MOH 文件，必须提供所需格式的文件。例如：

在 `/etc/asterisk/chan_dahdi.conf` 中，添加 `musiconhold` 行：

```
[channels]
musiconhold=default
```

Then edit `/etc/asterisk/musiconhold.conf` to define that class:

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

在 dial plan 中，您可以使用 `StartMusicOnHold` 在通道上启动保持音乐（并使用 `StopMusicOnHold` 停止它）：

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

要在固定时间内播放保持音乐以进行快速测试，请使用 `MusicOnHold` 应用并指定持续时间（秒）：

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## 应用映射

Application maps allow you to add new features by using the `[applicationmap]` section of the features.conf file. Suppose you need to identify the type of customer you are answering to a call center. You could create an application map for each customer type, which could count the number of answered customers per type.

## Summary

在本章中，你了解了 Asterisk 的 PBX 功能所在的位置——有些在核心，有些在 dialplan 中，还有一些在电话本身——以及 DTMF 功能代码如何映射在 `[featuremap]` 部分的 `features.conf` 中。你配置了 **call transfer**（盲转和有条件转接）和 **call parking**（`res_parking.conf`, 使用 `k`/`K` Dial 选项以及 `parkedcalls` 相关设置），**call pickup** 按组进行，以及使用 **ConfBridge**（`confbridge.conf` bridge/user/menu 配置文件）的 **conferencing**，它取代了旧的 MeetMe。你设置了 **one-touch recording** 与 MixMonitor（`automixmon`, `X`/`x` Dial 选项以及 `DYNAMIC_FEATURES`），配置了 **music on hold**，并了解了 **application maps** 如何让你将自定义的 dialplan 逻辑绑定到 DTMF 序列。通过这些构建块，你可以提供用户在企业 PBX 中期望的日常功能。

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___ . For DAHDI channels this is configured in the ___ file.
3. When transferring a call you can choose between a ___ transfer, where the destination is not consulted first, and an ___ transfer, where you talk to the destination before completing it.
4. To make an attended (consultative) transfer you use the ___ sequence; for a blind transfer you use ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. To host conference calls in Asterisk 22, you use the ___ application.
6. In ConfBridge, a participant is granted administrator privileges (kick, mute others, lock the room) by setting ___ in their user profile (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. The best format for music on hold is MP3, because it uses very little processing power on the Asterisk server.
   - A. True
   - B. False
8. To pick up a call from a specific call group, you must be in the matching ___ group.
9. You can record a call with the MixMonitor() application or the one-touch recording (`automixmon`) feature. In the `features.conf` sample, `automixmon` is mapped to the ___ DTMF sequence.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, which `confbridge.conf` user-profile option makes a participant join muted (they can hear the conference but cannot be heard until unmuted)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
