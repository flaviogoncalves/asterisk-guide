```{=latex}
\frontmatter
```

## Copyright {.unnumbered}

*Asterisk Guide* — Second Edition (Asterisk 22 LTS)

Copyright © 2006–2026 Flavio E. Gonçalves. All rights reserved.

No part of this book may be reproduced, stored in a retrieval system, or transmitted
in any form or by any means without the prior written consent of the author, except
for brief excerpts used in published reviews.

**Edition:** Second Edition.

A free ISBN is assigned by Amazon KDP at publication and will be printed here and on
the copyright page. (The first-edition ISBN 9781796396973 is not reused for this
second edition.)

Many of the designations used by manufacturers and sellers to distinguish their
products are claimed as trademarks. Where those designations appear in this book, and
the author was aware of a trademark claim, they have been printed in caps or initial
caps. Asterisk, Digium, IAX, and DUNDi are trademarks of Sangoma Technologies (Digium
was acquired by Sangoma in 2018; Asterisk is now sponsored by Sangoma).

While every precaution has been taken in preparing this book, the author assumes no
responsibility for errors or omissions, or for damages resulting from the use of the
information contained herein.

## Preface {.unnumbered}

This book is for anyone who wants to learn how to install and configure a PBX (Private
Branch Exchange) based on Asterisk 22 LTS. Asterisk is an open source telephony
platform that bridges VoIP and traditional TDM channels.

This is the fifth generation of a book that began life as the *Asterisk Configuration
Guide*. The material grew out of the work I did to prepare for the Digium dCAP
certification back in 2006 — which I passed on the first attempt — and it has been
taught to more than a thousand students since.

The open source PBX concept is revolutionary. For decades, telephony was dominated by
a handful of companies selling expensive proprietary systems. Asterisk put that power
back in the hands of users: features that were once economically out of reach — CTI
(computer-telephony integration), IVR (interactive voice response), ACD (automatic
call distribution), voicemail, and much more — are now available to anyone with a
Linux box and the willingness to learn.

This book will not turn you into a guru on its own — no book can — but by the end of
it you will be able to build and operate a real PBX with advanced features. The book
has a companion — hands-on labs and an online course — at **VoIP School Blackbelt**
(<https://voip.school>).

## Audience {.unnumbered}

This book is intended for readers who are new to Asterisk. I assume you are comfortable
with Linux — the shell, a text editor, and basic system administration. You can follow
along on a Linux desktop if that is easier while learning, and a virtual machine is
fine for the labs (expect slightly poorer voice quality). For production systems I do
not recommend running Asterisk on a desktop environment or inside a lightly-resourced
VM. Some familiarity with IP networks, Voice over IP (VoIP), and basic telephony
concepts will help.

## What's new in the second edition {.unnumbered}

The second edition is a thorough modernization for **Asterisk 22 LTS** (released 2024,
supported through October 2028). The headline changes:

- **PJSIP is the only SIP channel.** `chan_sip` was removed in Asterisk 21 and does not
  exist in 22. Every SIP example now uses PJSIP (`pjsip.conf`); the legacy `sip.conf`
  material is kept only as a migration reference.
- **Sangoma stewardship.** Digium was acquired by Sangoma in 2018; the project is now
  developed and sponsored by Sangoma, and the text reflects that throughout.
- **Three new chapters.** *WebRTC with Asterisk* (browser phones over WSS/DTLS-SRTP),
  *SIP trunking, DID & the PSTN*, and *Deployment, monitoring & scaling*.
- **A reproducible lab.** Every configuration and command in the book is verified
  against an Asterisk 22 Docker lab that you can run yourself.
- **Modernized features.** ConfBridge replaces the old MeetMe conferencing, ARI is
  introduced alongside AMI/AGI, PJSIP Realtime (Sorcery) is covered, and the install,
  security, and CDR chapters are brought up to date.
- **A new structure.** The book is now organized into four parts — Foundations,
  Channels & Connectivity, Dialplan & Call Features, and Integration & Operations.

## About the author {.unnumbered}

Flavio E. Gonçalves was born in 1966 in Brazil. He has had a strong interest in
computers since getting his first PC in 1983, and earned an engineering degree in 1989
with a focus on computer-aided design and manufacturing. He is the CEO of SipPulse in
Brazil, a company dedicated to softswitches, session border controllers, and
multitenant PBXs.

Over his career he has held a long list of certifications — Novell MCNE/MCNI, Microsoft
MCSE/MCT, Cisco CCSP/CCNP/CCDP, and Asterisk dCAP among them. He began writing about
open source software because he believes the structured way certifications once taught
their material is a great way to learn, and he has drawn on more than 25 years of
teaching experience to write for how people actually learn rather than purely from a
technical standpoint.

Flavio is a father of two and lives in Florianópolis, Brazil — one of the most
beautiful places in the world — where he spends his free time surfing and sailing.

## Feedback, credits & training {.unnumbered}

I try hard to find and eliminate errors, but some always slip through. If you find
something wrong, please let me know and I will act on it.

This book is also used as training material. If you would like to use it in your own
training center, or to take the companion online course and labs, visit **VoIP School
Blackbelt** at <https://voip.school> or email <flavio@voip.school>.

**Credits.** Cover work: Karla Braga. Reviewers: Luis F. Gonçalves, Guilherme Goes
(dCAP), and professional proofreaders. My thanks also to the many students whose
feedback over the years has shaped this material, and to my family for their support.

```{=latex}
\cleardoublepage
```
