# PBX機能の利用

SIPシステムでは、電話機能のほとんどがendpointに実装されています。多種多様なSIP電話機やメーカーが存在し、相互運用性は保証されていません。Asterisk開発チームは、PBX自体にほとんどの機能を実装するという素晴らしい仕事をしており、Asteriskをほぼendpointに依存しないものにしています。しかし、電話機とAsteriskの両方で同じ機能が実行されていることに気づく場合もあります。電話機とPBXの統合は、ユーザビリティにおける次のフロンティアであり、現在プロプライエタリなシステムが注力している分野です。この章では、これらの機能のほとんどを使用する方法を学びます。

## Objectives

By the end of this chapter, you will be able to understand and use:

- Call Parking
- Call Pickup
- Call Transfer
- Call Conference (ConfBridge)
- Call Recording
- Music on hold

## 機能が実装されている場所

まず何よりも、PBXの機能が実行されるタイミングと、電話機側ですべての処理が行われるタイミングの違いを理解することが重要です。例えば、電話機のTRANSFERボタンを使用して通話を転送する場合と、#をダイヤルして（PBX自身によって実行される無条件転送）転送する場合とでは、処理の主体が異なります。

## Asteriskによって実装される機能

これらの機能は、AsteriskのコードによってPBXに実装されています。

- Music on hold
- Call parking
- Call pickup
- Call recording
- ConfBridge conference room
- Call transfer (blind and consultative)

## dialplanで一般的に実装される機能

これらの機能は、Asteriskのdialplan（extensions.conf）でプログラムする必要があります。

- 話中時転送（Call forward on busy）
- 無条件転送（Call forward immediate）
- 不応答時転送（Call forward on unanswered）
- 着信フィルタリング（ブラックリスト）
- おやすみモード（Do not disturb）
- リダイヤル（Redial）

## 電話機側で実装される機能

これらの機能は、電話機のファームウェアによって実装されます。

![PBX機能が通常実装される場所：Asterisk自体、dialplan、または電話機](../images/13-pbx-features-fig01.png)

- 通話保留 (Call on hold)
- ブラインド転送 (Blind transfer)
- 相談転送 (Consultative transfer)
- 三者間通話 (Three-way conference)
- メッセージ待機表示 (Message waiting indicator)

## The features configuration file

本章で紹介する機能の一部は、features.conf 設定ファイルで構成されます。このファイルを変更することで、いくつかの機能の動作を変更することが可能です。関連する抜粋を以下に記載しました。本章の以降のセクションで、各機能について説明します。サンプルファイルからの抜粋（Asterisk 22）

![features.conf の `[featuremap]` セクション。デフォルトの DTMF 機能コードが含まれています](../images/13-pbx-features-fig02.png)

Asterisk 12 以降、コールパーキングは `features.conf` から独自のモジュールである `res_parking` へと移行され、設定は `res_parking.conf` に行われるようになりました。以下の parking-lot ブロック（`parkext`、`parkpos`、`context`、`parkingtime`など）は `res_parking.conf` に記述されます。`[featuremap]` セクション（`parkcall` を含む DTMF 機能コード）は引き続き `features.conf` に存在します。

parking-lot のオプションは `res_parking.conf` に記述されます。`default` という名前のパーキングロットは、設定ファイル内に存在しない場合でも常に存在します。以下の抜粋は Asterisk 22 の `res_parking.conf.sample` からのものです：

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

（ワンステップ `parkcall` を含む）DTMF 機能コードは、引き続き `features.conf` の `[featuremap]` セクションに存在します：

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

## Call Transfer

Call transferは、電話機、ATA、またはAsterisk自体によって実装できます。通話の転送方法については、お使いの電話機の説明書を参照してください。電話機がCall transferをサポートしていない場合は、Asteriskを使用してこのタスクを実行できます。Call transferには2つの異なる実装方法があります。1つ目はblind transfer機能を使用する方法で、#の後に転送先の番号をダイヤルします。IP電話やIP softphoneの転送機能を使用する場合もあります。転送に使用する文字は、features.confファイルのblindxferパラメータを編集することで変更できます。Asteriskでassisted transferを有効にするには、features.confファイルのatxferパラメータの前にある;を削除します。通話中に*2を押すと、Asteriskが「transfer」とアナウンスし、ダイヤルトーンが聞こえます。発信者はmusic on holdに送られます。転送先の相手と話した後に電話を切ると、システムは発信者と転送先をブリッジします。

