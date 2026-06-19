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

Ante todo, es importante entender cuándo se están ejecutando las funciones de la PBX frente a cuándo el teléfono está haciendo todo el trabajo. Por ejemplo, puede transferir una llamada usando el botón TRANSFER del teléfono o marcando # (transferencia incondicional ejecutada por la propia PBX).

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

Algunas de las funciones presentadas en este capítulo se configuran en el archivo de configuración features.conf. Es posible cambiar el comportamiento de algunas funciones modificando este archivo. Hemos incluido el extracto relevante a continuación. En las siguientes secciones de este capítulo, describiremos cada función. Extracto del archivo de muestra (Asterisk 22)

![La sección `[featuremap]` de features.conf, con los códigos de función DTMF predeterminados](../images/13-pbx-features-fig02.png)

Desde Asterisk 12, el estacionamiento de llamadas se trasladó fuera de `features.conf` a su propio módulo, `res_parking`, con configuración en `res_parking.conf`. El bloque de estacionamiento a continuación (`parkext`, `parkpos`, `context`, `parkingtime`, y así sucesivamente) reside en `res_parking.conf`. La sección `[featuremap]` (los códigos de función DTMF, incluyendo `parkcall`) permanece en `features.conf`.

Las opciones de estacionamiento residen en `res_parking.conf`. Un estacionamiento llamado `default` siempre existe, incluso si no está presente en el archivo de configuración. El extracto a continuación está tomado del `res_parking.conf.sample` de Asterisk 22:

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
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Transferencia de llamadas

La transferencia de llamadas puede ser implementada por el teléfono, por un ATA o por el propio Asterisk. Consulte el manual de su teléfono para entender cómo se transfieren las llamadas. Si su teléfono no admite la transferencia de llamadas, puede usar Asterisk para realizar esta tarea. La transferencia de llamadas se implementa de dos maneras diferentes. La primera forma es utilizar la función de transferencia ciega: marque # seguido del número al que se transferirá. A veces utilizará la función de transferencia de su teléfono IP o softphone IP. Puede cambiar el carácter de transferencia editando el parámetro blindxfer en el archivo features.conf. Puede habilitar la transferencia asistida en Asterisk eliminando el ; antes del parámetro atxfer en el archivo features.conf. Durante una conversación, presionaría *2. Asterisk dirá “transfer” y le dará tono de marcado. La persona que llama es enviada a música en espera. Después de hablar con la persona de destino y colgar el teléfono, el sistema conecta a la persona que llama con el destino.

