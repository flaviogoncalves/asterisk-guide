# Call Queues

Call queues, also known as ACD (Automatic Call Distribution) are becoming increasingly important for answering customer calls efficiently. An automatic call distributor can help reduce costs, increase service, and improve sales as call distributors affect how your business works—not for a few days, but for many years. In a call center environment, the number one factor is people; they are the most expensive resource. It takes time, money, and patience to hire, train, and motivate agents. With an ACD, you can maximize agents’ productivity by precisely dimensioning the number of agents required, controlling good and bad attendants, and analyzing the call flow.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Comprendre pourquoi et comment utiliser les files d'attente d'appels
- Comprendre la théorie de base des files d'attente d'appels
- Installer et configurer le système de files d'attente

## Comment fonctionnent les files d’attente ?

Les files d’attente d’appels ne sont pas exactement une nouveauté. Lorsque vous avez un flux d’appels entrants important, il est difficile de distribuer les appels de manière appropriée. Utiliser une stratégie de groupe où le téléphone sonne simultanément sur tous les agents ne semble pas fonctionner, sauf si vous n’avez que quelques agents. En revanche, une file d’attente ne délivrera les appels qu’à un seul agent disponible à la fois et mettra le client en attente avec de la musique lorsqu’aucun agent n’est disponible. La file d’attente fonctionne en retenant l’appel tout en recherchant un agent libre pour répondre. L’un des plus grands avantages de la file d’attente est d’éviter la perte d’appels tout en offrant la possibilité de générer des statistiques.

![Une file d’attente d’appels : les appels entrants 1‑800 entrent dans la file et une stratégie ACD (ringall, rrmemory, leastrecent, priority, et autres) les distribue aux agents disponibles](../images/14-queues-fig01.png)

En général, une file d’attente fonctionne ainsi :

- Les agents se connectent à la file.
- Les appels entrants sont mis en file d’attente.
- Une stratégie de mise en file d’attente pour distribuer les appels est utilisée afin d’envoyer les appels aux agents.
- De la musique d’attente est jouée pendant que l’appelant attend.
- Des annonces peuvent être faites aux appelants, les informant du temps d’attente
- L’appel est répondu par l’agent et des statistiques sont générées.

L’application principale des files d’attente est le service client. En utilisant les files d’attente, vous évitez de perdre des appels lorsque vos agents sont occupés. Vous pouvez ajouter de nouveaux agents à la file si vous constatez que le nombre d’appelants dans la file augmente. Un autre avantage des files d’attente est que vous pouvez désormais disposer de statistiques telles que le taux d’abandon d’appel, la durée moyenne des appels et l’objectif de réponse aux appels. Ces statistiques vous aideront à déterminer le nombre d’agents nécessaire pour offrir un meilleur service à votre clientèle.

### Architecture ACD

L’architecture ACD est constituée de files d’attente et d’agents. Un agent peut être dans deux files d’attente en même temps. Une file d’attente peut contenir des agents, des canaux et des groupes d’agents.

![Architecture ACD : chaque file d’attente (Customer Service, Inside Sales) est alimentée par un numéro de téléphone et délivre les appels aux agents, qui sont à leur tour liés à des canaux physiques](../images/14-queues-fig02.png)

## Queues

Les files d’attente sont définies dans le fichier de configuration queues.conf. Les agents sont des assistants qui se connectent et sont membres des files d’attente. Les agents sont définis dans le fichier agents.conf. Le système de files d’attente a considérablement évolué au fil des versions, rendant le fichier de configuration très complet. Nous expliquerons certains des paramètres principaux. Un paramètre général à souligner est `autofill` :

```
autofill=yes
```

L’ancien comportement de la file d’attente était de type sériel. La file attendait qu’un appel soit distribué avant d’envoyer l’appel suivant au prochain agent. Si un agent met 15 secondes à répondre à un appel, les autres appels dans la file devaient attendre que cet appel soit répondu. Pour les files à fort volume, ce comportement était inefficace. Le nouveau comportement autofill=yes n’attend pas qu’un appel soit répondu, mais fonctionne en parallèle. Vous pouvez enregistrer les appels dans la file en utilisant l’option mixmonitor. Dans ce mode, les appels sont enregistrés et mixés simultanément.

### Queue configuration file

Les files d’attente sont configurées dans le fichier queues.conf. Dans la figure, vous trouverez un exemple fonctionnel d’une file d’attente.

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### Agents

Vous pouvez configurer vos agents dans le fichier agents.conf. Les agents peuvent se connecter depuis n’importe quelle extension pour recevoir des appels. Vous pouvez appeler un agent en utilisant :

```
Dial(agent/<name>)
```

#### Agent login

Le flux de connexion pour l’Agent 300 fonctionne ainsi :

- L’utilisateur compose une extension qui exécute l’application `AgentLogin()`.
- `AgentLogin()` est exécutée et l’agent est associé au canal actuel.
- Vous pouvez vérifier l’état des agents avec la commande `agent show all`.

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

Vous pouvez définir les agents dans le fichier agents.conf

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

