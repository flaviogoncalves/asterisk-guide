# Introduction to Asterisk PBX

The popularity of ready-to-run distributions such as FreePBX and Issabel has recently grown. In this book, we will cover the classic Asterisk, which is the foundation for understanding these distributions. Asterisk PBX is open-source software capable of transforming an ordinary PC into a powerful multiprotocol PBX. In this chapter, we will learn about the possibilities of this new technology and its basic architecture.

## 目的

この章の終わりまでに、次のことができるようになります：

- Asterisk が何であり、何をするかを説明できること；
- Digium™ とその後継である Sangoma の役割を説明できること；
- Asterisk の基本アーキテクチャとそのコンポーネントを認識できること；
- いくつかの使用シナリオを指摘できること；そして
- 情報源とヘルプを特定できること。

## What is Asterisk

Asterisk はオープンソースの PBX ソフトウェアで、一般的なコンピュータを家庭ユーザー、企業、VoIP サービスプロバイダー、電話会社向けのフル機能 PBX に変換します。Asterisk はオープンソースコミュニティであると同時に、Sangoma Technologies（2018 年に Digium を買収）によって支援されているプロジェクトでもあります。Asterisk は自由に使用・改変でき、ニーズに合わせてカスタマイズ可能です。Asterisk は PSTN と VoIP ネットワーク間のリアルタイム接続を実現します。Asterisk は単なる PBX 以上の機能を持つため、既存の PBX の優れたアップグレードになるだけでなく、電話分野で新たなことも実現できます。例えば：

- 在宅勤務の従業員をブロードバンドインターネット経由でオフィス PBX に接続する;
- 異なる場所にある複数のオフィスを IP ネットワーク、プライベートネットワーク、あるいはインターネット自体を通じて接続する;
- 従業員にウェブとメールと統合されたボイスメールを提供する;
- 注文システムやその他のアプリケーションへ接続できる IVR のようなアプリケーションを構築する;
- 出張中のユーザーがシンプルなブロードバンドまたは VPN 接続でどこからでも会社の PBX にアクセスできるようにする; そして
- さらに多くのこと...

Asterisk には、従来は高価なシステムにしかなかった高度な機能がいくつか含まれています。例えば：

- コールキューで待機中の顧客向けの音楽再生、メディアストリーミングや MP3 ファイルに対応;
- エージェントチームが電話に応答し、キューを監視できるコールキュー機能;
- テキスト・トゥ・スピーチおよび音声認識との統合;
- テキストファイルと SQL データベースの両方に転送される詳細なレコード;
- デジタル回線とアナログ回線の両方を通じた PSTN 接続。

## What is AsteriskNOW (Historical) and FreePBX

Asterisk の最も純粋な形、いわゆる “classic asterisk”（Debian パッケージ名）は、単体では完成品というより開発ツールに近いと考えられています。AsteriskNOW は Asterisk をソフトアプライアンス化する取り組みでした。このディストリビューションはオペレーティングシステムに CentOS、グラフィカルインターフェースに FreePBX を含んでいました。AsteriskNOW はその後廃止されました。

現在、標準的なターンキー Asterisk ディストリビューションは **FreePBX**（Sangoma がメンテナンス）で、Asterisk をウェブベースの管理 GUI とモジュールエコシステムと共に提供します。FreePBX は GPL の下でライセンスされており、www.freepbx.org から自由にダウンロードできます。商用展開向けに、Sangoma は **FreePBX Distro**（完全な Linux イメージ）と商用製品 **PBXact** も提供しています。

## Role of Digium™ and Sangoma

Digium, a company located in Huntsville, Alabama, was the creator and primary developer of Asterisk since its founding in 1999. In addition to being the primary sponsor of Asterisk development, Digium produced telephony interface cards and other hardware for Asterisk PBXs, and created commercial products such as Switchvox (targeted at the SMB market). In 2018, Digium was acquired by **Sangoma Technologies**, a Canadian unified communications company. Since the acquisition, Sangoma has continued to sponsor Asterisk development and serves as its primary steward, maintaining the open-source project at www.asterisk.org.

Historically, Digium offered Asterisk under three types of license agreements:

