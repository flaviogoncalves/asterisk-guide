# Deployment, monitoring & scaling

Lograr que Asterisk responda una llamada en un laboratorio es una cosa; ejecutarlo como un servicio que sobreviva a fallas, reinicios, actualizaciones y atacantes — y que puedas observar, respaldar y hacer crecer — es otra. Este capítulo trata todo lo que ocurre *después* de que el dialplan funciona. Comenzamos con el supervisor que mantiene Asterisk activo (systemd), pasamos a empaquetarlo en un contenedor (usando el laboratorio Docker propio del libro como ejemplo práctico), luego cubrimos la gestión de configuración y copias de seguridad, el monitoreo y la observabilidad, y finalmente los patrones que utilizas cuando un solo servidor no es suficiente: alta disponibilidad y escalado, y las realidades de alojar en la nube.

Todo lo mostrado está verificado contra el laboratorio Asterisk 22 del libro en `lab/` — el mismo contenedor que has estado construyendo a lo largo del libro.

## Objetivos

Al final de este capítulo, deberías poder:

- Ejecutar Asterisk 22 de forma fiable bajo systemd, como usuario sin privilegios, con reinicio automático
- Contenerizar Asterisk con Docker y comprender los compromisos de red
- Mantener `/etc/asterisk` en control de versiones y respaldar el estado correcto
- Monitorear un sistema en ejecución a través de la CLI, CDR/CEL, AMI/ARI y métricas
- Aplicar patrones de alta disponibilidad activo/standby y escalado horizontal
- Alojar Asterisk en la nube de forma segura detrás de NAT y un firewall

## Ejecutando Asterisk bajo systemd

En cada distribución Linux actual — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — el gestor de servicios es **systemd**. El capítulo de instalación mostró que el paso `make config` (ejecutado durante `make install`) instala un script de inicio de la distribución (`/etc/init.d/asterisk` en Debian, un script `rc.d` en RedHat), que systemd envuelve automáticamente como un servicio; Asterisk también incluye una unidad nativa de systemd bajo `contrib/systemd/asterisk.service` que puedes instalar en su lugar para un control más fino.  
De cualquier forma, systemd es el método soportado y de producción para ejecutar Asterisk. Consulta *Installing Asterisk 22* para la compilación en sí; aquí nos centramos en lo que el servicio te brinda y cómo operarlo.

### La unidad de servicio y su ciclo de vida

Una vez que `make config` ha instalado el servicio, el ciclo de vida es el típico de systemd:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Algunas notas operativas:

- **`restart` vs. una recarga elegante.** `systemctl restart` finaliza el proceso y corta todas las llamadas. Para cambios de configuración casi nunca deseas eso — usa la CLI de Asterisk en su lugar: `asterisk -rx 'core reload'` (o una recarga específica de módulo como `pjsip reload`). Reserva `systemctl restart` para actualizaciones o un proceso atascado.  
- **Adjuntarse al daemon en ejecución.** Con Asterisk ejecutándose como servicio, abre su consola con `asterisk -r` (o `asterisk -rvvv` para salida detallada). Esto se conecta al daemon ya en ejecución a través de su socket de control; no inicia una segunda copia.

### `Restart=` reemplaza safe_asterisk

Históricamente Asterisk se lanzaba mediante el wrapper **safe_asterisk**, un script de shell que re‑iniciaba Asterisk si se bloqueaba. Bajo systemd esa tarea pertenece a la directiva `Restart=` de la unidad — systemd detecta la salida del proceso y lo vuelve a iniciar, con retroceso controlado por `RestartSec=` y protección contra bucles de fallos mediante `StartLimitIntervalSec=`/`StartLimitBurst=`. Así, en un host con systemd **safe_asterisk está** **suplantado** y generalmente es innecesario. Si tu unidad distribuida no lo establece ya, una sobrescritura drop‑in es la forma limpia de añadir reinicio‑al‑fallar sin editar el archivo empaquetado:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Aplícala con `systemctl daemon-reload && systemctl restart asterisk`. Usar un drop‑in (en lugar de editar la unidad instalada) significa que un futuro `make config` no sobrescribirá tu cambio.

### Ejecutando como usuario no root

Asterisk no debe ejecutarse como root en producción — un error de código remoto en un proceso que se ejecuta como root compromete todo el host, mientras que el mismo error en un proceso sin privilegios queda contenido. Hay dos lugares complementarios donde se aplica esta política:

