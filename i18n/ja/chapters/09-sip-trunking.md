# SIP trunking, DID & the PSTN

自分自身にしか電話をかけられないPBXは、あまり役に立ちません。遅かれ早かれ、すべてのシステムは外部の世界（PSTN：公衆交換電話網、SIPプロバイダー、あるいは他のPBX）と接続する必要があります。それらの通話を運ぶリンクが**trunk**です。TDM時代、trunkは物理的な回線（T1/E1 PRIやアナログFXO回線の束）でした。今日では、それはほぼ常に**SIP trunk**です。これは、他のすべてと同じIPネットワーク上で運ばれる、ITSP（Internet Telephony Service Provider）への論理的な接続です。

本章では、PJSIPを使用してAsterisk 22をITSPに接続する方法、登録ベースのtrunkとIPベースのtrunkのどちらを選択すべきか、着信したDID番号を適切な宛先にルーティングする方法、正しい発信者番号（caller-ID）とE.164形式で発信する方法、そして複数のtrunkにまたがるフェイルオーバーと最小コストルーティング（least-cost routing）を構築する方法を解説します。最後に、trunkのNAT処理について説明し、2台目のAsterisk（およびSIPp）を模擬ITSPとして立ち上げ、実際にtrunkを介して通話を行うラボを実施します。

ここでの内容はすべて、本書のAsterisk 22.10.0ラボ環境で検証済みです。trunkオブジェクトのパターンは、『Building your first PBX with PJSIP』および『SIP & PJSIP in depth』で紹介したものと同じです。

## Objectives

本章を終える頃には、以下のことができるようになります：

- PJSIPを使用してAsterisk 22をITSPに接続する
- 登録ベースのtrunkとIPベース（静的）のtrunkを選択する
- 着信DIDを適切なextension、IVR、またはキューにルーティングする
- 正しい発信者番号とE.164形式で発信をルーティングする
- `${DIALSTATUS}`を使用してtrunkのフェイルオーバーと最小コストルーティングを構築する
- trunkのトランスポートおよびエンドポイントにおけるNATを処理する

## What is a SIP trunk

SIP trunkは、あなたのPBXと他のSIPシステムとの間の論理的な音声パスです。実際には、その「他のシステム」は以下の2つのいずれかです：

- **ITSP（Internet Telephony Service Provider）。** 通話の発着信機能と、通常は電話番号のブロック（DID）を販売する商用キャリアです。Asteriskをプロバイダーのシグナリングホストに向けることで、プロバイダーがあなたの通話を広域PSTNに接続します。これが、現代のほとんどのシステムが電話網に到達する方法であり、電話用ハードウェアは不要です。
- **PSTN gateway。** 物理的なPSTNインターフェース（PRIカード、アナログFXOポート、またはGSM/4Gゲートウェイ）を持ち、それらをSIPとしてPBXに提示するデバイス（または別のAsterisk）です。ゲートウェイがTDMからSIPへの変換を行います。Asteriskから見れば、それは単なるSIP trunkの一つに過ぎません。

いずれの場合も、PJSIPにおいてtrunkは**単なるendpoint**です。電話機に使用したのと同じオブジェクトファミリー（`endpoint`、`auth`、`aor`、オプションで`identify`および`registration`）でtrunkを構築します。違いは詳細部分にあります。trunkは*発信*時に認証を行い（あなたがクライアントであるため、資格情報は`outbound_auth`に入り、`auth`には入りません）、通常はユーザーエージェントをあなたに対して登録しません（あなたが*相手*に登録するか、相手が既知のIPからトラフィックを送ってくるかのいずれかです）。また、着信は`from-internal`ではなく`from-pstn`のような専用のcontextに着地します。

> **古いTDM trunkとの比較。** PRIは固定数のBチャネル（T1で23、E1で30）を提供し、専用のDチャネルで通話設定をシグナリングしていました（『Legacy channels』の章を参照）。SIP trunkには固定のチャネル数はありません。容量は、帯域幅、プロバイダーのポリシー、および`max_contacts`/同時通話制限によって決まります。かつてISDN情報要素で運ばれていた発信者番号、DID、通話進行状況は、現在ではSIPヘッダーとSDPで運ばれます。

