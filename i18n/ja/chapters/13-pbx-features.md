# Using PBX features

SIP システムでは、ほとんどの電話機能はエンドポイントで実装されています。さまざまな SIP 電話機やメーカーが存在し、相互運用性は保証されていません。Asterisk 開発チームは、これらの機能の多くを PBX 自体で実装するという素晴らしい仕事を成し遂げ、Asterisk をほぼエンドポイントに依存しないものにしています。しかし、時には同じ機能が電話と Asterisk の両方で実行されていることがあります。電話と PBX の統合は、使いやすさに関する次のフロンティアであり、現在はプロプライエタリシステムが注力している領域です。本章では、これらの機能のほとんどをどのように使用するかを学びます。

## 目的

- コールパーキング
- コールピックアップ
- コール転送
- コール会議 (ConfBridge)
- コール録音
- 保留音楽

## 機能が実装される場所

まず第一に、PBX の機能が実行されるタイミングと、電話機がすべての処理を行うタイミングを理解することが重要です。たとえば、電話機の TRANSFER ボタンを使用するか、# をダイヤルして（PBX 自体が実行する無条件転送）転送を行うことができます。

## Asteriskで実装された機能

- ミュージック・オン・ホールド
- コール・パーキング
- コール・ピックアップ
- コール・レコーディング
- ConfBridge カンファレンスルーム
- コール・トランスファー（ブラインドおよびコンサルティブ）

## ダイヤルプランで通常実装される機能

- ビジー時の転送
- 即時転送
- 応答なし時の転送
- コールフィルタリング（ブラックリスト）
- 取り込み拒否
- 再ダイヤル

## 電話で通常実装される機能

These features are implemented by the phone’s firmware:

![PBX の機能は通常、Asterisk 本体、ダイヤルプラン、または電話側に実装されます](../images/13-pbx-features-fig01.png)

- 保留
- ブラインド転送
- コンサルティブ転送
- 三者会議
- メッセージ待ちインジケータ

## The features configuration file

この章で紹介する機能の一部は、features.conf 設定ファイルで構成されています。このファイルを変更することで、いくつかの機能の動作を変更することが可能です。以下に関連する抜粋を示します。この章の次のセクションでは、各機能について説明します。サンプルファイル（Asterisk 22）からの抜粋

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

Asterisk 12 以降、コールパーキングは `features.conf` から独立したモジュール `res_parking` に移行し、設定は `res_parking.conf` にあります。以下の parking-lot ブロック（`parkext`、`parkpos`、`context`、`parkingtime` など）は `res_parking.conf` にあります。DTMF 機能コード（`parkcall` を含む）を含む `[featuremap]` セクションは `features.conf` に残ります。

parking-lot のオプションは `res_parking.conf` にあります。名前が `default` のパーキングロットは、設定ファイルに記述がなくても常に存在します。以下の抜粋は Asterisk 22 `res_parking.conf.sample` からのものです：

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

DTMF 機能コード（ワンステップ `parkcall` を含む）は `[featuremap]` セクションの `features.conf` に残ります：

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

Call transfer can be implemented by the phone, by ATA, or by Asterisk itself. Refer to your phone manual to understand how calls are transferred. If your phone does not support call transfer, you can use Asterisk to accomplish this task. Call transfer is implemented in two different ways.

The first way is to use the blind transfer feature: dial # followed by the number to be transferred. Sometimes you will use the transfer feature of your IP phone or IP soft phone. You can change the transfer character by editing the blindxfer parameter in the features.conf file.

You can enable assisted transfer in Asterisk by removing the ; before the atxfer parameter in the features.conf file. During a conversation, you would press *2. Asterisk will say "transfer" and will give you a dial tone. The caller is sent to music on hold. After you speak to the destination person and hang up the phone, the system bridges the caller to the destination.

