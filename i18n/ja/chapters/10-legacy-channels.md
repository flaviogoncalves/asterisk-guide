# レガシーチャネル：アナログ、TDM、IAX2

2026年の純VoIPの世界において、本章で扱うチャネルタイプはますます希少なものとなっています。新規導入のほとんどはEthernet上のSIPトランクとPJSIPエンドポイントであり、テレフォニーハードウェアを一切使用しません。しかし、Asterisk 22は依然としてそれらのほとんどを完全にサポートしています。アナログ（FXO/FXS）およびデジタルTDM（E1/T1/ISDN PRI/BRI）の接続は、DAHDIを通じて提供されます。DAHDIは、かつてDigium社が開発したドライバスタックであり、同社は2018年にSangoma社によって買収されました。それ以前のZaptelドライバは、商標紛争を経て名称が変更されました。IAX2によるサーバー間接続は`chan_iax2`によって提供されます。これは現在も出荷・サポートされていますが、今日では完全にレガシーなプロトコルとなっています。本章では、**レガシーSIP**に関する資料もまとめています。古い`chan_sip`ドライバとその`sip.conf`設定はAsterisk 21で削除され、Asterisk 22には存在しません。これに加え、既存の`sip.conf`システムをPJSIPへ移行するための完全なガイドも記載しています。テレフォニーカードやIAX2トランクを使用せず、変換すべきレガシーな`sip.conf`も存在しない純粋なSIP環境で運用している場合は、本章を読み飛ばしても問題ありません。

## アナログチャネル（FXO/FXS）

> **[第2版注記]** 出版前に第2版用の前書きの日付とISBNを更新すること。

> **[第2版注記 — 導入環境]** Asterisk 22の時点でも、DAHDIおよびアナログテレフォニーカードは完全にサポートされており、DAHDIは現在のカーネルに対してもビルド可能です。しかし、新規導入の大部分は純粋なVoIP（SIPトランク、PJSIP）です。アナログ/TDMハードウェアは現在、レガシー環境、地方のPSTN接続、あるいは規制市場で見られるニッチな選択肢となっています。以下の内容は、そうしたシナリオにおいて依然として正確です。

公衆交換電話網（PSTN）に接続する方法はいくつかあります。最適な方法は、お住まいの地域で電話会社がどのような接続を提供しているかによって異なります。最も単純な方法は、家庭で使用しているようなアナログ回線を利用することです。本節では、Sangoma™（旧Digium™）およびXorcom™のアナログカードの設定方法を説明します。

### 目的

本章を読み終える頃には、以下のことができるようになっているはずです。

- 主要なテレフォニー用語と頭字語を認識する
- デジタル回線とアナログ回線を使用すべきタイミングを理解する
- FXSとFXOの違いを認識する
- AsteriskでFXSおよびFXOを設定する

### テレフォニーの基礎

ほとんどのアナログ実装では、チップ（tip）とリング（ring）と呼ばれる銅線のペアを使用します。ループが閉じると、電話機は電話交換機（または構内交換機であるPBX）から発信音（ダイヤルトーン）を受け取ります。最も頻繁に使用されるシグナリングはループスタートですが、他にもグランドスタートなど、いくつかの国で使用されているあまり一般的ではないシグナリングもあります。シグナリングには以下の3つのカテゴリがあります。

- 監視シグナリング
- アドレスシグナリング
- 情報シグナリング

#### 監視シグナリング

主な監視シグナリングには、オンフック、オフフック、リンギングがあります。オンフック – ユーザーが受話器を置くと、PBXは割り込みを行い、電流が流れないようにします。この状態をオンフックと呼びます。この位置では、リンガーのみがアクティブです。オフフック – 通話を開始する前に、電話機はオフフック状態に移行する必要があります。受話器を上げるとループが閉じ、ユーザーが発信しようとしていることがPBXに伝わります。この合図を受けると、PBXはダイヤルトーンを生成し、宛先アドレス（電話番号）を受け入れる準備ができたことをユーザーに知らせます。リンギング – ユーザーが別の電話機に発信すると、相手側に着信を知らせるための電圧がリンガーに送られます。シグナリングは国によって異なり、トーンも国ごとに異なります。Asteriskのトーンは、indications.confファイルを変更することで、お住まいの国に合わせてカスタマイズできます。例：

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### アドレスシグナリング

ダイヤルには2種類のシグナリングを使用できます。最初で最も一般的なものはデュアルトーン多重周波数（dtmf）であり、もう一つはパルスダイヤル（古い回転式電話機で使用）です。電話機にはダイヤル用のキーパッドがあり、各ボタンには高周波と低周波の2つの周波数が割り当てられています。dtmfシグナリングの場合、これらのトーンの組み合わせによって、どの数字が押されたかが示されます。MFC/R2は、dtmfとは異なる多重周波数トーンを使用します。

#### 情報シグナリング

情報シグナリングは、通話の進行状況やさまざまなイベントを示します。

- ダイヤルトーン
- 話中音（ビジートーン）
- リングバックトーン
- 輻輳（コンジェスチョン）
- 無効な番号
- 確認音

### PSTNインターフェース

古いPBXと同様に、Asterisk PBXをPSTNに接続する必要があることがよくあります。ここでは、その方法を説明します。通常、電話回線には3つの選択肢があります。

- アナログ：家庭や小規模ビジネスで最も一般的な形式で、通常は銅線のペアで提供されます。
- デジタル：多数の回線が必要な場合に使用されます。デジタル回線は通常、CSU/DSUまたは光マルチプレクサによって提供されます。エンドユーザー側のコネクタは通常RJ45です。国によっては、E1回線が2つの同軸BNCコネクタを使用して提供されることもあります。その場合、テレフォニーボードのRJ45ジャックに接続するためにバランが必要です。
- SIP：このオプションは近年開発されたものです。電話回線は、SIPシグナリング（VoIP）を使用したデータ接続で提供されます。Asteriskで使用するには良い選択肢であり、テレフォニーカードを購入する必要がありません。通話はEthernetポートに直接配信されます。もう一つの利点は、コーデックのトランスコーディングを回避することで、CPUリソースを解放できる可能性があることです。

### アナログFXS、FXO、およびE&Mインターフェース

いくつかのアナログインターフェースが利用可能です。電話網や他のPBXへの接続方法を学ぶには、これらのインターフェースの違いを理解することが不可欠です。ここでは、E&Mインターフェースを紹介します。現在Asteriskでは利用できず、多くのベンダーで製造中止になっていますが、この種のインターフェースを持つルーターやPBXを見かけることがあるため、何を取り扱っているのかを知っておくことは有益です。

#### Foreign eXchange (FX) インターフェース

FXインターフェースはアナログです。「Foreign eXchange」という用語は、PSTNの中央局（CO）へのアクセス回線に適用されます。Foreign eXchange Office (FXO)

![アナログ電話機（FXS）と電話会社の回線（FXO）の間に配置されたAsterisk：FXS側は電話機にダイヤルトーンとリンギングを提供し、FXO側は中央局からダイヤルトーンを引き出す。](../images/10-legacy-fig01.png)

FXOインターフェースは、中央局（CO）や他のPBXの内線に接続するために使用されます。PSTNから来る電話回線と直接通信します。もう一つの選択肢は、FXOインターフェースを既存のPBXに接続し、AsteriskとレガシーPBX間の通信を可能にすることです。AsteriskをPBXポートに接続し、VoIPを使用してリモート内線を提供することは、オフプレミス内線（OPX）と呼ばれることがよくあります。FXOインターフェースはダイヤルトーンを受け取ります。Foreign eXchange Station (FXS) FXSインターフェースは、アナログ電話機、モデム、またはファックスに給電します。FXSは、電話機にダイヤルトーンと電力を提供します。

#### トランクシグナリング

- ループスタート
- グランドスタート
- Kewlstart

Asteriskにおけるkewlstartシグナリングの使用は、ほぼデフォルトとなっています。Kewlstart自体はシグナリングではなく、相手側で何が起きているかを監視することで回路にインテリジェンスを追加するものです。Kewlstartはループスタートに基づいています。ほとんどの交換機はこの機能をサポートしておらず、切断通知を取得するために使用されます。

- ループスタート：ほとんどのアナログ回線で使用され、電話機が「オンフック」や「オフフック」を示し、交換機が「リング」や「ノーリング」を示すことを可能にします。これはおそらく、ほとんどの人が自宅で使用しているものです。この名前は、回線が常に開いているという事実に由来します。ループを閉じると、交換機がダイヤルトーンを提供します。着信は、開いたペア上の100Vのリンギング電圧によって通知されます。

![VoIPゲートウェイとして動作するAsterisk：FXOポートがレガシーPBXの内線に接続され、リモートのAsteriskがFXSポートを介してIP経由でアナログ電話機にその回線を提供する（オフプレミス内線、またはOPX）。](../images/10-legacy-fig02.png)

- グランドスタート：ループスタートに似ています。発信したい場合、回線の一方が短絡されます。交換機がこの状態を識別すると、開いたペアを介して電圧を反転させ、その後ループが閉じられます。その結果、回線は発信者に提供される前にまず占有されます。
- Kewlstart：回路にインテリジェンスを追加し、相手側の監視を可能にします。Kewlstartはループスタートの多くの利点を取り入れています。

### Asteriskテレフォニーチャネルの設定

テレフォニーインターフェースカードを設定するには、いくつかの手順が必要です。本章では、最も一般的な3つのシナリオを紹介します。

- FXSを使用したアナログ接続
- FXOを使用したアナログ接続
- FXSおよびFXOインターフェースを備えたAstribank™の接続

### 設定手順（両ケース共通）

Asterisk用のハードウェアを選択する前に、インストールおよび有効化する同時通話数、サービス、コーデックを考慮する必要があります。AsteriskはCPU負荷の高いアプリケーションであるため、Asterisk専用のマシンを推奨します。コンピュータ内にインストールできるインターフェースカードの数は、利用可能なスロットと割り込みの数によって制限されます。4ポートのカードを2枚挿すよりも、8つの音声インターフェースを持つカードを1枚挿す方が望ましいです。もう一つの選択肢は、Xorcom AstribankのようなUSBチャネルバンクを使用することです。最近では、一部のメーカー（CIANETなど）がTDMoEチャネルバンクの製造を開始しており、数十ものアナログインターフェースをより簡単に接続できるようになっています。

![Xorcom Astribank：19インチラックマウント型のUSBチャネルバンク。ホストのPCIスロットを消費することなく、数十のFXS/FXOポート（ここでは32ポートユニット）を提供する。](../images/10-legacy-fig03.png)

#### 例1：FXO 1つ、FXS 1つのインストール

この例では、1つのFXSモジュールと1つのFXOモジュールを備えたSangoma TDM400テレフォニーインターフェースカード（旧Digium TDM400として販売）を使用します。必要な手順は以下の通りです。

1. アナログカードのFXS、FXO、またはその両方をインストールする。
2. `/etc/dahdi/system.conf`（旧`/etc/zaptel.conf`）ファイルを構成する。
3. `dahdi_genconf`を使用して設定ファイルを生成する。
4. DAHDIインターフェース用のドライバをロードする。
5. `dahdi_test`を実行して割り込みの欠落を確認する。
6. `dahdi_cfg`を実行してドライバを設定する。
7. `chan_dahdi.conf`ファイルでDAHDIチャネルを設定し、Asteriskをロードする。

##### 手順1：TDM400ボードのインストール

TDM404PカードにはFXSおよびFXOモジュールが含まれています。FXS（S110M、緑）およびFXO（X100M、赤）モジュールを接続します。FXSモジュールを使用している場合は、Molexコネクタを使用してカードを電源に直接接続してください。ハードウェアの損傷を防ぐため、インターフェースカードを取り扱う前に静電気防止対策を行ってください。Sangoma（旧Digium）のアナログカードは、ハードウェアエコーキャンセレーションモジュールVPMADT032もサポートしています。

##### 手順2：dahdi_genconfによる設定の生成

