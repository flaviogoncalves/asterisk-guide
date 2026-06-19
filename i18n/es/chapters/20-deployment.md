# Despliegue, monitoreo y escalado

Lograr que Asterisk responda una llamada en un laboratorio es una cosa; ejecutarlo como un servicio que sobrevive a fallos, reinicios, actualizaciones y atacantes —y que puedes observar, respaldar y hacer crecer— es otra. Este capítulo trata sobre todo lo que sucede *después* de que el dialplan funciona. Comenzamos con el supervisor que mantiene a Asterisk vivo (systemd), pasamos a empaquetarlo en un contenedor (usando el propio laboratorio Docker del libro como ejemplo práctico), luego cubrimos la gestión de configuración y respaldos, monitoreo y observabilidad, y finalmente los patrones a los que recurres cuando un servidor no es suficiente: alta disponibilidad y escalado, y las realidades del alojamiento en la nube.

Todo lo mostrado está verificado contra el laboratorio de Asterisk 22 del libro en `lab/` — el mismo contenedor sobre el que has estado construyendo a lo largo del libro.

## Objetivos

Al final de este capítulo, deberías ser capaz de:

- Ejecutar Asterisk 22 de forma fiable bajo systemd, como usuario no root, con reinicio automático
- Contenerizar Asterisk con Docker y entender las compensaciones de red
- Mantener `/etc/asterisk` en control de versiones y respaldar el estado correcto
- Monitorear un sistema en ejecución a través de la CLI, CDR/CEL, AMI/ARI y métricas
- Aplicar patrones de alta disponibilidad activo/pasivo y escalado horizontal
- Alojar Asterisk en la nube de forma segura detrás de NAT y un firewall

## Ejecutar Asterisk bajo systemd

En cada distribución de Linux actual — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — el gestor de servicios es **systemd**. El capítulo de instalación mostró que el paso `make config` (ejecutado durante `make install`) instala un script de inicio de la distribución (`/etc/init.d/asterisk` en Debian, un script `rc.d` en RedHat), que systemd envuelve automáticamente como un servicio; Asterisk también incluye una unidad nativa de systemd bajo `contrib/systemd/asterisk.service` que puedes instalar en su lugar para un control más preciso.
De cualquier manera, systemd es la forma soportada y de producción para ejecutar Asterisk. Consulta *Instalando Asterisk 22* para la compilación en sí; aquí nos enfocamos en lo que el servicio te ofrece y cómo operarlo.

### La unidad de servicio y su ciclo de vida

Una vez que `make config` ha instalado el servicio, el ciclo de vida es el ordinario de systemd:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Algunas notas operativas:

- **`restart` vs. una recarga elegante.** `systemctl restart` destruye el proceso y termina todas las llamadas. Para cambios de configuración casi nunca querrás eso — usa la CLI de Asterisk en su lugar: `asterisk -rx 'core reload'` (o una recarga específica de módulo como `pjsip reload`). Reserva `systemctl restart` para actualizaciones o un proceso bloqueado.
- **Conectarse al demonio en ejecución.** Con Asterisk ejecutándose como un servicio, abre su consola con `asterisk -r` (o `asterisk -rvvv` para salida detallada). Esto se conecta al demonio que ya está en ejecución a través de su socket de control; no inicia una segunda copia.

### `Restart=` reemplaza a safe_asterisk

Históricamente, Asterisk se lanzaba a través del envoltorio **safe_asterisk**, un script de shell que reiniciaba Asterisk si fallaba. Bajo systemd, ese trabajo pertenece a la directiva `Restart=` de la unidad — systemd nota la salida del proceso y lo recupera, con un retroceso controlado por `RestartSec=` y protección contra bucles de fallo por `StartLimitIntervalSec=`/`StartLimitBurst=`. Así que en un host con systemd, **safe_asterisk queda superado** y generalmente es innecesario. Si tu unidad instalada no lo establece ya, una anulación (drop-in) es la forma limpia de añadir el reinicio tras fallo sin editar el archivo empaquetado:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Aplícalo con `systemctl daemon-reload && systemctl restart asterisk`. Usar un drop-in (en lugar de editar la unidad instalada) significa que una futura `make config` no sobrescribirá tu cambio.

