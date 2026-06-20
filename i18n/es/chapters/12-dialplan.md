# Funciones avanzadas del plan de marcación

El capítulo 3 trató los conceptos básicos de un plan de marcación. Por razones didácticas, no explicamos todas las funciones, sino solo algunas de las más importantes. Este capítulo profundizará más en el plan de marcación, describiendo técnicas avanzadas, nuevas aplicaciones y conceptos.

## Objetivos

Al final de este capítulo, deberías ser capaz de:

- Simplificar sus entradas de extensión
- Abordar la seguridad del plan de marcación y filtrar extensiones
- Recibir llamadas usando un menú IVR
- Usar subrutinas para evitar reescrituras innecesarias
- Implementar algo de seguridad del plan de marcación usando “Include”
- Implementar follow-me usando AsteriskDB
- Implementar comportamiento fuera de horario en su PBX
- Usar el comando switch para transferir a otro PBX
- Implementar el gestor de privacidad
- Implementar buzón de voz
- Implementar un directorio corporativo

## Simplificando su plan de marcación

Puede simplificar su plan de marcación usando la palabra clave “same” para definir una extensión. Debería reducir la cantidad de errores tipográficos en el plan de marcación. Revise el ejemplo a continuación:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Seguridad del Plan de Marcado

Se descubrió una vulnerabilidad en el plan de marcado de Asterisk que permite a un usuario inyectar un nuevo canal y número de marcado en su plan de marcado. Supongamos que tiene la siguiente línea en su servidor `exten=>_X.,1,Dial(PJSIP/${EXTEN})` y algún usuario malintencionado marcó el número `3000&DAHDI/1/011551123456789` en el softphone. El protocolo SIP, por defecto, acepta cualquier carácter alfanumérico, por lo que la extensión marcada en realidad activará dos llamadas: una para el canal PJSIP/3000 y otra para el canal DAHDI/011551123456789, que es un número internacional. Así, cualquier usuario con acceso a una extensión puede marcar a cualquier parte del mundo. La forma más sencilla de evitar este comportamiento es filtrar los números antes de llamar a la aplicación dial. La función FILTER() es muy útil para esto. Ejemplo:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

La aplicación filter le permitirá filtrar todos los caracteres del número marcado excepto los números del 0 al 9. Puede encontrar más información en el archivo README‑SERIOUSLY.bestpractices.txt disponible en Asterisk.

## Recibiendo llamadas usando un menú IVR.

En la sección anterior, recibiste todas las llamadas usando DID o reenviándolas al operador. Ahora aprenderás cómo implementar un menú IVR así como crear un servicio de auto‑atención. Antes de entrar en los detalles, examinemos algunas aplicaciones nuevas. Colocamos la salida del comando `core show application` a continuación simplemente para facilitar la lectura. Puedes obtener estas descripciones tú mismo usando `core show application <application_name>`.

### La aplicación Background()

Esta aplicación reproducirá la lista de archivos indicada mientras espera a que el canal llamante marque una extensión. Para seguir esperando dígitos después de que esta aplicación haya terminado de reproducir los archivos, debe usarse la aplicación **WaitExten**. La opción **langoverride** especifica explícitamente qué idioma intentar usar para los archivos de sonido solicitados. Cualquier contexto que se indique será el contexto del dialplan que esta aplicación utiliza al salir hacia una extensión marcada. Si uno de los archivos de sonido solicitados no existe, el procesamiento de la llamada se terminará. Opciones:

- s - Hace que la reproducción del mensaje se omita si el canal no está en el estado 'up' (es decir, aún no ha sido contestado). Si esto ocurre, la aplicación retornará inmediatamente.  
- n - No contestar el canal antes de reproducir los archivos.  
- m - Sólo interrumpe si el dígito pulsado coincide con una extensión de un dígito en el contexto de destino.

### La aplicación Record()

Esta aplicación graba desde el canal en un nombre de archivo dado. Si el archivo ya existe, será sobrescrito.

