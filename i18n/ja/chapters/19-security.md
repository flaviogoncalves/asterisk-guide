# Asterisk セキュリティ

Asterisk のセキュリティ問題は、その誕生以来、極めて重要です。CERT.BR によると、SIP (Session Initiation Protocol) はインターネット上で最も攻撃を受けているプロトコルです。ハニーポットを運用している人なら誰でもそれを確認できるでしょう。インターネット収益分配詐欺（Internet Revenue Share Fraud）の問題は非常に深刻で、数十万ドルを超える損失につながる可能性があります。適切なセキュリティ対策を講じずに、インターネットに接続された Asterisk サーバーを設置してはなりません。本章では、遭遇する可能性のある主な攻撃の種類を特定する方法と、適切なセキュリティポリシーを用いてそれらを防止する方法を学びます。最後に、提案されたセキュリティポリシーを実装する方法を学びます。

本章は **Asterisk 22 LTS** を対象としており、PJSIP (`res_pjsip` / `chan_pjsip`) が唯一の SIP チャネルとなります。（古い `chan_sip` ドライバは Asterisk 21 で削除されました。古いシステムから移行する場合は *Legacy Channels* の章を参照してください。）セキュリティに関連する重要な変更点として、認証失敗は Asterisk の **セキュリティイベントフレームワーク** および専用の `security` ロガーチャネルを通じて出力されるようになりました。これにより、Fail2Ban の設定方法が変更されています（本章の後半で解説します）。

## 学習目標

本章を終えると、以下のことができるようになります。

- Asterisk サーバーに対して頻繁に行われる主な攻撃の種類を特定する
- 効果的なセキュリティポリシーを定義する
- セキュリティポリシーを実装する
- Asterisk 用の IPTABLES をインストールおよび設定する
- Asterisk 用の Fail2Ban をインストールおよび設定する
- 暗号化のための TLS および SRTP をインストールおよび設定する

## IP 電話に対する主な攻撃

IP 電話に対する主な攻撃は、DOS/DDOS、サービス窃盗/通話詐欺（Toll Fraud）、および盗聴に分類できます。名称が紛らわしい場合があり、情報源によって同じ攻撃でも異なる名前で呼ばれることがあります。サービス窃盗、通話詐欺、インターネット収益分配詐欺、電話詐欺などは、ハッカーがあなたの PBX を悪用してプレミアムレート番号へトラフィックを流し、プロバイダーからリベートを得るための異なる呼称です。

### DDoS/DOS

サービス拒否（Denial of Service）および分散型サービス拒否（Distributed Denial of Service）は、あらゆる IT インフラに対する一般的な攻撃です。SIP やその他の Voice over IP プロトコルも例外ではありません。分散型サービス拒否は通常ボットネットによって実行され、DOS は単一のコンピュータによって実行されます。2011 年 2 月、Sality ボットネットは、脆弱な SIP サーバーを探して IPv4 アドレス空間全体を隠密かつ組織的にスキャンしました。UCSD Network Telescope を観測していた研究者は、UDP ポート 5060 を調査していた約 300 万の異なるソース IP を特定し、そのほとんどが通話詐欺を目的とした SIP アカウントのブルートフォース攻撃であったと結論付けています。[^sality]

[^sality]: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![サーバーに対して何千もの SIP 登録試行を行うピアツーピアボットネット](../images/19-security-fig01.png)

DOS は通常、ファジングやフラッディングといった手法を通じて行われます。フラッディングには SIP、IAX、RTP などのプロトコルが使用されます。これらはサービスを完全に停止させたり、音声品質を低下させたりする可能性があります。ポートがインターネットに公開されている場合、これらの攻撃を緩和するのは非常に困難です。以下に、攻撃者が使用するツールの一部を挙げます。

**ファジング:**

- **PROTOS Test Suite (c07-sip)** — オウル大学 OUSPG によるもの。何千もの不正なパケットを送信し、ソフトウェアを停止させるバッファオーバーフローなどの誤動作を誘発します。
- **Voiper** — すべての SIP 属性を網羅する 20 万以上のテストを生成し、サーバーがメッセージを効果的に処理できるかどうかを検証します。 <http://voiper.sourceforge.net/>

**フラッディング:**

- **INVITE Flooder** — SIP INVITE リクエストでサーバーをフラッド攻撃します。 <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — IAX2 トラフィックでサーバーをフラッド攻撃します。 <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — アクティブなメディアセッションを RTP パケットでフラッド攻撃し、音声品質を低下させます。 <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### DoS/DDoS の緩和手法

