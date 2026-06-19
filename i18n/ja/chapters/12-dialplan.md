# Dial Plan advanced features

第3章では、dialplanの基礎について説明しました。教育的な理由から、すべての機能ではなく、最も重要な機能のみを解説しました。本章では、dialplanをより深く掘り下げ、高度なテクニック、新しいアプリケーション、そして概念について説明します。

## 学習目標

本章を読み終えると、以下のことができるようになります。

- extensionのエントリを簡素化する
- dialplanのセキュリティとextensionのフィルタリングに対処する
- IVRメニューを使用して着信を受ける
- サブルーチンを使用して不要な書き換えを避ける
- 「Include」を使用してdialplanのセキュリティを実装する
- AsteriskDBを使用して「follow-me（追跡転送）」を実装する
- PBXで営業時間外の動作を実装する
- switchコマンドを使用して別のPBXへ転送する
- プライバシーマネージャーを実装する
- voicemailを実装する
- 企業ディレクトリを実装する

## Dial Planの簡素化

キーワード「same」を使用してextensionを定義することで、dialplanを簡素化できます。これにより、dialplan内のタイプミスを減らすことができます。以下の例を確認してください。

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Dial Planのセキュリティ

Asteriskのdialplanには、ユーザーが新しいチャネルを注入し、dialplan内の番号をダイヤルできてしまうという欠陥が発見されました。サーバーの`exten=>_X.,1,Dial(PJSIP/${EXTEN})`に以下の行があり、悪意のあるユーザーがソフトフォンで`3000&DAHDI/1/011551123456789`という番号をダイヤルしたと仮定します。SIPプロトコルはデフォルトで任意の英数字を受け入れるため、ダイヤルされたextensionは実際には2つの通話を引き起こします。1つはチャネルPJSIP/3000への通話、もう1つは国際電話番号であるチャネルDAHDI/011551123456789への通話です。したがって、extensionへのアクセス権を持つユーザーは、実際には世界中のどこへでもダイヤルできてしまいます。この動作を回避する最も簡単な方法は、dialアプリケーションを呼び出す前に番号をフィルタリングすることです。FILTER()関数は、この目的のために非常に便利です。例：

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

filterアプリケーションを使用すると、ダイヤルされた番号から0から9までの数字以外のすべての文字をフィルタリングできます。詳細については、Asteriskから入手可能なファイル README-SERIOUSLY.bestpractices.txt を参照してください。

## IVRメニューを使用した着信の受信

前節では、DIDを使用するか、オペレーターに転送することで、すべての着信を受けていました。ここでは、IVRメニューの実装方法と、自動応答サービス（auto-attendant）の作成方法を学びます。詳細に入る前に、いくつかの新しいアプリケーションを確認しましょう。読者が理解しやすいように、show applicationコマンドの出力を以下に記載します。これらの説明は、show application application_name を使用して取得できます。 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### Background()アプリケーション

このアプリケーションは、呼び出し側のチャネルによってextensionがダイヤルされるのを待機している間、指定されたファイルのリストを再生します。このアプリケーションがファイルの再生を終了した後も数字の入力を待機し続けるには、WaitExtenアプリケーションを使用する必要があります。langoverrideオプションは、要求された音声ファイルに使用する言語を明示的に指定します。指定されたcontextは、このアプリケーションがダイヤルされたextensionへ終了する際に使用するdialplanのcontextとなります。要求された音声ファイルのいずれかが存在しない場合、通話処理は終了します。オプション：

- s - チャネルが「up」状態（つまり、まだ応答されていない）でない場合、メッセージの再生をスキップします。これが発生した場合、アプリケーションは直ちに復帰します。
- n - ファイルを再生する前にチャネルに応答しません。
- m - 宛先context内の1桁のextensionに一致する数字が入力された場合にのみ中断します。

### Record()アプリケーション

このアプリケーションは、チャネルから指定されたファイル名へ録音を行います。ファイルが存在する場合は上書きされます。

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' は録音するファイル形式（wav, gsmなど）です。
- 'silence' は復帰するまでに許容される無音の秒数です。
- 'maxduration' は最大録音時間（秒）です。省略または0の場合、制限はありません。
- 'options' には以下の文字を含めることができます：
    - `a` — 既存の録音を置き換えるのではなく、追記します
    - `n` — 応答しませんが、回線がまだ応答されていない場合でも録音します
    - `q` — 静音（ビープ音を鳴らさない）
    - `s` — 回線がまだ応答されていない場合、録音をスキップします
    - `t` — デフォルトの`#`の代わりに、代替の`*`終了キー（DTMF）を使用します
    - `x` — すべての終了キー（DTMF）を無視し、切断されるまで録音を続けます

