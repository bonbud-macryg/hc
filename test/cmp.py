#!/usr/bin/env python3
# usage: cmp.py [-m MODE] [-k KERNEL] cases.txt [binary]
# Compare the parser against the reference on each case; cases are
# separated by lines of "%%%". MODE is a parser flag letter, see oracle.py.
import sys, os, subprocess, oracle

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
mode = 'x'
kernel = None
if args[0] == '-m':
    mode = args[1]
    args = args[2:]
if args[0] == '-k':
    kernel = args[1]
    args = args[2:]
binary = args[1] if len(args) > 1 else os.path.join(HERE, 'hp')

src = open(args[0]).read()
cases = [c[1:] if c.startswith('\n') else c for c in src.split('\n%%%')]
cases = [c for c in cases if c.strip() != '']

want = []
for i in range(0, len(cases), 200):
    want += oracle.run([c.encode() for c in cases[i:i+200]], mode, kernel)

bad = 0
for c, w in zip(cases, want):
    flags = ['-' + mode] + ([kernel] if kernel else [])
    r = subprocess.run([binary] + flags, input=c.encode(), capture_output=True, timeout=60)
    got = r.stdout.decode(errors='replace').strip()
    if r.returncode not in (0, 1):
        got = 'CRASH %d %s' % (r.returncode, r.stderr.decode()[-200:])
    if got != w:
        bad += 1
        print('=== MISMATCH:', repr(c[:300]))
        print('  want:', w[:600])
        print('  got: ', got[:600])
print('%d/%d ok' % (len(cases) - bad, len(cases)))
