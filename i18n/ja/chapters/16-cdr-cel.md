# Asterisk Call Detail Records

Asteriskは、他のテレフォニープラットフォームと同様に、通話の課金を行うことができます。市場にはPBXが生成したレコードをインポートできるプログラムがいくつか存在します。これらのレコードは、請求額の正確性の検証や統計の作成などに使用されます。

## 学習目標

本章を読み終えることで、読者は以下のことができるようになります。

- レコードがどこで、どのような形式で生成されるかを説明する
- ODBC (Open Database Connectivity) を使用してレコードを生成する
- 課金と統合された認証スキームを実装する

## Asterisk CDR形式

Asteriskは、通話ごとに通話詳細レコード（CDR）を生成します。これらのレコードはデフォルトで、/var/log/asterisk/cdr-csv にあるカンマ区切り値（CSV）形式のテキストファイルに保存されます。ファイルは以下のフィールドで構成されています。 CDR 説明 型 サイズ Accountcode アカウントコード 文字列 Src 発信者番号 文字列 Dst 着信先内線番号 文字列 Dcontext 着信先コンテキスト 文字列 Caller ID with Text 発信者名と番号 文字列 Channel 使用されたチャネル 文字列 Dstchannel 着信先チャネル 文字列 Lastapp 最後のアプリケーション 文字列 Lastdata 最後のアプリケーションデータ 文字列 Start 通話開始日時 日時 Answer 通話応答日時 日時 End 通話終了日時 日時 Duration ダイヤルから切断までの時間 整数（秒） Billsec 応答から切断までの時間 整数（秒） Disposition 通話の結果 文字列 (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags フラグ (DEFAULT, OMIT, BILLING, DOCUMENTATION) 文字列 User field ユーザー定義フィールド 文字列 テーブルにインポートされたCSVファイルのサンプル。 AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## アカウントコードと自動メッセージアカウンティング

各チャネルでアカウントコードとamaフラグを指定できます。通常、これはチャネル設定ファイル（例: chan_dahdi.conf, pjsip.conf）で行われます。パラメータ amaflags は、CDRレコードをどのように扱うかを定義します。指定可能な amaflag 値は以下の通りです。

- Default
- Omit
- Billing
- Documentation

レコードを課金用やドキュメント用にフラグ付けするのと同様に、各レコードにアカウントコードを設定できます。アカウントコードは自由形式の文字列であり（`accountcode` endpointオプションは任意の文字列を受け取り、CDRレコードはそれを80文字のフィールドに格納します）、通常はレコードを部門や事業単位に割り当てるために使用されます。例: pjsip.confのendpointセクション

```
[8576]
type=endpoint
accountcode=Support
```

AMAフラグはAsterisk 22における`pjsip.conf` endpointオプションではありません。ダイヤルプランから`CHANNEL`関数（例: `Set(CHANNEL(amaflags)=billing)`）を使用して通話ごとに設定するか、または`Set(CDR(amaflags)=billing)`を使用してください。

## CSVおよびCDR形式の変更

cdr_custom.confファイルを変更することで、CSV形式を変更できます。

```
;
; Mappings for custom config file
;
[mappings]
Master.csv =>
"${CDR(clid)}","${CDR(src)}","${CDR(dst)}","${CDR(dcontext)}","${CDR(channel)}"
,"${CDR(dstchannel)}","${CDR(lastapp)}","${CDR(lastdata)}","${CDR(start)}","${C
DR(answer)}","${CDR(end)}","${CDR(duration)}","${CDR(billsec)}","${CDR(disposit
ion)}","${CDR(amaflags)}","${CDR(accountcode)}","${CDR(uniqueid)}","${CDR(userf
ield)}"
```

cdr_custom.confファイル内でCDR形式を変更できます。

## CDRストレージ

CDRの保存はいくつかの方法で実現できます。最も重要な方法は、スプレッドシートに簡単にインポートできるCSVテキストファイルです。小規模なビジネスであれば、通常これで十分です。一部の課金ソフトウェアはデフォルトでCSVファイルを受け入れます。しかし、CDRをデータベースに保存する方がはるかに優れており、安全です。Asteriskはいくつかのデータベースをサポートしています。市場には課金用のグラフィカルインターフェースもいくつか存在します。これほど多くのドライバがある中で、どれを選ぶべきでしょうか？

### 利用可能なストレージドライバ

- cdr_csv – カンマ区切り値テキストファイル
- cdr_custom – カスタマイズ可能なカンマ区切り値テキストファイル
- cdr_adaptive_odbc – 適応型ODBCバックエンド（データベース保存に推奨）
- cdr_odbc – unixODBCサポートデータベース（レガシー、cdr_adaptive_odbcを推奨）
- cdr_pgsql – Postgresデータベース
- cdr_tds (cdr_freetds) – FreeTDS経由のSybaseおよびMSSQLデータベース
- cdr_manager – Manager InterfaceへのCDR出力
- cdr_radius – CDR RADIUSインターフェース
- cdr_sqlite3_custom – SQLite3カスタムCDRモジュール

古いガイドで推奨されていた`cdr_addon_mysql` (cdr_mysql) モジュールはAsterisk 19で削除されたため、Asterisk 22にはネイティブのMySQL CDRドライバは存在しません。CDRをMySQL/MariaDBに書き込むには、本章で採用しているアプローチである、MySQL ODBCドライバと組み合わせた`cdr_adaptive_odbc`を使用してください。

CDRの記録は、/etc/asterisk/modules.confファイルに読み込まれているすべてのアクティブなモジュールに対して行われます。パラメータ autoload=yes が設定されている場合、すべてのモジュールが読み込まれます。現在システムに読み込まれている cdr_drivers を確認するには、以下のコマンドを使用します。

```
asterisk*CLI> module show like cdr_
Module                 Description                              Use Count  Status
Support Level
cdr_adaptive_odbc.so   Adaptive ODBC CDR backend                0          Running
core
cdr_csv.so             Comma Separated Values CDR Backend       0          Running
extended
cdr_custom.so          Customizable Comma Separated Values CDR  0          Running
core
cdr_manager.so         Asterisk Manager Interface CDR Backend   0          Running
core
cdr_odbc.so            ODBC CDR Backend                         0          Running
extended
cdr_sqlite3_custom.so  SQLite3 Custom CDR Module                0          Not Running
extended
6 modules loaded
```

上記のスクリーンショットが表示されれば、少なくとも cdr_adaptive_odbc、cdr_csv、cdr_custom、cdr_manager、cdr_odbc、cdr_sqlite3_custom が実行されています。近年のAstriconを経て、AsteriskチームがODBCを推奨していることは明らかです。これは接続プーリングをサポートする唯一のドライバです。接続プーリングは、操作のたびに新しい接続を開く必要がないため、パフォーマンスの面で大きな利点があります。本章は以前 cdr_mysql を使用して執筆されていましたが、本版では設定が少し複雑であることを承知の上で cdr_adaptive_odbc に移行しました。 cdr_adaptive_odbc を選択することで、CDRをカスタマイズすることも可能になります。ダイヤルプランで新しいCDR変数を設定し、その列をデータベースに追加するだけです。 Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### CSVストレージ

前述の通り、Asteriskはデフォルトで cdr_csv.so モジュールを使用してすべてのCDRをCSVテキストファイルに送信します。/var/log/asterisk/cdr-csv にファイルが見当たらない場合は、CLIコマンド module show を使用してモジュールが読み込まれているか確認してください。読み込まれていない場合は、modules.confを確認してください。本章では、バックアップとしてCDRを cdr_csv にも送信します。

### modules.confの設定

適切なモジュールのみを読み込むには、modules.confファイルに以下の行を使用します。

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

これで cdr_csv と cdr_adaptive_odbc のみが読み込まれるようになりました。

## Ubuntu 22.04でのODBCのインストールと設定

詳細な手順を本書に掲載することは常に心苦しいものです。本書が出版されるよりも早く変更される可能性があるからです。バージョンやモジュールは変化するため、ここのコマンドを自身の状況に合わせて調整してください。ほとんどの場合、わずかな変更でインストールを再現できます。経験豊富なLinuxユーザーであっても、ODBCドライバのインストールは難しいと感じるステップがあるため、注意してください。

ステップ 1 - 必要なパッケージのインストール:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

ステップ 2 - データベースとユーザーの作成:

```
mysql -u root -p
```

（MySQLサーバー作成時に定義したパスワードを使用してください）MySQLコマンドラインで以下のコマンドを入力します。

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

ステップ 3 - データベースの作成

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

ステップ 4: OracleからMySQL ODBCコネクタをダウンロードします。以下のコマンドでオペレーティングシステムを確認してください: `lsb_release -a`。Ubuntu 22.04 (x86_64) の場合は、https://dev.mysql.com/downloads/connector/odbc/ にアクセスし、Ubuntu 22.04用の最新の 8.x または 9.x リリースを選択してください。正確なファイル名とバージョン番号は時間とともに変化するため、現在のLinux glibcビルド名に合わせて`VER`（下記）を設定してください。

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

ステップ 5: ODBCドライバのインストール

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

ステップ 6 - ODBCコネクタの設定。/etc/odbc.iniファイルを編集してDSN（Data Source Name）を作成します。

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

ステップ 7: iSQLを使用してドライバのアクセスをテストします。iSQLはunixodbc経由でデータベースに接続するためのコマンドラインユーティリティです。

```
isql -v astconn astdb supersecret
>show tables
```

isqlコマンドの結果が確認できない場合は、Asteriskの設定に進まないでください。

### AsteriskでのODBC設定

cdr_adaptive_odbc を設定する前に、まずODBCリソースファイルを設定する必要があります。

ステップ 1 - AsteriskをODBCに接続します。res_odbc.confファイルを編集します:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

ステップ 2 – Asteriskを再起動し、以下を使用してテストします。

```
CLI>odbc show
```

出力は以下の通りです。

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

ステップ 3 – /etc/asterisk/cdr_adaptive_odbc.conf で適応型ODBCドライバを設定します。

```
[cdr]
connection=cdr
table=cdr
```

ここで`connection`は`res_odbc.conf`で定義された`[cdr]`接続セクションを指し、`table`はCDRが書き込まれるデータベーステーブルです。

ステップ 4 – cdr_adaptive_odbc.so モジュールをリロードします:

```
asterisk*CLI>reload cdr_adaptive_odbc
```

ステップ 5 – いくつか通話を行い、データベースに新しいレコードがあるか確認します。データベースを確認するには:

```
mysql –u root –p
>use astdb
>select * from cdr
```

## アプリケーションと関数

課金に関連するアプリケーションはいくつかあります。

### CDR(accountcode)

別のアプリケーション dial() を呼び出す前にアカウントコードを設定します。例: 形式:

```
Set(CDR(accountcode)=account)
```

アカウントコードはチャネル変数 ${CDR(accountcode)} を使用して検証できます。

### CDR(amaflags)

課金目的のフラグを設定します。オプションは default, omit, documentation, billing です。

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

現在のチャネルのCDR記録を無効にします。これにより、ファイルやデータベースにCDRが書き込まれなくなります。`0`に戻すと記録が再有効化されます。

```
Set(CDR_PROP(disable)=1)
```

以前の版で使用されていた`NoCDR()`アプリケーションはAsterisk 21で削除されました。Asterisk 22では、代わりに`Set(CDR_PROP(disable)=1)`を使用してチャネルのCDRを無効にします。

### ResetCDR()

通話データレコードをリセットします。`start`時間（応答済みの場合は`answer`時間）が現在時刻に設定され、すべてのCDR変数が消去されます。`v`オプションが設定されている場合、リセット中もCDR変数は保持されます。

### Set(CDR(userfield)=Value)

このコマンドはCDRのユーザーフィールドを設定します。`cdr_adaptive_odbc`を使用する場合、CDRテーブルに`userfield`列が存在すればユーザーフィールドは自動的に保存されます（ソースの再コンパイルは不要です）。CSVテキストファイルの場合、ユーザーフィールドを使用するにはソースコード (cdr_csv.c) を編集し、Asteriskを再コンパイルする必要があります。

以前の版では、`cdr_addon_mysql`モジュール（`cdr_mysql.conf`）を使用してMySQLにCDRを保存していました。そのモジュールはAsterisk 19で削除されたため、Asterisk 22では利用できません。現在サポートされているパスは、MySQL ODBCドライバを使用した`cdr_adaptive_odbc`であり、適応型列マッピングを通じてユーザーフィールド（およびその他のカスタム列）をネイティブに保存します。

### AppendCDRUserField(Value)

CDRのユーザーフィールドにデータを追加します。

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## ユーザー認証

一部の企業では、従業員の通話に対して課金を行っています。Asteriskでは、認証されたユーザーをCDR上で課金対象にできる認証スキームを設定できます。この認証は、Authenticateアプリケーションにパラメータとして渡されるパスワード（パラメータの前に / (スラッシュ) を付けることでパスワードファイルを指定）、またはAsteriskデータベースキー（`d`オプションを使用）を使用して行うことができます。形式:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

オプション:

- a – チャネルのアカウントコードを入力されたパスワードに設定します。
- d – 指定されたパスをリテラルファイルではなくAsterisk DBキーとして解釈します。
- m – パスを`accountcode:passwordhash`行のファイルとして解釈します。
- r – 認証成功後にデータベースキーを削除します（`d`でのみ有効）。

発信者が3回の試行すべてに失敗した場合、チャネルは切断されます。ダイヤルプランの実行は継続されないため、失敗時のパスは`Authenticate()`の後の行で処理してください。例（国際電話）:

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

古い`j`オプション（失敗時に優先度 n+101 へジャンプ）および`+101`優先度規則は、ずっと前にAsteriskから削除されました。失敗した`Authenticate()`は単に切断されます。

コンソールからDBキーにパスワードを挿入するには:

```
CLI> database put senha 123456 1
```

## ボイスメールのパスワードの使用

このアプリケーションはauthenticateと同じ動作をしますが、パスワードにボイスメール設定ファイルを使用します。

```
VMAuthenticate([mailbox][@context][,options])
```

メールボックスが指定されている場合、そのメールボックスのパスワードのみが有効とみなされます。メールボックスが指定されていない場合、チャネル変数`${AUTH_MAILBOX}`に認証されたメールボックスが設定されます。`s`オプションが設定されている場合、初期プロンプトはスキップされます。例（国際電話）:

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

CDRレコードは通話ごとに1行の要約を提供します。個別のチャネル状態遷移、ブリッジへの参加/離脱イベント、転送の足跡など、より詳細なイベント追跡のために、Asterisk 22には**Channel Event Logging (CEL)**が含まれており、これは`/etc/asterisk/cel.conf`を介して設定され、`cel_odbc`や`cel_custom`などのバックエンドを通じて保存されます。

CELはCDRを置き換えるのではなく補完するものです。CDRは課金要約の標準であり続け、CELは不正検知、品質監視、高度なレポート作成に役立つ詳細なイベントごとのデータを提供します。

`cel.conf`の設定パターンは`cdr.conf`を反映しています。まず`cel.conf`の`[general]`セクションで必要なイベントタイプを有効にし、次に各ストレージバックエンドをそれぞれのファイル（CSV用は`cel_custom.conf`、ODBCデータベース用は`cel_odbc.conf`（CDRと同じ`res_odbc.conf`接続を使用））で設定します。CELがアクティブかどうかは、CLI上で`cel show status`を使用して確認できます。

## まとめ

本章では、テキストファイルおよびMySQLデータベースへのCDR記録の実装方法を学びました。また、amaflagsとアカウントコードの設定方法も学びました。章の最後には、CDRおよび課金と統合された認証スキームの使用方法を学びました。

## クイズ

1. デフォルトでは、Asteriskは /var/log/asterisk/cdr-csv ディレクトリにCDRを記録します。
   - A. 偽
   - B. 真
2. AsteriskはCDRをどこに書き込めますか（該当するものすべてを選択してください）:
   - A. MySQL
   - B. ネイティブOracle
   - C. Microsoft SQL Server
   - D. CSVテキストファイル
   - E. unixODBCサポートデータベース
3. Asteriskは一度に1種類のストレージに対してのみCDRを生成します。
   - A. 偽
   - B. 真
4. 利用可能なAsterisk amaflagsはどれですか？
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. 部門をCDRに関連付けるには ___ コマンドを使用し、アカウントコードは ___ チャネル変数で読み取ることができます。
6. `Set(CDR_PROP(disable)=1)`と`ResetCDR()`の違いは、CDRを無効にするとレコードが書き込まれなくなるのに対し、`ResetCDR()`は現在のレコードをリセット（ゼロ化）することです。（以前CDRを無効にしていた`NoCDR()`アプリケーションはAsterisk 21で削除されました。）
   - A. 偽
   - B. 真
7. `cdr_csv.so`モジュールでユーザー定義フィールドを使用するには、ソースコードを編集してAsteriskを再コンパイルする必要があります。
   - A. 偽
   - B. 真
8. Authenticate() アプリケーションで利用可能な3つの認証方法は次のうちどれですか？
   - A. パスワード
   - B. パスワードファイル
   - C. Asterisk DB (dbput および dbget)
   - D. ボイスメール
9. ボイスメールのパスワードは`voicemail.conf`の別のセクションで指定され、ボイスメールユーザーと同じではありません。
   - A. 偽
   - B. 真
10. Channel Event Logging (CEL) はAsterisk 22でCDRを置き換えるため、CELを有効にするとCDRの課金要約は生成されなくなります。
    - A. 偽
    - B. 真

**回答:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
