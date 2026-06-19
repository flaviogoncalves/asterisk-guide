# PJSIPによる最初のPBX構築

本章では、基本的なAsterisk PBXの設定方法を学びます。ここでの主な目的は、PBXを初めて稼働させ、内線同士の通話、メッセージ再生、および単一のアナログまたはSIP trunkへの発信ができるようにすることです。本章の狙いは、Asteriskを可能な限り早く立ち上げ、動作させることにあります。本章の作業を完了すれば、設定の詳細を深く掘り下げる後続の章に向けて十分な基礎知識が得られるはずです。

## 学習目標

本章を終える頃には、以下のことができるようになっているはずです。

- 設定ファイルを理解し、編集する
- SIPベースのsoftphoneをインストールする
- SIP trunkをインストールし、設定する
- アナログ接続をインストールし、設定する
- 内線間で通話する
- 電話機と外部の宛先間で通話する
- 自動応答（auto attendant）を設定する

## 設定ファイルの理解

Asteriskは、/etc/asterisk に配置されたテキスト形式の設定ファイルによって制御されます。ファイル形式はWindowsの「.ini」ファイルに似ています。セミコロンはコメント文字として使用され、「=」と「=>」の記号は同等であり、スペースは無視されます。

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asteriskは「=」と「=>」を同じように解釈します。構文の違いは、オブジェクトと変数を区別するために使用されます。変数を宣言したい場合は「=」を、オブジェクトを指定する場合は「=>」を使用してください。構文はすべてのファイルで共通ですが、以下で説明するように3種類の文法が使用されます。

## 文法

| 文法 | オブジェクトの作成方法 | 設定ファイル | 例 |
|---------|---------------------------|------------|---------|
| シンプルグループ | すべて同じ行に記述 | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| オプション継承 | オプションを先に定義し、オブジェクトがそれを継承する | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| 複雑なエンティティ | 各エンティティがコンテキストを持つ | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### シンプルグループ

extensions.conf、meetme.conf、voicemail.confで使用されるシンプルグループ形式は、最も基本的な文法です。各オブジェクトは、そのオプションと共に同じ行で宣言されます。例：

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

この例では、オブジェクト1がオプションop1、op2、op3と共に作成され、オブジェクト2も同様にオプションop1、op2、op3と共に作成されます。

### オブジェクトオプション継承文法

この形式はchan_dahdi.confやagents.confで使用されます。これらのファイルでは多数のオプションが利用可能であり、ほとんどのインターフェースやオブジェクトが同じオプションを共有します。通常、1つ以上のセクションにオブジェクトとチャネルの宣言が含まれます。オブジェクトに対するオプションはオブジェクトの上に宣言され、別のオブジェクトに対して変更可能です。この概念は理解しにくいかもしれませんが、使用するのは非常に簡単です。例：

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

最初の2行は、オプションop1とop2の値をそれぞれ「bas」と「adv」に設定します。オブジェクト1がインスタンス化されると、オプション1は「bas」、オプション2は「adv」として作成されます。オブジェクト1を定義した後、オプション1を「int」に変更します。次に、オプション1を「int」、オプション2を「adv」としてオブジェクト2を作成します。

### 複雑なエンティティオブジェクト

この形式はpjsip.conf、iax.conf、および多数のオプションを持つエンティティが存在するその他の設定ファイルで使用されます。通常、この形式では共通設定の大部分を共有することはありません。各エンティティはコンテキストを受け取ります。グローバル設定のための[general]のような予約済みコンテキストが存在する場合もあります。オプションはコンテキスト宣言内で宣言されます。例：

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

エンティティ[entity1]は、オプションop1とop2に対してそれぞれ「value1」と「value2」という値を持っています。エンティティ[entity2]は、オプションop1とop2に対して「value3」と「value4」という値を持っています。

## AsteriskのLAB構築のためのオプション

PBXを設定するには、基本的なハードウェアが必要です。難しくも高価でもありませんが、考慮すべきいくつかの選択肢があります。必要なのは電話機2台と公衆網への接続だけです。ラボを作成する際に可能なオプションと組み合わせについて、以下で説明します。

### オプション1：完全なLAB

完全なLABでは、利用可能なすべてのシナリオをテストし、ATA、IP-phone、softphoneなどのソリューションを比較できます。また、アナログtrunkとSIP trunkについても学ぶことができます。必要なものは以下の通りです。

- SIPアナログ電話アダプタ（ATA）
- IP-phone
- Asterisk専用サーバー
- softphoneを搭載したワークステーション
- 少なくとも2つのインターフェース（1 FXOおよび1 FXS）を持つアナログインターフェースカード
- VoIPプロバイダーのアカウント

### オプション2：経済的なLAB

経済的なLABでは、少し簡略化します。IP-phoneよりも通常安価なATAと、非常に安価な単一のFXOカードを使用します。サーバーに直接接続されたアナログ電話機は使用できませんが、実際にはあまり発生しないケースです。必要なものは以下の通りです。

- SIPアナログ電話アダプタ（ATA）
- Asterisk専用サーバー
- softphone用のワークステーション
- 1 FXOを持つアナログインターフェースカード
- VoIPプロバイダーのアカウント

### オプション3：超経済的なラボ

3番目のLABでは、学生自身のノートPC上の仮想化サーバーを使用します。このモデルの問題は、UDPポートによって発生する競合です。Asteriskサーバーとsoftphoneの両方が同じポートにアクセスしようとして、Asteriskがアドレスポートをバインドできなくなることがあります。もう1つの問題は通話品質です。仮想環境はAsteriskのようなリアルタイムアプリケーションには適していません。サーバーとワークステーションには無料のsoftphoneを使用し、SIPプロバイダーへのtrunk接続を使用します。必要なものは以下の通りです。

- softphoneを実行するノートPC
- Asteriskをインストールするための仮想マシン（VirtualBox、VMwareなど）
- VoIPプロバイダーのアカウント

## インストール手順

インストール手順を理解しやすくするために、Asteriskをインストールおよび設定するために必要なステップの順序を概説しました。

![リファレンスラボのレイアウト：SIP/IAX softphone、IP-phone、および内線としてのアナログアダプタ（1）、ETH0/FXO/FXSインターフェースを備えたAsteriskサーバー（3）、およびVoIPプロバイダーまたはブロードバンドリンクを介したPSTNへのtrunk（2）。](../images/04-first-pbx-fig01.png)

