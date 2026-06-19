# The new SIP channel PJSIP

PJSIP is the SIP channel in Asterisk. It was first introduced in Asterisk 12 and, after years of development, became the default and recommended SIP channel. In Asterisk 22 (the current LTS) it is the only SIP channel driver: the old module chan_sip was deprecated for several releases and was finally **removed in Asterisk 21**, so it no longer exists in Asterisk 22. PJSIP is based on Teluu’s project called pjproject. The pjproject stack is employed by many softphones and commercial SIP implementations. It is a versatile and mature SIP stack.

## Objectives

By the end of this chapter, you should be able to:

- Describe the PJSIP channel and its object model
- Connect SIP clients to Asterisk using PJSIP
- Connect a SIP trunk provider using PJSIP
- Convert legacy sip.conf files to pjsip.conf
- Use templates and the PJSIP configuration wizard to simplify the creation of endpoints

## Why to use PJSIP

The PJSIP channel driver brought many features and solved several long-standing problems with the old chan_sip. Even though chan_sip is gone, it is useful to understand why PJSIP replaced it.

### Features

The channel supports many features, some deserve mention here

- Multiple registrations:. You may use more than one phone connected to the same Address of Record. In other words, you can connect two phones to the same endpoint.
- Friendly Application Program Interface (API). The API is friendly and easier to extend compared to the monolithic chan_sip.
- Multiple transports: You can listen to multiple addresses, ports and transports when using PJSIP. With the old channel you had to use the same address for all peers. PJSIP is more flexible.

### Problems with chan_sip

- Monolithic: chan_sip was monolithic and any change in the code was becoming very risky. So the pace of innovation was compromised in the channel.
- No official support: chan_sip was deprecated and then removed in Asterisk 21. It does not exist at all in Asterisk 22.
- Adoption note: PJSIP configuration is more verbose than chan_sip was — it requires a little more effort and more lines of configuration. That extra complexity slowed early adoption, but PJSIP is now mature, universal, and the only SIP option, so learning it is no longer optional.

## PJSIP modules

The PJSIP channel is implemented by many modules described below:

### res_pjsip

This is the base layer of PJSIP and the main module. It is responsible for some of the main services.

### res_pjsip_session

This module is responsible for media sessions, session description protocol processing and some addons

### res_pjsip_messaging

Process SIP messages and parse SIP headers.

### res_pjsip_registrar

Responsible to handle SIP registrations

### res_pjsip_pubsub

Responsible to process subscribe, notify and publish. These messages are responsible to handle SIP presence and BLF (Busy Lamp Field).

## PJSIP configuration

PJSIP has many different sections. The format of the section are:

```
[Section Name]
Option = Value
Option = Value
```

### End point section

The most important configuration object is the endpoint. The endpoint configuration has core functionality and has to be associated with an AOR and Transport section. Example:

```
[xlite]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=xlite
auth=xlite
```

If you look at the example above, the endpoint is a kind of glue linking all sections together. It specifies a transport, the address of record and the authentication for a phone. Also defines the most important part, the context entry point in the dialplan.

### Address of Record (AOR)

This object tells Asterisk where to contact the endpoint. It stores the contact addresses. It also allow the configuration of mailboxes. Example:

```
[xlite]
type=aor
max_contacts=2
```

### Authentication

This section is responsible for inbound and outbound authentication. The documentation is found at the example file pjsip.conf. Example:

```
[xlite]
type=auth
auth_type=userpass
username=xlite
password=#supersecret#
```

### Transport

The transport section allows you to define IPV4 and IPV6 addresses and the transport protocol, TCP, UDP, TLS, Websockets and so on. You may also configure Natted addresses in this section. You can create multiple transports, but they cannot share the same IP and port and you cannot bind multiple TCP or TLS transports of the same IP version. Example:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

### Registration

This object is used to configure an outbound registration. Example:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

### Identify

This object controls which SIP request belongs to each endpoint. If you do not have an identify section, the system will match the content of the “From” header with the endpoint name. Using this section, you can assign specific IP addresses to specific endpoints, identified by username or IP. Example:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

### ACL

The ACL object allows you to configure specific networks with access to the endpoint. Now ACLs are defined in a specific section or in the acl.conf. Example:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

## Relationship between entities

The relationship between the configuration objects provides a great flexibility for configuration. However, it seems a bit complex for anyone starting. Identify Endpoint ACL Domain Alias Transport Auth AOR Contact Registration The graphic above means:

### Relationships:

- ENDPOINT/AOR many to many
- ENDPOINT/AUTH Zero to Many to Zero to One
- ENDPOINT/IDENTIFY Zero to Many to One
- ENDPOINT/AUTH Zero to Many to One
- ENDPOINT/TRANSPORT Zero to Many to at least one
- REGISTRATION/AUTH Zero to many to zero to one
- REGISTRATION/TRANSPOPRT Zero to many to at least one
- AOR/CONTACT many to many ACL, DOMAIN_ALIAS don’t have relationship configurations