### Ejecutar como usuario no root

Asterisk no debería ejecutarse como root en producción — un error de código remoto en un proceso ejecutándose como root es un compromiso total del host, mientras que el mismo error en un proceso sin privilegios está contenido. Hay dos lugares complementarios donde esto se aplica:

- **La unidad / asterisk.conf.** La unidad empaquetada normalmente ejecuta Asterisk como el usuario y grupo `asterisk`. También puedes (o en su lugar) establecer `runuser` y `rungroup` en la sección `[options]` de `asterisk.conf`, que el demonio respeta cuando abandona los privilegios después de realizar el binding:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Propiedad de archivos.** Los directorios de tiempo de ejecución deben ser escribibles por ese usuario. Después de crear la cuenta, asegúrate de la propiedad:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Debido a que SIP (5060) y RTP (10000+) son puertos altos, Asterisk **no** necesita root para hacer el binding — solo los puertos privilegiados estilo puerto 25 lo necesitarían, los cuales Asterisk no usa. Ejecutar sin privilegios es, por tanto, gratuito. (El capítulo de Seguridad expande por qué esto importa; ver *Seguridad de Asterisk*.)

## Contenerizar Asterisk

Un contenedor empaqueta Asterisk y sus dependencias exactas en una imagen inmutable, por lo que lo que pruebas es byte por byte lo que envías. La compensación es el medio en tiempo real: un servidor SIP es sensible a la latencia y necesita un rango amplio y predecible de puertos UDP alcanzables desde el exterior, y la red de contenedores puede interferir. El resto de esta sección recorre el propio laboratorio del libro — `lab/Dockerfile` y `lab/docker-compose.yml` — como un ejemplo concreto y funcional, y luego explica la trampa en la que todos caen: RTP y redes puente (bridged).

### La imagen: compilando Asterisk desde el código fuente

El `Dockerfile` del laboratorio compila Asterisk 22 desde el código fuente en Debian 12. Vale la pena leer su estructura incluso si nunca escribes una tú mismo:

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

- **La versión está fijada** (`ARG ASTERISK_VERSION=22.10.0`). La reproducibilidad es el objetivo principal de la contenerización — cámbiala deliberadamente, recompila, vuelve a probar.
- **`--with-pjproject-bundled` y `--with-jansson-bundled`** compilan la pila SIP con una versión que coincide con Asterisk, por lo que dependes de menos paquetes apt y nunca peleas con un PJSIP de la distribución que no está sincronizado.
- **`CMD ["asterisk", "-f", "-vvv"]`** ejecuta Asterisk en *primer plano* (`-f`, "no hacer fork"). Esta es la diferencia clave con un host systemd: el proceso principal de un contenedor no debe convertirse en demonio, o el contenedor saldría inmediatamente. Así que en un contenedor **no** usas la unidad de systemd en absoluto — el tiempo de ejecución del contenedor (Docker, más la política `restart:`) se convierte en el supervisor que la `Restart=` de la unidad era en una VM.

### Montaje de enlace (bind-mount) de `/etc/asterisk`

La imagen deliberadamente no contiene **ninguna** configuración. En su lugar, `docker-compose.yml` monta mediante enlace el directorio de configuración del host:

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

`./asterisk/etc:/etc/asterisk:ro` mapea el directorio `lab/asterisk/etc` bajo control de versiones en el `/etc/asterisk` del contenedor, como solo lectura (`:ro`). La recompensa es grande: la imagen permanece inmutable y reutilizable, mientras que la configuración vive en el host donde puede ser editada y, crucialmente, mantenida en git (siguiente sección). Para aplicar un cambio de configuración, editas el archivo y recargas — `docker compose exec asterisk asterisk -rx 'core reload'` — sin necesidad de recompilar. `restart: unless-stopped` es el equivalente a nivel de compose de la `Restart=` de systemd: Docker reinicia el contenedor si Asterisk sale, pero no si lo detuviste deliberadamente.

