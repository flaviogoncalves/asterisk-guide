# Instalando Asterisk 22

En el primer capítulo, aprendimos un poco sobre cómo Asterisk es útil en el entorno de telefonía. En este capítulo, cubriremos cómo descargar e instalar Asterisk. Antes de comenzar, es esencial aprender cómo compilarlo e instalarlo. El proceso de compilación puede parecer extraño para los usuarios tradicionales de Microsoft™ Windows™, pero es bastante común en el entorno Linux™. Se puede obtener un código optimizado para su hardware al compilar Asterisk, que es lo que haremos aquí. Asterisk se ejecuta en varios sistemas operativos, pero mantendremos las cosas simples y usaremos solo uno: Linux. Usamos **Ubuntu 24.04 LTS** porque sus dependencias son fáciles de instalar y es una distribución de servidor estable, bien soportada y con una huella baja. Si prefiere otra distribución, ajuste los nombres de los paquetes en consecuencia.

Esta edición está dirigida a **Asterisk 22 LTS** (lanzado el 2024-10-16; soporte completo hasta 2028-10-16, correcciones de seguridad hasta 2029-10-16). Asterisk 22 es la versión actual de soporte a largo plazo. Tenga en cuenta que Digium fue adquirido por **Sangoma** en 2018, y Asterisk ahora es patrocinado por Sangoma — las referencias a "Digium" a lo largo de este capítulo se refieren a la marca heredada para hardware histórico.

## Objetivos

Al final de este capítulo deberías ser capaz de:

- Determinar los requisitos de hardware para Asterisk;
- Instalar Linux con las dependencias requeridas;
- Descargar una versión estable mediante HTTPS;
- Compilar Asterisk; y
- Aprender cómo iniciar Asterisk al arrancar el sistema.

## Minimum Hardware Required

Asterisk no necesita mucho hardware para ejecutarse, sin embargo hay algunos consejos para elegir el mejor hardware para sus requerimientos. Debe tomar en consideración los siguientes factores principales al elegir su hardware:

- Número total de usuarios registrados. Defina cuántos registros por segundo necesita soportar
- Número total de llamadas simultáneas. Defina cuántas conversaciones de red necesita procesar en el adaptador de red y puente en el servidor Asterisk
- Qué códecs necesita soportar. Los códecs de alta complejidad requerirán mucha potencia CPU/FPU en su servidor; iLBC, por ejemplo, fue medido por su creador (Global IP Sound) en aproximadamente 18 MIPS por canal para tramas de 30 ms (y alrededor de 15 MIPS para tramas de 20 ms) en un DSP TI C54x
- Cancelación de eco. La cancelación de eco puede consumir mucha CPU/FPU; en algunos casos debe elegir cancelación de eco por hardware usando DSPs en la tarjeta de interfaz de telefonía
- Disponibilidad. Use RAID1 o 5 para aumentar la disponibilidad. Recuerde, Asterisk es una aplicación 24x7.

El componente principal de un servidor Asterisk es el adaptador de red. Se recomienda una buena tarjeta de red para servidor. La CPU es importante cuando necesita soportar códecs de alta complejidad como g.729 e iLBC y cancelación de eco. Puede elegir descargar esta carga a DSPs dedicados: Sangoma (anteriormente Digium) ofrece una tarjeta DSP llamada TC400B capaz de soportar 120 llamadas simultáneas G.729.

