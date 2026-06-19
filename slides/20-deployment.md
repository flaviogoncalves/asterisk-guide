---
theme: seriph
title: 'Deployment, Monitoring & Scaling'
info: |
  ## Asterisk Guide — Chapter 18
  Deployment, monitoring and scaling. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Deployment, Monitoring & Scaling

Chapter 18

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

- **Run** Asterisk 22 reliably under systemd, as a non-root user, with automatic restart
- **Containerize** Asterisk with Docker and understand the networking trade-offs
- **Keep** `/etc/asterisk` in version control and back up the right state
- **Monitor** through the CLI, CDR/CEL, AMI/ARI and metrics
- **Apply** active/standby high availability and horizontal scaling patterns
- **Host** Asterisk in the cloud safely behind NAT and a firewall

</v-clicks>

<!--
This is everything that happens AFTER the dialplan works: keeping the service alive,
observable, backed up, and able to grow. All verified against the book's Asterisk 22 lab.
-->

---
layout: section
---

# Running Asterisk under systemd

---

# The service unit and its lifecycle

On every current Linux distro — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — the service manager is **systemd**.

`make config` installs the init/service wrapper; Asterisk also ships a native unit at `contrib/systemd/asterisk.service`.

```bash
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start (drops calls!)
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

<div class="mt-3 text-sm" style="border-left: 4px solid #1C5D99; padding-left: 0.75rem;">
For config changes, never <code>restart</code> — use <code>asterisk -rx 'core reload'</code>. Attach to the live daemon with <code>asterisk -r</code> (or <code>-rvvv</code>); it does not start a second copy.
</div>

---

# `Restart=` replaces safe_asterisk

Historically Asterisk was launched through the **safe_asterisk** wrapper, which re-spawned it on crash. Under systemd that is the unit's `Restart=` directive — so safe_asterisk is **superseded**.

Add restart-on-failure cleanly with a drop-in override (a future `make config` won't clobber it):

```ini
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

```bash
systemctl daemon-reload && systemctl restart asterisk
```

<div class="mt-2 text-sm opacity-70">
Back-off via <code>RestartSec=</code>; crash-loop protection via <code>StartLimitIntervalSec=</code> / <code>StartLimitBurst=</code>.
</div>

---

# Running as a non-root user

Asterisk should **not** run as root in production — a remote-code bug as root is a full host compromise; the same bug unprivileged is contained.

<div grid="~ cols-2 gap-8 mt-2">
<div>

**The unit / asterisk.conf**

The packaged unit runs as the `asterisk` user/group. You can also set this in `asterisk.conf`:

```ini
[options]
runuser = asterisk
rungroup = asterisk
```

</div>
<div>

**File ownership**

Runtime directories must be writable by that user:

```bash
chown -R asterisk:asterisk \
  /var/lib/asterisk /var/log/asterisk \
  /var/spool/asterisk /var/run/asterisk \
  /etc/asterisk
```

</div>
</div>

<div class="mt-3 text-sm opacity-70">
SIP (5060) and RTP (10000+) are high ports — no root needed to bind them. Running unprivileged is free.
</div>

---
layout: section
---

# Containerizing Asterisk

---

# The image: building from source

A container packages Asterisk and its exact dependencies into one **immutable** image — what you test is byte-for-byte what you ship. The lab's `Dockerfile` builds Asterisk 22 on Debian 12:

```text
ARG ASTERISK_VERSION=22.10.0
RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" && make install && make install-logrotate && ldconfig
EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

<v-clicks>

- **Version pinned** (`22.10.0`) — reproducibility is the whole point; bump deliberately, rebuild, retest.
- **`--with-pjproject-bundled` / `--with-jansson-bundled`** — SIP stack version-matched to Asterisk.
- **`-f` (foreground)** — the container's main process must not daemonize. No systemd unit in a container; the **runtime + `restart:` policy** is the supervisor.

</v-clicks>

---

# Bind-mounting `/etc/asterisk`

The image contains **no** configuration. `docker-compose.yml` bind-mounts the host's config, read-only:

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

<div class="mt-2 text-sm">

The image stays immutable; config lives on the host where it can be **edited and kept in git**. Apply a change with a reload, no rebuild:

</div>

```bash
docker compose exec asterisk asterisk -rx 'core reload'
```

<div class="mt-1 text-sm opacity-70">
<code>restart: unless-stopped</code> is the compose equivalent of systemd's <code>Restart=</code>.
</div>

---

# Host vs. bridged networking — the RTP problem

The single most common containerized-Asterisk failure. Signaling (5060) is one port; **media is a *range*** of UDP ports, and every port that might carry audio must be published.

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"   # MUST match rtp.conf exactly
```

<div grid="~ cols-2 gap-6 mt-2 text-sm">
<div>

**Bridged-mode cautions**

