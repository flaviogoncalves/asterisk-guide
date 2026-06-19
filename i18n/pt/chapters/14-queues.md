# Call Queues

Call queues, também conhecidas como ACD (Automatic Call Distribution), estão se tornando cada vez mais importantes para atender chamadas de clientes de forma eficiente. Um distribuidor automático de chamadas pode ajudar a reduzir custos, aumentar o nível de serviço e melhorar as vendas, já que os distribuidores de chamadas afetam a forma como sua empresa funciona — não por alguns dias, mas por muitos anos. Em um ambiente de call center, o fator número um são as pessoas; elas são o recurso mais caro. Leva tempo, dinheiro e paciência para contratar, treinar e motivar agentes. Com um ACD, você pode maximizar a produtividade dos agentes dimensionando precisamente o número de agentes necessários, controlando atendentes bons e ruins e analisando o fluxo de chamadas.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Entender por que e como usar call queues
- Entender a teoria básica das call queues
- Instalar e configurar o sistema de filas

## Como as filas funcionam?

Call queues não são exatamente uma novidade. Quando você tem um alto fluxo de chamadas recebidas, é difícil distribuir as chamadas adequadamente. Usar uma estratégia de grupo onde o telefone toca simultaneamente em todos os agentes não parece funcionar, a menos que você tenha apenas alguns agentes. No entanto, uma call queue entregará chamadas apenas para um único agente disponível de cada vez e colocará o cliente em espera com música quando não houver agentes disponíveis. A fila funciona retendo a chamada enquanto encontra um agente desocupado para atendê-la. Um dos maiores benefícios da fila é evitar a perda de chamadas, ao mesmo tempo que oferece a possibilidade de gerar estatísticas.

![Uma call queue: chamadas recebidas 1-800 entram na fila e uma estratégia ACD (ringall, rrmemory, leastrecent, priority e outras) as distribui para os agentes disponíveis](../images/14-queues-fig01.png)

Geralmente, uma call queue funciona assim:

- Os agentes fazem login na fila.
- As chamadas recebidas são enfileiradas.
- Uma estratégia de enfileiramento para distribuir as chamadas é usada para enviar as chamadas aos agentes.
- Música de espera (MOH) é reproduzida enquanto o chamador aguarda.
- Anúncios podem ser feitos aos chamadores, notificando-os sobre o tempo de espera.
- A chamada é atendida pelo agente e estatísticas são geradas.

A principal aplicação para filas é o atendimento ao cliente. Ao usar filas, você evita perder chamadas quando seus agentes estão ocupados. Você pode adicionar novos agentes à fila se perceber que o número de chamadores na fila está crescendo. Outra vantagem das filas é que agora você pode ter estatísticas como taxa de abandono de chamadas, duração média da chamada e meta de atendimento de chamadas. Essas estatísticas ajudarão você a determinar quantos agentes usar para fornecer um melhor serviço ao seu cliente.

### Arquitetura ACD

A arquitetura ACD é formada por filas e agentes. Um agente pode estar em duas filas ao mesmo tempo. Uma fila pode ter agentes, canais e grupos de agentes.

![Arquitetura ACD: cada fila (Atendimento ao Cliente, Vendas Internas) é alimentada por um número de telefone e entrega chamadas aos agentes, que por sua vez estão vinculados a canais físicos](../images/14-queues-fig02.png)

## Filas

As filas são definidas no arquivo de configuração queues.conf. Agentes são atendentes que fazem login e são membros das filas. Agentes são definidos no arquivo agents.conf. O sistema de filas cresceu significativamente ao longo de muitas versões, tornando o arquivo de configuração extenso. Explicaremos alguns dos principais parâmetros. Parâmetros gerais

```
autofill=yes
```

O comportamento antigo da fila era do tipo serial. A fila esperava que uma chamada fosse despachada antes de enviar a chamada seguinte para o próximo agente. Se um agente levasse 15 segundos para atender uma chamada, as outras chamadas na fila tinham que esperar até que aquela chamada fosse atendida. Para filas de alto volume, esse comportamento era ineficiente. O novo comportamento autofill=yes não espera até que uma chamada seja atendida, mas trabalha em paralelo. Você pode gravar as chamadas na fila usando a opção mixmonitor. Nesse modo, as chamadas são gravadas e mixadas ao mesmo tempo.

### Arquivo de configuração de filas

As filas são configuradas no arquivo queues.conf. Na figura, você encontrará um exemplo funcional de uma fila.