- General Public License (GPL) Asterisk. This is the most used version. It includes all features and is free to be used and modified according to the terms of the GPL license.
- Asterisk Business Edition was a commercial version of Asterisk. Some companies used the business edition because they did not want or could not use the GPL license—usually because they did not want to release their source code together with Asterisk. **Note:** Asterisk Business Edition has been discontinued; today Asterisk is distributed solely under the GPL.
- Asterisk OEM licensing. After Digium stopped selling Asterisk Business Edition at retail, it continued to license that commercial edition to OEM customers — equipment vendors who wanted to build proprietary products on top of Asterisk without releasing their own source code under the GPL.

### The Zapata project and its relationship with Asterisk

The Zapata project was developed by Jim Dixon, who was also responsible for the revolutionary hardware design used with Asterisk. The hardware is open-source too; as such, it can be used by any company, and today several manufacturers produce cards compatible with this architecture.

The Zapata project produced an architecture called Zaptel, later renamed DAHDI (Digium/Asterisk Hardware Device Interface). One of the main benefits of this architecture is the ability to use the PC CPU to process media streaming, echo cancellation, and transcoding. In contrast, most existing cards use digital signal processors (DSP) to perform these tasks. The use of the PC CPU instead of dedicated DSPs reduces the board's price dramatically. Thus, these cards are significantly cheaper than previously available interfaces from other manufacturers. On the other hand, these cards require a lot of CPU; a misuse of the PC CPU can significantly impact voice quality. Recently, Digium launched a coprocessor card that uses DSPs to encode and decode G.729 and G.723, allowing better scalability for a large number of channels.

## Why Asterisk?

私は Asterisk と初めて出会ったことを覚えています。新しいもの、特に自分がすでに知っているものと競合するものに対する最初の反応は、拒絶することです！ 2003 年に起きたことはまさにそれでした。Asterisk は、私が顧客に販売していたソリューション（4 E1 VoIP Gateway）と競合しており、私が既に知っていたソリューションの価格の 10 分の 1 という非常に安価なものでした。この不均衡な価格により、私は Asterisk を調査し、潜在的な落とし穴や欠点を特定しようとしました。たとえば、当時の PC CPU では 120 本の g.729 同時セッションをサポートできないことが分かり、結局は自分の Gateway ソリューションで提案を勝ち取りました。

しかし、この作業を通じて、Asterisk が顧客基盤の非常に高価な問題を解決できることに気づきました。IVR、統合メッセージング、通話録音、ダイヤラーの見積もりが高額になる問題に直面していましたが、適切なディメンションを行えば CPU の問題は回避できました。実際、わずか 3 年で Asterisk は私の会社の主力製品となり（Asterisk ビジネス専用に別会社を設立しました）、私の考えでは Asterisk はテレコミュニケーションにおける革命であり、IP テレフォニーに対して Apache がウェブサービスに対して持つ位置付けに相当します。

### Extreme cost reduction

従来の PBX と Asterisk をデジタルインターフェースや電話機の観点で比較すると、Asterisk はそれらの PBX よりやや安価です。しかし、ボイスメール、ACD、IVR、CTI といった高度な機能を追加した場合、Asterisk のコストパフォーマンスは大きく上回ります。実際、低価格帯のアナログ PBX と Asterisk PBX を比較するのは不公平です。なぜなら、Asterisk は低価格帯アナログシステムにはない多くの機能を提供しているからです。

### Telephony system control and independence

顧客が最も頻繁に挙げる Asterisk の利点の一つは、提供される独立性です。今日の一部メーカーは、顧客にシステムのパスワードや設定ドキュメントすら提供しません。Asterisk の「DIY」アプローチにより、ユーザーは完全な自由を手に入れ、さらに標準インターフェースへのアクセスも得られます。

### Easy and rapid development environment

Asterisk は AMI や AGI インターフェースを介して PHP や Perl といったスクリプト言語で拡張できます。Asterisk はオープンソースであり、ユーザーがソースコードを変更可能です。ソースコードは主に ANSI C で記述されています。

### Feature rich

Asterisk には、従来の PBX では見られない、あるいはオプション扱いの機能が多数あります（例：ボイスメール、CTI、ACD、IVR、組み込みミュージックオンホールド、録音）。これらの機能のコストは、プラットフォーム自体の価格を上回ることさえあります。

