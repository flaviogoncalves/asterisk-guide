# Construyendo su primer PBX con PJSIP

En este capítulo, aprenderá a realizar una configuración básica de un PBX Asterisk. El objetivo principal aquí es ver el PBX funcionando por primera vez, ser capaz de marcar entre extensiones, marcar un mensaje que se está reproduciendo y marcar a un único trunk analógico o SIP. La idea detrás de este capítulo es asegurar que su Asterisk esté en funcionamiento lo antes posible. Después de completar el trabajo en este capítulo, tendrá suficiente base para prepararse para los capítulos siguientes, donde profundizaremos más en los detalles de configuración.

## Objetivos

Al final de este capítulo, debería ser capaz de:

- Entender y editar archivos de configuración;
- Instalar softphones basados en SIP;
- Instalar y configurar un trunk SIP;
- Instalar y configurar una conexión analógica;
- Marcar entre extensiones;
- Marcar entre teléfonos y destinos externos; y
- Configurar un contestador automático (auto attendant).

## Entendiendo los archivos de configuración

Asterisk es controlado por archivos de configuración de texto ubicados en /etc/asterisk. El formato del archivo es similar a los archivos “.ini” de Windows. Se utiliza un punto y coma como carácter de comentario, los signos “=” y “=>” son equivalentes, y los espacios son ignorados.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interpreta “=” y “=>” de la misma manera. Las diferencias en la sintaxis se utilizan para distinguir entre objetos y variables. Use “=” cuando quiera declarar una variable y “=>” para designar un objeto. La sintaxis es la misma entre todos los archivos, pero se utilizan tres tipos de gramática, como se discute a continuación.

## Gramáticas

| Gramática | Cómo se crea el objeto | Archivo conf. | Ejemplo |
|---------|---------------------------|------------|---------|
| Grupo Simple | Todo en la misma línea | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Herencia de Opciones | Las opciones se definen primero, el objeto hereda las opciones | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Entidad Compleja | Cada entidad recibe un context | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Grupo Simple

El formato de grupo simple utilizado en extensions.conf, meetme.conf y voicemail.conf es la gramática más básica. Cada objeto se declara con opciones en la misma línea. Ejemplo:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

En este ejemplo, el objeto 1 se crea con las opciones op1, op2 y op3, mientras que el objeto 2 se crea con las opciones op1, op2 y op3.

### Gramática de herencia de opciones de objeto

Este formato es utilizado por los archivos chan_dahdi.conf y agents.conf, donde hay numerosas opciones disponibles, y la mayoría de las interfaces y objetos comparten las mismas opciones. Típicamente, una o más secciones tienen declaraciones de objetos y canales. Las opciones para el objeto se declaran sobre el objeto y pueden cambiarse para otro objeto. Aunque este concepto es difícil de entender, es muy fácil de usar. Ejemplo:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

Las dos primeras líneas configuran el valor de las opciones op1 y op2 a “bas” y “adv”, respectivamente. Cuando se instancia el objeto 1, se crea usando la opción 1 como “bas” y la opción 2 como “adv”. Después de definir el objeto 1, cambiamos la opción 1 a “int”. A continuación, creamos el objeto 2 con la opción 1 como “int” y la opción 2 como “adv”.

### Objeto de entidad compleja

Este formato es utilizado por pjsip.conf, iax.conf y otros archivos de configuración en los que existen numerosas entidades con muchas opciones. Típicamente, este formato no comparte un gran volumen de configuraciones comunes. Cada entidad recibe un context. A veces existen contextos reservados, como [general] para configuraciones globales. Las opciones se declaran en las declaraciones de contexto. Ejemplo:

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

Para configurar un PBX, necesitará algo de hardware básico. No es difícil ni costoso, pero hay algunas opciones a considerar. Todo lo que necesitará son dos teléfonos y una conexión a la red pública. Existen algunas opciones y combinaciones posibles al crear su laboratorio, las cuales discutiremos a continuación.

### Opción 1: LAB completo

Con el LAB completo, es posible probar todos los escenarios disponibles y comparar soluciones como ATA, teléfonos IP y softphones. También puede aprender sobre trunks analógicos y SIP. Necesitará:

- Un adaptador de teléfono analógico (ATA) SIP
- Un teléfono IP
- Un servidor dedicado para Asterisk
- Una estación de trabajo con un softphone
- Una tarjeta de interfaz analógica con al menos dos interfaces (1 FXO y 1 FXS)
- Una cuenta de proveedor VoIP

### Opción 2: LAB económico

Con el LAB económico, lo simplificamos un poco. Usamos el ATA, que suele ser menos costoso que el teléfono IP, y una única tarjeta FXO, que es realmente económica. No podremos usar teléfonos analógicos conectados directamente al servidor, pero esto no ocurre comúnmente en la práctica. Necesitará:

- Un adaptador de teléfono analógico (ATA) SIP
- Un servidor dedicado para Asterisk
- Una estación de trabajo para el softphone
- Una tarjeta de interfaz analógica con 1 FXO
- Una cuenta con un proveedor VoIP

### Opción 3: Laboratorio súper económico

El tercer LAB utiliza un servidor virtualizado en la propia computadora portátil del estudiante. El problema con este modelo son los conflictos generados por el puerto UDP. A veces, tanto el servidor Asterisk como el softphone intentan acceder al mismo puerto, evitando que Asterisk vincule el puerto de dirección. Otro problema es la calidad de las llamadas; los entornos virtuales no están indicados para aplicaciones en tiempo real como Asterisk. Use un softphone gratuito para el servidor y la estación de trabajo y una conexión de trunk a un proveedor SIP. Necesitará:

- Una computadora portátil ejecutando un softphone
- Una máquina virtual (VirtualBox, VMware o similar) para instalar Asterisk
- Una cuenta con un proveedor VoIP

## Secuencia de instalación

Para ayudarle a entender la secuencia de instalación, describimos la secuencia de pasos necesarios para instalar y configurar Asterisk.

![Diseño del laboratorio de referencia: softphones SIP/IAX, un teléfono IP y adaptadores analógicos como extensiones (1), el servidor Asterisk con interfaces ETH0/FXO/FXS (3), y los trunks a la PSTN a través de un proveedor VoIP o un enlace de banda ancha (2).](../images/04-first-pbx-fig01.png)

1. Configuración de extensiones a. Extensiones SIP (ATA, Softphone, Teléfono IP) b. Extensiones IAX c. Extensiones FXS 2. Configuración de trunks a. Configuración de un trunk SIP b. Configuración de un trunk FXO 3. Construcción de un dialplan básico a. Marcar entre extensiones b. Marcar destinos externos c. Recibir una llamada desde la extensión del operador d. Recibir una llamada en un contestador automático

