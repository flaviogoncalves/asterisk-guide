# The Asterisk REST Interface (ARI)

The previous chapter covered AMI and AGI, the two classic ways of bolting external logic onto Asterisk. Both predate the modern web: AMI gives you a raw, line-oriented event stream over a TCP socket, and AGI hands a single channel to a script for the duration of a call. Neither was designed for the kind of stateful, asynchronous, multi-channel applications people build today — IVRs that talk to web services, click-to-call dashboards, conference controllers, or voicebots that stream audio to a speech engine.

ARI — the Asterisk REST Interface — was introduced in Asterisk 12 to fill that gap, and in Asterisk 22 it is the recommended interface for building new telephony applications. The idea behind ARI is a clean separation of concerns: **Asterisk becomes a media engine** (it answers channels, mixes bridges, plays and records audio, sends DTMF), and **your application provides all the call-control logic** through a combination of a REST (HTTP) API and a WebSocket event stream.

## Objectives

By the end of this chapter, the reader should be able to:

- Explain what ARI is and how it differs from AMI and AGI
- Decide when ARI is the right interface for a project
- Configure `ari.conf` and `http.conf` to enable ARI and create a user
- Connect to the ARI WebSocket event stream
- Describe the Stasis dialplan application and the `StasisStart`/`StasisEnd` events
- Describe the ARI resource model: channels, bridges, playbacks, recordings, endpoints, and device states
- Write a minimal Stasis application in Python that answers a channel, plays a sound, and hangs up
- Explain what the `externalMedia` channel is and why it matters for AI and voicebot integrations

## What ARI is, and when to use it

ARI is built on two transports working together:

- **A REST (HTTP) API** that your application calls to *do* things — originate a channel, answer it, play a sound, create a bridge, start a recording, hang up. These are ordinary HTTP requests (`GET`, `POST`, `DELETE`) against `http://asterisk-host:8088/ari/...`.
- **A WebSocket event stream** over which Asterisk *tells* your application what is happening — a channel was created, a DTMF digit arrived, a playback finished, a channel left your application. Events are delivered as JSON objects.

The pattern is asynchronous: you make a request, and the *result* of that request usually comes back later as an event. For example, you `POST` a request to play a sound; Asterisk answers immediately with a `Playback` object, and some seconds later you receive a `PlaybackFinished` event when the audio is done.

Choose ARI over AMI and AGI when:

- You need **fine-grained control of channels and bridges** — building conferences, parking, queues, or custom call flows from primitives instead of relying on dialplan applications.
- Your application is **stateful and long-lived**, holding several channels at once and reacting to events across all of them.
- You want to integrate with **web services, message buses, or AI/speech engines** and prefer JSON over HTTP to a line protocol or a stdin/stdout script.
- You are starting a **new project** and want the interface the Asterisk project actively recommends.

AMI is still the right tool when you only need to *observe* the system or fire occasional commands (dialers, wallboards, monitoring). AGI is still convenient for a quick, self-contained IVR script. But for anything that orchestrates calls, ARI is the modern answer.

> ARI does not replace the dialplan — it complements it. A channel runs in the dialplan as usual until it reaches the `Stasis()` application, at which point control is handed to your ARI application. When your application is done, the channel can be sent back into the dialplan or hung up.

## Enabling ARI: http.conf and ari.conf

ARI rides on top of Asterisk's built-in HTTP server, so two configuration files are involved: `http.conf` enables the web server, and `ari.conf` enables ARI and defines its users.

### http.conf

The HTTP server must be enabled and bound to an address and port. The conventional ARI port is **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

For production you should put ARI behind TLS. Asterisk can serve HTTPS directly (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), or you can terminate TLS in a reverse proxy in front of port 8088. Over TLS the URLs become `https://` and `wss://` instead of `http://` and `ws://`.

You can confirm the HTTP server is up from the CLI:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` has a `[general]` section and one section per user.

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

A few notes on these options:

- `enabled` turns ARI on or off globally.
- `pretty` formats JSON responses to be human-readable; turn it off in production.
- Each user is a named section with `type=user`.
- `read_only=yes` restricts that user to read-only (GET) requests.
- `password_format` may be `plain` (the password is in plaintext) or `crypt` (a hashed password, generated with `mkpasswd -m sha-512`).
- `permit`, `deny`, and `acl` allow per-user IP restrictions, following the same rules as `acl.conf`.

After editing the files, reload the relevant modules (`module reload res_ari.so` and `module reload http.so`) or restart Asterisk. You can verify ARI is running with:

```
asterisk*CLI> module show like res_ari
res_ari.so          Asterisk RESTful Interface          Running
res_ari_channels.so RESTful API module - Channel res... Running
res_ari_bridges.so  RESTful API module - Bridge reso... Running
...

