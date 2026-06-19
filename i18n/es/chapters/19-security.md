# Seguridad en Asterisk

Desde el principio, el tema de la seguridad en Asterisk ha sido crítico. SIP, Session Initiation Protocol, es el protocolo más atacado en Internet según CERT.BR. Cualquier persona que ejecute un honeypot puede confirmarlo. El problema del fraude de ingresos compartidos por Internet (Internet Revenue Share Fraud) es muy serio y puede llevar a pérdidas superiores a cientos de miles de dólares. Nunca debe instalar un servidor Asterisk conectado a Internet sin la seguridad adecuada. En este capítulo, aprenderá a identificar los principales tipos de ataques que puede recibir y cómo prevenirlos mediante una política de seguridad adecuada. Por último, pero no menos importante, aprenderá a implementar la política de seguridad sugerida.

Este capítulo está dirigido a **Asterisk 22 LTS**, donde PJSIP (`res_pjsip` / `chan_pjsip`) es el único canal SIP. (El antiguo controlador `chan_sip` fue eliminado en Asterisk 21; consulte el capítulo *Legacy Channels* si está migrando un sistema antiguo). Una consecuencia relevante para la seguridad: las autenticaciones fallidas ahora se emiten a través del **marco de eventos de seguridad** de Asterisk y el canal de registro dedicado `security`, lo que cambia la forma en que se configura Fail2Ban (se trata más adelante en este capítulo).

## Objetivos

Al final de este capítulo, usted debería ser capaz de:

- Identificar los principales tipos de ataques realizados frecuentemente a servidores Asterisk
- Definir una política de seguridad efectiva
- Implementar la política de seguridad
- Instalar y configurar IPTABLES para Asterisk
- Instalar y configurar Fail2Ban para Asterisk
- Instalar y configurar TLS y SRTP para cifrado

## Principales ataques a la telefonía IP

Los principales ataques a la telefonía IP pueden clasificarse como DOS/DDOS, robo de servicio/fraude telefónico (Toll Fraud) y escuchas ilegales (Eavesdropping). Algunos de los nombres pueden ser confusos y diferentes fuentes a veces tienen nombres distintos para el mismo ataque. Robo de servicio, fraude telefónico, fraude de ingresos compartidos por Internet, fraude telefónico son nombres diferentes para hackers que utilizan su PBX para dirigir tráfico a un número de tarifa premium y obtener reembolsos del proveedor.

### DDoS/DOS

La denegación de servicio (Denial of Service) y la denegación de servicio distribuida (Distributed Denial of Service) son ataques populares contra cualquier infraestructura de TI. No es diferente con SIP y otros protocolos de voz sobre IP. La denegación de servicio distribuida suele ser perpetrada por una botnet, mientras que el DOS es realizado por una sola computadora. En febrero de 2011, la botnet Sality llevó a cabo un escaneo sigiloso y coordinado de todo el espacio de direcciones IPv4 buscando servidores SIP vulnerables; los investigadores que observaron el telescopio de red de la UCSD lo atribuyeron a aproximadamente tres millones de IPs de origen distintas que sondeaban el puerto UDP 5060, muy probablemente para realizar ataques de fuerza bruta a cuentas SIP para fraude telefónico.[^sality]

[^sality]: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![Una botnet peer-to-peer dirigiendo miles de intentos de registro SIP a un servidor](../images/19-security-fig01.png)

El DOS se aplica generalmente mediante técnicas como fuzzing y flooding. El flooding puede utilizar SIP, IAX, RTP y otros protocolos. Pueden detener el servicio por completo o degradar la calidad de la voz. Son muy difíciles de mitigar si los puertos están abiertos a Internet. A continuación, se muestran algunas de las herramientas utilizadas por los atacantes:

**Fuzzing:**

- **PROTOS Test Suite (c07-sip)** — de la OUSPG de la Universidad de Oulu. Envía miles de paquetes malformados para provocar un mal funcionamiento, como un desbordamiento de búfer que detiene el software.
- **Voiper** — genera más de 200,000 pruebas que cubren todos los atributos SIP y verifica si su servidor puede procesar los mensajes de manera efectiva. <http://voiper.sourceforge.net/>

**Flooding:**

- **INVITE Flooder** — inunda el servidor con solicitudes SIP INVITE. <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — inunda el servidor con tráfico IAX2. <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — inunda sesiones multimedia activas con paquetes RTP para degradar la calidad de la voz. <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### Técnicas de mitigación para DoS/DDoS