## Configuración de las extensiones

Las extensiones son teléfonos SIP, IAX o analógicos conectados a un puerto FXS. Para configurar una extensión, debe editar el archivo de configuración relacionado con el canal (pjsip.conf, iax.conf, chan_dahdi.conf)

### Extensiones SIP

En Asterisk 22, PJSIP (la pila `res_pjsip`, configurada en `/etc/asterisk/pjsip.conf`) es el controlador de canal SIP. Soporta múltiples transportes por endpoint, se mantiene activamente y es el único controlador SIP enviado con la plataforma. (El controlador original `chan_sip` fue eliminado en Asterisk 21 — vea el capítulo *Legacy channels* si necesita migrar una configuración antigua.)

La idea aquí es configurar un PBX simple. (Los capítulos siguientes proporcionan una sesión completa de SIP/PJSIP con todos los detalles.) PJSIP se configura en `/etc/asterisk/pjsip.conf` y contiene todos los parámetros relacionados con teléfonos SIP y proveedores VoIP. Los clientes SIP deben configurarse antes de que pueda realizar y recibir llamadas.

#### El transporte

En PJSIP, la configuración del listener (dirección de enlace, puerto, protocolo) reside en un objeto `transport`. Asterisk tiene protección incorporada contra la adivinación de nombres de usuario: siempre devuelve un desafío de autenticación idéntico para usuarios desconocidos y conocidos, y las solicitudes no identificadas repetidas desde una IP están limitadas por tasa a través de las opciones `[global]` `unidentified_request_count`/`unidentified_request_period`. Las opciones principales de un transporte son:

- protocol: El protocolo de transporte — `udp`, `tcp`, `tls`, `ws` o `wss`.
- bind: Dirección y puerto a los que se vincula el listener. Si establece la dirección en `0.0.0.0`, se vincula a todas las interfaces; el puerto SIP es 5060 por defecto para UDP/TCP.

Un transporte UDP mínimo:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

La selección de codec (`disallow`/`allow`) y el `context` por defecto se configuran en cada `endpoint` (mostrado a continuación), no en el transporte. Las llamadas anónimas/invitadas son manejadas por un `endpoint` llamado `anonymous`. Los temporizadores de registro se controlan por AOR a través de `maximum_expiration`/`default_expiration`.

#### Clientes SIP

Después de completar la sección de transporte, es hora de configurar los clientes SIP. Me gustaría recordar una vez más al lector que tendremos un capítulo completo de SIP/PJSIP más adelante en el libro. Por ahora, concentrémonos en lo básico y dejemos los detalles para después.

En PJSIP, un cliente SIP se construye a partir de un conjunto de objetos relacionados, unidos por referencia de nombre:

- `endpoint`: El comportamiento de la llamada — codecs (`allow`/`disallow`), el dialplan `context`, y qué `auth` y `aors` utiliza.
- `auth`: Las credenciales. `username` es el usuario de autenticación SIP y `password` es el secreto utilizado para autenticar el dispositivo.
- `aor`: La "dirección de registro" (address of record) — dónde se puede alcanzar el endpoint. Ya sea un `contact=` estático (para un dispositivo en una IP fija) o `max_contacts=` para permitir que el dispositivo se registre dinámicamente.

Advertencia: Use contraseñas seguras, con al menos 8 caracteres, caracteres alfanuméricos y numéricos, y al menos un símbolo. Han aparecido informes de servidores hackeados en las listas de correo, y los crackers de contraseñas de fuerza bruta para SIP están fácilmente disponibles para los script kiddies. El fraude de llamadas cuesta miles de dólares a consumidores y proveedores.

El endpoint 6000 es un dispositivo en una IP fija, por lo que su AOR lleva un `contact` estático en lugar de permitir el registro. El endpoint 6001 es un dispositivo que se registra, por lo que su AOR le permite registrarse (`max_contacts=1`):

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
auth_type=userpass
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
auth_type=userpass
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP permite que las secciones `endpoint`, `auth` y `aor` compartan el mismo nombre de sección (por ejemplo, los dos bloques `[6001]` anteriores, distinguidos por su `type=`); muchos administradores en su lugar añaden un sufijo (`[6001]`, `[6001-auth]`, `[6001]` aor) para facilitar la lectura. Para un dispositivo que se registra, el contacto se aprende dinámicamente cuando el teléfono se registra, por lo que el AOR no necesita un `contact` estático.

## Extensiones IAX

`chan_iax2` todavía se envía en Asterisk 22 pero ahora es legado; SIP/PJSIP es el protocolo preferido para nuevas implementaciones.

También puede crear extensiones IAX. Este protocolo es nativo de Asterisk, y tendremos una sección completa dedicada a él más adelante en este libro. Por ahora, creemos algunas extensiones usando el protocolo. Como la primera sección a configurar, la sección [general] tiene ciertos parámetros a configurar. Las opciones principales son:

- allow/disallow: Define qué codecs se van a utilizar.
- bindaddr: Dirección a la que se vinculará el listener SIP de Asterisk. Si la configura como 0.0.0.0 (por defecto), se vinculará a todas las interfaces.
- context: Establece el contexto por defecto para todos los clientes a menos que se cambie en la sección del cliente. Usamos dummy por razones de seguridad. Los usuarios no autenticados entran en este contexto cuando la opción allowguest se establece en yes.
- bindport: Puerto UDP SIP para escuchar.
- delayreject: Cuando se establece en yes, retrasa el envío de un rechazo de autenticación para un REGREQ o AUTHREQ, lo que mejora la seguridad contra ataques de fuerza bruta de contraseñas.
- bandwidth: Cuando se establece en high, permite la selección de codecs de alto ancho de banda, como el g711 en sus variantes ulaw y alaw.

El siguiente es un ejemplo de la sección [general] del archivo iax.conf.

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

Después de terminar las secciones generales, es hora de configurar los clientes IAX.

- [name]: Cuando un dispositivo SIP se conecta a Asterisk, utiliza la parte del nombre de usuario del URI SIP para encontrar el peer/user.
- type: Configura la clase de conexión. Las opciones son peer, user y friend. o peer: Asterisk envía llamadas a un peer. o user: Asterisk recibe llamadas de un usuario. o friend: Ambos ocurren al mismo tiempo.
- host: Dirección IP o nombre de host. La opción más común es dynamic, que se utiliza cuando el host se registra en Asterisk.
- secret: Contraseña para autenticar peers y usuarios.

