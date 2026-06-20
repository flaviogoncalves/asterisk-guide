# Deployment, monitoring & scaling

Asterisk in einem Labor dazu zu bringen, einen Anruf anzunehmen, ist das eine; es als Dienst
laufen zu lassen, der Abstürze, Neustarts, Upgrades und Angreifer übersteht — und den man beobachten,
sichern und erweitern kann — ist das andere. Dieses Kapitel behandelt alles, was *nach*
dem Dialplan funktioniert, passiert. Wir beginnen mit dem Supervisor, der Asterisk am Leben hält
(systemd), gehen weiter zur Verpackung in einem Container (unter Verwendung des im Buch eigenen Docker‑Labs als
Beispiel), dann behandeln wir Konfigurationsmanagement und Backups, Monitoring und
Observability und schließlich die Muster, die man greift, wenn ein Server nicht ausreicht:
High Availability und Scaling sowie die Realitäten des Hostings in der Cloud.

Alles Gezeigte ist gegen das Asterisk 22‑Lab des Buches in `lab/` verifiziert — derselbe
Container, den Sie im gesamten Buch aufgebaut haben.

## Objectives

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Asterisk 22 zuverlässig unter systemd auszuführen, als Nicht‑Root‑Benutzer, mit automatischem Neustart
- Asterisk mit Docker zu containerisieren und die Netzwerkkompromisse zu verstehen
- `/etc/asterisk` in der Versionskontrolle zu behalten und den richtigen Zustand zu sichern
- Ein laufendes System über die CLI, CDR/CEL, AMI/ARI und Metriken zu überwachen
- Aktive/Passive Hochverfügbarkeit und horizontale Skalierungsmuster anzuwenden
- Asterisk sicher in der Cloud hinter NAT und einer Firewall zu hosten

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

Ein Container paketiert Asterisk und seine genauen Abhängigkeiten in ein unveränderliches Image, sodass das, was Sie testen, byte‑für‑byte das ist, was Sie ausliefern. Der Kompromiss liegt beim Echtzeit‑Media: Ein SIP‑Server ist empfindlich gegenüber Latenz und benötigt einen breiten, vorhersehbaren Bereich an UDP‑Ports, die von außen erreichbar sind, und die Container‑Netzwerk­konfiguration kann dabei hinderlich sein. Der Rest dieses Abschnitts führt durch das Labor des Buches — `lab/Dockerfile` und `lab/docker-compose.yml` — als konkretes, funktionierendes Beispiel und erklärt dann die eine Falle, in die jeder gerät: RTP und gebridgedes Networking.

### The image: building Asterisk from source

Das Labor‑`Dockerfile` baut Asterisk 22 aus dem Quellcode auf Debian 12. Die Struktur davon lohnt sich zu lesen, selbst wenn Sie nie selbst eines erstellen:

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

`./asterisk/etc:/etc/asterisk:ro` mappt das versionskontrollierte `lab/asterisk/etc` Verzeichnis auf das Container-`/etc/asterisk`, schreibgeschützt (`:ro`). Der Nutzen ist groß:
Das Image bleibt unveränderlich und wiederverwendbar, während die Konfiguration auf dem Host lebt, wo sie
bearbeitet werden kann und, entscheidend, in git gehalten wird (nächster Abschnitt). Um eine Konfigurationsänderung anzuwenden, editieren Sie die Datei und laden neu — `docker compose exec asterisk asterisk -rx 'core reload'` —
ohne Neuaufbau. `restart: unless-stopped` ist das Compose‑Ebene‑Äquivalent zu
systemd's `Restart=`: Docker startet den Container neu, wenn Asterisk beendet wird, jedoch nicht, wenn Sie ihn
absichtlich gestoppt haben.

### Host vs. Bridged-Netzwerk — das RTP-Problem

Dies ist der häufigste containerisierte-Asterisk-Fehler, daher lohnt es sich,
dies genau zu verstehen. Standardmäßig legt Docker einen Container in ein **bridged** Netzwerk
und Sie veröffentlichen einzelne Ports mit `ports:`. Das Signaling ist in Ordnung — 5060 ist ein Port.
Das Problem ist das Medium: RTP verwendet einen *Bereich* von UDP-Ports (die Lab‑`rtp.conf` setzt
`rtpstart=10000` / `rtpend=10100`), und **jeder** Port, der Audio transportieren könnte, muss
veröffentlicht werden.

Das Labor macht genau das:

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

