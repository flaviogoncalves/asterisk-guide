# The Asterisk REST Interface (ARI)

Le chapitre précédent a couvert AMI et AGI, les deux méthodes classiques pour raccorder une logique externe à Asterisk. Toutes deux sont antérieures au web moderne : AMI vous fournit un flux d’événements brut, orienté ligne, via une socket TCP, et AGI confie un canal unique à un script pendant toute la durée d’un appel. Aucun des deux n’a été conçu pour le type d’applications état‑ful, asynchrones et multi‑canaux que les gens construisent aujourd’hui — des IVR qui interagissent avec des services web, des tableaux de bord click‑to‑call, des contrôleurs de conférence, ou des voicebots qui diffusent de l’audio vers un moteur de reconnaissance vocale.

ARI — l’Asterisk REST Interface — a été introduit dans Asterisk 12 pour combler cette lacune, et dans Asterisk 22 c’est l’interface recommandée pour créer de nouvelles applications de téléphonie. L’idée derrière ARI est une séparation claire des responsabilités : **Asterisk devient un moteur média** (il répond aux canaux, mélange les ponts, lit et enregistre l’audio, envoie les DTMF), et **votre application fournit toute la logique de contrôle des appels** via une combinaison d’une API REST (HTTP) et d’un flux d’événements WebSocket.

## Objectifs

- Expliquer ce qu’est ARI et comment il diffère d’AMI et d’AGI
- Décider quand ARI est l’interface appropriée pour un projet
- Configurer `ari.conf` et `http.conf` pour activer ARI et créer un utilisateur
- Se connecter au flux d’événements WebSocket d’ARI
- Décrire l’application de dialplan Stasis et les événements `StasisStart`/`StasisEnd`
- Décrire le modèle de ressources ARI : canaux, ponts, lectures, enregistrements, points de terminaison et états des appareils
- Écrire une application Stasis minimale en Python qui répond à un canal, lit un son et raccroche
- Expliquer ce qu’est le canal `externalMedia` et pourquoi il est important pour les intégrations IA et voicebot

## What ARI is, and when to use it

ARI is built on two transports working together:

- **A REST (HTTP) API** that your application calls to *do* things — originate a channel, answer it, play a sound, create a bridge, start a recording, hang up. These are ordinary HTTP requests (`GET`, `POST`, `DELETE`) against `http://asterisk-host:8088/ari/...`.
- **A WebSocket event stream** over which Asterisk *tells* your application what is happening — a channel was created, a DTMF digit arrived, a playback finished, a channel left your application. Events are delivered as JSON objects.

The pattern is asynchronous: you make a request, and the *result* of that request usually comes back later as an event. For example, you `POST` a request to play a sound; Asterisk answers immediately with a `Playback` object, and some seconds later you receive a `PlaybackFinished` event when the audio is done.

Choose ARI over AMI and AGI when:

- You need **fine-grained control of channels and bridges** — building conferences, parking, queues, or custom call flows from primitives instead of relying on dialplan applications.
- Your application is **stateful and long-lived**, holding several channels at once and reacting to events across all of them.
- You want to integrate with **web services, message buses, or AI/speech engines** and prefer JSON over HTTP to a line protocol or a stdin/stdout script.
- You are starting a **new project** and want the interface the Asterisk project actively recommends.

AMI is still the right tool when you only need to *observe* the system or fire occasional commands (dialers, wallboards, monitoring). AGI is still convenient for a quick, self-contained IVR script. But for anything that orchestrates calls, ARI is the modern answer.

> ARI does not replace the dialplan — it complements it. A channel runs in the dialplan as usual until it reaches the `Stasis()` application, at which point control is handed to your ARI application. When your application is done, the channel can be sent back into the dialplan or hung up.

## Activation d'ARI : http.conf et ari.conf

ARI s’appuie sur le serveur HTTP intégré d’Asterisk, de sorte que deux fichiers de configuration sont concernés : `http.conf` active le serveur web, et `ari.conf` active ARI et définit ses utilisateurs.

### http.conf

Le serveur HTTP doit être activé et lié à une adresse et un port. Le port ARI conventionnel est **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

En production, vous devez placer ARI derrière TLS. Asterisk peut servir HTTPS directement (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), ou vous pouvez terminer TLS dans un proxy inverse placé devant le port 8088. En TLS, les URL deviennent `https://` et `wss://` au lieu de `http://` et `ws://`.