Advertencia: Use contraseñas seguras con al menos 8 caracteres, caracteres alfanuméricos y numéricos, y al menos un símbolo. Han aparecido informes de servidores hackeados en las listas de correo, y los crackers de contraseñas de fuerza bruta para hashes md5 de SIP están disponibles para los script kiddies. El fraude de llamadas cuesta miles de dólares a consumidores y proveedores. Ejemplo:

```
[guest]
type=user
context=dummy
callerid=”Guest IAX User”
[6003]
context=from-internal
type=friend
secret=#sup3rs3cr3t#
host=dynamic
context=from-internal
[6004]
context=from-internal
type=friend
secret=#s3cr3ts3cr3t#
host=dynamic
context=from-internal
```

## Configuración de los dispositivos SIP

Después de definir los teléfonos en el archivo de configuración de Asterisk, es hora de configurar el teléfono en sí. En este ejemplo, mostraremos cómo configurar un softphone gratuito. La 1ª edición usó X-Lite de CounterPath; ese producto ha sido descontinuado, así que use cualquier softphone SIP gratuito moderno (por ejemplo, Zoiper, Linphone o MicroSIP). Consulte el manual de su dispositivo para entender los parámetros de su teléfono. Paso 1: Configure el teléfono para usar la extensión 6000. Ejecute el programa de instalación. Después de la ejecución, abra la configuración de cuenta/SIP y agregue una nueva cuenta SIP. Complete la información requerida.

![La pantalla de cuenta del SipPulse Softphone — ingrese el Servidor (su IP o dominio de Asterisk), Nombre de usuario, Contraseña y Nombre para mostrar, luego elija el Transporte (UDP, TCP o TLS).](../images/softphone/sipphone-account.png){width=35%}

Nombre para mostrar: 6000  Nombre de usuario: 6000  Contraseña: #MySecret1#7  Nombre de usuario de autorización: 6000  Dominio: ip_de_su_servidor. Confirme que su teléfono esté registrado usando el comando de consola `pjsip show endpoints` (o `pjsip show endpoint 6000` para detalles; `pjsip show contacts` muestra los contactos AOR registrados). Repita la configuración para el teléfono 6001.

![Un SipPulse Softphone registrado — el punto verde y la línea de cuenta (`1001@softphone.sippulse.com.br`) confirman el registro; realice una llamada desde el teclado o los botones de llamada/video.](../images/softphone/sipphone-registered.png){width=35%}

## Configuración de los dispositivos IAX

IAX2 es un protocolo legado (vea el capítulo *Legacy channels*), y el SipPulse Softphone es solo SIP, por lo que no puede registrar una cuenta IAX. Si necesita probar IAX2, use un cliente que todavía lo soporte (por ejemplo, Zoiper, que históricamente ofrecía IAX). Cree una nueva cuenta IAX,

3. Seleccione nueva cuenta IAX. 4. Inserte las opciones relacionadas para el teléfono 6003 y opcionalmente para el 6004. 5. Guarde la configuración y verifique si el teléfono está registrado usando iax2 show peers. Importante: Use una cuenta para SIP y otra para IAX. Si desea configurar el sistema para que suenen tanto IAX como SIP al mismo tiempo, le mostraremos cómo hacerlo en la sección del dialplan.

### Configuración de una interfaz PSTN

Para conectarse a la PSTN, necesitará una interfaz de oficina de intercambio extranjero (FXO) y una línea telefónica. También puede usar una extensión de PBX existente. Puede obtener una tarjeta de interfaz de telefonía con una interfaz FXO de varios fabricantes. En este ejemplo, le mostraremos cómo instalar una tarjeta de interfaz DAHDI.

![Puertos FXS y FXO: el puerto FXS controla un teléfono analógico (suministra tono de marcado y timbre), mientras que el puerto FXO conecta Asterisk a la línea telefónica.](../images/04-first-pbx-fig02.png)

### Líneas analógicas usando DAHDI

Puede comprar una tarjeta analógica compatible con DAHDI de varios fabricantes. X100P fue una de las primeras tarjetas Digium y ya ha sido descontinuada. Algunos fabricantes todavía producen clones similares. Además del precio de la X100P, hemos encontrado varios problemas entre estas tarjetas y las nuevas placas base, así que úsela con cuidado. X100P, en mi opinión, no es una buena opción para un entorno de producción. Cualquier tarjeta compatible con DAHDI debería funcionar. Gracias al equipo de desarrolladores de DAHDI, ahora tenemos una herramienta para detectar y configurar las tarjetas de interfaz casi automáticamente. Si acaba de instalar los controladores DAHDI, por favor no olvide ejecutar make config y reiniciar la máquina para cargarlos automáticamente. Puede usar los comandos a continuación para detectar y configurar su tarjeta. Paso 1: Para detectar su hardware, use:

```
dahdi_hardware.
```

Paso 2: Para configurar use:

```
dahdi_genconf.
```

El comando anterior generará dos archivos /etc/dahdi/system.conf y /etc/asterisk/dahdi-channels.conf. Los parámetros por defecto para dahdi_genconf suelen estar bien, pero puede cambiarlos en el archivo /etc/dahdi/genconf_parameters. Por defecto, insertará las líneas (FXO) en el contexto from-pstn y los teléfonos (FXS) en el contexto from-internal. Paso 3: Después de ejecutar dahdi_genconf, en la última línea del archivo /etc/asterisk/chan_dahdi.conf inserte la siguiente línea:

```
#include dahdi-channels.conf
```

Paso 4: Edite el archivo /etc/dahdi/modules y comente todos los controladores no utilizados. Reinicie antes de proceder y verifique si los canales están siendo reconocidos usando:

```
CLI>dahdi show channels
```

### Conexión a la PSTN usando un proveedor VoIP

Si su presupuesto es realmente limitado, puede configurar un trunk SIP para conectarse a la PSTN. Es ciertamente la forma más asequible de conectarse a la PSTN. Existen miles de proveedores VoIP en todo el mundo. Para conectarse a uno de ellos, necesitará algunos parámetros. Parámetros proporcionados por el proveedor SIP.

- username: login
- password: secret
- Dominio del proveedor: domain
- Puerto UDP: 5060
- Codecs permitidos: g729, ilbc, alaw

Dos parámetros deben ser determinados por usted.

- Extensión para recibir llamadas—en este caso: 9999
- context: from-sip

En PJSIP, un trunk SIP que se registra se construye a partir de la misma familia de objetos utilizada para un endpoint, más objetos explícitos `registration` y `identify`. El objeto `registration` le dice a Asterisk que se registre en el proveedor, el objeto `identify` coincide con el tráfico entrante desde la IP del proveedor hacia el endpoint (PJSIP autentica los INVITE entrantes por IP de origen), y `outbound_auth` suministra las credenciales para llamadas salientes y registro:

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
auth_type=userpass
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

