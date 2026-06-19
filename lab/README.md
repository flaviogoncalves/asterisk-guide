# Asterisk 22 lab

A reproducible Asterisk 22 LTS environment used to **lab-verify every example in the book**.
It also serves as the worked example for the install and Deployment chapters.

## What's inside

- `Dockerfile` — Asterisk 22.10.0 built from source on Debian 12 (the install-chapter build).
- `asterisk/etc/` — minimal, correct config: PJSIP transport, endpoints, dialplan.
  - `6001` / `6002` — auth'd endpoints for the **SipPulse Softphone** (register from your LAN).
  - `sipp` — IP-identified endpoint (no auth) for **headless SIPp** verification.
- `sipp/` — SIPp driver image + scenarios (`uac_9000.xml` places a call to extension `9000`).
- `lab.sh` — control + verification helper.

## Usage

```bash
./lab.sh up        # build + start
./lab.sh status    # pjsip show endpoints / transports / dialplan
./lab.sh verify    # headless SIPp smoke test: call 9000, assert 200 OK
./lab.sh cli       # Asterisk CLI
./lab.sh down      # stop + remove
```

## Connect the SipPulse Softphone

Register against the host running the lab, port 5060/udp:

| Field    | Value                |
|----------|----------------------|
| Username | `6001` (or `6002`)   |
| Password | `Lab-6001-secret`    |
| Domain   | `<lab-host-ip>`      |

Then dial `6002`, `600` (echo test), or `9000` (greeting + echo).

> Lab credentials are intentionally trivial and bound to a private Docker subnet.
> Never reuse this config on a public interface.
