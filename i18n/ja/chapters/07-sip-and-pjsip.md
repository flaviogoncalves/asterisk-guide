# SIP & PJSIP の詳細

SIP はプロトコルであり、PJSIP は Asterisk 22 がそれを使用する方法です。**PJSIP**（`chan_pjsip`、`pjsip.conf`で設定）は Asterisk 22 LTS で唯一の SIP チャネルドライバです。本章では SIP プロトコルの基礎（プロトコルレベルであり、100% 有効です）と、日常的に使用する PJSIP オブジェクトモデルと設定について解説します。廃止されたレガシードライバと移行ガイドは *Legacy channels* 章で取り上げます。

## Objectives

この章の終わりまでに、次のことができるようになります。

- SIP ユーザーエージェント、プロキシ、レジストラ、ゲートウェイの役割を説明できること；
- 基本的な SIP コールフロー（REGISTER、INVITE、暫定応答と最終応答、ACK、BYE）をたどり、SIP メッセージを読めること；
- SDP がメディアセッションをどのように交渉し、NAT が SIP シグナリングと RTP にどのように影響するかを説明できること；
- PJSIP オブジェクトモデル — `endpoint`、`auth`、`aor`、`transport`、`identify`、および `registration` — をマッピングし、オブジェクト同士がどのように参照し合うかを理解できること；
- `pjsip.conf` で SIP 電話とトランクを設定し、NAT トラバーサルオプションを含めること；
- `pjsip show …` CLI コマンドを使用してエンドポイントを検証およびトラブルシューティングできること。

## SIP プロトコルの基礎

Session Initiation Protocol (SIP) は、HTTP や SMTP に似たテキストベースのプロトコルで、ユーザー間の対話型通信セッションを開始、維持、終了するために設計されています。これらのセッションには、音声、ビデオ、チャット、インタラクティブゲームなどが含まれます。SIP は IETF によって定義され、音声通信の事実上の標準となっています。SIP の仕組みを理解することは非常に重要です。Asterisk 22 では SIP 設定は `pjsip.conf` にあり、SIP ベースのシステムで最も頻繁に編集されるファイルの一つです（`extensions.conf`の次に多い）。

### 操作の理論

SIP は、次のコンポーネントを持つシグナリングプロトコルです：User Agent Client、User Agent Servers、SIP Proxies、そして SIP Gateways。以下の図は、これらのコンポーネント間の関係を示しています。

- UAC (user agent client) – クライアントまたは端末で、SIPシグナリングを開始するもの。
- UAS (user agent server) – UACから来るSIPシグナリングに応答するサーバ。
- UA (user agent) – UACとUASの両方を含むSIP端末（電話機やゲートウェイ）。
- Proxy Server – UAからのリクエストを受け取り、対象ステーションが管理下にない場合は他のSIP Proxyへ転送する。
- Redirect Server – リクエストを受け取り、宛先データを含めてUAに返す。直接宛先へ転送しない。
- Location Server – UAからのリクエストを受け取り、この情報でロケーションデータベースを更新する。

Usually, the proxy, redirect, and location servers are hosted within the same hardware and use the same piece of software, which we call the SIP proxy. The SIP proxy is responsible for location database maintenance, connection establishment, and session termination.

![主要なSIPコンポーネント：ユーザーエージェント（UAC/UAS/UA）、レジストラ/プロキシ/リダイレクトサーバー、およびPSTNへのゲートウェイ、エンドポイント間で直接流れるRTPメディア](../images/07-sip-and-pjsip-fig01.png)

#### SIP 登録プロセス

電話が着信を受け取るには、ロケーションデータベースに登録されている必要があります。ロケーションデータベースでは、IP アドレスが名前に結び付けられます。以下の例では、内線 8500 が IP アドレス 200.180.1.1 に結び付けられます。電話番号を必ずしも使用する必要はありません。SIP アーキテクチャでは、登録された内線は flavio@voip.school のようにすることもできます。

