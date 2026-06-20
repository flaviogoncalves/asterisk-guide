# Deployment, monitoring & scaling

Fazer o Asterisk atender uma chamada em um laboratório é uma coisa; executá‑lo como um serviço que sobrevive a falhas, reinicializações, atualizações e ataques — e que você pode observar, fazer backup e expandir — é outra. Este capítulo trata de tudo que acontece *depois* que o dialplan funciona. Começamos com o supervisor que mantém o Asterisk ativo (systemd), passamos para empacotá‑lo em um contêiner (usando o laboratório Docker do próprio livro como exemplo prático), depois abordamos gerenciamento de configuração e backups, monitoramento e observabilidade, e finalmente os padrões que você recorre quando um servidor não é suficiente: alta disponibilidade e escalabilidade, e as realidades de hospedagem na nuvem.

Tudo o que é mostrado foi verificado contra o laboratório Asterisk 22 do livro em `lab/` — o mesmo contêiner que você tem construído ao longo do livro.

## Objectives

By the end of this chapter, you should be able to:

- Run Asterisk 22 reliably under systemd, as a non-root user, with automatic restart
- Containerize Asterisk with Docker and understand the networking trade-offs
- Keep `/etc/asterisk` in version control and back up the right state
- Monitor a running system through the CLI, CDR/CEL, AMI/ARI and metrics
- Apply active/standby high availability and horizontal scaling patterns
- Host Asterisk in the cloud safely behind NAT and a firewall

## Executando Asterisk sob systemd

Em todas as distribuições Linux atuais — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — o gerenciador de serviços é **systemd**. O capítulo de instalação mostrou que a etapa `make config` (executada durante `make install`) instala um script de inicialização da distribuição (`/etc/init.d/asterisk` no Debian, um script `rc.d` no RedHat), que o systemd então encapsula automaticamente como um serviço; o Asterisk também fornece uma unidade nativa systemd em `contrib/systemd/asterisk.service` que você pode instalar em seu lugar para um controle mais fino. De qualquer forma, o systemd é o método suportado e de produção para executar o Asterisk. Consulte *Installing Asterisk 22* para a própria compilação; aqui nos concentramos no que o serviço oferece e como operá‑lo.

### A unidade de serviço e seu ciclo de vida

Depois que `make config` instalou o serviço, o ciclo de vida é o usual do systemd:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Algumas notas operacionais:

- **`restart` vs. um recarregamento gracioso.** `systemctl restart` encerra o processo e descarta todas as chamadas. Para alterações de configuração você quase nunca quer isso — use a CLI do Asterisk: `asterisk -rx 'core reload'` (ou um recarregamento específico de módulo, como `pjsip reload`). Reserve `systemctl restart` para atualizações ou um processo travado.
- **Anexar ao daemon em execução.** Com o Asterisk rodando como serviço, abra seu console com `asterisk -r` (ou `asterisk -rvvv` para saída detalhada). Isso se conecta ao daemon já em execução através de seu socket de controle; não inicia uma segunda cópia.

### `Restart=` substitui safe_asterisk

Historicamente o Asterisk era iniciado através do wrapper **safe_asterisk**, um script shell que reiniciava o Asterisk se ele travasse. Sob systemd essa tarefa pertence à diretiva `Restart=` da unidade — o systemd percebe a saída do processo e o traz de volta, com back‑off controlado por `RestartSec=` e proteção contra loops de falha por `StartLimitIntervalSec=`/`StartLimitBurst=`. Portanto, em um host systemd **safe_asterisk é substituído** e geralmente desnecessário. Se a unidade fornecida não definir isso, um sobrescrito drop‑in é a forma limpa de adicionar reinício‑em‑falha sem editar o arquivo empacotado:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Aplique‑o com `systemctl daemon-reload && systemctl restart asterisk`. Usar um drop‑in (em vez de editar a unidade instalada) significa que um futuro `make config` não sobrescreverá sua alteração.

### Executando como usuário não root

O Asterisk não deve ser executado como root em produção — um bug de código remoto em um processo rodando como root compromete todo o host, enquanto o mesmo bug em um processo sem privilégios fica contido. Existem dois locais complementares onde isso é imposto:

- **A unidade / asterisk.conf.** A unidade empacotada normalmente executa o Asterisk como o usuário e grupo `asterisk`. Você também pode (ou em vez disso) definir `runuser` e `rungroup` na seção `[options]` de `asterisk.conf`, que o daemon respeita ao abandonar privilégios após o bind:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Propriedade dos arquivos.** Os diretórios de tempo de execução devem ser graváveis por esse usuário. Após criar a conta, garanta a propriedade:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Como SIP (5060) e RTP (10000+) são todas portas altas, o Asterisk **não** precisa de root para vinculá‑las — apenas portas privilegiadas no estilo porta‑25 precisariam, o que o Asterisk não usa. Executar sem privilégios, portanto, é gratuito. (O capítulo de Segurança expande o porquê disso ser importante; veja *Asterisk Security*.)

## Containerizando Asterisk

Um contêiner empacota o Asterisk e suas dependências exatas em uma única imagem imutável, de modo que
o que você testa seja byte‑por‑byte o que você entrega. O trade‑off está na mídia em tempo real:
um servidor SIP é sensível à latência e precisa de uma ampla e previsível faixa de portas UDP
acessíveis de fora, e o networking de contêiner pode interferir. O resto desta
seção percorre o laboratório próprio do livro — `lab/Dockerfile` e
`lab/docker-compose.yml` — como um exemplo concreto e funcional, e então explica a única
armadilha que todos encontram: RTP e networking em ponte.

### A imagem: compilando o Asterisk a partir do código‑fonte

O `Dockerfile` do laboratório compila o Asterisk 22 a partir do código‑fonte no Debian 12. O formato dele vale a pena ler mesmo que você nunca escreva um por conta própria:

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Três coisas a destacar:

- **A versão está fixa** (`ARG ASTERISK_VERSION=22.10.0`). Reprodutibilidade é o
  objetivo principal da conteinerização — aumente-a deliberadamente, reconstrua, reteste.
- **`--with-pjproject-bundled` e `--with-jansson-bundled`** constroem a pilha SIP
  com a mesma versão do Asterisk, assim você depende de menos pacotes apt e nunca luta contra um
  PJSIP da distro que está fora de sincronia.
- **`CMD ["asterisk", "-f", "-vvv"]`** executa o Asterisk em *primeiro plano* (`-f`, "não fork"). Esta é a diferença chave em relação a um host systemd: o processo principal de um contêiner
  não deve se tornar daemon, ou o contêiner encerraria imediatamente. Portanto, em um contêiner você **não** usa a unidade systemd — o runtime do contêiner (Docker, mais a política `restart:`)
  torna‑se o supervisor que o `Restart=` da unidade era em uma VM.

### Bind-mounting `/etc/asterisk`

