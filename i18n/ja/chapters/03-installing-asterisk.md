# Installing Asterisk 22

第1章では、テレフォニー環境においてAsteriskがどのように役立つかを学びました。本章では、Asteriskのダウンロードとインストール方法について解説します。作業を始める前に、コンパイルとインストールの方法を学ぶことが不可欠です。コンパイルのプロセスは、従来のMicrosoft™ Windows™ユーザーには奇妙に思えるかもしれませんが、Linux™環境ではごく一般的なことです。Asteriskをコンパイルすることで、使用するハードウェアに最適化されたコードを得ることができます。これが、ここで行う作業です。Asteriskはいくつかのオペレーティングシステムで動作しますが、ここでは話を簡単にするために、Linuxのみを対象とします。依存関係のインストールが容易で、フットプリントが小さく安定しているという理由から、Linux™ディストリビューションとしてDebianを選択しました。別のディストリビューションを使用したい場合は、それに応じて依存関係の名前を変更してください。

> **[2nd-ed note]** 本版は **Asterisk 22 LTS**（2024年リリース、2028年10月16日までフルサポート）を対象としています。Asterisk 22は現在の長期サポートリリースです。Digiumは **Sangoma** に買収（2018年）されており、現在AsteriskはSangomaによってスポンサーされていることに注意してください。本章全体を通して言及される「Digium」は、レガシーハードウェアの旧ブランドを指します。

## 目標

本章を読み終えることで、以下のことができるようになります。

- Asteriskに必要なハードウェア要件を判断する
- 必要な依存関係を備えたLinuxをインストールする
- HTTPS経由で安定版をダウンロードする
- Asteriskをコンパイルする
- 起動時にAsteriskを開始する方法を学ぶ

## 最小ハードウェア要件

Asteriskの実行に高性能なハードウェアは必要ありませんが、要件に合わせて最適なハードウェアを選択するためのヒントがいくつかあります。ハードウェアを選択する際は、以下の主要な要素を考慮する必要があります。

- 登録ユーザーの総数。サポートが必要な1秒あたりの登録数を定義します
- 同時通話の総数。Asteriskサーバーのネットワークアダプターおよびブリッジで処理する必要があるネットワーク会話の数を定義します
- サポートが必要なcodec。複雑度の高いcodecは、サーバーのCPU/FPUパワーを大量に消費します。例えば、iLBCは作成者（Global IP Sound）によって、TI C54x DSP上で30 msフレームあたり約18 MIPS（20 msフレームでは約15 MIPS）と測定されています
- エコーキャンセレーション。エコーキャンセレーションは多くのCPU/FPUを消費する可能性があるため、場合によってはテレフォニーインターフェースカード上のDSPを使用したハードウェアエコーキャンセレーションを選択する必要があります
- 可用性。可用性を高めるためにRAID1または5を使用してください。Asteriskは24時間365日稼働するアプリケーションであることを忘れないでください。

Asteriskサーバーの主要コンポーネントはネットワークアダプターです。優れたサーバー用ネットワークアダプターを推奨します。g.729やiLBCのような複雑度の高いcodecやエコーキャンセレーションをサポートする必要がある場合、CPUは重要です。専用のDSPを使用することも選択肢です。Sangoma（旧Digium）は、120のg729同時通話をサポート可能なTC400BというDSPカードを提供しています。ベストプラクティスは、既知のメーカーの新しいサーバークラスのコンピューターを選択することです。特定のマシンが何件の同時通話や登録ユーザーをサポートできるかを正確に知るには、SIPP（http://sipp.sourceforge.net）のようなストレステストツールを使用してハードウェアをテストする必要があります。Xorcom（http://www.xorcom.com）のような一部のハードウェアメーカーは、その結果をウェブサイトで公開しています。注意：ConfBridgeやMusic on Holdなど、一部のAsteriskアプリケーションには内部タイミングソースが必要です。最新のLinuxでは、これは組み込みの `res_timing_timerfd` モジュールによって自動的に提供されるため、テレフォニーハードウェアは不要です。（古い `dahdi_dummy` ソフトウェアタイマーは存在しなくなりました。その機能はDAHDI Linux 2.3.0でメインの `dahdi` カーネルモジュールに統合されました。）アクティブなタイマーは、CLIコマンド `timing test` で確認できます。

### ハードウェア構成

Asteriskのハードウェアは洗練されている必要はありません。高価なビデオカードや多数の周辺機器は不要です。ハードウェア構成に関するいくつかのヒント：

