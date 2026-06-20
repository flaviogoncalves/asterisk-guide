# Using PBX features

Em sistemas SIP, a maioria dos recursos de telefone é implementada no endpoint. Existe uma variedade de telefones SIP e fabricantes, e a interoperabilidade não é garantida. A equipe de desenvolvimento do Asterisk fez um trabalho incrível ao implementar a maioria dos recursos no próprio PBX, tornando o Asterisk quase independente do endpoint. No entanto, às vezes você encontrará a mesma função sendo realizada tanto pelo telefone quanto pelo Asterisk. A integração do telefone com o PBX é a próxima fronteira em usabilidade e onde os sistemas proprietários estão focando atualmente. Neste capítulo, você aprenderá a usar a maioria desses recursos.

## Objetivos

By the end of this chapter, you will be able to understand and use:

- Estacionamento de Chamadas
- Atendimento de Chamadas
- Transferência de Chamadas
- Conferência de Chamadas (ConfBridge)
- Gravação de Chamadas
- Música em Espera

## Onde os recursos são implementados

Primeiro e antes de tudo, é importante entender quando os recursos do PBX são executados versus quando o telefone está realizando todo o trabalho. Por exemplo, você pode transferir uma chamada usando o botão TRANSFER no telefone ou discando # (transferência incondicional executada pelo próprio PBX).

## Recursos implementados pelo Asterisk

- Música em espera
- Estacionamento de chamadas
- Captação de chamada
- Gravação de chamada
- Sala de conferência ConfBridge
- Transferência de chamada (cega e consultiva)

## Recursos geralmente implementados pelo plano de discagem

- Encaminhamento de chamada quando ocupado
- Encaminhamento de chamada imediato
- Encaminhamento de chamada não atendida
- Filtragem de chamadas (lista negra)
- Não perturbe
- Rediscagem

## Recursos geralmente implementados pelo telefone

Esses recursos são implementados pelo firmware do telefone:

![Onde os recursos do PBX geralmente são implementados: no próprio Asterisk, no dialplan ou no telefone](../images/13-pbx-features-fig01.png)

- Chamada em espera
- Transferência cega
- Transferência consultiva
- Conferência de três vias
- Indicador de mensagem aguardando

## O arquivo de configuração de recursos

Alguns dos recursos apresentados neste capítulo são configurados no arquivo de configuração features.conf. É possível alterar o comportamento de alguns recursos modificando este arquivo. Incluímos o trecho relevante abaixo. Nas próximas seções deste capítulo, descreveremos cada recurso. Trecho do arquivo de exemplo (Asterisk 22)

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

Desde o Asterisk 12, o estacionamento de chamadas foi movido de `features.conf` para seu próprio módulo, `res_parking`, com configuração em `res_parking.conf`. O bloco parking-lot abaixo (`parkext`, `parkpos`, `context`, `parkingtime`, e assim por diante) está em `res_parking.conf`. A seção `[featuremap]` (os códigos de recurso DTMF, incluindo `parkcall`) permanece em `features.conf`.

As opções do parking-lot ficam em `res_parking.conf`. Um estacionamento chamado `default` sempre existe, mesmo que não esteja presente no arquivo de configuração. O trecho abaixo foi retirado do Asterisk 22 `res_parking.conf.sample`:

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

Os códigos de recurso DTMF (incluindo o `parkcall` de um passo) permanecem na seção `[featuremap]` de `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the Dial() or Queue()  app call!
;parkcall => #72                ; Park call (one step parking)  -- Make sure to set the K and/or k option in the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X and/or x option in the Dial() or Queue() app call!
```

## Transferência de Chamadas

A transferência de chamadas pode ser implementada pelo telefone, por ATA ou pelo próprio Asterisk. Consulte o manual do seu telefone para entender como as chamadas são transferidas. Se o seu telefone não suportar transferência de chamadas, você pode usar o Asterisk para realizar essa tarefa. A transferência de chamadas é implementada de duas maneiras diferentes.

A primeira forma é usar o recurso de transferência cega: disque # seguido do número a ser transferido. Às vezes você usará o recurso de transferência do seu telefone IP ou softphone IP. Você pode alterar o caractere de transferência editando o parâmetro blindxfer no arquivo features.conf.

Você pode habilitar a transferência assistida no Asterisk removendo o ; antes do parâmetro atxfer no arquivo features.conf. Durante uma conversa, você pressionaria *2. O Asterisk dirá "transfer" e lhe dará um tom de discagem. O chamador é enviado para música em espera. Depois de falar com a pessoa de destino e desligar o telefone, o sistema conecta o chamador ao destino.

