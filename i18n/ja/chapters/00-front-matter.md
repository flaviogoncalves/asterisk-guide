```{=latex}
\frontmatter
```

## Copyright {.unnumbered}

*Asterisk Guide* — Second Edition (Asterisk 22 LTS)

Copyright © 2006–2026 Flavio E. Gonçalves. All rights reserved.

本書のいかなる部分も、出版されたレビューでの短い引用を除き、著者の事前の書面による同意なしに、いかなる形式または手段によっても、複製、検索システムへの保存、または送信を行うことはできません。

**版:** Second Edition.

> **[author TODO]** 新しい第2版のISBNを割り当て（初版の 9781796396973 は再利用しないこと）、印刷前に発行日を設定してください。

メーカーや販売者が自社製品を区別するために使用する名称の多くは、商標として主張されています。本書にそれらの名称が登場し、かつ著者が商標権の主張を認識していた場合、それらは大文字または頭文字を大文字にして記載されています。Asterisk、Digium、IAX、および DUNDi は Sangoma Technologies の商標です（Digium は2018年に Sangoma に買収されました。現在 Asterisk は Sangoma がスポンサーとなっています）。

本書の作成には細心の注意を払っておりますが、著者は誤りや脱落、または本書に含まれる情報の使用から生じる損害について、一切の責任を負いません。

## Preface {.unnumbered}

本書は、Asterisk 22 LTS をベースとした PBX（構内交換機）のインストールと設定方法を学びたいすべての人のためのものです。Asterisk は、VoIP と従来の TDM チャネルを橋渡しするオープンソースのテレフォニー・プラットフォームです。

本書は、『*Asterisk Configuration Guide*』として始まった書籍の第5世代にあたります。本書の内容は、2006年に私が Digium dCAP 認定試験の準備のために行った作業（一発で合格しました）から発展したもので、それ以来1,000人以上の学生に教えられてきました。

オープンソース PBX という概念は革命的です。数十年にわたり、テレフォニーの世界は高価な独自システムを販売する一握りの企業によって支配されてきました。Asterisk はその力をユーザーの手に取り戻しました。かつては経済的に手が届かなかった機能（CTI、IVR、ACD、voicemail など）が、今では Linux マシンと学ぶ意欲さえあれば誰でも利用できるようになりました。

本書だけであなたを専門家にすることはできません（そのような本は存在しません）。しかし、読み終える頃には、高度な機能を備えた本物の PBX を構築・運用できるようになっているはずです。本書には、実践的なラボとオンラインコースを備えたコンパニオンサイト **VoIP School Blackbelt** (<https://voip.school>) があります。

## Audience {.unnumbered}

本書は、Asterisk 初心者の読者を対象としています。Linux（シェル、テキストエディタ、基本的なシステム管理）の操作に慣れていることを前提としています。学習中は Linux デスクトップ環境で進めても構いませんし、ラボには仮想マシンを使用しても問題ありません（音声品質はわずかに低下する可能性があります）。本番環境では、デスクトップ環境やリソースの少ない VM 上での Asterisk の実行は推奨しません。IP ネットワーク、VoIP、および基本的なテレフォニーの概念に関する知識があると役立ちます。

## What's new in the second edition {.unnumbered}

第2版は、**Asterisk 22 LTS**（2024年リリース、2028年10月までサポート）に合わせて全面的に刷新されました。主な変更点は以下の通りです。

- **PJSIP が唯一の SIP チャネルとなりました。** `chan_sip`は Asterisk 21 で削除され、22には存在しません。すべての SIP の例は現在 PJSIP（`pjsip.conf`）を使用しています。レガシーな`sip.conf`の資料は、移行の参考としてのみ残されています。
- **Sangoma による管理。** Digium は2018年に Sangoma に買収されました。プロジェクトは現在 Sangoma によって開発・支援されており、本書全体でその状況を反映しています。
- **3つの新章。** *WebRTC with Asterisk*（WSS/DTLS-SRTP 経由のブラウザフォン）、*SIP trunking, DID & the PSTN*、および *Deployment, monitoring & scaling*。
- **再現可能なラボ。** 本書内のすべての設定とコマンドは、読者が自分で実行できる Asterisk 22 Docker ラボで検証済みです。
- **機能の現代化。** 旧来の MeetMe 会議に代わって ConfBridge が採用され、AMI/AGI に加えて ARI が導入されました。PJSIP Realtime (Sorcery) がカバーされ、インストール、セキュリティ、CDR の各章が最新の内容に更新されました。
- **新しい構成。** 本書は、「Foundations（基礎）」、「Channels & Connectivity（チャネルと接続）」、「Dialplan & Call Features（dialplan と通話機能）」、「Integration & Operations（統合と運用）」の4部構成になりました。

## About the author {.unnumbered}

Flavio E. Gonçalves は1966年ブラジル生まれ。1983年に初めて PC を手にして以来コンピュータに強い関心を持ち、1989年にコンピュータ支援設計・製造を専攻して工学の学位を取得しました。彼はブラジルの SipPulse の CEO であり、同社は softswitch、SBC、マルチテナント PBX を専門としています。

これまでのキャリアにおいて、Novell MCNE/MCNI、Microsoft MCSE/MCT、Cisco CCSP/CCNP/CCDP、Asterisk dCAP など、数多くの認定資格を保持してきました。彼がオープンソースソフトウェアについて執筆を始めたのは、かつて認定資格の学習で教えられた構造化された手法が学習に最適であると信じているからであり、25年以上の教育経験を活かして、単なる技術的な観点からではなく、人々が実際にどのように学ぶかに焦点を当てて執筆しています。

Flavio は2人の子供の父親であり、世界で最も美しい場所の一つであるブラジルのフロリアノーポリスに住んでおり、余暇にはサーフィンやセーリングを楽しんでいます。

## Feedback, credits & training {.unnumbered}

誤りを見つけて排除するよう努めていますが、どうしても見落としが発生してしまいます。もし誤りを見つけた場合は、お知らせいただければ対応いたします。

本書はトレーニング資料としても使用されています。ご自身のトレーニングセンターで使用したい場合、あるいはコンパニオンのオンラインコースやラボを受講したい場合は、**VoIP School Blackbelt** (<https://voip.school>) にアクセスするか、<flavio@voip.school> までメールでお問い合わせください。

**クレジット。** カバーデザイン: Karla Braga。査読者: Luis F. Gonçalves、Guilherme Goes (dCAP)、および専門の校正者。長年にわたりフィードバックをくださり、本書の内容を形作ってくれた多くの学生たち、そしてサポートしてくれた家族に感謝します。

```{=latex}
\cleardoublepage
```
