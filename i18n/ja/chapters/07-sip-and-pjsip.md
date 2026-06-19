# SIP & PJSIP in depth

SIPはプロトコルであり、PJSIPはAsterisk 22がそれを利用するための手段です。**PJSIP**（`chan_pjsip`、設定は`pjsip.conf`経由）は、Asterisk 22 LTSにおける唯一のSIPチャネルドライバです。本章では、SIPプロトコルの基礎（プロトコルレベルの仕様であり、100%有効なままです）と、日常的に使用するPJSIPのオブジェクトモデルおよび設定について解説します。廃止されたレガシードライバと移行ガイドについては、「*Legacy channels*」の章で扱います。

## SIPプロトコルの基礎

Session Initiation Protocol (SIP) は、HTTPやSMTPに似たテキストベースのプロトコルであり、ユーザー間の対話型通信セッションを開始、維持、終了するために設計されました。これらのセッションには、音声、ビデオ、チャット、対話型ゲームなどが含まれます。SIPはIETFによって定義され、音声通信の事実上の標準となっています。SIPがどのように機能するかを理解することは非常に重要です。Asterisk 22では、SIPの設定は`pjsip.conf`に記述されます。これはSIPベースのシステムにおいて（`extensions.conf`に次いで）最も頻繁に編集されるファイルの一つです。

### 動作原理

SIPはシグナリングプロトコルであり、以下のコンポーネントで構成されます：User Agent Client、User Agent Servers、SIP Proxies、SIP Gateways。以下の図は、これらのコンポーネント間の関係を示しています。

- UAC (user agent client) – SIPシグナリングを開始するクライアントまたは端末。
- UAS (user agent server) – UACからのSIPシグナリングに応答するサーバー。
- UA (user agent) – SIP端末（UACとUASの両方を含む電話機やゲートウェイ）。
- Proxy Server – UAからリクエストを受け取り、特定のステーションが自身の管理下にない場合に他のSIP Proxyへ転送する。
- Redirect Server – リクエストを受け取り、宛先へ直接転送する代わりに、宛先データを含む情報をUAに送り返す。
- Location Server – UAからリクエストを受け取り、この情報で位置情報データベースを更新する。

通常、プロキシ、リダイレクト、およびロケーションサーバーは同じハードウェア上でホストされ、同じソフトウェアを使用します。これをSIPプロキシと呼びます。SIPプロキシは、位置情報データベースの保守、接続の確立、およびセッションの終了を担います。

![主なSIPコンポーネント：ユーザーエージェント（UAC/UAS/UA）、レジストラ/プロキシ/リダイレクトサーバー、およびPSTNへのゲートウェイ。RTPメディアはエンドポイント間を直接流れる](../images/07-sip-and-pjsip-fig01.png)

#### SIP登録プロセス

電話機が通話を受信できるようになる前に、位置情報データベースに登録される必要があります。位置情報データベースでは、IPアドレスが名前と紐付けられます。以下の例では、内線8500がIPアドレス200.180.1.1に紐付けられます。必ずしも電話番号を使用する必要はありません。SIPアーキテクチャでは、登録される内線は flavio@voip.school のような形式でも構いません。

![SIP登録：電話機が内線8500を自身のIPアドレスに紐付けるREGISTERを送信し、レジストラが位置情報データベースに連絡先を保存して200 OKで応答する](../images/07-sip-and-pjsip-fig02.png)

#### プロキシの動作

SIPプロキシとして動作する場合、SIPサーバーはシグナリングの中間に留まり、高度なルーティングや課金処理を行うことができます。Real Time Protocol (RTP) に基づくメディアフローは、依然としてエンドポイント間を直接流れます。

![プロキシの動作：SIPプロキシはシグナリングパス（INVITE/200 OK）に留まり、ロケーションサーバーで着信側を検索する一方、RTPメディアは2つのエンドポイント間を直接流れる](../images/07-sip-and-pjsip-fig03.png)

#### リダイレクトの動作

リダイレクトを行う際、SIPサーバーは単にメッセージ（例：302 moved temporarily）をユーザーエージェントに送信し、新しいメッセージのパスからは外れます。リソース使用量の観点からは非常に軽量ですが、制御は一切行えません。リダイレクトは、負荷分散設計で使用されることがあります。

