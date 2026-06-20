# Seguridad de Asterisk

Desde el principio, el tema de la seguridad para Asterisk es crítico. SIP, Session Initiation Protocol, es el protocolo más atacado en Internet según el CERT.BR. Cualquier persona que ejecute un honeypot puede confirmarlo. El problema del fraude de reparto de ingresos en Internet es muy serio y puede generar pérdidas superiores a cientos de miles de dólares. Nunca debe instalar un servidor Asterisk conectado a Internet sin la seguridad adecuada. En este capítulo, aprenderá a identificar los principales tipos de ataques que puede recibir y cómo prevenirlos mediante una política de seguridad apropiada. Por último, pero no menos importante, aprenderá a implementar la política de seguridad sugerida.

Este capítulo está dirigido a **Asterisk 22 LTS**, donde PJSIP (`res_pjsip` / `chan_pjsip`) es el único canal SIP. (El controlador antiguo `chan_sip` fue eliminado en Asterisk 21 — consulte el capítulo *Legacy Channels* si está migrando un sistema más antiguo.) Una consecuencia relevante para la seguridad: las autenticaciones fallidas ahora se emiten a través del **marco de eventos de seguridad** de Asterisk y el canal de registro dedicado `security`, lo que cambia la forma en que se configura Fail2Ban (se cubre más adelante en este capítulo).

## Objetivos

Al final de este capítulo deberías ser capaz de:

- Identificar los principales tipos de ataques que se realizan frecuentemente a servidores Asterisk
- Definir una política de seguridad eficaz
- Implementar la política de seguridad
- Instalar y configurar IPTABLES para Asterisk
- Instalar y configurar Fail2Ban para Asterisk
- Instalar y configurar TLS y SRTP para cifrado

## Principales ataques a la telefonía IP

Los principales ataques a la telefonía IP pueden clasificarse como DOS/DDOS, Robo de Servicio/Fraude de Tarifas y Escucha clandestina. Algunos de los nombres pueden resultar confusos y diferentes fuentes a veces utilizan nombres distintos para el mismo ataque. Robo de Servicio, Fraude de Tarifas, Fraude de Compartición de Ingresos por Internet, Fraude Telefónico son nombres diferentes para los hackers que usan su PBX para generar tráfico a un Número de Tarifa Premium y obtener reembolsos del proveedor.

### DDoS/DOS

Denial of Service y Distributed Denial of Service son ataques comunes contra cualquier infraestructura de TI. No es diferente con SIP y otros protocolos de Voice over IP. El ataque distribuido de denegación de servicio suele ser perpetrado por una botnet, mientras que el DOS lo realiza un solo equipo. En febrero de 2011 la botnet Sality llevó a cabo un escaneo sigiloso y coordinado de todo el espacio de direcciones IPv4 en busca de servidores SIP vulnerables; investigadores que observaban el UCSD Network Telescope lo atribuyeron a aproximadamente tres millones de IPs de origen distintas que sondaban el puerto UDP 5060, probablemente para forzar cuentas SIP y cometer fraude de tarifas.[^sality]

[^sality]: A. Dainotti et al., "Análisis de un escaneo sigiloso '/0' de una botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![Una botnet peer-to-peer que dirige miles de intentos de registro SIP a un servidor](../images/19-security-fig01.png)

El DOS se aplica usualmente mediante técnicas como fuzzing y flooding. Flooding puede usar SIP, IAX, RTP y otros protocolos. Pueden detener el servicio completamente o degradar la calidad de voz. Son muy difíciles de mitigar si los puertos están abiertos a Internet. A continuación se presentan algunas de las herramientas usadas por los atacantes

**Fuzzing:**

- **PROTOS Test Suite (c07-sip)** — de la Universidad de Oulu OUSPG. Envía miles de paquetes malformados para provocar un mal funcionamiento como un desbordamiento de búfer que detiene el software.  
- **Voiper** — genera más de 200 000 pruebas que cubren todos los atributos SIP y verifica si su servidor puede procesar los mensajes de manera eficaz. <http://voiper.sourceforge.net/>

