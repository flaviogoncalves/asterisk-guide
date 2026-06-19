---
theme: seriph
title: 'Downloading and Installing Asterisk'
info: |
  ## Asterisk Guide — Chapter 2
  Downloading and Installing Asterisk. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Downloading and Installing Asterisk

Chapter 2

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

- **Determine** the hardware requirements for Asterisk
- **Install** Linux with the required dependencies
- **Download** a stable version over HTTPS
- **Compile** Asterisk from source
- **Start** Asterisk at boot time

</v-clicks>

<!--
This edition targets Asterisk 22 LTS (released 2024, supported through 2028-10-16).
We compile from source on Ubuntu 24.04 LTS to get an optimized build.
-->

---
layout: section
---

# Choosing the hardware

---

# Minimum hardware required

Asterisk runs on modest hardware — but a few factors drive what you need.

<div grid="~ cols-2 gap-8" class="mt-2 text-sm">
<div>

**Size it around**

- Registered users — registrations/second to support
- Simultaneous calls — conversations to bridge
- Codecs in use — high-complexity codecs (G.729, iLBC) burn CPU/FPU
- Echo cancellation — heavy; consider hardware DSPs
- Availability — RAID 1 or 5; Asterisk is a 24×7 app

</div>
<div>

**Practical advice**

- A robust **server-class network adapter** is the key component
- Offload G.729 with a DSP card (e.g. Sangoma TC400B → 120 G.729 calls)
- Stress-test capacity with **SIPP** before going live
- No telephony card? You still get an internal timer via `res_timing_timerfd`

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
ConfBridge and Music on Hold need a timing source — provided automatically on modern Linux. Confirm with <code>timing test</code>.
</div>

---

# Hardware configuration & IRQ sharing

<div grid="~ cols-2 gap-8" class="text-sm">
<div>

### Configuration tips

- Disable unused USB, serial, parallel ports — free up IRQs
- A robust NIC is essential
- Telephony cards may need a 3.3 V PCI / PCIe bus
- Use **server-grade disks** — a PBX runs 24×7, not 8×5

</div>
<div>

### IRQ sharing

Telephony cards (e.g. X100P) raise huge interrupt loads. On single-CPU systems, **avoid IRQ sharing**.

```text
# cat /proc/interrupts
       CPU0
 3: 413437739 XT-PIC wctdm  <-- TDM400
 7: 413453581 XT-PIC wcfxo  <-- X100P
 9: 413445182 XT-PIC wcfxo  <-- X100P
```

Each card on its own IRQ — good. Otherwise, rework the BIOS.

</div>
</div>

---
layout: section
---

# Preparing Linux

---

# Choosing a Linux distribution

Asterisk officially targets the RHEL family, Ubuntu, and Debian.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

**Good choices today**

- **Debian 12**
- **Ubuntu 22.04 / 24.04 LTS**
- **Rocky Linux 9 / AlmaLinux 9**

CentOS Linux is end-of-life — prefer Rocky or AlmaLinux on RHEL-family systems.

</div>
<div>

**This book uses Ubuntu 24.04 LTS**

- Install the **64-bit server** image, no GUI
- Grab the current point release ISO

```bash
https://releases.ubuntu.com/24.04/
# e.g. ubuntu-24.04.4-live-server-amd64.iso
```

</div>
</div>

<div class="mt-3 text-sm opacity-70">
Install without a graphical desktop, and configure an e-mail server (exim4) — voicemail notifications need it later.
</div>

---

# Installing dependencies

The recommended way in Asterisk 22: use the script that ships with the source tree — it knows the right package names per distribution.

```bash
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

<div class="mt-2">

Prefer to install them by hand on Debian/Ubuntu? The equivalent list:

```bash
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Source now lives on <strong>Git</strong> (no more <code>subversion</code>), and modern systems ship <code>libncurses-dev</code>, not <code>libncurses5-dev</code>.
</div>

---

# DAHDI — only if you have telephony cards

<div grid="~ cols-2 gap-8" class="text-sm">
<div>

**DAHDI** = Digium/Sangoma Asterisk Hardware Device Interface — drivers for analog and digital cards.

- Increasingly **niche** — most deployments are pure VoIP
- Install it **only** if you have physical telephony hardware
- Otherwise, **skip this section entirely**

</div>
<div>

**Get and unpack the source**

```bash
wget https://downloads.asterisk.org/pub/\
telephony/dahdi-linux-complete/\
dahdi-linux-complete-current.tar.gz

tar -xzvf dahdi-linux-complete-current.tar.gz
```

</div>
</div>

```bash
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version
make && make install
cd ../tools && autoreconf -i && ./configure && make && make install
make install-config
```

<div class="mt-2 text-sm opacity-70">
Then edit <code>/etc/dahdi/modules</code> to load only the drivers for the cards you actually have.
</div>

---
layout: section
---

# Compiling Asterisk

---

# Which version to choose

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

Asterisk alternates **LTS** (long-term support) and standard releases.

- **Asterisk 22 = current LTS** — released 2024, supported through 2028
- Asterisk 20 — previous LTS
- Asterisk 16 (1st edition) — **end-of-life**

</div>
<div>

**Rule of thumb**

- Pick the version with the features you need
- For production, **always choose an LTS** release

</div>
</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
Verify the exact current point release at <strong>downloads.asterisk.org</strong> before going to print — the 22 branch is the active LTS.
</div>

---

# Download and build

<div grid="~ cols-2 gap-8 text-sm">
<div>

**1 — Download the source**

