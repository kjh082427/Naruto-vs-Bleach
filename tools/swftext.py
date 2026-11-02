"""Text-level SWF edits built on swfpatch: rewrite DefineEditText, convert DefineText to device-font
EditText sprites, and build simple bitmap/animation tags.

All coordinates in twips unless a name says px.
"""
import struct

from swfpatch import BitWriter, Tag, encode_matrix, encode_rect, place_object2, sbits_needed
from swfnames import Bits

# --- DefineEditText -----------------------------------------------------------------------------------


def parse_edit_text(body):
    b = Bits(body, 2)
    nb = b.ub(5)
    rect = [b.sb(nb) for _ in range(4)]
    q = b.align()
    f1, f2 = body[q], body[q + 1]; q += 2
    e = {'id': struct.unpack_from('<H', body)[0], 'rect': rect, 'f1': f1, 'f2': f2}
    if f1 & 0x01:
        e['font'] = struct.unpack_from('<H', body, q)[0]; q += 2
    if f2 & 0x80:
        z = body.index(0, q); e['font_class'] = body[q:z]; q = z + 1
    if f1 & 0x01:
        e['height'] = struct.unpack_from('<H', body, q)[0]; q += 2
    if f1 & 0x04:
        e['color'] = body[q:q + 4]; q += 4
    if f1 & 0x02:
        e['maxlen'] = struct.unpack_from('<H', body, q)[0]; q += 2
    if f2 & 0x20:
        e['layout'] = body[q:q + 9]; q += 9
    z = body.index(0, q); e['var'] = body[q:z].decode('utf-8', 'replace'); q = z + 1
    if f1 & 0x80:
        z = body.index(0, q); e['text'] = body[q:z].decode('utf-8', 'replace'); q = z + 1
    return e


def build_edit_text(e):
    f1, f2 = e['f1'], e['f2']
    f1 = (f1 | 0x80) if e.get('text') is not None else (f1 & ~0x80)
    body = struct.pack('<H', e['id']) + encode_rect(*_xxyy(e['rect'])) + bytes([f1, f2])
    if f1 & 0x01:
        body += struct.pack('<H', e['font'])
    if f2 & 0x80:
        body += e['font_class'] + b'\0'
    if f1 & 0x01:
        body += struct.pack('<H', e['height'])
    if f1 & 0x04:
        body += e['color']
    if f1 & 0x02:
        body += struct.pack('<H', e['maxlen'])
    if f2 & 0x20:
        body += e['layout']
    body += e.get('var', '').encode('utf-8') + b'\0'
    if f1 & 0x80:
        body += e['text'].encode('utf-8') + b'\0'
    return Tag(37, body, True)


def _xxyy(rect):
    return rect  # parse order is xmin, xmax, ymin, ymax already


def new_edit_text(cid, rect, font_id, height, rgba, text, align=2, html=False):
    """Read-only, non-selectable, single-line device-font text (WasStatic)."""
    f1 = 0x80 | 0x08 | 0x04 | 0x01           # HasText, ReadOnly, HasTextColor, HasFont
    f2 = 0x20 | 0x10 | 0x04 | (0x02 if html else 0)  # HasLayout, NoSelect, WasStatic, HTML
    layout = struct.pack('<BHHHh', align, 0, 0, 0, 0)
    e = {'id': cid, 'rect': rect, 'f1': f1, 'f2': f2, 'font': font_id, 'height': height,
         'color': bytes(rgba), 'layout': layout, 'var': '', 'text': text}
    return build_edit_text(e)


# --- DefineText ----------------------------------------------------------------------------------------


def parse_define_text(tag):
    body = tag.body
    rgba = tag.type == 33
    b = Bits(body, 2)
    nb = b.ub(5)
    bounds = [b.sb(nb) for _ in range(4)]
    q = b.align()
    from swfdisplay import read_matrix
    mb = Bits(body, q)
    a = d = 1.0; bb = c = 0.0
    if mb.ub(1):
        n = mb.ub(5); a = mb.sb(n) / 65536; d = mb.sb(n) / 65536
    if mb.ub(1):
        n = mb.ub(5); bb = mb.sb(n) / 65536; c = mb.sb(n) / 65536
    n = mb.ub(5)
    tx, ty = mb.sb(n), mb.sb(n)
    q = mb.align()
    gbits, abits = body[q], body[q + 1]; q += 2
    recs, font, color, height, x, y = [], None, (0, 0, 0, 255), 240, 0, 0
    while body[q] != 0:
        fl = body[q]; q += 1
        if fl & 0x08:
            font = struct.unpack_from('<H', body, q)[0]; q += 2
        if fl & 0x04:
            color = tuple(body[q:q + (4 if rgba else 3)]) + (() if rgba else (255,)); q += 4 if rgba else 3
        if fl & 0x01:
            x = struct.unpack_from('<h', body, q)[0]; q += 2
        if fl & 0x02:
            y = struct.unpack_from('<h', body, q)[0]; q += 2
        if fl & 0x08:
            height = struct.unpack_from('<H', body, q)[0]; q += 2
        count = body[q]; q += 1
        gb = Bits(body, q)
        adv = 0
        for _ in range(count):
            gb.ub(gbits); adv += gb.sb(abits)
        q = gb.align()
        recs.append({'font': font, 'color': color, 'height': height, 'x': x, 'y': y, 'adv': adv, 'glyphs': count})
        x += adv
    return {'id': tag.char_id, 'bounds': bounds, 'matrix': (a, bb, c, d, tx / 20, ty / 20), 'records': recs}