![SIP 登録: 電話が REGISTER を送信し、拡張子 8500 を自分の IP アドレスにバインドし、レジストラがロケーションデータベースにコンタクトを保存して 200 OK で応答する](../images/07-sip-and-pjsip-fig02.png)

#### プロキシ操作

When operating as a SIP proxy, the SIP server stays in the middle of the signaling and is capable of advanced routing and billing. The media flow, based on the real time protocol (RTP) still goes directly between the endpoints.

![プロキシの動作: SIPプロキシはシグナリングパス（INVITE/200 OK）に留まり、ロケーションサーバで被呼び出し側を検索し、RTPメディアは両エンドポイント間で直接流れます](../images/07-sip-and-pjsip-fig03.png)

#### リダイレクト操作

When redirecting, the SIP server simply sends a message (e.g., 302 moved temporarily) to the user agent and stays out of the path of new messages. It is very light in terms of resource usage, but you have no control at all. Redirection is sometimes used in load balance designs.

![リダイレクト操作: リダイレクトサーバーは INVITE に 302 Moved Temporarily を返し、contact を含め、呼び出し元が新しい場所へ直接 INVITE/ACK を再送する間、サーバーは横に退く](../images/07-sip-and-pjsip-fig04.png)

#### Asterisk が SIP を処理する方法

Asterisk が SIP プロキシでも SIP リダイレクタでもないことを理解することが重要です。Asterisk はレジストラおよびロケーションサーバの役割を果たすことができますが、実際には 2 つの UAC を自分自身に接続するだけです。したがって、Asterisk はバック・ツー・バック ユーザーエージェント (B2BUA) と見なされます。言い換えれば、2 つの SIP チャネルを接続し、ブリッジします。Asterisk には、SIP チャネル同士が Asterisk を経由せずに直接通信できるようにする再招待メカニズムがあります。PJSIP エンドポイントではこの動作はパラメータ `direct_media` で制御されます。`direct_media=yes` を使用すると、RTP フローはエンドポイント間を直接流れ、サーバーリソースが解放されます。

#### direct_media=yes を使用した SIP の動作

![directmedia=yes を使用した SIP 動作：SIP シグナリングは Asterisk を通過し、RTP オーディオは二つの電話間で直接やり取りされ、サーバーリソースが解放されます](../images/07-sip-and-pjsip-fig05.png)

しかし、Asterisk を使用して通話を転送または録音する必要がある場合は、パラメータ`direct_media=no`を使用して RTP のフローを Asterisk サーバー経由に強制できます。

#### direct_media=no の SIP 操作

![directmedia=no の SIP 動作: SIP シグナリングと RTP オーディオの両方が Asterisk を介してアンカーされ、録音、トランスコード、または通話の転送が可能になります](../images/07-sip-and-pjsip-fig06.png)

#### SIP メッセージ

基本的な SIP メッセージは次のとおりです:

- INVITE – 接続確立
- ACK – 確認応答
- BYE – 接続終了
- CANCEL – 確立していない呼び出しの接続終了
- REGISTER – UAC を SIP プロキシに登録
- OPTIONS – 利用可能性の確認に使用できる
- REFER – SIP 通話を他の相手に転送
- SUBSCRIBE – 通知イベントを購読
- NOTIFY – チャネル情報を送信
- INFO – 各種メッセージを送信（例: DTMF ）
- MESSAGE – インスタントメッセージを送信

SIP の応答はテキスト形式で、簡単に読めます（HTTP メッセージに似ています）。最も重要な応答は次のとおりです:

- 1XX – 情報メッセージ (100–trying, 180–ringing, 183–progress)
- 2XX – 成功したリクエスト完了 (200 – OK)
- 3XX – 呼び出しリダイレクト、リクエストを別の場所へ向ける必要あり (302 – moved temporarily, 305 – use proxy)
- 4XX – エラー (403 – Forbidden)
- 5XX – サーバーエラー (500 – Internal Server Error; 501 – Not implemented)
- 6XX – グローバル失敗 (606 – Not acceptable)

