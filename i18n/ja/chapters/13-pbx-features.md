# PBX機能の使用

SIPシステムでは、電話機能のほとんどはエンドポイント（端末）側で実装されています。多種多様なSIP電話機やメーカーが存在するため、相互運用性は保証されていません。Asterisk開発チームは、PBX自体にほとんどの機能を実装するという素晴らしい仕事をしており、Asteriskをほぼエンドポイントに依存しないものにしています。しかし、電話機とAsteriskの両方で同じ機能が実行されていることに気づく場合もあるでしょう。電話機とPBXの統合は、ユーザビリティにおける次のフロンティアであり、現在プロプライエタリなシステムが注力している分野です。本章では、これらの機能のほとんどを使用する方法を学びます。

## 学習目標

本章を終える頃には、以下の機能を理解し、使用できるようになります。

- 通話パーク（Call Parking）
- 通話ピックアップ（Call Pickup）
- 通話転送（Call Transfer）
- 通話会議（ConfBridge）
- 通話録音（Call Recording）
- 保留音（Music on hold）

## 機能が実装される場所

まず何よりも、PBX機能がいつ実行されるのか、あるいはいつ電話機がすべての処理を行っているのかを理解することが重要です。例えば、電話機のTRANSFERボタンを使用して通話を転送することも、#をダイヤルして（PBX自体が実行する無条件転送）転送することもできます。

## Asteriskによって実装される機能

これらの機能は、AsteriskのコードによってPBX内に実装されています。

- 保留音
- 通話パーク
- 通話ピックアップ
- 通話録音
- ConfBridge会議室
- 通話転送（ブラインド転送および相談転送）

## 通常ダイアルプランによって実装される機能

これらの機能は、Asteriskのダイアルプラン（extensions.conf）でプログラムする必要があります。

- 話中時転送
- 無条件転送
- 不応答時転送
- 通話フィルタリング（ブラックリスト）
- おやすみモード（Do not disturb）
- リダイヤル

## 通常電話機によって実装される機能

これらの機能は、電話機のファームウェアによって実装されています。

![PBX機能が通常実装される場所：Asterisk自体、ダイアルプラン、または電話機](../images/13-pbx-features-fig01.png)

- 通話保留
- ブラインド転送
- 相談転送
- 3者間会議
- メッセージ待機表示（MWI）

## 機能設定ファイル

本章で紹介する機能の一部は、features.conf設定ファイルで構成されます。このファイルを変更することで、一部の機能の動作を変更することが可能です。以下に関連する抜粋を記載しました。本章の次のセクションでは、各機能について説明します。サンプルファイルからの抜粋（Asterisk 22）

![デフォルトのDTMF機能コードを含む、features.confの`[featuremap]`セクション](../images/13-pbx-features-fig02.png)

> **[第2版注記]** Asterisk 12以降、通話パークは`features.conf`/`app_features`から独自のモジュール`res_parking`へと移行され、設定は`res_parking.conf`で行われるようになりました。以下のパーキングロットブロック（parkext、parkpos、context、parkingtimeなど）は`res_parking.conf`に存在し、Asterisk 22の`res_parking.conf.sample`の構文を使用して示されています。`[featuremap]`セクション（`parkcall`を含むDTMF機能コード）は`features.conf`に残っています。

パーキングロットのオプションは`res_parking.conf`に存在します。設定ファイルに存在しない場合でも、`default`という名前のパーキングロットは常に存在します。以下の抜粋はAsterisk 22の`res_parking.conf.sample`から引用したものです。

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

DTMF機能コード（ワンステップ`parkcall`を含む）は、`features.conf`の`[featuremap]`セクションに残っています。

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

## 通話転送

通話転送は、電話機、ATA、またはAsterisk自体によって実装できます。通話の転送方法については、お使いの電話機の手順書を参照してください。お使いの電話機が通話転送をサポートしていない場合は、Asteriskを使用してこのタスクを実行できます。通話転送は2つの異なる方法で実装されます。1つ目の方法は、ブラインド転送機能を使用することです。#に続いて転送先の番号をダイヤルします。IP電話機やIPソフトフォンの転送機能を使用する場合もあります。features.confファイルのblindxferパラメータを編集することで、転送文字を変更できます。features.confファイルのatxferパラメータの前にある;を削除することで、Asteriskで相談転送を有効にできます。会話中に*2を押すと、Asteriskが「transfer」とアナウンスし、ダイアルトーンが聞こえます。発信者は保留音に送られます。転送先の人と話した後に電話を切ると、システムは発信者と転送先をブリッジします。