### Redes de host vs. puente — el problema del RTP

Este es el fallo más común en Asterisk contenerizado, por lo que vale la pena entenderlo con precisión. Por defecto, Docker coloca un contenedor en una red **puente** y publicas puertos individuales con `ports:`. La señalización está bien — 5060 es un puerto. El problema es el medio: RTP usa un *rango* de puertos UDP (el `rtp.conf` del laboratorio establece `rtpstart=10000` / `rtpend=10100`), y **cada** puerto que pueda transportar audio debe ser publicado.

El laboratorio hace exactamente eso:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Nota que el rango de publicación de RTP (`10000-10100`) coincide exactamente con `rtp.conf`. Si te equivocas en esto —publicas muy pocos puertos, o un rango diferente al de `rtp.conf`— las llamadas se conectan pero tienen **audio unidireccional o nulo**, porque los paquetes RTP aterrizan en un puerto que Docker no está reenviando. Dos precauciones adicionales con el modo puente:

- **Publicar miles de puertos es lento y pesado.** Un rango RTP de producción es típicamente 10000–20000. Que Docker cree ~10000 reenvíos de proxy en espacio de usuario es costoso al inicio y añade un salto en la ruta de medios. El laboratorio mantiene un rango deliberadamente pequeño de 100 puertos porque solo ejecuta una o dos llamadas de prueba.
- **NAT en el SDP.** Detrás del puente, Asterisk ve su IP privada de contenedor y puede anunciarla en el SDP. En un host público debes decirle a PJSIP su dirección externa con `external_media_address` / `external_signaling_address` en el transporte (y establecer `local_net`), exactamente como lo harías detrás de cualquier NAT — ver *Alojamiento en la nube* a continuación.

La alternativa es **red de host** (`network_mode: host`), que elimina el puente por completo: el contenedor comparte la pila de red del host, por lo que el 5060 y todo el rango RTP son alcanzables sin publicar puertos y sin saltos de medios adicionales. Este es el modo recomendado para un contenedor Asterisk real — evita el problema del rango RTP por completo. Su costo es el aislamiento: el contenedor puede hacer binding a cualquier puerto del host y pierdes la red por servicio de compose. (La red de host es una característica de Linux; en Docker Desktop para macOS/Windows se comporta de manera diferente, lo cual es parte de por qué este laboratorio de enseñanza usa puertos publicados explícitos.)

### Volúmenes persistentes para spool y voicemail

La capa escribible de un contenedor es **efímera** — destruye el contenedor y todo lo que escribió desaparece. Para Asterisk, eso significa que el correo de voz, las grabaciones, el spool de llamadas salientes y la base de datos local desaparecerían en cada `docker compose up --build`. La configuración sobrevive porque está montada mediante enlace desde el host; el *estado* necesita el mismo tratamiento. Dentro del contenedor, los árboles relevantes son:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(El contenedor en ejecución del laboratorio muestra exactamente estos — `/var/spool/asterisk` contiene `voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` contiene `astdb.sqlite3`.) Para preservarlos, monta volúmenes nombrados para los directorios que contienen el estado que te importa:

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

El laboratorio de enseñanza omite esto a propósito — es sin estado y reproducible por diseño, por lo que cada `up` es un lienzo en blanco — pero un contenedor de producción **debe** tenerlos, o perderás el correo de voz en el primer redepliegue.

## Gestión de configuración y respaldos

El montaje de enlace anterior sugiere el modelo correcto: trata `/etc/asterisk` como **código** y el resto como **datos**.

### Mantén `/etc/asterisk` en control de versiones

El directorio de configuración es un conjunto plano de archivos de texto sin secretos que no puedan ser parametrizados — es ideal para git. Inicializa un repositorio en `/etc/asterisk` (o, como hace el laboratorio, mantén la configuración junto al proyecto y móntala mediante enlace). Beneficios:

- Cada cambio es revisable y reversible (`git diff`, `git revert`).
- Tienes un rastro de auditoría de quién cambió qué y cuándo.
- Combinado con una imagen de contenedor, un commit de configuración conocido como bueno más una etiqueta de imagen fijada describe completamente un despliegue.

