# Asterisk Real-Time

Como você sabe, a configuração do Asterisk é feita por meio do uso de vários arquivos de texto no diretório /etc/asterisk. Apesar da facilidade de usar arquivos de texto, há algumas desvantagens conhecidas:

- A necessidade de recarregar o Asterisk toda vez que os arquivos são alterados
- Aumento do uso de memória para um grande volume de usuários
- É difícil codificar uma interface de provisionamento usando arquivos de texto
- Não há possibilidade de integração com bancos de dados existentes

ARA ou Asterisk Realtime, como é conhecido, foi criado por Anthony Minessale II, Mark Spencer e Constantine Filin e foi projetado para permitir integração transparente com bancos de dados SQL. Uma interface LDAP também está disponível. Este sistema também é conhecido como Asterisk External Configuration e é configurado em /etc/asterisk/extconfig.conf. Você pode mapear arquivos de configuração para tabelas em um banco de dados (configuração estática) e entradas em tempo real para a criação dinâmica de objetos sem a necessidade de recarregar o Asterisk.

## Objetivos

Ao final deste capítulo, o leitor deverá ser capaz de:

- Compreender as vantagens e limitações do Asterisk Real Time.
- Utilizar ODBC para uso com ARA
- Compilar e instalar o ARA usando ODBC
- Testar o sistema em um ambiente de laboratório

## Como o Real Time do Asterisk funciona?

Na nova arquitetura Real Time, todo o código específico de banco de dados foi movido para os drivers de canal. O canal apenas chama uma rotina genérica que pesquisa o banco de dados. O resultado é um processo muito mais simples e limpo do ponto de vista do código‑fonte. O banco de dados é acessado por três funções:

- STATIC: usado para configurar uma configuração estática quando um módulo é carregado.  
- REALTIME: usado para pesquisar objetos durante uma chamada ou outro evento.  


- UPDATE: usado para atualizar objetos.

No Asterisk 22, os endpoints SIP são tratados pela pilha **PJSIP** (`res_pjsip`), que é construída sobre o modelo de objeto **Sorcery**. Com o assistente `realtime`, o Sorcery carrega cada objeto PJSIP do banco de dados sob demanda, e esses objetos então existem como objetos PJSIP configurados normais — não como os peers descartáveis de realtime que o antigo driver SIP descartava após cada chamada.

Como são objetos reais, a travessia NAT, qualify e a indicação de mensagem aguardando (MWI) funcionam normalmente para endpoints realtime. (O Sorcery pode ainda ser instruído a armazenar objetos em cache na memória via um assistente `memory_cache`, mas isso é opcional e separado do carregamento realtime.) Quando você altera um objeto no banco de dados, a mudança é capturada na próxima consulta; não é necessário recarregar após cada edição. (O modelo realtime aposentado `chan_sip`, com suas famílias `sippeers`/`sipusers`, é abordado apenas no capítulo *Legacy Channels*.)

## Configurando Asterisk Real Time

Para este laboratório, assumiremos que você já tem o ODBC instalado a partir do capítulo de CDR. O ARA é configurado no arquivo de texto extconfig.conf, onde duas seções podem ser vistas facilmente. A primeira é a seção de arquivos de configuração estáticos, onde você pode substituir os arquivos de configuração de texto por tabelas de banco de dados. A segunda seção é o mecanismo de configuração em tempo real, onde você configura tabelas de banco de dados para objetos dinâmicos (peers/users). Não é incomum usar arquivos de texto para a configuração estática e o banco de dados para entradas dinâmicas. Nesse caso, a primeira seção permanece intocada.

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

### Seção de configuração estática

A seção de configuração estática é onde você armazena o equivalente a arquivos de configuração no banco de dados. Essas configurações são lidas durante o carregamento do Asterisk. Alguns módulos relêem o banco de dados quando você recarrega. Exemplos de configuração estática são:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

O mapeamento de arquivo estático é mais útil para arquivos de configuração que não têm equivalente em tempo real por objeto. Para PJSIP, prefira as famílias em tempo real por objeto (`ps_endpoints`, `ps_aors`, e assim por diante) descritas mais adiante neste capítulo ao invés de mapear todo o `pjsip.conf` como um arquivo estático.