ITSPがあなたとトラフィックを交換する方法には2種類あり、それによってtrunkの構築方法が決まります。**登録ベース（registration-based）**と**IPベース（静的：IP-based (static)）**です。それぞれについて順に説明します。

## Registration-based trunks

登録ベースのtrunkは、プロバイダーが*あなた*からのログインを期待する場合に使用するモデルです。Asteriskは定期的にSIP `REGISTER`をプロバイダーに送信し、ユーザー名とパスワードで認証を行います。これは、電話機があなたのPBXに登録するのと全く同じ方法です。これは、あなたのパブリックIPが動的である場合、NATの背後にいる場合、あるいはプロバイダーがIPアドレスではなくSIP資格情報によって顧客を識別する場合に一般的です。

PJSIPでは、発信ログインは専用の`registration`オブジェクトに記述されます。これは、削除された`chan_sip`ドライバーが`sip.conf`で使用していた単一の`register =>`行に代わるものです。以下は、本書の以前の章で検証されたパターンに従った、架空のプロバイダーへの完全な登録trunkの例です。なお、`outbound_auth`（`auth`ではない）、`server_uri`/`client_uri`（`server`/`client`ではない）、エンドポイント上の`from_user`/`from_domain`、および`dtmf_mode=rfc4733`に注意してください：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

いくつか注目すべき点があります：

- **`auth_type=digest`（`userpass`ではない）。** どちらも同じダイジェスト認証を生成しますが、Asterisk 22では`userpass`（および古い`md5`）は**非推奨となり、自動的に`digest`に変換されます**。新しい設定では`digest`を優先してください。古いファイルや本書の以前の章では`userpass`を見かけることになります。
- **エンドポイントと登録の両方での`outbound_auth`。** 登録側はこれを使用して`REGISTER`を認証し、エンドポイント側はこれを使用して、プロバイダーが発信`INVITE`に対して送り返してくる`407 Proxy Authentication Required`に応答します。これらは一つの`auth`オブジェクトを共有できます。
- **`from_user` / `from_domain`。** 多くのプロバイダーは、`From`ヘッダーにあなたのアカウント番号と彼らのドメインが含まれていない通話を拒否します。これら2つのオプションは、まさにそれを設定するものです。
- **`contact_user=4830001000`。** これは登録する`Contact`のユーザー部分になるため、プロバイダーはどの番号に着信を配送すべきかを認識できます。これは、古い`register =>`行における`/9999`サフィックスの現代版です。
- **`retry_interval=60`。** 登録が失敗した場合、60秒ごとに再試行します。

リロード後、`pjsip show registrations`で登録を確認します。ラボ環境（`itsp.example.com`が実際には応答しない環境）では、テーブルは以下のようになります：

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

`(exp. Ns)`サフィックスは次の試行までの秒数をカウントダウンします。ゼロになると、再試行が実行される前に短時間`(exp. Ns ago)`と表示されます。実際のプロバイダーに対しては、`Status`列には次のリフレッシュまでの残り秒数が`Registered`として表示されます。`Rejected`（または`Unregistered`）は、プロバイダーがログインを受け入れなかったことを意味します。`pjsip set logger on`をオンにして`401`/`403`の応答を確認してください。ほとんどの場合、ユーザー名、パスワード、または`client_uri`ドメインの誤りです。

## IP-based (static) trunks

2つ目のモデルでは、登録は一切不要です。プロバイダーはあなたのパブリックIPアドレスを知っており、そこに直接通話を送信します。あなたもまた、プロバイダーの既知のシグナリングIPに通話を送信します。認証はSIP資格情報ではなく、**送信元IPアドレス**によって行われます。これは、あなたが管理する2つのサーバー間のtrunkや、両側が静的アドレスを持つ企業向けtrunkで一般的です。