Les membres sont des canaux actifs répondant à la file d’attente. Les membres peuvent être des canaux directs (PJSIP, DAHDI) ou des agents qui se connectent avant de recevoir des appels.

### Strategies

Les appels sont distribués parmi les membres selon l’une de ces stratégies :

- ringall : Sonne tous les canaux disponibles jusqu’à ce que quelqu’un réponde.
- leastrecent : Distribue au membre le moins récemment utilisé.
- fewestcalls : Distribue au membre ayant le moins d’appels.
- random : Sonnerie d’une interface aléatoire.
- wrandom : Sonnerie d’une interface aléatoire, mais utilise la pénalité du membre comme poids lors du calcul de sa métrique.
- rrmemory : Utilise le round robin avec mémoire ; il se souvient où il s’est arrêté avec l’appel lors du dernier passage.
- rrordered : Identique à rrmemory, sauf que l’ordre des membres de la file tel qu’il apparaît dans le fichier de configuration est conservé.
- linear : Sonne les membres dans l’ordre où ils sont listés dans queues.conf ; pour les membres dynamiques, dans l’ordre où ils ont été ajoutés.

L’ancienne stratégie `roundrobin` a été dépréciée dès Asterisk 1.4. Elle n’est plus documentée et ne doit pas être utilisée : dans Asterisk 22, l’analyseur accepte encore le mot `roundrobin`, mais uniquement comme alias de compatibilité rétroactive qui correspond à `rrmemory`. Utilisez `rrmemory` (ou `rrordered`) explicitement à la place. La liste ci‑dessus constitue l’ensemble des stratégies documentées pour l’option `strategy` dans l’Asterisk 22 `queues.conf`.

## Agents

Les agents sont implémentés comme des canaux proxy. Ils peuvent être utilisés à l’intérieur des files d’attente. Une autre utilisation des canaux d’agent est la mobilité d’extension. L’utilisateur peut se connecter avec n’importe quel téléphone et recevoir ses appels. Cela permet à un utilisateur d’aller dans n’importe quelle pièce pour en faire un bureau. Vous pouvez appeler un agent dans le dialplan avec dial(agent/<name>). Vous définissez les agents dans le fichier agents.conf.

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### Agent Groups

Vous pouvez choisir d’utiliser des groupes d’agents. Cette fonction ne prend pas en compte les stratégies ACD. Vous préférerez probablement lister tous les agents individuellement. Si vous voulez transférer vers un groupe d’agents, vous pouvez utiliser `queues.conf` :

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### The configuration file for agents

Les agents sont définis dans le fichier agents.conf. Vous trouverez ci‑dessous un exemple fonctionnel du fichier.

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## Applications liées à l'ACD

Le système de files d’attente d’Asterisk met à disposition plusieurs applications pour implémenter les files d’attente dans le dialplan. Ci‑dessous, nous en présentons quelques‑unes.

### L’application queue()

Cette application place les appels entrants dans une file d’attente particulière telle que définie dans **queues.conf**. La chaîne d’options peut contenir zéro ou plusieurs options d’une seule lettre (illustrées dans la figure ci‑après). En plus de transférer l’appel, un appel peut être mis en attente puis récupéré par un autre utilisateur. L’URL optionnelle sera envoyée à la partie appelée si le canal le supporte. Le paramètre AGI optionnel configurera un script AGI à exécuter sur le canal de l’appelant une fois qu’il sera connecté à un membre de la file. Le délai d’attente provoquera l’échec de la file après un nombre de secondes spécifié, vérifié entre chaque cycle de délai et de nouvelle tentative. Cette application définit la variable d’état **QUEUE** à la fin :

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### L’application agentlogin()

Cette application demande à l’agent de se connecter au système. Elle renvoie toujours **-1**. Une fois connecté, l’agent qui reçoit les appels entendra un bip lorsqu’un nouvel appel arrivera. L’agent peut rejeter l’appel en appuyant sur la touche *.

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### L’application addQueueMember()

Cette application ajoute dynamiquement un dispositif (par exemple, **PJSIP/3000**) à une file d’attente. Si le dispositif existe déjà, elle renverra une erreur.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### L’application removeQueueMember()

Cette application retire dynamiquement un dispositif de la file d’attente. Si le dispositif n’appartient pas à la file, elle renverra une erreur.

```
RemoveQueueMember(queuename[|interface])
```

### Applications de support et commandes CLI

Certaines applications et certaines commandes console peuvent aider à travailler avec les files d’attente. Ce qui suit décrit le rôle de chaque application :

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Tâches de configuration

La figure ci‑dessous résume les principales tâches pour créer un système de files d’attente fonctionnel.

![The ACD configuration tasks: (1) create the call queue (required), (2) define agent parameters (optional), (3) create agents (optional), (4) put the queue in the dial plan (required), (5) configure agent recording (optional), and (6) verify with agent show all and queue show (optional)](../images/14-queues-fig10.png)

Étape 1 : Créer la file d’attente Dans le fichier queues.conf:

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

Étape 2 : Définir les paramètres d’agent Dans le fichier agents.conf:

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