設定に関する朗報は、DAHDIインターフェースを自動的に検出して設定を生成する新しいユーティリティ`dahdi_genconf`です。このユーティリティは2つのファイルを生成します。

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf`（`users`オプション付き）
- これらのファイルはすべて`chan_dahdi full`オプションを使用します

`dahdi_genconf`を実行する前に、`genconf_parameters`（しばしば`gen_parameters.conf`と呼ばれます）ファイルを構成することが重要です。

![Sangoma/Digium TDM404Pアナログカード：最大4つのFXSまたはFXOモジュールが番号付きポートに差し込まれる。オプションのハードウェアエコーキャンセレーションドーターカードと、FXSモジュール専用の12V電源コネクタを備える。](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

`genconf_parameters`ファイルを使用すると、設定をカスタマイズできます。アナログ回線にとって最も重要なパラメータは以下の通りです。

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

警告：少なくともチャネルのエコーキャンセレーションアルゴリズムを設定する必要があります。base_extenパラメータは、FXS内線の基本的なダイヤルプランを定義します。この場合、最初のFXSチャネルは内線番号4000を受け取り、2番目は4001を受け取ります。回線（context_phones）とトランク（context_lines）が作成されるコンテキストは非常に重要です。ファイルを生成した後、`/etc/asterisk/dahdi-channels.conf`ファイルを`/etc/asterisk/chan_dahdi.conf`ファイルにインクルードする必要があります。

```
#include dahdi-channels.conf
```

注：アナログシグナリングは少し紛らわしいです。常にカードの逆になります。FXSカードはFXOでシグナリングされ、FXOカードはFXSでシグナリングされます。Asteriskは、反対側にいるかのようにこれらのデバイスと通信します。

##### 手順3：カーネルドライバのロード

次に、chan_dahdiモジュールと関連するカードカーネルドライバをロードする必要があります。dahdi_hardwareを使用して、カードとドライバ名を検出します。例：

- カード ドライバ 説明
- TE410P wct4xxp 4xE1/T1-3.3V PCI
- TE405P wct4xxp 4xE1/T1-5V PCI
- TDM400P wctdm 4 FXS/FXO
- T100P wct1xxp 1 T1 E100P wctlxxp 1 E1 X100P wcfxo 1 FXO

ドライバをロードするコマンド：

```
modprobe dahdi
modprobe wctdm
```

##### 手順4：dahdi_testユーティリティの使用

重要なユーティリティはdahdi_testで、DAHDIカードの割り込み欠落を検証するために使用されます。音質の問題は、割り込みの競合に関連していることがよくあります。DAHDIカードが他のカードと割り込みを共有していないことを確認するには、次のコマンドを使用します。

```
#cat /proc/interrupts
```

DAHDIカードと共にコンパイルされたdahdi_testユーティリティを使用して、割り込み欠落の数を確認できます。99.987%を下回る数値は、問題が発生している可能性を示しています。

##### 手順5：dahdi_cfgユーティリティによるドライバの設定

DAHDIには、ドライバをロードするための特殊なシステムがあります。まず/etc/dahdi/system.confを設定し、次にdahdi_cfgを使用してそれらの設定をDAHDIドライバに適用します。この場合、dahdi_cfgはFXインターフェースのシグナリングを設定するために使用されます。結果を確認するには、コマンドに“-vvvvv”を付けて詳細表示にします。

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

チャネルが正常にロードされた場合、上記のような出力が表示されます。ユーザーはよくchan_dahdi.confのチャネル間のシグナリングを逆に設定してしまいます。これが発生すると、以下のようなメッセージが表示されます。

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

ハードウェアの設定が完了したら、Asteriskの設定に進むことができます。

##### 手順6：/etc/asterisk/chan_dahdi.confファイルの設定

奇妙に聞こえるかもしれませんが、/etc/dahdi/system.confを設定した後、カード自体は設定済みです。DAHDIは、ルーティングやSS7など、他の目的にも使用できます。Asteriskで使用するには、AsteriskのDAHDIチャネルを設定する必要があります。Asteriskのすべてのチャネルを定義する必要があります。SIP/PJSIPチャネルはpjsip.confで定義されます（注：chan_sipとsip.confはAsterisk 21で削除されました）。一方、TDMチャネルはchan_dahdi.confで定義されます。これにより、ダイヤルプランで使用される論理TDMチャネルが作成されます。

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### 設定オプション

chan_dahdi.confファイルでは、いくつかのオプションが利用可能です。すべてのオプションを説明するのは退屈で非効率的です。代わりに、理解しやすいように主要なオプショングループに焦点を当てます。

#### 一般オプション（チャネル独立）

これらのオプションはどのチャネルでも機能します。context：着信コンテキストを定義します。

```
context=default
```

channel：チャネルまたはチャネル範囲を定義します。各チャネル定義は、宣言の前に定義されたオプションを継承します。チャネルは個別に、またはカンマ区切りで同じ行に指定できます。範囲は“-”を使用して定義できます。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group：チャネルをグループとして扱うことを可能にします。チャネル番号の代わりにグループ番号にダイヤルすると、利用可能な最初のチャネルが使用されます。チャネルが電話機の場合、グループにダイヤルするとすべての電話機が同時に鳴ります。カンマを使用すると、同じチャネルに対して複数のグループを指定できます。

```
group=1
group=3,5
```

language：国際化を有効にし、言語を設定します。この機能は、特定の言語のシステムメッセージを設定します。標準インストールでプロンプトが完全に利用可能な言語は英語のみです。musiconhold：保留音クラスを選択します。

#### 発信者番号（Caller ID）オプション

多くのcalleridオプションがあります。一部は無効にできますが、ほとんどはデフォルトで有効になっています。usecallerid：後続のチャネルのcallerid送信を有効または無効にします（Yes/No）。注：システムが応答する前に2回鳴る場合は、この機能を無効にしてみてください。即座に応答するはずです。hidecallerid：発信者番号を非表示にするかどうかを定義します（Yes/No）。callerid：特定のチャネルの発信者番号文字列を設定します。発信者はasreceivedで設定できます。これは主に、着信発信者番号を示すためにトランクインターフェースで使用されます。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid：キャッチホン中の発信者番号をサポートします。useincomingcalleridondahditransfer：転送時に着信発信者番号を使用します。

#### キャッチホン（Call Waiting）

AsteriskはFXSチャネルでのキャッチホンをサポートしています。誰かが内線にかけようとすると、ユーザーは待機音を受け取ります。キャッチホンを有効にするには：

```
callwaiting=yes
```

キャッチホンで発信者番号をサポートするには：

```
callwaitingcallerid=yes
```

#### 音質オプション

エコーキャンセレーションの調整は、半分は技術、半分は芸術です。これらのオプションは、DAHDIチャネルの音質に影響を与える特定のAsteriskパラメータを調整します。アナログインターフェースの音質を向上させるのに役立ちます。

#### fxotuneユーティリティ

fxotuneは、FXOモジュールの特定のパラメータを微調整するために使用されるユーティリティです。この微調整は、ハイブリッドによって引き起こされるインピーダンスの不一致を調整するために必要です。このユーティリティには3つの動作モードがあります。

- 検出（-i）：既存のFXOチャネルを検出して修正し、設定を```
fxotune.conf
```に保存します。
- ダンプモード（-d）：波形ファイルをfxotune_dump.valsに生成します。
- スタートアップモード（-s）：fxotune.confファイルを読み取り、FXOモジュールに適用します。

Asteriskを起動する前に、システムロード時にfxotune –s命令を挿入する必要があることを理解しておくことが重要です。

```
#modprobe dahdi
#modprobe wctdm
#fxotune-s
```

### エコーキャンセレーション

ほとんどのエコーキャンセレーションアルゴリズムは、受信信号の複数のコピーを生成し、それぞれを特定の時間だけ遅延させることで動作します。フィルタのタップ数は、キャンセルする必要があるエコー遅延のサイズを決定します。これらの遅延されたコピーは調整され、受信信号から差し引かれます。コツは、CPUサイクルを使いすぎずにエコーを除去するために必要な分だけ遅延信号を調整することです。ユーザーの観点からは、適切なエコーキャンセレーションアルゴリズムを選択することが重要です。デフォルトはMG2ですが、他にも2つのオプションがあります。Sangoma（旧Digium）のHigh Performance Echo Cancellation（HPEC）と、David Roweが開発したオープンソースのエコーキャンセレーション（OSLEC）です。

> **[第2版注記]** OSLECプロジェクトページ（http://www.rowetel.com/ucasterisk/oslec.html）は最新ではない可能性があります。参照する前に、最新のカーネルでの可用性とカーネル統合ステータスを確認してください。エコーキャンセレーションアルゴリズムを変更するには、/etc/dahdi/system.confのecho_canパラメータを変更します。例：

```
echo_can=oslec
```

Asteriskのエコーキャンセレーションは、/etc/asterisk/chan-ファイルの3つのパラメータで制御されます。

```
dahdi.conf.
```

echocancel：エコーキャンセレーションを無効または有効にします。この機能は有効にしておくべきです。“yes”またはタップ数を受け入れます。説明：エコーキャンセリングはどのように機能しますか？ほとんどのエコーキャンセリングアルゴリズムは、受信信号の複数のコピーを生成し、それぞれを短い間隔で遅延させることで動作します。この小さな流れを「タップ」と呼びます。タップ数は、キャンセル可能なエコー遅延を決定します。これらのコピーは遅延、調整され、元の信号から差し引かれます。コツは、エコーを除去するために必要な分だけ遅延信号を正確に調整することです。echocancelwhenbridged：純粋なTDM通話中にエコーキャンセラーを有効または無効にします。これは通常必要ありません。rxgain：受信音量を上げるか下げるために受信ゲインを調整します（-100%〜100%）。txgain：送信音量を上げるか下げるために送信ゲインを調整します（-100%〜100%）。例：

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 課金オプション

これらのオプションは、通話詳細記録（CDR）データベースに通話情報が記録される方法を変更します。amaflags：CDRの分類に影響を与えるAMAフラグを設定します。以下の値を受け入れます。

- billing
- documentation
- omit
- default

accountcode：特定のチャネルのアカウントコードを設定します。英数字の値を含めることができます（通常は部門名やユーザー名）。

```
accountcode=finance
amaflags=billing
```

### 通話進行オプション

これらの項目は、通話の進行状況に関する情報を取得するために使用されます。公衆インターフェースでは、通話の進行状況を検出し、応答があったか話中であるかを判断するのに役立つ場合があります。話中検出は非常に実験的なものであり、特定のパラメータによって制御されます。

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

これらのパラメータ（上記）は、インターフェースが話中音を検出しようとするかどうか、検出成功のためにいくつのトーンが使用されるか、話中パターンが何であるかを指定します。話中検出は大部分が実験的であり、Makefileでいくつかの追加パラメータを変更できます。通話の応答を検出することは正確な課金に不可欠ですが、極性反転を使用して正確な応答時間を通知することが可能です。これは、通話料金を請求する予定がある場合や、比較のために正確な課金記録が必要な場合に重要です。通常、このサービスをリクエストするには電話会社に連絡する必要があります。

```
answeronpolarityswitch=yes
```

国によっては、極性反転を使用して通話の切断を検出することも可能です。

```
hanguponpolarityswitch=yes
```

#### 電話機用オプション

これらのオプションは、FXSインターフェースに接続された電話機に使用されます。DAHDIインターフェースに直接接続されたアナログ電話機に提供されるすべての機能は、Asteriskによって制御されます。Adsi（Analog Display Services Interface）：これは、チケット購入などのサービスを提供するために一部の電話会社が使用するテレコム標準のセットです。cancallforward：通話転送を有効または無効にします（*72で有効、*73で無効）。calleridcallwaiting：キャッチホン通知中に受信した発信者番号を有効にします（Yes/No）。immediate：即時モードでは、ダイヤルトーンを提供する代わりに、チャネルは定義されたコンテキストの「s」内線に即座にジャンプします。これはホットラインを作成するために使用されます。threewaycalling：三者間会議を有効または無効にします。mailbox：利用可能なボイスメールメッセージをユーザーに警告します。可聴信号または視覚インジケータ（電話機がこの機能をサポートしている場合）になります。引数はメールボックス番号です。callgroup：ダイヤルまたはピックアップ用の電話機グループ。pickupgroup：通話ピックアップ用の電話機グループ。

### 便利なDAHDI CLIコマンド

DAHDIチャネルがロードされた状態でAsteriskが実行されている場合、Asterisk CLIからチャネルステータスを検査できます。これらのコマンドはAsterisk 22でも現役です。

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDIチャネル形式

DAHDIチャネルは、ダイヤルプランで以下の形式を使用します。

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

例：

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
```

## デジタルチャネル（E1/T1/PRI / TDM）

> **[第2版注記]** Asterisk 22の時点でも、DAHDIとlibpriは完全にサポートされていますが、TDMデジタルトランク（E1/T1/ISDN PRI）は新規導入においてSIPトランクに置き換えられつつあります。本章は、TDM接続が必要な場合には完全に適用可能です。グリーンフィールド環境の読者は、同様のチャネル密度を得るためにSIPトランキング（第3章）を好むかもしれません。

デジタルチャネルは非常に一般的であるため、大規模な顧客に焦点を当てたい場合は、これらのチャネルの実装方法を学ぶ必要があります。チャネル数が多い場合（通常8以上）、T1/E1/J1などのデジタルインターフェースを使用するのが一般的です。T1は米国で非常に一般的であり、E1はヨーロッパで、J1は日本で一般的です。これらのタイプのチャネルは、T1チャネルあたり24、E1チャネルあたり30という優れた回路密度を可能にします。ラテンアメリカ、中国、アフリカでは、MFC/R2として知られるチャネル関連シグナリング（CAS）の一種を使用するのが一般的です。本章では、OpenR2ライブラリを使用してMFC/R2を実装する方法を検討します。米国およびヨーロッパでは、統合サービスデジタル網（ISDN）PRIが最も一般的なシグナリングです。本章では、ヨーロッパの中規模アプリケーションで非常に一般的なISDN基本インターフェース（BRI）についても説明します。本書のすべての例はDAHDIチャネルに集中しています。一部のカードは独自のチャネルを使用して実装されているため、特定のカードの設定方法についてはメーカーに確認してください。

### 目的

本章を読み終える頃には、以下のことができるようになっているはずです。

- デジタルテレフォニーで使用される主要な用語を認識する
- CASシグナリングとCCSシグナリングを区別する
- R2シグナリングとISDNシグナリングを区別する
- ISDNシグナリングでインターフェースを設定する
- R2シグナリングでインターフェースを設定する

### E1/T1デジタル回線

デジタル回線E1/T1は、多数のチャネルを実装する必要がある場合の選択肢です。単一のE1回路は30の同時通話を可能にし、直接着信（DID）、発信者番号（発信者識別）、高度なシグナリングなどの機能を持つことができます。E1/T1回線は、国によってツイストペア、光ファイバー、マイクロ波を使用して会社に届く場合があります。デジタル回線は、UTP、光ファイバー、またはマイクロ波を使用して会社に提供されます。物理回線を提供するためにモデムやマルチプレクサ（MUX）が使用されます。T1回線への接続は常にRJ45コネクタに基づいています。しかし、E1回線はBNCを使用して提供されることもあります。E1回線では特に、どのようなコネクタが提供されるかを事前に知っておくことが非常に重要です。通常、RJ45までのすべての機器は電話会社によって提供されます。

![E1/T1回路のプロビジョニング方法：電話会社は、UTP銅線（E1用のHDSLモデム、またはT1用の直接カード接続）、光マルチプレクサを介した光ファイバー、またはマイクロ波無線リンクを介してトランクを提供できる。](../images/10-legacy-fig05.png)

![UTPかBNCか？ほとんどのデジタルカードはRJ45（UTP）コネクタを使用するが、一部のE1回線はデュアルBNC同軸で提供される。その場合、同軸ペアをカードのRJ45ジャックに適応させるためにバランが必要となる。](../images/10-legacy-fig06.png)

#### 音声はどのようにビットに変換されるのか？

アナログ信号は1秒間に8,000回サンプリングされ、アナログ音声のデジタルバージョンを作成します。このエンコーディングはパルス符号変調（PCM）として知られています。米国と日本では、信号はμ-law（Asteriskではulawと表記）を使用してエンコードされます。世界の他の地域では、エンコーディングはa-lawです。

![パルス符号変調（PCM）：4kHzのアナログ音声信号は1秒間に8,000回サンプリング（ナイキスト）され、64Kbpsのデジタルビットストリームに符号化される。](../images/10-legacy-fig07.png)

