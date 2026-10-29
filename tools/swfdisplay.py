"""Simulate the display list of SWF sprites frame by frame.

usage: python3 -I tools/swfdisplay.py <swf> <sprite_id> [<sprite_id> ...]
prints, per frame: depth char a b c d tx ty (matrix in pixels) [name]

Library use: display_lists(path) -> {sprite_id: [frame_state, ...]} where frame_state is
{depth: {'char': id, 'm': (a, b, c, d, tx, ty), 'name': str|None}} (sprite 0 = main timeline).
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swfnames import Bits, load, tags


def read_matrix(b):
    a = d = 1.0
    bb = c = 0.0
    if b.ub(1):
        n = b.ub(5); a = b.sb(n) / 65536; d = b.sb(n) / 65536
    if b.ub(1):
        n = b.ub(5); bb = b.sb(n) / 65536; c = b.sb(n) / 65536
    n = b.ub(5)
    tx, ty = b.sb(n) / 20, b.sb(n) / 20
    return b.align(), (a, bb, c, d, tx, ty)


def skip_cxform(b, alpha):
    add, mul = b.ub(1), b.ub(1)
    n = b.ub(4)
    for _ in range((4 if alpha else 3) * (add + mul)):
        b.ub(n)
    return b.align()


def simulate(d, p, end, out, sid=0):
    state, frames = {}, []
    for t, b, l in tags(d, p, end):
        if t == 39:
            cid = struct.unpack_from('<H', d, b)[0]
            simulate(d, b + 4, b + l, out, cid)
        elif t in (26, 70):
            fl = d[b]
            q = b + (2 if t == 70 else 1)
            fl2 = d[b + 1] if t == 70 else 0
            depth = struct.unpack_from('<H', d, q)[0]; q += 2
            if t == 70 and (fl2 & 8 or (fl2 & 16 and fl & 2)):
                q = d.index(0, q) + 1  # class name
            cur = dict(state.get(depth, {})) if fl & 1 else {}
            if fl & 2:
                cur['char'] = struct.unpack_from('<H', d, q)[0]; q += 2
            if fl & 4:
                q, cur['m'] = read_matrix(Bits(d, q))
            cur.setdefault('m', (1, 0, 0, 1, 0, 0))
            if fl & 8:
                q = skip_cxform(Bits(d, q), True)
            if fl & 16:
                q += 2
            if fl & 32:
                cur['name'] = d[q:d.index(0, q)].decode('utf-8', 'replace')
            state[depth] = cur
        elif t == 28:
            state.pop(struct.unpack_from('<H', d, b)[0], None)
        elif t == 5:
            state.pop(struct.unpack_from('<H', d, b + 2)[0], None)
        elif t == 1:
            frames.append({k: dict(v) for k, v in state.items()})
    out[sid] = frames


def display_lists(path):
    d, p = load(path)
    out = {}
    simulate(d, p, len(d), out)
    return out


if __name__ == '__main__':
    lists = display_lists(sys.argv[1])
    for sid in map(int, sys.argv[2:]):
        for i, st in enumerate(lists.get(sid, []), 1):
            for depth in sorted(st):
                e = st[depth]
                a, b, c, dd, tx, ty = e['m']
                print(sid, i, depth, e.get('char'), f'{a:.3f} {b:.3f} {c:.3f} {dd:.3f} {tx:.2f} {ty:.2f}', e.get('name', ''))
