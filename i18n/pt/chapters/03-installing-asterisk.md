# Instalando o Asterisk 22

No primeiro capítulo, aprendemos um pouco sobre como o Asterisk é útil no ambiente de telefonia. Neste capítulo, abordaremos como baixar e instalar o Asterisk. Antes de começar, é essencial aprender como compilá-lo e instalá-lo. O processo de compilação pode parecer estranho para usuários tradicionais do Microsoft™ Windows™, mas é bastante comum no ambiente Linux™. Pode-se obter um código otimizado para o seu hardware ao compilar o Asterisk, que é o que faremos aqui. O Asterisk roda em vários sistemas operacionais, mas escolhemos facilitar as coisas e começar com apenas um deles: Linux. Escolhemos o Debian como a distribuição Linux™ porque as dependências são fáceis de instalar e a distribuição é estável, com baixo consumo de recursos. Se você quiser usar outra distribuição, por favor, altere o nome das dependências adequadamente.

> **[Nota da 2ª ed.]** Esta edição tem como alvo o **Asterisk 22 LTS** (lançado em 2024, com suporte total até 16/10/2028). O Asterisk 22 é a versão de suporte de longo prazo atual. Observe que a Digium foi adquirida pela **Sangoma** (2018), e o Asterisk agora é patrocinado pela Sangoma — referências à "Digium" ao longo deste capítulo referem-se à marca legada para hardware histórico.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Determinar os requisitos de hardware para o Asterisk;
- Instalar o Linux com as dependências necessárias;
- Baixar uma versão estável via HTTPS;
- Compilar o Asterisk; e
- Aprender como iniciar o Asterisk no momento da inicialização (boot).

## Hardware mínimo necessário

O Asterisk não precisa de muito hardware para rodar, no entanto, existem algumas dicas para escolher o melhor hardware para suas necessidades. Você deve levar em consideração os seguintes fatores principais ao escolher seu hardware:

- Número total de usuários registrados. Defina quantos registros por segundo você precisa suportar
- Número total de chamadas simultâneas. Defina quantas conversas de rede você precisa processar no adaptador de rede e fazer a ponte no servidor Asterisk
- Quais codecs você precisa suportar. Codecs de alta complexidade exigirão muito poder de CPU/FPU em seu servidor; o iLBC, por exemplo, foi medido por seu criador (Global IP Sound) em aproximadamente 18 MIPS por canal para quadros de 30 ms (e cerca de 15 MIPS para quadros de 20 ms) em um DSP TI C54x
- Cancelamento de eco. O cancelamento de eco pode consumir muita CPU/FPU; em alguns casos, você deve escolher o cancelamento de eco por hardware usando DSPs na placa de interface de telefonia
- Disponibilidade. Use RAID1 ou 5 para aumentar a disponibilidade. Lembre-se, o Asterisk é uma aplicação 24x7.

