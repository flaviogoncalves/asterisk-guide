# WebRTC con Asterisk

WebRTC (Web Real-Time Communication) permite que un navegador web realice y reciba llamadas sin necesidad de plugins ni softphones externos: solo se requiere JavaScript, un micrófono y una conexión segura a Asterisk. Asterisk ha sido capaz de actuar como servidor WebRTC desde Asterisk 11, y desde la llegada de la pila PJSIP (`res_pjsip`) en Asterisk 12, esta ha sido la forma recomendada de hacerlo; en Asterisk 22, la configuración se ha consolidado en un puñado de opciones bien definidas. Este capítulo muestra cómo convertir un endpoint PJSIP en un teléfono de navegador, cómo funciona la ruta de medios segura y cuándo debería optar por el soporte WebRTC integrado de Asterisk frente a una pasarela dedicada.

Todo lo expuesto en este capítulo ha sido verificado con el laboratorio de Asterisk 22 del libro; la configuración mostrada es la misma que en `lab/asterisk/etc`.

## Objetivos

Al finalizar este capítulo, usted debería ser capaz de:

- Explicar qué aporta WebRTC a Asterisk y cuándo utilizarlo
- Describir cómo la seguridad de medios WebRTC (DTLS-SRTP) e ICE difieren del SIP convencional
- Habilitar el servidor HTTP de Asterisk y el endpoint de WebSocket seguro (`wss`)
- Configurar un transporte PJSIP `wss` y un endpoint WebRTC con `webrtc=yes`
- Conectar un softphone de navegador (SIP.js) y realizar una llamada
- Decidir entre WebRTC nativo de Asterisk y una pasarela de medios como Janus

## Por qué WebRTC con Asterisk

Un endpoint WebRTC es, desde el punto de vista de Asterisk, simplemente otro endpoint PJSIP. Lo que cambia es *cómo* el navegador llega a él y cómo se aseguran los medios. Los usos típicos incluyen:

- **Click-to-call** en un sitio web: un visitante llama a una cola o a una extension desde una página web.
- **Agentes basados en web**: un agente de centro de contacto trabaja completamente en el navegador, sin necesidad de instalar o actualizar un softphone de escritorio.
- **Llamadas integradas** en su propia aplicación web: por ejemplo, el softphone web SipPulse hablando con Asterisk.
- **Teléfonos internos sin instalación**: el personal utiliza una pestaña del navegador en lugar de un teléfono físico o un cliente instalado.

La gran ventaja es el alcance: todos los navegadores modernos ya hablan WebRTC. El costo es que WebRTC es estricto: *requiere* medios cifrados y un transporte seguro, por lo que hay más que configurar que en un teléfono SIP UDP convencional.

## Cómo difiere WebRTC del SIP convencional

Un teléfono SIP normal señaliza a través de UDP/TCP y generalmente transporta audio como RTP plano. Un cliente de navegador WebRTC es diferente en tres aspectos importantes, y Asterisk debe adaptarse a cada uno:

- **La señalización viaja por un WebSocket.** En lugar de SIP sobre el puerto UDP 5060, el navegador abre un WebSocket seguro (`wss://`) hacia el servidor HTTP integrado de Asterisk. Los mensajes SIP viajan dentro de ese WebSocket.
- **Los medios siempre están cifrados con DTLS-SRTP.** Los navegadores rechazan el RTP plano. Ambas partes realizan un handshake DTLS (autenticado mediante huellas digitales de certificado intercambiadas en el SDP) y derivan claves SRTP a partir de él.
- **La conectividad se negocia con ICE.** En lugar de asumir una IP y un puerto alcanzables, ambas partes recopilan direcciones candidatas (host, STUN-reflexive, TURN-relayed) y las prueban hasta que una funciona. RTP y RTCP generalmente se multiplexan en un solo puerto (`rtcp_mux`).

La buena noticia: en Asterisk 22, una única opción de endpoint, `webrtc=yes`, activa todo esto con valores predeterminados sensatos. Veremos exactamente qué configura.

## Paso 1: el servidor HTTP y el WebSocket

