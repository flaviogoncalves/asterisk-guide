# Asterisk Real-Time

正如您所知，Asterisk 的配置是通过使用位于 /etc/asterisk 目录下的多个文本文件来实现的。虽然使用文本文件很方便，但也存在一些已知的缺点：

- 每次修改文件后都需要重新加载 Asterisk
- 大量用户时会增加内存使用
- 使用文本文件难以编写配置接口
- 无法与现有数据库集成

ARA 或 Asterisk Realtime（即其名称）由 Anthony Minessale II、Mark Spencer 和 Constantine Filin 创建，旨在实现与 SQL 数据库的透明集成。也提供 LDAP 接口。该系统也被称为 Asterisk External Configuration，配置文件位于 /etc/asterisk/extconfig.conf。您可以将配置文件映射到数据库中的表（静态配置），以及将实时条目用于动态创建对象，而无需重新加载 Asterisk。

## 目标

By the end of this chapter, the reader should be able to:

- 了解 Asterisk Real Time 的优势和局限性。
- 使用 ODBC 与 ARA 配合使用
- 使用 ODBC 编译并安装 ARA
- 在实验环境中测试系统

## Asterisk 实时工作原理如何？

在新的实时架构中，所有特定于数据库的代码都已移至通道驱动程序。通道只调用一个通用例程来搜索数据库。从源代码的角度来看，这使得过程更加简洁清晰。数据库通过三个函数访问：

- STATIC：用于在模块加载时设置静态配置。
- REALTIME：用于在通话或其他事件期间搜索对象。


- UPDATE：用于更新对象。

在 Asterisk 22 中，SIP 端点由 **PJSIP** 堆栈（`res_pjsip`）处理，该堆栈基于 **Sorcery** 对象模型构建。通过 `realtime` 向导，Sorcery 按需从数据库加载每个 PJSIP 对象，这些对象随后以普通配置的 PJSIP 对象形式存在——而不是旧 SIP 驱动在每次通话后丢弃的临时实时对等体。

由于它们是真实对象，NAT 穿透、qualify 和消息等待指示（MWI）对实时端点都能正常工作。（Sorcery 还可以通过 `memory_cache` 向导被指示将对象缓存到内存中，但这需要自行选择，并且与实时加载分离。）当您在数据库中更改对象时，下一次查找时会自动拾取更改；无需在每次编辑后重新加载。（已退役的 `chan_sip` 实时模型及其 `sippeers`/`sipusers` 家族仅在 *Legacy Channels* 章节中介绍。）

## Configuring Asterisk Real Time

对于本实验，我们假设您已经在 CDR 章节中安装了 ODBC。ARA 在 extconfig.conf 文本文件中进行配置，其中可以清晰看到两个部分。第一部分是静态配置文件部分，您可以用数据库表来替代文本配置文件。第二部分是实时配置引擎，您在此为动态对象（peer/用户）配置数据库表。通常会对静态配置使用文本文件，而对动态条目使用数据库。在本例中，第一部分保持不变。

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

静态配置部分用于在数据库中存储相当于配置文件的内容。这些配置在 Asterisk 加载时读取。某些模块在重新加载时会重新读取数据库。静态配置的示例包括：

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

静态文件映射最适用于没有对应对象实时等价物的配置文件。对于 PJSIP，建议使用后文章节中描述的每对象实时族（`ps_endpoints`、`ps_aors`等），而不是将整个 `pjsip.conf` 映射为静态文件。

上面描述了三个示例。第一个示例中，您将 queues.conf 绑定到 asteriskdb 数据库中的 queues 表。第二个示例中，您将 pjsip.conf 绑定到在 ODBC 配置中定义的 asteriskdb 数据库的 pjsip_conf 表。最后一个示例中，您将 iax.conf 绑定到 LDAP 目录。MyBaseDN 是要搜索的基准 DN。在前面的示例中，加载了应用 app_queue.so，同时 MySQL 驱动查询数据库并获取所需信息。

### Real Time configuration section

实时配置（extconfig.conf 文件的第二部分）用于配置、更新和实时卸载要加载的配置片段。使用实时配置时，无需重新加载配置。实时语法如下：

```
<family name> => <driver>,<database name>[,table_name]
```

示例：

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

这里有五行配置。第一行中，您将 PJSIP/Sorcery 家族 `ps_endpoints` 绑定到 asteriskdb 数据库中的表 `ps_endpoints`。最后一行中，您将 voicemail 家族绑定到 asteriskdb 数据库中的 test 表。每种 PJSIP 对象类型（endpoint、aor、auth、contact）都有自己的家族和表；完整集合在下面的 “PJSIP Realtime (Sorcery)” 部分展示。`voicemail`、`extensions`、`queues`和`queue_members`家族在 Asterisk 22 中仍然有效。

