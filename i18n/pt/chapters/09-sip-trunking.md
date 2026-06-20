# SIP trunking, DID & the PSTN

Um PBX que só pode ligar para ele mesmo não é muito útil. Mais cedo ou mais tarde todo sistema
precisa alcançar o resto do mundo — a rede telefônica pública comutada
(PSTN), um provedor SIP ou outro PBX. O link que transporta essas chamadas é um
**trunk**. Na era TDM um trunk era um circuito físico: um T1/E1 PRI ou um conjunto
de linhas analógicas FXO. Hoje ele é quase sempre um **SIP trunk** — uma conexão
lógica a um Internet Telephony Service Provider (ITSP) transportada sobre a mesma
rede IP que todo o resto.

Este capítulo mostra como conectar o Asterisk 22 a um ITSP com PJSIP, como escolher
entre um trunk baseado em registro e um trunk baseado em IP, como rotear números DID
entrantes para o destino correto, como enviar chamadas externas com ID de chamada
correto e formatação E.164, e como construir failover e roteamento de menor custo
através de vários trunks. Terminamos com o tratamento de NAT para trunks e um laboratório que
levanta um segundo Asterisk (e SIPp) como um ITSP simulado para que você possa fazer chamadas reais
através de um trunk.

Tudo aqui foi verificado contra o laboratório do livro para Asterisk 22.10.0; o padrão
de objeto trunk é o mesmo introduzido em *Building your first PBX with PJSIP*
e *SIP & PJSIP in depth*.

## Objectives

Ao final deste capítulo, você deverá ser capaz de:

- Conectar o Asterisk 22 a um ITSP usando PJSIP
- Escolher entre troncos baseados em registro e troncos baseados em IP (estáticos)
- Roteir DIDs de entrada para a extensão, IVR ou fila corretas
- Roteir chamadas de saída com ID de chamada adequado e formatação E.164
- Construir failover de tronco e roteamento de menor custo com `${DIALSTATUS}`
- Gerenciar NAT para troncos no transporte e no endpoint

## O que é um tronco SIP

Um tronco SIP é um caminho lógico de voz entre seu PBX e outro sistema SIP. Na prática, esse “outro sistema” é uma das duas coisas:

- **Um ITSP (Internet Telephony Service Provider).** Um operadora comercial que lhe vende origem e terminação de chamadas e, geralmente, um bloco de números de telefone (DIDs). Você aponta o Asterisk para o host de sinalização do provedor, e o provedor conecta suas chamadas à rede PSTN mais ampla. É assim que a maioria dos sistemas modernos alcança a rede telefônica — sem necessidade de hardware de telefonia.
- **Um gateway PSTN.** Um dispositivo (ou outro Asterisk) que possui interfaces físicas PSTN — uma placa PRI, portas analógicas FXO ou um gateway GSM/4G — e as apresenta ao seu PBX como SIP. O gateway faz a conversão TDM‑para‑SIP; do ponto de vista do Asterisk, ele é apenas outro tronco SIP.

De qualquer forma, no PJSIP um tronco é **apenas um endpoint**. A mesma família de objetos que você usou para um telefone — `endpoint`, `auth`, `aor`, opcionalmente `identify` e `registration` — constrói um tronco. As diferenças estão nos detalhes: um tronco autentica *saída* (você é o cliente, então as credenciais vão em `outbound_auth`, não em `auth`), normalmente não registra um agente de usuário para você (você se registra nele, ou ele lhe envia tráfego de um IP conhecido), e direciona chamadas recebidas para um contexto dedicado como `from-pstn` em vez de `from-internal`.

> **Comparado ao antigo tronco TDM.** Um PRI lhe fornecia um número fixo de B‑channels (23 em um T1, 30 em um E1) e sinalizava o estabelecimento de chamadas por um D‑channel dedicado (veja o capítulo *Canais legados*). Um tronco SIP não tem contagem fixa de canais — a capacidade é o que sua largura de banda, a política do provedor e quaisquer limites `max_contacts`/de chamadas simultâneas permitirem. Caller‑ID, DID e progresso de chamada que antes viajavam em elementos de informação ISDN agora viajam em cabeçalhos SIP e SDP.

Existem duas maneiras pelas quais um ITSP concordará em trocar tráfego com você, e elas determinam como você constrói o tronco: **baseado em registro** e **baseado em IP (estático)**. Abordaremos cada uma a seguir.

## Trunks baseados em registro

