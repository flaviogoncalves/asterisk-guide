# Diseño de una red VoIP

Voice over IP está creciendo rápidamente en el mercado de la telefonía. El paradigma de convergencia está cambiando la forma en que nos comunicamos, reduciendo costos y mejorando la manera en que intercambiamos información. La voz es solo el comienzo de una era de comunicación multimedia completa, que incluye voz, video y presencia. En el futuro, no vamos a transportar a las personas al trabajo, sino el trabajo a las personas porque es más limpio, rápido y económico. VoIP es solo una parte de esta revolución. Nuestro desafío en este capítulo es diseñar una red VoIP. Para hacer esto, tendremos que entender conceptos como protocolos de sesión y codecs, así como también cómo dimensionar el número de circuitos y el ancho de banda.

## Objetivos

Al finalizar este capítulo, usted debería ser capaz de:

- Entender los beneficios de VoIP
- Describir cómo Asterisk maneja VoIP
- Describir los conceptos de los canales SIP e IAX
- Elegir el protocolo más adecuado para un canal de datos específico
- Elegir el codec más adecuado para un canal de datos específico
- Dimensionar el número requerido de canales
- Calcular el ancho de banda requerido

## Beneficios de VoIP

¿Por qué debería interesarle VoIP? VoIP proporciona beneficios tanto a empresas como a individuos. La reducción de costos es ciertamente uno de ellos, pero en algunos entornos VoIP simplifica la integración de sistemas informáticos. Varios de los beneficios se detallan aquí:

### Convergencia

El beneficio principal de VoIP es la combinación de redes de datos y voz para reducir costos (convergencia). Sin embargo, analizar solo los costos por minuto de voz puede no ser suficiente para justificar la adopción de VoIP. El precio de los minutos vendidos por las compañías telefónicas se está volviendo más barato rápidamente y es algo que debe considerarse antes de adoptar VoIP.

### Costos de infraestructura

El uso de una infraestructura de red única reduce los costos asociados con adiciones, eliminaciones y cambios. A medida que IP se ha vuelto omnipresente, ha llevado la tecnología relacionada con VoIP a varios dispositivos nuevos, como teléfonos celulares, PDA, sistemas embebidos y computadoras portátiles.

### Estándares abiertos

Finalmente, los estándares abiertos sobre los cuales se construye VoIP brindan la libertad de elegir entre diferentes proveedores. Este beneficio único hace que el cliente sea el rey en lugar de un subordinado de las TELCOS y los fabricantes de PBX.

### Integración de Telefonía e Informática (CTI)

La telefonía es mucho más antigua que la informática. Las PBX de telefonía se basan en conmutación de circuitos, y generalmente no se tiene más que una computadora para la supervisión. Con VoIP, la telefonía se crea desde cero basada en estándares informáticos. Esto hace que el uso de aplicaciones de Telefonía e Informática sea más barato y fácil que en el modelo antiguo. Puede crear rápidamente una larga lista de aplicaciones de telefonía basadas en Asterisk. Puede desarrollar IVRs, ACDs, CTI, marcadores, ventanas emergentes en pantalla y otras aplicaciones en una fracción del tiempo requerido para las PBX tradicionales.

## Arquitectura VoIP de Asterisk

La arquitectura de Asterisk se muestra a continuación. Asterisk trata todos los protocolos VoIP como canales. Puede usar cualquier codec o cualquier protocolo. El concepto a aprender aquí es que Asterisk puentea cualquier tipo de canal con cualquier otro. Por lo tanto, puede traducir protocolos de señalización como SIP e IAX entre sí e incluso con diferentes codecs. Por ejemplo, puede traducir una llamada desde un teléfono SIP en la red de área local usando el codec G.711 a un trunk SIP hacia su proveedor VoIP usando el codec G.729. En los próximos capítulos, explicaremos los detalles de la arquitectura SIP e IAX. El soporte para H.323 (a través del complemento chan_ooh323) está disponible pero es cada vez más raro; SIP/PJSIP es el estándar para implementaciones modernas.

![Arquitectura modular de Asterisk: las aplicaciones y los canales se conectan al núcleo del switch PBX a través de APIs, con traducción de codecs y módulos de formato de archivo cargados dinámicamente.](../images/06-voip-network-fig01.png)

## Protocolos VoIP y la pila de red

