# Usando recursos de PBX

Em sistemas SIP, a maioria dos recursos de telefonia é implementada no endpoint. Existe uma variedade de telefones SIP e fabricantes, e a interoperabilidade não é garantida. A equipe de desenvolvimento do Asterisk fez um trabalho incrível ao implementar a maioria dos recursos no próprio PBX, tornando o Asterisk quase independente do endpoint. No entanto, às vezes você encontrará a mesma função sendo executada tanto pelo telefone quanto pelo próprio Asterisk. A integração do telefone com o PBX é a próxima fronteira em usabilidade e onde os sistemas proprietários estão focando agora. Neste capítulo, você aprenderá como usar a maioria desses recursos.

## Objetivos

Ao final deste capítulo, você será capaz de entender e usar:

- Estacionamento de chamadas (Call Parking)
- Captura de chamadas (Call Pickup)
- Transferência de chamadas (Call Transfer)
- Conferência de chamadas (ConfBridge)
- Gravação de chamadas (Call Recording)
- Música em espera (Music on hold)

## Onde os recursos são implementados

Primeiro e mais importante, é importante entender quando os recursos do PBX estão sendo executados versus quando o telefone está fazendo todo o trabalho. Por exemplo, você pode transferir uma chamada usando o botão TRANSFER no telefone ou discando # (transferência incondicional executada pelo próprio PBX).

## Recursos implementados pelo Asterisk

Estes recursos são implementados no PBX pelo código do Asterisk:

- Música em espera
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
- Filtragem de chamadas (lista negra)
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

Desde o Asterisk 12, o estacionamento de chamadas foi movido para fora do `features.conf` para seu próprio módulo, `res_parking`, com configuração no `res_parking.conf`. O bloco parking-lot abaixo (`parkext`, `parkpos`, `context`, `parkingtime` e assim por diante) reside no `res_parking.conf`. A seção `[featuremap]` (os códigos de recurso DTMF, incluindo `parkcall`) permanece no `features.conf`.

As opções de parking-lot residem no `res_parking.conf`. Um estacionamento chamado `default` sempre existe, mesmo que não esteja presente no arquivo de configuração. O trecho abaixo foi retirado do `res_parking.conf.sample` do Asterisk 22:

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

