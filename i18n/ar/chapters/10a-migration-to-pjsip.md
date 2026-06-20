# Migrating from chan_sip to PJSIP: a cookbook

If you are reading this with an Asterisk 13, 16, or 18 box still in production,
you have a deadline. `chan_sip` — the original SIP channel driver configured
through `sip.conf` — was **deprecated in Asterisk 17, removed from the default
build in Asterisk 19, and deleted entirely in Asterisk 21**. It does not exist in
Asterisk 22 LTS. There is no flag to turn it back on, no `noload` to dodge, no
package to install. The only SIP channel driver in Asterisk 22 is **PJSIP**
(`res_pjsip` plus `chan_pjsip`), configured through `pjsip.conf`.

So an upgrade to Asterisk 22 is, for most sites, a *SIP migration project* as much
as a version bump. The good news is that the protocol on the wire does not change
— a phone that registered and called yesterday will register and call tomorrow —
and Asterisk ships a conversion tool to do the first 80% of the translation for
you. This chapter is a practical cookbook: the concept mapping, the conversion
script, side-by-side `sip.conf` → `pjsip.conf` translations for the cases you
actually have, the dialplan and CLI changes that come with the move, realtime
(database) migration, and a checklist plus the pitfalls that bite people.

Everything here is verified against the book's Asterisk 22.10.0 lab. The deep
legacy material on `chan_sip` itself — and a worked end-to-end conversion of a
multi-device `sip.conf` — lives in the *Legacy channels* chapter; this chapter is
the focused, recipe-style companion to it.

## Objectives

By the end of this chapter, you should be able to:

- Explain why `chan_sip` is gone in Asterisk 22 and what replaces it
- Map the `sip.conf` peer/user/friend model onto the PJSIP object model
  (endpoint + aor + auth + identify + transport + registration)
- Run the `sip_to_pjsip.py` conversion script and review its output critically
- Translate the common device types (registering phone, inbound trunk, outbound
  registration) from `sip.conf` to `pjsip.conf` by hand
- Migrate NAT, media, DTMF, codec, and authentication settings option-by-option
- Update the dialplan (`SIP/` → `PJSIP/`) and the CLI (`sip show` → `pjsip show`)
- Migrate a realtime/ARA deployment from `sippeers`/`sipregs` to the Sorcery
  `ps_*` tables
- Work through a migration checklist and avoid the classic pitfalls

## لماذا الترحيل على الإطلاق

`chan_sip` خدم Asterisk لما يقرب من عقدين من الزمن، لكنه حمل ديونًا معمارية: وحدة موحدة ضخمة، كتلة إعداد واحدة لكل جهاز، دعم ضعيف للنقل المتعدد، ومكدس SIP تراجع عن المعايير RFC.  
**PJSIP** — المبني على مكدس pjproject الناضج من Teluu والذي تم إدخاله في Asterisk 12 — كان البديل الكامل من الصفر. بحلول Asterisk 21 أنهى مشروع Asterisk المهمة وأزال `chan_sip` من الشجرة.

يمكنك التأكد من الوضع على أي نظام Asterisk 22:

```
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

`chan_sip` يُعيد *0 modules loaded* — فهو ببساطة غير موجود. لا يوجد ما تُهجر إليه سوى PJSIP، لذا السؤال الحقيقي الوحيد هو *كيف*، وليس *ما إذا* كان يجب الترحيل.

## The conceptual mapping: there is no single "peer"

The mental shift that trips up everyone coming from `sip.conf` is this: **PJSIP
has no `[peer]`.** In `sip.conf` one bracketed block — a `peer`, a `user`, or a
`friend` — described *everything* about a device: its credentials, where to reach
it, its codecs, its NAT behaviour, its dialplan context. PJSIP deliberately
breaks that single block into several smaller, single-purpose objects, each tagged
with a `type=`, that *reference each other by name*:

| PJSIP object (`type=`) | Responsibility |
| --- | --- |
| `endpoint` | هوية معالجة المكالمات للجهاز: codecs, context, DTMF, media, NAT, وإشارات إلى `auth`/`aors`/`transport` |
| `aor` (Address of Record) | *أين* يمكن الوصول إلى الجهاز — جهات اتصال مسجلة أو ثابتة، `max_contacts`، qualify |
| `auth` | بيانات الاعتماد (اسم المستخدم/كلمة المرور) للمصادقة الواردة و/أو الصادرة |
| `identify` | مطابقة طلب وارد إلى endpoint بواسطة **عنوان IP المصدر** بدلاً من مستخدم `From` |
| `transport` | مقبس (مقابس) الاستماع: البروتوكول، عنوان/منفذ الربط، عناوين NAT/الخارجية |
| `registration` | **REGISTER** صادرة من Asterisk إلى موفر |

The `friend`/`peer`/`user` distinction disappears entirely — in PJSIP everything
is an `endpoint`. A single `sip.conf` friend therefore becomes, typically, three
objects (`endpoint` + `auth` + `aor`) that share a name and point at one another:

```
                sip.conf                              pjsip.conf
            ┌──────────────┐              ┌──────────┐   ┌──────┐   ┌─────┐
            │   [2000]     │   becomes    │ endpoint │──▶│ auth │   │ aor │
            │ type=friend  │  ─────────▶  │  [2000]  │   │[2000]│   │[2000]│
            │ host=dynamic │              │  auth=───┼──▶└──────┘   └──────┘
            │ secret=...   │              │  aors=───┼───────────────▶ ▲
            └──────────────┘              └────┬─────┘
                                               │ transport=
                                               ▼
                                          ┌───────────┐
                                          │ transport │  (shared by all endpoints)
                                          └───────────┘
```

The endpoint is the glue. It names a `transport` (or inherits the default), an
`auth` object, and one or more `aors`. The object model is covered in depth in
*SIP & PJSIP in depth*; here we just need it as the target of every translation.

## أداة التحويل `sip_to_pjsip.py`

Asterisk ships a Python script that reads an existing `sip.conf` and writes a
`pjsip.conf`. It does not run as a CLI command — it lives in the **Asterisk source
tree**, not the installed binaries:

```
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

On the lab's Asterisk 22.10.0 the full path is, for example,
`/usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py`. The same
directory holds `sip_to_pjsql.py` (the realtime/SQL variant, covered later) and
the helper modules `astconfigparser.py`, `astdicts.py`, and `sqlconfigparser.py`.

### تشغيلها

The script takes optional positional arguments — `[input-file [output-file]]` —
defaulting to `sip.conf` and `pjsip.conf` in the current directory:

```
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

Its only real options are:

```
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

It reads the input, prints `Converting to PJSIP...`, and writes the output file.
Internally it walks every `sip.conf` section and, per device, emits the matching
`endpoint`, `auth`, `aor`, `registration`, and (where it can infer them)
`transport` objects, applying the option mappings in the next section
automatically.

### ما تفعله — وحدودها

Treat the output as a **first draft, not a finished file.** The script is honest
about its own gaps: anything it cannot map cleanly is written into a clearly
fenced block at the top of the output file:

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[softphone]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

Notice in that real fragment that `qualify = yes` from a `sip.conf` peer landed in
the *non-mapped* block — because PJSIP qualifies on the **aor** with
`qualify_frequency` (seconds), not a boolean on the device, the script leaves it
for you to set deliberately. The practical limitations to plan for:

- **Transports are guessed, not designed.** The script emits a basic
  `transport-udp` from `bindport`/`bindaddr`, but it cannot know your TLS certs,
  your TCP needs, or your multi-bind layout. Review and rewrite the transport.
- **NAT and external addresses need a human.** `externaddr`/`localnet` may not
  survive cleanly; confirm `external_media_address`, `external_signaling_address`,
  and `local_net` on the transport by hand.
- **`qualify`, custom timers, and a handful of options land in "non-mapped".**
  Read that block top-to-bottom and decide each one.
- **Codec lists, contexts, and security need review.** Verify `disallow`/`allow`,
  the dialplan `context`, and that no device is left unintentionally open.

