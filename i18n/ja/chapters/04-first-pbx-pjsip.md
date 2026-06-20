# PJSIPで最初のPBXを構築する

この章では、基本的な Asterisk PBX の設定方法を学びます。ここでの主な目的は、PBX を初めて起動させ、エクステンション間でダイヤルできること、メッセージを再生しながらダイヤルできること、そして単一のアナログまたは SIP トランクへダイヤルできることを確認することです。この章の狙いは、できるだけ早く Asterisk を稼働させることです。この作業を完了すると、以降の章でより詳細な設定に踏み込むための十分な基礎が身につきます。

## Objectives

この章の終わりまでに、次のことができるようになります：

- 設定ファイルを理解し、編集できること；
- SIP ベースのソフトフォンをインストールできること；
- SIP トランクをインストールし、設定できること；
- アナログ接続をインストールし、設定できること；
- エクステンション間でダイヤルできること；
- 電話と外部宛先間でダイヤルできること；および
- オートアテンダントを設定できること。

## 設定ファイルの理解

Asterisk は /etc/asterisk にあるテキスト形式の設定ファイルで制御されます。ファイル形式は Windows の「.ini」ファイルに似ています。セミコロンはコメント文字として使用され、記号「=」と「=>」は同等で、スペースは無視されます。

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk は「=」と「=>」を同じように解釈します。構文の違いはオブジェクトと変数を区別するために使用されます。変数を宣言したいときは「=」を、オブジェクトを指定したいときは「=>」を使用してください。構文はすべてのファイルで同じですが、以下で説明するように 3 種類の文法が使用されます。

## Grammars

| Grammar | How the object is created | Conf. file | Example |
|---------|---------------------------|------------|---------|
| Simple Group | All in the same line | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Option Inheritance | Options are defined first, the object inherits the options | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Complex Entity | Each entity receives a context | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Simple Group

`extensions.conf`と`voicemail.conf`で使用されるシンプルグループ形式は、最も基本的な文法です。各オブジェクトは同じ行でオプションとともに宣言されます。例:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

この例では、オブジェクト1はオプションop1、op2、op3で作成され、オブジェクト2はオプションop1、op2、op3で作成されます。

### Object options inheritance grammar

この形式は `chan_dahdi.conf` と `agents.conf` で使用され、数多くのオプションが利用可能で、ほとんどのインターフェースとオブジェクトが同じオプションを共有します。通常、1つまたは複数のセクションにオブジェクトとチャネルの宣言があります。オブジェクトへのオプションはオブジェクトの上部で宣言され、別のオブジェクトに変更できます。この概念は理解しにくいですが、使用は非常に簡単です。例:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

最初の2行は、オプションop1とop2の値をそれぞれ “bas” と “adv” に設定します。オブジェクト1がインスタンス化されると、オプション1は “bas”、オプション2は “adv” で作成されます。オブジェクト1を定義した後、オプション1を “int” に変更します。次に、オプション1が “int”、オプション2が “adv” のオブジェクト2を作成します。

### Complex entity object

この形式は `pjsip.conf`、`iax.conf`、および多数のオプションを持つ他の設定ファイルで使用されます。通常、この形式は大量の共通設定を共有しません。各エンティティはコンテキストを受け取ります。時には、全体設定用の `[general]` のような予約コンテキストが存在します。オプションはコンテキスト宣言内で宣言されます。例:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

エンティティ `[entity1]` はオプションop1とop2に対してそれぞれ “value1” と “value2” の値を持ちます。エンティティ `[entity2]` はオプションop1とop2に対してそれぞれ “value3” と “value4” の値を持ちます。

## Options to build a LAB for Asterisk

PBX を構成するには、基本的なハードウェアがいくつか必要です。高価でも難しいでもありませんが、検討すべき選択肢があります。必要なのは電話機 2 台と公衆ネットワークへの接続だけです。ラボを作成する際に可能なオプションや組み合わせについて、以下で説明します。

### Option 1: Complete LAB

Complete LAB では、利用可能なすべてのシナリオをテストし、ATA、IP 電話、ソフトフォンなどのソリューションを比較できます。アナログおよび SIP トランクについても学べます。必要なものは次のとおりです。

- A SIP analog telephone adapter (ATA)
- An IP phone
- A dedicated server for Asterisk
- A workstation with a softphone
- An analog interface card with at least two interfaces (1 FXO and 1 FXS)
- A VoIP provider account

### Option 2: Economy LAB

Economy LAB では、少し簡素化します。通常は IP 電話よりも安価な ATA と、非常に安価な単一 FXO カードを使用します。サーバーに直接接続されたアナログ電話は使用できませんが、実務上はあまり一般的ではありません。必要なものは次のとおりです。

- A SIP analog telephone adapter (ATA)
- A dedicated server for Asterisk
- A workstation for the softphone
- An analog interface card with 1 FXO
- An account with a VoIP provider

### Option 3: Super economy lab

3 番目の LAB は、学生自身のノートブック上の仮想化サーバーを使用します。このモデルの問題は UDP ポートの競合です。Asterisk サーバーとソフトフォンが同じポートにアクセスしようとし、Asterisk がアドレスポートにバインドできなくなることがあります。もう一つの課題は通話品質で、仮想環境は Asterisk のようなリアルタイムアプリケーションには適していません。サーバーとワークステーションには無料のソフトフォンを使用し、SIP プロバイダーへのトランク接続を行います。必要なものは次のとおりです。

- A laptop running a softphone
- A virtual machine (VirtualBox, VMware, or similar) to install Asterisk
- An account with a VoIP provider

## インストールシーケンス

インストールシーケンスを理解しやすくするために、Asterisk のインストールと設定に必要な手順の流れをまとめました。

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. エクステンションの設定
   - a. SIP エクステンション (ATA、ソフトフォン、IP 電話)
   - b. IAX エクステンション
   - c. FXS エクステンション