Os códigos de recurso DTMF (incluindo o `parkcall` de um passo) permanecem na seção `[featuremap]` do `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t
option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option
in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Transferência de chamadas

A transferência de chamadas pode ser implementada pelo telefone, por um ATA ou pelo próprio Asterisk. Consulte o manual do seu telefone para entender como as chamadas são transferidas. Se o seu telefone não suportar transferência de chamadas, você pode usar o Asterisk para realizar esta tarefa. A transferência de chamadas é implementada de duas maneiras diferentes. A primeira maneira é usar o recurso de transferência cega: disque # seguido pelo número para o qual a chamada será transferida. Às vezes, você usará o recurso de transferência do seu telefone IP ou softphone IP. Você pode alterar o caractere de transferência editando o parâmetro blindxfer no arquivo features.conf. Você pode habilitar a transferência assistida no Asterisk removendo o ; antes do parâmetro atxfer no arquivo features.conf. Durante uma conversa, você pressionaria *2. O Asterisk dirá “transfer” e lhe dará um tom de discagem. O chamador é enviado para a música em espera. Depois de falar com a pessoa de destino e desligar o telefone, o sistema conecta o chamador ao destino.

![Transferência de chamadas: os passos para uma transferência cega (pressione # durante a chamada) e uma transferência assistida (pressione *2)](../images/13-pbx-features-fig03.png)

### Lista de tarefas de configuração

1. Para um endpoint PJSIP, certifique-se de que a opção `direct_media` esteja definida como `no` (para que a mídia flua através do Asterisk e os códigos de recurso sejam detectados), ou use uma opção `t`/`T` no aplicativo `Dial()`

## Estacionamento de chamadas

Este recurso é usado para estacionar uma chamada. Isso ajuda, por exemplo, quando você está atendendo uma chamada telefônica fora da sua sala e deseja transferir a chamada de volta para sua mesa. Você pode realizar isso estacionando a chamada em um ramal. Assim que chegar à sua mesa, basta discar o número do ramal de estacionamento para recuperar a chamada.

![Estacionamento de chamadas: disque 700 para estacionar uma chamada no primeiro slot livre (701–720); o Asterisk anuncia o slot, que você disca de qualquer telefone para recuperar a chamada](../images/13-pbx-features-fig04.png)

Por padrão, o ramal 700 é usado para estacionar uma chamada. No meio de uma conversa, pressione # para transferir a chamada para o ramal 700. Agora o Asterisk anunciará seu ramal de estacionamento, como 701 ou 702. Desligue o telefone e o chamador será colocado em espera. Vá até o telefone da sua mesa e disque o ramal de estacionamento anunciado para recuperar a chamada. Se o chamador ficar estacionado por muito tempo, o recurso de timeout será acionado e o ramal originalmente discado tocará novamente.

### Lista de tarefas de configuração

Siga os passos abaixo para habilitar o estacionamento de chamadas. Passo 1: Torne o parking lot acessível a partir do seu dialplan (obrigatório). O `context` do parking lot padrão é `parkedcalls` (definido em `res_parking.conf`). Inclua esse contexto no contexto a partir do qual seus telefones discam, em `extensions.conf`:

```
include => parkedcalls
```

Passo 2: Teste o recurso de estacionamento de chamadas discando #700. Notas:

- O ramal de estacionamento não será exibido no comando CLI dialplan show.
- É necessário recarregar o módulo de estacionamento após alterar o arquivo de configuração de estacionamento: `module reload res_parking.so`. Para alterações no features.conf, `module reload features.so`.
- Para estacionar uma chamada, você precisa transferir para #700. Verifique as opções `t` e `T` no aplicativo `Dial()`.

## Captura de chamadas

A captura de chamadas permite que você capture uma chamada de um colega no mesmo grupo de chamada. Isso ajudaria a evitar, por exemplo, ter que se levantar para atender uma chamada que está tocando para outra pessoa na sua sala, mas que não está presente. Ao discar *8, você pode capturar uma chamada dentro do seu grupo de chamada. Este número pode ser modificado no

```
features.conf file.
```

![Captura de chamadas: os membros só podem capturar chamadas dentro do seu próprio grupo; o operador (pickupgroup=1,2,3) pode capturar chamadas de todos os grupos](../images/13-pbx-features-fig05.png)

### Lista de tarefas de configuração

Siga os passos abaixo para configurar o recurso de captura de chamadas. Passo 1: Configure um grupo de chamada para seus ramais. Isso é feito no arquivo de configuração do canal (pjsip.conf, iax.conf, chan_dahdi.conf). Para endpoints PJSIP, defina `call_group` e `pickup_group` na seção de endpoint do `pjsip.conf` (pjsip.conf usa nomes de opções em snake_case). Esta tarefa é obrigatória.

Para PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Passo 2: Altere o número do recurso de captura de chamadas (opcional). Isso é definido na seção `[general]` do `features.conf`, não no `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conferência (conferência de chamadas)

Existem diferentes maneiras de implementar uma conferência no Asterisk. A primeira opção é simplesmente usar a capacidade de conferência de três vias do telefone. Ao usar este recurso no telefone, você não requer nenhum suporte no próprio servidor. No entanto, quando você deseja uma conferência com mais de 3 pessoas, você deve executar uma sala de conferência. O aplicativo de conferência moderno do Asterisk é o ConfBridge (`app_confbridge`).

O ConfBridge suporta conferências de voz HD e videoconferência. Existem algumas limitações para videoconferência, como a ausência de transcodificação — todos os participantes precisam usar o mesmo codec e perfil. A videoconferência usa um modo "follow-the-talker", exibindo a imagem da última pessoa a falar. Você pode configurar facilmente novos menus DTMF no ConfBridge.

O ConfBridge substitui o antigo aplicativo MeetMe, que foi descontinuado no Asterisk 19 e removido no Asterisk 21. Ao contrário do MeetMe, o ConfBridge **não** requer DAHDI ou uma fonte de temporização de hardware: ele depende da interface de temporização integrada do Asterisk (`res_timing_timerfd` no Linux, ou `res_timing_pthread`), portanto, nenhum módulo `dahdi_dummy` é necessário. Se você estiver migrando de um sistema mais antigo que usava `MeetMe()` e `meetme.conf`, substitua-os por `ConfBridge()` e `confbridge.conf` conforme descrito abaixo.

### ConfBridge

Para iniciar uma sala de conferência, a sintaxe está listada abaixo.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Para obter uma descrição completa do comando, você pode usar core show application confbridge.

![Saída de `core show application confbridge`, mostrando a sinopse, sintaxe e os argumentos bridge_profile, user_profile e menu](../images/13-pbx-features-fig06.png)

