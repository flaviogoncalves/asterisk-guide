# デプロイメント、監視、スケーリング

Asteriskをラボ環境で呼び出しに応答させることと、クラッシュ、再起動、アップグレード、攻撃に耐えうるサービスとして運用し、さらに監視、バックアップ、拡張を行えるようにすることは別物です。本章では、dialplanが動作した「後」に起こるすべてのことについて扱います。まずはAsteriskを生存させ続けるスーパーバイザー（systemd）から始め、コンテナへのパッケージング（本書のDockerラボを実例として使用）へと進みます。その後、構成管理とバックアップ、監視と可観測性、そしてサーバー1台では足りなくなった時に採用するパターンである高可用性とスケーリング、さらにクラウドホスティングの現実について解説します。

ここで示すすべての内容は、本書のAsterisk 22ラボ（`lab/`）で検証済みです。これは本書を通じて構築してきたものと同じコンテナです。

## 学習目標

本章を読み終えることで、以下のことができるようになります：

- systemd配下で、非rootユーザーとして、自動再起動設定を行い、Asterisk 22を確実に実行する
- DockerでAsteriskをコンテナ化し、ネットワーク上のトレードオフを理解する
- `/etc/asterisk`をバージョン管理し、適切な状態をバックアップする
- CLI、CDR/CEL、AMI/ARI、メトリクスを通じて稼働中のシステムを監視する
- アクティブ/スタンバイの高可用性および水平スケーリングのパターンを適用する
- NATとファイアウォールの背後で、安全にクラウド上でAsteriskをホストする

## systemdによるAsteriskの実行

現在のすべてのLinuxディストリビューション（Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9）において、サービスマネージャーは**systemd**です。インストールに関する章で説明した通り、（`make install`中に実行される）`make config`ステップでは、ディストリビューションのinitスクリプト（Debianでは`/etc/init.d/asterisk`、RedHatでは`rc.d`スクリプト）がインストールされ、systemdがそれを自動的にサービスとしてラップします。Asteriskには、より詳細な制御のために代わりにインストールできるネイティブなsystemdユニットも`contrib/systemd/asterisk.service`配下に同梱されています。
いずれにせよ、systemdはAsteriskを運用環境で実行するためのサポートされた方法です。ビルドそのものについては『Installing Asterisk 22』を参照してください。ここでは、このサービスが何を提供し、どのように操作するかに焦点を当てます。

### サービスユニットとそのライフサイクル

`make config`によってサービスがインストールされると、ライフサイクルは通常のsystemdの操作となります：

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

運用上の注意点：

- **`restart`と正常なリロードの比較。** `systemctl restart`はプロセスを強制終了し、すべての通話を切断します。構成変更のためにこれを行うことはほぼありません。代わりにAsterisk CLIを使用してください：`asterisk -rx 'core reload'`（または`pjsip reload`のようなモジュール固有のリロード）。`systemctl restart`はアップグレードやプロセスが固まった場合のために取っておいてください。
- **実行中のデーモンへのアタッチ。** Asteriskがサービスとして実行されている状態で、コンソールを開くには`asterisk -r`（または詳細出力が必要な場合は`asterisk -rvvv`）を使用します。これは制御ソケット経由ですでに実行中のデーモンに接続するものであり、2つ目のコピーを起動するわけではありません。

### `Restart=`がsafe_asteriskに代わる

歴史的に、Asteriskは**safe_asterisk**ラッパーを通じて起動されていました。これはクラッシュ時にAsteriskを再起動するシェルスクリプトでした。systemd環境では、その役割はユニットの`Restart=`ディレクティブが担います。systemdはプロセスの終了を検知して再起動させ、そのバックオフは`RestartSec=`で制御され、クラッシュループ保護は`StartLimitIntervalSec=`/`StartLimitBurst=`によって行われます。そのため、systemdホスト上では**safe_asteriskは廃止**されており、通常は不要です。もし提供されているユニットに設定がない場合、パッケージ化されたファイルを編集せずに再起動設定を追加するクリーンな方法は、ドロップインによるオーバーライドです：

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

これを`systemctl daemon-reload && systemctl restart asterisk`で適用します。ドロップインを使用する（インストールされたユニットを直接編集するのではなく）ことで、将来の`make config`によって変更が上書きされることを防げます。

