# Asterisk 通話詳細レコード

Asterisk は他のテレフォニー・プラットフォームと同様に、通話の課金を可能にします。市場には PBX が生成するレコードをインポートできるプログラムが多数あります。これらのレコードは、請求額の正確性の確認や統計の作成などに利用されます。

## 目的

- 記録が生成される場所と形式を説明する
- ODBC（Open Database Connectivity）を使用して記録を生成する
- 課金と統合された認証スキームを実装する

## Asterisk CDR フォーマット

Asterisk は各通話ごとにコール詳細レコード (CDR) を生成します。これらのレコードはデフォルトで /var/log/asterisk/cdr-csv にあるカンマ区切り値 (CSV) 形式のテキストファイルに保存されます。ファイルは以下のフィールドで構成されています。

| フィールド | 説明 | 種類 |
|-------|-------------|------|
| Accountcode | 使用するアカウント番号 | String |
| Src | 発信者番号 | String |
| Dst | 宛先エクステンション | String |
| Dcontext | 宛先コンテキスト | String |
| Clid | テキスト付き発信者ID | String |
| Channel | 使用されたチャンネル | String |
| Dstchannel | 宛先チャンネル | String |
| Lastapp | 最後に実行されたアプリケーション | String |
| Lastdata | 最後のアプリケーションデータ | String |
| Start | 通話開始時刻 | Date/Time |
| Answer | 通話応答時刻 | Date/Time |
| End | 通話終了時刻 | Date/Time |
| Duration | ダイヤルから切断までの時間 | Integer (seconds) |
| Billsec | 応答から切断までの時間 | Integer (seconds) |
| Disposition | 通話の結果 (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | フラグ (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | ユーザー定義フィールド | String |

CSV ファイルのサンプルです。各行が 1 件のレコードになり、フィールドは上表と同じ順序で表示されます（`accountcode` が最初、`amaflags` が最後）：

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## アカウントコードと自動メッセージ課金

各チャンネルにアカウントコードと ama フラグを指定できます。通常はチャンネル設定ファイル（例: `chan_dahdi.conf`、`pjsip.conf`）で行います。パラメータ `amaflags` は CDR レコードに対して何を行うかを定義します。利用可能な amaflag の値は次のとおりです：

- Default
- Omit
- Billing
- Documentation

レコードを課金または文書化のためにフラグ付けできるのと同様に、各レコードにアカウントコードを設定できます。アカウントコードは自由形式の文字列で（`accountcode` エンドポイントオプションは任意の文字列を受け取り、CDR レコードは 80 文字フィールドに保存します）、通常はレコードを部門や事業単位に割り当てるために使用されます。例: `pjsip.conf` エンドポイントセクション

```
[8576]
type=endpoint
accountcode=Support
```

AMA フラグは Asterisk 22 では `pjsip.conf` エンドポイントオプションではありません。ダイヤルプランから `CHANNEL` 関数（例: `Set(CHANNEL(amaflags)=billing)`）で、または `Set(CDR(amaflags)=billing)` で通話ごとに設定します。

## CSV および/または CDR 形式の変更

cdr_custom.conf ファイルを変更することで CSV 形式を変更できます。

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

cdr_custom.conf ファイルで CDR 形式を変更できます。

## CDR ストレージ

CDR のストレージは複数の方法で実現できます。最も重要なのは、スプレッドシートに簡単にインポートできる CSV テキストファイルです。小規模事業者にとっては通常これで十分です。いくつかの請求ソフトウェアはデフォルトで CSV ファイルを受け付けます。しかし、データベースに CDR を保存する方がはるかに優れており安全です。Asterisk は複数のデータベース種別をサポートしています。市場には請求用のグラフィカルインターフェースもあります。ドライバが多数ある中で、どれを選べばよいでしょうか？

### 利用可能なストレージドライバ

- cdr_csv – カンマ区切りテキストファイル
- cdr_custom – カスタマイズ可能なカンマ区切りテキストファイル
- cdr_adaptive_odbc – アダプティブ ODBC バックエンド（データベースストレージに推奨）
- cdr_odbc – unixODBC 対応データベース（レガシー；cdr_adaptive_odbc 推奨）
- cdr_pgsql – Postgres データベース
- cdr_tds (cdr_freetds) – FreeTDS 経由の Sybase および MSSQL データベース
- cdr_manager – CDR を Manager Interface に送信
- cdr_radius – CDR radius インターフェース
- cdr_sqlite3_custom – SQLite3 カスタム CDR モジュール

古いガイドで推奨されていた `cdr_addon_mysql` (cdr_mysql) モジュールは Asterisk 19 で削除され、Asterisk 22 にはネイティブの MySQL CDR ドライバがありません。MySQL/MariaDB に CDR を書き込むには、`cdr_adaptive_odbc` と MySQL ODBC ドライバを組み合わせて使用します — 本章で使用するアプローチです。

CDR の記録は、/etc/asterisk/modules.conf ファイルにロードされているすべてのアクティブモジュールで行われます。パラメータ autoload=yes が設定されている場合、すべてのモジュールがロードされます。現在システムにロードされている cdr_drivers を確認するには、以下のコマンドを使用します。

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

もし上のスクリーンショットが見えるなら、少なくとも cdr_adaptive_odbc、cdr_csv、cdr_custom、cdr_manager、cdr_odbc、cdr_sqlite3_custom が実行中です。近年、いくつかの astricon の後で、Asterisk チームが ODBC を好んでいることが明らかになりました。ODBC は接続プーリングをサポートする唯一のドライバです。接続プーリングは、すべての操作ごとに新しい接続を開く必要がなくなるため、パフォーマンス面で大きな利点があります。この章は以前は cdr_mysql を使用して書かれていましたが、今回の版では cdr_adaptive_odbc に移行しました。設定はやや複雑になることを承知の上での選択です。cdr_adaptive_odbc を選ぶことで CDR をカスタマイズできるようになります。ダイヤルプランで新しい CDR 変数を設定し、データベースに対応するカラムを追加するだけです。例えば、オーディオジッターを記録する場合は次のようにします。

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### CSV ストレージ

前述したように、デフォルトでは Asterisk はすべての CDR を cdr_csv.so モジュールを使用して CSV テキストファイルに送ります。/var/log/asterisk/cdr-csv にファイルが見当たらない場合は、CLI コマンド `module show` でモジュールがロードされているか確認してください。ロードされていなければ、`modules.conf` を確認します。この章では、バックアップとして cdr を cdr_csv に送信します。

### ファイル modules.conf の設定

適切なモジュールだけをロードするには、`modules.conf` ファイルに以下の行を使用します

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Now we have only cdr_csv and cdr_adaptive_odbc loaded.

## Installing and configuring ODBC on Ubuntu 22.04

I always regret to publish detailed instructions in the book. They will change sometimes sooner than the book is published. Versions change, modules change, so try to adapt the command here to your own situation. Most of the time minor changes are enough to reproduce the installation. Pay attention on the steps even experienced Linux users will find hard to install the ODBC drivers.

Step 1 - Install the required packages:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Step 2 - Create a database and a user:

```
mysql -u root -p
```

(Use the password defined when you created the mysql server) Type this commands in mysql command line

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Step 3 - Create the database

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Step 4: Download the MySQL ODBC connector from Oracle. Check your operating system using: `lsb_release -a`. For Ubuntu 22.04 (x86_64), visit https://dev.mysql.com/downloads/connector/odbc/ and choose the current 8.x or 9.x release for Ubuntu 22.04. The exact filename and version number change over time, so set `VER` (below) to whatever the current Linux glibc build is called.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Step 5: Install the ODBC driver

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Step 6 - Configure the ODBC connector edit the file /etc/odbc.ini to create the DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Step 7: Test the driver access using iSQL. iSQL is a command line utility to connect to the database over unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Please, do not procede with Asterisk configuration if you can’t see the result of the isql command.

### Configuring ODBC in the Asterisk

Before you can configure the cdr_adaptive_odbc, you should first configure the ODBC resource file.

Step 1 - Connect Asterisk to ODBC. Edit the file res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Step 2 – Restart Asterisk and test using

```
asterisk*CLI> odbc show
```

The output is shown below.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Step 3 – Configure the adaptive ODBC driver in /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Here `connection` points to the `[cdr]` connection section defined in `res_odbc.conf`, and `table` is the database table where CDRs are written.

Step 4 – Reload the module cdr_adaptive_odbc.so:

```
asterisk*CLI> reload cdr_adaptive_odbc
```

Step 5 – Make same calls and check the database fro new records. To check the database:

```
mysql -u root -p
>use astdb
>select * from cdr;
```

## Applications and functions

いくつかのアプリケーションは課金に関連しています。

### CDR(accountcode)

別のアプリケーション dial() を呼び出す前にアカウントコードを設定します。例: フォーマット:

```
Set(CDR(accountcode)=account)
```

アカウントコードはチャンネル変数 ${CDR(accountcode)} を使用して確認できます。

### CDR(amaflags)

課金目的のフラグを設定します。オプションは default、omit、documentation、billing です。

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

現在のチャンネルの CDR 記録を無効にします。これによりファイルやデータベースに CDR が書き込まれません。`0` に戻すと記録が再び有効になります。

```
Set(CDR_PROP(disable)=1)
```

以前のエディションで使用されていた `NoCDR()` アプリケーションは Asterisk 21 で削除されました。Asterisk 22 では `Set(CDR_PROP(disable)=1)` を使用してチャンネルの CDR を無効にします。

### ResetCDR()

Call Data Record をリセットします。`start` 時間（応答があった場合は `answer` 時間）は現在時刻に設定され、すべての CDR 変数はクリアされます。`v` オプションが設定されている場合、リセット中に CDR 変数は保持されます。

### Set(CDR(userfield)=Value)

このコマンドは CDR のユーザーフィールドを設定します。`cdr_adaptive_odbc` を使用すると、CDR テーブルに `userfield` カラムが存在する場合にユーザーフィールドが自動的に保存されます — ソースの再コンパイルは不要です。CSV テキストファイルの場合、ユーザーフィールドを使用したい場合はソースコード (cdr_csv.c) を編集し、Asterisk を再コンパイルする必要があります。

以前のエディションでは `cdr_addon_mysql` モジュール（`cdr_mysql.conf`）を使用して MySQL に CDR を保存していました。そのモジュールは Asterisk 19 で削除され、Asterisk 22 では利用できません。現在サポートされているパスは `cdr_adaptive_odbc` で、MySQL ODBC ドライバーを使用し、ユーザーフィールドやその他のカスタムカラムを適応的カラムマッピングを通じてネイティブに保存します。

### Appending to the user field

以前のエディションでは `AppendCDRUserField()` アプリケーションを使用して CDR ユーザーフィールドにデータを追加していました。そのアプリケーションは Asterisk から削除されました。Asterisk 22 では `CDR` 関数でユーザーフィールドを読み取り、再設定することでデータを追加します。例:

`Set(CDR(userfield)=${CDR(userfield)}extra)`

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## User authentication

一部の企業では従業員の通話料金を請求します。Asterisk では、認証されたユーザーを CDR に請求できる認証方式を設定できます。この認証は、`Authenticate` アプリケーションにパラメータとして渡すパスワード、パラメータの前に `/`（スラッシュ）を付けて示すパスワードファイル、または Asterisk データベースキー（`d`オプション使用）を使用して行うことができます。形式:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

オプション:

- a – 入力されたパスワードをチャンネルのアカウントコードに設定します。
- d – 指定されたパスを文字列としてのファイルではなく、Asterisk DB キーとして解釈します。
- m – パスを`accountcode:passwordhash`行のファイルとして解釈します。
- r – 認証に成功した後にデータベースキーを削除します（`d`と併用可能）。

呼び出し側が 3 回すべて失敗した場合、チャンネルは切断されます。ダイヤルプランの実行は続行されないため、`Authenticate()`の次の行で失敗パスを処理してください。例（国際電話）:

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

古い`j`オプション（失敗時に優先度 n+101 へジャンプ）および`+101`優先度規則は、かなり前に Asterisk から削除されました。失敗した`Authenticate()`は単に切断されます。

コンソールから DB キーにパスワードを挿入するには:

```
asterisk*CLI> database put senha 123456 1
```

## ボイスメールからパスワードを使用する

このアプリケーションは authenticate と同じ動作をしますが、パスワードにボイスメール設定ファイルを使用します。

```
VMAuthenticate([mailbox][@context][,options])
```

メールボックスが指定されている場合、そのメールボックスのパスワードのみが有効とみなされます。メールボックスが指定されていない場合、チャネル変数 `${AUTH_MAILBOX}` に認証されたメールボックスが設定されます。`s` オプションが設定されていると、最初のプロンプトがスキップされます。例（国際電話）：

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

CDR records provide one summary row per call. For more detailed event tracking — such as individual channel state transitions, bridge enter/leave events, and attended transfer legs — Asterisk 22 includes **Channel Event Logging (CEL)**, configured via `/etc/asterisk/cel.conf` and stored through backends such as `cel_odbc` or `cel_custom`.

CEL complements CDR rather than replacing it: CDR remains the standard for billing summaries, while CEL gives granular per-event data useful for fraud detection, quality monitoring, and advanced reporting.

The `cel.conf` configuration pattern mirrors `cdr.conf`: you enable the event types you want in the `[general]` section of `cel.conf`, then configure each storage back-end in its own file — `cel_custom.conf` for CSV, `cel_odbc.conf` for an ODBC database (the same `res_odbc.conf` connection used for CDRs). You can confirm whether CEL is active with `cel show status` on the CLI.

## 概要

この章では、CDR をテキストファイルおよび MySQL データベースに記録する方法を学びました。また、amaflags とアカウントコードの設定方法も学習しました。章の最後では、CDR と課金と統合された認証方式の使用方法を学びました。

## Quiz

1. デフォルトでは、Asterisk は /var/log/asterisk/cdr-csv ディレクトリに CDR を記録します。
   - A. False
   - B. True
2. Asterisk は CDR を書き込むことができます（該当するものすべてを選択）：
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. CSV text files
   - E. unixODBC-supported databases
3. Asterisk は同時に 1 種類のストレージに対してのみ CDR を生成します。
   - A. False
   - B. True
4. 利用可能な Asterisk amaflags はどれですか？
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. 部門を CDR に関連付けるには ___ コマンドを使用し、アカウントコードは ___ チャネル変数で取得できます。
6. `Set(CDR_PROP(disable)=1)` と `ResetCDR()` の違いは、CDR を無効にするとレコードが書き込まれなくなるのに対し、`ResetCDR()` は現在のレコードをリセット（ゼロに）することです。（以前 CDR を無効にしていた `NoCDR()` アプリケーションは Asterisk 21 で削除されました。）
   - A. False
   - B. True
7. `cdr_csv.so` モジュールでユーザー定義フィールドを使用するには、ソースコードを編集して Asterisk を再コンパイルしなければなりません。
   - A. False
   - B. True
8. Authenticate() アプリケーションで利用できる 3 つの認証方法は次のとおりです：
   - A. Password
   - B. Password file
   - C. Asterisk DB (dbput and dbget)
   - D. Voicemail
9. ボイスメールのパスワードは `voicemail.conf` の別セクションで指定され、ボイスメールユーザーとは別です。
   - A. False
   - B. True
10. Channel Event Logging (CEL) は Asterisk 22 で CDR に取って代わります — CEL が有効になると、CDR の課金サマリーは生成されなくなります。
    - A. False
    - B. True

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
