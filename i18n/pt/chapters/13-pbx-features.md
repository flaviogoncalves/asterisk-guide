# Usando recursos de PBX

Em sistemas SIP, a maioria dos recursos de telefonia é implementada no endpoint. Existe uma variedade de telefones SIP e fabricantes, e a interoperabilidade não é garantida. A equipe de desenvolvimento do Asterisk fez um trabalho incrível ao implementar a maioria dos recursos no próprio PBX, tornando o Asterisk quase independente do endpoint. No entanto, às vezes você encontrará a mesma função sendo executada tanto pelo telefone quanto pelo próprio Asterisk. A integração do telefone e do PBX é a próxima fronteira em usabilidade e onde os sistemas proprietários estão focando agora. Neste capítulo, você aprenderá como usar a maioria desses recursos.

## Objetivos

Ao final deste capítulo, você será capaz de entender e usar:

- Estacionamento de chamadas (Call Parking)
- Captura de chamadas (Call Pickup)
- Transferência de chamadas (Call Transfer)
- Conferência de chamadas (ConfBridge)
- Gravação de chamadas (Call Recording)
- Música de espera (Music on hold)

## Onde os recursos são implementados

Primeiro e mais importante, é importante entender quando os recursos do PBX estão sendo executados versus quando o telefone está fazendo todo o trabalho. Por exemplo, você pode transferir uma chamada usando o botão TRANSFER no telefone ou discando # (transferência incondicional executada pelo próprio PBX).

## Recursos implementados pelo Asterisk

Estes recursos são implementados no PBX pelo código do Asterisk:

- Música de espera
- Estacionamento de chamadas
- Captura de chamadas
- Gravação de chamadas
- Sala de conferência ConfBridge
- Transferência de chamadas (cega e consultiva)

## Recursos geralmente implementados pelo dialplan

Estes recursos precisam ser programados no dialplan do Asterisk (extensions.conf):

- Encaminhamento de chamada ocupada
- Encaminhamento de chamada imediato
- Encaminhamento de chamada não atendida
- Filtragem de chamadas (blacklist)
- Não perturbe
- Rediscagem

## Recursos geralmente implementados pelo telefone

Estes recursos são implementados pelo firmware do telefone:

![Onde os recursos do PBX são geralmente implementados: no próprio Asterisk, no dialplan ou no telefone](../images/13-pbx-features-fig01.png)

- Chamada em espera
- Transferência cega
- Transferência consultiva
- Conferência de três vias
- Indicador de mensagem em espera

## O arquivo de configuração de recursos

Alguns dos recursos apresentados neste capítulo são configurados no arquivo de configuração features.conf. É possível alterar o comportamento de alguns recursos modificando este arquivo. Incluímos o trecho relevante abaixo. Nas próximas seções deste capítulo, descreveremos cada recurso. Trecho do arquivo de exemplo (Asterisk 22)

![A seção `[featuremap]` do features.conf, com os códigos de recurso DTMF padrão](../images/13-pbx-features-fig02.png)

> **[Nota da 2ª ed.]** A partir do Asterisk 12+, o estacionamento de chamadas foi movido de `features.conf`/`app_features` para seu próprio módulo `res_parking` com configuração em `res_parking.conf`. O bloco parking-lot abaixo (parkext, parkpos, context, parkingtime, etc.) reside em `res_parking.conf` e é mostrado usando a sintaxe do Asterisk 22 `res_parking.conf.sample`. A seção `[featuremap]` (os códigos de recurso DTMF, incluindo `parkcall`) permanece em `features.conf`.

As opções de parking-lot residem em `res_parking.conf`. Um estacionamento chamado `default` sempre existe, mesmo que não esteja presente no arquivo de configuração. O trecho abaixo foi retirado do Asterisk 22 `res_parking.conf.sample`:

```
; res_parking.conf
[default]                       ; Default Parking Lot
parkext => 700                  ; What extension to dial to park. (optional; if
                                ; specified, extensions will be created for parkext and
                                ; the whole range of parkpos)
parkpos => 701-720              ; What range of parking spaces to use - must be numeric.
                                ; Creates these spaces as extensions if parkext is set.
context => parkedcalls          ; Which context parked calls and the default park
                                ; extension are created in
;parkingtime => 45             ; Number of seconds a call can be parked before returning
;comebacktoorigin = yes        ; When a parked call times out, attempt to send it back to
                               ; the peer that parked it (default is yes)
;courtesytone = beep           ; Sound file to play when someone picks up a parked call
;parkedplay = caller           ; Who to play courtesytone to: parked, caller, both (default caller)
;parkedcalltransfers = caller  ; Enable DTMF transfers when picking up a parked call (default no)
;parkedcallreparking = caller  ; Enable DTMF parking when picking up a parked call (default no)
;parkedcallhangup = caller     ; Enable DTMF hangups when picking up a parked call (default no)
;findslot => next              ; 'next' uses the next space after the most recently used one;
                               ; 'first' (default) uses the lowest-numbered space available
;parkedmusicclass = default    ; MOH class to use for the parked channel
```

Os códigos de recurso DTMF (incluindo o de um passo `parkcall`) permanecem na seção `[featuremap]` de `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t
option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option
in the Dial() or Queue() app call!
;automon => *1                  ; One Touch Record a.k.a. Touch Monitor -- Make sure to set the W
and/or w option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Transferência de chamadas

A transferência de chamadas pode ser implementada pelo telefone, por ATA ou pelo próprio Asterisk. Consulte o manual do seu telefone para entender como as chamadas são transferidas. Se o seu telefone não suportar transferência de chamadas, você pode usar o Asterisk para realizar esta tarefa. A transferência de chamadas é implementada de duas maneiras diferentes. A primeira maneira é usar o recurso de transferência cega: disque # seguido pelo número para o qual a chamada será transferida. Às vezes, você usará o recurso de transferência do seu telefone IP ou softphone IP. Você pode alterar o caractere de transferência editando o parâmetro blindxfer no arquivo features.conf. Você pode habilitar a transferência assistida no Asterisk removendo o ; antes do parâmetro atxfer no arquivo features.conf. Durante uma conversa, você pressionaria *2. O Asterisk dirá "transfer" e lhe dará um tom de discagem. O chamador é enviado para a música de espera. Depois de falar com a pessoa de destino e desligar o telefone, o sistema faz a ponte entre o chamador e o destino.

![Transferência de chamadas: os passos para uma transferência cega (pressione # durante a chamada) e uma transferência assistida (pressione *2)](../images/13-pbx-features-fig03.png)

### Lista de tarefas de configuração

1. Se o telefone for baseado em SIP, certifique-se de que a opção directmedia seja igual a no ou use uma opção t ou T na aplicação dial()

## Estacionamento de chamadas

Este recurso é usado para estacionar uma chamada. Isso ajuda, por exemplo, quando você está atendendo a uma chamada telefônica fora da sua sala e deseja transferir a chamada de volta para sua mesa. Você pode realizar isso estacionando a chamada em um ramal. Assim que chegar à sua mesa, basta discar o número do ramal de estacionamento para recuperar a chamada.

![Estacionamento de chamadas: disque 700 para estacionar uma chamada no primeiro slot livre (701–720); o Asterisk anuncia o slot, que você disca de qualquer telefone para recuperar a chamada](../images/13-pbx-features-fig04.png)

Por padrão, o ramal 700 é usado para estacionar uma chamada. No meio de uma conversa, pressione # para transferir a chamada para o ramal 700. Agora o Asterisk anunciará seu ramal de estacionamento, como 701 ou 702. Desligue o telefone e o chamador será colocado em espera. Vá até o telefone da sua mesa e disque o ramal de estacionamento anunciado para recuperar a chamada. Se o chamador ficar estacionado por muito tempo, o recurso de timeout será acionado e o ramal original discado tocará novamente.

### Lista de tarefas de configuração

Siga os passos abaixo para habilitar o estacionamento de chamadas. Passo 1: Torne o estacionamento acessível a partir do seu dialplan (obrigatório). O `context` do estacionamento padrão é `parkedcalls` (definido em `res_parking.conf`). Inclua esse context no contexto a partir do qual seus telefones discam, em `extensions.conf`:

```
include => parkedcalls
```

Passo 2: Teste o recurso de estacionamento de chamadas discando #700. Notas:

- O ramal de estacionamento não será mostrado no comando CLI dialplan show.
- É necessário recarregar o módulo de estacionamento após alterar o arquivo de configuração de estacionamento: `module reload res_parking.so`. Para alterações no features.conf, `module reload features.so`.
- Para estacionar uma chamada, você precisa transferir para #700. Verifique as opções t e T na aplicação dial().

## Captura de chamadas

A captura de chamadas permite que você capture uma chamada de um colega no mesmo grupo de chamada. Isso ajudaria a evitar, por exemplo, ter que se levantar para atender a uma chamada que está tocando para outra pessoa na sua sala, mas que não está presente. Ao discar *8, você pode capturar uma chamada dentro do seu grupo de chamada. Este número pode ser modificado no

```
features.conf file.
```

![Captura de chamadas: os membros só podem capturar chamadas dentro do seu próprio grupo; o operador (pickupgroup=1,2,3) pode capturar chamadas de todos os grupos](../images/13-pbx-features-fig05.png)

### Lista de tarefas de configuração

Siga os passos abaixo para configurar o recurso de captura de chamadas. Passo 1: Configure um grupo de chamada para seus ramais. Isso é feito no arquivo de configuração do canal (pjsip.conf, iax.conf, chan_dahdi.conf). Para endpoints PJSIP, defina `call_group` e `pickup_group` na seção endpoint de `pjsip.conf` (pjsip.conf usa nomes de opção em snake_case). Esta tarefa é obrigatória.

Para PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Passo 2: Altere o número do recurso de captura de chamadas (opcional).

```
pickupexten=*8; Configures the call pickup extension
```

## Conferência (conferência de chamadas)

Existem diferentes maneiras de implementar uma conferência no Asterisk. A primeira opção é simplesmente usar a capacidade de conferência de três vias do telefone. Ao usar este recurso no telefone, você não precisa de nenhum suporte no próprio servidor. No entanto, quando você deseja uma conferência com mais de 3 pessoas, você deve executar uma sala de conferência. A aplicação de conferência moderna do Asterisk é a ConfBridge (`app_confbridge`).

O ConfBridge suporta conferências de voz HD e videoconferência. Existem algumas limitações para videoconferência, como a ausência de transcodificação — todos os participantes devem usar o mesmo codec e perfil. A videoconferência usa um modo "follow-the-talker", exibindo a imagem da última pessoa a falar. Você pode configurar facilmente novos menus DTMF no ConfBridge.

> **[Nota da 2ª ed.]** O MeetMe (`app_meetme`) foi **descontinuado no Asterisk 19** e estava programado para remoção no Asterisk 21, mas essa remoção foi pausada (a pedido do projeto ViciDial). O código-fonte do módulo ainda é enviado com o Asterisk 22, mas ele requer DAHDI e **não é compilado na compilação padrão do Asterisk 22** — uma instalação padrão não possui `app_meetme.so` e a aplicação `MeetMe()` está indisponível. Todas as novas implementações de salas de conferência devem usar o ConfBridge. A seção MeetMe abaixo é mantida apenas para referência histórica.

### Confbridge

Para iniciar uma sala de conferência, a sintaxe está listada abaixo.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Para obter uma descrição completa do comando, você pode usar core show application confbridge.

![Saída de `core show application confbridge`, mostrando a sinopse, sintaxe e os argumentos bridge_profile, user_profile e menu](../images/13-pbx-features-fig06.png)

Como você pode ver acima, existem três seções importantes: Bridge_profile: Você define o perfil no arquivo confbridge.conf. Lá você pode selecionar o número máximo de participantes, gravação, video_mode e muitos outros parâmetros de bridge.

Não faz sentido reproduzir o arquivo de exemplo completo aqui, então deixe-me dar um exemplo simples de como configurar um bridge_profile no arquivo confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

User_profile: Aqui você define opções que são específicas por usuário, como se o usuário é um administrador ou não. Música de espera e muitas outras opções podem ser definidas por usuário. Exemplo:

```
[admin_user]
type=user
admin=yes
```

Menu: Na seção menu, você pode definir seu mapeamento de teclado para a aplicação, onde alternar entre mudo e não mudo. Verifique o arquivo confbridge.conf para ver as opções. Exemplo:

```
[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
4=decrease_talking_volume
5=increase_talking_volume
6=leave_conference
```

#### Funções do Confbridge

As opções da bridge de conferência podem ser passadas dinamicamente no dialplan usando a função CONFBRIDGE(). Veja os exemplos abaixo:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

## Meetme (Legado — descontinuado, não compilado por padrão no Asterisk 22)

> **[Nota da 2ª ed.]** `app_meetme` foi descontinuado no Asterisk 19. Sua remoção planejada no Asterisk 21 foi pausada, então o código-fonte ainda é enviado no Asterisk 22, mas o módulo não é compilado na compilação padrão do Asterisk 22 (ele depende do DAHDI). Portanto, uma instalação padrão do Asterisk 22 não possui a aplicação `MeetMe()`. O conteúdo abaixo é mantido para referência histórica e para leitores que estão atualizando sistemas mais antigos. **Para novas instalações, use o ConfBridge (veja acima).** A dependência DAHDI e o módulo `dahdi_dummy` não são necessários para o ConfBridge.

Alternativamente, em versões mais antigas do Asterisk, você poderia usar a aplicação meetme(). Meetme é uma bridge de conferência muito simples de usar. Lembre-se, o meetme foi descontinuado no Asterisk 19 e depende do módulo DAHDI para sincronização.

![Tipos de conferência MeetMe — conferências de alto-falante único, protegidas por senha e dinâmicas — todas exigindo uma fonte de temporização Zaptel/DAHDI](../images/13-pbx-features-fig07.png)

### A aplicação meetme()

Usando o comando CLI meetme show, você pode obter a descrição acima. Para usar o meetme, você precisa compilar os drivers DAHDI e ter pelo menos um módulo de kernel DAHDI carregado. Se você não tiver pelo menos uma placa DAHDI instalada, carregue o módulo de kernel dahdi_dummy para fornecer uma fonte de temporização. Descrição:

![A aplicação MeetMe(): sintaxe `MeetMe([confno][,[options][,pin]])` e suas principais flags de opção](../images/13-pbx-features-fig08.png)

A aplicação meetme() coloca o usuário em uma conferência meetme especificada. Se o número da conferência for omitido, o usuário será solicitado a inserir um. O usuário pode sair da conferência desligando ou — se a opção p for especificada — pressionando #. Observe: Os módulos de kernel DAHDI e pelo menos um driver de hardware (ou dahdi_dummy) devem estar presentes para que a conferência funcione corretamente. Além disso, o driver de canal chan_dahdi deve estar carregado para que as opções i e r funcionem.

> **[Nota da 2ª ed.]** As listas de flags de opção e comandos de administrador que seguem descrevem a interface legada `app_meetme` e refletem a documentação histórica de `MeetMe()`/`MeetMeAdmin()`. Como `app_meetme` não é compilado na instalação padrão do Asterisk 22, essas flags não podem ser confirmadas em um sistema Asterisk 22 em execução; elas são reproduzidas para leitores que mantêm implementações mais antigas. No Asterisk 22, use o ConfBridge e a função de dialplan `CONFBRIDGE()`.

A string de opção pode conter zero ou uma ou mais das seguintes letras:

- 'a' -- define o modo administrador
- 'A' -- define o modo marcado
- 'b' – executa o script AGI especificado em ${MEETME_AGI_BACKGROUND}Padrão: conf-background.agi (Nota: Isso não funciona com canais não-DAHDI na mesma conferência)
- 'c' -- anuncia a contagem de usuário(s) ao entrar em uma conferência
- 'd' -- adiciona conferência dinamicamente
- 'D' -- adiciona conferência dinamicamente, solicitando um PIN
- 'e' -- seleciona uma conferência vazia
- 'E' -- seleciona uma conferência vazia sem PIN
- 'i' -- anuncia um usuário entrando/saindo com revisão
- 'I' -- anuncia um usuário entrando/saindo sem revisão
- 'l' -- define o modo apenas escuta (Listen only, sem falar)
- 'm' -- define inicialmente mudo
- 'M' -- habilita música de espera quando a conferência tem um único chamador
- 'o' -- define a otimização de falante, que trata os falantes que não estão falando como mudos, significando (a) nenhuma codificação é feita na transmissão e (b) o áudio recebido que não é registrado como falando é omitido, não causando acúmulo de ruído de fundo
- 'p' -- permite que os usuários saiam da conferência pressionando '#'
- 'P' -- sempre solicita o PIN, mesmo que seja especificado
- 'q' -- modo silencioso (não toca sons de entrada/saída)
- 'r' -- Grava a conferência (grava como ${MEETME_RECORDINGFILE}usando o formato ${MEETME_RECORDINGFORMAT}). O nome de arquivo padrão é meetme-conf-rec-${CONFNO}-${UNIQUEID} e o formato padrão é wav.
- 's' -- Apresenta menu (usuário ou administrador) quando '*' é recebido ('send' para o menu)
- 't' -- define o modo apenas fala. (Talk only, sem ouvir)
- 'T' -- define a detecção de falante (enviado para a interface do gerenciador e lista meetme)
- 'w[(<secs>)]' -- aguarda até que o usuário marcado entre na conferência
- 'x' -- fecha a conferência quando o último usuário marcado sai
- 'X' -- permite que o usuário saia da conferência inserindo um ramal de um dígito válido ${MEETME_EXIT_CONTEXT} ou o contexto atual se essa variável não estiver definida.
- '1' -- não toca mensagem quando a primeira pessoa entra

### Arquivo de configuração Meetme

Este arquivo é usado para configurar a aplicação meetme. Por exemplo:

```
;
; Configuration file for MeetMe simple conference rooms for Asterisk of course.
;
; This configuration file is read every time you call app meetme()
[general]
;audiobuffers=32        ; The number of 20ms audio buffers to be used
                        ; when feeding audio frames from non-DAHDI channels
                        ; into the conference; larger numbers will allow
                        ; for the conference to 'de-jitter' audio that arrives
                        ; at different timing than the conference's timing
                        ; source, but can also allow for latency in hearing
                        ; the audio from the speaker. Minimum value is 2,
                        ; maximum value is 32.
;
[rooms]
;
; Usage is conf => confno[,pin][,adminpin]
;
conf=>9000
conf=>9001,123456
```

Não é necessário usar reload ou restart para fazer o Asterisk ver as alterações no arquivo meetme.conf.

### Aplicações relacionadas ao Meetme

A aplicação meetme() tem duas outras aplicações de suporte.

```
MeetMeCount(confno[|var])
```

Isso toca o número de usuários na conferência. Se uma variável for especificada, ela não toca a mensagem, mas define o número de usuários para ela.

```
MeetMeAdmin(confno,command,[user]):
```

Execute o comando de administrador para uma conferência:

- 'e' -- Ejeta o último usuário que entrou
- 'k' -- Expulsa um usuário da conferência
- 'K' -- Expulsa todos os usuários da conferência
- 'l' -- Desbloqueia a conferência
- 'L' -- Bloqueia a conferência
- 'm' -- Tira o mudo de um usuário
- 'M' -- Coloca um usuário no mudo
- 'n' -- Tira o mudo de todos os usuários na conferência
- 'N' -- Coloca todos os usuários não administradores no mudo na conferência
- 'r' -- Redefine as configurações de volume de um usuário
- 'R' -- Redefine as configurações de volume de todos os usuários
- 's' -- Diminui o volume de fala de toda a conferência
- 'S' -- Aumenta o volume de fala de toda a conferência
- 't' -- Diminui o volume de fala de um usuário
- 'T' -- Diminui o volume de fala de todos os usuários
- 'u' -- Diminui o volume de escuta de um usuário
- 'U' -- Diminui o volume de escuta de todos os usuários
- 'v' -- Diminui o volume de escuta de toda a conferência
- 'V' -- Aumenta o volume de escuta de toda a conferência

### Lista de tarefas de configuração do Meetme

Siga os passos abaixo para configurar a aplicação de conferência meetme. Passo 1: Escolha o ramal para a sala Meetme (obrigatório) Passo 2: Edite o arquivo meetme.conf para configurar as senhas (opcional)

### Exemplos

Exemplo #1: Sala meetme simples 1. No arquivo extensions.conf, crie a sala de conferência 101

```
exten=>500,1,MeetMe(101,,123456)
```

2. No arquivo meetme.conf, estabeleça a senha para a sala 101. Nota importante: A aplicação meetme() precisa de um temporizador para funcionar. Se você não tiver hardware digium instalado e configurado, use dahdi_dummy como fonte de temporização.

## Gravação de chamadas

Existem várias maneiras de gravar uma chamada no Asterisk. Você pode usar a aplicação mixmonitor() para gravar chamadas facilmente.

### Usando a aplicação mixmonitor

A aplicação mixmonitor grava o áudio no canal atual para o arquivo especificado. Se o nome do arquivo for um caminho absoluto, ele usa esse caminho. Caso contrário, ele cria o arquivo no diretório de monitoramento configurado em asterisk.conf.

![A aplicação MixMonitor(): grava e mixa o áudio de um canal para um arquivo, com opções para anexar, apenas em bridge e ajuste de volume](../images/13-pbx-features-fig09.png)

### Mixmonitor()

Grave uma chamada e mixe o áudio durante a gravação [Descrição] MixMonitor(<file>.<ext>[|<options>[|<command>]]) Grava o áudio no canal atual para o arquivo especificado. opções: a- Anexa ao arquivo em vez de sobrescrevê-lo. b- Salva áudio no arquivo apenas enquanto o canal estiver em bridge. Nota: não inclui conferências. v(<x>) - Ajusta o volume ouvido por um fator de <x> V(<x>) - Ajusta o volume falado por um fator de <x> W(<x>) - Ajusta ambos os volumes, ouvido e falado, por um fator de <x> Opções válidas:

- a - Anexa ao arquivo em vez de sobrescrevê-lo.
- b - Salva áudio no arquivo apenas enquanto o canal estiver em bridge.
- Nota: não inclui conferências.
- v(<x>) - Ajusta o volume audível por um fator de <x> (variando de -4 a 4)
- V(<x>) - Ajusta o volume falado por um fator de <x> (variando de -4 a 4)
- W(<x>) - Ajusta ambos os volumes, audível e falado, por um fator de <x> (variando de -4 a 4)
- <command> será executado quando a gravação terminar. Quaisquer strings correspondentes a ^{X} serão desescapadas para ${X} e todas as variáveis serão avaliadas naquele momento. A variável MIXMONITOR_FILENAME conterá o nome do arquivo usado para gravar.

Um recurso interessante é o automon, que permite que você simplesmente disque *1 para iniciar a gravação imediatamente. Exemplo:

```
exten=>_4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten=>_4XXX,2,Dial(PJSIP/${EXTEN},20,jtTwW);wW enables the recording.
```

Os canais de áudio são de entrada (IN) e saída (OUT) e são separados em dois arquivos distintos no diretório /var/spool/asterisk/monitor. Ambos os arquivos podem ser mixados usando a aplicação sox.

```
debian#soxmix *in.wav *out.wav output.wav
```

Se você não quiser usar Set() antes da aplicação Dial(), você pode definir isso na seção globals:

```
[globals]
DYNAMIC_FEATURES=>automon
```

### Música de espera

A música de espera (MOH) mudou várias vezes entre as versões 1.0, 1.2 e 1.4. Na versão mais recente, a MOH é "FILE-BASED" por padrão. Em outras palavras, o Asterisk fornecerá os arquivos de MOH em formatos como g729, alaw, ulaw e gsm. Assim, não é necessário transcodificar a música antes de enviá-la para o canal. Isso economiza tempo de processador, o que é uma modificação bem-vinda para aqueles que trabalham com sistemas de produção. Em versões mais antigas, a MOH era geralmente fornecida por MP3 (ainda pode ser configurada dessa forma). Fornecer MOH usando MP3 obriga o Asterisk a transcodificar, gastando um valioso poder de CPU no processo. O novo arquivo de configuração é mostrado abaixo. Observe que a classe padrão agora usa o modo de formato de arquivo nativo mode=files. Todos os outros modos estão comentados. Cada seção é uma classe. A única classe não comentada neste momento é a default. Se você quiser ter classes diferentes para arquivos diferentes, precisará criar novas seções (classes).

![A configuração de exemplo musiconhold.conf, listando os modos MOH válidos (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

```
; Music on Hold -- Sample Configuration
;[samplemp3]
;mode=quietmp3
;directory=/var/lib/asterisk/mohmp3
;
; valid mode options:
; quietmp3      -- default
; mp3           -- loud
; mp3nb         -- unbuffered
; quietmp3nb    -- quiet unbuffered
; custom        -- run a custom application (See examples below)
; files         -- read files from a directory in any Asterisk supported
;                  media format. (See examples below)
;[manual]
;mode=custom
; Note that with mode=custom, a directory is not required, such as when reading
; from a stream.
;directory=/var/lib/asterisk/mohmp3
;application=/usr/bin/mpg123 -q -r 8000 -f 8192 -b 2048 --mono -s
;[ulawstream]
;mode=custom
;application=/usr/bin/streamplayer 192.168.100.52 888
;format=ulaw
; mpg123 on Solaris does not always exit properly; madplay may be a better
; choice
;[solaris]
;mode=custom
;directory=/var/lib/asterisk/mohmp3
;application=/site/sw/bin/madplay -Q -o raw:- --mono -R 8000 -a -12
;
;
; File-based (native) music on hold
;
; This plays files directly from the specified directory, no external
; processes are required. Files are played in normal sorting order
; (same as a sorted directory listing), and no volume or other
; sound adjustments are available. If the file is available in
; the same format as the channel's codec, then it will be played
; without transcoding (same as Playback would do in the dialplan).
; Files can be present in as many formats as you wish, and the
; 'best' format will be chosen at playback time.
;
; NOTE:
; If you are not using "autoload" in modules.conf, then you
; must ensure that the format modules for any formats you wish
; to use are loaded _before_ res_musiconhold. If you do not do
; this, res_musiconhold will skip the files it is not able to
; understand when it loads.
;
[default]
mode=files
directory=/var/lib/asterisk/moh
;
;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes     ; Play the files in a random order
```

### Tarefas de configuração de MOH

Agora, para usar música de espera, defina a classe MOH nos arquivos de configuração de canal (chan_dahdi.conf, pjsip.conf, iax.conf, e assim por diante). Para endpoints PJSIP, defina `moh_suggest` na seção endpoint de `pjsip.conf` (o nome de opção legado `musicclass` aplica-se ao chan_dahdi e outros drivers de canal, não ao PJSIP). As músicas freeplay instaladas agora estão no formato wav. No momento da instalação, você pode selecionar (usando make menuselect) os formatos de arquivo MOH disponíveis. Se você quiser adicionar novos arquivos MOH, terá que fornecê-los nos formatos necessários. Por exemplo:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

No dialplan, você pode ouvir a MOH usando o seguinte exemplo:

```
Exten=>100,1,SetMusicOnHold(default)
Exten=>100,2,Dial(DAHDI/2)
```

Para configurar o arquivo extensions.conf para testar a MOH:

```
[local]
exten => 6601,1,WaitMusicOnHold(30)
```

## Mapas de aplicação

Os mapas de aplicação permitem que você adicione novos recursos usando a seção `[applicationmap]` do arquivo features.conf. Suponha que você precise identificar o tipo de cliente que está atendendo em um call center. Você poderia criar um mapa de aplicação para cada tipo de cliente, que poderia contar o número de clientes atendidos por tipo.

## Quiz

1. Quais afirmações são verdadeiras sobre o estacionamento de chamadas?
   - A. Por padrão, o ramal 800 é usado para estacionamento de chamadas.
   - B. Quando você está longe da sua mesa e recebe uma chamada, você pode estacioná-la; o sistema anuncia o slot de estacionamento, e você disca esse slot de qualquer telefone para recuperar a chamada.
   - C. Por padrão, o ramal 700 estaciona uma chamada, e as chamadas são estacionadas nos slots 701–720.
   - D. Você disca 700 para recuperar uma chamada estacionada.
2. Para usar o recurso de captura de chamadas, todos os ramais devem estar no mesmo ___. Para canais DAHDI, isso é configurado no arquivo ___.
3. Ao transferir uma chamada, você pode escolher entre uma transferência ___, onde o destino não é consultado primeiro, e uma transferência ___, onde você fala com o destino antes de concluir.
4. Para fazer uma transferência assistida (consultiva), você usa a sequência ___; para uma transferência cega, você usa ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Para hospedar chamadas em conferência no Asterisk 22, você usa a aplicação ___.
6. No ConfBridge, um participante recebe privilégios de administrador (expulsar, colocar outros no mudo, bloquear a sala) definindo ___ em seu perfil de usuário (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. O melhor formato para música de espera é MP3, porque ele usa muito pouco poder de processamento no servidor Asterisk.
   - A. Verdadeiro
   - B. Falso
8. Para capturar uma chamada de um grupo de chamada específico, você deve estar no grupo de ___ correspondente.
9. Você pode gravar uma chamada com a aplicação MixMonitor() ou o recurso de um toque (automon). Por padrão, o automon usa a sequência DTMF ___.
   - A. *1
   - B. *2
   - C. #3
   - D. #1
10. No ConfBridge, qual opção de perfil de usuário `confbridge.conf` faz com que um participante entre no mudo (eles podem ouvir a conferência, mas não podem ser ouvidos até que o mudo seja removido)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Respostas:** 1 — B, C · 2 — grupo de captura (pickup group); `chan_dahdi.conf` · 3 — cega; assistida · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — captura · 9 — A · 10 — A
