# WebRTC with Asterisk

WebRTC (Web Real-Time Communication) を使用すると、Webブラウザからプラグインや外部のsoftphoneを使用することなく、JavaScript、マイク、そしてAsteriskへのセキュアな接続だけで通話の発着信が可能になります。AsteriskはAsterisk 11からWebRTCサーバーとして機能することができ、Asterisk 12でPJSIPスタック（`res_pjsip`）が登場して以来、それが推奨される方法となっています。Asterisk 22では、設定は十分に理解されたいくつかのオプションに集約されました。本章では、PJSIP endpointをブラウザフォンに変える方法、セキュアなメディアパスの仕組み、そしてAsteriskの組み込みWebRTCサポートを使用すべき場合と専用ゲートウェイを使用すべき場合について解説します。

本章の内容はすべて、本書のAsterisk 22ラボ環境で検証済みです。示されている設定は`lab/asterisk/etc`のものと同じです。

## 学習目標

本章を読み終えると、以下のことができるようになります。

- WebRTCがAsteriskに何をもたらし、いつそれを使用すべきかを説明する
- WebRTCのメディアセキュリティ（DTLS-SRTP）とICEが、通常のSIPとどのように異なるかを説明する
- Asterisk HTTPサーバーとセキュアなWebSocket（`wss`）endpointを有効にする
- `wss` PJSIP transportと`webrtc=yes`を使用したWebRTC endpointを設定する
- ブラウザsoftphone（SIP.js）を接続し、通話を発信する
- AsteriskネイティブのWebRTCとJanusのようなメディアゲートウェイのどちらを選択すべきか判断する

## なぜAsteriskでWebRTCなのか

WebRTC endpointは、Asteriskの観点からは単なるPJSIP endpointの一つに過ぎません。変わるのは、ブラウザがどのようにそこに到達するか、そしてメディアがどのように保護されるかという点です。典型的な用途には以下が含まれます。

- Webサイトでの**クリック・トゥ・コール** — 訪問者がWebページからキューやextensionを呼び出します。
- **Webベースのエージェント** — コンタクトセンターのエージェントがブラウザだけで業務を行い、デスクトップsoftphoneのインストールや更新が不要になります。
- **独自のWebアプリケーションへの通話機能の組み込み** — 例えば、SipPulse Web softphoneがAsteriskと通信するようなケースです。
- **インストール不要の社内電話** — スタッフがハードウェア電話やインストール済みクライアントの代わりにブラウザのタブを使用します。

最大の利点は到達範囲の広さです。すべてのモダンブラウザはすでにWebRTCに対応しています。その代償として、WebRTCは厳格であり、暗号化されたメディアとセキュアなトランスポートを*必須*とするため、通常のUDP SIP電話よりも設定項目が多くなります。

## WebRTCと通常のSIPの違い

通常のSIP電話はUDP/TCPでシグナリングを行い、通常は音声データをプレーンなRTPとして伝送します。WebRTCブラウザクライアントは、以下の3つの重要な点で異なり、Asteriskはそれぞれに対応する必要があります。

- **シグナリングはWebSocket上で行われる。** ブラウザはUDPポート 5060でのSIPの代わりに、Asteriskの組み込みHTTPサーバーに対してセキュアなWebSocket（`wss://`）を開きます。SIPメッセージはそのWebSocket内を流れます。
- **メディアは常にDTLS-SRTPで暗号化される。** ブラウザはプレーンなRTPを拒否します。双方はDTLSハンドシェイク（SDPで交換された証明書のフィンガープリントによって認証される）を実行し、そこからSRTPキーを導出します。
- **接続性はICEでネゴシエートされる。** 到達可能なIPとポートを前提とするのではなく、双方が候補アドレス（host、STUN-reflexive、TURN-relayed）を収集し、接続できるまでそれらをプローブします。RTPとRTCPは通常、単一のポート上で多重化されます（`rtcp_mux`）。

朗報として、Asterisk 22では一つのendpointオプション`webrtc=yes`によって、これらすべてを適切なデフォルト設定で有効にできます。次に、それが具体的に何を設定するのかを見ていきます。

## ステップ 1 — HTTPサーバーとWebSocket

WebRTCのシグナリングは、Asteriskの組み込みHTTPサーバーによって提供されます（`res_http_websocket`がその上の`/ws`パスを公開します）。ブラウザは*セキュアな*WebSocketを要求するため、TLSを有効にします。`http.conf`を編集します。

```
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088

; TLS / WSS for WebRTC. Browsers require a secure WebSocket (wss://).
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.crt
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

リロード（`module reload res_http_websocket`または再起動）して確認します。

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

ブラウザは`wss://your-asterisk:8089/ws`に接続します。