## Configuring a Softphone

To configure a softphone you have to define many different sections. Below an example on how to configure a softphone.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[xlite]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=xlite
auth=xlite
[xlite]
type=auth
auth_type=userpass
username=xlite
password=#supersecret#
[xlite]
type=aor
max_contacts=2
```

The configuration above sets a transport for UDP in the port 5060, then define an endpoint, its authentication by username and password and then the Address of Record with a maximum of two contacts.

## Configuring a SIP trunk

To configure a SIP trunk you need to have the IP address or Host of the SIP trunk, name and password. You have to create a new registration section for this purpose.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=userpass
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

## Nat traversal on res_pjsip

Network Address Translation was created a long time ago as a way to deal with the shortage of IP version 4 addresses. Many people also use NAT as a security feature hiding the internal addresses of a network from the public Internet. Sometimes you will have to handle NAT traversal. In some cases, the server can be behind NAT, such as where you are deploying the server in the cloud. Many times if you are deploying in the cloud your users will also be behind a NAT router. To organize things, we will split this chapter in two parts. The first one is the Asterisk server behind NAT such as in a cloud deployment. In the second section, we will cover how to support clients behind NAT using res_pjsip.

### Asterisk Server behind NAT

When the Asterisk server is behind NAT, you should inform the external and internal local addresses in the transport section. We will have the following directives.

#### direct_media

Similar to the one in chan_sip. Does the media flow directly from peer to peer or thru the server? For NAT it should flow thru the server. For NAT select no. Example:

```
direct_media=no
```

#### external_media_address

Media address to handle external RTP. Usually the same as the external_media_signaling. Use the public IP address of your server for media and signalling. Example:

```
external_media_address=54.232.1.20
```

#### external_signaling_address

External SIP address where to receive messages. Example:

```
external_signaling_address=54.232.1.20
```

#### local_net

The network you consider your local network. Example:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

### Complete example for transport for an Asterisk server behind NAT

To use an Asterisk server behind NAT you have to do two steps. First, define a transport behind NAT. Two, associate this transport to the endpoint.

#### Creating the transport behind NAT

To create the transport behind NAT in the file pjsip.conf create a section like below.

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

Associate the transport to an endpoint

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

For SIP trunks you should also associate the transport to the registration section as below.

```
[siptrunk_reg]
type=registration
transport=tnat
server=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=23456789@flagonc.com
contact_user=9999
realm=flagonc.com
```

### Using Asterisk with clients behind NAT

To use phones behind NAT you have to configure some additional parameters per endpoint.

#### direct_media

Similar to the one in chan_sip. Does the media flow directly from peer to peer or thru the server? For NAT it should flow thru the server. Example:

```
direct_media=no
```

#### rtp_symmetric

This is what we call comedia. Instead of relying in the address defined in this SDP header as usual in SIP, use the address from where you receive the first rtp packet and send back from the same address. Example:

```
rtp_symmetric=yes
```

#### force_rport

This is the behaviour defined in the RFC3581. Rather than using the address in the VIA header, send back the responses from where the requests are coming from. Example:

```
force_rport=yes
```

#### qualify_frequency

This settings have to be applied to the endpoint. There is also the last step, to configure the qualify option. You should have always some packets pinging the destination to keep the NAT mapping open. This is set in the AOR section. Example:

- qualify_frequency=15

Complete example of an endpoint where the server and the client are behind NAT

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

## Channel Naming

As usual one of the important aspects of a channel is its naming and PJSIP has some interesting details. You can start in a way that is similar to the SIP channel

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

The novelty is the possibility to dial all contacts. This was not possible with the old chan_sip. The function PJSIP_DIAL_CONTACTS will be translated to the list of contacts to dial.

```
exten=>6000,dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

To dial a trunk is slightly different than the previous version. Assume the trunk won’t be registered to your platform or don’t have and IP address associated with your AOR address of record. You can specify the address of the trunk directly in the line. Using an international dial as the example.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

If you prefer to specify the address of the trunk in the AOR section, you may also use.

```
exten=>9011.,Dial(PJSIP/${EXTEN:1}@siptrunk
```

## Migration from chan_sip to res_pjsip