### Dynamic content on the phone

Asterisk は C 言語や、現在の開発環境で一般的な他の言語でプログラミングされます。動的コンテンツを提供する可能性は事実上無限です。

### Flexible and powerful dial plan

Asterisk のもう一つの画期的な点は、強力なダイヤルプランです。従来の PBX では、最安経路選択（LCR）といったシンプルな機能すら実装が難しいかオプション扱いでした。Asterisk なら、最適なル

## Main objections to Asterisk PBX

Asterisk の導入に対する反論はよく耳にしますが、ここでそれらに対処します。

### Asterisk’s market share is too small

市場シェアは通常、販売された PBX の台数で測定されます。これらの統計は主に大手ディストリビュータから取得されます。Asterisk はダウンロードして導入できるフリーソフトウェアであり、販売記録が残らないため、これらの数字では体系的に過小評価されています。それでも、Asterisk は世界中で非常に大規模な導入実績を持ち、単一サーバのオフィス PBX から大規模キャリアやコンタクトセンターまで幅広く利用されており、オープンソース PBX エコシステム（FreePBX などのターンキー配布を含む）を支える支配的なエンジンです。

### If it is free, how does the manufacturer survive?

実際のところ、従来の意味でのオープンソースソフトウェアメーカーというものは存在しません。Digium は 1999 年から Asterisk を開発し、電話インターフェースカードの販売、Switchvox などの商用 PBX 製品、関連ソフトウェアの販売で自らを維持してきました。2018 年に Sangoma Technologies が Digium を買収し、Sangoma は Asterisk の開発資金を提供し続け、商用製品（FreePBX の商用モジュール、PBXact、Switchvox）やハードウェア販売、プロフェッショナルサービスを通じて収益を上げています。

### It is hard to find technical support!

Sangoma はパートナーエコシステムおよび自社製品を通じて、Asterisk に対する商用テクニカルサポートを提供しています。認定プロフェッショナルのグローバルネットワークが一次サポートとプロフェッショナルサービスを提供します。コミュニティサポートは Asterisk フォーラムや www.asterisk.org のメーリングリストを通じて活発に続いています。

### Does Asterisk support more than 200 extensions?

はい、全く問題ありません。適切にサイズ設定された単一の Asterisk サーバは多数のエクステンションを処理でき、さらにロードバランシングやフェイルオーバーでユーザーを複数サーバに分散させることで、巨大なマルチサイト展開にも対応可能です。

### Only “geeks” are able to install Asterisk

FreePBX（Sangoma が提供するスタンドアロンディストリビューション）を使用すれば、Linux の知識が限られたプロでも中規模の PBX をインストール・設定できます。GUI の助けを借りれば、数時間で PBX 全体を構成することが可能です。

### What if the server fails?

Asterisk の主な利点の一つは、フォールトトレラントシステムで動作できることです。二台のサーバを並列で稼働させるのは比較的簡単で低コストです。従来型の PBX でこれを試す勇気はありますか？

### Our company does not use open-source software

貴社は実はオープンソースソフトウェアを使用している可能性があります。多くのアプライアンスは OS に Linux を採用しています。さらに、Sangoma とその認定パートナーネットワークから商用サポートやマネージドデプロイメントを受けることができます。

### Using the PC's CPU to process signaling and media is not recommended

Asterisk は専用 DSP を使用せず、サーバの CPU でシグナリングと音声チャンネルのメディア処理を行います。これにより最大で 5 倍のコスト削減が可能になる一方、システムはメイン CPU の性能に依存します。適切にサイズ設定すれば、Asterisk は大容量の処理にも対応できます。もしメイン CPU からこれらの負荷

## Asterisk Architecture

このセクションでは、Asterisk のアーキテクチャがどのように機能するかを説明します。以下の図は基本的な Asterisk アーキテクチャを示しています。次に、チャンネル、コーデック、アプリケーションなど、アーキテクチャに関連する概念を説明します。

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

