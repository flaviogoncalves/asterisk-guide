# Construyendo su primer PBX con PJSIP

En este capítulo, aprenderá cómo realizar una configuración básica de un PBX Asterisk. El objetivo principal aquí es ver el PBX en funcionamiento por primera vez, poder marcar entre extensiones, marcar un mensaje que se está reproduciendo y marcar a un único tronco analógico o SIP. La idea detrás de este capítulo es asegurar que su Asterisk esté activo y funcionando lo antes posible. Después de completar el trabajo en este capítulo, tendrá los conocimientos suficientes para prepararse para los capítulos siguientes, donde profundizaremos más en los detalles de la configuración.

## Objetivos

Al final de este capítulo, deberías ser capaz de:

- Entender y editar archivos de configuración;
- Instalar softphones basados en SIP;
- Instalar y configurar un trunk SIP;
- Instalar y configurar una conexión analógica;
- Marcar entre extensiones;
- Marcar entre teléfonos y destinos externos; y
- Configurar un auto‑atendedor.

## Understanding the configuration files

Asterisk es controlado por archivos de configuración de texto ubicados en /etc/asterisk. El formato del archivo es similar a los archivos “.ini” de Windows. Se usa un punto y coma como carácter de comentario, los signos “=” y “=>” son equivalentes, y los espacios se ignoran.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interpreta “=” y “=>” de la misma manera. Las diferencias en la sintaxis se usan para distinguir entre objetos y variables. Use “=” cuando quiera declarar una variable y “=>” para designar un objeto. La sintaxis es la misma en todos los archivos, pero se utilizan tres tipos de gramática, como se discute a continuación.

## Gramáticas

| Gramática | Cómo se crea el objeto | Archivo de conf. | Ejemplo |
|-----------|------------------------|------------------|---------|
| Grupo simple | Todo en la misma línea | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Herencia de opciones | Las opciones se definen primero, el objeto hereda las opciones | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Entidad compleja | Cada entidad recibe un contexto | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Grupo simple

El formato de grupo simple usado en `extensions.conf` y `voicemail.conf` es la gramática más básica. Cada objeto se declara con opciones en la misma línea. Ejemplo:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

En este ejemplo, el objeto 1 se crea con las opciones op1, op2 y op3 mientras que el objeto 2 se crea con las opciones op1, op2 y op3.

### Gramática de herencia de opciones de objeto

Este formato es usado por los archivos chan_dahdi.conf y agents.conf, donde existen numerosas opciones y la mayoría de interfaces y objetos comparten las mismas opciones. Típicamente, una o más secciones tienen declaraciones de objetos y canales. Las opciones del objeto se declaran sobre el objeto y pueden cambiarse para otro objeto. Aunque este concepto es difícil de entender, es muy fácil de usar. Ejemplo:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

Las dos primeras líneas configuran el valor de las opciones op1 y op2 a “bas” y “adv”, respectivamente. Cuando el objeto 1 se instancia, se crea usando la opción 1 como “bas” y la opción 2 como “adv”. Después de definir el objeto 1, cambiamos la opción 1 a “int”. A continuación, creamos el objeto 2 con la opción 1 como “int” y la opción 2 como “adv”.

### Objeto de entidad compleja

Este formato es usado por pjsip.conf, iax.conf y otros archivos de configuración en los que existen numerosas entidades con muchas opciones. Típicamente, este formato no comparte un gran volumen de configuraciones comunes. Cada entidad recibe un contexto. A veces existen contextos reservados, como [general] para configuraciones globales. Las opciones se declaran en las declaraciones de contexto. Ejemplo:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

La entidad [entity1] tiene los valores “value1” y “value2” para las opciones op1 y op2, respectivamente. La entidad [entity2] tiene los valores “value3” y “value4” para las opciones op1 y op2.

## Opciones para construir un LAB para Asterisk

Para configurar una PBX, necesitará algo de hardware básico. No es difícil ni costoso, pero hay algunas opciones que deben considerarse. Todo lo que necesitará son dos teléfonos y una conexión a la red pública. Algunas opciones y combinaciones son posibles al crear su laboratorio, que discutiremos a continuación.

### Opción 1: LAB completo

Con el LAB completo, es posible probar todos los escenarios disponibles y comparar soluciones como ATA, teléfonos IP y softphones. También podrá aprender sobre trunks analógicos y SIP. Necesitará:

- Un adaptador telefónico analógico SIP (ATA)
- Un teléfono IP
- Un servidor dedicado para Asterisk
- Una estación de trabajo con un softphone
- Una tarjeta de interfaz analógica con al menos dos interfaces (1 FXO y 1 FXS)
- Una cuenta de proveedor de VoIP

### Opción 2: LAB económico

Con el LAB económico, lo simplificamos un poco. Usamos el ATA, que suele ser menos costoso que el teléfono IP, y una única tarjeta FXO, que es realmente barata. No podremos usar teléfonos analógicos conectados directamente al servidor, pero esto no ocurre comúnmente en la práctica. Necesitará:

- Un adaptador telefónico analógico SIP (ATA)
- Un servidor dedicado para Asterisk
- Una estación de trabajo para el softphone
- Una tarjeta de interfaz analógica con 1 FXO
- Una cuenta con un proveedor de VoIP

### Opción 3: LAB súper económico

El tercer LAB utiliza un servidor virtualizado en el propio notebook del estudiante. El problema con este modelo son los conflictos generados por el puerto UDP. A veces tanto el servidor Asterisk como el softphone intentan acceder al mismo puerto, impidiendo que Asterisk vincule el puerto de la dirección. Otro asunto es la calidad de las llamadas; los entornos virtuales no están indicados para aplicaciones en tiempo real como Asterisk. Use un softphone gratuito para el servidor y la estación de trabajo y una conexión trunk a un proveedor SIP. Necesitará:

- Un portátil que ejecute un softphone
- Una máquina virtual (VirtualBox, VMware o similar) para instalar Asterisk
- Una cuenta con un proveedor de VoIP

## Secuencia de instalación