重要なオブジェクトは`identify`です。これはAsteriskに対して「*この*IPから到着するSIPリクエストはすべて*あの*エンドポイントに属する」と伝えます。これがないと、PJSIPは着信リクエストを`From`ユーザーによってエンドポイントに照合しようとしますが、キャリアのトラフィックはこれに適合しないため、通話は拒否されるか、`anonymous`エンドポイントに転送されてしまいます。

静的trunkでは`registration`オブジェクトを削除し、`identify`を追加します：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
```

`match`はIPアドレス、CIDR範囲、またはホスト名を受け入れます。**ホスト名は設定読み込み時に一度だけ解決される**ため、プロバイダーのIPが変更された場合はリロードが必要です。複数のメディアゲートウェイを公開しているキャリアの場合は、各シグナリングIPをリストアップします。`match`を繰り返すか、CIDRを指定できます：

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Asteriskが何を受け入れるかは`pjsip show identifies`で確認してください。ラボ環境からキャプチャしたものです（`sipp-identify`行はラボに既存のSIPpエンドポイントです）：

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### The security implication

認証のないIPベースのtrunkは扉であり、`identify`/`match`はその唯一の鍵です。もし`match`で広すぎる範囲を指定したり、攻撃者が送信元IPを偽装できたりした場合、通話は認証なしであなたの`from-pstn` contextに着地します。以下の2つの防御策を併用してください：

- **可能な限り厳密に照合する。** 広いCIDRよりも特定のホストIPを優先してください。プロバイダーの実際のシグナリングIPのみを`match`に含めます。
- **ACLと組み合わせる。** PJSIPは、`type=acl`オブジェクト（または`acl.conf`）を使用して、トラフィックがエンドポイントに到達する前にSIP層で破棄できます：

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

これをグローバルセクション（`[global]`/`type=global`内の`acl=itsp-acl`）から参照するか、トランスポートごとに適用します。原則はSIPの章と同じです。すべてを拒否し、信頼できるものだけを許可します。また、trunkのcontextが何をするにしても、**意図的かつ認証されたルールなしでPSTNへ発信できるcontextに到達させてはいけません**。それが古典的な通話詐欺（toll-fraud）の穴です。

> **どちらのモデルを使うべきか？** プロバイダーがユーザー名とパスワードを提供してくれる場合は、**登録（registration）**trunkを使用してください。彼らがあなたのIPアドレスを要求し、彼らのIPを教えてくれる場合は、**識別（identify）**trunkを使用してください。一部のプロバイダーは両方をサポートしています。多くの実際のtrunkでは、登録（プロバイダーがあなたを見つけられるようにするため）と識別（プロバイダーのメディアゲートウェイからの着信INVITEが、レジストラ以外のIPから到着しても照合されるようにするため）を組み合わせています。

## Inbound routing and DID handling

着信通話が到着すると、それらはエンドポイントの`context`（ここでは`from-pstn`）に着地します。**DID**（Direct Inward Dialing number：ダイヤルイン番号）は、プロバイダーがリクエストURIで渡してくるダイヤルされた番号に過ぎません。dialplanでのあなたの仕事は、各DIDを適切な宛先（単一のextension、IVR、キュー、またはリンググループ）にマッピングすることです。

プロバイダーが送信してくる番号は、`from-pstn`内の`${EXTEN}`として照合されます。どの程度見えるかはプロバイダー次第です。完全なE.164番号（`+4830001000`）を送ってくる場合もあれば、国内番号のみ、あるいは下数桁のみを送ってくる場合もあります。パターンを書く前に、`pjsip set logger on`で実際の着信を検査し、リクエストURIを確認してください。

### One DID to one extension

最も単純なケース。単一のDIDを電話機に直接ルーティングします：

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### One DID to an IVR (auto attendant)

電話を鳴らすのではなく、メニューで応答すべき代表番号：

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main`は、dialplanの章（`Background()` + `WaitExten()`）で構築した自動応答用contextです。DIDのルーティングは単なる`Goto`です。