**Inundación:**

- **INVITE Flooder** — inunda el servidor con solicitudes SIP INVITE. <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — inunda el servidor con tráfico IAX2. <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — inunda sesiones de medios activas con paquetes RTP para degradar la calidad de voz. <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### Técnicas de mitigación para DoS/DDoS

Mis recomendaciones son

1. No exponga su servidor Asterisk en Internet, a menos que sea necesario con la protección adecuada (SBC)  
2. En la red interna use una LAN virtual para voz, principalmente si está en una Universidad, Colegio donde el número de usuarios es alto.  
3. Use VPN o TLS para acceso externo.

### Fraude de Compartición de Ingresos por Internet

Este fraude es un poco complicado de entender. La clave es comprender el concepto de un número de tarifa premium internacional (IPRN).

![Los tres pasos del fraude de reparto de ingresos por Internet: comprar un número de tarifa premium, encontrar un dispositivo VoIP vulnerable y llamar al número, luego cobrar el pago](../images/19-security-fig02.png)

Un IPRN es un número que puedes asignar de forma gratuita en algunas compañías de telefonía por internet específicas. Busca proveedores de Internet Premium Rate Number y encontrarás varios. En este tipo de operador puedes asignar, por ejemplo, un número en una red satelital como Iridium, un destino que cuesta décimas de dólar por minuto al llamante. El proveedor de IPRN te devolverá un porcentaje de los ingresos (10 a 20 % de la ganancia) por cada minuto recibido.

![Lista de precios de un proveedor IPRN que muestra tasas de pago por país y números de prueba](../images/19-security-fig03.png)

Después de la fase de asignación, el hacker intenta encontrar cualquier servidor Asterisk abierto capaz de marcar el IPRN asignado. La PBX de la víctima, controlada por el hacker, realizará cientos de llamadas al número IPRN generando un gran reembolso para el hacker y una enorme factura telefónica para la víctima. Muchas veces, más de cientos de miles de dólares en un solo fin de semana.

Principales herramientas usadas por los hackers para atacar una PBX:

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious es un conjunto de herramientas de seguridad fácil de usar. Su objetivo principal es reconocer PBX vulnerables y romper las contraseñas SIP mediante un ataque de fuerza bruta. La herramienta más utilizada es svcrack. La herramienta es capaz de probar miles de contraseñas por segundo.  
2. **Phone vulnerabilities**. Otro punto que los hackers usan frecuentemente como vector de ataque es el propio teléfono. Muchas personas que instalan Asterisk no cambian la contraseña predeterminada en la interfaz web del teléfono. Cuando estos teléfonos están expuestos en Internet, los hackers pueden intentar usar la contraseña predeterminada de la interfaz para descargar la configuración donde a menudo pueden encontrar la contraseña secreta SIP.

#### Robo de TFTP:

Si está utilizando aprovisionamiento automático de teléfonos mediante TFTP, probablemente esté abierto a este tipo de ataque. TFTP es una forma simple e insegura de un Protocolo de Transferencia de Archivos.

![Un atacante descargando archivos .cfg adivinables de un servidor TFTP, recolectando credenciales en texto plano de los archivos de configuración](../images/19-security-fig04.png)

El nombre de los archivos de configuración es fácilmente adivinable usando la dirección MAC seguida de .cfg (p. ej. 001A2B3C4D5E.cfg). Un hacker astuto puede crear fácilmente una utilidad para probar todas las direcciones MAC secuencialmente o simplemente descargar una herramienta para hacerlo. El archivo de configuración suele estar sin cifrar y contiene la contraseña secreta SIP en su interior.

#### Mitigación de ataques de fuerza bruta y robo de tftp

