# Extending Asterisk with AMI and AGI

In several situations, it may be necessary to extend Asterisk features using external applications. There are many different ways by which it may be extended. In this chapter, we will cover two of the classic ways to integrate Asterisk with other systems: AMI – Asterisk Manager Interface and AGI – Asterisk Gateway Interface. We will also look at the command asterisk –rx and the system() application. To choose which way you want to integrate with Asterisk depends on the application. For AGI the most usual application is the IVR connected to a database. For AMI, dialers are the most popular app. A third, more modern interface — ARI, the Asterisk REST Interface — is covered separately in the next chapter.

## Objectives

By the end of this chapter, the reader should be able to:

- Describe access options to external programs
- Use asterisk –rx command to execute a console command
- Use the system() app to call external programs in the dial plan
- Explain what AMI is and how it works
- Configure the manager.conf file and enable AMI
- Execute an AMI command from a PHP program
- Explain what Asterisk manager proxy is and how it works
- Describe different AGI Flavors (DeadAGI, AGI, EAGI, FastAGI)
- Execute a simple AGI program created with PHP

## Major ways to extend Asterisk

Asterisk has different ways to interface with external programs. In this chapter, we will cover:

- Linux command line and Asterisk Console
- System() Application
- AMI
- AGI

## Extending Asterisk with console CLI

An application can easily call Asterisk from the Linux shell using the following command.

```
asterisk -rx <command>
```

Example:

```
asterisk -rx "stop now"
```

Even a command with an output can be called:

```
asterisk:~# asterisk -rx "pjsip show endpoints"
Endpoint:  <Endpoint/CID.....................................>  <State.....>  <Channels.>
    I/OAuth:  <AuthId/UserName..............................>
         Aor:  <Aor............................................>  <MaxContact>
       Contact:  <Aor/ContactUri..........................> <Hash....> <Status> <RTT(ms)..>
   Transport:  <TransportId........>  <Type>  <cos>  <tos>  <BindAddress..................>
    Identify:  <Identify/Endpoint.........................................................>
         Match:  <criteria.........................>
     Channel:  <ChannelId......................................>  <State.....>  <Time.....>
       Exten: <DialedExten...........>  CLCID: <ConnectedLineCID.......>
=========================================================================================

 Endpoint:  4000                                                 Not in use    0 of inf
```

## Extending Asterisk using the System() application

The system() application enables Asterisk to call an external application.

```
asterisk*CLI> core show application System
  -= Info about application 'System' =-
[Synopsis]
Execute a system command
[Description]
  System(command): Executes a command  by  using  system(). If the command
fails, the console should report a fallthrough.
Result of execution is returned in the SYSTEMSTATUS channel variable:
   FAILURE      Could not execute the specified command
   SUCCESS      Specified command successfully executed
```

Example: This application does a screen-pop using netbios WindowsPopup.

```
exten => 9000,1,System(/bin/echo -e "'Incoming Call From -> ${CALLERID(num)}
\\r Received: ${DATETIME}'"|/usr/bin/smbclient -M target_netbiosname)
exten => 9000,2,Dial(PJSIP/9000,15,t)
exten => 9000,3,Hangup
```

## What is AMI?

AMI enables a client program to connect to an Asterisk instance and issue commands or read events over a TCP connection. System integrators will find these resources useful for tracking channel states. AMI relies on a simple concept of a line protocol using key:value pairs over TCP. Asterisk by itself is not ready to handle too many connections over this interface. If you have lots of connections to AMI, consider using Asterisk manager proxy.

### What language to use for AMI

Selecting a programming language can be hard these days. There are simply too many options—Java, PHP, Perl, C, C#, Python, and several others. It’s possible to use AMI with any language that supports a socket or telnet interface. We have chosen PHP for this book because of its popularity.

### AMI protocol behavior

- Before sending any commands to Asterisk, you need to establish an AMI session
- The first line of a packet will have the key “Action” when sent from a client
- The first line of a packet will have the key “Response” or “Event” when coming from Asterisk
- Packages can be transmitted in any direction after the authentication

### Packet types

The type of the packet is determined by the existence of the following keys:

- Action: A packet sent from a client connected to AMI asking for a specific action. There is a finite set of actions available to clients. The loaded modules determine these actions. A packet contains the action name and its parameters.
- Response: The response sent from Asterisk to the last action sent from the client.
- Event: Data belonging to an event generated in the Asterisk core or by a module.

When a client sends packets of the Action type, a parameter named ActionID is included. Since the order in which the responses sent from Asterisk cannot be predicted, ActionID is used to correlate actions and responses. Event packets are used in two different contexts. First, events inform the client about changes in Asterisk (e.g., newly created channels, channels disconnected, or agents logging in and out of a queue). Second, events are used to transport responses to a client action.

## Configuring users and permissions

To access AMI, it is necessary to establish a TCP connection listening to a TCP port (usually 5038). You will need to configure the /etc/asterisk/manager.conf file to create a user account and permissions. There is a finite set of permissions: “read,” “write,” or both. These permissions are defined in the

```
manager.conf file.
[general]
enabled=yes
port=5038
bindaddr=127.0.0.1
[admin]
secret=senha
read=system,call,log,verbose,command,agent,user
write=system,call,log,verbose,command,agent,user
deny=0.0.0.0/0.0.0.0
permit=127.0.0.1/255.255.255.255
```

### Logging in to the AMI

To log in to and authenticate AMI, you will need to send an action packet of the login type with a username and account created in the manager.conf.

```
Action:login
Username:admin
Secret:password
```

Example: Logging in to AMI using php

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
?>
```

If you don’t need to receive the events, you can use “Events Off”.

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
fputs($socket, "Events: off\r\n\r\n");
?>
```

### Action packets

When you send an action packet to Asterisk, you can provide some extra keys (e.g., called number) by passing key:value pairs after the action. It is also possible to pass channel and global variables to the dial plan.

```
Action: <action type><CRLF>
<Key 1>: <Value 1><CRLF>
<Key 2>: <Value 2><CRLF>
Variable: <Variable 1>=<Value 1><CRLF>
Variable: <Variable 2>=<Value 2><CRLF>
...
<CRLF>
```

### Action commands

You can use the CLI instruction manager show commands to list the available actions. In Asterisk 22 the core set of commands includes (this list is representative; loaded modules add more):

