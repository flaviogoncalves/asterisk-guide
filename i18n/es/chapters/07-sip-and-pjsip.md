# SIP y PJSIP en profundidad

SIP es el protocolo; PJSIP es la forma en que Asterisk 22 lo utiliza. **PJSIP** (`chan_pjsip`, configurado vía `pjsip.conf`) es el único controlador de canal SIP en Asterisk 22 LTS. Este capítulo cubre los fundamentos del protocolo SIP (que son a nivel de protocolo y siguen siendo 100 % válidos) y el modelo de objetos y la configuración de PJSIP que utilizas a diario. El controlador heredado en desuso y una guía de migración se tratan en el capítulo *Legacy channels*.

## Objectives

Al final de este capítulo, deberías ser capaz de:

- Explicar el rol de los agentes de usuario SIP, proxies, registrador y pasarelas;
- Seguir un flujo de llamada SIP básico (REGISTER, INVITE, respuestas provisionales y finales, ACK, BYE) y leer un mensaje SIP;
- Describir cómo SDP negocia la sesión de medios y cómo NAT afecta la señalización SIP y RTP;
- Mapear el modelo de objetos PJSIP — `endpoint`, `auth`, `aor`, `transport`, `identify`, y `registration` — y cómo los objetos se referencian entre sí;
- Configurar teléfonos SIP y trunks en `pjsip.conf`, incluidas las opciones de NAT‑traversal; y
- Verificar y solucionar problemas de endpoints con los comandos CLI `pjsip show …`.

## Fundamentos del protocolo SIP

Session Initiation Protocol (SIP) es un protocolo basado en texto similar a HTTP y SMTP que fue diseñado para iniciar, mantener y terminar sesiones de comunicación interactiva entre usuarios. Estas sesiones pueden incluir voz, video, chat, juegos interactivos y otros. SIP fue definido por el IETF y se ha convertido en el estándar de facto para las comunicaciones de voz. Es muy importante entender cómo funciona SIP. En Asterisk 22 la configuración SIP se encuentra en `pjsip.conf`, que es uno de los archivos más editados con frecuencia en un sistema basado en SIP (justo después de `extensions.conf`).

### Teoría de Operación

SIP es un protocolo de señalización con los siguientes componentes: User Agent Client, User Agent Servers, SIP Proxies y SIP Gateways. La siguiente figura muestra las relaciones entre estos componentes.

- UAC (user agent client) – El cliente o terminal que inicializa la señalización SIP.  
- UAS (user agent server) – El servidor que responde a una señalización SIP proveniente de un UAC.  
- UA (user agent) – El terminal SIP (teléfonos o pasarelas que contienen tanto UAC como UAS).  
- Proxy Server – Recibe solicitudes de una UA y las transfiere a otros Proxy SIP si la estación particular no está bajo su administración.  
- Redirect Server – Recibe solicitudes y las envía de vuelta a la UA, incluyendo datos de destino, en lugar de reenviarlas directamente al destino.  
- Location Server – Recibe solicitudes de una UA y actualiza la base de datos de ubicación con esta información.

Usualmente, los servidores proxy, de redirección y de ubicación se alojan en el mismo hardware y utilizan el mismo programa, al que llamamos el SIP proxy. El SIP proxy es responsable del mantenimiento de la base de datos de ubicación, el establecimiento de la conexión y la terminación de la sesión.

![Los componentes principales de SIP: agentes de usuario (UAC/UAS/UA), el servidor de registro/proxy/redirección y una pasarela al PSTN, con el medio RTP fluyendo directamente entre los puntos finales](../images/07-sip-and-pjsip-fig01.png)

#### SIP Proceso de registro

Antes de que un teléfono pueda recibir llamadas, necesita estar registrado en una base de datos de ubicación. En la base de datos de ubicación, la dirección IP se vinculará al nombre. En el siguiente ejemplo, la extensión 8500 se vinculará a la dirección IP 200.180.1.1. No es necesario usar números de teléfono. En la arquitectura SIP, la extensión registrada podría ser flavio@voip.school también.

