# WebRTC con Asterisk

WebRTC (Web Real-Time Communication) permite que un navegador web realice y reciba llamadas sin necesidad de complementos ni de un softphone externo — solo JavaScript, un micrófono y una conexión segura a Asterisk. Asterisk ha podido actuar como servidor WebRTC desde Asterisk 11, y desde que la pila PJSIP (`res_pjsip`) llegó a Asterisk 12 ha sido la forma recomendada de hacerlo; en Asterisk 22 la configuración se ha consolidado en un puñado de opciones bien comprendidas. Este capítulo muestra cómo convertir un endpoint PJSIP en un teléfono de navegador, cómo funciona la ruta de medios segura y cuándo debe recurrir al soporte WebRTC incorporado de Asterisk en lugar de a una pasarela dedicada.

Todo lo expuesto en este capítulo está verificado contra el laboratorio de Asterisk 22 del libro; la configuración mostrada es la misma que en `lab/asterisk/etc`.

## Objectives

Al final de este capítulo, deberías ser capaz de:

- Explicar qué agrega WebRTC a Asterisk y cuándo usarlo
- Describir cómo la seguridad de medios de WebRTC (DTLS‑SRTP) y ICE difieren del SIP simple
- Habilitar el servidor HTTP de Asterisk y el endpoint de WebSocket seguro (`wss`)
- Configurar un transporte PJSIP `wss` y un endpoint WebRTC con `webrtc=yes`
- Conectar un softphone de navegador (SIP.js) y realizar una llamada
- Decidir entre WebRTC nativo de Asterisk y una pasarela de medios como Janus

## Por qué WebRTC con Asterisk

Un punto final WebRTC es, desde el punto de vista de Asterisk, simplemente otro punto final PJSIP. Lo que cambia es *cómo* el navegador lo alcanza y cómo se asegura el medio. Los usos típicos incluyen:

- **Click-to-call** en un sitio web — un visitante llama a una cola o a una extensión desde una página web.
- **Agentes basados en la web** — un agente de centro de contacto trabaja completamente en el navegador, sin necesidad de instalar o actualizar un softphone de escritorio.
- **Llamadas incrustadas** en su propia aplicación web — por ejemplo, el softphone web SipPulse comunicándose con Asterisk.
- **Teléfonos internos sin instalación** — el personal usa una pestaña del navegador en lugar de un teléfono hardware o un cliente instalado.

La gran ventaja es el alcance: cada navegador moderno ya soporta WebRTC. El costo es que WebRTC es estricto — *requiere* medios cifrados y un transporte seguro, por lo que hay más que configurar que en un teléfono SIP UDP simple.

## Cómo difiere WebRTC del SIP simple

Un teléfono SIP regular señaliza sobre UDP/TCP y usualmente transporta audio como RTP simple. Un cliente de navegador WebRTC es diferente en tres aspectos importantes, y Asterisk debe coincidir con cada uno:

- **La señalización viaja en un WebSocket.** En lugar de SIP sobre el puerto UDP 5060, el navegador abre un WebSocket seguro (`wss://`) al servidor HTTP integrado de Asterisk. Los mensajes SIP viajan dentro de ese WebSocket.
- **Los medios siempre están cifrados con DTLS‑SRTP.** Los navegadores rechazan RTP simple. Ambas partes realizan un apretón de manos DTLS (autenticado por huellas digitales de certificados intercambiadas en el SDP) y derivan claves SRTP a partir de él.
- **La conectividad se negocia con ICE.** En lugar de asumir una IP y puerto alcanzables, ambas partes recopilan direcciones candidatas (host, STUN‑reflexiva, TURN‑retransmitida) y las prueban hasta que una funciona. RTP y RTCP usualmente se multiplexan en un solo puerto (`rtcp_mux`).

La buena noticia: en Asterisk 22 una única opción de endpoint, `webrtc=yes`, activa todo esto con valores predeterminados sensatos. Veremos exactamente qué configura.

## Paso 1 — el servidor HTTP y el WebSocket

