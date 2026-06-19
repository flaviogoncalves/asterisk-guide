# Construindo seu primeiro PBX com PJSIP

Neste capítulo, você aprenderá como realizar uma configuração básica de um PBX Asterisk. O objetivo principal aqui é ver o PBX funcionando pela primeira vez, ser capaz de discar entre ramais, discar para uma mensagem sendo reproduzida e discar para um único tronco analógico ou SIP. A ideia por trás deste capítulo é garantir que seu Asterisk esteja instalado e funcionando o mais rápido possível. Após concluir o trabalho neste capítulo, você terá base suficiente para se preparar para os capítulos subsequentes, onde nos aprofundaremos nos detalhes de configuração.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Entender e editar arquivos de configuração;
- Instalar softphones baseados em SIP;
- Instalar e configurar um tronco SIP;
- Instalar e configurar uma conexão analógica;
- Discar entre ramais;
- Discar entre telefones e destinos externos; e
- Configurar um atendimento automático (URA).

## Entendendo os arquivos de configuração

O Asterisk é controlado por arquivos de configuração de texto localizados em /etc/asterisk. O formato do arquivo é semelhante aos arquivos “.ini” do Windows. Um ponto e vírgula é usado como caractere de comentário, os sinais “=” e “=>” são equivalentes e espaços são ignorados.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

O Asterisk interpreta “=” e “=>” da mesma forma. Diferenças na sintaxe são usadas para distinguir entre objetos e variáveis. Use “=” quando quiser declarar uma variável e “=>” para designar um objeto. A sintaxe é a mesma entre todos os arquivos, mas três tipos de gramática são usados, conforme discutido abaixo.

## Gramáticas

| Gramática | Como o objeto é criado | Arquivo de conf. | Exemplo |
|---------|---------------------------|------------|---------|
| Grupo Simples | Tudo na mesma linha | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Herança de Opções | Opções são definidas primeiro, o objeto herda as opções | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Entidade Complexa | Cada entidade recebe um contexto | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Grupo Simples

O formato de grupo simples usado em `extensions.conf` e `voicemail.conf` é a gramática mais básica. Cada objeto é declarado com opções na mesma linha. Exemplo:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

Neste exemplo, o objeto 1 é criado com as opções op1, op2 e op3, enquanto o objeto 2 é criado com as opções op1, op2 e op3.

### Gramática de herança de opções de objeto

Este formato é usado pelos arquivos chan_dahdi.conf e agents.conf, onde inúmeras opções estão disponíveis e a maioria das interfaces e objetos compartilham as mesmas opções. Normalmente, uma ou mais seções possuem declarações de objetos e canais. As opções para o objeto são declaradas acima do objeto e podem ser alteradas para outro objeto. Embora este conceito seja difícil de entender, é muito fácil de usar. Exemplo:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

As duas primeiras linhas configuram o valor das opções op1 e op2 para “bas” e “adv”, respectivamente. Quando o objeto 1 é instanciado, ele é criado usando a opção 1 como “bas” e a opção 2 como “adv”. Após definir o objeto 1, alteramos a opção 1 para “int”. Em seguida, criamos o objeto 2 com a opção 1 como “int” e a opção 2 como “adv”.

### Objeto de entidade complexa

Este formato é usado por pjsip.conf, iax.conf e outros arquivos de configuração nos quais existem inúmeras entidades com muitas opções. Normalmente, este formato não compartilha um grande volume de configurações comuns. Cada entidade recebe um contexto. Às vezes, existem contextos reservados, como [general] para configurações globais. As opções são declaradas nas declarações de contexto. Exemplo:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

A entidade [entity1] possui os valores “value1” e “value2” para as opções op1 e op2, respectivamente. A entidade [entity2] possui os valores “value3” e “value4” para as opções op1 e op2.

## Opções para construir um LAB para Asterisk

Para configurar um PBX, você precisará de um hardware básico. Não é difícil nem caro, mas há algumas opções a serem consideradas. Tudo o que você precisará são dois telefones e uma conexão com a rede pública. Algumas opções e combinações são possíveis ao criar seu laboratório, as quais discutiremos abaixo.

### Opção 1: LAB Completo

Com o LAB completo, é possível testar todos os cenários disponíveis e comparar soluções como ATA, telefones IP e softphones. Você também pode aprender sobre troncos analógicos e SIP. Você precisará de:

- Um adaptador de telefone analógico SIP (ATA)
- Um telefone IP
- Um servidor dedicado para o Asterisk
- Uma estação de trabalho com um softphone
- Uma placa de interface analógica com pelo menos duas interfaces (1 FXO e 1 FXS)
- Uma conta de provedor VoIP

### Opção 2: LAB Econômico

Com o LAB econômico, simplificamos um pouco. Usamos o ATA, que geralmente é menos caro que o telefone IP, e uma única placa FXO, que é realmente barata. Não poderemos usar telefones analógicos conectados diretamente ao servidor, mas isso não ocorre com frequência na prática. Você precisará de:

- Um adaptador de telefone analógico SIP (ATA)
- Um servidor dedicado para o Asterisk
- Uma estação de trabalho para o softphone
- Uma placa de interface analógica com 1 FXO
- Uma conta com um provedor VoIP

### Opção 3: LAB Super econômico

O terceiro LAB usa um servidor virtualizado no próprio notebook do aluno. O problema com este modelo são os conflitos gerados pela porta UDP. Às vezes, tanto o servidor Asterisk quanto o softphone tentam acessar a mesma porta, impedindo que o Asterisk vincule a porta de endereço. Outra questão é a qualidade das chamadas; ambientes virtuais não são indicados para aplicações de tempo real como o Asterisk. Use um softphone gratuito para o servidor e a estação de trabalho e uma conexão de tronco com um provedor SIP. Você precisará de:

- Um laptop executando um softphone
- Uma máquina virtual (VirtualBox, VMware ou similar) para instalar o Asterisk
- Uma conta com um provedor VoIP

## Sequência de Instalação

Para ajudá-lo a entender a sequência de instalação, delineamos a sequência de passos necessários para instalar e configurar o Asterisk.

![Layout do laboratório de referência: softphones SIP/IAX, um telefone IP e adaptadores analógicos como ramais (1), o servidor Asterisk com interfaces ETH0/FXO/FXS (3) e os troncos para a PSTN através de um provedor VoIP ou um link de banda larga (2).](../images/04-first-pbx-fig01.png)

