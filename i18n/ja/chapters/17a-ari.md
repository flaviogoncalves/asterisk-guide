# The Asterisk REST Interface (ARI)

前章では、Asteriskに外部ロジックを組み込むための古典的な2つの方法であるAMIとAGIについて解説しました。どちらも現代のWeb以前から存在する技術です。AMIはTCPソケットを介した生の行指向イベントストリームを提供し、AGIは通話中、単一のチャネルをスクリプトに渡します。どちらも、今日人々が構築しているような、Webサービスと対話するIVR、クリック・トゥ・コール・ダッシュボード、会議コントローラー、音声エンジンに音声をストリーミングするボイスボットといった、ステートフルで非同期、かつマルチチャネルなアプリケーション向けには設計されていません。

ARI（Asterisk REST Interface）は、そのギャップを埋めるためにAsterisk 12で導入され、Asterisk 22では新しいテレフォニーアプリケーションを構築するための推奨インターフェースとなっています。ARIの背後にある考え方は、関心の明確な分離です。**Asteriskはメディアエンジンとなり**（チャネルの応答、ブリッジのミキシング、音声の再生と録音、DTMFの送信などを行います）、**アプリケーションはREST（HTTP）APIとWebSocketイベントストリームを組み合わせて、すべての通話制御ロジックを提供します**。

## 目標

本章を読み終えることで、読者は以下のことができるようになります。

- ARIとは何か、そしてAMIやAGIとどう違うのかを説明する
- プロジェクトにおいてARIが適切なインターフェースであるかどうかを判断する
- `ari.conf`と`http.conf`を設定してARIを有効にし、ユーザーを作成する
- ARIのWebSocketイベントストリームに接続する
- Stasis dialplanアプリケーションと`StasisStart`/`StasisEnd`イベントについて説明する
- ARIのリソースモデル（チャネル、ブリッジ、再生、録音、endpoint、デバイス状態）について説明する
- チャネルに応答し、音声を再生し、切断する最小限のStasisアプリケーションをPythonで記述する
- `externalMedia`チャネルとは何か、そしてそれがAIやボイスボットの統合においてなぜ重要なのかを説明する

## ARIとは何か、そしていつ使うべきか

ARIは、連携して動作する2つのトランスポートの上に構築されています。

- **REST（HTTP）API**: アプリケーションが「何かを行う」ために呼び出すAPIです。チャネルの発信、応答、音声の再生、ブリッジの作成、録音の開始、切断などを行います。これらは`http://asterisk-host:8088/ari/...`に対する通常のHTTPリクエスト（`GET`、`POST`、`DELETE`）です。
- **WebSocketイベントストリーム**: Asteriskが「何が起きているか」をアプリケーションに伝えるためのストリームです。チャネルが作成された、DTMFが届いた、再生が終了した、チャネルがアプリケーションから離れた、といった情報がJSONオブジェクトとして配信されます。

このパターンは非同期です。リクエストを行うと、そのリクエストの「結果」は通常、後からイベントとして返ってきます。例えば、音声を再生するリクエストを`POST`すると、Asteriskは直ちに`Playback`オブジェクトで応答し、数秒後に音声が完了した時点で`PlaybackFinished`イベントを受け取ります。

以下のような場合に、AMIやAGIではなくARIを選択してください。

- **チャネルとブリッジのきめ細かな制御が必要な場合**: ダイヤルプランのアプリケーションに頼るのではなく、プリミティブから会議、パーク、キュー、あるいは独自の通話フローを構築する場合。
- **アプリケーションがステートフルで長期間動作する場合**: 一度に複数のチャネルを保持し、それらすべてのイベントに反応する必要がある場合。
- **Webサービス、メッセージバス、AI/音声エンジンと統合したい場合**: 行プロトコルやstdin/stdoutスクリプトよりも、HTTP上のJSONを好む場合。
- **新しいプロジェクトを開始する場合**: Asteriskプロジェクトが積極的に推奨しているインターフェースを使いたい場合。

システムを「監視」するだけ、あるいは時折コマンドを発行するだけ（ダイヤラー、ウォールボード、モニタリングなど）であれば、AMIが依然として適切なツールです。AGIは、小規模で完結したIVRスクリプトには依然として便利です。しかし、通話をオーケストレーションするようなものであれば、ARIが現代の答えとなります。

