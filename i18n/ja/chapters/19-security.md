# Asterisk Security

最初から、Asterisk のセキュリティ問題は重要です。SIP（Session Initiation Protocol）は、CERT.BR によるとインターネット上で最も攻撃を受けるプロトコルです。ハニーポットを運用している人なら誰でも確認できます。インターネット収益分配詐欺（Internet Revenue Share Fraud）の問題は非常に深刻で、数十万ドルを超える損失につながる可能性があります。適切なセキュリティ対策なしにインターネットに接続された Asterisk Server をインストールしてはいけません。この章では、受ける可能性のある主な攻撃タイプを特定し、適切なセキュリティポリシーでそれらを防止する方法を学びます。最後に、提案されたセキュリティポリシーを実装する方法も学びます。

この章は **Asterisk 22 LTS** を対象としており、PJSIP（`res_pjsip` / `chan_pjsip`）が唯一の SIP チャネルです。（古い`chan_sip`ドライバは Asterisk 21 で削除されました — 以前のシステムを移行する場合は *Legacy Channels* 章を参照してください。）1 つのセキュリティ上重要な結果として、認証失敗は現在 Asterisk **security event framework** と専用の`security`ロガーチャネルを通じて出力され、Fail2Ban の設定方法が変更されます（この章の後半で説明します）。

## 目的

- Asterisk サーバーに頻繁に行われる主な攻撃タイプを特定する
- 効果的なセキュリティポリシーを定義する
- セキュリティポリシーを実装する
- Asterisk 用に IPTABLES をインストールおよび設定する
- Asterisk 用に Fail2Ban をインストールおよび設定する
- 暗号化のために TLS と SRTP をインストールおよび設定する

## IPテレフォニーへの主な攻撃

IPテレフォニーに対する主な攻撃は、DOS/DDOS、サービス窃盗/料金詐欺、そして盗聴に分類できます。名称が紛らわしいことがあり、同じ攻撃でも情報源によって異なる呼び方がされることがあります。サービス窃盗、料金詐欺、インターネット収益分配詐欺、電話詐欺は、ハッカーが自分のPBXを利用してプレミアムレート番号へトラフィックを流し、プロバイダーからリベートを受け取る行為の異なる呼称です。

### DDoS/DOS

Denial of Service と Distributed Denial of Service は、あらゆる IT インフラストラクチャに対する一般的な攻撃です。SIP やその他の Voice over IP プロトコルでも例外ではありません。Distributed denial of service は通常ボットネットによって実行され、DOS は単一のコンピュータによって行われます。2011 年 2 月、Sality ボットネットは IPv4 アドレス空間全体を対象に、脆弱な SIP サーバーを探すステルスかつ協調的なスキャンを実施しました。UCSD Network Telescope を観測していた研究者は、UDP ポート 5060 をプローブする約 300 万個の異なる送信元 IP が、主にトール詐欺のために SIP アカウントを総当たり攻撃しようとしていると特定しました。[^sality]

[^sality]: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![ピアツーピアのボットネットがサーバーに対して数千件のSIP登録試行を行っている](../images/19-security-fig01.png)

The DOS is applied usually thru techniques such as fuzzing and flooding. Flooding can use SIP, IAX, RTP and other protocols. They can stop the service completely or degrade the voice quality. They are very hard to mitigate if the ports are open to the Internet. Below are some of the tools used by attackers

**ファジング:**

- **PROTOS Test Suite (c07-sip)** — オウル大学 OUSPG から。何千もの不正なパケットを送信し、バッファオーバーフローなどのソフトウェアを停止させる不具合を引き起こします。  
- **Voiper** — すべての SIP 属性を網羅した 200,000 以上のテストを生成し、サーバーがメッセージを効果的に処理できるかを検証します。 <http://voiper.sourceforge.net/>

**フラッディング:**

- **INVITE Flooder** — サーバーにSIP INVITE リクエストを大量に送信します。 <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — サーバーに IAX2 トラフィックを大量に送信します。 <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — アクティブなメディアセッションに RTP パケットを大量に送信し、音声品質を低下させます。 <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### DoS/DDoS に対する緩和技術

私の推奨は

1. Asteriskサーバーをインターネットに公開しないでください、必要な場合は適切な保護（SBC）を行うこと。  
2. 内部ネットワークでは、特に大学やカレッジなど利用者が多い場合、音声用にVirtual LANを使用してください。  
3. 外部アクセスにはVPNまたはTLSを使用してください。

