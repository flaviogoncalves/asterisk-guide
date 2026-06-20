# Uso de funciones del PBX

En los sistemas SIP, la mayoría de las funciones del teléfono se implementan en el endpoint. Existe una gran variedad de teléfonos SIP y fabricantes, y la interoperabilidad no está garantizada. El equipo de desarrollo de Asterisk ha realizado un trabajo asombroso al implementar la mayor parte de las funciones en el propio PBX, haciendo que Asterisk sea casi independiente del endpoint. Sin embargo, a veces encontrará que la misma función es realizada tanto por el teléfono como por Asterisk. La integración del teléfono y el PBX es la próxima frontera en usabilidad y donde los sistemas propietarios se están enfocando actualmente. En este capítulo, aprenderá cómo usar la mayoría de estas funciones.

## Objetivos

Al final de este capítulo, podrás comprender y usar:

- Estacionamiento de llamadas
- Recogida de llamadas
- Transferencia de llamadas
- Conferencia de llamadas (ConfBridge)
- Grabación de llamadas
- Música en espera

## Dónde se implementan las funciones

En primer lugar, es importante comprender cuándo se ejecutan las funciones del PBX y cuándo el teléfono realiza todo el trabajo. Por ejemplo, puede transferir una llamada usando el botón TRANSFER del teléfono o marcando # (transferencia incondicional ejecutada por el propio PBX).

## Funciones implementadas por Asterisk

- Música en espera
- Aparcamiento de llamadas
- Captura de llamadas
- Grabación de llamadas
- Sala de conferencias ConfBridge
- Transferencia de llamadas (ciega y consultiva)

## Funciones usualmente implementadas por el plan de marcación

- Desvío de llamada cuando está ocupada
- Desvío de llamada inmediato
- Desvío de llamada sin respuesta
- Filtrado de llamadas (lista negra)
- No molestar
- Volver a marcar

## Características usualmente implementadas por el teléfono

These features are implemented by the phone’s firmware:

![Dónde se implementan usualmente las funciones del PBX: en Asterisk mismo, en el plan de marcación o en el teléfono](../images/13-pbx-features-fig01.png)

- Llamada en espera
- Transferencia ciega
- Transferencia consultiva
- Conferencia de tres vías
- Indicador de mensaje pendiente

## The features configuration file

Algunas de las funciones presentadas en este capítulo se configuran en el archivo de configuración features.conf. Es posible cambiar el comportamiento de algunas funciones modificando este archivo. Hemos incluido el fragmento relevante a continuación. En las siguientes secciones de este capítulo describiremos cada función. Fragmento del archivo de ejemplo (Asterisk 22)

![La sección `[featuremap]` de features.conf, con los códigos de funciones DTMF predeterminados](../images/13-pbx-features-fig02.png)

Desde Asterisk 12, el estacionamiento de llamadas se trasladó de `features.conf` a su propio módulo, `res_parking`, con configuración en `res_parking.conf`. El bloque parking-lot a continuación (`parkext`, `parkpos`, `context`, `parkingtime`, y así sucesivamente) vive en `res_parking.conf`. La sección `[featuremap]` (los códigos de funciones DTMF, incluido `parkcall`) permanece en `features.conf`.

Las opciones de parking-lot viven en `res_parking.conf`. Siempre existe un estacionamiento llamado `default`, incluso si no está presente en el archivo de configuración. El fragmento a continuación se tomó del Asterisk 22 `res_parking.conf.sample`:

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

Los códigos de funciones DTMF (incluido el `parkcall` de un solo paso) permanecen en la sección `[featuremap]` de `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the Dial() or Queue()  app call!
;parkcall => #72                ; Park call (one step parking)  -- Make sure to set the K and/or k option in the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X and/or x option in the Dial() or Queue() app call!
```

## Transferencia de Llamada

La transferencia de llamada puede ser implementada por el teléfono, por el ATA o por el propio Asterisk. Consulte el manual de su teléfono para entender cómo se transfieren las llamadas. Si su teléfono no soporta la transferencia de llamada, puede usar Asterisk para realizar esta tarea. La transferencia de llamada se implementa de dos maneras diferentes.

