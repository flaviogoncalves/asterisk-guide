# Asterisk Real-Time

ご存知の通り、Asteriskの設定は /etc/asterisk ディレクトリにある複数のテキストファイルを使用して行われます。テキストファイルは手軽ですが、以下のような既知の欠点があります。

- ファイルを変更するたびに Asterisk をリロードする必要がある
- ユーザー数が増えるとメモリ使用量が増加する
- テキストファイルを使用してプロビジョニングインターフェースを構築するのが困難
- 既存のデータベースとの統合ができない

ARA（Asterisk Realtime）は、Anthony Minessale II、Mark Spencer、Constantine Filinの各氏によって作成され、SQLデータベースとの透過的な統合を可能にするよう設計されました。LDAPインターフェースも利用可能です。このシステムは Asterisk External Configuration とも呼ばれ、/etc/asterisk/extconfig.conf で設定されます。設定ファイルをデータベース内のテーブルにマッピング（静的設定）したり、Asterisk をリロードすることなくオブジェクトを動的に作成するためのリアルタイムエントリを設定したりできます。

## 学習目標

この章を終えるまでに、読者は以下のことができるようになります。

- Asterisk Real Time の利点と制限を理解する。
- ARA で ODBC を使用する。
- ODBC を使用して ARA をコンパイルおよびインストールする。
- ラボ環境でシステムをテストする。

## Asterisk Real Time はどのように動作するか？

新しい Real Time アーキテクチャでは、データベース固有のコードはすべてチャネルドライバに移動されました。チャネルは、データベースを検索する汎用ルーチンを呼び出すだけです。ソースコードの観点から見ると、はるかにシンプルでクリーンなプロセスになっています。データベースには以下の3つの関数でアクセスします。

- STATIC: モジュールがロードされたときに静的設定をセットアップするために使用されます。
- REALTIME: 通話中やその他のイベント中にオブジェクトを検索するために使用されます。
- UPDATE: オブジェクトを更新するために使用されます。

Asterisk 22 では、SIP endpoint は **Sorcery** オブジェクトモデル上に構築された **PJSIP** スタック（`res_pjsip`）によって処理されます。Sorcery は `realtime` ウィザードを使用して、データベースから各 PJSIP オブジェクトをオンデマンドでロードします。これらのオブジェクトは、古い SIP ドライバが通話ごとに破棄していた使い捨てのリアルタイムピアとは異なり、通常の PJSIP 設定オブジェクトとして存在します。これらは実際のオブジェクトであるため、NAT traversal、qualify、および message waiting indication (MWI) は、リアルタイム endpoint に対して正常に機能します。（Sorcery は、さらに `memory_cache` ウィザードを介してオブジェクトをメモリにキャッシュするように指示することもできますが、これはオプトインであり、リアルタイムロードとは別個の機能です。）データベース内のオブジェクトを変更すると、次回の検索時にその変更が反映されるため、編集のたびにリロードする必要はありません。（`chan_sip` リアルタイムモデルと、その `sippeers`/`sipusers` ファミリーは廃止されており、*Legacy Channels* の章でのみ扱われます。）

## Asterisk Real Time の設定

このラボでは、CDR の章で ODBC がすでにインストールされていることを前提とします。ARA は extconfig.conf テキストファイルで設定され、そこには2つのセクションがあります。1つ目は静的設定ファイルセクションで、テキスト設定ファイルをデータベーステーブルに置き換えることができます。2つ目はリアルタイム設定エンジンで、動的オブジェクト（peers/users）用のデータベーステーブルを設定します。静的設定にはテキストファイルを、動的エントリにはデータベースを使用することは珍しくありません。その場合、最初のセクションは変更されません。

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Asterisk Real Time アーキテクチャ: 設定ファイルと静的データベーステーブルは Asterisk 起動時にロードされますが、リアルタイムデータベーステーブルは通話中にオンデマンドで読み込まれる動的設定を提供します。](../images/18-realtime-fig01.png)

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

### 静的設定セクション