Un par de precauciones específicas para la configuración de Asterisk:

- **Secretos.** `pjsip.conf` (y `manager.conf`, `ari.conf`) contienen contraseñas. No hagas commit de secretos reales a un repositorio compartido en texto plano — parametrizalos (un archivo por entorno, o un gestor de secretos / sustitución de variables de entorno en tiempo de despliegue) y mantén solo marcadores de posición en git. Las contraseñas triviales estilo `Lab-6001-secret` del laboratorio están bien *solo* porque viven en una subred privada de Docker.
- **Parametrización por entorno.** Los valores de tiempo real que difieren entre desarrollo, staging y producción (direcciones de binding, IPs externas, credenciales de troncales, URLs de bases de datos) son exactamente las líneas que parametrizas, manteniendo el grueso de la configuración idéntico entre entornos.

### Qué respaldar

La configuración en git cubre el dialplan y los endpoints, pero una PBX en vivo acumula *estado* que no está en ningún archivo de configuración. Un respaldo completo es:

| Qué | Dónde | Por qué |
|------|-------|-----|
| Configuración | `/etc/asterisk/` | dialplan, endpoints (también en git) |
| Voicemail & grabaciones | `/var/spool/asterisk/` | datos de usuario — irreemplazables |
| Base de datos interna | `/var/lib/asterisk/astdb.sqlite3` | claves `DB()`, estado del dispositivo |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` o almacén SQL | facturación e historial |
| Bases de datos externas | tu MySQL/PostgreSQL | tiempo real, CDR, voicemail |

La **astdb** merece una nota: es el pequeño almacén de clave/valor incorporado de Asterisk (un archivo SQLite en `/var/lib/asterisk/astdb.sqlite3`) usado por las funciones de dialplan `DB()`, estados de dispositivo, configuraciones de sígueme y similares. Puedes volcarla para inspección o respaldo desde la CLI:

```
asterisk -rx 'database show'
```

Si tu CDR/CEL o voicemail o configuración de PJSIP vive en una base de datos externa (ver *Asterisk Real-Time* y *Asterisk Call Detail Records*), esa base de datos es ahora la fuente de verdad para esos datos y debe estar en tu rotación normal de respaldos de base de datos — respaldar `/etc/asterisk` por sí solo no es suficiente.

## Monitoreo y observabilidad

No puedes operar lo que no puedes ver. Asterisk expone su estado en cuatro niveles, desde un vistazo humano rápido hasta una tubería de métricas: la **CLI**, los registros **CDR/CEL**, eventos **AMI/ARI**, y **exportadores de métricas**.

### Verificaciones de salud en la CLI

La verificación más rápida de "¿está saludable?" es la CLI. Los comandos a continuación se ejecutan en vivo contra el laboratorio. Primero los canales:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` en un sistema silencioso es normal; en uno ocupado esta es tu concurrencia en tiempo real. `core show uptime` confirma que el proceso no se ha estado reiniciando bajo tu supervisión:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Para la salud SIP, `pjsip show endpoints` muestra cada endpoint y si sus contactos registrados son alcanzables. Desde el laboratorio:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` aquí simplemente significa que ningún teléfono está registrado actualmente en esos endpoints (el laboratorio no tiene clientes en vivo) — una vez que un softphone se registra y `qualify` lo confirma, el estado muestra el contacto como alcanzable. Comandos complementarios: `pjsip show contacts` (registros actuales y tiempo de ida y vuelta), `pjsip show transports`, y `pjsip show aor <name>` para un AOR. Estas son las herramientas del día a día para "¿por qué no se puede alcanzar la extensión X?".

### CDR y CEL

Cada llamada deja un **Call Detail Record** (CDR); **Channel Event Logging** (CEL) añade eventos más finos por canal. Confirma que CDR está activo y qué backend lo almacena:

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

El laboratorio muestra `(none)` bajo backends registrados porque la configuración mínima del laboratorio no carga ningún módulo de almacenamiento CDR — por lo que los registros se calculan pero no se escriben en ninguna parte. En producción cargas un backend (CSV, o `cdr_odbc`/`cdr_adaptive_odbc` en MySQL/PostgreSQL) y eso se convierte en tu fuente de facturación e historial. CEL está **deshabilitado por defecto** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` solo cuando necesitas detalle a nivel de evento. Ambos se cubren en profundidad en *Asterisk Call Detail Records*; para el monitoreo, el punto es que CDR/CEL son tu registro *histórico*, donde la CLI es tu vista *en vivo*.