![Transferência de chamadas: os passos para uma transferência cega (pressione # durante a chamada) e uma transferência assistida (pressione *2)](../images/13-pbx-features-fig03.png)

### Lista de tarefas de configuração

1. Para um endpoint PJSIP, certifique‑se de que a opção `direct_media` esteja definida como `no` (para que a mídia flua através do Asterisk e os códigos de recurso sejam detectados), ou use uma opção `t`/`T` no aplicativo `Dial()`

## Call parking

Este recurso é usado para estacionar uma chamada. Isso ajuda, por exemplo, quando você atende uma chamada telefônica fora da sua sala e quer transferir a chamada de volta para a sua mesa. Você pode fazer isso estacionando a chamada em uma extensão. Quando chegar à sua mesa, basta discar o número da extensão de estacionamento para recuperar a chamada.

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

Por padrão, a extensão 700 é usada para estacionar uma chamada. No meio de uma conversa, pressione # para transferir a chamada para a extensão 700. Agora o Asterisk anunciará sua extensão de estacionamento, como 701 ou 702. Encerre a chamada, e o chamador ficará em espera. Vá até o telefone da sua mesa e disque a extensão de estacionamento anunciada para recuperar a chamada. Se o chamador permanecer estacionado por muito tempo, o recurso de timeout será acionado e a extensão originalmente discada tocará novamente.

### Configuration task list

Siga os passos abaixo para habilitar o estacionamento de chamadas. Passo 1: Torne o estacionamento acessível a partir do seu dialplan (obrigatório). O `context` padrão do estacionamento é `parkedcalls` (definido em `res_parking.conf`). Inclua esse contexto no contexto a partir do qual seus telefones discam, em `extensions.conf`:

```
include => parkedcalls
```

Passo 2: Teste o recurso de estacionamento de chamadas discando #700. Observações:

- A extensão de estacionamento não será exibida no comando CLI `dialplan show`.
- É necessário recarregar o módulo de estacionamento após alterar o arquivo de configuração de estacionamento: `module reload res_parking.so`. Para alterações em `features.conf`, `module reload features.so`.
- Para estacionar uma chamada, você precisa transferir para #700. Verifique as opções `t` e `T` no aplicativo `Dial()`.

## Call pickup

Call pickup allows you to capture a call from a colleague in the same call group. This would help avoid, for example, having to wake up to take a call that is ringing to another person in your room, but who is not present. By dialing *8, you can capture a call within your call group. This number can be modified in the `features.conf` file.

![Call pickup: members can only capture calls within their own group; the operator (pickupgroup=1,2,3) can pick up calls from every group](../images/13-pbx-features-fig05.png)

### Configuration task list

Follow the steps below to configure the call pickup feature. Step 1: Configure a call group for your extensions. This is done in the channel configuration file (pjsip.conf, iax.conf, chan_dahdi.conf). For PJSIP endpoints, set `call_group` and `pickup_group` in the endpoint section of `pjsip.conf` (pjsip.conf uses snake_case option names). This task is required.

For PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Step 2: Change the call-pickup feature number (optional). This is set in the `[general]` section of `features.conf`, not in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conferência (call conference)

Existem diferentes maneiras de implementar uma conferência no Asterisk. A primeira opção é simplesmente usar a capacidade de conferência de três vias do telefone. Ao usar esse recurso no telefone, você não precisa de nenhum suporte no próprio servidor. No entanto, quando quiser uma conferência com mais de 3 pessoas, deve executar uma sala de conferência. O aplicativo de conferência moderno do Asterisk é o ConfBridge (`app_confbridge`).

O ConfBridge suporta conferências de voz em HD e videoconferências. Existem algumas limitações para videoconferência, como a ausência de transcodificação — todos os participantes precisam usar o mesmo codec e perfil. A videoconferência usa um modo follow-the-talker, exibindo a imagem da última pessoa que falou. Você pode configurar facilmente novos menus DTMF no ConfBridge.

O ConfBridge substitui o antigo aplicativo MeetMe, que foi descontinuado no Asterisk 19. O MeetMe ainda está presente na árvore de código-fonte do Asterisk 22, mas depende do DAHDI e não é compilado por padrão, portanto, em uma instalação típica de PJSIP ele simplesmente não está disponível — o ConfBridge é o aplicativo de conferência suportado. Ao contrário do MeetMe, o ConfBridge **não** requer DAHDI ou uma fonte de temporização de hardware: ele depende da interface de temporização interna do Asterisk (`res_timing_timerfd` no Linux, ou `res_timing_pthread`), portanto nenhum módulo `dahdi_dummy` é necessário. Se você estiver migrando de um sistema mais antigo que usava `MeetMe()` e `meetme.conf`, substitua-os por `ConfBridge()` e `confbridge.conf` conforme descrito abaixo.

### ConfBridge

Para iniciar uma sala de conferência, a sintaxe está listada abaixo.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Para obter uma descrição completa do comando, você pode usar `core show application confbridge`.

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

Como pode ser visto acima, há três argumentos importantes, cada um mapeando para um tipo de seção em `confbridge.conf`. **bridge_profile** (uma seção `type=bridge`): aqui você seleciona o número máximo de participantes (`max_members`), gravação (`record_conference`), `video_mode` e muitos outros parâmetros globais da ponte.

Não faz sentido reproduzir todo o arquivo de exemplo aqui, então deixarei um exemplo simples de como configurar um `bridge_profile` no arquivo `confbridge.conf`.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (uma seção `type=user`): aqui você define opções que são específicas por usuário, como se o usuário é um administrador (`admin=yes`), se ele inicia silenciado (`startmuted=yes`), music on hold, e muitas outras opções por usuário. Exemplo:

```
[admin_user]
type=user
admin=yes
```

**menu** (uma seção `type=menu`): aqui você define o mapeamento do teclado (DTMF) para a conferência — por exemplo, qual tecla alterna o mute, ajusta o volume ou sai da conferência. Verifique o arquivo `confbridge.conf.sample` para ver todas as ações disponíveis. Exemplo:

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

#### Funções Confbridge

As opções da ponte de conferência podem ser passadas dinamicamente no dialplan usando a função CONFBRIDGE(). Veja os exemplos abaixo:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Comandos de administração do ConfBridge e migração do MeetMe

Se você vem do MeetMe, as funções de administração que você usava através do `MeetMeAdmin()` e da opção `a` (admin) agora são expressas através do **perfil de usuário admin** (`admin=yes`) mais as ações do **menu**. Um administrador que entra com um perfil admin e um menu contendo ações de administração pode bloquear a sala, expulsar usuários e silenciar participantes ao vivo a partir do teclado. As ações de menu relevantes em `confbridge.conf` são:

- `admin_kick_last` -- expulsar o último usuário que entrou
- `admin_toggle_mute_participants` -- silenciar/ativar áudio de todos os participantes não‑admin
- `toggle_mute` -- silenciar/ativar áudio de si mesmo
- `participant_count` -- anunciar o número de participantes
- `leave_conference` -- sair da ponte e continuar no dialplan

Essas substituem as flags de opção do MeetMe `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x`, …) e os comandos `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N`, …). Em uma instalação moderna do PJSIP você não carregará `app_meetme` de forma alguma; toda a configuração de conferência vive em `confbridge.conf`, e as alterações são aplicadas com `module reload app_confbridge.so` (a lógica do ConfBridge vive em `app_confbridge`; não há módulo `res_confbridge`).

