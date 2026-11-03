"""Dracule Mihawk (쥬라큘 미호크): a new fighter built from the Bankai form of game/fighter/yihu.swf.

usage (normally called from tools/build.py): tools/venv/bin/python tools/mihawk.py <out.swf>

Inputs  game/fighter/yihu.swf            base fighter (form 2 = Bankai, sprite 1180, controller sprite 651)
        work/mihawk/sprites/<id>.png      reskinned bitmaps (work/mihawk/render_sprites.py)
        work/mihawk/sprites_purple/<id>.png  violet-trail copies of the 跳招2 bitmaps, used by the grounded S+J
        work/mihawk/voices.json, silence.mp3  Ichigo's voice clips (spectrogram-classified) are replaced by silence
Moves   J 砍1→砍2→砍3; hidden J J J then W+J W+J (within 1 s) → 砍4→砍5 (new labels composed from 招3 / 上必杀
        frames); J after 砍5 → 砍1
        W+J 砍技2, S+J 冲砍 (new, grounded 跳招2), U 招1→招12, W+U 砍技1 (launcher), S+U 招2 (short dash slash),
        air U / air S+U 跳招→跳招2 (plunge + blue landing slash), I and W+I 必杀, S+I 超必杀, O 招换; 万解 disabled.
New labels are appended to sprite 1180 by copying source frame ranges: each part first restores the source's
display list (raw creation tags, so hurtbox clip actions survive), then replays the source tags. Controller
windows (sprite 651 with clip actions) and frame scripts of copied frames are dropped; the new frames get their own
scripts (movement, combo windows, end) through marker DoActions that are replaced via FFDec -importScript.
"""
import json
import os
import re
import shutil
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from swfdisplay import display_lists  # noqa: E402
from swfpatch import Swf, Tag, bits_lossless2, clone_shape_with_bitmap, place_object2  # noqa: E402

SRC = os.path.join(ROOT, 'game/fighter/yihu.swf')
WORK = os.path.join(ROOT, 'work/mihawk')
FFDEC = ['java', '-jar', os.path.join(ROOT, 'tools/ffdec/ffdec.jar')]
FORM, CONTROLLER = 1180, 651
SKIP_TAGS = {1, 12, 43}  # ShowFrame, DoAction, FrameLabel: rebuilt per new frame

DIR = '(_parent._xscale > 0 ? 1 : -1)'
LIVE = '_root.zhanting == false && _root.game["p" + pn].mc.sw == false'
JPRESS = '(_parent.useAI ? attran < 110 : kis(斩) && !kis(跳) && !kis(上) && !kis(下))'


def move(k):
    return f'if(_root.zhanting == false)\n{{\n   _parent._x += {DIR} * Math.round(speed * {k});\n}}\n'


WJPRESS = '(_parent.useAI ? attran < 110 : kis(斩) && kis(上))'  # W+J


def chain(label, press=JPRESS):
    return f'if({LIVE})\n{{\n   if({press})\n   {{\n      gotoAndPlay("{label}");\n   }}\n}}\n'


END = 'gotoAndStop("站立");\nplay();\n'
START = '动作 = 1;\nql += 5;\n'


def scripts(n, start_extra='', moves=(), k=0.25, idle_at=None, chain_to=None, chain_from=None, press=JPRESS):
    """Per-frame AS for a new n-frame move (1-based offsets)."""
    out = {i: '' for i in range(1, n + 1)}
    out[1] += START + start_extra
    for i in moves:
        out[i] += move(k)
    if idle_at:
        out[idle_at] += '动作 = 0;\n'
    if chain_to:
        for i in range(chain_from, n):
            out[i] += chain(chain_to, press)
    out[n] += END
    return {i: s for i, s in out.items() if s}


# label, parts (inclusive source frame ranges of sprite 1180), hitbox renames, frame scripts
SEGMENTS = [
    ('砍4', [(425, 441)], {'zh3atm': 'k4atm'},
     scripts(17, moves=range(2, 8), k=0.25, start_extra='', idle_at=12, chain_to='砍5', chain_from=11, press=WJPRESS)
     | {8: '_root.shine(0);\n', 17: 'mhJ4 = getTimer();\n' + END}),
    ('砍5', [(547, 560), (604, 611)], {'sbsatm': 'k5atm'},
     scripts(22, start_extra='_root.shine(0);\n', moves=range(1, 13), k=0.3, idle_at=15, chain_to='砍1', chain_from=13)),
    ('冲砍', [(151, 164)], {'tzatm': 'sbsatm'},
     scripts(14, moves=range(1, 7), k=2.2, idle_at=8)),
]
PURPLE_FRAMES = {'冲砍'}  # segments whose 跳招2 art uses the violet-trail bitmap copies

