# Hoon literals for test inputs.

def esc(b):
    """bytes as a single-quoted cord literal"""
    out = []
    for x in b:
        c = chr(x)
        if c == '\\': out.append('\\\\')
        elif c == "'": out.append("\\'")
        elif x < 32 or x >= 127: out.append('\\%02x' % x)
        else: out.append(c)
    return "'" + ''.join(out) + "'"

def cord(b, n=64):
    """bytes as a cord expression that's fast to parse: hoon parses a long
    cord literal in quadratic time, so join short ones with +rap"""
    if not b:
        return "''"
    parts = [esc(b[i:i+n]) for i in range(0, len(b), n)]
    return "(rap 3 `(list @)`~[%s])" % ' '.join(parts)
