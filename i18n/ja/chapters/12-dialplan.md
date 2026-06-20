# ダイヤルプラン高度機能

Chapter 3 ではダイヤルプランの基本について説明しました。教育上の理由から、すべての機能を解説したわけではなく、最も重要なものだけを取り上げました。本章ではダイヤルプランをさらに掘り下げ、上級テクニックや新しいアプリケーション、概念について詳述します。

## 目的

この章の終わりまでに、次のことができるようになります：

- 拡張エントリを簡素化する
- ダイヤルプランのセキュリティと拡張のフィルタリングに対処する
- IVR メニューを使用して着信を受け取る
- 不要な書き換えを避けるためにサブルーチンを使用する
- “Include” を使用したダイヤルプランのセキュリティを実装する
- AsteriskDB を使用したフォローミーを実装する
- 勤務時間外の動作を PBX に実装する
- switch コマンドを使用して別の PBX に転送する
- プライバシーマネージャーを実装する
- ボイスメールを実装する
- 社内ディレクトリを実装する

## ダイヤルプランの簡素化

ダイヤルプランを簡素化するには、キーワード “same” を使用してエクステンションを定義します。これにより、ダイヤルプラン内のタイプミスの数が減少するはずです。以下の例をご確認ください：

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Dial Plan Security

Asterisk のダイヤルプランに、ユーザーが新しいチャネルとダイヤル番号をインジェクトできる欠陥が発見されました。サーバーに `exten=>_X.,1,Dial(PJSIP/${EXTEN})` という行があり、悪意のあるユーザーがソフトフォンで番号 `3000&DAHDI/1/011551123456789` をダイヤルしたとします。SIP プロトコルはデフォルトで任意の英数字を受け付けるため、ダイヤルされた内線は実際には 2 つの呼び出しをトリガーします。1 つはチャネル PJSIP/3000、もう 1 つは国際番号であるチャネル DAHDI/011551123456789 です。したがって、内線へのアクセス権を持つユーザーは実質的に世界中のどこへでも電話をかけることができます。この動作を回避する最も簡単な方法は、dial アプリケーションを呼び出す前に番号をフィルタリングすることです。関数 FILTER() が非常に便利です。例:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

filter アプリケーションは、ダイヤルされた番号から 0 から 9 までの数字以外のすべての文字を除去できます。詳細は、Asterisk から入手可能な README‑SERIOUSLY.bestpractices.txt ファイルをご参照ください。

## IVR メニューを使用した着信の受信。

前のセクションでは、DID またはオペレーターへの転送で全ての着信を受け取っていました。ここでは、IVR メニューの実装方法と自動応答サービスの作成方法を学びます。具体的な内容に入る前に、新しいアプリケーションをいくつか確認しておきましょう。読者の利便性を考えて、コマンド `core show application` の出力を以下に示しています。これらの説明は、`core show application <application_name>` を使用して自分でも取得できます。

### Background() アプリケーション

このアプリケーションは、呼び出し元チャネルが番号をダイヤルするのを待ちながら、指定されたファイルのリストを再生します。このアプリケーションの再生が終了した後も数字の入力待ちを続けるには、`WaitExten` アプリケーションを使用する必要があります。`langoverride` オプションは、要求されたサウンドファイルに使用する言語を明示的に指定します。指定されたコンテキストは、ダイヤルされたエクステンションに退出する際にこのアプリケーションが使用するダイヤルプランコンテキストとなります。要求されたサウンドファイルのいずれかが存在しない場合、コール処理は終了します。Options:

- s - チャネルが「up」状態でない場合（つまり、まだ応答されていない場合）にメッセージの再生をスキップさせます。この場合、アプリケーションは直ちに戻ります。  
- n - ファイルを再生する前にチャネルに応答しません。  
- m - 入力された数字が宛先コンテキストの1桁エクステンションと一致したときだけブレークします。

### Record() アプリケーション

このアプリケーションは、チャンネルから指定されたファイル名に録音します。ファイルが既に存在する場合、上書きされます。

![10-ダイヤルプラン高度機能 図 1](../images/10-dialplan-advanced-features-img01.png)