# I / W+I (必杀) and S+I (超必杀): keep the stage dark (the engine's super-move look: blackStg hides bgmc/fgmc and
# shows blackMu frame 2) from the end of the built-in freeze (bsw/cbsw) until the attack ends (动作 = 0).
# Ownership: _root.mhDark = pn (pn = this fighter's opponent number, so it is distinct per side in a mirror match).
# Heavy hits pause the game and their effect clip calls resumeGame() -> resumeBlackStg(), so a watcher clip re-darkens
# every frame while the move runs (only when no freeze is active and blackMu is back on frame 1). It hands the stage
# to the KO flow when someone is KO'd, and lifts the darkness when Mihawk leaves the move's frames.
# LIGHTEN runs at the move end, on the hurt labels (hit / launched / knocked down) and in the 站立 loop, and only lifts
# a darkness this fighter still owns and that nothing else is using: no freeze running (zhanting: another bsd, pause,
# KO) and blackMu still on the plain-black frame 2 (KO shows frame "KO" = 5, which KOend restores).
LIFT = 'if(_root.zhanting == false && _root.blackMu._currentframe == 2)\n{\n   _root.resumeBlackStg();\n}\n'


def indent(s, n):
    return re.sub('^(?=.)', ' ' * n, s, flags=re.M)


LIGHTEN = 'if(_root.mhDark == pn)\n{\n   _root.mhDark = 0;\n' + indent(LIFT, 3) + '}\n'


def darken(first, last):
    """DARKEN for a move whose label spans frames first..last of sprite 1180."""
    watch = ('var m = this._parent;\n'
             'if(_root.mhDark != m.pn)\n{\n   this.removeMovieClip();\n   return undefined;\n}\n'
             'if(m.sw == true || _root.game["p" + m.pn].mc.sw == true)\n'  # KO: KOplay/KOend own the stage now
             '{\n   _root.mhDark = 0;\n   this.removeMovieClip();\n   return undefined;\n}\n'
             'if(m._currentframe < this.a || m._currentframe > this.b)\n'  # left the move some other way
             '{\n   _root.mhDark = 0;\n' + indent(LIFT, 3) + '   this.removeMovieClip();\n   return undefined;\n}\n'
             'if(_root.zhanting == false && _root.blackMu._currentframe == 1)\n{\n   _root.blackStg();\n}\n')
    return ('if(_root.zhanting == false)\n{\n   _root.mhDark = pn;\n   _root.blackStg();\n'
            '   var w = this.createEmptyMovieClip("mhDarkW", 16000);\n'
            f'   w.a = {first};\n   w.b = {last};\n'
            '   w.onEnterFrame = function()\n   {\n' + indent(watch, 6) + '   };\n}\n')


DARK_EDITS = {
    474: [('bs = 0;', 'bs = 0;\n' + darken(458, 526))],  # 必杀: freeze over
    495: [('动作 = 0;', '动作 = 0;\n' + LIGHTEN)],  # 必杀: slash done
    646: [('bs = 0;', 'bs = 0;\n' + darken(622, 726))],  # 超必杀: freeze over (cbsw)
    681: [('动作 = 0;', '动作 = 0;\n' + LIGHTEN)],  # 超必杀: wave fading out
    2: [('hits = 0;', 'hits = 0;\n' + LIGHTEN)],  # 站立 loop (fallback for any other way out)
    786: [('play();', LIGHTEN + 'play();')],  # 被打
    799: [('hited = 0;', LIGHTEN + 'hited = 0;')],  # 击飞
    811: [('_root.touchFloorEffect(_parent);', LIGHTEN + '_root.touchFloorEffect(_parent);')],  # 击落地
}

