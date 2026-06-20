# SIP e PJSIP em profundidade

SIP é o protocolo; PJSIP é como o Asterisk 22 o utiliza. **PJSIP** (`chan_pjsip`, configurado via `pjsip.conf`) é o único driver de canal SIP no Asterisk 22 LTS. Este capítulo cobre os fundamentos do protocolo SIP (que são de nível de protocolo e permanecem 100 % válidos) e o modelo de objetos e a configuração do PJSIP que você usa diariamente. O driver legado aposentado e um guia de migração são abordados no capítulo *Legacy channels*.

## Objectives

Ao final deste capítulo, você deverá ser capaz de:

- Explicar o papel dos agentes de usuário SIP, proxies, registrador e gateways;
- Seguir um fluxo básico de chamada SIP (REGISTER, INVITE, respostas provisórias e finais, ACK, BYE) e ler uma mensagem SIP;
- Descrever como o SDP negocia a sessão de mídia e como o NAT afeta o sinalização SIP e o RTP;
- Mapear o modelo de objetos PJSIP — `endpoint`, `auth`, `aor`, `transport`, `identify`, e `registration` — e como os objetos referenciam uns aos outros;
- Configurar telefones SIP e trunks em `pjsip.conf`, incluindo as opções de travessia NAT; e
- Verificar e solucionar problemas de endpoints com os comandos CLI `pjsip show …`.

## Fundamentos do protocolo SIP

Session Initiation Protocol (SIP) é um protocolo baseado em texto semelhante ao HTTP e SMTP, projetado para iniciar, manter e encerrar sessões de comunicação interativa entre usuários. Essas sessões podem incluir voz, vídeo, chat, jogos interativos e outros. O SIP foi definido pelo IETF e se tornou o padrão de fato para comunicações de voz. É muito importante entender como o SIP funciona. No Asterisk 22 a configuração SIP está em `pjsip.conf`, que é um dos arquivos mais frequentemente editados em um sistema baseado em SIP (logo após `extensions.conf`).

### Teoria de Operação

SIP é um protocolo de sinalização com os seguintes componentes: User Agent Client, User Agent Servers, SIP Proxies e SIP Gateways. A figura a seguir mostra os relacionamentos entre esses componentes.

- UAC (user agent client) – O cliente ou terminal que inicializa a sinalização SIP.  
- UAS (user agent server) – O servidor que responde a uma sinalização SIP proveniente de um UAC.  
- UA (user agent) – O terminal SIP (telefones ou gateways que contêm tanto UAC quanto UAS).  
- Proxy Server – Recebe solicitações de um UA e as transfere para outros Proxy SIP se a estação específica não estiver sob sua administração.  
- Redirect Server – Recebe solicitações e as devolve ao UA, incluindo dados de destino, ao invés de encaminhá‑las diretamente ao destino.  
- Location Server – Recebe solicitações de um UA e atualiza o banco de dados de localização com essas informações.

Usually, the proxy, redirect, and location servers are hosted within the same hardware and use the same piece of software, which we call the SIP proxy. The SIP proxy is responsible for location database maintenance, connection establishment, and session termination.

![Os principais componentes SIP: agentes de usuário (UAC/UAS/UA), o servidor registrar/proxy/redirect, e um gateway para a PSTN, com a mídia RTP fluindo diretamente entre os endpoints](../images/07-sip-and-pjsip-fig01.png)

#### Processo de Registro SIP

Antes que um telefone possa receber chamadas, ele precisa ser registrado em um banco de dados de localização. No banco de dados de localização, o endereço IP será vinculado ao nome. No exemplo a seguir, a extensão 8500 será vinculada ao endereço IP 200.180.1.1. Você não precisa necessariamente usar números de telefone. Na arquitetura SIP, a extensão registrada poderia ser flavio@voip.school também.

