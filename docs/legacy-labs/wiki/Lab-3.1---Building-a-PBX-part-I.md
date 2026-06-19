These labs are part of the Complete Asterisk Training at [voip.school](https://www.voip.school/p/complete-asterisk-training)

SIP Extensions and trunks configuration

> Note: I have made two modifications in the script since the video. I have changed from bindaddr to udpbindaddr. In the peer channel I have changed from secret to remotesecret. In later versions, this options have changed, the old options still works (the lab worked just fine), but this seem to be the most correct configuration.

Step 0: Remove chan_pjsip to avoid conflicts

Add a # in from of the chan_pjsip line
Remove the # from the chan_sip line

`cd /etc/asterisk`\
`vi modules.conf`

Add noload=chan_pjsip.so\
Remove the # from noload=chan_sip.sip

This will make the chan_sip the standard SIP channel. While it is deprecated chan_sip is by far the most used SIP channel for Asterisk

Step 1: Move the sample file to sip.conf.default

`cd /etc/asterisk`\
`mv sip.conf sip.conf.default`

Step 2: Configure the general options in the file /etc/asterisk/sip.conf

Use your favorite editor to include the following lines in the beggining of the file

`[general]`\
`udpbindaddr = 0.0.0.0:5060`\
`context = dummy`\
`disallow = all`\
`allow = ulaw`\
`alwaysauthreject=yes`\
`allowguest=no`

Step 3: Configure your SIP extensions

`[zoiper]`\
`type=friend`\
`secret=#supersecret#`\
`host=dynamic`\
`qualify=yes`\
`directmedia=no`\
`context=from-internal`

`[xlite]`\
`type=friend`\
`secret=#supersecret#`\
`host=dynamic`\
`qualify=yes`\
`directmedia=no`\
`context=from-internal`

Step 4: Configure your softphones as explained in the corresponding lecture

If you want to use the versions originally shown in the videos, the links are below. I did my best to assure the links do not have viruses or malware. You may retest if you want in the link https://opentip.kaspersky.com/.

[X-Lite 5](https://github.com/flaviogoncalves/AsteriskTraining/blob/master/X-Lite_5.8.3_102651.exe)\
[Zoiper 3](https://github.com/flaviogoncalves/AsteriskTraining/blob/master/Zoiper_Free_3.15_Setup.exe)

Unfortunately X-Lite (2023-11-28) does not run anymore, it is expired. My recommendation for the training is to use Zoiper 5 in the desktop and another Zoiper 5 in the Mobile. Zoiper 5 runs on Mac, Linux and Windows. If you are running Linux, Mac, Android or iOS you can use Zoiper5.

Other Free Softphones known to work:

[Windows - Microsip](https://www.microsip.org/) - Can even open several windows, I love it!\
[Windows - Blink](https://icanblink.com/) - Support for TLS, messaging and several advanced features\
[Mac - Telephone](https://apps.apple.com/br/app/telephone/id406825478?mt=12) - Best free softphone for Mac\
[Windows/Mac/Linux/iOS/Android - Zoiper](https://www.zoiper.com/) - Best multi-platform softphone

Step 5: Configure your SIP trunk

Edit /etc/asterisk/sip.conf using your favorite editor

At the end of the general section include the following lines. Please use a different user as the trunk username than 1010, many people can be using the same trunk number. There are trunk usernames from 1010 to 1040 with the same password.

`[general]`\
`register=>1010:supersecret@sip.flagonc.com:5600/9999`

`[siptrunk]`\
`type=peer`\
`defaultuser=1010`\
`remotesecret=supersecret`\
`port=5600`\
`insecure=invite`\
`host=sip.flagonc.com`\
`fromuser=1010`\
`fromdomain=sip.flagonc.com`\
`context=from-siptrunk`

Step 5: Check the creation of the extensions and trunks using

`sip reload`\
`sip show peers`\
`sip show registry`

Step 6: Troubleshooting (if things don't work)

If you can't receive a call. 

0 - Check if you have mistakenly used 5060 instead of 5600\
1 - Check if you are registered using (sip show registry)\
2 - Try a different trunk username (1011 to 1040) pick one\
3 - Check if you have connectivity, ping sip.flagonc.com from the command line\
4 - Enable verbose 15 and check the logs in the console (core set verbose 15)\
5 - Enable SIP debuging (sip set debug on) and check if the call is arriving at your server.

If you are behind NAT and your calls are mute. 

1 - Discover your external address (Simply google "whats my ip")\
2  - Add the following lines to your sip.conf in the [general] section. In the exteraddr add the external address discovered in "whatsmyip".

`localnet=192.168.0.0/24`\
`localnet=172.16.0.0/12`\
`localnet=10.0.0.0/8`\
`externaddr=<your_external_address_discovered_in_whatsmyip>`\ 
