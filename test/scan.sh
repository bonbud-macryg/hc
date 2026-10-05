#!/bin/sh
# Sample go to definition over the kernel and vanes, then over 60 desk
# files, and summarize. Slow, a few minutes.
cd "$(dirname "$0")"
S=$HOME/Desktop/urbit/pkg/arvo/sys
./gdscan.py -n 40 $S/*.hoon $S/vane/*.hoon 2>&1 | tail -5
find ~/Desktop/urbit/pkg/arvo ~/Desktop/urbit/pkg/landscape -type f -name '*.hoon' -not -path '*/sys/*' | python3 -c "
import sys,random; random.seed(7); l=sys.stdin.read().split(); random.shuffle(l); print(' '.join(l[:60]))" > sample.lst
./gdscan.py -n 20 $(cat sample.lst) 2>&1 | tail -4
rm sample.lst