ファイル名に %d が含まれている場合、ファイルが録音されるたびにこれらの文字が1ずつ増加する数字に置き換えられます。システムで使用可能な形式を確認するには、core show file formats を使用してください。ユーザーは # を押して録音を終了し、次の優先順位に進むことができます。録音中にユーザーが切断した場合、すべてのデータは失われ、アプリケーションは終了します。

### Playback()アプリケーション

このアプリケーションは、指定されたファイル名（拡張子は含めない）を再生します。パイプ記号の後にオプションを含めることもできます。'skip'オプションは、チャネルが「up」状態（つまり、まだ応答されていない）でない場合にメッセージの再生をスキップさせます。

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

'skip'が指定されている場合、チャネルがオフフック状態でなければ、アプリケーションは直ちに復帰します。それ以外の場合、'noanswer'が指定されていない限り、音声が再生される前にチャネルが応答されます。すべてのチャネルがオンフック状態でメッセージの再生をサポートしているわけではありません。'j'が指定されている場合、ファイルが存在しないときに優先順位 n+101 にジャンプします。このアプリケーションは、完了時に以下のチャネル変数を設定します：

- PLAYBACKSTATUS — 再生試行のステータスを示すテキスト文字列。以下のいずれか：
    - `SUCCESS`
    - `FAILED`

### Read()アプリケーション

このアプリケーションは、ユーザーから指定された変数に対して、あらかじめ決められた桁数の数字を一定回数読み取ります。

- filename -- 数字やトーンを読み取る前に再生するファイル（iオプション使用時）
- maxdigits -- 許容される最大桁数。maxdigitsが入力されると読み取りを停止します（ユーザーが # キーを押す必要はありません）。デフォルトは0（制限なし）で、ユーザーが # キーを押すのを待ちます。0未満の値も同様の意味を持ちます。最大許容値は255です。

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- オプションは`s`, `i`, `n`です：
    - `s` — 回線がup状態でなければ直ちに復帰する
    - `i` — filenameを`indications.conf`からの指示トーンとして再生する
    - `n` — 回線がup状態でなくても数字を読み取る
- attempts -- 1より大きい場合、データが入力されなかった場合に試行される回数
- timeout -- 数字の応答を待つ秒数（整数）。0より大きい場合、その値がデフォルトのタイムアウトを上書きします。

read()アプリケーションは、関数が失敗またはエラーになった場合に切断されるべきです。

### Gotoif()アプリケーション

このアプリケーションは、指定された条件の評価に基づいて、呼び出し側のチャネルをdialplan内の指定された場所にジャンプさせます。条件が真であれば labeliftrue に、偽であれば 'labeliffalse' に進みます。ラベルは、Gotoアプリケーション内で使用されるのと同じ構文で指定されます。条件によって選択されたラベルが省略された場合、ジャンプは実行されず、dialplan内の次の優先順位で実行が継続されます。

### ラボ：IVRメニューの段階的な構築

以下の機能を持つIVRメニューを作成しましょう。ダイヤルされると、IVRは「XYZコーポレーションへようこそ。セールスは1を、技術サポートは2を、トレーニングは3を押してください。担当者と話す場合はそのままお待ちください」というメッセージの音声ファイルを再生します。数字は発信者を以下のようにルーティングします：

- `1` — セールスへ転送 (PJSIP/4001)
- `2` — 技術サポートへ転送 (PJSIP/4002)
- `3` — トレーニングへ転送 (PJSIP/4003)
- 数字が押されない場合 — オペレーターへ転送 (PJSIP/4000)

**ステップ1 – プロンプトの録音**

プロンプトを録音するためのextensionを作成しましょう。プロンプトを録音するには、ソフトフォンから`9003<filename>`（例：`9003welcome`）へダイヤルします。ビープ音が聞こえたら録音を開始し、`#`を押して停止します。ビープ音が聞こえ、システムが録音されたプロンプトを再生します。

**ステップ2 – メニューロジックの作成**

9004 extensionをダイヤルすると、処理は`s` extensionの優先順位1のメニューへジャンプします。

### ダイヤル中のマッチング

これは、着信を受けるための会社設定メニューです。backgroundアプリケーションは現在のcontextを読み取り、あらゆる可能な組み合わせに対して各番号の最大長を定義します。

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

