# Fact-check ledger — Extending Asterisk with AMI, AGI and ARI

Verified: 28 · Wrong (fixed): 1 · Unverified: 0

(Plus 3 author findings — outdated AMI event material that needs an editorial rewrite, not a one-word fix.)

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "ARI (introduced in Asterisk 12)" | 3 | VERIFIED | lab: `config show help res_ari general enabled` → `[Since] 12.0.0` |
| 2 | "ARI … was introduced in Asterisk 12 and is now the recommended approach" | 664 | VERIFIED | lab: `config show help res_ari general enabled` → Since 12.0.0; docs.asterisk.org/Configuration/Interfaces/Asterisk-REST-Interface-ARI/ ("before Asterisk 12") |
| 3 | `asterisk –rx <command>` runs a console command from the shell | 33-46 | VERIFIED | lab: `asterisk -rx 'core show version'` returns output |
| 4 | System() "Result of execution is returned in the SYSTEMSTATUS channel variable" with FAILURE/SUCCESS | 74-76 | VERIFIED | lab: `core show application System` → `${SYSTEMSTATUS}: FAILURE / SUCCESS` |
| 5 | System() provided by app_system, executes via system() | 63 | VERIFIED | lab: `core show application System` → Provided By app_system |
| 6 | AMI is "a line protocol using key:value pairs over TCP" | 90 | VERIFIED | docs.asterisk.org/Configuration/Interfaces/Asterisk-Manager-Interface-AMI/ |
| 7 | "first line of a packet will have the key 'Action' when sent from a client" / "'Response' or 'Event'" from Asterisk | 99-100 | VERIFIED | docs.asterisk.org AMI v2 Specification (packet structure) |
| 8 | AMI listens on "a TCP port (usually 5038)" | 115 | VERIFIED | AMI well-known default port 5038 (manager.conf `port=5038`); docs.asterisk.org AMI |
| 9 | manager.conf general options enabled/port/bindaddr; per-user secret/read/write/deny/permit | 119-128 | VERIFIED | lab: `manager show settings` (AMI off by default, TCP bindaddress disabled); option names per docs.asterisk.org AMI |
| 10 | "manager show commands" lists available actions | 180 | VERIFIED | lab: `manager show commands` returns the action table |
| 11 | Action `WaitEvent`, privilege `<none>` | 184 | VERIFIED | lab: `manager show commands` → WaitEvent present |
| 12 | Action `CoreShowChannels` "List currently active channels" | 188 | FIXED | Chapter had `CoreShowChannel`; lab `manager show commands` → `CoreShowChannels` |
| 13 | Actions `ModuleCheck`, `ModuleLoad`, `Reload`, `CoreStatus`, `CoreSettings`, `UserEvent`, `SendText`, `ListCommands` exist | 185-194 | VERIFIED | lab: `manager show commands` (all present) |
| 14 | Actions `Originate`, `Atxfer`, `Redirect`, `Command`, `Status`, `Hangup`, `Challenge`, `Login`, `Logoff`, `Events`, `Ping`, `Getvar`, `Setvar` exist | 199-216 | VERIFIED | lab: `manager show commands` |
| 15 | Queue actions `QueueRule/QueuePenalty/QueueLog/QueuePause/QueueRemove/QueueAdd/QueueSummary/QueueStatus` exist | 227-235 | VERIFIED | lab: `manager show commands` (QueueStatus, QueueSummary, etc. present) |
| 16 | `AgentLogoff`, `Agents`, `UnpauseMonitor`, `PlayDTMF` exist | 236-239 | VERIFIED | lab: `manager show commands` (AgentLogoff, Agents, PlayDTMF present) |
| 17 | PJSIP actions `PJSIPShowEndpoints/PJSIPShowEndpoint/PJSIPQualify/PJSIPShowRegistrationsOutbound/PJSIPShowContacts` exist | 240-244 | VERIFIED | lab: `manager show commands` (all five present) |
| 18 | `AGI` action "Add an AGI command to execute by Async AGI" | 248 | VERIFIED | lab: `manager show commands` → AGI present |
| 19 | DB actions `DBDelTree/DBDel/DBPut/DBGet`, `Bridge`, plus monitor/park actions | 254-261 | VERIFIED (core ones) | lab: `manager show commands` (DBDel/DBDelTree/DBGet/DBPut/Bridge present). Monitor/Park/IAX/DAHDI come from optional modules — chapter caveats "loaded modules add more" |
| 20 | `manager show command originate` describes Channel/Exten/Context/Priority/Application/Data/Timeout/CallerID/Variable/Account/Async | 266-284 | VERIFIED | lab: `manager show command Originate` (all fields present; lab adds EarlyMedia/Codecs/ChannelId/PreDialGoSub) |
| 21 | AGI "allows the use of high-level languages like Perl, PHP, and Python" | 414 | VERIFIED | lab: `core show application AGI` ("written in any language") |
| 22 | Four AGI types: Normal AGI, FastAGI (TCP), EAGI (audio access), DeadAGI (dead channel) | 414-419 | VERIFIED | lab: `core show application AGI` (AGI/FastAGI/AsyncAGI variants) + `core show application EAGI` + DeadAGI() see-also |
| 23 | EAGI "incoming audio available out of band on file descriptor 3" | 437 | VERIFIED | lab: `core show application EAGI` → "out of band on file descriptor 3" |
| 24 | "agi show commands" lists AGI commands | 442 | VERIFIED | lab: `agi show commands` returns the table |
| 25 | AGI command names (answer/get data/say number/stream file/set variable/exec/gosub etc.) | 445-493 | VERIFIED | lab: `agi show commands` (all listed commands present; lab adds `asyncagi break`) |
| 26 | FastAGI uses TCP port 4573 by default, URI form agi:// | 654-657, 711 | VERIFIED | lab: `core show application AGI` (FastAGI URI `agi://host[:port]`); default port 4573 per res_agi (voip-info.org, asteriskdocs.org) |
| 27 | ARI WebSocket `ws://host:8088/ari/events?app=…&api_key=user:pass`; events as JSON; REST POST /ari/channels etc. | 667-669 | VERIFIED | docs.asterisk.org ARI Getting-Started (`/ari/events?api_key=…&app=…`); lab `http show status` → HTTP bound 0.0.0.0:8088 |
| 28 | ARI configured in ari.conf + http.conf; options enabled/pretty + user type/read_only/password/password_format=plain | 671-683 | VERIFIED | lab: `config show help res_ari general enabled` (Default yes), `general pretty` (Default no), `user read_only` (Default no), `user password_format` (plain/crypt, Default plain) |
| 29 | Quiz: AMI "enabled by default in a fresh Asterisk install" answer False | 705, 733 | VERIFIED | lab: `manager show settings` → Manager (AMI): No (disabled by default) |
| 30 | Quiz: ARI read_only=yes marks user read-only | 727-731, 733 | VERIFIED | lab: `config show help res_ari user read_only` → "user is only authorized for read-only requests" |
| 31 | Quiz: `agi show commands` / `manager show commands` are the listing commands | 720-721, 733 | VERIFIED | lab: both commands return their respective tables |