Para mitigar estos ataques puede aplicar las soluciones a continuación.  
Fuerza bruta: La mejor solución para mitigar ataques de fuerza bruta es impedir intentos no autorizados secuenciales. Casi cualquier instalador de Asterisk usa la utilidad fail2ban para esto. Cuando fail2ban detecta múltiples intentos con la contraseña o nombre de usuario incorrectos, bloquea la IP del atacante por un período de tiempo determinado. La segunda medida contra la fuerza bruta es usar contraseñas fuertes, de más de 12 caracteres, con al menos un carácter especial.  
Tftptheft: Para prevenir TFTPTheft configure el aprovisionamiento para usar https con nombre y contraseña. El archivo se transmite cifrado y un nombre y contraseña evitan que los atacantes intenten descargar cualquier archivo.

### Escucha clandestina

No vemos mucho este tipo de ataques porque en la mayoría de los casos simplemente no se detectan. La interceptación es muy difícil de detectar en un entorno IP. Utilidades como UCsniff, disponibles libremente, son capaces de interceptar una llamada VoIP en la mayoría de las redes. La técnica principal es usar ARP spoofing para forzar el tráfico a través del equipo que ejecuta UCsniff y grabar las llamadas.

#### Mitigación contra la interceptación

Puedes prevenir la interceptación cifrando tu tráfico VoIP. La otra forma es prevenir ataques de hombre en el medio (MITM) en tu red. La inspección ARP es muy eficaz para prevenir MITM en redes de capa 2. Consulta el soporte técnico de tu red para entender cómo implementarla. Más adelante en este libro aprenderemos cómo instalar cifrado basado en TLS y SRTP. También puedes usar ARPWatch para descubrir si alguien está abusando ahora del protocolo ARP para atacar tu red.

## Política de seguridad para Asterisk

La mejor manera de implementar la seguridad es crear una política de seguridad. Para este entrenamiento sugeriré una política de seguridad para la mayoría de instalaciones de Asterisk. Úsela como punto de partida base y cámbiela según sus necesidades. La política de seguridad sugerida se muestra a continuación:

1. No abrir puertos UDP/TCP innecesarios
2. No dejar acceso a ninguna interfaz administrativa (SSH/HTTPS) abierta en Internet.
3. Para acceder a SSH y/o HTTP/HTTPS debe haber excepciones explícitas en el firewall IPTABLES
4. Contraseñas fuertes con 12 caracteres y al menos un carácter especial
5. Bloquear direcciones IP que fallen más de 10 veces en la autenticación usando Fail2ban
6. Confirmación de contraseña para llamadas internacionales
7. Limitar el acceso al puerto SIP a su rango conocido de direcciones IP

Si necesita tener acceso externo a su PBX, hay dos posibilidades. Use un SBC (Session Border Controller) para proteger su servidor contra DOS/DDOS o use una VPN siempre que quiera acceso externo. Si deja el puerto 5060 abierto en Internet sin un SBC o VPN, está expuesto a un ataque DOS/DDOS. El riesgo es suyo.

### Endurecimiento de la era PJSIP (Asterisk 22)

Más allá del firewall y Fail2Ban, la pila PJSIP de Asterisk 22 ofrece varios controles a nivel de configuración que deberían formar parte de su política de seguridad. Estos complementan (no reemplazan) los controles de red anteriores:

- **Autenticación por endpoint.** Cada endpoint debe referenciar una sección dedicada `type=auth` con un `password` fuerte y único (`auth_type=digest`). Nunca reutilice credenciales entre endpoints.  
- **El manejo anónimo está incorporado.** PJSIP no revela si un nombre de usuario existe cuando la autenticación falla. Para aceptar llamadas anónimas debe crear explícitamente un endpoint llamado `anonymous` y usar secciones `type=identify` (coincidiendo con la IP de origen) para mapear pares conocidos a endpoints. Si no desea llamadas anónimas, simplemente no cree un endpoint `anonymous`, y las solicitudes no coincidentes serán desafiadas/rechazadas.  
- **ACLs.** Restrinja quién puede alcanzar un endpoint con ACLs nombradas `/etc/asterisk/acl.conf`, referenciadas desde el endpoint con `acl=` (ACL de señalización/fuente) y `contact_acl=` (restringe la dirección de contacto/registro). También puede establecer permit/deny directamente en el endpoint.  
- **`qualify`.** Establezca `qualify_frequency` (y `qualify_timeout`) en el AOR para que Asterisk monitoree activamente la alcanzabilidad de los contactos registrados y elimine los que estén muertos.  
- **Endurecimiento del transporte PJSIP / protección contra DoS.** El `type=transport` no expone un límite de clientes por transporte, por lo que la protección contra inundaciones de conexiones proviene del firewall (las reglas iptables/Fail2Ban en este capítulo) en lugar de una opción de PJSIP. Lo que el transporte *sí* brinda son ajustes de keep-alive TCP (`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`) para limpiar conexiones muertas o a medio abrir, y configuraciones `local_net`/`external_*` para un manejo correcto de NAT. Combine estos con las reglas del firewall para mitigar ataques de inundación de conexiones.  
- **TLS + SRTP para medios.** Encripte la señalización con un transporte TLS y los medios con `media_encryption=sdes` (o `dtls` para WebRTC) en el endpoint — cubierto más adelante en este capítulo.  
- **Control de acceso AMI/ARI.** Restrinja la Asterisk Manager Interface (`manager.conf`) y ARI (`ari.conf` / `http.conf`) a localhost o a una red de gestión confiable, use secretos fuertes y únicos, vincule el servidor HTTP a una interfaz privada, y nunca exponga estos servicios a Internet.

Todos los nombres de opciones anteriores están confirmados con Asterisk 22.10: la sección `type=transport` expone `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net` y la familia `external_*`, pero **no** tiene la opción `max_clients` — la protección contra inundación de conexiones proviene del firewall, no del transporte. Las opciones de endpoint `acl` y `contact_acl` toman nombres de sección de `acl.conf`, y la coincidencia de IP de origen para pares no autenticados se realiza con secciones `type=identify` (`match=`).

### Eliminando puertos innecesarios

En lugar de descubrir todas las vulnerabilidades asociadas con todos los protocolos de Asterisk, simplifiquemos el problema eliminando los puertos innecesarios. Para listar todos los puertos abiertos por el servidor Asterisk use:

```
netstat -pantu |grep asterisk
```

The output of the command is shown below.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

If you look at the output, you will discover that many ports are open. Do we need them? Not necessarily, 2727 is the MGCP protocol (chan_mgcp), 4569 is the IAX (chan_iax2). If you are not using these protocols, you can simply remove the module in the configuration file modules.conf.

You may notice Asterisk binding a high-numbered UDP port. This comes from `res_pjsip`'s resolver making outbound DNS queries (the source port is ephemeral, like any client DNS lookup), not from an inbound listener — your firewall only needs to allow **established/related** return traffic for it (the iptables `conntrack ESTABLISHED,RELATED` rule shown below already covers this). You do **not** need to open a wide inbound high-UDP range just for PJSIP DNS.

To remove the unnecessary ports, disable the modules you don't use. Edit the file modules.conf and add `noload` lines for the channels and protocols you are not using. **Do not** noload `res_pjsip`, `res_pjproject`, or `chan_pjsip` — those are required for SIP in Asterisk 22:

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(In Asterisk 22 you no longer need to noload `chan_mgcp` or `chan_skinny` — those drivers were *removed* in Asterisk 21 and are not part of a stock 22 build.) With the instructions above, I have removed all unnecessary channels keeping only PJSIP. You can choose whatever protocol modules you want, just remove the unused ones. The result is shown in the screenshot below — only the SIP port (5060) bound by your PJSIP transport is now exposed inbound.

![netstat output after disabling the unused modules: only UDP port 5060 remains bound by Asterisk](../images/19-security-fig06.png)

### Implementando la política de seguridad con IPTABLES

IPTABLES o netfilter es un firewall estándar presente en la mayoría de distribuciones Linux. En este laboratorio configuraremos iptables y fail2ban. El objetivo es implementar la política de seguridad recomendada para Asterisk y bloquear todo el tráfico innecesario. Siga los pasos a continuación:

1. Bloquear todo el tráfico externo
2. Permitir tráfico SSH desde una red interna o un host único
3. Permitir tráfico SIP en UDP y TCP en los puertos 5060
4. Permitir tráfico RTP en el rango de puertos de medios UDP. No existe un valor predeterminado único incorporado — el `rtp.conf` propio de Asterisk recurre a los puertos 5000–31000 cuando no se configura nada, pero el `rtp.conf.sample` distribuido configura `rtpstart=10000` / `rtpend=20000`, por lo que usamos ese rango de ejemplo aquí. Ajuste su regla de firewall a cualquier `rtpstart`/`rtpend` que realmente haya configurado en `rtp.conf`.

Asegúrese de tener acceso a la consola del servidor, no querrá bloquearse a sí mismo fuera del sistema. Tenga cuidado.

1. Instale el paquete net-persistent.```
   sudo apt-get install iptables-persistent
   ```

2. Permitir todo el tráfico desde el bucle de retorno```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. Permitir conexiones establecidas```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

4. Permitir tráfico SSH/HTTPS desde la red 192.168.0.0```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. Insertar las reglas de Asterisk```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

Tenga en cuenta que el puerto 5061 (SIP sobre TLS) es **TCP**, no UDP. Las reglas anteriores abren el 5060 tanto en UDP como en TCP y el 5061 en TCP. Si solo usa TLS, puede eliminar completamente las reglas del 5060 sin cifrar. Abra solo los puertos a los que sus transportes PJSIP realmente se enlazan.

`-I` significa PREPEND

6. La última regla debe ser un drop```
   sudo iptables -A INPUT -j DROP
   ```

`-A` significa APPEND. Nota: Tenga cuidado al mantener reglas nuevas, debe agregar reglas antes del DROP. Use PREPEND para reglas nuevas `-I`

7. Guarde las reglas y reinicie iptables```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### Usando Fail2Ban para bloquear múltiples intentos fallidos de autenticación

Fail2Ban es casi un estándar para Asterisk. La mayoría de los usuarios lo implementan para mejorar la seguridad. Esta utilidad escanea los registros de Asterisk en busca de intentos fallidos y bloquea las direcciones IP de los atacantes. A continuación, proporciono las instrucciones para instalar Fail2Ban.

En Asterisk 22, PJSIP informa autenticaciones fallidas y otros eventos de seguridad a través del **marco de eventos de seguridad** de Asterisk, escrito en el canal de registro dedicado **`security`**. Para que Fail2Ban funcione debes:

1. Habilitar el canal de seguridad en `/etc/asterisk/logger.conf`. La sintaxis es `<filename> => <levels>`, así que para enviar el nivel de seguridad a un archivo llamado `security` escribe:

```
[logfiles]
security => security
```

luego ejecute `logger reload` desde la CLI. Esto produce `/var/log/asterisk/security` con una línea por evento de seguridad, en la forma:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

Los eventos que le interesan a Fail2Ban son `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID` y `FailedACL`, cada uno con un campo `RemoteAddress="IPV4/UDP/<ip>/<port>"` que identifica al infractor. (Observe que la dirección está envuelta como `IPV4/UDP/.../...`, no como una IP simple — su filtro debe extraer el host desde dentro de esa cadena.)

2. Apunte la cárcel `asterisk` a ese archivo (`logpath = /var/log/asterisk/security`) y use un filtro que analice este formato de evento de seguridad.

Fail2Ban moderno incluye un filtro `asterisk` cuyo `failregex` ya coincide con los eventos anteriores y extrae `<HOST>` del campo `RemoteAddress`, por ejemplo:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX distributions (FreePBX/Sangoma) ship equivalent filters. Prefer the packaged filter over hand‑writing one, since the exact event strings are version‑dependent. One caveat to be aware of: a now‑patched advisory (GHSA-5743-x3p5-3rg7) showed that crafted PJSIP traffic could inject fake log lines — keep both Asterisk and your Fail2Ban filter current.

Below I provide the instructions to install Fail2Ban

1. Instalar fail2ban on Linux```
   sudo apt-get install fail2ban
   ```

2. Activar fail2ban para Asterisk y SSH```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