![リダイレクトの動作：リダイレクトサーバーが連絡先情報を含む302 Moved TemporarilyでINVITEに応答し、その後は脇に退く。発信側は新しい場所へ直接INVITE/ACKを再送する](../images/07-sip-and-pjsip-fig04.png)

#### AsteriskにおけるSIPの扱い

AsteriskはSIPプロキシでもSIPリダイレクタでもないことを理解しておくことが重要です。Asteriskはレジストラおよびロケーションサーバーの役割を果たすことはできますが、自身に対して2つのUACを接続するだけです。そのため、AsteriskはBack-to-Back User Agent (B2BUA) と見なされます。言い換えれば、2つのSIPチャネルを接続し、ブリッジする役割を果たします。Asteriskには、SIPチャネルをAsterisk経由ではなく直接通信させるre-inviteメカニズムがあります。PJSIPエンドポイントでは、これはパラメータ`direct_media`によって制御されます。`direct_media=yes`を使用すると、RTPフローはエンドポイント間を直接流れるようになり、サーバーリソースを解放します。

#### direct_media=yes を使用したSIP動作

![directmedia=yes を使用したSIP動作：SIPシグナリングはAsteriskを経由するが、RTP音声は2台の電話機間を直接流れ、サーバーリソースを解放する](../images/07-sip-and-pjsip-fig05.png)

ただし、Asteriskを使用して通話を転送または録音する必要がある場合は、パラメータ`direct_media=no`を使用してRTPフローをAsteriskサーバー経由に強制することができます。

#### direct_media=no を使用したSIP動作

![directmedia=no を使用したSIP動作：SIPシグナリングとRTP音声の両方がAsteriskを介してアンカーされるため、通話の録音、トランスコード、転送が可能になる](../images/07-sip-and-pjsip-fig06.png)

#### SIPメッセージ

基本的なSIPメッセージは以下の通りです：

- INVITE – 接続の確立
- ACK – 応答確認
- BYE – 接続の終了
- CANCEL – 確立されていない通話の終了
- REGISTER – UACをSIPプロキシに登録
- OPTIONS – 可用性の確認に使用
- REFER – SIP通話を他へ転送
- SUBSCRIBE – 通知イベントの購読
- NOTIFY – チャネル情報の送信
- INFO – 各種メッセージの送信（例：DTMF）
- MESSAGE – インスタントメッセージの送信

SIP応答はテキスト形式であり、容易に読み取ることができます（HTTPメッセージに似ています）。最も重要な応答は以下の通りです：

- 1XX – 情報メッセージ（100–trying, 180–ringing, 183–progress）
- 2XX – リクエスト成功（200 – OK）
- 3XX – 通話リダイレクト、リクエストを別の場所に転送する必要がある（302 – moved temporarily, 305 – use proxy）
- 4XX – エラー（403 – Forbidden）
- 5XX – サーバーエラー（500 – Internal Server Error; 501 – Not implemented）
- 6XX – グローバル失敗（606 – Not acceptable）

例：

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### Session Description Protocol (SDP)

SDPは元々IETF RFC 2327で定義され、現在はRFC 4566によって廃止されています。これは、セッションアナウンス、セッション招待、およびその他のマルチメディアセッション開始の目的で、マルチメディアセッションを記述するためのものです。SDPには以下が含まれます：

- トランスポートプロトコル（RTP/UDP/IP）
- メディアタイプ（テキスト、音声、ビデオ）
- メディアフォーマットまたはコーデック（H.261ビデオ、g.711音声など）
- これらのメディアを受信するために必要な情報（アドレス、ポートなど）

以下の例は、2台の電話機間の通話を記述するSDPの転写です。

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### SIP NATトラバーサル

Network Address Translation (NAT) は、インターネットIPアドレスを節約するためにほとんどのネットワークで使用されている機能です。通常、企業は小さなIPアドレスブロックを受け取り、エンドユーザーはインターネットに接続する際に動的に1つのIPアドレスを受け取ります。NATは、内部アドレスを外部アドレスにマッピングすることでアドレス問題を解決します。NATは内部アドレスと外部アドレスのマッピングをメモリに保持します。このマッピングは特定の期間のみ有効で、その後破棄されます。マッピングには、内部および外部アドレスのIP:ポートペアが使用されます。NATには4つの種類があります：

