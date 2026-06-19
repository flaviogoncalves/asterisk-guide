# PBX機能の使用

SIPシステムでは、電話機の機能のほとんどはエンドポイント（電話機側）で実装されています。多種多様なSIP電話機やメーカーが存在するため、相互運用性は保証されていません。Asterisk開発チームは、機能のほとんどをPBX自体に実装するという素晴らしい仕事をしており、Asteriskをほぼエンドポイントに依存しないものにしています。しかし、電話機とAsteriskの両方で同じ機能が実行されていることに気づく場合もあります。電話機とPBXの統合は、ユーザビリティにおける次のフロンティアであり、現在プロプライエタリなシステムが注力している分野です。この章では、これらの機能のほとんどを使用する方法を学びます。

## 目的

この章を読み終えると、以下の機能を理解し、使用できるようになります。

- 通話パーク（Call Parking）
- 通話ピックアップ（Call Pickup）
- 通話転送（Call Transfer）
- 通話会議（ConfBridge）
- 通話録音（Call Recording）
- 保留音（Music on hold）

## 機能が実装される場所

まず第一に、PBX機能がいつ実行されるのか、またいつ電話機側ですべての処理が行われるのかを理解することが重要です。例えば、電話機のTRANSFERボタンを使用して通話を転送することも、#をダイヤルして（PBX自体が実行する無条件転送）転送することもできます。

## Asteriskによって実装される機能

これらの機能は、AsteriskのコードによってPBXに実装されています。

- 保留音
- 通話パーク
- 通話ピックアップ
- 通話録音
- ConfBridge会議室
- 通話転送（ブラインド転送および相談転送）

## 通常ダイヤルプランによって実装される機能

これらの機能は、Asteriskのダイヤルプラン（extensions.conf）でプログラムする必要があります。

- 話中時転送
- 即時転送
- 無応答時転送
- 通話フィルタリング（ブラックリスト）
- おやすみモード（Do not disturb）
- リダイヤル

## 通常電話機によって実装される機能

これらの機能は、電話機のファームウェアによって実装されています。

![PBX機能が通常実装される場所：Asterisk自体、ダイヤルプラン、または電話機](../images/13-pbx-features-fig01.png)

- 通話保留
- ブラインド転送
- 相談転送
- 3者間会議
- メッセージ待機インジケータ

## 機能設定ファイル

この章で紹介する機能の一部は、features.conf設定ファイルで構成されます。このファイルを変更することで、一部の機能の動作を変更することが可能です。関連する抜粋を以下に含めました。この章の次のセクションで、各機能について説明します。サンプルファイルからの抜粋（Asterisk 22）

![features.confの`[featuremap]`セクション。デフォルトのDTMF機能コードが含まれる](../images/13-pbx-features-fig02.png)

Asterisk 12以降、通話パークは`features.conf`から独自のモジュール`res_parking`に移行され、設定は`res_parking.conf`で行われるようになりました。以下のパーキングロットブロック（`parkext`、`parkpos`、`context`、`parkingtime`など）は`res_parking.conf`に存在します。`[featuremap]`セクション（`parkcall`を含むDTMF機能コード）は`features.conf`に残っています。

パーキングロットのオプションは`res_parking.conf`にあります。`default`という名前のパーキングロットは、設定ファイルに存在しなくても常に存在します。以下の抜粋はAsterisk 22の`res_parking.conf.sample`から引用したものです。

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

DTMF機能コード（ワンステップ`parkcall`を含む）は、引き続き`features.conf`の`[featuremap]`セクションにあります。

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

## 通話転送

通話転送は、電話機、ATA、またはAsterisk自体によって実装できます。通話の転送方法については、電話機のマニュアルを参照してください。お使いの電話機が通話転送をサポートしていない場合は、Asteriskを使用してこのタスクを実行できます。通話転送には2つの異なる方法があります。最初の方法は、ブラインド転送機能を使用することです。#をダイヤルし、続いて転送先の番号をダイヤルします。IP電話やIPソフトフォンの転送機能を使用する場合もあります。features.confファイルのblindxferパラメータを編集することで、転送文字を変更できます。features.confファイルのatxferパラメータの前にある;を削除することで、Asteriskで相談転送を有効にできます。通話中に*2を押すと、Asteriskが「transfer」とアナウンスし、ダイヤルトーンが聞こえます。発信者は保留音に送られます。転送先の人と話をして電話を切ると、システムは発信者と転送先をブリッジします。