## PJSIP 实时（Sorcery）

在 Asterisk 22 中，SIP 端点完全由 **PJSIP** 栈（`res_pjsip`）处理，该栈基于 **Sorcery** 对象抽象层构建。PJSIP 不再使用单一的 SIP “peer”，而是将一个 SIP 账户拆分为多种对象类型，每种对象存储在其各自的实时表中：

| Sorcery object type | Realtime table | 包含内容 |
|---------------------|----------------|----------|
| endpoint | ps_endpoints | 每个账户的设置（context、codecs、DTMF 等） |
| aor (address of record) | ps_aors | 注册限制和 `qualify` 设置 |
| auth | ps_auths | `username` / `password` 凭证 |
| contact | ps_contacts | 动态注册的位置 |
| domain alias | ps_domain_aliases | 端点的备用 SIP 域 |
| endpoint identifier by IP | ps_endpoint_id_ips | 按源 IP 匹配端点 |

PJSIP 的实时功能在两个位置启用。首先，在 `extconfig.conf` 中将 Sorcery 对象类型映射到实时：

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

其次，在 `sorcery.conf` 中告诉 Sorcery 对这些对象类型使用 `realtime` 向导。映射名称（此处为 `res_pjsip`）是您要迁移对象的模块，右侧的值指向您在 `extconfig.conf` 中定义的族：

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

您可以混合使用静态和实时对象。如果在 `sorcery.conf` 中省略某种类型，则该对象类型仍从 `pjsip.conf` 读取。常见的做法是将静态传输和全局设置保存在 `pjsip.conf` 中，而将端点、aors、auths 和 contacts 存储在数据库中。

### 使用 Alembic 创建 PJSIP 实时模式

Asterisk 在 `contrib/ast-db-manage` 下提供了所有实时模式的数据库迁移。这是创建（以及版本升级）PJSIP 表的受支持方式——您不再需要手动编写 `ps_*` 表定义。 `config` 迁移集包含了 PJSIP/Sorcery 表。

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

这将创建 `ps_endpoints`、`ps_aors`、`ps_auths`、`ps_contacts` 以及其他 PJSIP 表，并为运行中的 Asterisk 版本提供正确的列。（Alembic 需要 Python 的 `alembic` 包以及如 `pymysql`（用于 MySQL/MariaDB）或 `psycopg2`（用于 PostgreSQL）的 SQLAlchemy 驱动程序。）

一个最小的实时端点只需在三个表中各插入一行——例如端点 `6010`：

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

插入这些行后无需重新加载——下一个 REGISTER/INVITE 将直接从数据库中获取对象。您可以使用以下命令确认实时返回的内容：

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## 数据库配置

现在我们已经配置了 extconfig.conf 文件，接下来创建表。一般来说，每个数据库列对应相应配置文件中的选项名。PJSIP `ps_*` 表遵循此规则：每个 `ps_endpoints` 列以 `pjsip.conf` 端点选项命名，每个 `ps_auths` 列以认证选项命名，依此类推。例如，下面的 `pjsip.conf` 端点，

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

在三个表中存储为一行。 `ps_endpoints` 行保存 `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`； `ps_auths` 行保存 `id=4000, auth_type=userpass, username=4000, password=supersecret`； `ps_aors` 行保存 `id=4000, max_contacts=1`。只需填充实际使用的列——任何留为 NULL 的列将回退到选项的默认值。如果需要，例如在端点上使用 `callerid` 参数，请在 `ps_endpoints` 的 `callerid` 列中填写（列名与 `pjsip.conf` 选项名相同）。

语音邮件表遵循相同的思路。它的列映射到 `voicemail.conf` 字段：

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

`uniqueid` 应对每个语音邮件用户唯一，并且可以自增。它不必与 mailbox 或 context 有任何关联。

### 使用 Asterisk 实时构建 dialplan

也可以使用实时系统来创建 dialplan。ARA 使用 `switch` 语句将实时分机包含到 extensions.conf 文件中的普通 dialplan 中。分机表应如下所示：

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

`extensions` 实时族在 Asterisk 22 中保持不变；只需确保 `appdata` 列拨打 PJSIP 通道，例如 `PJSIP/4000`。在 dialplan 中，必须使用 `switch` 命令来使用实时。

