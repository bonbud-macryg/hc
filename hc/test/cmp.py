#!/usr/bin/env python3
# usage: cmp.py [-m MODE] [-k KERNEL] cases.txt [binary]
# Compare the compiler against the reference on each case; cases are
# separated by lines of "%%%". MODE is a compiler flag letter, see
# oracle.py.
import sys, os, subprocess, oracle

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
mode = 'n'
kernel = None
if args[0] == '-m':
    mode = args[1]
    args = args[2:]
if args[0] == '-k':
    kernel = args[1]
    args = args[2:]
binary = args[1] if len(args) > 1 else os.path.join(HERE, '..', 'hc-debug')
# the compiling kernel, as the reference runs it
KERNEL = os.environ.get('HC_KERNEL', os.path.expanduser('~/Desktop/urbit/pkg/arvo/sys/hoon.hoon'))

src = open(args[0]).read()
cases = [c[1:] if c.startswith('\n') else c for c in src.split('\n%%%')]
cases = [c for c in cases if c.strip() != '']

want = []
for i in range(0, len(cases), 200):
    want += oracle.run([c.encode() for c in cases[i:i+200]], mode, kernel)

flags = ['-c', KERNEL, '-' + mode] + ([kernel] if kernel else [])

def one(c):
    r = subprocess.run([binary] + flags, input=c.encode(), capture_output=True, timeout=600)
    got = r.stdout.decode(errors='replace').strip()
    if r.returncode not in (0, 1):
        got = 'CRASH %d %s' % (r.returncode, r.stderr.decode()[-200:])
    return got

# all at once, or one by one if that dies
r = subprocess.run([binary, '-b'] + flags, input='\n%%%\n'.join(cases).encode(),
                   capture_output=True, timeout=3600)
gots = r.stdout.decode(errors='replace').split('\n')[:-1]
if r.returncode not in (0, 1) or len(gots) != len(cases):
    gots = [one(c) for c in cases]

bad = 0
for c, w, got in zip(cases, want, gots):
    if got != w:
        bad += 1
        print('=== MISMATCH:', repr(c[:300]))
        print('  want:', w[:600])
        print('  got: ', got[:600])
print('%d/%d ok' % (len(cases) - bad, len(cases)))
