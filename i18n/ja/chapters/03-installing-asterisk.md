# Asterisk 22のインストール

第1章では、テレフォニー環境においてAsteriskがどのように役立つかを学びました。本章では、Asteriskのダウンロードとインストール方法について解説します。作業を始める前に、コンパイルとインストールの方法を理解しておくことが不可欠です。コンパイルというプロセスは、従来のMicrosoft™ Windows™ユーザーには奇妙に思えるかもしれませんが、Linux™環境ではごく一般的なことです。Asteriskをコンパイルすることで、使用するハードウェアに最適化されたコードを得ることができます。本章ではその手順に従います。Asteriskは複数のオペレーティングシステムで動作しますが、ここでは簡略化のため、Linuxのみを対象とします。依存関係のインストールが容易で、安定性が高く、フットプリントが小さいことから、Linux™ディストリビューションとしてDebianを選択しました。別のディストリビューションを使用したい場合は、それに応じて依存関係のパッケージ名を変更してください。

本書は **Asterisk 22 LTS**（2024年10月16日リリース。2028年10月16日までフルサポート、2029年10月16日までセキュリティ修正を提供）を対象としています。Asterisk 22は現在の長期サポート（LTS）リリースです。Digiumは2018年に **Sangoma** によって買収され、現在AsteriskはSangomaのスポンサーシップを受けていることに注意してください。本書全体を通して言及される「Digium」は、レガシーハードウェアの旧ブランド名を指します。

## 学習目標

本章を終えるまでに、以下のことができるようになります。

- Asteriskのハードウェア要件を判断する
- 必要な依存関係を備えたLinuxをインストールする
- HTTPS経由で安定版をダウンロードする
- Asteriskをコンパイルする
- ブート時にAsteriskを起動する方法を学ぶ

## 最小ハードウェア要件

Asteriskの動作に高性能なハードウェアは必要ありませんが、要件に合わせて最適なハードウェアを選択するためのヒントがいくつかあります。ハードウェアを選択する際は、以下の主要な要素を考慮する必要があります。

- 登録ユーザーの総数。サポートが必要な1秒あたりの登録数を定義します。
- 同時通話の総数。Asteriskサーバー上のネットワークアダプターおよびブリッジで処理する必要があるネットワーク会話数を定義します。
- サポートが必要なコーデック。複雑度の高いコーデックは、サーバーのCPU/FPUパワーを大量に消費します。例えば、iLBCは開発元（Global IP Sound）の測定によると、TI C54x DSP上で30msフレームあたり約18 MIPS（20msフレームでは約15 MIPS）を消費します。
- エコーキャンセレーション。エコーキャンセレーションは多くのCPU/FPUを消費する可能性があるため、場合によってはテレフォニーインターフェースカード上のDSPを使用したハードウェアエコーキャンセレーションを選択すべきです。
- 可用性。可用性を高めるためにRAID1または5を使用してください。Asteriskは24時間365日稼働するアプリケーションであることを忘れないでください。

Asteriskサーバーの主要コンポーネントはネットワークアダプターです。優れたサーバー用ネットワークアダプターを推奨します。g.729やiLBCのような複雑度の高いコーデックやエコーキャンセレーションをサポートする必要がある場合、CPUは重要です。専用のDSPを使用することも可能です。Sangoma（旧Digium）は、120通話のg.729同時通話をサポート可能なTC400BというDSPカードを提供しています。ベストプラクティスは、既知のメーカーの新しいサーバークラスのコンピューターを選択することです。特定のマシンが何通話の同時通話や何人の登録ユーザーをサポートできるかを正確に知るには、SIPP（http://sipp.sourceforge.net）のような負荷テストツールを使用してハードウェアをテストする必要があります。Xorcom（http://www.xorcom.com）のような一部のハードウェアメーカーは、その結果をウェブサイトで公開しています。注意：ConfBridgeやMusic on Holdなど、一部のAsteriskアプリケーションは内部タイミングソースを必要とします。現代のLinuxでは、これは組み込みの `res_timing_timerfd` モジュールによって自動的に提供されるため、テレフォニーハードウェアは不要です。（古い `dahdi_dummy` ソフトウェアタイマーは存在しなくなりました。その機能はDAHDI Linux 2.3.0でメインの `dahdi` カーネルモジュールに統合されました。）アクティブなタイマーはCLIコマンド `timing test` で確認できます。

### ハードウェア構成

Asteriskのハードウェアは洗練されている必要はありません。高価なビデオカードや多数の周辺機器は不要です。ハードウェア構成に関するいくつかのヒントを挙げます。

