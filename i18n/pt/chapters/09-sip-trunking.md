# SIP trunking, DID & the PSTN

Um PBX que só consegue ligar para si mesmo não é muito útil. Mais cedo ou mais tarde, todo sistema precisa alcançar o resto do mundo — a rede telefônica pública comutada (PSTN), um provedor SIP ou outro PBX. O link que transporta essas chamadas é um **trunk**. Na era TDM, um trunk era um circuito físico: um T1/E1 PRI ou um conjunto de linhas FXO analógicas. Hoje, é quase sempre um **SIP trunk** — uma conexão lógica com um Internet Telephony Service Provider (ITSP) transportada pela mesma rede IP que todo o resto.

Este capítulo mostra como conectar o Asterisk 22 a um ITSP com PJSIP, como escolher entre um trunk baseado em registro e um baseado em IP, como rotear números DID de entrada para o destino correto, como enviar chamadas de saída com o caller-ID correto e formatação E.164, e como criar failover e roteamento de menor custo entre vários trunks. Terminamos com o tratamento de NAT para trunks e um laboratório que levanta um segundo Asterisk (e SIPp) como um ITSP simulado para que você possa realizar chamadas reais através de um trunk.

Tudo aqui foi verificado no laboratório Asterisk 22.10.0 do livro; o padrão de objeto de trunk é o mesmo introduzido em *Building your first PBX with PJSIP* e *SIP & PJSIP in depth*.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Conectar o Asterisk 22 a um ITSP com PJSIP
- Escolher entre trunks baseados em registro e baseados em IP (estáticos)
- Rotear DIDs de entrada para a extensão, IVR ou fila correta
- Rotear chamadas de saída com o caller-ID correto e formatação E.164
- Criar failover de trunk e roteamento de menor custo com `${DIALSTATUS}`
- Lidar com NAT para trunks no transporte e no endpoint

## O que é um SIP trunk

Um SIP trunk é um caminho de voz lógico entre seu PBX e outro sistema SIP. Na prática, esse "outro sistema" é uma de duas coisas:

- **Um ITSP (Internet Telephony Service Provider).** Uma operadora comercial que vende originação e terminação de chamadas e, geralmente, um bloco de números de telefone (DIDs). Você aponta o Asterisk para o host de sinalização do provedor, e o provedor conecta suas chamadas à PSTN mais ampla. É assim que a maioria dos sistemas modernos alcança a rede telefônica — sem necessidade de hardware de telefonia.
- **Um gateway PSTN.** Um dispositivo (ou outro Asterisk) que possui interfaces PSTN físicas — uma placa PRI, portas FXO analógicas ou um gateway GSM/4G — e as apresenta ao seu PBX como SIP. O gateway faz a conversão TDM-para-SIP; do ponto de vista do Asterisk, é apenas mais um SIP trunk.

De qualquer forma, no PJSIP, um trunk é **apenas um endpoint**. A mesma família de objetos que você usou para um telefone — `endpoint`, `auth`, `aor`, opcionalmente `identify` e `registration` — constrói um trunk. As diferenças estão nos detalhes: um trunk autentica *saídas* (você é o cliente, então as credenciais vão em `outbound_auth`, não `auth`), geralmente não registra um user agent para você (você se registra *nele*, ou ele envia tráfego de um IP conhecido), e ele direciona chamadas de entrada para um context dedicado como `from-pstn` em vez de `from-internal`.

> **Comparado com o antigo trunk TDM.** Um PRI fornecia um número fixo de canais B (23 em um T1, 30 em um E1) e sinalizava o estabelecimento da chamada através de um canal D dedicado (veja o capítulo *Legacy channels*). Um SIP trunk não tem contagem fixa de canais — a capacidade é o que sua largura de banda, a política do seu provedor e quaisquer limites de `max_contacts`/chamadas simultâneas permitirem. Caller-ID, DID e o progresso da chamada que costumavam trafegar em elementos de informação ISDN agora trafegam em cabeçalhos SIP e SDP.

Existem duas maneiras pelas quais um ITSP concordará em trocar tráfego com você, e elas determinam como você constrói o trunk: **baseado em registro** e **baseado em IP (estático)**. Cobriremos cada um por vez.

## Trunks baseados em registro