Para ayudarle a comprender la secuencia de instalación, hemos descrito los pasos necesarios para instalar y configurar Asterisk.

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. Configuración de extensiones
   - a. Extensiones SIP (ATA, Softphone, IP Phone)
   - b. Extensiones IAX
   - c. Extensiones FXS
2. Configuración de troncos
   - a. Configuración de un tronco SIP
   - b. Configuración de un tronco FXO
3. Construcción de un plan de marcación básico
   - a. Marcación entre extensiones
   - b. Marcación a destinos externos
   - c. Recepción de una llamada en la extensión del operador
   - d. Recepción de una llamada en un asistente automático

## Configuración de las extensiones

Las extensiones son teléfonos SIP, IAX o analógicos conectados a un puerto FXS. Para configurar una extensión, debe editar el archivo de configuración relacionado con el canal (pjsip.conf, iax.conf, chan_dahdi.conf)

### Extensiones SIP

En Asterisk 22, PJSIP (la pila `res_pjsip`, configurada en `/etc/asterisk/pjsip.conf`) es el controlador del canal SIP. Soporta múltiples transportes por endpoint, se mantiene activamente y es el único controlador SIP incluido con la plataforma. (El controlador original `chan_sip` fue eliminado en Asterisk 21 — consulte el capítulo *Legacy channels* si necesita migrar una configuración antigua.)

La idea aquí es configurar una PBX simple. (Los capítulos siguientes proporcionan una sesión completa SIP/PJSIP con todos los detalles.) PJSIP se configura en `/etc/asterisk/pjsip.conf` y contiene todos los parámetros relacionados con teléfonos SIP y proveedores VoIP. Los clientes SIP deben configurarse antes de que pueda realizar y recibir llamadas.

#### El transporte

En PJSIP, la configuración del listener (dirección de enlace, puerto, protocolo) vive en un objeto `transport`. Asterisk tiene protección incorporada contra la adivinación de nombres de usuario — siempre devuelve un desafío de autenticación idéntico para usuarios desconocidos y conocidos, y las solicitudes no identificadas repetidas desde una IP son limitadas en velocidad mediante las opciones `[global]` `unidentified_request_count`/`unidentified_request_period`. Las opciones principales de un transporte son:

- protocol: El protocolo de transporte — `udp`, `tcp`, `tls`, `ws`, o `wss`.  
- bind: Dirección y puerto a los que el listener se enlaza. Si establece la dirección a `0.0.0.0`, se enlaza a todas las interfaces; el puerto SIP por defecto es 5060 para UDP/TCP.

