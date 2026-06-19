# ダイヤルプランの高度な機能

第3章では、ダイヤルプランの基礎について説明しました。教育的な理由から、すべての機能ではなく、最も重要な機能のみを取り上げました。本章ではダイヤルプランをさらに深く掘り下げ、高度なテクニック、新しいアプリケーション、そして概念について解説します。

## 学習目標

本章を読み終えることで、以下のことができるようになります。

- エクステンションの記述を簡素化する
- ダイヤルプランのセキュリティとエクステンションのフィルタリングに対処する
- IVRメニューを使用して着信を受ける
- サブルーチンを使用して不要な書き換えを避ける
- 「Include」を使用してダイヤルプランのセキュリティを実装する
- AsteriskDBを使用して「フォローミー（転送）」を実装する
- PBXで営業時間外の動作を実装する
- switchコマンドを使用して別のPBXへ転送する
- プライバシーマネージャーを実装する
- ボイスメールを実装する
- 企業ディレクトリを実装する

## ダイヤルプランの簡素化

「same」キーワードを使用することで、エクステンションの定義を簡素化できます。これにより、ダイヤルプラン内のタイプミスを減らすことができます。以下の例を確認してください。

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## ダイヤルプランのセキュリティ

Asteriskのダイヤルプランには、ユーザーが新しいチャネルを注入し、ダイヤルプラン内の番号をダイヤルできてしまうという脆弱性が発見されました。サーバーの `exten=>_X.,1,Dial(PJSIP/${EXTEN})` に以下の行があり、悪意のあるユーザーがソフトフォンで `3000&DAHDI/1/011551123456789` という番号をダイヤルしたと仮定します。SIPプロトコルはデフォルトで任意の英数字を受け入れるため、ダイヤルされたエクステンションは実際には2つの通話を引き起こします。1つはチャネル PJSIP/3000 への通話、もう1つは国際電話番号であるチャネル DAHDI/011551123456789 への通話です。このように、エクステンションにアクセスできるユーザーであれば誰でも、世界中のどこへでもダイヤルできてしまいます。この動作を回避する最も簡単な方法は、dialアプリケーションを呼び出す前に番号をフィルタリングすることです。FILTER() 関数は、この目的に非常に便利です。例：

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

このfilterアプリケーションを使用すると、ダイヤルされた番号から0から9までの数字以外のすべての文字をフィルタリングできます。詳細については、Asteriskで提供されている README-SERIOUSLY.bestpractices.txt ファイルを参照してください。

## IVRメニューを使用した着信の受信

前節では、DIDを使用するかオペレーターに転送することで、すべての着信を受けていました。ここでは、IVRメニューの実装方法と、自動応答サービスの作成方法を学びます。詳細に入る前に、いくつかの新しいアプリケーションを確認しましょう。読者が理解しやすいように、show applicationコマンドの出力を以下に記載します。これらの説明は show application application_name を使用して取得できます。 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### Background() アプリケーション

このアプリケーションは、呼び出し側のチャネルによってエクステンションがダイヤルされるのを待機している間、指定されたファイルリストを再生します。このアプリケーションがファイルの再生を終了した後も数字の入力を待ち続けるには、WaitExtenアプリケーションを使用する必要があります。langoverrideオプションは、要求された音声ファイルに使用する言語を明示的に指定します。指定されたコンテキストは、このアプリケーションがダイヤルされたエクステンションへ抜ける際に使用するダイヤルプランのコンテキストとなります。要求された音声ファイルが存在しない場合、通話処理は終了します。オプション：

- s - チャネルが「up」状態（つまり、まだ応答されていない）でない場合、メッセージの再生をスキップします。この場合、アプリケーションは直ちに終了します。
- n - ファイルを再生する前にチャネルに応答しません。
- m - 宛先コンテキスト内の1桁のエクステンションと一致する数字が入力された場合にのみ中断します。

### Record() アプリケーション

このアプリケーションは、チャネルから指定されたファイル名へ録音を行います。ファイルが存在する場合は上書きされます。

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' は録音するファイル形式（wav, gsmなど）です。
- 'silence' は、終了するまでに許容される無音の秒数です。
- 'maxduration' は最大録音時間（秒）です。省略または0の場合、制限はありません。
- 'options' には以下の文字を含めることができます：
    - `a` — 既存の録音を置き換えるのではなく、追記します
    - `n` — 応答していない場合でも、応答せずに録音します
    - `q` — 静音（ビープ音を鳴らさない）
    - `s` — 回線がまだ応答していない場合は録音をスキップします
    - `t` — デフォルトの `#` の代わりに、代替の `*` 終了キー（DTMF）を使用します
    - `x` — すべての終了キー（DTMF）を無視し、切断されるまで録音を続けます

