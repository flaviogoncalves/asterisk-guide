# Asterisk 通话详细记录

Asterisk 与其他电话平台一样，支持对电话通话进行计费。市场上有多种程序可以导入 PBX 生成的记录。这些记录用于核对账单金额的准确性以及进行统计等工作。

## 目标

在本章结束时，读者应该能够：

- 描述记录生成的位置及其格式
- 使用 ODBC（Open Database Connectivity）生成记录
- 实现与计费集成的认证方案

## Asterisk CDR Format

Asterisk 为每个通话生成通话详细记录（CDR）。这些记录默认存储在 /var/log/asterisk/cdr-csv 目录下的逗号分隔值（CSV）文本文件中。文件按以下字段组织：

| Field | Description | Type |
|-------|-------------|------|
| Accountcode | 使用的账户号码 | String |
| Src | 主叫号码 | String |
| Dst | 目标分机 | String |
| Dcontext | 目标上下文 | String |
| Clid | 带文本的主叫号码 | String |
| Channel | 使用的通道 | String |
| Dstchannel | 目标通道 | String |
| Lastapp | 最后一个应用程序 | String |
| Lastdata | 最后一个应用程序数据 | String |
| Start | 通话开始时间 | Date/Time |
| Answer | 通话应答时间 | Date/Time |
| End | 通话结束时间 | Date/Time |
| Duration | 从拨号到挂断的时长 | Integer (seconds) |
| Billsec | 从应答到挂断的时长 | Integer (seconds) |
| Disposition | 通话结果（ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION） | String |
| Amaflags | 标志（DEFAULT, OMIT, BILLING, DOCUMENTATION） | String |
| Userfield | 用户自定义字段 | String |

CSV 文件示例。每行是一条记录；字段顺序与上表相同（`accountcode` 为首，`amaflags` 为尾）：

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## 账户代码和自动计费信息

您可以在每个通道上指定账户代码和 ama 标志。通常在通道配置文件中完成此操作（例如，chan_dahdi.conf，pjsip.conf）。参数 amaflags 定义了对 CDR 记录的处理方式。可能的 amaflag 值有：

- Default
- Omit
- Billing
- Documentation

类似于可以将记录标记为计费或文档的方式，账户代码可以在每条记录上设置。账户代码是一个自由格式的字符串（`accountcode` endpoint 选项接受任意 String，且 CDR 记录将其存储在 80 字符的字段中），通常用于将记录分配给某个部门或业务单元。示例：pjsip.conf endpoint 部分

```
[8576]
type=endpoint
accountcode=Support
```

AMA 标志在 Asterisk 22 中不是 `pjsip.conf` endpoint 选项；可以在 dialplan 中使用 `CHANNEL` 函数（例如 `Set(CHANNEL(amaflags)=billing)`）或使用 `Set(CDR(amaflags)=billing)` 为每个呼叫设置。

## 更改 CSV 和/或 CDR 格式

您可以通过更改 cdr_custom.conf 文件来更改 CSV 格式。

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

您可以在 cdr_custom.conf 文件中更改 CDR 格式。

## CDR 存储

CDR 存储可以通过多种方式实现。最常用的方式是 CSV 文本文件，便于导入电子表格。对于小型企业来说，这通常已经足够。一些计费软件默认接受 CSV 文件。然而，将 CDR 存储在数据库中要好得多，也更安全。Asterisk 支持多种数据库类型。市场上也有一些计费的图形界面。面对如此多的驱动，应该选择哪一个？

### 可用的存储驱动

- cdr_csv – 逗号分隔值文本文件
- cdr_custom – 可自定义的逗号分隔值文本文件
- cdr_adaptive_odbc – 自适应 ODBC 后端（推荐用于数据库存储）
- cdr_odbc – unixODBC 支持的数据库（旧版；推荐使用 cdr_adaptive_odbc）
- cdr_pgsql – Postgres 数据库
- cdr_tds (cdr_freetds) – 通过 FreeTDS 访问 Sybase 和 MSSQL 数据库
- cdr_manager – 将 CDR 发送到 Manager 接口
- cdr_radius – CDR radius 接口
- cdr_sqlite3_custom – SQLite3 自定义 CDR 模块