- **La unidad / asterisk.conf.** La unidad empaquetada normalmente ejecuta Asterisk como el usuario y grupo `asterisk`. También puedes (o en su lugar) establecer `runuser` y `rungroup` en la sección `[options]` de `asterisk.conf`, que el daemon respeta cuando deja de tener privilegios después de enlazar:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Propiedad de archivos.** Los directorios de tiempo de ejecución deben ser escribibles por ese usuario. Después de crear la cuenta, asegura la propiedad:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Debido a que SIP (5060) y RTP (10000+) son puertos altos, Asterisk **no** necesita root para enlazarlos — solo los puertos privilegiados tipo puerto‑25 lo requerirían, lo cual Asterisk no usa. Ejecutarse sin privilegios es, por tanto, gratuito. (El capítulo de Seguridad amplía por qué esto importa; véase *Asterisk Security*.)

## Containerizando Asterisk

Un contenedor empaqueta Asterisk y sus dependencias exactas en una única imagen inmutable, de modo que lo que pruebas es byte‑por‑byte lo que envías. El compromiso está en los medios en tiempo real: un servidor SIP es sensible a la latencia y necesita un rango amplio y predecible de puertos UDP accesibles desde el exterior, y el networking de contenedores puede interferir. El resto de esta sección recorre el laboratorio propio del libro — `lab/Dockerfile` y `lab/docker-compose.yml` — como un ejemplo concreto y funcional, y luego explica la única trampa que todos encuentran: RTP y networking puenteado.

### La imagen: compilando Asterisk desde el código fuente

El `Dockerfile` del laboratorio compila Asterisk 22 desde el código fuente en Debian 12. Su estructura vale la pena leerla aunque nunca escribas una tú mismo:

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Tres cosas a destacar:

- **La versión está fijada** (`ARG ASTERISK_VERSION=22.10.0`). La reproducibilidad es el
  objetivo principal de la contenedorización — actualízala deliberadamente, recompila, vuelve a probar.
- **`--with-pjproject-bundled` y `--with-jansson-bundled`** construyen la pila SIP
  con la versión que coincide con Asterisk, por lo que dependes de menos paquetes apt y nunca te enfrentas a un
  PJSIP de la distribución que esté desfasado.
- **`CMD ["asterisk", "-f", "-vvv"]`** ejecuta Asterisk en el *primer plano* (`-f`, "no fork"). Esta es la diferencia clave respecto a un host systemd: el proceso principal de un contenedor
  no debe convertirse en demonio, o el contenedor saldría inmediatamente. Así que en un contenedor **no** utilizas la unidad systemd en absoluto — el runtime del contenedor (Docker, más la política `restart:`)
  se convierte en el supervisor que la `Restart=` de la unidad era en una VM.

### Montaje enlazado `/etc/asterisk`

