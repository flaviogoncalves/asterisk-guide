# Deployment, monitoring & scaling

Getting Asterisk to answer a call in a lab is one thing; running it as a service
that survives crashes, reboots, upgrades and attackers — and that you can observe,
back up and grow — is another. This chapter is about everything that happens *after*
the dialplan works. We start with the supervisor that keeps Asterisk alive
(systemd), move to packaging it in a container (using the book's own Docker lab as
the worked example), then cover configuration management and backups, monitoring and
observability, and finally the patterns you reach for when one server is not enough:
high availability and scaling, and the realities of hosting in the cloud.

Everything shown is verified against the book's Asterisk 22 lab in `lab/` — the same
container you have been building on throughout the book.

## Objectives

By the end of this chapter, you should be able to:

- Run Asterisk 22 reliably under systemd, as a non-root user, with automatic restart
- Containerize Asterisk with Docker and understand the networking trade-offs
- Keep `/etc/asterisk` in version control and back up the right state
- Monitor a running system through the CLI, CDR/CEL, AMI/ARI and metrics
- Apply active/standby high availability and horizontal scaling patterns
- Host Asterisk in the cloud safely behind NAT and a firewall

## Running Asterisk under systemd

On every current Linux distribution — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux
9 — the service manager is **systemd**. The install chapter showed that the
`make config` step (run during `make install`) installs a distribution init script
(`/etc/init.d/asterisk` on Debian, an `rc.d` script on RedHat), which systemd then
wraps automatically as a service; Asterisk also ships a native systemd unit under
`contrib/systemd/asterisk.service` that you can install in its place for finer control.
Either way, systemd is the supported, production way to run Asterisk. Cross-reference
*Installing Asterisk 22* for the build itself; here we focus on what the service gives
you and how to operate it.

### The service unit and its lifecycle

Once `make config` has installed the service, the lifecycle is ordinary systemd:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

A few operational notes:

- **`restart` vs. a graceful reload.** `systemctl restart` tears down the process and
  drops every call. For configuration changes you almost never want that — use the
  Asterisk CLI instead: `asterisk -rx 'core reload'` (or a module-specific reload such
  as `pjsip reload`). Reserve `systemctl restart` for upgrades or a wedged process.
- **Attach to the running daemon.** With Asterisk running as a service, open its
  console with `asterisk -r` (or `asterisk -rvvv` for verbose output). This connects
  to the already-running daemon over its control socket; it does not start a second
  copy.

### `Restart=` replaces safe_asterisk

Historically Asterisk was launched through the **safe_asterisk** wrapper, a shell
script that re-spawned Asterisk if it crashed. Under systemd that job belongs to the
unit's `Restart=` directive — systemd notices the process exit and brings it back,
with back-off controlled by `RestartSec=` and crash-loop protection by
`StartLimitIntervalSec=`/`StartLimitBurst=`. So on a systemd host **safe_asterisk is
superseded** and generally unnecessary. If your shipped unit does not already set it,
a drop-in override is the clean way to add restart-on-failure without editing the
packaged file:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Apply it with `systemctl daemon-reload && systemctl restart asterisk`. Using a drop-in
(rather than editing the installed unit) means a future `make config` will not clobber
your change.

### Running as a non-root user

Asterisk should not run as root in production — a remote-code bug in a process running
as root is a full host compromise, whereas the same bug in an unprivileged process is
contained. There are two complementary places this is enforced:

- **The unit / asterisk.conf.** The packaged unit normally runs Asterisk as the
  `asterisk` user and group. You can also (or instead) set `runuser` and `rungroup` in
  the `[options]` section of `asterisk.conf`, which the daemon honours when it drops
  privileges after binding:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **File ownership.** The runtime directories must be writable by that user. After
  creating the account, ensure ownership:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Because SIP (5060) and RTP (10000+) are all high ports, Asterisk does **not** need
root to bind them — only port-25-style privileged ports would, which Asterisk does not
use. Running unprivileged is therefore free. (The Security chapter expands on why this
matters; see *Asterisk Security*.)

## Containerizing Asterisk