![通話転送：ブラインド転送（通話中に#を押す）と相談転送（*2を押す）の手順](../images/13-pbx-features-fig03.png)

### 設定タスクリスト

1. 電話機がSIPベースの場合は、directmediaオプションがnoに設定されていることを確認するか、dial()アプリケーションでtまたはTオプションを使用してください。

## 通話パーク

この機能は、通話をパーク（保留）するために使用されます。これは、例えば部屋の外で電話に出たときに、その通話を自分のデスクに戻したい場合などに役立ちます。通話を内線にパークすることでこれを実現できます。デスクに着いたら、パークした内線番号をダイヤルするだけで通話を復帰できます。

![通話パーク：700をダイヤルして最初の空きスロット（701–720）にパークします。Asteriskがスロットをアナウンスし、どの電話機からでもその番号をダイヤルして通話を復帰できます](../images/13-pbx-features-fig04.png)

デフォルトでは、700の内線番号が通話のパークに使用されます。会話の途中で#を押すと、通話が700の内線に転送されます。するとAsteriskが701や702といったパーク先の内線番号をアナウンスします。電話を切ると、発信者は保留状態になります。デスクの電話機に行き、アナウンスされたパーク先の内線番号をダイヤルして通話を復帰してください。発信者が長時間パークされたままだと、タイムアウト機能がトリガーされ、最初にダイヤルされた内線が再び鳴ります。

### 設定タスクリスト

以下の手順に従って通話パークを有効にします。ステップ1：ダイアルプランからパーキングロットに到達できるようにします（必須）。デフォルトのパーキングロットの`context`は`parkedcalls`です（`res_parking.conf`で設定）。そのコンテキストを、電話機がダイヤルするコンテキストに`extensions.conf`で含めます。

```
include => parkedcalls
```

ステップ2：#700をダイヤルして通話パーク機能をテストします。注意：

- パーク用内線はdialplan show CLIコマンドには表示されません。
- パーキング設定ファイルを変更した後は、パーキングモジュールをリロードする必要があります：`module reload res_parking.so`。features.confの変更については、`module reload features.so`を実行してください。
- 通話をパークするには、#700へ転送する必要があります。dial()アプリケーションのtおよびTオプションを確認してください。

## 通話ピックアップ

通話ピックアップを使用すると、同じコールグループ内の同僚の通話に応答できます。これは、例えば、自分の部屋にいるがその場にいない別の人の電話が鳴っているときに、わざわざ立ち上がって電話に出る必要を避けるのに役立ちます。*8をダイヤルすることで、コールグループ内の通話をキャプチャできます。この番号は以下で変更可能です。

```
features.conf file.
```

![通話ピックアップ：メンバーは自分のグループ内の通話のみをキャプチャできます。オペレーター（pickupgroup=1,2,3）はすべてのグループの通話をピックアップできます](../images/13-pbx-features-fig05.png)

### 設定タスクリスト

以下の手順に従って通話ピックアップ機能を設定します。ステップ1：内線用のコールグループを設定します。これはチャネル設定ファイル（pjsip.conf, iax.conf, chan_dahdi.conf）で行います。PJSIPエンドポイントの場合は、`pjsip.conf`のエンドポイントセクションで`call_group`と`pickup_group`を設定します（pjsip.confはsnake_caseのオプション名を使用します）。このタスクは必須です。

PJSIPの場合（pjsip.conf）：
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


ステップ2：通話ピックアップ機能の番号を変更します（オプション）。

```
pickupexten=*8; Configures the call pickup extension
```

## 会議（通話会議）

Asteriskで会議を実装する方法はいくつかあります。最初のオプションは、電話機の3者間会議機能を使用することです。この機能を使用する場合、サーバー側でのサポートは不要です。しかし、3人以上の会議が必要な場合は、会議室を運用する必要があります。Asteriskの最新の会議アプリケーションはConfBridge（`app_confbridge`）です。

ConfBridgeはHD音声会議とビデオ会議をサポートしています。ビデオ会議にはトランスコーディングができないという制限があり、すべての参加者が同じコーデックとプロファイルを使用する必要があります。ビデオ会議は「話者追従（follow-the-talker）」モードを使用し、最後に話した人の映像を表示します。ConfBridgeでは新しいDTMFメニューを簡単に設定できます。

> **[第2版注記]** MeetMe（`app_meetme`）は**Asterisk 19で非推奨**となり、Asterisk 21で削除される予定でしたが、その削除は（ViciDialプロジェクトの要請により）一時停止されました。モジュールのソースはAsterisk 22にも同梱されていますが、DAHDIが必要であり、**デフォルトのAsterisk 22ビルドではビルドされません**。標準インストールには`app_meetme.so`は存在せず、`MeetMe()`アプリケーションは使用できません。新しい会議室の展開にはすべてConfBridgeを使用する必要があります。以下のMeetMeセクションは歴史的参照のためにのみ保持されています。

### Confbridge

会議室を開始するための構文は以下の通りです。

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

コマンドの詳細な説明を得るには、core show application confbridgeを使用してください。

![`core show application confbridge`の出力。概要、構文、bridge_profile、user_profile、およびmenu引数が表示されています](../images/13-pbx-features-fig06.png)

上記のように、3つの重要なセクションがあります。Bridge_profile：confbridge.confファイルでプロファイルを定義します。そこで、最大参加者数、録音、video_mode、その他多くのブリッジパラメータを選択できます。

ここでサンプルファイル全体を再現しても意味がないため、confbridge.confファイルでbridge_profileを設定する簡単な例を示します。

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

User_profile：ここでは、ユーザーが管理者かどうかなど、ユーザー固有のオプションを定義します。保留音やその他多くのオプションをユーザーごとに設定できます。例：

```
[admin_user]
type=user
admin=yes
```

Menu：メニューセクションでは、ミュートやミュート解除を切り替えるためのアプリケーションのキーボードマッピングを定義できます。オプションについてはconfbridge.confファイルを確認してください。例：

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

会議ブリッジのオプションは、CONFBRIDGE()関数を使用してダイアルプラン内で動的に渡すことができます。以下の例を参照してください。

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

## Meetme（レガシー — 非推奨、Asterisk 22ではデフォルトでビルドされません）

> **[第2版注記]** `app_meetme`はAsterisk 19で非推奨となりました。Asterisk 21での削除予定は一時停止されたため、ソースはAsterisk 22にも同梱されていますが、モジュールはデフォルトのAsterisk 22ビルドではビルドされません（DAHDIに依存するため）。したがって、標準的なAsterisk 22インストールには`MeetMe()`アプリケーションは存在しません。以下の内容は歴史的参照用であり、古いシステムからアップグレードする読者のために保持されています。**新規インストールにはConfBridge（上記参照）を使用してください。** DAHDIの依存関係と`dahdi_dummy`モジュールはConfBridgeには不要です。

あるいは、古いAsteriskバージョンではmeetme()アプリケーションを使用できました。Meetmeは非常に使いやすい会議ブリッジです。MeetmeはAsterisk 19で非推奨となり、同期のためにDAHDIモジュールに依存していることに注意してください。

![MeetMe会議タイプ — シングルスピーカー、パスワード保護、動的会議 — すべてZaptel/DAHDIタイミングソースが必要](../images/13-pbx-features-fig07.png)

### meetme()アプリケーション

meetme show CLIコマンドを使用すると、上記の説明を取得できます。meetmeを使用するには、DAHDIドライバーをコンパイルし、少なくとも1つのDAHDIカーネルモジュールをロードしておく必要があります。DAHDIカードがインストールされていない場合は、dahdi_dummyカーネルモジュールをロードしてタイミングソースを提供してください。説明：

![MeetMe()アプリケーション：構文`MeetMe([confno][,[options][,pin]])`とその主なオプションフラグ](../images/13-pbx-features-fig08.png)

meetme()アプリケーションは、ユーザーを指定されたMeetme会議に参加させます。会議番号が省略された場合、ユーザーは番号の入力を求められます。ユーザーは電話を切るか、pオプションが指定されている場合は#を押すことで会議から退出できます。注意：会議を適切に動作させるには、DAHDIカーネルモジュールと少なくとも1つのハードウェアドライバー（またはdahdi_dummy）が存在する必要があります。さらに、iおよびrオプションを動作させるには、chan_dahdiチャネルドライバーがロードされている必要があります。

> **[第2版注記]** 続くオプションフラグと管理コマンドのリストは、レガシーな`app_meetme`インターフェースを説明するものであり、歴史的な`MeetMe()`/`MeetMeAdmin()`ドキュメントを反映しています。`app_meetme`はデフォルトのAsterisk 22インストールではビルドされないため、これらのフラグを稼働中のAsterisk 22システムで確認することはできません。これらは古い環境を維持している読者のために再現されています。Asterisk 22では、ConfBridgeと`CONFBRIDGE()`ダイアルプラン関数を使用してください。

オプション文字列には、以下の文字を0個以上含めることができます。

- 'a' -- 管理者モードを設定
- 'A' -- マーク付きモードを設定
- 'b' – ${MEETME_AGI_BACKGROUND}で指定されたAGIスクリプトを実行。デフォルト：conf-background.agi（注：これは同じ会議内の非DAHDIチャネルでは動作しません）
- 'c' -- 会議参加時にユーザー数をアナウンス
- 'd' -- 会議を動的に追加
- 'D' -- 会議を動的に追加し、PINを要求
- 'e' -- 空の会議を選択
- 'E' -- 空のPINなし会議を選択
- 'i' -- ユーザーの参加/退出をレビュー付きでアナウンス
- 'I' -- ユーザーの参加/退出をレビューなしでアナウンス
- 'l' -- リッスン専用モードを設定（聞くだけ、話すことは不可）
- 'm' -- 初期状態でミュートを設定
- 'M' -- 会議に1人しかいない場合に保留音を有効化
- 'o' -- 話者最適化を設定。話していない話者をミュートとして扱い、(a)送信時のエンコードを行わず、(b)話していると登録されていない受信音声を省略することで、バックグラウンドノイズの蓄積を防ぐ
- 'p' -- '#'を押して会議から退出することを許可
- 'P' -- 指定されていても常にPINを要求
- 'q' -- 静音モード（入退室音を再生しない）
- 'r' -- 会議を録音（${MEETME_RECORDINGFILE}として、${MEETME_RECORDINGFORMAT}形式で録音）。デフォルトのファイル名は meetme-conf-rec-${CONFNO}-${UNIQUEID}、デフォルト形式はwav。
- 's' -- '*'を受信したときにメニュー（ユーザーまたは管理者）を表示（メニューへ「送信」）
- 't' -- 話す専用モードを設定（話すだけ、聞くことは不可）
- 'T' -- 話者検出を設定（マネージャーインターフェースとmeetmeリストに送信）
- 'w[(<secs>)]' -- マークされたユーザーが会議に参加するまで待機
- 'x' -- 最後にマークされたユーザーが退出したときに会議を閉じる
- 'X' -- ユーザーが有効な1桁の内線${MEETME_EXIT_CONTEXT}、またはその変数が定義されていない場合は現在のコンテキストを入力して会議から退出することを許可
- '1' -- 最初の人が入室したときにメッセージを再生しない

### Meetme設定ファイル

このファイルはmeetmeアプリケーションの設定に使用されます。例：

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

meetme.confファイルの変更をAsteriskに反映させるために、リロードや再起動を行う必要はありません。

### Meetme関連アプリケーション

meetme()アプリケーションには、他に2つのサポートアプリケーションがあります。

```
MeetMeCount(confno[|var])
```

これは会議内のユーザー数を再生します。変数が指定されている場合、メッセージは再生されず、ユーザー数がその変数に設定されます。

```
MeetMeAdmin(confno,command,[user]):
```

会議の管理コマンドを実行します：

- 'e' -- 最後に参加したユーザーを退出させる
- 'k' -- ユーザーを1人会議からキックする
- 'K' -- すべてのユーザーを会議からキックする
- 'l' -- 会議のロックを解除する
- 'L' -- 会議をロックする
- 'm' -- ユーザー1人のミュートを解除する
- 'M' -- ユーザー1人をミュートにする
- 'n' -- 会議内の全ユーザーのミュートを解除する
- 'N' -- 会議内の管理者以外の全ユーザーをミュートにする
- 'r' -- ユーザー1人の音量設定をリセットする
- 'R' -- 全ユーザーの音量設定をリセットする
- 's' -- 会議全体の通話音量を下げる
- 'S' -- 会議全体の通話音量を上げる
- 't' -- ユーザー1人の通話音量を下げる
- 'T' -- 全ユーザーの通話音量を下げる
- 'u' -- ユーザー1人の聞き取り音量を下げる
- 'U' -- 全ユーザーの聞き取り音量を下げる
- 'v' -- 会議全体の聞き取り音量を下げる
- 'V' -- 会議全体の聞き取り音量を上げる

### Meetme設定タスクリスト

以下の手順に従ってMeetme会議アプリケーションを設定します。ステップ1：Meetmeルームの内線番号を選択する（必須）。ステップ2：meetme.confファイルを編集してパスワードを設定する（オプション）。

### 例

例#1：シンプルなMeetmeルーム1。extensions.confファイルで会議室101を作成します。

```
exten=>500,1,MeetMe(101,,123456)
```

2. meetme.confファイルで、ルーム101のパスワードを設定します。重要な注意：meetme()アプリケーションが動作するにはタイマーが必要です。Digiumハードウェアがインストール・設定されていない場合は、タイミングソースとしてdahdi_dummyを使用してください。

## 通話録音

Asteriskで通話を録音する方法はいくつかあります。mixmonitor()アプリケーションを使用すると、簡単に通話を録音できます。

### mixmonitorアプリケーションの使用

mixmonitorアプリケーションは、現在のチャネルの音声を指定されたファイルに録音します。ファイル名が絶対パスの場合はそのパスを使用し、それ以外の場合はasterisk.confで設定されたモニタリングディレクトリにファイルを作成します。

![MixMonitor()アプリケーション：チャネルの音声を録音・ミックスしてファイルに保存。追加、ブリッジのみ、音量調整のオプションあり](../images/13-pbx-features-fig09.png)

### Mixmonitor()

通話を録音し、録音中に音声をミックスする [説明] MixMonitor(<file>.<ext>[|<options>[|<command>]]) 現在のチャネルの音声を指定されたファイルに録音します。オプション：a - 上書きせずにファイルに追加。b - チャネルがブリッジされている間のみ音声をファイルに保存。注：会議は含まれません。v(<x>) - 聞こえる音量を<x>倍に調整。V(<x>) - 話す音量を<x>倍に調整。W(<x>) - 聞こえる音量と話す音量の両方を調整。有効なオプション：

- a - 上書きせずにファイルに追加します。
- b - チャネルがブリッジされている間のみ音声をファイルに保存します。
- 注：会議は含まれません。
- v(<x>) - 聞こえる音量を<x>倍に調整します（-4から4の範囲）。
- V(<x>) - 話す音量を<x>倍に調整します（-4から4の範囲）。
- W(<x>) - 聞こえる音量と話す音量の両方を<x>倍に調整します（-4から4の範囲）。
- <command>は録音終了時に実行されます。^{X}に一致する文字列は${X}にエスケープ解除され、すべての変数はその時点で評価されます。変数MIXMONITOR_FILENAMEには録音に使用されたファイル名が含まれます。

興味深いリソースとしてautomonがあります。これを使用すると、*1をダイヤルするだけで即座に録音を開始できます。例：

```
exten=>_4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten=>_4XXX,2,Dial(PJSIP/${EXTEN},20,jtTwW);wW enables the recording.
```

音声チャネルは着信（IN）と発信（OUT）に分かれており、/var/spool/asterisk/monitorディレクトリ内の2つの別々のファイルに分離されます。両方のファイルはsoxアプリケーションを使用してミックスできます。

```
debian#soxmix *in.wav *out.wav output.wav
```

Dial()アプリケーションの前にSet()を使用したくない場合は、globalsセクションでこれを設定できます：

```
[globals]
DYNAMIC_FEATURES=>automon
```

### 保留音

保留音（MOH）は、バージョン1.0、1.2、1.4の間で何度か変更されました。最新バージョンでは、MOHはデフォルトで「FILE-BASED」になっています。つまり、Asteriskはg729、alaw、ulaw、gsmなどの形式でMOHファイルを提供します。そのため、チャネルに送信する前に音楽をトランスコードする必要はありません。これによりプロセッサ時間を節約でき、本番システムを運用する人々にとって歓迎される変更です。古いバージョンでは、MOHは通常MP3で提供されていました（現在もそのように設定可能です）。MP3を使用してMOHを提供すると、Asteriskはトランスコードを強制され、その過程で貴重なCPUパワーを消費します。新しい設定ファイルを以下に示します。デフォルトクラスは現在、ネイティブファイル形式のmode=filesを使用していることに注意してください。他のすべてのモードはコメントアウトされています。各セクションがクラスです。現時点でコメントアウトされていないクラスはdefaultのみです。異なるファイルに対して異なるクラスを持たせたい場合は、新しいセクション（クラス）を作成する必要があります。

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

保留音を使用するには、チャネル設定ファイル（chan_dahdi.conf, pjsip.conf, iax.confなど）でMOHクラスを設定します。PJSIPエンドポイントの場合は、`pjsip.conf`のエンドポイントセクションで`moh_suggest`を設定します（レガシーな`musicclass`オプション名はchan_dahdiや他のチャネルドライバーに適用され、PJSIPには適用されません）。インストールされているフリーの楽曲は現在wav形式です。インストール時に（make menuselectを使用して）、利用可能なMOHファイル形式を選択できます。新しいMOHファイルを追加したい場合は、必要な形式で提供する必要があります。例：

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

ダイアルプランでは、以下の例を使用してMOHを聞くことができます：

```
Exten=>100,1,SetMusicOnHold(default)
Exten=>100,2,Dial(DAHDI/2)
```

MOHをテストするためにextensions.confファイルを構成するには：

```
[local]
exten => 6601,1,WaitMusicOnHold(30)
```

## アプリケーションマップ

アプリケーションマップを使用すると、features.confファイルの`[applicationmap]`セクションを使用して新しい機能を追加できます。コールセンターで応答している顧客のタイプを識別する必要があるとします。顧客タイプごとにアプリケーションマップを作成し、タイプごとの応答済み顧客数をカウントすることができます。

## クイズ

1. 通話パークについて正しい記述はどれですか？
   - A. デフォルトでは、内線800が通話パークに使用されます。
   - B. デスクから離れているときに電話を受けた場合、パークすることができます。システムがパークスロットをアナウンスし、どの電話機からでもそのスロットをダイヤルして通話を復帰できます。
   - C. デフォルトでは、700で通話をパークし、通話は701–720のスロットにパークされます。
   - D. パークされた通話を復帰するには700をダイヤルします。
2. 通話ピックアップ機能を使用するには、すべての内線が同じ___にある必要があります。DAHDIチャネルの場合、これは___ファイルで設定されます。
3. 通話を転送する際、転送先を事前に確認しない___転送と、完了前に転送先と話をする___転送を選択できます。
4. 相談転送（attended transfer）を行うには___シーケンスを使用し、ブラインド転送には___を使用します。
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Asterisk 22で会議通話をホストするには、___アプリケーションを使用します。
6. ConfBridgeにおいて、参加者に管理者権限（キック、他者のミュート、部屋のロック）を付与するには、ユーザープロファイル（`confbridge.conf`）で___を設定します：
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. 保留音に最適な形式はMP3です。なぜなら、Asteriskサーバーでの処理負荷が非常に少ないからです。
   - A. 正
   - B. 誤
8. 特定のコールグループから通話をピックアップするには、一致する___グループに属している必要があります。
9. MixMonitor()アプリケーションまたはワンタッチ（automon）機能を使用して通話を録音できます。デフォルトでは、automonは___ DTMFシーケンスを使用します。
   - A. *1
   - B. *2
   - C. #3
   - D. #1
10. ConfBridgeにおいて、参加者をミュート状態で参加させる（会議を聞くことはできるが、ミュート解除されるまで話すことはできない）ユーザープロファイルオプション`confbridge.conf`はどれですか？
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**回答：** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — A · 10 — A
