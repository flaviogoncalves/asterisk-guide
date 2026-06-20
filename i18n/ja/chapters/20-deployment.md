# デプロイ、モニタリング & スケーリング

Asterisk がラボで電話に応答できるようにするのは一つのことです；クラッシュ、再起動、アップグレード、攻撃者に耐えるサービスとして実行し、かつ観測・バックアップ・拡張できるようにするのは別です。この章では *dialplan* が機能した後に起こるすべてについて扱います。まず Asterisk を常に稼働させる supervisor（systemd）から始め、次にコンテナにパッケージ化する方法（本書独自の Docker ラボを実例として）を説明し、続いて構成管理とバックアップ、モニタリングと可観測性、そしてサーバーが一台では足りない場合に取るべきパターン、すなわち高可用性とスケーリング、そしてクラウドでのホスティングの現実について解説します。

示されているすべては、本書の Asterisk 22 ラボ（`lab/`）で検証されています — 本書全体で構築してきた同じコンテナです。

## Objectives

この章の終わりまでに、次のことができるようになります。

- systemd の下で Asterisk 22 を信頼性高く、非 root ユーザーとして、かつ自動再起動付きで実行する
- Docker で Asterisk をコンテナ化し、ネットワークに関するトレードオフを理解する
- `/etc/asterisk` をバージョン管理下に置き、正しい状態をバックアップする
- CLI、CDR/CEL、AMI/ARI、メトリクスを通じて稼働中のシステムを監視する
- アクティブ/スタンバイの高可用性と水平スケーリングパターンを適用する
- NAT とファイアウォールの背後で、クラウド上に安全に Asterisk をホストする

## Running Asterisk under systemd

現在の主要な Linux ディストリビューション — Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9 — では、サービスマネージャは **systemd** です。インストール章で示した`make config`ステップ（`make install`中に実行）により、ディストリビューション用の init スクリプト（Debian では`/etc/init.d/asterisk`、RedHat では`rc.d`スクリプト）がインストールされ、systemd が自動的にサービスとしてラップします。Asterisk には`contrib/systemd/asterisk.service`にネイティブの systemd ユニットが同梱されており、より細かい制御が必要な場合はそれを代わりにインストールできます。いずれにせよ、systemd は Asterisk を実行するためにサポートされている本番環境向けの方法です。ビルド自体については *Installing Asterisk 22* を参照してください；ここではサービスが提供する機能とその操作方法に焦点を当てます。

### The service unit and its lifecycle

`make config`がサービスをインストールしたら、ライフサイクルは通常の systemd と同様です。

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

A few operational notes:

- **`restart` vs. a graceful reload.** `systemctl restart` tears down the process and
  drops every call. For configuration changes you almost never want that — use the
  Asterisk CLI instead: `asterisk -rx 'core reload'` (or a module-specific reload such
  as `pjsip reload`). Reserve `systemctl restart` for upgrades or a wedged process.
- **Attach to the running daemon.** With Asterisk running as a service, open its
  console with `asterisk -r` (or `asterisk -rvvv` for verbose output). This connects
  to the already-running daemon over its control socket; it does not start a second
  copy.

### `Restart=` replaces safe_asterisk

Historically Asterisk was launched through the **safe_asterisk** wrapper, a shell
script that re-spawned Asterisk if it crashed. Under systemd that job belongs to the
unit's `Restart=` directive — systemd notices the process exit and brings it back,
with back-off controlled by `RestartSec=` and crash-loop protection by
`StartLimitIntervalSec=`/`StartLimitBurst=`. So on a systemd host **safe_asterisk is
superseded** and generally unnecessary. If your shipped unit does not already set it,
a drop-in override is the clean way to add restart-on-failure without editing the
packaged file:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Apply it with `systemctl daemon-reload && systemctl restart asterisk`. Using a drop-in
(rather than editing the installed unit) means a future `make config` will not clobber
your change.

### 非 root ユーザーとして実行する

