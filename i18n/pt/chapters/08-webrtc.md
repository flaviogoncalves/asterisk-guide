# WebRTC com Asterisk

WebRTC (Web Real-Time Communication) permite que um navegador da web faça e receba chamadas sem plug‑in e sem softphone externo — apenas JavaScript, um microfone e uma conexão segura ao Asterisk. O Asterisk pode atuar como servidor WebRTC desde o Asterisk 11, e desde que a pilha PJSIP (`res_pjsip`) chegou ao Asterisk 12 ela tem sido a forma recomendada de fazê‑lo; no Asterisk 22 a configuração se consolidou em um pequeno conjunto de opções bem compreendidas. Este capítulo mostra como transformar um endpoint PJSIP em um telefone de navegador, como funciona o caminho de mídia segura e quando você deve usar o suporte WebRTC nativo do Asterisk versus um gateway dedicado.

Tudo neste capítulo foi verificado com o laboratório do livro para Asterisk 22; a configuração mostrada é a mesma de `lab/asterisk/etc`.

## Objectives

Ao final deste capítulo, você deverá ser capaz de:

- Explicar o que o WebRTC adiciona ao Asterisk e quando utilizá‑lo
- Descrever como a segurança de mídia do WebRTC (DTLS‑SRTP) e o ICE diferem do SIP simples
- Habilitar o servidor HTTP do Asterisk e o endpoint WebSocket seguro (`wss`)
- Configurar um transporte PJSIP `wss` e um endpoint WebRTC com `webrtc=yes`
- Conectar um softphone de navegador (SIP.js) e efetuar uma chamada
- Decidir entre o WebRTC nativo do Asterisk e um gateway de mídia como o Janus

## Por que usar WebRTC com Asterisk

Um endpoint WebRTC é, do ponto de vista do Asterisk, apenas outro endpoint PJSIP. O que muda é *como* o navegador o alcança e como a mídia é protegida. Usos típicos incluem:

- **Click-to-call** em um site — um visitante liga para uma fila ou uma extensão a partir de uma página web.
- **Agentes baseados na web** — um agente de contact center trabalha totalmente no navegador, sem precisar instalar ou atualizar um softphone de desktop.
- **Chamadas incorporadas** em sua própria aplicação web — por exemplo, o softphone web SipPulse conversando com o Asterisk.
- **Phones internos sem instalação** — a equipe usa uma aba do navegador em vez de um telefone físico ou cliente instalado.

A grande vantagem é o alcance: todo navegador moderno já suporta WebRTC. O custo é que o WebRTC é rigoroso — ele *exige* mídia criptografada e um transporte seguro, portanto há mais configuração necessária do que para um telefone SIP UDP simples.

## Como o WebRTC difere do SIP simples

Um telefone SIP regular sinaliza sobre UDP/TCP e geralmente transporta áudio como RTP simples. Um cliente de navegador WebRTC é diferente em três aspectos importantes, e o Asterisk precisa corresponder a cada um:

- **O sinalização viaja em um WebSocket.** Em vez de SIP sobre UDP na porta 5060, o navegador abre um WebSocket seguro (`wss://`) para o servidor HTTP embutido do Asterisk. Mensagens SIP trafegam dentro desse WebSocket.
- **A mídia está sempre criptografada com DTLS‑SRTP.** Navegadores recusam RTP simples. As duas partes realizam um handshake DTLS (autenticado por impressões digitais de certificados trocadas no SDP) e derivam chaves SRTP a partir dele.
- **A conectividade é negociada com ICE.** Em vez de assumir um IP e porta alcançáveis, ambas as partes coletam endereços candidatos (host, STUN‑reflexivo, TURN‑reencaminhado) e os testam até que um funcione. RTP e RTCP geralmente são multiplexados em uma única porta (`rtcp_mux`).

A boa notícia: no Asterisk 22 uma única opção de endpoint, `webrtc=yes`, ativa tudo isso com padrões sensatos. Veremos exatamente o que ela configura.

## Step 1 — the HTTP server and the WebSocket

WebRTC signaling is served by Asterisk's built-in HTTP server (`res_http_websocket`
exposes the `/ws` path on it). Browsers require a *secure* WebSocket, so we enable
TLS. Edit `http.conf`:

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

Reload (`module reload res_http_websocket` or restart) and confirm:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

The browser will connect to `wss://your-asterisk:8089/ws`.

### About the certificate

