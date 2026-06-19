These labs are part of the training Complete Asterisk Training at www.udemy.com, attend using our [discounted coupon](
https://www.udemy.com/building-a-complete-pbx-with-asterisk/?couponCode=GITHUB2018)


In this lab we will configure iptables and fail2ban. The objective is to implement the recommended basic security for Asterisk block all traffic except:

# Part I - Configure IPTABLEs as a firewall for Asterisk

1 - SSH traffic from an internal network or single host
2 - SIP traffic in UDP and TCP the ports 5060 and 5080
3 - RTP traffic in the UDP range 10000 to 20000. 

Make sure you have console access to the server, you don't want to block yourself out of the system. Be careful.

Step 1 - Install the package net-persistent. 

`sudo apt-get install iptables-persistent`

Step 2 - Allow all traffic from the loopback

`sudo iptables -I INPUT -i lo -j ACCEPT`\
`sudo iptables -I OUTPUT -o lo -j ACCEPT`

Step 3 - Allow established connections

`sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT`

Step 4 - Allow SSH traffic from the network 192.168.0.0

`sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT`

Step 5 - Insert the Asterisk rules

`sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT`\
`sudo iptables -I INPUT -p udp -m udp --dport 5080 -j ACCEPT`\
`sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT`

-I means PREPEND

Step 6 - The last rule has to be a drop

`sudo iptables -A INPUT -j DROP`

-A means APPEND

> Note: Take care when maintaining new rules, you have to add rules before the DROP. Use PREPEND for new rules -I

Step 7 - Save the rules and restart iptables

`sudo iptables-save >/etc/iptables/rules.v4`\
`sudo /etc/init.d/netfilter-persistent restart`

# Part II - Installing Fail2Ban

Step 1 - Installing Fail2Ban

`sudo apt-get install fail2ban`

Step 2 - Activate fail2ban for Asterisk and SSH

`sudo vi /etc/fail2ban/jail.d/defaults-debian.conf`

Add the following lines to activate fail2ban for ssh and asterisk

`[sshd]`\
`enabled = true`\

`[asterisk]`\
`enabled=true`\

Step 3 - Restart fail2ban 

`/etc/init.d/fail2ban restart`

Step 4 - Verify

Change the secret from Zoiper an try to re-register 10 times

Using iptables -L, check if the zoiper address was included as a blocked address. 

Step 5 - Remove the address from the ban. 

`sudo fail2ban-client set asterisk unbanip 192.168.0.5`

Note: In the command replace 192.168.0.5 by the ip address of your phone



