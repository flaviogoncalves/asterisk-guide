# Call Queues

Las colas de llamadas, también conocidas como ACD (Distribución Automática de Llamadas), están adquiriendo una importancia cada vez mayor para responder a las llamadas de los clientes de manera eficiente. Un distribuidor automático de llamadas puede ayudar a reducir costos, aumentar el servicio y mejorar las ventas, ya que los distribuidores de llamadas afectan cómo funciona su negocio—no solo por unos días, sino durante muchos años. En un entorno de centro de llamadas, el factor número uno son las personas; son el recurso más costoso. Contratar, capacitar y motivar a los agentes requiere tiempo, dinero y paciencia. Con un ACD, puede maximizar la productividad de los agentes dimensionando con precisión la cantidad de agentes necesarios, controlando los atendientes buenos y malos, y analizando el flujo de llamadas.

## Objetivos

Al final de este capítulo, deberías ser capaz de:

- Entender por qué y cómo usar las colas de llamadas
- Entender la teoría básica de las colas de llamadas
- Instalar y configurar el sistema de colas

## ¿Cómo funcionan las colas?

Las colas de llamadas no son exactamente una novedad. Cuando tienes un alto flujo de llamadas entrantes, es difícil distribuirlas adecuadamente. Usar una estrategia de grupo donde el teléfono suena simultáneamente en todos los agentes no parece funcionar, a menos que tengas solo unos pocos agentes. Sin embargo, una cola de llamadas entregará las llamadas a un solo agente disponible cada vez y pondrá al cliente en espera con música cuando no haya agentes disponibles. La cola funciona reteniendo la llamada mientras se busca un agente desocupado para contestarla. Uno de los mayores beneficios de la cola es evitar perder llamadas mientras se brinda la posibilidad de generar estadísticas.

![Una cola de llamadas: llamadas entrantes 1-800 ingresan a la cola y una estrategia ACD (ringall, rrmemory, leastrecent, priority y otras) las distribuye a los agentes disponibles](../images/14-queues-fig01.png)

Normalmente, una cola de llamadas funciona así:

- Los agentes inician sesión en la cola.
- Las llamadas entrantes se ponen en cola.
- Se utiliza una estrategia de colas para distribuir las llamadas a los agentes.
- Se reproduce música en espera mientras el llamante espera.
- Se pueden hacer anuncios a los llamantes, notificándoles el tiempo de espera
- La llamada es contestada por el agente y se generan estadísticas.

La aplicación principal de las colas es el servicio al cliente. Al usar colas, evitas perder llamadas cuando tus agentes están ocupados. Puedes agregar nuevos agentes a la cola si observas que el número de llamantes en la cola está creciendo. Otra ventaja de las colas es que ahora puedes obtener estadísticas como tasa de abandono de llamadas, duración promedio de llamadas y objetivo de respuesta de llamadas. Estas estadísticas te ayudarán a determinar cuántos agentes necesitas para brindar un mejor servicio a tu cliente.

### Arquitectura ACD

La arquitectura ACD está formada por colas y agentes. Un agente puede estar en dos colas al mismo tiempo. Una cola puede tener agentes, canales y grupos de agentes.

![Arquitectura ACD: cada cola (Servicio al Cliente, Ventas Internas) es alimentada por un número de teléfono y entrega llamadas a los agentes, que a su vez están vinculados a canales físicos](../images/14-queues-fig02.png)

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

## Agentes

Los agentes se implementan como canales proxy. Pueden usarse dentro de las colas. Otro uso para los canales de agente es la movilidad de extensiones. El usuario puede iniciar sesión usando cualquier teléfono y recibir sus llamadas. Esto permite que un usuario vaya a cualquier habitación para convertirla en una oficina. Puedes marcar un agente en el plan de marcación usando dial(agent/<name>). Definas los agentes en el archivo agents.conf.

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### Grupos de Agentes

Puedes optar por usar grupos de agentes. Esta función no tiene en cuenta las estrategias de ACD. Probablemente prefieras listar a todos los agentes individualmente. Si deseas transferir a un grupo de agentes, puedes usar `queues.conf`:

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### El archivo de configuración para agentes

Los agentes se definen en el archivo agents.conf. A continuación se muestra un ejemplo funcional del archivo.

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## Aplicaciones relacionadas con ACD

El sistema de colas de Asterisk pone a disposición varias aplicaciones para implementar las colas en el plan de marcación. A continuación, mostramos algunas de ellas.

### La aplicación queue()

Esta aplicación coloca las llamadas entrantes en una cola de llamadas particular según lo definido en queues.conf. La cadena de opciones puede contener cero o más opciones de una sola letra (mostradas en la figura a continuación). Además de transferir la llamada, una llamada puede ser estacionada y luego recogida por otro usuario. La URL opcional será enviada a la parte llamada si el canal lo soporta. El parámetro opcional AGI configurará un script AGI para ejecutarse en el canal de la parte llamante una vez que estén conectados a un miembro de la cola. El tiempo de espera provocará que la cola falle después de un número especificado de segundos, verificado entre cada ciclo de tiempo de espera y reintento. Esta aplicación establece la variable de estado QUEUE al completarse:

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### La aplicación agentlogin()

Esta aplicación solicita al agente iniciar sesión en el sistema. Siempre devuelve -1. Mientras está conectado, el agente que recibe llamadas escuchará un pitido cuando llegue una nueva llamada. El agente puede descartar la llamada presionando la tecla *.

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### La aplicación addQueueMember()