1. Configuração de ramais a. Ramais SIP (ATA, Softphone, Telefone IP) b. Ramais IAX c. Ramais FXS 2. Configuração de tronco a. Configuração de um tronco SIP b. Configuração de um tronco FXO 3. Construindo um dialplan básico a. Discagem entre ramais b. Discagem para destinos externos c. Recebendo uma chamada no ramal da operadora d. Recebendo uma chamada em um atendimento automático

## Configuração dos ramais

Os ramais são telefones SIP, IAX ou analógicos conectados a uma porta FXS. Para configurar um ramal, você deve editar o arquivo de configuração relacionado ao canal (pjsip.conf, iax.conf, chan_dahdi.conf)

### Ramais SIP

No Asterisk 22, o PJSIP (a pilha `res_pjsip`, configurada em `/etc/asterisk/pjsip.conf`) é o driver de canal SIP. Ele suporta múltiplos transportes por endpoint, é mantido ativamente e é o único driver SIP fornecido com a plataforma. (O driver original `chan_sip` foi removido no Asterisk 21 — veja o capítulo *Legacy channels* se precisar migrar uma configuração antiga.)

A ideia aqui é configurar um PBX simples. (Capítulos subsequentes fornecem uma sessão completa de SIP/PJSIP com todos os detalhes.) O PJSIP é configurado em `/etc/asterisk/pjsip.conf` e contém todos os parâmetros relacionados a telefones SIP e provedores VoIP. Os clientes SIP precisam ser configurados antes que você possa fazer e receber chamadas.

#### O transporte

No PJSIP, a configuração do ouvinte (endereço de bind, porta, protocolo) reside em um objeto `transport`. O Asterisk possui proteção integrada contra adivinhação de nome de usuário — ele sempre retorna um desafio de autenticação idêntico para usuários desconhecidos e conhecidos, e solicitações não identificadas repetidas de um IP são limitadas por taxa através das opções `[global]` `unidentified_request_count`/`unidentified_request_period`. As principais opções de um transporte são:

- protocol: O protocolo de transporte — `udp`, `tcp`, `tls`, `ws` ou `wss`.
- bind: Endereço e porta aos quais o ouvinte se vincula. Se você definir o endereço como `0.0.0.0`, ele se vinculará a todas as interfaces; a porta SIP padrão é 5060 para UDP/TCP.

Um transporte UDP mínimo:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

A seleção de codec (`disallow`/`allow`) e o `context` padrão são configurados em cada `endpoint` (mostrado abaixo), não no transporte. Chamadas anônimas/convidadas são tratadas por um `endpoint` chamado `anonymous`. Os temporizadores de registro são controlados por AOR via `maximum_expiration`/`default_expiration`.

#### Clientes SIP

Após concluir a seção de transporte, é hora de configurar os clientes SIP. Gostaria de lembrar mais uma vez ao leitor que teremos um capítulo inteiro de SIP/PJSIP mais adiante no livro. Por enquanto, vamos nos concentrar no básico e deixar os detalhes para depois.

No PJSIP, um cliente SIP é construído a partir de um conjunto de objetos relacionados, unidos por referência de nome:

- `endpoint`: O comportamento da chamada — codecs (`allow`/`disallow`), o dialplan `context` e quais `auth` e `aors` ele usa.
- `auth`: As credenciais. `username` é o usuário de autenticação SIP e `password` é o segredo usado para autenticar o dispositivo.
- `aor`: O "address of record" — onde o endpoint pode ser alcançado. Ou um `contact=` estático (para um dispositivo em um IP fixo) ou `max_contacts=` para permitir que o dispositivo se registre dinamicamente.

Aviso: Use senhas fortes, com pelo menos 8 caracteres, caracteres alfanuméricos e numéricos, e pelo menos um símbolo. Relatos de servidores hackeados apareceram nas listas de discussão, e crackers de senha de força bruta para SIP estão facilmente disponíveis para script kiddies. Fraudes de telecomunicações custam milhares de dólares para consumidores e provedores.

O endpoint 6000 é um dispositivo em um IP fixo, portanto, seu AOR carrega um `contact` estático em vez de permitir o registro. O endpoint 6001 é um dispositivo que se registra, portanto, seu AOR permite que ele se registre (`max_contacts=1`):

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

O PJSIP permite que as seções `endpoint`, `auth` e `aor` compartilhem o mesmo nome de seção (por exemplo, os dois blocos `[6001]` acima, distinguidos por seu `type=`); muitos administradores, em vez disso, adicionam um sufixo (`[6001]`, `[6001-auth]`, `[6001]` aor) para facilitar a leitura. Para um dispositivo que se registra, o contato é aprendido dinamicamente quando o telefone se registra, portanto, o AOR não precisa de um `contact` estático.

## Ramais IAX

O `chan_iax2` ainda é fornecido no Asterisk 22, mas agora é legado; SIP/PJSIP é o protocolo preferido para novas implantações.

Você também pode criar ramais IAX. Este protocolo é nativo do Asterisk, e teremos uma seção inteira dedicada a ele mais adiante neste livro. Por enquanto, vamos criar alguns ramais usando o protocolo. Como a primeira seção a ser configurada, a seção [general] tem certos parâmetros a serem configurados. As principais opções são:

- allow/disallow: Define quais codecs serão usados.
- bindaddr: Endereço a ser vinculado ao ouvinte SIP do Asterisk. Se você configurá-lo como 0.0.0.0 (padrão), ele se vinculará a todas as interfaces.
- context: Define o contexto padrão para todos os clientes, a menos que alterado na seção do cliente. Usamos dummy por motivos de segurança. Usuários não autenticados entram neste contexto quando a opção allowguest é definida como yes.
- bindport: Porta UDP SIP para escutar.
- delayreject: Quando definido como yes, atrasa o envio de uma rejeição de autenticação para um REGREQ ou AUTHREQ, o que melhora a segurança contra ataques de força bruta de senha.
- bandwidth: Quando definido como high, permite a seleção de codecs de alta largura de banda, como o g711 em suas variantes ulaw e alaw.

A seguir, uma amostra da seção [general] do arquivo iax.conf.

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

Após terminar as seções gerais, é hora de configurar os clientes IAX.

- [name]: Quando um dispositivo SIP se conecta ao Asterisk, ele usa a parte do nome de usuário do URI SIP para encontrar o peer/user.
- type: Configura a classe de conexão. As opções são peer, user e friend. o peer: O Asterisk envia chamadas para um peer. o user: O Asterisk recebe chamadas de um usuário. o friend: Ambos ocorrem ao mesmo tempo.
- host: Endereço IP ou nome do host. A opção mais comum é dynamic, que é usada quando o host se registra no Asterisk.
- secret: Senha para autenticar peers e usuários.