Mis recomendaciones son:

1. No exponga su servidor Asterisk a Internet, a menos que sea necesario con la protección adecuada (SBC). 2. En la red interna, utilice una VLAN para voz, principalmente si se encuentra en una universidad o colegio donde el número de usuarios es alto. 3. Utilice VPN o TLS para el acceso externo.

### Fraude de ingresos compartidos por Internet

Este fraude es un poco complicado de entender. La clave es comprender el concepto de número internacional de tarifa premium (IPRN).

![Los tres pasos del fraude de ingresos compartidos por Internet: comprar un número de tarifa premium, encontrar un dispositivo VoIP vulnerable y llamar al número, luego cobrar el pago](../images/19-security-fig02.png)

Un IPRN es un número que puede asignar de forma gratuita en algunas compañías telefónicas de Internet específicas. Busque proveedores de números de tarifa premium de Internet y encontrará muchos de ellos. En este tipo de operador puede asignar, por ejemplo, un número en una red satelital como Iridium, un destino que cuesta decenas de dólares por minuto al llamante. El proveedor de IPRN le devolverá un porcentaje de los ingresos (10 al 20% de los ingresos) por cada minuto recibido.

![Una lista de precios de un proveedor de IPRN que muestra las tasas de pago por país y números de prueba](../images/19-security-fig03.png)

Después de la fase de asignación, el hacker intenta encontrar cualquier servidor Asterisk abierto capaz de marcar el IPRN asignado. La PBX de la víctima, controlada por el hacker, realizará cientos de llamadas al número IPRN, generando un gran reembolso para el hacker y una factura telefónica enorme para la víctima. Muchas veces, superior a cientos de miles de dólares en un solo fin de semana. Principales herramientas utilizadas por los hackers para atacar una PBX: 1. SIPVicious: http://code.google.com/p/sipvicious/. Sipvicious es un conjunto de herramientas de seguridad fácil de usar. Su objetivo principal es reconocer PBXs vulnerables y descifrar las contraseñas SIP mediante un ataque de fuerza bruta. La herramienta más utilizada es svcrack. La herramienta es capaz de probar miles de contraseñas por segundo. 2. Vulnerabilidades del teléfono. Otro punto utilizado frecuentemente por los hackers como vector de ataque es el propio teléfono. Muchas personas que instalan Asterisk no cambian la contraseña predeterminada en la interfaz web del teléfono. Una vez que estos teléfonos están abiertos en Internet, los hackers pueden intentar usar la contraseña de interfaz predeterminada para descargar la configuración, donde a menudo pueden encontrar la contraseña secreta SIP.

#### Robo por TFTP:

Si está utilizando el aprovisionamiento automático de teléfonos mediante TFTP, probablemente esté abierto a este tipo de ataque. TFTP es una forma simple e insegura de protocolo de transferencia de archivos.

![Un atacante descargando archivos .cfg adivinables desde un servidor TFTP, recolectando credenciales en texto plano de los archivos de configuración](../images/19-security-fig04.png)

El nombre de los archivos de configuración es fácilmente adivinable utilizando la dirección MAC seguida de .cfg (por ejemplo, 001A2B3C4D5E.cfg). Un hacker inteligente puede crear fácilmente una utilidad para probar todas las direcciones MAC secuencialmente o simplemente descargar una herramienta para hacerlo. El archivo de configuración suele estar sin cifrar y contiene la contraseña secreta SIP en su interior.

#### Mitigación para ataques de fuerza bruta y robo por TFTP

Para mitigar estos ataques, puede aplicar las soluciones a continuación. Fuerza bruta: La mejor solución para mitigar los ataques de fuerza bruta es prevenir intentos no autorizados secuenciales. Casi cualquier instalador de Asterisk utiliza la utilidad fail2ban para esto. Cuando fail2ban detecta múltiples intentos con la contraseña o el nombre de usuario incorrectos, bloquea la IP del atacante durante un cierto período de tiempo. La segunda medida contra la fuerza bruta es utilizar contraseñas seguras, de más de 12 caracteres, con al menos un carácter especial. Robo por TFTP: Para prevenir el robo por TFTP, configure el aprovisionamiento para usar https con nombre de usuario y contraseña. El archivo se transmite cifrado y un nombre de usuario y contraseña impiden que los atacantes intenten descargar archivos.

