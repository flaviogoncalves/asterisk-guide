# WebRTC with Asterisk

WebRTC（Web Real-Time Communication）を使用すると、プラグインや外部ソフトフォンを必要とせず、ウェブブラウザだけで通話の発信と受信が可能です。JavaScript、マイク、そして Asterisk への安全な接続さえあれば実現できます。Asterisk は Asterisk 11 以降 WebRTC サーバとして機能でき、PJSIP スタック（`res_pjsip`）が Asterisk 12 に導入されてからはそれが推奨される方法となりました。Asterisk 22 では設定がいくつかの分かりやすいオプションに整理されています。本章では、PJSIP エンドポイントをブラウザ電話に変換する方法、セキュアなメディアパスの仕組み、そして Asterisk の組み込み WebRTC サポートを使用すべきか、専用ゲートウェイを使用すべきかの判断基準を示します。

本章の内容はすべて本書の Asterisk 22 ラボで検証済みです。示されている設定は`lab/asterisk/etc`と同一です。

## 目的

By the end of this chapter, you should be able to:

- Asterisk に WebRTC が追加する機能と使用すべきタイミングを説明する
- WebRTC のメディアセキュリティ (DTLS-SRTP) と ICE が通常の SIP とどのように異なるかを説明する
- Asterisk HTTP サーバーと安全な WebSocket (`wss`) エンドポイントを有効にする
- `wss` PJSIP トランスポートと `webrtc=yes` を使用した WebRTC エンドポイントを設定する
- ブラウザソフトフォン (SIP.js) を接続し、通話を発信する
- Asterisk ネイティブの WebRTC と Janus などのメディアゲートウェイのどちらを使用するか判断する

## Why WebRTC with Asterisk

A WebRTC endpoint is, from Asterisk's point of view, just another PJSIP endpoint.
What changes is *how* the browser reaches it and how media is secured. Typical
uses include:

- **Click-to-call** on a website — a visitor calls a queue or an extension from a
  web page.
- **Web-based agents** — a contact-center agent works entirely in the browser, no
  desktop softphone to install or update.
- **Embedded calling** in your own web application — for example, the SipPulse web
  softphone talking to Asterisk.
- **Zero-install internal phones** — staff use a browser tab instead of a hardware
  phone or installed client.

The big advantage is reach: every modern browser already speaks WebRTC. The cost
is that WebRTC is strict — it *requires* encrypted media and a secure transport,
so there is more to configure than a plain UDP SIP phone.

## How WebRTC differs from plain SIP

通常の SIP 電話は UDP/TCP 上でシグナリングを行い、音声はプレーン RTP として運ばれます。WebRTC ブラウザクライアントは 3 つの重要な点で異なり、Asterisk はそれぞれに対応しなければなりません。

- **Signaling rides a WebSocket.** Instead of SIP over UDP port 5060, the browser
  opens a secure WebSocket (`wss://`) to Asterisk's built-in HTTP server. SIP
  messages travel inside that WebSocket.
- **Media is always encrypted with DTLS-SRTP.** Browsers refuse plain RTP. The two
  sides perform a DTLS handshake (authenticated by certificate fingerprints
  exchanged in the SDP) and derive SRTP keys from it.
- **Connectivity is negotiated with ICE.** Rather than assuming a reachable IP and
  port, both sides gather candidate addresses (host, STUN-reflexive, TURN-relayed)
  and probe them until one works. RTP and RTCP are usually multiplexed on a single
  port (`rtcp_mux`).

The good news: in Asterisk 22 a single endpoint option, `webrtc=yes`, turns all of
this on with sensible defaults. We will see exactly what it sets.

## Step 1 — the HTTP server and the WebSocket

WebRTC signaling is served by Asterisk's built-in HTTP server (`res_http_websocket`  
exposes the `/ws` path on it). Browsers require a *secure* WebSocket, so we enable  
TLS. Edit `http.conf`:

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

Reload (`module reload res_http_websocket` or restart) and confirm:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

The browser will connect to `wss://your-asterisk:8089/ws`.

### About the certificate

