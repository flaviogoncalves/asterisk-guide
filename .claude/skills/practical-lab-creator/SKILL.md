# Practical Lab Creator

Design and write **hands-on lab exercises** for *Asterisk Guide* that a student can follow
**step by step, start to finish, on their own machine** — Windows, macOS, or Linux — using
only the project's reproducible **Docker lab**. The output is a self-contained lab that a
beginner can complete without guessing, without buying hardware, and without touching legacy
code paths.

The labs live in the standalone **`labs/LAB-GUIDE.md`** (a separate deliverable from the book
chapters). Each lab you write is appended/edited there, and every command in it is **verified
against the running lab** before you commit.

## Hard constraints (non-negotiable)

1. **Docker only, cross-platform.** Everything runs in the `lab/` Docker environment. Give the
   exact command for **all three platforms** wherever they differ (PowerShell vs. Terminal vs.
   shell, path separators, `docker compose` invocation). Never assume a Linux-only tool.
2. **No hardware. Ever.** No analog cards (DAHDI/`chan_dahdi`), no FXO/FXS, no PSTN gateways,
   no physical phones required. A softphone (the SipPulse Softphone) or a browser is the only
   endpoint a student needs.
3. **No legacy.** Pure PJSIP. Never `chan_sip`, `sip.conf`, `SIP/…`, `sip show …`, `Macro()`,
   or MeetMe. Asterisk 22 terminology only (`pjsip.conf`, `PJSIP/…`, `pjsip show …`, `GoSub`,
   `ConfBridge`).
4. **Credentials live on page one.** Every username, password, extension, host, and port a
   student needs across ALL labs is collected in the **Lab Credentials** table at the very top
   of `LAB-GUIDE.md` — never scattered or invented mid-lab. The shared SIP trunk is
   **`sip.flagonc.com`**, accounts **`1001`–`1020`**, password **`#supersecret#`**. The lab
   softphone accounts are `6001`/`6002` (passwords in the base `pjsip.conf`) and `webrtc-1000`.
5. **Never fabricate output.** Every command block's "expected output" must be **really
   captured** from the running lab. If you cannot run it (e.g. a live trunk call that depends on
   an account being provisioned), say so plainly and describe the *correct expected state*
   (`Registered`, a `200 OK`) without pasting an invented capture — and add a Troubleshooting
   entry for the failure modes.

## The lab template (use this exact shape for every lab)

````
## Lab N — <imperative title> 

> **You will:** one sentence on the skill gained.
> **Time:** ~NN min   **Prerequisites:** Lab 0 (lab running); Lab K if it builds on one.

### Objective
2–4 sentences: what the student builds and why it matters in the real world.

### Step 1 — <action>
Plain-language instruction, then the exact command(s) in a fenced block. Tell the student
*where* to run it (host shell vs. Asterisk CLI vs. inside the container) every time.

```bash
# on your computer (Terminal / PowerShell), from the repo root
docker compose -f lab/docker-compose.yml exec asterisk asterisk -rx 'pjsip show endpoints'
```

**You should see:** then a REAL captured block, trimmed to the relevant lines.

### Step 2 … (numbered, one idea each)

### ✅ Checkpoint
A concrete, observable result the student can confirm ("you hear your own voice",
"`Status` reads `Registered`", "the browser shows `Connected`"). If it fails, point to
Troubleshooting.

### Troubleshooting
| Symptom | Cause | Fix |
| … | … | … |

### Clean up
How to undo any config the lab added (revert the file, `module reload res_pjsip.so`), so the
next lab starts from the known base state.
````

## Procedure for authoring one lab

Do these in order. One lab end-to-end, then report.

1. **Boot/confirm the lab.** `./lab/lab.sh up` (or `docker compose -f lab/docker-compose.yml up
   -d`). Confirm health: `docker compose -f lab/docker-compose.yml exec asterisk asterisk -rx
   'core show version'`.
2. **Decide what the student edits.** The base config under `lab/asterisk/etc/` is the known
   starting point. A lab teaches by having the student **add** config: a new dialplan context
   in `extensions.conf`, a new endpoint/auth/aor in `pjsip.conf`, or a **new file** (e.g.
   `voicemail.conf`, `queues.conf`, `ari.conf`) — the whole `etc/` dir is bind-mounted, so a
   host-created file appears in the container. Reload with the **narrowest** command that works
   (`dialplan reload`, `module reload res_pjsip.so`, `voicemail reload`, …).
3. **Write each step, then RUN it in the lab** exactly as written, copy-pasting your own
   instructions. Capture the real output and paste the relevant lines under "You should see".
   If a step doesn't behave as described, fix the step — never the expectation.
4. **Give the cross-platform form** for any host command that differs (softphone setup, opening
   a browser at `https://localhost:8089`, `python3 -m http.server`, file paths).
5. **Write the Checkpoint** as something the student can see/hear, not "it should work".
6. **Write Troubleshooting** from the failures you actually hit (wrong password → `401`,
   firewall, cert not trusted, `Unregistered`, NAT one-way audio).
7. **Write Clean up** so the lab is idempotent and the base state is restored.
8. **Verify the whole lab once more** from a clean base, top to bottom, as a student would.
9. **Update the Credentials table** on page one if the lab introduced any new account/port.
10. **Report**: the lab title, which commands were lab-verified (with the version string), any
    step that could not be fully run live and why.

## Style

- Address the student as **"you"**, imperative voice, short steps. Assume a capable beginner,
  not an Asterisk expert. Define a term the first time it appears.
- Every command is **copy-pasteable as-is** — no `<placeholders>` the student must mentally
  fill unless the line above tells them exactly what to substitute.
- Keep each lab to one clear objective. If it grows past ~8 steps, split it or move depth into a
  "Stretch" step at the end.
- Match the book's pedagogy and the `lab/` environment; cross-reference the relevant chapter by
  name (not page number).

## Guardrails

- One lab per run; verify against the live Asterisk 22 lab; report before moving on.
- No hardware, no legacy, no fabricated output, credentials on page one — restate the four hard
  constraints to yourself before writing.
- Never print or commit secrets beyond the shared lab credentials the user has authorized
  (`6001`/`6002` lab passwords, `webrtc-1000`, and the `sip.flagonc.com` `1001`–`1020` /
  `#supersecret#` trunk). TLS private keys stay gitignored.
- Commit as `git -c user.name='Flavio E. Gonçalves' -c user.email='flavio@sippulse.com'`, with
  the message ending `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