# Hidden J4/J5 (user 2026-11-03: J J J, then W+J W+J within 1 s -> the 4th and 5th slashes; plain W+J stays 砍技2):
# 砍3's late window takes W+J to 砍4, and 砍3's last frame stamps mhJ3 = getTimer(); 砍4 takes W+J to 砍5 in its
# window and stamps mhJ4 on its last frame. Standing W+J within 1000 ms of a stamp goes to 砍5 / 砍4 instead of 砍技2.
W_J = '   if(skill2())\n   {\n      _parent.gotoAndPlay("砍技2");\n   }\n'
W_J_HIDDEN = ('   if(skill2())\n   {\n      if(getTimer() - _parent.mhJ4 < 1000)\n      {\n         _parent.mhJ4 = 0;\n'
              '         _parent.gotoAndPlay("砍5");\n      }\n      else if(getTimer() - _parent.mhJ3 < 1000)\n      {\n'
              '         _parent.mhJ3 = 0;\n         _parent.gotoAndPlay("砍4");\n      }\n      else\n      {\n'
              '         _parent.gotoAndPlay("砍技2");\n      }\n   }\n')

# edits to existing scripts (exported paths of the FFDec script dump), applied as exact text replacements
LABEL_REMAP = [('gotoAndPlay("砍技1")', 'gotoAndPlay("@冲砍")'), ('gotoAndPlay("招3")', 'gotoAndPlay("@砍技1")'),
               ('gotoAndPlay("上必杀")', 'gotoAndPlay("@必杀")')]  # S+J, W+U, W+I (the '@' keeps steps apart)
SCRIPT_EDITS = {
    f'DefineSprite_{CONTROLLER}/frame_1/DoAction.as': [  # no transformation into the hollow form; hidden J4/J5
        ('return _parent.ql >= 300 && _parent.kis(_parent.斩) && _parent.kis(_parent.跳);', 'return false;'),
        (W_J, W_J_HIDDEN), (W_J, W_J_HIDDEN)],  # doStand, doAllAction
    'DefineSprite_1180/frame_219/PlaceObject2_651_34/CLIPACTIONRECORD onClipEvent(enterFrame).as': [  # 砍3 W+J → 砍4
        ('   if(gameRunning())\n   {\n', '   if(gameRunning())\n   {\n      if(skill2())\n      {\n'
         '         _parent.mhJ3 = 0;\n         _parent.gotoAndPlay("砍4");\n      }\n')],
    'DefineSprite_1180/frame_230/DoAction.as': [('gotoAndStop("站立");', 'mhJ3 = getTimer();\ngotoAndStop("站立");')],
    'DefineSprite_1180/frame_351/PlaceObject2_651_33/CLIPACTIONRECORD onClipEvent(enterFrame).as': [  # S+U: short dash
        ('_parent.speed * 6.5', '_parent.speed * 3'), ('_parent.speed * 6.5', '_parent.speed * 3')],
    'DefineSprite_1180/frame_461/DoAction.as': [('"一户1"', '"米霍克1"')],
    'DefineSprite_1180/frame_625/DoAction.as': [('"一户万解1"', '"米霍克2"')],
    'DefineSprite_1180/frame_646/DoAction.as': [('_root.cbsw(pn);', '_root.cbsw(pn);\n_root.shake(6,10);')],  # S+I beat
    'DefineSprite_1180/frame_651/DoAction.as': [('_root._y = 0;', '_root._y = 0;\n_root.shake(12,18);')],  # S+I slash
}
for _f, _e in DARK_EDITS.items():
    SCRIPT_EDITS.setdefault(f'DefineSprite_{FORM}/frame_{_f}/DoAction.as', []).extend(_e)
SI_WAVE = ((648, 680), {28, 30}, 1.3)
# vector streak shapes inside the S+I wave sprite 1038: solid violet fill pairs -> the blue wave's palette
SHAPE_RECOLOR = {sid: (bytes.fromhex('003f2e81' '00120d26'), bytes.fromhex('005ac8ff' '001034be')) for sid in (1034, 1037)}  # S+I: wave sprite (depth 30) and its hitbox cbsatm (depth 28) scaled up
GJL = {  # Bankai attack table additions / overrides (pw damage, zl stun, up launch, x push, tm, dz reaction)
    'k4': (40, 1, 0, 3, 400, '被打'), 'k5': (55, 2, 0, 6, 450, '被打'), 'sbs': (60, 3, 0, 6, 400, '被打'),
    'kj1': (70, 6, 12, 2, 0, '击飞'),
}


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


