"""Build a custom fighter SWF from an existing BVN-template fighter: reskinned bitmaps + recomposed moves.

Generalises tools/mihawk.py (ANALYSIS.md §9) so each custom fighter is just a Spec (see tools/shanks.py):
  - reskinned bitmaps (<work>/sprites/<id>.png, optional canvas padding <work>/sprites_pad.json) replace the
    originals; voice clips (<work>/voices.json) become silence;
  - new animation labels are appended to the fighter's animation sprite by copying source frame ranges (each part
    restores the source's display list from the raw creation tags, so hurtbox clip actions survive, then replays the
    source tags; controller windows and frame scripts are dropped and replaced by our own scripts through marker
    DoActions that FFDec -importScript turns into AS source);
  - overlays put extra objects on those new frames: effect sprites built from PNG sequences (<work>/fx/<name>/NN.png
    + fx/layout.json offsets) or existing characters such as a hitbox clip with an attack name and a big scale;
  - label remaps / exact-text script edits / attack-table (gjl) entries patch the existing scripts.
"""
import json
import os
import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from swfdisplay import display_lists, read_matrix  # noqa: E402
from swfnames import Bits  # noqa: E402
from swfpatch import Swf, Tag, bits_lossless2, clone_shape_with_bitmap, encode_matrix, place_object2  # noqa: E402

FFDEC = ['java', '-jar', os.path.join(ROOT, 'tools/ffdec/ffdec.jar')]
SKIP_TAGS = {1, 12, 43}  # ShowFrame, DoAction, FrameLabel: rebuilt per new frame
SILENCE = os.path.join(ROOT, 'work/mihawk/silence.mp3')

# --- AS snippets for new frames (scope = the animation sprite, like the original frame scripts) ---------------------
DIR = '(_parent._xscale > 0 ? 1 : -1)'
LIVE = '_root.zhanting == false && _root.game["p" + pn].mc.sw == false'
JPRESS = '(_parent.useAI ? attran < 110 : kis(斩) && !kis(跳) && !kis(上) && !kis(下))'
END = 'gotoAndStop("站立");\nplay();\n'
START = '动作 = 1;\nql += 5;\n'


def move(k):
    return f'if(_root.zhanting == false)\n{{\n   _parent._x += {DIR} * Math.round(speed * {k});\n}}\n'


def chain(label):
    return f'if({LIVE})\n{{\n   if({JPRESS})\n   {{\n      gotoAndPlay("{label}");\n   }}\n}}\n'


def scripts(n, start_extra='', moves=(), k=0.25, idle_at=None, chain_to=None, chain_from=None, start=START):
    """Per-frame AS for a new n-frame move (1-based offsets): start, movement, idle, combo window, end."""
    out = {i: '' for i in range(1, n + 1)}
    out[1] += start + start_extra
    for i in moves:
        out[i] += move(k)
    if idle_at:
        out[idle_at] += '动作 = 0;\n'
    if chain_to:
        for i in range(chain_from, n):
            out[i] += chain(chain_to)
    out[n] += END
    return {i: s for i, s in out.items() if s}


@dataclass
class Overlay:
    """An object shown on frames [start, end] (1-based offsets within a segment)."""
    start: int
    end: int
    depth: int
    fx: str = None          # effect sprite name from <work>/fx (built from PNG frames)
    char: int = None        # or an existing character (e.g. the hitbox clip)
    name: str = None        # instance name (hitboxes: '<attack>atm')
    matrix: tuple = (1, 0, 0, 1, 0, 0)


@dataclass
class Segment:
    label: str
    parts: list             # inclusive source frame ranges of the animation sprite
    renames: dict = field(default_factory=dict)   # hitbox instance renames
    scripts: dict = field(default_factory=dict)   # {offset: AS}
    variant: str = None     # use alternate bitmaps <work>/sprites_<variant>/ for this segment
    overlays: list = field(default_factory=list)
    drop: set = field(default_factory=set)        # more characters to leave out, like the controller (e.g. a
                                                  # base-move clip that moves the fighter)


