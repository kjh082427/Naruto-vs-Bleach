#!/bin/bash
# WSL clock drift breaks github.com TLS; set the clock from GitHub's Date header (run as root)
d=$(curl -skI https://api.github.com | grep -i '^date:' | cut -d' ' -f2- | tr -d '\r')
date -s "$d"