1. 内線の設定 a. SIP内線（ATA、softphone、IP-phone） b. IAX内線 c. FXS内線 2. Trunkの設定 a. SIP trunkの設定 b. FXO trunkの設定 3. 基本的なdialplanの構築 a. 内線間の発信 b. 外部宛先への発信 c. オペレーター内線での着信 d. 自動応答での着信

## 内線の設定

内線とは、FXSポートに接続されたSIP、IAX、またはアナログ電話機のことです。内線を設定するには、チャネルに関連する設定ファイル（pjsip.conf、iax.conf、chan_dahdi.conf）を編集する必要があります。

### SIP内線

Asterisk 22では、PJSIP（`res_pjsip`スタック、設定は`/etc/asterisk/pjsip.conf`）がSIPチャネルドライバです。エンドポイントごとに複数のトランスポートをサポートし、活発にメンテナンスされており、プラットフォームに同梱される唯一のSIPドライバです。（オリジナルの`chan_sip`ドライバはAsterisk 21で削除されました。古い設定を移行する必要がある場合は、「Legacy channels」の章を参照してください。）

ここでの考え方は、シンプルなPBXを設定することです。（後続の章で、すべての詳細を含む完全なSIP/PJSIPセッションを提供します。）PJSIPは`/etc/asterisk/pjsip.conf`で設定され、SIP電話機とVoIPプロバイダーに関連するすべてのパラメータを保持します。通話の発着信を行う前に、SIPクライアントを設定する必要があります。

#### トランスポート

PJSIPでは、リスナー設定（バインドアドレス、ポート、プロトコル）は`transport`オブジェクト内に存在します。Asteriskにはユーザー名推測に対する組み込みの保護機能があり、不明なユーザーと既知のユーザーに対して常に同一の認証チャレンジを返し、単一のIPからの未確認のリクエストは`[global]`オプションの`unidentified_request_count`/`unidentified_request_period`を介してレート制限されます。トランスポートの主なオプションは以下の通りです。

- protocol: トランスポートプロトコル — `udp`、`tcp`、`tls`、`ws`、または`wss`。
- bind: リスナーがバインドするアドレスとポート。アドレスを`0.0.0.0`に設定すると、すべてのインターフェースにバインドされます。SIPポートはUDP/TCPでデフォルトの5060になります。

最小限のUDPトランスポート：

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

コーデックの選択（`disallow`/`allow`）とデフォルトの`context`は、トランスポートではなく、各`endpoint`（下記参照）で設定されます。匿名/ゲスト通話は`anonymous`という名前の`endpoint`によって処理されます。登録タイマーは`maximum_expiration`/`default_expiration`を介してAORごとに制御されます。

#### SIPクライアント

トランスポートセクションが完了したら、SIPクライアントをセットアップします。繰り返しになりますが、本書の後半でSIP/PJSIPに関する章を丸ごと設けています。今は基本に集中し、詳細は後回しにしましょう。

PJSIPでは、SIPクライアントは名前参照によって結び付けられた一連の関連オブジェクトから構築されます。

- `endpoint`: 通話動作 — コーデック（`allow`/`disallow`）、dialplanの`context`、および使用する`auth`と`aors`。
- `auth`: 資格情報。`username`はSIP認証ユーザー名であり、`password`はデバイスの認証に使用されるシークレットです。
- `aor`: "Address of Record"（AOR） — エンドポイントに到達可能な場所。固定IP上のデバイス用の静的な`contact=`、またはデバイスが動的に登録できるようにする`max_contacts=`のいずれかです。

警告：8文字以上で、英数字を含み、少なくとも1つの記号を使用した強力なパスワードを使用してください。メーリングリストにはサーバーがハッキングされたという報告が寄せられており、SIP用の総当たりパスワードクラッカーはスクリプトキディでも容易に入手できます。通話詐欺は、消費者やプロバイダーに数千ドルの損害を与えます。

エンドポイント6000は固定IP上のデバイスであるため、そのAORは登録を許可する代わりに静的な`contact`を保持します。エンドポイント6001は登録を行うデバイスであるため、そのAORは登録を許可します（`max_contacts=1`）：

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
auth_type=userpass
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
auth_type=userpass
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIPでは、`endpoint`、`auth`、および`aor`セクションで同じセクション名を共有できます（例：上記の2つの`[6001]`ブロックは、その`type=`で区別されます）。多くの管理者は、読みやすさのためにそれらにサフィックス（`[6001]`、`[6001-auth]`、`[6001]` aor）を付けます。登録するデバイスの場合、連絡先は電話機が登録する際に動的に学習されるため、AORに静的な`contact`は不要です。

## IAX内線

`chan_iax2`はAsterisk 22にも同梱されていますが、現在はレガシーです。新規導入にはSIP/PJSIPが推奨されるプロトコルです。

IAX内線を作成することもできます。このプロトコルはAsteriskネイティブであり、本書の後半で専用のセクションを設けます。今のところは、このプロトコルを使用していくつか内線を作成しましょう。最初に設定するセクションとして、[general]セクションには設定すべき特定のパラメータがあります。主なオプションは以下の通りです。

- allow/disallow: 使用するコーデックを定義します。
- bindaddr: Asterisk SIPリスナーにバインドするアドレス。0.0.0.0（デフォルト）に設定すると、すべてのインターフェースにバインドされます。
- context: クライアントセクションで変更されない限り、すべてのクライアントのデフォルトコンテキストを設定します。セキュリティ上の理由からdummyを使用しました。allowguestオプションがyesに設定されている場合、認証されていないユーザーはこのコンテキストに入ります。
- bindport: リッスンするSIP UDPポート。
- delayreject: yesに設定すると、REGREQまたはAUTHREQに対する認証拒否の送信を遅延させ、総当たりパスワード攻撃に対するセキュリティを向上させます。
- bandwidth: highに設定すると、g711のulawやalawといったバリエーションなど、高帯域幅コーデックの選択が可能になります。

以下はiax.confファイルの[general]セクションのサンプルです。

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

### IAXクライアント

generalセクションが完了したら、IAXクライアントをセットアップします。

- [name]: SIPデバイスがAsteriskに接続する際、SIP URIのユーザー名部分を使用してピア/ユーザーを検索します。
- type: 接続クラスを設定します。オプションはpeer、user、friendです。 o peer: Asteriskはピアに通話を送信します。 o user: Asteriskはユーザーからの通話を受信します。 o friend: 両方が同時に発生します。
- host: IPアドレスまたはホスト名。最も一般的なオプションはdynamicで、ホストがAsteriskに登録する際に使用されます。
- secret: ピアとユーザーを認証するためのパスワード。