### One DID to a queue

コールキューに着地させるべきサポート回線：

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Many DIDs at once

番号ブロックを購入した場合、パターンを使用することでdialplanを小さく保てます。DID範囲が`4830003000`–`4830003099`で、プロバイダーが完全な番号を送信してくる場合、各DIDの下2桁をextension `60xx`にマッピングします：

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}`は下2桁を取得します（負のオフセットは右からカウントします）。したがって、`4830003007`は`PJSIP/6007`を鳴らします。`GoSub`やAsteriskデータベース（`AstDB`/`func_odbc`）で構築された`did => extension`ルックアップテーブルを使用すればさらに拡張可能ですが、少数の番号であれば明示的なパターンが最も明確です。

> **一致しないDIDをキャッチする。** `from-pstn`に`i`（無効）extensionを追加し、ルーティングされていない着信番号が黙って切断されるのではなく、アナウンスを流したりオペレーターを呼び出したりするようにします：
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Outbound routing, caller-ID and E.164

発信通話は逆方向に流れます。内線電話が番号をダイヤルし、dialplanがそれに一致し、アクセスプレフィックスを取り除き、プロバイダーが期待する発信者番号を設定し、通話をtrunkエンドポイントに`Dial(PJSIP/<number>@itsp)`で渡します。

### Sending the call to the trunk

trunkのチャネル構文は`PJSIP/<number>@<endpoint>`です。`@`の前の部分は発信リクエストURIのユーザー部分になり、`@`の後の部分は、その`aor` `contact`が宛先ホストを提供するエンドポイント名を指定します。古典的な「外線発信には9をダイヤル」というルール：

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}`は、番号が送信される前に先頭の`9`アクセスコードを取り除きます。パターン`_9NXXXXXXXXX`は、`9`と、最初の桁が2〜9である10桁の番号に一致します。あなたのdialplanに合わせて調整してください。

### Caller-ID on outbound calls

ほとんどのITSPは、あなたが所有していない番号の発信者番号を無視するか、積極的に拒否します。前述のように、`Dial()`の前に`CALLERID(num)`関数を使用して、発信者番号をあなたのDIDの一つに設定してください。名前を設定することもできます：

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

プロバイダーが依然としてあなたの発信者番号名を削除または上書きする場合、それは彼らのポリシーです。多くのキャリアは、表示名をあなたの`From`ヘッダーからではなく、番号をキーとした彼ら自身のCNAMデータベースから取得しています。

これには2つのエンドポイントオプションが関係します：

- **`from_user`** はSIPレベルで`From`ヘッダーのユーザー部分を設定します。これは、一部のプロバイダーが`CALLERID(num)`に関係なくあなたのアカウントを識別するために使用します。
- **`trust_id_outbound`** （デフォルト`no`）は、Asteriskがプライバシーに関わる識別ヘッダー（`P-Asserted-Identity`/`P-Preferred-Identity`）を発信するかどうかを制御します。プロバイダーがPAIを要求すると文書化していない限り、オフのままにしてください。要求される場合は、`trust_id_outbound=yes`および`send_pai=yes`を設定します。

### Normalizing to E.164

E.164は国際番号形式です。先頭の`+`、国コード、そして国内番号で構成され、スペースや句読点は含みません（例：`+5548999990000`や`+14155550100`）。キャリアはtrunk上でE.164を期待、あるいは要求するようになっています。dialplan全体に形式を散らばらせるのではなく、発信contextで一度だけ正規化します。

10桁のローカル番号、`1`で始まる11桁の番号、または既にE.164形式の番号を受け入れ、常に`+1…`をtrunkに提示する北米の例：

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

`+`を要求するプロバイダーもあれば、数字のみを要求するプロバイダーもあります。もしあなたのプロバイダーが`+`を拒否する場合は、`Dial`内の`${EXTEN:1}`で送信時に取り除いてください。重要なのは、すべての形式知識が一箇所に集約されていることであり、プロバイダーの切り替えや2つ目のプロバイダーの追加が1行の変更で済むということです。