Para acceder a este trunk, usaremos el nombre de canal `PJSIP/siptrunk`. El ajuste `dtmf_mode=rfc4733` lleva DTMF fuera de banda (RFC 4733 hace obsoleta la antigua RFC 2833; la carga útil es idéntica). La opción `identify`/`match` acepta direcciones IP, CIDRs o nombres de host, pero los nombres de host se resuelven una vez en el momento de la carga de la configuración, por lo que para un proveedor con IPs cambiantes, enumere la(s) IP(s) de señalización explícitamente. Confirme el registro con `pjsip show registrations`.

## Introducción al dialplan

El dialplan es como el corazón de Asterisk. Define cómo Asterisk maneja cada llamada al PBX. Consiste en extensiones que crean una lista de instrucciones para que Asterisk las siga. Las instrucciones son disparadas por dígitos recibidos desde el canal o la aplicación. Para configurar Asterisk con éxito, es crucial entender el dialplan. La mayor parte del dialplan está contenido en el archivo extensions.conf en el directorio /etc/asterisk. Este archivo utiliza la gramática de grupo simple y tiene cuatro conceptos principales:

- Extensiones
- Prioridades
- Aplicaciones
- Contextos

Creemos un dialplan básico. En las secciones siguientes de este libro, dedicaré un capítulo exclusivamente al dialplan. Si instaló los archivos de muestra (make samples), el extensions.conf ya existe. Guárdelo con otro nombre y comience con un archivo en blanco.

## La estructura del archivo extensions.conf

El archivo extensions.conf está separado en secciones. La primera es la sección [general] seguida de la sección [globals]. El comienzo de cada sección empieza con la definición de su nombre (es decir, [default]) y termina cuando se crea otra sección.

### La sección [general]

La sección general se encuentra en la parte superior del archivo. Antes de comenzar a configurar el dialplan, es útil conocer las opciones generales que controlan ciertos comportamientos del dialplan. Estas opciones son:

- static y write protect: Si static=yes y writeprotect=no, puede usar la CLI

```
command save dialplan.
```

Advertencia: Si emite un comando save dialplan desde la CLI, terminará perdiendo cualquier nota y comentario en el archivo.

- autofallthrough: Si autofallthrough está configurado, entonces si una extensión se queda sin cosas que hacer, terminará la llamada con BUSY, CONGESTION o HANGUP dependiendo de la mejor estimación de Asterisk. Este es el valor por defecto. Si autofallthrough no está configurado, entonces si una extensión se queda sin cosas que hacer, Asterisk esperará a que se marque una nueva extensión.
- clearglobalvars: Si clearglobalvars está configurado, las variables globales se borrarán y se volverán a analizar en un dialplan reload o Asterisk reload. Si clearglobalvars no está configurado, entonces las variables globales persistirán a través de recargas y—incluso si se eliminan del extensions.conf o uno de sus archivos incluidos—permanecerán establecidas en el valor anterior.
- extenpatternmatchnew: Utiliza un algoritmo de coincidencia de patrones más rápido, lo que ayuda notablemente cuando tiene un gran número de extensiones. Por defecto es no.
- userscontext: Este es el contexto donde se registran las entradas de users.conf.

### La sección [globals]

En la sección [globals] definirá variables globales y sus valores iniciales. Puede acceder a la variable en el dialplan usando ${GLOBAL(variable)}. Incluso puede acceder a variables definidas en el entorno linux/unix usando ${ENV(variable)}. Las variables globales no distinguen entre mayúsculas y minúsculas. Algunos ejemplos podrían ser:

```
INCOMING>DAHDI/8&DAHDI/9
RINGTIME=>3
```

En el siguiente ejemplo, puede establecer y probar una variable global en el dialplan.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contextos

El contexto es la partición nombrada del dialplan. Después de las secciones [general] y [globals], el dialplan es un conjunto de contextos en los que cada contexto tiene varias extensiones, cada extensión tiene varias prioridades, y cada prioridad llama a una aplicación con varios argumentos.

![Flujo de llamadas de Asterisk: cada llamada llega a un canal (IAX, SIP y otros) como una pata de llamada entrante; el contexto del canal — establecido globalmente o por canal en el archivo de configuración del canal — decide qué contexto en extensions.conf procesa la llamada antes de que salga por la pata saliente.](../images/04-first-pbx-fig03.png)

![Procesamiento de llamadas: el `context=` definido para un canal (en chan_dahdi.conf o pjsip.conf) nombra el contexto coincidente en extensions.conf donde el dialplan maneja la llamada.](../images/04-first-pbx-fig04.png)

Puede construir un dialplan simple para llegar a otros teléfonos y a la PSTN. Sin embargo, Asterisk es mucho más potente que eso. Nuestro objetivo es enseñarle más detalles de lo que es posible en el dialplan.

## Extensiones

A diferencia del PBX tradicional, donde las extensiones están asociadas con teléfonos, interfaces, menús, etc., en Asterisk una extensión es una lista de comandos a procesar cuando se dispara un número o nombre de extensión específico. Los comandos se procesan en orden de prioridad.

![Sintaxis de extensión: `exten => number(name),{priority|label}[(alias)],application`. Las extensiones pueden ser numéricas, alfanuméricas, numéricas con identificador de llamadas, un patrón o una extensión estándar como `s`; las prioridades pueden ser un número, `n` (siguiente), `s` (mismo), un desplazamiento o una `hint`.](../images/04-first-pbx-fig05.png)

Una extensión puede ser literal, estándar o especial. Una extensión estándar incluye solo números o nombres y los caracteres * y #; 12#89* es una extensión literal válida. Los nombres también se pueden usar para la coincidencia de extensiones. Las extensiones distinguen entre mayúsculas y minúsculas. Sin embargo, no puede crear dos extensiones con el mismo nombre pero diferente caso. Cuando se marca una extensión, se ejecuta el comando con la primera prioridad, seguido del comando con la prioridad 2 y así sucesivamente. Esto sucede hasta que la llamada se desconecta o algún comando devuelve el número uno, indicando un fallo. Lo que hace Asterisk cuando se ejecuta la última prioridad está regulado por el parámetro autofallthrough. Vea la sección [general] en este capítulo. Ejemplo:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Arriba encuentra la lista de instrucciones a procesar cuando se marca la extensión 123. La primera prioridad es responder al canal (necesario cuando el canal está en estado de timbre: es decir, canales FXO). La segunda prioridad es reproducir un archivo de audio llamado tt-weasels. La tercera prioridad cuelga el canal. Otra opción es manejar la llamada de acuerdo con el identificador de llamadas. Puede usar el carácter / para especificar el identificador de llamadas a procesar. Ejemplos:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Este ejemplo disparará la extensión 123 y ejecutará las siguientes opciones solo si el identificador de llamadas es 100. Esto también se puede hacer usando el patrón descrito a continuación:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: asigna una extensión a un canal. Se utiliza para monitorear el estado del canal. Se utiliza junto con la presencia. El teléfono tiene que soportarlo.