Esta aplicación agrega dinámicamente un dispositivo (p. ej., PJSIP/3000) a una cola. Si el dispositivo ya existe, devolverá un error.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### La aplicación removeQueueMember()

Esta aplicación elimina dinámicamente un dispositivo de la cola. Si el dispositivo no pertenece a la cola, devolverá un error.

```
RemoveQueueMember(queuename[|interface])
```

### Aplicaciones de soporte y comandos CLI

Algunas aplicaciones y comandos de consola pueden ayudar en el trabajo con colas. A continuación se describe lo que hace cada aplicación:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

The figure below summarizes the major tasks to create a working queue system.

![Las tareas de configuración del ACD: (1) crear la cola de llamadas (requerido), (2) definir los parámetros del agente (opcional), (3) crear agentes (opcional), (4) colocar la cola en el dialplan (requerido), (5) configurar la grabación del agente (opcional), y (6) verificar con agent show all y queue show (opcional)](../images/14-queues-fig10.png)

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

## Operación de la cola

Los siguientes ejemplos explican cómo usar la cola.

1. Inicio de sesión del agente. Ejemplo: Un agente en la cola de telemarketing levanta el teléfono y marca #9000. El agente escucha un mensaje de inicio de sesión inválido y se le solicita su nombre y contraseña. La cola de auditoría sigue el mismo procedimiento.
2. Cola. Una vez en la cola, el agente escuchará MOH, si está definido. Cuando una llamada llega a la cola de telemarketing, el agente escuchará un pitido y será conectado a esa llamada.
3. Finalización de la llamada. Cuando el agente termina la llamada, él/ella puede:
   - Presionar ‘*’ para desconectar y permanecer en la cola.
   - Colgar el teléfono, desconectándose así de la cola.
   - Presionar #8000 para transferir la llamada para auditoría.

## Recursos avanzados

El sistema de colas de Asterisk tiene algunas funciones avanzadas para priorizar a ciertos clientes y agentes, así como habilitar un menú de usuario.

### Menú de usuario

Puede definir un menú para un usuario mientras espera en la cola usando extensiones de un dígito. Para habilitar esta opción, defina un contexto en la configuración de colas en **queues.conf**.

### Penalización

Los agentes pueden configurarse con una penalización. Una cola enviará primero las llamadas a los usuarios con valores de penalización más bajos. Por ejemplo, como sabemos que a nuestros clientes les encanta Susan y su voz suave, podemos asignarle prioridad 0. Alternativamente, el agente llamado Uber, que tiene menos experiencia, es menos preferido para el servicio al cliente; por lo tanto, asignamos una prioridad 10 a este agente. En el archivo **queues.conf**:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Prioridad

Las colas operan en modo FIFO (first in first out). Si desea dar prioridad a clientes especiales (platino, oro) puede configurar prioridades diferenciadas. Para clientes platino o oro:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Clientes azules:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

The application `agentcallbacklogin()` was deprecated by Digium in Asterisk 1.4 (July 2006) and is no longer available in Asterisk 22. The recommended approach is to use `AddQueueMember()` with a PJSIP interface to dynamically add callback-style members to a queue. The document `queues-with-callback-members.txt` was included in older Asterisk `/doc` directories for migration guidance.

The old `chan_agent` channel driver was likewise removed; its functionality was rewritten as the `app_agent_pool` module, which is what provides `AgentLogin()`, `AgentRequest()` and the `AGENT()` dialplan function in Asterisk 22 (these are still present — `app_agent_pool.so` ships with a stock 22 build). For modern call centers, however, the standard pattern is to skip agent channels entirely and add the agent's PJSIP device directly to the queue with `AddQueueMember()`/`RemoveQueueMember()` (statically in `queues.conf`, or dynamically from the dialplan or AMI). This is simpler, integrates cleanly with PJSIP device state, and is the approach used throughout this chapter.

## Estadísticas de colas

Todos los eventos de las colas se registran en /var/log/asterisk/queue_log. El formato del registro de colas se publica en el documento queuelog.txt en el directorio /doc de la documentación de Asterisk. A continuación se presentan algunos de los eventos más importantes registrados.

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

Puede crear su propia utilidad para procesar estos eventos o usar un paquete de estadísticas listo para usar:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – un paquete comercial, mantenido activamente que analiza `queue_log` y sigue siendo una de las herramientas de informes más completas para centros de llamadas Asterisk.
- **Roll your own** – porque el formato `queue_log` anterior es estable y está bien documentado, es sencillo analizarlo con un script pequeño (Python, etc.) y alimentar los eventos a una base de datos o panel de control.

Para un enfoque más orientado a eventos que el de seguir `queue_log`, la **Asterisk REST Interface (ARI)** y las acciones **AMI** `QueueSummary`/`QueueStatus` le permiten crear paneles de colas en tiempo real e integraciones personalizadas contra el estado de la cola en tiempo real en lugar de analizar los registros después del hecho. ARI es la superficie de integración moderna y soportada para este tipo de trabajo en Asterisk 22.

## Resumen

En este capítulo has aprendido cómo usar un ACD, su arquitectura y cómo configurarlo. También se presentaron algunas funciones avanzadas, como prioridades y penalizaciones.

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
