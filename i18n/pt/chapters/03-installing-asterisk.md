# Instalando Asterisk 22

No primeiro capítulo, aprendemos um pouco sobre como o Asterisk é útil no ambiente de telefonia. Neste capítulo, abordaremos como baixar e instalar o Asterisk. Antes de começar, é essencial aprender como compilá‑lo e instalá‑lo. O processo de compilação pode parecer estranho para usuários tradicionais do Microsoft™ Windows™, mas é bastante comum no ambiente Linux™. É possível obter um código otimizado para o seu hardware ao compilar o Asterisk, que é o que faremos aqui. O Asterisk roda em vários sistemas operacionais, mas manteremos as coisas simples e usaremos apenas um: Linux. Usamos **Ubuntu 24.04 LTS** porque suas dependências são fáceis de instalar e ele é uma distribuição de servidor estável, bem‑suportada e com baixa pegada. Se você preferir outra distribuição, ajuste os nomes dos pacotes de acordo.

Esta edição tem como alvo **Asterisk 22 LTS** (lançado em 2024-10-16; suporte total até 2028-10-16, correções de segurança até 2029-10-16). O Asterisk 22 é a versão atual de suporte de longo prazo. Observe que a Digium foi adquirida pela **Sangoma** em 2018, e o Asterisk agora é patrocinado pela Sangoma — referências a "Digium" ao longo deste capítulo referem‑se à marca legada para hardware histórico.

## Objetivos

Ao final deste capítulo você deverá ser capaz de:

- Determinar os requisitos de hardware para o Asterisk;
- Instalar o Linux com as dependências necessárias;
- Baixar uma versão estável via HTTPS;
- Compilar o Asterisk; e
- Aprender como iniciar o Asterisk na inicialização.

## Minimum Hardware Required

Asterisk não precisa de muito hardware para rodar, porém há algumas dicas para escolher o melhor hardware para suas necessidades. Você deve levar em consideração os seguintes fatores principais ao escolher seu hardware:

- Número total de usuários registrados. Defina quantas inscrições por segundo você precisa suportar
- Número total de chamadas simultâneas. Defina quantas conversas de rede você precisa processar no adaptador de rede e na ponte no servidor Asterisk
- Quais codecs você precisa suportar. Codecs de alta complexidade exigirão muito poder de CPU/FPU no seu servidor; iLBC, por exemplo, foi medido por seu criador (Global IP Sound) em aproximadamente 18 MIPS por canal para quadros de 30 ms (e cerca de 15 MIPS para quadros de 20 ms) em um DSP TI C54x
- Cancelamento de eco. O cancelamento de eco pode consumir muita CPU/FPU; em alguns casos você deve escolher cancelamento de eco em hardware usando DSPs na placa de interface telefônica
- Disponibilidade. Use RAID1 ou 5 para aumentar a disponibilidade. Lembre‑se, Asterisk é uma aplicação 24x7.

O componente principal de um servidor Asterisk é o adaptador de rede. Recomenda‑se um adaptador de rede de servidor de boa qualidade. A CPU é importante quando você precisa suportar codecs de alta complexidade como g.729 e iLBC e cancelamento de eco. Você pode optar por descarregar isso para DSPs dedicados: Sangoma (antiga Digium) fornece uma placa DSP chamada TC400B capaz de suportar 120 chamadas simultâneas G.729.