### 証明書について

ここでのTLS証明書は*WebSocket*（シグナリングチャネル）を保護するものです。ラボ環境では自己署名証明書で問題ありません。ブラウザで一度受け入れるだけです。本番環境では、ブラウザが接続するホスト名と一致する本物の証明書（Let's Encryptなど）を使用してください。そうしないと、ブラウザはWebSocketを拒否します。

ラボ環境では、`lab/make-certs.sh`が`CN=localhost`（および`localhost`/`127.0.0.1` SAN）を使用して自己署名証明書を生成し、`asterisk/etc/keys/`に書き込みます。公開環境へのデプロイでは、代わりに本物の証明書を取得してください（例えばLet's Encryptを使用します）。

```
certbot certonly --standalone -d voip.example.com
```

次に、`http.conf`を発行されたファイルに向け、リロードします`res_http_websocket`。

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

証明書名がブラウザの接続先ホストと一致していることを確認し、期限切れになる前に更新してください（certbotのタイマーが自動的に行います）。そうしないとWebSocketは失敗します。

この証明書は、メディアを暗号化するために使用されるDTLS証明書とは**別物**です。後者はAsteriskが自動的に生成します。

## ステップ 2 — WSSトランスポート

PJSIPには`wss`タイプのトランスポートが必要です。`pjsip.conf`に追加します。

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

読み込まれたことを確認します。

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

`wss`トランスポートに対して表示される`0.0.0.0:5060`に惑わされないでください。WebSocketはポート 5060では提供**されません**。WebRTCシグナリングは、ステップ1で設定したHTTPサーバー（`wss`の場合はポート 8089）によって提供されます。PJSIPの`wss`トランスポートは`res_http_websocket`上の薄いシム（shim）であるため、表示される`bind`アドレスは装飾的なものであり無視して構いません。重要なポートは`http.conf`内の`tlsbindaddr`です。

## ステップ 3 — WebRTC endpoint

次はendpoint自体です。鍵となるのは`webrtc=yes`です。

```
[webrtc-1000]
type=endpoint
context=internal
disallow=all
allow=opus,ulaw
webrtc=yes
transport=transport-wss
aors=webrtc-1000
auth=webrtc-1000

[webrtc-1000]
type=auth
auth_type=userpass
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes`は便利なスイッチです。これは、WebRTCに必要なすべてのオプションを手動で設定するのと同等です。何が有効になったかを正確に確認できます。

```
*CLI> pjsip show endpoint webrtc-1000
 dtls_auto_generate_cert            : Yes
 dtls_fingerprint                   : SHA-256
 dtls_setup                         : actpass
 ice_support                        : true
 media_encryption                   : dtls
 rtcp_mux                           : true
 use_avpf                           : true
 webrtc                             : yes
```

出力の読み方：

- `media_encryption: dtls`および`dtls_auto_generate_cert: Yes` — メディアはDTLS-SRTPであり、AsteriskがDTLS証明書を自動生成するため、自分で作成する必要は**ありません**。フィンガープリントはSDP（`SHA-256`）でアドバタイズされます。
- `ice_support: true` — AsteriskがICE候補を収集し、ネゴシエートします。
- `rtcp_mux: true` — ブラウザの期待通り、RTPとRTCPが1つのポートを共有します。
- `use_avpf: true` — WebRTCで必須となるAVPF RTPプロファイル（フィードバック）です。

`allow=opus`が推奨されます。Opusはブラウザが優先するcodecです。Asterisk 22はコア（`res_format_attr_opus`モジュール）でOpusの*パススルー*を提供しており、これは再エンコードなしでOpus対応のレグ間でOpusを中継するのに十分です。Opusを別のcodecに*トランスコード*するには、別途`codec_opus`モジュールが必要です。これは公式のWebRTCガイドではオプションとされていますが、強く推奨されており、ベースビルドの上に追加インストールします。『Designing a VoIP network』のcodecに関する議論を参照してください。Opusを話せない非WebRTCレグへのブリッジ用に、`ulaw`をフォールバックとして保持してください。

## ステップ 4 — ICE、STUN、TURN

フラットなLAN上では、ホスト候補を用いたICEだけで十分であり、他には何も必要ありません。インターネット越しの場合、通常はAsteriskとブラウザが自身のパブリックアドレスを発見できるようにSTUNサーバーを追加し、直接メディア通信が不可能な場合（対称型NAT、制限の厳しいファイアウォール）のためにTURNサーバーを追加します。`rtp.conf`でAsteriskにそれらを指定します。

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