静的設定セクションは、設定ファイルと同等のものをデータベースに保存する場所です。これらの設定は Asterisk のロード時に読み込まれます。一部のモジュールは、リロード時にデータベースを再読み込みします。静的設定の例を以下に示します。

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

静的ファイルマッピングは、オブジェクトごとのリアルタイム相当が存在しない設定ファイルに最も役立ちます。PJSIP の場合は、ファイル全体を `pjsip.conf` として静的ファイルにマッピングするのではなく、この章の後半で説明するオブジェクトごとのリアルタイムファミリー（`ps_endpoints`、`ps_aors`など）を使用することを推奨します。

上記には3つの例が記載されています。最初の例では、queues.conf を asteriskdb データベースの queues テーブルにバインドしています。2番目の例では、pjsip.conf を odbc 設定で定義された asteriskdb データベースの pjsip_conf テーブルにバインドしています。最後の例では、iax.conf を LDAP ディレクトリにバインドしています。MyBaseDN は検索対象のベース DN です。前の例では、MySQL ドライバがデータベースにクエリを実行して必要な情報を取得する間、アプリケーション app_queue.so がロードされます。

### リアルタイム設定セクション

リアルタイム設定（extconfig.conf ファイルの後半部分）は、ロード、更新、アンロードされる設定部分をリアルタイムで構成する場所です。リアルタイムを使用すると、設定をリロードする必要はありません。リアルタイムの構文は以下の通りです。

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

ここでは5つの設定行があります。最初の行では、PJSIP/Sorcery ファミリー `ps_endpoints` を asteriskdb データベースのテーブル `ps_endpoints` にバインドしています。最後では、voicemail ファミリーを asteriskdb データベースの test テーブルにバインドしています。各 PJSIP オブジェクトタイプ（endpoint、aor、auth、contact）は独自のファミリーとテーブルを持ちます。完全なセットは以下の「PJSIP Realtime (Sorcery)」セクションに示されています。`voicemail`、`extensions`、`queues`、および `queue_members` ファミリーは Asterisk 22 でも有効です。

## PJSIP Realtime (Sorcery)

Asterisk 22 では、SIP endpoint は **Sorcery** オブジェクト抽象化レイヤー上に構築された **PJSIP** スタック（`res_pjsip`）によって排他的に処理されます。PJSIP は単一の SIP "peer" ではなく、SIP アカウントをいくつかのオブジェクトタイプに分割し、それぞれを独自のリアルタイムテーブルに保存します。

| Sorcery オブジェクトタイプ | リアルタイムテーブル | 内容 |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | アカウントごとの設定 (context, codecs, DTMF など) |
| aor (address of record) | ps_aors | 登録制限および `qualify` 設定 |
| auth | ps_auths | `username` / `password` 資格情報 |
| contact | ps_contacts | 動的に登録された場所 |
| domain alias | ps_domain_aliases | endpoint の代替 SIP ドメイン |
| endpoint identifier by IP | ps_endpoint_id_ips | 送信元 IP による endpoint の照合 |

PJSIP のリアルタイムは2か所で有効化されます。まず、Sorcery オブジェクトタイプを `extconfig.conf` のリアルタイムにマッピングします。

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

次に、それらのオブジェクトタイプに対して `realtime` ウィザードを使用するように Sorcery に指示します（`sorcery.conf`）。マッピング名（ここでは `res_pjsip`）はオブジェクトを再配置するモジュールであり、右側の値は `extconfig.conf` で定義したファミリーを指します。

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

静的オブジェクトとリアルタイムオブジェクトを混在させることもできます。もし `sorcery.conf` からタイプを省略した場合、そのオブジェクトタイプは `pjsip.conf` から読み込み続けます。一般的なパターンは、静的な transports とグローバル設定を `pjsip.conf` に保持し、endpoints、aors、auths、contacts をデータベースに保存することです。

### Alembic を使用した PJSIP リアルタイムスキーマの作成