Um trunk baseado em registro é o modelo usado quando o provedor espera que *você* faça login *neles*. Seu Asterisk envia periodicamente um `REGISTER` SIP para o provedor, autenticando-se com um nome de usuário e senha, exatamente da mesma forma que um telefone se registra no seu PBX. Isso é comum quando seu IP público é dinâmico, quando você está atrás de NAT, ou quando o provedor simplesmente identifica os clientes por credenciais SIP em vez de endereço IP.

No PJSIP, o login de saída reside em um objeto `registration` dedicado. Ele substitui a única linha `register =>` que o driver removido `chan_sip` usava em `sip.conf`. Aqui está um trunk de registro completo para um provedor fictício, seguindo o padrão verificado dos capítulos anteriores — observe `outbound_auth` (não `auth`), `server_uri`/`client_uri` (não `server`/`client`), `from_user`/`from_domain` no endpoint, e `dtmf_mode=rfc4733`:

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

Algumas coisas a notar:

- **`auth_type=digest`, não `userpass`.** Ambos produzem a mesma autenticação digest, mas no Asterisk 22, `userpass` (e o antigo `md5`) são **descontinuados e convertidos silenciosamente para `digest`**. Prefira `digest` em novas configurações; você ainda verá `userpass` em arquivos antigos e nos capítulos anteriores deste livro.
- **`outbound_auth` tanto no endpoint quanto no registro.** O registro o usa para autenticar o `REGISTER`; o endpoint o usa para responder ao `407 Proxy Authentication Required` que o provedor envia de volta para um `INVITE` de saída. Eles podem compartilhar um objeto `auth`.
- **`from_user` / `from_domain`.** Muitos provedores rejeitam chamadas cujo cabeçalho `From` não carrega o número da sua conta e o domínio deles. Essas duas opções definem exatamente isso.
- **`contact_user=4830001000`.** Isso se torna a parte de usuário do `Contact` que você registra, para que o provedor saiba para qual número entregar as chamadas de entrada. É o equivalente moderno do sufixo `/9999` na antiga linha `register =>`.
- **`retry_interval=60`.** Se o registro falhar, tente novamente a cada 60 segundos.

Após um reload, confirme o registro com `pjsip show registrations`. No laboratório — onde o `itsp.example.com` não responde de fato — a tabela fica assim:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

O sufixo `(exp. Ns)` faz a contagem regressiva dos segundos até a próxima tentativa; assim que cruza zero, ele lê brevemente `(exp. Ns ago)` antes que a tentativa de reenvio seja disparada. Contra um provedor real, a coluna `Status` lê `Registered` com os segundos restantes até a próxima atualização. `Rejected` (ou `Unregistered`) significa que o provedor não aceitou o login — ative o `pjsip set logger on` e leia a resposta `401`/`403`, quase sempre um nome de usuário, senha ou domínio `client_uri` incorreto.

## Trunks baseados em IP (estáticos)

O segundo modelo não precisa de registro algum. O provedor conhece seu endereço IP público e envia chamadas diretamente para ele; você, por sua vez, envia chamadas para o IP de sinalização conhecido do provedor. A autenticação é feita por **endereço IP de origem**, não por credenciais SIP. Isso é típico para trunks entre dois servidores que você controla, ou para um trunk corporativo onde ambos os lados possuem endereços estáticos.

O objeto chave é o `identify`. Ele diz ao Asterisk: "qualquer solicitação SIP que chegue deste IP pertence àquele endpoint". Sem ele, o PJSIP tenta combinar uma solicitação de entrada com um endpoint pelo usuário `From`, o que o tráfego de uma operadora não satisfará — então a chamada seria rejeitada ou cairia no endpoint `anonymous`.

Um trunk estático remove o objeto `registration` e adiciona o `identify`:

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

O `match` aceita um endereço IP, um intervalo CIDR ou um nome de host. **Nomes de host são resolvidos uma vez, no momento do carregamento da configuração**, portanto, se o IP do seu provedor mudar, você deve recarregar. Para uma operadora que publica vários gateways de mídia, liste cada IP de sinalização — você pode repetir o `match` ou fornecer um CIDR:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Verifique o que o Asterisk aceitará com `pjsip show identifies`. Capturado do laboratório (a linha `sipp-identify` é o endpoint SIPp pré-existente do laboratório):

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

### A implicação de segurança

Um trunk baseado em IP sem autenticação é uma porta, e o `identify`/`match` é a única fechadura nela. Se você definir um `match` muito amplo — ou se um invasor puder falsificar um IP de origem — as chamadas cairão no seu context `from-pstn` sem autenticação. Duas defesas, usadas juntas:

- **Combine o mais estritamente possível.** Prefira IPs de host específicos em vez de CIDRs amplos. Apenas os IPs de sinalização reais do provedor pertencem ao `match`.
- **Combine com uma ACL.** O PJSIP pode descartar tráfego na camada SIP antes mesmo que ele chegue a um endpoint, usando um objeto `type=acl` (ou `acl.conf`):

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Referencie-o a partir da seção global (`acl=itsp-acl` em `[global]`/`type=global`) ou aplique por transporte. O princípio é o mesmo do capítulo SIP: negue tudo, depois permita apenas o que você confia. E o que quer que seu context de trunk faça, **nunca o deixe alcançar um context que possa discar de volta para a PSTN** sem uma regra deliberada e autenticada — esse é o clássico buraco de fraude telefônica.

> **Qual modelo devo usar?** Se o provedor lhe fornecer um nome de usuário e senha, use um trunk de **registro**. Se eles pedirem seu endereço IP e fornecerem o deles, use um trunk de **identify**. Alguns provedores suportam ambos; muitos trunks reais combinam um registro (para que o provedor possa encontrá-lo) com um identify (para que INVITEs de entrada dos gateways de mídia do provedor sejam combinados mesmo quando chegam de um IP diferente do registrar).

## Roteamento de entrada e tratamento de DID

Assim que as chamadas de entrada chegam, elas caem no `context` do endpoint — aqui, `from-pstn`. Um **DID** (Direct Inward Dialing number) é simplesmente o número discado que o provedor lhe entrega na URI da solicitação. Seu trabalho no dialplan é mapear cada DID para um destino: uma extensão única, um IVR, uma fila ou um grupo de toque.

O número que o provedor envia é correspondido como `${EXTEN}` no `from-pstn`. O quanto dele você vê depende do provedor — alguns enviam o número E.164 completo (`+4830001000`), alguns enviam o número nacional, alguns enviam apenas os últimos dígitos. Inspecione uma chamada de entrada real com `pjsip set logger on` e observe a URI da solicitação antes de escrever os padrões.

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

`ivr-main` é o context de atendente automático que você construiu nos capítulos de dialplan (`Background()` + `WaitExten()`). Rotear o DID é apenas um `Goto`.

### Um DID para uma fila

Uma linha de suporte que deve cair em uma fila de chamadas:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Muitos DIDs de uma vez

Ao comprar um bloco de números, um padrão mantém o dialplan pequeno. Suponha que seu intervalo de DID seja `4830003000`–`4830003099` e o provedor envie o número completo; mapeie os dois últimos dígitos de cada DID para a extensão `60xx`:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

O `${EXTEN:-2}` pega os dois últimos dígitos (o deslocamento negativo conta da direita), então `4830003007` toca `PJSIP/6007`. Uma tabela de consulta `did => extension` construída com `GoSub` ou um banco de dados Asterisk (`AstDB`/`func_odbc`) escala ainda mais, mas para um punhado de números, padrões explícitos são os mais claros.

> **Capture o DID não correspondido.** Adicione uma extensão `i` (inválida) ao `from-pstn` para que um número de entrada mal roteado reproduza um anúncio ou toque para o operador em vez de cair silenciosamente:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Roteamento de saída, caller-ID e E.164

As chamadas de saída fluem para o outro lado: um telefone interno disca um número, seu dialplan o corresponde, remove qualquer prefixo de acesso, define o caller-ID que o provedor espera e entrega a chamada ao endpoint do trunk com `Dial(PJSIP/<number>@itsp)`.

### Enviando a chamada para o trunk

A sintaxe de canal para um trunk é `PJSIP/<number>@<endpoint>`: a parte antes do `@` torna-se a parte de usuário da URI da solicitação de saída, e a parte após o `@` nomeia o endpoint cujo `aor` `contact` fornece o host de destino. Uma regra clássica de "disque 9 para uma linha externa":

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

O `${EXTEN:1}` remove o código de acesso `9` inicial antes que o número seja enviado. O padrão `_9NXXXXXXXXX` corresponde a `9` mais um número de 10 dígitos cujo primeiro dígito é 2–9; ajuste-o para o seu plano de discagem.

### Caller-ID em chamadas de saída

A maioria dos ITSPs ignora — ou rejeita ativamente — um caller-ID que não seja um número que você possui. Defina o número de caller-ID de saída para um dos seus DIDs com a função `CALLERID(num)` antes do `Dial()`, como mostrado acima. Você também pode definir o nome:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

