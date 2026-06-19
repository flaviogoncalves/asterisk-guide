# Complete Asterisk™ Training

## A systematic guide to building an IP PBX using the

## most advanced open source IP telephony

## platform.

## Flavio E. Gonçalves

Published by V.Office Networks Complete Asterisk Trainingtm

![00-front-matter figure 1](../images/00-front-matter-img01.png)

Copyright © 2006-2019 V.Office Networks Ltda., All rights reserved All rights reserved. No part of this book may be reproduced, stored in a retrieval system, or transmitted in any form or by any means without prior written consent of the publisher. Exceptions are made for brief excerpts used in publish reviews. Printing History First Edition: February 2019, File Date: Saturday, February 09, 2019 ISBN: 9781796396973 File Date: Saturday, February 09, 2019 Some manufacturers claim trademarks for several designations that distinguish their products. Wherever those designations appear in this book and we are aware of them, the designation is printed in CAPS or the initials are capitalized. Although a great degree of care was used in writing this book, the author assumes no responsibility for errors and omissions, or damages resulting from the use of the information contained in this book. We have done the maximum effort to provide trademark information about all the companies and products mentioned in this book by the appropriate use of capitals. Asterisk, Digium, IAX and DUNDI trademarks are property of Digium Inc. Digium was acquired by Sangoma Technologies in 2018; Asterisk is now sponsored by Sangoma.

> **[2nd-ed note]** The copyright year range, edition line ("First Edition: February 2019"), and ISBN all need updating for the 2nd edition. Do not reuse ISBN 9781796396973 — a new ISBN is required for a new edition.

## Preface

This book is for anyone who wants to learn how to install and configure a PBX (Private Branch Exchange) based on Asterisk PBX 22 LTS. Asterisk is an open source telephony platform capable to use VoIP and TDM channels. This is the fifth generation of the book started as the Asterisk Configuration Guide. The material that I present in this book has helped me to prepare for the dCAP certification from Digium in May 2006 and to pass it in the first try. The Asterisk Open Source PBX concept is revolutionary. For many years, huge companies with proprietary systems have dominated telephony. Finally, users can recover their buying power by having access to an open telephony platform. Thus, things that were not possible before, because they were not economically viable are likely to start happening. Examples include resources such as CTI (computer telephony integration), IVR (interactive voice response), ACD (automatic call distribution), and voicemail, that are now available to everybody. I have not designed to teach every single detail of Asterisk. In fact, you will certainly not become a guru simply by reading this book. However, you will be able to build and configure a PBX with advanced features such as voicemail, IVR an ACD by the end of reading. I hope you enjoy as much learning about Asterisk as I have enjoyed writing about it. This book now has two companions; an online training on udemy (www.udemy.com) and a lab guide on github were I publish the examples and labs. More details ahead on this book including a coupon code.

> **[2nd-ed note]** "fourth generation" updated to "fifth generation" above — verify the edition count is correct before publishing.

## Audience

This book is intended for those who are new to Asterisk. We assume you are familiar with Linux, Linux shell commands and Linux text editors. You could test Asterisk using a Linux system with a graphical interface which may be easier for Linux newbies. Some users will try to execute Asterisk using virtualization and this is really not a problem, except for poorer voice quality. For production systems we do not encourage VMware or Linux with a graphical user interface. It is also desirable that the reader has some knowledge of IP networks, voice over IP (VoIP) and telephony concepts.

## Mistakes and errors in the e-Book

We always try to find and eliminate errors and mistakes. Please, if you find something wrong, give us feedback and we will act on it immediately. E-mail address for feedback: flavio@asteriskguide.com

## Use as a training material

We use this book for Asterisk training. If you are interested to use it in your training center, please send an e-mail to flavio@asteriskguide.com.

## Credits

Cover Work: Karla Braga Reviewers: Luis F. Goncalves, Guilherme Goes dCAP, Edit Avenue, professional proofreaders

## About the Author

