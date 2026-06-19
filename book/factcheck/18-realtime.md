# Fact-check ledger — Asterisk Real-Time

Verified: 24 · Wrong (fixed): 0 · Reworded (sourced): 3 · Unverified: 0

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "ARA or Asterisk Realtime ... was created by Anthony Minessale II, Mark Spencer, and Constantine Filin" | 10 | VERIFIED (secondary) | https://www.voip-info.org/asterisk-realtime/ ("the result of work by Anthony Minessale II, Mark Spencer and Constantine Filin"); corroborated http://www.asteriskdocs.org/en/3rd_Edition/asterisk-book-html-chunk/I_section12_tt1465.html |
| 2 | "configured in /etc/asterisk/extconfig.conf" | 10 | VERIFIED | lab: file present /usr/src/asterisk-22.10.0/configs/samples/extconfig.conf.sample |
| 3 | "An LDAP interface is available too" | 10 | VERIFIED | https://docs.asterisk.org/Fundamentals/Asterisk-Configuration/Database-Support-Configuration/Realtime-Database-Configuration/ (LDAP realtime driver) |
| 4 | "On Asterisk 22, SIP endpoints are handled by the PJSIP stack (res_pjsip), which is built on the Sorcery object model" | 32,135 | VERIFIED | https://docs.asterisk.org/Fundamentals/Asterisk-Configuration/Sorcery/ ; res_pjsip uses Sorcery |
| 5 | "Sorcery has a built-in caching and persistence layer, so realtime PJSIP objects are not thrown away after each call ... NAT traversal, qualify, and MWI all work normally" | 32 | REWORDED (sourced) | Sorcery caching is OPT-IN ('/cache' mapping / memory_cache wizard), confirmed https://docs.asterisk.org/Fundamentals/Asterisk-Configuration/Sorcery/ ("A wizard can optionally be marked as an object cache by adding '/cache'"). Reworded: realtime wizard loads objects on demand from DB; they exist as ordinary configured PJSIP objects (so qualify/MWI/NAT work), unlike chan_sip's discarded realtime peers; memory_cache noted as separate opt-in. |
| 6 | "The following files CANNOT be loaded from Realtime storage: asterisk.conf, extconfig.conf, logger.conf" | 66-69 | VERIFIED | lab: /usr/src/asterisk-22.10.0/configs/samples/extconfig.conf.sample (exact lines) |
| 7 | "cannot be loaded ... unless ... 'preload' ... : manager.conf, cdr.conf, rtp.conf" | 71-76 | VERIFIED | lab: extconfig.conf.sample (exact lines) |
| 8 | Static mapping syntax "<conf filename> => <driver>,<databasename>[,table_name]" | 103 | VERIFIED | lab extconfig.conf.sample ("file.conf => driver,database[,table]") |
| 9 | Realtime family syntax "<family name> => <driver>,<database name>[,table_name]" | 118 | VERIFIED | https://docs.asterisk.org/Fundamentals/Asterisk-Configuration/Database-Support-Configuration/Realtime-Database-Configuration/ ("<family> => <realtime driver>,<class name>[,<table>]") |
| 10 | "voicemail, extensions, queues, and queue_members families are still valid in Asterisk 22" | 131 | VERIFIED | lab extconfig.conf.sample lists voicemail/extensions/queues/queue_members |
| 11 | Sorcery object→table map: endpoint=ps_endpoints, aor=ps_aors, auth=ps_auths, contact=ps_contacts, domain alias=ps_domain_aliases, endpoint id by IP=ps_endpoint_id_ips | 137-144 | VERIFIED | lab: contrib/ast-db-manage/config/versions/43956d550a44_add_tables_for_pjsip.py creates exactly these 6 tables |
| 12 | "aor ... holds registration limits and qualify settings" | 140 | VERIFIED | lab migration: ps_aors has max_contacts, qualify_frequency, authenticate_qualify |
| 13 | "auth ... username / password credentials" | 141 | VERIFIED | lab migration: ps_auths has username, password (+auth_type) |
| 14 | "contact ... the dynamically registered location" stored in ps_contacts | 142,345 | VERIFIED | lab migration: ps_contacts (uri, expiration_time); https://docs.asterisk.org/.../Setting-up-PJSIP-Realtime/ |
| 15 | "domain alias ... alternate SIP domains" (ps_domain_aliases) | 143 | VERIFIED | lab migration: ps_domain_aliases has 'domain' column |
| 16 | "endpoint identifier by IP ... matching an endpoint by source IP" (ps_endpoint_id_ips) | 144 | VERIFIED | lab migration: ps_endpoint_id_ips has 'endpoint','match' columns |
| 17 | extconfig.conf families: ps_endpoints/ps_aors/ps_auths/ps_contacts/ps_domain_aliases/ps_endpoint_id_ips => odbc,asterisk | 150-156 | VERIFIED | https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/Setting-up-PJSIP-Realtime/ (identical list) |
| 18 | sorcery.conf [res_pjsip] endpoint/aor/auth/domain_alias/contact = realtime,ps_* | 161-166 | VERIFIED | https://docs.asterisk.org/.../Setting-up-PJSIP-Realtime/ (identical mappings) |
| 19 | "[res_pjsip_endpoint_identifier_ip] identify=realtime,ps_endpoint_id_ips" | 168-169 | VERIFIED | https://docs.asterisk.org/.../Setting-up-PJSIP-Realtime/ (exact line); identify provided by res_pjsip_endpoint_identifier_ip.so |
| 20 | "If you omit a type from sorcery.conf, that object type keeps reading from pjsip.conf" | 172 | VERIFIED | https://docs.asterisk.org/.../Setting-up-PJSIP-Realtime/ (static config.conf wizard is the default fallback) |
| 21 | "Asterisk ships database migrations ... under contrib/ast-db-manage ... config migration set contains the PJSIP/Sorcery tables" | 176 | VERIFIED | lab: /usr/src/asterisk-22.10.0/contrib/ast-db-manage/config/ with config.ini.sample; 43956d550a44 creates ps_* tables |
| 22 | "legacy static schema files still ship under contrib/realtime/ (mysql, postgresql)" | 257 | VERIFIED | lab: /usr/src/asterisk-22.10.0/contrib/realtime/ contains mysql, postgresql |
| 23 | ps_auths row: "auth_type=userpass, username=6010, password=..." | 191,323,327 | VERIFIED | lab migration PJSIP_AUTH_TYPE_VALUES=['md5','userpass']; auth_type default userpass (config show help res_pjsip auth auth_type) |
| 24 | ps_endpoints columns: transport, aors, auth, context, disallow, allow, direct_media, dtmf_mode, callerid all valid | 193-196,219,335-340 | VERIFIED | lab migration ps_endpoints column list (all present) |
| 25 | "the RFC 2833 / RFC 4733 DTMF mode is named rfc4733 (dtmf_mode=rfc4733, the default)" | 339,345 | VERIFIED | lab: config show help res_pjsip endpoint dtmf_mode → "Default: rfc4733" |
| 26 | "an AOR accepts dynamic REGISTERs as long as ... max_contacts greater than zero ... written to ps_contacts" | 345 | VERIFIED | lab migration: ps_aors.max_contacts; ps_contacts table for registered locations |
| 27 | "ARA uses the switch statement ... switch => realtime / realtime/ramais@extensions" | 225,233,240,366 | VERIFIED | lab: `core show switches` lists "Realtime: Realtime Dialplan Switch" |
| 28 | "Databases supported are MySQL and any other Unix ODBC-supported databases" | 376 | REWORDED (sourced) | https://docs.asterisk.org/Fundamentals/Asterisk-Configuration/Database-Support-Configuration/Realtime-Database-Configuration/ — native drivers: ODBC, MySQL, PostgreSQL; plus LDAP realtime driver (page + chapter L10). Reworded summary to list ODBC (incl. UnixODBC dbs like MySQL/MariaDB/SQLite), MySQL, PostgreSQL, and LDAP, and to stop presenting the list as exhaustive. |
| 29 | Quiz 5: "PJSIP realtime (Sorcery) fully supports qualify and MWI ... because Sorcery keeps the objects cached" | 396 | REWORDED (sourced) | Same source as #5 (Sorcery docs). "cached" rationale was imprecise; reworded to "loads them as ordinary configured PJSIP objects rather than discarding them ... the way the old SIP realtime peers were." Answer (True) unchanged. |
| 30 | Quiz 6: endpoints/contacts held by ps_endpoints and ps_contacts | 402-403 | VERIFIED | lab migration (ps_endpoints, ps_contacts) |
| 31 | Quiz 10: recommended way is Alembic config migrations under contrib/ast-db-manage | 416-419 | VERIFIED | lab: ast-db-manage/config present; matches docs setup workflow |