私の推奨事項は以下の通りです。

1. 適切な保護（SBC）なしに Asterisk サーバーをインターネットに公開しないこと。 2. 内部ネットワークでは、特にユーザー数が多い大学やカレッジなどでは、音声用に仮想 LAN (VLAN) を使用すること。 3. 外部アクセスには VPN または TLS を使用すること。

### インターネット収益分配詐欺

この詐欺は少し理解しにくいものです。鍵となるのは、国際プレミアムレート番号（IPRN）の概念を理解することです。

![インターネット収益分配詐欺の 3 つのステップ：プレミアムレート番号を購入し、脆弱な VoIP デバイスを見つけてその番号に発信し、報酬を受け取る](../images/19-security-fig02.png)

IPRN とは、特定のインターネット電話会社で無料で割り当てることができる番号です。「Internet Premium Rate Number Providers」で検索すれば、多くのプロバイダーが見つかります。このタイプの事業者では、例えばイリジウムのような衛星ネットワークの番号を割り当てることができ、発信者には 1 分あたり数十ドルのコストがかかります。IPRN プロバイダーは、着信した通話 1 分ごとに収益の一定割合（収入の 10 ～ 20%）をあなたに支払います。

![国別の支払いレートとテスト番号を示す IPRN プロバイダーの価格表](../images/19-security-fig03.png)

割り当てフェーズの後、ハッカーは割り当てられた IPRN に発信できるオープンな Asterisk サーバーを探します。ハッカーに制御された被害者の PBX は、IPRN 番号に対して何百もの通話を行い、ハッカーに多額の報酬をもたらし、被害者には莫大な電話料金を請求させます。多くの場合、週末だけで数十万ドルを超えることもあります。ハッカーが PBX を攻撃するために使用する主なツール： 1. SIPVicious: http://code.google.com/p/sipvicious/。Sipvicious は使いやすいセキュリティツールセットです。主な目的は、脆弱な PBX を認識し、ブルートフォース攻撃を使用して SIP パスワードを解読することです。最も使用されるツールは svcrack です。このツールは 1 秒間に何千ものパスワードをテストできます。 2. 電話機の脆弱性。ハッカーが攻撃ベクトルとして頻繁に使用するもう一つのポイントは、電話機そのものです。Asterisk をインストールする多くの人は、電話機の Web インターフェースのデフォルトパスワードを変更しません。これらの電話機がインターネットに公開されると、ハッカーはデフォルトのインターフェースパスワードを使用して設定をダウンロードし、多くの場合、そこに記載されている秘密の SIP パスワードを入手できます。

#### TFTP 窃盗:

TFTP を使用して電話機の自動プロビジョニングを行っている場合、この種の攻撃に対して脆弱である可能性が高いです。TFTP は、ファイル転送プロトコルの単純かつ安全でない形式です。

![攻撃者が TFTP サーバーから推測可能な .cfg ファイルをダウンロードし、設定ファイルから平文の認証情報を収集している様子](../images/19-security-fig04.png)

設定ファイルの名前は、MAC アドレスの後に .cfg を付けることで簡単に推測できます（例: 001A2B3C4D5E.cfg）。賢いハッカーなら、すべての MAC アドレスを順番に試すユーティリティを簡単に作成したり、単にそれを行うためのツールをダウンロードしたりできます。設定ファイルは通常暗号化されておらず、内部に秘密の SIP パスワードが含まれています。

#### ブルートフォース攻撃と TFTP 窃盗の緩和策

これらの攻撃を緩和するために、以下の解決策を適用できます。ブルートフォース：ブルートフォース攻撃を緩和するための最善の解決策は、連続した不正な試行を防ぐことです。ほとんどすべての Asterisk インストーラーは、この目的で fail2ban ユーティリティを使用します。fail2ban は、パスワードやユーザー名が間違っている試行を複数回検出すると、攻撃者の IP を一定時間禁止します。ブルートフォースに対する 2 つ目の対策は、12 文字以上で少なくとも 1 つの特殊文字を含む強力なパスワードを使用することです。TFTP 窃盗：TFTP 窃盗を防ぐには、名前とパスワードを使用して HTTPS を使用するようにプロビジョニングを設定します。ファイルは暗号化されて送信され、名前とパスワードによって攻撃者がファイルをダウンロードしようとするのを防ぎます。