## Failover and least-cost routing

trunkが1つしかない場合、プロバイダーの障害は発信不能を意味します。2つ以上あれば、自動的にフェイルオーバーさせたり、宛先ごとに最も安いルートを選択したり（最小コストルーティング：LCR）できます。

### Failover with `${DIALSTATUS}`

`Dial()`は、戻り値として`${DIALSTATUS}`チャネル変数を設定します。フェイルオーバーで考慮すべき値は、`CHANUNAVAIL`（trunkに全く到達できなかった）と`CONGESTION`（通話が拒否された、例：全回線使用中）です。プライマリtrunkを試し、通話を実行できなかった場合はバックアップにフォールスルーします：

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

`BUSY`や`NOANSWER`でフェイルオーバー**しない**という意図的な選択に注意してください。これらは*相手先*に到達したが拒否されたことを意味するため、別のtrunkで再試行しても、既に断られた電話を再び鳴らすことになり（しかも2回目の通話料金がかかる可能性があります）、無意味です。*trunk自体*が失敗した時のみ再ルーティングしてください。

### A reusable routing subroutine

すべてのダイヤルパターンに対してそのロジックを繰り返すのはエラーの元です。宛先番号を受け取り、各trunkを順番に試す`GoSub`ルーチンにまとめます：

```
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

これで、すべての発信パターンは1回の`GoSub`呼び出しになり、trunkの順序は一箇所だけで定義されます。

### Least-cost routing by destination

真のLCRは、通話の行き先によってtrunkを選択します。一般的な形は、宛先プレフィックスを照合し、通話クラスごとに最も安いプロバイダーに送信することです。例えば、国際通話は卸売キャリアへ、国内通話はプライマリへ送信します：

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

プレフィックスが多数ある場合は、ルートテーブルをデータベース（`func_odbc`/`AstDB`）に保存し、パターンをハードコーディングする代わりにプレフィックスでtrunkを検索します。dialplanは小さく保たれ、料金表はロジックをリロードすることなく編集可能なテーブルに保持されます。

## NAT and trunks

NATはtrunkの問題の最も一般的な原因です。典型的には、片方向音声や、登録はできるが着信を全く受け取れないといった問題です。原因は電話機の場合と同じです（『SIP & PJSIP in depth』および『Designing a VoIP network』で解説）。AsteriskはSIPやSDPの中で自身のアドレスを通知しますが、NATの背後では、それはプロバイダーがルーティングできないプライベートなRFC 1918アドレスです。

trunkの場合、修正には2つの部分があります。**トランスポート**の設定（あなたのパブリックアドレス）と、**エンドポイント**の設定（プロバイダーのメディアをどう扱うか）です。

### On the transport — your public address

Asteriskサーバー自体がNATの背後にある場合（プライベートIPと1:1のパブリックIPを持つクラウドやオンプレミスのボックス）、トランスポートにそのパブリックアドレスと、どのネットワークがローカルであるかを伝えます。これらのオプションは`transport`で一度設定され、その上のすべてのトラフィックに適用されます：

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** — `local_net`外の宛先に対してAsteriskがSIPヘッダー（`Via`、`Contact`）に書き込むパブリックIP。
- **`external_media_address`** — RTPが正しい場所に戻るように、AsteriskがSDPの`c=`行に書き込むパブリックIP。通常はシグナリングアドレスと同じです。
- **`local_net`** — Asteriskが内部として扱うネットワーク。LANピアに対してアドレスを書き換えないようにします。すべての内部サブネットをリストします。

### On the endpoint — the provider's media

もう半分は、プロバイダー自体がNATの背後にいる場合や、単にSDPにあるアドレスとは異なるアドレスからメディアを送信してくる場合を処理します。これらはtrunkエンドポイントごとに設定します：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** — 2つのレグを直接会話させるのではなく、Asteriskを経由してメディアを流し続けます。NATを越える場合には不可欠であり、通話の録音、トランスコード、監視を行う場合にも必要です。
- **`rtp_symmetric=yes`** — 古典的な*comedia*動作。SDPが主張するアドレスではなく、メディアが実際に到着したアドレスにRTPを返送します。
- **`force_rport=yes`** — `Via`ヘッダーを信頼する代わりに、リクエストの送信元IP/ポート（RFC 3581）に対してSIPで応答します。
- **`rewrite_contact=yes`** — このエンドポイントからの着信SIPメッセージに対して、`Contact`ヘッダー（または適切な`Record-Route`ヘッダー）を、パケットが実際に到着した送信元IPアドレスとポートに書き換えます。このオプションのドキュメントにある通り、これは「NATの背後にいるエンドポイントとの通信を助け」、「TCPやTLSのような信頼性の高いトランスポート接続の再利用を助ける」ものです。

> **推奨事項 — 電話機 vs trunk。** `rewrite_contact`は電話機にとってはほぼ常に正しい選択です。なぜなら、電話機が通知する連絡先は通常、到達不可能なプライベートなRFC 1918アドレスだからです。静的なIPベースのtrunkでは、プロバイダーの連絡先は通常すでに正しいパブリックアドレスであるため、書き換えは不要なことが多いです。一部のオペレーターは、そこではオフにしておき、登録trunkやNAT配下の電話機でのみ有効にすることを好みます。このオプションの文書化された効果は、上記の着信`Contact`/`Record-Route`書き換えのみであるため、静的trunkで有効にする前に特定のキャリアでテストするのが安全な慣行です。

エンドポイントの有効な設定は`pjsip show endpoint <name>`で確認できます。`direct_media`、`rtp_symmetric`、`force_rport`、`rewrite_contact`などがパラメータダンプにすべて出力されます。

## Lab — a mock ITSP with a second Asterisk and SIPp

練習のために有料のtrunkは必要ありません。本書のラボでは、Asterisk 22.10.0コンテナとSIPpコンテナがプライベートな`172.30.0.0/24`ネットワーク上で既に実行されています。SIPpコンテナを「着信通話をかけてくるキャリア」として扱い、それらの通話を`from-pstn` contextに着地させるtrunkエンドポイントを追加します。

![Asterisk PBXとITSP間のSIP trunk：PBXは一つのアカウントとして登録し、発信通話は`PJSIP/<num>@trunk`をダイヤルし、着信通話は`from-pstn` contextに着地する。](../images/09-sip-trunking-fig01.png)

### 1. Add the trunk endpoint

ラボのSIPpホストと一致し、着信を`from-pstn`に着地させるIPベースのtrunkを`lab/asterisk/etc/pjsip.conf`に追加します：

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. Route the inbound DID

`lab/asterisk/etc/extensions.conf`に、模擬キャリアがダイヤルするDIDに応答して再生を行う`from-pstn` contextを追加し、発信ルールを追加します：

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

両方のファイルをリロード（`core reload`）し、trunkが読み込まれたことを確認します：

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Place an inbound call across the trunk

DIDをターゲットユーザーとして、SIPpシナリオをPBXに向けます。ラボには既に`lab/sipp/uac_9000.xml`が同梱されており、これはextension `9000`をINVITEします。`uac_did.xml`にコピーし、リクエストURI/`To`ユーザーを`9000`から`4830001000`に変更してから、SIPpコンテナから実行します：

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Asteriskコンソールで通話が`from-pstn`に到達するのを確認します（`pjsip set logger on`は着信INVITEを表示し、`core show channels`は`PJSIP/itsp-…`チャネルが`demo-congrats`を再生していることを示します）。SIPpの送信元IPが`identify`と一致するため、通話は認証なしで受け入れられます。これは静的キャリアtrunkが動作するのと全く同じです。

### 4. Inspect the trunk

メモ用にtrunkの完全な設定をキャプチャします：

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) make it a registration trunk

*2台目*のAsteriskコンテナを本物のレジストラとして立ち上げます。アカウント`4830001000`に対して`endpoint`+`auth`+`aor`を与え、PBX上で`identify`ブロックを本章冒頭の`registration`ブロックと入れ替えます（`server_uri`を2台目のコンテナのIPに向けます）。`pjsip show registrations`でステータスが`Registered`と読み取れることを確認し、各方向に通話をかけます。

## Summary

SIP trunkはあなたのPBXを外部の世界と接続します。PJSIPにおいてそれは、あなたが既に知っている`endpoint` + `auth` + `aor`ファミリーに、`identify`または`registration`を加えただけの単なるエンドポイントです。プロバイダーがユーザー名とパスワードを提供してくれる場合は**登録trunk**（`type=registration`と`outbound_auth`）を使用し、認証が送信元IPによる場合は**IPベースtrunk**（`type=identify`と`match`）を使用してください。後者は、認証なしのtrunkは通話詐欺の標的となるため、狭い`match`と`acl`でロックダウンしてください。着信時、プロバイダーのDIDはあなたの`from-pstn` contextに`${EXTEN}`として到着し、そこでextension、IVR、またはキューにルーティングします。パターンと`${EXTEN:-N}`を使えばDIDブロックをコンパクトに保てます。発信時は、`CALLERID(num)`をあなたが所有する番号に設定し、一箇所でE.164に正規化し、通話を`PJSIP/<number>@trunk`に渡します。複数のtrunkを試し、`${DIALSTATUS}`で分岐させることで回復力を構築します（`CHANUNAVAIL`/`CONGESTION`は再ルーティングを意味し、`BUSY`/`NOANSWER`はそうではありません）。最小コストルーティングは`GoSub`テーブルに入れてください。最後に、trunkのNATは両面対応が必要です。**トランスポート**にはあなたのパブリックアドレス用に`external_media_address`/`external_signaling_address`/`local_net`を、**エンドポイント**にはプロバイダーのメディア用に`direct_media=no`、`rtp_symmetric`、`force_rport`、および`rewrite_contact`を設定します。

## Quiz

1. PJSIPにおいて、プロバイダーへの*発信*通話や登録を認証するために使用される資格情報は、以下を参照します：
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. `type=registration`trunkを使用すべきなのはどのような場合ですか：
   - A. プロバイダーが送信元IPアドレスであなたを識別する場合。
   - B. プロバイダーがユーザー名とパスワードを提供し、ログインを期待する場合。
   - C. Asteriskから`REGISTER`を送信したくない場合。
   - D. trunkがあなたが管理する2つの静的IPサーバー間にある場合。
3. `identify`オブジェクトの`match`オプションが受け入れるもの（すべて選択）：
   - A. IPアドレス
   - B. CIDR範囲
   - C. ホスト名（設定読み込み時に解決）
   - D. SIPユーザー名のみ
4. Asterisk 22において、`auth_type=userpass`は：
   - A. 唯一の有効な値
   - B. 非推奨であり、`digest`に変換される
   - C. 削除されており、読み込みエラーを引き起こす
   - D. 発信登録に必須
5. 着信DID番号はdialplanに以下として到着します：
   - A. `${CALLERID(num)}`
   - B. trunkエンドポイントの`context`における`${EXTEN}`
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. ダイヤルされたDID `4830003007`の下2桁をextensionに送信するには、以下を使用します：
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. trunkへの`Dial()`の後、どの`${DIALSTATUS}`値の場合にバックアップtrunkへフェイルオーバーすべきですか（2つ選択）：
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. 発信時にプロバイダーに提示する発信者番号を設定するには、以下を使用します：
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. サーバーがNATの背後にある場合にAsteriskにその*パブリック*アドレスを伝えるオプションは、どこに設定しますか：
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. trunkエンドポイント上の`rtp_symmetric=yes`は、Asteriskに何を引き起こしますか：
    - A. RTPをSRTPで暗号化する
    - B. SDPを無視し、メディアが実際に到着したアドレスにRTPを返送する
    - C. RTPを完全に無効にする
    - D. エンドポイント間の直接メディアを強制する

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
