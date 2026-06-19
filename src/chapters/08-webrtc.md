# WebRTC with Asterisk

> **[2nd-ed note]** NEW chapter — outline only; prose to be written in Phase 4 and
> lab-verified (browser softphone → Asterisk 22 over WSS/DTLS-SRTP). Asterisk is the
> WebRTC *server* here (PJSIP `wss` transport), distinct from a Janus-style gateway.

## Objectives

By the end of this chapter, you should be able to:

- Explain why and when to use Asterisk as a WebRTC server
- Configure a PJSIP `wss` transport with TLS
- Set up a WebRTC-enabled endpoint (DTLS-SRTP, ICE, AVPF)
- Connect a browser softphone (SIP.js / JsSIP) to Asterisk
- Understand how STUN/TURN fit in for NAT traversal

## Why WebRTC with Asterisk

> **[2nd-ed note]** Browser-native calling, no plugins; clicktocall, web agents, embedding
> Asterisk behind a web app. Contrast with chan_pjsip-vs-gateway (Janus) trade-offs.

## The secure WebSocket transport (wss)

> **[2nd-ed note]** `type=transport` / `protocol=wss`, TLS cert chain, `res_http_websocket`,
> `http.conf` (tlsenable, tlsbindaddr), reuse of the Asterisk built-in HTTP server.

## DTLS-SRTP and certificates

> **[2nd-ed note]** `media_encryption=dtls`, `dtls_*` endpoint options, `dtls_auto_generate_cert`
> vs explicit certs, `media_use_received_transport`, RTCP-mux.

## ICE, STUN and TURN

> **[2nd-ed note]** `ice_support=yes`, `rtp.conf` stunaddr/turnaddr, why TURN is needed for
> symmetric NAT, candidate gathering.

## A WebRTC endpoint, end to end

> **[2nd-ed note]** Full endpoint/aor/auth example with `webrtc=yes` (the convenience option
> that sets transport-ws defaults), plus the dialplan to bridge a browser call to a PJSIP phone.

## Browser clients

> **[2nd-ed note]** SIP.js and JsSIP minimal examples; registering over WSS; getUserMedia;
> attaching media streams. Note the SipPulse web softphone as a reference client.

## Asterisk WebRTC vs a media gateway

> **[2nd-ed note]** When Asterisk-native WebRTC is enough vs. when a dedicated gateway
> (e.g. Janus) earns its place. Tie back to the reader's architecture.

## Lab

> **[2nd-ed note]** Extend the Docker lab with the wss transport + a static browser softphone
> page; verify a browser-to-PJSIP call. Capture real CLI (`pjsip show endpoint webrtc-user`).

## Summary