- 不要な割り込みの消費を避けるため、使用していないUSB、シリアル、パラレルポートを無効にします。
- 堅牢なネットワークインターフェースカードが不可欠です。
- テレフォニーインターフェースカードを使用する場合は特に注意してください。一部のカードは3.3ボルトのPCIバスを使用しますが、これに対応するマザーボードを見つけるのは容易ではありません。現在では、PCI Expressの方が容易に入手できます。
- ハードディスクには細心の注意を払ってください。PBXは24時間365日稼働しますが、デスクトップPCは8時間×5日稼働を想定しています。PBXにデスクトップ用ハードウェアを使用しないでください。通常、ハードディスクは1年以内に故障します。サーバーマシン、または24時間365日のアプリケーションを実行するように設計されたアプライアンスを使用することを推奨します。

### IRQ共有

テレフォニーインターフェースカード（例：X100P）は大量の割り込みを生成します。これらの割り込みを処理するにはプロセッサ時間が必要です。別のデバイスが同じ割り込みを使用している場合、ドライバーはその処理を行えません。シングルCPUシステムでは、デバイス間でのIRQ共有を避けるべきです。Asteriskを実行するには専用のハードウェアを使用することを推奨します。外部または不要なハードウェアを無効にすることを忘れないでください。一部のハードウェアはマザーボードのBIOS設定で無効にできます。コンピューターを起動したら、/proc/interruptsで割り当てられた割り込みを確認してください。

```
#cat /proc/interrupts
CPU0
0: 41353058 XT-PIC timer
1: 1988 XT-PIC keyboard
2: 0 XT-PIC cascade
3: 413437739 XT-PIC wctdm <-- TDM400
4: 5721494 XT-PIC eth0
7: 413453581 XT-PIC wcfxo <-- X100P
8: 1 XT-PIC rtc
9: 413445182 XT-PIC wcfxo <-- X100P
12: 0 XT-PIC PS/2 Mouse
14: 179578 XT-PIC ide0
15: 3 XT-PIC ide1
NMI: 0
ERR: 0
```

ここでは3枚のDigiumカードが表示されており、それぞれが独自のIRQを使用しています。システムがこの状態であれば、ハードウェアドライバーのインストールに進んでください。そうでない場合は、戻ってIRQ共有を避けるための対策を講じてください。

## Linuxディストリビューションの選択

Asteriskは当初、Linux上で動作するように開発されました。しかし、BSD UnixやmacOS上でも動作可能です。Asteriskが初めてであれば、はるかに簡単なLinuxから試してください。Asteriskは公式にRHELファミリー（CentOS/RHEL/Fedora）、Ubuntu、Debianをターゲットとしています。今日、実用的な選択肢として適しているのは **Debian 12**、**Ubuntu 22.04 LTS / 24.04 LTS**、**Rocky Linux 9 / AlmaLinux 9** です。CentOS Linuxはサポートが終了しているため、RHELファミリーのシステムではRockyまたはAlmaLinuxを優先してください。本書ではUbuntu 24.04 LTSを使用します。以下の公式リリースディレクトリから最新の24.04ポイントリリースサーバーイメージをダウンロードしてください（正確なファイル名は現在のポイントリリースを含みます。例： `ubuntu-24.04.4-live-server-amd64.iso`）。

```
https://releases.ubuntu.com/24.04/
```

### AsteriskのためのLinux準備

Asteriskのインストール直後に、AsteriskおよびDAHDIドライバーのコンパイルに必要なパッケージをインストールします。まず、apt-setupユーティリティを使用して、パッケージのダウンロード元をDebianに指定します。ステップ1：仮想マシンにUbuntu 24.04 LTS Serverをインストールします（64ビットイメージを使用してください。本書で使用するディストリビューションは64ビットですが、Asterisk自体は32ビットx86もサポートしています）。このトレーニングではVirtualBoxを使用しました。イメージは https://releases.ubuntu.com/24.04 からダウンロードできます。Linuxのインストール手順は本トレーニングの範囲外です。Linuxの基本的な知識は本トレーニングの前提条件となります。

## AsteriskのためのLinuxインストール

グラフィカルユーザーインターフェースを使用せず、通常通りLinuxをインストールしてください。メールサーバーもインストールして設定します。本書の後半でボイスメール通知を送信するためにメールサーバー（exim4）が必要になります。注意：このインストールによりPCがフォーマットされます。ディスク上のすべてのデータが消去されます。開始前に必ずすべてのデータをバックアップしてください。ステップ1：CDをCD-ROMドライブに入れ、PCを起動します。ほとんどの質問に対する回答は非常に単純です。

## 依存関係のインストール

AsteriskとDAHDIをインストールするには、多くのソフトウェア依存関係をインストールする必要があります。Asterisk 22でこれを実行する推奨方法は、ソースツリーに付属のスクリプトを使用することです。このスクリプトは、サポートされている各ディストリビューションの正しいパッケージ名を知っています。Asteriskソースをダウンロードして展開した後（以下の「Asteriskのコンパイル」を参照）、以下を実行します。

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

