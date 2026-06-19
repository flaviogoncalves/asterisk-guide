# Fact-check ledger — Call Queues (Chapter 14)

Verified: 22 · Wrong (fixed): 6 · Unverified: 3

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "Call queues also know as ACD (Automatic Call Distribution)" | 3 | VERIFIED | app_queue "True Call Queueing" — lab: `module show like app_queue` (app_queue.so Running, core) |
| 2 | "autofill=yes ... does not wait until a call is answered, but rather works in parallel" | 41-44 | VERIFIED | queues.conf.sample (branch 22): "autofill=yes makes sure that ... waiting callers are connecting with available members in a parallel fashion" — https://raw.githubusercontent.com/asterisk/asterisk/22/configs/samples/queues.conf.sample |
| 3 | "Queues are defined in the queues.conf configuration file" | 38 | VERIFIED | https://docs.asterisk.org/Configuration/Applications/Asterisk-Queues/Building-Queues/ ; queues.conf.sample (branch 22) |
| 4 | "Agents are defined in the agents.conf file" | 38,70,131 | VERIFIED | lab: `core show application AgentLogin` See Also lists agents.conf; app_agent_pool reads agents.conf |
| 5 | "ringall: Plays all channels available until someone answers" | 101 | VERIFIED | queues.conf.sample (branch 22) strategy=ringall (default) |
| 6 | "leastrecent: Distributes to the least recent member" | 102 | VERIFIED | queues.conf.sample: leastrecent = ring interface least recently hung up |
| 7 | "fewestcalls: Distributes to the member with fewest calls" | 103 | VERIFIED | queues.conf.sample: fewestcalls = fewest completed calls |
| 8 | "random: Ring random interface" | 104 | VERIFIED | queues.conf.sample lists random strategy |
| 9 | "wrandom: ... use the member's penalty as a weight when calculating their metric" | 105 | VERIFIED | queues.conf.sample wrandom description (penalty-weighted metric) |
| 10 | "rrmemory: Uses round robin with memory; remembers where it left off" | 106 | VERIFIED | queues.conf.sample: rrmemory = round robin with memory |
| 11 | "rrordered: Same as rrmemory, except the queue member order from the config file is preserved" | 107 | VERIFIED | queues.conf.sample rrordered description (verbatim match) |
| 12 | "linear: Rings members in the order they are listed ...; for dynamic members, in the order they were added" | 108 | VERIFIED | queues.conf.sample linear description (verbatim match) |
| 13 | "The roundrobin strategy was replaced by rrmemory ... and is no longer available" | 110 | VERIFIED | roundrobin absent from queues.conf.sample (branch 22) strategy list; only ringall/leastrecent/fewestcalls/random/wrandom/rrmemory/rrordered/linear present |
| 14 | "All strategies listed above are confirmed present in Asterisk 22" | 110 | VERIFIED | queues.conf.sample (branch 22) lists all 8 strategies the chapter enumerates |
| 15 | "AgentLogin ... It always returns -1 ... silent login (s option)" | 154,156 | VERIFIED | lab: `core show application AgentLogin` — option s "silent login"; Since 12.0.0; app_agent_pool |
| 16 | "AddQueueMember(queuename[,interface[,penalty...]]) ... if device already exists returns an error" | 158-163 | VERIFIED | lab: `core show application AddQueueMember` — AQMSTATUS MEMBERALREADY; Syntax matches (extra optional args exist) |
| 17 | "RemoveQueueMember(queuename[,interface]) ... if device does not belong returns an error" | 166-171 | VERIFIED | lab: `core show application RemoveQueueMember` — RQMSTATUS NOTINQUEUE; Syntax `RemoveQueueMember(queuename[,interface])` |
| 18 | "Queue ... sets the QUEUE status variable ... TIMEOUT, FULL, JOINEMPTY, LEAVEEMPTY, JOINUNAVAIL, LEAVEUNAVAIL" | 141-150 | VERIFIED | lab: `core show application Queue` — ${QUEUESTATUS} values include all six (plus CONTINUE, WITHDRAW added in 22) |
| 19 | "monitor-format ... monitor-type = MixMonitor ... monitor-join = yes" | 292,301-303 | VERIFIED | queues.conf.sample (branch 22): monitor-type MixMonitor only supported option; monitor-format gsm/wav/wav49; monitor-join |
| 20 | "context ... define a context in the queue configuration ... one-digit extensions menu" | 320 | VERIFIED | queues.conf.sample: "If a 'context' is specified ... caller enters an extension ... taken out of queue" |
| 21 | "A queue will send the calls first to users with lower penalty values" | 324 | VERIFIED | queues.conf.sample: member penalty — higher penalties considered last |
| 22 | "set the QUEUE_PRIO ... Higher values mean higher priority (FIFO default 0)" | 338,346 | VERIFIED | https://docs.asterisk.org/Configuration/Dialplan/Variables/Channel-Variables/Asterisk-Standard-Channel-Variables/Various-application-variables/ ; queues.conf.sample priority |
| 23 | "the command core show agents" / "show agents" to check agent status | 64,68,116,178,184 | WRONG (fixed) | No such CLI command; lab: `core show agents` → "No such command"; correct is `agent show all` — lab: `agent show all` lists agents. Fixed to `agent show all` / `queue show`. |
| 24 | "SetMusicOnHold(default)" used in dialplan example | 277 | WRONG (fixed) | lab: `core show application SetMusicOnHold` → "not registered". Replaced with `Set(CHANNEL(musicclass)=default)`. MusicOnHold/StartMusicOnHold/StopMusicOnHold are the surviving apps — lab: `core show applications like usicOnHold` |
| 25 | "agentcallbacklogin() ... It is not available in Asterisk 22" | 350-352 | VERIFIED | lab: `core show application AgentCallbackLogin` → "not registered" |
| 26 | "agentcallbacklogin() was deprecated in version 1.2 and was removed in Asterisk 12" | 352 | UNVERIFIED | Could not confirm exact versions from a primary source. chan_agent→app_agent_pool replacement landed in Asterisk 12 (ReviewBoard r/2657), but AgentCallbackLogin itself was deprecated/removed earlier (commonly cited 1.4). Removal-from-22 fact is verified (#25); the specific "1.2 / 12" versions are not corroborated. |
| 27 | "recorded using Asterisk's monitor or mixmonitor application" | 292 | UNVERIFIED | The standalone `Monitor()` application is removed in 22 — lab: `core show application Monitor` → "not registered"; only MixMonitor/StopMixMonitor exist. In queues.conf context, monitor-type accepts only MixMonitor. Phrase "monitor application" no longer maps to a real app; author should reword to "MixMonitor". Left for author (borderline: may refer to the monitor-* config feature). |
| 28 | "Since chan_sip was removed in Asterisk 21, a static queue member must reference ... PJSIP/1001 rather than SIP/1001" | 425 | VERIFIED | chan_sip removed in 21; lab: `module show like chan_sip.so` → 0 modules loaded; PJSIP is the registered SIP channel — lab: `core show channeltypes` lists PJSIP |
| 29 | "All events from queues are logged to /var/log/asterisk/queue_log" | 358 | VERIFIED | https://docs.asterisk.org/Configuration/Applications/Asterisk-Queues/Building-Queues/ (queue_log) ; lab CLI `queue` help references queue logging |
| 30 | queue_log event list (ABANDON, CONNECT, ENTERQUEUE, COMPLETECALLER, RINGNOANSWER, TRANSFER, etc.) | 360-376 | UNVERIFIED | Event names are consistent with historical queuelog.txt, but AGENTCALLBACKLOGOFF corresponds to the removed callback-login feature and is unlikely to be emitted in 22. Could not fully corroborate the full 22 event set against a primary doc page. Author should verify AGENTCALLBACKLOGOFF/SYSCOMPAT against current app_queue source. |
| 31 | "Dial(agent/<name>)" to dial an agent | 57,114 | VERIFIED | app_agent_pool provides Agent channel via AgentRequest/AgentLogin — lab: `module show like app_agent_pool` Running; Agent device state per AgentLogin docs |

## Unverified items the author must resolve before print

- Line 352: exact deprecation/removal versions of `AgentCallbackLogin` ("deprecated in 1.2 and removed in Asterisk 12"). Its absence from Asterisk 22 IS confirmed; the specific version numbers are not corroborated by a primary source. Recommend dropping the version specifics or sourcing them.
- Line 292: "Asterisk's monitor or mixmonitor application" — the standalone `Monitor()` application is removed in Asterisk 22 (only `MixMonitor` remains). Reword to MixMonitor; the queues.conf `monitor-type` setting only supports MixMonitor.
- Lines 360-376: queue_log event catalog — confirm against current app_queue (notably `AGENTCALLBACKLOGOFF`, tied to the removed callback-login mechanism, and `SYSCOMPAT`).

## Corrections applied
- Line 277: `SetMusicOnHold(default)` → `Set(CHANNEL(musicclass)=default)` (app removed in 22; lab confirmed).
- Lines 64, 68, 116, 178, 184: `core show agents` / `show agents` → `agent show all` (and `queue show` for queues); the book's command does not exist in 22 (lab confirmed `agent show all`).