### Exemplo de ConfBridge

Para criar uma sala de conferência acessível na extensão 500, em `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

O primeiro chamador que disca 500 cria a conferência `101`; os chamadores subsequentes entram nela. Perfis e menus referenciados aqui (`default_bridge`, `default_user`, `sample_user_menu`) são definidos em `confbridge.conf`. Para exigir um PIN, defina `pin=` no perfil do usuário; para tornar um participante um administrador da conferência, atribua a ele um perfil de usuário com `admin=yes`.

## Gravação de Chamadas

Existem várias maneiras de gravar uma chamada no Asterisk. Você pode usar a aplicação `MixMonitor()` para gravar chamadas facilmente. (A aplicação mais antiga `Monitor`, que gravava dois arquivos separados, foi removida; use `MixMonitor` em seu lugar.)

### Usando a aplicação MixMonitor

A aplicação `MixMonitor` grava o áudio no canal atual no arquivo especificado. Se o nome do arquivo for um caminho absoluto, ele usa esse caminho. Caso contrário, cria o arquivo no diretório de monitoramento configurado em asterisk.conf.

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

Grava uma chamada e mistura o áudio durante a gravação. Sintaxe: `MixMonitor(filename.extension[,options[,command]])`. Grava o áudio no canal atual no arquivo especificado. Opções válidas:

- a - Anexa ao arquivo em vez de sobrescrevê‑lo.
- b - Salva o áudio no arquivo somente enquanto o canal estiver em ponte.
- Note: does not include conferences.
- v(<x>) - Ajusta o volume audível por um fator de <x> (variando de -4 a 4)
- V(<x>) - Ajusta o volume falado por um fator de <x> (variando de -4 a 4)
- W(<x>) - Ajusta ambos os volumes audível e falado por um fator de <x> (variando de -4 a 4)
- <command> will be executed when the recording is over. Any strings matching ^{X} will be unescaped to ${X} and all variables will be evaluated at that time. The variable MIXMONITOR_FILENAME will contain the filename used to record.

Um recurso interessante é a funcionalidade de gravação com um toque `automixmon`, que permite que uma parte disque um código DTMF (o exemplo `features.conf` sugere `*3`; não há padrão incorporado, portanto você deve configurá‑lo) durante a chamada para iniciar imediatamente (e desativar) a gravação. Ela é baseada no MixMonitor, portanto grava um único arquivo misturado. Exemplo:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

The `X` and `x` options enable the one-touch MixMonitor feature for the caller and callee respectively. Because MixMonitor records a single mixed file, there is no need to combine separate IN/OUT files afterward (the old `automon`/`Monitor` approach, which produced two files for `soxmix`, was removed along with the `Monitor` application).

If you don’t want to use Set() before the Dial() application, you can set this in the globals section:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Música em espera

Música em espera (MOH) mudou várias vezes entre as versões 1.0, 1.2 e 1.4. Na versão mais recente, o MOH padrão é “FILE-BASED”. Em outras palavras, o Asterisk fornecerá os arquivos de MOH em formatos como g729, alaw, ulaw e gsm. Assim, não é necessário transcodificar a música antes de enviá‑la ao canal. Isso economiza tempo de processamento, o que é uma modificação bem‑vinda para quem trabalha com sistemas de produção.

Em versões mais antigas, o MOH geralmente era fornecido em MP3 (ainda pode ser configurado dessa forma). Fornecer MOH usando MP3 obriga o Asterisk a transcodificar, consumindo poder de CPU valioso no processo.

O novo arquivo de configuração é mostrado abaixo. Observe que a classe padrão agora usa o modo de formato de arquivo nativo = files. Todos os outros modos estão comentados. Cada seção é uma classe. A única classe não comentada neste ponto é default. Se você quiser ter classes diferentes para arquivos diferentes, precisará criar novas seções (classes).

![Exemplo de configuração do musiconhold.conf, listando os modos válidos de MOH (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

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

### Tarefas de configuração do MOH

Agora, para usar música em espera, defina a classe MOH nos arquivos de configuração de canal (chan_dahdi.conf, pjsip.conf, iax.conf, etc.). Para endpoints PJSIP, defina `moh_suggest` na seção endpoint de `pjsip.conf` (o nome da opção legada `musicclass` se aplica ao chan_dahdi e outros drivers de canal, não ao PJSIP). As músicas freeplay instaladas agora estão no formato wav. No momento da instalação, você pode selecionar (usando make menuselect) os formatos de arquivo MOH disponíveis. Se quiser adicionar novos arquivos MOH, será necessário fornecê‑los nos formatos exigidos. Por exemplo:

Em `/etc/asterisk/chan_dahdi.conf`, adicione a linha `musiconhold`.

```
[channels]
musiconhold=default
```

Em seguida, edite `/etc/asterisk/musiconhold.conf` para definir essa classe:

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

No dialplan, você pode iniciar música em espera em um canal com `StartMusicOnHold` (e pará‑la com `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Para reproduzir música em espera por um tempo fixo como um teste rápido, use o aplicativo `MusicOnHold` com uma duração (em segundos):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Mapas de Aplicação