- Range must match `rtpstart`/`rtpend`, or calls connect with **one-way / no audio**.
- Publishing thousands of ports is **slow and heavy** (~10000 userland proxies).
- **NAT in SDP** — set `external_*` + `local_net`.

</div>
<div>

**Host networking** — `network_mode: host`

- Shares the host stack; the whole RTP range is reachable with **no port publishing**, no extra hop.
- Recommended for a real container.
- Cost: less isolation; Linux-only (differs on Docker Desktop).

</div>
</div>

---

# Persistent volumes for state

A container's writable layer is **ephemeral** — config survives (bind-mounted), but *state* would vanish on every rebuild. Mount named volumes for the trees that hold state:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings
      - ast-lib:/var/lib/asterisk            # astdb.sqlite3
      - ast-log:/var/log/asterisk            # logs

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

<div class="mt-2 text-sm" style="border-left: 4px solid #1C5D99; padding-left: 0.75rem;">
The teaching lab omits these on purpose — it is stateless by design. A <strong>production</strong> container must have them, or you lose voicemail on the first redeploy.
</div>

---
layout: section
---

# Configuration management & backups

---

# Config is code, the rest is data

<div grid="~ cols-2 gap-8">
<div>

### Keep `/etc/asterisk` in git

A flat set of text files — ideal for version control.

- Every change is reviewable and revertible (`git diff`, `git revert`)
- An audit trail of who changed what, when
- A known-good config commit + a pinned image tag fully describe a deployment

**Caution:** `pjsip.conf`, `manager.conf`, `ari.conf` hold passwords — **template secrets**, commit placeholders only.

</div>
<div>

### What to back up

| What | Where |
|------|-------|
| Configuration | `/etc/asterisk/` |
| Voicemail & recordings | `/var/spool/asterisk/` |
| Internal database | `/var/lib/asterisk/astdb.sqlite3` |
| CDR / CEL | `cdr-csv/` or SQL store |
| External databases | your MySQL / PostgreSQL |

</div>
</div>

```text
*CLI> database show     ; dump the astdb key/value store for inspection/backup
```

<div class="mt-1 text-sm opacity-70">
If CDR/CEL, voicemail or PJSIP config lives in an external DB, that DB is now the source of truth — back it up too.
</div>

---
layout: section
---

# Monitoring & observability

---

# CLI health checks

The fastest "is it healthy?" check. Channels first, then uptime to confirm it has not been restarting under you:

```text
*CLI> core show channels
0 active channels
0 active calls
0 calls processed

*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

For SIP health, `pjsip show endpoints` shows every endpoint and contact reachability:

```text
*CLI> pjsip show endpoints
 Endpoint:  6001                          Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                        1
Objects found: 4
```

<div class="mt-1 text-sm opacity-70">
<code>Unavailable</code> = no phone registered yet. Companions: <code>pjsip show contacts</code>, <code>pjsip show transports</code>, <code>pjsip show aor &lt;name&gt;</code>.
</div>

---

# CDR / CEL, AMI / ARI

<div grid="~ cols-2 gap-8 text-sm">
<div>

### History — CDR & CEL

Every call leaves a **Call Detail Record**; **CEL** adds per-channel events.

```text
*CLI> cdr show status
  Logging:   Enabled
  Mode:      Simple
* Registered Backends
    (none)
```

`(none)` = no storage module loaded. In production load CSV or `cdr_adaptive_odbc` into SQL. CEL is **off by default** (enable in `cel.conf`).

</div>
<div>

### Live events — AMI & ARI

- **AMI** — long-standing TCP event/command protocol (`manager.conf`): `Newchannel`, `Hangup`, `DialBegin`, `PeerStatus`…
- **ARI** — modern HTTP + WebSocket (`ari.conf`): JSON event stream + fine-grained call control. Best for new integrations.

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>AMI and ARI must never be exposed to the internet.</strong> Bind to localhost / a management network, use strong secrets, firewall the ports — see <em>Securing Asterisk</em>.
</div>

---

# Metrics: Prometheus & Grafana

Asterisk 22 ships a Prometheus exporter, **`res_prometheus.so`** (*extended* support), exposing metrics on an HTTP endpoint that Prometheus scrapes:

<div grid="~ cols-2 gap-8 text-sm">
<div>

```text
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
# channels
asterisk_channels_count
asterisk_channels_state
# calls
asterisk_calls_count
# endpoints
asterisk_endpoints_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

</div>
<div>

```text
*CLI> module show like prometheus
res_prometheus.so   ...   Not Running  extended
```

Point Prometheus at the scrape endpoint and Grafana at Prometheus for time-series dashboards (concurrent calls, registrations, ASR/ACD) and alerting.

**SIP codes worth alerting on:** sustained `401`/`407`/`403` (brute force), `503` (overload/congestion), spikes in `408`/`480` (endpoints unreachable).

