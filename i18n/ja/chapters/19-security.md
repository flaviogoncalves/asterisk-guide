# Asterisk セキュリティ

Asterisk のセキュリティ問題は、その誕生以来、極めて重要です。CERT.BR によると、SIP（Session Initiation Protocol）はインターネット上で最も攻撃を受けているプロトコルです。ハニーポットを運用している人なら誰でもそれを確認できるでしょう。インターネット収益分配詐欺（Internet Revenue Share Fraud）の問題は非常に深刻で、数十万ドルを超える損失につながる可能性があります。適切なセキュリティ対策なしに、インターネットに接続された Asterisk サーバーをインストールしてはなりません。本章では、受ける可能性のある主な攻撃の種類を特定する方法と、適切なセキュリティポリシーを用いてそれらを防ぐ方法を学びます。最後に、提案されたセキュリティポリシーを実装する方法を学びます。

本章は **Asterisk 22 LTS** を対象としており、PJSIP（`res_pjsip` / `chan_pjsip`）が唯一の SIP チャネルとなります。（古い `chan_sip` ドライバは Asterisk 21 で削除されました。古いシステムから移行する場合は「レガシーチャネル」の章を参照してください。）セキュリティに関連する重要な変更点として、認証失敗は Asterisk の **セキュリティイベントフレームワーク** および専用の `security` ロガーチャネルを通じて出力されるようになりました。これにより、Fail2Ban の設定方法が変更されています（本章の後半で解説します）。

## 学習目標

本章を終えると、以下のことができるようになります。

- Asterisk サーバーに対して頻繁に行われる主な攻撃の種類を特定する
- 効果的なセキュリティポリシーを定義する
- セキュリティポリシーを実装する
- Asterisk 用の IPTABLES をインストールおよび設定する
- Asterisk 用の Fail2Ban をインストールおよび設定する
- 暗号化のために TLS および SRTP をインストールおよび設定する

## IP 電話に対する主な攻撃

IP 電話に対する主な攻撃は、DoS/DDoS、サービス窃盗/通話詐欺、盗聴に分類できます。名称が紛らわしい場合があり、情報源によって同じ攻撃でも異なる名前で呼ばれることがあります。サービス窃盗、通話詐欺、インターネット収益分配詐欺、電話詐欺などは、ハッカーがあなたの PBX を悪用してプレミアムレート番号へトラフィックを流し、プロバイダーからリベートを得るための異なる呼び名です。

### DDoS/DOS

サービス拒否（DoS）および分散型サービス拒否（DDoS）は、あらゆる IT インフラに対する一般的な攻撃です。SIP やその他の VoIP プロトコルも例外ではありません。分散型サービス拒否は通常ボットネットによって実行され、DoS は単一のコンピュータによって実行されます。2011年2月、Sality ボットネットは、脆弱な SIP サーバーを探して IPv4 アドレス空間全体を隠密かつ組織的にスキャンしました。UCSD Network Telescope で観測した研究者は、UDP ポート 5060 を調査していた約300万の異なるソース IP を特定し、そのほとんどが通話詐欺を目的とした SIP アカウントのブルートフォース攻撃であると結論付けました。[^sality]

[^sality]: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![サーバーに対して数千もの SIP 登録試行を向けるピアツーピアボットネット](../images/19-security-fig01.png)

DoS は通常、ファジングやフラッディングといった手法を通じて行われます。フラッディングには SIP、IAX、RTP などのプロトコルが使用されます。これらはサービスを完全に停止させたり、音声品質を低下させたりする可能性があります。ポートがインターネットに公開されている場合、これらの攻撃を緩和するのは非常に困難です。以下に、攻撃者が使用するツールの一部を挙げます。

**ファジング:**

- **PROTOS Test Suite (c07-sip)** — オウル大学 OUSPG によるもの。数千の不正なパケットを送信し、ソフトウェアを停止させるバッファオーバーフローなどの誤動作を引き起こします。
- **Voiper** — すべての SIP 属性を網羅する 200,000 以上のテストを生成し、サーバーがメッセージを効果的に処理できるかを検証します。<http://voiper.sourceforge.net/>

**フラッディング:**