Aviso: Use senhas fortes com pelo menos 8 caracteres, caracteres alfanuméricos e numéricos, e pelo menos um símbolo. Relatos de servidores hackeados apareceram nas listas de discussão, e crackers de senha de força bruta para hashes md5 SIP estão disponíveis para script kiddies. Fraudes de telecomunicações custam milhares de dólares para consumidores e provedores. Exemplo:

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

## Configurando os dispositivos SIP

Após definir os telefones no arquivo de configuração do Asterisk, é hora de configurar o próprio telefone. Neste exemplo, mostraremos como configurar um softphone gratuito — o SipPulse Softphone (baixe-o em https://www.sippulse.com/produtos/softphone). Verifique o manual do seu dispositivo para entender os parâmetros do seu telefone. Passo 1: Configure o telefone para usar o ramal 6000. Execute o programa de instalação. Após a execução, abra as configurações de conta/SIP e adicione uma nova conta SIP. Preencha as informações necessárias.

![A tela de conta do SipPulse Softphone — insira o Servidor (seu IP ou domínio do Asterisk), Nome de Usuário, Senha e Nome de Exibição, depois escolha o Transporte (UDP, TCP ou TLS).](../images/softphone/sipphone-account.png){width=35%}

Nome de Exibição: 6000 Nome de Usuário: 6000 Senha: #MySecret1#7 Nome de Usuário de Autorização: 6000 Domínio: ip_do_seu_servidor. Confirme se o seu telefone está registrado usando o comando de console `pjsip show endpoints` (ou `pjsip show endpoint 6000` para detalhes; `pjsip show contacts` mostra os contatos AOR registrados). Repita a configuração para o telefone 6001.

![Um SipPulse Softphone registrado — o ponto verde e a linha da conta (`1001@softphone.sippulse.com.br`) confirmam o registro; faça uma chamada pelo teclado ou pelos botões de chamada/vídeo.](../images/softphone/sipphone-registered.png){width=35%}

## Configurando os dispositivos IAX

IAX2 é um protocolo legado (veja o capítulo *Legacy channels*), e o SipPulse Softphone é apenas SIP, portanto, ele não pode registrar uma conta IAX. Se você precisar testar o IAX2, use um softphone que ainda o suporte. Crie uma nova conta IAX,

3. Selecione nova conta IAX. 4. Insira as opções relacionadas para o telefone 6003 e, opcionalmente, para o 6004. 5. Salve a configuração e verifique se o telefone está registrado usando iax2 show peers. Importante: Use uma conta para SIP e outra para IAX. Se você quiser configurar o sistema para tocar tanto IAX quanto SIP ao mesmo tempo, mostraremos como fazer isso na seção de dialplan.

### Configurando uma interface PSTN

Para conectar à PSTN, você precisará de uma interface FXO (foreign exchange office) e uma linha telefônica. Você também pode usar um ramal de PBX existente. Você pode obter uma placa de interface de telefonia com uma interface FXO de vários fabricantes. Neste exemplo, mostraremos como instalar uma placa de interface DAHDI.

![Portas FXS e FXO: a porta FXS controla um telefone analógico (fornece tom de discagem e toque), enquanto a porta FXO conecta o Asterisk à linha da operadora.](../images/04-first-pbx-fig02.png)

### Linhas analógicas usando DAHDI

Você pode comprar uma placa analógica compatível com DAHDI de vários fabricantes. A X100P foi uma das primeiras placas Digium e já foi descontinuada. Alguns fabricantes ainda produzem clones semelhantes. Além do preço da X100P, encontramos vários problemas entre essas placas e novas placas-mãe, então use-a com cuidado. A X100P, na minha opinião, não é uma boa escolha para um ambiente de produção. Qualquer placa compatível com DAHDI deve funcionar. Graças à equipe de desenvolvedores do DAHDI, agora temos uma ferramenta para detectar e configurar as placas de interface quase automaticamente. Se você acabou de instalar os drivers DAHDI, não se esqueça de executar make config e reiniciar a máquina para carregá-lo automaticamente. Você pode usar os comandos abaixo para detectar e configurar sua placa. Passo 1: Para detectar seu hardware, use:

```
dahdi_hardware.
```

Passo 2: Para configurar, use:

```
dahdi_genconf.
```

O comando acima gerará dois arquivos /etc/dahdi/system.conf e /etc/asterisk/dahdi-channels.conf. Os parâmetros padrão para dahdi_genconf geralmente são bons, mas você pode alterá-los no arquivo /etc/dahdi/genconf_parameters. Por padrão, ele inserirá as linhas (FXO) no contexto from-pstn e os telefones (FXS) no contexto from-internal. Passo 3: Após executar dahdi_genconf, na última linha do arquivo /etc/asterisk/chan_dahdi.conf, insira a seguinte linha:

```
#include dahdi-channels.conf
```

Passo 4: Edite o arquivo /etc/dahdi/modules e comente todos os drivers não utilizados. Reinicie antes de prosseguir e verifique se os canais estão sendo reconhecidos usando:

```
CLI>dahdi show channels
```

### Conectando à PSTN usando um provedor VoIP

Se o seu orçamento for realmente limitado, você pode configurar um tronco SIP para conectar à PSTN. É certamente a maneira mais acessível de se conectar à PSTN. Existem milhares de provedores VoIP em todo o mundo. Para se conectar a um deles, você precisará de alguns parâmetros. Parâmetros fornecidos pelo provedor SIP.

- username: login
- password: secret
- Domínio do provedor: domain
- Porta UDP: 5060
- Codecs permitidos: g729, ilbc, alaw

Dois parâmetros devem ser determinados por você.

- Ramal para receber chamadas — neste caso: 9999
- context: from-sip

No PJSIP, um tronco SIP de registro é construído a partir da mesma família de objetos usada para um endpoint, mais objetos explícitos `registration` e `identify`. O objeto `registration` diz ao Asterisk para se registrar no provedor, o objeto `identify` corresponde ao tráfego de entrada do IP do provedor ao endpoint (o PJSIP autentica INVITEs de entrada pelo IP de origem), e `outbound_auth` fornece as credenciais para chamadas de saída e registro:

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

Para acessar este tronco, usaremos o nome de canal `PJSIP/siptrunk`. A configuração `dtmf_mode=rfc4733` transporta DTMF fora de banda (RFC 4733 torna obsoleta a RFC 2833 mais antiga; o payload é idêntico). A opção `identify`/`match` aceita endereços IP, CIDRs ou nomes de host, mas nomes de host são resolvidos uma vez no momento do carregamento da configuração, portanto, para um provedor com IPs variáveis, liste o(s) IP(s) de sinalização explicitamente. Confirme o registro com `pjsip show registrations`.

## Introdução ao dialplan

O dialplan é como o coração do Asterisk. Ele define como o Asterisk lida com cada chamada para o PBX. Consiste em ramais que criam uma lista de instruções para o Asterisk seguir. As instruções são disparadas por dígitos recebidos do canal ou aplicação. Para configurar o Asterisk com sucesso, é crucial entender o dialplan. A maior parte do dialplan está contida no arquivo extensions.conf no diretório /etc/asterisk. Este arquivo usa a gramática de grupo simples e possui quatro conceitos principais:

- Ramais (Extensions)
- Prioridades
- Aplicações
- Contextos

Vamos criar um dialplan básico. Nas seções subsequentes deste livro, dedicarei um capítulo exclusivamente ao dialplan. Se você instalou os arquivos de exemplo (make samples), o extensions.conf já existe. Salve-o com outro nome e comece com um arquivo em branco.

## A estrutura do arquivo extensions.conf

O arquivo extensions.conf é separado em seções. A primeira é a seção [general] seguida pela seção [globals]. O início de cada seção começa com a definição do seu nome (ou seja, [default]) e termina quando outra seção é criada.

### A seção [general]

A seção general fica no topo do arquivo. Antes de começar a configurar o dialplan, é útil conhecer as opções gerais que controlam certos comportamentos do dialplan. Essas opções são:

- static e write protect: Se static=yes e writeprotect=no, você pode usar a CLI

```
command save dialplan.
```

Aviso: Se você emitir um comando save dialplan da CLI, você acabará perdendo quaisquer observações e comentários no arquivo.

- autofallthrough: Se autofallthrough estiver definido, então, se um ramal ficar sem coisas para fazer, ele encerrará a chamada com BUSY, CONGESTION ou HANGUP, dependendo da melhor estimativa do Asterisk. Este é o padrão. Se autofallthrough não estiver definido, então, se um ramal ficar sem coisas para fazer, o Asterisk aguardará um novo ramal ser discado.
- clearglobalvars: Se clearglobalvars estiver definido, as variáveis globais serão limpas e reanalisadas em um dialplan reload ou Asterisk reload. Se clearglobalvars não estiver definido, as variáveis globais persistirão através de recarregamentos e — mesmo se excluídas do extensions.conf ou de um de seus arquivos incluídos — elas permanecerão definidas com o valor anterior.
- extenpatternmatchnew: Usa um algoritmo de correspondência de padrão mais rápido, o que ajuda visivelmente quando você tem um grande número de ramais. O padrão é no.
- userscontext: Este é o contexto onde as entradas do users.conf são registradas.

### A seção [globals]

Na seção [globals], você definirá variáveis globais e seus valores iniciais. Você pode acessar a variável no dialplan usando ${GLOBAL(variable)}. Você pode até acessar variáveis definidas no ambiente linux/unix usando ${ENV(variable)}. Variáveis globais não diferenciam maiúsculas de minúsculas. Alguns exemplos poderiam ser:

```
INCOMING>DAHDI/8&DAHDI/9
RINGTIME=>3
```

No exemplo a seguir, você pode definir e testar uma variável global no dialplan.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contextos

Contexto é a partição nomeada do dialplan. Após as seções [general] e [globals], o dialplan é um conjunto de contextos nos quais cada contexto possui vários ramais, cada ramal possui várias prioridades e cada prioridade chama uma aplicação com vários argumentos.

![Fluxo de chamada do Asterisk: cada chamada chega em um canal (IAX, SIP e outros) como uma perna de chamada de entrada; o contexto do canal — definido globalmente ou por canal no arquivo de configuração do canal — decide qual contexto no extensions.conf processa a chamada antes que ela saia na perna de saída.](../images/04-first-pbx-fig03.png)

![Processamento de chamada: o `context=` definido para um canal (em chan_dahdi.conf ou pjsip.conf) nomeia o contexto correspondente no extensions.conf onde o dialplan lida com a chamada.](../images/04-first-pbx-fig04.png)

Você pode construir um dialplan simples para alcançar outros telefones e a PSTN. No entanto, o Asterisk é muito mais poderoso do que isso. Nosso objetivo é ensinar mais detalhes sobre o que é possível no dialplan.

## Ramais (Extensions)

Ao contrário do PBX tradicional, onde os ramais estão associados a telefones, interfaces, menus e assim por diante, no Asterisk um ramal é uma lista de comandos a serem processados quando um número ou nome de ramal específico é acionado. Os comandos são processados em ordem de prioridade.

![Sintaxe de ramal: `exten => number(name),{priority|label}[(alias)],application`. Ramais podem ser numéricos, alfanuméricos, numéricos com identificador de chamadas, um padrão ou um ramal padrão como `s`; prioridades podem ser um número, `n` (próximo), `s` (mesmo), um deslocamento ou um `hint`.](../images/04-first-pbx-fig05.png)

Um ramal pode ser literal, padrão ou especial. Um ramal padrão inclui apenas números ou nomes e os caracteres * e #; 12#89* é um ramal literal válido. Nomes também podem ser usados para correspondência de ramais. Ramais diferenciam maiúsculas de minúsculas. No entanto, você não pode criar dois ramais com o mesmo nome, mas com casos diferentes. Quando um ramal é discado, o comando com a primeira prioridade é executado, seguido pelo comando com a prioridade 2 e assim por diante. Isso acontece até que a chamada seja desconectada ou algum comando retorne o número um, indicando falha. O que o Asterisk faz quando a última prioridade é executada é regulado pelo parâmetro autofallthrough. Veja a seção [general] neste capítulo. Exemplo:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Acima, você encontra a lista de instruções a serem processadas quando o ramal 123 é discado. A primeira prioridade é atender o canal (necessário quando o canal está no estado de toque: ou seja, canais FXO). A segunda prioridade é reproduzir um arquivo de áudio chamado tt-weasels. A terceira prioridade desliga o canal. Outra opção é lidar com a chamada de acordo com o identificador de chamadas (Caller ID). Você pode usar o caractere / para especificar o identificador de chamadas a ser processado. Exemplos:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Este exemplo acionará o ramal 123 e executará as seguintes opções apenas se o identificador de chamadas for 100. Isso também pode ser feito usando o padrão descrito abaixo:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: mapeia um ramal para um canal. É usado para monitorar o estado do canal. É usado em conjunto com a presença. O telefone deve suportar isso.

#### Padrões

Você pode usar padrões e literais no dialplan. Padrões são muito úteis para reduzir o tamanho do dialplan. Todos os padrões começam com o caractere “_”. Os seguintes caracteres podem ser usados para definir um padrão. A figura identifica os padrões disponíveis para uso com o Asterisk.

![Caracteres de correspondência de padrão: `_` inicia um padrão, `.` corresponde a um ou mais caracteres, `!` corresponde a zero ou mais, `[123-7]` corresponde a qualquer dígito ou intervalo listado, `X` é 0-9, `Z` é 1-9 e `N` é 2-9 — com exemplos mapeando intervalos de ramais de escritório.](../images/04-first-pbx-fig06.png)

### Ramais especiais

O Asterisk usa alguns nomes de ramais como ramais padrão.

![Ramais especiais do Asterisk: `i` (inválido), `s` (início), `h` (desligar), `t` (tempo limite), `T` (tempo limite absoluto), `o` (operadora), `a` (pressionado `*` no correio de voz), `fax` (detecção de fax) e `Talk` (usado com BackgroundDetect).](../images/04-first-pbx-fig07.png)

Descrição: s: Início. É usado para lidar com uma chamada quando não há número discado. É útil para troncos FXO e processamento de menu. t: Tempo limite. É usado quando as chamadas permanecem inativas após um prompt ter sido reproduzido. Também é usado para desligar uma linha inativa. T: AbsoluteTimeout. Se você estabelecer um limite de chamada usando a função de dialplan `TIMEOUT(absolute)`, uma vez que a chamada exceda o limite definido, ela será enviada para o ramal T. h: Hangup. É chamado após o usuário desconectar a chamada. i: Inválido. É acionado quando você chama um ramal inexistente no contexto. O uso desses ramais pode afetar o conteúdo dos registros CDR — especificamente, o dst que não contém o número discado. o: Operadora. É usado para ir para a operadora quando o usuário pressiona “0” durante o correio de voz. O uso desses ramais pode alterar o conteúdo dos registros de faturamento (CDR) — em particular, o campo dst não terá o número discado. Para contornar esse problema, você deve usar a opção g na aplicação dial() e considerar as funções resetcdr(w) e/ou nocdr()

## Variáveis

No PBX Asterisk, as variáveis podem ser globais, específicas do canal e específicas do ambiente. Você pode usar a aplicação NoOP() para ver o conteúdo de uma variável no console. Ela pode usar uma variável global ou uma variável específica do canal como argumentos de aplicações. Uma variável pode ser referenciada como no exemplo a seguir, onde varname é o nome da variável.

```
${varname}
```

Um nome de variável pode ser uma string alfanumérica começando com uma letra. Nomes de variáveis globais não diferenciam maiúsculas de minúsculas. No entanto, variáveis de sistema (definidas pelo Asterisk são definidas pelo canal) diferenciam maiúsculas de minúsculas. Assim, a variável ${EXTEN} é diferente de ${exten}.

### Variáveis globais

Variáveis globais podem ser configuradas na seção [global] no arquivo extensions.conf ou usando a aplicação:

```
set(Global(variable)=content)
```

### Variáveis específicas do canal

Variáveis específicas do canal são configuradas usando a aplicação set(). Cada canal recebe seu próprio espaço de variável. Não há chance de colisões entre variáveis de diferentes canais. Uma variável específica do canal é destruída quando o canal é desligado. Algumas das variáveis mais usadas são:

- ${EXTEN} Ramal discado
- ${CONTEXT} Contexto atual
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} Identificador de chamadas atual
- ${PRIORITY} Prioridade atual