Vous pouvez confirmer que le serveur HTTP est opérationnel depuis la CLI :

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` possède une section `[general]` et une section par utilisateur.

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

Quelques remarques sur ces options :

- `enabled` active ou désactive ARI globalement.
- `pretty` formate les réponses JSON pour qu’elles soient lisibles par l’homme ; désactivez-le en production.
- Chaque utilisateur est une section nommée avec `type=user`.
- `read_only=yes` limite cet utilisateur aux requêtes en lecture seule (GET).
- `password_format` peut être `plain` (le mot de passe en texte clair) ou `crypt` (un mot de passe haché, généré avec `mkpasswd -m sha-512`).
- `permit`, `deny` et `acl` autorisent des restrictions d’IP par utilisateur, suivant les mêmes règles que `acl.conf`.

Après avoir modifié les fichiers, rechargez les modules concernés (`module reload res_ari.so` et `module reload http.so`) ou redémarrez Asterisk. Vous pouvez vérifier qu’ARI fonctionne avec :

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

`ari show apps` répertorie les applications Stasis actuellement enregistrées par les clients connectés. Elle est vide tant qu’aucun client ne s’est connecté, ce qui est exactement ce que nous ferons ensuite.

### URL des événements WebSocket

Un client s’abonne au flux d’événements en ouvrant un WebSocket vers le point de terminaison `/ari/events`, en indiquant l’application Stasis qu’il implémente et en transmettant ses identifiants :

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

Les paramètres de requête sont :

- `app` — le nom de votre application Stasis. C’est le même nom que vous utiliserez dans l’appel `Stasis()` du dialplan. Vous pouvez transmettre plusieurs noms séparés par des virgules.
- `api_key` — les identifiants, sous la forme `username:password`, correspondant à un utilisateur dans `ari.conf`.
- `subscribeAll` — booléen optionnel (par défaut `false`) ; lorsque `true`, l’application reçoit tous les événements, pas seulement ceux relatifs aux ressources qu’elle possède.

Les mêmes identifiants `user:pass` sont utilisés comme authentification HTTP Basic sur les appels REST (ou ajoutés comme paramètre de requête `api_key` également).

## Stasis : remise d’un canal à votre application

Le pont entre le dialplan et ARI est l’application dialplan **`Stasis()`** (le cadre sous‑jacent s’appelle également Stasis). Lorsqu’un canal atteint `Stasis(appname[,args])`, Asterisk remet ce canal à l’application ARI enregistrée sous `appname` et cesse d’exécuter le dialplan pour celui‑ci. Le contrôle revient maintenant à votre code.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Lorsque le canal entre dans l’application, chaque client connecté abonné à `hello` reçoit un événement **`StasisStart`** via le WebSocket, contenant l’objet complet du canal (son ID, son nom, son caller ID, son état, et tout argument transmis à `Stasis()`). C’est le signal pour commencer à contrôler le canal.

Lorsque le canal quitte l’application — parce que votre code l’a renvoyé au dialplan avec `continueInDialplan`, ou parce qu’il a été raccroché — vous recevez un événement **`StasisEnd`**. Après que `Stasis()` revienne au dialplan, il définit la variable de canal `STASISSTATUS` (`SUCCESS` ou `FAILED`), afin que le dialplan puisse bifurquer selon le résultat.

## The ARI resource model

ARI expose les internes d'Asterisk sous forme d'un petit ensemble de ressources REST. Chaque ressource vit sous `/ari/<resource>` et est manipulée avec les méthodes HTTP standard. Les plus importantes :

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | A single call leg | originate, answer, play, record, hangup |
| **bridges** | A mixing point that joins channels | create, add/remove channels, play to the bridge |
| **playbacks** | An in-progress media playback | get status, stop, pause/unpause |
| **recordings** | Live and stored recordings | start, stop, list stored, delete |
| **endpoints** | Configured peers (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Custom device states | list, get, set, delete |

Some concrete REST calls (paths shown with the `/ari` prefix that appears on the wire):

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

The `media` parameter on a `play` request takes a media URI. The most common form is a `sound:` URI naming a built-in sound, e.g. `sound:hello-world` or `sound:tt-monkeys`. When the audio finishes, Asterisk emits a `PlaybackFinished` event for that playback ID, which is how your application knows it can move on.

Channels and bridges are the two building blocks you combine to make call flows. To connect two callers, for instance, you originate or accept two channels, create a `mixing` bridge with `POST /ari/bridges`, and add both channels to it with `POST /ari/bridges/{bridgeId}/addChannel`. To build a conference, you simply keep adding channels to the same bridge.

## Un exemple pratique : une application Stasis minimale

Construisons la plus petite application ARI utile. Lorsqu’une extension est composée, l’appel entre dans notre application Stasis, qui répond, joue le prompt classique `hello-world`, puis raccroche.

### Le dialplan

Dans `extensions.conf`, envoyez le canal à Stasis :

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Le nom de l’application `hello` correspond au `app=hello` que nous utilisons lors de la connexion.

### Le client Python

Ce client utilise deux bibliothèques bien connues : `requests` pour les appels REST et `websocket-client` pour le flux d’événements. Installez‑les avec `pip install requests websocket-client`.

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

Exécutez le script, puis composez n’importe quel numéro depuis un point d’accès enregistré. Vous devriez entendre « Hello, world », après quoi l’appel est libéré. Sur la console Asterisk, `ari show apps` affichera maintenant `hello` tant que le client est connecté.

Le déroulement vaut la peine d’être suivi une fois :

1. Le dialplan exécute `Stasis(hello)` ; Asterisk transmet le canal à notre application et envoie un événement `StasisStart`.
2. Nous répondons au canal, puis demandons à Asterisk de jouer `sound:hello-world`. Asterisk renvoie un objet `Playback` dont nous mémorisons le `id`.
3. Lorsque l’audio se termine, Asterisk envoie `PlaybackFinished` avec cette lecture `id` ; nous recherchons le canal et le raccrochons.
4. Le raccrochage provoque la sortie du canal de Stasis, générant un événement `StasisEnd`.

> **Une remarque sur les bibliothèques clientes.** Un wrapper de haut niveau appelé `ari-py` (le paquet `ari`) existe, mais il n’est plus maintenu et a été écrit pour une époque antérieure de Python et des outils Swagger. Pour de nouveaux travaux sur Asterisk 22, privilégiez l’approche explicite `requests` + WebSocket présentée ci‑dessus, ou une bibliothèque asyncio telle que `asyncari` si vous avez besoin de concurrence. L’approche brute vous maintient proche des appels REST et des événements réels, ce qui est exactement ce que vous voulez lors de l’apprentissage d’ARI.

## externalMedia: the door to AI and voicebots

The resources above let you play and record *files*. But modern voice applications — speech-to-text transcription, AI voicebots, real-time analytics — need the *live audio stream* of a call delivered to an external process, and they need to inject audio back.

ARI provides this through the **`externalMedia` channel**. A `POST /ari/channels/externalMedia` request creates a special channel that, instead of talking to a phone, streams the call's RTP media to (and from) an external host. You bridge this channel with the caller's channel, and now your external program is in the audio path: it receives the caller's audio as RTP and can send synthesized audio back.

The request requires only:

- `app` — the Stasis application that owns the new channel.
- `format` — the audio format, e.g. `ulaw` or `slin16`.

`external_host` (the `host:port` of your media application) is optional in the schema — it may be empty for a WebSocket-server-style connection — but for a classic RTP voicebot you will supply it. The `encapsulation` parameter defaults to `rtp` and `transport` to `udp`, which is exactly what you want for a streaming media endpoint.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

This single feature is what turns Asterisk into a front-end for AI: the telephone network terminates on Asterisk, ARI orchestrates the call, and `externalMedia` pipes the audio to a speech/AI engine and back. This is the mechanism on which AI services and voicebots are built.

## Résumé

ARI est l’interface moderne et recommandée pour créer des applications de téléphonie sur Asterisk 22. Elle sépare clairement le travail : Asterisk est le moteur média, et votre application — communiquant en JSON via HTTP et un WebSocket — fournit la logique de contrôle des appels. Vous l’activez via `http.conf` (le serveur web intégré sur le port 8088) et `ari.conf` (qui active ARI et définit les utilisateurs).

L’application de dialplan `Stasis()` remet un canal à votre application, déclenchant `StasisStart` lorsqu’il entre et `StasisEnd` lorsqu’il quitte. À partir de là, vous manipulez un petit ensemble de ressources REST — channels, bridges, playbacks, recordings, endpoints et device states — pour répondre, jouer, enregistrer, créer des ponts et raccrocher.

Nous avons construit une application Python Stasis minimale qui répond à un appel, joue une invite et raccroche, et nous avons vu comment le canal `externalMedia` diffuse du RTP en direct vers un programme externe — la base pour les intégrations d’IA et de bots vocaux.

## Quiz

1. ARI a été introduit dans quelle version d'Asterisk ?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. Dans le modèle ARI, Asterisk agit comme moteur média tandis que votre application externe fournit la logique de contrôle d’appel.
   - A. Vrai
   - B. Faux
3. ARI utilise deux transports ensemble. Quelle paire est correcte ?
   - A. Une API REST/HTTP pour émettre des commandes et un flux WebSocket pour recevoir des événements
   - B. Un protocole ligne TCP et un script stdin/stdout
   - C. SNMP et SMTP
   - D. Deux sockets UDP séparés
4. Quels sont les deux fichiers de configuration à configurer pour activer ARI ?
   - A. `manager.conf` et `agi.conf`
   - B. `http.conf` et `ari.conf`
   - C. `sip.conf` et `rtp.conf`
   - D. `modules.conf` et `cdr.conf`
5. Le port TCP conventionnel pour le serveur HTTP d'Asterisk (et donc ARI) est ____.
6. Quelle application du dialplan transmet un canal à une application ARI ?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. Lorsqu’un canal entre dans une application Stasis, quel événement est envoyé au client connecté ?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Quelle requête ARI crée un point de mixage pouvant joindre deux canaux ou plus ensemble ?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. Pour lire une invite intégrée sur un canal, quel événement indique à votre application que l’audio est terminé afin de pouvoir continuer ?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. Le canal `externalMedia` est principalement utilisé pour :
    - A. Enregistrer un appel dans un fichier WAV local
    - B. Diffuser l’audio en direct de l’appel (RTP) vers et depuis une application externe, par ex. un moteur IA/voix
    - C. Enregistrer un endpoint PJSIP
    - D. Recharger le dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
