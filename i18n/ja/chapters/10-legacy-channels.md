# Legacy channels: analog, TDM & IAX2

2026年の純粋なVoIP環境では、本章で扱うチャンネルタイプはますます稀少になっています。新規導入の多くはイーサネット上のSIPトランクやPJSIPエンドポイントであり、電話機器は一切使用されません。Asterisk 22 はそれでもなお、これらの多くを完全にサポートしています。アナログ（FXO/FXS）およびデジタルTDM（E1/T1/ISDN PRI/BRI）接続は、Digium が開発し、2018年に Sangoma が買収した DAHDI ドライバスタックを通じて提供されます。これは、以前の Zaptel ドライバが商標紛争の結果名前が変更されたものです。サーバ間接続の IAX2 は`chan_iax2`によって提供されており、現在も配布・サポートされていますが、完全にレガシープロトコルとなっています。

本章では **legacy SIP** に関する資料もまとめています。古い`chan_sip`ドライバとその`sip.conf`設定（Asterisk 21 で削除、Asterisk 22 では完全に廃止）に加え、既存の`sip.conf`システムを PJSIP に移行するための完全ガイドを掲載しています。もし PJSIP だけで構成された純粋な SIP 環境で、電話カードや IAX2 トランク、変換すべきレガシー`sip.conf`が存在しない場合は、本章をスキップして問題ありません。

## Objectives

この章の終わりまでに、次のことができるようになります。

- DAHDI を介した FXO/FXS インターフェースでアナログ回線や電話機を Asterisk に接続すること；
- デジタル TDM 接続（E1/T1、ISDN PRI/BRI）を認識し、その設定方法を理解すること；
- サーバー間トランク用に IAX2（`chan_iax2`）を設定し、なぜ現在はレガシーと見なされているかを理解すること；
- 廃止された `chan_sip` ドライバと、まだ遭遇する可能性のある `sip.conf` 構文を特定すること；
- 既存の `chan_sip`/`sip.conf` システムを PJSIP に移行すること。

## アナログチャネル (FXO/FXS)

Asterisk 22 以降も、DAHDI とアナログ電話カードは完全にサポートされており、DAHDI は現在のカーネルに対してビルドされ続けています。新規導入の大半は依然として純粋な VoIP（SIP トランク、PJSIP）であるため、アナログ/TDM ハードウェアはニッチな選択肢となっており、主にレガシー環境、農村部の PSTN 接続、または規制された市場で見られます。以下の内容はそれらのシナリオにも当てはまります。

公衆交換電話網 (PSTN) に接続する方法はいくつかあります。最適な方法は、電話会社が地域でどのように接続を提供しているかによります。最も簡単な方法は、家庭で使用しているのと同様のアナログ回線を利用することです。本節では、Sangoma™（旧 Digium™）および Xorcom™ のアナログカードの設定方法を示します。

### 目的

本章の終わりまでに、以下ができるようになります。

- 主な電話用語と略語を認識できること；
- デジタル回路とアナログ回路の使い分けを理解できること；
- FXS と FXO の違いを認識できること；そして
- Asterisk を FXS と FXO 用に設定できること。

### 電話の基礎

ほとんどのアナログ実装は、tip と ring と呼ばれる 2 本の銅線ペアを使用します。ループが閉じられると、電話は通信交換機（またはプライベート PBX）からダイヤルトーンを受け取ります。最も頻繁に使用される信号方式はループスタートで、他にもいくつかの国で使用されるグラウンドスタートなど、あまり一般的でない方式があります。信号方式は次の 3 つに分類されます。

- 監視信号
- アドレス信号
- 情報信号

#### 監視信号

主な監視信号は on-hook、off-hook、ringing です。

- **On-Hook** – ユーザーが電話をフックに置くと、PBX は回路を遮断し電流が流れないようにします。この状態の回路は on-hook と呼ばれます。この位置では、着信音だけが作動します。
- **Off-Hook** – 電話をかけ始める前に、電話は off-hook 状態に移行する必要があります。受話器をフックから外すとループが閉じ、ユーザーが通話を開始しようとしていることを PBX に通知します。この通知を受け取ると、PBX はダイヤルトーンを生成し、ユーザーが宛先アドレス（電話番号）を入力できる状態であることを示します。
- **Ringing** – ユーザーが別の電話に呼び出すと、着信音用の電圧が生成され、相手に呼び出しがあることを警告します。信号方式は国によって異なり、国ごとに異なるトーンが使用されます。

`indications.conf` ファイルを変更することで、国ごとの Asterisk トーンをカスタマイズできます。例:

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

You can use two kinds of signaling for dialing. The first and most common is dual tone multi-frequency (dtmf) while the other is pulse dialing (used in old rotary dial phones). Phones have a keypad for dialing, and each button is associated with two frequencies: one high and one low. In the case of dtmf signaling, the combination of these tones indicates what digit is being pressed. MFC/R2 uses a multi-frequency tone different from dtmf.

#### Information signaling

---

情報シグナリングは、通話の進行状況やさまざまなイベントを示します。

- ダイヤルトーン
- ビジートーン
- リングバック
- 混雑
- 無効な番号
- 確認トーン

### PSTN インターフェース

As in the case of old PBXs, it is often required to connect the Asterisk PBX to the PSTN. Here we’ll show you how to do it. Usually you have three options for telephone lines.

- Analog: ホームや小規模ビジネスで最も一般的な形態で、通常は金属製のツイストペア銅線で提供されます。  
- Digital: 多数の回線が必要な場合に使用されます。デジタル回線は通常、CSU/DSU またはファイバーマルチプレクサで提供されます。エンドユーザー側のコネクタは通常 RJ45 です。国によっては、E1 回線が 2 本の同軸 BNC コネクタで提供されることがあります。その場合、RJ45 ジャックとテレフォニー ボードを接続するためにバルーンが必要になります。  
- SIP: このオプションは最近開発されました。電話回線は SIP シグナリング（VoIP）を使用したデータ接続で提供されます。Asterisk で使用するのに適したオプションであり、テレフォニーカードを購入する必要がありません。電話は直接 Ethernet ポートに届けられます。もう一つの利点は、コーデックのトランスコーディングを回避することで CPU のリソースを解放できる可能性があることです。

### アナログ FXS、FXO、E&M インターフェース

Several types of analog interfaces are available. It is fundamental to understand the differences between these interfaces to learn how to connect to the phone network as well as to other PBXs. Here, we will show you the E&M interface. Although it is not currently available for Asterisk and has been discontinued by several vendors, you may find routers and PBXs with this kind of interface, so it is better to know what you are dealing with。

#### 外国為替（FX）インターフェース

FXインターフェースはアナログです。用語「Foreign eXchange」は、PSTNのセンタリングオフィス（CO）へのアクセストランクに適用されます。Foreign eXchange Office (FXO)

![アナログ電話（FXS）と電話回線（FXO）の間のAsterisk：FXS側は電話にダイヤルトーンとリングを提供し、FXO側は中央局からダイヤルトーンを取得します.](../images/10-legacy-fig01.png)

FXO インターフェースは、セントラルオフィス（CO）または別の PBX の内線に接続するために使用されます。PSTN から来る電話回線と直接通信します。別のオプションとして、FXO インターフェースを既存の PBX に接続し、Asterisk とレガシー PBX の間で通信できるようにする方法があります。Asterisk を PBX ポートに接続し、VoIP を使用してリモート内線を提供することは、しばしばオフプロミス内線（OPX）と呼ばれます。FXO インターフェースはダイヤルトーンを受信します。  
Foreign eXchange Station（FXS）  
FXS インターフェースはアナログ電話、モデム、またはファックスに電力を供給します。FXS は電話にダイヤルトーンと電源を提供します。

#### トランクシグナリング

- ループスタート
- グラウンドスタート
- クールスタート

The use of kewlstart signaling in Asterisk is almost default. Kewlstart is not signaling itself, but adds intelligence to the circuit by monitoring what is happening on the other side. Kewlstart is based in loop-start. Most switches do not support this feature, which is used to get the hang-up notification.

- Loopstart: ほとんどのアナログ回線で使用され、電話が「オンフック」および「オフフック」を示し、スイッチが「リング」および「ノーリング」を示すことを可能にします。これはおそらく家庭で最も一般的に見られる方式です。名前は回線が常に開いていることに由来します。ループを閉じると、スイッチはダイヤルトーンを提供します。着信は、開いたペア上に 100V のリング電圧がかかることで通知されます。

![VoIPゲートウェイとして動作するAsterisk：FXOポートがレガシーPBXの内線に接続し、リモートのAsteriskがその回線をIP経由でアナログ電話にFXSポートを通して提供します（オフプレミス内線、またはOPX）。](../images/10-legacy-fig02.png)

- Groundstart: Loopstart と似ています。通話をかけたいとき、回線の片側が短絡されます。スイッチがこの状態を検知すると、開いたペアに対して電圧を逆転させ、ループが閉じます。その結果、回線は呼び出し側に提示される前にまず占有状態になります。
- Kewlstart: 回路にインテリジェンスを付加し、相手側の監視を可能にします。Kewlstart は loop‑start の多くの利点を取り入れています。

### Asterisk 電話チャンネル設定

電話インターフェースカードを設定するには、いくつかの手順が必要です。本章では、最も一般的なシナリオのうち3つをご紹介します：

- FXS を使用したアナログ接続
- FXO を使用したアナログ接続
- FXS および FXO インターフェースを備えた Astribank™ の接続

### 構成手順 (両方の場合に有効)

Asterisk のハードウェアを選択する前に、同時通話数、サービス、および有効化するコーデックの数を考慮すべきです。Asterisk は CPU 集中型アプリケーションであるため、専用マシンの使用を推奨します。コンピュータに搭載できるインターフェースカードの数は、スロット数と割り込み数によって制限されます。4 口カードを 2 枚よりも、8 口の単一カードを搭載する方が望ましいです。別の選択肢として、Xorcom Astribank のような USB チャネルバンクを使用する方法があります。最近では、一部のメーカー（例: CIANET）によって TDMoE チャネルバンクが製造され始めており、数十本のアナログインターフェースを接続することがさらに容易になっています。