Outras variáveis específicas do canal estão todas em maiúsculas. Você pode ver o conteúdo de várias variáveis usando a aplicação dumpchan(). Abaixo está um pequeno trecho de variáveis de dump-channel.

```
exten=9001,1,dumnpchan()
exten=9001,n,echo()
exten=9001,n,hangup()
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

O layout de campo acima é a saída do Asterisk 22 `DumpChan` (um nome de canal `PJSIP/...` real, os campos `CallerIDNum`/`ConnectedLineID` e as linhas `Raw*`/`Transcode`/`BridgeID` que os canais PJSIP preenchem). Ao contrário do driver antigo, um canal PJSIP não define automaticamente variáveis de canal `SIPCALLID`/`SIPUSERAGENT`; os detalhes SIP equivalentes são lidos sob demanda com as funções de dialplan `PJSIP_HEADER()` e `CHANNEL()` — por exemplo, `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` e `${CHANNEL(rtp,dest)}` para o endereço RTP remoto.

### Variáveis específicas do ambiente

Variáveis específicas do ambiente podem ser usadas para acessar variáveis definidas no sistema operacional. Você pode definir variáveis específicas do ambiente usando a função ENV(). Por exemplo:

```
${ENV(LANG)}
Set(ENV(LANG))=en_US
```

### Variáveis específicas da aplicação

Algumas aplicações usam variáveis para entrada e saída de dados. Você pode definir variáveis antes de chamar a aplicação ou recuperar a variável após a execução da aplicação. Por exemplo: A aplicação Dial retorna as seguintes variáveis:

- ${DIALEDTIME} -> Este é o tempo desde a discagem de um canal até ele ser desconectado.
- ${ANSWEREDTIME} -> Esta é a quantidade de tempo para a chamada real.
- ${DIALSTATUS} Este é o status da chamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Mensagem de erro para a chamada.

## Expressões

Expressões podem ser muito úteis no dialplan. Elas são usadas para manipular strings e realizar operações matemáticas e lógicas.

![Visão geral das expressões do Asterisk — `$[expression1 operator expression2]` — agrupando os operadores matemáticos, lógicos, de comparação, de expressão regular e condicionais disponíveis no dialplan.](../images/04-first-pbx-fig08.png)

A sintaxe da expressão é definida da seguinte forma:

```
$[expression1 operator expression2]
```

Vamos supor que temos uma variável chamada “I” e queremos adicionar 100 à variável:

```
$[${I}+100]
```

Quando o Asterisk encontra uma expressão no dialplan, ele altera a expressão inteira pelo valor resultante.

### Operadores

Os seguintes operadores podem ser usados para construir expressões. É importante observar a precedência dos operadores. 1. Parênteses “()” 2. Operadores unários “! -“ 3. Expressão regular “: =~ 4. Operadores multiplicativos “* / %” 5. Operadores aditivos “+ -“ 6. Operadores de comparação 7. Operadores lógicos 8. Operadores condicionais

#### Operadores Matemáticos

- Adição (+)
- Subtração (-)
- Multiplicação (*)
- Divisão (/)
- Módulo (%)

#### Operadores Lógicos

- Lógico “AND” (&)
- Lógico “OR” (|)
- Complemento Unário Lógico (!)

#### Operadores de expressão regular

- Correspondência de expressão regular (:)
- Correspondência exata de expressão regular (=~)

Uma expressão regular é uma string de texto especial usada para descrever um padrão de pesquisa. Você pode pensar em expressões regulares como curingas. Expressões regulares são usadas para corresponder uma string a um padrão para verificar a correspondência. Se a correspondência for bem-sucedida e a expressão regular contiver pelo menos uma correspondência, a primeira correspondência será retornada; caso contrário, o resultado é o número de caracteres correspondidos.

#### Operadores de comparação

O resultado de uma comparação é 1 se a relação for verdadeira ou 0 se for falsa.

- = igual
- != não igual
- < menor que
- > maior que
- <= menor ou igual a
- >= maior ou igual a

### LAB. Avalie as seguintes expressões:

Coloque essas expressões no seu dialplan e use a aplicação NoOP() para avaliar as expressões. Disque 9002 e examine os resultados no console do Asterisk. Use verbose 15 para mostrar os resultados.

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

## Funções

Algumas aplicações foram substituídas por funções, que permitem o processamento de variáveis de uma forma mais avançada do que apenas expressões. Você pode ver a lista completa de funções emitindo o seguinte comando de console:

```
CLI>core show functions
```

Comprimento da string: ${LEN(string)} retorna o comprimento da string

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

Na primeira operação, o sistema mostra 5 como resultado (o número de letras na palavra “fruit”). A segunda retorna o número 4 (o número de letras na palavra “pear”). Substrings: Retorna a substring, começando da posição definida pelo parâmetro “offset”, com o comprimento da string definido no parâmetro “length”. Se o offset for negativo, ele começa da direita para a esquerda, começando no final da string. Se o comprimento for omitido ou negativo, ele pega a string inteira começando com o offset.

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

Exemplo #3: Pega todos os dígitos da variável ${EXTEN}, exceto o código de área.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Concatenação de strings

Para concatenar duas strings, simplesmente escreva-as juntas.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Aplicações

Para construir um dialplan, precisamos entender o conceito de aplicações. Você usará aplicações para lidar com o canal no dialplan. As aplicações são implementadas em vários módulos. As aplicações disponíveis dependem dos módulos. Você pode mostrar todas as aplicações do Asterisk usando o comando de console:

```
CLI>core show applications
```

Alternativamente, você pode mostrar detalhes de uma aplicação específica usando o seguinte exemplo:

```
CLI>core show application dial
```

Para construir um dialplan simples, você precisa conhecer algumas aplicações. Discutiremos exemplos mais avançados mais adiante no livro.

![O punhado de aplicações necessárias para construir um dialplan simples: Answer (atender um canal), Dial (chamar outro canal), Hangup (desligar um canal), Playback (reproduzir um arquivo de áudio) e Goto (pular para uma prioridade, ramal ou contexto).](../images/04-first-pbx-fig09.png)

Usaremos essas aplicações (acima) para criar um dialplan simples para dois PBXs básicos.

### Answer()

[Sinopse] Atende um canal se estiver tocando [Descrição] Answer([delay]): Se a chamada não tiver sido atendida, a aplicação a atenderá. Caso contrário, não tem efeito na chamada. Se um atraso for especificado, o Asterisk aguardará o número de milissegundos especificado em ‘delay’ antes de atender a chamada.

### Dial()

A descrição a seguir pode ser obtida emitindo show application dial no dialplan. Para facilitar a pesquisa, ela é reproduzida abaixo. A sintaxe para a aplicação Dial também é mostrada abaixo:

```
;dial to a single channel
Dial(type/identifier,timeout,options, URL)
;Dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...][|timeout][|options][|URL]):
```

Esta aplicação fará chamadas para um ou mais canais especificados. Assim que um dos canais solicitados atender, o canal de origem será atendido — se ainda não tiver sido atendido. Esses dois canais estarão então ativos em uma chamada em ponte. Todos os outros canais solicitados serão então desligados. A menos que um tempo limite seja especificado, a aplicação Dial aguardará indefinidamente até que um dos canais chamados atenda, o usuário desligue ou todos os canais chamados estejam ocupados ou indisponíveis. A execução do dialplan continuará se nenhum canal solicitado puder ser chamado ou se o tempo limite expirar. Esta aplicação define as seguintes variáveis de canal após a conclusão:

- DIALEDTIME - Este é o tempo desde a discagem de um canal até o momento em que ele é desconectado.
- ANSWEREDTIME - Esta é a quantidade de tempo para uma chamada real.
- DIALSTATUS - Este é o status da chamada: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

Para os Modos de Privacidade e Triagem, a variável DIALSTATUS será definida como DONTCALL se a parte chamada optar por enviar a parte chamadora para o script 'Go Away'. A variável DIALSTATUS será definida como TORTURE se a parte chamada quiser enviar o chamador para o script 'torture'. Esta aplicação relatará o encerramento normal se o canal de origem desligar ou se a chamada for colocada em ponte e qualquer uma das partes na ponte encerrar a chamada. A URL opcional será enviada para a parte chamada se o canal a suportar. Se a variável OUTBOUND_GROUP estiver definida, todos os canais peer criados por esta aplicação serão incluídos nesse grupo (como em

```
Set(GROUP()=...).
```

A tabela a seguir resume algumas das opções usadas com mais frequência para a aplicação Dial. Para a lista completa, use o comando de console `core show application Dial`. No Asterisk 22, essas opções são separadas do canal e do tempo limite por vírgulas — por exemplo, `Dial(PJSIP/2000,20,tTm)`.

| Opção | Descrição |
|--------|-------------|
| `A(x)` | Reproduz um anúncio para a parte chamada, usando `x` como o arquivo. |
| `C` | Redefine o CDR para esta chamada. |
| `d` | Permite que o usuário chamador disque um ramal de 1 dígito enquanto aguarda a chamada ser atendida. Sai para esse ramal se ele existir no contexto atual, ou para o contexto definido na variável `EXITCONTEXT`, se existir. |
| `D([called][:calling])` | Envia as strings DTMF especificadas após a parte chamada atender, mas antes da chamada ser colocada em ponte. A string `called` é enviada para a parte chamada e a string `calling` para a parte chamadora. Qualquer parâmetro pode ser usado sozinho. |
| `f` | Força o identificador de chamadas do canal chamador a ser definido como o ramal associado ao canal via um `hint` de dialplan. Útil onde a PSTN não permite um identificador de chamadas arbitrário. |
| `g` | Prossegue com a execução do dialplan no ramal atual se o canal de destino desligar. |
| `G(context^exten^pri)` | Se a chamada for atendida, transfere a parte chamadora para a prioridade especificada e a parte chamada para prioridade+1. Opcionalmente, um ramal (ou ramal e contexto) pode ser especificado; caso contrário, o ramal atual é usado. |
| `h` | Permite que a parte chamada desligue enviando o dígito DTMF `*`. |
| `H` | Permite que a parte chamadora desligue enviando o dígito DTMF `*`. |
| `L(x[:y][:z])` | Limita a chamada a `x` ms, reproduz um aviso quando restarem `y` ms e repete o aviso a cada `z` ms. Veja as variáveis `LIMIT_*` abaixo. |
| `m([class])` | Fornece música de espera para a parte chamadora até que o canal solicitado atenda. Uma classe MusicOnHold específica pode ser especificada. |
| `r` | Indica toque para a parte chamadora e não passa áudio até que o canal chamado atenda. |
| `S(x)` | Desliga a chamada `x` segundos após a parte chamada atender. |
| `t` | Permite que a parte chamada transfira a parte chamadora enviando a sequência DTMF definida em `features.conf`. |
| `T` | Permite que a parte chamadora transfira a parte chamada enviando a sequência DTMF definida em `features.conf`. |
| `w` | Permite que a parte chamada habilite a gravação com um toque enviando a sequência DTMF definida em `features.conf`. |
| `W` | Permite que a parte chamadora habilite a gravação com um toque enviando a sequência DTMF definida em `features.conf`. |
| `k` | Permite que a parte chamada estacione a chamada enviando a sequência DTMF definida para estacionamento de chamadas em `features.conf`. |
| `K` | Permite que a parte chamadora estacione a chamada enviando a sequência DTMF definida para estacionamento de chamadas em `features.conf`. |

A opção `L(x[:y][:z])` pode ser ajustada com as seguintes variáveis especiais:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (padrão `yes`): reproduz sons para o chamador.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: reproduz sons para a parte chamada.
- `LIMIT_TIMEOUT_FILE` — arquivo a ser reproduzido quando o tempo acabar.
- `LIMIT_CONNECT_FILE` — arquivo a ser reproduzido quando a chamada começar.
- `LIMIT_WARNING_FILE` — arquivo a ser reproduzido como um aviso quando `y` é definido. O padrão é dizer o tempo restante.

Exemplo:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

No exemplo acima, a aplicação discará para o canal PJSIP correspondente. Tanto o chamador quanto o chamado poderiam transferir a chamada (Tt). Música de espera será ouvida em vez do toque de retorno. Se ninguém atender dentro de 20 segundos, o ramal irá para a próxima prioridade.

### Hangup()

Desliga o canal chamador [Descrição] Hangup([causecode]): Esta aplicação desligará o canal chamador. Se um código de causa for fornecido, a causa de desligamento do canal será definida com o valor fornecido.

### Goto()

Pular para uma prioridade, ramal ou contexto específico [Descrição] Goto([[context|]extension|]priority): Esta aplicação fará com que o canal chamador continue a execução do dialplan na prioridade especificada. Se nenhum ramal específico (ou ramal e contexto) for especificado, esta aplicação pulará para a prioridade especificada do ramal atual. Se a tentativa de pular para outro local no dialplan não for bem-sucedida, o canal continuará na próxima prioridade do ramal atual.

## Construindo um dialplan

Para construir um dialplan simples, você precisa tratar todas as chamadas de entrada e saída criando contextos e ramais. Nesta seção, mostraremos como construir os ramais mais comuns.

### Discagem entre ramais

Para permitir a discagem entre ramais, poderíamos usar a variável de canal ${EXTEN}, que se refere ao ramal discado. Por exemplo, se o intervalo de ramais estiver entre 4000 e 4999 e todos os ramais usarem SIP, poderíamos adotar o seguinte comando:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Discagem para um destino externo

Para discar para um destino externo, você pode preceder o número discado com uma rota. Na América do Norte, é comum usar 9 seguido pelo número a ser discado externamente. Se você estiver usando um canal analógico ou digital para a PSTN, o comando deve ser semelhante ao seguinte: Se você quiser usar o tronco SIP em vez do DAHDI, use o canal `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