```
Action Privilege Synopsis
  WaitEvent        <none>           Wait for an event to occur
  ModuleCheck      system,all       Check if module is loaded
  ModuleLoad       system,all       Module management
  CoreShowChannels system,reportin  List currently active channels
  Reload           system,config,a  Send a reload event
  CoreStatus       system,reportin  Show PBX core status variables
  CoreSettings     system,reportin  Show PBX core settings (version etc)
  VoicemailUsersL  call,reporting,  List All Voicemail User Information
  UserEvent        user,all         Send an arbitrary event
  SendText         call,all         Send text message to channel
  ListCommands     <none>           List available manager commands
  MailboxCount     call,reporting,  Check Mailbox Message Count
  MailboxStatus    call,reporting,  Check Mailbox
  AbsoluteTimeout  system,call,all  Set Absolute Timeout
  ExtensionState   call,reporting,  Check Extension Status
  Command          command,all      Execute Asterisk CLI Command
  Originate        originate,all    Originate Call
  Atxfer           call,all         Attended transfer
  Redirect         call,all         Redirect (transfer) a call
  ListCategories   config,all       List categories in configuration file
  CreateConfig     config,all       Creates an empty file in the configuration directory
  UpdateConfig     config,all       Update basic configuration
  GetConfigJSON    system,config,a  Retrieve configuration (JSON format)
  GetConfig        system,config,a  Retrieve configuration
  Getvar           call,reporting,  Gets a Channel Variable
  Setvar           call,all         Set Channel Variable
  Status           system,call,rep  Lists channel status
  Hangup           system,call,all  Hangup Channel
  Challenge        <none>           Generate Challenge for MD5 Auth
  Login            <none>           Login Manager
  Logoff           <none>           Logoff Manager
  Events           <none>           Control Event Flow
  Ping             <none>           Keepalive command
  DAHDIRestart     <none>           Fully Restart DAHDI channels (terminates calls)
  DAHDIShowChanne  <none>           Show status DAHDI channels
  DAHDIDNDoff      <none>           Toggle DAHDI channel Do Not Disturb status OFF
  DAHDIDNDon       <none>           Toggle DAHDI channel Do Not Disturb status ON
  DAHDIDialOffhoo  <none>           Dial over DAHDI channel while offhook
  DAHDIHangup      <none>           Hangup DAHDI Channel
  DAHDITransfer    <none>           Transfer DAHDI Channel
  IAXnetstats      system,reportin  Show IAX Netstats
  IAXpeerlist      system,reportin  List IAX Peers
  IAXpeers         system,reportin  List IAX Peers
  QueueRule        <none>           Queue Rules
  QueuePenalty     agent,all        Set the penalty for a queue member
  QueueLog         agent,all        Adds custom entry in queue_log
  QueuePause       agent,all        Makes a queue member temporarily unavailable
  QueueRemove      agent,all        Remove interface from queue.
  QueueAdd         agent,all        Add interface to queue.
  QueueSummary     <none>           Queue Summary
  QueueStatus      <none>           Queue Status
  Queues           <none>           Queues
  AgentLogoff      agent,all        Sets an agent as no longer logged in
  Agents           agent,all        Lists agents and their status
  PlayDTMF                        call,all         Play DTMF signal on a specific channel.
  PJSIPShowEndpoints              system,reportin  Lists PJSIP endpoints
  PJSIPShowEndpoint               system,reportin  Detail listing of an endpoint
  PJSIPQualify                    system,all       Qualify a chan_pjsip endpoint
  PJSIPShowRegistrationsOutbound  system,reportin  Lists outbound registrations
  PJSIPShowContacts               system,reportin  Lists PJSIP Contacts
```

```
  AGI              agi,all          Add an AGI command to execute by Async AGI
  MixMonitor       system,all       Record a call and mix the audio during recording
  StopMixMonitor   system,call,all  Stop recording a call through MixMonitor
  MixMonitorMute   system,call,all  Mute / unMute a Mixmonitor recording
  ShowDialPlan     config,reportin  List dialplan
  DBDelTree        system,all       Delete DB Tree
  DBDel            system,all       Delete DB Entry
  DBPut            system,all       Put DB Entry
  DBGet            system,reportin  Get DB Entry
  Bridge           call,all         Bridge two channels already in the PBX
  Park             call,all         Park a channel
  ParkedCalls      <none>           List parked calls
```

If you need to know specific command parameters, use the manager show command <command>. Example:

```
asterisk*CLI> manager show command Originate

  -= Info about Manager Command 'Originate' =-

[Synopsis]
Originate a call.

[Provided By]
builtin

[Since]
0.2.0

[Description]
Generates an outgoing call to a <Extension>/<Context>/<Priority> or
<Application>/<Data>

[Syntax]
Action: Originate
[ActionID:] <value>
Channel: <value>
[Exten:] <value>
[Context:] <value>
[Priority:] <value>
[Application:] <value>
[Data:] <value>
[Timeout:] <value>
[CallerID:] <value>
[Variable:] <value>
[Account:] <value>
[EarlyMedia:] <value>
[Async:] <value>
[Codecs:] <value>
[ChannelId:] <value>
[OtherChannelId:] <value>
[PreDialGoSub:] <value>

[Arguments]
Channel
    Channel name to call.
Exten
    Extension to use (requires 'Context' and 'Priority')
Context
    Context to use (requires 'Exten' and 'Priority')
Priority
    Priority to use (requires 'Exten' and 'Context')
Application
    Application to execute.
Data
    Data to use (requires 'Application').
Timeout
    How long to wait for call to be answered (in ms.).
CallerID
    Caller ID to be set on the outgoing channel.
Variable
    Channel variable to set, multiple Variable: headers are allowed.
Account
    Account code.
EarlyMedia
    Set to 'true' to force call bridge on early media.
Async
    Set to 'true' for fast origination.
Codecs
    Comma-separated list of codecs to use for this call.
ChannelId
    Channel UniqueId to be set on the channel.
OtherChannelId
    Channel UniqueId to be set on the second local channel.
PreDialGoSub
    Context,Extension,Priority to set options/headers needed before
    starting the outgoing extension.

[Privilege]
originate,all

[See Also]
OriginateResponse
```