@dataclass
class Inject:
    """An object added to EXISTING frames of the animation sprite: [(frame, matrix), ...] in frame order; placed on
    the first, moved on the others, removed on the frame after the last."""
    frames: list
    depth: int
    fx: str = None
    char: int = None
    name: str = None


@dataclass
class Spec:
    name: str
    src: str
    form: int
    controller: int
    work: str
    segments: list = field(default_factory=list)
    label_remap: list = field(default_factory=list)   # (old, new) on gotoAndPlay(...) text; '@' keeps steps apart
    script_edits: dict = field(default_factory=dict)  # {dump path: [(old, new)]}
    gjl_table: str = 'gjl1'
    gjl: dict = field(default_factory=dict)           # {attack: (pw, zl, up, x, tm, dz)}
    scales: list = field(default_factory=list)        # [((a, b), depths, k)] scale existing placements
    shape_recolor: dict = field(default_factory=dict)  # {shape id: (old bytes, new bytes)}
    fx_once: set = field(default_factory=set)          # fx sprites that stop on their last frame
    fx_hold: dict = field(default_factory=dict)        # {fx name: game frames per PNG frame} (default 1)
    fx_alias: dict = field(default_factory=dict)       # {new fx name: existing fx name} same art, own fx_hold/once
    tints: dict = field(default_factory=dict)          # {(rgb mult, rgb add): (rgb mult, rgb add)} colour transforms
    inject: list = field(default_factory=list)         # [Inject] objects added to existing frames
    marker: str = 'NEW'


# --- tag helpers ---------------------------------------------------------------------------------------------------
def frames_of(sp):
    frames, cur = [], []
    for t in sp.children:
        if t.type == 0:
            break
        if t.type == 1:
            frames.append(cur)
            cur = []
        else:
            cur.append(t)
    return frames


def placed_char(t):
    if t.type == 26 and t.body[0] & 2:
        return int.from_bytes(t.body[3:5], 'little')
    if t.type == 70 and t.body[0] & 2 and not t.body[1] & 0x18:
        return int.from_bytes(t.body[4:6], 'little')
    return None


DEPTH_AT = {26: 1, 70: 2, 28: 0, 5: 2}  # byte offset of the depth in PlaceObject2/3, RemoveObject2/1


def depth_of(t):
    off = DEPTH_AT.get(t.type)
    return None if off is None else int.from_bytes(t.body[off:off + 2], 'little')


def retarget(t, renames, swaps):
    body = bytes(t.body)
    for old, new in renames.items():
        body = body.replace(old.encode() + b'\0', new.encode() + b'\0')
    body = bytearray(body)
    c = placed_char(t)
    if c in swaps:
        off = 3 if t.type == 26 else 4
        body[off:off + 2] = swaps[c].to_bytes(2, 'little')
    return Tag(t.type, bytes(body), t.long)


def marker_tag(prefix, n):
    s = f'{prefix}{n}'.encode() + b'\0'
    return Tag(12, b'\x96' + struct.pack('<H', len(s) + 1) + b'\x00' + s + b'\x17\x00', False)


def remove_tag(depth):
    return Tag(28, struct.pack('<H', depth), False)


# --- bitmaps ---------------------------------------------------------------------------------------------------------
def bitmap_fill(tag):
    """(bitmap id, matrix) of the first bitmap fill of a DefineShape tag, or None."""
    body = tag.body
    q = 2 + (5 + 4 * (body[2] >> 3) + 7) // 8
    if tag.type == 83:  # DefineShape4: edge bounds + flags
        q += (5 + 4 * (body[q] >> 3) + 7) // 8 + 1
    count = body[q]
    q += 1
    if count == 0xFF:
        count, q = struct.unpack_from('<H', body, q)[0], q + 2
    if count and 0x40 <= body[q] <= 0x43:
        return struct.unpack_from('<H', body, q + 1)[0], read_matrix(Bits(body, q + 3))[1]
    return None


