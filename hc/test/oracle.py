#!/usr/bin/env python3
# Run the reference compiler on test inputs, in one batch, with the
# oracle from ../../test (see mkoracle.py there).
#
# Each mode is a hoon expression over the cord t, producing the tape the
# compiler prints in the matching mode: nouns in canonical form (cells
# bracketed, atoms in hex), mugs in decimal, or "err L C" / "crash".
import sys, subprocess, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.join(HERE, '..', '..', 'test')
sys.path.insert(0, TOP)
from esc import cord

PR = '|=(n=* ^-(tape ?@(n ((x-co:co 1) n) :(weld "[" $(n -.n) " " $(n +.n) "]"))))'

PARSE = '''=/  v  (vest [[1 1] (trip t)])
  ?~  q.v  "err {(a-co:co p.p.v)} {(a-co:co q.p.v)}"
  =/  r  (mule |.((~(mint ut kt) %noun p.u.q.v)))
  ?:  ?=(%| -.r)  "crash"
  '''

MODES = {
    # the type, after +burp, and the formula
    'm': PARSE + '(pr [~(burp ut p.p.r) q.p.r])',
    # the formula
    'n': PARSE + '(pr q.p.r)',
    # mugs of the type and the formula, against a kernel's type, or %noun
    'k': PARSE + '"{(a-co:co (mug ~(burp ut p.p.r)))} {(a-co:co (mug q.p.r))}"',
}
MODES['f'] = MODES['k']

def run(srcs, mode='n', kernel=None, timeout=600, subjects=()):
    """subjects are sources, each compiled against the last one's type,
    as hc -s and -e do"""
    items = ' '.join(cord(s) for s in srcs)
    kt = cord(open(kernel, 'rb').read()) if kernel else "''"
    st = '~[%s]' % ' '.join(cord(s) for s in subjects) if subjects else '~'
    prog = '''=/  pr  %s
=/  kt  ?:  =('' %s)  %%noun  (~(play ut %%noun) (ream %s))
=.  kt  (roll `(list @t)`%s |=([s=@t k=_kt] p:(~(mint ut k) %%noun (ream s))))
=/  one
  |=  t=@t
  ^-  tape
  %s
=/  l=(list @t)  ~[%s]
(crip (zing (turn l |=(t=@t (weld (one t) "|")))))
''' % (PR, kt, kt, st, MODES[mode], items)
    r = subprocess.run([os.path.join(TOP, 'urbit135'), 'eval'], input=prog.encode(),
                       capture_output=True, timeout=timeout)
    m = re.search(r"'(.*)'", r.stdout.decode(errors='replace'), re.S)
    if not m:
        sys.stderr.write(r.stdout.decode(errors='replace') + r.stderr.decode(errors='replace'))
        sys.exit(1)
    return m.group(1).split('|')[:-1]

if __name__ == '__main__':
    mode = 'n'
    args = sys.argv[1:]
    if args and args[0] == '-m':
        mode, args = args[1], args[2:]
    for line in run([open(f, 'rb').read() for f in args], mode):
        print(line)