O componente principal para um servidor Asterisk é o adaptador de rede. Recomenda-se um bom adaptador de rede para servidor. A CPU é importante quando você precisa suportar codecs de alta complexidade, como g.729 e iLBC, e cancelamento de eco. Você pode optar por usar DSPs dedicados; a Sangoma (anteriormente Digium) fornece uma placa DSP chamada TC400B capaz de suportar 120 chamadas g729 simultâneas. A melhor prática é escolher um computador novo, de classe servidor, de um fabricante conhecido. Para saber exatamente quantas chamadas simultâneas ou quantos usuários registrados uma máquina específica pode suportar, você deve testar este hardware com uma ferramenta de teste de estresse, como o SIPP (http://sipp.sourceforge.net). Alguns fabricantes de hardware, como a Xorcom (http://www.xorcom.com), publicam seus resultados no site. Nota: Algumas aplicações do Asterisk, como ConfBridge e música em espera, precisam de uma fonte de temporização interna. No Linux moderno, isso é fornecido automaticamente pelo módulo integrado `res_timing_timerfd` — nenhum hardware de telefonia é necessário. (O antigo temporizador de software `dahdi_dummy` não existe mais; sua funcionalidade foi incorporada ao módulo principal do kernel `dahdi` no DAHDI Linux 2.3.0.) Você pode confirmar o temporizador ativo com o comando CLI `timing test`.

### Configuração de hardware

O hardware do Asterisk não precisa ser sofisticado. Você não precisa de uma placa de vídeo cara ou de inúmeros periféricos. Algumas dicas sobre a configuração de hardware:

- Desative portas USB, seriais e paralelas não utilizadas para evitar o consumo de interrupções desnecessárias.
- Uma placa de interface de rede robusta é essencial.
- Tenha cuidado especial se estiver usando placas de interface de telefonia. Algumas placas usam um barramento PCI de 3,3 volts, e não é fácil encontrar placas-mãe para elas. Hoje em dia, o PCI express é encontrado mais facilmente.
- Preste muita atenção ao disco rígido; PBXs costumam trabalhar em regime 24x7, enquanto desktops trabalham 8x5. Não use hardware de desktop para um PBX, geralmente o disco rígido falha antes do primeiro ano. Minha recomendação é usar uma máquina servidor ou um appliance projetado para rodar aplicações 24x7.

### Compartilhamento de IRQ

Placas de interface de telefonia (por exemplo, X100P) geram grandes quantidades de interrupções. Atender a essas interrupções requer tempo de processador. Os drivers não podem fazer esse processamento se você tiver outro dispositivo usando a mesma interrupção. Em um sistema de CPU única, você deve evitar o compartilhamento de IRQ entre dispositivos. Recomendamos o uso de hardware dedicado para rodar o Asterisk. Não se esqueça de desativar qualquer hardware estranho ou desnecessário. Alguns hardwares podem ser desativados na configuração da BIOS da placa-mãe. Depois de iniciar o computador, veja suas interrupções atribuídas em /proc/interrupts.

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

Aqui você pode ver três placas Digium, cada uma em seu próprio IRQ. Se este for o caso em seu sistema, prossiga e instale os drivers de hardware. Se este não for o caso, volte e tente algo diferente para evitar o compartilhamento de IRQ.

## Escolhendo uma distribuição Linux

O Asterisk foi inicialmente desenvolvido para rodar em Linux. No entanto, ele também pode rodar em BSD Unix ou macOS. Se você é novo no Asterisk, tente usar Linux primeiro, pois é muito mais fácil. O Asterisk tem como alvo oficial a família RHEL (CentOS/RHEL/Fedora), Ubuntu e Debian. Boas escolhas práticas hoje são **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS** e **Rocky Linux 9 / AlmaLinux 9** — o CentOS Linux chegou ao fim da vida útil, então prefira Rocky ou AlmaLinux em sistemas da família RHEL. Para este livro, usarei o Ubuntu 24.04 LTS. Baixe a imagem de servidor da versão pontual mais recente 24.04 no diretório oficial de lançamentos abaixo (o nome exato do arquivo inclui a versão pontual atual, por exemplo, `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparando o Linux para o Asterisk

Imediatamente após instalar o Asterisk, instalaremos os pacotes necessários para a compilação subsequente do Asterisk e dos drivers DAHDI. Primeiro, indicaremos ao Debian de onde os pacotes serão baixados. Isso é feito usando o utilitário apt-setup. Passo 1: Instale o Ubuntu 24.04 LTS Server em uma máquina virtual (use a imagem de 64 bits; as distribuições usadas neste livro são de 64 bits, embora o próprio Asterisk ainda suporte x86 de 32 bits). Usamos o VirtualBox para este treinamento. Você pode baixar a imagem em https://releases.ubuntu.com/24.04. A instalação do Linux está fora do escopo deste treinamento. O conhecimento básico de Linux é pré-requisito para este treinamento.

## Instalando o Linux para o Asterisk

Instale seu Linux como de costume, sem uma interface gráfica de usuário. Instale e configure o servidor de e-mail também. Precisaremos do servidor de e-mail (exim4) para enviar notificações de correio de voz mais adiante neste livro. Cuidado: Esta instalação formatará seu PC. Todos os dados do seu disco serão apagados. Por favor, certifique-se de fazer backup de todos os dados antes de começar. Passo 1: Coloque o CD na unidade de CD-ROM e inicialize seu PC. A maioria das perguntas é muito simples de responder.

## Instalando dependências

Para instalar o Asterisk e o DAHDI, você precisa instalar muitas dependências de software. A maneira recomendada de fazer isso no Asterisk 22 é usar o script que acompanha a árvore de fontes, que conhece os nomes corretos dos pacotes para cada distribuição suportada. Após baixar e extrair a fonte do Asterisk (veja "Compilando o Asterisk" abaixo), execute:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

Passo 1: Faça login como root (ou use `sudo`). Passo 2: Se você preferir instalar as dependências manualmente em um sistema Debian/Ubuntu, a lista de pacotes equivalente é:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

> **[Nota da 2ª ed.]** A lista original fazia referência a `subversion`, `libnewt-dev` e `libncurses5-dev`. A fonte do Asterisk agora está hospedada no Git (o subversion não é mais necessário), e o Debian/Ubuntu moderno envia o `libncurses-dev` em vez do versionado `libncurses5-dev`. Prefira o `./contrib/scripts/install_prereq install` em vez de uma lista mantida manualmente.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) é a arquitetura de drivers para placas analógicas e digitais. Antes de instalar o Asterisk, é importante instalar o DAHDI se você planeja usar interfaces analógicas ou digitais. O DAHDI ainda existe para placas de telefonia analógica/digital, mas é cada vez mais um nicho — a maioria das implantações modernas é puramente VoIP e pode pular esta seção inteiramente. Instale o DAHDI apenas se você tiver hardware de interface de telefonia física. Obtenha os arquivos de origem usando:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Descompacte os arquivos usando:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compilando drivers DAHDI

Você precisará compilar os módulos DAHDI. Os comandos ./configure e make menuselect foram introduzidos há vários anos. O último permite que você selecione quais utilitários e módulos construir. Os seguintes comandos farão isso:

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

make install-config O DAHDI foi configurado. Se você tiver algum hardware DAHDI, agora é recomendado que você edite /etc/dahdi/modules para carregar o suporte apenas para o hardware DAHDI instalado neste sistema. Por padrão, o suporte para todo o hardware DAHDI é carregado na inicialização do DAHDI. Acho que o hardware DAHDI que você tem em seu sistema é: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware Esta tela (acima) pede que você altere o arquivo /etc/dahdi/modules para carregar apenas os drivers necessários para sua configuração específica e mostrar o hardware detectado. Edite o arquivo /etc/dahdi/modules e carregue apenas o hardware necessário. No meu caso, eu estava usando uma máquina de teste com um Xorcom Astribank 6FXS e 2FXO. O arquivo é mostrado abaixo.

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

Como regra geral, você deve usar a versão com os recursos necessários. O Asterisk segue um modelo de lançamento que alterna entre LTS (suporte de longo prazo) e lançamentos padrão. No momento desta edição, o **Asterisk 22 é o lançamento LTS atual** (lançado em 2024, com suporte até 2028), o que o torna a melhor escolha agora. O Asterisk 20 é o LTS anterior, e a versão 16 (usada na primeira edição) chegou ao fim da vida útil. Para sistemas de produção, escolha sempre um lançamento LTS.

> **[Nota da 2ª ed.]** Verifique a versão pontual exata atual em downloads.asterisk.org antes de imprimir. No momento desta escrita, o branch 22 é o LTS ativo.

## Compilando o Asterisk

Se você já compilou software anteriormente, compilar o Asterisk será uma tarefa fácil. Execute os seguintes comandos para compilar e instalar o Asterisk. Lembre-se, você pode escolher quais aplicações e módulos construir usando make menuselect. Passo 1: Baixe o código-fonte

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Passo 2: Instale os pré-requisitos de compilação (veja "Instalando dependências" acima)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Passo 3: Configure a compilação

```
./configure
```

Passo 4: Selecione os módulos para construir

```
make menuselect
```

Use make menuselect para instalar apenas os módulos necessários. No Asterisk 22, o canal SIP é o **chan_pjsip** (construído por padrão); o antigo **chan_sip** foi removido no Asterisk 21 e não existe mais. O *pass-through* de Opus funciona imediatamente (o módulo `res_format_attr_opus` na árvore lida com a negociação SDP), mas o módulo de transcodificação **codec_opus** ainda é um binário externo de código fechado da Sangoma/Digium — selecioná-lo no menuselect faz o download a partir dos servidores da Digium. O binário é gratuito. Veja "Selecionando módulos com menuselect" abaixo para detalhes.

Passo 5: Construa e instale o Asterisk, depois crie a configuração padrão e os arquivos de exemplo

```
make
make install
make samples
make config
ldconfig
```

`make install` instala os binários e módulos, `make samples` escreve os arquivos de configuração de exemplo em `/etc/asterisk`, `make config` instala o script de inicialização SysV para sua distribuição detectada (por exemplo, `/etc/init.d/asterisk` no Debian/Ubuntu), e `ldconfig` atualiza o cache de bibliotecas compartilhadas. Uma unidade systemd também é enviada na árvore de fontes em `contrib/systemd/asterisk.service`, mas o `make config` não a instala automaticamente — copie-a para o lugar certo se você preferir rodar o Asterisk sob systemd (veja abaixo).

### Selecionando módulos com menuselect

`make menuselect` abre um menu baseado em texto onde você escolhe exatamente quais aplicações, codecs, canais e recursos construir. Algumas notas específicas para o Asterisk 22:

- **chan_pjsip** (em *Channel Drivers*) é o canal SIP moderno e está habilitado por padrão; é o único canal SIP no Asterisk 22.
- **codec_opus** (em *Codec Translators*) é um módulo **externo** (sua entrada no menuselect diz "Download the Opus codec from Digium"); habilitá-lo faz o `make` buscar o binário gratuito de código fechado da Sangoma/Digium. O pass-through de Opus em si não precisa de módulo extra. O módulo **codec_g729** da Sangoma também está disponível — o binário é gratuito para baixar, mas a transcodificação G.729 legal requer uma licença comprada por canal.
- Selecione os formatos de som e idiomas que você deseja nos menus *Core Sound Packages*, *Music On Hold File Packages* e *Extras Sound Packages*; tudo o que você marcar lá é baixado e instalado automaticamente durante o `make install`.

Após fazer suas seleções, escolha **Save & Exit** e continue com `make`.

> **[Nota da 2ª ed.]** Insira uma nova captura de tela do `make menuselect` capturada do Asterisk 22 (a captura de tela da 1ª edição mostrava chan_sip/chan_skinny/chan_mgcp, que não existem mais). A tela Channel Drivers deve mostrar chan_pjsip e nenhum chan_sip.

## Iniciando e parando o Asterisk

Com esta configuração mínima, é possível iniciar o Asterisk com sucesso. Para aprendizado e depuração, você pode iniciar o Asterisk em primeiro plano conectado ao console:

```
/usr/sbin/asterisk –vvvgc
```

Use o comando CLI stop now para desligar o Asterisk.

```
CLI>core stop now
```

### Iniciando o Asterisk com systemd

Em distribuições Linux modernas (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), o gerenciador de serviços do sistema é o **systemd**. O Asterisk envia uma unidade systemd em `contrib/systemd/asterisk.service` na árvore de fontes; copie-a para `/etc/systemd/system/asterisk.service` e execute `systemctl daemon-reload`. Uma vez instalado, a maneira recomendada de rodar o Asterisk em produção é através do `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Uma vez que o Asterisk esteja rodando como um serviço, conecte-se à sua CLI com `asterisk -r` (conectar) ou `asterisk -rvvv` (conectar com saída detalhada).

> **[Nota da 2ª ed.]** Em sistemas mais antigos, o Asterisk era iniciado via script de inicialização SysV legado (`/etc/init.d/asterisk`) e o wrapper **safe_asterisk**, que reiniciava o Asterisk automaticamente se ele travasse. Com o systemd, a reinicialização automática é tratada pela diretiva `Restart=` do arquivo de unidade, então o `safe_asterisk` geralmente não é mais necessário. A abordagem legada init/`safe_asterisk` ainda funciona, mas está obsoleta em distribuições baseadas em systemd.

### Opções de tempo de execução do Asterisk

O processo de inicialização do Asterisk é muito simples. Se o Asterisk for executado sem nenhum parâmetro, ele é iniciado como um daemon.

```
/sbin/asterisk
```

Você pode acessar o console do Asterisk executando o seguinte comando. Observe que mais de um processo de console pode ser executado ao mesmo tempo.

```
/sbin/asterisk -r
```

### Opções de tempo de execução disponíveis para o Asterisk

Você pode mostrar as opções de tempo de execução disponíveis usando asterisk –h

```
sipast:/usr/src/asterisk-22.x.y# asterisk -h
```

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation e outros. Uso: asterisk [OPÇÕES] Opções válidas: -V Exibir número da versão e sair -C <arquivo_config> Usar um arquivo de configuração alternativo -G <grupo> Executar como um grupo diferente do chamador -U <usuário> Executar como um usuário diferente do chamador -c Fornecer CLI de console -d Aumentar depuração (múltiplos d's = mais depuração) -f Não fazer fork -F Sempre fazer fork -g Despejar core em caso de travamento -h Esta tela de ajuda -i Inicializar chaves criptográficas na inicialização -L <carga> Limitar a carga média máxima antes de rejeitar novas chamadas -M <valor> Limitar o número máximo de chamadas ao valor especificado -m Silenciar depuração e saída do console no console -n Desativar colorização do console. Pode ser usado apenas na inicialização. -p Executar como thread de pseudo-tempo real -q Modo silencioso (suprimir saída) -r Conectar ao Asterisk nesta máquina -R Igual a -r, exceto tentar reconectar se desconectado -s <socket> Conectar ao Asterisk via socket <socket> (válido apenas com -r) -t Gravar arquivos de som em /var/tmp e movê-los para onde pertencem após a conclusão -T Exibir a hora no formato [Mmm dd hh:mm:ss] para cada linha de saída na CLI. Não pode ser usado com modo de console remoto. -v Aumentar verbosidade (múltiplos v's = mais detalhado) -x <cmd> Executar comando <cmd> (implica -r) -X Habilitar o uso de #exec no asterisk.conf -W Ajustar cores do terminal para compensar um fundo claro

## Diretórios de instalação

O Asterisk é instalado em vários diretórios, que podem ser modificados no arquivo asterisk.conf. Para fins de treinamento, eu alteraria a verbosidade de 3 para 15; para produção, mantenha em 3. As opções max_calls e max_load são boas opções para proteger seu sistema contra sobrecarga.

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

## Arquivos de log e rotação de log

O PBX Asterisk registra suas mensagens no diretório /var/log/asterisk. O arquivo que controla os logs

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

; Alguns comandos de console estão associados ao processo de logger.

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

Mais informações sobre o logrotate podem ser obtidas usando:

```
#man logrotate
```

## Desinstalando o Asterisk

Para desinstalar o Asterisk, use:

```
make uninstall
```

Para desinstalar o Asterisk e todos os arquivos de configuração, use:

```
make uninstall-all
```

## Notas de instalação do Asterisk

Esta seção fornecerá alguns conselhos sobre questões a serem abordadas antes de instalar o Asterisk.

### Sistemas de Produção

Se o Asterisk for instalado em um ambiente de produção, você deve prestar atenção ao design do sistema. Um servidor deve ser otimizado de tal forma que os sistemas de telefonia tenham prioridade sobre outros processos do sistema. O Asterisk não deve rodar junto com software intensivo em processador, como X-Windows. Se você precisar rodar processos intensivos em CPU (por exemplo, um banco de dados enorme), use um servidor separado. De um modo geral, o Asterisk é suscetível a variações de desempenho de hardware. Portanto, tente usar o Asterisk em um ambiente de hardware que não exija mais de 40% de utilização da CPU.

### Dicas de Rede

Se você planeja usar telefones IP, é importante que você preste atenção à sua rede. Protocolos de voz são muito bons e resistentes à latência e até mesmo a jitters; no entanto, se você usar uma rede local mal configurada, a qualidade da voz sofrerá. Só é possível garantir uma boa qualidade de voz usando qualidade de serviço (QoS) em switches e roteadores. A voz em uma rede local tende a ser boa, mas mesmo em um ambiente LAN, se você tiver hubs de 10 Mbps com muitas colisões, acabará tendo uma voz distorcida ou ruim. Siga estas recomendações para garantir a melhor qualidade de voz possível:

- Use QoS de ponta a ponta, se possível ou economicamente viável. Com QoS de ponta a ponta, a qualidade da voz é perfeita. Sem desculpas!
- Evite usar hubs de 10/100 Mbps para voz em um ambiente de produção. Colisões podem impor jitters na rede. Hubs full duplex de 10/100 Mbps são preferíveis porque não ocorrem colisões.
- Use VLANs para separar transmissões desnecessárias da rede de voz. Você não quer um vírus destruindo sua rede de voz com transmissões ARP.
- Eduque os usuários sobre as expectativas em uma rede de voz. Sem QoS, não afirme que a voz será perfeita, pois na maioria dos casos não será. Uma qualidade de voz semelhante à de um telefone celular será alcançada na maioria das vezes. Use telefones de qualidade, pois problemas com firmware e design de hardware são comuns.

## Resumo

Neste capítulo, você aprendeu sobre os requisitos mínimos de hardware, bem como como baixar, instalar e compilar o Asterisk. O Asterisk deve ser executado com um usuário não root por motivos de segurança. Você deve verificar seu ambiente de rede antes de iniciar o ambiente de produção.

## Questionário

1. No Asterisk 22, qual driver de canal fornece suporte SIP, e o que aconteceu com o antigo `chan_sip`?
   - A. O `chan_sip` ainda é o padrão; o `chan_pjsip` é opcional.
   - B. O `chan_pjsip` é o canal SIP padrão; o `chan_sip` foi removido no Asterisk 21 e não existe mais.
   - C. Ambos são construídos por padrão e você escolhe entre eles em tempo de execução.
   - D. O suporte SIP foi removido inteiramente em favor do IAX2.
2. Placas de interface de telefonia para o Asterisk geralmente possuem Processadores de Sinal Digital (DSPs) integrados e, portanto, não precisam de muita CPU do PC.
   - A. Verdadeiro
   - B. Falso
3. Se você deseja uma qualidade de voz perfeita, precisa implementar qualidade de serviço (QoS) de ponta a ponta.
   - A. Verdadeiro
   - B. Falso
4. Você deve sempre escolher a versão mais recente do Asterisk, pois é a mais estável.
   - A. Verdadeiro
   - B. Falso
5. Qual é a maneira recomendada de instalar as dependências de compilação para o Asterisk 22?
6. Se você não tiver uma placa de interface TDM, ainda terá uma fonte de temporização interna para sincronização, fornecida pelo módulo `res_timing_timerfd` no Linux. Essa temporização é usada por aplicações como ________ e ________.
7. Ao instalar o Asterisk, é melhor deixar ambientes de desktop como GNOME ou KDE de fora, porque interfaces gráficas consomem ciclos de CPU.
   - A. Verdadeiro
   - B. Falso
8. Os arquivos de configuração do Asterisk estão localizados no diretório ________.
9. Para instalar os arquivos de configuração de exemplo do Asterisk, digite o comando: ________
10. Por que é importante rodar o Asterisk como um usuário não root?

**Respostas:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Execute o `./contrib/scripts/install_prereq install` a partir da árvore de fontes do Asterisk extraída · 6 — ConfBridge e Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Segurança (limita os danos se o Asterisk for comprometido)