VoIP utiliza un conjunto de diferentes protocolos que trabajan juntos. Es tentador alinearlos contra el modelo de referencia OSI de siete capas, y muchos diagramas antiguos hacen exactamente eso: colocar SIP y H.323 en la capa de "sesión" y los codecs en la capa de "presentación". Ese mapeo siempre ha sido polémico. El IETF, que estandariza SIP, no utiliza el modelo OSI; sigue el modelo TCP/IP (DoD) de cuatro capas más antiguo, y RFC 3261 define **SIP como un protocolo de capa de aplicación**. Los medios siguen el mismo patrón: RTP y los codecs viven en la carga útil de la aplicación, transportados sobre UDP en la capa de transporte. La tabla a continuación mapea los principales protocolos VoIP en el modelo TCP/IP que el IETF realmente utiliza, con el equivalente OSI aproximado mostrado solo como referencia.

| Capa TCP/IP (IETF) | Protocolos | Equivalente OSI aproximado |
|---|---|---|
| Aplicación | SIP, H.323, MGCP, señalización IAX2; RTP/RTCP; codecs (G.711, G.729, Opus…) | Aplicación / Presentación / Sesión |
| Transporte | UDP, TCP | Transporte |
| Internet | IP (con QoS como DiffServ) | Red |
| Enlace | Ethernet, PPP, Frame Relay… | Enlace de datos / Físico |

Los mecanismos de QoS como DiffServ operan en la capa IP para priorizar los paquetes de voz y mejorar la calidad de la llamada. Algunos detalles específicos de los protocolos:

- **SIP** utiliza UDP o TCP en el puerto 5060 (TLS en 5061) para transportar la señalización. El audio se transporta por separado mediante RTP sobre un rango de puertos UDP configurable (la muestra `rtp.conf` que incluye Asterisk utiliza de 10000 a 20000), codificado con un codec como G.711.
- **H.323** transporta la señalización de llamadas sobre TCP (señalización de llamadas H.225 en el puerto 1720), mientras que el canal RAS H.225 utiliza UDP en el puerto 1719; RTP transporta el audio.
- **IAX2** es inusual: multiplexa tanto la señalización como los medios sobre un solo puerto UDP (4569), lo que simplifica el cruce de NAT y firewall.

> **[author]** Opcional: encargar una figura redibujada de la pila TCP/IP anterior si se desea una imagen; de lo contrario, la tabla es autosuficiente.

## Cómo elegir un protocolo

Dados los muchos protocolos, ¿cómo puede elegir el mejor para su red? En esta sección, destacaremos las ventajas y desventajas de cada protocolo.

### SIP - Session Initiated Protocol

SIP es un estándar abierto del Internet Engineering Task Force (IETF), definido en gran medida en RFC 3261. La mayoría de los proveedores de VoIP modernos utilizan SIP; de hecho, se está convirtiendo en el estándar VoIP más popular. La fortaleza de SIP es que es un estándar basado en IETF. SIP es ligero en comparación con el antiguo H.323. La principal debilidad de SIP es el cruce de NAT, un desafío para la mayoría de los proveedores de VoIP SIP. El IETF no creó SIP pensando en la facturación, sino para comunicaciones abiertas entre pares. La facturación suele ser una preocupación para los proveedores de VoIP.

### IAX – Inter Asterisk eXchange

IAX es un protocolo abierto desarrollado originalmente por Digium (ahora Sangoma). IAX es un protocolo todo en uno ya que transporta señalización y medios a través del mismo puerto UDP (4569). Mark Spencer desarrolló IAX como un protocolo binario para reducir el ancho de banda. La principal fortaleza de IAX es su reducido uso de ancho de banda (no utiliza RTP); también es muy fácil para el cruce de NAT y firewall ya que utiliza solo un puerto UDP (4569). Si un fabricante de PBX tradicional hubiera creado IAX, probablemente habría comercializado el protocolo como "lo mejor desde el helado"; en algunas situaciones, IAX en modo trunk puede reducir el uso de ancho de banda de voz en un tercio. IAX2 (versión 2) todavía se incluye en Asterisk 22 a través del módulo `chan_iax2` y sigue siendo útil para trunks de Asterisk a Asterisk, aunque se considera heredado; SIP/PJSIP es preferido para nuevas implementaciones. IAX2 se especifica en [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informativo).

### MGCP – Media Gateway Control Protocol