ステップ1：rootとしてログインします（または `sudo` を使用します）。ステップ2：Debian/Ubuntuシステムで依存関係を手動でインストールしたい場合、同等のパッケージリストは以下の通りです。

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

Asteriskソースは現在Gitでホストされているため、 `subversion` は不要です。また、現代のDebian/Ubuntuはバージョン付きの `libncurses5-dev` ではなく `libncurses-dev` を提供しています。スクリプトは常にディストリビューションの正しいパッケージ名を追跡するため、手動で管理するリストよりも `./contrib/scripts/install_prereq install` を優先してください。

### DAHDI

DAHDI（Digium/Sangoma Asterisk Hardware Device Interface）は、アナログおよびデジタルカード用のドライバーアーキテクチャです。アナログまたはデジタルインターフェースを使用する予定がある場合は、Asteriskをインストールする前にDAHDIをインストールすることが重要です。DAHDIはアナログ/デジタルテレフォニーカードのために依然として存在しますが、ますますニッチな存在になっています。現代の導入のほとんどは純粋なVoIPであり、このセクションを完全にスキップできます。物理的なテレフォニーインターフェースハードウェアがある場合のみDAHDIをインストールしてください。以下のコマンドでソースファイルを取得します。

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

以下のコマンドでファイルを解凍します。

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### DAHDIドライバーのコンパイル

DAHDIモジュールをコンパイルする必要があります。./configureおよびmake menuselectコマンドは数年前に導入されました。後者は、どのユーティリティとモジュールをビルドするかを選択できるようにします。以下のコマンドでこれを実行します。

```
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version downloaded
make
make install
cd ../tools
autoreconf -i
./configure
make
make install
```

make install-configによりDAHDIの設定が完了します。DAHDIハードウェアがある場合は、このシステムにインストールされているDAHDIハードウェアのサポートのみをロードするように /etc/dahdi/modules を編集することを推奨します。デフォルトでは、すべてのDAHDIハードウェアのサポートがDAHDI起動時にロードされます。システム上のDAHDIハードウェアは以下の通りと推測されます：usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware。上記の画面は、特定の構成に必要なドライバーのみをロードするように /etc/dahdi/modules ファイルを変更し、検出されたハードウェアを表示するように求めています。/etc/dahdi/modules ファイルを編集し、必要なハードウェアのみをロードしてください。私の場合、Xorcom Astribank 6FXSおよび2FXOを備えたテストマシンを使用していました。ファイルは以下の通りです。

```
# Contains the list of modules to be loaded / unloaded by /etc/init.d/dahdi.
#
# NOTE:  Please add/edit /etc/modprobe.d/dahdi or /etc/modprobe.conf if you
#        would like to add any module parameters.
#
# Format of this file: list of modules, each in its own line.
# Anything after a '#' is ignore, likewise trailing and leading
# whitespaces and empty lines.
# Digium TE205P/TE207P/TE210P/TE212P: PCI dual-port T1/E1/J1
# Digium TE405P/TE407P/TE410P/TE412P: PCI quad-port T1/E1/J1
# Digium TE220: PCI-Express dual-port T1/E1/J1
# Digium TE420: PCI-Express quad-port T1/E1/J1
#wct4xxp
# Digium TE120P: PCI single-port T1/E1/J1
# Digium TE121: PCI-Express single-port T1/E1/J1
# Digium TE122: PCI single-port T1/E1/J1
#wcte12xp
# Digium T100P: PCI single-port T1
# Digium E100P: PCI single-port E1
#wct1xxp
# Digium TE110P: PCI single-port T1/E1/J1
#wcte11xp
# Digium TDM2400P/AEX2400: up to 24 analog ports
# Digium TDM800P/AEX800: up to 8 analog ports
# Digium TDM410P/AEX410: up to 4 analog ports
#wctdm24xxp
# X100P - Single port FXO interface
# X101P - Single port FXO interface
#wcfxo
# Digium TDM400P: up to 4 analog ports
#wctdm
# Xorcom Astribank Devices
xpp_usb
```

コンピューターを再初期化し、ドライバーが正しくロードされていることを確認してください。

## バージョンの選択

経験則として、必要な機能を備えたバージョンを使用すべきです。Asteriskは、LTS（長期サポート）と標準リリースを交互に行うリリースモデルを採用しています。本書執筆時点で、**Asterisk 22は最新のLTSリリース**（2024年10月リリース。最新のポイントリリースは22.10.0）であり、今選択するのに最適です。Asterisk 20は前回のLTSであり、バージョン16（初版で使用）はサポートが終了しています。本番システムでは、常にLTSリリースを選択してください。

> **[第2版注]** 著者/印刷時の確認のみ：downloads.asterisk.orgで最新の22.xポイントリリースを確認し、新しいリリースが出ている場合は上記のバージョン文字列を更新してください。

## Asteriskのコンパイル