Un transporte UDP mínimo:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Codec selection (`disallow`/`allow`) and the default `context` are configured on each `endpoint` (shown below), not on the transport. Anonymous/guest calls are handled by an `endpoint` named `anonymous`. Registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`.

#### SIP clients

After completing the transport section, it is time to set up the SIP clients. I would once again like to remind the reader that we will have an entire SIP/PJSIP chapter later in the book. For now, let’s concentrate on the basics and leave the details for later.

In PJSIP a SIP client is built from a set of related objects, tied together by name reference:

- `endpoint`: The call behaviour — codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.
- `auth`: The credentials. `username` is the SIP authentication user and `password` is the secret used to authenticate the device.
- `aor`: The "address of record" — where the endpoint can be reached. Either a static `contact=` (for a device at a fixed IP) or `max_contacts=` to allow the device to register dynamically.

Warning: Use strong passwords, with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for SIP are easily available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers.

Endpoint 6000 is a device at a fixed IP, so its AOR carries a static `contact` instead of allowing registration. Endpoint 6001 is a device that registers, so its AOR allows it to register (`max_contacts=1`):

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=digest
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP permite que las secciones `endpoint`, `auth` y `aor` compartan el mismo nombre de sección (p. ej., los dos bloques `[6001]` anteriores, distinguidos por sus `type=`); muchos administradores en su lugar les añaden un sufijo (`[6001]`, `[6001-auth]`, `[6001]` aor) para mayor legibilidad. Para un dispositivo que se registra, el contacto se aprende dinámicamente cuando el teléfono se registra, por lo que el AOR no necesita un `contact` estático.

## Extensiones IAX

`chan_iax2` todavía se incluye en Asterisk 22 pero ahora es heredado; SIP/PJSIP es el protocolo preferido para nuevas implementaciones.

También puede crear extensiones IAX. Este protocolo es nativo de Asterisk, y tendremos una sección completa dedicada a él más adelante en este libro. Por ahora, vamos a crear algunas extensiones usando el protocolo. Como primera sección a configurar, la sección [general] tiene ciertos parámetros que deben configurarse. Las opciones principales son:

- allow/disallow: Define qué códecs se van a usar.
- bindaddr: Dirección a la que se enlaza el escuchador IAX2. Si lo configura como 0.0.0.0 (valor predeterminado), se enlazará a todas las interfaces.
- context: Establece el contexto predeterminado para todos los clientes a menos que se cambie en la sección del cliente. Usamos dummy por razones de seguridad. Los usuarios no autenticados entran en este contexto cuando la opción allowguest está establecida en yes.
- bindport: Puerto UDP IAX2 en el que escuchar (predeterminado 4569).
- delayreject: Cuando se establece en yes, retrasa el envío de un rechazo de autenticación para un REGREQ o AUTHREQ, lo que mejora la seguridad contra ataques de fuerza bruta a contraseñas.
- bandwidth: Cuando se establece en high, permite la selección de códecs de gran ancho de banda, como el g711 en sus variantes ulaw y alaw.

A continuación se muestra un ejemplo de la sección [general] del archivo iax.conf.

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### Clientes IAX

Después de terminar las secciones generales, es momento de configurar los clientes IAX.

- `[name]`: El nombre de la sección es el nombre del peer/usuario IAX; una conexión IAX entrante se empareja con él por nombre.
- `type`: La clase de conexión — `peer`, `user`, o `friend`:
  - `peer`: Asterisk envía llamadas a un peer.
  - `user`: Asterisk recibe llamadas de un usuario.
  - `friend`: ambas direcciones a la vez.
- `host`: Dirección IP o nombre de host. El valor más común es `dynamic`, usado cuando el dispositivo se registra en Asterisk.
- `secret`: Contraseña para autenticar peers y usuarios.

Advertencia: Use contraseñas seguras con al menos 8 caracteres, combinando letras y números, y al menos un símbolo. Han aparecido informes de servidores hackeados en las listas de correo, y existen crackers de fuerza bruta para hashes md5 de IAX disponibles para script kiddies. El fraude de tarifas cuesta miles de dólares a consumidores y proveedores. Ejemplo:

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Configurando los dispositivos SIP

Después de definir los teléfonos en el archivo de configuración de Asterisk, es hora de configurar el propio teléfono. En este ejemplo, mostraremos cómo configurar un softphone gratuito — el SipPulse Softphone (descárguelo desde https://www.sippulse.com/produtos/softphone). Consulte el manual de su dispositivo para entender los parámetros de su teléfono. Paso 1: Configure el teléfono para usar la extensión 6000. Ejecute el programa de instalación. Después de la ejecución, abra la configuración de cuenta/SIP y añada una nueva cuenta SIP. Complete la información requerida.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Confirme que su teléfono está registrado usando el comando de consola `pjsip show endpoints` (o `pjsip show endpoint 6000` para detalle; `pjsip show contacts` muestra los contactos AOR registrados). Repita la configuración para el teléfono 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## Configurando los dispositivos IAX

IAX2 es un protocolo heredado (ver el capítulo *Legacy channels*), y el Softphone SipPulse es solo SIP, por lo que no puede registrar una cuenta IAX. Si necesita probar IAX2, use un softphone que aún lo soporte. Cree una nueva cuenta IAX,

3. Seleccione nueva cuenta IAX.  
4. Inserte las opciones relacionadas para el teléfono 6003 y opcionalmente para el 6004.  
5. Guarde la configuración y verifique si el teléfono está registrado usando `iax2 show peers`.

Importante: Use una cuenta para SIP y otra para IAX. Si desea configurar el sistema para que suene tanto IAX como SIP al mismo tiempo, le mostraremos cómo hacerlo en la sección del dialplan.

### Configurando una interfaz PSTN

Para conectarse a la PSTN, necesitará una interfaz foreign exchange office (FXO) y una línea telefónica. También puede usar una extensión PBX existente. Puede obtener una tarjeta de interfaz telefónica con una interfaz FXO de varios fabricantes. En este ejemplo, le mostraremos cómo instalar una tarjeta de interfaz DAHDI.

![FXS and FXO ports: the FXS port drives an analog phone (supplies dial tone and ring), while the FXO port connects Asterisk to the Telco line.](../images/04-first-pbx-fig02.png)

### Líneas analógicas usando DAHDI

Puede comprar una tarjeta analógica compatible con DAHDI de varios fabricantes. X100P fue una de las primeras tarjetas Digium y ya había sido descontinuada. Algunos fabricantes aún producen clones similares. Además del precio de la X100P, hemos encontrado varios problemas entre estas tarjetas y nuevas placas madre, así que úsela con cuidado. X100P, en mi opinión, no es una buena elección para un entorno de producción. Cualquier tarjeta compatible con DAHDI debería funcionar. Gracias al equipo de desarrolladores de DAHDI, ahora contamos con una herramienta para detectar y configurar las tarjetas de interfaz casi automáticamente. Si acaba de instalar los controladores DAHDI, por favor no olvide ejecutar make config y reiniciar la máquina para cargarla automáticamente. Puede usar los comandos a continuación para detectar y configurar su tarjeta. Paso 1: Para detectar su hardware, use:

```
dahdi_hardware
```

Paso 2: Para configurar use:

```
dahdi_genconf
```

El comando anterior generará dos archivos /etc/dahdi/system.conf y /etc/asterisk/dahdi-channels.conf. Los parámetros predeterminados para dahdi_genconf suelen ser adecuados, pero puede modificarlos en el archivo /etc/dahdi/genconf_parameters. Por defecto, insertará las líneas (FXO) en el contexto from-pstn y los teléfonos (FXS) en el contexto from-internal. Paso 3: Después de ejecutar dahdi_genconf, en la última línea del archivo /etc/asterisk/chan_dahdi.conf inserte la siguiente línea:

```
#include dahdi-channels.conf
```

Paso 4: Edite el archivo /etc/dahdi/modules y comente todos los controladores no utilizados. Reinicie antes de continuar y verifique si los canales están siendo reconocidos usando:

```
*CLI> dahdi show channels
```

### Conexión a la PSTN usando un proveedor VoIP

Si su presupuesto es realmente limitado, puede configurar un trunk SIP para conectarse a la PSTN. Es, sin duda, la forma más económica de conectar a la PSTN. Miles de proveedores VoIP existen en todo el mundo. Para conectarse a uno de ellos, necesitará algunos parámetros. Parámetros provistos por el proveedor SIP.

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

Dos parámetros deben ser determinados por usted.

- Extension to receive calls—in this case: 9999
- context: from-sip

In PJSIP, a registering SIP trunk is built from the same object family used for an endpoint, plus explicit `registration` and `identify` objects. The `registration` object tells Asterisk to register to the provider, the `identify` object matches inbound traffic from the provider's IP to the endpoint (PJSIP authenticates inbound INVITEs by source IP), and `outbound_auth` supplies the credentials for outbound calls and registration:

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=digest
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

Para acceder a este trunk, usaremos el nombre de canal `PJSIP/siptrunk`. La configuración `dtmf_mode=rfc4733` transporta DTMF fuera de banda (RFC 4733 reemplaza al RFC 2833 anterior; la carga útil es idéntica). La opción `identify`/`match` acepta direcciones IP, CIDR o nombres de host, pero los nombres de host se resuelven una sola vez al cargar la configuración, así que para un proveedor con IPs cambiantes liste explícitamente la(s) IP de señalización. Confirme el registro con `pjsip show registrations`.

## Introducción al plan de marcación

El plan de marcación es como el corazón de Asterisk. Define cómo Asterisk maneja cada llamada al PBX. Consiste en extensiones que forman una lista de instrucciones que Asterisk debe seguir. Las instrucciones se activan mediante los dígitos recibidos del canal o de la aplicación. Para configurar Asterisk con éxito, es crucial comprender el plan de marcación. La mayor parte del plan de marcación se encuentra en el archivo extensions.conf en el directorio /etc/asterisk. Este archivo usa la gramática simple de grupos y tiene cuatro conceptos principales:

- Extensions
- Priorities
- Applications
- Contexts

Creemos un plan de marcación básico. En secciones posteriores de este libro, dedicaré un capítulo exclusivamente al plan de marcación. Si instalaste los archivos de ejemplo (make samples), el archivo extensions.conf ya existe. Guárdalo con otro nombre y comienza con un archivo vacío.

## La estructura del archivo extensions.conf

El archivo extensions.conf está dividido en secciones. La primera es la sección [general] seguida por la sección [globals]. El comienzo de cada sección inicia con la definición de su nombre (p.ej., [default]) y termina cuando se crea otra sección.

### La sección [general]

La sección general se encuentra al inicio del archivo. Antes de comenzar a configurar el plan de marcación, es útil conocer las opciones generales que controlan ciertos comportamientos del plan de marcación. Estas opciones son:

- static and write protect: Si `static=yes` y `writeprotect=no`, puedes guardar el plan de marcación en ejecución de nuevo en el disco con el comando CLI:

```
*CLI> dialplan save
```

Advertencia: Si ejecutas un comando `dialplan save` desde la CLI, perderás cualquier observación y comentario en el archivo.

- autofallthrough: Si autofallthrough está configurado, entonces si una extensión se queda sin acciones que ejecutar, terminará la llamada con BUSY, CONGESTION o HANGUP según la mejor suposición de Asterisk. Este es el valor predeterminado. Si autofallthrough no está configurado, entonces si una extensión se queda sin acciones, Asterisk esperará a que se marque una nueva extensión.
- clearglobalvars: Si clearglobalvars está configurado, las variables globales se borrarán y volverán a analizarse en una recarga del dialplan o una recarga de Asterisk. Si clearglobalvars no está configurado, las variables globales persistirán a través de recargas y—aunque se eliminen del extensions.conf o de uno de sus archivos incluidos—permanecerán con el valor anterior.
- extenpatternmatchnew: Utiliza un algoritmo de coincidencia de patrones más rápido, lo que ayuda notablemente cuando tienes un gran número de extensiones. Por defecto está desactivado.
- userscontext: Este es el contexto donde se registran las entradas de users.conf.

### La sección [globals]

En la sección [globals] definirás variables globales y sus valores iniciales. Puedes acceder a la variable en el plan de marcación usando ${GLOBAL(variable)}. Incluso puedes acceder a variables definidas en el entorno linux/unix usando ${ENV(variable)}. Las variables globales no distinguen entre mayúsculas y minúsculas. Algunos ejemplos podrían ser:

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

En el siguiente ejemplo, puedes establecer y probar una variable global en el plan de marcación.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contextos

El contexto es la partición nombrada del dialplan. Después de las secciones [general] y [globals], el dialplan es un conjunto de contextos en los que cada contexto tiene varias extensiones, cada extensión tiene varias prioridades, y cada prioridad llama a una aplicación con varios argumentos.

![Asterisk call flow: every call arrives on a channel (IAX, SIP, and others) as an incoming call leg; the channel's context — set globally or per-channel in the channel config file — decides which context in extensions.conf processes the call before it leaves on the outgoing leg.](../images/04-first-pbx-fig03.png)

![Call processing: the `context=` defined for a channel (in chan_dahdi.conf or pjsip.conf) names the matching context in extensions.conf where the dial plan handles the call.](../images/04-first-pbx-fig04.png)

Puedes crear un dialplan sencillo para alcanzar otros teléfonos y la PSTN. Sin embargo, Asterisk es mucho más potente que eso. Nuestro objetivo es enseñarte más detalles de lo que es posible en el dialplan.

## Extensiones

A diferencia del PBX tradicional, donde las extensiones están asociadas a teléfonos, interfaces, menús, etc., en Asterisk una extensión es una lista de comandos que se procesan cuando se activa un número o nombre de extensión específico. Los comandos se procesan en orden de prioridad.

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

Una extensión puede ser literal, estándar o especial. Una extensión estándar incluye solo números o nombres y los caracteres * y #; 12#89* es una extensión literal válida. También se pueden usar nombres para la coincidencia de extensiones. Las extensiones distinguen entre mayúsculas y minúsculas. Sin embargo, no se pueden crear dos extensiones con el mismo nombre pero con diferentes mayúsculas/minúsculas. Cuando se marca una extensión, se ejecuta el comando con la primera prioridad, seguido del comando con prioridad 2 y así sucesivamente. Esto ocurre hasta que la llamada se desconecta o algún comando devuelve el número uno, indicando fallo. Lo que Asterisk hace cuando se ejecuta la última prioridad está regulado por el parámetro autofallthrough. Ver la sección [general] en este capítulo. Ejemplo:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Arriba encontrará la lista de instrucciones que se procesan cuando se marca la extensión 123. La primera prioridad es responder el canal (necesario cuando el canal está en estado de timbre: p. ej., canales FXO). La segunda prioridad es reproducir un archivo de audio llamado tt-weasels. La tercera prioridad cuelga el canal. Otra opción es manejar la llamada según el ID de quien llama. Puede usar el carácter / para especificar el ID de quien llama que se procesará. Ejemplos:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Este ejemplo activará la extensión 123 y ejecutará las siguientes opciones solo si el ID de quien llama es 100. Esto también puede hacerse usando el patrón descrito a continuación:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: asigna una extensión a un canal. Se usa para monitorear el estado del canal. Se utiliza en conjunto con presencia. El teléfono debe ser compatible.

#### Patrones

Puede usar patrones y literales en el plan de marcación. Los patrones son muy útiles para reducir el tamaño del plan de marcación. Todos los patrones comienzan con el carácter “_”. Los siguientes caracteres pueden usarse para definir un patrón. La figura identifica los patrones disponibles para usar con Asterisk.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Extensiones especiales

Asterisk usa algunos nombres de extensión como extensiones estándar.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

Descripción:

- **s**: Start. Se usa para manejar una llamada cuando no hay número marcado. Es útil para trunks FXO y para procesamiento en menús.
- **t**: Timeout. Se usa cuando las llamadas permanecen inactivas después de reproducir un mensaje. También se usa para colgar una línea inactiva.
- **T**: AbsoluteTimeout. Si establece un límite de llamadas usando la función de dialplan `TIMEOUT(absolute)`, una vez que la llamada supera el límite definido, se enviará a la extensión T.
- **h**: Hangup. Se llama después de que el usuario desconecta la llamada.
- **i**: Invalid. Se activa cuando se llama a una extensión inexistente en el contexto. Usar estas extensiones puede afectar el contenido de los registros CDR—específicamente, el campo dst que no contiene el número marcado.
- **o**: Operator. Se usa para ir al operador cuando el usuario presiona “0” durante el

## Variables

En el PBX Asterisk, las variables pueden ser globales, específicas de canal y específicas del entorno. Puedes usar la aplicación NoOP() para ver el contenido de una variable en la consola. Puede usar una variable global o una variable específica de canal como argumentos de la aplicación. Una variable puede ser referenciada como en el siguiente ejemplo, donde varname es el nombre de la variable.

```
${varname}
```

El nombre de una variable puede ser una cadena alfanumérica que comience con una letra. Los nombres de variables globales no distinguen entre mayúsculas y minúsculas. Sin embargo, las variables del sistema (definidas por Asterisk y por el canal) sí distinguen entre mayúsculas y minúsculas. Así, la variable ${EXTEN} es diferente de ${exten}.

### Global variables

Las variables globales pueden configurarse en la sección [global] del archivo extensions.conf o usando la aplicación:

```
set(Global(variable)=content)
```

### Channel-specific variables

Las variables específicas de canal se configuran usando la aplicación set(). Cada canal recibe su propio espacio de variables. No hay posibilidad de colisiones entre variables de diferentes canales. Una variable específica de canal se destruye cuando el canal cuelga. Algunas de las variables más usadas son:

- ${EXTEN} Extensión marcada
- ${CONTEXT} Contexto actual
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} ID de llamante actual
- ${PRIORITY} Prioridad actual

Otras variables específicas de canal están en mayúsculas. Puedes ver el contenido de varias variables usando la aplicación dumpchan(). A continuación se muestra un extracto sencillo de variables de dump-channel.

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Salida de Dumpchan:

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

El diseño de campos anterior es la salida de Asterisk 22 `DumpChan` (un nombre de canal real `PJSIP/...`, los campos `CallerIDNum`/`ConnectedLineID` y las filas `Raw*`/`Transcode`/`BridgeID` que los canales PJSIP rellenan). A diferencia del controlador antiguo, un canal PJSIP no establece automáticamente las variables de canal `SIPCALLID`/`SIPUSERAGENT`; los detalles equivalentes de SIP se leen bajo demanda con las funciones de dialplan `PJSIP_HEADER()` y `CHANNEL()` — por ejemplo `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` y `${CHANNEL(rtp,dest)}` para la dirección RTP remota.

### Environment-specific variables

Las variables específicas del entorno pueden usarse para acceder a variables definidas en el sistema operativo. Puedes establecer variables específicas del entorno usando la función ENV(). Por ejemplo:

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

Algunas aplicaciones usan variables para la entrada y salida de datos. Puedes establecer variables antes de llamar a la aplicación o recuperar la variable después de la ejecución de la aplicación. Por ejemplo: la aplicación Dial devuelve las siguientes variables:

- ${DIALEDTIME} ->Este es el tiempo desde marcar un canal hasta que se desconecta.
- ${ANSWEREDTIME} -> Este es el tiempo de la llamada real.
- ${DIALSTATUS} Este es el estado de la llamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Mensaje de error para la llamada.

## Expresiones

Las expresiones pueden ser muy útiles en el plan de marcación. Se usan para manipular cadenas y realizar operaciones matemáticas y lógicas.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

La sintaxis de la expresión se define de la siguiente manera:

```
$[expression1 operator expression2]
```

Supongamos que tenemos una variable llamada “I” y queremos añadir 100 a la variable:

```
$[${I}+100]
```

Cuando Asterisk encuentra una expresión en el plan de marcación, cambia toda la expresión por el valor resultante.

### Operadores

Los siguientes operadores pueden usarse para construir expresiones. Es importante observar la precedencia de los operadores.

1. Paréntesis “()”
2. Operadores unarios “! -“
3. Expresión regular “: =~
4. Operadores multiplicativos “* / %”
5. Operadores aditivos “+ -“
6. Operadores de comparación
7. Operadores lógicos
8. Operadores condicionales

#### Operadores matemáticos

- Suma (+)
- Resta (-)
- Multiplicación (*)
- División (/)
- Módulo (%)

#### Operadores lógicos

- AND lógico (&)
- OR lógico (|)
- Complemento lógico unario (!)

#### Operadores de expresión regular

- Coincidencia de expresión regular (:)
- Coincidencia exacta de expresión regular (=~)

Una expresión regular es una cadena de texto especial usada para describir un patrón de búsqueda. Puedes pensar en las expresiones regulares como comodines. Las expresiones regulares se usan para comparar una cadena con un patrón y verificar la coincidencia. Si la coincidencia tiene éxito y la expresión regular contiene al menos una coincidencia, se devuelve la primera coincidencia; de lo contrario, el resultado es el número de caracteres coincidentes.

#### Operadores de comparación

El resultado de una comparación es 1 si la relación es verdadera o 0 si es falsa.

- = igual
- != no igual
- < menor que
- > mayor que
- <= menor o igual que
- >= mayor o igual que

### LAB. Evalúe las siguientes expresiones:

Ponga estas expresiones en su plan de marcación y use la aplicación NoOP() para evaluar las expresiones. Marque 9002 y examine los resultados en la consola de Asterisk. Use verbose 15 para mostrar los resultados.

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## Functions

Algunas aplicaciones han sido reemplazadas por funciones, que permiten el procesamiento de variables de una manera más avanzada que solo con expresiones. Puedes ver la lista completa de funciones ejecutando el siguiente comando en la consola:

```
*CLI> core show functions
```

Longitud de cadena: ${LEN(string)} devuelve la longitud de la cadena

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

En la primera operación, el sistema muestra 5 como resultado (el número de letras en la palabra “fruit”). La segunda devuelve el número 4 (el número de letras en la palabra “pear”). Subcadenas: Devuelve la subcadena, comenzando desde la posición definida por el parámetro “offset”, con la longitud de cadena definida en el parámetro “length”. Si el offset es negativo, comienza de derecha a izquierda, empezando al final de la cadena. Si la longitud se omite o es negativa, toma toda la cadena a partir del offset.

```
${string:offset:length }
```

Ejemplo #1: Varias subcadenas

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Ejemplo #2: Obtén el código de área de los tres primeros dígitos.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Ejemplo #3: Toma todos los dígitos de la variable ${EXTEN}, excepto el código de área.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Concatenación de cadenas

Para concatenar dos cadenas, simplemente escríbelas juntas.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Aplicaciones

Para construir un plan de marcación, necesitamos comprender el concepto de aplicaciones. Utilizará aplicaciones para manejar el canal en el plan de marcación. Las aplicaciones están implementadas en varios módulos. Las aplicaciones disponibles dependen de los módulos. Puede mostrar todas las aplicaciones de Asterisk usando el comando de consola:

```
*CLI> core show applications
```

Alternativamente, puede mostrar los detalles de una aplicación específica usando el siguiente ejemplo:

```
*CLI> core show application Dial
```

Para construir un plan de marcación simple, necesitas conocer algunas aplicaciones. Discutiremos ejemplos más avanzados más adelante en el libro.

![The handful of applications needed to build a simple dial plan: Answer (answer a channel), Dial (call another channel), Hangup (hang up a channel), Playback (play an audio file), and Goto (jump to a priority, extension, or context).](../images/04-first-pbx-fig09.png)

Usaremos estas aplicaciones (arriba) para crear un plan de marcación simple para dos PBX básicos.

### Answer()

[Synopsis] Responde a un canal si está sonando [Description] Answer([delay]): Si la llamada no ha sido contestada, la aplicación la contestará. De lo contrario, no tiene efecto sobre la llamada. Si se especifica un retardo, Asterisk esperará la cantidad de milisegundos indicada en ‘delay’ antes de contestar la llamada.

### Dial()

La siguiente descripción se puede obtener ejecutando `show application dial` en el plan de marcación. Para una búsqueda fácil, se reproduce a continuación. La sintaxis de la aplicación Dial también se muestra a continuación:

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

Esta aplicación realizará llamadas a uno o más canales especificados. Tan pronto como uno de los canales solicitados conteste, el canal originador será contestado—si aún no lo ha sido. Estos dos canales estarán entonces activos en una llamada puenteada. Todos los demás canales solicitados serán colgados. A menos que se especifique un tiempo de espera, la aplicación Dial esperará indefinidamente hasta que uno de los canales llamados conteste, el usuario cuelgue, o todos los canales llamados estén ocupados o no disponibles. La ejecución del dialplan continuará si no se pueden llamar los canales solicitados o si expira el tiempo de espera. Esta aplicación establece las siguientes variables de canal al completarse:

- DIALEDTIME - Este es el tiempo desde que se marca un canal hasta que se desconecta.
- ANSWEREDTIME - Esta es la duración de la llamada real.
- DIALSTATUS - Este es el estado de la llamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

Para los modos de Privacidad y Filtrado, la variable DIALSTATUS se establecerá en DONTCALL si la parte llamada elige enviar a la parte llamante al script 'Go Away'. La variable DIALSTATUS se establecerá en TORTURE si la parte llamada desea enviar al llamante al script 'torture'. Esta aplicación informará una terminación normal si el canal originador cuelga o si la llamada está puenteada y cualquiera de las partes en el puente finaliza la llamada. La URL opcional será enviada a la parte llamada si el canal la soporta. Si la variable OUTBOUND_GROUP está establecida, todos los canales pares creados por esta aplicación se incluirán en ese grupo (como en

```
Set(GROUP()=...).
```

La siguiente tabla resume algunas de las opciones más usadas para la aplicación Dial. Para la lista completa, use el comando de consola `core show application Dial`. En Asterisk 22 estas opciones se separan del canal y del tiempo de espera con comas — por ejemplo `Dial(PJSIP/2000,20,tTm)`.

| Option | Description |
|--------|-------------|
| `A(x)` | Reproduce un anuncio a la parte llamada, usando `x` como archivo. |
| `C` | Restablece el CDR para esta llamada. |
| `d` | Permite al usuario que llama marcar una extensión de 1 dígito mientras espera que la llamada sea contestada. Sale a esa extensión si existe en el contexto actual, o al contexto definido en la variable `EXITCONTEXT`, si existe. |
| `D([called][:calling])` | Envía las cadenas DTMF especificadas después de que la parte llamada conteste, pero antes de que la llamada sea puenteada. La cadena `called` se envía a la parte llamada y la cadena `calling` a la parte que llama. Cualquiera de los parámetros puede usarse solo. |
| `f` | Fuerza que la identificación de llamada del canal que llama se establezca a la extensión asociada al canal mediante un dial plan `hint`. Útil cuando la PSTN no permite una identificación de llamada arbitraria. |
| `g` | Continúa la ejecución del dial plan en la extensión actual si el canal de destino cuelga. |
| `G(context^exten^pri)` | Si la llamada es contestada, transfiere a la parte que llama a la prioridad especificada y a la parte llamada a prioridad+1. Opcionalmente se puede especificar una extensión (o extensión y contexto); de lo contrario se usa la extensión actual. |
| `h` | Permite a la parte llamada colgar enviando el dígito DTMF `*`. |
| `H` | Permite a la parte que llama colgar enviando el dígito DTMF `*`. |
| `L(x[:y][:z])` | Limita la llamada a `x` ms, reproduce una advertencia cuando quedan `y` ms, y repite la advertencia cada `z` ms. Vea las variables `LIMIT_*` a continuación. |
| `m([class])` | Proporciona música en espera a la parte que llama hasta que el canal solicitado conteste. Se puede especificar una clase MusicOnHold específica. |
| `r` | Indica timbre a la parte que llama y no pasa audio hasta que el canal llamado conteste. |
| `S(x)` | Cuelga la llamada `x` segundos después de que la parte llamada conteste. |
| `t` | Permite a la parte llamada transferir a la parte que llama enviando la secuencia DTMF definida en `features.conf`. |
| `T` | Permite a la parte que llama transferir a la parte llamada enviando la secuencia DTMF definida en `features.conf`. |
| `w` | Permite a la parte llamada habilitar la grabación con un toque enviando la secuencia DTMF definida en `features.conf`. |
| `W` | Permite a la parte que llama habilitar la grabación con un toque enviando la secuencia DTMF definida en `features.conf`. |
| `k` | Permite a la parte llamada estacionar la llamada enviando la secuencia DTMF definida para estacionamiento de llamadas en `features.conf`. |
| `K` | Permite a la parte que llama estacionar la llamada enviando la secuencia DTMF definida para estacionamiento de llamadas en `features.conf`. |

La opción `L(x[:y][:z])` puede ajustarse con las siguientes variables especiales:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (predeterminado `yes`): reproduce sonidos para el llamante.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: reproduce sonidos para la parte llamada.
- `LIMIT_TIMEOUT_FILE` — archivo a reproducir cuando el tiempo se agota.
- `LIMIT_CONNECT_FILE` — archivo a reproducir cuando la llamada comienza.
- `LIMIT_WARNING_FILE` — archivo a reproducir como advertencia cuando `y` está definido. El valor predeterminado es anunciar el tiempo restante.

Ejemplo:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

En el ejemplo anterior, la aplicación marcará el canal PJSIP correspondiente. Tanto el llamante como el llamado pueden transferir la llamada (Tt). Se escuchará música en espera en lugar de tono de regreso. Si nadie contesta dentro de 20 segundos, la extensión pasará a la siguiente prioridad.

### Hangup()

Cuelga el canal que llama [Description] Hangup([causecode]): Esta aplicación colgará el canal que llama. Si se proporciona un código de causa, la causa de colgado del canal se establecerá al valor dado.

### Goto()

Salta a una prioridad, extensión o contexto particular [Description] Goto([[context|]extension|]priority): Esta aplicación hará que el canal que llama continúe la ejecución del dialplan en la prioridad especificada. Si no se especifica una extensión concreta (o extensión y contexto), esta aplicación saltará a la prioridad especificada de la extensión actual. Si el intento de saltar a otra ubicación en el dialplan no tiene éxito, el canal continuará en la siguiente prioridad de la extensión actual.

## Construyendo un plan de marcación

Para construir un plan de marcación sencillo, necesita manejar todas las llamadas entrantes y salientes creando contextos y extensiones. En esta sección, le mostraremos cómo crear las extensiones más comunes.

### Marcación entre extensiones

Para habilitar la marcación entre extensiones, podríamos usar la variable de canal ${EXTEN}, que se refiere a la extensión marcada. Por ejemplo, si el rango de extensiones está entre 4000 y 4999 y todas las extensiones usan SIP, podríamos adoptar el siguiente comando:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Marcando a un destino externo

Para marcar un destino externo podrías preceder el número marcado con una ruta. En Norteamérica, es común usar 9 seguido del número que se marcará externamente. Si estás usando un canal analógico o digital hacia la PSTN, el comando debería verse como sigue: Si deseas usar el trunk SIP en lugar del DAHDI, usa el canal `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