### 非rootユーザーとしての実行

Asteriskを本番環境でrootとして実行すべきではありません。rootで実行されているプロセスにリモートコード実行のバグがあればホスト全体が侵害されますが、権限のないプロセスであればそのバグは封じ込められます。これを強制するには、以下の2つの補完的な場所があります：

- **ユニットファイル / asterisk.conf。** パッケージ化されたユニットは通常、Asteriskを`asterisk`ユーザーおよびグループとして実行します。また、デーモンがバインド後に権限を降格する際に参照する`asterisk.conf`の`[options]`セクションで、`runuser`と`rungroup`を設定することもできます：

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **ファイルの所有権。** ランタイムディレクトリは、そのユーザーが書き込み可能である必要があります。アカウントを作成した後、所有権を確認してください：

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

SIP（5060）やRTP（10000+）はすべてハイポートであるため、Asteriskがそれらをバインドするのにroot権限は**不要**です。root権限が必要なのはポート25のような特権ポートのみであり、Asteriskはそれを使用しません。したがって、非特権での実行はコストなしで行えます。（セキュリティの章で、なぜこれが重要なのかを詳しく解説します。*Asterisk Security*を参照してください。）

## Asteriskのコンテナ化

コンテナはAsteriskとその正確な依存関係を1つの不変なイメージにパッケージ化するため、テストしたものがそのまま出荷されるものとバイト単位で一致します。トレードオフとなるのはリアルタイムメディアです。SIPサーバーは遅延に敏感であり、外部から到達可能な広範囲かつ予測可能なUDPポート範囲を必要としますが、コンテナのネットワークがその妨げになることがあります。本節の残りの部分では、本書のラボである`lab/Dockerfile`と`lab/docker-compose.yml`を具体的かつ実用的な例として解説し、誰もが陥る罠であるRTPとブリッジネットワークについて説明します。

### イメージ：ソースからのAsteriskビルド

ラボの`Dockerfile`は、Debian 12上でソースからAsterisk 22をビルドします。自分で書くことがなくても、その構成を読む価値はあります：

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

注目すべき3つの点：

- **バージョンが固定されている**（`ARG ASTERISK_VERSION=22.10.0`）。再現性はコンテナ化の最大の目的です。意図的にバージョンを上げ、再ビルドし、再テストしてください。
- **`--with-pjproject-bundled`と`--with-jansson-bundled`**は、Asteriskとバージョンが一致したSIPスタックをビルドします。これにより、aptパッケージへの依存を減らし、ディストリビューションのPJSIPとの不整合に悩まされることがなくなります。
- **`CMD ["asterisk", "-f", "-vvv"]`**はAsteriskを*フォアグラウンド*で実行します（`-f`、「forkしない」）。これはsystemdホストとの決定的な違いです。コンテナのメインプロセスはデーモン化してはならず、さもなければコンテナは即座に終了してしまいます。そのため、コンテナ内ではsystemdユニットを一切使用**しません**。コンテナランタイム（Dockerと`restart:`ポリシー）が、VMにおけるユニットの`Restart=`の役割を果たすスーパーバイザーとなります。

### `/etc/asterisk`のバインドマウント

このイメージには意図的に構成ファイルが**含まれていません**。代わりに`docker-compose.yml`がホストの構成ディレクトリをバインドマウントします：

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

`./asterisk/etc:/etc/asterisk:ro`は、バージョン管理された`lab/asterisk/etc`ディレクトリをコンテナの`/etc/asterisk`に読み取り専用（`:ro`）でマッピングします。このメリットは絶大です。イメージは不変かつ再利用可能なまま維持され、構成ファイルはホスト上に存在するため、編集が可能であり、何よりgitで管理（次節）できます。構成変更を適用するには、ファイルを編集してリロードするだけです（`docker compose exec asterisk asterisk -rx 'core reload'`）。再ビルドは不要です。`restart: unless-stopped`はsystemdの`Restart=`に相当するcomposeレベルの機能です。Asteriskが終了した場合はDockerがコンテナを再起動しますが、意図的に停止した場合は再起動しません。

### ホストネットワーク vs ブリッジネットワーク — RTPの問題

