# Introduction to Asterisk PBX

The popularity of ready-to-run distributions such as FreePBX and Issabel has recently grown. In this book, we will cover the classic Asterisk, which is the foundation for understanding these distributions. Asterisk PBX is open-source software capable of transforming an ordinary PC into a powerful multiprotocol PBX. In this chapter, we will learn about the possibilities of this new technology and its basic architecture.

## Objectives

By the end of this chapter you should be able to:

- Explain what Asterisk is and what it does;
- Describe the role of Digium™ and its successor Sangoma;
- Recognize the basic architecture of Asterisk and its components;
- Point out several usage scenarios; and
- Identify sources of information and help.

## What is Asterisk

Asterisk is an open-source PBX software once installed in a PC’s hardware along with the correct interfaces—can be used as a full-featured PBX for home users, enterprises, VoIP service providers, and phone companies. Asterisk is also both an open-source community and a project sponsored by Sangoma Technologies (which acquired Digium in 2018). You are free to use and modify Asterisk to suit your needs. Asterisk allows real-time connectivity between PSTN and VoIP networks. Since Asterisk is much more than a PBX, you not only have an exceptional upgrade to your existing PBX, but you can also do new things in telephony, such as:

- Connect employees working from home to an Office PBX over broadband Internet;
- Connect several offices in different places over an IP network, private network, or even through the Internet itself;
- Give your employees a voicemail integrated with the web and e-mail;
- Build applications like IVRs that allow connections to your ordering system or other applications;
- Give traveling users access to the company PBX from anywhere with a simple broadband or VPN connection; and
- much more....

Asterisk includes several advanced resources previously only found in high-end systems, such as:

- Music for customers on hold waiting in call queues, supporting media streaming and MP3 files;
- Call queues, whereby a team of agents can answer calls and monitor queues;
- Integration with text-to-speech and voice recognition;
- Detailed records transferred to both text files and SQL databases; and
- PSTN connectivity through both digital and analog lines.

## What is AsteriskNOW (Historical) and FreePBX

Asterisk in its purest form, also known as “classic asterisk” (Debian package denomination) is considered more of a development tool than a finished product by itself. AsteriskNOW was an initiative to transform Asterisk into a soft-appliance. The distribution included CentOS as the operating system and FreePBX as the graphical interface. AsteriskNOW has since been discontinued.

Today, the standard turnkey Asterisk distribution is **FreePBX** (maintained by Sangoma), which bundles Asterisk with a web-based administration GUI and module ecosystem. FreePBX is licensed according to the GPL and can be freely downloaded from www.freepbx.org. For commercial deployments, Sangoma also offers **FreePBX Distro** (a complete Linux image) and its commercial product **PBXact**.

## Role of Digium™ and Sangoma

Digium, a company located in Huntsville, Alabama, was the creator and primary developer of Asterisk since its founding in 1999. In addition to being the primary sponsor of Asterisk development, Digium produced telephony interface cards and other hardware for Asterisk PBXs, and created commercial products such as Switchvox (targeted at the SMB market). In 2018, Digium was acquired by **Sangoma Technologies**, a Canadian unified communications company. Since the acquisition, Sangoma has continued to sponsor Asterisk development and serves as its primary steward, maintaining the open-source project at www.asterisk.org.

Historically, Digium offered Asterisk under three types of license agreements:

- General Public License (GPL) Asterisk. This is the most used version. It includes all features and is free to be used and modified according to the terms of the GPL license.
- Asterisk Business Edition was a commercial version of Asterisk. Some companies used the business edition because they did not want or could not use the GPL license—usually because they did not want to release their source code together with Asterisk. **Note:** Asterisk Business Edition has been discontinued; today Asterisk is distributed solely under the GPL.
- Asterisk OEM. This version was mostly used by PBX manufacturers who did not want to reveal to the public that their software was based on Asterisk.

### The Zapata project and its relationship with Asterisk

The Zapata project was developed by Jim Dixon, who was also responsible for the revolutionary hardware design used with Asterisk. The hardware is open-source too; as such, it can be used by any company, and today several manufacturers produce cards compatible with this architecture.