警告：8文字以上で、英数字を含み、少なくとも1つの記号を使用した強力なパスワードを使用してください。メーリングリストにはサーバーがハッキングされたという報告が寄せられており、SIP md5ハッシュ用の総当たりパスワードクラッカーはスクリットキディでも入手可能です。通話詐欺は、消費者やプロバイダーに数千ドルの損害を与えます。例：

```
[guest]
type=user
context=dummy
callerid=”Guest IAX User”
[6003]
context=from-internal
type=friend
secret=#sup3rs3cr3t#
host=dynamic
context=from-internal
[6004]
context=from-internal
type=friend
secret=#s3cr3ts3cr3t#
host=dynamic
context=from-internal
```

## SIPデバイスの設定

Asterisk設定ファイルで電話機を定義した後、電話機自体を設定します。この例では、無料のsoftphoneであるSipPulse Softphone（https://www.sippulse.com/produtos/softphone からダウンロード）の設定方法を示します。お使いのデバイスのパラメータについては、マニュアルを確認してください。ステップ1：内線6000を使用するように電話機を設定します。インストールプログラムを実行します。実行後、アカウント/SIP設定を開き、新しいSIPアカウントを追加します。必要な情報を入力します。

![SipPulse Softphoneのアカウント画面 — サーバー（AsteriskのIPまたはドメイン）、ユーザー名、パスワード、表示名を入力し、トランスポート（UDP、TCP、またはTLS）を選択します。](../images/softphone/sipphone-account.png){width=35%}

表示名：6000  ユーザー名：6000  パスワード：#MySecret1#7  認証ユーザー名：6000  ドメイン：ip_of_your_server。コンソールコマンド`pjsip show endpoints`（詳細は`pjsip show endpoint 6000`、登録済みAOR連絡先は`pjsip show contacts`）を使用して、電話機が登録されていることを確認します。電話機6001についても同様の設定を繰り返します。

![登録済みのSipPulse Softphone — 緑色の点とアカウント行（`1001@softphone.sippulse.com.br`）が登録を確認しています。キーパッドまたは通話/ビデオボタンから発信します。](../images/softphone/sipphone-registered.png){width=35%}

## IAXデバイスの設定

IAX2はレガシープロトコルであり（「Legacy channels」の章を参照）、SipPulse SoftphoneはSIP専用であるため、IAXアカウントを登録できません。IAX2をテストする必要がある場合は、まだサポートしているsoftphoneを使用してください。新しいIAXアカウントを作成します。

3. 新しいIAXアカウントを選択します。 4. 電話機6003およびオプションで6004に関連するオプションを挿入します。 5. 設定を保存し、iax2 show peersを使用して電話機が登録されているか確認します。重要：SIP用に1つ、IAX用に1つのアカウントを使用してください。IAXとSIPの両方を同時に鳴らすようにシステムを設定したい場合は、dialplanのセクションでその方法を説明します。

### PSTNインターフェースの設定

PSTNに接続するには、Foreign Exchange Office（FXO）インターフェースと電話回線が必要です。既存のPBX内線を使用することもできます。FXOインターフェースを備えた電話インターフェースカードは、複数のメーカーから入手可能です。この例では、DAHDIインターフェースカードのインストール方法を示します。

![FXSポートとFXOポート：FXSポートはアナログ電話機を駆動し（ダイヤルトーンと呼び出し音を供給）、FXOポートはAsteriskを電話会社の回線に接続します。](../images/04-first-pbx-fig02.png)

### DAHDIを使用したアナログ回線

DAHDIと互換性のあるアナログカードは、複数のメーカーから購入できます。X100Pは最初のDigiumカードの1つでしたが、すでに製造中止になっています。一部のメーカーは依然として同様のクローンを製造しています。X100Pの価格に加え、これらのカードと新しいマザーボードの間でいくつかの問題が見つかっているため、注意して使用してください。私の意見では、X100Pは本番環境には適していません。DAHDIと互換性のあるカードであれば動作するはずです。DAHDI開発者チームのおかげで、インターフェースカードをほぼ自動的に検出して設定するツールが利用可能になりました。DAHDIドライバをインストールしたばかりの場合は、make configを実行し、マシンを再起動して自動的にロードすることを忘れないでください。以下のコマンドを使用して、カードを検出および設定できます。ステップ1：ハードウェアを検出するには、以下を使用します。

```
dahdi_hardware.
```

ステップ2：設定するには以下を使用します。

```
dahdi_genconf.
```

上記のコマンドは、/etc/dahdi/system.confと/etc/asterisk/dahdi-channels.confの2つのファイルを生成します。dahdi_genconfのデフォルトパラメータは通常問題ありませんが、/etc/dahdi/genconf_parametersファイルで変更できます。デフォルトでは、回線（FXO）をfrom-pstnコンテキストに、電話機（FXS）をfrom-internalコンテキストに挿入します。ステップ3：dahdi_genconfを実行した後、/etc/asterisk/chan_dahdi.confファイルの最後の行に次の行を挿入します。

```
#include dahdi-channels.conf
```

ステップ4：/etc/dahdi/modulesファイルを編集し、未使用のドライバをすべてコメントアウトします。続行する前に再起動し、以下を使用してチャネルが認識されているか確認します。

```
CLI>dahdi show channels
```

### VoIPプロバイダーを使用したPSTNへの接続

予算が非常に限られている場合は、SIP trunkを設定してPSTNに接続できます。これは間違いなくPSTNに接続する最も手頃な方法です。世界中に何千ものVoIPプロバイダーが存在します。それらのいずれかに接続するには、いくつかのパラメータが必要です。SIPプロバイダーから提供されるパラメータ：

- username: ログイン名
- password: パスワード
- Provider’s domain: ドメイン
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

2つのパラメータは自分で決定する必要があります。

- 着信を受ける内線 — この場合は: 9999
- context: from-sip

PJSIPでは、登録を行うSIP trunkはエンドポイントに使用されるのと同じオブジェクトファミリーから構築され、さらに明示的な`registration`および`identify`オブジェクトが追加されます。`registration`オブジェクトはプロバイダーに登録するようにAsteriskに指示し、`identify`オブジェクトはプロバイダーのIPからの着信トラフィックをエンドポイントに一致させ（PJSIPはソースIPによって着信INVITEを認証します）、`outbound_auth`は発信通話と登録のための資格情報を提供します：

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
auth_type=userpass
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

