#!/usr/bin/env python3
# usage: lspscan.py [-n N] FILE...
# Ask one language server session for definitions of sampled names in
# the files, interleaved, and check each answer against a fresh run of
# the command line. Catches state leaking between requests.
import sys, os, re, json, random, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.environ.get('HP', os.path.join(HERE, 'hp-fast'))
args = sys.argv[1:]
n = 10
if args[0] == '-n':
    n = int(args[1])
    args = args[2:]

random.seed(3)
queries = []
for path in args:
    lines = open(path, errors='replace').read().split('\n')
    cands = []
    for i, line in enumerate(lines):
        code = line.split('::')[0]
        if code.lstrip().startswith('/'):
            continue
        for m in re.finditer(r"(?<![%a-z0-9\-'\"@$])[a-z][a-z0-9\-]*", code):
            if not line.isascii():
                continue
            cands.append((os.path.realpath(path), i + 1, m.start() + 1))
    random.shuffle(cands)
    queries += cands[:n]
random.shuffle(queries)

proc = subprocess.Popen([BIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
def request(i, method, params):
    body = json.dumps({'jsonrpc': '2.0', 'id': i, 'method': method, 'params': params}).encode()
    proc.stdin.write(b'Content-Length: %d\r\n\r\n' % len(body) + body)
    proc.stdin.flush()
    k = 0
    while True:
        l = proc.stdout.readline().strip()
        if not l:
            break
        k = int(l.split(b':', 1)[1])
    return json.loads(proc.stdout.read(k))

request(0, 'initialize', {})
bad = 0
for i, (path, line, col) in enumerate(queries):
    r = request(i + 1, 'textDocument/definition',
                {'textDocument': {'uri': 'file://' + path}, 'position': {'line': line - 1, 'character': col - 1}})
    res = r['result']
    got = None if res is None else '%s:%d:%d' % (res['uri'][7:], res['range']['start']['line'] + 1,
                                                 res['range']['start']['character'] + 1)
    c = subprocess.run([BIN, '-d', path, str(line), str(col)], capture_output=True, timeout=60)
    want = c.stdout.decode().strip() if c.returncode == 0 else None
    if got != want:
        bad += 1
        print('DIFF %s:%d:%d\n  lsp %s\n  cli %s' % (os.path.basename(path), line, col, got, want))
request(10**6, 'shutdown', None)
print('%d/%d same' % (len(queries) - bad, len(queries)))
