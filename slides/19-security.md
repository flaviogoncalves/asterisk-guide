---
theme: seriph
title: 'Securing Asterisk'
info: |
  ## Asterisk Guide — Chapter 17
  Securing Asterisk. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Securing Asterisk

Chapter 17

<div class="abs-bl m-6 text-sm opacity-70">
  Asterisk Guide · Asterisk 22 LTS · PJSIP-first
</div>

<style>
h1 { color: #1C5D99; }
</style>

---
layout: default
---

# Objectives

By the end of this chapter you will be able to:

<v-clicks>

- **Identify** the main types of attacks made against Asterisk servers
- **Define** an effective security policy
- **Implement** the security policy
- **Install and configure** IPTABLES for Asterisk
- **Install and configure** Fail2Ban for Asterisk
- **Install and configure** TLS and SRTP for encryption

</v-clicks>

<!--
SIP is the most attacked protocol on the Internet per CERT.BR. Never expose Asterisk
without proper security — toll fraud can cost hundreds of thousands of dollars in a weekend.
-->

---

# Why security comes first

<div class="mt-2">

- **SIP is the most attacked protocol on the Internet** (per CERT.BR) — run a honeypot and you'll see it within minutes.
- **Internet Revenue Share Fraud** can lead to losses over **hundreds of thousands of dollars** in a single weekend.
- **Never** connect an Asterisk server to the Internet without proper security.

</div>

<div class="mt-6 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Asterisk 22 is PJSIP-only.</strong> <code>chan_sip</code> was removed in Asterisk 21.
Failed authentications are now emitted through the <strong>security event framework</strong>
and the dedicated <code>security</code> logger channel — this changes how Fail2Ban is configured.
</div>

---
layout: section
---

# Anatomy of the attacks

---

# The three classes of attack

<div grid="~ cols-3 gap-4 text-sm mt-2">
<div>

### DoS / DDoS

Flooding and fuzzing to stop the service or degrade voice quality.

DDoS = botnet · DoS = single host.

</div>
<div>

### Theft of Service

Toll Fraud · Phone Fraud · **Internet Revenue Share Fraud** — pumping traffic to a premium-rate number for a rebate.

</div>
<div>

### Eavesdropping

Recording calls via **ARP spoofing** to redirect media. Hard to detect in an IP network.

</div>
</div>

<div class="mt-4 text-sm opacity-70">
Different sources use different names for the same attack — the underlying techniques are what matter.
</div>

---
layout: image-right
image: /images/19-security-fig01.png
backgroundSize: contain
---

# DoS / DDoS

Applied through **fuzzing** and **flooding** over SIP, IAX, RTP and other protocols.

<div class="text-sm mt-2">

**Fuzzing tools**

- **PROTOS c07-sip** (Univ. of Oulu) — malformed packets to provoke buffer overflows
- **Voiper** — 200,000+ tests over all SIP attributes

**Flooding tools**

- **INVITE Flooder** — floods with SIP INVITEs
- **IAX Flooder** — floods with IAX2 traffic
- **RTP Flooder** — degrades active media sessions

</div>

<!--
Feb 2011: the Sality botnet scanned the entire IPv4 space (~3M source IPs) probing
UDP/5060 to brute-force SIP accounts for toll fraud.
-->

---

# Mitigating DoS / DDoS

<v-clicks>

1. **Do not expose** your Asterisk server on the Internet unless necessary — and then only behind an **SBC** (Session Border Controller).
2. On the internal network, put voice on a **dedicated VLAN** — especially in large user populations.
3. Use a **VPN** or **TLS** for external access.

</v-clicks>

<div class="mt-6 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
If you leave UDP <strong>5060</strong> open on the Internet with no SBC or VPN, you are open to a DoS/DDoS attack. The risk is yours.
</div>

---
layout: image-right
image: /images/19-security-fig02.png
backgroundSize: contain
---

# Internet Revenue Share Fraud

The key concept: the **International Premium Rate Number (IPRN)**.

<div class="text-sm mt-2">

1. The hacker allocates a **free IPRN** (e.g. a costly satellite destination) from an IPRN provider.
2. The provider **pays back 10–20%** of the revenue for every minute received.
3. The hacker finds a **vulnerable PBX** and pumps hundreds of calls to that number.

</div>

<div class="mt-3 text-sm opacity-70">
Result: a huge payout for the hacker, a huge phone bill for the victim — often over $100k in one weekend.
</div>

---
layout: image-right
image: /images/19-security-fig03.png
backgroundSize: contain
---

# How the PBX gets compromised

<div class="text-sm">

**SIPVicious** — a brute-force toolkit; `svcrack` tests **thousands of passwords per second** to crack SIP credentials.

**Phone vulnerabilities** — default web-interface passwords left unchanged let attackers download the phone's config and read the SIP secret.

</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
An IPRN provider price list (left) shows per-country payout rates and test numbers — this is the attacker's profit sheet.
</div>

---
layout: image-right
image: /images/19-security-fig04.png
backgroundSize: contain
---

# TFTPTheft

Auto-provisioning over **TFTP** is insecure — no encryption, no authentication.

<div class="text-sm mt-2">

- Config filenames are guessable: **MAC address + `.cfg`** (e.g. `001A2B3C4D5E.cfg`).
- An attacker scripts every MAC sequentially and downloads each file.
- The config is usually **plaintext** and contains the SIP secret.

</div>

<div class="mt-4 text-sm opacity-80">
<strong>Mitigation:</strong> provision over <strong>HTTPS with username and password</strong> — encrypted transfer, no anonymous downloads.
</div>

---

# Eavesdropping

Rarely seen — because it is rarely **detected**.

<div grid="~ cols-2 gap-8 mt-2">
<div>

**The attack**

- Tools like **UCsniff** record VoIP calls on most networks.
- Uses **ARP spoofing** to force traffic through the attacker's machine (MITM).

</div>
<div>

**Mitigation**

- **Encrypt media** with TLS + SRTP (later in this chapter).
- Prevent MITM with **Dynamic ARP Inspection** in layer-2 switches.
- Use **ARPwatch** to detect ARP abuse.

</div>
</div>

---
layout: section
---

# A security policy for Asterisk

---

# The suggested policy

<div class="text-sm">

<v-clicks>

1. **No unnecessary** UDP/TCP ports open
2. **No administrative interface** (SSH / HTTPS) open on the Internet
3. SSH and HTTP/HTTPS reachable only via explicit **IPTABLES exceptions**
4. **Strong passwords** — 12+ characters, at least one special character
5. **Ban** IPs failing authentication more than 10 times — via **Fail2Ban**
6. **Password confirmation** for international calls
7. **Limit the SIP port** to your known range of IP addresses

</v-clicks>

</div>

<div class="mt-3 text-sm opacity-70">
For external access use an <strong>SBC</strong> or a <strong>VPN</strong> — never a bare port 5060.
</div>

---

# PJSIP-era hardening (Asterisk 22)

Configuration-level controls that **complement** the network controls.

<div grid="~ cols-2 gap-6 text-sm mt-2">
<div>

- **Per-endpoint auth** — dedicated `type=auth`, `auth_type=digest`, unique strong password; never reuse credentials.
- **Anonymous handling** — PJSIP won't reveal whether a username exists. To allow anonymous calls you must explicitly create an `anonymous` endpoint and `type=identify` sections.
- **ACLs** — `acl=` (source) and `contact_acl=` (registration), or permit/deny on the endpoint.

</div>
<div>

- **`qualify`** — set `qualify_frequency` / `qualify_timeout` on the AOR to prune dead contacts.
- **Transport hardening** — no per-transport client cap; use the firewall for flood protection, plus `tcp_keepalive_*` and `local_net`/`external_*`.
- **TLS + SRTP** — `media_encryption=sdes` (or `dtls` for WebRTC).
- **AMI / ARI** — bind to localhost, strong secrets, never expose.

</div>
</div>

<div class="mt-2 text-xs opacity-60">
Note: <code>res_pjsip</code> transports have <strong>no</strong> <code>max_clients</code> option in Asterisk 22.
</div>

---

# Removing unnecessary ports

List the ports Asterisk binds:

```bash
netstat -pantu | grep asterisk
```

Disable modules you don't use in `modules.conf` — but **keep PJSIP loaded**:

```ini
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 — keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

<div class="mt-3 text-sm opacity-80">
A high-numbered UDP port is just <code>res_pjsip</code>'s resolver doing outbound DNS (ephemeral source port) — your <code>ESTABLISHED,RELATED</code> rule already covers it. <code>chan_mgcp</code> and <code>chan_skinny</code> were <strong>removed in Asterisk 21</strong> — nothing to noload.
</div>

---
layout: image-right
image: /images/19-security-fig06.png
backgroundSize: contain
---

# After hardening modules

Before: MGCP (**2727**), IAX (**4569**) and more were bound.

After noloading the unused channels, **only UDP 5060** (your PJSIP transport) remains exposed inbound.

<div class="mt-4 text-sm opacity-70">
Keep only the protocol modules you actually use — for a pure SIP PBX that means PJSIP and nothing else.
</div>

---

# IPTABLES — loopback, established, admin

```bash
sudo apt-get install iptables-persistent

# Allow loopback
sudo iptables -I INPUT  -i lo -j ACCEPT
sudo iptables -I OUTPUT -o lo -j ACCEPT

# Allow established/related connections (covers PJSIP outbound DNS replies)
sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow SSH/HTTPS only from the internal network
sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22  -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
```

<div class="mt-2 text-sm opacity-70">
Keep <strong>console access</strong> to the server — you do not want to lock yourself out.
</div>

---

# IPTABLES — SIP, RTP, and the DROP

```bash
# SIP signalling — 5060 UDP+TCP, 5061 TCP (TLS), plus the RTP media range
sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT

# The LAST rule must be a drop (-A appends; -I prepends)
sudo iptables -A INPUT -j DROP

# Persist and restart
sudo iptables-save > /etc/iptables/rules.v4
sudo /etc/init.d/netfilter-persistent restart
```

<div class="mt-2 text-sm opacity-70">
Port <strong>5061 (SIP over TLS) is TCP</strong>, not UDP. Match the RTP range to your <code>rtpstart</code>/<code>rtpend</code> in <code>rtp.conf</code>. If you only run TLS, drop the 5060 rules. Add new rules with <strong>-I</strong> (prepend) <em>before</em> the DROP.
</div>

---
layout: section
---

# Fail2Ban — banning brute-force attackers

---

# Fail2Ban + the security logger

In Asterisk 22, PJSIP reports failed auth through the **security event framework** → the dedicated **`security`** logger channel.

Enable it in `/etc/asterisk/logger.conf`:

```ini
[logfiles]
security => security
```

Then reload, from the Asterisk CLI:

```text
CLI> module reload logger
```

<div class="mt-2 text-sm opacity-80">
This writes <code>/var/log/asterisk/security</code> with lines like <code>SecurityEvent="InvalidPassword"</code>, <code>ChallengeResponseFailed</code>, <code>InvalidAccountID</code> — each carrying the <code>RemoteAddress=</code> of the offender. Point the jail's <code>logpath</code> at this file.
</div>

---

# Installing and activating Fail2Ban

```bash
sudo apt-get install fail2ban

# Activate the sshd and asterisk jails
sudo vi /etc/fail2ban/jail.d/defaults-debian.conf
```

```ini
[sshd]
enabled = true
[asterisk]
enabled = true
```

```bash
sudo /etc/init.d/fail2ban restart
```

<div class="mt-2 text-sm opacity-80">
Modern Fail2Ban ships an <code>asterisk</code> filter, and FreePBX/Sangoma distros ship updated filters that already understand the PJSIP / security-event format. <strong>Prefer those.</strong>
</div>

---

# Verifying and unbanning

<div class="text-sm">

- **Test:** change the secret on your softphone and try to re-register **10 times**.
- **Check:** the attacker IP should now appear as a blocked address.

</div>

```bash
# List the firewall to confirm the IP was banned
sudo iptables -L

# Remove an address from the ban (e.g. 192.168.0.5 = your phone)
sudo fail2ban-client set asterisk unbanip 192.168.0.5
```

<div class="mt-3 text-sm opacity-70">
Pair Fail2Ban with <strong>strong passwords</strong> (12+ chars, a special character) — banning slows brute force, strong secrets defeat it.
</div>

---
layout: section
---

# TLS and SRTP — encrypting signalling and media

---

# What TLS protects (and what it doesn't)

<div class="text-sm mt-2">

| Attack | Protected? | Why |
|--------|:---------:|-----|
| Signalling attacks | **YES** | TLS assures message integrity |
| Man-in-the-Middle | **YES** | TLS checks the server certificate |
| Eavesdropping (media) | **NO** | TLS encrypts signalling, not voice — use **SRTP** for media |

</div>

<div class="mt-4 text-sm opacity-80">
For VoIP you can be your <strong>own certificate authority</strong> — a commercial cert from GoDaddy/Verisign is an unnecessary expense. Generate self-signed certs with <code>ast_tls_cert</code>.
</div>

---

# Generating the certificates

`ast_tls_cert` lives in `contrib/scripts`. Options: `-C` host/IP, `-O` org, `-d` key directory.

```bash
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
```

It creates the CA and the Asterisk certificate:

```text
Creating CA key /etc/asterisk/keys/ca.key
Creating CA certificate /etc/asterisk/keys/ca.crt
Creating certificate /etc/asterisk/keys/asterisk.key
Creating certificate /etc/asterisk/keys/asterisk.crt
Combining key and crt into /etc/asterisk/keys/asterisk.pem
```

<div class="mt-2 text-sm opacity-70">
No <strong>client certificate</strong> is generated — Asterisk only <em>encrypts</em> the session here; authentication stays username + password.
</div>

---

# Configuring the TLS transport

PJSIP is the only SIP channel in Asterisk 22 — just confirm it's loaded, then add a TLS transport in `pjsip.conf`:

```ini
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

<div class="mt-3 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
Use <code>method=tlsv1_2</code> (or <code>tlsv1_3</code> if your OpenSSL/PJSIP build supports it). <strong>TLS 1.0 / 1.1 are obsolete and insecure</strong> — never use them.
</div>

---

# Endpoint, AOR and auth over TLS

```ini
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes

[blink]
type=aor
max_contacts=2
remove_existing=yes

[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

---

# Verifying the TLS registration

```text
CLI> pjsip show aor blink

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual nan

 contact : sip:03694827@192.168.0.67:56295;transport=tls
```

<div class="mt-4 text-sm opacity-80">
The <code>transport=tls</code> in the contact URI confirms the device registered over the encrypted transport. If a client cert is signed by a public CA (e.g. Let's Encrypt — see the <em>Deployment</em> chapter) a modern softphone trusts it automatically; for self-signed, import <code>ca.crt</code> into the client trust store.
</div>

---

# SRTP — encrypting the media

SRTP (RFC 3711) encrypts voice/video. Asterisk exchanges keys with **SDES** over SDP, protected by TLS signalling.

```ini
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

<div class="mt-3 text-sm opacity-80">
<code>media_encryption_optimistic=no</code> <strong>rejects</strong> unencrypted media rather than silently allowing it. SDES requires the signalling to run over <strong>TLS</strong> so keys aren't sent in the clear. In the softphone, set <strong>SRTP</strong> to <em>Mandatory</em>.
</div>

---

# The softphone — TLS + SRTP

<div grid="~ cols-2 gap-6">
<div>

Choose **TLS** as the transport (port **5061**) and set **SRTP** to *Mandatory* so both signalling and media are encrypted.

<div class="text-sm mt-3">

- Use the correct password — **auth is still password-based**.
- For self-signed certs, import `ca.crt`.
- **No client certificate** needed.
- After changing transport, **fully restart** the softphone.

</div>

</div>
<div>

![SipPulse Softphone account screen — Server, Username, Password, Display Name, and Transport (UDP/TCP/TLS)](/images/softphone/sipphone-account.png)

</div>
</div>

---

# Toll-fraud defence: two-way auth for international calls

The best defence is **no international routes**. If you need them, demand a **second password** (the voicemail PIN) before dialing:

```ini
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

<div class="mt-3 text-sm opacity-80">
Now an attacker who steals a SIP password or compromises a phone <strong>still</strong> needs the voicemail PIN to dial abroad. <code>VMAuthenticate</code> is valid in Asterisk 22; route over a <strong>PJSIP trunk</strong> (use <code>DAHDI/...</code> only if you really have a span). Also restrict which contexts can reach outbound/international routes.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**TLS and SRTP — encrypt signalling and media end-to-end**

Generate a CA with `ast_tls_cert`, add a TLS transport to `pjsip.conf`,
set `media_encryption=sdes`, and register a softphone over **TLS (5061)** with SRTP.

See **Lab 7 — TLS and SRTP** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Then verify with <code>pjsip show aor</code> that the contact carries <code>transport=tls</code>.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- **SIP is the most-attacked protocol** — never expose Asterisk without security; toll fraud is the costliest risk.
- Attacks fall into three classes: **DoS/DDoS**, **theft of service / IRSF**, and **eavesdropping**.
- Build a **security policy** first: close unused ports, lock down admin interfaces, strong passwords, ACLs, and per-endpoint PJSIP auth.
- Enforce it with **IPTABLES** (default-DROP) and **Fail2Ban** reading the Asterisk 22 **`security`** logger channel.
- Encrypt with **TLS** (signalling) + **SRTP / `media_encryption=sdes`** (media), and add **two-way auth** for international calls.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Deployment</strong> — taking a hardened Asterisk 22 to production.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 17 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which PJSIP endpoint setting turns on SRTP media encryption using in-SDP (SDES) keys?</em>
</div>
