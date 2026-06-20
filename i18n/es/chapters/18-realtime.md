# Asterisk Real-Time

Como sabes, la configuración de Asterisk se logra mediante el uso de varios archivos de texto en el directorio /etc/asterisk. A pesar de la facilidad de usar archivos de texto, existen algunas desventajas conocidas:

- La necesidad de recargar Asterisk cada vez que se cambian los archivos
- Mayor uso de memoria para un gran volumen de usuarios
- Es difícil codificar una interfaz de aprovisionamiento usando archivos de texto
- No hay posibilidad de integración con bases de datos existentes

ARA o Asterisk Realtime, como se le conoce, fue creado por Anthony Minessale II, Mark Spencer y Constantine Filin y fue diseñado para permitir una integración transparente con bases de datos SQL. También está disponible una interfaz LDAP. Este sistema también se conoce como Asterisk External Configuration y se configura en /etc/asterisk/extconfig.conf. Puedes mapear archivos de configuración a tablas en una base de datos (configuración estática) y entradas en tiempo real para la creación dinámica de objetos sin necesidad de recargar Asterisk.

## Objetivos

Al final de este capítulo, el lector debería ser capaz de:

- Entender las ventajas y limitaciones de Asterisk Real Time.
- Utilizar ODBC para su uso con ARA
- Compilar e instalar ARA usando ODBC
- Probar el sistema en un entorno de laboratorio

## ¿Cómo funciona Asterisk Real Time?

En la nueva arquitectura Real Time, todo el código específico de la base de datos se trasladó a los controladores de canal. El canal solo llama a una rutina genérica que busca en la base de datos. El resultado es un proceso mucho más simple y limpio desde el punto de vista del código fuente. La base de datos es accedida por tres funciones:

- STATIC: Se usa para establecer una configuración estática cuando se carga un módulo.
- REALTIME: Se usa para buscar objetos durante una llamada u otro evento.


- UPDATE: Se usa para actualizar objetos.

En Asterisk 22, los endpoints SIP son manejados por la pila **PJSIP** (`res_pjsip`), que está construida sobre el modelo de objetos **Sorcery**. Con el asistente `realtime`, Sorcery carga cada objeto PJSIP de la base de datos bajo demanda, y esos objetos existen entonces como objetos PJSIP configurados ordinarios — no como los peers temporales de realtime que el controlador SIP antiguo descartaba después de cada llamada.

Debido a que son objetos reales, el recorrido NAT, qualify y la indicación de mensajes en espera (MWI) funcionan normalmente para los endpoints realtime. (Sorcery también puede configurarse para almacenar en caché objetos en memoria mediante un asistente `memory_cache`, pero eso es opcional y separado de la carga realtime.) Cuando cambias un objeto en la base de datos, el cambio se detecta en la siguiente búsqueda; no necesitas recargar después de cada edición. (El modelo realtime retirado `chan_sip`, con sus familias `sippeers`/`sipusers`, se cubre solo en el capítulo *Legacy Channels*.)

## Configurando Asterisk Real Time

Para este laboratorio, asumiremos que ya tiene ODBC instalado desde el capítulo CDR. ARA se configura en el archivo de texto extconfig.conf, donde se pueden ver fácilmente dos secciones. La primera es la sección de archivos de configuración estáticos, donde puede sustituir los archivos de configuración de texto por tablas de base de datos. La segunda sección es el motor de configuración en tiempo real, donde configura tablas de base de datos para objetos dinámicos (peers/users). No es inusual usar archivos de texto para la configuración estática y la base de datos para entradas dinámicas. En este caso, la primera sección permanece sin cambios.

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

### Sección de configuración estática

La sección de configuración estática es donde almacena el equivalente a los archivos de configuración en la base de datos. Estas configuraciones se leen durante la carga de Asterisk. Algunos módulos vuelven a leer la base de datos cuando usted recarga. Ejemplos de la configuración estática son:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

