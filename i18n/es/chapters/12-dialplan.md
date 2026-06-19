# Características avanzadas del dialplan

El Capítulo 3 trató los conceptos básicos de un dialplan. Por razones didácticas, no explicamos todas las funciones, sino solo algunas de las más importantes. Este capítulo profundizará más en el dialplan, describiendo técnicas avanzadas, nuevas aplicaciones y conceptos.

## Objetivos

Al finalizar este capítulo, usted debería ser capaz de:

- Simplificar sus entradas de extensiones
- Abordar la seguridad del dialplan y filtrar extensiones
- Recibir llamadas mediante un menú IVR
- Usar subrutinas para evitar reescrituras innecesarias
- Implementar cierta seguridad en el dialplan usando “Include”
- Implementar el desvío de llamadas (follow-me) usando AsteriskDB
- Implementar un comportamiento fuera de horario en su PBX
- Usar el comando switch para transferir a otra PBX
- Implementar el gestor de privacidad
- Implementar el correo de voz (voicemail)
- Implementar un directorio corporativo

## Simplificando su dialplan

Puede simplificar su dialplan usando la palabra clave “same” para definir una extensión. Esto debería reducir el número de errores tipográficos en el dialplan. Revise el siguiente ejemplo:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Seguridad del dialplan

Se descubrió una vulnerabilidad en el dialplan de Asterisk que permite a un usuario inyectar un nuevo canal y marcar un número en su dialplan. Supongamos que usted tiene la siguiente línea en su servidor `exten=>_X.,1,Dial(PJSIP/${EXTEN})` y un usuario malintencionado marcó el número `3000&DAHDI/1/011551123456789` en el softphone. El protocolo SIP, por defecto, acepta cualquier carácter alfanumérico, por lo que la extensión marcada activará en realidad dos llamadas: una para el canal PJSIP/3000 y la otra para el canal DAHDI/011551123456789, que es un número internacional. Por lo tanto, cualquier usuario con acceso a una extensión puede marcar a cualquier parte del mundo. La forma más sencilla de evitar este comportamiento es filtrar los números antes de llamar a la aplicación dial. La función FILTER() es muy útil para esto. Ejemplo:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

La aplicación filter le permitirá filtrar todos los caracteres del número marcado excepto los números del 0 al 9. Puede encontrar más información en el archivo README-SERIOUSLY.bestpractices.txt disponible en Asterisk.

## Recibir llamadas usando un menú IVR

En la sección anterior, usted recibió todas las llamadas usando DID o reenviándolas al operador. Ahora aprenderá cómo implementar un menú IVR, así como crear un servicio de operadora automática. Antes de entrar en detalles, examinemos algunas aplicaciones nuevas. Ponemos la salida del comando show application a continuación simplemente para facilitar la lectura. Puede obtener estas descripciones usando show application nombre_de_aplicacion. 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### La aplicación Background()

Esta aplicación reproducirá la lista de archivos proporcionada mientras espera que el canal que llama marque una extensión. Para seguir esperando dígitos después de que esta aplicación haya terminado de reproducir los archivos, se debe usar la aplicación WaitExten. La opción langoverride especifica explícitamente qué idioma intentar usar para los archivos de sonido solicitados. Cualquier contexto que se especifique será el contexto del dialplan que esta aplicación usará al salir a una extensión marcada. Si uno de los archivos de sonido solicitados no existe, el procesamiento de la llamada terminará. Opciones:

- s - Hace que la reproducción del mensaje se omita si el canal no está en estado 'up' (es decir, aún no ha sido contestado). Si esto sucede, la aplicación regresará inmediatamente.
- n - No contesta el canal antes de reproducir los archivos.
- m - Solo se interrumpe si un dígito coincide con una extensión de un solo dígito en el contexto de destino.

### La aplicación Record()

Esta aplicación graba desde el canal en un nombre de archivo determinado. Si el archivo existe, será sobrescrito.

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' es el formato del tipo de archivo a grabar (wav, gsm, etc.).
- 'silence' es el número de segundos de silencio permitidos antes de regresar.
- 'maxduration' es la duración máxima de grabación en segundos; si falta o es cero, no hay máximo.
- 'options' puede contener cualquiera de las siguientes letras:
    - `a` — añade a una grabación existente en lugar de reemplazarla
    - `n` — no contesta, pero graba de todos modos si la línea aún no ha sido contestada
    - `q` — silencioso (no reproduce un tono de pitido)
    - `s` — omite la grabación si la línea aún no ha sido contestada
    - `t` — usa la tecla terminadora alternativa `*` (DTMF) en lugar de la predeterminada `#`
    - `x` — ignora todas las teclas terminadoras (DTMF) y continúa grabando hasta colgar

Si el nombre de archivo contiene %d, estos caracteres serán reemplazados por un número incrementado en uno cada vez que se grabe el archivo. Use core show file formats para ver los formatos disponibles en su sistema. El usuario puede presionar # para terminar la grabación y continuar con la siguiente prioridad. Si el usuario cuelga durante una grabación, todos los datos se perderán y la aplicación terminará.

