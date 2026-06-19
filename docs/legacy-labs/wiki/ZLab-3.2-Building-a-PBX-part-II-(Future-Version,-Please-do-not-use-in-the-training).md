These labs are part of the training Complete Asterisk Training at www.udemy.com, attend using our [discounted coupon](
https://www.udemy.com/building-a-complete-pbx-with-asterisk/?couponCode=GITHUB2018)

Configuring a dial plan

Step 1: Configuring the extensions

Move the current file extensions.conf to extensions.conf.sample

`mv extensions.conf extensions.conf.sample`

Use your favorite editor to edit a new file /etc/asterisk/extensions.conf

`[from-internal]`\
`exten=>6000,1,dial(SIP/phone1,20)`\
`exten=>6001,1,dial(SIP/phone2,20)`

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
`OPERATOR=SIP/phone1`\
`[from-siptrunk]`\
`exten=9999,1,dial(${OPERATOR},20)`

Step 4 - Testing incoming calls
 
To test incoming calls is a little harder. We will need to simulate an incoming call. I have in my server a click to call application. To generate an incoming call, go to:

http://sip.voip.school

Generate an incoming call from the page, it should ring your SIP phone. 

Include the extension you have registered in the SIP provider defined in the Lab 3.1 as show below 

_[general]_\
_register=>**1010**:supersecret@sip.voip.school:5600/9999_

Use any Caller ID you want. (e.g Flavio 1010)

![image](https://user-images.githubusercontent.com/4958202/179411553-93d44f20-b1e0-46e3-bf8b-d4cf8ba2f840.png)

Troubleshooting

If you are no receiving the calls,

Solution 1: Please try to generate the call very quickly after a sip reload. There are more than one student registered as 1010 ansd the last to register remove the other registrations. 

Solution 2: Rather than registering with the user 1010, try with another such as 1011 or 1012 and so on. The passwords are the same. 