La primera forma es usar la función de transferencia ciega: marque # seguido del número al que se transferirá. A veces usará la función de transferencia de su teléfono IP o softphone IP. Puede cambiar el carácter de transferencia editando el parámetro blindxfer en el archivo features.conf.

Puede habilitar la transferencia asistida en Asterisk quitando el ; antes del parámetro atxfer en el archivo features.conf. Durante una conversación, presionará *2. Asterisk dirá "transfer" y le dará un tono de marcado. El llamante es enviado a música en espera. Después de hablar con la persona de destino y colgar el teléfono, el sistema conecta al llamante con el destino.

![Transferencia de llamada: los pasos para una transferencia ciega (presione # durante la llamada) y una transferencia asistida (presione *2)](../images/13-pbx-features-fig03.png)

### Lista de tareas de configuración

1. Para un endpoint PJSIP, asegúrese de que la opción `direct_media` esté configurada en `no` (para que los medios fluyan a través de Asterisk y se detecten los códigos de función), o use una opción `t`/`T` en la aplicación `Dial()`

## Estacionamiento de llamadas

Esta función se usa para estacionar una llamada. Esto ayuda, por ejemplo, cuando estás contestando una llamada telefónica fuera de tu habitación y deseas transferir la llamada de regreso a tu escritorio. Puedes lograrlo estacionando la llamada en una extensión. Una vez que llegues a tu escritorio, simplemente marca el número de la extensión de estacionamiento para recuperar la llamada.

![Estacionamiento de llamadas: marca 700 para estacionar una llamada en la primera ranura libre (701–720); Asterisk anuncia la ranura, que marcas desde cualquier teléfono para recuperar la llamada](../images/13-pbx-features-fig04.png)

Por defecto, se usa la extensión 700 para estacionar una llamada. En medio de una conversación, presiona # para transferir la llamada a la extensión 700. Ahora Asterisk anunciará tu extensión de estacionamiento, como 701 o 702. Cuelga el teléfono, y el llamante quedará en espera. Ve a tu teléfono de escritorio y marca la extensión de estacionamiento anunciada para recuperar la llamada. Si el llamante está estacionado por mucho tiempo, la función de tiempo de espera se activará y la extensión original marcada volverá a sonar.

### Lista de tareas de configuración

Sigue los pasos a continuación para habilitar el estacionamiento de llamadas. Paso 1: Haz que el lote de estacionamiento sea accesible desde tu dialplan (requerido). El lote de estacionamiento predeterminado `context` es `parkedcalls` (configurado en `res_parking.conf`). Incluye ese contexto en el contexto desde el cual tus teléfonos marcan, en `extensions.conf`:

```
include => parkedcalls
```

Paso 2: Prueba la función de estacionamiento de llamadas marcando #700. Notas:

- La extensión de estacionamiento no se mostrará en el comando CLI `dialplan show`.
- Es necesario recargar el módulo de estacionamiento después de cambiar el archivo de configuración de estacionamiento: `module reload res_parking.so`. Para cambios en `features.conf`, `module reload features.so`.
- Para estacionar una llamada, necesitas transferir a #700. Verifica las opciones `t` y `T` en la aplicación `Dial()`.

## Call pickup

Call pickup allows you to capture a call from a colleague in the same call group. This would help avoid, for example, having to wake up to take a call that is ringing to another person in your room, but who is not present. By dialing *8, you can capture a call within your call group. This number can be modified in the `features.conf` file.

![Recogida de llamada: los miembros solo pueden capturar llamadas dentro de su propio grupo; el operador (pickupgroup=1,2,3) puede recoger llamadas de cualquier grupo](../images/13-pbx-features-fig05.png)

### Configuration task list

Follow the steps below to configure the call pickup feature. Step 1: Configure a call group for your extensions. This is done in the channel configuration file (pjsip.conf, iax.conf, chan_dahdi.conf). For PJSIP endpoints, set `call_group` and `pickup_group` in the endpoint section of `pjsip.conf` (pjsip.conf uses snake_case option names). This task is required.

For PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Step 2: Change the call-pickup feature number (optional). This is set in the `[general]` section of `features.conf`, not in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conferencia (conferencia de llamada)

Existen diferentes formas de implementar una conferencia en Asterisk. La primera opción es simplemente usar la capacidad de conferencia de tres vías del teléfono. Al usar esta función en el teléfono no se requiere ningún soporte en el propio servidor. Sin embargo, cuando se desea una conferencia con más de 3 personas, debe ejecutarse una sala de conferencias. La aplicación de conferencias moderna de Asterisk es ConfBridge (`app_confbridge`).

ConfBridge admite conferencias de voz HD y videoconferencias. Hay algunas limitaciones para la videoconferencia, como la ausencia de transcodificación — todos los participantes deben usar el mismo códec y perfil. La videoconferencia utiliza un modo de seguir al hablante, mostrando la imagen de la última persona que habló. Puede configurar fácilmente nuevos menús DTMF en ConfBridge.

ConfBridge reemplaza la antigua aplicación MeetMe, que fue desaprobada en Asterisk 19. MeetMe todavía se incluye en el árbol de fuentes de Asterisk 22, pero depende de DAHDI y no se compila por defecto, por lo que en una instalación típica de PJSIP simplemente no está disponible — ConfBridge es la aplicación de conferencia soportada. A diferencia de MeetMe, ConfBridge **no** requiere DAHDI ni una fuente de temporización de hardware: se basa en la interfaz de temporización incorporada de Asterisk (`res_timing_timerfd` en Linux, o `res_timing_pthread`), por lo que no se necesita el módulo `dahdi_dummy`. Si está migrando desde un sistema anterior que usaba `MeetMe()` y `meetme.conf`, reemplácelos con `ConfBridge()` y `confbridge.conf` como se describe a continuación.

### ConfBridge

Para iniciar una sala de conferencias, la sintaxis se muestra a continuación.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Para obtener una descripción completa del comando puedes usar `core show application confbridge`.

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

Como puedes ver arriba, hay tres argumentos importantes, cada uno asignado a un tipo de sección en `confbridge.conf`. **bridge_profile** (una sección `type=bridge`): aquí seleccionas el número máximo de participantes (`max_members`), la grabación (`record_conference`), `video_mode` y muchos otros parámetros a nivel de puente.

No tiene sentido reproducir todo el archivo de ejemplo aquí, así que permíteme darte un ejemplo sencillo de cómo configurar un `bridge_profile` en el archivo `confbridge.conf`.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (una sección `type=user`): aquí define opciones que son específicas por usuario, como si el usuario es un administrador (`admin=yes`), si comienza silenciado (`startmuted=yes`), música en espera, y muchas otras opciones por usuario. Ejemplo:

```
[admin_user]
type=user
admin=yes
```

**menu** (una sección `type=menu`): aquí defines la asignación del teclado (DTMF) para la conferencia — por ejemplo, qué tecla activa/desactiva el mute, ajusta el volumen o abandona la conferencia. Revisa el archivo `confbridge.conf.sample` para ver todas las acciones disponibles. Ejemplo:

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

Las opciones del puente de conferencia pueden pasarse dinámicamente en el plan de marcación usando la función CONFBRIDGE(). Vea los ejemplos a continuación:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Comandos de administración de ConfBridge y migración desde MeetMe

Si viene de MeetMe, las funciones de administración que usaba a través de `MeetMeAdmin()` y la opción `a` (admin) ahora se expresan mediante el **perfil de usuario admin** (`admin=yes`) más las acciones del **menú**. Un administrador que se une con un perfil admin y un menú que contiene acciones de administrador puede bloquear la sala, expulsar usuarios y silenciar a los participantes en vivo desde el teclado. Las acciones de menú relevantes en `confbridge.conf` son:

- `admin_kick_last` -- expulsar al último usuario que se unió
- `admin_toggle_mute_participants` -- silenciar/activar sonido de todos los participantes que no son admin
- `toggle_mute` -- silenciar/activar sonido de usted mismo
- `participant_count` -- anunciar el número de participantes
- `leave_conference` -- salir del puente y continuar en el dialplan

Estos reemplazan las banderas de opción MeetMe `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x`, …) y los comandos `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N`, …). En una instalación moderna de PJSIP no cargará `app_meetme` en absoluto; toda la configuración de conferencias vive en `confbridge.conf`, y los cambios se aplican con `module reload app_confbridge.so` (la lógica de ConfBridge vive en `app_confbridge`; no hay módulo `res_confbridge`).