この会社にダイヤルすると、最初にウェルカムメッセージが再生されます。その後、Asteriskは数字がダイヤルされるのを待ちます。ダイヤルされた番号 Asteriskの動作 直ちに Dial(DAHDI/1) を呼び出す タイムアウトを待ってから Dial(DAHDI/2) へ行く 直ちに (DAHDI/3) を呼び出す 直ちに (DAHDI/4) を呼び出す タイムアウトを待ってから切断する 直ちに Dial(DAHDI/5) を呼び出す 直ちに Dial(DAHDI/6) を呼び出す 直ちに切断する メニュー内の曖昧さを避けることが重要です。誰もが素早く応答されたいと思っています。このため、2、21、または22という番号は使用すべきではありません。

### ラボ：Read()アプリケーションの使用

read()アプリケーションを使用したラボを試してください。Readはユーザーからの数字を受け入れて指定された変数に挿入します。その後、gotoifアプリケーションを使用して通話をリダイレクトできます。

## Contextのインクルード

あるcontextは、別のcontextの内容をインクルードできます。上記の例では、どのチャネルもinternal context内の任意のextensionをダイヤルできますが、4003チャネルのみが国際extensionをダイヤルできます。contextのインクルードを使用して、dialplanの作成を容易にすることができます。contextのインクルードを使用することで、誰がどのextensionにアクセスできるかを制御できます。

### 「number not found」メッセージのトラブルシューティング

「number not found」というメッセージを受け取ることは非常によくあります。多くの人は、インクルードされたcontextの概念を混同します。なぜなら、それは直感的ではないからです。経験則として、まず`pjsip.conf`, `chan_dahdi.conf`, `iax.conf`などの着信チャネル設定ファイルに移動し、現在のcontextを確認してください。次に、extensions.confファイルのdialplanに移動し、ダイヤルされた番号がそのcontextで見つかるかどうかを確認します。見つからない場合、dialplanに何か問題があります。contextの黄金律は以下の通りです：1. チャネルは、そのチャネルと同じcontext内の番号しかダイヤルできません。2. 通話が処理されるcontextは、着信チャネル設定ファイル（`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`）で定義されます。

## switchステートメントの使用

switchコマンドを使用して、dialplanの処理を別のサーバーに送信できます。別のサーバーの名前とキーが必要です。contextは宛先のcontextです。

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Dial planの処理順序

Asteriskが着信を受けると、チャネルによって定義されたcontext内を検索します。場合によっては、複数のパターンがダイヤルされた番号に一致すると、Asteriskが想定通りの方法で通話を処理できないことがあります。dialplan show CLIコマンドを使用して、マッチング順序を確認できます。例：912をダイヤルしてアナログトランク（DAHDI/1）にルーティングし、9で始まる他のすべての番号を別のアナログトランク（DAHDI/2）にルーティングしたいとします。以下のように記述します：

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

2つのパターンがextensionに一致する場合、インクルードされたcontextを使用して、どのextensionが最初に処理されるかを制御できます。インクルードされたcontextは、同じcontext内のパターンよりも後に処理されます。

## #INCLUDEステートメント

大きなファイルを1つ使うべきか、複数のファイルを使うべきでしょうか？ #include <filename> ステートメントを使用して、extensions.confに他のファイルをインクルードできます。例えば、ローカルユーザー用に users.conf を、特別なサービス用に services.conf を作成できます。#include <filename> と以下を混同しないように注意してください。

```
include=>context statement.
```

## GOSUBによるサブルーチン

古いバージョンのAsteriskにはMacroコマンドがありました。このコマンドは、GOSUBを優先するためにずっと前に非推奨となりました。ここでは、voicemail処理用のサブルーチンを簡単かつ整然とした方法で作成する方法を説明します。コマンド形式：

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

GOSUBコマンドはAsterisk 1.6以降で使用可能であり、引数の受け渡し（サブルーチン内では`${ARG1}`, `${ARG2}`などとして利用可能）をサポートしています。引数を使用することで、古いMacroコマンドを完全に置き換えることが可能になりました。Macro（`app_macro`）はAsterisk 21で削除されました。サブルーチンにはGOSUBを使用しなければなりません。

### サブルーチンの作成

定義は非常に似ています。voicemail用にstdextenという名前（好きな名前を選んでください）で定義された以下のサブルーチンを見てください。最初の引数（チャネル名）でDialコマンドを呼び出した後、${DIALSTATUS}をチェックして、通話ロジックを次のステップへ送ります。

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