Três exemplos são descritos acima. No primeiro, você associa queues.conf a uma tabela queues no banco de dados asteriskdb. No segundo exemplo, você associa pjsip.conf à tabela pjsip_conf no banco de dados asteriskdb definido na configuração odbc. No último exemplo, você associa iax.conf a um diretório LDAP. MyBaseDN é o DN base a ser pesquisado. No exemplo anterior, o aplicativo app_queue.so é carregado enquanto o driver MySQL consulta o banco de dados e obtém as informações necessárias.

### Seção de configuração em tempo real

A configuração em tempo real (segunda parte do arquivo extconfig.conf) é onde o trecho de configuração a ser carregado é configurado, atualizado e descarregado em tempo real. Com tempo real, não é necessário recarregar as configurações. A sintaxe de tempo real segue:

```
<family name> => <driver>,<database name>[,table_name]
```

Exemplo:

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

Aqui temos cinco linhas de configuração. Na primeira linha, você associa a família PJSIP/Sorcery `ps_endpoints` a uma tabela `ps_endpoints` no banco de dados asteriskdb. Na última, você associa a família voicemail à tabela test no banco de dados asteriskdb. Cada tipo de objeto PJSIP (endpoint, aor, auth, contact) recebe sua própria família e tabela; o conjunto completo é mostrado na seção "PJSIP Realtime (Sorcery)" abaixo. As famílias `voicemail`, `extensions`, `queues` e `queue_members` ainda são válidas no Asterisk 22.

## PJSIP Realtime (Sorcery)

No Asterisk 22, os endpoints SIP são tratados exclusivamente pela pilha **PJSIP** (`res_pjsip`), que é construída sobre a camada de abstração de objetos **Sorcery**. Em vez de um único “peer” SIP, o PJSIP divide uma conta SIP em vários tipos de objetos, cada um armazenado em sua própria tabela realtime:

| Sorcery object type | Realtime table | What it holds |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | configurações por conta (context, codecs, DTMF, etc.) |
| aor (address of record) | ps_aors | limites de registro e configurações `qualify` |
| auth | ps_auths | credenciais `username` / `password` |
| contact | ps_contacts | o local registrado dinamicamente |
| domain alias | ps_domain_aliases | domínios SIP alternativos para um endpoint |
| endpoint identifier by IP | ps_endpoint_id_ips | correspondência de um endpoint por IP de origem |

O realtime para PJSIP é habilitado em dois locais. Primeiro, mapeie os tipos de objetos Sorcery para realtime em `extconfig.conf`:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Segundo, indique ao Sorcery para usar o assistente `realtime` para esses tipos de objeto em `sorcery.conf`. O nome do mapeamento (aqui `res_pjsip`) é o módulo cujos objetos você está realocando, e o valor à direita aponta para a família que você definiu em `extconfig.conf`:

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

Você pode misturar objetos estáticos e realtime. Se omitir um tipo de `sorcery.conf`, esse tipo de objeto continuará lendo de `pjsip.conf`. Um padrão comum é manter transports estáticos e configurações globais em `pjsip.conf` enquanto armazena endpoints, aors, auths e contacts no banco de dados.

### Criando o esquema realtime do PJSIP com Alembic

O Asterisk fornece migrações de banco de dados para todos os seus esquemas realtime em `contrib/ast-db-manage`. Esta é a forma suportada de criar (e atualizar a versão) as tabelas PJSIP — você não precisa mais escrever manualmente as definições de tabela `ps_*`. O conjunto de migrações `config` contém as tabelas PJSIP/Sorcery.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

Isso cria `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts` e as demais tabelas PJSIP com as colunas corretas para a versão do Asterisk em execução. (Alembic requer o pacote Python `alembic` mais um driver SQLAlchemy como `pymysql` para MySQL/MariaDB ou `psycopg2` para PostgreSQL.)

Um endpoint realtime mínimo consiste em uma linha em cada uma de três tabelas — por exemplo o endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