このtrunkにアクセスするには、チャネル名`PJSIP/siptrunk`を使用します。`dtmf_mode=rfc4733`設定はDTMFを帯域外で伝送します（RFC 4733は古いRFC 2833を廃止しました。ペイロードは同一です）。`identify`/`match`オプションはIPアドレス、CIDR、またはホスト名を受け入れますが、ホスト名は設定読み込み時に一度だけ解決されるため、IPが変更されるプロバイダーの場合は、シグナリングIPを明示的にリストしてください。`pjsip show registrations`で登録を確認します。

## Dialplanの紹介

DialplanはAsteriskの心臓部のようなものです。PBXへのすべての通話をAsteriskがどのように処理するかを定義します。これは、Asteriskが従うべき命令リストを作成する内線で構成されます。命令は、チャネルまたはアプリケーションから受信した数字によって実行されます。Asteriskを正常に設定するには、dialplanを理解することが不可欠です。dialplanの大部分は、/etc/asteriskディレクトリ内のextensions.confファイルに含まれています。このファイルはシンプルグループ文法を使用し、4つの主要な概念を持っています。

- 内線（Extensions）
- 優先順位（Priorities）
- アプリケーション（Applications）
- コンテキスト（Contexts）

基本的なdialplanを作成してみましょう。本書の後続のセクションで、dialplan専用の章を設けます。サンプルファイル（make samples）をインストールした場合、extensions.confはすでに存在します。別の名前で保存し、空のファイルから始めてください。

## extensions.confファイルの構造

extensions.confファイルはセクションに分かれています。最初は[general]セクションで、その後に[globals]セクションが続きます。各セクションの先頭は名前の定義（例：[default]）で始まり、別のセクションが作成されると終了します。

### [general]セクション

generalセクションはファイルの上部にあります。dialplanの設定を開始する前に、特定のdialplanの動作を制御する一般的なオプションを知っておくと便利です。これらのオプションは以下の通りです。

- staticおよびwrite protect: static=yesかつwriteprotect=noの場合、CLIを使用できます。

```
command save dialplan.
```

警告：CLIからsave dialplanコマンドを発行すると、ファイル内の備考やコメントがすべて失われます。

- autofallthrough: autofallthroughが設定されている場合、内線で実行すべきことがなくなると、Asteriskの最善の推測に基づいてBUSY、CONGESTION、またはHANGUPで通話を終了します。これがデフォルトです。autofallthroughが設定されていない場合、内線で実行すべきことがなくなると、Asteriskは新しい内線がダイヤルされるのを待ちます。
- clearglobalvars: clearglobalvarsが設定されている場合、dialplan reloadまたはAsterisk reload時にグローバル変数がクリアされ、再解析されます。clearglobalvarsが設定されていない場合、グローバル変数はリロード後も保持され、extensions.confやそのインクルードファイルから削除されたとしても、以前の値に設定されたままになります。
- extenpatternmatchnew: より高速なパターンマッチングアルゴリズムを使用します。これは多数の内線がある場合に顕著に役立ちます。デフォルトはnoです。
- userscontext: users.confからのエントリが登録されるコンテキストです。

### [globals]セクション

[globals]セクションでは、グローバル変数とその初期値を定義します。dialplan内では${GLOBAL(variable)}を使用して変数にアクセスできます。linux/unix環境で定義された変数に${ENV(variable)}を使用してアクセスすることも可能です。グローバル変数は大文字と小文字を区別しません。いくつかの例を挙げます。

```
INCOMING>DAHDI/8&DAHDI/9
RINGTIME=>3
```

次の例では、dialplanでグローバル変数を設定およびテストできます。

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## コンテキスト

コンテキストはdialplanの名前付きパーティションです。[general]および[globals]セクションの後、dialplanは一連のコンテキストであり、各コンテキストには複数の内線があり、各内線には複数の優先順位があり、各優先順位は複数の引数を持つアプリケーションを呼び出します。

![Asteriskの通話フロー：すべての通話は着信通話レグとしてチャネル（IAX、SIPなど）に到着します。チャネルのコンテキスト（チャネル設定ファイルでグローバルまたはチャネルごとに設定）は、発信レグに出る前にdialplanのどのコンテキストが通話を処理するかを決定します。](../images/04-first-pbx-fig03.png)

![通話処理：チャネルに対して定義された`context=`（chan_dahdi.confまたはpjsip.conf内）は、extensions.conf内の対応するコンテキスト名を指定し、そこでdialplanが通話を処理します。](../images/04-first-pbx-fig04.png)

他の電話機やPSTNに到達するためのシンプルなdialplanを構築できます。しかし、Asteriskはそれよりもはるかに強力です。私たちの目的は、dialplanで可能なことの詳細を教えることです。

## 内線

電話機、インターフェース、メニューなどに関連付けられた従来のPBXとは異なり、Asteriskでは内線とは特定の番号や名前がトリガーされたときに処理されるコマンドのリストです。コマンドは優先順位順に処理されます。

![内線の構文：`exten => number(name),{priority|label}[(alias)],application`。内線は数値、英数字、発信者ID付きの数値、パターン、または`s`のような標準内線にできます。優先順位は数値、`n`（次）、`s`（同じ）、オフセット、または`hint`にできます。](../images/04-first-pbx-fig05.png)

内線はリテラル、標準、または特殊なものにできます。標準内線には数字や名前、および*と#文字のみが含まれます。12#89*は有効なリテラル内線です。名前も内線マッチングに使用できます。内線は大文字と小文字を区別します。ただし、同じ名前で大文字と小文字が異なる2つの内線を作成することはできません。内線がダイヤルされると、最初の優先順位のコマンドが実行され、続いて優先順位2のコマンドが実行されます。これは通話が切断されるか、何らかのコマンドが失敗を示す1を返すまで続きます。最後の優先順位が実行されたときにAsteriskが何をするかは、パラメータautofallthroughによって制御されます。本章の[general]セクションを参照してください。例：

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

上記は、内線123がダイヤルされたときに処理される命令リストです。最初の優先順位はチャネルに応答することです（チャネルが呼び出し状態にある場合、つまりFXOチャネルで必要）。2番目の優先順位はtt-weaselsという音声ファイルを再生することです。3番目の優先順位はチャネルを切断します。もう1つのオプションは、発信者IDに従って通話を処理することです。/文字を使用して、処理する発信者IDを指定できます。例：

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