A prática recomendada é escolher um computador novo, de classe servidor, de um fabricante conhecido. Para saber exatamente quantas chamadas simultâneas ou quantos usuários registrados uma máquina específica pode suportar, você deve testar esse hardware com uma ferramenta de teste de estresse como SIPP (http://sipp.sourceforge.net). Alguns fabricantes de hardware, como Xorcom (http://www.xorcom.com), publicam seus resultados no site.

Nota: Algumas aplicações Asterisk, como ConfBridge e música em espera, precisam de uma fonte de temporização interna. Em Linux moderno isso é fornecido automaticamente pelo módulo built‑in `res_timing_timerfd` — nenhum hardware telefônico é necessário. (O antigo timer de software `dahdi_dummy` não existe mais; sua funcionalidade foi incorporada ao módulo kernel principal `dahdi` no DAHDI Linux 2.3.0.) Você pode confirmar o timer ativo com o comando CLI `timing test`.

### Hardware configuration

O hardware do Asterisk não precisa ser sofisticado. Você não precisa de uma placa de vídeo cara ou de inúmeros periféricos. Algumas dicas sobre configuração de hardware:

- Desative portas USB, seriais e paralelas não usadas para evitar o consumo de interrupções desnecessárias.
- Uma placa de interface de rede robusta é essencial.
- Tenha cuidado especial se estiver usando placas de interface telefônica. Algumas placas usam barramento PCI de 3,3 volts, e não é fácil encontrar placas‑mãe para elas. Hoje em dia, PCI Express é mais facilmente encontrado.
- Preste muita atenção ao disco rígido; PBX costuma operar em regime 24x7 enquanto desktops funcionam 8x5. Não use hardware de desktop para uma PBX, geralmente o disco falha antes do primeiro ano. Minha recomendação é usar uma máquina servidor ou um appliance projetado para rodar aplicações 24x7.

### IRQ sharing (legacy PCI cards only)

Esta preocupação se aplica **apenas** se você instalar placas telefônicas físicas PCI/PCI‑Express (hardware DAHDI). Essas placas geram grande número de interrupções e, em sistemas antigos de CPU única, compartilhar uma linha IRQ com outro dispositivo pode privar o driver e degradar a qualidade de voz. Se você usar placas telefônicas, dedique a máquina ao Asterisk, desative quaisquer dispositivos integrados não usados na BIOS e verifique as interrupções atribuídas com `cat /proc/interrupts`. Servidores modernos multi‑core que utilizam interrupções MSI/MSI‑X tornam o compartilhamento de IRQ uma questão inexistente na prática, e uma implantação puramente VoIP (sem placas) não precisa se preocupar com isso.

## Choosing a Linux distribution

Asterisk was initially developed to run on Linux. However, it can also run on BSD Unix or macOS. If you are new to Asterisk, try using Linux first since it is much easier. Asterisk officially targets the RHEL family (CentOS/RHEL/Fedora), Ubuntu, and Debian. Good practical choices today are **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS**, and **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux is end-of-life, so prefer Rocky or AlmaLinux on RHEL-family systems. For this book I will use Ubuntu 24.04 LTS. Download the latest 24.04 point-release server image from the official releases directory below (the exact filename includes the current point release, e.g. `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparing Linux for Asterisk

Before compiling Asterisk you need a working Linux system with the build packages installed. Install **Ubuntu 24.04 LTS Server** in a virtual machine or on a dedicated box (use the 64-bit image; everything in this book is 64-bit, though Asterisk itself still supports 32-bit x86). We used VirtualBox for this training; you can download the image from <https://releases.ubuntu.com/24.04>. Installing Linux itself is out of the scope of this book — basic Linux knowledge is a prerequisite. With Linux installed, you will add the Asterisk build dependencies (see *Installing dependencies* below) and then compile Asterisk.

## Instalando Linux para Asterisk

Instale o Linux como de costume, sem ambiente gráfico. Durante a instalação, habilite também um agente de transferência de e‑mail (usamos **exim4**) — o Asterisk precisará dele para enviar notificações de correio de voz para e‑mail mais adiante neste livro. **Cuidado:** instalar um sistema operacional apaga o disco de destino. Se você instalar em hardware físico, faça backup dos seus dados primeiro; instalar em uma máquina virtual deixa o host intacto. Inicialize o instalador a partir do ISO do Ubuntu Server (ou da unidade óptica virtual da VM) e responda às solicitações — a maioria é direta.

## Instalando dependências

Para instalar o Asterisk e o DAHDI você precisa instalar muitas dependências de software. A forma recomendada de fazer isso no Asterisk 22 é usar o script que acompanha a árvore de código-fonte, que conhece os nomes corretos dos pacotes para cada distribuição suportada. Depois de baixar e extrair o código‑fonte do Asterisk (veja “Compilando o Asterisk” abaixo), execute:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. Faça login como root (ou use `sudo`).
2. Se preferir instalar as dependências manualmente em um sistema Debian/Ubuntu, a lista equivalente de pacotes é:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

Observe que o código‑fonte do Asterisk agora está hospedado no Git, portanto `subversion` não é mais necessário, e as versões modernas do Debian/Ubuntu fornecem `libncurses-dev` em vez do `libncurses5-dev` versionado. Prefira `./contrib/scripts/install_prereq install` a uma lista mantida manualmente, já que o script sempre acompanha os nomes corretos dos pacotes para sua distribuição.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) é a arquitetura de drivers para placas analógicas e digitais. Antes de instalar o Asterisk é importante instalar o DAHDI se você planeja usar interfaces analógicas ou digitais. O DAHDI ainda existe para placas de telefonia analógica/digital, mas está se tornando cada vez mais nicho — a maioria das implantações modernas é puramente VoIP e pode pular esta seção completamente. Instale o DAHDI somente se você possuir hardware de interface telefônica física. Obtenha os arquivos‑fonte usando:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Descompacte os arquivos usando:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compilando drivers DAHDI

Você precisará compilar os módulos DAHDI. Os comandos ./configure e make menuselect foram introduzidos há vários anos. Este último permite que você selecione quais utilitários e módulos serão construídos. Os comandos a seguir farão isso:

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

make install-config DAHDI foi configurado. Se você tem algum hardware DAHDI, agora é recomendado editar /etc/dahdi/modules para carregar suporte apenas para o hardware DAHDI instalado neste sistema. Por padrão, o suporte a todo o hardware DAHDI é carregado na inicialização do DAHDI. Eu acredito que o hardware DAHDI que você tem no seu sistema é: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware. Esta tela (acima) pede que você altere o arquivo /etc/dahdi/modules para carregar apenas os drivers necessários para sua configuração específica e exiba o hardware detectado. Edite o arquivo /etc/dahdi/modules e carregue apenas o hardware necessário. No meu caso, eu estava usando uma máquina de teste com um Xorcom Astribank 6FXS e 2FXO. O arquivo é mostrado abaixo.

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

Reinicialize seu computador e verifique o carregamento correto dos drivers.

## Qual versão escolher

Como regra geral, você deve usar a versão que contém os recursos necessários. O Asterisk segue um modelo de lançamentos alternando entre LTS (suporte de longo prazo) e versões padrão. No momento desta edição, **Asterisk 22 é a versão LTS atual** (lançada em outubro de 2024; a última versão pontual é 22.10.0), o que a torna a melhor escolha agora. O Asterisk 20 é a LTS anterior, e a versão 16 (usada na primeira edição) está em fim de vida. Para sistemas de produção, sempre escolha uma versão LTS.

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

## Iniciando e parando o Asterisk

Com esta configuração mínima, é possível iniciar o Asterisk com sucesso. Para aprendizado e depuração, você pode iniciar o Asterisk em primeiro plano conectado ao console:

```
/usr/sbin/asterisk -vvvgc
```

Use o comando CLI `core stop now` para desligar o Asterisk:

```
*CLI> core stop now
```

### Iniciando o Asterisk com systemd

Em distribuições Linux modernas (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), o gerenciador de serviços do sistema é o **systemd**. O Asterisk inclui uma unidade systemd em `contrib/systemd/asterisk.service` na árvore de código; copie-a para `/etc/systemd/system/asterisk.service` e execute `systemctl daemon-reload`. Uma vez instalado, a forma recomendada de executar o Asterisk em produção é através do `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Depois que o Asterisk estiver rodando como serviço, conecte‑se ao seu CLI com `asterisk -r` (connect) ou `asterisk -rvvv` (connect with verbose output).

Em sistemas mais antigos o Asterisk era iniciado via o script legacy SysV init (`/etc/init.d/asterisk`) e o wrapper **safe_asterisk**, que reiniciava o Asterisk automaticamente se ele travasse. Com o systemd, a reinicialização automática é tratada pela diretiva `Restart=` do arquivo de unidade, portanto `safe_asterisk` geralmente não é mais necessária. A abordagem legacy init/`safe_asterisk` ainda funciona, mas está obsoleta em distribuições baseadas em systemd.

### Opções de tempo de execução do Asterisk

O processo de inicialização do Asterisk é muito simples. Se o Asterisk for executado sem nenhum parâmetro, ele será iniciado como daemon.

```
/sbin/asterisk
```

Você pode acessar o console do Asterisk executando o comando a seguir. Observe que mais de um processo de console pode ser executado ao mesmo tempo.

```
/sbin/asterisk -r
```

### Opções de tempo de execução disponíveis para o Asterisk

Você pode exibir as opções de tempo de execução disponíveis usando `asterisk -h`

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

## Diretórios de instalação

Asterisk é instalado em vários diretórios, que podem ser modificados no arquivo asterisk.conf. Para fins de treinamento eu mudaria o verbose de 3 para 15; para produção mantenha em 3. As opções `maxcalls` e `maxload` são boas opções para proteger seu sistema de sobrecarga.

### asterisk.conf (trecho)

A seção `[directories]` define onde o Asterisk mantém sua configuração, módulos, dados, spool e logs:

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

A seção `[options]` contém ajustes de tempo de execução. As opções mais úteis a conhecer são mostradas abaixo (descomente para habilitar); o arquivo vem com muitas outras, cada uma documentada por um comentário inline:

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

## Arquivos de log e rotação de logs

O PBX Asterisk registra suas mensagens em `/var/log/asterisk`. O registro é controlado por `logger.conf`. A parte crucial é a seção `[logfiles]`, onde cada linha define um canal de log e os níveis de mensagem que ele captura (trecho):

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

Depois de editar, aplique a alteração com `logger reload` e confirme os canais com `logger show channels`:

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

Os arquivos de log podem crescer rapidamente, portanto rotacione‑os com o daemon do sistema `logrotate` — adicione um arquivo em `/etc/logrotate.d/`:

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

Mais informações sobre o logrotate podem ser obtidas usando:

```
#man logrotate
```

## Desinstalando Asterisk

Para desinstalar o Asterisk, use:

```
make uninstall
```

Para desinstalar o Asterisk e todos os arquivos de configuração, use:

```
make uninstall-all
```

## Notas de instalação do Asterisk

Esta seção fornecerá alguns conselhos sobre questões a serem resolvidas antes de instalar o Asterisk.

### Sistemas de produção

Se o Asterisk for instalado em um ambiente de produção, você deve prestar atenção ao design do sistema. Um servidor precisa ser otimizado de modo que os sistemas de telefonia tenham prioridade sobre outros processos do sistema. O Asterisk não deve ser executado junto com softwares que consomem muito processador, como X-Windows. Se for necessário executar processos intensivos em CPU (por exemplo, um banco de dados enorme), use um servidor separado. De modo geral, o Asterisk é sensível a variações de desempenho de hardware. Portanto, tente usar o Asterisk em um ambiente de hardware que não exija mais de 40 % de utilização da CPU.

### Dicas de rede

Se você planeja usar telefones IP, é importante prestar atenção à sua rede. Os protocolos de voz são muito bons e resistentes à latência e até a jitter; porém, se você usar uma rede local mal configurada, a qualidade da voz sofrerá. Só é possível garantir boa qualidade de voz usando qualidade de serviço (QoS) em switches e roteadores. A voz em uma rede local tende a ser boa, mas mesmo em um ambiente LAN, se você tiver hubs de 10 Mbps com muitas colisões, acabará tendo voz distorcida ou de baixa qualidade. Siga estas recomendações para garantir a melhor qualidade de voz possível:

- Use QoS de ponta a ponta, se possível ou economicamente viável. Com QoS de ponta a ponta, a qualidade da voz é perfeita. Sem desculpas!
- Evite usar hubs de 10/100 Mbps para voz em um ambiente de produção. Colisões podem impor jitter na rede. Full‑duplex 10/100 Mbps são preferidos porque não ocorrem colisões.
- Use VLANs para separar transmissões desnecessárias da rede de voz. Você não quer um vírus destruindo sua rede de voz com transmissões ARP.
- Eduque os usuários sobre as expectativas em uma rede de voz. Sem QoS, não afirme que a voz será perfeita, pois na maioria dos casos não será. Uma qualidade de voz semelhante à de um telefone móvel será alcançada na maioria das vezes. Use telefones de qualidade, pois problemas com firmware e design de hardware são comuns.

## Resumo

Neste capítulo, você aprendeu sobre os requisitos mínimos de hardware, bem como como baixar, instalar e compilar o Asterisk. O Asterisk deve ser executado com um usuário não root por razões de segurança. Você deve verificar seu ambiente de rede antes de iniciar o ambiente de produção.

## Quiz

1. No Asterisk 22, qual driver de canal fornece suporte a SIP, e o que aconteceu com o antigo `chan_sip`?
   - A. `chan_sip` ainda é o padrão; `chan_pjsip` é opcional.
   - B. `chan_pjsip` é o canal SIP padrão; `chan_sip` foi removido no Asterisk 21 e não existe mais.
   - C. Ambos são compilados por padrão e você escolhe entre eles em tempo de execução.
   - D. O suporte a SIP foi removido completamente em favor do IAX2.
2. As placas de interface telefônica para Asterisk geralmente têm Processadores de Sinal Digital (DSPs) integrados e, portanto, não precisam de muita CPU do PC.
   - A. Verdadeiro
   - B. Falso
3. Se você quer qualidade de voz perfeita, precisa implementar qualidade de serviço de ponta a ponta (QoS).
   - A. Verdadeiro
   - B. Falso
4. Você deve sempre escolher a versão mais recente do Asterisk, pois ela é a mais estável.
   - A. Verdadeiro
   - B. Falso
5. Qual é a forma recomendada de instalar as dependências de compilação para o Asterisk 22?
6. Se você não tem uma placa de interface TDM, ainda terá uma fonte de temporização interna para sincronização, fornecida pelo módulo `res_timing_timerfd` no Linux. Essa temporização é usada por aplicações como ________ e ________.
7. Ao instalar o Asterisk é melhor deixar ambientes de desktop como GNOME ou KDE de fora, porque interfaces gráficas consomem ciclos de CPU.
   - A. Verdadeiro
   - B. Falso
8. Os arquivos de configuração do Asterisk estão localizados no diretório ________.
9. Para instalar os arquivos de configuração de exemplo do Asterisk, digite o comando: ________
10. Por que é importante executar o Asterisk como um usuário não root?

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