A linha acima permitirá que você disque 9 e o número desejado. No exemplo dado, você usará o primeiro canal DAHDI (DAHDI/1). Se você tiver várias linhas e esta estiver ocupada, a chamada não será completada. No entanto, você poderia usar a seguinte linha para escolher automaticamente o primeiro canal DAHDI disponível. Opcionalmente, você pode usar o tronco SIP em vez do DAHDI. Na forma PJSIP `Dial(PJSIP/number@siptrunk,...)`, o número discado é a parte do usuário e `siptrunk` é o endpoint configurado acima.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

O parâmetro “g1” procurará o primeiro canal disponível no grupo, permitindo o uso de todos os canais. Usando a linha abaixo, você poderia discar um número de longa distância.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Discando 9 para obter uma linha PSTN

Se você não tiver nenhuma restrição para discagem externa, você pode simplificar e usar o seguinte:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Recebendo uma chamada no ramal da operadora

No exemplo a seguir, o ramal da operadora é 4000. A linha PSTN está conectada a uma interface FXO. No arquivo chan_dahdi.conf, o contexto especificado é from-pstn. Qualquer chamada vinda da PSTN será roteada para o contexto from-pstn no dialplan. Esta linha não possui discagem direta interna (DID); como tal, teremos que receber a chamada via ramal “s”. Se estiver recebendo do tronco SIP, use o contexto [from-sip].

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

