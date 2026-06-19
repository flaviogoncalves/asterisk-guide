# Registros de Detalle de Llamadas (CDR) de Asterisk

Asterisk, al igual que otras plataformas de telefonía, permite la facturación de llamadas telefónicas. Existen varios programas en el mercado que pueden importar los registros generados por las PBX. Dichos registros se utilizan para verificar el monto correcto de la factura y obtener estadísticas, entre otras cosas.

## Objetivos

Al finalizar este capítulo, el lector debería ser capaz de:

- Describir dónde y en qué formato se generan los registros
- Generar registros utilizando ODBC (Open Database Connectivity)
- Implementar un esquema de autenticación integrado con la facturación

## Formato de CDR de Asterisk

Asterisk genera un registro de detalle de llamadas (CDR, por sus siglas en inglés) para cada llamada. Estos registros se almacenan, de forma predeterminada, en un archivo de texto con valores separados por comas (CSV) en /var/log/asterisk/cdr-csv. El archivo está organizado en los siguientes campos: CDR Description Type Size Accountcode Account Number to use String Src Caller ID Number String Dst Destination Extension String Dcontext Destination Context String Caller ID with Text String Channel Channel Used String Dstchannel Destination channel String Lastapp Last application String Lastdata Last application data String Start Start of call Date/Time Answer Answer of call Date/Time End End of Call Date/Time Duration Time, from dial to hang up Integer (seconds) Billsec Time, from answer to hang up Integer (seconds) Disposition What Happened to the call String (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags Flags (DEFAULT, OMIT, BILLING, DOCUMENTATION) String User field User defined field String Muestra de un archivo csv importado en una tabla. AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## Códigos de cuenta y contabilidad de mensajes automatizada (AMA)

Puede especificar códigos de cuenta y flags ama en cada canal. Por lo general, esto se hace en el archivo de configuración del canal (por ejemplo, chan_dahdi.conf, pjsip.conf). El parámetro amaflags define qué hacer con el registro CDR. Los valores posibles de amaflag son:

- Default
- Omit
- Billing
- Documentation

De manera similar a cómo un registro puede ser marcado para facturación o documentación, se puede establecer un código de cuenta en cada registro. El código de cuenta es una cadena de texto de formato libre (la opción de endpoint `accountcode` acepta cualquier String, y el registro CDR lo almacena en un campo de 80 caracteres) que generalmente se utiliza para asignar un registro a un departamento o unidad de negocio. Ejemplo: sección de endpoint en pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

El flag AMA no es una opción de endpoint `pjsip.conf` en Asterisk 22; configúrelo por llamada desde el dialplan con la función `CHANNEL` (por ejemplo, `Set(CHANNEL(amaflags)=billing)`), o con `Set(CDR(amaflags)=billing)`.

## Cambio del formato CSV y/o CDR

Puede cambiar el formato CSV modificando el archivo cdr_custom.conf.

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

Puede cambiar el formato del CDR en el archivo cdr_custom.conf.

## Almacenamiento de CDR

El almacenamiento de CDR se puede lograr de varias maneras. La forma más importante son los archivos de texto CSV, que pueden importarse fácilmente a hojas de cálculo. Para pequeñas empresas, esto suele ser suficiente. Algunos programas de facturación aceptan archivos CSV de forma predeterminada. Sin embargo, almacenar los CDR en una base de datos es mucho mejor y más seguro. Asterisk admite varios tipos de bases de datos. Existen algunas interfaces gráficas para facturación en el mercado. Con tantos controladores, ¿cuál elegir?

### Controladores de almacenamiento disponibles

- cdr_csv – Archivos de texto con valores separados por comas
- cdr_adaptive_odbc – Backend de ODBC adaptativo (preferido para almacenamiento en base de datos)
- cdr_odbc – Bases de datos compatibles con unixODBC (legado; se prefiere cdr_adaptive_odbc)
- cdr_pgsql – Bases de datos Postgres
- cdr_mysql – Bases de datos MySQL (**obsoleto**; utilice cdr_adaptive_odbc + controlador ODBC de MySQL en su lugar)
- cdr_freetds – Bases de datos Sybase y MSSQL
- cdr_manager – CDR a la interfaz de gestión (Manager Interface)
- cdr_radius – Interfaz de radio para CDR
- cdr_sqlite3_custom – Módulo de CDR personalizado para SQLite3

El registro de CDR se realiza en todos los módulos activos cargados en el archivo /etc/asterisk/modules.conf. Si el parámetro autoload=yes está configurado, se cargan todos los módulos. Para verificar qué cdr_drivers están cargados actualmente en el sistema, utilice el siguiente comando:

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

Si observa la captura de pantalla anterior, al menos cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc y cdr_sqlite3_custom están en ejecución. En los últimos años, después de algunas Astricon, me quedó claro que el equipo de Asterisk favorecía a ODBC. Es el único controlador que admite agrupación de conexiones (connection pooling). La agrupación de conexiones es una gran ventaja en términos de rendimiento, ya que no es necesario abrir una nueva conexión para cada operación. Este capítulo fue escrito anteriormente utilizando cdr_mysql. He cambiado a cdr_adaptive_odbc para esta edición, aun sabiendo que es un poco más complejo de configurar. La elección de cdr_adaptive_odbc también nos permite personalizar el CDR. Simplemente puede establecer una nueva variable CDR en el dialplan y agregar la columna a la base de datos. Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### Almacenamiento CSV

Como dijimos anteriormente, de forma predeterminada, Asterisk envía todos los CDR a un archivo de texto CSV utilizando el módulo cdr_csv.so. Si no puede ver los archivos en /var/log/asterisk/cdr-csv, verifique si el módulo se está cargando utilizando el comando de CLI module show. Si no está cargado, revise modules.conf. En este capítulo enviaremos los CDR a cdr_csv como respaldo.

### Configuración del archivo modules.conf

Para cargar solo los módulos apropiados, utilice las siguientes líneas en el archivo modules.conf

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Ahora solo tenemos cargados cdr_csv y cdr_adaptive_odbc.

## Instalación y configuración de ODBC en Ubuntu 22.04

> **[Nota de la 2da ed.]** Los pasos originales estaban dirigidos a Ubuntu 18.04 y MySQL Connector/ODBC 8.0.14. Los pasos a continuación están actualizados para Ubuntu 22.04 LTS; ajuste las versiones de los paquetes y las URLs de descarga para que coincidan con la versión actual de MySQL Connector/ODBC desde dev.mysql.com.

Siempre me arrepiento de publicar instrucciones detalladas en el libro. A veces cambian antes de que el libro sea publicado. Las versiones cambian, los módulos cambian, así que intente adaptar el comando aquí a su propia situación. La mayoría de las veces, cambios menores son suficientes para reproducir la instalación. Preste atención a los pasos, incluso los usuarios experimentados de Linux encontrarán difícil instalar los controladores ODBC.

Paso 1 - Instale los paquetes requeridos:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Paso 2 - Cree una base de datos y un usuario:

```
mysql -u root -p
```

(Utilice la contraseña definida cuando creó el servidor mysql) Escriba estos comandos en la línea de comandos de mysql

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Paso 3 - Cree la base de datos

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Paso 4: Descargue el conector ODBC de MySQL desde Oracle. Verifique su sistema operativo usando: `lsb_release -a`. Para Ubuntu 22.04 (x86_64), visite https://dev.mysql.com/downloads/connector/odbc/ y elija la versión actual 8.x o 9.x para Ubuntu 22.04.

> **[Nota de la 2da ed.]** Verifique la URL de descarga exacta y el nombre del archivo en dev.mysql.com; el número de versión y el sufijo de Ubuntu diferirán de la 1ra edición. El ejemplo a continuación utiliza una versión de marcador de posición.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Paso 5: Instale el controlador ODBC

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Paso 6 - Configure el conector ODBC editando el archivo /etc/odbc.ini para crear el DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Paso 7: Pruebe el acceso al controlador usando iSQL. iSQL es una utilidad de línea de comandos para conectarse a la base de datos a través de unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Por favor, no proceda con la configuración de Asterisk si no puede ver el resultado del comando isql.

### Configuración de ODBC en Asterisk

Antes de poder configurar cdr_adaptive_odbc, primero debe configurar el archivo de recursos ODBC.

Paso 1 - Conecte Asterisk a ODBC. Edite el archivo res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Paso 2 – Reinicie Asterisk y pruebe usando

```
CLI>odbc show
```

El resultado se muestra a continuación.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Paso 3 – Configure el controlador ODBC adaptativo en /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Aquí `connection` apunta a la sección de conexión `[cdr]` definida en `res_odbc.conf`, y `table` es la tabla de la base de datos donde se escriben los CDR.

Paso 4 – Recargue el módulo cdr_adaptive_odbc.so:

```
asterisk*CLI>reload cdr_adaptive_odbc
```

Paso 5 – Realice algunas llamadas y verifique si hay nuevos registros en la base de datos. Para verificar la base de datos:

```
mysql –u root –p
>use astdb
>select * from cdr
```

## Aplicaciones y funciones

Varias aplicaciones están relacionadas con la facturación.

### CDR(accountcode)

Establece un código de cuenta antes de llamar a otra aplicación dial(); por ejemplo: Formato:

```
Set(CDR(accountcode)=account)
```

El código de cuenta se puede verificar utilizando la variable de canal ${CDR(accountcode)}

### CDR(amaflags)

Establece un flag para fines de facturación. Las opciones son default, omit, documentation y billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Deshabilita el registro de CDR para el canal actual, por lo que no se escribe ningún CDR en el archivo o base de datos. Configurarlo de nuevo a `0` vuelve a habilitar el registro.

```
Set(CDR_PROP(disable)=1)
```

> **[Nota de la 2da ed.]** El texto original utilizaba la aplicación `NoCDR()`. `NoCDR` fue obsoleta y luego eliminada en Asterisk 21; utilice `Set(CDR_PROP(disable)=1)` en su lugar.

### ResetCDR()

Restablece el registro de datos de llamadas: el tiempo `start` (y, si fue contestada, el tiempo `answer`) se establece en la hora actual y todas las variables CDR se borran. Si se establece la opción `v`, las variables CDR se conservan durante el restablecimiento.

### Set(CDR(userfield)=Value)

Este comando establece un campo de usuario en el CDR. Al usar `cdr_adaptive_odbc`, el campo de usuario se almacena automáticamente si existe una columna `userfield` en la tabla CDR — no se requiere recompilación de la fuente. Para archivos de texto CSV, debe editar el código fuente (cdr_csv.c) y recompilar Asterisk si desea utilizar campos de usuario.

> **[Nota de la 2da ed.]** El texto original hacía referencia a `cdr_addon_mysql` y `cdr_mysql.conf`. El módulo `cdr_mysql` está obsoleto en Asterisk 22; la ruta recomendada es `cdr_adaptive_odbc` con un controlador ODBC de MySQL, que admite campos de usuario de forma nativa a través del mapeo de columnas adaptativo.

### AppendCDRUserField(Value)

Agrega datos al campo de usuario en el CDR.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Autenticación de usuario

Algunas empresas facturan las llamadas a sus empleados. En Asterisk puede establecer un esquema de autenticación que le permite facturar al usuario autenticado en el CDR. Esta autenticación se puede realizar utilizando una contraseña pasada como parámetro a la aplicación Authenticate —un archivo de contraseñas, indicado por una / (barra diagonal) antes del parámetro, o una base de datos de Asterisk (dbput/dbget). Formato:

```
Authenticate(password[|options])
Authenticate(/passwdfile|[|options])
Authenticate(</db-keyfamily|d>options)
```

Opciones:

- a – Establece el código de cuenta como la contraseña.
- d – Interpreta el parámetro como una clave de base de datos de Asterisk
- r – Elimina la clave después de una autenticación exitosa (solo con la opción ´d´)
- j – Salta a la prioridad n+101 para una autenticación no válida

Ejemplo: (Llamadas internacionales)

```
exten=_9011.,1,Authenticate(/password|daj)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

Para insertar la contraseña en una clave de base de datos desde la consola:

```
CLI> database put senha 123456 1
```

## Uso de contraseñas de voicemail

Esta aplicación hace lo mismo que authenticate, pero utiliza el archivo de configuración de voicemail para la contraseña.

```
VMAuthenticate([mailbox][@context][|options])
```

Si se especifica un buzón, solo se considerará válida la contraseña del buzón. Si no se especifica el buzón, se establecerá una variable de canal AUTH_MAILBOX con el buzón autenticado. Si se establece la opción ´s´ (silencioso), no se ejecutará ninguna solicitud. Ejemplo: (Llamadas internacionales)

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local|ajs)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

## Registro de eventos de canal (CEL)

Los registros CDR proporcionan una fila de resumen por llamada. Para un seguimiento de eventos más detallado —como transiciones de estado de canal individuales, eventos de entrada/salida de puente y tramos de transferencia asistida—, Asterisk 22 incluye **Channel Event Logging (CEL)**, configurado a través de `/etc/asterisk/cel.conf` y almacenado a través de backends como `cel_odbc` o `cel_custom`.

CEL complementa al CDR en lugar de reemplazarlo: el CDR sigue siendo el estándar para los resúmenes de facturación, mientras que CEL proporciona datos granulares por evento útiles para la detección de fraudes, monitoreo de calidad e informes avanzados.

> **[Nota de la 2da ed.]** Considere agregar una subsección corta de CEL o una referencia a un capítulo de facturación avanzada si el programa de estudios lo cubre. El patrón de configuración `cel.conf` refleja a `cdr.conf`.

## Resumen

En este capítulo hemos aprendido cómo implementar el registro de CDR en archivos de texto y en una base de datos MySQL. También hemos aprendido cómo establecer amaflags y códigos de cuenta. Al final del capítulo, aprendimos cómo utilizar un esquema de autenticación integrado con CDR y facturación.

## Cuestionario

1. De forma predeterminada, Asterisk registra el CDR en el directorio /var/log/asterisk/cdr-csv.
   - A. Falso
   - B. Verdadero
2. Asterisk puede escribir CDR en (seleccione todas las que correspondan):
   - A. MySQL
   - B. Oracle nativo
   - C. Microsoft SQL Server
   - D. Archivos de texto CSV
   - E. Bases de datos compatibles con unixODBC
3. Asterisk genera un CDR para un solo tipo de almacenamiento a la vez.
   - A. Falso
   - B. Verdadero
4. ¿Qué amaflags de Asterisk están disponibles?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Para asociar un departamento con un CDR, usted utiliza el comando ___, y el código de cuenta se puede leer con la variable de canal ___.
6. La diferencia entre `Set(CDR_PROP(disable)=1)` y `ResetCDR()` es que deshabilitar el CDR evita que se escriba cualquier registro, mientras que `ResetCDR()` restablece (pone a cero) el registro actual. (La aplicación `NoCDR()` que anteriormente deshabilitaba los CDR fue eliminada en Asterisk 21.)
   - A. Falso
   - B. Verdadero
7. Para utilizar un campo definido por el usuario con el módulo `cdr_csv.so`, debe editar el código fuente y recompilar Asterisk.
   - A. Falso
   - B. Verdadero
8. Los tres métodos de autenticación disponibles para la aplicación Authenticate() son:
   - A. Contraseña
   - B. Archivo de contraseñas
   - C. Base de datos de Asterisk (dbput y dbget)
   - D. Voicemail
9. Las contraseñas de voicemail se especifican en una sección separada de `voicemail.conf` y no son las mismas que las de los usuarios de voicemail.
   - A. Falso
   - B. Verdadero
10. El registro de eventos de canal (CEL) reemplaza al CDR en Asterisk 22; una vez que CEL está habilitado, ya no se producen resúmenes de facturación CDR.
    - A. Falso
    - B. Verdadero

**Respuestas:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
