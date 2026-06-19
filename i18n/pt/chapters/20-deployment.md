# Deployment, monitoring & scaling

Fazer o Asterisk atender a uma chamada em um laboratório é uma coisa; executá-lo como um serviço que sobrevive a falhas, reinicializações, atualizações e atacantes — e que você pode observar, fazer backup e expandir — é outra. Este capítulo trata de tudo o que acontece *depois* que o dialplan funciona. Começamos com o supervisor que mantém o Asterisk ativo (systemd), passamos para o empacotamento em um contêiner (usando o próprio laboratório Docker do livro como exemplo prático), depois cobrimos o gerenciamento de configuração e backups, monitoramento e observabilidade e, finalmente, os padrões que você utiliza quando um servidor não é suficiente: alta disponibilidade e escalabilidade, além das realidades de hospedagem na nuvem.

Tudo o que é mostrado foi verificado em relação ao laboratório Asterisk 22 do livro em `lab/` — o mesmo contêiner que você tem construído ao longo do livro.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Executar o Asterisk 22 de forma confiável sob o systemd, como um usuário não root, com reinicialização automática
- Containerizar o Asterisk com Docker e entender as compensações de rede
- Manter `/etc/asterisk` sob controle de versão e fazer backup do estado correto
- Monitorar um sistema em execução através da CLI, CDR/CEL, AMI/ARI e métricas
- Aplicar padrões de alta disponibilidade ativo/standby e escalabilidade horizontal
- Hospedar o Asterisk na nuvem com segurança atrás de NAT e um firewall

## Executando o Asterisk sob o systemd

Em todas as distribuições Linux atuais — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — o gerenciador de serviços é o **systemd**. O capítulo de instalação mostrou que a etapa `make config` (executada durante `make install`) instala um script de inicialização da distribuição (`/etc/init.d/asterisk` no Debian, um script `rc.d` no RedHat), que o systemd então encapsula automaticamente como um serviço; o Asterisk também fornece uma unidade nativa do systemd em `contrib/systemd/asterisk.service` que você pode instalar em seu lugar para um controle mais refinado.
De qualquer forma, o systemd é a maneira suportada e recomendada para produção de executar o Asterisk. Consulte *Installing Asterisk 22* para a compilação em si; aqui focamos no que o serviço oferece a você e como operá-lo.

### A unidade de serviço e seu ciclo de vida

Uma vez que `make config` tenha instalado o serviço, o ciclo de vida é o padrão do systemd:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Algumas notas operacionais:

- **`restart` vs. um recarregamento gracioso.** `systemctl restart` encerra o processo e derruba todas as chamadas. Para alterações de configuração, você quase nunca quer isso — use a CLI do Asterisk: `asterisk -rx 'core reload'` (ou um recarregamento específico de módulo, como `pjsip reload`). Reserve `systemctl restart` para atualizações ou um processo travado.
- **Anexar ao daemon em execução.** Com o Asterisk rodando como um serviço, abra seu console com `asterisk -r` (ou `asterisk -rvvv` para saída detalhada). Isso se conecta ao daemon já em execução através de seu socket de controle; ele não inicia uma segunda cópia.

### `Restart=` substitui o safe_asterisk

Historicamente, o Asterisk era iniciado através do wrapper **safe_asterisk**, um script shell que reiniciava o Asterisk se ele travasse. Sob o systemd, essa tarefa pertence à diretiva `Restart=` da unidade — o systemd percebe a saída do processo e o traz de volta, com o atraso controlado por `RestartSec=` e proteção contra loop de falhas por `StartLimitIntervalSec=`/`StartLimitBurst=`. Portanto, em um host com systemd, o **safe_asterisk é substituído** e geralmente desnecessário. Se a sua unidade fornecida ainda não o define, uma substituição (drop-in) é a maneira limpa de adicionar reinicialização em caso de falha sem editar o arquivo empacotado:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Aplique-o com `systemctl daemon-reload && systemctl restart asterisk`. Usar um drop-in (em vez de editar a unidade instalada) significa que uma futura `make config` não sobrescreverá sua alteração.