サブルーチンを呼び出すときは、パラメータの前に括弧を使用することに注意してください。

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Asterisk DBの使用

通話転送（call forward）やブラックリストを実装するには、データを保存および復元する方法が必要です。幸いなことに、AsteriskにはAstDBと呼ばれる組み込みデータベースからデータを保存および取得するメカニズムが用意されています。最新のAsterisk（Asterisk 22を含む）では、AstDBは**SQLite3**（ファイル`/var/lib/asterisk/astdb.sqlite3`）によってバックアップされています。Asterisk 1.8以前はBerkeley DB v1を使用していました。これは、ファミリーとキーの階層概念を使用するWindowsレジストリデータベースに似ています。データはAsteriskの再起動後も保持されます。ファミリー/キーAPIは古いバックエンドから変更されていません。ディスク上のストレージ形式のみが変更されました。

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

- DB_DELETE(<family/key>) — 単一のキーを返して削除する関数
- DBdeltree(<family>) — ファミリー全体/サブツリー全体を削除するアプリケーション

古い`DBdel()`アプリケーションはAsterisk 22にはもう存在しません。単一のキーを削除するには`DB_DELETE()`dialplan関数を使用します（例：`Set(x=${DB_DELETE(family/key)})`、または書き込み操作として`Set(DB_DELETE(family/key)=)`）。`DBdeltree()`（ファミリー全体/サブツリー全体の削除）は依然としてアプリケーションです。

CLIコマンドを使用してキーを設定および削除することも可能です：

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### 通話転送、DND、およびブラックリストの実装

この例では、即時通話転送（call forward immediate）と話中時通話転送（call forward on busy）の実装方法を学びます。即時通話転送のプログラムには *21* を、話中時通話転送のプログラムには *61* を使用します。プログラムをキャンセルするには、それぞれ #21# と #61# を使用します。上記の例を使用してデータベースを構築してください。使用されるファミリー：

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

以下をダイヤルしてデータベースを構築してみてください：

- *21* (即時通話転送用の宛先extension)
- *61* (話中時通話転送用の宛先extension)
- *41* (おやすみモード（DND）にするためのextension)

CLIコマンド database show を使用して、追加されたファミリー、キー、および値を確認してください。

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### 通話転送、ブラックリスト、DND

上記のサブルーチンは、データベースにCFIM、CFBS、またはDNDに対応するキー:値のペアが含まれているかどうかを確認し、それに応じて処理します。followサブルーチンはダイヤルルーチンを呼び出します：

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## ブラックリストの使用

古い`LookupBlacklist()`アプリケーションはAsteriskから**削除**されました（レガシーな「priority+101ジャンプ」メカニズムと共に消滅しました）。Asterisk 22では、ブラックリストは`DB_EXISTS()`関数（キーをテストし、見つかった場合はその値を`${DB_RESULT}`に公開する）と`GotoIf`を使用して直接構築します。各ブロックされた番号を`blacklist`ファミリーのキーとして保存し、着信contextの先頭で発信者IDを確認します：

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

`DB_EXISTS(blacklist/${CALLERID(num)})`は、発信者の番号がデータベースに存在する場合に`1`を返し（通話を`blocked`contextに送信）、そうでない場合は`0`を返すため、通話は通常の`Dial()`に進みます。

ブラックリストに番号を挿入するには、以前と同じリソースを使用し、*31* の後にブラックリストに登録するextensionを続けます。ブラックリストから番号を削除するには、#31# の後に削除する番号を続けます。

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

コンソールCLIを使用してブラックリストに番号を挿入することもできます：

```
CLI>database put blacklist <name/number> 1
```

注：キーには任意の値が関連付けられます。`DB_EXISTS()`テストは値ではなくキーを検索します。ブラックリストから番号を消去するには、以下を使用できます：

```
CLI>database del blacklist <name/number>
```

## 時間ベースのcontext

以下の図では、3つのcontextを持つdialplanを示しています。[incoming] contextは、通常通話が受信される場所です。以下のように、システム時刻に応じて動作を変更する4つの行をインクルードしました：

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

最新のAsterisk（22を含む）では、時間インクルードフィールドはパイプではなく**カンマ**で区切られます。レガシーなパイプ形式（`include => context|times|weekdays|mdays|months`）は、単なるリテラルのcontext名として解析され、時間条件は適用されず黙って失敗します。