以前にソフトウェアをコンパイルしたことがあれば、Asteriskのコンパイルは簡単な作業です。以下のコマンドを実行してAsteriskをコンパイルおよびインストールします。make menuselectを使用して、ビルドするアプリケーションとモジュールを選択できることを忘れないでください。ステップ1：ソースコードをダウンロードします。

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

ステップ2：ビルドの前提条件をインストールします（上記の「依存関係のインストール」を参照）。

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

ステップ3：ビルドを設定します。

```
./configure
```

ステップ4：ビルドするモジュールを選択します。

```
make menuselect
```

make menuselectを使用して、必要なモジュールのみをインストールします。Asterisk 22では、SIPチャネルは **chan_pjsip** です（デフォルトでビルドされます）。古い **chan_sip** はAsterisk 21で削除され、存在しません。Opusの *パススルー* はそのまま動作します（ツリー内の `res_format_attr_opus` モジュールがSDPネゴシエーションを処理します）が、**codec_opus** トランスコーディングモジュールは依然としてSangoma/Digiumの外部クローズドソースバイナリです。menuselectでこれを選択すると、Digiumのサーバーからダウンロードされます。このバイナリは無料です。詳細は以下の「menuselectによるモジュールの選択」を参照してください。

ステップ5：Asteriskをビルドしてインストールし、デフォルトの設定ファイルとサンプルファイルを作成します。

```
make
make install
make samples
make config
ldconfig
```

`make install` はバイナリとモジュールをインストールし、 `make samples` はサンプル設定ファイルを `/etc/asterisk` に書き込み、 `make config` は検出されたディストリビューション用のSysV init起動スクリプト（例：Debian/Ubuntu上の `/etc/init.d/asterisk` ）をインストールし、 `ldconfig` は共有ライブラリキャッシュを更新します。systemdユニットもソースツリーの `contrib/systemd/asterisk.service` に付属していますが、 `make config` はそれを自動的にインストールしません。systemd下でAsteriskを実行したい場合は、自分で適切な場所にコピーしてください（下記参照）。

### menuselectによるモジュールの選択

`make menuselect` は、ビルドするアプリケーション、コーデック、チャネル、リソースを正確に選択できるテキストベースのメニューを開きます。Asterisk 22固有の注意点：

- **chan_pjsip**（*Channel Drivers*配下）は最新のSIPチャネルであり、デフォルトで有効になっています。Asterisk 22における唯一のSIPチャネルです。
- **codec_opus**（*Codec Translators*配下）は **外部** モジュールです（menuselectのエントリには「Download the Opus codec from Digium」と表示されます）。これを有効にすると、 `make` がSangoma/Digiumから無料のクローズドソースバイナリを取得します。Opusパススルー自体には追加モジュールは不要です。Sangomaの **codec_g729** モジュールも利用可能です。バイナリのダウンロードは無料ですが、合法的なG.729トランスコーディングには、チャネルごとのライセンス購入が必要です。
- *Core Sound Packages*、*Music On Hold File Packages*、*Extras Sound Packages*メニューで必要なサウンドフォーマットと言語を選択してください。チェックを入れたものはすべて、 `make install` の実行中に自動的にダウンロードおよびインストールされます。

選択が完了したら、**Save & Exit** を選択し、 `make` に進みます。

> **[第2版注]** 著者のアクション：初版の `make menuselect` スクリーンショットを、Channel Drivers画面にchan_pjsipが表示され、chan_sip/chan_skinny/chan_mgcpが表示されない最新のAsterisk 22のキャプチャに差し替えてください。

## Asteriskの起動と停止

この最小構成で、Asteriskを正常に起動できます。学習やデバッグのために、コンソールに接続した状態でフォアグラウンドでAsteriskを起動できます。

```
/usr/sbin/asterisk –vvvgc
```

CLIコマンド stop now を使用してAsteriskをシャットダウンします。

```
CLI>core stop now
```

### systemdによるAsteriskの起動

現代のLinuxディストリビューション（Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9）では、システムサービスマネージャーは **systemd** です。Asteriskはソースツリーの `contrib/systemd/asterisk.service` にsystemdユニットを同梱しています。これを `/etc/systemd/system/asterisk.service` にコピーし、 `systemctl daemon-reload` を実行してください。インストール後、本番環境でAsteriskを実行する推奨方法は `systemctl` を通すことです。

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Asteriskがサービスとして実行されたら、 `asterisk -r` （接続）または `asterisk -rvvv` （詳細出力付きで接続）を使用してCLIに接続します。

古いシステムでは、AsteriskはレガシーなSysV initスクリプト（ `/etc/init.d/asterisk` ）と、クラッシュ時にAsteriskを自動再起動する **safe_asterisk** ラッパーを介して起動されていました。systemdでは、自動再起動はユニットファイルの `Restart=` ディレクティブによって処理されるため、一般的に `safe_asterisk` は不要です。レガシーなinit/ `safe_asterisk` のアプローチは依然として機能しますが、systemdベースのディストリビューションでは非推奨です。

