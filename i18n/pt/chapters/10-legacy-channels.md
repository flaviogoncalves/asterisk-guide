# Legacy channels: analog, TDM & IAX2

Em um mundo puro‑VoIP em 2026, os tipos de canal deste capítulo são cada vez mais raros: a maioria das novas implantações são trunks SIP e endpoints PJSIP sobre Ethernet, sem nenhum hardware de telefonia. O Asterisk 22, no entanto, ainda oferece suporte total à maioria deles. A conectividade analógica (FXO/FXS) e digital TDM (E1/T1/ISDN PRI/BRI) é fornecida através do DAHDI — a pilha de drivers originalmente desenvolvida pela Digium, que foi adquirida pela Sangoma em 2018, após os drivers Zaptel serem renomeados devido a uma disputa de marca. A conectividade servidor‑para‑servidor via IAX2 é fornecida por `chan_iax2`, que ainda é distribuído e suportado, mas agora é firmemente um protocolo legado.

Este capítulo também reúne o material **legacy SIP**: o antigo driver `chan_sip` e sua configuração `sip.conf` — removidos no Asterisk 21 e inexistentes no Asterisk 22 — juntamente com um guia completo para migrar um sistema `sip.conf` existente para PJSIP. Se você está operando uma loja puramente SIP no PJSIP sem placas de telefonia, sem trunks IAX2 e sem legacy `sip.conf` para converter, pode pular este capítulo com segurança.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Conectar o Asterisk a linhas analógicas e telefones com interfaces FXO/FXS através do DAHDI;
- Reconhecer a conectividade digital TDM (E1/T1, ISDN PRI/BRI) e como ela é configurada;
- Configurar IAX2 (`chan_iax2`) para troncos servidor‑para‑servidor e entender por que ele agora é legado;
- Identificar o driver `chan_sip` aposentado e a sintaxe `sip.conf` que você ainda pode encontrar; e
- Migrar um sistema `chan_sip`/`sip.conf` existente para o PJSIP.

## Canais analógicos (FXO/FXS)

A partir do Asterisk 22, os cartões de telefonia analógica e DAHDI continuam totalmente suportados, e o DAHDI ainda é compilado contra kernels atuais. A maioria das novas implantações, no entanto, é puramente VoIP (trunks SIP, PJSIP), de modo que o hardware analógico/TDM agora é uma escolha de nicho — encontrado principalmente em ambientes legados, conectividade PSTN rural ou mercados regulados. Tudo abaixo ainda se aplica a esses cenários.

Existem várias maneiras de conectar à rede pública de telefonia comutada (PSTN). A melhor forma depende de como a operadora disponibiliza essa conexão na sua região. A maneira mais simples é usar uma linha analógica, semelhante à linha que você usa em casa. Nesta seção, mostraremos como configurar cartões analógicos da Sangoma™ (antiga Digium™) e Xorcom™.

### Objetivos

Ao final deste capítulo você deverá ser capaz de:

- Reconhecer os principais termos e siglas de telefonia;
- Entender quando usar circuitos digitais e analógicos;
- Reconhecer a diferença entre FXS e FXO; e
- Configurar o Asterisk para FXS e FXO.

### Noções básicas de telefonia

A maioria das implementações analógicas usa um par de linhas chamadas tip e ring. Quando um loop é fechado, o telefone recebe o tom de discagem do comutador de telecomunicações (ou do PBX privado). O sinal de discagem mais usado é o loop-start; há outros tipos menos comuns, incluindo ground start, que é usado em vários países. As três categorias de sinalização são:

- Sinalização de supervisão
- Sinalização de endereço
- Sinalização de informação

#### Sinalização de supervisão

Os principais sinais de supervisão são on-hook, off-hook e ringing.

- **On-Hook** – Quando o usuário coloca o telefone no gancho, o PBX interrompe e não permite que a corrente elétrica passe. Nesse estado, o circuito é chamado on-hook. Nessa posição, apenas o toque está ativo.
- **Off-Hook** – Antes de iniciar uma chamada, o telefone precisa passar para o estado off-hook. Retirar o fone do gancho fecha o loop e indica ao PBX que o usuário pretende fazer uma chamada. Ao receber essa indicação, o PBX gera um tom de discagem, indicando ao usuário que está pronto para aceitar o endereço de destino (ou seja, o número de telefone).
- **Ringing** – Quando um usuário chama outro telefone, gera uma tensão no toque que avisa o outro usuário sobre a chamada recebida. A sinalização varia por país, com tons diferentes para diferentes países.

Você pode personalizar os tons do Asterisk para o seu país modificando o arquivo indications.conf. Por exemplo:

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### Sinalização de Endereço

Você pode usar dois tipos de sinalização para discagem. O primeiro e mais comum é dual tone multi-frequency (dtmf) enquanto o outro é discagem por pulso (usada em telefones antigos de disco). Os telefones têm um teclado para discagem, e cada botão está associado a duas frequências: uma alta e uma baixa. No caso da sinalização dtmf, a combinação desses tons indica qual dígito está sendo pressionado. MFC/R2 usa um tom multifrequência diferente do dtmf.

#### Sinalização de informação

O sinal de informação mostra o progresso da chamada e diferentes eventos.

- Tom de discagem
- Tom ocupado
- Tom de retorno
- Congestão
- Número inválido
- Tom de confirmação

### Interfaces PSTN

Como no caso dos PBXs antigos, costuma ser necessário conectar o Asterisk PBX ao PSTN. Aqui mostraremos como fazer isso. Normalmente você tem três opções para linhas telefônicas.

- Analog: A forma mais comum para residências e pequenas empresas, geralmente fornecida com um par metálico de linhas de cobre.  
- Digital: Usado quando muitas linhas são necessárias. Uma linha digital geralmente é entregue por um CSU/DSU ou um multiplexador de fibra. O conector do usuário final costuma ser um RJ45. Em alguns países, linhas E1 são entregues usando dois conectores coaxiais BNC; nesse caso, você precisará de um adaptador em forma de balão para conectar o plug RJ45 à placa de telefonia.  
- SIP: Esta opção foi desenvolvida recentemente. A linha telefônica é fornecida usando uma conexão de dados com sinalização SIP (VoIP). Esta é uma boa opção para usar com Asterisk, pois você não precisará comprar uma placa de telefonia. As chamadas telefônicas serão entregues diretamente na porta Ethernet. Outra vantagem é que você pode liberar recursos da sua CPU ao evitar a transcodificação de codecs.

### Interfaces Analógicas FXS, FXO e E&M interfaces

Vários tipos de interfaces analógicas estão disponíveis. É fundamental entender as diferenças entre essas interfaces para aprender como conectar à rede telefônica, bem como a outros PBXs. Aqui, mostraremos a interface E&M. Embora não esteja atualmente disponível para Asterisk e tenha sido descontinuada por vários fornecedores, você pode encontrar roteadores e PBXs com esse tipo de interface, portanto é melhor saber com o que está lidando.

#### Interfaces Foreign eXchange (FX)

FX interfaces are analog. The term “Foreign eXchange” is applied to access trunks to a PSTN central office (CO). Foreign eXchange Office (FXO)

![Asterisk entre um telefone analógico (FXS) e a linha da operadora (FXO): o lado FXS fornece tom de discagem e toque ao telefone, enquanto o lado FXO obtém o tom de discagem da central.](../images/10-legacy-fig01.png)

A interface FXO é usada para conectar a um central office (CO) ou a extensão de outro PBX. Ela se comunica diretamente com uma linha telefônica proveniente da PSTN. Outra opção é conectar a interface FXO a um PBX existente, permitindo a comunicação entre Asterisk e o PBX legado. Conectar o Asterisk a uma porta de PBX e fornecer uma extensão remota usando VoIP é frequentemente referido como uma extensão off‑promises (OPX). Uma interface FXO recebe um tom de discagem. **Foreign eXchange Station (FXS)** A interface FXS alimenta um telefone analógico, modem ou fax. O FXS fornece o tom de discagem e a energia para o telefone.

#### Sinalização de tronco

- Loop-Start
- Ground-Start
- Kewlstart

O uso de sinalização kewlstart no Asterisk é quase padrão. Kewlstart não é sinalização em si, mas adiciona inteligência ao circuito monitorando o que está acontecendo do outro lado. Kewlstart é baseado em loop-start. A maioria dos switches não suporta esse recurso, que é usado para obter a notificação de desligamento.

- Loopstart: Usado na maioria das linhas analógicas, permite que o telefone indique “on-hook” e “off-hook” e que o interruptor indique “ring” e “no-ring”. Provavelmente é o que a maioria das pessoas tem em casa. O nome vem do fato de que a linha está sempre aberta. Quando você fecha o loop, o interruptor fornece um tom de discagem. Uma chamada recebida é sinalizada por uma tensão de toque de 100V sobre o par aberto.

![Asterisk operando como um gateway VoIP: uma porta FXO conecta-se a uma extensão de PBX legada enquanto um Asterisk remoto entrega essa linha a um telefone analógico via IP através de uma porta FXS (uma extensão fora das instalações, ou OPX).](../images/10-legacy-fig02.png)

- Groundstart: Semelhante ao Loopstart. Quando você deseja fazer uma chamada, um lado da linha é curto-circuitado. Quando o comutador identifica esse estado, ele inverte a tensão através do par aberto, e então o loop é fechado. Consequentemente, a linha primeiro se torna ocupada antes de ser oferecida ao chamador.
- Kewlstart: Adiciona inteligência aos circuitos, permitindo o monitoramento do outro lado. Kewlstart incorpora muitas vantagens do loop-start.

### Configuração de canais de telefonia Asterisk

Para configurar uma placa de interface de telefonia, vários passos são necessários. Neste capítulo, mostraremos três dos cenários mais comuns:

- Conexão analógica usando FXS
- Conexão analógica usando FXO
- Conexão de um Astribank™ com interfaces FXS e FXO

### Procedimento de Configuração (válido em ambos os casos)

Antes de escolher o hardware para o Asterisk, você deve considerar o número de chamadas simultâneas, serviços e codecs que serão instalados e habilitados. O Asterisk é uma aplicação intensiva em CPU, por isso recomendamos uma máquina dedicada para o Asterisk. O número de placas de interface instaladas no computador é limitado pelo número de slots e interrupções disponíveis. É preferível instalar uma única placa com oito interfaces de voz do que duas placas com quatro. Outra opção é usar um banco de canais USB, como o Xorcom Astribank. Recentemente, alguns fabricantes (por exemplo, CIANET) começaram a produzir bancos de canais TDMoE, facilitando ainda mais a conexão de dezenas de interfaces analógicas.

![A Xorcom Astribank: um rack-mount de 19 polegadas USB channel bank que expõe dezenas de portas FXS/FXO (aqui uma unidade de 32 portas) sem consumir slots PCI no host.](../images/10-legacy-fig03.png)

#### Exemplo 1: Instalação de um FXO e um FXS

Neste exemplo, usaremos uma placa de interface telefônica Sangoma TDM400 (anteriormente vendida como Digium TDM400) com um módulo FXS e um módulo FXO. Os passos necessários estão listados abaixo:

1. Instale a placa analógica FXS, FXO ou ambas.  
2. Configure o arquivo `/etc/dahdi/system.conf` (anteriormente `/etc/zaptel.conf`).  
3. Gere os arquivos de configuração usando `dahdi_genconf`.  
4. Carregue o driver para a interface DAHDI.  
5. Execute `dahdi_test` para verificar perdas de interrupção.  
6. Execute `dahdi_cfg` para configurar o driver.  
7. Configure o canal DAHDI no arquivo `chan_dahdi.conf`, então carregue o Asterisk.

##### Etapa 1: Instale a placa TDM400

O cartão TDM404P contém módulos FXS e FXO. Conecte os módulos FXS (S110M, verde) e FXO (X100M, vermelho). Se você estiver usando módulos FXS, conecte o cartão diretamente à fonte de alimentação usando um conector molex. Por favor, use proteção eletrostática antes de manusear cartões de interface para evitar danos ao hardware. Os cartões analógicos Sangoma (anteriormente Digium) também suportam um módulo de cancelamento de eco de hardware VPMADT032.

##### Etapa 2: Gere a configuração com dahdi_genconf