ファイル名に %d が含まれている場合、ファイルが録音されるたびに、これらの文字は1ずつ増加する数字に置き換えられます。システムで使用可能な形式を確認するには、core show file formats を使用してください。ユーザーは # を押すことで録音を終了し、次の優先順位に進むことができます。録音中にユーザーが切断した場合、すべてのデータは失われ、アプリケーションは終了します。

### Playback() アプリケーション

このアプリケーションは、指定されたファイル名（拡張子は含めない）を再生します。パイプ記号の後にオプションを含めることもできます。'skip' オプションは、チャネルが「up」状態（つまり、まだ応答されていない）でない場合にメッセージの再生をスキップさせます。

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

'skip' が指定されている場合、チャネルがオフフック状態でなければアプリケーションは直ちに終了します。それ以外の場合、'noanswer' が指定されていない限り、音声が再生される前にチャネルが応答されます。すべてのチャネルがオンフック状態でメッセージを再生できるわけではありません。'j' が指定されている場合、ファイルが存在しないときに優先順位 n+101 にジャンプします。このアプリケーションは、完了時に以下のチャネル変数を設定します：

- PLAYBACKSTATUS — 再生試行のステータスを示すテキスト文字列。以下のいずれか：
    - `SUCCESS`
    - `FAILED`

### Read() アプリケーション

このアプリケーションは、ユーザーから指定された回数だけ、指定された桁数の文字列を読み取り、指定された変数に格納します。

- filename -- 数字やトーンを読み取る前に再生するファイル（iオプション使用時）
- maxdigits -- 許容される最大桁数。maxdigitsに達すると（ユーザーが # キーを押す必要なく）読み取りを停止します。デフォルトは0（制限なし）で、ユーザーが # キーを押すのを待ちます。0未満の値も同様です。最大値は255です。

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- オプションは `s`, `i`, `n` です：
    - `s` — 回線がアップしていない場合は直ちに終了します
    - `i` — filename を `indications.conf` からの通知トーンとして再生します
    - `n` — 回線がアップしていない場合でも数字を読み取ります
- attempts -- 1より大きい場合、データが入力されなかった場合に試行される回数
- timeout -- 数字の応答を待機する秒数（整数）。0より大きい場合、その値がデフォルトのタイムアウトを上書きします。

read() アプリケーションは、関数が失敗またはエラーになった場合に切断されるべきです。

### Gotoif() アプリケーション

このアプリケーションは、指定された条件の評価に基づいて、呼び出し側のチャネルをダイヤルプラン内の指定された場所へジャンプさせます。条件が真であれば labeliftrue へ、偽であれば 'labeliffalse' へと処理が続きます。ラベルは Goto アプリケーションで使用されるのと同じ構文で指定されます。条件によって選択されるラベルが省略された場合、ジャンプは行われず、ダイヤルプランの次の優先順位で実行が継続されます。

### ラボ：IVRメニューの段階的な構築

以下の機能を持つIVRメニューを作成しましょう。ダイヤルされると、IVRは「XYZコーポレーションへようこそ。営業の方は1を、技術サポートの方は2を、トレーニングの方は3を押してください。オペレーターに繋ぐ場合はそのままお待ちください」というメッセージの音声ファイルを再生します。数字によるルーティングは以下の通りです：

- `1` — 営業へ転送 (PJSIP/4001)
- `2` — 技術サポートへ転送 (PJSIP/4002)
- `3` — トレーニングへ転送 (PJSIP/4003)
- 数字が押されない場合 — オペレーターへ転送 (PJSIP/4000)

**ステップ 1 – プロンプトの録音**

プロンプトを録音するためのエクステンションを作成しましょう。プロンプトを録音するには、ソフトフォンから `9003<filename>` （例： `9003welcome` ）へダイヤルします。ビープ音が聞こえたら録音を開始し、 `#` を押して停止します。ビープ音が鳴り、システムが録音されたプロンプトを再生します。

**ステップ 2 – メニューロジックの作成**

9004エクステンションにダイヤルすると、処理は `s` エクステンションの優先順位1へジャンプします。

### ダイヤル中のマッチング

これは着信を受けるための企業向け設定メニューです。Backgroundアプリケーションは現在のコンテキストを読み取り、あらゆる可能な組み合わせに対して各番号の最大長を定義します。

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

この会社にダイヤルすると、最初にウェルカムメッセージが再生されます。その後、Asteriskは数字がダイヤルされるのを待ちます。ダイヤルされた番号に対するAsteriskのアクションは、即座に Dial(DAHDI/1) を呼び出す、タイムアウトを待ってから Dial(DAHDI/2) へ行く、即座に (DAHDI/3) を呼び出す、即座に Dial(DAHDI/4) を呼び出す、タイムアウトを待ってから切断する、即座に Dial(DAHDI/5) を呼び出す、即座に Dial(DAHDI/6) を呼び出す、即座に切断するなどです。メニュー内の曖昧さを避けることが重要です。誰もが素早く応答されたいと考えています。このため、2、21、22といった番号を使用すべきではありません。