> ARIはダイヤルプランを置き換えるものではなく、補完するものです。チャネルは通常通りダイヤルプラン内で実行され、`Stasis()`アプリケーションに到達した時点で、制御がARIアプリケーションに引き渡されます。アプリケーションの処理が完了すると、チャネルはダイヤルプランに戻されるか、切断されます。

## ARIの有効化: http.conf と ari.conf

ARIはAsteriskの組み込みHTTPサーバー上で動作するため、2つの設定ファイルが関係します。`http.conf`でWebサーバーを有効にし、`ari.conf`でARIを有効にしてユーザーを定義します。

### http.conf

HTTPサーバーを有効にし、アドレスとポートにバインドする必要があります。ARIの標準的なポートは**8088**です。

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

本番環境では、ARIをTLSの背後に配置すべきです。AsteriskはHTTPSを直接提供することもできますし（`tlsenable=yes`、`tlsbindaddr`、`tlscertfile`、`tlsprivatekey`）、ポート8088の手前にあるリバースプロキシでTLSを終端させることもできます。TLS経由の場合、URLは`http://`や`ws://`ではなく`https://`や`wss://`になります。

HTTPサーバーが起動しているかどうかは、CLIから確認できます。

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf`には`[general]`セクションと、ユーザーごとのセクションがあります。

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

これらのオプションに関するいくつかの注意点です。

- `enabled`はARIをグローバルにオン/オフします。
- `pretty`はJSONレスポンスを人間が読みやすい形式に整形します。本番環境ではオフにしてください。
- 各ユーザーは`type=user`を持つ名前付きセクションです。
- `read_only=yes`はそのユーザーを読み取り専用（GET）リクエストに制限します。
- `password_format`は`plain`（パスワードがプレーンテキスト）または`crypt`（`mkpasswd -m sha-512`で生成されたハッシュ化パスワード）のいずれかになります。
- `permit`、`deny`、`acl`は、`acl.conf`と同じルールに従い、ユーザーごとのIP制限を可能にします。

ファイルを編集した後、関連するモジュールをリロード（`module reload res_ari.so`および`module reload http.so`）するか、Asteriskを再起動します。ARIが実行されているかどうかは以下で確認できます。

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

`ari show apps`は、接続中のクライアントによって現在登録されているStasisアプリケーションを一覧表示します。クライアントが接続するまでは空ですが、次にそれを行います。

### WebSocketイベントURL

クライアントは、`/ari/events`エンドポイントに対してWebSocketを開き、実装するStasisアプリケーション名を指定し、資格情報を渡すことでイベントストリームを購読します。

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

クエリパラメータは以下の通りです。

- `app`: Stasisアプリケーションの名前。これはダイヤルプランの`Stasis()`呼び出しで使用する名前と同じです。カンマ区切りで複数の名前を渡すこともできます。
- `api_key`: 資格情報。形式は`username:password`で、`ari.conf`内のユーザーと一致する必要があります。
- `subscribeAll`: オプションのブール値（デフォルトは`false`）。`true`の場合、アプリケーションは自身が所有するリソースだけでなく、すべてのイベントを受信します。

同じ`user:pass`資格情報が、REST呼び出し時のHTTP Basic認証として使用されます（または、そこでも`api_key`クエリパラメータとして付加されます）。

## Stasis: アプリケーションへのチャネルの引き渡し

ダイヤルプランとARIの架け橋となるのが**`Stasis()`**ダイヤルプランアプリケーションです（基盤となるフレームワークもStasisと呼ばれます）。チャネルが`Stasis(appname[,args])`に到達すると、Asteriskはそのチャネルを`appname`の下に登録されたARIアプリケーションに引き渡し、そのチャネルに対するダイヤルプランの実行を停止します。制御はあなたのコードに委ねられます。

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

チャネルがアプリケーションに入ると、`hello`を購読しているすべての接続済みクライアントは、WebSocket経由で**`StasisStart`**イベントを受信します。これには完全なチャネルオブジェクト（ID、名前、発信者ID、状態、および`Stasis()`に渡された引数）が含まれています。これがチャネルの制御を開始する合図です。

チャネルがアプリケーションから離れるとき（コードが`continueInDialplan`でダイヤルプランに戻したか、切断された場合）、**`StasisEnd`**イベントを受信します。`Stasis()`がダイヤルプランに戻ると、`STASISSTATUS`チャネル変数（`SUCCESS`または`FAILED`）が設定されるため、ダイヤルプランは結果に基づいて分岐できます。

## ARIのリソースモデル

ARIはAsteriskの内部構造を少数のRESTリソースとして公開します。各リソースは`/ari/<resource>`の下に存在し、標準的なHTTPメソッドで操作されます。最も重要なものは以下の通りです。

| リソース | 表すもの | 操作例 |
|----------|--------------------|--------------------|
| **channels** | 単一の通話レグ | originate, answer, play, record, hangup |
| **bridges** | チャネルを結合するミキシングポイント | create, add/remove channels, play to the bridge |
| **playbacks** | 進行中のメディア再生 | get status, stop, pause/unpause |
| **recordings** | ライブおよび保存済みの録音 | start, stop, list stored, delete |
| **endpoints** | 設定済みのピア (PJSIPなど) | list, get state, send a message |
| **deviceStates** | カスタムデバイス状態 | list, get, set, delete |

具体的なREST呼び出し（パスはネットワーク上に現れる`/ari`プレフィックス付きで表示）：

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

`play`リクエストの`media`パラメータは、メディアURIを受け取ります。最も一般的な形式は、組み込みサウンドを指定する`sound:`URIです（例: `sound:hello-world`や`sound:tt-monkeys`）。音声が終了すると、Asteriskはその再生IDに対して`PlaybackFinished`イベントを発行します。アプリケーションはこれによって、次の処理に進めることを知ります。

チャネルとブリッジは、通話フローを作成するために組み合わせる2つの構成要素です。例えば、2人の発信者を接続するには、2つのチャネルを発信または受け入れ、`POST /ari/bridges`で`mixing`ブリッジを作成し、`POST /ari/bridges/{bridgeId}/addChannel`で両方のチャネルをそこに追加します。会議を構築するには、同じブリッジにチャネルを追加し続けるだけです。

## 実践例: 最小限のStasisアプリケーション

最も小さく有用なARIアプリケーションを構築してみましょう。任意のエクステンションがダイヤルされると、通話はStasisアプリに入り、応答して古典的な`hello-world`プロンプトを再生し、切断します。

### ダイヤルプラン

`extensions.conf`で、チャネルをStasisに送信します。

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

アプリケーション名`hello`は、接続時に使用する`app=hello`と一致します。

### Pythonクライアント

このクライアントは、2つの有名なライブラリを使用します。REST呼び出し用の`requests`と、イベントストリーム用の`websocket-client`です。これらは`pip install requests websocket-client`でインストールします。

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

スクリプトを実行し、登録済みのendpointから任意の番号にダイヤルしてください。「Hello, world」が聞こえ、その後通話が解放されるはずです。Asteriskコンソールでは、クライアントが接続されている間、`ari show apps`が`hello`をリスト表示します。

このフローは一度追跡する価値があります。

1. ダイヤルプランが`Stasis(hello)`を実行し、Asteriskがチャネルをアプリに引き渡し、`StasisStart`イベントを送信します。
2. チャネルに応答し、Asteriskに`sound:hello-world`を再生するよう要求します。Asteriskは`Playback`オブジェクトを返し、その`id`を記憶します。
3. 音声が終了すると、Asteriskはその再生`id`を含む`PlaybackFinished`を送信します。チャネルを検索して切断します。
4. 切断によりチャネルがStasisから離れ、`StasisEnd`イベントが生成されます。

> **クライアントライブラリに関する注意点。** `ari-py`（`ari`パッケージ）という高レベルのラッパーが存在しますが、これはメンテナンスされておらず、古い時代のPythonとSwaggerツール向けに書かれたものです。Asterisk 22での新しい作業には、上記で示した明示的な`requests` + WebSocketアプローチ、あるいは並行処理が必要な場合は`asyncari`のようなasyncioライブラリを推奨します。生の（raw）アプローチをとることで、実際のREST呼び出しやイベントに近い状態を維持でき、ARIを学習する際にはまさにそれが求められます。

## externalMedia: AIとボイスボットへの扉

上記のリソースでは「ファイル」の再生と録音しかできません。しかし、現代の音声アプリケーション（音声テキスト変換、AIボイスボット、リアルタイム分析）では、通話の「ライブ音声ストリーム」を外部プロセスに配信し、音声を注入し返す必要があります。

ARIは、**`externalMedia`チャネル**を通じてこれを提供します。`POST /ari/channels/externalMedia`リクエストは、電話と通信する代わりに、通話のRTPメディアを外部ホストへ（および外部ホストから）ストリーミングする特別なチャネルを作成します。このチャネルを発信者のチャネルとブリッジすることで、外部プログラムが音声パスに入ります。外部プログラムは発信者の音声をRTPとして受信し、合成音声を送り返すことができます。

リクエストに必要なのは以下のみです。

- `app`: 新しいチャネルを所有するStasisアプリケーション。
- `format`: 音声フォーマット（例: `ulaw`や`slin16`）。

`external_host`（メディアアプリケーションの`host:port`）はスキーマ上はオプションであり、WebSocketサーバー形式の接続であれば空でも構いませんが、古典的なRTPボイスボットの場合は指定します。`encapsulation`パラメータはデフォルトで`rtp`、そして`transport`は`udp`となり、これはストリーミングメディアエンドポイントとしてまさに望ましい設定です。

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

この単一の機能こそが、AsteriskをAIのフロントエンドに変えるものです。電話網はAsteriskで終端し、ARIが通話をオーケストレーションし、`externalMedia`が音声をAI/音声エンジンへパイプします。これが、AIサービスやボイスボットが構築されるメカニズムです。

## まとめ

ARIは、Asterisk 22上でテレフォニーアプリケーションを構築するための現代的で推奨されるインターフェースです。ARIは作業を明確に分割します。Asteriskはメディアエンジンであり、HTTPとWebSocket経由でJSONを話すアプリケーションが通話制御ロジックを提供します。ARIは`http.conf`（ポート8088の組み込みWebサーバー）と`ari.conf`（ARIをオンにしユーザーを定義する）を通じて有効にします。`Stasis()`ダイヤルプランアプリケーションはチャネルをアプリに引き渡し、入室時に`StasisStart`、退室時に`StasisEnd`を発生させます。そこから、チャネル、ブリッジ、再生、録音、endpoint、デバイス状態といった少数のRESTリソースを操作して、応答、再生、録音、ブリッジ、切断を行います。私たちは、通話に応答し、プロンプトを再生し、切断する最小限のPython Stasisアプリを構築し、`externalMedia`チャネルがライブRTPを外部プログラムにストリーミングする方法を確認しました。これはAIやボイスボット統合の基盤となります。

## クイズ

1. ARIはAsteriskのどのバージョンで導入されましたか？
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. ARIモデルにおいて、Asteriskはメディアエンジンとして機能し、外部アプリケーションが通話制御ロジックを提供します。
   - A. 正
   - B. 誤
3. ARIは2つのトランスポートを組み合わせて使用します。正しい組み合わせはどれですか？
   - A. コマンドを発行するためのREST/HTTP APIと、イベントを受信するためのWebSocketストリーム
   - B. TCP行プロトコルとstdin/stdoutスクリプト
   - C. SNMPとSMTP
   - D. 2つの独立したUDPソケット
4. ARIを有効にするために設定しなければならない2つの設定ファイルはどれですか？
   - A. `manager.conf`と`agi.conf`
   - B. `http.conf`と`ari.conf`
   - C. `sip.conf`と`rtp.conf`
   - D. `modules.conf`と`cdr.conf`
5. Asterisk HTTPサーバー（およびARI）の標準的なTCPポートは ____ です。
6. チャネルをARIアプリケーションに引き渡すダイヤルプランアプリケーションはどれですか？
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. チャネルがStasisアプリケーションに入ると、接続中のクライアントにどのイベントが送信されますか？
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. 2つ以上のチャネルを結合できるミキシングポイントを作成するARIリクエストはどれですか？
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. チャネル上で組み込みプロンプトを再生する際、音声が終了して次の処理に進めることをアプリケーションに伝えるイベントはどれですか？
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. `externalMedia`チャネルは主に何のために使用されますか？
    - A. 通話をローカルのWAVファイルに録音する
    - B. 通話のライブ音声（RTP）を外部アプリケーション（AI/音声エンジンなど）と送受信する
    - C. PJSIP endpointを登録する
    - D. ダイヤルプランをリロードする

**回答:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
