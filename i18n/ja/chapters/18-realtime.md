# Asterisk Real-Time

ご存知のとおり、Asterisk の設定は /etc/asterisk ディレクトリ内の複数のテキストファイルを使用して行われます。テキストファイルを使うことは簡単ですが、いくつか既知の欠点があります。

- ファイルを変更するたびに Asterisk をリロードする必要がある
- ユーザー数が多い場合、メモリ使用量が増加する
- テキストファイルだけでプロビジョニングインターフェースをコーディングするのが困難
- 既存のデータベースとの統合ができない

ARA（Asterisk Realtime）として知られるこの機能は、Anthony Minessale II、Mark Spencer、Constantine Filin によって作成され、SQL データベースとの透過的な統合を可能にするよう設計されました。LDAP インターフェースも利用可能です。このシステムは Asterisk External Configuration とも呼ばれ、/etc/asterisk/extconfig.conf で設定します。設定ファイルをデータベースのテーブルにマッピング（静的設定）したり、Asterisk をリロードすることなくオブジェクトを動的に作成するためのリアルタイムエントリを使用したりできます。

## 目的

この章の終わりまでに、読者は次のことができるようになる：

- Asterisk Real Time の利点と制限を理解すること。
- ODBC を ARA と共に使用すること。
- ODBC を使用して ARA をコンパイルおよびインストールすること。
- ラボ環境でシステムをテストすること。

## Asterisk Real Time はどのように機能しますか？

新しい Real Time アーキテクチャでは、データベース固有のコードはすべてチャンネルドライバに移動されました。チャンネルはデータベースを検索する汎用ルーチンを呼び出すだけです。その結果、ソースコードの観点からははるかにシンプルでクリーンなプロセスになります。データベースは次の 3 つの関数でアクセスされます。

- STATIC: モジュールがロードされたときに静的設定を行うために使用されます。
- REALTIME: 通話中またはその他のイベント時にオブジェクトを検索するために使用されます。


- UPDATE: オブジェクトを更新するために使用されます。

Asterisk 22 では、SIP エンドポイントは **PJSIP** スタック（`res_pjsip`）で処理されます。このスタックは **Sorcery** オブジェクトモデル上に構築されています。`realtime`ウィザードを使用すると、Sorcery はデータベースから必要に応じて各 PJSIP オブジェクトをロードし、これらのオブジェクトは従来の SIP ドライバが各通話後に破棄した使い捨ての realtime ピアではなく、通常の設定済み PJSIP オブジェクトとして存在します。

これらは実際のオブジェクトであるため、NAT トラバーサル、qualify、メッセージ待ち通知（MWI）はすべて realtime エンドポイントで通常通り機能します。（Sorcery は`memory_cache`ウィザードを介してオブジェクトをメモリにキャッシュするよう指示することもできますが、これはオプトインであり realtime ローディングとは別です。）データベース内のオブジェクトを変更すると、次回の検索時に変更が反映されます。すべての編集後にリロードする必要はありません。（廃止された`chan_sip`realtime モデルとその`sippeers`/`sipusers`ファミリーについては、*Legacy Channels* 章でのみ取り上げられています。）

## Configuring Asterisk Real Time

このラボでは、CDR 章で ODBC をインストール済みであることを前提とします。ARA は extconfig.conf テキストファイルで設定され、2 つのセクションが簡単に確認できます。最初のセクションは静的設定ファイルセクションで、テキスト設定ファイルをデータベーステーブルに置き換えることができます。2 番目のセクションはリアルタイム設定エンジンで、データベーステーブルを動的オブジェクト（ピア/ユーザー）用に設定します。静的設定にはテキストファイル、動的エントリにはデータベースを使用することは珍しくありません。この場合、最初のセクションは変更されていません。

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Asterisk Real Time architecture: configuration files and static database tables are loaded when Asterisk starts, while realtime database tables provide dynamic configuration that is read on demand during a call.](../images/18-realtime-fig01.png)