def define_text_to_sprite(swf, text_tag, record_texts, ascent=0.86, pad_twips=60, color=None):
    """Replace a DefineText by a same-id sprite of centered device-font EditTexts, one per text line.

    record_texts: translated text per TEXTRECORD (same order as FFDec's record export). Records on the
    same baseline are merged into one line (their texts joined without separator).
    Returns the list of new tags (EditText defs + sprite) to substitute for the DefineText.
    """
    info = parse_define_text(text_tag)
    lines = []
    for rec, txt in zip(info['records'], record_texts):
        if lines and lines[-1]['y'] == rec['y']:
            ln = lines[-1]
            ln['text'] += txt
            ln['x1'] = rec['x'] + rec['adv']
        else:
            lines.append({**rec, 'text': txt, 'x0': rec['x'], 'x1': rec['x'] + rec['adv']})
    new_tags, places = [], []
    for k, ln in enumerate(lines):
        if not ln['text'].strip():
            continue
        cid = swf.new_id()
        cx = (ln['x0'] + ln['x1']) // 2
        half = max((ln['x1'] - ln['x0']) // 2, ln['height'] * max(1, len(ln['text'])) // 2) + 400
        top = ln['y'] - int(ln['height'] * ascent) - 40
        rect = [cx - half, cx + half, top, top + int(ln['height'] * 1.25) + 80]
        new_tags.append(new_edit_text(cid, rect, ln['font'], ln['height'], color or ln['color'], ln['text']))
        places.append(place_object2(k + 1, char=cid, matrix=info['matrix']))
    sprite = Tag(39, struct.pack('<HH', info['id'], 1), True,
                 places + [Tag(1, b'', False), Tag(0, b'', False)])
    sprite.sprite_id, sprite.frames = info['id'], 1
    return new_tags + [sprite]


# --- bitmap rectangle shapes, color transforms, actions ---------------------------------------------------


def bitmap_rect_shape(cid, bitmap_id, x_px, y_px, w_px, h_px, bitmap_px=None, fill_px=None):
    """DefineShape covering (x,y,w,h) px with a clipped bitmap fill stretched over that rect.

    bitmap_px = (bw, bh) of the bitmap when it differs from (w, h) (e.g. inside a scaled sprite).
    fill_px = (fx, fy, fw, fh): the bitmap is stretched over this rect instead, and the shape shows only the part
    inside (x,y,w,h) (one frame of a sprite sheet).
    """
    X, Y, W, H = (round(v * 20) for v in (x_px, y_px, w_px, h_px))
    fx, fy, fw, fh = fill_px or (x_px, y_px, w_px, h_px)
    bw, bh = bitmap_px or (fw, fh)
    body = struct.pack('<H', cid) + encode_rect(X, X + W, Y, Y + H)
    body += bytes([1, 0x41]) + struct.pack('<H', bitmap_id) + encode_matrix(20.0 * fw / bw, 0, 0, 20.0 * fh / bh, fx, fy)
    body += bytes([0])  # no line styles
    w = BitWriter()
    w.ub(1, 4); w.ub(0, 4)  # NumFillBits=1, NumLineBits=0
    n = sbits_needed(X, Y)
    w.ub(0, 1); w.ub(0, 1); w.ub(0, 1); w.ub(1, 1); w.ub(0, 1); w.ub(1, 1)  # moveTo + fill1
    w.ub(n, 5); w.sb(X, n); w.sb(Y, n)
    w.ub(1, 1)  # fillStyle1 = 1
    for dx, dy in ((W, 0), (0, H), (-W, 0), (0, -H)):
        v = dx or dy
        nb = max(2, sbits_needed(v))
        w.ub(1, 1); w.ub(1, 1); w.ub(nb - 2, 4); w.ub(0, 1); w.ub(1 if dy else 0, 1); w.sb(v, nb)
    w.ub(0, 6)  # end
    return Tag(2, body + w.bytes(), True)


def empty_shape(cid):
    """DefineShape that draws nothing."""
    return Tag(2, struct.pack('<H', cid) + encode_rect(0, 0, 0, 0) + bytes([0, 0, 0x00, 0x00]), True)


def place_with_alpha(depth, alpha, char=None, matrix=None, move=True):
    """PlaceObject2 with an alpha multiply colour transform (alpha 0..1)."""
    tag = place_object2(depth, char=char, matrix=matrix, move=move)
    body = bytearray(tag.body)
    body[0] |= 0x08
    w = BitWriter()
    am = round(alpha * 256)
    n = sbits_needed(256, am)
    w.ub(0, 1); w.ub(1, 1); w.ub(n, 4)
    for v in (256, 256, 256, am):
        w.sb(v, n)
    return Tag(26, bytes(body) + w.bytes(), False)