チャンネルは電話回線に相当しますが、デジタル形式です。通常、アナログまたはデジタル（TDM）シグナリングシステム、あるいはコーデックとシグナリングプロトコルの組み合わせ（例: SIP‑GSM、IAX‑uLaw）で構成されます。当初、すべての電話接続はアナログで、エコーやノイズの影響を受けやすいものでした。その後、ほとんどのシステムがデジタルに変換され、アナログ音声は多くの場合パルス符号変調（PCM）を使用してデジタル形式に変換されました。この形式により、圧縮なしで 64 キロビット/秒で音声を伝送できます。

Public Switched Telephone Network（PSTN）とインターフェースするチャンネル:

- `chan_dahdi`: Sangoma（旧 Digium）、Xorcom などのアナログ（FXO/FXS）およびデジタル（E1/T1/PRI）TDM カード。DAHDI に対して個別にビルドされています — *Legacy channels* 章を参照。

Voice over IP とインターフェースするチャンネル:

- `chan_pjsip`: SIP — Asterisk 22 LTS の主要かつ唯一の SIP チャンネルドライバ。ダイヤル文字列: `PJSIP/endpoint_name`。(**Note:** 旧 `chan_sip` は Asterisk 21 で削除され、Asterisk 22 には存在しません。設定については *Building your first PBX with PJSIP* を参照。)
- `chan_iax2`: IAX2 プロトコル — 依然として Asterisk 22 に同梱されていますがレガシーです。新規導入では SIP/PJSIP が推奨されます。ダイヤル文字列: `IAX2/peer`。
- `chan_unistim`: Nortel/Avaya UNISTIM 電話。まだ利用可能（拡張サポート）ですが、使用頻度は低いです。

古い VoIP チャンネルは標準の Asterisk 22 ビルドには含まれていません: `chan_h323`（H.323）はコミュニティの `ooh323` アドオンとしてのみ残っており、`chan_mgcp`（MGCP）および `chan_skinny`（Cisco SCCP）は非推奨となり、最新のチャンネルセットから除外されました。これらのプロトコルと相互運用する必要がある場合は、Asterisk の前にゲートウェイを配置するのが一般的なアプローチです。

その他のチャンネル:

- **Local**: コアに組み込まれた疑似チャンネルで、別のコンテキストのダイヤルプランにループバックします — 再帰的ルーティングや、呼び出しを複数の宛先に分配する際に便利です。ダイヤル文字列: `Local/extension@context`。

### Codec and codec translation

できるだけ多くの音声接続をデータネットワーク上に置くことを目指しています。コーデックはデジタル音声に新機能をもたらし、圧縮率 8:1 を超える圧縮を可能にします。多くのコーデックは音声活動検出（無音抑制）、パケットロス隠蔽、コンフォートノイズ生成といった機能も定義していますが、Asterisk 自体はコンフォートノイズを生成したり無音抑制を行ったりしません。Asterisk には複数のコーデックが用意されており、相

```
CLI>core show translation
```

以下のコーデックがサポートされています:

- G.711 ulaw (USA) - (64 Kbps)。
- G.711 alaw (Europe) - (64 Kbps)。
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - パススルーモードのみ
- G.726 - (16/24/32/40kbps)
- G.729 - Sangoma が配布するバイナリコーデックモジュール；ダウンロードは無料ですが、合法的に使用するにはチャネルごとのライセンス購入が必要です (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocols

電話間でデータを送信するのは、データが自動的に相手側の電話へ経路を見つけられれば簡単です。しかし実際にはそうはならず、電話間の接続を確立し、エンドデバイスを検出し、電話シグナリングを実装するためにシグナリングプロトコルが必要です。SIP は現代の導入で支配的なシグナリングプロトコルであり、Asterisk 22 LTS で利用可能な唯一の SIP チャネルです (via chan_pjsip)。IAX2 もまだ利用可能ですがレガシーと見なされています。Asterisk は以下のプロトコルをサポートしています。

- SIP — via `chan_pjsip`
- IAX2 — レガシー、Asterisk 22 に同梱
- UNISTIM — Nortel/Avaya 電話 (拡張サポート)
- H.323、MGCP、SCCP (Cisco Skinny) — 標準の Asterisk 22 ビルドには含まれないレガシープロトコル (H.323 は community `ooh323` アドオン経由のみ)

### Applications

電話間のブリッジを行うには、アプリケーション `dial()` が使用されます。ほとんどの Asterisk 機能 (例: voicemail や conference) はアプリケーションとして実装されています。利用可能な Asterisk アプリケーションは、`core show applications` コンソールコマンドで確認できます。

```
CLI>core show applications
```

Asteriskのアドオン、サードパーティプロバイダー、あるいは自分で開発したものからアプリケーションを追加できます。

## Asteriskシステムの概要

AsteriskはオープンソースのPBXで、TDMとIPテレフォニーなどの技術を統合したハイブリッドPBXとして機能します。Asteriskはインタラクティブ・ボイス・レスポンス（IVR）やオートマティック・コール・ディストリビューション（ACD）といった機能を実装でき、さらに前述のとおり新しいアプリケーションの開発にもオープンです。この図は、Asteriskがアナログおよびデジタルインターフェースを使用してPSTNや既存のPBXに接続し、アナログ電話とIP電話の両方をサポートする様子を示しています。Asteriskはソフトスイッチ、メディアゲートウェイ、ボイスメール、オーディオ会議として機能し、さらに組み込みのミュージック・オン・ホールドも備えています。

![Asteriskシステムの概要](../images/01-introduction-fig02.png)

## Comparing the old and the new world

古いソフトスイッチモデルでは、すべてのコンポーネントが個別に販売されており、各コンポーネントを別々に購入し、PBX またはソフトスイッチ環境に統合する必要がありました。コストとリスクは高く、ほとんどの機器は専有でした。

![The old world: components bought and integrated separately](../images/01-introduction-fig03.png)

### Telephony using Asterisk

すべての機能が Asterisk プラットフォームに統合されており、規模に応じて同一ボックスまたは別々のボックスで提供され、すべて GPL ライセンスです。主流の IP-PBX のいくつかをライセンスするよりも、Asterisk をインストールする方が簡単なことがあります。

![Telephony using Asterisk: the functions are integrated](../images/01-introduction-fig04.png)

## テストシステムの構築

Asterisk ソリューションを実装する際、最初のステップは通常テストシステムを構築することです。目標は最小限の **1×1 PBX** — 1 本の電話が別の電話にかけられる状態 — を作り、エンドポイント、ダイヤルプラン、機能を本番環境に触れる前に試すことです。現在はすべてソフトウェアで完結します。電話ハードウェアは不要です。

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### 現代的な方法：ソフトウェアラボ（推奨）

最速のテストシステムは、コンテナまたは仮想マシン上で動作する Asterisk 22 に、エンドポイント用の **softphones** を組み合わせ、必要に応じて **SIP trunk** を使って公衆ネットワークに接続する構成です。

- **Asterisk 22** を小型 Linux マシン、VM、または Docker コンテナで実行します。本書では、単一コマンドで完全に設定された Asterisk 22 を起動する Docker ラボ（ラボガイド参照）を提供しています — コンパイル不要、ハードウェア不要です。
- **2 つの softphone** を PJSIP エンドポイントとして登録し、実際に相互通話できるようにします。本書全体で **SipPulse Softphone**（無料ダウンロード: <https://www.sippulse.com/produtos/softphone>）を使用しています。デスクトップ版とモバイル版が利用可能です。
- **SIP trunk**（オプション）を VoIP プロバイダーから取得し、PSTN へ接続できるようにします。カードやアナログ回線は不要で、認証情報だけで済みます。

本書のすべての例はこの構成で作成・検証されており、任意のノートパソコンでも再現可能です。

### 従来の方法：アナログ/デジタルカード

VoIP が普及する前は、テスト PBX に物理インターフェースが必要でした。既存の電話回線に接続する **FXO** ポートと、アナログ電話を接続する **FXS** ポートを組み合わせて 1×1 PBX を構成します。1 枚のカードに FXO と FXS がそれぞれ 1 つずつ搭載されたのが従来の入門キットです。これらの DAHDI ベースのカード（Sangoma 製、旧 Digium 製）は、アナログ回線や T1/E1 回線を終端する必要がある現場ではまだ利用されていますが、今日ではニッチな存在です — 大半の導入は純粋な VoIP です。アナログ電話や回線だけを接続したい場合は *Legacy Channels* 章を参照してください。そうでなければ、電話ハードウェアは完全に省略できます。

## Asterisk scenarios

Asterisk can be used in several different scenarios. We will list some of them and explain the advantages and possible limitations of each.

### IP PBX

The most common scenario is the installation of a new or the replacement of an existing PBX. If you compare Asterisk with some other alternatives, you will find it to be cheaper and richer in features than most PBXs currently available on the market. Several companies are now changing their specifications to Asterisk instead of other brand-name PBXs.

![Asterisk as an IP PBX](../images/01-introduction-fig06.png)

### IP-enabling legacy PBXs

The following image illustrates one of the most commonly used setups. Large companies generally do not want to take significant risk when investing in new technologies and simultaneously wish to preserve their investments in legacy equipment. IP-enabling legacy PBX can be very expensive; thus, connecting an Asterisk PBX using T1/E1 lines can be a good alternative for cost-conscious customers. Another benefit is the possibility of connecting to a VoIP service provider with better telephony rates.

![IP-enabling a legacy PBX](../images/01-introduction-fig07.png)

### Toll Bypass

A very useful application for VoIP is connecting branch offices over the Internet or a WAN. Using an existing data connection allows you to bypass toll charges incurred in telecommunication connections between headquarters and branch offices.

![Toll bypass between offices over a WAN](../images/01-introduction-fig08.png)

### Application Server (IVR, Conference, Voicemail)

Asterisk can be used as an application server for the existing PBX or be directly connected to PSTN. Asterisk offers services such as voicemail, fax reception, call recording, IVR connected to a database, and an audio conferencing server. If you integrate voicemail and fax into an existing e-mail server, you will have a unified messaging system, which is usually an expensive solution. Using Asterisk as an application server provides extreme cost reduction compared to other solutions.

![Asterisk as an application server](../images/01-introduction-fig09.png)

### Media Gateway

Most voice-over IP service providers use an SIP proxy to host all registration, location, and authentication of SIP users. They still have to send calls to the PSTN directly or route it through a wholesale call termination provider using an SIP or H.323 voice-over IP connection. Asterisk can act as a back-to-back user agent (B2BUA) or media gateway, replacing very expensive soft switches or media gateways. Compare the price of a four E1/T1 gateway from the main market manufacturers with Asterisk. The Asterisk solution can cost several times less than other solutions and is capable of translating signaling protocols (H.323, SIP, IAX…) and codecs (G.711, G.729…).

![Asterisk as a media gateway](../images/01-introduction-fig10.png)

### Contact Center Platform

A contact center is a very complex solution that combines several technologies, such as automatic call distribution (ACD), interactive voice response (IVR), and call supervision. Basically, three types of contact centers are available: inbound, outbound, and blended.

Inbound contact centers are very sophisticated and usually require ACD, IVR, CTI, recording, supervision, and reports. Asterisk has a built-in ACD to queue the calls. IVR can be done using Asterisk Gateway Interface (AGI) or internal mechanisms such as the application background(). Computer telephony integration (CTI) is achieved using Asterisk Manager Interface (AMI); recording and reporting are built in to Asterisk.

For an outbound contact center, a predictive or power dialer is one of the main components. Although several dialers are available for the open-source Asterisk, it is not hard to build your own for the platform if you so desire. A blended contact center allows simultaneous inbound and outbound operation, saving money by ensuring better use of the agent's time. It is possible to use Asterisk and its ACD mechanism to implement a blended solution.

![An Asterisk contact-center platform](../images/01-introduction-fig11.png)

## 情報とヘルプの探し方

このセクションでは、Asterisk に関する主な情報源をいくつか紹介します。

- Asterisk の公式ウェブサイト: <https://www.asterisk.org> ここでは次の情報が見つかります:
- Documentation & Wiki -> <https://docs.asterisk.org>
- Community forum -> <https://community.asterisk.org>
- Bug tracking -> <https://github.com/asterisk/asterisk/issues>
- Wiki (legacy, largely superseded by docs.asterisk.org) -> <https://wiki.asterisk.org>

### Community forum

Asterisk コミュニティフォーラムは、旧来のメーリングリストに取って代わり、質問をする場所となっています。投稿する前にできるだけ多くの情報を集めてください。宿題をしていなければ誰も助けてくれません — 少なくとも一度は自分で問題を解決しようと試みてください。

- <https://community.asterisk.org>

## Summary

Asterisk は GPL に基づいてライセンスされたソフトウェアで、一般的な PC を強力な IP PBX プラットフォームとして機能させることができます。Digium の Mark Spencer が 1990 年代後半に Asterisk を作成し、Digium は Asterisk 関連ハードウェアや商用製品の販売で事業を維持してきました。Digium は 2018 年に Sangoma Technologies に買収され、現在は Sangoma が Asterisk の開発を支援しています。ハードウェアインタフェースの設計は Jim Dixon が開発した Zapata プロジェクトに端を発し、これが DAHDI の基礎となりました。

Asterisk アーキテクチャは主に以下のコンポーネントで構成されています。

- CHANNELS: アナログ、デジタル、または voice‑over IP。Asterisk 22 LTS では、SIP は`chan_pjsip`のみで処理されます。
- PROTOCOLS: 通話のシグナリングを担当する通信プロトコルで、SIP（PJSIP 経由）、H.323、MGCP、IAX2 などがあります。
- CODECS: 音声のデジタルフォーマットを変換し、圧縮やパケットロス隠蔽を可能にします。Asterisk 自体は無音抑制（音声活動検出）やコンフォートノイズ生成を行わないことに注意してください。エンドポイントが VAD を使用する場合、コンフォートノイズはクライアント側で無効にすべきです。
- APPLICATIONS: Asterisk PBX の機能を提供します。Conference、voicemail、fax などが Asterisk アプリケーションの例です。

Asterisk は小規模な IP PBX から高度なコンタクトセンターまで、さまざまなシナリオで利用できます。ヘルプは www.asterisk.org および docs.asterisk.org で簡単に見つけることができます。

## Quiz

1. 2018年に Digium を買収し、現在 Asterisk オープンソースプロジェクトの主要な管理者となっている企業はどこですか？
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. Asterisk 22 LTS で SIP 接続性を提供するチャネルドライバはどれですか？
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. 真偽問題：`chan_sip`チャネルドライバは Asterisk 21 で削除され、標準の Asterisk 22 ビルドには存在しません。

4. 標準の Asterisk 22 ビルドに **もはや含まれない** チャネル/プロトコルはどれですか？（該当するものすべて選択）
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, community `ooh323` アドオンとしてのみ存続)