The Zapata project produced an architecture called Zaptel, later renamed DAHDI (Digium/Asterisk Hardware Device Interface). One of the main benefits of this architecture is the ability to use the PC CPU to process media streaming, echo cancellation, and transcoding. In contrast, most existing cards use digital signal processors (DSP) to perform these tasks. The use of the PC CPU instead of dedicated DSPs reduces the board's price dramatically. Thus, these cards are significantly cheaper than previously available interfaces from other manufacturers. On the other hand, these cards require a lot of CPU; a misuse of the PC CPU can significantly impact voice quality. Recently, Digium launched a coprocessor card that uses DSPs to encode and decode G.729 and G.723, allowing better scalability for a large number of channels.

## Why Asterisk?

I remember my first contact with Asterisk. Usually, the first reaction to something new—especially something that competes with what you already know—is to reject it! This is exactly what happened in 2003. Asterisk was competing with a solution that I was selling to a customer (4 E1 VoIP Gateway), and it was ten times less expensive than what I was charging for the solution I already knew. This disproportionate price led me to start studying Asterisk in order to identify potential pitfalls and drawbacks. For example, I found that the PC CPU at that time would not support 120 g.729 simultaneous sections, at the end of the day, I won the proposal with my Gateway solution. However, this exercise led me to the discovery that Asterisk could solve a variety of very expensive problems for my customer base. We were in trouble with expensive quotes for IVR, unified messaging, call recording, and dialers; with appropriate dimensioning, the CPU problems could be worked around. Indeed, in just three years Asterisk became the flagship product of my company (I actually decided to open another company just for the Asterisk business). In my opinion, Asterisk is a revolution in telecommunication that represents to IP telephony what Apache represents to web services.

### Extreme cost reduction

If you compare a traditional PBX with Asterisk in regard to digital interfaces and phones, Asterisk is slightly cheaper than those PBXs. However, Asterisk really pays off when you add advanced features such as voicemail, ACD, IVR and CTI. With these advanced features, Asterisk becomes significantly less expensive than traditional PBXs. In fact, comparing Asterisk PBXs with low-end analog PBXs is unfair because Asterisk offers so many features not available in low-end analog systems.

### Telephony system control and independence

One of customers’ most often-quoted benefits of asterisk is the independence that it provides. Some of today’s manufacturers do not even give the customer the system’s password or the configuration documentation. With Asterisk's “do-it-yourself” approach, the user achieves total freedom; as a bonus, the user has access to a standard interface.

### Easy and rapid development environment

Asterisk can be extended using script languages like PHP and Perl with AMI and AGI interfaces. Asterisk is open-source, and its source code can be modified by the user. The source code is written mostly in ANSI C programming language.

### Feature rich

Asterisk has several features that are either not found or optional in traditional PBXs (e.g., voicemail, CTI, ACD, IVR, built-in music on hold, and recording). The costs of these features in some platforms exceed the price of the platform itself.

### Dynamic content on the phone

Asterisk is programmed using C language and other languages common in today's development environment. The possibility to provide dynamic content is practically limitless.

### Flexible and powerful dial plan

Another Asterisk breakthrough is its powerful dial plan. In traditional PBXs, even simple features like least cost routing (LCR) are either not feasible or optional. With Asterisk, choosing the best route is easy and clean.

### Open-source running on top of Linux