これはコンテナ化されたAsteriskで最もよくある失敗であるため、正確に理解しておく価値があります。デフォルトでは、Dockerはコンテナを**ブリッジ**ネットワークに配置し、`ports:`で個別のポートを公開します。シグナリングは問題ありません。5060は1つのポートだからです。問題はメディアです。RTPはUDPポートの*範囲*を使用し（ラボの`rtp.conf`は`rtpstart=10000` / `rtpend=10100`を設定）、音声が流れる可能性のある**すべて**のポートを公開しなければなりません。

ラボではまさにそれを行っています：

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

RTPの公開範囲（`10000-10100`）が`rtp.conf`と完全に一致していることに注意してください。ここを間違えて、公開するポートが少なすぎたり、設定と異なる範囲（`rtp.conf`）を指定したりすると、通話は接続されても**音声が片方向または無音**になります。これは、RTPパケットがDockerが転送していないポートに到達するためです。ブリッジモードにおけるさらなる2つの注意点：

- **数千のポートを公開するのは遅く、負荷が高い。** 本番環境のRTP範囲は通常10000–20000です。Dockerが約10000のユーザーランドプロキシ転送を作成するのは起動時に負荷がかかり、メディアパスにホップを追加します。ラボでは、1〜2回のテスト通話しか行わないため、意図的に100ポートという小さな範囲にしています。
- **SDP内のNAT。** ブリッジの背後では、Asteriskは自身のコンテナプライベートIPを認識し、それをSDPでアドバタイズする可能性があります。パブリックホスト上では、トランスポート上で`external_media_address` / `external_signaling_address`を使用してPJSIPに外部アドレスを伝え（かつ`local_net`を設定し）、NATの背後にある場合と全く同じようにする必要があります。以下の『クラウドホスティング』を参照してください。

代替案は**ホストネットワーク**（`network_mode: host`）であり、ブリッジを完全に取り除きます。コンテナはホストのネットワークスタックを共有するため、5060とRTP範囲全体がポート公開なし、メディアホップの追加なしで到達可能です。これは本番用Asteriskコンテナに推奨されるモードであり、RTP範囲の問題を完全に回避します。その代償は分離性の低下です。コンテナは任意のホストポートをバインドでき、composeのサービスごとのネットワーク機能が失われます。（ホストネットワークはLinuxの機能です。macOS/Windows上のDocker Desktopでは動作が異なるため、この教育用ラボでは明示的なポート公開を使用しています。）

### スプールとボイスメールのための永続ボリューム

コンテナの書き込み可能レイヤーは**一時的**です。コンテナを破棄すれば、書き込まれたものはすべて消滅します。Asteriskにとって、これはボイスメール、録音、発信コールスプール、ローカルデータベースが`docker compose up --build`のたびに消えることを意味します。構成ファイルはホストからバインドマウントされているため生存しますが、*状態*も同様の扱いが必要です。コンテナ内の関連するツリーは以下の通りです：

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

（ラボの実行中のコンテナにはこれらが正確に表示されます。— `/var/spool/asterisk`には`voicemail`、`monitor`、`outgoing`、`recording`が含まれ、`/var/lib/asterisk`には`astdb.sqlite3`が保持されています。）これらを保持するには、状態を保持するディレクトリに対して名前付きボリュームをマウントします：

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

教育用ラボではこれらを意図的に省略しています。設計上ステートレスで再現可能であるため、すべての`up`はクリーンな状態から始まります。しかし、本番用コンテナには**必ず**これらが必要であり、さもなければ再デプロイのたびにボイスメールが失われます。

## 構成管理とバックアップ

上記のバインドマウントは、正しいモデルを示唆しています。すなわち、`/etc/asterisk`を**コード**として扱い、それ以外を**データ**として扱うことです。

### `/etc/asterisk`をバージョン管理する

構成ディレクトリは、テンプレート化できない秘密情報を含まないプレーンテキストファイルの集合体であり、gitに最適です。リポジトリを`/etc/asterisk`で初期化します（あるいはラボのように、構成をプロジェクトの横に置いてバインドマウントします）。利点：

- すべての変更がレビュー可能かつ取り消し可能（`git diff`、`git revert`）。
- 誰がいつ何を変更したかの監査証跡が残る。
- コンテナイメージと組み合わせることで、既知の良好な構成コミットと固定されたイメージタグが、デプロイメントを完全に記述する。