### Executando como um usuário não root

O Asterisk não deve ser executado como root em produção — um bug de código remoto em um processo rodando como root é um comprometimento total do host, enquanto o mesmo bug em um processo sem privilégios é contido. Existem dois lugares complementares onde isso é aplicado:

- **A unidade / asterisk.conf.** A unidade empacotada normalmente executa o Asterisk como o usuário e grupo `asterisk`. Você também pode (ou em vez disso) definir `runuser` e `rungroup` na seção `[options]` do `asterisk.conf`, que o daemon honra quando descarta privilégios após a vinculação:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Propriedade de arquivo.** Os diretórios de tempo de execução devem ser graváveis por esse usuário. Após criar a conta, garanta a propriedade:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Como SIP (5060) e RTP (10000+) são portas altas, o Asterisk **não** precisa de root para vinculá-las — apenas portas privilegiadas estilo porta 25 precisariam, as quais o Asterisk não usa. Executar sem privilégios é, portanto, gratuito. (O capítulo de Segurança expande sobre por que isso é importante; veja *Asterisk Security*.)

## Containerizando o Asterisk

Um contêiner empacota o Asterisk e suas dependências exatas em uma imagem imutável, de modo que o que você testa é byte por byte o que você envia. A compensação é a mídia em tempo real: um servidor SIP é sensível à latência e precisa de uma faixa ampla e previsível de portas UDP acessíveis de fora, e a rede de contêineres pode atrapalhar. O restante desta seção percorre o próprio laboratório do livro — `lab/Dockerfile` e `lab/docker-compose.yml` — como um exemplo concreto e funcional, e então explica a armadilha em que todos caem: RTP e rede em ponte (bridged).

### A imagem: compilando o Asterisk a partir do código-fonte

O `Dockerfile` do laboratório compila o Asterisk 22 a partir do código-fonte no Debian 12. Vale a pena ler sua estrutura, mesmo que você nunca escreva uma sozinho:

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

- **A versão é fixada** (`ARG ASTERISK_VERSION=22.10.0`). A reprodutibilidade é o objetivo principal da containerização — altere-a deliberadamente, recompile, teste novamente.
- **`--with-pjproject-bundled` e `--with-jansson-bundled`** compilam a pilha SIP com a versão correspondente ao Asterisk, para que você dependa de menos pacotes apt e nunca precise lutar com um PJSIP da distribuição que esteja desatualizado.
- **`CMD ["asterisk", "-f", "-vvv"]`** executa o Asterisk em *primeiro plano* (`-f`, "não bifurcar"). Esta é a principal diferença de um host systemd: o processo principal de um contêiner não deve se tornar um daemon, ou o contêiner sairia imediatamente. Portanto, em um contêiner, você **não** usa a unidade do systemd — o tempo de execução do contêiner (Docker, mais a política `restart:`) torna-se o supervisor que a `Restart=` da unidade era em uma VM.

### Bind-mounting `/etc/asterisk`

A imagem deliberadamente não contém **nenhuma** configuração. Em vez disso, o `docker-compose.yml` monta o diretório de configuração do host:

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

`./asterisk/etc:/etc/asterisk:ro` mapeia o diretório `lab/asterisk/etc` sob controle de versão no `/etc/asterisk` do contêiner, somente leitura (`:ro`). A vantagem é grande: a imagem permanece imutável e reutilizável, enquanto a configuração reside no host, onde pode ser editada e, crucialmente, mantida no git (próxima seção). Para aplicar uma alteração de configuração, você edita o arquivo e recarrega — `docker compose exec asterisk asterisk -rx 'core reload'` — sem recompilar. `restart: unless-stopped` é o equivalente ao nível de compose da `Restart=` do systemd: o Docker reinicia o contêiner se o Asterisk sair, mas não se você o parou deliberadamente.

### Rede host vs. em ponte — o problema do RTP