def apply_padding(swf, spec, pads, base_img):
    """Enlarged canvases (pads {bitmap id: [l, t, r, b]} in original pixels) and high-resolution reskins (a sprite PNG
    k times the padded original size, e.g. 2x art): rebuild their rectangle shapes so the original pixels stay where
    they were on screen and the PNG is drawn at 1/k scale (smoothed fill)."""
    from PIL import Image
    from swfbounds import read_rect
    from swftext import bitmap_rect_shape
    users = {}
    for shape, bmps in json.load(open(os.path.join(spec.work, 'shape_bitmaps.json'))).items():
        for b in bmps:
            users.setdefault(b, []).append(int(shape))
    sprites = os.path.join(spec.work, 'sprites')
    ids = {int(k) for k in pads} | ({int(f[:-4]) for f in os.listdir(sprites) if f.endswith('.png')}
                                    if os.path.isdir(sprites) else set())
    done = 0
    for bid in sorted(ids):
        l, t, r, b = pads.get(str(bid), (0, 0, 0, 0))
        w0, h0 = Image.open(os.path.join(base_img, f'{bid}.png')).size
        png = os.path.join(sprites, f'{bid}.png')
        pw, ph = Image.open(png).size if os.path.exists(png) else (w0 + l + r, h0 + t + b)
        k = pw / (w0 + l + r)
        if abs(ph / (h0 + t + b) - k) > 1e-6:
            raise ValueError(f'{spec.name}: sprite {bid} is {pw}x{ph}, not a uniform scale of {w0 + l + r}x{h0 + t + b}')
        if (l, t, r, b) == (0, 0, 0, 0) and k == 1:
            continue
        for shape in users.get(bid, []):
            _, _, tag = swf.find_define(shape)
            fill = bitmap_fill(tag)
            if fill and fill[0] == bid:
                a, _, _, d, tx, ty = fill[1]
                sx, sy = a / 20, d / 20  # shape px per bitmap px
                x0, y0, x1, y1 = read_rect(tag.body, 2)
                if x0 > tx + sx / 2 or y0 > ty + sy / 2 or x1 < tx + (w0 - .5) * sx or y1 < ty + (h0 - .5) * sy:
                    # the shape shows one part of the bitmap (a sheet: Kenpachi's 4 stand frames in bitmap 6):
                    # keep its own rect, only move / rescale the fill
                    swf.replace_define(shape, bitmap_rect_shape(
                        shape, bid, x0, y0, x1 - x0, y1 - y0, bitmap_px=(pw, ph),
                        fill_px=(tx - l * sx, ty - t * sy, (w0 + l + r) * sx, (h0 + t + b) * sy)))
                    done += 1
                    continue
            else:  # bitmap set in a later style-change record: use the shape rect if it is the 1:1 bitmap rect
                tx, ty, x1, y1 = read_rect(tag.body, 2)
                if (round(x1 - tx), round(y1 - ty)) != (w0, h0):
                    if k != 1:
                        raise ValueError(f'{spec.name}: shape {shape} (bitmap {bid}) is not a 1:1 bitmap rect; '
                                         f'keep sprite {bid} at the original resolution')
                    print(f'  ! {spec.name}: shape {shape} (bitmap {bid}) not a 1:1 bitmap rect, padding skipped')
                    continue
                sx = sy = 1
            swf.replace_define(shape, bitmap_rect_shape(shape, bid, tx - l * sx, ty - t * sy, (w0 + l + r) * sx,
                                                        (h0 + t + b) * sy, bitmap_px=(pw, ph)))
            done += 1
    return done


