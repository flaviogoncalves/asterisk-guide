# Migrando de chan_sip para PJSIP: um guia prático

Se você está lendo isto com um servidor Asterisk 13, 16 ou 18 ainda em produção, você tem um prazo. `chan_sip` — o driver de canal SIP original configurado através de `sip.conf` — foi **descontinuado no Asterisk 17, removido da compilação padrão no Asterisk 19 e excluído inteiramente no Asterisk 21**. Ele não existe no Asterisk 22 LTS. Não há sinalizador para reativá-lo, não há `noload` para contornar, nem pacote para instalar. O único driver de canal SIP no Asterisk 22 é o **PJSIP** (`res_pjsip` mais `chan_pjsip`), configurado através de `pjsip.conf`.

Portanto, uma atualização para o Asterisk 22 é, para a maioria dos locais, um *projeto de migração SIP* tanto quanto uma atualização de versão. A boa notícia é que o protocolo na rede não muda — um telefone que se registrou e fez chamadas ontem se registrará e fará chamadas amanhã — e o Asterisk fornece uma ferramenta de conversão para fazer os primeiros 80% da tradução para você. Este capítulo é um guia prático: o mapeamento de conceitos, o script de conversão, traduções lado a lado de `sip.conf` → `pjsip.conf` para os casos que você realmente possui, as mudanças no dialplan e na CLI que acompanham a mudança, migração de realtime (banco de dados), e uma lista de verificação, além das armadilhas que costumam afetar as pessoas.

Tudo aqui foi verificado no laboratório Asterisk 22.10.0 deste livro. O material legado profundo sobre o próprio `chan_sip` — e uma conversão completa de ponta a ponta de um `sip.conf` com múltiplos dispositivos — reside no capítulo *Legacy channels*; este capítulo é o companheiro focado, em estilo de receita, para ele.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Explicar por que o `chan_sip` desapareceu no Asterisk 22 e o que o substitui
- Mapear o modelo peer/user/friend do `sip.conf` para o modelo de objetos PJSIP (endpoint + aor + auth + identify + transport + registration)
- Executar o script de conversão `sip_to_pjsip.py` e revisar seu resultado criticamente
- Traduzir manualmente os tipos de dispositivos comuns (telefone com registro, trunk de entrada, registro de saída) de `sip.conf` para `pjsip.conf`
- Migrar configurações de NAT, mídia, DTMF, codec e autenticação opção por opção
- Atualizar o dialplan (`SIP/` → `PJSIP/`) e a CLI (`sip show` → `pjsip show`)
- Migrar uma implementação realtime/ARA de `sippeers`/`sipregs` para as tabelas Sorcery `ps_*`
- Trabalhar com uma lista de verificação de migração e evitar as armadilhas clássicas

## Por que migrar?

O `chan_sip` serviu ao Asterisk por quase duas décadas, mas carregava dívidas arquiteturais: um módulo monolítico, um único bloco de configuração por dispositivo, suporte fraco a múltiplos transportes e uma pilha SIP que havia ficado atrás das RFCs. O **PJSIP** — construído sobre a pilha madura pjproject da Teluu e introduzido no Asterisk 12 — foi a substituição feita do zero. No Asterisk 21, o projeto Asterisk terminou o trabalho e removeu o `chan_sip` da árvore.

Você pode confirmar a situação em qualquer sistema Asterisk 22:

```
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

O `chan_sip` retorna *0 modules loaded* — ele simplesmente não está lá. Não há nada para onde migrar, exceto PJSIP, então a única pergunta real é *como*, não *se*.

## O mapeamento conceitual: não existe um "peer" único

A mudança mental que atrapalha todos que vêm do `sip.conf` é esta: **o PJSIP não possui `[peer]`.** No `sip.conf`, um bloco entre colchetes — um `peer`, um `user` ou um `friend` — descrevia *tudo* sobre um dispositivo: suas credenciais, onde alcançá-lo, seus codecs, seu comportamento de NAT, seu contexto de dialplan. O PJSIP divide deliberadamente esse bloco único em vários objetos menores e de propósito único, cada um marcado com um `type=`, que *referenciam uns aos outros pelo nome*:

| Objeto PJSIP (`type=`) | Responsabilidade |
| --- | --- |
| `endpoint` | A identidade de tratamento de chamadas do dispositivo: codecs, context, DTMF, mídia, NAT e referências aos seus `auth`/`aors`/`transport` |
| `aor` (Address of Record) | *Onde* alcançar o dispositivo — contatos registrados ou estáticos, `max_contacts`, qualify |
| `auth` | Credenciais (nome de usuário/senha) para autenticação de entrada e/ou saída |
| `identify` | Corresponder uma solicitação de entrada a um endpoint pelo **IP de origem** em vez do usuário `From` |
| `transport` | O(s) socket(s) de escuta: protocolo, endereço/porta de bind, endereços NAT/externos |
| `registration` | Um REGISTER de **saída** do Asterisk para um provedor |

A distinção `friend`/`peer`/`user` desaparece inteiramente — no PJSIP, tudo é um `endpoint`. Um único friend `sip.conf` torna-se, portanto, tipicamente três objetos (`endpoint` + `auth` + `aor`) que compartilham um nome e apontam um para o outro:

```
                sip.conf                              pjsip.conf
            ┌──────────────┐              ┌──────────┐   ┌──────┐   ┌─────┐
            │   [2000]     │   becomes    │ endpoint │──▶│ auth │   │ aor │
            │ type=friend  │  ─────────▶  │  [2000]  │   │[2000]│   │[2000]│
            │ host=dynamic │              │  auth=───┼──▶└──────┘   └──────┘
            │ secret=...   │              │  aors=───┼───────────────▶ ▲
            └──────────────┘              └────┬─────┘
                                               │ transport=
                                               ▼
                                          ┌───────────┐
                                          │ transport │  (shared by all endpoints)
                                          └───────────┘
```

O endpoint é a cola. Ele nomeia um `transport` (ou herda o padrão), um objeto `auth` e um ou mais `aors`. O modelo de objetos é abordado em profundidade em *SIP & PJSIP in depth*; aqui, precisamos dele apenas como o alvo de cada tradução.

## A ferramenta de conversão `sip_to_pjsip.py`

O Asterisk fornece um script Python que lê um `sip.conf` existente e escreve um `pjsip.conf`. Ele não é executado como um comando CLI — ele reside na **árvore de fontes do Asterisk**, não nos binários instalados:

```
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

No Asterisk 22.10.0 do laboratório, o caminho completo é, por exemplo, `/usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py`. O mesmo diretório contém o `sip_to_pjsql.py` (a variante realtime/SQL, abordada posteriormente) e os módulos auxiliares `astconfigparser.py`, `astdicts.py` e `sqlconfigparser.py`.

### Executando o script

O script aceita argumentos posicionais opcionais — `[input-file [output-file]]` — assumindo como padrão `sip.conf` e `pjsip.conf` no diretório atual:

```
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

Suas únicas opções reais são:

```
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

Ele lê a entrada, imprime `Converting to PJSIP...` e escreve o arquivo de saída. Internamente, ele percorre cada seção `sip.conf` e, por dispositivo, emite os objetos correspondentes `endpoint`, `auth`, `aor`, `registration` e (onde pode inferi-los) `transport`, aplicando automaticamente os mapeamentos de opções da próxima seção.

### O que ele faz — e seus limites

Trate a saída como um **primeiro rascunho, não um arquivo finalizado.** O script é honesto sobre suas próprias lacunas: tudo o que ele não consegue mapear claramente é escrito em um bloco claramente delimitado no topo do arquivo de saída:

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[softphone]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

Observe nesse fragmento real que o `qualify = yes` de um peer `sip.conf` caiu no bloco *não mapeado* — porque o PJSIP qualifica no **aor** com `qualify_frequency` (segundos), não um booleano no dispositivo, o script deixa para você definir deliberadamente. As limitações práticas para planejar são:

- **Transportes são adivinhados, não projetados.** O script emite um `transport-udp` básico de `bindport`/`bindaddr`, mas ele não pode saber seus certificados TLS, suas necessidades de TCP ou seu layout de múltiplos binds. Revise e reescreva o transporte.
- **NAT e endereços externos precisam de um humano.** `externaddr`/`localnet` podem não sobreviver limpos; confirme `external_media_address`, `external_signaling_address` e `local_net` no transporte manualmente.
- **`qualify`, timers personalizados e um punhado de opções caem em "não mapeado".** Leia esse bloco de cima a baixo e decida cada um.
- **Listas de codecs, contextos e segurança precisam de revisão.** Verifique `disallow`/`allow`, o dialplan `context` e certifique-se de que nenhum dispositivo foi deixado aberto sem intenção.

O fluxo de trabalho é, portanto: execute o script em um arquivo *temporário*, compare e revise-o, incorpore as partes boas no seu `pjsip.conf` real e, em seguida, teste exaustivamente antes da produção.

## Traduções lado a lado

Estas são as receitas. `sip.conf` à esquerda, o equivalente verificado `pjsip.conf` à direita (empilhados aqui para largura da página). Cada nome e valor de opção à direita foi verificado no laboratório Asterisk 22 com `config show help res_pjsip ...`.

### Um telefone com registro (`host=dynamic`)

O dispositivo mais comum: um telefone de mesa ou softphone que faz login com um segredo e registra sua própria localização.

**Legado `sip.conf`:**

```
[2000]
type=friend
host=dynamic
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmfmode=rfc2833
secret=Sup3rSecret
qualify=yes
```

**Asterisk 22 `pjsip.conf`:**

```
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
auth=2000
aors=2000

[2000]
type=auth
auth_type=digest
username=2000
password=Sup3rSecret

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

Principais movimentos: `host=dynamic` torna-se um `aor` com `max_contacts` (o dispositivo faz REGISTER para preencher seu contato); `secret=` torna-se `password=` dentro de um `type=auth`; `qualify=yes` torna-se `qualify_frequency=60` (segundos) no **aor**, não no endpoint. Defina `max_contacts` acima de 1 apenas se você realmente quiser a mesma conta em vários dispositivos ao mesmo tempo.

### Um trunk de entrada (`host=<ip>` / `type=peer`)

Um provedor que envia chamadas para você a partir de um endereço IP conhecido. Não há registro aqui — você autentica o *tráfego da operadora pelo seu IP de origem* usando `identify`.

**Legado `sip.conf`:**

```
[itsp-in]
type=peer
host=203.0.113.10
context=from-pstn
disallow=all
allow=ulaw
insecure=invite
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp-in]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw

[itsp-in]
type=aor
contact=sip:203.0.113.10:5060

[itsp-in]
type=identify
endpoint=itsp-in
match=203.0.113.10
```

A tradução crucial é **`insecure=invite` → `identify`**. No `chan_sip`, o `insecure=invite` dizia ao Asterisk "não desafie INVITEs de entrada deste peer para autenticação". O PJSIP alcança o mesmo efeito *correspondendo o IP de origem ao endpoint* com `type=identify`/`match=`, o que é mais explícito e mais seguro. O `host=` estático torna-se um `contact=` permanente no `aor` para que você também possa discar *para fora* para a operadora. O `match=` aceita um IP, uma faixa CIDR ou um nome de host (resolvido no momento do carregamento da configuração — recarregue se o IP do provedor mudar).

### Um registro de saída (`register =>`)

Quando o provedor quer que *você* faça login neles, o `chan_sip` usava uma única linha `register =>` em `[general]`. O PJSIP a substitui por um objeto `type=registration` dedicado mais um `outbound_auth`.

**Legado `sip.conf`:**

```
[general]
register => 1020:supersecret@sip.example.com:5600/9999

[itsp]
type=peer
host=sip.example.com
port=5600
defaultuser=1020
secret=supersecret
fromuser=1020
fromdomain=sip.example.com
context=from-pstn
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
outbound_auth=itsp-auth
aors=itsp-aor
from_user=1020
from_domain=sip.example.com

[itsp-auth]
type=auth
auth_type=digest
username=1020
password=supersecret

