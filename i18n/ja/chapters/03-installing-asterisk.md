# Installing Asterisk 22

最初の章では、Asterisk が電話システムでどのように役立つかを少し学びました。この章では、Asterisk のダウンロードとインストール方法を取り上げます。開始する前に、コンパイルとインストールの方法を学んでおくことが重要です。コンパイルプロセスは、従来の Microsoft™ Windows™ ユーザーには奇妙に感じられるかもしれませんが、Linux™ 環境ではかなり一般的です。Asterisk をコンパイルすることで、ハードウェアに最適化されたコードを得ることができ、ここでもそれを行います。Asterisk は複数の OS 上で動作しますが、今回は簡単にするために Linux のみを使用します。**Ubuntu 24.04 LTS** を選んだのは、依存関係のインストールが容易で、安定したサポートが受けられるサーバーディストリビューションであり、フットプリントが小さいためです。他のディストリビューションを好む場合は、パッケージ名を適宜調整してください。

このエディションは **Asterisk 22 LTS**（2024-10-16 リリース；2028-10-16 までフルサポート、2029-10-16 までセキュリティ修正）を対象としています。Asterisk 22 は現在の長期サポートリリースです。なお、Digium は 2018 年に **Sangoma** に買収され、現在は Sangoma が Asterisk をスポンサーしています。この章中の「Digium」という表記は、歴史的なハードウェアに関するレガシーブランドを指します。

## 目的

この章の終わりまでに、次のことができるようになります：

- Asterisk のハードウェア要件を判断する;
- 必要な依存関係を備えた Linux をインストールする;
- HTTPS 経由で安定版をダウンロードする;
- Asterisk をコンパイルする;
- 起動時に Asterisk を開始する方法を学ぶ。

## 必要最低限のハードウェア

Asterisk は多くのハードウェアを必要としませんが、要件に合わせて最適なハードウェアを選ぶためのいくつかのポイントがあります。ハードウェアを選択する際は、次の主要な要素を考慮すべきです。

- 登録ユーザーの総数。1秒あたりにサポートする必要がある登録数を定義します
- 同時通話数の総計。Asteriskサーバーのネットワークアダプタとブリッジで処理する必要があるネットワーク会話の数を定義します
- サポートすべきコーデック。高複雑度のコーデックはサーバーのCPU/FPUリソースを大量に消費します。例として iLBC は、開発元（Global IP Sound）の測定によると、TI C54x DSP 上で30 ms フレームでチャンネルあたり約18 MIPS、20 ms フレームで約15 MIPS です
- エコーキャンセレーション。エコーキャンセルは多くのCPU/FPUを使用する可能性があり、場合によっては電話インターフェースカードのDSPを使用したハードウェアエコーキャンセルを選択すべきです
- 可用性。RAID1 または RAID5 を使用して可用性を向上させます。Asterisk は 24 時間 365 日稼働するアプリケーションであることを忘れないでください

The main component for an Asterisk Server is the network adapter. A good server network adapter is recommended. CPU is important when you need to support high complexity codecs such as g.729 and iLBC and echo cancellation. You may choose to offload this to dedicated DSPs: Sangoma (formerly Digium) provides a DSP card named TC400B capable of supporting 120 G.729 simultaneous calls.

ベストプラクティスは、既知のメーカーから新しいサーバークラスのコンピュータを選択することです。特定のマシンが同時通話数や登録ユーザー数を正確にどれだけサポートできるかを知るには、SIPP（http://sipp.sourceforge.net）などのストレステストツールでハードウェアをテストすべきです。Xorcom（http://www.xorcom.com）などのハードウェアメーカーは、結果をウェブサイトで公開しています。

注: ConfBridge や music on hold などの一部の Asterisk アプリケーションは、内部タイミングソースが必要です。最新の Linux では、組み込みの`res_timing_timerfd`モジュールが自動的に提供されます — 電話ハードウェアは不要です。（古い`dahdi_dummy`ソフトウェアタイマーはもはや存在せず、その機能は DAHDI Linux 2.3.0 のメイン`dahdi`カーネルモジュールに統合されました。）CLI コマンド`timing test`でアクティブなタイマーを確認できます。