def variant_swaps(swf, spec, variant):
    """Clone single-bitmap shapes onto alternate bitmaps (<work>/sprites_<variant>/<id>.png)."""
    vdir = os.path.join(spec.work, f'sprites_{variant}')
    swaps = {}
    if not os.path.isdir(vdir):
        return swaps
    for shape, bmps in json.load(open(os.path.join(spec.work, 'shape_bitmaps.json'))).items():
        if len(bmps) == 1 and os.path.exists(os.path.join(vdir, f'{bmps[0]}.png')):
            bmp, shp = swf.new_id(), swf.new_id()
            swf.insert_before_define(spec.form, [bits_lossless2(bmp, os.path.join(vdir, f'{bmps[0]}.png'))])
            swf.insert_before_define(spec.form, [clone_shape_with_bitmap(swf, int(shape), shp, bmp)])
            swaps[int(shape)] = shp
    return swaps


def fx_sprites(swf, spec):
    """Effect sprites from <work>/fx/<name>/NN.png with fx/layout.json {name: [[x, y], ...]} (offsets from the
    fighter origin). Returns {name: sprite id}."""
    from PIL import Image
    from swftext import bitmap_rect_shape
    layout_path = os.path.join(spec.work, 'fx', 'layout.json')
    if not os.path.exists(layout_path):
        return {}
    layout = json.load(open(layout_path))
    out = {}
    entries = list(layout.items()) + [(a, layout.get(src)) for a, src in spec.fx_alias.items()]
    for name, offsets in entries:
        d = os.path.join(spec.work, 'fx', spec.fx_alias.get(name, name))
        if not isinstance(offsets, list) or not os.path.isdir(d):  # other layout data (anchors, flags)
            continue
        pngs = sorted(f for f in os.listdir(d) if f.endswith('.png'))
        shapes = []
        for png, (x, y) in zip(pngs, offsets):
            w, h = Image.open(os.path.join(d, png)).size
            bmp, shp = swf.new_id(), swf.new_id()
            swf.insert_before_define(spec.form, [bits_lossless2(bmp, os.path.join(d, png)),
                                                 bitmap_rect_shape(shp, bmp, x, y, w, h)])
            shapes.append(shp)
        hold = spec.fx_hold.get(name, 1)  # int: every frame held that long; list: [(png index, game frames), ...]
        seq = [(i, hold) for i in range(len(shapes))] if isinstance(hold, int) else hold
        kids, total = [], 0
        for k, (i, n) in enumerate(seq):
            kids.append(place_object2(1, char=shapes[i], move=k > 0))
            for h in range(n):
                if name in spec.fx_once and k == len(seq) - 1 and h == n - 1:
                    kids.append(Tag(12, b'\x07\x00', False))  # stop()
                kids.append(Tag(1, b'', False))
            total += n
        kids.append(Tag(0, b'', False))
        sid = swf.new_id()
        swf.insert_before_define(spec.form, [Tag(39, struct.pack('<HH', sid, total), True, kids)])
        out[name] = sid
    return out