ブラウザはJavaScript（`RTCPeerConnection`の`iceServers`リスト）内で独自のICEサーバーを設定します。完全に内部的なデプロイであれば、STUN/TURNを完全にスキップできます。

`turnaddr`はオプションのポート（デフォルトは`3478`）を取ります。`turnusername`と`turnpassword`はリレーへの認証に使用されます。STUNはピアが自身のパブリックアドレスを*発見*するのを助けるだけです。双方が対称型NATや制限の厳しいファイアウォールの背後にいる場合、直接メディア通信は不可能であり、TURNリレーだけが音声を流す唯一の方法となります。

**本番環境への推奨事項：** パブリックSTUNサーバー（Googleのものなど）はアドレス発見には問題ありませんが、実際のトラフィックでパブリックTURNに依存しては**いけません**。TURNはすべてのメディアをリレーするため、自身の管理下に置く必要があります。独自の[coturn](https://github.com/coturn/coturn)サーバーを運用してください。長期認証情報を使用した最小限の`/etc/turnserver.conf`は以下のようになります。

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

次に、`rtp.conf`でAsteriskにそれを指定します。

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

ブラウザの`iceServers`リストにも同じTURNサーバーを指定し、両方のレグがリレーできるようにします。モバイルネットワークや企業ファイアウォールの背後にいるユーザーを抱える本番環境では、セルフホストのcoturnが事実上必須です。

## ステップ 5 — ブラウザクライアント

WebRTC SIPライブラリであればどれでも機能します。広く使われているものに**SIP.js**と**JsSIP**があります。ラボ環境には`lab/webrtc/index.html`に最小限のSIP.js softphoneが含まれています。不可欠なのはトランスポートURLと認証情報です。

```javascript
const ua = new SIP.UserAgent({
  uri: SIP.UserAgent.makeURI('sip:webrtc-1000@your-asterisk'),
  transportOptions: { server: 'wss://your-asterisk:8089/ws' },
  authorizationUsername: 'webrtc-1000',
  authorizationPassword: 'Lab-webrtc-secret',
});
await ua.start();
await new SIP.Registerer(ua).register();
// place a call to the echo test
const inviter = new SIP.Inviter(ua, SIP.UserAgent.makeURI('sip:600@your-asterisk'));
await inviter.invite();
```

ブラウザの現実として覚えておくべき2つの点：

- **セキュアコンテキスト。** `getUserMedia`（マイクへのアクセス）は`https://`ページまたは`http://localhost`でのみ機能します。本番環境ではページをHTTPSで提供してください。
- **証明書を一度受け入れる。** 自己署名ラボ証明書の場合、最初に同じブラウザで`https://your-asterisk:8089/ws`にアクセスして警告を受け入れてください。そうしないとWebSocketがサイレントに失敗します。

SipPulse Web softphoneは、これらと同じプリミティブに基づいて構築された本番グレードのリファレンスクライアントです。

## WebRTC通話の検証

ブラウザが登録されると、`pjsip show contacts`に動的なコンタクトが表示され、通話によってチャネルが点灯します。

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

音声が片方向であったり、聞こえない場合は、ほぼ間違いなくICEか証明書の問題です。以下のトラブルシューティングを参照してください。

## Asterisk WebRTC vs メディアゲートウェイ

AsteriskはWebRTCを直接終端できますが、常にそれが正しいツールとは限りません。

- **AsteriskネイティブのWebRTCを使用する場合：** ブラウザがPBX上の*電話*である場合（エージェント、内線、ダイヤルプランに着信するクリック・トゥ・コールなど）。ブラウザは単なるendpointであり、すべて（キュー、ボイスメール、IVR）が機能します。
- **専用ゲートウェイ（例：Janus）を使用する場合：** 通話制御とは独立して多数のブラウザセッションをスケーリングする必要がある場合、大規模な会議やストリーミングのために選択的転送を行う場合、あるいはメディアプレーンをPBXから分離しておきたい場合。ゲートウェイはWebRTCを通常のSIPにブリッジし、Asteriskからは通常のSIPレグとして見えます。

多くの実システムでは両方を組み合わせています。通話制御にはAsteriskを、ブラウザ側のメディアスケーリングにはゲートウェイを使用します。（これはSipPulse自身のスタックの背後にあるアーキテクチャです。）

## トラブルシューティング

- **WebSocketが接続できない：** ブラウザがTLS証明書を拒否しました。`https://host:8089/ws`を直接開いて受け入れるか、信頼された証明書をインストールしてください。
- **登録はできるが音声がない：** ICEが失敗しました。STUNを追加し、NAT越えの場合はTURNを追加してください。`pjsip set logger on`をチェックし、SDP候補を確認してください。
- **片方向音声：** 通常は片側のNAT/ICEの問題、または共通のcodecがない場合です。`allow=opus,ulaw`を確認してください。
- **応答時に通話が切断される：** DTLSハンドシェイクが失敗しました。`dtls_auto_generate_cert`が`Yes`であることを確認し、システム時刻が正しいことを確認してください（証明書は時間に敏感です）。

## ラボ

1. `./lab.sh up`を実行し、次に`bash lab/make-certs.sh`を実行してAsteriskを再起動します。
2. `lab/webrtc/index.html`（`lab/webrtc`からの`python3 -m http.server`）を提供し、開きます。`https://localhost:8089/ws`で証明書を受け入れます。
3. `webrtc-1000`として登録し、`600`（エコーテスト）に発信します。自分の声が聞こえるはずです。
4. `6001`として登録されたSipPulse Softphoneから、`1000`にダイヤルしてブラウザを呼び出します。
5. ネゴシエーションを検査します。`pjsip set logger on`で通話を発信し、SDP内のDTLSフィンガープリントとICE候補を見つけます。

## まとめ

WebRTCはブラウザを一流のAsterisk endpointに変えます。レシピは小規模ですが厳格です。ブラウザがセキュアなWebSocketを開けるようにTLS付きのHTTPサーバーを有効にし、`wss` PJSIPトランスポートを追加し、endpointに`webrtc=yes`を設定します。これにより、DTLS-SRTP（自動生成証明書付き）、ICE、RTP/RTCP多重化、AVPFプロファイルが有効になります。NATを越える場合はSTUN/TURNを追加し、ページをHTTPSで提供し、SIP.js（またはJsSIP）クライアントを`wss://asterisk:8089/ws`に向けます。PBX上のブラウザフォンにはAsteriskネイティブのWebRTCが最もシンプルなパスであり、大規模なメディアにはゲートウェイと組み合わせてください。

## クイズ

1. WebRTCブラウザクライアントは、SIPシグナリングをAsteriskに運ぶためにどのトランスポートを使用しますか？
   - A. ポート 5060でのプレーンなUDP
   - B. AsteriskのHTTPサーバーへのセキュアなWebSocket（`wss://`）
   - C. ポート 5061でのTLS
   - D. ポート 8088での生のTCPソケット

2. ブラウザとAsterisk間のWebRTCメディアは、どのメカニズムを使用して暗号化されますか？
   - A. SDES-SRTP（SDPで交換されるキー）
   - B. DTLS-SRTP（DTLSハンドシェイクから導出されるキー）
   - C. IPsec
   - D. プレーンなRTP — WebRTCはメディアを暗号化しません

3. 正か誤か：`webrtc=yes`を設定する場合、メディアを暗号化するために使用されるDTLS証明書を手動で生成およびインストールする必要があります。

4. ラボのAsterisk HTTPサーバーは、WebRTC用の**セキュアな**WebSocketをどのポートで公開していますか？
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. `webrtc=yes`はデフォルトで以下のどれを有効にしますか？（すべて選択してください。）
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. 空欄を埋めてください：WebRTCは、双方が候補アドレス（host、STUN-reflexive、TURN-relayed）を収集してプローブすることにより、________フレームワークを使用して接続性をネゴシエートします。

7. `rtp.conf`において、Asteriskがパブリックアドレスを発見し、直接パスが失敗したときにメディアをリレーできるようにするために、外部サーバーを指定する2つの設定はどれですか？（すべて選択してください。）
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. Asteriskの`res_http_websocket`がWebRTCシグナリングのために公開するURLパスは________です。

9. 本章によると、AsteriskネイティブのWebRTCの代わりに専用メディアゲートウェイ（Janusなど）を使用すべきなのはいつですか？
   - A. ブラウザが通話を行う必要があるときはいつでも
   - B. 通話制御とは独立して多数のブラウザメディアセッションをスケーリングする必要がある場合、大規模な会議のために選択的転送を行う場合、あるいはメディアプレーンをPBXから分離しておきたい場合
   - C. ブラウザがDTLSをサポートしていない場合のみ
   - D. ブラウザendpointでボイスメールとIVRを機能させたい場合

10. 正か誤か：`getUserMedia`（マイクへのアクセス）は任意の`http://`ページで機能するため、ブラウザsoftphoneをHTTPSで提供することはオプションです。

**回答：** 1 — B · 2 — B · 3 — 誤（AsteriskがDTLS証明書を自動生成します；`dtls_auto_generate_cert: Yes`） · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — 誤（セキュアコンテキストが必要です：`getUserMedia`は`https://`または`http://localhost`でのみ機能します）