### ハードウェア構成

The Asterisk hardware does not need to be sophisticated. You don't need an expensive video card or numerous peripherals. Some tips about hardware configuration:

- 未使用のUSB、シリアル、パラレルポートを無効にし、不要な割り込みの消費を防ぎます。  
- 堅牢なネットワークインターフェースカードは必須です。  
- 電話インターフェースカードを使用する場合は特に注意してください。カードの中には 3.3 ボルト PCI バスを使用するものがあり、対応するマザーボードを見つけるのは容易ではありません。現在では PCI Express がより入手しやすくなっています。  
- ハードディスクには細心の注意を払ってください。PBX は 24x7 体制で稼働するのに対し、デスクトップは 8x5 で動作します。デスクトップ用ハードウェアを PBX に使用しないでください。通常、ハードディスクは 1 年も経たずに故障します。私の推奨は、サーバーマシンまたは 24x7 アプリケーション向けに設計されたアプライアンスを使用することです。

### IRQ 共有（レガシー PCI カードのみ）

この注意点は、物理的な PCI/PCI-Express 電話カード（DAHDI ハードウェア）をインストールした場合に**のみ**適用されます。このようなカードは大量の割り込みを生成し、古いシングル CPU システムでは、別のデバイスと IRQ ラインを共有するとドライバが飢餓状態になり、音声品質が低下する可能性があります。電話カードを使用する場合は、マシンを Asterisk 専用にし、BIOS で未使用のオンボードデバイスを無効化し、`cat /proc/interrupts`で割り当てられた割り込みを確認してください。MSI/MSI‑X 割り込みを使用する最新のマルチコアサーバーでは、実際には IRQ 共有は問題にならず、カードを使用しない純粋な VoIP 展開では全く心配する必要はありません。

## Choosing a Linux distribution

Asterisk は当初 Linux 上で動作するように開発されました。しかし、BSD Unix や macOS 上でも動作します。Asterisk が初めての方は、はるかに簡単な Linux をまず使ってみてください。Asterisk は公式に RHEL 系（CentOS/RHEL/Fedora）、Ubuntu、Debian を対象としています。現在実用的な選択肢は **Debian 12**、**Ubuntu 22.04 LTS / 24.04 LTS**、そして **Rocky Linux 9 / AlmaLinux 9** です — CentOS Linux はサポートが終了しているため、RHEL 系システムでは Rocky または AlmaLinux を選んでください。本書では Ubuntu 24.04 LTS を使用します。下記の公式リリースディレクトリから最新の 24.04 ポイントリリースサーバーイメージをダウンロードしてください（正確なファイル名には現在のポイントリリースが含まれます、例: `ubuntu-24.04.4-live-server-amd64.iso`）：

```
https://releases.ubuntu.com/24.04/
```

### Preparing Linux for Asterisk

Asterisk をコンパイルする前に、ビルド用パッケージがインストールされた動作する Linux システムが必要です。**Ubuntu 24.04 LTS Server** を仮想マシンまたは専用マシンにインストールしてください（64 ビットイメージを使用します。本書のすべては 64 ビットですが、Asterisk 自体はまだ 32 ビット x86 もサポートしています）。このトレーニングでは VirtualBox を使用しました；イメージは <https://releases.ubuntu.com/24.04> からダウンロードできます。Linux のインストール自体は本書の範囲外です — 基本的な Linux 知識が前提条件となります。Linux をインストールしたら、Asterisk のビルド依存関係を追加（*Installing dependencies* を参照）し、続いて Asterisk をコンパイルします。

## Installing Linux for Asterisk

Linux を通常通りインストールし、グラフィカルデスクトップは入れません。インストール中にメール転送エージェントも有効にしてください（**exim4** を使用します）— 本書の後半でボイスメールからメールへの通知を送信する際に Asterisk が必要とします。**注意:** オペレーティングシステムをインストールすると対象ディスクが消去されます。物理ハードウェアにインストールする場合は、まずデータをバックアップしてください。仮想マシンにインストールすればホストはそのままです。Ubuntu Server ISO（または VM の仮想光学ドライブ）からインストーラを起動し、プロンプトに答えていきます — 大半はわかりやすいです。