#### Patrones

Puede usar patrones y literales en el dialplan. Los patrones son muy útiles para reducir el tamaño del dialplan. Todos los patrones comienzan con el carácter “_”. Se pueden usar los siguientes caracteres para definir un patrón. La figura identifica los patrones disponibles para su uso con Asterisk.

![Caracteres de coincidencia de patrones: `_` inicia un patrón, `.` coincide con uno o más caracteres, `!` coincide con cero o más, `[123-7]` coincide con cualquier dígito o rango listado, `X` es 0-9, `Z` es 1-9 y `N` es 2-9 — con ejemplos que mapean rangos de extensiones de oficina.](../images/04-first-pbx-fig06.png)

### Extensiones especiales

Asterisk utiliza algunos nombres de extensión como extensiones estándar.

![Extensiones especiales de Asterisk: `i` (inválido), `s` (inicio), `h` (colgar), `t` (tiempo de espera), `T` (tiempo de espera absoluto), `o` (operador), `a` (presionado `*` en correo de voz), `fax` (detección de fax) y `Talk` (usado con BackgroundDetect).](../images/04-first-pbx-fig07.png)

Descripción: s: Inicio. Se utiliza para manejar una llamada cuando no hay un número marcado. Es útil para trunks FXO y procesamiento de menús. t: Tiempo de espera. Se utiliza cuando las llamadas permanecen inactivas después de que se ha reproducido un aviso. También se utiliza para colgar una línea inactiva. T: AbsoluteTimeout. Si establece un límite de llamada usando la función de dialplan `TIMEOUT(absolute)`, una vez que la llamada excede el límite definido, se enviará a la extensión T. h: Colgar. Se llama después de que el usuario desconecta la llamada. i: Inválido. Se dispara cuando llama a una extensión inexistente en el contexto. El uso de estas extensiones puede afectar el contenido de los registros CDR—específicamente, el dst que no contiene el número marcado. o: Operador. Se utiliza para ir al operador cuando el usuario presiona “0” durante el correo de voz. El uso de estas extensiones puede cambiar el contenido de los registros de facturación (CDR)—en particular, el campo dst no tendrá el número marcado. Para solucionar este problema, debe usar la opción g en la aplicación dial() y considerar las funciones resetcdr(w) y/o nocdr()

## Variables

En el PBX Asterisk, las variables pueden ser globales, específicas del canal y específicas del entorno. Puede usar la aplicación NoOP() para ver el contenido de una variable en la consola. Puede usar una variable global o una variable específica del canal como argumentos de aplicaciones. Una variable puede ser referenciada como en el siguiente ejemplo, donde varname es el nombre de la variable.

```
${varname}
```

Un nombre de variable puede ser una cadena alfanumérica que comienza con una letra. Los nombres de variables globales no distinguen entre mayúsculas y minúsculas. Sin embargo, las variables del sistema (definidas por Asterisk son definidas por el canal) distinguen entre mayúsculas y minúsculas. Por lo tanto, la variable ${EXTEN} es diferente de ${exten}.

### Variables globales

Las variables globales se pueden configurar en la sección [global] en el archivo extensions.conf o usando la aplicación:

```
set(Global(variable)=content)
```

### Variables específicas del canal

Las variables específicas del canal se configuran usando la aplicación set(). Cada canal recibe su propio espacio de variables. No hay posibilidad de colisiones entre variables de diferentes canales. Una variable específica del canal se destruye cuando el canal cuelga. Algunas de las variables más utilizadas son:

- ${EXTEN} Extensión marcada
- ${CONTEXT} Contexto actual
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} Identificador de llamadas actual
- ${PRIORITY} Prioridad actual

Otras variables específicas del canal están todas en mayúsculas. Puede ver el contenido de varias variables usando la aplicación dumpchan(). A continuación se muestra un extracto simple de variables de dump-channel.