Asterisk構成特有の2つの注意点：

- **秘密情報。** `pjsip.conf`（および`manager.conf`、`ari.conf`）にはパスワードが含まれます。実際の秘密情報を平文で共有リポジトリにコミットしないでください。テンプレート化し（環境ごとに1ファイル、またはデプロイ時にシークレットマネージャー/環境変数置換を使用）、gitにはプレースホルダーのみを残します。ラボの単純な`Lab-6001-secret`形式のパスワードは、プライベートなDockerサブネット内に存在する場合に*のみ*許容されます。
- **環境ごとのテンプレート化。** 開発、ステージング、本番で異なるリアルタイム値（バインドアドレス、外部IP、トランク認証情報、データベースURL）は、まさにテンプレート化すべき行であり、構成の大半を環境間で同一に保つことができます。

### バックアップ対象

git内の構成はdialplanとエンドポイントをカバーしますが、稼働中のPBXはどの構成ファイルにも含まれない*状態*を蓄積します。完全なバックアップは以下の通りです：

| 対象 | 場所 | 理由 |
|------|-------|-----|
| 構成 | `/etc/asterisk/` | dialplan、エンドポイント（gitにも存在） |
| ボイスメールと録音 | `/var/spool/asterisk/` | ユーザーデータ — 代替不可 |
| 内部データベース | `/var/lib/asterisk/astdb.sqlite3` | `DB()`キー、デバイス状態 |
| CDR / CEL | `/var/log/asterisk/cdr-csv/`またはSQLストア | 課金と履歴 |
| 外部データベース | MySQL/PostgreSQL | リアルタイム、CDR、ボイスメール |

**astdb**には言及が必要です。これはAsteriskの小さな組み込みキー/値ストア（`/var/lib/asterisk/astdb.sqlite3`にあるSQLiteファイル）であり、`DB()`のdialplan関数、デバイス状態、フォローミー設定などで使用されます。CLIから検査やバックアップのためにダンプできます：

```
asterisk -rx 'database show'
```

CDR/CEL、ボイスメール、またはPJSIP構成が外部データベースにある場合（『Asterisk Real-Time』および『Asterisk Call Detail Records』を参照）、そのデータベースがそのデータの信頼できる唯一の情報源となるため、通常のデータベースバックアップローテーションに含める必要があります。`/etc/asterisk`だけをバックアップしても不十分です。

## 監視と可観測性

見えないものは運用できません。Asteriskはその状態を、人間が素早く確認するものからメトリクスパイプラインまで、4つのレベルで公開しています：**CLI**、**CDR/CEL**レコード、**AMI/ARI**イベント、そして**メトリクスエクスポーター**です。

### CLIヘルスチェック

最も素早い「正常か？」の確認はCLIです。以下のコマンドはラボに対してライブで実行されます。まずはチャネルから：

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

静かなシステムでの`0 active calls`は正常です。忙しいシステムでは、これがリアルタイムの同時接続数となります。`core show uptime`は、プロセスが勝手に再起動していないことを確認します：

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

SIPの健全性については、`pjsip show endpoints`がすべてのエンドポイントと、その登録済みコンタクトが到達可能かどうかを表示します。ラボから：

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

ここでの`Unavailable`は、現在そのエンドポイントに登録されている電話機がないことを意味します（ラボにはライブクライアントがいません）。ソフトフォンが登録し、`qualify`がそれを確認すれば、状態は到達可能として表示されます。関連コマンド：`pjsip show contacts`（現在の登録とラウンドトリップタイム）、`pjsip show transports`、および1つのAORに対する`pjsip show aor <name>`。これらは「なぜ内線Xに到達できないのか？」という日常的なトラブルシューティングツールです。

### CDRとCEL

すべての通話は**Call Detail Record**（CDR）を残します。**Channel Event Logging**（CEL）は、チャネルごとのより詳細なイベントを追加します。CDRがアクティブかどうか、どのバックエンドが保存しているかを確認します：

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

