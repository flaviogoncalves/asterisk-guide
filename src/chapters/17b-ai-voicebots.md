# Building AI Voicebots with Asterisk

Conversational AI has turned the old, menu-driven IVR ("press 1 for sales") into
something that listens, understands, and talks back in natural language. This
chapter shows how to build such a voicebot on top of Asterisk 22. The single most
important idea — and the one most often gotten wrong — is this: **Asterisk is the
media engine, not the AI.** Asterisk owns the call (SIP signaling, RTP, codecs,
bridging) and streams the caller's audio out to *your* application; your
application runs the AI loop — speech-to-text (STT), a language model or dialog
engine, and text-to-speech (TTS) — and streams the answer back. Every AI engine
mentioned here (Whisper, Deepgram, OpenAI, Piper, ElevenLabs, Azure, and so on) is
an **external, third-party** service. Asterisk provides the telephony plumbing that
gets the audio in and out, and nothing more.

This is a fast-moving area: the STT/LLM/TTS landscape changes month to month, and
new managed "voice agent" APIs appear constantly. The Asterisk-side mechanisms,
however, are stable and well documented, and that is what this chapter focuses on.
Everything Asterisk-specific here is verified against the book's Asterisk 22 lab
(Asterisk 22.10.0).

## Objectives

By the end of this chapter, you should be able to:

- Describe the voicebot architecture and where Asterisk fits versus the AI services
- Explain the STT → LLM/dialog → TTS pipeline and that those engines are external
- Stream call audio to an external application with the `AudioSocket()` application
  and the `chan_audiosocket` channel driver
- Describe the AudioSocket framed protocol (type / length / payload) at a high level
- Use ARI `externalMedia` to bridge call audio to an external RTP endpoint
- Reason about audio formats and resampling (8 kHz `slin`/`ulaw` vs. 16 kHz STT)
- Account for the practical concerns: latency, barge-in, endpointing/VAD, partial
  transcripts, cost, and privacy/PII
- Decide where a voicebot fits (IVR replacement, after-hours assistant, qualification)

## The architecture: Asterisk as the media engine

A voicebot call has two halves that meet at the audio stream:

```
   Caller (PSTN / SIP / WebRTC)
        |  SIP + RTP
        v
   +-------------+        audio out      +------------------------------+
   |  Asterisk   | -------------------->  |   Your voicebot application  |
   |  (media     |                        |                              |
   |   engine)   | <--------------------  |  STT --> LLM/dialog --> TTS  |
   +-------------+        audio in        +------------------------------+
```

Asterisk answers the call, handles all the SIP/RTP/codec work, and exposes the
caller's audio as a stream. Your application consumes that stream, sends it to an
STT engine to get text, feeds the text to an LLM (or a rules-based dialog engine)
to decide what to say, runs the reply through a TTS engine to get audio, and sends
that audio back to Asterisk, which plays it to the caller.

Asterisk's job is small but essential: it is the only part that speaks telephony.
The AI loop lives entirely outside Asterisk. This separation is what keeps the
design clean — you can swap STT or LLM providers without touching the dialplan, and
Asterisk does not need to know AI exists.

There are two supported ways to get the audio between Asterisk and your app:
**AudioSocket** (a simple TCP audio protocol) and **ARI external media** (an RTP
stream driven by a Stasis application). We cover both, with their trade-offs.

## Mechanism 1 — AudioSocket

AudioSocket is the simplest path. It is a small TCP protocol that streams raw PCM
audio frames between a channel and a TCP server you write. It comes in two forms:

- The **`AudioSocket()` dialplan application** (`app_audiosocket`) — you bridge one
  channel's audio to your server from the dialplan.
- The **`chan_audiosocket` channel driver** — AudioSocket as a channel technology,
  so you can `Dial(AudioSocket/...)` or originate such a channel (used, among other
  things, as a transport option for ARI `externalMedia`, below).

In the lab, all three supporting modules are present and loaded:

```
*CLI> module show like audiosocket
Module                         Description                   Use Count  Status   Support Level
app_audiosocket.so             AudioSocket Application        0          Running  extended
chan_audiosocket.so            AudioSocket Channel            0          Running  extended
res_audiosocket.so             AudioSocket support            2          Running  extended
3 modules loaded
```

AudioSocket was introduced in Asterisk 18, so any Asterisk 18+ (including 22) has
it. Its support level is `extended` rather than `core`.

### The dialplan side

The application takes a UUID and a `host:port`:

```
*CLI> core show application AudioSocket
  -= Info about Application 'AudioSocket' =-
[Synopsis]
Transmit and receive PCM audio between a channel and a TCP socket server.
[Syntax]
AudioSocket(uuid,service)
```

A minimal dialplan that answers the call and connects it to a voicebot server
listening on `voicebot:8090`:

```
[voicebot]
exten => s,1,Answer()
 same => n,AudioSocket(40325ec2-5efd-4bd3-805f-53576e581d13,voicebot:8090)
 same => n,Hangup()
```

The UUID identifies this call to your service (so a single server can multiplex many
calls and correlate them with whatever session state it keeps). It must be a valid
string-form UUID. The `service` is `host:port`; IPv6 goes in brackets, e.g.
`[::1]:8090`.

Important: `AudioSocket()` does **not** answer the channel for you. Precede it with
`Answer()` (or `Progress()` for early media), exactly as shown — the application's
own help says so.

### The AudioSocket framed protocol

AudioSocket is a length-prefixed binary protocol. Every message on the TCP
connection is a frame with a **three-byte header** followed by a variable payload:

```
+--------+------------------+-----------------------------+
| type   | length (16-bit)  | payload (length bytes)      |
| 1 byte | big-endian uint  |                             |
+--------+------------------+-----------------------------+
```

- **Byte 0 — type (kind):** what the frame carries.
- **Bytes 1–2 — length:** a 16-bit unsigned big-endian integer, the number of
  payload bytes that follow.
- **Remaining bytes — payload:** interpreted according to the type.

The frame types you will actually handle:

| Type   | Meaning                                                              |
|--------|---------------------------------------------------------------------|
| `0x00` | Terminate / hang up the connection                                  |
| `0x01` | UUID — the 16-byte binary UUID identifying the call (sent at start) |
| `0x03` | DTMF — payload is one ASCII digit                                   |
| `0x10` | Audio — signed-linear 16-bit, 8 kHz, mono PCM                       |
| `0xff` | Error                                                               |