La mejor práctica es elegir una computadora de clase servidor, nueva, de un fabricante reconocido. Para saber exactamente cuántas llamadas simultáneas o cuántos usuarios registrados puede soportar una máquina específica, debe probar este hardware con una herramienta de prueba de estrés como SIPP (http://sipp.sourceforge.net). Algunos fabricantes de hardware como Xorcom (http://www.xorcom.com) publican sus resultados en el sitio web.

Nota: Algunas aplicaciones de Asterisk, como ConfBridge y música en espera, necesitan una fuente de temporización interna. En Linux moderno esto se provee automáticamente por el módulo incorporado `res_timing_timerfd` — no se requiere hardware de telefonía. (El antiguo temporizador de software `dahdi_dummy` ya no existe; su funcionalidad se integró en el módulo principal del kernel `dahdi` en DAHDI Linux 2.3.0.) Puede confirmar el temporizador activo con el comando CLI `timing test`.

### Hardware configuration

El hardware de Asterisk no necesita ser sofisticado. No necesita una tarjeta de video costosa ni numerosos periféricos. Algunos consejos sobre la configuración del hardware:

- Desactive los puertos USB, serie y paralelo no usados para evitar el consumo de interrupciones innecesarias.
- Una tarjeta de interfaz de red robusta es esencial.
- Tenga especial cuidado si está usando tarjetas de interfaz de telefonía. Algunas tarjetas usan un bus PCI de 3.3 voltios, y no es fácil encontrar placas base para ellas. Hoy en día, PCI Express se encuentra más fácilmente.
- Preste mucha atención al disco duro; una PBX funciona en un régimen 24x7 mientras que los escritorios trabajan 8x5. No use hardware de escritorio para una PBX, usualmente el disco duro falla antes del primer año. Mi recomendación es usar una máquina servidor o un appliance diseñado para ejecutar aplicaciones 24x7.

### IRQ sharing (legacy PCI cards only)

Esta preocupación se aplica **solo** si instala tarjetas de telefonía físicas PCI/PCI-Express (hardware DAHDI). Tales tarjetas generan gran número de interrupciones, y en sistemas antiguos de un solo CPU, compartir una línea IRQ con otro dispositivo podría privar al controlador y degradar la calidad de voz. Si usa tarjetas de telefonía, dedique la máquina a Asterisk, desactive cualquier dispositivo integrado no usado en el BIOS, y verifique las interrupciones asignadas con `cat /proc/interrupts`. Los servidores modernos de múltiples núcleos que usan interrupciones MSI/MSI‑X hacen que el compartir IRQ no sea un problema en la práctica, y un despliegue puro VoIP (sin tarjetas) no necesita preocuparse por ello en absoluto.

## Elegir una distribución de Linux

Asterisk se desarrolló inicialmente para ejecutarse en Linux. Sin embargo, también puede ejecutarse en BSD Unix o macOS. Si eres nuevo en Asterisk, prueba usar Linux primero, ya que es mucho más fácil. Asterisk tiene como objetivo oficial la familia RHEL (CentOS/RHEL/Fedora), Ubuntu y Debian. Buenas opciones prácticas hoy son **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS**, y **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux está al final de su vida, así que prefiere Rocky o AlmaLinux en sistemas de la familia RHEL. Para este libro usaré Ubuntu 24.04 LTS. Descarga la última imagen de servidor 24.04 point‑release del directorio oficial de lanzamientos a continuación (el nombre exacto del archivo incluye la versión point release actual, por ejemplo `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparar Linux para Asterisk

Antes de compilar Asterisk necesitas un sistema Linux funcional con los paquetes de compilación instalados. Instala **Ubuntu 24.04 LTS Server** en una máquina virtual o en una caja dedicada (usa la imagen de 64 bits; todo en este libro es de 64 bits, aunque Asterisk todavía soporta 32 bits x86). Usamos VirtualBox para este entrenamiento; puedes descargar la imagen desde <https://releases.ubuntu.com/24.04>. Instalar Linux en sí está fuera del alcance de este libro — el conocimiento básico de Linux es un requisito previo. Con Linux instalado, agregarás las dependencias de compilación de Asterisk (ver *Installing dependencies* más abajo) y luego compilarás Asterisk.

## Instalando Linux para Asterisk

Instale Linux como de costumbre, sin un escritorio gráfico. Durante la instalación, también habilite un agente de transferencia de correo (usamos **exim4**) — Asterisk lo necesitará para enviar notificaciones de buzón de voz a correo electrónico más adelante en este libro. **Caution:** instalar un sistema operativo borra el disco de destino. Si lo instala en hardware físico, haga una copia de seguridad de sus datos primero; instalar en una máquina virtual deja su host intacto. Arranque el instalador desde el ISO de Ubuntu Server (o la unidad óptica virtual de la VM) y responda las indicaciones — la mayoría son directas.

## Instalando dependencias

Para instalar Asterisk y DAHDI debe instalar muchas dependencias de software. La forma recomendada de hacerlo en Asterisk 22 es usar el script que se incluye con el árbol de fuentes, el cual conoce los nombres correctos de los paquetes para cada distribución soportada. Después de descargar y extraer el código fuente de Asterisk (ver “Compiling Asterisk” más abajo), ejecute:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. Inicie sesión como root (o use `sudo`).  
2. Si prefiere instalar las dependencias manualmente en un sistema Debian/Ubuntu, la lista de paquetes equivalente es:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

Observe que el código fuente de Asterisk ahora se aloja en Git, por lo que `subversion` ya no es necesario, y las versiones modernas de Debian/Ubuntu entregan `libncurses-dev` en lugar de los `libncurses5-dev` versionados. Prefiera `./contrib/scripts/install_prereq install` sobre una lista mantenida a mano, ya que el script siempre rastrea los nombres correctos de los paquetes para su distribución.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) es la arquitectura de controladores para tarjetas analógicas y digitales. Antes de instalar Asterisk es importante instalar DAHDI si planea usar interfaces analógicas o digitales. DAHDI sigue existiendo para tarjetas de telefonía analógica/digital pero es cada vez más un nicho — la mayoría de los despliegues modernos son puramente VoIP y pueden omitir esta sección por completo. Instale DAHDI solo si dispone de hardware de interfaz telefónica física. Obtenga los archivos fuente usando:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Descomprima los archivos usando:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compilando controladores DAHDI

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

make install-config DAHDI ha sido configurado. Si tiene hardware DAHDI, ahora se recomienda editar /etc/dahdi/modules para cargar soporte solo para el hardware DAHDI instalado en este sistema. Por defecto, el soporte para todo el hardware DAHDI se carga al iniciar DAHDI. Creo que el hardware DAHDI que tiene en su sistema es: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware Esta pantalla (arriba) le pide cambiar el archivo /etc/dahdi/modules para cargar solo los controladores requeridos para su configuración específica y mostrar el hardware detectado. Edite el archivo /etc/dahdi/modules y cargue solo el hardware necesario. En mi caso, estaba usando una máquina de pruebas con un Xorcom Astribank 6FXS y 2FXO. El archivo se muestra a continuación.

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

Reinicie su computadora y verifique la carga correcta de los controladores.

## Qué versión elegir

Como regla general, debe usar la versión que incluya las funciones requeridas. Asterisk sigue un modelo de lanzamiento que alterna versiones LTS (soporte a largo plazo) y versiones estándar. Al momento de esta edición, **Asterisk 22 es la versión LTS actual** (lanzada en octubre de 2024; la última versión puntual es 22.10.0), lo que la convierte en la mejor opción para elegir ahora. Asterisk 20 es la LTS anterior, y la versión 16 (utilizada en la primera edición) está al final de su vida. Para sistemas de producción, siempre elija una versión LTS.

## Compilando Asterisk

Si ya ha compilado software anteriormente, compilar Asterisk será una tarea fácil. Ejecute los siguientes comandos para compilar e instalar Asterisk. Recuerde, puede elegir qué aplicaciones y módulos construir usando `make menuselect`. Paso 1: Descargar el código fuente

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Paso 2: Instalar los prerrequisitos de compilación (ver "Installing dependencies" arriba)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Paso 3: Configurar la compilación

```
./configure
```

Paso 4: Seleccionar los módulos a compilar

```
make menuselect
```

Use `make menuselect` para instalar solo los módulos necesarios. En Asterisk 22 el canal SIP es **chan_pjsip** (construido por defecto); el antiguo **chan_sip** fue eliminado en Asterisk 21 y ya no existe. El *pass‑through* de Opus funciona de inmediato (el módulo interno `res_format_attr_opus` maneja la negociación SDP), pero el módulo de transcodificación **codec_opus** sigue siendo un binario externo y de código cerrado de Sangoma/Digium — al seleccionarlo en menuselect se descarga desde los servidores de Digium. El binario es gratuito. Consulte "Selecting modules with menuselect" más abajo para más detalles.

Paso 5: Compilar e instalar Asterisk, luego crear la configuración predeterminada y los archivos de ejemplo

```
make
make install
make samples
make config
ldconfig
```

`make install` instala los binarios y módulos, `make samples` escribe los archivos de configuración de ejemplo en `/etc/asterisk`, `make config` instala el script de inicio SysV init para su distribución detectada (p. ej. `/etc/init.d/asterisk` en Debian/Ubuntu), y `ldconfig` actualiza la caché de bibliotecas compartidas. Una unidad systemd también se incluye en el árbol de fuentes en `contrib/systemd/asterisk.service`, pero `make config` no la instala automáticamente — cópiela al lugar correspondiente si prefiere ejecutar Asterisk bajo systemd (ver más abajo).

### Selección de módulos con menuselect

`make menuselect` abre un menú basado en texto donde elige exactamente qué aplicaciones, codecs, canales y recursos compilar. Algunas notas específicas para Asterisk 22:

- **chan_pjsip** (bajo *Channel Drivers*) es el canal SIP moderno y está habilitado por defecto; es el único canal SIP en Asterisk 22.
- **codec_opus** (bajo *Codec Translators*) es un módulo **externo** (su entrada en menuselect dice "Download the Opus codec from Digium"); habilitarlo hace que `make` obtenga el binario gratuito y de código cerrado de Sangoma/Digium. El *pass‑through* de Opus no necesita módulo adicional. El módulo **codec_g729** de Sangoma también está disponible — el binario es gratuito para descargar, pero la transcodificación legal de G.729 requiere una licencia por canal adquirida.
- Seleccione los formatos de sonido y los idiomas que desea en los menús *Core Sound Packages*, *Music On Hold File Packages* y *Extras Sound Packages*; todo lo que marque allí se descarga e instala automáticamente durante `make install`.

Después de hacer sus selecciones, elija **Save & Exit** y continúe con `make`.

## Iniciando y deteniendo Asterisk

Con esta configuración mínima, es posible iniciar Asterisk con éxito. Para aprendizaje y depuración, puedes iniciar Asterisk en primer plano adjunto a la consola:

```
/usr/sbin/asterisk -vvvgc
```

Usa el comando CLI `core stop now` para apagar Asterisk:

```
*CLI> core stop now
```

### Iniciando Asterisk con systemd

En distribuciones Linux modernas (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), el gestor de servicios del sistema es **systemd**. Asterisk incluye una unidad systemd en `contrib/systemd/asterisk.service` dentro del árbol de fuentes; cópiala a `/etc/systemd/system/asterisk.service` y ejecuta `systemctl daemon-reload`. Una vez instalada, la forma recomendada de ejecutar Asterisk en producción es a través de `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Una vez que Asterisk se está ejecutando como servicio, conéctate a su CLI con `asterisk -r` (conectar) o `asterisk -rvvv` (conectar con salida detallada).

En sistemas más antiguos Asterisk se iniciaba mediante el script de inicio legado SysV (`/etc/init.d/asterisk`) y el wrapper **safe_asterisk**, que reiniciaba Asterisk automáticamente si se bloqueaba. Con systemd, el reinicio automático lo maneja la directiva `Restart=` del archivo de unidad, por lo que `safe_asterisk` generalmente ya no es necesario. El enfoque legado init/`safe_asterisk` todavía funciona pero está obsoleto en distribuciones basadas en systemd.

### Opciones de tiempo de ejecución de Asterisk

El proceso de inicio de Asterisk es muy sencillo. Si Asterisk se ejecuta sin ningún parámetro, se lanza como un daemon.

```
/sbin/asterisk
```

Puedes acceder a la consola de Asterisk ejecutando el siguiente comando. Ten en cuenta que se pueden ejecutar más de un proceso de consola al mismo tiempo.

```
/sbin/asterisk -r
```

### Opciones de tiempo de ejecución disponibles para Asterisk

Puedes mostrar las opciones de tiempo de ejecución disponibles usando `asterisk -h`

```text
sipast:/usr/src/asterisk-22.x.y# asterisk -h
Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others.
Usage: asterisk [OPTIONS]
Valid Options:
   -V              Display version number and exit
   -C <configfile> Use an alternate configuration file
   -G <group>      Run as a group other than the caller
   -U <user>       Run as a user other than the caller
   -c              Provide console CLI
   -d              Increase debugging (multiple d's = more debugging)
   -f              Do not fork
   -F              Always fork
   -g              Dump core in case of a crash
   -h              This help screen
   -i              Initialize crypto keys at startup
   -L <load>       Limit the maximum load average before rejecting new calls
   -M <value>      Limit the maximum number of calls to the specified value
   -m              Mute debugging and console output on the console
   -n              Disable console colorization. Can be used only at startup.
   -p              Run as pseudo-realtime thread
   -q              Quiet mode (suppress output)
   -r              Connect to Asterisk on this machine
   -R              Same as -r, except attempt to reconnect if disconnected
   -s <socket>     Connect to Asterisk via socket <socket> (only valid with -r)
   -t              Record soundfiles in /var/tmp and move them where they
                   belong after they are done
   -T              Display the time in [Mmm dd hh:mm:ss] format for each line
                   of output to the CLI. Cannot be used with remote console mode.
   -v              Increase verbosity (multiple v's = more verbose)
   -x <cmd>        Execute command <cmd> (implies -r)
   -X              Enable use of #exec in asterisk.conf
   -W              Adjust terminal colors to compensate for a light background
```

## Directorios de instalación

Asterisk se instala en varios directorios, los cuales pueden modificarse en el archivo asterisk.conf. Para propósitos de entrenamiento cambiaría el nivel de verbose de 3 a 15; para producción lo mantenga en 3. Las opciones `maxcalls` y `maxload` son buenas opciones para proteger su sistema de sobrecarga.

### asterisk.conf (extracto)

La sección `[directories]` define dónde Asterisk guarda su configuración, módulos, datos, spool y registros:

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
```

La sección `[options]` contiene ajustes de tiempo de ejecución. Las opciones más útiles que debe conocer se muestran a continuación (descomente para habilitar); el archivo incluye muchas más, cada una documentada con un comentario en línea:

```
[options]
;verbose = 3      ; Console verbosity (raise to 15 for training, keep 3 in production)
;debug = 3        ; Debug level
;maxcalls = 10    ; Maximum number of simultaneous calls allowed
;maxload = 0.9    ; Stop accepting new calls when load average exceeds this
;maxfiles = 1000  ; Maximum number of open files
;runuser = asterisk   ; The user to run as
;rungroup = asterisk  ; The group to run as
```

## Archivos de registro y rotación de registros

Asterisk PBX registra sus mensajes en `/var/log/asterisk`. El registro está controlado por `logger.conf`. La parte clave es la sección `[logfiles]`, donde cada línea define un canal de registro y los niveles de mensaje que captura (extracto):

```ini
; logger.conf (excerpt)
[general]
;dateformat = %F %T.%3q          ; ISO 8601 timestamps, with milliseconds

[logfiles]
; <logger_name> => [formatter]<levels>
console  => notice,warning,error
messages => notice,warning,error
full     => notice,warning,error,verbose,dtmf,fax
security => security              ; PJSIP/auth security events (used by Fail2Ban)
```

Después de editar, aplique el cambio con `logger reload` y confirme los canales con `logger show channels`:

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

Los archivos de registro pueden crecer rápidamente, por lo que deben rotarse con el demonio del sistema `logrotate` — añada un archivo bajo `/etc/logrotate.d/`:

```text
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

Se puede obtener más información sobre logrotate usando:

```
#man logrotate
```

## Desinstalando Asterisk

Para desinstalar Asterisk, use:

```
make uninstall
```

Para desinstalar Asterisk y todos los archivos de configuración, use:

```
make uninstall-all
```

## Notas de instalación de Asterisk

Esta sección ofrecerá algunos consejos sobre los problemas que deben abordarse antes de instalar Asterisk.

### Sistemas de producción

Si Asterisk se instala en un entorno de producción, debe prestar atención al diseño del sistema. Un servidor debe estar optimizado de manera que los sistemas de telefonía tengan prioridad sobre otros procesos del sistema. Asterisk no debe ejecutarse junto con software intensivo en procesador como X‑Windows. Si necesita ejecutar procesos intensivos en CPU (p. ej., una base de datos enorme), use un servidor separado. En términos generales, Asterisk es susceptible a variaciones en el rendimiento del hardware. Por lo tanto, intente usar Asterisk en un entorno de hardware que no requiera más del 40 % de utilización de la CPU.

### Consejos de red

Si planea usar teléfonos IP, es importante que preste atención a su red. Los protocolos de voz son muy buenos y resistentes a la latencia e incluso a los jitter; sin embargo, si usa una red de área local mal configurada, la calidad de voz se verá afectada. Sólo es posible garantizar una buena calidad de voz utilizando calidad de servicio (QoS) en switches y routers. La voz en una red de área local tiende a ser buena, pero incluso en un entorno LAN, si tiene hubs de 10 Mbps con demasiadas colisiones, terminará con una voz distorsionada o de mala calidad. Siga estas recomendaciones para asegurar la mejor calidad de voz posible:

- Use QoS de extremo a extremo si es posible o económicamente factible. Con QoS de extremo a extremo, la calidad de voz es perfecta. ¡Sin excusas!
- Evite usar hubs de 10/100 Mbps para voz en un entorno de producción. Las colisiones pueden imponer jitter en la red. Se prefieren los 10/100 Mbps full‑duplex porque no se producen colisiones.
- Use VLANs para separar las transmisiones innecesarias de la red de voz. No quiere que un virus destruya su red de voz con transmisiones ARP.
- Eduque a los usuarios sobre las expectativas en una red de voz. Sin QoS, no afirme que la voz será perfecta, ya que en la mayoría de los casos no lo será. Se logrará una calidad de voz similar a la de un teléfono móvil en la mayoría de los casos. Use teléfonos de calidad, ya que los problemas de firmware y diseño de hardware son comunes.

## Resumen

En este capítulo, has aprendido sobre los requisitos mínimos de hardware, así como cómo descargar, instalar y compilar Asterisk. Asterisk debe ejecutarse con un usuario que no sea root por razones de seguridad. Debes verificar tu entorno de red antes de iniciar el entorno de producción.

## Quiz

1. En Asterisk 22, ¿qué controlador de canal proporciona soporte SIP, y qué ocurrió con el antiguo `chan_sip`?
   - A. `chan_sip` sigue siendo el predeterminado; `chan_pjsip` es opcional.
   - B. `chan_pjsip` es el canal SIP predeterminado; `chan_sip` se eliminó en Asterisk 21 y ya no existe.
   - C. Ambos se compilan por defecto y usted elige entre ellos en tiempo de ejecución.
   - D. El soporte SIP se eliminó por completo en favor de IAX2.
2. Las tarjetas de interfaz telefónica para Asterisk suelen tener procesadores de señal digital (DSP) integrados y por lo tanto no necesitan mucho CPU del PC.
   - A. Verdadero
   - B. Falso
3. Si desea una calidad de voz perfecta, necesita implementar calidad de servicio de extremo a extremo (QoS).
   - A. Verdadero
   - B. Falso
4. Siempre debe elegir la última versión de Asterisk, ya que es la más estable.
   - A. Verdadero
   - B. Falso
5. ¿Cuál es la forma recomendada de instalar las dependencias de compilación para Asterisk 22?
6. Si no tiene una tarjeta de interfaz TDM, aún tendrá una fuente de temporización interna para sincronización, provista por el módulo `res_timing_timerfd` en Linux. Esta temporización es usada por aplicaciones como ________ y ________.
7. Al instalar Asterisk es mejor dejar fuera entornos de escritorio como GNOME o KDE, porque las interfaces gráficas consumen ciclos de CPU.
   - A. Verdadero
   - B. Falso
8. Los archivos de configuración de Asterisk se encuentran en el directorio ________.
9. Para instalar los archivos de configuración de ejemplo de Asterisk, escriba el comando: ________
10. ¿Por qué es importante ejecutar Asterisk como un usuario que no sea root?

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
