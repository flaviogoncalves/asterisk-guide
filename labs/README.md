# Hands-On Labs

A standalone, cross-platform lab manual for *Asterisk Guide* — runnable on **Windows, macOS, or
Linux** with nothing but **Docker**. No SIP hardware, no analog cards, no legacy `chan_sip`:
pure PJSIP on Asterisk 22.10.0.

**Start here → [`LAB-GUIDE.md`](LAB-GUIDE.md)**

The guide opens with a **Lab Credentials** page (every username, password, and the shared SIP
trunk on `sip.flagonc.com`), then walks through:

| Lab | Topic |
|----:|-------|
| 0 | Install Docker and start the lab (Windows/macOS/Linux) |
| 1 | Your first calls (phone-to-phone, echo test) |
| 2 | A dial plan with an auto-attendant (IVR) |
| 3 | Voicemail |
| 4 | A call queue |
| 5 | Connect a real SIP trunk (`sip.flagonc.com`) |
| 6 | A WebRTC phone in the browser |
| 7 | Securing SIP with TLS and SRTP |
| 8 | Controlling Asterisk with ARI |

Every command in the guide was verified against the Docker lab in [`../lab/`](../lab/). The lab
environment itself (Dockerfile, compose, base config) lives there; this folder is just the
student-facing workbook.

Authoring new labs is driven by the **`practical-lab-creator`** skill
(`.claude/skills/practical-lab-creator/`).