5. 元々 Zaptel と呼ばれていた Zapata プロジェクトのハードウェアアーキテクチャは、後に ____ に改名されました。
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Asterisk があるコーデックから別のコーデックへ音声を変換しなければならないとき、内部的にどのストリームフォーマットを経由して変換しますか？
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. 本章によると、Sangoma が配布する G.729 コーデックモジュールのライセンス状況はどうなっていますか？
   - A. GPL で、あらゆる用途に完全に無料です。
   - B. ダウンロードは無料ですが、合法的に使用するにはチャンネルごとのライセンス購入が必要です。
   - C. Asterisk Business Edition を購入しない限り入手できません。
   - D. パススルーモードでのみ動作し、インストールできません。

8. ある電話から別の電話へ通話をブリッジするために使用される Asterisk アプリケーションはどれですか？
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Asterisk の `Local` チャネルとは何ですか？
   - A. アナログ電話用のハードウェア FXS インターフェース。
   - B. ローカルサービスプロバイダーへの SIP トランク。
   - C. 異なるコンテキストのダイヤルプランに通話をループバックさせる疑似チャネル。
   - D. オンネット通話に使用されるコーデック。

10. Asterisk がバック・ツー・バック ユーザーエージェント (B2BUA) として動作し、シグナリングプロトコルとコーデック間の変換を行って高価な SoftSwitch の代替となる使用シナリオはどれですか？
    - A. レガシー PBX の IP 化
    - B. トールバイパス
    - C. メディアゲートウェイ
    - D. コンタクトセンタープラットフォーム

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
