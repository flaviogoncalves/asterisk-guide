# Troncado SIP, DID y la PSTN

Una PBX que solo puede llamarse a sí misma no es muy útil. Tarde o temprano todo
sistema tiene que alcanzar el resto del mundo — la red telefónica pública conmutada
(PSTN), un proveedor SIP o otra PBX. El enlace que transporta esas llamadas es un
**trunk**. En la era TDM un trunk era un circuito físico: un T1/E1 PRI o un conjunto
de líneas analógicas FXO. Hoy en día casi siempre es un **SIP trunk** — una conexión
lógica a un Proveedor de Servicios de Telefonía por Internet (ITSP) transportada
sobre la misma red IP que todo lo demás.

Este capítulo muestra cómo conectar Asterisk 22 a un ITSP con PJSIP, cómo elegir
entre un trunk basado en registro y uno basado en IP, cómo enrutar números DID
entrantes al destino correcto, cómo enviar llamadas salientes con el identificador
de llamada y formato E.164 correctos, y cómo construir conmutación por falla y
enrutamiento de menor costo a través de varios trunks. Terminamos con el manejo
de NAT para trunks y un laboratorio que levanta una segunda Asterisk (y SIPp) como
un ITSP simulado para que puedas realizar llamadas reales a través de un trunk.

Todo aquí está verificado contra el laboratorio del libro de Asterisk 22.10.0; el
patrón de objeto trunk es el mismo introducido en *Building your first PBX with PJSIP*
y *SIP & PJSIP in depth*.

## Objectives

Al final de este capítulo, deberías poder:

- Conectar Asterisk 22 a un ITSP con PJSIP
- Elegir entre trunks basados en registro y trunks basados en IP (estáticos)
- Enrutar DIDs entrantes a la extensión, IVR o cola correcta
- Enrutar llamadas salientes con el identificador de llamada correcto y formato E.164
- Construir failover de trunk y enrutamiento de menor costo con `${DIALSTATUS}`
- Manejar NAT para trunks en el transporte y el endpoint

## What is a SIP trunk

Un SIP trunk es una ruta lógica de voz entre su PBX y otro sistema SIP. En la práctica ese "otro sistema" es una de dos cosas:

- **Un ITSP (Internet Telephony Service Provider).** Un operador comercial que le vende origen y terminación de llamadas y, usualmente, un bloque de números de teléfono (DIDs). Usted apunta Asterisk al host de señalización del proveedor, y el proveedor conecta sus llamadas a la PSTN más amplia. Así es como la mayoría de los sistemas modernos llegan a la red telefónica — sin hardware de telefonía requerido.
- **Una puerta de enlace PSTN.** Un dispositivo (u otro Asterisk) que tiene interfaces físicas PSTN — una tarjeta PRI, puertos analógicos FXO, o una puerta de enlace GSM/4G — y los presenta a su PBX como SIP. La puerta de enlace realiza la conversión TDM‑a‑SIP; desde el punto de vista de Asterisk es simplemente otro SIP trunk.

De cualquier forma, en PJSIP un trunk es **solo un endpoint**. La misma familia de objetos que usó para un teléfono — `endpoint`, `auth`, `aor`, opcionalmente `identify` y `registration` — construye un trunk. Las diferencias están en los detalles: un trunk autentica *salientes* (usted es el cliente, así que las credenciales van en `outbound_auth`, no en `auth`), usualmente no registra un agente de usuario hacia usted (usted se registra a *él*, o él le envía tráfico desde una IP conocida), y coloca las llamadas entrantes en un contexto dedicado como `from-pstn` en lugar de `from-internal`.

> **Comparado con el antiguo trunk TDM.** Un PRI le daba un número fijo de canales B (23 en un T1, 30 en un E1) y señalizaba el establecimiento de la llamada a través de un canal D dedicado (ver el capítulo *Legacy channels*). Un SIP trunk no tiene un recuento fijo de canales — la capacidad es la que permite su ancho de banda, la política de su proveedor y cualquier límite `max_contacts`/de‑llamadas‑concurrentes. El identificador de llamada, DID y el progreso de la llamada que antes viajaban en elementos de información ISDN ahora viajan en encabezados SIP y SDP.

