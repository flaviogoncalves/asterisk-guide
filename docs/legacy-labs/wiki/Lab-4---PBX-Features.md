Lab Preparation:

Before doing this lab add another extensions 6002, install a Blink softphone as an additional extension. In all Dial commands add the options 'tT' to enable transfers.

1 - Music On Hold

To test music on hold type commands below

Edit the file /etc/asterisk/extensions.conf and add the following configuration in the context [from-internal]

`exten => 8100,1,Answer()`\
`exten => 8100,n,MusicOnHold(default,30)`

> Note: Don't forget to reload the dialplan 

`CLI>dialplan reload`

Test by dialing 8100

2 - Blind Call Transfer 

We will test only the transfer executed by Asterisk. If you have phones supporting transfers by using SIP refer (usually paid phones and softphones), please check the instructions of your phone. 

To test the blind transfer, dial from one softphone to another, now in the destination press the key #. You will hear the world "transfer". Then dial to an external number such as 913052345678 and again press #.  

3 - Consultative Call Transfer (Attended Transfer)

In the features.conf remove the remark from the atxfer and change accordingly

`transferdigittimeout => 5`

`[featuremap]`\
`atxfer => *2                   ; Attended transfer`

> Note: Use _module reload features_ to reload the features.conf

Dial from phone A to B, press *2 to transfer to the destination number (Use 9130523456789). After the second call is answered, hangup the phone.  

4 - Call Parking

Prepare your dialplan for call parking

in the file /etc/asterisk/extensions.conf in the context [from-internal] add.

`include => parkedcalls`

> Note: Don't forget to reload the dialplan. 

To test, call from one phone to the other, transfer to the 700, record the parked extensions. hangup the phone and call the parked extension a few seconds later, you should get the same call. 

5 - Call Pickup

Prepare Asterisk for call pickup. 

Edit the file /etc/asterisk/features.conf and remove the semicolon (;) from the following line

`;pickupexten = *8`

> Note: Use _module reload features_ to reload the features.conf

Prepare your extensions adding callgroups and pickupgroups in the sip.conf file

callgroup=1
pickupgroup=1
directmedia=no

>Note: Don't forget the SIP reload

`CLI> sip reload`

Call from the 6002 to the 6000 and capture from 6001

6 - Follow Me

To test follow me, you will have to change two files, followme.conf and extensions.conf

Edit the file /etc/asterisk/followme.conf and add these lines to the end of the file

`[6001]`\
`context=from-internal`\
`number=6000`\
`[6000]`\
`context=from-internal`\
`number=9130523456789`

Then edit the file /etc/asterisk/extensions.conf and add the bold line in the MACRO. 

`[stdexten]`\
`exten=>s,1,Dial(${ARG1},20,tT)`\
**`exten=>s,n,FollowMe(${ARG2})`**\
`exten=>s,n,Goto(${DIALSTATUS})`\
`exten=>s,n,hangup()`\
`exten=>s,n(BUSY),voicemail(${ARG2},b)`\
`exten=>s,n,hangup()`\
`exten=>s,n(NOANSWER),voicemail(${ARG2},u)`\
`exten=>s,n,hangup()`\
`exten=>s,n(CANCEL),hangup`\
`exten=>s,n(CHANUNAVAIL),hangup`\
`exten=>s,n(CONGESTION),hangup`


To test:\
1 - From 6002 call 6001 and reject the call on 6001, the call should be sent to 6000\
2 - From 6001 call 6002 and reject the call. As 6002 does not have a followme ID, the command will be ignored and the call will be diverted to the voicemail\
3 - From 6001 call 6000 , the number will be forward to an external destination  