Esta é a falha mais comum do Asterisk containerizado, por isso vale a pena entender com precisão. Por padrão, o Docker coloca um contêiner em uma rede **em ponte (bridged)** e você publica portas individuais com `ports:`. A sinalização funciona bem — 5060 é uma porta. O problema é a mídia: o RTP usa uma *faixa* de portas UDP (o `rtp.conf` do laboratório define `rtpstart=10000` / `rtpend=10100`), e **toda** porta que possa transportar áudio deve ser publicada.

O laboratório faz exatamente isso:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Observe que a faixa de publicação RTP (`10000-10100`) corresponde exatamente a `rtp.conf`. Se você errar isso — publicar poucas portas ou uma faixa diferente de `rtp.conf` — as chamadas conectam, mas têm **áudio unidirecional ou nenhum áudio**, porque os pacotes RTP chegam a uma porta que o Docker não está encaminhando. Duas precauções adicionais com o modo em ponte:

- **Publicar milhares de portas é lento e pesado.** Uma faixa RTP de produção é normalmente 10000–20000. O Docker criar ~10000 encaminhamentos de proxy em espaço de usuário é caro na inicialização e adiciona um salto no caminho da mídia. O laboratório mantém uma faixa deliberadamente pequena de 100 portas porque só executa uma ou duas chamadas de teste.
- **NAT no SDP.** Atrás da ponte, o Asterisk vê seu IP de contêiner privado e pode anunciá-lo no SDP. Em um host público, você deve informar ao PJSIP seu endereço externo com `external_media_address` / `external_signaling_address` no transporte (e definir `local_net`), exatamente como faria atrás de qualquer NAT — veja *Cloud hosting* abaixo.

A alternativa é a **rede host** (`network_mode: host`), que remove a ponte completamente: o contêiner compartilha a pilha de rede do host, portanto, a 5060 e toda a faixa RTP são acessíveis sem publicação de porta e sem salto de mídia extra. Este é o modo recomendado para um contêiner Asterisk real — ele evita completamente o problema da faixa RTP. Seu custo é o isolamento: o contêiner pode vincular qualquer porta do host e você perde a rede por serviço do compose. (A rede host é um recurso do Linux; no Docker Desktop para macOS/Windows, ele se comporta de maneira diferente, o que é parte do motivo pelo qual este laboratório de ensino usa portas publicadas explicitamente.)

### Volumes persistentes para spool e voicemail

A camada gravável de um contêiner é **efêmera** — destrua o contêiner e tudo o que ele escreveu desaparecerá. Para o Asterisk, isso significa que voicemail, gravações, o spool de chamadas de saída e o banco de dados local desapareceriam a cada `docker compose up --build`. A configuração sobrevive porque é montada a partir do host; o *estado* precisa do mesmo tratamento. Dentro do contêiner, as árvores relevantes são:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(O contêiner em execução do laboratório mostra exatamente estas — `/var/spool/asterisk` contém `voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` contém `astdb.sqlite3`.) Para preservá-los, monte volumes nomeados para os diretórios que contêm o estado com o qual você se importa:

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

O laboratório de ensino omite isso propositalmente — ele é sem estado e reprodutível por design, então cada `up` é um novo começo — mas um contêiner de produção **deve** tê-los, ou você perderá o voicemail na primeira reimplantação.

## Gerenciamento de configuração e backups

A montagem (bind-mount) acima sugere o modelo correto: trate `/etc/asterisk` como **código** e o restante como **dados**.

### Mantenha `/etc/asterisk` sob controle de versão

O diretório de configuração é um conjunto simples de arquivos de texto sem segredos que não possam ser modelados — é ideal para o git. Inicialize um repositório em `/etc/asterisk` (ou, como o laboratório faz, mantenha a configuração junto ao projeto e monte-a). Benefícios:

- Cada alteração é revisável e reversível (`git diff`, `git revert`).
- Você tem uma trilha de auditoria de quem mudou o quê e quando.
- Combinado com uma imagem de contêiner, um commit de configuração conhecido como bom mais uma tag de imagem fixada descreve totalmente uma implantação.

Algumas precauções específicas para a configuração do Asterisk:

- **Segredos.** `pjsip.conf` (e `manager.conf`, `ari.conf`) contêm senhas. Não envie segredos reais para um repositório compartilhado em texto simples — modele-os (um arquivo por ambiente, ou um gerenciador de segredos / substituição de ambiente no momento da implantação) e mantenha apenas espaços reservados no git. As senhas triviais estilo `Lab-6001-secret` do laboratório são aceitáveis *apenas* porque vivem em uma sub-rede Docker privada.
- **Modelagem por ambiente.** Os valores de tempo real que diferem entre desenvolvimento, homologação e produção (endereços de vinculação, IPs externos, credenciais de tronco, URLs de banco de dados) são exatamente as linhas que você modela, mantendo a maior parte da configuração idêntica entre os ambientes.

### O que fazer backup

A configuração no git cobre o dialplan e os endpoints, mas um PBX ativo acumula *estado* que não está em nenhum arquivo de configuração. Um backup completo é:

| O que | Onde | Por que |
|------|-------|-----|
| Configuração | `/etc/asterisk/` | dialplan, endpoints (também no git) |
| Voicemail & gravações | `/var/spool/asterisk/` | dados do usuário — insubstituíveis |
| Banco de dados interno | `/var/lib/asterisk/astdb.sqlite3` | chaves `DB()`, estado do dispositivo |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` ou armazenamento SQL | faturamento & histórico |
| Bancos de dados externos | seu MySQL/PostgreSQL | tempo real, CDR, voicemail |

O **astdb** merece uma nota: é o pequeno armazenamento de chave/valor embutido do Asterisk (um arquivo SQLite em `/var/lib/asterisk/astdb.sqlite3`) usado pelas funções de dialplan `DB()`, estados de dispositivo, configurações de siga-me e similares. Você pode despejá-lo para inspeção ou backup a partir da CLI:

```
asterisk -rx 'database show'
```

Se o seu CDR/CEL ou voicemail ou configuração PJSIP residir em um banco de dados externo (veja *Asterisk Real-Time* e *Asterisk Call Detail Records*), esse banco de dados agora é a fonte da verdade para esses dados e deve estar na sua rotação normal de backup de banco de dados — fazer backup apenas de `/etc/asterisk` não é suficiente.

## Monitoramento e observabilidade

Você não pode operar o que não pode ver. O Asterisk expõe seu estado em quatro níveis, desde um rápido olhar humano até um pipeline de métricas: a **CLI**, os registros **CDR/CEL**, eventos **AMI/ARI** e **exportadores de métricas**.

### Verificações de integridade da CLI

A verificação mais rápida de "está saudável?" é a CLI. Os comandos abaixo são executados ao vivo contra o laboratório. Canais primeiro:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` em um sistema silencioso é normal; em um sistema ocupado, esta é sua simultaneidade em tempo real. `core show uptime` confirma que o processo não foi reiniciado sob você:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Para a saúde SIP, `pjsip show endpoints` mostra cada endpoint e se seus contatos registrados são alcançáveis. Do laboratório:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` aqui simplesmente significa que nenhum telefone está registrado atualmente nesses endpoints (o laboratório não tem clientes ativos) — assim que um softphone se registra e `qualify` confirma, o estado mostra o contato como alcançável. Comandos complementares: `pjsip show contacts` (registros atuais e tempo de ida e volta), `pjsip show transports` e `pjsip show aor <name>` para um AOR. Estas são as ferramentas do dia a dia "por que a extensão X não pode ser alcançada?".

### CDR e CEL

Cada chamada deixa um **Call Detail Record** (CDR); o **Channel Event Logging** (CEL) adiciona eventos mais refinados por canal. Confirme se o CDR está ativo e qual backend o armazena:

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

O laboratório mostra `(none)` em backends registrados porque a configuração mínima do laboratório não carrega nenhum módulo de armazenamento CDR — então os registros são calculados, mas não gravados em lugar nenhum. Em produção, você carrega um backend (CSV, ou `cdr_odbc`/`cdr_adaptive_odbc` em MySQL/PostgreSQL) e isso se torna sua fonte de faturamento e histórico. O CEL é **desativado por padrão** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` apenas quando você precisa de detalhes em nível de evento. Ambos são abordados em profundidade em *Asterisk Call Detail Records*; para monitoramento, o ponto é que CDR/CEL são seu registro *histórico*, onde a CLI é sua visão *ao vivo*.