Hay dos formas en que un ITSP aceptará intercambiar tráfico con usted, y determinan cómo construye el trunk: **basado en registro** y **basado en IP (estático)**. Cubrimos cada una a su vez.

## Troncales basadas en registro

Una troncal basada en registro es el modelo usado cuando el proveedor espera que *tú* inicies sesión en *él*. Tu Asterisk envía periódicamente un SIP `REGISTER` al proveedor, autenticándose con un nombre de usuario y una contraseña, exactamente como lo hace un teléfono al registrarse en tu PBX. Esto es común cuando tu IP pública es dinámica, cuando estás detrás de NAT, o cuando el proveedor simplemente identifica a los clientes por credenciales SIP en lugar de por dirección IP.

En PJSIP el inicio de sesión saliente vive en un objeto dedicado `registration`. Reemplaza la única línea `register =>` que el controlador `chan_sip` eliminado usaba en `sip.conf`. Aquí hay una troncal de registro completa a un proveedor ficticio, siguiendo el patrón verificado de los capítulos anteriores — nota `outbound_auth` (no `auth`), `server_uri`/`client_uri` (no `server`/`client`), `from_user`/`from_domain` en el endpoint, y `dtmf_mode=rfc4733`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

Algunas cosas a notar:

- **`auth_type=digest`, no `userpass`.** Ambas producen la misma autenticación digest, pero en Asterisk 22 `userpass` (y el antiguo `md5`) están **obsoletos y se convierten silenciosamente a `digest`**. Prefiere `digest` en configuraciones nuevas; aún verás `userpass` en archivos más antiguos y en los capítulos anteriores de este libro.
- **`outbound_auth` tanto en el endpoint como en el registro.** El registro lo usa para autenticar el `REGISTER`; el endpoint lo usa para responder al `407 Proxy Authentication Required` que el proveedor envía de vuelta a un `INVITE` saliente. Pueden compartir un objeto `auth`.
- **`from_user` / `from_domain`.** Muchos proveedores rechazan llamadas cuyo encabezado `From` no lleva tu número de cuenta y su dominio. Estas dos opciones establecen exactamente eso.
- **`contact_user=4830001000`.** Esto se convierte en la parte de usuario del `Contact` que registras, de modo que el proveedor sepa a qué número entregar las llamadas entrantes. Es el equivalente moderno del sufijo `/9999` en la antigua línea `register =>`.
- **`retry_interval=60`.** Si el registro falla, reintenta cada 60 segundos.

Después de una recarga, confirma el registro con `pjsip show registrations`. En el laboratorio — donde `itsp.example.com` no responde realmente — la tabla se ve así:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

El sufijo `(exp. Ns)` cuenta regresivamente los segundos hasta el próximo intento; una vez que cruza a cero muestra brevemente `(exp. Ns ago)` antes de que se dispare el reintento. Contra un proveedor en vivo la columna `Status` muestra `Registered` con los segundos restantes hasta la próxima actualización. `Rejected` (o `Unregistered`) significa que el proveedor no aceptó el inicio de sesión — activa `pjsip set logger on` y lee la respuesta `401`/`403`, casi siempre un nombre de usuario, contraseña o dominio `client_uri` incorrectos.

## Troncales basados en IP (estáticos)

El segundo modelo no necesita registro alguno. El proveedor conoce su dirección IP pública y envía las llamadas directamente a ella; usted, a su vez, envía llamadas a la IP de señalización conocida del proveedor. La autenticación se realiza por **dirección IP de origen**, no por credenciales SIP. Esto es típico para troncales entre dos servidores que usted controla, o para una troncal empresarial donde ambos lados tienen direcciones estáticas.

