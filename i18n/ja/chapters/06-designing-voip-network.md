# Designing a VoIP network

Voice over IPは電話市場で急速に成長しています。コンバージェンスのパラダイムは、コミュニケーションの方法を変え、コストを削減し、情報取引の方法を向上させています。音声は、音声、ビデオ、プレゼンスを含むフルマルチメディア通信時代の始まりにすぎません。将来的には、人を職場へ輸送するのではなく、仕事を人々のもとへ届けることになるでしょう。なぜならそれがよりクリーンで、速く、安価になるからです。VoIPはこの革命の一部に過ぎません。本章での課題はVoIPネットワークを設計することです。そのためには、セッションプロトコルやコーデックといった概念、そして回線数や帯域幅の見積もり方法を理解しなければなりません。

## Objectives

この章の終わりまでに、次のことができるようになります：

- VoIP の利点を理解する
- Asterisk が VoIP をどのように処理するかを説明する
- SIP と IAX チャネルの概念を説明する
- 特定のデータチャネルに最適なプロトコルを選択する
- 特定のデータチャネルに最適なコーデックを選択する
- 必要なチャネル数を見積もる
- 必要な帯域幅を計算する

## VoIP benefits

Why would you care about VoIP? VoIP provides benefits to both companies and individuals. Cost reduction is certainly one of them, but in some environments VoIP simplifies the integration of computer systems. Several of the benefits are detailed here:

### Convergence

The primary benefit of VoIP is the combination of data and voice networks to reduce costs (convergence). However, analyzing just voice minute costs may not be enough to justify the adoption of VoIP. The price of the minutes sold by phone companies is quickly becoming cheaper and is something to be considered before adopting VoIP.

### Infrastructure costs

The use of a single network infrastructure reduces the costs associated with additions, removals, and changes. As IP has become pervasive, it has brought VoIP-related technology to several new devices, such as cell phones, PDAs, embedded systems, and laptops.

### Open Standards

Finally, the open standards upon which VoIP is built provide the freedom to choose from different vendors. This single benefit makes the customer king instead of a subordinate to TELCOS and PBX manufacturers.

### Computer Telephony Integration

Telephony is far older than computing. Telephony PBXs are circuit-switch based, and you usually do not have more than a computer for supervision. With VoIP, telephony is from the ground up created based in computer standards. This makes the use of Computer Telephony applications cheaper and easier than in the old model. You can quickly create a long list of telephony applications based on Asterisk. You can develop IVRs, ACDs, CTI, dialers, screen popups, and other applications in a fraction of the time required for traditional PBXs.

## Asterisk VoIP アーキテクチャ

Asterisk のアーキテクチャは以下のとおりです。Asterisk はすべての VoIP プロトコルをチャンネルとして扱います。任意のコーデックやプロトコルを使用できます。ここで学ぶ概念は、Asterisk が任意のタイプのチャンネルを他のチャンネルにブリッジすることです。したがって、SIP や IAX などのシグナリングプロトコルを相互に変換したり、異なるコーデック間で変換したりできます。たとえば、ローカルエリアネットワーク内の SIP 電話から G.711 コーデックを使用して発信し、G.729 コーデックを使用する VoIP プロバイダーへの SIP トランクに変換することができます。次の章では、SIP と IAX のアーキテクチャの詳細を説明します。chan_ooh323 アドオンによる H.323 サポートも利用可能ですが、ますます稀になっています。SIP/PJSIP が現代の展開の標準です。

![Asterisk のモジュラーアーキテクチャ：アプリケーションとチャンネルが API を介して PBX スイッチコアに接続し、コーデック変換とファイル形式モジュールが動的にロードされます](../images/06-voip-network-fig01.png)

## VoIPプロトコルとネットワークスタック

VoIPはさまざまなプロトコルが連携して動作します。これらを七層OSI参照モデルに当てはめようとする誘惑がありますが、古い図の多くは実際にそうしています――SIP と H.323 を「セッション」層に、コーデックを「プレゼンテーション」層に配置します。この対応付けは常に議論の的でした。SIP を標準化する IETF は OSI モデルを使用せず、古い四層 TCP/IP（DoD）モデルに従い、RFC 3261 では **SIP をアプリケーション層プロトコル** と定義しています。メディアも同様のパターンで、RTP とコーデックはアプリケーションペイロードに位置し、トランスポート層の UDP 上で運ばれます。以下の表は、IETF が実際に使用している TCP/IP モデルに主要な VoIP プロトコルをマッピングし、参考用に大まかな OSI の対応を示しています。

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