#### 時分割多重化（TDM）

アナログ回線は、少数のチャネルが必要な場合に理にかなっています。時分割多重化（TDM）を使用すると、単一のデータ接続に複数のチャネルを詰め込むことができます。多数の回路が必要な場合、電話会社は通常、デジタルトランクを提供します。これは、音声がPCMを使用してデジタル形式で転送されるデータ回路です。各タイムスロットは、単一の音声チャネルを転送するために64Kbpsの帯域幅を使用します。

![E1およびT1における時分割多重化：E1フレームは2048Kbpsで32のタイムスロットを運ぶ（フレーム同期用にDS0 #0、シグナリング用にDS0 #16）、一方T1フレームは1544Kbpsで24のタイムスロットを運び、同期用に1ビット、シグナリング用にビット強奪スキームを使用する。](../images/10-legacy-fig08.png)

米国では、最も一般的なデジタルトランクはT1で、24の利用可能な回線があります。ヨーロッパとラテンアメリカでは、E1トランクに30の回線があります。一部の企業は、より少ないチャネルを持つフラクショナルT1/E1を提供しています。ビット強奪シグナリング（Robbed bit signaling）時々、T1トランクはシグナリングのために1ビットを借りるビット強奪スキームを使用します。T1トランクでは、データ/音声チャネルは各タイムスロットで56Kbpsで送信されます。お気づきの通り、ビット強奪を使用する場合、T1回路は同期とシグナリングのために2つのスロットを失うことはありません。

#### T1/E1回線符号

T1とE1は実際にはデータ回路であり、ビットが解釈される方法を決定するデータコーディングを持っています。E1の場合、最も一般的な回線符号はレイヤー1用にHDB3、レイヤー2用にCCSです。デジタルトランクの設定方法を知る最も簡単な方法は、電話会社にこの情報を問い合わせることです。/etc/dahdi/system.confファイルを設定するには、この情報が必要です。

#### T1/E1シグナリング

T1/E1回線は、以下のようなさまざまな種類のシグナリングを使用して提供される可能性があることを理解することが重要です。

- ビット強奪シグナリング付きT1
- ISDNシグナリング付きT1
- MFC/R2付きE1（CAS - チャネル関連シグナリング）
- ISDNシグナリング付きE1

ISDNはヨーロッパや米国でよく使用されます。これは1984年に国際電気通信連合（ITU）によって標準化されたデジタル音声ネットワークです。ISDNは2種類のチャネルを提供します。

- ベアラチャネル o 音声 o データ
- データチャネル o 帯域外シグナリング o LAPDシグナリング o Q.931

通常、ISDN回線は2つの物理的手段を使用して提供されます。

- 基本インターフェース（BRI） o 2B+Dとして知られる o 2つのベアラ（64K）チャネルと1つのデータ（16K）チャネル o 148Kbpsの銅線ペアを使用。
- 一次群インターフェース（PRI） o T1/E1トランクを使用して提供 o T1の場合は23B+D o E1の場合は30B+D

時々、E1回路はMFC/R2と呼ばれるCASシグナリングスキームを使用します。これはITUによってQ.421/Q441として知られる標準として定義されました。これはラテンアメリカやアジアで頻繁に見られます。これらの国のいくつかの電話会社は、MFC/R2のカスタマイズされたバリエーションを使用しています。したがって、動作させるには正しい国別バリエーションを知る必要があります。

### ISDN BRI

ISDN BRIシグナリングを使用するチャネルはヨーロッパで非常に人気があります。Asterisk用のほとんどのISDN BRIカードは、NTおよびTE機能を備えたS/Tインターフェースをサポートしています。TE（端末）接続は、電話会社やネットワーク終端（NT）として設定された他のPBXに接続するために使用されます。NTは、電話機やTEとして設定されたPBXを接続するために使用されます。ISDN BRIは2つのデータ/音声チャネルと1つのシグナリングチャネルを提供します。ISDN BRIカードは、Asterisk用のインターフェースカードのいくつかのベンダーから入手可能です。

### Asteriskサーバー用のテレフォニーカードの選択

Asteriskと互換性のあるデジタルカードのメーカーはいくつかあります。カードの選択は、以下の要因のいくつかに依存します。

#### データバス

PCにはいくつかの種類のバスがあります。サーバーに適したカードを持つことが非常に重要です。以下の概要は、最も頻繁に使用されるカードの概要です。

- 32ビットPCI 5V：デスクトップを含むほとんどのコンピュータで見られる o Sangoma（旧Digium）TE405、TE407、TE205、TE207、TE120、TE122、B410、TDM2400、TDM800、TDM410、およびTC400 o Sangoma A101、A102、およびA104
- 32/64ビットPCI 3.3V：基本的にサーバーで見られる o Sangoma（旧Digium）TE410、TE412、TE210、TE212、TE120、TE122、B410、TDM2400、TDM800、TDM410、およびTC400
- PCI Express：デスクトップとサーバーで見られる o Sangoma（旧Digium）TE420、TE220、TE121、AEX2400、およびAEX800 o Sangoma A101、A102、およびA104

> **[第2版注記]** Sangomaは2018年にDigiumを買収しました。Digiumブランドのカードは現在、Sangomaブランドで販売・サポートされています。一部の古いSKUは製造中止になっている可能性があるため、Sangomaのウェブサイト（www.sangoma.com）で現在のモデルの可用性を確認してください。
- MiniPCI：組み込みシステムで見られる o OpenVOX A100M(FXO)、B100M(ISDN BRI)、B200M(ISDN BRI)、およびB400M(ISDN BRI)
- USB 2.0：ほとんどの最新PCで見られる。USBベースのソリューションは、アナログおよびデジタルチャネルの高密度化を可能にします。このバスは480Mbpsをサポートし、各音声チャネルは64Kbpsを占有します。USBハブを使用すると、単一ポートで最大1000のアナログポートの密度を得ることが可能です。 o Xorcom Astribank（FXS、FXO、E1-ISDN、E1-R2）
- Ethernet：Ethernetの最大の利点は、カードを複数のサーバーで接続できることです。高可用性ソリューションは、通常これらのデバイスのコアアプリケーションです。このソリューションの強みは、空きPCIスロットのないサーバーやブレードサーバーを使用できることです。 o Redfone FoneBridge（最大4つのE1回路）

### ハードウェアエコーキャンセレーションの使用

ハードウェアエコーキャンセレーションは、ホストCPUの負荷を軽減します。単一のE1インターフェースを超えるカードの場合、ハードウェアエコーキャンセレーションはプロセッサの負担を軽減するのに役立ちます。OSLECのような新しい強化されたソフトウェアエコーキャンセラーは、ハードウェアエコーキャンセラーの必要性を減らしています。ハードウェアとソフトウェアのエコーキャンセラーのどちらを選択するかは、サーバーで利用可能な処理能力とE1回路の数を考慮する必要があります。エコーキャンセレーションプロセスは、OSLECを使用して128タップの振幅で音声チャネルあたり最大9MIPS（1秒あたりの百万命令）を使用する場合があります（参照：Xorcom Ltd.）。各命令に1つのCPUサイクルを考慮すると（プロセッサとソフトウェア実装自体に基づいて常に正しいとは限りませんが）、4つのE1に対して1.080GHzとなります。

#### シグナリングの種類

シグナリングの種類（T1 CAS、T1 PRI、E1 CAS R2、またはE1 CAS ISDNなど）を選択するのは簡単な作業ではありません。それは本当にお住まいの地域で何が利用可能で、どのような価格であるかに依存します。共通線シグナリング（CCS）は、チャネル関連シグナリング（CAS）よりも優れていることが多いです。しかし、利用できないこともよくあります。米国では、通常選択可能です。ほとんどの電話会社は一般ユーザーにT1 CASを、高度なユーザー（コールセンターなど）にT1 PRIを提供しているためです。ラテンアメリカではE1 CAS R2が普及していますが、一部の都市ではISDN PRIが利用可能です。

![DAHDIソフトウェアアーキテクチャ：Asteriskは`chan_dahdi`チャネルドライバと通信し、それがプロトコルライブラリlibpri（ISDN）、libopenr2（MFC/R2）、libss7（SS7）をロードする。これらは`/dev/dahdi`インターフェース、DAHDIカーネルドライバ、およびカード固有のインターフェースカーネルドライバの上に位置する。](../images/10-legacy-fig09.png)

R2を実装するには、Moises Silvaによって開発されたOpenR2として知られるライブラリ（www.libopenr2.org）をインストールし、インストール前にAsteriskにパッチを当てる必要があります。これは本章の後半で示す簡単な手順です。このライブラリはいくつかのテストに合格しており、私たちの顧客の数社で本番稼働しています。ISDNは、私の意見では、利用可能であれば常に最良の選択です。一部のプロバイダーは、電話会社間で利用可能なCCSシグナリングであるシグナリングシステム7（SS7）にアクセスできる場合があります。SS7には独自のソリューションとオープンソースのソリューションが利用可能です。ライブラリlibss7は、AsteriskでSS7をサポートするために使用されます。

### Asteriskテレフォニーチャネルの設定

テレフォニーインターフェースカードの設定には、いくつかの必要な手順が含まれます。本章では、最も一般的な3つのシナリオを紹介します。

- ISDN PRIを使用したデジタル接続
- ISDN BRIを使用したデジタル接続
- MFC/R2を使用したデジタル接続

DAHDIチャネルを設定するには2つの方法があります。1つ目は、すべてのパラメータを完全に制御して手動で設定することです。2つ目は、dahdi_genconfユーティリティを使用してカードを検出し、設定することです。

#### 自動検出と設定

DAHDI開発チームのおかげで、カードの自動検出と設定が可能になりました。手順1：設定を自動的に生成するには、dahdi_genconfユーティリティを使用します。これによりカードが検出され、/etc/dahdi/system.confおよびdahdi-channels.confファイルが生成されます。

```
dahdi_genconf
```

手順2：chan_dahdi.confファイルの最後の行に、dahdi-channels.confファイルをインクルードします。

```
#include dahdi_channels.conf
```

手順3：modulesファイル内のすべての未使用モジュールをコメントアウトするか、単に以下を使用します。

```
dahdi_genconf modules
```

#### 手動設定

もう一つのオプションは、インターフェースを手動で設定することです。以下に、DAHDIチャネルの設定例をいくつか示します。

##### 例#1 – ISDNを使用した2つのT1/E1チャネル

必要な手順：

1. TE205PまたはTE210Pのインストール
2. `/etc/dahdi/system.conf`ファイルの設定
3. DAHDIドライバのロード
4. `dahdi_test`ユーティリティ
5. `dahdi_cfg`ユーティリティ
6. `chan_dahdi.conf`ファイルの設定
7. Asteriskのロードとテスト

手順1：TE205Pのインストール。TE205Pをインストールする前に、TE205PカードとTE210Pカードの違いを理解することが重要です。TE210Pカードは、サーバーのマザーボードにしか見られない3.3ボルトで駆動する64ビットバスを使用します。このインターフェースカードを指定する場合は注意してください。ハードウェアが64ビット、3.3Vバスをサポートしていることを確認してください。TE205Pカードは、デスクトップコンピュータによく見られる5V PCIを使用します。この例では、1スパンカードに減らしたり、4スパンカードに拡張したりするのが容易であるため、2スパンのTE205Pインターフェースカードを選択しました。これらのカードは現在、Sangomaブランド（旧Digium）で販売されています。

![Sangoma/Digium TE205PデュアルスパンE1/T1カード：2つのRJ45ポートがデジタルトランクを受け入れ、オンボードジャンパ（E1/T1/J1セレクタ）が回線標準を設定する。](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

TDMデジタルカードの設定は、アナログカードの設定とは少し異なります。まず、ボードスパンを設定し、次にチャネルを設定する必要があります。スパンは、カードの認識順序に応じて順番に番号が付けられます。言い換えれば、複数のインターフェースカードがある場合、どのスパンがどれに属しているかを知ることは困難です。dahdi_hardwareを使用して、各スパンにどのハードウェアがインストールされているかを確認してください。例#1（2xT1 PRI）

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

例#2（2xE1 PRI）

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

例#3（4xBRI）

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

手順3：カーネルドライバのロード。dahdi_hardwareを使用して、インストールする必要があるドライバを確認します。

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

ロードするには以下を使用します：

```
modprobe dahdi
modprobe wct2xxp
```

手順4：dahdi_testを使用して、割り込みの欠落を確認します。DAHDIカードと共にコンパイルされたdahdi_testユーティリティを使用して、割り込み欠落の数を確認できます。99.987%を下回る数値は、問題が発生している可能性を示しています。dahdi_testは以下にあります。

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

手順5：dahdi_cfgユーティリティの使用。これは、1つのフラクショナルE1（15ポート）スパンと2つのFXOポートに対するdahdi_cfgの正しい出力です。

```
#./dahdi_cfg –vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

手順6：/etc/asterisk/chan_dahdi.confファイルへのDAHDIの設定。例#1（2xT1）

```
callerid=”John Doe”<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

例#2（2xE1）

```
callerid=”Flavio Eduardo” <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

例#3（4xBRI）

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

ポイント・ツー・マルチポイントBRIにはsignaling=bri_cpe_ptmpを使用してください。現在、BRIポイント・ツー・マルチポイントはNTモードではサポートされていません。

#### カーネルドライバのロード

ドライバを設定した後、サーバーを再起動するだけです。make configでDAHDIをインストールしている場合は、追加の作業は必要ありません。カーネルドライバは自動的にロードおよび設定されます。ただし、ドライバを手動でロードおよびアンロードすると便利な場合があります。例：

```
modprobe wct11xp
dahdi_cfg –vvvvv
```

最初のコマンドはドライバをロードし、2番目のdahdi_cfgは設定をカーネルドライバに適用します。

### トラブルシューティング

物事が最初からうまくいくとは限りません。DAHDIのトラブルシューティングのためのリソースをいくつか確認しましょう。手順1：カードがオペレーティングシステムによって認識されているか確認します。Sangoma/Digiumカードは通常、ISDNモデムとして認識されます。

```
lspci –v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

手順2：以下を使用して、カーネルドライバが正しくロードされているか確認します。

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

手順3：接続の物理層に関連するアラームのステータスを確認します。E1接続の物理層を検証するには、次のAsterisk CLIコマンドを使用できます。

```
dahdi show status
```

アラームはポートの問題を示します：赤色アラーム：リモート交換機との同期を維持できません。これは通常、回線符号やフレーミングの不一致などの物理的な問題です。黄色アラーム：リモート交換機が赤色アラーム状態であることを示します。これは、リモート交換機があなたの送信を受信していないことを示します。青色アラーム：すべてのタイムスロットでフレーミングされていないすべての1を受信します。dahdi_toolは現在青色アラームを検出しません。ループバック：ポートはローカルまたはリモートのループバック状態です。

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

手順4：Asteriskサーバー上のDAHDIの問題を検出するには、まず以下を使用してチャネルが認識されているか確認します。

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

手順5：ISDNレイヤー3（q.931とも呼ばれます）のステータスを確認します。`pri show spans`（すべてのスパンをリスト）または特定のスパンに対して`pri show span <n>`を使用して、ISDNレイヤー3がアップしているか確認できます。

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

設定されたすべてのPRIスパンのステータスを一度にリストするには、`pri show spans`（複数形）を使用します。

特定のチャネルを確認します。dahdi show channel x：

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1*CLI>
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x：すべてを確認しても問題がある場合は、priスパンのデバッグを開始します。このコマンドは、ISDN通話の詳細なデバッグを有効にします。何かが正しくないと思われる場合に重要なコマンドです。誤ってダイヤルされた数字やその他の問題を検出できます。以下に、成功した通話のデバッグ出力の例を示します。問題のない通話と比較する必要がある場合は、この例を参照してください。ヒントは、ISDN q.931メッセージのみを受け取るためにcore set verbose=0を使用することです。

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]fice*CLI>
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### chan_dahdi.confの設定オプション

chan_dahdi.confファイルでは、いくつかのオプションが利用可能です。すべてのオプションを説明するのは退屈で非効率的です。ここでは、より良い理解を提供するために利用可能な主要なオプショングループを詳述します。

#### 一般オプション（チャネル独立）

context：着信コンテキストを定義します。

```
context=default
```

channel：チャネルまたはチャネル範囲を定義します。各チャネル定義は、宣言の前に定義されたオプションを継承します。チャネルは個別に、またはカンマ区切りで同じ行に指定できます。範囲は“-”を使用して定義できます。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group：チャネルをグループとして扱うことを可能にします。チャネル番号の代わりにグループ番号にダイヤルすると、利用可能な最初のチャネルが使用されます。チャネルが電話機の場合、グループにダイヤルするとすべての電話機が同時に鳴ります。カンマを使用すると、同じチャネルに対して複数のグループを指定できます。

```
group=1
group=3,5
```

language：国際化を有効にし、言語を設定します。この機能は、特定の言語のシステムメッセージを設定します。標準インストールでプロンプトが完全に利用可能な言語は英語のみです。musiconhold：保留音クラスを選択します。

#### ISDNオプション

switchtype：使用されるPBXまたは交換機に依存します。ヨーロッパとラテンアメリカでは、EuroISDNが一般的です。

- 5ess：Lucent 5ESS
- euroisdn：EuroISDN
- national：National ISDN
- dms100：Nortel DMS100
- 4ess：AT&T 4ESS
- Qsig：Q.SIG

```
switchtype = EuroISDN
```

pridialplan：ダイヤルプランの指定が必要な一部の交換機で必要です。このオプションは多くの交換機で無視されます。有効なオプションはprivate、national、international、unknownです。

```
pridialplan = unknown
```

prilocaldialplan：一部の交換機で必要です。通常はunknownです。

```
prilocaldialplan = unknown
```

overlapdial：オーバーラップダイヤルは、接続が確立された後に数字を渡す場合に使用されます。ブロックモード番号付け（overlapdial=no）または数字モード（overlapdial=yes）を使用できます。ブロックモードはオペレーターによってよく使用されます。signaling：後続のチャネルのシグナリングタイプを設定します。これらのパラメータは、chan_dahdi.confファイルのパラメータに対応している必要があります。正しい選択は利用可能なチャネルに基づいています。ISDNの場合、5つのオプションを選択できます。

- pri_cpe：デバイスがCPEの場合に使用されます。クライアント、ユーザー、またはスレーブと呼ばれることもあります。これは最も単純で最も使用されるシグナリング形式です。時々、プライベートPBXに接続しようとすると、PBXもCPEとして設定されていることがよくあります。その場合、Asteriskではpri_netシグナリングを使用してください。
- pri_net：AsteriskがCPEとして設定されたプライベートPBXに接続されている場合に使用されます。シグナリングはホスト、マスター、またはネットワークと呼ばれることがよくあります。
- bri_cpe：AsteriskがISDN BRIトランクにCPEとして接続されている場合に使用されます。
- bri_net：Asteriskが端末（TE）として設定されたISDN電話機またはPBXに接続されている場合に使用されます。
- bri_cpe_ptmp：bri_cpeと同じですが、ポイント・ツー・マルチポイントアーキテクチャで使用されます。

#### CallerIDオプション

多くのCaller IDオプションが利用可能です。一部は無効にできますが、ほとんどはデフォルトで有効になっています。usecallerid：後続のチャネルのCaller ID送信を有効または無効にします（Yes/No）。注：システムが応答する前に2回鳴る場合は、即座に応答するようにこの機能を無効にしてみてください。hidecallerid：Caller IDを非表示にします（Yes/No）。calleridcallwaiting：キャッチホン通知中にCaller IDを受信することを有効にします（Yes/No）。callerid：特定のチャネルのCaller ID文字列を設定します。発信者は、Caller IDを転送するためにトランクインターフェースで“asreceived”に設定できます。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

注：ほとんどの電話会社は、正しい発信者番号を設定することを義務付けています。正しい発信者番号を渡さないと、電話会社経由でダイヤルアウトできない場合があります。一方で、発信者番号を設定しなくても着信は可能です。

#### 音質オプション

これらのオプションは、DAHDIチャネルの音質に影響を与える特定のAsteriskパラメータを調整します。echocancel：エコーキャンセレーションを無効または有効にします。この機能は有効にしておくべきです。“yes”またはタップ数を受け入れます。説明：エコーキャンセリングはどのように機能しますか？ほとんどのエコーキャンセリングアルゴリズムは、受信信号の複数のコピーを生成し、それぞれを短い間隔で遅延させることで動作します。この小さな流れを「タップ」と呼びます。タップ数は、キャンセル可能なエコー遅延を決定します。これらのコピーは遅延、調整され、元の信号から差し引かれます。コツは、エコーを除去するために必要な分だけ遅延信号を正確に調整することです。echocancelwhenbridged：純粋なTDM通話中にエコーキャンセラーを有効または無効にします。これは通常必要ありません。rxgain：受信音量を上げるか下げるために受信ゲインを調整します（-100%〜100%）。txgain：送信音量を上げるか下げるために送信ゲインを調整します（-100%〜100%）。例：

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 課金オプション

これらのオプションは、通話詳細記録（CDR）データベースに通話情報が記録される方法を変更します。amaflags：CDRの分類に影響を与えます。以下の値を受け入れます。

- billing
- documentation
- omit
- default

accountcode：特定のチャネルのアカウントコードを設定します。英数字の値を含めることができます（通常は部門名やユーザー名）。

```
accountcode=finance
amaflags=billing
```

### MFC/R2設定

MFC/R2は、ラテンアメリカ、中国、アフリカのいくつかの国、および一部のヨーロッパ諸国で使用されています。ISDNは優れており、お住まいの地域で利用可能な場合は優先されます。

#### 問題の理解

MFC/R2をシグナリングするために使用されるカードは、ISDNをシグナリングするために使用されるものと同じです。libopenR2（www.libopenr2.com）と呼ばれるライブラリを使用して、DAHDIチャネルでMFC/R2を使用することが可能です。このライブラリは、1.6.2より前のバージョンのAsteriskの一部ではありませんでした。

##### MFC/R2プロトコルの理解

MFC/R2プロトコルは、帯域内シグナリングと帯域外シグナリングを組み合わせたものです。アドレスシグナリングは一連のトーンを使用して帯域内で転送され、チャネル情報は帯域外シグナリングとしてタイムスロット16を介して送信されます。

**回線シグナリング（ITU-T Q.421）。** タイムスロット16では、各音声チャネルは4つのABCDビットを使用してその状態と通話制御をシグナリングします。ビットCとDはめったに使用されません。国によっては、課金（課金用のパルス課金）に使用される場合があります。通常の会話では、発信側と着信側の両方が機能しています。発信側からのシグナリングは順方向シグナリングと呼ばれ、着信側は逆方向シグナリングを使用します。順方向シグナリングをAfとBf、逆方向シグナリングをAbとBbと指定します。

| 状態 | ABCD順方向 | ABCD逆方向 |
| --- | --- | --- |
| アイドル/解放 | 1001 | 1001 |
| 捕捉 | 0001 | 1001 |
| 捕捉確認 | 0001 | 1101 |
| 応答 | 0001 | 0101 |
| クリアバック | 0001 | 1101 |
| クリアフォワード（クリアバック前） | 1001 | 0101 |
| クリアフォワード（切断確認） | 1001 | 1001 |
| ブロック | 1001 | 1101 |

MFC/R2はITUによって定義されました。残念ながら、いくつかの国は標準を独自のニーズに合わせてカスタマイズしました。その結果、国間で標準のバリエーションが生じました。

**レジスタ間信号（ITU-T Q.441）。** MFC/R2シグナリングは、2つのトーンの組み合わせを使用します。以下の表はITU標準を示しています。

信号グループI（順方向）：

| 説明 | 順方向信号 |
| --- | --- |
| 数字1 | I-1 |
| 数字2 | I-2 |
| 数字3 | I-3 |
| 数字4 | I-4 |
| 数字5 | I-5 |
| 数字6 | I-6 |
| 数字7 | I-7 |
| 数字8 | I-8 |
| 数字9 | I-9 |
| 数字0 | I-10 |
| 国コードインジケータ、発信側ハーフエコーサプレッサが必要 | I-11 |
| 国コードインジケータ、エコーサプレッサ不要 | I-12 |
| テスト通話インジケータ | I-13 |
| 国コードインジケータ、発信側ハーフエコーサプレッサ挿入済み | I-14 |
| 未使用 | I-15 |

信号グループII（順方向）：

| 説明 | 順方向信号 |
| --- | --- |
| 優先順位なしの加入者 | II-1 |
| 優先順位付きの加入者 | II-2 |
| 保守機器 | II-3 |
| 予備 | II-4 |
| オペレーター | II-5 |
| データ転送 | II-6 |
| 順方向転送機能なしの加入者またはオペレーター | II-7 |
| データ転送 | II-8 |
| 優先順位付きの加入者 | II-9 |
| 順方向転送機能付きのオペレーター | II-10 |
| 予備 | II-11 |
| 予備 | II-12 |
| 予備 | II-13 |
| 予備 | II-14 |
| 予備 | II-15 |

信号グループA（逆方向）：

| 説明 | 逆方向信号 |
| --- | --- |
| 次の数字を送信 (n+1) | A-1 |
| 最後から2番目の数字を送信 (n-1) | A-2 |
| アドレス完了、グループB信号の受信へ切り替え | A-3 |
| 国内ネットワークの輻輳 | A-4 |
| 発信者カテゴリを送信 | A-5 |
| アドレス完了、課金、通話条件の設定 | A-6 |
| 最後から3番目の数字を送信 (n-2) | A-7 |
| 最後から4番目の数字を送信 (n-3) | A-8 |
| 予備 | A-9 |
| 予備 | A-10 |
| 国コードインジケータを送信 | A-11 |
| 言語または識別数字を送信 | A-12 |
| 回線の性質を送信 | A-13 |
| エコーサプレッサの使用に関する情報を要求 | A-14 |
| 国際交換機またはその出力での輻輳 | A-15 |

信号グループB（逆方向）：

| 説明 | 逆方向信号 |
| --- | --- |
| 予備 | B-1 |
| 特別情報トーンを送信 | B-2 |
| 加入者回線話中 | B-3 |
| 輻輳（グループAからBへの切り替え後） | B-4 |
| 未割り当て番号 | B-5 |
| 加入者回線空き、課金 | B-6 |
| 加入者回線空き、課金なし | B-7 |
| 加入者回線故障 | B-8 |
| 予備 | B-9 |
| 予備 | B-10 |
| 予備 | B-11 |
| 予備 | B-12 |
| 予備 | B-13 |
| 予備 | B-14 |
| 予備 | B-15 |

#### MFC/R2シーケンス

以下のシーケンスは、Asteriskの内線からPSTNの端末への発信を示しています。PSTNは通話をドロップし、通信を終了します。

![Asteriskと電話会社間の完全なMFC/R2通話フロー：回線シグナリング（アイドル、捕捉、捕捉確認、応答、クリアバック、クリアフォワード）がタイムスロット16で交換され、ダイヤルされた数字と逆方向の「次の数字を送信」信号（グループI/A/B）が帯域内で移動し、可聴トーンが加入者に到達する。](../images/10-legacy-fig11.png)

### libopenr2ドライバの使用方法

Moises Silvaによって開始されたプロジェクトは、Steve Underwoodによって書かれたUnicallチャネルドライバに触発されました。OpenR2ライブラリは、現在Asteriskにとって最も安定したソフトウェアソリューションです。このソリューションにより、DAHDIと互換性のある任意のデジタルカードを使用できます。以前は、MFC/R2には独自のソリューションしか利用できませんでした。私が使用した中で最高のものの一つは、Khomp（www.khomp.com.br）によって提供されたものです。Asterisk 22では、コンパイル時にライブラリが存在する場合、libopenR2を介したMFC/R2サポートが組み込まれています。外部パッチは不要です。以下の手順は参照用の歴史的な手動インストールを示しています。最新のシステムでは、`./configure`を実行する前にディストリビューションのパッケージマネージャーから`libopenr2-dev`をインストールし、`make menuselect`で`chan_dahdi`を有効にします。

> **[第2版注記]** 第1版のパッチ適用済みAsterisk 1.4ツリーは時代遅れです。Asterisk 22では、MFC/R2サポートはメインソースツリーに統合されており、以下の手順は廃止された`svn.digium.com`ではなく現在のGitリポジトリを使用します。最終版に向けて、これらの歴史的なビルド手順を要約することを検討してください。

手順1：インストールしたいAsteriskのバージョンのパッチを確認します。

```
apt-get install git
```

手順2：パッチが適用された変更済みAsteriskコードをダウンロードします。

> **[第2版注記]** 元のAsterisk 1.4 SVNパッチツリーは、以下では現在のGitリポジトリに置き換えられています。Asterisk 22ではMFC/R2パッチは不要です（`chan_dahdi`はlibopenr2に対して直接R2サポートをビルドします）。したがって、必要なのはopenr2ライブラリと通常のAsteriskビルドだけです。

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

手順3：コンパイルとインストール。進める前にサーバーをバックアップしてください。

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

注：設定ファイルを上書きしないように「make samples」を実行しないでください。

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

1つのE1インターフェースを持つカードを持っていると仮定します。

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

手順5：dahdi_cfgコマンドを実行して、ドライバに変更を適用します。

```
dahdi_cfg –vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

手順5：chan_dahdi.confファイルを変更します。

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

手順6：extensions.confファイルのダイヤルプランを変更します。

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

注：一部の電話会社は、発信者番号なしの通話を受け付けません。オペレーターによって割り当てられたDID番号のいずれかに発信者番号を設定してください。国によっては、この手順は不要です。手順7：ソリューションをテストします。これで、from-internalコンテキストの内線から任意の番号にダイヤルし、コンソールを観察します。エラーが発生していないか確認してください。 -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### OpenR2のデバッグ

通話のエラーを検出するには、デバッグを有効にできます。これを行うには、以下の手順に従います。手順1：chan_dahdi.confファイルを編集し、設定に次の3行を追加します。

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

手順2：Asteriskサーバーを再起動します。手順3：通話をテストし、/var/log/asterisk/mfcr2/span1の通話ファイルを確認します。以下は通常の通話のトレースです。受信した通話と比較してください。

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### MFC/R2設定

オプションはchan_dahdi.confファイル内に文書化されています。最も重要なオプションのいくつかをここで詳述します。必須パラメータ：mfcr2_variant、mfcr2_max_ani、mfcr2_max_dnis。mfcr2_variant：国別バリエーション。

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani：要求するANI数字の最大量 mfcr2_max_dnis：要求するDNIS数字の最大量 mfcr2_get_ani_first：DNISの前にANIを取得するかどうか（一部の電話会社で必要） mfcr2_category：発信者カテゴリ。通話を開始する前に変数MFCR2_CATEGORYを設定できます mfcr2_logdir：通話ファイルを記録するディレクトリ（/var/log/asterisk/mfcr2/directory） mfcr2_call_files：通話を記録するかどうか

- mfcr2_logging：ログ値
- cas – 送受信用のABCDビット
- mf – 多重周波数トーン
- stack – チャネルおよびコンテキストスタックの詳細出力
- all – すべてのアクティビティ
- nothing – 何も記録しない

mfcr2_mfback_timeout：この値は言及に値します。携帯電話への通話や完了までに時間がかかる通話をしている場合、このパラメータがタイムアウトする可能性があるため、微調整のために変更されることがよくあります。通話が完了しない場合は、最初に変更すべきパラメータです。mfcr2_metering_pulse_timeout：パルスは、コストを示すために一部のR2バリエーションで使用されます mfcr2_allow_collect_calls：ブラジルでは、トーンII-8はコレクトコールを示すために使用されます。このパラメータはコレクトコールをブロックすることを可能にします。 mfcr2_double_answer：二重応答が必要な場合にコレクトコールを回避するためにも使用されます。double_answer=yesを使用すると、実際にコレクトコールをブロックします。 mfcr2_immediate_accept：グループB/II信号の使用をスキップし、直接受け入れ状態に進むことを可能にします。 mfcr2_forced_release：通話の解放をスピードアップすることを可能にします。ブラジルのバリエーションで機能します。

#### ANIとDNIS

自動番号識別（ANI）は発信者の番号です。ダイヤル番号識別サービス（DNIS）は、呼び出された番号、言い換えればダイヤルされた番号です。通話が着信すると、通常、最後の4つの数字が直接着信（DID）と呼ばれるプロセスでPBXに渡されます。ANI番号は実際には発信者番号です。ANIはダイヤル時に発信者の内線番号を持ち、DNISは通話先を含みます。これらのパラメータが正しく設定されていることが重要です。一部の交換機は最後の4桁のみを送信し、他の交換機は完全な番号を送信します。

### DAHDIチャネル形式

DAHDIチャネルは、ダイヤルプランで以下の形式を使用します。

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

例：

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
[g] – Group identifier
[c] – Answer confirmation; A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

## IAX2プロトコル

本章では、Inter-Asterisk eXchange（IAX）プロトコルについて、その強みと弱みを含めて学習します。トランクモードや2つのAsteriskサーバーの相互接続などの詳細もカバーされます。本書のすべての参照はIAXバージョン2に対応しています。IAXプロトコルは、音声とビデオのメディア転送とシグナリングを提供します。IAXは非常に革新的です。トランクモードで帯域幅を節約し、NATを通過する必要がある場合にSIPよりもはるかに単純です。IAXの主な用途は、現在ではAsteriskサーバー同士を相互接続することです。IAXは主に音声用に作成されましたが、ビデオやその他のマルチメディアストリームにも対応できます。IAXは、SIPやMGCPなどの他のVoIPプロトコルから着想を得ました。シグナリングとメディアに2つの別々のプロトコルを使用する代わりに、IAXはそれらを統合してユニークなプロトコルにしました。IAXはメディア転送にRTPを使用しません。代わりに、メディアを同じUDP接続に埋め込みます。

> **[第2版注記 — Asterisk 22でのステータス]** `chan_iax2`はAsterisk 22 LTSでも含まれており、完全にサポートされているため、本章のすべては有効です。しかし、IAX2は現在レガシープロトコルであり、新規導入は比較的少ないです。VoIP業界は、プロバイダトランキングとサーバー相互接続の両方で、SIP（Asterisk 22の`chan_pjsip`経由）に大きく収束しています。IAX2の主な残りのセールスポイントは、**シングルポートNATトラバーサル**です。すべてのシグナリングとメディアが単一のUDPポート（デフォルトで4569）を流れるため、SIP + RTPと比較してファイアウォールとNATの設定が大幅に簡素化されます。新しいAsterisk間トランクを構築していてNATが懸念事項でない場合は、PJSIPトランクが推奨される現代的なアプローチです。IAX2がここに残されているのは、依然として有効な選択肢であり、特にファイアウォールを介して1つのUDPポートしか開けない環境では有効であるためです。

### 目的

本章を読み終える頃には、以下のことができるようになっているはずです。

- IAXプロトコルの強みと弱みを特定する
- IAXプロトコルの使用シナリオを説明する
- IAXトランクモードの利点を説明する
- 電話機用にiax.confを設定する
- VoIPプロバイダへの接続用にiax.confを設定する
- Asterisk相互接続用にiax.confを設定する
- IAX認証を理解する

### IAX設計

IAX設計の主な目的は以下の通りです。

- メディア転送とシグナリングに必要な帯域幅を削減する
- NAT透過性を提供する
- ダイヤルプラン情報を送信できるようにする
- ページングとインターコムの効率的な使用をサポートする

IAXは、RTPを使用しないSIPに似たピア・ツー・ピアのシグナリングおよびメディアプロトコルです。基本的なアプローチは、2つのホスト間の単一のUDP接続上でマルチメディアストリームを多重化することです。このアプローチの最大の利点は、xDSLモデムで定期的に見られるNATを介した接続を通過する際の単純さです。IAXは単一のポート（デフォルトでUDP 4569）を使用し、次に15ビットのコール番号を使用してすべてのストリームを多重化します。IAXプロトコルは、SIPプロトコルと同様の登録および認証プロセスを使用します。プロトコルの説明は、http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt にあります。

![IAXプロトコルは、単一のUDPポート（デフォルトで4569）上で2つのエンドポイント間の多くの通話を多重化し、15ビットのコール番号を使用してストリームを分離する。これによりNATトラバーサルが単純化される。](../images/10-legacy-fig12.png)

### 帯域幅の使用

VoIPネットワークで使用される帯域幅は、いくつかの要因によって影響を受けます。コーデックとプロトコルヘッダーが最も重要です。IAXプロトコルには、単一のヘッダーを使用して複数の通話を多重化するトランクモードと呼ばれる驚くべき機能があります。Asterisk帯域幅計算機で遊んでみると、IAXトランクが複数の通話で最大80%のトラフィックを節約できることがわかります。

![IAXとSIPのオーバーヘッドの比較：2つのSIP/RTP通話は2つのパケットを必要とする（156バイトのオーバーヘッドで運ばれる40バイトのペイロード）、一方IAX2トランクモードは、多くのミニフレーム間で1つのIP/UDPヘッダーを共有することにより、単一のパケットで両方の通話を運ぶ（わずか66バイトのオーバーヘッドで40バイトのペイロード）。](../images/10-legacy-fig13.png)

### チャネル命名

ダイヤルプランでチャネルを指定する際にこれらの名前を使用するため、チャネル命名規則を理解することが重要です。アウトバウンドチャネルに使用されるIAXチャネル名の形式は以下の通りです。

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

<user> リモートピア上のUserID、またはiax.confで設定されたクライアント名 <secret> パスワード。あるいは、末尾の拡張子（.keyまたは.pub）なしのRSAキーのファイル名で、角括弧で囲まれたもの <peer> 接続先のサーバー名 <portno> 接続用のポート番号 <exten> リモートAsteriskサーバー内の内線 <context> リモートAsteriskサーバー内のコンテキスト <options> 利用可能な唯一のオプションは「自動応答を要求する」を意味する「a」

#### アウトバウンドチャネルの例：

アウトバウンドチャネルはAsteriskコンソールで見られます。IAX2/8590:secret@myserver/8590@default myserverの内線8590を呼び出します。8590:secretを名前/パスワードのペアとして使用します。

IAX2/iaxphone "iaxphone"を呼び出します IAX2/judy:[judyrsa]@somewhere.com judyをユーザー名として、認証にRSAキーを使用してsomewhere.comを呼び出します

#### 着信IAXチャネルの形式は以下の通りです：

着信チャネルはAsteriskコンソールで見られます。

```
IAX2/[<username>@]<host>]-<callno>
```

<username> 既知の場合のユーザー名 <host> 接続元のホスト <callno> ローカルコール番号 着信チャネルの例： IAX2[flavio@8.8.30.34]/10 IPアドレス8.8.30.34からのコール番号10、ユーザーとしてflavioを使用。 IAX2[8.8.30.50]/11 IPアドレス8.8.30.50からのコール番号11。

### IAXの使用

IAXはいくつかの方法で使用できます。本節では、以下を含むいくつかのシナリオでIAXを設定する方法を示します。

- IAXを使用したソフトフォンの接続
- IAXを使用したVoIPプロバイダへのIAXの接続
- IAXを使用した2つのサーバーの接続
- トランクモードでIAXを使用した2つのサーバーの接続
- IAX接続のデバッグ
- 認証にRSAペアキーを使用する

#### IAXを使用したソフトフォンの接続

Asteriskは、ATCOMやDigiumの古いATA（IAXyと呼ばれる）などのIAXベースのIP電話機、および依然としてIAX2プロトコルを実装しているソフトフォンをサポートしています。ソフトフォン、ATA、ハード電話機の手順は似ています。IAXデバイスを設定するには、/etc/asteriskのiax.confファイルを編集する必要があります。

```
directory.
```

例としてIAX2対応のソフトフォンを使用します。手順1：以下を使用して元のiax.confファイルのバックアップを作成します。

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

手順2：新しいiax.confファイルの編集を開始します：

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; 非常に重要なパラメータ、利用可能なコーデックを変更します

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

サンプルファイルのデフォルト（コメントアウトされていない）行を保持するようにしました。以下のパラメータが変更されました：

```
bandwidth=high
```

この行はコーデックの選択に影響します。high設定を使用すると、ulawキーワードで定義されるg.711のような高帯域幅かつ高品質のコーデックを選択できます。デフォルトのパラメータを保持すると、ulawを選択できません。その場合、Asteriskは以下の設定に対して「no codec available」というメッセージを表示します。

```
disallow=all
allow=ulaw
```

上記で説明したコマンドでは、すべてのコーデックを無効にし、ulawのみを有効にしました。LANでは、ulawはプロセッサ負荷が高くなく、CPUサイクルを節約できるため、ほとんどの人がulawの使用を好みます。より多くの帯域幅を使用しても、LANには通常100メガビットEthernetやギガビットがあるため、このコーデックが好まれます。WANやインターネットネットワークでは、通常ulawを無効にし、より良い帯域幅使用のために音声圧縮のために利用可能なCPUサイクルをトレードオフします。コーデックgsm、g729、ilbcも優れた圧縮率を提供します。

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

上記のコマンドでは、[2003]という名前のフレンドを定義しました。コンテキストはdefaultです（最初のラボでは混乱を避けるために常にdefaultコンテキストを使用します。このコンテキストは第9章で完全に説明されます）。「host=dynamic」行は、電話機のIPアドレスの動的登録を提供します。手順3：IAX2対応のソフトフォンをダウンロードしてインストールします。ラボ用に依然としてIAX2プロトコルをサポートしているソフトフォンならどれでも選択できます。手順4：クライアントでIAXアカウントを設定します（通常は*アカウントの追加* → IAX）。SipPulse SoftphoneはSIP専用であり、IAX2経由で登録できないことに注意してください。したがって、IAXテストには依然としてプロトコルをサポートしているクライアントが必要です。

手順5：IAXデバイスをテストするためにextensions.confファイルを構成します。

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

これで、第3章で作成したSIP電話機と、ラボで作成したIAX電話機の間でダイヤルできます。

#### IAXを使用したVoIPプロバイダへの接続

少数のVoIPプロバイダがIAXをサポートしています。IAXプロバイダを検索することで、簡単にIAXプロバイダを見つけることができます。IAXプロバイダを使用することは、IAXが多くの帯域幅を節約でき、NATを簡単に通過でき、RSAキーペアを使用して認証できるため、非常に理にかなっています。

![インターネット経由でIAXトランクを介してVoIPプロバイダに接続された顧客のAsterisk：単一のトランクがプロバイダとの間のすべての通話を運ぶ。](../images/10-legacy-fig14.png)

> **[第2版注記]** IAX対応の商用VoIPプロバイダの数は、Asterisk 16以降大幅に減少しました。ほとんどのプロバイダは現在、SIP/PJSIPトランクのみを提供しています。IAXプロバイダを選択する前に、彼らがIAXインフラストラクチャを積極的に維持していることを確認してください。新しいプロバイダ統合には、PJSIPトランクが推奨される代替手段です。

#### IAXを使用したプロバイダへの接続

手順1：お気に入りのプロバイダでアカウントを開設します。プロバイダは3つのものを提供します。

- 名前
- シークレット
- IPアドレスまたはホスト名
- RSA公開鍵

手順2：Asteriskをプロバイダに登録するようにiax.confファイルを構成します。ファイルの[general]セクションに以下の行を追加します。

```
[general]
register=>name:secret@hostname/2003
```

上記で説明した手順で、アカウントとパスワードを使用してプロバイダに登録しました。通話を受信すると、内線2003に転送されます。

```
[name]
```

- ; アカウント名または番号

```
type=peer
secret=secret
; Your password
host=hostname
```

上記で説明した手順で、ダイヤル目的のためにプロバイダに対応するピアを作成しました。

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

これはRSA認証に必要です。プロバイダからの公開鍵を使用すると、受信した通話が本当にプロバイダからのものであることを確認できます。他の誰かが同じパスを使用しようとしても、対応する秘密鍵を持っていないため、認証できません。手順3：接続を試みます。接続をテストするには、任意の番号にダイヤルします。一部のベンダーはエコーテストを提供しています。これを達成するには、extensions.confファイルを編集してください。

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Asterisk CLIに移動し、リロードを発行します。Asteriskがプロバイダに登録されているか確認するには、次のコマンドを使用します。

```
CLI>reload
CLI>iax2 show register
```

これで、Asteriskサーバーに接続されたソフトフォンで*98にダイヤルするだけです。

#### IAXトランクを介した2つのAsteriskサーバーの接続

1つのサーバーを別のサーバーに接続するのは非常に簡単です。IPアドレスはすでにわかっているため、登録する必要はありません。iax.confファイルでピアとユーザーを作成する必要があります。HQサイトのすべての内線は20で始まり、その後に2桁が続きます（例：2000）。ブランチでは、すべての内線は22で始まり、その後に2桁が続きます（例：2200）。トランクを使用します。この機能を有効にするには、DAHDIタイミングソースが必要です。手順1：ブランチサーバーのiax.confファイルを編集します。

![IAXトランクで接続された2つのAsteriskサーバー：HQサーバー（192.168.1.1、内線20xx）とブランチサーバー（192.168.1.2、内線22xx）は単一のIAXトランクを介して互いに到達する。両方のIPアドレスが固定で既知であるため、登録は不要。](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

手順2：ブランチサーバーのextensions.confファイルを構成します。

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

手順3：HQサーバーのiax.confファイルを構成します。

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

手順4：HQサーバーのextensions.confファイルを構成します。

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

手順5：HQサーバーの電話機2000からブランチサーバーの電話機2200への通話をテストします。

### IAX認証

次に、特定の要件ごとに最適な方法を選択できるように、実用的な観点からIAX認証プロセスを分析しましょう。

#### 着信接続

![着信通話のIAX認証決定フロー：Asteriskは、ユーザー名が提供されているか、セクションと一致するか、ソースIPが許可されているか、シークレット（プレーンテキスト、MD5、またはRSA）が一致するかによって分岐し、そのセクションのコンテキストとピアオプションで通話を受け入れるか、拒否する。](../images/10-legacy-fig16.png)

Asteriskが着信接続を受信すると、初期情報にはユーザー名（「username=」フィールドから）が含まれる場合と含まれない場合があります。着信接続にはIPアドレスもあり、Asteriskは認証にもそれを使用します。ユーザーが提供された場合、Asteriskは：1. iax.confでtype=user（またはユーザー名と一致するセクション名を持つtype=friend）のエントリを検索します。見つからない場合、Asteriskは接続を拒否します。2. 見つかったエントリにdeny/allow設定がある場合、発信者のIPアドレスを比較して、deny/allow句に応じて通話を受け入れるかどうかを判断します。3. プレーンテキスト、md5、またはRSAを使用してパスワード（シークレット）を確認します。4. 接続を受け入れ、iax.confファイルの「context=」行で指定されたコンテキストに通話を送信します。ユーザー名が提供されない場合、Asteriskは：1. iax.confファイルでシークレットが指定されていないtype=user（またはtype=friend）を含むエントリを検索します。deny/allow句も確認します。エントリが見つかった場合、接続は受け入れられ、セクション名がユーザー名として使用されます。2. iax.confファイルでシークレットまたはRSAキーが指定されているtype=user（またはtype=friend）を含むエントリを検索します。deny/allow句を確認します。エントリが見つかった場合、指定されたシークレットを使用して発信者を認証しようとします。一致すれば、接続を受け入れます。セクション名がユーザー名です。iax.confファイルに以下のエントリがあると仮定します：

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

以下のようにユーザー名が指定されている場合：

- guest
- iaxtel
- iax-gateway
- iax-friend

Asteriskは、iax.confファイルの対応するエントリのみを使用して通話を認証しようとします。他の名前が指定された場合、通話は拒否されます。ユーザーが指定されていない場合、Asteriskは接続をguestとして認証しようとします。しかし、guestが存在しない場合、一致するシークレットを持つ他の接続を試みます。言い換えれば、iax.confファイルにguestセクションがない場合、悪意のあるユーザーはユーザー名を指定しないことで一致するシークレットを推測しようとする可能性があります。IPアドレスのdeny/allow制限も適用されます。シークレットの推測を避ける良い方法は、RSA認証を使用することです。もう一つの方法は、呼び出しを許可するIPアドレスを制限することです。

#### IPアドレス制限

permit = <ipaddr>/<netmask> ルールは順次解釈され、すべて評価されます（この概念は、ルーターやファイアウォールで通常見られるACLとは異なります）。例#1 permit=0.0.0.0/0.0.0.0 deny=192.168.0.0/255.255.255.0 192.168.0.0/24ネットワークからのパケットを拒否します 例#2 deny=192.168.0.0/255.255.255.0 permit=0.0.0.0/0.0.0.0 任意のパケットを許可します。最後の命令が最初の命令を上書きします。

#### アウトバウンド接続

アウトバウンド接続は、以下の方法を使用して認証情報を取得します。

- dial()アプリケーションによって渡されるIAX2チャネル記述。
- iax.confファイルのtype=peerまたはtype=friendを持つエントリ。
- 両方の方法の組み合わせ。

#### RSAキーを使用した2つのAsteriskサーバーの接続

非対称RSAキーを使用して強力な認証でIAXを使用することが可能です。ソースコード（res_krypto.c）によると、Asteriskは弱いMD5の代わりにメッセージダイジェストにSHA-1アルゴリズムを使用したRSAキーを使用します。以下は、RSAキーを使用して2つのサーバーを設定するためのステップバイステップガイドです。

##### ブランチサーバーの設定

手順1：ブランチサーバーでRSAキーを生成します

```
astkeygen –n
```

尋ねられたら、キー名branchを使用します。Asteriskが再初期化されるたびにパスフレーズを渡すのを避けるために、パラメータ–nを使用しました。セキュリティを向上させたい場合は、–nを使用せず、asterisk -iでAsteriskを開始してください。手順2：キーを/var/lib/asterisk/keysディレクトリにコピーします

```
cp branch.* /var/lib/asterisk/keys
```

手順3：公開鍵をHQサーバーにコピーします

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

手順4：ブランチサーバーのiax.confファイルを編集します。

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

手順8：ブランチサーバーのextensions.confファイルを構成します

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### 本社サーバーの設定

手順1：HQサーバーでRSAキーを生成します

```
astkeygen –n
```

尋ねられたら、キー名hqを使用します。手順2：キーを/var/lib/asterisk/keysディレクトリにコピーします

```
cp hq.* /var/lib/asterisk/keys
```

手順3：公開鍵をBRANCHサーバーにコピーします

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

手順4：HQサーバーのiax.confファイルを構成します。

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

手順10：HQサーバーのextensions.confファイルを構成します。

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

手順11：HQサーバーの2000電話機からブランチサーバーの2200電話機への通話をテストします。

### iax.confファイルの設定

iax.confファイルにはいくつかのパラメータがあります。各パラメータを一つずつ議論するのは退屈で非効率的です。すべてのパラメータと説明はサンプルファイルにあります。wiki www.voip-info.org にはそれぞれに関する詳細情報があります。ここでは、generalセクション、ピア、ユーザーの設定のための最も重要なパラメータのいくつかを示します。

#### [General] セクション

サーバーアドレス bindport = <portnum> IAX UDPポートを設定します。デフォルトは4569です。 bindaddr = <ipaddr> Asteriskをすべてのインターフェースにバインドするには0.0.0.0を使用するか、特定のインターフェースのIPアドレスを指定します。 コーデック選択 bandwidth = [low|medium|high] High = すべてのコーデック Medium = ulawとalawを除くすべてのコーデック Low = 低帯域幅コーデック allow/disallow = コーデック選択の微調整 [alaw|ulaw|gsm|g.729|など]

### ジッターバッファ

ジッターはパケット間の遅延変動です。音声品質に影響を与える最も重要な要因です。ジッターバッファは、遅延変動を補償するために使用されます。ジッターを低くするためにレイテンシを犠牲にします。ジッターバッファと水タンクの間に類似点を作ることができます。どちらも不規則な間隔でパケットや水を受け取ることができますが、最終的には規則的な流れを提供します。

![水タンクとしてのジッターバッファ：パケットはネットワークから不規則に到着してバッファを満たし、バッファは滑らかな音声フローを生成するために一定の速度でそれらを放出する。バッファサイズ（ms単位）は、ジッターを低くするために少しのレイテンシをトレードオフする。過剰バッファ帯域は、ネットワーク条件の変化に応じてAsteriskがバッファを拡大または縮小できるようにする。](../images/10-legacy-fig17.png)

小さなジッター（20ms未満）は通常知覚できません。しかし、このレベルを超えるジッターは煩わしいものです。レイテンシまたは遅延は150ms未満に保つ必要があります。ジッターバッファを作成すると、より低いジッターのためにいくらかの遅延を犠牲にします。これは「遅延予算」として知られる概念です。これらのパラメータを使用してジッターバッファに影響を与えることができます：

- Jitterbuffer=<yes/no> – 有効または無効
- Dropcount=<number> - 過去2秒間に遅延させるべきフレームの最大量。推奨設定は3（ドロップされたフレームの1.5%）
- Maxjitterbuffer=<ms> - 通常100ms未満
- Maxexcessbuffer=<ms> - ネットワーク遅延が改善した場合、ジッターバッファが大きすぎる可能性があります。その結果、Asteriskはそれを減らそうとします。
- Minexcessbuffer=<ms> - 過剰バッファがこの値まで低下すると、Asteriskはバッファサイズを増やし始めます。

### フレームタグ付け

以下のパラメータは、サービスタイプフィールドのIPパケットをマークします。ルーターはこのタグを読み取り、トラフィックを優先順位付けできます。AsteriskはこのフィールドにDSCPコードを使用します（RFC 2474）。許可される値は、CS0、CS1、CS2、CS3、CS4、CS5、CS6、CS7、AF11、AF12、AF13、AF21、AF22、AF23、AF31、AF32、AF33、AF41、AF42、AF43、およびef（つまり、高速転送）です。

```
tos=ef
```

### IAX2暗号化

IAXは、AES（Advanced Encryption Standard）と呼ばれる対称鍵128ビットブロック暗号を使用した通話暗号化をサポートしています。IAXトランク間で暗号化を有効にするのは非常に簡単です。iax.confファイルで以下を使用します：

```
encryption=yes
```

暗号化を強制するには：

```
forceencryption=yes
```

古いバージョンとの互換性を保証するために、以下を使用してキーローテーションを無効にする必要がある場合があります：

```
keyrotate=no
```

### IAX2デバッグコマンド

以下は、Asteriskにとって最も重要なトラブルシューティングコンソールコマンドの一部です。

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

この出力を見て、通話の開始と終了を特定します。pokeパケットとpongパケットを使用して取得された遅延とジッター情報を観察します。これらのパケットは「iax2 show netstats」コマンドの出力を作成するのに役立ちます。

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

デバッグをオフにするには、以下を使用します：

```
vtsvoffice*CLI>iax2 no debug
```

### まとめ

本章では、IAXプロトコルの強みと弱みをレビューしました。ソフトフォンや2つのAsteriskサーバー間のトランクなど、いくつかのシナリオでIAXがどのように機能するかを実証しました。トランクモードでは、単一のパケットで複数の通話を運ぶことで帯域幅を節約できます。最後に、ステータスを確認し、プロトコルをデバッグするために使用できるコンソールコマンドを学習しました。

## レガシーSIP：chan_sipとsip.conf（Asterisk 21+で削除）

> **レガシー / 歴史的：** 本節のすべては、古い`chan_sip`ドライバとその`sip.conf`設定ファイルを使用しています。`chan_sip`はいくつかのリリースで非推奨となり、**Asterisk 21で削除されたため、Asterisk 22には存在しません**。以下の`sip.conf`の例は現在のシステムでは実行されません。これらは、レガシーな導入がどのように機能していたかを文書化し、移行を支援するためにのみここに残されています。これらを実行するための現代的でサポートされている方法については、『SIP & PJSIP in depth』章の「PJSIP: the SIP channel」セクションを参照してください。SIP**プロトコル**理論（メソッド、登録、プロキシ/リダイレクト、SDP、NATタイプ）はプロトコルレベルであり、その章に記載されています。以下は、削除された`chan_sip`**設定**のみです。

Asterisk 20までのレガシーシステムでは、SIPは`/etc/asterisk/sip.conf`で設定されていました。これは（`extensions.conf`に次いで）2番目に変更されることが多いファイルでした。以下のセクションでは、`chan_sip`がAsteriskをSIPプロバイダに接続する方法、SIPを使用して2つのAsteriskを接続する方法、ドメインサポート、プレゼンス、コーデック/DTMF/QoSオプション、認証、およびNATを示し、その後にすべてをPJSIPに移行するためのガイドが続きます。

### AsteriskをSIPプロバイダに接続する（sip.conf）

Asteriskは、SIP VoIPプロバイダへの接続によく使用されます。VoIPプロバイダは通常、従来のプロバイダよりも通話料金が安いです。VoIPプロバイダのもう一つの興味深く魅力的な点は、他の都市（外国でさえも）でDID番号を購入できる可能性です。これらは、電気通信にVoIPを使用する良い理由です。本節では、レガシーな`chan_sip`がAsteriskをVoIPプロバイダに接続する方法を学習します。AsteriskをSIPプロバイダに接続するには3つの手順が必要です。テストは、お気に入りのプロバイダでアカウントを確立することで実施できます。手順1：sip.confでSIPプロバイダに登録する SIPプロバイダに接続するには、プロバイダから以下の情報が必要です。

![インターネットまたはプライベートWANを介してVoIPサービスプロバイダに接続されたAsterisk、Asteriskサーバーに登録されたローカルSIP電話機](../images/07-sip-and-pjsip-fig07.png)

- ユーザー名
- シークレットとremotesecret（インバウンドリクエストの認証にはsecretを使用し、アウトバウンドリクエストにはremotesecretを使用）
- ホスト名
- ドメイン
- 許可されるコーデック

この設定により、プロバイダはAsteriskのIPアドレスを特定できます。以下のステートメントでは、ホスト名で定義されたSIPプロバイダに登録し、AsteriskのIPアドレスをプロバイダに通知するようにAsteriskに指示しています。このステートメントは、内線4100で通話を受信したいことを示しています。sip.confファイルの[general]セクションに、以下の行を入力します。

```
register=>name:secret@hostname/4100
```

手順2：sip.confで[peer]を構成する Asteriskのダイヤルを簡素化するために、目的のプロバイダに対してピアタイプのエントリを作成します。

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

手順3：ダイヤルプランでプロバイダへのルートを作成する プロバイダへの宛先ルートとして数字010を選択します。プロバイダ内で#610000にダイヤルするには、単に010610000にダイヤルします。

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)=”Flavio Gonçalves”)
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### プロバイダシナリオに固有のSIPオプション

以下の議論では、VoIPプロバイダへの接続のためにsip.confファイルで設定されたオプションの詳細を検討します。

```
register=>username:password@hostname/4100
```

sip.confファイルに登録された命令は、プロバイダへの登録に使用されます。登録トランザクションは、名前とシークレットで認証されます。スラッシュ（“/”）を使用して、着信通話の内線を指定できます。技術的に言えば、内線はSIPリクエストの「Contact」ヘッダーフィールドに配置されます。登録動作は特定のパラメータによって制御できます：

```
registertimeout=20
registerattempts=10
```

登録が成功したか確認するためのレガシーコンソールコマンドは`sip show registry`でした。Asterisk 22での同等のコマンドは`pjsip show registrations`（アウトバウンド登録）およびエンドポイントステータス用の`pjsip show endpoints`です。

「username」パラメータは認証ダイジェストで使用されます。ダイジェストは、ユーザー名、シークレット、レルムを使用して計算されます：

```
username=username
```

HostはVoIPプロバイダのアドレスまたは名前を定義します：

```
host=hostname
```

FromuserおよびFromdomainパラメータは、認証のために必要な場合があります。これらのパラメータはSIP Fromヘッダーフィールドで使用されます：

```
fromuser=username
fromdomain=hostname
```

VoIPプロバイダに接続する場合、資格情報が必要です。最初の招待の後、プロバイダは「407 Proxy Authentication Required」と呼ばれるメッセージを送信します。その後のINVITEメッセージで資格情報を提供します。着信通話の場合、Asteriskサーバーはプロバイダの資格情報を要求します。明らかに、プロバイダはAsteriskサーバーの有効な資格情報を持っていません。insecure=inviteを使用する場合、Asteriskに対してプロバイダに「407 Proxy Authentication Required」を送信しないように、また着信通話を受け入れるように指示しています。insecure=port, inviteを使用して、ポート番号を一致させずにIPアドレスに基づいてピアを一致させることもできます。

```
insecure=invite, port
```

### SIPを使用して2つのAsteriskサーバーを接続する（sip.conf）

SIPを使用して2つのAsteriskボックスを相互接続できます。この設定を進める前に、ダイヤルプランに注意を払うことが重要です。ユーザーは通常、最小限の労力で他のPBXを接続したいと考えています。ここでのアイデアは、他のPBXに接続するためだけに内線番号を使用することです。手順1：サーバーAのsip.confファイルを編集します：

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

手順2：サーバーBのsip.confファイルを編集します：

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![SIPを使用して2つのAsteriskサーバーを接続：サーバーA（内線4400/4401）とサーバーB（内線4500/4501）がSIPシグナリングを交換し、各PBXのユーザーが他方にダイヤルできるようにする](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

手順3：サーバーAのextensions.confファイルを編集します：

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

手順4：サーバーBのextensions.confファイルを編集します：

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asteriskドメインサポート（sip.conf）

SIPプロトコルはインターネットアーキテクチャに従います。SIPを設定する前に最初に行うことは、DNSサーバーを正しく設定することです。SIP環境では、任意のSIPプロキシに配置されたユーザーを呼び出すことができ、他のユーザーもSIP Uniform Resource Identifier（URI）を使用してあなたを呼び出すことができます。SIPのDNSサーバーを設定するには、DNSサーバーにSRVレコードを追加する必要があります。

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

DNSを設定した後、SIPユーザー、SIP電話機、または電話内線を指すURIを使用できます。SIP URIはメールアドレスに似ています（例：sip:chuck@yourpartnerdomain.com）。SIP URIを使用すると、あるSIP電話機から別のSIP電話機へ通話するのに電話番号は不要です。外部ユーザーにダイヤルするには、以下のようなステートメントを使用します。

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

特定のパラメータでドメイン動作を制御できます。

```
srvlookup=yes
```

このパラメータは、アウトバウンド通話でのDNS SRVルックアップを有効にします。このパラメータを使用すると、ドメインに基づいてSIP名を使用して通話をダイヤルできます。

```
allowguest=yes
```

このパラメータは、認証なしで外部招待を処理することを可能にします。generalセクションまたはドメインステートメントで定義されたコンテキスト内で通話を処理します。警告：generalセクションでPSTNへのアクセス権を持つコンテキストを定義した場合、外部ユーザーはあなたのPBX経由でPSTNにダイヤルできます。その場合、料金が発生します。generalセクションで定義されたコンテキストには、自分の内線のみを許可してください。

![ドメインによる他のSIPサーバーへの接続：youdomain.comとyourpartnerdomain.comがSIPシグナリングを交換し、leeやbruceのようなユーザーがSIP URIを使用してchuckやnorrisを呼び出せるようにする](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

ドメインコマンドを使用すると、Asterisk内で複数のドメインを処理できます。特定のドメインから通話が着信した場合、特定のコンテキストに誘導されます。

```
;autodomain=yes
```

このパラメータは、許可されたドメインにローカルIPとホスト名を含めます。

```
;allowexternaldomains=no
```

デフォルトはyesです。外部ドメインへの通話を許可しない場合は、行のコメントを外してください。

### SIP高度な設定（sip.conf）

本節では、プレゼンス、コーデック選択、DTMFオプション、QoSパケットマーキングなど、レガシーSIPチャネルの高度なパラメータについて説明します。**概念**（BLF/プレゼンス、コーデックネゴシエーション、DTMFモード、DSCPマーキング）はPJSIPに引き継がれますが、ここに示されている`sip.conf`パラメータ名はAsterisk 22には存在しません。PJSIPでは、DTMFモードはエンドポイント上の`dtmf_mode=`であり、コーデックは`allow=`/`disallow=`で設定されます。

#### SIPプレゼンス

SIPプレゼンスはAsteriskで部分的に実装されています。Asteriskは、チャネルの状態に応じてSUBSCRIBEやNOTIFYユーザーなどのリクエストをサポートしています。AsteriskはSIPメソッドPUBLISHをサポートしていません。言い換えれば、チャネルの状態（話中、アイドル、リンギング）を購読することはできますが、「離席中」や「着信拒否」などの情報を公開することはできません。プレゼンスの最も一般的なシナリオは、各内線とトランクのランプを備えたKSシステムの動作をシミュレートする話中ランプフィールド（BLF）です。プレゼンス用のSIPパラメータ：

- allowsubscribe=yes：SIPサブスクリプションメソッドを許可
- subscribecontext=sip_subscribers：ヒントを探すコンテキスト
- notifyring=yes：リング時にSIP NOTIFYを送信
- notifyhold=yes：保留時にSIP NOTIFYを送信
- counteronpeer（Asterisk 1.4.xでlimitonpeerから名前変更）：ピア側でのみカウンターを適用
- callcounter=yes：デバイスで通話カウンターを有効にする
- busylevel=1：デバイスを話中とみなすための通話数のしきい値

例：手順1：AsteriskでのSIPプレゼンスのテストはそれほど難しくありません。まず、sip.confファイルとextensions.confファイルを構成しましょう。

sip.confファイル内

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

手順2：次に、ソフトフォンがプレゼンスを使用するように構成します。SipPulse Softphoneの設定方法を示します。

- シーケンス：右クリック->SIPアカウント設定->プロパティ->プレゼンス
- プレゼンスモデルをピア・ツー・ピアからプレゼンスエージェントに変更します。これにより、ソフトフォンはSIPイベントのためにAsteriskを購読します。

手順3：他のソフトフォンに連絡先を追加します。この例では、SipPulse Softphoneはアカウント2000であるため、アカウント2001の連絡先を追加します。シーケンス：右パネルを開く（ソフトフォンのプレゼンスパネル）->連絡先をクリック->連絡先を追加。名前2001を入力。2001として表示し、「この連絡先の可用性を表示」ボックスをチェックすることを忘れないでください。

手順4：内線2001にダイヤルし、ソフトフォンの右パネルで電話機のステータスを確認します。コンソールコマンド`core show hints`を使用して、サーバーでプレゼンスステータスが変化するのを確認します（レガシーchan_sipでは、`sip show inuse`が各回線で何通の通話があるかを示していました）。Asterisk 22では、`pjsip show endpoints`を使用してエンドポイントとチャネルの状態を検査します。プレゼンス/BLFステータスはソフトフォンの連絡先またはBLFパネルに表示されます。表示方法はクライアントによって異なります。

#### コーデック設定

コーデック設定は単純で直接的です。[general]セクションまたはピア/ユーザーセクションでallowおよびdisallowという単語を設定できます。ベストプラクティスは、プロセッサ負荷の高いトランスコーディングを避けるためにコーデックを標準化することです。メッセージとプロンプトには同じコーデックを使用してください。

```
[general]
disallow=all
allow=g729
```

#### DTMFオプション

特定の機会に、ボイスメールや自動音声応答（IVR）などのアプリケーションに数字を渡します。DTMFを正しく渡すことが重要です。DTMFを渡す最も単純な方法はinbandと呼ばれます。sip.confファイルの[general]またはピア/ユーザーセクションで設定されます。dtmfmode=inbandを設定すると、DTMFトーンは音声チャネル内の音として生成されます。この方法の主な問題は、g729のようなコーデックを使用して音声チャネルを圧縮すると、音が歪み、DTMFトーンが正しく認識されないことです。dtmfmode=inbandを使用する予定がある場合は、g.711コーデック（ulawおよびalaw）を使用してください。

```
dtmfmode=inband
```

もう一つのアプローチはRFC2833を使用することです。これにより、RTPパケット内の名前付きイベントとしてDTMFトーンを渡すことができます。

```
dtmfmode=rfc2833
```

最後に、RTPパケットの代わりにSIPパケット内にDTMF数字を渡すことができます。この方法はRFC3265（シグナリングイベント）およびRFC2976で定義されています。

```
dtmfmode=info
```

バージョン1.2のリリース後、以下を使用することが可能です：

```
dtmfmode=auto
```

これはRFC2833の使用を試みます。それが不可能な場合は、帯域トーンを使用します。

#### サービス品質（QoS）マーキング設定

QoSは音声品質に責任を持つ一連の技術です。QoSは、帯域幅、レイテンシ、ジッターを削減するように実装されています。QoSはAsterisk自体ではなく、スイッチやルーターに実装されています。しかし、Asteriskはパケットを高速配信のためにマークすることでルーターやスイッチを支援できます。マーキングは、RFC 2474およびRFC2475で定義された差別化サービスコードポイント（DSCP）を使用して行われます。

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

バージョン1.4以降、シグナリング（SIP）、音声（RTP）、およびビデオ（RTP）に対して異なるコードを指定できます。

### SIP認証（sip.conf）

レガシー`chan_sip`がSIP通話を受信したとき、以下の図に記載されているルールに従いました。3つのパラメータがSIP認証で重要な役割を果たしました。Asterisk 22では、認証は代わりにPJSIP`auth`オブジェクト（`type=auth`、`auth_type=userpass`、`username=`、`password=`）で設定され、エンドポイントによって参照されます。IPアクセス制御は、エンドポイント上の`permit=`/`deny=`、または`acl`を介して行われます。

![レガシーchan_sip認証決定フロー：AsteriskはFromヘッダーをsip.confと照合し、一致するtype=user/peerセクションとMD5資格情報を試し、insecure=inviteまたはallowguestにフォールバックしてから通話を許可または拒否する](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

このパラメータは、対応するピアを持たないユーザーが名前とシークレットなしで認証できるかどうかを制御します。このパラメータについてはドメインサポートセクションで説明しました。

```
insecure=invite,port
```

insecure=inviteを使用する場合、Asteriskは「407 Proxy Authentication Required」メッセージを生成しません。このメッセージがないと、ユーザーは認証なしで通話できます。これはVoIPサービスプロバイダへの接続によく使用されます。VoIPサービスプロバイダからの通話は通常認証されません。

```
autocreatepeer=yes/no
```

このコマンドは、AsteriskがSIPプロキシに接続されている場合に使用されます。各通話に対して動的にピアを作成します。このオプションが有効な場合、任意のUACがAsteriskサーバーに接続できます。IP接続をSIPプロキシに制限することが重要です。SIPプロキシは、アクセス制御を処理します。ピア設定は、generalオプションおよびSIPパケットの「Contact」ヘッダーフィールドに基づいています。警告：Asteriskを完全に開くため、細心の注意を払って使用してください。

```
secret=secret, remotesecret=secret
```

このパラメータは認証用のシークレットを設定します。インバウンドリクエストにはsecretを使用し、アウトバウンドリクエストにはremotesecretを使用します。テキストファイルにシークレットを表示したくない場合は、md5secretを使用してシークレットの代わりにハッシュを含めることができます。MD5シークレットを生成するには、以下を使用できます：

```
echo –n “username:realm:secret” |md5sum
```

次に、以下のステートメントを使用します：

```
md5secret=0b0e5d467890....
```

警告：–nパラメータを使用することを忘れないでください。キャリッジリターンがmd5計算に使用されます。

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

上記のステートメントは、すべてのIPアドレスを拒否し、ローカルネットワーク（192.168.1.0/24）からのUACのみを許可します。

#### RTPオプション

いくつかのRTPパラメータを制御できます。

```
rtptimeout=60
```

これは、保留中でない場合に60秒以上RTPアクティビティがない通話を終了します。

```
rtpholdtimeout=120
```

これは、保留中でもRTPアクティビティがない通話を終了します（rtptimeoutより大きくする必要があります）。

### SIP NATトラバーサル（sip.conf）

NAT**理論**（4つのNATタイプ、Contactヘッダー問題、キープアライブ、サーバーを介したメディアの強制）はプロトコルレベルであり、『SIP & PJSIP in depth』章でカバーされています。ここに示されている`sip.conf`パラメータ（`nat=`、`qualify=`、`directmedia=`、`externaddr=`、`localnet=`）は**レガシーchan_sip**であり、Asterisk 21+で削除されました。PJSIPでは、これらはトランスポート上の`rewrite_contact=yes`、`force_rport=yes`、`rtp_symmetric=yes`、`direct_media=no`、`external_media_address`、`external_signaling_address`、`local_net=`、およびAOR上の`qualify_frequency=`などのトランスポート/エンドポイント設定にマップされます。

レガシーchan_sipでは、パラメータ`nat`には5つのオプションがありました：

- nat = no — RFC3581以外の特別なNAT処理を行わない
- nat = force_rport — rportパラメータがなくてもあったかのように振る舞う
- nat = comedia — SDPがどこに送信するように指示しているかに関係なく、Asteriskが受信したポートにメディアを送信する
- nat = auto_force_rport — AsteriskがNATを検出した場合にforce_rportオプションを設定する（デフォルト）
- nat = auto_comedia — AsteriskがNATを検出した場合にcomediaオプションを設定する

sip.confファイルに「nat=force_rport」ステートメントを配置すると、Asteriskに対してSIPヘッダーの「Contact」ヘッダーフィールドに含まれるアドレスを無視し、パケットのIPヘッダーにあるソースIPアドレスとポートを使用するように、またSDPヘッダーの内容を無視して受信したアドレスにメディアを送信するように指示しています。

```
nat=force_rport,comedia
```

NATマッピングを開いたままにする必要があります。NATがタイムアウトすると、AsteriskはUACに招待を送信できません。UACは通話を送信できますが、受信できません。以下のステートメントを使用してNATを開いたままにできます。

```
qualify=yes
```

QualifyはOPTIONSメソッドを使用して定期的にSIPパケットを送信し、NATを開いたままにするのに役立ちます。Qualifyは60秒ごとに、ホストに到達できない場合は10秒ごとにOPTIONSを送信します。ピアのレイテンシを確認するには「sip show peers」を使用できます。ユーザーのNATが対称タイプの場合、あるUACから別のUACにパケットを直接送信することはできません。その場合、以下を使用してAsterisk経由でRTPを強制する必要があります：

```
directmedia=no
```

#### NATの背後のAsterisk（sip.conf）

これまでのすべてのシナリオは、Asteriskサーバーが外部（有効な）インターネットアドレスを持っていると仮定しています。時々、AsteriskサーバーはNATを備えたファイアウォールの背後に実装されます。その場合、いくつかの追加設定が必要です。

![NATの背後のAsterisk：ファイアウォールがパブリックアドレス200.180.4.168を内部Asteriskサーバー（192.168.1.100）にマップし、UDP 5060上のSIPとrtp.confで定義されたRTP範囲UDP 10000–20000を転送する](../images/07-sip-and-pjsip-fig13.png)

手順1：UDPポート5060をAsteriskサーバーに静的にリダイレクトするようにファイアウォールを設定します。手順2：UDPポート10000から20000を静的にリダイレクトするようにファイアウォールを設定します。開いているポートの数を制限したい場合は、rtp.confファイルを編集してRTPポート範囲を変更できます。もう一つの方法は、SIPプロトコルをサポートするインテリジェントなファイアウォールを使用して、RTPポートを動的に開くことです。

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

手順3：Session Description Protocol（SDP）を含むSIPパケットのヘッダーフィールドに外部アドレスを含めるようにAsteriskを設定します。これは、sip.confファイルに以下の2つのステートメントを追加することで達成できます：

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

最初のパラメータexternaddrは、外部宛先のSIPヘッダー内に外部IPアドレスを含めるようにAsteriskに指示します。2番目のパラメータlocalnetは、Asteriskが外部アドレスと内部アドレスを区別できるようにします。オプションで、サーバー上でDHCPアドレスを持つダイナミックDNSを使用している場合はexternhostを使用できます。

### SIPダイヤル文字列（chan_sip）

以下に示す`SIP/...`ダイヤル文字列技術は、削除されたchan_sipドライバです。Asterisk 22では代わりに`PJSIP/...`技術を使用してください。例：`Dial(PJSIP/2000)`または`Dial(PJSIP/${EXTEN}@provider)`。形式と意味はそれ以外は類似しています。

異なるダイヤル文字列を使用してレガシーSIP宛先を呼び出すことができます：

```
SIP/peer
```

- ; sip.confで定義されたピアを持つ必要がある

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

例は以下の通りです：

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## レガシーchan_sipシステムからPJSIPへの移行

`chan_sip`はAsterisk 21で削除され、Asterisk 22には存在しないため、既存の`sip.conf`導入はPJSIPに移行する必要があります。最大の概念的なシフトは、単一の`sip.conf`、`[peer]`、または`[friend]`がいくつかのPJSIPオブジェクトに分割されることです。それぞれが`type=`を持ちます：**エンドポイント**（通話/コーデック/メディア設定）、1つ以上の**aor**オブジェクト（デバイスが到達可能な場所/登録）、**auth**オブジェクト（資格情報）、および共有**トランスポート**（リスニングソケット、NATアドレス）。以下の表は、最も一般的な概念をマップしています。

| レガシーsip.conf概念 | PJSIP相当（pjsip.conf） |
| --- | --- |
| `[peer]` / `[friend]`ブロック | `type=endpoint` + `type=aor` + `type=auth`（`auth=`および`aors=`を介して参照） |
| `type=friend` / `type=peer` / `type=user` | 単一の`type=endpoint`（PJSIPにはフレンド/ピア/ユーザーの区別がない） |
| `host=dynamic`（デバイス登録） | `max_contacts=1`を持つ`type=aor`；デバイスは連絡先を更新するためにREGISTERする |
| `host=<ip/hostname>`（静的） | 静的`contact=sip:host:port`を持つ`type=aor` |
| `register=>user:secret@host/ext`（アウトバウンド） | `type=registration`（`server_uri=`、`client_uri=`、`outbound_auth=`） |
| `secret=` / `username=` | `type=auth`、`auth_type=userpass`、`username=`、`password=` |
| `context=` | エンドポイント上の`context=` |
| `disallow=all` / `allow=ulaw` | エンドポイント上の`disallow=all` / `allow=ulaw`（同じ構文） |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733`（PJSIP） — また`inband`、`info`、`auto` |
| `directmedia=yes/no` | エンドポイント上の`direct_media=yes/no` |
| `nat=force_rport,comedia` | `force_rport=yes`、`rewrite_contact=yes`、`rtp_symmetric=yes`（エンドポイント） |
| `qualify=yes` | **aor**上の`qualify_frequency=`（秒） |
| `externaddr=` | **トランスポート**上の`external_media_address=`および`external_signaling_address=` |
| `localnet=` | **トランスポート**上の`local_net=` |
| `insecure=invite`（プロバイダ、認証なし） | `auth=`/`outbound_auth=`を省略し、`identify`（`type=identify`、`match=`）を使用 |
| `allowguest=yes` | `anonymous`エンドポイント + `allow_unauthenticated_options`（注意して使用） |
| `tos_sip` / `tos_audio` | エンドポイント上の`tos_audio` / `tos_video`（および`cos_audio` / `cos_video`） |