La línea anterior le permitirá marcar 9 y el número deseado. En el ejemplo dado, usará el primer canal DAHDI (DAHDI/1). Si tiene varias líneas y esta está ocupada, la llamada no se completará. Sin embargo, podría usar la siguiente línea para elegir automáticamente el primer canal DAHDI disponible. Opcionalmente, puede usar el trunk SIP en lugar de DAHDI. En el formulario PJSIP `Dial(PJSIP/number@siptrunk,...)`, el número marcado es la parte de usuario y `siptrunk` es el endpoint configurado arriba.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

El parámetro “g1” buscará el primer canal disponible en el grupo, permitiendo el uso de todos los canales. Usando la línea a continuación, podrías marcar un número de larga distancia.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Marcando 9 para obtener una línea PSTN

Si no tiene ninguna restricción para marcar externamente, podría simplificar y usar lo siguiente:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Recibiendo una llamada en la extensión del operador

En el siguiente ejemplo, la extensión del operador es 4000. La línea PSTN está conectada a una interfaz FXO. En el archivo chan_dahdi.conf, el contexto especificado es from-pstn. Cualquier llamada proveniente de la PSTN será enrutada al contexto from-pstn en el dialplan. Esta línea no tiene marcación directa entrante (DID); por lo tanto, tendremos que recibir la llamada mediante la extensión “s”. Si se recibe desde el trunk SIP, use el contexto [from-sip].

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### Recibiendo una llamada usando marcación directa entrante (DID)