- 不要な割り込みの消費を避けるため、使用していないUSB、シリアル、パラレルポートを無効にします。
- 堅牢なネットワークインターフェースカードが不可欠です。
- テレフォニーインターフェースカードを使用する場合は特に注意してください。一部のカードは3.3ボルトのPCIバスを使用しており、それに対応するマザーボードを見つけるのは容易ではありません。現在では、PCI Expressの方が簡単に見つかります。
- ハードディスクには細心の注意を払ってください。PBXは24時間365日の体制で動作しますが、デスクトップは8時間×5日です。PBXにデスクトップ用ハードウェアを使用しないでください。通常、ハードディスクは1年以内に故障します。サーバーマシン、または24時間365日のアプリケーションを実行するように設計されたアプライアンスを使用することを推奨します。

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

ここでは、それぞれが独自のIRQを持つ3枚のDigiumカードを確認できます。システムがこの状態であれば、ハードウェアドライバーのインストールに進んでください。そうでない場合は、戻ってIRQ共有を避けるための別の方法を試してください。

## Linuxディストリビューションの選択

Asteriskは当初、Linux上で動作するように開発されました。しかし、BSD UnixやmacOSでも動作可能です。Asteriskが初めてであれば、はるかに簡単なLinuxを最初に試してください。Asteriskは公式にRHELファミリー（CentOS/RHEL/Fedora）、Ubuntu、Debianをターゲットとしています。今日、実用的な選択肢として優れているのは **Debian 12**、**Ubuntu 22.04 LTS / 24.04 LTS**、**Rocky Linux 9 / AlmaLinux 9** です。CentOS Linuxはサポートが終了しているため、RHELファミリーのシステムではRockyまたはAlmaLinuxを優先してください。本書ではUbuntu 24.04 LTSを使用します。以下の公式リリースディレクトリから最新の24.04ポイントリリースサーバーイメージをダウンロードしてください（正確なファイル名は現在のポイントリリースを含みます。例： `ubuntu-24.04.4-live-server-amd64.iso`）：

```
https://releases.ubuntu.com/24.04/
```

### AsteriskのためのLinux準備

Asteriskのインストール直後に、AsteriskおよびDAHDIドライバーのコンパイルに必要なパッケージをインストールします。まず、パッケージのダウンロード元をDebianに指定します。これはapt-setupユーティリティを使用して行います。ステップ1：仮想マシンにUbuntu 24.04 LTS Serverをインストールします（64ビットイメージを使用してください。本書で使用するディストリビューションは64ビットですが、Asterisk自体は依然として32ビットx86もサポートしています）。このトレーニングではVirtualBoxを使用しました。イメージは https://releases.ubuntu.com/24.04 からダウンロードできます。Linuxのインストールはこのトレーニングの範囲外です。Linuxの基本的な知識がこのトレーニングの前提条件となります。

## AsteriskのためのLinuxインストール

グラフィカルユーザーインターフェースなしで、通常通りLinuxをインストールしてください。メールサーバーもインストールして設定します。本書の後半でボイスメール通知を送信するためにメールサーバー（exim4）が必要になります。注意：このインストールを行うとPCがフォーマットされます。ディスク内のすべてのデータが消去されます。開始前に必ずすべてのデータをバックアップしてください。ステップ1：CDをCD-ROMドライブに入れ、PCを起動します。ほとんどの質問は非常に簡単に答えられます。

## 依存関係のインストール

AsteriskとDAHDIをインストールするには、多くのソフトウェア依存関係をインストールする必要があります。Asterisk 22でこれを推奨する方法は、ソースツリーに同梱されているスクリプトを使用することです。このスクリプトは、サポートされている各ディストリビューションの正しいパッケージ名を知っています。Asteriskのソースをダウンロードして展開した後（以下の「Asteriskのコンパイル」を参照）、以下を実行します：

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

ステップ1：rootとしてログインします（または `sudo` を使用します）。ステップ2：Debian/Ubuntuシステムで依存関係を手動でインストールしたい場合、同等のパッケージリストは以下の通りです：

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

> **[2nd-ed note]** 元のリストは `subversion`、 `libnewt-dev`、および `libncurses5-dev` を参照していました。Asteriskのソースは現在Gitでホストされており（Subversionは不要になりました）、最新のDebian/Ubuntuはバージョン付きの `libncurses5-dev` ではなく `libncurses-dev` を提供しています。手動で管理するリストよりも `./contrib/scripts/install_prereq install` を優先してください。

### DAHDI