ラボでは、最小限の構成ではCDRストレージモジュールがロードされないため、登録済みバックエンドの下に`(none)`と表示されます。つまり、レコードは計算されますがどこにも書き込まれません。本番環境ではバックエンド（CSV、またはMySQL/PostgreSQLへの`cdr_odbc`/`cdr_adaptive_odbc`）をロードし、それが課金と履歴のソースとなります。CELは**デフォルトで無効**です（`cel show status`は` reports `CEL Logging: Disabled` in the lab) and you enable it in `と表示されます）。イベントレベルの詳細が必要な場合にのみ` in the lab) and you enable it in `cel.confで有効にします。どちらも『Asterisk Call Detail Records』で詳しく解説されています。監視の観点では、CDR/CELは*履歴*記録であり、CLIは*ライブ*ビューであるという点が重要です。

### AMIとARIイベント

プログラムによるリアルタイム監視には、CLIをポーリングするのではなく、イベントのプッシュフィードが必要です：

- **AMI (Asterisk Manager Interface)** は、長年使用されているTCPイベント/コマンドプロトコル（`manager.conf`）です。サブスクライブすると、通話が発生するたびに`Newchannel`、`Hangup`、`DialBegin`、`BridgeEnter`、`PeerStatus`などのイベントを受信します。これはウォールボードや通話会計ツールのバックボーンです。ラボではAMIはデフォルトで無効です（`manager show settings`は`Manager (AMI): No`と報告します）。`manager.conf`で有効化し、ロックダウンします。
- **ARI (Asterisk REST Interface)** は、最新のHTTP + WebSocketインターフェース（`ari.conf`、組み込みHTTPサーバーで提供）です。JSONイベントストリームと詳細な通話制御を提供し、新しい統合には最適な選択肢です。

どちらも『Extending Asterisk with AMI and AGI』および『The Asterisk REST Interface (ARI)』で詳述されています。デプロイメントに関する警告：**AMIとARIは強力であり、インターネットに公開してはなりません。** HTTPサーバーをlocalhostまたは管理ネットワークにバインドし、強力でユニークな秘密情報を使用し、ポートをファイアウォールで保護してください。*Asterisk Security*を参照してください。

### メトリクス：PrometheusとGrafana

ダッシュボードとアラートのために、Asterisk 22にはPrometheusエクスポーターである**`res_prometheus.so`**（*拡張*サポートレベルのモジュール）が同梱されており、PrometheusサーバーがスクレイピングするHTTPエンドポイントでメトリクスを公開します。コアプロセス指標に加えて、チャネル、通話、エンドポイント、ブリッジ、PJSIPアウトバウンド登録をカバーするプラグ可能なプロバイダーを提供します：

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

ラボのビルドにモジュールが存在することを確認できます：

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

ラボでは構成もロードもされていないため`Not Running`と表示されます。これを有効化（`prometheus.conf`とHTTPサーバー）すると、AsteriskがPrometheusのターゲットになります。Prometheusをスクレイプエンドポイントに向け、GrafanaをPrometheusに向ければ、時系列ダッシュボード（同時通話数、登録数、ASR/ACDトレンド）とアラート（例：「アクティブ通話がゼロに低下」「登録失敗が急増」）が得られます。すでにPrometheus/Grafanaを運用しているチームにとって、CLI出力を解析するよりも、これがAsteriskを既存の可観測性に組み込む自然な方法です。

### 監視すべきSIPレスポンスコード

パイプラインが何であれ、いくつかのSIP結果はトラブルの兆候であり、アラートを出す価値があります。持続的な`401`/`407`のチャレンジ失敗や`403 Forbidden`は、ブルートフォース攻撃や構成ミスの認証情報の嵐を示唆しています（『Asterisk Security』のFail2Banを参照）。`503 Service Unavailable`はサーバーやトランクの過負荷や混雑を指し、`408 Request Timeout`/`480 Temporarily Unavailable`の急増は通常、エンドポイントが到達不能になったことを意味します（NATタイムアウト、qualify失敗）。

## 高可用性とスケーリング

Asteriskサーバー1台は単一障害点であり、通話数には上限があります。*稼働し続けること*と*規模を大きくすること*という2つの問題には、異なる答えがあります。

### フローティングIPによるアクティブ/スタンバイ

