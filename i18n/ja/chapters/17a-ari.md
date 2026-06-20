# The Asterisk REST Interface (ARI)

前章では AMI と AGI、Asterisk に外部ロジックを組み込む2つの従来手法について説明しました。どちらもモダンなウェブ以前の技術です。AMI は TCP ソケット上で生の行指向イベントストリームを提供し、AGI は通話中の単一チャネルをスクリプトに渡します。どちらも、今日構築されるような状態を保持し非同期で複数チャネルを扱うアプリケーション、たとえば Web サービスと連携する IVR、クリック・トゥ・コール ダッシュボード、会議コントローラ、音声をストリーミングして音声エンジンに渡すボイスボット向けに設計されたものではありません。

ARI — Asterisk REST Interface — は Asterisk 12 で導入され、このギャップを埋めるために作られました。Asterisk 22 では新しいテレフォニーアプリケーションを構築するための推奨インターフェースとなっています。ARI の背後にある考え方は、関心事の明確な分離です。**Asterisk はメディアエンジンになる**（チャネルに応答し、ブリッジをミックスし、音声を再生・録音し、DTMF を送信する）一方、**アプリケーション側が REST (HTTP) API と WebSocket イベントストリームの組み合わせで全てのコールコントロールロジックを提供する**というものです。

## Objectives

この章の終わりまでに、読者は次のことができるようになります。

- ARI が何であるか、そして AMI や AGI とどのように異なるかを説明できること
- プロジェクトに ARI が適切なインターフェースであるかを判断できること
- `ari.conf` と `http.conf` を設定して ARI を有効化し、ユーザーを作成できること
- ARI WebSocket イベントストリームに接続できること
- Stasis ダイヤルプランアプリケーションと `StasisStart`/`StasisEnd` イベントを説明できること
- ARI リソースモデル（チャネル、ブリッジ、プレイバック、レコーディング、エンドポイント、デバイスステート）を説明できること
- チャネルに応答し、サウンドを再生し、切断する最小限の Stasis アプリケーションを Python で作成できること
- `externalMedia` チャネルが何であるか、そして AI やボイスボット統合においてなぜ重要かを説明できること

## What ARI is, and when to use it

ARI は 2 つのトランスポートが連携して動作します:

- **REST (HTTP) API** – アプリケーションが *実行* するために呼び出すものです。チャネルの発信、応答、サウンドの再生、ブリッジの作成、録音の開始、切断などを行います。これらは普通の HTTP リクエスト（`GET`、`POST`、`DELETE`）で `http://asterisk-host:8088/ari/...` に対して行われます。
- **WebSocket イベントストリーム** – Asterisk がアプリケーションに何が起きたかを *通知* するものです。チャネルが作成された、DTMF が到着した、再生が完了した、チャネルがアプリケーションから離れた、などのイベントが JSON オブジェクトとして配信されます。

このパターンは非同期です: リクエストを送信し、そのリクエストの *結果* は通常、後でイベントとして返ってきます。たとえば、サウンドを再生するリクエストを `POST` とすると、Asterisk はすぐに `Playback` オブジェクトで応答し、数秒後に音声が終了したことを示す `PlaybackFinished` イベントが届きます。

ARI を AMI や AGI より選ぶべきケース:

- **チャネルやブリッジの細かい制御が必要** – 会議、パーキング、キュー、またはプリミティブからカスタムコールフローを構築したい場合、ダイヤルプランアプリケーションに依存しません。
- アプリケーションが **ステートフルで長時間稼働** し、複数のチャネルを同時に保持し、すべてのチャネルに対するイベントにリアクションする場合。
- **Web サービス、メッセージバス、AI/音声エンジン** と統合したい場合で、ラインプロトコルや stdin/stdout スクリプトよりも HTTP 上の JSON を好む場合。
- **新規プロジェクト** を開始し、Asterisk プロジェクトが積極的に推奨しているインターフェースを利用したい場合。

AMI はシステムを *観測* したり、たまにコマンドを発行したりするだけ（ダイヤラ、ウォールボード、モニタリング）には依然として適切です。AGI は手軽な単体 IVR スクリプトには便利です。しかし、コールをオーケストレーションするものすべてに対しては、ARI が現代的な答えです。

