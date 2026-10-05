#!/usr/bin/env python3
# usage: gdscan.py [-n N] FILE...
# Run go to definition on up to N sampled names per file and check that
# each result points at the same name. Prints failures and a summary.
import sys, os, re, random, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.environ.get('HP', os.path.join(HERE, 'hp-fast'))
EXTRA = os.environ.get('HPARGS', '').split()

args = sys.argv[1:]
n = 40
if args[0] == '-n':
    n = int(args[1])
    args = args[2:]

random.seed(1)
stats = collections.Counter()
for path in args:
    lines = open(path, errors='replace').read().split('\n')
    cands = []
    for i, line in enumerate(lines):
        code = line.split('::')[0]
        # skip ford runes, strings and cords roughly
        if code.lstrip().startswith('/'):
            continue
        for m in re.finditer(r"(?<![%a-z0-9\-'\"@$])[a-z][a-z0-9\-]*", code):
            before = code[:m.start()]
            if before.count('"') % 2 or before.count("'") % 2:
                continue
            after = code[m.end():m.end()+1]
            if after == '=':
                continue
            cands.append((i + 1, m.start() + 1, m.group()))
    random.shuffle(cands)
    for line, col, name in cands[:n]:
        r = subprocess.run([BIN, '-d', path, str(line), str(col)] + EXTRA, capture_output=True, timeout=60)
        out = r.stdout.decode().strip()
        err = r.stderr.decode().strip()
        if r.returncode > 1:
            stats['crash' if r.returncode > 2 else 'setup'] += 1
            print('CRASH %s:%d:%d %s rc=%d %s' % (os.path.basename(path), line, col, name, r.returncode, err[-100:]))
            continue
        if r.returncode == 1:
            stats[err] += 1
            print('FAIL  %s:%d:%d %-16s %s' % (os.path.basename(path), line, col, name, err))
            continue
        f, l, c = out.rsplit(':', 2)
        src = open(f, errors='replace').read().split('\n')[int(l) - 1]
        got = src[int(c) - 1:int(c) - 1 + len(name)]
        if got == name:
            stats['ok'] += 1
        else:
            stats['other name'] += 1
            print('DIFF  %s:%d:%d %-16s -> %s:%s:%s %s' % (os.path.basename(path), line, col, name,
                  os.path.basename(f), l, c, src.strip()[:60]))
total = sum(stats.values())
for k, v in stats.most_common():
    print('%5d  %s' % (v, k))
print('%5d  total' % total)
