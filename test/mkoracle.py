#!/usr/bin/env python3
# Build test/urbit135: a copy of an urbit binary whose embedded ivory pill
# is replaced, so that `urbit135 eval` runs the reference parser.
#
# usage: mkoracle.py URBIT OLD-IVORY NEW-IVORY
#   URBIT      urbit binary, e.g. ~/Downloads/urbit
#   OLD-IVORY  the ivory pill embedded in URBIT, e.g. ~/Desktop/urbit/bin/ivory.pill
#   NEW-IVORY  the pill to embed, e.g. ~/Downloads/ivory.pill (%135)
#
# The pill length is stored as a 32-bit word following the pill bytes.
import os, struct, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
urbit, old, new = (open(os.path.expanduser(f), 'rb').read() for f in sys.argv[1:4])
b = bytearray(urbit)

off = b.find(old)
if off < 0:
    sys.exit('old ivory pill not found in binary')
if len(new) > len(old):
    sys.exit('new ivory pill is larger than the embedded one')

hits = [i for i in range(off + len(old), off + len(old) + 64)
        if b[i:i+4] == struct.pack('<I', len(old))]
if len(hits) != 1:
    sys.exit('pill length word not found')

b[off:off+len(old)] = new + bytes(len(old) - len(new))
b[hits[0]:hits[0]+4] = struct.pack('<I', len(new))

out = os.path.join(here, 'urbit135')
open(out, 'wb').write(b)
os.chmod(out, 0o755)
if sys.platform == 'darwin':
    subprocess.run(['codesign', '-s', '-', '-f', out], check=True, capture_output=True)
print(out)
