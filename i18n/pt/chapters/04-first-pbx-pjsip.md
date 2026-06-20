# Construindo sua primeira PBX com PJSIP

Neste capítulo, você aprenderá como executar uma configuração básica de PBX no Asterisk. O objetivo principal aqui é ver a PBX em funcionamento pela primeira vez, ser capaz de discar entre ramais, discar para uma mensagem em reprodução e discar para um único tronco analógico ou SIP. A ideia por trás deste capítulo é garantir que seu Asterisk esteja instalado e operando o mais rápido possível. Após concluir o trabalho neste capítulo, você terá conhecimento suficiente para se preparar para os capítulos subsequentes, onde aprofundaremos mais os detalhes de configuração.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Entender e editar arquivos de configuração;
- Instalar softphones baseados em SIP;
- Instalar e configurar um tronco SIP;
- Instalar e configurar uma conexão analógica;
- Discar entre ramais;
- Discar entre telefones e destinos externos; e
- Configurar um atendente automático.

## Entendendo os arquivos de configuração

Asterisk é controlado por arquivos de configuração de texto localizados em /etc/asterisk. O formato do arquivo é semelhante aos arquivos “.ini” do Windows. Um ponto e vírgula é usado como caractere de comentário, os sinais “=” e “=>” são equivalentes, e os espaços são ignorados.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interpreta “=” e “=>” da mesma forma. Diferenças na sintaxe são usadas para distinguir entre objetos e variáveis. Use “=” quando quiser declarar uma variável e “=>” para designar um objeto. A sintaxe é a mesma em todos os arquivos, mas três tipos de gramática são usados, conforme discutido abaixo.

## Gramáticas

| Gramática | Como o objeto é criado | Arquivo de conf. | Exemplo |
|-----------|------------------------|------------------|---------|
| Simple Group | Tudo na mesma linha | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Option Inheritance | As opções são definidas primeiro, o objeto herda as opções | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Complex Entity | Cada entidade recebe um contexto | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Simple Group

O formato de grupo simples usado em `extensions.conf` e `voicemail.conf` é a gramática mais básica. Cada objeto é declarado com opções na mesma linha. Exemplo:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

Neste exemplo, o objeto 1 é criado com as opções op1, op2 e op3, enquanto o objeto 2 é criado com as opções op1, op2 e op3.

### Object options inheritance grammar

Este formato é usado pelos arquivos chan_dahdi.conf e agents.conf, onde há inúmeras opções disponíveis, e a maioria das interfaces e objetos compartilha as mesmas opções. Normalmente, uma ou mais seções contêm declarações de objetos e canais. As opções do objeto são declaradas acima do objeto e podem ser alteradas para outro objeto. Embora esse conceito seja difícil de entender, ele é muito fácil de usar. Exemplo:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

As duas primeiras linhas configuram o valor das opções op1 e op2 para “bas” e “adv”, respectivamente. Quando o objeto 1 é instanciado, ele é criado usando a opção 1 como “bas” e a opção 2 como “adv”. Após definir o objeto 1, mudamos a opção 1 para “int”. Em seguida, criamos o objeto 2 com a opção 1 como “int” e a opção 2 como “adv”.

### Complex entity object

Este formato é usado por pjsip.conf, iax.conf e outros arquivos de configuração nos quais existem inúmeras entidades com muitas opções. Normalmente, esse formato não compartilha um grande volume de configurações comuns. Cada entidade recebe um contexto. Às vezes, contextos reservados existem, como [general] para configurações globais. As opções são declaradas nas declarações de contexto. Exemplo:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

A entidade [entity1] tem os valores “value1” e “value2” para as opções op1 e op2, respectivamente. A entidade [entity2] tem os valores “value3” e “value4” para as opções op1 e op2.

## Options to build a LAB for Asterisk

Para configurar uma PBX, você precisará de algum hardware básico. Não é difícil nem caro, mas há algumas opções a serem consideradas. Tudo que você precisará são dois telefones e uma conexão à rede pública. Algumas opções e combinações são possíveis ao criar seu laboratório, que discutiremos abaixo.

### Option 1: Complete LAB

Com o LAB completo, é possível testar todos os cenários disponíveis e comparar soluções como ATA, telefones IP e softphones. Você também pode aprender sobre troncos analógicos e SIP. Você precisará:

- Um adaptador telefônico analógico SIP (ATA)
- Um telefone IP
- Um servidor dedicado para Asterisk
- Uma estação de trabalho com um softphone
- Uma placa de interface analógica com pelo menos duas interfaces (1 FXO e 1 FXS)
- Uma conta em um provedor de VoIP

### Option 2: Economy LAB

Com o LAB econômico, simplificamos um pouco. Usamos o ATA, que geralmente é menos caro que o telefone IP, e uma única placa FXO, que é realmente barata. Não poderemos usar telefones analógicos conectados diretamente ao servidor, mas isso não ocorre com frequência na prática. Você precisará:

- Um adaptador telefônico analógico SIP (ATA)
- Um servidor dedicado para Asterisk
- Uma estação de trabalho para o softphone
- Uma placa de interface analógica com 1 FXO
- Uma conta em um provedor de VoIP

### Option 3: Super economy lab

O terceiro LAB usa um servidor virtualizado no próprio notebook do estudante. O problema desse modelo são os conflitos gerados pela porta UDP. Às vezes, tanto o servidor Asterisk quanto o softphone tentam acessar a mesma porta, impedindo o Asterisk de vincular a porta de endereço. Outra questão é a qualidade das chamadas; ambientes virtuais não são indicados para aplicações em tempo real como o Asterisk. Use um softphone gratuito para o servidor e a estação de trabalho e uma conexão de tronco para um provedor SIP. Você precisará:

- Um laptop executando um softphone
- Uma máquina virtual (VirtualBox, VMware ou similar) para instalar o Asterisk
- Uma conta em um provedor de VoIP

## Sequência de Instalação

Para ajudá‑lo a entender a sequência de instalação, descrevemos os passos necessários para instalar e configurar o Asterisk.

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. Configuração de ramais
   - a. Ramais SIP (ATA, Softphone, IP Phone)
   - b. Ramais IAX
   - c. Ramais FXS
2. Configuração de troncos
   - a. Configuração de um tronco SIP
   - b. Configuração de um tronco FXO
3. Construindo um plano de discagem básico
   - a. Discando entre ramais
   - b. Discando destinos externos
   - c. Recebendo uma chamada na extensão do operador
   - d. Recebendo uma chamada em um atendente automático

## Configuration of the extensions

The extensions are SIP, IAX, or analog phones connected to an FXS port. To configure an extension, you should edit the configuration file related to the channel (pjsip.conf, iax.conf, chan_dahdi.conf)

### SIP extensions

On Asterisk 22, PJSIP (the `res_pjsip` stack, configured in `/etc/asterisk/pjsip.conf`) is the SIP channel driver. It supports multiple transports per endpoint, is actively maintained, and is the only SIP driver shipped with the platform. (The original `chan_sip` driver was removed in Asterisk 21 — see the *Legacy channels* chapter if you need to migrate an old configuration.)

The idea here is to configure a simple PBX. (Subsequent chapters provide an entire SIP/PJSIP session with all the details.) PJSIP is configured in `/etc/asterisk/pjsip.conf` and holds all the parameters related to SIP phones and VoIP providers. SIP clients have to be configured before you can make and receive calls.

#### The transport

In PJSIP, the listener configuration (bind address, port, protocol) lives in a `transport` object. Asterisk has built-in protection against username guessing — it always returns an identical authentication challenge for unknown and known users, and repeated unidentified requests from one IP are rate-limited via the `[global]` options `unidentified_request_count`/`unidentified_request_period`. The main options of a transport are:

- protocol: The transport protocol — `udp`, `tcp`, `tls`, `ws`, or `wss`.
- bind: Address and port the listener binds to. If you set the address to `0.0.0.0`, it binds to all interfaces; the SIP port defaults to 5060 for UDP/TCP.

A minimal UDP transport:

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

PJSIP allows the `endpoint`, `auth`, and `aor` sections to share the same section name (e.g. the two `[6001]` blocks above, distinguished by their `type=`); many admins instead suffix them (`[6001]`, `[6001-auth]`, `[6001]` aor) for readability. For a device that registers, the contact is learned dynamically when the phone registers, so the AOR needs no static `contact`.

## IAX Extensions

`chan_iax2` still ships in Asterisk 22 but is now legacy; SIP/PJSIP is the preferred protocol for new deployments.

You may also create IAX extensions. This protocol is native to the Asterisk, and we will have an entire section devoted to it later in this book. For now, let’s create a few extensions using the protocol. As the first section to be configured, the section [general] has certain parameters to be configured. The main options are:

- allow/disallow: Defines which codecs are going to be used.
- bindaddr: Address the IAX2 listener binds to. If you set it up as 0.0.0.0 (default), it will bind to all interfaces.
- context: Sets the default context for all clients unless changed in the client section. We used dummy for security reasons. Unauthenticated users get into this context when the option allowguest is set to yes.
- bindport: IAX2 UDP port to listen on (default 4569).
- delayreject: When set to yes, delays the sending of an authentication reject for a REGREQ or AUTHREQ, which improves the security against brute-force password attacks.
- bandwidth: When set to high, it allows the selection of high bandwidth codecs, such as the g711 in their variants ulaw and alaw.

The following is a sample of the [general] section of the file iax.conf.

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

### IAX Clients

After finishing the general sections, it is time to set up the IAX clients.

- `[name]`: The section name is the IAX peer/user name; an incoming IAX connection is matched to it by name.
- `type`: The connection class — `peer`, `user`, or `friend`:
  - `peer`: Asterisk sends calls to a peer.
  - `user`: Asterisk receives calls from a user.
  - `friend`: both directions at once.
- `host`: IP address or host name. The most common value is `dynamic`, used when the device registers to Asterisk.
- `secret`: Password to authenticate peers and users.

Warning: Use strong passwords with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for IAX md5 hashes are available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers. Example:

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

## Configurando os dispositivos SIP