asterisk*CLI> ari show apps
Application Name
=========================
```

`ari show apps` lists the Stasis applications currently registered by connected clients. It is empty until a client connects, which is exactly what we do next.

### The WebSocket events URL

A client subscribes to the event stream by opening a WebSocket to the `/ari/events` endpoint, naming the Stasis application it implements and passing its credentials:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

The query parameters are:

- `app` — the name of your Stasis application. This is the same name you will use in the dialplan's `Stasis()` call. You may pass several comma-separated names.
- `api_key` — the credentials, in the form `username:password`, matching a user in `ari.conf`.
- `subscribeAll` — optional boolean (default `false`); when `true`, the application receives all events, not just those for resources it owns.

The same `user:pass` credentials are used as HTTP Basic auth on the REST calls (or appended as an `api_key` query parameter there too).

## Stasis: handing a channel to your application

The bridge between the dialplan and ARI is the **`Stasis()`** dialplan application (the underlying framework is also called Stasis). When a channel reaches `Stasis(appname[,args])`, Asterisk hands that channel to the ARI application registered under `appname` and stops executing the dialplan for it. Control now belongs to your code.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

When the channel enters the application, every connected client subscribed to `hello` receives a **`StasisStart`** event over the WebSocket, carrying the full channel object (its ID, name, caller ID, state, and any arguments passed to `Stasis()`). This is your cue to start controlling the channel.

When the channel leaves the application — because your code moved it back to the dialplan with `continueInDialplan`, or because it was hung up — you receive a **`StasisEnd`** event. After `Stasis()` returns to the dialplan it sets the `STASISSTATUS` channel variable (`SUCCESS` or `FAILED`), so the dialplan can branch on the outcome.

## The ARI resource model

ARI exposes Asterisk's internals as a small set of REST resources. Each resource lives under `/ari/<resource>` and is manipulated with standard HTTP methods. The most important ones:

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | A single call leg | originate, answer, play, record, hangup |
| **bridges** | A mixing point that joins channels | create, add/remove channels, play to the bridge |
| **playbacks** | An in-progress media playback | get status, stop, pause/unpause |
| **recordings** | Live and stored recordings | start, stop, list stored, delete |
| **endpoints** | Configured peers (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Custom device states | list, get, set, delete |

Some concrete REST calls (paths shown with the `/ari` prefix that appears on the wire):

```
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

The `media` parameter on a `play` request takes a media URI. The most common form is a `sound:` URI naming a built-in sound, e.g. `sound:hello-world` or `sound:tt-monkeys`. When the audio finishes, Asterisk emits a `PlaybackFinished` event for that playback ID, which is how your application knows it can move on.

Channels and bridges are the two building blocks you combine to make call flows. To connect two callers, for instance, you originate or accept two channels, create a `mixing` bridge with `POST /ari/bridges`, and add both channels to it with `POST /ari/bridges/{bridgeId}/addChannel`. To build a conference, you simply keep adding channels to the same bridge.

## A worked example: a minimal Stasis application

Let's build the smallest useful ARI application. When any extension is dialed, the call enters our Stasis app, which answers it, plays the classic `hello-world` prompt, and hangs up.

### The dialplan

In `extensions.conf`, send the channel to Stasis:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

The application name `hello` matches the `app=hello` we use when connecting.

### The Python client

This client uses two well-known libraries: `requests` for the REST calls and `websocket-client` for the event stream. Install them with `pip install requests websocket-client`.

```python
#!/usr/bin/env python3
"""Minimal ARI Stasis app: answer, play hello-world, hang up."""
import json
import requests
from websocket import create_connection

ARI_HOST = "127.0.0.1"
ARI_PORT = 8088
ARI_USER = "asterisk"
ARI_PASS = "secret"
APP = "hello"

BASE = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

def answer(channel_id):
    requests.post(f"{BASE}/channels/{channel_id}/answer", auth=AUTH)

def play(channel_id, media):
    # Returns the Playback object; we could track its id to await PlaybackFinished.
    r = requests.post(
        f"{BASE}/channels/{channel_id}/play",
        params={"media": media},
        auth=AUTH,
    )
    return r.json()

def hangup(channel_id):
    requests.delete(f"{BASE}/channels/{channel_id}", auth=AUTH)

def main():
    ws_url = (
        f"ws://{ARI_HOST}:{ARI_PORT}/ari/events"
        f"?app={APP}&api_key={ARI_USER}:{ARI_PASS}"
    )
    ws = create_connection(ws_url)
    print(f"Connected to ARI, waiting for calls into Stasis app '{APP}'...")

    # Track which channel each playback belongs to, so we hang up when it ends.
    playback_owner = {}

    while True:
        event = json.loads(ws.recv())
        kind = event["type"]

        if kind == "StasisStart":
            channel_id = event["channel"]["id"]
            print(f"StasisStart on channel {channel_id}")
            answer(channel_id)
            pb = play(channel_id, "sound:hello-world")
            playback_owner[pb["id"]] = channel_id

        elif kind == "PlaybackFinished":
            pb_id = event["playback"]["id"]
            channel_id = playback_owner.pop(pb_id, None)
            if channel_id:
                print(f"Playback done, hanging up {channel_id}")
                hangup(channel_id)

        elif kind == "StasisEnd":
            print(f"StasisEnd on channel {event['channel']['id']}")

if __name__ == "__main__":
    main()
```

