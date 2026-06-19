```{=latex}
\frontmatter
```

## Copyright {.unnumbered}

*Asterisk Guide* — Second Edition (Asterisk 22 LTS)

Copyright © 2006–2026 Flavio E. Gonçalves. All rights reserved.

本書のいかなる部分も、出版された書評における短い引用を除き、著者の事前の書面による同意なしに、いかなる形式または手段によっても、複製、検索システムへの保存、または送信を行うことはできません。

**版:** Second Edition.
**ISBN:** *to be assigned.*

> **[2nd-ed note]** 第2版用に**新しいISBN**を割り当ててください。初版のISBN (9781796396973) は再利用しないでください。ここに出版日も設定してください。

製造業者や販売者が自社製品を区別するために使用する名称の多くは、商標として主張されています。本書にそれらの名称が登場し、著者が商標権の主張を認識していた場合、それらは大文字または頭文字を大文字で表記しています。Asterisk、Digium、IAX、およびDUNDiは、Sangoma Technologiesの商標です（Digiumは2018年にSangomaによって買収されました。Asteriskは現在Sangomaによってスポンサーされています）。

本書の作成には細心の注意を払っていますが、著者は誤りや脱落、または本書に含まれる情報の使用から生じる損害について、一切の責任を負いません。

## Preface {.unnumbered}

本書は、Asterisk 22 LTSをベースにしたPBX（構内交換機）のインストールと設定方法を学びたいすべての人のためのものです。Asteriskは、VoIPと従来のTDMチャネルを橋渡しするオープンソースのテレフォニー・プラットフォームです。

これは、『*Asterisk Configuration Guide*』として始まった書籍の第5世代にあたります。本書の内容は、2006年に私がDigium dCAP認定試験の準備のために行った作業から発展したものです（私は一発で合格しました）。それ以来、1,000人以上の学生に教えてきました。

オープンソースPBXのコンセプトは革命的です。数十年にわたり、テレフォニーの世界は高価な独自システムを販売する一握りの企業によって支配されてきました。Asteriskはその力をユーザーの手に取り戻しました。かつては経済的に手の届かなかった機能（CTI、IVR、ACD、voicemailなど）が、Linuxマシンと学ぶ意欲さえあれば誰でも利用できるようになったのです。

本書だけであなたをグル（指導者）にすることはできません。それはどの本にも不可能なことです。しかし、本書を読み終える頃には、高度な機能を備えた本物のPBXを構築し、運用できるようになっているはずです。本書には、実践的なラボとオンラインコースというコンパニオン教材が**VoIP School Blackbelt** (<https://voip.school>) に用意されています。

## Audience {.unnumbered}

本書は、Asteriskの初心者である読者を対象としています。Linux（シェル、テキストエディタ、基本的なシステム管理）に慣れていることを前提としています。学習中であれば、Linuxデスクトップ環境で進めても構いませんし、ラボ用には仮想マシンでも問題ありません（音声品質はわずかに低下する可能性があります）。本番環境では、デスクトップ環境やリソースの少ないVM上でAsteriskを動かすことは推奨しません。IPネットワーク、VoIP、および基本的なテレフォニーの概念に関する知識があれば、理解が深まるでしょう。

## What's new in the second edition {.unnumbered}

第2版は、**Asterisk 22 LTS**（2024年リリース、2028年10月までサポート）に合わせて全面的に刷新されました。主な変更点は以下の通りです。

- **PJSIPが唯一のSIPチャネルとなりました。** `chan_sip`はAsterisk 21で削除され、22には存在しません。すべてのSIPの例は現在PJSIP（`pjsip.conf`）を使用しています。レガシーな`sip.conf`の資料は、移行の参考としてのみ残されています。
- **Sangomaによる管理。** Digiumは2018年にSangomaによって買収されました。プロジェクトは現在Sangomaによって開発・スポンサーされており、本書全体にその方針が反映されています。
- **3つの新章。** *WebRTC with Asterisk*（WSS/DTLS-SRTP経由のブラウザフォン）、*SIP trunking, DID & the PSTN*、および*Deployment, monitoring & scaling*。
- **再現可能なラボ。** 本書内のすべての設定とコマンドは、読者自身が実行可能なAsterisk 22 Dockerラボで検証済みです。
- **機能の現代化。** 古いMeetMe会議に代わってConfBridgeが採用され、AMI/AGIと並んでARIが導入されました。PJSIP Realtime (Sorcery) がカバーされ、インストール、セキュリティ、CDRの各章が最新の内容に更新されました。
- **新しい構成。** 本書は、「Foundations（基礎）」、「Channels & Connectivity（チャネルと接続）」、「Dialplan & Call Features（dialplanと通話機能）」、「Integration & Operations（統合と運用）」の4部構成になりました。

## About the author {.unnumbered}

Flavio E. Gonçalvesは1966年ブラジル生まれ。1983年に初めてPCを手にして以来、コンピュータに強い関心を持ち、1989年にコンピュータ支援設計・製造を専攻して工学の学位を取得しました。彼はブラジルのSipPulseのCEOであり、同社はsoftswitch、SBC、マルチテナントPBXを専門としています。

これまでのキャリアにおいて、Novell MCNE/MCNI、Microsoft MCSE/MCT、Cisco CCSP/CCNP/CCDP、Asterisk dCAPなど、数多くの認定資格を取得してきました。彼がオープンソースソフトウェアについて執筆を始めたのは、かつて認定資格の学習で教えられた構造化された手法が学習に非常に有効であると信じているからです。彼は25年以上の教育経験を活かし、単なる技術的な視点からではなく、人々が実際にどのように学ぶかに焦点を当てて執筆しています。

Flavioは2人の子供の父親であり、世界で最も美しい場所の一つであるブラジルのフロリアノーポリスに住んでいます。余暇にはサーフィンやセーリングを楽しんでいます。

## Feedback, credits & training {.unnumbered}

誤りを見つけ出し、排除するよう努めていますが、どうしても見落としが発生してしまいます。もし誤りを見つけた場合は、お知らせいただければ対応いたします。

本書はトレーニング教材としても使用されています。ご自身のトレーニングセンターで使用したい場合や、コンパニオンのオンラインコースやラボを受講したい場合は、**VoIP School Blackbelt** (<https://voip.school>) にアクセスするか、<flavio@voip.school> までメールでお問い合わせください。

**クレジット。** カバーデザイン：Karla Braga。査読者：Luis F. Gonçalves、Guilherme Goes (dCAP)、および専門の校正者。長年にわたりフィードバックをくださり、本書の内容を形作ってくれた多くの学生たち、そしてサポートしてくれた家族に感謝します。

```{=latex}
\cleardoublepage
```
