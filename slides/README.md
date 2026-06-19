# Asterisk Guide — Slides (Slidev)

Presentation decks for *Asterisk Guide* (2nd edition, **Asterisk 22 LTS**, PJSIP-first),
authored in **[Slidev](https://sli.dev)** Markdown — **one deck per chapter**. The content is
sourced from the modernized, lab-verified book chapters in `../src/chapters/`, and the figures
are the book's modernized figures (shared via `public/images` → `../src/images`).

## Decks

Each chapter is a standalone Markdown deck named to match its book chapter:

| Deck | Chapter |
|------|---------|
| `02-introduction.md` | 1 — Introduction to Asterisk PBX |
| `03-installing-asterisk.md` | 2 — Downloading and Installing Asterisk |
| `04-first-pbx-pjsip.md` | 3 — Building Your First PBX (PJSIP) |
| `06-designing-voip-network.md` | 4 — Designing a VoIP Network |
| `07-sip-and-pjsip.md` | 5 — SIP and PJSIP |
| `08-webrtc.md` | 6 — WebRTC |
| `09-sip-trunking.md` | 7 — SIP Trunking |
| `10-legacy-channels.md` | 8 — Legacy Channels |
| `10a-migration-to-pjsip.md` | 9 — Migrating from chan_sip to PJSIP |
| `12-dialplan.md` | 10 — The Dial Plan |
| `13-pbx-features.md` | 11 — PBX Features |
| `14-queues.md` | 12 — Queues and Call Centers |
| `16-cdr-cel.md` | 13 — CDR and CEL |
| `17-ami-agi-ari.md` | 14 — Extending Asterisk (AMI/AGI) |
| `17a-ari.md` | 15 — The Asterisk REST Interface (ARI) |
| `18-realtime.md` | 16 — Realtime |
| `19-security.md` | 17 — Securing Asterisk |
| `20-deployment.md` | 18 — Deployment |

(The book's part dividers and front matter are not decks.)

## Run a deck

```bash
cd slides
npm install            # first time only
npx slidev 02-introduction.md      # live-present the Introduction deck (opens a browser)
```

Press `e` in the browser to edit live; arrow keys to navigate; `o` for the overview.

## Export to PDF / PPTX / PNGs

```bash
npx slidev export 02-introduction.md                 # -> 02-introduction-export.pdf
npx slidev export 02-introduction.md --format pptx   # -> PowerPoint, if you still need it
npx slidev export 02-introduction.md --format png    # one PNG per slide
```

Export everything:

```bash
for f in *.md; do npx slidev export "$f"; done
```

## Conventions (house style for every deck)

- **Theme:** `seriph` (serif headings), brand accent **`#1C5D99`** to match the book.
- **First slide:** chapter title + "Asterisk Guide · Asterisk 22 LTS".
- **Second slide:** *Objectives* ("By the end of this chapter you will be able to…"), taken
  from the chapter's `## Objectives`.
- **Section dividers:** `layout: section`.
- **Config/CLI:** fenced code blocks with language hints (`ini` for config, `bash` for shell, `text` for CLI output) — PJSIP
  only (`pjsip.conf`, `PJSIP/…`, `pjsip show …`); never `chan_sip`/`sip.conf`/`SIP/…`.
- **Figures:** `![alt](/images/NN-...-figNN.png)` (served from `public/images`).
- **Labs:** a `layout: center` slide pointing at the matching lab in `../labs/LAB-GUIDE.md`.
- **Last slide:** *Summary* + a short quiz teaser.

New decks are authored with the `book-design` / chapter conventions and verified against the
Asterisk 22 lab, exactly like the book.