```
;
[settings]
;
; Static configuration files:
;
; file.conf => driver,database[,table]
;
; maps a particular configuration file to the given
; database driver, database and table (or uses the
; name of the file as the table if not specified)
;
;uncomment to load queues.conf via the odbc engine.
;
;queues.conf => odbc,asterisk,ast_config
;
; The following files CANNOT be loaded from Realtime storage:
;       asterisk.conf
;       extconfig.conf (this file)
;       logger.conf
;
; Additionally, the following files cannot be loaded from
; Realtime storage unless the storage driver is loaded
; early using 'preload' statements in modules.conf:
;       manager.conf
;       cdr.conf
;       rtp.conf
;
; Realtime configuration engine
;
; maps a particular family of realtime
; configuration to a given database driver,
; database and table (or uses the name of
; the family if the table is not specified
;
;example => odbc,asterisk,alttable
;ps_endpoints => odbc,asterisk
;ps_aors => odbc,asterisk
;ps_auths => odbc,asterisk
;ps_contacts => odbc,asterisk
;voicemail => odbc,asterisk
;extensions => odbc,asterisk
;queues => odbc,asterisk
;queue_members => odbc,asterisk
```

### Static configuration section

静的設定セクションは、データベース内に設定ファイルに相当する情報を格納する場所です。これらの設定は Asterisk の起動時に読み込まれます。いくつかのモジュールはリロード時にデータベースを再読込します。静的設定の例は次のとおりです。

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

静的ファイルマッピングは、オブジェクトごとのリアルタイム対応がない設定ファイルに最も有用です。PJSIP では、後述するオブジェクトごとのリアルタイムファミリ（`ps_endpoints`、`ps_aors`など）を使用し、`pjsip.conf`全体を静的ファイルとしてマッピングすることは避けてください。

上記の 3 つの例が説明されています。最初の例では、queues.conf を asteriskdb データベースの tables queues にバインドします。2 番目の例では、pjsip.conf を odbc 設定で定義された asteriskdb データベースのテーブル pjsip_conf にバインドします。最後の例では、iax.conf を LDAP ディレクトリにバインドします。MyBaseDN は検索対象となるベース DN です。前の例では、アプリケーション app_queue.so がロードされ、MySQL ドライバがデータベースをクエリして必要な情報を取得します。

### Real Time configuration section

リアルタイム設定（extconfig.conf ファイルの第 2 部分）では、ロードされる設定項目をリアルタイムで設定、更新、アンロードします。リアルタイムを使用すれば、設定をリロードする必要はありません。リアルタイム構文は次のとおりです。

```
<family name> => <driver>,<database name>[,table_name]
```

例:

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

ここでは 5 行の設定があります。最初の行では、PJSIP/Sorcery ファミリ `ps_endpoints` を asteriskdb データベースのテーブル `ps_endpoints` にバインドします。最後の行では、voicemail ファミリを asteriskdb データベースの test テーブルにバインドします。各 PJSIP オブジェクトタイプ（endpoint、aor、auth、contact）はそれぞれ独自のファミリとテーブルを持ち、完全なセットは下記の「PJSIP Realtime (Sorcery)」セクションに示されています。`voicemail`、`extensions`、`queues`、`queue_members` ファミリは Asterisk 22 でも引き続き有効です。

## PJSIP Realtime (Sorcery)

Asterisk 22 では、SIP エンドポイントは **PJSIP** スタック（`res_pjsip`）のみで処理され、これは **Sorcery** オブジェクト抽象化レイヤ上に構築されています。単一の SIP 「ピア」ではなく、PJSIP は SIP アカウントをいくつかのオブジェクトタイプに分割し、それぞれを独自の realtime テーブルに格納します。

| Sorcery object type | Realtime table | What it holds |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | アカウントごとの設定（context、codecs、DTMF など） |
| aor (address of record) | ps_aors | 登録制限と`qualify`設定 |
| auth | ps_auths | `username` / `password` 認証情報 |
| contact | ps_contacts | 動的に登録されたロケーション |
| domain alias | ps_domain_aliases | エンドポイント用の代替 SIP ドメイン |
| endpoint identifier by IP | ps_endpoint_id_ips | ソース IP でエンドポイントを一致させる |

PJSIP の realtime は 2 か所で有効化します。まず、Sorcery オブジェクトタイプを realtime にマッピングします（`extconfig.conf`）：

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

次に、Sorcery に`realtime`ウィザードを使用させ、これらのオブジェクトタイプを`sorcery.conf`で指定します。マッピング名（ここでは`res_pjsip`）は、オブジェクトを再配置するモジュールであり、右側の値は`extconfig.conf`で定義したファミリを指します：