- **INVITE Flooder** — SIP INVITE リクエストでサーバーをフラッド攻撃します。<http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — IAX2 トラフィックでサーバーをフラッド攻撃します。<http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — RTP パケットでアクティブなメディアセッションをフラッド攻撃し、音声品質を低下させます。<http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### DoS/DDoS の緩和技術

推奨事項は以下の通りです。

1. 適切な保護（SBC）なしに Asterisk サーバーをインターネットに公開しないこと。 2. 内部ネットワークでは、特にユーザー数が多い大学やカレッジなどでは、音声用に仮想 LAN（VLAN）を使用すること。 3. 外部アクセスには VPN または TLS を使用すること。

### インターネット収益分配詐欺

この詐欺は少し理解しにくいものです。鍵となるのは、国際プレミアムレート番号（IPRN）の概念を理解することです。

![インターネット収益分配詐欺の3ステップ：プレミアムレート番号を購入し、脆弱な VoIP デバイスを見つけてその番号に発信し、報酬を受け取る](../images/19-security-fig02.png)

IPRN とは、特定のインターネット電話会社で無料で割り当てられる番号です。「Internet Premium Rate Number Providers」で検索すれば、多数のプロバイダーが見つかります。この種の事業者では、例えばイリジウムのような衛星ネットワークの番号を割り当てることができ、発信者にとって 1 分あたり数十ドルのコストがかかります。IPRN プロバイダーは、着信した 1 分ごとに収益の一定割合（10〜20%）をあなたに還元します。

![国別の支払いレートとテスト番号を示す IPRN プロバイダーの価格表](../images/19-security-fig03.png)

割り当てフェーズの後、ハッカーは割り当てられた IPRN に発信できるオープンな Asterisk サーバーを探します。ハッカーに制御された被害者の PBX は、IPRN 番号に対して数百回の通話を行い、ハッカーには多額の報酬を、被害者には莫大な電話料金を発生させます。多くの場合、週末だけで数十万ドルを超えることもあります。ハッカーが PBX を攻撃するために使用する主なツール： 1. SIPVicious: http://code.google.com/p/sipvicious/。Sipvicious は使いやすいセキュリティツールセットです。主な目的は、脆弱な PBX を認識し、ブルートフォース攻撃を使用して SIP パスワードを解読することです。最も使用されるツールは svcrack です。このツールは 1 秒間に数千のパスワードをテストできます。 2. 電話機の脆弱性。ハッカーが攻撃ベクトルとして頻繁に使用するもう一つのポイントは、電話機そのものです。Asterisk をインストールする多くの人は、電話機の Web インターフェースのデフォルトパスワードを変更しません。これらの電話機がインターネットに公開されると、ハッカーはデフォルトのインターフェースパスワードを使用して設定をダウンロードし、多くの場合、そこに記載されている秘密の SIP パスワードを入手できます。

#### TFTP 窃盗:

TFTP を使用して電話機の自動プロビジョニングを行っている場合、この種の攻撃に対して脆弱である可能性が高いです。TFTP は、単純で安全性の低いファイル転送プロトコルです。

![攻撃者が TFTP サーバーから推測可能な .cfg ファイルをダウンロードし、設定ファイルから平文の認証情報を収集している様子](../images/19-security-fig04.png)

設定ファイルの名前は、MAC アドレスに .cfg を付けたもの（例: 001A2B3C4D5E.cfg）であり、容易に推測可能です。賢いハッカーなら、すべての MAC アドレスを順番に試すユーティリティを簡単に作成するか、単にそれを行うツールをダウンロードするでしょう。設定ファイルは通常暗号化されておらず、内部に秘密の SIP パスワードが含まれています。

#### ブルートフォース攻撃および TFTP 窃盗の緩和策

これらの攻撃を緩和するために、以下の解決策を適用できます。ブルートフォース：ブルートフォース攻撃を緩和するための最善の解決策は、連続した不正な試行を防ぐことです。ほぼすべての Asterisk インストーラーは、この目的のために fail2ban ユーティリティを使用しています。fail2ban は、パスワードやユーザー名が間違っている試行を複数回検出すると、攻撃者の IP を一定時間禁止します。ブルートフォースに対する2つ目の対策は、12文字以上で少なくとも1つの特殊文字を含む強力なパスワードを使用することです。TFTP 窃盗：TFTP 窃盗を防ぐには、名前とパスワードを使用して HTTPS を使用するようにプロビジョニングを設定します。ファイルは暗号化されて送信され、名前とパスワードによって攻撃者がファイルをダウンロードしようとするのを防ぎます。