One of the greatest features of Asterisk is its community. Several resources are available, including the Asterisk wiki (www.voip-info.org <http://www.voip-info.org>), e-mail distribution lists, and forums. As Asterisk becomes increasingly adopted, any bugs found and fixed quickly. Asterisk is probably the most tested PBX software in the world. From versions 1.0 to 1.2, more than 3,000 changes and bugs in the source code were corrected, thereby ensuring a code that is both stable and almost error free.

### Asterisk architecture limitations

Some limitations in Asterisk stem from the use of the Zapata telephony design. In this design, Asterisk uses the PC CPU to process voice channels instead of dedicated digital signal processors (DSPs), which are common in other platforms. Although this allows for a huge cost reduction in hardware interface, the system becomes dependent on the PC CPU. My recommendation is to run Asterisk in a dedicated machine and be conservative about hardware dimensioning. You can also use Asterisk in a separate VLAN to avoid excessive broadcasts that consume the CPU (broadcast storms caused by loops or viruses). Some newer interface cards from several vendors are now including DSPs to process echo cancellation, codecs, and other features, which will make Asterisk even better.

## Main objections to Asterisk PBX

It is common to hear objections to adopting Asterisk, which we will address here.

### Asterisk’s market share is too small

The market share is usually measured by the number of PBXs sold. These statistics are generally acquired from the biggest distributors. Asterisk is free software that does not appear in sales statistics. However, independent numbers prove that Asterisk “rocks the world”. According to VoIP-Supply, more than 300,000 systems run Asterisk, and Digium has sold more than 4 million voice interfaces. Some time ago, the Eastern Management Group concluded that open-source PBXs account for 18% of the market share, with the vast majority of them being Asterisk. In fact, 85% of the open-source PBX market is based on Asterisk, which now ranks second in terms of lines connected to an IP PBX.

### If it is free, how does the manufacturer survive?

Actually, there is no such thing as an open-source software manufacturer in the traditional sense. Digium developed Asterisk since 1999, sustaining itself through sales of telephony interface cards, commercial PBX products such as Switchvox, and related software. In 2018, Sangoma Technologies acquired Digium. Sangoma continues to fund Asterisk development and generates revenue through commercial products (FreePBX commercial modules, PBXact, Switchvox), hardware sales, and professional services.

### It is hard to find technical support!

Sangoma provides commercial technical support for Asterisk through its partner ecosystem and directly via its product offerings. A global network of certified professionals provides first-line support and professional services. Community support remains active through the Asterisk forums and mailing lists at www.asterisk.org.

### Does Asterisk support more than 200 extensions?

Yes, absolutely. Asterisk has been used in installations with more than 10,000 users. It is largely scalable using load balancing and failover systems. It is not uncommon to see more than a thousand users on a single server.

### Only “geeks” are able to install Asterisk

With FreePBX (available as a standalone distro from Sangoma), even professionals with limited knowledge about Linux are able to install and configure a PBX of medium complexity. With the help of a GUI, it is possible to configure an entire PBX in just a few hours.

### What if the server fails?

One of the main advantages of Asterisk is its capability to run in fault-tolerant systems. It is relatively simple and inexpensive to have two servers running in parallel. I dare you to try this with a conventional PBX!

### Our company does not use open-source software

Your company probably uses open-source software without even realizing it. Several appliances use Linux as their operating system. Moreover, commercial support and managed deployments are available from Sangoma and its certified partner network.

### Using the PC's CPU to process signaling and media is not recommended

Asterisk uses the server's CPU to process signaling and media for voice channels instead of having dedicated DSPs. Although this allows a cost reduction of up to five times, it makes the system dependent on the performance of the main CPU. With the correct dimensioning, Asterisk is capable of handling large volumes. If you still want to release the main CPU from these tasks, you can also use hardware echo cancellation and even transcoder cards, such as the Sangoma (formerly Digium) TC400B based on DSPs.

## Asterisk Architecture

This section will explain how Asterisk’s architecture works. The figure below shows the basic Asterisk architecture. Next, we will explain architecture-related concepts, including channels, codecs, and applications.

### Channels

A channel is the equivalent of a telephone line, but in a digital format. It usually consists of an analog or digital (TDM) signaling system or a combination of codec and signaling protocol (e.g., SIP-GSM, IAX-uLaw). Initially, all telephony connections were analog and susceptible to echo and noise. Later, most systems were converted to digital systems, with the analogical sound converted into a digital format using pulse code modulation (PCM) in most cases. This format allows voice transmission in 64 kilobits/second without compression.

Channels interfacing with the Public Switched Telephone Network (PSTN):

- `chan_dahdi`: analog (FXO/FXS) and digital (E1/T1/PRI) TDM cards from Sangoma (formerly Digium), Xorcom, and others. Built separately against DAHDI — see the *Legacy channels* chapter.

Channels interfacing with Voice over IP:

- `chan_pjsip`: SIP — the primary and only SIP channel driver in Asterisk 22 LTS. Dial string: `PJSIP/endpoint_name`. (**Note:** the old `chan_sip` was removed in Asterisk 21 and does not exist in Asterisk 22. See *Building your first PBX with PJSIP* for configuration.)
- `chan_iax2`: the IAX2 protocol — still ships in Asterisk 22 but is legacy; SIP/PJSIP is preferred for new deployments. Dial string: `IAX2/peer`.
- `chan_unistim`: Nortel/Avaya UNISTIM phones. Still available (extended support) but rarely used.

The older VoIP channels are no longer part of a standard Asterisk 22 build: `chan_h323` (H.323) survives only as the community `ooh323` add-on, and `chan_mgcp` (MGCP) and `chan_skinny` (Cisco SCCP) were deprecated and dropped from the modern channel set. If you must interwork with those protocols, a gateway in front of Asterisk is the usual approach.

Miscellaneous channels:

- **Local**: a pseudo-channel (built into the core) that loops back into the dial plan in a different context — useful for recursive routing and for fanning a call out to multiple destinations. Dial string: `Local/extension@context`.

![01-introduction-to-asterisk figure 1](../images/01-introduction-to-asterisk-img01.png)

![01-introduction-to-asterisk figure 2](../images/01-introduction-to-asterisk-img02.png)

### Codec and codec translation

We usually try to put as many voice connections as possible in a data network. Codecs enable new features in digital voice, including compression, which is one of the most important features as it allows compression rates larger than 8 to 1. Other features include voice activity detection, packet loss concealment, and comfort noise generation. Several codecs are available for Asterisk and can be transparently translated from one to another. Internally, Asterisk uses slinear as the stream format when it needs to convert from one codec to another. Some codecs in Asterisk are supported only in pass-through mode; these codecs cannot be translated. To verify which codecs are installed in your system, you can use the console command:

```
CLI>core show translation
```

The following codecs are supported:

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - Only pass-through mode
- G.726 - (16/24/32/40kbps)
- G.729 - Binary codec module freely distributed by Sangoma (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.5 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus (5.3-510Kbps )

### Protocols

Sending data from one phone to another should be easy provided that the data find a path to the other phone on their own. Unfortunately, it doesn't happen this way, and a signaling protocol is necessary in order to establish connections between phones, discover end devices, and implement telephony signaling. SIP is the dominant signaling protocol in modern deployments and is the only SIP channel available in Asterisk 22 LTS (via chan_pjsip). IAX2 is still available but considered legacy. Asterisk supports the following protocols.

- SIP — via `chan_pjsip` (the old `chan_sip` was removed in Asterisk 21)
- IAX2 — legacy, still ships in Asterisk 22
- UNISTIM — Nortel/Avaya phones (extended support)
- H.323, MGCP, and SCCP (Cisco Skinny) — legacy protocols no longer in a standard Asterisk 22 build (H.323 only via the community `ooh323` add-on)

### Applications

To bridge calls from one phone to another, the application dial() is used. Most Asterisk features (e.g., voicemail and conferencing) are implemented as applications. You can see available Asterisk applications by using the core show applications console command.

```
CLI>core show applications
```

You can add applications from Asterisk add-ons, third-party providers, or even those you develop yourself.

## Overview of an Asterisk system

Asterisk is an open-source PBX that acts like a hybrid PBX, integrating technologies such as TDM and IP telephony. Asterisk is ready to implement functionality such as interactive voice response (IVR) and automatic call distribution (ACD); moreover, as previously mentioned, it is open to the development of new applications. This figure shows how Asterisk connects to the PSTN and existing PBXs using analog and digital interfaces as well as supports analog and IP phones. It can act as a soft-switch, media gateway, voicemail, and audio conference and also has built-in music on hold.

## Comparing the old and the new world

In the old soft-switch model, all components were sold separately, meaning you had to purchase each component separately and then integrate to the PBX or soft-switch environment. The costs and risks were high and most of the equipment proprietary.

![01-introduction-to-asterisk figure 3](../images/01-introduction-to-asterisk-img03.png)

![01-introduction-to-asterisk figure 4](../images/01-introduction-to-asterisk-img04.png)

### Telephony using Asterisk

All functions are integrated in the Asterisk platform in the same or in different boxes according to the dimensioning, and all are GPL licensed. Sometimes it is easier to install Asterisk than license some of the mainstream IP-PBXs

![01-introduction-to-asterisk figure 5](../images/01-introduction-to-asterisk-img05.png)

![01-introduction-to-asterisk figure 6](../images/01-introduction-to-asterisk-img06.png)

![01-introduction-to-asterisk figure 7](../images/01-introduction-to-asterisk-img07.png)

![01-introduction-to-asterisk figure 8](../images/01-introduction-to-asterisk-img08.png)

## Building a test system

When implementing an Asterisk solution, our first step is generally to build a test machine. The easiest test machine is the 1x1 PBX, including at least one phone and one line. There are several ways to do this.

### One FXO, one FXS

The first and simplest way to build a test machine is to purchase a card with one FXO and one FXS interface. Connect the FXO port to an existing line and connect one FXS to an analog phone. Thus, you have a 1x1 PBX.

### VoIP Service Provider: ATA

This is the VoIP option. In this case, you would sign up with a voice service provider to have the SIP trunks and will have to purchase a SIP analog telephony adapter. You will probably spend less than a hundred dollars if you already have the PC.

### Inexpensive FXO card or ATA

I started with an inexpensive FXO card. Some inexpensive V.90 fax/modems work with Asterisk as an FXO card. Some of the first Digium cards were created using these cards (e.g., X100P and X101P), which are old modems based on Motorola and Intel chipsets (Motorola 68202-51, Intel 537PU, Intel 537PG, and Intel Ambient MD3200 are known to work). These modems are often incompatible with new motherboards. Recently some manufacturers started to sell these cards as

![01-introduction-to-asterisk figure 9](../images/01-introduction-to-asterisk-img09.png)

![01-introduction-to-asterisk figure 10](../images/01-introduction-to-asterisk-img10.png)

X100P clones. Some of the incompatibilities can be solved using a patch, more information can be found at:

- http://www.voip.school/mediawiki/index.php/Asterisk_patch_for_the_X100P_card

## Asterisk scenarios

Asterisk can be used in several different scenarios. We will list some of them and explain the advantages and possible limitations of each.

### IP PBX

The most common scenario is the installation of a new or the replacement of an existing PBX. If you compare Asterisk with some other alternatives, you will find it to be cheaper and richer in features than most PBXs currently available on the market. Several companies are now changing their specifications to Asterisk instead of other brand-name PBXs.

### IP-enabling legacy PBXs

The following image illustrates one of the most commonly used setups. Large companies generally do not want to take significant risk when investing in new technologies and simultaneously wish to preserve their investments in legacy equipment. IP-enabling legacy PBX can be very expensive; thus, connecting an Asterisk PBX using T1/E1 lines can be a good alternative for cost-conscious customers. Another benefit is the possibility of connecting to a VoIP service provider with better telephony rates.

![01-introduction-to-asterisk figure 11](../images/01-introduction-to-asterisk-img11.png)

![01-introduction-to-asterisk figure 12](../images/01-introduction-to-asterisk-img12.png)

### Toll Bypass

A very useful application for VoIP is connecting branch offices over the Internet or a WAN. Using an existing data connection allows you to bypass toll charges incurred in telecommunication connections between headquarters and branch offices.

![01-introduction-to-asterisk figure 13](../images/01-introduction-to-asterisk-img13.png)

![01-introduction-to-asterisk figure 14](../images/01-introduction-to-asterisk-img14.png)

![01-introduction-to-asterisk figure 15](../images/01-introduction-to-asterisk-img15.png)

### Application Server (IVR, Conference, Voicemail)

Asterisk can be used as an application server for the existing PBX or be directly connected to PSTN. Asterisk offers services such as voicemail, fax reception, call recording, IVR connected to a database, and an audio conferencing server. If you integrate voicemail and fax into an existing e-mail server, you will have a unified messaging system, which is usually an expensive solution. Using Asterisk as an application server provides extreme cost reduction compared to other solutions.

### Media Gateway

Most voice-over IP service providers use an SIP proxy to host all registration, location, and authentication of SIP users. They still have to send calls to the PSTN directly or route it through a wholesale call termination provider using an SIP or H.323 voice-over IP connection. Asterisk can act as a back-to-back user agent (B2BUA) or media gateway, replacing very expensive soft switches or media gateways. Compare the price of a four E1/T1 gateway from the main market manufacturers with Asterisk. The Asterisk solution can cost several times less than other solutions and is capable of translating signaling protocols (H.323, SIP, IAX…) and codecs (G.711, G.729…).

![01-introduction-to-asterisk figure 16](../images/01-introduction-to-asterisk-img16.png)

### Contact Center Platform

A contact center is a very complex solution that combines several technologies, such as automatic call distribution (ACD), interactive voice response (IVR), and call supervision. Basically, three types of contact centers are available: inbound, outbound, and blended. Inbound contact centers are very sophisticated and usually require ACD, IVR, CTI, recording, supervision, and reports. Asterisk has a built-in ACD to queue the calls. IVR can be done using Asterisk Gateway Interface (AGI) or internal mechanisms such as the application background(). Computer telephony integration (CTI) is achieved using Asterisk Manager Interface (AMI); recording and reporting are built in to Asterisk. For an outbound contact center, a predictive or power dialer is one of the main components. Although several dialers are available for the open-source Asterisk, it is not hard to build your own for the platform if you so desire. A blended contact center allows simultaneous inbound and outbound operation, saving money by ensuring better use of the agent's time. It is possible to use Asterisk and its ACD mechanism to implement a blended solution.

![01-introduction-to-asterisk figure 17](../images/01-introduction-to-asterisk-img17.png)

![01-introduction-to-asterisk figure 18](../images/01-introduction-to-asterisk-img18.png)

## Finding information and help

This section will provide some of the main sources of information related to Asterisk.

- Asterisk’s official website: <https://www.asterisk.org> Here you can find information about:
- Documentation & Wiki -> <https://docs.asterisk.org>
- Community forum -> <https://community.asterisk.org>
- Bug tracking -> <https://github.com/asterisk/asterisk/issues>
- Wiki (legacy, largely superseded by docs.asterisk.org) -> <https://wiki.asterisk.org>

### Mailing lists

Mailing lists are quite handy when you have questions. Usually, you will receive answers for your questions. Try to gather as much information as possible before posting to the list. Nobody will help you if you haven't done your homework. In other words, try at least once to solve the problem by yourself.

- <http://www.asterisk.org/support/mailing-lists>

## Summary

Asterisk is software licensed according to the GPL that enables an ordinary PC to act as a powerful IP PBX platform. Digium’s Mark Spencer created Asterisk in the late 1990s, and Digium sustained itself by selling Asterisk-related hardware and commercial products. Digium was acquired by Sangoma Technologies in 2018; Sangoma now sponsors Asterisk development. Hardware interface design originated in the Zapata project developed by Jim Dixon, which gave rise to DAHDI.

![01-introduction-to-asterisk figure 19](../images/01-introduction-to-asterisk-img19.png)

![01-introduction-to-asterisk figure 20](../images/01-introduction-to-asterisk-img20.png)

The Asterisk architecture has the following main components:

- CHANNELS: Analog, digital, or voice-over IP. In Asterisk 22 LTS, SIP is handled exclusively by chan_pjsip (chan_sip was removed in Asterisk 21).
- PROTOCOLS: Communication protocols, which are responsible for signaling the calls, including SIP (via PJSIP), H323, MGCP, and IAX2.
- CODECS: Translate digital formats of voice allowing compressions, packet loss concealment, silence suppression, and comfort noise generation. Asterisk does not support silence suppression.
- APPLICATIONS: Responsible for the Asterisk PBX functionality. Conference, voicemail, and fax are examples of Asterisk applications.

Asterisk can be used in various scenarios, from a small IP PBX to a sophisticated contact center. You can easily find help at www.asterisk.org and docs.asterisk.org.
