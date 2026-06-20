# Designing a VoIP network

Voice over IP is quickly growing in the telephony market. The convergence paradigm is changing the way in which we communicate, reducing costs and enhancing the way in which we trade information. Voice is just the beginning of a full multimedia communication era, including voice, video, and presence. In the future, we are not going to transport people to work, but work to people because it is cleaner, faster, and cheaper. VoIP is just part of this revolution. Our challenge in this chapter is to design a VoIP network. To do this, we will have to understand concepts such as session protocols and codecs as well as how to dimension the number of circuits and bandwidth.

## Objetivos

- Entender los beneficios de VoIP
- Describir cómo Asterisk maneja VoIP
- Describir los conceptos de los canales SIP e IAX
- Elegir el protocolo más adecuado para un canal de datos específico
- Elegir el códec más adecuado para un canal de datos específico
- Dimensionar el número requerido de canales
- Calcular el ancho de banda requerido

## Beneficios del VoIP

¿Por qué debería importarle el VoIP? El VoIP brinda beneficios tanto a empresas como a individuos. La reducción de costos es ciertamente uno de ellos, pero en algunos entornos el VoIP simplifica la integración de sistemas informáticos. Varios de los beneficios se detallan a continuación:

### Convergencia

El beneficio principal del VoIP es la combinación de redes de datos y voz para reducir costos (convergencia). Sin embargo, analizar solo el costo por minuto de voz puede no ser suficiente para justificar la adopción del VoIP. El precio de los minutos que venden las compañías telefónicas está disminuyendo rápidamente y es algo a considerar antes de adoptar el VoIP.

### Costos de infraestructura

El uso de una única infraestructura de red reduce los costos asociados con adiciones, eliminaciones y cambios. A medida que IP se ha vuelto omnipresente, ha llevado la tecnología relacionada con VoIP a varios dispositivos nuevos, como teléfonos móviles, PDA, sistemas embebidos y laptops.

### Estándares abiertos

Finalmente, los estándares abiertos sobre los que se construye el VoIP proporcionan la libertad de elegir entre diferentes proveedores. Este único beneficio convierte al cliente en rey en lugar de ser un subordinado de TELCOS y fabricantes de PBX.

### Integración de Telefonía y Computadora

La telefonía es mucho más antigua que la computación. Las PBX de telefonía se basan en conmutación de circuitos, y usualmente no tiene más que una computadora para supervisión. Con VoIP, la telefonía se crea desde cero basada en estándares informáticos. Esto hace que el uso de aplicaciones de Computer Telephony sea más barato y más fácil que en el modelo antiguo. Puede crear rápidamente una larga lista de aplicaciones de telefonía basadas en Asterisk. Puede desarrollar IVR, ACD, CTI, marcadores, ventanas emergentes y otras aplicaciones en una fracción del tiempo requerido para PBX tradicionales.

## Arquitectura VoIP de Asterisk

La arquitectura de Asterisk se muestra a continuación. Asterisk trata todos los protocolos VoIP como canales. Puedes usar cualquier códec o cualquier protocolo. El concepto que se debe aprender aquí es que Asterisk interconecta cualquier tipo de canal con cualquier otro. Así, puedes traducir protocolos de señalización como SIP e IAX entre sí e incluso con diferentes códecs. Por ejemplo, puedes traducir una llamada desde un teléfono SIP en la red de área local usando el códec G.711 a un trunk SIP de tu proveedor VoIP usando el códec G.729. En los próximos capítulos, explicaremos los detalles de la arquitectura SIP e IAX. El soporte H.323 (a través del complemento chan_ooh323) está disponible pero es cada vez más raro; SIP/PJSIP es el estándar para implementaciones modernas.

![Arquitectura modular de Asterisk: aplicaciones y canales se conectan al núcleo del conmutador PBX a través de APIs, con traducción de códecs y módulos de formatos de archivo cargados dinámicamente.](../images/06-voip-network-fig01.png)

## Protocolos VoIP y la pila de red