Mapas de aplicação permitem que você adicione novos recursos usando a seção `[applicationmap]` do arquivo features.conf. Suponha que você precise identificar o tipo de cliente que está atendendo em um call center. Você poderia criar um mapa de aplicação para cada tipo de cliente, que poderia contar o número de clientes atendidos por tipo.

## Summary

In this chapter you learned where Asterisk's PBX features live — some in the core, some in the dial plan, and some on the phone — and how the DTMF feature codes are mapped in the `[featuremap]` section of `features.conf`. You configured **call transfer** (blind and attended) and **call parking** (`res_parking.conf`, with the `k`/`K` Dial options and the `parkedcalls` lot), **call pickup** by group, and **conferencing** with **ConfBridge** (`confbridge.conf` bridge/user/menu profiles), which replaces the old MeetMe. You set up **one-touch recording** with MixMonitor (`automixmon`, the `X`/`x` Dial options, and `DYNAMIC_FEATURES`), configured **music on hold**, and saw how **application maps** let you bind your own dialplan logic to a DTMF sequence. With these building blocks you can deliver the everyday features users expect from a business PBX.

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___. For DAHDI channels this is configured in the ___ file.
3. When transferring a call you can choose between a ___ transfer, where the destination is not consulted first, and an ___ transfer, where you talk to the destination before completing it.
4. To make an attended (consultative) transfer you use the ___ sequence; for a blind transfer you use ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. To host conference calls in Asterisk 22, you use the ___ application.
6. In ConfBridge, a participant is granted administrator privileges (kick, mute others, lock the room) by setting ___ in their user profile (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. The best format for music on hold is MP3, because it uses very little processing power on the Asterisk server.
   - A. True
   - B. False
8. To pick up a call from a specific call group, you must be in the matching ___ group.
9. You can record a call with the MixMonitor() application or the one-touch recording (`automixmon`) feature. In the `features.conf` sample, `automixmon` is mapped to the ___ DTMF sequence.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, which `confbridge.conf` user-profile option makes a participant join muted (they can hear the conference but cannot be heard until unmuted)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
