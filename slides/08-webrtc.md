---
theme: seriph
title: 'WebRTC with Asterisk'
info: |
  ## Asterisk Guide — Chapter 6
  WebRTC with Asterisk. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# WebRTC with Asterisk

Chapter 6

<div class="abs-bl m-6 text-sm opacity-70">
  Asterisk Guide · Asterisk 22 LTS · PJSIP-first
</div>

<style>
h1 { color: #1C5D99; }
/* QA: keep code inside the 16:9 frame — shrink slightly + wrap long lines (lossless) */
.slidev-layout pre { font-size: 0.8em; line-height: 1.32; }
.slidev-layout pre code { white-space: pre-wrap; overflow-wrap: anywhere; }
</style>

---
layout: default
---

# Objectives

By the end of this chapter you will be able to:

<v-clicks>

- **Explain** what WebRTC adds to Asterisk and when to use it
- **Describe** how WebRTC media security (DTLS-SRTP) and ICE differ from plain SIP
- **Enable** the HTTP server and the secure WebSocket (`wss`) endpoint
- **Configure** a `wss` PJSIP transport and a WebRTC endpoint with `webrtc=yes`
- **Connect** a browser softphone (SIP.js) and place a call
- **Decide** between Asterisk-native WebRTC and a media gateway such as Janus

</v-clicks>

<!--
A browser becomes a first-class PJSIP endpoint. Small recipe, but strict: encrypted media and a secure transport are mandatory.
-->

---
layout: section
---

# Why WebRTC with Asterisk

---

# Why WebRTC with Asterisk

A WebRTC endpoint is, to Asterisk, **just another PJSIP endpoint**. What changes is *how* the browser reaches it and how media is secured.

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

**Typical uses**

- **Click-to-call** on a website — a visitor reaches a queue or extension
- **Web-based agents** — contact-center agent fully in the browser
- **Embedded calling** in your own web app
- **Zero-install internal phones** — a browser tab, not a hardware phone

</div>
<div>

**The trade-off**

- **Reach:** every modern browser already speaks WebRTC — no plugin, no install
- **Strictness:** WebRTC *requires* encrypted media and a secure transport

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
There is more to configure than a plain UDP SIP phone — but a single endpoint option turns most of it on.
</div>

---

# How WebRTC differs from plain SIP

A regular SIP phone signals over UDP/TCP and carries audio as plain RTP. A WebRTC client differs in **three ways** — Asterisk matches each:

<div grid="~ cols-3 gap-4 text-sm mt-2">
<div>

### Signaling
Rides a **secure WebSocket** (`wss://`) to Asterisk's HTTP server — not UDP/5060. SIP messages travel inside the WebSocket.

</div>
<div>

### Media
Always encrypted with **DTLS-SRTP**. Browsers refuse plain RTP; keys are derived from a DTLS handshake authenticated by SDP cert fingerprints.

</div>
<div>

### Connectivity
Negotiated with **ICE**. Both sides gather candidates (host, STUN-reflexive, TURN-relayed) and probe. RTP + RTCP are multiplexed on one port (`rtcp_mux`).

</div>
</div>

<div class="mt-6 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
In Asterisk 22, a single endpoint option — <strong><code>webrtc=yes</code></strong> — turns all of this on with sensible defaults. We will see exactly what it sets.
</div>

---
layout: section
---

# Building the WebRTC stack

---

# Step 1 — The HTTP server and WebSocket

Signaling is served by Asterisk's built-in HTTP server; `res_http_websocket` exposes the **`/ws`** path. Browsers require a *secure* WebSocket, so enable TLS in `http.conf`:

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088

; TLS / WSS for WebRTC — browsers require a secure WebSocket (wss://)
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.crt
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

<div class="mt-2 text-sm opacity-70">
Reload (<code>module reload res_http_websocket</code>) — the browser connects to <code>wss://your-asterisk:8089/ws</code>.
</div>

---

# Step 1 — Confirm the server

```text
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
This TLS certificate secures the <strong>WebSocket</strong> (signaling). A self-signed cert is fine in the lab — accept it once in the browser. In production use a real cert (e.g. Let's Encrypt) whose name matches the host.
<br/><br/>
It is <strong>not</strong> the DTLS certificate that encrypts media — Asterisk generates that one automatically.
</div>

---

# Step 2 — The WSS transport

PJSIP needs a transport of type `wss`. Add it to `pjsip.conf`:

```ini
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Verify it loaded:

```text
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

<div class="mt-3 text-sm opacity-70">
The <code>wss</code> transport prints a <code>0.0.0.0:5060</code> bind even though the WebSocket is served by the HTTP server on <strong>8089</strong>. Expected — the <code>wss</code> transport is a thin shim over <code>res_http_websocket</code>; its <code>bind</code> line is effectively cosmetic.
</div>

---

# Step 3 — The WebRTC endpoint

The key is `webrtc=yes`:

```ini
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

<div class="mt-2 text-sm opacity-70">
<code>webrtc=yes</code> is a convenience switch — equivalent to setting every WebRTC-required option by hand.
</div>

---

# What `webrtc=yes` actually turns on

```text
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

<div grid="~ cols-2 gap-6 text-sm mt-2">
<div>

- `media_encryption: dtls` + `dtls_auto_generate_cert: Yes` — DTLS-SRTP, cert auto-generated (you create **none**); fingerprint advertised in SDP
- `ice_support: true` — Asterisk gathers/negotiates ICE candidates

</div>
<div>

- `rtcp_mux: true` — RTP and RTCP share one port, as browsers expect
- `use_avpf: true` — the AVPF (feedback) RTP profile, required by WebRTC

</div>
</div>

---

# A note on codecs

`allow=opus` is recommended — Opus is the codec browsers prefer.

<div grid="~ cols-2 gap-8 text-sm mt-2">
<div>

**Opus in Asterisk 22**

- Ships **Opus passthrough** in core (`res_format_attr_opus`)
- Enough to *relay* Opus between two Opus-capable legs without re-encoding

</div>
<div>

**Transcoding Opus**

- Requires the separate `codec_opus` module — installed on top of the base build
- Official WebRTC guide: optional but highly recommended

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Keep <code>ulaw</code> as a fallback for bridging to non-WebRTC legs that cannot speak Opus.
</div>

---

# Step 4 — ICE, STUN and TURN

On a flat LAN, ICE with **host candidates** is enough. Across the internet, add **STUN** (discover public addresses) and **TURN** (relay when direct media is impossible). Point Asterisk at them in `rtp.conf`:

```ini
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

<div class="mt-3 text-sm opacity-70">
The browser is configured with its own ICE servers in JavaScript (the <code>RTCPeerConnection</code> <code>iceServers</code> list). For a purely internal deployment you can skip STUN/TURN entirely; most real NAT-crossing deployments need a TURN server (e.g. self-hosted coturn).
</div>

---

# Step 5 — The browser client

Any WebRTC SIP library works — **SIP.js** and **JsSIP** are widely used. The essentials are the transport URL and credentials:

```text
const ua = new SIP.UserAgent({
  uri: SIP.UserAgent.makeURI('sip:webrtc-1000@your-asterisk'),
  transportOptions: { server: 'wss://your-asterisk:8089/ws' },
  authorizationUsername: 'webrtc-1000',
  authorizationPassword: 'Lab-webrtc-secret',
});
await ua.start();
await new SIP.Registerer(ua).register();
const inviter = new SIP.Inviter(ua, SIP.UserAgent.makeURI('sip:600@your-asterisk'));
await inviter.invite();   // call the echo test
```

<div class="mt-2 text-sm" style="border-left: 4px solid #1C5D99; padding-left: 0.75rem;">
<strong>Secure context:</strong> <code>getUserMedia</code> (mic) only works on <code>https://</code> or <code>http://localhost</code>.
<strong>Accept the cert once:</strong> with a self-signed lab cert, visit <code>https://your-asterisk:8089/ws</code> first, or the WebSocket fails silently.
</div>

---

# Verifying a WebRTC call

With the browser registered, the dynamic contact appears and a call lights up the channel:

```text
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail

*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

<div class="mt-4 text-sm opacity-70">
If audio is one-way or absent, it is almost always <strong>ICE</strong> or the <strong>certificate</strong>.
</div>

---

# Asterisk-native WebRTC vs. a media gateway

<div grid="~ cols-2 gap-8">
<div>

### Use Asterisk-native WebRTC

When the browser is a **phone on your PBX** — an agent, an internal extension, a click-to-call that lands in your dialplan.

The browser is just another endpoint: queues, voicemail and IVR all work.

</div>
<div>

### Use a gateway (e.g. Janus)

When you must **scale many browser sessions** independently of call control, do selective forwarding for large conferences/streaming, or keep the media plane separate from the PBX.

The gateway bridges WebRTC to plain SIP; Asterisk then sees an ordinary SIP leg.

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Many real systems combine both — Asterisk for call control, a gateway for browser-side media scaling. (This is the architecture behind SipPulse's own stack.)
</div>

---

# Troubleshooting

<div class="text-sm">

| Symptom | Cause | Fix |
|---------|-------|-----|
| **WebSocket won't connect** | Browser rejected the TLS cert | Open `https://host:8089/ws` and accept it, or install a trusted cert |
| **Registers but no audio** | ICE failed | Add STUN, and TURN across NAT; `pjsip set logger on` and read the SDP candidates |
| **One-way audio** | NAT/ICE on one side, or no common codec | Ensure `allow=opus,ulaw` |
| **Call drops at answer** | DTLS handshake failed | Confirm `dtls_auto_generate_cert: Yes` and the system clock is correct (certs are time-sensitive) |

</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**A WebRTC phone in the browser**

Generate the self-signed cert, serve `lab/webrtc/index.html`, register as `webrtc-1000`, and call `600` (echo) — then have `6001` ring the browser.

See **Lab 6** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Inspect the negotiation with <code>pjsip set logger on</code> — find the DTLS fingerprint and ICE candidates in the SDP.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- WebRTC turns a **browser into a first-class Asterisk endpoint** — no plugin, no install.
- The recipe is small but strict: enable the **HTTP server with TLS** so the browser opens a secure WebSocket (`wss://...:8089/ws`).
- Add a **`wss` PJSIP transport**, then set **`webrtc=yes`** on the endpoint.
- That one switch turns on **DTLS-SRTP** (auto-generated cert), **ICE**, **`rtcp_mux`**, and the **AVPF** profile.
- Add **STUN/TURN** when crossing NAT; serve the page over **HTTPS**; point **SIP.js / JsSIP** at the WebSocket.
- For browser phones on your PBX, **Asterisk-native** is simplest; for large-scale media, **pair it with a gateway**.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>SIP Trunking</strong> — connecting your PBX to the outside world.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 6 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which transport carries SIP signaling for a WebRTC browser client, and what does <code>webrtc=yes</code> turn on by default?</em>
</div>