The workflow is therefore: run the script into a *scratch* file, diff and review
it, fold the good parts into your real `pjsip.conf`, then test exhaustively before
production.

## الترجمات جنبًا إلى جنب

هذه هي الوصفات. `sip.conf` على اليسار، المكافئ المُتحقق منه `pjsip.conf` على اليمين (مُرتّبة هنا لتناسب عرض الصفحة). تم فحص كل اسم خيار وقيمته على اليمين مقابل مختبر Asterisk 22 باستخدام `config show help res_pjsip ...`.

### هاتف مسجل (`host=dynamic`)

الجهاز الأكثر شيوعًا: هاتف مكتبي أو برنامج هاتف (softphone) يسجل الدخول باستخدام سرّ ويسجّل موقعه الخاص.

**Legacy `sip.conf`:**

```
[2000]
type=friend
host=dynamic
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmfmode=rfc2833
secret=Sup3rSecret
qualify=yes
```

**Asterisk 22 `pjsip.conf`:**

```
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
auth=2000
aors=2000

[2000]
type=auth
auth_type=digest
username=2000
password=Sup3rSecret

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

الخطوات الرئيسية: يصبح `host=dynamic` عبارة عن `aor` مع `max_contacts` (الجهاز REGISTER لتعبئة معلومات الاتصال الخاصة به)؛ يصبح `secret=` هو `password=` داخل `type=auth`؛ يصبح `qualify=yes` هو `qualify_frequency=60` (ثوانٍ) على **aor**، وليس على الـ endpoint. اضبط `max_contacts` فوق 1 فقط إذا كنت تريد حقًا نفس الحساب على عدة أجهزة في آن واحد.

### خط وارد (`host=<ip>` / `type=peer`)

مزود يرسل لك مكالمات من عنوان IP معروف. لا يوجد تسجيل هنا — تقوم بالمصادقة على حركة المرور الخاصة بـ *الناقل* عبر عنوان IP المصدر باستخدام `identify`.

**Legacy `sip.conf`:**

```
[itsp-in]
type=peer
host=203.0.113.10
context=from-pstn
disallow=all
allow=ulaw
insecure=invite
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp-in]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw

[itsp-in]
type=aor
contact=sip:203.0.113.10:5060

[itsp-in]
type=identify
endpoint=itsp-in
match=203.0.113.10
```

التحويل الحاسم هو **`insecure=invite` → `identify`**. في `chan_sip`، أخبر `insecure=invite` Asterisk "لا تتحدى INVITEs الواردة من هذا النظير للمصادقة". يحقق PJSIP نفس التأثير عن طريق *مطابقة عنوان IP المصدر مع الـ endpoint* باستخدام `type=identify`/`match=`، وهو أكثر وضوحًا وأمانًا. يصبح الـ `host=` الثابت عبارة عن `contact=` دائم على الـ `aor` بحيث يمكنك أيضًا إجراء مكالمات *صادرة* إلى الناقل. يقبل `match=` عنوان IP أو نطاق CIDR أو اسم مضيف (يُحلّ عند تحميل الإعداد — أعد التحميل إذا تغيّر عنوان IP للموفر).

### تسجيل صادر (`register =>`)

عندما يرغب الموفر أن *أنت* تسجل الدخول إلى *هم*، كان `chan_sip` يستخدم سطرًا واحدًا `register =>` في `[general]`. يستبدل PJSIP ذلك بكائن مخصص `type=registration` بالإضافة إلى `outbound_auth`.

**Legacy `sip.conf`:**

```
[general]
register => 1020:supersecret@sip.example.com:5600/9999

[itsp]
type=peer
host=sip.example.com
port=5600
defaultuser=1020
secret=supersecret
fromuser=1020
fromdomain=sip.example.com
context=from-pstn
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
outbound_auth=itsp-auth
aors=itsp-aor
from_user=1020
from_domain=sip.example.com

[itsp-auth]
type=auth
auth_type=digest
username=1020
password=supersecret