### Asteriskの実行時オプション

Asteriskの起動プロセスは非常に単純です。パラメーターなしでAsteriskを実行すると、デーモンとして起動します。

```
/sbin/asterisk
```

以下のコマンドを実行してAsteriskコンソールにアクセスできます。同時に複数のコンソールプロセスを実行できることに注意してください。

```
/sbin/asterisk -r
```

### Asteriskで利用可能な実行時オプション

asterisk –h を使用して、利用可能な実行時オプションを表示できます。

```
sipast:/usr/src/asterisk-22.x.y# asterisk -h
```

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others. Usage: asterisk [OPTIONS] Valid Options: -V バージョン番号を表示して終了 -C <configfile> 代替設定ファイルを使用 -G <group> 呼び出し元以外のグループとして実行 -U <user> 呼び出し元以外のユーザーとして実行 -c コンソールCLIを提供 -d デバッグを増やす（dが多いほどデバッグ詳細が増加） -f フォークしない -F 常にフォークする -g クラッシュ時にコアをダンプ -h このヘルプ画面 -i 起動時に暗号キーを初期化 -L <load> 新しい通話を拒否する前の最大負荷平均を制限 -M <value> 最大通話数を指定値に制限 -m コンソール上のデバッグおよびコンソール出力をミュート -n コンソールカラーを無効化。起動時のみ使用可能。 -p 疑似リアルタイムスレッドとして実行 -q 静音モード（出力を抑制） -r このマシン上のAsteriskに接続 -R -rと同じだが、切断された場合に再接続を試みる -s <socket> ソケット <socket> を介してAsteriskに接続（-rでのみ有効） -t サウンドファイルを /var/tmp に記録し、完了後に本来の場所へ移動 -T CLIへの各出力行の時間を [Mmm dd hh:mm:ss] 形式で表示。リモートコンソールモードでは使用不可。 -v 詳細出力を増やす（vが多いほど詳細） -x <cmd> コマンド <cmd> を実行（-rを意味する） -X asterisk.conf で #exec の使用を有効化 -W 明るい背景を補正するために端末の色を調整

## インストールディレクトリ

Asteriskはいくつかのディレクトリにインストールされます。これらは asterisk.conf ファイルで変更可能です。トレーニング目的であればverboseを3から15に変更しますが、本番環境では3のままにしてください。max_callsおよびmax_loadオプションは、システムの過負荷を防ぐための優れたオプションです。

### asterisk.conf