El objeto clave es `identify`. Le dice a Asterisk: “cualquier solicitud SIP que llegue de *esta* IP pertenece a *ese* endpoint.” Sin él, PJSIP intenta emparejar una solicitud entrante a un endpoint por el usuario `From`, lo cual el tráfico de un carrier no satisfará — por lo que la llamada sería rechazada o caería al endpoint `anonymous`.

Una troncal estática elimina el objeto `registration` y agrega `identify`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
```

`match` acepta una dirección IP, un rango CIDR o un nombre de host. **Los nombres de host se resuelven una sola vez, al cargar la configuración**, así que si la IP de su proveedor cambia debe recargar. Para un carrier que publica varios gateways de medios, enumere cada IP de señalización — puede repetir `match` o dar un CIDR:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Verifique lo que Asterisk aceptará con `pjsip show identifies`. Capturado del
laboratorio (la línea `sipp-identify` es el endpoint SIPp preexistente del laboratorio):

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### La implicación de seguridad

Una troncal basada en IP sin autenticación es una puerta, y `identify`/`match` es la
única cerradura. Si `match` un rango demasiado amplio — o si un atacante puede falsificar una IP de origen — las llamadas llegan a su contexto `from-pstn` sin autenticación. Dos defensas,
usadas juntas:

- **Empareje lo más estrechamente posible.** Prefiera IPs de host específicas sobre CIDR amplios. Sólo las IPs reales de señalización del proveedor pertenecen a `match`.
- **Combínela con una ACL.** PJSIP puede descartar tráfico en la capa SIP antes de que llegue a un endpoint, usando un objeto `type=acl` (o `acl.conf`):

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Una sección `type=acl` no necesita referencia: `res_pjsip_acl` aplica cada uno de esos
objetos a *todo* el tráfico SIP entrante antes de que alcance cualquier endpoint. (Las opciones `acl` y `contact_acl` del objeto extraen listas de reglas nombradas de `acl.conf`
en lugar de listar `permit`/`deny` en línea como arriba.) El principio es el mismo
del capítulo SIP: denegar todo, luego permitir sólo lo que confía. Y
cualquiera que sea el contexto de su troncal,
**nunca lo deje alcanzar un contexto que pueda marcar de vuelta a la PSTN** sin una
regla deliberada y autenticada — ese es el clásico agujero de fraude de tarifas.

> **¿Qué modelo debo usar?** Si el proveedor le brinda un nombre de usuario y una contraseña,
> use una troncal de **registro**. Si le piden su dirección IP y le dan la
> suya, use una troncal de **identificación**. Algunos proveedores soportan ambos; muchas troncales reales combinan un registro (para que el proveedor pueda encontrarlo) con una identificación (para que los INVITE entrantes de los gateways de medios del proveedor se emparejen incluso cuando lleguen desde una IP distinta al registrador).

## Enrutamiento entrante y manejo de DID

Una vez que llegan las llamadas entrantes, aterrizan en el `context` del endpoint — aquí `from-pstn`. Un **DID** (número de marcación directa entrante) es simplemente el número marcado que el proveedor le entrega en el URI de solicitud. Su tarea en el dialplan es asignar cada DID a un destino: una extensión única, un IVR, una cola o un grupo de timbre.

El número que envía el proveedor se compara como `${EXTEN}` en `from-pstn`. Cuánto de él ve depende del proveedor — algunos envían el número completo E.164 (`+4830001000`), otros envían el número nacional, y otros solo los últimos dígitos. Inspeccione una llamada entrante real con `pjsip set logger on` y observe el URI de solicitud antes de escribir los patrones.

### Un DID a una extensión

El caso más simple — un solo DID enrutado directamente a un teléfono:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### Un DID a un IVR (asistente automático)

Un número principal que debe contestar con un menú en lugar de sonar un teléfono:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` es el contexto de asistente automático que construyó en los capítulos del dialplan (`Background()` + `WaitExten()`). Enrutar el DID es solo un `Goto`.