```
[res_pjsip]
endpoint=realtime,ps_endpoints
aor=realtime,ps_aors
auth=realtime,ps_auths
domain_alias=realtime,ps_domain_aliases
contact=realtime,ps_contacts

[res_pjsip_endpoint_identifier_ip]
identify=realtime,ps_endpoint_id_ips
```

静的オブジェクトと realtime オブジェクトを混在させることができます。`sorcery.conf`からタイプを省略すると、そのオブジェクトタイプは`pjsip.conf`から読み続けます。一般的なパターンは、静的トランスポートとグローバル設定を`pjsip.conf`に保持し、エンドポイント、aors、auths、contacts をデータベースに格納することです。

### Creating the PJSIP realtime schema with Alembic

Asterisk は`contrib/ast-db-manage`以下にすべての realtime スキーマ用データベースマイグレーションを同梱しています。これは PJSIP テーブルを作成（およびバージョンアップグレード）する公式の方法であり、もはや`ps_*`テーブル定義を手書きする必要はありません。`config`マイグレーションセットには PJSIP/Sorcery テーブルが含まれています。

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

これにより`ps_endpoints`、`ps_aors`、`ps_auths`、`ps_contacts`およびその他の PJSIP テーブルが、実行中の Asterisk バージョンに合わせた正しいカラムで作成されます。（Alembic には Python の`alembic`パッケージと、MySQL/MariaDB 用の`pymysql`や PostgreSQL 用の`psycopg2`といった SQLAlchemy ドライバが必要です。）

最小限の realtime エンドポイントは、3 つのテーブルにそれぞれ 1 行ずつ存在すれば構成できます。たとえばエンドポイント`6010`の場合：

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

行を挿入した後はリロードする必要はありません。次の REGISTER/INVITE がデータベースからオブジェクトを取得します。realtime が返した内容は次のコマンドで確認できます：

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## データベース設定

extconfig.conf ファイルの設定が完了したので、テーブルを作成しましょう。一般的に、各データベース列は対応する設定ファイルのオプション名に一致します。PJSIP `ps_*` テーブルはこの規則に従います：すべての `ps_endpoints` 列は `pjsip.conf` エンドポイントオプションの名前、すべての `ps_auths` 列は認証オプションの名前、というように命名されています。例えば、以下の `pjsip.conf` エンドポイントは、

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

3 つのテーブルにまたがって 1 行として保存されます。`ps_endpoints` 行は `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000` を保持し、`ps_auths` 行は `id=4000, auth_type=userpass, username=4000, password=supersecret` を保持し、`ps_aors` 行は `id=4000, max_contacts=1` を保持します。実際に使用する列だけを入力すればよく、NULL のままにした列はオプションのデフォルト値が使用されます。たとえばエンドポイントの `callerid` パラメータが必要な場合は、`callerid` 列（列名は `pjsip.conf` オプション名と同じ）に `ps_endpoints` を入力します。

ボイスメールテーブルも同様の考え方です。その列は `voicemail.conf` フィールドにマップされます。

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

`uniqueid` は各ボイスメールユーザーごとに一意であり、オートインクリメントにできます。mailbox や context との関係は必要ありません。

### Asterisk Real Time を使用したダイヤルプランの構築

リアルタイムシステムを使ってダイヤルプランを作成することもできます。ARA は `switch` ステートメントを使用して、extensions.conf に含まれる通常のダイヤルプランにリアルタイムのエクステンションを組み込みます。エクステンションテーブルは以下のようになります。

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

`extensions` realtime ファミリは Asterisk 22 でも変更されていません。たとえば `PJSIP/4000` のように `appdata` 列が PJSIP チャネルをダイヤルするようにしてください。ダイヤルプランでは、リアルタイムを使用するために `switch` コマンドを使用する必要があります。

![Asterisk Real Time でダイヤルプランを構築: extensions.conf は `switch => realtime` ステートメントを使用して、テキストファイルではなくデータベーステーブルからエクステンション行（context、exten、priority、app、data）を取得します.](../images/18-realtime-fig02.png)

```
[local]
switch => realtime
```

or

```
[local]
switch => realtime/from-internal@extensions
```

## Lab: Installing and creating the database tables

このラボでは、Asterisk のパラメータを受け取るためのデータベースを準備します。REALTIME テーブルだけを作成します。静的な設定は設定テキストファイルに残しておきます（かっこいいでしょ？）。MySQL でのテーブル作成は以下の通りです。

