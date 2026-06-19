# Deployment, monitoring & scaling

> **[2nd-ed note]** NEW chapter — outline only; prose to be written in Phase 4. The Docker
> lab in `lab/` is the worked example for the containerization section.

## Objectives

By the end of this chapter, you should be able to:

- Run Asterisk 22 reliably under systemd
- Containerize Asterisk with Docker and understand the trade-offs
- Manage configuration and backups
- Monitor a running system (logs, CDR/CEL, metrics)
- Apply basic high-availability and scaling patterns
- Host Asterisk in the cloud safely

## Running Asterisk under systemd

> **[2nd-ed note]** The shipped `asterisk.service`, `Restart=`, running as a non-root user,
> `systemctl` lifecycle; why `safe_asterisk` is superseded. Cross-reference the install chapter.

## Containerizing Asterisk

> **[2nd-ed note]** Walk through the book's own Docker lab: Dockerfile, bind-mounted config,
> host networking vs bridged + the RTP port range problem, persistent volumes for spool/voicemail.

## Configuration management and backups

> **[2nd-ed note]** Keeping `/etc/asterisk` in version control, templating per-environment,
> what to back up (config, voicemail, CDR, DB), `astdb`.

## Monitoring and observability

> **[2nd-ed note]** CLI health (`core show channels`, `pjsip show endpoints`), CDR/CEL,
> AMI events, ARI, and exporting metrics (Prometheus exporter / Grafana). SIP response codes to watch.

## High availability and scaling

> **[2nd-ed note]** Active/standby with a floating IP, externalizing state (PJSIP realtime —
> cross-reference the Realtime chapter), load distribution via SIP proxies (Kamailio/OpenSIPS),
> media scaling considerations.

## Cloud hosting

> **[2nd-ed note]** NAT/firewall on cloud VMs, the RTP port range, fail2ban (cross-reference
> Security), choosing a region for latency, SBC in front.

## Summary