- ‘format’ は記録するファイルタイプの形式です（wav、gsm など）。
- ‘silence’ は、戻るまでに許容される無音の秒数です。
- ‘maxduration’ は最大録音時間（秒）です。省略または 0 の場合、最大時間はありません。
- ‘options’ には以下の文字のいずれかを含めることができます:
    - `a` — 既存の録音に追加し、置き換えません
    - `n` — 応答しないが、ラインがまだ応答されていなくても録音します
    - `q` — 静かに（ビープ音を鳴らさない）
    - `s` — ラインがまだ応答されていない場合は録音をスキップします
    - `t` — デフォルトの`#`の代わりに代替の`*`終端キー（DTMF）を使用します
    - `x` — すべての終端キー（DTMF）を無視し、ハングアップするまで録音し続けます

If filename contains %d, these characters will be replaced with a number incremented by one each time the file is recorded. Use core show file formats to see the available formats on your system. The user can press # to terminate the recording and continue to the next priority. If the user hangs up during a recording, all data will be lost and the application will terminate.

### Playback() アプリケーション

このアプリケーションは指定されたファイル名（拡張子は含めない）を再生します。パイプ記号の後にオプションを付けることもできます。'skip' オプションは、チャネルが 'up' 状態でない場合（つまり、まだ応答されていない場合）にメッセージの再生をスキップさせます。

![10-dialplan-advanced-features 図 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features 図 3](../images/10-dialplan-advanced-features-img03.png)

もし `skip` が指定されている場合、チャンネルがフックオフ状態でないときはアプリケーションは直ちに戻ります。`noanswer` が指定されていない限り、サウンドが再生される前にチャンネルは応答されます。すべてのチャンネルがフックオンのままでメッセージを再生できるわけではありません。`j` が指定されている場合、ファイルが存在しないときに（存在する場合）アプリケーションは優先度 n+101 にジャンプします。このアプリケーションは完了時に次のチャンネル変数を設定します：

- PLAYBACKSTATUS — 再生試行のステータスをテキスト文字列で表したもので、次のいずれかです:
    - `SUCCESS`
    - `FAILED`

### Read() アプリケーション

このアプリケーションは、ユーザーから指定された変数へ、事前に決められた数の文字列数字を、所定回数読み取ります。

- filename -- オプション i で数字またはトーンを読み取る前に再生するファイル
- maxdigits -- 許容できる最大桁数。maxdigits が入力されると読み取りを停止します（ユーザーが # キーを押す必要はありません）。デフォルトは 0 で、制限なし（ユーザーが # キーを押すまで待ちます）。0 未満の値も同様の意味です。許容される最大値は 255 です。

![10-ダイヤルプラン-高度機能 図 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features 図 5](../images/10-dialplan-advanced-features-img05.png)

- option -- options are `s`, `i`, `n`:
    - `s` — 回線がアップしていない場合は直ちに戻ります
    - `i` — `indications.conf`からインジケーショントーンとしてファイル名を再生します
    - `n` — 回線がアップしていなくても数字を読み取ります
- attempts -- 1 より大きい場合、データが入力されなかったときに行われる試行回数
- timeout -- デジット応答を待つ秒数の整数です。0 より大きい場合、その値がデフォルトのタイムアウトを上書きします。

The read() アプリケーションは、関数が失敗したりエラーが発生した場合に切断すべきです。

### Gotoif() アプリケーション

このアプリケーションは、指定された条件の評価に基づいて、呼び出しチャンネルをダイヤルプラン内の指定された位置へジャンプさせます。条件が真の場合は labeliftrue に、偽の場合は 'labeliffalse' に続きます。ラベルは Goto アプリケーションで使用されるのと同じ構文で指定します。条件によって選択されたラベルが省略された場合、ジャンプは行われず、ダイヤルプランの次のプライオリティで実行が続行されます。

### Lab: IVR メニューをステップバイステップで構築