Si tiene una línea digital, recibirá la extensión marcada. Cuando este sea el caso, no necesita reenviar la llamada al operador; más bien, puede reenviar la llamada directamente al destino. Suponga que su rango de DID es de 3028550 a 3028599 y los últimos cuatro números se pasan en el DID. La configuración tendría el siguiente aspecto:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Reproduciendo varias extensiones simultáneamente

Puede configurar Asterisk para marcar una extensión y, si no es contestada, marcar varias otras extensiones simultáneamente, como se indica en el siguiente ejemplo:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

En este ejemplo, cuando alguien marca el operador, el canal DAHDI/1 se intenta inicialmente. Si nadie contesta después de 15 segundos (timeout), los canales DAHDI/1, DAHDI/2 y DAHDI/3 sonarán simultáneamente durante otros 15 segundos.

### Enrutamiento por ID de Llamante

En este ejemplo, podrías aplicar diferentes tratamientos según el ID de llamante, lo que podría ser útil para spammers de llamadas. Por ejemplo:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

En este ejemplo, hemos añadido una regla especial que, si el ID de llamada es 4832518888, reproduce un mensaje del archivo previamente grabado “I-have-moved-to-china”. Las demás llamadas se aceptan como de costumbre.

### Uso de variables en el dialplan

Asterisk puede usar variables globales y de canal en el dialplan como argumentos para ciertas aplicaciones. Observe los siguientes ejemplos:

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

