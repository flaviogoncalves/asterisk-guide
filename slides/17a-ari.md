---
theme: seriph
title: 'The Asterisk REST Interface (ARI)'
info: |
  ## Asterisk Guide — Chapter 15
  The Asterisk REST Interface (ARI). Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# The Asterisk REST Interface (ARI)

Chapter 15

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

- **Explain** what ARI is and how it differs from AMI and AGI
- **Decide** when ARI is the right interface for a project
- **Configure** `ari.conf` and `http.conf` to enable ARI and create a user
- **Connect** to the ARI WebSocket event stream
- **Describe** the `Stasis()` application and the `StasisStart`/`StasisEnd` events
- **Describe** the ARI resource model: channels, bridges, playbacks, recordings, endpoints, device states
- **Write** a minimal Stasis app that answers, plays a sound, and hangs up
- **Explain** the `externalMedia` channel for AI and voicebot integrations

</v-clicks>

<!--
This is the modern, recommended interface for building new telephony apps on Asterisk 22.
-->

---
layout: section
---

# What ARI is, and when to use it

---

# Beyond AMI and AGI

The classic interfaces predate the modern web:

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

**AMI** — a raw, line-oriented event stream over a TCP socket.

**AGI** — hands a single channel to a script for the duration of a call.

</div>
<div>

Neither was built for **stateful, asynchronous, multi-channel** applications:

- IVRs that talk to web services
- Click-to-call dashboards
- Conference controllers
- Voicebots streaming audio to a speech engine

</div>
</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
ARI was introduced in <strong>Asterisk 12</strong> and is the <strong>recommended</strong> interface for new telephony apps in Asterisk 22.
</div>

---

# The ARI model: a clean split

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

### Asterisk = media engine

Answers channels, mixes bridges, plays and records audio, sends DTMF.

</div>
<div>

### Your app = call-control logic

Speaks **JSON over HTTP** and a **WebSocket** event stream.

</div>
</div>

ARI is built on two transports working **together**:

<v-clicks>

- **A REST (HTTP) API** you call to *do* things — originate, answer, play, bridge, record, hang up. Plain `GET` / `POST` / `DELETE` against `http://asterisk-host:8088/ari/...`
- **A WebSocket event stream** over which Asterisk *tells* you what happened — channel created, DTMF arrived, playback finished. Events are JSON objects.

</v-clicks>

<div class="mt-2 text-sm opacity-70">
The pattern is <strong>asynchronous</strong>: you <code>POST</code> a play request, get a <code>Playback</code> object immediately, and a <code>PlaybackFinished</code> event arrives later.
</div>

---

# When to choose ARI

<div grid="~ cols-2 gap-8 text-sm mt-2">
<div>

**Reach for ARI when**

- You need **fine-grained control** of channels and bridges — conferences, parking, custom flows from primitives
- Your app is **stateful and long-lived**, holding several channels and reacting across all of them
- You integrate with **web services, message buses, or AI/speech engines** and prefer JSON
- You are starting a **new project** — the interface Asterisk actively recommends

</div>
<div>

**Still fine elsewhere**

- **AMI** — when you only *observe* the system or fire occasional commands (dialers, wallboards, monitoring)
- **AGI** — a quick, self-contained IVR script

</div>
</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
ARI does <strong>not</strong> replace the dialplan — it complements it. A channel runs in the dialplan until it reaches <code>Stasis()</code>, then control is handed to your app.
</div>

---
layout: section
---

# Enabling ARI

---

# http.conf — the built-in web server

ARI rides on Asterisk's built-in HTTP server. The conventional ARI port is **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

<div class="mt-2 text-sm">