- Full Cone
- Restricted Cone
- Port Restricted Cone
- Symmetric

以下のNAT理論（4つのNATタイプ、Contactヘッダーの問題、キープアライブ、サーバー経由のメディア強制）はプロトコルレベルのものであり、あらゆるSIP実装に適用されます。Asterisk 22 (PJSIP) で各動作を設定する方法は、本章の後半「*Nat traversal on res_pjsip*」で解説します。

#### Full Cone

最初のNATであるFull Coneは、外部IP:ポートペアから内部IP:ポートペアへの静的なマッピングを表します。外部のどのコンピュータも、その外部IP:ポートペアを使用して接続できます。これは、フィルタを使用して実装されたステートレスファイアウォールで見られるケースです。

![Full Cone NAT：内部ホスト（10.0.0.1:8000）が外部ペア 200.180.4.168:1234 に静的にマッピングされているため、外部のどのコンピュータもそのペアにパケットを送信して内部ホストに到達できる](../images/07-sip-and-pjsip-fig11.png)

#### Restricted Cone

Restricted Coneシナリオでは、外部IP:ポートペアは、内部コンピュータが外部アドレスにデータを送信したときにのみ開かれます。しかし、Restricted Cone NATは、異なるアドレスからの着信パケットをブロックします。言い換えれば、内部コンピュータは、外部コンピュータからデータを受け取る前に、まずそのコンピュータへデータを送信する必要があります。

#### Port Restricted Cone

Port Restricted Coneファイアウォールは、Restricted Coneとほぼ同じです。唯一の違いは、着信パケットが送信パケットと全く同じIPおよびポートから来る必要があるという点です。

#### Symmetric

最後のNATタイプはSymmetricと呼ばれます。これは、各外部アドレスに対して特定のマッピングが行われる点で、最初の3つとは異なります。NATマッピングによって、特定の外部アドレスからの戻り通信のみが許可されます。NATデバイスによって使用される外部IP:ポートペアを予測することは不可能です。他の3つのNATタイプでは、外部サーバーを使用して通信用の外部IPアドレスを検出できます。Symmetric NATでは、外部サーバーに接続できたとしても、検出されたアドレスはそのサーバー以外のデバイスには使用できません。

![Symmetric NAT：宛先ごとに異なる外部送信元ポートが割り当てられるため、あるサーバーに対して検出されたマッピングを別のホストが再利用できず、STUNベースのトラバーサルが機能しない](../images/07-sip-and-pjsip-fig12.png)

#### NATファイアウォール表

以下の表は、4つのNATタイプをまとめたものです。

| NATタイプ | 最初にデータを送信する必要があるか | 戻りパケット用の外部IP:ポートを特定できるか | 宛先IP:ポートへの着信パケットを制限するか |
| --- | --- | --- | --- |
| Full Cone | いいえ | はい | いいえ |
| Restricted Cone | はい | はい | IPのみ |
| Port Restricted Cone | はい | はい | はい |
| Symmetric | はい | いいえ | はい |

#### NAT越しのSIPシグナリングとRTP

NATトラバーサルにおける最大の問題の一つは、SIPシグナリングと音声（RTP）という2つの問題を解決しなければならないことです。片方向音声の問題のほとんどはNATに関連しています。SIPの興味深い点は、UACがパケットを送信する際、SIPの「Contact」ヘッダーフィールドにIPアドレスを埋め込むことです。通常、これは内部（RFC1918）アドレスであり、このパケットへの応答はインターネット経由でUACにルーティングできません。概念的な修正方法は常に同じです：

- **Contact/Viaアドレスを無視し、パケットが実際に来た場所に返信する。** これはRFC 3581（`rport`）で定義された動作です。PJSIPでは`force_rport=yes`であり、`rewrite_contact=yes`は保存された連絡先を送信元アドレスに書き換えます。
- **RTPが実際に到着したアドレスにメディアを返信する**（Symmetric RTP、歴史的に*comedia*と呼ばれます）。PJSIPでは`rtp_symmetric=yes`です。
- **NATマッピングを開いたままにする。** マッピングがタイムアウトすると、AsteriskはUACにINVITEを送信できなくなります（電話機は発信できても着信できなくなります）。定期的にOPTIONS（*qualify*）を送信することで、ピンホールを開いたままにします。PJSIPでは、これはAORの`qualify_frequency=`で設定します。