### Eventos AMI e ARI

Para monitoramento programático em tempo real, você deseja um feed de eventos em vez de consultar a CLI:

- **AMI (Asterisk Manager Interface)** é o protocolo de eventos/comandos TCP de longa data (`manager.conf`). Inscreva-se e você receberá `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` e eventos similares à medida que as chamadas acontecem — a espinha dorsal de painéis e ferramentas de contabilidade de chamadas. No laboratório, o AMI é desativado por padrão (`manager show settings` relata `Manager (AMI): No`); você o ativa e bloqueia em `manager.conf`.
- **ARI (Asterisk REST Interface)** é a interface moderna HTTP + WebSocket (`ari.conf`, servida pelo servidor HTTP embutido). Ele fornece um fluxo de eventos JSON e controle de chamadas refinado — a escolha certa para novas integrações.

Ambos são detalhados em *Extending Asterisk with AMI and AGI* e *The Asterisk REST Interface (ARI)*. O aviso relevante para a implantação: **AMI e ARI são poderosos e nunca devem ser expostos à internet.** Vincule o servidor HTTP ao localhost ou a uma rede de gerenciamento, use segredos únicos fortes e proteja as portas com firewall — veja *Asterisk Security*.

### Métricas: Prometheus e Grafana

Para painéis e alertas, o Asterisk 22 fornece um exportador Prometheus, **`res_prometheus.so`** (um módulo com nível de suporte *estendido*), que expõe métricas em um endpoint HTTP que um servidor Prometheus coleta. Juntamente com as métricas principais do processo, ele fornece provedores conectáveis cobrindo canais, chamadas, endpoints, pontes e registros de saída PJSIP:

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

Você pode confirmar que o módulo está presente na compilação do laboratório:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

Ele mostra `Not Running` porque o laboratório não o configura ou carrega; ativá-lo (`prometheus.conf` mais o servidor HTTP) transforma o Asterisk em um alvo do Prometheus. Aponte o Prometheus para o endpoint de coleta e o Grafana para o Prometheus, e você obtém painéis de séries temporais (chamadas simultâneas, registros, tendências de ASR/ACD) e alertas (por exemplo, "chamadas ativas caíram para zero" ou "picos de falhas de registro"). Para equipes que já executam Prometheus/Grafana, esta é a maneira natural de integrar o Asterisk à observabilidade existente, em vez de analisar a saída da CLI.

### Códigos de resposta SIP que vale a pena observar

Qualquer que seja o pipeline, alguns resultados SIP sinalizam problemas e valem a pena criar alertas: falhas de desafio `401`/`407` sustentadas ou `403 Forbidden` sugerem um ataque de força bruta ou uma tempestade de credenciais mal configuradas (consulte Fail2Ban em *Asterisk Security*); `503 Service Unavailable` aponta para um servidor ou tronco sobrecarregado ou congestionado; e um pico em `408 Request Timeout`/`480 Temporarily Unavailable` geralmente significa que os endpoints ficaram inalcançáveis (timeout de NAT, falhas de qualificação).

## Alta disponibilidade e escalabilidade

Um servidor Asterisk é um ponto único de falha e tem um limite finito de chamadas. Os dois problemas — *permanecer ativo* e *crescer* — têm respostas diferentes.

### Ativo/standby com um IP flutuante

O padrão de HA clássico e bem trilhado para o Asterisk é **ativo/standby** (não ativo/ativo — o estado da chamada no Asterisk é difícil de compartilhar ao vivo). Dois servidores idênticos, um ativo, um standby, compartilham um **IP flutuante (virtual)** gerenciado por um gerenciador de cluster como **keepalived** (VRRP) ou **Pacemaker/Corosync**. Telefones e troncos registram-se no IP flutuante, não em nenhum dos hosts reais. Se o nó ativo falhar em sua verificação de integridade, o IP flutuante move-se para o standby, que assume o controle.