![Registro SIP: o telefone envia um REGISTER vinculando a extensão 8500 ao seu endereço IP, o registrador armazena o contato no banco de dados de localização e responde com 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### Operação de Proxy

When operating as a SIP proxy, the SIP server stays in the middle of the signaling and is capable of advanced routing and billing. The media flow, based on the real time protocol (RTP) still goes directly between the endpoints.

![Operação de proxy: o proxy SIP permanece no caminho de sinalização (INVITE/200 OK) e procura o destinatário no servidor de localização, enquanto a mídia RTP flui diretamente entre os dois endpoints](../images/07-sip-and-pjsip-fig03.png)

#### Operação de redirecionamento

Ao redirecionar, o servidor SIP simplesmente envia uma mensagem (e.g., 302 moved temporarily) para o agente de usuário e permanece fora do caminho das novas mensagens. É muito leve em termos de uso de recursos, mas você não tem nenhum controle. O redirecionamento às vezes é usado em designs de balanceamento de carga.

![Operação de redirecionamento: o servidor de redirecionamento responde ao INVITE com um 302 Moved Temporarily contendo o contato, então se retira enquanto o chamador reenvia o INVITE/ACK diretamente para o novo local](../images/07-sip-and-pjsip-fig04.png)

#### Como o Asterisk lida com SIP

É importante entender que o Asterisk não é nem um proxy SIP nem um redirecionador SIP. O Asterisk pode desempenhar o papel de registrador e servidor de localização; porém, ele apenas conecta dois UACs a si mesmo. Portanto, o Asterisk é considerado um back-to-back user agent (B2BUA). Em outras palavras, ele conecta dois canais SIP, interligando‑os. O Asterisk possui um mecanismo de re‑invite que pode fazer os canais SIP conversarem diretamente entre si, em vez de passarem pelo Asterisk. Em um endpoint PJSIP isso é controlado pelo parâmetro `direct_media`. Ao usar `direct_media=yes` o fluxo RTP vai diretamente de um endpoint para outro, liberando recursos do servidor.

#### Operação SIP com direct_media=yes

![Operação SIP com directmedia=yes: o sinal de SIP flui através do Asterisk enquanto o áudio RTP vai diretamente entre os dois telefones, liberando recursos do servidor](../images/07-sip-and-pjsip-fig05.png)

No entanto, se você precisar transferir ou gravar a chamada usando o Asterisk, pode usar o parâmetro `direct_media=no` para forçar o fluxo RTP através do servidor Asterisk.

#### Operação SIP com direct_media=no

![Operação SIP com directmedia=no: tanto o sinal de SIP quanto o áudio RTP são ancorados através do Asterisk, permitindo que ele grave, transcodifique ou transfira a chamada](../images/07-sip-and-pjsip-fig06.png)

#### Mensagens SIP

As mensagens SIP básicas são:

- INVITE – estabelecimento de conexão
- ACK – confirmação
- BYE – terminação da conexão
- CANCEL – terminação da conexão para uma chamada não estabelecida
- REGISTER – registrar um UAC em um proxy SIP
- OPTIONS – pode ser usado para verificar disponibilidade
- REFER – transferir uma chamada SIP para outra pessoa
- SUBSCRIBE – inscrever-se a eventos de notificação
- NOTIFY – enviar informações do canal
- INFO – enviar várias mensagens (ex., DTMF )
- MESSAGE – enviar mensagens instantâneas

As respostas SIP estão em formato de texto e são facilmente legíveis (semelhantes a mensagens HTTP). As respostas mais importantes são:

- 1XX – Mensagens de informação (100–trying, 180–ringing, 183–progress)
- 2XX – Solicitação bem-sucedida concluída (200 – OK)
- 3XX – Redirecionamento de chamada, a solicitação deve ser direcionada para outro local (302 – moved temporarily, 305 – use proxy)
- 4XX – Erro (403 – Forbidden)
- 5XX – Erro do servidor (500 – Internal Server Error; 501 – Not implemented)
- 6XX – Falha global (606 – Not acceptable)

Por exemplo:

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### Protocolo de descrição de sessão (SDP)

O SDP foi originalmente definido no IETF RFC 2327, agora obsoleto pelo RFC 4566. Ele tem como objetivo descrever sessões multimídia para fins de anúncio de sessão, convite de sessão e outras formas de iniciação de sessão multimídia. O SDP inclui:

- Protocolo de transporte (RTP/UDP/IP)
- Tipo de mídia (texto, áudio, vídeo)
- Formato de mídia ou codec (vídeo H.261, áudio g.711, etc.)
- Informações necessárias para receber essas mídias (endereços, portas, etc.)

O exemplo a seguir é uma transcrição de um SDP descrevendo uma chamada entre dois telefones.

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### Travessia NAT SIP

Network Address Translation (NAT) é um recurso usado pela maioria das redes para economizar endereços IP da Internet. Normalmente, uma empresa recebe um pequeno bloco de endereços IP, e os usuários finais recebem um endereço IP dinamicamente quando se conectam à Internet. O NAT resolve o problema de endereçamento ao mapear endereços internos para endereços externos. Ele armazena um mapeamento de endereços internos para externos em sua memória. Esse mapeamento é válido por um período específico de tempo, após o qual o mapeamento é descartado. O mapeamento usa pares IP:porta para os endereços internos e externos. Existem quatro tipos de NAT:

- Cone completo
- Cone restrito
- Cone de porta restrita
- Simétrico

A teoria NAT abaixo — os quatro tipos de NAT, o problema do cabeçalho Contact, keep-alives e forçar a mídia através do servidor — está no nível do protocolo e se aplica a qualquer implementação SIP. A forma como você configura cada comportamento no Asterisk 22 (PJSIP) é abordada mais adiante neste capítulo em *Nat traversal on res_pjsip*.

#### Cone Completo

O primeiro NAT, full cone, representa um mapeamento estático de um par IP:porta externo para um par IP:porta interno. Qualquer computador externo pode conectar‑se a ele usando o par IP:porta externo. Isso ocorre em firewalls não stateful implementados com o uso de filtros.

![Full Cone NAT: o host interno (10.0.0.1:8000) está mapeado estaticamente para o par externo 200.180.4.168:1234, de modo que qualquer computador externo pode enviar pacotes para esse par e alcançar o host interno](../images/07-sip-and-pjsip-fig11.png)

#### Cone Restrito

No cenário de cone restrito, o par IP:porta externo é aberto somente quando o computador interno envia dados para um endereço externo. No entanto, o NAT de cone restrito bloqueia quaisquer pacotes de entrada de um endereço diferente. Em outras palavras, o computador interno precisa enviar dados para um computador externo antes que ele possa enviar dados de volta.

#### Cone Restrito por Porta

O firewall de cone restrito por porta é quase idêntico ao cone restrito. A única diferença é que, agora, o pacote de entrada deve vir exatamente do mesmo IP e porta do pacote enviado.

#### Simétrica

O último tipo de NAT é chamado de simétrico. Ele difere dos três primeiros porque um mapeamento específico é feito para cada endereço externo. Apenas endereços externos específicos são permitidos a retornar pelo mapeamento NAT. Não é possível prever o par IP:porta externo que será usado pelo dispositivo NAT. Os outros três tipos de NAT permitem o uso de um servidor externo para descobrir o endereço IP externo para a comunicação. Com NAT simétrico, mesmo que você consiga se conectar a um servidor externo, o endereço descoberto não pode ser usado por nenhum outro dispositivo, exceto por esse servidor.

![NAT Simétrica: uma porta de origem externa diferente é alocada para cada destino, de modo que o mapeamento descoberto para um servidor não pode ser reutilizado por outro host, o que quebra a travessia baseada em STUN】(../images/07-sip-and-pjsip-fig12.png)

#### Tabela de firewall NAT

A tabela a seguir resume os quatro tipos de NAT.

| NAT type | Must send data first | Can determine the external IP:port for return packets | Restricts incoming packets to the destination IP:port |
| --- | --- | --- | --- |
| Full Cone | No | Yes | No |
| Restricted Cone | Yes | Yes | Only IP |
| Port Restricted Cone | Yes | Yes | Yes |
| Symmetric | Yes | No | Yes |

#### Sinalização SIP e RTP sobre NAT

Alguns dos maiores problemas na travessia de NAT são que você precisa resolver duas questões: sinalização SIP e áudio (RTP). A maioria dos problemas de áudio unidirecional está relacionada ao NAT. Um aspecto interessante do SIP é que, quando um UAC envia um pacote, ele incorpora o endereço IP no campo de cabeçalho SIP “Contact”. Normalmente esse é um endereço interno (RFC1918); respostas a esse pacote não podem ser roteadas pela Internet de volta ao UAC. As correções conceituais são sempre as mesmas:

- **Ignore the Contact/Via address and reply to where the packet actually came from.** This is the behaviour defined in RFC 3581 (`rport`). On PJSIP it is `force_rport=yes`, and `rewrite_contact=yes` rewrites the stored contact to the source address.  
- **Send media back to the address the RTP actually arrived from** (symmetric RTP, historically called *comedia*). On PJSIP this is `rtp_symmetric=yes`.  
- **Keep the NAT mapping open.** If the mapping times out, Asterisk can no longer send an INVITE to the UAC — the phone can place calls but not receive them. Sending a periodic OPTIONS (a *qualify*) keeps the pinhole open. On PJSIP this is `qualify_frequency=` on the AOR.

Se o NAT do usuário for do tipo simétrico, não é possível enviar pacotes de um UAC para outro diretamente; nesse caso, você deve forçar o RTP através do Asterisk com `direct_media=no`. Essas configurações são adequadas para a maioria dos casos. É possível otimizar o tráfego usando técnicas avançadas como Simple Traversal of UDP over NAT (STUN), que é útil com full cone, restricted cone e port restricted cone, e Application Layer Gateway (ALG). Infelizmente, a maioria dos firewalls hoje — até mesmo roteadores domésticos DSL/cabo — são simétricos, tornando o STUN inutilizável. O ALG poderia resolver o problema, mas não é suportado, não está implementado ou apresenta bugs na maioria dos casos.

#### Asterisk atrás de NAT

Às vezes o servidor Asterisk está implementado atrás de um firewall com NAT — uma situação muito comum ao implantar na nuvem. Nesse caso, é necessário fazer uma configuração extra para que o Asterisk anuncie seu endereço **public** nos cabeçalhos SIP e SDP em vez do endereço privado.

Conceptualmente há três etapas:

- Encaminhe a porta de sinalização SIP (UDP 5060 por padrão) do firewall para o servidor Asterisk.  
- Encaminhe o intervalo de portas de mídia RTP (UDP 10000–20000 por padrão, definido em `rtp.conf`) do firewall para o servidor Asterisk.  
- Informe ao Asterisk seu endereço externo e qual rede é local, para que ele saiba quando substituir o endereço público nos cabeçalhos.

No PJSIP, esses dois últimos itens correspondem a `external_media_address` / `external_signaling_address` e `local_net=` no **transport**, e a faixa de portas RTP ainda é configurada em `rtp.conf`:

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

A configuração completa e funcional do PJSIP para um servidor Asterisk atrás de NAT é apresentada mais adiante neste capítulo em *Asterisk Server behind NAT*.

### Limitações do SIP

Asterisk usa o fluxo RTP de entrada para sincronizar o fluxo de saída. Se o fluxo de entrada for interrompido (silence suppression), a música em espera será cortada. Em outras palavras, você não deve usar silence suppression em telefones ou provedores com Asterisk.

## PJSIP: o canal SIP

PJSIP é o canal SIP no Asterisk. Foi introduzido pela primeira vez no Asterisk 12 e, após anos de desenvolvimento, tornou‑se o canal SIP padrão e recomendado, e no Asterisk 22 (o LTS atual) é o único driver de canal SIP. PJSIP baseia‑se no projeto da Teluu chamado pjproject. A pilha pjproject é utilizada por muitos softphones e implementações comerciais de SIP. É uma pilha SIP versátil e madura.

### Por que usar PJSIP

PJSIP foi um redesenho completo de como o Asterisk fala SIP, e vale a pena entender os recursos que o tornaram o padrão.

#### Recursos

O canal oferece muitos recursos, alguns merecem destaque aqui

- Múltiplos registros: Você pode usar mais de um telefone conectado ao mesmo Address of Record. Em outras palavras, pode conectar dois telefones ao mesmo endpoint.
- Interface de Programação de Aplicação (API) amigável. A API é modular e fácil de estender, construída a partir de muitos pequenos módulos cooperantes em vez de um grande bloco de código.
- Múltiplos transportes: Você pode escutar múltiplos endereços, portas e transportes ao usar PJSIP. Não está limitado a um único endereço de bind para todos os seus dispositivos. PJSIP é muito flexível.

#### Uma nota sobre configuração

A configuração do PJSIP é mais verbosa: requer um pouco mais de esforço e mais linhas de configuração, já que cada dispositivo é descrito por vários objetos relacionados em vez de um único bloco peer. Essa estrutura extra é o que confere ao PJSIP sua flexibilidade, e o assistente de configuração (abordado mais adiante) mantém o provisionamento diário curto.

### Módulos PJSIP

O canal PJSIP é implementado por vários módulos descritos abaixo:

#### res_pjsip

Esta é a camada base do PJSIP e o módulo principal. É responsável por alguns dos principais serviços.

#### res_pjsip_session

Este módulo é responsável por sessões de mídia, processamento do protocolo de descrição de sessão e alguns complementos.

#### res_pjsip_messaging

Processa mensagens SIP e analisa cabeçalhos SIP.

#### res_pjsip_registrar

Responsável por lidar com registros SIP.

#### res_pjsip_pubsub

Responsável por processar subscribe, notify e publish. Essas mensagens são responsáveis por lidar com presença SIP e BLF (Busy Lamp Field).

### Configuração PJSIP

PJSIP possui muitas seções diferentes. O formato da seção é:

```
[Section Name]
Option = Value
Option = Value
```

#### Seção de endpoint

O objeto de configuração mais importante é o endpoint. A configuração do endpoint possui funcionalidade central e deve ser associada a uma seção AOR e Transport. Exemplo:

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

Se você observar o exemplo acima, o endpoint é uma espécie de cola que liga todas as seções juntas. Ele especifica um transporte, o endereço de registro e a autenticação para um telefone. Também define a parte mais importante, o ponto de entrada do contexto no dialplan.

#### Address of Record (AOR)

Este objeto informa ao Asterisk onde contatar o endpoint. Ele armazena os endereços de contato. Também permite a configuração de caixas de correio. Exemplo:

```
[softphone]
type=aor
max_contacts=2
```

#### Autenticação

Esta seção é responsável pela autenticação de entrada e saída. A documentação está disponível no arquivo de exemplo pjsip.conf. Exemplo:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### Transport

A seção de transporte permite definir endereços IPV4 e IPV6 e o protocolo de transporte, TCP, UDP, TLS, Websockets etc. Você também pode configurar endereços NAT nesta seção. É possível criar múltiplos transportes, mas eles não podem compartilhar o mesmo IP e porta e não é permitido vincular múltiplos transportes TCP ou TLS da mesma versão IP. Exemplo:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### Registro

Este objeto é usado para configurar um registro de saída. Exemplo:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### Identify

Este objeto controla a qual endpoint cada requisição SIP pertence. Se você não possuir uma seção identify, o sistema corresponderá o conteúdo do cabeçalho “From” com o nome da endpoint. Usando esta seção, você pode atribuir endereços IP específicos a endpoints específicos, identificados por nome de usuário ou IP. Exemplo:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

O objeto ACL permite que você configure redes específicas com acesso ao endpoint. Agora as ACLs são definidas em uma seção específica ou no acl.conf. Exemplo:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### Relacionamento entre entidades

O relacionamento entre os objetos de configuração oferece grande flexibilidade para a configuração. No entanto, pode parecer um pouco complexo para quem está começando.

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

O gráfico acima significa:

#### Relacionamentos:

| Objects | Cardinality |
| --- | --- |
| ENDPOINT / AOR | many to many |
| ENDPOINT / AUTH | zero to many, to zero to one |
| ENDPOINT / IDENTIFY | zero to one |
| ENDPOINT / TRANSPORT | zero to many, to at least one |
| REGISTRATION / AUTH | zero to many, to zero to one |
| REGISTRATION / TRANSPORT | zero to many, to at least one |
| AOR / CONTACT | many to many |

ACL e DOMAIN_ALIAS não possuem um relacionamento de configuração direto com os demais objetos.

### Configurando um Softphone

Para configurar um softphone você precisa definir várias seções diferentes. Abaixo um exemplo de como configurar um softphone. Do lado do cliente você pode usar o SipPulse Softphone (https://www.sippulse.com/produtos/softphone), que pode ser baixado e registrado contra o endpoint abaixo.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

A configuração acima define um transporte UDP na porta 5060, depois define um endpoint, sua autenticação por nome de usuário e senha e, em seguida, o Address of Record com um máximo de dois contatos.

### Configurando um trunk SIP

Para configurar um trunk SIP você precisa ter o endereço IP ou Host do trunk SIP, nome e senha. Você deve criar uma nova seção de registro para esse propósito.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=digest
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### Nat traversal on res_pjsip

A Tradução de Endereços de Rede (Network Address Translation) foi criada há muito tempo como forma de lidar com a escassez de endereços IPv4. Muitas pessoas também utilizam NAT como recurso de segurança, ocultando os endereços internos de uma rede da Internet pública. Às vezes será necessário lidar com a travessia de NAT. Em alguns casos, o servidor pode estar atrás de NAT, como quando você implanta o servidor na nuvem. Muitas vezes, se você estiver implantando na nuvem, seus usuários também estarão atrás de um roteador NAT. Para organizar as coisas, dividiremos isso em duas partes. A primeira é o servidor Asterisk atrás de NAT, como em uma implantação na nuvem. Na segunda seção, abordaremos como suportar clientes atrás de NAT usando res_pjsip.

#### Asterisk Server behind NAT

Quando o servidor Asterisk está atrás de NAT, você deve informar os endereços externos e internos locais na seção de transporte. Teremos as seguintes diretivas.

##### direct_media

O fluxo de mídia ocorre diretamente de peer para peer ou através do servidor? Para NAT, ele deve fluir através do servidor. Para NAT selecione **no**. Exemplo:

```
direct_media=no
```

##### external_media_address

Endereço de mídia para lidar com RTP externo. Normalmente o mesmo que o external_signaling_address. Use o endereço IP público do seu servidor para mídia e sinalização. Exemplo:

```
external_media_address=54.232.1.20
```

##### external_signaling_address

Endereço SIP externo onde receber mensagens. Exemplo:

```
external_signaling_address=54.232.1.20
```

##### local_net

A rede que você considera sua rede local. Exemplo:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### Exemplo completo de transporte para um servidor Asterisk atrás de NAT

Para usar um servidor Asterisk atrás de NAT você deve fazer duas etapas. Primeiro, definir um transporte atrás de NAT. Segundo, associar esse transporte ao endpoint.

##### Criando o transporte atrás de NAT

Para criar o transporte atrás de NAT no arquivo pjsip.conf crie uma seção como a abaixo.

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

# Associar o transporte a um endpoint

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

Para troncos SIP, você também deve associar o transporte à seção de registro conforme abaixo.

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### Usando Asterisk com clientes atrás de NAT

Para usar telefones atrás de NAT, você deve configurar alguns parâmetros adicionais por endpoint.

##### direct_media

O fluxo de mídia ocorre diretamente de peer para peer ou através do servidor? Para NAT, ele deve passar pelo servidor. Exemplo:

```
direct_media=no
```

##### rtp_symmetric

Isso é o que chamamos de comédia. Em vez de confiar no endereço definido neste cabeçalho SDP como de costume no SIP, use o endereço de onde você recebe o primeiro pacote rtp e envie de volta a partir do mesmo endereço. Exemplo:

```
rtp_symmetric=yes
```

##### force_rport

Este é o comportamento definido na RFC3581. Em vez de usar o endereço no cabeçalho VIA, envie as respostas de onde as solicitações estão vindo. Exemplo:

```
force_rport=yes
```

##### qualify_frequency

Esta configuração deve ser aplicada ao AOR (não ao endpoint). Há também a última etapa, que é configurar a opção qualify. Você deve sempre ter alguns pacotes enviando ping ao destino para manter o mapeamento NAT aberto. Isso é definido na seção AOR. Exemplo:

- qualify_frequency=15

Exemplo completo de um endpoint onde o servidor e o cliente estão atrás de NAT

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### Nomeação de Canal

Como de costume, um dos aspectos importantes de um canal é sua nomeação e o PJSIP tem alguns detalhes interessantes. Você disca um endpoint PJSIP com a tecnologia `PJSIP/`:

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

Um recurso útil é a possibilidade de discar todos os contatos registrados em um AOR de uma só vez. A função PJSIP_DIAL_CONTACTS será traduzida para a lista de contatos a serem discados.

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

Para discar um tronco é um pouco diferente. Assuma que o tronco não será registrado na sua plataforma ou não tem um endereço IP associado ao seu AOR (address of record). Você pode especificar o endereço do tronco diretamente na linha. Usando uma discagem internacional como exemplo.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

Se você preferir especificar o endereço do tronco na seção AOR, também pode usar.

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### Assistente de configuração PJSIP

PJSIP é poderoso, mas verboso para configurar: muitas seções diferentes e modelos que podem ser confusos a princípio. A boa notícia é o assistente de configuração PJSIP. Definindo cada canal em poucas linhas, ele permite criar modelos e simplificar a configuração de novos dispositivos. Use o arquivo pjsip_wizard.conf para configurar. Você ainda precisa definir as seções de transporte e globais no arquivo pjsip.conf. Pessoalmente, prefiro usar o assistente apenas para telefones; para troncos sip, geralmente o número não é grande e você pode configurar diretamente no pjsip. A maior vantagem do assistente é a possibilidade de usar modelos e criar telefones rapidamente.

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### Carregando e descarregando PJSIP

PJSIP é o único canal SIP no Asterisk 22, e seus módulos são carregados por padrão. Em casos raros você ainda pode querer controlar o carregamento de módulos pelo arquivo modules.conf — por exemplo, para desativar o PJSIP em um servidor que usa apenas IAX2 ou DAHDI.

#### Para desativar o PJSIP

Edite o arquivo modules.conf e adicione as linhas a seguir.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### Console commands

Agora que você configurou seus endpoints PJSIP, é hora de ver como verificar sua configuração. Existem muitos comandos de console para ajudá‑lo nessa tarefa. Depois de editar pjsip.conf, recarregue a configuração com:

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

#### pjsip show registrations

The command below shows the registrations made by our own server.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listing contacts:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems.

```
pjsip set logger on
pjsip set logger off
```

Você também pode restringir o registro a um único host com `pjsip set logger host <ip>`.

#### pjsip set history on

Uma ótima adição ao PJSIP é o conceito de histórico. Você pode capturar e analisar solicitações e respostas SIP em tempo real de maneira fácil. Para iniciar o histórico use o comando abaixo.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Agora você pode exibir o histórico:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

Em seguida, para ver uma solicitação ou resposta específica, exiba o item do histórico:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

Muito fácil, não é? Você também pode limpar o histórico sempre que quiser usando `pjsip set history clear`.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Resumo

SIP é o protocolo de sinalização da IETF que estabelece, modifica e encerra sessões de mídia. Seus agentes de usuário, proxies, registrador e gateways trocam mensagens baseadas em texto — REGISTER, INVITE, as respostas provisórias e finais, ACK e BYE — enquanto o SDP negocia os codecs e o RTP transporta a mídia. Essa teoria de protocolo é atemporal e se aplica a qualquer implementação SIP.

No Asterisk 22 você utiliza SIP através do **PJSIP** (`chan_pjsip`), configurado em `pjsip.conf`. Em vez de um único peer monolítico, um dispositivo é modelado como um conjunto de pequenos objetos inter-referenciados: `endpoint` (comportamento de chamada e codecs), `auth` (credenciais), `aor` (onde ele é alcançável) e `transport` (o ouvinte), além de `identify` (corresponder um trunk por IP) e `registration` (registro outbound) para provedores de serviço. Você viu como esses objetos se encaixam, como configurar tanto telefones quanto trunks, como as opções de travessia de NAT (`force_rport`, `rewrite_contact`, `rtp_symmetric`, `direct_media` e os `external_*`/`local_net` do transporte) resolvem implantações do mundo real, e como inspecionar tudo isso com `pjsip show endpoints`, `aors`, `contacts` e `registrations`.

## Quiz

1. Na arquitetura SIP, qual componente recebe uma requisição e responde com um redirect (como `302 Moved Temporarily`) contendo a nova localização, permanecendo fora do caminho das mensagens subsequentes?
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. Qual papel o Asterisk desempenha ao manipular uma chamada SIP entre dois telefones?
   - A. Um proxy SIP que permanece apenas no caminho de sinalização
   - B. Um servidor de redirecionamento SIP
   - C. Um back-to-back user agent (B2BUA) que interliga dois canais SIP
   - D. Um balanceador de carga SIP sem estado

3. Qual método SIP é usado por um telefone para informar ao registrar seu endereço IP atual para que possa receber chamadas posteriormente?
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. Verdadeiro ou Falso: No Asterisk 22, `chan_sip` e `sip.conf` ainda estão disponíveis como fallback legado ao lado do PJSIP.

5. Quais objetos de configuração um endpoint deve estar associado para que o Asterisk saiba o socket de escuta a ser usado e para onde enviar chamadas desse dispositivo? (Marque todas as que se aplicam.)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. Em um objeto PJSIP `aor`, qual configuração mantém o mapeamento NAT aberto qualificando periodicamente o contato, e qual é sua unidade?
   - A. `qualify=yes` (boolean)
   - B. `qualify_frequency` (seconds)
   - C. `rtp_timeout` (milliseconds)
   - D. `nat=force_rport`

7. Preencha a lacuna: Para fazer o Asterisk corresponder uma requisição SIP de entrada a um endpoint específico pelo endereço IP de origem (em vez de pelo cabeçalho `From`), você cria uma seção com `type=________`.

8. Qual objeto PJSIP é usado para configurar um **registro outbound** do Asterisk para um provedor de tronco SIP?
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. No CLI do Asterisk 22, qual comando habilita o logger de pacotes SIP que imprime cada requisição e resposta SIP no console?
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. Em um endpoint PJSIP que atende a um telefone atrás de um NAT simétrico, qual par de configurações faz o Asterisk responder ao endereço de origem da requisição (RFC 3581) e enviar a mídia de volta para onde o RTP realmente chega?
    - A. `direct_media=yes` e `srvlookup=yes`
    - B. `force_rport=yes` e `rtp_symmetric=yes`
    - C. `allowguest=yes` e `insecure=invite`
    - D. `qualify=yes` e `nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
