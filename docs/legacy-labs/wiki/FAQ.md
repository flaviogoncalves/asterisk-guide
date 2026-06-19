Frequently Asked Question

Q: My softphones are not connecting to the server\
A: Please check the network settings in the VM, make sure your adapter is in **bridged** mode. Check also if your server has a valid IP address (use ifconfig).

Q: Can't register in the remote SIP server. \
A: Please check the port. The port in the remote server is 5600 instead of 5060. I use this port to avoid having logs full of messages of people scanning the server (friendly scanner). Check also if you can ping sip.api4com.com.

register=>1040:supersecret@sip.api4com.com:5600/9999

Q: I have installed Asterisk in the Cloud (Amazon AWS or any other where the server is behind NAT) and I'm having problems. \
A: This is not a supported configuration, but it can work if you use in sip.conf

externip= _External IP of your local server_ (e.g. 54.232.1.1)\
localnet= _Local Network of Your Server_ (e.g. 172.16.0.0/255.255.0.0)

The best Cloud to run this training is one without NAT such as Digital Ocean. Not supported anyway in this training because of possible issues with NAT that can occur in your environment. 

Q: I'm receiving messages such as below [Aug 30 15:11:53] NOTICE[1836]: chan_sip.c:28749 handle_request_register: Registration from '"186" <sip:186@54.37.5.203>' failed for '185.53.91.50:5972' - Wrong password\
A: Any Asterisk server connected to the Internet in the port 5060 is a target for SIP scanners. The message above is an external person scanning your extensions to brute force passwords. Use a different port or don't allow external access. 

Q: I'm seeing the message [Oct 12 06:04:24] WARNING[2697] chan_sip.c: Retransmission timeout reached on transmission 724916584 for seqno 1 (Critical Response) -- See https://wiki.asterisk.org/wiki/display/AST/SIP+Retransmissions. What I should do. \
A: This message indicates a communication problem usually caused by NAT.  The only way to fully discover is to use >sip set debug on in the console and check the addresses to isolate the router/nat causing the problem. 

Q: Are the labs working with Asterisk 16. \
A: No, Macro does not work with the newest version, you can replace Macro with Gosub if you want. In the future I will publish new labs for Asterisk 16.

Q: Do you provide remote access and troubleshooting to the Labs. \
A: No, for a low cost training is not viable to expend hours troubleshooting local environments. My only guarantee is the labs free of bugs, if you found and report a bug I will update the instructions as soon as possible. Considering exactly the same environment where they were created and demonstrated. 

Q: Cannot disable PJSIP\
A: Edit the file modules.conf\
`noload = chan_pjsip.so`\
`noload = res_pjsip.so`
On VI to exit the screen, use :wq