この例では、内線123がトリガーされ、発信者IDが100の場合にのみ以下のオプションが実行されます。これは以下で説明するパターンを使用しても実行できます。

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: 内線をチャネルにマッピングします。チャネルの状態を監視するために使用されます。プレゼンスと組み合わせて使用されます。電話機がサポートしている必要があります。

#### パターン

dialplanではパターンとリテラルを使用できます。パターンはdialplanのサイズを縮小するのに非常に役立ちます。すべてのパターンは「_」文字で始まります。パターンを定義するために以下の文字を使用できます。図はAsteriskで使用可能なパターンを識別します。

![パターンマッチング文字：`_`はパターンを開始し、`.`は1つ以上の文字にマッチし、`!`は0文字以上にマッチし、`[123-7]`はリストされた数字または範囲にマッチし、`X`は0-9、`Z`は1-9、`N`は2-9にマッチします。オフィス内線の範囲をマッピングする例もあります。](../images/04-first-pbx-fig06.png)

### 特殊内線

Asteriskは一部の内線名を標準内線として使用します。

![Asteriskの特殊内線：`i`（無効）、`s`（開始）、`h`（切断）、`t`（タイムアウト）、`T`（絶対タイムアウト）、`o`（オペレーター）、`a`（ボイスメールで`*`を押下）、`fax`（FAX検出）、および`Talk`（BackgroundDetectで使用）。](../images/04-first-pbx-fig07.png)

説明： s: 開始。ダイヤルされた番号がない場合に通話を処理するために使用されます。FXO trunkやメニュー内処理に役立ちます。 t: タイムアウト。プロンプトが再生された後に通話が非アクティブなままの場合に使用されます。非アクティブな回線を切断するためにも使用されます。 T: AbsoluteTimeout。dialplan関数`TIMEOUT(absolute)`を使用して通話制限を設定した場合、通話が定義された制限を超えると、T内線に送信されます。 h: 切断。ユーザーが通話を切断した後に呼び出されます。 i: 無効。コンテキスト内に存在しない内線を呼び出したときにトリガーされます。これらの内線を使用すると、CDRレコードの内容、特にダイヤルされた番号を含まないdstに影響を与える可能性があります。 o: オペレーター。ボイスメール中にユーザーが「0」を押したときにオペレーターに移動するために使用されます。これらの内線の使用は、課金レコード（CDR）の内容を変更する可能性があり、特にフィールドdstにはダイヤルされた番号が含まれません。この問題を回避するには、Dial()アプリケーションでオプションgを使用し、関数resetcdr(w)やnocdr()を検討してください。

## 変数

Asterisk PBXでは、変数はグローバル、チャネル固有、環境固有にできます。NoOP()アプリケーションを使用して、コンソールで変数の内容を確認できます。グローバル変数またはチャネル固有の変数をアプリケーションの引数として使用できます。変数は以下の例のように参照でき、varnameは変数名です。

```
${varname}
```

変数名は、文字で始まる英数字の文字列にできます。グローバル変数名は大文字と小文字を区別しません。ただし、システム変数（Asterisk定義はチャネル定義）は大文字と小文字を区別します。したがって、変数${EXTEN}は${exten}とは異なります。

### グローバル変数

グローバル変数は、extensions.confファイルの[global]セクションで、または以下のアプリケーションを使用して設定できます。

```
set(Global(variable)=content)
```

### チャネル固有変数

チャネル固有変数は、set()アプリケーションを使用して設定されます。各チャネルは独自の変数スペースを受け取ります。異なるチャネルの変数間で衝突が発生する可能性はありません。チャネル固有変数は、チャネルが切断されると破棄されます。最も一般的に使用される変数は以下の通りです。

- ${EXTEN} ダイヤルされた内線
- ${CONTEXT} 現在のコンテキスト
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} 現在の発信者ID
- ${PRIORITY} 現在の優先順位

その他のチャネル固有変数はすべて大文字です。dumpchan()アプリケーションを使用して、いくつかの変数の内容を確認できます。以下は、ダンプチャネル変数の簡単な抜粋です。

```
exten=9001,1,dumnpchan()
exten=9001,n,echo()
exten=9001,n,hangup()
```

Dumpchanの出力：

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

上記のフィールドレイアウトはAsterisk 22の`DumpChan`出力です（実際の`PJSIP/...`チャネル名、`CallerIDNum`/`ConnectedLineID`フィールド、およびPJSIPチャネルが設定する`Raw*`/`Transcode`/`BridgeID`行）。古いドライバとは異なり、PJSIPチャネルは`SIPCALLID`/`SIPUSERAGENT`チャネル変数を自動設定しません。同等のSIP詳細は、dialplan関数`PJSIP_HEADER()`および`CHANNEL()`を使用してオンデマンドで読み取られます。たとえば、リモートRTPアドレスには`${CHANNEL(pjsip,call-id)}`、`${PJSIP_HEADER(read,User-Agent)}`、`${CHANNEL(rtp,dest)}`などを使用します。

### 環境固有変数

環境固有変数は、オペレーティングシステムで定義された変数にアクセスするために使用できます。ENV()関数を使用して環境固有変数を設定できます。例：

```
${ENV(LANG)}
Set(ENV(LANG))=en_US
```

### アプリケーション固有変数

一部のアプリケーションは、データ入力および出力に変数を使用します。アプリケーションを呼び出す前に変数を設定するか、アプリケーション実行後に変数を取得できます。例：Dialアプリケーションは以下の変数を返します。

- ${DIALEDTIME} -> チャネルをダイヤルしてから切断されるまでの時間。
- ${ANSWEREDTIME} -> 実際の通話時間。
- ${DIALSTATUS} 通話のステータス： o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> 通話のエラーメッセージ。

## 式

式はdialplanで非常に役立ちます。文字列の操作や数学的・論理的な演算を実行するために使用されます。

![Asterisk式の概要 — `$[expression1 operator expression2]` — dialplanで使用可能な数学、論理、比較、正規表現、および条件演算子をグループ化しています。](../images/04-first-pbx-fig08.png)

式の構文は以下のように定義されます。

```
$[expression1 operator expression2]
```

「I」という変数があり、その変数に100を加えたいとします。

```
$[${I}+100]
```

Asteriskがdialplan内で式を見つけると、式全体を結果の値に置き換えます。

### 演算子

式を構築するには以下の演算子を使用できます。演算子の優先順位に注意することが重要です。 1. 括弧 “()” 2. 単項演算子 “! -“ 3. 正規表現 “: =~ 4. 乗法演算子 “* / %” 5. 加法演算子 “+ -“ 6. 比較演算子 7. 論理演算子 8. 条件演算子