Flavio E. Goncalves was born in 1966 in Brazil. Having always had a strong interest in computers, he got his first personal computer in 1983 and since then it has been almost an addiction. He received his degree in Engineering in 1989 with focus in the computer aided design and computer aided manufacturing. He is also, CEO of SipPulse in Brazil, a development company dedicated to soft switches, session border controllers and multitenant PBXs. Since 1993, he has participated in a series of certifications programs having being certificated as Novell MCNE/MCNI, Microsoft MCSE/MCT, Cisco CCSP/CCNP/CCDP, Asterisk dCAP and some others. He started writing about open source software, because, he thinks the way certification programs were organized in the past, were very good to help learners. Some books today are written by strictly technical people, who, sometimes, do not have a clear idea on how people learn. He tried to use his 25 year experience as instructor to help people learn open source telephony software. His experience with networks, protocol analyzers and IP telephony, combined with the teaching experience, give him an edge to write this book. As the CEO of SipPulse, Flavio E. Goncalves, balance his time between family, work and fun. He is a father of two children and lives in Florianopolis, Brazil, one of the most beautiful places in the world. He dedicates his free time in water sports such as surfing and sailing. Writing this book has been a process that involved many people. I would like to thank the staff at V.Office Networks in all the process of reviewing and editing the book. I would like to thank Guilherme Goes by the countless tips on Asterisk and the book itself. I would also like to thank several students, who took courses of Asterisk for their feedback, more than a thousand users have already taken classes using this material in the last five years. Finally, I would like to thank my family, for all the support they gave me during all these years. You can contact him at flavio@asteriskguide.com, or visit his website www.asteriskguide.com.

## Notes in version 10

In this version (v10 / 1st edition), we added some chapters and features described below:

### 1 – New name

I have renamed the book from Learning Guide for Asterisk to Complete Asterisk Training to match the online training with the same name. The new name is better in terms of SEO (Search Engine Optimization). The objective is to match a textbook, lab guide and online training in a single package.

### 2 – New chapter PJSIP, the new SIP channel

The Asterisk project deprecated chan_sip. Thus, I have written a new chapter about the new SIP channel based on the PJSIP stack. The new channel is quickly gaining ground to replace the old chan_sip. However, it is still a little trickier to setup, but some tools such as the converter from chan_sip to pjsip and PJSIP wizard can help with the task. In the security side, the random UDP port is a pain.

### 3 – Getting rid of MACROS

Macros are also deprecated and actually do not work on Asterisk 16, so we have to update all examples and labs replacing MACRO with GOSUB.

### 4 – MySQL replaced by ODBC

When I started this book in 2006, many things were not well defined and some things such as MySQL stayed. Last time I went to the Astricon, it was clear to me that ODBC (Open Database Connectivity Driver) is the preferred driver. It has support for connection pooling. Thus, I have replaced all examples with MySQL native drivers by ODBC. ODBC is also a pain to setup, but the advantage is connection pooling and the performance. A fact, if you are going to use Asterisk with a database you should be familiar with ODBC.

### 5 – Security

I have added a new chapter in security. To install Asterisk without proper security is so risky that is unacceptable. Any Asterisk professional should know how to configure IPTABLES and Fail2ban. Also added a section on TLS/SRTP.

### 6 – The Complete Asterisk Training on Udemy

This book has now a companion online training, the Complete Asterisk Training published on Udemy. To access the training with a discount coupon use the link below: https://www.udemy.com/building-a-complete-pbx-with-asterisk/?couponCode=CCSTRAT

### 7 – The LAB Guide for Asterisk

You do not need to be an enrolled online student to use our LAB guides. Lab guides are systematic instructions on how to setup a complete Asterisk PBX published on github. https://github.com/flaviogoncalves/AsteriskTraining/wiki

## What's new in the 2nd edition (Asterisk 22 LTS)

> **[2nd-ed note]** Author to expand this section into a full "What's new" narrative. The outline below captures the key changes that should be summarised here:
>
> - **chan_sip removed (Asterisk 21+):** chan_sip no longer ships in Asterisk 21 or 22. PJSIP (`res_pjsip`) is now the sole SIP channel driver. The legacy chan_sip chapter has been restructured accordingly; sip.conf examples are retained only as historical reference.
> - **Sangoma stewardship:** Digium was acquired by Sangoma Technologies in 2018. Asterisk is now developed and sponsored by Sangoma. References to Digium as the project steward have been updated throughout.
> - **ConfBridge replaces MeetMe:** `app_meetme` (which required DAHDI) is deprecated. `app_confbridge` is the modern conferencing application and does not require DAHDI hardware. All conference examples have been updated to ConfBridge.
> - **ARI (Asterisk REST Interface):** A new section introduces ARI as the preferred modern extension mechanism for external call control, complementing the existing AMI/AGI chapter.
> - **Updated installation:** Install instructions updated for Asterisk 22 LTS on a current Ubuntu/Debian LTS release. The `install_prereq` script and `make menuselect` flow are unchanged in shape but package names and defaults reflect Asterisk 22.
> - **Target version:** All CLI commands, configuration examples, and version references throughout the book target **Asterisk 22 LTS** (released 2024, full support through 2028-10-16).