Das Lehrlabor lässt diese absichtlich weg — es ist zustandslos und von Grund auf reproduzierbar,  
so dass jedes `up` ein sauberer Neustart ist — aber ein Produktions‑Container **muss** sie haben, sonst  
verlierst du die Voicemail beim ersten erneuten Bereitstellen.

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

## Überwachung und Beobachtbarkeit

Sie können nichts betreiben, was Sie nicht sehen können. Asterisk stellt seinen Zustand auf vier Ebenen bereit, von einem schnellen menschlichen Blick bis zu einer Metrik‑Pipeline: die **CLI**, die **CDR/CEL**‑Aufzeichnungen, **AMI/ARI**‑Ereignisse und **metrics exporters**.

### CLI-Gesundheitsprüfungen

Der schnellste „Ist es gesund?“-Check ist die CLI. Die untenstehenden Befehle werden live gegen das Labor ausgeführt. Channels zuerst:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` auf einem ruhigen System ist normal; bei einem stark ausgelasteten ist dies Ihre Echtzeit‑Parallelität. `core show uptime` bestätigt, dass der Prozess nicht unter Ihnen neu gestartet wird.

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Für die SIP‑Gesundheit zeigt `pjsip show endpoints` jeden Endpunkt und ob seine registrierten Kontakte erreichbar sind. Aus dem Labor:

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

`Unavailable` here simply means no phone is currently registered to those endpoints (the
lab has no live clients) — once a softphone registers and `qualify` confirms it, the
state shows the contact as reachable. Companion commands: `pjsip show contacts` (current
registrations and round-trip time), `pjsip show transports`, and `pjsip show aor <name>`
for one AOR. These are the day-to-day "why can't extension X be reached?" tools.

### CDR und CEL

Every call leaves a **Call Detail Record** (CDR); **Channel Event Logging** (CEL) adds
finer per-channel events. Confirm CDR is active and which backend stores it:

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

Das Labor zeigt `(none)` unter registrierten Backends, weil die minimale Labor‑Konfiguration kein CDR‑Speichermodul lädt — die Datensätze werden berechnet, aber nirgendwo geschrieben. In der Produktion laden Sie ein Backend (CSV oder `cdr_odbc`/`cdr_adaptive_odbc` in MySQL/PostgreSQL) und das wird zu Ihrer Abrechnungs‑ und Historienquelle. CEL ist **standardmäßig deaktiviert** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` nur wenn Sie Detail‑Ereignisse benötigen. Beide werden ausführlich in *Asterisk Call Detail Records* behandelt; für das Monitoring ist der Punkt, dass CDR/CEL Ihre *historischen* Aufzeichnungen sind, während die CLI Ihre *Live‑* Ansicht liefert.

### AMI und ARI‑Ereignisse

Für programmatisches, Echtzeit‑Monitoring möchten Sie einen Push‑Feed von Ereignissen statt das Abfragen der CLI:

- **AMI (Asterisk Manager Interface)** ist das langjährige TCP‑Ereignis‑/Befehls‑Protokoll (`manager.conf`). Abonnieren Sie und Sie erhalten `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` und ähnliche Ereignisse, sobald Anrufe stattfinden — das Rückgrat von Wallboards und Anruf‑Abrechnungstools. Im Labor ist AMI standardmäßig deaktiviert (`manager show settings` meldet `Manager (AMI): No`); Sie aktivieren und sperren es in `manager.conf`.
- **ARI (Asterisk REST Interface)** ist die moderne HTTP + WebSocket‑Schnittstelle (`ari.conf`, bereitgestellt vom integrierten HTTP‑Server). Sie liefert einen JSON‑Ereignis‑Stream und feinkörnige Anrufsteuerung — die richtige Wahl für neue Integrationen.

Beide werden in *Extending Asterisk with AMI and AGI* und *The Asterisk REST Interface (ARI)* detailliert beschrieben. Der deploymentsrelevante Hinweis: **AMI und ARI sind leistungsfähig und dürfen niemals dem Internet ausgesetzt werden.** Binden Sie den HTTP‑Server an localhost oder ein Verwaltungsnetzwerk, verwenden Sie starke, eindeutige Secrets und blockieren Sie die Ports per Firewall — siehe *Asterisk Security*.

### Metriken: Prometheus und Grafana

Für Dashboards und Alarmierung liefert Asterisk 22 einen Prometheus‑Exporter, **`res_prometheus.so`** (ein Modul mit *erweitertem* Support‑Level), der Metriken über einen HTTP‑Endpunkt bereitstellt, den ein Prometheus‑Server abruft. Neben Kernprozess‑Metriken liefert er plug‑in‑fähige Anbieter für Kanäle, Anrufe, Endpunkte, Bridges und PJSIP‑ausgehende Registrierungen.

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