def depth_of(t):
    if t.type in (26,):
        return int.from_bytes(t.body[1:3], 'little')
    if t.type == 70:
        return int.from_bytes(t.body[2:4], 'little')
    if t.type == 28:
        return int.from_bytes(t.body[0:2], 'little')
    if t.type == 5:
        return int.from_bytes(t.body[2:4], 'little')
    return None


def retarget(t, renames, swaps):
    body = bytearray(t.body)
    for old, new in renames.items():
        body = bytearray(bytes(body).replace(old.encode() + b'\0', new.encode() + b'\0'))
    c = placed_char(t)
    if c in swaps:
        off = 3 if t.type == 26 else 4
        body[off:off + 2] = swaps[c].to_bytes(2, 'little')
    return Tag(t.type, bytes(body), t.long)


def marker(n):
    s = f'MHK{n}'.encode() + b'\0'
    return Tag(12, b'\x96' + struct.pack('<H', len(s) + 1) + b'\x00' + s + b'\x17\x00', False)


def compose(swf, lists, purple_dir):
    """Append SEGMENTS to the Bankai sprite. Returns {frame number: AS source} for the new frames."""
    _, _, sp = swf.find_define(FORM)
    frames = frames_of(sp)
    states = lists[FORM]
    creation, history = {}, []  # depth -> creating tag, per frame
    for fr in frames:
        for t in fr:
            d = depth_of(t)
            if placed_char(t) is not None:
                creation[d] = t
            elif t.type in (5, 28):
                creation.pop(d, None)
        history.append(dict(creation))
    swaps = {}
    if purple_dir and os.path.isdir(purple_dir):  # violet copies of the 跳招2 art for the grounded S+J
        sb = json.load(open(os.path.join(WORK, 'shape_bitmaps.json')))
        for shape, bmps in sb.items():
            if len(bmps) == 1 and os.path.exists(os.path.join(purple_dir, f'{bmps[0]}.png')):
                bmp, shp = swf.new_id(), swf.new_id()
                swf.insert_before_define(FORM, [bits_lossless2(bmp, os.path.join(purple_dir, f'{bmps[0]}.png'))])
                swf.insert_before_define(FORM, [clone_shape_with_bitmap(swf, int(shape), shp, bmp)])
                swaps[int(shape)] = shp

    def visible(state):
        return {d: (e['char'], e.get('name')) for d, e in state.items() if e['char'] != CONTROLLER}

    current = visible(states[-1])
    new_frames, scripts_out = [], {}
    n0 = len(frames)
    for label, parts, renames, frame_scripts in SEGMENTS:
        sw = swaps if label in PURPLE_FRAMES else {}
        seg = []
        for a, b in parts:
            pre = states[a - 2]
            want = {d: (sw.get(c, c), renames.get(n, n)) for d, (c, n) in visible(pre).items()}
            trans = [Tag(28, struct.pack('<H', d), False) for d in sorted(current) if current[d] != want.get(d)]
            for d in sorted(want):
                if current.get(d) != want[d]:
                    t = retarget(history[a - 2][d], renames, sw)
                    trans.append(Tag(t.type, bytes([t.body[0] & ~1]) + t.body[1:], t.long))  # fresh placement
                trans.append(place_object2(d, matrix=pre[d]['m'], move=True))
            occupied = set(want)
            for i, f in enumerate(range(a, b + 1)):
                tags = [] if i else trans
                for t in frames[f - 1]:
                    if t.type in SKIP_TAGS:
                        continue
                    d, c = depth_of(t), placed_char(t)
                    if c == CONTROLLER:  # dropped window; if it replaced something there, remove that instead
                        if d in occupied:
                            tags.append(Tag(28, struct.pack('<H', d), False))
                            occupied.discard(d)
                        continue
                    t = retarget(t, renames, sw)
                    if c is not None:
                        if t.body[0] & 1 and d not in occupied:  # "replace" on an empty depth -> plain place
                            t = Tag(t.type, bytes([t.body[0] & ~1]) + t.body[1:], t.long)
                        occupied.add(d)
                    elif t.type in (5, 28):
                        occupied.discard(d)
                    tags.append(t)
                seg.append(tags)
            current = {d: (sw.get(c, c), renames.get(n, n)) for d, (c, n) in visible(states[b - 1]).items()}
        for i, tags in enumerate(seg, 1):
            fno = n0 + len(new_frames) + 1
            extra = [Tag(43, label.encode() + b'\0', False)] if i == 1 else []
            if i in frame_scripts:
                extra.append(marker(fno))
                scripts_out[fno] = frame_scripts[i]
            new_frames.append(extra + tags)
    end = len(sp.children) - 1 if sp.children[-1].type == 0 else len(sp.children)
    sp.children[end:end] = [t for fr in new_frames for t in fr + [Tag(1, b'', False)]]
    sp.frames += len(new_frames)
    return scripts_out