IVRメニューを次の機能で作成しましょう。ダイヤルされたとき、IVRは音声ファイルを再生し、メッセージ「Welcome to the XYZ Corporation; press 1 for sales, 2 for tech support, 3 for training, or wait to speak to a representative.」を流します。数字は発信者を次のようにルーティングします：

- `1` — 営業へ転送 (PJSIP/4001)
- `2` — テクニカルサポートへ転送 (PJSIP/4002)
- `3` — トレーニングへ転送 (PJSIP/4003)
- 数字が押されなかった場合 — オペレーターへ転送 (PJSIP/4000)

**ステップ1 – プロンプトを記録する**

プロンプトを録音するためのエクステンションを作成しましょう。プロンプトを録音するには、ソフトフォンから`9003<filename>`へダイヤルします（例: `9003welcome`）。ビープ音が聞こえたら録音を開始し、`#`を押して停止します。ビープ音が鳴り、システムが録音されたプロンプトを再生します。

**ステップ2 – メニュー ロジックの作成**

When dialing the 9004 extension, processing jumps to the menu in the `s` extension, priority 1.

### ダイヤル時のマッチング

これは、着信を受け取るための会社設定メニューです。 `Background()` アプリケーションはウェルカムプロンプトを再生し、その後、発信者がダイヤルした番号を現在のコンテキストで定義されたエクステンションと照合しながら、数字入力を待ちます。

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

When you dial this company, the welcome message is played first. After that, Asterisk waits for a digit to be dialed:

| ダイヤル番号 | Asterisk アクション |
|---------------|-----------------|
| 1 | すぐに `Dial(DAHDI/1)` を呼び出す |
| 2 | タイムアウトを待ち、次に `Dial(DAHDI/2)` を呼び出す |
| 21 | すぐに `Dial(DAHDI/3)` を呼び出す |
| 22 | すぐに `Dial(DAHDI/4)` を呼び出す |
| 3 | タイムアウトを待ち、切断する |
| 31 | すぐに `Dial(DAHDI/5)` を呼び出す |
| 32 | すぐに `Dial(DAHDI/6)` を呼び出す |

It is important to avoid ambiguity in the menus. Everybody wants to be answered quickly. For this reason, you should not use numbers 2, 21, or 22.

### ラボ：Read() アプリケーションの使用

Please try the lab with the read() application. Read accept digits from the user and inserts them into the specified variable; you can then use the gotoif application to redirect the call.

## コンテキストのインクルード

コンテキストは別のコンテキストの内容を取り込むことができます。上記の例では、任意のチャンネルが internal コンテキスト内の任意のエクステンションにダイヤルできますが、4003 チャンネルだけが国際エクステンションにダイヤルできます。コンテキストのインクルードを使用すると、ダイヤルプランの作成が容易になります。コンテキストのインクルードを利用して、誰がどのエクステンションにアクセスできるかを制御できます。

### メッセージ “number not found” のトラブルシューティング

“number not found” というメッセージを受け取ることは非常に一般的です。多くの人がインクルードされたコンテキストの概念を混同しますが、これは直感的ではありません。経験則として、まず incoming チャンネルの設定ファイル（例: `pjsip.conf`、`chan_dahdi.conf`、`iax.conf`）を開き、現在のコンテキストを確認します。その後、extensions.conf ファイル内のダイヤルプランに移動し、ダイヤルされた番号がそのコンテキストに存在するかをチェックします。存在しない場合、ダイヤルプランに問題があります。コンテキストの黄金律は次のとおりです。1. チャンネルは同じコンテキスト内の番号しかダイヤルできません。2. 呼び出しが処理されるコンテキストは、incoming チャンネルの設定ファイル（`chan_dahdi.conf`、`iax.conf`、`pjsip.conf`）で定義されています。

## スイッチ文の使用

スイッチコマンドを使用して、ダイヤルプランの処理を別のサーバーに送信できます。別のサーバーの名前とキーが必要です。コンテキストは宛先コンテキストです。

![10-dialplan-advanced-features 図 6](../images/10-dialplan-advanced-features-img06.png)

## ダイヤルプランの処理順序