A ressalva honesta: um failover de IP **derruba chamadas em andamento** — o Asterisk não replica o estado do canal ao vivo entre os nós, então qualquer pessoa no meio de uma chamada deve rediscar. Os registros restabelecem-se dentro de um ciclo de qualificação/registro. O que o failover lhe proporciona é que o *serviço* se recupera em segundos sem intervenção manual, o que para a maioria dos PBXs é exatamente o objetivo. Para tornar o standby genuinamente capaz de assumir, ambos os nós precisam da mesma configuração (seu `/etc/asterisk` no git, implantado de forma idêntica) e o mesmo *estado* — que é o próximo ponto.

### Externalizar estado com PJSIP Realtime

O ativo/standby só funciona se o standby souber dos mesmos endpoints e registros que o nó ativo. A maneira de conseguir isso é **parar de manter o estado em arquivos simples em uma caixa** e movê-lo para um banco de dados compartilhado que ambos os nós leem. O **PJSIP Realtime** (Sorcery apoiado por um banco de dados) faz exatamente isso: endpoints, AORs, autenticações — e, importantemente, **registros** (a tabela `ps_contacts`) — vivem em MySQL/PostgreSQL em vez de `pjsip.conf` e memória local. Ambos os nós do Asterisk apontam para o mesmo banco de dados, então um telefone registrado através de um nó é visível para o outro. Isso é abordado em *Asterisk Real-Time* (a seção PJSIP Realtime / Sorcery); aqui, o ponto de implantação é que **externalizar o estado é o pré-requisito tanto para HA quanto para escalabilidade horizontal** — sem isso, cada nó é uma ilha.

Aplique a mesma lógica ao restante do seu estado: CDR/CEL em um armazenamento SQL compartilhado, voicemail em armazenamento compartilhado/replicado (ou `ODBC_STORAGE`) e as chaves astdb das quais você depende em um banco de dados. Uma vez que o estado é externo, os nós do Asterisk tornam-se mais próximos de front-ends intercambiáveis.

### Proxies SIP na frente (OpenSIPS)

Para escalar *além* da capacidade de um servidor, você coloca um **proxy SIP/balanceador de carga** na frente de um pool de servidores de mídia Asterisk. O **OpenSIPS** é um proxy SIP construído para esse fim, de altíssimo rendimento (eles lidam com centenas de milhares de registros e roteiam a sinalização sem tocar na mídia). O proxy apresenta um único endereço SIP ao mundo, mantém o serviço de registro/localização e distribui chamadas entre os back-ends do Asterisk. Essa separação — uma camada de proxy leve fazendo registro e roteamento, uma camada de Asterisk escalável horizontalmente fazendo o processamento real de chamadas (IVR, filas, conferências, transcodificação) — é como grandes implantações crescem além de uma única caixa. (A própria plataforma SipPulse usa o OpenSIPS na frente de seus servidores de mídia/aplicação exatamente por esse motivo.)

### Escalabilidade de mídia

O proxy distribui a *sinalização* de forma barata; **a mídia é o recurso caro**. O retransmissor RTP, e especialmente a transcodificação entre codecs (por exemplo, Opus ↔ G.711) ou a execução de grandes conferências, é limitado pela CPU e é o que realmente limita um servidor. Estratégias:

- **Evite a transcodificação** sempre que possível — negocie um codec comum de ponta a ponta para que o Asterisk faça a ponte nativamente (pass-through) em vez de transcodificar. Esta é a maior vitória de capacidade de mídia.
- **Escale a mídia horizontalmente** adicionando nós Asterisk atrás do proxy; cada um carrega uma parte das chamadas simultâneas.
- **Descarregue a mídia do navegador** para um gateway WebRTC dedicado (por exemplo, Janus) para que o PBX também não esteja terminando e retransmitindo o fluxo DTLS-SRTP de cada navegador — veja *WebRTC with Asterisk*, que discute exatamente essa divisão Asterisk-mais-gateway.