MGCP es un protocolo utilizado junto con H.323, SIP e IAX. Su mayor ventaja es la escalabilidad. Se configura en el agente de llamadas en lugar de en los gateways. Esto simplifica el proceso de configuración y permite una gestión centralizada. Sin embargo, la implementación en Asterisk no está completa y parece que no mucha gente lo usa.

### H.323

H.323 se utiliza ampliamente en VoIP. Es uno de los primeros protocolos VoIP y es esencial para conectar infraestructuras VoIP antiguas basadas en gateways. H.323 sigue siendo el estándar en el mercado de gateways, aunque el mercado está migrando lentamente a SIP. Las fortalezas de H.323 incluyen la gran adopción en el mercado y la madurez. Las debilidades de H.323 están relacionadas con la complejidad de la implementación y los costos asociados de los organismos de estandarización.

### Tabla de comparación de protocolos

La siguiente tabla resume las diferencias entre los protocolos de sesión.

| Protocolo | Organismo de estandarización | Módulo / estado de Asterisk 22 | Utilizado para |
|----------|---------------|-----------------------------|----------|
| SIP | Estándar IETF | `chan_pjsip` (núcleo; el único controlador SIP — `chan_sip` fue eliminado en Asterisk 21) | Teléfonos SIP; conexión a proveedores de servicios SIP |
| IAX2 | RFC 5456 (Informativo) | `chan_iax2` (núcleo; aún incluido, considerado heredado) | Trunks de Asterisk a Asterisk; teléfonos IAX2; proveedores de servicios IAX |
| H.323 | Estándar ITU | `chan_ooh323` (complemento comunitario externo, no en la compilación base) | Teléfonos y gateways H.323 (puede usar un gatekeeper externo, no puede ser uno) |
| MGCP | IETF/ITU | `chan_mgcp` eliminado en Asterisk 21 — ya no disponible | (teléfonos MGCP heredados) |
| SCCP (Skinny) | Propietario de Cisco | `chan_skinny` eliminado en Asterisk 21 — ya no disponible | (teléfonos Cisco heredados) |

## Un endpoint por dispositivo

En Asterisk 22, la pila PJSIP modela cada teléfono, trunk o gateway como un único objeto **endpoint** en `pjsip.conf`. Un endpoint realiza y recibe llamadas; sus credenciales viven en un objeto `auth`, su dirección registrada en un `aor` y su ruta de red en un `transport`. Usted configura un endpoint por dispositivo y adjunta las piezas que necesita; no hay un rol separado de "usuario" versus "peer" sobre el cual razonar. (El modelo de objeto completo se cubre en *SIP y PJSIP*.)

## Codecs y traducción de codecs

Utilizará un codec para convertir la voz de una onda analógica a una señal digital. Los codecs difieren entre sí en aspectos como la calidad del sonido, la tasa de compresión, el ancho de banda y los requisitos informáticos. Los servicios, teléfonos y gateways generalmente admiten varios de estos aspectos. El codec G.729 es muy popular. No es parte de la compilación estándar de Asterisk 22; en cambio, se envía como un módulo complementario externo (`codec_g729`) que descarga de Digium (ahora Sangoma). La fuente `menuselect` de Asterisk lo enumera con `support_level=external` y señala claramente: "Descargue el codec g729a de Digium. Se debe comprar una licencia para este codec". En otras palabras, el uso legal de G.729 requiere una licencia comprada por canal. (También existe una alternativa de código abierto, `bcg729`.)

![Modulación por Codificación de Pulsos (PCM): una señal analógica de 4000 Hz se muestrea 8000 veces por segundo (teorema de Nyquist) y se codifica en un flujo de bits digital de 64 Kbps.](../images/06-voip-network-fig04.png)

Asterisk 22 admite los siguientes codecs (entre otros):

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — calidad PSTN estándar; ulaw común en América del Norte, alaw común en Europa y América Latina
- ITU G.722: 64 Kbps — banda ancha (voz HD), buena calidad con el mismo ancho de banda que G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — módulo binario externo `codec_g729` descargado de Digium/Sangoma (`support_level=external`; se debe comprar una licencia para usarlo)
- Speex: 2.15 a 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variable — codec moderno de banda ancha/banda completa; excelente calidad y resistencia a la pérdida de paquetes; proporcionado como un módulo binario externo `codec_opus` descargado de Digium/Sangoma (`support_level=external`; no se menciona compra de licencia, a diferencia de G.729); recomendado para WebRTC y endpoints SIP modernos. (Existen alternativas de compilación de código abierto en GitHub.)