Asterisk が着信を受け取ると、チャンネルで定義されたコンテキストを参照します。場合によっては、ダイヤルされた番号に対して複数のパターンが一致すると、Asterisk は期待通りに呼び出しを処理できないことがあります。`dialplan show` CLI コマンドを使用すると、マッチング順序を確認できます。例: 912 をアナログトランク (DAHDI/1) にルーティングし、9 で始まるその他のすべての番号を別のアナログトランク (DAHDI/2) にルーティングしたいとします。その場合は次のように記述します。

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

2 つのパターンが同じエクステンションにマッチした場合、インクルードされたコンテキストを使用して、どのエクステンションを先に処理するかを制御できます。インクルードされたコンテキストは、同じコンテキスト内のパターンよりも後に処理されます。

## #INCLUDE 文

大きなファイルを使うべきか、複数のファイルに分けるべきか？ extensions.conf に他のファイルを取り込むには #include <filename> 文を使用できます。例えば、ローカルユーザー用に users.conf を、特別なサービス用に services.conf を作成できます。#include <filename> を以下のものと混同しないよう注意してください。

```
include=>context statement.
```

## Subroutines with GOSUB

古いバージョンの Asterisk では Macro コマンドがありました。このコマンドは長い間前に非推奨となり、GOSUB に置き換えられました。ここでは、ボイスメール処理用のサブルーチンを簡単かつ整理された方法で作成する方法を示します。コマンド形式:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

GOSUB コマンドは Asterisk 1.6 以降で利用可能で、引数を渡すことができます（サブルーチン内では `${ARG1}`、`${ARG2}` などとして参照できます）。引数を使用すれば、従来の Macro コマンドを完全に置き換えることが可能です。Macro（`app_macro`）は Asterisk 21 で削除されました；サブルーチンには GOSUB を使用しなければなりません。

### Creating the subroutine

定義は非常に似ています。以下に、名前を stdexten としたボイスメール用サブルーチンの例を示します（好きな名前に変更してください）。最初の引数（チャンネル名）で Dial コマンドを呼び出した後、${DIALSTATUS} を確認して次のステップへ処理を送ります。

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

### Calling a subroutine

サブルーチンを呼び出す際は、パラメータの前に丸括弧を付けることに注意してください。

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Using Asterisk DB

コールフォワードやブラックリストを実装するには、データを保存・復元する手段が必要です。幸い、Asterisk には AstDB と呼ばれる組み込みデータベースからデータを保存・取得する仕組みが用意されています。最新の Asterisk（Asterisk 22 を含む）では AstDB は **SQLite3**（ファイル `/var/lib/asterisk/astdb.sqlite3`）で裏付けられています。Asterisk 1.8 以前は Berkeley DB v1 が使用されていました。これは、ファミリとキーの階層概念を使用する Windows レジストリ データベースに似ています。データは Asterisk の再起動間で永続化されます。ファミリ/キー API は古いバックエンドから変更されておらず、ディスク上の保存形式だけが変わっています。

### Functions, applications, and CLI commands

AstDB と連携する関数、アプリケーション、CLI コマンドがいくつかあります。

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

例:

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

AstDB を操作できるアプリケーションの例:

- DB_DELETE(<family/key>) — 単一キーを返して削除する関数
- DBdeltree(<family>) — ファミリ/サブツリー全体を削除するアプリケーション

古い `DBdel()` アプリケーションは Asterisk 22 では存在しません。単一キーの削除は `DB_DELETE()` ダイヤルプラン関数で行います — 例: `Set(x=${DB_DELETE(family/key)})` または、書き込み操作として `Set(DB_DELETE(family/key)=)`。`DBdeltree()`（ファミリ/サブツリー全体の削除）は依然としてアプリケーションです。

CLI コマンドでもキーの設定や削除が可能です:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementing Call Forward, DND, and Blacklists

この例では、コールフォワード即時とコールフォワードビジーの実装方法を学びます。*21* を使ってコールフォワード即時を、*61* を使ってコールフォワードビジーをプログラムします。プログラムをキャンセルするには、それぞれ #21# と #61# を使用します。上記の例を使ってデータベースに情報を登録します。使用するファミリは次のとおりです。

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