## Installing dependencies

Asterisk と DAHDI をインストールするには、多くのソフトウェア依存関係をインストールする必要があります。Asterisk 22 では、ソースツリーに同梱されているスクリプトを使用することが推奨されており、このスクリプトは各サポートディストリビューションに対する正しいパッケージ名を把握しています。Asterisk ソースをダウンロードして展開した後（「Compiling Asterisk」参照）、次を実行します：

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. root としてログインする（または `sudo` を使用）。
2. Debian/Ubuntu システムで依存関係を手動でインストールしたい場合、同等のパッケージ一覧は次のとおりです：

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

Asterisk のソースは現在 Git でホストされているため、`subversion` は不要になり、最新の Debian/Ubuntu はバージョン付きの `libncurses5-dev` ではなく `libncurses-dev` を提供しています。スクリプトは常にディストリビューションに適した正しいパッケージ名を追跡するため、手作業で管理したリストよりも `./contrib/scripts/install_prereq install` を優先してください。

### DAHDI

DAHDI（Digium/Sangoma Asterisk Hardware Device Interface）は、アナログおよびデジタルカード用ドライバのアーキテクチャです。Asterisk をインストールする前に、アナログまたはデジタルインターフェースを使用する予定がある場合は DAHDI をインストールすることが重要です。DAHDI はアナログ/デジタル電話カード向けにまだ存在しますが、徐々にニッチになっており、ほとんどの最新導入は純粋な VoIP であり、このセクションを完全にスキップできます。物理的な電話インターフェースハードウェアがある場合にのみ DAHDI をインストールしてください。ソースファイルは次のコマンドで取得します：

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

ファイルを解凍するには次を実行します：

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

DAHDI モジュールをコンパイルする必要があります。`./configure` と `make menuselect` コマンドは数年前に導入されました。後者は、ビルドするユーティリティとモジュールを選択できるようにします。以下のコマンドで実行できます：

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

`make install-config` DAHDI が設定されました。DAHDI ハードウェアがある場合、システムにインストールされている DAHDI ハードウェアのみをロードするように `/etc/dahdi/modules` を編集することが推奨されます。デフォルトでは、DAHDI 起動時にすべての DAHDI ハードウェアのサポートがロードされます。現在のシステムにある DAHDI ハードウェアは次のとおりです: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware。この画面（上）は、特定の構成に必要なドライバのみをロードするように `/etc/dahdi/modules` を変更し、検出されたハードウェアを表示するよう求めています。`/etc/dahdi/modules` を編集し、必要なハードウェアだけをロードしてください。私の場合、Xorcom Astribank 6FXS と 2FXO を搭載したテストマシンを使用していました。ファイルは以下に示します。

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

コンピュータを再起動し、ドライバが正しくロードされていることを確認してください。

## Which version to choose

原則として、必要な機能が含まれるバージョンを使用すべきです。Asterisk は LTS（長期サポート）版と標準版を交互にリリースするモデルを採用しています。本書執筆時点では、**Asterisk 22 が現在の LTS リリース**（2024年10月リリース；最新のポイントリリースは 22.10.0）であり、今選ぶべき最適なバージョンです。Asterisk 20 は前回の LTS、バージョン 16（第1版で使用）はサポート終了となっています。運用環境では、常に LTS リリースを選択してください。

## Compiling Asterisk

If you have previously compiled software, compiling Asterisk will be an easy task. Run the following commands to compile and install Asterisk. Remember, you can choose which applications and modules to build using make menuselect. Step 1: Download the source code

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Step 2: Install the build prerequisites (see "Installing dependencies" above)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Step 3: Configure the build

```
./configure
```

Step 4: Select the modules to build

```
make menuselect
```