### 盗聴

ほとんどの場合、盗聴は単に検出されないため、この種の攻撃をあまり目にすることはありません。IP 環境において盗聴を検出することは非常に困難です。UCsniff のような無料で利用可能なユーティリティは、ほとんどのネットワークで VoIP 通話を盗聴できます。主な手法は、ARP スプーフィングを使用してトラフィックを UCsniff を実行しているコンピュータ経由で強制的に流し、通話を記録することです。

#### 盗聴の緩和策

VoIP トラフィックを暗号化することで盗聴を防ぐことができます。もう一つの方法は、ネットワーク上での中間者攻撃（MITM）を防ぐことです。ARP インスペクションは、レイヤー 2 ネットワークでの MITM を防ぐのに非常に効果的です。実装方法については、ネットワークの技術サポートに確認してください。本書の後半では、TLS と SRTP に基づく暗号化のインストール方法を学びます。また、ARPWatch を使用して、誰かが ARP プロトコルを悪用してネットワークを攻撃していないかを確認することもできます。

## Asterisk のセキュリティポリシー

セキュリティを実装する最善の方法は、セキュリティポリシーを作成することです。このトレーニングでは、ほとんどの Asterisk インストールに推奨されるセキュリティポリシーを提案します。これをベースラインとして使用し、必要に応じて変更してください。推奨されるセキュリティポリシーは以下の通りです。 1. 不要な UDP/TCP ポートを開かない 2. インターネット上に管理インターフェース（SSH/HTTPS）へのアクセスを公開しない 3. SSH および/または HTTP/HTTPS にアクセスするには、IPTABLES ファイアウォールで明示的な例外を設定する必要がある 4. 12 文字以上で少なくとも 1 つの特殊文字を含む強力なパスワードを使用する 5. Fail2ban を使用して、認証に 10 回以上失敗した IP アドレスを禁止する 6. 国際電話にはパスワード確認を必須とする 7. SIP ポートへのアクセスを既知の IP アドレス範囲に制限する。PBX への外部アクセスが必要な場合は、2 つの可能性があります。SBC（Session Border Controller）を使用して DOS/DDOS からサーバーを保護するか、外部アクセスが必要なときは常に VPN を使用してください。SBC や VPN なしでポート 5060 をインターネットに公開したままにすると、DOS/DDOS 攻撃に対して無防備になります。リスクは自己責任です。

### PJSIP 時代の強化（Asterisk 22）

ファイアウォールと Fail2Ban に加え、Asterisk 22 の PJSIP スタックは、セキュリティポリシーの一部とすべきいくつかの設定レベルの制御を提供します。これらは上記のネットワーク制御を補完するものであり（置き換えるものではありません）：

- **エンドポイントごとの認証。** すべてのエンドポイントは、強力で一意な `password` (`auth_type=digest`) を持つ専用の `type=auth` セクションを参照する必要があります。エンドポイント間で認証情報を再利用しないでください。
- **匿名処理が組み込まれています。** PJSIP は、認証失敗時にユーザー名が存在するかどうかを明らかにしません。匿名通話を許可するには、明示的に `anonymous` という名前のエンドポイントを作成し、既知のピアをエンドポイントにマッピングするために（ソース IP で一致させる） `type=identify` セクションを使用する必要があります。匿名通話を許可したくない場合は、単に `anonymous` エンドポイントを作成しないでください。そうすれば、一致しないリクエストはチャレンジ/拒否されます。
- **ACL。** エンドポイントから参照される `/etc/asterisk/acl.conf` という名前の ACL を使用して、誰がエンドポイントに到達できるかを制限します（`acl=`（シグナリング/ソース ACL）および `contact_acl=`（コンタクト/登録アドレスを制限））。また、エンドポイント上で直接 permit/deny を設定することもできます。
- **`qualify`。** AOR に `qualify_frequency` (および `qualify_timeout`) を設定し、Asterisk が登録済みコンタクトの到達可能性を能動的に監視し、切断されたものを削除するようにします。
- **PJSIP トランスポートの強化 / DoS 保護。** `type=transport` はトランスポートごとのクライアント上限を公開していないため、接続フラッド保護は PJSIP オプションではなくファイアウォール（本章の iptables/Fail2Ban ルール）によって行われます。トランスポートが提供するのは、切断された/半開きの接続を回収するための TCP キープアライブ調整（`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`）と、正しい NAT 処理のための `local_net`/`external_*` 設定です。これらをファイアウォールルールと組み合わせて、接続フラッド攻撃を緩和してください。
- **メディア用の TLS + SRTP。** TLS トランスポートでシグナリングを暗号化し、エンドポイント上で `media_encryption=sdes` (または WebRTC 用の `dtls`) でメディアを暗号化します。これについては本章の後半で解説します。
- **AMI/ARI アクセス制御。** Asterisk Manager Interface (`manager.conf`) および ARI (`ari.conf` / `http.conf`) へのアクセスを localhost または信頼された管理ネットワークに制限し、強力で一意なシークレットを使用し、HTTP サーバーをプライベートインターフェースにバインドし、これらを決してインターネットに公開しないでください。

