# Designing a VoIP network

Voice over IP is quickly growing in the telephony market. The convergence paradigm is changing the way in which we communicate, reducing costs and enhancing the way in which we trade information. Voice is just the beginning of a full multimedia communication era, including voice, video, and presence. In the future, we are not going to transport people to work, but work to people because it is cleaner, faster, and cheaper. VoIP is just part of this revolution. Our challenge in this chapter is to design a VoIP network. To do this, we will have to understand concepts such as session protocols and codecs as well as how to dimension the number of circuits and bandwidth.

## Objectives

Ao final deste capítulo, você deverá ser capaz de:

- Compreender os benefícios do VoIP
- Descrever como o Asterisk lida com VoIP
- Descrever os conceitos dos canais SIP e IAX
- Escolher o protocolo mais adequado para um canal de dados específico
- Escolher o codec mais adequado para um canal de dados específico
- Dimensionar o número necessário de canais
- Calcular a largura de banda necessária

## VoIP benefits

Why would you care about VoIP? VoIP provides benefits to both companies and individuals. Cost reduction is certainly one of them, but in some environments VoIP simplifies the integration of computer systems. Several of the benefits are detailed here:

### Convergence

The primary benefit of VoIP is the combination of data and voice networks to reduce costs (convergence). However, analyzing just voice minute costs may not be enough to justify the adoption of VoIP. The price of the minutes sold by phone companies is quickly becoming cheaper and is something to be considered before adopting VoIP.

### Infrastructure costs

The use of a single network infrastructure reduces the costs associated with additions, removals, and changes. As IP has become pervasive, it has brought VoIP-related technology to several new devices, such as cell phones, PDAs, embedded systems, and laptops.

### Open Standards

Finally, the open standards upon which VoIP is built provide the freedom to choose from different vendors. This single benefit makes the customer king instead of a subordinate to TELCOS and PBX manufacturers.

### Computer Telephony Integration

Telephony is far older than computing. Telephony PBXs are circuit-switch based, and you usually do not have more than a computer for supervision. With VoIP, telephony is from the ground up created based in computer standards. This makes the use of Computer Telephony applications cheaper and easier than in the old model. You can quickly create a long list of telephony applications based on Asterisk. You can develop IVRs, ACDs, CTI, dialers, screen popups, and other applications in a fraction of the time required for traditional PBXs.

## Arquitetura VoIP do Asterisk

A arquitetura do Asterisk é mostrada abaixo. O Asterisk trata todos os protocolos VoIP como canais. Você pode usar qualquer codec ou qualquer protocolo. O conceito a ser aprendido aqui é que o Asterisk interliga qualquer tipo de canal a qualquer outro. Assim, você pode traduzir protocolos de sinalização como SIP e IAX entre si e ainda com codecs diferentes. Por exemplo, pode traduzir uma chamada de um telefone SIP na rede local usando o codec G.711 para um tronco SIP ao seu provedor VoIP usando o codec G.729. Nos próximos capítulos, explicaremos os detalhes da arquitetura SIP e IAX. O suporte a H.323 (via o add‑on chan_ooh323) está disponível, mas cada vez mais raro; SIP/PJSIP é o padrão para implantações modernas.

![Arquitetura modular do Asterisk: aplicações e canais conectam‑se ao núcleo do switch PBX através de APIs, com tradução de codec e módulos de formato de arquivo carregados dinamicamente.](../images/06-voip-network-fig01.png)

## VoIP protocols and the network stack

VoIP usa um conjunto de protocolos diferentes que trabalham em conjunto. É tentador alinhá‑los
com o modelo de referência OSI de sete camadas, e muitos diagramas mais antigos fazem exatamente
isso — colocando SIP e H.323 na camada “session” e os codecs na camada
“presentation”. Esse mapeamento sempre foi controverso. O IETF, que
padroniza o SIP, não usa o modelo OSI; ele segue o modelo TCP/IP de quatro camadas
(DoD) mais antigo, e o RFC 3261 define **SIP como um protocolo de camada de aplicação**. A mídia
segue o mesmo padrão: RTP e os codecs vivem na carga útil da aplicação, transportados
sobre UDP na camada de transporte. A tabela abaixo mapeia os principais protocolos VoIP para o
modelo TCP/IP que o IETF realmente usa, com o equivalente aproximado ao OSI mostrado apenas para
referência.

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

Mecanismos de QoS como DiffServ operam na camada IP para priorizar pacotes de voz e
melhorar a qualidade das chamadas. Algumas especificidades dos protocolos:

- **SIP** usa UDP ou TCP na porta 5060 (TLS na 5061) para transportar sinalização. O áudio é
  transportado separadamente por RTP sobre um intervalo configurável de portas UDP (o exemplo
  `rtp.conf` fornecido com o Asterisk usa de 10000 a 20000), codificado com um codec como G.711.
- **H.323** transporta a sinalização de chamada sobre TCP (sinalização de chamada H.225 na porta 1720), enquanto
  o canal H.225 RAS usa UDP na porta 1719; RTP transporta o áudio.
- **IAX2** é incomum: ele multiplexa tanto sinalização quanto mídia sobre uma única porta UDP
  (4569), o que simplifica a travessia de NAT e firewalls.


## Como escolher um protocolo

Dado a quantidade de protocolos, como escolher o melhor para sua rede? Nesta seção, destacaremos as vantagens e desvantagens de cada protocolo.

### SIP - Session Initiated Protocol

SIP é um padrão aberto da Internet Engineering Task Force (IETF), amplamente definido no RFC 3261. A maioria dos provedores modernos de VoIP usa SIP; de fato, está se tornando o padrão de VoIP mais popular. A força do SIP está no fato de ser um padrão baseado na IETF. SIP é leve quando comparado ao mais antigo H.323. A principal fraqueza do SIP é a travessia de NAT — um desafio para a maioria dos provedores de VoIP SIP. A IETF não criou o SIP pensando em faturamento, mas em comunicações abertas entre pares. O faturamento costuma ser uma preocupação para os provedores de VoIP.

### IAX – Inter Asterisk eXchange

IAX é um protocolo aberto originalmente desenvolvido pela Digium (agora Sangoma). IAX é um protocolo tudo-em-um, pois transporta sinalização e mídia através da mesma porta UDP (4569). Mark Spencer desenvolveu o IAX como um protocolo binário para reduzir a largura de banda. A principal força do IAX é seu uso reduzido de largura de banda (não utiliza RTP); ele também é muito fácil para travessia de NAT e firewall, já que usa apenas uma porta UDP (4569).

Se um fabricante tradicional de PBX tivesse criado o IAX, provavelmente teria comercializado o protocolo como “a melhor coisa desde o sorvete”; em algumas situações, o IAX em modo trunk pode reduzir o uso de largura de banda de voz em um terço. IAX2 (versão 2) ainda é distribuído no Asterisk 22 via o módulo `chan_iax2` e continua útil para trunks Asterisk‑to‑Asterisk, embora seja considerado legado; SIP/PJSIP é preferido para novas implantações. IAX2 está especificado no [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informacional).

### MGCP – Media Gateway Control Protocol

MGCP é um protocolo usado em conjunto com H.323, SIP e IAX. Sua maior vantagem é a escalabilidade. Ele é configurado no agente de chamadas em vez dos gateways. Isso simplifica o processo de configuração e permite gerenciamento centralizado. Contudo, a implementação no Asterisk não está completa, e parece que poucas pessoas o utilizam.

### H.323

H.323 ainda é bastante usado em VoIP. É um dos primeiros protocolos de VoIP e é essencial para conectar infraestruturas legadas de VoIP baseadas em gateways. H.323 ainda é o padrão no mercado de gateways, embora o mercado esteja migrando lentamente para SIP. As forças do H.323 incluem a ampla adoção de mercado e maturidade. As fraquezas do H.323 estão relacionadas à complexidade de implementação e aos custos associados aos órgãos de padronização.

### Tabela de comparação de protocolos

A tabela a seguir resume as diferenças entre os protocolos de sessão.

| Protocol | Standard body | Asterisk 22 module / status | Used for |
|----------|---------------|-----------------------------|----------|
| SIP | IETF standard | `chan_pjsip` (core; the only SIP driver — `chan_sip` was removed in Asterisk 21) | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; still shipped, considered legacy) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | `chan_ooh323` (external community add-on, not in the base build) | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | (legacy MGCP phones) |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | (legacy Cisco phones) |

## Um endpoint por dispositivo

Em Asterisk 22 a pilha PJSIP modela cada telefone, tronco ou gateway como um único objeto **endpoint** em `pjsip.conf`. Um endpoint tanto coloca quanto recebe chamadas; suas credenciais vivem em um objeto `auth`, seu endereço registrado em um `aor`, e seu caminho de rede em um `transport`. Você configura um endpoint por dispositivo e anexa as peças que ele precisa — não há papel separado de "user" versus "peer" para considerar. (O modelo completo de objetos é abordado em *SIP & PJSIP in depth*.)

