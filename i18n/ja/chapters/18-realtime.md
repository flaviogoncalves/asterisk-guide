# Asterisk Real-Time

ご存知の通り、Asteriskの設定は /etc/asterisk ディレクトリにある複数のテキストファイルを使用して行われます。テキストファイルの使用は容易ですが、いくつかの既知の欠点があります。

- ファイルを変更するたびに Asterisk をリロードする必要がある
- ユーザー数が多い場合にメモリ使用量が増加する
- テキストファイルを使用してプロビジョニングインターフェースをコーディングするのが困難である
- 既存のデータベースとの統合ができない

ARA（Asterisk Realtime）は、Anthony Minessale II、Mark Spencer、Constantine Filinによって作成され、SQLデータベースとの透過的な統合を可能にするよう設計されました。LDAPインターフェースも利用可能です。このシステムは Asterisk External Configuration とも呼ばれ、/etc/asterisk/extconfig.conf で設定されます。設定ファイルをデータベース内のテーブルにマッピング（静的設定）したり、Asteriskをリロードすることなくオブジェクトを動的に作成するためのリアルタイムエントリを作成したりできます。

## 目的

この章を終えるまでに、読者は以下のことができるようになります。

- Asterisk Real Time の利点と制限を理解する。
- ARA で使用するために ODBC を使用する。
- ODBC を使用して ARA をコンパイルおよびインストールする。
- ラボ環境でシステムをテストする。

## Asterisk Real Time はどのように動作するか？

新しい Real Time アーキテクチャでは、データベース固有のコードはすべてチャネルドライバーに移動されました。チャネルは、データベースを検索する汎用ルーチンを呼び出すだけです。ソースコードの観点から見ると、結果としてプロセスははるかにシンプルでクリーンなものになります。データベースには、次の3つの関数でアクセスします。

- STATIC: モジュールがロードされたときに静的設定をセットアップするために使用されます。
- REALTIME: 通話中やその他のイベント中にオブジェクトを検索するために使用されます。


- UPDATE: オブジェクトを更新するために使用されます。

Asterisk 22 では、SIP endpoint は **Sorcery** オブジェクトモデル上に構築された **PJSIP** スタック（`res_pjsip`）によって処理されます。`realtime`ウィザードを使用すると、Sorcery は各 PJSIP オブジェクトをデータベースからオンデマンドでロードします。これらのオブジェクトは、古い SIP ドライバーが通話ごとに破棄していた使い捨てのリアルタイムピアではなく、通常の PJSIP 設定オブジェクトとして存在します。これらは実際のオブジェクトであるため、NAT traversal、qualify、および message waiting indication (MWI) はすべて、リアルタイム endpoint に対して正常に機能します。（Sorcery はさらに、`memory_cache`ウィザードを介してメモリ内にオブジェクトをキャッシュするように指示することもできますが、これはオプトインであり、リアルタイムロードとは別個のものです。）データベース内のオブジェクトを変更すると、次回のルックアップ時に変更が反映されます。編集のたびにリロードする必要はありません。（`chan_sip`リアルタイムモデルと、その`sippeers`/`sipusers`ファミリーは、*Legacy Channels* の章でのみ扱われます。）

## Asterisk Real Time の設定

このラボでは、CDR の章で ODBC がすでにインストールされていることを前提とします。ARA は extconfig.conf テキストファイルで設定され、そこには2つのセクションが容易に確認できます。1つ目は静的設定ファイルセクションで、テキスト設定ファイルをデータベーステーブルに置き換えることができます。2つ目はリアルタイム設定エンジンで、動的オブジェクト（ピア/ユーザー）用のデータベーステーブルを設定します。静的設定にはテキストファイルを、動的エントリにはデータベースを使用することは珍しくありません。この場合、最初のセクションは変更されません。

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

静的ファイルマッピングは、オブジェクトごとのリアルタイム相当が存在しない設定ファイルに最も役立ちます。PJSIP の場合は、この章で後述するオブジェクトごとのリアルタイムファミリー（`ps_endpoints`、`ps_aors`など）を使用することを推奨します。全体を`pjsip.conf`として静的ファイルにマッピングするよりも適しています。

上記に3つの例を示しました。最初の例では、queues.conf を asteriskdb データベースの queues テーブルにバインドしています。2番目の例では、pjsip.conf を odbc 設定で定義されたデータベース asteriskdb のテーブル pjsip_conf にバインドしています。最後の例では、iax.conf を LDAP ディレクトリにバインドしています。MyBaseDN は検索対象のベース DN です。前の例では、MySQL ドライバーがデータベースにクエリを実行して必要な情報を取得する間、アプリケーション app_queue.so がロードされます。

