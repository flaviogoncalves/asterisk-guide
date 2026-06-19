These labs are part of the training Complete Asterisk Training at www.udemy.com, 

Online Trainings
Complete Asterisk Training Coupon http://bit.ly/2E6U7fP/

Books
Complete Asterisk Training Paperback and Kindle Book https://amzn.to/2tm7TFb/
Complete Asterisk Training eBook PDF http://bit.ly/2UUebHG

In this Lab we will learn how to install Asterisk step by step

# Instructions

Step 1: Install Ubuntu 18.04 Server in a virtual machine (you may use 32 or 64bits), for the examples I have used the 32 bit version. We have used Virtual Box for this training.

you may download the image from http://releases.ubuntu.com/18.04

The Linux installation is out of the scope of this training. Linux basic knowledge is prerequisite.

Step 2: Install the dependencies

`apt-get update`\
`apt-get install bison wget openssl libssl-dev libasound2-dev libc6-dev libxml2-dev libsqlite3-dev libnewt-dev libncurses5-dev zlib1g-dev gcc g++ make perl uuid-dev git subversion libjansson-dev unixodbc-dev unixodbc-bin unixodbc autoconf libedit-dev`

Step 3: Download the source code

`cd /usr/src`\
`wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-17-current.tar.gz`\
`tar -xzvf asterisk-17-current.tar.gz`

Step 4: Compile Asterisk

**Note:** Since Ubuntu 18, it is not possible anymore to use wildcards on the command cd. So you have to pass the complete name of the Asterisk directory in this lab after decompressing the files using tar. This is a new behavior of the bash shell. Please change the lab below according to the name of the directory decompressed. It will change when the Asterisk project releases a new version (ex. asterisk-16.1.0, asterisk-16.1.1, asterisk-16.2.0....)

`cd asterisk-17-<complete_with_the_name_where_asterisk_was_decompressed>`\
`./configure`\
`make && make install && make config && make samples`

Step 5: Test if Asterisk is running

`asterisk –vvvvvvvvgc`

Step 6: Stop the Asterisk process using:

`cli>core stop now`

Step 7: To start Asterisk in background use:

`asterisk`

Step 8: To connect to the Asterisk Console running on background use

`asterisk -r`

Solving problems

The most common error on the process is to forget one of the dependencies