#### 数学演算子

- 加算 (+)
- 減算 (-)
- 乗算 (*)
- 除算 (/)
- 剰余 (%)

#### 論理演算子

- 論理 “AND” (&)
- 論理 “OR” (|)
- 論理単項補数 (!)

#### 正規表現演算子

- 正規表現マッチング (:)
- 正規表現完全マッチング (=~)

正規表現は、検索パターンを記述するために使用される特別なテキスト文字列です。正規表現はワイルドカードと考えることができます。正規表現は、文字列をパターンと照合してマッチングを確認するために使用されます。マッチングが成功し、正規表現に少なくとも1つのマッチが含まれている場合、最初のマッチが返されます。それ以外の場合、結果はマッチした文字数になります。

#### 比較演算子

比較の結果は、関係が真であれば1、偽であれば0になります。

- = 等しい
- != 等しくない
- < 未満
- > より大きい
- <= 以下
- >= 以上

### LAB. 以下の式を評価してください：

これらの式をdialplanに入れ、NoOP()アプリケーションを使用して式を評価します。9002をダイヤルし、Asteriskコンソールで結果を調べます。verbose 15を使用して結果を表示します。

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

## 関数

一部のアプリケーションは関数に置き換えられており、式だけよりも高度な方法で変数を処理できます。以下のコンソールコマンドを発行すると、関数の全リストを確認できます。

```
CLI>core show functions
```

文字列の長さ：${LEN(string)} は文字列の長さを返します

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

最初の操作では、システムは結果として5（「fruit」という単語の文字数）を表示します。2番目は4（「pear」という単語の文字数）を返します。部分文字列：offsetパラメータで定義された位置から始まり、lengthパラメータで定義された文字列長を持つ部分文字列を返します。offsetが負の場合、文字列の末尾から右から左へ開始します。lengthが省略または負の場合、offsetから始まる文字列全体を取得します。

```
${string:offset:length }
```

例 #1：複数の部分文字列

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

例 #2：最初の3桁から市外局番を取得します。

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

例 #3：変数${EXTEN}から市外局番を除くすべての数字を取得します。

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### 文字列の連結

2つの文字列を連結するには、それらを並べて書くだけです。

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## アプリケーション

dialplanを構築するには、アプリケーションの概念を理解する必要があります。dialplanでチャネルを処理するためにアプリケーションを使用します。アプリケーションは複数のモジュールに実装されています。利用可能なアプリケーションはモジュールに依存します。以下のコンソールコマンドを使用して、すべてのAsteriskアプリケーションを表示できます。

```
CLI>core show applications
```

あるいは、以下の例を使用して特定のアプリケーションの詳細を表示できます。

```
CLI>core show application dial
```

シンプルなdialplanを構築するには、いくつかのアプリケーションを知る必要があります。より高度な例については本書の後半で説明します。

![シンプルなdialplanを構築するために必要なアプリケーション：Answer（チャネルに応答）、Dial（別のチャネルを呼び出す）、Hangup（チャネルを切断）、Playback（音声ファイルを再生）、およびGoto（優先順位、内線、またはコンテキストにジャンプ）。](../images/04-first-pbx-fig09.png)

これらのアプリケーション（上記）を使用して、2つの基本的なPBX用のシンプルなdialplanを作成します。

### Answer()

[概要] 呼び出し中のチャネルに応答する [説明] Answer([delay]): 通話が応答されていない場合、アプリケーションはそれに応答します。それ以外の場合、通話には影響しません。遅延が指定されている場合、Asteriskは通話に応答する前に「delay」で指定されたミリ秒数だけ待機します。

### Dial()

以下の説明は、dialplanでshow application dialを発行することで取得できます。検索しやすいように、以下に再現します。Dialアプリケーションの構文も以下に示します。

```
;dial to a single channel
Dial(type/identifier,timeout,options, URL)
;Dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...][|timeout][|options][|URL]):
```

このアプリケーションは、1つ以上の指定されたチャネルに通話を発信します。要求されたチャネルのいずれかが応答するとすぐに、発信元チャネルが（まだ応答していない場合）応答されます。これら2つのチャネルは、ブリッジされた通話でアクティブになります。要求された他のすべてのチャネルは切断されます。タイムアウトが指定されていない限り、Dialアプリケーションは呼び出されたチャネルのいずれかが応答するか、ユーザーが切断するか、呼び出されたすべてのチャネルがビジーまたは利用不可になるまで無期限に待機します。要求されたチャネルを呼び出せない場合、またはタイムアウトが経過した場合、dialplanの実行は継続されます。このアプリケーションは、完了時に以下のチャネル変数を設定します。

- DIALEDTIME - チャネルをダイヤルしてから切断されるまでの時間。
- ANSWEREDTIME - 実際の通話時間。
- DIALSTATUS - 通話のステータス： o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

プライバシーおよびスクリーニングモードの場合、呼び出された側が発信側を「Go Away」スクリプトに送信することを選択すると、DIALSTATUS変数はDONTCALLに設定されます。呼び出された側が発信者を「torture」スクリプトに送信したい場合、DIALSTATUS変数はTORTUREに設定されます。このアプリケーションは、発信元チャネルが切断された場合、または通話がブリッジされ、ブリッジ内のいずれかの当事者が通話を終了した場合に、通常の終了を報告します。チャネルがサポートしている場合、オプションのURLが呼び出された側に送信されます。OUTBOUND_GROUP変数が設定されている場合、このアプリケーションによって作成されたすべてのピアチャネルがそのグループに含まれます（以下のように

```
Set(GROUP()=...).
```

以下の表は、Dialアプリケーションで最も頻繁に使用されるオプションの一部をまとめたものです。完全なリストについては、コンソールコマンド`core show application Dial`を使用してください。Asterisk 22では、これらのオプションはカンマでチャネルとタイムアウトから分離されています（例：`Dial(PJSIP/2000,20,tTm)`）。