### Escuchas ilegales (Eavesdropping)

No vemos muchos de estos tipos de ataques porque en la mayoría de los casos simplemente no se detectan. Las escuchas ilegales son muy difíciles de detectar en un entorno IP. Utilidades como UCsniff, disponibles gratuitamente, son capaces de escuchar una llamada VoIP en la mayoría de las redes. La técnica principal es utilizar suplantación de ARP (ARP spoofing) para forzar el tráfico a través de la computadora que ejecuta UCsniff y grabar las llamadas.

#### Mitigación para escuchas ilegales

Puede prevenir las escuchas ilegales cifrando su tráfico VoIP. La otra forma es prevenir ataques de hombre en el medio (MITM) en su red. La inspección ARP es muy efectiva para prevenir MITM en redes de capa 2. Consulte con su soporte técnico de red para entender cómo implementarlo. Más adelante en este libro aprenderemos cómo instalar el cifrado basado en TLS y SRTP. También puede usar ARPWatch para descubrir si alguien está abusando del protocolo ARP para atacar su red.

## Política de seguridad para Asterisk

La mejor manera de implementar la seguridad es crear una política de seguridad. Para este entrenamiento, sugeriré una política de seguridad para la mayoría de las instalaciones de Asterisk. Úsela como punto de partida base y cámbiela según sus necesidades. La política de seguridad sugerida sigue a continuación: 1. No dejar puertos UDP/TCP innecesarios abiertos. 2. No dejar acceso a ninguna interfaz administrativa (SSH/HTTPS) abierto en Internet. 3. Para acceder a SSH y/o HTTP/HTTPS, debe haber excepciones explícitas en el firewall IPTABLES. 4. Contraseñas seguras con 12 caracteres y al menos un carácter especial. 5. Bloquear direcciones IP que fallen más de 10 veces en la autenticación usando Fail2ban. 6. Confirmación de contraseña para llamadas internacionales. 7. Limitar el acceso al puerto SIP a su rango conocido de direcciones IP. Si requiere tener acceso externo a su PBX, hay dos posibilidades. Utilice un SBC (Session Border Controller) para proteger su servidor contra DOS/DDOS o utilice una VPN siempre que desee acceso externo. Si deja el puerto 5060 abierto en Internet sin un SBC o VPN, está expuesto a un ataque DOS/DDOS. El riesgo es suyo.

### Endurecimiento en la era PJSIP (Asterisk 22)

Más allá del firewall y Fail2Ban, la pila PJSIP de Asterisk 22 proporciona varios controles a nivel de configuración que deberían ser parte de su política de seguridad. Estos complementan (no reemplazan) los controles de red anteriores:

- **Autenticación por endpoint.** Cada endpoint debe hacer referencia a una sección dedicada `type=auth` con un `password` fuerte y único (`auth_type=digest`). Nunca reutilice credenciales entre endpoints.
- **Manejo de llamadas anónimas integrado.** PJSIP no revela si un nombre de usuario existe cuando la autenticación falla. Para aceptar llamadas anónimas, debe crear explícitamente un endpoint llamado `anonymous` y usar secciones `type=identify` (coincidiendo con la IP de origen) para asignar pares conocidos a endpoints. Si no desea llamadas anónimas, simplemente no cree un endpoint `anonymous`, y las solicitudes no coincidentes serán desafiadas/rechazadas.
- **ACLs.** Restrinja quién puede llegar a un endpoint con ACLs nombradas `/etc/asterisk/acl.conf`, referenciadas desde el endpoint con `acl=` (ACL de señalización/origen) y `contact_acl=` (restringe la dirección de contacto/registro). También puede establecer permit/deny directamente en el endpoint.
- **`qualify`.** Establezca `qualify_frequency` (y `qualify_timeout`) en el AOR para que Asterisk monitoree activamente la alcanzabilidad de los contactos registrados y elimine los que no responden.
- **Endurecimiento de transporte PJSIP / Protección DoS.** El `type=transport` no expone un límite de cliente por transporte, por lo que la protección contra inundación de conexiones proviene del firewall (las reglas de iptables/Fail2Ban en este capítulo) en lugar de una opción de PJSIP. Lo que el transporte *sí* le da es ajuste de TCP keep-alive (`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`) para eliminar conexiones muertas/semiabiertas, y configuraciones `local_net`/`external_*` para un manejo correcto de NAT. Combínelos con las reglas del firewall para mitigar ataques de inundación de conexiones.
- **TLS + SRTP para medios.** Cifre la señalización con un transporte TLS y los medios con `media_encryption=sdes` (o `dtls` para WebRTC) en el endpoint — cubierto más adelante en este capítulo.
- **Control de acceso AMI/ARI.** Restrinja la interfaz de gestión de Asterisk (`manager.conf`) y ARI (`ari.conf` / `http.conf`) a localhost o a una red de gestión confiable, use secretos únicos fuertes, vincule el servidor HTTP a una interfaz privada y nunca los exponga a Internet.