Sie können bestätigen, dass das Modul im Lab-Build vorhanden ist:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

It shows `Not Running` because the lab does not configure or load it; enabling it
(`prometheus.conf` plus the HTTP server) turns Asterisk into a Prometheus target. Point
Prometheus at the scrape endpoint and Grafana at Prometheus, and you get time-series
dashboards (concurrent calls, registrations, ASR/ACD trends) and alerting (e.g. "active
calls dropped to zero" or "registration failures spiking"). For teams already running
Prometheus/Grafana this is the natural way to fold Asterisk into existing observability,
rather than parsing CLI output.

### SIP-Antwortcodes, die es zu beobachten gilt

Whatever the pipeline, a few SIP results signal trouble and are worth alerting on:
sustained `401`/`407` challenge failures or `403 Forbidden` suggest a brute-force or
misconfigured-credential storm (cross-reference Fail2Ban in *Asterisk Security*);
`503 Service Unavailable` points at an overloaded or congested server or trunk; and a
spike in `408 Request Timeout`/`480 Temporarily Unavailable` usually means endpoints
have gone unreachable (NAT timeout, qualify failures).

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
re-establish within a qualify/registration cycle. What failover buys you is that the
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
front-ends.

### SIP proxies in front (OpenSIPS)

To scale *beyond* one server's capacity you put a **SIP proxy/load balancer** in front of
a pool of Asterisk media servers. **OpenSIPS** is a purpose-built, very
high-throughput SIP proxy (they handle hundreds of thousands of registrations and route
signaling without touching media). The proxy presents a single SIP address to the world,
maintains the registration/location service, and distributes calls across the Asterisk
back-ends. This separation — a lightweight proxy tier doing registration and routing, a
horizontally-scalable Asterisk tier doing the actual call processing (IVR, queues,
conferences, transcoding) — is how large deployments grow past a single box. (The SipPulse
platform itself uses OpenSIPS in front of its media/application servers for exactly this
reason.)

### Media scaling

The proxy distributes *signaling* cheaply; **media is the expensive resource**. RTP
relaying, and especially transcoding between codecs (e.g. Opus ↔ G.711) or running large
conferences, is CPU-bound and is what actually caps a server. Strategies:

- **Avoid transcoding** wherever possible — negotiate a common codec end-to-end so
  Asterisk bridges natively (pass-through) instead of transcoding. This is the single
  biggest media-capacity win.
- **Scale media horizontally** by adding Asterisk nodes behind the proxy; each carries a
  share of the concurrent calls.
- **Offload browser media** to a dedicated WebRTC gateway (e.g. Janus) so the PBX is not
  also terminating and relaying every browser's DTLS-SRTP stream — see *WebRTC with
  Asterisk*, which discusses exactly this Asterisk-plus-gateway split.

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
  latency above ~150 ms is noticeable. Host the VM in the region nearest the bulk of your
  phones and trunks; cross-continent media is audibly worse.
- **Put an SBC in front for any internet-facing deployment.** A **Session Border
  Controller** terminates SIP/RTP at the edge, hides your topology, normalizes NAT, and
  absorbs DoS and scanning traffic before it reaches Asterisk. The Security chapter's core
  recommendation — *do not expose raw Asterisk to the internet* — applies doubly in the
  cloud, where your VM's public IP is being scanned within minutes of coming up. An SBC (or
  at minimum a hardened SIP proxy like OpenSIPS plus Fail2Ban) is the standard
  edge.

## Zusammenfassung

