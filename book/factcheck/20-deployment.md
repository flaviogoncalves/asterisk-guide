# Fact-check ledger — Deployment, monitoring & scaling

Verified: 28 · Wrong (fixed): 1 · Unverified: 1

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "On every current Linux distribution — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — the service manager is **systemd**" | 28 | VERIFIED | General fact; all listed distros ship systemd as PID 1. |
| 2 | "the `make config` step (run during `make install`) drops a systemd unit file into place" | 31 (orig) | WRONG (fixed) | `make config` installs a **SysV init script** on Debian (`contrib/init.d/rc.debian.asterisk` → `/etc/init.d/asterisk`) and RedHat rc.d scripts — NOT the systemd unit. The native unit ships in `contrib/systemd/asterisk.service` but is not installed by `make config`. lab: `sed -n '929,990p' Makefile` shows the Debian branch installs `rc.debian.asterisk`; `find … -name "*.service"` shows `contrib/systemd/asterisk.service` exists separately. Corroborated by docs.asterisk.org/Operation/Running-Asterisk (shows SysV rc*.d symlinks). Text rewritten. |
| 3 | "`asterisk -rx 'core reload'` (or a module-specific reload such as `pjsip reload`)" reloads config without dropping calls | 51-53 | VERIFIED | `core reload` and `pjsip reload` are valid CLI reload commands; reload does not tear down channels (vs systemctl restart). lab: commands accepted. |
| 4 | "open its console with `asterisk -r` … connects to the already-running daemon over its control socket; it does not start a second copy" | 54-57 | VERIFIED | lab: `asterisk -h` → "-r  Connect to Asterisk on this machine"; "-x <cmd>  Execute command (implies -r)". |
| 5 | "Historically Asterisk was launched through the **safe_asterisk** wrapper" | 61 | VERIFIED | lab: `contrib/scripts/safe_asterisk` present in source tree. |
| 6 | "systemd … with back-off controlled by `RestartSec=` and crash-loop protection by `StartLimitIntervalSec=`/`StartLimitBurst=`" | 64-65 | VERIFIED | Standard systemd directives (systemd.service(5) / systemd.unit(5)). |
| 7 | drop-in `Restart=always` / `RestartSec=2` example | 70-75 | VERIFIED | Valid systemd drop-in syntax. Note: shipped `contrib/systemd/asterisk.service` already sets `Restart=always`/`RestartSec=4`; book's "if your shipped unit does not already set it" hedge is correct. lab: grep of asterisk.service. |
| 8 | "set `runuser` and `rungroup` in the `[options]` section of `asterisk.conf`" | 88-96 | VERIFIED | lab: `grep runuser/rungroup configs/samples/asterisk.conf.sample` → `;runuser = asterisk` `;rungroup = asterisk` under [options]. |
| 9 | shipped unit "normally runs Asterisk as the `asterisk` user and group" | 87 | VERIFIED | lab: `contrib/systemd/asterisk.service` has `User=asterisk` `Group=asterisk`. |
| 10 | "SIP (5060) and RTP (10000+) are all high ports, Asterisk does **not** need root to bind them" | 106-108 | VERIFIED | General fact: ports ≥1024 are unprivileged on Linux; Asterisk binds no privileged port. |
| 11 | "`CMD ["asterisk", "-f", "-vvv"]` runs Asterisk in the *foreground* (`-f`, "do not fork")" | 159 | VERIFIED | lab: `asterisk -h` → "-f  Do not fork". |
| 12 | Dockerfile `ARG ASTERISK_VERSION=22.10.0`, `--with-pjproject-bundled`/`--with-jansson-bundled`, EXPOSE/CMD | 126-150 | VERIFIED | lab: `grep Dockerfile` matches every quoted line. |
| 13 | compose bind-mount `./asterisk/etc:/etc/asterisk:ro`, ports 5060/udp + 10000-10100/udp, `restart: unless-stopped` | 170-191 | VERIFIED | lab: `cat lab/docker-compose.yml` matches. |
| 14 | "the lab's `rtp.conf` sets `rtpstart=10000` / `rtpend=10100`" | 199-200 | VERIFIED | lab: `grep rtpstart/rtpend /etc/asterisk/rtp.conf` → `rtpstart=10000` `rtpend=10100`. |
| 15 | host networking via `network_mode: host` removes the bridge; Linux feature, differs on Docker Desktop mac/Win | 224-231 | VERIFIED | Docker docs: host network driver is Linux-only natively; behaves differently on Desktop. |
| 16 | spool tree contains voicemail, monitor, outgoing, recording; lib holds astdb.sqlite3 | 242-249 | VERIFIED | lab: `ls /var/spool/asterisk` → voicemail, monitor, outgoing, recording (+others); `ls /var/lib/asterisk` → astdb.sqlite3. |
| 17 | astdb is "a SQLite file at `/var/lib/asterisk/astdb.sqlite3`" used by `DB()` etc. | 311-312 | VERIFIED | lab: file present; `database show` returns key/value entries. |
| 18 | "`asterisk -rx 'database show'`" dumps astdb | 316 | VERIFIED | lab: `database show` → returns `/pbx/UUID …  1 results found`. |
| 19 | `core show channels` output (active channels/calls/processed) | 336-341 | VERIFIED | lab: `core show channels` → "0 active channels / 0 active calls / N call(s) processed". |
| 20 | `core show uptime` shows "System uptime" + "Last reload" | 347-350 | VERIFIED | lab: `core show uptime` → "System uptime: … / Last reload: …". |
| 21 | `pjsip show endpoints` output with Endpoint/InAuth/Aor; Unavailable = no registration | 356-373 | VERIFIED | lab: output matches shape (6001, 6002, webrtc-1000 shown Unavailable). Note: lab now also has a `sipp` endpoint, so "Objects found: 4" while book lists 3 — minor lab drift, illustrative. |
| 22 | companion cmds `pjsip show contacts`, `pjsip show transports`, `pjsip show aor <name>` exist | 372-373 | VERIFIED | lab: `core show help pjsip show` lists contacts, transports, aor. |
| 23 | `cdr show status` shows Logging Enabled / Mode Simple / Registered Backends (none) | 381-393 | VERIFIED | lab: `cdr show status` output matches exactly incl. "(none)". |
| 24 | "CEL is **disabled by default** (`cel show status` reports `CEL Logging: Disabled`)" | 399-401 | VERIFIED | lab: `cel show status` → "CEL Logging: Disabled". |
| 25 | "AMI is disabled by default (`manager show settings` reports `Manager (AMI): No`)" | 412-413 | VERIFIED | lab: `manager show settings` → "Manager (AMI): No". |
| 26 | AMI events `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` | 411 | VERIFIED | lab: `manager show events` lists Newchannel, DialBegin, BridgeEnter, PeerStatus (Hangup is a standard AMI event). |
| 27 | "Asterisk 22 ships a Prometheus exporter, **`res_prometheus.so`** (a module with *extended* support level)" + Not Running in lab | 425-434 | VERIFIED | lab: `module show like prometheus` → `res_prometheus.so … Not Running … extended`. |
| 28 | res_prometheus "exposes call counts, channel counts, endpoint state and bridge metrics" | 427-428 | UNVERIFIED | docs.asterisk.org res_prometheus page only enumerates "core metrics" (version, uptime, reload time) explicitly; channel/bridge/endpoint/call counters are part of the module's design but not exhaustively listed in the config doc. Module presence + support level VERIFIED; the specific metric list could not be confirmed from official docs. |
| 29 | PJSIP Realtime registrations live in the `ps_contacts` table | 480-482 | VERIFIED | lab: `grep ps_contacts contrib/ast-db-manage/config/versions/` → official Alembic migrations define `ps_contacts`. |
| 30 | transport NAT options `external_media_address`, `external_signaling_address`, `local_net` valid in PJSIP 22 | 542-546 | VERIFIED | lab: `config show help res_pjsip transport external_media_address` / `…external_signaling_address` / `…local_net` all return option info. |
| 31 | "one-way mouth-to-ear latency above ~150 ms is noticeable" | 580 | VERIFIED | ITU-T Rec. G.114: below 150 ms interactivity essentially transparent; 150–400 ms acceptable with awareness. itu.int/rec G.114. |
| 32 | legacy ruleset cited at `docs/legacy-labs/configs/Lab7/rules.v4` (accept SIP 5060, RTP 10000:20000, lo, established, drop) | 557-567 | VERIFIED | repo: file exists; contains `--dport 5060`, `--dport 10000:20000`, `-i lo`, `RELATED,ESTABLISHED`, `-j DROP`. |
| 33 | "open **5061 on TCP** (not UDP) if you run SIP/TLS" | 569-570 | VERIFIED | SIP/TLS runs over TCP; 5061 is the standard SIP-TLS port (RFC 3261). |
| 34 | `make install-logrotate` is a real target | 145 | VERIFIED | lab: `grep install-logrotate Makefile` → target present. |

## Summary

- **Verified:** 32 (rows counted as 33/34 with sub-claims; headline count 28 distinct factual assertions + corroborated infra claims).
- **Wrong (fixed):** 1 — the `make config` "drops a systemd unit file" claim (row 2); corrected to describe the SysV init script that `make config` installs (which systemd wraps) plus the separately-shipped `contrib/systemd/asterisk.service`.
- **Unverified:** 1 — the exact res_prometheus metric inventory (row 28). Module presence and "extended" support level are verified in the lab; the specific list "call counts, channel counts, endpoint state and bridge metrics" is not exhaustively enumerated in the official config docs. Author should confirm against res_prometheus source / a running exporter before print.

## Unverified items the author must resolve

1. **res_prometheus metric list** (line 427-428): confirm "call counts, channel counts, endpoint state and bridge metrics" against an actual `/metrics` scrape or the module source; docs only spell out "core metrics."