# --- composition -------------------------------------------------------------------------------------------------
def compose(swf, spec, lists):
    """Append spec.segments to the animation sprite. Returns {frame number: AS source} for the new frames."""
    _, _, sp = swf.find_define(spec.form)
    frames = frames_of(sp)
    states = lists[spec.form]
    creation, history = {}, []  # depth -> creating tag, per frame
    for fr in frames:
        for t in fr:
            d = depth_of(t)
            if placed_char(t) is not None:
                creation[d] = t
            elif t.type in (5, 28):
                creation.pop(d, None)
        history.append(dict(creation))
    swaps_by_variant = {v: variant_swaps(swf, spec, v) for v in {s.variant for s in spec.segments if s.variant}}
    fx = spec.fx_ids = fx_sprites(swf, spec)

    def visible(state, drop=()):
        return {d: (e['char'], e.get('name')) for d, e in state.items()
                if e['char'] != spec.controller and e['char'] not in drop}

    current = visible(states[-1])
    new_frames, scripts_out = [], {}
    n0 = len(frames)
    for seg in spec.segments:
        sw = swaps_by_variant.get(seg.variant, {})
        out = []
        for a, b in seg.parts:
            pre = states[a - 2]
            want = {d: (sw.get(c, c), seg.renames.get(n, n)) for d, (c, n) in visible(pre, seg.drop).items()}
            trans = [remove_tag(d) for d in sorted(current) if current[d] != want.get(d)]
            for d in sorted(want):
                if current.get(d) != want[d]:
                    t = retarget(history[a - 2][d], seg.renames, sw)
                    trans.append(Tag(t.type, bytes([t.body[0] & ~1]) + t.body[1:], t.long))  # fresh placement
                trans.append(place_object2(d, matrix=pre[d]['m'], move=True))
            occupied = set(want)
            for i, f in enumerate(range(a, b + 1)):
                tags = [] if i else trans
                for t in frames[f - 1]:
                    if t.type in SKIP_TAGS:
                        continue
                    d, c = depth_of(t), placed_char(t)
                    if c == spec.controller or c in seg.drop:  # dropped window; if it replaced something there, remove that instead
                        if d in occupied:
                            tags.append(remove_tag(d))
                            occupied.discard(d)
                        continue
                    t = retarget(t, seg.renames, sw)
                    if c is not None:
                        if t.body[0] & 1 and d not in occupied:  # "replace" on an empty depth -> plain place
                            t = Tag(t.type, bytes([t.body[0] & ~1]) + t.body[1:], t.long)
                        occupied.add(d)
                    elif t.type in (5, 28):
                        occupied.discard(d)
                    tags.append(t)
                out.append(tags)
            current = {d: (sw.get(c, c), seg.renames.get(n, n))
                       for d, (c, n) in visible(states[b - 1], seg.drop).items()}
        for ov in seg.overlays:  # extra objects on this segment's frames
            char = fx[ov.fx] if ov.fx else ov.char
            if char is None:
                print(f'  ! {spec.name}: overlay {ov.fx} missing (no fx art yet), skipped')
                continue
            out[ov.start - 1].append(place_object2(ov.depth, char=char, matrix=ov.matrix, name=ov.name))
            if ov.end < len(out):
                out[ov.end].insert(0, remove_tag(ov.depth))
            else:  # still on screen when the segment ends: the next segment's transition removes it
                current[ov.depth] = (char, ov.name)
        for i, tags in enumerate(out, 1):
            fno = n0 + len(new_frames) + 1
            extra = [Tag(43, seg.label.encode() + b'\0', False)] if i == 1 else []
            if i in seg.scripts:
                extra.append(marker_tag(spec.marker, fno))
                scripts_out[fno] = seg.scripts[i]
            new_frames.append(extra + tags)
    end = len(sp.children) - 1 if sp.children[-1].type == 0 else len(sp.children)
    sp.children[end:end] = [t for fr in new_frames for t in fr + [Tag(1, b'', False)]]
    sp.frames += len(new_frames)
    return scripts_out


def _cxform(mult, add):
    """CXFORMWITHALPHA bytes for 4 mult and 4 add terms."""
    vals = list(mult) + list(add)
    n = max(max(abs(v) for v in vals).bit_length() + 1, 2)
    bits = '11' + format(n, '04b') + ''.join(format(v & ((1 << n) - 1), f'0{n}b') for v in vals)
    bits += '0' * (-len(bits) % 8)
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