通常の営業時間中、処理はmainmenuにリダイレクトされ、そこで着信を処理するためにIVRが呼び出されるでしょう。営業時間外に通話が行われた場合、${SECURITY}変数で定義されたセキュリティextensionが呼び出されます。セキュリティextensionが通話に応答しない場合、オペレーターのvoicemailに送信されます。

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## gotoiftime()を使用した時間ベースのメッセージ

GotoIfTime()の構文を以下に示します。

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

Asterisk 22では、フィールド区切り文字はパイプではなく**カンマ**です（パイプ形式はAsterisk 1.6で非推奨となりました）。オプションの`timezone`フィールドがサポートされており、各分岐ラベルは通常の`[[context,]extension,]priority`形式を使用します。

このアプリケーションは時間ベースのcontextを置き換えることができ、理解しやすく読みやすいようです。時間は以下のように指定できます：

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

上記のステートメントは、通話が月曜日から金曜日の午前08:00から午後06:00の間に行われた場合、処理をnormalhours contextのextension sに転送します。

## DISAを使用して新しいダイヤルトーンを取得する

DISA（Direct Inward System Access）は、ユーザーが2番目のダイヤルトーンを受信できるようにするシステムです。ユーザーが別の宛先に再ダイヤルすることを許可します。週末に技術サポートのために長距離電話をかける際、技術者によってよく使用されます。自宅から直接宛先にダイヤルする代わりに、会社のDISA番号に電話をかけ、ダイヤルトーンを受信してから宛先に電話をかけます。長距離料金は自宅の電話ではなく会社に発生します。

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

例：

```
exten => s,1,DISA(no-password,default)
```

上記のステートメントを使用すると、ユーザーはPBXにダイヤルし、パスワードを必要とせずにダイヤルトーンを受信します。DISAを使用した通話はすべて`default`contextを使用して処理されます。このアプリケーションの引数には、グローバルパスワードまたはファイル内の個別のパスワードが含まれます。contextが指定されていない場合、`disa`contextが想定されます。パスワードファイルを使用する場合は、完全なパスを指定する必要があります。DISA外部ダイヤル用に発信者IDを指定することもできます。例：

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22は引数の区切り文字としてカンマを使用します（パイプ形式は1.6で非推奨となりました）。最初の引数は単一のパスコードまたはパスコードファイルへのパスであり、何も指定されていない場合のデフォルトのcontextは`disa`です。

## 同時通話の制限

GROUP()関数を使用すると、同時に1つのグループ内にいくつのアクティブなチャネルがあるかをカウントできます。例：リオデジャネイロに支店があり、電話が「_214X」というパターンに従っているとします。この場所は専用線でサービスされており、音声帯域幅として64Kが予約されています。この場合、許可される最大通話数は2です（G.729、1通話あたり30r.2K）。リオへの通話を2つに制限するには：

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemailは、着信音声メッセージを録音し、ディスクに保存したり電子メールで送信したりするコンピュータ化された電話応答システムです。名前でvoicemailボックスを検索できるディレクトリがある場合もあります。かつて、voicemailシステムは非常に高価でした。現在、IPテレフォニーにより、voicemailは標準機能になりつつあります。

voicemailを構成するには、以下の手順を実行する必要があります。

**ステップ1：`voicemail.conf`を編集し、一般的なパラメータを設定します。**

- `format` — メッセージの録音に使用されるコーデック（例：wav49, wav, gsm）
- `serveremail` — 電子メール通知の送信元として表示されるアドレス
- `maxmsg` — メールボックス内の最大メッセージ数。このしきい値を超えると、メッセージは破棄されます
- `maxsecs` — voicemailメッセージの最大長（秒）
- `minsecs` — メッセージの最小長（秒）。このしきい値を下回ると、メッセージは録音されません
- `maxsilence` — メッセージの終了とみなす無音の秒数

**ステップ2：`voicemail.conf`を編集し、ユーザーのメールボックスを作成します。**

### Voicemail.conf

メールボックスは、メールボックスごとに1行で定義されます。形式は以下の通りです：

```
mailboxID => pincode,fullname,email,pager-email,options
```

フィールドは以下の通りです：

- **MailboxID** — 通常はextension番号
- **Pincode** — voicemailシステムにアクセスするためのパスワード
- **Full name** — ディレクトリアプリケーションで使用されます
- **E-mail** — voicemail通知用のアドレス
- **Pager e-mail** — SMSゲートウェイまたはポケットベル経由の通知用アドレス
- **Options** — メールボックスごとのオプション（`[general]`と同じオプションですが、このメールボックスに適用されます）