## Summary

INTRODUCTION TO ASTERISK PBX Objectives What is Asterisk What is AsteriskNOW Role of Digium™ / Sangoma Why Asterisk? Main objections to Asterisk PBX Overview of an Asterisk system Comparing the old and the new world Building a test system Asterisk scenarios Finding information and help Summary HOW TO DOWNLOAD AND INSTALL ASTERISK Objectives Minimum Hardware Required Choosing a Linux distribution Installing Linux for Asterisk Installing dependencies BUILDING A SIMPLE PBX Installation Sequence Configuration of the extensions IAX Extensions Configuring the SIP devices Configuring the IAX devices Dial plan introduction The structure of the file extensions.conf Contexts Extensions Variables Expressions Functions Applications Building a dial plan ANALOG CHANNELS DIGITAL CHANNELS Objectives E1/T1 digital lines ISDN BRI Choosing a telephony card for your Asterisk server Using hardware echo cancellation Zaptel and DAHDI Asterisk telephony channels setup Troubleshooting Configuration options in chan_dahdi.conf MFC/R2 configuration How to use the driver libopenr2 MFC/R2 Configuration DAHDI channel format Questions DESIGNING A VOIP NETWORK THE IAX PROTOCOL Objectives IAX design Bandwidth usage Channel naming Using IAX IAX authentication The iax.conf file configuration Jitter buffer Frame tagging IAX2 Encryption IAX2 debug commands Summary Quiz THE SIP PROTOCOL (PJSIP) Objectives Theory of Operation SIP advanced scenarios Advanced configurations SIP authentication SIP NAT Traversal SIP limitations SIP dial strings PJSIP CLI commands Quiz THE SIP CHANNEL PJSIP Objectives Why to use PJSIP PJSIP modules PJSIP configuration Relationship between entities Configuring a Softphone Configuring a SIP trunk Nat traversal on res_pjsip Channel Naming Migration from chan_sip to res_pjsip PJSIP configuration wizard Console commands Summary DIAL PLAN ADVANCED FEATURES Objectives Simplifying your Dial Plan Dial Plan Security Receiving calls using an IVR menu. Context inclusion Using the switch statement Dial plan processing order The #INCLUDE statement Subroutines with GOSUB Using Asterisk DB Using a blacklist Time-based contexts Time-based messages using gotoiftime() Using DISA to get a new dial tone Limit simultaneous calls Voicemail Using the Voicemailmain() application Sending voicemail to e-mail Voicemail Web interface Voicemail notification Using the directory application Lab: Putting it all together Summary Quiz USING PBX FEATURES Call Transfer Call parking Call pickup Conference (call conference) ConfBridge Call Recording Application Maps Quiz CALL QUEUES Objectives How queues work? Queues Agents ACD-related applications Configuration tasks Queue operation Advanced resources The application agentcallbacklogin() is deprecated Queue statistics Summary Quiz ASTERISK CALL DETAIL RECORDS Account codes and automated message accounting Changing the CSV and/or CDR format CDR Storage Installing and configuring ODBC on Ubuntu Applications and functions User authentication Using passwords from voicemail Summary EXTENDING ASTERISK WITH AMI, AGI AND ARI Objectives Major ways to extend Asterisk Extending Asterisk with console CLI Extending Asterisk using the System() application What is AMI? Configuring users and permissions Asterisk Gateway Interface Asterisk REST Interface (ARI) Changing the source code Summary Quiz ASTERISK SECURITY Objectives Main attacks to IP telephony Security policy for Asterisk Enabling two way authentication for international calls Summary Quiz ASTERISK REAL-TIME Objectives How does Asterisk Real Time work? Configuring Asterisk Real Time Database configuration Lab: Installing and creating the database tables Lab: Configuring and testing ARA Summary Quiz

> **[2nd-ed note]** The Table of Contents above reflects the chapter structure of the 1st edition with minimal 2nd-edition updates applied (Digium→Sangoma, MeetMe→ConfBridge, ARI added, "Ubuntu 18.04" version stripped). The author should regenerate the full ToC from the actual chapter files once all chapters are updated. "AsteriskNOW" in the Introduction chapter should be updated to note it is discontinued and replaced by FreePBX/Sangoma distributions.