### インターネット収益分配詐欺

この詐欺は少し理解しにくいです。鍵は、International premium rate number (IPRN) の概念を理解することです。

![インターネット収益分配詐欺の3つのステップ：プレミアムレート番号を購入し、脆弱なVoIPデバイスを見つけて番号に発信し、支払いを受け取る](../images/19-security-fig02.png)

IPRN は、特定のインターネット電話会社で無料で割り当てられる番号です。Internet Premium Rate Number Providers を検索すれば、さまざまなプロバイダーが見つかります。この種のオペレーターでは、例として Iridium のような衛星ネットワーク上の番号を割り当てることができ、発信者にとっては 1 分あたり数十セントの料金がかかります。IPRN プロバイダーは、受信した分に対して収益の一定割合（収入の 10〜20%）を支払ってくれます。

![国別の支払率とテスト番号を示すIPRNプロバイダーの価格表](../images/19-security-fig03.png)

割り当てフェーズの後、ハッカーは割り当てられた IPRN をダイヤルできるオープンな Asterisk サーバーを探そうとします。ハッカーが制御する被害者側の PBX は、IPRN 番号に対して何百もの通話を発信し、ハッカーに大きなリターンをもたらすと同時に、被害者には莫大な電話料金が請求されます。週末だけで数十万ドルを超えることも多くあります。

ハッカーがPBXを攻撃する際に使用する主なツール：

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious は使いやすいセキュリティツールセットです。その主な目的は脆弱な PBX を検出し、ブルートフォース攻撃で SIP パスワードをクラックすることです。最も使用されているツールは svcrack です。このツールは 1 秒間に数千のパスワードをテストすることが可能です。  
2. **Phone vulnerabilities**. ハッカーが攻撃ベクターとして頻繁に利用する別のポイントは電話機そのものです。Asterisk をインストールした多くの人は、電話機のウェブインターフェースのデフォルトパスワードを変更していません。これらの電話機がインターネット上に公開されると、ハッカーはデフォルトのインターフェースパスワードを使って設定をダウンロードし、そこから SIP のシークレットパスワードを見つけ出すことがしばしばあります。

#### TFTP盗難:

If you are using auto provisioning of phones using TFTP, you are probably open to this type of attack. TFTP is a simple and insecure form of a File Transfer Protocol.

![攻撃者がTFTPサーバーから推測可能な.cfgファイルをダウンロードし、設定ファイルから平文の認証情報を収集する](../images/19-security-fig04.png)

設定ファイルの名前は、mac アドレスに .cfg を付けたもの（例: 001A2B3C4D5E.cfg）で簡単に推測できます。賢いハッカーは、すべての MAC アドレスを順に試すユーティリティを簡単に作成できるか、あるいはそれを行うツールをダウンロードするだけです。設定ファイルは通常暗号化されておらず、内部にシークレット SIP パスワードが含まれています。

#### ブルートフォース攻撃とtftp窃盗への対策

これらの攻撃を緩和するために、以下の対策を適用できます。  
Brute force: ブルートフォース攻撃を緩和する最善の策は、連続した不正試行を防止することです。ほとんどすべての Asterisk インストーラは fail2ban ユーティリティを使用します。fail2ban は、パスワードやユーザー名が間違っている試行が複数検出されると、攻撃者の IP を一定時間ブロックします。ブルートフォースに対する第2の対策は、12 文字以上で少なくとも 1 つの特殊文字を含む強力なパスワードを使用することです。  
Tftptheft: TFTPTheft を防止するには、プロビジョニングを https 経由で名前とパスワードを使用するように設定します。ファイルは暗号化されて転送され、名前とパスワードにより攻撃者がファイルをダウンロードしようとすることを防げます。

### 盗聴

これらのタイプの攻撃は、ほとんどの場合検出されないため、あまり目にすることはありません。IP 環境において盗聴は非常に検出が困難です。UCsniff のような無料で入手できるユーティリティを使用すれば、ほとんどのネットワークで VoIP 通話を盗聴することが可能です。主な手法は ARP スプーフィングを利用して、トラフィックを UCsniff を実行しているコンピュータに流し込み、通話を記録することです。

