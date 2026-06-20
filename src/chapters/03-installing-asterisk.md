# Installing Asterisk 22

In the first chapter, we learned a bit about how Asterisk is useful in the telephony environment. In this chapter, we will cover how to download and install Asterisk. Before starting, it is essential to learn how to compile and install it. The compilation process may seem weird for traditional Microsoft™ Windows™ users, but it is fairly common in the Linux™ environment. One can get an optimized code for your hardware when compiling Asterisk, which is what we will do here. Asterisk runs in several operating systems, but we chose to keep things easy and start with only one of them: Linux. We chose Debian as the Linux™ distribution because the dependencies are easy to install and the distribution is stable, with a low footprint. If you want to use another distribution, please change the name of the dependencies accordingly.

This edition targets **Asterisk 22 LTS** (released 2024-10-16; full support through 2028-10-16, security fixes through 2029-10-16). Asterisk 22 is the current long-term support release. Note that Digium was acquired by **Sangoma** in 2018, and Asterisk is now sponsored by Sangoma — references to "Digium" throughout this chapter refer to the legacy brand for historical hardware.

## Objectives

By the end of this chapter you should be able to:

- Determine the hardware requirements for Asterisk;
- Install Linux with the required dependencies;
- Download a stable version over HTTPS;
- Compile Asterisk; and
- Learn how to start Asterisk at boot time.

## Minimum Hardware Required

Asterisk does not need a lot of hardware to run, however there are some tips to choose the best hardware for your requirements. You should take into consideration the following main factors when choosing your hardware:

- Total number of registered users. Define how many registrations per second you need to support
- Total number of simultaneous calls. Define how many network conversations you need to process in the network adapter and bridge on the Asterisk server
- Which codecs you need to support. High complexity codecs will require a lot of CPU/FPU power in your server; iLBC, for example, was measured by its creator (Global IP Sound) at roughly 18 MIPS per channel for 30 ms frames (and about 15 MIPS for 20 ms frames) on a TI C54x DSP
- Echo cancellation. Echo cancellation may take a lot of CPU/FPU, in some cases you should choose hardware echo cancellation using DSPs in the telephony interface card
- Availability. Use RAID1 or 5 to increase availability. Remember, Asterisk is 24x7 application.

The main component for an Asterisk Server is the network adapter. A good server network adapter is recommended. CPU is important when you need to support high complexity codecs such as g.729 and iLBC and echo cancellation. You may choose to use dedicated DSPs, Sangoma (formerly Digium) provides a DSP card named TC400B capable to support 120 g729 simultaneous calls.

