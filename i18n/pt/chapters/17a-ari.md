# The Asterisk REST Interface (ARI)

O capítulo anterior abordou AMI e AGI, as duas formas clássicas de conectar lógica externa ao Asterisk. Ambas são anteriores à web moderna: o AMI fornece um fluxo de eventos bruto, orientado a linhas, sobre um socket TCP, e o AGI entrega um único canal a um script durante a duração de uma chamada. Nenhuma das duas foi projetada para o tipo de aplicações com estado, assíncronas e multicanal que as pessoas constroem hoje — IVRs que conversam com serviços web, painéis de click-to-call, controladores de conferência ou voicebots que transmitem áudio para um motor de fala.

O ARI — o Asterisk REST Interface — foi introduzido no Asterisk 12 para preencher essa lacuna e, no Asterisk 22, é a interface recomendada para a construção de novas aplicações de telefonia. A ideia por trás do ARI é uma separação clara de responsabilidades: **o Asterisk torna-se um motor de mídia** (ele atende canais, mistura bridges, reproduz e grava áudio, envia DTMF), e **sua aplicação fornece toda a lógica de controle de chamadas** através de uma combinação de uma API REST (HTTP) e um fluxo de eventos WebSocket.

## Objetivos

Ao final deste capítulo, o leitor deverá ser capaz de:

- Explicar o que é o ARI e como ele difere do AMI e do AGI
- Decidir quando o ARI é a interface correta para um projeto
- Configurar `ari.conf` e `http.conf` para habilitar o ARI e criar um usuário
- Conectar-se ao fluxo de eventos WebSocket do ARI
- Descrever a aplicação de dialplan Stasis e os eventos `StasisStart`/`StasisEnd`
- Descrever o modelo de recursos do ARI: canais, bridges, playbacks, gravações, endpoints e estados de dispositivo
- Escrever uma aplicação Stasis mínima em Python que atende um canal, reproduz um som e desliga
- Explicar o que é o canal `externalMedia` e por que ele é importante para integrações de IA e voicebots

## O que é o ARI e quando usá-lo

O ARI é construído sobre dois transportes trabalhando juntos:

- **Uma API REST (HTTP)** que sua aplicação chama para *fazer* coisas — originar um canal, atendê-lo, reproduzir um som, criar uma bridge, iniciar uma gravação, desligar. Estas são requisições HTTP comuns (`GET`, `POST`, `DELETE`) contra `http://asterisk-host:8088/ari/...`.
- **Um fluxo de eventos WebSocket** através do qual o Asterisk *informa* à sua aplicação o que está acontecendo — um canal foi criado, um dígito DTMF chegou, uma reprodução terminou, um canal deixou sua aplicação. Os eventos são entregues como objetos JSON.

O padrão é assíncrono: você faz uma requisição e o *resultado* dessa requisição geralmente retorna mais tarde como um evento. Por exemplo, você faz `POST` de uma requisição para reproduzir um som; o Asterisk responde imediatamente com um objeto `Playback` e, alguns segundos depois, você recebe um evento `PlaybackFinished` quando o áudio termina.

Escolha o ARI em vez de AMI e AGI quando:

- Você precisa de **controle refinado de canais e bridges** — construindo conferências, estacionamento, filas ou fluxos de chamadas personalizados a partir de primitivas, em vez de depender de aplicações de dialplan.
- Sua aplicação é **com estado e de longa duração**, mantendo vários canais ao mesmo tempo e reagindo a eventos em todos eles.
- Você deseja integrar com **serviços web, barramentos de mensagens ou motores de IA/fala** e prefere JSON sobre HTTP a um protocolo de linha ou um script stdin/stdout.
- Você está iniciando um **novo projeto** e deseja a interface que o projeto Asterisk recomenda ativamente.

O AMI ainda é a ferramenta certa quando você só precisa *observar* o sistema ou disparar comandos ocasionais (discadores, painéis de monitoramento). O AGI ainda é conveniente para um script de IVR rápido e autocontido. Mas, para qualquer coisa que orquestre chamadas, o ARI é a resposta moderna.