Asterisk は、すべてのリアルタイムスキーマのデータベースマイグレーションを `contrib/ast-db-manage` 配下に同梱しています。これが PJSIP テーブルを作成（およびバージョンアップ）するためのサポートされた方法であり、手動で `ps_*` テーブル定義を作成する必要はもうありません。`config` マイグレーションセットには PJSIP/Sorcery テーブルが含まれています。

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:supersecret@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

これにより、実行中の Asterisk バージョンに適したカラムを持つ `ps_endpoints`、`ps_aors`、`ps_auths`、`ps_contacts` およびその他の PJSIP テーブルが作成されます。（Alembic には Python の `alembic` パッケージと、MySQL/MariaDB 用の `pymysql` や PostgreSQL 用の `psycopg2` などの SQLAlchemy ドライバが必要です。）

最小限のリアルタイム endpoint は、3つのテーブルの各行1つずつで構成されます。例えば endpoint `6010` の場合です。

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

行を挿入した後はリロードする必要はありません。次の REGISTER/INVITE でデータベースからオブジェクトが取得されます。リアルタイムが何を返したかは以下で確認できます。

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## データベース設定

extconfig.conf ファイルの設定が完了したので、テーブルを作成しましょう。一般的に、各データベースカラムは対応する設定ファイルのオプション名と一致します。PJSIP `ps_*` テーブルはこのルールに従います。すべての `ps_endpoints` カラムは `pjsip.conf` endpoint オプションにちなんで名付けられ、すべての `ps_auths` カラムは auth オプションにちなんで名付けられる、といった具合です。例えば、以下の `pjsip.conf` endpoint は、

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

3つのテーブルにまたがる1行として保存されます。`ps_endpoints` 行は `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000` を保持し、`ps_auths` 行は `id=4000, auth_type=userpass, username=4000, password=supersecret` を保持し、`ps_aors` 行は `id=4000, max_contacts=1` を保持します。実際に使用するカラムのみを埋める必要があります。NULL のままにしたカラムは、オプションのデフォルト値にフォールバックされます。例えば、endpoint で `callerid` パラメータを使用したい場合は、テーブル `ps_endpoints` の `callerid` カラムを埋めます（カラム名は `pjsip.conf` オプション名と同じです）。

voicemail テーブルも同じ考え方に従います。そのカラムは `voicemail.conf` フィールドにマッピングされます。

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

`uniqueid` は各 voicemail ユーザーに対して一意である必要があり、自動インクリメントにすることができます。mailbox や context との関係を持つ必要はありません。

### Asterisk Real Time を使用した dialplan の構築

リアルタイムシステムを使用して dialplan を作成することもできます。ARA は `switch` ステートメントを使用して、extensions.conf ファイルに含まれる通常の dialplan にリアルタイム extension を含めます。extension テーブルは以下のようになります。

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

`extensions` リアルタイムファミリーは Asterisk 22 でも変更されていません。単に `appdata` カラムが PJSIP チャネル（例: `PJSIP/4000`）をダイヤルするようにしてください。dialplan 内では、リアルタイムを使用するために `switch` コマンドを使用する必要があります。

![Asterisk Real Time での dialplan 構築: extensions.conf は `switch => realtime` ステートメントを使用して、テキストファイルからではなくデータベーステーブルから extension 行（context, exten, priority, app, data）を取得します。](../images/18-realtime-fig02.png)

```
[local]
switch => realtime
```

または

```
[local]
switch => realtime/from-internal@extensions
```

## ラボ: データベーステーブルのインストールと作成

このラボでは、Asterisk パラメータを受け入れるためのデータベースを準備します。REALTIME テーブルのみを準備します。静的設定は設定テキストファイルに任せます（素晴らしいでしょう？）。MySQL でのテーブル作成は以下の通りです。

ステップ 1: root として MySQL データベースにログインします。

```
mysql –u root –p
```

ステップ 2: CDR ラボで作成した MySQL サーバーにログインします。

```
mysql –u astdb –p
```

パスワードを求められたら、supersecret と入力します。

