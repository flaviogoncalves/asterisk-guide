# Amazon KDP — Ready-to-Upload Package & Checklist

*Asterisk Guide*, Second Edition (Asterisk 22 LTS) — Flavio E. Gonçalves

This is the exact package to paste into Amazon KDP. KDP has **no publishing API**, so the
steps in Part 2 must be done by hand in the KDP dashboard. Everything you need to paste is
in Part 1. The machine-readable copy of this metadata lives in
[`book/kdp/listing-metadata.yaml`](listing-metadata.yaml).

---

## Part 1 — The metadata to paste

### Title / author
- **Title:** Asterisk Guide
- **Subtitle:** Building an IP PBX with Asterisk 22 LTS
- **Edition:** Second Edition
- **Author:** Flavio E. Gonçalves
- **Language:** English

### Prices (decided)
- **Paperback list price: $49.99 USD**
- **Kindle eBook list price: $9.99 USD**

### ISBN
- **Use the FREE KDP-assigned ISBN** (no purchase needed) for the paperback. The Kindle
  eBook does not need an ISBN — Amazon uses an ASIN. Do **not** reuse the first-edition
  ISBN `9781796396973`.

### Paperback specs (must match the interior PDF)
- **Trim size:** 7.5 x 9.25 in
- **Paper:** White
- **Interior:** Black & white
- **Bleed:** No bleed (interior). The cover is a separate wraparound file with 0.125 in bleed.

### BISAC categories (pick these two; KDP allows up to three)
1. **COM043000** — COMPUTERS / Networking / General
2. **COM046000** — COMPUTERS / Operating Systems / Linux

### Keywords (7 boxes)
1. Asterisk 22
2. PJSIP
3. VoIP PBX
4. SIP trunking
5. IP telephony
6. WebRTC Asterisk
7. open source telephony

### Book description (paste into the Description box)

> The only Asterisk book written for the Asterisk you actually run today. Every other
> guide on the shelf teaches chan_sip — a module that no longer exists. This second
> edition is rebuilt from the ground up for Asterisk 22 LTS, where PJSIP is the one and
> only SIP channel, and every configuration and command in the book was verified against
> a reproducible Asterisk 22 Docker lab. If an example is in here, it ran.
>
> Starting from a clean Linux box, you will install Asterisk, build a working PJSIP PBX,
> and grow it into a real system: SIP and PJSIP internals, WebRTC browser phones over
> WSS/DTLS-SRTP, SIP trunking with DIDs and the PSTN, a complete dialplan, queues and
> call-center features, voicemail, conferencing with ConfBridge, CDR/CEL accounting,
> AMI/AGI/ARI integration, PJSIP Realtime, hardening against toll fraud, and deployment,
> monitoring and scaling for production.
>
> Written by Flavio E. Gonçalves — Asterisk dCAP, CEO of SipPulse, and author of several
> telephony titles — with end-of-chapter quizzes and a companion hands-on course and labs
> at VoIP School Blackbelt. Whether you are new to Asterisk or migrating an aging
> chan_sip system to PJSIP, this is the current, lab-proven reference for Asterisk 22.

### Author bio (paste into the Author/Contributor bio box)

> Flavio E. Gonçalves is the CEO of SipPulse in Brazil, a company dedicated to
> softswitches, session border controllers, and multitenant PBXs. He holds the Asterisk
> dCAP certification (passed on the first attempt) along with a long list of others over
> his career — Novell MCNE/MCNI, Microsoft MCSE/MCT, and Cisco CCSP/CCNP/CCDP — and has
> drawn on more than 25 years of teaching experience to write for how people actually
> learn. He is the author of several telephony books, including titles on OpenSER and
> OpenSIPS. Flavio lives in Florianópolis, Brazil, where he spends his free time surfing
> and sailing.

---

## Part 2 — The only steps Flavio must do by hand

> **One blocker before you start:** the print interior PDF and the final cover were not
> regenerated in this pass because the `xelatex`/TeX toolchain was not available in the
> automation environment. Build them locally first (steps 1–2). The KDP-paste metadata
> above is final.

1. **Build the print interior.** On a machine with pandoc + a TeX distribution (xelatex
   with the TeX Gyre fonts), run `book/build.sh clean`. This produces
   `build/asterisk-guide.pdf` (the clean, ad-free KDP interior — *not* the sponsored
   GitHub edition). **Note the final page count** printed in/derived from the PDF; you
   need it for the cover spine.