2. トランクの設定
   - a. SIP トランクの設定
   - b. FXO トランクの設定
3. 基本的なダイヤルプランの構築
   - a. エクステンション間のダイヤル
   - b. 外部宛先へのダイヤル
   - c. オペレーターエクステンションでの着信受信
   - d. オートアテンダントでの着信受信

## 拡張機能の設定

拡張機能は SIP、IAX、または FXS ポートに接続されたアナログ電話です。拡張機能を設定するには、チャネルに関連する設定ファイル（pjsip.conf、iax.conf、chan_dahdi.conf）を編集します。

### SIP 拡張機能

Asterisk 22 では、PJSIP（`res_pjsip`スタック、`/etc/asterisk/pjsip.conf`で設定） が SIP チャネルドライバです。エンドポイントごとに複数のトランスポートをサポートし、積極的にメンテナンスされており、プラットフォームに同梱されている唯一の SIP ドライバです。（元の`chan_sip`ドライバは Asterisk 21 で削除されました — 古い設定を移行する必要がある場合は *Legacy channels* 章をご参照ください。）

ここでの目的はシンプルな PBX を設定することです。（続く章では、すべての詳細を含む完全な SIP/PJSIP セッションを提供します。）PJSIP は`/etc/asterisk/pjsip.conf`で設定され、SIP 電話や VoIP プロバイダに関するすべてのパラメータを保持します。SIP クライアントは、発信・受信できるようになる前に設定が必要です。

#### トランスポート

PJSIP では、リスナー設定（バインドアドレス、ポート、プロトコル）は`transport`オブジェクトに格納されます。Asterisk にはユーザー名推測に対する組み込み保護があり、未知のユーザーでも既知のユーザーでも同一の認証チャレンジを返し、同一 IP からの未認証リクエストは`[global]`オプション`unidentified_request_count`/`unidentified_request_period`でレート制限されます。トランスポートの主なオプションは次のとおりです。

- protocol: トランスポートプロトコル — `udp`、`tcp`、`tls`、`ws`、または`wss`。
- bind: リスナーがバインドするアドレスとポート。アドレスを`0.0.0.0`に設定すると、すべてのインターフェースにバインドされます。SIP ポートは UDP/TCP の場合デフォルトで 5060 です。