La imagen contiene deliberadamente **ninguna** configuración. En su lugar `docker-compose.yml`
monta enlazado el directorio de configuración del host en:

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro` asigna el directorio controlado por versiones `lab/asterisk/etc` al **`/etc/asterisk`** del contenedor, en modo solo lectura (`:ro`). El beneficio es grande: la imagen permanece inmutable y reutilizable, mientras que la configuración vive en el host donde puede ser editada y, lo que es crucial, mantenida en git (sección siguiente). Para aplicar un cambio de configuración editas el archivo y recargas — `docker compose exec asterisk asterisk -rx 'core reload'` — sin necesidad de recompilar. `restart: unless-stopped` es el equivalente a nivel de compose del **`Restart=`** de systemd: Docker reinicia el contenedor si Asterisk finaliza, pero no si lo detienes deliberadamente.

### Host vs. bridged networking — el problema de RTP

Este es el fallo más común en contenedores Asterisk, por lo que vale la pena entenderlo con precisión. Por defecto Docker coloca un contenedor en una red **bridged** y publicas puertos individuales con `ports:`. La señalización funciona bien — 5060 es un puerto. El problema está en los medios: RTP usa un *rango* de puertos UDP (el **`rtp.conf`** del laboratorio establece `rtpstart=10000` / `rtpend=10100`), y **cada** puerto que pueda transportar audio debe ser publicado.

El laboratorio hace exactamente eso:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Note the RTP publish range (`10000-10100`) matches `rtp.conf` exactly. Get this wrong —
publish too few ports, or a different range than `rtp.conf` — and calls connect but
have **one-way or no audio**, because the RTP packets land on a port Docker is not
forwarding. Two further cautions with bridged mode:

- **Publishing thousands of ports is slow and heavy.** A production RTP range is
  typically 10000–20000. Docker creating ~10000 userland proxy forwards is expensive at
  start-up and adds a hop in the media path. The lab keeps a deliberately small
  100-port range because it only ever runs one or two test calls.
- **NAT in the SDP.** Behind the bridge, Asterisk sees its private container IP and may
  advertise it in SDP. On a public host you must tell PJSIP its external address with
  `external_media_address` / `external_signaling_address` on the transport (and set
  `local_net`), exactly as you would behind any NAT — see *Cloud hosting* below.

The alternative is **host networking** (`network_mode: host`), which removes the bridge
entirely: the container shares the host's network stack, so 5060 and the whole RTP
range are reachable with no port publishing and no extra media hop. This is the
recommended mode for a real Asterisk container — it sidesteps the RTP-range problem
completely. Its cost is isolation: the container can bind any host port and you lose
compose's per-service network. (Host networking is a Linux feature; on Docker Desktop
for macOS/Windows it behaves differently, which is partly why this teaching lab uses
explicit published ports instead.)

### Volúmenes persistentes para spool y voicemail

Una capa escribible del contenedor es **efímera** — destruye el contenedor y todo lo que
escribió desaparece. Para Asterisk eso significa que el voicemail, las grabaciones, el spool de llamadas salientes
y la base de datos local se perderían en cada `docker compose up --build`. La configuración
sobrevive porque se monta desde el host; el *estado* necesita el mismo tratamiento.
Dentro del contenedor los árboles relevantes son:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(The lab's running container shows exactly these — `/var/spool/asterisk` contains
`voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` holds
`astdb.sqlite3`.) To preserve them, mount named volumes for the directories that hold
state you care about:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

El laboratorio de enseñanza omite esto a propósito — es sin estado y reproducible por diseño, de modo que cada `up` es una hoja limpia — pero un contenedor de producción **debe** tenerlos, o perderás el buzón de voz en el primer redeploy.

## Gestión de configuración y copias de seguridad

El bind‑mount anterior sugiere el modelo correcto: trate `/etc/asterisk` como **code** y
el resto como **data**.

### Mantenga `/etc/asterisk` bajo control de versiones

El directorio de configuración es un conjunto plano de archivos de texto sin secretos que no puedan ser
plantillados — es ideal para git. Inicialice un repositorio en `/etc/asterisk` (o, como hace el laboratorio,
mantenga la configuración junto al proyecto y haga bind‑mount). Beneficios:

- Cada cambio es revisable y reversible (`git diff`, `git revert`).
- Tiene un registro de auditoría de quién cambió qué y cuándo.
- Combinado con una imagen de contenedor, un commit de configuración conocido‑bueno más una etiqueta de imagen fijada
  describen completamente una implementación.

Un par de advertencias específicas a la configuración de Asterisk:

- **Secrets.** `pjsip.conf` (y `manager.conf`, `ari.conf`) contienen contraseñas. No
  comprometa secretos reales a un repositorio compartido en texto plano — plantíllelos (un archivo por
  entorno, o un gestor de secretos / sustitución de entorno en tiempo de despliegue) y mantenga
  solo marcadores de posición en git. Las contraseñas triviales estilo `Lab-6001-secret` del laboratorio están bien
  *solo* porque viven en una subred privada de Docker.
- **Plantillado por entorno.** Los valores en tiempo real que difieren entre dev, staging
  y producción (direcciones de enlace, IPs externas, credenciales de trunk, URLs de bases de datos) son
  exactamente las líneas que plantille, manteniendo la mayor parte de la configuración idéntica entre
  entornos.

### Qué respaldar

La configuración en git cubre el dialplan y los endpoints, pero un PBX en vivo acumula
*state* que no está en ningún archivo de configuración. Una copia de seguridad completa es:

| What | Where | Why |
|------|-------|-----|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (also in git) |
| Voicemail & recordings | `/var/spool/asterisk/` | datos de usuario — irremplazables |
| Internal database | `/var/lib/asterisk/astdb.sqlite3` | claves `DB()`, estado de dispositivos |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` or SQL store | facturación & historial |
| External databases | su MySQL/PostgreSQL | realtime, CDR, voicemail |

