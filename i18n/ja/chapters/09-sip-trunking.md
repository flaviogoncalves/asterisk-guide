# SIP trunking, DID & the PSTN

自分自身にしか電話できない PBX ではあまり役に立ちません。遅かれ早かれ、すべてのシステムは世界の残りの部分――公衆交換電話網（PSTN）、SIP プロバイダー、または別の PBX に接続しなければなりません。その通話を運ぶリンクが **trunk** です。TDM 時代には trunk は物理回線、すなわち T1/E1 PRI やアナログ FXO 回線のバンドルでした。現在ではほとんどの場合 **SIP trunk** であり、インターネットテレフォニーサービスプロバイダー（ITSP）への論理接続が、他のすべてと同じ IP ネットワーク上で運ばれます。

この章では、PJSIP を使用して Asterisk 22 を ITSP に接続する方法、登録ベースと IP ベースの trunk の選択方法、着信 DID 番号を適切な宛先へルーティングする方法、正しい発信者番号と E.164 形式で外部発信を行う方法、そして複数の trunk にまたがるフェイルオーバーと最小コストルーティングの構築方法を示します。最後に trunk の NAT 対応と、モック ITSP として第2の Asterisk（および SIPp）を立ち上げ、trunk を介して実際の通話を行うラボを紹介します。

ここに記載されたすべては、書籍の Asterisk 22.10.0 ラボで検証済みです。trunk オブジェクトのパターンは、*Building your first PBX with PJSIP* および *SIP & PJSIP in depth* で導入されたものと同じです。

## Objectives

この章の終わりまでに、次のことができるようになります。

- PJSIP を使用して Asterisk 22 を ITSP に接続する
- 登録ベースと IP ベース（静的）トランクのどちらかを選択する
- 着信 DID を適切なエクステンション、IVR、またはキューにルーティングする
- 発信時に正しい発信者 ID と E.164 形式でコールをルーティングする
- `${DIALSTATUS}` を使用してトランクのフェイルオーバーと最小コストルーティングを構築する
- トランクのトランスポートとエンドポイントで NAT を処理する

## What is a SIP trunk

SIPトランクは、PBXと別のSIPシステムとの間の論理的な音声経路です。実際にはその「別システム」は次の2つのうちのどちらかです。

- **ITSP（Internet Telephony Service Provider）。** 通話の発信と終端、そして通常は電話番号ブロック（DID）を販売する商用キャリアです。Asteriskをプロバイダーのシグナリングホストにポイントし、プロバイダーが通話を広域PSTNに接続します。これがほとんどの最新システムが電話ネットワークに到達する方法で、電話機器は不要です。
- **PSTNゲートウェイ。** 物理的なPSTNインターフェース（PRIカード、アナログFXOポート、またはGSM/4Gゲートウェイ）を持ち、それらをPBXにSIPとして提示するデバイス（または別のAsterisk）です。ゲートウェイがTDMからSIPへの変換を行い、Asteriskから見ると単なる別のSIPトランクになります。

どちらの場合でも、PJSIPではトランクは**単なるエンドポイント**です。電話用に使用したのと同じオブジェクトファミリー—`endpoint`、`auth`、`aor`、オプションで`identify`と`registration`—がトランクを構築します。違いは詳細にあります。トランクは*アウトバウンド*を認証します（クライアント側なので認証情報は`outbound_auth`に入れ、`auth`ではありません）、通常はユーザーエージェントを登録しません（*あなたが*それに登録するか、既知のIPからトラフィックが送られます）、そして着信呼び出しは`from-pstn`のような専用コンテキストに着地し、`from-internal`ではありません。

> **旧TDMトランクとの比較。** PRIは固定数のBチャネル（T1では23、E1では30）と専用Dチャネルでの呼制御信号（*Legacy channels*章参照）を提供しましたが、SIPトランクには固定チャネル数はありません—容量は帯域幅、プロバイダーのポリシー、そして任意の`max_contacts`/同時通話制限によって決まります。かつてISDN情報要素で運ばれていた発信者番号、DID、通話進行情報は、現在はSIPヘッダーとSDPで運ばれます。

ITSPがトラフィックの交換に同意する方法は2つあり、トランクの構築方法を決定します：**登録ベース**と**IPベース（静的）**です。これらを順に説明します。

## Registration-based trunks