### Ejemplo de ConfBridge

Para crear una sala de conferencias accesible en la extensión 500, en `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

El primer llamante que marque 500 crea la conferencia `101`; los llamantes posteriores se unen a ella. Los perfiles y menús referenciados aquí (`default_bridge`, `default_user`, `sample_user_menu`) están definidos en `confbridge.conf`. Para requerir un PIN, establezca `pin=` en el perfil de usuario; para convertir a un participante en administrador de la conferencia, asígnele un perfil de usuario con `admin=yes`.

## Grabación de Llamadas

Existen varias formas de grabar una llamada en Asterisk. Puedes usar la aplicación `MixMonitor()` para grabar llamadas fácilmente. (La aplicación más antigua `Monitor`, que grababa dos archivos separados, fue eliminada; usa `MixMonitor` en su lugar.)

### Uso de la aplicación MixMonitor

La aplicación `MixMonitor` graba el audio en el canal actual al archivo especificado. Si el nombre de archivo es una ruta absoluta, utiliza esa ruta. De lo contrario, crea el archivo en el directorio de monitoreo configurado en asterisk.conf.

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

Graba una llamada y mezcla el audio durante la grabación. Sintaxis: `MixMonitor(filename.extension[,options[,command]])`. Graba el audio en el canal actual al archivo especificado. Opciones válidas:

- a - Añade al archivo en lugar de sobrescribirlo.
- b - Sólo guarda el audio en el archivo mientras el canal está puenteado.
- Nota: no incluye conferencias.
- v(<x>) - Ajusta el volumen audible por un factor de <x> (rango de -4 a 4)
- V(<x>) - Ajusta el volumen hablado por un factor de <x> (rango de -4 a 4)
- W(<x>) - Ajusta ambos volúmenes, audible y hablado, por un factor de <x> (rango de -4 a 4)
- <command> se ejecutará cuando la grabación termine. Cualquier cadena que coincida con ^{X} será desescapada a ${X} y todas las variables se evaluarán en ese momento. La variable MIXMONITOR_FILENAME contendrá el nombre de archivo usado para la grabación.

Un recurso interesante es la función de grabación con un solo toque `automixmon`, que permite a una parte marcar un código DTMF (el ejemplo `features.conf` sugiere `*3`; no hay un valor predeterminado incorporado, por lo que debes configurarlo) durante una llamada para iniciar inmediatamente (y desactivar) la grabación. Está basada en MixMonitor, por lo que escribe un único archivo mezclado. Ejemplo:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Las opciones `X` y `x` habilitan la función de MixMonitor de un solo toque para el llamante y el llamado respectivamente. Debido a que MixMonitor graba un único archivo mezclado, no es necesario combinar archivos IN/OUT separados después (el antiguo enfoque `automon`/`Monitor`, que producía dos archivos para `soxmix`, se eliminó junto con la aplicación `Monitor`).

Si no desea usar Set() antes de la aplicación Dial(), puede establecer esto en la sección globals:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Música en espera

La música en espera (MOH) ha cambiado varias veces entre las versiones 1.0, 1.2 y 1.4. En la versión más reciente, MOH por defecto es "FILE-BASED". En otras palabras, Asterisk suministrará los archivos de MOH en formatos como g729, alaw, ulaw y gsm. Por lo tanto, no es necesario transcodificar la música antes de enviarla al canal. Esto ahorra tiempo de procesador, lo que es una modificación bienvenida para quienes trabajan con sistemas de producción.

En versiones anteriores, MOH se proporcionaba normalmente mediante MP3 (todavía puede configurarse de esa manera). Proveer MOH usando MP3 obliga a Asterisk a transcodificar, consumiendo valioso poder de CPU en el proceso.

El nuevo archivo de configuración se muestra a continuación. Observe que la clase predeterminada ahora usa el modo de formato de archivo nativo = files. Todos los demás modos están comentados. Cada sección es una clase. La única clase sin comentar en este punto es default. Si desea tener diferentes clases para distintos archivos, necesitará crear nuevas secciones (clases).

![Ejemplo de configuración de musiconhold.conf, enumerando los modos MOH válidos (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

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

Ahora, para usar música en espera, establezca la clase MOH en los archivos de configuración de canal (chan_dahdi.conf, pjsip.conf, iax.conf, etc.). Para los endpoints PJSIP, establezca `moh_suggest` en la sección endpoint de `pjsip.conf` (el nombre de opción heredado `musicclass` se aplica a chan_dahdi y a otros controladores de canal, no a PJSIP). Las melodías freeplay instaladas ahora están en formato wav. En el momento de la instalación, puede seleccionar (usando make menuselect) los formatos de archivo MOH disponibles. Si desea agregar nuevos archivos MOH, deberá proporcionarlos en los formatos requeridos. Por ejemplo:

En `/etc/asterisk/chan_dahdi.conf`, agregue la línea `musiconhold`:

```
[channels]
musiconhold=default
```

Luego edite `/etc/asterisk/musiconhold.conf` para definir esa clase:

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

En el dial plan, puedes iniciar música en espera en un canal con `StartMusicOnHold` (y detenerla con `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Para reproducir música en espera durante un tiempo fijo como prueba rápida, use la aplicación `MusicOnHold` con una duración (en segundos):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Mapas de Aplicación