Run the script, then dial any number from a registered endpoint. You should hear "Hello, world", after which the call is released. On the Asterisk console, `ari show apps` will now list `hello` while the client is connected.

The flow is worth tracing once:

1. The dialplan runs `Stasis(hello)`; Asterisk hands the channel to our app and sends a `StasisStart` event.
2. We answer the channel, then ask Asterisk to play `sound:hello-world`. Asterisk returns a `Playback` object whose `id` we remember.
3. When the audio finishes, Asterisk sends `PlaybackFinished` with that playback `id`; we look up the channel and hang it up.
4. Hanging up causes the channel to leave Stasis, producing a `StasisEnd` event.

> **A note on client libraries.** A higher-level wrapper called `ari-py` (the `ari` package) exists, but it is unmaintained and was written for an older era of Python and Swagger tooling. For new work on Asterisk 22, prefer the explicit `requests` + WebSocket approach shown above, or an asyncio library such as `asyncari` if you need concurrency. The raw approach keeps you close to the actual REST calls and events, which is exactly what you want while learning ARI.

## externalMedia: the door to AI and voicebots

The resources above let you play and record *files*. But modern voice applications — speech-to-text transcription, AI voicebots, real-time analytics — need the *live audio stream* of a call delivered to an external process, and they need to inject audio back.

ARI provides this through the **`externalMedia` channel**. A `POST /ari/channels/externalMedia` request creates a special channel that, instead of talking to a phone, streams the call's RTP media to (and from) an external host. You bridge this channel with the caller's channel, and now your external program is in the audio path: it receives the caller's audio as RTP and can send synthesized audio back.

The request requires only:

- `app` — the Stasis application that owns the new channel.
- `format` — the audio format, e.g. `ulaw` or `slin16`.

`external_host` (the `host:port` of your media application) is optional in the schema — it may be empty for a WebSocket-server-style connection — but for a classic RTP voicebot you will supply it. The `encapsulation` parameter defaults to `rtp` and `transport` to `udp`, which is exactly what you want for a streaming media endpoint.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

This single feature is what turns Asterisk into a front-end for AI: the telephone network terminates on Asterisk, ARI orchestrates the call, and `externalMedia` pipes the audio to a speech/AI engine and back. This is the mechanism on which AI services and voicebots are built.

## Summary

ARI is the modern, recommended interface for building telephony applications on Asterisk 22. It splits the work cleanly: Asterisk is the media engine, and your application — speaking JSON over HTTP and a WebSocket — provides the call-control logic. You enable it through `http.conf` (the built-in web server on port 8088) and `ari.conf` (which turns ARI on and defines users). The `Stasis()` dialplan application hands a channel to your app, raising `StasisStart` when it enters and `StasisEnd` when it leaves. From there you manipulate a small set of REST resources — channels, bridges, playbacks, recordings, endpoints, and device states — to answer, play, record, bridge, and hang up. We built a minimal Python Stasis app that answers a call, plays a prompt, and hangs up, and we saw how the `externalMedia` channel streams live RTP to an external program — the foundation for AI and voicebot integrations.

## Quiz

1. ARI was introduced in which version of Asterisk?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. In the ARI model, Asterisk acts as a media engine while your external application provides the call-control logic.
   - A. True
   - B. False
3. ARI uses two transports together. Which pair is correct?
   - A. A REST/HTTP API for issuing commands and a WebSocket stream for receiving events
   - B. A TCP line protocol and a stdin/stdout script
   - C. SNMP and SMTP
   - D. Two separate UDP sockets
4. Which two configuration files must be set up to enable ARI?
   - A. `manager.conf` and `agi.conf`
   - B. `http.conf` and `ari.conf`
   - C. `sip.conf` and `rtp.conf`
   - D. `modules.conf` and `cdr.conf`
5. The conventional TCP port for the Asterisk HTTP server (and therefore ARI) is ____.
6. Which dialplan application hands a channel over to an ARI application?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. When a channel enters a Stasis application, which event is sent to the connected client?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Which ARI request creates a mixing point that can join two or more channels together?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. To play a built-in prompt on a channel, which event tells your application that the audio has finished so it can move on?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. The `externalMedia` channel is primarily used to:
    - A. Record a call to a local WAV file
    - B. Stream the call's live audio (RTP) to and from an external application, e.g. an AI/speech engine
    - C. Register a PJSIP endpoint
    - D. Reload the dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