次の番号をダイヤルしてデータベースに情報を登録してみてください。

- *21*（コールフォワード即時の宛先エクステンション）
- *61*（コールフォワードビジーの宛先エクステンション）
- *41*（取り込み禁止にするエクステンション）

CLI コマンド `database show` を使用して、追加されたファミリ、キー、値を確認できます。

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Call Forward, Blacklist, DND

このサブルーチンは、データベースに CFIM、CFBS、または DND に対応する key:value ペアが存在するかを確認し、適切に処理します。以下のサブルーチンがダイヤリングルーチンを呼び出します:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Using a blacklist

古い`LookupBlacklist()`アプリケーションは **削除** されました（レガシーな「priority+101 jump」メカニズムと共に消失しました）。Asterisk 22 では`DB_EXISTS()`関数（キーの存在をテストし、見つかった場合はその値を`${DB_RESULT}`で取得できる）と`GotoIf`を組み合わせて直接ブラックリストを構築します。ブロックする各番号を`blacklist`ファミリのキーとして保存し、受信コンテキストの先頭で発信者IDをチェックします：

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

`DB_EXISTS(blacklist/${CALLERID(num)})`は、発信者番号がデータベースに存在する場合は`1`（`blocked`コンテキストへコールを送信）を返し、存在しない場合は`0`を返すので、コールは通常の`Dial()`へ進みます。

ブラックリストに番号を追加するには、以前と同じリソースを使用し、*31* の後にブラックリストに登録したい内線番号を入力します。番号を削除するには、#31# の後に削除したい番号を入力してください。

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

コンソール CLI からもブラックリストに番号を追加できます：

```
*CLI>database put blacklist <name/number> 1
```

※ 任意の値をキーに関連付けることができます。`DB_EXISTS()`テストは値ではなくキーを検索します。ブラックリストから番号を削除するには、次のコマンドを使用します：

```
*CLI>database del blacklist <name/number>
```

## 時間ベースのコンテキスト

以下の図では、3つのコンテキストを持つダイヤルプランを示しています。`[incoming]` コンテキストは通常、着信が受け取られる場所です。システム時刻に応じて動作を変更する4行を含めており、例は次のとおりです：

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

Modern Asterisk（22 を含む）は、時間インクルードフィールドを **コンマ** で区切ります。レガシーのパイプ形式（`include => context|times|weekdays|mdays|months`）は、単なるリテラルのコンテキスト名として解析され、時間条件が適用されずに黙って失敗します。

通常の勤務時間中は、処理は `mainmenu` にリダイレクトされ、恐らく着信を処理する IVR が呼び出されます。営業時間外に通話が行われた場合は、`${SECURITY}` 変数で定義されたセキュリティエクステンションが呼び出されます。セキュリティエクステンションが応答しない場合、オペレーターのボイスメールに転送されます。

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Time-based messages using gotoiftime()

The GotoIfTime() syntax is shown below.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

In Asterisk 22 the field separator is a **comma**, not a pipe (the pipe form was deprecated in Asterisk 1.6). An optional `timezone` field is supported, and each branch label uses the usual `[[context,]extension,]priority` form.

This application can replace the time-based context and seems easier to understand and read. You can specify the time as follows:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=number from 1 to 31
- <hour>=number from 0 to 23
- <minute>=number from 0 to 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Names for days and months are not case sensitive.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

The previous statement transfers the processing to the extension s in the normalhours context if the call is between 08:00AM and 06:00PM from Monday to Friday.

## DISA を使用して新しいダイヤルトーンを取得する

DISA（“direct inward system access”）は、ユーザーが第2のダイヤルトーンを受け取ることを可能にするシステムです。ユーザーは再度ダイヤルして別の宛先に接続できます。これは、週末に技術サポートのために長距離電話をかける技術者がよく使用します。自宅から直接宛先へダイヤルする代わりに、オフィスの DISA 番号に電話し、ダイヤルトーンを受け取ってから宛先へ電話します。長距離料金は自宅電話ではなく会社側で負担されます。

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

例:

```
exten => s,1,DISA(no-password,default)
```

上記の文を使用すると、ユーザーは PBX にダイヤルし、パスワードを要求されることなくダイヤルトーンを受け取ります。DISA を使用したすべての呼び出しは `default` コンテキストで処理されます。このアプリケーションの引数には、グローバルパスワードまたはファイル内の個別パスワードが含まれます。コンテキストが指定されていない場合は `disa` コンテキストがデフォルトとして使用されます。パスワードファイルを使用する場合は、完全なパスを指定しなければなりません。DISA の外部ダイヤリング用に発信者番号を指定することもできます。例:

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 は引数の区切り文字としてカンマを使用します（パイプ形式は 1.6 で非推奨となりました）。最初の引数は単一のパスコードかパスコードファイルへのパスで、何も指定されない場合のデフォルトコンテキストは `disa` です。

## 同時通話数の制限

GROUP() 関数を使用すると、同一グループ内で同時にアクティブなチャンネル数をカウントできます。例: リオデジャネイロに支店があり、電話番号が「_214X」のパターンに従う場合。この拠点は専用回線で接続され、音声帯域として 64K が確保されています。この場合、許容できる最大通話数は 2 本です（G.729、1 本あたり約 31.2K）。リオへの通話を 2 本に制限するには:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail は、着信音声メッセージを録音し、ディスクに保存または e‑mail で送信するコンピュータ化された電話応答システムです。ディレクトリがあり、名前で voicemail ボックスを検索できることもあります。かつては voicemail システムは非常に高価でしたが、IP 電話の普及により、voicemail は標準機能となりつつあります。

voicemail を設定するには、以下の手順を実行してください。

**Step 1: Edit `voicemail.conf` and set the general parameters.**

- `format` — codec used to record the message (e.g., wav49, wav, gsm)
- `serveremail` — who the e-mail notification should appear to come from
- `maxmsg` — maximum number of messages in the mailbox; after this threshold, messages are discarded
- `maxsecs` — maximum length of a voicemail message, in seconds
- `minsecs` — minimum length of a message, in seconds; below this threshold, no message is recorded
- `maxsilence` — how many seconds of silence to treat as the end of the message

**Step 2: Edit `voicemail.conf` and create the users’ mailboxes.**

### Voicemail.conf

A mailbox is defined with one line per mailbox, in the form:

```
mailboxID => pincode,fullname,email,pager-email,options
```

The fields are:

- **MailboxID** — usually the extension number
- **Pincode** — password to access the voicemail system
- **Full name** — used by the directory application
- **E-mail** — address for voicemail notification
- **Pager e-mail** — address for notification via an SMS gateway or pager
- **Options** — per-mailbox options (the same options as in `[general]`, but applied to this mailbox)

Voicemail has several options that control its behavior. For now, we will stick to the default options and concentrate on the mailbox definition. After the `[general]` section in the file, you start configuring the mailbox IDs, each in its own context. Example:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Please check for advanced options in the file `voicemail.conf`.

**Step 3: Configure the file `extensions.conf`.**

The `stdexten` subroutine shown earlier (under *Subroutines with GOSUB*) is exactly the call/voicemail handler you need here: it dials the extension and uses the value of the channel variable `${DIALSTATUS}` to redirect the call flow to the proper voicemail greeting (`b` for busy, `u` for unavailable). Call it with `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` from each extension in `extensions.conf`.

## Using the VoiceMailMain() application

The application voicemailmain() is used to configure the voicemail mailbox. Users can dial the application, record their greeting, and listen to their voicemail. To call the application in the dial plan, use:

```
exten=>9000,1,VoiceMailMain()
```

Below you will find a list of the options available for the application.

### Voicemail application syntax

This application allows the calling party to leave a message for a specified list of mailboxes. When multiple mailboxes are specified, the greeting will be taken from the first specified mailbox. The dial plan execution will stop if the specified mailbox does not exist. The syntax is shown below:

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

![10-dialplan-advanced-features 図13](../images/10-dialplan-advanced-features-img13.png)

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