Step 1: Get into the MySQL database as root.

```
mysql -u root -p
```

Step 2: Log in to the MySQL server created in the CDR labs.

```
mysql -u astdb -p
```

When asked for the password, type supersecret.

Step 3: Create the necessary tables. The legacy static schema files still ship under `contrib/realtime/` (for example `/usr/src/asterisk-22.x/contrib/realtime/mysql`), but on Asterisk 22 the recommended and version-correct way to build the realtime tables — especially the PJSIP `ps_*` tables — is the **Alembic** migrations under `contrib/ast-db-manage` (see the "Creating the PJSIP realtime schema with Alembic" section above).

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

The Alembic `config` migration set builds the PJSIP `ps_*` tables (along with `voicemail`, `extensions`, and the other realtime schemas) with exactly the columns the running Asterisk version expects, so the schema always matches the build.

Use supersecret as the password.

Step 4: Verify the creation of the tables.

```
mysql -u astdb -p astdb
mysql>use astdb;
mysql>show tables;
```

You should see the PJSIP `ps_*` tables (created by the Alembic `config` migration), along with the `voicemail`, `extensions`, and other realtime tables:

```
mysql> show tables;
+----------------------------+
| Tables_in_astdb            |
+----------------------------+
| ps_aors                    |
| ps_auths                   |
| ps_contacts                |
| ps_domain_aliases          |
| ps_endpoint_id_ips         |
| ps_endpoints               |
| ps_registrations           |
| extensions                 |
| voicemail                  |
+----------------------------+
```

(Alembic creates more tables than these — the list above shows the ones relevant to this lab.)

Step 5: The database is already configured for ODBC (since the CDR lab), so no further ODBC setup is needed here.

Step 6: Inspect and populate the tables from the MySQL client. You do not need a graphical tool such as phpMyAdmin — every step in this chapter is plain, copy-pasteable SQL run from the `mysql` command line. Connect to the `astdb` database (use `supersecret` when prompted):

```
mysql -u astdb -p astdb
```

You can confirm the columns of a table at any time with `DESCRIBE`, for example:

```
mysql> DESCRIBE ps_endpoints;
mysql> DESCRIBE ps_auths;
mysql> DESCRIBE ps_aors;
```

These tables were created by the Alembic `config` migration, so their columns already match the `pjsip.conf` option names for the running Asterisk version — you only fill in the columns you need.

## Lab: Configuring and testing ARA

このラボでは、extconfig.conf の設定をデータベースの構成とテーブルに合わせて変更します。

Step 1: Configure extconfig.conf and reload Asterisk.

```
; Realtime configuration engine
;
; maps a particular family of realtime
; configuration to a given database driver,
; database and table (or uses the name of
; the family if the table is not specified
;
ps_endpoints => odbc,cdr
ps_aors => odbc,cdr
ps_auths => odbc,cdr
ps_contacts => odbc,cdr
voicemail => odbc,cdr,voicemail
extensions => odbc,cdr,extensions
```

上記の `ps_endpoints`、`ps_aors`、`ps_auths`、および `ps_contacts` ファミリに注目してください。これらは、対応する `sorcery.conf` マッピング（「PJSIP Realtime (Sorcery)」セクション参照）と組み合わせることで、PJSIP がデータベースからアカウントを読み取ります。 `voicemail` と `extensions` ファミリは例を補完します。

Step 2: Real Time extension test. Create a new `6010` endpoint by inserting one row into each of `ps_auths`, `ps_aors`, and `ps_endpoints`, then try to register this endpoint with a softphone. Run the following SQL in the `mysql` client (`mysql -u astdb -p astdb`):

```sql
INSERT INTO ps_auths (id, auth_type, username, password)
VALUES ('6010-auth', 'userpass', '6010', 'supersecret');

INSERT INTO ps_aors (id, max_contacts)
VALUES ('6010', 1);

INSERT INTO ps_endpoints
  (id, transport, aors, auth, context, disallow, allow, dtmf_mode, direct_media)
VALUES
  ('6010', 'transport-udp', '6010', '6010-auth', 'from-internal',
   'all', 'ulaw', 'rfc4733', 'no');
```