एक कंटेनर Asterisk और उसकी सटीक निर्भरताओं को एक अपरिवर्तनीय इमेज में पैकेज करता है, इसलिए आप जो परीक्षण करते हैं वह बाइट‑फ़ॉर‑बाइट वही है जो आप शिप करते हैं। इसका समझौता रीयल‑टाइम मीडिया है: एक SIP सर्वर लेटेंसी के प्रति संवेदनशील होता है और बाहरी नेटवर्क से पहुँच योग्य UDP पोर्ट्स की एक विस्तृत, पूर्वानुमेय रेंज की आवश्यकता होती है, और कंटेनर नेटवर्किंग इसमें बाधा बन सकती है। इस अनुभाग का शेष भाग पुस्तक के अपने लैब — `lab/Dockerfile` और `lab/docker-compose.yml` — को एक ठोस, कार्यशील उदाहरण के रूप में दर्शाता है, और फिर वह एक आम जाल समझाता है जिसे हर कोई फंस जाता है: RTP और ब्रिज्ड नेटवर्किंग।

### The image: building Asterisk from source

लैब का `Dockerfile` Debian 12 पर स्रोत से Asterisk 22 बनाता है। इसका स्वरूप पढ़ने लायक है चाहे आप कभी खुद न बनाएं:

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Three things to call out:

- **The version is pinned** (`ARG ASTERISK_VERSION=22.10.0`). Reproducibility is the
  whole point of containerizing — bump it deliberately, rebuild, retest.
- **`--with-pjproject-bundled` and `--with-jansson-bundled`** build the SIP stack
  version-matched to Asterisk, so you depend on fewer apt packages and never fight a
  distro PJSIP that is out of step.