In all cases, the beep.gsm file will be played before the recording begins. Voicemail messages will be stored in the inbox directory.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

If a caller presses 0 (zero) during the announcement, it will be moved to the ‘o’ (out) extension in the voicemail current context. This can be used to exit to the operator. If during the recording the caller presses # or the silence limit times out, recording is stopped and the call goes to the next priority. Make sure that you handle the call after the voicemail is played, as shown below.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Tagging voicemail messages as urgent

You may tag some messages as “urgent.” Two methods are available for this:

- Pass the option ‘U’ in the application voicemail()
- Specify review=yes in the file voicemail.conf. If using this option, the user will be able to tag the message as urgent after recording the voice instructions.

## Sending voicemail to e-mail

一部のケース（私の場合など）では、voicemailmain() アプリケーションを使ってメールを読むことはせず、すべてのメッセージを音声添付でメール送信する方がシンプルで実用的です。`attach` と `delete` パラメータを使用すれば、メールを送信しながらメールボックスから削除できます。

```
attach=yes
delete=yes
```

ボイスメールをメールで送信する際、voicemail アプリケーションはオペレーティングシステムのコンポーネントであるメッセージ転送エージェント（MTA）を利用します。Debian では MTA として Exim が使用されています。メール送信に使用するアプリケーションは `mailcmd` パラメータで定義します。

```
mailcmd =/usr/sbin/sendmail -t
```

Linux の Debian ディストリビューションでは MTA は Exim です。Debian で Exim を設定するには、次のコマンドを使用します。

```
dpkg-reconfigure exim4-config
```

MTA が SMTP 直接送信するか、スマートホスト（通常は社内のメールサーバ）を経由して送信するかを選択できます。Asterisk サーバからメールサーバへメールを送信する最適な方法については、メール管理者に確認してください。

## カスタマイズされたメールメッセージ

メールの送信方法は、次の変数を設定することで制御できます。メールの件名と本文に使用する変数:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

メール本文と件名は、`[general]`セクションの`voicemail.conf`で設定したテンプレートから構築されます。本文と件名の両方を変更できますが、メッセージのサイズ上限は 512 バイトです。テンプレート内では、`\n`が改行を、`\t`がタブを挿入します。

以下の`emailsubject`例はシンプルです。`emailbody`例はデフォルトに非常に近く、デフォルトでは CIDNAME が null でない場合にそれだけが表示され、そうでなければ CIDNUM が表示され、両方が null の場合は「不明な発信者」と表示されます。

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Voicemail Web interface

ソース配布に含まれる Perl スクリプト`vmail.cgi`は、Asterisk ソースツリーの`contrib/scripts/vmail.cgi`にあります（Asterisk 22 でもまだ同梱されています）。コマンド`make install`はこのインターフェースをインストールしません。ソースディレクトリから`make webvmail`を実行する必要があります。このスクリプトは Perl コマンドインタプリタと、サーバ上にインストールされたウェブサーバ（Apache など）を必要とします。

```
make webvmail
```

`make webvmail`ターゲットは、スクリプト（setuid root）をウェブサーバの CGI ディレクトリ（`HTTP_CGIDIR`）にインストールし、サポート画像を`images/*.gif`から`HTTP_DOCSDIR/_asterisk`へ（デフォルトは`/var/www/html/_asterisk`）コピーします。これらのパスがウェブサーバのレイアウトと合わない場合は、ターゲットを実行する前に上位レベルの`Makefile`内の`HTTP_CGIDIR`と`HTTP_DOCSDIR`変数を編集してください。

## Voicemail notification

You can configure voicemail to send a notify message to your phone when you have new voicemail. In Asterisk 22, Message Waiting Indication (MWI) works with PJSIP and SIP phones as well as DAHDI phones. To indicate an unheard voicemail, an indicator light may blink or the phone may play a shutter tone. You need to configure the mailbox in the corresponding channel configuration file. Example: `pjsip.conf` (in the endpoint section):

```
mailboxes=8590
```

In PJSIP the mailbox hint is set with the `mailboxes` option inside the endpoint section of `pjsip.conf`, rather than the old `mailbox=` of `sip.conf`. MWI subscriptions are handled by the `res_pjsip_mwi` module.

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Lab: Message Notification in the Phone