3 行が合わせて 1 つの SIP アカウントを表します。残りのアカウント設定は PJSIP オブジェクトに分散しており、コンテキスト、コーデック、DTMF モード、メディア処理はエンドポイント上に（上記の最後の 6 列）、動的レジストレーションは AOR にあります。別個の「dynamic」フラグは存在せず、AOR は `max_contacts` が 0 より大きい限り動的 REGISTER を受け付け、各登録場所は `ps_contacts` に書き込まれます。

PJSIP では RFC 2833 / RFC 4733 のアウト・オブ・バンド DTMF モードは `rfc4733` と呼ばれ、デフォルトは `dtmf_mode=rfc4733` です。そのため、上記の `dtmf_mode` 列は任意であり、明確さのためにのみ示されています。

Step 3: Try to register the new phone with a softphone using username `6010` and password `supersecret`. Confirm the registration on the Asterisk CLI:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Step 4: Include the extensions in the database.

```
mysql -u astdb -p
```

Enter password:

Use supersecret when asked, then insert the extension row from the MySQL client:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Step 5: Include Asterisk Real Time in the dial plan. In the context `default`:

```
switch => realtime/test@extensions
```

Reload the extensions to activate the change.

```
asterisk-server*CLI> extensions reload
```

Step 6: Reconfigure one of the phones to the username `bria`, if you have not already done so.

Step 7: Dial 6007 from an existing phone; the `bria` phone should ring。

## Summary

この章では、Asterisk Real Time を使用して設定をデータベースに格納できることを学びました。Asterisk には ODBC 用のネイティブ realtime ドライバ（UnixODBC 対応のデータベース、たとえば MySQL/MariaDB や SQLite に対応）と PostgreSQL 用ドライバ、さらにディレクトリバックエンド用の LDAP realtime ドライバが同梱されています。MySQL/MariaDB は ODBC 経由でアクセスします（本章で行ったように）。専用の`res_config_mysql`アドオンも存在しますが、コアビルドの外部にあるため、一般的には ODBC が使用されます。設定は static と real time に分かれます。static 設定は設定ファイルに置き換える形で、real‑time 設定は通話やその他の関連イベントが発生したときにのみロードされる動的オブジェクトを作成します。最後に、ARA のインストールと設定方法について実践的なラボでまとめました。

## Quiz

1. Asterisk Realtime は標準の Asterisk 配布物の一部です。
   - A. True
   - B. False
2. データベースサーバーの接続パラメータは次のファイルで設定します：
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. `extconfig.conf` ファイルは Realtime で使用されるテーブルを設定します。2 つの異なるセクションがあります（2 つ選択）：
   - A. Static configuration
   - B. Realtime configuration
   - C. Outbound routes
   - D. IP addresses and database ports
4. 静的構成では、オブジェクトがデータベースからロードされた後、Asterisk のメモリに保持され、開始時またはリロード時にのみ更新されます。
   - A. True
   - B. False
5. PJSIP realtime (Sorcery) は `qualify` と MWI を realtime エンドポイントで完全にサポートします。これは、Sorcery がそれらを従来の構成済み PJSIP オブジェクトとしてロードし、古い SIP realtime ピアが各通話後に破棄されるのとは異なるためです。
   - A. True
   - B. False
6. PJSIP realtime では、エンドポイントとその登録されたコンタクトを保持するテーブルはどれですか？
   - A. `ps_endpoints` and `ps_contacts`
   - B. `ps_peers` and `ps_registry`
   - C. `ps_config` and `ps_data`
   - D. `extconfig` and `res_odbc`
7. ARA を有効にした後でも、テキスト構成ファイルを使用し続けることができます。
   - A. True
   - B. False
8. phpMyAdmin は Realtime を使用する際に必須です。
   - A. True
   - B. False
9. データベースは構成ファイルに存在するすべてのフィールドを作成しなければなりません。
   - A. True
   - B. False
10. Asterisk 22 で、PJSIP realtime テーブル（`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`）を作成する推奨かつバージョンに合った方法はどれですか？
    - A. 各 `ps_*` テーブルの `CREATE TABLE` 文を手書きする
    - B. `contrib/realtime/` からレガシー `mysql_config.sql` をインポートする
    - C. `contrib/ast-db-manage`（`alembic -c config.ini upgrade head`）で Alembic `config` マイグレーションを実行する
    - D. テーブルは Asterisk が最初に起動したときに自動的に作成される

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