Asteriskの古典的で実績のあるHAパターンは**アクティブ/スタンバイ**です（アクティブ/アクティブではありません。Asteriskの通話状態をライブで共有するのは困難です）。同一のサーバー2台（アクティブ1台、スタンバイ1台）が、**keepalived**（VRRP）や**Pacemaker/Corosync**などのクラスターマネージャーによって管理される**フローティング（仮想）IP**を共有します。電話機やトランクは、個々のホストではなくフローティングIPに登録します。アクティブノードがヘルスチェックに失敗すると、フローティングIPはスタンバイに移動し、スタンバイが引き継ぎます。

正直な注意点：IPフェイルオーバーは**進行中の通話を切断します**。Asteriskはノード間でライブチャネル状態を複製しないため、通話中のユーザーはかけ直す必要があります。登録はqualify/登録サイクル内で再確立されます。フェイルオーバーがもたらすのは、*サービス*が手動介入なしで数秒以内に回復することであり、ほとんどのPBXにとってこれがまさに目標です。スタンバイが確実に引き継げるようにするには、両方のノードが同じ構成（git管理された`/etc/asterisk`を同一にデプロイ）と、同じ*状態*を持つ必要があります。これが次のポイントです。

### PJSIP Realtimeによる状態の外部化

アクティブ/スタンバイは、スタンバイノードがアクティブノードと同じエンドポイントと登録情報を知っている場合にのみ機能します。これを実現する方法は、**1台のボックス上のフラットファイルに状態を保持するのをやめ**、両方のノードが読み取る共有データベースに移動することです。**PJSIP Realtime**（データベースに裏打ちされたSorcery）はまさにこれを行います。エンドポイント、AOR、認証、そして重要なことに**登録**（`ps_contacts`テーブル）が、`pjsip.conf`やローカルメモリではなくMySQL/PostgreSQLに存在します。両方のAsteriskノードが同じデータベースを指すため、一方のノードを通じて登録された電話機は他方からも認識されます。これは『Asterisk Real-Time』（PJSIP Realtime / Sorceryセクション）で解説されています。ここでのデプロイメントのポイントは、**状態の外部化がHAと水平スケーリングの両方の前提条件である**ということです。それがなければ、各ノードは孤島となります。

同じ論理を他の状態にも適用してください。CDR/CELは共有SQLストアへ、ボイスメールは共有/複製ストレージ（または`ODBC_STORAGE`）へ、依存するastdbキーはデータベースへ。状態が外部化されれば、Asteriskノードは交換可能なフロントエンドに近づきます。

### 前段のSIPプロキシ（OpenSIPS）

1台のサーバーの容量を*超えて*スケールするには、Asteriskメディアサーバーのプールを前段で受ける**SIPプロキシ/ロードバランサー**を配置します。**OpenSIPS**は、目的特化型の非常に高スループットなSIPプロキシです（メディアに触れることなく、数十万の登録を処理し、シグナリングをルーティングします）。プロキシは世界に対して単一のSIPアドレスを提示し、登録/ロケーションサービスを維持し、Asteriskバックエンドに通話を分散させます。この分離（登録とルーティングを行う軽量なプロキシ層と、実際の通話処理（IVR、キュー、会議、トランスコーディング）を行う水平スケーリング可能なAsterisk層）こそが、大規模デプロイメントが1台のボックスを超えて成長する方法です。（SipPulseプラットフォーム自体が、まさにこの理由でメディア/アプリケーションサーバーの前段にOpenSIPSを使用しています。）

### メディアスケーリング

プロキシは*シグナリング*を安価に分散させますが、**メディアは高価なリソースです**。RTPリレー、特にコーデック間のトランスコーディング（例：Opus ↔ G.711）や大規模会議の実行はCPUバウンドであり、サーバーの限界を決定づける要因です。戦略：

- 可能であれば**トランスコーディングを回避**してください。共通のコーデックをエンドツーエンドでネゴシエーションし、Asteriskがトランスコーディングではなくネイティブにブリッジ（パススルー）するようにします。これがメディア容量を増やす最大の要因です。
- プロキシの背後にAsteriskノードを追加して**メディアを水平方向にスケール**させます。それぞれが同時通話の分担を担います。
- **ブラウザメディアを専用のWebRTCゲートウェイ（例：Janus）にオフロード**し、PBXがすべてのブラウザのDTLS-SRTPストリームを終端およびリレーしないようにします。『WebRTC with Asterisk』を参照してください。このAsteriskとゲートウェイの分離について解説しています。

