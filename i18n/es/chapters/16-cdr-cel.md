# Registros Detallados de Llamadas de Asterisk

Asterisk, al igual que otras plataformas de telefonía, permite la facturación de llamadas telefónicas. Varios programas en el mercado pueden importar los registros generados por los PBX. Esos registros se utilizan para verificar el monto correcto de la factura y las estadísticas, entre otras cosas.

## Objectives

Al final de este capítulo, el lector debería ser capaz de:

- Describir dónde y en qué formato se generan los registros
- Generar registros usando ODBC (Open Database Connectivity)
- Implementar un esquema de autenticación integrado con facturación

## Formato CDR de Asterisk

Asterisk genera un registro de detalle de llamada (CDR) para cada llamada. Estos registros se almacenan, por defecto, en un archivo de texto en formato de valores separados por comas (CSV) en **/var/log/asterisk/cdr-csv**. El archivo está organizado en los siguientes campos:

| Campo | Descripción | Tipo |
|-------|-------------|------|
| Accountcode | Número de cuenta a usar | String |
| Src | Número de identificación del llamante | String |
| Dst | Extensión de destino | String |
| Dcontext | Contexto de destino | String |
| Clid | Identificación del llamante con texto | String |
| Channel | Canal usado | String |
| Dstchannel | Canal de destino | String |
| Lastapp | Última aplicación | String |
| Lastdata | Datos de la última aplicación | String |
| Start | Inicio de la llamada | Date/Time |
| Answer | Respuesta de la llamada | Date/Time |
| End | Fin de la llamada | Date/Time |
| Duration | Tiempo, desde marcar hasta colgar | Integer (seconds) |
| Billsec | Tiempo, desde contestar hasta colgar | Integer (seconds) |
| Disposition | Qué ocurrió con la llamada (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | Banderas (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | Campo definido por el usuario | String |

Ejemplo de un archivo CSV. Cada línea es un registro; los campos aparecen en el mismo
orden que la tabla anterior (`accountcode` primero, `amaflags` último):

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## Códigos de cuenta y contabilización automática de mensajes

Puede especificar códigos de cuenta y banderas ama en cada canal. Por lo general, esto se hace en el archivo de configuración del canal (p. ej., chan_dahdi.conf, pjsip.conf). El parámetro amaflags define qué hacer con el registro CDR. Los valores posibles de amaflag son:

- Default
- Omit
- Billing
- Documentation

De forma similar a cómo un registro puede marcarse para facturación o documentación, se puede establecer un código de cuenta en cada registro. El código de cuenta es una cadena de texto libre (la opción de endpoint `accountcode` acepta cualquier String, y el registro CDR lo almacena en un campo de 80 caracteres) que normalmente se usa para asignar un registro a un departamento o unidad de negocio. Ejemplo: sección de endpoint en pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

La bandera AMA no es una opción de endpoint `pjsip.conf` en Asterisk 22; configúrela por llamada desde el dialplan con la función `CHANNEL` (por ejemplo `Set(CHANNEL(amaflags)=billing)`), o con `Set(CDR(amaflags)=billing)`.

## Cambiar el formato CSV y/o CDR

Puedes cambiar el formato CSV modificando el archivo cdr_custom.conf.

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

Puedes cambiar el formato CDR en el archivo cdr_custom.conf.

## Almacenamiento de CDR

El almacenamiento de CDR puede lograrse de varias maneras. La forma más importante es mediante archivos de texto CSV que pueden importarse fácilmente a hojas de cálculo. Para pequeñas empresas, esto suele ser suficiente. Algunos programas de facturación aceptan, por defecto, archivos CSV. Sin embargo, almacenar los CDR en una base de datos es mucho mejor y más seguro. Asterisk soporta varios sabores de bases de datos. Existen algunas interfaces gráficas para facturación en el mercado. Con tantos controladores, ¿cuál elegir?

### Controladores de almacenamiento disponibles

- cdr_csv – Archivos de texto de valores separados por comas
- cdr_custom – Archivos de texto de valores separados por comas personalizables
- cdr_adaptive_odbc – Backend ODBC adaptativo (preferido para almacenamiento en base de datos)
- cdr_odbc – Bases de datos soportadas por unixODBC (legado; se prefiere cdr_adaptive_odbc)
- cdr_pgsql – Bases de datos Postgres
- cdr_tds (cdr_freetds) – Bases de datos Sybase y MSSQL vía FreeTDS
- cdr_manager – CDR a la Interfaz de Manager
- cdr_radius – Interfaz de CDR radius
- cdr_sqlite3_custom – Módulo CDR personalizado para SQLite3

El `cdr_addon_mysql` (cdr_mysql) módulo que las guías más antiguas recomendaban fue eliminado en Asterisk 19, por lo que no existe un controlador nativo de MySQL CDR en Asterisk 22. Para escribir CDR en MySQL/MariaDB, use `cdr_adaptive_odbc` junto con un controlador MySQL ODBC — el enfoque usado en este capítulo.

La grabación de CDR se realiza en todos los módulos activos cargados en el archivo /etc/asterisk/modules.conf. Si el parámetro autoload=yes está configurado, se cargan todos los módulos. Para comprobar qué cdr_drivers están actualmente cargados en el sistema, use el siguiente comando:

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

Si ve la captura de pantalla anterior, al menos cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc y cdr_sqlite3_custom están en ejecución. En los últimos años, después de algunos astricons, quedó claro para mí que el equipo de Asterisk estaba favoreciendo ODBC. Es el único controlador que soporta agrupamiento de conexiones. El agrupamiento de conexiones es una gran ventaja en términos de rendimiento porque no tiene que abrir una nueva conexión para cada operación. Este capítulo se escribió previamente usando cdr_mysql. He pasado a cdr_adaptive_odbc para esta edición aun sabiendo que es un poco más complejo de configurar. La elección de cdr_adaptive_odbc también nos permite personalizar el CDR. Puede simplemente establecer una nueva variable CDR en el dialplan y añadir la columna correspondiente a la base de datos. Por ejemplo, para registrar el jitter de audio:

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### Almacenamiento CSV

Como dijimos antes, por defecto, Asterisk envía todos los CDR a un archivo de texto CSV usando el módulo cdr_csv.so. Si no puede ver los archivos en /var/log/asterisk/cdr-csv, verifique si el módulo se está cargando usando el comando CLI module show. Si no está cargado, revise modules.conf. En este capítulo enviaremos los CDR a cdr_csv como respaldo.

### Configuración del archivo modules.conf

Para cargar solo los módulos apropiados, use las líneas siguientes en el archivo modules.conf

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Ahora solo tenemos cdr_csv y cdr_adaptive_odbc cargados.

## Instalación y configuración de ODBC en Ubuntu 22.04

Siempre lamento publicar instrucciones detalladas en el libro. A veces cambian antes de que el libro sea publicado. Las versiones cambian, los módulos cambian, así que intenta adaptar el comando aquí a tu propia situación. La mayoría de las veces bastan cambios menores para reproducir la instalación. Presta atención a los pasos que incluso usuarios experimentados de Linux encontrarán difíciles para instalar los controladores ODBC.

Paso 1 - Instala los paquetes requeridos:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Paso 2 - Crea una base de datos y un usuario:

```
mysql -u root -p
```

(Usa la contraseña definida cuando creaste el servidor mysql) Escribe estos comandos en la línea de comandos de mysql

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Paso 3 - Crea la base de datos

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Paso 4: Descarga el conector MySQL ODBC de Oracle. Verifica tu sistema operativo usando: `lsb_release -a`. Para Ubuntu 22.04 (x86_64), visita https://dev.mysql.com/downloads/connector/odbc/ y elige la versión actual 8.x o 9.x para Ubuntu 22.04. El nombre exacto del archivo y el número de versión cambian con el tiempo, así que establece `VER` (abajo) al nombre que tenga la compilación actual de Linux glibc.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Paso 5: Instala el controlador ODBC

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Paso 6 - Configura el conector ODBC editando el archivo /etc/odbc.ini para crear el DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Paso 7: Prueba el acceso al controlador usando iSQL. iSQL es una utilidad de línea de comandos para conectar a la base de datos a través de unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Por favor, no continúes con la configuración de Asterisk si no puedes ver el resultado del comando isql.

### Configuración de ODBC en Asterisk

Antes de poder configurar cdr_adaptive_odbc, debes primero configurar el archivo de recursos ODBC.

Paso 1 - Conecta Asterisk a ODBC. Edita el archivo res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Paso 2 – Reinicia Asterisk y prueba usando

```
asterisk*CLI> odbc show
```

La salida se muestra a continuación.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Paso 3 – Configura el controlador ODBC adaptativo en /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Aquí `connection` apunta a la sección de conexión `[cdr]` definida en `res_odbc.conf`, y `table` es la tabla de base de datos donde se escriben los CDR.

Paso 4 – Recarga el módulo cdr_adaptive_odbc.so:

```
asterisk*CLI> reload cdr_adaptive_odbc
```

Paso 5 – Realiza las mismas llamadas y verifica la base de datos en busca de nuevos registros. Para verificar la base de datos:

```
mysql -u root -p
>use astdb
>select * from cdr;
```

## Aplicaciones y funciones

Varias aplicaciones están relacionadas con la facturación.

### CDR(accountcode)

Establece un código de cuenta antes de llamar a otra aplicación dial(); por ejemplo: Formato:

```
Set(CDR(accountcode)=account)
```

El código de cuenta puede verificarse usando la variable de canal ${CDR(accountcode)}

### CDR(amaflags)

Establece una bandera para propósitos de facturación. Las opciones son default, omit, documentation y billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Desactiva el registro de CDR para el canal actual, de modo que no se escribe ningún CDR en el archivo o base de datos. Restablecerlo a `0` vuelve a habilitar el registro.

```
Set(CDR_PROP(disable)=1)
```

La aplicación `NoCDR()` que usaban ediciones anteriores para esto fue eliminada en Asterisk 21; en Asterisk 22 se desactiva el CDR de un canal con `Set(CDR_PROP(disable)=1)` en su lugar.

### ResetCDR()

Restablece el Call Data Record: el tiempo `start` (y, si se respondió, el tiempo `answer`) se fija al tiempo actual y todas las variables de CDR se borran. Si la opción `v` está establecida, las variables de CDR se conservan durante el restablecimiento.

### Set(CDR(userfield)=Value)

Este comando establece un campo de usuario en el CDR. Al usar `cdr_adaptive_odbc`, el campo de usuario se almacena automáticamente si existe una columna `userfield` en la tabla CDR — no se necesita recompilación de la fuente. Para archivos de texto CSV, debe editar el código fuente (cdr_csv.c) y recompilar Asterisk si desea usar campos de usuario.

Ediciones anteriores almacenaban los CDR en MySQL con el módulo `cdr_addon_mysql` (`cdr_mysql.conf`). Ese módulo fue eliminado en Asterisk 19, por lo que no está disponible en Asterisk 22. La ruta compatible ahora es `cdr_adaptive_odbc` con un controlador MySQL ODBC, que almacena el campo de usuario — y cualquier otra columna personalizada — de forma nativa mediante su mapeo adaptativo de columnas.

### Añadiendo al campo de usuario

Ediciones anteriores usaban la aplicación `AppendCDRUserField()` para añadir datos al campo de usuario del CDR. Esa aplicación fue eliminada de Asterisk; en Asterisk 22 se añade al campo de usuario leyendo y volviendo a establecerlo con la función `CDR`, por ejemplo `Set(CDR(userfield)=${CDR(userfield)}extra)`.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Autenticación de usuarios

Algunas empresas facturan las llamadas a sus empleados. En Asterisk puedes establecer un esquema de autenticación que permite facturar al usuario autenticado en el CDR. Esta autenticación puede realizarse usando una contraseña pasada como parámetro a la aplicación Authenticate—un archivo de contraseñas, indicado por una / (barra) antes del parámetro, o una clave de la base de datos de Asterisk (usando la opción `d`). Formato:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

Opciones:

- a – Establece el código de cuenta del canal a la contraseña ingresada.  
- d – Interpreta la ruta dada como una clave de la base de datos de Asterisk en lugar de un archivo literal.  
- m – Interpreta la ruta como un archivo de líneas `accountcode:passwordhash`.  
- r – Elimina la clave de la base de datos después de una autenticación exitosa (válido solo con `d`).

Si el llamante falla los tres intentos, el canal se cuelga; la ejecución del dialplan no continúa, por lo que debes manejar la ruta de falla en la línea después de `Authenticate()`. Ejemplo (Llamadas internacionales):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

La opción `j` (saltar a la prioridad n+101 en caso de falla) y la convención de prioridad `+101` fueron eliminadas de Asterisk hace tiempo; un `Authenticate()` fallido simplemente cuelga.

Para insertar la contraseña en una clave de base de datos desde la consola:

```
asterisk*CLI> database put senha 123456 1
```

## Uso de contraseñas del buzón de voz

Esta aplicación hace lo mismo que authenticate, pero usa el archivo de configuración del buzón de voz para la contraseña.

```
VMAuthenticate([mailbox][@context][,options])
```

Si se especifica un buzón, solo la contraseña de ese buzón se considerará válida. Si no se especifica el buzón, la variable de canal `${AUTH_MAILBOX}` se establecerá con el buzón autenticado. Si la opción `s` está activada, se omiten los avisos iniciales. Ejemplo (Llamadas internacionales):

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Registro de Eventos de Canal (CEL)

Los registros CDR proporcionan una fila de resumen por llamada. Para un seguimiento de eventos más detallado — como transiciones de estado de canal individuales, eventos de entrada/salida de puentes y tramos de transferencia asistida — Asterisk 22 incluye **Channel Event Logging (CEL)**, configurado mediante `/etc/asterisk/cel.conf` y almacenado a través de backends como `cel_odbc` o `cel_custom`.

CEL complementa a CDR en lugar de reemplazarlo: CDR sigue siendo el estándar para resúmenes de facturación, mientras que CEL brinda datos granulares por evento útiles para la detección de fraudes, el monitoreo de calidad y la generación de informes avanzados.

El patrón de configuración `cel.conf` refleja `cdr.conf`: habilita los tipos de eventos que deseas en la sección `[general]` de `cel.conf`, luego configura cada backend de almacenamiento en su propio archivo — `cel_custom.conf` para CSV, `cel_odbc.conf` para una base de datos ODBC (la misma conexión `res_odbc.conf` utilizada para los CDR). Puedes confirmar si CEL está activo con `cel show status` en la CLI.

## Resumen

En este capítulo hemos aprendido cómo implementar el registro de CDR en archivos de texto y en una base de datos MySQL. También hemos aprendido cómo establecer amaflags y códigos de cuenta. Al final del capítulo, aprendimos cómo usar un esquema de autenticación integrado con CDR y facturación.

## Quiz

1. Por defecto, Asterisk registra el CDR en el directorio /var/log/asterisk/cdr-csv.
   - A. False
   - B. True
2. Asterisk puede escribir CDRs a (seleccione todas las que correspondan):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. archivos de texto CSV
   - E. bases de datos compatibles con unixODBC
3. Asterisk genera un CDR solo para un tipo de almacenamiento a la vez.
   - A. False
   - B. True
4. ¿Qué amaflags de Asterisk están disponibles?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Para asociar un departamento con un CDR usa el comando ___, y el código de cuenta puede leerse con la variable de canal ___.
6. La diferencia entre `Set(CDR_PROP(disable)=1)` y `ResetCDR()` es que desactivar el CDR impide que se escriba cualquier registro, mientras que `ResetCDR()` restablece (pone a cero) el registro actual. (La aplicación `NoCDR()` que previamente desactivaba los CDR fue eliminada en Asterisk 21.)
   - A. False
   - B. True
7. Para usar un campo definido por el usuario con el módulo `cdr_csv.so`, debes editar el código fuente y recompilar Asterisk.
   - A. False
   - B. True
8. Los tres métodos de autenticación disponibles para la aplicación Authenticate() son:
   - A. Password
   - B. Password file
   - C. Asterisk DB (dbput and dbget)
   - D. Voicemail
9. Las contraseñas de voicemail se especifican en una sección separada de `voicemail.conf` y no son las mismas que los usuarios de voicemail.
   - A. False
   - B. True
10. Channel Event Logging (CEL) reemplaza al CDR en Asterisk 22 — una vez que CEL está habilitado, ya no se generan resúmenes de facturación de CDR.
    - A. False
    - B. True

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