Étape 3 : Créer les agents Dans le fichier agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Étape 4 : Insérer la file d’attente dans le dialplan, dans le fichier `extensions.conf`:

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

### Configurer l’enregistrement de la file d’attente

Les appels peuvent être enregistrés à l’aide de l’application MixMonitor d’Asterisk. (L’application autonome Monitor a été supprimée dans Asterisk 22, et l’option queues.conf `monitor-type` accepte désormais uniquement MixMonitor.) L’enregistrement peut être activé depuis l’application de file d’attente, à partir du moment où l’appel est réellement décroché. Seuls les appels réussis sont enregistrés, et aucun enregistrement n’est effectué pendant que des personnes écoutent la MOH. Pour activer la surveillance, il suffit de spécifier monitor-format. Cette fonctionnalité est sinon désactivée. Vous pouvez définir le nom de fichier pour l’enregistrement en utilisant `Set(MONITOR_FILENAME=<filename>)` ; sinon il utilisera `MONITOR_FILENAME=${UNIQUEID}`.

Dans le fichier queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Fonctionnement de la file d'attente

Les exemples suivants expliquent comment utiliser la file d'attente.

1. Connexion d'un agent. Exemple : Un agent de la file d'attente télévente décroche le téléphone et compose #9000. L'agent entend un message de connexion invalide et on lui demande son nom et son mot de passe. La file d'attente d'audit suit la même procédure.
2. File d'attente. Une fois dans la file, l'agent entendra de la MOH, si définie. Lorsqu'un appel arrive dans la file télévente, l'agent entendra un bip et sera connecté à cet appel.
3. Fin d'appel. Lorsque l'agent termine l'appel, il/elle peut :
   - Appuyer sur ‘*’ pour se déconnecter tout en restant dans la file.
   - Débrancher le téléphone, ce qui le déconnecte de la file.
   - Appuyer sur #8000 pour transférer l'appel à l'audit.

## Ressources avancées

Le système de files d’attente d’Asterisk possède des fonctionnalités avancées pour prioriser certains clients et agents ainsi que pour activer un menu utilisateur.

### Menu utilisateur

Vous pouvez définir un menu pour un utilisateur en attente dans la file d’attente en utilisant des extensions à un chiffre. Pour activer cette option, définissez un contexte dans la configuration des files d’attente `queues.conf`.

### Pénalité

Les agents peuvent être configurés avec une pénalité. Une file d’attente enverra d’abord les appels aux utilisateurs ayant des valeurs de pénalité plus faibles. Par exemple, comme nous savons que nos clients apprécient Susan et sa voix douce, nous pouvons choisir de lui attribuer la priorité 0. À l’inverse, l’agent nommé Uber, qui a moins d’expérience, est moins préféré pour le service client ; nous lui attribuons donc la priorité 10. Dans le fichier `queues.conf` :

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priorité

Les files d’attente fonctionnent en mode FIFO (first in first out). Si vous souhaitez accorder une priorité à des clients spéciaux (platinum, gold) vous pouvez mettre en place des priorités différenciées. Pour les clients platinum ou gold :

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Clients bleus :

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

The application `agentcallbacklogin()` was deprecated by Digium in Asterisk 1.4 (July 2006) and is no longer available in Asterisk 22. The recommended approach is to use `AddQueueMember()` with a PJSIP interface to dynamically add callback-style members to a queue. The document `queues-with-callback-members.txt` was included in older Asterisk `/doc` directories for migration guidance.

The old `chan_agent` channel driver was likewise removed; its functionality was rewritten as the `app_agent_pool` module, which is what provides `AgentLogin()`, `AgentRequest()` and the `AGENT()` dialplan function in Asterisk 22 (these are still present — `app_agent_pool.so` ships with a stock 22 build). For modern call centers, however, the standard pattern is to skip agent channels entirely and add the agent's PJSIP device directly to the queue with `AddQueueMember()`/`RemoveQueueMember()` (statically in `queues.conf`, or dynamically from the dialplan or AMI). This is simpler, integrates cleanly with PJSIP device state, and is the approach used throughout this chapter.

## Queue statistics

All events from queues are logged to /var/log/asterisk/queue_log. The format of the queue log is published in the document queuelog.txt in the /doc directory of the Asterisk documentation. Below are some of the most important events logged.

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

You can build your own utility to process these events or use a ready-to-run statistics package:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – a commercial, actively maintained package that parses `queue_log` and remains one of the most complete reporting tools for Asterisk call centers.
- **Roll your own** – because the `queue_log` format above is stable and well documented, it is straightforward to parse it with a small script (Python, etc.) and feed the events into a database or dashboard.

For a more event-driven approach than tailing `queue_log`, the **Asterisk REST Interface (ARI)** and the **AMI** `QueueSummary`/`QueueStatus` actions let you build live queue dashboards and custom integrations against real-time queue state rather than after-the-fact log parsing. ARI is the modern, supported integration surface for this kind of work in Asterisk 22.

## Résumé

Dans ce chapitre vous avez appris comment utiliser un ACD, son architecture, et comment le configurer. Certaines fonctionnalités avancées telles que les priorités et les pénalités ont également été présentées.

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