def fix_tints(swf, spec):
    """Rewrite colour transforms of the animation sprite's placements (the base fighter tints white effect bitmaps
    yellow/orange; the reskinned bitmaps need them neutral or crimson). Alpha terms are kept."""
    from swfnames import skip_matrix
    _, _, sp = swf.find_define(spec.form)
    n = 0
    for i, t in enumerate(sp.children):
        if t.type != 26 or not t.body[0] & 8:
            continue
        q = 3 + (2 if t.body[0] & 2 else 0)
        if t.body[0] & 4:
            q = skip_matrix(Bits(t.body, q))[0]
        b = Bits(t.body, q)
        has_add, has_mul, nb = b.ub(1), b.ub(1), b.ub(4)
        mult = [b.sb(nb) for _ in range(4)] if has_mul else [256] * 4
        add = [b.sb(nb) for _ in range(4)] if has_add else [0] * 4
        e = b.align()
        new = spec.tints.get((tuple(mult[:3]), tuple(add[:3])))
        if new:
            body = t.body[:q] + _cxform(list(new[0]) + mult[3:], list(new[1]) + add[3:]) + t.body[e:]
            sp.children[i] = Tag(26, body, t.long)
            n += 1
    return n


def inject(swf, spec):
    """Add spec.inject objects to existing frames (after compose, so new segments never copy them)."""
    _, _, sp = swf.find_define(spec.form)
    starts, frame = {1: 0}, 1  # frame number -> index of its first tag
    for i, t in enumerate(sp.children):
        if t.type == 1:
            frame += 1
            starts[frame] = i + 1
    adds = {}
    for inj in spec.inject:
        char = spec.fx_ids.get(inj.fx) if inj.fx else inj.char
        if char is None:
            print(f'  ! {spec.name}: inject {inj.fx} missing (no fx art yet), skipped')
            continue
        for k, (f, m) in enumerate(inj.frames):
            adds.setdefault(f, []).append(place_object2(inj.depth, char=char, matrix=m, name=inj.name) if k == 0
                                          else place_object2(inj.depth, matrix=m, move=True))
        adds.setdefault(inj.frames[-1][0] + 1, []).insert(0, remove_tag(inj.depth))
    for f in sorted(adds, reverse=True):
        i = starts[f]
        sp.children[i:i] = adds[f]
    return sum(len(v) for v in adds.values())


def scale_placements(swf, spec, frame_range, depths, k):
    """Scale PlaceObject2 matrices at `depths` in animation-sprite frames [a, b) by k (about their origin)."""
    _, _, sp = swf.find_define(spec.form)
    a, b = frame_range
    frame, n = 1, 0
    for i, t in enumerate(sp.children):
        if t.type == 1:
            frame += 1
            continue
        if not (a <= frame < b and t.type == 26 and t.body[0] & 4 and depth_of(t) in depths):
            continue
        q = 3 + (2 if t.body[0] & 2 else 0)
        end, (ma, mb, mc, md, tx, ty) = read_matrix(Bits(t.body, q))
        sp.children[i] = Tag(26, t.body[:q] + encode_matrix(ma * k, mb * k, mc * k, md * k, tx, ty) + t.body[end:],
                             t.long)
        n += 1
    return n


def gjl_lines(spec):
    out = ['', f'// {spec.name} move table (tools/fighter_builder.py)']
    for k, (pw, zl, up, x, tm, dz) in spec.gjl.items():
        g = spec.gjl_table
        out += [f'{g}.{k}pw = {pw};', f'{g}.{k}zl = {zl};', f'{g}.{k}up = {up};', f'{g}.{k}x = {x};',
                f'{g}.{k}tm = {tm};', f'{g}.{k}dz = "{dz}";']
    return '\n'.join(out) + '\n'


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or 'SEVERE' in r.stderr:
        raise RuntimeError(f'{cmd[:6]} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}')