El **astdb** merece una nota: es el pequeño almacén interno de pares clave/valor de Asterisk (un
archivo SQLite en `/var/lib/asterisk/astdb.sqlite3`) usado por funciones de dialplan `DB()`,
estados de dispositivos, configuraciones de follow‑me y similares. Puede volcarlo para inspección o copia de seguridad
desde la CLI:

```
asterisk -rx 'database show'
```

Si su CDR/CEL o voicemail o la configuración de PJSIP reside en una base de datos externa (ver
*Asterisk Real-Time* y *Asterisk Call Detail Records*), esa base de datos es ahora la
fuente de verdad para esos datos y debe estar en su rotación normal de copias de seguridad de bases de datos —
respaldar solo `/etc/asterisk` no es suficiente.

## Monitoreo y observabilidad

No puedes operar lo que no puedes ver. Asterisk expone su estado en cuatro niveles, desde una rápida mirada humana hasta una canalización de métricas: el **CLI**, los registros **CDR/CEL**, los eventos **AMI/ARI**, y los **exportadores de métricas**.

### Chequeos de salud del CLI

La verificación más rápida de “¿está saludable?” es el CLI. Los comandos a continuación se ejecutan en vivo contra el laboratorio. Primero los canales:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` en un sistema tranquilo es normal; en uno ocupado esto es su concurrencia en tiempo real. `core show uptime` confirma que el proceso no se ha estado reiniciando bajo su control:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Para la salud de SIP, `pjsip show endpoints` muestra cada endpoint y si sus contactos registrados son accesibles. Desde el laboratorio:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` aquí simplemente significa que ningún teléfono está registrado actualmente en esos endpoints (el laboratorio no tiene clientes activos) — una vez que un softphone se registra y `qualify` lo confirma, el estado muestra el contacto como alcanzable. Comandos complementarios: `pjsip show contacts` (registraciones actuales y tiempo de ida y vuelta), `pjsip show transports` y `pjsip show aor <name>` para un AOR. Estas son las herramientas cotidianas de “¿por qué no se puede alcanzar la extensión X?”.

### CDR y CEL

Cada llamada genera un **Call Detail Record** (CDR); **Channel Event Logging** (CEL) agrega eventos más detallados por canal. Confirme que el CDR está activo y qué backend lo almacena:

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