容量のサイジングは、登録ユーザー数ではなく、**同時通話数とトランスコーディング負荷**で行ってください。ほとんどアイドル状態の10,000台の登録済み電話機は、200の同時トランスコーディング会議よりもはるかに安価です。

## クラウドホスティング

クラウドVM（AWS、GCP、Azure、VPS）上でAsteriskを実行することは一般的でうまく機能しますが、クラウドネットワークは**デフォルトでNATおよびファイアウォール保護されており**、これがSIPと競合します。以下はデプロイメント固有の懸念事項です。

### NATとSDP

クラウドVMはほぼ常にNIC上に**プライベート**IPを持ち、プロバイダーがNATする別の**パブリック**IPを持ちます。AsteriskがSDPでプライベートIPをアドバタイズすると、リモートの電話機はRTPをブラックホールに送信してしまい、古典的な片方向/無音の症状が発生します。トランスポート上でPJSIPにパブリックIDを伝えてください：

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*`はAsteriskがパブリックピアにアドバタイズするアドレスを書き換えさせ、一方`local_net`はどのピアがローカル（書き換えるべきではない）かを伝えます。これは前述のブリッジDockerネットワークで議論したNAT処理と同じです。クラウドVMは実質的にNATの背後にあります。

### ファイアウォールとRTP範囲

クラウドVMには通常、**プロバイダーの**セキュリティグループ/ネットワークACLと、**ホストの**iptablesという2つのファイアウォールが適用されます。両方で同じポートを開く必要があり、ポリシーはセキュリティの章のものです。救済された第1版のルールセット（`docs/legacy-labs/configs/Lab7/rules.v4`）はその形状を捉えています。SIPとRTP範囲を受け入れ、確立済み/関連する通信を受け入れ、残りをドロップします：

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

ここで重要なセキュリティの章の2つの修正点：SIP/TLSを実行する場合は**5061をTCPで**（UDPではなく）開き、ファイアウォール内のRTP UDP範囲が`rtp.conf`の`rtpstart`/`rtpend`と完全に一致していることを確認してください。これはコンテナ上で公開する範囲と同じです。ここでiptables/Fail2Banの構築を複製しないでください。***Asterisk Security*のファイアウォール、Fail2Ban、TLS/SRTPセクションに従い**（Fail2Banはラボがすでに`logger.conf`で有効にしている`security`ロガーチャネルを監視します）、そのポリシーをホストファイアウォールとクラウドセキュリティグループの*両方*に適用してください。

### 遅延、リージョン、SBC

- **ユーザーに近いリージョンを選択してください。** 音声は遅延に敏感です。口から耳までの片方向遅延が約150msを超えると顕著になります。電話機やトランクの大部分に最も近いリージョンでVMをホストしてください。大陸をまたぐメディアは明らかに品質が低下します。
- **インターネットに面したデプロイメントには、前段にSBCを配置してください。** **Session Border Controller**はSIP/RTPをエッジで終端し、トポロジーを隠蔽し、NATを正規化し、Asteriskに到達する前にDoSやスキャントラフィックを吸収します。セキュリティの章の核心的な推奨事項である「*生のAsteriskをインターネットに公開しない*」は、VMのパブリックIPが起動後数分でスキャンされるクラウドでは二重に適用されます。SBC（または最低限、OpenSIPSのような堅牢なSIPプロキシとFail2Ban）が標準的なエッジです。

## まとめ

デプロイメントとは、動作するdialplanが信頼できるサービスになるプロセスです。VM上では、Asteriskを**systemd**配下で**非root**ユーザーとして実行し、ユニットの`Restart=`に生存させ続け（safe_asteriskは廃止）、構成変更には`systemctl restart`ではなく`core reload`を使用します。Dockerによる**コンテナ化**（本書のラボと同様）は、git管理された`/etc/asterisk`から**バインドマウント**された構成を持つ、不変で固定されたイメージを提供します。落とし穴はメディアであるため、**ホストネットワーク**を使用するか、`rtp.conf`と**完全に一致する**RTPポート範囲を公開し、再デプロイ後も状態が維持されるようにスプール/ボイスメール/astdb用の**永続ボリューム**をマウントしてください。構成をコードとして扱い、構成ファイルがキャプチャしない**状態をバックアップ**してください：ボイスメール、録音、`astdb.sqlite3`、CDR/CEL。システムを4つのレベルで**監視**してください。ライブビューにはCLI（`core show channels`、`pjsip show endpoints`）、履歴には**CDR/CEL**、プログラムイベントには**AMI/ARI**、ダッシュボードとアラートにはGrafanaへの**`res_prometheus`**エクスポーターを使用し、AMI/ARIはパブリックインターネットから遮断してください。**稼働し続ける**には、**フローティングIP**を使用してアクティブ/スタンバイを実行し（フェイルオーバーでライブ通話が切断されることを許容）、**成長させる**には、**PJSIP Realtime**で状態を外部化し、**OpenSIPS**でメディアサーバーのプールを前段に配置し、トランスコーディングを最小限に抑えてください。なぜなら、**サーバーの限界を決めるのは登録数ではなくメディアだからです**。最後に、**クラウド**ではVMをNATの背後にあるものとして扱い（`external_*`、`local_net`）、ホストとプロバイダーのセキュリティグループの両方でセキュリティの章に従ってファイアウォールを開き、低遅延のリージョンを選択し、生のAsteriskを公開せず、エッジに**SBC**を配置してください。

## クイズ

1. systemdホストにおいて、クラッシュしたAsteriskを再起動するという古い`safe_asterisk`ラッパーの役割に代わるものは何ですか？
   - A. cronジョブ
   - B. ユニットファイルの`Restart=`ディレクティブ
   - C. `systemctl enable`
   - D. astdb
2. 稼働中のAsteriskに対して、**通話を切断せずに**構成変更を適用するには、どうすべきですか？
   - A. `systemctl restart asterisk`
   - B. サーバーを再起動する
   - C. `asterisk -rx 'core reload'`
   - D. コンテナイメージを再ビルドする
3. コンテナ化された（ブリッジネットワーク）Asteriskで通話は接続されるが**音声がない**場合、最も可能性の高い原因は？
   - A. dialplanが間違っている
   - B. 公開されたRTP UDPポート範囲が`rtp.conf`の`rtpstart`/`rtpend`と一致していない
   - C. CDRが無効になっている
   - D. CLIに到達できない
4. コンテナの再デプロイで状態を失わないように、**永続ボリューム**としてマウントしなければならないディレクトリはどれですか？（すべて選択してください）
   - A. `/var/spool/asterisk`（ボイスメール、録音）
   - B. `/var/lib/asterisk`（astdb）
   - C. `/etc/asterisk`（すでにホストからバインドマウントされている）
   - D. `/usr/sbin`
5. アクティブな通話のライブカウントを表示するCLIコマンドはどれですか？
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. Asterisk 22において、Prometheus/Grafanaスタックに通話/チャネルメトリクスを公開するサポートされた方法はどれですか？
   - A. `full`ログファイルの解析
   - B. `res_prometheus.so`モジュール
   - C. AGIスクリプト
   - D. 方法はない
7. 複数のAsteriskノード間でのHAフェイルオーバーと水平スケーリングの両方の前提条件は何ですか？
   - A. rootとして実行する
   - B. 状態の外部化（例：共有データベース内のPJSIP Realtime登録）
   - C. CDRを無効にする
   - D. ブリッジネットワークを使用する
8. 1台のAsteriskサーバーが処理できる同時通話数を最も直接的に制限するリソースは何ですか？
   - A. 登録済みユーザー数
   - B. メディア処理、特にトランスコーディング
   - C. `/etc/asterisk`のサイズ
   - D. CDRバックエンド
9. クラウドVMにおいて、Asteriskがパブリックアドレスをアドバタイズしてリモート音声が機能するようにする`pjsip.conf`トランスポート設定はどれですか？（すべて選択してください）
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. インターネットに面したクラウドデプロイメントにおいて、セキュリティの章の核心的なルールは？
    - A. 常に2つのNICを実行する
    - B. 生のAsteriskをインターネットに公開しない。エッジにSBC（または堅牢なプロキシ + Fail2Ban）を配置する
    - C. UDPのみを使用する
    - D. TLSを無効にする

**回答：** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