def build(spec, out_swf, tmp, base_img):
    """base_img: directory of the base fighter's original bitmaps (FFDec image export), for padded sizes."""
    os.makedirs(tmp, exist_ok=True)
    swf = Swf.load(spec.src)
    pad_file = os.path.join(spec.work, 'sprites_pad.json')  # before compose: variant clones copy padded shapes
    padded = apply_padding(swf, spec, json.load(open(pad_file)), base_img) if os.path.exists(pad_file) else 0
    tinted = fix_tints(swf, spec) if spec.tints else 0  # before compose: copied frames get the fixed transforms
    new_scripts = compose(swf, spec, display_lists(spec.src))
    injected = inject(swf, spec) if spec.inject else 0
    scaled = sum(scale_placements(swf, spec, *s) for s in spec.scales)
    for sid, (old, new) in spec.shape_recolor.items():
        lst, i, tag = swf.find_define(sid)
        assert old in tag.body, sid
        lst[i] = Tag(tag.type, tag.body.replace(old, new), tag.long)
    stage1, stage2 = (os.path.join(tmp, f'{spec.name}_stage{i}.swf') for i in (1, 2))
    sprites = os.path.join(spec.work, 'sprites')
    pairs = sorted(int(f[:-4]) for f in os.listdir(sprites) if f.endswith('.png')) if os.path.isdir(sprites) else []
    for cid in pairs:  # reskinned bitmaps, encoded here (FFDec -replace misreads some PNGs as CMYK JPEG)
        swf.replace_define(cid, bits_lossless2(cid, os.path.join(sprites, f'{cid}.png')))
    swf.save(stage1)
    vfile = os.path.join(spec.work, 'voices.json')
    voices = json.load(open(vfile))['voices'] if os.path.exists(vfile) else []
    args = os.path.join(tmp, f'{spec.name}_replace.txt')
    with open(args, 'w') as f:
        for cid in voices:
            f.write(f'{cid}\n{SILENCE}\n')
    if voices:
        run(FFDEC + ['-replace', stage1, stage2, args])
    else:
        shutil.copy(stage1, stage2)
    dump = os.path.join(tmp, f'{spec.name}_dump')
    shutil.rmtree(dump, ignore_errors=True)
    run(FFDEC + ['-export', 'script', dump, stage2])
    sdir = os.path.join(dump, 'scripts')
    imp = os.path.join(tmp, f'{spec.name}_import')
    shutil.rmtree(imp, ignore_errors=True)
    edited = {}
    for top in (f'DefineSprite_{spec.form}', f'DefineSprite_{spec.controller}'):
        for r, _, fs in os.walk(os.path.join(sdir, top)):
            for fn in fs:
                rel = os.path.relpath(os.path.join(r, fn), sdir)
                txt = open(os.path.join(r, fn), encoding='utf-8').read()
                new = txt
                for a, b in spec.label_remap:
                    new = new.replace(a, b)
                new = new.replace('gotoAndPlay("@', 'gotoAndPlay("')
                if new != txt:
                    edited[rel] = new
    for rel, edits in spec.script_edits.items():
        txt = edited.get(rel) or open(os.path.join(sdir, rel), encoding='utf-8').read()
        for a, b in edits:
            assert a in txt, f'{rel}: anchor not found: {a[:50]!r}'
            txt = txt.replace(a, b, 1)
        edited[rel] = txt
    if spec.gjl:
        root = 'frame_1/DoAction.as'
        edited[root] = open(os.path.join(sdir, root), encoding='utf-8').read() + gjl_lines(spec)
    for fno, src in new_scripts.items():
        rel = f'DefineSprite_{spec.form}/frame_{fno}/DoAction.as'
        assert f'{spec.marker}{fno}' in open(os.path.join(sdir, rel), encoding='utf-8').read(), rel
        edited[rel] = src
    for rel, txt in edited.items():
        os.makedirs(os.path.join(imp, 'scripts', os.path.dirname(rel)), exist_ok=True)
        open(os.path.join(imp, 'scripts', rel), 'w', encoding='utf-8').write(txt)
    run(FFDEC + ['-importScript', stage2, out_swf, imp])
    return {'new_frames': len(new_scripts), 'edited': len(edited), 'bitmaps': len(pairs), 'padded_shapes': padded,
            'scaled': scaled, 'injected': injected, 'tinted': tinted}
