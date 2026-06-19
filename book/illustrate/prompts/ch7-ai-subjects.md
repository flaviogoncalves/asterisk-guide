# Chapter 07 — SIP & PJSIP: figure routing

No PATH 3 (Nano Banana / paid AI) figures were generated for this chapter.
Total AI spend: $0.00.

All redrawn figures were produced by `book/illustrate/render_07.py` (Pillow, house style:
white bg, ink #1A1A1A, accent #1C5D99, 1600x900, system fonts).

| fig | route | notes |
|-----|-------|-------|
| fig01 | PATH 1 (Pillow) | SIP main components architecture — redrawn flat from dated 3D clip-art |
| fig02 | PATH 1 (Pillow) | SIP registration; fixed OCR garble "wSIP/2.0" → "SIP/2.0 200 OK"; domain voip.school |
| fig03 | PATH 1 (Pillow) | Proxy operation INVITE/200 OK with direct RTP |
| fig04 | PATH 1 (Pillow) | Redirect operation 302 + direct INVITE/200 OK/ACK |
| fig05 | PATH 1 (Pillow) | direct_media=yes (was mislabeled "directmedia" in original) |
| fig06 | PATH 1 (Pillow) | direct_media=no (both SIP + RTP anchored through Asterisk) |
| fig11 | PATH 1 (Pillow) | Full Cone NAT |
| fig12 | PATH 1 (Pillow) | Symmetric NAT (per-destination port, breaks STUN) |
| fig14 | PATH 1 (Pillow) | PJSIP config object relationships (endpoint/transport/auth/aor/contact/identify/registration; acl + domain_alias stand alone) |

KEPT (real CLI captures — not redrawn, redrawing would fabricate output):
fig15 `pjsip show endpoints`, fig16 `pjsip show endpoint xlite`, fig17 `pjsip show registrations`,
fig18 `pjsip list endpoints`, fig19 `pjsip list contacts`, fig20 `pjsip set history on`,
fig21 `pjsip show history`, fig22 `pjsip show history entry 3`.

Flag: fig22 (genuine capture) shows "Server: Asterisk PBX 16.1.0" — left untouched because it is a
real packet capture; re-rendering it would fabricate CLI output. A future re-capture on the
Asterisk 22 lab would refresh the version string.
