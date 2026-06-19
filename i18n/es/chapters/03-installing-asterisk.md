# Instalación de Asterisk 22

En el primer capítulo, aprendimos un poco sobre cómo Asterisk es útil en el entorno de telefonía. En este capítulo, cubriremos cómo descargar e instalar Asterisk. Antes de comenzar, es esencial aprender cómo compilarlo e instalarlo. El proceso de compilación puede parecer extraño para los usuarios tradicionales de Microsoft™ Windows™, pero es bastante común en el entorno Linux™. Uno puede obtener un código optimizado para su hardware al compilar Asterisk, que es lo que haremos aquí. Asterisk funciona en varios sistemas operativos, pero elegimos mantener las cosas sencillas y comenzar con solo uno de ellos: Linux. Elegimos Debian como la distribución de Linux™ porque las dependencias son fáciles de instalar y la distribución es estable, con un bajo consumo de recursos. Si desea utilizar otra distribución, por favor cambie el nombre de las dependencias en consecuencia.

Esta edición está dirigida a **Asterisk 22 LTS** (lanzada el 2024-10-16; soporte completo hasta el 2028-10-16, correcciones de seguridad hasta el 2029-10-16). Asterisk 22 es la versión actual de soporte a largo plazo. Tenga en cuenta que Digium fue adquirida por **Sangoma** en 2018, y Asterisk ahora es patrocinado por Sangoma; las referencias a "Digium" a lo largo de este capítulo se refieren a la marca heredada para hardware histórico.

## Objetivos

Al final de este capítulo, usted debería ser capaz de:

- Determinar los requisitos de hardware para Asterisk;
- Instalar Linux con las dependencias requeridas;
- Descargar una versión estable a través de HTTPS;
- Compilar Asterisk; y
- Aprender cómo iniciar Asterisk en el momento del arranque.

## Hardware mínimo requerido

Asterisk no necesita mucho hardware para funcionar; sin embargo, hay algunos consejos para elegir el mejor hardware para sus necesidades. Debe tener en cuenta los siguientes factores principales al elegir su hardware:

- Número total de usuarios registrados. Defina cuántos registros por segundo necesita soportar.
- Número total de llamadas simultáneas. Defina cuántas conversaciones de red necesita procesar en el adaptador de red y el puente en el servidor Asterisk.
- Qué codecs necesita soportar. Los codecs de alta complejidad requerirán mucha potencia de CPU/FPU en su servidor; iLBC, por ejemplo, fue medido por su creador (Global IP Sound) en aproximadamente 18 MIPS por canal para tramas de 30 ms (y alrededor de 15 MIPS para tramas de 20 ms) en un DSP TI C54x.
- Cancelación de eco. La cancelación de eco puede consumir mucha CPU/FPU; en algunos casos, debería elegir cancelación de eco por hardware utilizando DSPs en la tarjeta de interfaz de telefonía.
- Disponibilidad. Utilice RAID1 o 5 para aumentar la disponibilidad. Recuerde, Asterisk es una aplicación 24x7.