[itsp-aor]
type=aor
contact=sip:sip.example.com:5600

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:sip.example.com:5600
client_uri=sip:1020@sip.example.com:5600
contact_user=9999
retry_interval=60
```

Mapeie os campos `register =>` um a um: as credenciais `1020:supersecret` tornam-se o objeto `auth` (referenciado como `outbound_auth`); `@sip.example.com:5600` torna-se o `server_uri`; o sufixo `/9999` — a parte do usuário para a qual o provedor entrega chamadas de entrada — torna-se `contact_user=9999`. `defaultuser`/`fromuser` e `fromdomain` tornam-se `from_user` e `from_domain` no endpoint. Observe que o `outbound_auth` aparece *duas vezes*: o registro o usa para o REGISTER, o endpoint o usa para responder ao desafio `407` em INVITEs de saída.

## Referência de migração opção por opção

Quando você estiver traduzindo manualmente (ou auditando a saída do script), esta tabela é a referência. Cada nome de opção PJSIP e o posicionamento (endpoint / aor / auth / transport) foi verificado no laboratório Asterisk 22.

| Legado `sip.conf` | Asterisk 22 `pjsip.conf` | Onde |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (dispositivo faz REGISTER) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `username=` / `defaultuser=` | `username=` | auth |
| `secret=` (método de auth) | `auth_type=digest` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `disallow=` / `allow=` | `disallow=` / `allow=` (mesma sintaxe) | endpoint |
| `context=` | `context=` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | omitir auth; use `type=identify` + `match=` | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

### Uma nota sobre `secret` → `auth` e `auth_type`

O `secret=` do `chan_sip` torna-se o campo `password=` de um objeto `type=auth`. O **método de autenticação** é definido com `auth_type`. Use `auth_type=digest`. Os valores mais antigos `userpass` e `md5` ainda funcionam, mas estão **descontinuados e convertidos silenciosamente para `digest`** — verificado diretamente do laboratório:

```
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

Você verá `auth_type=userpass` em configurações mais antigas e na saída do script de conversão (e em capítulos anteriores deste livro). É inofensivo, mas escreva `digest` em qualquer coisa nova.

### NAT, mídia e DTMF em detalhes

Estes três são a origem da maioria dos chamados pós-migração do tipo "ele registra, mas não tem áudio". O atalho `nat=force_rport,comedia` do `chan_sip` agrupava três comportamentos em uma opção; o PJSIP os divide para que você possa raciocinar sobre cada um:

```
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

Para **mídia**, `directmedia` torna-se `direct_media` (o sublinhado é toda a mudança); mantenha `direct_media=no` sempre que a chamada precisar ser ancorada no Asterisk — através de NAT, ou para gravar/transcodificar/transferir. Para **DTMF**, a RFC foi renumerada: o `dtmfmode=rfc2833` do `chan_sip` é o `dtmf_mode=rfc4733` do PJSIP (mesmo mecanismo de telephone-event fora de banda, número de RFC atual). O laboratório confirma que os valores válidos de `dtmf_mode` são `rfc4733`, `inband`, `info`, `auto` e `auto_info`, com padrão em `rfc4733`.

Para **codecs**, nada muda: `disallow=all` seguido por `allow=ulaw` (etc.) usa a sintaxe idêntica no endpoint PJSIP.

## Mudanças no dialplan e na CLI

A migração não para no `pjsip.conf`. Duas coisas de uso diário mudam.

### Strings de canal: `SIP/` → `PJSIP/`

Cada `Dial()` e referência de canal no `extensions.conf` que nomeava a tecnologia antiga deve ser atualizado:

```
; Before (chan_sip)
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

Strings de discagem de trunk seguem o mesmo padrão — `Dial(SIP/${EXTEN}@itsp)` torna-se `Dial(PJSIP/${EXTEN}@itsp)`. O PJSIP também adiciona a função `PJSIP_DIAL_CONTACTS()` para chamar todos os contatos vinculados a um AOR de uma vez, e as funções de dialplan `PJSIP_HEADER()` / `PJSIP_MEDIA_OFFER()`; procure no seu dialplan por referências SIP `SIP/`, `SIPPEER`, `SIPCHANINFO` e `CHANNEL(...)` e traduza cada uma.

