# Target Asterisk 22 LTS with a restructured 2nd edition

The 2nd edition targets **Asterisk 22 LTS** (newest LTS, supported to 2028-10-16) rather than
the conservative 20 LTS or the bleeding-edge 23 standard release, trading a small amount of
extra rewriting (chan_sip is gone in 21+) for the longest shelf life.

We chose a **bigger restructure** over a 1:1 in-place update: the original 16 chapters are
regrouped into 4 parts, the SIP-protocol and PJSIP chapters merge, the analog/digital/IAX2
chapters consolidate into one "Legacy channels" chapter, and three net-new chapters are added
(WebRTC, SIP trunking/DID/PSTN, Deployment/monitoring/scaling). Rationale: a 2026 Asterisk book
that still gives three chapters to TDM and omits WebRTC misrepresents how Asterisk is deployed
today.

Because **chan_sip was removed in Asterisk 21**, the legacy SIP chapter is retained for protocol
theory and reframed as a `sip.conf → pjsip.conf` migration guide; PJSIP is presented as *the*
SIP channel.

## Consequences

- Every config/CLI example must be re-verified against Asterisk 22 (chan_sip examples are no
  longer runnable). A Dockerized Asterisk 22 lab is the verification reference.
- Readers on Asterisk 20 lose some 1:1 applicability for SIP config; the migration guide covers them.
- The restructure invalidates the 1st-edition chapter numbering and cross-references.