### 盗聴

この種の攻撃は、ほとんどの場合検出されないため、あまり目にする機会がありません。IP 環境において盗聴を検出することは非常に困難です。UCsniff のような無料で利用可能なユーティリティは、ほとんどのネットワークで VoIP 通話を盗聴できます。主な手法は、ARP スプーフィングを使用してトラフィックを UCsniff を実行しているコンピュータ経由で強制的に流し、通話を録音することです。

#### 盗聴の緩和策

VoIP トラフィックを暗号化することで盗聴を防ぐことができます。もう一つの方法は、ネットワーク上での中間者攻撃（MITM）を防ぐことです。ARP インスペクションは、レイヤー 2 ネットワークでの MITM を防ぐのに非常に効果的です。実装方法については、ネットワークの技術サポートに確認してください。本書の後半では、TLS と SRTP に基づく暗号化のインストール方法を学びます。また、ARPWatch を使用して、誰かが ARP プロトコルを悪用してネットワークを攻撃していないかを確認することもできます。

## Asterisk のセキュリティポリシー

セキュリティを実装する最善の方法は、セキュリティポリシーを作成することです。このトレーニングでは、ほとんどの Asterisk インストールに推奨されるセキュリティポリシーを提案します。これを基本として使用し、必要に応じて変更してください。推奨されるセキュリティポリシーは以下の通りです。 1. 不要な UDP/TCP ポートを開かない 2. インターネット上に管理インターフェース（SSH/HTTPS）へのアクセスを公開しない 3. SSH および/または HTTP/HTTPS にアクセスするには、IPTABLES ファイアウォールで明示的な例外が必要 4. 12文字以上で少なくとも1つの特殊文字を含む強力なパスワード 5. Fail2ban を使用して、認証に10回以上失敗した IP アドレスを禁止する 6. 国際電話にはパスワード確認を必須とする 7. SIP ポートへのアクセスを既知の IP アドレス範囲に制限する。PBX への外部アクセスが必要な場合は、2つの可能性があります。SBC（Session Border Controller）を使用して DoS/DDoS からサーバーを保護するか、外部アクセスが必要なときは常に VPN を使用してください。SBC や VPN なしでポート 5060 をインターネットに公開したままにすると、DoS/DDoS 攻撃に対して無防備になります。リスクは自己責任です。

### PJSIP 時代の強化（Asterisk 22）

ファイアウォールと Fail2Ban に加え、Asterisk 22 の PJSIP スタックは、セキュリティポリシーの一部とすべきいくつかの設定レベルの制御を提供します。これらは上記のネットワーク制御を補完するものであり、置き換えるものではありません。