- **`CMD ["asterisk", "-f", "-vvv"]`** runs Asterisk in the *foreground* (`-f`, "do not
  fork"). This is the key difference from a systemd host: a container's main process
  must not daemonize, or the container would exit immediately. So in a container you do
  **not** use the systemd unit at all — the container runtime (Docker, plus `restart:`
  policy) becomes the supervisor that the unit's `Restart=` was on a VM.

### Bind-mounting `/etc/asterisk`

The image deliberately contains **no** configuration. Instead `docker-compose.yml`
bind-mounts the host's config directory in:

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro` maps the version-controlled `lab/asterisk/etc`  
directory onto the container's `/etc/asterisk`, read-only (`:ro`). The payoff is large:  
the image stays immutable and reusable, while configuration lives on the host where it  
can be edited and, crucially, kept in git (next section). To apply a config change you  
edit the file and reload — `docker compose exec asterisk asterisk -rx 'core reload'` —  
with no rebuild. `restart: unless-stopped` is the compose-level equivalent of  
systemd's `Restart=`: Docker restarts the container if Asterisk exits, but not if you  
deliberately stopped it.

### होस्ट बनाम ब्रिज्ड नेटवर्किंग — RTP समस्या

यह सबसे आम कंटेनराइज़्ड‑Asterisk विफलता है, इसलिए इसे ठीक‑ठीक समझना आवश्यक है। डिफ़ॉल्ट रूप से Docker एक कंटेनर को **ब्रिज्ड** नेटवर्क पर रखता है और आप व्यक्तिगत पोर्ट्स को `ports:` के साथ प्रकाशित करते हैं। सिग्नलिंग ठीक है — 5060 एक पोर्ट है। समस्या मीडिया की है: RTP UDP पोर्ट्स की *रेंज* का उपयोग करता है (लैब का `rtp.conf` सेट करता है `rtpstart=10000` / `rtpend=10100`), और **हर** पोर्ट जो ऑडियो ले जा सकता है उसे प्रकाशित करना पड़ता है।

लैब बिल्कुल यही करता है:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Note the RTP publish range (`10000-10100`) matches `rtp.conf` exactly. Get this wrong —
publish too few ports, or a different range than `rtp.conf` — and calls connect but
have **one-way or no audio**, because the RTP packets land on a port Docker is not
forwarding. Two further cautions with bridged mode:

- **Publishing thousands of ports is slow and heavy.** A production RTP range is
  typically 10000–20000. Docker creating ~10000 userland proxy forwards is expensive at
  start-up and adds a hop in the media path. The lab keeps a deliberately small
  100-port range because it only ever runs one or two test calls.
- **NAT in the SDP.** Behind the bridge, Asterisk sees its private container IP and may
  advertise it in SDP. On a public host you must tell PJSIP its external address with
  `external_media_address` / `external_signaling_address` on the transport (and set
  `local_net`), exactly as you would behind any NAT — see *Cloud hosting* below.

The alternative is **host networking** (`network_mode: host`), which removes the bridge
entirely: the container shares the host's network stack, so 5060 and the whole RTP
range are reachable with no port publishing and no extra media hop. This is the
recommended mode for a real Asterisk container — it sidesteps the RTP-range problem
completely. Its cost is isolation: the container can bind any host port and you lose
compose's per-service network. (Host networking is a Linux feature; on Docker Desktop
for macOS/Windows it behaves differently, which is partly why this teaching lab uses
explicit published ports instead.)

### Persistent volumes for spool and voicemail

A container's writable layer is **ephemeral** — destroy the container and anything it
wrote is gone. For Asterisk that means voicemail, recordings, the outgoing call spool
and the local database would vanish on every `docker compose up --build`. Configuration
survives because it is bind-mounted from the host; *state* needs the same treatment.
Inside the container the relevant trees are:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(The lab's running container shows exactly these — `/var/spool/asterisk` contains
`voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` holds
`astdb.sqlite3`.) To preserve them, mount named volumes for the directories that hold
state you care about:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

शिक्षण लैब ने इन्हें जानबूझकर छोड़ दिया है — यह डिज़ाइन के अनुसार स्टेटलेस और पुनरुत्पादनीय है, इसलिए हर `up` एक साफ़ स्लेट है — लेकिन एक प्रोडक्शन कंटेनर **must** इनका होना आवश्यक है, अन्यथा आप पहली रीडिप्लॉय पर वॉइसमेल खो देंगे।

## Configuration management and backups

The bind-mount above hints at the right model: treat `/etc/asterisk` as **code** and
the rest as **data**.

### Keep `/etc/asterisk` in version control

The config directory is a flat set of text files with no secrets that cannot be
templated — it is ideal for git. Initialise a repo in `/etc/asterisk` (or, as the lab
does, keep the config alongside the project and bind-mount it). Benefits:

- Every change is reviewable and revertible (`git diff`, `git revert`).
- You have an audit trail of who changed what and when.
- Combined with a container image, a known-good config commit plus a pinned image tag
  fully describes a deployment.

A couple of cautions specific to Asterisk config:

- **Secrets.** `pjsip.conf` (and `manager.conf`, `ari.conf`) contain passwords. Do not
  commit real secrets to a shared repo in clear text — template them (one file per
  environment, or a secrets manager / environment substitution at deploy time) and keep
  only placeholders in git. The lab's trivial `Lab-6001-secret` style passwords are fine
  *only* because they live on a private Docker subnet.
- **Per-environment templating.** The realtime values that differ between dev, staging
  and production (bind addresses, external IPs, trunk credentials, database URLs) are
  exactly the lines you templatize, keeping the bulk of the config identical across
  environments.

### What to back up

Configuration in git covers the dialplan and endpoints, but a live PBX accumulates
*state* that is not in any config file. A complete backup is:

| What | Where | Why |
|------|-------|-----|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (also in git) |
| Voicemail & recordings | `/var/spool/asterisk/` | user data — irreplaceable |
| Internal database | `/var/lib/asterisk/astdb.sqlite3` | `DB()` keys, device state |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` or SQL store | billing & history |
| External databases | your MySQL/PostgreSQL | realtime, CDR, voicemail |

The **astdb** deserves a note: it is Asterisk's small built-in key/value store (a
SQLite file at `/var/lib/asterisk/astdb.sqlite3`) used by `DB()` dialplan functions,
device states, follow-me settings and similar. You can dump it for inspection or backup
from the CLI:

```
asterisk -rx 'database show'
```

If your CDR/CEL or voicemail or PJSIP config lives in an external database (see
*Asterisk Real-Time* and *Asterisk Call Detail Records*), that database is now the
source of truth for that data and must be in your normal database backup rotation —
backing up `/etc/asterisk` alone is not enough.

## Monitoring and observability

आप वह नहीं चला सकते जो आप नहीं देख पाते। Asterisk अपनी स्थिति को चार स्तरों पर उजागर करता है, एक त्वरित मानव नज़र से लेकर मीट्रिक पाइपलाइन तक: **CLI**, **CDR/CEL** रिकॉर्ड्स, **AMI/ARI** इवेंट्स, और **metrics exporters**।

### CLI health checks