A boa notícia sobre a configuração é a nova utilidade `dahdi_genconf`, que detecta automaticamente e gera a configuração para interfaces DAHDI. A utilidade gera dois arquivos:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (com a `users` opção)
- Todos esses arquivos usam a opção `chan_dahdi full`

Before you can execute `dahdi_genconf`, it is important to configure the file `genconf_parameters` (often referred to as `gen_parameters.conf`):

![Um cartão analógico Sangoma/Digium TDM404P: até quatro módulos FXS ou FXO se conectam nas portas numeradas, com uma placa filha opcional de cancelamento de eco de hardware e um conector de alimentação dedicado de 12 V para módulos FXS.](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

O arquivo `genconf_parameters` permite que você personalize sua configuração. Os parâmetros mais importantes para linhas analógicas são:

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

Aviso: É necessário que você configure ao menos o algoritmo de cancelamento de eco para os canais. O parâmetro base_exten define o plano de discagem básico para extensões FXS. Nesse caso, o primeiro canal FXS receberá o número de extensão 4000, o segundo 4001, e assim por diante. O contexto no qual as linhas (context_phones) e os troncos (context_lines) são criados é muito importante. Após gerar os arquivos, você deve incluir o arquivo `/etc/asterisk/dahdi-channels.conf` no arquivo `/etc/asterisk/chan_dahdi.conf`:

```
#include dahdi-channels.conf
```

Note: O sinal de discagem analógico pode ser confuso; ele é sempre o inverso do cartão. Cartões FXS são sinalizados com FXO, enquanto cartões FXO são sinalizados com FXS. O Asterisk se comunica com esses dispositivos como se estivesse do lado oposto.

##### Step 3: Load kernel drivers

Agora você precisa carregar o módulo chan_dahdi e o driver de kernel do cartão correspondente. Use dahdi_hardware para detectar seu cartão e o nome do driver. Por exemplo:

| Card | Driver | Description |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 - PCI 3.3V |
| TE405P | wct4xxp | 4xE1/T1 - PCI 5V |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

Commands to load the drivers:

```
modprobe dahdi
modprobe wctdm
```

##### Etapa 4: Use o utilitário dahdi_test

Um utilitário importante é o dahdi_test, que é usado para verificar perdas de interrupção na placa DAHDI. Problemas de qualidade de áudio frequentemente estão relacionados a conflitos de interrupção. Para verificar se sua placa DAHDI não está compartilhando uma interrupção com outras placas, use o comando a seguir:

```
#cat /proc/interrupts
```

Você pode verificar o número de perdas de interrupção usando a ferramenta dahdi_test compilada com as placas DAHDI. Um valor abaixo de 99,987% indica possíveis problemas.

##### Step 5: Use the dahdi_cfg utility to configure the driver

DAHDI tem um sistema incomum para carregar os drivers. Primeiro configure o /etc/dahdi/system.conf e, em seguida, aplique essas configurações ao driver DAHDI usando dahdi_cfg. Neste caso, dahdi_cfg é usado para configurar o sinalização das interfaces FX. Para ver os resultados, você pode acrescentar “-vvvvv” ao comando para modo verboso.

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

If the channels were loaded successfully, you will see an output similar to the one shown above. Users often incorrectly configure chan_dahdi.conf with inverted signaling between channels. If this happens, you will see a message like the one shown below:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After successfully configuring the hardware, you can proceed to Asterisk configuration.

##### Step 6: Configure the /etc/asterisk/chan_dahdi.conf file

It sounds strange, but after configuring the /etc/dahdi/system.conf, you configured the card itself. DAHDI can be used for other purposes, like routing and SS7. To use it with Asterisk, you must configure the Asterisk DAHDI channels. Every channel in Asterisk has to be defined; SIP/PJSIP channels are defined in pjsip.conf (note: chan_sip and sip.conf were removed in Asterisk 21) while TDM channels are defined in chan_dahdi.conf. This creates the logical TDM channels to be used in your dial plan.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### Opções de configuração

Várias opções estão disponíveis no arquivo chan_dahdi.conf. Descrever todas as opções seria entediante e contraproducente; em vez disso, focaremos nos principais grupos de opções para facilitar a compreensão.

#### Opções gerais (independente de canal)

Essas opções funcionam para qualquer canal: context: Define o contexto de entrada.

```
context=default
```

channel: Define canal ou intervalo de canais. Cada definição de canal herdará opções definidas antes da declaração. Os canais podem ser identificados individualmente ou na mesma linha por separação por vírgula. Intervalos podem ser definidos usando “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Permite que canais sejam tratados como um grupo. Se você discar um número de grupo em vez de um número de canal, o primeiro canal disponível será usado. Se os canais são telefones, ao chamar um grupo, todos os telefones tocarão simultaneamente. Com vírgulas, você pode especificar mais de um grupo para o mesmo canal.

```
group=1
group=3,5
```

language: Ativa a internacionalização e configura um idioma. Esse recurso configurará as mensagens do sistema para um idioma específico. O inglês é o único idioma com prompts completos disponíveis através da instalação padrão. musiconhold: Seleciona a classe de música em espera.

#### Opções de Caller ID

Existem muitas opções de callerid. Algumas podem ser desativadas, embora a maioria esteja habilitada por padrão. usecallerid: Habilita ou desabilita a transmissão do callerid para os canais subsequentes (Yes/No). Nota: Se o seu sistema receber dois toques antes de atender, tente desativar esse recurso. Ele deve atender imediatamente. hidecallerid: Define se o callerid de saída deve ser ocultado ou não (Yes/No). callerid: Configura uma string de callerid para um canal específico. O caller pode ser configurado com asreceived. Isso é usado principalmente em interfaces de trunk para indicar o callerid recebido.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Suporta callerid durante chamada em espera. useincomingcalleridondahditransfer: Usa o callerid de entrada em uma transferência.

#### Chamada em Espera

Asterisk suporta chamada em espera em canais FXS. O usuário receberá um tom de espera se alguém tentar a extensão. Para habilitar a chamada em espera:

```
callwaiting=yes
```

Para suportar callerid em call waiting:

```
callwaitingcallerid=yes
```

#### Opções de qualidade de áudio

Ajustar a cancelamento de eco é meio técnico, meio arte. Essas opções ajustam certos parâmetros do Asterisk que afetam a qualidade de áudio nos canais DAHDI. Elas podem ajudar a melhorar a qualidade de áudio nas interfaces analógicas.

#### O utilitário fxotune

O fxotune é um utilitário usado para afinar certos parâmetros dos módulos FXO. Esse ajuste fino é necessário para corrigir o desajuste de impedância causado pelo híbrido. O utilitário possui três modos de operação:

- Detection (-i): detecta e corrige os canais FXO existentes e salva a configuração para

```
fxotune.conf
```

- Modo de despejo (-d): gera os arquivos de forma de onda para fxotune_dump.vals
- Modo de inicialização (-s): lê o arquivo fxotune.conf e o aplica aos módulos FXO

É importante entender que você deverá inserir a instrução fxotune –s na carga do sistema antes de iniciar o Asterisk.

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### Cancelamento de eco

A maioria dos algoritmos de cancelamento de eco opera gerando múltiplas cópias do sinal recebido, nas quais cada uma é atrasada por um intervalo de tempo específico. O número de taps do filtro determina o tamanho do atraso de eco que precisa ser cancelado. Essas cópias atrasadas são então ajustadas e subtraídas do sinal recebido. O truque é ajustar apenas o sinal atrasado para remover o eco sem usar muitos ciclos de CPU. Do ponto de vista do usuário, é importante escolher um algoritmo de cancelamento de eco adequado. O padrão é MG2; porém, duas outras opções estão disponíveis: o High Performance Echo Cancellation (HPEC) da Sangoma (antiga Digium) e o cancelamento de eco de código aberto (OSLEC) desenvolvido por David Rowe.

OSLEC (https://www.rowetel.com/?page_id=454) foi incorporado ao kernel Linux — ele reside na área `drivers/staging/echo` do kernel — e o DAHDI é compilado contra ele em vez de distribuir um download separado. Para mudar o algoritmo de cancelamento de eco, defina o parâmetro `echo_can` em `/etc/dahdi/system.conf`. Por exemplo:

```
echo_can=oslec
```

O cancelamento de eco no Asterisk é controlado por três parâmetros no arquivo /etc/asterisk/chan-

```
dahdi.conf.
```

- **echocancel**: Desativa ou habilita a cancelamento de eco. Você deve manter esse recurso habilitado. Aceita “yes” ou o número de taps. (Explicação: Como funciona o cancelamento de eco? A maioria dos algoritmos de cancelamento de eco opera gerando múltiplas cópias de um sinal recebido, cada uma atrasada por um pequeno intervalo. Esse pequeno fluxo é chamado de “tap”. O número de taps determina o atraso de eco que pode ser cancelado. Essas cópias são atrasadas, ajustadas e subtraídas do sinal original. O truque é ajustar o sinal atrasado exatamente ao necessário para remover o eco.)
- **echocancelwhenbridged**: Habilita ou desabilita o cancelador de eco durante uma chamada TDM pura. Normalmente isso não é necessário.
- **rxgain**: Ajusta o ganho de recepção de áudio para aumentar ou diminuir o volume de recepção (‑100% a 100%).
- **txgain**: Ajusta o ganho de transmissão de áudio para aumentar ou diminuir o volume de transmissão (‑100% a 100%).

Por exemplo:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Opções de faturamento

Essas opções alteram como as informações de chamadas são registradas no banco de dados de registros detalhados de chamadas (CDR). amaflags: Configura as flags AMA que afetam a categorização do CDR. Aceita os seguintes valores:

- billing
- documentation
- omit
- default

accountcode: Configura um código de conta para um canal específico. Pode conter qualquer valor alfanumérico—geralmente o departamento ou nome do usuário.

```
accountcode=finance
amaflags=billing
```

### Opções de progresso da chamada

Esses itens são usados para obter informações sobre o progresso da chamada. Em interfaces públicas, pode ser útil detectar o progresso da chamada e determinar se ela foi atendida ou está ocupada. A detecção de ocupado é altamente experimental e regulada por parâmetros específicos.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

Esses parâmetros (acima) especificam se a interface tentará detectar o tom de ocupado, quantos tons serão usados para a detecção bem‑sucedida e qual é o padrão de ocupado. A detecção de ocupado é em grande parte experimental, e alguns parâmetros adicionais podem ser alterados no Makefile. Para detectar a resposta de uma chamada, que é essencial para faturamento preciso, é possível usar a inversão de polaridade para sinalizar o momento exato da resposta. Isso é importante se você pretende cobrar a chamada ou apenas deseja ter um faturamento preciso para comparação. Normalmente, é necessário entrar em contato com a operadora telefônica para solicitar esse serviço.

```
answeronpolarityswitch=yes
```

Em alguns países, também é possível detectar o término da chamada usando a inversão de polaridade como também.

```
hanguponpolarityswitch=yes
```

#### Opções para telefones

Essas opções são usadas para telefones conectados às interfaces FXS. Todas as funcionalidades fornecidas aos telefones analógicos conectados diretamente às interfaces DAHDI são controladas pelo Asterisk.

- **adsi** (Analog Display Services Interface): Conjunto de padrões de telecomunicações usado por algumas operadoras para oferecer serviços como compra de ingressos.
- **cancallforward**: Habilita ou desabilita o encaminhamento de chamadas (*72 para habilitar e *73 para desabilitar).
- **calleridcallwaiting**: Habilita a exibição de callerid recebida durante um aviso de chamada em espera (Sim/Não).
- **immediate**: No modo imediato, em vez de fornecer um tom de discagem, o canal salta imediatamente para a extensão "s" no contexto definido. Isso é usado para criar linhas diretas.
- **threewaycalling**: Habilita ou desabilita a conferência de três vias.
- **mailbox**: Avisa o usuário sobre mensagens de voicemail disponíveis. Pode ser um sinal audível ou um indicador visual (se o telefone suportar esse recurso). O argumento é o número da caixa de correio.
- **callgroup**: Agrupa telefones para discagem ou para captura de chamada.
- **pickupgroup**: Grupo de telefones para captura de chamada.

### Comandos úteis do CLI DAHDI

Uma vez que o Asterisk esteja em execução com os canais DAHDI carregados, você pode inspecionar o status dos canais a partir do CLI do Asterisk. Esses comandos permanecem atuais no Asterisk 22.

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### Formato de canal DAHDI

Canais DAHDI usam o seguinte formato no dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Por exemplo:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## Canais digitais (E1/T1/PRI / TDM)

Como o Asterisk 22, DAHDI e libpri permanecem totalmente suportados, mas os troncos digitais TDM (E1/T1/ISDN PRI) estão sendo substituídos cada vez mais por troncos SIP em novas implantações. Esta seção permanece totalmente aplicável onde a conectividade TDM é necessária; em ambientes greenfield, o trunking SIP (Chapter 3) geralmente entrega a mesma densidade de canais sem hardware de telefonia.

Canais digitais são extremamente comuns, portanto você precisará aprender a implementar esses canais se quiser focar em grandes clientes. Quando o número de canais é alto—geralmente mais de 8—é bastante comum usar interfaces digitais como T1/E1/J1. T1 é muito comum nos EUA, enquanto E1 é comum na Europa e J1 no Japão. Esses tipos de canais permitem uma boa densidade de circuitos—24 por canal T1 e 30 para canais E1.

Na América Latina, China e África, é comum usar um tipo de sinalização associada ao canal (CAS) conhecido como MFC/R2. Este capítulo examinará como implementar MFC/R2 usando a biblioteca OpenR2. Nos EUA e na Europa, Integrated Services Digital Networks (ISDN) PRI é a sinalização mais comum. O capítulo também abordará ISDN Basic Rate Interface (BRI), que é muito comum na Europa em aplicações de médio alcance.

Todos os exemplos do livro concentram‑se nos canais DAHDI. Alguns cartões são implementados usando canais proprietários, portanto, verifique com o fabricante para obter mais detalhes sobre como configurar seu cartão específico.

### Objetivos

Ao final deste capítulo, você será capaz de:

- Reconhecer os principais termos usados em telefonia digital
- Diferenciar a sinalização CAS e CCS
- Diferenciar a sinalização R2 e ISDN
- Configurar interfaces com sinalização ISDN
- Configurar interfaces com sinalização R2

### Linhas digitais E1/T1

Linhas digitais E1/T1 são uma opção sempre que você precisa implementar um grande número de canais. Um único circuito E1 é capaz de 30 chamadas simultâneas, e você pode ter recursos como discagem direta interna (DID), Identificação de Chamador (Caller ID) e sinalização avançada. A linha E1/T1 pode chegar à sua empresa de várias maneiras usando par trançado, fibra e micro-ondas, dependendo do seu país. Linhas digitais são entregues à sua empresa usando UTP, fibra ou micro-ondas. Modems e multiplexadores (MUX) são usados para entregar a linha física. A conexão a uma linha T1 é sempre baseada em um conector RJ45. No entanto, linhas E1 também podem ser provisionadas usando BNC. É muito importante saber, com antecedência, o tipo de conector que você receberá, principalmente em linhas E1. Normalmente todo o equipamento até o RJ45 é fornecido pela TELCO.

![Como os circuitos E1/T1 são provisionados: a operadora pode entregar o tronco via cobre UTP (modem HDSL para E1, ou conexão direta de placa para T1), via fibra óptica através de um multiplexador óptico, ou via link de rádio micro-ondas](../images/10-legacy-fig05.png)

![UTP ou BNC? A maioria das placas digitais usa conectores RJ45 (UTP), mas algumas linhas E1 são entregues em coaxial duplo BNC, caso em que um balun é necessário para adaptar o par coaxial ao conector RJ45 da placa.](../images/10-legacy-fig06.png)

#### Como a voz é convertida em bits?

O sinal analógico é amostrado 8,000 vezes por segundo para criar uma versão digital da voz analógica. Essa codificação é conhecida como pulse code modulation (PCM). Nos EUA e no Japão, o sinal é codificado usando law (no Asterisk, referido como ulaw). No resto do mundo, a codificação é alaw.

![Modulação por código de pulso (PCM): o sinal de voz analógico de 4 kHz é amostrado 8.000 vezes por segundo (Nyquist) e codificado em um fluxo digital de bits de 64 Kbps.](../images/10-legacy-fig07.png)

#### Multiplexação por Divisão de Tempo

Linhas analógicas fazem sentido quando você precisa de apenas alguns canais. Ao usar multiplexação por divisão de tempo (TDM), é possível colocar múltiplos canais em uma única conexão de dados. Quando você deseja um grande número de circuitos, a operadora normalmente fornece um tronco digital, que é um circuito de dados no qual a voz é transportada em formato digital usando PCM. Cada intervalo de tempo usa 64 Kbps de largura de banda para transportar um único canal de voz.

![Multiplexação por divisão de tempo em E1 e T1: um quadro E1 transporta 32 timeslots a 2048 Kbps (DS0 #0 para sincronização de quadro, DS0 #16 para sinalização), enquanto um quadro T1 transporta 24 timeslots a 1544 Kbps usando um bit para sincronização e um esquema de bit roubado para sinalização.](../images/10-legacy-fig08.png)

Nos EUA, o tronco digital mais comum é o T1, que possui 24 linhas disponíveis; na Europa e na América Latina, os troncos E1 têm 30 linhas. Algumas empresas oferecem um T1/E1 fracionado com menos canais. **Robbed bit signaling** Às vezes, um tronco T1 usa um esquema de bit roubado onde um bit é emprestado para sinalização. Nos troncos T1, o canal de dados/voz é transmitido com 56 Kbps em cada timeslot. Como você pode observar, ao usar o bit roubado, o circuito T1 não perde dois slots para sincronização e sinalização.

#### Código de linha T1/E1

T1s e E1s são na verdade circuitos de dados e possuem uma codificação de dados que determina a forma como os bits são interpretados. Para E1s, o código de linha mais comum é HDB3 para a camada 1 e CCS para a camada 2. A maneira mais fácil de saber como seu tronco digital está configurado é perguntar à TELCO sobre essa informação. Você precisará dessas informações para configurar o arquivo /etc/dahdi/system.conf.

#### T1/E1 Sinalização

É importante entender que linhas T1/E1 podem ser entregues usando diferentes tipos de sinalização, como:

- T1 com sinalização de bit roubado
- T1 com sinalização ISDN
- E1 com MFC/R2 (CAS - Sinalização Associada ao Canal)
- E1 com sinalização ISDN

ISDN é frequentemente usado na Europa e nos EUA. É uma rede de voz digital, padronizada pela International Telecommunications Union (ITU) em 1984. O ISDN fornece dois tipos de canais:

- Canais Bearer
  - Voz
  - Dados
- Canais de dados
  - Sinalização out-of-band
  - Sinalização LAPD
  - Q.931

Normalmente, uma linha ISDN é fornecida usando dois meios físicos:

- Interface de taxa básica (BRI)
  - Conhecida como 2B+D
  - Dois canais de transporte (64K) e um canal de dados (16K)
  - Utiliza um par de fios de cobre com 148Kbps.
- Interface de taxa primária (PRI)
  - Fornecida usando um tronco T1/E1
  - 23B+D para T1s
  - 30B+D para E1s

Às vezes, circuitos E1 utilizam um esquema de sinalização CAS chamado MFC/R2, que foi definido pela ITU como um padrão conhecido como Q.421/Q441. Isso é encontrado com frequência na América Latina e na Ásia. Várias empresas de telefonia nesses países utilizam variantes personalizadas do MFC/R2. Portanto, você precisará conhecer a variação correta do país para que funcione.

### ISDN BRI

Canais que utilizam sinalização ISDN BRI são muito populares na Europa. A maioria dos cartões ISDN BRI para Asterisk suporta uma interface S/T com capacidades NT e TE. A conexão TE (terminal) é a que é usada para conectar ao TELCO ou a outros PBXs configurados como terminação de rede (NT). O NT é usado para conectar telefones e PBXs configurados como TE. O ISDN BRI fornece dois canais de dados/voz e um canal de sinalização. Cartões ISDN BRI estão disponíveis de vários fornecedores de cartões de interface para Asterisk.

### Escolhendo uma placa de telefonia para seu servidor Asterisk

Existem vários fabricantes de placas digitais compatíveis com Asterisk. A escolha de uma placa depende de alguns dos seguintes fatores:

#### Barramento de dados

Existem vários tipos de barramento no seu PC. É muito importante que você tenha a placa correta para o seu servidor. A visão geral a seguir descreve as placas mais usadas:

- 32 Bits PCI 5V encontrado na maioria dos computadores, incluindo desktops
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, e TC400
  - Sangoma A101, A102, e A104
- 32/64 bits PCI 3.3V, basicamente encontrado em servidores
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, e TC400
- PCI Express encontrado em desktops e servidores
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, e AEX800
  - Sangoma A101, A102, e A104

Essas famílias de placas se originaram na Digium, que a Sangoma adquiriu em 2018; agora são vendidas e suportadas sob a marca Sangoma. Muitas das SKUs mais antigas listadas aqui foram descontinuadas, portanto confirme a disponibilidade atual do modelo em www.sangoma.com antes de comprar.

- MiniPCI encontrado em sistemas embarcados
  - OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI) e B400M(ISDN BRI)
- USB 2.0 encontrado na maioria dos PCs modernos. Soluções baseadas em USB permitem uma grande densidade de canais analógicos e digitais. Esse barramento suporta 480 Mbps, e cada canal de voz ocupa 64 Kbps. Ao usar hubs USB, é possível alcançar densidades de até mil portas analógicas em uma única porta.
  - Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet. A maior vantagem da Ethernet é permitir que a placa seja conectada a mais de um servidor. Soluções de alta disponibilidade são normalmente a aplicação principal para esses dispositivos. O ponto forte dessa solução é o uso de servidores sem slots PCI livres ou servidores blade.
  - Redfone FoneBridge (até quatro circuitos E1)

### Usando cancelamento de eco de hardware

A cancelamento de eco por hardware reduz a carga na CPU do host. Para placas com mais de uma interface E1, o cancelamento de eco por hardware pode ajudar a aliviar o processador. Novos canceladores de eco por software aprimorados, como o OSLEC, estão reduzindo a necessidade de um cancelador de eco por hardware. Para escolher entre canceladores de eco por hardware e por software, você deve considerar a quantidade de poder de processamento disponível em seu servidor e o número de circuitos E1. Um processo de cancelamento de eco pode usar até nove MIPS (milhões de instruções por segundo) por canal de voz com 128 taps de amplitude usando OSLEC (Referência: Xorcom Ltd.). Se você considerar 1 ciclo de CPU por cada instrução (o que nem sempre é correto com base no processador e na implementação do software), estamos falando de 1,080 GHz para quatro E1s.

#### Tipo de sinalização

Selecionar o tipo de sinalização (por exemplo, T1 CAS, T1 PRI, E1 CAS R2 ou E1 CAS ISDN) não é uma tarefa fácil. Realmente depende do que está disponível na sua região e a que preço. Sinalização de Canal Comum (CCS) costuma ser melhor que sinalização associada ao canal (CAS). No entanto, muitas vezes não está disponível. Nos EUA, você geralmente pode escolher, já que a maioria das TELCOS oferece T1 CAS para usuários regulares e T1 PRI para usuários avançados (por exemplo, call centers). Na América Latina, E1 CAS R2 é predominante, mas ISDN PRI está disponível em algumas cidades.

![A arquitetura de software DAHDI: Asterisk se comunica com o driver de canal `chan_dahdi`, que por sua vez carrega as bibliotecas de protocolo libpri (ISDN), libopenr2 (MFC/R2) e libss7 (SS7); estas ficam sobre a interface `/dev/dahdi`, o driver de kernel DAHDI e o driver de kernel da interface específica da placa.](../images/10-legacy-fig09.png)

Implementar R2 é necessário para instalar uma biblioteca conhecida como OpenR2 (www.libopenr2.org), desenvolvida por Moises Silva, e para aplicar patches no Asterisk antes da instalação — um procedimento simples mostrado mais adiante neste capítulo. A biblioteca passou por vários testes e está em produção em diversos de nossos clientes. ISDN é, na minha opinião, sempre a melhor escolha, se disponível. Alguns provedores podem ter acesso ao sistema de sinalização 7 (SS7), que é uma sinalização CCS disponível entre operadoras telefônicas. Soluções proprietárias e de código aberto estão disponíveis para SS7. A biblioteca libss7 é usada para suportar SS7 no Asterisk.

### Configuração de canais de telefonia Asterisk

Configuring a telephony interface card involves several necessary steps. In this chapter, we will show three of the most common scenarios:

- Conexão digital usando ISDN PRI
- Conexão digital usando ISDN BRI
- Conexão digital usando MFC/R2

Existem duas maneiras de configurar canais DAHDI. A primeira é configurá‑los manualmente com controle total de todos os parâmetros. A segunda forma é usar a utilidade dahdi_genconf para detectar e configurar os cartões.

#### Detecção automática e configuração

Graças à equipe de desenvolvimento da DAHDI, agora temos detecção e configuração automáticas dos cartões. Etapa 1: Para gerar a configuração automaticamente, use o utilitário dahdi_genconf, que detectará o cartão e gerará os arquivos /etc/dahdi/system.conf e dahdi-channels.conf.

```
dahdi_genconf
```

Step 2: Na última linha do arquivo chan_dahdi.conf, inclua o arquivo dahdi-channels.conf

```
#include dahdi_channels.conf
```

Etapa 3: Comente todos os módulos não usados no arquivo **modules** ou simplesmente use:

```
dahdi_genconf modules
```

#### Configuração manual

Outra opção é configurar as interfaces manualmente. Abaixo estão alguns exemplos da configuração para canais DAHDI.

##### Exemplo #1 – Dois canais T1/ E1 usando ISDN

Passos necessários:

1. Instalação do TE205P ou TE210P
2. `/etc/dahdi/system.conf` file configuration
3. Carregamento do driver DAHDI
4. `dahdi_test` utility
5. `dahdi_cfg` utility
6. `chan_dahdi.conf` file configuration
7. Carregamento e teste do Asterisk

Passo 1: Instalação do TE205P. Antes de instalar o TE205P, é importante entender as diferenças entre as placas TE205P e TE210P. A placa TE210P usa um barramento de 64 bits alimentado por 3,3 volts, encontrado quase que exclusivamente nas placas‑mãe de servidores. Tenha cuidado ao especificar esta placa de interface; certifique‑se de que seu hardware suporta um barramento de 64 bits, 3,3 V. A placa TE205P usa um PCI de 5 V, que costuma ser encontrado em computadores desktop. Escolhemos a placa de interface TE205P com dois spans para este exemplo porque é mais fácil reduzi‑la para uma placa de um span ou expandi‑la para a placa de quatro spans. Estas placas agora são vendidas sob a marca Sangoma (anteriormente Digium).

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

A configuração das placas digitais TDM é um pouco diferente da configuração de suas contrapartes analógicas. Primeiro, precisaremos configurar os spans da placa e depois os canais. Os spans são numerados sequencialmente dependendo da ordem de reconhecimento das placas. Em outras palavras, se você tem mais de uma placa de interface, é difícil saber a qual span cada uma pertence. Use dahdi_hardware para verificar qual hardware está instalado em cada span. Exemplo #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

# Example #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

Exemplo #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

Step 3: Loading kernel drivers Check which driver you need to install using dahdi_hardware.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

Para carregar use:

```
modprobe dahdi
modprobe wct2xxp
```

Etapa 4: Usando dahdi_test, verifique as interrupções perdidas  
Você pode verificar o número de interrupções perdidas usando o utilitário dahdi_test compilado com as placas DAHDI.  
Um número abaixo de 99.987% indica possíveis problemas.  
Você encontrará dahdi_test em

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

Etapa 5: Usando o utilitário dahdi_cfg  
Esta é a saída correta do dahdi_cfg para um span E1 fracionado (15 portas) e duas portas FXO.

```
#./dahdi_cfg -vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

Etapa 6: Configuração do DAHDI no arquivo /etc/asterisk/chan_dahdi.conf Exemplo #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

Exemplo #2 (2xE1)

```
callerid="Flavio Eduardo" <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

Exemplo #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Use signaling=bri_cpe_ptmp para BRI ponto‑a‑multiponto. Atualmente, BRI ponto‑a‑multiponto não é suportado no modo NT.

#### Carregando os drivers do kernel

Depois de configurar os drivers, você pode simplesmente reiniciar o servidor. Se você instalou o DAHDI com `make config`, não precisará fazer nada extra. O driver do kernel será carregado e configurado automaticamente. Contudo, às vezes é útil carregar e descarregar os drivers manualmente. Exemplo:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

O primeiro comando carrega o driver e o segundo, dahdi_cfg, aplica a configuração ao driver do kernel.

### Solução de Problemas

Às vezes as coisas não funcionam na primeira tentativa. Vamos verificar alguns recursos para solução de problemas do DAHDI. Passo 1: Verifique se o cartão está sendo reconhecido pelo sistema operacional. Os cartões Sangoma/Digium geralmente são reconhecidos como o modem ISDN.

```
lspci -v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

Etapa 2: Verifique se o driver do kernel está carregando corretamente usando:

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Etapa 3: Verifique o status dos alarmes relacionados à camada física da conexão. Para verificar a camada física da conexão E1, você pode usar o seguinte comando Asterisk CLI.

```
dahdi show status
```

Os alarmes indicam problemas com a porta: Alarme Vermelho: Não é possível manter a sincronização com o switch remoto. Isso geralmente é um problema físico, como código de linha ou incompatibilidade de enquadramento. Alarme Amarelo: Sinaliza que o switch remoto está no alarme vermelho. Isso indica que o switch remoto não está recebendo suas transmissões. Alarme Azul: Recebe todos os 1s não enquadrados em todos os timeslots; dahdi_tool atualmente não detecta um alarme azul. Loopback: A porta está em loopback local ou remoto.

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Step 4: Para detectar problemas com DAHDI no servidor Asterisk, primeiro verifique se os canais estão sendo reconhecidos usando:

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

Etapa 5: Verifique o status da camada 3 do ISDN, também conhecida como q.931. Você pode verificar se a camada 3 do ISDN está ativa usando: `pri show spans` (para listar todos os spans) ou `pri show span <n>` para um span específico:

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

Use `pri show spans` (plural) para listar o status de todos os spans PRI configurados de uma vez.

Verifique um canal específico. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x: Se depois de tudo ainda houver problemas, inicie a depuração do pri span. Este comando habilita uma depuração detalhada de chamadas ISDN. É um comando importante quando você acha que algo não está correto. Você pode detectar dígitos discados incorretamente e outros problemas. Abaixo apresentamos um exemplo de saída de depuração para uma chamada bem‑sucedida. Consulte este exemplo se precisar comparar uma chamada malsucedida com uma sem problemas. Uma dica é usar core set verbose=0 para receber apenas as mensagens ISDN q.931.

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### Opções de configuração em chan_dahdi.conf

Várias opções estão disponíveis no arquivo chan_dahdi.conf. Descrever todas as opções seria entediante e contraproducente. Aqui, detalharemos os principais grupos de opções disponíveis para proporcionar uma melhor compreensão.

#### Opções gerais (independente de canal)

context: Define o contexto de entrada.

```
context=default
```

channel: Define canal ou intervalo de canais. Cada definição de canal herdará as opções definidas antes da declaração. Os canais podem ser identificados individualmente ou na mesma linha com separação por vírgula. Intervalos podem ser definidos usando “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Permite que canais sejam tratados como um grupo. Se você discar um número de grupo em vez de um número de canal, o primeiro canal disponível será usado. Se os canais forem telefones, ao chamar um grupo, todos os telefones tocarão simultaneamente. Usando vírgulas, você pode especificar mais de um grupo para o mesmo canal.

```
group=1
group=3,5
```

language: Turns on the internationalization and configures a language. This feature will configure system messages for a specific language. English is the only language with complete prompts available from the standard installation. musiconhold: Select music on hold class.

#### Opções ISDN

switchtype: Is dependent on the PBX or switch used. In Europe and Latin America, EuroISDN is common.

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: Obrigatório para alguns switches que precisam de uma especificação de plano de discagem. Esta opção é ignorada por muitos switches. As opções válidas são private, national, international e unknown.

```
pridialplan = unknown
```

prilocaldialplan: Necessário para alguns switches, geralmente desconhecido.

```
prilocaldialplan = unknown
```

overlapdial: Overlap dialing é usado quando você envia dígitos após a conexão ser estabelecida. Você pode usar numeração em modo bloco (overlapdial=no) ou modo dígito (overlapdial=yes). O modo bloco é frequentemente usado por operadores.  
signaling: Configura o tipo de sinalização para os canais subsequentes. Esses parâmetros devem corresponder aos do arquivo chan_dahdi.conf. As escolhas corretas são baseadas no canal disponível. Para ISDN você pode escolher cinco opções:

- pri_cpe: Usado quando o dispositivo é um CPE, às vezes referido como cliente, usuário ou escravo. Esta é a forma mais simples e mais usada de sinalização. Às vezes, ao tentar conectar a um PBX privado, o PBX também foi configurado como CPE. Nesse caso, use sinalização pri_net no Asterisk.  
- pri_net: Usado quando o Asterisk está conectado a um PBX privado configurado como CPE. A sinalização costuma ser referida como host, master ou network.  
- bri_cpe: Usado quando o Asterisk está conectado como CPE a um tronco ISDN BRI  
- bri_net: Usado quando o Asterisk está conectado a um telefone ISDN ou PBX configurado como terminal (TE).  
- bri_cpe_ptmp: Mesmo que bri_cpe, mas em uma arquitetura ponto‑a‑multiponto.  

#### CallerID options

Muitas opções de Caller ID estão disponíveis. Algumas podem ser desativadas, embora a maioria esteja habilitada por padrão.  
usecallerid: Habilita ou desabilita a transmissão do Caller ID para os canais subsequentes (Yes/No). Nota: Se o seu sistema requer dois toques antes de atender, tente desativar esse recurso para que ele atenda imediatamente.  
hidecallerid: Oculta o Caller ID (Yes/No).  
calleridcallwaiting: Habilita o recebimento do Caller ID durante uma indicação de chamada em espera (Yes/No).  
callerid: Configura uma string de Caller ID para um canal específico. O chamador pode ser configurado com “asreceived” nas interfaces de trunk para repassar o Caller ID.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Note: A maioria das TELCOs exige que você configure o ID de chamada correto. Se você não fornecer o ID de chamada correto, não deverá conseguir discar para fora através da TELCO. Por outro lado, você poderá receber chamadas mesmo sem configurar o ID de chamada.

#### Opções de qualidade de áudio

Essas opções ajustam certos parâmetros do Asterisk que afetam a qualidade de áudio nos canais DAHDI.

- **echocancel**: Desabilita ou habilita a cancelamento de eco. Você deve manter esse recurso habilitado. Aceita "yes" ou o número de taps. (Explicação: Como funciona o cancelamento de eco? A maioria dos algoritmos de cancelamento de eco opera gerando múltiplas cópias de um sinal recebido, cada uma atrasada por um pequeno intervalo. Esse pequeno fluxo é chamado de "tap". O número de taps determina o atraso de eco que pode ser cancelado. Essas cópias são atrasadas, ajustadas e subtraídas do sinal original. O truque é ajustar o sinal atrasado exatamente ao necessário para remover o eco.)
- **echocancelwhenbridged**: Habilita ou desabilita o cancelador de eco durante uma chamada TDM pura. Normalmente isso não é necessário.
- **rxgain**: Ajusta o ganho de recepção de áudio para aumentar ou diminuir o volume de recepção (-100% a 100%).
- **txgain**: Ajusta o ganho de transmissão de áudio para aumentar ou diminuir o volume de transmissão (-100% a 100%).

Example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Opções de faturamento

Essas opções alteram a forma como as informações de chamadas são registradas no banco de dados de registros detalhados de chamadas (CDR). amaflags: Afeta a categorização do CDR. Aceita estes valores:

- billing
- documentation
- omit
- default

accountcode: Configura um código de conta para um canal específico. Pode conter qualquer valor alfanumérico, geralmente o nome do departamento ou do usuário.

```
accountcode=finance
amaflags=billing
```

### Configuração MFC/R2

MFC/R2 é usado em vários países da América Latina, China e África, bem como em alguns países europeus. ISDN é superior e preferido se estiver disponível em sua região.

#### Entendendo o problema

A placa usada para sinalizar MFC/R2 é a mesma usada para sinalizar ISDN. É possível usar MFC/R2 em canais DAHDI usando a biblioteca chamada libopenR2 (www.libopenr2.com). Essa biblioteca não fazia parte das versões do Asterisk anteriores à 1.6.2.

##### Entendendo o protocolo MFC/R2

O protocolo MFC/R2 combina sinalização in-band e out-of-band. A sinalização de endereço é encaminhada in-band usando um conjunto de tons enquanto as informações de canal são transmitidas no timeslot 16 como sinalização out-of-band.

**Line Signaling (ITU-T Q.421).** No timeslot 16, cada canal de voz usa quatro bits ABCD para sinalizar seus estados e controle de chamada. Os bits C e D são raramente usados. Em alguns países, eles podem ser usados para medição (medição de pulsos para faturamento). Em uma conversa normal, temos ambos os lados em operação: o chamador e o chamado. O sinalização do lado do chamador é chamada de sinalização forward, enquanto o lado chamado usa sinalização backward. Designaremos Af e Bf para sinalização forward e Ab e Bb para sinalização backward.

| Estado | ABCD avançar | ABCD retroceder |
| --- | --- | --- |
| Inativo/Liberado | 1001 | 1001 |
| Capturado | 0001 | 1001 |
| Ack de Captura | 0001 | 1101 |
| Atendido | 0001 | 0101 |
| LimparRetro | 0001 | 1101 |
| LimparEnc (antes de limpar-retro) | 1001 | 0101 |
| LimparEnc (confirmação de desconexão) | 1001 | 1001 |
| Bloqueado | 1001 | 1101 |

MFC/R2 foi definido pela ITU. Infelizmente, vários países personalizaram o padrão de acordo com suas próprias necessidades. Como resultado, surgiram variações nos padrões entre os países.

**Sinais inter-registro (ITU-T Q.441).** O sinalização MFC/R2 usa uma combinação de dois tons. As tabelas abaixo mostram o padrão ITU.

Grupo de sinal I (avançado):

| Description | Forward signal |
| --- | --- |
| Dígito 1 | I-1 |
| Dígito 2 | I-2 |
| Dígito 3 | I-3 |
| Dígito 4 | I-4 |
| Dígito 5 | I-5 |
| Dígito 6 | I-6 |
| Dígito 7 | I-7 |
| Dígito 8 | I-8 |
| Dígito 9 | I-9 |
| Dígito 0 | I-10 |
| Indicador de código de país, supressor de meio eco de saída requerido | I-11 |
| Indicador de código de país, sem supressor de eco requerido | I-12 |
| Indicador de chamada de teste | I-13 |
| Indicador de código de país, supressor de meio eco de saída inserido | I-14 |
| Não usado | I-15 |

Grupo de sinal II (forward):

| Description | Forward signal |
| --- | --- |
| Assinante sem prioridade | II-1 |
| Assinante com prioridade | II-2 |
| Equipamento de manutenção | II-3 |
| Reserva | II-4 |
| Operador | II-5 |
| Transmissão de dados | II-6 |
| Assinante ou operador sem recurso de transferência direta | II-7 |
| Transmissão de dados | II-8 |
| Assinante com prioridade | II-9 |
| Operador com recurso de transferência direta | II-10 |
| Reserva | II-11 |
| Reserva | II-12 |
| Reserva | II-13 |
| Reserva | II-14 |
| Reserva | II-15 |

Grupo de sinal A (reverso):

| Description | Backward signal |
| --- | --- |
| Enviar próximo dígito (n+1) | A-1 |
| Enviar penúltimo dígito (n-1) | A-2 |
| Endereço completo, mudar para recepção de sinais do Grupo B | A-3 |
| Congestionamento na rede nacional | A-4 |
| Enviar categoria da parte chamadora | A-5 |
| Endereço completo, tarifar, estabelecer condições de fala | A-6 |
| Enviar antepenúltimo dígito (n-2) | A-7 |
| Enviar dígito anterior ao antepenúltimo (n-3) | A-8 |
| Reserva | A-9 |
| Reserva | A-10 |
| Enviar indicador de código do país | A-11 |
| Enviar dígito de idioma ou discriminação | A-12 |
| Enviar natureza do circuito | A-13 |
| Solicitar informação sobre uso de supressor de eco | A-14 |
| Congestionamento em uma troca internacional ou em sua saída | A-15 |

Grupo de sinal B (retroativo):

| Description | Backward signal |
| --- | --- |
| Reserva | B-1 |
| Enviar tom de informação especial | B-2 |
| Linha do assinante ocupada | B-3 |
| Congestão (após troca do grupo A para B) | B-4 |
| Número não alocado | B-5 |
| Linha do assinante livre, tarifada | B-6 |
| Linha do assinante livre, sem tarifação | B-7 |
| Linha do assinante fora de serviço | B-8 |
| Reserva | B-9 |
| Reserva | B-10 |
| Reserva | B-11 |
| Reserva | B-12 |
| Reserva | B-13 |
| Reserva | B-14 |
| Reserva | B-15 |

#### Sequência MFC/R2

A sequência a seguir ilustra uma chamada originada da extensão do Asterisk para um terminal na PSTN. A PSTN descarta a chamada e encerra a comunicação.

![Um fluxo de chamada MFC/R2 completo entre Asterisk e a operadora: o sinal de linha (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) é trocado no timeslot 16, os dígitos discados e os sinais de retorno "send next digit" (grupos I/A/B) viajam in-band, e os tons audíveis chegam ao assinante.](../images/10-legacy-fig11.png)

### Como usar o driver libopenr2

O projeto iniciado por Moises Silva foi inspirado no driver de canal Unicall escrito por Steve Underwood. A biblioteca OpenR2 é atualmente a solução de software mais estável para Asterisk. Com esta solução, podemos usar qualquer placa digital compatível com DAHDI. Anteriormente, apenas soluções proprietárias estavam disponíveis para MFC/R2, uma das melhores que usei foi a disponibilizada pela Khomp, www.khomp.com.br. No Asterisk 22, o suporte a MFC/R2 via libopenR2 é incorporado quando a biblioteca está presente no momento da compilação — não é necessário patch externo. Os passos abaixo mostram a instalação manual histórica para referência; em sistemas modernos, instale `libopenr2-dev` a partir do gerenciador de pacotes da sua distribuição antes de executar `./configure`, então habilite `chan_dahdi` em `make menuselect`.

Os passos abaixo constroem o openr2 e o Asterisk a partir de seus repositórios Git atuais. Eles são mantidos como referência para sites que compilam a partir do código‑fonte; em uma distribuição moderna você geralmente pode ignorá‑los totalmente instalando o pacote `libopenr2-dev` e uma versão empacotada do Asterisk 22, já que `chan_dahdi` compila o suporte R2 diretamente contra libopenr2 sem nenhum patch externo.

Passo 1: Instale as ferramentas de compilação que você precisa.

```
apt-get install git
```

Etapa 2: Clone a biblioteca openr2 e o código-fonte do Asterisk. Nenhuma árvore patch especial é necessária no Asterisk 22 — um checkout padrão compila o suporte R2 desde que libopenr2 esteja presente.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Etapa 3: Compilar e instalar  
Por favor, BACK UP seu servidor antes de prosseguir.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note: Não execute “make samples” para evitar sobrescrever seus arquivos de configuração.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Vamos supor que você tem um cartão com uma interface E1.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Etapa 5: Execute o comando dahdi_cfg para aplicar as alterações ao driver:

```
dahdi_cfg -vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

Step 5: Alterar o arquivo chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Etapa 6: Alterar o plano de discagem no arquivo extensions.conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Nota: Algumas TELCOS não aceitam chamadas sem o identificador de chamada. Defina o identificador de chamada para um dos números DID atribuídos pela operadora. Em alguns países, esta etapa não é necessária. Passo 7: Teste a solução: Agora, com uma extensão no contexto from-internal, disque qualquer número e observe o console. Verifique se há erros ocorrendo. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Depuração do OpenR2

Para detectar erros nas chamadas, você pode ativar a depuração. Para isso, siga os passos abaixo.

1. Edite o arquivo `chan_dahdi.conf` e adicione as três linhas seguintes à configuração:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. Reinicie o servidor Asterisk
3. Teste a chamada e verifique os arquivos de chamada em `/var/log/asterisk/mfcr2/span1`

A seguir está um rastreamento de uma chamada normal. Compare com o que você recebe na sua chamada.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### Configuração MFC/R2

As opções estão documentadas no arquivo chan_dahdi.conf. Algumas das opções mais importantes são detalhadas aqui. Parâmetros obrigatórios: mfcr2_variant, mfcr2_max_ani e mfcr2_max_dnis. mfcr2_variant: variante do país.

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani: Max amount of ANI digits to ask for mfcr2_max_dnis: Max amount of DNIS digits to ask for mfcr2_get_ani_first: Whether or not to get ANI before DNIS (required by some TELCOS) mfcr2_category: Caller category. You can set the variable MFCR2_CATEGORY before starting the call mfcr2_logdir: Directory to log the call files. (/var/log/asterisk/mfcr2/directory) mfcr2_call_files: Whether or not to log the calls

- mfcr2_logging: logging values
- cas – ABCD bits for tx and rx
- mf – Multifrequency tones
- stack – verbose output of the channel and context stack
- all – all activities
- nothing – do not log anything

mfcr2_mfback_timeout: This value deserves to be mentioned. Sometimes if you are calling a cell phone or any call that takes a long time to complete, this parameter can time out, so it is often changed for fine tuning. If some of your calls are not being completed, this is the parameter you should change first. mfcr2_metering_pulse_timeout: Pulses are used by some R2 variants to indicate costs mfcr2_allow_collect_calls: In Brazil, the tone II-8 is used to indicate a collect call; this parameter allows you to block collect calls. mfcr2_double_answer: Also used to avoid collect calls when a double answer is required. With double_answer=yes you actually block the collect calls. mfcr2_immediate_accept: Allows you to skip the use of group B/II signals and go directly to the accepted state. mfcr2_forced_release: Allows you to speed up the release of the call; works for the Brazilian variant.

#### ANI and DNIS

Identificação Automática de Número (ANI) é o número do chamador. Serviço de Identificação de Número Discado (DNIS) é o número chamado ou, em outras palavras, o número discado. Quando uma chamada é recebida, normalmente os últimos quatro dígitos são enviados ao PBX em um processo chamado discagem direta interna (DID). O número ANI é na verdade o Caller ID. O ANI conterá a extensão do chamador quando a chamada for feita, enquanto o DNIS conterá o destino da chamada. É importante que esses parâmetros sejam configurados corretamente. Alguns switches enviam apenas os últimos quatro dígitos, enquanto outros enviam o número completo.

### DAHDI channel format

DAHDI channels use the following format in the dial plan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Exemplos:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## O protocolo IAX2

Neste capítulo, aprenderemos sobre o protocolo Inter-Asterisk eXchange (IAX), incluindo seus pontos fortes e fracos. Detalhes como modo trunk e a interconexão de dois servidores Asterisk também serão abordados. Todas as referências neste documento correspondem à versão 2 do IAX.

O protocolo IAX fornece transporte de mídia e sinalização para voz e vídeo. IAX é muito inovador; economiza largura de banda no modo trunk e é muito mais simples que SIP quando você precisa atravessar NAT. O uso principal do IAX hoje em dia é interconectar servidores Asterisk. IAX foi criado principalmente para voz, mas também pode acomodar vídeo e outros fluxos multimídia.

IAX foi inspirado em outros protocolos VoIP, como SIP e MGCP. Em vez de usar dois protocolos separados para sinalização e mídia, IAX os unificou em um único protocolo. IAX não usa RTP para transporte de mídia; ao invés disso, incorpora a mídia na mesma conexão UDP.

**Status no Asterisk 22.** `chan_iax2` ainda está incluído e totalmente suportado no Asterisk 22 LTS, portanto tudo nesta seção permanece válido. IAX2 é, porém, um protocolo legado que vê relativamente pouca implantação nova: a indústria convergiu amplamente para SIP (via `chan_pjsip` no Asterisk 22) tanto para trunking de provedores quanto para interconexão de servidores. A principal vantagem remanescente do IAX2 é seu design de porta única — toda a sinalização e mídia fluem por uma única porta UDP (4569 por padrão), o que simplifica a configuração de firewall e NAT comparado ao SIP mais seus fluxos RTP separados. Para um novo trunk Asterisk‑to‑Asterisk onde NAT não é uma preocupação, um trunk PJSIP é a abordagem moderna recomendada; IAX2 é abordado aqui porque continua sendo uma escolha válida, especialmente onde apenas uma porta UDP pode ser aberta através de um firewall.

### Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Identificar pontos fortes e fracos do protocolo IAX
- Descrever cenários de uso para o protocolo IAX
- Descrever as vantagens do modo trunk do IAX
- Configurar iax.conf para telefones
- Configurar iax.conf para conexão a um provedor VoIP
- Configurar iax.conf para interconexão Asterisk
- Entender a autenticação IAX

### Design do IAX

Os principais objetivos do design do IAX são:

- Reduzir a largura de banda necessária para transporte de mídia e sinalização
- Prover transparência de NAT
- Poder transmitir as informações do dialplan
- Suportar o uso eficiente de paging e intercom

IAX é um protocolo de sinalização e mídia peer‑to‑peer que é semelhante ao SIP sem usar RTP. A abordagem básica é multiplexar os fluxos multimídia sobre uma única conexão UDP entre dois hosts. O maior benefício dessa abordagem é sua simplicidade ao atravessar conexões por NAT, comumente encontradas em modems xDSL. IAX usa uma única porta, UDP 4569 por padrão, e então usa um número de chamada com 15 bits para multiplexar todos os fluxos. O protocolo IAX usa processos de registro e autenticação semelhantes ao protocolo SIP. Uma descrição do protocolo pode ser encontrada em http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![The IAX protocol multiplexes many calls between two endpoints over a single UDP port (4569 by default), using a 15-bit call number to keep the streams apart — which makes NAT traversal simple.](../images/10-legacy-fig12.png)

### Uso de largura de banda

A largura de banda usada em redes VoIP é afetada por vários fatores; codecs e cabeçalhos de protocolo são os mais importantes. O protocolo IAX tem um recurso surpreendente chamado modo trunk, pelo qual ele multiplexa várias chamadas usando um único cabeçalho. Ao brincar com a calculadora de largura de banda do Asterisk, você verá como trunks IAX podem economizar até 80 % do tráfego com múltiplas chamadas.

![Comparing IAX and SIP overhead: two SIP/RTP calls need two packets (40 bytes of payload carried under 156 bytes of overhead), while IAX2 trunk mode carries both calls in a single packet (40 bytes of payload under just 66 bytes of overhead) by sharing one IP/UDP header across many mini-frames.](../images/10-legacy-fig13.png)

### Nomeação de canais

É importante entender as convenções de nomeação de canais, pois você usará esses nomes ao especificar um canal no dial

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — UserID no par remoto, ou nome do cliente configurado em iax.conf
- `<secret>` — A senha. Alternativamente pode ser o nome de arquivo de uma chave RSA sem a extensão final (.key ou .pub) e entre colchetes
- `<peer>` — Nome do servidor ao qual conectar
- `<portno>` — Número da porta para a conexão
- `<exten>` — Ramal no servidor Asterisk remoto
- `<context>` — Contexto no servidor Asterisk remoto
- `<options>` — A única opção disponível é 'a', que significa 'request autoanswer'

#### Outbound channels example:

Outbound channels are seen in the Asterisk console.

- `IAX2/8590:secret@myserver/8590@default` — Ligar para o ramal 8590 em myserver. Usa 8590:secret como par nome/senha
- `IAX2/iaxphone` — Ligar para "iaxphone"
- `IAX2/judy:[judyrsa]@somewhere.com` — Ligar para somewhere.com usando judy como nome de usuário e uma chave RSA para autenticação

#### The format of an incoming IAX channel is:

Inbound channels are seen in the Asterisk console.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — Nome de usuário, se conhecido
- `<host>` — Host de conexão
- `<callno>` — Número de chamada local

Exemplo de canal de entrada:

- `IAX2[flavio@8.8.30.34]/10` — Número de chamada 10 do endereço IP 8.8.30.34 usando flavio como usuário.
- `IAX2[8.8.30.50]/11` — Número de chamada 11 do endereço IP 8.8.30.50.

### Usando IAX

Você pode usar IAX de várias maneiras. Nesta seção, mostraremos como configurar IAX para diversos cenários, incluindo:

- Conectar um softphone usando IAX
- Conectar IAX a um provedor VoIP usando IAX
- Conectar dois servidores usando IAX
- Conectar dois servidores usando IAX em modo trunk
- Depurar uma conexão IAX
- Usar pares de chaves RSA para autenticação

#### Conectando um softphone usando IAX

Asterisk suporta telefones IP baseados em IAX como o ATCOM e o antigo ATA da Digium (chamado IAXy), bem como softphones que ainda implementam o protocolo IAX2. O processo para softphones, ATAs e hard‑phones é semelhante. Para configurar um dispositivo IAX, você precisa editar o arquivo iax.conf em /etc/asterisk

```
directory.
```

Usaremos um softphone compatível com IAX2 como exemplo.

1. Faça um backup do arquivo original `iax.conf` usando:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. Comece a editar um novo arquivo `iax.conf`:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; Parâmetro muito importante, ele altera os codecs disponíveis

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

Eu tentei preservar as linhas padrão (não comentadas) do arquivo de exemplo. Os seguintes parâmetros foram modificados:

```
bandwidth=high
```

Esta linha afeta a seleção de codec. Usar a configuração alta permite a escolha de um codec de alta largura de banda e alta qualidade, como g.711 definido pela palavra‑chave ulaw. Se você mantiver o parâmetro padrão, não poderá escolher ulaw. Nesse caso, o Asterisk exibirá a mensagem “no codec available” para a configuração abaixo.

```
disallow=all
allow=ulaw
```

Nos comandos descritos acima, desativamos todos os codecs e habilitamos apenas o ulaw. Em LANs, a maioria das pessoas prefere usar o ulaw porque ele não consome muito processador e economiza ciclos de CPU. Mesmo usando mais largura de banda, esse codec é preferível porque em LANs você geralmente tem Ethernet de 100 megabits ou até mesmo Gigabit. Uma chamada de voz usando ulaw consome quase 100 kilobits por segundo de largura de banda da sua rede, o que representa um uso muito leve para as LANs de alta velocidade atuais. Em redes WAN ou na Internet, você normalmente desativará o ulaw, trocando alguns ciclos de CPU disponíveis por compressão de voz para um melhor uso da largura de banda. Os codecs gsm, g729 e ilbc também fornecem um bom fator de compressão.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

No comandos acima, definimos um amigo chamado [2003]. O contexto é o padrão (nos primeiros laboratórios sempre usamos o contexto padrão para evitar confusão; este contexto será totalmente explicado quando abordarmos o dialplan). A linha “host=dynamic” fornece um registro dinâmico do endereço IP do telefone.

3. Baixe e instale um softphone compatível com IAX2. Você pode escolher qualquer softphone que ainda suporte o protocolo IAX2 para o laboratório.  
4. Configure uma conta IAX no cliente (geralmente *Add account* → IAX). Observe que o SipPulse Softphone é apenas SIP e não pode registrar via IAX2, portanto, para testes de IAX você precisa de um cliente que ainda suporte o protocolo.

5. Configure o arquivo `extensions.conf` para testar seu dispositivo IAX.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Conectando‑se a um provedor VoIP usando IAX

Alguns provedores VoIP suportam IAX. Você pode encontrar facilmente um provedor IAX pesquisando por “IAX providers”. Usar um provedor IAX faz muito sentido, pois IAX pode economizar muita largura de banda, atravessa NAT com facilidade e pode autenticar usando pares de chaves RSA.

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

O número de provedores comerciais de VoIP compatíveis com IAX diminuiu drasticamente nas últimas versões do Asterisk; a maioria dos provedores agora oferece trunks SIP/PJSIP exclusivamente. Antes de se comprometer com um provedor IAX, confirme que eles mantêm ativamente sua infraestrutura IAX. Para uma nova integração de provedor, um trunk PJSIP (Chapter 3) é a alternativa recomendada.

#### Conectando‑se a um provedor usando IAX

Passo 1: Abra uma conta no seu provedor favorito. Seu provedor lhe fornecerá três itens.

- Name
- Secret
- IP address or Host name
- RSA public key

Passo 2: Configure o arquivo iax.conf para registrar seu Asterisk no provedor. Adicione as linhas a seguir na seção [general] do arquivo.

```
[general]
register=>name:secret@hostname/2003
```

Nas instruções descritas acima, você se registrou no seu provedor usando sua conta e senha. No momento em que receber uma chamada, ela será encaminhada para a extensão 2003.

```
[name]
```

- ; Seu nome de conta ou número

```
type=peer
secret=secret
; Your password
host=hostname
```

Nas instruções descritas acima, criamos um peer correspondente ao provedor para fins de discagem.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

Isso é necessário para a autenticação RSA. Usar a chave pública do seu provedor permite que você tenha certeza de que a chamada recebida é realmente do provedor verdadeiro. Se qualquer outra pessoa tentar usar o mesmo caminho, não conseguirá autenticá‑la porque não possui a chave privada correspondente. Etapa 4: Teste a conexão. Para testar a conexão, disque qualquer número. Alguns fornecedores fornecem um teste de eco. Para isso, edite o arquivo extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Vá para o Asterisk CLI e execute um reload. Para verificar se o Asterisk está registrado com o provedor, use o próximo comando.

```
*CLI>reload
*CLI>iax2 show register
```

Now simply dial *98 on the softphone connected to the Asterisk server.

#### Conectando dois servidores Asterisk através de um tronco IAX

É muito fácil conectar um servidor a outro. Você não precisará registrá‑los porque os endereços IP já são conhecidos. Você terá que criar os peers e usuários no arquivo iax.conf. Todas as extensões no site da matriz começam com 20 seguido de dois dígitos (por exemplo, 2000). Na filial, todas as extensões começam com 22 seguido de dois dígitos (por exemplo, 2200). Usaremos o tronco. Você precisará de uma fonte de temporização DAHDI para habilitar este recurso. Passo 1: Edite o arquivo iax.conf no servidor da Filial.

![Connecting two Asterisk servers with an IAX trunk: the HQ server (192.168.1.1, extensions 20xx) and the Branch server (192.168.1.2, extensions 22xx) reach each other over a single IAX trunk — no registration is needed because both IP addresses are fixed and known.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

# Etapa 2: Configure o arquivo extensions.conf no servidor Branch

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

# Etapa 3: Configure o arquivo iax.conf no servidor HQ

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

Etapa 4: Configure o arquivo extensions.conf no servidor HQ.

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

Se uma chamada tem um nome de usuário especificado, como:

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk tentará autenticar a chamada usando apenas a entrada correspondente no arquivo iax.conf. Se quaisquer outros nomes forem especificados, a chamada será rejeitada. Se nenhum usuário for especificado, Asterisk tentará autenticar a conexão como guest. Contudo, se guest não existir, ele tentará quaisquer outras conexões com um secret correspondente. Em outras palavras, se você não tiver uma seção guest no seu arquivo iax.conf, um usuário mal‑intencionado poderia tentar adivinhar qualquer secret correspondente ao não especificar o nome de usuário. As restrições de negação/permissão de endereços IP também se aplicam. Uma boa forma de evitar a adivinhação de secrets é usar autenticação RSA. Outro método é restringir os endereços IP permitidos para chamar.

#### Restrições de endereço IP

O acesso é controlado com as linhas `permit` e `deny`:

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

Regras são interpretadas em sequência, e todas são avaliadas (esse conceito é diferente das ACLs normalmente encontradas em roteadores e firewalls). A última instrução correspondente substitui as anteriores.

Exemplo #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

Isso negará qualquer pacote da rede 192.168.0.0/24.

Exemplo #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

Isso permitirá qualquer pacote, pois a última instrução substitui a primeira.

#### Conexões de saída

As conexões de saída adquirem informações de autenticação usando os seguintes métodos:

- A descrição do canal IAX2 passada pela aplicação `dial()`.
- Uma entrada com `type=peer` ou `type=friend` no arquivo `iax.conf`.
- Uma combinação de ambos os métodos.

#### Conectando dois servidores Asterisk usando chaves RSA

É possível usar IAX com autenticação forte usando chaves RSA assimétricas. De acordo com o código‑fonte (`res_krypto.c`), o Asterisk usa chaves RSA com algoritmo SHA‑1 para digestões de mensagem, em vez do MD5 mais fraco. Abaixo está um guia passo a passo para configurar dois servidores usando chaves RSA.

##### Configurando o servidor para o ramo

Passo 1: Gere as chaves RSA no servidor do ramo

```
astgenkey -n
```

When asked, use the key name branch. We have used the parameter –n to avoid passing a passphrase whenever Asterisk reinitializes. If you want to improve the security, don’t use the –n and start Asterisk with asterisk -i Step 2: Copy the keys to the directory /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

# Etapa 3: Copiar a chave pública para o servidor HQ

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Step 4: Edit the iax.conf file in the Branch server.

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

# Etapa 8: Configure o arquivo extensions.conf no servidor Branch

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Configurando o servidor para a sede

Etapa 1: Gere as chaves RSA no servidor da sede

```
astgenkey -n
```

When asked use the key name hq. Step 2: Copy the keys to the directory /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

# Etapa 3: Copiar a chave pública para o servidor BRANCH

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

# Etapa 4: Configure o arquivo iax.conf no servidor HQ

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

Step 10: Configure o arquivo extensions.conf no servidor HQ.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### Criptografia IAX2

IAX suporta criptografia de chamadas usando uma chave simétrica, cifra de bloco de 128 bits chamada AES (Advanced Encryption Standard). É muito simples ativar a criptografia entre troncos IAX. No arquivo iax.conf use:

```
encryption=yes
```

Para forçar a criptografia:

```
forceencryption=yes
```

Para garantir compatibilidade com versões mais antigas, pode ser necessário desativar a rotação de chaves usando:

```
keyrotate=no
```

### Comandos de depuração IAX2

A seguir estão alguns dos comandos de console de solução de problemas mais importantes para o Asterisk.

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

Observando esta saída, identifique o início e o fim da chamada. Observe as informações de atraso e jitter obtidas usando pacotes poke e pong. Esses pacotes ajudam a gerar a saída do comando “iax2 show netstats”.

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

Para desativar a depuração, use:

```
vtsvoffice*CLI>iax2 no debug
```

### Resumo

Este capítulo revisou os pontos fortes e fracos do protocolo IAX. Demonstrou como o IAX funciona em vários cenários, como softphones e um tronco entre dois servidores Asterisk. O modo tronco permite economizar largura de banda ao transportar mais de uma chamada em um único pacote. Por fim, você aprendeu comandos de console que podem ser usados para verificar o status e depurar o protocolo.

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

Step 2: Configure the [peer] on sip.conf Create an entry of peer type to the desired provider to simplify Asterisk’s dialing.

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

Etapa 3: Crie uma rota para o provedor no dial plan Escolheremos os dígitos 010 como a rota de destino para o provedor. Para discar #610000 dentro do provedor, basta discar 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### Opções SIP específicas para o cenário do provedor

A discussão a seguir examina os detalhes das opções definidas no arquivo sip.conf para conexão a um provedor VoIP.

```
register=>username:password@hostname/4100
```

A instrução registered no arquivo sip.conf é usada para registrar-se em um provedor. A transação register é autenticada com o name e secret. Você pode usar uma barra (“/”) para fornecer uma extensão para chamadas recebidas. Tecnicamente, a extensão será colocada no campo de cabeçalho “Contact” da requisição SIP. O comportamento de registro pode ser controlado por certos parâmetros:

```
registertimeout=20
registerattempts=10
```

Para verificar se o registro foi bem‑sucedido, o comando legado do console era `sip show registry`. No Asterisk 22 o comando equivalente é `pjsip show registrations` (registros de saída) e `pjsip show endpoints` para o status do endpoint.

O parâmetro “username” é usado no digest de autenticação. O digest é calculado usando username, secret e realm:

```
username=username
```

Host define o endereço ou nome do provedor VoIP:

```
host=hostname
```

Os parâmetros Fromuser e Fromdomain às vezes são necessários para autenticação. Esses parâmetros são usados no campo de cabeçalho SIP From:

```
fromuser=username
fromdomain=hostname
```

Quando você se conecta a um provedor VoIP, são necessárias credenciais. Após o convite inicial, o provedor envia uma mensagem chamada “407 Proxy Authentication Required”; você fornece as credenciais na mensagem INVITE subsequente. Para chamadas recebidas, seu servidor Asterisk solicitará credenciais ao provedor. Obviamente, o provedor não possui uma credencial válida para seu servidor Asterisk. Quando você usa insecure=invite, está dizendo ao Asterisk para não enviar o “407 Proxy Authentication Required” ao provedor e para aceitar chamadas recebidas. Você também pode usar insecure=port,invite para combinar o peer com base no endereço IP sem combinar o número da porta.

```
insecure=invite, port
```

### Conectando dois servidores Asterisk usando SIP (sip.conf)

Você pode usar SIP para interconectar duas máquinas Asterisk. É importante prestar atenção ao dialplan antes de prosseguir com esta configuração. Os usuários geralmente desejam conectar outros PBXs com o mínimo de esforço. A ideia aqui é usar apenas um número de ramal para conectar ao outro PBX. Passo 1: Edite o arquivo sip.conf no servidor A:

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

Etapa 2: Edite o arquivo sip.conf no servidor B:

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![Conectando dois servidores Asterisk usando SIP: o servidor A (ramais 4400/4401) e o servidor B (ramais 4500/4501) trocam sinalização SIP para que usuários em cada PBX possam discar para o outro](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

Step 3: Edit the extensions.conf file in server A:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Etapa 4: Edite o arquivo extensions.conf no servidor B:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Suporte a domínio Asterisk (sip.conf)

O protocolo SIP segue a arquitetura da Internet. A primeira coisa a fazer antes de configurar o SIP é definir corretamente os servidores DNS. Em um ambiente SIP, você pode chamar um usuário localizado em qualquer proxy SIP, e outros usuários também podem chamar você usando seu Identificador Uniforme de Recursos SIP (URI). Para definir um servidor DNS para SIP, você deve adicionar registros SRV ao seu servidor DNS.

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

After configuring the DNS, you can use the URI, which points to a SIP user, SIP phone, or telephone extension. A SIP URI looks similar to an email address (e.g., sip:chuck@yourpartnerdomain.com). Using SIP URIs, no telephone number is needed to make a call from one SIP phone to another. To dial an external user, simply use a statement as the one shown below.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Alguns parâmetros podem controlar o comportamento do domínio.

```
srvlookup=yes
```

Este parâmetro habilita pesquisas DNS SRV em chamadas de saída. Usando este parâmetro, é possível discar chamadas usando nomes SIP baseados em domínio.

```
allowguest=yes
```

Este parâmetro permite que um convite externo seja processado sem autenticação. Ele processa a chamada dentro do contexto definido na seção geral ou na declaração de domínio. Aviso: Se você definir um contexto na seção geral com acesso ao PSTN, um usuário externo pode discar o PSTN através do seu PBX. Nesse caso, você incorrerá em quaisquer cobranças. Permita apenas suas próprias ramais no contexto definido na seção geral.

![Conectando a outros servidores SIP por domínio: youdomain.com e yourpartnerdomain.com trocam sinalização SIP, de modo que usuários como lee e bruce podem chamar chuck e norris usando URIs SIP](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

O comando domain permite que você gerencie mais de um domínio dentro do Asterisk. Se uma chamada vier de um domínio específico, ela será direcionada para um contexto específico.

```
;autodomain=yes
```

Este parâmetro inclui o IP local e o nome do host nos domínios permitidos.

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Step 2: Agora configure o softphone para usar presença. Mostraremos como configurar o SipPulse Softphone.

- Sequência: clique‑direito->Configurações de Conta SIP->Propriedades->Presença
- Altere o modelo de presença de peer-to-peer para presence agent, o que fará o softphone assinar o Asterisk para eventos SIP.

Step 3: Adicione o contato a outros softphones. Neste exemplo, o SipPulse Softphone é a conta 2000, então adicionaremos um contato para a conta 2001. Sequência: abra o painel direito (painel de presença no softphone)->Clique em Contatos->Adicionar um contato. Preencha o nome 2001. Exiba como 2001 e não se esqueça de marcar a caixa Mostrar disponibilidade deste contato.

Step 4: Agora disque a extensão 2001 e verifique o status do telefone no painel direito do softphone. Use o comando de console `core show hints` para ver o status de presença mudando no servidor (no chan_sip legado, `sip show inuse` mostrava quantas chamadas você tinha em cada linha). No Asterisk 22, use `pjsip show endpoints` para inspecionar o estado do endpoint e do canal. O status de presença/BLF aparece nos contatos ou no painel BLF do softphone — exatamente como é exibido depende do cliente.

#### Codec configuration

A configuração de codec é simples e direta. Você pode definir as palavras allow e disallow na seção [general] ou na seção peer/user. A melhor prática é padronizar o codec para evitar transcodificação, que consome muito processador. Por favor, use o mesmo codec para mensagens e prompts.

```
[general]
disallow=all
allow=g729
```

#### Opções de DTMF

Em certas ocasiões, você enviará dígitos para uma aplicação como voicemail ou resposta de voz interativa (IVR). É importante passar o DTMF corretamente. O método mais simples para passar DTMF é chamado inband. Ele é configurado na seção [general] ou na seção peer/user do arquivo sip.conf. Quando você define dtmfmode=inband, os tons DTMF são gerados como sons no canal de áudio. O principal problema desse método é que, ao comprimir o canal de áudio usando um codec como g729, os sons ficam distorcidos e os tons DTMF não são reconhecidos adequadamente. Se você planeja usar dtmfmode=inband, utilize o codec g.711 (ulaw e alaw).

```
dtmfmode=inband
```

Outra abordagem é usar RFC2833, que permite passar tons DTMF como eventos nomeados nos pacotes RTP.

```
dtmfmode=rfc2833
```

Finally, you can pass DTMF digits inside SIP packets, instead of RTP packets. This method is defined in the RFC3265 (signaling events) and RFC2976.

```
dtmfmode=info
```

Following the release of version 1.2, it is now possible to use:

```
dtmfmode=auto
```

Isso tenta usar o RFC2833; se não for possível, use tons de banda.

#### Configuração de marcação de Qualidade de Serviço (QoS)

QoS é um conjunto de técnicas responsáveis pela qualidade de voz. QoS é implementado de forma a reduzir largura de banda, latência e jitter. As principais funções de QoS são agendamento de pacotes, fragmentação e compressão de cabeçalhos. QoS é implementado em switches e roteadores, não pelo Asterisk propriamente dito. No entanto, o Asterisk pode ajudar roteadores e switches marcando pacotes para entrega prioritária. A marcação é feita usando pontos de código de serviços diferenciados (DSCP) definidos nos RFCs 2474 e RFC2475.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

A partir da versão 1.4, você pode especificar códigos diferentes para sinalização (SIP), áudio (RTP) e vídeo (RTP).

### SIP authentication (sip.conf)

Quando o legado `chan_sip` recebe uma chamada SIP, ele segue as regras descritas no diagrama a seguir. Três parâmetros desempenham um papel importante na autenticação SIP. No Asterisk 22, a autenticação é configurada em vez disso com objetos PJSIP `auth` (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenciados por um endpoint, e o controle de acesso IP é feito com `permit=`/`deny=` no endpoint ou via um `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

Este parâmetro controla se um usuário sem um peer correspondente pode autenticar sem um nome e segredo. Discutimos este parâmetro na seção de suporte a domínios.

```
insecure=invite,port
```

When we use insecure=invite, Asterisk does not generate the message “407 Proxy Authentication Required”. Without this message, the user can make a call without authentication. This is often used to connect to VoIP service providers. The calls coming from the VoIP service provider are usually not authenticated.

```
autocreatepeer=yes/no
```

Este comando é usado quando o Asterisk está conectado a um proxy SIP. Ele cria dinamicamente um peer para cada chamada. Quando esta opção está habilitada, qualquer UAC pode conectar ao servidor Asterisk. É importante limitar a conexão IP ao proxy SIP. O proxy SIP, por sua vez, cuida do controle de acesso. A configuração do peer baseia‑se nas opções gerais, bem como no campo de cabeçalho “Contact” do pacote SIP. Aviso: use isso com extrema cautela, pois abre completamente o Asterisk.

```
secret=secret, remotesecret=secret
```

Este parâmetro configura o secret para uso de autenticação, use secret para solicitações inbound e remotesecret para solicitações outbound. Se você não quiser apresentar os secrets em arquivos de texto, pode usar md5secret para incluir um hash em vez do secret. Para gerar o secret MD5, você pode usar:

```
echo -n "username:realm:secret" |md5sum
```

Em seguida, use a seguinte instrução:

```
md5secret=0b0e5d467890....
```

Aviso: Não se esqueça de usar o parâmetro –n; o retorno de carro será usado no cálculo do md5.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

As declarações acima negarão todos os endereços IP e permitirão UAC apenas da rede local (192.168.1.0/24).

#### Opções RTP

É possível controlar alguns parâmetros RTP.

```
rtptimeout=60
```

Isso encerra chamadas sem atividade RTP por mais de 60 segundos quando não está em espera.

```
rtpholdtimeout=120
```

Isso encerra chamadas sem atividade de RTP mesmo em espera (deve ser maior que rtptimeout).

### SIP NAT traversal (sip.conf)

A *teoria* NAT (os quatro tipos de NAT, o problema do cabeçalho Contact, keep-alives e forçar a mídia através do servidor) está no nível do protocolo e é abordada no capítulo *SIP & PJSIP in depth*. Os parâmetros `sip.conf` mostrados aqui (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) são **legacy chan_sip** e foram removidos no Asterisk 21+. No PJSIP eles correspondem a configurações de transporte/endpoint como `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address` e `local_net=` no transporte, além de `qualify_frequency=` no AOR.

No legacy chan_sip, o parâmetro `nat` tinha cinco opções:

- nat = no — Não fazer tratamento especial de NAT além do RFC3581
- nat = force_rport — Fingir que havia um parâmetro rport mesmo que não exista
- nat = comedia — Enviar mídia para a porta de onde o Asterisk a recebeu, independentemente de onde o SDP indique enviá‑la.
- nat = auto_force_rport — Definir a opção force_rport se o Asterisk detectar NAT (padrão)
- nat = auto_comedia — Definir a opção comedia se o Asterisk detectar NAT

Quando você coloca a instrução “nat=force_rport” no arquivo sip.conf, está dizendo ao Asterisk para ignorar o endereço contido no campo de cabeçalho “Contact” do cabeçalho SIP e usar o endereço IP de origem e a porta no cabeçalho IP do pacote, além de enviar a mídia de volta para o endereço de onde foi recebida, ignorando o conteúdo do cabeçalho SDP.

```
nat=force_rport,comedia
```

É necessário manter o mapeamento NAT aberto. Se o NAT expirar, o Asterisk não pode enviar um invite para o UAC. O UAC consegue enviar chamadas, mas não receber nenhuma. A instrução a seguir pode ser usada para manter o NAT aberto.

```
qualify=yes
```

Qualify enviará um pacote SIP usando o método OPTIONS regularmente, o que ajudará a manter o NAT aberto. Qualify envia um OPTIONS a cada 60 segundos e a cada 10 segundos quando o host não está acessível. Você pode usar “sip show peers” para ver a latência dos peers. Se o NAT do usuário for do tipo simétrico, não é possível enviar pacotes de um UAC para outro diretamente; nesse caso, você deve forçar o RTP através do Asterisk usando:

```
directmedia=no
```

#### Asterisk behind NAT (sip.conf)

Todos os cenários anteriores presumem que o servidor Asterisk possui um endereço externo (válido) na Internet. Às vezes o servidor Asterisk é implementado atrás de um firewall com NAT. Nesse caso, é necessário fazer algumas configurações extras.

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. Configure o firewall para redirecionar a porta UDP 5060 de forma estática para o servidor Asterisk.  
2. Configure o firewall para redirecionar as portas UDP de 10000 a 20000 de forma estática.

Se você quiser limitar o número de portas abertas, pode editar o arquivo `rtp.conf` para alterar o intervalo de portas RTP. Outra alternativa é usar um firewall inteligente que suporte o protocolo SIP para abrir as portas RTP dinamicamente.

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

Etapa 3: Configure o Asterisk para incluir o endereço externo nos campos de cabeçalho dos pacotes SIP, incluindo o Session Description Protocol (SDP). Você pode fazer isso adicionando as duas declarações a seguir ao arquivo sip.conf:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

O primeiro parâmetro `externaddr` indica ao Asterisk que inclua o endereço IP externo nos cabeçalhos SIP para destinos externos. O segundo parâmetro `localnet` permite ao Asterisk diferenciar entre endereços externos e internos. Opcionalmente, você pode usar `externhost` se utilizar um DNS Dinâmico com um endereço DHCP no servidor.

### SIP dial strings (chan_sip)

A tecnologia de dial-string `SIP/...` mostrada abaixo é o driver chan_sip removido. No Asterisk 22 use a tecnologia `PJSIP/...` — por exemplo `Dial(PJSIP/2000)` ou `Dial(PJSIP/${EXTEN}@provider)`. As formas e o significado são, de outra forma, análogos.

Você pode chamar um destino SIP legado usando diferentes dial strings:

```
SIP/peer
```

- ; Necessário ter um peer definido em sip.conf

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Exemplos incluem:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migrando um sistema legado chan_sip para PJSIP

Porque `chan_sip` foi removido no Asterisk 21 e não existe mais no Asterisk 22, qualquer implantação `sip.conf` existente deve ser migrada para PJSIP. A maior mudança conceitual é que um único `sip.conf` `[peer]` ou `[friend]` é dividido em vários objetos PJSIP, cada um com um `type=`: um **endpoint** (configurações de chamada/código/ mídia), um ou mais objetos **aor** (onde o dispositivo pode ser alcançado / registro), um objeto **auth** (credenciais) e um **transport** compartilhado (o socket de escuta, endereços NAT). A tabela a seguir mapeia os conceitos mais comuns.

| Conceito legado sip.conf | Equivalente PJSIP (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (referenciado via `auth=` e `aors=`) |
| `type=friend` / `type=peer` / `type=user` | um único `type=endpoint` (PJSIP não tem distinção friend/peer/user) |
| `host=dynamic` (dispositivo registra) | `type=aor` com `max_contacts=1`; o dispositivo REGISTERs para atualizar seu contato |
| `host=<ip/hostname>` (estático) | `type=aor` com um `contact=sip:host:port` estático |
| `register=>user:secret@host/ext` (outbound) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` no endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` no endpoint (mesma sintaxe) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — também `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` no endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (segundos) no **aor** |
| `externaddr=` | `external_media_address=` e `external_signaling_address=` no **transport** |
| `localnet=` | `local_net=` no **transport** |
| `insecure=invite` (provedor, sem auth) | omitir `auth=`/`outbound_auth=` e usar `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (usar com cuidado) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (e `cos_audio` / `cos_video`) no endpoint |

Uma extensão de registro que se parecia com isso no legado `sip.conf`:

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

torna‑se o seguinte em `pjsip.conf` no Asterisk 22:

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### O script de conversão sip_to_pjsip.py

Asterisk fornece um script auxiliar, **`sip_to_pjsip.py`**, que lê um **`sip.conf`** existente e produz um **`pjsip.conf`**. Você pode executá‑lo diretamente no diretório /etc/asterisk. O utilitário está na árvore de código‑fonte do Asterisk em **`contrib/scripts/sip_to_pjsip/`**, onde **`${PATH_TO_ASTERISK_SOURCE}`** é o caminho onde os arquivos fonte do Asterisk são encontrados (geralmente /usr/src/asterisk-22.x.y/).

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

Se você executá‑lo com a opção `--help` verá suas opções:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

Ele também aceita argumentos posicionais opcionais — `[input-file [output-file]]`,
padronizando para `sip.conf` e `pjsip.conf` no diretório atual.

Trate sua saída como um **ponto de partida**: revise cada objeto gerado,
especialmente transportes, configurações NAT e listas de codecs, e teste minuciosamente antes
de colocar em produção.

Vamos migrar o sip.conf em nossos laboratórios companheiros na VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.flagonc.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

Embora a conversão pareça ok, podemos ver que alguns elementos, como qualify=yes, não podem ser mapeados diretamente. Para corrigir, você deve adicionar à seção aor o comando qualify_frequency=time em segundos. Exemplo abaixo.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

Full PJSIP configuration is covered in the *SIP & PJSIP in depth* chapter, and the official documentation at docs.asterisk.org has full coverage of the channel. In our companion labs at voip.school, lab 5 lets you practice what you have just learned.

## Summary

Este capítulo reúne as tecnologias de canal que antecedem as implantações puras de VoIP de hoje, mas que o Asterisk 22 ainda suporta. Você viu como linhas e telefones **analógicos** se conectam através de interfaces **FXO/FXS** no DAHDI, como links **digitais TDM** (E1/T1 e ISDN PRI/BRI) são provisionados, e como **IAX2** (`chan_iax2`) ainda serve como um tronco servidor‑para‑servidor eficiente e amigável a NAT, embora agora seja claramente legado. Você também revisitou o driver **`chan_sip`** aposentado e sua sintaxe `sip.conf` — que encontrará em sistemas mais antigos, mas que não existe mais no Asterisk 22 — e trabalhou na migração de tal sistema para PJSIP usando a tabela de mapeamento de conceitos e o script `sip_to_pjsip.py`. A regra prática: recorra a qualquer item deste capítulo somente quando hardware real ou um sistema legado existente exigir; tudo que for novo deve ser PJSIP sobre IP.

## Quiz

1. Regarding the two analog Foreign eXchange interfaces, mark the correct statements (choose all that apply):
   - A. An FXO interface connects to the public switched telephone network (PSTN) central office and draws dial tone from it.
   - B. An FXS interface provides dial tone and ringing power to a standard analog phone, fax, or modem.
   - C. An FXS interface is the correct way to connect Asterisk to a telco line.
   - D. An FXO interface can also be connected to an extension port of a legacy PBX.
2. Supervision signaling on an analog line includes which of the following (choose all that apply)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, pops, and noise on a DAHDI analog card are most often caused by:
   - A. The way Asterisk was compiled
   - B. PCI interrupt conflicts
   - C. An incorrect SIP codec
   - D. A missing dial plan
4. For precise billing on analog channels you must detect exactly when the far end answers. Which feature do you activate on Asterisk (and request from the telco) to do this?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial-tone generation
5. The DAHDI hardware is independent of Asterisk: the physical card is configured in `/etc/dahdi/system.conf`, while `chan_dahdi.conf` defines the Asterisk channels, not the hardware itself.
   - A. True
   - B. False
6. Regarding digital trunk capacity and signaling, mark the correct statements (choose all that apply):
   - A. An E1 trunk carries 30 voice channels and a T1 trunk carries 24.
   - B. An ISDN PRI uses 30B+D on an E1 and 23B+D on a T1.
   - C. ISDN is an example of CCS signaling, while MFC/R2 is an example of CAS signaling.
   - D. T1 is the digital trunk most commonly used in Europe and Latin America.
7. Which utility automatically detects DAHDI cards and generates `/etc/dahdi/system.conf` and `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. When migrating a legacy `sip.conf` `[friend]` to PJSIP, a single block must be split into several objects. Which set of PJSIP `type=` objects normally replaces one registering `[friend]`?
   - A. `type=endpoint`, `type=aor`, and `type=auth`
   - B. `type=peer` and `type=user`
   - C. `type=sip` only
   - D. `type=channel` and `type=device`
9. What is the main practical advantage of using IAX2 trunk mode between two Asterisk servers?
   - A. It encrypts every call with TLS by default
   - B. It carries several calls under a single header, saving bandwidth
   - C. It removes the need for any codec
   - D. It allocates a separate UDP port per call for better quality
10. RSA keys can be used for IAX2 authentication. Which key must you keep secret, and which do you give to the other server?
    - A. Keep the public key secret; share the private key
    - B. Keep the private key secret; share the public key
    - C. Keep the shared key secret; share the private key
    - D. Both keys must be shared

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