### Eventos AMI y ARI

Para un monitoreo programático en tiempo real, quieres un flujo de eventos en lugar de consultar la CLI:

- **AMI (Asterisk Manager Interface)** es el protocolo de eventos/comandos TCP de larga duración (`manager.conf`). Te suscribes y recibes eventos `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` y similares a medida que ocurren las llamadas — la columna vertebral de los paneles de control y herramientas de contabilidad de llamadas. En el laboratorio, AMI está deshabilitado por defecto (`manager show settings` reporta `Manager (AMI): No`); lo habilitas y aseguras en `manager.conf`.
- **ARI (Asterisk REST Interface)** es la interfaz moderna HTTP + WebSocket (`ari.conf`, servida por el servidor HTTP incorporado). Ofrece un flujo de eventos JSON y control de llamadas de grano fino — la elección correcta para nuevas integraciones.

Ambos se detallan en *Extender Asterisk con AMI y AGI* y *The Asterisk REST Interface (ARI)*. La advertencia relevante para el despliegue: **AMI y ARI son potentes y nunca deben exponerse a internet.** Haz binding del servidor HTTP a localhost o a una red de gestión, usa secretos únicos fuertes y protege los puertos con firewall — ver *Seguridad de Asterisk*.

### Métricas: Prometheus y Grafana

Para paneles y alertas, Asterisk 22 incluye un exportador de Prometheus, **`res_prometheus.so`** (un módulo con nivel de soporte *extendido*), que expone métricas en un endpoint HTTP que un servidor Prometheus consulta. Junto a las métricas principales del proceso, incluye proveedores conectables que cubren canales, llamadas, endpoints, puentes y registros salientes de PJSIP:

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

Puedes confirmar que el módulo está presente en la compilación del laboratorio:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

Muestra `Not Running` porque el laboratorio no lo configura ni lo carga; habilitarlo (`prometheus.conf` más el servidor HTTP) convierte a Asterisk en un objetivo de Prometheus. Apunta Prometheus al endpoint de consulta y Grafana a Prometheus, y obtendrás paneles de series temporales (llamadas concurrentes, registros, tendencias de ASR/ACD) y alertas (ej. "llamadas activas cayeron a cero" o "picos de fallos de registro"). Para equipos que ya ejecutan Prometheus/Grafana, esta es la forma natural de integrar Asterisk en la observabilidad existente, en lugar de analizar la salida de la CLI.

### Códigos de respuesta SIP que vale la pena vigilar

Cualquiera que sea la tubería, algunos resultados SIP señalan problemas y vale la pena alertar sobre ellos: fallos de desafío `401`/`407` sostenidos o `403 Forbidden` sugieren una tormenta de fuerza bruta o credenciales mal configuradas (consulta Fail2Ban en *Seguridad de Asterisk*); `503 Service Unavailable` apunta a un servidor o troncal sobrecargado o congestionado; y un pico en `408 Request Timeout`/`480 Temporarily Unavailable` usualmente significa que los endpoints se han vuelto inalcanzables (timeout de NAT, fallos de calificación).

## Alta disponibilidad y escalado

Un servidor Asterisk es un punto único de fallo y tiene un techo de llamadas finito. Los dos problemas — *mantenerse arriba* y *hacerse más grande* — tienen respuestas diferentes.

### Activo/pasivo con una IP flotante

El patrón de HA clásico y bien trillado para Asterisk es **activo/pasivo** (no activo/activo — el estado de llamada en Asterisk es difícil de compartir en vivo). Dos servidores idénticos, uno activo, uno pasivo, comparten una **IP flotante (virtual)** gestionada por un gestor de clúster como **keepalived** (VRRP) o **Pacemaker/Corosync**. Los teléfonos y troncales se registran en la IP flotante, no en ninguno de los hosts reales. Si el nodo activo falla su verificación de salud, la IP flotante se mueve al pasivo, que toma el control.