Deployment ist der Ort, an dem ein funktionierender Dialplan zu einem zuverlässigen Service wird. Auf einer VM läuft Asterisk unter **systemd** als **non-root**‑Benutzer, wobei die Einheit `Restart=` ihn am Leben hält (safe_asterisk ist überholt) und **`core reload`** anstelle von `systemctl restart` für Konfigurationsänderungen verwendet wird. **Containerisierung** mit Docker – wie es das Labor des Buches macht – liefert ein unveränderliches, festgelegtes Image mit **bind‑gemounteter** Konfiguration aus einem git‑verwalteten `/etc/asterisk`; das Problem ist das Media, also entweder **host networking** verwenden oder einen RTP‑Port‑Bereich veröffentlichen, der **genau zu `rtp.conf`** passt, und **persistente Volumes** für spool/voicemail/astdb mounten, damit der Zustand einen Redeploy überlebt. Betrachte die Konfiguration als Code und **sichere den Zustand**, den die Konfiguration nicht erfasst: Voicemail, Aufnahmen, `astdb.sqlite3` und CDR/CEL. **Beobachte** das System auf vier Ebenen – die CLI (`core show channels`, `pjsip show endpoints`) für die Live‑Ansicht, **CDR/CEL** für die Historie, **AMI/ARI** für programmatische Ereignisse und den **`res_prometheus`**‑Exporter nach Grafana für Dashboards und Alarme – wobei AMI/ARI vom öffentlichen Internet ferngehalten wird. Um **laufend verfügbar** zu bleiben, betreibe ein Active/Standby‑Setup mit einer **floating IP** (unter der Annahme, dass ein Failover laufende Anrufe abbricht); um **zu wachsen**, externalisiere den Zustand mit **PJSIP Realtime**, setze einen Pool von Media‑Servern mit **OpenSIPS** vor und minimiere Transcoding, weil **Media – nicht Registrierungen – das ist, was einen Server begrenzt**. Schließlich, in der **cloud**, betrachte die VM als hinter NAT (`external_media_address`, `local_net`), öffne die Firewall gemäß dem Sicherheitskapitel sowohl im Host als auch in der Sicherheitsgruppe des Anbieters, wähle eine Region mit niedriger Latenz und setze Asterisk niemals roh ein – stelle ein **SBC** an den Rand.

## Quiz

1. Auf einem systemd‑Host, was ersetzt die alte `safe_asterisk`‑Wrapper‑Aufgabe, einen abgestürzten Asterisk neu zu starten?
   - A. Ein Cron‑Job
   - B. Die `Restart=`‑Direktive der Unit‑Datei
   - C. `systemctl enable`
   - D. Die astdb
2. Um eine Konfigurationsänderung an einem laufenden Asterisk **ohne Anrufe zu unterbrechen** anzuwenden, sollten Sie:
   - A. `systemctl restart asterisk`
   - B. Den Server neu starten
   - C. `asterisk -rx 'core reload'`
   - D. Das Container‑Image neu bauen
3. Ein containerisierter (Bridged‑Network) Asterisk verbindet Anrufe, hat aber **keinen Ton**. Die wahrscheinlichste Ursache ist:
   - A. Der Dialplan ist falsch
   - B. Der veröffentlichte RTP‑UDP‑Port‑Bereich stimmt nicht mit `rtpstart`/`rtpend` in `rtp.conf` überein
   - C. CDR ist deaktiviert
   - D. Die CLI ist nicht erreichbar
4. Welche Verzeichnisse müssen als **persistente Volumes** gemountet werden, damit ein erneutes Deployen des Containers den Zustand nicht verliert? (alle zutreffenden auswählen)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (bereits vom Host bind‑gemountet)
   - D. `/usr/sbin`
5. Welcher CLI‑Befehl liefert die aktuelle Anzahl aktiver Anrufe?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. In Asterisk 22 ist die unterstützte Methode, Call/Channel‑Metriken für einen Prometheus/Grafana‑Stack bereitzustellen:
   - A. Das Parsen der `full`‑Logdatei
   - B. Das `res_prometheus.so`‑Modul
   - C. AGI‑Skripte
   - D. Es gibt keine
7. Was ist die Voraussetzung sowohl für HA‑Failover als auch für horizontales Skalieren über mehrere Asterisk‑Knoten hinweg?
   - A. Ausführung als root
   - B. Externalisierung des Zustands (z. B. PJSIP‑Realtime‑Registrierungen in einer gemeinsamen Datenbank)
   - C. Deaktivierung von CDR
   - D. Verwendung von Bridged‑Networking
8. Welche Ressource begrenzt am direktesten, wie viele gleichzeitige Anrufe ein Asterisk‑Server verarbeiten kann?
   - A. Die Anzahl registrierter Benutzer
   - B. Medienverarbeitung, insbesondere Transcoding
   - C. Die Größe von `/etc/asterisk`
   - D. Das CDR‑Backend
9. Auf einer Cloud‑VM, welche `pjsip.conf`‑Transport‑Einstellungen lassen Asterisk seine öffentliche Adresse ankündigen, sodass Remote‑Audio funktioniert? (alle zutreffenden auswählen)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Für ein internet‑exponiertes Cloud‑Deployment ist die Kernregel des Security‑Kapitel:
    - A. Immer zwei NICs einsetzen
    - B. Nie rohen Asterisk direkt ins Internet stellen; ein SBC (oder gehärteter Proxy + Fail2Ban) an der Edge platzieren
    - C. Nur UDP verwenden
    - D. TLS deaktivieren

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