Agregue las siguientes líneas para activar fail2ban para ssh y asterisk```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. Reiniciar fail2ban```
   /etc/init.d/fail2ban restart
   ```

4. Verificar. Cambie el secreto de su softphone y intente volver a registrarse 10 veces. Usando `iptables -L`, verifique si la dirección del softphone fue incluida como una dirección bloqueada.  
5. Elimine la dirección del bloqueo (suponga que la dirección es 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note: In the command replace 192.168.0.5 by the ip address of your phone

### Implementando TLS y SRTP

Dividiré esta sección en dos partes. En la primera cubriremos TLS para cifrar la señalización y en la segunda SRTP para cifrar los medios. El objetivo aquí es configurar Asterisk para estos recursos.

#### TLS

TLS (Transport Layer Security) es el mecanismo de cifrado definido para proteger la señalización SIP. La tabla a continuación resume contra qué ataques protege TLS:

| Type of attack | Protected? | Notes |
|----------------|-----------|-------|
| Signaling attacks | Yes | TLS assures the integrity of the messages |
| Man in the middle | Yes | TLS checks the server certificate |
| Eavesdropping | No | TLS encrypts signaling, not media |

Para el cifrado de medios (voz/video) use SRTP.

#### Certificados digitales autofirmados

Existen dos tipos de certificados que puede usar: autofirmados y comerciales. Los certificados autofirmados son firmados por su propio servidor, mientras que los certificados comerciales son firmados por una autoridad externa. Para VoIP, puede ser su propia autoridad certificadora. No es necesario un certificado externo como GoDaddy o Verisign, ya que eso representa un gasto innecesario. Generaremos nuestros propios certificados usando ast_tls_cert.

#### Configurando TLS con certificados autofirmados

A continuación se muestra una guía paso a paso sobre cómo implementar TLS. Primero generamos los certificados, luego configuramos el transporte TLS de PJSIP (ver "Configuring TLS with chan_pjsip") y finalmente apuntamos el softphone a él. Usaremos el SipPulse Softphone, que soporta TLS y SRTP de forma nativa. (Cualquier softphone SIP compatible con TLS/SRTP funciona de la misma manera.)

**Step 1.** Create a private RSA key using 3DES encryption with length of 4096 bits for our certification authority. The command below present in /usr/src/asterisk-22.x.y/contrib/scripts will create the Certification Authority and The Asterisk Certificate. As usual adapt the instructions if required, versions change, directories change. Please, pay attention on what you are doing. Use your domain or IP address in the –C option. The command ast_tls_cert has three options.

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
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
Generating RSA private key, 2048 bit long modulus
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

No voy a generar un certificado de cliente porque no vamos a usar el certificado para autenticar al cliente. No se requiere que el cliente presente su propio certificado.

**Step 2.** Configure Asterisk para soportar a nuestro cliente mediante TLS. Esto se hace en `pjsip.conf` (un transporte TLS más la configuración del endpoint); la configuración completa se muestra en la siguiente sección, “Configuring TLS with chan_pjsip”. No estamos autenticando con certificados, solo encriptando el tráfico.

**Step 3.** Instale un softphone SIP compatible con TLS (el autor usa el SipPulse Softphone).

**Step 4.** Copie la autoridad certificadora al equipo que ejecuta el softphone. Después de instalarla, copie el archivo `/etc/asterisk/keys/ca.crt` al equipo que ejecuta el softphone (use scp, o WinSCP en Windows) si está usando un certificado autofirmado.

**Step 5.** Cree la cuenta en el softphone. En la pantalla de cuenta añada la cuenta normalmente como cualquier otra cuenta sip. Use la contraseña correcta, la autenticación sigue basándose en la contraseña.

**Step 6.** Establezca TLS como el transporte en la configuración de la cuenta. En la pantalla de cuenta del SipPulse Softphone (abajo), elija **TLS** como transporte y use el puerto 5061. Ajuste su firewall para abrir el puerto TCP 5061.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** Confíe en la autoridad certificadora. Si el certificado TLS de Asterisk está firmado por una CA pública (por ejemplo Let’s Encrypt — vea el capítulo *Deployment*), un softphone moderno como el SipPulse Softphone lo confía automáticamente a través del almacén de certificados del sistema, sin necesidad de importación manual. Si usa un certificado autofirmado, importe su CA (`/etc/asterisk/keys/ca.crt`) en el cliente o en el almacén de confianza del sistema operativo, o acéptelo cuando se le solicite.

**Step 8.** No necesita un certificado de cliente. Un error común es pensar que cada teléfono necesita su propio certificado para autenticarse; no es así. En este punto Asterisk solo *encripta* la sesión; la autenticación sigue siendo nombre de usuario y contraseña. Asterisk no verifica los certificados de cliente por defecto, por lo que no es necesario distribuir un certificado por cliente.

**Step 9.** Después de cambiar el certificado o el transporte, reinicie completamente el softphone (ciérrelo y vuelva a abrirlo, no solo cierre la ventana) para que se reconecte mediante el nuevo transporte.

### Configuring TLS with chan_pjsip

Ahora aprendamos cómo configurar PJSIP para TLS. PJSIP es el único canal SIP en Asterisk 22, así que no hay nada que cambiar; solo asegúrese de que `res_pjsip`, `res_pjproject` y `chan_pjsip` estén cargados. Paso 1: Confirme que PJSIP está habilitado en /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

Paso 2: Configurar PJSIP para que admita TLS. Añadir una sección para el transporte TLS en el archivo /etc/asterisk/pjsip.conf

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Use `method=tlsv1_2` (or `tlsv1_3` si su compilación de OpenSSL/PJSIP lo soporta) — TLS 1.0/1.1 son obsoletos e inseguros y no deben usarse.

Step 3: Configure the endpoint for blink. Edit `pjsip.conf` y edite la sección para blink. Deje que PJSIP elija el transporte automáticamente.

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

Step 4: Verificación. Para verificar que el registro se realizó mediante TLS, use el siguiente comando en la consola de Asterisk.

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### Realizando llamadas seguras usando SRTP

El protocolo responsable del cifrado de medios es el Secure Real Time Protocol (SRTP) definido en el RFC3711. Una de las limitaciones del protocolo es la falta de un método estandarizado para intercambiar claves. Asterisk usa intercambio de claves SDES sobre el protocolo SDP protegido por el cifrado de señalización provisto por TLS. También existen otros métodos como MIKEY y ZRTP. ZRTP, desarrollado por Philipp Zimmermann, es uno de los métodos más sofisticados para el intercambio de claves y el cifrado de medios. Algunos softphones y teléfonos fijos permiten ZRTP. Sin embargo, la forma estándar sigue siendo SDES y encontrará este método en casi cualquier teléfono disponible en el mercado. A continuación, un ejemplo de una solicitud con las claves criptográficas definidas en el SDP en las líneas a=crypto:1 y a=crypto:2.

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

#### Configurando SRTP en Asterisk

Configurar SRTP en Asterisk es muy simple. Establezca `media_encryption=sdes` en el endpoint; también puede requerirlo con `media_encryption_optimistic=no` para que los medios sin cifrar sean rechazados en lugar de permitidos silenciosamente. Tenga en cuenta que SDES requiere que la señalización se ejecute sobre TLS, de modo que las claves no se envíen en texto plano.

**Paso 1.** Configuración de Asterisk

Establezca lo siguiente en la sección `type=endpoint` de `pjsip.conf`:

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

**Paso 2.** Configuración del softphone

En el softphone, habilite SRTP para los medios de la cuenta (establezca la opción **SRTP (Media Encryption)** a *Mandatory*) para que la voz esté cifrada.

![La configuración de la cuenta del softphone SipPulse (sección inferior) — establezca **Transport** a TLS y **SRTP (Media Encryption)** a *Mandatory* para que la señalización y los medios estén ambos cifrados.](../images/softphone/sipphone-config.png){width=35%}

## Habilitar autenticación de dos factores para llamadas internacionales

A veces la mejor solución es no tener rutas internacionales. Sin embargo, si realmente necesitas marcar internacionalmente, usa una contraseña adicional. Vamos a utilizar la aplicación de Asterisk **vmauthenticate** para solicitar la contraseña del buzón de voz antes de marcar internacionalmente. Esto se configura en el dialplan dentro de **extensions.conf**. Vea el ejemplo a continuación. Así, un hacker, incluso después de descubrir una contraseña de peer o comprometer un teléfono, todavía necesitará la contraseña del buzón de voz para marcar este destino.

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` sigue siendo una aplicación estándar en Asterisk 22. El `Dial()` anterior enruta la llamada a través de un trunk SIP/PJSIP (`PJSIP/<number>@<trunk>`), que es como la mayoría de las instalaciones modernas acceden a la PSTN — adapte `my_trunk` a su propio nombre de trunk, y use `DAHDI/g1/...` solo si realmente tiene un span DAHDI. Defensa contra fraude de tarifas en el dialplan — un segundo factor como este, combinado con restringir qué contextos pueden alcanzar sus rutas salientes e internacionales — sigue siendo una de las protecciones individuales más importantes que puede desplegar.

