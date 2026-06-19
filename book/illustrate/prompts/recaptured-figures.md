# Re-captured figures (real Asterisk 22 lab, not AI)

## 07-sip-and-pjsip-fig22.png — pjsip show history entry
Captured a real SIP message from the 22.10.0 lab:
1. `asterisk -rx 'pjsip set history on'`
2. send a SIP OPTIONS probe to 127.0.0.1:5060 (python UDP socket) → Asterisk replies 404
3. `asterisk -rx 'pjsip show history entry 1'` → the response with `Server: Asterisk PBX 22.10.0`
4. `asterisk -rx 'pjsip set history off'`
Rendered as a dark terminal slide (the long Accept capability list elided with `...`).
Replaces the 1st-ed screenshot that showed `Asterisk PBX 16.1.0`.

## 10-dialplan-advanced-features-img14.png — Comedian Mail (vmail.cgi) login
A browser cannot be screenshotted in this CLI lab, so this is a clean house-style
depiction of the REAL current form, with fields taken verbatim from the A22 source
`contrib/scripts/vmail.cgi` (TITLE "Asterisk Web-Voicemail"; "Comedian Mail Login";
Mailbox; Password; Login). The old img14/img15 were two halves of one dated IE6/XP/2004
screenshot — consolidated into this single figure; img15 retired to .trash/.