Voicemailには、その動作を制御するいくつかのオプションがあります。今のところはデフォルトのオプションを使用し、メールボックスの定義に集中します。ファイル内の`[general]`セクションの後、各contextで独自のメールボックスIDの構成を開始します。例：

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

ファイル`voicemail.conf`の高度なオプションを確認してください。

**ステップ3：ファイル`extensions.conf`を構成します。**

以下に、サブルーチンを作成し、`extensions.conf`でvoicemailを実装する呼び出しの指示があります。チャネル変数`${DIALSTATUS}`の値を使用して、通話フローを適切なvoicemailメニューにリダイレクトします。

### Voicemailサブルーチン

## Voicemailmain()アプリケーションの使用

voicemailmain()アプリケーションは、voicemailメールボックスを構成するために使用されます。ユーザーはアプリケーションにダイヤルし、挨拶を録音し、voicemailを聞くことができます。dialplanでアプリケーションを呼び出すには、以下を使用します：

```
exten=>9000,1,VoiceMailMain()
```

以下に、アプリケーションで使用可能なオプションのリストを示します。

### Voicemailアプリケーションの構文

このアプリケーションを使用すると、呼び出し側は指定されたメールボックスのリストにメッセージを残すことができます。複数のメールボックスが指定されている場合、挨拶は最初に指定されたメールボックスから取得されます。指定されたメールボックスが存在しない場合、dialplanの実行は停止します。構文を以下に示します：

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

すべての場合において、録音が開始される前に beep.gsm ファイルが再生されます。Voicemailメッセージは inbox ディレクトリに保存されます。

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

発信者がアナウンス中に 0 を押すと、voicemailの現在のcontextにある「o」（out）extensionに移動します。これはオペレーターへ終了するために使用できます。録音中に発信者が # を押すか、無音制限がタイムアウトすると、録音は停止し、通話は次の優先順位に進みます。以下に示すように、voicemailが再生された後、通話を処理するようにしてください。

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Voicemailメッセージの緊急タグ付け

一部のメッセージを「緊急」としてタグ付けできます。これには2つの方法があります：

- voicemail()アプリケーションでオプション「U」を渡す
- voicemail.confファイルで review=yes を指定する。このオプションを使用すると、ユーザーは音声指示を録音した後、メッセージを緊急としてタグ付けできるようになります。

## Voicemailの電子メール送信

場合によっては（私のように）、voicemailmain()アプリケーションを使用して電子メールを読むことはありません。すべてのメッセージを音声付きで電子メールに送信する方が、よりシンプルで実用的です。'attach'および'delete'パラメータを使用すると、すべてのメールを電子メールに送信し、メールボックスから削除できます。

```
attach=yes
delete=yes
```

Voicemailを電子メールに送信するために、voicemailアプリケーションはオペレーティングシステムのコンポーネントであるメッセージ転送エージェント（MTA）を使用します。DebianはMTAとしてEximを使用します。電子メールを送信するアプリケーションは「mailcmd」パラメータで定義されます。

```
mailcmd =/usr/sbin/sendmail -t
```

LinuxのDebianディストリビューションでは、MTAはEximです。DebianでEximを構成するには、以下を使用します：

```
dpkg-reconfigure exim4-config
```

MTAがSMTPまたはスマートホスト（通常は会社のメールサーバー）を介して直接電子メールを送信するように選択できます。Asteriskサーバーから電子メールサーバーへ電子メールを送信する最良の方法を、電子メール管理者に確認してください。

## 電子メールメッセージのカスタマイズ

以下の変数を設定することで、メッセージの送信方法を制御できます。電子メールの件名と本文の変数：

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

電子メールの本文と件名は、`voicemail.conf`の`[general]`セクションで設定するテンプレートから構築されます。本文と件名の両方を変更できますが、メッセージのサイズ制限は512バイトです。テンプレートでは、`\n`は改行を挿入し、`\t`はタブを挿入します。

以下の`emailsubject`の例は単純明快です。`emailbody`の例はデフォルトに非常に近く、デフォルトではCIDNAMEがnullでない場合はCIDNAMEのみを表示し、そうでない場合はCIDNUMを表示し、両方がnullの場合は「an unknown caller」を表示します。

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Voicemail Webインターフェース