Se o provedor ainda remover ou substituir seu nome de caller-ID, essa é a política deles — muitas operadoras obtêm o nome exibido de seu próprio banco de dados CNAM baseado no número, não do seu cabeçalho `From`.

Duas opções de endpoint interagem com isso:

- **`from_user`** define a parte de usuário do cabeçalho `From` no nível SIP, que alguns provedores usam para identificar sua conta independentemente do `CALLERID(num)`.
- **`trust_id_outbound`** (padrão `no`) controla se o Asterisk enviará cabeçalhos de identidade sensíveis à privacidade (`P-Asserted-Identity`/`P-Preferred-Identity`) na saída. Deixe desligado, a menos que seu provedor documente que deseja PAI, caso em que defina `trust_id_outbound=yes` e `send_pai=yes`.

### Normalizando para E.164

E.164 é o formato de número internacional: um `+` inicial, código do país, depois o número nacional, sem espaços ou pontuação (por exemplo, `+5548999990000` ou `+14155550100`). As operadoras esperam — ou exigem — cada vez mais E.164 no trunk. Em vez de espalhar a formatação pelo dialplan, normalize uma vez no context de saída.

Um exemplo norte-americano que aceita um número local de 10 dígitos, um número prefixado com `1` de 11 dígitos ou um número já em E.164, e sempre apresenta `+1…` ao trunk:

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

Alguns provedores querem o `+`; outros querem apenas os dígitos. Se o seu rejeitar o `+`, remova-o na saída com `${EXTEN:1}` no `Dial`. O ponto é que todo o conhecimento de formato vive em um só lugar, então trocar de provedor — ou adicionar um segundo — é uma mudança de uma linha.

## Failover e roteamento de menor custo

Com um trunk, uma falha do provedor significa sem chamadas de saída. Com dois ou mais, você pode fazer failover automaticamente e até escolher a rota mais barata por destino — *roteamento de menor custo* (LCR).

### Failover com `${DIALSTATUS}`

O `Dial()` define a variável de canal `${DIALSTATUS}` quando retorna. Os valores com os quais você se preocupa para failover são `CHANUNAVAIL` (o trunk não pôde ser alcançado de forma alguma) e `CONGESTION` (a chamada foi rejeitada, por exemplo, todos os circuitos ocupados). Tente o trunk principal; se ele não puder realizar a chamada, passe para o backup:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Observe a escolha deliberada de **não** fazer failover em `BUSY` ou `NOANSWER` — isso significa que a *parte chamada* foi alcançada e recusou, então tentar novamente em outro trunk faria tocar novamente um telefone que já disse não (e poderia lhe custar uma segunda chamada). Apenas re-roteie quando o *próprio trunk* falhar.

### Uma sub-rotina de roteamento reutilizável

Repetir essa lógica para cada padrão de discagem é propenso a erros. Fatore-a em uma rotina `GoSub` que recebe o número de destino e tenta cada trunk em ordem:

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

Agora, cada padrão de saída é uma chamada `GoSub`, e a ordem do trunk é definida em exatamente um lugar.

### Roteamento de menor custo por destino

O LCR verdadeiro escolhe o trunk pelo destino da chamada. Um formato comum é corresponder ao prefixo de destino e enviar cada classe de chamada para o provedor que é mais barato para ela — por exemplo, chamadas internacionais para uma operadora de atacado e chamadas locais/nacionais para a sua principal:

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

Para mais do que alguns prefixos, armazene a tabela de rotas em um banco de dados (`func_odbc`/`AstDB`) e procure o trunk por prefixo em vez de codificar padrões. O dialplan permanece pequeno e as tarifas vivem em uma tabela que você pode editar sem recarregar a lógica.

## NAT e trunks

NAT é a causa mais comum de problemas em trunks — normalmente áudio unidirecional ou um trunk que se registra, mas nunca recebe chamadas de entrada. A causa é a mesma dos telefones (coberta em *SIP & PJSIP in depth* e *Designing a VoIP network*): o Asterisk anuncia sua própria ideia de seu endereço em SIP e SDP, e atrás de NAT, esse é um endereço privado RFC 1918 que o provedor não consegue rotear de volta.

Para trunks, a correção tem duas partes — configurações no **transporte** (seu endereço público) e configurações no **endpoint** (como tratar a mídia do provedor).