> O ARI não substitui o dialplan — ele o complementa. Um canal é executado no dialplan como de costume até atingir a aplicação `Stasis()`, momento em que o controle é entregue à sua aplicação ARI. Quando sua aplicação termina, o canal pode ser enviado de volta ao dialplan ou desligado.

## Habilitando o ARI: http.conf e ari.conf

O ARI roda sobre o servidor HTTP embutido do Asterisk, portanto, dois arquivos de configuração estão envolvidos: `http.conf` habilita o servidor web e `ari.conf` habilita o ARI e define seus usuários.

### http.conf

O servidor HTTP deve estar habilitado e vinculado a um endereço e porta. A porta convencional do ARI é **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

Para produção, você deve colocar o ARI atrás de TLS. O Asterisk pode servir HTTPS diretamente (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), ou você pode terminar o TLS em um proxy reverso na frente da porta 8088. Sobre TLS, as URLs tornam-se `https://` e `wss://` em vez de `http://` e `ws://`.

Você pode confirmar se o servidor HTTP está ativo a partir da CLI:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` possui uma seção `[general]` e uma seção por usuário.

```ini
[general]
enabled=yes
pretty=yes              ; pretty-print JSON responses (handy while learning)

[asterisk]
type=user
read_only=no            ; set to yes for a user that may only issue GET requests
password=secret
password_format=plain   ; "plain" (default) or "crypt"
```

Algumas notas sobre estas opções:

- `enabled` liga ou desliga o ARI globalmente.
- `pretty` formata as respostas JSON para serem legíveis por humanos; desligue isso em produção.
- Cada usuário é uma seção nomeada com `type=user`.
- `read_only=yes` restringe esse usuário a requisições somente leitura (GET).
- `password_format` pode ser `plain` (a senha está em texto simples) ou `crypt` (uma senha com hash, gerada com `mkpasswd -m sha-512`).
- `permit`, `deny` e `acl` permitem restrições de IP por usuário, seguindo as mesmas regras de `acl.conf`.

Após editar os arquivos, recarregue os módulos relevantes (`module reload res_ari.so` e `module reload http.so`) ou reinicie o Asterisk. Você pode verificar se o ARI está rodando com:

```
asterisk*CLI> module show like res_ari
res_ari.so          Asterisk RESTful Interface          Running
res_ari_channels.so RESTful API module - Channel res... Running
res_ari_bridges.so  RESTful API module - Bridge reso... Running
...

