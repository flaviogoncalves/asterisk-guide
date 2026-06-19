# Chapters 1 & 3 — Nano Banana Pro (flat house style) subjects

Base prompt: book/illustrate/prompts/house-flat.txt, with `Subject:` appended per figure.
Each was generated 1K / 16:9, 1 variation, with the original figure passed via --ref.

- 01-introduction-fig01: Asterisk architecture block diagram (PBX core + Applications/Channels/Codec-Translation/File-Format APIs; channel list modernized to PJSIP/SIP, IAX2, DAHDI).
- 01-introduction-fig02: Asterisk hub-and-spoke system overview (IP/analog phones, Telco, functions).
- 01-introduction-fig03/04: "separate appliances" vs "Asterisk-integrated" deployment pair.
- 01-introduction-fig05: simple Asterisk test lab (SIP phone, ITSP, FXS/FXO, ATA). English labels.
- 01-introduction-fig06: Asterisk IP-PBX with Ethernet backbone (labeled "Asterisk 22").
- 01-introduction-fig07: IP-enabling a legacy PBX (WAN/Internet + LAN).
- 01-introduction-fig08: multi-site toll bypass over a WAN (NY / Rio / LA HQ).
- 01-introduction-fig09: Asterisk as an application server behind a legacy PBX.
- 01-introduction-fig10: Asterisk as a media gateway (legacy PBX + ITSP/SIP proxy + customers).
- 04-first-pbx-fig01: layered lab topology in three bands (Trunks / Asterisk / Extensions).
- 04-first-pbx-fig02: FXS vs FXO ports (phone <-> Asterisk <-> Telco).

PATH-1/2 (free, scripted) figures in the same pilot:
- 04-first-pbx-fig03/04/07/09 -> book/illustrate/render_ch3_slides.py
- 01-introduction-fig11        -> book/illustrate/render_ch1_fig11.py