Use make menuselect to install only the necessary modules. In Asterisk 22 the SIP channel is **chan_pjsip** (built by default); the old **chan_sip** was removed in Asterisk 21 and no longer exists. Opus *pass-through* works out of the box (the in-tree `res_format_attr_opus` module handles SDP negotiation), but the **codec_opus** transcoding module is still an external, closed-source binary from Sangoma/Digium — selecting it in menuselect downloads it from Digium's servers. The binary is free of charge. See "Selecting modules with menuselect" below for details.

Step 5: Build and install Asterisk, then create the default config and sample files

```
make
make install
make samples
make config
ldconfig
```

`make install` installs the binaries and modules, `make samples` writes the sample configuration files into `/etc/asterisk`, `make config` installs the SysV init startup script for your detected distribution (e.g. `/etc/init.d/asterisk` on Debian/Ubuntu), and `ldconfig` refreshes the shared-library cache. A systemd unit also ships in the source tree at `contrib/systemd/asterisk.service`, but `make config` does not install it automatically — copy it into place yourself if you prefer to run Asterisk under systemd (see below).

### Selecting modules with menuselect

`make menuselect` opens a text-based menu where you choose exactly which applications, codecs, channels, and resources to build. A few notes specific to Asterisk 22:

- **chan_pjsip** (under *Channel Drivers*) is the modern SIP channel and is enabled by default; it is the only SIP channel in Asterisk 22.
- **codec_opus** (under *Codec Translators*) is an **external** module (its menuselect entry reads "Download the Opus codec from Digium"); enabling it makes `make` fetch the free, closed-source binary from Sangoma/Digium. Opus pass-through itself needs no extra module. Sangoma's **codec_g729** module is also available — the binary is free to download, but lawful G.729 transcoding requires a purchased per-channel license.
- Select the sound formats and languages you want in the *Core Sound Packages*, *Music On Hold File Packages*, and *Extras Sound Packages* menus; anything you check there is downloaded and installed automatically during `make install`.

After making your selections, choose **Save & Exit** and continue with `make`.

## Starting and stopping Asterisk

この最小構成で、Asterisk を正常に起動することができます。学習やデバッグのために、コンソールにアタッチした状態でフォアグラウンドで Asterisk を起動できます:

```
/usr/sbin/asterisk -vvvgc
```

CLI コマンド `core stop now` を使用して Asterisk をシャットダウンします:

```
*CLI> core stop now
```

### Starting Asterisk with systemd

最新の Linux ディストリビューション（Debian 12、Ubuntu 22.04/24.04、Rocky/AlmaLinux 9）では、システムサービスマネージャは **systemd** です。Asterisk はソースツリーの `contrib/systemd/asterisk.service` に systemd ユニットを同梱しています。これを `/etc/systemd/system/asterisk.service` にコピーし、`systemctl daemon-reload` を実行します。インストールが完了したら、本番環境で Asterisk を実行する推奨方法は `systemctl` を通すことです:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Asterisk がサービスとして実行されている場合、`asterisk -r`（接続）または `asterisk -rvvv`（冗長出力付きで接続）で CLI にアタッチできます。

古いシステムでは、レガシーな SysV init スクリプト（`/etc/init.d/asterisk`）と **safe_asterisk** ラッパーを使用して Asterisk を起動していました。このラッパーはクラッシュ時に自動的に Asterisk を再起動していました。systemd では、ユニットファイルの `Restart=` ディレクティブが自動再起動を処理するため、`safe_asterisk` は通常不要です。レガシーな init/`safe_asterisk` アプローチはまだ機能しますが、systemd ベースのディストリビューションでは非推奨となっています。

### Asterisk runtime options

Asterisk の起動プロセスは非常にシンプルです。パラメータなしで Asterisk を実行すると、デーモンとして起動します。

```
/sbin/asterisk
```

以下のコマンドを実行すると、Asterisk コンソールにアクセスできます。複数のコンソールプロセスを同時に実行できることに注意してください。

```
/sbin/asterisk -r
```

### Available runtime options for Asterisk

`asterisk -h` を使用して、利用可能なランタイムオプションを表示できます。