| オプション | 説明 |
|--------|-------------|
| `A(x)` | `x`をファイルとして使用し、呼び出された側にアナウンスを再生します。 |
| `C` | この通話のCDRをリセットします。 |
| `d` | 通話が応答されるのを待っている間に、呼び出し側のユーザーが1桁の内線をダイヤルできるようにします。現在のコンテキストにその内線が存在する場合、または`EXITCONTEXT`変数で定義されたコンテキストが存在する場合は、その内線に終了します。 |
| `D([called][:calling])` | 呼び出された側が応答した後、通話がブリッジされる前に指定されたDTMF文字列を送信します。`called`文字列は呼び出された側に、`calling`文字列は呼び出し側に送信されます。いずれかのパラメータのみを使用することもできます。 |
| `f` | 発信チャネルの発信者IDを、dialplanの`hint`を介してチャネルに関連付けられた内線に強制的に設定します。PSTNが任意の発信者IDを許可しない場合に便利です。 |
| `g` | 宛先チャネルが切断された場合、現在の内線でdialplanの実行を継続します。 |
| `G(context^exten^pri)` | 通話が応答された場合、呼び出し側を指定された優先順位に、呼び出された側を優先順位+1に転送します。オプションで内線（または内線とコンテキスト）を指定できます。それ以外の場合は、現在の内線が使用されます。 |
| `h` | 呼び出された側が`*` DTMF数字を送信して切断できるようにします。 |
| `H` | 呼び出し側が`*` DTMF数字を送信して切断できるようにします。 |
| `L(x[:y][:z])` | 通話を`x` msに制限し、`y` msが残っているときに警告を再生し、`z` msごとに警告を繰り返します。以下の`LIMIT_*`変数を参照してください。 |
| `m([class])` | 要求されたチャネルが応答するまで、呼び出し側に保留音を提供します。特定のMusicOnHoldクラスを指定できます。 |
| `r` | 呼び出し側に呼び出し音を示し、呼び出されたチャネルが応答するまで音声を渡しません。 |
| `S(x)` | 呼び出された側が応答してから`x`秒後に通話を切断します。 |
| `t` | 呼び出された側が`features.conf`で定義されたDTMFシーケンスを送信して、呼び出し側を転送できるようにします。 |
| `T` | 呼び出し側が`features.conf`で定義されたDTMFシーケンスを送信して、呼び出された側を転送できるようにします。 |
| `w` | 呼び出された側が`features.conf`で定義されたDTMFシーケンスを送信して、ワンタッチ録音を有効にできるようにします。 |
| `W` | 呼び出し側が`features.conf`で定義されたDTMFシーケンスを送信して、ワンタッチ録音を有効にできるようにします。 |
| `k` | 呼び出された側が`features.conf`で定義された通話保留用のDTMFシーケンスを送信して、通話を保留できるようにします。 |
| `K` | 呼び出し側が`features.conf`で定義された通話保留用のDTMFシーケンスを送信して、通話を保留できるようにします。 |

`L(x[:y][:z])`オプションは、以下の特別な変数で調整できます。

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no`（デフォルト`yes`）：呼び出し側に音声を再生します。
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`：呼び出された側に音声を再生します。
- `LIMIT_TIMEOUT_FILE` — 時間切れになったときに再生されるファイル。
- `LIMIT_CONNECT_FILE` — 通話開始時に再生されるファイル。
- `LIMIT_WARNING_FILE` — `y`が定義されているときに警告として再生されるファイル。デフォルトは残り時間を読み上げることです。

例：

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

上記の例では、アプリケーションは対応するPJSIPチャネルにダイヤルします。呼び出し側と呼び出された側の両方が通話を転送できます（Tt）。呼び出し音の代わりに保留音が聞こえます。20秒以内に誰も応答しない場合、内線は次の優先順位に進みます。

### Hangup()

呼び出し中のチャネルを切断する [説明] Hangup([causecode]): このアプリケーションは呼び出し中のチャネルを切断します。原因コードが指定されている場合、チャネルの切断原因が指定された値に設定されます。

### Goto()

特定の優先順位、内線、またはコンテキストにジャンプする [説明] Goto([[context|]extension|]priority): このアプリケーションは、呼び出し中のチャネルに指定された優先順位でdialplanの実行を継続させます。特定の内線（または内線とコンテキスト）が指定されていない場合、このアプリケーションは現在の内線の指定された優先順位にジャンプします。dialplan内の別の場所にジャンプしようとして成功しなかった場合、チャネルは現在の内線の次の優先順位で継続します。

## dialplanの構築

シンプルなdialplanを構築するには、コンテキストと内線を作成して、すべての着信および発信通話を処理する必要があります。このセクションでは、最も一般的な内線の構築方法を示します。

### 内線間の発信

内線間の発信を有効にするには、ダイヤルされた内線を参照するチャネル変数${EXTEN}を使用できます。たとえば、内線の範囲が4000から4999で、すべての内線がSIPを使用している場合、以下のコマンドを採用できます。

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### 外部宛先への発信

外部宛先にダイヤルするには、ダイヤルした番号の前にルートを付けることができます。北米では、外部にダイヤルするために9の後に番号を付けるのが一般的です。PSTNへのアナログまたはデジタルチャネルを使用している場合、コマンドは以下のようになります。DAHDIの代わりにSIP trunkを使用したい場合は、`PJSIP/...@siptrunk`チャネルを使用してください。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

上記の行により、9と希望の番号をダイヤルできます。この例では、最初のDAHDIチャネル（DAHDI/1）を使用します。複数の回線があり、これがビジー状態の場合、通話は完了しません。ただし、以下の行を使用して、最初に使用可能なDAHDIチャネルを自動的に選択できます。オプションで、DAHDIの代わりにSIP trunkを使用できます。PJSIP形式`Dial(PJSIP/number@siptrunk,...)`では、ダイヤルされた番号がユーザー部分であり、`siptrunk`は上記で設定されたエンドポイントです。

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

「g1」パラメータはグループ内で最初に使用可能なチャネルを検索し、すべてのチャネルを使用できるようにします。以下の行を使用すると、長距離番号をダイヤルできます。

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### 9をダイヤルしてPSTN回線を取得する

外部発信に制限がない場合は、簡略化して以下を使用できます。

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### オペレーター内線での着信

次の例では、オペレーター内線は4000です。PSTN回線はFXOインターフェースに接続されています。chan_dahdi.confファイルで指定されたコンテキストはfrom-pstnです。PSTNからの通話はすべて、dialplanのfrom-pstnコンテキストにルーティングされます。この回線にはDirect Inward Dialing（DID）がないため、「s」内線を介して通話を受ける必要があります。SIP trunkから受信する場合は、[from-sip]コンテキストを使用します。

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

### Direct Inward Dialing（DID）を使用した着信