旧指南推荐的 `cdr_addon_mysql` (cdr_mysql) 模块已在 Asterisk 19 中移除，因此 Asterisk 22 上没有原生的 MySQL CDR 驱动。要将 CDR 写入 MySQL/MariaDB，请使用 `cdr_adaptive_odbc` 并配合 MySQL ODBC 驱动——本章节采用的方式。

CDR 记录会写入加载在文件 /etc/asterisk/modules.conf 中的所有活动模块。如果参数 autoload=yes 被设置，则会加载所有模块。要检查系统当前加载了哪些 cdr_drivers，请使用下面的命令：

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

如果看到上面的截图，至少有 cdr_adaptive_odbc、cdr_csv、cdr_custom、cdr_manager、cdr_odbc 和 cdr_sqlite3_custom 正在运行。近年来在一些 astricon 之后，我逐渐意识到 Asterisk 团队倾向于使用 ODBC。它是唯一支持连接池的驱动。连接池在性能方面有很大优势，因为不必为每次操作都打开新连接。本章节最初是使用 cdr_mysql 编写的。此次版本我改用了 cdr_adaptive_odbc，尽管它的设置稍微复杂一些。选择 cdr_adaptive_odbc 还能让我们自定义 CDR。只需在 dialplan 中设置一个新的 CDR 变量，并在数据库中添加相应的列。例如，记录音频抖动：

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### CSV 存储

正如前面所述，默认情况下，Asterisk 使用 cdr_csv.so 模块将所有 CDR 写入 CSV 文本文件。如果在 /var/log/asterisk/cdr-csv 中看不到文件，请使用 CLI 命令 `module show` 检查模块是否已加载。如果未加载，请检查 modules.conf。本章节将把 CDR 发送到 cdr_csv 作为备份。

### 配置文件 modules.conf

要仅加载所需的模块，请在 modules.conf 文件中使用以下行：

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

现在我们只加载了 cdr_csv 和 cdr_adaptive_odbc。

## Installing and configuring ODBC on Ubuntu 22.04

我总是后悔在书中发布详细的步骤说明。它们有时会在书出版之前就已经改变。版本会变，模块会变，所以请根据自己的实际情况调整这里的命令。大多数情况下，只需做一点小改动就能完成安装。请注意，即使是有经验的 Linux 用户也会在安装 ODBC 驱动时遇到困难。

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

Several applications are related to billing.

### CDR(accountcode)

Sets an account code before calling another application dial(); for example: Format:

```
Set(CDR(accountcode)=account)
```

The account code can be verified using the channel variable ${CDR(accountcode)}

### CDR(amaflags)

Set a flag for billing purposes. Options are default, omit, documentation, and billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Disables CDR recording for the current channel, so no CDR is written to the file or database. Setting it back to `0` re-enables recording.

```
Set(CDR_PROP(disable)=1)
```

The `NoCDR()` application that previous editions used for this was removed in Asterisk 21; on Asterisk 22 you disable a channel's CDR with `Set(CDR_PROP(disable)=1)` instead.

### ResetCDR()

Resets the Call Data Record: the `start` time (and, if answered, the `answer` time) is set to the current time and all CDR variables are wiped. If the `v` option is set, the CDR variables are preserved during the reset.

### Set(CDR(userfield)=Value)

This command sets a user field in the CDR. When using `cdr_adaptive_odbc`, the user field is automatically stored if a `userfield` column exists in the CDR table — no source recompilation needed. For CSV text files, you have to edit the source code (cdr_csv.c) and recompile Asterisk if you want to use user fields.

Earlier editions stored CDRs in MySQL with the `cdr_addon_mysql` module (`cdr_mysql.conf`). That module was removed in Asterisk 19, so it is not available on Asterisk 22. The supported path is now `cdr_adaptive_odbc` with a MySQL ODBC driver, which stores the user field — and any other custom column — natively through its adaptive column mapping.

### Appending to the user field

Earlier editions used the `AppendCDRUserField()` application to append data to the
CDR user field. That application was removed from Asterisk; on Asterisk 22 you append
to the user field by reading and re-setting it with the `CDR` function, for example
`Set(CDR(userfield)=${CDR(userfield)}extra)`.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## 用户认证