Todos los nombres de opciones anteriores están confirmados para Asterisk 22.10: la sección `type=transport` expone `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net` y la familia `external_*`, pero **no** tiene una opción `max_clients` — la protección contra inundación de conexiones proviene del firewall, no del transporte. Las opciones de endpoint `acl` y `contact_acl` toman nombres de sección de `acl.conf`, y la coincidencia de IP de origen para pares no autenticados se realiza con secciones `type=identify` (`match=`).

### Eliminación de puertos innecesarios

En lugar de descubrir todas las vulnerabilidades asociadas con todos los protocolos de Asterisk, simplifiquemos el problema eliminando los puertos innecesarios. Para listar todos los puertos abiertos por el servidor Asterisk, utilice:

```
netstat –pantu |grep asterisk
```

El resultado del comando se muestra a continuación.

![Salida de netstat mostrando los muchos puertos vinculados por Asterisk, incluyendo 4569 (IAX) y 2727 (MGCP)](../images/19-security-fig05.png)

Si observa la salida, descubrirá que hay muchos puertos abiertos. ¿Los necesitamos? No necesariamente, 2727 es el protocolo MGCP (chan_mgcp), 4569 es el IAX (chan_iax2). Si no está utilizando estos protocolos, puede simplemente eliminar el módulo en el archivo de configuración modules.conf.

Puede notar que Asterisk se vincula a un puerto UDP de número alto. Esto proviene del resolvedor de `res_pjsip` realizando consultas DNS salientes (el puerto de origen es efímero, como cualquier búsqueda DNS de cliente), no de un oyente entrante; su firewall solo necesita permitir tráfico de retorno **establecido/relacionado** para ello (la regla de iptables `conntrack ESTABLISHED,RELATED` que se muestra a continuación ya cubre esto). **No** necesita abrir un rango amplio de puertos UDP altos entrantes solo para el DNS de PJSIP.

Para eliminar los puertos innecesarios, deshabilite los módulos que no utiliza. Edite el archivo modules.conf y agregue líneas `noload` para los canales y protocolos que no está utilizando. **No** haga noload de `res_pjsip`, `res_pjproject` o `chan_pjsip`; esos son necesarios para SIP en Asterisk 22:

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 — keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(En Asterisk 22 ya no necesita hacer noload de `chan_mgcp` o `chan_skinny`; esos controladores fueron *eliminados* en Asterisk 21 y no son parte de una compilación estándar de 22). Con las instrucciones anteriores, he eliminado todos los canales innecesarios manteniendo solo PJSIP. Puede elegir los módulos de protocolo que desee, simplemente elimine los que no use. El resultado se muestra en la captura de pantalla a continuación: solo el puerto SIP (5060) vinculado por su transporte PJSIP está ahora expuesto como entrante.

![Salida de netstat después de deshabilitar los módulos no utilizados: solo el puerto UDP 5060 permanece vinculado por Asterisk](../images/19-security-fig06.png)

### Implementación de la política de seguridad con IPTABLES

IPTABLES o netfilter es un firewall estándar presente en la mayoría de las distribuciones de Linux. En este laboratorio configuraremos iptables y fail2ban. El objetivo es implementar la política de seguridad recomendada para Asterisk y bloquear todo el tráfico innecesario. Siga los pasos a continuación: 1 – Bloquear todo el tráfico externo. 2 – Permitir tráfico SSH desde una red interna o un solo host. 3 – Permitir tráfico SIP en UDP y TCP en los puertos 5060. 4 – Permitir tráfico RTP en el rango de puertos multimedia UDP. No hay un valor predeterminado único incorporado; el propio `rtp.conf` de Asterisk vuelve a los puertos 5000–31000 cuando no se establece nada, pero la configuración enviada `rtp.conf.sample` configura `rtpstart=10000` / `rtpend=20000`, por lo que usamos ese rango de ejemplo aquí. Haga coincidir su regla de firewall con cualquier `rtpstart`/`rtpend` que realmente haya establecido en `rtp.conf`. Asegúrese de tener acceso a la consola del servidor, no querrá bloquearse a sí mismo fuera del sistema. Tenga cuidado. Paso 1 - Instalar el paquete net-persistent.