![Xorcom Astribank：19インチラックマウントのUSBチャネルバンクで、PCIスロットを消費せずに多数のFXS/FXOポート（ここでは32ポートユニット）を提供します】(../images/10-legacy-fig03.png)

#### 例 1: FXO が 1 本、FXS が 1 本の構成

この例では、1つのFXSモジュールと1つのFXOモジュールを備えたSangoma TDM400テレフォニーインターフェースカード（以前はDigium TDM400として販売されていました）を使用します。必要な手順は以下に示します：

1. アナログカード FXS、FXO、またはその両方をインストールします。  
2. ファイル `/etc/dahdi/system.conf` を設定します（以前は `/etc/zaptel.conf`）。  
3. `dahdi_genconf` を使用して設定ファイルを生成します。  
4. DAHDI インターフェース用のドライバをロードします。  
5. 割り込みミスを確認するために `dahdi_test` を実行します。  
6. ドライバを設定するために `dahdi_cfg` を実行します。  
7. `chan_dahdi.conf` ファイルで DAHDI チャネルを設定し、次に Asterisk をロードします。

##### Step 1: TDM400 ボードをインストールする

TDM404P カードには FXS と FXO モジュールが搭載されています。FXS（S110M、緑）と FXO（X100M、赤）モジュールを接続してください。FXS モジュールを使用する場合は、カードをモレックスコネクタで電源に直接接続します。ハードウェアの損傷を防ぐため、インターフェースカードを取り扱う前に静電気防止策を講じてください。Sangoma（旧 Digium）アナログカードは、ハードウェアエコーキャンセレーションモジュール VPMADT032 もサポートしています。

##### Step 2: dahdi_genconfで設定を生成する

設定に関する良いニュースは、新しいユーティリティ `dahdi_genconf`で、DAHDI インターフェースの設定を自動的に検出し生成することです。このユーティリティは 2 つのファイルを生成します:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (with the `users` option)
- これらすべてのファイルはオプション`chan_dahdi full`を使用します。

Before you can execute `dahdi_genconf`, it is important to configure the file `genconf_parameters` (often referred to as `gen_parameters.conf`):

![Sangoma/Digium TDM404P アナログカード：最大4つのFXSまたはFXOモジュールを番号付きポートに差し込め、オプションのハードウェアエコーキャンセレーション・娘カードとFXSモジュール用の専用12 V電源コネクタを備えています.](../images/10-legacy-fig04.png)

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

`genconf_parameters`ファイルは設定をカスタマイズできます。アナログ回線に最も重要なパラメータは次のとおりです:

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

Warning: It is required that you configure at least the echo cancellation algorithm for the channels. The base_exten parameter defines the basic dial plan for FXS extensions. In this case, the first FXS channel will receive the extension number 4000, the second 4001, and so on. The context in which the lines (context_phones) and trunks (context_lines) are created is very important. After generating the files, you should include the file `/etc/asterisk/dahdi-channels.conf` in the file `/etc/asterisk/chan_dahdi.conf`:

```
#include dahdi-channels.conf
```

Note: アナログ信号は少し混乱しやすく、常にカードの逆になります。FXS カードは FXO で信号が送られ、FXO カードは FXS で信号が送られます。Asterisk はこれらのデバイスと、まるで反対側にあるかのように通信します。

##### Step 3: Load kernel drivers

Now you have to load the chan_dahdi module and the related card kernel driver. Use dahdi_hardware to detect your card and the driver name. For example:

| カード | ドライバ | 説明 |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 - 3.3V PCI |
| TE405P | wct4xxp | 4xE1/T1 - 5V PCI |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

Commands to load the drivers:

```
modprobe dahdi
modprobe wctdm
```

##### ステップ 4: dahdi_test ユーティリティの使用

重要なユーティリティは dahdi_test で、DAHDI カードの割り込みミスを検証するために使用されます。音声品質の問題はしばしば割り込みの競合に関連しています。DAHDI カードが他のカードと割り込みを共有していないことを確認するには、以下のコマンドを使用してください:

```
#cat /proc/interrupts
```

You can verify the number of interrupt misses using the dahdi_test utility compiled with the DAHDI cards. A number below 99.987% indicates possible problems.

##### Step 5: Use the dahdi_cfg utility to configure the driver

DAHDI has an unusual system for loading the drivers. First configure the /etc/dahdi/system.conf, and then apply those configurations to the DAHDI driver using dahdi_cfg. In this case, dahdi_cfg is used to configure the signaling for the FX interfaces. To see the results, you can append “-vvvvv” to the command for verbose.

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

If the channels were loaded successfully, you will see an output similar to the one shown above. Users often incorrectly configure chan_dahdi.conf with inverted signaling between channels. If this happens, you will see a message like the one shown below:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After successfully configuring the hardware, you can proceed to Asterisk configuration.

##### Step 6: Configure the /etc/asterisk/chan_dahdi.conf file

It sounds strange, but after configuring the /etc/dahdi/system.conf, you configured the card itself. DAHDI can be used for other purposes, like routing and SS7. To use it with Asterisk, you must configure the Asterisk DAHDI channels. Every channel in Asterisk has to be defined; SIP/PJSIP channels are defined in pjsip.conf (note: chan_sip and sip.conf were removed in Asterisk 21) while TDM channels are defined in chan_dahdi.conf. This creates the logical TDM channels to be used in your dial plan.

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

chan_dahdi.conf ファイルには多数のオプションがあります。すべてのオプションを説明すると退屈で逆効果になるため、ここでは理解しやすいように主要なオプショングループに焦点を当てます。

#### 一般オプション（チャネル非依存）

これらのオプションはすべてのチャネルで機能します。context: 受信コンテキストを定義します。

```
context=default
```

channel: チャネルまたはチャネル範囲を定義します。各チャネル定義は宣言の前に定義されたオプションを継承します。チャネルは個別に、またはカンマ区切りで同じ行に識別できます。範囲は “-” を使用して定義できます。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: チャネルをグループとして扱えるようにします。チャネル番号の代わりにグループ番号をダイヤルすると、利用可能な最初のチャネルが使用されます。チャネルが電話の場合、グループに電話すると、すべての電話が同時に鳴ります。カンマで区切ることで、同じチャネルに対して複数のグループを指定できます。

```
group=1
group=3,5
```

language: 国際化を有効にし、言語を設定します。この機能は特定の言語用にシステムメッセージを構成します。英語は標準インストールで利用できる完全なプロンプトが唯一の言語です。musiconhold: ミュージックオンホールドクラスを選択します。

#### Caller ID options

利用できる callerid オプションは多数あります。いくつかは無効にできますが、ほとんどはデフォルトで有効になっています。usecallerid: 後続のチャネルに対して callerid の送信を有効または無効にします (Yes/No)。注: システムが応答前に2回リングする場合は、この機能を無効にしてみてください。すぐに応答するはずです。hidecallerid: 発信側 callerid を隠すかどうかを定義します (Yes/No)。callerid: 特定のチャネル用に callerid 文字列を設定します。caller は asreceived で構成できます。これは主にトランクインターフェースで受信した callerid を示すために使用されます。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: 通話待ち中のcalleridをサポートします。 useincomingcalleridondahditransfer: 転送時に受信calleridを使用します。

#### 通話待ち

AsteriskはFXSチャネルで通話待ちをサポートしています。 ユーザーは、誰かが内線にかけた場合、待機トーンを受け取ります。 通話待ちを有効にするには:

```
callwaiting=yes
```

通話待ちで発信者番号をサポートするには:

```
callwaitingcallerid=yes
```

#### オーディオ品質オプション

エコーキャンセレーションの調整は、技術的側面と芸術的側面の両方を含みます。これらのオプションは、DAHDI チャネルのオーディオ品質に影響を与える特定の Asterisk パラメータを調整します。アナログインターフェースのオーディオ品質向上に役立ちます。

#### fxotune ユーティリティ

fxotune は FXO モジュール用の特定パラメータを微調整するユーティリティです。この微調整は、ハイブリッドによって生じるインピーダンス不整合を調整するために必要です。ユーティリティには 3 つの動作モードがあります。

- Detection (-i): 既存の FXO チャネルを検出・修正し、設定を保存します。

```
fxotune.conf
```

- Dump mode (-d): fxotune_dump.vals に波形ファイルを生成します
- Startup mode (-s): fxotune.conf ファイルを読み取り、FXO モジュールに適用します

It is important to understand that you will have to insert the instruction fxotune –s in the system load before starting Asterisk:

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### Echo cancellation

ほとんどのエコーキャンセリングアルゴリズムは、受信した信号の複数のコピーを生成し、それぞれを特定の時間だけ遅延させて動作します。フィルタのタップ数は、キャンセルすべきエコー遅延のサイズを決定します。これらの遅延コピーは調整され、受信信号から減算されます。ポイントは、遅延信号だけを調整してエコーを除去し、CPUサイクルを過剰に使用しないことです。ユーザーの観点からは、適切なエコーキャンセリングアルゴリズムを選択することが重要です。デフォルトはMG2ですが、他に2つのオプションがあります：Sangoma（旧Digium）提供のHigh Performance Echo Cancellation (HPEC) と、David Roweが開発したオープンソースエコーキャンセリング（OSLEC）です。

OSLEC (https://www.rowetel.com/?page_id=454) は Linux カーネルにマージされており、カーネルの `drivers/staging/echo` 領域に存在し、DAHDI は別途ダウンロードを提供するのではなく、これに対してビルドされます。エコーキャンセリングアルゴリズムを変更するには、`/etc/dahdi/system.conf` の `echo_can` パラメータを設定します。例:

```
echo_can=oslec
```

The echo cancellation in Asterisk is controlled by three parameters in the file /etc/asterisk/chan-

```
dahdi.conf.
```

- **echocancel**: エコーキャンセリングを無効化または有効化します。この機能は有効にしておくことを推奨します。`yes` またはタップ数を指定できます。（解説: エコーキャンセルはどのように機能するのでしょうか？ほとんどのエコーキャンセルアルゴリズムは、受信した信号の複数コピーを生成し、それぞれを短い間隔で遅延させて処理します。この遅延は「タップ」と呼ばれます。タップ数はキャンセルできるエコー遅延を決定します。これらのコピーは遅延させ、調整され、元の信号から減算されます。ポイントは、遅延信号をエコー除去に必要な正確な形に調整することです。）
- **echocancelwhenbridged**: 純粋な TDM 通話中にエコーキャンセラを有効化または無効化します。通常は必要ありません。
- **rxgain**: 受信音声のゲインを調整し、受信音量を増減させます（-100% から 100%）。
- **txgain**: 送信音声のゲインを調整し、送信音量を増減させます（-100% から 100%）。

For example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 課金オプション

これらのオプションは、通話詳細レコード（CDR）データベースに通話情報が記録される方法を変更します。amaflags: CDR の分類に影響を与える AMA フラグを設定します。以下の値を受け付けます：

- billing
- documentation
- omit
- default

accountcode: 特定のチャネル用のアカウントコードを設定します。任意の英数字を含めることができ、通常は部門名やユーザー名です。

```
accountcode=finance
amaflags=billing
```

### 通話進行オプション

これらの項目は、通話の進行状況に関する情報を取得するために使用されます。公開インターフェースでは、通話の進行を検出し、応答されたかビジーだったかを判断することが有用な場合があります。ビジー検出は高度に実験的であり、特定のパラメータによって制御されます。

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

これらのパラメータ（上記）は、インターフェースがビジートーンを検出しようとするかどうか、検出に使用されるトーンの数、そしてビジーパターンが何であるかを指定します。ビジー検出は主に実験的なものであり、追加のパラメータは Makefile で変更できます。正確な課金のために重要な通話の応答を検出するには、極性反転を使用して正確な応答時刻を示すことが可能です。これは、通話料金を請求する予定がある場合や、比較のために正確な課金を行いたい場合に重要です。通常、このサービスを利用するには電話会社に問い合わせる必要があります。

```
answeronpolarityswitch=yes
```

一部の国では、極性反転を使用して通話の切断を検出することも可能です。

```
hanguponpolarityswitch=yes
```

#### 電話のオプション

これらのオプションはFXSインターフェースに接続された電話で使用されます。DAHDIインターフェースに直接接続されたアナログ電話に提供されるすべての機能はAsteriskによって制御されます。

- **adsi** (Analog Display Services Interface): 一部の電話会社がチケット購入などのサービスを提供するために使用する電気通信標準のセットです。
- **cancallforward**: コールフォワーディングを有効または無効にします (*72で有効化、*73で無効化)。
- **calleridcallwaiting**: コール待ち表示中に受信したcalleridを有効にします (Yes/No)。
- **immediate**: インスタントモードでは、ダイヤルトーンを提供する代わりに、チャネルは定義されたコンテキストの「s」エクステンションへ即座にジャンプします。これはホットラインを作成するために使用されます。
- **threewaycalling**: 3者通話会議を有効または無効にします。
- **mailbox**: 利用可能なボイスメールメッセージについてユーザーに警告します。音声サインまたは視覚的インジケータ（電話がこの機能をサポートしている場合）で表示できます。引数はメールボックス番号です。
- **callgroup**: ダイヤルまたはピックアップする電話をグループ化します。
- **pickupgroup**: コールピックアップ用の電話グループです。

### 有用な DAHDI CLI コマンド

Asterisk が起動し DAHDI チャネルがロードされた状態で、Asterisk CLI からチャネルのステータスを確認できます。これらのコマンドは Asterisk 22 でも有効です。

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDIチャネルフォーマット

DAHDI チャネルはダイヤルプランで以下の形式を使用します：

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

例えば：

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## デジタルチャネル (E1/T1/PRI / TDM)

As of Asterisk 22, DAHDI and libpri remain fully supported, but TDM digital trunks (E1/T1/ISDN PRI) are increasingly replaced by SIP trunks in new deployments. This section remains fully applicable where TDM connectivity is required; in greenfield environments, SIP trunking (Chapter 3) usually delivers the same channel density without telephony hardware。

デジタルチャネルは非常に一般的であるため、大手顧客に注力したい場合はこれらのチャネルの実装方法を学ぶ必要があります。チャネル数が多い、通常は 8 本以上の場合、T1/E1/J1 などのデジタルインターフェースを使用することがかなり一般的です。T1 は米国で非常に一般的であり、E1 はヨーロッパで、J1 は日本で一般的です。この種のチャネルは、回線密度が高く、T1 チャネルあたり 24 本、E1 チャネルあたり 30 本の回線を提供します。

In Latin America, China, and Africa, it is common to use a type of channel associated signaling (CAS) known as MFC/R2. This chapter will examine how to implement MFC/R2 using the library OpenR2. In the US and Europe, Integrated Services Digital Networks (ISDN) PRI is the most common signaling. The chapter will also discuss ISDN Basic Rate Interface (BRI), which is very common in Europe in mid-range applications.

All examples in the book concentrate on DAHDI channels. Some cards are implemented using proprietary channels, so please check with your manufacturer for further details on how to configure your specific card.

### 目的

この章の終わりまでに、あなたは以下ができるようになります：

- デジタル電話で使用される主要な用語を認識する
- CAS と CCS シグナリングを区別する
- R2 と ISDN シグナリングを区別する
- ISDN シグナリングでインターフェースを設定する
- R2 シグナリングでインターフェースを設定する

### E1/T1 デジタル回線

デジタル回線のE1/T1は、多数のチャネルを実装する必要がある場合のオプションです。単一のE1回線は同時に30通話を処理でき、ダイレクトインワードダイヤル（DID）や発信者番号表示（Caller ID）などの機能や高度なシグナリングを利用できます。E1/T1回線は、国によってツイステッドペア、光ファイバー、マイクロ波など、さまざまな方法で会社に届きます。デジタル回線はUTP、光ファイバー、またはマイクロ波を使用して会社に配信されます。モデムやマルチプレクサ（MUX）が物理回線の提供に使用されます。T1回線への接続は常にRJ45コネクタを基盤としています。ただし、E1回線はBNCを使用して配線されることもあります。特にE1回線では、事前に受け取るコネクタの種類を把握しておくことが非常に重要です。通常、RJ45までのすべての機器はTELCOが提供します。

![E1/T1回線のプロビジョニング方法：電話会社はUTP銅線（E1はHDSLモデム、T1は直接カード接続）上でトランクを提供したり、光ファイバーを光マルチプレクサを介して提供したり、マイクロ波無線リンクで提供したりできます。](../images/10-legacy-fig05.png)

![UTPまたはBNC？ほとんどのデジタルカードはRJ45（UTP）コネクタを使用しますが、いくつかのE1回線はデュアルBNC同軸で提供され、その場合は同軸ペアをカードのRJ45ジャックに適合させるためにバランが必要です】(../images/10-legacy-fig06.png)

#### 音声はどのようにビットに変換されるのですか？

アナログ信号は1秒間に8,000回サンプリングされ、アナログ音声のデジタル版が作られます。このエンコーディングはパルス符号変調（PCM）として知られています。米国と日本では、信号はlaw（Asterisk では ulaw と呼ばれます）を使用してエンコードされます。その他の地域では、エンコーディングは alaw です。

![パルス符号変調（PCM）：4 kHz のアナログ音声信号が 1 秒間に 8,000 回サンプリング（ナイキスト）され、64 Kbps のデジタルビットストリームに符号化されます】(../images/10-legacy-fig07.png)

#### 時分割多重化

アナログ回線は、少数のチャネルだけが必要なときに適しています。時分割多重 (TDM) を使用すると、複数のチャネルを単一のデータ接続に詰め込むことが可能です。多数の回線が必要な場合、電話会社は通常、デジタルトランクを提供します。これは、音声が PCM を用いたデジタル形式で輸送されるデータ回線です。各タイムスロットは、単一の音声チャネルを輸送するために 64 Kbps の帯域幅を使用します。

![E1 と T1 における時分割多重化：E1 フレームは 32 のタイムスロットを 2048 Kbps で運び（DS0 #0 はフレーム同期用、DS0 #16 はシグナリング用）、一方 T1 フレームは 24 のタイムスロットを 1544 Kbps で運び、同期に 1 ビット、シグナリングにロブドビット方式を使用します】(../images/10-legacy-fig08.png)

米国では、最も一般的なデジタルトランクは T1 で、24 本の回線が利用可能です。ヨーロッパやラテンアメリカでは、E1 トランクが 30 本の回線を持ちます。いくつかの会社は、チャネル数が少ないフラクショナル T1/E1 を提供しています。  

Robbed bit signaling  
時々、T1 トランクはシグナリング用に 1 ビットを借用する robbed bit 方式を使用します。T1 トランクでは、データ/音声チャネルは各タイムスロットで 56 Kbps で送信されます。ご覧のとおり、robbed bit を使用すると、T1 回線は同期とシグナリングのために 2 スロットを失いません。

#### T1/E1ラインコード

T1 と E1 は実際にはデータ回線であり、ビットの解釈方法を決定するデータ符号化方式があります。E1 の場合、最も一般的なラインコードはレイヤ 1 が HDB3、レイヤ 2 が CCS です。デジタルトランクの設定を確認する最も簡単な方法は、TELCO にこの情報を問い合わせることです。この情報はファイル `/etc/dahdi/system.conf` を設定する際に必要になります。

#### T1/E1 シグナリング

T1/E1回線は、次のようなさまざまな種類のシグナリングで提供されることがあります：

- ロブドビットシグナリング付き T1
- ISDNシグナリング付き T1
- MFC/R2（CAS - Channel Associated Signaling）付き E1
- ISDNシグナリング付き E1

ISDNはヨーロッパや米国でよく使用されます。これは国際電気通信連合（ITU）が1984年に標準化したデジタル音声ネットワークです。ISDNは2種類のチャネルを提供します：

- ベアラーチャネル
  - 音声
  - データ
- データチャネル
  - アウト・オブ・バンドシグナリング
  - LAPDシグナリング
  - Q.931

通常、ISDN回線は2つの物理的手段を使用して提供されます：

- Basic rate interface (BRI)
  - Known as 2B+D
  - Two bearer (64K) channels and a data (16K) channel
  - Uses a pair of copper wires with 148Kbps.
- Primary rate interface (PRI)
  - Delivered using a T1/E1 trunk
  - 23B+D for T1s
  - 30B+D for E1s

時々、E1回線はMFC/R2と呼ばれるCAS信号方式を使用します。これはITUが標準として定義したQ.421/Q441として知られています。これはラテンアメリカやアジアで頻繁に見られます。これらの国々のいくつかの電話会社はMFC/R2のカスタマイズされたバリエーションを使用しています。したがって、動作させるためには正しい国別バリエーションを知っている必要があります。

### ISDN BRI

Channels using ISDN BRI signalling are very popular in Europe. Most ISDN BRI cards for Asterisk supports an S/T interface with NT and TE capabilities. The TE (terminal) connection is the one used to connect to the TELCO or to other PBXs configured as network termination (NT). The NT is used to connect phones and PBXs configured as TE. ISDN BRI provides two data/voice channels and one signalling channel. ISDN BRI cards are available from several vendors of interface cards for Asterisk.

### Asteriskサーバー用の電話カードの選び方

Asterisk と互換性のあるデジタルカードにはいくつかのメーカーがあります。カードの選択は以下の要因のいくつかに依存します。

#### データバス

There are several types of bus on your PC. It is very important that you have the right card for your server. The following overview outlines the most frequently used cards:

- ほとんどのコンピュータ（デスクトップを含む）で見られる 32 ビット PCI 5V
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
  - Sangoma A101, A102, and A104
- 基本的にサーバーで見られる 32/64 ビット PCI 3.3V
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
- デスクトップとサーバーで見られる PCI Express
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, and AEX800
  - Sangoma A101, A102, and A104

これらのカードファミリーは Digium で始まり、2018 年に Sangoma が買収しました。現在は Sangoma ブランドで販売・サポートされています。ここに掲載されている古い SKU の多くは廃止されているため、購入前に www.sangoma.com で現在のモデルの在庫状況を確認してください。

- MiniPCI は組み込みシステムで見つかります
  - OpenVOX A100M(FXO)、B100M(ISDN BRI)、B200M(ISDN BRI)、および B400M(ISDN BRI)
- USB 2.0 はほとんどの最新 PC に搭載されています。USB ベースのソリューションは、アナログおよびデジタルチャネルの高密度化を実現します。このバスは 480 Mbps をサポートし、各音声チャネルは 64 Kbps を占有します。USB ハブを使用すれば、単一ポートで最大千本のアナログポートに相当する密度を得ることが可能です。
  - Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet。Ethernet の最大の利点は、カードを複数のサーバーに接続できることです。高可用性ソリューションは通常、これらのデバイスの主要な用途となります。このソリューションの強みは、空き PCI スロットがないサーバーやブレードサーバーでも利用できる点です。
  - Redfone FoneBridge (最大 4 本の E1 回線)

### ハードウェアエコーキャンセレーションの使用

ハードウェアエコーキャンセラはホストCPUの負荷を軽減します。単一のE1インターフェース以上を持つカードでは、ハードウェアエコーキャンセラがプロセッサの負担を和らげるのに役立ちます。OSLEC のような新しい高度なソフトウェアエコーキャンセラは、ハードウェアエコーキャンセラの必要性を減らしています。ハードウェアとソフトウェアのエコーキャンセラを選択する際は、サーバーで利用可能な処理能力とE1回線の本数を考慮すべきです。エコーキャンセラ処理は、OSLEC を使用した場合、128 タップの振幅で音声チャンネルあたり最大 9 MIPS（秒間百万命令）を消費することがあります（参考: Xorcom Ltd.）。各命令につき 1 CPU サイクルと仮定すると（プロセッサやソフトウェア実装により必ずしも正しくない場合があります）、4 本のE1で 1.080 GHz 程度の負荷になると考えられます。

#### シグナリングの種類

信号方式の選択（例：T1 CAS、T1 PRI、E1 CAS R2、または E1 CAS ISDN）は簡単な作業ではありません。これは、地域で利用できるものや価格に大きく依存します。共通チャネル信号（CCS）は、チャネル関連信号（CAS）よりも優れていることが多いですが、利用できないことも頻繁にあります。米国では、ほとんどの TELCOS が通常ユーザー向けに T1 CAS、上級ユーザー向け（例：コールセンター）に T1 PRI を提供しているため、通常は選択が可能です。ラテンアメリカでは E1 CAS R2 が主流ですが、いくつかの都市では ISDN PRI が利用可能です。

![DAHDI ソフトウェアアーキテクチャ：Asterisk は `chan_dahdi` チャネルドライバと通信し、そこからプロトコルライブラリ libpri (ISDN)、libopenr2 (MFC/R2)、および libss7 (SS7) をロードします。これらは `/dev/dahdi` インターフェース、DAHDI カーネルドライバ、およびカード固有のインターフェースカーネルドライバの上に位置します。](../images/10-legacy-fig09.png)

R2 の実装は、Moises Silva が開発した OpenR2（www.libopenr2.org）というライブラリをインストールし、インストール前に Asterisk をパッチ適用するために必要です――この章の後半で示す簡単な手順です。このライブラリは複数のテストを通過しており、当社のいくつかの顧客環境で本番稼働しています。ISDN は、利用可能であれば常に最良の選択だと私は考えています。いくつかのプロバイダーは、電話会社間で利用できる CCS シグナリングであるシグナリングシステム 7（SS7）へのアクセスを提供しています。SS7 用のプロプライエタリおよびオープンソースのソリューションが利用可能です。ライブラリ libss7 は Asterisk 上で SS7 をサポートするために使用されます。

### Asterisk 電話チャンネル設定

Configuring a telephony interface card involves several necessary steps. In this chapter, we will show three of the most common scenarios:

- ISDN PRI を使用したデジタル接続
- ISDN BRI を使用したデジタル接続
- MFC/R2 を使用したデジタル接続

DAHDIチャネルを設定する方法は2つあります。1つ目は、すべてのパラメータを完全に制御しながら手動で設定することです。2つ目は、ユーティリティdahdi_genconfを使用してカードを検出および設定することです。

#### 自動検出と構成

Thanks to the DAHDI development team, we now have automatic detection and configuration of the cards. Step 1: To generate the configuration automatically, use the utility dahdi_genconf, which will detect the card and generate the files /etc/dahdi/system.conf and dahdi-channels.conf.

```
dahdi_genconf
```

Step 2: In the last line of the file chan_dahdi.conf, include the file dahdi-channels.conf

```
#include dahdi_channels.conf
```

ステップ3: ファイル modules の未使用モジュールすべてにコメントを付けるか、単に使用してください。

```
dahdi_genconf modules
```

#### 手動構成

別のオプションとして、インターフェースを手動で構成することができます。以下は DAHDI チャネルの構成例です。

##### 例 #1 – ISDN を使用した 2 本の T1/E1 チャネル

必要な手順:

1. TE205P または TE210P のインストール
2. `/etc/dahdi/system.conf` ファイル構成
3. DAHDI ドライバのロード
4. `dahdi_test` ユーティリティ
5. `dahdi_cfg` ユーティリティ
6. `chan_dahdi.conf` ファイル構成
7. Asterisk のロードとテスト

ステップ 1: TE205P のインストール。TE205P をインストールする前に、TE205P と TE210P カードの違いを理解しておくことが重要です。TE210P カードは、サーバーのマザーボードにほぼ唯一搭載されている 3.3 ボルトの 64 ビットバスで動作します。このインターフェースカードを指定する場合は、ハードウェアが 64 ビット、3.3V バスに対応していることを確認してください。TE205P カードは 5V PCI を使用し、デスクトップコンピュータでよく見られます。本例では、2 スパンの TE205P インターフェースカードを選択しました。これは、1 スパンカードに縮小したり、4 スパンカードに拡張したりしやすいためです。これらのカードは現在、Sangoma ブランド（旧 Digium）で販売されています。

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

TDM デジタルカードの設定は、アナログカードの設定とはやや異なります。まず、ボードのスパンを設定し、その後にチャンネルを設定する必要があります。スパンはカードの認識順に従って連番で付けられます。つまり、インターフェースカードが複数ある場合、どのスパンがどのカードに対応しているか把握しにくくなります。`dahdi_hardware` を使用して、各スパンにどのハードウェアがインストールされているか確認してください。Example #1 (2xT1 PRI)

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

例 #2 (2xE1 PRI)

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

例 #3 (4xBRI)

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

ステップ3：カーネルドライバのロード dahdi_hardware を使用して、インストールが必要なドライバを確認してください。

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

ロードするには次を使用します：

```
modprobe dahdi
modprobe wct2xxp
```

ステップ4: dahdi_test を使用して欠落した割り込みを確認する

DAHDI カードでコンパイルされた dahdi_test ユーティリティを使用して、割り込みミスの数を確認できます。99.987% 未満の数値は問題の可能性を示します。dahdi_test は以下にあります

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

ステップ5: dahdi_cfg ユーティリティの使用  
これは、1つのフラクショナルE1（15ポート）スパンと2つのFXOポートに対する dahdi_cfg の正しい出力です。

```
#./dahdi_cfg -vvvv
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

Step 6: DAHDIの設定をファイル /etc/asterisk/chan_dahdi.conf に 行う Example #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

例 #2 (2xE1)

```
callerid="Flavio Eduardo" <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

# 例 #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Use signaling=bri_cpe_ptmp for point to multipoint BRI. Currently, BRI point to multipoint is not supported in NT mode.

#### カーネルドライバのロード

After configuring the drivers, you may simply restart the server. If you have installed DAHDI with make config, you won’t need to do anything extra. The kernel driver will be automatically loaded and configured. However, sometimes it is useful to load and unload the drivers manually. Example:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

The first command loads the driver and the second, dahdi_cfg, applies the configuration to the kernel driver.

### トラブルシューティング

Sometimes things don’t work the first time. Let’s check some resources for troubleshooting DAHDI. Step 1: Check if the card is being recognized by the operation system. Sangoma/Digium cards are usually recognized as the ISDN modem.

```
lspci -v
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

ステップ2: カーネルドライバが正しくロードされているか確認するには、次を使用します:

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

ステップ3：接続の物理層に関連するアラームの状態を確認します。E1 接続の物理層を確認するには、以下の Asterisk CLI コマンドを使用できます。

```
dahdi show status
```

アラームはポートの問題を示します: Red Alarm: リモートスイッチとの同期を維持できません。これは通常、ラインコードやフレーミングの不一致などの物理的な問題です。Yellow alarm: リモートスイッチが Red Alarm の状態であることを示します。これはリモートスイッチがあなたの送信を受信していないことを意味します。Blue Alarm: すべてのタイムスロットでフレーム化されていない 1 が受信されます；dahdi_tool は現在 Blue Alarm を検出しません。Loopback: ポートはローカルまたはリモートのループバック状態です

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

ステップ4：AsteriskサーバーでのDAHDIの問題を検出するには、まずチャンネルが認識されているかどうかを次の方法で確認します：

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

Step 5: ISDNレイヤ3（q.931としても知られています）のステータスを確認します。ISDNレイヤ3が稼働しているかどうかは、`pri show spans`（すべてのスパンを一覧表示）または`pri show span <n>`（特定のスパン用）を使用して確認できます。

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

Use `pri show spans`（複数形）を使用して、設定されたすべての PRI スパンのステータスを一度に一覧表示します。

Check a specific channel. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
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

debug pri span x: すべてを試した後でも問題が残る場合は、pri span のデバッグを開始してください。このコマンドは ISDN 呼び出しの詳細なデバッグを有効にします。何かが正しくないと考えるときに重要なコマンドです。誤ってダイヤルされた数字やその他の問題を検出できます。以下に、成功した呼び出しのデバッグ出力例を示します。問題のある呼び出しと問題のない呼び出しを比較する必要がある場合は、この例を参照してください。1 つのヒントとして、core set verbose=0 を使用すると ISDN q.931 メッセージだけを受信できます。

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
> [a1]
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

### Configuration options in chan_dahdi.conf

Several options are available in the file chan_dahdi.conf. A description of all options would be boring and counterproductive. Here, we will detail the main option groups available to provide a better understanding.

#### General options (channel independent)

context: Defines the incoming context.

```
context=default
```

channel: チャネルまたはチャネル範囲を定義します。各チャネル定義は宣言の前に定義されたオプションを継承します。チャネルは個別に、またはカンマ区切りで同じ行に識別できます。範囲は “-” を使用して定義できます。

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: チャネルをグループとして扱えるようにします。チャネル番号の代わりにグループ番号をダイヤルすると、利用可能な最初のチャネルが使用されます。チャネルが電話の場合、グループに電話するとすべての電話が同時に鳴ります。カンマを使用して、同じチャネルに対して複数のグループを指定できます。

```
group=1
group=3,5
```

language: 国際化を有効にし、言語を設定します。この機能は特定の言語用にシステムメッセージを構成します。英語は標準インストールで利用できる完全なプロンプトが唯一の言語です。musiconhold: 待機音楽クラスを選択します。

#### ISDN options

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: ダイヤルプランの指定が必要な一部のスイッチで必須です。このオプションは多くのスイッチで無視されます。有効なオプションは private、national、international、unknown です。

```
pridialplan = unknown
```

prilocaldialplan: 一部のスイッチに必要で、通常は不明です。

```
prilocaldialplan = unknown
```

overlapdial: Overlap dialing は、接続確立後に数字を送信する際に使用されます。ブロックモード番号付け (overlapdial=no) またはデジットモード (overlapdial=yes) を選択できます。ブロックモードはオペレーターがよく使用します。  
signaling: 後続のチャンネルのシグナリングタイプを設定します。これらのパラメータは chan_dahdi.conf ファイルの設定と対応している必要があります。正しい選択は利用可能なチャンネルに基づきます。ISDN の場合、次の 5 つのオプションから選択できます。

- pri_cpe: デバイスが CPE（クライアント、ユーザー、スレーブとも呼ばれる）である場合に使用します。最もシンプルで一般的に使用されるシグナリング形態です。プライベート PBX に接続しようとした際、PBX が CPE として設定されていることがよくあります。この場合、Asterisk では pri_net シグナリングを使用します。  
- pri_net: Asterisk が CPE として設定されたプライベート PBX に接続されている場合に使用します。シグナリングはホスト、マスター、またはネットワークと呼ばれることがあります。  
- bri_cpe: Asterisk が ISDN BRI トランクに CPE として接続されている場合に使用します。  
- bri_net: Asterisk が端末 (TE) として設定された ISDN 電話または PBX に接続されている場合に使用します。  
- bri_cpe_ptmp: bri_cpe と同じですが、ポイント・ツー・マルチポイント構成です。

#### CallerID options

利用可能な Caller ID オプションは多数あります。いくつかは無効にでき、ほとんどはデフォルトで有効です。  
usecallerid: 後続のチャンネルに対して Caller ID の送信を有効または無効にします (Yes/No)。注: システムが応答前に 2 回リングする必要がある場合、この機能を無効にするとすぐに応答できるようになります。  
hidecallerid: Caller ID を非表示にします (Yes/No)。  
calleridcallwaiting: コール待ち表示中に Caller ID を受信できるようにします (Yes/No)。  
callerid: 特定のチャンネル用に Caller ID 文字列を設定します。トランクインターフェースでは “asreceived” を使用して Caller ID をそのまま転送できます。

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Note: 多くの TELCO は正しい発信者番号を設定することを義務付けています。正しい発信者番号を渡さない場合、TELCO 経由で発信できなくなるはずです。一方、発信者番号を設定しなくても着信は可能です。

#### Audio quality options

これらのオプションは、DAHDI チャネルの音声品質に影響する Asterisk パラメータを調整します。

- **echocancel**: エコーキャンセルを無効化または有効化します。この機能は有効にしておくべきです。「yes」またはタップ数を指定できます。(説明: エコーキャンセルはどのように機能するのか？ほとんどのエコーキャンセルアルゴリズムは、受信した信号の複数のコピーを生成し、各コピーを短い間隔で遅延させます。この遅延は「tap」と呼ばれます。タップ数はキャンセルできるエコー遅延を決定します。これらのコピーは遅延させ、調整され、元の信号から減算されます。ポイントは、遅延信号をエコー除去に必要な正確な量に調整することです。)
- **echocancelwhenbridged**: 純粋な TDM 通話中にエコーキャンセルを有効または無効にします。通常は必要ありません。
- **rxgain**: 受信音量を増減させるためにオーディオ受信ゲインを調整します（-100% から 100%）。
- **txgain**: 送信音量を増減させるためにオーディオ送信ゲインを調整します（-100% から 100%）。

Example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### 課金オプション

これらのオプションは、通話詳細レコード（CDR）データベースに通話情報が記録される方法を変更します。 amaflags: CDR の分類に影響します。以下の値を受け付けます:

- billing
- documentation
- omit
- default

accountcode: 特定のチャネルのアカウントコードを設定します。任意の英数字を含めることができ、通常は部門名やユーザー名が使用されます。

```
accountcode=finance
amaflags=billing
```

### MFC/R2 設定

MFC/R2はラテンアメリカのいくつかの国、中国、アフリカ、そしていくつかのヨーロッパ諸国で使用されています。  
ISDNは優れており、利用可能な地域では推奨されます。

#### 問題の理解

The card used to signal MFC/R2 is the same used to signal ISDN. It’s possible to use MFC/R2 on DAHDI channels using the library called libopenR2 (www.libopenr2.com). This library was not part of versions of Asterisk prior to 1.6.2.

##### MFC/R2 プロトコルの理解

The MFC/R2 protocol combines in-band and out-of-band signaling. Address signaling is forwarded in-band using a set of tones while channel information is transmitted over timeslot 16 as out-of-band signaling。

**Line Signaling (ITU-T Q.421).** タイムスロット16では、各音声チャネルが4ビットのABCDビットを使用して状態と呼制御を信号します。ビットCとDはほとんど使用されません。いくつかの国では、課金用のパルスメータリング（メータリング）に使用されることがあります。通常の会話では、呼び出し側と呼び出され側の両方が機能します。呼び出し側からの信号は**forward signaling** と呼ばれ、呼び出され側は **backward signaling** を使用します。ここでは、forward signaling を **Af** と **Bf**、backward signaling を **Ab** と **Bb** と表記します。

| State | ABCD forward | ABCD backward |
| --- | --- | --- |
| Idle/Released | 1001 | 1001 |
| Seized | 0001 | 1001 |
| Seize Ack | 0001 | 1101 |
| Answered | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (before clear-back) | 1001 | 0101 |
| ClearFwd (disconnection confirmation) | 1001 | 1001 |
| Blocked | 1001 | 1101 |

MFC/R2はITUによって定義されました。残念ながら、いくつかの国は標準を自国のニーズに合わせてカスタマイズしました。その結果、国ごとに標準のばらつきが生じました。

**インターレジスタ信号 (ITU-T Q.441)。** MFC/R2 シグナリングは 2 つのトーンの組み合わせを使用します。 以下の表は ITU 標準を示しています。

シグナルグループ I（フォワード）：

| Description | Forward signal |
| --- | --- |
| 数字 1 | I-1 |
| 数字 2 | I-2 |
| 数字 3 | I-3 |
| 数字 4 | I-4 |
| 数字 5 | I-5 |
| 数字 6 | I-6 |
| 数字 7 | I-7 |
| 数字 8 | I-8 |
| 数字 9 | I-9 |
| 数字 0 | I-10 |
| 国番号インジケータ、送信側ハーフエコ抑制が必要 | I-11 |
| 国番号インジケータ、エコ抑制不要 | I-12 |
| テストコールインジケータ | I-13 |
| 国番号インジケータ、送信側ハーフエコ抑制が挿入される | I-14 |
| 未使用 | I-15 |

Signal group II（フォワード）:

| Description | Forward signal |
| --- | --- |
| 優先度なし加入者 | II-1 |
| 優先度あり加入者 | II-2 |
| 保守機器 | II-3 |
| 予備 | II-4 |
| オペレーター | II-5 |
| データ伝送 | II-6 |
| 転送機能なしの加入者またはオペレーター | II-7 |
| データ伝送 | II-8 |
| 優先度あり加入者 | II-9 |
| 転送機能ありオペレーター | II-10 |
| 予備 | II-11 |
| 予備 | II-12 |
| 予備 | II-13 |
| 予備 | II-14 |
| 予備 | II-15 |

シグナルグループ A（逆方向）：

| Description | Backward signal |
| --- | --- |
| 次の桁（n+1）を送信 | A-1 |
| 最後から2番目の桁（n-1）を送信 | A-2 |
| アドレス完了、Group B 信号の受信へ切り替え | A-3 |
| 国内ネットワークの混雑 | A-4 |
| 発信者のカテゴリを送信 | A-5 |
| アドレス完了、課金、通話条件設定 | A-6 |
| 最後から3番目の桁（n-2）を送信 | A-7 |
| 最後から4番目の桁（n-3）を送信 | A-8 |
| 予備 | A-9 |
| 予備 | A-10 |
| 国番号指示子を送信 | A-11 |
| 言語または識別桁を送信 | A-12 |
| 回線の性質を送信 | A-13 |
| エコーサプレッサ使用情報の要求 | A-14 |
| 国際交換局またはその出力での混雑 | A-15 |

シグナル グループ B（逆方向）：

| Description | Backward signal |
| --- | --- |
| 予備 | B-1 |
| 特別情報トーンを送信 | B-2 |
| 加入者回線がビジー | B-3 |
| 混雑（グループAからBへの切替後） | B-4 |
| 未割り当て番号 | B-5 |
| 加入者回線が空き、課金あり | B-6 |
| 加入者回線が空き、課金なし | B-7 |
| 加入者回線が故障 | B-8 |
| 予備 | B-9 |
| 予備 | B-10 |
| 予備 | B-11 |
| 予備 | B-12 |
| 予備 | B-13 |
| 予備 | B-14 |
| 予備 | B-15 |

#### MFC/R2 シーケンス

以下のシーケンスは、Asterisk のエクステンションから PSTN の端末へ発信される呼び出しを示しています。PSTN は呼び出しを切断し、通信を終了します。

![Asterisk と電話会社間の完全な MFC/R2 コールフロー：ラインシグナリング（Idle、Seized、Seize Ack、Answer、Clearback、Clear Forward）がタイムスロット 16 で交換され、ダイヤルされた数字と逆方向の「send next digit」シグナル（グループ I/A/B）はインバンドで伝送され、可聴トーンが加入者に届く】(../images/10-legacy-fig11.png)

### ドライバ libopenr2 の使用方法

プロジェクトは Moises Silva によって開始され、Steve Underwood が作成した Unicall チャネルドライバに触発されました。OpenR2 ライブラリは現在、Asterisk 用の最も安定したソフトウェアソリューションです。このソリューションを使用すれば、DAHDI と互換性のある任意のデジタルカードを利用できます。以前は MFC/R2 用の専用ソリューションしか利用できませんでしたが、私が使用した中で最も優れたものの一つは Khomp が提供するもの（www.khomp.com.br）です。Asterisk 22 では、コンパイル時にライブラリが存在すれば libopenR2 を介した MFC/R2 サポートが組み込まれ、外部パッチは不要です。以下の手順は参考用に歴史的な手動インストール方法を示しています。最新のシステムでは、`libopenr2-dev` をディストリビューションのパッケージマネージャからインストールしてから `./configure` を実行し、`chan_dahdi` を `make menuselect` で有効にしてください。

以下の手順は、openr2 と Asterisk を現在の Git リポジトリからビルドします。ソースからビルドするサイトの参考として残しています。最新のディストリビューションでは、通常、`libopenr2-dev`パッケージとパッケージ化された Asterisk 22 をインストールするだけでこれらの手順を完全に省略できます。なぜなら、`chan_dahdi`は外部パッチなしで libopenr2 に直接 R2 サポートをコンパイルするからです。

ステップ1：必要なビルドツールをインストールします。

```
apt-get install git
```

Step 2: Clone the openr2 library and the Asterisk source. No special patched tree is needed on Asterisk 22 — a stock checkout builds R2 support as long as libopenr2 is present.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

ステップ3: コンパイルとインストール サーバーをバックアップしてから続行してください。

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note: 「make samples」を実行しないで、設定ファイルが上書きされるのを防いでください。

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Let’s suppose you have a card with one E1 interface. → 「E1インターフェースが1つあるカードがあるとします。」

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

ステップ5: コマンド dahdi_cfg を実行して、ドライバへの変更を適用します:

```
dahdi_cfg -vvvvvvvv
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

Step 5: ファイル chan_dahdi.conf を変更する

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

ステップ6: ファイル extensions.conf のダイヤルプランを変更する

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Note: Some TELCOS do not accept calls without the caller ID. Please set the caller ID to one of the DID numbers assigned by the operator. In some countries, this step is not required. Step 7: Test the solution: Now, with an extension in the context from-internal, call any number and observe the console. Check to see if any errors are occurring. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Debugging OpenR2

To detect errors in the calls, you can activate the debug. To do this, follow the steps below.

1. Edit the file `chan_dahdi.conf` and add the following three lines to the configuration:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. Restart the Asterisk server
3. Test the call and check the call files at `/var/log/asterisk/mfcr2/span1`

Below is a trace for a normal call. Compare it to what you receive in your call.

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

#### MFC/R2 設定

オプションはファイル chan_dahdi.conf に文書化されています。ここでは最も重要なオプションのいくつかを詳述します。必須パラメータ: mfcr2_variant、mfcr2_max_ani、mfcr2_max_dnis。mfcr2_variant: 国別バリアント。

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

mfcr2_max_ani: 要求する ANI 桁数の最大値  
mfcr2_max_dnis: 要求する DNIS 桁数の最大値  
mfcr2_get_ani_first: ANI を DNIS の前に取得するかどうか（一部の TELCOS で必須）  
mfcr2_category: 発信者カテゴリ。通話開始前に変数 MFCR2_CATEGORY を設定できます  
mfcr2_logdir: 通話ファイルを記録するディレクトリ (/var/log/asterisk/mfcr2/directory)  
mfcr2_call_files: 通話を記録するかどうか  

- mfcr2_logging: ロギングの値  
- cas – tx と rx 用の ABCD ビット  
- mf – 多周波トーン  
- stack – チャネルとコンテキストスタックの詳細出力  
- all – すべてのアクティビティ  
- nothing – 何も記録しない  

mfcr2_mfback_timeout: この値は特に言及すべきです。セルフォンや長時間かかる通話を行う場合、このパラメータがタイムアウトすることがあり、微調整のために変更されることが多いです。通話が完了しない場合は、まずこのパラメータを変更してください。  
mfcr2_metering_pulse_timeout: パルスは一部の R2 バリアントで料金を示すために使用されます  
mfcr2_allow_collect_calls: ブラジルではトーン II-8 が着払い通話を示すために使用されます。このパラメータで着払い通話をブロックできます。  
mfcr2_double_answer: ダブルアンサーが必要な場合に着払い通話を回避するためにも使用されます。double_answer=yes に設定すると、実際に着払い通話をブロックします。  
mfcr2_immediate_accept: グループ B/II 信号の使用をスキップし、直接受け入れ状態に移行できます。  
mfcr2_forced_release: 通話の切断を高速化します。ブラジル版で機能します。  

#### ANI and DNIS

Automatic Number Identification (ANI) は発信者の番号です。Dialed Number Identification Service (DNIS) は呼び出された番号、すなわちダイヤルされた番号です。通話が受信されると、通常最後の 4 桁が直接インバウンドダイヤル (DID) と呼ばれるプロセスで PBX に渡されます。ANI 番号は実際には Caller ID です。ANI にはダイヤル時の発信者の内線が含まれ、DNIS には通話先が含まれます。これらのパラメータは正しく設定することが重要です。一部のスイッチは最後の 4 桁だけを送信し、他は完全な番号を送信します。  

### DAHDI channel format

DAHDI チャネルはダイヤルプランで次の形式を使用します:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

例:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## The IAX2 protocol

In this chapter, we will learn about the Inter-Asterisk eXchange (IAX) protocol, including its strengths and weaknesses. Details such as trunk mode and the interconnection of two Asterisk servers will also be covered. All references in this document correspond to IAX version 2.

The IAX protocol provides media transport and signaling for voice and video. IAX is very innovative; it saves bandwidth in trunk mode and is much simpler than SIP when you need to traverse NAT. The primary use for IAX nowadays is to interconnect Asterisk servers. IAX was created primarily for voice, but it can also accommodate video and other multimedia streams.

IAX was inspired from other VoIP protocols, such as SIP and MGCP. Instead of using two separate protocols for signaling and media, IAX unified them to make a unique protocol. IAX does not use RTP for media transport; instead, it embeds the media in the same UDP connection.

**Status in Asterisk 22.** `chan_iax2` is still included and fully supported in Asterisk 22 LTS, so everything in this section remains valid. IAX2 is, however, a legacy protocol that sees relatively little new deployment: the industry has largely converged on SIP (via `chan_pjsip` in Asterisk 22) for both provider trunking and server interconnection. IAX2's main remaining advantage is its single-port design — all signaling and media flow over a single UDP port (4569 by default), which simplifies firewall and NAT configuration compared to SIP plus its separate RTP streams. For a new Asterisk-to-Asterisk trunk where NAT is not a concern, a PJSIP trunk is the recommended modern approach; IAX2 is covered here because it remains a valid choice, especially where only one UDP port can be opened through a firewall.

### Objectives

By the end of this chapter, you should be able to:

- Identify strengths and weakness of IAX protocol
- Describe usage scenarios for the IAX protocol
- Describe the advantages of IAX trunk mode
- Configure iax.conf for phones
- Configure iax.conf for connection to a VoIP provider
- Configure iax.conf for Asterisk interconnection
- Understand IAX authentication

### IAX design

The main objectives for IAX design are:

- To reduce the bandwidth required for media transport and signaling
- To provide NAT transparency
- To be able to transmit the dial plan information
- To support the efficient use of paging and intercom

IAX is a peer-to-peer signaling and media protocol that is similar to SIP without using RTP. The basic approach is to multiplex the multimedia streams over a single UDP connection between two hosts. The greatest benefit of this approach is its simplicity when traversing connections over NAT, regularly found in xDSL modems. IAX uses a single port, UDP 4569 by default, and then uses a call number with 15 bits to multiplex all streams. The IAX protocol uses registration and authentication processes similar to the SIP protocol. A description of the protocol can be found at http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![The IAX protocol multiplexes many calls between two endpoints over a single UDP port (4569 by default), using a 15-bit call number to keep the streams apart — which makes NAT traversal simple.](../images/10-legacy-fig12.png)

### Bandwidth usage

The bandwidth used in VoIP networks is affected by several factors; codecs and protocol headers are the most important. The IAX protocol has a surprising feature called trunk mode, whereby it multiplexes several calls using a single header. By playing with the Asterisk bandwidth calculator, you will see how IAX trunks can save you up to 80% of the traffic with multiple calls.

![Comparing IAX and SIP overhead: two SIP/RTP calls need two packets (40 bytes of payload carried under 156 bytes of overhead), while IAX2 trunk mode carries both calls in a single packet (40 bytes of payload under just 66 bytes of overhead) by sharing one IP/UDP header across many mini-frames.](../images/10-legacy-fig13.png)

### Channel naming

It is important to understand channel-naming conventions as you will use these names when specifying a channel in the dial plan. The format of an IAX channel name used for outbound channels is:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — リモートピアの UserID、または iax.conf に設定されたクライアント名  
- `<secret>` — パスワード。あるいは、拡張子（.key または .pub）を除いた RSA 鍵ファイル名を角括弧で囲んだもの  
- `<peer>` — 接続先サーバーの名前  
- `<portno>` — 接続用ポート番号  
- `<exten>` — リモート Asterisk サーバー上のエクステンション  
- `<context>` — リモート Asterisk サーバー上のコンテキスト  
- `<options>` — 利用可能な唯一のオプションは 'a' で、'request autoanswer' を意味する  

#### Outbound channels example:

Outbound channels are seen in the Asterisk console.

- `IAX2/8590:secret@myserver/8590@default` — myserver の 8590 エクステンションに発信します。名前/パスワードの組み合わせは 8590:secret です  
- `IAX2/iaxphone` — "iaxphone" に発信します  
- `IAX2/judy:[judyrsa]@somewhere.com` — judy をユーザー名、RSA 鍵を認証に使用して somewhere.com に発信します  

#### The format of an incoming IAX channel is:

Inbound channels are seen in the Asterisk console.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — ユーザー名（既知の場合）
- `<host>` — 接続元ホスト
- `<callno>` — ローカル呼び出し番号

着信チャネルの例:

- `IAX2[flavio@8.8.30.34]/10` — ユーザー flavio として IP アドレス 8.8.30.34 からの呼び出し番号 10。
- `IAX2[8.8.30.50]/11` — IP アドレス 8.8.30.50 からの呼び出し番号 11。

### Using IAX

IAX はさまざまな方法で使用できます。このセクションでは、以下のシナリオ向けに IAX を設定する方法を示します。

- IAX を使用したソフトフォンの接続
- IAX を使用した VoIP プロバイダーへの接続
- IAX を使用した 2 台のサーバー間接続
- IAX を使用したトランクモードでの 2 台のサーバー間接続
- IAX 接続のデバッグ
- 認証に RSA 鍵ペアを使用

#### Connecting a softphone using IAX

Asterisk は IAX に基づく IP 電話、たとえば ATCOM や Digium の旧 ATA（IAXy と呼ばれる）だけでなく、IAX2 プロトコルを実装したソフトフォンもサポートします。ソフトフォン、ATA、ハードフォンの設定手順は似ています。IAX デバイスを設定するには、/etc/asterisk の iax.conf ファイルを編集する必要があります。

```
directory.
```

例として IAX2 対応のソフトフォンを使用します。

1. 元の`iax.conf`ファイルのバックアップを作成します:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. 新しい`iax.conf`ファイルの編集を開始します:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; 非常に重要なパラメータで、利用可能なコーデックを変更します

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

サンプルファイルのデフォルト（コメントされていない）行はできるだけ保持するようにしました。以下のパラメータが変更されました：

```
bandwidth=high
```

この行はコーデックの選択に影響します。高い設定を使用すると、ulaw キーワードで定義された g.711 のような高帯域幅・高品質のコーデックを選択できます。デフォルトのパラメータのままにすると、ulaw を選択できません。この場合、以下の設定に対して Asterisk は「no codec available」というメッセージを返します。

```
disallow=all
allow=ulaw
```

上記のコマンドでは、すべてのコーデックを無効にし、ulaw のみを有効にしました。LAN 環境では、ulaw はプロセッサ負荷が低く CPU サイクルを節約できるため、ほとんどの人が使用することを好みます。帯域幅を多く使用しますが、LAN では通常 100 メガビット Ethernet あるいはギガビットが利用できるため、このコーデックの方が好ましいです。ulaw を使用した音声通話は、ネットワークからほぼ 100 キロビット/秒の帯域幅しか使用せず、今日の高速 LAN にとっては非常に軽い負荷です。WAN やインターネット環境では、通常 ulaw を無効にし、音声圧縮によって利用可能な CPU サイクルをいくらか犠牲にして、帯域幅の使用効率を向上させます。gsm、g729、ilbc のコーデックも同様に優れた圧縮率を提供します。

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

上記のコマンドでは、[2003] という名前の友人を定義しました。コンテキストはデフォルトです（最初のラボでは混乱を避けるために常にデフォルトコンテキストを使用します。このコンテキストはダイヤルプランを扱う際に詳しく説明します）。行の “host=dynamic” は、電話の IP アドレスを動的に登録することを意味します。

3. IAX2 対応のソフトフォンをダウンロードしてインストールします。ラボ用に IAX2 プロトコルをまだサポートしているソフトフォンを任意に選択できます。  
4. クライアントで IAX アカウントを設定します（通常は *Add account* → IAX）。SipPulse Softphone は SIP のみで、IAX2 での登録はできないため、IAX のテストにはプロトコルをサポートしたクライアントが必要です。

5. `extensions.conf` ファイルを設定して IAX デバイスをテストします。

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Connecting to a VoIP provider using IAX

A few VoIP providers support IAX. You can easily find an IAX provider by searching for “IAX providers”. Using an IAX provider makes a lot of sense as IAX can save a lot of bandwidth, easily traverses NAT, and can authenticate using RSA key pairs.

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

The number of IAX-capable commercial VoIP providers has declined sharply over the past several Asterisk releases; most providers now offer SIP/PJSIP trunks exclusively. Before committing to an IAX provider, confirm they actively maintain their IAX infrastructure. For a new provider integration, a PJSIP trunk (Chapter 3) is the recommended alternative.

#### Connecting to a provider using IAX

Step 1: Open an account in your favorite provider. Your provider will provide you three things.

- Name
- Secret
- IP address or Host name
- RSA public key

Step 2: Configure the iax.conf file to register your Asterisk with your provider. Add the following lines to the [general] section of the file.

```
[general]
register=>name:secret@hostname/2003
```

上記の手順では、アカウントとパスワードを使用してプロバイダーに登録しました。電話がかかってきた瞬間に、2003 エクステンションに転送されます。

```
[name]
```

- ; あなたのアカウント名または番号

```
type=peer
secret=secret
; Your password
host=hostname
```

上記の手順では、ダイヤリング用にプロバイダーに対応するピアを作成しました。

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

This is required for RSA authentication. Using the public key from your provider allows you to be sure that the call being received is really from the true provider. If anyone else tries to use the same path, they will not be able to authenticate it because they do not have the corresponding private key. Step 4: Try the connection. To test the connection, call any number. Some vendors provide an echo test. To accomplish this, please edit the file extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Go to the Asterisk CLI and issue a reload. To verify if Asterisk is registered with the provider, use the next command.

```
*CLI>reload
*CLI>iax2 show register
```

Now simply dial *98 on the softphone connected to the Asterisk server.

#### Connecting two Asterisk servers through an IAX trunk

It is very easy to connect one server to another. You won’t need to register them because the IP addresses are already known. You will have to create the peers and users in the iax.conf file. All extensions in the HQ site start with 20 followed by two digits (e.g., 2000). In the Branch, all extensions start with 22 followed by two digits (e.g., 2200). We will use the trunk. You will need a DAHDI timing source to enable this feature. Step 1: Edit the iax.conf file in the Branch server.

![HQサーバー（192.168.1.1、内線20xx）とブランチサーバー（192.168.1.2、内線22xx）が単一のIAXトランクで相互接続され、両方のIPアドレスが固定かつ既知のため登録は不要です](../images/10-legacy-fig15.png)

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

ステップ2：ブランチサーバーで extensions.conf ファイルを設定する

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

ステップ3：HQサーバーでiax.confファイルを設定する

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

ステップ4: HQサーバーで extensions.conf ファイルを設定します。

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

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

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

If a call has a specified username, such as:

- ゲスト
- iaxtel
- iax-gateway
- iax-friend

Asterisk will try to authenticate the call using only the corresponding entry in the iax.conf file. If any other names are specified, the call would be rejected. If no user is specified, Asterisk will try to authenticate the connection as guest. However, if guest does not exist, it will try any other connections with a matching secret. In other words, if you don’t have a guest section in your iax.conf file, a malicious user could try to guess any matching secret by not specifying the user name. IP addresses’ deny/allow restrictions apply too. A good way to avoid secret guessing is to use RSA authentication. Another method is to restrict the IP addresses allowed to call in.

#### IP address restrictions

Access is controlled with `permit` and `deny` lines:

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

ルールは順番に解釈され、すべてが評価されます（この概念は、ルーターやファイアウォールで通常見られる ACL とは異なります）。最後に一致した指示がそれ以前のものに優先します。

例 #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

This will deny any packet from the 192.168.0.0/24 network.

例 #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

この設定は最初の指示を上書きするため、すべてのパケットを許可します。

#### Outbound connections

Outbound connections acquire authentication information using the following methods:

- The IAX2 channel description passed by the dial() application.
- An entry with type=peer or type=friend in the iax.conf file.
- A combination of both methods.

#### Connecting two Asterisk servers using RSA keys

It is possible to use IAX with strong authentication using asymmetric RSA keys. According to the source code (res_krypto.c), Asterisk uses RSA keys with an SHA-1 algorithm for message digests instead of the weaker MD5. Below is a step-by-step guide for setting up two servers using RSA keys.

##### Configuring the server for the branch

Step 1: Generate the RSA keys in the branch server

```
astgenkey -n
```

When asked, use the key name branch. We have used the parameter –n to avoid passing a passphrase whenever Asterisk reinitializes. If you want to improve the security, don’t use the –n and start Asterisk with asterisk -i Step 2: Copy the keys to the directory /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

Step 3: 公開鍵をHQサーバーにコピーする

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

ステップ4: ブランチサーバーの iax.conf ファイルを編集します。

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

ステップ8: ブランチサーバーの extensions.conf ファイルを設定する

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### 本部用サーバの設定

ステップ 1: HQ サーバで RSA 鍵を生成する

```
astgenkey -n
```

When asked use the key name hq. Step 2: Copy the keys to the directory /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

ステップ3：公開鍵をBRANCHサーバーにコピーする

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

ステップ4: HQサーバーでiax.confファイルを設定する

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

ステップ10: HQサーバーで extensions.conf ファイルを設定する。

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### IAX2 暗号化

IAX は、対称鍵である 128 ビットブロック暗号 AES（Advanced Encryption Standard）を使用した通話暗号化をサポートしています。IAX トランク間で暗号化を有効にするのは非常に簡単です。ファイル iax.conf では次のように使用します：

```
encryption=yes
```

暗号化を強制するには:

```
forceencryption=yes
```

古いバージョンとの互換性を保証するため、キーのローテーションを無効にする必要がある場合があります。

```
keyrotate=no
```

### IAX2 デバッグコマンド

以下は、Asterisk の最も重要なトラブルシューティング用コンソールコマンドのいくつかです。

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

この出力を見て、通話の開始と終了を特定します。poke と pong パケットを使用して取得した遅延とジッターの情報を確認します。これらのパケットは “iax2 show netstats” コマンドの出力を作成するのに役立ちます。

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

デバッグをオフにするには、次を使用します:

```
vtsvoffice*CLI>iax2 no debug
```

### Summary

この章では IAX プロトコルの長所と短所をレビューしました。ソフトフォンや 2 台の Asterisk サーバ間のトランクなど、いくつかのシナリオで IAX がどのように機能するかを示しました。トランクモードでは、1 つのパケットに複数の通話を載せることで帯域幅を節約できます。最後に、ステータスを確認したりプロトコルをデバッグしたりするために使用できるコンソールコマンドを学びました。

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

Step 2: Configure the [peer] on sip.conf Create an entry of peer type to the desired provider to simplify Asterisk’s dialing.

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

ステップ3: ダイヤルプランでプロバイダーへのルートを作成します プロバイダーへの宛先ルートとして 010 を選択します。プロバイダー内で #610000 をダイヤルするには、単に 010610000 とダイヤルしてください。

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### プロバイダーシナリオ固有のSIPオプション

以下の解説では、VoIPプロバイダーへの接続のために sip.conf ファイルに設定されたオプションの詳細を検討します。

```
register=>username:password@hostname/4100
```

sip.conf ファイルに登録された instruction は、プロバイダーへの登録に使用されます。register トランザクションは name と secret で認証されます。スラッシュ（“/”）を使用して、着信呼び出し用の extension を指定することができます。技術的には、その extension は SIP リクエストの “Contact” ヘッダー フィールドに配置されます。登録動作は、特定のパラメータによって制御できます。

```
registertimeout=20
registerattempts=10
```

To check if registration was successful, the legacy console command was `sip show registry`. On Asterisk 22 the equivalent command is `pjsip show registrations` (outbound registrations) and `pjsip show endpoints` for endpoint status.

The parameter “username” is used in the authentication digest. The digest is computed using username, secret, and realm:

```
username=username
```

ホストはVoIPプロバイダーのアドレスまたは名前を定義します。

```
host=hostname
```

Fromuser と Fromdomain パラメータは、認証の際に必要になることがあります。これらのパラメータは SIP の From ヘッダーフィールドで使用されます。

```
fromuser=username
fromdomain=hostname
```

VoIP プロバイダーに接続する際には認証情報が必要です。最初の INVITE の後、プロバイダーは「407 Proxy Authentication Required」というメッセージを送信します。続く INVITE メッセージで認証情報を提供します。着信呼び出しの場合、Asterisk サーバーはプロバイダーに対して認証情報を要求します。明らかに、プロバイダーは Asterisk サーバー用の有効な認証情報を持っていません。`insecure=invite` を使用すると、Asterisk に「407 Proxy Authentication Required」をプロバイダーに送らず、着信呼び出しを受け入れるよう指示します。また、`insecure=port,invite` を使用すると、ポート番号を一致させずに IP アドレスだけでピアを照合できます。

```
insecure=invite, port
```

### SIP (sip.conf) を使用して 2 つの Asterisk サーバーを接続する

SIP を使用して 2 台の Asterisk ボックスを相互接続できます。この設定に進む前にダイヤルプランに注意を払うことが重要です。ユーザーは通常、最小限の手間で他の PBX と接続したいと考えます。ここでの考え方は、他の PBX に接続するために拡張番号だけを使用することです。Step 1: Edit the sip.conf file in server A:

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

ステップ2: server B の sip.conf ファイルを編集します:

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

![SIP を使用して 2 台の Asterisk サーバーを接続: サーバー A（エクステンション 4400/4401）とサーバー B（エクステンション 4500/4501）が SIP シグナリングを交換し、各 PBX のユーザーが相手側にダイヤルできるようにする](../images/07-sip-and-pjsip-fig08.png)

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

ステップ3: サーバーAの extensions.conf ファイルを編集する:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

ステップ 4: サーバー B の extensions.conf ファイルを編集します:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk ドメインサポート (sip.conf)

SIP プロトコルはインターネットアーキテクチャに従います。SIP を設定する前に最初に行うべきことは、DNS サーバーを正しく設定することです。SIP 環境では、任意の SIP プロキシに所在するユーザーへ発信でき、他のユーザーもあなたの SIP Uniform Resource Identifier (URI) を使用してあなたに発信できます。SIP 用の DNS サーバーを設定するには、DNS サーバーに SRV レコードを追加する必要があります。

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

DNS の設定が完了したら、SIP ユーザー、SIP 電話、または電話内線を指す URI を使用できます。SIP URI はメールアドレスに似た形式です（例: sip:chuck@yourpartnerdomain.com）。SIP URI を使用すれば、ある SIP 電話から別の SIP 電話へ電話をかける際に電話番号は不要です。外部ユーザーに発信するには、以下に示すような文を使用します。

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Certain parameters can control domain behavior.

```
srvlookup=yes
```

このパラメータはアウトバウンドコールで DNS SRV ルックアップを有効にします。このパラメータを使用すると、ドメインに基づく SIP 名を使用して電話をダイヤルすることが可能です。

```
allowguest=yes
```

このパラメータは、外部からの INVITE を認証なしで処理できるようにします。呼び出しは、general セクションまたは domain ステートメントで定義されたコンテキスト内で処理されます。**Warning:** general セクションで PSTN へのアクセス権を持つコンテキストを定義すると、外部ユーザーが PBX 経由で PSTN にダイヤルできてしまいます。この場合、料金が発生します。general セクションで定義されたコンテキストには、必ず自分の内線だけを許可してください。

![ドメインで他の SIP サーバーに接続: youdomain.com と yourpartnerdomain.com が SIP シグナリングを交換し、lee や bruce といったユーザーが SIP URI を使用して chuck や norris に発信できるようにする](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

The domain コマンドを使用すると、Asterisk 内で複数のドメインを扱うことができます。特定のドメインからの呼び出しは、特定のコンテキストへと誘導されます。

```
;autodomain=yes
```

このパラメータは、許可されたドメインにローカル IP とホスト名を含めます。

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

このセクションでは、レガシー SIP チャネルの高度なパラメータ（プレゼンス、コーデック選択、DTMF オプション、QoS パケットマーキングなど）について説明します。**概念**（BLF/プレゼンス、コーデック交渉、DTMF モード、DSCP マーキング）は PJSIP にも引き継がれますが、ここに示す `sip.conf` パラメータ名は Asterisk 22 には **存在しません**。PJSIP では、DTMF モードはエンドポイントで `dtmf_mode=` と設定し、コーデックは `allow=`/`disallow=` で設定します。

#### SIP Presence

SIP プレゼンスは Asterisk で部分的に実装されています。Asterisk は、チャンネルの状態に応じて SUBSCRIBE や NOTIFY などのリクエストをサポートしますが、SIP メソッド PUBLISH はサポートしていません。つまり、チャンネルの状態（ビジー、アイドル、リング）をサブスクライブすることはできますが、「離席中」や「取り込み中」などの情報をパブリッシュすることはできません。プレゼンスで最も一般的なシナリオはビジーランプフィールド（BLF）で、各エクステンションやトランクに対してランプを用いた KS システムの動作をシミュレートします。SIP プレゼンス用パラメータ:

- allowsubscribe=yes: SIP サブスクリプションメソッドを許可する
- subscribecontext=sip_subscribers: ヒントを検索するコンテキスト
- notifyring=yes: リング時に SIP NOTIFY を送信する
- notifyhold=yes: ホールド時に SIP NOTIFY を送信する
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): カウンタをピア側のみに適用する
- callcounter=yes: デバイスでコールカウンタを有効にする
- busylevel=1: デバイスをビジーとみなすコール数の閾値

例: ステップ 1: SIP プレゼンスのテストはそれほど難しくありません。まず、sip.conf と extensions.conf のファイルを設定します。

In the file sip.conf

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

Step 2: Now configure the softphone to use presence. We will show you how to configure the SipPulse Softphone.

- Sequence: right-click->SIP Account Settings->Properties->Presence
- Change the presence model from peer-to-peer to presence agent, which will make the softphone subscribe Asterisk for SIP events.

Step 3: Add the contact to other softphones. In this example, the SipPulse Softphone is account 2000, so we will add a contact for account 2001. Sequence: Open the right panel (presence panel in the softphone)->Click in Contacts->Add a contact. Fill the name 2001. Display as 2001 and don’t forget to check the box Show this contact’s availability.

Step 4: Now call extension 2001 and check the status of the phone in the right panel of the softphone. Use the console command `core show hints` to see the presence status changing in the server (in legacy chan_sip, `sip show inuse` showed how many calls you had on each line). On Asterisk 22, use `pjsip show endpoints` to inspect endpoint and channel state. The presence/BLF status appears in the softphone's contacts or BLF panel — exactly how it is shown depends on the client.

#### Codec configuration

Codec configuration is simple and straightforward. You can set the words allow and disallow in the [general] section or peer/user section. The best practice is to standardize the codec to avoid transcoding, which is processor intensive. Please use the same codec for messages and prompts.

```
[general]
disallow=all
allow=g729
```

#### DTMF オプション

特定の場面では、voicemail や interactive voice response (IVR) といったアプリケーションに数字を渡す必要があります。DTMF を正しく渡すことが重要です。DTMF を渡す最も簡単な方法は inband と呼ばれます。これは sip.conf ファイルの [general] セクションまたは peer/user セクションで設定します。`dtmfmode=inband` を設定すると、DTMF トーンはオーディオチャンネル内の音として生成されます。この方法の主な問題は、g729 などのコーデックでオーディオチャンネルを圧縮すると、音が歪み、DTMF トーンが正しく認識されなくなることです。`dtmfmode=inband` を使用する予定がある場合は、g.711 コーデック（ulaw および alaw）を使用してください。

```
dtmfmode=inband
```

別のアプローチとして、RTP パケット内の名前付きイベントとして DTMF トーンを渡すことができる RFC2833 を使用する方法があります。

```
dtmfmode=rfc2833
```

最後に、RTP パケットの代わりに SIP パケット内で DTMF 桁を送ることができます。この方法は RFC3265（シグナリングイベント）および RFC2976 で定義されています。

```
dtmfmode=info
```

Following the release of version 1.2, it is now possible to use:

```
dtmfmode=auto
```

This tries to use the RFC2833; if it is not possible, use band tones.

#### Quality of service (QoS) marking configuration

QoS は音声品質を担保するための技術群です。QoS は帯域幅、遅延、ジッターを低減するように実装されます。主な QoS 機能はパケットスケジューリング、フラグメンテーション、ヘッダー圧縮です。QoS はスイッチやルーターで実装され、Asterisk 自体が実装するわけではありません。ただし、Asterisk はパケットにマークを付けて優先的に配信できるようにすることで、ルーターやスイッチを支援できます。マーク付けは RFC 2474 および RFC2475 で定義された差分サービスコードポイント (DSCP) を使用して行われます。

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

Starting from version 1.4, you can specify different codes for signaling (SIP), audio (RTP), and video (RTP).

### SIP authentication (sip.conf)

When legacy `chan_sip` received a SIP call, it followed the rules described in the following diagram. Three parameters played an important role in SIP authentication. On Asterisk 22, authentication is configured instead with PJSIP `auth` objects (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenced by an endpoint, and IP access control is done with `permit=`/`deny=` on the endpoint or via an `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

このパラメータは、対応するピアが存在しないユーザーが名前とシークレットなしで認証できるかどうかを制御します。このパラメータについては、ドメインサポートのセクションで説明しました。

```
insecure=invite,port
```

When we use insecure=invite, Asterisk does not generate the message “407 Proxy Authentication Required”. Without this message, the user can make a call without authentication. This is often used to connect to VoIP service providers. The calls coming from the VoIP service provider are usually not authenticated。

```
autocreatepeer=yes/no
```

このコマンドは Asterisk が SIP プロキシに接続されている場合に使用されます。各通話ごとにピアを動的に作成します。このオプションを有効にすると、任意の UAC が Asterisk サーバーに接続できるようになります。SIP プロキシへの IP 接続を制限することが重要です。SIP プロキシはその代わりにアクセス制御を行います。ピアの設定は一般的なオプションと SIP パケットの “Contact” ヘッダー フィールドに基づいて行われます。警告: これを使用すると Asterisk が完全に開放されるため、極めて注意して使用してください。

```
secret=secret, remotesecret=secret
```

このパラメータは認証用のシークレットを設定します。インバウンドリクエストには `secret` を、アウトバウンドリクエストには `remotesecret` を使用します。テキストファイルにシークレットを記載したくない場合は、シークレットの代わりにハッシュを含める `md5secret` を使用できます。`MD5` シークレットを生成するには、次のコマンドを使用できます:

```
echo -n "username:realm:secret" |md5sum
```

次に、以下の文を使用します：

```
md5secret=0b0e5d467890....
```

Warning: Do not forget to use the –n parameter; the carriage return will be used in the md5 computation.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

上記のステートメントはすべてのIPアドレスを拒否し、UAC をローカルネットワーク (192.168.1.0/24) のみから許可します。

#### RTP オプション

いくつかの RTP パラメータを制御することが可能です。

```
rtptimeout=60
```

This terminates calls without RTP activity for more the 60 seconds when not in hold.

```
rtpholdtimeout=120
```

This terminates calls without RTP activity even on hold (should be bigger than rtptimeout).

### SIP NAT traversal (sip.conf)

The NAT *theory* (the four NAT types, the Contact-header problem, keep-alives, and forcing media through the server) is protocol-level and is covered in the *SIP & PJSIP in depth* chapter. The `sip.conf` parameters shown here (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) are **legacy chan_sip** and were removed in Asterisk 21+. On PJSIP these map to transport/endpoint settings such as `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address`, and `local_net=` on the transport, plus `qualify_frequency=` on the AOR.

In legacy chan_sip, the parameter `nat` had five options:

- nat = no — Do no special NAT handling other than RFC3581
- nat = force_rport — Pretend there was an rport parameter even if there wasn't
- nat = comedia — Send media to the port Asterisk received it from regardless of where the SDP says to send it.
- nat = auto_force_rport — Set the force_rport option if Asterisk detects NAT (default)
- nat = auto_comedia — Set the comedia option if Asterisk detects NAT

When you put the statement “nat=force_rport” in the sip.conf file, you are telling Asterisk to ignore the address contained in the “Contact” header field of the SIP header and use the source IP address and port in the packet’s IP header and also to send the media back to the address from where it was received ignoring the content of the SDP header.

```
nat=force_rport,comedia
```

NATマッピングを開いたままにしておく必要があります。NATがタイムアウトすると、AsteriskはUACにインビットを送信できません。UACは発信はできても受信できません。以下のステートメントを使用してNATを開いたままにできます。

```
qualify=yes
```

Qualify は定期的に OPTIONS メソッドを使用した SIP パケットを送信し、NAT を開いたままに保ちます。Qualify は 60 秒ごとに OPTIONS を送信し、ホストに到達できない場合は 10 秒ごとに送信します。`sip show peers` を使用すると、ピアのレイテンシを確認できます。ユーザーの NAT が対称型の場合、ある UAC から別の UAC へ直接パケットを送ることはできません。その場合は、次のように RTP を Asterisk 経由に強制する必要があります。

```
directmedia=no
```

#### Asterisk behind NAT (sip.conf)

これまでのシナリオは、Asteriskサーバーが外部（有効な）インターネットアドレスを持っていることを前提としていました。Asteriskサーバーがファイアウォール背後のNAT環境で実装されていることもあります。この場合、追加の設定が必要です。

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. ファイアウォールを設定し、UDPポート5060をAsteriskサーバーへ静的にリダイレクトします。
2. ファイアウォールを設定し、UDPポート10000から20000までを静的にリダイレクトします。

開くポート数を制限したい場合は、`rtp.conf`ファイルを編集してRTPポート範囲を変更できます。別の方法として、SIPプロトコルをサポートするインテリジェントファイアウォールを使用し、RTPポートを動的に開くことも可能です。

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

ステップ3: Asterisk を設定し、外部アドレスを SIP パケットのヘッダーフィールド（Session Description Protocol (SDP) を含む）に含めます。次の 2 つのステートメントを sip.conf ファイルに追加することで実現できます。

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

最初のパラメータ `externaddr` は、外部宛先向けの SIP ヘッダーに外部 IP アドレスを含めるよう Asterisk に指示します。2 番目のパラメータ `localnet` は、外部アドレスと内部アドレスを区別できるようにします。必要に応じて、サーバーが DHCP アドレスを使用している場合は Dynamic DNS と組み合わせて `externhost` を使用できます。

### SIP dial strings (chan_sip)

以下に示す `SIP/...` ダイヤルストリング技術は、削除された chan_sip ドライバです。Asterisk 22 では代わりに `PJSIP/...` 技術を使用します — 例として `Dial(PJSIP/2000)` や `Dial(PJSIP/${EXTEN}@provider)` が挙げられます。形式と意味はそれ以外は同様です。

レガシー SIP 宛先を呼び出すには、さまざまなダイヤルストリングを使用できます。

```
SIP/peer
```

- ; sip.confで定義されたピアが必要です

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

例としては:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migrating a legacy chan_sip system to PJSIP

Because `chan_sip` was removed in Asterisk 21 and is gone in Asterisk 22, any
existing `sip.conf` deployment must be migrated to PJSIP. The biggest conceptual
shift is that a single `sip.conf` `[peer]` or `[friend]` is split into several
PJSIP objects, each with a `type=`: an **endpoint** (call/codec/media settings),
one or more **aor** objects (where the device can be reached / registration),
an **auth** object (credentials), and a shared **transport** (the listening
socket, NAT addresses). The following table maps the most common concepts.

| Legacy sip.conf concept | PJSIP equivalent (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (referenced via `auth=` and `aors=`) |
| `type=friend` / `type=peer` / `type=user` | a single `type=endpoint` (PJSIP has no friend/peer/user distinction) |
| `host=dynamic` (device registers) | `type=aor` with `max_contacts=1`; the device REGISTERs to update its contact |
| `host=<ip/hostname>` (static) | `type=aor` with a static `contact=sip:host:port` |
| `register=>user:secret@host/ext` (outbound) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` on the endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` on the endpoint (same syntax) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — also `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` on the endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (seconds) on the **aor** |
| `externaddr=` | `external_media_address=` and `external_signaling_address=` on the **transport** |
| `localnet=` | `local_net=` on the **transport** |
| `insecure=invite` (provider, no auth) | omit `auth=`/`outbound_auth=` and use `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (use with care) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (and `cos_audio` / `cos_video`) on the endpoint |

A registering extension that looked like this in legacy `sip.conf`:

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

Asterisk 22 の `pjsip.conf` では次のようになります：

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

### sip_to_pjsip.py 変換スクリプト

Asterisk はヘルパースクリプト **`sip_to_pjsip.py`** を提供しており、既存の`sip.conf`を読み取り、`pjsip.conf`を生成します。スクリプトは /etc/asterisk ディレクトリで直接実行できます。このユーティリティは Asterisk のソースツリー内の`contrib/scripts/sip_to_pjsip/`にあり、`${PATH_TO_ASTERISK_SOURCE}`は Asterisk ソースファイルが配置されているパス（通常は /usr/src/asterisk-22.x.y/）です。

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

If you run it with the `--help` option you will see its options:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

It also accepts optional positional arguments — `[input-file [output-file]]`,
defaulting to `sip.conf` and `pjsip.conf` in the current directory.

Treat its output as a **starting point**: review every generated object,
especially transports, NAT settings, and codec lists, and test thoroughly before
going to production.

Let’s migrate the sip.conf in our companion labs at VoIP School Blackbelt (voip.school)

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
register=>1020:supersecret@sip.flagonc.com:5600/9999
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
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
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
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
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
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
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
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

While the conversion seems ok, we can see that some elements such as qualify=yes cannot be mapped directly. To fix you have to add to the aor section the command qualify_frequency=time in seconds. Example below.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

完全な PJSIP 設定は *SIP & PJSIP in depth* 章で取り上げられており、docs.asterisk.org の公式ドキュメントでもチャンネルの全容がカバーされています。voip.school の補足ラボでは、ラボ 5 で学んだことを実践できます。

## Summary

この章では、現在の純粋な VoIP 展開よりも前に登場したチャネル技術を取り上げ、Asterisk 22 が依然としてサポートしているものをまとめました。**アナログ** 回線や電話が DAHDI の **FXO/FXS** インターフェースを介して接続される方法、**デジタル TDM** リンク（E1/T1 および ISDN PRI/BRI）のプロビジョニング方法、そして **IAX2**（`chan_iax2`）が依然として効率的で NAT フレンドリーなサーバー間トランクとして機能するが、現在は完全にレガシーとなっていることを確認しました。また、廃止された **`chan_sip`** ドライバとその `sip.conf` 構文（古いシステムで目にすることはあるが、Asterisk 22 には存在しない）を再確認し、概念マッピング表と `sip_to_pjsip.py` スクリプトを用いてそのようなシステムを PJSIP に移行する手順を学びました。経験則としては、この章の内容は実際のハードウェアや既存のレガシーシステムが必要とする場合にのみ使用し、すべての新規構築は IP 上の PJSIP を選択すべきです。

## Quiz

1. Regarding the two analog Foreign eXchange interfaces, mark the correct statements (choose all that apply):
   - A. An FXO interface connects to the public switched telephone network (PSTN) central office and draws dial tone from it.
   - B. An FXS interface provides dial tone and ringing power to a standard analog phone, fax, or modem.
   - C. An FXS interface is the correct way to connect Asterisk to a telco line.
   - D. An FXO interface can also be connected to an extension port of a legacy PBX.
2. Supervision signaling on an analog line includes which of the following (choose all that apply)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, pops, and noise on a DAHDI analog card are most often caused by:
   - A. The way Asterisk was compiled
   - B. PCI interrupt conflicts
   - C. An incorrect SIP codec
   - D. A missing dial plan
4. For precise billing on analog channels you must detect exactly when the far end answers. Which feature do you activate on Asterisk (and request from the telco) to do this?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial-tone generation
5. The DAHDI hardware is independent of Asterisk: the physical card is configured in `/etc/dahdi/system.conf`, while `chan_dahdi.conf` defines the Asterisk channels, not the hardware itself.
   - A. True
   - B. False
6. Regarding digital trunk capacity and signaling, mark the correct statements (choose all that apply):
   - A. An E1 trunk carries 30 voice channels and a T1 trunk carries 24.
   - B. An ISDN PRI uses 30B+D on an E1 and 23B+D on a T1.
   - C. ISDN is an example of CCS signaling, while MFC/R2 is an example of CAS signaling.
   - D. T1 is the digital trunk most commonly used in Europe and Latin America.
7. Which utility automatically detects DAHDI cards and generates `/etc/dahdi/system.conf` and `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. When migrating a legacy `sip.conf` `[friend]` to PJSIP, a single block must be split into several objects. Which set of PJSIP `type=` objects normally replaces one registering `[friend]`?
   - A. `type=endpoint`, `type=aor`, and `type=auth`
   - B. `type=peer` and `type=user`
   - C. `type=sip` only
   - D. `type=channel` and `type=device`
9. What is the main practical advantage of using IAX2 trunk mode between two Asterisk servers?
   - A. It encrypts every call with TLS by default
   - B. It carries several calls under a single header, saving bandwidth
   - C. It removes the need for any codec
   - D. It allocates a separate UDP port per call for better quality
10. RSA keys can be used for IAX2 authentication. Which key must you keep secret, and which do you give to the other server?
    - A. Keep the public key secret; share the private key
    - B. Keep the private key secret; share the public key
    - C. Keep the shared key secret; share the private key
    - D. Both keys must be shared

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