## Resumen

En este capítulo has aprendido sobre los riesgos de tener una IP PBX conectada a Internet. Luego aprendimos cómo proteger nuestra PBX implementando una política de seguridad. En esta política de seguridad hemos implementado iptables, fail2ban, TLS, SRTP y autenticación bidireccional para llamadas internacionales. Espero que hayas disfrutado este capítulo.

## Quiz

1. ¿Cuál es la medida de mitigación más importante contra el fraude de reparto de ingresos por Internet?
   - A. Implementar SRTP
   - B. Mantener Asterisk actualizado
   - C. Implementar TLS
   - D. Usar contraseñas seguras
2. El fuzzing SIP se define como:
   - A. Un ataque DoS usando solicitudes y respuestas malformadas
   - B. Robo de servicio donde se fuerza la contraseña
   - C. Interceptación de llamadas en curso
   - D. Un DDoS con una avalancha de solicitudes SIP
3. TFTPTheft ocurre cuando el servidor proporciona archivos de configuración vía TFTP. Puedes evitarlo usando:
   - A. FTP
   - B. HTTP
   - C. HTTPS con nombre de usuario y contraseña
   - D. SCP
4. Los ataques man-in-the-middle usan una técnica llamada:
   - A. Robo TFTP
   - B. ARP spoofing
   - C. Envenenamiento MAC
   - D. dsniff
5. Para SRTP, Asterisk usa el siguiente sistema para intercambiar claves:
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. La utilidad que genera la autoridad certificadora y los certificados, encontrada en `/usr/src/asterisk-22.x.y/contrib/scripts`, es:
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. Estrategias válidas para prevenir la interceptación (marque todas las que apliquen):
   - A. Implementar detectores analógicos de interceptación
   - B. Usar la utilidad ARPwatch para detectar ARP spoofing
   - C. Habilitar detección de ARP-spoofing en los switches
   - D. Usar SRTP
8. Asterisk admite autenticación fuerte verificando los certificados del cliente. (El transporte TLS de PJSIP puede requerir y verificar el certificado del cliente.)
   - A. Verdadero
   - B. Falso
9. En Asterisk 22, ¿qué ajuste del endpoint PJSIP activa el cifrado de medios SRTP usando claves in‑SDP (SDES)?
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. En Asterisk 22, Fail2Ban debe leer los eventos de autenticación fallida de PJSIP desde el canal de registro ________ dedicado (habilitado en `logger.conf`).
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