```
exten=9001,1,dumnpchan()
exten=9001,n,echo()
exten=9001,n,hangup()
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

El diseño de campo anterior es la salida `DumpChan` de Asterisk 22 (un nombre de canal `PJSIP/...` real, los campos `CallerIDNum`/`ConnectedLineID` y las filas `Raw*`/`Transcode`/`BridgeID` que los canales PJSIP completan). A diferencia del controlador antiguo, un canal PJSIP no establece automáticamente las variables de canal `SIPCALLID`/`SIPUSERAGENT`; los detalles SIP equivalentes se leen bajo demanda con las funciones de dialplan `PJSIP_HEADER()` y `CHANNEL()` — por ejemplo `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` y `${CHANNEL(rtp,dest)}` para la dirección RTP remota.

### Variables específicas del entorno

Las variables específicas del entorno se pueden usar para acceder a variables definidas en el sistema operativo. Puede establecer variables específicas del entorno usando la función ENV(). Por ejemplo:

```
${ENV(LANG)}
Set(ENV(LANG))=en_US
```

### Variables específicas de la aplicación

Algunas aplicaciones usan variables para entrada y salida de datos. Puede establecer variables antes de llamar a la aplicación o recuperar la variable después de la ejecución de la aplicación. Por ejemplo: La aplicación Dial devuelve las siguientes variables:

- ${DIALEDTIME} -> Este es el tiempo desde que se marca un canal hasta que se desconecta.
- ${ANSWEREDTIME} -> Esta es la cantidad de tiempo para la llamada real.
- ${DIALSTATUS} Este es el estado de la llamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Mensaje de error para la llamada.

## Expresiones

Las expresiones pueden ser muy útiles en el dialplan. Se utilizan para manipular cadenas y realizar operaciones matemáticas y lógicas.

![Descripción general de las expresiones de Asterisk — `$[expression1 operator expression2]` — agrupando los operadores matemáticos, lógicos, de comparación, de expresión regular y condicionales disponibles en el dialplan.](../images/04-first-pbx-fig08.png)

La sintaxis de la expresión se define de la siguiente manera:

```
$[expression1 operator expression2]
```

Supongamos que tenemos una variable llamada “I” y queremos sumar 100 a la variable:

```
$[${I}+100]
```

Cuando Asterisk encuentra una expresión en el dialplan, cambia toda la expresión por el valor resultante.

### Operadores

Los siguientes operadores se pueden usar para construir expresiones. Es importante observar la precedencia de los operadores. 1. Paréntesis “()” 2. Operadores unarios “! -“ 3. Expresión regular “: =~ 4. Operadores multiplicativos “* / %” 5. Operadores aditivos “+ -“ 6. Operadores de comparación 7. Operadores lógicos 8. Operadores condicionales

#### Operadores matemáticos

- Suma (+)
- Resta (-)
- Multiplicación (*)
- División (/)
- Módulo (%)

#### Operadores lógicos

- Lógico “AND” (&)
- Lógico “OR” (|)
- Complemento unario lógico (!)

#### Operadores de expresión regular

- Coincidencia de expresión regular (:)
- Coincidencia exacta de expresión regular (=~)

Una expresión regular es una cadena de texto especial utilizada para describir un patrón de búsqueda. Puede pensar en las expresiones regulares como comodines. Las expresiones regulares se utilizan para hacer coincidir una cadena con un patrón para verificar la coincidencia. Si la coincidencia tiene éxito y la expresión regular contiene al menos una coincidencia, se devuelve la primera coincidencia; de lo contrario, el resultado es el número de caracteres coincidentes.

#### Operadores de comparación

El resultado de una comparación es 1 si la relación es verdadera o 0 si es falsa.

- = igual
- != no igual
- < menor que
- > mayor que
- <= menor o igual que
- >= mayor o igual que

### LAB. Evalúe las siguientes expresiones:

Ponga estas expresiones en su dialplan y use la aplicación NoOP() para evaluar las expresiones. Marque 9002 y examine los resultados en la consola de Asterisk. Use verbose 15 para mostrar los resultados.

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

## Funciones

Algunas aplicaciones han sido reemplazadas por funciones, que permiten el procesamiento de variables de una manera más avanzada que las expresiones por sí solas. Puede ver la lista completa de funciones emitiendo el siguiente comando de consola:

```
CLI>core show functions
```

Longitud de cadena: ${LEN(string)} devuelve la longitud de la cadena

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

En la primera operación, el sistema muestra 5 como resultado (el número de letras en la palabra “fruit”). La segunda devuelve el número 4 (el número de letras en la palabra “pear”). Subcadenas: Devuelve la subcadena, comenzando desde la posición definida por el parámetro “offset”, con la longitud de cadena definida en el parámetro “length”. Si el offset es negativo, comienza de derecha a izquierda, empezando al final de la cadena. Si la longitud se omite o es negativa, toma toda la cadena comenzando con el offset.

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

Ejemplo #2: Tome el código de área de los primeros tres dígitos.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Ejemplo #3: Toma todos los dígitos de la variable ${EXTEN}, excepto el código de área.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Concatenación de cadenas

Para concatenar dos cadenas, simplemente escríbalas juntas.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Aplicaciones

Para construir un dialplan, necesitamos entender el concepto de aplicaciones. Usará aplicaciones para manejar el canal en el dialplan. Las aplicaciones se implementan en varios módulos. Las aplicaciones disponibles dependen de los módulos. Puede mostrar todas las aplicaciones de Asterisk usando el comando de consola:

```
CLI>core show applications
```

Alternativamente, puede mostrar detalles de una aplicación específica usando el siguiente ejemplo:

```
CLI>core show application dial
```

Para construir un dialplan simple, necesita conocer algunas aplicaciones. Discutiremos ejemplos más avanzados más adelante en el libro.

![El puñado de aplicaciones necesarias para construir un dialplan simple: Answer (responder un canal), Dial (llamar a otro canal), Hangup (colgar un canal), Playback (reproducir un archivo de audio) y Goto (saltar a una prioridad, extensión o contexto).](../images/04-first-pbx-fig09.png)

Usaremos estas aplicaciones (arriba) para crear un dialplan simple para dos PBX básicos.

### Answer()

[Sinopsis] Responde un canal si está sonando [Descripción] Answer([delay]): Si la llamada no ha sido respondida, la aplicación la responderá. De lo contrario, no tiene efecto en la llamada. Si se especifica un retraso, Asterisk esperará el número de milisegundos especificado en ‘delay’ antes de responder la llamada.

### Dial()

La siguiente descripción se puede obtener emitiendo show application dial en el dialplan. Para facilitar la búsqueda, se reproduce a continuación. La sintaxis para la aplicación Dial también se muestra a continuación:

```
;dial to a single channel
Dial(type/identifier,timeout,options, URL)
;Dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...][|timeout][|options][|URL]):
```

Esta aplicación realizará llamadas a uno o más canales especificados. Tan pronto como uno de los canales solicitados responda, el canal de origen será respondido—si no ha sido respondido ya. Estos dos canales estarán entonces activos en una llamada puenteada. Todos los demás canales solicitados serán colgados. A menos que se especifique un tiempo de espera, la aplicación Dial esperará indefinidamente hasta que uno de los canales llamados responda, el usuario cuelgue, o todos los canales llamados estén ocupados o no disponibles. La ejecución del dialplan continuará si no se pueden llamar a los canales solicitados o si expira el tiempo de espera. Esta aplicación establece las siguientes variables de canal al finalizar:

- DIALEDTIME - Este es el tiempo desde que se marca un canal hasta el momento en que se desconecta.
- ANSWEREDTIME - Esta es la cantidad de tiempo para una llamada real.
- DIALSTATUS - Este es el estado de la llamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

Para los Modos de Privacidad y Filtrado, la variable DIALSTATUS se establecerá en DONTCALL si la parte llamada elige enviar a la parte que llama al script 'Go Away'. La variable DIALSTATUS se establecerá en TORTURE si la parte llamada quiere enviar a la persona que llama al script 'torture'. Esta aplicación informará la terminación normal si el canal de origen cuelga o si la llamada está puenteada y cualquiera de las partes en el puente termina la llamada. La URL opcional se enviará a la parte llamada si el canal lo soporta. Si la variable OUTBOUND_GROUP está establecida, todos los canales pares creados por esta aplicación se incluirán en ese grupo (como en

```
Set(GROUP()=...).
```

La siguiente tabla resume algunas de las opciones más utilizadas para la aplicación Dial. Para la lista completa, use el comando de consola `core show application Dial`. En Asterisk 22, estas opciones están separadas del canal y el tiempo de espera por comas — por ejemplo `Dial(PJSIP/2000,20,tTm)`.

| Opción | Descripción |
|--------|-------------|
| `A(x)` | Reproduce un anuncio a la parte llamada, usando `x` como el archivo. |
| `C` | Restablece el CDR para esta llamada. |
| `d` | Permite al usuario que llama marcar una extensión de 1 dígito mientras espera a que se responda la llamada. Sale a esa extensión si existe en el contexto actual, o al contexto definido en la variable `EXITCONTEXT`, si existe. |
| `D([called][:calling])` | Envía las cadenas DTMF especificadas después de que la parte llamada responda, pero antes de que la llamada sea puenteada. La cadena `called` se envía a la parte llamada y la cadena `calling` a la parte que llama. Cualquiera de los parámetros se puede usar solo. |
| `f` | Fuerza a que el identificador de llamadas del canal que llama se establezca en la extensión asociada con el canal a través de un `hint` de dialplan. Útil donde la PSTN no permite un identificador de llamadas arbitrario. |
| `g` | Procede con la ejecución del dialplan en la extensión actual si el canal de destino cuelga. |
| `G(context^exten^pri)` | Si se responde la llamada, transfiere a la parte que llama a la prioridad especificada y a la parte llamada a prioridad+1. Opcionalmente se puede especificar una extensión (o extensión y contexto); de lo contrario, se utiliza la extensión actual. |
| `h` | Permite a la parte llamada colgar enviando el dígito DTMF `*`. |
| `H` | Permite a la parte que llama colgar enviando el dígito DTMF `*`. |
| `L(x[:y][:z])` | Limita la llamada a `x` ms, reproduce una advertencia cuando quedan `y` ms, y repite la advertencia cada `z` ms. Vea las variables `LIMIT_*` a continuación. |
| `m([class])` | Proporciona música en espera a la parte que llama hasta que el canal solicitado responda. Se puede especificar una clase de MusicOnHold específica. |
| `r` | Indica timbre a la parte que llama y no pasa audio hasta que el canal llamado responda. |
| `S(x)` | Cuelga la llamada `x` segundos después de que la parte llamada responda. |
| `t` | Permite a la parte llamada transferir a la parte que llama enviando la secuencia DTMF definida en `features.conf`. |
| `T` | Permite a la parte que llama transferir a la parte llamada enviando la secuencia DTMF definida en `features.conf`. |
| `w` | Permite a la parte llamada habilitar la grabación de un toque enviando la secuencia DTMF definida en `features.conf`. |
| `W` | Permite a la parte que llama habilitar la grabación de un toque enviando la secuencia DTMF definida en `features.conf`. |
| `k` | Permite a la parte llamada estacionar la llamada enviando la secuencia DTMF definida para el estacionamiento de llamadas en `features.conf`. |
| `K` | Permite a la parte que llama estacionar la llamada enviando la secuencia DTMF definida para el estacionamiento de llamadas en `features.conf`. |

La opción `L(x[:y][:z])` se puede ajustar con las siguientes variables especiales:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (por defecto `yes`): reproduce sonidos para la persona que llama.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: reproduce sonidos para la parte llamada.
- `LIMIT_TIMEOUT_FILE` — archivo a reproducir cuando se acaba el tiempo.
- `LIMIT_CONNECT_FILE` — archivo a reproducir cuando comienza la llamada.
- `LIMIT_WARNING_FILE` — archivo a reproducir como advertencia cuando se define `y`. El valor por defecto es decir el tiempo restante.

Ejemplo:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

En el ejemplo anterior, la aplicación marcará al canal PJSIP correspondiente. Tanto quien llama como quien es llamado podrían transferir la llamada (Tt). Se escuchará música en espera en lugar de tono de retorno. Si nadie responde dentro de 20 segundos, la extensión irá a la siguiente prioridad.

### Hangup()

Cuelga el canal que llama [Descripción] Hangup([causecode]): Esta aplicación colgará el canal que llama. Si se da un código de causa, la causa de colgado del canal se establecerá en el valor dado.

### Goto()

Saltar a una prioridad, extensión o contexto particular [Descripción] Goto([[context|]extension|]priority): Esta aplicación hará que el canal que llama continúe la ejecución del dialplan en la prioridad especificada. Si no se especifica una extensión específica (o extensión y contexto), esta aplicación saltará a la prioridad especificada de la extensión actual. Si el intento de saltar a otra ubicación en el dialplan no tiene éxito, el canal continuará en la siguiente prioridad de la extensión actual.

## Construyendo un dialplan

Para construir un dialplan simple, necesita tratar todas las llamadas entrantes y salientes creando contextos y extensiones. En esta sección, le mostraremos cómo construir las extensiones más comunes.

### Marcar entre extensiones

Para permitir marcar entre extensiones, podríamos usar la variable de canal ${EXTEN}, que se refiere a la extensión marcada. Por ejemplo, si el rango de extensión está entre 4000 y 4999 y todas las extensiones usan SIP, podríamos adoptar el siguiente comando:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Marcar a un destino externo

Para marcar un destino externo, podría preceder el número marcado con una ruta. En Norteamérica, es común usar 9 seguido del número a marcar externamente. Si está utilizando un canal analógico o digital a la PSTN, el comando debería verse como el siguiente: Si desea usar el trunk SIP en lugar del DAHDI, use el canal `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