El mapeo de archivos estáticos es más útil para archivos de configuración que no tienen equivalente en tiempo real por objeto. Para PJSIP, prefiera las familias en tiempo real por objeto (`ps_endpoints`, `ps_aors`, etc.) descritas más adelante en este capítulo en lugar de mapear todo `pjsip.conf` como un archivo estático.

Se describen tres ejemplos arriba. En el primero, enlaza queues.conf a una tabla queues en la base de datos asteriskdb. En el segundo ejemplo, enlaza pjsip.conf a la tabla pjsip_conf en la base de datos asteriskdb definida en la configuración odbc. En el último ejemplo, enlaza iax.conf a un directorio LDAP. MyBaseDN es el DN base que se buscará. En el ejemplo anterior, la aplicación app_queue.so se carga mientras el controlador MySQL consulta la base de datos y obtiene la información requerida.

### Sección de configuración en tiempo real

La configuración en tiempo real (segunda parte del archivo extconfig.conf) es donde se configura, actualiza y descarga la pieza de configuración que se cargará en tiempo real. Con tiempo real, no es necesario recargar las configuraciones. La sintaxis de tiempo real es la siguiente:

```
<family name> => <driver>,<database name>[,table_name]
```

Ejemplo:

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

Aquí tenemos cinco líneas de configuración. En la primera línea, enlaza la familia PJSIP/Sorcery `ps_endpoints` a una tabla `ps_endpoints` en la base de datos asteriskdb. En la última, enlaza la familia voicemail a la tabla test en la base de datos asteriskdb. Cada tipo de objeto PJSIP (endpoint, aor, auth, contact) obtiene su propia familia y tabla; el conjunto completo se muestra en la sección "PJSIP Realtime (Sorcery)" a continuación. Las familias `voicemail`, `extensions`, `queues` y `queue_members` siguen siendo válidas en Asterisk 22.

## PJSIP Realtime (Sorcery)

En Asterisk 22, los puntos finales SIP son manejados exclusivamente por la pila **PJSIP** (`res_pjsip`), que está construida sobre la capa de abstracción de objetos **Sorcery**. En lugar de un único “peer” SIP, PJSIP divide una cuenta SIP en varios tipos de objetos, cada uno almacenado en su propia tabla realtime:

| Sorcery object type | Realtime table | Qué contiene |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | configuraciones por cuenta (context, codecs, DTMF, etc.) |
| aor (address of record) | ps_aors | límites de registro y configuraciones `qualify` |
| auth | ps_auths | credenciales `username` / `password` |
| contact | ps_contacts | la ubicación registrada dinámicamente |
| domain alias | ps_domain_aliases | dominios SIP alternativos para un endpoint |
| endpoint identifier by IP | ps_endpoint_id_ips | coincidencia de un endpoint por IP de origen |

Realtime para PJSIP se habilita en dos lugares. Primero, mapee los tipos de objetos Sorcery a realtime en `extconfig.conf`:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Segundo, indique a Sorcery que use el asistente `realtime` para esos tipos de objetos en `sorcery.conf`. El nombre del mapeo (aquí `res_pjsip`) es el módulo cuyos objetos está reubicando, y el valor de la derecha apunta a la familia que definió en `extconfig.conf`:

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

Puede mezclar objetos estáticos y realtime. Si omite un tipo de `sorcery.conf`, ese tipo de objeto seguirá leyendo de `pjsip.conf`. Un patrón común es mantener los transportes estáticos y la configuración global en `pjsip.conf` mientras se almacenan los endpoints, aors, auths y contacts en la base de datos.

### Creación del esquema realtime de PJSIP con Alembic

Asterisk incluye migraciones de base de datos para todos sus esquemas realtime bajo `contrib/ast-db-manage`. Esta es la forma soportada de crear (y actualizar de versión) las tablas PJSIP — ya no necesita escribir a mano las definiciones de tabla `ps_*`. El conjunto de migraciones `config` contiene las tablas PJSIP/Sorcery.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