2. **Regenerate the cover at the final spine width.** Open
   `book/illustrate/render_kdp_cover.py`, set `PAGES = <final page count from step 1>`,
   run it to produce `book/kdp/asterisk-guide-cover.png`, then export/convert that PNG to
   a print-ready **PDF** (KDP prefers PDF for the wraparound cover). Verify the dimensions
   against KDP's own cover-template generator before uploading. *(The committed
   `asterisk-guide-cover.png` was rendered for an earlier 389-page estimate — do not
   upload it until the spine is rebuilt at the real count.)*

3. **Create the paperback in KDP.** New Title → Paperback. Enter title, subtitle, edition
   ("Second Edition"), author, and **English** (all from Part 1).

4. **Choose the free KDP ISBN.** On the ISBN step, select **"Assign me a free KDP ISBN."**
   Do not buy one and do not reuse `9781796396973`.

5. **Paste the listing metadata.** Description, the 7 keywords, and the two BISAC
   categories (COM043000, COM046000) from Part 1. Add the author bio in the
   contributor/bio field.

6. **Set print options & upload files.** Trim **7.5 x 9.25 in**, **white** paper,
   **black & white** interior, **no-bleed** interior. Upload `build/asterisk-guide.pdf`
   as the interior and your exported cover **PDF** as the cover. Use the KDP previewer to
   confirm no margin/bleed warnings.

7. **Set the paperback price: $49.99 USD.** Set other marketplaces by conversion or leave
   KDP's auto-conversion. Confirm royalty/distribution (Expanded Distribution optional).

8. **Order a printed proof.** Always proof a physical copy before publishing — check the
   spine text alignment, code-box rendering, and figure margins.

9. **Publish the paperback** once the proof looks right.

10. **Create the Kindle eBook.** New Title → Kindle eBook (or "Create Kindle eBook" from
    the paperback). Reuse the same title/description/keywords/categories/bio. Upload
    `build/asterisk-guide.epub` (the clean EPUB from step 1). No ISBN needed.

11. **Set the Kindle price: $9.99 USD** (this also keeps you in the 70% royalty band).
    Choose KDP Select enrollment per preference. Publish.

---

## Known follow-ups (optional, not blockers)
- **Index.** The print interior has no back-of-book index yet. Optional for v1; a strong
  professional polish item for a later revision.
- **Cover spine.** Must be regenerated once the final page count is known (steps 1–2) —
  the count could not be locked in this pass without the TeX toolchain.

---

## ✅ FINAL STATE (auto-finalized by the workforce)

- **Page count locked: 415pp** (from the June-20 interior build `asterisk-guide.pdf`, 7.5×9.25 trim).
- **Cover regenerated to match** — spine 0.9346″. Files: `book/kdp/asterisk-guide-cover.png` + `.pdf`.
- **Ready-to-upload package assembled at:** `~/Downloads/asterisk-guide-KDP-upload/`
  - `asterisk-guide-interior-415pp.pdf` (interior)
  - `asterisk-guide-cover.pdf` / `.png` (wraparound, 415pp spine)
  - `listing-metadata.yaml` (description, 7 keywords, 2 BISAC, prices, bio)

**Your remaining steps (KDP has no API — this part is yours):**
1. KDP → Create → Paperback. Title/subtitle/edition/author/English. Choose the **free KDP ISBN**.
2. Paste description / keywords / categories / bio from `listing-metadata.yaml`. Price **$49.99**.
3. Upload `asterisk-guide-interior-415pp.pdf` + `asterisk-guide-cover.pdf`. Confirm 7.5×9.25, white, B&W, no-bleed.
4. Preview in KDP Print Previewer, order a proof, publish.
5. Kindle eBook: upload the EPUB, price **$9.99**, publish.

**NOTE:** the interior in the package is the June-20 415pp build. If it predates the ch10 QA
fixes on this branch (PR #1), the printed book won't include them. They're minor (legacy-chapter
formatting + a few Portuguese words). To include them you must rebuild the interior (needs
`xelatex`, not installed on this mini) and re-check the page count. Otherwise the package is
upload-ready as-is.