### Event packets

Events are generated on the manager interface whenever something happens in Asterisk —
a channel is created or changes state, two channels are bridged or unbridged, a
registration changes, a queue member is added, and so on. Each event is a block of
`Key: value` lines beginning with an `Event:` header.

The exact set of events depends on the loaded modules and the Asterisk version, so rather
than reproduce a list that quickly goes stale, query the running server for the
authoritative set:

```
asterisk*CLI> manager show events             ; list every event this build can emit
asterisk*CLI> manager show event BridgeEnter  ; describe one event and its fields
```

For example, call bridging is reported through the `BridgeCreate`, `BridgeEnter`,
`BridgeLeave`, and `BridgeDestroy` events (`BridgeEnter` is "Raised when a channel enters a
bridge"). The older `Link`/`Unlink` events were removed in Asterisk 12.

## Asterisk Gateway Interface

AGI is a gateway interface to Asterisk similar to CGI used by web servers. It allows the use of high-level languages like Perl, PHP, and Python to extend Asterisk’s functionality. The main application for CGIs is IVR building. There are four types of AGI:

- Normal AGI, which calls a program inside Asterisk’s box.
- Fast AGI, which calls an AGI in another server using TCP sockets.
- EAGI, which enables sound channel access and control from the AGI.
- DEADAGI, which gives access to the channel even after hangup(). Usually called in the ‘h’ extension.

Application format:

```
asterisk*CLI> core show application AGI
  -= Info about application 'AGI' =-
[Synopsis]
Executes an AGI compliant application
[Description]
  [E|Dead]AGI(command|args): Executes an Asterisk Gateway Interface compliant
program on a channel. AGI allows Asterisk to launch external programs
written in any language to control a telephony channel, play audio,
read DTMF digits, etc. by communicating with the AGI protocol on stdin
and stdout.
Returns -1 on hangup (except for DeadAGI) or if application requested
 hangup, or 0 on non-hangup exit.
Using 'EAGI' provides enhanced AGI, with incoming audio available out of band
on file descriptor 3
Use the CLI command 'agi show' to list available agi commands
```

You can show the available AGI commands using the command `agi show commands` (output below is representative; Asterisk 22 adds a few additional commands):

```
Dead                        Command   Description
   No                         answer   Answer channel
   No                 channel status   Returns status of the connected channel
  Yes                   database del   Removes database key/value
  Yes               database deltree   Removes database keytree/value
  Yes                   database get   Gets database value
  Yes                   database put   Adds/updates database value
  Yes                           exec   Executes a given Application
   No                       get data   Prompts for DTMF on a channel
  Yes              get full variable   Evaluates a channel expression
   No                     get option   Stream file, prompt for DTMF, with timeout
  Yes                   get variable   Gets a channel variable
   No                         hangup   Hangup the current channel
  Yes                           noop   Does nothing
   No                   receive char   Receives one character from channels supporting it
   No                   receive text   Receives text from channels supporting it
   No                    record file   Records to a given file
   No                      say alpha   Says a given character string
   No                     say digits   Says a given digit string
   No                     say number   Says a given number
   No                   say phonetic   Says a given character string with phonetics
   No                       say date   Says a given date
   No                       say time   Says a given time
   No                   say datetime   Says a given time as specfied by the format given
   No                     send image   Sends images to channels supporting it
   No                      send text   Sends text to channels supporting it
   No                 set autohangup   Autohangup channel in some time
   No                   set callerid   Sets callerid for the current channel
   No                    set context   Sets channel context
   No                  set extension   Changes channel extension
   No                      set music   Enable/Disable Music on hold generator
   No                   set priority   Set channel dialplan priority
  Yes                   set variable   Sets a channel variable
   No                    stream file   Sends audio file on channel
   No            control stream file   Sends audio file and allows the listener cont.the
stream
   No                       tdd mode   Toggles TDD mode (for the deaf)
  Yes                        verbose   Logs a message to the asterisk verbose log
   No                 wait for digit   Waits for a digit to be pressed
   No                  speech create   Creates a speech object
   No                     speech set   Sets a speech engine setting
  Yes                 speech destroy   Destroys a speech object
   No            speech load grammar   Loads a grammar
  Yes          speech unload grammar   Unloads a grammar
   No        speech activate grammar   Activates a grammar
   No      speech deactivate grammar   Deactivates a grammar
   No               speech recognize   Recognizes speech
   No                          gosub   Execute a dialplan subroutine
```

To debug, use agi debug.

### Using AGI

In this example, we will use php-cli, the php command line version. Install php-cli if it’s not already installed. Follow these steps to use php AGI scripts.

1. All AGI scripts are located in `/var/lib/asterisk/agi-bin`
2. Change the permissions to allow execution.

```
chmod 755 *.php
```

3. Shell interface (php specific). The script’s first lines have to be:

```
#!/usr/bin/php -q
<?php
```

4. Open I/O channels:

```
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');
$stdlog = fopen('agi.log', 'w');
```

5. Manage the Asterisk output. Asterisk sends the information set each time AGI is called.

```
agi_request:testephp
agi_channel: Dahdi/1-1
agi_language: en
agi_type: Dahdi
agi_callerid:
agi_dnid:
agi_context: default
agi_extension: 4000
agi_priority: 1
```

Save the information sent:

```
while (!feof($stdin)) {
  $temp = fgets($stdin);
  $temp = str_replace("\n","",$temp);
  $s = explode(":",$temp);
  $agi[$s[0]] = trim($s[1]);
  if (($temp == "") || ($temp == "\n")) {
    break;
  }
}
```

The previous script will create an array named $agi. Available options are:

- agi_request – AGI file name
- agi_channel – AGI originating channel
- agi_language – Language set
- agi_type – Channel type (e.g., SIP, DAHDI)
- agi_uniqueid – Unique identifier
- agi_callerid – CallerID (Ex. Flavio <8590>)
- agi_context – Originating context
- agi_extension – Called extensions
- agi_priority – Priority
- agi_accountcode – Originating account code

To call a variable named agi_extensions, use $agi[agi_extensions].

6. Use channel AGI. At this point, you can start talking to Asterisk. Use the fputs command to send commands to AGI. You can also use the echo command.

```
fputs($stdout,"SAY NUMBER 4000 '79#' \n");
fflush($stdout);
```

Notes about using quotes:

- AGI command options are not optional
- Some options need to be enclosed in quotes <escape digits>
- Some options should not be enclosed in quotes <digit string>
- Some options can use both formats
- You can use single quotes

Step 7 – Pass variables Channel variables can be set in the AGI, but cannot be used inside the AGI. The following example does not work inside an AGI.

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/${EXTEN}"
```

The following example does work:

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/4000"
```

Step 8: Asterisk responses The following is necessary to verify responses from Asterisk:

```
$msg  = fgets($stdin,1024);
fputs($stdlog,$msg . "\n");
```

Step 9: Kill the locked (zombie) processes If your script fails for some reason, the process will hang. Use the killproc command to clean it before testing again.

```
 #!/usr/bin/php -q
 <?php
 ob_implicit_flush(true);
 set_time_limit(6);
 $in = fopen("php://stdin","r");
 $stdlog = fopen("/var/log/asterisk/agi.log", "w");
 // Enable debug (more verbose)
 $debug = false;
 // Functions definition
 function read() {
   global $in, $debug, $stdlog;
   $input = str_replace("\n", "", fgets($in, 4096));
   if ($debug) fputs($stdlog, "read: $input\n");
   return $input;
 }
 function errlog($line) {
   global $err;
   echo "VERBOSE \"$line\"\n";
 }
 function write($line) {
   global $debug, $stdlog;
   if ($debug) fputs($stdlog, "write: $line\n");
   echo $line."\n";
 }
 // Put agi headers in the array
 while ($env=read()) {
   $s = split(": ",$env);
   $agi[str_replace("agi_","",$s[0])] = trim($s[1]);
   if (($env == "") || ($env == "\n")) {
     break;
   }
 }
 // main program
 echo "VERBOSE \"Start here!\" 2\n";
 read();
 errlog("Call from ".$agi['channel']." – Phone ringing ");
 read();
 write("SAY DIGITS 22 X"); // X is the escape digit. since X is not DTMF, no ex
it is possible
 read();
 write("SAY NUMBER 2233 X"); // X is the escape digit. since X is not DTMF, no
exit is possible
 read();
 // clean up file handlers etc.
 fclose($in);
 fclose($stdlog);
 exit;
 ?>
```

### DeadAGI

DeadAGI is used when you do not have a live channel. Usually you execute the DeadAGI in the ´h´ extension.

### FASTAGI

Fast AGI implements AGI using a TCP port (4573 by default) as the Input/Output channel. FastAGI format is (agi://). For example:

```
exten => 0800400001, 1, Agi(agi://192.168.0.1)
```

When the TCP connection is lost or disconnected, the AGI ends and the TCP connection is closed, followed by a call disconnection. This resource is useful to ease the CPU load from your Asterisk server running scripts in an external server. You may obtain more details about FastAGI in the source code directory (please see the file “agi/fastagi-test”). The Asterisk-Java library provides a FastAGI server implementation for Java. For more information, see https://github.com/asterisk-java/asterisk-java

ARI, the modern REST/WebSocket interface, gets its own chapter next.

## Changing the source code

Asterisk is developed in C language (not C++). Teaching C programming is beyond the scope of this document. If you are interested, you will find related documentation at https://docs.asterisk.org, which offers good tips on how to apply and create patches to Asterisk as well as API documentation mostly generated by Doxygen software. For those familiar with C programming, changing the applications source code can be the most powerful (and dangerous) way to extend Asterisk.

## Summary

In this chapter, you have learned how to interface external programs to the Asterisk PBX. We have started with asterisk –rx passing commands from the Linux shell to the Asterisk console. Next, we learned about the System() application, which allows calling an external program from the dial plan. AMI is the closest interface to a CTI interface common in traditional PBXs. To call an application from the dial plan, we used the AGI, with a taste for its different flavors: DeadAGI for dead channels, EAGI for handling the audio streaming, Fast AGI for using TCP sockets as the input/output interface, and normal AGI for calling and processing the scripts inside the same Asterisk box. The next chapter is dedicated to ARI, the modern REST/WebSocket API that gives external applications full control of Asterisk channels and bridges.

## Quiz

1. Which of the following is NOT an interfacing method for Asterisk?
   - A. AMI
   - B. AGI
   - C. `asterisk -rx`
   - D. System()
   - E. External()
2. AMI allows passing Asterisk commands over TCP sockets, and this interface is enabled by default in a fresh Asterisk install.
   - A. True
   - B. False
3. AMI is very safe, because its authentication uses MD5 challenge/response.
   - A. True
   - B. False
4. FastAGI lets the dial plan call external scripts on another machine over TCP sockets (usually port 4573).
   - A. True
   - B. False
5. DeadAGI is used on active channels. It can be used on DAHDI channels but not on SIP or IAX channels.
   - A. True
   - B. False
6. AGI supports only PHP as a scripting language.
   - A. True
   - B. False
7. The command ___ shows all available AGI commands.
8. The command ___ shows all available AMI commands.
9. In an AMI action packet, which header does the client include so that the asynchronous responses and events coming back from Asterisk can be correlated with the action that triggered them?
   - A. `ActionID`
   - B. `Variable`
   - C. `Secret`
   - D. `Event`
10. Which AMI manager.conf permission class must a user have in order to run the `Originate` action and place an outbound call?
    - A. `originate`
    - B. `verbose`
    - C. `log`
    - D. `reporting`

**Answers:** 1 — E · 2 — B · 3 — B · 4 — A · 5 — B · 6 — B · 7 — `agi show commands` · 8 — `manager show commands` · 9 — A · 10 — A