最小構成の UDP トランスポート:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Codec selection (`disallow`/`allow`) and the default `context` are configured on each `endpoint` (shown below), not on the transport. Anonymous/guest calls are handled by an `endpoint` named `anonymous`. Registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`.

#### SIP clients

After completing the transport section, it is time to set up the SIP clients. I would once again like to remind the reader that we will have an entire SIP/PJSIP chapter later in the book. For now, let’s concentrate on the basics and leave the details for later.

In PJSIP a SIP client is built from a set of related objects, tied together by name reference:

- `endpoint`: The call behaviour — codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.
- `auth`: The credentials. `username` is the SIP authentication user and `password` is the secret used to authenticate the device.
- `aor`: The "address of record" — where the endpoint can be reached. Either a static `contact=` (for a device at a fixed IP) or `max_contacts=` to allow the device to register dynamically.

Warning: Use strong passwords, with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for SIP are easily available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers.

Endpoint 6000 is a device at a fixed IP, so its AOR carries a static `contact` instead of allowing registration. Endpoint 6001 is a device that registers, so its AOR allows it to register (`max_contacts=1`):

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=digest
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP は `endpoint`、`auth`、および `aor` セクションが同じセクション名を共有することを許可します（例：上記の二つの `[6001]` ブロックは `type=` で区別されます）。多くの管理者は可読性のためにそれらにサフィックスを付けます（`[6001]`、`[6001-auth]`、`[6001]` aor）。登録するデバイスの場合、電話が登録するとコンタクトが動的に学習されるため、AOR は静的な `contact` を必要としません。

## IAX Extensions

`chan_iax2`は Asterisk 22 にまだ同梱されていますが、現在はレガシー扱いです。新規導入では SIP/PJSIP が推奨プロトコルです。

IAX エクステンションを作成することもできます。このプロトコルは Asterisk にネイティブに組み込まれており、本書の後半で専用の章を設けます。まずはこのプロトコルを使っていくつかエクステンションを作成しましょう。最初に設定するセクションである [general] には、いくつかのパラメータを設定します。主なオプションは次のとおりです。

- allow/disallow: 使用するコーデックを定義します。
- bindaddr: IAX2 リスナーがバインドするアドレスです。0.0.0.0（デフォルト）に設定すると、すべてのインターフェースにバインドします。
- context: クライアントセクションで変更しない限り、すべてのクライアントに適用されるデフォルトコンテキストを設定します。セキュリティ上の理由で dummy を使用しました。allowguest が yes に設定されている場合、認証されていないユーザーはこのコンテキストに入ります。
- bindport: 監視する IAX2 UDP ポート（デフォルト 4569）。
- delayreject: yes に設定すると、REGREQ または AUTHREQ に対する認証拒否の送信を遅延させ、ブルートフォース攻撃に対するセキュリティが向上します。
- bandwidth: high に設定すると、ulaw や alaw などの高帯域コーデックの選択が可能になります。

以下は iax.conf の [general] セクションのサンプルです。

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### IAX Clients

一般セクションの設定が完了したら、IAX クライアントを設定します。

- `[name]`: セクション名は IAX ピア/ユーザー名です。受信した IAX 接続は名前でこのセクションにマッチします。
- `type`: 接続クラス — `peer`、`user`、または `friend`:
  - `peer`: Asterisk がピアに対して発信します。
  - `user`: Asterisk がユーザーからの呼び出しを受信します。
  - `friend`: 両方向同時に行います。
- `host`: IP アドレスまたはホスト名です。最も一般的な値は `dynamic`で、デバイスが Asterisk に登録する際に使用されます。
- `secret`: ピアやユーザーを認証するためのパスワードです。

Warning: 少なくとも 8 文字以上で、英数字と記号を組み合わせた強力なパスワードを使用してください。メーリングリストにはハッキングされたサーバーの報告があり、IAX md5 ハッシュを対象としたブルートフォースクラックツールがスクリプトキディ向けに公開されています。電話料金詐欺は消費者やプロバイダーに数千ドルの損失をもたらします。例:

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Configuring the SIP devices

After defining the phones in the Asterisk configuration file, it is time to configure the phone itself. In this example, we will show how to configure a free softphone — the SipPulse Softphone (download it from https://www.sippulse.com/produtos/softphone). Check your device’s manual to understand the parameters of your phone. Step 1: Configure the phone to use the extension 6000. Execute the installation program. After the execution, open the account/SIP settings and add a new SIP account. Fill in the required information.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Confirm that your phone is registered using the console command `pjsip show endpoints` (or `pjsip show endpoint 6000` for detail; `pjsip show contacts` shows the registered AOR contacts). Repeat the configuration for the phone 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## IAX デバイスの設定

IAX2 はレガシープロトコルです（*Legacy channels* 章参照）。SipPulse Softphone は SIP のみ対応なので、IAX アカウントを登録することはできません。IAX2 をテストする必要がある場合は、まだ対応しているソフトフォンを使用してください。新しい IAX アカウントを作成します。

3. 新しい IAX アカウントを選択します。  
4. 6003 電話用の関連オプションと、必要に応じて 6004 用のオプションを入力します。  
5. 設定を保存し、`iax2 show peers` を使用して電話が登録されているか確認します。

重要: SIP 用に 1 つのアカウント、IAX 用に別のアカウントを使用してください。IAX と SIP の両方を同時に鳴らすようにシステムを構成したい場合は、ダイヤルプランのセクションでその方法を示します。

### PSTN インターフェースの設定

PSTN に接続するには、FXO（Foreign Exchange Office）インターフェースと電話回線が必要です。既存の PBX エクステンションを使用することもできます。FXO インターフェースを備えた電話インターフェースカードは複数のメーカーから入手可能です。この例では、DAHDI インターフェースカードのインストール方法を示します。

![FXS と FXO ポート: FXS ポートはアナログ電話を駆動（ダイヤルトーンとリングを供給）し、FXO ポートは Asterisk を電話会社回線に接続します.](../images/04-first-pbx-fig02.png)

### DAHDI を使用したアナログ回線

複数のメーカーから DAHDI 対応のアナログカードを購入できます。X100P は Digium の最初期カードの一つで、すでに生産終了しています。いくつかのメーカーは類似のクローンをまだ製造しています。X100P の価格に加えて、これらのカードと新しいマザーボード間でいくつかの問題が報告されているため、使用には注意が必要です。個人的には X100P は本番環境には適さないと考えています。DAHDI 対応のカードであればどれでも動作するはずです。DAHDI 開発チームのおかげで、インターフェースカードをほぼ自動的に検出・設定するツールが提供されています。DAHDI ドライバをインストールしたばかりの場合は、`make config` を実行し、マシンを再起動して自動的にロードされるようにしてください。以下のコマンドでカードの検出と設定が行えます。Step 1: ハードウェアを検出するには、次を使用します:

```
dahdi_hardware
```

Step 2: 設定には次を使用します:

```
dahdi_genconf
```

The command above will generate two files /etc/dahdi/system.conf and /etc/asterisk/dahdi-channels.conf. The default parameters for dahdi_genconf are usually fine, but you can change them in the file /etc/dahdi/genconf_parameters. By default, it will insert the lines (FXO) in the context from-pstn and the phones (FXS) in the context from-internal. Step 3: After running dahdi_genconf, in the last line of the file /etc/asterisk/chan_dahdi.conf insert the following line:

```
#include dahdi-channels.conf
```

Step 4: Edit the file /etc/dahdi/modules and comment for all the unused drivers. Reboot before proceeding and check if the channels are being recognized using:

```
*CLI> dahdi show channels
```

### PSTN へ VoIP プロバイダーを介して接続する

予算が非常に限られている場合、SIP トランクを設定して PSTN に接続することができます。これは PSTN に接続する最も手頃な方法です。世界中に何千もの VoIP プロバイダーが存在します。プロバイダーのいずれかに接続するには、いくつかのパラメータが必要です。パラメータは SIP プロバイダーから提供されます。

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

2 つのパラメータは自分で決定する必要があります。

- Extension to receive calls—in this case: 9999
- context: from-sip

PJSIP では、登録用 SIP トランクはエンドポイントに使用されるのと同じオブジェクトファミリーから構築され、明示的な `registration` と `identify` オブジェクトが追加されます。`registration` オブジェクトは Asterisk にプロバイダーへの登録を指示し、`identify` オブジェクトはプロバイダーの IP からのインバウンドトラフィックをエンドポイントにマッチさせます（PJSIP は送信元 IP によってインバウンド INVITE を認証します）、そして `outbound_auth` はアウトバウンドコールと登録のための認証情報を提供します。

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=digest
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

このトランクにアクセスするには、チャネル名`PJSIP/siptrunk`を使用します。 `dtmf_mode=rfc4733`設定はバンド外でDTMFを送ります（RFC 4733は古いRFC 2833に取って代わり、ペイロードは同一です）。 `identify`/`match`オプションはIPアドレス、CIDR、またはホスト名を受け付けますが、ホスト名は設定読み込み時に一度だけ解決されるため、IPが変わるプロバイダーの場合はシグナリングIPを明示的に列挙してください。 `pjsip show registrations`で登録を確認します。

## ダイヤルプランの紹介

ダイヤルプランは Asterisk の心臓部のようなものです。PBX へのすべての通話を Asterisk がどのように処理するかを定義します。ダイヤルプランは、Asterisk が従うべき命令リストを作る extension で構成されます。命令はチャネルやアプリケーションから受け取った数字によって発火します。Asterisk を正しく設定するには、ダイヤルプランを理解することが不可欠です。ダイヤルプランの大部分は /etc/asterisk ディレクトリにある extensions.conf ファイルに格納されています。このファイルはシンプルなグループ文法を使用し、4 つの主要概念があります。

- Extensions
- Priorities
- Applications
- Contexts

基本的なダイヤルプランを作成しましょう。この本の後続の章では、ダイヤルプランだけを扱う章を設けます。サンプルファイル (make samples) をインストールした場合、extensions.conf はすでに存在します。別名で保存し、空のファイルから始めてください。

## The structure of the file extensions.conf

extensions.conf ファイルはセクションに分かれています。最初は [general] セクション、次に [globals] セクションです。各セクションの開始は名前定義（例: [default]）で始まり、別のセクションが作成されるまで続きます。

### The section [general]

general セクションはファイルの先頭にあります。ダイヤルプランの設定を始める前に、ダイヤルプランの動作を制御する一般的なオプションを把握しておくと便利です。これらのオプションは次のとおりです。

- static and write protect: If `static=yes` and `writeprotect=no`, you can save the running dial plan back to disk with the CLI command:

```
*CLI> dialplan save
```

Warning: If you issue a `dialplan save` command from the CLI, you will lose any remarks and comments in the file.

- autofallthrough: If autofallthrough is set, then if an extension runs out of things to do, it will terminate the call with BUSY, CONGESTION, or HANGUP depending on Asterisk's best guess. This is the default. If autofallthrough is not set, then if an extension runs out of things to do, Asterisk will wait for a new extension to be dialed.
- clearglobalvars: If clearglobalvars is set, global variables will be cleared and reparsed into an dialplan reload or Asterisk reload. If clearglobalvars is not set, then global variables will persist through reloads and—even if deleted from the extensions.conf or one of its included files—they will remain set to the previous value.
- extenpatternmatchnew: Uses a faster pattern-matching algorithm, which helps noticeably when you have a large number of extensions. Defaults to no.
- userscontext: This is the context where the entries from the users.conf are registered.

### The section [globals]

[globals] セクションでは、グローバル変数とその初期値を定義します。ダイヤルプラン内では `${GLOBAL(variable)}` を使って変数にアクセスできます。Linux/Unix 環境の変数は `${ENV(variable)}` で参照可能です。グローバル変数は大文字小文字を区別しません。例としては次のようになります。

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

以下の例では、ダイヤルプラン内でグローバル変数を設定し、テストする方法を示しています。

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contexts

Context is the named partition of the dial plan. After the [general] and [globals] sections, the dial plan is a set of contexts in which each context has several extensions, each extension has several priorities, and each priority calls an application with several arguments.

![Asterisk call flow: every call arrives on a channel (IAX, SIP, and others) as an incoming call leg; the channel's context — set globally or per-channel in the channel config file — decides which context in extensions.conf processes the call before it leaves on the outgoing leg.](../images/04-first-pbx-fig03.png)

![Call processing: the `context=` defined for a channel (in chan_dahdi.conf or pjsip.conf) names the matching context in extensions.conf where the dial plan handles the call.](../images/04-first-pbx-fig04.png)

You can build a simple dial plan to reach other phones and the PSTN. However, Asterisk is much more powerful than that. Our objective is to teach you more details of what is possible in the dial plan.

## Extensions

従来の PBX では、内線は電話機やインターフェース、メニューなどに紐付けられますが、Asterisk では特定の内線番号または名前がトリガーされたときに実行されるコマンドのリストが「内線」として扱われます。コマンドは優先順位の順に処理されます。

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

内線はリテラル、標準、または特別のいずれかに分類できます。標準内線は数字または名前と文字 * と # のみで構成され、12#89* は有効なリテラル内線です。名前も内線マッチングに使用できます。内線は大文字小文字を区別します。ただし、同じ名前で大文字小文字が異なる内線を二つ作成することはできません。内線がダイヤルされると、最初の優先順位のコマンドが実行され、続いて優先順位 2 のコマンドが実行されます。これが呼び出しが切断されるか、あるいはコマンドが 1 を返して失敗を示すまで続きます。最後の優先順位が実行されたときの Asterisk の動作はパラメータ autofallthrough によって制御されます。この章の [general] セクションを参照してください。例:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

上記は、内線 123 がダイヤルされたときに処理される指示の一覧です。最優先はチャンネルに応答することです（チャンネルがリング状態にある場合、例えば FXO チャンネルで必要です）。次に優先されるのは、tt‑weasels というオーディオファイルを再生することです。3 番目の優先度はチャンネルを切断することです。別のオプションとして、発信者 ID に基づいて通話を処理することもできます。処理する発信者 ID を指定するには、/ 文字を使用します。例:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

この例は、発信者IDが100の場合にのみ、エクステンション123をトリガーし、以下のオプションを実行します。以下に示すパターンを使用しても同様に行うことができます。

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: maps an extension to a channel. It is used to monitor the channel state. It is used in conjunction with presence. The phone has to support it.

#### Patterns

You can use patterns and literals in the dial plan. Patterns are very useful for reducing the dial plan size. All patterns start with the “_” character. The following characters may be used to define a pattern. The figure identifies the patterns available for use with Asterisk.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Special extensions

Asterisk uses some extension names as standard extensions.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

Description:

- **s**: 開始。ダイヤルされた番号がない場合の呼び出し処理に使用されます。FXOトランクやメニュー内処理に便利です。
- **t**: タイムアウト。プロンプト再生後に通話が非アクティブのまま残ったときに使用されます。また、非アクティブな回線を切断するためにも使用されます。
- **T**: 絶対タイムアウト。`TIMEOUT(absolute)`ダイヤルプラン関数で通話制限を設定した場合、制限を超えるとTエクステンションに送られます。
- **h**: 切断。ユーザーが通話を切断した後に呼び出されます。
- **i**: 無効。コンテキスト内で存在しないエクステンションに呼び出したときにトリガーされます。これらのエクステンションを使用すると、CDRレコードの内容、特にダイヤルされた番号を含まないdstフィールドに影響を与える可能性があります。
- **o**: オペレーター。ユーザーがボイスメール中に「0」を押したときにオペレーターへ転送するために使用されます。

これらのエクステンションの使用は、課金レコード（CDR）の内容を変更する可能性があります。特に、dstフィールドにダイヤルされた番号が残りません。この問題を回避するには、dial()アプリケーションでオプションgを使用し、resetcdr(w) および/または nocdr() 関数の使用を検討してください。

## Variables

Asterisk PBX では、変数はグローバル、チャンネル固有、環境固有に分けられます。コンソールで変数の内容を確認するには NoOP() アプリケーションを使用します。グローバル変数またはチャンネル固有変数をアプリケーションの引数として渡すことができます。変数は次の例のように参照でき、varname は変数名です。

```
${varname}
```

変数名は文字で始まる英数字文字列で構成できます。グローバル変数名は大文字小文字を区別しません。ただし、システム変数（Asterisk が定義するものやチャンネルが定義するもの）は大文字小文字を区別します。したがって、変数 ${EXTEN} は ${exten} とは異なります。

### Global variables

グローバル変数は extensions.conf ファイルの [global] セクションで設定するか、アプリケーションを使用して設定できます。

```
set(Global(variable)=content)
```

### Channel-specific variables

チャンネル固有変数は set() アプリケーションで設定します。各チャンネルは独自の変数空間を持ち、異なるチャンネル間で変数が衝突することはありません。チャンネルがハングアップするとチャンネル固有変数は破棄されます。最も一般的に使用される変数は次のとおりです。

- ${EXTEN} 発信されたエクステンション
- ${CONTEXT} 現在のコンテキスト
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} 現在の発信者 ID
- ${PRIORITY} 現在のプライオリティ

その他のチャンネル固有変数はすべて大文字です。dumpchan() アプリケーションを使用すると、複数の変数の内容を確認できます。以下は dump-channel 変数の簡単な抜粋です。

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Dumpchan 出力:

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

上記のフィールドレイアウトは Asterisk 22 `DumpChan` の出力です（実際の `PJSIP/...` チャンネル名、`CallerIDNum`/`ConnectedLineID` フィールド、そして PJSIP チャンネルが埋める `Raw*`/`Transcode`/`BridgeID` 行）。従来のドライバとは異なり、PJSIP チャンネルは `SIPCALLID`/`SIPUSERAGENT` チャンネル変数を自動設定しません。対応する SIP の詳細は、`PJSIP_HEADER()` と `CHANNEL()` ダイヤルプラン関数で必要に応じて取得されます。たとえば、リモート RTP アドレスに対しては `${CHANNEL(pjsip,call-id)}`、`${PJSIP_HEADER(read,User-Agent)}`、`${CHANNEL(rtp,dest)}` が使用されます。

### Environment-specific variables

環境固有変数は、オペレーティングシステムで定義された変数にアクセスするために使用できます。ENV() 関数を使って環境固有変数を設定できます。例:

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

一部のアプリケーションはデータの入力・出力に変数を使用します。アプリケーションを呼び出す前に変数を設定したり、実行後に変数を取得したりできます。例: Dial アプリケーションは次の変数を返します。

- ${DIALEDTIME} -> チャンネルをダイヤルしてから切断されるまでの時間。
- ${ANSWEREDTIME} -> 実際の通話時間。
- ${DIALSTATUS} 通話のステータス: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> 通話に関するエラーメッセージ。

## Expressions

Expressions can be very useful in the dial plan. They are used to manipulate strings and perform math and logical operations.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

The expression syntax is defined as follows:

```
$[expression1 operator expression2]
```

Let’s suppose that we have a variable called “I” and we want to add 100 to the variable:

```
$[${I}+100]
```

When Asterisk finds an expression in the dial plan, it changes the entire expression by the resulting value.

### Operators

The following operators can be used to build expressions. It is important to observe operator precedence.

1. Parentheses “()”
2. Unary operators “! -“
3. Regular expression “: =~
4. Multiplicative operators “* / %”
5. Additive operators “+ -“
6. Comparison operators
7. Logical operators
8. Conditional operators

#### Math Operators

- Addition (+)
- Subtraction (-)
- Multiplication(*)
- Division (/)
- Modulus (%)

#### Logical Operators

- Logical “AND” (&)
- Logical “OR” (|)
- Logical Unary Complement (!)

#### Regular expression operators

- Regular expression matching (:)
- Regular expression exact matching (=~)

A regular expression is a special text string used to describe a search pattern. You can think of regular expressions as wildcards. Regular expressions are used to match a string to a pattern to check the matching. If the match succeeds and the regular expression contains at least one match, the first match is returned; otherwise, the result is the number of characters matched.

#### Comparison operators

The result of a comparison is 1 if the relation is true or 0 if it is false.

- = equal
- != not equal
- < less than
- > greater than
- <= less than or equal to
- >= greater than or equal to

### LAB. Evaluate the following expressions:

Put these expressions in your dial plan and use the NoOP() application to evaluate the expressions. Dial 9002 and examine the results in the Asterisk console. Use verbose 15 to show the results.

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## Functions

いくつかのアプリケーションは関数に置き換えられました。関数を使用すると、式だけでは実現できない、より高度な変数処理が可能になります。以下のコンソールコマンドを実行すると、関数の全一覧を確認できます。

```
*CLI> core show functions
```

文字列長: ${LEN(string)} は文字列の長さを返します

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

最初の操作では、システムは 5 を結果として示します（単語 “fruit” の文字数）。2 番目は 4 を返します（単語 “pear” の文字数）。サブストリング: “offset” パラメータで定義された位置から開始し、“length” パラメータで定義された長さのサブストリングを返します。オフセットが負の場合、文字列の末尾から右から左へ開始します。長さが省略または負の場合、オフセットから始まる文字列全体を取得します。

```
${string:offset:length }
```

例 #1: 複数のサブストリング

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

例 #2: 最初の 3 桁からエリアコードを取得

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

例 #3: 変数 ${EXTEN} からエリアコードを除いたすべての数字を取得

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### String concatenation

2 つの文字列を連結するには、単に続けて書くだけです。

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## アプリケーション

ダイヤルプランを構築するには、アプリケーションの概念を理解する必要があります。ダイヤルプラン内でチャンネルを処理するためにアプリケーションを使用します。アプリケーションは複数のモジュールで実装されています。利用可能なアプリケーションはモジュールに依存します。コンソールコマンドを使用して、すべての Asterisk アプリケーションを表示できます:

```
*CLI> core show applications
```

代わりに、次の例を使用して特定のアプリケーションの詳細を表示できます。

```
*CLI> core show application Dial
```

簡単なダイヤルプランを構築するには、いくつかのアプリケーションを知っている必要があります。より高度な例については、後の章で説明します。

![The handful of applications needed to build a simple dial plan: Answer (answer a channel), Dial (call another channel), Hangup (hang up a channel), Playback (play an audio file), and Goto (jump to a priority, extension, or context).](../images/04-first-pbx-fig09.png)

これらのアプリケーション（上記）を使用して、2 つの基本的な PBX 用のシンプルなダイヤルプランを作成します。

### Answer()

[Synopsis] Answers a channel if ringing [Description] Answer([delay]): If the call has not been answered, the application will answer it. Otherwise, it has no effect on the call. If a delay is specified, Asterisk will wait the number of milliseconds specified in ‘delay’ before answering the call.

### Dial()

The following description can be obtained by issuing the show application dial in the dial plan. For easy searching, it is reproduced below. The syntax for the Dial application is also shown below:

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

このアプリケーションは、指定された 1 つまたは複数のチャンネルに対して呼び出しを行います。要求されたチャンネルのいずれかが応答すると、発信元チャンネルがまだ応答していない場合は応答されます。これら 2 つのチャンネルはブリッジされた通話でアクティブになります。その他の要求されたチャンネルはすべて切断されます。タイムアウトが指定されていない限り、Dial アプリケーションは、呼び出されたチャンネルのいずれかが応答するか、ユーザーが切断するか、すべての呼び出しチャンネルがビジーまたは利用不可になるまで無期限に待機します。要求されたチャンネルが呼び出せない場合やタイムアウトが期限切れになった場合でも、ダイヤルプランの実行は続行されます。このアプリケーションは完了時に以下のチャンネル変数を設定します：

- DIALEDTIME - チャンネルをダイヤルしてから切断されるまでの時間です。
- ANSWEREDTIME - 実際の通話時間です。
- DIALSTATUS - 通話のステータスです: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

プライバシーおよびスクリーニングモードでは、呼び出し先が「Go Away」スクリプトに発信者を送ることを選択した場合、DIALSTATUS 変数は DONTCALL に設定されます。呼び出し先が発信者を「torture」スクリプトに送ることを希望した場合、DIALSTATUS 変数は TORTURE に設定されます。このアプリケーションは、発信元チャンネルが切断された場合、または通話がブリッジされてブリッジ内のいずれかの当事者が通話を終了した場合に、正常終了として報告します。オプションの URL は、チャンネルがサポートしている場合に呼び出し先に送信されます。OUTBOUND_GROUP 変数が設定されている場合、このアプリケーションによって作成されたすべてのピアチャンネルがそのグループに含まれます（例として）

```
Set(GROUP()=...).
```

以下の表は、アプリケーション Dial で最も頻繁に使用されるオプションのいくつかをまとめたものです。完全なリストについては、コンソールコマンド `core show application Dial` を使用してください。Asterisk 22 では、これらのオプションはチャンネルとタイムアウトからカンマで区切られます — 例として `Dial(PJSIP/2000,20,tTm)`。

| Option | Description |
|--------|-------------|
| `A(x)` | `x` をファイルとして使用し、呼び出された相手にアナウンスを再生します。 |
| `C` | この通話の CDR をリセットします。 |
| `d` | 通話が応答されるまでの間、発信ユーザーが 1 桁の内線番号をダイヤルできるようにします。その内線が現在のコンテキストに存在すればその内線へ、存在しなければ `EXITCONTEXT` 変数で定義されたコンテキストへ転送します。 |
| `D([called][:calling])` | 呼び出された相手が応答した後、通話がブリッジされる前に指定された DTMF 文字列を送信します。 `called` 文字列は呼び出された相手に、`calling` 文字列は発信側に送られます。どちらか一方だけでも使用可能です。 |
| `f` | 発信チャネルの発信者 ID を、ダイヤルプラン `hint` によりチャネルに関連付けられた内線に設定します。PSTN が任意の発信者 ID を許可しない場合に有用です。 |
| `g` | 宛先チャネルがハングアップした場合、現在の内線でダイヤルプランの実行を続行します。 |
| `G(context^exten^pri)` | 通話が応答された場合、発信側を指定されたプライオリティへ、受信側をプライオリティ+1 へ転送します。オプションで内線（または内線とコンテキスト）を指定でき、指定しない場合は現在の内線が使用されます。 |
| `h` | `*` DTMF 桁を送信することで、受信側がハングアップできるようにします。 |
| `H` | `*` DTMF 桁を送信することで、発信側がハングアップできるようにします。 |
| `L(x[:y][:z])` | 通話時間を `x` ミリ秒に制限し、残り `y` ミリ秒になると警告を再生し、`z` ミリ秒ごとに警告を繰り返します。下記の `LIMIT_*` 変数を参照してください。 |
| `m([class])` | 要求されたチャネルが応答するまで、発信側に保留音楽を提供します。特定の MusicOnHold クラスを指定できます。 |
| `r` | 発信側にリング音を示し、呼び出されたチャネルが応答するまで音声を送信しません。 |
| `S(x)` | 呼び出された相手が応答してから `x` 秒後に通話をハングアップします。 |
| `t` | `features.conf` で定義された DTMF シーケンスを送信することで、受信側が発信側を転送できるようにします。 |
| `T` | `features.conf` で定義された DTMF シーケンスを送信することで、発信側が受信側を転送できるようにします。 |
| `w` | `features.conf` で定義された DTMF シーケンスを送信することで、受信側がワンタッチ録音を有効にできます。 |
| `W` | `features.conf` で定義された DTMF シーケンスを送信することで、発信側がワンタッチ録音を有効にできます。 |
| `k` | `features.conf` で定義されたコールパーキング用 DTMF シーケンスを送信することで、受信側が通話をパークできます。 |
| `K` | `features.conf` で定義されたコールパーキング用 DTMF シーケンスを送信することで、発信側が通話をパークできます。 |

The `L(x[:y][:z])` option can be tuned with the following special variables:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (default `yes`): 呼び出し元のために音声を再生します。
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: 呼び出された側のために音声を再生します。
- `LIMIT_TIMEOUT_FILE` — 時間切れ時に再生されるファイル。
- `LIMIT_CONNECT_FILE` — 通話開始時に再生されるファイル。
- `LIMIT_WARNING_FILE` — `y`が定義されているときの警告として再生されるファイル。デフォルトでは残り時間を告げます。

例:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

In the example above, the application will dial to the corresponding PJSIP channel. Both caller and called could transfer the call (Tt). Music on hold will be heard instead of ring back. If nobody answers within 20 seconds, the extension will go to the next priority.

### Hangup()

呼び出しチャンネルを切断します [Description] Hangup([causecode]): このアプリケーションは呼び出しチャンネルを切断します。cause code が指定された場合、チャンネルの切断原因がその値に設定されます。

### Goto()

特定の priority、extension、または context にジャンプします [Description] Goto([[context|]extension|]priority): このアプリケーションは、呼び出しチャンネルがダイヤルプランの実行を指定された priority で続行するようにします。特定の extension（または extension と context）が指定されていない場合、このアプリケーションは現在の extension の指定された priority にジャンプします。ダイヤルプラン内の別の場所へのジャンプが失敗した場合、チャンネルは現在の extension の次の priority で続行されます。

## ダイヤルプランの構築

シンプルなダイヤルプランを構築するには、コンテキストとエクステンションを作成して、すべての着信および発信を処理する必要があります。このセクションでは、最も一般的なエクステンションの作り方を示します。

### エクステンション間のダイヤリング

エクステンション間のダイヤリングを有効にするには、ダイヤルされたエクステンションを指すチャンネル変数 ${EXTEN} を使用できます。たとえば、エクステンションの範囲が 4000 から 4999 で、すべてのエクステンションが SIP を使用している場合、次のコマンドを採用できます。

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### 外部宛先へのダイヤル

外部宛先にダイヤルするには、ダイヤルする番号の前にルートを付けます。北米では、外部にダイヤルする番号の前に 9 を付けるのが一般的です。アナログまたはデジタルチャネルで PSTN に接続している場合、コマンドは次のようになります。DAHDI の代わりに SIP トランクを使用したい場合は、`PJSIP/...@siptrunk`チャネルを使用してください。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

上記の行により、9 と希望の番号をダイヤルできるようになります。例では、最初の DAHDI チャネル（DAHDI/1）を使用します。複数の回線があり、この回線がビジーの場合、通話は完了しません。ただし、次の行を使用すれば、最初に利用可能な DAHDI チャネルを自動的に選択できます。オプションで、DAHDI の代わりに SIP トランクを使用することも可能です。PJSIP 形式`Dial(PJSIP/number@siptrunk,...)`では、ダイヤルされた番号がユーザー部となり、`siptrunk`が上記で設定したエンドポイントです。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

The “g1” パラメータはグループ内で最初に利用可能なチャネルを検索し、すべてのチャネルの使用を可能にします。以下の行を使用すると、長距離番号をダイヤルできます。

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### 9 をダイヤルして PSTN 回線を取得する

外部へのダイヤルに制限がない場合、以下のように簡略化できます。

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### オペレーターエクステンションでの着信

以下の例では、オペレーターエクステンションは4000です。PSTN回線はFXOインターフェースに接続されています。`chan_dahdi.conf` ファイルで指定されたコンテキストは from-pstn です。PSTN からのすべての呼び出しはダイヤルプランのコンテキスト from-pstn にルーティングされます。この回線には直接インバウンドダイヤリング（DID）がありません。そのため、“s” エクステンションを介して呼び出しを受け取る必要があります。SIP トランクから受信する場合は、コンテキスト [from-sip] を使用してください。

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### ダイレクトインバウンドダイヤリング (DID) を使用した着信受信

デジタル回線がある場合、ダイヤルされた内線番号が取得されます。この場合、オペレーターに転送する必要はなく、直接目的地へ転送できます。たとえば、DID の範囲が 3028550 から 3028599 で、最後の 4 桁が DID として渡されるとします。設定は以下の例のようになります。

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### 複数の内線を同時に呼び出す

Asterisk を設定して、ある内線をダイヤルし、応答がない場合は、以下の例のように他の複数の内線を同時にダイヤルさせることができます。

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

この例では、オペレーターにダイヤルされたとき、最初にチャネル **DAHDI/1** が試みられます。15 秒（タイムアウト）以内に応答がない場合、チャネル **DAHDI/1**、**DAHDI/2**、**DAHDI/3** が同時に鳴り、さらに 15 秒間続きます。

### 発信者IDによるルーティング

この例では、発信者IDに基づいて異なる処理を行うことができ、迷惑電話の対策に役立ちます。例えば:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

この例では、発信者IDが 4832518888 の場合に、以前録音したファイル “I-have-moved-to-china” のメッセージを再生する特別なルールを追加しています。それ以外の呼び出しは通常どおり受け付けられます。

### ダイヤルプランで変数を使用する

Asterisk は、ダイヤルプラン内でグローバル変数やチャンネル変数を特定のアプリケーションの引数として使用できます。以下の例をご覧ください。

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

変数を使用すると、将来的な変更が容易になります。変数を変更すれば、すべての参照が即座に変更されます。

### アナウンスの録音

このセクションの後半で議論するいくつかのオプションでは、録音されたプロンプトを使用します。ここでは、簡単に録音する方法を示します。自分の電話を使ってアナウンスを保存するために、アプリケーション `Record()` を使用します。

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

これらの手順に従うと、ソフトフォンから任意のメッセージを録音できます。例: ソフトフォンで recordmenu をダイヤルする 手順は、最初の 6 文字を除いた変数 `${EXTEN:6}` を使用して録音を呼び出します。言い換えれば、手順は `record(menu:gsm)` と同等です。やることは、`record` + 録音したいファイル名 をダイヤルし、# を押して録音を終了し、録音が聞こえるまで待つだけです。

### デジタルレセプショニストでの着信受信

簡単な例がいくつかできたので、アプリケーション `background()` と `goto()` の学習を拡張しましょう。Asterisk におけるインタラクティブシステムの鍵となるのはアプリケーション `background()` で、これは発信者がキーを押したときに音声ファイルの再生を中断し、ダイヤルされたエクステンションへ通話を送ることができます。`background()` アプリケーションの構文:

```
exten=>extension, priority, background(filename)
```

Another application very useful is goto(). As the name implies, it jumps to the context, extension, and priority indicated. Syntax of the application goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

goto() コマンドの有効な形式:

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

以下の例では、デジタル受付を作成します。`extensions.conf` ファイルを編集し、次の内線を設定するのは非常に簡単です。

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

SIP エクステンションは`PJSIP/`を使用し、IAX エクステンションは`IAX2/`を使用します — どちらのドライバも Asterisk 22 に同梱されていますが、`chan_iax2`は現在レガシーと見なされており、SIP/PJSIP が推奨されています。

ファイル *menu1.gsm* に「エクステンションを押すか、オペレーターを待ってください」というメッセージを録音します。ユーザーが番号 6000 をダイヤルすると、エクステンション 6000 に送られます。この時点で、answer()、background()、goto()、hangup()、playback() といった複数のアプリケーションの使用方法を明確に理解しているはずです。もし理解が不十分であれば、この章をもう一度読み返し、内容に慣れるまで繰り返してください。background アプリケーションは非常に頻繁に使用します。エクステンション、プライオリティ、アプリケーションの基本を理解すれば、シンプルなダイヤルプランの作成は容易です。これらの概念は本書の後半でさらに詳しく掘り下げられ、ダイヤルプランがより強力になることがわかります。

## 要約

この章では、設定ファイルが **/etc/asterisk** ディレクトリに格納されていることを学びました。Asterisk を使用するには、まずチャンネル（例：pjsip、dahdi、iax）を設定する必要があります。設定ファイルには、シンプルグループ、オブジェクト継承、複雑エンティティという 3 種類の文法が存在します。ダイヤルプランは **extensions.conf** ファイルで作成され、コンテキストとエクステンションの集合です。ダイヤルプラン内では、各エクステンションがアプリケーションをトリガーします。**playback**、**background**、**dial**、**goto**、**hangup**、**answer** アプリケーションの使用方法を学びました。

## Quiz

1. チャネル設定ファイルはどれですか（該当するものすべてを選択）:
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. Asterisk 22 では、単一の`chan_sip`ピア`[6001]`（`type=friend`/`host=dynamic`）は`pjsip.conf`でどの関連オブジェクトのセットに置き換えられますか?
   - A. `type=peer`と`type=user`
   - B. `type=endpoint`、`type=auth`、および`type=aor`
   - C. 単一の`type=friend`
   - D. `type=transport`と`type=global`
3. チャネル設定ファイルでコンテキストを定義することは重要です。なぜなら、チャネルからの着信コールのコンテキストを設定し、コールは`extensions.conf`内の一致するコンテキストで処理されるからです。
   - A. True
   - B. False
4. `Playback()`アプリケーションと`Background()`アプリケーションの主な違いは（2つ選択）:
   - A. Playback はプロンプトを再生しますが、数字の入力は待ちません。
   - B. Background はプロンプトを再生しますが、数字の入力は待ちません。
   - C. Background はメッセージを再生し、数字が押されるのを待ちます。
   - D. Playback はメッセージを再生し、数字が押されるのを待ちます。
5. DID がないテレフォニーインターフェースカード（FXO）を通じて Asterisk にコールが入ると、特別なエクステンションで処理されます:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. `Goto()`アプリケーションの有効なフォーマットは（3つ選択）:
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. パターン`_7[1-5]XX`はどれにマッチしますか（該当するものすべてを選択）:
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. `Dial(PJSIP/${EXTEN},20,tTm)`で、`m`オプションは何をしますか?
   - A. コールの最大通話時間を制限します。
   - B. チャネルが応答するまで、呼び出し側にリングバックの代わりにミュージックオンホールドを提供します。
   - C. 被呼び出し側が応答した後に DTMF 桁を送信します。
   - D. ダイヤルプランヒントを使用して発信者IDを強制します。
9. `chan_dahdi.conf`で使用されるオプション継承文法では、あなたは:
   - A. オブジェクトを単一行で定義します。
   - B. まずオプションを定義し、定義したオプションの下にオブジェクトを宣言します。
   - C. 各オブジェクトごとに別々のコンテキストを定義します。
10. エクステンション内のプライオリティは連続して番号付け（1, 2, 3, …）する必要があり、`n`は使用できません。
    - A. True
    - B. False

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
