# Legacy channels: analog, TDM & IAX2

In a 2026 pure-VoIP world, the channel types in this chapter are increasingly rare: most new deployments are SIP trunks and PJSIP endpoints over Ethernet, with no telephony hardware at all. Asterisk 22 nonetheless still supports most of them fully. Analog (FXO/FXS) and digital TDM (E1/T1/ISDN PRI/BRI) connectivity is provided through DAHDI — the driver stack originally developed by Digium, which was acquired by Sangoma in 2018, after the earlier Zaptel drivers were renamed following a trademark dispute. Server-to-server connectivity over IAX2 is provided by `chan_iax2`, which is still shipped and supported but is now firmly a legacy protocol. This chapter also collects the **legacy SIP** material: the old `chan_sip` driver and its `sip.conf` configuration — removed in Asterisk 21 and gone in Asterisk 22 — together with a complete guide to migrating an existing `sip.conf` system to PJSIP. If you are running a pure-SIP shop on PJSIP with no telephony cards, no IAX2 trunks, and no legacy `sip.conf` to convert, you can safely skip this chapter.

## Analog channels (FXO/FXS)

> **[2nd-ed note]** Update front-matter dates/ISBN for the 2nd edition before publication.

> **[2nd-ed note — deployment context]** As of Asterisk 22, DAHDI and analog telephony cards remain fully supported and DAHDI still builds against current kernels. However, the majority of new deployments are pure VoIP (SIP trunks, PJSIP). Analog/TDM hardware is now a niche choice, mainly found in legacy environments, rural PSTN connectivity, or regulated markets. The content below is still accurate for those scenarios.

There are several ways to connect the public switched telephone network (PSTN). The best way depends on how the telephone company makes this connection available in your area. The simplest way is to use an analog line, similar to the line you use at home. In this section, we will show you how to configure analog cards from Sangoma™ (formerly Digium™) and Xorcom™.

### Objectives

By the end of this chapter you should be able to:

- Recognize the main telephony terms and acronyms;
- Understand when to use digital and analog circuits;
- Recognize the difference between FXS and FXO; and
- Configure Asterisk for FXS and FXO.

### Telephony basics

Most analog implementations use a pair of cooper lines named tip and ring. When a loop is closed, the phone receives the dial tone from the telecom switch (or the private PBX). The most frequently used signaling is loop-start; other, less common kinds of signaling including ground start, which is used in several countries. The three categories of signaling are:

- Supervision signaling
- Address signaling
- Information signaling

#### Supervision signaling

The main supervision signalings are on-hook, off-hook, and ringing. On-Hook – When a user puts the phone on the hook, the PBX interrupts and does not allow the electric current to pass. In this state, the circuit is named on-hook. In this position, only the ringer is active. Off-Hook – Before starting a phone call, the phone needs to pass to the off-hook state. Removing the handset from the hook closes the loop and indicates to the PBX that the user intends to make a call. Upon receiving this indication, the PBX generates a dial tone, indicating to the user that it is ready to accept the destination address (i.e., phone number). Ringing – When a user calls another phone, it generates a voltage to the ringer that warns the other user about a call being received. Signaling varies by country, with different tones for different countries. You can personalize Asterisk tones to your country by modifying the indications.conf file. For example:

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### Address Signaling

You can use two kinds of signaling for dialing. The first and most common is dual tone multi- frequency (dtmf) while the other is pulse dialing (used in old rotary dial phones). Phones have a keypad for dialing, and each button is associated with two frequencies: one high and one low. In the case of dtmf signaling, the combination of these tones indicates what digit is being pressed. MFC/R2 uses a multi-frequency tone different from dtmf.

#### Information signaling

Information signaling shows the call’s progress and different events.

- Dial tone
- Busy Tone
- Ringback
- Congestion
- Invalid number
- Confirmation tone

### PSTN interfaces

As in the case of old PBXs, it is often required to connect the Asterisk PBX to the PSTN. Here we’ll show you how to do it. Usually you have three options for telephone lines.

- Analog: The most common form for home and small business, usually delivered with a metallic pair of cooper lines.
- Digital: Used when many lines are necessary. A digital line is usually delivered by a CSU/DSU or a Fiber multiplexer. The end user connector is usually a RJ45. In some countries, E1 lines are delivered using two coaxial BNC connectors; in this case you will need a balloon to connect to the RJ45 jack to the telephony board.
- SIP: This option has been recently developed. The telephone line is delivered using a data connection with SIP signaling (VoIP). This is a good option to use with Asterisk since you will not need to buy a telephony card. Phone calls will be delivered directly to the Ethernet port. Another advantage is that you may be able to free resources from your CPU by avoiding codec transcoding.

### Analog FXS, FXO, and E&M interfaces

Several types of analog interfaces are available. It is fundamental to understand the differences between these interfaces to learn how to connect to the phone network as well as to other PBXs. Here, we will show you the E&M interface. Although it is not currently available for Asterisk and has been discontinued by several vendors, you may find routers and PBXs with this kind of interface, so it is better to know what you are dealing with.

#### Foreign eXchange (FX) Interfaces

FX interfaces are analog. The term “Foreign eXchange” is applied to access trunks to a PSTN central office (CO). Foreign eXchange Office (FXO)

![Asterisk between an analog phone (FXS) and the telco line (FXO): the FXS side provides dial tone and ringing to the phone, while the FXO side draws dial tone from the central office.](../images/10-legacy-fig01.png)

The FXO interface is used to connect to a central office (CO) or another PBX’s extension. It communicates directly with a telephone line coming from the PSTN. Another option is to connect the FXO interface to an existing PBX, allowing communication between Asterisk and the legacy PBX. Connecting Asterisk to a PBX port and delivering a remote extension using VoIP is often referred to as an off-promises extension (OPX). An FXO interface receives a dial tone. Foreign eXchange Station (FXS) The FXS interface feeds an analog phone, modem, or fax. The FXS provides the dial tone and power for a phone.

#### Trunk signaling

- Loop-Start
- Ground-Start
- Kewlstart

The use of kewlstart signaling in Asterisk is almost default. Kewlstart is not signaling itself, but adds intelligence to the circuit by monitoring what is happening on the other side. Kewlstart is based in loop-start. Most switches do not support this feature, which is used to get the hang-up notification.

- Loopstart: Used in most analog lines, it allows the telephone to indicate “on-hook” and “off-hook” and the switch to indicate “ring” and “no-ring”. This is probably what most people have at home. The name comes from the fact that the line is always open. When you close the loop, the switch provides you with a dial tone. An incoming call is signaled by a 100V ringing voltage over the open pair.

![Asterisk operating as a VoIP gateway: an FXO port connects to a legacy PBX extension while a remote Asterisk delivers that line to an analog phone over IP through an FXS port (an off-premises extension, or OPX).](../images/10-legacy-fig02.png)

- Groundstart: Similar to Loopstart. When you want to make a call, one side of the line is short-circuited. When the switch identifies this state, it reverses the voltage through the open pair, and then the loop is closed. Consequently, the line first becomes occupied before being offered to the caller.
- Kewlstart: Adds intelligence to the circuits, allowing monitoring of the other side. Kewlstart incorporates many advantages from loop-start.

### Asterisk telephony channels setup

To configure a telephony interface card, several steps are necessary. In this chapter, we will show three of the most common scenarios:

- Analog connection using FXS
- Analog connection using FXO
- Connection of an Astribank™ with FXS and FXO interfaces

### Configuration Procedure (valid in both cases)

Before choosing hardware for Asterisk, you should consider the number of simultaneous calls, services, and codecs that are going to be installed and enabled. Asterisk is a CPU-intensive application, which is why we recommend a dedicated machine for Asterisk. The number of interface cards installed within the computer is limited by the number of slots and interruptions available. It is preferable to install a single card with eight voice interfaces than two cards with four. Another option is to use a USB channel bank, such as the Xorcom Astribank. Recently, some manufacturers (e.g., CIANET) have started producing TDMoE channel banks, making it even easier to connect dozens of analog interfaces.

![A Xorcom Astribank: a 19-inch rack-mount USB channel bank that exposes dozens of FXS/FXO ports (here a 32-port unit) without consuming PCI slots in the host.](../images/10-legacy-fig03.png)

#### Example 1: One FXO, one FXS installation

In this example, we will use a Sangoma TDM400 telephony interface card (formerly sold as the Digium TDM400) with one FXS and one FXO module. The required steps are listed below:

1. Install the analog card FXS, FXO, or both.
2. Configure the file `/etc/dahdi/system.conf` (formerly `/etc/zaptel.conf`).
3. Generate the configuration files using `dahdi_genconf`.
4. Load the driver for the DAHDI interface.
5. Execute `dahdi_test` to verify interrupt misses.
6. Execute `dahdi_cfg` to configure the driver.
7. Configure the DAHDI channel in the `chan_dahdi.conf` file, then load Asterisk.

##### Step 1: Install the TDM400 board

The TDM404P card contains FXS and FXO modules. Connect the FXS (S110M, green) and FXO (X100M, red) modules. If you are using FXS modules, connect the card directly to the power source using a molex connector. Please wear electrostatic protection before handling interface cards to avoid damage to the hardware. Sangoma (formerly Digium) analog cards also support a hardware echo cancellation module VPMADT032.

##### Step 2: Generate the configuration with dahdi_genconf

The good news about the configuration is the new utility `dahdi_genconf`, which automatically detects and generates the configuration for DAHDI interfaces. The utility generates two files:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (with the `users` option)
- All these files use the option `chan_dahdi full`

Before you can execute `dahdi_genconf`, it is important to configure the file `genconf_parameters` (often referred to as `gen_parameters.conf`):

