"""Prepare the One Piece fighters' select/cut-in bitmaps for the BVN game.swf (consumed by tools/build.py).

usage: tools/venv/bin/python tools/op_assets.py

Input   source/onepiece/blog/fairy-tail-vs-one-piece-11.swf  (sprites 1386 icons, 1570 cut-in faces; labels = ids)
        work/op/roster.json
Output  work/op/ui/icon/<id>.png      50x48, BVN icon sprite 1465 local (0,0)
        work/op/ui/portrait/<id>.png  BVN portrait sprite 1346 (standing-art slot)
        work/op/ui/face/<label>.png   BVN cut-in sprite 1676
        work/op/ui/layout.json        {kind: {name: [x, y]}} top-left of each bitmap in its sprite's local px
"""
import json
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from swfbounds import bounds  # noqa: E402

SRC = os.path.join(ROOT, 'source/onepiece/blog/fairy-tail-vs-one-piece-11.swf')
EXPORT = os.path.join(ROOT, 'work/op/export/op')
OUT = os.path.join(ROOT, 'work/op/ui')
ICONS, FACES = 1386, 1570

# BVN targets (local px of the sprite the frame is appended to)
ICON_SIZE = (50, 48)            # sprite 1465 frames: 50x48 at (0,0)
FACE_BOX = (-90, -64, 121.5, 70)  # sprite 1676 union bounds: OP faces are scaled into this box's centre
FACE_SCALE = 0.6
PORTRAIT_TOP, PORTRAIT_CX, PORTRAIT_MAX = 75, 72, (165, 215)  # sprite 1346: BVN standing art spans x -3..144, y 73..456


def labels(swf, sprite):
    out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools/swfnames.py'), swf, str(sprite)],
                         capture_output=True, text=True, check=True).stdout
    return {ln.split(None, 2)[2]: int(ln.split()[1]) for ln in out.splitlines() if ln.strip().startswith('label')}


def frames(sprite):
    d = os.path.join(EXPORT, f'DefineSprite_{sprite}')
    if not os.path.isdir(d):
        subprocess.run(['java', '-jar', os.path.join(ROOT, 'tools/ffdec/ffdec.jar'), '-selectid', str(sprite),
                        '-format', 'sprite:png', '-export', 'sprite', EXPORT, SRC], capture_output=True, check=True)
    return d


def main():
    roster = json.load(open(os.path.join(ROOT, 'work/op/roster.json'), encoding='utf-8'))['fighters']
    b = bounds(SRC)
    face_x0, face_y0 = b[FACES][:2]  # FFDec sprite PNG canvas origin = union bounds
    icon_lab, face_lab = labels(SRC, ICONS), labels(SRC, FACES)
    layout = {'icon': {}, 'portrait': {}, 'face': {}}
    for k in layout:
        os.makedirs(os.path.join(OUT, k), exist_ok=True)

    icon_dir, face_dir = frames(ICONS), frames(FACES)
    bcx, bcy = (FACE_BOX[0] + FACE_BOX[2]) / 2, (FACE_BOX[1] + FACE_BOX[3]) / 2
    ocx, ocy = (b[FACES][0] + b[FACES][2]) / 2, (b[FACES][1] + b[FACES][3]) / 2
    for f in roster:
        fid = f['id']
        im = Image.open(os.path.join(icon_dir, f'{icon_lab[fid]}.png')).convert('RGBA')
        w, h = ICON_SIZE
        im = im.resize((w, w), Image.LANCZOS).crop((0, (w - h) // 2, w, (w - h) // 2 + h))
        im.save(os.path.join(OUT, 'icon', f'{fid}.png'))
        layout['icon'][fid] = [0, 0]

        for label in f['faces']:
            im = Image.open(os.path.join(face_dir, f'{face_lab[label]}.png')).convert('RGBA')
            x0, y0, x1, y1 = im.getbbox()
            art = im.crop((x0, y0, x1, y1))
            sw, sh = max(1, round(art.width * FACE_SCALE)), max(1, round(art.height * FACE_SCALE))
            art.resize((sw, sh), Image.LANCZOS).save(os.path.join(OUT, 'face', f'{label}.png'))
            # same placement relative to the box centre as in the source sprite, scaled
            layout['face'][label] = [round(bcx + (face_x0 + x0 - ocx) * FACE_SCALE, 2),
                                     round(bcy + (face_y0 + y0 - ocy) * FACE_SCALE, 2)]

        im = Image.open(os.path.join(face_dir, f'{face_lab[f["portrait"]]}.png')).convert('RGBA')
        art = im.crop(im.getbbox())
        s = min(PORTRAIT_MAX[0] / art.width, PORTRAIT_MAX[1] / art.height)
        art = art.resize((round(art.width * s), round(art.height * s)), Image.LANCZOS)
        art.save(os.path.join(OUT, 'portrait', f'{fid}.png'))
        layout['portrait'][fid] = [round(PORTRAIT_CX - art.width / 2, 2), PORTRAIT_TOP]
    json.dump(layout, open(os.path.join(OUT, 'layout.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', OUT, {k: len(v) for k, v in layout.items()})


if __name__ == '__main__':
    main()