Asterisk は本番環境で root として実行すべきではありません — root で動作しているプロセスにリモートコード実行バグがあると、ホスト全体が侵害されますが、特権のないプロセスで同じバグが発生した場合は影響が限定されます。これが適用される場所は次の二つです:

- **The unit / asterisk.conf.** The packaged unit normally runs Asterisk as the
  `asterisk` user and group. You can also (or instead) set `runuser` and `rungroup` in
  the `[options]` section of `asterisk.conf`, which the daemon honours when it drops
  privileges after binding:```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **ファイル所有権。** ランタイムディレクトリはそのユーザーが書き込み可能でなければなりません。アカウントを作成した後、所有権を確認してください：```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Because SIP (5060) and RTP (10000+) are all high ports, Asterisk does **not** need
root to bind them — only port-25-style privileged ports would, which Asterisk does not
use. Running unprivileged is therefore free. (The Security chapter expands on why this
matters; see *Asterisk Security*.)

## コンテナ化 Asterisk

コンテナは Asterisk とその正確な依存関係を 1 つの不変イメージにパッケージ化するため、テストしたものがバイト単位で出荷するものと同一になります。トレードオフはリアルタイムメディアです。SIP サーバはレイテンシに敏感で、外部から到達可能な広範かつ予測可能な UDP ポート範囲が必要ですが、コンテナのネットワーキングがそれを妨げることがあります。このセクションの残りでは、本書独自のラボ — `lab/Dockerfile` と `lab/docker-compose.yml` — を具体的で動作する例として歩みながら、誰もがハマりやすい罠である RTP とブリッジドネットワーキングについて説明します。

### イメージ: ソースから Asterisk をビルドする

ラボの `Dockerfile` は Debian 12 上でソースから Asterisk 22 をビルドします。その全体像は、たとえ自分で書くことがなくても読む価値があります。

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Three things to call out:

- **The version is pinned** (`ARG ASTERISK_VERSION=22.10.0`). Reproducibility is the
  whole point of containerizing — bump it deliberately, rebuild, retest.
- **`--with-pjproject-bundled` and `--with-jansson-bundled`** build the SIP stack
  version-matched to Asterisk, so you depend on fewer apt packages and never fight a
  distro PJSIP that is out of step.