![Um exemplo funcional do arquivo queues.conf, mostrando a seção geral e uma fila customerservice com estratégia, nível de serviço, anúncios, gravação e membros](../images/14-queues-fig03.png)

### Agentes

Você pode configurar seus agentes no arquivo agents.conf. Os agentes podem fazer login a partir de qualquer extension para receber chamadas. Você pode discar para um agente usando:

```
Dial(agent/<name>)
```

#### Agentes

Agente 300

- Você pode verificar o status dos agentes usando o comando `agent show all`
- o comando agentlogin é executado e o agente é associado ao canal atual.
- O usuário disca uma extension com a aplicação agentlogin.

![Agentes: um usuário faz login discando uma extension que executa a aplicação agentlogin, que vincula o Agente 300 ao canal atual; você pode verificar o status do agente com `agent show all`](../images/14-queues-fig04.png)

Você pode definir os agentes no arquivo agents.conf

```
; Agent configuration
[general]
persistentagents=yes
[agents]
autologoff=15
autologoffunavail=yes
ackcall=no
endcall=yes
wrapuptime=5000
musiconhold => default
;
;This section contains the agent definitions, in the form:
;
; agent => agentid,agentpassword,name
;
agent => 300,300
agent => 301,301
```

### Membros

Membros são canais ativos respondendo à fila. Membros podem ser canais diretos (PJSIP, DAHDI) ou agentes que fazem login antes de receber chamadas.


### Estratégias

As chamadas são distribuídas entre os membros de acordo com uma destas estratégias:

- ringall: Toca todos os canais disponíveis até que alguém atenda.
- leastrecent: Distribui para o membro menos recente.
- fewestcalls: Distribui para o membro com menos chamadas.
- random: Toca uma interface aleatória.
- wrandom: Toca uma interface aleatória, mas usa a penalidade do membro como um peso ao calcular sua métrica.
- rrmemory: Usa round robin com memória; ele lembra onde parou com a chamada na última passagem.
- rrordered: Igual ao rrmemory, exceto que a ordem dos membros da fila do arquivo de configuração é preservada.
- linear: Toca os membros na ordem em que estão listados no queues.conf; para membros dinâmicos, na ordem em que foram adicionados.

> **[Nota da 2ª ed.]** A estratégia `roundrobin` foi substituída por `rrmemory` nas primeiras versões do Asterisk e não está mais disponível. Remova-a da lista de estratégias se ela apareceu no texto da edição anterior. Todas as estratégias listadas acima estão confirmadas como presentes no Asterisk 22.

## Agentes

Agentes são implementados como canais proxy. Eles podem ser usados dentro das filas. Outro uso para os canais de agente é a mobilidade de extension. O usuário pode fazer login usando qualquer telefone e receber suas chamadas. Isso permite que um usuário vá para qualquer sala para torná-la um escritório. Você pode discar para um agente no dialplan usando dial(agent/<name>). Você define os agentes no arquivo agents.conf.

![Mobilidade de agente: o usuário atende qualquer telefone, disca uma extension de login e informa o número do agente e a senha; após o sucesso de agentlogin(), o agente (Agente 300) está pronto para receber chamadas, e você pode verificar o status com o comando CLI `agent show all`](../images/14-queues-fig05.png)

### Grupos de Agentes

Você pode optar por usar grupos de agentes. Esta função não leva em consideração as estratégias ACD. Você provavelmente preferirá listar todos os agentes individualmente. Se você quiser transferir para um grupo de agentes, você

```
can use queues.conf:
member=>agent/@1 ;any agent in group 1
member=>agent/:1,1 ;any agent in group 1, wait for first available, ;do not
use agent groups.
```

### O arquivo de configuração para agentes

Os agentes são definidos no arquivo agents.conf. Abaixo está um exemplo funcional do arquivo.

![Um exemplo funcional do arquivo agents.conf: uma seção geral com persistentagents, uma seção de agentes com os parâmetros padrão (autologoff, ackcall, endcall, wrapuptime, musiconhold) e duas definições de agente (300 e 301)](../images/14-queues-fig06.png)

## Aplicações relacionadas ao ACD

O sistema de filas do Asterisk disponibiliza várias aplicações para implementar as filas no dialplan. Abaixo, mostramos algumas delas.

### A aplicação queue()

