# WebRTC with Asterisk

WebRTC (Web Real-Time Communication) lets a web browser place and receive calls
with no plugin and no external softphone — just JavaScript, a microphone, and a
secure connection to Asterisk. Since Asterisk 11 the PJSIP stack has been able to
act as a WebRTC server, and in Asterisk 22 the configuration has settled into a
handful of well-understood options. This chapter shows how to turn a PJSIP
endpoint into a browser phone, how the secure media path works, and when you
should reach for Asterisk's built-in WebRTC support versus a dedicated gateway.

Everything in this chapter is verified against the book's Asterisk 22 lab; the
configuration shown is the same one in `lab/asterisk/etc`.

## Objectives

By the end of this chapter, you should be able to:

- Explain what WebRTC adds to Asterisk and when to use it
- Describe how WebRTC media security (DTLS-SRTP) and ICE differ from plain SIP
- Enable the Asterisk HTTP server and the secure WebSocket (`wss`) endpoint
- Configure a `wss` PJSIP transport and a WebRTC endpoint with `webrtc=yes`
- Connect a browser softphone (SIP.js) and place a call
- Decide between Asterisk-native WebRTC and a media gateway such as Janus

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

A regular SIP phone signals over UDP/TCP and usually carries audio as plain
RTP. A WebRTC browser client is different in three important ways, and Asterisk
has to match each one:

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

> **[2nd-ed note]** The lab ships `lab/make-certs.sh`, which generates a self-signed
> cert with `CN=localhost`. For a public deployment, document the Let's Encrypt flow
> and point `tlscertfile`/`tlsprivatekey` at the issued files.

This certificate is **not** the same as the DTLS certificate used to encrypt the
media — Asterisk generates that one automatically, as we will see.

## Step 2 — the WSS transport

PJSIP needs a transport of type `wss`. Add it to `pjsip.conf`:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Verify it loaded:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

> **[2nd-ed note]** The `wss` transport prints a `0.0.0.0:5060` bind address even
> though the actual WebSocket is served by the HTTP server on port 8089. This is
> expected: the `wss` transport is a thin shim over `res_http_websocket`; the `bind`
> line on it is effectively cosmetic. Worth a sentence in the final text so readers
> are not confused by the port.

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
auth_type=userpass
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

`allow=opus` is recommended — Opus is the codec browsers prefer. (`codec_opus` ships
freely with Asterisk 22; see the codecs discussion in *Designing a VoIP network*.)
Keep `ulaw` as a fallback for bridging to non-WebRTC legs.

## Step 4 — ICE, STUN and TURN

On a flat LAN, ICE with host candidates is enough and nothing else is needed. Across
the internet you usually add a STUN server so Asterisk and the browser can discover
their public addresses, and a TURN server for the cases where direct media is
impossible (symmetric NAT, restrictive firewalls). Point Asterisk at them in
`rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

The browser is configured with its own ICE servers in JavaScript (the
`RTCPeerConnection` `iceServers` list). For a purely internal deployment you can skip
STUN/TURN entirely.

> **[2nd-ed note]** Verify whether to recommend a self-hosted coturn for production
> (most real deployments need TURN). Add a short coturn config example if so.

## Step 5 — the browser client

Any WebRTC SIP library works; the two most common are **SIP.js** and **JsSIP**. The
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

## Verifying a WebRTC call

With the browser registered, `pjsip show contacts` shows the dynamic contact, and a
call lights up the channel:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

If audio is one-way or absent, it is almost always ICE or the certificate — see
troubleshooting below.

## Asterisk WebRTC vs a media gateway

Asterisk can terminate WebRTC directly, but it is not always the right tool:

- **Use Asterisk-native WebRTC** when the browser is a *phone* on your PBX — an
  agent, an internal extension, a click-to-call that lands in your dialplan. The
  browser is just another endpoint and everything (queues, voicemail, IVR) works.
- **Use a dedicated gateway (e.g. Janus)** when you need to scale many browser
  sessions independently of call control, do selective forwarding for large
  conferences/streaming, or keep the media plane separate from the PBX. A gateway
  bridges WebRTC to plain SIP, and Asterisk then sees an ordinary SIP leg.

Many real systems combine both: Asterisk for call control, a gateway for
browser-side media scaling. (This is the architecture behind SipPulse's own stack.)

## Troubleshooting

- **WebSocket won't connect:** the browser rejected the TLS certificate. Open
  `https://host:8089/ws` directly and accept it, or install a trusted cert.
- **Registers but no audio:** ICE failed — add STUN, and TURN if across NAT. Check
  `pjsip set logger on` and look at the SDP candidates.
- **One-way audio:** usually NAT/ICE on one side, or a codec with no common match —
  ensure `allow=opus,ulaw`.
- **Call drops at answer:** DTLS handshake failed; confirm `dtls_auto_generate_cert`
  is `Yes` and the system clock is correct (certs are time-sensitive).

## Lab

1. Run `./lab.sh up`, then `bash lab/make-certs.sh` and restart Asterisk.
2. Serve `lab/webrtc/index.html` (`python3 -m http.server` from `lab/webrtc`) and open
   it; accept the cert at `https://localhost:8089/ws`.
3. Register as `webrtc-1000` and call `600` (echo test) — you should hear yourself.
4. From the SipPulse Softphone registered as `6001`, dial `1000` to ring the browser.
5. Inspect the negotiation: `pjsip set logger on`, place a call, and find the DTLS
   fingerprint and ICE candidates in the SDP.

## Summary

WebRTC turns a browser into a first-class Asterisk endpoint. The recipe is small but
strict: enable the HTTP server with TLS so the browser can open a secure WebSocket,
add a `wss` PJSIP transport, and set `webrtc=yes` on the endpoint — which switches on
DTLS-SRTP (with an auto-generated certificate), ICE, RTP/RTCP multiplexing and the
AVPF profile. Add STUN/TURN when crossing NAT, serve your page over HTTPS, and point
a SIP.js (or JsSIP) client at `wss://asterisk:8089/ws`. For browser phones on your
PBX, Asterisk-native WebRTC is the simplest path; for large-scale media, pair it with
a gateway.