A imagem deliberadamente não contém **nenhuma** configuração. Em vez disso, `docker-compose.yml`
bind-mounts o diretório de configuração do host em:

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro` mapeia o diretório versionado `lab/asterisk/etc` para o `/etc/asterisk` do contêiner, somente leitura (`:ro`). O benefício é grande: a imagem permanece imutável e reutilizável, enquanto a configuração vive no host onde pode ser editada e, crucialmente, mantida no git (próxima seção). Para aplicar uma mudança de configuração você edita o arquivo e recarrega — `docker compose exec asterisk asterisk -rx 'core reload'` — sem reconstrução. `restart: unless-stopped` é o equivalente ao nível de compose do `Restart=` do systemd: o Docker reinicia o contêiner se o Asterisk sair, mas não se você o interromper deliberadamente.

### Host vs. bridged networking — o problema do RTP

Esta é a falha mais comum em Asterisk conteinerizado, portanto vale a pena entendê‑la precisamente. Por padrão o Docker coloca um contêiner em uma rede **bridged** e você publica portas individuais com `ports:`. O sinalização funciona — 5060 é uma porta. O problema está na mídia: o RTP usa uma *faixa* de portas UDP (o `rtp.conf` do laboratório define `rtpstart=10000` / `rtpend=10100`), e **toda** porta que possa transportar áudio deve ser publicada.

O laboratório faz exatamente isso:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Note the RTP publish range (`10000-10100`) matches `rtp.conf` exactly. Get this wrong —
publish too few ports, or a different range than `rtp.conf` — and calls connect but
have **one-way or no audio**, because the RTP packets land on a port Docker is not
forwarding. Two further cautions with bridged mode:

- **Publishing thousands of ports is slow and heavy.** A production RTP range is
  typically 10000–20000. Docker creating ~10000 userland proxy forwards is expensive at
  start-up and adds a hop in the media path. The lab keeps a deliberately small
  100-port range because it only ever runs one or two test calls.
- **NAT in the SDP.** Behind the bridge, Asterisk sees its private container IP and may
  advertise it in SDP. On a public host you must tell PJSIP its external address with
  `external_media_address` / `external_signaling_address` on the transport (and set
  `local_net`), exactly as you would behind any NAT — see *Cloud hosting* below.

The alternative is **host networking** (`network_mode: host`), which removes the bridge
entirely: the container shares the host's network stack, so 5060 and the whole RTP
range are reachable with no port publishing and no extra media hop. This is the
recommended mode for a real Asterisk container — it sidesteps the RTP-range problem
completely. Its cost is isolation: the container can bind any host port and you lose
compose's per-service network. (Host networking is a Linux feature; on Docker Desktop
for macOS/Windows it behaves differently, which is partly why this teaching lab uses
explicit published ports instead.)

### Volumes persistentes para spool e voicemail

A camada gravável de um contêiner é **efêmera** — destrua o contêiner e tudo o que ele
escreveu desaparece. Para o Asterisk isso significa que voicemail, gravações, o spool
de chamadas de saída e o banco de dados local desapareceriam a cada `docker compose up --build`. A
configuração sobrevive porque é montada por bind a partir do host; *estado* precisa do
mesmo tratamento. Dentro do contêiner as árvores relevantes são:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(O contêiner em execução no laboratório mostra exatamente isso — `/var/spool/asterisk` contém `voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` contém `astdb.sqlite3`.) Para preservá‑los, monte volumes nomeados para os diretórios que armazenam o estado que você se importa com:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

O laboratório de ensino omite isso de propósito — ele é sem estado e reproduzível por design, então cada `up` é uma página limpa — mas um contêiner de produção **deve** tê‑los, ou você perderá o voicemail na primeira redeploy.

## Configuration management and backups

The bind-mount above hints at the right model: treat `/etc/asterisk` as **code** and
the rest as **data**.

### Keep `/etc/asterisk` in version control

The config directory is a flat set of text files with no secrets that cannot be
templated — it is ideal for git. Initialise a repo in `/etc/asterisk` (or, as the lab
does, keep the config alongside the project and bind-mount it). Benefits:

- Every change is reviewable and revertible (`git diff`, `git revert`).
- You have an audit trail of who changed what and when.
- Combined with a container image, a known-good config commit plus a pinned image tag
  fully describes a deployment.

A couple of cautions specific to Asterisk config:

- **Secrets.** `pjsip.conf` (and `manager.conf`, `ari.conf`) contain passwords. Do not
  commit real secrets to a shared repo in clear text — template them (one file per
  environment, or a secrets manager / environment substitution at deploy time) and keep
  only placeholders in git. The lab's trivial `Lab-6001-secret` style passwords are fine
  *only* because they live on a private Docker subnet.
- **Per-environment templating.** The realtime values that differ between dev, staging
  and production (bind addresses, external IPs, trunk credentials, database URLs) are
  exactly the lines you templatize, keeping the bulk of the config identical across
  environments.

### What to back up

Configuration in git covers the dialplan and endpoints, but a live PBX accumulates
*state* that is not in any config file. A complete backup is:

| What | Where | Why |
|------|-------|-----|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (also in git) |
| Voicemail & recordings | `/var/spool/asterisk/` | user data — irreplaceable |
| Internal database | `/var/lib/asterisk/astdb.sqlite3` | `DB()` keys, device state |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` or SQL store | billing & history |
| External databases | your MySQL/PostgreSQL | realtime, CDR, voicemail |

The **astdb** deserves a note: it is Asterisk's small built-in key/value store (a
SQLite file at `/var/lib/asterisk/astdb.sqlite3`) used by `DB()` dialplan functions,
device states, follow-me settings and similar. You can dump it for inspection or backup
from the CLI:

```
asterisk -rx 'database show'
```

If your CDR/CEL or voicemail or PJSIP config lives in an external database (see
*Asterisk Real-Time* and *Asterisk Call Detail Records*), that database is now the
source of truth for that data and must be in your normal database backup rotation —
backing up `/etc/asterisk` alone is not enough.

## Monitoramento e observabilidade

Você não pode operar o que não pode ver. O Asterisk expõe seu estado em quatro níveis, desde
uma rápida olhada humana até um pipeline de métricas: o **CLI**, os registros **CDR/CEL**,
os eventos **AMI/ARI**, e os **metrics exporters**.

### Verificações de saúde via CLI

A verificação "está saudável?" mais rápida é o CLI. Os comandos abaixo são executados ao vivo contra
o laboratório. Primeiro os canais:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` em um sistema silencioso é normal; em um ocupado isso é sua concorrência em tempo real. `core show uptime` confirma que o processo não está reiniciando sob você:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Para a saúde do SIP, `pjsip show endpoints` mostra cada endpoint e se seus contatos registrados estão acessíveis. Do laboratório:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` aqui simplesmente indica que nenhum telefone está registrado nesses endpoints (o laboratório não tem clientes ativos) — assim que um softphone se registra e `qualify` o confirma, o estado mostra o contato como alcançável. Comandos auxiliares: `pjsip show contacts` (registros atuais e tempo de ida e volta), `pjsip show transports` e `pjsip show aor <name>` para um AOR. Estas são as ferramentas do dia a dia para a pergunta “por que a extensão X não pode ser alcançada?”.

### CDR and CEL

Cada chamada gera um **Call Detail Record** (CDR); **Channel Event Logging** (CEL) adiciona eventos mais detalhados por canal. Verifique se o CDR está ativo e qual backend o armazena:

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