### ラボ：Read() アプリケーションの使用

read() アプリケーションを使用したラボを試してください。Readはユーザーから数字を受け取り、指定された変数に挿入します。その後、gotoifアプリケーションを使用して通話をリダイレクトできます。

## コンテキストのインクルード

コンテキストには、別のコンテキストの内容を含めることができます。上記の例では、どのチャネルもinternalコンテキスト内の任意のエクステンションにダイヤルできますが、4003チャネルのみが国際エクステンションにダイヤルできます。コンテキストのインクルードを使用すると、ダイヤルプランの作成が容易になります。コンテキストのインクルードを使用することで、誰がどのエクステンションにアクセスできるかを制御できます。

### 「number not found」メッセージのトラブルシューティング

「number not found」というメッセージを受け取ることは非常によくあります。インクルードされたコンテキストの概念は直感的ではないため、多くの人が混乱します。経験則として、まず `pjsip.conf` 、 `chan_dahdi.conf` 、 `iax.conf` などの着信チャネル設定ファイルに移動し、現在のコンテキストを確認してください。次に、extensions.conf ファイルのダイヤルプランに移動し、ダイヤルされた番号がそのコンテキストで見つかるかどうかを確認します。見つからない場合は、ダイヤルプランに問題があります。コンテキストの黄金律は以下の通りです：1. チャネルは、そのチャネルと同じコンテキスト内の番号にしかダイヤルできない。2. 通話が処理されるコンテキストは、着信チャネル設定ファイル（ `chan_dahdi.conf` 、 `iax.conf` 、 `pjsip.conf` ）で定義される。

## switchステートメントの使用

switchコマンドを使用して、ダイヤルプランの処理を別のサーバーに送信できます。その際、相手サーバーの名前とキーが必要です。コンテキストは宛先のコンテキストです。

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## ダイヤルプランの処理順序

Asteriskが着信を受けると、チャネルによって定義されたコンテキスト内を検索します。場合によっては、複数のパターンがダイヤルされた番号と一致し、Asteriskが意図した通りに処理できないことがあります。マッチング順序は dialplan show CLIコマンドを使用して確認できます。例：912をダイヤルしてアナログトランク（DAHDI/1）にルーティングし、9で始まる他のすべての番号を別のアナログトランク（DAHDI/2）にルーティングしたい場合、以下のように記述します：

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

2つのパターンがエクステンションに一致する場合、インクルードされたコンテキストを使用して、どのエクステンションが先に処理されるかを制御できます。インクルードされたコンテキストは、同じコンテキスト内のパターンよりも後に処理されます。

## #INCLUDE ステートメント

大きなファイルを1つ使うべきか、複数のファイルに分けるべきでしょうか？ #include <filename> ステートメントを使用して、extensions.conf に他のファイルを含めることができます。例えば、ローカルユーザー用に users.conf を、特別なサービス用に services.conf を作成できます。#include <filename> と

```
include=>context statement.
```

を混同しないように注意してください。

## GOSUB を使用したサブルーチン

古いバージョンのAsteriskにはMacroコマンドがありました。このコマンドは、GOSUBを優先するためにずっと前に非推奨となりました。ここでは、ボイスメール処理用のサブルーチンを簡単かつ秩序立てて作成する方法を説明します。コマンド形式：

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

GOSUBコマンドはAsterisk 1.6から利用可能で、引数の受け渡し（サブルーチン内では `${ARG1}` 、 `${ARG2}` などとして利用可能）をサポートしています。引数を使用することで、古いMacroコマンドを完全に置き換えることが可能になりました。マクロ（ `app_macro` ）はAsterisk 21で削除されました。サブルーチンにはGOSUBを使用しなければなりません。

### サブルーチンの作成

定義は非常に似ています。ボイスメール用にstdextenという名前（好きな名前を選んでください）で定義された以下のサブルーチンを見てください。最初の引数（チャネル名）でDialコマンドを呼び出した後、${DIALSTATUS} をチェックして、通話ロジックを次のステップへ送ります。

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### サブルーチンの呼び出し

サブルーチンを呼び出す際は、パラメータの前に括弧を使用することに注意してください。

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Asterisk DB の使用

コール転送やブラックリストを実装するには、データを保存および復元する方法が必要です。幸いなことに、AsteriskにはAstDBと呼ばれる組み込みデータベースからデータを保存および取得するメカニズムが用意されています。最新のAsterisk（Asterisk 22を含む）では、AstDBは **SQLite3** （ファイル `/var/lib/asterisk/astdb.sqlite3` ）によってバックアップされています。古いバージョンではBerkeley DB v1が使用されていました。これは、ファミリーとキーの階層概念を使用するWindowsレジストリデータベースに似ています。データはAsteriskの再起動後も保持されます。

