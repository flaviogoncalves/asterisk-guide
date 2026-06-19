# Plan — Complete Asterisk Training, 2nd Edition

Living plan. Captures decisions from the planning interview and open questions.

## Locked decisions

1. **Deliverable:** a published 2nd edition (Amazon KDP / Udemy companion).
   Bar: every config/CLI example lab-verified against real Asterisk 22; production
   pipeline to print/ebook; new edition front matter + ISBN; all `[2nd-ed note]`
   markers resolved before ship.
2. **Target version:** Asterisk 22 LTS (support → 2028-10-16).
3. **chan_sip:** removed in Asterisk 21+. Reframed as legacy + a `sip.conf→pjsip.conf`
   migration guide. PJSIP is *the* SIP channel.
4. **Structure:** a bigger restructure (not 1:1). The 17 modernized first-pass files are
   *source material* to be reorganized into the TOC below.
5. **New chapters in scope:** WebRTC; SIP trunking/DID/PSTN; Deployment/monitoring/scaling;
   plus merge of SIP-theory (old ch8) + PJSIP (old ch9) into one chapter.

## Target TOC (draft — pending legacy-channels decision)

```
PART I — FOUNDATIONS
  1. Introduction to Asterisk (the Sangoma era)        ← ch1
  2. Installing Asterisk 22 (source + Docker)          ← ch2 + containers
  3. Building your first PBX with PJSIP                 ← ch3 (PJSIP-first)
PART II — CHANNELS & CONNECTIVITY
  4. SIP & PJSIP in depth                               ← ch8 + ch9 merged
  5. WebRTC with Asterisk                               ← NEW
  6. SIP trunking, DID & the PSTN                       ← NEW
  7. Legacy channels: analog, TDM & IAX2               ← ch4 + ch5 + ch7 (decision pending)
PART III — DIALPLAN & CALL FEATURES
  8. The dialplan: fundamentals to advanced            ← ch10
  9. PBX features (transfer, park, ConfBridge, VM)     ← ch11
 10. Queues & basic contact-center                     ← ch12
PART IV — INTEGRATION & OPERATIONS
 11. CDR & CEL                                          ← ch13
 12. AMI, AGI & ARI                                     ← ch14 (ARI expanded)
 13. Asterisk Realtime (ODBC + PJSIP Sorcery)          ← ch16
 14. Security & hardening                               ← ch15
 15. Deployment, monitoring & scaling                  ← NEW
```

## More locked decisions

6. **Legacy channels:** merge ch4+ch5+ch7 into one "Legacy channels" chapter (TOC slot 7).
7. **Lab-verification env:** a reproducible **Dockerized Asterisk 22 lab** on the Mac mini;
   doubles as the worked example in the install + Deployment chapters.
8. **Production pipeline:** **Pandoc → LaTeX book template → KDP 6×9 print PDF**, plus
   **Pandoc → EPUB** for Kindle. Single Markdown source of truth. (Evaluate the `make-pdf`
   skill for the PDF leg.) Author chapters in Pandoc-clean Markdown.
9. **Figures:** curate — convert CLI/terminal screenshots to monospace text blocks (captured
   live during lab verification), reshoot GUI/softphone shots using **SipPulse Softphone**
   (the author's own client — dogfooding/branding), keep/redraw conceptual diagrams.
   Test tooling: **SIPp** for headless/automated example verification; **SipPulse Softphone**
   for recorded video test calls and GUI screenshots.
10. **Companion:** **VoIP School Blackbelt Training** (the author's platform). Re-point all
    course references to it; the Docker lab + lab-verified configs are delivered as its
    companion lab. Defer video re-recording.
11. **GitHub discontinued:** remove ALL GitHub lab-guide references from the book; no public
    repo. Lab material is delivered through VoIP School Blackbelt, not GitHub.

12. **Branding:** consolidate the training funnel to **VoIP School Blackbelt**; strip dead
    Udemy/GitHub/asteriskguide course mentions; keep personal authorship. Exact URL/email TBD —
    use placeholders + `[2nd-ed note]` until provided.
13. **Positioning / openness:** the monetizable artifacts are the **paper book** and the
    **VoIP School Blackbelt training**. The Markdown source + Docker lab are commodity and may
    eventually be published as a **public GitHub repo** (marketing funnel). Design for clean
    publishability: no secrets, sane license, tidy history.

## Execution roadmap (lab-first, phased, checkpoint at each boundary)

- **Phase 1 — Lab: ✅ DONE.** Reproducible Docker Asterisk 22.10.0 lab (built from source),
  PJSIP endpoints + IP-identified SIPp endpoint; `lab.sh verify` places a real headless SIPp
  call to ext 9000 and asserts 200 OK (passing). Public repo + CI/CD pipeline (Phase 6's press)
  delivered early: https://github.com/flaviogoncalves/complete-asterisk-training builds
  PDF/EPUB/LaTeX on every push/PR (first build green: 355-page PDF).
- **Phase 2 — Restructure:** reorganize the 17 modernized files into the 15-chapter / 4-part
  TOC; perform the ch8+9 merge and the ch4+5+7 legacy merge. Renumber + fix cross-refs.
- **Phase 3 — Verify:** run every config/CLI example against the lab; capture real Asterisk 22
  output; convert CLI screenshots to text blocks; resolve technical `[2nd-ed note]` markers.
- **Phase 4 — New chapters:** draft WebRTC, SIP trunking/DID/PSTN, and Deployment/monitoring/
  scaling — each lab-verified.
- **Phase 5 — Polish:** reshoot GUI figures, redraw diagrams, branding sweep to VoIP School
  Blackbelt, front matter + new ISBN/edition.
- **Phase 6 — Produce:** Pandoc → LaTeX 6×9 print PDF + EPUB; proof; (optionally) publish the
  public source repo.

## Pending inputs from author (non-blocking)

- VoIP School Blackbelt canonical URL + contact email for the book.
- New ISBN + edition date for the 2nd edition.
- GUI screenshots reshoot (needs a human at a softphone) — or delegate to a tester.