例えば：

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

#### Session description protocol (SDP)

SDP はもともと IETF RFC 2327 で定義され、現在は RFC 4566 によって廃止されています。セッションのアナウンス、セッション招待、その他のマルチメディアセッション開始の目的で、マルチメディアセッションを記述するために使用されます。SDP には以下が含まれます。

- Transport protocol (RTP/UDP/IP)
- Type of media (text, audio, video)
- Media format or codec (H.261 video, g.711 audio, etc.)
- Information needed to receive these media (addresses, ports, etc.)

The following example is a transcription of a SDP describing a call between two phones.

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

### SIP NAT トラバーサル

Network Address Translation (NAT) は、ほとんどのネットワークで使用されているインターネット IP アドレスを節約する機能です。通常、企業は小さな IP アドレスブロックを取得し、エンドユーザーはインターネットに接続すると動的に 1 つの IP アドレスを受け取ります。NAT は内部アドレスを外部アドレスにマッピングすることでアドレス問題を解決します。内部アドレスと外部アドレスのマッピングをメモリに保存します。このマッピングは一定時間だけ有効で、時間が経つと破棄されます。マッピングは内部および外部アドレスの IP:port ペアを使用します。NAT には 4 種類あります:

- フルコーン
- 制限付きコーン
- ポート制限付きコーン
- 対称

以下のNAT理論—4つのNATタイプ、Contactヘッダーの問題、キープアライブ、そしてメディアをサーバー経由で強制する方法—はプロトコルレベルのものであり、任意のSIP実装に適用されます。Asterisk 22（PJSIP）で各動作を設定する方法は、本章の後半で*Nat traversal on res_pjsip*として取り上げられています。

#### フルコーン

最初のNAT、フルコーンは、外部IP:ポートペアから内部IP:ポートペアへの静的マッピングを表します。任意の外部コンピュータは、外部IP:ポートペアを使用してそれに接続できます。これは、フィルタの使用によって実装されたステートレスでないファイアウォールの場合です。

![フルコーンNAT：内部ホスト (10.0.0.1:8000) が外部ペア 200.180.4.168:1234 に静的にマッピングされているため、任意の外部コンピュータがそのペアにパケットを送信でき、内部ホストに到達できます](../images/07-sip-and-pjsip-fig11.png)

#### 制限コーン

In the restricted cone scenario, the external IP:port pair is opened only when the internal computer sends data to an outside address. However, the restricted cone NAT blocks any incoming packets from a different address. In other words, the internal computer has to send data to an external computer before it can send data back.

#### ポート制限コーン

The port restricted cone firewall is almost identical to the restricted cone. The only difference is that, now, the incoming packet has to come from exactly the same IP and port of the sent packet.

#### 対称

最後のタイプの NAT はシンメトリックと呼ばれます。これは最初の 3 種類とは異なり、各外部アドレスに対して個別のマッピングが行われます。NAT マッピングによって戻ってくることが許可されるのは特定の外部アドレスだけです。NAT デバイスが使用する外部 IP:ポートの組み合わせを予測することはできません。他の 3 種類の NAT は、外部サーバーを利用して通信に必要な外部 IP アドレスを検出することができます。シンメトリック NAT では、たとえ外部サーバーに接続できても、検出されたアドレスはそのサーバー以外のデバイスでは使用できません。