For production, put ARI behind **TLS** — serve HTTPS directly (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`) or terminate TLS in a reverse proxy. URLs then become `https://` and `wss://`.

</div>

Confirm the server is up from the CLI:

```text
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

---

# ari.conf — enable ARI and define users

A `[general]` section plus one section per user.

```ini
[general]
enabled=yes
pretty=yes              ; pretty-print JSON responses (handy while learning)

[asterisk]
type=user
read_only=no            ; set to yes for a user that may only issue GET requests
password=secret
password_format=plain   ; "plain" (default) or "crypt"
```

<div grid="~ cols-2 gap-6 text-sm mt-2">
<div>

- `enabled` — ARI on/off globally
- `pretty` — human-readable JSON; **off in production**
- Each user is a named section with `type=user`

</div>
<div>

- `read_only=yes` — restrict that user to GET requests
- `password_format` — `plain` or `crypt` (`mkpasswd -m sha-512`)
- `permit` / `deny` / `acl` — per-user IP rules (like `acl.conf`)

</div>
</div>

---

# Verifying ARI is running

After editing, reload (or restart):

```bash
asterisk -rx 'module reload res_ari.so'
asterisk -rx 'module reload http.so'
```

```text
asterisk*CLI> module show like res_ari
res_ari.so          Asterisk RESTful Interface          Running
res_ari_channels.so RESTful API module - Channel res... Running
res_ari_bridges.so  RESTful API module - Bridge reso... Running
...

asterisk*CLI> ari show apps
Application Name
=========================
```

<div class="mt-2 text-sm opacity-70">
<code>ari show apps</code> lists Stasis applications registered by connected clients — empty until a client connects.
</div>

---

# The WebSocket events URL

A client subscribes by opening a WebSocket to `/ari/events`, naming its Stasis app and passing credentials:

```text
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

<div class="text-sm mt-2">

| Parameter | Meaning |
|-----------|---------|
| `app` | Name of your Stasis app — same name used in the dialplan's `Stasis()`. Several names may be comma-separated. |
| `api_key` | Credentials as `username:password`, matching a user in `ari.conf`. |
| `subscribeAll` | Optional (default `false`); when `true`, receive **all** events, not just owned resources. |

</div>

<div class="mt-3 text-sm opacity-70">
The same <code>user:pass</code> is used as HTTP Basic auth on REST calls (or appended as an <code>api_key</code> query parameter).
</div>

---
layout: section
---

# Stasis: handing off a channel

---

# Stasis() — the bridge to your app

When a channel reaches `Stasis(appname[,args])`, Asterisk hands it to the ARI app registered under `appname` and **stops executing the dialplan** for it. Control now belongs to your code.

```ini
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

<v-clicks>

- **`StasisStart`** — fired when the channel *enters* the app, carrying the full channel object (ID, name, caller ID, state, args). Your cue to start controlling it.
- **`StasisEnd`** — fired when the channel *leaves* (moved back to the dialplan with `continueInDialplan`, or hung up).
- After `Stasis()` returns, the **`STASISSTATUS`** channel variable is set (`SUCCESS` or `FAILED`) so the dialplan can branch on the outcome.

</v-clicks>

---
layout: section
---

# The ARI resource model

---

# Resources

Asterisk's internals are exposed as a small set of REST resources under `/ari/<resource>`, manipulated with standard HTTP methods.

<div class="text-sm">

| Resource | Represents | Example operations |
|----------|------------|--------------------|
| **channels** | A single call leg | originate, answer, play, record, hangup |
| **bridges** | A mixing point joining channels | create, add/remove channels, play to bridge |
| **playbacks** | An in-progress media playback | get status, stop, pause/unpause |
| **recordings** | Live and stored recordings | start, stop, list stored, delete |
| **endpoints** | Configured peers (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Custom device states | list, get, set, delete |

</div>

<div class="mt-3 text-sm opacity-70">
<strong>channels</strong> and <strong>bridges</strong> are the two building blocks you combine to make call flows.
</div>

---

# Concrete REST calls

```bash
# Channels
POST   /ari/channels                          # originate a new channel
POST   /ari/channels/{channelId}/answer       # answer an incoming channel
POST   /ari/channels/{channelId}/play         # play media (body: media=sound:hello-world)
POST   /ari/channels/{channelId}/record       # record the channel
DELETE /ari/channels/{channelId}              # hang up the channel

# Bridges
POST   /ari/bridges                           # create a bridge (e.g. type=mixing)
POST   /ari/bridges/{bridgeId}/addChannel     # add a channel (param: channel=<id>)
POST   /ari/bridges/{bridgeId}/play           # play media to everyone in the bridge
DELETE /ari/bridges/{bridgeId}                # destroy the bridge

# Read-only resources
GET    /ari/endpoints
GET    /ari/deviceStates
GET    /ari/recordings/stored
GET    /ari/playbacks/{playbackId}
```

<div class="mt-2 text-sm opacity-70">
<code>media</code> takes a URI — usually <code>sound:</code>, e.g. <code>sound:hello-world</code>. When audio ends, Asterisk emits <code>PlaybackFinished</code> for that playback ID.
</div>

---

# Building call flows from primitives

To **connect two callers**:

<v-clicks>

1. Originate or accept **two channels**
2. Create a `mixing` bridge: `POST /ari/bridges`
3. Add both channels: `POST /ari/bridges/{bridgeId}/addChannel`

</v-clicks>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
To build a <strong>conference</strong>, keep adding channels to the same bridge.
</div>

---
layout: section
---

# A worked example

---

# A minimal Stasis application

The smallest useful ARI app: answer the call, play `hello-world`, hang up.

**The dialplan** — send the channel to Stasis:

```ini
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

The app name `hello` matches the `app=hello` we use when connecting.

**The client** uses two well-known libraries:

```bash
pip install requests websocket-client
```

`requests` for the REST calls, `websocket-client` for the event stream.

---

# The Python client

```python
import json, requests
from websocket import create_connection

ARI_HOST, ARI_PORT = "127.0.0.1", 8088
ARI_USER, ARI_PASS, APP = "asterisk", "secret", "hello"
BASE = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

def answer(cid): requests.post(f"{BASE}/channels/{cid}/answer", auth=AUTH)
def play(cid, media):
    return requests.post(f"{BASE}/channels/{cid}/play",
                         params={"media": media}, auth=AUTH).json()
def hangup(cid): requests.delete(f"{BASE}/channels/{cid}", auth=AUTH)

ws = create_connection(
    f"ws://{ARI_HOST}:{ARI_PORT}/ari/events?app={APP}&api_key={ARI_USER}:{ARI_PASS}")
playback_owner = {}
while True:
    event = json.loads(ws.recv())
    if event["type"] == "StasisStart":
        cid = event["channel"]["id"]; answer(cid)
        playback_owner[play(cid, "sound:hello-world")["id"]] = cid
    elif event["type"] == "PlaybackFinished":
        cid = playback_owner.pop(event["playback"]["id"], None)
        if cid: hangup(cid)
```

---

# Tracing the flow

Run the script, dial any number from a registered endpoint, hear "Hello, world", call released.

<v-clicks>

1. The dialplan runs `Stasis(hello)`; Asterisk hands over the channel and sends **`StasisStart`**.
2. We **answer**, then play `sound:hello-world`; Asterisk returns a `Playback` object whose `id` we remember.
3. When audio finishes, Asterisk sends **`PlaybackFinished`** with that `id`; we look up the channel and **hang up**.
4. Hanging up makes the channel leave Stasis, producing a **`StasisEnd`** event.

</v-clicks>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Client libraries:</strong> the old <code>ari-py</code> wrapper is unmaintained. For Asterisk 22, prefer explicit <code>requests</code> + WebSocket, or <code>asyncari</code> for concurrency.
</div>

---
layout: section
---

# externalMedia — the door to AI

---

# Streaming live audio to an external app

Playing and recording deal with *files*. Voicebots, transcription, and real-time analytics need the **live audio stream** delivered to an external process — and audio injected back.

ARI provides this through the **`externalMedia` channel**:

```bash
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

<div class="text-sm mt-2">

- `app` — the Stasis app that owns the new channel
- `format` — the audio format, e.g. `ulaw` or `slin16`
- `external_host` — `host:port` of your media app (optional in the schema; supply it for classic RTP)
- `encapsulation` defaults to `rtp`, `transport` to `udp`

</div>

<div class="mt-3 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
You bridge this channel with the caller's channel — now your program is in the audio path. This is the mechanism on which <strong>AI services and voicebots</strong> are built.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Control Asterisk with ARI**

Enable ARI, query the system over plain HTTP + JSON, list your endpoints, and **originate a call entirely from the REST API**.

```bash
curl -s -u labuser:Lab-ari-secret http://localhost:8088/ari/asterisk/info
```

See **Lab 8** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
~20 min · ARI on <code>localhost:8088</code> · originate makes <code>6001</code> ring and drops into the echo test.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- ARI is the **modern, recommended** interface for building telephony apps on Asterisk 22.
- It splits the work cleanly: **Asterisk is the media engine**; your app provides **call-control logic**, speaking JSON over **HTTP + a WebSocket**.
- Enable it via **`http.conf`** (built-in web server on **8088**) and **`ari.conf`** (turns ARI on, defines users).
- **`Stasis()`** hands a channel to your app — **`StasisStart`** on entry, **`StasisEnd`** on exit.
- Manipulate a small set of resources — **channels, bridges, playbacks, recordings, endpoints, device states** — to answer, play, record, bridge, and hang up.
- **`externalMedia`** streams live RTP to an external program — the foundation for **AI and voicebot** integrations.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Realtime</strong> — driving Asterisk configuration from a database.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 15 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which dialplan application hands a channel over to an ARI application, and which event fires when the channel enters it?</em>
</div>