La línea anterior le permitirá marcar 9 y el número deseado. En el ejemplo dado, usará el primer canal DAHDI (DAHDI/1). Si tiene varias líneas y esta está ocupada, la llamada no se completará. Sin embargo, podría usar la siguiente línea para elegir automáticamente el primer canal DAHDI disponible. Opcionalmente, puede usar el trunk SIP en lugar de DAHDI. En la forma PJSIP `Dial(PJSIP/number@siptrunk,...)`, el número marcado es la parte del usuario y `siptrunk` es el endpoint configurado arriba.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

El parámetro “g1” buscará el primer canal disponible en el grupo, permitiendo el uso de todos los canales. Usando la línea a continuación, podría marcar un número de larga distancia.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Marcar 9 para obtener una línea PSTN

Si no tiene ninguna restricción para marcar externamente, podría simplificar y usar lo siguiente:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Recibir una llamada en la extensión del operador

En el siguiente ejemplo, la extensión del operador es 4000. La línea PSTN está conectada a una interfaz FXO. En el archivo chan_dahdi.conf, el contexto especificado es from-pstn. Cualquier llamada que venga de la PSTN será enrutada al contexto from-pstn en el dialplan. Esta línea no tiene marcación directa entrante (DID); como tal, tendremos que recibir la llamada a través de la extensión “s”. Si recibe desde el trunk SIP, use el contexto [from-sip].

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

### Recibir una llamada usando marcación directa entrante (DID)

Si tiene una línea digital, recibirá la extensión marcada. Cuando este es el caso, no necesita reenviar la llamada al operador; en su lugar, puede reenviar la llamada directamente al destino. Suponga que su rango DID es de 3028550 a 3028599 y los últimos cuatro números se pasan en el DID. La configuración se vería como el siguiente ejemplo:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Reproducir varias extensiones simultáneamente