### Un DID a una cola

Una línea de soporte que debe aterrizar en una cola de llamadas:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Muchos DIDs a la vez

Cuando compra un bloque de números, un patrón mantiene pequeño el dialplan. Suponga que su rango de DID es `4830003000`–`4830003099` y el proveedor envía el número completo; asigne los últimos dos dígitos de cada DID a la extensión `60xx`:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` toma los últimos dos dígitos (el desplazamiento negativo cuenta desde la derecha), de modo que `4830003007` suena `PJSIP/6007`. Una tabla de búsqueda `did => extension` construida con `GoSub` o una base de datos de Asterisk (`AstDB`/`func_odbc`) escala aún más, pero para un puñado de números los patrones explícitos son los más claros.

> **Capture el DID no coincidente.** Añada una extensión `i` (inválida) a `from-pstn` para que un número entrante mal enroutado reproduzca un anuncio o haga sonar al operador en lugar de descartarse silenciosamente:
> 
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Enrutamiento saliente, identificador de llamada y E.164

Las llamadas salientes fluyen en sentido contrario: un teléfono interno marca un número, su dialplan lo coincide, elimina cualquier prefijo de acceso, establece el identificador de llamada que el proveedor espera y entrega la llamada al punto final del trunk con `Dial(PJSIP/<number>@itsp)`.

### Envío de la llamada al trunk

La sintaxis del canal para un trunk es `PJSIP/<number>@<endpoint>`: la parte antes del `@` se convierte en la porción de usuario del URI de solicitud saliente, y la parte después del `@` nombra el punto final cuyo `aor` `contact` suministra el host de destino. Una regla clásica de “marcar 9 para una línea externa”:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` elimina el código de acceso `9` inicial antes de que se envíe el número. El patrón `_9NXXXXXXXXX` coincide con `9` más un número de 10 dígitos cuyo primer dígito es 2–9; ajústelo a su plan de marcación.

### Identificador de llamada en llamadas salientes

La mayoría de los ITSP ignoran — o rechazan activamente — un identificador de llamada que no sea un número que usted posea. Establezca el número de identificador de llamada saliente a uno de sus DIDs con la función `CALLERID(num)` antes de `Dial()`, como se muestra arriba. También puede establecer el nombre:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

Si el proveedor aún elimina o sobrescribe el nombre de su identificador de llamada, esa es su política — muchos operadores obtienen el nombre mostrado de su propia base de datos CNAM basada en el número, no de su encabezado `From`.

Dos opciones del punto final interactúan con esto:

- **`from_user`** establece la parte de usuario del encabezado `From` a nivel SIP, que algunos proveedores usan para identificar su cuenta sin importar `CALLERID(num)`.
- **`trust_id_outbound`** (valor predeterminado `no`) controla si Asterisk enviará encabezados de identidad sensibles a la privacidad (`P-Asserted-Identity`/`P-Preferred-Identity`) en la salida. Déjelo desactivado a menos que su proveedor documente que desea PAI, en cuyo caso configure `trust_id_outbound=yes` y `send_pai=yes`.

### Normalización a E.164

E.164 es el formato internacional de número: un `+` inicial, código de país, luego el número nacional, sin espacios ni puntuación (por ejemplo `+5548999990000` o `+14155550100`). Cada vez más los operadores esperan — o requieren — E.164 en el trunk. En lugar de dispersar el formateo a lo largo del dialplan, normalice una sola vez en el contexto saliente.

Un ejemplo norteamericano que acepta un número local de 10 dígitos, un número prefijado con `1` de 11 dígitos, o un número ya en formato E.164, y siempre presenta `+1…` al trunk:

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

Algunos proveedores quieren el `+`; otros quieren solo los dígitos. Si el suyo rechaza el `+`, elimínelo al salir con `${EXTEN:1}` en el `Dial`. La idea es que todo el conocimiento del formato viva en un solo lugar, de modo que cambiar de proveedor — o agregar un segundo — sea un cambio de una sola línea.