### No transporte — seu endereço público

Quando o servidor Asterisk está atrás de NAT (uma nuvem ou caixa local com um IP privado e um IP público 1:1), informe ao transporte seu endereço público e quais redes são locais. Essas opções são definidas uma vez, no `transport`, e aplicam-se a todo o tráfego sobre ele:

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

- **`external_signaling_address`** — o IP público que o Asterisk escreve nos cabeçalhos SIP (`Via`, `Contact`) para destinos fora de `local_net`.
- **`external_media_address`** — o IP público que o Asterisk escreve na linha SDP `c=` para que o RTP volte para o lugar certo. Geralmente idêntico ao endereço de sinalização.
- **`local_net`** — redes que o Asterisk trata como internas, para que ele *não* reescreva endereços para pares LAN. Liste todas as sub-redes internas.

### No endpoint — a mídia do provedor

A outra metade lida com um provedor que também está atrás de NAT, ou simplesmente envia mídia de um endereço diferente daquele no SDP dele. Defina isso por endpoint de trunk:

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

- **`direct_media=no`** — mantenha a mídia fluindo através do Asterisk em vez de deixar as duas pernas conversarem diretamente. Essencial através de NAT, e necessário de qualquer maneira se você quiser gravar, transcodificar ou monitorar a chamada.
- **`rtp_symmetric=yes`** — o comportamento clássico *comedia*: envie RTP de volta para o endereço de onde a mídia realmente veio, não o endereço que o SDP alega.
- **`force_rport=yes`** — responda ao SIP a partir do IP/porta de origem da solicitação (RFC 3581), em vez de confiar no cabeçalho `Via`.
- **`rewrite_contact=yes`** — em mensagens SIP de entrada deste endpoint, reescreva o cabeçalho `Contact` (ou um cabeçalho `Record-Route` apropriado) para o endereço IP e porta de origem de onde o pacote realmente veio. Conforme a própria documentação da opção, isso "ajuda os servidores a se comunicarem com endpoints que estão atrás de NATs" e "ajuda a reutilizar conexões de transporte confiáveis, como TCP e TLS."

> **Recomendação — telefones vs trunks.** `rewrite_contact` é quase sempre a escolha certa para telefones, porque seu contato anunciado é tipicamente um endereço privado RFC 1918 que não é roteável de volta para eles. Em um trunk estático baseado em IP, o contato do provedor geralmente já é um endereço público correto, então reescrevê-lo é frequentemente desnecessário; alguns operadores preferem deixá-lo desligado lá e ativá-lo apenas para trunks de registro e telefones atrás de NAT. O efeito documentado da opção é puramente a reescrita de `Contact`/`Record-Route` de entrada acima — então a prática segura é testar contra sua operadora específica antes de ativá-la em um trunk estático.

Você pode confirmar as configurações efetivas em qualquer endpoint com `pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`, `rewrite_contact` e o restante são todos impressos no dump de parâmetros.

## Lab — um ITSP simulado com um segundo Asterisk e SIPp

Você não precisa de um trunk pago para praticar. O laboratório do livro já executa um container Asterisk 22.10.0 e um container SIPp em uma rede privada `172.30.0.0/24`; trataremos o container SIPp como a "operadora" fazendo chamadas de entrada e adicionaremos um endpoint de trunk que direciona essas chamadas para um context `from-pstn`.

![Um SIP trunk entre o PBX Asterisk e o ITSP: o PBX se registra como uma conta, chamadas de saída discam `PJSIP/<num>@trunk`, e chamadas de entrada caem no context `from-pstn`.](../images/09-sip-trunking-fig01.png)

### 1. Adicione o endpoint do trunk

Adicione um trunk baseado em IP ao `lab/asterisk/etc/pjsip.conf` que corresponda ao host SIPp do laboratório e direcione as chamadas de entrada para `from-pstn`:

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

### 2. Roteie o DID de entrada

No `lab/asterisk/etc/extensions.conf`, adicione um context `from-pstn` que atenda o DID que a operadora simulada discará e o reproduza, depois adicione uma regra de saída:

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

Recarregue ambos os arquivos (`core reload`) e verifique se o trunk carregou:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Faça uma chamada de entrada através do trunk

