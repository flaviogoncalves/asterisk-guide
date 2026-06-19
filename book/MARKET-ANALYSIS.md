# Market Analysis — *Asterisk Guide* (2nd Edition)

**An adversarial competitive evaluation of the Asterisk book market**

*Prepared 2026-06-19. THIS BOOK = "Asterisk Guide" (2nd edition) by Flavio E. Gonçalves — Asterisk 22 LTS, PJSIP-first, every example lab-verified against a reproducible Asterisk 22 Docker lab, CI/CD-built PDF/EPUB.*

This is a tough internal review, not marketing copy. The point is to find every place a competitor beats this book and fix it before print.

---

## 1. The competitive landscape

The defining fact of this market is that **it is old**. The genre peaked between 2005 and 2011. Almost every commercially significant Asterisk book predates `chan_pjsip` (introduced in Asterisk 12, late 2013) and the entire WebRTC/ARI era. The market leader is six years stale and still teaches against an Asterisk LTS that is itself end-of-life.

### The reigning champion

**Asterisk: The Definitive Guide, 5th Edition**
- Authors: Jim Van Meggelen, Russell Bryant, Leif Madsen (O'Reilly Media)
- Published: **July 2019** · 412 pages · 23 chapters
- Asterisk version: **16** (an LTS that reached End-of-Life around 2023)
- Format: print, ebook, O'Reilly Learning platform
- Relevance: **Still the default recommendation.** Strong reputation (Russell Bryant is a former Asterisk project lead; the lineage goes back to *Asterisk: The Future of Telephony*). It *does* have chapters on ARI, WebRTC, AGI, AMI, security, and certificates — which is why it remains hard to beat on breadth and authority. But it is six years old, targets an EOL version, and was written before PJSIP became the unquestioned default. Its SIP/device material straddles the chan_sip-to-PJSIP transition rather than committing to PJSIP.
- Sources: O'Reilly catalog page <https://www.oreilly.com/library/view/asterisk-the-definitive/9781492031598/> · Amazon <https://www.amazon.com/Asterisk-Definitive-Guide-Future-Telephony/dp/1492031607> · ebooks.com <https://www.ebooks.com/en-us/book/209723278/asterisk-the-definitive-guide/jim-van-meggelen/>

### The earlier O'Reilly lineage (now historical)

**Asterisk: The Future of Telephony, 2nd Edition** — O'Reilly, August 2007, Asterisk **1.4**. The book that defined the genre. Long superseded by the *Definitive Guide* line. Source: <https://www.oreilly.com/library/view/asterisk-the-future/9780596510480>

**Asterisk Cookbook** — Leif Madsen & Russell Bryant, O'Reilly, 2011, Asterisk **1.8**. A recipe-style companion. Useful patterns, but pre-PJSIP and out of print mindshare. Sources: <https://www.oreilly.com/library/view/asterisk-cookbook/9781449306793/> · <https://freecomputerbooks.com/asterisk-cookbook.html>

### The Packt catalog (mostly 2005–2011, all pre-PJSIP)

**Building Telephony Systems with Asterisk** — David Gomillion & Barrie Dempster, Packt, 2005. Asterisk 1.x (Zaptel-era; the install chapter literally covers installing Zaptel). Of historical interest only. Sources: <https://subscription.packtpub.com/book/networking-and-servers/9781904811152/1> · <https://www.amazon.com/Building-Telephony-Systems-Asterisk-Gomillion/dp/1904811159>

**Asterisk 1.6** — Packt, 2009. Install/configure/build-a-PBX walkthrough for Asterisk **1.6**. Sources: <https://www.packtpub.com/en-us/product/asterisk-16-9781847198624>

**Asterisk Gateway Interface 1.4 and 1.6 Programming** — Nir Simionovich, Packt, 2009, ~220 pages. Niche, AGI/PHP-PHPAGI focused, Asterisk 1.4/1.6. The only dedicated AGI book, but the AGI API it teaches is dated and the language tooling (PHPAGI) is largely abandoned. Source: <https://www.amazon.com/Asterisk-Gateway-Interface-1-4-Programming/dp/184719446X>

> Note: there is **no** Packt title literally called "Mastering Asterisk." The brief's working list assumed one; it does not exist in the catalog. Packt's Asterisk line effectively stops around 2011.

### The author's own back-catalog (the brand asset to leverage and to escape)

Flavio E. Gonçalves has a long publishing track record in this exact niche, which is both reputation capital and a reminder of how stale the field is:
- **Configuration Guide for Asterisk PBX** — BookSurge (the spiritual 1st edition / direct predecessor of THIS book).
- **Building Telephony Systems with OpenSER** — Packt.
- **Building Telephony Systems with OpenSIPS 1.6** — Packt, 2010 (later a 2nd edition with Bogdan-Andrei Iancu, OpenSIPS).
- Source: Goodreads author page <https://www.goodreads.com/author/show/1075604.Flavio_E_Gon_alves> · <https://www.amazon.com/Building-Telephony-Systems-OpenSIPS-1-6/dp/1849510741>

### The 2020s gap

A targeted search for any Asterisk book covering **18 / 20 / 21 / 22** returns **nothing of substance** — no commercially published, current-version Asterisk book exists. The only 2024-era technical writing on PJSIP+WebRTC in Asterisk is academic/blog material (e.g., a 2024 conference paper "WebRTC and PJSIP in Asterisk" <https://users.utcluj.ro/~dobrota/ATN_1_2024_5.pdf>) and the official docs at docs.asterisk.org. **The book-length, current-version slot is empty.**

Context facts that frame the whole market (all verified):
- Asterisk **22 LTS** released **2024-10-16**, full support to ~2028. Source: <https://www.sinologic.net/2024-10/asterisk-22-nueva-version-lts-con-la-eliminacion-definitiva-de-chan_sip.html> · <https://docs.asterisk.org/About-the-Project/Asterisk-Versions/>
- `chan_sip` was disabled-by-default/deprecated in **Asterisk 21** and **fully removed in Asterisk 22**. Source: <https://www.asterisk.org/asterisk-21-module-removal-chan_sip/>
- Asterisk **16** (the Definitive Guide's target) and **18** are both EOL; **21** is security-fix-only until Oct 2026. Source: <https://www.asterisk.org/asterisk-18-now-end-of-life-asterisk-21-security-fix-only/>

**Takeaway:** the entire competitive set teaches `chan_sip` as a first-class citizen — a module that no longer exists in current Asterisk. THIS book's PJSIP-first, Asterisk-22 stance is its single biggest structural advantage.

---

## 2. Comparison table

| Book | Year | Asterisk ver. | PJSIP coverage | WebRTC | ARI | Lab-verified | Free / open source | Last updated | Quizzes / training tie-in |
|---|---|---|---|---|---|---|---|---|---|
| **Asterisk Guide, 2nd ed. (THIS)** | 2026 | **22 LTS** | **First-class (chan_sip removed)** | **Yes (dedicated ch.)** | Yes (in AMI/AGI/ARI ch.) | **Yes — every example, Docker A22 lab** | **Yes — MD + lab, CC BY-NC-SA** | **2026** | **Yes — 10-Q quizzes/ch + VoIP School Blackbelt** |
| Asterisk: The Definitive Guide, 5th ed. | 2019 | 16 | Partial / transitional | Yes | Yes | No | No | 2019 | No |
| Asterisk: The Future of Telephony, 2nd ed. | 2007 | 1.4 | No (pre-PJSIP) | No | No | No | Read-free online | 2007 | No |
| Asterisk Cookbook | 2011 | 1.8 | No | No | No | No | No | 2011 | No |
| Building Telephony Systems w/ Asterisk | 2005 | 1.x (Zaptel) | No | No | No | No | No | 2005 | No |
| Asterisk 1.6 (Packt) | 2009 | 1.6 | No | No | No | No | No | 2009 | No |
| Asterisk Gateway Interface 1.4/1.6 | 2009 | 1.4/1.6 | No | No | No | No | No | 2009 | No |
| Configuration Guide for Asterisk PBX (1st ed.) | ~2000s | 1.x | No | No | No | No | No | (legacy) | Course tie-in (legacy) |

**The table tells the story:** on *version currency, PJSIP-first design, lab verification, openness, and training tie-in*, THIS book is alone in the right-hand columns. On *breadth and reputation*, the Definitive Guide still wins.

---

## 3. Adversarial critique — where competitors beat this book, and where it's weak

Being honest: "newest and lab-verified" is necessary but not sufficient. Here is where THIS book can lose to a six-year-old competitor, and where it has real holes.

### Where the Definitive Guide (5th ed.) is genuinely stronger

1. **Reference completeness & breadth.** 23 chapters / 412 pages vs. 16 chapters. The Definitive Guide carries dedicated chapters this book folds in or omits: **Voicemail**, **Internationalization**, **Device States/BLF**, **the Automated Attendant (IVR)**, **Interactive Voice Response** as its own topic, and **Certificates for Endpoint Security** as a standalone chapter. A reader doing a real deployment will hit all of these. If they aren't first-class here, the competitor remains the "complete" book.
2. **ARI / Stasis depth.** The Definitive Guide gives ARI its **own** chapter. THIS book bundles AMI+AGI+ARI into a single chapter (#13). ARI/Stasis is *the* modern way to build call applications (it's how voicebots, custom IVRs, and click-to-call backends are built). One-third of a shared chapter is not enough to beat a dedicated treatment, and it's the most future-facing API in Asterisk.
3. **Author authority signal.** Russell Bryant was an Asterisk project lead; Leif Madsen and Jim Van Meggelen are community institutions. That O'Reilly + core-team pedigree is a trust moat. THIS book counters with the author's own long track record and the lab, but must *show* its authority (citations, fact-check ledgers) to match it.
4. **Editorial polish.** O'Reilly copyediting, technical review, and indexing set a bar. A self/KDP-published book has to consciously match it (index, consistent terminology, professional figures) or it will read as "lesser" regardless of being more current.

### Where the older Packt/AGI books still have something

5. **AGI programming depth.** The dedicated AGI book goes deeper on writing AGI scripts than a section in a shared chapter will. Niche, but for the AGI reader it matters.

### Genuine gaps in THIS book (topics largely absent from the whole market AND from this TOC)

6. **FreePBX / GUI reality.** The overwhelming majority of production Asterisk installs run **FreePBX**. *No* book in the market covers the modern FreePBX/Sangoma stack well, and THIS book is pure CLI/config-file. That's pedagogically pure but commercially blind: many buyers want to understand the GUI they actually operate, or how hand-written dialplan coexists with FreePBX-generated config.
7. **High availability / clustering.** No HA, no active-passive failover, no DB replication patterns, no `res_pjsip` behind a load balancer. Production VoIP lives and dies on this. Absent from the market — a gap THIS book could *own*.
8. **Session Border Controllers (SBC) & topology.** Real deployments front Asterisk with an SBC (Kamailio/OpenSIPS/commercial). Given the author literally wrote the OpenSIPS book, **not** having a "where Asterisk sits behind an SBC" chapter is a missed, uniquely-credible opportunity.
9. **AI / voicebots / STT-TTS.** This is the #1 reason people open Asterisk in 2026. ARI + external media + real-time STT/TTS (and now `ARI external media` / audio-socket patterns to LLMs) is the hot topic. **Every** competing book predates it entirely. If THIS book ships without it, it leaves its single biggest differentiator on the table.
10. **Observability.** No Prometheus/Grafana, no structured logging, no `res_prometheus`-style metrics, no SIPp-driven load testing chapter (despite SIPp already being in the lab). Modern ops readers expect this.
11. **Containers/Kubernetes at depth.** The book installs via Docker (good) but "run Asterisk in production on Kubernetes" (stateful SIP, host networking, RTP port ranges, SDP/NAT in pods) is unaddressed and is a frequent real-world pain point.
12. **Fax / T.38** and **video calling** beyond WebRTC. Thin or absent. Fax-over-IP is still a paying enterprise need; T.38 is finicky and under-documented anywhere.
13. **Voicemail & IVR as first-class topics.** Folded into "PBX features" / not obviously present. Competitors give them chapters. New readers expect them.
14. **A concrete `chan_sip` → `pjsip.conf` migration cookbook.** The book reframes chan_sip as legacy (correct), but the highest-value, most-searched task for the *existing* installed base is "I have a working `sip.conf`, translate it." A side-by-side migration appendix would convert the entire legacy audience.

### Honest summary of the matchup

THIS book wins **currency, correctness-by-construction (the lab), PJSIP-first clarity, pedagogy (quizzes/fact-checks), and openness/funnel.** It currently loses on **breadth, ARI depth, reference completeness, and several production-grade topics (HA, SBC, observability, AI)**. The Definitive Guide is beatable *because it is stale* — but only if THIS book closes the breadth/ARI gap rather than just being newer.

---

## 4. The market gap this book uniquely fills

1. **The only current-version Asterisk book.** Every competitor targets 1.4–16; `chan_sip` (which they all teach) is *gone* in 22. THIS book is the only one a reader can follow command-for-command on a fresh install today without hitting "that module doesn't exist."
2. **PJSIP-first, not PJSIP-bolted-on.** Competitors treat PJSIP as the new option alongside chan_sip. THIS book makes it *the* model — matching how Asterisk 22 actually works.
3. **Correctness by construction.** No competing Asterisk book is **lab-verified against a reproducible environment with CI**. "Every example was run against real Asterisk 22 and the output captured" is a claim no other Asterisk book can make, and it directly attacks the #1 reader complaint about technical books (examples that don't work).
4. **Open + sponsor-supported + training funnel.** Free MD/EPUB/PDF under CC BY-NC-SA with the lab, monetized via print + VoIP School Blackbelt. No competitor has this model; it maximizes reach (and SEO/AI-citation surface) while still monetizing.
5. **Pedagogy.** Per-chapter 10-question quizzes, fact-check ledgers, modern flat figures, and a course companion. The market has *zero* books built for structured/self-paced learning with assessment.

**Positioning line:** *"The only Asterisk book written for the Asterisk you actually run today — PJSIP-first, every example proven against a live Asterisk 22 lab."*

---

## 5. Concrete suggestions to make this the best book on the market

Prioritized. P0 = needed to credibly claim "best"; P1 = strong differentiators; P2 = polish/upside.

### P0 — Close the gaps that let a stale competitor still win

1. **Promote ARI/Stasis to its own chapter (split #13).** Make AMI/AGI one chapter and **ARI + Stasis applications** another. Include a worked Stasis app (e.g., a click-to-call or custom IVR) end-to-end, lab-verified. This neutralizes the Definitive Guide's strongest modern chapter. *(Highest leverage single change.)*
2. **Add a `chan_sip → pjsip.conf` migration cookbook (appendix or boxed sections).** Side-by-side `sip.conf` → `pjsip.conf` for the common cases (endpoint, trunk, NAT, registration, codecs). This converts the *entire installed base* of legacy users — the largest, most motivated audience — and no competitor has it.
3. **Make Voicemail and IVR/Auto-Attendant unmistakably first-class.** Ensure each has a clear, indexed home (within PBX features is fine, but signposted). Buyers comparing TOCs against the Definitive Guide must not see them "missing."
4. **Ship a real index, glossary, and consistent terminology pass.** This is what makes a KDP book read as *professional* next to O'Reilly. The CONTEXT.md glossary already exists — surface it.
5. **Add an SBC / topology chapter (or strong appendix): "Asterisk behind an SBC."** Leverage the author's OpenSIPS authority. Show Asterisk fronted by OpenSIPS/Kamailio, why, and the PJSIP config that makes it work. Uniquely credible for this author; absent everywhere else.

### P1 — Differentiators that make it the *best*, not just the newest

6. **AI / voicebots chapter: ARI external media + STT/TTS (and LLM hookup).** Audio-socket / external-media → streaming STT → LLM → TTS back into the call. This is the most-searched 2026 Asterisk topic and **no book covers it.** Even one solid lab-verified pipeline (e.g., with an open STT/TTS) makes this *the* reference. Pairs naturally with the author's own SipPulse/aitrunk voicebot work.
7. **High Availability & scaling chapter.** Active/passive failover, shared Realtime DB, RTP/media considerations, registration persistence, and what "scale Asterisk horizontally" really means (hint: SBC distributes; Asterisk nodes are stateful). Owns a gap the whole market ignores.
8. **Observability section in the Deployment chapter.** Prometheus metrics, Grafana dashboards, structured/JSON logging, and **SIPp load testing** (SIPp is already in the lab — turn it into a teaching asset: "prove your PBX handles N cps"). Modern ops readers expect this and it reinforces the "verified" brand.
9. **Containers/K8s production realities.** Extend the Docker material with the hard parts: RTP port ranges, host vs. bridge networking, NAT/SDP in orchestration, stateful-set patterns. A short, honest "here be dragons" treatment beats the silence everywhere else.
10. **Security/TLS depth to match (and beat) the Definitive Guide's dedicated certificates chapter.** Ensure the Security chapter covers: PJSIP TLS/SRTP end-to-end with cert issuance (Let's Encrypt), fail2ban/`res_security_log`, `AMI`/ARI hardening, toll-fraud dialplan defenses, and a hardening checklist. This is table stakes for "best."
11. **Fax/T.38 and video beyond WebRTC.** At least a focused section: `res_fax`/T.38 gotchas and a working config; video call setup with PJSIP. Small page count, disproportionate "completeness" credit.

### P2 — Pedagogy & positioning polish

12. **Per-chapter "Lab" capstones tied to the Docker lab.** Each chapter ends with a hands-on lab the reader runs in the same environment the book was verified in — make the verification advantage *visible* to the reader, not just a backstage claim.
13. **Surface the fact-check ledgers in the book** (e.g., end-of-chapter "Verified against Asterisk 22.x" notes with doc links). Turn the rigor into a trust signal that directly answers the Definitive Guide's authority moat.
14. **Lead every relevant chapter with a "What changed since chan_sip" callout.** Speaks straight to the reader migrating from older books/installs and reinforces the only-current-book position.
15. **A migration/comparison preface: "If you learned Asterisk from the Definitive Guide / The Future of Telephony, start here."** Explicitly capture the audience of the dominant-but-stale competitor.
16. **Keep figures modern and consistent (flat, B/W, KDP-safe).** Already in progress — finish it; mismatched/dated diagrams are the fastest way a self-published book reads as second-tier.
17. **Exploit openness for distribution/AI-citation.** The free MD/HTML should be structured so AI search engines and Google cite *this* book for "Asterisk 22 / PJSIP" queries — since every competitor is paywalled and stale, THIS book can become the canonical web answer and feed the print/Blackbelt funnel.

### The one-sentence strategy

Be the **PJSIP-first, lab-verified, current** book (already won) **and** match the Definitive Guide on breadth by adding the four chapters the market never had — **dedicated ARI/Stasis, AI voicebots, HA/scaling, and SBC topology** — plus a chan_sip→PJSIP migration cookbook. Newest is the hook; *complete + verified + AI-ready* is what makes it the best.

---

### Sources

- Asterisk: The Definitive Guide, 5th ed. — <https://www.oreilly.com/library/view/asterisk-the-definitive/9781492031598/>, <https://www.amazon.com/Asterisk-Definitive-Guide-Future-Telephony/dp/1492031607>, <https://www.ebooks.com/en-us/book/209723278/asterisk-the-definitive-guide/jim-van-meggelen/>
- Asterisk: The Future of Telephony, 2nd ed. — <https://www.oreilly.com/library/view/asterisk-the-future/9780596510480>
- Asterisk Cookbook — <https://www.oreilly.com/library/view/asterisk-cookbook/9781449306793/>, <https://freecomputerbooks.com/asterisk-cookbook.html>
- Building Telephony Systems with Asterisk (Packt) — <https://subscription.packtpub.com/book/networking-and-servers/9781904811152/1>, <https://www.amazon.com/Building-Telephony-Systems-Asterisk-Gomillion/dp/1904811159>
- Asterisk 1.6 (Packt) — <https://www.packtpub.com/en-us/product/asterisk-16-9781847198624>
- Asterisk Gateway Interface 1.4 and 1.6 Programming (Simionovich, Packt) — <https://www.amazon.com/Asterisk-Gateway-Interface-1-4-Programming/dp/184719446X>
- Flavio E. Gonçalves back-catalog — <https://www.goodreads.com/author/show/1075604.Flavio_E_Gon_alves>, <https://www.amazon.com/Building-Telephony-Systems-OpenSIPS-1-6/dp/1849510741>
- Asterisk 22 LTS / chan_sip removal — <https://www.sinologic.net/2024-10/asterisk-22-nueva-version-lts-con-la-eliminacion-definitiva-de-chan_sip.html>, <https://www.asterisk.org/asterisk-21-module-removal-chan_sip/>, <https://docs.asterisk.org/About-the-Project/Asterisk-Versions/>
- Asterisk version lifecycle / EOL — <https://www.asterisk.org/asterisk-18-now-end-of-life-asterisk-21-security-fix-only/>
- 2024 academic paper on WebRTC + PJSIP in Asterisk — <https://users.utcluj.ro/~dobrota/ATN_1_2024_5.pdf>