![Vários endpoints PJSIP entram em uma conferência ConfBridge nomeada (101); um participante é o administrador. A mixagem e a temporização são tratadas pelo `res_confbridge` e pelo temporizador integrado `res_timing_*` — sem necessidade de DAHDI.](../images/13-pbx-features-fig09.png)

Como você pode ver acima, existem três argumentos importantes, cada um mapeando para um tipo de seção no `confbridge.conf`. **bridge_profile** (uma seção `type=bridge`): aqui você seleciona o número máximo de participantes (`max_members`), gravação (`record_conference`), `video_mode` e muitos outros parâmetros de toda a ponte.

Não faz sentido reproduzir o arquivo de exemplo completo aqui, então deixe-me dar um exemplo simples de como configurar um bridge_profile no arquivo confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (uma seção `type=user`): aqui você define opções que são específicas por usuário, como se o usuário é um administrador (`admin=yes`), se eles começam no mudo (`startmuted=yes`), música em espera e muitas outras opções por usuário. Exemplo:

```
[admin_user]
type=user
admin=yes
```

**menu** (uma seção `type=menu`): aqui você define o mapeamento do teclado (DTMF) para a conferência — por exemplo, qual tecla alterna o mudo, ajusta o volume ou sai da conferência. Verifique o arquivo `confbridge.conf.sample` para ver todas as ações disponíveis. Exemplo:

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

As opções da ponte de conferência podem ser passadas dinamicamente no dialplan usando a função CONFBRIDGE(). Veja os exemplos abaixo:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Comandos de administrador do ConfBridge e migração do MeetMe

Se você vem do MeetMe, as funções de administrador que você usava através do `MeetMeAdmin()` e a opção `a` (admin) agora são expressas através do **perfil de usuário administrador** (`admin=yes`) mais as ações de **menu**. Um administrador que entra com um perfil de administrador e um menu contendo ações de administrador pode bloquear a sala, expulsar usuários e silenciar participantes ao vivo pelo teclado. As ações de menu relevantes no `confbridge.conf` são:

- `admin_kick_last` -- expulsar o último usuário que entrou
- `admin_toggle_mute_participants` -- silenciar/ativar todos os participantes não administradores
- `toggle_mute` -- silenciar/ativar você mesmo
- `participant_count` -- anunciar o número de participantes
- `leave_conference` -- sair da ponte e continuar no dialplan

Estes substituem os sinalizadores de opção do MeetMe `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x`, …) e os comandos `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N`, …). Não existe `meetme.conf` no Asterisk 22; toda a configuração da conferência reside no `confbridge.conf`, e as alterações são aplicadas com `module reload res_confbridge.so`.

### Exemplo de ConfBridge