### La aplicación Playback()

Esta aplicación reproduce los nombres de archivo proporcionados (no incluya la extensión). Las opciones también pueden incluirse después de un símbolo de barra vertical (pipe). La opción 'skip' hace que la reproducción del mensaje se omita si el canal no está en estado 'up' (es decir, aún no ha sido contestado).

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

Si se especifica 'skip', la aplicación regresará inmediatamente si el canal no está descolgado. De lo contrario, a menos que se especifique 'noanswer', el canal será contestado antes de que se reproduzca el sonido. No todos los canales admiten la reproducción de mensajes mientras aún están descolgados. Si se especifica 'j', la aplicación saltará a la prioridad n+101 cuando el archivo no exista, si está presente. Esta aplicación establece la siguiente variable de canal al finalizar:

- PLAYBACKSTATUS — el estado del intento de reproducción como una cadena de texto, uno de:
    - `SUCCESS`
    - `FAILED`

### La aplicación Read()

Esta aplicación lee un número predeterminado de dígitos de cadena, un cierto número de veces, del usuario hacia la variable dada.

- filename -- archivo a reproducir antes de leer dígitos o tono con la opción i
- maxdigits -- número máximo aceptable de dígitos. Deja de leer después de que se hayan ingresado maxdigits (sin requerir que el usuario presione la tecla #). El valor predeterminado es 0 - sin límite - para esperar a que el usuario presione la tecla #. Cualquier valor por debajo de 0 significa lo mismo. El valor máximo aceptado es 255.

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- las opciones son `s`, `i`, `n`:
    - `s` — regresa inmediatamente si la línea no está activa
    - `i` — reproduce filename como un tono de indicación desde su `indications.conf`
    - `n` — lee dígitos incluso si la línea no está activa
- attempts -- si es mayor que 1, el número de intentos que se realizarán en caso de que no se ingresen datos
- timeout -- Un número entero de segundos para esperar una respuesta de dígito. Si es mayor que 0, ese valor anulará el tiempo de espera predeterminado.

La aplicación read() debería desconectarse si la función falla o genera errores.

### La aplicación Gotoif()

Esta aplicación hará que el canal que llama salte a la ubicación especificada en el dialplan basándose en la evaluación de la condición dada. El canal continuará en labeliftrue si la condición es verdadera, o en 'labeliffalse' si la condición es falsa. Las etiquetas se especifican con la misma sintaxis que la utilizada dentro de la aplicación Goto. Si se omite la etiqueta elegida por la condición, no se realiza ningún salto; más bien, la ejecución continúa con la siguiente prioridad en el dialplan.

### Laboratorio: Construyendo un menú IVR paso a paso

Creemos un menú IVR con la siguiente funcionalidad. Cuando se marca, el IVR reproduce un archivo de audio con el mensaje “Bienvenido a XYZ Corporation; presione 1 para ventas, 2 para soporte técnico, 3 para capacitación, o espere para hablar con un representante”. Los dígitos enrutan a la persona que llama de la siguiente manera:

- `1` — transferir a ventas (PJSIP/4001)
- `2` — transferir a soporte técnico (PJSIP/4002)
- `3` — transferir a capacitación (PJSIP/4003)
- Ningún dígito presionado — transferir al operador (PJSIP/4000)

**Paso 1 – Grabar los mensajes**

Creemos una extensión para grabar los mensajes. Para grabar un mensaje, marque desde un softphone a `9003<filename>` (por ejemplo, `9003welcome`). Cuando escuche el pitido, comience a grabar; presione `#` para detener. Escuchará un pitido y el sistema reproducirá el mensaje grabado.

**Paso 2 – Crear la lógica del menú**

Al marcar la extensión 9004, el procesamiento salta al menú en la extensión `s`, prioridad 1.

### Coincidencia mientras marca

Este es un menú de configuración de empresa para recibir llamadas. La aplicación background lee el contexto actual y define la longitud máxima para cada número para cualquier combinación posible.

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

Cuando usted marca a esta empresa, primero se reproduce el mensaje de bienvenida. Después de eso, Asterisk espera a que se marque un dígito. Número marcado Acción de Asterisk Llama inmediatamente a Dial(DAHDI/1) Espera el tiempo de espera, luego va a Dial(DAHDI/2) Llama inmediatamente a (DAHDI/3) Llama inmediatamente a (DAHDI/4) Espera el tiempo de espera, luego se desconecta Llama inmediatamente a Dial(DAHDI/5) Llama inmediatamente a Dial(DAHDI/6) Se desconecta inmediatamente Es importante evitar la ambigüedad en los menús. Todo el mundo quiere ser atendido rápidamente. Por esta razón, no debe usar los números 2, 21 o 22.

### Laboratorio: Usando la aplicación Read()

Por favor, pruebe el laboratorio con la aplicación read(). Read acepta dígitos del usuario y los inserta en la variable especificada; luego puede usar la aplicación gotoif para redirigir la llamada.

## Inclusión de contextos

Un contexto puede incluir el contenido de otro contexto. En el ejemplo anterior, cualquier canal puede marcar cualquier extensión en el contexto internal, pero solo el canal 4003 puede marcar extensiones internacionales. Puede usar la inclusión de contextos para facilitar la creación del dialplan. Usando la inclusión de contextos, puede controlar quién tiene acceso a qué extensiones.

### Solución de problemas del mensaje “number not found”

Es muy común recibir el mensaje “number not found”. La mayoría de las personas confunden el concepto de contextos incluidos porque realmente no es intuitivo. Como regla general, primero vaya al archivo de configuración del canal entrante, como `pjsip.conf`, `chan_dahdi.conf` y `iax.conf`, y determine el contexto actual. Luego, vaya al dialplan en el archivo extensions.conf y verifique si el número marcado se puede encontrar en ese contexto. Si no, algo anda mal con su dialplan. Las reglas de oro de los contextos son: 1. Un canal solo puede marcar números dentro del mismo contexto que el canal. 2. El contexto donde se procesa la llamada se define en el archivo de configuración del canal entrante (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Usando la sentencia switch

Puede enviar el procesamiento del dialplan a otro servidor usando el comando switch. Necesitará el nombre y la clave del otro servidor. El contexto es el contexto de destino.

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Orden de procesamiento del dialplan

Cuando Asterisk recibe una llamada entrante, busca en el contexto definido por el canal. En algunos casos, si más de un patrón coincide con el número marcado, Asterisk no puede procesar la llamada de la manera exacta que usted cree que debería. Puede ver el orden de coincidencia usando el comando CLI dialplan show. Ejemplo: Digamos que desea marcar 912 para enrutar a un trunk analógico (DAHDI/1) y todos los demás números que comienzan con 9 a otro trunk analógico (DAHDI/2). Usted escribiría algo como:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Si dos patrones coinciden con una extensión, puede controlar qué extensión se procesa primero usando los contextos incluidos. Un contexto incluido se procesa después que un patrón en el mismo contexto.

## La sentencia #INCLUDE

¿Deberíamos usar un archivo grande o varios archivos? Puede usar la sentencia #include <filename> para incluir otros archivos en su extensions.conf. Por ejemplo, podríamos crear un users.conf para usuarios locales y services.conf para servicios especiales. Tenga cuidado de no confundir #include <filename> con la

```
include=>context statement.
```

## Subrutinas con GOSUB

En versiones anteriores de Asterisk tenía el comando Macro. Este comando fue desaprobado hace mucho tiempo en favor de GOSUB. Demostraremos aquí cómo crear subrutinas para el procesamiento de voicemail de una manera fácil y ordenada. Formato del comando:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

El comando GOSUB ha estado disponible desde Asterisk 1.6 y admite el paso de argumentos (disponibles dentro de la subrutina como `${ARG1}`, `${ARG2}`, etc.). Con argumentos, ahora es posible reemplazar completamente los antiguos comandos Macro. Las macros (`app_macro`) fueron eliminadas en Asterisk 21; debe usar GOSUB para las subrutinas.

### Creando la subrutina

La definición es muy similar. Mire la subrutina a continuación definida para voicemail con el nombre stdexten (elija el nombre que desee). Después de llamar al comando Dial con el primer argumento (nombre del canal), verificamos ${DIALSTATUS} para enviar la lógica de la llamada al siguiente paso.

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

Preste atención al llamar a la subrutina para usar paréntesis antes de los parámetros.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Usando Asterisk DB

Para implementar el desvío de llamadas y las listas negras, necesitamos alguna forma de almacenar y restaurar datos. Afortunadamente, Asterisk proporciona un mecanismo para almacenar y recuperar datos de una base de datos incorporada llamada AstDB. En el Asterisk moderno (incluyendo Asterisk 22), AstDB está respaldado por **SQLite3** (el archivo `/var/lib/asterisk/astdb.sqlite3`); las versiones anteriores usaban Berkeley DB v1. Esto es similar a la base de datos del registro de Windows usando el concepto jerárquico de familia y claves. Los datos persisten entre reinicios de Asterisk.

> **[Nota de la 2.ª ed.]** Desde Asterisk 10, AstDB se almacena en SQLite3 (`astdb.sqlite3`), no en el archivo heredado Berkeley DB v1 utilizado por Asterisk 1.8 y versiones anteriores. La API de familia/clave no ha cambiado.

### Funciones, aplicaciones y comandos CLI

Hay algunas funciones, aplicaciones y comandos CLI que funcionan con AstDB:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Ejemplos:

```
exten=_*21*XXXX,1,set(DB(CFBS/${CALLERID(num)}=${EXTEN:4}))
exten=s,1,set(temp=${DB(CFBS/${EXTEN})})
```

Algunas aplicaciones se pueden usar para manipular AstDB:

- DB_DELETE(<family/key>) — función que devuelve y elimina una clave (la antigua aplicación `DBdel()` fue eliminada)
- DBdeltree(<family>)

> **[Nota de la 2.ª ed.]** La aplicación `DBdel()` ya no existe en Asterisk 22. Elimine una sola clave con la función de dialplan `DB_DELETE()` — p. ej., `Set(x=${DB_DELETE(family/key)})` o, como operación de escritura, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (eliminar una familia/subárbol completo) sigue siendo una aplicación.

Es posible usar comandos CLI para establecer y eliminar claves también:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementando desvío de llamadas, DND y listas negras

En este ejemplo, aprenderá cómo implementar el desvío de llamadas inmediato y el desvío de llamadas por ocupado. Usaremos *21* para programar el desvío de llamadas inmediato y *61* para programar el desvío de llamadas por estado ocupado. Para cancelar la programación, use #21# y #61#, respectivamente. Use el ejemplo anterior para poblar la base de datos. Familias utilizadas:

- CFIM – Desvío de llamadas inmediato
- CFBS – Desvío de llamadas por estado ocupado
- DND – No molestar

Intente poblar la base de datos marcando:

- *21* (Extensión de destino para el desvío de llamadas inmediato)
- *61* (Extensión de destino para el desvío de llamadas por estado ocupado)
- *41* (Extensión para poner en no molestar)

Use el comando CLI database show para ver las familias, claves y valores agregados.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Desvío de llamadas. Lista negra, DND

La subrutina anterior verifica si la base de datos contiene los pares clave:valor correspondientes a CFIM, CFBS o DND, y luego los maneja adecuadamente. La subrutina follow llama a la rutina de marcado:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Usando una lista negra

> **[Nota de la 2.ª ed.]** La aplicación `LookupBlacklist()` fue **eliminada** (desapareció con el antiguo mecanismo de "salto de prioridad+101" mucho antes de Asterisk 22 — confirmado que no está registrada en el laboratorio 22.10.0). Implemente una lista negra en su lugar con las funciones `DB()`/`DB_EXISTS()` más `GotoIf`, por ejemplo:
>
> ```
> exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
> exten => s,n,Dial(PJSIP/4000,20,tT)
> exten => s,n,Hangup()
> ```
>
> El ejemplo a continuación se conserva para referencia histórica; la opción `j` y el salto de prioridad `n+101` ya no existen.

Para crear una lista negra, usamos la aplicación LookupBlacklist(). La aplicación verifica el nombre/número en el identificador de llamadas (caller ID). Si no se encuentra el número, la aplicación establece la variable $LOOKUPBLSTATUS en NOTFOUND. Si se encuentra el número, la aplicación establece la variable en FOUND. Puede usar la opción “j” en la aplicación para usar el comportamiento antiguo (1.0), saltando 101 posiciones si se encuentra el número/nombre. Ejemplo:

```
[incoming]
exten => s,1,LookupBlacklist(j)
exten => s,2,Dial(PJSIP/4000,20,tTj)
exten => s,3,Hangup()
exten => s,102,Goto(blocked,s,1)
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

Para insertar un número en la lista negra, podemos usar el mismo recurso que antes, usando *31* seguido de las extensiones que se incluirán en la lista negra. Para eliminar un número de la lista negra, debe usar #31# seguido del número que se eliminará.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN}=1})
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

También puede insertar los números en la lista negra usando la consola CLI:

```
CLI>database put blacklist <name/number> 1
```

Nota: Cualquier valor puede asociarse con la clave. La aplicación de lista negra buscará la clave, no el valor. Para borrar el número de la lista negra, puede usar:

```
CLI>database del blacklist <name/number>
```

## Contextos basados en el tiempo

En la siguiente figura, tenemos un dialplan con tres contextos. El contexto [incoming] es donde se reciben habitualmente las llamadas. Hemos incluido cuatro líneas que cambian el comportamiento dependiendo de la hora del sistema, como se ejemplifica a continuación:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

> **[Nota de la 2.ª ed.]** El Asterisk moderno (incl. 22) separa los campos de time-include con **comas**, no con barras verticales. La forma heredada de barra vertical (`include => context|times|weekdays|mdays|months`) se analiza como un nombre de contexto literal simple y falla silenciosamente al aplicar cualquier condición de tiempo. Verificado en el laboratorio de Asterisk 22.10.0.

Durante el horario laboral habitual, el procesamiento se redirigirá al mainmenu, donde probablemente llamará a un IVR para manejar la llamada entrante. Si la llamada ocurre fuera del horario laboral, llamará a la extensión de seguridad definida en la variable ${SECURITY}. Si la extensión de seguridad no responde la llamada, se enviará al correo de voz del operador.

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Mensajes basados en el tiempo usando gotoiftime()

La sintaxis de gotoiftime() se muestra a continuación.

```
GotoIfTime(<timerange>,<daysofweek>,<daysofmonth>,<months>[,<timezone>]?[[context,]extension,]pri)
```

> **[Nota de la 2.ª ed.]** En Asterisk 22, el separador de campos es una **coma**, no una barra vertical (la forma de barra vertical fue desaprobada en Asterisk 1.6). La sintaxis documentada actual es `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])`. Se admite un campo opcional `timezone`.

Esta aplicación puede reemplazar el contexto basado en el tiempo y parece más fácil de entender y leer. Puede especificar el tiempo de la siguiente manera:

- <timerange>=<hora>':'<minuto>'-'<hora>':'<minuto> |"*"
- <diasdelasemana>=<nombre_dia>|<nombre_dia>'-'<nombre_dia>|"*"
- <nombre_dia>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <diasdelmes>=<num_dia>|<num_dia>'-'<num_dia> |"*"
- <num_dia>=número del 1 al 31
- <hora>=número del 0 al 23
- <minuto>=número del 0 al 59
- <meses>=<nombre_mes>|<nombre_mes>'-'<nombre_mes>|"*"
- <nombre_mes>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Los nombres de los días y meses no distinguen entre mayúsculas y minúsculas.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

La sentencia anterior transfiere el procesamiento a la extensión s en el contexto normalhours si la llamada es entre las 08:00 AM y las 06:00 PM de lunes a viernes.

## Usando DISA para obtener un nuevo tono de marcado

DISA, o “direct inward system access”, es un sistema que permite a los usuarios recibir un segundo tono de marcado. Permite a los usuarios marcar de nuevo a otro destino. A menudo es utilizado por técnicos cuando realizan llamadas de larga distancia para soporte técnico los fines de semana; en lugar de marcar desde sus hogares directamente al destino, llaman al número DISA de la oficina, reciben un tono de marcado y luego llaman al destino. Los cargos de larga distancia corren a cargo de la empresa en lugar del teléfono del hogar.

```
DISA(passcode[,context])
DISA(password-file[,context])
```

Ejemplo:

```
exten => s,1,DISA(no-password,default)
```

Usando la sentencia anterior, el usuario marca la PBX y, sin requerir ninguna contraseña, recibe un tono de marcado. Cualquier llamada que use DISA será procesada usando el contexto `default`. Los argumentos para esta aplicación incluyen una contraseña global o una contraseña individual dentro de un archivo. Si no se especifica ningún contexto, se asume el contexto `disa`. Si usa un archivo de contraseña, se debe especificar la ruta completa. También se puede especificar un identificador de llamadas para la marcación externa DISA. Ejemplo:

```
numeric-passcode,context,"Flavio" <4830258590>
```

> **[Nota de la 2.ª ed.]** Asterisk 22 usa comas como separadores de argumentos (la forma de barra vertical fue desaprobada en 1.6). La sintaxis completa es `DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])`, y el contexto predeterminado cuando no se da ninguno es `disa` (no "DISA"). Verificado con `core show application DISA` en el laboratorio de Asterisk 22.10.0.

## Limitar llamadas simultáneas

La función GROUP() le permite contar cuántos canales activos tiene en un grupo al mismo tiempo. Ejemplo: Usted tiene una sucursal en Río de Janeiro, donde los teléfonos siguen el patrón “_214X”. Esta ubicación es atendida por una línea dedicada, con 64K reservados para el ancho de banda de voz. En este caso, el número máximo de llamadas permitidas es 2 (G.729, 30r.2K por llamada). Para limitar las llamadas a Río a dos:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

El correo de voz es un sistema de respuesta telefónica computarizado que graba mensajes de voz entrantes, guardándolos en el disco o enviándolos por correo electrónico. A veces tiene un directorio donde puede buscar buzones de voz por nombre. En el pasado, los sistemas de correo de voz eran muy caros. Ahora, con la telefonía IP, el correo de voz se está convirtiendo en una característica estándar.

Para configurar el correo de voz, debe seguir los siguientes pasos.

**Paso 1: Edite `voicemail.conf` y establezca los parámetros generales.**

- `format` — códec utilizado para grabar el mensaje (p. ej., wav49, wav, gsm)
- `serveremail` — de quién debería parecer que proviene la notificación por correo electrónico
- `maxmsg` — número máximo de mensajes en el buzón; después de este umbral, los mensajes se descartan
- `maxsecs` — duración máxima de un mensaje de correo de voz, en segundos
- `minsecs` — duración mínima de un mensaje, en segundos; por debajo de este umbral, no se graba ningún mensaje
- `maxsilence` — cuántos segundos de silencio tratar como el final del mensaje

**Paso 2: Edite `voicemail.conf` y cree los buzones de los usuarios.**

### Voicemail.conf

Un buzón se define con una línea por buzón, en la forma:

```
mailboxID => pincode,fullname,email,pager-email,options
```

Los campos son:

- **MailboxID** — generalmente el número de extensión
- **Pincode** — contraseña para acceder al sistema de correo de voz
- **Full name** — utilizado por la aplicación de directorio
- **E-mail** — dirección para la notificación de correo de voz
- **Pager e-mail** — dirección para la notificación a través de una puerta de enlace SMS o buscapersonas
- **Options** — opciones por buzón (las mismas opciones que en `[general]`, pero aplicadas a este buzón)

El correo de voz tiene varias opciones que controlan su comportamiento. Por ahora, nos ceñiremos a las opciones predeterminadas y nos concentraremos en la definición del buzón. Después de la sección `[general]` en el archivo, comienza a configurar los ID de buzón, cada uno en su propio contexto. Ejemplo:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Por favor, verifique las opciones avanzadas en el archivo `voicemail.conf`.

**Paso 3: Configure el archivo `extensions.conf`.**

A continuación, tiene las instrucciones para crear la subrutina y la llamada que implementan el correo de voz en `extensions.conf`. Usamos el valor de la variable de canal `${DIALSTATUS}` para redirigir el flujo de llamadas al menú de correo de voz adecuado.

### Subrutina de Voicemail

## Usando la aplicación Voicemailmain()

La aplicación voicemailmain() se utiliza para configurar el buzón de correo de voz. Los usuarios pueden marcar la aplicación, grabar su saludo y escuchar su correo de voz. Para llamar a la aplicación en el dialplan, use:

```
exten=>9000,1,VoiceMailMain()
```

A continuación encontrará una lista de las opciones disponibles para la aplicación.

### Sintaxis de la aplicación Voicemail

Esta aplicación permite a la parte que llama dejar un mensaje para una lista especificada de buzones. Cuando se especifican varios buzones, el saludo se tomará del primer buzón especificado. La ejecución del dialplan se detendrá si el buzón especificado no existe. La sintaxis se muestra a continuación:

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

En todos los casos, el archivo beep.gsm se reproducirá antes de que comience la grabación. Los mensajes de correo de voz se almacenarán en el directorio inbox.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Si una persona que llama presiona 0 (cero) durante el anuncio, se moverá a la extensión ‘o’ (out) en el contexto actual de voicemail. Esto se puede usar para salir al operador. Si durante la grabación la persona que llama presiona # o el límite de silencio se agota, la grabación se detiene y la llamada pasa a la siguiente prioridad. Asegúrese de manejar la llamada después de que se reproduzca el correo de voz, como se muestra a continuación.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Etiquetar mensajes de correo de voz como urgentes

Puede etiquetar algunos mensajes como “urgentes”. Hay dos métodos disponibles para esto:

- Pase la opción ‘U’ en la aplicación voicemail()
- Especifique review=yes en el archivo voicemail.conf. Si usa esta opción, el usuario podrá etiquetar el mensaje como urgente después de grabar las instrucciones de voz.

## Enviar correo de voz a correo electrónico

En algunos casos (como el mío), simplemente no usamos la aplicación voicemailmain() para leer el correo. Es más simple y práctico enviar todos los mensajes al correo electrónico con el audio adjunto. Usando los parámetros ‘attach’ y ‘delete’, puede enviar todos los correos al correo electrónico y eliminarlos del buzón.

```
attach=yes
delete=yes
```

Para enviar el correo de voz al correo electrónico, la aplicación de correo de voz utiliza el agente de transferencia de mensajes (MTA), un componente de su sistema operativo. Debian usa Exim como MTA. La aplicación que envía el correo electrónico se define en el parámetro ‘mailcmd’.

```
mailcmd =/usr/sbin/sendmail -t
```

En la distribución Debian de Linux, el MTA es Exim. Para configurar Exim en Debian, use:

```
dpkg-reconfigure exim4-config
```

Puede optar por hacer que su MTA envíe un correo electrónico directamente a través de SMTP o un smarthost (generalmente el servidor de correo de su empresa). Verifique con su administrador de correo electrónico la mejor manera de enviar correos electrónicos desde el servidor Asterisk a su servidor de correo electrónico.

## Personalizar el mensaje de correo electrónico

Puede controlar cómo se envían los mensajes configurando las siguientes variables: Variables para el asunto y el cuerpo del correo electrónico:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

El cuerpo y el asunto del correo electrónico se crean a partir de una plantilla que usted configura en la sección `[general]` de `voicemail.conf`. Puede modificar tanto el cuerpo como el asunto, pero el límite de tamaño del mensaje es de 512 bytes. En la plantilla, `\n` inserta una nueva línea y `\t` inserta una tabulación.

El ejemplo `emailsubject` a continuación es sencillo. El ejemplo `emailbody` es muy cercano al predeterminado; el predeterminado muestra solo el CIDNAME cuando no es nulo, de lo contrario el CIDNUM, o "an unknown caller" cuando ambos son nulos.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interfaz web de Voicemail

Hay un script de Perl en la distribución fuente llamado `vmail.cgi`, ubicado en `contrib/scripts/vmail.cgi` en el árbol de fuentes de Asterisk (todavía se envía con Asterisk 22). El comando `make install` no instala esta interfaz; debe ejecutar `make webvmail` desde el directorio fuente. Este script requiere que el intérprete de comandos Perl y un servidor web (como Apache) estén instalados en el servidor.

```
make webvmail
```

El objetivo `make webvmail` instala el script (setuid root) en el directorio CGI de su servidor web (`HTTP_CGIDIR`) y copia las imágenes de soporte desde `images/*.gif` a `HTTP_DOCSDIR/_asterisk` (por defecto `/var/www/html/_asterisk`). Si esas rutas no coinciden con el diseño de su servidor web, edite las variables `HTTP_CGIDIR` y `HTTP_DOCSDIR` en el `Makefile` de nivel superior antes de ejecutar el objetivo.

## Notificación de Voicemail

Puede configurar el correo de voz para enviar un mensaje de notificación a su teléfono cuando tenga un nuevo correo de voz. En Asterisk 22, la indicación de mensaje en espera (MWI) funciona con teléfonos PJSIP y SIP, así como con teléfonos DAHDI. Para indicar un correo de voz no escuchado, una luz indicadora puede parpadear o el teléfono puede reproducir un tono de obturador. Debe configurar el buzón en el archivo de configuración del canal correspondiente. Ejemplo: `pjsip.conf` (en la sección endpoint):

```
mailboxes=8590
```

> **[Nota de la 2.ª ed.]** En PJSIP, la sugerencia de buzón se establece con la opción `mailboxes` dentro de la sección `[endpoint]` de `pjsip.conf`, en lugar de `mailbox=` en `sip.conf`. Las suscripciones MWI son manejadas por `res_pjsip_mwi`. Verifique la sintaxis de configuración exacta para Asterisk 22.

![La interfaz web de Comedian Mail (`vmail.cgi`): el inicio de sesión de Asterisk Web-Voicemail — ingrese su buzón y contraseña para reproducir, guardar, reenviar o eliminar el correo de voz desde un navegador. Todavía se envía con Asterisk 22 y se instala con `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Laboratorio: Notificación de mensajes en el teléfono

Este laboratorio se probó usando un softphone SIP. 1. Edite `pjsip.conf` y agregue `mailboxes=4401` en la sección endpoint para el dispositivo llamado 4401. 2. Edite el extensions.conf y cree una extensión para grabar un correo de voz en las extensiones 4401.

```
exten=9008,n,voicemail(b4401)
```

3. Vaya a la consola CLI y recargue. 4. En el softphone SipPulse, abra la configuración de la cuenta SIP y habilite la verificación de correo de voz (message-waiting) para la cuenta. 5. Marque 9008 y deje un mensaje. 6. Observe el icono de mensaje en el teléfono.

## Usando la aplicación de directorio

Esta aplicación le permite encontrar rápidamente un usuario para marcar. La lista de nombres y las extensiones correspondientes se recuperan del archivo de configuración de correo de voz voicemail.conf. La sintaxis para la aplicación se puede mostrar usando core show application directory:

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

### Laboratorio: Usando la aplicación de directorio

1. Edite el archivo voicemail.conf para agregar dos extensiones en el dialplan

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Cree estas extensiones en su dialplan

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Vaya a la consola y recargue 4. Marque 9006 y grabe un nombre para cada extensión (4400, 4401) 5. Marque 9007 y seleccione las tres letras del apellido para una extensión (Eas=327). Si esta es la opción correcta, presione ‘1’ para transferir al nombre.

## Laboratorio: Poniéndolo todo junto

Hasta ahora, ha aprendido varios conceptos de dialplan. Pongamos todas las aplicaciones, funciones y conceptos en un ejemplo de dialplan para que pueda entender cómo se usan juntos. Vamos a guiarlo a través de toda la configuración de la PBX para el escenario a continuación.

- 4 trunks analógicos
- 16 extensiones basadas en SIP
- 3 clases de servicio:
    - restrict (interno, local y 1-800)
    - ld (larga distancia)
    - ldi (internacional)
- Mensaje fuera de horario
- Operadora automática

### Paso 1 – Configurando canales

Trunks analógicos (chan_dahdi.conf) Primero, configuraremos los trunks analógicos en el archivo de configuración del canal DAHDI chan_dahdi.conf. En este caso, usaremos una tarjeta T400P Digium con 4 interfaces FXO. Supongamos que el controlador ya está cargado y el archivo de configuración del controlador (/etc/dahdi/system.conf) está configurado correctamente.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

Canales SIP (pjsip.conf) Hemos elegido la numeración del dialplan de 2000 a 2099. Se utilizarán dos códecs: G.729 y G.711 ulaw. El primero se utilizará para teléfonos que usan Asterisk a través de Internet o WAN, mientras que el segundo se utilizará para teléfonos que usan la red local. En `pjsip.conf`, arbitraremos qué dispositivos pertenecerán a cada clase de servicio (restrict, ld, ldi). Para reducir la vulnerabilidad a ataques de fuerza bruta, usaremos las direcciones MAC de los teléfonos como nombres de dispositivo. ¡Recomiendo encarecidamente que use contraseñas seguras para evitar ataques de fuerza bruta!

Definimos un transporte y tres plantillas reutilizables — una base de endpoint con los códecs compartidos, una autenticación userpass y un AOR de contacto único — luego adjuntamos cada dispositivo a las plantillas y anulamos solo lo que difiere (su contexto de clase de servicio y credenciales). `host=dynamic` se convierte en un AOR contra el cual se registra el teléfono, y `directmedia` se convierte en `direct_media`:

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

[auth-userpass](!)
type=auth
auth_type=userpass

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-userpass)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-userpass)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-userpass)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Paso 2 – Configurar el dialplan

Ahora comencemos a configurar el extensions.conf. Definir extensiones internas y marcación local

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Definir LD (larga distancia)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Definir llamadas internacionales

```
[ldi)
include=> ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Paso 3 - Recibir llamadas usando una operadora automática

Para recibir llamadas, use dos contextos. El primero es para la operación en horario normal, donde la llamada será recibida por una operadora automática. El segundo es para fuera de horario, donde la persona que llama recibirá un mensaje como “ha llamado a la empresa XYZ, nuestro horario normal es de 08:00 AM a 06:00 PM; si conoce el número de extensión de destino puede intentar marcarlo ahora o colgar”. Menús: Horario normal, Fuera de horario En los menús a continuación, el sistema reproducirá un mensaje advirtiendo a la persona que llama que se contactó a la empresa fuera del horario laboral habitual, permitiendo a la persona que llama marcar el número de extensión de destino (alguien puede estar trabajando fuera del horario laboral habitual).

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

Menús: Principal y Ventas Durante el horario laboral normal, la llamada es contestada por un menú de operadora automática, recibiendo un mensaje como “bienvenido a la empresa XYZ; marque 1 para ventas, 2 para soporte técnico, 3 para capacitación, o el número de extensión deseado”.

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

Con todas estas sentencias, la funcionalidad de su plan de marcado ya está lista. En la siguiente sección, demostraremos cómo operar la PBX.

## Resumen

En este capítulo, ha aprendido cómo recibir llamadas usando un IVR o una operadora automática. Ha estudiado el concepto de inclusión de contextos y ha implementado algunos ejemplos. Se utilizaron subrutinas para evitar la escritura repetitiva, y la base de datos de Asterisk basada en el motor Berkley DB se utilizó para funciones que requieren almacenamiento de datos (p. ej., desvío de llamadas, no molestar, listas negras). Finalmente, ha aprendido cómo implementar el comportamiento fuera de horario y ha implementado un dialplan completo utilizando estos conceptos.

## Cuestionario

1. Una inclusión de contexto dependiente del tiempo usa la forma `include => context,<times>,<weekdays>,<mdays>,<months>`. ¿Qué hace `include => normalhours,08:00-18:00,mon-fri,*,*`?
   - A. Ejecutar las extensiones de lunes a viernes, de 08:00 a 18:00
   - B. Ejecutar las opciones todos los días en todos los meses
   - C. Nada; el formato no es válido
2. En el Asterisk moderno (incluyendo Asterisk 22), los campos de un `include =>` basado en el tiempo y de `GotoIfTime()` están separados por qué carácter?
   - A. La barra vertical `|`
   - B. La coma `,`
   - C. El punto y coma `;`
   - D. La barra diagonal `/`
3. Para marcar varios canales a la vez (haciéndolos sonar simultáneamente), los separa dentro de `Dial()` con el carácter ___.
4. Un menú de voz que reproduce un mensaje mientras espera que la persona que llama marque una extensión generalmente se crea con la aplicación ___.
5. Puede incluir el contenido de otro archivo dentro de `extensions.conf` usando la sentencia ___ (nota: esto es diferente de la sentencia de contexto `include =>`).
6. En Asterisk 22, la base de datos AstDB incorporada está respaldada por:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Cuando usa `Dial(type1/identifier1&type2/identifier2)`, Asterisk marca cada canal en secuencia, esperando 20 segundos entre ellos.
   - A. Falso
   - B. Verdadero
8. Con la aplicación Background(), debe esperar hasta que el mensaje termine de reproducirse antes de poder presionar un dígito DTMF para elegir una opción.
   - A. Falso
   - B. Verdadero
9. Dada la sintaxis `Goto([[context,]extension,]priority)`, ¿cuáles de las siguientes son invocaciones válidas de la aplicación Goto()? (marque todas las que correspondan)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Para eliminar una sola clave de AstDB en el dialplan de Asterisk 22, usa:
    - A. La aplicación `DBdel()`
    - B. La función `DB_DELETE()`
    - C. La aplicación `DBdeltree()`
    - D. La aplicación `LookupBlacklist()`

**Respuestas:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