Se você tiver uma linha digital, receberá o ramal discado. Quando este for o caso, você não precisa encaminhar a chamada para a operadora; em vez disso, você pode encaminhar a chamada diretamente para o destino. Suponha que seu intervalo DID seja de 3028550 a 3028599 e os últimos quatro números sejam passados no DID. A configuração seria semelhante ao exemplo a seguir:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Reproduzindo vários ramais simultaneamente

Você pode configurar o Asterisk para discar para um ramal e, se não for atendido, discar para vários outros ramais simultaneamente, conforme indicado no exemplo a seguir:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

Neste exemplo, quando alguém disca para a operadora, o canal DAHDI/1 é tentado inicialmente. Se ninguém atender após 15 segundos (tempo limite), os canais DAHDI/1, DAHDI/2 e DAHDI/3 tocarão simultaneamente por mais 15 segundos.

### Roteamento por identificador de chamadas (Caller ID)

Neste exemplo, você pode dar tratamentos diferentes com base no identificador de chamadas, o que pode ser útil para spammers de chamadas. Por exemplo:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

Neste exemplo, adicionamos uma regra especial que, se o identificador de chamadas for 4832518888, você reproduz uma mensagem do arquivo gravado anteriormente “I-have-moved-to-china”. Outras chamadas são aceitas como de costume.