登録ベースのトランクは、プロバイダーが*あなた*に対して*自分*にログインすることを期待するモデルです。Asterisk は定期的に SIP `REGISTER` をプロバイダーに送信し、ユーザー名とパスワードで認証します。これは、電話が PBX に登録するのと同じ方法です。パブリック IP が動的である場合や、NAT の背後にいる場合、またはプロバイダーが顧客を IP アドレスではなく SIP 資格情報で識別する場合に一般的です。

PJSIP では、アウトバウンドログインは専用の `registration` オブジェクトにあります。これは、削除された `chan_sip` ドライバーが `sip.conf` で使用していた単一の `register =>` 行に取って代わります。以下は、前章で検証されたパターンに従った架空のプロバイダーへの完全な登録トランクです — `outbound_auth`（`auth` ではなく）、`server_uri`/`client_uri`（`server`/`client` ではなく）、エンドポイント上の `from_user`/`from_domain`、そして `dtmf_mode=rfc4733` に注意してください。

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

いくつかのポイント:

- **`auth_type=digest`、`userpass` ではありません。** 両方とも同じダイジェスト認証を生成しますが、Asterisk 22 では `userpass`（および古い `md5`）は **非推奨となり、静かに `digest` に変換されます**。新しい設定では `digest` を使用してください；古いファイルや本書の前章では依然として `userpass` が見られます。
- **エンドポイントと登録の両方で `outbound_auth` を使用。** 登録は `REGISTER` の認証に使用し、エンドポイントはプロバイダーがアウトバウンド `INVITE` に対して返す `407 Proxy Authentication Required` に応答するために使用します。これらは 1 つの `auth` オブジェクトを共有できます。
- **`from_user` / `from_domain`。** 多くのプロバイダーは、`From` ヘッダーに自分のアカウント番号とドメインが含まれていない呼び出しを拒否します。この 2 つのオプションはまさにそれを設定します。
- **`contact_user=4830001000`。** これは登録する `Contact` のユーザー部分となり、プロバイダーはどの番号に着信呼び出しを配信すべきかを把握します。これは古い `register =>` 行の `/9999` サフィックスの現代的な等価物です。
- **`retry_interval=60`。** 登録が失敗した場合、60 秒ごとに再試行します。

リロード後、`pjsip show registrations` で登録を確認します。ラボ環境では `itsp.example.com` が実際に応答しないため、テーブルは次のようになります:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

`(exp. Ns)` サフィックスは次の試行までの秒数をカウントダウンし、ゼロを越えると一瞬 `(exp. Ns ago)` と表示されてから再試行が開始されます。実際のプロバイダーに対しては `Status` 列が `Registered` と表示され、次のリフレッシュまでの残り秒数が示されます。`Rejected`（または `Unregistered`）はプロバイダーがログインを受け付けなかったことを意味します — `pjsip set logger on` を有効にし、`401`/`403` の応答を確認してください。ほとんどの場合、ユーザー名、パスワード、または `client_uri` ドメインが間違っています。

## IPベース（静的）トランク

2番目のモデルは登録が全く不要です。プロバイダーはあなたのパブリックIPアドレスを把握しており、直接そこへ呼び出しを送ります。あなたは代わりに、プロバイダーが既知のシグナリングIPへ呼び出しを送ります。認証は **ソースIPアドレス** によって行われ、SIPクレデンシャルではありません。これは、あなたが管理する2つのサーバー間のトランクや、両側が静的アドレスを持つエンタープライズトランクで典型的です。

キーオブジェクトは`identify`です。Asteriskに対し「*この* IPから来たすべてのSIPリクエストは*あの* エンドポイントに属する」と指示します。これがなければ、PJSIPは`From`ユーザーでインバウンドリクエストをエンドポイントにマッチさせようとしますが、キャリアのトラフィックはそれを満たさないため、呼び出しは拒否されるか`anonymous`エンドポイントにフォールバックします。

静的トランクは`registration`オブジェクトを削除し、`identify`を追加します：

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

`match`はIPアドレス、CIDRレンジ、またはホスト名を受け取ります。**ホスト名は設定ロード時に一度だけ解決されます**。したがって、プロバイダーのIPが変更された場合はリロードが必要です。複数のメディアゲートウェイを公開しているキャリアの場合、シグナリングIPをそれぞれ列挙します—`match`を繰り返すか、CIDRを指定できます：

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Asteriskが受け入れる内容は`pjsip show identifies`で確認してください。ラボから取得したものです（`sipp-identify`行はラボの既存SIPpエンドポイントです）：

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

### セキュリティ上の意味