> **[2nd-ed note]** Asterisk 10以降、AstDBはAsterisk 1.8以前で使用されていたレガシーなBerkeley DB v1ファイルではなく、SQLite3（ `astdb.sqlite3` ）に保存されています。ファミリー/キーAPIに変更はありません。

### 関数、アプリケーション、およびCLIコマンド

AstDBで動作する関数、アプリケーション、およびCLIコマンドがいくつかあります：

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

例：

```
exten=_*21*XXXX,1,set(DB(CFBS/${CALLERID(num)}=${EXTEN:4}))
exten=s,1,set(temp=${DB(CFBS/${EXTEN})})
```

一部のアプリケーションはAstDBを操作するために使用できます：

- DB_DELETE(<family/key>) — キーを返して削除する関数（古い `DBdel()` アプリケーションは削除されました）
- DBdeltree(<family>)

> **[2nd-ed note]** `DBdel()` アプリケーションはAsterisk 22には存在しません。単一のキーを削除するには `DB_DELETE()` ダイヤルプラン関数を使用してください（例： `Set(x=${DB_DELETE(family/key)})` 、または書き込み操作として `Set(DB_DELETE(family/key)=)` ）。 `DBdeltree()` （ファミリー/サブツリー全体を削除）は依然としてアプリケーションです。

CLIコマンドを使用してキーを設定および削除することも可能です：

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### コール転送、DND、ブラックリストの実装

この例では、即時転送と話中転送の実装方法を学びます。即時転送のプログラムには *21* を、話中転送のプログラムには *61* を使用します。プログラムをキャンセルするには、それぞれ #21# と #61# を使用します。データベースにデータを入力するには、上記の例を使用してください。使用するファミリー：

- CFIM – 即時転送 (Call Forward Immediate)
- CFBS – 話中転送 (Call Forward on Busy status)
- DND – おやすみモード (Do Not Disturb)

以下をダイヤルしてデータベースにデータを入力してみてください：

- *21* （即時転送の宛先エクステンション）
- *61* （話中転送の宛先エクステンション）
- *41* （おやすみモードにするエクステンション）

CLIコマンド database show を使用して、追加されたファミリー、キー、値を確認してください。

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### コール転送、ブラックリスト、DND

上記のサブルーチンは、データベースにCFIM、CFBS、またはDNDに対応するキー:値のペアが含まれているかどうかを確認し、それに応じて処理します。followサブルーチンはダイヤルルーチンを呼び出します：

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## ブラックリストの使用

> **[2nd-ed note]** `LookupBlacklist()` アプリケーションは **削除されました** （Asterisk 22よりずっと前に、古い「priority+101ジャンプ」メカニズムと共に消滅しました。22.10.0ラボで登録されていないことを確認済み）。代わりに `DB()` / `DB_EXISTS()` 関数と `GotoIf` を使用してブラックリストを実装してください。例：
>
> ```
> exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
> exten => s,n,Dial(PJSIP/4000,20,tT)
> exten => s,n,Hangup()
> ```
>
> 以下の例は歴史的な参照のために残されています。 `j` オプションと `n+101` 優先順位ジャンプはもう存在しません。

ブラックリストを作成するには、LookupBlacklist() アプリケーションを使用します。このアプリケーションは、発信者IDの名前/番号をチェックします。番号が見つからない場合、アプリケーションは変数 $LOOKUPBLSTATUS を NOTFOUND に設定します。番号が見つかった場合、アプリケーションは変数を FOUND に設定します。アプリケーションの「j」オプションを使用すると、古い（1.0）動作を利用でき、番号/名前が見つかった場合に101ポジションジャンプします。例：

