# Call Queues

Call queues, also known as ACD (Automatic Call Distribution) are becoming increasingly important for answering customer calls efficiently. An automatic call distributor can help reduce costs, increase service, and improve sales as call distributors affect how your business works—not for a few days, but for many years. In a call center environment, the number one factor is people; they are the most expensive resource. It takes time, money, and patience to hire, train, and motivate agents. With an ACD, you can maximize agents’ productivity by precisely dimensioning the number of agents required, controlling good and bad attendants, and analyzing the call flow.

## Objectives

Ao final deste capítulo, você deverá ser capaz de:

- Entender por que e como usar filas de chamadas
- Entender a teoria básica das filas de chamadas
- Instalar e configurar o sistema de filas

## Como as filas funcionam?

Filas de chamadas não são exatamente uma novidade. Quando você tem um alto volume de chamadas inbound, é difícil distribuir as chamadas adequadamente. Usar uma estratégia de grupo onde o telefone toca simultaneamente em todos os agentes não parece funcionar, a menos que você tenha apenas alguns agentes. No entanto, uma fila de chamadas entregará chamadas a um único agente disponível a cada vez e colocará o cliente em espera com música quando não houver agentes disponíveis. A fila funciona retendo a chamada enquanto procura um agente desocupado para atender a chamada. Um dos maiores benefícios da fila é evitar a perda de chamadas enquanto fornece a possibilidade de gerar estatísticas.

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

Normalmente, uma fila de chamadas funciona assim:

- Agentes fazem login na fila.
- Chamadas inbound são enfileiradas.
- Uma estratégia de enfileiramento para distribuir as chamadas é usada para enviá‑las aos agentes.
- Música em espera é reproduzida enquanto o chamador aguarda.
- Anúncios podem ser feitos aos chamadores, notificando‑os do tempo de espera
- A chamada é atendida pelo agente e estatísticas são geradas.

A principal aplicação das filas é o atendimento ao cliente. Ao usar filas, você evita perder chamadas quando seus agentes estão ocupados. Você pode adicionar novos agentes à fila se perceber que o número de chamadores na fila está crescendo. Outra vantagem das filas é que agora você pode ter estatísticas como taxa de abandono de chamadas, duração média das chamadas e meta de atendimento. Essas estatísticas ajudarão a determinar quantos agentes usar para oferecer um serviço melhor ao seu cliente.

### Arquitetura ACD

A arquitetura ACD é formada por filas e agentes. Um agente pode estar em duas filas ao mesmo tempo. Uma fila pode ter agentes, canais e grupos de agentes.

![ACD architecture: each queue (Customer Service, Inside Sales) is fed by a phone number and delivers calls to agents, who are in turn bound to physical channels](../images/14-queues-fig02.png)

## Queues

Queues are defined in the queues.conf configuration file. Agents are attendants who log in and are members of queues. Agents are defined in the agents.conf file. The queue system has grown significantly over many releases, making the configuration file extensive. We will explain some of the major parameters. One general parameter worth highlighting is `autofill`:

```
autofill=yes
```

The old behavior for the queue was serial type. The queue waited for a call to be dispatched before sending the succeeding call to the next agent. If an agent takes 15 seconds to answer a call, the other calls in the queue had to wait until that call was answered. For high-volume queues, this behavior was inefficient. The new behavior autofill=yes does not wait until a call is answered, but rather works in parallel. You can record the calls in the queue using the option mixmonitor. In this mode, calls are recorded and mixed at the same time.

### Queue configuration file

Queues are configured in the queues.conf file. In the figure, you will find a working example of a queue.

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### Agents

You can configure your agents in the file agents.conf. Agents can log in from any extension to receive calls. You can dial an agent using:

```
Dial(agent/<name>)
```

#### Agent login

The login flow for Agent 300 works like this:

- The user dials an extension that runs the `AgentLogin()` application.
- `AgentLogin()` is executed and the agent is associated with the current channel.
- You can check the status of the agents using the command `agent show all`.

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

You can define the agents in the file agents.conf

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

### Members

Members are active channels responding to the queue. Members can be direct channels (PJSIP, DAHDI) or agents who log in before receiving calls.

### Strategies