ユーザーのNATがSymmetricタイプの場合、あるUACから別のUACへ直接パケットを送信することは不可能です。その場合は、`direct_media=no`を使用してRTPをAsterisk経由に強制する必要があります。これらの設定はほとんどのケースで適切です。Full Cone、Restricted Cone、Port Restricted Coneで有用なSimple Traversal of UDP over NAT (STUN) や、Application Layer Gateway (ALG) といった高度な技術を使用してトラフィックを最適化することも可能です。残念ながら、今日のほとんどのファイアウォール（家庭用DSL/ケーブルルーターでさえ）はSymmetricであり、STUNを使用できません。ALGは問題を解決できる可能性がありますが、ほとんどの場合サポートされていないか、実装されていないか、バグがあります。

#### NAT配下のAsterisk

Asteriskサーバー自体がNAT配下のファイアウォールに設置されることもあります。これはクラウドにデプロイする際によくある状況です。この場合、AsteriskがSIPおよびSDPヘッダー内でプライベートアドレスではなく**パブリック**アドレスをアドバタイズするように、追加の設定が必要です。

概念的には3つのステップがあります：

- ファイアウォールからAsteriskサーバーへ、SIPシグナリングポート（デフォルトでUDP 5060）を転送する。
- ファイアウォールからAsteriskサーバーへ、RTPメディアポート範囲（デフォルトでUDP 10000–20000、`rtp.conf`で設定）を転送する。
- Asteriskに外部アドレスとローカルネットワークを伝え、ヘッダー内のアドレスをパブリックアドレスに置き換えるべきタイミングを認識させる。

PJSIPでは、これら後半の2項目は**トランスポート**の`external_media_address` / `external_signaling_address`および`local_net=`に対応し、RTPポート範囲は引き続き`rtp.conf`で設定します：

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

NAT配下のAsteriskサーバーに対する完全なPJSIP設定例は、本章の後半「*Asterisk Server behind NAT*」で説明します。

### SIPの制限

Asteriskは、着信RTPフローを使用して発信フローを同期します。着信フローが中断されると（無音抑制）、保留音（Music-on-Hold）が途切れます。つまり、Asteriskを使用する電話機やプロバイダー側で無音抑制を使用してはいけません。

## PJSIP: SIPチャネル

PJSIPはAsteriskのSIPチャネルです。Asterisk 12で初めて導入され、長年の開発を経てデフォルトかつ推奨のSIPチャネルとなり、Asterisk 22（現在のLTS）では唯一のSIPチャネルドライバとなっています。PJSIPはTeluuのpjprojectというプロジェクトに基づいています。pjprojectスタックは、多くのソフトフォンや商用SIP実装で採用されており、多機能で成熟したSIPスタックです。

### PJSIPを使用する理由

PJSIPはAsteriskがSIPを扱う方法をゼロから再設計したものであり、標準となった理由である機能を理解する価値があります。

#### 機能

このチャネルは多くの機能をサポートしており、特筆すべきものを挙げます：

- 複数登録：同じAddress of Recordに接続された複数の電話機を使用できます。つまり、同じエンドポイントに2台の電話機を接続できます。
- フレンドリーなアプリケーションプログラミングインターフェース（API）：APIはモジュール式で拡張が容易であり、巨大なコードブロックではなく、連携する小さなモジュール群から構築されています。
- 複数トランスポート：PJSIPを使用すると、複数のアドレス、ポート、トランスポートをリッスンできます。すべてのデバイスに対して単一のバインドアドレスに限定されることはありません。PJSIPは非常に柔軟です。

#### 設定に関する注意

PJSIPの設定はより冗長です。各デバイスが1つのピアブロックではなく複数の関連オブジェクトによって記述されるため、少しの手間と多くの設定行が必要になります。その余分な構造こそがPJSIPに柔軟性を与えており、設定ウィザード（後述）が日々のプロビジョニングを簡潔に保ちます。

### PJSIPモジュール

