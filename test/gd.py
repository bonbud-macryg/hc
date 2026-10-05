#!/usr/bin/env python3
# usage: gd.py FILE LINE:COL...
# Run go to definition at each position and show the source there.
import sys, os, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1]
lines = open(path, errors='replace').read().split('\n')

def word(ls, line, col):
    s = ls[line-1]
    i = col - 1
    j = i
    while j < len(s) and (s[j].isalnum() or s[j] in '-'):
        j += 1
    return s[i:j] or s[i:i+1]

for arg in sys.argv[2:]:
    line, col = map(int, arg.split(':'))
    t = time.time()
    r = subprocess.run([os.path.join(HERE, 'hp'), '-d', path, str(line), str(col)],
                       capture_output=True, timeout=120)
    dt = time.time() - t
    out = r.stdout.decode().strip() or r.stderr.decode().strip()
    shown = out
    if r.returncode == 0:
        f, l, c = out.rsplit(':', 2)
        src = open(f, errors='replace').read().split('\n')[int(l)-1]
        shown = '%s:%s:%s  | %s' % (os.path.basename(f), l, c, src.strip()[:70])
    print('%4d:%-3d %-14s -> %s  (%.2fs)' % (line, col, word(lines, line, col), shown, dt))