La señalización WebRTC es servida por el servidor HTTP integrado de Asterisk (`res_http_websocket` expone la ruta `/ws` en él). Los navegadores requieren un WebSocket *seguro*, por lo que habilitamos TLS. Edite `http.conf`:

```
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088

; TLS / WSS for WebRTC. Browsers require a secure WebSocket (wss://).
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.crt
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

Recargue (`module reload res_http_websocket` o reinicie) y confirme:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

El navegador se conectará a `wss://your-asterisk:8089/ws`.

### Sobre el certificado

El certificado TLS aquí asegura el *WebSocket* (el canal de señalización). En un laboratorio, un certificado autofirmado es suficiente: lo acepta una vez en el navegador. En producción, utilice un certificado real (por ejemplo, Let's Encrypt) cuyo nombre coincida con el host al que se conecta el navegador; de lo contrario, el navegador rechazará el WebSocket.

> **[Nota de la 2.ª ed.]** El laboratorio incluye `lab/make-certs.sh`, que genera un certificado autofirmado con `CN=localhost`. Para un despliegue público, documente el flujo de Let's Encrypt y apunte `tlscertfile`/`tlsprivatekey` a los archivos emitidos.

Este certificado **no** es el mismo que el certificado DTLS utilizado para cifrar los medios; Asterisk genera ese automáticamente, como veremos.

## Paso 2: el transporte WSS

PJSIP necesita un transporte de tipo `wss`. Añádalo a `pjsip.conf`:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Verifique que se haya cargado:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

> **[Nota de la 2.ª ed.]** El transporte `wss` imprime una dirección de enlace `0.0.0.0:5060` aunque el WebSocket real es servido por el servidor HTTP en el puerto 8089. Esto es esperado: el transporte `wss` es una capa delgada sobre `res_http_websocket`; la línea `bind` en él es efectivamente cosmética. Vale la pena mencionarlo en el texto final para que los lectores no se confundan con el puerto.

## Paso 3: el endpoint WebRTC

Ahora, el endpoint en sí. La clave es `webrtc=yes`:

```
[webrtc-1000]
type=endpoint
context=internal
disallow=all
allow=opus,ulaw
webrtc=yes
transport=transport-wss
aors=webrtc-1000
auth=webrtc-1000

[webrtc-1000]
type=auth
auth_type=userpass
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` es un interruptor de conveniencia. Es equivalente a configurar manualmente todas las opciones requeridas por WebRTC. Puede confirmar exactamente qué activó:

```
*CLI> pjsip show endpoint webrtc-1000
 dtls_auto_generate_cert            : Yes
 dtls_fingerprint                   : SHA-256
 dtls_setup                         : actpass
 ice_support                        : true
 media_encryption                   : dtls
 rtcp_mux                           : true
 use_avpf                           : true
 webrtc                             : yes
```

Al leer esa salida:

- `media_encryption: dtls` y `dtls_auto_generate_cert: Yes`: los medios son DTLS-SRTP, y Asterisk genera automáticamente el certificado DTLS, por lo que **no** necesita crear uno usted mismo. La huella digital se anuncia en el SDP (`SHA-256`).
- `ice_support: true`: Asterisk recopila y negocia candidatos ICE.
- `rtcp_mux: true`: RTP y RTCP comparten un puerto, como esperan los navegadores.
- `use_avpf: true`: el perfil RTP AVPF (feedback), requerido por WebRTC.

`allow=opus` es recomendable: Opus es el códec que prefieren los navegadores. Asterisk 22 incluye el *passthrough* de Opus en el núcleo (el módulo `res_format_attr_opus`), lo cual es suficiente para retransmitir Opus entre dos ramas capaces de Opus sin volver a codificar. La *transcodificación* de Opus a otro códec requiere el módulo separado `codec_opus`, que la guía oficial de WebRTC enumera como opcional pero altamente recomendado y que se instala sobre la compilación base; consulte la discusión sobre códecs en *Designing a VoIP network*. Mantenga `ulaw` como respaldo para puentear hacia ramas que no son WebRTC y que no pueden hablar Opus.

## Paso 4: ICE, STUN y TURN

En una LAN plana, ICE con candidatos de host es suficiente y no se necesita nada más. A través de Internet, generalmente se añade un servidor STUN para que Asterisk y el navegador puedan descubrir sus direcciones públicas, y un servidor TURN para los casos en que los medios directos son imposibles (NAT simétrico, firewalls restrictivos). Apunte Asterisk hacia ellos en `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

El navegador se configura con sus propios servidores ICE en JavaScript (la lista `RTCPeerConnection` `iceServers`). Para un despliegue puramente interno, puede omitir STUN/TURN por completo.

> **[Nota de la 2.ª ed.]** Verifique si recomendar un coturn autoalojado para producción (la mayoría de los despliegues reales necesitan TURN). Añada un breve ejemplo de configuración de coturn si es así.

## Paso 5: el cliente de navegador

Cualquier biblioteca SIP WebRTC funciona; dos muy utilizadas son **SIP.js** y **JsSIP**. El laboratorio incluye un softphone SIP.js mínimo en `lab/webrtc/index.html`. La parte esencial es la URL de transporte y las credenciales:

```javascript
const ua = new SIP.UserAgent({
  uri: SIP.UserAgent.makeURI('sip:webrtc-1000@your-asterisk'),
  transportOptions: { server: 'wss://your-asterisk:8089/ws' },
  authorizationUsername: 'webrtc-1000',
  authorizationPassword: 'Lab-webrtc-secret',
});
await ua.start();
await new SIP.Registerer(ua).register();
// place a call to the echo test
const inviter = new SIP.Inviter(ua, SIP.UserAgent.makeURI('sip:600@your-asterisk'));
await inviter.invite();
```

Dos realidades del navegador a recordar:

- **Contexto seguro.** `getUserMedia` (acceso al micrófono) solo funciona en páginas `https://` o `http://localhost`. Sirva la página a través de HTTPS en producción.
- **Acepte el certificado una vez.** Con un certificado de laboratorio autofirmado, visite `https://your-asterisk:8089/ws` en el mismo navegador primero y acepte la advertencia, o el WebSocket fallará silenciosamente.

El softphone web SipPulse es un cliente de referencia de grado de producción construido sobre estas mismas primitivas.

## Verificación de una llamada WebRTC

Con el navegador registrado, `pjsip show contacts` muestra el contacto dinámico, y una llamada ilumina el canal:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Si el audio es unidireccional o está ausente, casi siempre se debe a ICE o al certificado; consulte la resolución de problemas a continuación.

## WebRTC de Asterisk vs. una pasarela de medios

Asterisk puede terminar WebRTC directamente, pero no siempre es la herramienta adecuada:

- **Utilice WebRTC nativo de Asterisk** cuando el navegador sea un *teléfono* en su PBX: un agente, una extensión interna, un click-to-call que aterriza en su dialplan. El navegador es solo otro endpoint y todo (colas, voicemail, IVR) funciona.
- **Utilice una pasarela dedicada (p. ej., Janus)** cuando necesite escalar muchas sesiones de navegador independientemente del control de llamadas, realizar reenvío selectivo para grandes conferencias/streaming, o mantener el plano de medios separado de la PBX. Una pasarela puentea WebRTC a SIP convencional, y Asterisk entonces ve una rama SIP ordinaria.

Muchos sistemas reales combinan ambos: Asterisk para el control de llamadas, una pasarela para el escalado de medios del lado del navegador. (Esta es la arquitectura detrás de la propia pila de SipPulse).

## Resolución de problemas

- **El WebSocket no conecta:** el navegador rechazó el certificado TLS. Abra `https://host:8089/ws` directamente y acéptelo, o instale un certificado de confianza.
- **Se registra pero no hay audio:** ICE falló; añada STUN, y TURN si está a través de NAT. Verifique `pjsip set logger on` y observe los candidatos SDP.
- **Audio unidireccional:** generalmente NAT/ICE en un lado, o un códec sin coincidencia común; asegúrese de `allow=opus,ulaw`.
- **La llamada se corta al contestar:** el handshake DTLS falló; confirme que `dtls_auto_generate_cert` es `Yes` y que el reloj del sistema es correcto (los certificados son sensibles al tiempo).

## Laboratorio

1. Ejecute `./lab.sh up`, luego `bash lab/make-certs.sh` y reinicie Asterisk.
2. Sirva `lab/webrtc/index.html` (`python3 -m http.server` desde `lab/webrtc`) y ábralo; acepte el certificado en `https://localhost:8089/ws`.
3. Regístrese como `webrtc-1000` y llame a `600` (prueba de eco); debería escucharse a sí mismo.
4. Desde el Softphone SipPulse registrado como `6001`, marque `1000` para llamar al navegador.
5. Inspeccione la negociación: `pjsip set logger on`, realice una llamada y encuentre la huella digital DTLS y los candidatos ICE en el SDP.

## Resumen

WebRTC convierte un navegador en un endpoint de Asterisk de primera clase. La receta es pequeña pero estricta: habilite el servidor HTTP con TLS para que el navegador pueda abrir un WebSocket seguro, añada un transporte PJSIP `wss` y configure `webrtc=yes` en el endpoint, lo cual activa DTLS-SRTP (con un certificado autogenerado), ICE, multiplexación RTP/RTCP y el perfil AVPF. Añada STUN/TURN al cruzar NAT, sirva su página a través de HTTPS y apunte un cliente SIP.js (o JsSIP) a `wss://asterisk:8089/ws`. Para teléfonos de navegador en su PBX, el WebRTC nativo de Asterisk es el camino más sencillo; para medios a gran escala, combínelo con una pasarela.

## Cuestionario

1. ¿Qué transporte utiliza un cliente de navegador WebRTC para llevar la señalización SIP a Asterisk?
   - A. UDP plano en el puerto 5060
   - B. Un WebSocket seguro (`wss://`) al servidor HTTP de Asterisk
   - C. TLS en el puerto 5061
   - D. Un socket TCP crudo en el puerto 8088

2. ¿Los medios WebRTC entre el navegador y Asterisk se cifran utilizando qué mecanismo?
   - A. SDES-SRTP (claves intercambiadas en el SDP)
   - B. DTLS-SRTP (claves derivadas de un handshake DTLS)
   - C. IPsec
   - D. RTP plano: WebRTC no cifra los medios

3. Verdadero o falso: cuando configura `webrtc=yes`, debe generar e instalar manualmente el certificado DTLS utilizado para cifrar los medios.

4. ¿En qué puerto expone el servidor HTTP de Asterisk del laboratorio el WebSocket **seguro** para WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. ¿Cuál de los siguientes activa `webrtc=yes` de forma predeterminada? (Elija todas las que correspondan.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Complete el espacio en blanco: WebRTC negocia la conectividad haciendo que ambos lados recopilen y prueben direcciones candidatas (host, STUN-reflexive, TURN-relayed) utilizando el marco de trabajo ________.

7. En `rtp.conf`, ¿qué dos configuraciones apuntan a Asterisk hacia un servidor externo para que pueda descubrir su dirección pública y retransmitir medios cuando las rutas directas fallan? (Elija todas las que correspondan.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. La ruta URL que el `res_http_websocket` de Asterisk expone para la señalización WebRTC es ________.

9. Según el capítulo, ¿cuándo debería optar por una pasarela de medios dedicada (como Janus) en lugar del WebRTC nativo de Asterisk?
   - A. Siempre que cualquier navegador necesite realizar una llamada
   - B. Cuando debe escalar muchas sesiones de medios de navegador independientemente del control de llamadas, realizar reenvío selectivo para grandes conferencias o mantener el plano de medios separado de la PBX
   - C. Solo cuando el navegador no admite DTLS
   - D. Cuando desea que el voicemail y el IVR funcionen para el endpoint del navegador

10. Verdadero o falso: `getUserMedia` (acceso al micrófono) funciona en cualquier página `http://`, por lo que servir el softphone del navegador a través de HTTPS es opcional.

**Respuestas:** 1 — B · 2 — B · 3 — Falso (Asterisk autogenera el certificado DTLS; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — Falso (se requiere contexto seguro: `getUserMedia` solo funciona en `https://` o `http://localhost`)
