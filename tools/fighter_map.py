"""Map every bitmap in a fighter SWF to where it is used (action label / effect sprite).

usage: python3 -I tools/fighter_map.py <fighter.xml from ffdec -swf2xml> <tree.txt from swfnames --all> <mc_sprite_id> <out.json>

Output entries: {bitmap_id, w, h, uses: [{sprite, frame, label, label_start, label_len, t, via}]}
  - sprite == mc sprite: the bitmap is a character animation frame for `label`
  - otherwise via = nested sprite chain; label = the mc label where that nested sprite is placed
"""
import json
import re
import sys
from collections import defaultdict


def parse_xml(path):
    xml = open(path, encoding='utf-8').read()
    bitmaps, shape_bitmaps = {}, defaultdict(set)
    for m in re.finditer(r'<item type="DefineBits\w*Tag"([^>]*)>', xml):
        a = m.group(1)
        cid = re.search(r'characterID="(\d+)"', a)
        w = re.search(r'bitmapWidth="(\d+)"', a)
        h = re.search(r'bitmapHeight="(\d+)"', a)
        if cid:
            bitmaps[int(cid.group(1))] = (int(w.group(1)) if w else None, int(h.group(1)) if h else None)
    starts = [(m.start(), int(m.group(1))) for m in re.finditer(r'<item type="DefineShape\d?Tag"[^>]*shapeId="(\d+)"', xml)]
    starts.append((len(xml), None))
    for (pos, sid), (nxt, _) in zip(starts, starts[1:]):
        for b in re.findall(r'bitmapId="(\d+)"', xml[pos:nxt]):
            if int(b) != 65535:
                shape_bitmaps[sid].add(int(b))
    return bitmaps, shape_bitmaps


def parse_tree(path):
    places, labels, cur = defaultdict(list), defaultdict(list), None
    for line in open(path, encoding='utf-8'):
        if line.startswith('=='):
            cur = int(line.split()[2])
            continue
        p = line.split()
        if p[0] == 'label':
            labels[cur].append((int(p[1]), p[2]))
        elif p[0] == 'place':
            places[cur].append((int(p[1]), int(p[3]), p[2]))
    return places, labels


def main():
    xml_path, tree_path, mc, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    bitmaps, shape_bitmaps = parse_xml(xml_path)
    places, labels = parse_tree(tree_path)
    frames_of = {s: max([f for f, _, _ in v] + [1]) for s, v in places.items()}
    mc_labels = sorted(labels[mc])
    total = max(frames_of.get(mc, 1), mc_labels[-1][0] if mc_labels else 1)

    def label_at(frame):
        best = None
        for i, (f, name) in enumerate(mc_labels):
            if f <= frame:
                nxt = mc_labels[i + 1][0] if i + 1 < len(mc_labels) else total + 1
                best = (name, f, nxt - f)
        return best or ('?', 1, 1)

    # where each character id is placed: char -> [(sprite, frame)]
    placed_in = defaultdict(list)
    for s, v in places.items():
        for f, ch, _ in v:
            placed_in[ch].append((s, f))

    def resolve(ch, chain, depth=0):
        res = []
        for s, f in placed_in.get(ch, []):
            if s == mc:
                name, start, length = label_at(f)
                res.append({'sprite': s, 'frame': f, 'label': name, 'label_start': start, 'label_len': length,
                            't': round((f - start) / max(1, length - 1), 3), 'via': chain})
            elif s != 0 and depth < 6:
                for r in resolve(s, chain + [{'sprite': s, 'frame': f, 'frames': frames_of.get(s, 1)}], depth + 1):
                    res.append(r)
            elif s == 0:
                res.append({'sprite': 0, 'frame': f, 'label': 'ROOT', 'via': chain})
        return res

    result = []
    shapes_by_bitmap = defaultdict(list)
    for sid, bs in shape_bitmaps.items():
        for b in bs:
            shapes_by_bitmap[b].append(sid)
    for b, (w, h) in sorted(bitmaps.items()):
        uses = []
        for sid in shapes_by_bitmap.get(b, []):
            uses += resolve(sid, [])
        result.append({'bitmap_id': b, 'w': w, 'h': h, 'shapes': shapes_by_bitmap.get(b, []), 'uses': uses})
    json.dump(result, open(out, 'w'), ensure_ascii=False, indent=1)
    direct = sum(1 for r in result if any(u['sprite'] == mc and not u['via'] for u in r['uses']))
    nested = sum(1 for r in result if r['uses'] and not any(u['sprite'] == mc and not u['via'] for u in r['uses']))
    unused = sum(1 for r in result if not r['uses'])
    print(f'{len(result)} bitmaps: {direct} direct mc frames, {nested} nested/effects, {unused} unresolved')


if __name__ == '__main__':
    main()
