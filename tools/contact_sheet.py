"""Build labelled contact sheets from a folder of images (largest first).

usage: tools/venv/bin/python tools/contact_sheet.py <imgdir> <outprefix> [--min 40] [--cell 150] [--cols 8] [--rows 6]
Each cell shows the image scaled to fit, on a checkerboard, labelled with "<id> WxH".
"""
import os
import sys

from PIL import Image, ImageDraw


def opt(name, default):
    return int(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def main():
    src, prefix = sys.argv[1], sys.argv[2]
    minsize, cell, cols, rows = opt('--min', 40), opt('--cell', 150), opt('--cols', 8), opt('--rows', 6)
    items = []
    for f in os.listdir(src):
        if not f.lower().endswith(('.png', '.jpg')):
            continue
        im = Image.open(os.path.join(src, f))
        if max(im.size) >= minsize:
            items.append((im.size[0] * im.size[1], f, im))
    items.sort(reverse=True)
    per = cols * rows
    for page in range(0, len(items), per):
        sheet = Image.new('RGB', (cols * cell, rows * (cell + 14)), (60, 60, 60))
        dr = ImageDraw.Draw(sheet)
        for k, (_, f, im) in enumerate(items[page:page + per]):
            x, y = (k % cols) * cell, (k // cols) * (cell + 14)
            for cy in range(0, cell, 10):
                for cx in range(0, cell, 10):
                    c = (200, 200, 200) if (cx + cy) // 10 % 2 else (240, 240, 240)
                    dr.rectangle([x + cx, y + cy, x + cx + 9, y + cy + 9], fill=c)
            t = im.convert('RGBA')
            t.thumbnail((cell - 4, cell - 4))
            sheet.paste(t, (x + 2, y + 2), t)
            dr.text((x + 2, y + cell), f'{f.rsplit(".", 1)[0]} {im.size[0]}x{im.size[1]}', fill=(255, 255, 0))
        out = f'{prefix}_{page // per:02d}.png'
        sheet.save(out)
        print(out, len(items[page:page + per]))


if __name__ == '__main__':
    main()