![Building a dial plan with Asterisk Real Time: extensions.conf uses a `switch => realtime` statement to pull extension rows (context, exten, priority, app, data) from a database table instead of from the text file.](../images/18-realtime-fig02.png)

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

在本实验中，我们将准备数据库以接收 Asterisk 参数。我们只会准备 REALTIME 表。静态配置将保留在配置文本文件中（很酷，对吧？）。下面是 MySQL 中的表创建过程。

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

在本实验中，我们将修改 extconfig.conf 配置，以匹配我们的数据库配置和表。

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

注意上面的 `ps_endpoints`、`ps_aors`、`ps_auths` 和 `ps_contacts` 家族；以及对应的 `sorcery.conf` 映射（参见 “PJSIP Realtime (Sorcery)” 部分），它们使 PJSIP 能够从数据库读取其账户。 `voicemail` 和 `extensions` 家族补全了本示例。

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

这三行共同描述了一个 SIP 账户。其余的账户设置分布在 PJSIP 对象中：context、codecs、DTMF 模式以及媒体处理直接位于 endpoint 上（上表的最后六列）；动态注册信息位于 AOR 上。没有单独的 “dynamic” 标志——只要 `max_contacts` 大于零，AOR 就接受动态 REGISTER，并且每个已注册的位置都会写入 `ps_contacts`。

在 PJSIP 中，RFC 2833 / RFC 4733 带外 DTMF 模式称为 `rfc4733`, 而 `dtmf_mode=rfc4733` 是默认值——因此上表的 `dtmf_mode` 列是可选的，仅为说明而显示。

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

Step 7: Dial 6007 from an existing phone; the `bria` phone should ring.

## 摘要

在本章中，您已经了解到 Asterisk 实时（Real Time）允许您将配置放入数据库。Asterisk 提供了原生的实时驱动程序，支持 ODBC（可连接任何支持 UnixODBC 的数据库，包括 MySQL/MariaDB 和 SQLite）和 PostgreSQL，以及用于目录后端的 LDAP 实时驱动程序。MySQL/MariaDB 通过 ODBC 访问，正如本章所示（还有一个专用的 `res_config_mysql` 插件，但它位于核心构建之外，因此 ODBC 是常用路径）。配置分为静态和实时两部分。静态配置替代配置文件，而实时配置则创建仅在通话或其他相关事件发生时才加载的动态对象。我们最后通过一个实操实验，演示了如何安装和配置 ARA。

## 测验

1. Asterisk Realtime 是标准 Asterisk 发行版的一部分。
   - A. 正确
   - B. 错误
2. 数据库服务器的连接参数在以下文件中配置：
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. `extconfig.conf`文件配置 Realtime 使用的表。它有两个不同的部分（请选择两个）：
   - A. 静态配置
   - B. Realtime 配置
   - C. 出站路由
   - D. IP 地址和数据库端口
4. 在静态配置中，一旦对象从数据库加载，它们会保存在 Asterisk 的内存中，仅在启动或重新加载时刷新。
   - A. 正确
   - B. 错误
5. PJSIP realtime（Sorcery）完全支持 `qualify` 和 MWI 用于 realtime 端点，因为 Sorcery 将它们加载为普通配置的 PJSIP 对象，而不是像旧的 SIP realtime 对等体在每次呼叫后被丢弃。
   - A. 正确
   - B. 错误
6. 在 PJSIP realtime 中，哪些表保存端点及其已注册的联系人？
   - A. `ps_endpoints` 和 `ps_contacts`
   - B. `ps_peers` 和 `ps_registry`
   - C. `ps_config` 和 `ps_data`
   - D. `extconfig` 和 `res_odbc`
7. 启用 ARA 后仍然可以使用文本配置文件。
   - A. 正确
   - B. 错误
8. 使用 Realtime 时必须使用 phpMyAdmin。
   - A. 正确
   - B. 错误
9. 必须为配置文件中出现的每个字段在数据库中创建对应的列。
   - A. 正确
   - B. 错误
10. 在 Asterisk 22 上，创建 PJSIP realtime 表（`ps_endpoints`、`ps_aors`、`ps_auths`、`ps_contacts`）的推荐、版本对应的方式是什么？
    - A. 为每个 `ps_*` 表手动编写 `CREATE TABLE` 语句
    - B. 从 `contrib/realtime/` 导入旧的 `mysql_config.sql`
    - C. 在 `contrib/ast-db-manage`（`alembic -c config.ini upgrade head`）下运行 Alembic `config` 迁移
    - D. 第一次启动 Asterisk 时自动创建表

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