Asteriskソースツリーの`contrib/scripts/vmail.cgi`に、`vmail.cgi`というPerlスクリプトがあります（Asterisk 22にも同梱されています）。コマンド`make install`はこのインターフェースをインストールしません。ソースディレクトリから`make webvmail`を実行する必要があります。このスクリプトには、Perlコマンドインタープリタと、サーバーにインストールされたWebサーバー（Apacheなど）が必要です。

```
make webvmail
```

`make webvmail`ターゲットは、スクリプト（setuid root）をWebサーバーのCGIディレクトリ（`HTTP_CGIDIR`）にインストールし、サポート画像を`images/*.gif`から`HTTP_DOCSDIR/_asterisk`（デフォルトでは`/var/www/html/_asterisk`）にコピーします。これらのパスがWebサーバーのレイアウトと一致しない場合は、ターゲットを実行する前に、トップレベルの`Makefile`にある`HTTP_CGIDIR`および`HTTP_DOCSDIR`変数を編集してください。

## Voicemail通知

新しいvoicemailがあるときに電話に通知メッセージを送信するようにvoicemailを構成できます。Asterisk 22では、メッセージ待機表示（MWI）はPJSIPおよびSIP電話、さらにDAHDI電話で動作します。未読のvoicemailを示すために、インジケーターライトが点滅したり、電話がシャッター音を鳴らしたりすることがあります。対応するチャネル設定ファイルでメールボックスを構成する必要があります。例：`pjsip.conf`（endpointセクション内）：

```
mailboxes=8590
```

PJSIPでは、メールボックスのヒントは`pjsip.conf`のendpointセクション内の`mailboxes`オプションで設定されます（`sip.conf`の古い`mailbox=`ではありません）。MWIサブスクリプションは`res_pjsip_mwi`モジュールによって処理されます。

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### ラボ：電話機でのメッセージ通知

このラボはSIPソフトフォンを使用してテストされました。1. `pjsip.conf`を編集し、デバイス名4401のendpointセクションに`mailboxes=4401`を追加します。2. extensions.confを編集し、4401 extensionへのvoicemailを録音するためのextensionを作成します。

```
exten=9008,n,voicemail(b4401)
```

3. CLI > コンソールに移動し、リロードします。4. SipPulseソフトフォンで、SIPアカウント設定を開き、アカウントのvoicemail（message-waiting）チェックを有効にします。5. 9008にダイヤルし、メッセージを残します。6. 電話機のメッセージアイコンを確認します。

## directoryアプリケーションの使用

このアプリケーションを使用すると、ダイヤルするユーザーを素早く見つけることができます。名前と対応するextensionのリストは、voicemail設定ファイル voicemail.conf から取得されます。アプリケーションの構文は core show application directory を使用して表示できます：

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

### ラボ：directoryアプリケーションの使用

1. voicemail.confファイルを編集し、dialplanに2つのextensionを追加します

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. dialplanにこれらのextensionを作成します

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. コンソールに移動し、リロードします 4. 9006にダイヤルし、各extension（4400, 4401）の名前を録音します 5. 9007にダイヤルし、1つのextensionの姓の3文字を選択します（Eas=327）。これが正しいオプションであれば、「1」を押してその名前に転送します。

## ラボ：すべてをまとめる

これまで、いくつかのdialplanの概念を学びました。それらがどのように組み合わされているかを理解できるように、dialplanの例ですべてのアプリケーション、関数、概念をまとめましょう。以下のシナリオのPBX構成全体をガイドします。

- 4つのアナログトランク
- 16のSIPベースのextension
- 3つのサービスクラス：
    - restrict（内部、ローカル、および1-800）
    - ld（長距離）
    - ldi（国際）
- 営業時間外メッセージ
- 自動応答

### ステップ1 – チャネルの構成

アナログトランク（chan_dahdi.conf） まず、DAHDIチャネル設定ファイル chan_dahdi.conf でアナログトランクを構成します。この場合、4つのFXOインターフェースを持つT400P Digiumカードを使用します。ドライバーはすでにロードされており、ドライバー設定ファイル（/etc/dahdi/system.conf）が正しく構成されていると仮定します。

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

SIPチャネル（pjsip.conf） dialplanの番号付けは2000から2099を選択しました。G.729とG.711 ulawの2つのコーデックを使用します。前者はインターネットまたはWAN経由でAsteriskを使用する電話機に使用され、後者はローカルネットワークを使用する電話機に使用されます。`pjsip.conf`では、どのデバイスが各サービスクラス（restrict, ld, ldi）に属するかを決定します。ブルートフォース攻撃への脆弱性を減らすために、デバイス名として電話機のMACアドレスを使用します。ブルートフォース攻撃を避けるために、強力なパスワードを使用することを強くお勧めします！