![10-dialplan-advanced-features figura 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' es el formato del tipo de archivo a grabar (wav, gsm, etc).
- 'silence' es la cantidad de segundos de silencio permitidos antes de devolver.
- 'maxduration' es la duración máxima de la grabación en segundos; si falta o es cero, no hay máximo.
- 'options' puede contener cualquiera de las siguientes letras:
    - `a` — agrega a una grabación existente en lugar de reemplazarla
    - `n` — no contestar, pero grabar de todos modos si la línea aún no ha sido contestada
    - `q` — silencioso (no reproducir tono de beep)
    - `s` — omite la grabación si la línea aún no ha sido contestada
    - `t` — usa la tecla terminadora alterna `*` (DTMF) en lugar de la predeterminada `#`
    - `x` — ignora todas las teclas terminadoras (DTMF) y continúa grabando hasta colgar.

Si el nombre de archivo contiene %d, esos caracteres se reemplazarán con un número incrementado en uno cada vez que se grabe el archivo. Use core show file formats para ver los formatos disponibles en su sistema. El usuario puede presionar # para terminar la grabación y continuar con la siguiente prioridad. Si el usuario cuelga durante una grabación, se perderán todos los datos y la aplicación terminará.

### La aplicación Playback()

Esta aplicación reproduce los nombres de archivo dados (no incluya la extensión). También se pueden incluir opciones después de un símbolo de barra vertical. La opción 'skip' hace que la reproducción del mensaje se omita si el canal no está en estado 'up' (es decir, aún no ha sido contestado).

![10-dialplan-advanced-features figura 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figura 3](../images/10-dialplan-advanced-features-img03.png)

Si se especifica `skip`, la aplicación devolverá inmediatamente si el canal no está levantado. De lo contrario, a menos que se especifique `noanswer`, el canal será contestado antes de reproducir el sonido. No todos los canales admiten reproducir mensajes mientras siguen colgados. Si se especifica `j`, la aplicación saltará a la prioridad n+101 cuando el archivo no exista, si está presente. Esta aplicación establece la siguiente variable de canal al completarse:

- PLAYBACKSTATUS — el estado del intento de reproducción como una cadena de texto, uno de:
    - `SUCCESS`
    - `FAILED`

### La aplicación Read()

Esta aplicación lee un número predeterminado de dígitos de cadena, una cierta cantidad de veces, del usuario en la variable dada.

- filename -- archivo a reproducir antes de leer dígitos o tono con la opción i
- maxdigits -- número máximo aceptable de dígitos. Detiene la lectura después de que se hayan ingresado maxdigits (sin requerir que el usuario presione la tecla #). El valor predeterminado es 0 - sin límite - para esperar a que el usuario presione la tecla #. Cualquier valor inferior a 0 significa lo mismo. El valor máximo aceptado es 255.

![10-dialplan-advanced-features figura 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figura 5](../images/10-dialplan-advanced-features-img05.png)

- option -- options are `s`, `i`, `n`:
    - `s` — regresar inmediatamente si la línea no está activa
    - `i` — reproducir el nombre de archivo como tono de indicación desde su `indications.conf`
    - `n` — leer dígitos aun si la línea no está activa
- attempts -- si es mayor que 1, el número de intentos que se realizarán en caso de que no se ingresen datos
- timeout -- Un número entero de segundos para esperar una respuesta de dígitos. Si es mayor que 0, ese valor sobrescribirá el tiempo de espera predeterminado.

La aplicación read() debe desconectarse si la función falla o produce un error.

### La aplicación Gotoif()

Esta aplicación hará que el canal llamante salte a la ubicación especificada en el dialplan según la evaluación de la condición dada. El canal continuará en **labeliftrue** si la condición es verdadera, o en **labeliffalse** si la condición es falsa. Las etiquetas se especifican con la misma sintaxis que la utilizada dentro de la aplicación Goto. Si se omite la etiqueta elegida por la condición, no se realiza ningún salto; en su lugar, la ejecución continúa con la siguiente prioridad en el dialplan.

### Laboratorio: Construyendo un menú IVR paso a paso

Creemos un menú IVR con la siguiente funcionalidad. Cuando se marque, el IVR reproduce un archivo de audio con el mensaje “Welcome to the XYZ Corporation; press 1 for sales, 2 for tech support, 3 for training, or wait to speak to a representative.” Los dígitos enrutan al llamante de la siguiente manera:

- `1` — transferir a ventas (PJSIP/4001)
- `2` — transferir a soporte técnico (PJSIP/4002)
- `3` — transferir a capacitación (PJSIP/4003)
- No se presionó ningún dígito — transferir al operador (PJSIP/4000)

**Paso 1 – Grabar los prompts**

Creemos una extensión para grabar los avisos. Para grabar un aviso, marque desde un softphone a `9003<filename>` (por ejemplo, `9003welcome`). Cuando escuche el pitido, comience a grabar; presione `#` para detenerse. Oirá un pitido, y el sistema reproducirá el aviso grabado.

**Paso 2 – Crear la lógica del menú**

When dialing the 9004 extension, processing jumps to the menu in the `s` extension, priority 1.

### Coincidencia al marcar

This is a company setup menu for receiving calls. The `Background()` application plays the welcome prompt and then waits for digits, matching what the caller dials against the extensions defined in the current context.

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

Cuando marca esta empresa, primero se reproduce el mensaje de bienvenida. Después de eso, Asterisk espera a que se marque un dígito:

| Número marcado | Acción de Asterisk |
|---------------|--------------------|
| 1 | Llama inmediatamente a `Dial(DAHDI/1)` |
| 2 | Espera el tiempo de espera y luego llama a `Dial(DAHDI/2)` |
| 21 | Llama inmediatamente a `Dial(DAHDI/3)` |
| 22 | Llama inmediatamente a `Dial(DAHDI/4)` |
| 3 | Espera el tiempo de espera y luego desconecta |
| 31 | Llama inmediatamente a `Dial(DAHDI/5)` |
| 32 | Llama inmediatamente a `Dial(DAHDI/6)` |

Es importante evitar ambigüedades en los menús. Todos quieren ser atendidos rápidamente. Por esta razón, no debe usar los números 2, 21 o 22.

### Laboratorio: Uso de la aplicación Read()

Por favor, pruebe el laboratorio con la aplicación read(). Read acepta dígitos del usuario y los inserta en la variable especificada; luego puede usar la aplicación gotoif para redirigir la llamada.

## Inclusión de contexto

Un contexto puede incluir el contenido de otro contexto. En el ejemplo anterior, cualquier canal puede marcar cualquier extensión en el contexto interno, pero solo el canal 4003 puede marcar extensiones internacionales. Puedes usar la inclusión de contexto para facilitar la creación del plan de marcación. Usando la inclusión de contexto, puedes controlar quién tiene acceso a qué extensiones.

### Solución de problemas del mensaje “number not found”

Es muy común recibir el mensaje “number not found”. La mayoría de la gente confunde el concepto de contextos incluidos porque realmente no es intuitivo. Como regla general, primero ve al archivo de configuración del canal entrante, como `pjsip.conf`, `chan_dahdi.conf` y `iax.conf`, y determina el contexto actual. Luego, ve al plan de marcación en el archivo extensions.conf y verifica si el número marcado se encuentra en ese contexto. Si no, algo está mal con tu plan de marcación. Las reglas de oro de los contextos son: 1. Un canal solo puede marcar números dentro del mismo contexto que el canal. 2. El contexto donde se procesa la llamada se define en el archivo de configuración del canal entrante (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Usando la sentencia switch

Puedes enviar el procesamiento del dialplan a otro servidor usando el comando switch. Necesitarás el nombre y la clave del otro servidor. El contexto es el contexto de destino.

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Orden de procesamiento del plan de marcación

Cuando Asterisk recibe una llamada entrante, busca en el contexto definido por el canal. En algunos casos, si más de un patrón coincide con el número marcado, Asterisk no puede procesar la llamada exactamente como usted espera. Puede ver el orden de coincidencia usando el comando CLI `dialplan show`. Ejemplo: supongamos que desea marcar 912 para enrutar a un tronco analógico (DAHDI/1) y todos los demás números que comienzan con 9 a otro tronco analógico (DAHDI/2). Escribiría algo como:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Si dos patrones coinciden con una extensión, puede controlar qué extensión se procesa primero usando los contextos incluidos. Un contexto incluido se procesa después que un patrón en el mismo contexto.

## La sentencia #INCLUDE

¿Deberíamos usar un archivo grande o varios archivos? Puede usar la sentencia #include <filename> para incluir otros archivos en su extensions.conf. Por ejemplo, podríamos crear un users.conf para usuarios locales y un services.conf para servicios especiales. Tenga cuidado de no confundir #include <filename> con el

```
include=>context statement.
```

## Subrutinas con GOSUB

En versiones anteriores de Asterisk existía el comando Macro. Este comando quedó obsoleto hace mucho tiempo en favor de GOSUB. Aquí demostraremos cómo crear subrutinas para el procesamiento de buzón de voz de manera fácil y ordenada. Formato del comando:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

El comando GOSUB está disponible desde Asterisk 1.6 y permite pasar argumentos (disponibles dentro de la subrutina como `${ARG1}`, `${ARG2}`, etc.). Con argumentos, ahora es posible reemplazar completamente los antiguos comandos Macro. Los Macros (`app_macro`) fueron eliminados en Asterisk 21; debe usar GOSUB para las subrutinas.

### Creando la subrutina

La definición es muy similar. Observe la subrutina a continuación definida para el buzón de voz con el nombre stdexten (elija el nombre que prefiera). Después de invocar el comando Dial con el primer argumento (nombre del canal) verificamos el ${DIALSTATUS} para enviar la lógica de la llamada al siguiente paso.

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### Llamando a una subrutina

Preste atención al llamar la subrutina para usar paréntesis antes de los parámetros.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Usando la base de datos de Asterisk

Para implementar el desvío de llamadas y listas negras, necesitamos alguna forma de almacenar y restaurar datos. Afortunadamente, Asterisk proporciona un mecanismo para guardar y recuperar datos de una base de datos incorporada llamada AstDB. En Asterisk moderno (incluyendo Asterisk 22) AstDB está respaldada por **SQLite3** (el archivo `/var/lib/asterisk/astdb.sqlite3`); Asterisk 1.8 y versiones anteriores usaban Berkeley DB v1. Esto es similar a la base de datos del registro de Windows que utiliza el concepto jerárquico de familia y claves. Los datos persisten entre reinicios de Asterisk. La API familia/clave no ha cambiado respecto al backend anterior; solo cambió el formato de almacenamiento en disco.

### Funciones, aplicaciones y comandos CLI

Existen algunas funciones, aplicaciones y comandos CLI que trabajan con AstDB:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Ejemplos:

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

Algunas aplicaciones pueden usarse para manipular AstDB:

- DB_DELETE(<family/key>) — función que devuelve y elimina una única clave
- DBdeltree(<family>) — aplicación que elimina una familia/subárbol completo

La antigua aplicación `DBdel()` ya no existe en Asterisk 22. Elimine una única clave con la función de dialplan `DB_DELETE()` — por ejemplo `Set(x=${DB_DELETE(family/key)})` o, como operación de escritura, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (eliminar una familia/subárbol completo) sigue siendo una aplicación.

También es posible usar comandos CLI para establecer y eliminar claves:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementando desvío de llamadas, DND y listas negras

En este ejemplo, aprenderá cómo implementar el desvío de llamadas inmediato y el desvío de llamadas cuando la línea está ocupada. Usaremos *21* para programar el desvío inmediato y *61* para programar el desvío cuando está ocupado. Para cancelar la programación, use #21# y #61#, respectivamente. Use el ejemplo anterior para poblar la base de datos. Familias usadas:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

Intente poblar la base de datos marcando:

- *21* (extensión de destino para desvío inmediato)
- *61* (extensión de destino para desvío cuando está ocupado)
- *41* (extensión para activar No Molestar)

Use el comando CLI `database show` para ver las familias, claves y valores añadidos.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Desvío de llamadas, lista negra, DND

La subrutina verifica si la base de datos contiene los pares clave:valor correspondientes a CFIM, CFBS o DND, y luego los maneja adecuadamente. La siguiente subrutina llama a la rutina de marcación:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Usando una lista negra

La antigua aplicación `LookupBlacklist()` fue **eliminada** de Asterisk (desapareció junto con el mecanismo heredado de salto "priority+101"). En Asterisk 22 construyes una lista negra directamente con la función `DB_EXISTS()` (que tanto prueba una clave como, cuando la encuentra, expone su valor en `${DB_RESULT}`) más `GotoIf`. Almacena cada número bloqueado como una clave en una familia `blacklist`, luego verifica el ID de la llamada al inicio de tu contexto de entrada:

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

`DB_EXISTS(blacklist/${CALLERID(num)})` devuelve `1` cuando el número del llamante está presente en la base de datos (enviando la llamada al contexto `blocked`) y `0` en caso contrario, de modo que la llamada continúa al `Dial()` normal.

Para insertar un número en la lista negra, podemos usar el mismo recurso que antes, usando *31* seguido de las extensiones que se desean bloquear. Para eliminar un número de la lista negra, debe usarse #31# seguido del número a eliminar.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

También puedes insertar los números en la lista negra usando la CLI de la consola:

```
*CLI>database put blacklist <name/number> 1
```

Nota: Cualquier valor puede asociarse con la clave. La prueba `DB_EXISTS()` busca la clave, no el valor. Para borrar el número de la lista negra, puedes usar:

```
*CLI>database del blacklist <name/number>
```

## Contextos basados en tiempo

En la figura siguiente, tenemos un plan de marcación con tres contextos. El contexto [incoming] es donde normalmente se reciben las llamadas. Hemos incluido cuatro líneas que cambian el comportamiento según la hora del sistema, como se ejemplifica a continuación:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

Modern Asterisk (including 22) separates the time-include fields with **commas**, not pipes. The legacy pipe form (`include => context|times|weekdays|mdays|months`) is parsed as a plain literal context name and silently fails to apply any time condition.

During regular working hours, processing will be redirected to the mainmenu, where it will probably call an IVR to handle the incoming call. If the call takes place after hours, it will call the security extension defined in the ${SECURITY} variable. If the security extension does not answer the call, it will be sent to the operator’s voicemail.

![10-dialplan-advanced-features figura 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figura 12](../images/10-dialplan-advanced-features-img12.png)

## Mensajes basados en tiempo usando gotoiftime()

La sintaxis de GotoIfTime() se muestra a continuación.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

En Asterisk 22 el separador de campos es una **coma**, no una barra vertical (la forma con barra vertical quedó obsoleta en Asterisk 1.6). Se admite un campo opcional `timezone`, y cada etiqueta de rama usa la forma habitual `[[context,]extension,]priority`.

Esta aplicación puede reemplazar el contexto basado en tiempo y parece más fácil de entender y leer. Puede especificar el tiempo de la siguiente manera:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=número del 1 al 31
- <hour>=número del 0 al 23
- <minute>=número del 0 al 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Los nombres de los días y los meses no distinguen entre mayúsculas y minúsculas.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

La instrucción anterior transfiere el procesamiento a la extensión s en el contexto normalhours si la llamada se realiza entre las 08:00 AM y las 06:00 PM de lunes a viernes.

## Usando DISA para obtener un nuevo tono de marcación

DISA, o “acceso directo al sistema interno”, es un sistema que permite a los usuarios recibir un segundo tono de marcación. Permite a los usuarios marcar nuevamente a otro destino. Se usa frecuentemente por técnicos cuando marcan llamadas de larga distancia para soporte técnico los fines de semana; en lugar de marcar desde sus casas directamente al destino, llaman al número DISA de la oficina, reciben un tono de marcación y luego llaman al destino. Los cargos de larga distancia se generan a nombre de la empresa en lugar del teléfono doméstico.

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

Ejemplo:

```
exten => s,1,DISA(no-password,default)
```

Usando la declaración anterior, el usuario marca la PBX y—sin requerir ninguna contraseña—recibe un tono de marcación. Cualquier llamada que use DISA será procesada usando el contexto `default`. Los argumentos para esta aplicación incluyen una contraseña global o una contraseña individual dentro de un archivo. Si no se especifica un contexto, se asume el contexto `disa`. Si usa un archivo de contraseñas, debe especificarse la ruta completa. También se puede especificar un identificador de llamada para la marcación externa de DISA. Ejemplo:

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 usa comas como separadores de argumentos (la forma con barra vertical quedó obsoleta en la versión 1.6). El primer argumento es ya sea un solo código de acceso o la ruta a un archivo de códigos, y el contexto predeterminado cuando no se indica ninguno es `disa`.

## Limitar llamadas simultáneas

La función GROUP() le permite contar cuántos canales activos tiene en un grupo al mismo tiempo. Ejemplo: tiene una sucursal en Río de Janeiro, donde los teléfonos siguen el patrón “_214X”. Esta ubicación está servida por una línea arrendada, con 64 K reservados para ancho de banda de voz. En este caso, el número máximo de llamadas permitidas es 2 (G.729, aproximadamente 31,2 K por llamada). Para limitar las llamadas a Río a dos:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail es un sistema de contestador telefónico computarizado que graba los mensajes de voz entrantes, guardándolos en disco o enviándolos por correo electrónico. A veces tiene un directorio donde se pueden buscar los buzones de voz por nombre. En el pasado, los sistemas de voicemail eran muy costosos. Ahora, con la telefonía IP, el voicemail se está convirtiendo en una característica estándar.

Para configurar el voicemail, debe seguir los siguientes pasos.

**Step 1: Edit `voicemail.conf` and set the general parameters.**

- `format` — codec used to record the message (e.g., wav49, wav, gsm)
- `serveremail` — who the e-mail notification should appear to come from
- `maxmsg` — maximum number of messages in the mailbox; after this threshold, messages are discarded
- `maxsecs` — maximum length of a voicemail message, in seconds
- `minsecs` — minimum length of a message, in seconds; below this threshold, no message is recorded
- `maxsilence` — how many seconds of silence to treat as the end of the message

**Step 2: Edit `voicemail.conf` and create the users’ mailboxes.**

### Voicemail.conf

A mailbox is defined with one line per mailbox, in the form:

```
mailboxID => pincode,fullname,email,pager-email,options
```

The fields are:

- **MailboxID** — usually the extension number
- **Pincode** — password to access the voicemail system
- **Full name** — used by the directory application
- **E-mail** — address for voicemail notification
- **Pager e-mail** — address for notification via an SMS gateway or pager
- **Options** — per-mailbox options (the same options as in `[general]`, but applied to this mailbox)

Voicemail has several options that control its behavior. For now, we will stick to the default options and concentrate on the mailbox definition. After the `[general]` section in the file, you start configuring the mailbox IDs, each in its own context. Example:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Please check for advanced options in the file `voicemail.conf`.

**Step 3: Configure the file `extensions.conf`.**

The `stdexten` subroutine shown earlier (under *Subroutines with GOSUB*) is exactly the call/voicemail handler you need here: it dials the extension and uses the value of the channel variable `${DIALSTATUS}` to redirect the call flow to the proper voicemail greeting (`b` for busy, `u` for unavailable). Call it with `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` from each extension in `extensions.conf`.

## Uso de la aplicación VoiceMailMain()

La aplicación voicemailmain() se usa para configurar el buzón de correo de voz. Los usuarios pueden marcar la aplicación, grabar su saludo y escuchar su correo de voz. Para llamar a la aplicación en el dialplan, use:

```
exten=>9000,1,VoiceMailMain()
```

A continuación encontrará una lista de las opciones disponibles para la aplicación.

### Sintaxis de la aplicación Voicemail

Esta aplicación permite que la parte que llama deje un mensaje para una lista especificada de buzones. Cuando se especifican varios buzones, el saludo se tomará del primer buzón especificado. La ejecución del dialplan se detendrá si el buzón especificado no existe. La sintaxis se muestra a continuación:

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

En todos los casos, se reproducirá el archivo beep.gsm antes de que comience la grabación. Los mensajes de correo de voz se almacenarán en el directorio inbox.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Si el llamante presiona 0 (cero) durante el anuncio, será trasladado a la extensión ‘o’ (out) en el contexto actual de voicemail. Esto puede usarse para salir al operador. Si durante la grabación el llamante presiona # o se agota el tiempo límite de silencio, la grabación se detiene y la llamada pasa a la siguiente prioridad. Asegúrese de manejar la llamada después de reproducir el correo de voz, como se muestra a continuación.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Etiquetar mensajes de voicemail como urgentes

Puede etiquetar algunos mensajes como “urgente”. Hay dos métodos disponibles para ello:

- Pase la opción ‘U’ en la aplicación voicemail()
- Especifique review=yes en el archivo voicemail.conf. Si usa esta opción, el usuario podrá etiquetar el mensaje como urgente después de grabar las instrucciones de voz.

## Envío de correo de buzón de voz

En algunos casos (como el mío), simplemente no usamos la aplicación voicemailmain() para leer el correo. Es más simple y práctico enviar todos los mensajes al correo con el audio adjunto. Usando los parámetros ‘attach’ y ‘delete’, puedes enviar todos los correos al correo y eliminarlos del buzón.

```
attach=yes
delete=yes
```

Para enviar el buzón de voz al correo, la aplicación voicemail usa el agente de transferencia de mensajes (MTA), un componente de tu sistema operativo. Debian usa Exim como MTA. La aplicación que envía el correo está definida en el parámetro ‘mailcmd’.

```
mailcmd =/usr/sbin/sendmail -t
```

En la distribución Debian de Linux, el MTA es Exim. Para configurar Exim en Debian, usa:

```
dpkg-reconfigure exim4-config
```

Puedes elegir que tu MTA envíe un correo directamente mediante SMTP o a través de un smarthost (usualmente el servidor de correo de tu empresa). Verifica con tu administrador de correo la mejor forma de enviar correo desde el servidor Asterisk a tu servidor de correo.

## Personalizando el mensaje de correo electrónico

Puedes controlar cómo se envían los mensajes configurando las siguientes variables: Variables para el asunto del correo y el cuerpo del correo:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

El cuerpo y el asunto del correo se construyen a partir de una plantilla que estableces en la sección `[general]` de `voicemail.conf`. Puedes modificar tanto el cuerpo como el asunto, pero el límite de tamaño del mensaje es de 512 bytes. En la plantilla, `\n` inserta una nueva línea y `\t` inserta una tabulación.

El ejemplo `emailsubject` a continuación es sencillo. El ejemplo `emailbody` está muy cerca del valor predeterminado; el predeterminado muestra solo el CIDNAME cuando no es nulo, de lo contrario el CIDNUM, o "un llamante desconocido" cuando ambos son nulos.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interfaz web de buzón de voz

Existe un script Perl en la distribución fuente llamado `vmail.cgi`, ubicado en `contrib/scripts/vmail.cgi` dentro del árbol de fuentes de Asterisk (todavía se incluye con Asterisk 22). El comando `make install` no instala esta interfaz; debe ejecutar `make webvmail` desde el directorio de fuentes. Este script requiere que el intérprete de comandos Perl y un servidor web (como Apache) estén instalados en el servidor.

```
make webvmail
```

El objetivo `make webvmail` instala el script (setuid root) en el directorio CGI de su servidor web (`HTTP_CGIDIR`) y copia las imágenes de soporte desde `images/*.gif` a `HTTP_DOCSDIR/_asterisk` (por defecto `/var/www/html/_asterisk`). Si esas rutas no coinciden con la estructura de su servidor web, edite las variables `HTTP_CGIDIR` y `HTTP_DOCSDIR` en el archivo de nivel superior `Makefile` antes de ejecutar el objetivo.

## Notificación de buzón de voz

Puede configurar el buzón de voz para enviar un mensaje de notificación a su teléfono cuando tenga un nuevo buzón de voz. En Asterisk 22, la Indicación de Mensaje en Espera (MWI) funciona con teléfonos PJSIP y SIP, así como con teléfonos DAHDI. Para indicar un buzón de voz no escuchado, una luz indicadora puede parpadear o el teléfono puede reproducir un tono de alerta. Necesita configurar el buzón en el archivo de configuración del canal correspondiente. Ejemplo: `pjsip.conf` (en la sección endpoint):

```
mailboxes=8590
```

En PJSIP la pista del buzón se establece con la opción `mailboxes` dentro de la sección endpoint de `pjsip.conf`, en lugar del antiguo `mailbox=` de `sip.conf`. Las suscripciones MWI son manejadas por el módulo `res_pjsip_mwi`.

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Laboratorio: Notificación de mensaje en el teléfono

Este laboratorio se probó usando un softphone SIP.

1. Edite `pjsip.conf` y añada `mailboxes=4401` en la sección endpoint para el dispositivo llamado 4401.
2. Edite el `extensions.conf` y cree una extensión para grabar un buzón de voz a extensiones 4401.

```
exten=9008,1,voicemail(4401,b)
```

3. Vaya a la consola y recargue.
4. En el Softphone SipPulse, abra la configuración de la cuenta SIP y habilite la verificación de buzón de voz (message-waiting) para la cuenta.
5. Marque 9008 y deje un mensaje.
6. Observe el ícono de mensaje en el teléfono.

## Usando la aplicación directory

Esta aplicación le permite encontrar rápidamente un usuario para marcar. La lista de nombres y extensiones correspondientes se recupera del archivo de configuración de buzón de voz voicemail.conf. La sintaxis de la aplicación puede mostrarse usando core show application directory:

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### Laboratorio: Usando la aplicación directory

1. Edite el archivo voicemail.conf para agregar dos extensiones en el plan de marcación

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Cree estas extensiones en su plan de marcación

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Vaya a la consola y recargue  
4. Marque 9006 y grabe un nombre para cada extensión (4400, 4401)  
5. Marque 9007 y seleccione las tres letras del apellido para una extensión (Eas=327). Si esta es la opción correcta, presione ‘1’ para transferir al nombre.

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## Resumen

En este capítulo, has aprendido cómo recibir llamadas usando un IVR o un asistente automático. Has estudiado el concepto de inclusión de contextos y implementado algunos ejemplos. Se usaron subrutinas para evitar escribir de forma repetitiva, y la base de datos de Asterisk (AstDB, respaldada por SQLite3 en Asterisk 22) se utilizó para funciones que requieren almacenamiento de datos (p. ej., desvío de llamadas, no molestar, listas negras). Finalmente, has aprendido cómo implementar el comportamiento fuera de horario y has implementado un plan de marcación completo usando estos conceptos.

## Quiz

1. Un contexto dependiente del tiempo incluye el formato `include => context,<times>,<weekdays>,<mdays>,<months>`. ¿Qué hace `include => normalhours,08:00-18:00,mon-fri,*,*`?
   - A. Ejecuta las extensiones de lunes a viernes, de 08:00 a 18:00
   - B. Ejecuta las opciones todos los días en todos los meses
   - C. Nada; el formato es inválido
2. En Asterisk moderno (incluyendo Asterisk 22), los campos de un `include =>` basado en tiempo y de `GotoIfTime()` están separados por qué carácter?
   - A. La barra vertical `|`
   - B. La coma `,`
   - C. El punto y coma `;`
   - D. La barra diagonal `/`
3. Para marcar varios canales a la vez (sonándolos simultáneamente), los separas dentro de `Dial()` con el carácter ___.
4. Un menú de voz que reproduce un mensaje mientras espera que el llamante marque una extensión se crea normalmente con la aplicación ___.
5. Puedes incluir el contenido de otro archivo dentro de `extensions.conf` usando la sentencia ___ (nota: esto es diferente de la sentencia de contexto `include =>`).
6. En Asterisk 22, la base de datos interna AstDB está respaldada por:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Cuando usas `Dial(type1/identifier1&type2/identifier2)`, Asterisk marca cada canal en secuencia, esperando 20 segundos entre ellos.
   - A. Falso
   - B. Verdadero
8. Con la aplicación Background(), debes esperar a que el mensaje termine de reproducirse antes de poder presionar un dígito DTMF para elegir una opción.
   - A. Falso
   - B. Verdadero
9. Dada la sintaxis `Goto([[context,]extension,]priority)`, ¿cuáles de las siguientes son invocaciones válidas de la aplicación Goto()? (marca todas las que correspondan)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Para eliminar una sola clave de AstDB en el plan de marcación de Asterisk 22, utilizas:
    - A. La aplicación `DBdel()`
    - B. La función `DB_DELETE()`
    - C. La aplicación `DBdeltree()`
    - D. La aplicación `LookupBlacklist()`

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
