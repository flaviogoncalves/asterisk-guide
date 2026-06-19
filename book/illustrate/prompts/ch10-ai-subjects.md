# Chapter 10 — Legacy Channels: figure routing

No PATH 3 (Nano Banana / paid AI) figures were generated for this chapter.
**Total AI spend: $0.00.**

All redrawn figures were produced by `book/illustrate/render_10.py` (Pillow, house style:
white bg, ink #1A1A1A, accent #1C5D99, 1600x900, system fonts). This is the Legacy Channels
chapter, so analog (FXS/FXO), TDM (E1/T1, PCM), DAHDI, MFC/R2 and IAX2 content is in scope.

Labels cross-checked against the chapter text (no fact-check ledger exists for ch10):
- fig08 — E1 = 32 timeslots @ 2048 Kbps, DS0 #0 frame sync, DS0 #16 CAS signaling; T1 = 24
  timeslots @ 1544 Kbps, 1 framing bit/frame, robbed-bit CAS or the 24th channel as the
  D-channel (PRI/ISDN). Removed the original's ambiguous "DS0 #24" loose label.
- fig09 — DAHDI stack: Asterisk → chan_dahdi (libpri=ISDN, libopenr2=MFC/R2, libss7=SS7) →
  /dev/dahdi → DAHDI kernel driver → card interface kernel driver. Matches ch text line 614.
  Recolored from the dated green/red original into house style.
- fig11 — MFC/R2 call flow. AB line-signaling codes verified against the chapter's ABCD state
  table (Idle 10, Seized 00, Seize Ack 11, Answer 01, Clearback 11, Clear Forward 10). MF
  inter-register signals I-X / A-1 / A-3 / B-6 per Q.441 table. Translated the original's
  Portuguese leftovers ("Retorno da Campainha"→Ringback, "Discado"→dialed, "Rede IP"→IP
  Network) and relabeled the three line styles (in-band MF/audio, timeslot-16 line signaling,
  audible/voice).
- fig12/fig14/fig15 — IAX2: single UDP port 4569, 15-bit call number; trunk topologies.
- fig13 — IAX2-trunk vs SIP overhead; kept the original's byte counts and the 156/66 totals.
- fig16 — IAX auth decision flow, redrawn from the broken/garbled original with corrected
  logic and connections (username→section→IP→secret→ACCEPT; guest / secret-matches-a-user
  fallbacks; DENY on failure).

| fig | route | reason |
|-----|-------|--------|
| fig01 | PATH 1 (Pillow) | FXS/FXO conceptual diagram — redrawn flat from dated grayscale clip-art |
| fig02 | PATH 1 (Pillow) | VoIP gateway / OPX topology — redrawn flat |
| fig03 | **KEEP** | Real photo of a Xorcom Astribank (USB channel bank) — pictorial capture |
| fig04 | **KEEP** | Real photo of a TDM404P analog card with annotations — pictorial capture |
| fig05 | PATH 1 (Pillow) | E1/T1 provisioning (UTP/fiber/microwave) — redrawn flat |
| fig06 | **KEEP** | Real photos of digital cards + balun ("UTP or BNC?") — pictorial capture |
| fig07 | PATH 1 (Pillow) | PCM sampling concept — redrawn flat |
| fig08 | PATH 1 (Pillow) | E1/T1 TDM framing — redrawn flat, label fix (DS0 loose label dropped) |
| fig09 | PATH 1 (Pillow) | DAHDI stack — recolored from green/red into house style |
| fig10 | **KEEP** | Real photos of a TE205P dual-span card + E1/T1/J1 jumper — pictorial capture |
| fig11 | PATH 1 (Pillow) | MFC/R2 call flow sequence — redrawn, Portuguese removed, states verified |
| fig12 | PATH 1 (Pillow) | IAX2 UDP-4569 multiplexing — redrawn flat ("Rede IP"→IP Network) |
| fig13 | PATH 1 (Pillow) | IAX2-trunk vs SIP byte-field overhead — redrawn flat |
| fig14 | PATH 1 (Pillow) | IAX trunk to a VoIP provider — redrawn flat |
| fig15 | PATH 1 (Pillow) | Two Asterisk servers over an IAX trunk — redrawn flat |
| fig16 | PATH 1 (Pillow) | IAX auth decision flow — rebuilt with corrected logic/connections |
| fig17 | PATH 1 (Pillow) | Jitter buffer water-tank metaphor — redrawn flat |

Cross-reference figures `07-sip-and-pjsip-fig07/08/09/10/13` are reused from chapter 7 and
are out of scope here (owned + tracked by ch07).