```
[directories](!) ; remove the (!) to enable this
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk
astsbindir => /usr/sbin
[options]
;verbose = 3
;debug = 3
;refdebug = yes                 ; Enable reference count debug logging.
;alwaysfork = yes               ; Same as -F at startup.
;nofork = yes                   ; Same as -f at startup.
;quiet = yes                    ; Same as -q at startup.
;timestamp = yes                ; Same as -T at startup.
;execincludes = yes             ; Support #exec in config files.
;console = yes                  ; Run as console (same as -c at startup).
;highpriority = yes             ; Run realtime priority (same as -p at
                                ; startup).
;initcrypto = yes               ; Initialize crypto keys (same as -i at
                                ; startup).
;nocolor = yes                  ; Disable console colors.
;dontwarn = yes                 ; Disable some warnings.
;dumpcore = yes                 ; Dump core on crash (same as -g at startup).
;languageprefix = yes           ; Use the new sound prefix path syntax.
;systemname = my_system_name    ; Prefix uniqueid with a system name for
                                ; Global uniqueness issues.
;autosystemname = yes           ; Automatically set systemname to hostname,
                                ; uses 'localhost' on failure, or systemname if
                                ; set.
;mindtmfduration = 80           ; Set minimum DTMF duration in ms (default 80
ms)
                                ; If we get shorter DTMF messages, these will
be
                                ; changed to the minimum duration
;maxcalls = 10                  ; Maximum amount of calls allowed.
;maxload = 0.9                  ; Asterisk stops accepting new calls if the
                                ; load average exceed this limit.
;maxfiles = 1000                ; Maximum amount of openfiles.
;minmemfree = 1                 ; In MBs, Asterisk stops accepting new calls if
                                ; the amount of free memory falls below this
                                ; watermark.
;cache_media_frames = yes       ; Cache media frames for performance
                                ; Disable this option to help track down media
frame
                                ; mismanagement when using valgrind or
MALLOC_DEBUG.
                                ; The cache gets in the way of determining if
the
                                ; frame is used after being freed and who freed
it.
                                ; NOTE: This option has no effect when Asterisk
is
                                ; compiled with the LOW_MEMORY compile time
option
                                ; enabled because the cache code does not
exist.
                                ; Default yes
;cache_record_files = yes       ; Cache recorded sound files to another
                                ; directory during recording.
;record_cache_dir = /tmp        ; Specify cache directory (used in conjunction
                                ; with cache_record_files).
;transmit_silence = yes         ; Transmit silence while a channel is in a
                                ; waiting state, a recording only state, or
                                ; when DTMF is being generated.  Note that the
                                ; silence internally is generated in raw signed
                                ; linear format. This means that it must be
                                ; transcoded into the native format of the
                                ; channel before it can be sent to the device.
                                ; It is for this reason that this is optional,
                                ; as it may result in requiring a temporary
                                ; codec translation path for a channel that may
                                ; not otherwise require one.
;transcode_via_sln = yes        ; Build transcode paths via SLINEAR, instead of
                                ; directly.
;runuser = asterisk             ; The user to run as.
;rungroup = asterisk            ; The group to run as.
;lightbackground = yes          ; If your terminal is set for a light-colored
                                ; background.
;forceblackbackground = yes     ; Force the background of the terminal to be
                                ; black, in order for terminal colors to show
                                ; up properly.
;defaultlanguage = en           ; Default language
documentation_language = en_US  ; Set the language you want documentation
                                ; displayed in. Value is in the same format as
                                ; locale names.
;hideconnect = yes              ; Hide messages displayed when a remote console
                                ; connects and disconnects.
;lockconfdir = no               ; Protect the directory containing the
                                ; configuration files (/etc/asterisk) with a
                                ; lock.
;live_dangerously = no          ; Enable the execution of 'dangerous' dialplan
                                ; functions from external sources (AMI,
                                ; etc.) These functions (such as SHELL) are
                                ; considered dangerous because they can allow
                                ; privilege escalation.
                                ; Default no
;entityid=00:11:22:33:44:55     ; Entity ID.
                                ; This is in the form of a MAC address.
                                ; It should be universally unique.
                                ; It must be unique between servers
communicating
                                ; with a protocol that uses this value.
                                ; This is currently is used by DUNDi and
                                ; Exchanging Device and Mailbox State
                                ; using protocols: XMPP, Corosync and PJSIP.
;rtp_use_dynamic = yes          ; When set to "yes" RTP dynamic payload types
                                ; are assigned dynamically per RTP instance vs.
                                ; allowing Asterisk to globally initialize them
                                ; to pre-designated numbers (defaults to
"yes").
;rtp_pt_dynamic = 35            ; Normally the Dynamic RTP Payload Type numbers
                                ; are 96-127, which allow just 32 formats. The
                                ; starting point 35 enables the range 35-63 and
                                ; allows 29 additional formats. When you use
                                ; more than 32 formats in the dynamic range and
                                ; calls are not accepted by a remote
                                ; implementation, please report this and go
                                ; back to value 96.
; Changing the following lines may compromise your security.
;[files]
;astctlpermissions = 0660
;astctlowner = root
;astctlgroup = apache
;astctl = asterisk.ctl
```

## ログファイルとログローテーション

Asterisk PBXはメッセージを /var/log/asterisk ディレクトリに記録します。ログを制御するファイルは以下の通りです。