## Codecs and codec translation

Você usará um codec para converter a voz de uma onda analógica para um sinal digital. Codecs diferem entre si em aspectos como qualidade de som, taxa de compressão, largura de banda e requisitos de computação. Serviços, telefones e gateways normalmente suportam vários desses aspectos. O codec G.729 é muito popular. Ele não faz parte da compilação padrão do Asterisk 22; ao invés disso ele é distribuído como um módulo externo (`codec_g729`) que você baixa da Digium (agora Sangoma). O código‑fonte do Asterisk `menuselect` lista‑o com `support_level=external` e observa claramente: "Download the g729a codec from Digium. A license must be purchased for this codec." Em outras palavras, o uso legal do G.729 requer uma licença comprada por canal. (Uma alternativa de código aberto, `bcg729`, também existe.)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

O Asterisk 22 suporta os seguintes codecs (entre outros):

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — qualidade padrão PSTN; ulaw comum na América do Norte, alaw comum na Europa e América Latina
- ITU G.722: 64 Kbps — wideband (voz HD), boa qualidade com a mesma largura de banda do G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — módulo binário externo `codec_g729` baixado da Digium/Sangoma (`support_level=external`; é necessário comprar uma licença para usá‑lo)
- Speex: 2.15 to 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variável — codec moderno wideband/fullband; excelente qualidade e resiliência à perda de pacotes; fornecido como um módulo binário externo `codec_opus` baixado da Digium/Sangoma (`support_level=external`; nenhuma compra de licença mencionada, ao contrário do G.729); recomendado para WebRTC e endpoints SIP modernos. (Alternativas de compilação open‑source existem no GitHub.)

Além disso, o Asterisk permite a tradução entre codecs. Em alguns casos, isso não é possível, como no caso do g723, que é suportado apenas em modo pass‑thru. Traduzir de um codec para outro consome muitos recursos da CPU. Portanto, evite isso sempre que possível.

## How to choose a Codec

Codec selection depends on several options, such as:

- Qualidade de som
- Custos de licenciamento
- Consumo de CPU
- Requisitos de largura de banda
- Ocultação de perda de pacotes
- Disponibilidade para Asterisk e dispositivos telefônicos

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## Overhead causado por cabeçalhos de protocolo

Apesar de os codecs utilizarem pouca largura de banda, precisamos considerar o overhead causado pelos cabeçalhos de protocolo como Ethernet, IP, UDP e RTP. Dessa forma, a largura de banda realmente consumida depende dos cabeçalhos usados. Em uma rede Ethernet o requisito é maior do que em uma rede PPP, porque o cabeçalho PPP é mais curto que o Ethernet. Um único pacote de voz G.729, por exemplo, transporta apenas 20 bytes de carga útil, mas é encapsulado em aproximadamente 58 bytes de cabeçalhos Ethernet, IP, UDP e RTP — portanto, são os cabeçalhos, e não o codec, que dominam a largura de banda (veja a figura abaixo).