PJSIPチャネルは、以下に説明する多くのモジュールによって実装されています：

#### res_pjsip

PJSIPのベースレイヤーであり、メインモジュールです。主要なサービスの一部を担います。

#### res_pjsip_session

メディアセッション、SDP処理、およびいくつかのアドオンを担当するモジュールです。

#### res_pjsip_messaging

SIPメッセージを処理し、SIPヘッダーを解析します。

#### res_pjsip_registrar

SIP登録の処理を担当します。

#### res_pjsip_pubsub

subscribe、notify、publishの処理を担当します。これらのメッセージは、SIPプレゼンスおよびBLF (Busy Lamp Field) の処理を担います。

### PJSIP設定

PJSIPには多くの異なるセクションがあります。セクションの形式は以下の通りです：

```
[Section Name]
Option = Value
Option = Value
```

#### エンドポイントセクション

最も重要な設定オブジェクトはエンドポイントです。エンドポイント設定はコア機能であり、AORおよびトランスポートセクションと関連付ける必要があります。例：

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

上記の例を見ると、エンドポイントはすべてのセクションを繋ぐ接着剤のような役割を果たしています。トランスポート、Address of Record、電話機の認証を指定します。また、ダイアルプランへのエントリポイントである最も重要なコンテキストも定義します。

#### Address of Record (AOR)

このオブジェクトは、エンドポイントへの連絡先をAsteriskに伝えます。連絡先アドレスを保存します。また、ボイスメールボックスの設定も可能です。例：

```
[softphone]
type=aor
max_contacts=2
```

#### 認証

このセクションは、インバウンドおよびアウトバウンドの認証を担当します。ドキュメントはサンプルファイル pjsip.conf にあります。例：

```
[softphone]
type=auth
auth_type=userpass
username=softphone
password=#supersecret#
```

#### トランスポート

トランスポートセクションでは、IPv4およびIPv6アドレス、トランスポートプロトコル（TCP、UDP、TLS、Websocketsなど）を定義できます。このセクションでNATアドレスを設定することも可能です。複数のトランスポートを作成できますが、同じIPとポートを共有することはできず、同じIPバージョンの複数のTCPまたはTLSトランスポートをバインドすることもできません。例：

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### 登録

このオブジェクトは、アウトバウンド登録を設定するために使用されます。例：

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### Identify

このオブジェクトは、どのSIPリクエストがどのエンドポイントに属するかを制御します。identifyセクションがない場合、システムは「From」ヘッダーの内容とエンドポイント名を照合します。このセクションを使用すると、ユーザー名やIPによって識別される特定のIPアドレスを特定のエンドポイントに割り当てることができます。例：

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

ACLオブジェクトを使用すると、エンドポイントへのアクセス権を持つ特定のネットワークを設定できます。現在、ACLは特定のセクションまたは acl.conf で定義されます。例：

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### エンティティ間の関係

設定オブジェクト間の関係は、設定に大きな柔軟性を提供します。しかし、初心者には少し複雑に見えるかもしれません。

![PJSIP設定オブジェクト間の関係：エンドポイントはトランスポート、auth、AOR（連絡先を保持）にリンクし、登録はトランスポートとauthに結びつき、identifyはエンドポイントを指し、ACLとドメインエイリアスは独立している](../images/07-sip-and-pjsip-fig14.png)

上記の図は以下を意味します：

#### 関係：

- ENDPOINT/AOR 多対多
- ENDPOINT/AUTH 0対多から0対1
- ENDPOINT/IDENTIFY 0対多から1
- ENDPOINT/AUTH 0対多から1
- ENDPOINT/TRANSPORT 0対多から少なくとも1
- REGISTRATION/AUTH 0対多から0対1
- REGISTRATION/TRANSPORT 0対多から少なくとも1
- AOR/CONTACT 多対多、ACL、DOMAIN_ALIASには関係設定がない

### ソフトフォンの設定