```
[incoming]
exten => s,1,LookupBlacklist(j)
exten => s,2,Dial(PJSIP/4000,20,tTj)
exten => s,3,Hangup()
exten => s,102,Goto(blocked,s,1)
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

ブラックリストに番号を挿入するには、以前と同じリソースを使用し、*31* に続いてブラックリストに登録するエクステンションを入力します。ブラックリストから番号を削除するには、#31# に続いて削除する番号を入力する必要があります。

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN}=1})
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

コンソールCLIを使用してブラックリストに番号を挿入することもできます：

```
CLI>database put blacklist <name/number> 1
```

注：キーには任意の値が関連付けられます。ブラックリストアプリケーションは値ではなくキーを検索します。ブラックリストから番号を消去するには、以下を使用できます：

```
CLI>database del blacklist <name/number>
```

## 時間ベースのコンテキスト

以下の図では、3つのコンテキストを持つダイヤルプランを示しています。[incoming] コンテキストは、通常通話が着信する場所です。以下のように、システム時刻に応じて動作を変更する4つの行を含めています：

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

> **[2nd-ed note]** 最新のAsterisk（22を含む）では、時間インクルードフィールドはパイプではなく **カンマ** で区切ります。レガシーなパイプ形式（ `include => context|times|weekdays|mdays|months` ）はプレーンなリテラルのコンテキスト名として解析され、時間条件は適用されずに黙って失敗します。Asterisk 22.10.0ラボで検証済み。

通常の営業時間中、処理はmainmenuへリダイレクトされ、そこでIVRを呼び出して着信を処理します。営業時間外に着信があった場合は、${SECURITY} 変数で定義されたセキュリティエクステンションを呼び出します。セキュリティエクステンションが応答しない場合は、オペレーターのボイスメールに送信されます。

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## gotoiftime() を使用した時間ベースのメッセージ

gotoiftime() の構文を以下に示します。

```
GotoIfTime(<timerange>,<daysofweek>,<daysofmonth>,<months>[,<timezone>]?[[context,]extension,]pri)
```

> **[2nd-ed note]** Asterisk 22では、フィールド区切り文字はパイプではなく **カンマ** です（パイプ形式はAsterisk 1.6で非推奨となりました）。現在文書化されている構文は `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])` です。オプションの `timezone` フィールドがサポートされています。

このアプリケーションは時間ベースのコンテキストを置き換えることができ、理解しやすく読みやすいようです。時間は以下のように指定できます：

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=1から31までの数字
- <hour>=0から23までの数字
- <minute>=0から59までの数字
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

曜日と月の名前は大文字と小文字を区別しません。

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

上記のステートメントは、月曜日から金曜日の午前08:00から午後06:00の間に通話があった場合、処理をnormalhoursコンテキストのエクステンションsへ転送します。

## DISAを使用して新しいダイヤルトーンを取得する

DISA（「Direct Inward System Access」）は、ユーザーが2番目のダイヤルトーンを受け取れるようにするシステムです。これにより、ユーザーは別の宛先へ再度ダイヤルできます。これは、週末に技術サポートのために長距離電話をかける際、技術者によってよく使用されます。自宅から直接宛先にダイヤルする代わりに、会社のDISA番号に電話をかけ、ダイヤルトーンを受け取ってから宛先に電話をかけます。長距離料金は自宅の電話ではなく会社に発生します。

```
DISA(passcode[,context])
DISA(password-file[,context])
```

例：

```
exten => s,1,DISA(no-password,default)
```

上記のステートメントを使用すると、ユーザーはPBXにダイヤルし、パスワードを必要とせずにダイヤルトーンを受け取ります。DISAを使用した通話はすべて `default` コンテキストを使用して処理されます。このアプリケーションの引数には、グローバルパスワードまたはファイル内の個別のパスワードが含まれます。コンテキストが指定されていない場合は、 `disa` コンテキストが想定されます。パスワードファイルを使用する場合は、完全なパスを指定する必要があります。DISA外部ダイヤル用に発信者IDを指定することも可能です。例：

```
numeric-passcode,context,"Flavio" <4830258590>
```

> **[2nd-ed note]** Asterisk 22は引数の区切り文字としてカンマを使用します（パイプ形式は1.6で非推奨となりました）。完全な構文は `DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])` であり、何も指定されていない場合のデフォルトコンテキストは 「DISA」 ではなく `disa` です。Asterisk 22.10.0ラボで `core show application DISA` を使用して検証済み。

## 同時通話の制限

GROUP() 関数を使用すると、同時に1つのグループ内にアクティブなチャネルがいくつあるかをカウントできます。例：リオデジャネイロに支店があり、電話が「_214X」というパターンに従っているとします。この場所は専用線でサービスされており、音声帯域幅として64Kが予約されています。この場合、許可される最大通話数は2です（G.729、1通話あたり30r.2K）。リオへの通話を2つに制限するには：

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## ボイスメール

ボイスメールは、着信した音声メッセージを録音し、ディスクに保存したり電子メールで送信したりするコンピュータ化された電話応答システムです。名前でボイスメールボックスを検索できるディレクトリ機能を持つこともあります。かつて、ボイスメールシステムは非常に高価でした。現在、IPテレフォニーの普及により、ボイスメールは標準機能になりつつあります。

ボイスメールを設定するには、以下の手順を実行する必要があります。

**ステップ 1: `voicemail.conf` を編集し、一般的なパラメータを設定します。**

- `format` — メッセージの録音に使用するコーデック（例：wav49, wav, gsm）
- `serveremail` — 電子メール通知の送信元として表示されるアドレス
- `maxmsg` — メールボックス内の最大メッセージ数。このしきい値を超えると、メッセージは破棄されます
- `maxsecs` — ボイスメールメッセージの最大長（秒）
- `minsecs` — メッセージの最小長（秒）。このしきい値を下回ると、メッセージは録音されません
- `maxsilence` — メッセージの終了とみなす無音の秒数

**ステップ 2: `voicemail.conf` を編集し、ユーザーのメールボックスを作成します。**

### Voicemail.conf

メールボックスは、1行につき1つのメールボックスとして、以下の形式で定義されます：

```
mailboxID => pincode,fullname,email,pager-email,options
```

フィールドは以下の通りです：

- **MailboxID** — 通常はエクステンション番号
- **Pincode** — ボイスメールシステムにアクセスするためのパスワード
- **Full name** — ディレクトリアプリケーションで使用されます
- **E-mail** — ボイスメール通知用のアドレス
- **Pager e-mail** — SMSゲートウェイまたはポケットベル経由の通知用アドレス
- **Options** — メールボックスごとのオプション（ `[general]` と同じオプションですが、このメールボックスに適用されます）

ボイスメールには、その動作を制御するいくつかのオプションがあります。今のところはデフォルトのオプションを使用し、メールボックスの定義に集中します。ファイル内の `[general]` セクションの後、各コンテキスト内でメールボックスIDの設定を開始します。例：

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

高度なオプションについては、 `voicemail.conf` ファイルを確認してください。

**ステップ 3: `extensions.conf` ファイルを設定します。**

以下に、 `extensions.conf` でボイスメールを実装するサブルーチンと呼び出しを作成するための手順を示します。チャネル変数 `${DIALSTATUS}` の値を使用して、通話フローを適切なボイスメールメニューへリダイレクトします。

### ボイスメールサブルーチン

## Voicemailmain() アプリケーションの使用

voicemailmain() アプリケーションは、ボイスメールボックスを設定するために使用されます。ユーザーはこのアプリケーションにダイヤルし、挨拶を録音したり、ボイスメールを聞いたりできます。ダイヤルプランでこのアプリケーションを呼び出すには、以下を使用します：

```
exten=>9000,1,VoiceMailMain()
```

以下に、このアプリケーションで利用可能なオプションのリストを示します。

### Voicemail アプリケーションの構文

このアプリケーションを使用すると、呼び出し側は指定されたメールボックスリストにメッセージを残すことができます。複数のメールボックスが指定された場合、挨拶は最初に指定されたメールボックスから取得されます。指定されたメールボックスが存在しない場合、ダイヤルプランの実行は停止します。構文を以下に示します：

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

すべての場合において、録音が開始される前に beep.gsm ファイルが再生されます。ボイスメールメッセージは inbox ディレクトリに保存されます。

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

アナウンス中に発信者が 0 を押すと、ボイスメールの現在のコンテキストにある「o」（out）エクステンションへ移動します。これはオペレーターへ抜けるために使用できます。録音中に発信者が # を押すか、無音制限時間が経過すると、録音は停止し、通話は次の優先順位へ進みます。以下に示すように、ボイスメールが再生された後の通話を必ず処理するようにしてください。

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### ボイスメールメッセージの緊急タグ付け

一部のメッセージを「緊急」としてタグ付けできます。これには2つの方法があります：

- voicemail() アプリケーションで 'U' オプションを渡す
- voicemail.conf ファイルで review=yes を指定する。このオプションを使用すると、ユーザーは音声指示を録音した後、メッセージを緊急としてタグ付けできるようになります。

## ボイスメールの電子メール送信

（私のように）ボイスメールmain() アプリケーションを使用してメールを読むことをしない場合もあります。すべてのメッセージを音声付きで電子メールに送信する方が、よりシンプルで実用的です。'attach' および 'delete' パラメータを使用すると、すべてのメールを電子メールに送信し、メールボックスから削除できます。

```
attach=yes
delete=yes
```

ボイスメールを電子メールに送信するために、ボイスメールアプリケーションはオペレーティングシステムのコンポーネントであるメッセージ転送エージェント（MTA）を使用します。DebianはMTAとしてEximを使用します。電子メールを送信するアプリケーションは 'mailcmd' パラメータで定義されます。

```
mailcmd =/usr/sbin/sendmail -t
```

LinuxのDebianディストリビューションでは、MTAはEximです。DebianでEximを設定するには、以下を使用します：

```
dpkg-reconfigure exim4-config
```

MTAがSMTP経由で直接電子メールを送信するか、スマートホスト（通常は会社のメールサーバー）経由で送信するかを選択できます。Asteriskサーバーから電子メールサーバーへ電子メールを送信する最適な方法については、電子メール管理者に確認してください。

## 電子メールメッセージのカスタマイズ

以下の変数を設定することで、メッセージの送信方法を制御できます。電子メールの件名と本文用の変数：

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

電子メールの本文と件名は、 `voicemail.conf` の `[general]` セクションで設定するテンプレートから構築されます。本文と件名の両方を変更できますが、メッセージのサイズ制限は512バイトです。テンプレート内では、 `\n` が改行を挿入し、 `\t` がタブを挿入します。

以下の `emailsubject` の例は単純明快です。 `emailbody` の例はデフォルトに非常に近く、デフォルトではCIDNAMEがnullでない場合はそれのみを表示し、そうでない場合はCIDNUMを、両方がnullの場合は「an unknown caller」を表示します。

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## ボイスメールWebインターフェース

ソース配布物には `vmail.cgi` というPerlスクリプトが含まれており、Asteriskソースツリーの `contrib/scripts/vmail.cgi` に配置されています（Asterisk 22にも同梱されています）。 `make install` コマンドはこのインターフェースをインストールしません。ソースディレクトリから `make webvmail` を実行する必要があります。このスクリプトには、PerlコマンドインタープリタとWebサーバー（Apacheなど）がサーバーにインストールされている必要があります。

```
make webvmail
```

`make webvmail` ターゲットは、スクリプトをWebサーバーのCGIディレクトリ（ `HTTP_CGIDIR` ）に（setuid rootで）インストールし、サポート画像を `images/*.gif` から `HTTP_DOCSDIR/_asterisk` （デフォルトは `/var/www/html/_asterisk` ）にコピーします。これらのパスがWebサーバーのレイアウトと一致しない場合は、ターゲットを実行する前に最上位の `Makefile` にある `HTTP_CGIDIR` および `HTTP_DOCSDIR` 変数を編集してください。

## ボイスメール通知

新しいボイスメールがあるときに電話へ通知メッセージを送信するようにボイスメールを設定できます。Asterisk 22では、メッセージ待機表示（MWI）はPJSIPおよびSIP電話、さらにDAHDI電話で動作します。未読のボイスメールを示すために、インジケーターライトが点滅したり、電話がシャッター音を鳴らしたりすることがあります。対応するチャネル設定ファイルでメールボックスを設定する必要があります。例： `pjsip.conf` （エンドポイントセクション内）：

```
mailboxes=8590
```

> **[2nd-ed note]** PJSIPでは、メールボックスヒントは `mailbox=` （ `sip.conf` 内）ではなく、 `pjsip.conf` の `[endpoint]` セクション内の `mailboxes` オプションで設定されます。MWIサブスクリプションは `res_pjsip_mwi` によって処理されます。Asterisk 22の正確な設定構文を確認してください。

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### ラボ：電話機でのメッセージ通知

このラボはSIPソフトフォンを使用してテストされました。 1. `pjsip.conf` を編集し、デバイス名4401のエンドポイントセクションに `mailboxes=4401` を追加します。 2. extensions.conf を編集し、4401エクステンションへのボイスメールを録音するエクステンションを作成します。

```
exten=9008,n,voicemail(b4401)
```

3. CLI > コンソールに移動し、リロードします。 4. SipPulseソフトフォンで、SIPアカウント設定を開き、アカウントのボイスメール（メッセージ待機）チェックを有効にします。 5. 9008にダイヤルし、メッセージを残します。 6. 電話機のメッセージアイコンを確認します。

## directory アプリケーションの使用

このアプリケーションを使用すると、ダイヤルするユーザーを素早く見つけることができます。名前と対応するエクステンションのリストは、ボイスメール設定ファイル voicemail.conf から取得されます。アプリケーションの構文は core show application directory を使用して表示できます：

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### ラボ：directory アプリケーションの使用

1. voicemail.conf ファイルを編集し、ダイヤルプランに2つのエクステンションを追加します

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. ダイヤルプランにこれらのエクステンションを作成します

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. コンソールに移動し、リロードします 4. 9006にダイヤルし、各エクステンション（4400, 4401）の名前を録音します 5. 9007にダイヤルし、1つのエクステンションの姓の最初の3文字を選択します（Eas=327）。これが正しいオプションであれば、「1」を押してその名前へ転送します。

## ラボ：すべてをまとめる

これまでに、いくつかのダイヤルプランの概念を学びました。それらがどのように組み合わされるかを理解できるように、ダイヤルプランの例ですべてのアプリケーション、関数、概念をまとめてみましょう。以下のシナリオのPBX設定全体をガイドします。

- 4つのアナログトランク
- 16のSIPベースのエクステンション
- 3つのサービスクラス：
    - restrict（内部、市内、1-800）
    - ld（長距離）
    - ldi（国際）
- 営業時間外メッセージ
- 自動応答

### ステップ 1 – チャネルの設定

アナログトランク（chan_dahdi.conf） まず、DAHDIチャネル設定ファイル chan_dahdi.conf でアナログトランクを設定します。この場合、4つのFXOインターフェースを持つT400P Digiumカードを使用します。ドライバーはすでにロードされており、ドライバー設定ファイル（/etc/dahdi/system.conf）が正しく設定されていると仮定します。

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

SIPチャネル（pjsip.conf） ダイヤルプランの番号付けは2000から2099を選択しました。G.729とG.711 ulawの2つのコーデックを使用します。前者はインターネットまたはWAN経由でAsteriskを使用する電話機用、後者はローカルネットワークを使用する電話機用です。 `pjsip.conf` では、どのデバイスがどのサービスクラス（restrict, ld, ldi）に属するかを決定します。ブルートフォース攻撃への脆弱性を減らすため、電話機のMACアドレスをデバイス名として使用します。ブルートフォース攻撃を避けるため、強力なパスワードを使用することを強くお勧めします！

トランスポートと3つの再利用可能なテンプレート（共有コーデックを持つエンドポイントベース、userpass認証、単一連絡先AOR）を定義し、各デバイスをテンプレートにアタッチして、異なる部分（サービスクラスのコンテキストと資格情報）のみを上書きします。 `host=dynamic` は電話機が登録するAORとなり、 `directmedia` は `direct_media` となります：

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-userpass](!)
type=auth
auth_type=userpass

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-userpass)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-userpass)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-userpass)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### ステップ 2 – ダイヤルプランの設定

次に、extensions.conf の設定を開始します。内部エクステンションと市内ダイヤルを定義します

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

LD（長距離）を定義します

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

国際電話を定義します

```
[ldi)
include=> ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### ステップ 3 - 自動応答を使用した着信の受信

着信を受けるには、2つのコンテキストを使用します。1つ目は通常営業時間用で、通話は自動応答によって受け取られます。2つ目は営業時間外用で、発信者は「XYZ会社にお電話ありがとうございます。当社の通常営業時間は午前08:00から午後06:00です。宛先のエクステンション番号をご存知の場合は、今すぐダイヤルするか、切断してください」といったメッセージを受け取ります。メニュー：通常営業時間、営業時間外。以下のメニューでは、システムは会社が通常営業時間外に連絡されたことを警告するメッセージを再生し、発信者が宛先のエクステンション番号をダイヤルできるようにします（通常営業時間外に誰かが働いている可能性があります）。

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

メニュー：メインおよび営業。通常営業時間中、通話は自動応答メニューによって応答され、「XYZ会社へようこそ。営業の方は1を、技術サポートの方は2を、トレーニングの方は3を、またはご希望のエクステンション番号をダイヤルしてください」といったメッセージを受け取ります。

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

これらのステートメントにより、ダイヤルプランの機能は準備完了です。次のセクションでは、PBXの操作方法を説明します。

## まとめ

本章では、IVRや自動応答を使用して着信を受ける方法を学びました。コンテキストのインクルードの概念を学習し、いくつかの例を実装しました。繰り返し入力を避けるためにサブルーチンを使用し、データ保存が必要な機能（コール転送、おやすみモード、ブラックリストなど）にはBerkley DBエンジンに基づくAsteriskデータベースを使用しました。最後に、営業時間外の動作を実装する方法を学び、これらの概念を使用して完全なダイヤルプランを実装しました。

## クイズ

1. 時間依存のコンテキストインクルードは `include => context,<times>,<weekdays>,<mdays>,<months>` という形式を使用します。 `include => normalhours,08:00-18:00,mon-fri,*,*` は何をしますか？
   - A. 月曜日から金曜日の08:00から18:00にエクステンションを実行する
   - B. すべての月の毎日オプションを実行する
   - C. 何もしない。形式が無効である
2. 最新のAsterisk（Asterisk 22を含む）では、時間ベースの `include =>` と `GotoIfTime()` のフィールドはどの文字で区切られますか？
   - A. パイプ `|`
   - B. カンマ `,`
   - C. セミコロン `;`
   - D. スラッシュ `/`
3. 複数のチャネルを一度にダイヤルする（同時に鳴らす）には、 `Dial()` 内で ___ 文字を使用してそれらを区切ります。
4. 発信者がエクステンションをダイヤルするのを待機している間にプロンプトを再生する音声メニューは、通常 ___ アプリケーションで作成されます。
5. ___ ステートメントを使用して、別のファイルの内容を `extensions.conf` 内に含めることができます（注：これは `include =>` コンテキストステートメントとは異なります）。
6. Asterisk 22では、組み込みのAstDBデータベースは以下によってバックアップされています：
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. `Dial(type1/identifier1&type2/identifier2)` を使用すると、Asteriskは各チャネルを順番にダイヤルし、それらの間で20秒間待機します。
   - A. 偽
   - B. 真
8. Background() アプリケーションでは、オプションを選択するためにDTMF数字を押す前に、メッセージの再生が終了するまで待たなければなりません。
   - A. 偽
   - B. 真
9. 構文 `Goto([[context,]extension,]priority)` が与えられた場合、Goto() アプリケーションの有効な呼び出しはどれですか？（該当するものすべてにマークしてください）
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Asterisk 22ダイヤルプランでAstDBから単一のキーを削除するには、以下を使用します：
    - A. `DBdel()` アプリケーション
    - B. `DB_DELETE()` 関数
    - C. `DBdeltree()` アプリケーション
    - D. `LookupBlacklist()` アプリケーション

**回答:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