- **エンドポイントごとの認証。** すべてのエンドポイントは、強力で一意な `password`（`auth_type=digest`）を持つ専用の `type=auth` セクションを参照する必要があります。エンドポイント間で認証情報を再利用しないでください。
- **匿名処理が組み込まれています。** PJSIP は、認証失敗時にユーザー名が存在するかどうかを明かしません。匿名通話を許可するには、明示的に `anonymous` という名前のエンドポイントを作成し、既知のピアをエンドポイントにマッピングするために（ソース IP で一致させる） `type=identify` セクションを使用する必要があります。匿名通話を許可したくない場合は、単に `anonymous` エンドポイントを作成しないでください。一致しないリクエストはチャレンジ/拒否されます。
- **ACL。** `/etc/asterisk/acl.conf` という名前の ACL を使用してエンドポイントに到達できるユーザーを制限し、エンドポイントから `acl=`（シグナリング/ソース ACL）および `contact_acl=`（コンタクト/登録アドレスを制限）で参照します。エンドポイントで直接 permit/deny を設定することもできます。
- **`qualify`。** AOR に `qualify_frequency`（および `qualify_timeout`）を設定し、Asterisk が登録済みコンタクトの到達可能性を能動的に監視し、切断されたものを削除するようにします。
- **PJSIP トランスポートの強化 / DoS 保護。** `type=transport` はトランスポートごとのクライアント上限を公開していないため、接続フラッド保護は PJSIP オプションではなくファイアウォール（本章の iptables/Fail2Ban ルール）によって行われます。トランスポートが提供するのは、切断された/半開きの接続を回収するための TCP キープアライブ調整（`tcp_keepalive_enable`、`tcp_keepalive_idle_time`、`tcp_keepalive_interval_time`、`tcp_keepalive_probe_count`）と、正しい NAT 処理のための `local_net`/`external_*` 設定です。これらをファイアウォールルールと組み合わせて、接続フラッド攻撃を鈍らせます。
- **メディア用の TLS + SRTP。** TLS トランスポートでシグナリングを暗号化し、エンドポイントで `media_encryption=sdes`（または WebRTC 用の `dtls`）を使用してメディアを暗号化します。これについては本章の後半で説明します。
- **AMI/ARI アクセス制御。** Asterisk Manager Interface（`manager.conf`）および ARI（`ari.conf` / `http.conf`）へのアクセスを localhost または信頼された管理ネットワークに制限し、強力で一意なシークレットを使用し、HTTP サーバーをプライベートインターフェースにバインドし、これらをインターネットに公開しないでください。

上記のすべてのオプション名は Asterisk 22.10 で確認されています：`type=transport` セクションは `tcp_keepalive_enable`、`tcp_keepalive_idle_time`、`tcp_keepalive_interval_time`、`tcp_keepalive_probe_count`、`tos`、`cos`、`local_net`、および `external_*` ファミリーを公開しますが、**`max_clients` オプションはありません**。接続フラッド保護はトランスポートではなくファイアウォールから提供されます。`acl` および `contact_acl` エンドポイントオプションは `acl.conf` からセクション名を取得し、認証されていないピアのソース IP 一致は `type=identify` セクション（`match=`）で行われます。

### 不要なポートの削除

Asterisk のすべてのプロトコルに関連するすべての脆弱性を発見する代わりに、不要なポートを削除して問題を単純化しましょう。Asterisk サーバーによって開かれているすべてのポートをリストするには、以下を使用します。

```
netstat –pantu |grep asterisk
```

コマンドの出力は以下の通りです。

![Asterisk によってバインドされた多数のポート（4569 (IAX) や 2727 (MGCP) を含む）を示す netstat の出力](../images/19-security-fig05.png)

出力を見ると、多くのポートが開いていることがわかります。これらは必要でしょうか？必ずしもそうではありません。2727 は MGCP プロトコル（chan_mgcp）、4569 は IAX（chan_iax2）です。これらのプロトコルを使用していない場合は、設定ファイル modules.conf でモジュールを削除するだけで済みます。

Asterisk が大きな番号の UDP ポートをバインドしていることに気づくかもしれません。これは `res_pjsip` のリゾルバーがアウトバウンドの DNS クエリを行っているためであり（ソースポートはクライアントの DNS ルックアップと同様に一時的なものです）、インバウンドのリスナーではありません。ファイアウォールでは、これに対して **established/related** な戻りトラフィックのみを許可すれば十分です（以下に示す iptables の `conntrack ESTABLISHED,RELATED` ルールがこれをカバーしています）。PJSIP DNS のためだけに、広いインバウンドの UDP 高ポート範囲を開く必要は **ありません**。

不要なポートを削除するには、使用しないモジュールを無効にします。modules.conf ファイルを編集し、使用していないチャネルやプロトコルの `noload` 行を追加します。**`res_pjsip`、`res_pjproject`、または `chan_pjsip` は noload しないでください**。これらは Asterisk 22 で SIP に必要です。

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 — keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

（Asterisk 22 では `chan_mgcp` や `chan_skinny` を noload する必要はありません。これらのドライバは Asterisk 21 で *削除* されており、標準の 22 ビルドには含まれていません。）上記の手順により、不要なチャネルをすべて削除し、PJSIP のみを残しました。どのプロトコルモジュールを選択しても構いませんが、使用しないものは削除してください。結果は下のスクリーンショットの通りです。PJSIP トランスポートによってバインドされた SIP ポート（5060）のみがインバウンドとして公開されています。