VoIP utiliza un conjunto de diferentes protocolos que trabajan juntos. Es tentador alinearlos con el modelo de referencia OSI de siete capas, y muchos diagramas antiguos hacen exactamente eso — colocando SIP y H.323 en la capa de "sesión" y los códecs en la capa de "presentación". Esa asignación siempre ha sido controvertida. El IETF, que estandariza SIP, no usa el modelo OSI; sigue el modelo TCP/IP de cuatro capas (DoD) más antiguo, y el RFC 3261 define **SIP como un protocolo de capa de aplicación**. Los medios siguen el mismo patrón: RTP y los códecs viven en la carga útil de aplicación, transportados sobre UDP en la capa de transporte. La tabla a continuación asigna los principales protocolos VoIP al modelo TCP/IP que realmente usa el IETF, con el equivalente aproximado de OSI mostrado solo como referencia.

| Capa TCP/IP (IETF) | Protocolos | Equivalente aproximado OSI |
|---|---|---|
| Aplicación | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Aplicación / Presentación / Sesión |
| Transporte | UDP, TCP | Transporte |
| Internet | IP (con QoS como DiffServ) | Red |
| Enlace | Ethernet, PPP, Frame Relay… | Enlace de datos / Física |

Los mecanismos de QoS como DiffServ operan en la capa IP para priorizar los paquetes de voz y mejorar la calidad de la llamada. Algunas especificaciones de protocolos:

- **SIP** usa UDP o TCP en el puerto 5060 (TLS en 5061) para transportar la señalización. El audio se transporta por separado mediante RTP sobre un rango configurable de puertos UDP (la muestra `rtp.conf` incluida con Asterisk usa de 10000 a 20000), codificado con un códec como G.711.
- **H.323** transporta la señalización de la llamada sobre TCP (señalización de llamada H.225 en el puerto 1720), mientras que el canal H.225 RAS usa UDP en el puerto 1719; RTP transporta el audio.
- **IAX2** es inusual: multiplexa tanto la señalización como los medios sobre un solo puerto UDP (4569), lo que simplifica la traversía de NAT y firewalls.


## Cómo elegir un protocolo

Dado la gran cantidad de protocolos, ¿cómo puedes elegir el mejor para tu red? En esta sección resaltaremos las ventajas y desventajas de cada protocolo.

### SIP - Session Initiated Protocol

SIP es un estándar abierto de la Internet Engineering Task Force (IETF), definido mayormente en el RFC 3261. La mayoría de los proveedores modernos de VoIP usan SIP; de hecho, se está convirtiendo en el estándar de VoIP más popular. La fortaleza de SIP es que es un estándar basado en IETF. SIP es ligero en comparación con el más antiguo H.323. La principal debilidad de SIP es la traversa de NAT, un desafío para la mayoría de los proveedores de VoIP SIP. IETF no creó SIP pensando en la facturación, sino en comunicaciones abiertas entre pares. La facturación suele ser una preocupación para los proveedores de VoIP.

### IAX – Inter Asterisk eXchange

IAX es un protocolo abierto desarrollado originalmente por Digium (ahora Sangoma). IAX es un protocolo todo‑en‑uno ya que transporta señalización y medios a través del mismo puerto UDP (4569). Mark Spencer desarrolló IAX como un protocolo binario para reducir el ancho de banda. La principal fortaleza de IAX es su uso reducido de ancho de banda (no utiliza RTP); también es muy fácil para la traversa de NAT y firewalls puesto que usa solo un puerto UDP (4569).

Si un fabricante tradicional de PBX hubiera creado IAX, probablemente habría comercializado el protocolo como “lo mejor desde el helado”; en algunas situaciones, IAX en modo trunk puede reducir el uso de ancho de banda de voz en un tercio. IAX2 (versión 2) todavía se incluye en Asterisk 22 a través del módulo `chan_iax2` y sigue siendo útil para trunks Asterisk‑to‑Asterisk, aunque se considera legado; SIP/PJSIP es preferido para nuevas implementaciones. IAX2 está especificado en [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational).

### MGCP – Media Gateway Control Protocol