In practice the flow is: your server accepts the TCP connection, reads the `0x01`
UUID frame, then enters a loop reading `0x10` audio frames (the caller's voice) and
writing `0x10` audio frames back (the bot's voice). DTMF arrives as `0x03` frames.
Send a `0x00` frame to end the connection. The protocol is documented at
`docs.asterisk.org` under Channel Drivers → AudioSocket.

The default audio carried by the `AudioSocket()` application is **signed linear,
16-bit, 8 kHz, mono PCM** (`slin`) — i.e. `0x10` frames. Other codecs are possible
through the channel-driver interface, but plain 8 kHz `slin` is the baseline you
should expect.

### A reference server sketch (Python)

The following sketch shows the *Asterisk-facing* half of an AudioSocket server: it
parses frames and exposes the caller audio. The AI calls (STT/LLM/TTS) are shown as
external function calls — they are third-party services, not part of Asterisk.

```python
import asyncio
import struct

# Frame types
KIND_HANGUP, KIND_UUID, KIND_DTMF, KIND_AUDIO, KIND_ERROR = 0x00, 0x01, 0x03, 0x10, 0xff

async def read_frame(reader):
    header = await reader.readexactly(3)
    kind = header[0]
    length = struct.unpack(">H", header[1:3])[0]   # 16-bit big-endian
    payload = await reader.readexactly(length) if length else b""
    return kind, payload

def make_audio_frame(pcm8k_slin: bytes) -> bytes:
    return bytes([KIND_AUDIO]) + struct.pack(">H", len(pcm8k_slin)) + pcm8k_slin

async def handle_call(reader, writer):
    call_uuid = None
    try:
        while True:
            kind, payload = await read_frame(reader)
            if kind == KIND_UUID:
                call_uuid = payload.hex()
            elif kind == KIND_AUDIO:
                # payload is 8 kHz, 16-bit, mono PCM from the caller.
                # Feed it to your VAD / STT. STT engines usually want 16 kHz,
                # so resample 8k -> 16k before sending (see "Audio format reality").
                text = await stt_engine.feed(payload)          # EXTERNAL service
                if text:                                       # got a final transcript
                    reply = await llm.respond(text)            # EXTERNAL service
                    speech = await tts.synthesize(reply)       # EXTERNAL service
                    # speech must be 8 kHz slin to go back to Asterisk:
                    for chunk in chunked(speech, 320):         # 20 ms @ 8 kHz = 320 bytes
                        writer.write(make_audio_frame(chunk))
                        await writer.drain()
            elif kind == KIND_DTMF:
                digit = payload.decode("ascii", "ignore")      # caller pressed a key
            elif kind in (KIND_HANGUP, KIND_ERROR):
                break
    finally:
        writer.close()

async def main():
    server = await asyncio.start_server(handle_call, "0.0.0.0", 8090)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

The Asterisk-specific code is just the frame parser and the audio-frame builder.
Everything labelled "EXTERNAL service" is a third-party AI engine you choose and
integrate yourself.

### AudioSocket trade-offs

- **Pros:** dead simple, one TCP connection per call, trivial to parse, no media
  negotiation. Great for prototypes and single-channel bots.
- **Cons:** raw TCP (you handle reconnection, flow control, jitter yourself); 8 kHz
  `slin` only in the common case; one connection per channel; the protocol carries
  audio and DTMF but not the rich call-control events you get from ARI. It does not,
  by itself, give you bridging, transfers, or multi-party control — for that you
  combine it with the dialplan or ARI.

## Mechanism 2 — ARI external media

If you are already building with ARI (see the chapter *The Asterisk REST Interface
(ARI)*), the `externalMedia` resource is the more powerful option. Introduced
in Asterisk 16.6, it creates a special channel whose media is sent to (and received
from) an external endpoint, and which you can put into bridges and manipulate like
any other channel.

You create it with a REST call:

```
POST /ari/channels/externalMedia?app=MyApp&external_host=127.0.0.1:60000&format=ulaw
```

Key parameters:

- `app` — the Stasis application that will own the resulting channel.
- `external_host` — `host:port` of *your* media endpoint (where Asterisk sends RTP).
- `format` — the media format, e.g. `ulaw` or `slin16`.
- `encapsulation` / `transport` — by default RTP over UDP. The combination of
  transport and encapsulation selects the underlying channel driver: `chan_rtp`
  (udp/rtp), `chan_audiosocket` (tcp/audiosocket), or `chan_websocket`
  (websocket/none). So external media can *also* ride AudioSocket — the two
  mechanisms are not mutually exclusive.

The call returns an **ExternalMedia** object that contains a normal **Channel**
object. You then bridge that channel with the caller's channel inside your Stasis
app:

```
1. Caller enters Stasis(MyApp)              -> you get a StasisStart event
2. POST /ari/channels/externalMedia ...      -> creates the external-media channel
3. POST /ari/bridges                          -> create a mixing bridge
4. POST /ari/bridges/{id}/addChannel          -> add caller + external-media channel
5. RTP now flows to/from your media server; you run STT/LLM/TTS there
```

Because the external-media channel is just a channel, everything in the ARI toolbox
applies: you can play prompts with `POST /ari/channels/{id}/play`, record, add or
remove channels from the bridge, transfer to a human agent, and so on. That control
richness is the main reason to choose ARI external media over plain AudioSocket.

The lab confirms the ARI stack is loaded (`res_ari`, `res_ari_channels`,
`res_ari_events`, the model validators, etc.). Configure ARI in `ari.conf` and
`http.conf` exactly as described in the ARI chapter; external media needs no extra
configuration beyond a working ARI/Stasis setup.

### AudioSocket vs. external media — which to use

| Concern                 | AudioSocket                          | ARI external media                       |
|-------------------------|--------------------------------------|------------------------------------------|
| Transport               | TCP                                  | RTP/UDP (or TCP/WebSocket via driver)    |
| Setup complexity        | Very low (one dialplan line)         | Higher (Stasis app + REST orchestration) |
| Call control            | Audio + DTMF only                    | Full ARI: bridges, transfers, playback   |
| Best for                | Quick bots, single-channel pipelines | Production bots needing rich control     |
| Introduced              | Asterisk 18                          | Asterisk 16.6                            |

A common pattern: start with AudioSocket to validate the AI pipeline, then move to
ARI external media when you need transfers to a human, conferencing, or to manage
many concurrent bot sessions.

## Audio format reality: 8 kHz telephony vs. 16 kHz STT

This is where many voicebots sound bad. Telephony audio from the PSTN is **8 kHz,
narrowband** — usually `ulaw`/`alaw` (G.711) on the wire, which Asterisk exposes to
you as 8 kHz signed-linear (`slin`) through AudioSocket. Most modern STT engines,
however, are trained on (and expect) **16 kHz** audio, and many TTS engines produce
16 kHz, 22.05 kHz, or 24 kHz output.

So you almost always have to **resample** at the boundaries of your application:

- **Caller → STT:** upsample the 8 kHz `slin` you receive to 16 kHz before sending
  to the STT engine. (Upsampling does not add lost high frequencies, but most STT
  engines still want their native rate; feeding 8 kHz where 16 kHz is expected
  usually hurts accuracy.)
- **TTS → caller:** downsample the TTS output (often 22.05/24 kHz) to 8 kHz `slin`
  before writing it back to Asterisk over AudioSocket. If you send the wrong rate,
  the audio plays too fast or too slow and is unintelligible.

With ARI external media you have a little more flexibility: you can request
`format=slin16` so Asterisk hands you 16 kHz directly and does the narrowband ↔
wideband conversion itself. If both legs of the call are wideband (e.g. a WebRTC
caller using Opus, or G.722), you may be able to keep 16 kHz end-to-end and skip the
caller-side upsample entirely. Always confirm what sample rate each engine actually
ingests and emits, and resample explicitly — never assume.

A short checklist:

- Know the sample rate and encoding at every hop (8 kHz `slin`, 16 kHz `slin16`,
  TTS output rate).
- Resample with a real resampler (e.g. `libsamplerate`/`soxr`, `scipy`, or your
  STT/TTS SDK's helper), not by naive byte-stuffing.
- Keep everything mono; telephony is mono.

## A concrete reference pipeline

Putting it together, a working voicebot looks like this end to end:

```
Caller (PSTN/SIP/WebRTC)
   │  SIP + RTP (8 kHz ulaw, or Opus/G.722 for wideband)
   ▼
Asterisk  ──(AudioSocket TCP  OR  ARI externalMedia RTP)──►  Voicebot app
   ▲                                                            │
   │  bot audio (8 kHz slin back)                               ▼
   │                                          ┌──────────────────────────────┐
   │                                          │  1. VAD / endpointing         │
   │                                          │  2. STT  (Whisper/Deepgram/   │
   │                                          │          Vosk)  [EXTERNAL]    │
   │                                          │  3. LLM / dialog  (OpenAI-    │
   │                                          │          compatible API)      │
   │                                          │          [EXTERNAL]           │
   │                                          │  4. TTS  (Piper/ElevenLabs/   │
   │                                          │          Azure)  [EXTERNAL]   │
   └──────────────────────────────────────────┴──────────────────────────────┘
```

1. **Caller → Asterisk → app.** Asterisk answers and streams the caller's 8 kHz
   audio to your app via AudioSocket or external media.
2. **VAD / endpointing.** Your app detects when the caller is speaking and, crucially,
   when they have *stopped* (an utterance boundary), so it knows when to run STT.
3. **STT** — speech to text. **Whisper** (self-hosted or via API), **Deepgram**
   (streaming API), and **Vosk** (offline) are common choices. All external.
4. **LLM / dialog** — decide what to say. An OpenAI-compatible chat API is typical;
   for constrained flows a rules/intent engine may be enough. External.
5. **TTS** — text to speech. **Piper** (fast, local, open source), **ElevenLabs**
   (high quality, cloud), **Azure**/Google/Amazon Polly (cloud). External.
6. **app → Asterisk → caller.** Downsample the TTS audio to 8 kHz `slin` and stream
   it back; Asterisk plays it to the caller.

The streaming variants of STT and TTS matter for latency: feeding audio to STT
continuously and starting TTS playback before the whole reply is synthesized are
what make the bot feel responsive rather than walkie-talkie-like.

## Practical concerns

Getting a voicebot to *work* is easy; getting it to feel natural is the hard part.

**Latency budget.** Aim for **sub-second** turn-taking — the gap between the caller
finishing and the bot starting to talk. That budget is split across network +
endpointing + STT + LLM + TTS, so every stage must stream. A non-streaming pipeline
(record whole utterance → transcribe → prompt LLM → synthesize whole reply → play)
easily exceeds 2–3 seconds and feels broken. Use streaming STT, stream tokens out of
the LLM, and start TTS on the first sentence.

**Barge-in.** Humans interrupt. When the caller starts talking while the bot is
speaking, you must **stop the TTS playback immediately** and start listening. With
AudioSocket this means: detect caller speech via VAD even while you are writing bot
audio, and stop writing `0x10` audio frames the moment you do. With ARI, stop the
playback (`DELETE /ari/playbacks/{id}` / `stopPlayback`). Without barge-in the bot
talks over the caller and the conversation collapses.

**Endpointing / VAD.** Voice Activity Detection decides where an utterance ends.
Too eager and you cut the caller off mid-sentence; too lazy and the bot feels slow.
Tune the silence threshold (often 300–800 ms of trailing silence) to your use case.

**Partial transcripts.** Streaming STT emits *partial* (interim) results as the
caller speaks and a *final* result when the utterance ends. Use partials to show
progress / pre-warm the LLM, but act on the *final* transcript. Acting on partials
leads to the bot responding to half-finished sentences.

**Cost.** Cloud STT, LLM, and TTS are billed per minute / per token / per character.
A chatty bot at scale gets expensive fast. Local options (Vosk for STT, Piper for
TTS, a self-hosted model for the LLM) trade quality/effort for predictable cost.
Model and price these before you ship.

**Privacy and PII.** Call audio frequently contains personal data — names, account
numbers, card numbers, health details. Sending it to third-party AI services has
legal and contractual consequences (GDPR, HIPAA, PCI-DSS, recording-consent laws).
Know where the audio goes, get consent where required, redact or avoid capturing
sensitive fields (e.g. take card numbers via DTMF, not voice), and prefer providers
with appropriate data-processing terms — or self-host the engines.

## Where this fits

Good fits for an Asterisk voicebot today:

- **IVR replacement.** Natural-language routing instead of nested DTMF menus
  ("What can I help you with?" → routes to the right queue).
- **After-hours / overflow assistant.** Answers common questions, takes messages, or
  schedules callbacks when no agent is available.
- **Lead qualification / intake bots.** Collect structured information (name, reason,
  account) before handing off to a human, with the ARI path enabling a clean transfer
  into a queue.

And a caveat worth repeating: this is a **fast-moving** field. The Asterisk side —
AudioSocket and ARI external media — is stable and is what you should build on. The
AI side (which STT/LLM/TTS to use, and the growing crop of all-in-one "voice agent"
APIs) changes constantly; design your application so those components are swappable.

## Summary

A voicebot built on Asterisk cleanly separates two responsibilities: Asterisk is the
**media engine** that owns the call and streams audio, and an **external
application** runs the AI loop of STT → LLM/dialog → TTS using third-party engines.
Asterisk gives you two ways to get the audio out and back: **AudioSocket** — a simple
TCP protocol (`AudioSocket()` application and `chan_audiosocket`, since Asterisk 18)
with three-byte-header frames (type/length/payload) carrying 8 kHz `slin` audio and
DTMF — and **ARI external media** (since Asterisk 16.6), an RTP-based channel you
drive from a Stasis app for full call control. Remember the 8 kHz-telephony vs.
16 kHz-STT mismatch and resample at the edges. Then budget for sub-second latency,
implement barge-in and good endpointing, act on final (not partial) transcripts, and
take cost and PII seriously. Asterisk supplies the telephony; the intelligence is
yours to plug in.

## Quiz

1. In an Asterisk voicebot, what is Asterisk's role?
   - A. It runs the speech-to-text and language model itself
   - B. It is the media engine — it handles the call (SIP/RTP/codecs) and streams
     audio to/from an external application
   - C. It hosts the text-to-speech voices
   - D. It replaces the need for any external AI service

2. The AI pipeline in a voicebot is, in order:
   - A. TTS → LLM → STT
   - B. STT → LLM/dialog → TTS
   - C. LLM → STT → TTS
   - D. STT → TTS → LLM

3. Which dialplan application streams a channel's PCM audio to an external TCP
   server, and which channel driver backs it?
   - A. `ExternalMedia()` / `chan_rtp`
   - B. `AudioSocket()` / `chan_audiosocket`
   - C. `MixMonitor()` / `chan_local`
   - D. `Stasis()` / `chan_websocket`

4. True or false: `AudioSocket()` answers the channel for you, so you do not need
   `Answer()` before it.

5. An AudioSocket frame header is three bytes. What do those bytes encode?
   - A. A 3-byte magic number
   - B. A 1-byte type plus a 2-byte (16-bit, big-endian) payload length
   - C. A 2-byte type plus a 1-byte length
   - D. A 3-byte timestamp

6. Which ARI request creates a channel that bridges call audio to an external RTP
   endpoint?
   - A. `POST /ari/channels` with `app=...`
   - B. `POST /ari/bridges/{id}/addChannel`
   - C. `POST /ari/channels/externalMedia` with `external_host` and `format`
   - D. `POST /ari/playbacks`

7. Telephony audio from the PSTN is typically 8 kHz, but most STT engines expect
   ________ audio, so you must ________ at the boundaries of your application.

8. Which technique stops the bot's TTS playback the moment the caller starts
   speaking again?
   - A. Endpointing
   - B. Barge-in
   - C. Transcoding
   - D. Partial transcripts

9. Which of the following are legitimate practical concerns for a production
   voicebot? (Choose all that apply.)
   - A. Keeping turn-taking latency sub-second
   - B. Handling caller PII / privacy obligations
   - C. Acting on final transcripts rather than partial (interim) ones
   - D. The cost of cloud STT/LLM/TTS at scale

10. True or false: AudioSocket and ARI external media are mutually exclusive — a
    channel created by `externalMedia` can never use the AudioSocket transport.

**Answers:** 1 — B · 2 — B · 3 — B · 4 — False (it does not answer; precede it with `Answer()` or `Progress()`) · 5 — B · 6 — C · 7 — 16 kHz / resample · 8 — B · 9 — A, B, C, D · 10 — False (`externalMedia` can select the `chan_audiosocket` transport via the transport/encapsulation combination)