### リアルタイム設定セクション

リアルタイム設定（extconfig.conf ファイルの2番目の部分）は、ロードされる設定部分をリアルタイムで設定、更新、およびアンロードする場所です。リアルタイムを使用すると、設定をリロードする必要はありません。リアルタイムの構文は以下の通りです。

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

ここでは5つの設定行があります。最初の行では、PJSIP/Sorcery ファミリー`ps_endpoints`を asteriskdb データベースのテーブル`ps_endpoints`にバインドしています。最後では、voicemail ファミリーを asteriskdb データベースの test テーブルにバインドしています。各 PJSIP オブジェクトタイプ（endpoint、aor、auth、contact）は独自のファミリーとテーブルを持ちます。完全なセットは以下の「PJSIP Realtime (Sorcery)」セクションに示されています。`voicemail`、`extensions`、`queues`、および`queue_members`ファミリーは Asterisk 22 でも有効です。

## PJSIP Realtime (Sorcery)

Asterisk 22 では、SIP endpoint は **Sorcery** オブジェクト抽象化レイヤー上に構築された **PJSIP** スタック（`res_pjsip`）によって排他的に処理されます。PJSIP は単一の SIP "ピア" ではなく、SIP アカウントを複数のオブジェクトタイプに分割し、それぞれを独自のリアルタイムテーブルに保存します。

| Sorcery オブジェクトタイプ | リアルタイムテーブル | 保持内容 |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | アカウントごとの設定 (context, codecs, DTMF など) |
| aor (address of record) | ps_aors | 登録制限および`qualify`設定 |
| auth | ps_auths | `username` / `password` 資格情報 |
| contact | ps_contacts | 動的に登録された場所 |
| domain alias | ps_domain_aliases | endpoint の代替 SIP ドメイン |
| endpoint identifier by IP | ps_endpoint_id_ips | 送信元 IP による endpoint の照合 |

PJSIP のリアルタイムは2か所で有効化されます。まず、Sorcery オブジェクトタイプを`extconfig.conf`のリアルタイムにマッピングします。

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

次に、それらのオブジェクトタイプに対して`realtime`ウィザードを使用するように Sorcery に指示します（`sorcery.conf`）。マッピング名（ここでは`res_pjsip`）はオブジェクトを再配置するモジュールであり、右側の値は`extconfig.conf`で定義したファミリーを指します。

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

静的オブジェクトとリアルタイムオブジェクトを混在させることができます。`sorcery.conf`からタイプを省略すると、そのオブジェクトタイプは`pjsip.conf`から読み込み続けます。一般的なパターンは、静的なトランスポートとグローバル設定を`pjsip.conf`に保持し、endpoint、aor、auth、contact をデータベースに保存することです。

### Alembic を使用した PJSIP リアルタイムスキーマの作成

Asterisk は、すべてのリアルタイムスキーマのデータベース移行ファイルを`contrib/ast-db-manage`の下に出荷しています。これが PJSIP テーブルを作成（およびバージョンアップグレード）するためのサポートされた方法です。手動で`ps_*`テーブル定義を作成する必要はもうありません。`config`移行セットには PJSIP/Sorcery テーブルが含まれています。

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:supersecret@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

これにより、`ps_endpoints`、`ps_aors`、`ps_auths`、`ps_contacts`およびその他の PJSIP テーブルが、実行中の Asterisk バージョンに適したカラムで作成されます。（Alembic には Python の`alembic`パッケージと、MySQL/MariaDB 用の`pymysql`や PostgreSQL 用の`psycopg2`などの SQLAlchemy ドライバーが必要です。）

最小限のリアルタイム endpoint は、3つのテーブルのそれぞれに1行ずつで構成されます。例えば endpoint`6010`の場合です。

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

extconfig.conf ファイルを設定したので、テーブルを作成しましょう。一般的に、各データベースカラムは対応する設定ファイルのオプション名と一致します。PJSIP`ps_*`テーブルはこのルールに従います。すべての`ps_endpoints`カラムは`pjsip.conf`endpoint オプションにちなんで名付けられ、すべての`ps_auths`カラムは auth オプションにちなんで名付けられています。例えば、以下の`pjsip.conf`endpoint は、

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

3つのテーブルにまたがる1行として保存されます。`ps_endpoints`行は`id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`を保持し、`ps_auths`行は`id=4000, auth_type=userpass, username=4000, password=supersecret`を保持し、`ps_aors`行は`id=4000, max_contacts=1`を保持します。実際に使用するカラムのみを入力すればよく、NULL のままにしたカラムはオプションのデフォルト値にフォールバックされます。例えば、endpoint で`callerid`パラメータが必要な場合は、`ps_endpoints`の`callerid`カラムに入力します（カラム名は`pjsip.conf`オプション名と同じです）。