### CLI: `sip show ...` → `pjsip show ...`

Toda a árvore de comandos `sip ...` desaparece com o driver. As substituições:

| Comando `chan_sip` | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (ou `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (ou `core reload`) |

Os comandos antigos não apenas se comportam de forma diferente — eles não existem mais. No laboratório, `sip show peers` retorna *No such command*, enquanto `pjsip show endpoints`, `pjsip show aors`, `pjsip show auths`, `pjsip show contacts`, `pjsip show registrations` e `pjsip show identifies` estão todos presentes. O comando de solução de problemas mais útil — o logger de pacotes SIP que imprimia cada mensagem com `sip set debug` — agora é **`pjsip set logger on`** (com `pjsip set logger host <ip>` para focar em um peer).

## Migração Realtime (ARA)

Se você executava o `chan_sip` a partir de um banco de dados (Asterisk Realtime Architecture), seus dispositivos viviam na tabela `sippeers` e os registros na `sipregs`. O PJSIP usa uma camada de armazenamento completamente diferente — **Sorcery** — com uma tabela *por tipo de objeto*. O mapeamento:

| Tabela realtime `chan_sip` | Tabela(s) PJSIP / Sorcery |
| --- | --- |
| `sippeers` | `ps_endpoints`, `ps_aors`, `ps_auths` (uma linha cada, divididas) |
| `sipregs` | `ps_contacts` (registros dinâmicos) |
| — (saída `register=>`) | `ps_registrations` |
| — (correspondência de IP) | `ps_endpoint_id_ips` (os objetos `identify`) |
| — (aliases de domínio) | `ps_domain_aliases` |

A divisão conceitual é a mesma do caso de arquivo simples: uma linha `sippeers` torna-se *três* linhas em três tabelas (`ps_endpoints` + `ps_aors` + `ps_auths`) que referenciam umas às outras pelo nome do endpoint.

Duas coisas tornam isso tratável:

- **O esquema é gerado para você.** O Asterisk fornece migrações Alembic em `contrib/ast-db-manage/` que criam cada tabela `ps_*`. Execute `alembic upgrade head` contra o banco de dados `config` para construir o esquema PJSIP atual em vez de escrever DDL manualmente.
- **Existe um script de conversão SQL.** Ao lado do `sip_to_pjsip.py` está o **`sip_to_pjsql.py`** no mesmo diretório `contrib/scripts/sip_to_pjsip/`; ele reutiliza a mesma lógica do `convert()`, mas emite um arquivo `pjsip.sql` de instruções `INSERT` para as tabelas `ps_*` em vez de um arquivo de configuração simples. Assim como com a ferramenta de arquivo simples, revise a saída antes de carregá-la.

Finalmente, aponte o `sorcery.conf` para o seu banco de dados para que o PJSIP leia endpoints, aors, auths e contatos das tabelas `ps_*` (via `res_config_odbc` / `res_pjsip_realtime`), exatamente como o `extconfig.conf` apontava o `sippeers` para o banco de dados para o `chan_sip`. A mecânica do realtime é abordada no capítulo *Realtime*; o ponto específico da migração é simplesmente *quais tabelas mapeiam para quais*.

## Lista de verificação de migração

Uma ordem de operações pragmática para uma transição de produção:

1. **Inventário.** Liste cada dispositivo, trunk e `register =>` no `sip.conf` (ou cada linha `sippeers`/`sipregs`). Anote configurações personalizadas de NAT, codec e DTMF.
2. **Execute o conversor em um arquivo temporário.** `sip_to_pjsip.py sip.conf pjsip_generated.conf`. **Não** aponte para o seu `pjsip.conf` ativo.
3. **Leia o bloco "Non mapped elements"** no topo da saída e resolva cada linha — especialmente `qualify`, timers e qualquer coisa relacionada a NAT.
4. **Projete o(s) transporte(s) manualmente.** Um transporte por IP/porta; adicione TLS/TCP conforme necessário; defina `external_*_address` e `local_net` para caixas na nuvem/NAT.
5. **Verifique a autenticação.** Confirme `auth_type=digest`, nomes de usuário e senhas em cada objeto `auth`.
6. **Verifique NAT/mídia/DTMF.** `force_rport`/`rewrite_contact`/`rtp_symmetric`, `direct_media`, `dtmf_mode=rfc4733` por endpoint conforme necessário.
7. **Atualize o dialplan.** `SIP/` → `PJSIP/` em toda parte; verifique as funções `SIP*` e variáveis de canal.
8. **Atualize scripts e monitoramento.** Qualquer ferramenta ou consumidor AMI que analisava a saída do `sip show ...` deve migrar para `pjsip show ...` / ações AMI do PJSIP.
9. **Recarregue e verifique.** `module reload res_pjsip.so`, depois `pjsip show endpoints`, `pjsip show registrations`, `pjsip show identifies`.
10. **Teste com o logger de pacotes.** `pjsip set logger on`; faça um registro, uma chamada de entrada e uma chamada de saída e leia a troca SIP de ponta a ponta.

## Armadilhas comuns

- **O `alwaysauthreject` já vem integrado — não procure por ele.** O `chan_sip` precisava do `alwaysauthreject=yes` para não vazar quais extensões existiam respondendo de forma diferente a nomes de usuário incorretos. O PJSIP faz a coisa segura por design: ele nunca revela se um endpoint existe. Não há opção `alwaysauthreject` para definir. A proteção relacionada — limitar remetentes não identificados — é o `unidentified_request_count` / `unidentified_request_period` global, ativado por padrão.

- **O `insecure=invite` não é uma opção PJSIP — use `identify`.** Não existe `insecure=` no `pjsip.conf`. A maneira de aceitar INVITEs não autenticados de uma operadora conhecida é *identificar o endpoint pelo IP de origem* com `type=identify` / `match=`. Corresponda o mais estritamente possível (IPs de host específicos, não CIDRs amplos) e proteja-o com um `type=acl` — um trunk correspondido por IP sem autenticação é um alvo para fraude telefônica.

- **Um transporte por IP/porta.** Você não pode vincular dois transportes ao mesmo IP:porta, e você não pode vincular múltiplos transportes TCP ou TLS da mesma versão de IP. O script de conversão pode emitir um transporte que colide com um que você já possui — consolide em uma única camada de transporte projetada deliberadamente.

- **O `qualify=yes` não traduz para um booleano.** Ele pertence ao **aor** como `qualify_frequency=<seconds>`. O conversor descarta o `qualify=yes` no bloco não mapeado precisamente porque não há booleano equivalente no endpoint.

- **O `secret=` não é uma opção de endpoint.** Credenciais vivem apenas em um objeto `type=auth` que o endpoint *referencia* (`auth=` para entrada, `outbound_auth=` para saída). Colocar uma senha no endpoint não faz nada.

- **A CLI e quaisquer scripts de scraping quebram silenciosamente.** O `sip show ...` retorna "No such command", não um erro que seu monitoramento necessariamente detectará. Audite cada tarefa cron, verificação Nagios e cliente AMI para comandos `sip ` antes da transição.

## Resumo

Migrar para o Asterisk 22 significa migrar para fora do `chan_sip`, porque o driver foi removido no Asterisk 21 e o PJSIP é o único canal SIP que permanece. O cerne do trabalho é reexpressar cada `sip.conf` `peer`/`user`/`friend` — que agrupava tudo em um bloco — como um conjunto de objetos PJSIP cooperantes: um `endpoint` mais um `auth`, um `aor` e, dependendo do dispositivo, um `identify` (trunk de entrada), um `registration` (login de saída) e um `transport` compartilhado. O script `sip_to_pjsip.py` em `contrib/scripts/sip_to_pjsip/` faz a tradução em massa e sinaliza honestamente o que não consegue mapear em um bloco "Non mapped elements", mas sua saída é um primeiro rascunho: projete o transporte, NAT e segurança manualmente e teste antes da produção. Em torno da configuração, atualize o dialplan (`SIP/` → `PJSIP/`) e seus dedos e scripts (`sip show` → `pjsip show`, `sip set debug` → `pjsip set logger`). Implementações realtime movem-se das tabelas `sippeers`/`sipregs` para as tabelas Sorcery `ps_endpoints`/`ps_aors`/`ps_auths`/`ps_contacts`, com o `sip_to_pjsql.py` e o esquema `contrib/ast-db-manage` para ajudar. Observe as armadilhas — o `alwaysauthreject` já vem integrado, o `insecure=invite` torna-se `identify`, o `qualify=yes` torna-se `qualify_frequency` e um transporte por IP/porta — e a transição será mecânica em vez de misteriosa.

## Quiz

1. Por que uma implementação Asterisk 22 deve usar PJSIP para SIP?
   - A. O `chan_sip` é mais lento, mas ainda está disponível
   - B. O `chan_sip` foi removido no Asterisk 21 e não existe no Asterisk 22
   - C. PJSIP é o padrão, mas o `chan_sip` pode ser carregado com `modules.conf`
   - D. O `chan_sip` só funciona com TLS no Asterisk 22

2. Um único bloco `sip.conf` `type=friend` torna-se mais comumente qual conjunto de objetos PJSIP?
   - A. Um único `type=peer`
   - B. Apenas `type=endpoint`
   - C. `type=endpoint` + `type=auth` + `type=aor`
   - D. `type=transport` + `type=registration`

3. No `sip.conf`, o `host=dynamic` (o dispositivo registra sua própria localização) mapeia para:
   - A. `type=identify` com `match=dynamic`
   - B. um `type=aor` com `max_contacts` (o dispositivo faz REGISTER)
   - C. `direct_media=yes` no endpoint
   - D. `type=registration`

4. O script de conversão `sip_to_pjsip.py` é:
   - A. Um comando CLI: `asterisk -rx 'sip_to_pjsip'`
   - B. Um script Python na árvore de fontes do Asterisk em `contrib/scripts/sip_to_pjsip/`
   - C. Um módulo compilado carregado no boot
   - D. Parte do `res_pjsip.so`

5. Verdadeiro ou Falso: A saída do `sip_to_pjsip.py` está pronta para produção e deve ser carregada sem revisão.

6. O atalho `nat=force_rport,comedia` do `chan_sip` traduz em um endpoint PJSIP para quais três opções?
   - A. `nat=yes`, `qualify=yes`, `directmedia=no`
   - B. `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes`
   - C. `external_media_address`, `external_signaling_address`, `local_net`
   - D. `insecure=invite`, `identify`, `match`

7. O `dtmfmode=rfc2833` do `sip.conf` torna-se qual configuração PJSIP?
   - A. `dtmf_mode=rfc2833`
   - B. `dtmf_mode=inband`
   - C. `dtmf_mode=rfc4733`
   - D. `dtmf_mode=info`

8. No Asterisk 22, um objeto `auth` deve usar qual `auth_type`, e qual é o status do `userpass`?
   - A. `auth_type=userpass`; é o único valor válido
   - B. `auth_type=digest`; o `userpass` está descontinuado e convertido para `digest`
   - C. `auth_type=md5`; o `digest` está descontinuado
   - D. `auth_type=plaintext`; o `digest` foi removido

9. Um peer de provedor `chan_sip` com `insecure=invite` (aceitar INVITEs não autenticados de um IP conhecido) é migrado para PJSIP usando:
   - A. `insecure=invite` no endpoint
   - B. `allowguest=yes` em `[global]`
   - C. um objeto `type=identify` com `match=<provider IP>`
   - D. `auth_type=anonymous`

10. Em uma migração realtime, a tabela `chan_sip` `sippeers` é substituída por quais tabelas PJSIP/Sorcery?
    - A. Uma única tabela `pjsip_peers`
    - B. `ps_endpoints`, `ps_aors` e `ps_auths`
    - C. `sipregs` e `voicemail`
    - D. Apenas `ps_contacts`

**Respostas:** 1 — B · 2 — C · 3 — B · 4 — B · 5 — Falso · 6 — B · 7 — C · 8 — B · 9 — C · 10 — B
