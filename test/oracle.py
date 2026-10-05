#!/usr/bin/env python3
# Run the reference hoon on test inputs, in one batch.
#
# Each mode is a hoon expression over the cord t, producing the tape that
# the parser prints in the matching mode: a noun in canonical form (cells
# bracketed, atoms in hex) or "err L C" / "crash".
import sys, subprocess, re, os
from esc import cord

HERE = os.path.dirname(os.path.abspath(__file__))

PR = '|=(n=* ^-(tape ?@(n ((x-co:co 1) n) :(weld "[" $(n -.n) " " $(n +.n) "]"))))'

MODES = {
    # parse, as +ream
    'x': '''=/  v  (vest [[1 1] (trip t)])
  ?~  q.v  "err {(a-co:co p.p.v)} {(a-co:co q.p.v)}"
  (pr p.u.q.v)''',
    # one +open of the parsed hoon
    'o': '''=/  r  (mule |.(~(open ap (ream t))))
  ?:  ?=(%| -.r)  "crash"
  (pr p.r)''',
    # the type of the parsed hoon against %noun, as +play
    't': '''=/  r  (mule |.((~(play ut %noun) (ream t))))
  ?:  ?=(%| -.r)  "crash"
  (pr p.r)''',
    # the mug of the type against the type of a kernel file
    'k': '''=/  r  (mule |.((~(play ut kt) (ream t))))
  ?:  ?=(%| -.r)  "crash"
  (a-co:co (mug p.r))''',
}

def run(srcs, mode='x', kernel=None):
    items = ' '.join(cord(s) for s in srcs)
    kt = cord(open(kernel, 'rb').read()) if kernel else "''"
    prog = '''=/  pr  %s
=/  kt  ?:  =('' %s)  %%noun  (~(play ut %%noun) (ream %s))
=/  one
  |=  t=@t
  ^-  tape
  %s
=/  l=(list @t)  ~[%s]
(crip (zing (turn l |=(t=@t (weld (one t) "|")))))
''' % (PR, kt, kt, MODES[mode], items)
    r = subprocess.run([os.path.join(HERE, 'urbit135'), 'eval'], input=prog.encode(),
                       capture_output=True, timeout=600)
    m = re.search(r"'(.*)'", r.stdout.decode(errors='replace'), re.S)
    if not m:
        sys.stderr.write(r.stdout.decode(errors='replace') + r.stderr.decode(errors='replace'))
        sys.exit(1)
    return m.group(1).split('|')[:-1]

if __name__ == '__main__':
    for line in run([open(f, 'rb').read() for f in sys.argv[1:]]):
        print(line)