```bash
cd /usr/src
wget https://downloads.asterisk.org/pub/\
telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

**2 — Install prerequisites**

```bash
cd asterisk-22.x.y
./contrib/scripts/install_prereq install
```

</div>
<div>

**3 — Configure the build**

```bash
./configure
```

**4 — Select modules**

```bash
make menuselect
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
Compiling from source lets you produce code optimized for your hardware.
</div>

---

# Selecting modules with menuselect

`make menuselect` opens a text menu to choose applications, codecs, channels, and resources to build.

<div grid="~ cols-2 gap-8" class="text-sm mt-2">
<div>

**Channels**

- **chan_pjsip** (*Channel Drivers*) — the modern SIP channel, **enabled by default**
- It is the **only** SIP channel in Asterisk 22

</div>
<div>

**Codecs**

- **codec_opus** (*Codec Translators*) — *external* module; enabling it fetches the free, closed-source binary from Sangoma/Digium
- Opus **pass-through** needs no extra module
- **codec_g729** — free binary, but lawful transcoding needs a per-channel license

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>chan_sip was removed in Asterisk 21</strong> — it no longer exists in Asterisk 22. The Channel Drivers screen shows <code>chan_pjsip</code> and no <code>chan_sip</code>.
</div>

---

# Build, install, and create the config

After **Save & Exit** in menuselect, build and install:

```bash
make
make install
make samples
make config
ldconfig
```

<div grid="~ cols-2 gap-8 text-sm mt-3">
<div>

- `make install` — binaries and modules
- `make samples` — sample config into `/etc/asterisk`
- `make config` — installs the SysV init script for your distro

</div>
<div>

- `ldconfig` — refreshes the shared-library cache
- A **systemd** unit ships at `contrib/systemd/asterisk.service`, but `make config` does **not** install it — copy it yourself

</div>
</div>

---
layout: section
---

# Running Asterisk

---

# Starting and stopping Asterisk

<div grid="~ cols-2 gap-8 text-sm">
<div>

**Foreground (learning / debugging)**

```bash
/usr/sbin/asterisk -vvvgc
```

Stop from the CLI:

```text
CLI> core stop now
```

**As a daemon**

```bash
/sbin/asterisk
```

</div>
<div>

**Connect to a running instance**

```bash
asterisk -r        # connect to the CLI
asterisk -rvvv     # connect, verbose
```

More than one console can attach at the same time.

</div>
</div>

---

# Starting Asterisk with systemd

On modern Linux (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), the recommended way to run Asterisk in production is **systemd**.

```bash
cp contrib/systemd/asterisk.service /etc/systemd/system/asterisk.service
systemctl daemon-reload
```

```bash
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
The unit's <code>Restart=</code> directive replaces the legacy <strong>safe_asterisk</strong> wrapper — automatic restart is built in.
</div>

---

# Runtime options & directories

<div grid="~ cols-2 gap-8 text-sm">
<div>

**Common runtime flags** (`asterisk -h`)

- `-c` — provide console CLI
- `-r` / `-R` — connect (reconnect) to a running instance
- `-v` — increase verbosity
- `-d` — increase debugging
- `-x <cmd>` — execute a CLI command
- `-U` / `-G` — run as a non-root user / group

</div>
<div>

**Install directories** — set in `asterisk.conf`

```ini
[directories](!)
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astspooldir => /var/spool/asterisk
astlogdir => /var/log/asterisk

[options]
;verbose = 3       ; raise to 15 for training
;maxcalls = 10     ; protect from overload
;maxload = 0.9
```

</div>
</div>

---

# Logging and log rotation

<div grid="~ cols-2 gap-8 text-sm">
<div>

Logs live in `/var/log/asterisk`, configured by **`logger.conf`**.

```ini
[logfiles]
console  => notice,warning,error
messages => notice,warning,error
;full    => notice,warning,error,debug,verbose,dtmf,fax
;security => security
```

Inspect and rotate from the CLI:

```text
CLI> logger show channels
CLI> logger rotate
```

</div>
<div>

Hand off rotation to **logrotate** — drop a file in `/etc/logrotate.d`:

```ini
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
     /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

</div>
</div>

---

# Uninstalling & deployment notes

<div grid="~ cols-2 gap-8 text-sm">
<div>

**Uninstall**

```bash
make uninstall        # binaries & modules
make uninstall-all    # also config files
```

</div>
<div>

**Production & network tips**

- Run Asterisk as a **non-root user** — limits damage if compromised
- Keep CPU usage under **~40%**; no X-Windows or heavy DBs on the box
- For IP phones, **QoS** is non-negotiable
- Avoid 10/100 Mbps hubs; prefer full-duplex switches and **VLANs**

</div>
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Set up the lab on your computer**

Instead of compiling by hand, boot the reproducible Asterisk 22 Docker lab and get a working PBX in minutes.

See **Lab 0 — Set up the lab** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Runs on Windows, macOS, or Linux — no telephony hardware required.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- Asterisk runs on **modest hardware** — size it around users, calls, codecs, and echo cancellation.
- We install on **Ubuntu 24.04 LTS** (no GUI) and let `install_prereq` pull the dependencies.
- **DAHDI** is only needed for physical analog/digital cards — pure-VoIP setups skip it.
- Always choose an **LTS** release; **Asterisk 22** is the current LTS.
- Build from source: `./configure` → `make menuselect` → `make` → `install` → `samples` → `config`.
- **chan_pjsip** is the only SIP channel; `chan_sip` was removed in Asterisk 21.
- Run it under **systemd** and as a **non-root** user in production.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Building Your First PBX (PJSIP)</strong> — your first endpoints and a call.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 2 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which channel driver provides SIP in Asterisk 22, and what is the recommended way to install the build dependencies?</em>
</div>
