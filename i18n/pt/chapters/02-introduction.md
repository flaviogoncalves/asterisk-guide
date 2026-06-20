# Introdução ao Asterisk PBX

A popularidade de distribuições prontas para uso, como FreePBX e Issabel, tem crescido recentemente. Neste livro, abordaremos o Asterisk clássico, que é a base para entender essas distribuições. O Asterisk PBX é um software de código aberto capaz de transformar um PC comum em um poderoso PBX multiprotocolo. Neste capítulo, aprenderemos sobre as possibilidades dessa nova tecnologia e sua arquitetura básica.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Explicar o que é o Asterisk e o que ele faz;
- Descrever o papel da Digium™ e de sua sucessora Sangoma;
- Reconhecer a arquitetura básica do Asterisk e seus componentes;
- Apontar diversos cenários de uso; e
- Identificar fontes de informação e ajuda.

## O que é Asterisk

Asterisk é um software PBX de código aberto que transforma um computador comum em um PBX completo para usuários domésticos, empresas, provedores de serviços VoIP e companhias telefônicas. Asterisk também é tanto uma comunidade de código aberto quanto um projeto patrocinado pela Sangoma Technologies (que adquiriu a Digium em 2018). Você é livre para usar e modificar o Asterisk conforme suas necessidades. O Asterisk permite conectividade em tempo real entre redes PSTN e VoIP. Como o Asterisk é muito mais que um PBX, você não apenas tem uma atualização excepcional para o seu PBX existente, mas também pode fazer coisas novas em telefonia, como:

- Conectar funcionários que trabalham de casa a um PBX de Escritório via Internet de banda larga;
- Conectar vários escritórios em locais diferentes através de uma rede IP, rede privada ou até mesmo pela própria Internet;
- Oferecer aos seus funcionários um correio de voz integrado com a web e e‑mail;
- Construir aplicações como IVRs que permitem conexões ao seu sistema de pedidos ou outras aplicações;
- Dar a usuários em viagem acesso ao PBX da empresa de qualquer lugar com uma simples conexão de banda larga ou VPN; e
- muito mais....

O Asterisk inclui vários recursos avançados antes encontrados apenas em sistemas de alto nível, tais como:

- Música para clientes em espera nas filas de chamadas, com suporte a streaming de mídia e arquivos MP3;
- Filas de chamadas, permitindo que uma equipe de agentes atenda chamadas e monitore as filas;
- Integração com texto‑para‑fala e reconhecimento de voz;
- Registros detalhados transferidos tanto para arquivos de texto quanto para bancos de dados SQL; e
- Conectividade PSTN através de linhas digitais e analógicas.

## O que é AsteriskNOW (Histórico) e FreePBX

Asterisk em sua forma mais pura, também conhecido como “classic asterisk” (denominação do pacote Debian) é considerado mais uma ferramenta de desenvolvimento do que um produto acabado por si só. AsteriskNOW foi uma iniciativa para transformar o Asterisk em um soft-appliance. A distribuição incluía CentOS como sistema operacional e FreePBX como interface gráfica. AsteriskNOW foi descontinuado.

Hoje, a distribuição padrão turnkey de Asterisk é **FreePBX** (mantida pela Sangoma), que agrupa o Asterisk com uma GUI de administração baseada na web e um ecossistema de módulos. FreePBX é licenciado sob a GPL e pode ser baixado gratuitamente em www.freepbx.org. Para implantações comerciais, a Sangoma também oferece **FreePBX Distro** (uma imagem Linux completa) e seu produto comercial **PBXact**.

## Role of Digium™ and Sangoma

Digium, uma empresa localizada em Huntsville, Alabama, foi a criadora e desenvolvedora principal do Asterisk desde sua fundação em 1999. Além de ser a patrocinadora principal do desenvolvimento do Asterisk, a Digium produzia placas de interface telefônica e outros hardwares para PBXs Asterisk, e criou produtos comerciais como o Switchvox (direcionado ao mercado SMB). Em 2018, a Digium foi adquirida pela **Sangoma Technologies**, uma empresa canadense de comunicações unificadas. Desde a aquisição, a Sangoma continua a patrocinar o desenvolvimento do Asterisk e atua como sua principal guardiã, mantendo o projeto de código aberto em www.asterisk.org.

Historicamente, a Digium oferecia o Asterisk sob três tipos de acordos de licença:

- General Public License (GPL) Asterisk. Esta é a versão mais usada. Inclui todos os recursos e é livre para ser usada e modificada de acordo com os termos da licença GPL.
- Asterisk Business Edition era uma versão comercial do Asterisk. Algumas empresas usavam a Business Edition porque não queriam ou não podiam usar a licença GPL — geralmente porque não queriam liberar seu código‑fonte junto com o Asterisk. **Note:** Asterisk Business Edition foi descontinuada; hoje o Asterisk é distribuído exclusivamente sob a GPL.
- Asterisk OEM licensing. Após a Digium parar de vender a Asterisk Business Edition no varejo, continuou a licenciar essa edição comercial para clientes OEM — fornecedores de equipamentos que queriam construir produtos proprietários sobre o Asterisk sem liberar seu próprio código‑fonte sob a GPL.

### The Zapata project and its relationship with Asterisk

O projeto Zapata foi desenvolvido por Jim Dixon, que também foi responsável pelo design revolucionário de hardware usado com o Asterisk. O hardware também é open‑source; como tal, pode ser usado por qualquer empresa, e hoje vários fabricantes produzem placas compatíveis com essa arquitetura.

O projeto Zapata produziu uma arquitetura chamada Zaptel, posteriormente renomeada para DAHDI (Digium/Asterisk Hardware Device Interface). Um dos principais benefícios dessa arquitetura é a capacidade de usar a CPU do PC para processar streaming de mídia, cancelamento de eco e transcodificação. Em contraste, a maioria das placas existentes usa processadores de sinal digital (DSP) para executar essas tarefas. O uso da CPU do PC em vez de DSPs dedicados reduz drasticamente o preço da placa. Assim, essas placas são significativamente mais baratas que as interfaces anteriormente disponíveis de outros fabricantes. Por outro lado, essas placas exigem muita CPU; um uso inadequado da CPU do PC pode impactar significativamente a qualidade de voz. Recentemente, a Digium lançou uma placa coprocessadora que usa DSPs para codificar e decodificar G.729 e G.723, permitindo melhor escalabilidade para um grande número de canais.

## Por que Asterisk?

Lembro-me do meu primeiro contato com o Asterisk. Normalmente, a primeira reação a algo novo—especialmente algo que compete com o que você já conhece—é rejeitá‑lo! Foi exatamente isso que aconteceu em 2003. O Asterisk competia com uma solução que eu estava vendendo a um cliente (gateway VoIP 4 E1) e era dez vezes mais barato do que eu cobrava pela solução que já conhecia. Esse preço desproporcional me levou a começar a estudar o Asterisk para identificar possíveis armadilhas e desvantagens. Por exemplo, descobri que a CPU do PC na época não suportaria 120 sessões simultâneas de g.729; no fim das contas, ganhei a proposta com a minha solução de gateway.

Entretanto, esse exercício me fez descobrir que o Asterisk poderia resolver uma variedade de problemas muito caros para a minha base de clientes. Estávamos em apuros com orçamentos elevados para IVR, mensagens unificadas, gravação de chamadas e discadores; com dimensionamento adequado, os problemas de CPU podiam ser contornados. De fato, em apenas três anos o Asterisk se tornou o produto carro‑chefe da minha empresa (cheguei a abrir outra empresa apenas para o negócio de Asterisk). Na minha opinião, o Asterisk é uma revolução em telecomunicações que representa para a telefonia IP o que o Apache representa para serviços web.

### Redução extrema de custos

Se você comparar um PBX tradicional com o Asterisk no que diz respeito a interfaces digitais e telefones, o Asterisk é ligeiramente mais barato que esses PBXs. Contudo, o Asterisk realmente compensa quando você adiciona recursos avançados como voicemail, ACD, IVR e CTI. Com esses recursos avançados, o Asterisk torna‑se significativamente menos caro que os PBXs tradicionais. Na verdade, comparar PBXs Asterisk com PBXs analógicos de baixo custo é injusto, pois o Asterisk oferece tantos recursos que não estão disponíveis em sistemas analógicos de baixo custo.

### Controle e independência do sistema telefônico

Um dos benefícios mais citados pelos clientes do Asterisk é a independência que ele proporciona. Alguns fabricantes atuais nem sequer fornecem ao cliente a senha do sistema ou a documentação de configuração. Com a abordagem “faça‑você‑mesmo” do Asterisk, o usuário obtém total liberdade; como bônus, o usuário tem acesso a uma interface padrão.