> ARI はダイヤルプランを置き換えるものではなく、補完します。チャネルは通常通りダイヤルプラン内で実行され、`Stasis()` アプリケーションに到達した時点で制御が ARI アプリケーションに渡されます。アプリケーションが終了すると、チャネルはダイヤルプランに戻すことも、切断することもできます。

## ARI の有効化: http.conf と ari.conf

ARI は Asterisk の組み込み HTTP サーバ上で動作するため、2 つの設定ファイルが関係します。`http.conf`でウェブサーバを有効にし、`ari.conf`で ARI を有効にしてユーザーを定義します。

### http.conf

HTTP サーバは有効化され、アドレスとポートにバインドされている必要があります。慣例的な ARI ポートは **8088** です。

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

本番環境では ARI を TLS の背後に置くべきです。Asterisk は HTTPS を直接提供できます（`tlsenable=yes`、`tlsbindaddr`、`tlscertfile`、`tlsprivatekey`）、あるいは 8088 ポートの前にリバースプロキシで TLS を終端させることもできます。TLS を使用すると URL は`https://`と`wss://`になり、`http://`と`ws://`ではなくなります。

CLI から HTTP サーバが起動しているか確認できます:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf`には`[general]`セクションとユーザーごとのセクションがあります。

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

これらのオプションに関するいくつかの注意点:

- `enabled`は ARI を全体的にオンまたはオフにします。
- `pretty`は JSON 応答を人間が読みやすい形式に整形します。本番環境ではオフにしてください。
- 各ユーザーは`type=user`を持つ名前付きセクションです。
- `read_only=yes`はそのユーザーを読み取り専用 (GET) リクエストに制限します。
- `password_format`は`plain`（パスワードが平文）または`crypt`（ハッシュ化されたパスワード、`mkpasswd -m sha-512`で生成）である可能性があります。
- `permit`、`deny`、`acl`はユーザーごとの IP 制限を許可し、`acl.conf`と同じルールに従います。

ファイルを編集したら、関連モジュール（`module reload res_ari.so`と`module reload http.so`）をリロードするか Asterisk を再起動してください。ARI が動作しているかは次で確認できます:

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

`ari show apps`は接続されたクライアントが現在登録している Stasis アプリケーションを一覧表示します。クライアントが接続するまで空であり、次に行うことがそれです。

### WebSocket イベント URL

クライアントは`/ari/events`エンドポイントに対して WebSocket を開き、実装する Stasis アプリケーション名を指定し、認証情報を渡すことでイベントストリームを購読します:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

クエリパラメータは次のとおりです:

- `app` — Stasis アプリケーションの名前。これは dialplan の`Stasis()`呼び出しで使用する名前と同じです。カンマ区切りで複数指定できます。
- `api_key` — 認証情報で、形式は`username:password`、`ari.conf`のユーザーに一致します。
- `subscribeAll` — オプションのブール値（デフォルト`false`）。`true`の場合、アプリケーションは所有するリソースだけでなくすべてのイベントを受け取ります。

同じ`user:pass`認証情報は REST 呼び出し時の HTTP Basic 認証としても使用され（または`api_key`クエリパラメータとして付加され）ます。

## Stasis: アプリケーションへのチャンネルの受け渡し

ダイヤルプランと ARI の間のブリッジは **`Stasis()`** ダイヤルプランアプリケーションです（基盤となるフレームワークも Stasis と呼ばれます）。チャンネルが `Stasis(appname[,args])` に到達すると、Asterisk はそのチャンネルを `appname` に登録された ARI アプリケーションに渡し、ダイヤルプランの実行を停止します。制御はあなたのコードに移ります。

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

チャンネルがアプリケーションに入ると、`hello` にサブスクライブしているすべてのクライアントに **`StasisStart`** イベントが WebSocket を通じて送られ、完全なチャンネルオブジェクト（ID、名前、発信者 ID、状態、そして `Stasis()` に渡された任意の引数）が含まれます。これがチャンネル制御を開始する合図です。

チャンネルがアプリケーションから離れるとき—コードが `continueInDialplan` でダイヤルプランに戻した場合や、ハングアップされた場合—**`StasisEnd`** イベントが受信されます。`Stasis()` がダイヤルプランに戻った後、`STASISSTATUS` チャンネル変数（`SUCCESS` または `FAILED`）が設定され、ダイヤルプランは結果に基づいて分岐できます。

## ARI リソースモデル

ARI は Asterisk の内部を小さな REST リソースの集合として公開します。各リソースは `/ari/<resource>` の下にあり、標準的な HTTP メソッドで操作されます。最も重要なものは次のとおりです。

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | 単一の通話レッグ | originate, answer, play, record, hangup |
| **bridges** | チャネルを結合するミキシングポイント | create, add/remove channels, play to the bridge |
| **playbacks** | 進行中のメディア再生 | get status, stop, pause/unpause |
| **recordings** | ライブおよび保存された録音 | start, stop, list stored, delete |
| **endpoints** | 設定されたピア (PJSIP など) | list, get state, send a message |
| **deviceStates** | カスタムデバイス状態 | list, get, set, delete |

いくつかの具体的な REST 呼び出し (パスはワイヤ上で表示される `/ari` プレフィックス付き):

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

The `media`パラメータは`play`リクエストでメディアURIを受け取ります。最も一般的な形式は、組み込みサウンドを指す`sound:`URIで、例えば`sound:hello-world`や`sound:tt-monkeys`です。音声が終了すると、Asteriskはその再生IDに対して`PlaybackFinished`イベントを発行し、これによりアプリケーションは次に進めることが分かります。

チャネルとブリッジは、通話フローを構成するために組み合わせる二つの構成要素です。例えば二人の発信者を接続するには、二つのチャネルを発信または受信し、`mixing`ブリッジを`POST /ari/bridges`で作成し、`POST /ari/bridges/{bridgeId}/addChannel`で両方のチャネルを追加します。会議を構築する場合は、同じブリッジにチャネルを追加し続けるだけです。

## A worked example: a minimal Stasis application

最小限の有用な ARI アプリケーションを構築しましょう。任意の内線がダイヤルされると、通話は Stasis アプリに入ります。アプリは通話に応答し、古典的な `hello-world` プロンプトを再生し、切断します。

### The dialplan

`extensions.conf` で、チャンネルを Stasis に送ります:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

アプリケーション名 `hello` は、接続時に使用する `app=hello` と一致します。

### The Python client

このクライアントは二つの有名なライブラリを使用します: `requests` は REST 呼び出し用、`websocket-client` はイベントストリーム用です。これらは `pip install requests websocket-client` でインストールします。

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

スクリプトを実行し、登録済みエンドポイントから任意の番号をダイヤルしてください。「Hello, world」の音声が聞こえた後、通話は切断されます。Asterisk コンソール上では、クライアントが接続中に `ari show apps` が `hello` を一覧表示します。

フローは一度追跡すると理解しやすいです:

1. ダイヤルプランが `Stasis(hello)` を実行します。Asterisk はチャンネルをアプリに渡し、`StasisStart` イベントを送信します。  
2. チャンネルに応答し、Asterisk に `sound:hello-world` の再生を指示します。Asterisk は `Playback` オブジェクトを返し、その `id` を保持します。  
3. 音声が終了すると、Asterisk は `PlaybackFinished` とその再生 `id` を送信します。チャンネルを検索し、切断します。  
4. 切断によりチャンネルは Stasis から離れ、`StasisEnd` イベントが生成されます。

> **A note on client libraries.** `ari-py`（`ari` パッケージ）という上位ラッパーも存在しますが、メンテナンスされておらず、古い Python と Swagger ツールチェーン向けに作られました。Asterisk 22 で新規に開発する場合は、上記の明示的な `requests` + WebSocket アプローチ、または並行処理が必要な場合は `asyncari` のような asyncio ライブラリを使用することを推奨します。生のアプローチは実際の REST 呼び出しとイベントに近い形で操作でき、ARI を学習する際にまさに求められる方法です。

## externalMedia: the door to AI and voicebots

上記のリソースでは *files* の再生と録音が可能です。しかし、モダンな音声アプリケーション――音声からテキストへの文字起こし、AI ボイスボット、リアルタイム分析――は、通話の *live audio stream* を外部プロセスに渡し、さらに音声を注入する必要があります。

ARI はこれを **`externalMedia` channel** を通じて提供します。`POST /ari/channels/externalMedia` リクエストは、電話と対話する代わりに通話の RTP メディアを外部ホストへ（および外部ホストから）ストリームする特別なチャネルを作成します。このチャネルを発信者のチャネルとブリッジすれば、外部プログラムがオーディオパスに入り、RTP で発信者の音声を受け取り、合成音声を送り返すことができます。

リクエストに必要なのは以下だけです：

- `app` ― 新しいチャネルを所有する Stasis アプリケーション。
- `format` ― オーディオフォーマット、例: `ulaw` または `slin16`。

`external_host`（メディアアプリケーションの `host:port`）はスキーマ上オプションです――WebSocket サーバー形式の接続では空でも構いません――しかし、従来型の RTP ボイスボットでは指定する必要があります。`encapsulation` パラメータはデフォルトで `rtp`、`transport` は `udp` に設定されており、これはストリーミングメディアエンドポイントに最適です。

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

この単一機能が Asterisk を AI のフロントエンドに変える鍵です：電話ネットワークは Asterisk で終端し、ARI が通話をオーケストレーションし、`externalMedia` が音声を音声/AI エンジンへ、そして戻します。これが AI サービスやボイスボットが構築されるメカニズムです。

## Summary

ARI は Asterisk 22 上でテレフォニーアプリケーションを構築するための、最新かつ推奨されるインターフェースです。作業をきれいに分割します：Asterisk がメディアエンジンとなり、JSON を HTTP と WebSocket でやり取りするアプリケーションがコールコントロールロジックを提供します。これを有効にするには `http.conf`（ポート 8088 の組み込みウェブサーバ）と `ari.conf`（ARI をオンにしユーザーを定義する）を使用します。

`Stasis()` ダイヤルプランアプリケーションはチャンネルをアプリに渡し、入場時に `StasisStart`、退出時に `StasisEnd` を発生させます。そこからは、REST リソース（channels、bridges、playbacks、recordings、endpoints、device states）の小さな集合を操作して、応答、再生、録音、ブリッジ、ハングアップを行います。

最小限の Python Stasis アプリを作成し、通話に応答してプロンプトを再生し、ハングアップする例を示しました。また、`externalMedia` チャンネルが外部プログラムへライブ RTP をストリームする様子を確認しました—これは AI やボイスボット統合の基盤となります。

## Quiz

1. ARI はどのバージョンの Asterisk で導入されましたか？
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. ARI モデルでは、Asterisk がメディアエンジンとして動作し、外部アプリケーションがコールコントロールロジックを提供します。
   - A. True
   - B. False
3. ARI は 2 つのトランスポートを組み合わせて使用します。正しい組み合わせはどれですか？
   - A. コマンド発行用の REST/HTTP API と、イベント受信用の WebSocket ストリーム
   - B. TCP ラインプロトコルと stdin/stdout スクリプト
   - C. SNMP と SMTP
   - D. 2 つの別個の UDP ソケット
4. ARI を有効にするために設定が必要な 2 つの設定ファイルはどれですか？
   - A. `manager.conf` と `agi.conf`
   - B. `http.conf` と `ari.conf`
   - C. `sip.conf` と `rtp.conf`
   - D. `modules.conf` と `cdr.conf`
5. Asterisk HTTP サーバー（したがって ARI）の標準 TCP ポートは ____ です。
6. どの dialplan アプリケーションがチャンネルを ARI アプリケーションに渡しますか？
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. チャンネルが Stasis アプリケーションに入ると、接続されたクライアントに送信されるイベントはどれですか？
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. 2 つ以上のチャンネルを結合できるミキシングポイントを作成する ARI リクエストはどれですか？
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. チャンネルで組み込みプロンプトを再生する際、オーディオが終了したことをアプリケーションに通知し、次に進めるようにするイベントはどれですか？
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. `externalMedia` チャンネルは主に何に使用されますか？
    - A. ローカル WAV ファイルへの通話録音
    - B. 通話のライブオーディオ（RTP）を外部アプリケーション（例：AI/音声エンジン）へストリームすること
    - C. PJSIP エンドポイントの登録
    - D. dialplan のリロード

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
