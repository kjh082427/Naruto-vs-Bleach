"""Minimal, byte-preserving SWF tag editor.

Unmodified tags are written back byte-for-byte (including their short/long header form), so a
load/save round trip reproduces the input exactly. Sprites are parsed into child tag lists.

    swf = Swf.load('game.swf')
    bmp = swf.new_id(); shp = swf.new_id()
    swf.insert_before_define(1465, [bits_lossless2(bmp, 'icon.png'), clone_shape_with_bitmap(swf, 1374, shp, bmp)])
    swf.add_labeled_frame(1465, 'new_label', shp)
    swf.save('out.swf')
"""
import struct
import zlib

DEFINE_TAGS = {2, 22, 32, 83, 39, 11, 33, 37, 7, 34, 6, 21, 35, 90, 20, 36, 46, 84, 14, 10, 48, 75, 60, 87}


class Tag:
    __slots__ = ('type', 'body', 'long', 'children', 'sprite_id', 'frames')

    def __init__(self, type_, body=b'', long=None, children=None):
        self.type, self.body = type_, body
        self.long = long if long is not None else (len(body) >= 63 or type_ in DEFINE_TAGS)
        self.children = children
        self.sprite_id = self.frames = None
        if type_ == 39 and children is not None:
            self.sprite_id, self.frames = struct.unpack_from('<HH', body)

    @property
    def char_id(self):
        if self.type in DEFINE_TAGS and len(self.body) >= 2:
            return struct.unpack_from('<H', self.body)[0]
        return None

    def encode(self):
        body = self.body
        if self.children is not None:
            body = struct.pack('<HH', self.sprite_id, self.frames) + b''.join(t.encode() for t in self.children)
        if self.long or len(body) >= 63:
            return struct.pack('<HI', (self.type << 6) | 63, len(body)) + body
        return struct.pack('<H', (self.type << 6) | len(body)) + body


def parse_tags(d, p, end):
    out = []
    while p < end:
        h = struct.unpack_from('<H', d, p)[0]; p += 2
        t, l = h >> 6, h & 63
        long = l == 63
        if long:
            l = struct.unpack_from('<I', d, p)[0]; p += 4
        body = d[p:p + l]
        if t == 39:
            tag = Tag(39, body[:4], long, parse_tags(body, 4, len(body)))
        else:
            tag = Tag(t, body, long)
        out.append(tag)
        p += l
        if t == 0:
            break
    return out


class Swf:
    def __init__(self, version, header_rest, tags, compressed):
        self.version, self.header_rest, self.tags, self.compressed = version, header_rest, tags, compressed

    @classmethod
    def load(cls, path):
        raw = open(path, 'rb').read()
        sig, ver = raw[:3], raw[3]
        d = raw[:8] + zlib.decompress(raw[8:]) if sig == b'CWS' else raw
        nbits = d[8] >> 3
        hdr_end = 8 + (5 + 4 * nbits + 7) // 8 + 4
        return cls(ver, d[8:hdr_end], parse_tags(d, hdr_end, len(d)), sig == b'CWS')

    def save(self, path, compress=None):
        body = self.header_rest + b''.join(t.encode() for t in self.tags)
        length = 8 + len(body)
        comp = self.compressed if compress is None else compress
        sig = b'CWS' if comp else b'FWS'
        data = zlib.compress(body, 9) if comp else body
        open(path, 'wb').write(sig + bytes([self.version]) + struct.pack('<I', length) + data)

    # --- lookup -------------------------------------------------------------------------------
    def walk(self, tags=None):
        for i, t in enumerate(self.tags if tags is None else tags):
            yield (self.tags if tags is None else tags), i, t
            if t.children is not None:
                yield from self.walk(t.children)

    def find_define(self, cid):
        for lst, i, t in self.walk():
            if t.char_id == cid and t.type in DEFINE_TAGS:
                return lst, i, t
        raise KeyError(cid)

    def max_id(self):
        return max(t.char_id or 0 for _, _, t in self.walk())

    def new_id(self):
        self._next = max(getattr(self, '_next', 0), self.max_id()) + 1
        return self._next

    def insert_before_define(self, cid, new_tags):
        lst, i, _ = self.find_define(cid)
        lst[i:i] = new_tags

    def replace_define(self, cid, new_tag):
        lst, i, _ = self.find_define(cid)
        lst[i] = new_tag

    # --- sprite edits ----------------------------------------------------------------------------
    def add_labeled_frame(self, sprite_id, label, char_id, depth=1):
        """Append one frame to a sprite that swaps `depth` to `char_id` and carries frame label `label`."""
        _, _, sp = self.find_define(sprite_id)
        assert sp.type == 39
        end = len(sp.children) - 1 if sp.children and sp.children[-1].type == 0 else len(sp.children)
        sp.children[end:end] = [place_object2(depth, char=char_id, move=True), frame_label(label), Tag(1, b'', False)]
        sp.frames += 1

    def first_frame_insert(self, sprite_id, new_tags):
        """Insert tags into frame 1 of a sprite (before its first ShowFrame)."""
        _, _, sp = self.find_define(sprite_id)
        k = next(i for i, t in enumerate(sp.children) if t.type == 1)
        sp.children[k:k] = new_tags

    def find_place(self, sprite_id, name):
        _, _, sp = self.find_define(sprite_id)
        for t in sp.children:
            if t.type == 26 and parse_place_object2(t.body).get('name') == name:
                return t
        raise KeyError(name)