MGCP es un protocolo usado en conjunto con H.323, SIP e IAX. Su mayor ventaja es la escalabilidad. Se configura en el agente de llamadas en lugar de en los gateways. Esto simplifica el proceso de configuración y permite una gestión centralizada. Sin embargo, la implementación en Asterisk no está completa, y parece que no muchas personas lo usan.

### H.323

H.323 se sigue usando mucho en VoIP. Es uno de los primeros protocolos de VoIP y es esencial para conectar infraestructuras de VoIP más antiguas basadas en gateways. H.323 sigue siendo el estándar en el mercado de gateways, aunque el mercado está migrando lentamente a SIP. Las fortalezas de H.323 incluyen la gran adopción en el mercado y su madurez. Las debilidades de H.323 están relacionadas con la complejidad de implementación y los costos asociados a los organismos de estandarización.

### Tabla comparativa de protocolos

La siguiente tabla resume las diferencias entre los protocolos de sesión.

| Protocolo | Organismo estándar | Módulo / estado en Asterisk 22 | Uso |
|----------|-------------------|-------------------------------|-----|
| SIP | Estándar IETF | `chan_pjsip` (core; el único controlador SIP — `chan_sip` fue eliminado en Asterisk 21) | Teléfonos SIP; conexión a proveedores de servicios SIP |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; todavía incluido, considerado legado) | Trunks Asterisk‑to‑Asterisk; teléfonos IAX2; proveedores de servicios IAX |
| H.323 | Estándar ITU | `chan_ooh323` (complemento externo de la comunidad, no está en la compilación base) | Teléfonos y gateways H.323 (puede usar un gatekeeper externo, no puede ser uno) |
| MGCP | IETF/ITU | `chan_mgcp` eliminado en Asterisk 21 — ya no disponible | (teléfonos MGCP legacy) |
| SCCP (Skinny) | Propietario Cisco | `chan_skinny` eliminado en Asterisk 21 — ya no disponible | (teléfonos Cisco legacy) |

## Un endpoint por dispositivo

En Asterisk 22 la pila PJSIP modela cada teléfono, troncal o pasarela como un único objeto **endpoint** en `pjsip.conf`. Un endpoint tanto coloca como recibe llamadas; sus credenciales viven en un objeto `auth`, su dirección registrada en un `aor`, y su ruta de red en un `transport`. Configura un endpoint por dispositivo y adjunta las piezas que necesita — no hay un rol separado de "usuario" versus "par" que considerar. (El modelo completo de objetos se cubre en *SIP & PJSIP in depth*.)

## Codecs and codec translation

Usarás un codec para convertir la voz de una onda analógica a una señal digital. Los codecs difieren entre sí en aspectos como la calidad de sonido, la tasa de compresión, el ancho de banda y los requisitos de cómputo. Los servicios, teléfonos y pasarelas suelen soportar varios de estos aspectos. El codec G.729 es muy popular. No forma parte de la compilación estándar de Asterisk 22; en su lugar se entrega como un módulo externo adicional (`codec_g729`) que descargas de Digium (ahora Sangoma). La fuente `menuselect` de Asterisk lo lista con `support_level=external` y señala claramente: "Download the g729a codec from Digium. A license must be purchased for this codec." En otras palabras, el uso legal de G.729 requiere una licencia por canal adquirida. (Existe también una alternativa de código abierto, `bcg729`.)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 soporta los siguientes codecs (entre otros):

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — calidad estándar de PSTN; ulaw común en Norteamérica, alaw común en Europa y América Latina
- ITU G.722: 64 Kbps — wideband (voz HD), buena calidad con el mismo ancho de banda que G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — módulo binario externo `codec_g729` descargado de Digium/Sangoma (`support_level=external`; se debe comprar una licencia para usarlo)
- Speex: 2.15 a 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variable — codec moderno wideband/fullband; excelente calidad y resiliencia a pérdida de paquetes; provisto como un módulo binario externo `codec_opus` descargado de Digium/Sangoma (`support_level=external`; no se menciona compra de licencia, a diferencia de G.729); recomendado para WebRTC y endpoints SIP modernos. (Existen alternativas de compilación de código abierto en GitHub.)

