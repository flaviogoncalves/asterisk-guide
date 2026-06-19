This labs are part of the training Complete Asterisk Training at www.udemy.com

SIP Extensions and trunks configuration

Step 1: Remove chan_pjsip to avoid conflicts

Add a # in from of the chan_pjsip line
Remove the # from the chan_sip line

`cd /etc/asterisk`\
`vi modules.conf`

Add noload=chan_pjsip.so\
Remove the # from noload=chan_sip.sip

This will make the chan_sip the standard SIP channel. While it is deprecated chan_sip is by far the most used SIP channel for Asterisk

Step 2: Move the sample file to sip.conf.default

`cd /etc/asterisk`\
`mv sip.conf sip.conf.default`

Step 3: Configure the general options in the file /etc/asterisk/sip.conf

Use your favorite editor to include the following lines in the beggining of the file

`[general]`\
`udpbindaddr = 0.0.0.0:5060`\
`context = dummy`\
`disallow = all`\
`allow = ulaw`\
`alwaysauthreject=yes`\
`allowguest=no`

Step 4: Configure your SIP extensions

`[phone1]`\
`type=friend`\
`secret=#supersecret#`\
`host=dynamic`\
`qualify=yes`\
`directmedia=no`\
`context=from-internal`

`[phone2]`\
`type=friend`\
`secret=#supersecret#`\
`host=dynamic`\
`qualify=yes`\
`directmedia=no`\
`context=from-internal`

Step 5: Configure your softphones as explained in the corresponding lecture

There are many options for softphones. Recently I've switched to MicroSIP, easy to install and run but limited to Windows. Zoiper is available for MAC, Windows, Linux, Android and iPhone. You can use one phone in the desktop and other in the mobile. Pay attention to disable stun in the phones. Stun will make the phones take the external IP address of your router causing problems.  

Step 6: Configure your SIP trunk

Edit /etc/asterisk/sip.conf using your favorite editor

At the end of the general section include the following lines. Please use a different user as the trunk username than 1010, many people can be using the same trunk number. There are trunk usernames from 1010 to 1040 with the same password.

`[general]`\
`register=>1010:supersecret@sip.voip.school:5600/9999`

`[siptrunk]`\
`type=peer`\
`defaultuser=1010`\
`remotesecret=supersecret`\
`port=5600`\
`insecure=invite`\
`host=sip.voip.school`\
`fromuser=1010`\
`fromdomain=sip.voip.school`\
`context=from-siptrunk`

Step 7: Check the creation of the extensions and trunks using

`sip reload`\
`sip show peers`\
`sip show registry`

Step 8: Troubleshooting (if things don't work)

If you can't receive a call. 

0 - Check if you have mistakenly used 5060 instead of 5600\
1 - Check if you are registered using (sip show registry)\
2 - Try a different trunk username (1011 to 1040) pick one\
3 - Check if you have connectivity, ping sip.voip.school from the command line\
4 - Enable verbose 15 and check the logs in the console (core set verbose 15)\
5 - Enable SIP debuging (sip set debug on) and check if the call is arriving at your server.

If you are behind NAT and your calls are mute. 

1 - Discover your external address (Simply google "whats my ip")\
2  - Add the following lines to your sip.conf in the [general] section. In the exteraddr add the external address discovered in "whatsmyip".

`localnet=192.168.0.0/24`\
`localnet=172.16.0.0/12`\
`localnet=10.0.0.0/8`\
`externaddr=<your_external_address_discovered_in_whatsmyip>`\ 