![Call transfer: blind transfer（通話中に#を押す）とattended transfer（*2を押す）の手順](../images/13-pbx-features-fig03.png)

### Configuration task list

1. PJSIP endpointの場合、オプション`direct_media`が`no`に設定されていることを確認してください（これによりメディアがAsteriskを経由し、feature codeが検出されるようになります）。または、`Dial()`アプリケーションで`t`/`T`オプションを使用してください。

## Call parking

この機能は、通話をパーク（保留）するために使用されます。例えば、自席以外の場所で電話を受けた際に、その通話を自分のデスクへ転送したい場合などに役立ちます。通話を特定のextensionにパークすることでこれを実現できます。デスクに戻ったら、そのパーク用extensionの番号をダイヤルするだけで通話を再開できます。

![Call parking: 700をダイヤルして最初の空きスロット（701–720）に通話をパークします。Asteriskがスロット番号をアナウンスするので、どの電話機からでもその番号をダイヤルして通話を復帰できます](../images/13-pbx-features-fig04.png)

デフォルトでは、700というextensionが通話のパークに使用されます。通話中に # を押すと、その通話が700のextensionへ転送されます。するとAsteriskが701や702といったパーク用extensionをアナウンスします。電話を切ると、発信者は保留状態になります。デスクの電話機へ移動し、アナウンスされたパーク用extensionをダイヤルすれば通話を再開できます。発信者が長時間パークされたままの場合、タイムアウト機能が作動し、最初にダイヤルされたextensionが再び呼び出されます。

### Configuration task list

Call parkingを有効にするには、以下の手順に従ってください。ステップ1：dialplanからparking lotに到達できるようにします（必須）。デフォルトのparking lotの`context`は`parkedcalls`です（`res_parking.conf`で設定）。このcontextを、電話機がダイヤルを行うcontextに`extensions.conf`で含めてください：

```
include => parkedcalls
```

ステップ2：#700をダイヤルしてCall parking機能をテストします。注意点：

- パーク用extensionは、dialplan show CLIコマンドには表示されません。
- parkingの設定ファイルを変更した後は、parkingモジュールをリロードする必要があります：`module reload res_parking.so`。features.confの変更については、`module reload features.so`を実行してください。
- 通話をパークするには、#700へ転送する必要があります。`Dial()`アプリケーション内の`t`および`T`オプションを確認してください。

## Call pickup

Call pickup を使用すると、同じ call group 内の同僚への着信を自分の電話で受けることができます。例えば、同じ部屋にいる別の人の電話が鳴っているものの、本人が不在である場合に、わざわざ席を立たなくても電話に出られるため便利です。*8 をダイヤルすることで、自分の call group 内の着信をピックアップできます。この番号は以下で変更可能です。

```
features.conf file.
```

![Call pickup: メンバーは自分のグループ内の着信のみピックアップ可能。オペレーター (pickupgroup=1,2,3) はすべてのグループの着信をピックアップ可能](../images/13-pbx-features-fig05.png)

### Configuration task list

Call pickup 機能を設定するには、以下の手順に従ってください。ステップ 1: 各 extension に call group を設定します。これはチャネル設定ファイル (pjsip.conf, iax.conf, chan_dahdi.conf) で行います。PJSIP endpoint の場合、endpoint セクションで `call_group` および `pickup_group` を設定します (pjsip.conf では snake_case のオプション名を使用します)。このタスクは必須です。

PJSIP (pjsip.conf) の場合:
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


ステップ 2: Call-pickup の機能番号を変更します (オプション)。これは `pjsip.conf` ではなく、 `features.conf` の `[general]` セクションで設定します。

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conference (会議)

Asteriskで会議を実装する方法はいくつかあります。最初の選択肢は、電話機の3者間通話機能を使用することです。この機能を使用する場合、サーバー側でのサポートは一切不要です。しかし、4人以上の会議を行いたい場合は、会議室（カンファレンスルーム）を運用する必要があります。Asteriskの現代的な会議用アプリケーションが ConfBridge (`app_confbridge`) です。

ConfBridgeはHD音声会議およびビデオ会議をサポートしています。ビデオ会議にはトランスコーディングができないという制限があり、すべての参加者が同じ codec とプロファイルを使用する必要があります。ビデオ会議では「発言者追従（follow-the-talker）」モードが使用され、最後に発言した人の映像が表示されます。ConfBridgeでは、新しい DTMF メニューを簡単に設定できます。

ConfBridgeは古い MeetMe アプリケーションを置き換えるもので、MeetMe は Asterisk 19 で非推奨となり、Asterisk 21 で削除されました。MeetMe とは異なり、ConfBridge は DAHDI やハードウェアのタイミングソースを**必要としません**。Asterisk 内蔵のタイミングインターフェース（Linux上の`res_timing_timerfd`、または`res_timing_pthread`）に依存するため、いかなる`dahdi_dummy`モジュールも不要です。もし`MeetMe()`や`meetme.conf`を使用していた古いシステムから移行する場合は、以下で説明するようにそれらを`ConfBridge()`や`confbridge.conf`に置き換えてください。

### ConfBridge

会議室を開始するための構文は以下の通りです。

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

コマンドの詳細な説明については、core show application confbridge を使用してください。

![`core show application confbridge`の出力。シノプシス、構文、および bridge_profile、user_profile、menu 引数が表示されている](../images/13-pbx-features-fig06.png)

> **[第2版注記]** ここに ConfBridge の図があると役立つでしょう。複数の SIP endpoint が単一の会議名（例: `101`）に`ConfBridge()`を通じて参加し、1人の参加者が管理者としてフラグ立てされ、ミキシング/タイミングが`res_confbridge`と内蔵の`res_timing_*`タイマー（DAHDIなし）によって処理される様子を示す図です。

上記のように、3つの重要な引数があり、それぞれが`confbridge.conf`内のセクションタイプに対応しています。**bridge_profile**（`type=bridge`セクション）では、参加者の最大数（`max_members`）、録音（`record_conference`）、`video_mode`、その他多くのブリッジ全体に関わるパラメータを選択します。

例ファイル全体をここに転載しても意味がないため、confbridge.conf ファイル内で bridge_profile を設定する簡単な例を紹介します。

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile**（`type=user`セクション）では、ユーザーが管理者かどうか（`admin=yes`）、開始時にミュート状態にするか（`startmuted=yes`）、保留音の設定など、ユーザーごとのオプションを定義します。例:

```
[admin_user]
type=user
admin=yes
```

**menu**（`type=menu`セクション）では、会議用のキーパッド（DTMF）マッピングを定義します。例えば、どのキーでミュートの切り替え、音量調整、会議からの退出を行うかなどを設定します。利用可能なすべてのアクションについては`confbridge.conf.sample`ファイルを確認してください。例:

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

#### Confbridge 関数

会議ブリッジのオプションは、dialplan 内で CONFBRIDGE() 関数を使用して動的に渡すことができます。以下の例を参照してください。

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge 管理者コマンドと MeetMe からの移行

MeetMe から移行する場合、以前`MeetMeAdmin()`や`a`（管理者）オプションを通じて使用していた管理者機能は、現在では **admin user profile**（`admin=yes`）と **menu** アクションを通じて表現されます。管理者プロファイルと管理者アクションを含むメニューで参加した管理者は、キーパッドから直接、会議室のロック、ユーザーの強制退出、参加者のミュートを行うことができます。`confbridge.conf`における関連メニューアクションは以下の通りです。

- `admin_kick_last` -- 最後に入室したユーザーを強制退出させる
- `admin_toggle_mute_participants` -- 管理者以外の全参加者をミュート/ミュート解除する
- `toggle_mute` -- 自分自身をミュート/ミュート解除する
- `participant_count` -- 参加者数をアナウンスする
- `leave_conference` -- ブリッジから退出して dialplan の続きを実行する

これらは MeetMe の`MeetMe()`オプションフラグ（`a`、`A`、`m`、`M`、`l`、`x`…）や`MeetMeAdmin()`コマンド（`k`、`K`、`L`、`M`、`N`…）を置き換えるものです。Asterisk 22 には`meetme.conf`は存在しません。すべての会議設定は`confbridge.conf`に集約されており、変更は`module reload res_confbridge.so`で適用されます。

### ConfBridge の例

extension 500 で到達可能な会議室を作成するには、`extensions.conf`で以下のように設定します。

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

500 にダイヤルした最初の発信者が会議`101`を作成し、後続の発信者がそこに参加します。ここで参照されているプロファイルとメニュー（`default_bridge`、`default_user`、`sample_user_menu`）は`confbridge.conf`で定義されています。PIN を要求するには user profile で`pin=`を設定し、参加者を会議管理者に設定するには`admin=yes`を含む user profile を割り当ててください。

## 通話録音

Asteriskで通話録音を行う方法はいくつかあります。`MixMonitor()`アプリケーションを使用すれば、簡単に通話を録音できます。（2つの別々のファイルを録音していた古い`Monitor`アプリケーションは削除されました。代わりに`MixMonitor`を使用してください。）

### MixMonitorアプリケーションの使用

`MixMonitor`アプリケーションは、現在のチャネルの音声を指定されたファイルに録音します。ファイル名が絶対パスである場合はそのパスが使用されます。それ以外の場合は、asterisk.confで設定されたモニタリングディレクトリ内にファイルが作成されます。

![MixMonitor()アプリケーション：チャネルの音声を録音してミックスし、ファイルに保存します。追記、ブリッジ時のみ、音量調整のオプションがあります](../images/13-pbx-features-fig09.png)

### MixMonitor()

通話を録音し、録音中に音声をミックスします。構文：`MixMonitor(filename.extension[,options[,command]])`。現在のチャネルの音声を指定されたファイルに録音します。有効なオプションは以下の通りです。

- a - ファイルを上書きせず、追記します。
- b - チャネルがブリッジされている間のみ、音声をファイルに保存します。
- 注：カンファレンスは含まれません。
- v(<x>) - 可聴音量を <x> 倍に調整します（-4から4の範囲）。
- V(<x>) - 通話音量を <x> 倍に調整します（-4から4の範囲）。
- W(<x>) - 可聴音量と通話音量の両方を <x> 倍に調整します（-4から4の範囲）。
- <command> は録音が終了したときに実行されます。^{X} に一致する文字列は ${X} にエスケープ解除され、その時点で全ての変数が評価されます。変数 MIXMONITOR_FILENAME には、録音に使用されたファイル名が格納されます。

興味深いリソースとして、ワンタッチ録音機能`automixmon`があります。これは、通話中にDTMFコード（デフォルトは`*3`）をダイヤルすることで、即座に録音を開始（および停止）できる機能です。これはMixMonitorに基づいて構築されているため、単一のミックスされたファイルが書き込まれます。例：

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

`X`および`x`オプションは、それぞれ発信者と着信者に対してワンタッチMixMonitor機能を有効にします。MixMonitorは単一のミックスされたファイルを録音するため、後で個別のIN/OUTファイルを結合する必要はありません（`soxmix`のために2つのファイルを生成していた古い`automon`/`Monitor`方式は、`Monitor`アプリケーションと共に削除されました）。

Dial()アプリケーションの前にSet()を使用したくない場合は、globalsセクションで以下のように設定できます。

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### 保留音 (Music on hold)

保留音（MOH）は、バージョン1.0、1.2、1.4の間で何度か変更されました。最新バージョンでは、MOHはデフォルトで「FILE-BASED」となっています。つまり、Asteriskはg729、alaw、ulaw、gsmといった形式でMOHファイルを提供します。そのため、チャネルに送信する前に音楽をトランスコードする必要はありません。これによりプロセッサの時間を節約でき、本番システムを運用するユーザーにとって歓迎すべき変更です。古いバージョンでは、MOHは通常MP3で提供されていました（現在もそのように設定可能です）。MP3を使用してMOHを提供する場合、Asteriskはトランスコードを強制され、その過程で貴重なCPUパワーを消費します。新しい設定ファイルを以下に示します。デフォルトのクラスがネイティブファイルフォーマットの mode=files を使用していることに注意してください。他の全てのモードはコメントアウトされています。各セクションはクラスです。現時点でコメントアウトされていないクラスは default のみです。異なるファイルに対して異なるクラスを持たせたい場合は、新しいセクション（クラス）を作成する必要があります。

![musiconhold.confのサンプル設定。有効なMOHモード（quietmp3, mp3, custom, files, …）がリストされています](../images/13-pbx-features-fig10.png)

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

### MOH設定タスク

保留音を使用するには、チャネル設定ファイル（chan_dahdi.conf、pjsip.conf、iax.confなど）でMOHクラスを設定します。PJSIP endpointの場合は、`pjsip.conf`のendpointセクションで`moh_suggest`を設定します（レガシーな`musicclass`オプション名はchan_dahdiやその他のチャネルドライバに適用されるものであり、PJSIPには適用されません）。インストールされるフリーの楽曲は現在wav形式です。インストール時に（make menuselectを使用して）利用可能なMOHファイル形式を選択できます。新しいMOHファイルを追加したい場合は、必要な形式で提供する必要があります。例：

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

ダイヤルプランでは、`StartMusicOnHold`でチャネルの保留音を開始し、`StopMusicOnHold`で停止できます。

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

簡単なテストとして一定時間保留音を再生するには、`MusicOnHold`アプリケーションを期間（秒単位）と共に使用します。

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Application Maps

Application maps を使用すると、features.conf ファイルの `[applicationmap]` セクションを使用して新しい機能を追加できます。コールセンターで対応している顧客のタイプを識別する必要があると仮定します。顧客タイプごとに application map を作成し、タイプごとの応答済み顧客数をカウントできるようにすることが可能です。

## Quiz

1. コールパーキングについて正しい記述はどれですか？
   - A. デフォルトでは、extension 800 がコールパーキングに使用されます。
   - B. デスクから離れているときに電話を受けた場合、その通話をパークできます。システムがパーキングスロットをアナウンスし、どの電話機からでもそのスロット番号をダイヤルすることで通話を再開できます。
   - C. デフォルトでは、extension 700 が通話をパークし、通話は 701–720 のスロットにパークされます。
   - D. パークされた通話を再開するには 700 をダイヤルします。
2. コールピックアップ機能を使用するには、すべての extension が同じ ___ に属している必要があります。DAHDI チャネルの場合、これは ___ ファイルで設定されます。
3. 通話を転送する際、転送先に事前に確認を行わない ___ 転送と、転送先に話してから完了させる ___ 転送を選択できます。
4. アテンデッド（相談）転送を行うには ___ シーケンスを使用し、ブラインド転送には ___ を使用します。
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Asterisk 22 で会議通話をホストするには、___ アプリケーションを使用します。
6. ConfBridge において、参加者に管理者権限（キック、他者のミュート、ルームのロック）を付与するには、ユーザープロファイル（`confbridge.conf`）で以下を設定します：
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. 保留音（Music on Hold）に最適なフォーマットは MP3 です。なぜなら、Asterisk サーバーの処理能力をほとんど消費しないからです。
   - A. True
   - B. False
8. 特定のコールグループから通話をピックアップするには、一致する ___ グループに属している必要があります。
9. MixMonitor() アプリケーションまたはワンタッチ録音（`automixmon`）機能を使用して通話を録音できます。デフォルトでは、`automixmon`は ___ DTMF シーケンスを使用します。
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. ConfBridge において、参加者がミュート状態で参加する（会議を聞くことはできるが、ミュート解除されるまで話すことはできない）ようにする`confbridge.conf`ユーザープロファイルオプションはどれですか？
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