O laboratório mostra `(none)` sob back‑ends registrados porque a configuração mínima do laboratório não carrega
nenhum módulo de armazenamento de CDR — então os registros são calculados mas não gravados em lugar nenhum. Em produção você
carrega um back‑end (CSV, ou `cdr_odbc`/`cdr_adaptive_odbc` no MySQL/PostgreSQL) e isso
se torna sua fonte de faturamento e histórico. CEL está **desativado por padrão** (`cel show
status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` apenas
quando você precisa de detalhe ao nível de evento. Ambos são abordados em profundidade em *Asterisk Call Detail
Records*; para monitoramento, o ponto é que CDR/CEL são seus registros *históricos*, enquanto
o CLI é sua visão *em tempo real*.

### AMI and ARI events

Para monitoramento programático e em tempo real você quer um fluxo push de eventos ao invés de
interrogar o CLI:

- **AMI (Asterisk Manager Interface)** é o protocolo TCP de eventos/comandos de longa data
  (`manager.conf`). Inscreva‑se e você receberá `Newchannel`, `Hangup`, `DialBegin`,
  `BridgeEnter`, `PeerStatus` e eventos semelhantes à medida que as chamadas acontecem — a espinha dorsal de painéis
  e ferramentas de contabilidade de chamadas. No laboratório o AMI está desativado por padrão (`manager show settings`
  relata `Manager (AMI): No`); você o habilita e o restringe em `manager.conf`.
- **ARI (Asterisk REST Interface)** é a interface moderna HTTP + WebSocket
  (`ari.conf`, servida pelo servidor HTTP embutido). Ela fornece um fluxo de eventos JSON e
  controle de chamadas granular — a escolha certa para novas integrações.

Ambos são detalhados em *Extending Asterisk with AMI and AGI* e *The Asterisk REST
Interface (ARI)*. Aviso relevante para implantação: **AMI e ARI são poderosos e nunca devem ser expostos à internet.** Vincule o
servidor HTTP ao localhost ou a uma rede de gerenciamento, use segredos fortes e únicos, e
configure o firewall nas portas — veja *Asterisk Security*.

### Metrics: Prometheus and Grafana

Para painéis e alertas, o Asterisk 22 inclui um exportador Prometheus,
**`res_prometheus.so`** (um módulo com nível de suporte *estendido*), que expõe métricas
em um endpoint HTTP que um servidor Prometheus coleta. Junto às métricas do processo principal, ele
inclui provedores plugáveis que cobrem canais, chamadas, endpoints, bridges e registros outbound do PJSIP:

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

Você pode confirmar que o módulo está presente na compilação de laboratório:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

It shows `Not Running` because the lab does not configure or load it; enabling it
(`prometheus.conf` plus the HTTP server) turns Asterisk into a Prometheus target. Point
Prometheus at the scrape endpoint and Grafana at Prometheus, and you get time-series
dashboards (concurrent calls, registrations, ASR/ACD trends) and alerting (e.g. "active
calls dropped to zero" or "registration failures spiking"). For teams already running
Prometheus/Grafana this is the natural way to fold Asterisk into existing observability,
rather than parsing CLI output.

### Códigos de resposta SIP que valem a pena monitorar

Whatever the pipeline, a few SIP results signal trouble and are worth alerting on:
sustained `401`/`407` challenge failures or `403 Forbidden` suggest a brute-force or
misconfigured-credential storm (cross-reference Fail2Ban in *Asterisk Security*);
`503 Service Unavailable` points at an overloaded or congested server or trunk; and a
spike in `408 Request Timeout`/`480 Temporarily Unavailable` usually means endpoints
have gone unreachable (NAT timeout, qualify failures).

## Alta disponibilidade e escalabilidade

Um servidor Asterisk é um ponto único de falha e tem um teto finito de chamadas. Os dois
problemas — *manter o serviço ativo* e *crescer* — têm respostas diferentes.

### Ativo/standby com IP flutuante

O padrão clássico e bem estabelecido de HA para Asterisk é **ativo/standby** (não
ativo/ativo — o estado de chamada no Asterisk é difícil de compartilhar ao vivo). Dois servidores idênticos,
um ativo, um standby, compartilham um **IP flutuante (virtual)** gerenciado por um gerenciador de cluster
como **keepalived** (VRRP) ou **Pacemaker/Corosync**. Telefones e troncos se registram no
IP flutuante, não em nenhum dos hosts reais. Se o nó ativo falhar sua verificação de saúde, o
IP flutuante se move para o standby, que assume o controle.

A ressalva honesta: um failover de IP **corta chamadas em andamento** — o Asterisk não
replica o estado dos canais ao vivo entre os nós, então quem está em chamada precisa discar novamente. Registros
são restabelecidos dentro de um ciclo de qualify/registration. O que o failover lhe oferece é que o
*serviço* se recupera em segundos sem intervenção manual, o que para a maioria dos PBXs é exatamente
o objetivo. Para que o standby realmente possa assumir, ambos os nós precisam da mesma
configuração (seu `/etc/asterisk` versionado no git, implantado identicamente) e do mesmo *estado* —
que é o próximo ponto.

### Externalizar estado com PJSIP Realtime

Ativo/standby só funciona se o standby souber dos mesmos endpoints e
registros que o nó ativo. A forma de conseguir isso é **parar de manter estado em
arquivos planos em uma única máquina** e movê‑lo para um banco de dados compartilhado que ambos os nós leem. **PJSIP
Realtime** (Sorcery suportado por um banco de dados) faz exatamente isso: endpoints, AORs, auths —
e, importante, **registrations** (a tabela `ps_contacts`) — vivem em MySQL/PostgreSQL
em vez de `pjsip.conf` e memória local. Ambos os nós Asterisk apontam para o mesmo banco de dados,
de modo que um telefone registrado através de um nó fica visível para o outro. Isso está coberto em
*Asterisk Real-Time* (a seção PJSIP Realtime / Sorcery); aqui o ponto de implantação é
que **externalizar o estado é o pré‑requisito tanto para HA quanto para escalonamento horizontal** —
sem isso, cada nó é uma ilha.

Aplique a mesma lógica ao resto do seu estado: CDR/CEL em um armazenamento SQL compartilhado, voicemail
em armazenamento compartilhado/replicado (ou `ODBC_STORAGE`), e as chaves astdb das quais você depende em um
banco de dados. Quando o estado está externo, os nós Asterisk tornam‑se quase intercambiáveis
como front‑ends.

### Proxies SIP na frente (OpenSIPS)

Para escalar *além* da capacidade de um único servidor você coloca um **proxy SIP/balancer de carga** na frente de
um pool de servidores de mídia Asterisk. **OpenSIPS** é um proxy SIP construído para isso, de altíssima taxa de transferência (eles lidam com centenas de milhares de registros e roteiam
sinalização sem tocar na mídia). O proxy apresenta um único endereço SIP ao mundo,
mantém o serviço de registro/ localização e distribui chamadas entre os back‑ends Asterisk. Essa separação — uma camada de proxy leve fazendo registro e roteamento, uma
camada Asterisk escalável horizontalmente realizando o processamento real das chamadas (IVR, filas,
conferências, transcodificação) — é como grandes implantações crescem além de uma única caixa. (A própria plataforma SipPulse usa OpenSIPS na frente de seus servidores de mídia/aplicação exatamente por esse motivo.)

### Escalonamento de mídia

O proxy distribui *sinalização* de forma barata; **a mídia é o recurso caro**. Relaying de RTP,
e especialmente transcodificação entre codecs (ex.: Opus ↔ G.711) ou execução de grandes
conferências, consome CPU e é o que realmente limita um servidor. Estratégias:

- **Evitar transcodificação** sempre

## Cloud hosting

Executar o Asterisk em uma VM na nuvem (AWS, GCP, Azure, um VPS) é comum e funciona bem, mas a
rede da nuvem é **NAT‑ed e firewalled por padrão**, o que conflita com SIP. As
preocupações específicas de implantação são as seguintes.

### NAT e o SDP

Uma VM na nuvem quase sempre tem um IP **privado** na sua NIC e um IP **público** separado que
o provedor faz NAT para ele. Se o Asterisk anunciar o IP privado no SDP, os telefones remotos enviam
RTP para um buraco negro — o clássico sintoma de áudio unilateral/ausente. Informe ao PJSIP sua identidade pública no transporte:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` faz o Asterisk reescrever o endereço que ele anuncia para pares públicos, enquanto
`local_net` indica quais pares são locais (e *não* devem ser reescritos). Isso é o
mesmo tratamento de NAT discutido para redes Docker em ponte acima — uma VM na nuvem está,
na prática, atrás de NAT.

### Firewall e a faixa de RTP

Dois firewalls geralmente se aplicam a uma VM na nuvem: o **grupo de segurança** do provedor / ACL de rede,
e o **iptables** do **host**. Ambos devem abrir as mesmas portas, e a política é a
mesma do capítulo Segurança. O conjunto de regras da 1ª edição recuperado
(`docs/legacy-labs/configs/Lab7/rules.v4`) captura a forma — aceitar SIP e a faixa de RTP,
aceitar estabelecido/relacionado, descartar o resto:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Dois ajustes que o capítulo Segurança faz e que importam aqui: abrir **5061 em TCP** (não
UDP) se você usar SIP/TLS, e lembrar que a faixa UDP de RTP no seu firewall deve corresponder
exatamente a `rtpstart`/`rtpend` em `rtp.conf` — a mesma faixa que você publica em um contêiner.
Não duplique a construção iptables/Fail2Ban aqui; **siga as seções firewall, Fail2Ban e
TLS/SRTP de *Asterisk Security*** (Fail2Ban monitora o canal de logger `security` que o laboratório já habilita em `logger.conf`) e aplique essa política tanto no firewall do *host*
quanto no grupo de segurança da nuvem.

### Latência, região e o SBC

- **Escolha uma região próxima dos seus usuários.** Voz é sensível à latência — latência unidirecional de voz acima de ~150 ms é perceptível. Hospede a VM na região mais próxima da maioria dos seus
  telefones e troncos; mídia intercontinental soa visivelmente pior.
- **Coloque um SBC na frente de qualquer implantação voltada para a internet.** Um **Session Border
  Controller** termina SIP/RTP na borda, oculta sua topologia, normaliza NAT e
  absorve tráfego de DoS e varredura antes que ele alcance o Asterisk. A recomendação central
  do capítulo Segurança — *não exponha o Asterisk bruto à internet* — se aplica em dobro na
  nuvem, onde o IP público da sua VM é escaneado em minutos após ser iniciado. Um SBC (ou,
  no mínimo, um proxy SIP endurecido como OpenSIPS mais Fail2Ban) é o padrão
  de borda.

## Summary

Deployment is where a working dialplan becomes a dependable service. On a VM, run
Asterisk under **systemd** as a **non-root** user, letting the unit's `Restart=` keep it
alive (safe_asterisk is superseded) and using `core reload` rather than `systemctl
restart` for config changes. **Containerizing** with Docker — as the book's lab does —
gives you an immutable, pinned image with config **bind-mounted** from a git'd
`/etc/asterisk`; the catch is media, so either use **host networking** or publish an RTP
port range that **exactly matches `rtp.conf`**, and mount **persistent volumes** for
spool/voicemail/astdb so state survives a redeploy. Treat config as code and **back up the
state** config does not capture: voicemail, recordings, `astdb.sqlite3`, and CDR/CEL.
**Observe** the system at four levels — the CLI (`core show channels`, `pjsip show
endpoints`) for the live view, **CDR/CEL** for history, **AMI/ARI** for programmatic
events, and the **`res_prometheus`** exporter into Grafana for dashboards and alerts —
while keeping AMI/ARI off the public internet. To **stay up**, run active/standby with a
**floating IP** (accepting that failover drops live calls); to **grow**, externalize state
with **PJSIP Realtime**, front a pool of media servers with **OpenSIPS**, and
minimize transcoding because **media — not registrations — is what caps a server**.
Finally, in the **cloud**, treat the VM as behind NAT (`external_media_address`,
`local_net`), open the firewall per the Security chapter in both the host and the provider
security group, pick a low-latency region, and never expose raw Asterisk — put an **SBC**
at the edge.

## Quiz

1. Em um host systemd, o que substitui a antiga tarefa do wrapper `safe_asterisk` de reiniciar um Asterisk que travou?
   - A. Um trabalho cron
   - B. A diretiva `Restart=` do arquivo de unidade
   - C. `systemctl enable`
   - D. O astdb
2. Para aplicar uma mudança de configuração a um Asterisk em execução **sem interromper chamadas**, você deve:
   - A. `systemctl restart asterisk`
   - B. Reiniciar o servidor
   - C. `asterisk -rx 'core reload'`
   - D. Reconstruir a imagem do contêiner
3. Um Asterisk conteinerizado (rede em ponte) conecta chamadas, mas **não tem áudio**. A causa mais provável é:
   - A. O dialplan está errado
   - B. O intervalo de portas UDP RTP publicado não corresponde a `rtpstart`/`rtpend` em `rtp.conf`
   - C. O CDR está desativado
   - D. O CLI está inacessível
4. Quais diretórios devem ser montados como **volumes persistentes** para que uma reinstalação do contêiner não perca o estado? (marque todas as opções aplicáveis)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (já bind-montado a partir do host)
   - D. `/usr/sbin`
5. Qual comando CLI fornece a contagem ao vivo de chamadas ativas?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. No Asterisk 22, a forma suportada de expor métricas de chamadas/canais para uma pilha Prometheus/Grafana é:
   - A. Analisar o arquivo de log `full`
   - B. O módulo `res_prometheus.so`
   - C. Scripts AGI
   - D. Não existe
7. Qual é o pré-requisito tanto para failover HA quanto para escalonamento horizontal entre múltiplos nós Asterisk?
   - A. Executar como root
   - B. Externalizar o estado (ex.: registros PJSIP Realtime em um banco de dados compartilhado)
   - C. Desativar o CDR
   - D. Usar rede em ponte
8. Qual recurso limita mais diretamente quantas chamadas simultâneas um servidor Asterisk pode atender?
   - A. O número de usuários registrados
   - B. Processamento de mídia, especialmente transcodificação
   - C. O tamanho de `/etc/asterisk`
   - D. O backend do CDR
9. Em uma VM na nuvem, quais configurações de transporte `pjsip.conf` fazem o Asterisk anunciar seu endereço público para que o áudio remoto funcione? (marque todas as opções aplicáveis)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Para uma implantação na nuvem voltada para a internet, a regra central do capítulo Segurança é:
    - A. Sempre usar duas NICs
    - B. Nunca expor o Asterisk puro à internet; colocar um SBC (ou proxy endurecido + Fail2Ban) na borda
    - C. Usar apenas UDP
    - D. Desativar TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
