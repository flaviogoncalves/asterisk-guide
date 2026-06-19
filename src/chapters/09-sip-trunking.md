# SIP trunking, DID & the PSTN

> **[2nd-ed note]** NEW chapter — outline only; prose to be written in Phase 4 and
> lab-verified against a test ITSP (or a second Asterisk acting as the provider).
> Consolidates trunking material previously scattered across the simple-PBX and SIP chapters.

## Objectives

By the end of this chapter, you should be able to:

- Connect Asterisk 22 to an Internet Telephony Service Provider (ITSP) with PJSIP
- Choose between registration-based and IP-based trunks
- Route inbound DIDs to the right extension or IVR
- Route outbound calls with correct caller-ID and E.164 formatting
- Build trunk failover and least-cost routing
- Handle NAT for trunks

## What is a SIP trunk

> **[2nd-ed note]** ITSP vs PSTN gateway; the trunk as a PJSIP endpoint; SIP vs the old
> TDM PRI (cross-reference the Legacy channels chapter).

## Registration-based trunks

> **[2nd-ed note]** `type=registration` + `outbound_auth`; when the provider expects you to
> register; `pjsip show registrations`.

## IP-based (static) trunks

> **[2nd-ed note]** `type=identify` matching the provider IP; no registration; `match=` and
> the security implications (pair with an ACL).

## Inbound routing and DID handling

> **[2nd-ed note]** Matching the dialed DID in the trunk's context; `${EXTEN}` patterns;
> sending to extensions / IVR / queues; multiple DIDs.

## Outbound routing, caller-ID and E.164

> **[2nd-ed note]** Dial(PJSIP/${EXTEN}@trunk); `CALLERID(num)`; `from_user`/`from_domain`;
> number normalization to E.164; dial patterns and `_` prefixes.

## Failover and least-cost routing

> **[2nd-ed note]** Multiple trunks, `Dial()` with multiple technologies, `${DIALSTATUS}`
> handling, GoSub-based routing tables.

## NAT and trunks

> **[2nd-ed note]** `rewrite_contact`, `rtp_symmetric`, `force_rport`, `external_media_address`,
> `external_signaling_address` on the transport; cross-reference Designing a VoIP network.

## Lab

> **[2nd-ed note]** Use a second Asterisk container as a mock ITSP; place an inbound + outbound
> call across the trunk with SIPp; capture `pjsip show endpoint trunk`.

## Summary