### Usando variáveis no dialplan

O Asterisk pode usar variáveis globais e de canal no dialplan como argumentos para certas aplicações. Veja os exemplos a seguir:

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

Usar variáveis torna as mudanças futuras mais fáceis. Se você alterar a variável, todas as referências são alteradas imediatamente.

### Gravando um anúncio

Em algumas das opções discutidas mais adiante nesta seção, usaremos prompts gravados. Aqui mostramos uma maneira fácil de gravá-los. Usaremos a aplicação Record() para salvar o anúncio usando o próprio telefone.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Estas instruções permitem que você grave qualquer mensagem de um softphone. Exemplo: discando recordmenu do softphone As instruções chamarão a gravação com a variável ${EXTEN:6} sem as seis primeiras letras. Em outras palavras, a instrução é equivalente a record(menu:gsm). Tudo o que você precisa fazer é discar record + nome_do_arquivo_a_ser_gravado, pressionar # para finalizar a gravação e esperar para ouvir a gravação.

### Recebendo as chamadas em uma recepcionista digital

Agora que temos alguns exemplos simples, vamos expandir nosso aprendizado sobre as aplicações background() e goto(). A chave para sistemas interativos no Asterisk é a aplicação background(), que permite executar um arquivo de áudio que, quando o chamador pressiona uma tecla, é interrompido para enviar a chamada para o ramal discado. Sintaxe da aplicação background():