```
is the logger.conf.
;
; Logging Configuration
;
; In this file, you configure logging to files or to
; the syslog system.
;
; "logger reload" at the CLI will reload configuration
; of the logging system.
[general]
;
; Customize the display of debug message time stamps
; this example is the ISO 8601 date format (yyyy-mm-dd HH:MM:SS)
;
; see strftime(3) Linux manual for format specifiers.  Note that there is also
; a fractional second parameter which may be used in this field.  Use %1q
; for tenths, %2q for hundredths, etc.
;
;dateformat=%F %T       ; ISO 8601 date format
;dateformat=%F %T.%3q   ; with milliseconds
;
;
; This makes Asterisk write callids to log messages
; (defaults to yes)
;use_callids = no
;
; This appends the hostname to the name of the log files.
;appendhostname = yes
;
; This determines whether or not we log queue events to a file
; (defaults to yes).
;queue_log = no
;
; Determines whether the queue_log always goes to a file, even
; when a realtime backend is present (defaults to no).
;queue_log_to_file = yes
;
; Set the queue_log filename
; (defaults to queue_log)
;queue_log_name = queue_log
;
; When using realtime for the queue log, use GMT for the timestamp
; instead of localtime.  The default of this option is 'no'.
;queue_log_realtime_use_gmt = yes
;
; Log rotation strategy:
; none:  Do not perform any logrotation at all.  You should make
;        very sure to set up some external logrotate mechanism
;        as the asterisk logs can get very large, very quickly.
; sequential:  Rename archived logs in order, such that the newest
;              has the highest sequence number [default].  When
;              exec_after_rotate is set, ${filename} will specify
;              the new archived logfile.
; rotate:  Rotate all the old files, such that the oldest has the
;          highest sequence number [this is the expected behavior
;          for Unix administrators].  When exec_after_rotate is
;          set, ${filename} will specify the original root filename.
; timestamp:  Rename the logfiles using a timestamp instead of a
;             sequence number when "logger rotate" is executed.
;             When exec_after_rotate is set, ${filename} will
;             specify the new archived logfile.
;rotatestrategy = rotate
;
; Run a system command after rotating the files.  This is mainly
; useful for rotatestrategy=rotate. The example allows the last
; two archive files to remain uncompressed, but after that point,
; they are compressed on disk.
;
; exec_after_rotate=gzip -9 ${filename}.2
;
;
; For each file, specify what to log.
;
; For console logging, you set options at start of
; Asterisk with -v for verbose and -d for debug
; See 'asterisk -h' for more information.
;
; Directory for log files is configures in asterisk.conf
; option astlogdir
;
; All log messages go to a queue serviced by a single thread
; which does all the IO.  This setting controls how big that
; queue can get (and therefore how much memory is allocated)
; before new messages are discarded.
; The default is 1000
;logger_queue_limit = 250
;
;
[logfiles]
;
; Format is:
;
; logger_name => [formatter]levels
;
; The name of the logger dictates not only the name of the logging
; channel, but also its type. Valid types are:
;   - 'console'  - The root console of Asterisk
;   - 'syslog'   - Linux syslog, with facilities specified afterwards with
;                  a period delimiter, e.g., 'syslog.local0'
;   - 'filename' - The name of the log file to create. This is the default
;                  for log channels.
;
; Filenames can either be relative to the standard Asterisk log directory
; (see 'astlogdir' in asterisk.conf), or absolute paths that begin with
; '/'.
;
; An optional formatter can be specified prior to the log levels sent
; to the log channel. The formatter is defined immediately preceeding the
; levels, and is enclosed in square brackets. Valid formatters are:
;   - [default] - The default formatter, this outputs log messages using a
;                 human readable format.
;   - [json]    - Log the output in JSON. Note that JSON formatted log entries,
;                 if specified for a logger type of 'console', will be formatted
;                 per the 'default' formatter for log messages of type VERBOSE.
;                 This is due to the remote consoles intepreting verbosity
;                 outside of the logging subsystem.
;
; Log levels include the following, and are specified in a comma delineated
; list:
;    debug
;    notice
;    warning
;    error
;    verbose(<level>)
;    dtmf
;    fax
;    security
;
; Verbose takes an optional argument, in the form of an integer level.
; Verbose messages with higher levels will not be logged to the file.  If
; the verbose level is not specified, it will log verbose messages following
; the current level of the root console.
;
; Special level name "*" means all levels, even dynamic levels registered
; by modules after the logger has been initialized (this means that loading
; and unloading modules that create/remove dynamic logger levels will result
; in these levels being included on filenames that have a level name of "*",
; without any need to perform a 'logger reload' or similar operation).
; Note that there is no value in specifying both "*" and specific level names
; for a filename; the "*" level means all levels.  The only exception is if
; you need to specify a specific verbose level. e.g, "verbose(3),*".
;
; We highly recommend that you DO NOT turn on debug mode if you are simply
; running a production system.  Debug mode turns on a LOT of extra messages,
; most of which you are unlikely to understand without an understanding of
; the underlying code.  Do NOT report debug messages as code issues, unless
; you have a specific issue that you are attempting to debug.  They are
; messages for just that -- debugging -- and do not rise to the level of
; something that merit your attention as an Asterisk administrator.  Debug
; messages are also very verbose and can and do fill up logfiles quickly;
; this is another reason not to have debug mode on a production system unless
; you are in the process of debugging a specific issue.
;
;debug => debug
;security => security
console => notice,warning,error
;console => notice,warning,error,debug
messages => notice,warning,error
;full => notice,warning,error,debug,verbose,dtmf,fax
;
;full-json => [json]debug,verbose,notice,warning,error,dtmf,fax
;
;syslog keyword : This special keyword logs to syslog facility
;
;syslog.local0 => notice,warning,error
```

; 一部のコンソールコマンドはロガープロセスに関連付けられています。