Usar variables facilita los cambios futuros. Si cambias la variable, todas las referencias se actualizan de inmediato.

### Grabación de un anuncio

En algunas de las opciones que se discutirán más adelante en esta sección, utilizaremos avisos grabados. Aquí te mostramos una forma sencilla de grabarlos. Usaremos la aplicación Record() para guardar el anuncio con el propio teléfono.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Estas instrucciones le permiten grabar cualquier mensaje desde un softphone. Ejemplo: marcar recordmenu desde el softphone Las instrucciones llamarán a la grabación con la variable ${EXTEN:6} sin las primeras seis letras. En otras palabras, la instrucción es equivalente a record(menu:gsm). Todo lo que tiene que hacer es marcar record + nombre_del_archivo_a_grabar, presionar # para terminar la grabación y esperar a escuchar la grabación.

### Recepción de llamadas en una recepcionista digital

Ahora que tenemos algunos ejemplos simples, expandamos nuestro aprendizaje sobre las aplicaciones background() y goto(). La clave para los sistemas interactivos en Asterisk es la aplicación background(), que le permite ejecutar un archivo de audio que, cuando el llamante presiona una tecla, se interrumpe para enviar la llamada a la extensión marcada. Sintaxis de la aplicación background():

```
exten=>extension, priority, background(filename)
```