![Transferencia de llamadas: los pasos para una transferencia ciega (presionar # durante la llamada) y una transferencia asistida (presionar *2)](../images/13-pbx-features-fig03.png)

### Lista de tareas de configuración

1. Para un endpoint PJSIP, asegúrese de que la opción `direct_media` esté configurada en `no` (para que el medio fluya a través de Asterisk y se detecten los códigos de función), o use una opción `t`/`T` en la aplicación `Dial()`

## Estacionamiento de llamadas

Esta función se utiliza para estacionar una llamada. Esto ayuda, por ejemplo, cuando está respondiendo una llamada telefónica fuera de su oficina y desea transferir la llamada de regreso a su escritorio. Puede lograr esto estacionando la llamada en una extension. Una vez que llegue a su escritorio, simplemente marque el número de la extension de estacionamiento para recuperar la llamada.

![Estacionamiento de llamadas: marque 700 para estacionar una llamada en el primer espacio libre (701–720); Asterisk anuncia el espacio, el cual usted marca desde cualquier teléfono para recuperar la llamada](../images/13-pbx-features-fig04.png)

De forma predeterminada, la extension 700 se utiliza para estacionar una llamada. En medio de una conversación, presione # para transferir la llamada a la extension 700. Ahora Asterisk anunciará su extension de estacionamiento, como 701 o 702. Cuelgue el teléfono y la persona que llama quedará en espera. Vaya al teléfono de su escritorio y marque la extension de estacionamiento anunciada para recuperar la llamada. Si la persona que llama permanece estacionada durante mucho tiempo, la función de tiempo de espera (timeout) se activará y la extension marcada originalmente volverá a sonar.

### Lista de tareas de configuración

Siga los pasos a continuación para habilitar el estacionamiento de llamadas. Paso 1: Haga que el estacionamiento sea accesible desde su dialplan (obligatorio). El `context` del estacionamiento predeterminado es `parkedcalls` (configurado en `res_parking.conf`). Incluya ese context en el context desde el cual marcan sus teléfonos, en `extensions.conf`:

```
include => parkedcalls
```

Paso 2: Pruebe la función de estacionamiento de llamadas marcando #700. Notas:

- La extension de estacionamiento no se mostrará en el comando CLI dialplan show.
- Es necesario recargar el módulo de estacionamiento después de cambiar el archivo de configuración de estacionamiento: `module reload res_parking.so`. Para cambios en features.conf, `module reload features.so`.
- Para estacionar una llamada, necesita transferir a #700. Verifique las opciones `t` y `T` en la aplicación `Dial()`.

## Captura de llamadas

La captura de llamadas le permite tomar una llamada de un colega en el mismo grupo de llamadas. Esto ayudaría a evitar, por ejemplo, tener que levantarse para atender una llamada que está sonando para otra persona en su oficina, pero que no está presente. Marcando *8, puede capturar una llamada dentro de su grupo de llamadas. Este número puede ser modificado en el

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


Paso 2: Cambie el número de la función de captura de llamadas (opcional). Esto se configura en la sección `[general]` de `features.conf`, no en `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conferencia (conferencia de llamadas)

Existen diferentes formas de implementar una conferencia en Asterisk. La primera opción es simplemente utilizar la capacidad de conferencia tripartita del teléfono. Al usar esta función en el teléfono, no requiere ningún soporte en el servidor. Sin embargo, cuando desea una conferencia con más de 3 personas, debe ejecutar una sala de conferencias. La aplicación de conferencia moderna de Asterisk es ConfBridge (`app_confbridge`).

ConfBridge admite conferencias de voz HD y videoconferencias. Existen algunas limitaciones para la videoconferencia, como la ausencia de transcodificación: todos los participantes deben usar el mismo codec y perfil. La videoconferencia utiliza un modo de "seguir al que habla", mostrando la imagen de la última persona en hablar. Puede configurar fácilmente nuevos menús DTMF en ConfBridge.

ConfBridge reemplaza la antigua aplicación MeetMe, que fue obsoleta en Asterisk 19 y eliminada en Asterisk 21. A diferencia de MeetMe, ConfBridge **no** requiere DAHDI o una fuente de temporización de hardware: depende de la interfaz de temporización incorporada de Asterisk (`res_timing_timerfd` en Linux, o `res_timing_pthread`), por lo que no se necesita el módulo `dahdi_dummy`. Si está migrando desde un sistema más antiguo que usaba `MeetMe()` y `meetme.conf`, reemplácelos con `ConfBridge()` y `confbridge.conf` como se describe a continuación.

### ConfBridge

Para iniciar una sala de conferencias, la sintaxis se enumera a continuación.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Para obtener una descripción completa del comando, puede usar core show application confbridge.

![Salida de `core show application confbridge`, mostrando la sinopsis, la sintaxis y los argumentos bridge_profile, user_profile y menu](../images/13-pbx-features-fig06.png)

> **[Nota de la 2da ed.]** Un diagrama de ConfBridge ayudaría aquí: mostrar varios endpoints SIP uniéndose a una única conferencia nombrada (p. ej., `101`) a través de `ConfBridge()`, con un participante marcado como administrador, y una nota aclaratoria de que la mezcla/temporización es manejada por `res_confbridge` + el temporizador incorporado `res_timing_*` (sin DAHDI).

Como puede ver arriba, hay tres argumentos importantes, cada uno asignado a un tipo de sección en `confbridge.conf`. **bridge_profile** (una sección `type=bridge`): aquí selecciona el número máximo de participantes (`max_members`), grabación (`record_conference`), `video_mode` y muchos otros parámetros a nivel de puente.

No tiene sentido reproducir el archivo de ejemplo completo aquí, así que permítame darle un ejemplo simple sobre cómo configurar un bridge_profile en el archivo confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (una sección `type=user`): aquí define opciones que son específicas por usuario, como si el usuario es un administrador (`admin=yes`), si comienzan en silencio (`startmuted=yes`), música en espera y muchas otras opciones por usuario. Ejemplo:

```
[admin_user]
type=user
admin=yes
```

**menu** (una sección `type=menu`): aquí define el mapeo del teclado (DTMF) para la conferencia; por ejemplo, qué tecla alterna el silencio, ajusta el volumen o abandona la conferencia. Consulte el archivo `confbridge.conf.sample` para ver todas las acciones disponibles. Ejemplo:

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

Las opciones del puente de conferencia se pueden pasar dinámicamente en el dialplan usando la función CONFBRIDGE(). Vea los ejemplos a continuación:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Comandos de administrador de ConfBridge y migración desde MeetMe

Si proviene de MeetMe, las funciones de administrador que usaba a través de `MeetMeAdmin()` y la opción `a` (admin) ahora se expresan a través del **perfil de usuario administrador** (`admin=yes`) más las acciones de **menu**. Un administrador que se une con un perfil de administrador y un menú que contiene acciones de administrador puede bloquear la sala, expulsar usuarios y silenciar participantes en vivo desde el teclado. Las acciones de menú relevantes en `confbridge.conf` son:

- `admin_kick_last` -- expulsar al último usuario que se unió
- `admin_toggle_mute_participants` -- silenciar/activar el sonido de todos los participantes no administradores
- `toggle_mute` -- silenciar/activar su propio sonido
- `participant_count` -- anunciar el número de participantes
- `leave_conference` -- abandonar el puente y continuar en el dialplan

Estos reemplazan las banderas de opción de MeetMe `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x`, …) y los comandos `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N`, …). No existe `meetme.conf` en Asterisk 22; toda la configuración de la conferencia reside en `confbridge.conf`, y los cambios se aplican con `module reload res_confbridge.so`.

### Ejemplo de ConfBridge

Para crear una sala de conferencias accesible en la extension 500, en `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

La primera persona que marca 500 crea la conferencia `101`; los siguientes llamantes se unen a ella. Los perfiles y menús referenciados aquí (`default_bridge`, `default_user`, `sample_user_menu`) se definen en `confbridge.conf`. Para requerir un PIN, configure `pin=` en el perfil de usuario; para hacer que un participante sea administrador de la conferencia, asígnele un perfil de usuario con `admin=yes`.

## Grabación de llamadas

Existen varias formas de grabar una llamada en Asterisk. Puede usar la aplicación `MixMonitor()` para grabar llamadas fácilmente. (La aplicación más antigua `Monitor`, que grababa dos archivos separados, fue eliminada; use `MixMonitor` en su lugar).

### Uso de la aplicación MixMonitor

La aplicación `MixMonitor` graba el audio en el canal actual al archivo especificado. Si el nombre del archivo es una ruta absoluta, utiliza esa ruta. De lo contrario, crea el archivo en el directorio de monitoreo configurado en asterisk.conf.

![La aplicación MixMonitor(): graba y mezcla el audio de un canal en un archivo, con opciones para anexar, solo puente y ajuste de volumen](../images/13-pbx-features-fig09.png)

### MixMonitor()

Grabe una llamada y mezcle el audio durante la grabación. Sintaxis: `MixMonitor(filename.extension[,options[,command]])`. Graba el audio en el canal actual al archivo especificado. Opciones válidas:

- a - Anexa al archivo en lugar de sobrescribirlo.
- b - Solo guarda audio en el archivo mientras el canal está en puente.
- Nota: no incluye conferencias.
- v(<x>) - Ajusta el volumen audible por un factor de <x> (que va de -4 a 4)
- V(<x>) - Ajusta el volumen hablado por un factor de <x> (que va de -4 a 4)
- W(<x>) - Ajusta tanto el volumen audible como el hablado por un factor de <x> (que va de -4 a 4)
- <command> se ejecutará cuando termine la grabación. Cualquier cadena que coincida con ^{X} será desescapada a ${X} y todas las variables serán evaluadas en ese momento. La variable MIXMONITOR_FILENAME contendrá el nombre del archivo utilizado para grabar.

Un recurso interesante es la función de grabación de un solo toque `automixmon`, que permite a una parte marcar un código DTMF (predeterminado `*3`) durante una llamada para iniciar (y desactivar) la grabación inmediatamente. Se basa en MixMonitor, por lo que escribe un único archivo mezclado. Ejemplo:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Las opciones `X` y `x` habilitan la función MixMonitor de un solo toque para quien llama y quien recibe, respectivamente. Debido a que MixMonitor graba un único archivo mezclado, no hay necesidad de combinar archivos IN/OUT separados después (el antiguo enfoque `automon`/`Monitor`, que producía dos archivos para `soxmix`, fue eliminado junto con la aplicación `Monitor`).

Si no desea usar Set() antes de la aplicación Dial(), puede configurar esto en la sección globals:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Música en espera

La música en espera (MOH) ha cambiado varias veces entre las versiones 1.0, 1.2 y 1.4. En la última versión, la MOH es "FILE-BASED" por defecto. En otras palabras, Asterisk suministrará los archivos de MOH en formatos como g729, alaw, ulaw y gsm. Por lo tanto, no es necesario transcodificar la música antes de enviarla al canal. Esto ahorra tiempo de procesador, lo cual es una modificación bienvenida para aquellos que trabajan con sistemas de producción. En versiones anteriores, la MOH solía ser proporcionada por MP3 (todavía se puede configurar de esa manera). Proporcionar MOH usando MP3 obliga a Asterisk a transcodificar, gastando valiosa potencia de CPU en el proceso. El nuevo archivo de configuración se muestra a continuación. Tenga en cuenta que la clase predeterminada ahora usa el modo de formato de archivo nativo mode=files. Todos los demás modos están comentados. Cada sección es una clase. La única clase no comentada en este punto es default. Si desea tener diferentes clases para diferentes archivos, deberá crear nuevas secciones (clases).

![La configuración de muestra de musiconhold.conf, listando los modos de MOH válidos (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

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

Ahora, para usar música en espera, configure la clase de MOH en los archivos de configuración del canal (chan_dahdi.conf, pjsip.conf, iax.conf, etc.). Para endpoints PJSIP, configure `moh_suggest` en la sección de endpoint de `pjsip.conf` (el nombre de opción heredado `musicclass` se aplica a chan_dahdi y otros controladores de canal, no a PJSIP). Las melodías freeplay instaladas ahora están en formato wav. En el momento de la instalación, puede seleccionar (usando make menuselect) los formatos de archivo de MOH disponibles. Si desea agregar nuevos archivos de MOH, deberá suministrarlos en los formatos requeridos. Por ejemplo:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

En el dialplan, puede iniciar la música en espera en un canal con `StartMusicOnHold` (y detenerla con `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Para reproducir música en espera durante un tiempo fijo como prueba rápida, use la aplicación `MusicOnHold` con una duración (en segundos):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Mapas de aplicaciones

Los mapas de aplicaciones le permiten agregar nuevas funciones utilizando la sección `[applicationmap]` del archivo features.conf. Suponga que necesita identificar el tipo de cliente al que está respondiendo en un centro de llamadas. Podría crear un mapa de aplicaciones para cada tipo de cliente, que podría contar el número de clientes respondidos por tipo.

## Cuestionario

1. ¿Qué afirmaciones son verdaderas sobre el estacionamiento de llamadas?
   - A. De forma predeterminada, la extension 800 se utiliza para el estacionamiento de llamadas.
   - B. Cuando está lejos de su escritorio y recibe una llamada, puede estacionarla; el sistema anuncia el espacio de estacionamiento, y usted marca ese espacio desde cualquier teléfono para recuperar la llamada.
   - C. De forma predeterminada, la extension 700 estaciona una llamada, y las llamadas se estacionan en los espacios 701–720.
   - D. Usted marca 700 para recuperar una llamada estacionada.
2. Para usar la función de captura de llamadas, todas las extensiones deben estar en el mismo ___. Para canales DAHDI, esto se configura en el archivo ___.
3. Al transferir una llamada, puede elegir entre una transferencia ___, donde el destino no es consultado primero, y una transferencia ___, donde usted habla con el destino antes de completarla.
4. Para realizar una transferencia asistida (consultiva) utiliza la secuencia ___; para una transferencia ciega utiliza ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Para alojar conferencias telefónicas en Asterisk 22, utiliza la aplicación ___.
6. En ConfBridge, a un participante se le otorgan privilegios de administrador (expulsar, silenciar a otros, bloquear la sala) configurando ___ en su perfil de usuario (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. El mejor formato para la música en espera es MP3, porque utiliza muy poca potencia de procesamiento en el servidor Asterisk.
   - A. Verdadero
   - B. Falso
8. Para capturar una llamada de un grupo de llamadas específico, debe estar en el grupo ___ coincidente.
9. Puede grabar una llamada con la aplicación MixMonitor() o la función de grabación de un solo toque (`automixmon`). De forma predeterminada, `automixmon` utiliza la secuencia DTMF ___.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. En ConfBridge, ¿qué opción de perfil de usuario `confbridge.conf` hace que un participante se una en silencio (pueden escuchar la conferencia pero no pueden ser escuchados hasta que se les quite el silencio)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Respuestas:** 1 — B, C · 2 — grupo de captura; `chan_dahdi.conf` · 3 — ciega; asistida · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — captura · 9 — C · 10 — A
