These labs are part of the training Complete Asterisk Training at www.udemy.com, attend using our [discounted coupon](
https://www.udemy.com/building-a-complete-pbx-with-asterisk/?couponCode=GITHUB2018)

Adding other applications

Step 1: Record two messages

In this lab we will use the Record() command to record a few audio messages. The first message for the autoattendant and the second for the IVR. 

At /etc/asterisk/extensions.conf, in the context [from-internal] include the following lines

`[from-internal]`\
`exten => _4.,1,Record(${EXTEN:1}:gsm)`\
`exten => _4.,n,wait(1)`\
`exten => _4.,n,Playback(${EXTEN:1})`\
`exten => _4.,n,Hangup()`

After editing don't forget to reload the dialplan (CLI>dialplan reload) 

From one of the softphones dial **4menu1** and record the following message "Please, dial the extension number or wait to be attended". Press # at the end to hear what you've just recorded. 

Repeat the process now, for the file menu2 (dial 4menu2) and record the following message "Dial 1 for sales, 2 for tech support and 3 for financial services". Press # at the end to hear what you've just recorded. 

Step 2: Configuring an autoattendant

To configure an autoattendant, use the commands below. 

`[from-internal]`\
`;Extension to simulate an incoming call`\
`exten=>8,1,goto(aasiptrunk,9999,1)`


`[from-siptrunk]`\
`include=aasiptrunk`

`[aasiptrunk]`\
`exten=>9999,1,answer()`\
`exten=>9999,n,background(menu1)`\
`exten=>9999,n,waitexten(10)`\
`exten=>9999,n,Dial(${OPERATOR})`\
`exten=>6000,1,Dial(SIP/zoiper)`\
`exten=>6001,1,Dial(SIP/xlite)`

When ready, dial 8 to testand choose 6001 to transfer the call to the extension 6001. 

Step 3: Configuring an IVR

In this step we will replace the autoattendant by an IVR

`[from-siptrunk]`\
`include=ivrsip`

`[from-internal]`\
`;Extension to simulate an incoming call`\
`exten=>8,1,goto(ivrsip,9999,1)`

`[ivrsip]`\
`exten=>9999,1,answer()`\
`exten=>9999,n,background(menu2)`\
`exten=>9999,n,waitexten(10)`\
`exten=>9999,n,Dial(${OPERATOR})`\
`exten=>1,1,dial(SIP/zoiper)`\
`exten=>2,1,dial(SIP/xlite)`\
`exten=>3,1,dial(IAX/zoiper2)`\
`exten=>6000,1,Dial(SIP/zoiper)`\
`exten=>6001,1,Dial(SIP/xlite)`

When ready, dial 8 to test and choose one of the options. 

Step 4: Voicemail

To configure a voicemail we have to follow two steps. The first is to configure the file voicemail.conf. Then you have to create a macro in the extensions.conf. 

**voicemail.conf**

`[general]`\
`format=wav49|gsm|wav`\
`[default]`\
`6000=>6000,Caixa do PAP2,root@localhost,,|attach=yes|delete=0`\
`6001=>6001,Xlite, root@localhost,,|attach=yes|delete=0`

extensions.conf

`[stdexten]`\
`exten=>s,1,Dial(${ARG1},20,tT)`\
`exten=>s,n,Goto(${DIALSTATUS})`\
`exten=>s,n,hangup()`\
`exten=>s,n(BUSY),voicemail(${ARG2},b)`\
`exten=>s,n,hangup()`\
`exten=>s,n(NOANSWER),voicemail(${ARG2},u)`\
`exten=>s,n,hangup()`\
`exten=>s,n(CANCEL),hangup`\
`exten=>s,n(CHANUNAVAIL),hangup`\
`exten=>s,n(CONGESTION),hangup`


`[from-internal]`\
`exten=>6000,1,Gosub(stdexten,s,1(SIP/Zoiper,${EXTEN}))`\
`exten=>6001,1,Gosub(stdexten,s,1(SIP/xlite,${EXTEN}))`\
`exten=8,1,voicemailmain()`

Reload the dialplan (CLI>dialplan reload) and dial 8 to test the voicemail menu. 

Step 5: Conference Room 

To configure a conference room, is just one step 

`exten=5,1,Confbridge(main)`

Test the conference room with two phones dialing the extension 5. 