![A single g.729 voice packet on Ethernet: 20 bytes of payload wrapped in 58 bytes of Ethernet, IP, UDP, and RTP headers — a g.729 conversation consumes 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

Você pode calcular facilmente outros requisitos de largura de banda usando uma calculadora online de largura de banda VoIP, como <https://www.voip.school/bandcalc/bandcalc.php>.


## Engenharia de Tráfego

Um problema principal no projeto de redes VoIP é dimensionar o número de linhas e a largura de banda necessária para um destino específico, como um escritório remoto ou um provedor de serviços. Também é importante dimensionar o número de chamadas simultâneas do Asterisk (parâmetro principal para o dimensionamento do Asterisk).

### Simplificações

A simplificação primária e mais amplamente usada é estimar o número de chamadas por tipo de usuário. Por exemplo:

- PBXs corporativas (uma chamada simultânea para cada cinco ramais)
- Usuários residenciais (uma chamada simultânea para cada dezesseis usuários)

Exemplo #1 A sede da empresa tem 120 ramais e duas filiais—a primeira com 30 ramais e a segunda com 15 ramais. Nosso objetivo é dimensionar o número de troncos E1 na sede e a largura de banda necessária para a rede Frame-Relay.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Número de linhas T1

- Total de ramais usando linhas T1: 120+30+15=165 linhas
- Usando um tronco para cada cinco ramais para uso empresarial
- Total de linhas = 33 ou aproximadamente 2xT1 linhas

1b Requisitos de largura de banda Escolhemos o codec g.729 por causa dos requisitos de largura de banda, qualidade de som e consumo médio de CPU.

Com um tronco para cada cinco ramais:

- Largura de banda necessária para a filial #1 (Frame-relay): 26.8*6=160.8 Kbps
- Largura de banda necessária para a filial #2 (Frame-relay): 26.8*3= 80.4 Kbps

### Método Erlang B

Quando você tem dados históricos, pode dimensionar o tronco de forma mais científica em vez de simplificar. Usaremos o trabalho de Agner Karup Erlang (Copenhagen Telephone Company, 1909), que desenvolveu uma fórmula para calcular o número de linhas em um grupo de troncos entre duas cidades.

Um **Erlang** é uma unidade de medida de tráfego comum em telecom; descreve o volume de tráfego durante uma hora. Por exemplo, suponha que 20 chamadas ocorram em uma hora, com média de 5 minutos de conversa cada:

- Minutos de tráfego na hora: 20 × 5 = 100 minutos
- Horas de tráfego dentro de uma hora: 100 / 60 = **1.66 Erlangs**

Você pode ler essas medidas de um registrador de chamadas e usá‑las para projetar sua rede e calcular o número de linhas necessárias. Uma vez conhecido o número de linhas, você pode calcular os requisitos de largura de banda.

**Erlang B** é o método mais usado para calcular o número de linhas em um grupo de troncos. Ele assume que as chamadas chegam aleatoriamente (distribuição de Poisson) e que chamadas bloqueadas são imediatamente descartadas. Requer que você conheça o **Busy Hour Traffic (BHT)**, que pode ser obtido de um registrador de chamadas ou estimado como simplificação: BHT = 17% dos minutos de chamada de um dia.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

Outra variável importante é o Grade of Service (GoS), que define a probabilidade de bloqueio de chamadas por falta de linhas. Você pode arbitrar esse parâmetro, que normalmente é 0.05 (5% das chamadas perdidas) ou 0.01 (1% das chamadas perdidas). Exemplo #1: Usando o mesmo exemplo de sede e duas filiais introduzido anteriormente nesta seção, forneceremos alguns dados sobre padrões de tráfego. Do registrador de chamadas, descobrimos estes dados: Dados do registrador de chamadas (Minutos de chamada e BHT):

- Sede para Filial #1 = 2.000 minutos, BHT = 300 minutos
- Sede para Filial #2 = 1.000 minutos, BHT = 170 minutos
- Filial #1 para Filial #2 = 0, BHT=0

Vamos arbitrar GoS

## Reduzindo a largura de banda necessária para VoIP

Três métodos podem ser usados para reduzir a largura de banda necessária para chamadas VoIP:

- compressão de cabeçalho RTP
- IAX Trunked
- carga útil de VoIP

### Compressão de Cabeçalho RTP

Em redes Frame-Relay e PPP, você pode usar compressão de cabeçalho RTP. A compressão de cabeçalho RTP foi definida na RFC 2508. É um padrão IETF disponível em vários roteadores. No entanto, seja cauteloso, pois alguns roteadores exigem um conjunto de recursos diferente para que esse recurso esteja disponível. O impacto de usar compressão de cabeçalho RTP é fabuloso, pois reduz a largura de banda necessária em nosso exemplo de 26,8 Kbps por conversa de voz para 11,2 Kbps — uma redução de 58,2%!

### Modo trunk IAX2

Se você estiver conectando dois servidores Asterisk, pode usar o protocolo IAX2 no modo trunk. Essa tecnologia revolucionária não precisa de roteadores especiais e pode ser aplicada a qualquer tipo de enlace de dados.

![Modo trunk IAX2 em Ethernet: uma única chamada g.729 precisa de sua pilha completa de cabeçalhos (31,2 Kbps), mas uma segunda chamada compartilha esses cabeçalhos e adiciona apenas um pequeno miniframe IAX2, resultando em cerca de 9,6 Kbps de largura de banda extra por chamada adicional.](../images/06-voip-network-fig08.png)

O modo trunk IAX2 reutiliza os mesmos cabeçalhos da segunda chamada e seguintes. Usando g729 em um link PPP, a primeira chamada consumirá 30 Kbps de largura de banda, enquanto a segunda chamada usará o mesmo cabeçalho da primeira e reduzirá a largura de banda necessária para a chamada adicional para 9,6 Kbps. Podemos calcular a largura de banda necessária no modo trunk da seguinte forma: Branch #1 (11 calls) Bandwidth = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Branch #2 (8 calls) Bandwidth = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps A primeira chamada usa 31,2 Kbps, a próxima 9,6, e assim por diante.

### Aumentando a Carga Útil de Voz

Esse método é muito comum ao usar gateways VoIP pela Internet. Ao usar uma carga útil maior, você sacrifica latência em favor de redução de largura de banda. Você pode alterar a packetização RTP acrescentando o tamanho do quadro ao codec na instrução allow.

![Aumentando a carga útil de voz: empacotar 60 bytes de carga g.729 em um único pacote (em vez de 20) amortiza os 58 bytes de cabeçalhos em mais voz, reduzindo a largura de banda para cerca de 16,05 Kbps por chamada ao custo de latência adicional.](../images/06-voip-network-fig09.png)

Exemplo:

```
allow=ulaw:30
```

O número após os dois pontos é o intervalo de packetização em milissegundos — quanto de voz é transportado em cada pacote RTP. Um valor maior amortiza a sobrecarga fixa do cabeçalho em mais áudio (menos largura de banda) ao custo de latência adicional. Cada codec tem seu próprio tamanho mínimo, máximo e padrão de quadro; G.711 (`ulaw`/`alaw`), por exemplo, tem padrão de 20 ms.

## Summary

Neste capítulo, você aprendeu que o Asterisk trata a VoIP usando canais. Ele suporta SIP (via `chan_pjsip` no Asterisk 22) e IAX2; H.323 está disponível apenas através do add‑on comunitário `ooh323`, e os canais mais antigos MGCP e SCCP (Skinny) não fazem mais parte de uma compilação padrão do Asterisk 22. Você comparou e aprendeu como escolher um protocolo de sinalização e um codec para canais VoIP. O IAX2 é mais eficiente em largura de banda e pode atravessar NAT facilmente. SIP/PJSIP é o protocolo mais suportado por fornecedores de telefones e gateways de terceiros e é o único driver de canal SIP no Asterisk 22. O protocolo H.323 é o mais antigo e deve ser usado para conectar a infraestruturas legadas de VoIP. Na seção de Engenharia de Tráfego, aprendemos como projetar e dimensionar uma rede VoIP.

## Quiz

1. Which of the following are benefits of VoIP described in this chapter (check all that apply)?
   - A. Convergence of data and voice networks to reduce cost
   - B. Lower infrastructure cost for additions, removals, and changes
   - C. Open standards that free you from a single vendor
   - D. Easier and cheaper Computer Telephony Integration
   - E. Guaranteed lower per-minute calling rates than any phone company
2. Convergence is the integration of voice, data, and video in a single network; its primary benefit is cost reduction in the implementation and maintenance of separate networks.
   - A. False
   - B. True
3. Asterisk treats every VoIP protocol as a channel and can bridge any channel type to any other, transcoding between codecs when needed.
   - A. False
   - B. True
4. In Asterisk 22, SIP is handled by which channel driver?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In the TCP/IP (IETF) model that SIP is actually defined against in RFC 3261, the signaling protocols SIP, H.323, and IAX2 operate at the ___ layer.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP is the most adopted protocol for IP phones and is an open standard largely defined by the IETF in RFC 3261.
   - A. False
   - B. True
7. IAX2 transports both signaling and media over a single UDP port, which makes it efficient and easy to traverse NAT. Which UDP port does IAX2 use?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX was originally developed by Digium (now Sangoma). Despite limited adoption by phone vendors, IAX is excellent when you need (check all that apply):
   - A. To reduce bandwidth usage (it does not use RTP)
   - B. A video media format
   - C. Easy NAT and firewall traversal
   - D. Trunk mode to combine many Asterisk-to-Asterisk calls and amortize header overhead
9. In Asterisk 22, a device is configured as a single PJSIP `endpoint` object that both places and receives calls — there is no separate "user" or "peer" role.
   - A. False
   - B. True
10. Regarding codecs in Asterisk 22, check all the true statements:
    - A. G.711 is equivalent to PCM and uses 64 Kbps of bandwidth.
    - B. Sangoma's codec_g729 module is free to download, but lawful use requires a purchased per-channel license.
    - C. GSM is popular because it uses about 13 Kbps and needs no license.
    - D. G.711 u-law is common in North America, while a-law is common in Europe and Latin America.
    - E. G.729 is light and uses very few CPU resources to encode and decode compared with G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