The best practice is to choose a new, server class, computer from a known manufacturer. To know exactly how many simultaneous calls or how many registered users a specific machine can support, you should test this hardware with a stress test tool such as SIPP (http://sipp.sourceforge.net). Some hardware manufacturers such as Xorcom (http://www.xorcom.com) publish its results in the website.

Note: Some Asterisk applications, such as ConfBridge and music on hold, need an internal timing source. On modern Linux this is provided automatically by the built-in `res_timing_timerfd` module — no telephony hardware is required. (The old `dahdi_dummy` software timer no longer exists; its functionality was folded into the main `dahdi` kernel module in DAHDI Linux 2.3.0.) You can confirm the active timer with the CLI command `timing test`.

### Hardware configuration

The Asterisk hardware does not need to be sophisticated. You don't need an expensive video card or numerous peripherals. Some tips about hardware configuration;

- Disable unused USB, serial and parallel ports to avoid the consumption of unnecessary interrupts.
- A robust network interface card is essential.
- Take particular care if you are using telephony interface cards. Some cards use a 3.3 volts PCI bus, and it is not easy to find motherboards for them. In these days, PCI express is more easily found.
- Pay a close attention to the hard disk, PBX used to work in a 24x7 regime while desktops work 8x5. Do not use desktop hardware for a PBX, usually the hard disk fails before the first year. My recommendation is to use a server machine or an appliance designed to run 24x7 applications.

### IRQ sharing

Telephony interface cards (e.g., X100P) generate large quantities of interruptions. Serving these interruptions requires processor time. The drivers can't do this processing if you have another device using the same interruption. In a single CPU system, you should avoid IRQ sharing between devices. We recommend the use of dedicated hardware to run Asterisk. Don't forget to disable any foreign or unnecessary hardware. Some hardware can be disabled in the motherboard bios setup. Once you have started your computer, see your assigned interrupts in /proc/interrupts.

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

Here you can see three Digium cards, each in their own IRQ. If this is the case in your system, go ahead and install the hardware drivers. If this is not the case, go back and try something else to avoid IRQ sharing.

## Choosing a Linux distribution

Asterisk was initially developed to run on Linux. However, it can also run on BSD Unix or macOS. If you are new to Asterisk, try using Linux first since it is much easier. Asterisk officially targets the RHEL family (CentOS/RHEL/Fedora), Ubuntu, and Debian. Good practical choices today are **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS**, and **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux is end-of-life, so prefer Rocky or AlmaLinux on RHEL-family systems. For this book I will use Ubuntu 24.04 LTS. Download the latest 24.04 point-release server image from the official releases directory below (the exact filename includes the current point release, e.g. `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparing Linux for Asterisk

Immediately after installing Asterisk, we will install the packages required for the subsequent compilation of Asterisk and DAHDI drivers. First, we will indicate to Debian where the packages will be downloaded from. This is done by using the apt-setup utility. Step 1: Install Ubuntu 24.04 LTS Server in a virtual machine (use the 64-bit image; the distributions used in this book are 64-bit, though Asterisk itself still supports 32-bit x86). We have used VirtualBox for this training. You may download the image from https://releases.ubuntu.com/24.04 The Linux installation is out of the scope of this training. Linux basic knowledge is prerequisite for this training.

## Installing Linux for Asterisk

Install your Linux as usual, without a graphical user interface. Install and configure the email server as well. We will need the email server (exim4) to send voicemail notifications later in this book. Caution: This installation will format your PC. All your disk data will be erased. Please make sure to back up all data before starting. Step 1: Put the CD in the CD-ROM drive and boot your PC. Most questions are very simple to answer.

## Installing dependencies

To install Asterisk and DAHDI you have to install many software dependencies. The recommended way to do this in Asterisk 22 is to use the script that ships with the source tree, which knows the correct package names for each supported distribution. After downloading and extracting the Asterisk source (see "Compiling Asterisk" below), run:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. Login as root (or use `sudo`).
2. If you prefer to install the dependencies manually on a Debian/Ubuntu system, the equivalent package list is:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

Note that Asterisk source is now hosted on Git, so `subversion` is no longer needed, and modern Debian/Ubuntu ship `libncurses-dev` rather than the versioned `libncurses5-dev`. Prefer `./contrib/scripts/install_prereq install` over a hand-maintained list, since the script always tracks the correct package names for your distribution.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) is the architecture of drivers for analog and digital cards. Before installing Asterisk it is important to install DAHDI if you are planning to use analog or digital interfaces. DAHDI still exists for analog/digital telephony cards but is increasingly niche — most modern deployments are pure VoIP and can skip this section entirely. Install DAHDI only if you have physical telephony interface hardware. Get the source files using:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Uncompress the files using:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

You will need to compile the DAHDI modules. The commands ./configure and make menuselect where introduced several years ago. The latter enables you to select which utilities and modules to build. The following commands will do this:

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

make install-config DAHDI has been configured. If you have any DAHDI hardware it is now recommended you edit /etc/dahdi/modules in order to load support for only the DAHDI hardware installed in this system. By default support for all DAHDI hardware is loaded at DAHDI start. I think that the DAHDI hardware you have on your system is: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware This screen (above) asks you to change the file /etc/dahdi/modules to load only the required drivers for your specific configuration and show the detected hardware. Edit the file /etc/dahdi/modules and load only the required hardware. In my case, I was using a test machine with a Xorcom Astribank 6FXS and 2FXO. The file is shown below.

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

Re-initialize your computer and verify the correct loading of the drivers.

## Which version to choose

As a rule of thumb, you should use the version with the required features. Asterisk follows a release model of alternating LTS (long-term support) and standard releases. At the time of this edition, **Asterisk 22 is the current LTS release** (released October 2024; the latest point release is 22.10.0), which makes it the best one to choose now. Asterisk 20 is the previous LTS, and version 16 (used in the first edition) is end-of-life. For production systems, always pick an LTS release.

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

With this minimal configuration, it’s possible to start Asterisk successfully. For learning and debugging, you can start Asterisk in the foreground attached to the console:

```
/usr/sbin/asterisk –vvvgc
```

Use the CLI command stop now to shutdown Asterisk.

```
CLI>core stop now
```

### Starting Asterisk with systemd

On modern Linux distributions (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), the system service manager is **systemd**. Asterisk ships a systemd unit at `contrib/systemd/asterisk.service` in the source tree; copy it to `/etc/systemd/system/asterisk.service` and run `systemctl daemon-reload`. Once installed, the recommended way to run Asterisk in production is through `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Once Asterisk is running as a service, attach to its CLI with `asterisk -r` (connect) or `asterisk -rvvv` (connect with verbose output).

On older systems Asterisk was started via the legacy SysV init script (`/etc/init.d/asterisk`) and the **safe_asterisk** wrapper, which restarted Asterisk automatically if it crashed. With systemd, automatic restart is handled by the unit file's `Restart=` directive, so `safe_asterisk` is generally no longer needed. The legacy init/`safe_asterisk` approach still works but is deprecated on systemd-based distributions.

### Asterisk runtime options

The Asterisk starting process is very simple. If Asterisk is run without any parameters, it is launched as a daemon.

```
/sbin/asterisk
```

You can access the Asterisk console by executing the following command. Please note that more than one console process can be run at the same time.

```
/sbin/asterisk -r
```

### Available runtime options for Asterisk

You can show the available runtime options using asterisk –h

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

## Installation directories

Asterisk is installed on several directories, which can be modified in the asterisk.conf file. For training purposes I would change the verbose from 3 to 15, for production keep it in 3. The option max_calls and max_load are good options to protect your system from overloading.

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

## Log files and log rotation

Asterisk PBX logs its messages on the /var/log/asterisk directory. The file that controls the logs

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

More information about logrotate can be obtained using:

```
#man logrotate
```

## Uninstalling Asterisk

To uninstall Asterisk, use:

```
make uninstall
```

To uninstall Asterisk and all configuration files, use:

```
make uninstall-all
```

## Asterisk installation notes

This section will provide some advice about issues to address before installing Asterisk.

### Production Systems

If Asterisk is installed in a production environment, you should pay attention to the system design. A server has to be optimized in such a way that telephony systems have priority over other system processes. Asterisk should not run together with processor-intensive software such as X-Windows. If you need to run CPU-intensive processes (e.g., a huge database), use a separate server. Generally speaking, Asterisk is susceptible to hardware performance variations. Thus, try using Asterisk in a hardware environment that does not require more than 40% of CPU utilization.

### Network Tips

If you plan to use IP phones, it is important that you pay attention to your network. Voice protocols are very good and resistant to latency and even jitters; however, if you use a poorly configured local area network, voice quality will suffer. It is only possible to guarantee good voice quality using quality of service (QoS) in switches and routers. Voice in a local area network tends to be good, but even in a LAN environment, if you have 10 Mbps hubs with too many collisions, you will end up having a distorted or crappy voice. Follow these recommendations to ensure the best possible voice quality:

- Use end-to-end QoS if possible or economically feasible. With end-to-end QoS, the voice quality is perfect. No excuses!
- Avoid using 10/100 Mbps hubs for voice in a production environment. Collisions can impose jitters on the network. Full duplex 10/100 Mbps are preferred because no collisions occur.
- Use VLANs to separate unnecessary broadcasts of the voice network. You don’t want a virus destroying your voice network with ARP broadcasts.
- Educate users about expectations in a voice network. Without QoS, don’t state that the voice will be perfect as in most cases it won’t be. A quality of voice similar to a mobile phone will most often be achieved. Use quality phones as problems with firmware and hardware design are common.

## Summary

In this chapter, you have learned about the minimum hardware requirements as well as how to download, install, and compile Asterisk. Asterisk should be executed with a non-root user for security reasons. You should check your network environment before starting the production environment.

## Quiz

1. In Asterisk 22, which channel driver provides SIP support, and what happened to the older `chan_sip`?
   - A. `chan_sip` is still the default; `chan_pjsip` is optional.
   - B. `chan_pjsip` is the default SIP channel; `chan_sip` was removed in Asterisk 21 and no longer exists.
   - C. Both are built by default and you choose between them at runtime.
   - D. SIP support was removed entirely in favor of IAX2.
2. Telephony interface cards for Asterisk usually have Digital Signal Processors (DSPs) built in and so do not need much CPU from the PC.
   - A. True
   - B. False
3. If you want perfect voice quality, you need to implement end-to-end quality of service (QoS).
   - A. True
   - B. False
4. You should always choose the latest Asterisk version, as it is the most stable.
   - A. True
   - B. False
5. What is the recommended way to install the build dependencies for Asterisk 22?
6. If you don't have a TDM interface card you will still have an internal timing source for synchronization, provided by the `res_timing_timerfd` module on Linux. This timing is used by applications such as ________ and ________.
7. When installing Asterisk it is better to leave desktop environments such as GNOME or KDE out, because graphical interfaces consume CPU cycles.
   - A. True
   - B. False
8. Asterisk configuration files are located in the ________ directory.
9. To install the Asterisk sample configuration files, type the command: ________
10. Why is it important to run Asterisk as a non-root user?

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
