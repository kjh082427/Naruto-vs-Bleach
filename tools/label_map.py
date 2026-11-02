"""Label map of a fighter's animation sprite: which bitmaps and hitboxes each action label uses.

usage: tools/venv/bin/python tools/label_map.py <fighter.swf> <mc sprite id> <out dir>

Writes <out dir>/shape_bitmaps.json ({shape id: [bitmap ids]}, from FFDec -swf2xml) and <out dir>/label_map.json:
  {"labels": {label: {"frames": [first, last], "bitmaps": [...], "named": [instance names]}}, "all_bitmaps": [...]}
Hitboxes are the named instances ending in "atm" (k1atm, zh2atm, cbsatm ...). Used to brief the reskin and to plan
new moves for custom fighters (see tools/mihawk.py, ANALYSIS.md §9).
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from swfdisplay import display_lists  # noqa: E402


def shape_bitmaps(swf, out_dir):
    xml_path = os.path.join(out_dir, 'fighter.xml')
    subprocess.run(['java', '-jar', os.path.join(ROOT, 'tools/ffdec/ffdec.jar'), '-swf2xml', swf, xml_path],
                   capture_output=True, check=True)
    x = open(xml_path, encoding='utf-8', errors='replace').read()
    starts = list(re.finditer(r'<item type="(Define\w+)"[^>]*?(?:shapeId|spriteId|characterID|characterId|fontId|'
                              r'buttonId)="(\d+)"', x))
    sb = {}
    for i, m in enumerate(starts):  # a define's XML runs until the next top-level define
        if m.group(1).startswith('DefineShape'):
            end = starts[i + 1].start() if i + 1 < len(starts) else len(x)
            sb[int(m.group(2))] = sorted({int(b) for b in re.findall(r'bitmapId="(\d+)"', x[m.start():end])} - {65535})
    return sb


def label_map(swf, mc, sb):
    dl = display_lists(swf)
    out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools/swfnames.py'), swf, str(mc)],
                         capture_output=True, text=True, check=True).stdout
    labs = [(int(ln.split()[1]), ln.split(None, 2)[2]) for ln in out.splitlines() if ln.strip().startswith('label')]
    memo = {}

    def bitmaps_of(cid, stack=()):
        if cid in memo:
            return memo[cid]
        found = set(sb.get(cid, []))
        if cid in dl and cid not in stack:
            for st in dl[cid]:
                for e in st.values():
                    found |= bitmaps_of(e['char'], stack + (cid,))
        memo[cid] = found
        return found

    res, n = {}, len(dl[mc])
    for i, (first, name) in enumerate(labs):
        last = labs[i + 1][0] - 1 if i + 1 < len(labs) else n
        bm, names = set(), set()
        for fr in range(first, last + 1):
            for e in dl[mc][fr - 1].values():
                bm |= bitmaps_of(e['char'])
                if e.get('name'):
                    names.add(e['name'])
        res[name] = {'frames': [first, last], 'bitmaps': sorted(bm), 'named': sorted(names)}
    return {'labels': res, 'all_bitmaps': sorted(set().union(*[set(v['bitmaps']) for v in res.values()]))}


if __name__ == '__main__':
    swf, mc, out_dir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    sb = shape_bitmaps(swf, out_dir)
    json.dump(sb, open(os.path.join(out_dir, 'shape_bitmaps.json'), 'w'))
    lm = label_map(swf, mc, sb)
    json.dump(lm, open(os.path.join(out_dir, 'label_map.json'), 'w'), ensure_ascii=False, indent=1)
    for k, v in lm['labels'].items():
        hits = [n for n in v['named'] if n.endswith('atm')]
        print(f"{k:5} {v['frames']} bitmaps={len(v['bitmaps']):3} hit={hits}")
    print('total bitmaps', len(lm['all_bitmaps']))