The TLS certificate here secures the *WebSocket* (the signaling channel). In a lab
a self-signed certificate is fine — you accept it once in the browser. In
production use a real certificate (for example Let's Encrypt) whose name matches
the host the browser connects to, otherwise the browser will refuse the WebSocket.

For the lab, `lab/make-certs.sh` generates a self-signed certificate with
`CN=localhost` (plus `localhost`/`127.0.0.1` SANs) and writes it to
`asterisk/etc/keys/`. For a public deployment, obtain a real certificate instead — for
example with Let's Encrypt:

```
certbot certonly --standalone -d voip.example.com
```

Then point `http.conf` at the issued files and reload `res_http_websocket`:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Make sure the certificate name matches the host the browser connects to, and renew it
(certbot's timer does this automatically) before it expires, or the WebSocket will fail.

This certificate is **not** the same as the DTLS certificate used to encrypt the
media — Asterisk generates that one automatically, as we will see.

## Step 2 — the WSS transport

PJSIP needs a transport of type `wss`. Add it to `pjsip.conf`:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Verify it loaded:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

Do not be misled by the `0.0.0.0:5060` shown for the `wss` transport — the WebSocket
is **not** served on port 5060. WebRTC signaling is served by the HTTP server you
configured in Step 1 (port 8089 for `wss`). The PJSIP `wss` transport is a thin shim
over `res_http_websocket`, so the `bind` address printed for it is cosmetic and can be
ignored; the port that matters is `tlsbindaddr` in `http.conf`.

## Step 3 — the WebRTC endpoint

Now the endpoint itself. The key is `webrtc=yes`:

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

`webrtc=yes` is a convenience switch. It is equivalent to setting all of the
WebRTC-required options by hand. You can confirm exactly what it turned on:

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

Reading that output:

- `media_encryption: dtls` and `dtls_auto_generate_cert: Yes` — media is DTLS-SRTP,
  and Asterisk auto-generates the DTLS certificate, so you do **not** create one
  yourself. The fingerprint is advertised in the SDP (`SHA-256`).
- `ice_support: true` — Asterisk gathers and negotiates ICE candidates.
- `rtcp_mux: true` — RTP and RTCP share one port, as browsers expect.
- `use_avpf: true` — the AVPF RTP profile (feedback), required by WebRTC.

`allow=opus` is recommended — Opus is the codec browsers prefer. Asterisk 22 ships
Opus *passthrough* in core (the `res_format_attr_opus` module), which is enough to
relay Opus between two Opus-capable legs without re-encoding. *Transcoding* Opus to
another codec requires the separate `codec_opus` module, which the official WebRTC
guide lists as optional but highly recommended and which you install on top of the
base build; see the codecs discussion in *Designing a VoIP network*. Keep `ulaw` as a
fallback for bridging to non-WebRTC legs that cannot speak Opus.

## Step 4 — ICE, STUN and TURN

Em uma LAN plana, ICE com candidatos host é suficiente e nada mais é necessário. Na internet você normalmente adiciona um servidor STUN para que Asterisk e o navegador possam descobrir seus endereços públicos, e um servidor TURN para os casos em que a mídia direta é impossível (NAT simétrico, firewalls restritivos). Aponte o Asterisk para eles em `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

O navegador é configurado com seus próprios servidores ICE em JavaScript (a lista `RTCPeerConnection` `iceServers`). Para uma implantação puramente interna você pode pular STUN/TURN completamente.

`turnaddr` aceita uma porta opcional (padrão `3478`); `turnusername` e `turnpassword` autenticam no relé. STUN apenas ajuda um par a *descobrir* seu endereço público — quando ambas as pontas estão atrás de NAT simétrico ou firewall restritivo, a mídia direta é impossível e um relé TURN é a única coisa que faz o áudio fluir.

**Recomendação para produção:** um servidor STUN público (como o do Google) é suficiente para descoberta de endereço, mas **não** dependa de TURN público para tráfego real — relés TURN encaminham toda a sua mídia, então você quer que estejam sob seu controle. Execute seu próprio servidor [coturn](https://github.com/coturn/coturn). Um `/etc/turnserver.conf` mínimo com credenciais de longo prazo se parece com:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

Então aponte o Asterisk para ele em `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Forneça ao navegador o mesmo servidor TURN em sua lista `iceServers` para que ambas as pernas possam retransmitir. Para produção com usuários em redes móveis ou atrás de firewalls corporativos, um coturn auto-hospedado é efetivamente obrigatório.

## Step 5 — the browser client

Qualquer biblioteca WebRTC SIP funciona; duas amplamente usadas são **SIP.js** e **JsSIP**. O
laboratório inclui um softphone SIP.js mínimo em `lab/webrtc/index.html`. A parte essencial
é a URL de transporte e as credenciais:

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

Duas realidades do navegador a serem lembradas:

- **Secure context.** `getUserMedia` (acesso ao microfone) só funciona em páginas `https://`
  ou `http://localhost`. Sirva a página via HTTPS em produção.
- **Accept the cert once.** Com um certificado auto‑assinado do laboratório, acesse
  `https://your-asterisk:8089/ws` no mesmo navegador primeiro e aceite o aviso,
  ou o WebSocket falhará silenciosamente.

O softphone web SipPulse é um cliente de referência de nível de produção construído sobre esses mesmos
primitivos.

## Verificando uma chamada WebRTC

Com o navegador registrado, `pjsip show contacts` mostra o contato dinâmico, e uma chamada acende o canal:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Se o áudio for unidirecional ou ausente, quase sempre é ICE ou o certificado — veja a solução de problemas abaixo.

## Asterisk WebRTC vs um gateway de mídia

- **Use Asterisk-native WebRTC** quando o navegador é um *phone* no seu PBX — um agente, uma extensão interna, um click-to-call que chega ao seu dialplan. O navegador é apenas outro endpoint e tudo (queues, voicemail, IVR) funciona.
- **Use a dedicated gateway (e.g. Janus)** quando você precisa escalar muitas sessões de navegador independentemente do controle de chamadas, fazer encaminhamento seletivo para grandes conferências/streaming, ou manter o plano de mídia separado do PBX. Um gateway faz a ponte entre WebRTC e SIP puro, e o Asterisk então vê uma perna SIP ordinária.

Muitos sistemas reais combinam ambos: Asterisk para controle de chamadas, um gateway para escalonamento de mídia do lado do navegador. (Esta é a arquitetura por trás da própria pilha da SipPulse.)

## Solução de Problemas

- **WebSocket won't connect:** o navegador rejeitou o certificado TLS. Abra `https://host:8089/ws` diretamente e aceite‑o, ou instale um certificado confiável.  
- **Registers but no audio:** ICE falhou — adicione STUN, e TURN se estiver atravessando NAT. Verifique `pjsip set logger on` e examine os candidatos SDP.  
- **One-way audio:** geralmente NAT/ICE em um dos lados, ou um codec sem correspondência comum — assegure que `allow=opus,ulaw`.  
- **Call drops at answer:** a negociação DTLS falhou; confirme que `dtls_auto_generate_cert` está `Yes` e que o relógio do sistema está correto (certificados são sensíveis ao tempo).

## Laboratório

1. Execute `./lab.sh up`, depois `bash lab/make-certs.sh` e reinicie o Asterisk.  
2. Sirva `lab/webrtc/index.html` (`python3 -m http.server` de `lab/webrtc`) e abra‑lo; aceite o certificado em `https://localhost:8089/ws`.  
3. Registre‑se como `webrtc-1000` e ligue para `600` (teste de eco) — você deve ouvir a sua própria voz.  
4. Do Softphone SipPulse registrado como `6001`, disque `1000` para fazer o navegador tocar.  
5. Inspecione a negociação: `pjsip set logger on`, inicie uma chamada e localize a impressão digital DTLS e os candidatos ICE no SDP.

## Resumo

WebRTC transforma um navegador em um endpoint Asterisk de primeira classe. A receita é pequena, mas rigorosa: habilite o servidor HTTP com TLS para que o navegador possa abrir um WebSocket seguro, adicione um transporte PJSIP `wss`, e defina `webrtc=yes` no endpoint — o que ativa DTLS-SRTP (com um certificado gerado automaticamente), ICE, multiplexação RTP/RTCP e o perfil AVPF. Adicione STUN/TURN ao atravessar NAT, sirva sua página via HTTPS e aponte um cliente SIP.js (ou JsSIP) para `wss://asterisk:8089/ws`. Para telefones de navegador no seu PBX, o WebRTC nativo do Asterisk é o caminho mais simples; para mídia em grande escala, combine‑o com um gateway.

## Quiz

1. Which transport does a WebRTC browser client use to carry SIP signaling to
   Asterisk?
   - A. Plain UDP on port 5060
   - B. A secure WebSocket (`wss://`) to Asterisk's HTTP server
   - C. TLS on port 5061
   - D. A raw TCP socket on port 8088

2. WebRTC media between the browser and Asterisk is encrypted using which mechanism?
   - A. SDES-SRTP (keys exchanged in the SDP)
   - B. DTLS-SRTP (keys derived from a DTLS handshake)
   - C. IPsec
   - D. Plain RTP — WebRTC does not encrypt media

3. True or false: when you set `webrtc=yes`, you must manually generate and install
   the DTLS certificate used to encrypt the media.

4. On which port does the lab's Asterisk HTTP server expose the **secure** WebSocket
   for WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Which of the following does `webrtc=yes` turn on by default? (Choose all that
   apply.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Fill in the blank: WebRTC negotiates connectivity by having both sides gather and
   probe candidate addresses (host, STUN-reflexive, TURN-relayed) using the
   ________ framework.

7. In `rtp.conf`, which two settings point Asterisk at an external server so it can
   discover its public address and relay media when direct paths fail? (Choose all
   that apply.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. The URL path that Asterisk's `res_http_websocket` exposes for WebRTC signaling is
   ________.

9. According to the chapter, when should you reach for a dedicated media gateway
   (such as Janus) instead of Asterisk-native WebRTC?
   - A. Whenever any browser needs to make a call
   - B. When you must scale many browser media sessions independently of call
     control, do selective forwarding for large conferences, or keep the media plane
     separate from the PBX
   - C. Only when the browser does not support DTLS
   - D. When you want voicemail and IVR to work for the browser endpoint

10. True or false: `getUserMedia` (microphone access) works on any `http://` page, so
    serving the browser softphone over HTTPS is optional.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