Esta aplicação enfileira chamadas recebidas em uma call queue específica conforme definido no queues.conf. A string de opção pode conter zero ou mais dos seguintes caracteres: Além de transferir a chamada, uma chamada pode ser estacionada e depois atendida por outro usuário. A URL opcional será enviada à parte chamada se o canal a suportar. O parâmetro AGI opcional configurará um script AGI para ser executado no canal da parte chamadora assim que ela for conectada a um membro da fila. O timeout fará com que a fila falhe após um número especificado de segundos, verificado entre cada ciclo de timeout e nova tentativa. Esta aplicação define a variável de status QUEUE após a conclusão:

![A aplicação queue(): sua sintaxe `Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])` e as opções de letra única disponíveis (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### A aplicação agentlogin()

Esta aplicação solicita que o agente faça login no sistema. Ela sempre retorna -1. Enquanto estiver logado, o agente que recebe chamadas ouvirá um bipe quando uma nova chamada chegar. O agente pode derrubar a chamada pressionando a tecla *.

![A aplicação agentlogin(): sua sintaxe `AgentLogin([AgentNo][|options])` e a opção `s` para um login silencioso que não anuncia a confirmação de login](../images/14-queues-fig08.png)

### A aplicação addQueueMember()

Esta aplicação adiciona dinamicamente um dispositivo (por exemplo, PJSIP/3000) a uma fila. Se o dispositivo já existir, ela retornará um erro.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### A aplicação removeQueueMember()

Esta aplicação remove dinamicamente um dispositivo da fila. Se o dispositivo não pertencer à fila, ela retornará um erro.

```
RemoveQueueMember(queuename[|interface])
```

### Aplicações de suporte e comandos CLI

Algumas aplicações e comandos de console são capazes de ajudar no trabalho com filas. O seguinte descreve o que cada aplicação faz:

![Aplicações de suporte (AddQueueMember, RemoveQueueMember) e comandos CLI (agent show all, queue show, queue show <name>) usados para gerenciar filas em tempo de execução](../images/14-queues-fig09.png)

## Tarefas de configuração

A figura abaixo resume as principais tarefas para criar um sistema de filas funcional.

![As tarefas de configuração do ACD: (1) criar a call queue (obrigatório), (2) definir parâmetros de agente (opcional), (3) criar agentes (opcional), (4) colocar a fila no dialplan (obrigatório), (5) configurar gravação de agente (opcional) e (6) verificar com agent show all e queue show (opcional)](../images/14-queues-fig10.png)

Passo 1: Criar a call queue No arquivo queues.conf:

```
[telemarketing]
music = default
;announce = queue-telemarketing
;context = qoutcon
timeout = 2
retry = 2
maxlen = 0
member => Agent/300
member => Agent/301
[auditing]
music = default
;announce = queue-auditing
;context = qoutcon
timeout = 15
retry = 5
maxlen = 0
member => Agent/600
member => Agent/601
```

Passo 2: Definir parâmetros de agente No arquivo agents.conf:

```
debian:/etc/asterisk# cat agents.conf
;
; Agent configuration
;
[agents]
; Define maxlogintries to allow agent to try max logins before
; failed.
; default to 3
maxlogintries=5
; Define autologoff times if appropriate.  This is how long
; the phone has to ring with no answer before the agent is
; automatically logged off (in seconds)
autologoff=15
; Define autologoffunavail to have agents automatically logged
; out when the extension that they are at returns a CHANUNAVAIL
; status when a call is attempted to be sent there.
; Default is "no".
;autologoffunavail=yes
; Define ackcall to require an acknowledgement by '#' when
; an agent logs in using agentcallbacklogin.  Default is "no".
;ackcall=no
; Define endcall to allow an agent to hangup a call by '*'.
; Default is "yes". Set this to "no" to ignore '*'.
;endcall=yes
; Define wrapuptime.  This is the minimum amount of time when
; after disconnecting before the caller can receive a new call
; note this is in milliseconds.
;wrapuptime=5000
; Define the default musiconhold for agents
; musiconhold => music_class
;musiconhold => default
;
; Define the default good bye sound file for agents
; default to vm-goodbye
;agentgoodbye => goodbye_file
; Define updatecdr. This is whether or not to change the source
; channel in the CDR record for this call to agent/agent_id so
; that we know which agent generates the call
;updatecdr=no
;
; Group memberships for agents (may change in mid-file)
;
;group=3
;group=1,2
;group=
```

Passo 3: Criar os agentes No arquivo agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Passo 4: Inserir a fila no dialplan

```
In the file extensions.conf:
; Telemarketing queue.
exten=>_0800XXXXXXX,1,Answer
exten=>_0800XXXXXXX,2,Set(CHANNEL(musicclass)=default)
exten=>_0800XXXXXXX,3,Set(TIMEOUT(digit)=5)
exten=>_0800XXXXXXX,4,Set(TIMEOUT(response)=10)
exten=>_0800XXXXXXX,5,Background(welcome)
exten=>_0800XXXXXXX,6,Queue(telemarketing)
; Transfer to the queue auditing
exten => 8000,1,Queue,(auditing)
exten => 8000,2,Playback(demo-echotest); No auditor available
exten => 8000,3,Goto(8000,1) ; Verify auditor again
; Agent login for the telemarketing and auditing queues
exten => 9000,1,Wait(1)
exten => 9000,2,AgentLogin()
```

### Configurar gravação de fila

As chamadas podem ser gravadas usando a aplicação MixMonitor do Asterisk. (A aplicação independente Monitor foi removida no Asterisk 22, e a opção `monitor-type` do queues.conf agora aceita apenas MixMonitor.) A gravação pode ser ativada dentro da aplicação de fila, começando quando a chamada é efetivamente atendida. Apenas chamadas bem-sucedidas são gravadas, e nenhuma gravação é realizada enquanto as pessoas estão ouvindo a MOH. Para ativar o monitoramento, basta especificar monitor-format. Este recurso é desativado por padrão. Você pode definir o nome do arquivo para a gravação usando Set (MONITOR_FILENAME=<filename>); caso contrário

```
it will use MONITOR_FILENAME=${UNIQUEID}.
```

No arquivo queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Operação da fila

Os exemplos a seguir explicam como usar a fila. Passo 1: Login do agente Exemplo: Um agente na fila de telemarketing atende o telefone e disca #9000. O agente ouve uma mensagem de login inválido e é solicitado seu nome e senha. A fila de auditoria segue o mesmo procedimento. Passo 2: Fila Uma vez na fila, o agente ouvirá a MOH, se definida. Quando uma chamada chegar à fila de telemarketing, o agente ouvirá um bipe e será conectado a essa chamada. Passo 3: Finalização da chamada Quando o agente termina a chamada, ele/ela pode:

- Pressionar ‘*’ para desconectar e permanecer na fila.
- Desconectar o telefone, desconectando-se assim da fila.
- Pressionar #8000 para transferir a chamada para auditoria.

## Recursos avançados

O sistema de filas do Asterisk possui alguns recursos avançados para priorizar certos clientes e agentes, bem como habilitar um menu de usuário.

### Menu de usuário

Você pode definir um menu para um usuário enquanto ele aguarda na fila usando extensões de um dígito. Para ativar esta opção, defina um context na configuração da fila queues.conf.

### Penalidade

Os agentes podem ser configurados com uma penalidade. Uma fila enviará as chamadas primeiro para usuários com valores de penalidade mais baixos. Por exemplo, como sabemos que nossos clientes adoram a Susan e sua voz suave, podemos optar por atribuir prioridade 0 a ela. Alternativamente, o agente chamado Uber, que tem menos experiência, é menos preferido para atendimento ao cliente; portanto, atribuímos uma prioridade 10 a este agente. No arquivo queues.conf:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Prioridade

As filas operam no modo FIFO (primeiro a entrar, primeiro a sair). Se você quiser dar prioridade a clientes especiais (platina, ouro), você pode configurar prioridades diferenciadas. Para clientes platina ou ouro:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Clientes azuis:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## A aplicação agentcallbacklogin() foi removida

A aplicação `agentcallbacklogin()` foi descontinuada pela Digium no Asterisk 1.4 (julho de 2006) e não está mais disponível no Asterisk 22. A abordagem recomendada é usar `AddQueueMember()` com uma interface PJSIP para adicionar dinamicamente membros do tipo callback a uma fila. O documento `queues-with-callback-members.txt` foi incluído em diretórios mais antigos do Asterisk `/doc` para orientação de migração.

> **[Nota da 2ª ed.]** Verifique se o driver de canal `chan_agent` (app_agent_pool) ainda é o mecanismo preferido para o comportamento de callback de agente no Asterisk 22, ou se membros PJSIP diretos com `AddQueueMember()`/`RemoveQueueMember()` é agora o padrão.

## Estatísticas de fila

Todos os eventos das filas são registrados em /var/log/asterisk/queue_log. O formato do log da fila é publicado no documento queuelog.txt no diretório /doc da documentação do Asterisk. Abaixo estão alguns dos eventos mais importantes registrados.

- ABANDON(position|origposition|waittime)
- AGENTDUMP
- AGENTLOGIN(channel)
- AGENTLOGOFF(channel|logintime)
- ATTENDEDTRANSFER(destexten|destcontext|holdtime|calltime|origposition)
- BLINDTRANSFER(extension|context|holdtime|calltime|origposition)
- COMPLETEAGENT(holdtime|calltime|origposition)
- COMPLETECALLER(holdtime|calltime|origposition)
- CONFIGRELOAD
- CONNECT(holdtime|bridgedchanneluniqueid)
- ENTERQUEUE(url|callerid)
- EXITEMPTY(position|origposition|waittime)
- EXITWITHKEY(key|position)
- EXITWITHTIMEOUT(position|origposition|waittime)
- QUEUESTART
- RINGNOANSWER(ringtime)
- SYSCOMPAT

Você pode criar seu próprio utilitário para processar esses eventos ou usar um pacote de estatísticas pronto para uso. Testamos dois utilitários na voip.school:

- Qlog analyzer (http://www.micpc.com/qloganalyzer/) – Excelente pacote open source
- Queue metrics (http://queuemetrics.com/) – Um dos pacotes mais completos para estatísticas de fila

> **[Nota da 2ª ed.]** Verifique se ambas as ferramentas de estatísticas de terceiros acima ainda são mantidas e compatíveis com o formato queue_log do Asterisk 22. Considere adicionar uma referência à Asterisk REST Interface (ARI) como uma alternativa moderna para construir integrações personalizadas de relatórios de fila.

## Resumo

Neste capítulo, você aprendeu como usar um ACD, sua arquitetura e como configurá-lo. Alguns recursos avançados, como prioridades e penalidades, também foram apresentados.

## Quiz

1. Quais das seguintes são estratégias de distribuição de fila válidas no `queues.conf` (escolha todas as que se aplicam)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. Você pode gravar uma conversa entre um agente e um cliente a partir da fila definindo a opção ___ no arquivo `queues.conf`.
3. Qual `strategy` toca os membros na ordem exata em que estão listados no `queues.conf`?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. Quando o agente termina uma chamada no exemplo de telemarketing, quais ações ele pode tomar (escolha todas as que se aplicam)?
   - A. Pressionar `*` para desconectar e permanecer na fila
   - B. Desligar o telefone e desconectar da fila
   - C. Pressionar `#8000` para transferir a chamada para auditoria
   - D. Pressionar `#` para sair de todas as filas imediatamente
5. Quais duas tarefas são *obrigatórias* para obter uma fila funcional (escolha todas as que se aplicam)?
   - A. Criar a fila
   - B. Criar os agentes
   - C. Configurar parâmetros de agente
   - D. Configurar gravação
   - E. Colocar a fila no dialplan
6. Em uma call queue, você pode oferecer um menu de um dígito que o chamador pode discar enquanto aguarda. Isso é ativado definindo um(a) ___ na seção ___ da fila:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. As aplicações de suporte `AddQueueMember()` e `RemoveQueueMember()` são usadas no ___ para adicionar ou remover membros em tempo de execução:
   - A. dialplan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. Como o chan_sip foi removido no Asterisk 21, um membro de fila estático deve referenciar um canal como ___ em vez de `SIP/1001`.
9. O parâmetro `wrapuptime` é o tempo mínimo após um agente desconectar uma chamada antes que a fila envie uma nova chamada para esse agente.
   - A. True
   - B. False
10. Um chamador pode receber uma posição mais alta na mesma fila definindo a variável de canal `QUEUE_PRIO` antes de chamar `Queue()`.
    - A. True
    - B. False

**Respostas:** 1 — A, C, D, E, F (roundrobin foi substituído por rrmemory e não existe mais) · 2 — `monitor-format` (a gravação a partir da fila é ativada especificando `monitor-format`; `monitor-type` seleciona MixMonitor vs Monitor) · 3 — C (linear) · 4 — A, B, C (`*` desconecta e permanece; `#` não é uma tecla de sair de tudo) · 5 — A, E · 6 — C (a opção `context`) · 7 — A (o dialplan) · 8 — `PJSIP/1001` (qualquer interface `PJSIP/`) · 9 — True · 10 — True