Aponte um cenário SIPp para o PBX com o DID como o usuário de destino. O laboratório já envia `lab/sipp/uac_9000.xml`, que faz INVITE para a extensão `9000`; copie-o para `uac_did.xml` e altere o usuário da request-URI/`To` de `9000` para `4830001000`, depois execute-o a partir do container SIPp:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Observe a chamada atingir o `from-pstn` no console do Asterisk (`pjsip set logger on` mostra o INVITE de entrada; `core show channels` mostra o canal `PJSIP/itsp-…` reproduzindo `demo-congrats`). Como o IP de origem do SIPp corresponde ao `identify`, a chamada é aceita sem autenticação — exatamente como um trunk de operadora estático se comporta.

### 4. Inspecione o trunk

Capture a configuração completa do trunk para suas anotações:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Desafio) torne-o um trunk de registro

Levante o *segundo* container Asterisk como um registrar real: dê a ele um `endpoint`+`auth`+`aor` para a conta `4830001000`, então no PBX troque o bloco `identify` pelo bloco `registration` do início deste capítulo (apontando o `server_uri` para o IP do segundo container). Confirme com `pjsip show registrations` que o status lê `Registered`, depois faça uma chamada em cada direção.

## Resumo

Um SIP trunk conecta seu PBX ao mundo exterior, e no PJSIP é apenas um endpoint construído a partir da mesma família `endpoint` + `auth` + `aor` que você já conhece, mais um `identify` ou um `registration`. Use um **trunk de registro** (`type=registration` com `outbound_auth`) quando o provedor lhe fornecer um nome de usuário e senha; use um **trunk baseado em IP** (`type=identify` com `match`) quando a autenticação for por IP de origem — e bloqueie este último com um `match` estreito e um `acl`, porque um trunk não autenticado é um alvo de fraude telefônica. Na entrada, o DID do provedor chega como `${EXTEN}` no seu context `from-pstn`, onde você o roteia para uma extensão, um IVR ou uma fila — padrões e `${EXTEN:-N}` mantêm os blocos de DID compactos. Na saída, defina o `CALLERID(num)` para um número que você possui, normalize para E.164 em um só lugar e entregue a chamada ao `PJSIP/<number>@trunk`. Construa resiliência tentando vários trunks e ramificando no `${DIALSTATUS}` (`CHANUNAVAIL`/`CONGESTION` significam re-rotear; `BUSY`/`NOANSWER` não), e coloque o roteamento de menor custo em uma tabela `GoSub`. Finalmente, NAT para trunks é de dois lados: `external_media_address`/`external_signaling_address`/`local_net` no **transporte** para seu endereço público, e `direct_media=no`, `rtp_symmetric`, `force_rport` e `rewrite_contact` no **endpoint** para a mídia do provedor.

## Quiz

1. No PJSIP, as credenciais usadas para autenticar uma chamada de *saída* ou registro para um provedor são referenciadas com:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Você deve usar um trunk `type=registration` quando:
   - A. O provedor o identifica pelo seu endereço IP de origem.
   - B. O provedor lhe fornece um nome de usuário e senha e espera que você faça login.
   - C. Você nunca quer que o Asterisk envie um `REGISTER`.
   - D. O trunk é entre dois servidores de IP estático que você controla.
3. A opção `match` do objeto `identify` aceita (escolha todas as que se aplicam):
   - A. Um endereço IP
   - B. Um intervalo CIDR
   - C. Um nome de host (resolvido no momento do carregamento da configuração)
   - D. Apenas um nome de usuário SIP
4. No Asterisk 22, `auth_type=userpass` é:
   - A. O único valor válido
   - B. Descontinuado e convertido para `digest`
   - C. Removido e causa um erro de carregamento
   - D. Necessário para registro de saída
5. Um número DID de entrada chega no dialplan como:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` no `context` do endpoint do trunk
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Para enviar os dois últimos dígitos do DID discado `4830003007` para uma extensão, você usaria:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Após `Dial()` para um trunk, você deve fazer failover para um trunk de backup em quais valores `${DIALSTATUS}` (escolha dois)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Para definir o número de caller-ID apresentado ao provedor antes de discar para fora, use:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. As opções que informam ao Asterisk seu endereço *público* quando o servidor está atrás de NAT são definidas no:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` em um endpoint de trunk faz com que o Asterisk:
    - A. Criptografe RTP com SRTP
    - B. Envie RTP de volta para o endereço de onde a mídia realmente veio, ignorando o SDP
    - C. Desabilite RTP completamente
    - D. Force mídia direta entre endpoints

**Respostas:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