> **[2nd-ed note]** 印刷前に、テスト対象のビルドの Asterisk 22 PJSIP 設定リファレンスと照らし合わせて、正確な PJSIP トランスポートオプション名（`tcp_keepalive_*` ファミリー、`tos`/`cos`、`local_net`）および `type=identify` / `acl` / `contact_acl` 構文を確認してください。Asterisk 22 では `res_pjsip` トランスポートに `max_clients` オプションは**ありません**ので注意してください。

### 不要なポートの削除

Asterisk のすべてのプロトコルに関連するすべての脆弱性を発見する代わりに、不要なポートを削除して問題を単純化しましょう。Asterisk サーバーによって開かれているすべてのポートをリストするには、以下を使用します。

```
netstat –pantu |grep asterisk
```

コマンドの出力は以下の通りです。

![netstat の出力。4569 (IAX) や 2727 (MGCP) を含む、Asterisk がバインドしている多くのポートが表示されている](../images/19-security-fig05.png)

出力を見ると、多くのポートが開いていることがわかります。これらは必要でしょうか？必ずしもそうではありません。2727 は MGCP プロトコル (chan_mgcp)、4569 は IAX (chan_iax2) です。これらのプロトコルを使用していない場合は、設定ファイル modules.conf でモジュールを削除するだけで済みます。

Asterisk が大きな番号の UDP ポートをバインドしていることに気づくかもしれません。これは `res_pjsip` のリゾルバーがアウトバウンド DNS クエリを行っているためであり（ソースポートはクライアントの DNS ルックアップと同様にエフェメラルです）、インバウンドリスナーによるものではありません。ファイアウォールでは、これに対する **確立済み/関連（established/related）** の戻りトラフィックのみを許可する必要があります（以下に示す iptables `conntrack ESTABLISHED,RELATED` ルールですでにカバーされています）。PJSIP DNS のためだけに、広いインバウンド高 UDP 範囲を開く必要は**ありません**。

不要なポートを削除するには、使用しないモジュールを無効にします。modules.conf ファイルを編集し、使用していないチャネルとプロトコルの `noload` 行を追加します。**`res_pjsip`、`res_pjproject`、または `chan_pjsip` は noload しないでください**。これらは Asterisk 22 で SIP に必要です。

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 — keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

（Asterisk 22 では `chan_mgcp` や `chan_skinny` を noload する必要はもうありません。これらのドライバは Asterisk 21 で *削除* されており、標準の 22 ビルドには含まれていません。）上記の手順により、不要なチャネルをすべて削除し、PJSIP のみを保持しました。必要なプロトコルモジュールは自由に選択できますが、使用しないものは削除してください。結果は下のスクリーンショットの通りです。PJSIP トランスポートによってバインドされた SIP ポート (5060) のみがインバウンドに公開されています。

![未使用モジュールを無効にした後の netstat 出力：Asterisk によってバインドされているのは UDP ポート 5060 のみ](../images/19-security-fig06.png)

### IPTABLES によるセキュリティポリシーの実装