</div>
</div>

---
layout: section
---

# High availability & scaling

---

# Active/standby with a floating IP

The classic HA pattern is **active/standby** (not active/active — live call state is hard to share). Two identical nodes share a **floating (virtual) IP** managed by **keepalived** (VRRP) or **Pacemaker/Corosync**.

<v-clicks>

- Phones and trunks register to the **floating IP**, not to either real host.
- If the active node fails its health check, the IP **moves to the standby**.
- **Honest caveat:** failover **drops calls in progress** — Asterisk does not replicate live channel state. Registrations re-establish within a qualify/registration cycle.
- The win: the *service* recovers in **seconds**, without manual intervention.

</v-clicks>

<div class="mt-3 text-sm opacity-70">
Both nodes need the same config (your git'd <code>/etc/asterisk</code>) <strong>and</strong> the same state — next slide.
</div>

---

# Externalize state, then scale out

<div grid="~ cols-2 gap-8 text-sm">
<div>

### PJSIP Realtime

Stop keeping state in flat files on one box. **PJSIP Realtime** (Sorcery + a DB) moves endpoints, AORs, auths — and crucially **registrations** (`ps_contacts`) — into MySQL/PostgreSQL both nodes read.

Externalizing state is the **prerequisite** for both HA and horizontal scaling. Apply the same to CDR/CEL, voicemail (`ODBC_STORAGE`) and astdb keys.

</div>
<div>

### SIP proxies in front

To scale *beyond* one server, put **OpenSIPS** in front of a pool of Asterisk media servers. The proxy does registration + routing (no media); Asterisk does call processing.

*(SipPulse itself uses OpenSIPS in front of its media/application servers.)*

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Media — not registrations — caps a server.</strong> Avoid transcoding (negotiate a common codec end-to-end), scale media horizontally, and offload browser media to a WebRTC gateway (Janus). Size by concurrent calls + transcoding load, not registered users.
</div>

---
layout: section
---

# Cloud hosting

---

# NAT, the SDP, and the firewall

A cloud VM has a **private** NIC IP and a NAT'd **public** IP. If Asterisk advertises the private IP in SDP, remote RTP goes into a black hole. Tell PJSIP its public identity:

```ini
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

Open the **same ports in both** the provider security group and the host iptables (RTP range must match `rtp.conf`):

```text
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

<div class="mt-1 text-sm opacity-70">
Run SIP/TLS? Open <strong>5061 on TCP</strong>. Follow the firewall / Fail2Ban / TLS-SRTP sections of <em>Securing Asterisk</em>.
</div>

---

# Latency, region & the SBC

<div grid="~ cols-2 gap-8 mt-2">
<div>

### Choose a close region

Voice is latency-sensitive — one-way mouth-to-ear above **~150 ms** is noticeable. Host the VM nearest the bulk of your phones and trunks; cross-continent media is audibly worse.

</div>
<div>

### Put an SBC at the edge

A **Session Border Controller** terminates SIP/RTP at the edge, hides topology, normalizes NAT, and absorbs DoS/scanning before it reaches Asterisk.

</div>
</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Never expose raw Asterisk to the internet.</strong> A cloud VM's public IP is scanned within minutes of coming up. An SBC — or at minimum a hardened proxy (OpenSIPS) plus Fail2Ban — is the standard edge.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Deploy the Asterisk 22 container the way the book runs it**

Build the pinned image, bind-mount `/etc/asterisk` from git, publish the RTP range to match `rtp.conf`, and reload with `core reload`.

See the **Deployment lab** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
The same reproducible Docker lab you have used throughout the book — host or bridged, your choice.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- On a VM: run under **systemd**, **non-root**, with `Restart=` (safe_asterisk superseded); use **`core reload`**, not `systemctl restart`, for config changes.
- **Containerize** with an immutable, pinned image and config **bind-mounted** from a git'd `/etc/asterisk`; either use **host networking** or publish an RTP range that **exactly matches `rtp.conf`**, and mount **persistent volumes** for state.
- **Back up** what config doesn't capture: voicemail, recordings, `astdb.sqlite3`, CDR/CEL.
- **Observe** at four levels — CLI (live), CDR/CEL (history), AMI/ARI (events), `res_prometheus` → Grafana (dashboards) — keeping AMI/ARI off the public internet.
- **Stay up:** active/standby + **floating IP** (failover drops live calls). **Grow:** externalize state with **PJSIP Realtime**, front with **OpenSIPS**; **media caps a server**.
- **Cloud:** treat the VM as behind NAT (`external_media_address`, `local_net`), open both firewalls, pick a low-latency region, put an **SBC** at the edge.

</v-clicks>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 18 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>A bridged-network container connects calls but has no audio — what is the most likely cause?</em>
</div>