```
sudo apt-get install iptables-persistent
```

Paso 2 - Permitir todo el tráfico desde el loopback

```
sudo iptables -I INPUT -i lo -j ACCEPT
sudo iptables -I OUTPUT -o lo -j ACCEPT
```

Paso 3 - Permitir conexiones establecidas

```
sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

Paso 4 - Permitir tráfico SSH/HTTPS desde la red 192.168.0.0

```
sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
NEW,ESTABLISHED -j ACCEPT
sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
NEW,ESTABLISHED -j ACCEPT
```

Paso 5 - Insertar las reglas de Asterisk

```
sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
```

Tenga en cuenta que el puerto 5061 (SIP sobre TLS) es **TCP**, no UDP. Las reglas anteriores abren 5060 tanto en UDP como en TCP y 5061 en TCP. Si solo ejecuta TLS, puede eliminar las reglas 5060 simples por completo. Solo abra los puertos a los que realmente se vinculan sus transportes PJSIP.

-I significa PREPEND (insertar al principio). Paso 6 - La última regla tiene que ser un drop (descarte)

```
sudo iptables -A INPUT -j DROP
```

-A significa APPEND (agregar al final). Nota: Tenga cuidado al mantener nuevas reglas, debe agregar reglas antes del DROP. Use PREPEND para nuevas reglas -I. Paso 7 - Guardar las reglas y reiniciar iptables

```
sudo iptables-save >/etc/iptables/rules.v4
sudo /etc/init.d/netfilter-persistent restart
```

### Uso de Fail2Ban para bloquear múltiples intentos fallidos de autenticación

Fail2Ban es casi un estándar para Asterisk. La mayoría de los usuarios lo implementan para mejorar la seguridad. Esta utilidad escanea los registros de Asterisk en busca de intentos fallidos y bloquea las direcciones IP de los atacantes. A continuación, proporciono las instrucciones para instalar Fail2Ban.

En Asterisk 22, PJSIP informa de las autenticaciones fallidas y otros eventos de seguridad a través del **marco de eventos de seguridad** de Asterisk, escrito en el **canal de registro `security` dedicado**. Para que Fail2Ban funcione, debe:

1. Habilitar el canal de seguridad en `/etc/asterisk/logger.conf`. La sintaxis es `<filename> => <levels>`, por lo que para enviar el nivel de seguridad a un archivo llamado `security` escriba:

```
[logfiles]
security => security
```

luego ejecute `logger reload` desde la CLI. Esto produce `/var/log/asterisk/security` con una línea por evento de seguridad, en la forma:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

Los eventos que le interesan a Fail2Ban son `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID` y `FailedACL`, cada uno con un campo `RemoteAddress="IPV4/UDP/<ip>/<port>"` que identifica al infractor. (Tenga en cuenta que la dirección está envuelta como `IPV4/UDP/.../...`, no como una IP desnuda; su filtro debe extraer el host de dentro de esa cadena).

2. Apunte la cárcel `asterisk` a ese archivo (`logpath = /var/log/asterisk/security`) y use un filtro que analice este formato de evento de seguridad.

Fail2Ban moderno incluye un filtro `asterisk` cuyo `failregex` ya coincide con los eventos anteriores y extrae `<HOST>` del campo `RemoteAddress`, por ejemplo:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

Las distribuciones de PBX (FreePBX/Sangoma) incluyen filtros equivalentes. Prefiera el filtro empaquetado sobre escribir uno a mano, ya que las cadenas de eventos exactas dependen de la versión. Una advertencia a tener en cuenta: un aviso ahora parcheado (GHSA-5743-x3p5-3rg7) mostró que el tráfico PJSIP manipulado podría inyectar líneas de registro falsas; mantenga actualizados tanto Asterisk como su filtro Fail2Ban.

A continuación, proporciono las instrucciones para instalar Fail2Ban. Paso 1 – Instalar fail2ban en Linux

```
sudo apt-get install fail2ban
```

Paso 2 - Activar fail2ban para Asterisk y SSH

```
sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
```

Agregue las siguientes líneas para activar fail2ban para ssh y asterisk

```
[sshd]
enabled = true
[asterisk]
enabled=true
```

Paso 3 - Reiniciar fail2ban

```
/etc/init.d/fail2ban restart
```

Paso 4 - Verificar. Cambie el secreto de su softphone e intente registrarse nuevamente 10 veces. Usando iptables -L, verifique si la dirección del softphone se incluyó como una dirección bloqueada. Paso 5 - Eliminar la dirección del bloqueo (suponga que la dirección es 192.168.0.5)

```
sudo fail2ban-client set asterisk unbanip 192.168.0.5
```

Nota: En el comando, reemplace 192.168.0.5 por la dirección IP de su teléfono.

### Implementación de TLS y SRTP

Dividiré esta sección en dos. En la primera parte cubriremos TLS para cifrar la señalización y en la segunda parte SRTP para cifrar los medios. El objetivo aquí es configurar Asterisk para estos recursos.

#### TLS

TLS (Transport Layer Security) es el mecanismo de cifrado definido para proteger la señalización SIP. Tipo de ataque Protección Ataques de señalización SÍ TLS asegura la integridad de los mensajes Hombre en el medio SÍ TLS verifica el certificado del servidor Escuchas ilegales NO TLS cifra la señalización, no los medios. Para el cifrado de medios (voz/video) utilice SRTP.

#### Certificados digitales autofirmados

Hay dos tipos de certificados que puede usar: autofirmados y comerciales. Los certificados autofirmados están firmados por su propio servidor, mientras que los certificados comerciales están firmados por una autoridad externa. Para VoIP, puede ser su propia autoridad de certificación. No hay necesidad de un certificado externo como GoDaddy y Verisign, este es un gasto innecesario. Generaremos nuestros propios certificados usando ast_tls_cert.

#### Configuración de TLS con certificados autofirmados

A continuación, se presenta una guía paso a paso sobre cómo implementar TLS. Primero generamos los certificados, luego configuramos el transporte TLS de PJSIP (consulte "Configuración de TLS con chan_pjsip") y finalmente apuntamos el softphone hacia él. Usaremos el SipPulse Softphone, que admite TLS y SRTP de forma nativa. (Cualquier softphone SIP capaz de TLS/SRTP funciona de la misma manera). Paso 1. Cree una clave RSA privada usando cifrado 3DES con una longitud de 4096 bits para nuestra autoridad de certificación. El comando a continuación, presente en /usr/src/asterisk-22.x.y/contrib/scripts, creará la Autoridad de Certificación y el Certificado de Asterisk. Como siempre, adapte las instrucciones si es necesario; las versiones cambian, los directorios cambian. Por favor, preste atención a lo que está haciendo. Use su dominio o dirección IP en la opción –C. El comando ast_tls_cert tiene tres opciones.

- -C nombre de host o dirección IP (he usado 192.168.0.74, la dirección IP de mi VM)
- -O Nombre de la organización
- -d Directorio donde almacenar las claves

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
/ast_tls_cert -C 192.168.0.74 -O "Asteriskguide" -d /etc/asterisk/keys
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
./ast_tls_cert
-C
192.168.0.74
-O
"AsteriskGuide"
-d
/etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 1024 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

No voy a generar un certificado de cliente porque no vamos a usar el certificado para autenticar al cliente. No se requiere que el cliente presente su propio certificado. Paso 2: Configure Asterisk para admitir a nuestro cliente sobre TLS. Esto se hace en `pjsip.conf` (un transporte TLS más la configuración del endpoint); la configuración completa se muestra en la siguiente sección, "Configuración de TLS con chan_pjsip". No estamos autenticando usando certificados, solo cifrando el tráfico.

Paso 3: Instale un softphone SIP capaz de TLS (el autor usa el SipPulse Softphone). Paso 4: Copie la autoridad de certificación a la computadora que ejecuta el softphone. Después de instalarlo, copie el archivo /etc/asterisk/keys/ca.crt a la computadora que ejecuta el softphone (use scp, o WinSCP en Windows) si está usando un certificado autofirmado. Paso 5: Cree la cuenta en el softphone. En la pantalla de cuenta, agregue la cuenta normalmente como cualquier otra cuenta sip. Use la contraseña correcta, la autenticación sigue basándose en la contraseña. Paso 6: Establezca TLS como el transporte en la configuración de la cuenta. En la pantalla de cuenta del SipPulse Softphone (a continuación), elija **TLS** como transporte y use el puerto 5061. Ajuste su firewall para abrir el puerto TCP 5061.

![La pantalla de cuenta del SipPulse Softphone: ingrese el servidor (su IP o dominio de Asterisk), nombre de usuario, contraseña y nombre para mostrar, luego elija el transporte (UDP, TCP o TLS).](../images/softphone/sipphone-account.png){width=35%}

Paso 7: Confíe en la autoridad de certificación. Si su certificado TLS de Asterisk está firmado por una CA pública (por ejemplo, Let's Encrypt; consulte el capítulo *Deployment*), un softphone moderno como el SipPulse Softphone confía en él automáticamente a través del almacén de certificados del sistema, sin importación manual. Si usa un certificado autofirmado, importe su CA (`/etc/asterisk/keys/ca.crt`) al cliente o al almacén de confianza del sistema operativo, o acéptelo cuando se le solicite.

Paso 8: **No** necesita un certificado de cliente. Un error común es pensar que cada teléfono necesita su propio certificado para autenticarse; no es así. En este punto, Asterisk solo *cifra* la sesión; la autenticación sigue siendo nombre de usuario y contraseña. Asterisk no verifica los certificados de cliente de forma predeterminada, por lo que no hay necesidad de distribuir un certificado por cliente.

Paso 9: Después de cambiar el certificado o el transporte, reinicie completamente el softphone (salga y vuelva a iniciar, no solo cierre la ventana) para que se vuelva a conectar a través del nuevo transporte.

### Configuración de TLS con chan_pjsip

Ahora aprendamos a configurar PJSIP para TLS. PJSIP es el único canal SIP en Asterisk 22, por lo que no hay nada que cambiar; solo asegúrese de que `res_pjsip`, `res_pjproject` y `chan_pjsip` estén cargados. Paso 1: Confirme que PJSIP esté habilitado en /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

Paso 2: Configure PJSIP para admitir TLS. Agregue una sección para el transporte TLS en el archivo /etc/asterisk/pjsip.conf

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Use `method=tlsv1_2` (o `tlsv1_3` si su compilación de OpenSSL/PJSIP lo admite); TLS 1.0/1.1 están obsoletos e inseguros y no deben usarse.

Paso 3: Configure el endpoint para blink. Edite el pjsip.conf y edite la sección para blink. Deje que pjsip elija automáticamente el transporte.

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

Paso 4: Verificación. Para verificar si el registro ocurrió sobre TLS, use el siguiente comando en la consola de Asterisk.

```
CLI>pjsip show aor blink
asterisk*CLI> pjsip show aor blink
      Aor:  <Aor..............................................>  <MaxContact>
    Contact:
```

- <Aor/ContactUri............................>

```
<Hash....>
<Status> <RTT(ms)..>
============================================================================
==============
      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual
nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
```

- contact
- :

```
sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 mailboxes            :
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 outbound_proxy       :
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
 voicemail_extension  :
```

### Realización de llamadas seguras usando SRTP

El protocolo responsable del cifrado de medios es el Secure Real Time Protocol (SRTP) definido en el RFC3711. Una de las deficiencias del protocolo es la falta de una forma estandarizada de intercambiar claves. Asterisk utiliza claves de intercambio SDES sobre el protocolo SDP protegido por el cifrado de señalización proporcionado por TLS. También existen otros métodos como MIKEY y ZRTP. ZRTP, desarrollado por Philipp Zimmermann, es uno de los métodos más sofisticados para el intercambio de claves y el cifrado de medios. Algunos softphones y teléfonos físicos permiten ZRTP. Sin embargo, la forma estándar sigue siendo SDES y encontrará este método en casi cualquier teléfono disponible en el mercado. A continuación, un ejemplo de una solicitud con las claves criptográficas definidas en el SDP en las líneas a=crypto:1 y a=crypto:2.

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### Configuración de SRTP en Asterisk

Configurar SRTP en Asterisk es muy simple. Establezca `media_encryption=sdes` en el endpoint; también puede requerirlo con `media_encryption_optimistic=no` para que los medios sin cifrar sean rechazados en lugar de permitirse silenciosamente. Tenga en cuenta que SDES requiere que la señalización se ejecute sobre TLS para que las claves no se envíen en texto plano. Paso 1: Configuración de Asterisk

Establezca lo siguiente en la sección `type=endpoint` en `pjsip.conf`:

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

Paso 2: Configuración del softphone

En el softphone, habilite SRTP para los medios de la cuenta (establezca la opción **SRTP (Media Encryption)** en *Mandatory*) para que la voz esté cifrada.

![La configuración de cuenta del SipPulse Softphone (sección inferior): establezca **Transport** en TLS y **SRTP (Media Encryption)** en *Mandatory* para que tanto la señalización como los medios estén cifrados.](../images/softphone/sipphone-config.png){width=35%}

## Habilitación de autenticación de dos vías para llamadas internacionales

A veces, la mejor manera es no tener rutas internacionales. Sin embargo, si realmente necesita marcar internacionalmente, use una contraseña adicional. Vamos a usar la aplicación vmauthenticate de Asterisk para solicitar la contraseña del correo de voz antes de marcar internacionalmente. Esto se configura en el dialplan en extensions.conf. Vea el ejemplo a continuación. Así, un hacker, incluso después de descubrir la contraseña de un par o comprometer un teléfono, todavía necesita la contraseña del correo de voz para marcar a este destino.

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` sigue siendo una aplicación estándar en Asterisk 22. El `Dial()` anterior enruta la llamada a través de un trunk SIP/PJSIP (`PJSIP/<number>@<trunk>`), que es como la mayoría de las instalaciones modernas llegan a la PSTN; adapte `my_trunk` al nombre de su propio trunk y use `DAHDI/g1/...` solo si realmente tiene un span DAHDI. La defensa contra el fraude telefónico en el dialplan (un segundo factor como este, combinado con la restricción de qué contextos pueden llegar a sus rutas salientes e internacionales) sigue siendo una de las protecciones más importantes que puede implementar.