DAHDI（Digium/Sangoma Asterisk Hardware Device Interface）は、アナログおよびデジタルカード用のドライバーアーキテクチャです。アナログまたはデジタルインターフェースを使用する予定がある場合は、Asteriskをインストールする前にDAHDIをインストールすることが重要です。DAHDIはアナログ/デジタルテレフォニーカードのために依然として存在しますが、ますますニッチな存在になっています。最新の展開のほとんどは純粋なVoIPであり、このセクションを完全にスキップできます。物理的なテレフォニーインターフェースハードウェアがある場合のみDAHDIをインストールしてください。以下のコマンドでソースファイルを取得します：

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

以下のコマンドでファイルを解凍します：

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### DAHDIドライバーのコンパイル

DAHDIモジュールをコンパイルする必要があります。./configureおよびmake menuselectコマンドは数年前に導入されました。後者は、どのユーティリティとモジュールをビルドするかを選択できるようにします。以下のコマンドでこれを行います：

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

make install-configによりDAHDIが設定されました。DAHDIハードウェアがある場合は、このシステムにインストールされているDAHDIハードウェアのサポートのみをロードするように /etc/dahdi/modules を編集することを推奨します。デフォルトでは、すべてのDAHDIハードウェアのサポートがDAHDI開始時にロードされます。システム上のDAHDIハードウェアは以下の通りと思われます：usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware この画面（上記）は、特定の構成に必要なドライバーのみをロードし、検出されたハードウェアを表示するために /etc/dahdi/modules ファイルを変更するように求めています。/etc/dahdi/modules ファイルを編集し、必要なハードウェアのみをロードしてください。私の場合、Xorcom Astribank 6FXSおよび2FXOを備えたテストマシンを使用していました。ファイルを以下に示します。

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

経験則として、必要な機能を備えたバージョンを使用すべきです。Asteriskは、LTS（長期サポート）と標準リリースを交互に行うリリースモデルに従っています。本書の執筆時点では、**Asterisk 22が現在のLTSリリース**（2024年リリース、2028年までサポート）であり、今選択するのに最適です。Asterisk 20は前回のLTSであり、バージョン16（初版で使用）はサポートが終了しています。本番システムでは、常にLTSリリースを選択してください。

> **[2nd-ed note]** 印刷前に downloads.asterisk.org で正確な現在のポイントリリースを確認してください。執筆時点では22ブランチがアクティブなLTSです。

## Asteriskのコンパイル

以前にソフトウェアをコンパイルしたことがあれば、Asteriskのコンパイルは簡単な作業です。以下のコマンドを実行してAsteriskをコンパイルおよびインストールします。make menuselectを使用して、どのアプリケーションやモジュールをビルドするかを選択できることを忘れないでください。ステップ1：ソースコードをダウンロードします

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

ステップ2：ビルドの前提条件をインストールします（上記の「依存関係のインストール」を参照）

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

ステップ3：ビルドを設定します

```
./configure
```

ステップ4：ビルドするモジュールを選択します

```
make menuselect
```

make menuselectを使用して、必要なモジュールのみをインストールします。Asterisk 22では、SIPチャネルは **chan_pjsip** （デフォルトでビルドされます）です。古い **chan_sip** はAsterisk 21で削除され、存在しません。Opusの *パススルー* はそのまま動作しますが（ツリー内の `res_format_attr_opus` モジュールがSDPネゴシエーションを処理します）、**codec_opus** トランスコーディングモジュールは依然としてSangoma/Digiumの外部クローズドソースバイナリです。menuselectでこれを選択すると、Digiumのサーバーからダウンロードされます。バイナリは無料です。詳細は以下の「menuselectによるモジュールの選択」を参照してください。

ステップ5：Asteriskをビルドしてインストールし、デフォルトの設定ファイルとサンプルファイルを作成します

```
make
make install
make samples
make config
ldconfig
```

`make install` はバイナリとモジュールをインストールし、 `make samples` はサンプル設定ファイルを `/etc/asterisk` に書き込み、 `make config` は検出されたディストリビューション用のSysV init起動スクリプト（例：Debian/Ubuntu上の `/etc/init.d/asterisk`）をインストールし、 `ldconfig` は共有ライブラリキャッシュを更新します。systemdユニットもソースツリーの `contrib/systemd/asterisk.service` に同梱されていますが、 `make config` はそれを自動的にインストールしません。systemd下でAsteriskを実行したい場合は、自分で適切な場所にコピーしてください（下記参照）。

### menuselectによるモジュールの選択

`make menuselect` は、ビルドするアプリケーション、codec、チャネル、リソースを正確に選択できるテキストベースのメニューを開きます。Asterisk 22に固有のいくつかの注意点：