IPTABLES または netfilter は、ほとんどの Linux ディストリビューションに存在する標準的なファイアウォールです。このラボでは、iptables と fail2ban を設定します。目的は、Asterisk の推奨セキュリティポリシーを実装し、すべての不要なトラフィックをブロックすることです。以下の手順に従ってください： 1 – すべての外部トラフィックをブロックする 2 – 内部ネットワークまたは単一ホストからの SSH トラフィックを許可する 3 – UDP および TCP のポート 5060 での SIP トラフィックを許可する 4 – UDP メディアポート範囲での RTP トラフィックを許可する。単一の組み込みデフォルトはありません。Asterisk 自身の `rtp.conf` は何も設定されていない場合 5000–31000 ポートにフォールバックしますが、出荷時の `rtp.conf.sample` は `rtpstart=10000` / `rtpend=20000` を設定するため、ここではその例の範囲を使用します。ファイアウォールルールを、実際に `rtp.conf` で設定した `rtpstart`/`rtpend` に合わせてください。サーバーへのコンソールアクセス権があることを確認してください。システムから自分自身を締め出したくはないはずです。注意してください。ステップ 1 - net-persistent パッケージをインストールします。

```
sudo apt-get install iptables-persistent
```

ステップ 2 - ループバックからのすべてのトラフィックを許可します

```
sudo iptables -I INPUT -i lo -j ACCEPT
sudo iptables -I OUTPUT -o lo -j ACCEPT
```

ステップ 3 - 確立された接続を許可します