#### 盗聴対策

VoIP トラフィックを暗号化することで盗聴を防止できます。もう一つの方法は、ネットワーク上での中間者（MITM）攻撃を防ぐことです。ARP インスペクションは、レイヤー 2 ネットワークにおける MITM を防止するのに非常に効果的です。実装方法を理解するために、ネットワークの技術サポートに確認してください。本書の後半では、TLS と SRTP に基づく暗号化のインストール方法を学びます。また、ARPWatch を使用して、誰かが ARP プロトコルを悪用してネットワークを攻撃していないかを検出することもできます。

## Asterisk のセキュリティポリシー

The best way to implement security is to create a security policy. For this training I will suggest a security policy for most Asterisk installations. Use it as the base starting point and change it according to your needs. The suggested security policy follows below:

1. 不要な UDP/TCP ポートを開放しない
2. インターネット上で管理インターフェース（SSH/HTTPS）へのアクセスを開放しない。
3. SSH および/または HTTP/HTTPS にアクセスするには、IPTABLES ファイアウォールで明示的な例外を設定する必要がある。
4. 12 文字以上で少なくとも 1 つの特殊文字を含む強力なパスワード
5. Fail2ban を使用して認証に 10 回以上失敗した IP アドレスを禁止する
6. 国際電話に対するパスワード確認
7. SIP ポートへのアクセスを既知の IP アドレス範囲に限定する

If you require to have external access to your PBX, there are two possibilities. Use a SBC (Session Border Controller) to protect your server against DOS/DDOS or use a VPN whenever you want external access. If you leave the port 5060 open on the Internet without a SBC or VPN, you are open to a DOS/DDOS attack. The risk is yours。

### PJSIP時代のハードニング (Asterisk 22)

Beyond the firewall and Fail2Ban, Asterisk 22's PJSIP stack provides several configuration-level controls that should be part of your security policy. These complement (not replace) the network controls above:

- **エンドポイントごとの認証。** すべてのエンドポイントは、強力で一意な`password`（`auth_type=digest`）を持つ専用の`type=auth`セクションを参照すべきです。エンドポイント間で認証情報を再利用しないでください。  
- **匿名処理は組み込みです。** PJSIP は認証失敗時にユーザー名が存在するかどうかを明かしません。匿名呼び出しを受け入れるには、`anonymous`という名前のエンドポイントを明示的に作成し、`type=identify`セクション（送信元 IP でマッチ）を使用して既知のピアをエンドポイントにマッピングします。匿名呼び出しを不要とする場合は、`anonymous`エンドポイントを作成せず、マッチしないリクエストはチャレンジ/拒否されます。  
- **ACL。** エンドポイントに対して`/etc/asterisk/acl.conf`で名前付けされた ACL を設定し、エンドポイントから`acl=`（シグナリング/ソース ACL）および`contact_acl=`（コンタクト/登録アドレスを制限）で参照します。エンドポイント自体に permit/deny を直接設定することもできます。  
- **`qualify`。** AOR に`qualify_frequency`（および`qualify_timeout`）を設定し、Asterisk が登録コンタクトの到達可能性を能動的に監視し、死んだコンタクトを除去できるようにします。  
- **PJSIP トランスポートのハードニング / DoS 保護。** `type=transport`はトランスポートごとのクライアント上限を公開しないため、接続フラッド保護はファイアウォール（本章の iptables/Fail2Ban ルール）から提供されます。トランスポートが提供するのは TCP キープアライブ調整（`tcp_keepalive_enable`、`tcp_keepalive_idle_time`、`tcp_keepalive_interval_time`、`tcp_keepalive_probe_count`）で、死んだ/半開状態の接続を除去し、正しい NAT 処理のための`local_net`/`external_*`設定です。これらをファイアウォールルールと組み合わせて接続フラッド攻撃を緩和してください。  
- **TLS + SRTP によるメディア暗号化。** エンドポイントで TLS トランスポートを使用してシグナリングを暗号化し、メディアは`media_encryption=sdes`（WebRTC の場合は`dtls`）で暗号化します—本章の後半で詳しく説明します。  
- **AMI/ARI アクセス制御。** Asterisk Manager Interface（`manager.conf`）と ARI（`ari.conf` / `http.conf`）へのアクセスを localhost または信頼できる管理ネットワークに制限し、強力で一意なシークレットを使用し、HTTP サーバーをプライベートインターフェースにバインドし、インターネットに公開しないでください。