ソフトフォンを設定するには、多くの異なるセクションを定義する必要があります。以下にソフトフォンの設定例を示します。クライアント側にはSipPulse Softphone (https://www.sippulse.com/produtos/softphone) を使用でき、これをダウンロードして以下のエンドポイントに対して登録できます。

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=userpass
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

上記の設定では、ポート5060でUDPのトランスポートを設定し、エンドポイント、ユーザー名とパスワードによる認証、そして最大2つの連絡先を持つAddress of Recordを定義しています。

### SIPトランクの設定

SIPトランクを設定するには、SIPトランクのIPアドレスまたはホスト名、名前、パスワードが必要です。この目的のために新しい登録セクションを作成する必要があります。

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=userpass
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### res_pjsipにおけるNATトラバーサル

Network Address Translationは、IPv4アドレスの不足に対処する方法として大昔に作成されました。多くの人はNATを、ネットワークの内部アドレスをパブリックインターネットから隠すセキュリティ機能としても使用しています。時にはNATトラバーサルを処理しなければならないこともあります。サーバーをクラウドにデプロイする場合など、サーバーがNAT配下にあるケースもあります。クラウドにデプロイする場合、ユーザーもNATルーター配下にいることがよくあります。整理するために、これを2つのパートに分けます。1つ目はクラウドデプロイのようなNAT配下のAsteriskサーバー、2つ目はres_pjsipを使用してNAT配下のクライアントをサポートする方法です。

#### NAT配下のAsteriskサーバー

AsteriskサーバーがNAT配下にある場合、トランスポートセクションで外部アドレスと内部ローカルアドレスを通知する必要があります。以下のディレクティブを使用します。

##### direct_media

メディアはピアツーピアで直接流れるか、サーバーを経由するか？NATの場合、サーバーを経由させる必要があります。NATでは no を選択してください。例：

```
direct_media=no
```

##### external_media_address

外部RTPを処理するためのメディアアドレス。通常は external_signaling_address と同じです。メディアとシグナリングにはサーバーのパブリックIPアドレスを使用してください。例：

```
external_media_address=54.232.1.20
```

##### external_signaling_address

メッセージを受信するための外部SIPアドレス。例：

```
external_signaling_address=54.232.1.20
```

##### local_net

ローカルネットワークと見なすネットワーク。例：

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### NAT配下のAsteriskサーバー用トランスポートの完全な例

NAT配下のAsteriskサーバーを使用するには、2つのステップが必要です。1つ目はNAT配下のトランスポートを定義すること、2つ目はそのトランスポートをエンドポイントに関連付けることです。

##### NAT配下のトランスポートの作成

pjsip.conf ファイル内にNAT配下のトランスポートを作成するには、以下のようなセクションを作成します。

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

トランスポートをエンドポイントに関連付ける

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

SIPトランクの場合は、以下のようにトランスポートを登録セクションにも関連付ける必要があります。

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### NAT配下のクライアントとAsteriskの使用

NAT配下の電話機を使用するには、エンドポイントごとにいくつかの追加パラメータを設定する必要があります。

##### direct_media

メディアはピアツーピアで直接流れるか、サーバーを経由するか？NATの場合、サーバーを経由させる必要があります。例：

```
direct_media=no
```

##### rtp_symmetric

これは*comedia*と呼ばれるものです。SIPで通常行われるSDPヘッダーで定義されたアドレスに頼るのではなく、最初のRTPパケットを受信したアドレスを使用し、同じアドレスに返信します。例：

```
rtp_symmetric=yes
```

##### force_rport

これはRFC3581で定義された動作です。VIAヘッダーのアドレスを使用するのではなく、リクエストが来た場所に応答を返します。例：

```
force_rport=yes
```

##### qualify_frequency

この設定は（エンドポイントではなく）AORに適用する必要があります。最後のステップとして、qualifyオプションを設定します。NATマッピングを開いたままにするために、常に宛先にパケットをpingし続ける必要があります。これはAORセクションで設定します。例：

- qualify_frequency=15

サーバーとクライアントの両方がNAT配下にあるエンドポイントの完全な例

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### チャネルの命名

いつものように、チャネルの重要な側面の一つはその命名であり、PJSIPには興味深い詳細がいくつかあります。PJSIPエンドポイントには`PJSIP/`テクノロジーでダイアルします：

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

便利な機能として、AORに登録されているすべての連絡先を一度にダイアルする可能性があります。関数 PJSIP_DIAL_CONTACTS は、ダイアルする連絡先のリストに変換されます。

```
exten=>6000,dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

トランクへのダイアルは少し異なります。トランクがプラットフォームに登録されない、またはAORに関連付けられたIPアドレスを持たないと仮定します。トランクのアドレスを直接行に指定できます。国際電話を例にします。

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

トランクのアドレスをAORセクションで指定したい場合は、以下も使用できます。

```
exten=>9011.,Dial(PJSIP/${EXTEN:1}@siptrunk
```

### PJSIP設定ウィザード

PJSIPは強力ですが、設定が冗長です。多くの異なるセクションやテンプレートがあり、最初は混乱するかもしれません。幸いなことに、PJSIP設定ウィザードがあります。各チャネルを数行で定義することで、テンプレートを作成し、新しいデバイスの設定を簡素化できます。設定には pjsip_wizard.conf ファイルを使用します。引き続き pjsip.conf ファイル内でトランスポートおよびグローバルセクションを定義する必要があります。個人的には、ウィザードは電話機に対してのみ使用することを好みます。SIPトランクは通常数が多くないため、pjsipで直接設定できます。ウィザードの最大の利点は、テンプレートを使用して電話機を素早く作成できることです。

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### PJSIPのロードとアンロード

PJSIPはAsterisk 22における唯一のSIPチャネルであり、そのモジュールはデフォルトでロードされます。稀なケースとして、IAX2やDAHDIのみを使用するサーバーでPJSIPを無効にするなど、modules.conf ファイルからモジュールのロードを制御したい場合があります。

#### PJSIPを無効にするには

modules.conf ファイルを編集し、以下の行を追加します。

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
noload => res_pjsip_log_forwarder.so
```

### コンソールコマンド

PJSIPエンドポイントの設定が完了したら、設定を確認する方法を見てみましょう。このタスクを支援する多くのコンソールコマンドがあります。pjsip.conf を編集した後、以下のコマンドで設定をリロードします：

```
module reload res_pjsip.so
```

単純な`reload`（または`core reload`）は、PJSIPを含むすべてのモジュールをリロードします。（単独の`pjsip reload`コマンドは存在しないことに注意してください。—`pjsip reload`は`pjsip reload qualify aor|endpoint`の形式でのみ存在します。）利用可能なすべてのPJSIPコンソールコマンドは`help pjsip`で一覧表示できます。

#### pjsip show endpoints

このコマンドは利用可能なエンドポイントを表示します。下の画像はスクリーンショットです。ソフトフォンエンドポイントのアドレスを確認でき、利用可能であることがわかります。

![`pjsip show endpoints`の出力：blink、siptrunk、softphoneエンドポイントをAOR、auth、トランスポート、可用性とともに表示。ソフトフォン連絡先は登録済み（Avail）](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

上記のコマンドで、エンドポイントの各パラメータを確認できます。以下のリストは、現在のパラメータの半分以下に短縮されています。

![`pjsip show endpoint softphone`の出力：100relやallow=(ulaw)からcallerid、connected_line_methodまで、単一エンドポイントの全パラメータリストを表示](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

このコマンドは、設定されたAddress of Recordオブジェクトとその連絡先を一覧表示するため、各エンドポイントに対してAsteriskがどこに通話を送信するかを確認できます。

#### pjsip show registrations

以下のコマンドは、自サーバーによって行われた登録を表示します。

![`pjsip show registrations`の出力：アウトバウンド登録 siptrunk/sip:1020@sip.api4com.com:5600 が Registered ステータスで表示されている](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

listコマンドは少しフレンドリーで、データ量は少ないですが、より適切に構造化されています。エンドポイントのリスト：

![`pjsip list endpoints`の出力：エンドポイントごとのコンパクトな1行リスト（blink、siptrunk、softphone）と、その状態およびチャネル数](../images/07-sip-and-pjsip-fig18.png)

連絡先のリスト：

![`pjsip list contacts`の出力：siptrunkとsoftphoneの連絡先URIをハッシュおよびqualifyステータスとともに表示](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

最も便利なトラブルシューティングコマンドはSIPパケットロガーです。すべてのSIPリクエストと応答が送受信されるたびにコンソールに出力されるため、登録や通話設定の問題を診断する際に非常に貴重です。

```
pjsip set logger on
pjsip set logger off
```

`pjsip set logger host <ip>`を使用して、ログを単一のホストに制限することもできます。

#### pjsip set history on

PJSIPへの素晴らしい追加機能は、履歴の概念です。SIPリクエストと応答をリアルタイムで簡単にキャプチャおよび分析できます。履歴を開始するには、以下のコマンドを使用します。

![`pjsip set history on`を実行すると "PJSIP History enabled" が返される](../images/07-sip-and-pjsip-fig20.png)

これで履歴を表示できます：

![`pjsip show history`の出力：キャプチャされたSIPメッセージ（REGISTER、401 Unauthorized、REGISTER、200 OK）の番号付きテーブル。タイムスタンプ、方向、アドレスを表示](../images/07-sip-and-pjsip-fig21.png)

特定の要求や応答を確認するには、履歴アイテムを表示します：

![`pjsip show history entry`の出力：キャプチャされた単一SIPメッセージの全文。ここではAsterisk 22の`404 Not Found`応答（OPTIONSプローブに対するもの）。Via（`rport`/`received`付き）、Call-ID、From、To、CSeqヘッダー、`Allow`/`Supported`機能、および`Server: Asterisk PBX 22.10.0`ヘッダーを表示](../images/07-sip-and-pjsip-fig22.png)

非常に簡単ですね。いつでも`pjsip set history clear`を使用して履歴をクリアできます。

> **既存の chan_sip/sip.conf システムからの移行ですか？** レガシーの`chan_sip`
> ドライバと、完全な **sip.conf → pjsip.conf 移行ガイド**（概念マッピングテーブルと
> `sip_to_pjsip.py`変換スクリプトを含む）は、「*Legacy channels*」の章で扱っています。

## クイズ

1. SIPアーキテクチャにおいて、リクエストを受け取り、新しい場所を含むリダイレクト応答（`302 Moved Temporarily`など）で回答し、その後のメッセージのパスから外れるコンポーネントはどれですか？
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. 2台の電話機間のSIP通話を処理する際、Asteriskはどのような役割を果たしますか？
   - A. シグナリングパスにのみ留まるSIPプロキシ
   - B. SIPリダイレクトサーバー
   - C. 2つのSIPチャネルをブリッジするBack-to-Back User Agent (B2BUA)
   - D. ステートレスSIP負荷分散装置

3. 電話機が後に通話を受信できるように、現在のIPアドレスをレジストラに伝えるために使用されるSIPメソッドはどれですか？
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. 正誤問題：Asterisk 22では、`chan_sip`および`sip.conf`はPJSIPと並んでレガシーフォールバックとして依然として利用可能です。

5. Asteriskが使用するリッスンソケットを認識し、そのデバイスへの通話送信先を把握するために、エンドポイントを関連付ける必要がある設定オブジェクトはどれですか？（すべて選択してください。）
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. PJSIPの`aor`オブジェクトにおいて、連絡先を定期的にqualifyすることでNATマッピングを開いたままにする設定はどれですか。また、その単位は何ですか？
   - A. `qualify=yes`（ブール値）
   - B. `qualify_frequency`（秒）
   - C. `rtp_timeout`（ミリ秒）
   - D. `nat=force_rport`

7. 空欄を埋めてください：インバウンドSIPリクエストを（`From`ヘッダーではなく）送信元IPアドレスによって特定のエンドポイントに照合させるには、`type=________`を持つセクションを作成します。

8. AsteriskからSIPトランクプロバイダーへの**アウトバウンド**登録を設定するために使用されるPJSIPオブジェクトはどれですか？
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. Asterisk 22 CLIにおいて、すべてのSIPリクエストと応答をコンソールに出力するSIPパケットロガーを有効にするコマンドはどれですか？
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. Symmetric NAT配下の電話機にサービスを提供するPJSIPエンドポイントにおいて、Asteriskがリクエストの送信元アドレスに応答し（RFC 3581）、RTPが実際に到着した場所にメディアを返信するようにする設定のペアはどれですか？
    - A. `direct_media=yes`および`srvlookup=yes`
    - B. `force_rport=yes`および`rtp_symmetric=yes`
    - C. `allowguest=yes`および`insecure=invite`
    - D. `qualify=yes`および`nat=no`

**回答:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
