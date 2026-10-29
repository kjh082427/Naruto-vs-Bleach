"""Tag-level diff of two SWFs (recurses into DefineSprite).

usage: python3 -I swfdiff.py a.swf b.swf
"""
import struct
import sys
import zlib


def load(path):
    d = open(path, 'rb').read()
    if d[:3] == b'CWS':
        d = d[:8] + zlib.decompress(d[8:])
    nbits = d[8] >> 3
    return d, 8 + (5 + 4 * nbits + 7) // 8 + 4


def tags(d, p, end):
    out = []
    while p < end:
        h = struct.unpack_from('<H', d, p)[0]; p += 2
        t, l = h >> 6, h & 63
        if l == 63:
            l = struct.unpack_from('<I', d, p)[0]; p += 4
        body = d[p:p + l]
        if t == 39:
            sid = struct.unpack_from('<H', body)[0]
            out.append((t, body[:4], tags(body, 4, len(body))))
        else:
            out.append((t, body, None))
        p += l
        if t == 0:
            break
    return out


def cmp(a, b, path='root'):
    diffs = 0
    if len(a) != len(b):
        print(f'{path}: tag count {len(a)} vs {len(b)}')
    for i, (x, y) in enumerate(zip(a, b)):
        if x[0] != y[0]:
            print(f'{path}[{i}]: type {x[0]} vs {y[0]}'); diffs += 1; continue
        if x[2] is not None:
            diffs += cmp(x[2], y[2], f'{path}/sprite{struct.unpack_from("<H", x[1])[0]}')
        elif x[1] != y[1]:
            cid = struct.unpack_from('<H', x[1])[0] if len(x[1]) >= 2 else -1
            print(f'{path}[{i}]: tag {x[0]} (first u16 {cid}) len {len(x[1])} vs {len(y[1])}'); diffs += 1
    return diffs


a, pa = load(sys.argv[1]); b, pb = load(sys.argv[2])
print('header', a[3:pa] == b[3:pb])
print('diffs', cmp(tags(a, pa, len(a)), tags(b, pb, len(b))))