All of the option names above are confirmed against Asterisk 22.10: the `type=transport` section exposes `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net`, and the `external_*` family, but it has **no** `max_clients` option — connection-flood protection comes from the firewall, not from the transport. The `acl` and `contact_acl` endpoint options take section names from `acl.conf`, and source-IP matching for unauthenticated peers is done with `type=identify` sections (`match=`).

### 不要なポートの削除

Instead of discovering all vulnerabilities associated with all Asterisk protocols, let us simplify the problem removing the unnecessary ports. To list all ports open by the Asterisk server use:

```
netstat -pantu |grep asterisk
```

The output of the command is shown below.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

If you look at the output, you will discover that many ports are open. Do we need them? Not necessarily, 2727 is the MGCP protocol (chan_mgcp), 4569 is the IAX (chan_iax2). If you are not using these protocols, you can simply remove the module in the configuration file modules.conf.

You may notice Asterisk binding a high-numbered UDP port. This comes from `res_pjsip`'s resolver making outbound DNS queries (the source port is ephemeral, like any client DNS lookup), not from an inbound listener — your firewall only needs to allow **established/related** return traffic for it (the iptables `conntrack ESTABLISHED,RELATED` rule shown below already covers this). You do **not** need to open a wide inbound high-UDP range just for PJSIP DNS.

To remove the unnecessary ports, disable the modules you don't use. Edit the file modules.conf and add `noload` lines for the channels and protocols you are not using. **Do not** noload `res_pjsip`, `res_pjproject`, or `chan_pjsip` — those are required for SIP in Asterisk 22.

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(In Asterisk 22 you no longer need to noload `chan_mgcp` or `chan_skinny` — those drivers were *removed* in Asterisk 21 and are not part of a stock 22 build.) With the instructions above, I have removed all unnecessary channels keeping only PJSIP. You can choose whatever protocol modules you want, just remove the unused ones. The result is shown in the screenshot below — only the SIP port (5060) bound by your PJSIP transport is now exposed inbound.

![netstat output after disabling the unused modules: only UDP port 5060 remains bound by Asterisk](../images/19-security-fig06.png)

### IPTABLES でセキュリティポリシーを実装する

IPTABLES または netfilter は、ほとんどの Linux ディストリビューションに標準で搭載されているファイアウォールです。このラボでは iptables と fail2ban を設定します。目的は、Asterisk に推奨されるセキュリティポリシーを実装し、不要なトラフィックをすべてブロックすることです。以下の手順に従ってください。

1. すべての外部トラフィックをブロックする
2. 内部ネットワークまたは単一ホストからの SSH トラフィックを許可する
3. UDP と TCP のポート 5060 で SIP トラフィックを許可する
4. UDP メディアポート範囲で RTP トラフィックを許可する。デフォルトの単一設定はなく、Asterisk の独自 `rtp.conf` は何も設定されていない場合 5000–31000 にフォールバックしますが、同梱の `rtp.conf.sample` は `rtpstart=10000` / `rtpend=20000` を設定しているため、ここではその例の範囲を使用します。ファイアウォールルールは、実際に `rtp.conf` で設定した `rtpstart`/`rtpend` に合わせてください。

サーバーへのコンソールアクセスがあることを確認してください。自分自身をシステムから締め出さないように注意が必要です。

1. パッケージ net-persistent をインストールする。```
   sudo apt-get install iptables-persistent
   ```

2. ループバックからのすべてのトラフィックを許可する```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. 確立された接続を許可する```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

ネットワーク 192.168.0.0 からの SSH/HTTPS トラフィックを許可する```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. Asterisk のルールを挿入する```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

   ポート 5061（TLS 上の SIP）は **TCP** であり、UDP ではありません。上記のルールは 5060 を UDP と TCP の両方で、5061 を TCP で開きます。TLS のみを使用する場合は、プレーンな 5060 のルールを完全に削除できます。実際にバインドしている PJSIP トランスポートが使用するポートだけを開放してください。

   `-I` は PREPEND を意味します

6. 最後のルールはドロップでなければなりません```
   sudo iptables -A INPUT -j DROP
   ```