Esto crea `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts` y las demás tablas PJSIP con las columnas correctas para la versión de Asterisk en ejecución. (Alembic requiere el paquete Python `alembic` más un driver SQLAlchemy como `pymysql` para MySQL/MariaDB o `psycopg2` para PostgreSQL.)

Un endpoint realtime mínimo consiste entonces en una fila en cada una de tres tablas — por ejemplo el endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

Después de insertar las filas no hay nada que recargar — el siguiente REGISTER/INVITE extrae los objetos de la base de datos. Puede confirmar lo que realtime devolvió con:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Configuración de la base de datos

Ahora que hemos configurado el archivo extconfig.conf, vamos a crear las tablas. En términos generales, cada columna de la base de datos coincide con un nombre de opción del archivo de configuración correspondiente. Las tablas PJSIP `ps_*` siguen esta regla: cada columna `ps_endpoints` lleva el nombre de una opción de endpoint `pjsip.conf`, cada columna `ps_auths` lleva el nombre de una opción de autenticación, y así sucesivamente. Por ejemplo, el endpoint `pjsip.conf` a continuación,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

se almacena como una fila distribuida en tres tablas. La fila `ps_endpoints` contiene `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`; la fila `ps_auths` contiene `id=4000, auth_type=userpass, username=4000, password=supersecret`; y la fila `ps_aors` contiene `id=4000, max_contacts=1`. Sólo necesita rellenar las columnas que realmente use — cualquier columna que deje en NULL volverá al valor predeterminado de la opción. Si desea, por ejemplo, el parámetro `callerid` en un endpoint, complete la columna `callerid` de `ps_endpoints` (el nombre de la columna es el mismo que el nombre de la opción `pjsip.conf`).

Una tabla de voicemail sigue la misma idea. Sus columnas se asignan a los campos `voicemail.conf`:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

El `uniqueid` debe ser único para cada usuario de voicemail y puede ser autoincremental. No necesita tener ninguna relación con el mailbox o el context.

### Construcción de un dialplan usando Asterisk Real Time

También puede usar el sistema en tiempo real para crear el dialplan. ARA utiliza la sentencia `switch` para incluir las extensiones en tiempo real en el dialplan normal contenido en el archivo extensions.conf. La tabla de extensiones debería verse como la siguiente:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

La familia realtime `extensions` no ha cambiado en Asterisk 22; solo asegúrese de que la columna `appdata` marque canales PJSIP, por ejemplo `PJSIP/4000`. En el dialplan, debe usar el comando `switch` para emplear el tiempo real.

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

## Lab: Configurando y probando ARA

En este laboratorio cambiaremos la configuración de **extconfig.conf** para que refleje nuestra configuración y tablas de base de datos.

Paso 1: Configure **extconfig.conf** y recargue Asterisk.

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

Observe las familias `ps_endpoints`, `ps_aors`, `ps_auths` y `ps_contacts` arriba; junto con los mapeos correspondientes `sorcery.conf` (vea la sección “PJSIP Realtime (Sorcery)”) hacen que PJSIP lea sus cuentas de la base de datos. Las familias `voicemail` y `extensions` completan el ejemplo.

Paso 2: Prueba de extensión en tiempo real. Cree un nuevo endpoint `6010` insertando una fila en cada una de `ps_auths`, `ps_aors` y `ps_endpoints`, luego intente registrar este endpoint con un softphone. Ejecute el siguiente SQL en el cliente `mysql` (`mysql -u astdb -p astdb`):

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

Las tres filas describen una cuenta SIP. Los ajustes restantes de la cuenta están distribuidos entre los objetos PJSIP: contexto, códecs, modo DTMF y manejo de medios en vivo en el endpoint (las últimas seis columnas arriba); el registro dinámico vive en el AOR. No existe una bandera “dinámica” separada — un AOR acepta REGISTERs dinámicos siempre que `max_contacts` sea mayor que cero, y cada ubicación registrada se escribe en `ps_contacts`.

En PJSIP el modo DTMF fuera de banda RFC 2833 / RFC 4733 se llama `rfc4733`, y `dtmf_mode=rfc4733` es el valor predeterminado — por lo que la columna `dtmf_mode` arriba es opcional y se muestra solo por claridad.

