# Registros de Detalhes de Chamadas (CDR) do Asterisk

O Asterisk, assim como outras plataformas de telefonia, permite a tarifação de chamadas telefônicas. Vários programas no mercado podem importar os registros gerados por PBXs. Esses registros são usados para verificar o valor correto da conta e estatísticas, entre outras coisas.

## Objetivos

Ao final deste capítulo, o leitor deverá ser capaz de:

- Descrever onde e em que formato os registros são gerados
- Gerar registros usando ODBC (Open Database Connectivity)
- Implementar um esquema de autenticação integrado com a tarifação

## Formato de CDR do Asterisk

O Asterisk gera um registro de detalhes de chamada (CDR) para cada chamada. Esses registros são armazenados, por padrão, em um arquivo de texto no formato de valores separados por vírgula (CSV) em /var/log/asterisk/cdr-csv. O arquivo é organizado nos seguintes campos: CDR Description Type Size Accountcode Account Number to use String Src Caller ID Number String Dst Destination Extension String Dcontext Destination Context String Caller ID with Text String Channel Channel Used String Dstchannel Destination channel String Lastapp Last application String Lastdata Last application data String Start Start of call Date/Time Answer Answer of call Date/Time End End of Call Date/Time Duration Time, from dial to hang up Integer (seconds) Billsec Time, from answer to hang up Integer (seconds) Disposition What Happened to the call String (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags Flags (DEFAULT, OMIT, BILLING, DOCUMENTATION) String User field User defined field String Amostra de arquivo csv importado para uma tabela. AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## Códigos de conta e contabilidade automatizada de mensagens (AMA)

Você pode especificar códigos de conta e flags ama em cada canal. Geralmente, isso é feito no arquivo de configuração do canal (por exemplo, chan_dahdi.conf, pjsip.conf). O parâmetro amaflags define o que fazer com o registro CDR. Os valores possíveis de amaflag são:

- Default
- Omit
- Billing
- Documentation

De forma semelhante à maneira como um registro pode ser marcado para faturamento ou documentação, um código de conta pode ser definido em cada registro. O código de conta é uma string de formato livre (a opção de endpoint `accountcode` aceita qualquer String, e o registro CDR armazena-o em um campo de 80 caracteres) geralmente usado para atribuir um registro a um departamento ou unidade de negócios. Exemplo: seção endpoint do pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

A flag AMA não é uma opção de endpoint `pjsip.conf` no Asterisk 22; defina-a por chamada a partir do dialplan com a função `CHANNEL` (por exemplo, `Set(CHANNEL(amaflags)=billing)`), ou com `Set(CDR(amaflags)=billing)`.

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

Você pode alterar o formato do CDR no arquivo cdr_custom.conf.

## Armazenamento de CDR

O armazenamento de CDR pode ser realizado de várias maneiras. A forma mais importante são arquivos de texto CSV que podem ser facilmente importados para planilhas. Para pequenas empresas, isso geralmente é aceitável. Alguns softwares de faturamento aceitam, por padrão, arquivos CSV. No entanto, armazenar CDRs em um banco de dados é muito melhor e mais seguro. O Asterisk suporta vários tipos de bancos de dados. Existem algumas interfaces gráficas para faturamento no mercado. Com tantos drivers, qual escolher?

### Drivers de armazenamento disponíveis

- cdr_csv – Arquivos de texto com valores separados por vírgula
- cdr_adaptive_odbc – Backend ODBC adaptativo (preferencial para armazenamento em banco de dados)
- cdr_odbc – Bancos de dados suportados por unixODBC (legado; cdr_adaptive_odbc é preferencial)
- cdr_pgsql – Bancos de dados Postgres
- cdr_mysql – Bancos de dados MySQL (**obsoleto**; use cdr_adaptive_odbc + driver MySQL ODBC em vez disso)
- cdr_freetds – Bancos de dados Sybase e MSSQL
- cdr_manager – CDR para Interface de Gerenciamento (Manager Interface)
- cdr_radius – Interface de CDR radius
- cdr_sqlite3_custom – Módulo de CDR personalizado SQLite3

A gravação de CDR é feita para todos os módulos ativos carregados no arquivo /etc/asterisk/modules.conf. Se o parâmetro autoload=yes estiver definido, todos os módulos são carregados. Para verificar quais cdr_drivers estão carregados atualmente no sistema, use o comando abaixo:

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

Se você vir a captura de tela acima, pelo menos cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc e cdr_sqlite3_custom estão em execução. Nos últimos anos, após algumas Astricons, ficou claro para mim que a equipe do Asterisk estava favorecendo o ODBC. É o único driver que suporta pool de conexões. O pool de conexões é uma grande vantagem em termos de desempenho, pois você não precisa abrir uma nova conexão para cada operação. Este capítulo foi escrito anteriormente usando cdr_mysql. Mudei para cdr_adaptive_odbc para esta edição, mesmo sabendo que é um pouco mais complexo de configurar. A escolha pelo cdr_adaptive_odbc também nos permite personalizar o CDR. Você pode simplesmente definir uma nova variável CDR no dialplan e adicionar a coluna ao banco de dados. Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### Armazenamento CSV

Como dissemos antes, por padrão, o Asterisk envia todos os CDRs para um arquivo de texto CSV usando o módulo cdr_csv.so. Se você não conseguir ver os arquivos em /var/log/asterisk/cdr-csv, verifique se o módulo está sendo carregado usando o comando CLI module show. Se não estiver carregado, verifique o modules.conf. Neste capítulo, enviaremos os CDRs para cdr_csv como backup.

### Configurando o arquivo modules.conf

Para carregar apenas os módulos apropriados, use as linhas abaixo no arquivo modules.conf

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Agora temos apenas cdr_csv e cdr_adaptive_odbc carregados.

## Instalando e configurando ODBC no Ubuntu 22.04

> **[Nota da 2ª ed.]** Os passos originais visavam o Ubuntu 18.04 e o MySQL Connector/ODBC 8.0.14. Os passos abaixo foram atualizados para o Ubuntu 22.04 LTS; ajuste as versões dos pacotes e URLs de download para corresponder à versão atual do MySQL Connector/ODBC em dev.mysql.com.

Sempre me arrependo de publicar instruções detalhadas no livro. Elas mudarão, às vezes antes mesmo de o livro ser publicado. As versões mudam, os módulos mudam, então tente adaptar o comando aqui à sua própria situação. Na maioria das vezes, pequenas mudanças são suficientes para reproduzir a instalação. Preste atenção nos passos, mesmo usuários experientes de Linux acharão difícil instalar os drivers ODBC.

Passo 1 - Instale os pacotes necessários:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Passo 2 - Crie um banco de dados e um usuário:

```
mysql -u root -p
```

(Use a senha definida quando você criou o servidor mysql) Digite estes comandos na linha de comando do mysql

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Passo 3 - Crie o banco de dados

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Passo 4: Baixe o conector MySQL ODBC da Oracle. Verifique seu sistema operacional usando: `lsb_release -a`. Para Ubuntu 22.04 (x86_64), visite https://dev.mysql.com/downloads/connector/odbc/ e escolha a versão 8.x ou 9.x atual para Ubuntu 22.04.

> **[Nota da 2ª ed.]** Verifique a URL de download exata e o nome do arquivo em dev.mysql.com; o número da versão e o sufixo do Ubuntu serão diferentes da 1ª edição. O exemplo abaixo usa uma versão de espaço reservado.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Passo 5: Instale o driver ODBC

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Passo 6 - Configure o conector ODBC editando o arquivo /etc/odbc.ini para criar o DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Passo 7: Teste o acesso ao driver usando iSQL. iSQL é um utilitário de linha de comando para conectar ao banco de dados via unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Por favor, não prossiga com a configuração do Asterisk se você não conseguir ver o resultado do comando isql.

### Configurando ODBC no Asterisk

Antes de configurar o cdr_adaptive_odbc, você deve primeiro configurar o arquivo de recursos ODBC.

Passo 1 - Conecte o Asterisk ao ODBC. Edite o arquivo res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Passo 2 – Reinicie o Asterisk e teste usando

```
CLI>odbc show
```

A saída é mostrada abaixo.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Passo 3 – Configure o driver ODBC adaptativo em /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Aqui `connection` aponta para a seção de conexão `[cdr]` definida em `res_odbc.conf`, e `table` é a tabela do banco de dados onde os CDRs são gravados.

Passo 4 – Recarregue o módulo cdr_adaptive_odbc.so:

```
asterisk*CLI>reload cdr_adaptive_odbc
```

Passo 5 – Faça algumas chamadas e verifique o banco de dados em busca de novos registros. Para verificar o banco de dados:

```
mysql –u root –p
>use astdb
>select * from cdr
```

## Aplicações e funções

Várias aplicações estão relacionadas ao faturamento.

### CDR(accountcode)

Define um código de conta antes de chamar outra aplicação dial(); por exemplo: Formato:

```
Set(CDR(accountcode)=account)
```

O código de conta pode ser verificado usando a variável de canal ${CDR(accountcode)}

### CDR(amaflags)

Define uma flag para fins de faturamento. As opções são default, omit, documentation e billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Desativa a gravação de CDR para o canal atual, para que nenhum CDR seja gravado no arquivo ou banco de dados. Definir de volta para `0` reativa a gravação.

```
Set(CDR_PROP(disable)=1)
```

> **[Nota da 2ª ed.]** O texto original usava a aplicação `NoCDR()`. `NoCDR` foi descontinuada e depois removida no Asterisk 21; use `Set(CDR_PROP(disable)=1)` em vez disso.

### ResetCDR()

Redefine o Registro de Dados de Chamada: o tempo `start` (e, se atendida, o tempo `answer`) é definido para o horário atual e todas as variáveis de CDR são apagadas. Se a opção `v` estiver definida, as variáveis de CDR são preservadas durante a redefinição.

### Set(CDR(userfield)=Value)

Este comando define um campo de usuário no CDR. Ao usar `cdr_adaptive_odbc`, o campo de usuário é armazenado automaticamente se uma coluna `userfield` existir na tabela CDR — sem necessidade de recompilação do código-fonte. Para arquivos de texto CSV, você precisa editar o código-fonte (cdr_csv.c) e recompilar o Asterisk se quiser usar campos de usuário.

> **[Nota da 2ª ed.]** O texto original fazia referência a `cdr_addon_mysql` e `cdr_mysql.conf`. O módulo `cdr_mysql` está obsoleto no Asterisk 22; o caminho recomendado é `cdr_adaptive_odbc` com um driver MySQL ODBC, que suporta campos de usuário nativamente através do mapeamento de colunas adaptativo.

### AppendCDRUserField(Value)

Anexa dados ao campo de usuário no CDR.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Autenticação de usuário

Algumas empresas cobram as chamadas de seus funcionários. No Asterisk, você pode definir um esquema de autenticação que permite cobrar o usuário autenticado no CDR. Essa autenticação pode ser feita usando uma senha passada como parâmetro para a aplicação Authenticate — um arquivo de senha, indicado por uma / (barra) antes do parâmetro ou um banco de dados Asterisk (dbput/dbget). Formato:

```
Authenticate(password[|options])
Authenticate(/passwdfile|[|options])
Authenticate(</db-keyfamily|d>options)
```

Opções:

- a – Define o código da conta como a senha.
- d – Interpreta o parâmetro como uma chave do banco de dados Asterisk
- r – Remove a chave após a autenticação bem-sucedida (apenas com a opção 'd')
- j – Pula para a prioridade n+101 para autenticação inválida

Exemplo: (Chamadas Internacionais)

```
exten=_9011.,1,Authenticate(/password|daj)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

Para inserir a senha em uma chave de banco de dados a partir do console:

```
CLI> database put senha 123456 1
```

## Usando senhas de voicemail

Esta aplicação faz o mesmo que authenticate, mas usa o arquivo de configuração de voicemail para a senha.

```
VMAuthenticate([mailbox][@context][|options])
```

Se uma caixa postal for especificada, apenas a senha da caixa postal será considerada válida. Se a caixa postal não for especificada, uma variável de canal AUTH_MAILBOX será definida com a caixa postal autenticada. Se a opção 's' (silencioso) estiver definida, nenhum prompt será executado. Exemplo: (Chamadas Internacionais)

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local|ajs)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

## Registro de Eventos de Canal (CEL)

Os registros CDR fornecem uma linha de resumo por chamada. Para um rastreamento de eventos mais detalhado — como transições de estado de canal individual, eventos de entrada/saída de ponte e pernas de transferência assistida — o Asterisk 22 inclui o **Channel Event Logging (CEL)**, configurado via `/etc/asterisk/cel.conf` e armazenado através de backends como `cel_odbc` ou `cel_custom`.

O CEL complementa o CDR em vez de substituí-lo: o CDR permanece o padrão para resumos de faturamento, enquanto o CEL fornece dados granulares por evento, úteis para detecção de fraude, monitoramento de qualidade e relatórios avançados.

> **[Nota da 2ª ed.]** Considere adicionar uma subseção curta de CEL ou uma referência direta a um capítulo de faturamento avançado se o programa cobrir isso. O padrão de configuração `cel.conf` espelha o `cdr.conf`.

## Resumo

Neste capítulo, aprendemos como implementar a gravação de CDR em arquivos de texto e em um banco de dados MySQL. Também aprendemos como definir amaflags e códigos de conta. Ao final do capítulo, aprendemos como usar um esquema de autenticação integrado com CDR e faturamento.

## Questionário

1. Por padrão, o Asterisk registra o CDR no diretório /var/log/asterisk/cdr-csv.
   - A. Falso
   - B. Verdadeiro
2. O Asterisk pode gravar CDRs em (selecione todas as que se aplicam):
   - A. MySQL
   - B. Oracle nativo
   - C. Microsoft SQL Server
   - D. Arquivos de texto CSV
   - E. Bancos de dados suportados por unixODBC
3. O Asterisk gera um CDR para apenas um tipo de armazenamento por vez.
   - A. Falso
   - B. Verdadeiro
4. Quais amaflags do Asterisk estão disponíveis?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Para associar um departamento a um CDR, você usa o comando ___, e o código da conta pode ser lido com a variável de canal ___.
6. A diferença entre `Set(CDR_PROP(disable)=1)` e `ResetCDR()` é que desativar o CDR impede que qualquer registro seja gravado, enquanto `ResetCDR()` redefine (zera) o registro atual. (A aplicação `NoCDR()` que desativava anteriormente os CDRs foi removida no Asterisk 21.)
   - A. Falso
   - B. Verdadeiro
7. Para usar um campo definido pelo usuário com o módulo `cdr_csv.so`, você deve editar o código-fonte e recompilar o Asterisk.
   - A. Falso
   - B. Verdadeiro
8. Os três métodos de autenticação disponíveis para a aplicação Authenticate() são:
   - A. Senha
   - B. Arquivo de senha
   - C. Banco de dados Asterisk (dbput e dbget)
   - D. Voicemail
9. As senhas de voicemail são especificadas em uma seção separada de `voicemail.conf` e não são as mesmas dos usuários de voicemail.
   - A. Falso
   - B. Verdadeiro
10. O Channel Event Logging (CEL) substitui o CDR no Asterisk 22 — uma vez que o CEL é ativado, os resumos de faturamento de CDR não são mais produzidos.
    - A. Falso
    - B. Verdadeiro

**Respostas:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