asterisk*CLI> ari show apps
Application Name
=========================
```

`ari show apps` lista as aplicações Stasis atualmente registradas por clientes conectados. Ela fica vazia até que um cliente se conecte, que é exatamente o que faremos a seguir.

### A URL de eventos WebSocket

Um cliente assina o fluxo de eventos abrindo um WebSocket para o endpoint `/ari/events`, nomeando a aplicação Stasis que ele implementa e passando suas credenciais:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

Os parâmetros de consulta são:

- `app` — o nome da sua aplicação Stasis. Este é o mesmo nome que você usará na chamada `Stasis()` do dialplan. Você pode passar vários nomes separados por vírgula.
- `api_key` — as credenciais, na forma `username:password`, correspondendo a um usuário em `ari.conf`.
- `subscribeAll` — booleano opcional (padrão `false`); quando `true`, a aplicação recebe todos os eventos, não apenas aqueles dos recursos que ela possui.

As mesmas credenciais `user:pass` são usadas como autenticação HTTP Basic nas chamadas REST (ou anexadas como um parâmetro de consulta `api_key` lá também).

## Stasis: entregando um canal para sua aplicação

A ponte entre o dialplan e o ARI é a aplicação de dialplan **`Stasis()`** (o framework subjacente também é chamado de Stasis). Quando um canal atinge `Stasis(appname[,args])`, o Asterisk entrega esse canal para a aplicação ARI registrada sob `appname` e para de executar o dialplan para ele. O controle agora pertence ao seu código.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Quando o canal entra na aplicação, todo cliente conectado inscrito em `hello` recebe um evento **`StasisStart`** sobre o WebSocket, carregando o objeto de canal completo (seu ID, nome, identificador de chamadas, estado e quaisquer argumentos passados para `Stasis()`). Esta é a sua deixa para começar a controlar o canal.

Quando o canal deixa a aplicação — porque seu código o moveu de volta para o dialplan com `continueInDialplan`, ou porque ele foi desligado — você recebe um evento **`StasisEnd`**. Após `Stasis()` retornar ao dialplan, ele define a variável de canal `STASISSTATUS` (`SUCCESS` ou `FAILED`), para que o dialplan possa ramificar com base no resultado.

## O modelo de recursos do ARI

O ARI expõe os internos do Asterisk como um pequeno conjunto de recursos REST. Cada recurso vive sob `/ari/<resource>` e é manipulado com métodos HTTP padrão. Os mais importantes:

| Recurso | O que representa | Operações de exemplo |
|----------|--------------------|--------------------|
| **channels** | Uma perna de chamada única | originate, answer, play, record, hangup |
| **bridges** | Um ponto de mistura que une canais | create, add/remove channels, play to the bridge |
| **playbacks** | Uma reprodução de mídia em andamento | get status, stop, pause/unpause |
| **recordings** | Gravações ao vivo e armazenadas | start, stop, list stored, delete |
| **endpoints** | Peers configurados (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Estados de dispositivo personalizados | list, get, set, delete |

Algumas chamadas REST concretas (caminhos mostrados com o prefixo `/ari` que aparece na rede):

```
# Channels
POST   /ari/channels                          # originate a new channel
POST   /ari/channels/{channelId}/answer       # answer an incoming channel
POST   /ari/channels/{channelId}/play         # play media (body: media=sound:hello-world)
POST   /ari/channels/{channelId}/record       # record the channel
DELETE /ari/channels/{channelId}              # hang up the channel

# Bridges
POST   /ari/bridges                           # create a bridge (e.g. type=mixing)
POST   /ari/bridges/{bridgeId}/addChannel     # add a channel (param: channel=<id>)
POST   /ari/bridges/{bridgeId}/play           # play media to everyone in the bridge
DELETE /ari/bridges/{bridgeId}                # destroy the bridge

# Read-only resources
GET    /ari/endpoints
GET    /ari/deviceStates
GET    /ari/recordings/stored
GET    /ari/playbacks/{playbackId}
```

O parâmetro `media` em uma requisição `play` aceita um URI de mídia. A forma mais comum é um URI `sound:` nomeando um som embutido, por exemplo, `sound:hello-world` ou `sound:tt-monkeys`. Quando o áudio termina, o Asterisk emite um evento `PlaybackFinished` para aquele ID de playback, que é como sua aplicação sabe que pode prosseguir.

Canais e bridges são os dois blocos de construção que você combina para criar fluxos de chamadas. Para conectar dois chamadores, por exemplo, você origina ou aceita dois canais, cria uma bridge `mixing` com `POST /ari/bridges` e adiciona ambos os canais a ela com `POST /ari/bridges/{bridgeId}/addChannel`. Para construir uma conferência, você simplesmente continua adicionando canais à mesma bridge.

## Um exemplo prático: uma aplicação Stasis mínima

Vamos construir a menor aplicação ARI útil. Quando qualquer extensão é discada, a chamada entra em nosso app Stasis, que a atende, reproduz o prompt clássico `hello-world` e desliga.

### O dialplan

Em `extensions.conf`, envie o canal para o Stasis:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

O nome da aplicação `hello` corresponde ao `app=hello` que usamos ao conectar.

### O cliente Python

Este cliente usa duas bibliotecas bem conhecidas: `requests` para as chamadas REST e `websocket-client` para o fluxo de eventos. Instale-as com `pip install requests websocket-client`.

```python
#!/usr/bin/env python3
"""Minimal ARI Stasis app: answer, play hello-world, hang up."""
import json
import requests
from websocket import create_connection