Dimensione a capacidade por **chamadas simultâneas e carga de transcodificação**, não por usuários registrados — 10.000 telefones registrados que estão quase todos ociosos são muito mais baratos do que 200 conferências transcodificadas simultâneas.

## Hospedagem na nuvem

Executar o Asterisk em uma VM na nuvem (AWS, GCP, Azure, um VPS) é comum e funciona bem, mas a rede na nuvem é **NAT'd e protegida por firewall por padrão**, o que entra em conflito com o SIP. As seguintes são as preocupações específicas da implantação.

### NAT e o SDP

Uma VM na nuvem quase sempre tem um IP **privado** em sua NIC e um IP **público** separado que o provedor NAT para ela. Se o Asterisk anunciar o IP privado no SDP, os telefones remotos enviam RTP para um buraco negro — o sintoma clássico de áudio unidirecional/nenhum áudio. Informe ao PJSIP sua identidade pública no transporte:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` faz o Asterisk reescrever o endereço que ele anuncia para pares públicos, enquanto `local_net` informa quais pares são locais (e *não* devem ser reescritos). Este é o mesmo tratamento de NAT discutido para a rede Docker em ponte acima — uma VM na nuvem está, na verdade, atrás de NAT.

### Firewall e a faixa RTP

Dois firewalls geralmente se aplicam em uma VM na nuvem: o grupo de segurança / ACL de rede do **provedor** e o iptables do **host**. Ambos devem abrir as mesmas portas, e a política é a do capítulo de Segurança. O conjunto de regras da 1ª edição recuperado (`docs/legacy-labs/configs/Lab7/rules.v4`) captura a forma — aceite SIP e a faixa RTP, aceite estabelecido/relacionado, descarte o resto:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Duas correções que o capítulo de Segurança faz e que importam aqui: abra a **5061 em TCP** (não UDP) se você executar SIP/TLS, e lembre-se de que a faixa UDP RTP em seu firewall deve corresponder exatamente a `rtpstart`/`rtpend` em `rtp.conf` — a mesma faixa que você publica em um contêiner. Não duplique a compilação do iptables/Fail2Ban aqui; **siga as seções de firewall, Fail2Ban e TLS/SRTP do *Asterisk Security*** (o Fail2Ban monitora o canal de log `security` que o laboratório já ativa em `logger.conf`) e aplique essa política tanto no firewall do host quanto no grupo de segurança da nuvem.

### Latência, região e o SBC

- **Escolha uma região próxima aos seus usuários.** A voz é sensível à latência — uma latência de boca a ouvido unidirecional acima de ~150 ms é perceptível. Hospede a VM na região mais próxima da maioria dos seus telefones e troncos; a mídia transcontinental é audivelmente pior.
- **Coloque um SBC na frente para qualquer implantação voltada para a internet.** Um **Session Border Controller** termina SIP/RTP na borda, oculta sua topologia, normaliza o NAT e absorve o tráfego de DoS e varredura antes que ele chegue ao Asterisk. A recomendação principal do capítulo de Segurança — *não exponha o Asterisk bruto à internet* — aplica-se duplamente na nuvem, onde o IP público da sua VM está sendo varrido minutos após subir. Um SBC (ou, no mínimo, um proxy SIP endurecido como o OpenSIPS mais Fail2Ban) é a borda padrão.

## Resumo

A implantação é onde um dialplan funcional se torna um serviço confiável. Em uma VM, execute o Asterisk sob o **systemd** como um usuário **não root**, deixando a `Restart=` da unidade mantê-lo vivo (o safe_asterisk foi substituído) e usando `core reload` em vez de `systemctl restart` para alterações de configuração. **Containerizar** com o Docker — como o laboratório do livro faz — oferece uma imagem imutável e fixada com configuração **montada (bind-mounted)** a partir de um `/etc/asterisk` no git; o problema é a mídia, então use **rede host** ou publique uma faixa de porta RTP que **corresponda exatamente a `rtp.conf`**, e monte **volumes persistentes** para spool/voicemail/astdb para que o estado sobreviva a uma reimplantação. Trate a configuração como código e **faça backup do estado** que a configuração não captura: voicemail, gravações, `astdb.sqlite3` e CDR/CEL. **Observe** o sistema em quatro níveis — a CLI (`core show channels`, `pjsip show endpoints`) para a visão ao vivo, **CDR/CEL** para histórico, **AMI/ARI** para eventos programáticos e o exportador **`res_prometheus`** para o Grafana para painéis e alertas — mantendo o AMI/ARI fora da internet pública. Para **permanecer ativo**, execute ativo/standby com um **IP flutuante** (aceitando que o failover derruba chamadas ao vivo); para **crescer**, externalize o estado com **PJSIP Realtime**, coloque um pool de servidores de mídia na frente com **OpenSIPS** e minimize a transcodificação, porque **a mídia — não os registros — é o que limita um servidor**. Finalmente, na **nuvem**, trate a VM como estando atrás de NAT (`external_media_address`, `local_net`), abra o firewall conforme o capítulo de Segurança tanto no host quanto no grupo de segurança do provedor, escolha uma região de baixa latência e nunca exponha o Asterisk bruto — coloque um **SBC** na borda.

## Quiz

1. Em um host systemd, o que substitui o trabalho do antigo wrapper `safe_asterisk` de reiniciar um Asterisk travado?
   - A. Um cron job
   - B. A diretiva `Restart=` do arquivo de unidade
   - C. `systemctl enable`
   - D. O astdb
2. Para aplicar uma alteração de configuração a um Asterisk em execução **sem derrubar chamadas**, você deve:
   - A. `systemctl restart asterisk`
   - B. Reiniciar o servidor
   - C. `asterisk -rx 'core reload'`
   - D. Recompilar a imagem do contêiner
3. Um Asterisk containerizado (rede em ponte) conecta chamadas, mas **não tem áudio**. A causa mais provável é:
   - A. O dialplan está errado
   - B. A faixa de porta UDP RTP publicada não corresponde a `rtpstart`/`rtpend` em `rtp.conf`
   - C. O CDR está desativado
   - D. A CLI está inalcançável
4. Quais diretórios devem ser montados como **volumes persistentes** para que uma reimplantação de contêiner não perca o estado? (marque todas as que se aplicam)
   - A. `/var/spool/asterisk` (voicemail, gravações)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (já montado a partir do host)
   - D. `/usr/sbin`
5. Qual comando da CLI fornece a contagem ao vivo de chamadas ativas?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. No Asterisk 22, a maneira suportada de expor métricas de chamada/canal para uma pilha Prometheus/Grafana é:
   - A. Analisar o arquivo de log `full`
   - B. O módulo `res_prometheus.so`
   - C. Scripts AGI
   - D. Não existe
7. Qual é o pré-requisito tanto para failover de HA quanto para escalabilidade horizontal em vários nós Asterisk?
   - A. Executar como root
   - B. Externalizar o estado (por exemplo, registros PJSIP Realtime em um banco de dados compartilhado)
   - C. Desativar o CDR
   - D. Usar rede em ponte
8. Qual recurso limita mais diretamente quantas chamadas simultâneas um servidor Asterisk pode manipular?
   - A. O número de usuários registrados
   - B. Processamento de mídia, especialmente transcodificação
   - C. O tamanho de `/etc/asterisk`
   - D. O backend CDR
9. Em uma VM na nuvem, quais configurações de transporte `pjsip.conf` fazem o Asterisk anunciar seu endereço público para que o áudio remoto funcione? (marque todas as que se aplicam)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Para uma implantação na nuvem voltada para a internet, a regra principal do capítulo de Segurança é:
    - A. Sempre execute duas NICs
    - B. Nunca exponha o Asterisk bruto à internet; coloque um SBC (ou proxy endurecido + Fail2Ban) na borda
    - C. Use apenas UDP
    - D. Desative o TLS

**Respostas:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