![A Sangoma/Digium TDM404P analog card: up to four FXS or FXO modules plug into the numbered ports, with an optional hardware echo-cancellation daughter card and a dedicated 12 V power connector for FXS modules.](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

The `genconf_parameters` file lets you customize your configuration. The most important parameters for analog lines are:

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

Warning: It is required that you configure at least the echo cancellation algorithm for the channels. The base_exten parameter defines the basic dial plan for FXS extensions. In this case, the first FXS channel will receive the extension number 4000, the second 4001, and so on. The context in which the lines (context_phones) and trunks (context_lines) are created is very important. After generating the files, you should include the file `/etc/asterisk/dahdi-channels.conf` in the file `/etc/asterisk/chan_dahdi.conf`:

```
#include dahdi-channels.conf
```

Note: Analog signaling is a bit confusing; it is always the inverse of the card. FXS cards are signaled with FXO whereas FXO cards are signaled with FXS. Asterisk talks to these devices as if it was on the opposite side.

##### Step 3: Load kernel drivers

Now you have to load the chan_dahdi module and the related card kernel driver. Use dahdi_hardware to detect your card and the driver name. For example:

- Card Driver Description
- TE410P wct4xxp 4xE1/T1-3.3V PCI
- TE405P wct4xxp 4xE1/T1-5V PCI
- TDM400P wctdm 4 FXS/FXO
- T100P wct1xxp 1 T1 E100P wctlxxp 1 E1 X100P wcfxo 1 FXO

Commands to load the drivers:

```
modprobe dahdi
modprobe wctdm
```

##### Step 4: Use the dahdi_test utility

An important utility is dahdi_test, which is used to verify interrupt misses in the DAHDI card. Audio quality problems are often related to interrupt conflicts. To verify that your DAHDI card is not sharing an interrupt with other cards, use the following command:

```
#cat /proc/interrupts
```

You can verify the number of interrupt misses using the dahdi_test utility compiled with the DAHDI cards. A number below 99.987% indicates possible problems.

##### Step 5: Use the dahdi_cfg utility to configure the driver

DAHDI has an unusual system for loading the drivers. First configure the /etc/dahdi/system.conf, and then apply those configurations to the DAHDI driver using dahdi_cfg. In this case, dahdi_cfg is used to configure the signaling for the FX interfaces. To see the results, you can append “-vvvvv” to the command for verbose.

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

If the channels were loaded successfully, you will see an output similar to the one shown above. Users often incorrectly configure chan_dahdi.conf with inverted signaling between channels. If this happens, you will see a message like the one shown below:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After successfully configuring the hardware, you can proceed to Asterisk configuration.

##### Step 6: Configure the /etc/asterisk/chan_dahdi.conf file

It sounds strange, but after configuring the /etc/dahdi/system.conf, you configured the card itself. DAHDI can be used for other purposes, like routing and SS7. To use it with Asterisk, you must configure the Asterisk DAHDI channels. Every channel in Asterisk has to be defined; SIP/PJSIP channels are defined in pjsip.conf (note: chan_sip and sip.conf were removed in Asterisk 21) while TDM channels are defined in chan_dahdi.conf. This creates the logical TDM channels to be used in your dial plan.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### Configuration options

Several options are available in the chan_dahdi.conf file. A description of all options would be boring and counterproductive; instead, we will focus on the main option groups available for easy understanding.

#### General options (channel independent)

These options work for any channel: context: Defines the incoming context.

```
context=default
```

channel: Defines channel or channel range. Each channel definition will inherit options defined before the declaration. Channels can be identified individually or in the same line by comma separation. Ranges can be defined using “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Allows channels to be handled as a group. If you dial a group number instead of a channel number, the first channel available is used. If channels are phones, when you call a group, all phones will ring simultaneously. With commas, you can specify more than one group for the same channel.

```
group=1
group=3,5
```

language: Turns on the internationalization and configures a language. This feature will configure system messages for a specific language. English is the only language with complete prompts available through standard installation. musiconhold: Selects music on hold class.

#### Caller ID options

There are many callerid options. Some can be disabled, although most are enabled by default. usecallerid: Enables or disables the callerid transmission for the subsequent channels (Yes/No). Note: If your system gets two rings before answering, try disabling this feature. It should answer immediately. hidecallerid: Defines whether or not to hide the outgoing callerid (Yes/No). callerid: Configures a callerid string for a specific channel. The caller can be configured with asreceived. This is mostly used in trunk interfaces to indicate the incoming callerid.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Supports callerid during call waiting. useincomingcalleridondahditransfer: Uses the incoming callerid in a transfer.

#### Call Waiting

Asterisk supports call waiting in FXS channels. The user will receive a waiting tone if someone tries the extension. To enable call waiting:

```
callwaiting=yes
```

To support callerid in call waiting:

```
callwaitingcallerid=yes
```

#### Audio quality options

Adjusting the echo cancellation is half technical, half art. These options adjust certain Asterisk parameters that affect audio quality in the DAHDI channels. They can help improve audio quality in analog interfaces.

#### The fxotune utility

The fxotune is a utility used to fine-tune certain parameters for FXO modules. This fine-tuning is required to adjust impedance mismatch caused by the hybrid. The utility has three operation modes:

- Detection (-i): detects and fixes the existing FXO channels and saves the configuration to

```
fxotune.conf
```

- Dump mode (-d): generates the waveform files to fxotune_dump.vals
- Startup mode (-s): reads the file fxotune.conf and applies it to the FXO modules

It is important to understand that you will have to insert the instruction fxotune –s in the system load before starting Asterisk:

```
#modprobe dahdi
#modprobe wctdm
#fxotune-s
```

### Echo cancellation

Most echo cancellation algorithms operate by generating multiple copies of the received signal, in which each one is delayed by a specific amount of time. The number of taps of the filter determines the size of the echo delay that needs to be cancelled. These delayed copies are then adjusted and subtracted from the received signal. The trick is to adjust only the delayed signal to remove the echo without using too many CPU cycles. From the users’ perspective, it is important to choose an appropriate echo cancellation algorithm. The default is MG2; however, two other options are available: the High Performance Echo Cancellation (HPEC) from Sangoma (formerly Digium) and the open-source echo cancellation (OSLEC) developed by David Rowe.

> **[2nd-ed note]** The OSLEC project page (http://www.rowetel.com/ucasterisk/oslec.html) may no longer be current; verify availability and kernel integration status for modern kernels before referencing it. To change the echo cancellation algorithm, change the parameter echo_can to /etc/dahdi/system.conf. For example:

```
echo_can=oslec
```

The echo cancellation in Asterisk is controlled by three parameters in the file /etc/asterisk/chan-

```
dahdi.conf.
```

echocancel: Disables or enables echo cancellation. You should keep this feature enabled. It accepts “yes” or the number of taps. Explanation: How does echo canceling work? Most echo canceling algorithms operate by generating multiple copies of a received signal, with each being delayed by a small interval. This little flow is called a “tap”. The number of taps determines the echo delay that can be cancelled. These copies are delayed, adjusted, and subtracted from the original signal. The trick is to adjust the delayed signal exactly to what is necessary to remove the echo. echocancelwhenbridged: Enables or disables the echo canceller during a pure TDM call. This is usually not necessary. rxgain: Adjusts the audio reception gain to either increase or decrease reception volume (-100% to 100%). txgain: Adjusts audio transmission gain to either increase or decrease the transmission volume (- 100% to 100%). For example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Billing options

These options change how call information is recorded in the call detail records (CDR) database. amaflags: Configures the AMA flags affecting the CDR categorization. It accepts the following values:

- billing
- documentation
- omit
- default

accountcode: Configures an account code for a specific channel. It can contain any alphanumeric value—usually the department or user name.

```
accountcode=finance
amaflags=billing
```

### Call progress options

These items are used to acquire information about the progress of the call. In public interfaces, it may be useful to detect the call progress and determine if it was answered or busy. The busy detection is highly experimental and regulated by specific parameters.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

These parameters (above) specify whether the interface will try to detect the busy tone, how many tones will be used for successful detection, and what is the busy pattern. The busy detection is largely experimental, and some additional parameters can be changed in the Makefile. To detect the answer of a call, which is essential for precise billing, it is possible to use the polarity reversal to signal the exact answer time. This is important if you plan to charge for the call or just wish to have precise billing for comparison. Usually you have to contact the phone company to request this service.

```
answeronpolarityswitch=yes
```

In some countries, it is possible to detect the hang up of the call using polarity reversal as well.

```
hanguponpolarityswitch=yes
```

#### Options for phones

These options are used for phones connected to the FXS interfaces. All the functionalities delivered to analog phones connected directly to the DAHDI interfaces are controlled by Asterisk. Adsi (Analog Display Services Interface): This is a set of telecom standards used by some telcos to offer services such as ticket buying. cancallforward: Enables or disables call forwarding (*72 to enable and *73 to disable). calleridcallwaiting: Enables callerid received during a call waiting indication (Yes/No). immediate: In immediate mode, instead of providing a dial tone, the channel jumps immediately to the “s” extension in the defined context. This is used to create hotlines. threewaycalling: Enables or disables three-way conferencing. mailbox: Warns the user about available voicemail messages. It can be an audible sign or a visual indicator (if the telephone supports this feature). The argument is the mailbox number. callgroup: Group phones to dial or to pick up. pickupgroup: Group of phones for call pickup.

### Useful DAHDI CLI commands

Once Asterisk is running with DAHDI channels loaded, you can inspect channel status from the Asterisk CLI. These commands remain current in Asterisk 22:

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDI channel format

DAHDI channels use the following format in the dial plan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

For example:

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
```

## Digital channels (E1/T1/PRI / TDM)

> **[2nd-ed note]** As of Asterisk 22, DAHDI and libpri remain fully supported, but TDM digital trunks (E1/T1/ISDN PRI) are increasingly replaced by SIP trunks in new deployments. This chapter remains fully applicable where TDM connectivity is required; readers in greenfield environments may prefer SIP trunking (Chapter 3) for similar channel density.

Digital channels are extremely common, so you will need to learn how to implement these channels if you want to focus on large customers. When the number of channels is high—usually more than 8—it is fairly common to use digital interfaces such as T1/E1/J1. T1 is very common in the US, whereas E1 is common in Europe and J1 in Japan. These types of channels allow for a good density of circuits—24 per T1 channel and 30 for E1 channels. In Latin America, China, and Africa, it is common to use a type of channel associated signaling (CAS) known as MFC/R2. This chapter will examine how to implement MFC/R2 using the library OpenR2. In the US and Europe, Integrated Services Digital Networks (ISDN) PRI is the most common signaling. The chapter will also discuss ISDN Basic Rate Interface (BRI), which is very common in Europe in mid-range applications. All examples in the book concentrate on DAHDI channels. Some cards are implemented using proprietary channels, so please check with your manufacturer for further details on how to configure your specific card.

### Objectives

By the end of this chapter you will be able to:

- Recognize the main terms used in digital telephony
- Differentiate CAS and CCS signaling
- Differentiate R2 and ISDN signaling
- Configure interfaces with ISDN signaling
- Configure interfaces with R2 signaling

### E1/T1 digital lines

Digital lines E1/T1 are an option whenever you need to implement a large number of channels. A single E1 circuit is capable of 30 simultaneous calls, and you may have features such as direct inward dial (DID), Caller ID (caller identification), and advanced signaling. The E1/T1 line may arrive at your company in several ways using twisted pair, fiber, and microwaves, depending on your country. Digital lines are delivered to your company using UTP, fiber, or microwaves. Modems and multiplexors (MUX) are used to deliver the physical line. The connection to a T1 line is always based in an RJ45 connector. However, E1 lines may be provisioned as well using BNC. It is very important to know the type of connector you are going to receive in advance, mainly in E1 lines. Usually all the equipment up to the RJ45 is provided by the TELCO.

![How E1/T1 circuits are provisioned: the telco can deliver the trunk over UTP copper (HDSL modem for E1, or a direct card connection for T1), over optical fiber through an optical multiplexer, or over a microwave radio link.](../images/10-legacy-fig05.png)

![UTP or BNC? Most digital cards use RJ45 (UTP) connectors, but some E1 lines are delivered on dual BNC coax, in which case a balun is needed to adapt the coaxial pair to the card's RJ45 jack.](../images/10-legacy-fig06.png)

#### How is the voice converted to bits?

The analog signal is sampled 8,000 times per second to create a digital version of the analog voice. This encoding is known as pulse code modulation (PCM). In the US and Japan, the signal is encoded using law (in Asterisk, referred to as ulaw). In the rest of the world, the encoding is alaw.

![Pulse code modulation (PCM): the 4 kHz analog voice signal is sampled 8,000 times per second (Nyquist) and coded into a 64 Kbps digital stream of bits.](../images/10-legacy-fig07.png)

#### Time Division Multiplexing

Analog lines make sense when you need just a few channels. When using time division multiplexing (TDM), it is possible to stuff multiple channels into a single data connection. When you want a large number of circuits, the phone company will usually provide you with a digital trunk, which is a data circuit in which the voice is transported in a digital format using PCM. Each timeslot uses 64 Kbps of bandwidth to transport a single voice channel.

![Time-division multiplexing in E1 and T1: an E1 frame carries 32 timeslots at 2048 Kbps (DS0 #0 for frame synchronization, DS0 #16 for signaling), while a T1 frame carries 24 timeslots at 1544 Kbps using one bit for synchronization and a robbed-bit scheme for signaling.](../images/10-legacy-fig08.png)

In the US, the most common digital trunk is T1, which has 24 available lines; in Europe and Latin America, E1 trunks have 30 lines. Some companies provide a fractional T1/E1 with fewer channels. Robbed bit signaling Sometimes a T1 trunk uses a robbed bit scheme where one bit is borrowed for signaling. On T1 trunks, the data/voice channel is transmitted with 56 Kbps on each timeslot. As you may observe, when you use the robbed bit, the T1 circuit does not lose two slots for synchronization and signaling.

#### T1/E1 Line code

T1s and E1s are actually data circuits and have a data coding that determines the way in which the bits are interpreted. For E1s, the most common line code is HDB3 for layer 1 and CCS for layer 2. The easiest way to know how your digital trunk is configured is to ask the TELCO about this information. You will need this information to configure the file /etc/dahdi/system.conf.

#### T1/E1 Signaling

It is important to understand that T1/E1 lines may be delivered using different kinds of signaling, such as:

- T1 with robbed bit signaling
- T1 with ISDN signaling
- E1 with MFC/R2 (CAS - Channel Associated Signaling)
- E1 with ISDN signaling

ISDN is often used in Europe and the US. It is a digital voice network, standardized by the International Telecommunications Union (ITU) in 1984. ISDN provides two kinds of channels:

- Bearer channels o Voice o Data
- Data channels o Out of band signaling o LAPD signaling o Q.931

Usually, an ISDN line is provided using two physical means:

- Basic rate interface (BRI) o Known as 2B+D o Two bearer (64K) channels and a data (16K) channel o Uses a pair of copper wires with 148Kbps.
- Primary rate interface (PRI) o Delivered using a T1/E1 trunk o 23B+D for T1s o 30B+D for E1s

Sometimes, E1 circuits use a CAS signaling scheme called MFC/R2, which was defined by the ITU as a standard known as Q.421/Q441. This is frequently found in Latin America and Asia. Several telephony companies in these countries use customized variants of MFC/R2. Hence, you will need to know the correct country variation in order to make it work.

### ISDN BRI

Channels using ISDN BRI signalling are very popular in Europe. Most ISDN BRI cards for Asterisk supports an S/T interface with NT and TE capabilities. The TE (terminal) connection is the one used to connect to the TELCO or to other PBXs configured as network termination (NT). The NT is used to connect phones and PBXs configured as TE. ISDN BRI provides two data/voice channels and one signalling channel. ISDN BRI cards are available from several vendors of interface cards for Asterisk.

### Choosing a telephony card for your Asterisk server

There are several manufacturers for digital cards compatible with Asterisk. The choice of a card depends on some of the following factors:

#### Data bus

There are several types of bus on your PC. It is very important that you have the right card for your server. The following overview outlines the most frequently used cards:

- 32 Bits PCI 5V found in most computers, including desktops o Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400 o Sangoma A101, A102, and A104
- 32/64 bits PCI 3.3V, basically found in servers o Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
- PCI Express found on desktops and servers o Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, and AEX800 o Sangoma A101, A102, and A104

> **[2nd-ed note]** Sangoma acquired Digium in 2018. Digium-branded cards are now sold and supported under the Sangoma brand. Verify current model availability on the Sangoma website (www.sangoma.com) as some older SKUs may be discontinued.
- MiniPCI found on embedded systems o OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI), and B400M(ISDN BRI)
- USB 2.0 found in most modern PCs. Solutions based on USB allow a great density of analog and digital channels. This bus supports 480 Mbps, and each voice channel occupies 64 Kbps. When using USB hubs, it is possible to get densities up to a thousand analog ports in a single port. o Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Etherne t. The biggest advantage of Ethernet is to allow the card to be connected by more than one server. High availability solutions are usually the core application for these devices. The strength of this solution is the use of servers without free PCI slots or blade servers. o Redfone FoneBridge (up to four E1 circuits)

### Using hardware echo cancellation

Hardware echo cancellation reduces the load in the host CPU. For cards with more than a single E1 interface, hardware echo cancellation can help alleviate your processor. New enhanced software echo cancellers such as the OSLEC are reducing the need for a hardware echo canceller. To choose between hardware and software echo cancellers, you should consider the amount of processing power available in your server and the number of E1 circuits. An echo cancellation process may use up to nine MIPS (millions of instructions per second) per voice channel with 128 taps of amplitude using OSLEC (Reference: Xorcom Ltd.). If you consider 1 CPU cycle per each instruction (which is not always correct based on the processor and software implementation itself), we are speaking of 1.080 Ghz for four E1s.

#### Type of signaling

Selecting the type of signaling (e.g., T1 CAS, T1 PRI, E1 CAS R2, or E1 CAS ISDN) is not an easy task. It really depends on what you have available in your area and at what price. Common Channel Signaling (CCS) is often better than channel associated signaling (CAS). However, it is often not available. In the US, you can usually choose, as most TELCOS offer T1 CAS for regular users and T1 PRI for advanced users (e.g., call centers). In Latin America, E1 CAS R2 is prevalent, but ISDN PRI is available in some cities.

![The DAHDI software architecture: Asterisk talks to the `chan_dahdi` channel driver, which in turn loads the protocol libraries libpri (ISDN), libopenr2 (MFC/R2), and libss7 (SS7); these sit on top of the `/dev/dahdi` interface, the DAHDI kernel driver, and the card-specific interface kernel driver.](../images/10-legacy-fig09.png)

Implementing R2 is necessary for installing a library known as OpenR2 (www.libopenr2.org), developed by Moises Silva, and to patch Asterisk before the installation—a simple procedure shown later in this chapter. The library has passed several tests and is in production in several of our customers. ISDN is, in my opinion, always the best choice, if available. Some providers can have access to signaling system 7 (SS7), which is a CCS signaling available between phone companies. Proprietary and open source solutions are available for SS7. Library libss7 is used to support SS7 on Asterisk.

### Asterisk telephony channels setup

Configuring a telephony interface card involves several necessary steps. In this chapter, we will show three of the most common scenarios:

- Digital connection using ISDN PRI
- Digital connection using ISDN BRI
- Digital connection using MFC/R2

There are two ways to configure DAHDI channels. The first one is to configure it manually with full control of all parameters. The second way is to use the utility dahdi_genconf to detect and configure the cards.

#### Automatic detection and configuration

Thanks to the DAHDI development team, we now have automatic detection and configuration of the cards. Step 1: To generate the configuration automatically, use the utility dahdi_genconf, which will detect the card and generate the files /etc/dahdi/system.conf and dahdi-channels.conf.

```
dahdi_genconf
```

Step 2: In the last line of the file chan_dahdi.conf, include the file dahdi-channels.conf

```
#include dahdi_channels.conf
```

Step 3: Comment on all the unused modules in the file modules or simply use:

```
dahdi_genconf modules
```

#### Manual configuration

Another option is to configure the interfaces manually. Below are some examples of the configuration for DAHDI channels.

##### Example #1 – Two T1/ E1 channels using ISDN

Required steps:

1. TE205P or TE210P installation
2. `/etc/dahdi/system.conf` file configuration
3. DAHDI driver loading
4. `dahdi_test` utility
5. `dahdi_cfg` utility
6. `chan_dahdi.conf` file configuration
7. Asterisk load and testing

Step 1: TE205P installation. Before installing TE205P, it is important to understand the differences between the TE205P and TE210P cards. The TE210P card uses a 64-bit bus powered by 3.3 volts found almost only in the server’s motherboards. Be careful if you specify this interface card; make sure your hardware supports a 64-bit, 3.3V bus. The TE205P card uses a 5V PCI, which is often found in desktop computers. We have chosen the TE205P interface card with two spans for this example because it is easier to reduce it to one-span card or to expand it to the four-span card. These cards are now sold under the Sangoma brand (formerly Digium).

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

The configuration of TDM digital cards is a bit different from the configuration of their analog counterparts. First, we will need to configure the board spans and then the channels. Spans are numbered sequentially depending on the recognizing order of the cards. In other words, if you have more than one interface card, it is hard to know what span belongs to each one. Use dahdi_hardware to check which hardware is installed on each span. Example #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

Example #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

Example #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

Step 3: Loading kernel drivers Check which driver you need to install using dahdi_hardware.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

To load use:

```
modprobe dahdi
modprobe wct2xxp
```

Step 4: Using dahdi_test, check the missing interrupts You may verify the number of interrupt misses using the dahdi_test utility compiled with the DAHDI cards. A number below 99.987% indicates possible problems. You will find dahdi_test in

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

Step 5: Using the dahdi_cfg utility This is the correct output for dahdi_cfg for one fractional E1 (15 ports) span and two FXO ports.

```
#./dahdi_cfg –vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

Step 6: Configuration of DAHDI into the file /etc/asterisk/chan_dahdi.conf Example #1 (2xT1)

```
callerid=”John Doe”<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

Example #2 (2xE1)

```
callerid=”Flavio Eduardo” <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

Example #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Use signaling=bri_cpe_ptmp for point to multipoint BRI. Currently, BRI point to multipoint is not supported in NT mode.

#### Loading the kernel drivers

After configuring the drivers, you may simply restart the server. If you have installed DAHDI with make config, you won’t need to do anything extra. The kernel driver will be automatically loaded and configured. However, sometimes it is useful to load and unload the drivers manually. Example:

```
modprobe wct11xp
dahdi_cfg –vvvvv
```

The first command loads the driver and the second, dahdi_cfg, applies the configuration to the kernel driver.

### Troubleshooting

Sometimes things don’t work the first time. Let’s check some resources for troubleshooting DAHDI. Step 1: Check if the card is being recognized by the operation system. Sangoma/Digium cards are usually recognized as the ISDN modem.

```
lspci –v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

Step 2: Check if the kernel driver is loading correctly using:

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Step 3: Verify the status of alarms related to the physical layer of the connection. To verify the physical layer of the E1 connection, you may use the following Asterisk CLI command.

```
dahdi show status
```

The alarms indicate problems with the port: Red Alarm: Cannot maintain synchronization with the remote switch. This is usually a physical problem, such as line code or framing mismatch. Yellow alarm: Signals that the remote switch is in the red alarm. This indicates that the remote switch is not receiving your transmissions. Blue Alarm: Receives all unframed 1s on all timeslots; dahdi_tool currently does not detect a blue alarm. Loopback: The port is either in local or remote loopback

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Step 4: To detect problems with DAHDI on the Asterisk server, first check if the channels are being recognized using:

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

Step 5: Check the status of the ISDN layer 3, also known as q.931. You can check if the ISDN layer 3 is up using: `pri show spans` (to list all spans) or `pri show span <n>` for a specific span:

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

Use `pri show spans` (plural) to list the status of all configured PRI spans at once.

Check a specific channel. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1*CLI>
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x: If after everything you still have problems, start debugging the pri span. This command enables a detailed debugging of ISDN calls. It is an important command when you think that something is not correct. You can detect digits being misdialed and other problems. Below we present the example of a debugging output for a successful call. Refer to this example if you need to compare an unsuccessful call to one without problems. One tip is using core set verbose=0 to receive just the ISDN q.931 messages.

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]fice*CLI>
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### Configuration options in chan_dahdi.conf

Several options are available in the file chan_dahdi.conf. A description of all options would be boring and counterproductive. Here, we will detail the main option groups available to provide a better understanding.

#### General options (channel independent)

context: Defines the incoming context.

```
context=default
```

channel: Defines channel or channel range. Each channel definition will inherit options defined before the declaration. Channels can be identified individually or in the same line with comma separation. Ranges can be defined using “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Allows channels to be treated as a group. If you dial a group number instead of a channel number, the first channel available is used. If channels are phones, when you call a group, all phones will ring simultaneously. Using commas, you can specify more than one group for the same channel.

```
group=1
group=3,5
```

language: Turns on the internationalization and configures a language. This feature will configure system messages for a specific language. English is the only language with complete prompts available from the standard installation. musiconhold: Select music on hold class.

#### ISDN options

switchtype: Is dependent on the PBX or switch used. In Europe and Latin America, EuroISDN is common.

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: Required for some switches that need a dial plan specification. This option is ignored by many switches. The valid options are private, national, international, and unknown.

```
pridialplan = unknown
```

prilocaldialplan: Necessary for some switches, usually unknown.

```
prilocaldialplan = unknown
```

overlapdial: Overlap dialing is used when you pass digits after the connection is established. You can use block mode numbering (overlapdial=no) or digit mode (overlapdial=yes). Block mode is often used by operators. signaling: Configures the signaling type for the subsequent channels. These parameters should correspond to those in the chan_dahdi.conf file. Correct choices are based on the available channel. For ISDN you might choose five options:

- pri_cpe: Used when the device is a CPE, sometimes referred to as client, user, or slave. This is the simplest and most used form of signaling. Sometimes, when you try to connect to a private PBX, the PBX has commonly been configured as a CPE as well. In this case, use pri_net signaling in Asterisk.
- pri_net: Used when Asterisk is connected to a private PBX configured as a CPE. The signaling is often referred to as host, master, or network.
- bri_cpe: Used when Asterisk is connected as a CPE to a ISDN BRI trunk
- bri_net: Used when Asterisk is connected to an ISDN phone or PBX configured as a terminal (TE).
- bri_cpe_ptmp: Sames as bri_cpe, but in a point-to-multipoint architecture.

#### CallerID options

Many Caller ID options are available. Some can be disabled, although most are enabled by default. usecallerid: Enables or disables the Caller ID transmission for the subsequent channels (Yes/No). Note: If your system requires two rings before answering, try disabling this feature so that it will answer immediately. hidecallerid: Hides the Caller ID (Yes/No). calleridcallwaiting: Enables receiving Caller ID during a call waiting indication (Yes/No). callerid: Configures a Caller ID string for a specific channel. The caller can be configured with “asreceived” in trunk interfaces to pass the Caller ID forward.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Note: Most TELCOs mandate that you configure your correct caller ID. If you do not pass the right caller ID, you shouldn’t be able to dial out over the TELCO. On the other hand, you will be able to receive calls even without configuring the caller ID.

#### Audio quality options

These options adjust certain Asterisk parameters that affect audio quality in DAHDI channels. echocancel: Disable or enable echo cancellation. You should keep this feature enabled. It accepts “yes” or the number of taps. Explanation: How does echo canceling work? Most echo canceling algorithms operate by generating multiple copies of a received signal, with each being delayed by a small interval. This little flow is named “tap”. The number of taps determines the echo delay that can be cancelled. These copies are delayed, adjusted, and subtracted from the original signal. The trick is to adjust the delayed signal exactly to what is necessary to remove the echo. echocancelwhenbridged: Enables or disables the echo canceller during a pure TDM call. This is usually not required. rxgain: Adjusts the audio reception gain to either increase or decrease reception volume (-100% to 100%). txgain: Adjusts audio transmission gain to either increase or decrease the transmission volume (- 100% to 100%). Example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Billing options

These options change the way in which call information is recorded in the call detail records (CDR) database. amaflags: Affects the categorization of CDR. It accepts these values:

- billing
- documentation
- omit
- default

accountcode: It configures an account code for a specific channel. It can contain any alphanumeric value, usually the department or user name.

```
accountcode=finance
amaflags=billing
```

### MFC/R2 configuration

MFC/R2 is used in several countries in Latin America, China, and Africa as well as some European countries. ISDN is superior and preferred if available in your area.

#### Understanding the problem

The card used to signal MFC/R2 is the same used to signal ISDN. It’s possible to use MFC/R2 on DAHDI channels using the library called libopenR2 (www.libopenr2.com). This library was not part of versions of Asterisk prior to 1.6.2.

##### Understanding the MFC/R2 protocol

The MFC/R2 protocol combines in-band and out-of-band signaling. Address signaling is forwarded in-band using a set of tones while channel information is transmitted over timeslot 16 as out-of-band signaling.

**Line Signaling (ITU-T Q.421).** In timeslot 16, each voice channel uses four ABCD bits to signal its states and call control. Bits C and D are rarely used. In some countries, they can be used for metering (pulse metering for billing). In a normal conversation, we have both sides working: the caller and the called side. Signaling from the caller side is referred to as forward signaling while the called side uses backward signaling. We will designate Af and Bf for forward signaling and Ab and Bb for backward signaling.

| State | ABCD forward | ABCD backward |
| --- | --- | --- |
| Idle/Released | 1001 | 1001 |
| Seized | 0001 | 1001 |
| Seize Ack | 0001 | 1101 |
| Answered | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (before clear-back) | 1001 | 0101 |
| ClearFwd (disconnection confirmation) | 1001 | 1001 |
| Blocked | 1001 | 1101 |

MFC/R2 was defined by the ITU. Unfortunately, several countries customized the standard to their own needs. As a result, variations emerged in standards between countries.

**Inter-register signals (ITU-T Q.441).** MFC/R2 signaling uses a combination of two tones. The tables below show the ITU standard.

Signal group I (forward):

| Description | Forward signal |
| --- | --- |
| Digit 1 | I-1 |
| Digit 2 | I-2 |
| Digit 3 | I-3 |
| Digit 4 | I-4 |
| Digit 5 | I-5 |
| Digit 6 | I-6 |
| Digit 7 | I-7 |
| Digit 8 | I-8 |
| Digit 9 | I-9 |
| Digit 0 | I-10 |
| Country code indicator, outgoing half-echo suppressor required | I-11 |
| Country code indicator, no echo suppressor required | I-12 |
| Test call indicator | I-13 |
| Country code indicator, outgoing half-echo suppressor inserted | I-14 |
| Not used | I-15 |

Signal group II (forward):

| Description | Forward signal |
| --- | --- |
| Subscriber without priority | II-1 |
| Subscriber with priority | II-2 |
| Maintenance equipment | II-3 |
| Spare | II-4 |
| Operator | II-5 |
| Data transmission | II-6 |
| Subscriber or operator without forward transfer facility | II-7 |
| Data transmission | II-8 |
| Subscriber with priority | II-9 |
| Operator with forward transfer facility | II-10 |
| Spare | II-11 |
| Spare | II-12 |
| Spare | II-13 |
| Spare | II-14 |
| Spare | II-15 |

Signal group A (backward):

| Description | Backward signal |
| --- | --- |
| Send next digit (n+1) | A-1 |
| Send last but one digit (n-1) | A-2 |
| Address complete, changeover to reception of Group B signals | A-3 |
| Congestion in the national network | A-4 |
| Send calling party’s category | A-5 |
| Address complete, charge, set-up speech conditions | A-6 |
| Send last but two digit (n-2) | A-7 |
| Send last but three digit (n-3) | A-8 |
| Spare | A-9 |
| Spare | A-10 |
| Send country code indicator | A-11 |
| Send language or discrimination digit | A-12 |
| Send nature of circuit | A-13 |
| Request information on use of echo suppressor | A-14 |
| Congestion in an international exchange or at its output | A-15 |

Signal group B (backward):

| Description | Backward signal |
| --- | --- |
| Spare | B-1 |
| Send special information tone | B-2 |
| Subscriber’s line busy | B-3 |
| Congestion (after changeover group A to B) | B-4 |
| Unallocated number | B-5 |
| Subscriber’s line free, charge | B-6 |
| Subscriber’s line free, no charge | B-7 |
| Subscriber’s line out of order | B-8 |
| Spare | B-9 |
| Spare | B-10 |
| Spare | B-11 |
| Spare | B-12 |
| Spare | B-13 |
| Spare | B-14 |
| Spare | B-15 |

#### MFC/R2 sequence

The following sequence illustrates a call originating from an Asterisk’s extension to a terminal in the PSTN. The PSTN drops the call and ends the communication.

![A complete MFC/R2 call flow between Asterisk and the telco: line signaling (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) is exchanged in timeslot 16, the dialed digits and backward "send next digit" signals (groups I/A/B) travel in-band, and the audible tones reach the subscriber.](../images/10-legacy-fig11.png)

### How to use the driver libopenr2

The project initiated by Moises Silva was inspired on the Unicall channel driver written by Steve Underwood. The OpenR2 library is currently the most stable software solution for Asterisk. With this solution, we may use any digital card compatible with DAHDI. Previously, only proprietary solutions were available for MFC/R2, one of the best I have used is the one made available by Khomp, www.khomp.com.br. In Asterisk 22, MFC/R2 support via libopenR2 is built in when the library is present at compile time — no external patch is required. The steps below show the historical manual installation for reference; on modern systems, install `libopenr2-dev` from your distribution's package manager before running `./configure`, then enable `chan_dahdi` in `make menuselect`.

> **[2nd-ed note]** The patched Asterisk 1.4 tree from the 1st edition is obsolete; for Asterisk 22, MFC/R2 support via libopenr2 is integrated in the main source tree, and the steps below now use the current Git repositories instead of the retired `svn.digium.com`. Consider condensing these historical build steps for the final edition.

Step 1: Check the patches for the version of Asterisk you want to install.

```
apt-get install git
```

Step2: Download the modified Asterisk code with the patch installed.

> **[2nd-ed note]** The original Asterisk 1.4 SVN patch tree has been replaced below by the current Git repositories. On Asterisk 22 the MFC/R2 patch is unnecessary — `chan_dahdi` builds R2 support directly against libopenr2 — so you only need the openr2 library plus a normal Asterisk build.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Step 3: Compile and install Please, BACK UP your server before proceeding.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note: Do not execute “make samples” to avoid overwriting your configuration files.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Let’s suppose you have a card with one E1 interface.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Step 5: Run the command dahdi_cfg to apply the changes to the driver:

```
dahdi_cfg –vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

Step 5: Change the file chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Step 6: Change the dial plan in the file extensions .conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Note: Some TELCOS do not accept calls without the caller ID. Please set the caller ID to one of the DID numbers assigned by the operator. In some countries, this step is not required. Step 7: Test the solution: Now, with an extension in the context from-internal, call any number and observe the console. Check to see if any errors are occurring. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Debugging OpenR2

To detect errors in the calls, you can activate the debug. To do this, follow the steps below. Step 1: Edit the file chan_dahdi.conf and add the following three lines to the configuration:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

Step 2: Restart the Asterisk server Step 3: Test the call and check the call files at /var/log/asterisk/mfcr2/span1 Below is a trace for a normal call. Compare it to what you receive in your call.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### MFC/R2 Configuration

The options are documented within the file chan_dahdi.conf. Some of the most important options are detailed here. Mandatory parameters: mfcr2_variant, mfcr2_max_ani and mfcr2_max_dnis. mfcr2_variant: Country variant.

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani: Max amount of ANI digits to ask for mfcr2_max_dnis: Max amount of DNIS digits to ask for mfcr2_get_ani_first: Whether or not to get ANI before DNIS (required by some TELCOS) mfcr2_category: Caller category. You can set the variable MFCR2_CATEGORY before starting the call mfcr2_logdir: Directory to log the call files. (/var/log/asterisk/mfcr2/directory) mfcr2_call_files: Whether or not to log the calls

- mfcr2_logging: logging values
- cas – ABCD bits for tx and rx
- mf – Multifrequency tones
- stack – verbose output of the channel and context stack
- all – all activities
- nothing – do not log anything

mfcr2_mfback_timeout: This value deserves to be mentioned. Sometimes if you are calling a cell phone or any call that takes a long time to complete, this parameter can time out, so it is often changed for fine tuning. If some of your calls are not being completed, this is the parameter you should change first. mfcr2_metering_pulse_timeout: Pulses are used by some R2 variants to indicate costs mfcr2_allow_collect_calls: In Brazil, the tone II-8 is used to indicate a collect call; this parameter allows you to block collect calls. mfcr2_double_answer: Also used to avoid collect calls when a double answer is required. With double_answer=yes you actually block the collect calls. mfcr2_immediate_accept: Allows you to skip the use of group B/II signals and go directly to the accepted state. mfcr2_forced_release: Allows you to speed up the release of the call; works for the Brazilian variant.

#### ANI and DNIS

Automatic Number Identification (ANI) is the caller’s number. Dialed Number Identification Service (DNIS ) is the number called or, in other words, the number dialed. When a call is received, usually the last four numbers are passed to the PBX in a process referred to as direct inward dial (DID). The ANI number is actually the Caller ID. ANI will have the caller’s extension when dialing while DNIS will contain the call destination. It is important that these parameters be configured correctly. Some switches send just the last four digits while others send the complete number.

### DAHDI channel format

DAHDI channels use the following format in the dial plan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

Examples:

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
[g] – Group identifier
[c] – Answer confirmation; A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

## The IAX2 protocol

In this chapter, we will learn about the Inter-Asterisk eXchange (IAX) protocol, including its strengths and weaknesses. Details such as trunk mode and the interconnection of two Asterisk servers will also be covered. All references in this document correspond to IAX version 2. The IAX protocol provides media transport and signaling for voice and video. IAX is very innovative; it saves bandwidth in trunk mode and is much simpler than SIP when you need to traverse NAT. The primary use for IAX nowadays is to interconnect Asterisk servers. IAX was created primarily for voice, but it can also accommodate video and other multimedia streams. IAX was inspired from other VoIP protocols, such as SIP and MGCP. Instead of using two separate protocols for signaling and media, IAX unified them to make a unique protocol. IAX does not use RTP for media transport; instead, it embeds the media in the same UDP connection.

> **[2nd-ed note — Status in Asterisk 22]** `chan_iax2` is still included and fully supported in Asterisk 22 LTS, so everything in this chapter remains valid. However, IAX2 is now a legacy protocol and sees relatively little new deployment. The VoIP industry has largely converged on SIP (via `chan_pjsip` in Asterisk 22) for both provider trunking and server interconnection. IAX2's primary remaining selling point is its **single-port NAT traversal**: all signaling and media flow over a single UDP port (4569 by default), which greatly simplifies firewall and NAT configuration compared to SIP + RTP. If you are building a new Asterisk-to-Asterisk trunk and NAT is not a concern, PJSIP trunks are the recommended modern approach. IAX2 is kept here because it is still a valid choice, especially in environments where only one UDP port can be opened through a firewall.

### Objectives

By the end of this chapter, you should be able to:

- Identify strengths and weakness of IAX protocol
- Describe usage scenarios for the IAX protocol
- Describe the advantages of IAX trunk mode
- Configure iax.conf for phones
- Configure iax.conf for connection to a VoIP provider
- Configure iax.conf for Asterisk interconnection
- Understand IAX authentication

### IAX design

The main objectives for IAX design are:

- To reduce the bandwidth required for media transport and signaling
- To provide NAT transparency
- To be able to transmit the dial plan information
- To support the efficient use of paging and intercom

IAX is a peer-to-peer signaling and media protocol that is similar to SIP without using RTP. The basic approach is to multiplex the multimedia streams over a single UDP connection between two hosts. The greatest benefit of this approach is its simplicity when traversing connections over NAT, regularly found in xDSL modems. IAX uses a single port, UDP 4569 by default, and then uses a call number with 15 bits to multiplex all streams. The IAX protocol uses registration and authentication processes similar to the SIP protocol. A description of the protocol can be found at http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![The IAX protocol multiplexes many calls between two endpoints over a single UDP port (4569 by default), using a 15-bit call number to keep the streams apart — which makes NAT traversal simple.](../images/10-legacy-fig12.png)

### Bandwidth usage

The bandwidth used in VoIP networks is affected by several factors; codecs and protocol headers are the most important. The IAX protocol has a surprising feature called trunk mode, whereby it multiplexes several calls using a single header. By playing with the Asterisk bandwidth calculator, you will see how IAX trunks can save you up to 80% of the traffic with multiple calls.

![Comparing IAX and SIP overhead: two SIP/RTP calls need two packets (40 bytes of payload carried under 156 bytes of overhead), while IAX2 trunk mode carries both calls in a single packet (40 bytes of payload under just 66 bytes of overhead) by sharing one IP/UDP header across many mini-frames.](../images/10-legacy-fig13.png)

### Channel naming

It is important to understand channel-naming conventions as you will use these names when specifying a channel in the dial plan. The format of an IAX channel name used for outbound channels is:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

<user> UserID on remote peer, or name of client configured in iax.conf <secret> The password. Alternatively it can be the filename for an RSA key without the trailing extension (.key or .pub) and enclosed in square brackets <peer> Name of server to connect to <portno> Port number for connection <exten> Extension in the remote Asterisk server <context> Context in the remote Asterisk server <options> The only option available is ‘a’ meaning ‘request autoanswer’

#### Outbound channels example:

Outbound channels are seen in the Asterisk console. IAX2/8590:secret@myserver/8590@default Call the 8590 extension in myserver. It uses 8590:secret as the name/password pair

IAX2/iaxphone Call "iaxphone" IAX2/judy:[judyrsa]@somewhere.com Call somewhere.com using judy as the username and a RSA key for authentication

#### The format of an incoming IAX channel is:

Inbound channels are seen in the Asterisk console.

```
IAX2/[<username>@]<host>]-<callno>
```

<username> Username if known <host> Host connecting <callno> Local call number Incoming channel example: IAX2[flavio@8.8.30.34]/10 Call number 10 from IP address 8.8.30.34 using flavio as the user. IAX2[8.8.30.50]/11 Call number 11 from IP address 8.8.30.50.

### Using IAX

You may use IAX in several ways. In this section, we will show you how to configure IAX for several scenarios, including:

- Connecting a soft-phone using IAX
- Connecting IAX to a VoIP provider using IAX
- Connecting two servers using IAX
- Connecting two servers using IAX in trunk mode
- Debugging an IAX connection
- Using RSA pair keys for authentication

#### Connecting a soft-phone using IAX

Asterisk supports IP phones based on IAX such as the ATCOM and the old ATA from Digium (called IAXy) as well as soft-phones that still implement the IAX2 protocol. The process for soft-phones, ATAs, and hard- phones is similar. To configure an IAX device, you need to edit the iax.conf file in /etc/asterisk

```
directory.
```

We will use an IAX2-capable soft-phone as an example. Step 1: Make a backup of the original iax.conf file using:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

Step 2: Start editing a new iax.conf file:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; Very important parameter, it changes the codecs available

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

I’ve tried to preserve the default (non-commented) lines of the sample file. The following parameters were modified:

```
bandwidth=high
```

This line affects the codec selection. Using the high setting allows for the selection of a high bandwidth and a high quality codec such as g.711 defined by the ulaw keyword. If you keep the default parameter, you will not be able to choose ulaw. In this case, Asterisk will give you the message “no codec available” for the configuration below.

```
disallow=all
allow=ulaw
```

In the commands described above, we disabled all codecs and enabled just ulaw. In LANs, most people prefer to use ulaw because it is not processor-intensive and saves CPU cycles. Even using more bandwidth, this codec is preferable because in LANs you usually have a 100-megabits Ethernet or even a Gigabit. A voice call using ulaw uses almost 100 kilobits per second of bandwidth from your network, which is a very light use for today’s high-speed LANs. In WAN or Internet networks, you will usually disable ulaw, trading some available CPU cycles by voice compression for better bandwidth use. The codecs gsm , g729, and ilbc provide a good compression factor as well.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

In the above commands, we have defined a friend named [2003]. The context is the default (in the first labs we always use the default context to avoid confusion; this context will be fully explained in chapter 9). The line “host=dynamic” provides a dynamic registration of the phone’s IP address. Step 3: Download and install an IAX2-capable soft-phone. You can choose any soft-phone that still supports the IAX2 protocol for the lab. Step 4: Configure an IAX account in the client (typically *Add account* → IAX). Note that the SipPulse Softphone is SIP-only and cannot register over IAX2, so for IAX testing you need a client that still supports the protocol.

Step 5: Configure the extensions.conf file to test your IAX device.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Connecting to a VoIP provider using IAX

A few VoIP providers support IAX. You can easily find an IAX provider by searching for “IAX providers”. Using an IAX provider makes a lot of sense as IAX can save a lot of bandwidth, easily traverses NAT, and can authenticate using RSA key pairs.

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

> **[2nd-ed note]** The number of IAX-capable commercial VoIP providers has declined significantly since Asterisk 16. Most providers now offer SIP/PJSIP trunks exclusively. Before choosing an IAX provider, confirm they actively maintain their IAX infrastructure. For new provider integrations, a PJSIP trunk is the recommended alternative.

#### Connecting to a provider using IAX

Step 1: Open an account in your favorite provider. Your provider will provide you three things.

- Name
- Secret
- IP address or Host name
- RSA public key

Step 2: Configure the iax.conf file to register your Asterisk with your provider. Add the following lines to the [general] section of the file.

```
[general]
register=>name:secret@hostname/2003
```

In the instructions described above, you registered with your provider using your account and password. The moment you receive a call, it will be forwarded to the 2003 extension.

```
[name]
```

- ; Your account name or number

```
type=peer
secret=secret
; Your password
host=hostname
```

In the instructions described above, we have created a peer corresponding to the provider for dialing purposes.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

This is required for RSA authentication. Using the public key from your provider allows you to be sure that the call being received is really from the true provider. If anyone else tries to use the same path, they will not be able to authenticate it because they do not have the corresponding private key. Step 4: Try the connection. To test the connection, call any number. Some vendors provide an echo test. To accomplish this, please edit the file extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Go to the Asterisk CLI and issue a reload. To verify if Asterisk is registered with the provider, use the next command.

```
CLI>reload
CLI>iax2 show register
```

Now simply dial *98 on the soft-phone connected to the Asterisk server.

#### Connecting two Asterisk servers through an IAX trunk

It is very easy to connect one server to another. You won’t need to register them because the IP addresses are already known. You will have to create the peers and users in the iax.conf file. All extensions in the HQ site start with 20 followed by two digits (e.g., 2000). In the Branch, all extensions start with 22 followed by two digits (e.g., 2200). We will use the trunk. You will need a DAHDI timing source to enable this feature. Step 1: Edit the iax.conf file in the Branch server.

![Connecting two Asterisk servers with an IAX trunk: the HQ server (192.168.1.1, extensions 20xx) and the Branch server (192.168.1.2, extensions 22xx) reach each other over a single IAX trunk — no registration is needed because both IP addresses are fixed and known.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

Step 2: Configure the file extensions.conf in the Branch server

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

Step 3: Configure the iax.conf file in the HQ server

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

Step 4: Configure the extensions.conf file in the HQ server.

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field “username=”) or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well. If a user is provided, Asterisk: 1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection. 2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses. 3. It checks the password (secret) using plaintext, md5, or RSA. 4. It accepts the connection and sends the call to the context specified in the line “context=” from the iax.conf file. If a username is not provided, Asterisk: 1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user’s name. 2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user’s name. Let’s suppose your iax.conf file has the following entries:

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

If a call has a specified username, such as:

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk will try to authenticate the call using only the corresponding entry in the iax.conf file. If any other names are specified, the call would be rejected. If no user is specified, Asterisk will try to authenticate the connection as guest. However, if guest does not exist, it will try any other connections with a matching secret. In other words, if you don’t have a guest section in your iax.conf file, a malicious user could try to guess any matching secret by not specifying the user name. IP addresses’ deny/allow restrictions apply too. A good way to avoid secret guessing is to use RSA authentication. Another method is to restrict the IP addresses allowed to call in.

#### IP address restrictions

permit = <ipaddr>/<netmask> Rules are interpreted in sequence, and all are evaluated (this concept is different from ACLs deny = <ipaddr>/<netmask> usually found in routers and firewalls). Example #1 permit=0.0.0.0/0.0.0.0 deny=192.168.0.0/255.255.255.0 Will deny any packet from 192.168.0.0/24 network Example #2 deny=192.168.0.0/255.255.255.0 permit=0.0.0.0/0.0.0.0 It will permit any packet. The last instruction supersedes the first.

#### Outbound connections

Outbound connections acquire authentication information using the following methods:

- The IAX2 channel description passed by the dial() application.
- An entry with type=peer or type=friend in the iax.conf file.
- A combination of both methods.

#### Connecting two Asterisk servers using RSA keys

It is possible to use IAX with strong authentication using asymmetric RSA keys. According to the source code (res_krypto.c), Asterisk uses RSA keys with an SHA-1 algorithm for message digests instead of the weaker MD5. Below is a step-by-step guide for setting up two servers using RSA keys.

##### Configuring the server for the branch

Step 1: Generate the RSA keys in the branch server

```
astkeygen –n
```

When asked, use the key name branch. We have used the parameter –n to avoid passing a passphrase whenever Asterisk reinitializes. If you want to improve the security, don’t use the –n and start Asterisk with asterisk -i Step 2: Copy the keys to the directory /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

Step 3: Copy the public key to the HQ server

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Step 4: Edit the iax.conf file in the Branch server.

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

Step 8: Configure the extensions.conf file in the Branch server

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Configuring the server for the headquarters

Step 1: Generate the RSA keys in the HQ server

```
astkeygen –n
```

When asked use the key name hq. Step 2: Copy the keys to the directory /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

Step 3: Copy the public key to the BRANCH server

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

Step 4: Configure the iax.conf file in the HQ server

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

Step 10: Configure the extensions.conf file in the HQ server.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses bindport = <portnum> Configures the IAX UDP port. Default is 4569. bindaddr = <ipaddr> Use 0.0.0.0 to bind Asterisk to all interfaces or specify the IP address of a specific interface. Codec selection bandwidth = [low|medium|high] High = all codecs Medium = all codecs except ulaw and alaw Low = low bandwidth codecs allow/disallow = Codec selection fine tuning [alaw|ulaw|gsm|g.729| etc.]

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### IAX2 Encryption

IAX supports call encryption using a symmetric key, 128-bit block cipher called AES (Advanced Encryption Standard). It is very simple to activate the encryption between IAX trunks. In the file iax.conf use:

```
encryption=yes
```

To force the encryption:

```
forceencryption=yes
```

To guarantee compatibility with older versions, you may need to disable key rotation using:

```
keyrotate=no
```

### IAX2 debug commands

Below are some of the most important troubleshooting console commands for Asterisk.

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

Looking at this output, identify the beginning and end of the call. Observe the delay and jitter information obtained using poke and pong packets. These packets help create the output of the “iax2 show netstats” command.

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

To turn off debugging, use:

```
vtsvoffice*CLI>iax2 no debug
```

### Summary

This chapter has reviewed the strengths and weaknesses of the IAX protocol. It has demonstrated how IAX works in several scenarios, such as soft-phones and a trunk between two Asterisk servers. Trunk mode allows you to save bandwidth by carrying more than one call in a single packet. Finally, you learned console commands that you can use to check the status and debug the protocol.

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

Step 2: Configure the [peer] on sip.conf Create an entry of peer type to the desired provider to simplify Asterisk’s dialing.

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

Step 3: Create a route to the provider in the dial plan We will choose the digits 010 as the destination route to the provider. To dial #610000 inside the provider, simply dial 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)=”Flavio Gonçalves”)
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### SIP options specific to the provider scenario

The following discussion examines the details of the options set in the sip.conf file for connection to a VoIP provider.

```
register=>username:password@hostname/4100
```

The instruction registered in the sip.conf file is used to register with a provider. The register transaction is authenticated with the name and secret. You can use a slash (“/”) to provide an extension for incoming calls. Technically speaking, the extension will be placed in the “Contact” header field of the SIP request. The registering behavior can be controlled by certain parameters:

```
registertimeout=20
registerattempts=10
```

To check if registration was successful, the legacy console command was `sip show registry`. On Asterisk 22 the equivalent command is `pjsip show registrations` (outbound registrations) and `pjsip show endpoints` for endpoint status.

The parameter “username” is used in the authentication digest. The digest is computed using username, secret, and realm:

```
username=username
```

Host defines the VoIP provider address or name:

```
host=hostname
```

The parameters Fromuser and Fromdomain are sometimes required for authentication. These parameters are used in the SIP From header field:

```
fromuser=username
fromdomain=hostname
```

When you connect to a VoIP provider, credentials are required. After the initial invite, the provider sends you a message called “407 Proxy Authentication Required”; you provide the credentials in the subsequent INVITE message. For incoming calls, your Asterisk server will ask for credentials for the provider. Obviously, the provider does not have a valid credential for your Asterisk server. When you use insecure=invite, you are telling Asterisk not to send the “407 Proxy Authentication Required” to the provider and to accept incoming calls. You can also use insecure=port, invite to match the peer based on the IP address without matching the port number.

```
insecure=invite, port
```

### Connecting two Asterisk servers together using SIP (sip.conf)

You can use SIP to interconnect two Asterisk boxes. It is important to pay attention to the dial plan before moving on with this configuration. Users generally want to connect other PBXs with minimal effort. The idea here is to use an extension number only to connect to the other PBX. Step 1: Edit the sip.conf file in server A:

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

Step 2: Edit the sip.conf file in server B:

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![Connecting two Asterisk servers using SIP: server A (extensions 4400/4401) and server B (extensions 4500/4501) exchange SIP signaling so users on each PBX can dial the other](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

Step 3: Edit the extensions.conf file in server A:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Step 4: Edit the extensions.conf file in server B:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk domain support (sip.conf)

The SIP protocol follows the Internet architecture. The first thing to do before configuring SIP is to correctly set the DNS servers. In a SIP environment, you can call a user located in any SIP proxy, and other users can call you as well using your SIP Uniform Resource Identifier (URI). To set a DNS server for SIP, you have to add SRV records to your DNS server.

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

After configuring the DNS, you can use the URI, which points to a SIP user, SIP phone, or telephone extension. A SIP URI looks similar to an email address (e.g., sip:chuck@yourpartnerdomain.com). Using SIP URIs, no telephone number is needed to make a call from one SIP phone to another. To dial an external user, simply use a statement as the one shown below.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Certain parameters can control domain behavior.

```
srvlookup=yes
```

This parameter enables DNS SRV lookups on outbound calls. Using this parameter, it is possible to dial calls using SIP names based on domain.

```
allowguest=yes
```

This parameter allows an external invite to be processed without authentication. It processes the call within the context defined in the general section or in the domain statement. Warning: If you define a context in the general section with access to PSTN, an external user can dial the PSTN over your PBX. In this case, you will incur any charges. Allow only your own extensions in the context defined in the general section.

![Connecting to other SIP servers by domain: youdomain.com and yourpartnerdomain.com exchange SIP signaling, so users such as lee and bruce can call chuck and norris using SIP URIs](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

The domain command allows you to handle more than one domain within Asterisk. If a call comes from one specific domain, it is directed to a specific context.

```
;autodomain=yes
```

This parameter includes the local IP and hostname in the allowed domains.

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Step 2: Now configure the soft-phone to use presence. We will show you how to configure the SipPulse Softphone.

- Sequence: right-click->SIP Account Settings->Properties->Presence
- Change the presence model from peer-to-peer to presence agent, which will make the soft-phone subscribe Asterisk for SIP events.

Step 3: Add the contact to other soft-phones. In this example, the SipPulse Softphone is account 2000, so we will add a contact for account 2001. Sequence: Open the right panel (presence panel in the softphone)->Click in Contacts->Add a contact. Fill the name 2001. Display as 2001 and don’t forget to check the box Show this contact’s availability.

Step 4: Now call extension 2001 and check the status of the phone in the right panel of the soft-phone. Use the console command `core show hints` to see the presence status changing in the server (in legacy chan_sip, `sip show inuse` showed how many calls you had on each line). On Asterisk 22, use `pjsip show endpoints` to inspect endpoint and channel state. The presence/BLF status appears in the softphone's contacts or BLF panel — exactly how it is shown depends on the client.

#### Codec configuration

Codec configuration is simple and straightforward. You can set the words allow and disallow in the [general] section or peer/user section. The best practice is to standardize the codec to avoid transcoding, which is processor intensive. Please use the same codec for messages and prompts.

```
[general]
disallow=all
allow=g729
```

#### DTMF options

On certain occasions, you will pass digits to an application such as voicemail or interactive voice response (IVR). It is important to pass DTMF correctly. The simplest method for passing DTMF is called inband. It is set in the [general] or peer/user section of the sip.conf file. When you set dtmfmode=inband, DTMF tones are generated as sounds in the audio channel. The main issue with this method is that, when you compress the audio channel using a codec such as g729, sounds are distorted and DTMF tones are not properly recognized. If you are planning to use dtmfmode=inband, use the g.711 codec (ulaw and alaw).

```
dtmfmode=inband
```

Another approach is to use RFC2833, which allows you to pass DTMF tones as named events in the RTP packets.

```
dtmfmode=rfc2833
```

Finally, you can pass DTMF digits inside SIP packets, instead of RTP packets. This method is defined in the RFC3265 (signaling events) and RFC2976.

```
dtmfmode=info
```

Following the release of version 1.2, it is now possible to use:

```
dtmfmode=auto
```

This tries to use the RFC2833; if it is not possible, use band tones.

#### Quality of service (QoS) marking configuration

QoS is a set of techniques responsible for voice quality. QoS is implemented in such a way as to reduce bandwidth, latency, and jitter. The main QoS functions are packet scheduling, fragmentation, and header compression. QoS is implemented in switches and routers, not by Asterisk itself. However, Asterisk can help routers and switches by marking packets for express delivery. Marking is done using differentiated services code points (DSCP) defined in RFCs 2474 and RFC2475.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

Starting from version 1.4, you can specify different codes for signaling (SIP), audio (RTP), and video (RTP).

### SIP authentication (sip.conf)

When legacy `chan_sip` received a SIP call, it followed the rules described in the following diagram. Three parameters played an important role in SIP authentication. On Asterisk 22, authentication is configured instead with PJSIP `auth` objects (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenced by an endpoint, and IP access control is done with `permit=`/`deny=` on the endpoint or via an `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

This parameter controls whether a user without a corresponding peer can authenticate without a name and secret. We discussed this parameter in the domain support section.

```
insecure=invite,port
```

When we use insecure=invite, Asterisk does not generate the message “407 Proxy Authentication Required”. Without this message, the user can make a call without authentication. This is often used to connect to VoIP service providers. The calls coming from the VoIP service provider are usually not authenticated.

```
autocreatepeer=yes/no
```

This command is used when Asterisk is connected to a SIP proxy. It dynamically creates a peer to each call. When this option is enabled, any UAC can connect to the Asterisk server. It is important to limit the IP connection to the SIP proxy. The SIP proxy, in turn, takes care of access control. Peer configuration is based on the general options as well as the “Contact” header field of the SIP packet. Warning: Use this with extreme caution as it completely opens Asterisk.

```
secret=secret, remotesecret=secret
```

This parameter configures the secret for authentication use secret for inbound requests and remotesecret for outbound requests. If you do not want to present the secrets in text files, you can use md5secret to include a hash instead of the secret. To generate the MD5 secret, you can use:

```
echo –n “username:realm:secret” |md5sum
```

Then use the following statement:

```
md5secret=0b0e5d467890....
```

Warning: Do not forget to use the –n parameter; the carriage return will be used in the md5 computation.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

The statements above will deny all IP addresses and allow UAC only from the local network (192.168.1.0/24).

#### RTP options

It is possible to control some RTP parameters.

```
rtptimeout=60
```

This terminates calls without RTP activity for more the 60 seconds when not in hold.

```
rtpholdtimeout=120
```

This terminates calls without RTP activity even on hold (should be bigger than rtptimeout).

### SIP NAT traversal (sip.conf)

The NAT *theory* (the four NAT types, the Contact-header problem, keep-alives, and forcing media through the server) is protocol-level and is covered in the *SIP & PJSIP in depth* chapter. The `sip.conf` parameters shown here (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) are **legacy chan_sip** and were removed in Asterisk 21+. On PJSIP these map to transport/endpoint settings such as `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address`, and `local_net=` on the transport, plus `qualify_frequency=` on the AOR.

In legacy chan_sip, the parameter `nat` had five options:

- nat = no — Do no special NAT handling other than RFC3581
- nat = force_rport — Pretend there was an rport parameter even if there wasn't
- nat = comedia — Send media to the port Asterisk received it from regardless of where the SDP says to send it.
- nat = auto_force_rport — Set the force_rport option if Asterisk detects NAT (default)
- nat = auto_comedia — Set the comedia option if Asterisk detects NAT

When you put the statement “nat=force_rport” in the sip.conf file, you are telling Asterisk to ignore the address contained in the “Contact” header field of the SIP header and use the source IP address and port in the packet’s IP header and also to send the media back to the address from where it was received ignoring the content of the SDP header.

```
nat=force_rport,comedia
```

It is necessary to keep the NAT mapping open. If NAT times out, Asterisk cannot send an invite to the UAC. The UAC is able to send calls, but not receive any. The following statement can be used to keep NAT open.

```
qualify=yes
```

Qualify will send a SIP packet using the OPTIONS method regularly, which will help keep NAT open. Qualify sends an OPTIONS each 60 seconds and every 10th second when the host is not reachable. You can use “sip show peers” to see the latency for the peers. If the user’s NAT is of the symmetric type, it is not possible to send packets from one UAC to another directly; in that case you have to force the RTP through Asterisk using:

```
directmedia=no
```

#### Asterisk behind NAT (sip.conf)

All the previous scenarios assume that the Asterisk server has an external (valid) Internet address. Sometimes the Asterisk server is implemented behind a firewall with NAT. In this case, it is necessary to do some extra configurations.

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

Step 1: Configure the firewall to redirect the UDP port 5060 statically to the Asterisk server. Step 2: Configure the firewall to redirect the UDP ports from 10000 to 20000 statically. If you want to restrict the number of opened ports, you can edit the rtp.conf file to change the RTP port range. Another way is to use an intelligent firewall that supports the SIP protocol to open the RTP ports dynamically.

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

Step 3: Configure Asterisk to include the external address in the header fields of the SIP packets including Session Description Protocol (SDP). You can accomplish this by adding the following two statements to the sip.conf file:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

The first parameter externaddr tells Asterisk to include the external IP address inside the SIP headers for external destinations. The second parameter localnet allows Asterisk to differentiate between external and internal addresses. Optionally, you can use externhost if you use a Dynamic DNS with a DHCP address on the server.

### SIP dial strings (chan_sip)

The `SIP/...` dial-string technology shown below is the removed chan_sip driver. On Asterisk 22 use the `PJSIP/...` technology instead — for example `Dial(PJSIP/2000)` or `Dial(PJSIP/${EXTEN}@provider)`. The forms and meaning are otherwise analogous.

You can call a legacy SIP destination using different dial strings:

```
SIP/peer
```

- ; Need to have a defined peer in sip.conf

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Examples include:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migrating a legacy chan_sip system to PJSIP

Because `chan_sip` was removed in Asterisk 21 and is gone in Asterisk 22, any
existing `sip.conf` deployment must be migrated to PJSIP. The biggest conceptual
shift is that a single `sip.conf` `[peer]` or `[friend]` is split into several
PJSIP objects, each with a `type=`: an **endpoint** (call/codec/media settings),
one or more **aor** objects (where the device can be reached / registration),
an **auth** object (credentials), and a shared **transport** (the listening
socket, NAT addresses). The following table maps the most common concepts.

| Legacy sip.conf concept | PJSIP equivalent (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (referenced via `auth=` and `aors=`) |
| `type=friend` / `type=peer` / `type=user` | a single `type=endpoint` (PJSIP has no friend/peer/user distinction) |
| `host=dynamic` (device registers) | `type=aor` with `max_contacts=1`; the device REGISTERs to update its contact |
| `host=<ip/hostname>` (static) | `type=aor` with a static `contact=sip:host:port` |
| `register=>user:secret@host/ext` (outbound) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` on the endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` on the endpoint (same syntax) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — also `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` on the endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (seconds) on the **aor** |
| `externaddr=` | `external_media_address=` and `external_signaling_address=` on the **transport** |
| `localnet=` | `local_net=` on the **transport** |
| `insecure=invite` (provider, no auth) | omit `auth=`/`outbound_auth=` and use `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (use with care) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (and `cos_audio` / `cos_video`) on the endpoint |

A registering extension that looked like this in legacy `sip.conf`:

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

becomes the following in `pjsip.conf` on Asterisk 22:

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### The sip_to_pjsip.py conversion script

Asterisk ships a helper script, **`sip_to_pjsip.py`**, that reads an existing
`sip.conf` and produces a `pjsip.conf`. You can run it directly in the
/etc/asterisk directory. The utility is in the Asterisk source tree under
`contrib/scripts/sip_to_pjsip/`, where `${PATH_TO_ASTERISK_SOURCE}` is the path
where the Asterisk source files are found (usually /usr/src/asterisk-22.x.y/):

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

If you run it with the `--help` option you will see its options:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

It also accepts optional positional arguments — `[input-file [output-file]]`,
defaulting to `sip.conf` and `pjsip.conf` in the current directory.

Treat its output as a **starting point**: review every generated object,
especially transports, NAT settings, and codec lists, and test thoroughly before
going to production.

Let’s migrate the sip.conf in our companion labs at VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.api4com.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.api4com.com
fromuser=1020
fromdomain=sip.api4com.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.api4com.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.api4com.com
client_uri = sip:1020@sip.api4com.com:5600
server_uri = sip:sip.api4com.com:5600
[auth_reg_sip.api4com.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.api4com.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.api4com.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.api4com.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

While the conversion seems ok, we can see that some elements such as qualify=yes cannot be mapped directly. To fix you have to add to the aor section the command qualify_frequency=time in seconds. Example below.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

Full PJSIP configuration is covered in the *SIP & PJSIP in depth* chapter, and the official documentation at docs.asterisk.org has full coverage of the channel. In our companion labs at voip.school, lab 5 lets you practice what you have just learned.

## Quiz

1. Regarding the two analog Foreign eXchange interfaces, mark the correct statements (choose all that apply):
   - A. An FXO interface connects to the public switched telephone network (PSTN) central office and draws dial tone from it.
   - B. An FXS interface provides dial tone and ringing power to a standard analog phone, fax, or modem.
   - C. An FXS interface is the correct way to connect Asterisk to a telco line.
   - D. An FXO interface can also be connected to an extension port of a legacy PBX.
2. Supervision signaling on an analog line includes which of the following (choose all that apply)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, pops, and noise on a DAHDI analog card are most often caused by:
   - A. The way Asterisk was compiled
   - B. PCI interrupt conflicts
   - C. An incorrect SIP codec
   - D. A missing dial plan
4. For precise billing on analog channels you must detect exactly when the far end answers. Which feature do you activate on Asterisk (and request from the telco) to do this?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial-tone generation
5. The DAHDI hardware is independent of Asterisk: the physical card is configured in `/etc/dahdi/system.conf`, while `chan_dahdi.conf` defines the Asterisk channels, not the hardware itself.
   - A. True
   - B. False
6. Regarding digital trunk capacity and signaling, mark the correct statements (choose all that apply):
   - A. An E1 trunk carries 30 voice channels and a T1 trunk carries 24.
   - B. An ISDN PRI uses 30B+D on an E1 and 23B+D on a T1.
   - C. ISDN is an example of CCS signaling, while MFC/R2 is an example of CAS signaling.
   - D. T1 is the digital trunk most commonly used in Europe and Latin America.
7. Which utility automatically detects DAHDI cards and generates `/etc/dahdi/system.conf` and `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. When migrating a legacy `sip.conf` `[friend]` to PJSIP, a single block must be split into several objects. Which set of PJSIP `type=` objects normally replaces one registering `[friend]`?
   - A. `type=endpoint`, `type=aor`, and `type=auth`
   - B. `type=peer` and `type=user`
   - C. `type=sip` only
   - D. `type=channel` and `type=device`
9. What is the main practical advantage of using IAX2 trunk mode between two Asterisk servers?
   - A. It encrypts every call with TLS by default
   - B. It carries several calls under a single header, saving bandwidth
   - C. It removes the need for any codec
   - D. It allocates a separate UDP port per call for better quality
10. RSA keys can be used for IAX2 authentication. Which key must you keep secret, and which do you give to the other server?
    - A. Keep the public key secret; share the private key
    - B. Keep the private key secret; share the public key
    - C. Keep the shared key secret; share the private key
    - D. Both keys must be shared

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