有些公司会把通话费用计入员工的账单。在 Asterisk 中，你可以设置一种认证方案，使得在 CDR 上对已认证的用户进行计费。此认证可以通过向 Authenticate 应用传递密码参数来完成——使用密码文件（在参数前加 `/`），或使用 Asterisk 数据库键（使用 `d` 选项）。格式：

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

选项：

- a – 将通道的账户代码设置为输入的密码。
- d – 将给定的路径解释为 Asterisk DB 键，而不是字面文件。
- m – 将路径解释为包含 `accountcode:passwordhash` 行的文件。
- r – 在成功认证后删除数据库键（仅在 `d` 有效时使用）。

如果呼叫者三次尝试全部失败，通道将被挂断；dialplan 执行不会继续，因此请在 `Authenticate()` 之后的行处理失败路径。示例（国际呼叫）：

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

旧的 `j` 选项（在失败时跳转到优先级 n+101）以及 `+101` 优先级约定早已在 Asterisk 中移除；失败的 `Authenticate()` 只会挂断。

要从控制台向数据库键插入密码：

```
asterisk*CLI> database put senha 123456 1
```

## 使用语音信箱密码

此应用的功能与 authenticate 相同，但使用语音信箱配置文件中的密码。

```
VMAuthenticate([mailbox][@context][,options])
```

如果指定了邮箱，则仅该邮箱的密码被视为有效。如果未指定邮箱，通道变量 `${AUTH_MAILBOX}` 将被设置为已认证的邮箱。如果设置了 `s` 选项，则会跳过初始提示。示例（国际呼叫）：

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

CDR records provide one summary row per call. For more detailed event tracking — such as individual channel state transitions, bridge enter/leave events, and attended transfer legs — Asterisk 22 includes **Channel Event Logging (CEL)**, configured via `/etc/asterisk/cel.conf` and stored through backends such as `cel_odbc` or `cel_custom`.

CEL complements CDR rather than replacing it: CDR remains the standard for billing summaries, while CEL gives granular per-event data useful for fraud detection, quality monitoring, and advanced reporting.

The `cel.conf` configuration pattern mirrors `cdr.conf`: you enable the event types you want in the `[general]` section of `cel.conf`, then configure each storage back-end in its own file — `cel_custom.conf` for CSV, `cel_odbc.conf` for an ODBC database (the same `res_odbc.conf` connection used for CDRs). You can confirm whether CEL is active with `cel show status` on the CLI.

## 摘要

在本章中，我们学习了如何在文本文件和 MySQL 数据库中实现 CDR 记录。我们还学习了如何设置 amaflags 和 account codes。章节末尾，我们学习了如何使用与 CDR 和计费集成的认证方案。

## Quiz

1. 默认情况下，Asterisk 将 CDR 记录在 /var/log/asterisk/cdr-csv 目录中。
   - A. False
   - B. True
2. Asterisk 可以将 CDR 写入（请选择所有适用项）：
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. CSV 文本文件
   - E. unixODBC 支持的数据库
3. Asterisk 同时只为一种存储方式生成 CDR。
   - A. False
   - B. True
4. 哪些 Asterisk amaflags 可用？
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. 要将部门关联到 CDR，您使用 ___ 命令，且可以通过 ___ 通道变量读取账户代码。
6. `Set(CDR_PROP(disable)=1)`和`ResetCDR()`的区别在于，禁用 CDR 会阻止任何记录被写入，而`ResetCDR()`会将当前记录重置（清零）。（之前用于禁用 CDR 的`NoCDR()`应用已在 Asterisk 21 中移除。）
   - A. False
   - B. True
7. 要在 `cdr_csv.so` 模块中使用用户自定义字段，必须编辑源代码并重新编译 Asterisk。
   - A. False
   - B. True
8. Authenticate() 应用可用的三种认证方法是：
   - A. Password
   - B. Password file
   - C. Asterisk DB (dbput and dbget)
   - D. Voicemail
9. Voicemail 密码在 `voicemail.conf` 的单独章节中指定，并且与 voicemail 用户不同。
   - A. False
   - B. True
10. Channel Event Logging (CEL) 在 Asterisk 22 中取代了 CDR —— 一旦启用 CEL，便不再生成 CDR 计费摘要。
    - A. False
    - B. True

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
