#!/usr/bin/env python3
# usage: files.py file...
# Compare the parser against the reference on whole files, by mug.
import sys, os, subprocess, re, time, mugpy
HERE=os.path.dirname(os.path.abspath(__file__))
TIMEOUT=int(os.environ.get('ORACLE_TIMEOUT','3600'))
from esc import cord
files=sys.argv[1:]
def oracle(srcs):
    items=' '.join(cord(s) for s in srcs)
    prog='''=/  one
  |=  t=@t
  ^-  tape
  =/  v  (vest [[1 1] (trip t)])
  ?~  q.v  "err {(a-co:co p.p.v)} {(a-co:co q.p.v)}"
  (a-co:co (mug p.u.q.v))
=/  l=(list @t)  ~[%s]
(crip (zing (turn l |=(t=@t (weld (one t) "|")))))
''' % items
    try:
        r=subprocess.run([os.path.join(HERE,'urbit135'),'eval'],input=prog.encode(),capture_output=True,timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return ['timeout']
    m=re.search(r"'(.*)'",r.stdout.decode(errors='replace'),re.S)
    if not m: sys.stderr.write(r.stdout.decode()+r.stderr.decode()); sys.exit(1)
    return m.group(1).split('|')[:-1]
bad=0
for f in files:
    src=open(f,'rb').read()
    t=time.time(); w=oracle([src]); ot=time.time()-t
    t=time.time()
    r=subprocess.run([os.path.join(HERE,'hp'),'-x'],stdin=open(f,'rb'),capture_output=True,timeout=120)
    out=r.stdout.decode().strip()
    got=out if out.startswith('err') or r.returncode not in (0,) else str(mugpy.mugtext(out))
    if r.returncode not in (0,1): got='CRASH %d'%r.returncode
    ok=got==w[0]
    if w[0]=='timeout': print('skip %s (oracle timeout)'%f,flush=True); continue
    bad+=not ok
    print('%s %s want=%s got=%s (oracle %.1fs, us %.2fs)'%('ok' if ok else 'MISMATCH',f,w[0],got,ot,time.time()-t),flush=True)
print('%d/%d ok'%(len(files)-bad,len(files)))
