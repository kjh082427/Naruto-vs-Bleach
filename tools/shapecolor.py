"""Find and rewrite the colours of vector shapes (DefineShape 1-4 and DefineMorphShape 1-2): solid fills, gradient
stops and line colours, including the style arrays that StyleChange records bring in.

usage: python3 -I tools/shapecolor.py <swf> [shape id ...]   -> shape id, kind, colours (hex)
Library: color_slots(tag_type, body) -> [(offset, size)], recolor(tag_type, body, fn) -> new body
         (fn((r, g, b)) -> (r, g, b); alpha is kept)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swfnames import Bits, skip_matrix  # noqa: E402

SHAPE_VERSION = {2: 1, 22: 2, 32: 3, 83: 4}
MORPH = {46: 1, 84: 2}


def _rect_end(d, q):
    n = d[q] >> 3
    return q + (5 + 4 * n + 7) // 8


def _matrix_end(d, q):
    return skip_matrix(Bits(d, q))[0]


def _fill(d, q, ver, out, morph=False):
    t = d[q]
    q += 1
    csize = 4 if (ver >= 3 or morph) else 3
    reps = 2 if morph else 1
    if t == 0x00:
        for _ in range(reps):
            out.append((q, csize))
            q += csize
    elif t in (0x10, 0x12, 0x13):
        for _ in range(reps):
            q = _matrix_end(d, q)
        n = d[q] & 0x0F
        q += 1
        for _ in range(n):
            for _ in range(reps):
                q += 1  # ratio
                out.append((q, csize))
                q += csize
        if t == 0x13:
            q += 2 * reps
    elif 0x40 <= t <= 0x43:
        q += 2
        for _ in range(reps):
            q = _matrix_end(d, q)
    else:
        raise ValueError(f'fill type {t:#x}')
    return q


def _count(d, q, extended=True):
    n = d[q]
    q += 1
    if n == 0xFF and extended:
        n = d[q] | d[q + 1] << 8
        q += 2
    return n, q


def _fills(d, q, ver, out, morph=False):
    n, q = _count(d, q, ver >= 2 or morph)
    for _ in range(n):
        q = _fill(d, q, ver, out, morph)
    return q


def _lines(d, q, ver, out, morph=False, morph2=False):
    n, q = _count(d, q)
    for _ in range(n):
        q += 4 if morph else 2  # width (start/end widths for morphs)
        if ver == 4 or morph2:
            f1 = d[q]
            q += 2
            if (f1 >> 4) & 3 == 2:
                q += 2  # miter limit
            if (f1 >> 3) & 1:
                q = _fill(d, q, ver, out, morph)
                continue
        for _ in range(2 if morph else 1):
            size = 4 if (ver >= 3 or morph) else 3
            out.append((q, size))
            q += size
    return q


def _records(d, q, ver, out):
    b = Bits(d, q)
    nfb, nlb = b.ub(4), b.ub(4)
    while True:
        if b.ub(1) == 0:
            flags = b.ub(5)
            if flags == 0:
                return
            if flags & 1:
                n = b.ub(5)
                b.sb(n), b.sb(n)
            if flags & 2:
                b.ub(nfb)
            if flags & 4:
                b.ub(nfb)
            if flags & 8:
                b.ub(nlb)
            if flags & 16:
                q = _lines(d, _fills(d, b.align(), ver, out), ver, out)
                b = Bits(d, q)
                nfb, nlb = b.ub(4), b.ub(4)
        elif b.ub(1):  # straight edge
            n = b.ub(4) + 2
            if b.ub(1):
                b.sb(n), b.sb(n)
            else:
                b.ub(1), b.sb(n)
        else:  # curved edge
            n = b.ub(4) + 2
            for _ in range(4):
                b.sb(n)


def color_slots(tag_type, body):
    """[(byte offset, 3 or 4)] of every colour in a shape / morph shape body."""
    out = []
    d = body
    if tag_type in SHAPE_VERSION:
        ver = SHAPE_VERSION[tag_type]
        q = _rect_end(d, 2)
        if ver == 4:
            q = _rect_end(d, q) + 1
        q = _lines(d, _fills(d, q, ver, out), ver, out)
        _records(d, q, ver, out)
    elif tag_type in MORPH:
        m2 = MORPH[tag_type] == 2
        q = _rect_end(d, _rect_end(d, 2))
        if m2:
            q = _rect_end(d, _rect_end(d, q)) + 1
        q += 4  # offset to end edges
        q = _lines(d, _fills(d, q, 3, out, morph=True), 3, out, morph=True, morph2=m2)
    return out


def recolor(tag_type, body, fn):
    body = bytearray(body)
    for q, _ in color_slots(tag_type, body):
        body[q:q + 3] = bytes(fn(tuple(body[q:q + 3])))
    return bytes(body)


def main():
    from swfpatch import Swf
    swf = Swf.load(sys.argv[1])
    want = {int(a) for a in sys.argv[2:]}
    for t in swf.tags:
        if t.type in SHAPE_VERSION or t.type in MORPH:
            sid = t.body[0] | t.body[1] << 8
            if want and sid not in want:
                continue
            slots = color_slots(t.type, t.body)
            cols = sorted({bytes(t.body[q:q + 3]).hex() for q, _ in slots})
            print(sid, 'morph' if t.type in MORPH else f'shape{SHAPE_VERSION[t.type]}', ' '.join(cols))


if __name__ == '__main__':
    main()