ARI_HOST = "127.0.0.1"
ARI_PORT = 8088
ARI_USER = "asterisk"
ARI_PASS = "secret"
APP = "hello"

BASE = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

def answer(channel_id):
    requests.post(f"{BASE}/channels/{channel_id}/answer", auth=AUTH)

def play(channel_id, media):
    # Returns the Playback object; we could track its id to await PlaybackFinished.
    r = requests.post(
        f"{BASE}/channels/{channel_id}/play",
        params={"media": media},
        auth=AUTH,
    )
    return r.json()

def hangup(channel_id):
    requests.delete(f"{BASE}/channels/{channel_id}", auth=AUTH)

def main():
    ws_url = (
        f"ws://{ARI_HOST}:{ARI_PORT}/ari/events"
        f"?app={APP}&api_key={ARI_USER}:{ARI_PASS}"
    )
    ws = create_connection(ws_url)
    print(f"Connected to ARI, waiting for calls into Stasis app '{APP}'...")

    # Track which channel each playback belongs to, so we hang up when it ends.
    playback_owner = {}

    while True:
        event = json.loads(ws.recv())
        kind = event["type"]

        if kind == "StasisStart":
            channel_id = event["channel"]["id"]
            print(f"StasisStart on channel {channel_id}")
            answer(channel_id)
            pb = play(channel_id, "sound:hello-world")
            playback_owner[pb["id"]] = channel_id

        elif kind == "PlaybackFinished":
            pb_id = event["playback"]["id"]
            channel_id = playback_owner.pop(pb_id, None)
            if channel_id:
                print(f"Playback done, hanging up {channel_id}")
                hangup(channel_id)

        elif kind == "StasisEnd":
            print(f"StasisEnd on channel {event['channel']['id']}")

if __name__ == "__main__":
    main()