DiffServ などの QoS メカニズムは IP 層で動作し、音声パケットの優先順位付けと通話品質の向上を実現します。いくつかのプロトコル固有のポイント:

- **SIP** はポート 5060 の UDP または TCP（TLS は 5061）でシグナリングを運びます。音声は別途 RTP により、設定可能な UDP ポート範囲（Asterisk の shipped `rtp.conf` sample は 10000 から 20000）で運ばれ、G.711 などのコーデックでエンコードされます。
- **H.323** は TCP（ポート 1720 の H.225 コールシグナリング）で通話シグナリングを運び、H.225 RAS チャネルはポート 1719 の UDP を使用します。音声は RTP が輸送します。
- **IAX2** は珍しく、シグナリングとメディアの両方を単一の UDP ポート（4569）で多重化し、NAT やファイアウォールの通過を簡素化します。


## プロトコルの選び方

多くのプロトコルがある中で、ネットワークに最適なものはどれか？このセクションでは、各プロトコルの利点と欠点をハイライトします。

### SIP - セッション開始プロトコル

SIP はインターネットエンジニアリングタスクフォース (IETF) のオープンスタンダードであり、主に RFC 3261 で定義されています。ほとんどの最新の VoIP プロバイダーは SIP を使用しており、実際に最も普及している VoIP 標準となりつつあります。SIP の強みは IETF ベースの標準であることです。SIP は古い H.323 と比較して軽量です。SIP の主な弱点は NAT トラバーサルであり、ほとんどの SIP VoIP プロバイダーにとって課題となります。IETF は請求処理を念頭に置いて SIP を作成したわけではなく、ピア間のオープンな通信を目的としています。請求は通常、VoIP プロバイダーの関心事です。

### IAX – Inter Asterisk eXchange（インタ Asterisk 交換）

IAX は、もともと Digium（現在は Sangoma）によって開発されたオープンプロトコルです。IAX はシグナリングとメディアを同じ UDP ポート (4569) で転送するオールインワンプロトコルです。Mark Spencer は帯域幅削減のためにバイナリプロトコルとして IAX を開発しました。IAX の主な強みは帯域幅使用量が少ないこと（RTP を使用しません）であり、UDP ポートが 1 つだけなので NAT やファイアウォールの通過も非常に容易です。

If a traditional PBX manufacturer were to have created IAX, it would probably have marketed the protocol as the 「アイスクリーム以来の最高のもの」; in some situations, IAX in trunk mode can reduce voice bandwidth use by one third. IAX2 (version 2) still ships in Asterisk 22 via the `chan_iax2` module and remains useful for Asterisk-to-Asterisk trunks, though it is considered legacy; SIP/PJSIP is preferred for new deployments. IAX2 is specified in [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational).

### MGCP – メディアゲートウェイ制御プロトコル

MGCP は H.323、SIP、IAX と組み合わせて使用されるプロトコルです。その最大の利点はスケーラビリティです。ゲートウェイではなくコールエージェントで設定されるため、設定プロセスが簡素化され、集中管理が可能になります。ただし、Asterisk の実装は完全ではなく、利用者はあまり多くないようです。

### H.323

H.323は主にVoIPで使用されています。これは最初期のVoIPプロトコルの一つで、ゲートウェイをベースとした古いVoIPインフラストラクチャを接続するために不可欠です。H.323は依然としてゲートウェイ市場の標準ですが、市場は徐々にSIPへ移行しています。H.323の強みは広範な市場採用と成熟度にあります。H.323の弱みは実装の複雑さと標準化団体に伴うコストに関連しています。

### プロトコル比較表

以下の表はセッションプロトコル間の違いをまとめたものです。

| プロトコル | 標準団体 | Asterisk 22 モジュール / 状態 | 用途 |
|----------|---------------|-----------------------------|----------|
| SIP | IETF 標準 | `chan_pjsip` (core; the only SIP driver — `chan_sip` は Asterisk 21 で削除されました) | SIP 電話; SIP サービスプロバイダへの接続 |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; 依然として提供され、レガシーと見なされます) | Asterisk 間トランク; IAX2 電話; IAX サービスプロバイダ |
| H.323 | ITU 標準 | `chan_ooh323` (external community add-on, not in the base build) | H.323 電話とゲートウェイ（外部ゲートキーパーを使用可能、ゲートキーパーになることはできません） |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | （レガシー MGCP 電話） |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | （レガシー Cisco 電話） |