This lab was tested using a SIP softphone.

1. Edit `pjsip.conf` and add `mailboxes=4401` in the endpoint section for the device named 4401.
2. Edit the `extensions.conf` and create an extension to record a voicemail to 4401 extensions.

```
exten=9008,1,voicemail(4401,b)
```

3. Go to the console and reload.
4. In the SipPulse Softphone, open the SIP account settings and enable voicemail (message-waiting) checking for the account.
5. Dial 9008 and leave a message.
6. Observe the message icon on the phone.

## ディレクトリアプリケーションの使用

このアプリケーションを使用すると、ダイヤルすべきユーザーをすばやく検索できます。名前と対応する内線番号の一覧は、voicemail 設定ファイル voicemail.conf から取得されます。アプリケーションの構文は、`core show application directory` で表示できます。

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

### ラボ: ディレクトリアプリケーションの使用

1. voicemail.conf ファイルを編集し、ダイヤルプランに 2 つの内線を追加します

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. これらの内線をダイヤルプランに作成します

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. コンソールに移動してリロードします
4. 9006 をダイヤルし、各内線（4400、4401）の名前を録音します
5. 9007 をダイヤルし、ある内線の姓の最初の 3 文字（Eas=327）を選択します。正しいオプションであれば、‘1’ を押して名前に転送します。

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

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

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

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

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

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

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## Summary

この章では、IVR や自動応答装置を使用して着信を受け取る方法を学びました。コンテキストインクルージョンの概念を検討し、いくつかの例を実装しました。サブルーチンを使用して繰り返し入力を回避し、Asterisk データベース（AstDB、Asterisk 22 では SQLite3 がバックエンド）をデータ保存が必要な機能（例：転送、取り込み禁止、ブラックリスト）に利用しました。最後に、営業時間外の動作を実装し、これらの概念を組み合わせた完全なダイヤルプランを実装しました。

## Quiz

1. 時間依存コンテキストの include は `include => context,<times>,<weekdays>,<mdays>,<months>` という形式を使用します。 `include => normalhours,08:00-18:00,mon-fri,*,*` は何を行いますか？
   - A. 月曜から金曜の 08:00 から 18:00 まで拡張子を実行する
   - B. すべての月の毎日オプションを実行する
   - C. 何もしない；形式が無効である
2. 現代の Asterisk（Asterisk 22 を含む）では、時間ベースの `include =>` と `GotoIfTime()` のフィールドはどの文字で区切られますか？
   - A. パイプ `|`
   - B. カンマ `,`
   - C. セミコロン `;`
   - D. スラッシュ `/`
3. 複数のチャンネルを同時にダイヤル（同時にリング）するには、 `Dial()` 内で ___ 文字で区切ります。
4. 発信者が番号をダイヤルするのを待つ間にプロンプトを再生する音声メニューは、通常 ___ アプリケーションで作成します。
5. `extensions.conf` 内で別ファイルの内容を取り込むには、___ 文を使用します（※`include =>` コンテキスト文とは異なります）。
6. Asterisk 22 では、組み込みの AstDB データベースは次によってサポートされています：
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. `Dial(type1/identifier1&type2/identifier2)` を使用すると、Asterisk は各チャンネルを順番にダイヤルし、間に 20 秒待機します。
   - A. 偽
   - B. 真
8. Background() アプリケーションでは、メッセージの再生が終了するまで DTMF キーを押してオプションを選択できません。
   - A. 偽
   - B. 真
9. 構文 `Goto([[context,]extension,]priority)` が与えられたとき、次のうち Goto() アプリケーションの有効な呼び出しはどれですか？（該当するものすべてにマーク）
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Asterisk 22 のダイヤルプランで AstDB から単一キーを削除するには、次のどれを使用しますか：
    - A. `DBdel()` アプリケーション
    - B. `DB_DELETE()` 関数
    - C. `DBdeltree()` アプリケーション
    - D. `LookupBlacklist()` アプリケーション

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