voicemail テーブルも同じ考え方に従います。そのカラムは`voicemail.conf`フィールドにマッピングされます。

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

`uniqueid`は各 voicemail ユーザーに対して一意である必要があり、自動インクリメントにできます。mailbox や context との関係を持つ必要はありません。

### Asterisk Real Time を使用した dialplan の構築

リアルタイムシステムを使用して dialplan を作成することもできます。ARA は`switch`ステートメントを使用して、リアルタイム extension を extensions.conf ファイルに含まれる通常の dialplan に含めます。extension テーブルは以下のようになります。

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

`extensions`リアルタイムファミリーは Asterisk 22 でも変更されていません。`appdata`カラムが PJSIP チャネル（例:`PJSIP/4000`）をダイヤルすることを確認してください。dialplan では、リアルタイムを使用するために`switch`コマンドを使用する必要があります。

![Asterisk Real Time を使用した dialplan の構築: extensions.conf は`switch => realtime`ステートメントを使用して、テキストファイルからではなくデータベーステーブルから extension 行（context, exten, priority, app, data）を取得します。](../images/18-realtime-fig02.png)


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

このラボでは、Asterisk パラメータを受け入れるようにデータベースを準備します。REALTIME テーブルのみを準備します。静的設定は設定テキストファイルに任せます（素晴らしいでしょう？）。MySQL でのテーブル作成は以下の通りです。

ステップ 1: root として MySQL データベースにログインします。

```
mysql –u root –p
```

ステップ 2: CDR ラボで作成した MySQL サーバーにログインします。

```
mysql –u astdb –p
```

パスワードを求められたら、supersecret と入力します。

ステップ 3: 必要なテーブルを作成します。レガシーな静的スキーマファイルは依然として`contrib/realtime/`（例:`/usr/src/asterisk-22.x/contrib/realtime/mysql`）の下に出荷されていますが、Asterisk 22 では、リアルタイムテーブル（特に PJSIP`ps_*`テーブル）を構築するための推奨されるバージョン正しい方法は、`contrib/ast-db-manage`の下にある **Alembic** 移行を使用することです（上記の「Alembic を使用した PJSIP リアルタイムスキーマの作成」セクションを参照）。

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

Alembic`config`移行セットは、実行中の Asterisk バージョンが期待する正確なカラムを持つ PJSIP`ps_*`テーブル（および`voicemail`、`extensions`、その他のリアルタイムスキーマ）を構築するため、スキーマは常にビルドと一致します。

パスワードとして supersecret を使用してください。

ステップ 4: テーブルの作成を確認します。

```
mysql –u astdb –p astdb
mysql>use astdb;
mysql>show tables;
```

Alembic`config`移行によって作成された PJSIP`ps_*`テーブルと、`voicemail`、`extensions`およびその他のリアルタイムテーブルが表示されるはずです。

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

（Alembic はこれら以上のテーブルを作成します。上記のリストはこのラボに関連するものを示しています。）

ステップ 5: データベースはすでに ODBC 用に設定されているため（CDR ラボより）、ここでの追加の ODBC 設定は不要です。

ステップ 6: MySQL クライアントからテーブルを検査し、データを入力します。phpMyAdmin などのグラフィカルツールは不要です。この章のすべてのステップは、`mysql`コマンドラインから実行する単純なコピー＆ペースト可能な SQL です。`astdb`データベースに接続します（プロンプトが表示されたら`supersecret`を使用します）。

```
mysql -u astdb -p astdb
```

テーブルのカラムはいつでも`DESCRIBE`で確認できます。例:

```
mysql> DESCRIBE ps_endpoints;
mysql> DESCRIBE ps_auths;
mysql> DESCRIBE ps_aors;
```

これらのテーブルは Alembic`config`移行によって作成されたため、そのカラムは実行中の Asterisk バージョンの`pjsip.conf`オプション名とすでに一致しています。必要なカラムのみを入力してください。

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

上記の`ps_endpoints`、`ps_aors`、`ps_auths`、および`ps_contacts`ファミリーに注目してください。これらは一致する`sorcery.conf`マッピング（「PJSIP Realtime (Sorcery)」セクションを参照）とともに、PJSIP がデータベースからアカウントを読み取るようにします。`voicemail`および`extensions`ファミリーが例を締めくくります。

ステップ 2: リアルタイム extension のテスト。`ps_auths`、`ps_aors`、および`ps_endpoints`のそれぞれに1行ずつ挿入して新しい`6010`endpoint を作成し、この endpoint をソフトフォンで登録してみてください。`mysql`クライアント（`mysql -u astdb -p astdb`）で以下の SQL を実行します。

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