![シンメトリックNAT：各宛先ごとに異なる外部送信ポートが割り当てられるため、あるサーバー向けに発見されたマッピングは別のホストでは再利用できず、STUNベースのトラバーサルが失敗します】(../images/07-sip-and-pjsip-fig12.png)

#### NAT ファイアウォールテーブル

The following table summarizes the four types of NAT. → 次の表は、4 つの NAT タイプを要約しています。

| NATタイプ | 最初にデータを送信する必要がある | 戻りパケットの外部IP:ポートを決定できる | 受信パケットを宛先IP:ポートに制限する |
| --- | --- | --- | --- |
| Full Cone | No | Yes | No |
| Restricted Cone | Yes | Yes | Only IP |
| Port Restricted Cone | Yes | Yes | Yes |
| Symmetric | Yes | No | Yes |

#### SIPシグナリングとNAT上のRTP

NAT トラバーサルにおける最大の課題の一つは、SIP シグナリングとオーディオ (RTP) の二つの問題を解決しなければならないことです。ワンウェイオーディオの問題の多くは NAT が原因です。SIP の興味深い点は、UAC がパケットを送信するときに、SIP “Contact” ヘッダーフィールドに IP アドレスを埋め込むことです。通常、これは内部 (RFC1918) アドレスです; このパケットへの応答はインターネット経由で UAC にルーティングできません。概念的な解決策は常に同じです:

- **Contact/Via アドレスは無視し、パケットが実際に来た場所へ返信する。** これは RFC 3581（`rport`）で定義された動作です。PJSIP では`force_rport=yes`で、`rewrite_contact=yes`が保存されたコンタクトを送信元アドレスに書き換えます。  
- **RTP が実際に到着したアドレスにメディアを返す**（対称 RTP、歴史的には *comedia* と呼ばれます）。PJSIP ではこれは`rtp_symmetric=yes`です。  
- **NAT マッピングを開いたままに保つ。** マッピングがタイムアウトすると、Asterisk は UAC に INVITE を送れなくなります――電話は発信はできても受信できなくなります。定期的に OPTIONS（*qualify*）を送信するとピンホールが維持されます。PJSIP ではこれは AOR 上の`qualify_frequency=`です。

ユーザーの NAT が対称型の場合、UAC 同士が直接パケットを送信することはできません。そのような場合は`direct_media=no`を使用して RTP を Asterisk 経由に強制する必要があります。これらの設定はほとんどのケースに適しています。トラフィックを最適化するために、Simple Traversal of UDP over NAT (STUN) や Application Layer Gateway (ALG) などの高度な手法を使用することも可能です。STUN はフルコーン、制限コーン、ポート制限コーンで有効ですが、残念ながら現在の多くのファイアウォール—家庭用 DSL/ケーブルルータでさえ—は対称型であるため使用できません。ALG は問題を解決できる可能性がありますが、ほとんどの場合サポートされていないか、実装されていないか、バグがあるため利用できません。

#### NAT の背後にある Asterisk

Sometimes the Asterisk server itself is implemented behind a firewall with NAT — a very common situation when you deploy in the cloud. In this case it is necessary to do some extra configuration so that Asterisk advertises its **public** address in the SIP and SDP headers instead of its private one.

概念的には3つのステップがあります：

- ファイアウォールから Asterisk サーバへ SIP シグナリングポート（デフォルトは UDP 5060）を転送します。
- ファイアウォールから Asterisk サーバへ RTP メディアポート範囲（デフォルトは UDP 10000–20000、`rtp.conf`で設定）を転送します。
- Asterisk に外部アドレスとローカルネットワークを通知し、ヘッダーにパブリックアドレスを差し込むタイミングを認識させます。

PJSIPでは、これら最後の2つの項目は`external_media_address` / `external_signaling_address`および`local_net=`に**transport**上でマップされ、RTPポート範囲は依然として`rtp.conf`で設定されます:

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

The complete, worked PJSIP configuration for an Asterisk server behind NAT is given later in this chapter under *Asterisk Server behind NAT*.

### SIP の制限

Asterisk は受信 RTP フローを使用して送信フローを同期させます。受信フローが中断される（サイレンス抑制）と、ミュージックオンホールドが途切れます。つまり、Asterisk を使用する電話やプロバイダーでサイレンス抑制を使用すべきではありません。

## PJSIP: the SIP channel

PJSIP は Asterisk の SIP チャネルです。Asterisk 12 で初めて導入され、長年の開発を経てデフォルトかつ推奨される SIP チャネルとなり、現在の LTS である Asterisk 22 では唯一の SIP チャネルドライバです。PJSIP は Teluu のプロジェクト pjproject をベースにしています。pjproject スタックは多くのソフトフォンや商用 SIP 実装で採用されており、汎用性が高く成熟した SIP スタックです。

### Why to use PJSIP

PJSIP は Asterisk が SIP を扱う方式を根本から再設計したものであり、標準となった機能を理解する価値があります。

#### Features

このチャネルは多数の機能をサポートしており、ここでは特に重要なものを挙げます。

- Multiple registrations: You may use more than one phone connected to the same Address of Record. In other words, you can connect two phones to the same endpoint.
- Friendly Application Program Interface (API). The API is modular and easy to extend, built from many small cooperating modules rather than one large block of code.
- Multiple transports: You can listen to multiple addresses, ports and transports when using PJSIP. You are not limited to a single bind address for all your devices. PJSIP is very flexible.

#### A note on configuration

PJSIP の設定はより冗長です。各デバイスが複数の関連オブジェクトで記述されるため、設定行数が増え、多少の手間がかかります。この余分な構造こそが PJSIP の柔軟性を支えており、後述する設定ウィザードが日常的なプロビジョニングを短く保ちます。

### PJSIP modules

PJSIP チャネルは以下の多数のモジュールによって実装されています。

#### res_pjsip

これは PJSIP の基盤層であり、主要モジュールです。主なサービスのいくつかを担当します。

#### res_pjsip_session

このモジュールはメディアセッション、セッション記述プロトコルの処理、およびいくつかのアドオンを担当します。

#### res_pjsip_messaging

Process SIP messages and parse SIP headers.

#### res_pjsip_registrar

Responsible to handle SIP registrations

#### res_pjsip_pubsub

Responsible to process subscribe, notify and publish. These messages are responsible to handle SIP presence and BLF (Busy Lamp Field).

### PJSIP configuration

PJSIP には多数の異なるセクションがあります。セクションの形式は次のとおりです:

```
[Section Name]
Option = Value
Option = Value
```

#### End point section

最も重要な設定オブジェクトは endpoint です。endpoint の設定はコア機能を持ち、AOR と Transport セクションに関連付ける必要があります。Example:

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

If you look at the example above, the endpoint is a kind of glue linking all sections together. It specifies a transport, the address of record and the authentication for a phone. Also defines the most important part, the context entry point in the dialplan.

#### アドレス・オブ・レコード (AOR)

This object tells Asterisk where to contact the endpoint. It stores the contact addresses. It also allow the configuration of mailboxes. Example:

```
[softphone]
type=aor
max_contacts=2
```

#### 認証

このセクションは、インバウンドおよびアウトバウンドの認証を担当します。ドキュメントはサンプルファイル pjsip.conf にあります。例:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### トランスポート

このトランスポートセクションでは、IPV4 および IPV6 アドレスと、TCP、UDP、TLS、Websockets などのトランスポートプロトコルを定義できます。また、このセクションで Natted アドレスを設定することも可能です。複数のトランスポートを作成できますが、同じ IP とポートを共有することはできず、同一 IP バージョンの TCP または TLS トランスポートを複数バインドすることもできません。Example:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### 登録

このオブジェクトはアウトバウンド登録を設定するために使用されます。例：

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### 識別

このオブジェクトは、どの SIP リクエストが各エンドポイントに属するかを制御します。identify セクションがない場合、システムは “From” ヘッダーの内容をエンドポイント名と照合します。このセクションを使用すると、ユーザー名または IP で識別される特定のエンドポイントに、特定の IP アドレスを割り当てることができます。例:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

ACLオブジェクトを使用すると、エンドポイントへのアクセスを許可する特定のネットワークを設定できます。現在、ACLは特定のセクションまたは `acl.conf` で定義されます。例:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### エンティティ間の関係

設定オブジェクト間の関係は、設定に大きな柔軟性を提供します。しかし、初心者にとってはやや複雑に感じられることがあります。

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

上の図は次のことを意味します。

#### 関係:

| Objects | Cardinality |
| --- | --- |
| ENDPOINT / AOR | 多対多 |
| ENDPOINT / AUTH | 0〜多、0〜1 |
| ENDPOINT / IDENTIFY | 0〜1 |
| ENDPOINT / TRANSPORT | 0〜多、少なくとも1 |
| REGISTRATION / AUTH | 0〜多、0〜1 |
| REGISTRATION / TRANSPORT | 0〜多、少なくとも1 |
| AOR / CONTACT | 多対多 |

ACL と DOMAIN_ALIAS は他のオブジェクトとの直接的な設定関係を持ちません。

### ソフトフォンの設定

ソフトフォンを設定するには、さまざまなセクションを定義する必要があります。以下はソフトフォンの設定例です。クライアント側には SipPulse Softphone (https://www.sippulse.com/produtos/softphone) を使用でき、ダウンロードして下記のエンドポイントに登録できます。

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
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

上記の設定は、ポート 5060 の UDP 用トランスポートを設定し、エンドポイントとその認証（ユーザー名とパスワード）を定義し、さらに最大 2 つのコンタクトを持つ Address of Record を設定します。

### SIPトランクの設定

SIP トランクを設定するには、SIP トランクの IP アドレスまたはホスト名、名前、パスワードが必要です。この目的のために新しい registration セクションを作成する必要があります。

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
auth_type=digest
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

### Nat traversal on res_pjsip

Network Address Translation は、IPv4 アドレス不足への対策として昔から作られました。多くの人が NAT を、内部ネットワークのアドレスをインターネット上から隠すセキュリティ機能としても利用しています。時には NAT トラバーサルを処理しなければならないことがあります。サーバー自体が NAT の背後にある場合もあり、たとえばクラウド上にサーバーをデプロイするケースです。クラウドにデプロイする場合、ユーザー側も NAT ルータの背後にいることが多くなります。整理のため、これを二つに分けて説明します。最初はクラウドデプロイなどで NAT の背後にある Asterisk サーバーについてです。第二部では、クライアントが NAT の背後にある場合に res_pjsip でどのように対応するかを取り上げます。

#### Asterisk Server behind NAT

Asterisk サーバーが NAT の背後にある場合、transport セクションで外部アドレスと内部ローカルアドレスを通知する必要があります。以下のディレクティブを使用します。

##### direct_media

メディアはピアツーピアで直接流れるべきか、サーバーを経由すべきかです。NAT 環境ではサーバーを経由させる必要があります。NAT では **no** を選択します。例:

```
direct_media=no
```

##### external_media_address

外部RTPを処理するためのメディアアドレス。通常は external_signaling_address と同じです。メディアとシグナリングにはサーバーのパブリックIPアドレスを使用します。例:

```
external_media_address=54.232.1.20
```

##### external_signaling_address

外部 SIP アドレスで、メッセージを受信する場所です。例:

```
external_signaling_address=54.232.1.20
```

##### local_net

あなたがローカルネットワークとみなすネットワークです。例:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### 完全な例：NAT 背後の Asterisk サーバー用トランスポート

NAT 背後の Asterisk サーバーを使用するには、2 つの手順が必要です。まず、NAT 背後のトランスポートを定義します。次に、そのトランスポートをエンドポイントに関連付けます。

##### NAT 背後のトランスポートの作成

NAT 背後のトランスポートを作成するには、`pjsip.conf` ファイルに以下のようなセクションを作成します。

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

# トランスポートをエンドポイントに関連付ける

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

SIPトランクの場合、以下のようにトランスポートを登録セクションに関連付ける必要があります。

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### NAT 背後のクライアントで Asterisk を使用する

NAT 背後の電話を使用するには、エンドポイントごとにいくつかの追加パラメータを設定する必要があります。

##### direct_media

メディアはピアツーピアで直接流れるか、サーバーを経由して流れるかのどちらでしょうか？ NAT の場合、サーバーを経由して流すべきです。例:

```
direct_media=no
```

##### rtp_symmetric

これは私たちが「comedia」と呼ぶものです。通常のSIPで使用されるSDPヘッダーに定義されたアドレスに依存する代わりに、最初のrtpパケットを受信したアドレスを使用し、同じアドレスから返信します。例:

```
rtp_symmetric=yes
```

##### force_rport

これはRFC3581で定義された動作です。VIAヘッダーのアドレスを使用するのではなく、リクエストが来ている場所から応答を返します。例:

```
force_rport=yes
```

##### qualify_frequency

この設定はエンドポイントではなく AOR に適用しなければなりません。最後のステップとして、qualify オプションを設定します。NAT マッピングを開いたままにするために、常に宛先にパケットを ping させておく必要があります。これは AOR セクションで設定します。例:

- qualify_frequency=15

サーバーとクライアントの両方が NAT の背後にあるエンドポイントの完全な例

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

### チャネル命名

通常、チャネルの重要な側面の一つはその命名であり、PJSIP にはいくつか興味深い詳細があります。PJSIP エンドポイントは `PJSIP/` テクノロジーでダイヤルします。

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

A useful feature is the possibility to dial all contacts registered to an AOR at once. The function PJSIP_DIAL_CONTACTS will be translated to the list of contacts to dial.

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

トランクにダイヤルする方法はやや異なります。トランクがプラットフォームに登録されていない、または AOR（アドレス・オブ・レコード）に関連付けられた IP アドレスを持っていないと仮定します。トランクのアドレスを直接行に指定できます。例として国際ダイヤルを使用します。

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

トランクのアドレスを AOR セクションで指定したい場合は、こちらも使用できます。

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### PJSIP configuration wizard

PJSIP は強力ですが、設定が冗長になりがちです。さまざまなセクションがあり、テンプレートは最初は混乱しやすいです。そこで便利なのが PJSIP 設定ウィザードです。数行で各チャンネルを定義することで、テンプレートを作成し、新しいデバイスの設定を簡素化できます。設定には `pjsip_wizard.conf` ファイルを使用します。`pjsip.conf` でトランスポートとグローバルセクションを定義する必要があります。個人的には、電話機だけにウィザードを使用し、SIP トランクは通常数が少ないため直接 `pjsip` で設定する方が好みです。ウィザードの最大の利点は、テンプレートを利用して電話機を素早く作成できることです。

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

### Loading and unloading PJSIP

PJSIP は Asterisk 22 の唯一の SIP チャネルであり、モジュールはデフォルトでロードされます。まれに、modules.conf ファイルからモジュールのロードを制御したい場合があります。たとえば、IAX2 または DAHDI のみを使用するサーバーで PJSIP を無効にしたいときなどです。

#### To disable PJSIP

Edit the file modules.conf and add the following lines.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### コンソールコマンド

PJSIP エンドポイントの設定が完了したので、設定を確認する方法を見てみましょう。この作業を支援するコンソールコマンドが多数用意されています。pjsip.conf を編集した後は、次のコマンドで設定をリロードします。

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

#### pjsip show registrations

The command below shows the registrations made by our own server.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listing contacts:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems。

```
pjsip set logger on
pjsip set logger off
```

You can also restrict the logging to a single host with `pjsip set logger host <ip>`.

#### pjsip set history on

A great addition to PJSIP is the concept of history. You can capture and analyse SIP request and replies in real time in an easy way. To start history use the command below.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Now you can show the history:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

Then to see a specific request or reply, show the history item:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

Very easy, isn’t it? You may also clear the history whenever you want using `pjsip set history clear`.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Summary

SIP は IETF のシグナリングプロトコルで、メディアセッションの確立、変更、切断を行います。ユーザーエージェント、プロキシ、レジストラ、ゲートウェイはテキストベースのメッセージ — REGISTER、INVITE、暫定応答と最終応答、ACK、BYE — を交換し、SDP がコーデックを交渉し、RTP がメディアを運びます。そのプロトコル理論は時代を超えて有効であり、あらゆる SIP 実装に適用できます。

Asterisk 22 では **PJSIP**（`chan_pjsip`）を通して SIP を使用し、`pjsip.conf`で設定します。単一のモノリシックなピアの代わりに、デバイスは小さな相互参照オブジェクトの集合としてモデル化されます：`endpoint`（通話動作とコーデック）、`auth`（認証情報）、`aor`（到達可能場所）、`transport`（リスナー）、さらにサービスプロバイダー向けに`identify`（IP でトランクをマッチ）と`registration`（アウトバウンド登録）があります。これらのオブジェクトがどのように組み合わさるか、電話とトランクの両方をどのように設定するか、NAT 通過オプション（`force_rport`、`rewrite_contact`、`rtp_symmetric`、`direct_media`、およびトランスポートの`external_*`/`local_net`）が実際の導入でどのように問題を解決するか、そして`pjsip show endpoints`、`aors`、`contacts`、`registrations`でそれらすべてをどのように検査できるかを見ました。

## Quiz

1. SIP アーキテクチャにおいて、リクエストを受け取り新しい場所を示すリダイレクトレスポンス（例: `302 Moved Temporarily`）で応答し、その後はフォローアップメッセージの経路から外れるコンポーネントはどれですか？
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. Asterisk が 2 台の電話間の SIP コールを処理する際の役割は何ですか？
   - A. シグナリングパスにのみ残る SIP プロキシ
   - B. SIP リダイレクトサーバ
   - C. 2 つの SIP チャネルを橋渡しする back-to-back user agent (B2BUA)
   - D. ステートレスな SIP ロードバランサ

3. 電話がレジストラに現在の IP アドレスを通知し、後で着信を受け取れるようにするために使用する SIP メソッドはどれですか？
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. 真偽: Asterisk 22 では、`chan_sip` と `sip.conf` は PJSIP と併存するレガシーフォールバックとしてまだ利用可能です。

5. エンドポイントがどのリスニングソケットを使用し、デバイスへの呼び出しをどこに送るかを Asterisk が認識できるようにするために、エンドポイントが関連付けられる必要がある設定オブジェクトはどれですか？（該当するものすべてを選択。）
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. PJSIP `aor` オブジェクトにおいて、NAT マッピングを定期的にコンタクトを確認することで開いたままに保つ設定はどれで、その単位は何ですか？
   - A. `qualify=yes` (boolean)
   - B. `qualify_frequency` (seconds)
   - C. `rtp_timeout` (milliseconds)
   - D. `nat=force_rport`

7. 空欄を埋めてください: inbound SIP リクエストを `From` ヘッダーではなく送信元 IP アドレスで特定のエンドポイントにマッチさせるために、`type=________` を使用してセクションを作成します。

8. Asterisk から SIP トランクプロバイダへの **outbound** 登録を設定するために使用される PJSIP オブジェクトはどれですか？
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. Asterisk 22 CLI で、すべての SIP リクエストとレスポンスをコンソールに出力する SIP パケットロガーを有効にするコマンドはどれですか？
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. 対称 NAT の背後にある電話にサービスを提供する PJSIP エンドポイントで、Asterisk がリクエストの送信元アドレス（RFC 3581）に応答し、RTP が実際に到着する場所にメディアを返すようにする設定の組み合わせはどれですか？
    - A. `direct_media=yes` と `srvlookup=yes`
    - B. `force_rport=yes` と `rtp_symmetric=yes`
    - C. `allowguest=yes` と `insecure=invite`
    - D. `qualify=yes` と `nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