Calls are distributed among members according to one of these strategies:

- ringall: Plays all channels available until someone answers.
- leastrecent: Distributes to the least recent member.
- fewestcalls: Distributes to the member with fewest calls.
- random: Ring random interface.
- wrandom: Ring random interface, but use the member’s penalty as a weight when calculating their metric.
- rrmemory: Uses round robin with memory; it remembers where it left off with the call in the last pass.
- rrordered: Same as rrmemory, except the queue member order from the config file is preserved.
- linear: Rings members in the order they are listed in queues.conf; for dynamic members, in the order they were added.

The older `roundrobin` strategy was deprecated back in Asterisk 1.4. It is no longer a documented strategy and should not be used: in Asterisk 22 the parser still accepts the word `roundrobin`, but only as a backward-compatibility alias that maps to `rrmemory`. Use `rrmemory` (or `rrordered`) explicitly instead. The list above is the set of documented strategies for the `strategy` option in the Asterisk 22 `queues.conf`.

## Agents

Agents are implemented as proxy channels. They can be used inside the queues. Another use for the agent channels is extension mobility. The user can log in using any phone and receive its calls. This allows a user to go to any room to make it an office. You can dial an agent in the dial plan using dial(agent/<name>). You define agents in the agents.conf file.

![Mobilidade de agente: o usuário atende qualquer telefone, disca uma extensão de login e informa o número do agente e a senha; após agentlogin() ser bem‑sucedido o agente (Agent 300) está pronto para receber chamadas, e você pode verificar o status com o comando CLI `agent show all`](../images/14-queues-fig05.png)

### Agent Groups

You may choose to use agent groups. This function does not take ACD strategies into consideration. You will probably prefer to list all agents individually. If you want to transfer to an agent group, you can use `queues.conf`:

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### The configuration file for agents

Agents are defined in the file agents.conf. Below is a working example of the file.

![Um exemplo funcional do arquivo agents.conf: uma seção geral com persistentagents, uma seção agents com os parâmetros padrão (autologoff, ackcall, endcall, wrapuptime, musiconhold), e duas definições de agente (300 e 301)](../images/14-queues-fig06.png)

## Aplicações relacionadas ao ACD

O sistema de filas do Asterisk disponibiliza várias aplicações para implementar as filas no dialplan. A seguir, mostramos algumas delas.

### A aplicação queue()

Esta aplicação coloca chamadas recebidas em fila em uma fila de chamadas específica, conforme definido em queues.conf. A string de opções pode conter zero ou mais opções de uma única letra (mostradas na figura abaixo). Além de transferir a chamada, a chamada pode ser estacionada e então atendida por outro usuário. A URL opcional será enviada à parte chamada se o canal a suportar. O parâmetro AGI opcional configurará um script AGI a ser executado no canal da parte chamadora assim que ela for conectada a um membro da fila. O timeout fará a fila falhar após um número especificado de segundos, verificado entre cada ciclo de timeout e nova tentativa. Esta aplicação define a variável de status QUEUE ao concluir:

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### A aplicação agentlogin()

Esta aplicação solicita que o agente faça login no sistema. Ela sempre retorna -1. Enquanto estiver logado, o agente que recebe chamadas ouvirá um bip quando uma nova chamada chegar. O agente pode encerrar a chamada pressionando a tecla *.

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### A aplicação addQueueMember()

Esta aplicação adiciona dinamicamente um dispositivo (ex.: PJSIP/3000) a uma fila. Se o dispositivo já existir, retornará um erro.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### A aplicação removeQueueMember()

Esta aplicação remove dinamicamente um dispositivo da fila. Se o dispositivo não pertencer à fila, retornará um erro.

```
RemoveQueueMember(queuename[|interface])
```

### Aplicações de suporte e comandos CLI

Algumas aplicações e comandos de console podem ajudar no trabalho com filas. A seguir, descrevemos o que cada aplicação faz:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

The figure below summarizes the major tasks to create a working queue system.

![As tarefas de configuração do ACD: (1) criar a fila de chamadas (obrigatório), (2) definir parâmetros do agente (opcional), (3) criar agentes (opcional), (4) colocar a fila no dialplan (obrigatório), (5) configurar gravação do agente (opcional) e (6) verificar com agent show all e queue show (opcional)](../images/14-queues-fig10.png)

