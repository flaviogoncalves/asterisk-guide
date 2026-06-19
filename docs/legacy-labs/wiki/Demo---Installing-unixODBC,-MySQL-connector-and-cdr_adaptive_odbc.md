These labs are part of the training Complete Asterisk Training at www.udemy.com, attend using our [discounted coupon](
https://www.udemy.com/building-a-complete-pbx-with-asterisk/?couponCode=GITHUB2018)

This is not a lab, you are not required to complete it. This lab requires advanced knowledge in Linux and there are many things that can go wrong. A linux geek will complete it easily. However, It took me almost an hour to execute it for the first time. So unless you have the required knowledge and patience let it as just a demo. If you require CDRs sent to ODBC and this lab don't work for you, hire an Linux expert to execute it. 

Step 1: Install MySQL Server

 `apt-get install mysql-server`

 Provide a password for mysql "qsasterisk". You can change the password if you want, but change the lab accordingly.  

Step 2: Install MySQL connector for ODBC
 
`wget https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.11-linux-ubuntu16.04-x86-32bit.tar.gz`


`tar -xzvf mysql-connector-odbc-8.0.11-linux-ubuntu16.04-x86-32bit.tar.gz`\
`cd mysql-connector-odbc-8.0.11-linux-ubuntu16.04-x86-32bit`\
`cp libmyodbc8a.so /usr/lib/i386-linux-gnu/odbc/`

Step 3: Edit odbcinst.init and install the drivers

`[MySQL]`\
`Description = ODBC for MySQL`\
`Driver = /usr/lib/i386-linux-gnu/odbc/libmyodbc8a.so`\
`Setup = /usr/lib/i386-linux-gnu/odbc/libodbcmyS.so`\
`FileUsage = 1`

Step 4: Edit /etc/odbc.ini and create the dsn

`[astcdr]`\
`Description           = MySQL connection to  database`\
`Driver                = MySQL`\
`Database              = cdr`\
`Server                = localhost`\
`User                  = root`\
`Password              = qsasterisk`\
`Port                  = 3306`\
`Socket                = /var/run/mysqld/mysqld.sock`

Step 5: Create the database cdr

`mysqladmin -uroot -p create cdr`

use qsasterisk as the password. 

Step 7: Configure res_dbc.conf

Add to the end of the file 

`[astcdr]`\
`enabled => yes`\
`dsn => astcdr`\
`username => root`\
`password => qsasterisk`\
`pre-connect => yes`

Step 8: Verify in the Asterisk console if you have Adaptive ODBC as an option

After restarting Asterisk, 

CLI>cdr show status

qsasterisk*CLI> show cdr status
No such command 'show cdr status' (type 'core show help show cdr' for other possible commands)
qsasterisk*CLI> cdr show status

`Call Detail Record (CDR) settings`\
`----------------------------------`\
  `Logging:                    Enabled`\
  `Mode:                       Simple`\
  `Log unanswered calls:       No`\
  `Log congestion:             No`

`* Registered Backends`\
  `-------------------`\
    `cdr-custom`\
    `csv`\
    `cdr_manager (suspended)`\
    `**Adaptive ODBC**`

Step 9: Verify the ODBC conenction 

`CLI>odbc show all `\
`ODBC DSN Settings`\
`-----------------`\

  `Name:   astcdr`\
  `DSN:    astcdr`\
    `Number of active connections: 1 (out of 1)`

Step 10 - Create the database schema

root@qsasterisk:/usr/src/asterisk-15.4.1/contrib/realtime/mysql# mysql -u root -p cdr <mysql_cdr.sql

Step 11 - Check if cdr_adaptive_odbc.conf is like below

`[cdr]`
`connection=astcdr`
`table=cdr`
`;alias start => calldate`

Step 12 - Make some calls and check if the database is filled. 

`mysql -u root -p cdr`