Además, Asterisk permite la traducción entre codecs. En algunos casos, esto no es posible, como en el caso de g723, que solo se admite en modo pass-thru. Traducir de un codec a otro consume muchos recursos de la CPU. Por lo tanto, evite esto por completo siempre que sea posible.

## Cómo elegir un Codec

La selección del codec depende de varias opciones, tales como:

- Calidad de sonido
- Costos de licencia
- Consumo de procesamiento de CPU
- Requisitos de ancho de banda
- Ocultamiento de pérdida de paquetes
- Disponibilidad para Asterisk y dispositivos telefónicos

La siguiente tabla compara los codecs más populares. La calidad de estos codecs se considera "toll"—en otras palabras, similar a la PSTN.

| Codec | G.711 (ulaw/alaw) | G.722 | Opus | G.729A | iLBC | GSM 06.10 |
|---|---|---|---|---|---|---|
| Banda de audio | Banda estrecha | Banda ancha (HD) | Estrecha→banda completa | Banda estrecha | Banda estrecha | Banda estrecha |
| Ancho de banda (Kbps) | 64 | 64 | 6–510 (variable) | 8 | 13.33 | 13 |
| Módulo Asterisk 22 | `codec_ulaw`/`codec_alaw` (núcleo) | `codec_g722` (núcleo) | `codec_opus` (externo) | `codec_g729` (externo) | `codec_ilbc` (núcleo) | `codec_gsm` (núcleo) |
| Costo (por canal) | Gratis | Gratis | Gratis (descarga binaria) | Requiere compra de licencia¹ | Gratis | Gratis |
| Resistencia al borrado de tramas² | Ninguna | Baja | Excelente (FEC/PLC integrado) | ~3% | ~5% | ~3% |
| Costo relativo de CPU | Muy bajo | Bajo | Moderado–alto | Alto | Alto | Bajo |

La línea base de PSTN es **G.711** — es la referencia para la calidad "toll" y se transcodifica gratis dentro de Asterisk. **G.722** ofrece voz de banda ancha (HD) a los mismos 64 Kbps y es una buena opción para LAN/interna. **Opus** es el estándar moderno para WebRTC y endpoints SIP capaces: adapta su bitrate, tiene corrección de errores hacia adelante integrada y resiste bien la pérdida de paquetes; se envía como el binario externo `codec_opus` (gratis para descargar). **G.729** sigue siendo útil en trunks WAN de bajo ancho de banda, pero el uso legal requiere el `codec_g729` con licencia de Sangoma (gratis para descargar, licencia por canal para usar) o la implementación de código abierto **bcg729** como alternativa.

¹ El binario `codec_g729` de Sangoma es gratuito para descargar pero requiere una licencia comprada por canal para usarlo legalmente. El `bcg729` de código abierto es una alternativa sin licencia.

² La resistencia al borrado de tramas se refiere a qué tan bien se mantiene la calidad percibida (MOS) bajo pérdida de paquetes. El punto de cruce exacto varía con la paquetización y las condiciones de la red; use esta columna para comparación relativa, no como una cifra precisa.

**Recomendaciones de codecs para Asterisk 22:**

- **G.711 (ulaw/alaw):** Úselo para trunks PSTN y máxima interoperabilidad; costo de transcodificación cero dentro de Asterisk.
- **G.729:** Útil para trunks WAN de bajo ancho de banda; el módulo `codec_g729` de Sangoma es gratuito para descargar pero requiere una licencia comprada por canal para usarlo.
- **G.722:** Buena opción para voz de banda ancha (HD) en extensiones LAN/internas; mismo ancho de banda que G.711 con mejor calidad.
- **Opus:** Recomendado para endpoints modernos, clientes WebRTC y cualquier implementación donde el endpoint lo admita. Bitrate adaptativo, excelente resistencia a la pérdida de paquetes, disponible gratuitamente a través del módulo binario `codec_opus` de Sangoma.

## Sobrecarga causada por encabezados de protocolo