Um trunk baseado em registro é o modelo usado quando o provedor espera que *você* faça login *neles*. Seu Asterisk periodicamente envia um SIP `REGISTER` ao provedor, autenticando com um nome de usuário e senha, exatamente como um telefone se registra ao seu PBX. Isso é comum quando seu IP público é dinâmico, quando você está atrás de NAT, ou quando o provedor simplesmente identifica clientes por credenciais SIP em vez de por endereço IP.

Em PJSIP o login de saída vive em um objeto `registration` dedicado. Ele substitui a única linha `register =>` que o driver `chan_sip` removido usava em `sip.conf`. Aqui está um trunk de registro completo para um provedor fictício, seguindo o padrão verificado dos capítulos anteriores — note `outbound_auth` (não `auth`), `server_uri`/`client_uri` (não `server`/`client`), `from_user`/`from_domain` no endpoint e `dtmf_mode=rfc4733`:

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

Algumas coisas a observar:

- **`auth_type=digest`, não `userpass`.** Ambos produzem a mesma autenticação digest, mas no Asterisk 22 `userpass` (e o antigo `md5`) são **obsoletos e convertidos silenciosamente para `digest`**. Prefira `digest` em novas configurações; você ainda verá `userpass` em arquivos mais antigos e nos capítulos anteriores deste livro.
- **`outbound_auth` tanto no endpoint quanto no registro.** O registro o usa para autenticar o `REGISTER`; o endpoint o usa para responder ao `407 Proxy Authentication Required` que o provedor envia de volta a um outbound `INVITE`. Eles podem compartilhar um único objeto `auth`.
- **`from_user` / `from_domain`.** Muitos provedores rejeitam chamadas cujo cabeçalho `From` não contém seu número de conta e seu domínio. Essas duas opções definem exatamente isso.
- **`contact_user=4830001000`.** Isso se torna a parte do usuário do `Contact` que você registra, de modo que o provedor saiba para qual número entregar chamadas inbound. É o equivalente moderno do sufixo `/9999` na antiga linha `register =>`.
- **`retry_interval=60`.** Se o registro falhar, tente novamente a cada 60 segundos.

Após um reload, confirme o registro com `pjsip show registrations`. No laboratório — onde `itsp.example.com` não responde de fato — a tabela fica assim:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

O sufixo `(exp. Ns)` conta regressivamente os segundos até a próxima tentativa; quando chega a zero ele exibe brevemente `(exp. Ns ago)` antes que a nova tentativa seja disparada. Contra um provedor real a coluna `Status` mostra `Registered` com os segundos restantes até a próxima atualização. `Rejected` (ou `Unregistered`) significa que o provedor não aceitou o login — ative `pjsip set logger on` e leia a resposta `401`/`403`, quase sempre um nome de usuário, senha ou domínio `client_uri` incorretos.

## IP-based (static) trunks

O segundo modelo não requer registro algum. O provedor conhece seu endereço IP público e envia chamadas diretamente para ele; você, por sua vez, envia chamadas para o IP de sinalização conhecido do provedor. A autenticação é feita por **endereço IP de origem**, não por credenciais SIP. Isso é típico para trunks entre dois servidores que você controla, ou para um trunk empresarial onde ambos os lados têm endereços estáticos.

O objeto chave é `identify`. Ele diz ao Asterisk: "qualquer requisição SIP que chegar deste IP *pertence* àquele endpoint." Sem ele, o PJSIP tenta corresponder uma requisição inbound a um endpoint pelo usuário `From`, o que o tráfego de uma operadora não satisfaz — então a chamada seria rejeitada ou cairia no endpoint `anonymous`.

Um trunk estático elimina o objeto `registration` e adiciona `identify`:

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

`match` aceita um endereço IP, um intervalo CIDR ou um nome de host. **Nomes de host são resolvidos uma única vez, no carregamento da configuração**, portanto, se o IP do seu provedor mudar você deverá recarregar. Para uma operadora que publica vários gateways de mídia, liste cada IP de sinalização — você pode repetir `match` ou fornecer um CIDR:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Verifique o que o Asterisk aceitará com `pjsip show identifies`. Capturado do laboratório (a linha `sipp-identify` é o endpoint SIPp pré‑existente do laboratório):

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

### The security implication

Um trunk baseado em IP sem autenticação é uma porta, e `identify`/`match` é a única fechadura nela. Se você `match` um intervalo muito amplo — ou se um atacante puder falsificar um IP de origem — as chamadas chegam ao seu contexto `from-pstn` não autenticadas. Duas defesas, usadas em conjunto:

- **Correspondência o mais restrita possível.** Prefira IPs de host específicos em vez de CIDRs amplos. Apenas os verdadeiros IPs de sinalização do provedor pertencem a `match`.
- **Combine isso com uma ACL.** O PJSIP pode descartar tráfego na camada SIP antes que ele chegue a um endpoint, usando um objeto `type=acl` (ou `acl.conf`):

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Uma seção `type=acl` não precisa de referência: `res_pjsip_acl` aplica cada um desses objetos a *todo* o tráfego SIP inbound antes que ele alcance qualquer endpoint. (As opções `acl` e `contact_acl` no objeto puxam listas de regras nomeadas de `acl.conf` ao invés de listar `permit`/`deny` inline como acima.) O princípio é o mesmo do capítulo SIP: negar tudo, então permitir apenas o que você confia. E seja qual for o contexto do seu trunk,
**nunca o deixe alcançar um contexto que possa discar de volta para a PSTN** sem uma regra deliberada e autenticada — esse é o clássico buraco de fraude de tarifas.

> **Which model should I use?** If the provider gives you a username and password,
> use a **registration** trunk. If they ask for your IP address and give you
> theirs, use an **identify** trunk. Some providers support both; many real
> trunks combine a registration (so the provider can find you) with an identify
> (so inbound INVITEs from the provider's media gateways are matched even when
> they arrive from an IP other than the registrar).

## Roteamento de entrada e tratamento de DID

Uma vez que as chamadas de entrada chegam, elas caem no `context` do endpoint — aqui
`from-pstn`. Um **DID** (número de Discagem Direta Interna) é simplesmente o número discado
que o provedor entrega a você no URI da requisição. Seu trabalho no dialplan é mapear cada
DID para um destino: uma única extensão, um IVR, uma fila ou um grupo de toque.

O número que o provedor envia é comparado como `${EXTEN}` em `from-pstn`. Quanto dele você vê depende do provedor — alguns enviam o número completo no formato E.164
(`+4830001000`), outros enviam o número nacional, outros enviam apenas os últimos
dígitos. Inspecione uma chamada de entrada real com `pjsip set logger on` e observe o
URI da requisição antes de escrever padrões.

### Um DID para uma extensão

O caso mais simples — um único DID roteado diretamente para um telefone:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### Um DID para um IVR (atendente automático)

Um número principal que deve atender com um menu em vez de tocar um telefone:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` é o contexto de atendente automático que você criou nos capítulos do dialplan
(`Background()` + `WaitExten()`). Roteando o DID é apenas um `Goto`.

### Um DID para uma fila

Uma linha de suporte que deve entrar em uma fila de chamadas:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Vários DIDs de uma vez

Quando você compra um bloco de números, um padrão mantém o dialplan pequeno. Suponha que sua
faixa de DIDs seja `4830003000`–`4830003099` e o provedor envie o número completo; mapeie
os dois últimos dígitos de cada DID para a extensão `60xx`:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` obtém os dois últimos dígitos (deslocamento negativo conta a partir da direita),
então `4830003007` toca `PJSIP/6007`. Uma tabela de consulta `did => extension` construída com
`GoSub` ou um banco de dados Asterisk (`AstDB`/`func_odbc`) escala ainda mais, mas para
um pequeno número de DIDs padrões explícitos são os mais claros.

> **Capture o DID não correspondido.** Adicione uma extensão `i` (inválida) a `from-pstn` para que um
> número de entrada mal roteado reproduza um anúncio ou toque o operador em vez de
> ser descartado silenciosamente:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Roteamento de saída, caller-ID e E.164

Chamadas de saída fluem no sentido oposto: um telefone interno disca um número, seu dialplan
o corresponde, remove qualquer prefixo de acesso, define o caller-ID que o provedor espera e
encaminha a chamada para o endpoint trunk com `Dial(PJSIP/<number>@itsp)`.

### Enviando a chamada para o trunk