```text
sipast:/usr/src/asterisk-22.x.y# asterisk -h
Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others.
Usage: asterisk [OPTIONS]
Valid Options:
   -V              Display version number and exit
   -C <configfile> Use an alternate configuration file
   -G <group>      Run as a group other than the caller
   -U <user>       Run as a user other than the caller
   -c              Provide console CLI
   -d              Increase debugging (multiple d's = more debugging)
   -f              Do not fork
   -F              Always fork
   -g              Dump core in case of a crash
   -h              This help screen
   -i              Initialize crypto keys at startup
   -L <load>       Limit the maximum load average before rejecting new calls
   -M <value>      Limit the maximum number of calls to the specified value
   -m              Mute debugging and console output on the console
   -n              Disable console colorization. Can be used only at startup.
   -p              Run as pseudo-realtime thread
   -q              Quiet mode (suppress output)
   -r              Connect to Asterisk on this machine
   -R              Same as -r, except attempt to reconnect if disconnected
   -s <socket>     Connect to Asterisk via socket <socket> (only valid with -r)
   -t              Record soundfiles in /var/tmp and move them where they
                   belong after they are done
   -T              Display the time in [Mmm dd hh:mm:ss] format for each line
                   of output to the CLI. Cannot be used with remote console mode.
   -v              Increase verbosity (multiple v's = more verbose)
   -x <cmd>        Execute command <cmd> (implies -r)
   -X              Enable use of #exec in asterisk.conf
   -W              Adjust terminal colors to compensate for a light background
```

## インストールディレクトリ

Asterisk は複数のディレクトリにインストールされますが、これらは asterisk.conf ファイルで変更できます。トレーニング目的であれば verbose を 3 から 15 に変更し、本番環境では 3 のままにしてください。オプション `maxcalls` と `maxload` は、システムが過負荷になるのを防ぐための有効な設定です。

### asterisk.conf（抜粋）

`[directories]`セクションは、Asterisk が設定ファイル、モジュール、データ、スプール、ログを保持する場所を定義します。

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
```

`[options]`セクションは実行時のチューニングを保持します。以下に示すのが最も有用なオプションです（有効にするにはコメントを外してください）。このファイルにはさらに多くのオプションが含まれており、すべてインラインコメントで説明されています。

```
[options]
;verbose = 3      ; Console verbosity (raise to 15 for training, keep 3 in production)
;debug = 3        ; Debug level
;maxcalls = 10    ; Maximum number of simultaneous calls allowed
;maxload = 0.9    ; Stop accepting new calls when load average exceeds this
;maxfiles = 1000  ; Maximum number of open files
;runuser = asterisk   ; The user to run as
;rungroup = asterisk  ; The group to run as
```

## ログファイルとログローテーション

Asterisk PBX はメッセージを `/var/log/asterisk` に記録します。ロギングは `logger.conf` で制御されます。重要な部分は `[logfiles]` セクションで、各行がログチャンネルと取得するメッセージレベルを定義しています（抜粋）：

```ini
; logger.conf (excerpt)
[general]
;dateformat = %F %T.%3q          ; ISO 8601 timestamps, with milliseconds

[logfiles]
; <logger_name> => [formatter]<levels>
console  => notice,warning,error
messages => notice,warning,error
full     => notice,warning,error,verbose,dtmf,fax
security => security              ; PJSIP/auth security events (used by Fail2Ban)
```

編集後は `logger reload` で変更を適用し、`logger show channels` でチャンネルを確認します：

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

ログファイルはすぐに大きくなる可能性があるため、システムの `logrotate` デーモンでローテーションします — `/etc/logrotate.d/` にファイルを追加してください：

```text
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

logrotate に関する詳細情報は次のコマンドで取得できます：

```
#man logrotate
```

## Asterisk のアンインストール

Asterisk をアンインストールするには、次を使用します:

```
make uninstall
```

Asterisk とすべての設定ファイルをアンインストールするには、次を使用します:

```
make uninstall-all
```

## Asterisk インストール時の注意事項

このセクションでは、Asterisk をインストールする前に対処すべき問題についていくつかの助言を提供します。

### 本番システム

