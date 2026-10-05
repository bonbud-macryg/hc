#!/usr/bin/env python3
# usage: finddiff.py [-s FILE | -e HOON]... FILE [-a AXIS]
# Find where the formula compiled from FILE, against %noun or against
# the subjects as hc -s and -e make them, differs from the reference:
# list the mugs of subtrees on both sides, a few levels at a time,
# descend into the first child that differs, and show both there.
import sys, os, subprocess, re, oracle
from esc import cord

HERE = os.path.dirname(os.path.abspath(__file__))
# the compiling kernel, as the reference runs it
KERNEL = os.environ.get('HC_KERNEL', os.path.expanduser('~/Desktop/urbit/pkg/arvo/sys/hoon.hoon'))
DEPTH = 10
args = sys.argv[1:]
subjects, flags = [], []
while args and args[0] in ('-s', '-e'):
    flags += args[:2]
    subjects.append(open(args[1], 'rb').read() if args[0] == '-s' else args[1].encode())
    args = args[2:]
src = open(args[0], 'rb').read()
show = int(args[2], 16) if len(args) > 2 and args[1] == '-a' else None

def ux(n):
    """n as a hoon @ux literal, dotted every four digits"""
    s = '%x' % n
    return '0x' + '.'.join(s[max(0, i-4):i] for i in range(len(s), 0, -4)[::-1])

def eval(body):
    """body over n, the subtree at axis of the reference's formula"""
    st = '~[%s]' % ' '.join(cord(s) for s in subjects) if subjects else '~'
    prog = '''=/  kt  (roll `(list @t)`%s |=([s=@t k=type] p:(~(mint ut k) %%noun (ream s))))
=/  r  (~(mint ut kt) %%noun (ream %s))
%s''' % (st, cord(src), body)
    r = subprocess.run([os.path.join(oracle.TOP, 'urbit135'), 'eval'], input=prog.encode(),
                       capture_output=True, timeout=3600)
    m = re.search(r"'(.*)'", r.stdout.decode(errors='replace'), re.S)
    if not m:
        sys.exit(r.stdout.decode(errors='replace') + r.stderr.decode(errors='replace'))
    return m.group(1)

def theirs(axis):
    out = eval('''=/  walk
  |=  [a=@ x=* d=@]
  ^-  (list [@ @])
  :-  [a (mug x)]
  ?:  |(?=(@ x) =(0 d))  ~
  (weld $(a (mul 2 a), x -.x, d (dec d)) $(a +((mul 2 a)), x +.x, d (dec d)))
=/  n  .*(q.r [0 %s])
%%-  crip
%%-  zing
%%+  turn  (walk %s n %d)
|=([a=@ m=@] "{((x-co:co 1) a)} {(a-co:co m)},")''' % (ux(axis), ux(axis), DEPTH))
    return dict((int(x.split()[0], 16), int(x.split()[1])) for x in out.split(',') if x)

def hc(*a):
    return subprocess.run([os.path.join(HERE, '..', 'hc'), '-c', KERNEL] + flags + ['-d'] + [str(x) for x in a],
                          input=src, capture_output=True, timeout=3600).stdout.decode()

def ours(axis):
    return dict((int(x.split()[0], 16), int(x.split()[1])) for x in hc('%x' % axis, DEPTH).split('\n') if x)

axis = show or 1
while not show:
    t, o = theirs(axis), ours(axis)
    if t[axis] == o.get(axis):
        print('no difference under %x' % axis)
        sys.exit()
    # follow the first differing child down as far as both listings go,
    # then list again from there, until a node differs and no child does
    a = axis
    while True:
        kids = [k for k in (2*a, 2*a+1) if k in t and k in o and t[k] != o[k]]
        if not kids:
            break
        a = kids[0]
    if a == axis:
        break
    print('differs under %x' % a, flush=True)
    axis = a
print('differs at axis %x' % axis)
# both, as far as 8 deep
PR = '''|=  [n=* d=@]
^-  tape
?:  =(0 d)  "…"
?@  n  ((x-co:co 1) n)
:(weld "[" $(n -.n, d (dec d)) " " $(n +.n, d (dec d)) "]")'''
print('want:', eval('''=/  pr  %s
=/  n  .*(q.r [0 %s])
(crip (pr n 8))''' % (PR, ux(axis))))
print('got: ', hc('%x' % axis, 0))