## Failover y enrutamiento de menor costo

Con una troncal, una caída del proveedor significa que no hay llamadas salientes. Con dos o más, puedes conmutar automáticamente y hasta elegir la ruta más barata por destino — *enrutamiento de menor costo* (LCR).

### Failover con `${DIALSTATUS}`

`Dial()` establece la variable de canal `${DIALSTATUS}` cuando regresa. Los valores que te importan para el failover son `CHANUNAVAIL` (la troncal no pudo ser alcanzada en absoluto) y `CONGESTION` (la llamada fue rechazada, p. ej. todos los circuitos ocupados). Prueba la troncal primaria; si no pudo transportar la llamada, pasa a la de respaldo:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Observa la elección deliberada **no** de hacer failover en `BUSY` o `NOANSWER` — esos indican que la *parte llamada* fue alcanzada y rechazó, por lo que volver a intentar en otra troncal haría sonar de nuevo un teléfono que ya dijo que no (y podría costarte una segunda llamada). Sólo redirige cuando la *troncal misma* falló.

### Una subrutina de enrutamiento reutilizable

Repetir esa lógica para cada patrón de marcación es propenso a errores. Factorízala en una rutina `GoSub` que tome el número de destino y pruebe cada troncal en orden:

```
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

Ahora cada patrón saliente es una llamada `GoSub`, y el orden de las troncales se define en un solo lugar.

### Enrutamiento de menor costo por destino

El LCR verdadero elige la troncal según a dónde va la llamada. Una forma común es coincidir el prefijo del destino y enviar cada clase de llamada al proveedor que sea más barato para ella — por ejemplo, llamadas internacionales a un carrier mayorista y llamadas locales/nacionales a tu troncal primaria:

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

Para más de unos pocos prefijos, almacena la tabla de rutas en una base de datos (`func_odbc`/`AstDB`) y busca la troncal por prefijo en lugar de codificar los patrones. El dialplan permanece pequeño y las tarifas viven en una tabla que puedes editar sin recargar la lógica.

## NAT y trunks

NAT es la causa más común de problemas con trunks — típicamente audio unidireccional,
o un trunk que se registra pero nunca recibe llamadas entrantes. La causa es la misma
que para los teléfonos (cubierta en *SIP & PJSIP in depth* y *Designing a VoIP network*):
Asterisk anuncia su propia idea de su dirección en SIP y SDP, y detrás de NAT
esa es una dirección privada RFC 1918 que el proveedor no puede enrutar de regreso.

Para los trunks la solución tiene dos partes — configuraciones en el **transport** (su
dirección pública) y configuraciones en el **endpoint** (cómo tratar los medios del
proveedor).

### En el transport — su dirección pública

Cuando el servidor Asterisk está detrás de NAT (una nube o una caja on‑prem con una
IP privada y una IP pública 1:1), indique al transport su dirección pública y qué
redes son locales. Estas opciones se establecen una sola vez, en el `transport`, y se aplican a
todo el tráfico sobre él:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** — la IP pública que Asterisk escribe en los encabezados SIP
  (`Via`, `Contact`) para destinos fuera de `local_net`.
- **`external_media_address`** — la IP pública que Asterisk escribe en la línea SDP `c=`
  para que RTP regrese al lugar correcto. Normalmente idéntica a la dirección de señalización.
- **`local_net`** — redes que Asterisk trata como internas, de modo que *no* reescribe
  direcciones para pares LAN. Liste cada subred interna.

### En el endpoint — los medios del proveedor

La otra mitad maneja un proveedor que también está detrás de NAT, o que simplemente envía
medios desde una dirección distinta a la que aparece en su SDP. Establezca estos por
endpoint de trunk:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** — mantener los medios fluyendo a través de Asterisk en lugar de permitir
  que las dos piernas hablen directamente. Esencial a través de NAT, y necesario de todos
  modos si desea grabar, transcodificar o monitorear la llamada.
- **`rtp_symmetric=yes`** — el comportamiento clásico *comedia*: enviar RTP de regreso a la
  dirección de la que realmente provino el medio, no a la dirección que reclama el SDP.
- **`force_rport=yes`** — responder a SIP desde la IP/puerto de origen de la solicitud
  (RFC 3581), en lugar de confiar en el encabezado `Via`.
- **`rewrite_contact=yes`** — en mensajes SIP entrantes de este endpoint, reescribir
  el encabezado `Contact` (o un encabezado `Record-Route` apropiado) a la dirección IP
  de origen y puerto de donde realmente llegó el paquete. Según la propia
  documentación de la opción, esto "ayuda a los servidores a comunicarse con endpoints que están detrás
  de NATs" y "ayuda a reutilizar conexiones de transporte confiables como TCP y TLS."

> **Recomendación — teléfonos vs trunks.** `rewrite_contact` es casi siempre la
> opción correcta para teléfonos, porque su contacto anunciado suele ser una dirección privada
> RFC 1918 que no es enrutable de regreso a ellos. En un trunk basado en IP estática,
> el contacto del proveedor suele ya ser una dirección pública correcta, por lo que reescribirlo
> a menudo es innecesario; algunos operadores prefieren dejarlo desactivado allí y habilitarlo
> solo para trunks de registro y teléfonos con NAT. El efecto documentado de la
> opción es puramente la reescritura inbound `Contact`/`Record-Route` anterior — así que la
> práctica segura es probar con su carrier específico antes de activarla en un
> trunk estático.

Puede confirmar la configuración efectiva en cualquier endpoint con
`pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`,
`rewrite_contact`, y el resto se imprimen todos en el volcado de parámetros.

## Laboratorio — un ITSP simulado con un segundo Asterisk y SIPp

No necesita un trunk de pago para practicar. El laboratorio del libro ya ejecuta un contenedor Asterisk
22.10.0 y un contenedor SIPp en una red privada `172.30.0.0/24`; trataremos el contenedor SIPp como el "carrier" que realiza llamadas entrantes, y añadiremos un
endpoint de trunk que dirige esas llamadas a un contexto `from-pstn`.

![Un trunk SIP entre el PBX Asterisk y el ITSP: el PBX se registra como una cuenta, las llamadas salientes marcan `PJSIP/<num>@trunk`, y las llamadas entrantes llegan al contexto `from-pstn`.](../images/09-sip-trunking-fig01.png)

### 1. Añadir el endpoint del trunk

Añada un trunk basado en IP a `lab/asterisk/etc/pjsip.conf` que coincida con el host SIPp del laboratorio
y dirija las llamadas entrantes a `from-pstn`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. Enrutar el DID entrante

En `lab/asterisk/etc/extensions.conf`, añada un contexto `from-pstn` que conteste el
DID que marcará el carrier simulado y lo reproduzca, luego añada una regla saliente:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

Recargue ambos archivos (`core reload`) y verifique que el trunk se haya cargado:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Realizar una llamada entrante a través del trunk

Apunte un escenario SIPp al PBX con el DID como usuario objetivo. El laboratorio ya
incluye `lab/sipp/uac_9000.xml`, que INVITEa la extensión `9000`; cópielo a
`uac_did.xml` y cambie el request-URI/usuario `To` de `9000` a `4830001000`,
luego ejecútelo desde el contenedor SIPp:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Observe cómo la llamada llega a `from-pstn` en la consola de Asterisk (`pjsip set logger on`
muestra el INVITE entrante; `core show channels` muestra el canal `PJSIP/itsp-…`
reproduciendo `demo-congrats`). Como la IP de origen SIPp coincide con el `identify`,
la llamada se acepta sin autenticación — exactamente como se comporta un trunk de carrier estático.

### 4. Inspeccionar el trunk

Capture la configuración completa del trunk para sus notas:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Opcional) convertirlo en un trunk de registro

Levante el *segundo* contenedor Asterisk como un registrador real: asigne un
`endpoint`+`auth`+`aor` para la cuenta `4830001000`, luego en el PBX reemplace el
bloque `identify` por el bloque `registration` del inicio de este capítulo
(apuntando `server_uri` a la IP del segundo contenedor). Confirme con
`pjsip show registrations` que el estado muestre `Registered`, y luego realice una llamada
en cada dirección.

## Resumen

Un trunk SIP conecta su PBX al mundo exterior, y en PJSIP es simplemente un
endpoint construido a partir de la misma familia `endpoint` + `auth` + `aor` que ya conoce,
más un `identify` o un `registration`. Use un **trunk de registro**
(`type=registration` con `outbound_auth`) cuando el proveedor le proporciona un nombre de usuario
y una contraseña; use un **trunk basado en IP** (`type=identify` con `match`) cuando
la autenticación sea por IP de origen — y asegure este último con un `match`
estrecho y un `acl`, porque un trunk no autenticado es un objetivo de fraude de tarifas. Entrante,
el DID del proveedor llega como `${EXTEN}` en su contexto `from-pstn`, donde lo
encamina a una extensión, a un IVR o a una cola — los patrones y `${EXTEN:-N}` mantienen
los bloques de DID compactos. Saliente, configure `CALLERID(num)` a un número que posea, normalice
a E.164 en un solo lugar, y entregue la llamada a `PJSIP/<number>@trunk`. Construya
resiliencia intentando múltiples trunks y ramificando en `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` significan reencaminar; `BUSY`/`NOANSWER` no lo hacen), y coloque
el enrutamiento de menor costo en una tabla `GoSub`. Finalmente, NAT para trunks es bidireccional:
`external_media_address`/`external_signaling_address`/`local_net` en el
**transport** para su dirección pública, y `direct_media=no`, `rtp_symmetric`,
`force_rport` y `rewrite_contact` en el **endpoint** para los medios del proveedor.

## Cuestionario

1. En PJSIP, las credenciales usadas para autenticar una llamada *saliente* o
   registro a un proveedor se hacen referencia con:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Debe usar un tronco `type=registration` cuando:
   - A. El proveedor lo identifica por su dirección IP de origen.
   - B. El proveedor le da un nombre de usuario y contraseña y espera que inicie sesión.
   - C. Nunca quiere que Asterisk envíe un `REGISTER`.
   - D. El tronco está entre dos servidores con IP estática que usted controla.
3. La opción `match` del objeto `identify` acepta (elija todas las que correspondan):
   - A. Una dirección IP
   - B. Un rango CIDR
   - C. Un nombre de host (resuelto al cargar la configuración)
   - D. Sólo un nombre de usuario SIP
4. En Asterisk 22, `auth_type=userpass` es:
   - A. El único valor válido
   - B. Obsoleto y convertido a `digest`
   - C. Eliminado y provoca un error de carga
   - D. Requerido para registro saliente
5. Un número DID entrante llega al dialplan como:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` en el `context` del endpoint del tronco
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Para enviar los dos últimos dígitos del DID marcado `4830003007` a una extensión,
   usaría:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Después de `Dial()` a un tronco, debe cambiar a un tronco de respaldo en el que
   los valores `${DIALSTATUS}` (elija dos)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Para establecer el número de identificación de llamada presentado al proveedor antes de marcar, use:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. Las opciones que indican a Asterisk su dirección *pública* cuando el servidor está detrás de
   NAT se configuran en:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` en un endpoint de tronco hace que Asterisk:
    - A. Encripte RTP con SRTP
    - B. Envíe RTP de vuelta a la dirección desde la que realmente llegó el medio, ignorando el SDP
    - C. Desactive RTP por completo
    - D. Fuerce medios directos entre endpoints

**Respuestas:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