![通話転送：ブラインド転送（通話中に#を押す）と相談転送（*2を押す）の手順](../images/13-pbx-features-fig03.png)

### 設定タスクリスト

1. PJSIPエンドポイントの場合、オプション`direct_media`が`no`に設定されていることを確認してください（メディアがAsteriskを経由し、機能コードが検出されるようにするため）。または、`Dial()`アプリケーションで`t`/`T`オプションを使用してください。

## 通話パーク

この機能は通話をパーク（保留）するために使用されます。これは、例えば部屋の外で電話に出ているときに、その通話を自分のデスクに転送したい場合などに役立ちます。内線番号に通話をパークすることでこれを実現できます。デスクに戻ったら、パークした内線番号をダイヤルするだけで通話を復帰できます。

![通話パーク：700をダイヤルして最初の空きスロット（701–720）に通話をパークします。Asteriskがスロットをアナウンスし、どの電話機からでもその番号をダイヤルして通話を復帰できます](../images/13-pbx-features-fig04.png)

デフォルトでは、700の内線番号が通話のパークに使用されます。会話の途中で#を押すと、通話が700の内線番号に転送されます。するとAsteriskが701や702といったパーク先の内線番号をアナウンスします。電話を切ると、発信者は保留状態になります。デスクの電話機に行き、アナウンスされたパーク先の内線番号をダイヤルして通話を復帰します。発信者が長時間パークされたままの場合、タイムアウト機能がトリガーされ、最初にダイヤルされた内線番号が再び鳴ります。

### 設定タスクリスト

以下の手順に従って通話パークを有効にします。ステップ1：ダイヤルプランからパーキングロットに到達できるようにします（必須）。デフォルトのパーキングロットの`context`は`parkedcalls`です（`res_parking.conf`で設定）。そのコンテキストを、電話機がダイヤルするコンテキストに`extensions.conf`で含めます。

```
include => parkedcalls
```

ステップ2：#700をダイヤルして通話パーク機能をテストします。注意：

- パーク用内線番号は、CLIコマンドdialplan showには表示されません。
- パーキング設定ファイルを変更した後は、パーキングモジュールをリロードする必要があります：`module reload res_parking.so`。features.confの変更については、`module reload features.so`。
- 通話をパークするには、#700に転送する必要があります。`Dial()`アプリケーションの`t`および`T`オプションを確認してください。

## 通話ピックアップ

通話ピックアップを使用すると、同じコールグループ内の同僚の通話に応答できます。これは、例えば、部屋にいる他の人の電話が鳴っているが本人が不在の場合に、わざわざ席を立つ必要がなくなるため便利です。*8をダイヤルすることで、コールグループ内の通話に応答できます。この番号は以下で変更可能です。

```
features.conf file.
```

![通話ピックアップ：メンバーは自分のグループ内の通話のみ応答可能です。オペレーター（pickupgroup=1,2,3）はすべてのグループの通話に応答できます](../images/13-pbx-features-fig05.png)

### 設定タスクリスト

以下の手順に従って通話ピックアップ機能を設定します。ステップ1：内線番号のコールグループを設定します。これはチャネル設定ファイル（pjsip.conf, iax.conf, chan_dahdi.conf）で行います。PJSIPエンドポイントの場合は、`pjsip.conf`のエンドポイントセクションで`call_group`と`pickup_group`を設定します（pjsip.confはsnake_caseのオプション名を使用します）。このタスクは必須です。

PJSIP（pjsip.conf）の場合：
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


ステップ2：通話ピックアップ機能の番号を変更します（オプション）。これは`pjsip.conf`ではなく、`features.conf`の`[general]`セクションで設定されます。

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## 会議（通話会議）

Asteriskで会議を実装する方法はいくつかあります。最初のオプションは、電話機の3者間会議機能を使用することです。この機能を使用する場合、サーバー側でのサポートは必要ありません。ただし、3人以上の会議が必要な場合は、会議室を運用する必要があります。Asteriskの最新の会議アプリケーションはConfBridge（`app_confbridge`）です。

ConfBridgeはHD音声会議とビデオ会議をサポートしています。ビデオ会議にはトランスコーディングができないなどの制限があり、すべての参加者が同じコーデックとプロファイルを使用する必要があります。ビデオ会議は「発言者追従（follow-the-talker）」モードを使用し、最後に発言した人の映像を表示します。ConfBridgeでは新しいDTMFメニューを簡単に設定できます。

ConfBridgeは、Asterisk 19で非推奨となりAsterisk 21で削除された古いMeetMeアプリケーションに代わるものです。MeetMeとは異なり、ConfBridgeはDAHDIやハードウェアタイミングソースを**必要としません**。Asteriskの内蔵タイミングインターフェース（Linux上の`res_timing_timerfd`、または`res_timing_pthread`）に依存するため、`dahdi_dummy`モジュールは不要です。`MeetMe()`と`meetme.conf`を使用していた古いシステムから移行する場合は、以下のように`ConfBridge()`と`confbridge.conf`に置き換えてください。

### ConfBridge

会議室を開始するための構文を以下に示します。

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

コマンドの詳細な説明については、core show application confbridgeを使用してください。

![`core show application confbridge`の出力。シノプシス、構文、およびbridge_profile、user_profile、menu引数が表示されています](../images/13-pbx-features-fig06.png)

![複数のPJSIPエンドポイントが1つの名前付きConfBridge会議（101）に参加。1人の参加者が管理者。ミキシングとタイミングは`res_confbridge`と内蔵の`res_timing_*`タイマーによって処理され、DAHDIは不要](../images/13-pbx-features-fig09.png)

上記のように、3つの重要な引数があり、それぞれが`confbridge.conf`のセクションタイプに対応しています。**bridge_profile**（`type=bridge`セクション）：ここで参加者の最大数（`max_members`）、録音（`record_conference`）、`video_mode`、その他多くのブリッジ全体のパラメータを選択します。

サンプルファイル全体をここに再現しても意味がないため、confbridge.confファイルでbridge_profileを設定する簡単な例を示します。

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile**（`type=user`セクション）：ここで、ユーザーが管理者かどうか（`admin=yes`）、ミュート状態で開始するかどうか（`startmuted=yes`）、保留音など、ユーザーごとのオプションを定義します。例：

```
[admin_user]
type=user
admin=yes
```

**menu**（`type=menu`セクション）：ここで会議用のキーパッド（DTMF）マッピングを定義します。例えば、どのキーでミュートの切り替え、音量の調整、会議からの退出を行うかなどです。利用可能なすべてのアクションについては`confbridge.conf.sample`ファイルを確認してください。例：

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

#### Confbridge関数

会議ブリッジのオプションは、CONFBRIDGE()関数を使用してダイヤルプラン内で動的に渡すことができます。以下の例を参照してください。

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge管理者コマンドとMeetMeからの移行

MeetMeから移行する場合、以前`MeetMeAdmin()`と`a`（管理者）オプションを通じて使用していた管理者機能は、**管理者ユーザープロファイル**（`admin=yes`）と**メニュー**アクションを通じて表現されるようになりました。管理者プロファイルと管理者アクションを含むメニューで参加した管理者は、キーパッドから直接、会議室のロック、ユーザーの強制退出、参加者のミュートを行うことができます。`confbridge.conf`における関連メニューアクションは以下の通りです。

- `admin_kick_last` -- 最後に参加したユーザーを強制退出させる
- `admin_toggle_mute_participants` -- 管理者以外の全参加者をミュート/ミュート解除する
- `toggle_mute` -- 自分自身をミュート/ミュート解除する
- `participant_count` -- 参加者数をアナウンスする
- `leave_conference` -- ブリッジから退出してダイヤルプランを続行する

これらはMeetMeの`MeetMe()`オプションフラグ（`a`、`A`、`m`、`M`、`l`、`x`…）および`MeetMeAdmin()`コマンド（`k`、`K`、`L`、`M`、`N`…）に代わるものです。Asterisk 22には`meetme.conf`は存在しません。すべての会議設定は`confbridge.conf`にあり、変更は`module reload res_confbridge.so`で適用されます。

### ConfBridgeの例

内線番号500で到達可能な会議室を作成するには、`extensions.conf`で以下のようにします。

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

500をダイヤルした最初の発信者が会議`101`を作成し、後続の発信者がそこに参加します。ここで参照されているプロファイルとメニュー（`default_bridge`、`default_user`、`sample_user_menu`）は`confbridge.conf`で定義されています。PINを要求するには、ユーザープロファイルで`pin=`を設定します。参加者を会議管理者に設定するには、ユーザープロファイルに`admin=yes`を指定します。

## 通話録音

Asteriskで通話を録音する方法はいくつかあります。`MixMonitor()`アプリケーションを使用して簡単に通話を録音できます。（2つの別々のファイルを録音していた古い`Monitor`アプリケーションは削除されました。代わりに`MixMonitor`を使用してください。）

### MixMonitorアプリケーションの使用

`MixMonitor`アプリケーションは、現在のチャネルの音声を指定されたファイルに録音します。ファイル名が絶対パスの場合はそのパスを使用し、それ以外の場合はasterisk.confで設定された監視ディレクトリにファイルを作成します。

![MixMonitor()アプリケーション：チャネルの音声をファイルに録音・ミキシング。追記、ブリッジのみ、音量調整のオプションあり](../images/13-pbx-features-fig09.png)

### MixMonitor()

通話を録音し、録音中に音声をミキシングします。構文：`MixMonitor(filename.extension[,options[,command]])`。現在のチャネルの音声を指定されたファイルに録音します。有効なオプション：

- a - ファイルを上書きせず、追記します。
- b - チャネルがブリッジされている間のみ音声をファイルに保存します。
- 注意：会議は含まれません。
- v(<x>) - 可聴音量を<x>の係数で調整します（-4から4の範囲）。
- V(<x>) - 発話音量を<x>の係数で調整します（-4から4の範囲）。
- W(<x>) - 可聴音量と発話音量の両方を<x>の係数で調整します（-4から4の範囲）。
- <command>は録音終了時に実行されます。^{X}に一致する文字列は${X}にエスケープ解除され、すべての変数がその時点で評価されます。変数MIXMONITOR_FILENAMEには、録音に使用されたファイル名が含まれます。

興味深いリソースとして、ワンタッチ録音機能`automixmon`があります。これは、通話中にDTMFコード（デフォルトは`*3`）をダイヤルすることで、即座に録音を開始（および切り替え）できる機能です。MixMonitorに基づいて構築されているため、単一のミキシングされたファイルに書き込まれます。例：

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

`X`および`x`オプションは、発信者と着信者それぞれに対してワンタッチMixMonitor機能を有効にします。MixMonitorは単一のミキシングされたファイルを録音するため、後で個別のIN/OUTファイルを結合する必要はありません（`soxmix`用に2つのファイルを作成していた古い`automon`/`Monitor`アプローチは、`Monitor`アプリケーションとともに削除されました）。

Dial()アプリケーションの前にSet()を使用したくない場合は、globalsセクションでこれを設定できます。

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### 保留音

保留音（MOH）は、バージョン1.0、1.2、1.4の間で何度か変更されました。最新バージョンでは、MOHはデフォルトで「FILE-BASED」になっています。つまり、Asteriskはg729、alaw、ulaw、gsmなどの形式でMOHファイルを提供します。そのため、チャネルに送信する前に音楽をトランスコードする必要はありません。これによりプロセッサ時間を節約でき、本番システムで作業する人にとっては歓迎すべき変更です。古いバージョンでは、MOHは通常MP3で提供されていました（現在もそのように設定可能です）。MP3を使用してMOHを提供すると、Asteriskはトランスコードを強制され、その過程で貴重なCPUパワーを消費します。新しい設定ファイルを以下に示します。デフォルトのクラスは現在ネイティブファイル形式のmode=filesを使用していることに注意してください。他のすべてのモードはコメントアウトされています。各セクションはクラスです。現時点でコメントアウトされていない唯一のクラスはdefaultです。異なるファイルに対して異なるクラスを持たせたい場合は、新しいセクション（クラス）を作成する必要があります。

![musiconhold.confのサンプル設定。有効なMOHモード（quietmp3, mp3, custom, filesなど）がリストされています](../images/13-pbx-features-fig10.png)

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

次に、保留音を使用するには、チャネル設定ファイル（chan_dahdi.conf, pjsip.conf, iax.confなど）でMOHクラスを設定します。PJSIPエンドポイントの場合は、`pjsip.conf`のエンドポイントセクションで`moh_suggest`を設定します（レガシーな`musicclass`オプション名はchan_dahdiやその他のチャネルドライバに適用され、PJSIPには適用されません）。インストールされているfreeplayの曲は現在wav形式です。インストール時に（make menuselectを使用して）利用可能なMOHファイル形式を選択できます。新しいMOHファイルを追加する場合は、必要な形式で提供する必要があります。例：

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

ダイヤルプランでは、`StartMusicOnHold`でチャネル上の保留音を開始し、`StopMusicOnHold`で停止できます。

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

簡単なテストとして一定時間保留音を再生するには、期間（秒単位）を指定して`MusicOnHold`アプリケーションを使用します。

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## アプリケーションマップ

アプリケーションマップを使用すると、features.confファイルの`[applicationmap]`セクションを使用して新しい機能を追加できます。例えば、コールセンターで応答している顧客のタイプを識別する必要があるとします。顧客タイプごとにアプリケーションマップを作成し、タイプごとの応答済み顧客数をカウントすることができます。

## クイズ

1. 通話パークについて正しい記述はどれですか？
   - A. デフォルトでは、内線800が通話パークに使用されます。
   - B. デスクから離れているときに電話を受けた場合、通話をパークできます。システムがパークスロットをアナウンスし、どの電話機からでもそのスロットをダイヤルして通話を復帰できます。
   - C. デフォルトでは、内線700が通話をパークし、通話は701–720のスロットにパークされます。
   - D. パークされた通話を復帰するには700をダイヤルします。
2. 通話ピックアップ機能を使用するには、すべてのアテンションが同じ___にある必要があります。DAHDIチャネルの場合、これは___ファイルで設定されます。
3. 通話を転送する際、転送先にあらかじめ相談しない___転送と、完了前に転送先と話をする___転送を選択できます。
4. 相談転送を行うには___シーケンスを使用し、ブラインド転送には___を使用します。
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Asterisk 22で会議通話をホストするには、___アプリケーションを使用します。
6. ConfBridgeにおいて、参加者に管理者権限（強制退出、他者のミュート、会議室のロック）を付与するには、ユーザープロファイル（`confbridge.conf`）で___を設定します。
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. 保留音に最適な形式はMP3です。Asteriskサーバーでの処理負荷が非常に低いためです。
   - A. 正しい
   - B. 間違い
8. 特定のコールグループから通話をピックアップするには、一致する___グループに属している必要があります。
9. MixMonitor()アプリケーションまたはワンタッチ録音（`automixmon`）機能を使用して通話を録音できます。デフォルトでは、`automixmon`は___ DTMFシーケンスを使用します。
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. ConfBridgeにおいて、参加者をミュート状態で参加させる（会議を聞くことはできるが、ミュート解除されるまで発言できない）ユーザープロファイルオプション`confbridge.conf`はどれですか？
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**回答:** 1 — B, C · 2 — ピックアップグループ; `chan_dahdi.conf` · 3 — ブラインド; 相談 · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — ピックアップ · 9 — C · 10 — A