The lab shows `(none)` under registered backends because the minimal lab config loads
no CDR storage module — so records are computed but written nowhere. In production you
load a backend (CSV, or `cdr_odbc`/`cdr_adaptive_odbc` into MySQL/PostgreSQL) and that
becomes your billing and history source. CEL is **disabled by default** (`cel show
status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` only
when you need event-level detail. Both are covered in depth in *Asterisk Call Detail
Records*; for monitoring, the point is that CDR/CEL are your *historical* record, where
the CLI is your *live* view.

### AMI and ARI events

For programmatic, real-time monitoring you want a push feed of events rather than
polling the CLI:

- **AMI (Asterisk Manager Interface)** is the long-standing TCP event/command protocol
  (`manager.conf`). Subscribe and you receive `Newchannel`, `Hangup`, `DialBegin`,
  `BridgeEnter`, `PeerStatus` and similar events as calls happen — the backbone of wallboards
  and call-accounting tools. In the lab AMI is disabled by default (`manager show settings`
  reports `Manager (AMI): No`); you enable and lock it down in `manager.conf`.
- **ARI (Asterisk REST Interface)** is the modern HTTP + WebSocket interface
  (`ari.conf`, served by the built-in HTTP server). It gives a JSON event stream and
  fine-grained call control — the right choice for new integrations.

Both are detailed in *Extending Asterisk with AMI and AGI* and *The Asterisk REST
Interface (ARI)*. The deployment-relevant
warning: **AMI and ARI are powerful and must never be exposed to the internet.** Bind the
HTTP server to localhost or a management network, use strong unique secrets, and
firewall the ports — see *Asterisk Security*.

### Métricas: Prometheus y Grafana

Para paneles y alertas, Asterisk 22 incluye un exportador de Prometheus,
**`res_prometheus.so`** (un módulo con nivel de soporte *extendido*), que expone métricas
en un endpoint HTTP que un servidor Prometheus recopila. Junto a las métricas del proceso central, incluye proveedores plug‑in que cubren canales, llamadas, endpoints, puentes y registros salientes de PJSIP.

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

Puede confirmar que el módulo está presente en la compilación del laboratorio:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

Muestra `Not Running` porque el laboratorio no lo configura ni lo carga; habilitarlo (`prometheus.conf` más el servidor HTTP) convierte Asterisk en un objetivo de Prometheus. Apunte Prometheus al endpoint de raspado y Grafana a Prometheus, y obtendrá paneles de series temporales (llamadas concurrentes, registros, tendencias ASR/ACD) y alertas (p. ej., "llamadas activas caídas a cero" o "fallos de registro en pico"). Para equipos que ya ejecutan Prometheus/Grafana esta es la forma natural de integrar Asterisk en la observabilidad existente, en lugar de analizar la salida del CLI.

### Códigos de respuesta SIP que vale la pena vigilar

Sea cual sea la cadena, algunos resultados SIP indican problemas y merecen generar alertas: fallos sostenidos de desafío `401`/`407` o `403 Forbidden` sugieren un ataque de fuerza bruta o una tormenta de credenciales mal configuradas (ver también Fail2Ban en *Asterisk Security*); `503 Service Unavailable` indica un servidor o trunk sobrecargado o congestionado; y un pico en `408 Request Timeout`/`480 Temporarily Unavailable` normalmente significa que los endpoints se han vuelto inalcanzables (tiempo de espera NAT, fallos de qualify).

## Alta disponibilidad y escalado

Un servidor Asterisk es un punto único de falla y tiene un techo finito de llamadas. Los dos
problemas — *mantenerse activo* y *crecer* — tienen respuestas diferentes.

### Activo/standby con una IP flotante

El patrón clásico y bien recorrido de HA para Asterisk es **activo/standby** (no
activo/activo — el estado de la llamada en Asterisk es difícil de compartir en vivo). Dos servidores idénticos,
uno activo, uno en standby, comparten una **IP flotante (virtual)** gestionada por un administrador de clúster
como **keepalived** (VRRP) o **Pacemaker/Corosync**. Los teléfonos y trunks se registran en
la IP flotante, no en ninguno de los hosts reales. Si el nodo activo falla su verificación de salud, la
IP flotante pasa al standby, que asume el control.

La advertencia honesta: un failover de IP **corta las llamadas en curso** — Asterisk no
replica el estado de los canales en vivo entre nodos, por lo que cualquiera que esté en medio de una llamada debe volver a marcar. Las registraciones
se restablecen dentro de un ciclo de calificación/registro. Lo que el failover te brinda es que el
*servicio* se recupera en segundos sin intervención manual, lo cual para la mayoría de los PBX es exactamente
el objetivo. Para que el standby pueda realmente tomar el control, ambos nodos necesitan la misma
configuración (tu `/etc/asterisk` versionado en git, desplegado idénticamente) y el mismo *estado* —
que es el siguiente punto.

### Externalizar el estado con PJSIP Realtime

Activo/standby solo funciona si el standby conoce los mismos endpoints y
registraciones que el nodo activo. La forma de lograr eso es **dejar de mantener el estado en
archivos planos en una sola máquina** y moverlo a una base de datos compartida que ambos nodos lean. **PJSIP
Realtime** (Sorcery respaldado por una base de datos) hace exactamente esto: endpoints, AORs, auths —
y, lo que es importante, **registraciones** (la tabla `ps_contacts`) — viven en MySQL/PostgreSQL
en lugar de `pjsip.conf` y la memoria local. Ambos nodos Asterisk apuntan a la misma base de datos,
de modo que un teléfono registrado a través de un nodo es visible para el otro. Esto se cubre en
*Asterisk Real-Time* (la sección PJSIP Realtime / Sorcery); aquí el punto de despliegue es
que **externalizar el estado es el requisito previo tanto para HA como para el escalado horizontal** —
sin ello, cada nodo es una isla.

Aplica la misma lógica al resto de tu estado: CDR/CEL en un almacén SQL compartido, buzón de voz
en almacenamiento compartido/replicado (o `ODBC_STORAGE`), y las claves astdb de las que dependes en una
base de datos. Una vez que el estado es externo, los nodos Asterisk se vuelven más intercambiables
como front‑ends.

### Proxies SIP al frente (OpenSIPS)

Para escalar *más allá* de la capacidad de un solo servidor colocas un **proxy SIP/balanceador de carga** al frente de
un conjunto de servidores de medios Asterisk. **OpenSIPS** es un proxy SIP construido a propósito, muy
de alto rendimiento (manejan cientos de miles de registraciones y enrutan
señalización sin tocar los medios). El proxy presenta una única dirección SIP al mundo,
mantiene el servicio de registro/ubicación y distribuye las llamadas entre los back‑ends Asterisk.
Esta separación — una capa ligera de proxy que hace registro y enrutamiento, una
capa Asterisk escalable horizontalmente que realiza el procesamiento real de llamadas (IVR, colas,
conferencias, transcodificación) — es cómo los despliegues grandes crecen más allá de una sola caja. (La plataforma SipPulse
usa OpenSIPS al frente de sus servidores de medios/aplicación precisamente por esta razón.)

### Escalado de medios

El proxy distribuye la *señalización* de forma económica; **los medios son el recurso costoso**. Relé de RTP,
y especialmente la transcodificación entre codecs (p. ej. Opus ↔ G.711) o la ejecución de grandes
conferencias, depende de la CPU y es lo que realmente limita un servidor. Estrategias:

- **Evitar la transcodificación** siempre que sea posible — negociar un

## Cloud hosting

Ejecutar Asterisk en una VM en la nube (AWS, GCP, Azure, un VPS) es común y funciona bien, pero la
red de la nube está **NAT‑eada y con firewall por defecto**, lo que compite con SIP. Las
preocupaciones específicas del despliegue son las siguientes.

### NAT y el SDP

Una VM en la nube casi siempre tiene una IP **privada** en su NIC y una **pública** separada que
el proveedor NATea hacia ella. Si Asterisk anuncia la IP privada en SDP, los teléfonos remotos envían
RTP a un agujero negro — el clásico síntoma de un solo sentido/sin audio. Indique a PJSIP su identidad
pública en el transporte:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` hace que Asterisk reescriba la dirección que anuncia a pares públicos, mientras que
`local_net` le indica qué pares son locales (y *no* deben ser reescritos). Esto es lo mismo que el
manejo de NAT discutido para el networking Docker puenteado arriba — una VM en la nube está,
en efecto, detrás de NAT.

### Firewall y el rango RTP

Dos firewalls suelen aplicarse en una VM en la nube: el **grupo de seguridad del proveedor** / ACL
de red, y el **firewall del host** iptables. Ambos deben abrir los mismos puertos, y la política es la
del capítulo Seguridad. El conjunto de reglas de la 1ª edición recuperado
(`docs/legacy-labs/configs/Lab7/rules.v4`) captura la forma — aceptar SIP y el rango RTP, aceptar conexiones establecidas/relacionadas,
descartar el resto:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Dos correcciones que el capítulo Seguridad hace y que importan aquí: abrir **5061 en TCP** (no
UDP) si usa SIP/TLS, y recordar que el rango UDP RTP en su firewall debe coincidir
exactamente con `rtpstart`/`rtpend` en `rtp.conf` — el mismo rango que publica en un contenedor.
No duplique la construcción iptables/Fail2Ban aquí; **siga las secciones firewall, Fail2Ban y
TLS/SRTP de *Asterisk Security*** (Fail2Ban vigila el canal de registro `security` que el laboratorio ya
activa en `logger.conf`) y aplique esa política tanto en el firewall del host como en el grupo de seguridad
de la nube.

### Latencia, región y el SBC

- **Elija una región cercana a sus usuarios.** La voz es sensible a la latencia — una latencia
  de un solo sentido de boca a oído superior a ~150 ms se percibe. Aloje la VM en la región más
  cercana al grueso de sus teléfonos y trunks; el tráfico multimedia intercontinental suena peor.
- **Coloque un SBC al frente para cualquier despliegue expuesto a Internet.** Un **Session Border
  Controller** termina SIP/RTP en el borde, oculta su topología, normaliza NAT y absorbe tráfico
  DoS y de escaneo antes de que llegue a Asterisk. La recomendación central del capítulo Seguridad —
  *no exponer Asterisk sin protección a Internet* — se aplica doblemente en la nube, donde la IP
  pública de su VM es escaneada en minutos después de iniciarse. Un SBC (o, como mínimo, un
  proxy SIP endurecido como OpenSIPS más Fail2Ban) es el estándar en el borde.

## Resumen

El despliegue es donde un dialplan funcional se convierte en un servicio confiable. En una VM, ejecuta
Asterisk bajo **systemd** como un usuario **non-root**, dejando que la unidad `Restart=` lo
mantenga activo (safe_asterisk está obsoleto) y usando `core reload` en lugar de `systemctl
restart` para los cambios de configuración. **Containerizar** con Docker — como hace el laboratorio del libro —
te brinda una imagen inmutable, fijada, con la configuración **bind-mounted** desde un `/etc/asterisk` git; el problema es el medio, así que usa **host networking** o publica un rango de puertos RTP que **coincida exactamente con `rtp.conf`**, y monta **volúmenes persistentes** para
spool/voicemail/astdb de modo que el estado sobreviva a un redeploy. Trata la configuración como código y **haz copia de seguridad del
estado** que la configuración no captura: voicemail, grabaciones, `astdb.sqlite3` y CDR/CEL.
**Observa** el sistema en cuatro niveles — la CLI (`core show channels`, `pjsip show
endpoints`) para la vista en tiempo real, **CDR/CEL** para el historial, **AMI/ARI** para eventos programáticos,
y el exportador **`res_prometheus`** a Grafana para paneles y alertas — mientras mantienes AMI/ARI fuera de Internet público. Para **mantenerte activo**, ejecuta activo/standby con una **IP flotante** (aceptando que el failover interrumpe llamadas en curso); para **crecer**, externaliza el estado con **PJSIP Realtime**, coloca un pool de servidores de medios con **OpenSIPS**, y minimiza la transcodificación porque **media — no registrations — es lo que limita un servidor**.
Finalmente, en la **nube**, trata la VM como detrás de NAT (`external_media_address`,
`local_net`), abre el firewall según el capítulo de Seguridad tanto en el host como en el grupo de seguridad del proveedor, elige una región de baja latencia y nunca expongas Asterisk sin protección — coloca un **SBC** en el borde.

## Quiz

1. En un host con systemd, ¿qué reemplaza la antigua tarea del wrapper `safe_asterisk` de reiniciar un Asterisk que se ha bloqueado?
   - A. Un trabajo cron
   - B. La directiva `Restart=` del archivo de unidad
   - C. `systemctl enable`
   - D. El astdb
2. Para aplicar un cambio de configuración a un Asterisk en ejecución **sin colgar llamadas**, debe:
   - A. `systemctl restart asterisk`
   - B. Reiniciar el servidor
   - C. `asterisk -rx 'core reload'`
   - D. Reconstruir la imagen del contenedor
3. Un Asterisk contenedorizado (red puente) conecta llamadas pero **no tiene audio**. La causa más probable es:
   - A. El dialplan está equivocado
   - B. El rango de puertos UDP RTP publicado no coincide con `rtpstart`/`rtpend` en `rtp.conf`
   - C. CDR está deshabilitado
   - D. La CLI es inaccesible
4. ¿Qué directorios deben montarse como **volúmenes persistentes** para que una redeplegación del contenedor no pierda el estado? (marque todas las que correspondan)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (ya bind-mounted desde el host)
   - D. `/usr/sbin`
5. ¿Qué comando de la CLI muestra el recuento en vivo de llamadas activas?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. En Asterisk 22, la forma soportada de exponer métricas de llamadas/canales a una pila Prometheus/Grafana es:
   - A. Analizar el archivo de registro `full`
   - B. El módulo `res_prometheus.so`
   - C. Scripts AGI
   - D. No existe
7. ¿Cuál es el requisito previo tanto para HA failover como para escalado horizontal entre varios nodos Asterisk?
   - A. Ejecutarse como root
   - B. Externalizar el estado (p. ej., registros Realtime de PJSIP en una base de datos compartida)
   - C. Deshabilitar CDR
   - D. Usar redes puente
8. ¿Qué recurso limita más directamente cuántas llamadas simultáneas puede manejar un servidor Asterisk?
   - A. El número de usuarios registrados
   - B. Procesamiento de medios, especialmente transcodificación
   - C. El tamaño de `/etc/asterisk`
   - D. El backend de CDR
9. En una VM en la nube, ¿qué configuraciones de transporte `pjsip.conf` hacen que Asterisk anuncie su dirección pública para que el audio remoto funcione? (marque todas las que correspondan)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Para una implementación en la nube orientada a Internet, la regla central del capítulo de Seguridad es:
    - A. Siempre usar dos NICs
    - B. Nunca exponer Asterisk sin protección a Internet; colocar un SBC (o proxy endurecido + Fail2Ban) en el perímetro
    - C. Usar solo UDP
    - D. Desactivar TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
