---
theme: seriph
title: 'CDR and CEL'
info: |
  ## Asterisk Guide — Chapter 13
  Call Detail Records and Channel Event Logging. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# CDR and CEL

Chapter 13

<div class="abs-bl m-6 text-sm opacity-70">
  Asterisk Guide · Asterisk 22 LTS · PJSIP-first
</div>

<style>
h1 { color: #1C5D99; }
/* QA: keep code inside the 16:9 frame — shrink slightly + wrap long lines (lossless) */
.slidev-layout pre { font-size: 0.8em; line-height: 1.32; }
.slidev-layout pre code { white-space: pre-wrap; overflow-wrap: anywhere; }
</style>

---
layout: default
---

# Objectives

By the end of this chapter you will be able to:

<v-clicks>

- **Describe** where and in what format Asterisk records calls
- **Configure** CSV and custom CDR backends
- **Generate** records into a database using **ODBC**
- **Manipulate** CDRs from the dial plan with `Set(CDR(...))`
- **Implement** an authentication scheme integrated with billing
- **Distinguish** CDR billing summaries from **CEL** per-event logging

</v-clicks>

<!--
This is the accounting chapter: every call leaves a record, and you decide where it lands.
-->

---
layout: section
---

# What gets recorded — CDR vs. CEL

---

# CDR vs. CEL

Two complementary logging subsystems — they coexist, they do not replace each other.

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

### CDR — Call Detail Record

- **One summary row per call**
- The standard for **billing** and statistics
- Fields: src, dst, channel, duration, billsec, disposition…
- Default backend writes CSV text files

</div>
<div>

### CEL — Channel Event Logging

- **Many rows per call** — one per event
- Channel state changes, bridge enter/leave, transfer legs
- For **fraud detection**, QA, advanced reporting
- Configured in `cel.conf`, stored via `cel_odbc` / `cel_custom`

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
CEL <strong>complements</strong> CDR — billing summaries keep flowing while CEL adds granular per-event detail.
</div>

---
layout: section
---

# The CDR format

---

# The CDR format

Asterisk generates one CDR per call. By default it lands in
`/var/log/asterisk/cdr-csv/` as comma-separated text.

<div grid="~ cols-2 gap-8 text-sm" class="mt-2">
<div>

- **accountcode** — account number (department / unit)
- **src / dst** — caller ID number, destination
- **dcontext** — destination context
- **clid** — caller ID with name text
- **channel / dstchannel** — channels used
- **lastapp / lastdata** — last app and its arguments

</div>
<div>

- **start / answer / end** — call timestamps
- **duration** — seconds from dial to hang-up
- **billsec** — seconds from answer to hang-up
- **disposition** — ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION
- **amaflags** — DEFAULT, OMIT, BILLING, DOCUMENTATION
- **userfield** — your own free-form field

</div>
</div>

---

# A single CDR row

![A CDR row from SELECT * FROM cdr](/images/13-call-detail-records-img01.png)

<div class="mt-2 text-sm opacity-70">
One summary row per call. Channels are PJSIP; <code>amaflags 3 = DOCUMENTATION</code>. Extra columns (e.g. <code>CDR(jitter)</code>) come for free with <code>cdr_adaptive_odbc</code>.
</div>

---
layout: section
---

# CSV and custom backends

---

# cdr.conf and cdr_csv

By default Asterisk sends every CDR to a CSV text file via `cdr_csv.so` —
fine for small businesses, and easy to import into a spreadsheet.

```bash
asterisk*CLI> module show like cdr_
```

```text
Module                 Description                              Use Count  Status
cdr_adaptive_odbc.so   Adaptive ODBC CDR backend                0          Running
cdr_csv.so             Comma Separated Values CDR Backend       0          Running
cdr_custom.so          Customizable Comma Separated Values CDR  0          Running
cdr_manager.so         Asterisk Manager Interface CDR Backend   0          Running
cdr_odbc.so            ODBC CDR Backend                         0          Running
cdr_sqlite3_custom.so  SQLite3 Custom CDR Module                0          Not Running
```

<div class="mt-2 text-sm opacity-70">
CDRs are written to <strong>every</strong> loaded backend at once. Trim the list in <code>modules.conf</code>.
</div>

---

# Loading only what you need

Disable the backends you do not want in `modules.conf` so only
`cdr_csv` (backup) and `cdr_adaptive_odbc` (database) stay active.

```ini
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

<div class="mt-3 text-sm opacity-70">
With <code>autoload=yes</code> set, every module loads unless you <code>noload</code> it explicitly.
</div>

---

# Customizing the CSV — cdr_custom.conf

`cdr_custom.conf` lets you pick the exact columns and order written to a file.

```ini
;
; Mappings for custom config file
;
[mappings]
Master.csv => "${CDR(clid)}","${CDR(src)}","${CDR(dst)}","${CDR(dcontext)}","${CDR(channel)}","${CDR(dstchannel)}","${CDR(lastapp)}","${CDR(lastdata)}","${CDR(start)}","${CDR(answer)}","${CDR(end)}","${CDR(duration)}","${CDR(billsec)}","${CDR(disposition)}","${CDR(amaflags)}","${CDR(accountcode)}","${CDR(uniqueid)}","${CDR(userfield)}"
```

<div class="mt-3 text-sm opacity-70">
Each mapping is <code>filename =&gt; "template"</code> built from <code>${CDR(...)}</code> variables.
</div>

---
layout: section
---

# Dispositions, account codes & AMA flags

---

# Dispositions and AMA flags

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

### Disposition — what happened

- `ANSWERED`
- `NO ANSWER`
- `BUSY`
- `FAILED`
- `CONGESTION`

</div>
<div>

### amaflags — Automated Message Accounting

- `DEFAULT`
- `OMIT`
- `BILLING`
- `DOCUMENTATION`

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<code>amaflags</code> is <strong>not</strong> a <code>pjsip.conf</code> endpoint option in Asterisk 22 — set it per call from the dial plan.
</div>

---

# Account codes & billing flags

The **account code** is a free-form string (stored in an 80-char field),
usually used to tag a call to a department or business unit.

<div grid="~ cols-2 gap-8 mt-2">
<div>

**Per-endpoint account code** — `pjsip.conf`

```ini
[8576]
type=endpoint
accountcode=Support
```

</div>
<div>

**Per-call, from the dial plan**

```ini
exten => _9XXX,1,Set(CDR(accountcode)=Support)
 same => n,Set(CHANNEL(amaflags)=billing)
 same => n,Dial(PJSIP/8584,30,tT)
```

</div>
</div>

<div class="mt-3 text-sm opacity-70">
Read it back with the channel variable <code>${CDR(accountcode)}</code>. The AMA flag can also be set with <code>Set(CDR(amaflags)=billing)</code>.
</div>

---
layout: section
---

# Controlling the CDR from the dial plan

---

# Set(CDR(...)) and related functions

<div class="text-sm">

| Function / app | What it does |
|----------------|--------------|
| `Set(CDR(accountcode)=acct)` | Tag the record to a department / unit |
| `Set(CDR(amaflags)=billing)` | Set the AMA flag (default, omit, documentation, billing) |
| `Set(CDR(userfield)=value)` | Write your own free-form field |
| `AppendCDRUserField(value)` | Append data to the user field |
| `Set(CDR_PROP(disable)=1)` | Stop any CDR being written for this channel (`0` re-enables) |
| `ResetCDR()` | Zero the record — reset `start`/`answer`, wipe variables (`v` keeps them) |

</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<code>NoCDR()</code> was removed in Asterisk 21 — use <code>Set(CDR_PROP(disable)=1)</code> instead.
</div>

---

# Custom CDR columns

With `cdr_adaptive_odbc`, the **user field stores automatically** when a
`userfield` column exists — no recompile.

```ini
exten => 100,1,Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
 same => n,Set(CDR(userfield)=premium-route)
```

<div class="mt-3 text-sm">

- Define a CDR variable in the dial plan, add the matching **column** to the table — adaptive mapping does the rest.
- For plain **CSV** user fields you must edit `cdr_csv.c` and recompile Asterisk.

</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<code>cdr_mysql</code> was removed in Asterisk 19 (no native MySQL CDR driver on 22) — use <code>cdr_adaptive_odbc</code> with a MySQL ODBC driver.
</div>

---
layout: section
---

# Sending CDRs to a database (ODBC)

---

# Why ODBC? The available backends

<div grid="~ cols-2 gap-8 text-sm" class="mt-2">
<div>

- `cdr_csv` — CSV text files
- `cdr_adaptive_odbc` — **preferred** for databases
- `cdr_odbc` — unixODBC (legacy)
- `cdr_pgsql` — PostgreSQL
- `cdr_mysql` — MySQL (**removed in Asterisk 19**)
- `cdr_freetds` — Sybase / MSSQL
- `cdr_manager` — CDR to AMI
- `cdr_radius` — RADIUS
- `cdr_sqlite3_custom` — SQLite3

</div>
<div>

**Why `cdr_adaptive_odbc`**

- The only backend with **connection pooling** — no new connection per write, far better performance
- **Customizable** — add a CDR variable, add a column, done
- The direction the Asterisk team has clearly favored

</div>
</div>

---

# Prepare the database

Install the ODBC stack, then create the database and user.

```bash
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

```sql
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
```

```bash
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb < mysql_cdr.sql
```

<div class="mt-2 text-sm opacity-70">
Install the MySQL Connector/ODBC driver from dev.mysql.com, then register it with <code>myodbc-installer</code>.
</div>

---

# Define and test the DSN

Create the Data Source Name in `/etc/odbc.ini`, then prove it with `isql`
**before** touching Asterisk.

```ini
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

```text
isql -v astconn astdb supersecret
> show tables
```

<div class="mt-2 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Do <strong>not</strong> proceed to Asterisk configuration until <code>isql</code> connects and lists tables.
</div>

---

# Wire Asterisk to ODBC

Two files: `res_odbc.conf` defines the connection, `cdr_adaptive_odbc.conf`
points the CDR backend at a table.

<div grid="~ cols-2 gap-6 mt-2">
<div>

**`res_odbc.conf`**

```ini
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

</div>
<div>

**`cdr_adaptive_odbc.conf`**

```ini
[cdr]
connection=cdr
table=cdr
```

</div>
</div>

```text
asterisk*CLI> odbc show
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

<div class="mt-1 text-sm opacity-70">
<code>connection</code> points at the <code>[cdr]</code> block in <code>res_odbc.conf</code>; <code>table</code> is where rows are written. Then <code>reload cdr_adaptive_odbc</code>.
</div>

---
layout: section
---

# Authentication integrated with billing

---

# Billing the authenticated user

`Authenticate()` lets you bill a call to a user who enters a password —
the account code lands on the CDR.

```ini
exten => _9011.,1,Authenticate(secret,a)   ; a = stamp the code as accountcode
 same => n,Dial(PJSIP/trunk/${EXTEN:1},20,tT)
 same => n,Hangup()
```

<div class="text-sm opacity-80">On three wrong tries <code>Authenticate</code> plays a failure prompt and <strong>hangs up</strong> — there is no priority-jump fall-through.</div>

<div grid="~ cols-2 gap-8 text-sm mt-3">
<div>

**`Authenticate(password[,options])` options**

- `a` — set the account code to the password
- `d` — treat the parameter as an Asterisk DB key

</div>
<div>

- `r` — remove the key after success (with `d`)
- `m` — the parameter is a file of account codes

</div>
</div>

```text
asterisk*CLI> database put senha 123456 1
```

---

# Passwords from voicemail

`VMAuthenticate()` works like `Authenticate()` but validates against
`voicemail.conf` passwords.

```ini
exten => _9011.,1,VMAuthenticate(${CALLERID(num)}@default,s)
 same => n,Dial(PJSIP/trunk/${EXTEN:1},20,tT)
 same => n,Hangup()
```

<div class="text-sm opacity-80"><code>s</code> skips the prompts; the only valid option. On failure the app hangs up.</div>

<div class="mt-3 text-sm">

- A specific **mailbox** → only that mailbox password is valid.
- **No mailbox** → the authenticated mailbox lands in `${AUTH_MAILBOX}`.
- Option `s` (silent) suppresses the prompt.

</div>

---
layout: section
---

# Channel Event Logging (CEL)

---

# CEL — granular per-event data

Where CDR gives one summary row, CEL records **each event** during a call.

<div grid="~ cols-2 gap-8 mt-2">
<div>

**What CEL captures**

- Individual channel state transitions
- Bridge enter / leave events
- Attended-transfer legs

```ini
; /etc/asterisk/cel.conf
[general]
enable=yes
```

</div>
<div>

**Backends & use cases**

- Stored via `cel_odbc` or `cel_custom`
- The `cel.conf` pattern mirrors `cdr.conf`
- Great for fraud detection, quality monitoring, advanced reporting

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
CEL does <strong>not</strong> replace CDR — CDR stays the billing standard while CEL adds event-level detail.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Record every call — CSV first, then a database**

Enable `cdr_csv`, place a few PJSIP calls, then send CDRs into MySQL
over `cdr_adaptive_odbc` and confirm rows with `SELECT * FROM cdr`.

See the **CDR / billing lab** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Bonus: tag a call with <code>Set(CDR(accountcode)=...)</code> and verify it in the database.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- Asterisk writes a **CDR** per call — by default CSV in `/var/log/asterisk/cdr-csv/`.
- CDRs go to **every** loaded backend at once; trim them in `modules.conf`.
- **`cdr_adaptive_odbc`** is the preferred database path — connection pooling and free custom columns.
- Shape records from the dial plan with `Set(CDR(...))`, `ResetCDR()`, and `Set(CDR_PROP(disable)=1)` (`NoCDR()` is gone).
- `Authenticate()` / `VMAuthenticate()` tie user authentication to billing.
- **CEL** adds per-event logging alongside CDR — it complements, never replaces, billing summaries.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Extending Asterisk</strong> — AMI and AGI.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 13 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which CDR backend is preferred for databases, and why — and what replaced <code>NoCDR()</code> in Asterisk 22?</em>
</div>
