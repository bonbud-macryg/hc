#!/usr/bin/env python3
# usage: files.py [-s FILE | -e HOON]... file...
# Compile whole files against %noun, or against the type of each subject
# compiled in turn as hc -s and -e do, and compare the mugs of the type
# and the formula against the reference, all files in one batch.
import sys, os, subprocess, time, oracle

HERE = os.path.dirname(os.path.abspath(__file__))
# the compiling kernel, as the reference runs it
KERNEL = os.environ.get('HC_KERNEL', os.path.expanduser('~/Desktop/urbit/pkg/arvo/sys/hoon.hoon'))
TIMEOUT = int(os.environ.get('ORACLE_TIMEOUT', '3600'))
args = sys.argv[1:]
subjects = []
flags = []
while args and args[0] in ('-s', '-e'):
    flags += args[:2]
    subjects.append(open(args[1], 'rb').read() if args[0] == '-s' else args[1].encode())
    args = args[2:]
# the reference, in batches, as each run compiles the subjects again
want = {}
BATCH = int(os.environ.get('ORACLE_BATCH', '12'))
for i in range(0, len(args), BATCH):
    chunk = args[i:i+BATCH]
    t = time.time()
    try:
        ws = oracle.run([open(f, 'rb').read() for f in chunk], 'f', timeout=TIMEOUT, subjects=subjects)
    except subprocess.TimeoutExpired:
        ws = ['timeout'] * len(chunk)
    for f, w in zip(chunk, ws):
        want[f] = w
    print('oracle: %d files in %.1fs' % (len(chunk), time.time() - t), file=sys.stderr, flush=True)
bad = skip = 0
for f in args:
    w = want[f]
    if w == 'timeout':
        print('skip %s (oracle timeout)' % f, flush=True)
        skip += 1
        continue
    t = time.time()
    r = subprocess.run([os.path.join(HERE, '..', 'hc'), '-c', KERNEL] + flags + ['-f'], stdin=open(f, 'rb'),
                       capture_output=True, timeout=TIMEOUT)
    got = r.stdout.decode().strip()
    if r.returncode not in (0, 1):
        got = 'CRASH %d' % r.returncode
    bad += got != w
    print('%s %s want=%s got=%s (us %.2fs)'
          % ('ok' if got == w else 'MISMATCH', f, w, got, time.time() - t), flush=True)
print('%d/%d ok' % (len(args) - skip - bad, len(args) - skip))