Another application very useful is goto(). As the name implies, it jumps to the context, extension, and priority indicated. Syntax of the application goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Formatos válidos para el comando goto():

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

En el siguiente ejemplo, crearemos una recepcionista digital. Es muy sencillo editar el archivo extensions.conf y configurar las siguientes extensiones:

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

Las extensiones SIP usan `PJSIP/` y las extensiones IAX usan `IAX2/` — ambos controladores se incluyen en Asterisk 22, aunque `chan_iax2` ahora se considera heredado y se prefiere SIP/PJSIP.

En el archivo menu1.gsm, grabe el mensaje “presione la extensión o espere al operador”. Cuando el usuario marque el número 6000, será enviado a la extensión 6000. En este punto, debe tener una comprensión clara del uso de varias aplicaciones, incluyendo answer(), background(), goto(), hangup() y playback(). Si no tiene una comprensión clara, lea este capítulo nuevamente hasta que se sienta cómodo con el contenido. Usará la aplicación background con mucha frecuencia. Una vez que entienda los conceptos básicos de extensiones, prioridades y aplicaciones, será fácil crear un plan de marcación simple. Estos conceptos se explorarán con mayor profundidad más adelante en el libro, y verá que el plan de marcación se volverá más potente.

## Resumen

En este capítulo, has aprendido que los archivos de configuración se almacenan en el directorio /etc/asterisk. Para usar Asterisk, primero es necesario configurar los canales (p. ej., pjsip, dahdi, iax). Existen tres gramáticas diferentes para los archivos de configuración: grupo simple, herencia de objetos y entidad compleja. El plan de marcación se crea en el archivo extensions.conf y es un conjunto de contextos y extensiones. En el plan de marcación, cada extensión activa una aplicación. Has aprendido a usar las aplicaciones playback, background, dial, goto, hangup y answer.