Depois de inserir as linhas não há nada para recarregar — o próximo REGISTER/INVITE buscará os objetos no banco de dados. Você pode confirmar o que o realtime retornou com:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Configuração do banco de dados

Agora que configuramos o arquivo extconfig.conf, vamos criar as tabelas. De modo geral, cada coluna do banco de dados corresponde a um nome de opção do arquivo de configuração correspondente. As tabelas PJSIP `ps_*` seguem essa regra: cada coluna `ps_endpoints` recebe o nome de uma opção de endpoint `pjsip.conf`, cada coluna `ps_auths` recebe o nome de uma opção de autenticação, e assim por diante. Por exemplo, o endpoint `pjsip.conf` abaixo,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

é armazenado como uma linha distribuída em três tabelas. A linha `ps_endpoints` contém `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`; a linha `ps_auths` contém `id=4000, auth_type=userpass, username=4000, password=supersecret`; e a linha `ps_aors` contém `id=4000, max_contacts=1`. Você só precisa preencher as colunas que realmente usa — qualquer coluna deixada NULL volta ao valor padrão da opção. Se quiser, por exemplo, o parâmetro `callerid` em um endpoint, preencha a coluna `callerid` de `ps_endpoints` (o nome da coluna é o mesmo da opção `pjsip.conf`).

Uma tabela de voicemail segue a mesma ideia. Suas colunas mapeiam para os campos `voicemail.conf`:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

O `uniqueid` deve ser único para cada usuário de voicemail e pode ser autoincrementado. Não precisa ter qualquer relação com a mailbox ou o context.

### Construindo um plano de discagem usando Asterisk Real Time

Você também pode usar o sistema em tempo real para criar o plano de discagem. O ARA usa a instrução `switch` para incluir as extensões em tempo real no plano de discagem normal contido no arquivo extensions.conf. A tabela de extensões deve ter a aparência abaixo:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

A família realtime `extensions` permanece inalterada no Asterisk 22; apenas certifique-se de que a coluna `appdata` disque canais PJSIP, por exemplo `PJSIP/4000`. No plano de discagem, você deve usar o comando `switch` para utilizar o tempo real.

![Construindo um plano de discagem com Asterisk Real Time: extensions.conf usa uma instrução `switch => realtime` para buscar linhas de extensão (context, exten, priority, app, data) de uma tabela de banco de dados em vez de do arquivo de texto.](../images/18-realtime-fig02.png)

```
[local]
switch => realtime
```

ou

```
[local]
switch => realtime/from-internal@extensions
```

## Lab: Installing and creating the database tables