def bitmap_fill(tag):
    """(bitmap id, (a, b, c, d, tx, ty)) of the first bitmap fill of a DefineShape tag, or None."""
    from swfdisplay import read_matrix
    from swfnames import Bits
    body = tag.body
    q = 2 + (5 + 4 * (body[2] >> 3) + 7) // 8
    if tag.type == 83:  # DefineShape4: edge bounds + flags
        q += (5 + 4 * (body[q] >> 3) + 7) // 8 + 1
    count = body[q]
    q += 1
    if count == 0xFF:
        count, q = struct.unpack_from('<H', body, q)[0], q + 2
    for _ in range(count):
        ftype = body[q]
        if 0x40 <= ftype <= 0x43:
            return struct.unpack_from('<H', body, q + 1)[0], read_matrix(Bits(body, q + 3))[1]
        return None  # only single-fill sprite shapes are handled
    return None


def apply_padding(swf, pads):
    """Sprites whose canvas was enlarged (Yoru is longer than the katana): rebuild their rectangle shapes so the
    original pixels stay where they were. pads: {bitmap id: [left, top, right, bottom]} in bitmap pixels."""
    from PIL import Image
    from swfbounds import read_rect
    from swftext import bitmap_rect_shape
    sb = json.load(open(os.path.join(WORK, 'shape_bitmaps.json')))
    users = {}
    for shape, bmps in sb.items():
        for b in bmps:
            users.setdefault(b, []).append(int(shape))
    done = 0
    for bid, (l, t, r, b) in ((int(k), v) for k, v in pads.items()):
        w0, h0 = Image.open(os.path.join(WORK, 'base/img', f'{bid}.png')).size
        for shape in users.get(bid, []):
            _, _, tag = swf.find_define(shape)
            fill = bitmap_fill(tag)
            if fill and fill[0] == bid:
                a, _, _, d, tx, ty = fill[1]
                sx, sy = a / 20, d / 20  # shape px per bitmap px
            else:  # bitmap set in a later style-change record: use the shape rect if it is the 1:1 bitmap rect
                tx, ty, x1, y1 = read_rect(tag.body, 2)
                if (round(x1 - tx), round(y1 - ty)) != (w0, h0):
                    print(f'  ! mihawk: shape {shape} (bitmap {bid}) not a 1:1 bitmap rect, padding skipped')
                    continue
                sx = sy = 1
            swf.replace_define(shape, bitmap_rect_shape(shape, bid, tx - l * sx, ty - t * sy, (w0 + l + r) * sx,
                                                        (h0 + t + b) * sy, bitmap_px=(w0 + l + r, h0 + t + b)))
            done += 1
    return done


def scale_placements(swf, frame_range, depths, k):
    """Scale the matrices of PlaceObject2 tags at `depths` within sprite FORM frames [a, b) by k (about their origin)."""
    from swfdisplay import read_matrix
    from swfnames import Bits
    from swfpatch import encode_matrix
    _, _, sp = swf.find_define(FORM)
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
        sp.children[i] = Tag(26, t.body[:q] + encode_matrix(ma * k, mb * k, mc * k, md * k, tx, ty) + t.body[end:], t.long)
        n += 1
    return n


def gjl_lines():
    out = ['', '// Mihawk move table (tools/mihawk.py)']
    for k, (pw, zl, up, x, tm, dz) in GJL.items():
        out += [f'gjl2.{k}pw = {pw};', f'gjl2.{k}zl = {zl};', f'gjl2.{k}up = {up};', f'gjl2.{k}x = {x};',
                f'gjl2.{k}tm = {tm};', f'gjl2.{k}dz = "{dz}";']
    return '\n'.join(out) + '\n'


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or 'SEVERE' in r.stderr:
        raise RuntimeError(f'{cmd[:6]} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}')


