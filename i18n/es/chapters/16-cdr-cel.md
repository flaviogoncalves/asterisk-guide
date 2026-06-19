# Registros de Detalle de Llamadas (CDR) de Asterisk

Asterisk, al igual que otras plataformas de telefonía, permite la facturación de llamadas telefónicas. Existen varios programas en el mercado que pueden importar los registros generados por las PBX. Dichos registros se utilizan para verificar el monto correcto de la factura y obtener estadísticas, entre otras cosas.

## Objetivos

Al finalizar este capítulo, el lector debería ser capaz de:

- Describir dónde y en qué formato se generan los registros
- Generar registros utilizando ODBC (Open Database Connectivity)
- Implementar un esquema de autenticación integrado con la facturación

## Formato de CDR de Asterisk

Asterisk genera un registro de detalle de llamadas (CDR) por cada llamada. Estos registros se almacenan, de forma predeterminada, en un archivo de texto con valores separados por comas (CSV) en /var/log/asterisk/cdr-csv. El archivo está organizado en los siguientes campos: CDR Descripción Tipo Tamaño Accountcode Número de cuenta a utilizar String Src Número de identificación del llamante (Caller ID) String Dst Extensión de destino String Dcontext Contexto de destino String Caller ID with Text Caller ID con texto String Channel Canal utilizado String Dstchannel Canal de destino String Lastapp Última aplicación String Lastdata Datos de la última aplicación String Start Inicio de la llamada Fecha/Hora Answer Respuesta de la llamada Fecha/Hora End Fin de la llamada Fecha/Hora Duration Tiempo, desde la marcación hasta colgar Entero (segundos) Billsec Tiempo, desde la respuesta hasta colgar Entero (segundos) Disposition Qué sucedió con la llamada String (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags Indicadores (DEFAULT, OMIT, BILLING, DOCUMENTATION) String User field Campo definido por el usuario String Ejemplo de archivo csv importado en una tabla. AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## Códigos de cuenta y contabilidad automatizada de mensajes (AMA)

Puede especificar códigos de cuenta e indicadores ama en cada canal. Por lo general, esto se hace en el archivo de configuración del canal (por ejemplo, chan_dahdi.conf, pjsip.conf). El parámetro amaflags define qué hacer con el registro CDR. Los valores posibles de amaflag son:

- Default
- Omit
- Billing
- Documentation

De manera similar a cómo se puede marcar un registro para facturación o documentación, se puede establecer un código de cuenta en cada registro. El código de cuenta es una cadena de texto de formato libre (la opción de endpoint `accountcode` acepta cualquier String, y el registro CDR lo almacena en un campo de 80 caracteres) que se utiliza habitualmente para asignar un registro a un departamento o unidad de negocio. Ejemplo: sección de endpoint en pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

El indicador AMA no es una opción de endpoint `pjsip.conf` en Asterisk 22; configúrelo por llamada desde el dialplan con la función `CHANNEL` (por ejemplo, `Set(CHANNEL(amaflags)=billing)`), o con `Set(CDR(amaflags)=billing)`.

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

Puede cambiar el formato CDR en el archivo cdr_custom.conf.

## Almacenamiento de CDR

El almacenamiento de CDR se puede lograr de varias maneras. La forma más importante son los archivos de texto CSV, que pueden importarse fácilmente a hojas de cálculo. Para pequeñas empresas, esto suele ser suficiente. Algunos programas de facturación aceptan archivos CSV de forma predeterminada. Sin embargo, almacenar los CDR en una base de datos es mucho mejor y más seguro. Asterisk admite varios tipos de bases de datos. Existen algunas interfaces gráficas para facturación en el mercado. Con tantos controladores, ¿cuál elegir?

### Controladores de almacenamiento disponibles

- cdr_csv – Archivos de texto con valores separados por comas
- cdr_custom – Archivos de texto personalizables con valores separados por comas
- cdr_adaptive_odbc – Backend de ODBC adaptativo (preferido para almacenamiento en base de datos)
- cdr_odbc – Bases de datos compatibles con unixODBC (legado; se prefiere cdr_adaptive_odbc)
- cdr_pgsql – Bases de datos Postgres
- cdr_tds (cdr_freetds) – Bases de datos Sybase y MSSQL a través de FreeTDS
- cdr_manager – CDR hacia la interfaz de gestión (Manager Interface)
- cdr_radius – Interfaz RADIUS para CDR
- cdr_sqlite3_custom – Módulo de CDR personalizado para SQLite3

El módulo `cdr_addon_mysql` (cdr_mysql) que recomendaban las guías antiguas fue eliminado en Asterisk 19, por lo que no existe un controlador CDR nativo para MySQL en Asterisk 22. Para escribir CDR en MySQL/MariaDB, utilice `cdr_adaptive_odbc` junto con un controlador ODBC de MySQL: el enfoque utilizado en este capítulo.

La grabación de CDR se realiza en todos los módulos activos cargados en el archivo /etc/asterisk/modules.conf. Si el parámetro autoload=yes está configurado, se cargan todos los módulos. Para verificar qué cdr_drivers están cargados actualmente en el sistema, utilice el siguiente comando:

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

Si ve la captura de pantalla anterior, al menos cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc y cdr_sqlite3_custom están ejecutándose. En los últimos años, después de algunas AstriCon, me quedó claro que el equipo de Asterisk favorecía ODBC. Es el único controlador que admite agrupación de conexiones (connection pooling). La agrupación de conexiones es una gran ventaja en términos de rendimiento, ya que no es necesario abrir una nueva conexión para cada operación. Este capítulo fue escrito anteriormente utilizando cdr_mysql. He cambiado a cdr_adaptive_odbc para esta edición, aun sabiendo que es un poco más complejo de configurar. La elección de cdr_adaptive_odbc también nos permite personalizar el CDR. Simplemente puede establecer una nueva variable CDR en el dialplan y agregar la columna a la base de datos. Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### Almacenamiento CSV

Como dijimos anteriormente, de forma predeterminada, Asterisk envía todos los CDR a un archivo de texto CSV utilizando el módulo cdr_csv.so. Si no puede ver los archivos en /var/log/asterisk/cdr-csv, verifique si el módulo se está cargando usando el comando de CLI module show. Si no está cargado, revise modules.conf. En este capítulo enviaremos los CDR a cdr_csv como respaldo.

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

Siempre me arrepiento de publicar instrucciones detalladas en el libro. A veces cambian antes de que el libro sea publicado. Las versiones cambian, los módulos cambian, así que intente adaptar el comando aquí a su propia situación. La mayoría de las veces, cambios menores son suficientes para reproducir la instalación. Preste atención a los pasos, incluso los usuarios experimentados de Linux encontrarán difícil instalar los controladores ODBC.

Paso 1 - Instalar los paquetes requeridos:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Paso 2 - Crear una base de datos y un usuario:

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

Paso 3 - Crear la base de datos

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Paso 4: Descargue el conector ODBC de MySQL desde Oracle. Verifique su sistema operativo usando: `lsb_release -a`. Para Ubuntu 22.04 (x86_64), visite https://dev.mysql.com/downloads/connector/odbc/ y elija la versión actual 8.x o 9.x para Ubuntu 22.04. El nombre exacto del archivo y el número de versión cambian con el tiempo, así que establezca `VER` (abajo) a lo que sea que se llame la compilación actual de glibc para Linux.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Paso 5: Instalar el controlador ODBC

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Paso 6 - Configurar el conector ODBC editando el archivo /etc/odbc.ini para crear el DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Paso 7: Probar el acceso al controlador usando iSQL. iSQL es una utilidad de línea de comandos para conectarse a la base de datos a través de unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Por favor, no proceda con la configuración de Asterisk si no puede ver el resultado del comando isql.

### Configuración de ODBC en Asterisk

Antes de poder configurar cdr_adaptive_odbc, primero debe configurar el archivo de recursos ODBC.

Paso 1 - Conectar Asterisk a ODBC. Edite el archivo res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Paso 2 – Reiniciar Asterisk y probar usando

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

Paso 3 – Configurar el controlador ODBC adaptativo en /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Aquí `connection` apunta a la sección de conexión `[cdr]` definida en `res_odbc.conf`, y `table` es la tabla de la base de datos donde se escriben los CDR.

Paso 4 – Recargar el módulo cdr_adaptive_odbc.so:

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

El código de cuenta se puede verificar usando la variable de canal ${CDR(accountcode)}

### CDR(amaflags)

Establece un indicador para fines de facturación. Las opciones son default, omit, documentation y billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Deshabilita la grabación de CDR para el canal actual, por lo que no se escribe ningún CDR en el archivo o base de datos. Establecerlo de nuevo a `0` vuelve a habilitar la grabación.

```
Set(CDR_PROP(disable)=1)
```

La aplicación `NoCDR()` que las ediciones anteriores utilizaban para esto fue eliminada en Asterisk 21; en Asterisk 22, usted deshabilita el CDR de un canal con `Set(CDR_PROP(disable)=1)` en su lugar.

### ResetCDR()

Restablece el registro de datos de llamadas (Call Data Record): el tiempo `start` (y, si fue contestada, el tiempo `answer`) se establece en la hora actual y todas las variables CDR se borran. Si se establece la opción `v`, las variables CDR se conservan durante el restablecimiento.

### Set(CDR(userfield)=Value)

Este comando establece un campo de usuario en el CDR. Al usar `cdr_adaptive_odbc`, el campo de usuario se almacena automáticamente si existe una columna `userfield` en la tabla CDR; no se necesita recompilación del código fuente. Para archivos de texto CSV, debe editar el código fuente (cdr_csv.c) y recompilar Asterisk si desea utilizar campos de usuario.

Las ediciones anteriores almacenaban los CDR en MySQL con el módulo `cdr_addon_mysql` (`cdr_mysql.conf`). Ese módulo fue eliminado en Asterisk 19, por lo que no está disponible en Asterisk 22. La ruta admitida ahora es `cdr_adaptive_odbc` con un controlador ODBC de MySQL, que almacena el campo de usuario —y cualquier otra columna personalizada— de forma nativa a través de su mapeo de columnas adaptativo.

### AppendCDRUserField(Value)

Agrega datos al campo de usuario en el CDR.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Autenticación de usuario

Algunas empresas facturan las llamadas a sus empleados. En Asterisk puede establecer un esquema de autenticación que le permite facturar al usuario autenticado en el CDR. Esta autenticación se puede realizar utilizando una contraseña pasada como parámetro a la aplicación Authenticate: un archivo de contraseñas, indicado por una / (barra diagonal) antes del parámetro, o una clave de base de datos de Asterisk (usando la opción `d`). Formato:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

Opciones:

- a – Establece el código de cuenta del canal a la contraseña ingresada.
- d – Interpreta la ruta dada como una clave de Asterisk DB en lugar de un archivo literal.
- m – Interpreta la ruta como un archivo de líneas `accountcode:passwordhash`.
- r – Elimina la clave de la base de datos después de una autenticación exitosa (válido solo con `d`).

Si el llamante falla los tres intentos, el canal se cuelga; la ejecución del dialplan no continúa, así que maneje la ruta de error en la línea después de `Authenticate()`. Ejemplo (Llamadas internacionales):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

La antigua opción `j` (saltar a la prioridad n+101 en caso de error) y la convención de prioridad `+101` fueron eliminadas de Asterisk hace mucho tiempo; un `Authenticate()` fallido simplemente cuelga.

Para insertar la contraseña en una clave de DB desde la consola:

```
CLI> database put senha 123456 1
```

## Uso de contraseñas de correo de voz (voicemail)

Esta aplicación hace lo mismo que authenticate, pero utiliza el archivo de configuración de correo de voz para la contraseña.

```
VMAuthenticate([mailbox][@context][,options])
```

Si se especifica un buzón, solo se considerará válida la contraseña de ese buzón. Si no se especifica el buzón, la variable de canal `${AUTH_MAILBOX}` se establecerá con el buzón autenticado. Si se establece la opción `s`, se omiten los avisos iniciales. Ejemplo (Llamadas internacionales):

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Registro de eventos de canal (CEL)

Los registros CDR proporcionan una fila de resumen por llamada. Para un seguimiento de eventos más detallado —como transiciones de estado de canal individuales, eventos de entrada/salida de puente y tramos de transferencia atendida— Asterisk 22 incluye **Channel Event Logging (CEL)**, configurado a través de `/etc/asterisk/cel.conf` y almacenado a través de backends como `cel_odbc` o `cel_custom`.

CEL complementa al CDR en lugar de reemplazarlo: el CDR sigue siendo el estándar para los resúmenes de facturación, mientras que CEL proporciona datos granulares por evento útiles para la detección de fraudes, monitoreo de calidad e informes avanzados.

El patrón de configuración `cel.conf` refleja a `cdr.conf`: usted habilita los tipos de eventos que desea en la sección `[general]` de `cel.conf`, luego configura cada backend de almacenamiento en su propio archivo — `cel_custom.conf` para CSV, `cel_odbc.conf` para una base de datos ODBC (la misma conexión `res_odbc.conf` utilizada para los CDR). Puede confirmar si CEL está activo con `cel show status` en la CLI.

## Resumen

En este capítulo hemos aprendido cómo implementar la grabación de CDR en archivos de texto y en una base de datos MySQL. También hemos aprendido cómo establecer amaflags y códigos de cuenta. Al final del capítulo, aprendimos cómo utilizar un esquema de autenticación integrado con CDR y facturación.

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
5. Para asociar un departamento con un CDR, utiliza el comando ___, y el código de cuenta se puede leer con la variable de canal ___.
6. La diferencia entre `Set(CDR_PROP(disable)=1)` y `ResetCDR()` es que deshabilitar el CDR evita que se escriba cualquier registro, mientras que `ResetCDR()` restablece (pone a cero) el registro actual. (La aplicación `NoCDR()` que deshabilitaba previamente los CDR fue eliminada en Asterisk 21.)
   - A. Falso
   - B. Verdadero
7. Para utilizar un campo definido por el usuario con el módulo `cdr_csv.so`, debe editar el código fuente y recompilar Asterisk.
   - A. Falso
   - B. Verdadero
8. Los tres métodos de autenticación disponibles para la aplicación Authenticate() son:
   - A. Contraseña
   - B. Archivo de contraseñas
   - C. Asterisk DB (dbput y dbget)
   - D. Correo de voz (voicemail)
9. Las contraseñas de correo de voz se especifican en una sección separada de `voicemail.conf` y no son las mismas que las de los usuarios de correo de voz.
   - A. Falso
   - B. Verdadero
10. Channel Event Logging (CEL) reemplaza al CDR en Asterisk 22; una vez que CEL está habilitado, ya no se producen resúmenes de facturación CDR.
    - A. Falso
    - B. Verdadero

**Respuestas:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