![Call transfer: the steps for a blind transfer (press # during the call) and an attended transfer (press *2)](../images/13-pbx-features-fig03.png)

### Configuration task list

1. For a PJSIP endpoint, make sure the option `direct_media` is set to `no` (so the media flows through Asterisk and the feature codes are detected), or use a `t`/`T` option in the `Dial()` application

## Call parking

この機能は通話をパーク（保留）するために使用されます。たとえば、部屋の外で電話に出て、通話をデスクに戻したい場合などに便利です。パーク用の内線に通話をパークすることで実現できます。デスクに戻ったら、パークされた内線番号をダイヤルするだけで通話を取り戻せます。

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

既定では 700 内線が通話のパークに使用されます。会話の最中に # を押して通話を 700 内線に転送します。すると Asterisk がパークされた内線（例: 701 や 702）をアナウンスします。電話を切ると、発信者は保留状態になります。デスクの電話でアナウンスされたパーク内線をダイヤルすれば通話を取り戻せます。発信者が長時間パークされた場合、タイムアウト機能が作動し、元のダイヤル先内線が再び鳴ります。

### Configuration task list

以下の手順に従って通話パークを有効にします。  
Step 1: ダイヤルプランからパークロットへアクセスできるようにします（必須）。既定のパークロットの `context` は `parkedcalls`（`res_parking.conf`で設定）です。そのコンテキストを、電話がダイヤルするコンテキストに `extensions.conf` で含めます。

```
include => parkedcalls
```

Step 2: #700 をダイヤルして通話パーク機能をテストします。注意点:

- パーク内線は `dialplan show` CLI コマンドには表示されません。
- パーク設定ファイルを変更した後はパークモジュールをリロードする必要があります: `module reload res_parking.so`。`features.conf` の変更後は `module reload features.so`。
- 通話をパークするには #700 に転送する必要があります。``t`` と ``T`` オプションが ``Dial()`` アプリケーションで有効か確認してください。

## Call pickup

Call pickup allows you to capture a call from a colleague in the same call group. This would help avoid, for example, having to wake up to take a call that is ringing to another person in your room, but who is not present. By dialing *8, you can capture a call within your call group. This number can be modified in the `features.conf` file.

![Call pickup: members can only capture calls within their own group; the operator (pickupgroup=1,2,3) can pick up calls from every group](../images/13-pbx-features-fig05.png)

### Configuration task list

Follow the steps below to configure the call pickup feature. Step 1: Configure a call group for your extensions. This is done in the channel configuration file (pjsip.conf, iax.conf, chan_dahdi.conf). For PJSIP endpoints, set `call_group` and `pickup_group` in the endpoint section of `pjsip.conf` (pjsip.conf uses snake_case option names). This task is required.

For PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Step 2: Change the call-pickup feature number (optional). This is set in the `[general]` section of `features.conf`, not in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conference (call conference)

Asterisk でカンファレンスを実装する方法はいくつかあります。最初のオプションは、電話機の三者通話機能を単に使用することです。この機能を電話機で利用すれば、サーバ側でのサポートは必要ありません。ただし、3 人以上のカンファレンスを行いたい場合は、カンファレンスルームを実行する必要があります。Asterisk の最新のカンファレンスアプリケーションは ConfBridge (`app_confbridge`) です。

ConfBridge は HD 音声カンファレンスとビデオカンファレンスをサポートします。ビデオカンファレンスにはいくつかの制限があり、トランスコーディングができないため、すべての参加者が同じコーデックとプロファイルを使用しなければなりません。ビデオカンファレンスは「話者追従」モードで、最後に話した人の映像が表示されます。ConfBridge では新しい DTMF メニューを簡単に設定できます。

ConfBridge は、Asterisk 19 で非推奨となった従来の MeetMe アプリケーションに取って代わります。MeetMe は Asterisk 22 のソースツリーにはまだ含まれていますが、DAHDI に依存しておりデフォルトではビルドされません。そのため、一般的な PJSIP インストールでは利用できず、ConfBridge がサポートされるカンファレンスアプリケーションとなります。MeetMe とは異なり、ConfBridge は **DAHDI** やハードウェアタイミングソースを必要とせず、Asterisk の組み込みタイミングインターフェース（Linux の場合は`res_timing_timerfd`、または`res_timing_pthread`）に依存します。そのため `dahdi_dummy` モジュールは不要です。古いシステムで `MeetMe()` と `meetme.conf` を使用していた場合は、以下に示すようにそれらを `ConfBridge()` と `confbridge.conf` に置き換えてください。

### ConfBridge

カンファレンスルームを開始する構文は以下のとおりです。

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

完全なコマンドの説明を取得するには、`core show application confbridge` を使用します。

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

上記のように、3 つの重要な引数があり、各々が`confbridge.conf`のセクションタイプに対応しています。**bridge_profile**（`type=bridge`セクション）：ここで参加者の最大数（`max_members`）、録音（`record_conference`）、`video_mode`、その他多数のブリッジ全体のパラメータを選択します。

ここに全例ファイルをすべて掲載する意味はありませんので、`confbridge.conf` ファイルで bridge_profile を設定する簡単な例を示します。

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile**（`type=user`セクション）：ここでユーザーごとに固有のオプションを定義します。たとえば、ユーザーが管理者かどうか（`admin=yes`）、ミュート状態で開始するかどうか（`startmuted=yes`）、ミュージックオンホールドなど、その他多数のユーザー固有オプションがあります。例:

```
[admin_user]
type=user
admin=yes
```

**menu** (a `type=menu` section): ここで会議のキーパッド（DTMF）マッピングを定義します — たとえばどのキーがミュートの切替、音量調整、会議からの退出を行うかです。 `confbridge.conf.sample` ファイルを確認して利用可能なすべてのアクションを確認してください。 Example:

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

会議ブリッジのオプションは、dial plan で CONFBRIDGE() 関数を使用して動的に渡すことができます。以下の例をご覧ください。

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge 管理コマンドと MeetMe からの移行

MeetMe から移行してくる場合、`MeetMeAdmin()` と `a` (admin) オプションで使用していた管理機能は、**admin ユーザープロファイル**（`admin=yes`）と **メニュー** アクションで表現されます。admin プロファイルで参加し、admin アクションを含むメニューを持つ管理者は、キー入力だけで部屋をロックしたり、ユーザーをキックしたり、参加者をミュートにしたりできます。`confbridge.conf` の該当メニューアクションは次のとおりです。

- `admin_kick_last` -- 最後に参加したユーザーをキック
- `admin_toggle_mute_participants` -- 管理者以外の全参加者をミュート/ミュート解除
- `toggle_mute` -- 自分自身をミュート/ミュート解除
- `participant_count` -- 参加者数をアナウンス
- `leave_conference` -- ブリッジを離れ、ダイヤルプランで続行

これらは MeetMe `MeetMe()` オプションフラグ（`a`、`A`、`m`、`M`、`l`、`x`、…）および `MeetMeAdmin()` コマンド（`k`、`K`、`L`、`M`、`N`、…）に取って代わります。最新の PJSIP 環境では `app_meetme` をロードすることはなく、すべての会議設定は `confbridge.conf` にあり、変更は `module reload app_confbridge.so` で適用されます（ConfBridge のロジックは `app_confbridge` にあり、`res_confbridge` モジュールは存在しません）。

### ConfBridge の例

エクステンション 500 でアクセス可能な会議室を作成するには、`extensions.conf` で次のようにします。

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

500 をダイヤルした最初の発信者が会議 `101` を作成します；その後の発信者はそれに参加します。ここで参照されているプロファイルとメニュー（`default_bridge`、`default_user`、`sample_user_menu`）は `confbridge.conf` で定義されています。PIN を要求するには、ユーザープロファイルで `pin=` を設定します；参加者を会議管理者にするには、`admin=yes` を持つユーザープロファイルを付与します。

## Call Recording

Asterisk で通話を録音する方法はいくつかあります。通話を簡単に録音するには `MixMonitor()` アプリケーションを使用できます。（2 つの別々のファイルを録音していた古い `Monitor` アプリケーションは削除されました；代わりに `MixMonitor` を使用してください。）

### Using the MixMonitor application

`MixMonitor` アプリケーションは、現在のチャンネルの音声を指定されたファイルに録音します。ファイル名が絶対パスの場合はそのパスを使用します。そうでない場合は、asterisk.conf の設定された monitoring ディレクトリにファイルを作成します。

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

通話を録音し、録音中に音声をミックスします。構文: `MixMonitor(filename.extension[,options[,command]])`。現在のチャンネルの音声を指定されたファイルに録音します。有効なオプション:

- a - 上書きせずにファイルに追記します。
- b - チャンネルがブリッジされている間だけ音声をファイルに保存します。
- Note: does not include conferences.
- v(<x>) - 可聴音量を <x> 倍に調整します（範囲は -4 から 4）。
- V(<x>) - 発話音量を <x> 倍に調整します（範囲は -4 から 4）。
- W(<x>) - 可聴音量と発話音量の両方を <x> 倍に調整します（範囲は -4 から 4）。
- <command> は録音が終了したときに実行されます。`^{X}` にマッチする文字列は `${X}` にアンエスケープされ、すべての変数はその時点で評価されます。変数 `MIXMONITOR_FILENAME` には録音に使用されたファイル名が格納されます。

興味深いリソースとして、ワンタッチ録音機能 `automixmon` があります。これは通話中に相手が DTMF コードをダイヤル（`features.conf` のサンプルでは `*3` が示唆されています；デフォルトは組み込みされていないため設定が必要です）すると、すぐに録音を開始（またはオフに）できます。MixMonitor 上に構築されているため、単一のミックスファイルが生成されます。例:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

`X`および`x`オプションは、発信者と受信者それぞれにワンタッチMixMonitor機能を有効にします。MixMonitorは単一の混合ファイルを記録するため、後で別々のIN/OUTファイルを結合する必要はありません（`automon`/`Monitor`方式のように`soxmix`用に2つのファイルを生成した古い手法は、`Monitor`アプリケーションとともに削除されました）。

Dial()アプリケーションの前にSet()を使用したくない場合は、globalsセクションでこれを設定できます。

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Music on hold

Music on hold (MOH) はバージョン 1.0、1.2、1.4 の間で何度か変更されました。最新バージョンでは、MOH のデフォルトは「FILE-BASED」になっています。つまり、Asterisk は g729、alaw、ulaw、gsm などの形式の MOH ファイルを直接提供します。そのため、音楽をチャンネルに送る前にトランスコードする必要はありません。これにより CPU 時間が節約でき、実運用システムで作業する人にとっては歓迎すべき変更です。

古いバージョンでは、MOH は通常 MP3 で提供されていました（まだそのように設定することも可能です）。MP3 で MOH を提供すると、Asterisk はトランスコードを行わなければならず、貴重な CPU リソースを消費します。

新しい設定ファイルは以下に示されています。デフォルトクラスは現在、ネイティブファイル形式 mode=files を使用しています。他のモードはすべてコメントアウトされています。各セクションがクラスです。現時点でコメントが外されているクラスは default だけです。異なるファイル用に別のクラスを作成したい場合は、新しいセクション（クラス）を作成する必要があります。

![musiconhold.conf のサンプル設定、利用可能な MOH モード（quietmp3、mp3、custom、files、…）を一覧表示](../images/13-pbx-features-fig10.png)

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

### MOH 設定タスク

保留音楽（MOH）を使用するには、チャネル設定ファイル（chan_dahdi.conf、pjsip.conf、iax.conf など）で MOH クラスを設定します。PJSIP エンドポイントの場合、`moh_suggest` を `pjsip.conf` のエンドポイントセクションに設定します（レガシーの`musicclass` オプション名は chan_dahdi や他のチャネルドライバには適用されますが、PJSIP には適用されません）。フリープレイのチューンは現在 wav 形式でインストールされています。インストール時に、利用可能な MOH ファイル形式を（make menuselect を使用して）選択できます。新しい MOH ファイルを追加したい場合は、必要な形式で用意する必要があります。例：

`/etc/asterisk/chan_dahdi.conf` に `musiconhold` 行を追加します。

```
[channels]
musiconhold=default
```

次に、`/etc/asterisk/musiconhold.conf`を編集してそのクラスを定義します：

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

ダイヤルプランでは、`StartMusicOnHold`を使用してチャンネルで保留音を開始できます（`StopMusicOnHold`で停止します）。

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

To play music on hold for a fixed time as a quick test, use the `MusicOnHold` application with a duration (in seconds):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## アプリケーションマップ

アプリケーションマップを使用すると、features.conf ファイルの `[applicationmap]` セクションを利用して新機能を追加できます。コールセンターで対応する顧客のタイプを識別する必要があるとします。顧客タイプごとにアプリケーションマップを作成すれば、タイプ別に応答した顧客数をカウントできます。

## Summary

この章では、Asterisk の PBX 機能がどこに実装されているか――コア、ダイヤルプラン、電話機のそれぞれ――と、DTMF 機能コードが `[featuremap]` の `features.conf` セクションでどのようにマッピングされているかを学びました。**call transfer**（ブラインドおよびアテンド）と **call parking**（`res_parking.conf`、`k`/`K` Dial オプションと `parkedcalls` ロット）、**call pickup**（グループ単位）、そして **ConfBridge**（`confbridge.conf` bridge/user/menu プロファイル）による **conferencing**（旧 MeetMe の代替）を設定しました。**MixMonitor**（`automixmon`、`X`/`x` Dial オプション、`DYNAMIC_FEATURES`）を使用した **one-touch recording**、**music on hold** の設定、そして **application maps** によって DTMF シーケンスに独自のダイヤルプランロジックをバインドできる方法も確認しました。これらの構成要素を組み合わせることで、ビジネス PBX がユーザーに期待される日常的な機能を提供できるようになります。

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___. For DAHDI channels this is configured in the ___ file.
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