Puede configurar Asterisk para marcar una extensión y, si no se responde, marcar varias otras extensiones simultáneamente, como se indica en el siguiente ejemplo:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

En este ejemplo, cuando alguien marca al operador, se intenta inicialmente el canal DAHDI/1. Si nadie responde después de 15 segundos (tiempo de espera), los canales DAHDI/1, DAHDI/2 y DAHDI/3 sonarán simultáneamente por otros 15 segundos.

### Enrutamiento por identificador de llamadas

En este ejemplo, podría dar diferentes tratamientos basados en el identificador de llamadas, lo que podría ser útil para los spammers de llamadas. Por ejemplo:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

En este ejemplo, hemos añadido una regla especial que, si el identificador de llamadas es 4832518888, reproduce un mensaje del archivo previamente grabado “I-have-moved-to-china”. Otras llamadas se aceptan como de costumbre.

### Usando variables en el dialplan

Asterisk puede usar variables globales y de canal en el dialplan como argumentos para ciertas aplicaciones. Mire los siguientes ejemplos:

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

Usar variables hace que los cambios futuros sean más fáciles. Si cambia la variable, todas las referencias se cambian inmediatamente.

### Grabar un anuncio

En algunas de las opciones discutidas más adelante en esta sección, usaremos avisos grabados. Aquí le mostramos una forma fácil de grabarlos. Usaremos la aplicación Record() para guardar el anuncio usando el propio teléfono.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Estas instrucciones le permiten grabar cualquier mensaje desde un softphone. Ejemplo: marcar recordmenu desde el softphone Las instrucciones llamarán a la grabación con la variable ${EXTEN:6} sin las primeras seis letras. En otras palabras, la instrucción es equivalente a record(menu:gsm). Todo lo que tiene que hacer es marcar record + nombre_del_archivo_a_ser_grabado, presione # para finalizar la grabación y espere a escuchar la grabación.

### Recibir las llamadas en una recepcionista digital

Ahora que tenemos algunos ejemplos simples, expandamos nuestro aprendizaje sobre las aplicaciones background() y goto(). La clave para los sistemas interactivos en Asterisk es la aplicación background(), que le permite ejecutar un archivo de audio que, cuando la persona que llama presiona una tecla, se interrumpe para enviar la llamada a la extensión marcada. Sintaxis de la aplicación background():

```
exten=>extension, priority, background(filename)
```

Otra aplicación muy útil es goto(). Como su nombre indica, salta al contexto, extensión y prioridad indicados. Sintaxis de la aplicación goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Formatos válidos para el comando goto():

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

En el siguiente ejemplo, crearemos una recepcionista digital. Es muy simple editar el archivo extensions.conf y configurar las siguientes extensiones:

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

Las extensiones SIP usan `PJSIP/` y las extensiones IAX usan `IAX2/` — ambos controladores se envían en Asterisk 22, aunque `chan_iax2` ahora se considera legado y se prefiere SIP/PJSIP.

En el archivo menu1.gsm, grabe el mensaje “presione la extensión o espere al operador”. Cuando el usuario marca el número 6000, será enviado a la extensión 6000. En este punto, debería tener una comprensión clara del uso de varias aplicaciones, incluyendo answer(), background(), goto(), hangup() y playback(). Si no tiene una comprensión clara, por favor lea este capítulo de nuevo hasta que se sienta cómodo con el contenido. Usará la aplicación background muy a menudo. Una vez que entienda los conceptos básicos de extensiones, prioridades y aplicaciones, será fácil crear un dialplan simple. Estos conceptos se explorarán con mayor profundidad más adelante en el libro, y verá que el dialplan se volverá más potente.

## Resumen

En este capítulo, ha aprendido que los archivos de configuración se almacenan en el directorio /etc/asterisk. Para usar Asterisk, primero es necesario configurar los canales (p. ej., pjsip, dahdi, iax). Existen tres gramáticas diferentes para los archivos de configuración: grupo simple, herencia de objetos y entidad compleja. El dialplan se crea en el archivo extensions.conf y es un conjunto de contextos y extensiones. En el dialplan, cada extensión dispara una aplicación. Ha aprendido a usar las aplicaciones playback, background, dial, goto, hangup y answer.

## Cuestionario

1. Los archivos de configuración de canal son (elija todos los que correspondan):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. En Asterisk 22, el único peer `chan_sip` `[6001]` (`type=friend`/`host=dynamic`) es reemplazado en `pjsip.conf` por qué conjunto de objetos relacionados?
   - A. Un `type=peer` y un `type=user`
   - B. Un `type=endpoint`, un `type=auth` y un `type=aor`
   - C. Un único `type=friend`
   - D. Un `type=transport` y un `type=global`
3. Definir un contexto en el archivo de configuración del canal importa porque establece el contexto entrante para las llamadas desde ese canal — una llamada desde el canal se procesa en el contexto coincidente en `extensions.conf`.
   - A. Verdadero
   - B. Falso
4. Las principales diferencias entre las aplicaciones `Playback()` y `Background()` son (elija dos):
   - A. Playback reproduce un aviso pero no espera dígitos.
   - B. Background reproduce un aviso pero no espera dígitos.
   - C. Background reproduce un mensaje y espera a que se presionen dígitos.
   - D. Playback reproduce un mensaje y espera a que se presionen dígitos.
5. Cuando una llamada entra a Asterisk a través de una tarjeta de interfaz de telefonía (FXO) sin DID, se maneja en la extensión especial:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Los formatos válidos para la aplicación `Goto()` son (elija tres):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. El patrón `_7[1-5]XX` coincide con (elija todos los que correspondan):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. En `Dial(PJSIP/${EXTEN},20,tTm)`, ¿qué hace la opción `m`?
   - A. Limita la llamada a una duración máxima.
   - B. Proporciona música en espera a la persona que llama en lugar de tono de retorno hasta que el canal responde.
   - C. Envía dígitos DTMF después de que la parte llamada responde.
   - D. Fuerza el identificador de llamadas usando una sugerencia (hint) de dialplan.
9. En la gramática de herencia de opciones utilizada por `chan_dahdi.conf`, usted:
   - A. Define el objeto en una sola línea.
   - B. Define las opciones primero y declara los objetos debajo de las opciones definidas.
   - C. Define un contexto separado para cada objeto.
10. Las prioridades en una extensión deben estar numeradas consecutivamente (1, 2, 3, …) y no pueden usar `n`.
    - A. Verdadero
    - B. Falso

**Respuestas:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
