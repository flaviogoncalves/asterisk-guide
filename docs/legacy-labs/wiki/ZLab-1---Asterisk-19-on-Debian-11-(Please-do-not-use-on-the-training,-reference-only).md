These labs are part of the training Complete Asterisk Training at www.udemy.com, 

Online Trainings
Complete Asterisk Training Coupon http://bit.ly/2E6U7fP/

Books
Complete Asterisk Training Paperback and Kindle Book https://amzn.to/2tm7TFb/
Complete Asterisk Training eBook PDF http://bit.ly/2UUebHG

In this Lab we will learn how to install Asterisk step by step

# Instructions

Step 1: Install Debian 11 in a virtual machine (you may use 32 or 64bits), for the examples I have used the 32 bit version. We have used Virtual Box for this training.

The Linux installation is out of the scope of this training. Linux basic knowledge is prerequisite.

Step 2: Install the dependencies and a few useful utilities

`apt-get update`\
`apt-get install bison wget openssl libssl-dev libasound2-dev libc6-dev libxml2-dev libsqlite3-dev libnewt-dev libncurses5-dev zlib1g-dev gcc g++ make perl uuid-dev git subversion libjansson-dev unixodbc-dev unixodbc autoconf libedit-dev locate sngrep`

Step 3: Download the source code

`cd /usr/src`\
`wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-19-current.tar.gz`\
`tar -xzvf asterisk-19-current.tar.gz`

Step 4: Install chan_sip, it is deprecated, but still widely used. 

Use the command:

`cd asterisk-19-<complete_with_the_name_where_asterisk_was_decompressed>`\
`./configure`\
`make menuselect`

and select the channel chan_sip in the menu. 

![image](https://user-images.githubusercontent.com/4958202/179405377-2da7b5b2-4cbe-4424-83b8-36b8e4740d16.png)

Step 5: Compile Asterisk

`make && make install && make config && make samples`

Step 6: Test if Asterisk is running

`/usr/sbin/asterisk –vvvvvvvvgc`

Step 6: Stop the Asterisk process using:

`cli>core stop now`

Step 7: To start Asterisk in background use:

`/usr/sbin/asterisk`

Step 8: To connect to the Asterisk Console running on background use

`/usr/sbin/asterisk -r`

Solving problems

The most common error on the process is to forget one of the dependencies