![Registro SIP: el teléfono envía un REGISTER vinculando la extensión 8500 a su dirección IP, el registrador almacena el contacto en la base de datos de ubicación y responde con 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### Operación de proxy

When operating as a SIP proxy, the SIP server stays in the middle of the signaling and is capable of advanced routing and billing. The media flow, based on the real time protocol (RTP) still goes directly between the endpoints.

![Operación del proxy: el proxy SIP permanece en la ruta de señalización (INVITE/200 OK) y busca al llamado en el servidor de ubicación, mientras que los medios RTP fluyen directamente entre los dos endpoints](../images/07-sip-and-pjsip-fig03.png)

#### Operación de redirección

Al redirigir, el servidor SIP simplemente envía un mensaje (p. ej., 302 moved temporarily) al agente de usuario y se mantiene fuera de la ruta de los nuevos mensajes. Es muy ligero en cuanto al uso de recursos, pero no tienes ningún control. La redirección a veces se usa en diseños de balanceo de carga.

![Operación de redirección: el servidor de redirección responde al INVITE con un 302 Moved Temporarily que lleva el contacto, luego se retira mientras el llamante vuelve a enviar INVITE/ACK directamente a la nueva ubicación](../images/07-sip-and-pjsip-fig04.png)

#### Cómo Asterisk maneja SIP

Es importante entender que Asterisk no es ni un proxy SIP ni un redireccionador SIP. Asterisk puede desempeñar el papel de servidor de registro y de ubicación; sin embargo, solo conecta dos UAC a sí mismo. Por lo tanto, Asterisk se considera un agente de usuario back-to-back (B2BUA). En otras palabras, conecta dos canales SIP, puenteándolos entre sí. Asterisk tiene un mecanismo de re‑invite que puede hacer que los canales SIP se comuniquen directamente entre sí en lugar de pasar por Asterisk. En un endpoint PJSIP esto se controla mediante el parámetro `direct_media`. Al usar `direct_media=yes` el flujo RTP va directamente de un endpoint a otro, liberando recursos del servidor.

#### Operación SIP con direct_media=yes

![Operación SIP con directmedia=yes: la señalización SIP fluye a través de Asterisk mientras el audio RTP va directamente entre los dos teléfonos, liberando recursos del servidor](../images/07-sip-and-pjsip-fig05.png)

Sin embargo, si necesita transferir o grabar la llamada usando Asterisk, puede usar el parámetro `direct_media=no` para forzar el flujo RTP a través del servidor Asterisk.

#### Operación SIP con direct_media=no

![Operación SIP con directmedia=no: tanto la señalización SIP como el audio RTP están anclados a través de Asterisk, lo que permite grabar, transcodificar o transferir la llamada](../images/07-sip-and-pjsip-fig06.png)

#### Mensajes SIP

Los mensajes SIP básicos son:

- INVITE – establecimiento de conexión
- ACK – reconocimiento
- BYE – terminación de conexión
- CANCEL – terminación de conexión para una llamada no establecida
- REGISTER – registrar un UAC en un proxy SIP
- OPTIONS – puede usarse para comprobar disponibilidad
- REFER – transferir una llamada SIP a otra persona
- SUBSCRIBE – suscribirse a eventos de notificación
- NOTIFY – enviar información del canal
- INFO – enviar varios mensajes (p. ej., DTMF )
- MESSAGE – enviar mensajes instantáneos

Las respuestas SIP están en formato de texto y son fácilmente legibles (similares a los mensajes HTTP). Las respuestas más importantes son:

- 1XX – Mensajes de información (100–trying, 180–ringing, 183–progress)
- 2XX – Solicitud completada con éxito (200 – OK)
- 3XX – Redirección de llamada, la solicitud debe dirigirse a otro lugar (302 – moved temporarily, 305 – use proxy)
- 4XX – Error (403 – Forbidden)
- 5XX – Error del servidor (500 – Internal Server Error; 501 – Not implemented)
- 6XX – Falla global (606 – Not acceptable)

Por ejemplo:

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### Protocolo de descripción de sesión (SDP)

SDP fue definido originalmente en el RFC 2327 del IETF, ahora obsoleto por el RFC 4566. Está destinado a describir sesiones multimedia para los propósitos de anuncio de sesión, invitación a sesión y otras formas de iniciación de sesiones multimedia. SDP incluye:

- Protocolo de transporte (RTP/UDP/IP)
- Tipo de medio (texto, audio, video)
- Formato de medio o códec (video H.261, audio g.711, etc.)
- Información necesaria para recibir estos medios (direcciones, puertos, etc.)

El siguiente ejemplo es una transcripción de un SDP que describe una llamada entre dos teléfonos.

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### Recorrido NAT de SIP

Network Address Translation (NAT) es una característica utilizada por la mayoría de las redes para ahorrar direcciones IP de Internet. Usualmente, una empresa recibe un pequeño bloque de direcciones IP, y los usuarios finales reciben una dirección IP de forma dinámica cuando se conectan a Internet. NAT resuelve el problema de direccionamiento al mapear direcciones internas a direcciones externas. Almacena un mapeo de direcciones internas a externas en su memoria. Este mapeo es válido por un tiempo específico, tras el cual se descarta. El mapeo utiliza pares IP:puerto para las direcciones internas y externas. Existen cuatro tipos de NAT:

- Cono completo
- Cono restringido
- Cono con puerto restringido
- Simétrico

La teoría NAT a continuación — los cuatro tipos de NAT, el problema del encabezado Contact, los keep-alives y forzar los medios a través del servidor — es a nivel de protocolo y se aplica a cualquier implementación SIP. La forma en que configura cada comportamiento en Asterisk 22 (PJSIP) se cubre más adelante en este capítulo bajo *Nat traversal on res_pjsip*.

#### Cono Completo

El primer NAT, full cone, representa un mapeo estático de un par IP:puerto externo a un par IP:puerto interno. Cualquier computadora externa puede conectarse a él usando el par IP:puerto externo. Este es el caso en firewalls no stateful implementados con el uso de filtros.

![Full Cone NAT: el host interno (10.0.0.1:8000) está mapeado estáticamente al par externo 200.180.4.168:1234, de modo que cualquier computadora externa puede enviar paquetes a ese par y alcanzar el host interno](../images/07-sip-and-pjsip-fig11.png)

#### Cono Restringido

En el escenario de cono restringido, el par IP:puerto externo se abre solo cuando la computadora interna envía datos a una dirección externa. Sin embargo, el NAT de cono restringido bloquea cualquier paquete entrante de una dirección diferente. En otras palabras, la computadora interna debe enviar datos a una computadora externa antes de que pueda recibir datos de vuelta.

#### Cono de Puerto Restringido

El firewall de cono restringido por puerto es casi idéntico al cono restringido. La única diferencia es que, ahora, el paquete entrante debe provenir exactamente de la misma IP y puerto del paquete enviado.

#### Simétrica

El último tipo de NAT se llama simétrico. Es diferente de los tres primeros en que se realiza un mapeo específico para cada dirección externa. Sólo se permiten direcciones externas específicas para volver a través del mapeo NAT. No es posible predecir el par IP:puerto externo que usará el dispositivo NAT. Los otros tres tipos de NAT permiten usar un servidor externo para descubrir la dirección IP externa para la comunicación. Con NAT simétrico, incluso si puedes conectarte a un servidor externo, la dirección descubierta no puede usarse para ningún otro dispositivo excepto para este servidor.

![NAT simétrica: se asigna un puerto de origen externo diferente para cada destino, de modo que la asignación descubierta hacia un servidor no puede ser reutilizada por otro host, lo que rompe la traversía basada en STUN】(../images/07-sip-and-pjsip-fig12.png)

#### tabla de firewall NAT

La tabla siguiente resume los cuatro tipos de NAT.

| Tipo NAT | Debe enviar datos primero | Puede determinar la IP:puerto externa para paquetes de retorno | Restringe los paquetes entrantes al IP:puerto de destino |
| --- | --- | --- | --- |
| Full Cone | No | Sí | No |
| Restricted Cone | Sí | Sí | Solo IP |
| Port Restricted Cone | Sí | Sí | Sí |
| Symmetric | Sí | No | Sí |

#### SIP señalización y RTP sobre NAT

Algunos de los problemas más grandes en la traversa de NAT son que debes resolver dos cuestiones: la señalización SIP y el audio (RTP). La mayoría de los problemas de audio unidireccional están relacionados con NAT. Un aspecto interesante de SIP es que, cuando un UAC envía un paquete, inserta la dirección IP en el campo de encabezado SIP “Contact”. Usualmente esta es una dirección interna (RFC1918); las respuestas a este paquete no pueden ser enrutadas a través de Internet de regreso al UAC. Las soluciones conceptuales son siempre las mismas:

- **Ignore the Contact/Via address and reply to where the packet actually came from.** This is the behaviour defined in RFC 3581 (`rport`). On PJSIP it is `force_rport=yes`, and `rewrite_contact=yes` rewrites the stored contact to the source address.
- **Send media back to the address the RTP actually arrived from** (symmetric RTP, historically called *comedia*). On PJSIP this is `rtp_symmetric=yes`.
- **Keep the NAT mapping open.** If the mapping times out, Asterisk can no longer send an INVITE to the UAC — the phone can place calls but not receive them. Sending a periodic OPTIONS (a *qualify*) keeps the pinhole open. On PJSIP this is `qualify_frequency=` on the AOR.

Si el NAT del usuario es del tipo simétrico, no es posible enviar paquetes de un UAC a otro directamente; en ese caso debe forzar el RTP a través de Asterisk con `direct_media=no`. Estas configuraciones son apropiadas para la mayoría de los casos. Es posible optimizar el tráfico usando técnicas avanzadas como Simple Traversal of UDP over NAT (STUN), que es útil con cono completo, cono restringido y cono restringido por puerto, y Application Layer Gateway (ALG). Desafortunadamente, la mayoría de los firewalls actuales — incluso los routers domésticos DSL/cable — son simétricos, lo que hace que STUN sea inutilizable. ALG podría resolver el problema, pero no está soportado, no está implementado o presenta errores en la mayoría de los casos.

#### Asterisk detrás de NAT

A veces el servidor Asterisk está implementado detrás de un firewall con NAT — una situación muy común cuando se despliega en la nube. En este caso es necesario realizar una configuración adicional para que Asterisk anuncie su dirección **pública** en los encabezados SIP y SDP en lugar de la privada.

Conceptualmente hay tres pasos:

- Reenviar el puerto de señalización SIP (UDP 5060 por defecto) del firewall al servidor Asterisk.  
- Reenviar el rango de puertos de medios RTP (UDP 10000–20000 por defecto, configurado en `rtp.conf`) del firewall al servidor Asterisk.  
- Indicar a Asterisk su dirección externa y qué red es local, para que sepa cuándo sustituir la dirección pública en los encabezados.

En PJSIP estos dos últimos elementos se asignan a `external_media_address` / `external_signaling_address` y `local_net=` en el **transport**, y el rango de puertos RTP sigue configurado en `rtp.conf`:

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

El configuración completa y funcional de PJSIP para un servidor Asterisk detrás de NAT se muestra más adelante en este capítulo bajo *Asterisk Server behind NAT*.

### Limitaciones de SIP

Asterisk usa el flujo RTP entrante para sincronizar el flujo saliente. Si el flujo entrante se interrumpe (supresión de silencio), la música en espera se cortará. En otras palabras, no debe usar supresión de silencio en teléfonos o proveedores con Asterisk.

## PJSIP: el canal SIP

PJSIP es el canal SIP en Asterisk. Fue introducido por primera vez en Asterisk 12 y, tras años de desarrollo, se convirtió en el canal SIP predeterminado y recomendado, y en Asterisk 22 (el LTS actual) es el único controlador de canal SIP. PJSIP se basa en el proyecto de Teluu llamado pjproject. La pila pjproject es utilizada por muchos softphones e implementaciones SIP comerciales. Es una pila SIP versátil y madura.

### Por qué usar PJSIP

PJSIP fue un rediseño completo de cómo Asterisk habla SIP, y vale la pena entender las características que lo convirtieron en el estándar.

#### Características

El canal soporta muchas características, algunas merecen mención aquí

- Multiple registrations: You may use more than one phone connected to the same Address of Record. In other words, you can connect two phones to the same endpoint.
- Friendly Application Program Interface (API). The API is modular and easy to extend, built from many small cooperating modules rather than one large block of code.
- Multiple transports: You can listen to multiple addresses, ports and transports when using PJSIP. You are not limited to a single bind address for all your devices. PJSIP is very flexible.

#### Una nota sobre la configuración

PJSIP configuration is more verbose: it requires a little more effort and more lines of configuration, since each device is described by several related objects instead of one peer block. That extra structure is what gives PJSIP its flexibility, and the configuration wizard (covered later) keeps day-to‑to provisioning short.

### Módulos PJSIP

The PJSIP channel is implemented by many modules described below:

#### res_pjsip

This is the base layer of PJSIP and the main module. It is responsible for some of the main services.

#### res_pjsip_session

This module is responsible for media sessions, session description protocol processing and some addons

#### res_pjsip_messaging

Process SIP messages and parse SIP headers.

#### res_pjsip_registrar

Responsible to handle SIP registrations

#### res_pjsip_pubsub

Responsible to process subscribe, notify and publish. These messages are responsible to handle SIP presence and BLF (Busy Lamp Field).

### Configuración PJSIP

PJSIP has many different sections. The format of the section are:

```
[Section Name]
Option = Value
Option = Value
```

#### Sección de punto final

El objeto de configuración más importante es el endpoint. La configuración del endpoint tiene funcionalidad central y debe asociarse con una sección AOR y Transport. Ejemplo:

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

Si observas el ejemplo anterior, el endpoint es una especie de pegamento que une todas las secciones. Especifica un transporte, la dirección de registro y la autenticación para un teléfono. También define la parte más importante, el punto de entrada del contexto en el dialplan.

#### Dirección de Registro (AOR)

Este objeto indica a Asterisk dónde contactar al endpoint. Almacena las direcciones de contacto. También permite la configuración de buzones de correo. Ejemplo:

```
[softphone]
type=aor
max_contacts=2
```

#### Autenticación

Esta sección es responsable de la autenticación entrante y saliente. La documentación se encuentra en el archivo de ejemplo pjsip.conf. Ejemplo:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### Transporte

La sección de transporte le permite definir direcciones IPV4 e IPV6 y el protocolo de transporte, TCP, UDP, TLS, Websockets, etc. También puede configurar direcciones con NAT en esta sección. Puede crear múltiples transportes, pero no pueden compartir la misma IP y puerto y no puede enlazar varios transportes TCP o TLS de la misma versión IP. Ejemplo:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### Registro

Este objeto se utiliza para configurar un registro saliente. Ejemplo:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### Identificar

Este objeto controla a qué solicitud SIP pertenece cada endpoint. Si no tiene una sección identify, el sistema coincidirá el contenido del encabezado “From” con el nombre del endpoint. Usando esta sección, puede asignar direcciones IP específicas a endpoints específicos, identificados por nombre de usuario o IP. Ejemplo:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

El objeto ACL le permite configurar redes específicas con acceso al endpoint. Ahora los ACL se definen en una sección específica o en el acl.conf. Ejemplo:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### Relación entre entidades

La relación entre los objetos de configuración brinda una gran flexibilidad para la configuración. Sin embargo, puede parecer un poco compleja para quien está comenzando.

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

El gráfico anterior significa:

#### Relaciones:

| Objects | Cardinality |
| --- | --- |
| ENDPOINT / AOR | muchos a muchos |
| ENDPOINT / AUTH | cero a muchos, a cero a uno |
| ENDPOINT / IDENTIFY | cero a uno |
| ENDPOINT / TRANSPORT | cero a muchos, al menos uno |
| REGISTRATION / AUTH | cero a muchos, a cero a uno |
| REGISTRATION / TRANSPORT | cero a muchos, al menos uno |
| AOR / CONTACT | muchos a muchos |

ACL y DOMAIN_ALIAS no tienen una relación de configuración directa con los demás objetos.

### Configuración de un Softphone

Para configurar un softphone debes definir muchas secciones diferentes. A continuación, un ejemplo de cómo configurar un softphone. En el lado del cliente puedes usar el SipPulse Softphone (https://www.sippulse.com/produtos/softphone), que puedes descargar y registrar contra el endpoint abajo.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

The configuration above sets a transport for UDP in the port 5060, then define an endpoint, its authentication by username and password and then the Address of Record with a maximum of two contacts.

### Configuring a SIP trunk

To configure a SIP trunk you need to have the IP address or Host of the SIP trunk, name and password. You have to create a new registration section for this purpose.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=digest
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### Nat traversal on res_pjsip

Network Address Translation was created a long time ago as a way to deal with the shortage of IP version 4 addresses. Many people also use NAT as a security feature hiding the internal addresses of a network from the public Internet. Sometimes you will have to handle NAT traversal. In some cases, the server can be behind NAT, such as where you are deploying the server in the cloud. Many times if you are deploying in the cloud your users will also be behind a NAT router. To organize things, we will split this into two parts. The first one is the Asterisk server behind NAT such as in a cloud deployment. In the second section, we will cover how to support clients behind NAT using res_pjsip.

#### Asterisk Server behind NAT

When the Asterisk server is behind NAT, you should inform the external and internal local addresses in the transport section. We will have the following directives.

##### direct_media

Does the media flow directly from peer to peer or thru the server? For NAT it should flow thru the server. For NAT select no. Example:

```
direct_media=no
```

##### external_media_address

Dirección de medios para manejar RTP externo. Usualmente la misma que external_signaling_address. Use la dirección IP pública de su servidor para medios y señalización. Ejemplo:

```
external_media_address=54.232.1.20
```

##### external_signaling_address

Dirección SIP externa donde recibir mensajes. Ejemplo:

```
external_signaling_address=54.232.1.20
```

##### local_net

La red que consideras tu red local. Ejemplo:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### Ejemplo completo de transporte para un servidor Asterisk detrás de NAT

Para usar un servidor Asterisk detrás de NAT debes realizar dos pasos. Primero, define un transporte detrás de NAT. Segundo, asocia este transporte al endpoint.

##### Creación del transporte detrás de NAT

Para crear el transporte detrás de NAT en el archivo `pjsip.conf` crea una sección como la siguiente.

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

# Asociar el transporte a un punto final

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

Para los trunks SIP también debe asociar el transporte a la sección de registro como se muestra a continuación.

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### Usando Asterisk con clientes detrás de NAT

Para usar teléfonos detrás de NAT debes configurar algunos parámetros adicionales por endpoint.

##### direct_media

¿Fluye el medio directamente de par a par o a través del servidor? Para NAT debería fluir a través del servidor. Ejemplo:

```
direct_media=no
```

##### rtp_symmetric

Esto es lo que llamamos comedia. En lugar de confiar en la dirección definida en este encabezado SDP como es habitual en SIP, use la dirección desde donde recibe el primer paquete rtp y envíe de vuelta desde la misma dirección. Ejemplo:

```
rtp_symmetric=yes
```

##### force_rport

Este es el comportamiento definido en el RFC3581. En lugar de usar la dirección en el encabezado VIA, envía de vuelta las respuestas desde donde provienen las solicitudes. Ejemplo:

```
force_rport=yes
```

##### qualify_frequency

Esta configuración debe aplicarse al AOR (no al endpoint). También está el último paso, configurar la opción qualify. Siempre debe haber algunos paquetes haciendo ping al destino para mantener abierta la asignación NAT. Esto se establece en la sección AOR. Ejemplo:

- qualify_frequency=15

Ejemplo completo de un endpoint donde el servidor y el cliente están detrás de NAT

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### Nombrado de Canal

Como es habitual, uno de los aspectos importantes de un canal es su nombrado y PJSIP tiene algunos detalles interesantes. Usted marca un endpoint PJSIP con la tecnología `PJSIP/`:

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

Una característica útil es la posibilidad de marcar todos los contactos registrados en un AOR de una sola vez. La función PJSIP_DIAL_CONTACTS se traducirá a la lista de contactos a marcar.

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

To dial a trunk is slightly different. Assume the trunk won’t be registered to your platform or don’t have and IP address associated with your AOR address of record. You can specify the address of the trunk directly in the line. Using an international dial as the example.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

Si prefiere especificar la dirección del trunk en la sección AOR, también puede usar.

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### Asistente de configuración de PJSIP

PJSIP es potente pero verboso de configurar: muchas secciones diferentes, y plantillas que pueden resultar confusas al principio. La buena noticia es el asistente de configuración de PJSIP. Definiendo cada canal en unas pocas líneas, permite crear plantillas y simplificar la configuración de nuevos dispositivos. Use el archivo pjsip_wizard.conf para configurar. Aún debe definir las secciones transport y global en el archivo pjsip.conf. Personalmente, prefiero usar el asistente solo para teléfonos; para sip trunks usualmente el número no es grande y puede configurarse directamente en pjsip. La mayor ventaja del asistente es la posibilidad de usar plantillas y crear teléfonos rápidamente.

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### Cargando y descargando PJSIP

PJSIP es el único canal SIP en Asterisk 22, y sus módulos se cargan por defecto. En casos raros aún puede que desee controlar la carga de módulos desde el archivo modules.conf — por ejemplo, para desactivar PJSIP en un servidor que solo usa IAX2 o DAHDI.

#### Para desactivar PJSIP

Edite el archivo modules.conf y añada las siguientes líneas.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### Comandos de consola

Ahora que configuraste tus endpoints PJSIP, es hora de ver cómo verificar tu configuración. Hay muchos comandos de consola que te ayudarán con esta tarea. Después de editar pjsip.conf, recarga la configuración con:

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

Este comando enumera los objetos Address of Record configurados y sus contactos, para que pueda confirmar a dónde enviará Asterisk las llamadas para cada endpoint.

#### pjsip show registrations

El comando a continuación muestra los registros realizados por nuestro propio servidor.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

La lista de comandos es un poco más amigable y muestra menos datos, pero está mejor estructurada. Listado de endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listado de contactos:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

El comando de solución de problemas más útil es el registrador de paquetes SIP. Imprime cada solicitud y respuesta SIP en la consola a medida que se envía o recibe, lo cual es invaluable al diagnosticar problemas de registro y configuración de llamadas.

```
pjsip set logger on
pjsip set logger off
```

You can also restrict the logging to a single host with `pjsip set logger host <ip>`.

#### pjsip set history on

A great addition to PJSIP is the concept of history. You can capture and analyse SIP request and replies in real time in an easy way. To start history use the command below.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Now you can show the history:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

Then to see a specific request or reply, show the history item:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

Very easy, isn’t it? You may also clear the history whenever you want using `pjsip set history clear`.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Resumen

SIP es el protocolo de señalización de IETF que establece, modifica y finaliza sesiones de medios. Sus agentes de usuario, proxies, registrador y pasarelas intercambian mensajes basados en texto — REGISTER, INVITE, las respuestas provisionales y finales, ACK y BYE — mientras SDP negocia los códecs y RTP transporta los medios. Esa teoría del protocolo es atemporal y se aplica a cualquier implementación de SIP.

En Asterisk 22 se utiliza SIP a través de **PJSIP** (`chan_pjsip`), configurado en `pjsip.conf`. En lugar de un único peer monolítico, un dispositivo se modela como un conjunto de objetos pequeños y referenciados entre sí: `endpoint` (comportamiento de la llamada y códecs), `auth` (credenciales), `aor` (dónde es alcanzable) y `transport` (el listener), más `identify` (coincidir un trunk por IP) y `registration` (registro saliente) para proveedores de servicio. Viste cómo encajan estos objetos, cómo configurar tanto teléfonos como trunks, cómo las opciones de NAT‑traversal (`force_rport`, `rewrite_contact`, `rtp_symmetric`, `direct_media` y los `external_*`/`local_net` del transporte) resuelven implementaciones del mundo real, y cómo inspeccionarlo todo con `pjsip show endpoints`, `aors`, `contacts` y `registrations`.

## Quiz

1. En la arquitectura SIP, ¿qué componente recibe una solicitud y la responde con una respuesta de redirección (como `302 Moved Temporarily`) que lleva la nueva ubicación, y luego sale del camino de los mensajes posteriores?
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. ¿Qué papel desempeña Asterisk cuando maneja una llamada SIP entre dos teléfonos?
   - A. A SIP proxy that stays only in the signaling path
   - B. A SIP redirect server
   - C. A back-to-back user agent (B2BUA) that bridges two SIP channels
   - D. A stateless SIP load balancer

3. ¿Qué método SIP usa un teléfono para informar al registrador su dirección IP actual para que luego pueda recibir llamadas?
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. Verdadero o Falso: En Asterisk 22, `chan_sip` y `sip.conf` siguen disponibles como una alternativa heredada junto a PJSIP.

5. ¿Con qué objetos de configuración debe asociarse un endpoint para que Asterisk conozca el socket de escucha a usar y a dónde enviar las llamadas para ese dispositivo? (Elija todas las que correspondan.)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. En un objeto PJSIP `aor`, ¿qué ajuste mantiene abierto el mapeo NAT calificando periódicamente el contacto, y cuál es su unidad?
   - A. `qualify=yes` (boolean)
   - B. `qualify_frequency` (seconds)
   - C. `rtp_timeout` (milliseconds)
   - D. `nat=force_rport`

7. Complete el espacio en blanco: Para que Asterisk haga coincidir una solicitud SIP entrante con un endpoint específico por dirección IP de origen (en lugar de por el encabezado `From`), crea una sección con `type=________`.

8. ¿Qué objeto PJSIP se usa para configurar un **registro saliente** de Asterisk a un proveedor de tronco SIP?
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. En la CLI de Asterisk 22, ¿qué comando habilita el registrador de paquetes SIP que imprime cada solicitud y respuesta SIP en la consola?
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. En un endpoint PJSIP que sirve a un teléfono detrás de un NAT simétrico, ¿qué par de ajustes hace que Asterisk responda a la dirección de origen de la solicitud (RFC 3581) y envíe medios de vuelta a donde realmente llega el RTP?
    - A. `direct_media=yes` and `srvlookup=yes`
    - B. `force_rport=yes` and `rtp_symmetric=yes`
    - C. `allowguest=yes` and `insecure=invite`
    - D. `qualify=yes` and `nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