The TLS certificate here secures the *WebSocket* (the signaling channel). In a lab  
a self-signed certificate is fine — you accept it once in the browser. In  
production use a real certificate (for example Let's Encrypt) whose name matches  
the host the browser connects to, otherwise the browser will refuse the WebSocket.

For the lab, `lab/make-certs.sh` generates a self-signed certificate with  
`CN=localhost` (plus `localhost`/`127.0.0.1` SANs) and writes it to  
`asterisk/etc/keys/`. For a public deployment, obtain a real certificate instead — for  
example with Let's Encrypt:

```
certbot certonly --standalone -d voip.example.com
```

Then point `http.conf` at the issued files and reload `res_http_websocket`:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Make sure the certificate name matches the host the browser connects to, and renew it  
(certbot's timer does this automatically) before it expires, or the WebSocket will fail.

This certificate is **not** the same as the DTLS certificate used to encrypt the  
media — Asterisk generates that one automatically, as we will see.

## Step 2 — WSSトランスポート

PJSIPは`wss`タイプのトランスポートが必要です。これを`pjsip.conf`に追加します:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

ロードされたことを確認します:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

`wss`トランスポートに表示されている`0.0.0.0:5060`に惑わされないでください — WebSocketはポート5060で提供され**ません**。WebRTCシグナリングはステップ1で設定したHTTPサーバー（`wss`のポート8089）によって提供されます。PJSIP`wss`トランスポートは`res_http_websocket`上の薄いラッパーなので、そこに表示される`bind`アドレスは見た目上のものであり無視して構いません。重要なのは`http.conf`内の`tlsbindaddr`ポートです。

## Step 3 — the WebRTC endpoint

Now the endpoint itself. The key is `webrtc=yes`:

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
auth_type=digest
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` is a convenience switch. It is equivalent to setting all of the
WebRTC-required options by hand. You can confirm exactly what it turned on:

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

Reading that output:

- `media_encryption: dtls` and `dtls_auto_generate_cert: Yes` — media is DTLS-SRTP,
  and Asterisk auto-generates the DTLS certificate, so you do **not** create one
  yourself. The fingerprint is advertised in the SDP (`SHA-256`).
- `ice_support: true` — Asterisk gathers and negotiates ICE candidates.
- `rtcp_mux: true` — RTP and RTCP share one port, as browsers expect.
- `use_avpf: true` — the AVPF RTP profile (feedback), required by WebRTC.

`allow=opus` is recommended — Opus is the codec browsers prefer. Asterisk 22 ships
Opus *passthrough* in core (the `res_format_attr_opus` module), which is enough to
relay Opus between two Opus-capable legs without re-encoding. *Transcoding* Opus to
another codec requires the separate `codec_opus` module, which the official WebRTC
guide lists as optional but highly recommended and which you install on top of the
base build; see the codecs discussion in *Designing a VoIP network*. Keep `ulaw` as a
fallback for bridging to non-WebRTC legs that cannot speak Opus.

## Step 4 — ICE, STUN and TURN

フラットな LAN では、ホスト候補だけの ICE で十分であり、他に何も必要ありません。インターネット越しの場合は、通常 STUN サーバーを追加して Asterisk とブラウザーがパブリックアドレスを検出できるようにし、直接メディアが不可能なケース（対称 NAT、制限的なファイアウォール）に備えて TURN サーバーを用意します。Asterisk をそれらにポイントさせるには、`rtp.conf`をご参照ください。

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

ブラウザは JavaScript（`RTCPeerConnection` `iceServers` リスト）で独自の ICE サーバーを設定しています。純粋に内部だけの展開の場合、STUN/TURN は完全に省略できます。

`turnaddr` はオプションのポート（デフォルトは `3478`）を受け取り、`turnusername` と `turnpassword` がリレーに認証します。STUN はピアが自分のパブリックアドレスを *発見* するのにしか役立ちません — 両端が対称 NAT や制限の厳しいファイアウォールの背後にある場合、直接メディアは不可能で、TURN リレーだけが音声を流すことができます。

**本番環境の推奨:** アドレス発見のためにパブリック STUN サーバー（Google のものなど）を使用して問題ありませんが、実際のトラフィックでパブリック TURN に依存しないでください — TURN リレーはすべてのメディアを中継するため、管理下に置く必要があります。自前の [coturn](https://github.com/coturn/coturn) サーバーを運用してください。長期認証情報を使用した最小構成の `/etc/turnserver.conf` は次のようになります:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

それを`rtp.conf`で Asterisk に指示します:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Give the browser the same TURN server in its `iceServers` list so both legs can relay.  
For production with users on mobile networks or behind corporate firewalls, a  
self-hosted coturn is effectively mandatory。

## Step 5 — the browser client

Any WebRTC SIP library works; two widely used ones are **SIP.js** and **JsSIP**. The
lab includes a minimal SIP.js softphone at `lab/webrtc/index.html`. The essential
part is the transport URL and the credentials:

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

Two browser realities to remember:

- **Secure context.** `getUserMedia` (microphone access) only works on `https://`
  pages or `http://localhost`. Serve the page over HTTPS in production.
- **Accept the cert once.** With a self-signed lab certificate, visit
  `https://your-asterisk:8089/ws` in the same browser first and accept the warning,
  or the WebSocket will fail silently.

The SipPulse web softphone is a production-grade reference client built on these same
primitives.

## WebRTC コールの検証

ブラウザが登録されると、`pjsip show contacts`は動的コンタクトを示し、コールがチャンネルを点灯させます:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

音声が片方向のみ、または全くない場合、ほとんどの場合 ICE または証明書が原因です — 以下のトラブルシューティングを参照してください。

## Asterisk WebRTC とメディアゲートウェイ

Asterisk は WebRTC を直接終端できるが、常に最適なツールとは限らない。

- **Asterisk ネイティブの WebRTC を使用する** のは、ブラウザが PBX 上の *電話*、すなわちエージェントや内部エクステンション、ダイヤルプランに着地するクリック・トゥ・コールである場合。ブラウザは単なる別のエンドポイントとなり、キュー、ボイスメール、IVR などすべてが機能する。
- **専用ゲートウェイ（例: Janus）を使用する** のは、コール制御とは別に多数のブラウザセッションをスケールさせる必要がある場合や、大規模会議/ストリーミングのために選択的転送を行う場合、またはメディアプレーンを PBX から分離したい場合である。ゲートウェイは WebRTC をプレーン SIP にブリッジし、Asterisk は普通の SIP レッグとして認識する。

多くの実際のシステムは両方を組み合わせている。Asterisk がコール制御を担当し、ゲートウェイがブラウザ側のメディアスケーリングを行う。（これは SipPulse の独自スタックの背後にあるアーキテクチャである。）

## トラブルシューティング

- **WebSocket won't connect:** ブラウザがTLS証明書を拒否しました。 `https://host:8089/ws` を直接開いて受け入れるか、信頼できる証明書をインストールしてください。
- **Registers but no audio:** ICEが失敗しました — STUNを追加し、NAT越えの場合はTURNも追加してください。 `pjsip set logger on` を確認し、SDP候補を確認してください。
- **One-way audio:** 通常は片側のNAT/ICE、または共通のコーデックがないことが原因です — `allow=opus,ulaw` を確実にしてください。
- **Call drops at answer:** DTLSハンドシェイクが失敗しました；`dtls_auto_generate_cert` が `Yes` であることと、システム時計が正しいことを確認してください（証明書は時間に敏感です）。

## ラボ

1. `./lab.sh up`を実行し、次に`bash lab/make-certs.sh`を実行してAsteriskを再起動します。
2. `lab/webrtc/index.html`を提供し（`lab/webrtc`からの`python3 -m http.server`）、それを開きます；`https://localhost:8089/ws`で証明書を受け入れます。
3. `webrtc-1000`として登録し、`600`に発信します（エコーテスト）— 自分の声が聞こえるはずです。
4. `6001`として登録されたSipPulse Softphoneから、`1000`をダイヤルしてブラウザを鳴らします。
5. 交渉を検査します：`pjsip set logger on`、通話を開始し、SDP内のDTLSフィンガープリントとICE候補を確認します。

## 概要

WebRTC はブラウザを Asterisk のファーストクラスエンドポイントに変えます。レシピは小さいですが厳格です：TLS を使用した HTTP サーバーを有効にしてブラウザが安全な WebSocket を開けるようにし、`wss` PJSIP トランスポートを追加し、エンドポイント上で`webrtc=yes` を設定します――これにより DTLS‑SRTP（自動生成証明書付き）、ICE、RTP/RTCP の多重化、AVPF プロファイルが有効になります。NAT を通過する場合は STUN/TURN を追加し、ページは HTTPS で提供し、SIP.js（または JsSIP）クライアントを`wss://asterisk:8089/ws` にポイントします。PBX 上のブラウザ電話には Asterisk ネイティブの WebRTC が最もシンプルなパスです；大規模メディアの場合はゲートウェイと組み合わせます。

## Quiz

1. Which transport does a WebRTC browser client use to carry SIP signaling to
   Asterisk?
   - A. Plain UDP on port 5060
   - B. A secure WebSocket (`wss://`) to Asterisk's HTTP server
   - C. TLS on port 5061
   - D. A raw TCP socket on port 8088

2. WebRTC media between the browser and Asterisk is encrypted using which mechanism?
   - A. SDES-SRTP (keys exchanged in the SDP)
   - B. DTLS-SRTP (keys derived from a DTLS handshake)
   - C. IPsec
   - D. Plain RTP — WebRTC does not encrypt media

3. True or false: when you set `webrtc=yes`, you must manually generate and install
   the DTLS certificate used to encrypt the media.

4. On which port does the lab's Asterisk HTTP server expose the **secure** WebSocket
   for WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Which of the following does `webrtc=yes` turn on by default? (Choose all that
   apply.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Fill in the blank: WebRTC negotiates connectivity by having both sides gather and
   probe candidate addresses (host, STUN-reflexive, TURN-relayed) using the
   ________ framework.

7. In `rtp.conf`, which two settings point Asterisk at an external server so it can
   discover its public address and relay media when direct paths fail? (Choose all
   that apply.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. The URL path that Asterisk's `res_http_websocket` exposes for WebRTC signaling is
   ________.

9. According to the chapter, when should you reach for a dedicated media gateway
   (such as Janus) instead of Asterisk-native WebRTC?
   - A. Whenever any browser needs to make a call
   - B. When you must scale many browser media sessions independently of call
     control, do selective forwarding for large conferences, or keep the media plane
     separate from the PBX
   - C. Only when the browser does not support DTLS
   - D. When you want voicemail and IVR to work for the browser endpoint

10. True or false: `getUserMedia` (microphone access) works on any `http://` page, so
    serving the browser softphone over HTTPS is optional.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