![未使用のモジュールを無効にした後の netstat の出力：Asterisk によってバインドされているのは UDP ポート 5060 のみ](../images/19-security-fig06.png)

### IPTABLES によるセキュリティポリシーの実装

IPTABLES または netfilter は、ほとんどの Linux ディストリビューションに存在する標準的なファイアウォールです。このラボでは、iptables と fail2ban を設定します。目的は、Asterisk の推奨セキュリティポリシーを実装し、すべての不要なトラフィックをブロックすることです。以下の手順に従ってください。 1 – すべての外部トラフィックをブロックする 2 – 内部ネットワークまたは単一ホストからの SSH トラフィックを許可する 3 – UDP および TCP のポート 5060 で SIP トラフィックを許可する 4 – UDP メディアポート範囲で RTP トラフィックを許可する。組み込みのデフォルト設定は存在しません。Asterisk 自身の `rtp.conf` は何も設定されていない場合 5000–31000 ポートにフォールバックしますが、出荷時の `rtp.conf.sample` は `rtpstart=10000` / `rtpend=20000` を設定しているため、ここではその範囲の例を使用します。ファイアウォールルールを、実際に `rtp.conf` で設定した `rtpstart`/`rtpend` に合わせてください。サーバーへのコンソールアクセス権があることを確認してください。システムから自分自身を締め出したくはないはずです。注意してください。ステップ 1 - net-persistent パッケージをインストールします。

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

ポート 5061（TLS 上の SIP）は UDP ではなく **TCP** であることに注意してください。上記のルールは 5060 を UDP と TCP の両方で、5061 を TCP で開きます。TLS のみを使用する場合は、プレーンな 5060 ルールを完全に削除できます。PJSIP トランスポートが実際にバインドしているポートのみを開いてください。

-I は PREPEND を意味します ステップ 6 - 最後のルールは DROP にする必要があります

```
sudo iptables -A INPUT -j DROP
```

-A は APPEND を意味します 注：新しいルールを維持する際は注意してください。DROP の前に追加する必要があります。新しいルールには PREPEND（-I）を使用してください。ステップ 7 - ルールを保存し、iptables を再起動します

```
sudo iptables-save >/etc/iptables/rules.v4
sudo /etc/init.d/netfilter-persistent restart
```

### Fail2Ban を使用して認証失敗をブロックする

Fail2Ban は Asterisk の標準に近い存在です。ほとんどのユーザーがセキュリティを強化するために実装しています。このユーティリティは Asterisk のログをスキャンして失敗した試行を検出し、攻撃者の IP アドレスを禁止します。以下に Fail2Ban をインストールする手順を示します。

Asterisk 22 では、PJSIP は認証失敗やその他のセキュリティイベントを Asterisk **セキュリティイベントフレームワーク** を通じて報告し、専用の **`security` ロガーチャネル** に書き込みます。Fail2Ban を機能させるには、以下を行う必要があります。

1. `/etc/asterisk/logger.conf` でセキュリティチャネルを有効にします。構文は `<filename> => <levels>` なので、セキュリティレベルを `security` という名前のファイルに送信するには、以下のように記述します。

```
[logfiles]
security => security
```

次に、CLI から `logger reload` を実行します。これにより、セキュリティイベントごとに 1 行の `/var/log/asterisk/security` が生成されます。形式は以下の通りです。

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

Fail2Ban が監視するイベントは `InvalidPassword`、`ChallengeResponseFailed`、`InvalidAccountID`、および `FailedACL` であり、それぞれが攻撃者を識別する `RemoteAddress="IPV4/UDP/<ip>/<port>"` フィールドを持っています。（アドレスは生の IP ではなく `IPV4/UDP/.../...` としてラップされていることに注意してください。フィルタはその文字列内からホストを抽出する必要があります。）

2. `asterisk` ジェイルをそのファイル（`logpath = /var/log/asterisk/security`）に向け、このセキュリティイベント形式を解析するフィルタを使用します。