Even though chan_sip no longer ships in Asterisk 22, you will still encounter legacy sip.conf files when upgrading older systems, and converting them is the fastest way to move to PJSIP. The Asterisk project provides a utility, `sip_to_pjsip.py`, to convert the configuration files and simplify the migration. You should run it directly in the /etc/asterisk directory. The utility is in the source code in the directory below, where ${PATH_TO_ASTERISK_SOURCE} is the path where the Asterisk source files are found. (Usually /usr/src/asterisk-22.x.y/)

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip.py
```

If you run using the option –help you will see two options:

```
-h help
-p prefix output included files with a prefix
```

Let’s migrate the sip.conf in our companion labs (github labs https://github.com/flaviogoncalves/AsteriskTraining)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.api4com.com:5600/9999
[zoiper]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[xlite]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.api4com.com
fromuser=1020
fromdomain=sip.api4com.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[zoiper]
qualify = yes
[xlite]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.api4com.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.api4com.com
client_uri = sip:1020@sip.api4com.com:5600
server_uri = sip:sip.api4com.com:5600
[auth_reg_sip.api4com.com]
type = auth
password = supersecret
username = 1020
[zoiper]
type = aor
max_contacts = 1
[zoiper]
type = auth
username = zoiper
password = #supersecret#
[zoiper]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = zoiper
outbound_auth = zoiper
aors = zoiper
[xlite]
type = aor
max_contacts = 1
[xlite]
type = auth
username = xlite
password = #supersecret#
[xlite]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = xlite
outbound_auth = xlite
aors = xlite
[siptrunk]
type = aor
contact = sip:1020@sip.api4com.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.api4com.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.api4com.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

While the conversion seems ok, we can see that some elements such as qualify=yes cannot be mapped directly. To fix you have to add to the aor section the command qualify_frequency=time in seconds. Example below.

```
[xlite]
type = aor
max_contacts = 1
qualify_frequency=15
```

## PJSIP configuration wizard

PJSIP is powerful but verbose to configure: many different sections, and templates that can be confusing at first. The good news is the PJSIP configuration wizard. By defining each channel in a few lines, it allows you to create templates and simplify the configuration of new devices. Use the file pjsip_wizard.conf to configure. You still have to define transport and global sections in the file pjsip.conf. Personally, I prefer to use the wizard just for phones, for sip trunks usually the number is not big and you can configure directly in pjsip. The biggest advantage of the wizard is the possibility to use templates and create phones quickly.

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[xlite](phone_default)
inbound_auth/username = xlite
inbound_auth/password = supersecret
[zoiper](phone_default)
inbound_auth/username = zoiper
inbound_auth/password = supersecret
```

## Loading and unloading PJSIP

In Asterisk 22 there is no longer a chan_sip channel to coexist with: chan_sip was removed in Asterisk 21, so PJSIP is the only SIP channel and there is no conflict to manage. PJSIP modules are loaded by default. In rare cases you may still want to control module loading from the modules.conf file — for example, to disable PJSIP on a server that only uses IAX2 or DAHDI.

> **[2nd-ed note]** On older Asterisk 16/18 systems this section described running chan_sip and PJSIP side by side and using `noload => chan_sip.so` to disable the legacy channel. Since chan_sip no longer exists in 21+, that part has been dropped. Confirm whether you want to keep any historical note for readers upgrading from very old releases.

### To disable PJSIP

Edit the file modules.conf and add the following lines.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
noload => res_pjsip_log_forwarder.so
```

## Console commands

Now that you configured your PJSIP endpoints, it is time to see how to check your configuration. There are many console commands to help you with this task. After editing pjsip.conf, reload the configuration with:

```
module reload res_pjsip.so
```

The shorthand `pjsip reload` works as well.

### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the xlite softphone and see that is available.

### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![09-pjsip-the-new-sip-channel figure 1](../images/09-pjsip-the-new-sip-channel-img01.png)

### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

### pjsip show registrations

The command below shows the registrations made by our own server.

![09-pjsip-the-new-sip-channel figure 2](../images/09-pjsip-the-new-sip-channel-img02.png)

![09-pjsip-the-new-sip-channel figure 3](../images/09-pjsip-the-new-sip-channel-img03.png)

### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints. Listing contacts

### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems.

```
pjsip set logger on
pjsip set logger off
```

You can also restrict the logging to a single host with `pjsip set logger host <ip>`.

### pjsip set history on

A great addition to PJSIP is the concept of history. You can capture and analyse SIP request and replies in real time in an easy way. To start history use the command below. Now you can show history Then to see a specific request or reply show the history item.

![09-pjsip-the-new-sip-channel figure 4](../images/09-pjsip-the-new-sip-channel-img04.png)

![09-pjsip-the-new-sip-channel figure 5](../images/09-pjsip-the-new-sip-channel-img05.png)

![09-pjsip-the-new-sip-channel figure 6](../images/09-pjsip-the-new-sip-channel-img06.png)

Very easy, isn’t it? You may also clear the history whenever you want using pjsip history clear.

## Summary

PJSIP comes with a lot of features. It is now the only SIP channel in Asterisk, since chan_sip was removed in Asterisk 21. If you want to use Asterisk 22, you will have to learn how to use it. In this chapter you have learned the basics of PJSIP. Check the official documentation at docs.asterisk.org for full coverage of the channel, there is a lot more to learn. In our labs in the github in the lab 5 you may practice what you have just learned. (https://github.com/flaviogoncalves/AsteriskTraining/wiki/Lab-5----Using- PJSIP)

![09-pjsip-the-new-sip-channel figure 7](../images/09-pjsip-the-new-sip-channel-img07.png)