[itsp-aor]
type=aor
contact=sip:sip.example.com:5600

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:sip.example.com:5600
client_uri=sip:1020@sip.example.com:5600
contact_user=9999
retry_interval=60
```

قم بربط حقول `register =>` واحدًا لواحد: تصبح بيانات الاعتماد `1020:supersecret` هي كائن `auth` (المُشار إليه كـ `outbound_auth`)؛ يصبح `@sip.example.com:5600` هو `server_uri`؛ يصبح لاحقة `/9999` — الجزء الخاص بالمستخدم الذي يرسل الموفر المكالمات الواردة إليه — هو `contact_user=9999`. يصبح `defaultuser`/`fromuser` و`fromdomain` هما `from_user` و`from_domain` على الـ endpoint. لاحظ أن `outbound_auth` يظهر *مرتين*: يستخدم التسجيل ذلك للـ REGISTER، ويستخدم الـ endpoint ذلك للرد على تحدي `407` في INVITEs الصادرة.

## Option-by-option migration reference

When you are translating by hand (or auditing the script's output), this table is
the lookup. Every PJSIP option name and the placement (endpoint / aor / auth /
transport) is verified against the Asterisk 22 lab.

| Legacy `sip.conf` | Asterisk 22 `pjsip.conf` | Where |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (device REGISTERs) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `username=` / `defaultuser=` | `username=` | auth |
| `secret=` (auth method) | `auth_type=digest` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `disallow=` / `allow=` | `disallow=` / `allow=` (same syntax) | endpoint |
| `context=` | `context=` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | omit auth; use `type=identify` + `match=` | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

### A note on `secret` → `auth` and `auth_type`

`chan_sip`'s `secret=` becomes the `password=` field of a `type=auth` object. The
**authentication method** is set with `auth_type`. Use `auth_type=digest`. The
older values `userpass` and `md5` still work but are **deprecated and silently
converted to `digest`** — verified directly from the lab:

```
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

You will see `auth_type=userpass` in older configs and in the conversion script's
output (and in earlier chapters of this book). It is harmless, but write `digest`
in anything new.

### NAT, media, and DTMF in detail

These three are where most post-migration "it registers but has no audio" tickets
come from. The `chan_sip` shorthand `nat=force_rport,comedia` packed three
behaviours into one option; PJSIP splits them so you can reason about each:

```
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

For **media**, `directmedia` becomes `direct_media` (the underscore is the whole
change); keep `direct_media=no` whenever the call must be anchored on Asterisk —
across NAT, or to record/transcode/transfer. For **DTMF**, the RFC was
renumbered: `chan_sip`'s `dtmfmode=rfc2833` is PJSIP's `dtmf_mode=rfc4733` (same
out-of-band telephone-event mechanism, current RFC number). The lab confirms the
valid `dtmf_mode` values are `rfc4733`, `inband`, `info`, `auto`, and `auto_info`,
defaulting to `rfc4733`.

For **codecs**, nothing changes: `disallow=all` followed by `allow=ulaw` (etc.)
uses the identical syntax on the PJSIP endpoint.

## مخطط الاتصال وتغييرات سطر الأوامر

لا تتوقف عملية الترحيل عند `pjsip.conf`. هناك شيئين يتغيران في الاستخدام اليومي.

### سلاسل القنوات: `SIP/` → `PJSIP/`

يجب تحديث كل `Dial()` وإشارة قناة في `extensions.conf` التي كانت تسمي التقنية القديمة:

```
; Before (chan_sip)
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

سلاسل طلبات الاتصال تتبع النمط نفسه — يتحول `Dial(SIP/${EXTEN}@itsp)` إلى
`Dial(PJSIP/${EXTEN}@itsp)`. كما يضيف PJSIP الدالة `PJSIP_DIAL_CONTACTS()` لترن جميع جهات الاتصال المرتبطة بـ AOR مرة واحدة، ودوال مخطط الاتصال `PJSIP_HEADER()` /
`PJSIP_MEDIA_OFFER()`؛ ابحث في مخطط الاتصال عن `SIP/`،
`SIPPEER`، `SIPCHANINFO`، و`CHANNEL(...)` مرجع SIP وقم بترجمتها جميعًا.