`-A` は APPEND を意味します。注意: 新しいルールを管理する際は、DROP の前にルールを追加する必要があります。新しいルールには PREPEND を使用してください `-I`

7. ルールを保存して iptables を再起動します```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### Fail2Ban を使用して複数の認証失敗をブロックする

Fail2Ban は Asterisk においてほぼ標準的な存在です。ほとんどのユーザーがセキュリティ強化のために導入しています。このユーティリティは Asterisk のログをスキャンし、認証失敗を検出して攻撃者の IP アドレスをブロックします。以下に Fail2Ban のインストール手順を示します。

Asterisk 22 では、PJSIP が認証失敗やその他のセキュリティイベントを Asterisk **security event framework** を通じて報告し、専用の **`security`** ロガーチャネルに書き込みます。Fail2Ban を機能させるには次のことが必要です。

1. `/etc/asterisk/logger.conf`でセキュリティチャネルを有効にします。構文は`<filename> => <levels>`で、セキュリティレベルを`security`という名前のファイルに送るには次のように記述します：

```
[logfiles]
security => security
```

次に CLI から `logger reload` を実行します。これにより、1 行につき 1 つのセキュリティイベントが含まれる `/var/log/asterisk/security` が生成され、形式は次のとおりです:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

The events Fail2Ban cares about are `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID`, and `FailedACL`, each carrying a `RemoteAddress="IPV4/UDP/<ip>/<port>"` field that identifies the offender. (Note the address is wrapped as `IPV4/UDP/.../...`, not a bare IP — your filter must extract the host from inside that string.)

2. Point the `asterisk` jail at that file (`logpath = /var/log/asterisk/security`) and use a filter that parses this security-event format.

Modern Fail2Ban ships an `asterisk` filter whose `failregex` already matches the events above and extracts `<HOST>` from the `RemoteAddress` field, for example:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX ディストリビューション（FreePBX/Sangoma）は同等のフィルタを提供します。正確なイベント文字列はバージョン依存であるため、手動で作成するよりもパッケージ化されたフィルタを使用してください。注意すべき点として、現在パッチが適用されたアドバイザリ（GHSA-5743-x3p5-3rg7）により、細工された PJSIP トラフィックが偽のログ行を注入できることが示されました — Asterisk と Fail2Ban フィルタの両方を最新の状態に保ちましょう。

以下に Fail2Ban をインストールする手順を示します

1. Linux に fail2ban をインストールする```
   sudo apt-get install fail2ban
   ```

2. Asterisk と SSH のために fail2ban を有効化する```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

Add the following lines to activate fail2ban for ssh and asterisk