Depois de definir os telefones no arquivo de configuração do Asterisk, é hora de configurar o próprio telefone. Neste exemplo, mostraremos como configurar um softphone gratuito — o SipPulse Softphone (faça o download em https://www.sippulse.com/produtos/softphone). Consulte o manual do seu dispositivo para entender os parâmetros do seu telefone. Passo 1: Configure o telefone para usar a extensão 6000. Execute o programa de instalação. Após a execução, abra as configurações de conta/SIP e adicione uma nova conta SIP. Preencha as informações solicitadas.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Confirme que seu telefone está registrado usando o comando de console `pjsip show endpoints` (ou `pjsip show endpoint 6000` para detalhes; `pjsip show contacts` mostra os contatos AOR registrados). Repita a configuração para o telefone 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## Configurando os dispositivos IAX

IAX2 é um protocolo legado (veja o capítulo *Legacy channels*), e o Softphone SipPulse é apenas SIP, portanto não pode registrar uma conta IAX. Se precisar testar IAX2, use um softphone que ainda o suporte. Crie uma nova conta IAX,

3. Selecione nova conta IAX.  
4. Insira as opções relacionadas ao telefone 6003 e, opcionalmente, ao 6004.  
5. Salve a configuração e verifique se o telefone está registrado usando `iax2 show peers`.

Importante: Use uma conta para SIP e outra para IAX. Se quiser configurar o sistema para tocar simultaneamente tanto IAX quanto SIP, mostraremos como fazer isso na seção do dialplan.

### Configurando uma interface PSTN

Para conectar ao PSTN, você precisará de uma interface foreign exchange office (FXO) e de uma linha telefônica. Você também pode usar uma extensão PBX existente. É possível obter uma placa de interface telefônica com interface FXO de vários fabricantes. Neste exemplo, mostraremos como instalar uma placa de interface DAHDI.

![FXS and FXO ports: the FXS port drives an analog phone (supplies dial tone and ring), while the FXO port connects Asterisk to the Telco line.](../images/04-first-pbx-fig02.png)

### Linhas analógicas usando DAHDI

Você pode comprar uma placa analógica compatível com DAHDI de vários fabricantes. X100P foi uma das primeiras placas Digium e já foi descontinuada. Alguns fabricantes ainda produzem clones semelhantes. Além do preço da X100P, encontramos vários problemas entre essas placas e placas‑mãe novas, portanto use‑a com cautela. X100P, na minha opinião, não é uma boa escolha para ambiente de produção. Qualquer placa compatível com DAHDI deve funcionar. Graças à equipe de desenvolvedores DAHDI, agora temos uma ferramenta para detectar e configurar as placas de interface quase automaticamente. Se você acabou de instalar os drivers DAHDI, não se esqueça de executar `make config` e reiniciar a máquina para carregá‑los automaticamente. Você pode usar os comandos abaixo para detectar e configurar sua placa. Passo 1: Para detectar seu hardware, use:

```
dahdi_hardware
```

Passo 2: Para configurar use:

```
dahdi_genconf
```

O comando acima gerará dois arquivos /etc/dahdi/system.conf e /etc/asterisk/dahdi-channels.conf. Os parâmetros padrão para dahdi_genconf geralmente são adequados, mas você pode alterá‑los no arquivo /etc/dahdi/genconf_parameters. Por padrão, ele inserirá as linhas (FXO) no contexto from-pstn e os telefones (FXS) no contexto from-internal. Etapa 3: Após executar dahdi_genconf, na última linha do arquivo /etc/asterisk/chan_dahdi.conf insira a seguinte linha:

```
#include dahdi-channels.conf
```

Etapa 4: Edite o arquivo /etc/dahdi/modules e comente todos os drivers não utilizados. Reinicie antes de prosseguir e verifique se os canais estão sendo reconhecidos usando:

```
*CLI> dahdi show channels
```

### Conectando ao PSTN usando um provedor VoIP

Se o seu orçamento é realmente limitado, você pode configurar um trunk SIP para conectar ao PSTN. É certamente a forma mais econômica de conectar ao PSTN. Existem milhares de provedores VoIP em todo o mundo. Para conectar a um deles, você precisará de alguns parâmetros. Parâmetros fornecidos pelo provedor SIP.

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

Dois parâmetros devem ser determinados por você.

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

Para acessar este tronco, usaremos o nome de canal `PJSIP/siptrunk`. A configuração `dtmf_mode=rfc4733` transporta DTMF fora da banda (RFC 4733 substitui o antigo RFC 2833; a carga útil é idêntica). A opção `identify`/`match` aceita endereços IP, CIDRs ou nomes de host, mas os nomes de host são resolvidos apenas uma vez no carregamento da configuração, portanto, para um provedor com IPs que mudam, liste explicitamente o(s) IP(s) de sinalização. Confirme o registro com `pjsip show registrations`.

## Introdução ao plano de discagem

O plano de discagem é como o coração do Asterisk. Ele define como o Asterisk trata cada chamada que chega ao PBX. Consiste em extensões que formam uma lista de instruções para o Asterisk seguir. As instruções são disparadas pelos dígitos recebidos do canal ou da aplicação. Para configurar o Asterisk com sucesso, é crucial entender o plano de discagem. A maior parte do plano de discagem está contida no arquivo extensions.conf no diretório /etc/asterisk. Esse arquivo usa a gramática de grupo simples e possui quatro conceitos principais:

- Extensões
- Prioridades
- Aplicações
- Contextos

Vamos criar um plano de discagem básico. Nas seções subsequentes deste livro, dedicarei um capítulo exclusivamente ao plano de discagem. Se você instalou os arquivos de exemplo (make samples), o extensions.conf já existe. Salve-o com outro nome e comece com um arquivo em branco.

## A estrutura do arquivo extensions.conf

O arquivo extensions.conf é dividido em seções. A primeira é a seção [general] seguida pela seção [globals]. O início de cada seção começa com a definição do seu nome (por exemplo, [default]) e termina quando outra seção é criada.

### A seção [general]

A seção general fica no topo do arquivo. Antes de começar a configurar o dialplan, é útil conhecer as opções gerais que controlam certos comportamentos do dialplan. Essas opções são:

- static and write protect: Se `static=yes` e `writeprotect=no`, você pode salvar o dialplan em execução de volta ao disco com o comando CLI:

```
*CLI> dialplan save
```

Warning: Se você emitir um comando `dialplan save` a partir da CLI, perderá quaisquer observações e comentários no arquivo.

- autofallthrough: Se autofallthrough estiver definido, então se uma extensão ficar sem nada para fazer, ela encerrará a chamada com BUSY, CONGESTION ou HANGUP, dependendo da melhor suposição do Asterisk. Esta é a configuração padrão. Se autofallthrough não estiver definido, então se uma extensão ficar sem nada para fazer, o Asterisk aguardará que uma nova extensão seja discada.
- clearglobalvars: Se clearglobalvars estiver definido, variáveis globais serão limpadas e reprocessadas em um reload do dialplan ou reload do Asterisk. Se clearglobalvars não estiver definido, então variáveis globais persistirão através de reloads e—mesmo que sejam deletadas do extensions.conf ou de um de seus arquivos incluídos—continuarão definidas com o valor anterior.
- extenpatternmatchnew: Usa um algoritmo de correspondência de padrão mais rápido, o que ajuda perceptivelmente quando você tem um grande número de extensões. O padrão é não.
- userscontext: Este é o contexto onde as entradas do users.conf são registradas.

### A seção [globals]

Na seção [globals] você definirá variáveis globais e seus valores iniciais. Você pode acessar a variável no dialplan usando ${GLOBAL(variable)}. Você pode até acessar variáveis definidas no ambiente linux/unix usando ${ENV(variable)}. Variáveis globais não diferenciam maiúsculas de minúsculas. Alguns exemplos podem ser:

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

No exemplo a seguir, você pode definir e testar uma variável global no dialplan.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contexts

Context is the named partition of the dial plan. After the [general] and [globals] sections, the dial plan is a set of contexts in which each context has several extensions, each extension has several priorities, and each priority calls an application with several arguments.

![Asterisk call flow: every call arrives on a channel (IAX, SIP, and others) as an incoming call leg; the channel's context — set globally or per-channel in the channel config file — decides which context in extensions.conf processes the call before it leaves on the outgoing leg.](../images/04-first-pbx-fig03.png)

![Call processing: the `context=` defined for a channel (in chan_dahdi.conf or pjsip.conf) names the matching context in extensions.conf where the dial plan handles the call.](../images/04-first-pbx-fig04.png)

You can build a simple dial plan to reach other phones and the PSTN. However, Asterisk is much more powerful than that. Our objective is to teach you more details of what is possible in the dial plan.

## Extensions

Ao contrário do PBX tradicional, onde ramais estão associados a telefones, interfaces, menus etc., no Asterisk um ramal é uma lista de comandos a serem processados quando um número ou nome de ramal específico é acionado. Os comandos são processados em ordem de prioridade.

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

Um ramal pode ser literal, padrão ou especial. Um ramal padrão inclui apenas números ou nomes e os caracteres * e #; 12#89* é um ramal literal válido. Nomes também podem ser usados para correspondência de ramais. Ramais diferenciam maiúsculas de minúsculas. No entanto, não é possível criar dois ramais com o mesmo nome mas com casos diferentes. Quando um ramal é discado, o comando com a primeira prioridade é executado, seguido pelo comando com prioridade 2 e assim sucessivamente. Isso ocorre até que a chamada seja desconectada ou algum comando retorne o número um, indicando falha. O que o Asterisk faz quando a última prioridade é executada é regulado pelo parâmetro autofallthrough. Veja a seção [general] neste capítulo. Exemplo:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Acima você encontra a lista de instruções a serem processadas quando o ramal 123 é discado. A primeira prioridade é atender o canal (necessário quando o canal está no estado de toque: ou seja, canais FXO). A segunda prioridade é reproduzir um arquivo de áudio chamado tt-weasels. A terceira prioridade desliga o canal. Outra opção é tratar a chamada de acordo com o caller ID. Você pode usar o caractere / para especificar o caller ID a ser processado. Exemplos:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Este exemplo acionará o ramal 123 e executará as opções a seguir somente se o caller ID for 100. Isso também pode ser feito usando o padrão descrito abaixo:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: mapeia um ramal para um canal. É usado para monitorar o estado do canal. É usado em conjunto com presença. O telefone precisa oferecer suporte a isso.

#### Patterns

Você pode usar padrões e literais no dialplan. Padrões são muito úteis para reduzir o tamanho do dialplan. Todos os padrões começam com o caractere “_”. Os seguintes caracteres podem ser usados para definir um padrão. A figura identifica os padrões disponíveis para uso com Asterisk.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Special extensions

Asterisk usa alguns nomes de ramais como ramais padrão.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

Descrição:

- **s**: Start. É usado para tratar uma chamada quando não há número discado. É útil para troncos FXO e processamento em menu.
- **t**: Timeout. É usado quando chamadas permanecem inativas após um prompt ter sido reproduzido. Também é usado para desligar uma linha inativa.
- **T**: AbsoluteTimeout. Se você estabelecer um limite de chamada usando a função de dialplan `TIMEOUT(absolute)`, quando a chamada ultrapassar o limite definido, ela será enviada para o ramal T.
- **h**: Hangup. É chamado após o usuário desconectar a chamada.
- **i**: Invalid. É acionado quando você liga para um ramal inexistente no contexto. O uso desses ramais pode afetar o conteúdo dos registros CDR — especificamente, o campo dst que não contém o número discado.
- **o**: Operator. É usado para ir ao operador quando o usuário pressiona “0” durante a caixa postal.

O

## Variables

No PBX Asterisk, as variáveis podem ser globais, específicas de canal e específicas de ambiente. Você pode usar a aplicação NoOP() para ver o conteúdo de uma variável no console. Ela pode usar uma variável global ou uma variável específica de canal como argumentos da aplicação. Uma variável pode ser referenciada como no exemplo a seguir, onde varname é o nome da variável.

```
${varname}
```

Um nome de variável pode ser uma string alfanumérica que começa com uma letra. Nomes de variáveis globais não diferenciam maiúsculas de minúsculas. Entretanto, variáveis de sistema (definidas pelo Asterisk ou definidas por canal) diferenciam maiúsculas de minúsculas. Assim, a variável ${EXTEN} é diferente de ${exten}.

### Global variables

Variáveis globais podem ser configuradas na seção [global] no arquivo extensions.conf ou usando a aplicação:

```
set(Global(variable)=content)
```

### Channel-specific variables

Variáveis específicas de canal são configuradas usando a aplicação set(). Cada canal recebe seu próprio espaço de variáveis. Não há risco de colisões entre variáveis de canais diferentes. Uma variável específica de canal é destruída quando o canal desliga. Algumas das variáveis mais usadas são:

- ${EXTEN} Extensão discada
- ${CONTEXT} Contexto atual
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} ID de chamador atual
- ${PRIORITY} Prioridade atual

Outras variáveis específicas de canal são todas em maiúsculas. Você pode ver o conteúdo de várias variáveis usando a aplicação dumpchan(). Abaixo está um trecho simples das variáveis dump-channel.

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Saída do Dumpchan:

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

O layout de campos acima é a saída do Asterisk 22 `DumpChan` (um nome de canal real `PJSIP/...`, os campos `CallerIDNum`/`ConnectedLineID`, e as linhas `Raw*`/`Transcode`/`BridgeID` que os canais PJSIP preenchem). Diferente do driver antigo, um canal PJSIP não define automaticamente as variáveis de canal `SIPCALLID`/`SIPUSERAGENT`; os detalhes equivalentes de SIP são lidos sob demanda com as funções de dialplan `PJSIP_HEADER()` e `CHANNEL()` — por exemplo `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` e `${CHANNEL(rtp,dest)}` para o endereço RTP remoto.

### Environment-specific variables

Variáveis específicas de ambiente podem ser usadas para acessar variáveis definidas no sistema operacional. Você pode definir variáveis específicas de ambiente usando a função ENV(). Por exemplo:

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

Algumas aplicações usam variáveis para entrada e saída de dados. Você pode definir variáveis antes de chamar a aplicação ou recuperar a variável após a execução da aplicação. Por exemplo: A aplicação Dial retorna as seguintes variáveis:

- ${DIALEDTIME} ->Este é o tempo desde a discagem de um canal até ele ser desconectado.
- ${ANSWEREDTIME} -> Este é o tempo de duração da chamada real.
- ${DIALSTATUS} Este é o status da chamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Mensagem de erro da chamada.

## Expressions

Expressions can be very useful in the dial plan. They are used to manipulate strings and perform math and logical operations.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

The expression syntax is defined as follows:

```
$[expression1 operator expression2]
```

Let’s suppose that we have a variable called “I” and we want to add 100 to the variable:

```
$[${I}+100]
```

When Asterisk finds an expression in the dial plan, it changes the entire expression by the resulting value.

### Operators

The following operators can be used to build expressions. It is important to observe operator precedence.

1. Parentheses “()”
2. Unary operators “! -“
3. Regular expression “: =~
4. Multiplicative operators “* / %”
5. Additive operators “+ -“
6. Comparison operators
7. Logical operators
8. Conditional operators

#### Math Operators

- Addition (+)
- Subtraction (-)
- Multiplication(*)
- Division (/)
- Modulus (%)

#### Logical Operators

- Logical “AND” (&)
- Logical “OR” (|)
- Logical Unary Complement (!)

#### Regular expression operators

- Regular expression matching (:)
- Regular expression exact matching (=~)

A regular expression is a special text string used to describe a search pattern. You can think of regular expressions as wildcards. Regular expressions are used to match a string to a pattern to check the matching. If the match succeeds and the regular expression contains at least one match, the first match is returned; otherwise, the result is the number of characters matched.

#### Comparison operators

The result of a comparison is 1 if the relation is true or 0 if it is false.

- = equal
- != not equal
- < less than
- > greater than
- <= less than or equal to
- >= greater than or equal to

### LAB. Evaluate the following expressions:

Put these expressions in your dial plan and use the NoOP() application to evaluate the expressions. Dial 9002 and examine the results in the Asterisk console. Use verbose 15 to show the results.

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

Algumas aplicações foram substituídas por funções, que permitem o processamento de variáveis de forma mais avançada do que apenas expressões. Você pode ver a lista completa de funções emitindo o seguinte comando no console:

```
*CLI> core show functions
```

Comprimento da string: ${LEN(string)} retorna o comprimento da string

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

Na primeira operação, o sistema mostra 5 como resultado (o número de letras da palavra “fruit”). A segunda retorna o número 4 (o número de letras da palavra “pear”). Substrings: Retorna a substring, começando a partir da posição definida pelo parâmetro “offset”, com o comprimento da string definido no parâmetro “length”. Se o offset for negativo, ele começa da direita para a esquerda, iniciando no final da string. Se o length for omitido ou negativo, ele pega a string inteira a partir do offset.

```
${string:offset:length }
```

Exemplo #1: Várias substrings

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Exemplo #2: Pegue o código de área dos três primeiros dígitos.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Exemplo #3: Obtém todos os dígitos da variável ${EXTEN}, exceto o código de área.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Concatenação de strings

Para concatenar duas strings, basta escrevê‑las juntas.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Aplicações

Para construir um dial plan, precisamos entender o conceito de applications. Você usará applications para manipular o channel no dial plan. Applications são implementadas em vários modules. Applications disponíveis dependem dos modules. Você pode exibir todas as applications do Asterisk usando o comando de console:

```
*CLI> core show applications
```

Alternativamente, você pode exibir detalhes de um aplicativo específico usando o exemplo a seguir:

```
*CLI> core show application Dial
```

Para construir um plano de discagem simples, você precisa conhecer alguns aplicativos. Discutiremos exemplos mais avançados mais adiante no livro.

![The handful of applications needed to build a simple dial plan: Answer (answer a channel), Dial (call another channel), Hangup (hang up a channel), Playback (play an audio file), and Goto (jump to a priority, extension, or context).](../images/04-first-pbx-fig09.png)

Usaremos esses aplicativos (acima) para criar um plano de discagem simples para duas PBXs básicas.

### Answer()

[Synopsis] Answers a channel if ringing [Description] Answer([delay]): Se a chamada ainda não foi atendida, o aplicativo a atenderá. Caso contrário, não tem efeito sobre a chamada. Se um atraso for especificado, o Asterisk aguardará o número de milissegundos indicado em ‘delay’ antes de atender a chamada.

### Dial()

A descrição a seguir pode ser obtida emitindo o comando **show application dial** no plano de discagem. Para facilitar a busca, ela é reproduzida abaixo. A sintaxe para o aplicativo Dial também é mostrada abaixo:

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

Esta aplicação fará chamadas para um ou mais canais especificados. Assim que um dos canais solicitados atender, o canal originador será atendido — se ainda não tiver sido atendido. Esses dois canais ficarão então ativos em uma chamada em ponte. Todos os demais canais solicitados serão então desligados. A menos que um timeout seja especificado, a aplicação Dial aguardará indefinidamente até que um dos canais chamados atenda, o usuário desligue, ou todos os canais chamados estejam ocupados ou indisponíveis. A execução do dialplan continuará se nenhum canal solicitado puder ser chamado ou se o timeout expirar. Esta aplicação define as seguintes variáveis de canal ao concluir:

- DIALEDTIME - Este é o tempo desde a discagem de um canal até o momento em que ele é desconectado.
- ANSWEREDTIME - Este é o tempo de duração de uma chamada real.
- DIALSTATUS - Este é o status da chamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

Para os Modos de Privacidade e Triagem, a variável DIALSTATUS será definida como DONTCALL se a parte chamada escolher enviar a parte chamadora para o script 'Go Away'. A variável DIALSTATUS será definida como TORTURE se a parte chamada quiser enviar o chamador para o script 'torture'. Esta aplicação relatará término normal se o canal originador desligar ou se a chamada for em ponte e qualquer uma das partes na ponte encerrar a chamada. O URL opcional será enviado à parte chamada se o canal o suportar. Se a variável OUTBOUND_GROUP estiver definida, todos os canais peer criados por esta aplicação serão incluídos nesse grupo (como em

```
Set(GROUP()=...).
```

The following table summarizes some of the most frequently used options for the application Dial. For the complete list, use the console command `core show application Dial`. In Asterisk 22 these options are separated from the channel and timeout by commas — for example `Dial(PJSIP/2000,20,tTm)`.

| Option | Description |
|--------|-------------|
| `A(x)` | Reproduz um anúncio para a parte chamada, usando `x` como o arquivo. |
| `C` | Reinicia o CDR para esta chamada. |
| `d` | Permite que o usuário que está ligando disque uma extensão de 1 dígito enquanto aguarda a chamada ser atendida. Sai para essa extensão se ela existir no contexto atual, ou para o contexto definido na variável `EXITCONTEXT`, se existir. |
| `D([called][:calling])` | Envia as sequências DTMF especificadas após a parte chamada atender, mas antes da chamada ser interligada. A sequência `called` é enviada para a parte chamada e a sequência `calling` para a parte que está ligando. Qualquer um dos parâmetros pode ser usado isoladamente. |
| `f` | Força o caller ID do canal que está ligando a ser definido como a extensão associada ao canal via um dial plan `hint`. Útil quando o PSTN não permite um caller ID arbitrário. |
| `g` | Prossegue a execução do dial plan na extensão atual se o canal de destino desligar. |
| `G(context^exten^pri)` | Se a chamada for atendida, transfere a parte que está ligando para a prioridade especificada e a parte chamada para prioridade+1. Opcionalmente pode ser especificada uma extensão (ou extensão e contexto); caso contrário, a extensão atual é usada. |
| `h` | Permite que a parte chamada desligue enviando o dígito DTMF `*`. |
| `H` | Permite que a parte que está ligando desligue enviando o dígito DTMF `*`. |
| `L(x[:y][:z])` | Limita a chamada a `x` ms, reproduz um aviso quando restam `y` ms, e repete o aviso a cada `z` ms. Veja as variáveis `LIMIT_*` abaixo. |
| `m([class])` | Fornece música em espera para a parte que está ligando até que o canal solicitado atenda. Uma classe MusicOnHold específica pode ser especificada. |
| `r` | Indica toque para a parte que está ligando e não passa áudio até que o canal chamado atenda. |
| `S(x)` | Desliga a chamada `x` segundos após a parte chamada atender. |
| `t` | Permite que a parte chamada transfira a parte que está ligando enviando a sequência DTMF definida em `features.conf`. |
| `T` | Permite que a parte que está ligando transfira a parte chamada enviando a sequência DTMF definida em `features.conf`. |
| `w` | Permite que a parte chamada habilite gravação de toque único enviando a sequência DTMF definida em `features.conf`. |
| `W` | Permite que a parte que está ligando habilite gravação de toque único enviando a sequência DTMF definida em `features.conf`. |
| `k` | Permite que a parte chamada estacione a chamada enviando a sequência DTMF definida para estacionamento de chamada em `features.conf`. |
| `K` | Permite que a parte que está ligando estacione a chamada enviando a sequência DTMF definida para estacionamento de chamada em `features.conf`. |

The `L(x[:y][:z])` option can be tuned with the following special variables:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (default `yes`): reproduz sons para o chamador.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: reproduz sons para a parte chamada.
- `LIMIT_TIMEOUT_FILE` — arquivo a ser reproduzido quando o tempo acabar.
- `LIMIT_CONNECT_FILE` — arquivo a ser reproduzido quando a chamada começar.
- `LIMIT_WARNING_FILE` — arquivo a ser reproduzido como aviso quando `y` estiver definido. O padrão é anunciar o tempo restante.

Example:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

In the example above, the application will dial to the corresponding PJSIP channel. Both caller and called could transfer the call (Tt). Music on hold will be heard instead of ring back. If nobody answers within 20 seconds, the extension will go to the next priority.

### Hangup()

Hangs up the calling channel [Description] Hangup([causecode]): This application will hang up the calling channel. If a cause code is given, the channel's hang-up cause will be set to the given value.

### Goto()

Jump to a particular priority, extension, or context [Description] Goto([[context|]extension|]priority): This application will cause the calling channel to continue the dial plan execution at the specified priority. If no specific extension (or extension and context) are specified, this application will jump to the specified priority of the current extension. If the attempt to jump to another location in the dial plan is not successful, the channel will continue at the next priority of the current extension.

## Construindo um plano de discagem

Para construir um plano de discagem simples, você precisa tratar todas as chamadas recebidas e realizadas criando contexts e extensions. Nesta seção, mostraremos como criar as extensions mais comuns.

### Discando entre extensions

Para habilitar a discagem entre extensions, podemos usar a variável de canal ${EXTEN}, que se refere à extension discada. Por exemplo, se o intervalo de extensions for entre 4000 e 4999 e todas as extensions usarem SIP, poderíamos adotar o seguinte comando:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Discando para um destino externo

Para discar um destino externo você pode preceder o número discado com uma rota. Na América do Norte, é comum usar 9 seguido do número a ser discado externamente. Se você estiver usando um canal analógico ou digital para o PSTN, o comando deve ser semelhante ao seguinte: Se quiser usar o tronco SIP em vez do DAHDI, use o canal `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

A linha acima permitirá que você disque 9 e o número desejado. No exemplo apresentado, você usará o primeiro canal DAHDI (DAHDI/1). Se houver várias linhas e esta estiver ocupada, a chamada não será completada. No entanto, você pode usar a linha a seguir para escolher automaticamente o primeiro canal DAHDI disponível. Opcionalmente, pode usar o tronco SIP em vez de DAHDI. No formulário PJSIP `Dial(PJSIP/number@siptrunk,...)`, o número discado é a parte do usuário e `siptrunk` é o endpoint configurado acima.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

O parâmetro “g1” buscará o primeiro canal disponível no grupo, permitindo o uso de todos os canais. Usando a linha abaixo, você poderia discar um número de longa distância.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Discando 9 para obter uma linha PSTN

Se você não tem restrições para discagem externa, pode simplificar e usar o seguinte:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Recebendo uma chamada na extensão do operador

No exemplo a seguir, a extensão do operador é 4000. A linha PSTN está conectada a uma interface FXO. No arquivo chan_dahdi.conf, o contexto especificado é from-pstn. Qualquer chamada proveniente da PSTN será roteada para o contexto from-pstn no dialplan. Esta linha não possui discagem direta interna (DID); portanto, teremos que receber a chamada via extensão “s”. Se estiver recebendo da trunk SIP, use o contexto [from-sip].

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

### Recebendo uma chamada usando discagem direta interna (DID)

Se você possui uma linha digital, receberá a extensão discada. Quando isso ocorre, não é necessário encaminhar a chamada para o operador; ao contrário, você pode encaminhar a chamada diretamente para o destino. Suponha que sua faixa de DID vá de 3028550 a 3028599 e os últimos quatro números sejam passados no DID. A configuração ficaria como no exemplo a seguir:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Reproduzindo várias extensões simultaneamente

Você pode configurar o Asterisk para discar uma extensão e, se não for atendida, discar várias outras extensões simultaneamente, conforme indicado no exemplo a seguir:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

Neste exemplo, quando alguém disca o operador, o canal DAHDI/1 é tentado inicialmente. Se ninguém atender após 15 segundos (timeout), os canais DAHDI/1, DAHDI/2 e DAHDI/3 tocarão simultaneamente por mais 15 segundos.

### Roteamento por Caller ID

Neste exemplo, você pode aplicar tratamentos diferentes com base no caller ID, o que pode ser útil para spammers de chamadas. Por exemplo:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

In this example, we have added a special rule that, if the caller ID is 4832518888, you play back a message from the previously recorded file “I-have-moved-to-china”. Other calls are accepted as usual.

### Usando variáveis no dial plan

Asterisk can use global and channel variables in the dial plan as arguments for certain applications. Look at the following examples:

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

Usar variáveis facilita alterações futuras. Se você mudar a variável, todas as referências são alteradas imediatamente.

### Gravando um anúncio

Em algumas das opções discutidas mais adiante nesta seção, usaremos prompts gravados. Aqui mostramos uma maneira simples de gravá‑los. Usaremos a aplicação Record() para salvar o anúncio usando o próprio telefone.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Estas instruções permitem gravar qualquer mensagem a partir de um softphone. Exemplo: discar recordmenu do softphone As instruções chamarão a gravação com a variável ${EXTEN:6} sem as primeiras seis letras. Em outras palavras, a instrução equivale a record(menu:gsm). Tudo que você precisa fazer é discar record + nome_do_arquivo_a_ser_gravado, pressionar # para terminar a gravação e aguardar ouvir a gravação.

### Recebendo as chamadas em uma recepcionista digital

Agora que temos alguns exemplos simples, vamos expandir nosso aprendizado sobre as aplicações background() e goto(). A chave para sistemas interativos no Asterisk é a aplicação background(), que permite executar um arquivo de áudio que, quando o chamador pressiona uma tecla, é interrompido para enviar a chamada para a extensão discada. Sintaxe da aplicação background():

```
exten=>extension, priority, background(filename)
```

Outra aplicação muito útil é goto(). Como o nome indica, ela salta para o contexto, extensão e prioridade indicados. Sintaxe da aplicação goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Formatos válidos para o comando goto():

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

No exemplo a seguir, criaremos uma recepcionista digital. É muito simples editar o arquivo extensions.conf e configurar as seguintes extensões:

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

As extensões SIP usam `PJSIP/` e as extensões IAX usam `IAX2/` — ambos os drivers são incluídos no Asterisk 22, embora `chan_iax2` agora seja considerado legado e SIP/PJSIP seja o preferido.

No arquivo menu1.gsm, grave a mensagem “press the extension or wait for the operator”. Quando o usuário discar o número 6000, ele será enviado para a extensão 6000. Neste ponto, você deve ter uma compreensão clara do uso de várias aplicações, incluindo answer(), background(), goto(), hangup() e playback(). Se você não tiver uma compreensão clara, por favor, releia este capítulo até se sentir confortável com o conteúdo. Você usará a aplicação background com muita frequência. Uma vez que você entenda os fundamentos de extensões, prioridades e aplicações, será fácil criar um plano de discagem simples. Esses conceitos serão explorados com mais profundidade mais adiante no livro, e você verá que o plano de discagem se tornará mais poderoso.

## Resumo

Neste capítulo, você aprendeu que os arquivos de configuração são armazenados no diretório **/etc/asterisk**. Para usar o Asterisk, é primeiro necessário configurar os canais (por exemplo, pjsip, dahdi, iax). Existem três gramáticas diferentes para arquivos de configuração: grupo simples, herança de objetos e entidade complexa. O dialplan é criado no arquivo **extensions.conf** e consiste em um conjunto de contexts e extensions. No dialplan, cada extension aciona uma aplicação. Você aprendeu a usar as aplicações **playback**, **background**, **dial**, **goto**, **hangup** e **answer**.

## Quiz

1. Os arquivos de configuração de canal são (escolha todas as que se aplicam):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. No Asterisk 22, o único peer `chan_sip` `[6001]` (`type=friend`/`host=dynamic`) é substituído em `pjsip.conf` por qual conjunto de objetos relacionados?
   - A. Um `type=peer` e um `type=user`
   - B. Um `type=endpoint`, um `type=auth` e um `type=aor`
   - C. Um único `type=friend`
   - D. Um `type=transport` e um `type=global`
3. Definir um contexto no arquivo de configuração de canal importa porque define o contexto de entrada para chamadas desse canal — uma chamada do canal é processada no contexto correspondente em `extensions.conf`.
   - A. Verdadeiro
   - B. Falso
4. As principais diferenças entre as aplicações `Playback()` e `Background()` são (escolha duas):
   - A. Playback reproduz um prompt mas não aguarda dígitos.
   - B. Background reproduz um prompt mas não aguarda dígitos.
   - C. Background reproduz uma mensagem e aguarda que dígitos sejam pressionados.
   - D. Playback reproduz uma mensagem e aguarda que dígitos sejam pressionados.
5. Quando uma chamada entra no Asterisk através de uma placa de interface telefônica (FXO) sem DID, ela é tratada na extensão especial:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Formatos válidos para a aplicação `Goto()` são (escolha três):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. O padrão `_7[1-5]XX` corresponde (escolha todas as que se aplicam):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. Em `Dial(PJSIP/${EXTEN},20,tTm)`, o que a opção `m` faz?
   - A. Limita a chamada a uma duração máxima.
   - B. Fornece música em espera ao chamador em vez de tom de retorno até que o canal atenda.
   - C. Envia dígitos DTMF após a parte chamada atender.
   - D. Força o ID do chamador usando uma dica de dialplan.
9. Na gramática de herança de opções usada por `chan_dahdi.conf`, você:
   - A. Define o objeto em uma única linha.
   - B. Define opções primeiro e declara os objetos abaixo das opções definidas.
   - C. Define um contexto separado para cada objeto.
10. Prioridades em uma extensão devem ser numeradas consecutivamente (1, 2, 3, …) e não podem usar `n`.
    - A. Verdadeiro
    - B. Falso

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