In this lab, we will prepare the database to receive Asterisk parameters. We will prepare just the REALTIME tables. The static configuration will be left to the configuration text files (cool, isn't it?). Table creation in MySQL follows.

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

## Lab: Configurando e testando ARA

Neste laboratório vamos alterar a configuração do extconfig.conf para refletir nossa configuração de banco de dados e tabelas.

Passo 1: Configure o extconfig.conf e recarregue o Asterisk.

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

Observe as famílias `ps_endpoints`, `ps_aors`, `ps_auths` e `ps_contacts` acima; juntamente com os mapeamentos correspondentes `sorcery.conf` (veja a seção "PJSIP Realtime (Sorcery)") elas fazem o PJSIP ler suas contas do banco de dados. As famílias `voicemail` e `extensions` completam o exemplo.

Passo 2: Teste de extensão em tempo real. Crie um novo endpoint `6010` inserindo uma linha em cada um de `ps_auths`, `ps_aors` e `ps_endpoints`, então tente registrar esse endpoint com um softphone. Execute o SQL a seguir no cliente `mysql` (`mysql -u astdb -p astdb`):

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

As três linhas juntas descrevem uma conta SIP. As demais configurações da conta estão distribuídas pelos objetos PJSIP: context, codecs, modo DTMF e tratamento de mídia ao vivo no endpoint (as últimas seis colunas acima); o registro dinâmico vive no AOR. Não existe uma flag “dynamic” separada — um AOR aceita REGISTERs dinâmicos enquanto `max_contacts` for maior que zero, e cada localização registrada é gravada em `ps_contacts`.

No PJSIP, o modo DTMF out-of-band RFC 2833 / RFC 4733 recebe o nome `rfc4733`, e `dtmf_mode=rfc4733` é o padrão — portanto a coluna `dtmf_mode` acima é opcional e mostrada apenas para clareza.

Passo 3: Tente registrar o novo telefone com um softphone usando o nome de usuário `6010` e a senha `supersecret`. Confirme o registro no CLI do Asterisk:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Passo 4: Inclua as extensões no banco de dados.

```
mysql -u astdb -p
```

Digite a senha:

Use supersecret quando solicitado, então insira a linha da extensão a partir do cliente MySQL:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Passo 5: Inclua o Asterisk Real Time no dialplan. No contexto `default`:

```
switch => realtime/test@extensions
```

Recarregue as extensões para ativar a mudança.

```
asterisk-server*CLI> extensions reload
```

Passo 6: Reconfigure um dos telefones para o nome de usuário `bria`, se ainda não o fez.

Passo 7: Disque 6007 a partir de um telefone existente; o telefone `bria` deve tocar.

## Resumo

Neste capítulo, você aprendeu que o Asterisk Real Time permite colocar suas configurações em um banco de dados. O Asterisk fornece drivers nativos de realtime para ODBC (que alcança qualquer banco suportado pelo UnixODBC, incluindo MySQL/MariaDB e SQLite) e PostgreSQL, além de um driver de realtime LDAP para back‑ends de diretório. O MySQL/MariaDB é acessado através do ODBC, como fizemos neste capítulo (também existe um add‑on dedicado `res_config_mysql`, mas ele fica fora da compilação principal, portanto o ODBC é o caminho mais comum). A configuração é dividida em estática e em tempo real. A configuração estática substitui os arquivos de configuração, enquanto a configuração em tempo real cria objetos dinâmicos que são carregados apenas quando uma chamada ou outro evento relacionado ocorre. Concluímos com um laboratório prático sobre como instalar e configurar o ARA.

## Quiz

1. Asterisk Realtime é parte da distribuição padrão do Asterisk.
   - A. Verdadeiro
   - B. Falso
2. Os parâmetros de conexão de um servidor de banco de dados são configurados no arquivo:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. O arquivo `extconfig.conf` configura as tabelas usadas pelo Realtime. Ele tem duas seções distintas (marque duas):
   - A. Configuração estática
   - B. Configuração Realtime
   - C. Rotas de saída
   - D. Endereços IP e portas de banco de dados
4. Na configuração estática, uma vez que os objetos são carregados do banco de dados eles permanecem na memória do Asterisk e são atualizados apenas na inicialização ou recarga.
   - A. Verdadeiro
   - B. Falso
5. O realtime PJSIP (Sorcery) suporta totalmente `qualify` e MWI para endpoints realtime, porque o Sorcery os carrega como objetos PJSIP configurados ordinários ao invés de descartá‑los após cada chamada como os antigos peers SIP realtime.
   - A. Verdadeiro
   - B. Falso
6. No realtime PJSIP, quais tabelas armazenam os endpoints e seus contatos registrados?
   - A. `ps_endpoints` e `ps_contacts`
   - B. `ps_peers` e `ps_registry`
   - C. `ps_config` e `ps_data`
   - D. `extconfig` e `res_odbc`
7. Você ainda pode usar arquivos de configuração de texto mesmo após habilitar ARA.
   - A. Verdadeiro
   - B. Falso
8. phpMyAdmin é obrigatório quando você usa Realtime.
   - A. Verdadeiro
   - B. Falso
9. O banco de dados deve ser criado com todos os campos que existem no arquivo de configuração.
   - A. Verdadeiro
   - B. Falso
10. No Asterisk 22, qual é a forma recomendada e correta de versão para criar as tabelas realtime PJSIP (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`)?
    - A. Escrever manualmente as instruções `CREATE TABLE` para cada tabela `ps_*`
    - B. Importar o legado `mysql_config.sql` de `contrib/realtime/`
    - C. Executar as migrações Alembic `config` sob `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`)
    - D. As tabelas são criadas automaticamente na primeira vez que o Asterisk inicia

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