सबसे तेज़ "क्या यह स्वस्थ है?" जाँच CLI है। नीचे दिए गए कमांड्स को लैब के खिलाफ लाइव चलाया जाता है। पहले चैनल्स:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` एक शांत सिस्टम पर सामान्य है; एक व्यस्त सिस्टम पर यह आपका वास्तविक‑समय concurrency है। `core show uptime` पुष्टि करता है कि प्रक्रिया आपके तहत पुनः आरंभ नहीं हो रही है:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

For SIP health, `pjsip show endpoints` shows every endpoint and whether its registered
contacts are reachable. From the lab:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` यहाँ केवल यह दर्शाता है कि उन एंडपॉइंट्स पर वर्तमान में कोई फ़ोन पंजीकृत नहीं है (प्रयोगशाला में कोई लाइव क्लाइंट नहीं है) — एक सॉफ़्टफ़ोन पंजीकृत होने पर और `qualify` इसकी पुष्टि करने पर, स्थिति संपर्क को पहुँच योग्य दिखाती है। सहायक कमांड: `pjsip show contacts` (वर्तमान पंजीकरण और राउंड‑ट्रिप टाइम), `pjsip show transports`, और `pjsip show aor <name>` एक AOR के लिए। ये दैनिक उपयोग के “एक्सटेंशन X क्यों नहीं पहुँच रहा?” उपकरण हैं।

### CDR और CEL

हर कॉल एक **Call Detail Record** (CDR) छोड़ती है; **Channel Event Logging** (CEL) अधिक सूक्ष्म प्रति‑चैनल घटनाएँ जोड़ता है। पुष्टि करें कि CDR सक्रिय है और कौन‑सा बैकएंड इसे संग्रहीत करता है:

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