A sintaxe do canal para um trunk é `PJSIP/<number>@<endpoint>`: a parte antes do
`@` torna‑se a porção de usuário do URI de requisição de saída, e a parte após o
`@` nomeia o endpoint cujo `aor` `contact` fornece o host de destino. Uma regra clássica “disque 9 para uma linha externa”:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` remove o código de acesso `9` inicial antes que o número seja enviado. O
padrão `_9NXXXXXXXXX` corresponde a `9` mais um número de 10 dígitos cujo primeiro dígito é
2–9; ajuste-o ao seu plano de discagem.

### Caller-ID em chamadas de saída

A maioria dos ITSPs ignora — ou rejeita ativamente — um caller-ID que não seja um número que você possua.
Defina o número de caller-ID de saída para um dos seus DIDs com a função `CALLERID(num)`
antes de `Dial()`, como mostrado acima. Você também pode definir o nome:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

Se o provedor ainda remover ou sobrescrever o nome do seu caller-ID, essa é a política dele — muitos operadores obtêm o nome exibido de seu próprio banco de dados CNAM
associado ao número, não do seu cabeçalho `From`.

Duas opções de endpoint interagem com isso:

- **`from_user`** define a parte de usuário do cabeçalho `From` no nível SIP, que
  alguns provedores usam para identificar sua conta independentemente de `CALLERID(num)`.
- **`trust_id_outbound`** (padrão `no`) controla se o Asterisk enviará
  cabeçalhos de identidade sensíveis à privacidade (`P-Asserted-Identity`/`P-Preferred-Identity`)
  na saída. Deixe desativado a menos que seu provedor documente que deseja PAI, caso
  em que configure `trust_id_outbound=yes` e `send_pai=yes`.

### Normalizando para E.164

E.164 é o formato internacional de número: um `+` inicial, código do país, depois o
número nacional, sem espaços ou pontuação (por exemplo `+5548999990000` ou
`+14155550100`). Os operadores cada vez mais esperam — ou exigem — E.164 no trunk.
Em vez de espalhar a formatação pelo dialplan, normalize uma única vez no contexto de saída.

Um exemplo norte‑americano que aceita um número local de 10 dígitos, um número de 11 dígitos
com prefixo `1`, ou um número já em E.164, e sempre apresenta `+1…` ao
trunk:

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

Alguns provedores desejam o `+`; outros querem apenas os dígitos. Se o seu rejeitar o
`+`, remova‑o na saída com `${EXTEN:1}` no `Dial`. O ponto é que
todo o conhecimento de formato fica em um único lugar, então trocar de provedor — ou adicionar um
segundo — é uma mudança de uma linha.

## Failover and least-cost routing

Com um tronco, uma falha do provedor significa que não há chamadas de saída. Com dois ou mais, você pode fazer failover automaticamente e ainda escolher a rota mais barata por destino — *least-cost routing* (LCR).

### Failover com `${DIALSTATUS}`

`Dial()` define a variável de canal `${DIALSTATUS}` quando retorna. Os valores que importam para failover são `CHANUNAVAIL` (o tronco não pôde ser alcançado) e `CONGESTION` (a chamada foi rejeitada, por exemplo, todos os circuitos ocupados). Tente o tronco primário; se ele não puder transportar a chamada, passe para o backup:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Observe a escolha deliberada **não** fazer failover em `BUSY` ou `NOANSWER` — esses indicam que a *parte chamada* foi alcançada e recusou, então tentar novamente em outro tronco faria o telefone tocar novamente quando já havia dito não (e poderia custar uma segunda chamada). Redirecione apenas quando o *próprio tronco* falhar.

### Uma subrotina de roteamento reutilizável

Repetir essa lógica para cada padrão de discagem é propenso a erros. Refatore-a em uma rotina `GoSub` que recebe o número de destino e tenta cada tronco na ordem:

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

Agora cada padrão de saída é uma chamada `GoSub`, e a ordem dos troncos é definida em **um único** lugar.

### Least-cost routing por destino

Um LCR verdadeiro escolhe o tronco de acordo com o destino da chamada. Um padrão comum é combinar o prefixo de destino e enviar cada classe de chamada ao provedor que for mais barato para ela — por exemplo, chamadas internacionais para um carrier wholesale e chamadas locais/nacionais para o seu tronco primário:

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

Para mais de alguns prefixos, armazene a tabela de rotas em um banco de dados (`func_odbc`/`AstDB`) e procure o tronco pelo prefixo em vez de codificar os padrões. O dialplan permanece pequeno e as tarifas ficam em uma tabela que pode ser editada sem recarregar a lógica.

## NAT and trunks

NAT é a causa única mais comum de problemas em trunks — tipicamente áudio unidirecional,
ou um trunk que registra mas nunca recebe chamadas inbound. A causa é a mesma
dos telefones (abordada em *SIP & PJSIP in depth* e *Designing a VoIP network*):
Asterisk anuncia sua própria ideia de endereço em SIP e SDP, e atrás de NAT
esse é um endereço privado RFC 1918 que o provedor não pode rotear de volta.

Para trunks a correção tem duas partes — configurações no **transport** (seu endereço público) e configurações no **endpoint** (como tratar a mídia do provedor).

### On the transport — your public address

Quando o próprio servidor Asterisk está atrás de NAT (uma máquina na nuvem ou on‑prem com
um IP privado e um IP público 1:1), informe ao transport seu endereço público e quais
redes são locais. Essas opções são definidas uma única vez, no `transport`, e se aplicam a
todo o tráfego sobre ele:

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

- **`external_signaling_address`** — o IP público que Asterisk grava nos cabeçalhos SIP
  (`Via`, `Contact`) para destinos fora de `local_net`.
- **`external_media_address`** — o IP público que Asterisk grava na linha SDP `c=`
  para que o RTP retorne ao lugar correto. Normalmente idêntico ao endereço de sinalização.
- **`local_net`** — redes que Asterisk trata como internas, portanto *não* reescreve
  endereços para pares LAN. Liste todas as sub‑redes internas.

### On the endpoint — the provider's media

A outra metade lida com um provedor que também está atrás de NAT, ou simplesmente envia
mídia de um endereço diferente daquele presente em seu SDP. Defina estas opções por endpoint de trunk:

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

- **`direct_media=no`** — mantenha a mídia fluindo através do Asterisk ao invés de permitir
  que as duas pernas conversem diretamente. Essencial através de NAT, e necessário de qualquer forma se você
  quiser gravar, transcodificar ou monitorar a chamada.
- **`rtp_symmetric=yes`** — o comportamento clássico *comedia*: envie RTP de volta para o
  endereço de onde a mídia realmente veio, não para o endereço que o SDP indica.
- **`force_rport=yes`** — responda ao SIP a partir do IP/porta de origem da requisição
  (RFC 3581), ao invés de confiar no cabeçalho `Via`.
- **`rewrite_contact=yes`** — em mensagens SIP inbound desse endpoint, reescreva
  o cabeçalho `Contact` (ou um cabeçalho `Record-Route` apropriado) para o IP
  de origem e porta de onde o pacote realmente veio. Conforme a própria
  documentação da opção, isso "ajuda servidores a comunicar com endpoints que estão atrás
  de NATs" e "ajuda a reutilizar conexões de transporte confiáveis como TCP e TLS."

> **Recommendation — phones vs trunks.** `rewrite_contact` é quase sempre a
> escolha correta para telefones, porque o contato anunciado geralmente é um endereço privado
> RFC 1918 que não é roteável de volta para eles. Em um trunk baseado em IP estático
> o contato do provedor costuma já ser um endereço público correto, então reescrevê‑lo
> muitas vezes é desnecessário; alguns operadores preferem deixá‑lo desativado aí e habilitá‑lo
> apenas para trunks de registro e telefones NAT‑ados. O efeito documentado da
> opção é puramente a reescrita inbound `Contact`/`Record-Route` acima — portanto a
> prática segura é testar com sua operadora específica antes de ativá‑la em um
> trunk estático.

Você pode confirmar as configurações efetivas em qualquer endpoint com
`pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`,
`rewrite_contact`, e o restante é impresso no dump de parâmetros.

## Lab — um ITSP simulado com um segundo Asterisk e SIPp

Você não precisa de um tronco pago para praticar. O laboratório do livro já executa um contêiner Asterisk
22.10.0 e um contêiner SIPp em uma rede privada `172.30.0.0/24`; trataremos o contêiner SIPp como o “operador” que faz chamadas inbound, e adicionaremos um
endpoint de tronco que direciona essas chamadas para um contexto `from-pstn`.

![Um tronco SIP entre o PBX Asterisk e o ITSP: o PBX registra como uma conta, chamadas outbound discam `PJSIP/<num>@trunk`, e chamadas inbound chegam ao contexto `from-pstn`](../images/09-sip-trunking-fig01.png)

### 1. Adicionar o endpoint de tronco

Adicione um tronco baseado em IP ao `lab/asterisk/etc/pjsip.conf` que corresponda ao host SIPp do laboratório
e direcione chamadas inbound para `from-pstn`:

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

### 2. Roteir o DID inbound

Em `lab/asterisk/etc/extensions.conf`, adicione um contexto `from-pstn` que atenda ao
DID que o operador simulado discará e reproduza-o, então adicione uma regra outbound:

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

Recarregue ambos os arquivos (`core reload`) e verifique se o tronco foi carregado:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Fazer uma chamada inbound através do tronco

Aponte um cenário SIPp para o PBX com o DID como usuário alvo. O laboratório já
distribui `lab/sipp/uac_9000.xml`, que INVITE a extensão `9000`; copie‑o para
`uac_did.xml` e altere o request‑URI/usuário `To` de `9000` para `4830001000`,
então execute‑o a partir do contêiner SIPp:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Observe a chamada atingir `from-pstn` no console do Asterisk (`pjsip set logger on`
mostra o INVITE inbound; `core show channels` mostra o canal `PJSIP/itsp-…`
reproduzindo `demo-congrats`). Como o IP de origem do SIPp corresponde ao `identify`, a
chamada é aceita sem autenticação — exatamente como um tronco de operador estático
se comporta.

### 4. Inspecionar o tronco

Capture a configuração completa do tronco para suas anotações:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) torná‑lo um tronco de registro

Levante o *segundo* contêiner Asterisk como um registrador real: forneça-lhe um
`endpoint`+`auth`+`aor` para a conta `4830001000`, então no PBX troque o
bloco `identify` pelo bloco `registration` do início deste capítulo
(apontando `server_uri` para o IP do segundo contêiner). Confirme com
`pjsip show registrations` que o status exibe `Registered`, então faça uma chamada
em cada direção.

## Summary

Um trunk SIP conecta seu PBX ao mundo externo, e no PJSIP ele é apenas um
endpoint construído a partir da mesma família `endpoint` + `auth` + `aor` que você já conhece,
mais um `identify` ou um `registration`. Use um **trunk de registro**
(`type=registration` com `outbound_auth`) quando o provedor lhe fornece um nome de usuário
e senha; use um **trunk baseado em IP** (`type=identify` com `match`) quando
a autenticação for por IP de origem — e restrinja este último com um `match`
estreito e um `acl`, porque um trunk não autenticado é um alvo de fraude de tarifas. De entrada,
o DID do provedor chega como `${EXTEN}` no seu contexto `from-pstn`, onde você
o encaminha para uma extensão, um IVR ou uma fila — padrões e `${EXTEN:-N}` mantêm
os blocos de DID compactos. De saída, defina `CALLERID(num)` para um número que você possui, normalize
para E.164 em um único lugar, e entregue a chamada ao `PJSIP/<number>@trunk`. Construa
resiliência tentando múltiplos trunks e ramificando em `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` significam reencaminhamento; `BUSY`/`NOANSWER` não), e coloque
roteamento de menor custo em uma tabela `GoSub`. Finalmente, NAT para trunks é bidirecional:
`external_media_address`/`external_signaling_address`/`local_net` no
**transport** para seu endereço público, e `direct_media=no`, `rtp_symmetric`,
`force_rport` e `rewrite_contact` no **endpoint** para a mídia do provedor.

## Quiz

1. No PJSIP, as credenciais usadas para autenticar uma chamada *outbound* ou
   registro para um provedor são referenciadas com:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Você deve usar um tronco `type=registration` quando:
   - A. O provedor o identifica pelo seu endereço IP de origem.
   - B. O provedor fornece um nome de usuário e senha e espera que você faça login.
   - C. Você nunca quer que o Asterisk envie um `REGISTER`.
   - D. O tronco está entre dois servidores de IP estático que você controla.
3. A opção `match` do objeto `identify` aceita (marque todas que se aplicam):
   - A. Um endereço IP
   - B. Um intervalo CIDR
   - C. Um nome de host (resolvido no momento da carga da configuração)
   - D. Apenas um nome de usuário SIP
4. No Asterisk 22, `auth_type=userpass` é:
   - A. O único valor válido
   - B. Obsoleto e convertido para `digest`
   - C. Removido e causa erro de carregamento
   - D. Obrigatório para registro outbound
5. Um número DID inbound chega ao dialplan como:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` no `context` do endpoint do tronco
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Para enviar os dois últimos dígitos do DID discado `4830003007` para uma extensão,
   você usaria:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Após `Dial()` para um tronco, você deve mudar para um tronco de backup no qual
   os valores `${DIALSTATUS}` (marque dois)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Para definir o número de caller-ID apresentado ao provedor antes de discar para fora, use:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. As opções que informam ao Asterisk seu endereço *público* quando o servidor está atrás de
   NAT são configuradas em:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` em um endpoint de tronco faz o Asterisk:
    - A. Criptografar RTP com SRTP
    - B. Enviar RTP de volta para o endereço de onde a mídia realmente chegou, ignorando o SDP
    - C. Desativar RTP completamente
    - D. Forçar mídia direta entre endpoints

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