### سطر الأوامر: `sip show ...` → `pjsip show ...`

شجرة الأوامر الكاملة `sip ...` اختفت مع السائق. البدائل:

| `chan_sip` command | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (or `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (or `core reload`) |

الأوامر القديمة لا تتصرف بشكل مختلف فقط — بل لم تعد موجودة. في
المختبر، يُعيد `sip show peers` *No such command*، بينما `pjsip show endpoints`،
`pjsip show aors`، `pjsip show auths`، `pjsip show contacts`،
`pjsip show registrations`، و`pjsip show identifies` كلها موجودة. أكثر أمر مفيد لاستكشاف الأخطاء — مسجل حزم SIP الذي كان يطبع كل رسالة
مع `sip set debug` — هو الآن **`pjsip set logger on`** (مع `pjsip set logger
host <ip>` للتركيز على نظير واحد).

## Realtime (ARA) migration

If you ran `chan_sip` from a database (Asterisk Realtime Architecture), your
devices lived in the `sippeers` table and registrations in `sipregs`. PJSIP uses a
completely different storage layer — **Sorcery** — with one table *per object
type*. The mapping:

| `chan_sip` realtime table | PJSIP / Sorcery table(s) |
| --- | --- |
| `sippeers` | `ps_endpoints`, `ps_aors`, `ps_auths` (one row each, split out) |
| `sipregs` | `ps_contacts` (dynamic registrations) |
| — (outbound `register=>`) | `ps_registrations` |
| — (IP matching) | `ps_endpoint_id_ips` (the `identify` objects) |
| — (domain aliases) | `ps_domain_aliases` |

The conceptual split is the same as the flat-file case: one `sippeers` row becomes
*three* rows in three tables (`ps_endpoints` + `ps_aors` + `ps_auths`) that
reference each other by the endpoint name.

Two things make this tractable:

- **The schema is generated for you.** Asterisk ships Alembic migrations under
  `contrib/ast-db-manage/` that create every `ps_*` table. Run
  `alembic upgrade head` against the `config` database to build the current PJSIP
  schema rather than writing DDL by hand.
- **There is a SQL conversion script.** Alongside `sip_to_pjsip.py` sits
  **`sip_to_pjsql.py`** in the same `contrib/scripts/sip_to_pjsip/` directory; it
  reuses the same `convert()` logic but emits a `pjsip.sql` file of `INSERT`
  statements for the `ps_*` tables instead of a flat config file. As with the
  flat-file tool, review the output before loading it.

Finally, point `sorcery.conf` at your database so PJSIP reads endpoints, aors,
auths, and contacts from the `ps_*` tables (via `res_config_odbc` /
`res_pjsip_realtime`), exactly as `extconfig.conf` once pointed `sippeers` at the
database for `chan_sip`. The realtime mechanics are covered in the *Realtime*
chapter; the migration-specific point is simply *which tables map to which*.

## قائمة التحقق للترحيل

ترتيب عملي للخطوات عند الانتقال إلى بيئة إنتاج:

1. **الجرد.** قوّم كل جهاز، وصلة، و`register =>` في `sip.conf` (أو كل صف من `sippeers`/`sipregs`). لاحظ إعدادات NAT المخصصة، والترميز، وإعدادات DTMF.
2. **شغّل المحول في ملف مؤقت.**  
   `sip_to_pjsip.py sip.conf pjsip_generated.conf`. **لا** توجهه إلى `pjsip.conf` الحي.
3. **اقرأ كتلة "العناصر غير المعيّنة"** في أعلى المخرجات وحل كل سطر — خصوصًا `qualify`، المؤقتات، وأي شيء يتعلق بـ NAT.
4. **صمّم النقل(ات) يدوياً.** نقل واحد لكل IP/منفذ؛ أضف TLS/TCP حسب الحاجة؛ اضبط `external_*_address` و`local_net` لصناديق السحابة/NAT.
5. **تحقق من المصادقة.** أكد `auth_type=digest`، أسماء المستخدمين، وكلمات المرور على كل كائن `auth`.
6. **تحقق من NAT/الوسائط/DTMF.** `force_rport`/`rewrite_contact`/`rtp_symmetric`، `direct_media`، `dtmf_mode=rfc4733` لكل نقطة نهاية حسب المتطلبات.
7. **حدّث مخطط الاتصال.** `SIP/` → `PJSIP/` في كل مكان؛ افحص وظائف `SIP*` ومتغيّرات القناة.
8. **حدّث السكريبتات والمراقبة.** أي أداة أو مستهلك AMI قام بتحليل مخرجات `sip show ...` يجب أن ينتقل إلى `pjsip show ...` / إجراءات PJSIP AMI.
9. **أعد التحميل وتحقق.** `module reload res_pjsip.so`، ثم `pjsip show endpoints`، `pjsip show registrations`، `pjsip show identifies`.
10. **اختبر باستخدام مسجل الحزم.** `pjsip set logger on`؛ أجرِ تسجيلًا، مكالمة واردة، ومكالمة صادرة واقرأ تبادل SIP من البداية إلى النهاية.

## Common pitfalls

- **`alwaysauthreject` is built-in now — don't look for it.** `chan_sip` needed
  `alwaysauthreject=yes` so it wouldn't leak which extensions existed by replying
  differently to bad usernames. PJSIP does the secure thing by design: it never
  reveals whether an endpoint exists. There is no `alwaysauthreject` option to
  set. The related protection — throttling unidentified senders — is the global
  `unidentified_request_count` / `unidentified_request_period`, on by default.

- **`insecure=invite` is not a PJSIP option — use `identify`.** There is no
  `insecure=` in `pjsip.conf`. The way to accept unauthenticated INVITEs from a
  known carrier is to *identify the endpoint by source IP* with `type=identify` /
  `match=`. Match as narrowly as possible (specific host IPs, not wide CIDRs), and
  back it with a `type=acl` — an IP-matched trunk with no auth is a toll-fraud
  target.

- **One transport per IP/port.** You cannot bind two transports to the same
  IP:port, and you cannot bind multiple TCP or TLS transports of the same IP
  version. The conversion script may emit a transport that collides with one you
  already have — consolidate to a single, deliberately designed transport layer.

- **`qualify=yes` doesn't translate to a boolean.** It belongs on the **aor** as
  `qualify_frequency=<seconds>`. The converter drops `qualify=yes` into the
  non-mapped block precisely because there is no equivalent boolean on the
  endpoint.

- **`secret=` is not an endpoint option.** Credentials live only in a `type=auth`
  object that the endpoint *references* (`auth=` for inbound, `outbound_auth=` for
  outbound). Putting a password on the endpoint does nothing.

- **The CLI and any scraping scripts break silently.** `sip show ...` returns "No
  such command", not an error your monitoring will necessarily catch. Audit every
  cron job, Nagios check, and AMI client for `sip ` commands before cutover.

## Summary

Migrating to Asterisk 22 means migrating off `chan_sip`, because the driver was
removed in Asterisk 21 and PJSIP is the only SIP channel that remains. The core of
the work is re-expressing each `sip.conf` `peer`/`user`/`friend` — which packed
everything into one block — as a set of cooperating PJSIP objects: an `endpoint`
plus an `auth`, an `aor`, and, depending on the device, an `identify` (inbound
trunk), a `registration` (outbound login), and a shared `transport`. The
`sip_to_pjsip.py` script in `contrib/scripts/sip_to_pjsip/` does the bulk
translation and honestly flags what it cannot map in a "Non mapped elements"
block, but its output is a first draft: design the transport, NAT, and security by
hand and test before production. Around the config, update the dialplan
(`SIP/` → `PJSIP/`) and your fingers and scripts (`sip show` → `pjsip show`,
`sip set debug` → `pjsip set logger`). Realtime deployments move from
`sippeers`/`sipregs` to the Sorcery `ps_endpoints`/`ps_aors`/`ps_auths`/
`ps_contacts` tables, with `sip_to_pjsql.py` and the `contrib/ast-db-manage`
schema to help. Watch the pitfalls — `alwaysauthreject` is built-in,
`insecure=invite` becomes `identify`, `qualify=yes` becomes
`qualify_frequency`, and one transport per IP/port — and the cutover is
mechanical rather than mysterious.

## Quiz

1. لماذا يجب على نشر Asterisk 22 استخدام PJSIP لـ SIP؟
   - A. `chan_sip` أبطأ لكنه لا يزال متاحًا
   - B. `chan_sip` تم إزالته في Asterisk 21 ولا يوجد في Asterisk 22
   - C. PJSIP هو الافتراضي لكن يمكن تحميل `chan_sip` باستخدام `modules.conf`
   - D. `chan_sip` يعمل فقط مع TLS في Asterisk 22

2. كتلة `sip.conf` `type=friend` واحدة تصبح عادةً أي مجموعة من كائنات PJSIP؟
   - A. `type=peer` واحدة
   - B. `type=endpoint` فقط
   - C. `type=endpoint` + `type=auth` + `type=aor`
   - D. `type=transport` + `type=registration`

3. في `sip.conf`، `host=dynamic` (الجهاز يسجل موقعه الخاص) يطابق:
   - A. `type=identify` مع `match=dynamic`
   - B. `type=aor` مع `max_contacts` (الجهاز يُسجِّل REGISTER)
   - C. `direct_media=yes` على الطرفية
   - D. `type=registration`

4. برنامج التحويل `sip_to_pjsip.py` هو:
   - A. أمر CLI: `asterisk -rx 'sip_to_pjsip'`
   - B. برنامج Python في شجرة مصدر Asterisk تحت
     `contrib/scripts/sip_to_pjsip/`
   - C. وحدة مُجمَّعة تُحمَّل عند الإقلاع
   - D. جزء من `res_pjsip.so`

5. صواب أم خطأ: مخرجات `sip_to_pjsip.py` جاهزة للإنتاج ويجب تحميلها دون مراجعة.

6. اختصار `chan_sip` `nat=force_rport,comedia` يترجم على طرفية PJSIP إلى أي ثلاثة خيارات؟
   - A. `nat=yes`، `qualify=yes`، `directmedia=no`
   - B. `force_rport=yes`، `rewrite_contact=yes`، `rtp_symmetric=yes`
   - C. `external_media_address`، `external_signaling_address`، `local_net`
   - D. `insecure=invite`، `identify`، `match`

7. يصبح `sip.conf`'s `dtmfmode=rfc2833` أي إعداد PJSIP؟
   - A. `dtmf_mode=rfc2833`
   - B. `dtmf_mode=inband`
   - C. `dtmf_mode=rfc4733`
   - D. `dtmf_mode=info`

8. في Asterisk 22، يجب أن يستخدم كائن `auth` أي `auth_type`، وما هو وضعية `userpass`؟
   - A. `auth_type=userpass`؛ إنها القيمة الوحيدة الصالحة
   - B. `auth_type=digest`؛ `userpass` مهملة وتم تحويلها إلى `digest`
   - C. `auth_type=md5`؛ `digest` مهملة
   - D. `auth_type=plaintext`؛ تم إزالة `digest`

9. مزود `chan_sip` نظير مع `insecure=invite` (يقبل INVITEs غير مصدقة من عنوان IP معروف) يُهجر إلى PJSIP باستخدام:
   - A. `insecure=invite` على الطرفية
   - B. `allowguest=yes` في `[global]`
   - C. كائن `type=identify` مع `match=<provider IP>`
   - D. `auth_type=anonymous`

10. في ترحيل realtime، يتم استبدال جدول `chan_sip` `sippeers` بأي جداول PJSIP/Sorcery؟
    - A. جدول `pjsip_peers` واحد
    - B. `ps_endpoints`، `ps_aors`، و`ps_auths`
    - C. `sipregs` و`voicemail`
    - D. `ps_contacts` فقط

**Answers:** 1 — B · 2 — C · 3 — B · 4 — B · 5 — False · 6 — B · 7 — C · 8 — B · 9 — C · 10 — B
