# Modernization brief — READ FIRST (shared rules for every chapter)

You are updating *Asterisk Guide* (Flavio E. Gonçalves) from
**Asterisk 16 → Asterisk 22 LTS** for a 2nd edition. The author is a SIP/VoIP
expert who will review your work. **Accuracy beats completeness.**

## Hard facts (verified from docs.asterisk.org, do not contradict)

- **Asterisk 22** = current LTS (released 2024, full support → 2028-10-16). This is the target.
- Version lineage: 18 (EOL), 20 (LTS 2022), 21 (standard, security-fix-only), 22 (LTS 2024), 23 (standard 2025).
- **chan_sip was REMOVED in Asterisk 21 and does not exist in 22.** PJSIP is the only SIP channel.
- **app_macro (Macro())** was removed — use GoSub/GoSubIf. (This edition already migrated.)
- **AsteriskNOW** is discontinued. The modern turnkey distro is **FreePBX** (Sangoma).
- Digium was acquired by **Sangoma** (2018). Asterisk is now sponsored by Sangoma.
- Build flow is unchanged in shape: `./contrib/scripts/install_prereq install`,
  `./configure`, `make menuselect`, `make`, `make install`, `make samples`.
- `codec_opus` and `codec_silk`/g729 binary modules are now freely distributed by Sangoma.
- chan_iax2 still ships in 22 but is legacy; SIP/PJSIP is preferred.
- DAHDI still exists for analog/digital cards but is increasingly niche.

## Rules

1. **Preserve the author's voice, structure, and pedagogy.** Don't rewrite for style.
2. **Keep all Markdown structure**: heading levels, code fences, bullet lists,
   and `![...](../images/...)` figure references — do not delete figures.
3. **Make grounded edits only.** Update version numbers, removed/deprecated
   features, changed commands, install steps, and config syntax that you are
   confident about from the hard facts above or well-established Asterisk knowledge.
4. **When unsure, do NOT invent.** Insert an editor note instead:
   `> **[2nd-ed note]** <what to verify>` on its own line. These are for the author.
5. **chan_sip → PJSIP:** Where the book shows `sip.conf` config as the *primary*
   way to do something (Ch 3 especially), add the `pjsip.conf` equivalent and note
   chan_sip is removed in 21+. Do not silently delete chan_sip examples that are
   pedagogically referenced — mark them legacy.
6. **CLI commands:** verify channel-specific commands. e.g. `sip show peers` →
   `pjsip show endpoints`; `sip reload` → `module reload res_pjsip.so` / `pjsip reload`.
7. Don't touch front matter dates/ISBN — leave an editor note that they need updating
   for the 2nd edition.
8. Fix obvious OCR-era typos only if trivially certain (e.g. "Monolythic"→"Monolithic");
   otherwise leave the author's words.

## Output

Edit the chapter file **in place** (Edit/Write). Keep it valid Markdown.
At the very top of the file, leave the existing H1 untouched. Do not add a
changelog inside the file — your editor notes are the trail.
