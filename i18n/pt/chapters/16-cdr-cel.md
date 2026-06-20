# Registros Detalhados de Chamadas do Asterisk

Asterisk, como outras plataformas de telefonia, permite a cobrança de chamadas telefônicas. Vários programas no mercado podem importar os registros gerados pelos PBXs. Esses registros são usados para verificar o valor correto da fatura e estatísticas, entre outras coisas.

## Objetivos

- Descrever onde e em que formato os registros são gerados
- Gerar registros usando ODBC (Open Database Connectivity)
- Implementar um esquema de autenticação integrado com faturamento

## Formato CDR do Asterisk

Asterisk gera um registro de detalhes de chamada (CDR) para cada chamada. Esses registros são armazenados, por padrão, em um arquivo de texto em formato de valores separados por vírgula (CSV) em /var/log/asterisk/cdr-csv. O arquivo é organizado nos seguintes campos:

| Campo | Descrição | Tipo |
|-------|-----------|------|
| Accountcode | Número da conta a ser usado | String |
| Src | Número do Caller ID | String |
| Dst | Ramal de destino | String |
| Dcontext | Contexto de destino | String |
| Clid | Caller ID com texto | String |
| Channel | Canal usado | String |
| Dstchannel | Canal de destino | String |
| Lastapp | Última aplicação | String |
| Lastdata | Dados da última aplicação | String |
| Start | Início da chamada | Date/Time |
| Answer | Resposta da chamada | Date/Time |
| End | Fim da chamada | Date/Time |
| Duration | Tempo, do discar ao desligar | Integer (seconds) |
| Billsec | Tempo, da resposta ao desligar | Integer (seconds) |
| Disposition | O que aconteceu com a chamada (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | Flags (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | Campo definido pelo usuário | String |

Amostra de um arquivo CSV. Cada linha é um registro; os campos aparecem na mesma
ordem da tabela acima (`accountcode` primeiro, `amaflags` último):

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## Códigos de conta e contabilização automática de mensagens

Você pode especificar códigos de conta e flags ama em cada canal. Normalmente isso é feito no arquivo de configuração do canal (por exemplo, chan_dahdi.conf, pjsip.conf). O parâmetro amaflags define o que fazer com o registro CDR. Os valores possíveis para amaflag são:

- Default
- Omit
- Billing
- Documentation

Semelhante à forma como um registro pode ser marcado para cobrança ou documentação, um código de conta pode ser definido em cada registro. O código de conta é uma string de formato livre (a opção de endpoint `accountcode` aceita qualquer String, e o registro CDR o armazena em um campo de 80 caracteres) geralmente usado para atribuir um registro a um departamento ou unidade de negócios. Exemplo: seção de endpoint pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

A flag AMA não é uma opção de endpoint `pjsip.conf` no Asterisk 22; defina-a por chamada a partir do dialplan com a função `CHANNEL` (por exemplo `Set(CHANNEL(amaflags)=billing)`), ou com `Set(CDR(amaflags)=billing)`.

## Alterando o formato CSV e/ou CDR

Você pode alterar o formato CSV alterando o arquivo cdr_custom.conf.

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

Você pode alterar o formato CDR no arquivo cdr_custom.conf.

## CDR Storage

CDR storage can be achieved in several ways. The most important way is CSV text files that can be easily imported into spreadsheets. For small businesses, this is usually okay. Some billing software accepts, by default, CSV files. However, storing CDRs in a database is a lot better and safer. Asterisk supports several database flavors. There are some graphical interfaces for billing in the market. With so many drivers, which one to choose?

### Storage drivers available

- cdr_csv – Comma Separated Value text files
- cdr_custom – Customizable comma-separated-value text files
- cdr_adaptive_odbc – Adaptive ODBC backend (preferred for database storage)
- cdr_odbc – unixODBC supported databases (legacy; cdr_adaptive_odbc preferred)
- cdr_pgsql – Postgres databases
- cdr_tds (cdr_freetds) – Sybase and MSSQL databases via FreeTDS
- cdr_manager – CDR to Manager Interface
- cdr_radius – CDR radius interface
- cdr_sqlite3_custom – SQLite3 custom CDR module

The `cdr_addon_mysql` (cdr_mysql) module that older guides recommended was removed in Asterisk 19, so there is no native MySQL CDR driver on Asterisk 22. To write CDRs to MySQL/MariaDB, use `cdr_adaptive_odbc` together with a MySQL ODBC driver — the approach used in this chapter.

CDR recording is done to all active modules loaded in the file /etc/asterisk/modules.conf. If the parameter autoload=yes is set, all modules are loaded. To check which cdr_drivers are currently loaded in the system use the command below:

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

If you see the screenshot above, at least cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc and cdr_sqlite3_custom are running. In the latest years after some astricons it become clear for me the Asterisk team was favoring ODBC. It is the only driver supporting connection pooling. Connection pooling is a great advantage in terms of performance because you don’t have to open a new connection for every operation. This chapter was previously written using cdr_mysql. I have moved to cdr_adaptive_odbc for this edition even knowing that it is a little more complex to setup. The choice for cdr_adaptive_odbc also allows us to customize the CDR. You may simply set a new CDR variable in the dialplan and add the matching column to the database. For example, to record the audio jitter:

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### CSV Storage

As we said before, by default, Asterisk sends all CDR to a CSV text file using the cdr_csv.so module. If you can’t see the files in the /var/log/asterisk/cdr-csv, check to see if the module is being loaded using the CLI command module show. If it’s not loaded, check modules.conf. In this chapter we will send cdrs to cdr_csv as a backup.

### Configuring the file modules.conf

To load only the appropriate modules, use the lines below in the modules.conf file

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

Várias aplicações estão relacionadas à cobrança.

### CDR(accountcode)

Define um código de conta antes de chamar outra aplicação dial(); por exemplo: Formato:

```
Set(CDR(accountcode)=account)
```

O código de conta pode ser verificado usando a variável de canal ${CDR(accountcode)}

### CDR(amaflags)

Define uma bandeira para fins de cobrança. As opções são default, omit, documentation e billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Desabilita o registro de CDR para o canal atual, de modo que nenhum CDR é gravado no arquivo ou banco de dados. Definir novamente para `0` reabilita o registro.

```
Set(CDR_PROP(disable)=1)
```

A aplicação `NoCDR()` que edições anteriores usavam para isso foi removida no Asterisk 21; no Asterisk 22 você desabilita o CDR de um canal com `Set(CDR_PROP(disable)=1)` em vez disso.

### ResetCDR()

Reinicia o Call Data Record: o tempo `start` (e, se atendido, o tempo `answer`) é definido para o horário atual e todas as variáveis de CDR são apagadas. Se a opção `v` estiver definida, as variáveis de CDR são preservadas durante a reinicialização.

### Set(CDR(userfield)=Value)

Este comando define um campo de usuário no CDR. Ao usar `cdr_adaptive_odbc`, o campo de usuário é armazenado automaticamente se existir uma coluna `userfield` na tabela CDR — não é necessária recompilação da fonte. Para arquivos de texto CSV, você precisa editar o código‑fonte (cdr_csv.c) e recompilar o Asterisk se quiser usar campos de usuário.

Edições anteriores armazenavam CDRs no MySQL com o módulo `cdr_addon_mysql` (`cdr_mysql.conf`). Esse módulo foi removido no Asterisk 19, portanto não está disponível no Asterisk 22. O caminho suportado agora é `cdr_adaptive_odbc` com um driver MySQL ODBC, que armazena o campo de usuário — e qualquer outra coluna personalizada — nativamente através de seu mapeamento adaptativo de colunas.

### Appending to the user field

Edições anteriores usavam a aplicação `AppendCDRUserField()` para acrescentar dados ao campo de usuário do CDR. Essa aplicação foi removida do Asterisk; no Asterisk 22 você acrescenta ao campo de usuário lendo‑o e redefinindo‑o com a função `CDR`, por exemplo

`Set(CDR(userfield)=${CDR(userfield)}extra)`.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Autenticação de usuário

Algumas empresas cobram as chamadas de seus funcionários. No Asterisk você pode definir um esquema de autenticação que permite cobrar o usuário autenticado no CDR. Essa autenticação pode ser feita usando uma senha passada como parâmetro para o aplicativo Authenticate—um arquivo de senhas, indicado por uma / (barra) antes do parâmetro, ou uma chave do banco de dados do Asterisk (usando a opção `d`). Formato:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

Opções:

- a – Define o código de conta do canal para a senha inserida.  
- d – Interpreta o caminho fornecido como uma chave do DB do Asterisk em vez de um arquivo literal.  
- m – Interpreta o caminho como um arquivo de linhas `accountcode:passwordhash`.  
- r – Remove a chave do banco de dados após autenticação bem‑sucedida (válido somente com `d`).

Se o chamador falhar nas três tentativas, o canal é desligado; a execução do dialplan não continua, portanto trate o caminho de falha na linha após `Authenticate()`. Exemplo (Chamadas Internacionais):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

A antiga opção `j` (pular para a prioridade n+101 em caso de falha) e a convenção de prioridade `+101` foram removidas do Asterisk há muito tempo; um `Authenticate()` falhado simplesmente desliga.

Para inserir a senha em uma chave de DB a partir do console:

```
asterisk*CLI> database put senha 123456 1
```

## Usando senhas do voicemail

Este aplicativo faz o mesmo que authenticate, mas usa o arquivo de configuração de voicemail para a senha.

```
VMAuthenticate([mailbox][@context][,options])
```

Se uma caixa de correio for especificada, somente a senha dessa caixa será considerada válida. Se a caixa de correio não for especificada, a variável de canal `${AUTH_MAILBOX}` será definida com a caixa de correio autenticada. Se a opção `s` estiver definida, os prompts iniciais são pulados. Exemplo (Chamadas Internacionais):

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

Os registros CDR fornecem uma linha de resumo por chamada. Para um rastreamento de eventos mais detalhado — como transições individuais de estado de canal, eventos de entrada/saída de bridge e pernas de transferência atendida — o Asterisk 22 inclui **Channel Event Logging (CEL)**, configurado via `/etc/asterisk/cel.conf` e armazenado através de back‑ends como `cel_odbc` ou `cel_custom`.

O CEL complementa o CDR em vez de substituí‑lo: o CDR continua sendo o padrão para resumos de faturamento, enquanto o CEL fornece dados granulares por evento úteis para detecção de fraudes, monitoramento de qualidade e relatórios avançados.

O padrão de configuração `cel.conf` espelha `cdr.conf`: você habilita os tipos de evento desejados na seção `[general]` de `cel.conf`, então configura cada back‑end de armazenamento em seu próprio arquivo — `cel_custom.conf` para CSV, `cel_odbc.conf` para um banco de dados ODBC (a mesma conexão `res_odbc.conf` usada para CDRs). Você pode confirmar se o CEL está ativo com `cel show status` na CLI.

## Resumo

Neste capítulo aprendemos como implementar gravação de CDR em arquivos de texto e em um banco de dados MySQL. Também aprendemos como definir amaflags e códigos de conta. Ao final do capítulo, aprendemos como usar um esquema de autenticação integrado ao CDR e à cobrança.

## Quiz

1. Por padrão, o Asterisk registra o CDR no diretório /var/log/asterisk/cdr-csv.
   - A. False
   - B. True
2. O Asterisk pode gravar CDRs em (selecione todas as opções que se aplicam):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. arquivos de texto CSV
   - E. bancos de dados suportados por unixODBC
3. O Asterisk gera um CDR para apenas um tipo de armazenamento por vez.
   - A. False
   - B. True
4. Quais amaflags do Asterisk estão disponíveis?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Para associar um departamento a um CDR você usa o comando ___, e o código da conta pode ser lido com a variável de canal ___.
6. A diferença entre `Set(CDR_PROP(disable)=1)` e `ResetCDR()` é que desativar o CDR impede que qualquer registro seja escrito, enquanto `ResetCDR()` zera o registro atual. (A aplicação `NoCDR()` que anteriormente desativava CDRs foi removida no Asterisk 21.)
   - A. False
   - B. True
7. Para usar um campo definido pelo usuário com o módulo `cdr_csv.so`, você deve editar o código‑fonte e recompilar o Asterisk.
   - A. False
   - B. True
8. Os três métodos de autenticação disponíveis para a aplicação Authenticate() são:
   - A. Password
   - B. Password file
   - C. Asterisk DB (dbput and dbget)
   - D. Voicemail
9. As senhas de voicemail são especificadas em uma seção separada de `voicemail.conf` e não são as mesmas dos usuários de voicemail.
   - A. False
   - B. True
10. O Channel Event Logging (CEL) substitui o CDR no Asterisk 22 — uma vez que o CEL está habilitado, os resumos de cobrança do CDR não são mais produzidos.
    - A. False
    - B. True

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