The lab shows `(none)` under registered backends because the minimal lab config loads
no CDR storage module — so records are computed but written nowhere. In production you
load a backend (CSV, or `cdr_odbc`/`cdr_adaptive_odbc` into MySQL/PostgreSQL) and that
becomes your billing and history source. CEL is **disabled by default** (`cel show
status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` only
when you need event-level detail. Both are covered in depth in *Asterisk Call Detail
Records*; for monitoring, the point is that CDR/CEL are your *historical* record, where
the CLI is your *live* view.

### AMI और ARI इवेंट्स

प्रोग्रामेटिक, रीयल‑टाइम मॉनिटरिंग के लिए आप इवेंट्स का पुश फ़ीड चाहते हैं न कि
CLI को पोल करना:

- **AMI (Asterisk Manager Interface)** एक पुराना TCP इवेंट/कमांड प्रोटोकॉल है
  (`manager.conf`). सब्सक्राइब करें और आपको `Newchannel`, `Hangup`, `DialBegin`,
  `BridgeEnter`, `PeerStatus` और इसी तरह के इवेंट्स कॉल होने पर मिलते हैं — वॉलबोर्ड
  और कॉल‑अकाउंटिंग टूल्स की रीढ़। लैब में AMI डिफ़ॉल्ट रूप से डिसेबल है (`manager show settings`
  reports `Manager (AMI): No`); आप इसे `manager.conf` में एनेबल और लॉक कर सकते हैं।
- **ARI (Asterisk REST Interface)** एक आधुनिक HTTP + WebSocket इंटरफ़ेस है
  (`ari.conf`, बिल्ट‑इन HTTP सर्वर द्वारा सर्व किया जाता है). यह JSON इवेंट स्ट्रीम और
  फाइन‑ग्रेन कॉल कंट्रोल प्रदान करता है — नई इंटीग्रेशन्स के लिए सही विकल्प।

दोनों को *Extending Asterisk with AMI and AGI* और *The Asterisk REST
Interface (ARI)* में विस्तृत रूप से बताया गया है। डिप्लॉयमेंट‑संबंधी
चेतावनी: **AMI और ARI बहुत शक्तिशाली हैं और इन्हें कभी भी इंटरनेट पर एक्सपोज़ नहीं करना चाहिए।** HTTP सर्वर को localhost या मैनेजमेंट नेटवर्क पर बाइंड करें, मजबूत और यूनिक सीक्रेट्स का उपयोग करें, और पोर्ट्स को फ़ायरवॉल करें — देखें *Asterisk Security*।

### मेट्रिक्स: Prometheus और Grafana

डैशबोर्ड और अलर्टिंग के लिए, Asterisk 22 एक Prometheus एक्सपोर्टर के साथ आता है,
**`res_prometheus.so`** (एक मॉड्यूल जिसमें *विस्तारित* सपोर्ट लेवल है), जो एक HTTP एंडपॉइंट पर मेट्रिक्स एक्सपोज़ करता है जिसे एक Prometheus सर्वर स्क्रैप करता है। कोर प्रोसेस मेट्रिक्स के साथ यह चैनल्स, कॉल्स, एंडपॉइंट्स, ब्रिजेज और PJSIP
आउटबाउंड रजिस्ट्रेशन्स को कवर करने वाले प्लगेबल प्रोवाइडर्स भी शिप करता है:

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

आप लैब बिल्ड में मॉड्यूल की उपस्थिति की पुष्टि कर सकते हैं:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

It shows `Not Running` because the lab does not configure or load it; enabling it (`prometheus.conf` plus the HTTP server) turns Asterisk into a Prometheus target. Point Prometheus at the scrape endpoint and Grafana at Prometheus, and you get time-series dashboards (concurrent calls, registrations, ASR/ACD trends) and alerting (e.g. "active calls dropped to zero" or "registration failures spiking"). For teams already running Prometheus/Grafana this is the natural way to fold Asterisk into existing observability, rather than parsing CLI output.

### SIP प्रतिक्रिया कोड जो देखना चाहिए

Whatever the pipeline, a few SIP results signal trouble and are worth alerting on: sustained `401`/`407` challenge failures or `403 Forbidden` suggest a brute-force or misconfigured-credential storm (cross-reference Fail2Ban in *Asterisk Security*); `503 Service Unavailable` points at an overloaded or congested server or trunk; and a spike in `408 Request Timeout`/`480 Temporarily Unavailable` usually means endpoints have gone unreachable (NAT timeout, qualify failures).

## High availability and scaling

One Asterisk server is a single point of failure and has a finite call ceiling. The two
problems — *staying up* and *getting bigger* — have different answers.

### Active/standby with a floating IP

The classic, well-trodden HA pattern for Asterisk is **active/standby** (not
active/active — call state in Asterisk is hard to share live). Two identical servers,
one active, one standby, share a **floating (virtual) IP** managed by a cluster manager
such as **keepalived** (VRRP) or **Pacemaker/Corosync**. Phones and trunks register to
the floating IP, not to either real host. If the active node fails its health check, the
floating IP moves to the standby, which takes over.

The honest caveat: an IP failover **drops calls in progress** — Asterisk does not
replicate live channel state between nodes, so anyone mid-call must redial. Registrations
re‑establish within a qualify/registration cycle. What failover buys you is that the
*service* recovers in seconds without manual intervention, which for most PBXs is exactly
the goal. To make the standby genuinely able to take over, both nodes need the same
configuration (your git'd `/etc/asterisk`, deployed identically) and the same *state* —
which is the next point.

### Externalize state with PJSIP Realtime

Active/standby only works if the standby knows about the same endpoints and
registrations as the active node. The way to achieve that is to **stop keeping state in
flat files on one box** and move it to a shared database both nodes read. **PJSIP
Realtime** (Sorcery backed by a database) does exactly this: endpoints, AORs, auths —
and, importantly, **registrations** (the `ps_contacts` table) — live in MySQL/PostgreSQL
instead of `pjsip.conf` and local memory. Both Asterisk nodes point at the same database,
so a phone registered through one node is visible to the other. This is covered in
*Asterisk Real-Time* (the PJSIP Realtime / Sorcery section); here the deployment point is
that **externalizing state is the prerequisite for both HA and horizontal scaling** —
without it, each node is an island.

Apply the same logic to the rest of your state: CDR/CEL into a shared SQL store, voicemail
on shared/replicated storage (or `ODBC_STORAGE`), and the astdb keys you depend on into a
database. Once state is external, the Asterisk nodes become closer to interchangeable
front‑ends.

### SIP proxies in front (OpenSIPS)

To scale *beyond* one server's capacity you put a **SIP proxy/load balancer** in front of
a pool of Asterisk media servers. **OpenSIPS** is a purpose‑built, very
high‑throughput SIP proxy (they handle hundreds of thousands of registrations and route
signaling without touching media). The proxy presents a single SIP address to the world,
maintains the registration/location service, and distributes calls across the Asterisk
back‑ends. This separation — a lightweight proxy tier doing registration and routing, a
horizontally‑scalable Asterisk tier doing the actual call processing (IVR, queues,
conferences, transcoding) — is how large deployments grow past a single box. (The SipPulse
platform itself uses OpenSIPS in front of its media/application servers for exactly this
reason.)

### Media scaling

The proxy distributes *signaling* cheaply; **media is the expensive resource**. RTP
relaying, and especially transcoding between codecs (e.g. Opus ↔ G.711) or running large
conferences, is CPU‑bound and is what actually caps a server. Strategies:

- **Avoid transcoding** wherever possible — negotiate a common codec end‑to‑end so
  Asterisk bridges natively (pass‑through) instead of transcoding. This is the single
  biggest media‑capacity win.
- **Scale media horizontally** by adding Asterisk nodes behind the proxy; each carries a
  share of the concurrent calls.
- **Offload browser media** to a dedicated WebRTC gateway (e.g. Janus) so the PBX is not
  also terminating and relaying every browser's DTLS‑SRTP stream — see *WebRTC with
  Asterisk*, which discusses exactly this Asterisk‑plus‑gateway split.

Size capacity by **concurrent calls and transcoding load**, not by registered users —
10,000 registered phones that are mostly idle are far cheaper than 200 simultaneous
transcoded conferences.

## Cloud hosting

Running Asterisk on a cloud VM (AWS, GCP, Azure, a VPS) is common and works well, but the
cloud network is **NAT'd and firewalled by default**, which fights with SIP. The
following are the deployment-specific concerns.

### NAT and the SDP

A cloud VM almost always has a **private** IP on its NIC and a separate **public** IP that
the provider NATs to it. If Asterisk advertises the private IP in SDP, remote phones send
RTP into a black hole — the classic one-way/no-audio symptom. Tell PJSIP its public
identity on the transport:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` make Asterisk rewrite the address it advertises to public peers, while
`local_net` tells it which peers are local (and should *not* be rewritten). This is the
same NAT handling discussed for bridged Docker networking above — a cloud VM is, in
effect, behind NAT.

### Firewall and the RTP range

Two firewalls usually apply on a cloud VM: the **provider's** security group / network
ACL, and the **host's** iptables. Both must open the same ports, and the policy is the
one from the Security chapter. The salvaged 1st-edition ruleset
(`docs/legacy-labs/configs/Lab7/rules.v4`) captures the shape — accept SIP and the RTP
range, accept established/related, drop the rest:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Two corrections the Security chapter makes that matter here: open **5061 on TCP** (not
UDP) if you run SIP/TLS, and remember that the RTP UDP range in your firewall must match
`rtpstart`/`rtpend` in `rtp.conf` exactly — the same range you publish on a container.
Do not duplicate the iptables/Fail2Ban build here; **follow the firewall, Fail2Ban and
TLS/SRTP sections of *Asterisk Security*** (Fail2Ban watches the `security` logger channel
that the lab already enables in `logger.conf`) and apply that policy in *both* the host
firewall and the cloud security group.

### Latency, region and the SBC

- **Choose a region close to your users.** Voice is latency-sensitive — one-way mouth-to-ear
  latency above ~150 ms is noticeable. Host the VM in the region nearest the bulk of your
  phones and trunks; cross-continent media is audibly worse.
- **Put an SBC in front for any internet-facing deployment.** A **Session Border
  Controller** terminates SIP/RTP at the edge, hides your topology, normalizes NAT, and
  absorbs DoS and scanning traffic before it reaches Asterisk. The Security chapter's core
  recommendation — *do not expose raw Asterisk to the internet* — applies doubly in the
  cloud, where your VM's public IP is being scanned within minutes of coming up. An SBC (or
  at minimum a hardened SIP proxy like OpenSIPS plus Fail2Ban) is the standard
  edge.

## Summary

Deployment वह जगह है जहाँ एक कार्यशील dialplan एक भरोसेमंद सेवा बन जाता है। एक VM पर, **systemd** के तहत Asterisk को **non-root** उपयोगकर्ता के रूप में चलाएँ, जिससे unit का `Restart=` इसे जीवित रखे (safe_asterisk अब पुराना है) और कॉन्फ़िगरेशन बदलावों के लिए `systemctl restart` की बजाय `core reload` का उपयोग करें। **Containerizing** Docker के साथ — जैसा कि पुस्तक के लैब में किया गया है — आपको एक अपरिवर्तनीय, पिन किया हुआ इमेज देता है जिसमें कॉन्फ़िग **bind-mounted** git‑ड किए हुए `/etc/asterisk` से आता है; यहाँ मुख्य बात मीडिया है, इसलिए या तो **host networking** उपयोग करें या एक RTP पोर्ट रेंज प्रकाशित करें जो **सटीक रूप से `rtp.conf`** से मेल खाती हो, और **persistent volumes** को spool/voicemail/astdb के लिए माउंट करें ताकि स्थिति पुनः‑डिप्लॉय पर बनी रहे। कॉन्फ़िग को कोड की तरह मानें और **state** का बैक‑अप लें क्योंकि कॉन्फ़िग में नहीं पकड़ा जाता: voicemail, recordings, `astdb.sqlite3`, और CDR/CEL। **Observe** सिस्टम को चार स्तरों पर देखें — CLI (`core show channels`, `pjsip show endpoints`) के लिए लाइव व्यू, इतिहास के लिए **CDR/CEL**, प्रोग्रामेटिक इवेंट्स के लिए **AMI/ARI**, और Grafana के लिए **`res_prometheus`** एक्सपोर्टर डैशबोर्ड और अलर्ट के साथ — जबकि AMI/ARI को सार्वजनिक इंटरनेट से दूर रखें। **stay up** रहने के लिए, **floating IP** के साथ active/standby चलाएँ (यह स्वीकार करते हुए कि फेलओवर लाइव कॉल्स को ड्रॉप कर देगा); **grow** करने के लिए, state को **PJSIP Realtime** के साथ बाहरी बनाएँ, मीडिया सर्वरों के पूल को **OpenSIPS** के साथ फ्रंट करें, और ट्रांसकोडिंग को न्यूनतम रखें क्योंकि **media — not registrations — is what caps a server**। अंत में, **cloud** में, VM को NAT के पीछे मानें (`external_media_address`, `local_net`), दोनों होस्ट और प्रोवाइडर सुरक्षा समूह में Security अध्याय के अनुसार फ़ायरवॉल खोलें, कम‑लेटेंसी वाला रीजन चुनें, और कभी भी कच्चा Asterisk उजागर न करें — एज पर एक **SBC** रखें।

## Quiz

1. On a systemd host, what replaces the old `safe_asterisk` wrapper's job of restarting a
   crashed Asterisk?
   - A. A cron job
   - B. The unit file's `Restart=` directive
   - C. `systemctl enable`
   - D. The astdb
2. To apply a configuration change to a running Asterisk **without dropping calls**, you should:
   - A. `systemctl restart asterisk`
   - B. Reboot the server
   - C. `asterisk -rx 'core reload'`
   - D. Rebuild the container image
3. A containerized (bridged-network) Asterisk connects calls but has **no audio**. The most likely cause is:
   - A. The dialplan is wrong
   - B. The published RTP UDP port range does not match `rtpstart`/`rtpend` in `rtp.conf`
   - C. CDR is disabled
   - D. The CLI is unreachable
4. Which directories must be mounted as **persistent volumes** so a container redeploy does not lose state? (check all that apply)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (already bind-mounted from the host)
   - D. `/usr/sbin`
5. Which CLI command gives the live count of active calls?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. In Asterisk 22, the supported way to expose call/channel metrics to a Prometheus/Grafana stack is:
   - A. Parsing the `full` log file
   - B. The `res_prometheus.so` module
   - C. AGI scripts
   - D. There is none
7. What is the prerequisite for both HA failover and horizontal scaling across multiple Asterisk nodes?
   - A. Running as root
   - B. Externalizing state (e.g. PJSIP Realtime registrations in a shared database)
   - C. Disabling CDR
   - D. Using bridged networking
8. Which resource most directly caps how many simultaneous calls one Asterisk server can handle?
   - A. The number of registered users
   - B. Media processing, especially transcoding
   - C. The size of `/etc/asterisk`
   - D. The CDR backend
9. On a cloud VM, which `pjsip.conf` transport settings make Asterisk advertise its public address so remote audio works? (check all that apply)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. For an internet-facing cloud deployment, the Security chapter's core rule is:
    - A. Always run two NICs
    - B. Never expose raw Asterisk to the internet; put an SBC (or hardened proxy + Fail2Ban) at the edge
    - C. Use UDP only
    - D. Disable TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