### Ambiente de desenvolvimento fácil e rápido

O Asterisk pode ser estendido usando linguagens de script como PHP e Perl com as interfaces AMI e AGI. O Asterisk é open‑source, e seu código‑fonte pode ser modificado pelo usuário. O código‑fonte é escrito principalmente em linguagem de programação ANSI C.

### Rico em recursos

O Asterisk possui vários recursos que são inexistentes ou opcionais em PBXs tradicionais (por exemplo, voicemail, CTI, ACD, IVR, música em espera embutida e gravação). Os custos desses recursos em algumas plataformas excedem o preço da própria plataforma.

### Conteúdo dinâmico no telefone

O Asterisk é programado em linguagem C e outras linguagens comuns no ambiente de desenvolvimento atual. A possibilidade de fornecer conteúdo dinâmico é praticamente ilimitada.

### Plano de discagem flexível e poderoso

Outro avanço do Asterisk é seu poderoso plano de discagem. Em PBXs tradicionais, até recursos simples como roteamento de menor custo (LCR) são inviáveis ou opcionais. Com o Asterisk, escolher a melhor rota é fácil e limpo.

### Open‑source rodando sobre Linux

Um dos maiores atributos do Asterisk é sua comunidade. Vários recursos estão disponíveis, incluindo a documentação oficial do Asterisk (docs.asterisk.org), a wiki VoIP‑Info mantida pela comunidade (www.voip-info.org <http://www.voip-info.org>), listas de distribuição por e‑mail e fóruns. À medida que o Asterisk é cada vez mais adotado, bugs são encontrados e corrigidos rapidamente. Com uma grande base de usuários e uma equipe de desenvolvimento ativa, o Asterisk está entre as plataformas PBX mais amplamente testadas no mundo, o que ajuda a manter o código estável e maduro.

### Limitações da arquitetura do Asterisk

Algumas limitações do Asterisk decorrem do uso do design de telefonia Zapata. Nesse design, o Asterisk usa a CPU do PC para processar canais de voz em vez de processadores digitais de sinal (DSPs) dedicados, que são comuns em outras plataformas. Embora isso permita uma enorme redução de custos em interfaces

## Principais objeções ao Asterisk PBX

É comum ouvir objeções à adoção do Asterisk, que abordaremos aqui.

### A participação de mercado do Asterisk é muito pequena

A participação de mercado costuma ser medida pelo número de PBXs vendidas. Essas estatísticas são geralmente obtidas dos maiores distribuidores. O Asterisk é software livre que pode ser baixado e implantado sem que nenhuma venda seja registrada, portanto é sistematicamente subcontado nesses números. Mesmo assim, o Asterisk alimenta uma base instalada muito grande em todo o mundo — desde PBXs de escritório de servidor único até grandes implantações de operadoras e centros de contato — e continua sendo o motor dominante por trás do ecossistema de PBX de código aberto (incluindo distribuições turnkey como o FreePBX).

### Se é gratuito, como o fabricante sobrevive?

Na verdade, não existe algo como um fabricante de software de código aberto no sentido tradicional. A Digium desenvolve o Asterisk desde 1999, sustentando‑se por meio da venda de placas de interface telefônica, produtos comerciais de PBX como o Switchvox e softwares relacionados. Em 2018, a Sangoma Technologies adquiriu a Digium. A Sangoma continua a financiar o desenvolvimento do Asterisk e gera receita através de produtos comerciais (módulos comerciais do FreePBX, PBXact, Switchvox), vendas de hardware e serviços profissionais.

### É difícil encontrar suporte técnico!

A Sangoma fornece suporte técnico comercial para o Asterisk por meio de seu ecossistema de parceiros e diretamente via suas ofertas de produtos. Uma rede global de profissionais certificados oferece suporte de primeira linha e serviços profissionais. O suporte da comunidade permanece ativo através dos fóruns e listas de discussão do Asterisk em www.asterisk.org.

### O Asterisk suporta mais de 200 ramais?

Sim, absolutamente. Um único servidor Asterisk bem dimensionado pode lidar com um grande número de ramais, e o Asterisk escala ainda mais distribuindo usuários entre múltiplos servidores com balanceamento de carga e failover, permitindo grandes implantações multi‑site.

### Só “geeks” conseguem instalar o Asterisk

Com o FreePBX (disponível como distro independente da Sangoma), até profissionais com conhecimento limitado de Linux conseguem instalar e configurar uma PBX de complexidade média. Com a ajuda de uma GUI, é possível configurar uma PBX completa em apenas algumas horas.

### E se o servidor falhar?

Uma das principais vantagens do Asterisk é sua capacidade de operar em sistemas tolerantes a falhas. É relativamente simples e barato ter dois servidores rodando em paralelo. Eu te desafio a tentar isso com uma PBX convencional!

### Nossa empresa não usa software de código aberto

Sua empresa provavelmente usa software de código aberto sem sequer perceber. Vários appliances utilizam Linux como sistema operacional. Além disso, suporte comercial e implantações gerenciadas estão disponíveis pela Sangoma e sua rede de parceiros certificados.

### Usar a CPU do PC para processar sinalização e mídia não é recomendado

O Asterisk usa a CPU do servidor para processar sinalização e mídia dos canais de voz em vez de ter DSPs dedicados. Embora isso permita uma redução de custo de até cinco vezes, torna o sistema dependente do desempenho da CPU principal. Com o dimensionamento correto, o Asterisk é capaz de lidar com grandes volumes. Se ainda quiser liberar a CPU principal dessas tarefas, você também pode usar cancelamento de eco em hardware e até placas de transcodificação, como a Sangoma (antiga Digium) TC400B baseada em DSPs.

## Asterisk Architecture

Esta seção explicará como funciona a arquitetura do Asterisk. A figura abaixo mostra a arquitetura básica do Asterisk. Em seguida, explicaremos conceitos relacionados à arquitetura, incluindo canais, codecs e aplicações.

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

Um canal é o equivalente a uma linha telefônica, mas em formato digital. Normalmente consiste em um sistema de sinalização analógico ou digital (TDM) ou em uma combinação de codec e protocolo de sinalização (ex.: SIP‑GSM, IAX‑uLaw). Inicialmente, todas as conexões telefônicas eram analógicas e suscetíveis a eco e ruído. Mais tarde, a maioria dos sistemas foi convertida para sistemas digitais, com o som analógico convertido para um formato digital usando modulação por código de pulso (PCM) na maioria dos casos. Esse formato permite a transmissão de voz em 64 kilobits/segundo sem compressão.

Canais que se conectam à Public Switched Telephone Network (PSTN):

- `chan_dahdi`: cartões TDM analógicos (FXO/FXS) e digitais (E1/T1/PRI) da Sangoma (antiga Digium), Xorcom e outros. Construídos separadamente contra DAHDI — veja o capítulo *Legacy channels*.

Canais que se conectam ao Voice over IP:

- `chan_pjsip`: SIP — o driver de canal SIP principal e único no Asterisk 22 LTS. String de discagem: `PJSIP/endpoint_name`. (**Note:** o antigo `chan_sip` foi removido no Asterisk 21 e não existe no Asterisk 22. Veja *Building your first PBX with PJSIP* para configuração.)
- `chan_iax2`: o protocolo IAX2 — ainda incluído no Asterisk 22, mas legado; SIP/PJSIP é preferido para novas implantações. String de discagem: `IAX2/peer`.
- `chan_unistim`: telefones Nortel/Avaya UNISTIM. Ainda disponíveis (suporte estendido), mas raramente usados.

Os canais VoIP mais antigos não fazem mais parte de uma compilação padrão do Asterisk 22: `chan_h323` (H.323) sobrevive apenas como o add‑on comunitário `ooh323`, e `chan_mgcp` (MGCP) e `chan_skinny` (Cisco SCCP) foram descontinuados e removidos do conjunto de canais moderno. Se for necessário interoperar com esses protocolos, um gateway à frente do Asterisk é a abordagem usual.

Canais diversos:

- **Local**: um pseudo‑canal (integrado ao núcleo) que faz loop de volta ao dialplan em um contexto diferente — útil para roteamento recursivo e para distribuir uma chamada para múltiplos destinos. String de discagem: `Local/extension@context`.

### Codec and codec translation

Normalmente tentamos colocar o maior número possível de conexões de voz em uma rede de dados. Codecs habilitam novos recursos na voz digital, incluindo compressão, que é uma das características mais importantes, pois permite taxas de compressão superiores a 8 para 1. Muitos codecs também definem recursos como detecção de atividade de voz (supressão de silêncio), ocultação de perda de pacotes e geração de ruído de conforto, embora o próprio Asterisk não gere ruído de conforto nem execute supressão de silêncio. Vários codecs estão disponíveis para o Asterisk e podem ser traduzidos de forma transparente de um para outro. Internamente, o Asterisk usa slinear como formato de fluxo quando precisa converter de um codec para outro. Alguns codecs no Asterisk são suportados apenas em modo pass‑through; esses codecs não podem ser traduzidos. Para verificar quais codecs estão instalados no seu sistema, você pode usar o comando de console:

```
CLI>core show translation
```

The following codecs are supported:

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - Only pass-through mode
- G.726 - (16/24/32/40kbps)
- G.729 - Binary codec module distributed by Sangoma; the download is free of charge, but lawful use requires purchasing a per-channel license (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocols

Sending data from one phone to another should be easy provided that the data find a path to the other phone on their own. Unfortunately, it doesn't happen this way, and a signaling protocol is necessary in order to establish connections between phones, discover end devices, and implement telephony signaling. SIP is the dominant signaling protocol in modern deployments and is the only SIP channel available in Asterisk 22 LTS (via chan_pjsip). IAX2 is still available but considered legacy. Asterisk supports the following protocols.

- SIP — via `chan_pjsip`
- IAX2 — legacy, still ships in Asterisk 22
- UNISTIM — Nortel/Avaya phones (extended support)
- H.323, MGCP, and SCCP (Cisco Skinny) — legacy protocols no longer in a standard Asterisk 22 build (H.323 only via the community `ooh323` add-on)

### Applications

To bridge calls from one phone to another, the application dial() is used. Most Asterisk features (e.g., voicemail and conferencing) are implemented as applications. You can see available Asterisk applications by using the core show applications console command.

```
CLI>core show applications
```

Você pode adicionar aplicações de complementos do Asterisk, de provedores terceiros ou até mesmo aquelas que você desenvolve você mesmo.

## Visão geral de um sistema Asterisk

Asterisk é um PBX de código aberto que funciona como um PBX híbrido, integrando tecnologias como TDM e telefonia IP. O Asterisk está pronto para implementar funcionalidades como resposta de voz interativa (IVR) e distribuição automática de chamadas (ACD); além disso, como mencionado anteriormente, está aberto ao desenvolvimento de novas aplicações. Esta figura mostra como o Asterisk se conecta ao PSTN e a PBXs existentes usando interfaces analógicas e digitais, bem como suporta telefones analógicos e IP. Ele pode atuar como um soft‑switch, gateway de mídia, correio de voz e conferência de áudio e também possui música em espera integrada.

![Visão geral de um sistema Asterisk](../images/01-introduction-fig02.png)

## Comparando o mundo antigo e o novo

No modelo de soft‑switch antigo, todos os componentes eram vendidos separadamente, o que significava que você precisava adquirir cada componente individualmente e então integrá‑los ao ambiente PBX ou soft‑switch. Os custos e riscos eram altos e a maior parte do equipamento era proprietário.

![O mundo antigo: componentes comprados e integrados separadamente](../images/01-introduction-fig03.png)

### Telefonia usando Asterisk

Todas as funções são integradas na plataforma Asterisk no mesmo ou em diferentes servidores, de acordo com o dimensionamento, e todas são licenciadas sob GPL. Às vezes é mais fácil instalar o Asterisk do que licenciar alguns dos IP‑PBXs mais populares

![Telefonia usando Asterisk: as funções são integradas](../images/01-introduction-fig04.png)

## Building a test system

When implementing an Asterisk solution, our first step is generally to build a test system. The goal is a minimal **1×1 PBX** — one phone that can call another — so you can try out endpoints, dialplan, and features before touching production. Today this is entirely software: you do not need any telephony hardware.

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### The modern way: a software lab (recommended)

The fastest test system is Asterisk 22 running in a container or virtual machine, with **softphones** for the endpoints and, optionally, a **SIP trunk** to reach the public network:

- **Asterisk 22** on a small Linux box, VM, or Docker container. This book ships a ready-made Docker lab (see the lab guide) that boots a fully configured Asterisk 22 with a single command — no compilation, no hardware.
- **Two softphones** registered as PJSIP endpoints, so you can place a real call between them. Throughout this book we use the **SipPulse Softphone** (free download: <https://www.sippulse.com/produtos/softphone>), available for desktop and mobile.
- **A SIP trunk** (optional) from a VoIP provider, for when you want to reach the PSTN. No card and no analog line — just credentials.

This is how every example in this book is built and verified, and you can reproduce it on any laptop.

### The legacy way: analog/digital cards

Before VoIP, a test PBX needed physical interfaces: an **FXO** port to connect to an existing telephone line and an **FXS** port to connect an analog phone, which together gave you a 1×1 PBX. A single card carrying one FXO and one FXS interface was the classic starter kit. These DAHDI-based cards (from Sangoma, formerly Digium) still exist for sites that must terminate analog or T1/E1 lines, but they are niche today — most deployments are pure VoIP. If you only need to connect analog phones or lines, see the *Legacy Channels* chapter; otherwise you can skip telephony hardware entirely.

## Asterisk scenarios

Asterisk can be used in several different scenarios. We will list some of them and explain the advantages and possible limitations of each.

### IP PBX

The most common scenario is the installation of a new or the replacement of an existing PBX. If you compare Asterisk with some other alternatives, you will find it to be cheaper and richer in features than most PBXs currently available on the market. Several companies are now changing their specifications to Asterisk instead of other brand-name PBXs.

![Asterisk as an IP PBX](../images/01-introduction-fig06.png)

### IP-enabling legacy PBXs

The following image illustrates one of the most commonly used setups. Large companies generally do not want to take significant risk when investing in new technologies and simultaneously wish to preserve their investments in legacy equipment. IP-enabling legacy PBX can be very expensive; thus, connecting an Asterisk PBX using T1/E1 lines can be a good alternative for cost-conscious customers. Another benefit is the possibility of connecting to a VoIP service provider with better telephony rates.

![IP-enabling a legacy PBX](../images/01-introduction-fig07.png)

### Toll Bypass

A very useful application for VoIP is connecting branch offices over the Internet or a WAN. Using an existing data connection allows you to bypass toll charges incurred in telecommunication connections between headquarters and branch offices.

![Toll bypass between offices over a WAN](../images/01-introduction-fig08.png)

### Application Server (IVR, Conference, Voicemail)

Asterisk can be used as an application server for the existing PBX or be directly connected to PSTN. Asterisk offers services such as voicemail, fax reception, call recording, IVR connected to a database, and an audio conferencing server. If you integrate voicemail and fax into an existing e-mail server, you will have a unified messaging system, which is usually an expensive solution. Using Asterisk as an application server provides extreme cost reduction compared to other solutions.

![Asterisk as an application server](../images/01-introduction-fig09.png)

### Media Gateway

Most voice-over IP service providers use an SIP proxy to host all registration, location, and authentication of SIP users. They still have to send calls to the PSTN directly or route it through a wholesale call termination provider using an SIP or H.323 voice-over IP connection. Asterisk can act as a back-to-back user agent (B2BUA) or media gateway, replacing very expensive soft switches or media gateways. Compare the price of a four E1/T1 gateway from the main market manufacturers with Asterisk. The Asterisk solution can cost several times less than other solutions and is capable of translating signaling protocols (H.323, SIP, IAX…) and codecs (G.711, G.729…).

![Asterisk as a media gateway](../images/01-introduction-fig10.png)

### Contact Center Platform

A contact center is a very complex solution that combines several technologies, such as automatic call distribution (ACD), interactive voice response (IVR), and call supervision. Basically, three types of contact centers are available: inbound, outbound, and blended.

Inbound contact centers are very sophisticated and usually require ACD, IVR, CTI, recording, supervision, and reports. Asterisk has a built-in ACD to queue the calls. IVR can be done using Asterisk Gateway Interface (AGI) or internal mechanisms such as the application background(). Computer telephony integration (CTI) is achieved using Asterisk Manager Interface (AMI); recording and reporting are built in to Asterisk.

For an outbound contact center, a predictive or power dialer is one of the main components. Although several dialers are available for the open-source Asterisk, it is not hard to build your own for the platform if you so desire. A blended contact center allows simultaneous inbound and outbound operation, saving money by ensuring better use of the agent's time. It is possible to use Asterisk and its ACD mechanism to implement a blended solution.

![An Asterisk contact-center platform](../images/01-introduction-fig11.png)

## Encontrando informações e ajuda

Esta seção fornecerá algumas das principais fontes de informação relacionadas ao Asterisk.

- Site oficial do Asterisk: <https://www.asterisk.org> Aqui você pode encontrar informações sobre:
- Documentação & Wiki -> <https://docs.asterisk.org>
- Fórum da comunidade -> <https://community.asterisk.org>
- Rastreamento de bugs -> <https://github.com/asterisk/asterisk/issues>
- Wiki (legado, em grande parte substituído por docs.asterisk.org) -> <https://wiki.asterisk.org>

### Fórum da comunidade

O fórum da comunidade Asterisk substituiu em grande parte as antigas listas de discussão e é o local para fazer perguntas. Tente reunir o máximo de informações possível antes de postar. Ninguém o ajudará se você não tiver feito sua lição de casa — tente ao menos uma vez resolver o problema por conta própria.

- <https://community.asterisk.org>

## Summary

Asterisk é um software licenciado sob a GPL que permite que um PC comum atue como uma poderosa plataforma de IP PBX. Mark Spencer, da Digium, criou o Asterisk no final dos anos 1990, e a Digium se sustentou vendendo hardware relacionado ao Asterisk e produtos comerciais. A Digium foi adquirida pela Sangoma Technologies em 2018; a Sangoma agora patrocina o desenvolvimento do Asterisk. O design da interface de hardware originou‑se no projeto Zapata desenvolvido por Jim Dixon, que deu origem ao DAHDI.

A arquitetura do Asterisk possui os seguintes componentes principais:

- CHANNELS: Analógico, digital ou voice‑over IP. No Asterisk 22 LTS, o SIP é tratado exclusivamente por `chan_pjsip`.
- PROTOCOLS: Protocolos de comunicação, responsáveis por sinalizar as chamadas, incluindo SIP (via PJSIP), H.323, MGCP e IAX2.
- CODECS: Traduzem formatos digitais de voz permitindo compressão e ocultação de perda de pacotes. Observe que o próprio Asterisk não realiza supressão de silêncio (detecção de atividade de voz) nem geração de ruído de conforto; quando os endpoints usam VAD, o ruído de conforto deve ser desativado no lado do cliente.
- APPLICATIONS: Responsáveis pela funcionalidade de PBX do Asterisk. Conferência, correio de voz e fax são exemplos de aplicações do Asterisk.

O Asterisk pode ser usado em diversos cenários, desde um pequeno IP PBX até um centro de contato sofisticado. Você pode encontrar ajuda facilmente em www.asterisk.org e docs.asterisk.org.

## Quiz

1. Qual empresa adquiriu a Digium em 2018 e agora atua como principal responsável pelo projeto open‑source Asterisk?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. No Asterisk 22 LTS, qual driver de canal fornece conectividade SIP?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. Verdadeiro ou Falso: O driver de canal `chan_sip` foi removido no Asterisk 21 e não está presente em uma compilação padrão do Asterisk 22.

4. Quais dos seguintes canais/protocolos **não fazem mais parte** de uma compilação padrão do Asterisk 22? (Marque todas as opções que se aplicam.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, sobrevivendo apenas como o add‑on comunitário `ooh323`)

5. A arquitetura de hardware do projeto Zapata, originalmente chamada Zaptel, foi posteriormente renomeada para ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Quando o Asterisk precisa converter áudio de um codec para outro, por qual formato interno de fluxo ele realiza a tradução?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. De acordo com o capítulo, qual é a situação de licenciamento do módulo de codec G.729 distribuído pela Sangoma?
   - A. É GPL e completamente gratuito para qualquer uso.
   - B. O download é gratuito, mas o uso legal requer a compra de uma licença por canal.
   - C. Não pode ser obtido de forma alguma sem comprar o Asterisk Business Edition.
   - D. Só funciona em modo pass‑through e não pode ser instalado.

8. Qual aplicação do Asterisk é usada para conectar uma chamada de um telefone a outro?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. O que é o canal `Local` no Asterisk?
   - A. Uma interface de hardware FXS para telefones analógicos.
   - B. Um tronco SIP para um provedor de serviços local.
   - C. Um pseudo‑canal que devolve a chamada ao dialplan em um contexto diferente.
   - D. Um codec usado para chamadas on‑net.

10. Em qual cenário de uso o Asterisk atua como um back‑to‑back user agent (B2BUA), traduzindo entre protocolos de sinalização e codecs para substituir soft switches caros?
    - A. Habilitação IP de um PBX legado
    - B. Bypass de tarifas
    - C. Media Gateway
    - D. Plataforma de Contact Center

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