## One endpoint per device

Asterisk 22 の PJSIP スタックは、すべての電話、トランク、またはゲートウェイを`pjsip.conf`内の単一の **endpoint** オブジェクトとしてモデル化します。1 つの endpoint は発信と受信の両方を行い、その認証情報は`auth`オブジェクトに、登録されたアドレスは`aor`に、ネットワークパスは`transport`に格納されます。デバイスごとに 1 つの endpoint を設定し、必要な要素を結び付けます — 「ユーザー」と「ピア」という別々の役割を考える必要はありません。（完全なオブジェクトモデルは *SIP & PJSIP in depth* に掲載されています。）

## コーデックとコーデック変換

音声をアナログ波形からデジタル信号に変換するためにコーデックを使用します。コーデックは音質、圧縮率、帯域幅、計算要件などの点で互いに異なります。サービス、電話機、ゲートウェイは通常、これらのうちいくつかをサポートしています。コーデック G.729 は非常に人気があります。これは標準の Asterisk 22 ビルドの一部ではなく、代わりに外部アドオンモジュール（`codec_g729`）として Digium（現 Sangoma）からダウンロードします。Asterisk の `menuselect` ソースはそれを `support_level=external` と共にリストし、はっきりと記しています。「Digium から g729a コーデックをダウンロードしてください。このコーデックにはライセンスの購入が必要です。」つまり、合法的な G.729 の使用にはチャンネルごとのライセンス購入が必要です。（オープンソースの代替品 `bcg729` も存在します。）

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 は次のコーデック（他にも多数）をサポートしています。

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — 標準 PSTN 品質；ulaw は北米で、alaw は欧州およびラテンアメリカで一般的
- ITU G.722: 64 Kbps — ワイドバンド（HD 音声）、G.711 と同じ帯域幅で高品質
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — Digium/Sangoma からダウンロードする外部 `codec_g729` バイナリモジュール（`support_level=external`；使用にはライセンス購入が必要）
- Speex: 2.15 から 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps、可変 — 現代のワイドバンド/フルバンドコーデック；優れた音質とパケットロス耐性；Digium/Sangoma からダウンロードする外部 `codec_opus` バイナリモジュールとして提供（`support_level=external`；G.729 とは異なりライセンス購入は不要）；WebRTC および最新の SIP エンドポイントに推奨されます。（GitHub にオープンソースビルドの代替品があります。）

さらに、Asterisk はコーデック間の変換を許可しています。ただし、g723 のようにパススルーモードでのみサポートされるケースなど、変換が不可能な場合もあります。あるコーデックから別のコーデックへの変換は CPU リソースを多く消費します。したがって、可能な限りこの処理は避けるようにしてください。

## How to choose a Codec

Codec selection depends on several options, such as:

- Sound quality
- Licensing costs
- CPU-processing consumption
- Bandwidth requirements
- Packet-loss concealment
- Availability for Asterisk and phone devices

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## プロトコルヘッダーによるオーバーヘッド

コーデックは帯域幅をほとんど使用しないにもかかわらず、Ethernet、IP、UDP、RTP などのプロトコルヘッダーによるオーバーヘッドを考慮しなければなりません。そのため、実際に消費される帯域幅は使用されるヘッダーに依存します。Ethernet ネットワークでは PPP ネットワークよりも要件が高くなります。これは PPP ヘッダーが Ethernet ヘッダーより短いためです。たとえば、単一の G.729 音声パケットはペイロードがわずか 20 バイトですが、Ethernet、IP、UDP、RTP ヘッダーで約 58 バイトにラップされます。つまり、ヘッダーが帯域幅を支配しており、コーデックは支配していません（下図参照）。

