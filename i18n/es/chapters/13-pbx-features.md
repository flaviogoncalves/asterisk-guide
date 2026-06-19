# Uso de funciones de PBX

En los sistemas SIP, la mayoría de las funciones telefónicas se implementan en el endpoint. Existe una gran variedad de teléfonos SIP y fabricantes, y la interoperabilidad no está garantizada. El equipo de desarrollo de Asterisk ha hecho un trabajo increíble al implementar la mayoría de las funciones en la propia PBX, haciendo que Asterisk sea casi independiente del endpoint. Sin embargo, a veces encontrará que la misma función es realizada tanto por el teléfono como por el propio Asterisk. La integración del teléfono y la PBX es la siguiente frontera en usabilidad y donde los sistemas propietarios se están enfocando en este momento. En este capítulo, aprenderá a utilizar la mayoría de estas funciones.

## Objetivos

Al final de este capítulo, usted será capaz de comprender y utilizar:

- Estacionamiento de llamadas (Call Parking)
- Captura de llamadas (Call Pickup)
- Transferencia de llamadas (Call Transfer)
- Conferencia de llamadas (ConfBridge)
- Grabación de llamadas (Call Recording)
- Música en espera (Music on hold)

## Dónde se implementan las funciones

Ante todo, es importante entender cuándo se están ejecutando las funciones de la PBX frente a cuándo el teléfono está haciendo todo el trabajo. Por ejemplo, puede transferir una llamada usando el botón TRANSFER en el teléfono o marcando # (transferencia incondicional ejecutada por la propia PBX).

## Funciones implementadas por Asterisk

Estas funciones son implementadas en la PBX por el código de Asterisk:

- Música en espera
- Estacionamiento de llamadas
- Captura de llamadas
- Grabación de llamadas
- Sala de conferencias ConfBridge
- Transferencia de llamadas (ciega y consultiva)

## Funciones usualmente implementadas por el dialplan

Estas funciones necesitan ser programadas en el dialplan de Asterisk (extensions.conf):

- Desvío de llamadas si está ocupado
- Desvío de llamadas inmediato
- Desvío de llamadas si no hay respuesta
- Filtrado de llamadas (lista negra)
- No molestar
- Rellamada

## Funciones usualmente implementadas por el teléfono

Estas funciones son implementadas por el firmware del teléfono:

![Dónde se implementan usualmente las funciones de PBX: en el propio Asterisk, en el dialplan o en el teléfono](../images/13-pbx-features-fig01.png)

- Llamada en espera
- Transferencia ciega
- Transferencia consultiva
- Conferencia tripartita
- Indicador de mensaje en espera

## El archivo de configuración de funciones

Algunas de las funciones presentadas en este capítulo se configuran en el archivo de configuración features.conf. Es posible cambiar el comportamiento de algunas funciones modificando este archivo. Hemos incluido el extracto relevante a continuación. En las siguientes secciones de este capítulo, describiremos cada función. Extracto del archivo de ejemplo (Asterisk 22)

![La sección `[featuremap]` de features.conf, con los códigos de función DTMF predeterminados](../images/13-pbx-features-fig02.png)

> **[Nota de la 2da ed.]** A partir de Asterisk 12+, el estacionamiento de llamadas se trasladó fuera de `features.conf`/`app_features` a su propio módulo `res_parking` con configuración en `res_parking.conf`. El bloque de parking-lot a continuación (parkext, parkpos, context, parkingtime, etc.) reside en `res_parking.conf` y se muestra usando la sintaxis de Asterisk 22 `res_parking.conf.sample`. La sección `[featuremap]` (los códigos de función DTMF, incluyendo `parkcall`) permanece en `features.conf`.

Las opciones de parking-lot residen en `res_parking.conf`. Un parking lot llamado `default` siempre existe, incluso si no está presente en el archivo de configuración. El extracto a continuación está tomado de Asterisk 22 `res_parking.conf.sample`:

```
; res_parking.conf
[default]                       ; Default Parking Lot
parkext => 700                  ; What extension to dial to park. (optional; if
                                ; specified, extensions will be created for parkext and
                                ; the whole range of parkpos)
parkpos => 701-720              ; What range of parking spaces to use - must be numeric.
                                ; Creates these spaces as extensions if parkext is set.
context => parkedcalls          ; Which context parked calls and the default park
                                ; extension are created in
;parkingtime => 45             ; Number of seconds a call can be parked before returning
;comebacktoorigin = yes        ; When a parked call times out, attempt to send it back to
                               ; the peer that parked it (default is yes)
;courtesytone = beep           ; Sound file to play when someone picks up a parked call
;parkedplay = caller           ; Who to play courtesytone to: parked, caller, both (default caller)
;parkedcalltransfers = caller  ; Enable DTMF transfers when picking up a parked call (default no)
;parkedcallreparking = caller  ; Enable DTMF parking when picking up a parked call (default no)
;parkedcallhangup = caller     ; Enable DTMF hangups when picking up a parked call (default no)
;findslot => next              ; 'next' uses the next space after the most recently used one;
                               ; 'first' (default) uses the lowest-numbered space available
;parkedmusicclass = default    ; MOH class to use for the parked channel
```

Los códigos de función DTMF (incluyendo el de un solo paso `parkcall`) permanecen en la sección `[featuremap]` de `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t
option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option
in the Dial() or Queue() app call!
;automon => *1                  ; One Touch Record a.k.a. Touch Monitor -- Make sure to set the W
and/or w option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Transferencia de llamadas

La transferencia de llamadas puede ser implementada por el teléfono, por un ATA o por el propio Asterisk. Consulte el manual de su teléfono para entender cómo se transfieren las llamadas. Si su teléfono no admite la transferencia de llamadas, puede usar Asterisk para realizar esta tarea. La transferencia de llamadas se implementa de dos maneras diferentes. La primera forma es usar la función de transferencia ciega: marque # seguido del número al que se va a transferir. A veces usará la función de transferencia de su teléfono IP o softphone IP. Puede cambiar el carácter de transferencia editando el parámetro blindxfer en el archivo features.conf. Puede habilitar la transferencia asistida en Asterisk eliminando el ; antes del parámetro atxfer en el archivo features.conf. Durante una conversación, presionaría *2. Asterisk dirá “transfer” y le dará tono de marcado. La persona que llama es enviada a música en espera. Después de hablar con la persona de destino y colgar el teléfono, el sistema conecta a la persona que llama con el destino.

![Transferencia de llamadas: los pasos para una transferencia ciega (presione # durante la llamada) y una transferencia asistida (presione *2)](../images/13-pbx-features-fig03.png)

### Lista de tareas de configuración

1. Si el teléfono está basado en SIP, asegúrese de que la opción directmedia sea igual a no o use una opción t o T en la aplicación dial()

## Estacionamiento de llamadas

Esta función se utiliza para estacionar una llamada. Esto ayuda, por ejemplo, cuando está respondiendo una llamada telefónica fuera de su oficina y desea transferir la llamada de regreso a su escritorio. Puede lograr esto estacionando la llamada en una extension. Una vez que llegue a su escritorio, simplemente marque el número de la extension de estacionamiento para recuperar la llamada.

![Estacionamiento de llamadas: marque 700 para estacionar una llamada en el primer espacio libre (701–720); Asterisk anuncia el espacio, el cual usted marca desde cualquier teléfono para recuperar la llamada](../images/13-pbx-features-fig04.png)

De forma predeterminada, la extension 700 se utiliza para estacionar una llamada. En medio de una conversación, presione # para transferir la llamada a la extension 700. Ahora Asterisk anunciará su extension de estacionamiento, como 701 o 702. Cuelgue el teléfono y la persona que llama quedará en espera. Vaya al teléfono de su escritorio y marque la extension de estacionamiento anunciada para recuperar la llamada. Si la persona que llama permanece estacionada durante mucho tiempo, la función de tiempo de espera (timeout) se activará y la extension marcada originalmente volverá a sonar.

### Lista de tareas de configuración

Siga los pasos a continuación para habilitar el estacionamiento de llamadas. Paso 1: Haga que el parking lot sea accesible desde su dialplan (obligatorio). El `context` del parking lot predeterminado es `parkedcalls` (configurado en `res_parking.conf`). Incluya ese context en el context desde el cual marcan sus teléfonos, en `extensions.conf`:

```
include => parkedcalls
```

Paso 2: Pruebe la función de estacionamiento de llamadas marcando #700. Notas:

- La extension de estacionamiento no se mostrará en el comando CLI dialplan show.
- Es necesario recargar el módulo de estacionamiento después de cambiar el archivo de configuración de estacionamiento: `module reload res_parking.so`. Para cambios en features.conf, `module reload features.so`.
- Para estacionar una llamada, necesita transferir a #700. Verifique las opciones t y T en la aplicación dial().

## Captura de llamadas

La captura de llamadas le permite capturar una llamada de un colega en el mismo grupo de llamadas. Esto ayudaría a evitar, por ejemplo, tener que levantarse para atender una llamada que está sonando para otra persona en su oficina, pero que no está presente. Marcando *8, puede capturar una llamada dentro de su grupo de llamadas. Este número puede ser modificado en el

```
features.conf file.
```

![Captura de llamadas: los miembros solo pueden capturar llamadas dentro de su propio grupo; el operador (pickupgroup=1,2,3) puede capturar llamadas de cada grupo](../images/13-pbx-features-fig05.png)

### Lista de tareas de configuración

Siga los pasos a continuación para configurar la función de captura de llamadas. Paso 1: Configure un grupo de llamadas para sus extensiones. Esto se hace en el archivo de configuración del canal (pjsip.conf, iax.conf, chan_dahdi.conf). Para endpoints PJSIP, configure `call_group` y `pickup_group` en la sección de endpoint de `pjsip.conf` (pjsip.conf usa nombres de opciones en snake_case). Esta tarea es obligatoria.

Para PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Paso 2: Cambie el número de la función de captura de llamadas (opcional).

```
pickupexten=*8; Configures the call pickup extension
```

## Conferencia (conferencia de llamadas)

Existen diferentes formas de implementar una conferencia en Asterisk. La primera opción es simplemente usar la capacidad de conferencia tripartita del teléfono. Al usar esta función en el teléfono, no requiere ningún soporte en el propio servidor. Sin embargo, cuando desea una conferencia con más de 3 personas, debe ejecutar una sala de conferencias. La aplicación de conferencia moderna de Asterisk es ConfBridge (`app_confbridge`).

ConfBridge admite conferencias de voz HD y videoconferencias. Existen algunas limitaciones para la videoconferencia, como la ausencia de transcodificación: todos los participantes deben usar el mismo codec y perfil. La videoconferencia utiliza un modo de seguimiento del hablante (follow-the-talker), mostrando la imagen de la última persona en hablar. Puede configurar fácilmente nuevos menús DTMF en ConfBridge.

> **[Nota de la 2da ed.]** MeetMe (`app_meetme`) fue **obsoleto en Asterisk 19** y estaba programado para su eliminación en Asterisk 21, pero dicha eliminación se pausó (a petición del proyecto ViciDial). El código fuente del módulo todavía se envía con Asterisk 22, pero requiere DAHDI y **no se compila en la compilación predeterminada de Asterisk 22**: una instalación estándar no tiene `app_meetme.so` y la aplicación `MeetMe()` no está disponible. Todas las nuevas implementaciones de salas de conferencias deben usar ConfBridge. La sección de MeetMe a continuación se conserva solo como referencia histórica.

### Confbridge

Para iniciar una sala de conferencias, la sintaxis se enumera a continuación.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Para obtener una descripción completa del comando, puede usar core show application confbridge.

![Salida de `core show application confbridge`, mostrando la sinopsis, la sintaxis y los argumentos bridge_profile, user_profile y menu](../images/13-pbx-features-fig06.png)

Como puede ver arriba, hay tres secciones importantes: Bridge_profile: Usted define el perfil en el archivo confbridge.conf. Allí puede seleccionar el número máximo de participantes, grabación, video_mode y muchos otros parámetros del bridge.

No tiene sentido reproducir el archivo de ejemplo completo aquí, así que permítame darle un ejemplo simple sobre cómo configurar un bridge_profile en el archivo confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

User_profile: Aquí define opciones que son específicas por usuario, como si el usuario es administrador o no. La música en espera y muchas otras opciones se pueden configurar por usuario. Ejemplo:

```
[admin_user]
type=user
admin=yes
```

Menu: En la sección de menú puede definir su mapeo de teclado para la aplicación, dónde alternar entre silenciar y reactivar el audio. Consulte el archivo confbridge.conf para ver las opciones. Ejemplo:

```
[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
4=decrease_talking_volume
5=increase_talking_volume
6=leave_conference
```

#### Funciones de Confbridge

Las opciones del bridge de conferencia se pueden pasar dinámicamente en el dialplan usando la función CONFBRIDGE(). Vea los ejemplos a continuación:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

## Meetme (Legado — obsoleto, no se compila por defecto en Asterisk 22)

> **[Nota de la 2da ed.]** `app_meetme` fue obsoleto en Asterisk 19. Su eliminación planificada en Asterisk 21 se pausó, por lo que el código fuente todavía se envía en Asterisk 22, pero el módulo no se compila en la compilación predeterminada de Asterisk 22 (depende de DAHDI). Por lo tanto, una instalación estándar de Asterisk 22 no tiene la aplicación `MeetMe()`. El contenido a continuación se mantiene como referencia histórica y para lectores que actualizan desde sistemas más antiguos. **Para nuevas instalaciones, use ConfBridge (ver arriba).** La dependencia de DAHDI y el módulo `dahdi_dummy` no son necesarios para ConfBridge.

Alternativamente, en versiones anteriores de Asterisk, podía usar la aplicación meetme(). Meetme es un bridge de conferencia que es muy fácil de usar. Recuerde, meetme fue obsoleto en Asterisk 19 y depende del módulo DAHDI para la sincronización.

![Tipos de conferencia MeetMe — conferencia de un solo hablante, protegida por contraseña y dinámica — todas requieren una fuente de temporización Zaptel/DAHDI](../images/13-pbx-features-fig07.png)

### La aplicación meetme()

Usando el comando CLI meetme show, puede obtener la descripción anterior. Para usar meetme, necesita compilar los controladores DAHDI y tener al menos un módulo de kernel DAHDI cargado. Si no tiene al menos una tarjeta DAHDI instalada, cargue el módulo de kernel dahdi_dummy para proporcionar una fuente de temporización. Descripción:

![La aplicación MeetMe(): sintaxis `MeetMe([confno][,[options][,pin]])` y sus principales flags de opciones](../images/13-pbx-features-fig08.png)

La aplicación meetme() lleva al usuario a una conferencia meetme especificada. Si se omite el número de conferencia, se le pedirá al usuario que ingrese uno. El usuario puede abandonar la conferencia colgando o, si se especifica la opción p, presionando #. Tenga en cuenta: Los módulos de kernel DAHDI y al menos un controlador de hardware (o dahdi_dummy) deben estar presentes para que la conferencia funcione correctamente. Además, el controlador de canal chan_dahdi debe estar cargado para que las opciones i y r funcionen en absoluto.

> **[Nota de la 2da ed.]** Las listas de flags de opciones y comandos de administración que siguen describen la interfaz heredada `app_meetme` y reflejan la documentación histórica de `MeetMe()`/`MeetMeAdmin()`. Debido a que `app_meetme` no se compila en la instalación predeterminada de Asterisk 22, estos flags no pueden confirmarse contra un sistema Asterisk 22 en ejecución; se reproducen para lectores que mantienen implementaciones antiguas. En Asterisk 22, use ConfBridge y la función de dialplan `CONFBRIDGE()` en su lugar.

La cadena de opciones puede contener cero, una o más de los siguientes caracteres:

- 'a' -- establece el modo administrador
- 'A' -- establece el modo marcado
- 'b' – ejecuta el script AGI especificado en ${MEETME_AGI_BACKGROUND}Predeterminado: conf- background.agi (Nota: Esto no funciona con canales que no sean DAHDI en la misma conferencia)
- 'c' -- anuncia el conteo de usuario(s) al unirse a una conferencia
- 'd' -- agrega conferencia dinámicamente
- 'D' -- agrega conferencia dinámicamente, solicitando un PIN
- 'e' -- selecciona una conferencia vacía
- 'E' -- selecciona una conferencia vacía sin PIN
- 'i' -- anuncia un usuario uniéndose/saliendo con revisión
- 'I' -- anuncia un usuario uniéndose/saliendo sin revisión
- 'l' -- establece el modo solo escucha (Listen only, sin hablar)
- 'm' -- establece silenciado inicialmente
- 'M' -- habilita música en espera cuando la conferencia tiene un solo llamante
- 'o' -- establece la optimización del hablante, que trata a los hablantes que no están hablando como silenciados, lo que significa (a) no se realiza codificación en la transmisión y (b) el audio recibido que no está registrado como hablando se omite, sin causar acumulación de ruido de fondo
- 'p' -- permite a los usuarios salir de la conferencia presionando '#'
- 'P' -- siempre solicita el PIN incluso si está especificado
- 'q' -- modo silencioso (no reproducir sonidos de entrada/salida)
- 'r' -- Graba la conferencia (graba como ${MEETME_RECORDINGFILE}usando el formato ${MEETME_RECORDINGFORMAT}). El nombre de archivo predeterminado es meetme-conf-rec- ${CONFNO}-${UNIQUEID} y el formato predeterminado es wav.
- 's' -- Presenta el menú (usuario o administrador) cuando se recibe '*' ('send' al menú)
- 't' -- establece el modo solo hablar. (Talk only, sin escuchar)
- 'T' -- establece la detección de hablante (enviado a la interfaz del administrador y a la lista de meetme)
- 'w[(<secs>)]' -- espera hasta que el usuario marcado entre a la conferencia
- 'x' -- cierra la conferencia cuando el último usuario marcado sale
- 'X' -- permite al usuario salir de la conferencia ingresando una extension válida de un solo dígito ${MEETME_EXIT_CONTEXT} o el context actual si esa variable no está definida.
- '1' -- no reproduce el mensaje cuando entra la primera persona

### Archivo de configuración de Meetme

Este archivo se utiliza para configurar la aplicación meetme. Por ejemplo:

```
;
; Configuration file for MeetMe simple conference rooms for Asterisk of course.
;
; This configuration file is read every time you call app meetme()
[general]
;audiobuffers=32        ; The number of 20ms audio buffers to be used
                        ; when feeding audio frames from non-DAHDI channels
                        ; into the conference; larger numbers will allow
                        ; for the conference to 'de-jitter' audio that arrives
                        ; at different timing than the conference's timing
                        ; source, but can also allow for latency in hearing
                        ; the audio from the speaker. Minimum value is 2,
                        ; maximum value is 32.
;
[rooms]
;
; Usage is conf => confno[,pin][,adminpin]
;
conf=>9000
conf=>9001,123456
```

No es necesario usar reload o restart para que Asterisk vea los cambios en el archivo meetme.conf.

### Aplicaciones relacionadas con Meetme

La aplicación meetme() tiene otras dos aplicaciones de soporte.

```
MeetMeCount(confno[|var])
```

Esto reproduce el número de usuarios en la conferencia. Si se especifica una variable, no reproduce el mensaje pero establece el número de usuarios en ella.

```
MeetMeAdmin(confno,command,[user]):
```

Ejecute el comando de administración para una conferencia:

- 'e' -- Expulsa al último usuario que se unió
- 'k' -- Expulsa a un usuario de la conferencia
- 'K' -- Expulsa a todos los usuarios de la conferencia
- 'l' -- Desbloquea la conferencia
- 'L' -- Bloquea la conferencia
- 'm' -- Reactiva el audio de un usuario
- 'M' -- Silencia a un usuario
- 'n' -- Reactiva el audio de todos los usuarios en la conferencia
- 'N' -- Silencia a todos los usuarios no administradores en la conferencia
- 'r' -- Restablece la configuración de volumen de un usuario
- 'R' -- Restablece la configuración de volumen de todos los usuarios
- 's' -- Reduce el volumen de habla de toda la conferencia
- 'S' -- Aumenta el volumen de habla de toda la conferencia
- 't' -- Reduce el volumen de habla de un usuario
- 'T' -- Reduce el volumen de habla de todos los usuarios
- 'u' -- Reduce el volumen de escucha de un usuario
- 'U' -- Reduce el volumen de escucha de todos los usuarios
- 'v' -- Reduce el volumen de escucha de toda la conferencia
- 'V' -- Aumenta el volumen de escucha de toda la conferencia

### Lista de tareas de configuración de Meetme

Siga los pasos a continuación para configurar la aplicación de conferencia meetme. Paso 1: Elija la extension para la sala Meetme (obligatorio) Paso 2: Edite el archivo meetme.conf para configurar las contraseñas (opcional)

### Ejemplos

Ejemplo #1: Sala meetme simple 1. En el archivo extensions.conf, cree la sala de conferencias 101

```
exten=>500,1,MeetMe(101,,123456)
```

2. En el archivo meetme.conf, establezca la contraseña para la sala 101. Nota importante: La aplicación meetme() necesita un temporizador para funcionar. Si no tiene hardware de Digium instalado y configurado, use dahdi_dummy como fuente de temporización.

## Grabación de llamadas

Hay varias formas de grabar una llamada en Asterisk. Puede usar la aplicación mixmonitor() para grabar llamadas fácilmente.

### Uso de la aplicación mixmonitor

La aplicación mixmonitor graba el audio en el canal actual en el archivo especificado. Si el nombre de archivo es una ruta absoluta, usa esa ruta. De lo contrario, crea el archivo en el directorio de monitoreo configurado desde asterisk.conf.

![La aplicación MixMonitor(): graba y mezcla el audio de un canal en un archivo, con opciones para adjuntar, solo puenteado y ajuste de volumen](../images/13-pbx-features-fig09.png)

### Mixmonitor()

Grabe una llamada y mezcle el audio durante la grabación [Descripción] MixMonitor(<file>.<ext>[|<options>[|<command>]]) Graba el audio en el canal actual en el archivo especificado. opciones: a- Adjuntar al archivo en lugar de sobrescribirlo. b-Solo guardar audio en el archivo mientras el canal está puenteado. Nota: no incluye conferencias. v(<x>) - Ajuste el volumen escuchado por un factor de <x> V(<x>) - Ajuste el volumen hablado por un factor de <x> W(<x>) - Ajuste tanto los volúmenes escuchados como hablados Opciones válidas:

- a - Adjunta al archivo en lugar de sobrescribirlo.
- b - Solo guarda audio en el archivo mientras el canal está puenteado.
- Nota: no incluye conferencias.
- v(<x>) - Ajusta el volumen audible por un factor de <x> (que va de -4 a 4)
- V(<x>) - Ajusta el volumen hablado por un factor de <x> (que va de -4 a 4)
- W(<x>) - Ajusta tanto los volúmenes audibles como hablados por un factor de <x> (que va de -4 a 4)
- <command> se ejecutará cuando termine la grabación. Cualquier cadena que coincida con ^{X} se desescapará a ${X} y todas las variables se evaluarán en ese momento. La variable MIXMONITOR_FILENAME contendrá el nombre de archivo utilizado para grabar.

Un recurso interesante es automon, que le permite simplemente marcar *1 para comenzar a grabar inmediatamente. Ejemplo:

```
exten=>_4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten=>_4XXX,2,Dial(PJSIP/${EXTEN},20,jtTwW);wW enables the recording.
```

Los canales de audio son entrantes (IN) y salientes (OUT) y se separan en dos archivos distintos en el directorio /var/spool/asterisk/monitor. Ambos archivos se pueden mezclar usando la aplicación sox.

```
debian#soxmix *in.wav *out.wav output.wav
```

Si no desea usar Set() antes de la aplicación Dial(), puede configurar esto en la sección globals:

```
[globals]
DYNAMIC_FEATURES=>automon
```

### Música en espera

La música en espera (MOH) ha cambiado varias veces entre las versiones 1.0, 1.2 y 1.4. En la última versión, MOH es "FILE-BASED" por defecto. En otras palabras, Asterisk suministrará los archivos MOH en formatos como g729, alaw, ulaw y gsm. Por lo tanto, no es necesario transcodificar la música antes de enviarla al canal. Esto ahorra tiempo de procesador, lo cual es una modificación bienvenida para aquellos que trabajan con sistemas de producción. En versiones anteriores, MOH generalmente se proporcionaba mediante MP3 (todavía se puede configurar de esa manera). Proporcionar MOH usando MP3 obliga a Asterisk a transcodificar, gastando valiosa potencia de CPU en el proceso. El nuevo archivo de configuración se muestra a continuación. Tenga en cuenta que la clase predeterminada ahora usa el modo de formato de archivo nativo mode=files. Todos los demás modos están comentados. Cada sección es una clase. La única clase no comentada en este punto es default. Si desea tener diferentes clases para diferentes archivos, deberá crear nuevas secciones (clases).

![La configuración de ejemplo de musiconhold.conf, enumerando los modos MOH válidos (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

```
; Music on Hold -- Sample Configuration
;[samplemp3]
;mode=quietmp3
;directory=/var/lib/asterisk/mohmp3
;
; valid mode options:
; quietmp3      -- default
; mp3           -- loud
; mp3nb         -- unbuffered
; quietmp3nb    -- quiet unbuffered
; custom        -- run a custom application (See examples below)
; files         -- read files from a directory in any Asterisk supported
;                  media format. (See examples below)
;[manual]
;mode=custom
; Note that with mode=custom, a directory is not required, such as when reading
; from a stream.
;directory=/var/lib/asterisk/mohmp3
;application=/usr/bin/mpg123 -q -r 8000 -f 8192 -b 2048 --mono -s
;[ulawstream]
;mode=custom
;application=/usr/bin/streamplayer 192.168.100.52 888
;format=ulaw
; mpg123 on Solaris does not always exit properly; madplay may be a better
; choice
;[solaris]
;mode=custom
;directory=/var/lib/asterisk/mohmp3
;application=/site/sw/bin/madplay -Q -o raw:- --mono -R 8000 -a -12
;
;
; File-based (native) music on hold
;
; This plays files directly from the specified directory, no external
; processes are required. Files are played in normal sorting order
; (same as a sorted directory listing), and no volume or other
; sound adjustments are available. If the file is available in
; the same format as the channel's codec, then it will be played
; without transcoding (same as Playback would do in the dialplan).
; Files can be present in as many formats as you wish, and the
; 'best' format will be chosen at playback time.
;
; NOTE:
; If you are not using "autoload" in modules.conf, then you
; must ensure that the format modules for any formats you wish
; to use are loaded _before_ res_musiconhold. If you do not do
; this, res_musiconhold will skip the files it is not able to
; understand when it loads.
;
[default]
mode=files
directory=/var/lib/asterisk/moh
;
;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes     ; Play the files in a random order
```

### Tareas de configuración de MOH

Ahora, para usar música en espera, configure la clase MOH en los archivos de configuración del canal (chan_dahdi.conf, pjsip.conf, iax.conf, etc.). Para endpoints PJSIP, configure `moh_suggest` en la sección de endpoint de `pjsip.conf` (el nombre de opción heredado `musicclass` se aplica a chan_dahdi y otros controladores de canal, no a PJSIP). Las melodías freeplay instaladas están ahora en formato wav. En el momento de la instalación, puede seleccionar (usando make menuselect) los formatos de archivo MOH disponibles. Si desea agregar nuevos archivos MOH, deberá suministrarlos en los formatos requeridos. Por ejemplo:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

En el dialplan, puede escuchar la MOH usando el siguiente ejemplo:

```
Exten=>100,1,SetMusicOnHold(default)
Exten=>100,2,Dial(DAHDI/2)
```

Para configurar el archivo extensions.conf para probar la MOH:

```
[local]
exten => 6601,1,WaitMusicOnHold(30)
```

## Mapas de aplicaciones

Los mapas de aplicaciones le permiten agregar nuevas funciones usando la sección `[applicationmap]` del archivo features.conf. Suponga que necesita identificar el tipo de cliente al que está respondiendo en un centro de llamadas. Podría crear un mapa de aplicaciones para cada tipo de cliente, que podría contar el número de clientes respondidos por tipo.

## Cuestionario

1. ¿Qué afirmaciones son ciertas sobre el estacionamiento de llamadas?
   - A. Por defecto, la extension 800 se usa para el estacionamiento de llamadas.
   - B. Cuando está lejos de su escritorio y recibe una llamada, puede estacionarla; el sistema anuncia el espacio de estacionamiento y usted marca ese espacio desde cualquier teléfono para recuperar la llamada.
   - C. Por defecto, la extension 700 estaciona una llamada, y las llamadas se estacionan en los espacios 701–720.
   - D. Usted marca 700 para recuperar una llamada estacionada.
2. Para usar la función de captura de llamadas, todas las extensiones deben estar en el mismo ___. Para canales DAHDI, esto se configura en el archivo ___.
3. Al transferir una llamada, puede elegir entre una transferencia ___ , donde no se consulta primero al destino, y una transferencia ___ , donde habla con el destino antes de completarla.
4. Para realizar una transferencia asistida (consultiva) usa la secuencia ___ ; para una transferencia ciega usa ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Para alojar llamadas de conferencia en Asterisk 22, usa la aplicación ___.
6. En ConfBridge, a un participante se le otorgan privilegios de administrador (expulsar, silenciar a otros, bloquear la sala) configurando ___ en su perfil de usuario (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. El mejor formato para música en espera es MP3, porque utiliza muy poca potencia de procesamiento en el servidor Asterisk.
   - A. Verdadero
   - B. Falso
8. Para capturar una llamada de un grupo de llamadas específico, debe estar en el grupo ___ coincidente.
9. Puede grabar una llamada con la aplicación MixMonitor() o la función de un solo toque (automon). Por defecto, automon usa la secuencia DTMF ___.
   - A. *1
   - B. *2
   - C. #3
   - D. #1
10. En ConfBridge, ¿qué opción de perfil de usuario `confbridge.conf` hace que un participante se una silenciado (pueden escuchar la conferencia pero no pueden ser escuchados hasta que se les reactive el audio)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Respuestas:** 1 — B, C · 2 — grupo de captura (pickup group); `chan_dahdi.conf` · 3 — ciega; asistida · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — captura · 9 — A · 10 — A