def build(out_swf, tmp):
    os.makedirs(tmp, exist_ok=True)
    swf = Swf.load(SRC)
    pad_file = os.path.join(WORK, 'sprites_pad.json')  # before compose: the purple clones copy padded shapes
    padded = apply_padding(swf, json.load(open(pad_file))) if os.path.exists(pad_file) else 0
    new_scripts = compose(swf, display_lists(SRC), os.path.join(WORK, 'sprites_purple'))
    scaled = scale_placements(swf, *SI_WAVE)
    for sid, (old, new) in SHAPE_RECOLOR.items():  # fill-style arrays (byte aligned) holding the two solid fills
        lst, i, tag = swf.find_define(sid)
        assert old in tag.body, sid
        lst[i] = Tag(tag.type, tag.body.replace(old, new), tag.long)
    stage1, stage2 = os.path.join(tmp, 'mihawk_stage1.swf'), os.path.join(tmp, 'mihawk_stage2.swf')
    swf.save(stage1)
    sprites = os.path.join(WORK, 'sprites')
    pairs = sorted(int(f[:-4]) for f in os.listdir(sprites) if f.endswith('.png')) if os.path.isdir(sprites) else []
    voices = json.load(open(os.path.join(WORK, 'voices.json')))['voices']  # Ichigo's voice clips -> silence
    args = os.path.join(tmp, 'mihawk_replace.txt')
    with open(args, 'w') as f:
        for cid in pairs:
            f.write(f'{cid}\n{os.path.join(sprites, f"{cid}.png")}\nlossless2\n')
        for cid in voices:
            f.write(f'{cid}\n{os.path.join(WORK, "silence.mp3")}\n')
    run(FFDEC + ['-replace', stage1, stage2, args])
    dump = os.path.join(tmp, 'mihawk_dump')
    shutil.rmtree(dump, ignore_errors=True)
    run(FFDEC + ['-export', 'script', dump, stage2])
    sdir = os.path.join(dump, 'scripts')
    imp = os.path.join(tmp, 'mihawk_import')
    shutil.rmtree(imp, ignore_errors=True)

    def emit(rel, text):
        os.makedirs(os.path.join(imp, 'scripts', os.path.dirname(rel)), exist_ok=True)
        open(os.path.join(imp, 'scripts', rel), 'w', encoding='utf-8').write(text)

    edited = {}
    for top in (f'DefineSprite_{FORM}', f'DefineSprite_{CONTROLLER}'):
        for r, _, fs in os.walk(os.path.join(sdir, top)):
            for fn in fs:
                rel = os.path.relpath(os.path.join(r, fn), sdir)
                txt = open(os.path.join(r, fn), encoding='utf-8').read()
                new = txt
                for a, b in LABEL_REMAP:
                    new = new.replace(a, b)
                new = new.replace('gotoAndPlay("@', 'gotoAndPlay("')
                if new != txt:
                    edited[rel] = new
    for rel, edits in SCRIPT_EDITS.items():
        txt = edited.get(rel) or open(os.path.join(sdir, rel), encoding='utf-8').read()
        for a, b in edits:
            assert a in txt, f'{rel}: anchor not found: {a[:50]!r}'
            txt = txt.replace(a, b, 1)
        edited[rel] = txt
    root = 'frame_1/DoAction.as'
    edited[root] = open(os.path.join(sdir, root), encoding='utf-8').read() + gjl_lines()
    found = set()
    for fno, src in new_scripts.items():
        rel = f'DefineSprite_{FORM}/frame_{fno}/DoAction.as'
        txt = open(os.path.join(sdir, rel), encoding='utf-8').read()
        assert f'MHK{fno}' in txt, rel
        edited[rel] = src
        found.add(fno)
    for rel, txt in edited.items():
        emit(rel, txt)
    run(FFDEC + ['-importScript', stage2, out_swf, imp])
    return {'new_frames': len(new_scripts), 'edited': len(edited), 'bitmaps': len(pairs), 'padded_shapes': padded, 'si_scaled': scaled}


if __name__ == '__main__':
    print(build(sys.argv[1], os.path.join(ROOT, 'work/build')))