```
exten=>extension, priority, background(filename)
```

Outra aplicação muito útil é goto(). Como o nome sugere, ela pula para o contexto, ramal e prioridade indicados. Sintaxe da aplicação goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Formatos válidos para o comando goto():

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

No exemplo a seguir, criaremos uma recepcionista digital. É muito simples editar o arquivo extensions.conf e configurar os seguintes ramais:

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

Os ramais SIP usam `PJSIP/` e os ramais IAX usam `IAX2/` — ambos os drivers são fornecidos no Asterisk 22, embora `chan_iax2` seja agora considerado legado e SIP/PJSIP seja preferido.

No arquivo menu1.gsm, grave a mensagem “pressione o ramal ou aguarde a operadora”. Quando o usuário discar o número 6000, ele será enviado para o ramal 6000. Neste ponto, você deve ter uma compreensão clara do uso de várias aplicações, incluindo answer(), background(), goto(), hangup() e playback(). Se você não tiver uma compreensão clara, por favor, leia este capítulo novamente até se sentir confortável com o conteúdo. Você usará a aplicação background com muita frequência. Uma vez que você entenda o básico de ramais, prioridades e aplicações, será fácil criar um dialplan simples. Esses conceitos serão explorados com mais profundidade mais adiante no livro, e você verá que o dialplan se tornará mais poderoso.

## Resumo

Neste capítulo, você aprendeu que os arquivos de configuração são armazenados no diretório /etc/asterisk. Para usar o Asterisk, é primeiro necessário configurar os canais (por exemplo, pjsip, dahdi, iax). Existem três gramáticas diferentes para arquivos de configuração: grupo simples, herança de objeto e entidade complexa. O dialplan é criado no arquivo extensions.conf e é um conjunto de contextos e ramais. No dialplan, cada ramal aciona uma aplicação. Você aprendeu a usar as aplicações playback, background, dial, goto, hangup e answer.

## Quiz

1. Os arquivos de configuração de canal são (escolha todos os que se aplicam):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. No Asterisk 22, o único peer `chan_sip` `[6001]` (`type=friend`/`host=dynamic`) é substituído no `pjsip.conf` por qual conjunto de objetos relacionados?
   - A. Um `type=peer` e um `type=user`
   - B. Um `type=endpoint`, um `type=auth` e um `type=aor`
   - C. Um único `type=friend`
   - D. Um `type=transport` e um `type=global`
3. Definir um contexto no arquivo de configuração do canal é importante porque define o contexto de entrada para chamadas desse canal — uma chamada do canal é processada no contexto correspondente em `extensions.conf`.
   - A. Verdadeiro
   - B. Falso
4. As principais diferenças entre as aplicações `Playback()` e `Background()` são (escolha duas):
   - A. Playback reproduz um prompt, mas não aguarda dígitos.
   - B. Background reproduz um prompt, mas não aguarda dígitos.
   - C. Background reproduz uma mensagem e aguarda que dígitos sejam pressionados.
   - D. Playback reproduz uma mensagem e aguarda que dígitos sejam pressionados.
5. Quando uma chamada entra no Asterisk através de uma placa de interface de telefonia (FXO) sem DID, ela é tratada no ramal especial:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Formatos válidos para a aplicação `Goto()` são (escolha três):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. O padrão `_7[1-5]XX` corresponde a (escolha todos os que se aplicam):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. Em `Dial(PJSIP/${EXTEN},20,tTm)`, o que a opção `m` faz?
   - A. Limita a chamada a uma duração máxima.
   - B. Fornece música de espera ao chamador em vez do toque de retorno até que o canal atenda.
   - C. Envia dígitos DTMF após a parte chamada atender.
   - D. Força o identificador de chamadas usando uma dica de dialplan.
9. Na gramática de herança de opções usada por `chan_dahdi.conf`, você:
   - A. Define o objeto em uma única linha.
   - B. Define as opções primeiro e declara os objetos abaixo das opções definidas.
   - C. Define um contexto separado para cada objeto.
10. As prioridades em um ramal devem ser numeradas consecutivamente (1, 2, 3, …) e não podem usar `n`.
    - A. Verdadeiro
    - B. Falso

**Respostas:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