```
sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

ステップ 4 - ネットワーク 192.168.0.0 からの SSH/HTTPS トラフィックを許可します

```
sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
NEW,ESTABLISHED -j ACCEPT
sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
NEW,ESTABLISHED -j ACCEPT
```

ステップ 5 - Asterisk ルールを挿入します

```
sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
```

ポート 5061 (TLS 経由の SIP) は UDP ではなく **TCP** であることに注意してください。上記のルールは 5060 を UDP と TCP の両方で、5061 を TCP で開きます。TLS のみを使用する場合は、プレーンな 5060 ルールを完全に削除できます。PJSIP トランスポートが実際にバインドしているポートのみを開いてください。

-I は PREPEND を意味します ステップ 6 - 最後のルールはドロップである必要があります

```
sudo iptables -A INPUT -j DROP
```

-A は APPEND を意味します 注：新しいルールを維持するときは注意してください。DROP の前に追加する必要があります。新しいルールには PREPEND (-I) を使用してください。ステップ 7 - ルールを保存し、iptables を再起動します

```
sudo iptables-save >/etc/iptables/rules.v4
sudo /etc/init.d/netfilter-persistent restart
```

### Fail2Ban を使用して認証失敗をブロックする

Fail2Ban は Asterisk の標準に近い存在です。ほとんどのユーザーがセキュリティを強化するために実装しています。このユーティリティは Asterisk ログで失敗した試行をスキャンし、攻撃者の IP アドレスを禁止します。以下に Fail2Ban をインストールする手順を示します。

Asterisk 22 では、PJSIP は認証失敗やその他のセキュリティイベントを Asterisk **セキュリティイベントフレームワーク** を通じて報告し、専用の **`security` ロガーチャネル** に書き込みます。Fail2Ban を機能させるには、以下を行う必要があります：

1. `/etc/asterisk/logger.conf` でセキュリティチャネルを有効にします。例：

```
[logfiles]
security => security
```

次に、CLI から `module reload logger` (または `logger reload`) を実行します。これにより、以下のような行を含む `/var/log/asterisk/security` が生成されます：`SecurityEvent="InvalidPassword"`、`ChallengeResponseFailed`、および `InvalidAccountID`。それぞれに攻撃者の `RemoteAddress=` が含まれています。

2. `asterisk` ジェイルをそのファイル (`logpath = /var/log/asterisk/security`) に向け、セキュリティイベント形式と `res_pjsip` 認証失敗イベントを解析するフィルターを使用します。

最新の Fail2Ban には `asterisk` フィルターが付属しており、最新の PBX ディストリビューション（FreePBX/Sangoma）には、PJSIP/セキュリティイベントログ形式をすでに理解している更新済みのフィルターが付属しています。それらを使用することを推奨します。

> **[2nd-ed note]** `asterisk` フィルターの正確な正規表現 / `failregex`、正確な `logger.conf` 構文、および正確なセキュリティイベント行形式は、印刷前に著者がテストする Fail2Ban バージョンおよび Asterisk 22 ビルドと照らし合わせて確認する必要があります。これらの文字列はバージョン間で変更されています。

以下に Fail2Ban をインストールする手順を示します。ステップ 1 – Linux に fail2ban をインストールします

```
sudo apt-get install fail2ban
```

ステップ 2 - Asterisk および SSH 用の fail2ban を有効にします

```
sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
```

ssh および asterisk 用の fail2ban を有効にするために以下の行を追加します

```
[sshd]
enabled = true
[asterisk]
enabled=true
```

ステップ 3 - fail2ban を再起動します

```
/etc/init.d/fail2ban restart
```

ステップ 4 - 検証。ソフトフォンからシークレットを変更し、10 回再登録を試みます。iptables -L を使用して、ソフトフォンのアドレスがブロックされたアドレスとして含まれているか確認します。ステップ 5 - 禁止からアドレスを削除します（アドレスが 192.168.0.5 であると仮定）

```
sudo fail2ban-client set asterisk unbanip 192.168.0.5
```

注：コマンド内の 192.168.0.5 を電話機の IP アドレスに置き換えてください。

### TLS と SRTP の実装

このセクションを 2 つに分けます。前半ではシグナリングを暗号化するための TLS を、後半ではメディアを暗号化するための SRTP を扱います。ここでの目的は、これらのリソースのために Asterisk を設定することです。

#### TLS

TLS (Transport Layer Security) は、SIP シグナリングを保護するために定義された暗号化メカニズムです。攻撃の種類 保護 シグナリング攻撃 YES TLS はメッセージの整合性を保証します 中間者攻撃 YES TLS はサーバー証明書をチェックします 盗聴 NO TLS はシグナリングを暗号化しますが、メディアは暗号化しません。メディア（音声/ビデオ）の暗号化には SRTP を使用してください。

#### 自己署名デジタル証明書

使用できる証明書には、自己署名証明書と商用証明書の 2 種類があります。自己署名証明書は独自のサーバーによって署名され、商用証明書は外部の認証局によって署名されます。VoIP の場合、あなた自身が認証局になることができます。GoDaddy や Verisign のような外部証明書は不要であり、無駄な出費です。ast_tls_cert を使用して独自の証明書を生成します。

#### 自己署名証明書による TLS の設定

以下は TLS を実装するためのステップバイステップガイドです。まず証明書を生成し、次に PJSIP TLS トランスポートを設定し（「Configuring TLS with chan_pjsip」を参照）、最後にソフトフォンをそれらに向けます。TLS と SRTP をネイティブでサポートする SipPulse Softphone を使用します。（TLS/SRTP 対応の SIP ソフトフォンであればどれでも同じように動作します。）ステップ 1. 認証局用に 4096 ビット長の 3DES 暗号化を使用したプライベート RSA キーを作成します。/usr/src/asterisk-22.x.y/contrib/scripts にある以下のコマンドは、認証局と Asterisk 証明書を作成します。通常通り、必要に応じて手順を調整してください。バージョンやディレクトリは変更される可能性があります。何をしているか注意してください。–C オプションにはドメインまたは IP アドレスを使用してください。ast_tls_cert コマンドには 3 つのオプションがあります。

- -C ホストまたは IP アドレス（私は VM の IP アドレスである 192.168.0.74 を使用しました）
- -O 組織名
- -d キーを保存するディレクトリ

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
/ast_tls_cert -C 192.168.0.74 -O "Asteriskguide" -d /etc/asterisk/keys
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
./ast_tls_cert
-C
192.168.0.74
-O
"AsteriskGuide"
-d
/etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 1024 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

クライアント証明書を使用してクライアントを認証するわけではないため、クライアント証明書は生成しません。クライアントは独自の証明書を提示する必要はありません。ステップ 2: TLS 経由でクライアントをサポートするように Asterisk を設定します。これは `pjsip.conf` で行われます（TLS トランスポートとエンドポイント設定）。完全な設定は次のセクション「Configuring TLS with chan_pjsip」で示します。証明書を使用して認証するのではなく、トラフィックを暗号化するだけです。

ステップ 3: TLS 対応の SIP ソフトフォンをインストールします（著者は SipPulse Softphone を使用）。ステップ 4: ソフトフォンを実行しているコンピュータに認証局をコピーします。インストール後、自己署名証明書を使用している場合は、/etc/asterisk/keys/ca.crt ファイルをソフトフォンを実行しているコンピュータにコピーします（scp、または Windows の場合は WinSCP を使用）。ステップ 5: ソフトフォンでアカウントを作成します。アカウント画面で、他の SIP アカウントと同様に通常通りアカウントを追加します。正しいパスワードを使用してください。認証は依然としてパスワードに基づいています。ステップ 6: アカウント設定でトランスポートとして TLS を設定します。SipPulse Softphone のアカウント画面（下図）で、トランスポートとして **TLS** を選択し、ポート 5061 を使用します。ファイアウォールを調整して TCP ポート 5061 を開きます。

![SipPulse Softphone アカウント画面 — サーバー（Asterisk の IP またはドメイン）、ユーザー名、パスワード、表示名を入力し、トランスポート（UDP、TCP、または TLS）を選択します。](../images/softphone/sipphone-account.png){width=35%}

ステップ 7: 認証局を信頼します。Asterisk の TLS 証明書がパブリック CA（例えば Let's Encrypt — *Deployment* の章を参照）によって署名されている場合、SipPulse Softphone のような最新のソフトフォンは、システム証明書ストアを通じて自動的に信頼するため、手動インポートは不要です。自己署名証明書を使用する場合は、その CA (`/etc/asterisk/keys/ca.crt`) をクライアントまたはオペレーティングシステムの信頼ストアにインポートするか、プロンプトが表示されたら受け入れてください。

ステップ 8: クライアント証明書は**不要**です。各電話機が認証のために独自の証明書を必要とするという一般的な誤解がありますが、そうではありません。この時点で Asterisk はセッションを *暗号化* するだけであり、認証は依然としてユーザー名とパスワードです。Asterisk はデフォルトでクライアント証明書を検証しないため、クライアントごとに証明書を配布する必要はありません。

ステップ 9: 証明書またはトランスポートを変更した後、ソフトフォンを完全に再起動（ウィンドウを閉じるだけでなく、終了して再起動）し、新しいトランスポート経由で再接続するようにします。

### Configuring TLS with chan_pjsip

次に、PJSIP で TLS を設定する方法を学びます。PJSIP は Asterisk 22 における唯一の SIP チャネルであるため、切り替える必要はありません。単に `res_pjsip`、`res_pjproject` および `chan_pjsip` がロードされていることを確認してください。ステップ 1: /etc/asterisk/modules.conf で PJSIP が有効になっていることを確認します。

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

ステップ 2: TLS をサポートするように PJSIP を設定します。/etc/asterisk/pjsip.conf ファイルに TLS トランスポート用のセクションを追加します。

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

`method=tlsv1_2` (または OpenSSL/PJSIP ビルドがサポートしている場合は `tlsv1_3`) を使用してください。TLS 1.0/1.1 は時代遅れで安全ではないため、使用すべきではありません。

ステップ 3: blink 用のエンドポイントを設定します。pjsip.conf を編集し、blink 用のセクションを編集します。pjsip が自動的にトランスポートを選択するようにします。

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

ステップ 4: 検証。登録が TLS 経由で行われたかどうかを確認するには、Asterisk コンソールで次のコマンドを使用します。

```
CLI>pjsip show aor blink
asterisk*CLI> pjsip show aor blink
      Aor:  <Aor..............................................>  <MaxContact>
    Contact:
```

- <Aor/ContactUri............................>

```
<Hash....>
<Status> <RTT(ms)..>
============================================================================
==============
      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual
nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
```

- contact
- :

```
sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 mailboxes            :
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 outbound_proxy       :
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
 voicemail_extension  :
```

### SRTP を使用した安全な通話

メディア暗号化を担当するプロトコルは、RFC3711 で定義されている Secure Real Time Protocol (SRTP) です。このプロトコルの欠点の一つは、鍵を交換するための標準化された方法が欠如していることです。Asterisk は、TLS によって提供されるシグナリング暗号化によって保護された SDP プロトコル上で SDES 交換鍵を使用します。MIKEY や ZRTP などの他の方法もあります。Philipp Zimmermann によって開発された ZRTP は、鍵交換とメディア暗号化のための最も洗練された方法の一つです。一部のソフトフォンやハードフォンは ZRTP を許可しています。しかし、標準的な方法は依然として SDES であり、市場で入手可能なほとんどの電話機でこの方法を見つけることができます。以下は、SDP 内の a=crypto:1 および a=crypto:2 行で暗号鍵が定義されたリクエストの例です。

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### Asterisk での SRTP の設定

Asterisk で SRTP を設定するのは非常に簡単です。エンドポイントで `media_encryption=sdes` を設定します。また、暗号化されていないメディアが黙って許可されるのではなく拒否されるように、`media_encryption_optimistic=no` で必須にすることもできます。SDES はシグナリングが TLS 経由で実行されることを必要とするため、鍵が平文で送信されることはありません。ステップ 1: Asterisk の設定

`pjsip.conf` の `type=endpoint` セクションで以下を設定します：

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

ステップ 2: ソフトフォンの設定

ソフトフォンで、アカウントメディアの SRTP を有効にします（**SRTP (Media Encryption)** オプションを *Mandatory* に設定）。これにより音声が暗号化されます。

![SipPulse Softphone アカウント設定（下部） — **Transport** を TLS に、**SRTP (Media Encryption)** を *Mandatory* に設定し、シグナリングとメディアの両方が暗号化されるようにします。](../images/softphone/sipphone-config.png){width=35%}

## 国際電話に対する双方向認証の有効化

国際ルートを持たないことが最善の方法である場合があります。しかし、どうしても国際電話をかける必要がある場合は、追加のパスワードを使用してください。Asterisk アプリケーション vmauthenticate を使用して、国際電話をかける前にボイスメールパスワードを要求します。これは extensions.conf のダイヤルプランで設定されます。以下の例を参照してください。これにより、ハッカーがピアパスワードを発見したり電話機を侵害したりした後でも、この宛先に発信するにはボイスメールパスワードが必要になります。

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

> **[2nd-ed note]** `VMAuthenticate` は Asterisk 22 でも有効です。元の例では `DAHDI/g1/...` にダイヤルしていましたが、最近のほとんどのインストールでは国際電話は SIP/PJSIP トランク経由でルーティングされるため、上記の `Dial()` は `PJSIP/<number>@<trunk>` を使用しています。トランク名はセットアップに合わせて調整してください（`DAHDI/...` は実際に DAHDI スパンがある場合のみ使用してください）。ダイヤルプランでの通話詐欺防御（このような第 2 要素認証に加え、どのコンテキストがアウトバウンド/国際ルートに到達できるかを制限すること）は、依然として最も重要な保護の一つです。

## まとめ

本章では、IP PBX をインターネットに接続するリスクについて学びました。次に、セキュリティポリシーを実装して PBX を保護する方法を学びました。このセキュリティポリシーでは、iptables、fail2ban、TLS、SRTP、および国際電話に対する双方向認証を実装しました。本章を楽しんでいただけたなら幸いです。

## クイズ

1. インターネット収益分配詐欺に対する最も重要な対策は何ですか？
   - A. SRTP を実装する
   - B. Asterisk を最新に保つ
   - C. TLS を実装する
   - D. 強力なパスワードを使用する
2. SIP ファジングは次のように定義されます：
   - A. 不正なリクエストと応答を使用した DoS 攻撃
   - B. パスワードがブルートフォースされるサービス窃盗
   - C. 現在の通話の盗聴
   - D. SIP リクエストのフラッドによる DDoS
3. TFTP 窃盗は、サーバーが TFTP 経由で設定ファイルを提供するときに発生します。これを回避するには：
   - A. FTP を使用する
   - B. HTTP を使用する
   - C. ユーザー名とパスワード付きの HTTPS を使用する
   - D. SCP を使用する
4. 中間者攻撃は、次のどの技術を使用しますか：
   - A. TFTP 窃盗
   - B. ARP スプーフィング
   - C. MAC ポイズニング
   - D. dsniff
5. SRTP のために、Asterisk は鍵交換に次のどのシステムを使用しますか：
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. `/usr/src/asterisk-22.x.y/contrib/scripts` にある、認証局と証明書を生成するユーティリティは：
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. 盗聴を防ぐための有効な戦略（該当するものすべてを選択）：
   - A. アナログ盗聴検出器を実装する
   - B. ARPwatch ユーティリティを使用して ARP スプーフィングを検出する
   - C. スイッチで ARP スプーフィング検出を有効にする
   - D. SRTP を使用する
8. Asterisk はクライアント証明書を検証することで強力な認証をサポートしています。（PJSIP TLS トランスポートはクライアントの証明書を要求および検証できます。）
   - A. True
   - B. False
9. Asterisk 22 で、in-SDP (SDES) 鍵を使用して SRTP メディア暗号化をオンにする PJSIP エンドポイント設定はどれですか？
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. Asterisk 22 では、Fail2Ban は専用の ________ ロガーチャネル（`logger.conf` で有効化）から PJSIP 認証失敗イベントを読み取る必要があります。
    - A. `console`
    - B. `messages`
    - C. `security`
    - D. `verbose`

**回答:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