## Quiz

1. Los archivos de configuración del canal son (elija todas las que correspondan):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. En Asterisk 22, el único par `chan_sip` `[6001]` (`type=friend`/`host=dynamic`) es reemplazado en `pjsip.conf` por cuál conjunto de objetos relacionados?
   - A. Un `type=peer` y un `type=user`
   - B. Un `type=endpoint`, un `type=auth` y un `type=aor`
   - C. Un único `type=friend`
   - D. Un `type=transport` y un `type=global`
3. Definir un contexto en el archivo de configuración del canal importa porque establece el contexto de entrada para llamadas desde ese canal — una llamada desde el canal se procesa en el contexto coincidente en `extensions.conf`.
   - A. Verdadero
   - B. Falso
4. Las principales diferencias entre las aplicaciones `Playback()` y `Background()` son (elija dos):
   - A. Playback reproduce un mensaje pero no espera dígitos.
   - B. Background reproduce un mensaje pero no espera dígitos.
   - C. Background reproduce un mensaje y espera a que se marquen dígitos.
   - D. Playback reproduce un mensaje y espera a que se marquen dígitos.
5. Cuando una llamada entra a Asterisk a través de una tarjeta de interfaz telefónica (FXO) sin DID, se maneja en la extensión especial:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Los formatos válidos para la aplicación `Goto()` son (elija tres):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. El patrón `_7[1-5]XX` coincide (elija todas las que correspondan):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. En `Dial(PJSIP/${EXTEN},20,tTm)`, ¿qué hace la opción `m`?
   - A. Limita la llamada a una duración máxima.
   - B. Proporciona música en espera al llamante en lugar de tono de marcación hasta que el canal conteste.
   - C. Envía dígitos DTMF después de que la parte llamada conteste.
   - D. Fuerza el identificador de llamante usando una pista del dialplan.
9. En la gramática de herencia de opciones usada por `chan_dahdi.conf`, usted:
   - A. Define el objeto en una sola línea.
   - B. Define opciones primero y declara los objetos bajo las opciones definidas.
   - C. Define un contexto separado para cada objeto.
10. Las prioridades en una extensión deben numerarse consecutivamente (1, 2, 3, …) y no pueden usar `n`.
    - A. Verdadero
    - B. Falso

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