最新の Fail2Ban には `asterisk` フィルタが同梱されており、その `failregex` はすでに上記のイベントと一致し、例えば以下のように `RemoteAddress` フィールドから `<HOST>` を抽出します。

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX ディストリビューション（FreePBX/Sangoma）には同等のフィルタが同梱されています。正確なイベント文字列はバージョン依存であるため、自作するよりもパッケージ化されたフィルタを優先してください。注意すべき点として、修正済みの勧告（GHSA-5743-x3p5-3rg7）では、細工された PJSIP トラフィックが偽のログ行を注入できる可能性が示されていました。Asterisk と Fail2Ban フィルタの両方を最新の状態に保ってください。

以下に Fail2Ban をインストールする手順を示します。ステップ 1 – Linux に fail2ban をインストールします

```
sudo apt-get install fail2ban
```

ステップ 2 - Asterisk および SSH 用の fail2ban を有効にします

```
sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
```

ssh と asterisk 用の fail2ban を有効にするために以下の行を追加します

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

ステップ 4 - 検証。ソフトフォンからシークレットを変更し、10回再登録を試みます。iptables -L を使用して、ソフトフォンのアドレスがブロックされたアドレスとして含まれているか確認します。ステップ 5 - 禁止からアドレスを削除します（アドレスが 192.168.0.5 であると仮定）

```
sudo fail2ban-client set asterisk unbanip 192.168.0.5
```

注：コマンド内の 192.168.0.5 は、電話機の IP アドレスに置き換えてください。

### TLS と SRTP の実装

このセクションを2つに分けます。前半ではシグナリングを暗号化するための TLS を、後半ではメディアを暗号化するための SRTP を扱います。ここでの目的は、これらのリソースのために Asterisk を設定することです。

#### TLS

TLS（Transport Layer Security）は、SIP シグナリングを保護するために定義された暗号化メカニズムです。攻撃の種類 保護 シグナリング攻撃 YES TLS はメッセージの整合性を保証します 中間者攻撃 YES TLS はサーバー証明書をチェックします 盗聴 NO TLS はシグナリングを暗号化しますが、メディアは暗号化しません。メディア（音声/ビデオ）の暗号化には SRTP を使用してください。

#### 自己署名デジタル証明書

使用できる証明書には、自己署名と商用の2種類があります。自己署名証明書は自分のサーバーによって署名され、商用証明書は外部の認証局によって署名されます。VoIP の場合、自分自身が認証局になることができます。GoDaddy や Verisign のような外部証明書は不要であり、無駄な出費です。ast_tls_cert を使用して独自の証明書を生成します。

#### 自己署名証明書による TLS の設定

以下は TLS を実装するためのステップバイステップガイドです。まず証明書を生成し、次に PJSIP TLS トランスポートを設定し（「chan_pjsip による TLS の設定」を参照）、最後にソフトフォンをそれらに向けます。ここでは、TLS と SRTP をネイティブでサポートする SipPulse Softphone を使用します。（TLS/SRTP 対応の SIP ソフトフォンであれば同様に動作します。）ステップ 1. 認証局用に 4096 ビット長の 3DES 暗号化を使用したプライベート RSA キーを作成します。/usr/src/asterisk-22.x.y/contrib/scripts にある以下のコマンドは、認証局と Asterisk 証明書を作成します。通常通り、必要に応じて指示を適応させてください。バージョンやディレクトリは変更される可能性があります。何をしているか注意してください。–C オプションにはドメインまたは IP アドレスを使用してください。ast_tls_cert コマンドには3つのオプションがあります。

- -C ホストまたは IP アドレス（ここでは VM の IP アドレスである 192.168.0.74 を使用しました）
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

クライアントを認証するために証明書を使用しないため、クライアント証明書は生成しません。クライアントは独自の証明書を提示する必要はありません。ステップ 2: TLS 経由でクライアントをサポートするように Asterisk を設定します。これは `pjsip.conf`（TLS トランスポートとエンドポイント設定）で行われます。完全な設定は次のセクション「chan_pjsip による TLS の設定」に示されています。ここでは証明書を使用して認証するのではなく、トラフィックを暗号化するだけです。