- **chan_pjsip** （*Channel Drivers* 内）は最新のSIPチャネルであり、デフォルトで有効になっています。Asterisk 22における唯一のSIPチャネルです。
- **codec_opus** （*Codec Translators* 内）は **外部** モジュールです（menuselectのエントリには「Download the Opus codec from Digium」と表示されます）。これを有効にすると、 `make` がSangoma/Digiumから無料のクローズドソースバイナリを取得します。Opusパススルー自体には追加モジュールは不要です。Sangomaの **codec_g729** モジュールも利用可能です。バイナリは無料でダウンロードできますが、合法的なG.729トランスコーディングには、チャネルごとのライセンス購入が必要です。
- *Core Sound Packages*、*Music On Hold File Packages*、*Extras Sound Packages* メニューで必要なサウンドフォーマットと言語を選択してください。チェックしたものはすべて、 `make install` の実行中に自動的にダウンロードおよびインストールされます。

選択が完了したら、**Save & Exit** を選択し、 `make` に進みます。

> **[2nd-ed note]** Asterisk 22からキャプチャした新しい `make menuselect` スクリーンショットを挿入してください（初版のスクリーンショットは、現在は存在しないchan_sip/chan_skinny/chan_mgcpを表示していました）。Channel Drivers画面にはchan_pjsipが表示され、chan_sipは表示されないはずです。

## Asteriskの開始と停止

この最小限の設定で、Asteriskを正常に開始できます。学習やデバッグのために、コンソールにアタッチした状態でAsteriskをフォアグラウンドで開始できます：

```
/usr/sbin/asterisk –vvvgc
```

Asteriskをシャットダウンするには、CLIコマンド stop now を使用します。

```
CLI>core stop now
```

### systemdによるAsteriskの開始

最新のLinuxディストリビューション（Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9）では、システムサービスマネージャーは **systemd** です。Asteriskはソースツリーの `contrib/systemd/asterisk.service` にsystemdユニットを同梱しています。これを `/etc/systemd/system/asterisk.service` にコピーし、 `systemctl daemon-reload` を実行してください。インストール後、本番環境でAsteriskを実行する推奨方法は `systemctl` を通すことです：

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Asteriskがサービスとして実行されたら、 `asterisk -r` （接続）または `asterisk -rvvv` （詳細出力付きで接続）を使用してCLIにアタッチします。

> **[2nd-ed note]** 古いシステムでは、AsteriskはレガシーなSysV initスクリプト（ `/etc/init.d/asterisk` ）と、クラッシュ時にAsteriskを自動的に再起動する **safe_asterisk** ラッパーを介して開始されていました。systemdでは、自動再起動はユニットファイルの `Restart=` ディレクティブによって処理されるため、一般的に `safe_asterisk` は不要になりました。レガシーなinit/ `safe_asterisk` アプローチは依然として機能しますが、systemdベースのディストリビューションでは非推奨です。

### Asteriskの実行時オプション

Asteriskの開始プロセスは非常に単純です。パラメーターなしでAsteriskを実行すると、デーモンとして起動します。

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

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others. Usage: asterisk [OPTIONS] Valid Options: -V Display version number and exit -C <configfile> Use an alternate configuration file -G <group> Run as a group other than the caller -U <user> Run as a user other than the caller -c Provide console CLI -d Increase debugging (multiple d's = more debugging) -f Do not fork -F Always fork -g Dump core in case of a crash -h This help screen -i Initialize crypto keys at startup -L <load> Limit the maximum load average before rejecting new calls -M <value> Limit the maximum number of calls to the specified value -m Mute debugging and console output on the console -n Disable console colorization. Can be used only at startup. -p Run as pseudo-realtime thread -q Quiet mode (suppress output) -r Connect to Asterisk on this machine -R Same as -r, except attempt to reconnect if disconnected -s <socket> Connect to Asterisk via socket <socket> (only valid with -r) -t Record soundfiles in /var/tmp and move them where they belong after they are done -T Display the time in [Mmm dd hh:mm:ss] format for each line of output to the CLI. Cannot be used with remote console mode. -v Increase verbosity (multiple v's = more verbose) -x <cmd> Execute command <cmd> (implies -r) -X Enable use of #exec in asterisk.conf -W Adjust terminal colors to compensate for a light background

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

; Some console commands are associated with the logger process.

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

logrotateに関する詳細は以下を使用して取得できます：

```
#man logrotate
```

## Asteriskのアンインストール

Asteriskをアンインストールするには、以下を使用します：

```
make uninstall
```

Asteriskとすべての設定ファイルをアンインストールするには、以下を使用します：

```
make uninstall-all
```

## Asteriskインストールに関する注意点

