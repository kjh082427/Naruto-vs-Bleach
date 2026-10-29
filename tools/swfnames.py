"""List named PlaceObject2 instances (and frame labels) per DefineSprite in an SWF.

usage: python3 -I swfnames.py file.swf [sprite_id ...]
"""
import struct
import sys
import zlib


class Bits:
    def __init__(self, data, pos):
        self.d, self.byte, self.bit = data, pos, 0

    def ub(self, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | ((self.d[self.byte] >> (7 - self.bit)) & 1)
            self.bit += 1
            if self.bit == 8:
                self.bit, self.byte = 0, self.byte + 1
        return v

    def sb(self, n):
        v = self.ub(n)
        return v - (1 << n) if n and v & (1 << (n - 1)) else v

    def align(self):
        if self.bit:
            self.bit, self.byte = 0, self.byte + 1
        return self.byte


def skip_matrix(b):
    if b.ub(1):
        n = b.ub(5); b.ub(n); b.ub(n)
    if b.ub(1):
        n = b.ub(5); b.ub(n); b.ub(n)
    n = b.ub(5)
    tx, ty = b.sb(n), b.sb(n)
    return b.align(), tx / 20, ty / 20


def skip_cxform_alpha(b):
    add, mul = b.ub(1), b.ub(1)
    n = b.ub(4)
    for _ in range(4 * (add + mul)):
        b.ub(n)
    return b.align()


def load(path):
    d = open(path, 'rb').read()
    if d[:3] == b'CWS':
        d = d[:8] + zlib.decompress(d[8:])
    nbits = d[8] >> 3
    return d, 8 + (5 + 4 * nbits + 7) // 8 + 4


def tags(d, p, end):
    while p < end:
        h = struct.unpack_from('<H', d, p)[0]; p += 2
        t, l = h >> 6, h & 63
        if l == 63:
            l = struct.unpack_from('<I', d, p)[0]; p += 4
        yield t, p, l
        p += l
        if t == 0:
            return


TAG_NAMES = {2: 'Shape', 22: 'Shape2', 32: 'Shape3', 83: 'Shape4', 39: 'Sprite', 11: 'Text', 33: 'Text2',
             37: 'EditText', 7: 'Button', 34: 'Button2', 6: 'Bits', 21: 'BitsJPEG2', 35: 'BitsJPEG3',
             20: 'BitsLossless', 36: 'BitsLossless2', 46: 'MorphShape', 14: 'Sound', 10: 'Font', 48: 'Font2',
             75: 'Font3', 60: 'Video'}
CHAR_TYPES = {}


def walk(d, p, end, sprites, sid=0, show_all=False):
    frame = 1
    for t, b, l in tags(d, p, end):
        if t in TAG_NAMES and t not in (6,):
            CHAR_TYPES[struct.unpack_from('<H', d, b)[0]] = TAG_NAMES[t]
        if t == 39:
            cid = struct.unpack_from('<H', d, b)[0]
            walk(d, b + 4, b + l, sprites, cid, show_all)
        elif t == 1:
            frame += 1
        elif t == 43:
            name = d[b:d.index(0, b)].decode('utf-8', 'replace')
            sprites.setdefault(sid, []).append(('label', frame, name))
        elif t == 26:
            fl = d[b]; q = b + 1 + 2
            ch = None
            if fl & 2:
                ch = struct.unpack_from('<H', d, q)[0]; q += 2
            x = y = None
            if fl & 4:
                q, x, y = skip_matrix(Bits(d, q))
            if fl & 8:
                q = skip_cxform_alpha(Bits(d, q))
            if fl & 16:
                q += 2
            if fl & 32:
                name = d[q:d.index(0, q)].decode('utf-8', 'replace')
                sprites.setdefault(sid, []).append(('place', frame, name, ch, x, y))
            elif show_all and ch is not None:
                sprites.setdefault(sid, []).append(('place', frame, '-', ch, x, y))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--all']
    d, p = load(args[0])
    sprites = {}
    walk(d, p, len(d), sprites, show_all='--all' in sys.argv)
    want = {int(a) for a in args[1:]}
    for sid, items in sprites.items():
        if want and sid not in want:
            continue
        print(f'== sprite {sid}')
        for it in items:
            extra = (CHAR_TYPES.get(it[3], '?'),) if it[0] == 'place' else ()
            print('  ', *it, *extra)