## Resumen

En este capítulo ha aprendido sobre los riesgos de tener una PBX IP conectada a Internet. Luego aprendimos cómo proteger nuestra PBX implementando una política de seguridad. En esta política de seguridad hemos implementado iptables, fail2ban, TLS, SRTP y autenticación de dos vías para llamadas internacionales. Espero que haya disfrutado de este capítulo.

## Cuestionario

1. ¿Cuál es la contramedida más importante contra el fraude de ingresos compartidos por Internet?
   - A. Implementar SRTP
   - B. Mantener Asterisk actualizado
   - C. Implementar TLS
   - D. Usar contraseñas seguras
2. El fuzzing SIP se define como:
   - A. Un ataque DoS usando solicitudes y respuestas malformadas
   - B. Robo de servicio donde las contraseñas son forzadas por fuerza bruta
   - C. Escuchas ilegales en llamadas actuales
   - D. Un DDoS con una inundación de solicitudes SIP
3. El robo por TFTP ocurre cuando el servidor proporciona archivos de configuración a través de TFTP. Puede evitarlo usando:
   - A. FTP
   - B. HTTP
   - C. HTTPS con nombre de usuario y contraseña
   - D. SCP
4. Los ataques de hombre en el medio (Man-in-the-middle) usan una técnica llamada:
   - A. Robo por TFTP
   - B. Suplantación de ARP (ARP spoofing)
   - C. Envenenamiento de MAC
   - D. dsniff
5. Para SRTP, Asterisk utiliza el siguiente sistema para intercambiar claves:
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. La utilidad que genera la autoridad de certificación y los certificados, encontrada en `/usr/src/asterisk-22.x.y/contrib/scripts`, es:
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. Estrategias válidas para prevenir escuchas ilegales (marque todas las que correspondan):
   - A. Implementar detectores de escuchas analógicas
   - B. Usar la utilidad ARPwatch para detectar suplantación de ARP
   - C. Habilitar la detección de suplantación de ARP en los switches
   - D. Usar SRTP
8. Asterisk admite una autenticación sólida verificando certificados de cliente. (El transporte TLS de PJSIP puede requerir y verificar el certificado del cliente).
   - A. Verdadero
   - B. Falso
9. En Asterisk 22, ¿qué configuración de endpoint PJSIP activa el cifrado de medios SRTP usando claves in-SDP (SDES)?
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. En Asterisk 22, Fail2Ban debe leer los eventos de autenticación fallida de PJSIP desde el canal de registro ________ dedicado (habilitado en `logger.conf`).
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Respuestas:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