ステップ 3: 必要なテーブルを作成します。レガシーな静的スキーマファイルは引き続き `contrib/realtime/`（例: `/usr/src/asterisk-22.x/contrib/realtime/mysql`）に同梱されていますが、Asterisk 22 では、リアルタイムテーブル（特に PJSIP `ps_*` テーブル）を構築するための推奨されるバージョン正しい方法は、Alembic マイグレーション（`contrib/ast-db-manage`）を使用することです（上記の「Alembic を使用した PJSIP リアルタイムスキーマの作成」セクションを参照）。

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

Alembic `config` マイグレーションセットは、実行中の Asterisk バージョンが期待する正確なカラムを持つ PJSIP `ps_*` テーブル（および `voicemail`、`extensions`、その他のリアルタイムスキーマ）を構築するため、スキーマは常にビルドと一致します。

パスワードとして supersecret を使用してください。

ステップ 4: テーブルの作成を確認します。

```
mysql –u astdb –p astdb
mysql>use astdb;
mysql>show tables;
```

Alembic `config` マイグレーションによって作成された PJSIP `ps_*` テーブルと、その他のリアルタイムテーブル（`voicemail`、`extensions`など）が表示されるはずです。

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

（Alembic はこれらよりも多くのテーブルを作成します。上記のリストはこのラボに関連するものを示しています。）

ステップ 5: データベースは（CDR ラボから）すでに ODBC 用に設定されているため、ここではこれ以上の ODBC 設定は不要です。

ステップ 6: データベースタスクを処理するために phpMyAdmin をインストールします。

```
apt-get install phpmyadmin
```

以下に、このユーティリティのログイン画面とテーブル画面の2つのスクリーンショットを示します。名前とパスワードには astdb/supersecret を使用してください。

> **[2nd-ed note]** 最新のデータベース管理スクリーンショット（phpMyAdmin/Adminer）に置き換えるか、これらの手順をプレーンな SQL (CREATE TABLE/INSERT) に変換してください。

## ラボ: ARA の設定とテスト

このラボでは、データベース設定とテーブルを反映するように extconfig.conf 設定を変更します。

ステップ 1: extconfig.conf を設定し、Asterisk をリロードします。

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

上記の `ps_endpoints`、`ps_aors`、`ps_auths`、および `ps_contacts` ファミリーに注目してください。これらは一致する `sorcery.conf` マッピング（「PJSIP Realtime (Sorcery)」セクションを参照）とともに、PJSIP がデータベースからアカウントを読み取るようにします。`voicemail` および `extensions` ファミリーがこの例を締めくくります。

ステップ 2: リアルタイム extension テスト。phpMyAdmin を使用して、各 `ps_auths`、`ps_aors`、および `ps_endpoints` に1行ずつ挿入して新しい `6010` endpoint を作成し、この endpoint をソフトフォンで登録してみてください。

```
-- ps_auths
id=6010-auth, auth_type=userpass, username=6010, password=supersecret
-- ps_aors
id=6010, max_contacts=1
-- ps_endpoints
id=6010, transport=transport-udp, aors=6010, auth=6010-auth
```

> **[2nd-ed note]** 最新のデータベース管理スクリーンショット（phpMyAdmin/Adminer）に置き換えるか、これらの手順をプレーンな SQL (CREATE TABLE/INSERT) に変換してください。

残りのアカウント設定は PJSIP オブジェクト全体に分散されています。Context、codecs、DTMF モード、およびメディア処理は endpoint に存在し、動的登録は AOR に存在します。

```
-- ps_endpoints columns for 6010
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
-- ps_aors: dynamic registration is implicit; the AOR accepts
--          registrations and the contact is written to ps_contacts
```

PJSIP では、RFC 2833 / RFC 4733 DTMF モードは `rfc4733`（デフォルトは `dtmf_mode=rfc4733`）と呼ばれます。登録用の個別の「動的」フラグはありません。AOR は少なくとも1つの contact（`max_contacts` が0より大きい）を許可している限り動的な REGISTER を受け入れ、登録された各場所は `ps_contacts` に書き込まれます。