La señalización de WebRTC es servida por el servidor HTTP incorporado de Asterisk (`res_http_websocket` expone la ruta `/ws` en él). Los navegadores requieren un WebSocket *seguro*, por lo que habilitamos TLS. Edite `http.conf`:

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

### Acerca del certificado

El certificado TLS aquí protege el *WebSocket* (el canal de señalización). En un laboratorio un certificado autofirmado está bien — lo acepta una vez en el navegador. En producción use un certificado real (por ejemplo Let's Encrypt) cuyo nombre coincida con el host al que se conecta el navegador, de lo contrario el navegador rechazará el WebSocket.

Para el laboratorio, `lab/make-certs.sh` genera un certificado autofirmado con `CN=localhost` (más SANs `localhost`/`127.0.0.1`) y lo escribe en `asterisk/etc/keys/`. Para una implementación pública, obtenga un certificado real en su lugar — por ejemplo con Let's Encrypt:

```
certbot certonly --standalone -d voip.example.com
```

Luego apunte `http.conf` a los archivos emitidos y recargue `res_http_websocket`:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Asegúrese de que el nombre del certificado coincida con el host al que se conecta el navegador, y renuévelo (el temporizador de certbot lo hace automáticamente) antes de que expire, o el WebSocket fallará.

Este certificado **no** es el mismo que el certificado DTLS usado para cifrar los medios — Asterisk genera ese automáticamente, como veremos.

## Paso 2 — el transporte WSS

PJSIP necesita un transporte del tipo `wss`. Agrégalo a `pjsip.conf`:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Verifica que se haya cargado:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

No te dejes engañar por el `0.0.0.0:5060` que se muestra para el transporte `wss` — el WebSocket **no** se sirve en el puerto 5060. La señalización WebRTC es servida por el servidor HTTP que configuraste en el Paso 1 (puerto 8089 para `wss`). El transporte PJSIP `wss` es una capa delgada sobre `res_http_websocket`, por lo que la dirección `bind` que se imprime es meramente estética y puede ser ignorada; el puerto que importa es `tlsbindaddr` en `http.conf`.

## Paso 3 — el punto final WebRTC

Ahora el propio punto final. La clave es `webrtc=yes`:

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
auth_type=digest
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` es un interruptor de conveniencia. Es equivalente a configurar a mano todas las
opciones requeridas por WebRTC. Puedes confirmar exactamente qué activó:

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

Leyendo esa salida:

- `media_encryption: dtls` y `dtls_auto_generate_cert: Yes` — el medio es DTLS‑SRTP,
  y Asterisk genera automáticamente el certificado DTLS, por lo que **no** debes crear uno
  tú mismo. La huella digital se anuncia en el SDP (`SHA-256`).
- `ice_support: true` — Asterisk recopila y negocia candidatos ICE.
- `rtcp_mux: true` — RTP y RTCP comparten un puerto, como esperan los navegadores.
- `use_avpf: true` — el perfil RTP AVPF (retroalimentación), requerido por WebRTC.

`allow=opus` es recomendado — Opus es el códec que prefieren los navegadores. Asterisk 22 incluye
Opus *passthrough* en el núcleo (el módulo `res_format_attr_opus`), lo cual es suficiente para
retransmitir Opus entre dos piernas compatibles con Opus sin recodificar. *Transcodificar* Opus a
otro códec requiere el módulo separado `codec_opus`, que la guía oficial de WebRTC
enumera como opcional pero altamente recomendado y que se instala sobre la
compilación base; consulta la discusión de códecs en *Designing a VoIP network*. Mantén `ulaw` como
alternativa para puentear a piernas no WebRTC que no pueden usar Opus.

## Paso 4 — ICE, STUN y TURN

En una LAN plana, ICE con candidatos de host es suficiente y no se necesita nada más. A través
de internet normalmente se agrega un servidor STUN para que Asterisk y el navegador puedan descubrir
sus direcciones públicas, y un servidor TURN para los casos en que los medios directos son
imposibles (NAT simétrico, firewalls restrictivos). Apunte Asterisk a ellos en
`rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

El navegador se configura con sus propios servidores ICE en JavaScript (la lista
`RTCPeerConnection` `iceServers`). Para una implementación puramente interna puede omitir
STUN/TURN por completo.

`turnaddr` toma un puerto opcional (por defecto `3478`); `turnusername` y `turnpassword`
se autentican en el relé. STUN solo ayuda a un par a *descubrir* su dirección pública — cuando
ambos extremos están detrás de NAT simétrico o un firewall restrictivo, los medios directos son
imposibles y un relé TURN es lo único que permite que el audio fluya.

**Recomendación para producción:** un servidor STUN público (como el de Google) está bien para
descubrir direcciones, pero **no** confíe en TURN público para tráfico real — los relés TURN
manejan todo su medio, por lo que debe estar bajo su control. Ejecute su propio
[coturn](https://github.com/coturn/coturn) servidor. Un `/etc/turnserver.conf` mínimo
con credenciales a largo plazo se ve así:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

Luego apunte Asterisk a él en `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Dé al navegador el mismo servidor TURN en su lista `iceServers` para que ambas piernas puedan retransmitir.
Para producción con usuarios en redes móviles o detrás de firewalls corporativos, un
coturn auto‑alojado es efectivamente obligatorio.

## Paso 5 — el cliente del navegador

Cualquier biblioteca WebRTC SIP funciona; dos de las más usadas son **SIP.js** y **JsSIP**. El
laboratorio incluye un softphone SIP.js mínimo en `lab/webrtc/index.html`. La parte esencial es la URL de transporte y las credenciales:

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

Dos realidades del navegador que recordar:

- **Contexto seguro.** `getUserMedia` (acceso al micrófono) solo funciona en páginas `https://`
  o `http://localhost`. Sirva la página mediante HTTPS en producción.
- **Aceptar el certificado una vez.** Con un certificado de laboratorio autofirmado, visite
  `https://your-asterisk:8089/ws` en el mismo navegador primero y acepte la advertencia,
  o el WebSocket fallará silenciosamente.

El softphone web SipPulse es un cliente de referencia de nivel producción construido sobre estos mismos
primitivos.

## Verificando una llamada WebRTC

Con el navegador registrado, `pjsip show contacts` muestra el contacto dinámico, y una
llamada ilumina el canal:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Si el audio es unidireccional o está ausente, casi siempre es ICE o el certificado — vea la solución de problemas a continuación.

## Asterisk WebRTC vs a media gateway

Asterisk puede terminar WebRTC directamente, pero no siempre es la herramienta adecuada:

- **Use Asterisk-native WebRTC** cuando el navegador es un *phone* en su PBX — un
  agente, una extensión interna, un click-to-call que llega a su dialplan. El
  navegador es simplemente otro endpoint y todo (colas, voicemail, IVR) funciona.
- **Use a dedicated gateway (e.g. Janus)** cuando necesita escalar muchas sesiones de navegador
  independientemente del control de llamadas, hacer reenvío selectivo para grandes
  conferencias/transmisiones, o mantener el plano de medios separado del PBX. Un gateway
  puentea WebRTC a SIP simple, y Asterisk entonces ve una pierna SIP ordinaria.

Muchos sistemas reales combinan ambos: Asterisk para el control de llamadas, un gateway para
escalar los medios del lado del navegador. (Esta es la arquitectura detrás del stack propio de SipPulse.)

## Troubleshooting

- **WebSocket won't connect:** the browser rejected the TLS certificate. Open
  `https://host:8089/ws` directly and accept it, or install a trusted cert.
- **Registers but no audio:** ICE failed — add STUN, and TURN if across NAT. Check
  `pjsip set logger on` and look at the SDP candidates.
- **One-way audio:** usually NAT/ICE on one side, or a codec with no common match —
  ensure `allow=opus,ulaw`.
- **Call drops at answer:** DTLS handshake failed; confirm `dtls_auto_generate_cert`
  is `Yes` and the system clock is correct (certs are time-sensitive).

## Laboratorio

1. Ejecute `./lab.sh up`, luego `bash lab/make-certs.sh` y reinicie Asterisk.  
2. Sirva `lab/webrtc/index.html` (`python3 -m http.server` desde `lab/webrtc`) y ábralo; acepte el certificado en `https://localhost:8089/ws`.  
3. Regístrese como `webrtc-1000` y llame a `600` (prueba de eco) — debería escucharse a sí mismo.  
4. Desde el Softphone SipPulse registrado como `6001`, marque `1000` para que suene el navegador.  
5. Inspeccione la negociación: `pjsip set logger on`, realice una llamada y encuentre la huella DTLS y los candidatos ICE en el SDP.

## Resumen

WebRTC convierte un navegador en un endpoint de Asterisk de primera clase. La receta es pequeña pero estricta: habilite el servidor HTTP con TLS para que el navegador pueda abrir un WebSocket seguro, agregue un `wss` transporte PJSIP, y establezca `webrtc=yes` en el endpoint — lo que activa DTLS‑SRTP (con un certificado generado automáticamente), ICE, multiplexación RTP/RTCP y el perfil AVPF. Añada STUN/TURN cuando atraviese NAT, sirva su página mediante HTTPS y apunte un cliente SIP.js (o JsSIP) a `wss://asterisk:8089/ws`. Para teléfonos de navegador en su PBX, WebRTC nativo de Asterisk es la ruta más simple; para medios a gran escala, combínelo con un gateway.

## Quiz

1. ¿Qué transporte usa un cliente de navegador WebRTC para transportar la señalización SIP a
   Asterisk?
   - A. UDP simple en el puerto 5060
   - B. Un WebSocket seguro (`wss://`) al servidor HTTP de Asterisk
   - C. TLS en el puerto 5061
   - D. Un socket TCP sin procesar en el puerto 8088

2. ¿El medio de WebRTC entre el navegador y Asterisk está cifrado usando qué mecanismo?
   - A. SDES‑SRTP (claves intercambiadas en el SDP)
   - B. DTLS‑SRTP (claves derivadas de un apretón de manos DTLS)
   - C. IPsec
   - D. RTP simple — WebRTC no cifra el medio

3. Verdadero o falso: cuando configuras `webrtc=yes`, debes generar e instalar manualmente
   el certificado DTLS usado para cifrar el medio.

4. ¿En qué puerto expone el servidor HTTP de Asterisk del laboratorio el WebSocket **seguro**
   para WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. ¿Cuál de los siguientes activa `webrtc=yes` por defecto? (Elige todas las que correspondan.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Completa el espacio en blanco: WebRTC negocia la conectividad haciendo que ambos lados recopilen y
   prueben direcciones candidatas (host, STUN‑reflexive, TURN‑relayed) usando el
   marco ________.

7. En `rtp.conf`, ¿qué dos configuraciones apuntan a Asterisk a un servidor externo para que pueda
   descubrir su dirección pública y reenviar el medio cuando fallan las rutas directas? (Elige todas
   las que correspondan.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. La ruta URL que expone `res_http_websocket` de Asterisk para la señalización WebRTC es
   ________.

9. Según el capítulo, ¿cuándo deberías usar una pasarela de medios dedicada
   (como Janus) en lugar de WebRTC nativo de Asterisk?
   - A. Cada vez que cualquier navegador necesite realizar una llamada
   - B. Cuando debas escalar muchas sesiones de medios de navegador independientemente del control de llamadas, hacer reenvío selectivo para conferencias grandes, o mantener el plano de medios separado del PBX
   - C. Sólo cuando el navegador no soporta DTLS
   - D. Cuando quieras que el buzón de voz y el IVR funcionen para el punto final del navegador

10. Verdadero o falso: `getUserMedia` (acceso al micrófono) funciona en cualquier página `http://`, por lo que
    servir el softphone del navegador sobre HTTPS es opcional.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
