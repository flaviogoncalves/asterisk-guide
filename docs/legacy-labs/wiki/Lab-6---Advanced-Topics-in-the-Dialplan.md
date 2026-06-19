These labs are part of the training Complete Asterisk Training at www.udemy.com, attend using our [discounted coupon](
https://www.udemy.com/building-a-complete-pbx-with-asterisk/?couponCode=GITHUB2018)

Implementing authorization for calls using included contexts

Step 1: Go to the file pjsip.conf and at the endpoint configure the following contexts

xlite -> from-internal\
zoiper -> to-local\
blink -> to-ld

Step 2: Remove the line below from the context [from-internal]

`exten=>_9.,1,dial(PJSIP/${EXTEN:1}@siptrunk,20)`

Step 3: Edit the extensions.conf file and add the following lines

`[to-local]`\
`include=>from-internal`\
`exten=>_9NXXXXXX,1,dial(PJSIP/${EXTEN:1}@siptrunk,20)`

`[to-ld]`\
`include=>to-local`\
`exten=>_91NXXNXXXXXX,1,dial(PJSIP/${EXTEN:1}@siptrunk,20)`

`[to-int]`\
`include=>to-ld`\
`exten=>_9011.,1,dial(SIP/siptrunk/${EXTEN:1},20)`

Step 4 - Now test the solution trying to make long distance call from xlite.

Dial 913052345678

Step 5 - Try the same call from blink 

Dial 913052345678

> Please observe the log in the console. 