# --- tag builders ------------------------------------------------------------------------------------
class BitWriter:
    def __init__(self):
        self.bits = []

    def ub(self, v, n):
        self.bits += [(v >> (n - 1 - i)) & 1 for i in range(n)]

    def sb(self, v, n):
        self.ub(v & ((1 << n) - 1), n)

    def bytes(self):
        b = self.bits + [0] * (-len(self.bits) % 8)
        return bytes(int(''.join(map(str, b[i:i + 8])), 2) for i in range(0, len(b), 8))


def sbits_needed(*vals):
    n = 1
    for v in vals:
        while not (-(1 << (n - 1)) <= v < (1 << (n - 1))):
            n += 1
    return n


def encode_matrix(a=1.0, b=0.0, c=0.0, d=1.0, tx=0.0, ty=0.0):
    w = BitWriter()
    if (a, d) != (1.0, 1.0):
        sa, sd = round(a * 65536), round(d * 65536)
        n = sbits_needed(sa, sd)
        w.ub(1, 1); w.ub(n, 5); w.sb(sa, n); w.sb(sd, n)
    else:
        w.ub(0, 1)
    if (b, c) != (0.0, 0.0):
        sb_, sc = round(b * 65536), round(c * 65536)
        n = sbits_needed(sb_, sc)
        w.ub(1, 1); w.ub(n, 5); w.sb(sb_, n); w.sb(sc, n)
    else:
        w.ub(0, 1)
    itx, ity = round(tx * 20), round(ty * 20)
    n = sbits_needed(itx, ity) if (itx or ity) else 0
    w.ub(n, 5)
    if n:
        w.sb(itx, n); w.sb(ity, n)
    return w.bytes()


def encode_rect(xmin, xmax, ymin, ymax):
    """Twips."""
    w = BitWriter()
    n = sbits_needed(xmin, xmax, ymin, ymax)
    w.ub(n, 5)
    for v in (xmin, xmax, ymin, ymax):
        w.sb(v, n)
    return w.bytes()


def place_object2(depth, char=None, matrix=None, name=None, move=False, raw_tail=b''):
    fl = (1 if move else 0) | (2 if char is not None else 0) | (4 if matrix is not None else 0) | (32 if name else 0)
    body = bytes([fl]) + struct.pack('<H', depth)
    if char is not None:
        body += struct.pack('<H', char)
    if matrix is not None:
        body += encode_matrix(*matrix)
    if name:
        body += name.encode('utf-8') + b'\0'
    return Tag(26, body + raw_tail, False)


def parse_place_object2(body):
    from swfnames import Bits, skip_cxform_alpha
    fl = body[0]
    out = {'flags': fl, 'depth': struct.unpack_from('<H', body, 1)[0]}
    q = 3
    if fl & 2:
        out['char'] = struct.unpack_from('<H', body, q)[0]; q += 2
    if fl & 4:
        from swfdisplay import read_matrix
        q, out['matrix'] = read_matrix(Bits(body, q))
    if fl & 8:
        q = skip_cxform_alpha(Bits(body, q))
    if fl & 16:
        out['ratio'] = struct.unpack_from('<H', body, q)[0]; q += 2
    if fl & 32:
        e = body.index(0, q)
        out['name'] = body[q:e].decode('utf-8', 'replace'); q = e + 1
    out['tail'] = body[q:]  # clip depth + clip actions, kept verbatim
    return out


def frame_label(name):
    return Tag(43, name.encode('utf-8') + b'\0', False)


def bits_lossless2(cid, png_path):
    from PIL import Image
    im = Image.open(png_path).convert('RGBA')
    w, h = im.size
    px = bytearray()
    for r, g, b, a in im.getdata():
        px += bytes((a, r * a // 255, g * a // 255, b * a // 255))
    body = struct.pack('<HBHH', cid, 5, w, h) + zlib.compress(bytes(px), 9)
    return Tag(36, body, True)


def clone_shape_with_bitmap(swf, ref_shape_id, new_id, new_bitmap_id):
    """Copy a single-bitmap-fill shape and point it at another bitmap (same pixel size expected)."""
    _, _, ref = swf.find_define(ref_shape_id)
    body = bytearray(ref.body)
    nbits = body[2] >> 3
    q = 2 + (5 + 4 * nbits + 7) // 8
    if ref.type == 83:  # DefineShape4: edge bounds + flags byte
        nb2 = body[q] >> 3
        q += (5 + 4 * nb2 + 7) // 8 + 1
    count = body[q]; q += 1
    if count == 0xFF:
        count = struct.unpack_from('<H', body, q)[0]; q += 2
    from swfnames import Bits
    from swfdisplay import read_matrix
    patched = 0
    for _ in range(count):  # every non-null bitmap fill in the initial fill style array
        ftype = body[q]
        if 0x40 <= ftype <= 0x43:
            if struct.unpack_from('<H', body, q + 1)[0] != 0xFFFF:
                struct.pack_into('<H', body, q + 1, new_bitmap_id)
                patched += 1
            q, _ = read_matrix(Bits(body, q + 3))
        elif ftype == 0x00:
            q += 1 + (4 if ref.type in (32, 83) else 3)
        else:
            raise ValueError(f'shape {ref_shape_id}: unsupported fill type {ftype:#x}')
    assert patched, f'shape {ref_shape_id} has no bitmap fill'
    struct.pack_into('<H', body, 0, new_id)
    return Tag(ref.type, bytes(body), True)