![単一の g.729 音声パケット（Ethernet 上）：20 バイトのペイロードが 58 バイトの Ethernet、IP、UDP、RTP ヘッダーでラップされ、g.729 通話は 31.2 Kbps を消費します。](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

オンラインの VoIP 帯域幅計算ツール（例：<https://www.voip.school/bandcalc/bandcalc.php>）を使用すれば、他の帯域幅要件も簡単に計算できます。


## Traffic Engineering

VoIP ネットワークの設計における主な課題は、リモートオフィスやサービスプロバイダーなど特定の宛先へ向けた回線数と必要帯域幅を見積もることです。また、Asterisk の同時通話数（Asterisk のサイズ決定の主要パラメータ）を見積もることも重要です。

### Simplifications

最も一般的に使用される単純化手法は、ユーザータイプ別に通話数を推定することです。例：

- Business PBXs（5 拡張子につき 1 通の同時通話）
- Residential users（16 ユーザーにつき 1 通の同時通話）

Example #1 本社には 120 拡張子があり、2 つの支店があります――1 つ目は 30 拡張子、2 つ目は 15 拡張子です。目的は、本社の E1 トランク数と Frame‑Relay ネットワークに必要な帯域幅を算出することです。

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Number of T1 lines

- Total number of extensions using T1 lines: 120+30+15=165 lines
- Using one trunk for each five extensions for business use
- Total number of lines = 33 or approximately 2xT1 lines

1b Bandwidth requirements g.729 コーデックを選択したのは、帯域幅要件、音質、そして中程度の CPU 消費量が理由です。

5 拡張子につき 1 本のトランクを使用した場合:

- Required bandwidth for branch #1 (Frame-relay): 26.8*6=160.8 Kbps
- Required bandwidth for branch #2 (Frame-relay): 26.8*3= 80.4 Kbps

### Erlang B method

履歴データがある場合、単純化せずにより科学的にトランクをサイズ決定できます。ここでは、1909 年にコペンハーゲン電話会社の Agner Karup Erlang が開発した、2 つの都市間のトランクグループの回線数を算出する式を使用します。

**Erlang** は通信業界で共通のトラフィック測定単位で、1 時間あたりのトラフィック量を表します。例えば、1 時間に 20 件の通話があり、各通話の平均会話時間が 5 分の場合:

- Traffic minutes in the hour: 20 × 5 = 100 minutes
- Hours of traffic within one hour: 100 / 60 = **1.66 Erlangs**

これらの測定値はコールロガーから取得でき、ネットワーク設計や必要回線数の算出に利用できます。回線数が分かれば、帯域幅要件も計算できます。

**Erlang B** はトランクグループの回線数を算出する最も一般的な手法です。通話がランダムに到着する（ポアソン分布）ことと、ブロックされた通話が即座にクリアされることを前提とします。**Busy Hour Traffic (BHT)** を把握している必要があり、これはコールロガーから取得するか、簡易的に「1 日の通話分の 17%」として推定できます。

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

もう一つ重要な変数は Grade of Service (GoS) で、回線不足によるブロック確率を定義します。このパラメータは通常 0.05（5% の通話ロス）または 0.01

## VoIP に必要な帯域幅の削減

VoIP 通話に必要な帯域幅を削減する方法は次の 3 つです。

- RTP ヘッダー圧縮
- IAX トランク化
- VoIP ペイロードの増加

### RTP ヘッダー圧縮

フレームリレーや PPP ネットワークでは、RTP ヘッダー圧縮を使用できます。RTP ヘッダー圧縮は RFC 2508 で定義されており、複数のルータで利用可能な IETF 標準です。ただし、一部のルータではこの機能を利用できるように別の機能セットが必要になることがありますので注意してください。RTP ヘッダー圧縮を使用した場合の効果はすばらしく、例では音声会話 1 回あたり 26.8 Kbps の帯域幅が 11.2 Kbps にまで削減され、58.2% の削減となります。

### IAX2 トランクモード

2 台の Asterisk サーバを接続する場合、IAX2 プロトコルをトランクモードで使用できます。この革新的な技術は特別なルータを必要とせず、あらゆる種類のデータリンクに適用できます。

![IAX2 trunk mode on Ethernet: a single g.729 call needs its full header stack (31.2 Kbps), but a second call shares those headers and adds only a small IAX2 miniframe, averaging about 9.6 Kbps of extra bandwidth per additional call.](../images/06-voip-network-fig08.png)

IAX2 トランクモードは 2 回目以降の通話で同じヘッダーを再利用します。PPP リンクで g729 を使用した場合、最初の通話は 30 Kbps の帯域幅を消費しますが、2 回目の通話は最初と同じヘッダーを使用し、追加の通話に必要な帯域幅は 9.6 Kbps にまで削減されます。トランクモードで必要な帯域幅は次のように計算できます。  
Branch #1 (11 calls) Bandwidth = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps  
Branch #2 (8 calls) Bandwidth = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps  
最初の通話は 31.2 Kbps、次は 9.6 Kbps と続きます。

### 音声ペイロードの増加

この方法はインターネット経由で VoIP ゲートウェイを使用する際に非常に一般的です。ペイロードを大きくすると、帯域幅は削減されますが、レイテンシが増加します。`allow` 命令でコーデックにフレームサイズを付加することで、RTP のパケット化を変更できます。

![Increasing the voice payload: packing 60 bytes of g.729 payload into one packet (instead of 20) amortizes the 58 bytes of headers across more voice, dropping bandwidth to about 16.05 Kbps per call at the cost of added latency.](../images/06-voip-network-fig09.png)

例:

```
allow=ulaw:30
```

コロンの後の数値はミリ秒単位のパケット化間隔で、各 RTP パケットにどれだけの音声が含まれるかを示します。値が大きいほど固定ヘッダーのオーバーヘッドがより多くの音声に分散され（帯域幅は減少）、レイテンシが増加します。各コーデックには最小・最大・デフォルトのフレームサイズがあり、たとえば G.711 (`ulaw`/`alaw`) はデフォルトで 20 ms です。

## Summary

この章では、Asterisk がチャンネルを使用して VoIP を扱うことを学びました。SIP（Asterisk 22 の `chan_pjsip` を介して）と IAX2 をサポートし、H.323 はコミュニティの `ooh323` アドオンを通じてのみ利用可能で、古い MGCP と SCCP（Skinny）チャンネルは標準の Asterisk 22 ビルドには含まれなくなっています。シグナリングプロトコルと VoIP チャンネル用のコーデックの選択方法を比較・学習しました。IAX2 は帯域幅効率が高く、NAT を簡単に通過できます。SIP/PJSIP はサードパーティの電話機やゲートウェイベンダーに最も広くサポートされているプロトコルで、Asterisk 22 で唯一の SIP チャンネルドライバです。H.323 プロトコルは最も古く、レガシーな VoIP インフラストラクチャに接続する際に使用すべきです。Traffic Engineering のセクションでは、VoIP ネットワークの設計と容量算出方法を学びました。

## Quiz

1. Which of the following are benefits of VoIP described in this chapter (check all that apply)?
   - A. Convergence of data and voice networks to reduce cost
   - B. Lower infrastructure cost for additions, removals, and changes
   - C. Open standards that free you from a single vendor
   - D. Easier and cheaper Computer Telephony Integration
   - E. Guaranteed lower per-minute calling rates than any phone company
2. Convergence is the integration of voice, data, and video in a single network; its primary benefit is cost reduction in the implementation and maintenance of separate networks.
   - A. False
   - B. True
3. Asterisk treats every VoIP protocol as a channel and can bridge any channel type to any other, transcoding between codecs when needed.
   - A. False
   - B. True
4. In Asterisk 22, SIP is handled by which channel driver?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In the TCP/IP (IETF) model that SIP is actually defined against in RFC 3261, the signaling protocols SIP, H.323, and IAX2 operate at the ___ layer.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP is the most adopted protocol for IP phones and is an open standard largely defined by the IETF in RFC 3261.
   - A. False
   - B. True
7. IAX2 transports both signaling and media over a single UDP port, which makes it efficient and easy to traverse NAT. Which UDP port does IAX2 use?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX was originally developed by Digium (now Sangoma). Despite limited adoption by phone vendors, IAX is excellent when you need (check all that apply):
   - A. To reduce bandwidth usage (it does not use RTP)
   - B. A video media format
   - C. Easy NAT and firewall traversal
   - D. Trunk mode to combine many Asterisk-to-Asterisk calls and amortize header overhead
9. In Asterisk 22, a device is configured as a single PJSIP `endpoint` object that both places and receives calls — there is no separate "user" or "peer" role.
   - A. False
   - B. True
10. Regarding codecs in Asterisk 22, check all the true statements:
    - A. G.711 is equivalent to PCM and uses 64 Kbps of bandwidth.
    - B. Sangoma's codec_g729 module is free to download, but lawful use requires a purchased per-channel license.
    - C. GSM is popular because it uses about 13 Kbps and needs no license.
    - D. G.711 u-law is common in North America, while a-law is common in Europe and Latin America.
    - E. G.729 is light and uses very few CPU resources to encode and decode compared with G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