デジタル回線がある場合は、ダイヤルされた内線を受信します。この場合、通話をオペレーターに転送する必要はなく、宛先に直接転送できます。DID範囲が3028550から3028599で、最後の4桁がDIDで渡されるとします。設定は以下の例のようになります。

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### 複数の内線を同時に鳴らす

Asteriskを設定して、内線をダイヤルし、応答がない場合に他の複数の内線を同時にダイヤルするようにできます。以下の例を参照してください。

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

この例では、誰かがオペレーターをダイヤルすると、最初にチャネルDAHDI/1が試行されます。15秒（タイムアウト）経過しても誰も応答しない場合、チャネルDAHDI/1、DAHDI/2、およびDAHDI/3が同時にさらに15秒間鳴ります。

### 発信者IDによるルーティング

この例では、発信者IDに基づいて異なる処理を行うことができ、これは通話スパマーに役立ちます。例：

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

この例では、発信者IDが4832518888の場合に、以前に録音されたファイル「I-have-moved-to-china」からメッセージを再生するという特別なルールを追加しました。その他の通話は通常通り受け入れられます。

### dialplanでの変数の使用

Asteriskは、特定のアプリケーションの引数としてdialplanでグローバル変数およびチャネル変数を使用できます。以下の例を見てください。

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

変数を使用すると、将来の変更が容易になります。変数を変更すると、すべての参照が即座に変更されます。

### アナウンスの録音

このセクションで後述するオプションの一部では、録音されたプロンプトを使用します。ここでは、それらを録音する簡単な方法を示します。Record()アプリケーションを使用して、自分の電話機からアナウンスを保存します。

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

これらの命令により、softphoneから任意のメッセージを録音できます。例：softphoneからrecordmenuをダイヤルする。命令は、最初の6文字を除いた変数${EXTEN:6}で録音を呼び出します。言い換えれば、命令はrecord(menu:gsm)と同等です。record + 録音するファイル名 をダイヤルし、#を押して録音を終了し、録音を聞くのを待つだけです。

### デジタル受付での着信

いくつかの簡単な例がわかったので、background()およびgoto()アプリケーションについての学習を広げましょう。Asteriskのインタラクティブシステムの鍵はbackground()アプリケーションです。これにより、音声ファイルを実行でき、発信者がキーを押すと、ダイヤルされた内線に通話を送信するために中断されます。background()アプリケーションの構文：

```
exten=>extension, priority, background(filename)
```

もう1つの非常に便利なアプリケーションはgoto()です。名前が示すように、指定されたコンテキスト、内線、および優先順位にジャンプします。goto()アプリケーションの構文：

```
exten=>extension, priority,goto(context, extension, priority)
```

goto()コマンドの有効な形式：

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

次の例では、デジタル受付を作成します。extensions.confファイルを編集し、以下の内線を設定するのは非常に簡単です。

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

SIP内線は`PJSIP/`を使用し、IAX内線は`IAX2/`を使用します。どちらのドライバもAsterisk 22に同梱されていますが、`chan_iax2`は現在レガシーと見なされており、SIP/PJSIPが推奨されます。

menu1.gsmファイルに、「内線をダイヤルするか、オペレーターをお待ちください」というメッセージを録音します。ユーザーが6000という番号をダイヤルすると、内線6000に送信されます。この時点で、answer()、background()、goto()、hangup()、playback()を含むいくつかのアプリケーションの使用方法を明確に理解しているはずです。明確に理解できていない場合は、内容に慣れるまでこの章を読み直してください。backgroundアプリケーションは非常に頻繁に使用します。内線、優先順位、アプリケーションの基本を理解すれば、シンプルなdialplanを作成するのは簡単です。これらの概念は本書の後半でより深く掘り下げられ、dialplanがより強力になることがわかります。

## まとめ

本章では、設定ファイルが/etc/asteriskディレクトリに保存されていることを学びました。Asteriskを使用するには、まずチャネル（pjsip、dahdi、iaxなど）を設定する必要があります。設定ファイルには、シンプルグループ、オブジェクト継承、複雑なエンティティという3つの異なる文法が存在します。dialplanはextensions.confファイルで作成され、一連のコンテキストと内線です。dialplanでは、各内線がアプリケーションをトリガーします。playback、background、dial、goto、hangup、answerアプリケーションの使用方法を学びました。

## クイズ

1. チャネル設定ファイルは（該当するものすべてを選択）：
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. Asterisk 22では、単一の`chan_sip`ピア`[6001]`（`type=friend`/`host=dynamic`）は、`pjsip.conf`のどの関連オブジェクトセットに置き換えられますか？
   - A. `type=peer`と`type=user`
   - B. `type=endpoint`、`type=auth`、および`type=aor`
   - C. 単一の`type=friend`
   - D. `type=transport`と`type=global`
3. チャネル設定ファイルでコンテキストを定義することは、そのチャネルからの通話の着信コンテキストを設定するため重要です。チャネルからの通話は`extensions.conf`の対応するコンテキストで処理されます。
   - A. True
   - B. False
4. `Playback()`アプリケーションと`Background()`アプリケーションの主な違いは（2つ選択）：
   - A. Playbackはプロンプトを再生しますが、数字を待ちません。
   - B. Backgroundはプロンプトを再生しますが、数字を待ちません。
   - C. Backgroundはメッセージを再生し、数字が押されるのを待ちます。
   - D. Playbackはメッセージを再生し、数字が押されるのを待ちます。
5. DIDなしの電話インターフェースカード（FXO）を介して通話がAsteriskに入るとき、それは特殊内線で処理されます：
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. `Goto()`アプリケーションの有効な形式は（3つ選択）：
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. パターン`_7[1-5]XX`は以下にマッチします（該当するものすべてを選択）：
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. `Dial(PJSIP/${EXTEN},20,tTm)`において、`m`オプションは何をしますか？
   - A. 通話を最大持続時間に制限します。
   - B. チャネルが応答するまで、呼び出し音の代わりに呼び出し側に保留音を提供します。
   - C. 呼び出された側が応答した後にDTMF数字を送信します。
   - D. dialplanのヒントを使用して発信者IDを強制します。
9. `chan_dahdi.conf`で使用されるオプション継承文法では：
   - A. オブジェクトを1行で定義します。
   - B. オプションを先に定義し、定義されたオプションの下にオブジェクトを宣言します。
   - C. 各オブジェクトに個別のコンテキストを定義します。
10. 内線の優先順位は連続して番号付けする必要があり（1, 2, 3, …）、`n`を使用することはできません。
    - A. True
    - B. False

**回答:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