3つの行は合わせて1つの SIP アカウントを記述します。残りのアカウント設定は PJSIP オブジェクト全体に分散されています。context、codecs、DTMF モード、およびメディア処理は endpoint（上記の最後の6カラム）に存在し、動的登録は AOR に存在します。個別の "dynamic" フラグはありません。AOR は`max_contacts`がゼロより大きい限り動的な REGISTER を受け入れ、登録された各場所は`ps_contacts`に書き込まれます。

PJSIP では、RFC 2833 / RFC 4733 アウトオブバンド DTMF モードは`rfc4733`と呼ばれ、`dtmf_mode=rfc4733`がデフォルトであるため、上記の`dtmf_mode`カラムはオプションであり、明確にするためにのみ示されています。

ステップ 3: ユーザー名`6010`とパスワード`supersecret`を使用して、ソフトフォンで新しい電話を登録してみてください。Asterisk CLI で登録を確認します。

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

ステップ 4: データベースに extension を含めます。

```
mysql -u astdb -p
```

パスワードを入力:

求められたら supersecret を使用し、MySQL クライアントから extension 行を挿入します。

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

ステップ 5: dialplan に Asterisk Real Time を含めます。context`default`において:

```
switch => realtime/test@extensions
```

extensions をリロードして変更を有効にします。

```
asterisk-server*CLI>extensions reload
```

ステップ 6: まだ行っていない場合は、電話の1つをユーザー名`bria`に再設定します。

ステップ 7: 既存の電話から 6007 をダイヤルします。`bria`の電話が鳴るはずです。

## まとめ

この章では、Asterisk Real Time を使用すると設定をデータベースに配置できることを学びました。Asterisk は ODBC（MySQL/MariaDB や SQLite を含む UnixODBC サポートデータベースに接続）、MySQL、PostgreSQL 用のネイティブリアルタイムドライバーと、ディレクトリバックエンド用の LDAP リアルタイムドライバーを出荷しています。設定は静的とリアルタイムに分かれています。静的設定は設定ファイルを置き換え、リアルタイム設定は通話やその他の関連イベントが発生したときにのみロードされる動的オブジェクトを作成します。最後に、ARA のインストールと設定方法に関する実践的なラボで締めくくりました。

## クイズ

1. Asterisk Realtime は標準の Asterisk ディストリビューションの一部です。
   - A. True
   - B. False
2. データベースサーバーの接続パラメータは、次のファイルで設定されます。
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. `extconfig.conf`ファイルは Realtime で使用されるテーブルを設定します。これには2つの異なるセクションがあります（2つ選択してください）。
   - A. 静的設定
   - B. リアルタイム設定
   - C. アウトバウンドルート
   - D. IP アドレスとデータベースポート
4. 静的設定では、オブジェクトがデータベースからロードされると、Asterisk のメモリに保持され、起動またはリロード時にのみ更新されます。
   - A. True
   - B. False
5. PJSIP リアルタイム (Sorcery) は、リアルタイム endpoint に対して`qualify`と MWI を完全にサポートしています。これは、Sorcery が古い SIP リアルタイムピアのように通話ごとに破棄するのではなく、通常の PJSIP 設定オブジェクトとしてロードするためです。
   - A. True
   - B. False
6. PJSIP リアルタイムにおいて、endpoint とその登録済みコンタクトを保持するテーブルはどれですか？
   - A. `ps_endpoints` と `ps_contacts`
   - B. `ps_peers` と `ps_registry`
   - C. `ps_config` と `ps_data`
   - D. `extconfig` と `res_odbc`
7. ARA を有効にした後でも、テキスト設定ファイルを使用できます。
   - A. True
   - B. False
8. Realtime を使用する場合、phpMyAdmin は必須です。
   - A. True
   - B. False
9. データベースは、設定ファイルに存在するすべてのフィールドで作成する必要があります。
   - A. True
   - B. False
10. Asterisk 22 で、PJSIP リアルタイムテーブル（`ps_endpoints`、`ps_aors`、`ps_auths`、`ps_contacts`）を作成するための推奨されるバージョン正しい方法は何ですか？
    - A. 各`ps_*`テーブルの`CREATE TABLE`ステートメントを手書きする
    - B. `contrib/realtime/`からレガシーな`mysql_config.sql`をインポートする
    - C. `contrib/ast-db-manage`（`alembic -c config.ini upgrade head`）の下で Alembic`config`移行を実行する
    - D. Asterisk が最初に起動したときにテーブルが自動的に作成される

**回答:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