- **`CMD ["asterisk", "-f", "-vvv"]`** runs Asterisk in the *foreground* (`-f`, "do not
  fork"). This is the key difference from a systemd host: a container's main process
  must not daemonize, or the container would exit immediately. So in a container you do
  **not** use the systemd unit at all — the container runtime (Docker, plus `restart:`
  policy) becomes the supervisor that the unit's `Restart=` was on a VM.

### Bind-mounting `/etc/asterisk`

The image deliberately contains **no** configuration. Instead `docker-compose.yml`
bind-mounts the host's config directory in:

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro`はバージョン管理された`lab/asterisk/etc`ディレクトリをコンテナの`/etc/asterisk`に読み取り専用（`:ro`）でマッピングします。そのメリットは大きく、イメージは不変で再利用可能なまま、設定はホスト上にあり、編集可能で、重要なことに git で管理できます（次のセクション）。設定変更を適用するには、ファイルを編集してリロードするだけです — `docker compose exec asterisk asterisk -rx 'core reload'` — 再ビルドは不要です。`restart: unless-stopped`は compose レベルでの systemd の`Restart=`に相当します。Docker は Asterisk が終了した場合にコンテナを再起動しますが、意図的に停止した場合は再起動しません。

### Host vs. bridged networking — the RTP problem

これはコンテナ化された Asterisk の失敗で最も一般的なケースであり、正確に理解する価値があります。デフォルトでは Docker はコンテナを **bridged** ネットワークに配置し、`ports:`で個別のポートを公開します。シグナリングは問題なく、5060 が 1 つのポートです。問題はメディアにあります。RTP は UDP ポートの *範囲* を使用します（ラボの`rtp.conf`が`rtpstart=10000` / `rtpend=10100`を設定）。**音声を運ぶ可能性のあるすべてのポート**を公開しなければなりません。

ラボはまさにそれを行っています：

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Note the RTP publish range (`10000-10100`) matches `rtp.conf` exactly. Get this wrong —
publish too few ports, or a different range than `rtp.conf` — and calls connect but
have **one-way or no audio**, because the RTP packets land on a port Docker is not
forwarding. Two further cautions with bridged mode:

- **Publishing thousands of ports is slow and heavy.** A production RTP range is
  typically 10000–20000. Docker creating ~10000 userland proxy forwards is expensive at
  start-up and adds a hop in the media path. The lab keeps a deliberately small
  100-port range because it only ever runs one or two test calls.
- **NAT in the SDP.** Behind the bridge, Asterisk sees its private container IP and may
  advertise it in SDP. On a public host you must tell PJSIP its external address with
  `external_media_address` / `external_signaling_address` on the transport (and set
  `local_net`), exactly as you would behind any NAT — see *Cloud hosting* below.

The alternative is **host networking** (`network_mode: host`), which removes the bridge
entirely: the container shares the host's network stack, so 5060 and the whole RTP
range are reachable with no port publishing and no extra media hop. This is the
recommended mode for a real Asterisk container — it sidesteps the RTP-range problem
completely. Its cost is isolation: the container can bind any host port and you lose
compose's per-service network. (Host networking is a Linux feature; on Docker Desktop
for macOS/Windows it behaves differently, which is partly why this teaching lab uses
explicit published ports instead.)

### Persistent volumes for spool and voicemail

A container's writable layer is **ephemeral** — destroy the container and anything it
wrote is gone. For Asterisk that means voicemail, recordings, the outgoing call spool
and the local database would vanish on every `docker compose up --build`. Configuration
survives because it is bind-mounted from the host; *state* needs the same treatment.
Inside the container the relevant trees are:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(The lab's running container shows exactly these — `/var/spool/asterisk` contains
`voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` holds
`astdb.sqlite3`.) To preserve them, mount named volumes for the directories that hold
state you care about:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

The teaching lab omits these on purpose — it is stateless and reproducible by design, so every `up` is a clean slate — but a production container **必ず** have them, or you will lose voicemail on the first redeploy.

## Configuration management and backups

上記のバインドマウントは正しいモデルを示唆しています：`/etc/asterisk`を **code** とみなし、残りを **data** と扱うことです。

### Keep `/etc/asterisk` in version control

設定ディレクトリはテキストファイルのフラットな集合で、テンプレート化できない機密情報は含まれていません—git に最適です。`/etc/asterisk`でリポジトリを初期化します（または、ラボではプロジェクトと同じ場所に設定を置き、バインドマウントします）。メリット：

- すべての変更がレビュー可能で元に戻せます（`git diff`、`git revert`）。
- 誰がいつ何を変更したかの監査トレイルが残ります。
- コンテナイメージと組み合わせることで、既知の良好な設定コミットと固定されたイメージタグが
  デプロイメント全体を記述します。

Asterisk 設定に特有の注意点がいくつかあります：

- **Secrets.** `pjsip.conf`（および`manager.conf`、`ari.conf`）にはパスワードが含まれます。実際の機密情報を平文のまま共有リポジトリにコミットしないでください—テンプレート化します（環境ごとにファイルを分けるか、デプロイ時にシークレットマネージャ／環境変数置換を使用）し、git にはプレースホルダーだけを残します。ラボの簡易的な`Lab-6001-secret`スタイルのパスワードは、プライベートな Docker サブネット上にあるため **only** 許容されます。
- **Per-environment templating.** 開発、ステージング、プロダクションで異なるリアルタイム値（バインドアドレス、外部 IP、トランク認証情報、データベース URL）は、テンプレート化すべき行であり、環境間で設定の大部分を同一に保ちます。

### What to back up

git で管理する設定はダイヤルプランやエンドポイントをカバーしますが、稼働中の PBX は設定ファイルに存在しない *state* を蓄積します。完全なバックアップは次のとおりです：

| What | Where | Why |
|------|-------|-----|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (also in git) |
| Voicemail & recordings | `/var/spool/asterisk/` | user data — irreplaceable |
| Internal database | `/var/lib/asterisk/astdb.sqlite3` | `DB()` keys, device state |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` or SQL store | billing & history |
| External databases | your MySQL/PostgreSQL | realtime, CDR, voicemail |

**astdb** についても言及しておきます：これは Asterisk の小規模な組み込みキー/バリューストア（`/var/lib/asterisk/astdb.sqlite3`にある SQLite ファイル）で、`DB()`ダイヤルプラン関数、デバイス状態、follow-me 設定などに使用されます。CLI からダンプして確認またはバックアップできます：

```
asterisk -rx 'database show'
```

CDR/CEL やボイスメール、PJSIP 設定が外部データベースに保存されている場合（*Asterisk Real-Time* および *Asterisk Call Detail Records* を参照）、そのデータベースがデータの唯一の真実の情報源となり、通常のデータベースバックアップサイクルに含める必要があります—`/etc/asterisk`だけのバックアップでは不十分です。

## Monitoring and observability

自分で見えないものは操作できません。Asterisk は 4 つのレベルで状態を公開します。人がすぐに目で確認できるものからメトリクスパイプラインまで、**CLI**、**CDR/CEL** レコード、**AMI/ARI** イベント、そして **metrics exporters** です。

### CLI health checks

最も高速な「正常か？」チェックは CLI です。以下のコマンドはラボに対してリアルタイムで実行されます。まずはチャンネルです：

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls`は静かなシステムでは正常です；忙しいシステムではリアルタイムの同時実行です。 `core show uptime`はプロセスが再起動していないことを確認します。

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

For SIP health, `pjsip show endpoints` shows every endpoint and whether its registered
contacts are reachable. From the lab:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` は単に、これらのエンドポイントに現在電話が登録されていないこと（ラボにライブクライアントがいない）を意味します — ソフトフォンが登録され、`qualify` がそれを確認すると、状態はコンタクトが到達可能であることを示します。補助コマンド: `pjsip show contacts`（現在の登録と往復時間）、`pjsip show transports`、および `pjsip show aor <name>`（単一 AOR 用）。これらは日常的な「なぜ extension X に到達できないのか？」という問題を解決するツールです。

### CDR と CEL

すべての通話は **Call Detail Record** (CDR) を残します；**Channel Event Logging** (CEL) はチャネルごとのより細かいイベントを追加します。CDR が有効であり、どのバックエンドに保存されているかを確認してください。

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

The lab shows `(none)` under registered backends because the minimal lab config loads
no CDR storage module — so records are computed but written nowhere. In production you
load a backend (CSV, or `cdr_odbc`/`cdr_adaptive_odbc` into MySQL/PostgreSQL) and that
becomes your billing and history source. CEL is **disabled by default** (`cel show
status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` only
when you need event-level detail. Both are covered in depth in *Asterisk Call Detail
Records*; for monitoring, the point is that CDR/CEL are your *historical* record, where
the CLI is your *live* view.

### AMI and ARI events

For programmatic, real-time monitoring you want a push feed of events rather than
polling the CLI:

- **AMI (Asterisk Manager Interface)** is the long-standing TCP event/command protocol
  (`manager.conf`). Subscribe and you receive `Newchannel`, `Hangup`, `DialBegin`,
  `BridgeEnter`, `PeerStatus` and similar events as calls happen — the backbone of wallboards
  and call-accounting tools. In the lab AMI is disabled by default (`manager show settings`
  reports `Manager (AMI): No`); you enable and lock it down in `manager.conf`.
- **ARI (Asterisk REST Interface)** is the modern HTTP + WebSocket interface
  (`ari.conf`, served by the built-in HTTP server). It gives a JSON event stream and
  fine-grained call control — the right choice for new integrations.

Both are detailed in *Extending Asterisk with AMI and AGI* and *The Asterisk REST
Interface (ARI)*. The deployment-relevant
warning: **AMI and ARI are powerful and must never be exposed to the internet.** Bind the
HTTP server to localhost or a management network, use strong unique secrets, and
firewall the ports — see *Asterisk Security*.

### Metrics: Prometheus and Grafana

For dashboards and alerting, Asterisk 22 ships a Prometheus exporter,
**`res_prometheus.so`** (a module with *extended* support level), which exposes metrics
on an HTTP endpoint that a Prometheus server scrapes. Alongside core process metrics it
ships pluggable providers covering channels, calls, endpoints, bridges and PJSIP
outbound registrations:

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

ラボビルドにモジュールが存在することを確認できます。

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

It shows `Not Running` because the lab does not configure or load it; enabling it
(`prometheus.conf` plus the HTTP server) turns Asterisk into a Prometheus target. Point
Prometheus at the scrape endpoint and Grafana at Prometheus, and you get time-series
dashboards (concurrent calls, registrations, ASR/ACD trends) and alerting (e.g. "active
calls dropped to zero" or "registration failures spiking"). For teams already running
Prometheus/Grafana this is the natural way to fold Asterisk into existing observability,
rather than parsing CLI output.

### SIP response codes worth watching

Whatever the pipeline, a few SIP results signal trouble and are worth alerting on:
sustained `401`/`407` challenge failures or `403 Forbidden` suggest a brute-force or
misconfigured-credential storm (cross-reference Fail2Ban in *Asterisk Security*);
`503 Service Unavailable` points at an overloaded or congested server or trunk; and a
spike in `408 Request Timeout`/`480 Temporarily Unavailable` usually means endpoints
have gone unreachable (NAT timeout, qualify failures).

## High availability and scaling

One Asterisk server is a single point of failure and has a finite call ceiling. The two
problems — *staying up* and *getting bigger* — have different answers.

### Active/standby with a floating IP

The classic, well-trodden HA pattern for Asterisk is **active/standby** (not
active/active — call state in Asterisk is hard to share live). Two identical servers,
one active, one standby, share a **floating (virtual) IP** managed by a cluster manager
such as **keepalived** (VRRP) or **Pacemaker/Corosync**. Phones and trunks register to
the floating IP, not to either real host. If the active node fails its health check, the
floating IP moves to the standby, which takes over.

The honest caveat: an IP failover **drops calls in progress** — Asterisk does not
replicate live channel state between nodes, so anyone mid-call must redial. Registrations
re-establish within a qualify/registration cycle. What failover buys you is that the
*service* recovers in seconds without manual intervention, which for most PBXs is exactly
the goal. To make the standby genuinely able to take over, both nodes need the same
configuration (your git'd `/etc/asterisk`, deployed identically) and the same *state* —
which is the next point.

### Externalize state with PJSIP Realtime

Active/standby only works if the standby knows about the same endpoints and
registrations as the active node. The way to achieve that is to **stop keeping state in
flat files on one box** and move it to a shared database both nodes read. **PJSIP
Realtime** (Sorcery backed by a database) does exactly this: endpoints, AORs, auths —
and, importantly, **registrations** (the `ps_contacts` table) — live in MySQL/PostgreSQL
instead of `pjsip.conf` and local memory. Both Asterisk nodes point at the same database,
so a phone registered through one node is visible to the other. This is covered in
*Asterisk Real-Time* (the PJSIP Realtime / Sorcery section); here the deployment point is
that **externalizing state is the prerequisite for both HA and horizontal scaling** —
without it, each node is an island.

Apply the same logic to the rest of your state: CDR/CEL into a shared SQL store, voicemail
on shared/replicated storage (or `ODBC_STORAGE`), and the astdb keys you depend on into a
database. Once state is external, the Asterisk nodes become closer to interchangeable
front-ends.

### SIP proxies in front (OpenSIPS)

To scale *beyond* one server's capacity you put a **SIP proxy/load balancer** in front of
a pool of Asterisk media servers. **OpenSIPS** is a purpose-built, very
high-throughput SIP proxy (they handle hundreds of thousands of registrations and route
signaling without touching media). The proxy presents a single SIP address to the world,
maintains the registration/location service, and distributes calls across the Asterisk
back-ends. This separation — a lightweight proxy tier doing registration and routing, a
horizontally-scalable Asterisk tier doing the actual call processing (IVR, queues,
conferences, transcoding) — is how large deployments grow past a single box. (The SipPulse
platform itself uses OpenSIPS in front of its media/application servers for exactly this
reason.)

### Media scaling

The proxy distributes *signaling* cheaply; **media is the expensive resource**. RTP
relaying, and especially transcoding between codecs (e.g. Opus ↔ G.711) or running large
conferences, is CPU-bound and is what actually caps a server. Strategies:

- **Avoid transcoding** wherever possible — negotiate a common codec end-to-end so
  Asterisk bridges natively (pass-through) instead of transcoding. This is the single
  biggest media-capacity win.
- **Scale media horizontally** by adding Asterisk nodes behind the proxy; each carries a
  share of the concurrent calls.
- **Offload browser media** to a dedicated WebRTC gateway (e.g. Janus) so the PBX is not
  also terminating and relaying every browser's DTLS-SRTP stream — see *WebRTC with
  Asterisk*, which discusses exactly this Asterisk-plus-gateway split.

Size capacity by **concurrent calls and transcoding load**, not by registered users —
10,000 registered phones that are mostly idle are far cheaper than 200 simultaneous
transcoded conferences.

## Cloud hosting

Running Asterisk on a cloud VM (AWS, GCP, Azure, a VPS) is common and works well, but the
cloud network is **NAT'd and firewalled by default**, which fights with SIP. The
following are the deployment-specific concerns.

### NAT and the SDP

A cloud VM almost always has a **private** IP on its NIC and a separate **public** IP that
the provider NATs to it. If Asterisk advertises the private IP in SDP, remote phones send
RTP into a black hole — the classic one-way/no-audio symptom. Tell PJSIP its public
identity on the transport:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` make Asterisk rewrite the address it advertises to public peers, while
`local_net` tells it which peers are local (and should *not* be rewritten). This is the
same NAT handling discussed for bridged Docker networking above — a cloud VM is, in
effect, behind NAT.

### Firewall and the RTP range

Two firewalls usually apply on a cloud VM: the **provider's** security group / network
ACL, and the **host's** iptables. Both must open the same ports, and the policy is the
one from the Security chapter. The salvaged 1st-edition ruleset
(`docs/legacy-labs/configs/Lab7/rules.v4`) captures the shape — accept SIP and the RTP
range, accept established/related, drop the rest:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Two corrections the Security chapter makes that matter here: open **5061 on TCP** (not
UDP) if you run SIP/TLS, and remember that the RTP UDP range in your firewall must match
`rtpstart`/`rtpend` in `rtp.conf` exactly — the same range you publish on a container.
Do not duplicate the iptables/Fail2Ban build here; **follow the firewall, Fail2Ban and
TLS/SRTP sections of *Asterisk Security*** (Fail2Ban watches the `security` logger channel
that the lab already enables in `logger.conf`) and apply that policy in *both* the host
firewall and the cloud security group.

### Latency, region and the SBC

- **Choose a region close to your users.** Voice is latency-sensitive — one-way mouth-to-ear
  latency above ~150 ms is noticeable. Host the VM in the region nearest the bulk of your
  phones and trunks; cross-continent media is audibly worse.
- **Put an SBC in front for any internet-facing deployment.** A **Session Border
  Controller** terminates SIP/RTP at the edge, hides your topology, normalizes NAT, and
  absorbs DoS and scanning traffic before it reaches Asterisk. The Security chapter's core
  recommendation — *do not expose raw Asterisk to the internet* — applies doubly in the
  cloud, where your VM's public IP is being scanned within minutes of coming up. An SBC (or
  at minimum a hardened SIP proxy like OpenSIPS plus Fail2Ban) is the standard
  edge.

## Summary

Deployment is where a working dialplan becomes a dependable service. On a VM, run
Asterisk under **systemd** as a **non-root** user, letting the unit's `Restart=` keep it
alive (safe_asterisk is superseded) and using `core reload` rather than `systemctl
restart` for config changes. **Containerizing** with Docker — as the book's lab does —
gives you an immutable, pinned image with config **bind-mounted** from a git'd
`/etc/asterisk`; the catch is media, so either use **host networking** or publish an RTP
port range that **exactly matches `rtp.conf`**, and mount **persistent volumes** for
spool/voicemail/astdb so state survives a redeploy. Treat config as code and **back up the
state** config does not capture: voicemail, recordings, `astdb.sqlite3`, and CDR/CEL.
**Observe** the system at four levels — the CLI (`core show channels`, `pjsip show
endpoints`) for the live view, **CDR/CEL** for history, **AMI/ARI** for programmatic
events, and the **`res_prometheus`** exporter into Grafana for dashboards and alerts —
while keeping AMI/ARI off the public internet. To **stay up**, run active/standby with a
**floating IP** (accepting that failover drops live calls); to **grow**, externalize state
with **PJSIP Realtime**, front a pool of media servers with **OpenSIPS**, and
minimize transcoding because **media — not registrations — is what caps a server**.
Finally, in the **cloud**, treat the VM as behind NAT (`external_media_address`,
`local_net`), open the firewall per the Security chapter in both the host and the provider
security group, pick a low-latency region, and never expose raw Asterisk — put an **SBC**
at the edge.

## Quiz

1. On a systemd host, what replaces the old `safe_asterisk` wrapper's job of restarting a
   crashed Asterisk?
   - A. A cron job
   - B. The unit file's `Restart=` directive
   - C. `systemctl enable`
   - D. The astdb
2. To apply a configuration change to a running Asterisk **without dropping calls**, you should:
   - A. `systemctl restart asterisk`
   - B. Reboot the server
   - C. `asterisk -rx 'core reload'`
   - D. Rebuild the container image
3. A containerized (bridged-network) Asterisk connects calls but has **no audio**. The most likely cause is:
   - A. The dialplan is wrong
   - B. The published RTP UDP port range does not match `rtpstart`/`rtpend` in `rtp.conf`
   - C. CDR is disabled
   - D. The CLI is unreachable
4. Which directories must be mounted as **persistent volumes** so a container redeploy does not lose state? (check all that apply)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (already bind-mounted from the host)
   - D. `/usr/sbin`
5. Which CLI command gives the live count of active calls?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. In Asterisk 22, the supported way to expose call/channel metrics to a Prometheus/Grafana stack is:
   - A. Parsing the `full` log file
   - B. The `res_prometheus.so` module
   - C. AGI scripts
   - D. There is none
7. What is the prerequisite for both HA failover and horizontal scaling across multiple Asterisk nodes?
   - A. Running as root
   - B. Externalizing state (e.g. PJSIP Realtime registrations in a shared database)
   - C. Disabling CDR
   - D. Using bridged networking
8. Which resource most directly caps how many simultaneous calls one Asterisk server can handle?
   - A. The number of registered users
   - B. Media processing, especially transcoding
   - C. The size of `/etc/asterisk`
   - D. The CDR backend
9. On a cloud VM, which `pjsip.conf` transport settings make Asterisk advertise its public address so remote audio works? (check all that apply)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. For an internet-facing cloud deployment, the Security chapter's core rule is:
    - A. Always run two NICs
    - B. Never expose raw Asterisk to the internet; put an SBC (or hardened proxy + Fail2Ban) at the edge
    - C. Use UDP only
    - D. Disable TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