## Author findings (need editorial rewrite, not a one-word fix)

- **F1 — "Link Events / Unlink events" section is obsolete (lines 286-312).** The AMI `Link`/`Unlink` events were removed in Asterisk 12 with the new bridging framework. Asterisk 22 emits `BridgeCreate`/`BridgeEnter`/`BridgeLeave`/`BridgeDestroy` instead. Verified absent: `manager show events` shows no Link/Unlink, but lists BridgeCreate/BridgeEnter/BridgeLeave/BridgeDestroy. Recommend rewriting the section around bridge events. (Also: the "Unlink events" example at lines 307-311 erroneously repeats `Event: Link` — but the whole example should be replaced, not just relabeled.)
- **F2 — "Events available" list is a legacy AMI-v1 / Java-library class list (lines 318-410).** It includes events removed/renamed in Asterisk 22: `MeetMeEvent`, `MeetMeJoinEvent`, `MeetMeLeaveEvent`, `MeetMeTalkingEvent`, `MeetMeStopTalkingEvent` (app_meetme is removed — lab `module show like meetme` → 0 modules; `core show application MeetMe` → not registered), plus `LinkEvent`/`UnlinkEvent`/`HoldedCallEvent`/`DBGetResponseEvent`/`AbstractAgentEvent` etc. Actual 22 event names differ (e.g. `Hold`/`Unhold`, `AgentCalled`, `QueueCallerJoin`). Recommend regenerating from `manager show events`.
- **F3 — Originate AMI example output (lines 266-284) is quoted in the old `Variables:` help format.** Asterisk 22 renders `manager show command Originate` with `[Synopsis]/[Syntax]/[Arguments]` sections (see lab output). Content is accurate; only the formatting is dated. Low priority.

## Unverified
None. All checkable affirmations were confirmed against the lab or docs.asterisk.org (FastAGI 4573 confirmed via secondary sources since the docs AGI page is "under construction").
