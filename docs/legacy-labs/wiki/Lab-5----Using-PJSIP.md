These labs are part of the training Complete Asterisk Training at www.udemy.com, attend using our [discounted coupon](
https://www.udemy.com/building-a-complete-pbx-with-asterisk/?couponCode=GITHUB2018)

Lab 5 - SIP using the new channel driver PJSIP. 

> Note: When testing this lab I saw sometimes XLITE loosing the registration. So check if phones registration is ok before inbound tests using **pjsip show aors**

Step 1 - Disable chan_sip and load chan_pjsip

Edit /etc/asterisk/modules.conf and change the following lines. 

`;noload => chan_pjsip.so`\
`noload =>chan_sip.so`

Go to the Linux command line and restart Asterisk

#/etc/init.d/asterisk restart

Step 2 - Save the original pjsip.conf

Step 3 - Configure the new pjsip.conf

`[transport-udp-main]`\
`type=transport`\
`protocol=udp`\
`bind=0.0.0.0:5060`\
`[transport-udp-alternative]`\
`type=transport`\
`protocol=udp`\
`bind=0.0.0.0:5080`

`[xlite]`\
`type=endpoint`\
`transport=transport-udp-main`\
`context=from-internal`\
`disallow=all`\
`allow=ulaw`\
`aors=xlite`\
`auth=xlite`\
`[xlite]`\
`type=auth`\
`auth_type=userpass`\
`username=xlite`\
`password=#supersecret#`\
`[xlite]`\
`type=aor`\
`max_contacts=2`

`[zoiper]`\
`type=endpoint`\
`transport=transport-udp-main`\
`context=from-internal`\
`disallow=all`\
`allow=ulaw`\
`aors=zoiper`\
`auth=zoiper`\
`[zoiper]`\
`type=auth`\
`auth_type=userpass`\
`username=zoiper`\
`password=#supersecret#`
`[zoiper]`\
`type=aor`\
`max_contacts=2`

`[blink]`\
`type=endpoint`\
`transport=transport-udp-main`\
`context=from-internal`\
`disallow=all`\
`allow=ulaw`\
`aors=blink`\
`auth=blink`
`[blink]`\
`type=auth`\
`auth_type=userpass`\
`username=blink`\
`password=#supersecret#`\
`[blink]`\
`type=aor`\
`max_contacts=2`

Step 7 - Change the naming of the SIP channels in extensions.conf

`[globals]`\
`OPERATOR=PJSIP/xlite`

`exten=>6000,1,gosub(PJSIP/zoiper,${EXTEN})`\
`exten=>6001,1,gosub(PJSIP/xlite,${EXTEN})`\
`exten=>6002,1,gosub(PJSIP/blink,${EXTEN})`\
`exten=>6003,1,gosub(PJSIP/bria,${EXTEN})`

`exten=>1,1,dial(PJSIP/zoiper)`\
`exten=>2,1,dial(PJSIP/xlite)`\
`exten=>3,1,dial(PJSIP/bria)`\
`exten=>6000,1,Dial(PJSIP/zoiper)`\
`exten=>6001,1,Dial(PJSIP/xlite)`

Step 8 - Test calls between extensions, please reload all phones. Pay attention to disable stun on all phones

> Note: Some times, only one softphone get access to the multimedia, so try from all the phones, sometimes only one of them will get audio. 

Step 9 - Create the siptrunk

Edit the file /etc/asterisk/pjsip.conf

`[siptrunk]`\
`type=endpoint`\
`transport=transport-udp-main`\
`context=from-siptrunk`\
`direct_media=no`\
`disallow=all`\
`allow=ulaw`\
`outbound_auth=siptrunk`\
`aors=siptrunk`

`[siptrunk]`\
`type=aor`\
`contact=sip:sip.flagonc.com:5600`

`[siptrunk]`\
`type=auth`\
`auth_type=userpass`\
`username=1020`\
`password=supersecret`

`[siptrunk]`\
`type=registration`\
`outbound_auth=siptrunk`\
`server_uri=sip:1020@sip.flagonc.com:5600`\
`client_uri=sip:1020@sip.flagonc.com`\
`contact_user=9999`

`[siptrunk]`\
`type=identify`\
`endpoint=siptrunk`\
`match=sip.flagonc.com`

Step 10 - Change the naming of the SIP channels in extensions.conf

exten=>_9.,1,dial(PJSIP/${EXTEN:1}@siptrunk,20)

Step 11 - Test the outgoing calls

Dial 9130523456789

Step 12 - Test the incoming calls

Go to the page sip.flagonc.com and use the click to call to generate a call to your registered account (in the lab case 1020). Check if monkeys called your xlite phone as they can't choose an option in your IVR :)