レガシー`sip.conf`で以下のように見えた登録内線は：

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

Asterisk 22の`pjsip.conf`では以下のようになります：

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### sip_to_pjsip.py変換スクリプト

Asteriskは、既存の`sip.conf`を読み取り、`pjsip.conf`を生成するヘルパースクリプト**`sip_to_pjsip.py`**を出荷しています。/etc/asteriskディレクトリで直接実行できます。このユーティリティはAsteriskソースツリーの`contrib/scripts/sip_to_pjsip/`にあります。ここで`${PATH_TO_ASTERISK_SOURCE}`はAsteriskソースファイルが見つかるパスです（通常は/usr/src/asterisk-22.x.y/）：

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

`--help`オプションで実行すると、そのオプションが表示されます：

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

また、オプションの位置引数も受け入れます — `[input-file [output-file]]`。デフォルトは現在のディレクトリの`sip.conf`と`pjsip.conf`です。

その出力を**出発点**として扱ってください。生成されたすべてのオブジェクト、特にトランスポート、NAT設定、コーデックリストをレビューし、本番環境に移行する前に徹底的にテストしてください。

VoIP School Blackbelt（voip.school）のコンパニオンラボでsip.confを移行しましょう。

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.api4com.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.api4com.com
fromuser=1020
fromdomain=sip.api4com.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.api4com.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.api4com.com
client_uri = sip:1020@sip.api4com.com:5600
server_uri = sip:sip.api4com.com:5600
[auth_reg_sip.api4com.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.api4com.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.api4com.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.api4com.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

変換は問題ないようですが、qualify=yesのような一部の要素は直接マップできないことがわかります。修正するには、aorセクションに秒単位でtimeを指定するqualify_frequency=timeコマンドを追加する必要があります。以下の例を参照してください。

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

完全なPJSIP設定は『SIP & PJSIP in depth』章でカバーされており、docs.asterisk.orgの公式ドキュメントにはチャネルの完全なカバレッジがあります。voip.schoolのコンパニオンラボでは、ラボ5で学んだことを練習できます。

## クイズ

1. 2つのアナログForeign eXchangeインターフェースに関して、正しいステートメントにマークしてください（複数選択可）：
   - A. FXOインターフェースは公衆交換電話網（PSTN）中央局に接続し、そこからダイヤルトーンを引き出す。
   - B. FXSインターフェースは標準のアナログ電話機、ファックス、またはモデムにダイヤルトーンとリンギング電力を提供する。
   - C. FXSインターフェースはAsteriskを電話会社の回線に接続する正しい方法である。
   - D. FXOインターフェースはレガシーPBXの内線ポートに接続することもできる。
2. アナログ回線の監視シグナリングには以下のどれが含まれますか（複数選択可）？
   - A. オンフック
   - B. オフフック
   - C. リンギング
   - D. DTMF
3. DAHDIアナログカードのエコー、ポップ音、ノイズは、最も頻繁に何によって引き起こされますか：
   - A. Asteriskのコンパイル方法
   - B. PCI割り込みの競合
   - C. 不適切なSIPコーデック
   - D. ダイヤルプランの欠落
4. アナログチャネルでの正確な課金のために、相手側がいつ応答したかを正確に検出する必要があります。これを行うためにAsteriskで有効化し（電話会社にリクエストする）機能は何ですか？
   - A. 応答反転
   - B. 課金反転
   - C. 極性反転
   - D. ダイヤルトーン生成
5. DAHDIハードウェアはAsteriskから独立しています。物理カードは`/etc/dahdi/system.conf`で設定され、`chan_dahdi.conf`はハードウェア自体ではなくAsteriskチャネルを定義します。
   - A. 真
   - B. 偽
6. デジタルトランクの容量とシグナリングに関して、正しいステートメントにマークしてください（複数選択可）：
   - A. E1トランクは30の音声チャネルを運び、T1トランクは24を運ぶ。
   - B. ISDN PRIはE1で30B+D、T1で23B+Dを使用する。
   - C. ISDNはCCSシグナリングの例であり、MFC/R2はCASシグナリングの例である。
   - D. T1はヨーロッパとラテンアメリカで最も一般的に使用されるデジタルトランクである。
7. DAHDIカードを自動的に検出し、`/etc/dahdi/system.conf`と`dahdi-channels.conf`を生成するユーティリティは何ですか？
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. レガシー`sip.conf` `[friend]`をPJSIPに移行する場合、単一のブロックをいくつかのオブジェクトに分割する必要があります。登録`[friend]`を置き換えるPJSIP`type=`オブジェクトのセットはどれですか？
   - A. `type=endpoint`、`type=aor`、および`type=auth`
   - B. `type=peer`および`type=user`
   - C. `type=sip`のみ
   - D. `type=channel`および`type=device`
9. 2つのAsteriskサーバー間でIAX2トランクモードを使用する主な実用的な利点は何ですか？
   - A. デフォルトですべての通話をTLSで暗号化する
   - B. 単一のヘッダーの下で複数の通話を運び、帯域幅を節約する
   - C. コーデックの必要性を排除する
   - D. 品質向上のために通話ごとに個別のUDPポートを割り当てる
10. RSAキーはIAX2認証に使用できます。どのキーを秘密にしておく必要があり、どれを他のサーバーに渡しますか？
    - A. 公開鍵を秘密にし、秘密鍵を共有する
    - B. 秘密鍵を秘密にし、公開鍵を共有する
    - C. 共有鍵を秘密にし、秘密鍵を共有する
    - D. 両方のキーを共有する必要がある

**回答：** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