認証なしのIPベーストランクはドアに例えられ、`identify`/`match`が唯一のロックです。範囲を`match`しすぎると、あるいは攻撃者がソースIPを偽装できると、呼び出しは認証されずに`from-pstn`コンテキストに着地します。併用すべき2つの防御策：

- **できるだけ狭くマッチさせる。** 広いCIDRよりも特定のホストIPを優先します。プロバイダーの実際のシグナリングIPだけを`match`に含めます。
- **ACLと組み合わせる。** PJSIPは`type=acl`オブジェクト（または`acl.conf`）を使用して、エンドポイントに到達する前にSIP層でトラフィックをドロップできます：

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

`type=acl`セクションは参照不要です：`res_pjsip_acl`はそのようなすべてのオブジェクトを*すべての*インバウンドSIPトラフィックに適用し、エンドポイントに到達する前に処理します。（オブジェクトの`acl`および`contact_acl`オプションは、上記のようにインラインで`permit`/`deny`を列挙する代わりに、`acl.conf`から名前付きルールリストを取得します。）原則はSIP章と同じで、すべてを拒否し、信頼できるものだけを許可します。そして、トランクコンテキストが何であれ、**認証された明示的なルールなしにPSTNへ再ダイヤルできるコンテキストに到達させてはいけません**—これが古典的な課金詐欺の穴です。

> **どのモデルを使うべきです

## Inbound routing and DID handling

一度インバウンドコールが到着すると、エンドポイントの `context` に着地します — ここが `from-pstn` です。**DID**（Direct Inward Dialing number）とは、プロバイダーがリクエスト URI で渡すダイヤルされた番号のことです。ダイヤルプランでのあなたの仕事は、各 DID を宛先にマッピングすることです：単一のエクステンション、IVR、キュー、またはリンググループです。

プロバイダーが送信する番号は `${EXTEN}` として `from-pstn` にマッチします。どれだけの情報が見えるかはプロバイダー次第です — 完全な E.164 番号（`+4830001000`）を送る場合もあれば、国内番号、あるいは最後の数桁だけを送る場合もあります。実際のインバウンドコールを `pjsip set logger on` で確認し、パターンを書く前にリクエスト URI を確認してください。

### One DID to one extension

最もシンプルなケース — 単一の DID をそのまま電話にルーティングする場合:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### One DID to an IVR (auto attendant)

電話が鳴る代わりにメニューで応答すべきメイン番号:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` はダイヤルプラン章（`Background()` + `WaitExten()`）で構築したオートアテンダントコンテキストです。DID のルーティングは単なる `Goto` です。

### One DID to a queue

サポートラインをコールキューに流す場合:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Many DIDs at once

番号ブロックを購入したとき、パターンを使うことでダイヤルプランを小さく保てます。例えば DID 範囲が `4830003000`–`4830003099` で、プロバイダーが完全な番号を送る場合、各 DID の最後の二桁をエクステンション `60xx` にマップします:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` は最後の二桁を取得します（負のオフセットは右から数えます）。したがって `4830003007` は `PJSIP/6007` を鳴らします。`did => extension` ルックアップテーブルを `GoSub` もしくは Asterisk データベース（`AstDB`/`func_odbc`）で構築すればさらにスケールしますが、数件の番号であれば明示的なパターンが最も分かりやすいです。

> **Catch the unmatched DID.** `from-pstn` に `i`（無効）エクステンションを追加し、誤ってルーティングされたインバウンド番号がアナウンスを再生したり、オペレーターに転送されたりして、黙って切れないようにします:
> 
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Outbound routing, caller-ID and E.164

Outbound calls flow the other way: an internal phone dials a number, your dialplan
matches it, strips any access prefix, sets the caller-ID the provider expects, and
hands the call to the trunk endpoint with `Dial(PJSIP/<number>@itsp)`.

### Sending the call to the trunk