ssh と asterisk 用に fail2ban を有効にするには、以下の行を追加してください```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. fail2ban の再起動```
   /etc/init.d/fail2ban restart
   ```

4. Verify. Change the secret from your softphone and try to re-register 10 times. Using `iptables -L`, check if the softphone address was included as a blocked address.
5. Remove the address from the ban (suppose the address is 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note: In the command replace 192.168.0.5 by the ip address of your phone

### Implementing TLS and SRTP

I will split this section in two. In the first part we will cover TLS to encrypt signaling and in the second part SRTP to encrypt media. The objective here is to configure Asterisk for these resources.

#### TLS

TLS (Transport Layer Security) is the encryption mechanism defined to protect the SIP signaling. The table below summarizes which attacks TLS protects against:

| Type of attack | Protected? | Notes |
|----------------|-----------|-------|
| Signaling attacks | Yes | TLS assures the integrity of the messages |
| Man in the middle | Yes | TLS checks the server certificate |
| Eavesdropping | No | TLS encrypts signaling, not media |

For media (voice/video) encryption use SRTP.

#### Self-signed digital certificates

There are two types of certificates you can use self-signed and commercial. Self-signed certificates are signed by your own server while commercial certificates are signed by an external authority. For VoIP, you can be your own certificate authority. There is no need for an external certificate such as GoDaddy and Verisign, this is an unnecessary expense. We will generate our own certificates using ast_tls_cert.

#### Configuring TLS with self signed certificates

Below is a step-by-step guide on how to implement TLS. We first generate the certificates, then configure the PJSIP TLS transport (see "Configuring TLS with chan_pjsip"), and finally point the softphone at it. We will use the SipPulse Softphone, which supports TLS and SRTP natively. (Any TLS/SRTP-capable SIP softphone works the same way.)

**Step 1.** Create a private RSA key using 3DES encryption with length of 4096 bits for our certification authority. The command below present in /usr/src/asterisk-22.x.y/contrib/scripts will create the Certification Authority and The Asterisk Certificate. As usual adapt the instructions if required, versions change, directories change. Please, pay attention on what you are doing. Use your domain or IP address in the –C option. The command ast_tls_cert has three options.

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
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
Generating RSA private key, 2048 bit long modulus
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

I’m not going to generate a client certificate because we are not going to use the certificate to authenticate the client. The client is not required to present its own certificate.

**Step 2.** Configure Asterisk to support our client over TLS. This is done in `pjsip.conf` (a TLS transport plus the endpoint settings) — the full configuration is shown in the next section, "Configuring TLS with chan_pjsip." We are not authenticating using certificates, just encrypting the traffic.

**Step 3.** Install a TLS-capable SIP softphone (the author uses the SipPulse Softphone).

**Step 4.** Copy the certificate authority to the computer running the softphone. After installing it, copy the file `/etc/asterisk/keys/ca.crt` to the computer running the softphone (use scp, or WinSCP on Windows) if you are using a self-signed certificate.

**Step 5.** Create the account in the softphone. In the account screen add the account normally like any other sip account. Use the right password, the authentication is still based on the password.

**Step 6.** Set TLS as the transport in the account settings. In the SipPulse Softphone account screen (below), choose **TLS** as the transport and use port 5061. Adjust your firewall to open TCP port 5061.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** Trust the certificate authority. If your Asterisk TLS certificate is signed by a public CA (for example Let's Encrypt — see the *Deployment* chapter), a modern softphone such as the SipPulse Softphone trusts it automatically through the system certificate store, with no manual import. If you use a self-signed certificate, import its CA (`/etc/asterisk/keys/ca.crt`) into the client or the operating-system trust store, or accept it when prompted.

**Step 8.** You do **not** need a client certificate. A common misconception is that each phone needs its own certificate to authenticate — it does not. At this point Asterisk only *encrypts* the session; authentication is still username and password. Asterisk does not verify client certificates by default, so there is no need to distribute a per-client certificate.

**Step 9.** After changing the certificate or transport, fully restart the softphone (quit and relaunch, not just close the window) so it reconnects over the new transport.

### Configuring TLS with chan_pjsip

Now let’s learn how to configure PJSIP for TLS. PJSIP is the only SIP channel in Asterisk 22, so there is nothing to switch — just make sure `res_pjsip`, `res_pjproject` and `chan_pjsip` are loaded. Step 1: Confirm PJSIP is enabled in /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

ステップ2: PJSIP を TLS 対応に設定します。ファイル /etc/asterisk/pjsip.conf に TLS トランスポート用のセクションを追加します。

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Use `method=tlsv1_2` (or `tlsv1_3` if your OpenSSL/PJSIP build supports it) — TLS 1.0/1.1 are obsolete and insecure and should not be used.

ステップ 3: Configure the endpoint for blink. Edit `pjsip.conf` and edit the section for blink. Let PJSIP choose the transport automatically.

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

Step 4: Verifying. TLS を使用して登録が行われたことを確認するには、Asterisk コンソールで次のコマンドを使用します。

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### Making secure calls using SRTP

メディア暗号化を担当するプロトコルは、RFC3711で定義された Secure Real Time Protocol (SRTP) です。このプロトコルの短所の一つは、鍵交換の標準化された方法がないことです。Asterisk は、TLS によって保護されたシグナリング暗号化を利用し、SDP プロトコル上で SDES による鍵交換を行います。他にも MIKEY や ZRTP といった方法があります。Philipp Zimmermann が開発した ZRTP は、鍵交換とメディア暗号化のための最も高度な手法の一つです。一部のソフトフォンやハードフォンは ZRTP に対応しています。しかし、標準的な方法は依然として SDES であり、市場に出回っているほぼすべての電話でこの方式が採用されています。以下は、SDP の a=crypto:1 および a=crypto:2 行で暗号鍵が定義されたリクエストの例です。

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

#### AsteriskでのSRTP設定

AsteriskでSRTPを設定するのは非常に簡単です。エンドポイントで`media_encryption=sdes`を設定します；`media_encryption_optimistic=no`を使用して暗号化されていないメディアを静かに許可するのではなく、拒否するように要求することもできます。SDESはシグナリングをTLS上で実行する必要があるため、キーが平文で送信されないことに注意してください。

**Step 1.** Asterisk設定

`pjsip.conf`の`type=endpoint`セクションに以下を設定します：

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

**Step 2.** ソフトフォンの設定

In the softphone, enable SRTP for the account media (set the **SRTP (Media Encryption)** option to *Mandatory*) so that voice is encrypted.

![SipPulse ソフトフォンのアカウント設定（下部） — **Transport** を TLS に、**SRTP (Media Encryption)** を *Mandatory* に設定し、シグナリングとメディアの両方を暗号化します](../images/softphone/sipphone-config.png){width=35%}

## 国際電話のための二要素認証の有効化

国際ルートを持たないことが最善の場合もあります。しかし、どうしても国際電話をかける必要がある場合は、追加のパスワードを使用します。国際電話をかける前にボイスメールのパスワードを要求するために、Asterisk アプリケーション **vmauthenticate** を使用します。これは `extensions.conf` のダイヤルプランで設定します。以下の例をご参照ください。これにより、ハッカーがピアパスワードを取得したり電話を侵害したとしても、この宛先に電話をかけるにはボイスメールのパスワードが必要になります。

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate`は Asterisk 22 でも引き続き標準アプリケーションです。上記の`Dial()`は SIP/PJSIP トランク（`PJSIP/<number>@<trunk>`）経由で通話をルーティングします。これはほとんどの最新インストールが PSTN に接続する方法です — `my_trunk`を自分のトランク名に合わせて変更し、実際に DAHDI スパンがある場合のみ`DAHDI/g1/...`を使用してください。ダイヤルプランにおけるトラブル防止策 — このような第二要素を、アウトバウンドおよび国際ルートに到達できるコンテキストを制限することと組み合わせることは、展開できる最も重要な保護策の一つです。