Además, Asterisk permite la traducción entre codecs. En algunos casos, esto no es posible, como en el caso de g723, que solo se soporta en modo pass‑thru. Traducir de un codec a otro consume muchos recursos de la CPU. Por lo tanto, evita esto siempre que sea posible.

## How to choose a Codec

Codec selection depends on several options, such as:

- Calidad de sonido
- Costos de licenciamiento
- Consumo de procesamiento de CPU
- Requerimientos de ancho de banda
- Ocultación de pérdida de paquetes
- Disponibilidad para Asterisk y dispositivos telefónicos

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## Overhead causado por los encabezados de protocolo

A pesar de que los codecs hacen poco uso del ancho de banda, debemos considerar el overhead causado por los encabezados de protocolo como Ethernet, IP, UDP y RTP. Como tal, el ancho de banda realmente consumido depende de los encabezados utilizados. En una red Ethernet el requerimiento es mayor que en una red PPP, porque el encabezado PPP es más corto que el de Ethernet. Un solo paquete de voz G.729, por ejemplo, lleva solo 20 bytes de carga útil pero está envuelto en aproximadamente 58 bytes de encabezados Ethernet, IP, UDP y RTP — por lo que los encabezados, no el codec, dominan el ancho de banda (ver la figura abajo).

![Un solo paquete de voz g.729 en Ethernet: 20 bytes de carga útil envueltos en 58 bytes de encabezados Ethernet, IP, UDP y RTP — una conversación g.729 consume 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

Puedes calcular fácilmente otros requerimientos de ancho de banda usando una calculadora de ancho de banda VoIP en línea como <https://www.voip.school/bandcalc/bandcalc.php>.


## Ingeniería de Tráfico

Un problema principal en el diseño de redes VoIP es dimensionar la cantidad de líneas y el ancho de banda requerido hacia un destino específico, como una oficina remota o un proveedor de servicios. También es importante dimensionar la cantidad de llamadas simultáneas de Asterisk (parámetro principal para el dimensionamiento de Asterisk).

### Simplificaciones

La simplificación primaria y más utilizada es estimar la cantidad de llamadas por tipo de usuario. Por ejemplo:

- PBX empresariales (una llamada simultánea por cada cinco extensiones)
- Usuarios residenciales (una llamada simultánea por cada dieciséis usuarios)

Ejemplo #1 La sede central de la empresa tiene 120 extensiones y dos sucursales—la primera con 30 extensiones y la segunda con 15 extensiones. Nuestro objetivo es dimensionar la cantidad de trunks E1 en la sede central y el ancho de banda requerido para la red Frame‑Relay.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Número de líneas T1

- Total de extensiones que usan líneas T1: 120+30+15=165 líneas
- Usando un trunk por cada cinco extensiones para uso empresarial
- Total de líneas = 33 o aproximadamente 2xT1 líneas

1b Requisitos de ancho de banda Elegimos el códec g.729 por los requisitos de ancho de banda, la calidad de sonido y el consumo medio de CPU.

Con un trunk por cada cinco extensiones:

- Ancho de banda requerido para la sucursal #1 (Frame‑relay): 26.8*6=160.8 Kbps
- Ancho de banda requerido para la sucursal #2 (Frame‑relay): 26.8*3= 80.4 Kbps

### Método Erlang B

Cuando se dispone de datos históricos, se puede dimensionar el trunk de forma más científica en lugar de simplificar. Utilizaremos el trabajo de Agner Karup Erlang (Copenhagen Telephone Company, 1909), quien desarrolló una fórmula para calcular la cantidad de líneas en un grupo de trunks entre dos ciudades.

Un **Erlang** es una unidad de medida de tráfico común en telecomunicaciones; describe el volumen de tráfico durante una hora. Por ejemplo, supongamos que se realizan 20 llamadas en una hora, con un promedio de 5 minutos de conversación cada una:

- Minutos de tráfico en la hora: 20 × 5 = 100 minutos
- Horas de tráfico dentro de una hora: 100 / 60 = **1.66 Erlangs**

Puede leer estas medidas de un registrador de llamadas y usarlas para diseñar su red y calcular la cantidad de líneas requeridas. Una vez conocida la cantidad de líneas, puede calcular los requisitos de ancho de banda.

**Erlang B** es el método más usado para calcular la cantidad de líneas en un grupo de trunks. Asume que las llamadas llegan aleatoriamente (distribución de Poisson) y que las llamadas bloqueadas se liberan inmediatamente. Requiere que conozca el **Busy Hour Traffic (BHT)**, que puede obtener de un registrador de llamadas o estimar como simplificación: BHT = 17 % de los minutos de llamada de un día.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

Otra variable importante es el Grade of Service (GoS), que define la probabilidad de bloquear llamadas por falta de líneas. Puede arbitrar este parámetro, que usualmente es 0.05 (5 % de llamadas perdidas) o 0.01 (1 % de llamadas perdidas). Ejemplo #1: Usando el mismo ejemplo de sede central y dos sucursales introducido antes en esta sección, le daremos algunos datos sobre los patrones de tráfico. Del registrador de llamadas, descubrimos estos datos: Datos del registrador de llamadas (Minutos de llamada y BHT):

- Sede central a Sucursal #1 = 2,000 minutos, BHT = 300 minutos
- Sede central a Sucursal #2 = 1,000 minutos, BHT = 170 minutos
- Sucursal #1 a Sucursal #2 = 0, BHT=0

Arbitramos Go

## Reducción del ancho de banda requerido para VoIP

Se pueden usar tres métodos para reducir el ancho de banda requerido para las llamadas VoIP:

- Compresión de encabezado RTP
- Troncado IAX
- Carga útil de VoIP

### Compresión de encabezado RTP

En redes Frame-Relay y PPP, puede usar compresión de encabezado RTP. La compresión de encabezado RTP fue definida en RFC 2508. Es un estándar IETF disponible en varios routers. Sin embargo, tenga cuidado, ya que algunos routers requieren un conjunto de funciones diferente para que este recurso esté disponible. El impacto de usar compresión de encabezado RTP es fabuloso, pues reduce el ancho de banda requerido en nuestro ejemplo de 26.8 Kbps por conversación de voz a 11.2 Kbps—una reducción del 58.2 %!

### Modo de tronco IAX2

Si está conectando dos servidores Asterisk, puede usar el protocolo IAX2 en modo tronco. Esta tecnología revolucionaria no necesita routers especiales y puede aplicarse a cualquier tipo de enlace de datos.

![Modo de tronco IAX2 en Ethernet: una sola llamada g.729 necesita su pila completa de encabezados (31.2 Kbps), pero una segunda llamada comparte esos encabezados y agrega solo un pequeño miniframe IAX2, promediando alrededor de 9.6 Kbps de ancho de banda extra por llamada adicional.](../images/06-voip-network-fig08.png)

El modo de tronco IAX2 reutiliza los mismos encabezados de la segunda llamada en adelante. Usando g729 en un enlace PPP, la primera llamada consumirá 30 Kbps de ancho de banda, mientras que la segunda llamada usará el mismo encabezado que la primera y reducirá el ancho de banda necesario para la llamada adicional a 9.6 Kbps. Podemos calcular el ancho de banda requerido en modo tronco de la siguiente forma: Rama #1 (11 llamadas) Ancho de banda = 31.2 + (11‑1)* 9.6 Kbps = 127.2 Kbps Rama #2 (8 llamadas) Ancho de banda = 31.2 + (8‑1)* 9.6 Kbps = 98.4 Kbps La primera llamada usa 31.2 Kbps, la siguiente 9.6, y así sucesivamente.

### Aumento de la carga útil de voz

Este método es muy común al usar pasarelas VoIP a través de Internet. Al usar una carga útil mayor, sacrificará latencia a favor de un ancho de banda reducido. Puede cambiar la paquetización RTP añadiendo el tamaño de cuadro al códec en la instrucción allow.

![Aumento de la carga útil de voz: empaquetar 60 bytes de carga g.729 en un solo paquete (en lugar de 20) amortiza los 58 bytes de encabezados en más voz, reduciendo el ancho de banda a aproximadamente 16.05 Kbps por llamada a costa de latencia añadida.](../images/06-voip-network-fig09.png)

Ejemplo:

```
allow=ulaw:30
```

El número después de los dos puntos es el intervalo de paquetización en milisegundos — cuánta voz se transporta en cada paquete RTP. Un valor mayor amortiza la sobrecarga fija del encabezado en más audio (menos ancho de banda) a costa de latencia añadida. Cada códec tiene su propio tamaño de cuadro mínimo, máximo y por defecto; G.711 (`ulaw`/`alaw`), por ejemplo, usa por defecto 20 ms.

## Resumen

En este capítulo, has aprendido que Asterisk trata la VoIP mediante canales. Soporta SIP (a través de `chan_pjsip` en Asterisk 22) e IAX2; H.323 está disponible solo mediante el complemento comunitario `ooh323`, y los canales más antiguos MGCP y SCCP (Skinny) ya no forman parte de una compilación estándar de Asterisk 22. Comparaste y aprendiste cómo elegir un protocolo de señalización y un códec para los canales de VoIP. IAX2 es más eficiente en ancho de banda y puede atravesar NAT fácilmente. SIP/PJSIP es el protocolo más soportado por proveedores de teléfonos y pasarelas de terceros y es el único controlador de canal SIP en Asterisk 22. El protocolo H.323 es el más antiguo y debe usarse para conectar a infraestructuras de VoIP heredadas. En la sección de Ingeniería de Tráfico, aprendimos cómo diseñar y dimensionar una red VoIP.

## Quiz

1. Which of the following are benefits of VoIP described in this chapter (check all that apply)?
   - A. Convergence of data and voice networks to reduce cost
   - B. Lower infrastructure cost for additions, removals, and changes
   - C. Open standards that free you from a single vendor
   - D. Easier and cheaper Computer Telephony Integration
   - E. Guaranteed lower per-minute calling rates than any phone company
2. Convergence is the integration of voice, data, and video in a single network; its primary benefit is cost reduction in the implementation and maintenance of separate networks.
   - A. False
   - B. True
3. Asterisk treats every VoIP protocol as a channel and can bridge any channel type to any other, transcoding between codecs when needed.
   - A. False
   - B. True
4. In Asterisk 22, SIP is handled by which channel driver?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In the TCP/IP (IETF) model that SIP is actually defined against in RFC 3261, the signaling protocols SIP, H.323, and IAX2 operate at the ___ layer.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP is the most adopted protocol for IP phones and is an open standard largely defined by the IETF in RFC 3261.
   - A. False
   - B. True
7. IAX2 transports both signaling and media over a single UDP port, which makes it efficient and easy to traverse NAT. Which UDP port does IAX2 use?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX was originally developed by Digium (now Sangoma). Despite limited adoption by phone vendors, IAX is excellent when you need (check all that apply):
   - A. To reduce bandwidth usage (it does not use RTP)
   - B. A video media format
   - C. Easy NAT and firewall traversal
   - D. Trunk mode to combine many Asterisk-to-Asterisk calls and amortize header overhead
9. In Asterisk 22, a device is configured as a single PJSIP `endpoint` object that both places and receives calls — there is no separate "user" or "peer" role.
   - A. False
   - B. True
10. Regarding codecs in Asterisk 22, check all the true statements:
    - A. G.711 is equivalent to PCM and uses 64 Kbps of bandwidth.
    - B. Sangoma's codec_g729 module is free to download, but lawful use requires a purchased per-channel license.
    - C. GSM is popular because it uses about 13 Kbps and needs no license.
    - D. G.711 u-law is common in North America, while a-law is common in Europe and Latin America.
    - E. G.729 is light and uses very few CPU resources to encode and decode compared with G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