Step 1: Create the call queue In the file queues.conf:

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

Step 2: Define agent parameters In the file agents.conf:

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

Step 3: Create the agents In the file agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Step 4: Insert the queue in the dial plan, in the file `extensions.conf`:

```
; Telemarketing queue.
exten=>_0800XXXXXXX,1,Answer
exten=>_0800XXXXXXX,2,Set(CHANNEL(musicclass)=default)
exten=>_0800XXXXXXX,3,Set(TIMEOUT(digit)=5)
exten=>_0800XXXXXXX,4,Set(TIMEOUT(response)=10)
exten=>_0800XXXXXXX,5,Background(welcome)
exten=>_0800XXXXXXX,6,Queue(telemarketing)
; Transfer to the queue auditing
exten => 8000,1,Queue(auditing)
exten => 8000,2,Playback(demo-echotest); No auditor available
exten => 8000,3,Goto(8000,1) ; Verify auditor again
; Agent login for the telemarketing and auditing queues
exten => 9000,1,Wait(1)
exten => 9000,2,AgentLogin()
```

### Configure queue recording

Calls may be recorded using Asterisk's MixMonitor application. (The standalone Monitor application was removed in Asterisk 22, and the queues.conf `monitor-type` option now accepts only MixMonitor.) Recording can be enabled from within the queue application, beginning when the call is actually picked up. Only successful calls are recorded, and no recordings are performed while people are listening to MOH. To enable monitoring, simply specify monitor-format. This feature is otherwise disabled. You can set the filename for the recording using `Set(MONITOR_FILENAME=<filename>)`; otherwise it will use `MONITOR_FILENAME=${UNIQUEID}`.

In the file queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Operação da fila

Os exemplos a seguir explicam como usar a fila.

1. Login do agente. Exemplo: Um agente na fila de telemarketing atende o telefone e disca #9000. O agente ouve uma mensagem de login inválido e é solicitado a fornecer seu nome e senha. A fila de auditoria segue o mesmo procedimento.  
2. Fila. Uma vez na fila, o agente ouvirá MOH, se definido. Quando uma chamada chegar à fila de telemarketing, o agente ouvirá um bip e será conectado a essa chamada.  
3. Encerramento da chamada. Quando o agente termina a chamada, ele/ela pode:
   - Pressionar ‘*’ para desconectar e permanecer na fila.
   - Desconectar o telefone, desconectando-se da fila.
   - Pressionar #8000 para transferir a chamada para auditoria.

## Recursos avançados

O sistema de filas do Asterisk possui alguns recursos avançados para priorizar determinados clientes e agentes, além de habilitar um menu de usuário.

### Menu de usuário

Você pode definir um menu para um usuário enquanto ele aguarda na fila usando extensões de um dígito. Para habilitar essa opção, defina um contexto na configuração de filas **queues.conf**.

### Penalidade

Agentes podem ser configurados com uma penalidade. Uma fila enviará as chamadas primeiro para usuários com valores de penalidade mais baixos. Por exemplo, como sabemos que nossos clientes adoram a Susan e sua voz suave, podemos escolher atribuir prioridade 0 a ela. Alternativamente, o agente chamado Uber, que tem menos experiência, é menos preferido para o atendimento ao cliente; portanto, atribuímos prioridade 10 a esse agente. No arquivo **queues.conf**:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Prioridade

Filas operam no modo FIFO (first in first out). Se você quiser dar prioridade a clientes especiais (platinum, gold) pode definir prioridades diferenciadas. Para clientes platinum ou gold:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Clientes blue:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

A aplicação `agentcallbacklogin()` foi descontinuada pela Digium no Asterisk 1.4 (julho de 2006) e não está mais disponível no Asterisk 22. A abordagem recomendada é usar `AddQueueMember()` com uma interface PJSIP para adicionar dinamicamente membros no estilo callback a uma fila. O documento `queues-with-callback-members.txt` foi incluído em diretórios mais antigos do Asterisk `/doc` como orientação de migração.