このセクションでは、Asteriskをインストールする前に対処すべき問題についていくつかのアドバイスを提供します。

### 本番システム

Asteriskを本番環境にインストールする場合は、システム設計に注意を払う必要があります。サーバーは、テレフォニーシステムが他のシステムプロセスよりも優先されるように最適化する必要があります。Asteriskは、X-Windowsのようなプロセッサ集約型のソフトウェアと一緒に実行すべきではありません。CPU集約型のプロセス（巨大なデータベースなど）を実行する必要がある場合は、別のサーバーを使用してください。一般的に言って、Asteriskはハードウェアのパフォーマンス変動の影響を受けやすいです。そのため、CPU使用率が40%を超えないようなハードウェア環境でAsteriskを使用するようにしてください。

### ネットワークのヒント

IP電話を使用する予定がある場合は、ネットワークに注意を払うことが重要です。音声プロトコルは非常に優れており、遅延やジッターにも耐性がありますが、設定が不十分なローカルエリアネットワークを使用すると、音声品質が低下します。優れた音声品質を保証できるのは、スイッチやルーターでQuality of Service（QoS）を使用している場合のみです。ローカルエリアネットワークでの音声は良好な傾向がありますが、LAN環境であっても、衝突が多すぎる10 Mbpsハブを使用していると、最終的には音声が歪んだり、ひどい品質になったりします。最高の音声品質を確保するために、以下の推奨事項に従ってください：

- 可能であれば、または経済的に実現可能であれば、エンドツーエンドのQoSを使用してください。エンドツーエンドのQoSがあれば、音声品質は完璧です。言い訳は無用です！
- 本番環境で音声用に10/100 Mbpsハブを使用することは避けてください。衝突はネットワークにジッターを課す可能性があります。衝突が発生しない全二重の10/100 Mbpsが推奨されます。
- 音声ネットワークの不要なブロードキャストを分離するためにVLANを使用してください。ARPブロードキャストで音声ネットワークが破壊されるような事態は避けたいはずです。
- 音声ネットワークにおける期待値についてユーザーを教育してください。QoSがない場合、ほとんどのケースで音声が完璧になるとは言わないでください。多くの場合、携帯電話と同等の音声品質が達成されます。ファームウェアやハードウェア設計の問題は一般的であるため、高品質な電話機を使用してください。

## まとめ

本章では、最小ハードウェア要件について学び、Asteriskのダウンロード、インストール、コンパイル方法を習得しました。セキュリティ上の理由から、Asteriskはroot以外のユーザーで実行する必要があります。本番環境を開始する前に、ネットワーク環境を確認してください。

## クイズ

1. Asterisk 22において、SIPサポートを提供するチャネルドライバーはどれですか。また、古い `chan_sip` はどうなりましたか？
   - A. `chan_sip` が依然としてデフォルトであり、 `chan_pjsip` はオプションです。
   - B. `chan_pjsip` がデフォルトのSIPチャネルであり、 `chan_sip` はAsterisk 21で削除され、存在しません。
   - C. 両方がデフォルトでビルドされ、実行時に選択します。
   - D. SIPサポートはIAX2のために完全に削除されました。
2. Asterisk用のテレフォニーインターフェースカードには通常、デジタル信号プロセッサ（DSP）が組み込まれているため、PCのCPUをあまり必要としません。
   - A. 正
   - B. 誤
3. 完璧な音声品質が必要な場合は、エンドツーエンドのQuality of Service（QoS）を実装する必要があります。
   - A. 正
   - B. 誤
4. 最新のAsteriskバージョンは最も安定しているため、常に最新バージョンを選択すべきです。
   - A. 正
   - B. 誤
5. Asterisk 22のビルド依存関係をインストールする推奨方法は何ですか？
6. TDMインターフェースカードがない場合でも、Linux上の `res_timing_timerfd` モジュールによって提供される内部タイミングソースがあります。このタイミングは、________ や ________ などのアプリケーションで使用されます。
7. Asteriskをインストールする際、グラフィカルインターフェースはCPUサイクルを消費するため、GNOMEやKDEのようなデスクトップ環境は入れない方が良いです。
   - A. 正
   - B. 誤
8. Asteriskの設定ファイルは ________ ディレクトリにあります。
9. Asteriskのサンプル設定ファイルをインストールするには、________ というコマンドを入力します。
10. Asteriskをroot以外のユーザーとして実行することが重要な理由は何ですか？

**回答:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — 展開したAsteriskソースツリーから `./contrib/scripts/install_prereq install` を実行する · 6 — ConfBridgeおよびMusic on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — セキュリティ（Asteriskが侵害された場合の被害を制限するため）
