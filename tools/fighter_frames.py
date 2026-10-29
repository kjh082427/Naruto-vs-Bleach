"""Per-bitmap placement facts for a fighter SWF, from the simulated display list.

usage: python3 -I tools/fighter_frames.py <fighter.swf> <fighter.xml> <mc_sprite_id> <out.json>

For every bitmap: size, the shapes that fill with it, and for each mc frame where it is visible:
  label, t (0..1 within the label), anchor = pixel position of the mc origin inside the bitmap,
  sx/sy = placement scale (negative = mirrored), or for effects the nested sprite and its frame index.
"""
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swfdisplay  # noqa: E402
from swfnames import load, walk  # noqa: E402


def xml_facts(path):
    xml = open(path, encoding='utf-8').read()
    sizes = {}
    for m in re.finditer(r'<item type="DefineBits\w*Tag"([^>]*)>', xml):
        a = m.group(1)
        cid = int(re.search(r'characterID="(\d+)"', a).group(1))
        w, h = re.search(r'bitmapWidth="(\d+)"', a), re.search(r'bitmapHeight="(\d+)"', a)
        sizes[cid] = (int(w.group(1)), int(h.group(1))) if w else None
    shape_fill = {}
    starts = [(m.start(), int(m.group(1))) for m in re.finditer(r'<item type="DefineShape\d?Tag"[^>]*shapeId="(\d+)"', xml)]
    starts.append((len(xml), None))
    for (pos, sid), (nxt, _) in zip(starts, starts[1:]):
        seg = xml[pos:nxt]
        for fm in re.finditer(r'bitmapId="(\d+)"[^>]*>\s*<bitmapMatrix([^>]*)/>', seg):
            bid = int(fm.group(1))
            if bid == 65535:
                continue
            a = fm.group(2)
            g = lambda k, dflt: float(re.search(k + r'="([-\d.]+)"', a).group(1)) if re.search(k + r'="([-\d.]+)"', a) else dflt
            shape_fill.setdefault(sid, []).append((bid, g('scaleX', 20.0) / 20, g('scaleY', 20.0) / 20,
                                                   g('translateX', 0) / 20, g('translateY', 0) / 20))
    return sizes, shape_fill


def main():
    swf, xml, mc, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    sizes, shape_fill = xml_facts(xml)
    lists = swfdisplay.display_lists(swf)
    d, p = load(swf)
    tree = {}
    walk(d, p, len(d), tree)
    labels = sorted((it[1], it[2]) for it in tree.get(mc, []) if it[0] == 'label')
    mc_frames = lists[mc]

    def label_at(f):
        cur = ('?', 1, len(mc_frames))
        for i, (start, name) in enumerate(labels):
            if start <= f:
                end = labels[i + 1][0] if i + 1 < len(labels) else len(mc_frames) + 1
                cur = (name, start, end - start)
        return cur

    facts = defaultdict(lambda: {'char': [], 'effect': []})
    for f, state in enumerate(mc_frames, 1):
        name, start, length = label_at(f)
        t = round((f - start) / max(1, length - 1), 3)
        for depth, e in state.items():
            ch, (a, b, c, dd, tx, ty) = e.get('char'), e['m']
            for bid, fsx, fsy, ftx, fty in shape_fill.get(ch, []):
                # bitmap pixel -> shape: (fsx*px + ftx); shape -> mc: (a*x + tx). mc origin -> pixel:
                sx, sy = a * fsx, dd * fsy
                ax = (-tx / a - ftx) / fsx if a else None
                ay = (-ty / dd - fty) / fsy if dd else None
                facts[bid]['char'].append({'frame': f, 'label': name, 't': t, 'depth': depth,
                                           'anchor': [round(ax, 2), round(ay, 2)], 'sx': round(sx, 3), 'sy': round(sy, 3),
                                           'rot': bool(b or c)})
            if ch in lists:  # nested sprite: record which of its bitmaps appear at which inner frame
                inner = lists[ch]
                for k, st in enumerate(inner, 1):
                    for e2 in st.values():
                        for bid, *_ in shape_fill.get(e2.get('char'), []):
                            facts[bid]['effect'].append({'sprite': ch, 'inner_frame': k, 'inner_frames': len(inner),
                                                         'label': name, 'mc_frame': f})
    result = []
    for bid, sz in sorted(sizes.items()):
        fx = facts.get(bid, {'char': [], 'effect': []})
        eff = {(e['sprite'], e['inner_frame']): e for e in fx['effect']}
        result.append({'bitmap_id': bid, 'size': sz, 'char_uses': fx['char'], 'effect_uses': sorted(eff.values(), key=lambda e: (e['sprite'], e['inner_frame']))})
    json.dump(result, open(out, 'w'), ensure_ascii=False, indent=1)
    c = sum(1 for r in result if r['char_uses'])
    e = sum(1 for r in result if not r['char_uses'] and r['effect_uses'])
    print(f'{len(result)} bitmaps: {c} character frames, {e} effect-only, {len(result) - c - e} unused')


if __name__ == '__main__':
    main()