ステップ 3: TLS 対応の SIP ソフトフォンをインストールします（著者は SipPulse Softphone を使用）。ステップ 4: ソフトフォンを実行しているコンピュータに認証局をコピーします。インストール後、自己署名証明書を使用している場合は、/etc/asterisk/keys/ca.crt ファイルをソフトフォンを実行しているコンピュータにコピーします（scp、または Windows の場合は WinSCP を使用）。ステップ 5: ソフトフォンでアカウントを作成します。アカウント画面で、他の SIP アカウントと同様にアカウントを追加します。正しいパスワードを使用してください。認証は依然としてパスワードに基づいています。ステップ 6: アカウント設定でトランスポートとして TLS を設定します。SipPulse Softphone のアカウント画面（下図）で、トランスポートとして **TLS** を選択し、ポート 5061 を使用します。ファイアウォールを調整して TCP ポート 5061 を開きます。

![SipPulse Softphone のアカウント画面 — サーバー（Asterisk の IP またはドメイン）、ユーザー名、パスワード、表示名を入力し、トランスポート（UDP、TCP、または TLS）を選択します。](../images/softphone/sipphone-account.png){width=35%}

ステップ 7: 認証局を信頼します。Asterisk の TLS 証明書が公開 CA（例えば Let's Encrypt — 「デプロイメント」の章を参照）によって署名されている場合、SipPulse Softphone のような最新のソフトフォンは、手動インポートなしでシステム証明書ストアを通じて自動的に信頼します。自己署名証明書を使用する場合は、その CA（`/etc/asterisk/keys/ca.crt`）をクライアントまたはオペレーティングシステムの信頼ストアにインポートするか、プロンプトが表示されたら受け入れてください。

ステップ 8: クライアント証明書は **不要** です。各電話機が認証のために独自の証明書を必要とするというのは一般的な誤解ですが、そうではありません。この時点で Asterisk はセッションを *暗号化* するだけであり、認証は依然としてユーザー名とパスワードです。Asterisk はデフォルトでクライアント証明書を検証しないため、クライアントごとに証明書を配布する必要はありません。

ステップ 9: 証明書やトランスポートを変更した後は、ソフトフォンを完全に再起動（ウィンドウを閉じるだけでなく、終了して再起動）し、新しいトランスポート経由で再接続するようにしてください。

### chan_pjsip による TLS の設定

次に、TLS 用に PJSIP を設定する方法を学びます。PJSIP は Asterisk 22 における唯一の SIP チャネルであるため、切り替える必要はありません。単に `res_pjsip`、`res_pjproject`、および `chan_pjsip` がロードされていることを確認してください。ステップ 1: /etc/asterisk/modules.conf で PJSIP が有効になっていることを確認します。

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

`method=tlsv1_2`（または OpenSSL/PJSIP ビルドがサポートしている場合は `tlsv1_3`）を使用してください。TLS 1.0/1.1 は時代遅れで安全ではないため、使用すべきではありません。

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

ステップ 4: 検証。登録が TLS 経由で行われたかを確認するには、Asterisk コンソールで以下のコマンドを使用します。

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

メディア暗号化を担当するプロトコルは、RFC3711 で定義されている Secure Real Time Protocol（SRTP）です。このプロトコルの欠点の1つは、鍵を交換するための標準化された方法が欠如していることです。Asterisk は、TLS によって提供されるシグナリング暗号化によって保護された SDP プロトコル上で SDES 交換鍵を使用します。MIKEY や ZRTP などの他の方法もあります。Philipp Zimmermann によって開発された ZRTP は、鍵交換とメディア暗号化のための最も洗練された方法の1つです。一部のソフトフォンやハードフォンは ZRTP を許可しています。しかし、標準的な方法は依然として SDES であり、市場で入手可能なほぼすべての電話機でこの方法を見つけることができます。以下は、SDP の a=crypto:1 および a=crypto:2 行で暗号鍵が定義されたリクエストの例です。

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

Asterisk で SRTP を設定するのは非常に簡単です。エンドポイントで `media_encryption=sdes` を設定します。また、暗号化されていないメディアが黙認されるのではなく拒否されるように、`media_encryption_optimistic=no` で必須にすることもできます。SDES は鍵が平文で送信されないように、シグナリングを TLS 上で実行する必要があることに注意してください。ステップ 1: Asterisk の設定