## Resolved (this pass)

- **Line 32 / Quiz 5: "Sorcery has a built-in caching ... layer." — REWORDED.** Confirmed against https://docs.asterisk.org/Fundamentals/Asterisk-Configuration/Sorcery/ that Sorcery caching is *opt-in* ("A wizard can optionally be marked as an object cache by adding '/cache' to the object type"; memory_cache wizard), not an always-on built-in cache. The realtime wizard loads objects from the DB on demand. Rewrote L32 to attribute persistent qualify/MWI/NAT to the objects being loaded as ordinary configured PJSIP objects (vs. chan_sip's discarded realtime peers), noting memory_cache as a separate opt-in. Quiz 5 stem reworded the same way; answer (True) unchanged. Functional conclusion preserved.
- **Line 376 (summary): "Databases supported are MySQL and any other Unix ODBC-supported databases." — REWORDED.** Per https://docs.asterisk.org/Fundamentals/Asterisk-Configuration/Database-Support-Configuration/Realtime-Database-Configuration/, native realtime drivers are ODBC, MySQL, and PostgreSQL; an LDAP realtime driver also exists (chapter L10). Reworded to list ODBC (incl. UnixODBC-reachable databases such as MySQL/MariaDB/SQLite), MySQL, PostgreSQL, and LDAP, removing the implied-exhaustive "MySQL + ODBC only" framing.
- **ODBC realtime (lab limitation, no chapter change).** The lab image lacks `res_config_odbc.so` (only res_sorcery_realtime.so present), so ODBC realtime could not be exercised end-to-end. The chapter's ODBC statements (extconfig.conf family→driver mapping syntax, `ps_*` families => odbc,<db>, sorcery.conf realtime wizard) match the official docs and the Alembic migration sources, so no chapter change was needed. All ODBC-family/realtime-mapping claims verified against the docs page + Alembic migrations rather than a live ODBC connection.

## Left for other reviewers (non-factual)

- **Stray Portuguese chapter-1 running headers** ("Capítulo 1 | Introdução ao Asterisk") embedded in the English text. Not a factual claim — leftover layout artifacts for the general/structure reviewer.

## Notes
- No unambiguous factual errors found; the PJSIP/Sorcery realtime conversion (tables, columns, sorcery.conf and extconfig.conf mappings, dtmf_mode, auth_type, switch=>realtime) matches Asterisk 22.10.0 sources. No Edits applied.
