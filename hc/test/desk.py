#!/usr/bin/env python3
# usage: desk.py [-s FILE | -S FILE | -e HOON]... DESK file...
# Build desk files through ford, with hc -D and with the reference, and
# compare the mugs of their types and formulas. The reference is clay's
# own ford: the subjects are built as vases, values and all, clay.hoon
# is compiled against the last of them as arvo compiles a vane, and its
# +ford:fusion, given the desk's .hoon and .txt files as pages, builds
# each file's subject with +prelude, and the file's body is compiled
# against that.
# Files are given relative to DESK, like app/dojo.hoon.
import sys, os, re, subprocess, time, oracle
from esc import cord, esc

HERE = os.path.dirname(os.path.abspath(__file__))
KERNEL = os.environ.get('HC_KERNEL', os.path.expanduser('~/Desktop/urbit/pkg/arvo/sys/hoon.hoon'))
CLAY = os.path.join(os.path.dirname(KERNEL), 'vane', 'clay.hoon')
BATCH = int(os.environ.get('ORACLE_BATCH', '40'))

def deskpath(rel):
    """app/foo.hoon as ['app', 'foo', 'hoon']"""
    head, ext = rel.rsplit('.', 1)
    return head.split('/') + [ext]

def hoonpath(pax):
    """a path as hoon, a list of cords: knots like a.hoon aren't
    allowed in /a/b"""
    return '`path`~[%s]' % ' '.join(esc(k.encode()) for k in pax)

args = sys.argv[1:]
# each subject as [path text], the path ~ but with -S, where it's the
# file's path from its sys directory and the text is parsed with +rain
subjects, flags = [], []
while args and args[0] in ('-s', '-S', '-e'):
    flags += args[:2]
    if args[0] == '-e':
        subjects.append(('~', args[1].encode()))
    else:
        pax = '~'
        if args[0] == '-S':
            parts = os.path.abspath(args[1]).split('/')
            rel = parts[len(parts) - 1 - parts[::-1].index('sys'):]
            pax = hoonpath(deskpath('/'.join(rel)))
        subjects.append((pax, open(args[1], 'rb').read()))
    args = args[2:]
desk, files = args[0], args[1:]

# every .hoon and .txt file in the desk as clay's pages
pages = []
for root, dirs, names in os.walk(desk, followlinks=True):
    for n in sorted(names):
        full = os.path.join(root, n)
        rel = os.path.relpath(full, desk)
        if not os.path.isfile(full):
            continue
        if n.endswith('.hoon'):
            pages.append('[%s [%%& %%hoon %s]]' % (hoonpath(deskpath(rel)), cord(open(full, 'rb').read())))
        elif n.endswith('.txt'):
            pages.append('[%s [%%& %%txt (to-wain:format %s)]]' % (hoonpath(deskpath(rel)), cord(open(full, 'rb').read())))

src = open(CLAY).read()
start = src.index('++  parsing-rules')
rules = src[start:src.index('--  =>\n~%  %clay  +', start)]

PROG = '''=/  zv=vase
  %+  roll  `(list [path @t])`@SUBJECTS@
  |=  [[p=path s=@t] v=vase]
  (slap v ?~(p (ream s) (rain p s)))
=/  cv=vase  (slam (slap zv (rain /sys/vane/clay/hoon @CLAY@)) !>(~zod))
=/  files=(map path (each page:clay lobe:clay))
  (malt `(list [path (each page:clay lobe:clay)])`@FILES@)
=/  fc=vase
  %+  slam  (slap cv (ream 'ford:fusion'))
  !>([files=files file-store=*(map lobe:clay page:clay) verb=0])
=/  pre=vase  (slap fc (ream 'prelude'))
=,  clay
=>  |%
@RULES@
    ++  top
      |=  pax=path
      ^-  tape
      =/  fil  (~(got by files) pax)
      ?>  ?=(%& -.fil)
      =/  [=hair res=(unit [=pile:clay =nail])]
        ((pile-rule pax) [1 1] (trip ;;(@t q.p.fil)))
      ?~  res  "err {(a-co:co p.hair)} {(a-co:co q.hair)}"
      =/  r
        %-  mule  |.
        =/  tus=vase  !<(vase (slam pre !>(pax)))
        (~(mint ut p.tus) %noun hoon.pile.u.res)
      ?:  ?=(%| -.r)  "crash"
      "{(a-co:co (mug ~(burp ut p.p.r)))} {(a-co:co (mug q.p.r))}"
    --
(crip (zing (turn `(list path)`@TOPS@ |=(p=path (weld (top p) "|")))))
'''

def theirs(tops):
    st = '~[%s]' % ' '.join('[%s %s]' % (p, cord(s)) for p, s in subjects) if subjects else '~'
    prog = (PROG.replace('@SUBJECTS@', st).replace('@CLAY@', cord(open(CLAY, 'rb').read()))
                .replace('@FILES@', '~[%s]' % ' '.join(pages)).replace('@RULES@', rules)
                .replace('@TOPS@', '~[%s]' % ' '.join(hoonpath(p) for p in tops)))
    r = subprocess.run([os.path.join(oracle.TOP, 'urbit135'), 'eval'], input=prog.encode(),
                       capture_output=True, timeout=7200)
    m = re.search(r"'(.*)'", r.stdout.decode(errors='replace'), re.S)
    if not m:
        sys.stderr.write(r.stdout.decode(errors='replace')[-3000:] + r.stderr.decode(errors='replace')[-2000:])
        return ['oracle failed'] * len(tops)
    return m.group(1).split('|')[:-1]

tops = [deskpath(f) for f in files]
want = []
for i in range(0, len(tops), BATCH):
    t = time.time()
    want += theirs(tops[i:i+BATCH])
    print('oracle: %d files in %.1fs' % (len(tops[i:i+BATCH]), time.time() - t), file=sys.stderr, flush=True)

r = subprocess.run([os.path.join(HERE, '..', 'hc'), '-c', KERNEL] + flags + ['-D', desk, '-b', '-f'],
                   input='\n'.join(files).encode(), capture_output=True, timeout=7200)
got = r.stdout.decode().split('\n')[:-1]
if len(got) != len(tops):
    sys.stderr.write(r.stderr.decode()[-2000:])
    got += ['CRASH'] * (len(tops) - len(got))
bad = 0
for f, w, g in zip(files, want, got):
    bad += g != w
    print('%s %s want=%s got=%s' % ('ok' if g == w else 'MISMATCH', f, w, g), flush=True)
print('%d/%d ok' % (len(files) - bad, len(files)))