Para criar uma sala de conferência acessível no ramal 500, no `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

O primeiro chamador a discar 500 cria a conferência `101`; os chamadores subsequentes entram nela. Os perfis e menus referenciados aqui (`default_bridge`, `default_user`, `sample_user_menu`) são definidos no `confbridge.conf`. Para exigir um PIN, defina `pin=` no perfil de usuário; para tornar um participante um administrador da conferência, dê a ele um perfil de usuário com `admin=yes`.

## Gravação de chamadas

Existem várias maneiras de gravar uma chamada no Asterisk. Você pode usar o aplicativo `MixMonitor()` para gravar chamadas facilmente. (O aplicativo mais antigo `Monitor`, que gravava dois arquivos separados, foi removido; use o `MixMonitor` em seu lugar.)

### Usando o aplicativo MixMonitor

O aplicativo `MixMonitor` grava o áudio no canal atual para o arquivo especificado. Se o nome do arquivo for um caminho absoluto, ele usa esse caminho. Caso contrário, ele cria o arquivo no diretório de monitoramento configurado em asterisk.conf.

![O aplicativo MixMonitor(): grava e mixa o áudio de um canal para um arquivo, com opções para anexar, apenas em ponte e ajuste de volume](../images/13-pbx-features-fig09.png)

### MixMonitor()

Grave uma chamada e mixe o áudio durante a gravação. Sintaxe: `MixMonitor(filename.extension[,options[,command]])`. Grava o áudio no canal atual para o arquivo especificado. Opções válidas:

- a - Anexa ao arquivo em vez de sobrescrevê-lo.
- b - Salva áudio no arquivo apenas enquanto o canal estiver em ponte.
- Nota: não inclui conferências.
- v(<x>) - Ajusta o volume audível por um fator de <x> (variando de -4 a 4)
- V(<x>) - Ajusta o volume falado por um fator de <x> (variando de -4 a 4)
- W(<x>) - Ajusta ambos os volumes, audível e falado, por um fator de <x> (variando de -4 a 4)
- <command> será executado quando a gravação terminar. Quaisquer strings correspondentes a ^{X} serão desescapadas para ${X} e todas as variáveis serão avaliadas naquele momento. A variável MIXMONITOR_FILENAME conterá o nome do arquivo usado para gravar.

Um recurso interessante é o recurso de gravação com um toque `automixmon`, que permite que uma parte disque um código DTMF (padrão `*3`) durante uma chamada para iniciar (e alternar) a gravação imediatamente. Ele é construído sobre o MixMonitor, portanto, grava um único arquivo mixado. Exemplo:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

As opções `X` e `x` habilitam o recurso de MixMonitor com um toque para o chamador e o atendido, respectivamente. Como o MixMonitor grava um único arquivo mixado, não há necessidade de combinar arquivos IN/OUT separados posteriormente (a abordagem antiga `automon`/`Monitor`, que produzia dois arquivos para `soxmix`, foi removida junto com o aplicativo `Monitor`).

Se você não quiser usar Set() antes do aplicativo Dial(), você pode definir isso na seção globals:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Música em espera

A música em espera (MOH) mudou várias vezes entre as versões 1.0, 1.2 e 1.4. Na versão mais recente, a MOH é “FILE-BASED” por padrão. Em outras palavras, o Asterisk fornecerá os arquivos MOH em formatos como g729, alaw, ulaw e gsm. Assim, não é necessário transcodificar a música antes de enviá-la para o canal. Isso economiza tempo de processador, o que é uma modificação bem-vinda para aqueles que trabalham com sistemas de produção. Em versões mais antigas, a MOH era geralmente fornecida por MP3 (ainda pode ser configurada dessa forma). Fornecer MOH usando MP3 obriga o Asterisk a transcodificar, gastando um valioso poder de CPU no processo. O novo arquivo de configuração é mostrado abaixo. Observe que a classe padrão agora usa o modo de formato de arquivo nativo mode=files. Todos os outros modos estão comentados. Cada seção é uma classe. A única classe não comentada neste momento é a default. Se você quiser ter classes diferentes para arquivos diferentes, precisará criar novas seções (classes).

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

Agora, para usar a música em espera, defina a classe MOH nos arquivos de configuração de canal (chan_dahdi.conf, pjsip.conf, iax.conf, etc.). Para endpoints PJSIP, defina `moh_suggest` na seção de endpoint do `pjsip.conf` (o nome da opção legada `musicclass` se aplica ao chan_dahdi e outros drivers de canal, não ao PJSIP). As músicas freeplay instaladas agora estão no formato wav. No momento da instalação, você pode selecionar (usando make menuselect) os formatos de arquivo MOH disponíveis. Se você quiser adicionar novos arquivos MOH, terá que fornecê-los nos formatos necessários. Por exemplo:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

No dialplan, você pode iniciar a música em espera em um canal com `StartMusicOnHold` (e pará-la com `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Para reproduzir música em espera por um tempo fixo como um teste rápido, use o aplicativo `MusicOnHold` com uma duração (em segundos):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Mapas de aplicativos

Os mapas de aplicativos permitem que você adicione novos recursos usando a seção `[applicationmap]` do arquivo features.conf. Suponha que você precise identificar o tipo de cliente que está atendendo em um call center. Você poderia criar um mapa de aplicativos para cada tipo de cliente, que poderia contar o número de clientes atendidos por tipo.

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
5. Para hospedar chamadas em conferência no Asterisk 22, você usa o aplicativo ___.
6. No ConfBridge, um participante recebe privilégios de administrador (expulsar, silenciar outros, bloquear a sala) definindo ___ em seu perfil de usuário (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. O melhor formato para música em espera é MP3, porque usa muito pouco poder de processamento no servidor Asterisk.
   - A. Verdadeiro
   - B. Falso
8. Para capturar uma chamada de um grupo de chamada específico, você deve estar no grupo de ___ correspondente.
9. Você pode gravar uma chamada com o aplicativo MixMonitor() ou o recurso de gravação com um toque (`automixmon`). Por padrão, o `automixmon` usa a sequência DTMF ___.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. No ConfBridge, qual opção de perfil de usuário `confbridge.conf` faz com que um participante entre no mudo (eles podem ouvir a conferência, mas não podem ser ouvidos até que o mudo seja desativado)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Respostas:** 1 — B, C · 2 — grupo de captura; `chan_dahdi.conf` · 3 — cega; assistida · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — captura · 9 — C · 10 — A