The channel syntax for a trunk is `PJSIP/<number>@<endpoint>`: the part before the
`@` becomes the user portion of the outbound request URI, and the part after the
`@` names the endpoint whose `aor` `contact` supplies the destination host. A
classic "dial 9 for an outside line" rule:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` strips the leading `9` access code before the number is sent. The
pattern `_9NXXXXXXXXX` matches `9` plus a 10-digit number whose first digit is
2–9; adjust it to your dial plan.

### Caller-ID on outbound calls

Most ITSPs ignore — or actively reject — a caller-ID that is not a number you own.
Set the outbound caller-ID number to one of your DIDs with the `CALLERID(num)`
function before `Dial()`, as shown above. You can also set the name:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

If the provider still strips or overrides your caller-ID name, that is their
policy — many carriers source the displayed name from their own CNAM database
keyed on the number, not from your `From` header.

Two endpoint options interact with this:

- **`from_user`** sets the user part of the `From` header at the SIP level, which
  some providers use to identify your account regardless of `CALLERID(num)`.
- **`trust_id_outbound`** (default `no`) controls whether Asterisk will send
  privacy-sensitive identity headers (`P-Asserted-Identity`/`P-Preferred-Identity`)
  outbound. Leave it off unless your provider documents that they want PAI, in
  which case set `trust_id_outbound=yes` and `send_pai=yes`.

### Normalizing to E.164

E.164 is the international number format: a leading `+`, country code, then the
national number, with no spaces or punctuation (for example `+5548999990000` or
`+14155550100`). Carriers increasingly expect — or require — E.164 on the trunk.
Rather than scatter formatting across the dialplan, normalize once in the outbound
context.

A North-American example that accepts a 10-digit local number, an 11-digit
`1`-prefixed number, or an already-E.164 number, and always presents `+1…` to the
trunk:

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

Some providers want the `+`; others want the bare digits. If yours rejects the
`+`, strip it on the way out with `${EXTEN:1}` in the `Dial`. The point is that
all the format knowledge lives in one place, so switching providers — or adding a
second one — is a one-line change.

## Failover and least-cost routing

1 本のトランクだけでは、プロバイダー障害が発生するとアウトバウンドコールができなくなります。2 本以上のトランクがあれば、自動的にフェイルオーバーでき、宛先ごとに最も安価な経路を選択することも可能です — *least-cost routing*（LCR）。

### Failover with `${DIALSTATUS}`

`Dial()` は戻り値として `${DIALSTATUS}` チャネル変数を設定します。フェイルオーバー時に重要になる値は `CHANUNAVAIL`（トランクに全く到達できなかった）と `CONGESTION`（コールが拒否された、例: 全回線がビジー）です。プライマリートランクを試み、もしコールを運べなければバックアップにフォールスルーします:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

`BUSY` や `NOANSWER` でフェイルオーバーしないという意図的な選択に注意してください — それらは *called party* が到達して拒否したことを意味し、別のトランクで再試行すると、すでに「いいえ」と言った電話が再び鳴ります（しかも二回目の通話料金がかかります）。*トランク自体* が失敗したときだけ再ルーティングします。

### A reusable routing subroutine

このロジックをすべてのダイヤルパターンで繰り返すのはミスが起きやすいです。目的番号を受け取り、順番に各トランクを試す `GoSub` ルーチンに分割します:

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

これで、すべてのアウトバウンドパターンは 1 つの `GoSub` 呼び出しになり、トランクの順序は **1 カ所** で定義されます。

### Least-cost routing by destination

真の LCR は、通話先に応じてトランクを選択します。一般的な形としては、宛先プレフィックスにマッチさせ、各クラスの通話を最も安価なプロバイダーに送ります — 例として、国際電話は卸売キャリアへ、ローカル/国内電話はプライマリープロバイダーへ送る、といった具合です:

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

数個以上のプレフィックスがある場合は、ルートテーブルをデータベース（`func_odbc`/`AstDB`）に保存し、ハードコーディングしたパターンの代わりにプレフィックスでトランクを検索します。ダイヤルプランは小さく保たれ、レートはテーブルで管理できるため、ロジックをリロードせずに編集可能です。

## NAT とトランク

NAT はトランク問題の最も一般的な原因で、典型的には一方向オーディオや、トランクは登録されているが着信呼び出しを受け取らないといった症状が現れます。その原因は電話の場合と同じで（*SIP & PJSIP in depth* と *Designing a VoIP network* で取り上げられています）、Asterisk が SIP と SDP で自分のアドレスを広告し、NAT の背後にあるプライベート RFC 1918 アドレスはプロバイダーが戻ってルーティングできません。

トランクに対する対策は二つの部分からなります — **transport**（あなたのパブリックアドレス）側の設定と **endpoint**（プロバイダーのメディアをどのように扱うか）側の設定です。

### transport 側 — あなたのパブリックアドレス

Asterisk サーバ自体が NAT の背後にある場合（プライベート IP と 1:1 のパブリック IP を持つクラウドやオンプレミスのボックス）、transport にパブリックアドレスとローカルネットワークを伝えます。これらのオプションは一度だけ `transport` で設定し、そこを通るすべてのトラフィックに適用されます。

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

- **`external_signaling_address`** — Asterisk が SIP ヘッダー（`Via`、`Contact`）に書き込むパブリック IP で、`local_net`外の宛先向けです。  
- **`external_media_address`** — Asterisk が SDP `c=` 行に書き込むパブリック IP で、RTP が正しい場所に戻ってくるようにします。通常はシグナリングアドレスと同じです。  
- **`local_net`** — Asterisk が内部とみなすネットワークで、LAN ピアに対してアドレスを書き換えません。すべての内部サブネットを列挙してください。

### エンドポイント側 — プロバイダーのメディア

もう一方は、NAT の背後にあるプロバイダー、あるいは SDP に記載されたアドレスとは異なるアドレスからメディアを送信するプロバイダーを扱います。これらはトランクエンドポイントごとに設定します。

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

- **`direct_media=no`** — Asterisk を通してメディアを流すようにし、2 本のレッグが直接会話しないようにします。NAT 環境で必須であり、通話の録音、トランスコード、モニタリングを行う場合にも必要です。  
- **`rtp_symmetric=yes`** — 従来の *comedia* 動作です。SDP が示すアドレスではなく、実際にメディアが届いたアドレスに RTP を返します。  
- **`force_rport=yes`** — `Via` ヘッダーを信用せず、リクエスト元の IP/ポートから SIP に応答します (RFC 3581)。  
- **`rewrite_contact=yes`** — このエンドポイントからのインバウンド SIP メッセージに対し、`Contact` ヘッダー（または適切な `Record-Route` ヘッダー）を、パケットが実際に来た送信元 IP アドレスとポートに書き換えます。このオプションのドキュメントによれば、これは「NAT の背後にあるエンドポイントとサーバーが通信できるようにし」「TCP や TLS などの信頼できるトランスポート接続の再利用を助ける」ものです。

> **Recommendation — phones vs trunks.** `rewrite_contact` は電話機に対してほぼ常に正しい選択です。なぜなら、電話機が広告するコンタクトは通常、ルーティングできないプライベート RFC 1918 アドレスだからです。静的 IP ベースのトランクでは、プロバイダー側のコンタクトはすでに正しいパブリックアドレスであることが多く、書き換えは不要な場合が多いです。いくつかのオペレーターは、登録トランクや NAT 環境の電話機に対してのみ有効にし、他の場合はオフにしています。オプションの効果は上記のインバウンド `Contact`/`Record-Route` 書き換えだけなので、静的トランクで有効にする前に、必ずご利用のキャリアでテストしてください。

任意のエンドポイントに対して効果的な設定を確認するには、`pjsip show endpoint <name>` — `direct_media`、`rtp_symmetric`、`force_rport`、`rewrite_contact` を使用し、パラメータダンプにすべて出力されます。

## Lab — a mock ITSP with a second Asterisk and SIPp

有料のトランクを用意しなくても練習できます。本書のラボでは、プライベート`172.30.0.0/24`ネットワーク上に Asterisk 22.10.0 コンテナと SIPp コンテナがすでに起動しています。SIPp コンテナを「キャリア」とみなし、着信呼び出しを行い、トランクエンドポイントを追加してそれらの呼び出しを`from-pstn`コンテキストに流します。

![A SIP trunk between the Asterisk PBX and the ITSP: the PBX registers as one account, outbound calls dial `PJSIP/<num>@trunk`, and inbound calls land in the `from-pstn` context.](../images/09-sip-trunking-fig01.png)

### 1. Add the trunk endpoint

IP ベースのトランクを`lab/asterisk/etc/pjsip.conf`に追加し、ラボの SIPp ホストと一致させ、着信呼び出しを`from-pstn`に流します:

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

`lab/asterisk/etc/extensions.conf`で、モックキャリアがダイヤルする DID に応答し、再生する`from-pstn`コンテキストを追加し、さらにアウトバウンドルールを追加します:

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

両方のファイルをリロード（`core reload`）し、トランクがロードされたことを確認します:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Place an inbound call across the trunk

SIPp シナリオを PBX に向け、ターゲットユーザーとして DID を指定します。ラボにはすでに`lab/sipp/uac_9000.xml`が用意されており、エクステンション`9000`に INVITE を送ります。これを`uac_did.xml`にコピーし、リクエスト URI／`To`ユーザーを`9000`から`4830001000`に変更して、SIPp コンテナから実行します:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Asterisk コンソールで`from-pstn`が呼び出されるのを確認します（`pjsip set logger on`は着信 INVITE を示し、`core show channels`は`PJSIP/itsp-…`チャンネルが`demo-congrats`を再生していることを示します）。SIPp の送信元 IP が`identify`と一致しているため、認証なしで呼び出しが受け入れられます――静的キャリアトランクの動作と同様です。

### 4. Inspect the trunk

メモ用にトランクの完全な設定を取得します:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) make it a registration trunk

*2 番目* の Asterisk コンテナを実際のレジストラとして立ち上げます。アカウント`4830001000`に対して`endpoint`＋`auth`＋`aor`を設定し、PBX 側ではこの章の冒頭にある`registration`ブロックに置き換えて`identify`ブロックを差し替えます（`server_uri`を 2 番目のコンテナの IP に指すように）。`pjsip show registrations`でステータスが`Registered`と表示されることを確認し、双方向に通話を行います。

## Summary

SIPトランクは PBX を外部と接続し、PJSIP では既に知っている同じ `endpoint` + `auth` + `aor` ファミリから構築されたエンドポイントに、`identify`または`registration`を加えたものです。プロバイダーがユーザー名とパスワードを提供する場合は **registration trunk**（`type=registration` と `outbound_auth`）を使用し、認証が送信元 IP による場合は **IP-based trunk**（`type=identify` と `match`）を使用します。その際、認証されていないトランクは料金詐欺の対象になるため、狭い `match` と `acl` でロックしてください。インバウンドでは、プロバイダーの DID が `${EXTEN}` として `from-pstn` コンテキストに届き、そこからエクステンション、IVR、またはキューへルーティングします——パターンと `${EXTEN:-N}` により DID ブロックをコンパクトに保ちます。アウトバウンドでは、所有する番号を `CALLERID(num)` に設定し、1 カ所で E.164 に正規化し、通話を `PJSIP/<number>@trunk` に渡します。複数のトランクを試みて `${DIALSTATUS}`（`CHANUNAVAIL`/`CONGESTION` は再ルートを意味し、`BUSY`/`NOANSWER` は意味しません）で分岐させ、`GoSub` テーブルに最安値ルーティングを配置してレジリエンスを構築します。最後に、トランクの NAT は双方向です：パブリックアドレス用の **transport** で `external_media_address`/`external_signaling_address`/`local_net`、プロバイダー側メディア用の **endpoint** で `direct_media=no`、`rtp_symmetric`、`force_rport`、および `rewrite_contact` を設定します。

## Quiz

1. PJSIP で、プロバイダーへの *outbound* コールまたは登録を認証するために使用される資格情報は次で参照されます:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. 次の場合に `type=registration` トランクを使用すべきです:
   - A. プロバイダーが送信元 IP アドレスであなたを識別する場合。
   - B. プロバイダーがユーザー名とパスワードを提供し、ログインを期待している場合。
   - C. Asterisk が `REGISTER` を送信したくない場合。
   - D. トランクが、あなたが管理する 2 つの静的 IP サーバー間にある場合。
3. `identify` オブジェクトの `match` オプションは次を受け入れます（該当するものすべて選択）:
   - A. IP アドレス
   - B. CIDR 範囲
   - C. 設定読み込み時に解決されるホスト名
   - D. SIP ユーザー名のみ
4. Asterisk 22 では、`auth_type=userpass` は次のとおりです:
   - A. 唯一の有効な値
   - B. 非推奨となり `digest` に変換される
   - C. 削除され、ロードエラーを引き起こす
   - D. アウトバウンド登録に必須
5. インバウンド DID 番号はダイヤルプランに次の形で届きます:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` がトランクエンドポイントの `context` に含まれる
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. ダイヤルされた DID `4830003007` の下2桁をエクステンションに送信するには、次を使用します:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. トランクへの `Dial()` 後、バックアップトランクにフェイルオーバーすべきで、`${DIALSTATUS}` 値は（2つ選択）:
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. 発信前にプロバイダーに提示する発信者番号を設定するには、次を使用します:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. サーバーが NAT の背後にある場合に Asterisk に *public* アドレスを知らせるオプションは次に設定します:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. トランクエンドポイントの `rtp_symmetric=yes` は Asterisk に次を行わせます:
    - A. RTP を SRTP で暗号化する
    - B. メディアが実際に到着したアドレスに RTP を送り返し、SDP を無視する
    - C. RTP を完全に無効化する
    - D. エンドポイント間で直接メディアを強制する

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