`pjsip.conf` の `type=endpoint` セクションで以下を設定します。

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

![SipPulse Softphone のアカウント設定（下部） — **Transport** を TLS に、**SRTP (Media Encryption)** を *Mandatory* に設定し、シグナリングとメディアの両方を暗号化します。](../images/softphone/sipphone-config.png){width=35%}

## 国際電話に対する双方向認証の有効化

国際ルートを持たないことが最善の方法である場合もあります。しかし、どうしても国際電話をかける必要がある場合は、追加のパスワードを使用してください。Asterisk アプリケーション vmauthenticate を使用して、国際電話をかける前にボイスメールのパスワードを要求します。これは extensions.conf のダイヤルプランで設定します。以下の例を参照してください。これにより、ハッカーがピアのパスワードを発見したり電話機を侵害したりした後でも、この宛先に発信するにはボイスメールのパスワードが必要になります。

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` は Asterisk 22 でも標準的なアプリケーションです。上記の `Dial()` は、SIP/PJSIP トランク（`PJSIP/<number>@<trunk>`）経由で通話をルーティングします。これは、ほとんどの最新のインストールが PSTN に到達する方法です。ご自身のトランク名に合わせて `my_trunk` を調整し、実際に DAHDI スパンがある場合のみ `DAHDI/g1/...` を使用してください。ダイヤルプランにおける通話詐欺防御 — このような第2の要素と、アウトバウンドおよび国際ルートに到達できるコンテキストの制限を組み合わせることは、展開できる最も重要な保護策の1つです。

## まとめ

本章では、IP PBX をインターネットに接続するリスクについて学びました。次に、セキュリティポリシーを実装して PBX を保護する方法を学びました。このセキュリティポリシーでは、iptables、fail2ban、TLS、SRTP、および国際電話に対する双方向認証を実装しました。本章を楽しんでいただけたなら幸いです。

## クイズ

1. インターネット収益分配詐欺に対する最も重要な対策は何ですか？
   - A. SRTP を実装する
   - B. Asterisk を最新に保つ
   - C. TLS を実装する
   - D. 強力なパスワードを使用する
2. SIP ファジングの定義はどれですか？
   - A. 不正なリクエストと応答を使用した DoS 攻撃
   - B. パスワードがブルートフォースされるサービス窃盗
   - C. 現在の通話の盗聴
   - D. SIP リクエストのフラッドによる DDoS
3. TFTP 窃盗は、サーバーが TFTP 経由で設定ファイルを提供するときに発生します。これを回避する方法は？
   - A. FTP
   - B. HTTP
   - C. ユーザー名とパスワード付きの HTTPS
   - D. SCP
4. 中間者攻撃は、どの技術を使用しますか？
   - A. TFTP 窃盗
   - B. ARP スプーフィング
   - C. MAC ポイズニング
   - D. dsniff
5. SRTP のために、Asterisk は鍵交換にどのシステムを使用しますか？
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. `/usr/src/asterisk-22.x.y/contrib/scripts` にあり、認証局と証明書を生成するユーティリティはどれですか？
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. 盗聴を防ぐための有効な戦略はどれですか（該当するものすべてを選択）：
   - A. アナログ盗聴検出器を実装する
   - B. ARPwatch ユーティリティを使用して ARP スプーフィングを検出する
   - C. スイッチで ARP スプーフィング検出を有効にする
   - D. SRTP を使用する
8. Asterisk はクライアント証明書を検証することで強力な認証をサポートしています。（PJSIP TLS トランスポートはクライアントの証明書を要求および検証できます。）
   - A. True
   - B. False
9. Asterisk 22 で、in-SDP（SDES）鍵を使用して SRTP メディア暗号化をオンにする PJSIP エンドポイント設定はどれですか？
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. Asterisk 22 では、Fail2Ban は専用の ________ ロガーチャネル（`logger.conf` で有効化）から PJSIP の認証失敗イベントを読み取る必要があります。
    - A. `console`
    - B. `messages`
    - C. `security`
    - D. `verbose`

**回答:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