トランスポートと3つの再利用可能なテンプレート（共有コーデックを持つendpointベース、userpass認証、単一のcontact AOR）を定義し、各デバイスをテンプレートにアタッチして、異なる部分（サービスクラスのcontextと資格情報）のみをオーバーライドします。`host=dynamic`は電話機が登録するAORとなり、`directmedia`は`direct_media`となります：

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

### ステップ2 – Dial planの構成

次に、extensions.confの構成を開始します。内部extensionとローカルダイヤルを定義します

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
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### ステップ3 - 自動応答を使用した着信の受信

着信を受けるには、2つのcontextを使用します。1つ目は通常営業時間中の操作用で、通話は自動応答によって受信されます。2つ目は営業時間外用で、発信者は「XYZ社にお電話ありがとうございます。営業時間は午前08:00から午後06:00までです。宛先のextension番号をご存知の場合は、今すぐダイヤルするか、切断してください」といったメッセージを受け取ります。メニュー：通常営業時間、営業時間外 以下のメニューでは、システムは会社が通常の営業時間外に連絡されたことを発信者に警告するメッセージを再生し、発信者が宛先のextension番号をダイヤルできるようにします（通常の営業時間外に誰かが働いている可能性があります）。

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

メニュー：メインとセールス 通常の営業時間中、通話は自動応答メニューによって応答され、「XYZ社へようこそ。セールスは1を、技術サポートは2を、トレーニングは3を、または希望するextension番号をダイヤルしてください」といったメッセージを受け取ります。

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

これらのステートメントにより、dialplanの機能は準備完了です。次のセクションでは、PBXの操作方法を説明します。

## まとめ

本章では、IVRや自動応答を使用して着信を受ける方法を学びました。contextのインクルードの概念を学習し、いくつかの例を実装しました。繰り返し入力を避けるためにサブルーチンを使用し、データストレージを必要とする機能（通話転送、おやすみモード、ブラックリストなど）にはAsteriskデータベース（Asterisk 22ではSQLite3でバックアップされたAstDB）を使用しました。最後に、営業時間外の動作を実装する方法を学び、これらの概念を使用して完全なdialplanを実装しました。

## クイズ

1. 時間依存のcontextインクルードは`include => context,<times>,<weekdays>,<mdays>,<months>`の形式を使用します。`include => normalhours,08:00-18:00,mon-fri,*,*`は何を行いますか？
   - A. 月曜日から金曜日の08:00から18:00にextensionを実行する
   - B. すべての月の毎日オプションを実行する
   - C. 何もしない。形式が無効である
2. 最新のAsterisk（Asterisk 22を含む）では、時間ベースの`include =>`および`GotoIfTime()`のフィールドはどの文字で区切られますか？
   - A. パイプ`|`
   - B. カンマ`,`
   - C. セミコロン`;`
   - D. スラッシュ`/`
3. 一度に複数のチャネルをダイヤルする（同時に鳴らす）には、`Dial()`内で___文字を使用してそれらを区切ります。
4. 発信者がextensionをダイヤルするのを待っている間にプロンプトを再生する音声メニューは、通常___アプリケーションで作成されます。
5. ___ステートメントを使用して、`extensions.conf`内に別のファイルの内容をインクルードできます（注：これは`include =>`contextステートメントとは異なります）。
6. Asterisk 22では、組み込みのAstDBデータベースは以下によってバックアップされています：
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. `Dial(type1/identifier1&type2/identifier2)`を使用すると、Asteriskは各チャネルを順番にダイヤルし、それらの間で20秒間待機します。
   - A. 偽
   - B. 真
8. Background()アプリケーションでは、オプションを選択するためにDTMF数字を押す前に、メッセージの再生が終了するまで待つ必要があります。
   - A. 偽
   - B. 真
9. 構文`Goto([[context,]extension,]priority)`が与えられた場合、Goto()アプリケーションの有効な呼び出しはどれですか？（すべて選択してください）
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Asterisk 22のdialplanでAstDBから単一のキーを削除するには、以下を使用します：
    - A. `DBdel()`アプリケーション
    - B. `DB_DELETE()`関数
    - C. `DBdeltree()`アプリケーション
    - D. `LookupBlacklist()`アプリケーション

**回答:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