ステップ 3: ユーザー名 `6010` とパスワード `supersecret` を使用して、ソフトフォンで新しい電話を登録してみてください。Asterisk CLI で登録を確認します。

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

ステップ 4: データベースに extensions を含めます。

```
mysql -u astdb -p
```

パスワードを入力:

パスワードを求められたら supersecret を使用します。phpMyAdmin を使用してデータベースに extension を含めます。必要に応じて、代わりに MySQL クライアントインターフェースで以下のコマンドを使用してください。

```
use astdb;
insert into extensions(id, context, exten, priority, app, appdata) VALUES
('1','test', '6007','1','Dial','PJSIP/bria');
```

ステップ 5: dialplan に Asterisk Real Time を含めます。context `default` 内で:

```
switch => realtime/test@extensions
```

extensions をリロードして変更を有効にします。

```
asterisk-server*CLI>extensions reload
```

ステップ 6: まだ行っていない場合は、電話の1つをユーザー名 `bria` に再設定します。

ステップ 7: 既存の電話から 6007 にダイヤルします。電話 `bria` が鳴るはずです。

## まとめ

この章では、Asterisk Real Time を使用して設定をデータベースに保存できることを学びました。Asterisk は、ODBC（MySQL/MariaDB や SQLite を含む UnixODBC サポートデータベースに接続）、MySQL、PostgreSQL 用のネイティブリアルタイムドライバと、ディレクトリバックエンド用の LDAP リアルタイムドライバを同梱しています。設定は静的とリアルタイムに分かれています。静的設定は設定ファイルを置き換え、リアルタイム設定は通話やその他の関連イベントが発生したときにのみロードされる動的オブジェクトを作成します。最後に、ARA のインストールと設定方法に関する実践的なラボで締めくくりました。

## クイズ

1. Asterisk Realtime は標準の Asterisk ディストリビューションの一部である。
   - A. True
   - B. False
2. データベースサーバーの接続パラメータは、どのファイルで設定されるか:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. `extconfig.conf` ファイルは Realtime が使用するテーブルを設定する。これには2つの異なるセクションがある（2つ選択せよ）:
   - A. 静的設定
   - B. リアルタイム設定
   - C. アウトバウンドルート
   - D. IP アドレスとデータベースポート
4. 静的設定では、オブジェクトがデータベースからロードされると、Asterisk のメモリに保持され、起動またはリロード時にのみ更新される。
   - A. True
   - B. False
5. PJSIP リアルタイム (Sorcery) は、リアルタイム endpoint に対して `qualify` と MWI を完全にサポートしている。なぜなら、Sorcery は古い SIP リアルタイムピアのように通話後に破棄するのではなく、通常の PJSIP 設定オブジェクトとしてロードするからである。
   - A. True
   - B. False
6. PJSIP リアルタイムにおいて、endpoints とその登録済み contacts を保持するテーブルはどれか:
   - A. `ps_endpoints` と `ps_contacts`
   - B. `ps_peers` と `ps_registry`
   - C. `ps_config` と `ps_data`
   - D. `extconfig` と `res_odbc`
7. ARA を有効にした後でもテキスト設定ファイルを使用できる。
   - A. True
   - B. False
8. Realtime を使用する場合、phpMyAdmin は必須である。
   - A. True
   - B. False
9. データベースは、設定ファイルに存在するすべてのフィールドで作成しなければならない。
   - A. True
   - B. False
10. Asterisk 22 において、PJSIP リアルタイムテーブル（`ps_endpoints`、`ps_aors`、`ps_auths`、`ps_contacts`）を作成するための推奨されるバージョン正しい方法はどれか:
    - A. 各 `ps_*` テーブルの `CREATE TABLE` ステートメントを手動で記述する
    - B. `contrib/realtime/` からレガシーな `mysql_config.sql` をインポートする
    - C. `contrib/ast-db-manage`（`alembic -c config.ini upgrade head`）配下の Alembic `config` マイグレーションを実行する
    - D. Asterisk が最初に起動したときにテーブルが自動的に作成される

**回答:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