```
CLI> logger show channels
Logger queue limit: 1000

Channel                             Type     Formatter  Status    Configuration
-------                             ----     ---------  ------    -------------
/var/log/asterisk/security          File     default    Enabled    - SECURITY
/var/log/asterisk/full              File     default    Enabled    - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages          File     default    Enabled    - NOTICE WARNING ERROR
CLI> logger rotate
  == Parsing '/etc/asterisk/logger.conf': Found
Asterisk Event Logger restarted
Asterisk Queue Logger restarted
You can control the log rotation using the logrotate daemon. Edit the file
/etc/logrotate.d and include the content below to start rotating the log files.
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
       /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

logrotateに関する詳細は以下を使用して取得できます。

```
#man logrotate
```

## Asteriskのアンインストール

Asteriskをアンインストールするには、以下を使用します。

```
make uninstall
```

Asteriskとすべての設定ファイルをアンインストールするには、以下を使用します。

```
make uninstall-all
```

## Asteriskインストールに関する注意点

このセクションでは、Asteriskをインストールする前に解決すべき問題についていくつかのアドバイスを提供します。

### 本番システム

Asteriskを本番環境にインストールする場合は、システム設計に注意を払う必要があります。サーバーは、テレフォニーシステムが他のシステムプロセスよりも優先されるように最適化する必要があります。Asteriskは、X-Windowsのようなプロセッサ集約型のソフトウェアと一緒に実行すべきではありません。CPU集約型のプロセス（巨大なデータベースなど）を実行する必要がある場合は、別のサーバーを使用してください。一般的に、Asteriskはハードウェアパフォーマンスの変動の影響を受けやすいです。そのため、CPU使用率が40%を超えないハードウェア環境でAsteriskを使用するようにしてください。

### ネットワークのヒント

IP電話を使用する予定がある場合は、ネットワークに注意を払うことが重要です。音声プロトコルは非常に優れており、遅延やジッターにも耐性がありますが、設定が不十分なローカルエリアネットワークを使用すると、音声品質が低下します。スイッチやルーターでサービス品質（QoS）を使用することによってのみ、良好な音声品質を保証できます。ローカルエリアネットワーク内の音声は良好な傾向にありますが、LAN環境であっても、衝突が多すぎる10 Mbpsハブを使用していると、最終的に音声が歪んだり、ひどい品質になったりします。可能な限り最高の音声品質を確保するために、以下の推奨事項に従ってください。

- 可能であれば、または経済的に実現可能であれば、エンドツーエンドのQoSを使用してください。エンドツーエンドのQoSを使用すれば、音声品質は完璧です。言い訳は無用です！
- 本番環境で音声用に10/100 Mbpsハブを使用することは避けてください。衝突はネットワークにジッターを課す可能性があります。衝突が発生しない全二重10/100 Mbpsが推奨されます。
- 音声ネットワークの不要なブロードキャストを分離するためにVLANを使用してください。ARPブロードキャストで音声ネットワークが破壊されるような事態は避けたいはずです。
- 音声ネットワークにおける期待値についてユーザーを教育してください。QoSがない場合、音声が完璧であるとは言わないでください。ほとんどの場合、そうはならないからです。多くの場合、携帯電話と同等の音声品質が達成されます。ファームウェアやハードウェア設計の問題が一般的であるため、高品質な電話機を使用してください。

## まとめ

本章では、最小ハードウェア要件、およびAsteriskのダウンロード、インストール、コンパイル方法について学びました。セキュリティ上の理由から、Asteriskはroot以外のユーザーで実行する必要があります。本番環境を開始する前に、ネットワーク環境を確認してください。

## クイズ

1. Asterisk 22において、SIPサポートを提供するチャネルドライバーはどれですか。また、古い `chan_sip` はどうなりましたか？
   - A. `chan_sip` が依然としてデフォルトであり、 `chan_pjsip` はオプションです。
   - B. `chan_pjsip` がデフォルトのSIPチャネルであり、 `chan_sip` はAsterisk 21で削除され、存在しません。
   - C. 両方がデフォルトでビルドされ、実行時に選択します。
   - D. SIPサポートはIAX2を優先して完全に削除されました。
2. Asterisk用のテレフォニーインターフェースカードには通常、デジタル信号プロセッサ（DSP）が組み込まれているため、PCのCPUをあまり必要としません。
   - A. 正
   - B. 誤
3. 完璧な音声品質が必要な場合は、エンドツーエンドのサービス品質（QoS）を実装する必要があります。
   - A. 正
   - B. 誤
4. 最新のAsteriskバージョンが最も安定しているため、常に最新バージョンを選択すべきです。
   - A. 正
   - B. 誤
5. Asterisk 22のビルド依存関係をインストールする推奨方法は何ですか？
6. TDMインターフェースカードがない場合でも、Linux上の `res_timing_timerfd` モジュールによって提供される内部タイミングソースがあります。このタイミングは、________ や ________ などのアプリケーションで使用されます。
7. Asteriskをインストールする際は、グラフィカルインターフェースがCPUサイクルを消費するため、GNOMEやKDEなどのデスクトップ環境は除外する方が良いです。
   - A. 正
   - B. 誤
8. Asteriskの設定ファイルは ________ ディレクトリにあります。
9. Asteriskのサンプル設定ファイルをインストールするには、コマンド ________ を入力します。
10. Asteriskをroot以外のユーザーとして実行することが重要な理由は何ですか？

**回答:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — 展開したAsteriskソースツリーから `./contrib/scripts/install_prereq install` を実行する · 6 — ConfBridgeおよびMusic on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — セキュリティ（Asteriskが侵害された場合の被害を制限するため）
