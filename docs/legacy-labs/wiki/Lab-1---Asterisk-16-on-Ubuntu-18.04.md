These labs are part of the training Complete Asterisk Training at [voip.school](https://www.voip.school)

In this Lab we will learn how to install Asterisk step by step.

# Instructions

Step 1: Install Ubuntu 18.04 Server in a virtual machine (you may use 32 or 64bits), for the examples I have used the 32 bit version. We have used Virtual Box for this training.

you may download the image from http://releases.ubuntu.com/18.04

The Linux installation is out of the scope of this training. Linux basic knowledge is prerequisite.

Step 2: Install the dependencies

`apt-get update`\
`apt-get install bison wget openssl libssl-dev libasound2-dev libc6-dev libxml2-dev libsqlite3-dev libnewt-dev libncurses5-dev zlib1g-dev gcc g++ make perl uuid-dev git subversion unixodbc-dev unixodbc-bin unixodbc autoconf libedit-dev`

Step 3: Download the source code

`cd /usr/src`\
`wget https://downloads.asterisk.org/pub/telephony/asterisk/old-releases/asterisk-16.30.0.tar.gz`\
`tar -xzvf asterisk-16.30.0.tar.gz`

Step 4: Compile Asterisk

**Note:** Since Ubuntu 18, it is not possible anymore to use wildcards on the command cd. So you have to pass the complete name of the Asterisk directory in this lab after decompressing the files using tar. This is a new behavior of the bash shell. Please change the lab below according to the name of the directory decompressed. It will change when the Asterisk project releases a new version (ex. asterisk-16.1.0, asterisk-16.1.1, asterisk-16.2.0....)

`cd asterisk-16-<complete_with_the_name_where_asterisk_was_decompressed>`\
`./configure --with-jansson-bundled`\

Step 5 (optional): Add the application Macro (Useful if you will follow the video rather then the text labs)

`make menuselect`

Select the application **macro** to compile.

![image](https://user-images.githubusercontent.com/4958202/196203328-25eaa00d-33b9-49f7-a11d-0d242205eb5c.png)

Step 5a (optional): If you are going to use Asterisk 18, 19, please add the channel driver chan_sip. For Asterisk 16 it is installed by default. 

![image](https://user-images.githubusercontent.com/4958202/196235765-7645c58b-51a0-4aff-8320-94d38e9c2ec3.png)

Step 6: Compile Asterisk

`make && make install && make config && make samples`

Step 7: Test if Asterisk is running

`asterisk –vvvvvvvvgc`

Step 8: Stop the Asterisk process using:

`cli>core stop now`

Step 9: To start Asterisk in background use:

`asterisk`

Step 10: To connect to the Asterisk Console running on background use

`asterisk -r`

Solving problems

The most common error on the process is to forget one of the dependencies