Asterisk を本番環境にインストールする場合は、システム設計に注意を払う必要があります。サーバは、テレフォニーシステムが他のシステムプロセスよりも優先されるように最適化しなければなりません。Asterisk を X‑Windows などの CPU 集中型ソフトウェアと同時に実行すべきではありません。CPU 集中型プロセス（例：巨大なデータベース）を実行する必要がある場合は、別のサーバを使用してください。一般的に、Asterisk はハードウェア性能の変動に影響を受けやすいです。したがって、CPU 使用率が 40% を超えないハードウェア環境で Asterisk を使用することを検討してください。

### ネットワークのヒント

IP 電話を使用する予定がある場合は、ネットワークに注意を払うことが重要です。音声プロトコルは遅延やジッターに対して非常に強固ですが、設定が不十分なローカルエリアネットワークを使用すると音声品質が低下します。スイッチやルータで QoS（Quality of Service）を導入しなければ、良好な音声品質を保証することはできません。LAN 内の音声は概ね良好ですが、10 Mbps ハブで衝突が多発すると、音声が歪んだり粗くなったりします。以下の推奨事項に従って、可能な限り最高の音声品質を確保してください。

- 可能であれば、または経済的に実現可能であればエンドツーエンド QoS を使用してください。エンドツーエンド QoS があれば音声品質は完璧です。言い訳は無用です！
- 本番環境で音声に 10/100 Mbps ハブの使用は避けてください。衝突はネットワークにジッターをもたらします。衝突が発生しないフルデュプレックス 10/100 Mbps が推奨されます。
- VLAN を使用して音声ネットワークの不要なブロードキャストを分離してください。ARP ブロードキャストでウイルスが音声ネットワークを破壊するような事態は避けたいものです。
- ユーザーに音声ネットワークでの期待値を教育してください。QoS がない場合、音声が常に完璧になるとは言わないでください。多くの場合、携帯電話と同程度の音声品質が得られます。ファームウェアやハードウェア設計に問題があることが多いため、品質の高い電話機を使用してください。

## 概要

この章では、最低ハードウェア要件と Asterisk のダウンロード、インストール、コンパイル方法について学びました。セキュリティ上の理由から、Asterisk は非 root ユーザーで実行すべきです。本番環境を開始する前に、ネットワーク環境を確認してください。

## Quiz

1. Asterisk 22 で、どのチャネルドライバが SIP サポートを提供し、古い`chan_sip`はどうなりましたか？
   - A. `chan_sip`はまだデフォルトです；`chan_pjsip`はオプションです。
   - B. `chan_pjsip`がデフォルトの SIP チャネルです；`chan_sip`は Asterisk 21 で削除され、もはや存在しません。
   - C. 両方ともデフォルトでビルドされ、実行時に選択します。
   - D. SIP サポートは完全に削除され、IAX2 に置き換えられました。
2. Asterisk 用のテレフォニーインターフェースカードは通常、デジタルシグナルプロセッサ (DSP) を内蔵しているため、PC の CPU をあまり使用しません。
   - A. True
   - B. False
3. 完璧な音声品質を得るには、エンドツーエンドのサービス品質 (QoS) を実装する必要があります。
   - A. True
   - B. False
4. 常に最新の Asterisk バージョンを選択すべきです。最も安定しているからです。
   - A. True
   - B. False
5. Asterisk 22 のビルド依存関係をインストールする推奨方法は何ですか？
6. TDM インターフェースカードがなくても、Linux の`res_timing_timerfd`モジュールが提供する内部タイミングソースがあります。このタイミングは ________ や ________ などのアプリケーションで使用されます。
7. Asterisk をインストールする際は、GNOME や KDE などのデスクトップ環境を省いた方が良いです。グラフィカルインターフェースは CPU サイクルを消費するためです。
   - A. True
   - B. False
8. Asterisk の設定ファイルは ________ ディレクトリにあります。
9. Asterisk のサンプル設定ファイルをインストールするには、次のコマンドを入力します： ________
10. Asterisk を非 root ユーザーとして実行することが重要なのはなぜですか？

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