A pesar de que los codecs hacen poco uso del ancho de banda, tenemos que considerar la sobrecarga causada por los encabezados de protocolo como Ethernet, IP, UDP y RTP. Como tal, podríamos decir que el ancho de banda depende de los encabezados utilizados. Si estamos en una red Ethernet, el requisito de ancho de banda es mayor que en una red PPP porque el encabezado PPP es más corto que el de Ethernet. Veamos algunos ejemplos: Destino Ethernet G.729 codificado (20) Encabezado UDP (8) Tipo Ethernet (2) Fuente Ethernet Encabezado IP (20) Encabezado RTP (12) Carga útil de voz Suma de verificación (4) Dirección (6) Dirección (6) Ethernet Codec g.711 (64 Kbps)

![Un solo paquete de voz g.729 en Ethernet: 20 bytes de carga útil envueltos en 58 bytes de encabezados Ethernet, IP, UDP y RTP — una conversación g.729 consume 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

Puede calcular fácilmente otros requisitos de ancho de banda utilizando una calculadora de ancho de banda VoIP en línea como <https://www.voip.school/bandcalc/bandcalc.php>.


## Ingeniería de tráfico

Un problema principal en el diseño de redes VoIP es dimensionar el número de líneas y el ancho de banda requerido a un destino específico, como una oficina remota o un proveedor de servicios. También es importante dimensionar el número de llamadas simultáneas de Asterisk (parámetro principal para el dimensionamiento de Asterisk).

### Simplificaciones

La simplificación principal y más utilizada es estimar el número de llamadas por tipo de usuario. Por ejemplo:

- PBX empresariales (una llamada simultánea por cada cinco extensiones)
- Usuarios residenciales (una llamada simultánea por cada dieciséis usuarios)

Ejemplo #1 La sede de la empresa tiene 120 extensiones y dos sucursales: la primera con 30 extensiones y la segunda con 15 extensiones. Nuestro objetivo es dimensionar el número de trunks E1 en la sede y el ancho de banda requerido para la red Frame-Relay.

![Topología de red de ejemplo (misma ciudad): la sede con 120 extensiones se conecta a la PSTN a través de líneas T1, y a la sucursal #1 (30 extensiones) y la sucursal #2 (15 extensiones) a través de una nube Frame-Relay.](../images/06-voip-network-fig06.png)

1a Número de líneas T1

- Número total de extensiones usando líneas T1: 120+30+15=165 líneas
- Usando un trunk por cada cinco extensiones para uso comercial
- Número total de líneas = 33 o aproximadamente 2xT1 líneas

1b Requisitos de ancho de banda Elegimos el codec g.729 debido a los requisitos de ancho de banda, la calidad del sonido y el consumo medio de CPU.

Con un trunk por cada cinco extensiones:

- Ancho de banda requerido para la sucursal #1 (Frame-relay): 26.8*6=160.8 Kbps
- Ancho de banda requerido para la sucursal #2 (Frame-relay): 26.8*3= 80.4 Kbps

### Método Erlang B

1.a Número de llamadas simultáneas VoIP A veces, la simplificación no es el mejor enfoque. Cuando tiene datos previos, puede adoptar un enfoque más científico. Utilizaremos el trabajo de Agner Karup Erlang (Copenhagen Telephone Company, 1909), quien desarrolló una fórmula para calcular líneas en un grupo de trunks entre dos ciudades. Erlang es una unidad de medida de tráfico que generalmente se encuentra en telecomunicaciones. Se utiliza para describir el volumen de tráfico durante una hora. Por ejemplo: ocurren 20 llamadas en una hora, con un promedio de 5 minutos de conversación cada una. Puede calcular el número de Erlangs como se muestra a continuación: Minutos de tráfico en la hora: 20 x 5 = 100 minutos Hora de tráfico dentro de una hora: 100/60 = 1.66 Erlangs Puede determinar estas medidas a partir de un registro de llamadas y usarlo para diseñar su red para calcular el número de líneas requeridas. Una vez que se conoce el número de líneas, es posible calcular los requisitos de ancho de banda. Erlang B es el método más utilizado para calcular el número de líneas en un grupo de trunks. Asume que las llamadas llegan aleatoriamente (distribución de Poisson) mientras que las llamadas bloqueadas se borran inmediatamente. Este método requiere que conozca el Tráfico de Hora Pico (BHT), que puede obtener de un registro de llamadas o mediante la siguiente simplificación: BHT=17% de los minutos de llamada de un día.

![Resultados de la calculadora Erlang B: 5 Erlangs al 1% de bloqueo requieren 11 líneas (sede a sucursal #1), y 2.83 Erlangs al 1% de bloqueo requieren 8 líneas (sede a sucursal #2).](../images/06-voip-network-fig07.png)

Otra variable importante es el Grado de Servicio (GoS), que define la probabilidad de bloquear llamadas por escasez de líneas. Puede arbitrar este parámetro, que suele ser 0.05 (5% de llamadas perdidas) o 0.01 (1% de llamadas perdidas). Ejemplo #1: Usando el mismo ejemplo de 5.10.1, le daremos algunos datos sobre los patrones de tráfico. Del registro de llamadas, descubrimos estos datos: Datos del registro de llamadas (Minutos de llamada y BHT):

- Sede a Sucursal #1 = 2,000 minutos, BHT = 300 minutos
- Sede a Sucursal #2 = 1,000 minutos, BHT = 170 minutos
- Sucursal #1 a Sucursal #2 = 0, BHT=0

Arbitremos GoS=0.01

- Sede a Sucursal #1 - BHT=300 minutos/60 = 5 Erlangs
- Sede a Sucursal #2 – BHT=170 minutos/60 = 2.83 Erlangs

Usando una calculadora Erlang como <https://www.erlang.com>

- Para la Sede a la Sucursal #1, se requieren 11 líneas.
- Para la Sede a la Sucursal #2, se requieren 8 líneas

1.b Ancho de banda requerido Estamos usando una WAN donde la pérdida de paquetes es rara. Elegiremos el codec g729 debido a su buena calidad de sonido y compresión de datos (8 Kbps).

Codec seleccionado: g729 Capa de enlace de datos: Frame-Relay

- Ancho de banda de voz estimado para la Sucursal #1: 26.8x11 = 294.8 Kbps
- Ancho de banda de voz estimado para la Sucursal #2: 26.8x8 = 214.40 Kbps

## Reducción del ancho de banda requerido para VoIP

Se pueden utilizar tres métodos para reducir el ancho de banda requerido para las llamadas VoIP:

- Compresión de encabezado RTP
- IAX Trunked
- Carga útil VoIP

### Compresión de encabezado RTP

En redes Frame-Relay y PPP, puede utilizar la compresión de encabezado RTP. La compresión de encabezado RTP fue definida en RFC 2508. Es un estándar IETF disponible en varios routers. Sin embargo, tenga cuidado, ya que algunos routers requieren un conjunto de características diferente para que este recurso esté disponible. El impacto de usar la compresión de encabezado RTP es fabuloso, ya que reduce el ancho de banda requerido en nuestro ejemplo de 26.8 Kbps por conversación de voz a 11.2 Kbps: ¡una reducción del 58.2%!

### Modo trunk IAX2

Si está conectando dos servidores Asterisk, puede utilizar el protocolo IAX2 en modo trunk. Esta tecnología revolucionaria no necesita routers especiales y se puede aplicar a cualquier tipo de enlace de datos.

![Modo trunk IAX2 en Ethernet: una sola llamada g.729 necesita su pila de encabezado completa (31.2 Kbps), pero una segunda llamada comparte esos encabezados y agrega solo un pequeño miniframe IAX2, promediando alrededor de 9.6 Kbps de ancho de banda adicional por llamada adicional.](../images/06-voip-network-fig08.png)

El modo trunk IAX2 reutiliza los mismos encabezados a partir de la segunda llamada en adelante. Usando g729 en un enlace PPP, la primera llamada consumirá 30 Kbps de ancho de banda, mientras que la segunda llamada usará el mismo encabezado que la primera y reducirá el ancho de banda necesario para la llamada adicional a 9.6 Kbps. Podemos calcular el ancho de banda requerido en modo trunk de la siguiente manera: Sucursal #1 (11 llamadas) Ancho de banda = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Sucursal #2 (8 llamadas) Ancho de banda = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps La primera llamada usa 31.2 Kbps, la siguiente 9.6, y así sucesivamente.

### Aumento de la carga útil de voz

Este método es muy común cuando se utilizan gateways VoIP a través de Internet. Al usar una carga útil más grande, sacrificará la latencia en favor de un ancho de banda reducido. Puede cambiar la paquetización RTP añadiendo el tamaño de trama al codec en la instrucción allow.

![Aumento de la carga útil de voz: empaquetar 60 bytes de carga útil g.729 en un paquete (en lugar de 20) amortiza los 58 bytes de encabezados en más voz, reduciendo el ancho de banda a unos 16.05 Kbps por llamada a costa de una latencia añadida.](../images/06-voip-network-fig09.png)

Ejemplo:

```
allow=ulaw:30
```

Los valores permitidos son: Nombre Mín Máx Predeterminado Incremento g723 gsm ulaw alaw g726 ADPCM SLIN lpc10 g729 speex ilbc

## Resumen

En este capítulo, ha aprendido que Asterisk trata VoIP utilizando canales. Admite SIP (a través de `chan_pjsip` en Asterisk 22) e IAX2; H.323 solo está disponible a través del complemento comunitario `ooh323`, y los canales antiguos MGCP y SCCP (Skinny) ya no son parte de una compilación estándar de Asterisk 22. Comparó y aprendió cómo elegir un protocolo de señalización y un codec para canales VoIP. IAX2 es más eficiente en ancho de banda y puede atravesar NAT fácilmente. SIP/PJSIP es el protocolo más compatible por parte de proveedores externos de teléfonos y gateways y es el único controlador de canal SIP en Asterisk 22. El protocolo H.323 es el más antiguo y debe usarse para conectarse a infraestructuras VoIP heredadas. En la sección 5.11, aprendimos cómo diseñar y dimensionar una red VoIP.

## Cuestionario

1. ¿Cuáles de los siguientes son beneficios de VoIP descritos en este capítulo (marque todos los que correspondan)?
   - A. Convergencia de redes de datos y voz para reducir costos
   - B. Menor costo de infraestructura para adiciones, eliminaciones y cambios
   - C. Estándares abiertos que lo liberan de un solo proveedor
   - D. Integración de Telefonía e Informática más fácil y barata
   - E. Tarifas de llamadas por minuto garantizadas más bajas que cualquier compañía telefónica
2. La convergencia es la integración de voz, datos y video en una sola red; su beneficio principal es la reducción de costos en la implementación y mantenimiento de redes separadas.
   - A. Falso
   - B. Verdadero
3. Asterisk trata cada protocolo VoIP como un canal y puede puentear cualquier tipo de canal con cualquier otro, transcodificando entre codecs cuando es necesario.
   - A. Falso
   - B. Verdadero
4. En Asterisk 22, ¿SIP es manejado por qué controlador de canal?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. En el modelo TCP/IP (IETF) contra el cual SIP está realmente definido en RFC 3261, los protocolos de señalización SIP, H.323 e IAX2 operan en la capa ___.
   - A. Presentación
   - B. Aplicación
   - C. Física
   - D. Sesión
   - E. Enlace de datos
6. SIP es el protocolo más adoptado para teléfonos IP y es un estándar abierto definido en gran medida por el IETF en RFC 3261.
   - A. Falso
   - B. Verdadero
7. IAX2 transporta tanto señalización como medios sobre un solo puerto UDP, lo que lo hace eficiente y fácil para atravesar NAT. ¿Qué puerto UDP utiliza IAX2?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX fue desarrollado originalmente por Digium (ahora Sangoma). A pesar de la adopción limitada por parte de los proveedores de teléfonos, IAX es excelente cuando necesita (marque todos los que correspondan):
   - A. Reducir el uso de ancho de banda (no utiliza RTP)
   - B. Un formato de medio de video
   - C. Fácil cruce de NAT y firewall
   - D. Modo trunk para combinar muchas llamadas de Asterisk a Asterisk y amortizar la sobrecarga de encabezado
9. En Asterisk 22, un dispositivo se configura como un único objeto PJSIP `endpoint` que realiza y recibe llamadas; no hay un rol separado de "usuario" o "peer".
   - A. Falso
   - B. Verdadero
10. Con respecto a los codecs en Asterisk 22, marque todas las afirmaciones verdaderas:
    - A. G.711 es equivalente a PCM y utiliza 64 Kbps de ancho de banda.
    - B. El módulo codec_g729 de Sangoma es gratuito para descargar, pero el uso legal requiere una licencia comprada por canal.
    - C. GSM es popular porque utiliza alrededor de 13 Kbps y no necesita licencia.
    - D. G.711 u-law es común en América del Norte, mientras que a-law es común en Europa y América Latina.
    - E. G.729 es ligero y utiliza muy pocos recursos de CPU para codificar y decodificar en comparación con G.711.

**Respuestas:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Aplicación — SIP es un protocolo de capa de aplicación en el modelo TCP/IP que utiliza el IETF) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
