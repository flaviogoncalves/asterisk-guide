These labs are part of the training Complete Asterisk Training at [voip.school](https://www.voip.school/p/complete-asterisk-training)

Configuring a dial plan

Step 1: Configuring the extensions

Move the current file extensions.conf to extensions.conf.sample

`mv extensions.conf extensions.conf.sample`

Use your favorite editor to edit a new file /etc/asterisk/extensions.conf

`[from-internal]`\
`exten=>6000,1,dial(SIP/zoiper,20)`\
`exten=>6001,1,dial(SIP/xlite,20)`

After the configuration, type the following command in the Asterisk Console to reload the dialplan

`CLI>dialplan reload`

Step 2: Dial between phones

Now test a call between 6000 and 6001

Step 3:  Dialing to the public network

Let's create a route in this exercise. Access the route by dialing "9" first

`exten=>_9.,1,dial(SIP/siptrunk/${EXTEN:1},20,r)`

Reload the dialplan again

`CLI>dialplan reload`

Test the route dialing 9 and any specific number

Step 4: Receiving calls from the operator

Now let's create some new contexts in the dialplan. The context globals should be the first context in the file. There you can create global variables. Then we will create a new context called [from-siptrunk], this context will be used to handle incoming calls. 

`[globals]`\
`OPERATOR=SIP/xlite`\
`[from-siptrunk]`\
`exten=9999,1,dial(${OPERATOR},20)`

Step 4 - Testing incoming calls
 
To test incoming calls is a little harder. We will need to simulate an incoming call. I have in my server a click to call application. To generate an incoming call, go to:

http://sip.flagonc.com

Generate an incoming call from the page, it should ring your SIP phone. 

Include your name and the extension you have registered (e.g Flavio 1010)