```

Execute o script e, em seguida, disque qualquer número de um endpoint registrado. Você deve ouvir "Hello, world", após o que a chamada é liberada. No console do Asterisk, `ari show apps` agora listará `hello` enquanto o cliente estiver conectado.

Vale a pena rastrear o fluxo uma vez:

1. O dialplan executa `Stasis(hello)`; o Asterisk entrega o canal ao nosso app e envia um evento `StasisStart`.
2. Nós atendemos o canal e, em seguida, pedimos ao Asterisk para reproduzir `sound:hello-world`. O Asterisk retorna um objeto `Playback` cujo `id` nós memorizamos.
3. Quando o áudio termina, o Asterisk envia `PlaybackFinished` com aquele `id` de playback; nós procuramos o canal e o desligamos.
4. Desligar faz com que o canal deixe o Stasis, produzindo um evento `StasisEnd`.

> **Uma nota sobre bibliotecas de cliente.** Um wrapper de nível superior chamado `ari-py` (o pacote `ari`) existe, mas não é mantido e foi escrito para uma era mais antiga de Python e ferramentas Swagger. Para novos trabalhos no Asterisk 22, prefira a abordagem explícita `requests` + WebSocket mostrada acima, ou uma biblioteca asyncio como `asyncari` se você precisar de concorrência. A abordagem bruta mantém você próximo das chamadas REST e eventos reais, que é exatamente o que você quer enquanto aprende o ARI.

## externalMedia: a porta para IA e voicebots

Os recursos acima permitem que você reproduza e grave *arquivos*. Mas aplicações de voz modernas — transcrição de fala para texto, voicebots de IA, análise em tempo real — precisam do *fluxo de áudio ao vivo* de uma chamada entregue a um processo externo, e precisam injetar áudio de volta.

O ARI fornece isso através do **canal `externalMedia`**. Uma requisição `POST /ari/channels/externalMedia` cria um canal especial que, em vez de falar com um telefone, transmite a mídia RTP da chamada para (e de) um host externo. Você faz a bridge deste canal com o canal do chamador, e agora seu programa externo está no caminho do áudio: ele recebe o áudio do chamador como RTP e pode enviar áudio sintetizado de volta.

A requisição requer apenas:

- `app` — a aplicação Stasis que possui o novo canal.
- `format` — o formato de áudio, por exemplo, `ulaw` ou `slin16`.

`external_host` (o `host:port` da sua aplicação de mídia) é opcional no esquema — pode ficar vazio para uma conexão estilo servidor WebSocket — mas para um voicebot RTP clássico, você o fornecerá. O parâmetro `encapsulation` tem como padrão `rtp` e `transport` para `udp`, que é exatamente o que você deseja para um endpoint de mídia de streaming.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

Este único recurso é o que transforma o Asterisk em um front-end para IA: a rede telefônica termina no Asterisk, o ARI orquestra a chamada e `externalMedia` canaliza o áudio para um motor de fala/IA e de volta. Este é o mecanismo sobre o qual serviços de IA e voicebots são construídos.

## Resumo

O ARI é a interface moderna e recomendada para a construção de aplicações de telefonia no Asterisk 22. Ele divide o trabalho de forma limpa: o Asterisk é o motor de mídia, e sua aplicação — falando JSON sobre HTTP e um WebSocket — fornece a lógica de controle de chamadas. Você o habilita através de `http.conf` (o servidor web embutido na porta 8088) e `ari.conf` (que liga o ARI e define usuários). A aplicação de dialplan `Stasis()` entrega um canal para seu app, levantando `StasisStart` quando ele entra e `StasisEnd` quando ele sai. A partir daí, você manipula um pequeno conjunto de recursos REST — canais, bridges, playbacks, gravações, endpoints e estados de dispositivo — para atender, reproduzir, gravar, fazer bridge e desligar. Construímos um app Stasis em Python mínimo que atende uma chamada, reproduz um prompt e desliga, e vimos como o canal `externalMedia` transmite RTP ao vivo para um programa externo — a base para integrações de IA e voicebots.

## Quiz

1. O ARI foi introduzido em qual versão do Asterisk?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. No modelo ARI, o Asterisk atua como um motor de mídia enquanto sua aplicação externa fornece a lógica de controle de chamadas.
   - A. Verdadeiro
   - B. Falso
3. O ARI usa dois transportes juntos. Qual par está correto?
   - A. Uma API REST/HTTP para emitir comandos e um fluxo WebSocket para receber eventos
   - B. Um protocolo de linha TCP e um script stdin/stdout
   - C. SNMP e SMTP
   - D. Dois sockets UDP separados
4. Quais dois arquivos de configuração devem ser configurados para habilitar o ARI?
   - A. `manager.conf` e `agi.conf`
   - B. `http.conf` e `ari.conf`
   - C. `sip.conf` e `rtp.conf`
   - D. `modules.conf` e `cdr.conf`
5. A porta TCP convencional para o servidor HTTP do Asterisk (e, portanto, o ARI) é ____.
6. Qual aplicação de dialplan entrega um canal para uma aplicação ARI?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. Quando um canal entra em uma aplicação Stasis, qual evento é enviado ao cliente conectado?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Qual requisição ARI cria um ponto de mistura que pode unir dois ou mais canais?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. Para reproduzir um prompt embutido em um canal, qual evento informa à sua aplicação que o áudio terminou para que ela possa prosseguir?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. O canal `externalMedia` é usado principalmente para:
    - A. Gravar uma chamada em um arquivo WAV local
    - B. Transmitir o áudio ao vivo (RTP) da chamada para e de uma aplicação externa, por exemplo, um motor de IA/fala
    - C. Registrar um endpoint PJSIP
    - D. Recarregar o dialplan

**Respostas:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
