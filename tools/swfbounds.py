"""Character bounds (pixels) for shapes and sprites, as FFDec uses them for PNG export canvases.

usage: python3 -I tools/swfbounds.py <swf> <char_id> [...]   -> id xmin ymin xmax ymax
Library: bounds(path) -> {char_id: (xmin, ymin, xmax, ymax)} for shapes, texts and sprites (union over frames).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swfdisplay import display_lists
from swfnames import Bits, load, tags

RECT_TAGS = {2, 22, 32, 83, 11, 33, 46, 84, 37}  # shapes, texts, morph shapes, edit text: id then RECT


def read_rect(d, p):
    b = Bits(d, p)
    n = b.ub(5)
    xmin, xmax, ymin, ymax = (b.sb(n) / 20 for _ in range(4))
    return xmin, ymin, xmax, ymax


def _collect_rects(d, p, end, out):
    for t, b, l in tags(d, p, end):
        if t in RECT_TAGS:
            out[d[b] | d[b + 1] << 8] = read_rect(d, b + 2)
        elif t == 39:
            _collect_rects(d, b + 4, b + l, out)


def transform(rect, m):
    a, b, c, dd, tx, ty = m
    xs, ys = [], []
    for x, y in ((rect[0], rect[1]), (rect[2], rect[1]), (rect[0], rect[3]), (rect[2], rect[3])):
        xs.append(a * x + c * y + tx)
        ys.append(b * x + dd * y + ty)
    return min(xs), min(ys), max(xs), max(ys)


def union(rs):
    rs = [r for r in rs if r]
    if not rs:
        return None
    return min(r[0] for r in rs), min(r[1] for r in rs), max(r[2] for r in rs), max(r[3] for r in rs)


def bounds(path):
    d, p = load(path)
    rects = {}
    _collect_rects(d, p, len(d), rects)
    lists = display_lists(path)
    memo = {}

    def get(cid, frame=None, stack=()):
        if cid in rects and cid not in lists:
            return rects[cid]
        if cid not in lists or cid in stack:
            return None
        frames = lists[cid] if frame is None else [lists[cid][frame - 1]]
        key = (cid, frame)
        if key not in memo:
            memo[key] = union([transform(r, e['m']) for st in frames for e in st.values()
                               if (r := get(e['char'], None, stack + (cid,)))])
        return memo[key]

    out = dict(rects)
    out.update({sid: get(sid) for sid in lists if sid})
    out['frame'] = get  # frame bounds: out['frame'](sprite_id, frame_no)
    return out


if __name__ == '__main__':
    bs = bounds(sys.argv[1])
    for cid in map(int, sys.argv[2:]):
        print(cid, bs.get(cid))