Paso 3: Intente registrar el nuevo teléfono con un softphone usando el nombre de usuario `6010` y la contraseña `supersecret`. Confirme el registro en la CLI de Asterisk:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Paso 4: Incluya las extensiones en la base de datos.

```
mysql -u astdb -p
```

Ingrese la contraseña:

Use **supersecret** cuando se le solicite, luego inserte la fila de extensión desde el cliente MySQL:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Paso 5: Incluya Asterisk Real Time en el plan de marcación. En el contexto `default`:

```
switch => realtime/test@extensions
```

Recargue las extensiones para activar el cambio.

```
asterisk-server*CLI> extensions reload
```

Paso 6: Reconfigure uno de los teléfonos al nombre de usuario `bria`, si aún no lo ha hecho.

Paso 7: Marque 6007 desde un teléfono existente; el teléfono `bria` debería sonar.

## Resumen

En este capítulo, has aprendido que Asterisk Real Time te permite colocar tus configuraciones en una base de datos. Asterisk incluye controladores nativos de realtime para ODBC (que accede a cualquier base de datos compatible con UnixODBC, incluyendo MySQL/MariaDB y SQLite) y PostgreSQL, además de un controlador LDAP realtime para back‑ends de directorio. MySQL/MariaDB se accede a través de ODBC, como hicimos en este capítulo (también existe un complemento dedicado `res_config_mysql`, pero vive fuera de la compilación central, por lo que ODBC es la ruta común). La configuración se divide en estática y realtime. La configuración estática reemplaza los archivos de configuración, mientras que la configuración realtime crea objetos dinámicos que se cargan solo cuando ocurre una llamada u otro evento relacionado. Concluimos con un laboratorio práctico sobre cómo instalar y configurar ARA.

## Cuestionario

1. Asterisk Realtime es parte de la distribución estándar de Asterisk.
   - A. Verdadero
   - B. Falso
2. Los parámetros de conexión del servidor de base de datos se configuran en el archivo:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. El archivo `extconfig.conf` configura las tablas usadas por Realtime. Tiene dos secciones distintas (marque dos):
   - A. Configuración estática
   - B. Configuración Realtime
   - C. Rutas salientes
   - D. Direcciones IP y puertos de base de datos
4. En la configuración estática, una vez que los objetos se cargan desde la base de datos se mantienen en la memoria de Asterisk y solo se actualizan al iniciar o recargar.
   - A. Verdadero
   - B. Falso
5. PJSIP realtime (Sorcery) soporta completamente `qualify` y MWI para endpoints realtime, porque Sorcery los carga como objetos PJSIP configurados ordinariamente en lugar de descartarlos después de cada llamada como ocurría con los antiguos peers SIP realtime.
   - A. Verdadero
   - B. Falso
6. En PJSIP realtime, ¿qué tablas contienen los endpoints y sus contactos registrados?
   - A. `ps_endpoints` y `ps_contacts`
   - B. `ps_peers` y `ps_registry`
   - C. `ps_config` y `ps_data`
   - D. `extconfig` y `res_odbc`
7. aún puedes usar archivos de configuración de texto incluso después de habilitar ARA.
   - A. Verdadero
   - B. Falso
8. phpMyAdmin es obligatorio cuando usas Realtime.
   - A. Verdadero
   - B. Falso
9. La base de datos debe crearse con cada campo que exista en el archivo de configuración.
   - A. Verdadero
   - B. Falso
10. En Asterisk 22, ¿cuál es la forma recomendada y correcta según la versión para crear las tablas realtime de PJSIP (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`)?
    - A. Escribir manualmente las sentencias `CREATE TABLE` para cada tabla `ps_*`
    - B. Importar el legado `mysql_config.sql` desde `contrib/realtime/`
    - C. Ejecutar las migraciones Alembic `config` bajo `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`)
    - D. Las tablas se crean automáticamente la primera vez que Asterisk se inicia

**Respuestas:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