Los mapas de aplicación le permiten agregar nuevas funciones usando la sección `[applicationmap]` del archivo features.conf. Suponga que necesita identificar el tipo de cliente al que está respondiendo en un centro de llamadas. Podría crear un mapa de aplicación para cada tipo de cliente, que podría contar la cantidad de clientes atendidos por tipo.

## Resumen

En este capítulo aprendiste dónde residen las funciones PBX de Asterisk — algunas en el núcleo, otras en el dialplan y otras en el teléfono — y cómo los códigos de función DTMF están asignados en la sección `[featuremap]` de `features.conf`. Configuraste **transferencia de llamada** (ciega y asistida) y **estacionamiento de llamada** (`res_parking.conf`, con las opciones de marcado `k`/`K` y el conjunto `parkedcalls`), **captura de llamada** por grupo, y **conferencias** con **ConfBridge** (perfiles de puente/usuario/menú `confbridge.conf`), que reemplaza al antiguo MeetMe. Configuraste **grabación con un solo toque** con MixMonitor (`automixmon`, las opciones de marcado `X`/`x` y `DYNAMIC_FEATURES`), configuraste **música en espera**, y viste cómo los **mapas de aplicación** te permiten vincular tu propia lógica del dialplan a una secuencia DTMF. Con estos bloques de construcción puedes ofrecer las funciones cotidianas que los usuarios esperan de una PBX empresarial.

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___. For DAHDI channels this is configured in the ___ file.
3. When transferring a call you can choose between a ___ transfer, where the destination is not consulted first, and an ___ transfer, where you talk to the destination before completing it.
4. To make an attended (consultative) transfer you use the ___ sequence; for a blind transfer you use ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. To host conference calls in Asterisk 22, you use the ___ application.
6. In ConfBridge, a participant is granted administrator privileges (kick, mute others, lock the room) by setting ___ in their user profile (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. The best format for music on hold is MP3, because it uses very little processing power on the Asterisk server.
   - A. True
   - B. False
8. To pick up a call from a specific call group, you must be in the matching ___ group.
9. You can record a call with the MixMonitor() application or the one-touch recording (`automixmon`) feature. In the `features.conf` sample, `automixmon` is mapped to the ___ DTMF sequence.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, which `confbridge.conf` user-profile option makes a participant join muted (they can hear the conference but cannot be heard until unmuted)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