La advertencia honesta: una conmutación por error de IP **termina las llamadas en curso** — Asterisk no replica el estado del canal en vivo entre nodos, por lo que cualquiera en medio de una llamada debe volver a marcar. Los registros se restablecen dentro de un ciclo de calificación/registro. Lo que la conmutación por error te compra es que el *servicio* se recupera en segundos sin intervención manual, lo cual para la mayoría de las PBX es exactamente el objetivo. Para hacer que el pasivo sea genuinamente capaz de tomar el control, ambos nodos necesitan la misma configuración (tu `/etc/asterisk` en git, desplegada idénticamente) y el mismo *estado* — que es el siguiente punto.

### Externalizar el estado con PJSIP Realtime

Activo/pasivo solo funciona si el pasivo conoce los mismos endpoints y registros que el nodo activo. La forma de lograr eso es **dejar de mantener el estado en archivos planos en una caja** y moverlo a una base de datos compartida que ambos nodos lean. **PJSIP Realtime** (Sorcery respaldado por una base de datos) hace exactamente esto: endpoints, AORs, autenticaciones — y, importantemente, **registros** (la tabla `ps_contacts`) — viven en MySQL/PostgreSQL en lugar de en `pjsip.conf` y memoria local. Ambos nodos de Asterisk apuntan a la misma base de datos, por lo que un teléfono registrado a través de un nodo es visible para el otro. Esto se cubre en *Asterisk Real-Time* (la sección de PJSIP Realtime / Sorcery); aquí el punto de despliegue es que **externalizar el estado es el prerrequisito tanto para HA como para escalado horizontal** — sin él, cada nodo es una isla.

Aplica la misma lógica al resto de tu estado: CDR/CEL en un almacén SQL compartido, voicemail en almacenamiento compartido/replicado (o `ODBC_STORAGE`), y las claves astdb de las que dependes en una base de datos. Una vez que el estado es externo, los nodos de Asterisk se vuelven más cercanos a front-ends intercambiables.

### Proxies SIP al frente (OpenSIPS)

Para escalar *más allá* de la capacidad de un servidor, pones un **proxy SIP/balanceador de carga** frente a un grupo de servidores de medios Asterisk. **OpenSIPS** es un proxy SIP de muy alto rendimiento construido específicamente para esto (manejan cientos de miles de registros y enrutan señalización sin tocar los medios). El proxy presenta una única dirección SIP al mundo, mantiene el servicio de registro/ubicación y distribuye las llamadas a través de los back-ends de Asterisk. Esta separación — una capa de proxy ligera haciendo registro y enrutamiento, una capa de Asterisk escalable horizontalmente haciendo el procesamiento de llamadas real (IVR, colas, conferencias, transcodificación) — es cómo los grandes despliegues crecen más allá de una sola caja. (La plataforma SipPulse misma usa OpenSIPS frente a sus servidores de medios/aplicación por esta misma razón.)

### Escalado de medios

El proxy distribuye la *señalización* de forma barata; **los medios son el recurso costoso**. El reenvío RTP, y especialmente la transcodificación entre códecs (ej. Opus ↔ G.711) o ejecutar grandes conferencias, está limitado por la CPU y es lo que realmente limita a un servidor. Estrategias:

- **Evita la transcodificación** siempre que sea posible — negocia un códec común de extremo a extremo para que Asterisk haga puentes de forma nativa (pass-through) en lugar de transcodificar. Esta es la mayor victoria en capacidad de medios.
- **Escala los medios horizontalmente** añadiendo nodos de Asterisk detrás del proxy; cada uno lleva una parte de las llamadas concurrentes.
- **Descarga los medios del navegador** a una puerta de enlace WebRTC dedicada (ej. Janus) para que la PBX no esté también terminando y reenviando cada flujo DTLS-SRTP del navegador — ver *WebRTC con Asterisk*, que discute exactamente esta división Asterisk-más-puerta-de-enlace.