O antigo driver de canal `chan_agent` também foi removido; sua funcionalidade foi reescrita como o módulo `app_agent_pool`, que é o que fornece `AgentLogin()`, `AgentRequest()` e a função de dialplan `AGENT()` no Asterisk 22 (eles ainda estão presentes — `app_agent_pool.so` vem com uma compilação padrão 22). Para call centers modernos, porém, o padrão é pular completamente os canais de agente e adicionar o dispositivo PJSIP do agente diretamente à fila com `AddQueueMember()`/`RemoveQueueMember()` (estaticamente em `queues.conf`, ou dinamicamente a partir do dialplan ou AMI). Isso é mais simples, integra‑se de forma limpa ao estado do dispositivo PJSIP, e é a abordagem usada ao longo deste capítulo.

## Estatísticas de fila

Todos os eventos das filas são registrados em /var/log/asterisk/queue_log. O formato do registro de fila está publicado no documento queuelog.txt no diretório /doc da documentação do Asterisk. Abaixo estão alguns dos eventos mais importantes registrados.

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

Você pode criar sua própria ferramenta para processar esses eventos ou usar um pacote de estatísticas pronto para uso:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – um pacote comercial, mantido ativamente, que analisa `queue_log` e continua sendo uma das ferramentas de relatório mais completas para call centers Asterisk.
- **Roll your own** – como o formato `queue_log` acima é estável e bem documentado, é simples analisá‑lo com um pequeno script (Python, etc.) e alimentar os eventos em um banco de dados ou painel.

Para uma abordagem mais orientada a eventos do que fazer tail em `queue_log`, as ações **Asterisk REST Interface (ARI)** e **AMI** `QueueSummary`/`QueueStatus` permitem que você construa painéis de fila em tempo real e integrações personalizadas contra o estado da fila em tempo real, em vez de analisar logs após o fato. ARI é a superfície de integração moderna e suportada para esse tipo de trabalho no Asterisk 22.

## Resumo

Neste capítulo, você aprendeu como usar um ACD, sua arquitetura e como configurá‑lo. Alguns recursos avançados, como prioridades e penalidades, também foram apresentados.

## Quiz

1. Which of the following are valid queue distribution strategies in `queues.conf` (choose all that apply)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. You can record a conversation between an agent and a customer from within the queue by setting the ___ option in the `queues.conf` file.
3. Which `strategy` rings members in the exact order they are listed in `queues.conf`?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. When the agent finishes a call in the telemarketing example, which actions can they take (choose all that apply)?
   - A. Press `*` to disconnect and stay in the queue
   - B. Hang up the phone and disconnect from the queue
   - C. Press `#8000` to transfer the call for auditing
   - D. Press `#` to log off all queues immediately
5. Which two tasks are *required* to get a working queue (choose all that apply)?
   - A. Create the queue
   - B. Create the agents
   - C. Configure agent parameters
   - D. Configure recording
   - E. Put the queue in the dial plan
6. In a call queue you can offer a single-digit menu the caller can dial while waiting. This is enabled by defining a(n) ___ in the queue's `queues.conf` section:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. The support applications `AddQueueMember()` and `RemoveQueueMember()` are used in the ___ to add or remove members at runtime:
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. Since chan_sip was removed in Asterisk 21, a static queue member must reference a channel such as ___ rather than `SIP/1001`.
9. The `wrapuptime` parameter is the minimum time after an agent disconnects a call before the queue will send that agent a new call.
   - A. True
   - B. False
10. A caller can be given a higher position in the same queue by setting the `QUEUE_PRIO` channel variable before calling `Queue()`.
    - A. True
    - B. False

**Answers:** 1 — A, C, D, E, F (roundrobin is not a documented strategy; in Asterisk 22 it survives only as a deprecated alias for rrmemory) · 2 — `monitor-format` (recording from the queue is enabled by specifying `monitor-format`; in Asterisk 22 `monitor-type` only supports MixMonitor) · 3 — C (linear) · 4 — A, B, C (`*` disconnects and stays; `#` is not a log-off-all key) · 5 — A, E · 6 — C (the `context` option) · 7 — A (the dial plan) · 8 — `PJSIP/1001` (any `PJSIP/` interface) · 9 — True · 10 — True
