# Part II — Channels & Connectivity {.unnumbered}

Part II is about how calls get in and out of Asterisk. We start by designing the VoIP
network around it — codecs, bandwidth, and NAT — then study SIP and its modern PJSIP
implementation in depth, since PJSIP is the only SIP channel in Asterisk 22.

From there we add the connections a real deployment needs: browser calling with
WebRTC, trunks and DIDs to reach the PSTN and your providers, and the legacy analog,
digital (TDM), and IAX2 channels you may still meet in the field. By the end you can
connect Asterisk to phones, browsers, carriers, and older equipment alike.