Dimensiona la capacidad por **llamadas concurrentes y carga de transcodificación**, no por usuarios registrados — 10,000 teléfonos registrados que están mayormente inactivos son mucho más baratos que 200 conferencias transcodificadas simultáneas.

## Alojamiento en la nube

Ejecutar Asterisk en una VM en la nube (AWS, GCP, Azure, un VPS) es común y funciona bien, pero la red de la nube está **NAT'd y protegida por firewall por defecto**, lo cual pelea con SIP. Las siguientes son las preocupaciones específicas del despliegue.

### NAT y el SDP

Una VM en la nube casi siempre tiene una IP **privada** en su NIC y una IP **pública** separada que el proveedor hace NAT hacia ella. Si Asterisk anuncia la IP privada en el SDP, los teléfonos remotos envían RTP a un agujero negro — el síntoma clásico de audio unidireccional/nulo. Dile a PJSIP su identidad pública en el transporte:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` hace que Asterisk reescriba la dirección que anuncia a los pares públicos, mientras que `local_net` le dice qué pares son locales (y *no* deben ser reescritos). Este es el mismo manejo de NAT discutido para redes Docker puente arriba — una VM en la nube está, en efecto, detrás de NAT.

### Firewall y el rango RTP

Dos firewalls usualmente se aplican en una VM en la nube: el grupo de seguridad / ACL de red del **proveedor**, y el iptables del **host**. Ambos deben abrir los mismos puertos, y la política es la del capítulo de Seguridad. El conjunto de reglas rescatado de la 1ª edición (`docs/legacy-labs/configs/Lab7/rules.v4`) captura la forma — acepta SIP y el rango RTP, acepta establecido/relacionado, descarta el resto:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Dos correcciones que el capítulo de Seguridad hace y que importan aquí: abre **5061 en TCP** (no UDP) si ejecutas SIP/TLS, y recuerda que el rango UDP RTP en tu firewall debe coincidir exactamente con `rtpstart`/`rtpend` en `rtp.conf` — el mismo rango que publicas en un contenedor. No dupliques la compilación de iptables/Fail2Ban aquí; **sigue las secciones de firewall, Fail2Ban y TLS/SRTP de *Seguridad de Asterisk*** (Fail2Ban vigila el canal de registro `security` que el laboratorio ya habilita en `logger.conf`) y aplica esa política tanto en el firewall del host como en el grupo de seguridad de la nube.

### Latencia, región y el SBC

- **Elige una región cercana a tus usuarios.** La voz es sensible a la latencia — una latencia de boca a oído superior a ~150 ms es notable. Aloja la VM en la región más cercana a la mayoría de tus teléfonos y troncales; los medios transcontinentales son audiblemente peores.
- **Pon un SBC al frente para cualquier despliegue expuesto a internet.** Un **Session Border Controller** termina SIP/RTP en el borde, oculta tu topología, normaliza NAT y absorbe el tráfico de DoS y escaneo antes de que llegue a Asterisk. La recomendación central del capítulo de Seguridad — *no expongas Asterisk crudo a internet* — se aplica doblemente en la nube, donde la IP pública de tu VM está siendo escaneada a los pocos minutos de levantarse. Un SBC (o como mínimo un proxy SIP endurecido como OpenSIPS más Fail2Ban) es el borde estándar.

## Resumen

El despliegue es donde un dialplan funcional se convierte en un servicio confiable. En una VM, ejecuta Asterisk bajo **systemd** como un usuario **no root**, dejando que la `Restart=` de la unidad lo mantenga vivo (safe_asterisk queda superado) y usando `core reload` en lugar de `systemctl restart` para cambios de configuración. **Contenerizar** con Docker — como hace el laboratorio del libro — te da una imagen inmutable y fijada con configuración **montada mediante enlace** desde un `/etc/asterisk` en git; la trampa son los medios, así que usa **red de host** o publica un rango de puertos RTP que **coincida exactamente con `rtp.conf`**, y monta **volúmenes persistentes** para spool/voicemail/astdb para que el estado sobreviva a un redepliegue. Trata la configuración como código y **respalda el estado** que la configuración no captura: voicemail, grabaciones, `astdb.sqlite3`, y CDR/CEL. **Observa** el sistema en cuatro niveles — la CLI (`core show channels`, `pjsip show endpoints`) para la vista en vivo, **CDR/CEL** para el historial, **AMI/ARI** para eventos programáticos, y el exportador **`res_prometheus`** hacia Grafana para paneles y alertas — mientras mantienes AMI/ARI fuera de la internet pública. Para **mantenerte arriba**, ejecuta activo/pasivo con una **IP flotante** (aceptando que la conmutación por error termina las llamadas en vivo); para **crecer**, externaliza el estado con **PJSIP Realtime**, pon un grupo de servidores de medios frente a **OpenSIPS**, y minimiza la transcodificación porque **los medios — no los registros — son lo que limita a un servidor**. Finalmente, en la **nube**, trata la VM como si estuviera detrás de NAT (`external_media_address`, `local_net`), abre el firewall según el capítulo de Seguridad tanto en el host como en el grupo de seguridad del proveedor, elige una región de baja latencia y nunca expongas Asterisk crudo — pon un **SBC** en el borde.

## Cuestionario

1. En un host con systemd, ¿qué reemplaza el trabajo del antiguo envoltorio `safe_asterisk` de reiniciar un Asterisk bloqueado?
   - A. Un trabajo cron
   - B. La directiva `Restart=` del archivo de unidad
   - C. `systemctl enable`
   - D. La astdb
2. Para aplicar un cambio de configuración a un Asterisk en ejecución **sin terminar llamadas**, deberías:
   - A. `systemctl restart asterisk`
   - B. Reiniciar el servidor
   - C. `asterisk -rx 'core reload'`
   - D. Recompilar la imagen del contenedor
3. Un Asterisk contenerizado (red puente) conecta llamadas pero **no tiene audio**. La causa más probable es:
   - A. El dialplan está mal
   - B. El rango de puertos UDP RTP publicado no coincide con `rtpstart`/`rtpend` en `rtp.conf`
   - C. CDR está deshabilitado
   - D. La CLI es inalcanzable
4. ¿Qué directorios deben montarse como **volúmenes persistentes** para que un redepliegue de contenedor no pierda el estado? (marca todas las que apliquen)
   - A. `/var/spool/asterisk` (voicemail, grabaciones)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (ya montado mediante enlace desde el host)
   - D. `/usr/sbin`
5. ¿Qué comando de CLI da el conteo en vivo de llamadas activas?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. En Asterisk 22, la forma soportada de exponer métricas de llamada/canal a una pila Prometheus/Grafana es:
   - A. Analizar el archivo de registro `full`
   - B. El módulo `res_prometheus.so`
   - C. Scripts AGI
   - D. No existe ninguna
7. ¿Cuál es el prerrequisito tanto para la conmutación por error de HA como para el escalado horizontal a través de múltiples nodos de Asterisk?
   - A. Ejecutar como root
   - B. Externalizar el estado (ej. registros PJSIP Realtime en una base de datos compartida)
   - C. Deshabilitar CDR
   - D. Usar redes puente
8. ¿Qué recurso limita más directamente cuántas llamadas simultáneas puede manejar un servidor Asterisk?
   - A. El número de usuarios registrados
   - B. El procesamiento de medios, especialmente la transcodificación
   - C. El tamaño de `/etc/asterisk`
   - D. El backend de CDR
9. En una VM en la nube, ¿qué configuraciones de transporte `pjsip.conf` hacen que Asterisk anuncie su dirección pública para que el audio remoto funcione? (marca todas las que apliquen)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Para un despliegue en la nube expuesto a internet, la regla central del capítulo de Seguridad es:
    - A. Ejecutar siempre dos NICs
    - B. Nunca exponer Asterisk crudo a internet; poner un SBC (o proxy endurecido + Fail2Ban) en el borde
    - C. Usar solo UDP
    - D. Deshabilitar TLS

**Respuestas:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