## 要約

この章では、IP PBX をインターネットに接続することのリスクについて学びました。その後、セキュリティポリシーを実装して PBX を保護する方法を学びました。このセキュリティポリシーでは、iptables、fail2ban、TLS、SRTP、そして国際通話向けの双方向認証を実装しました。この章を楽しんでいただけたことを願っています。

## Quiz

1. インターネット収益分配詐欺に対する最も重要な対策は何ですか？
   - A. SRTP を実装する
   - B. Asterisk を最新の状態に保つ
   - C. TLS を実装する
   - D. 強力なパスワードを使用する
2. SIP ファジングは次のように定義されます：
   - A. 不正なリクエストやレスポンスを用いた DoS 攻撃
   - B. パスワードを総当たりで試すサービス窃盗
   - C. 現在の通話を盗聴すること
   - D. SIP リクエストの洪水による DDoS
3. TFTPTheft はサーバーが TFTP 経由で設定ファイルを提供する際に発生します。これを回避する方法は次のうちどれですか？
   - A. FTP
   - B. HTTP
   - C. ユーザー名とパスワード付き HTTPS
   - D. SCP
4. 中間者攻撃で使用される手法は次のどれですか？
   - A. TFTP theft
   - B. ARP スプーフィング
   - C. MAC ポイズニング
   - D. dsniff
5. SRTP では、Asterisk はキー交換に次のシステムを使用します：
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. `/usr/src/asterisk-22.x.y/contrib/scripts`にある、認証局と証明書を生成するユーティリティはどれですか？
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. 盗聴防止の有効な戦略（該当するものすべてにチェック）：
   - A. アナログ盗聴検知器を実装する
   - B. ARPwatch ユーティリティで ARP スプーフィングを検出する
   - C. スイッチで ARP スプーフィング検出を有効にする
   - D. SRTP を使用する
8. Asterisk はクライアント証明書を検証することで強力な認証をサポートしています。（PJSIP TLS トランスポートはクライアントの証明書を要求・検証できます。）
   - A. 正しい
   - B. 誤り
9. Asterisk 22 で、SDES キーを使用したイン SDP による SRTP メディア暗号化を有効にする PJSIP エンドポイント設定はどれですか？
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. Asterisk 22 では、Fail2Ban が専用の ________ ロガーチャネル（`logger.conf`で有効化）から PJSIP の認証失敗イベントを読み取る必要があります。
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
