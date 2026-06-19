# Asterisk 通话详细记录 (CDR)

Asterisk 与其他电话平台一样，允许对通话进行计费。市场上有多种程序可以导入由 PBX 生成的记录。这些记录除其他用途外，还用于核实账单金额的准确性以及统计分析。

## 目标

读完本章后，读者应能够：

- 描述记录生成的位置和格式
- 使用 ODBC (Open Database Connectivity) 生成记录
- 实现与计费集成的身份验证方案

## Asterisk CDR 格式

Asterisk 为每次通话生成一条通话详细记录 (CDR)。默认情况下，这些记录以逗号分隔值 (CSV) 格式存储在 /var/log/asterisk/cdr-csv 目录下的文本文件中。该文件包含以下字段：CDR 描述 类型 大小 Accountcode 账户代码 字符串 Src 主叫号码 字符串 Dst 被叫分机 字符串 Dcontext 目标上下文 字符串 Caller ID with Text 主叫姓名 字符串 Channel 使用的通道 字符串 Dstchannel 目标通道 字符串 Lastapp 最后执行的应用程序 字符串 Lastdata 最后应用程序数据 字符串 Start 通话开始 日期/时间 Answer 通话应答 日期/时间 End 通话结束 日期/时间 Duration 从拨号到挂断的时间 整数（秒） Billsec 从应答到挂断的时间 整数（秒） Disposition 通话结果 字符串 (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags 标志 (DEFAULT, OMIT, BILLING, DOCUMENTATION) 字符串 User field 用户自定义字段 字符串 导入到表中的 CSV 文件示例。 AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## 账户代码与自动计费核算 (AMA)

你可以在每个通道上指定账户代码和 ama 标志。通常这在通道配置文件（例如 chan_dahdi.conf, pjsip.conf）中完成。参数 amaflags 定义了如何处理 CDR 记录。可能的 amaflag 值包括：

- Default
- Omit
- Billing
- Documentation

与记录可以标记为计费或文档类似，每个记录都可以设置一个账户代码。账户代码是一个自由格式的字符串（`accountcode` endpoint 选项接受任何字符串，CDR 记录将其存储在 80 个字符的字段中），通常用于将记录分配给某个部门或业务单元。示例：pjsip.conf endpoint 部分

```
[8576]
type=endpoint
accountcode=Support
```

在 Asterisk 22 中，AMA 标志不是一个`pjsip.conf` endpoint 选项；请通过 dialplan 使用`CHANNEL`函数（例如`Set(CHANNEL(amaflags)=billing)`）或使用`Set(CDR(amaflags)=billing)`按通话进行设置。

## 更改 CSV 和/或 CDR 格式

你可以通过更改 cdr_custom.conf 文件来更改 CSV 格式。

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

你可以在 cdr_custom.conf 文件中更改 CDR 格式。

## CDR 存储

CDR 存储可以通过多种方式实现。最主要的方式是 CSV 文本文件，它可以轻松导入到电子表格中。对于小型企业，这通常已经足够。一些计费软件默认接受 CSV 文件。然而，将 CDR 存储在数据库中会更好且更安全。Asterisk 支持多种数据库类型。市场上有一些用于计费的图形界面。面对如此多的驱动程序，该选择哪一个？

### 可用的存储驱动程序

- cdr_csv – 逗号分隔值文本文件
- cdr_custom – 可自定义的逗号分隔值文本文件
- cdr_adaptive_odbc – 自适应 ODBC 后端（数据库存储的首选）
- cdr_odbc – 支持 unixODBC 的数据库（旧版；首选 cdr_adaptive_odbc）
- cdr_pgsql – Postgres 数据库
- cdr_tds (cdr_freetds) – 通过 FreeTDS 连接的 Sybase 和 MSSQL 数据库
- cdr_manager – CDR 到管理接口
- cdr_radius – CDR radius 接口
- cdr_sqlite3_custom – SQLite3 自定义 CDR 模块

旧指南中推荐的`cdr_addon_mysql` (cdr_mysql) 模块已在 Asterisk 19 中移除，因此 Asterisk 22 中没有原生的 MySQL CDR 驱动程序。要将 CDR 写入 MySQL/MariaDB，请使用`cdr_adaptive_odbc`配合 MySQL ODBC 驱动程序——这也是本章采用的方法。

CDR 记录会发送给 /etc/asterisk/modules.conf 文件中加载的所有活动模块。如果设置了参数 autoload=yes，则会加载所有模块。要检查系统中当前加载了哪些 cdr_drivers，请使用以下命令：

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

如果你看到上面的截图，说明至少 cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc 和 cdr_sqlite3_custom 正在运行。在参加了几次 Astricon 会议后的这些年里，我很清楚 Asterisk 团队更倾向于 ODBC。它是唯一支持连接池的驱动程序。连接池在性能方面具有巨大优势，因为你无需为每个操作打开新连接。本章之前是使用 cdr_mysql 编写的。在本版中，我改用了 cdr_adaptive_odbc，尽管我知道它的设置稍微复杂一些。选择 cdr_adaptive_odbc 还允许我们自定义 CDR。你只需在 dialplan 中设置一个新的 CDR 变量，并将该列添加到数据库中即可。Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### CSV 存储

正如我们之前所说，默认情况下，Asterisk 使用 cdr_csv.so 模块将所有 CDR 发送到 CSV 文本文件。如果你无法在 /var/log/asterisk/cdr-csv 中看到文件，请使用 CLI 命令 module show 检查该模块是否已加载。如果未加载，请检查 modules.conf。在本章中，我们将把 CDR 发送到 cdr_csv 作为备份。

### 配置 modules.conf 文件

要仅加载适当的模块，请在 modules.conf 文件中使用以下行

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

现在我们只加载了 cdr_csv 和 cdr_adaptive_odbc。

## 在 Ubuntu 22.04 上安装和配置 ODBC

我总是很后悔在书中发布详细说明。它们的变化有时比书的出版还要快。版本在变，模块在变，所以请尝试根据你自己的情况调整这里的命令。大多数情况下，稍作修改就足以重现安装过程。请注意这些步骤，即使是有经验的 Linux 用户也会觉得安装 ODBC 驱动程序很困难。

第 1 步 - 安装所需的软件包：

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

第 2 步 - 创建数据库和用户：

```
mysql -u root -p
```

（使用你创建 mysql 服务器时定义的密码）在 mysql 命令行中输入这些命令

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

第 3 步 - 创建数据库

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

第 4 步：从 Oracle 下载 MySQL ODBC 连接器。使用以下命令检查你的操作系统：`lsb_release -a`。对于 Ubuntu 22.04 (x86_64)，请访问 https://dev.mysql.com/downloads/connector/odbc/ 并选择适用于 Ubuntu 22.04 的当前 8.x 或 9.x 版本。确切的文件名和版本号会随时间变化，因此请将`VER`（如下所示）设置为当前 Linux glibc 构建版本的名称。

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

第 5 步：安装 ODBC 驱动程序

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

第 6 步 - 配置 ODBC 连接器，编辑 /etc/odbc.ini 文件以创建 DSN (数据源名称)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

第 7 步：使用 iSQL 测试驱动程序访问。iSQL 是一个用于通过 unixodbc 连接到数据库的命令行实用程序。

```
isql -v astconn astdb supersecret
>show tables
```

请在无法看到 isql 命令的结果之前，不要继续进行 Asterisk 配置。

### 在 Asterisk 中配置 ODBC

在配置 cdr_adaptive_odbc 之前，你应该先配置 ODBC 资源文件。

第 1 步 - 将 Asterisk 连接到 ODBC。编辑文件 res_odbc.conf：

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

第 2 步 – 重启 Asterisk 并使用以下命令进行测试

```
CLI>odbc show
```

输出如下所示。

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

第 3 步 – 在 /etc/asterisk/cdr_adaptive_odbc.conf 中配置自适应 ODBC 驱动程序

```
[cdr]
connection=cdr
table=cdr
```

此处`connection`指向`res_odbc.conf`中定义的`[cdr]`连接部分，而`table`是写入 CDR 的数据库表。

第 4 步 – 重新加载模块 cdr_adaptive_odbc.so：

```
asterisk*CLI>reload cdr_adaptive_odbc
```

第 5 步 – 进行一些通话并检查数据库中是否有新记录。要检查数据库：

```
mysql –u root –p
>use astdb
>select * from cdr
```

## 应用程序和函数

有几个应用程序与计费相关。

### CDR(accountcode)

在调用另一个应用程序 dial() 之前设置账户代码；例如：格式：

```
Set(CDR(accountcode)=account)
```

可以使用通道变量 ${CDR(accountcode)} 来验证账户代码

### CDR(amaflags)

为计费目的设置标志。选项包括 default, omit, documentation 和 billing。

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

禁用当前通道的 CDR 记录，因此不会将 CDR 写入文件或数据库。将其设置回`0`可重新启用记录。

```
Set(CDR_PROP(disable)=1)
```

之前版本用于此目的的`NoCDR()`应用程序已在 Asterisk 21 中移除；在 Asterisk 22 上，你可以改用`Set(CDR_PROP(disable)=1)`来禁用通道的 CDR。

### ResetCDR()

重置通话数据记录：`start`时间（如果已应答，则为`answer`时间）被设置为当前时间，并且所有 CDR 变量都被清除。如果设置了`v`选项，CDR 变量将在重置期间保留。

### Set(CDR(userfield)=Value)

此命令设置 CDR 中的用户字段。使用`cdr_adaptive_odbc`时，如果 CDR 表中存在`userfield`列，则会自动存储用户字段——无需重新编译源代码。对于 CSV 文本文件，如果你想使用用户字段，则必须编辑源代码 (cdr_csv.c) 并重新编译 Asterisk。

早期版本使用`cdr_addon_mysql`模块 (`cdr_mysql.conf`) 将 CDR 存储在 MySQL 中。该模块已在 Asterisk 19 中移除，因此在 Asterisk 22 上不可用。目前支持的路径是使用带有 MySQL ODBC 驱动程序的`cdr_adaptive_odbc`，它通过其自适应列映射原生存储用户字段以及任何其他自定义列。

### AppendCDRUserField(Value)

将数据附加到 CDR 上的用户字段。

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## 用户身份验证

有些公司向其员工收取通话费用。在 Asterisk 中，你可以设置一种身份验证方案，使你能够在 CDR 上对经过身份验证的用户进行计费。此身份验证可以使用作为参数传递给 Authenticate 应用程序的密码来完成——密码文件（参数前加 / 斜杠）或 Asterisk 数据库键（使用`d`选项）。格式：

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

选项：

- a – 将通道的账户代码设置为输入的密码。
- d – 将给定的路径解释为 Asterisk DB 键而不是字面文件。
- m – 将路径解释为`accountcode:passwordhash`行组成的文件。
- r – 成功验证后删除数据库键（仅对`d`有效）。

如果主叫方三次尝试均失败，通道将被挂断；dialplan 执行不会继续，因此请在`Authenticate()`之后的行上处理失败路径。示例（国际长途）：

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

旧的`j`选项（失败时跳转到优先级 n+101）和`+101`优先级约定早已从 Asterisk 中移除；失败的`Authenticate()`只会挂断通话。

要从控制台将密码插入 DB 键：

```
CLI> database put senha 123456 1
```

## 使用语音信箱密码

此应用程序的功能与 authenticate 相同，但使用语音信箱配置文件作为密码。

```
VMAuthenticate([mailbox][@context][,options])
```

如果指定了邮箱，则仅该邮箱的密码被视为有效。如果未指定邮箱，通道变量`${AUTH_MAILBOX}`将被设置为已验证的邮箱。如果设置了`s`选项，则跳过初始提示。示例（国际长途）：

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## 通道事件日志 (CEL)

CDR 记录为每次通话提供一行摘要。为了进行更详细的事件跟踪——例如单个通道状态转换、桥接进入/离开事件以及转接腿——Asterisk 22 包含了**通道事件日志 (CEL)**，通过`/etc/asterisk/cel.conf`配置，并存储在诸如`cel_odbc`或`cel_custom`等后端中。

CEL 是对 CDR 的补充而非替代：CDR 仍然是计费摘要的标准，而 CEL 提供可用于欺诈检测、质量监控和高级报告的细粒度每事件数据。

`cel.conf`配置模式镜像了`cdr.conf`：你在`cel.conf`的`[general]`部分启用所需的事件类型，然后在各自的文件中配置每个存储后端——`cel_custom.conf`用于 CSV，`cel_odbc.conf`用于 ODBC 数据库（与 CDR 使用相同的`res_odbc.conf`连接）。你可以使用 CLI 上的`cel show status`确认 CEL 是否处于活动状态。

## 总结

在本章中，我们学习了如何在文本文件和 MySQL 数据库中实现 CDR 记录。我们还学习了如何设置 amaflags 和账户代码。在章末，我们学习了如何使用与 CDR 和计费集成的身份验证方案。

## 测验

1. 默认情况下，Asterisk 将 CDR 记录在 /var/log/asterisk/cdr-csv 目录中。
   - A. 错误
   - B. 正确
2. Asterisk 可以将 CDR 写入（选择所有适用项）：
   - A. MySQL
   - B. 原生 Oracle
   - C. Microsoft SQL Server
   - D. CSV 文本文件
   - E. 支持 unixODBC 的数据库
3. Asterisk 一次只能为一种存储类型生成 CDR。
   - A. 错误
   - B. 正确
4. 哪些 Asterisk amaflags 是可用的？
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. 要将部门与 CDR 关联，请使用 ___ 命令，并且可以使用 ___ 通道变量读取账户代码。
6. `Set(CDR_PROP(disable)=1)`和`ResetCDR()`之间的区别在于，禁用 CDR 会阻止写入任何记录，而`ResetCDR()`会重置（清零）当前记录。（之前禁用 CDR 的`NoCDR()`应用程序已在 Asterisk 21 中移除。）
   - A. 错误
   - B. 正确
7. 要在`cdr_csv.so`模块中使用用户定义字段，必须编辑源代码并重新编译 Asterisk。
   - A. 错误
   - B. 正确
8. Authenticate() 应用程序可用的三种身份验证方法是：
   - A. 密码
   - B. 密码文件
   - C. Asterisk DB (dbput 和 dbget)
   - D. 语音信箱
9. 语音信箱密码在`voicemail.conf`的单独部分中指定，并且与语音信箱用户不同。
   - A. 错误
   - B. 正确
10. 通道事件日志 (CEL) 在 Asterisk 22 中取代了 CDR——一旦启用了 CEL，将不再生成 CDR 计费摘要。
    - A. 错误
    - B. 正确

**答案：** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