El componente principal para un servidor Asterisk es el adaptador de red. Se recomienda un buen adaptador de red para servidores. La CPU es importante cuando necesita soportar codecs de alta complejidad como g.729 e iLBC y cancelación de eco. Puede optar por utilizar DSPs dedicados; Sangoma (anteriormente Digium) proporciona una tarjeta DSP llamada TC400B capaz de soportar 120 llamadas simultáneas en g729. La mejor práctica es elegir una computadora nueva, de clase servidor, de un fabricante conocido. Para saber exactamente cuántas llamadas simultáneas o cuántos usuarios registrados puede soportar una máquina específica, debe probar este hardware con una herramienta de prueba de estrés como SIPP (http://sipp.sourceforge.net). Algunos fabricantes de hardware como Xorcom (http://www.xorcom.com) publican sus resultados en su sitio web. Nota: Algunas aplicaciones de Asterisk, como ConfBridge y música en espera, necesitan una fuente de temporización interna. En Linux moderno, esto es proporcionado automáticamente por el módulo integrado `res_timing_timerfd`; no se requiere hardware de telefonía. (El antiguo temporizador de software `dahdi_dummy` ya no existe; su funcionalidad fue incorporada al módulo principal del kernel `dahdi` en DAHDI Linux 2.3.0.) Puede confirmar el temporizador activo con el comando de CLI `timing test`.

### Configuración de hardware

El hardware de Asterisk no necesita ser sofisticado. No necesita una tarjeta de video costosa ni numerosos periféricos. Algunos consejos sobre la configuración de hardware:

- Deshabilite los puertos USB, seriales y paralelos no utilizados para evitar el consumo de interrupciones innecesarias.
- Una tarjeta de interfaz de red robusta es esencial.
- Tenga especial cuidado si está utilizando tarjetas de interfaz de telefonía. Algunas tarjetas utilizan un bus PCI de 3.3 voltios, y no es fácil encontrar placas base para ellas. En estos días, PCI express es más fácil de encontrar.
- Preste mucha atención al disco duro; los PBX suelen trabajar en un régimen 24x7, mientras que las computadoras de escritorio trabajan 8x5. No utilice hardware de escritorio para un PBX; por lo general, el disco duro falla antes del primer año. Mi recomendación es utilizar una máquina servidor o un dispositivo diseñado para ejecutar aplicaciones 24x7.

### Compartición de IRQ

Las tarjetas de interfaz de telefonía (p. ej., X100P) generan grandes cantidades de interrupciones. Atender estas interrupciones requiere tiempo de procesador. Los controladores no pueden realizar este procesamiento si tiene otro dispositivo utilizando la misma interrupción. En un sistema de una sola CPU, debe evitar compartir IRQ entre dispositivos. Recomendamos el uso de hardware dedicado para ejecutar Asterisk. No olvide deshabilitar cualquier hardware extraño o innecesario. Algunos componentes de hardware pueden deshabilitarse en la configuración del BIOS de la placa base. Una vez que haya iniciado su computadora, vea sus interrupciones asignadas en /proc/interrupts.

```
#cat /proc/interrupts
CPU0
0: 41353058 XT-PIC timer
1: 1988 XT-PIC keyboard
2: 0 XT-PIC cascade
3: 413437739 XT-PIC wctdm <-- TDM400
4: 5721494 XT-PIC eth0
7: 413453581 XT-PIC wcfxo <-- X100P
8: 1 XT-PIC rtc
9: 413445182 XT-PIC wcfxo <-- X100P
12: 0 XT-PIC PS/2 Mouse
14: 179578 XT-PIC ide0
15: 3 XT-PIC ide1
NMI: 0
ERR: 0
```

Aquí puede ver tres tarjetas Digium, cada una en su propia IRQ. Si este es el caso en su sistema, proceda a instalar los controladores de hardware. Si este no es el caso, regrese e intente algo más para evitar compartir IRQ.

## Elección de una distribución de Linux

Asterisk fue desarrollado inicialmente para ejecutarse en Linux. Sin embargo, también puede ejecutarse en BSD Unix o macOS. Si usted es nuevo en Asterisk, intente usar Linux primero, ya que es mucho más fácil. Asterisk apunta oficialmente a la familia RHEL (CentOS/RHEL/Fedora), Ubuntu y Debian. Buenas opciones prácticas hoy en día son **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS** y **Rocky Linux 9 / AlmaLinux 9**; CentOS Linux ha llegado al fin de su vida útil, así que prefiera Rocky o AlmaLinux en sistemas de la familia RHEL. Para este libro, usaré Ubuntu 24.04 LTS. Descargue la última imagen de servidor de la versión puntual 24.04 desde el directorio de lanzamientos oficial a continuación (el nombre de archivo exacto incluye la versión puntual actual, p. ej., `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparación de Linux para Asterisk

Inmediatamente después de instalar Asterisk, instalaremos los paquetes requeridos para la posterior compilación de Asterisk y los controladores DAHDI. Primero, indicaremos a Debian desde dónde se descargarán los paquetes. Esto se hace utilizando la utilidad apt-setup. Paso 1: Instale Ubuntu 24.04 LTS Server en una máquina virtual (use la imagen de 64 bits; las distribuciones utilizadas en este libro son de 64 bits, aunque Asterisk todavía soporta x86 de 32 bits). Hemos utilizado VirtualBox para este entrenamiento. Puede descargar la imagen desde https://releases.ubuntu.com/24.04. La instalación de Linux está fuera del alcance de este entrenamiento. El conocimiento básico de Linux es un prerrequisito para este entrenamiento.

## Instalación de Linux para Asterisk

Instale su Linux como de costumbre, sin una interfaz gráfica de usuario. Instale y configure el servidor de correo también. Necesitaremos el servidor de correo (exim4) para enviar notificaciones de correo de voz más adelante en este libro. Precaución: Esta instalación formateará su PC. Todos los datos de su disco serán borrados. Por favor, asegúrese de respaldar todos los datos antes de comenzar. Paso 1: Inserte el CD en la unidad de CD-ROM y arranque su PC. La mayoría de las preguntas son muy sencillas de responder.

## Instalación de dependencias

Para instalar Asterisk y DAHDI, debe instalar muchas dependencias de software. La forma recomendada de hacer esto en Asterisk 22 es utilizar el script que viene con el árbol de fuentes, el cual conoce los nombres de paquetes correctos para cada distribución soportada. Después de descargar y extraer la fuente de Asterisk (vea "Compilación de Asterisk" a continuación), ejecute:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

Paso 1: Inicie sesión como root (o utilice `sudo`). Paso 2: Si prefiere instalar las dependencias manualmente en un sistema Debian/Ubuntu, la lista de paquetes equivalente es:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

Tenga en cuenta que la fuente de Asterisk ahora está alojada en Git, por lo que `subversion` ya no es necesario, y las versiones modernas de Debian/Ubuntu incluyen `libncurses-dev` en lugar de la versión con número `libncurses5-dev`. Prefiera `./contrib/scripts/install_prereq install` sobre una lista mantenida manualmente, ya que el script siempre rastrea los nombres de paquetes correctos para su distribución.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) es la arquitectura de controladores para tarjetas analógicas y digitales. Antes de instalar Asterisk, es importante instalar DAHDI si planea utilizar interfaces analógicas o digitales. DAHDI todavía existe para tarjetas de telefonía analógica/digital, pero es cada vez más un nicho; la mayoría de las implementaciones modernas son puramente VoIP y pueden omitir esta sección por completo. Instale DAHDI solo si tiene hardware de interfaz de telefonía física. Obtenga los archivos fuente utilizando:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Descomprima los archivos utilizando:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compilación de controladores DAHDI

Necesitará compilar los módulos DAHDI. Los comandos ./configure y make menuselect fueron introducidos hace varios años. Este último le permite seleccionar qué utilidades y módulos construir. Los siguientes comandos harán esto:

```
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version downloaded
make
make install
cd ../tools
autoreconf -i
./configure
make
make install
```

make install-config DAHDI ha sido configurado. Si tiene algún hardware DAHDI, ahora se recomienda que edite /etc/dahdi/modules para cargar soporte solo para el hardware DAHDI instalado en este sistema. Por defecto, el soporte para todo el hardware DAHDI se carga al iniciar DAHDI. Creo que el hardware DAHDI que tiene en su sistema es: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware. Esta pantalla (arriba) le pide que cambie el archivo /etc/dahdi/modules para cargar solo los controladores requeridos para su configuración específica y mostrar el hardware detectado. Edite el archivo /etc/dahdi/modules y cargue solo el hardware requerido. En mi caso, estaba usando una máquina de prueba con un Xorcom Astribank 6FXS y 2FXO. El archivo se muestra a continuación.

```
# Contains the list of modules to be loaded / unloaded by /etc/init.d/dahdi.
#
# NOTE:  Please add/edit /etc/modprobe.d/dahdi or /etc/modprobe.conf if you
#        would like to add any module parameters.
#
# Format of this file: list of modules, each in its own line.
# Anything after a '#' is ignore, likewise trailing and leading
# whitespaces and empty lines.
# Digium TE205P/TE207P/TE210P/TE212P: PCI dual-port T1/E1/J1
# Digium TE405P/TE407P/TE410P/TE412P: PCI quad-port T1/E1/J1
# Digium TE220: PCI-Express dual-port T1/E1/J1
# Digium TE420: PCI-Express quad-port T1/E1/J1
#wct4xxp
# Digium TE120P: PCI single-port T1/E1/J1
# Digium TE121: PCI-Express single-port T1/E1/J1
# Digium TE122: PCI single-port T1/E1/J1
#wcte12xp
# Digium T100P: PCI single-port T1
# Digium E100P: PCI single-port E1
#wct1xxp
# Digium TE110P: PCI single-port T1/E1/J1
#wcte11xp
# Digium TDM2400P/AEX2400: up to 24 analog ports
# Digium TDM800P/AEX800: up to 8 analog ports
# Digium TDM410P/AEX410: up to 4 analog ports
#wctdm24xxp
# X100P - Single port FXO interface
# X101P - Single port FXO interface
#wcfxo
# Digium TDM400P: up to 4 analog ports
#wctdm
# Xorcom Astribank Devices
xpp_usb
```

Reinicialice su computadora y verifique la carga correcta de los controladores.

## Qué versión elegir

Como regla general, debe utilizar la versión con las características requeridas. Asterisk sigue un modelo de lanzamiento que alterna entre LTS (soporte a largo plazo) y lanzamientos estándar. Al momento de esta edición, **Asterisk 22 es la versión LTS actual** (lanzada en octubre de 2024; la última versión puntual es 22.10.0), lo que la convierte en la mejor opción ahora. Asterisk 20 es la LTS anterior, y la versión 16 (utilizada en la primera edición) ha llegado al fin de su vida útil. Para sistemas de producción, elija siempre una versión LTS.

## Compilación de Asterisk

Si ha compilado software anteriormente, compilar Asterisk será una tarea fácil. Ejecute los siguientes comandos para compilar e instalar Asterisk. Recuerde, puede elegir qué aplicaciones y módulos construir utilizando make menuselect. Paso 1: Descargue el código fuente

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Paso 2: Instale los prerrequisitos de compilación (vea "Instalación de dependencias" arriba)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Paso 3: Configure la compilación

```
./configure
```

Paso 4: Seleccione los módulos a construir

```
make menuselect
```

Utilice make menuselect para instalar solo los módulos necesarios. En Asterisk 22, el canal SIP es **chan_pjsip** (construido por defecto); el antiguo **chan_sip** fue eliminado en Asterisk 21 y ya no existe. El *pass-through* de Opus funciona de inmediato (el módulo `res_format_attr_opus` incluido maneja la negociación SDP), pero el módulo de transcodificación **codec_opus** sigue siendo un binario externo de código cerrado de Sangoma/Digium; seleccionarlo en menuselect lo descarga desde los servidores de Digium. El binario es gratuito. Vea "Selección de módulos con menuselect" a continuación para más detalles.

Paso 5: Construya e instale Asterisk, luego cree la configuración por defecto y los archivos de ejemplo

```
make
make install
make samples
make config
ldconfig
```

`make install` instala los binarios y módulos, `make samples` escribe los archivos de configuración de ejemplo en `/etc/asterisk`, `make config` instala el script de inicio SysV para su distribución detectada (p. ej., `/etc/init.d/asterisk` en Debian/Ubuntu), y `ldconfig` actualiza la caché de bibliotecas compartidas. Una unidad de systemd también se incluye en el árbol de fuentes en `contrib/systemd/asterisk.service`, pero `make config` no la instala automáticamente; cópiela en su lugar usted mismo si prefiere ejecutar Asterisk bajo systemd (vea a continuación).

### Selección de módulos con menuselect

`make menuselect` abre un menú basado en texto donde usted elige exactamente qué aplicaciones, codecs, canales y recursos construir. Algunas notas específicas para Asterisk 22:

- **chan_pjsip** (bajo *Channel Drivers*) es el canal SIP moderno y está habilitado por defecto; es el único canal SIP en Asterisk 22.
- **codec_opus** (bajo *Codec Translators*) es un módulo **externo** (su entrada en menuselect dice "Download the Opus codec from Digium"); habilitarlo hace que `make` obtenga el binario gratuito de código cerrado de Sangoma/Digium. El pass-through de Opus en sí no necesita ningún módulo adicional. El módulo **codec_g729** de Sangoma también está disponible; el binario es gratuito para descargar, pero la transcodificación legal de G.729 requiere una licencia comprada por canal.
- Seleccione los formatos de sonido e idiomas que desee en los menús *Core Sound Packages*, *Music On Hold File Packages* y *Extras Sound Packages*; todo lo que marque allí se descarga e instala automáticamente durante `make install`.

Después de realizar sus selecciones, elija **Save & Exit** y continúe con `make`.

## Inicio y detención de Asterisk

Con esta configuración mínima, es posible iniciar Asterisk con éxito. Para aprendizaje y depuración, puede iniciar Asterisk en primer plano conectado a la consola:

```
/usr/sbin/asterisk –vvvgc
```

Utilice el comando de CLI stop now para apagar Asterisk.

```
CLI>core stop now
```

### Inicio de Asterisk con systemd

En distribuciones de Linux modernas (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), el gestor de servicios del sistema es **systemd**. Asterisk incluye una unidad de systemd en `contrib/systemd/asterisk.service` en el árbol de fuentes; cópiela a `/etc/systemd/system/asterisk.service` y ejecute `systemctl daemon-reload`. Una vez instalada, la forma recomendada de ejecutar Asterisk en producción es a través de `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Una vez que Asterisk se esté ejecutando como un servicio, conéctese a su CLI con `asterisk -r` (conectar) o `asterisk -rvvv` (conectar con salida detallada).

En sistemas más antiguos, Asterisk se iniciaba a través del script de inicio SysV heredado (`/etc/init.d/asterisk`) y el envoltorio **safe_asterisk**, que reiniciaba Asterisk automáticamente si se bloqueaba. Con systemd, el reinicio automático es manejado por la directiva `Restart=` del archivo de unidad, por lo que `safe_asterisk` generalmente ya no es necesario. El enfoque heredado de init/`safe_asterisk` todavía funciona, pero está obsoleto en distribuciones basadas en systemd.

### Opciones de tiempo de ejecución de Asterisk

El proceso de inicio de Asterisk es muy sencillo. Si Asterisk se ejecuta sin ningún parámetro, se lanza como un demonio.

```
/sbin/asterisk
```

Puede acceder a la consola de Asterisk ejecutando el siguiente comando. Tenga en cuenta que se puede ejecutar más de un proceso de consola al mismo tiempo.

```
/sbin/asterisk -r
```

### Opciones de tiempo de ejecución disponibles para Asterisk

Puede mostrar las opciones de tiempo de ejecución disponibles utilizando asterisk –h

```
sipast:/usr/src/asterisk-22.x.y# asterisk -h
```

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation y otros. Uso: asterisk [OPTIONS] Opciones válidas: -V Mostrar número de versión y salir -C <configfile> Usar un archivo de configuración alternativo -G <group> Ejecutar como un grupo distinto al llamador -U <user> Ejecutar como un usuario distinto al llamador -c Proporcionar CLI de consola -d Aumentar depuración (múltiples d = más depuración) -f No hacer fork -F Hacer fork siempre -g Volcar core en caso de bloqueo -h Esta pantalla de ayuda -i Inicializar claves criptográficas al inicio -L <load> Limitar la carga promedio máxima antes de rechazar nuevas llamadas -M <value> Limitar el número máximo de llamadas al valor especificado -m Silenciar depuración y salida de consola en la consola -n Deshabilitar colorización de consola. Solo se puede usar al inicio. -p Ejecutar como hilo pseudo-realtime -q Modo silencioso (suprimir salida) -r Conectar a Asterisk en esta máquina -R Igual que -r, excepto intentar reconectar si se desconecta -s <socket> Conectar a Asterisk vía socket <socket> (solo válido con -r) -t Grabar archivos de sonido en /var/tmp y moverlos a donde pertenecen después de terminar -T Mostrar la hora en formato [Mmm dd hh:mm:ss] para cada línea de salida a la CLI. No se puede usar con modo de consola remota. -v Aumentar verbosidad (múltiples v = más detallado) -x <cmd> Ejecutar comando <cmd> (implica -r) -X Habilitar el uso de #exec en asterisk.conf -W Ajustar colores de terminal para compensar un fondo claro

## Directorios de instalación

Asterisk se instala en varios directorios, los cuales pueden modificarse en el archivo asterisk.conf. Para propósitos de entrenamiento, cambiaría la verbosidad de 3 a 15; para producción, manténgala en 3. Las opciones max_calls y max_load son buenas opciones para proteger su sistema de sobrecargas.

### asterisk.conf

```
[directories](!) ; remove the (!) to enable this
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk
astsbindir => /usr/sbin
[options]
;verbose = 3
;debug = 3
;refdebug = yes                 ; Enable reference count debug logging.
;alwaysfork = yes               ; Same as -F at startup.
;nofork = yes                   ; Same as -f at startup.
;quiet = yes                    ; Same as -q at startup.
;timestamp = yes                ; Same as -T at startup.
;execincludes = yes             ; Support #exec in config files.
;console = yes                  ; Run as console (same as -c at startup).
;highpriority = yes             ; Run realtime priority (same as -p at
                                ; startup).
;initcrypto = yes               ; Initialize crypto keys (same as -i at
                                ; startup).
;nocolor = yes                  ; Disable console colors.
;dontwarn = yes                 ; Disable some warnings.
;dumpcore = yes                 ; Dump core on crash (same as -g at startup).
;languageprefix = yes           ; Use the new sound prefix path syntax.
;systemname = my_system_name    ; Prefix uniqueid with a system name for
                                ; Global uniqueness issues.
;autosystemname = yes           ; Automatically set systemname to hostname,
                                ; uses 'localhost' on failure, or systemname if
                                ; set.
;mindtmfduration = 80           ; Set minimum DTMF duration in ms (default 80
ms)
                                ; If we get shorter DTMF messages, these will
be
                                ; changed to the minimum duration
;maxcalls = 10                  ; Maximum amount of calls allowed.
;maxload = 0.9                  ; Asterisk stops accepting new calls if the
                                ; load average exceed this limit.
;maxfiles = 1000                ; Maximum amount of openfiles.
;minmemfree = 1                 ; In MBs, Asterisk stops accepting new calls if
                                ; the amount of free memory falls below this
                                ; watermark.
;cache_media_frames = yes       ; Cache media frames for performance
                                ; Disable this option to help track down media
frame
                                ; mismanagement when using valgrind or
MALLOC_DEBUG.
                                ; The cache gets in the way of determining if
the
                                ; frame is used after being freed and who freed
it.
                                ; NOTE: This option has no effect when Asterisk
is
                                ; compiled with the LOW_MEMORY compile time
option
                                ; enabled because the cache code does not
exist.
                                ; Default yes
;cache_record_files = yes       ; Cache recorded sound files to another
                                ; directory during recording.
;record_cache_dir = /tmp        ; Specify cache directory (used in conjunction
                                ; with cache_record_files).
;transmit_silence = yes         ; Transmit silence while a channel is in a
                                ; waiting state, a recording only state, or
                                ; when DTMF is being generated.  Note that the
                                ; silence internally is generated in raw signed
                                ; linear format. This means that it must be
                                ; transcoded into the native format of the
                                ; channel before it can be sent to the device.
                                ; It is for this reason that this is optional,
                                ; as it may result in requiring a temporary
                                ; codec translation path for a channel that may
                                ; not otherwise require one.
;transcode_via_sln = yes        ; Build transcode paths via SLINEAR, instead of
                                ; directly.
;runuser = asterisk             ; The user to run as.
;rungroup = asterisk            ; The group to run as.
;lightbackground = yes          ; If your terminal is set for a light-colored
                                ; background.
;forceblackbackground = yes     ; Force the background of the terminal to be
                                ; black, in order for terminal colors to show
                                ; up properly.
;defaultlanguage = en           ; Default language
documentation_language = en_US  ; Set the language you want documentation
                                ; displayed in. Value is in the same format as
                                ; locale names.
;hideconnect = yes              ; Hide messages displayed when a remote console
                                ; connects and disconnects.
;lockconfdir = no               ; Protect the directory containing the
                                ; configuration files (/etc/asterisk) with a
                                ; lock.
;live_dangerously = no          ; Enable the execution of 'dangerous' dialplan
                                ; functions from external sources (AMI,
                                ; etc.) These functions (such as SHELL) are
                                ; considered dangerous because they can allow
                                ; privilege escalation.
                                ; Default no
;entityid=00:11:22:33:44:55     ; Entity ID.
                                ; This is in the form of a MAC address.
                                ; It should be universally unique.
                                ; It must be unique between servers
communicating
                                ; with a protocol that uses this value.
                                ; This is currently is used by DUNDi and
                                ; Exchanging Device and Mailbox State
                                ; using protocols: XMPP, Corosync and PJSIP.
;rtp_use_dynamic = yes          ; When set to "yes" RTP dynamic payload types
                                ; are assigned dynamically per RTP instance vs.
                                ; allowing Asterisk to globally initialize them
                                ; to pre-designated numbers (defaults to
"yes").
;rtp_pt_dynamic = 35            ; Normally the Dynamic RTP Payload Type numbers
                                ; are 96-127, which allow just 32 formats. The
                                ; starting point 35 enables the range 35-63 and
                                ; allows 29 additional formats. When you use
                                ; more than 32 formats in the dynamic range and
                                ; calls are not accepted by a remote
                                ; implementation, please report this and go
                                ; back to value 96.
; Changing the following lines may compromise your security.
;[files]
;astctlpermissions = 0660
;astctlowner = root
;astctlgroup = apache
;astctl = asterisk.ctl
```

## Archivos de registro y rotación de registros

El PBX Asterisk registra sus mensajes en el directorio /var/log/asterisk. El archivo que controla los registros

```
is the logger.conf.
;
; Logging Configuration
;
; In this file, you configure logging to files or to
; the syslog system.
;
; "logger reload" at the CLI will reload configuration
; of the logging system.
[general]
;
; Customize the display of debug message time stamps
; this example is the ISO 8601 date format (yyyy-mm-dd HH:MM:SS)
;
; see strftime(3) Linux manual for format specifiers.  Note that there is also
; a fractional second parameter which may be used in this field.  Use %1q
; for tenths, %2q for hundredths, etc.
;
;dateformat=%F %T       ; ISO 8601 date format
;dateformat=%F %T.%3q   ; with milliseconds
;
;
; This makes Asterisk write callids to log messages
; (defaults to yes)
;use_callids = no
;
; This appends the hostname to the name of the log files.
;appendhostname = yes
;
; This determines whether or not we log queue events to a file
; (defaults to yes).
;queue_log = no
;
; Determines whether the queue_log always goes to a file, even
; when a realtime backend is present (defaults to no).
;queue_log_to_file = yes
;
; Set the queue_log filename
; (defaults to queue_log)
;queue_log_name = queue_log
;
; When using realtime for the queue log, use GMT for the timestamp
; instead of localtime.  The default of this option is 'no'.
;queue_log_realtime_use_gmt = yes
;
; Log rotation strategy:
; none:  Do not perform any logrotation at all.  You should make
;        very sure to set up some external logrotate mechanism
;        as the asterisk logs can get very large, very quickly.
; sequential:  Rename archived logs in order, such that the newest
;              has the highest sequence number [default].  When
;              exec_after_rotate is set, ${filename} will specify
;              the new archived logfile.
; rotate:  Rotate all the old files, such that the oldest has the
;          highest sequence number [this is the expected behavior
;          for Unix administrators].  When exec_after_rotate is
;          set, ${filename} will specify the original root filename.
; timestamp:  Rename the logfiles using a timestamp instead of a
;             sequence number when "logger rotate" is executed.
;             When exec_after_rotate is set, ${filename} will
;             specify the new archived logfile.
;rotatestrategy = rotate
;
; Run a system command after rotating the files.  This is mainly
; useful for rotatestrategy=rotate. The example allows the last
; two archive files to remain uncompressed, but after that point,
; they are compressed on disk.
;
; exec_after_rotate=gzip -9 ${filename}.2
;
;
; For each file, specify what to log.
;
; For console logging, you set options at start of
; Asterisk with -v for verbose and -d for debug
; See 'asterisk -h' for more information.
;
; Directory for log files is configures in asterisk.conf
; option astlogdir
;
; All log messages go to a queue serviced by a single thread
; which does all the IO.  This setting controls how big that
; queue can get (and therefore how much memory is allocated)
; before new messages are discarded.
; The default is 1000
;logger_queue_limit = 250
;
;
[logfiles]
;
; Format is:
;
; logger_name => [formatter]levels
;
; The name of the logger dictates not only the name of the logging
; channel, but also its type. Valid types are:
;   - 'console'  - The root console of Asterisk
;   - 'syslog'   - Linux syslog, with facilities specified afterwards with
;                  a period delimiter, e.g., 'syslog.local0'
;   - 'filename' - The name of the log file to create. This is the default
;                  for log channels.
;
; Filenames can either be relative to the standard Asterisk log directory
; (see 'astlogdir' in asterisk.conf), or absolute paths that begin with
; '/'.
;
; An optional formatter can be specified prior to the log levels sent
; to the log channel. The formatter is defined immediately preceeding the
; levels, and is enclosed in square brackets. Valid formatters are:
;   - [default] - The default formatter, this outputs log messages using a
;                 human readable format.
;   - [json]    - Log the output in JSON. Note that JSON formatted log entries,
;                 if specified for a logger type of 'console', will be formatted
;                 per the 'default' formatter for log messages of type VERBOSE.
;                 This is due to the remote consoles intepreting verbosity
;                 outside of the logging subsystem.
;
; Log levels include the following, and are specified in a comma delineated
; list:
;    debug
;    notice
;    warning
;    error
;    verbose(<level>)
;    dtmf
;    fax
;    security
;
; Verbose takes an optional argument, in the form of an integer level.
; Verbose messages with higher levels will not be logged to the file.  If
; the verbose level is not specified, it will log verbose messages following
; the current level of the root console.
;
; Special level name "*" means all levels, even dynamic levels registered
; by modules after the logger has been initialized (this means that loading
; and unloading modules that create/remove dynamic logger levels will result
; in these levels being included on filenames that have a level name of "*",
; without any need to perform a 'logger reload' or similar operation).
; Note that there is no value in specifying both "*" and specific level names
; for a filename; the "*" level means all levels.  The only exception is if
; you need to specify a specific verbose level. e.g, "verbose(3),*".
;
; We highly recommend that you DO NOT turn on debug mode if you are simply
; running a production system.  Debug mode turns on a LOT of extra messages,
; most of which you are unlikely to understand without an understanding of
; the underlying code.  Do NOT report debug messages as code issues, unless
; you have a specific issue that you are attempting to debug.  They are
; messages for just that -- debugging -- and do not rise to the level of
; something that merit your attention as an Asterisk administrator.  Debug
; messages are also very verbose and can and do fill up logfiles quickly;
; this is another reason not to have debug mode on a production system unless
; you are in the process of debugging a specific issue.
;
;debug => debug
;security => security
console => notice,warning,error
;console => notice,warning,error,debug
messages => notice,warning,error
;full => notice,warning,error,debug,verbose,dtmf,fax
;
;full-json => [json]debug,verbose,notice,warning,error,dtmf,fax
;
;syslog keyword : This special keyword logs to syslog facility
;
;syslog.local0 => notice,warning,error
```

; Algunos comandos de consola están asociados con el proceso de registro.

```
CLI> logger show channels
Logger queue limit: 1000

Channel                             Type     Formatter  Status    Configuration
-------                             ----     ---------  ------    -------------
/var/log/asterisk/security          File     default    Enabled    - SECURITY
/var/log/asterisk/full              File     default    Enabled    - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages          File     default    Enabled    - NOTICE WARNING ERROR
CLI> logger rotate
  == Parsing '/etc/asterisk/logger.conf': Found
Asterisk Event Logger restarted
Asterisk Queue Logger restarted
You can control the log rotation using the logrotate daemon. Edit the file
/etc/logrotate.d and include the content below to start rotating the log files.
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
       /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

Se puede obtener más información sobre logrotate utilizando:

```
#man logrotate
```

## Desinstalación de Asterisk

Para desinstalar Asterisk, utilice:

```
make uninstall
```

Para desinstalar Asterisk y todos los archivos de configuración, utilice:

```
make uninstall-all
```

## Notas de instalación de Asterisk

Esta sección proporcionará algunos consejos sobre problemas a abordar antes de instalar Asterisk.

### Sistemas de producción

Si Asterisk se instala en un entorno de producción, debe prestar atención al diseño del sistema. Un servidor debe optimizarse de tal manera que los sistemas de telefonía tengan prioridad sobre otros procesos del sistema. Asterisk no debe ejecutarse junto con software intensivo en procesador como X-Windows. Si necesita ejecutar procesos intensivos en CPU (p. ej., una base de datos enorme), utilice un servidor separado. En términos generales, Asterisk es susceptible a variaciones en el rendimiento del hardware. Por lo tanto, intente utilizar Asterisk en un entorno de hardware que no requiera más del 40% de utilización de CPU.

### Consejos de red

Si planea utilizar teléfonos IP, es importante que preste atención a su red. Los protocolos de voz son muy buenos y resistentes a la latencia e incluso al jitter; sin embargo, si utiliza una red de área local mal configurada, la calidad de voz sufrirá. Solo es posible garantizar una buena calidad de voz utilizando calidad de servicio (QoS) en switches y routers. La voz en una red de área local tiende a ser buena, pero incluso en un entorno LAN, si tiene hubs de 10 Mbps con demasiadas colisiones, terminará teniendo una voz distorsionada o de mala calidad. Siga estas recomendaciones para garantizar la mejor calidad de voz posible:

- Utilice QoS de extremo a extremo si es posible o económicamente viable. Con QoS de extremo a extremo, la calidad de voz es perfecta. ¡Sin excusas!
- Evite utilizar hubs de 10/100 Mbps para voz en un entorno de producción. Las colisiones pueden imponer jitter en la red. Se prefieren los 10/100 Mbps full duplex porque no ocurren colisiones.
- Utilice VLANs para separar transmisiones innecesarias de la red de voz. No querrá que un virus destruya su red de voz con transmisiones ARP.
- Eduque a los usuarios sobre las expectativas en una red de voz. Sin QoS, no afirme que la voz será perfecta, ya que en la mayoría de los casos no lo será. Se logrará con mayor frecuencia una calidad de voz similar a la de un teléfono móvil. Utilice teléfonos de calidad, ya que los problemas con el firmware y el diseño del hardware son comunes.

## Resumen

En este capítulo, ha aprendido sobre los requisitos mínimos de hardware, así como sobre cómo descargar, instalar y compilar Asterisk. Asterisk debe ejecutarse con un usuario no root por razones de seguridad. Debe verificar su entorno de red antes de iniciar el entorno de producción.

## Cuestionario

1. En Asterisk 22, ¿qué controlador de canal proporciona soporte SIP, y qué sucedió con el antiguo `chan_sip`?
   - A. `chan_sip` sigue siendo el predeterminado; `chan_pjsip` es opcional.
   - B. `chan_pjsip` es el canal SIP predeterminado; `chan_sip` fue eliminado en Asterisk 21 y ya no existe.
   - C. Ambos se construyen por defecto y usted elige entre ellos en tiempo de ejecución.
   - D. El soporte SIP fue eliminado por completo en favor de IAX2.
2. Las tarjetas de interfaz de telefonía para Asterisk generalmente tienen procesadores de señales digitales (DSPs) integrados y, por lo tanto, no necesitan mucha CPU de la PC.
   - A. Verdadero
   - B. Falso
3. Si desea una calidad de voz perfecta, necesita implementar calidad de servicio (QoS) de extremo a extremo.
   - A. Verdadero
   - B. Falso
4. Siempre debe elegir la última versión de Asterisk, ya que es la más estable.
   - A. Verdadero
   - B. Falso
5. ¿Cuál es la forma recomendada de instalar las dependencias de compilación para Asterisk 22?
6. Si no tiene una tarjeta de interfaz TDM, aún tendrá una fuente de temporización interna para la sincronización, proporcionada por el módulo `res_timing_timerfd` en Linux. Esta temporización es utilizada por aplicaciones como ________ y ________.
7. Al instalar Asterisk, es mejor dejar fuera los entornos de escritorio como GNOME o KDE, porque las interfaces gráficas consumen ciclos de CPU.
   - A. Verdadero
   - B. Falso
8. Los archivos de configuración de Asterisk se encuentran en el directorio ________.
9. Para instalar los archivos de configuración de ejemplo de Asterisk, escriba el comando: ________
10. ¿Por qué es importante ejecutar Asterisk como un usuario no root?

**Respuestas:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Ejecute `./contrib/scripts/install_prereq install` desde el árbol de fuentes de Asterisk extraído · 6 — ConfBridge y Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Seguridad (limita el daño si Asterisk es comprometido)
