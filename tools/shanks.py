"""Shanks (샹크스): a custom fighter built from Kenpachi (game/fighter/jianba.swf, animation sprite 514).

usage (normally called from tools/build.py): tools/venv/bin/python tools/shanks.py <out.swf>

Inputs  work/shanks/sprites/<id>.png, sprites_pad.json   reskin (work/shanks/render_sprites.py)
        work/shanks/fx/<name>/NN.png, fx/layout.json     effects (work/shanks/render_fx.py)
        work/shanks/voices.json                          Kenpachi's voice clips -> silence
Moves (user spec 2026-11-02; Mihawk = thin fast violet blade, Shanks = heavy black-red Haoshoku Haki)
  J      Kenpachi's 3-hit chain 砍1-3 + a black-red aura on the blade; J after the 3rd hit loops back to 1
         (1 2 3 1 ...); the 3rd hit pushes the opponent away so the loop does not lock.
  W+J    冲天斩: rising crescent (砍技1 frames) while dashing diagonally up-forward; launches; then falls.
  S+J    冲斩 on the ground: short dash + slash (砍技2/21 frames without Kenpachi's teleport);
         空斩 in the air: a black-red slash flying diagonally down that bursts where it meets the floor.
  U      霸斩: slow Haki-charged heavy slash (必杀 wind-up + swing, no wave) that breaks guard (zl > 10).
  W+U    飞斩: rising slash that fires a black-red blade diagonally up (fx wu_launch / wu_slash).
  S+U    霸王色: he stands, then plants himself facing front, coat blown out (超必杀1 burst pose, user 2026-11-02:
         "기를 내뿜는 모션", not 招3's leg-up pose) while the Conqueror's Haki dome (fx haki_ring) hits all around.
  I, W+I Kenpachi's 必杀 / 上必杀 (black-red by the reskin).
  S+I    神避 Kamusari: freeze + scarred-eye cut-in while a crimson Haki eagle spreads over him with black-red
         lightning, then a screen-covering black-red slash (one giant hitbox), flash, shakes, dark veil.
Kenpachi's input → label map: skill2 (W+J) 砍技2, skill1 (S+J) 砍技1, magichit1 (U) 招1, magichit2 (S+U) 招2,
magichit3 (W+U) 招3, bishaSuper (S+I) 超必杀.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import fighter_builder as fb  # noqa: E402
from fighter_builder import Inject, Overlay, Segment, Spec  # noqa: E402

WORK = os.path.join(ROOT, 'work/shanks')
FORM, CONTROLLER, HITBOX = 514, 13, 216  # animation sprite, input controller, attack-box clip (66x40 px at 0,0)
MOVER = 143  # clip whose enterFrame moves the fighter (moveX/moveY) inside some of Kenpachi's moves
HB_W, HB_H = 65.95, 40.5
FEET = 24  # the animation sprite sits at (-0.65, -23.9) in the fighter: fx offsets (relative to his feet) get +24
LAYOUT = json.load(open(os.path.join(WORK, 'fx', 'layout.json')))
FAR = (1, 0, 0, 1, 0, -3000)  # parked attack box (moved into place by script)
STAGE_FIT = 'var p0 = {x:0, y:0};\nvar p1 = {x:600, y:400};\nthis.globalToLocal(p0);\nthis.globalToLocal(p1);\n'
FIT_ONE = 'N._x = p0.x;\nN._y = p0.y;\nN._xscale = (p1.x - p0.x) / 6;\nN._yscale = (p1.y - p0.y) / 4;\n'
FLOOR = '(_root.floorY - _parent._y + 24)'  # floor line in this sprite's coordinates


def stage_fit(*names):
    return STAGE_FIT + ''.join(FIT_ONE.replace('N.', n + '.') for n in names)


def ticks(seq):
    """[(png index, game frames)] -> png index per game frame"""
    return [i for i, n in seq for _ in range(n)]


def box_at(name, cx, cy, w, h):
    """AS placing attack box `name` (the 66x40 clip) over the rectangle centred on (cx, cy)."""
    return (f'{name}._x = {cx - w / 2:.1f};\n{name}._y = {cy - h / 2:.1f};\n'
            f'{name}._xscale = {w / HB_W * 100:.1f};\n{name}._yscale = {h / HB_H * 100:.1f};\n')


def new_scripts(n):
    return {i: '' for i in range(1, n + 1)}


def done(s):
    return {i: v for i, v in s.items() if v}


# --- 神避 Kamusari (S+I) --------------------------------------------------------------------------------------------
# parts: Kenpachi's super freeze/charge (706-752) then his giant-slash follow-through (926-966) -> 47 + 41 frames
FREEZE, SLASH_AT, N = 47, 50, 88
EAGLE_SEQ = [(0, 3), (1, 3), (2, 3), (3, 3), (4, 4), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3),  # rise, spread, hold
             (10, 4), (11, 2), (12, 2), (13, 3)]                                               # wind-up, dive, hit
SLASH_SEQ = [(0, 1), (1, 2), (2, 2), (3, 2), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3)]
FLASH_SEQ = [(0, 1), (1, 1), (2, 2), (3, 2)]
EAGLE_AT = FREEZE + 1 - sum(n for _, n in EAGLE_SEQ)  # the comet hits the blade as the freeze ends
SLASH_LEN, FLASH_LEN = sum(n for _, n in SLASH_SEQ), sum(n for _, n in FLASH_SEQ)
HIT = (SLASH_AT + 6, SLASH_AT + 16)  # one screen-sized attack box while the crescent is near its peak (frames 03-06)


def kamusari():
    s = new_scripts(N)
    s[1] += '动作 = 3;\nbs = 1;\nql -= 300;\n'
    s[3] += '_root.cbsd(pn);\n_root.showFace(pn,"香克斯2");\n'
    s[FREEZE] += '_root.cbsw(pn);\nbs = 0;\n_root.shake(8,12);\n'
    s[SLASH_AT] += '_root.shine(16711680);\n_root.shake(16,24);\n'
    s[SLASH_AT + 8] += '_root.shake(10,14);\n'
    s[SLASH_AT + 28] += '动作 = 0;\n'
    s[N] += fb.END
    for i in range(FREEZE, SLASH_AT + SLASH_LEN):  # veil (+ flash) follow the camera every frame
        s[i] += stage_fit('kmVeil', *(['kmFlash'] if SLASH_AT <= i < SLASH_AT + FLASH_LEN else []))
    eagle = [Overlay(EAGLE_AT, FREEZE, 12, fx='eagle')]  # behind his pose (depth 27); veil below it
    bolts = [Overlay(EAGLE_AT + 6 + 4 * k, FREEZE + 2, 61 + k, fx='lightning', matrix=(1, 0, 0, 1, x, y))
             for k, (x, y) in enumerate(LAYOUT['lightning_anchors_eagle'])]
    slash = [Overlay(SLASH_AT, SLASH_AT + SLASH_LEN - 1, 66, fx='slash'),
             Overlay(SLASH_AT, SLASH_AT + FLASH_LEN - 1, 67, fx='flash', name='kmFlash'),
             Overlay(FREEZE, SLASH_AT + SLASH_LEN - 1, 10, fx='veil', name='kmVeil')]
    sbolts = [Overlay(SLASH_AT + 2 + 3 * k, N - 4, 68 + k, fx='lightning', matrix=(1.2, 0, 0, 1.2, x, y))
              for k, (x, y) in enumerate(LAYOUT['lightning_anchors_slash'])]
    hit = [Overlay(*HIT, 74, char=HITBOX, name='cbsatm', matrix=(10.6, 0, 0, 10.9, -20, -425))]
    return Segment('神避', [(706, 752), (926, 966)],
                   renames={'cbs5atm': 'kmoff', 'cbsatm': 'kmoff', 'cbs0atm': 'kmoff', 'cbs1atm': 'kmoff'},
                   scripts=done(s), overlays=eagle + bolts + slash + sbolts + hit)


# --- J: aura on the blade (injected into Kenpachi's 砍1-3 frames) + 3 -> 1 loop -------------------------------------
# blade/trail centres measured on the original frames (sprite coordinates)
AURA_AT = {
    '砍1': [(184, 25, -2), (185, -11, 6), (186, -11, 6), (187, -26, -3), (188, -26, -3), (189, -8, -3), (190, -8, -3)],
    '砍2': [(201, -7, -30), (202, 48, -3), (203, 48, -3), (204, 31, 11), (205, 31, 11), (206, 7, 4), (207, 7, 4)],
    '砍3': [(224, 25, 9), (225, 25, 9), (226, 15, -50), (227, 15, -50), (228, -30, -24), (229, -30, -24),
            (230, -30, -24)],
}
AURA_SEQ = [(i, 2) for i in range(6)]
J3_WINDOW = f'DefineSprite_{FORM}/frame_233/PlaceObject2_13_34/CLIPACTIONRECORD onClipEvent(enterFrame).as'


def j_aura():
    return [Inject([(f, (1.1, 0, 0, 1.1, x, y)) for f, x, y in pts], 40, fx='aura') for pts in AURA_AT.values()]


# --- W+J 冲天斩: rising crescent while dashing diagonally up-forward, then fall --------------------------------------
def rising_dash():
    n = 22  # 257-278: wind-up 1-7, crescent 8-15, then he drops (落2)
    s = new_scripts(n)
    s[1] += '动作 = 1;\nql += 5;\njump = 1;\n'
    for i in range(7, 17):
        s[i] += f'if(_root.zhanting == false)\n{{\n   _parent._x += {fb.DIR} * 11;\n   _parent._y -= 9;\n}}\n'
    s[8] += '_root.shake(3,6);\n'
    s[n] += 'jump = 0;\njumped = 0;\ngotoAndStop("落2");\nplay();\n'
    return Segment('冲天斩', [(257, 278)], renames={'kj11atm': 'kj2atm', 'kj1atm': 'kj21atm'}, scripts=done(s))


# --- S+J ground 冲斩: short dash + slash ------------------------------------------------------------------------------
def dash_slash():
    n = 37  # 293-301 crouch/dash, 306-333 slash (313 = offset 17) + recovery; 302-305 = Kenpachi's vanish
    s = new_scripts(n)
    s[1] += fb.START
    for i in range(2, 15):
        s[i] += f'if(_root.zhanting == false)\n{{\n   _parent._x += {fb.DIR} * 8;\n}}\n'
    s[29] += '动作 = 0;\n'
    s[n] += fb.END
    return Segment('冲斩', [(293, 301), (306, 333)], renames={'kj2atm': 'kj1atm'}, scripts=done(s))


# --- S+J air 空斩: a black-red blade flying diagonally down (W+U art flipped), bursting on the floor ----------------
AIR_FIRE = 4         # 跳砍 crescent frame 130
AIR_MAT = (5, -65)   # flip (x, y) -> (x + 5, -y - 65): launch point (30,-70) -> (35, 5) in front of his blade


def air_slash():
    n = 14  # 跳砍 127-140, hovering
    s = new_scripts(n)
    s[1] += '动作 = 1;\nkhit = 1;\njump = 1;\nql += 5;\nasOn = true;\nasImp._visible = false;\n'
    tx, ty = AIR_MAT
    for k, (cx, cy, w, h) in enumerate(LAYOUT['wu_path']):
        o = AIR_FIRE + k
        if o > n:
            break
        cx, cy = cx + tx, -cy + ty
        hit = (f'if({FLOOR} <= {cy + h / 2:.1f})\n{{\n   asOn = false;\n   asSl._visible = false;\n'
               f'   kj13atm._y = -3000;\n   asImp._x = {cx:.1f};\n   asImp._y = {FLOOR};\n   asImp._visible = true;\n'
               f'   asImp.gotoAndPlay(1);\n   _root.shake(6,10);\n}}\n')
        body = hit + (f'else\n{{\n{box_at("kj13atm", cx, cy, w, h)}}}\n' if k >= 2 else '')
        s[o] += f'if(asOn)\n{{\n{body}}}\n'
    s[n] += 'jump = 0;\njumped = 0;\ngotoAndStop("落2");\nplay();\n'
    ov = [Overlay(AIR_FIRE, n, 65, fx='as_slash', name='asSl', matrix=(1, 0, 0, -1, tx, ty)),
          Overlay(1, n, 66, fx='as_impact', name='asImp', matrix=FAR),
          Overlay(AIR_FIRE, n, 75, char=HITBOX, name='kj13atm', matrix=FAR)]
    return Segment('空斩', [(127, 140)], renames={'tkatm': 'kmoff'}, scripts=done(s), overlays=ov)


AIR_SJ_EDIT = ('         if(bishaAir())\n         {\n            _parent.gotoAndPlay("空中必杀");\n         }\n      }\n'
               '      if(step == 1 || step == 4)\n      {\n         js -= 1;',
               '         if(bishaAir())\n         {\n            _parent.gotoAndPlay("空中必杀");\n         }\n'
               '         if(skill1())\n         {\n            _parent.gotoAndPlay("空斩");\n         }\n      }\n'
               '      if(step == 1 || step == 4)\n      {\n         js -= 1;')


# --- U 霸斩: slow Haki-charged heavy slash that breaks guard ---------------------------------------------------------
def heavy_slash():
    n = 50  # 必杀 wind-up 532-555 (1-24), swing 556-562 (25-31; box 558-562), recovery 574-592 (32-50)
    s = new_scripts(n)
    s[1] += fb.START
    s[25] += '_root.shake(10,14);\n'
    s[27] += '_root.shine(9109504);\n'
    s[44] += '动作 = 0;\n'
    s[n] += fb.END
    ov = [Overlay(8, 26, 60, fx='lightning', matrix=(0.55, 0, 0, 0.55, 2, -12)),       # Haki gathering on him
          Overlay(14, 26, 61, fx='aura', matrix=(1.3, 0, 0, 1.3, -14, 4)),
          Overlay(27, 40, 70, fx='u_impact', matrix=(1.3, 0, 0, 1.3, 75, -15))]
    return Segment('霸斩', [(532, 562), (574, 592)], renames={'bs1atm': 'zh1atm', 'bsatm': 'kmoff'},
                   scripts=done(s), overlays=ov)


# --- W+U 飞斩: rising slash firing a black-red blade diagonally up ---------------------------------------------------
WU_LAUNCH_SEQ = [(0, 1), (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2)]
WU_SLASH_SEQ = [(0, 1), (1, 1)] + [(i, 2) for i in range(2, 14)]
WU_FIRE = 14            # 招2 stance 414-422 (1-9), then 砍3 222-256: rising crescent 226 = offset 14
WU_MAT = (10, FEET + 1)  # launch point (30,-70) above his feet -> (40,-45) on the crescent


def flying_slash():
    n = 44
    s = new_scripts(n)
    s[1] += fb.START
    s[WU_FIRE] += '_root.shake(6,8);\n'
    tx, ty = WU_MAT
    path = LAYOUT['wu_path']
    for t, k in enumerate(ticks(WU_SLASH_SEQ)):
        o = WU_FIRE + t
        if k >= 2 and o <= n:
            cx, cy, w, h = path[k]
            s[o] += box_at('zh31atm', cx + tx, cy + ty, w, h)
    s[40] += '动作 = 0;\n'
    s[n] += fb.END
    end = WU_FIRE + len(ticks(WU_SLASH_SEQ)) - 1
    ov = [Overlay(WU_FIRE, WU_FIRE + len(ticks(WU_LAUNCH_SEQ)) - 1, 64, fx='wu_launch', matrix=(1, 0, 0, 1, tx, ty)),
          Overlay(WU_FIRE, min(end, n), 65, fx='wu_slash', matrix=(1, 0, 0, 1, tx, ty)),
          Overlay(WU_FIRE + 2, min(end, n), 75, char=HITBOX, name='zh31atm', matrix=FAR)]
    return Segment('飞斩', [(414, 422), (222, 256)], renames={'k3atm': 'zh3atm'}, scripts=done(s), overlays=ov)


# --- S+U 霸王色: Conqueror's Haki dome around him --------------------------------------------------------------------
HAKI_SEQ = [(0, 2), (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 3), (10, 3), (11, 3)]
HAKI_AT = 4  # stance 1-3, then the burst pose from the first burst frame
HAKI_GATHER = (1, 3)    # 站立: he stands still for a beat
HAKI_BURST = (863, 888)  # 超必杀1: Kenpachi facing front, coat blown out by his own pressure (bitmaps 441/443
#                          alternate = flutter); his golden sphere (sprite 407) and its box (cbs4atm) are dropped
SPHERE = 407


def haoshoku():
    n = (HAKI_GATHER[1] - HAKI_GATHER[0] + 1) + (HAKI_BURST[1] - HAKI_BURST[0] + 1)
    s = new_scripts(n)
    s[1] += fb.START
    s[HAKI_AT] += '_root.shake(12,18);\n_root.shine(4980736);\n'
    s[HAKI_AT + 8] += '_root.shake(8,10);\n'
    end = HAKI_AT + len(ticks(HAKI_SEQ)) - 1
    for i in range(HAKI_AT, min(end, n) + 1):
        s[i] += stage_fit('hkVeil')
    s[n - 3] += '动作 = 0;\n'
    s[n] += fb.END
    r = LAYOUT['haki_ring_radius'][8]
    ov = [Overlay(HAKI_AT, min(end, n), 10, fx='veil', name='hkVeil'),
          Overlay(HAKI_AT, min(end, n), 66, fx='haki_ring', matrix=(1, 0, 0, 1, 0, FEET)),
          Overlay(HAKI_AT + 2, HAKI_AT + 12, 67, fx='lightning', matrix=(0.8, 0, 0, 0.8, -95, -10)),
          Overlay(HAKI_AT + 4, HAKI_AT + 14, 68, fx='lightning', matrix=(0.8, 0, 0, 0.8, 90, -40)),
          Overlay(HAKI_AT + 6, HAKI_AT + 16, 69, fx='lightning', matrix=(0.7, 0, 0, 0.7, 0, -120)),
          Overlay(HAKI_AT + 3, HAKI_AT + 13, 75, char=HITBOX, name='zh21atm',  # dome: centre (0,-16), radius ~175
                  matrix=(2 * r / HB_W, 0, 0, (r + 40) / HB_H, -r, -16 - r))]
    return Segment('霸王色', [HAKI_GATHER, HAKI_BURST], renames={'cbs4atm': 'kmoff'}, scripts=done(s), overlays=ov,
                   drop={SPHERE})


SPEC = Spec(
    name='shanks', src=os.path.join(ROOT, 'game/fighter/jianba.swf'), form=FORM, controller=CONTROLLER, work=WORK,
    segments=[kamusari(), rising_dash(), dash_slash(), air_slash(), heavy_slash(), flying_slash(), haoshoku()],
    label_remap=[('gotoAndPlay("超必杀")', 'gotoAndPlay("@神避")'),     # S+I
                 ('gotoAndPlay("砍技2")', 'gotoAndPlay("@冲天斩")'),    # W+J (and its follow-up from J2)
                 ('gotoAndPlay("砍技21")', 'gotoAndPlay("@冲天斩")'),
                 ('gotoAndPlay("砍技1")', 'gotoAndPlay("@冲斩")'),      # S+J (ground)
                 ('gotoAndPlay("招1")', 'gotoAndPlay("@霸斩")'),        # U
                 ('gotoAndPlay("招2")', 'gotoAndPlay("@霸王色")'),      # S+U
                 ('gotoAndPlay("招3")', 'gotoAndPlay("@飞斩")')],       # W+U
    script_edits={**{f'DefineSprite_{FORM}/frame_{f}/DoAction.as': [('"剑八1"', '"香克斯1"')] for f in (535, 595)},
                  J3_WINDOW: [('   if(gameRunning())\n   {\n',
                               '   if(gameRunning())\n   {\n      if(nornalhit(true))\n      {\n'
                               '         _parent.gotoAndPlay("砍1");\n      }\n')],
                  f'DefineSprite_{CONTROLLER}/frame_1/DoAction.as': [AIR_SJ_EDIT]},
    gjl_table='gjl1',
    gjl={'cbs': (500, 12, 10, 20, 0, '击飞'),    # Kamusari
         'k3': (70, 6, 6, 9, 500, '被打'),       # J3 pushes away (loop does not lock)
         'kj2': (50, 1, 12, 2, 500, '被打'),     # W+J first hits: lift
         'kj21': (70, 6, 20, 3, 600, '被打'),    # W+J: launch
         'kj1': (70, 6, 3, 7, 500, '被打'),      # S+J ground dash slash
         'kj13': (60, 6, -8, 4, 400, '被打'),    # S+J air blade (knocks down)
         'zh1': (130, 16, 4, 24, 0, '击飞'),     # U: zl > 10 breaks guard
         'zh2': (60, 9, 6, 10, 0, '击飞'),       # S+U body burst
         'zh21': (110, 9, 10, 18, 0, '击飞'),    # S+U dome
         'zh3': (60, 6, 8, 4, 300, '被打'),      # W+U crescent at the blade
         'zh31': (110, 6, 12, 8, 0, '击飞')},    # W+U flying blade
    fx_once={'eagle', 'slash', 'flash', 'wu_launch', 'wu_slash', 'as_slash', 'as_impact', 'u_impact', 'haki_ring'},
    fx_hold={'eagle': EAGLE_SEQ, 'slash': SLASH_SEQ, 'flash': FLASH_SEQ, 'lightning': 2, 'aura': AURA_SEQ,
             'wu_launch': WU_LAUNCH_SEQ, 'wu_slash': WU_SLASH_SEQ, 'as_slash': 1, 'haki_ring': HAKI_SEQ,
             'as_impact': [(0, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 3)],
             'u_impact': [(0, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 3)]},
    fx_alias={'as_slash': 'wu_slash', 'as_impact': 'wu_impact', 'u_impact': 'wu_impact'},
    inject=j_aura(),
    tints={((256, 256, 256), (255, 255, 0)): ((256, 256, 256), (0, 0, 0)),     # 必杀 wave (I, U): was yellow
           ((0, 0, 0), (508, 487, 219)): ((0, 0, 0), (205, 30, 54)),            # 必杀 wave fading silhouette
           ((256, 256, 256), (255, 142, -77)): ((256, 256, 256), (0, 0, 0)),    # air U blast: was orange
           ((256, 256, 256), (255, 118, 0)): ((256, 256, 256), (0, 0, 0))},     # 上必杀 (W+I): was orange
    marker='SHK')


def build(out_swf, tmp):
    return fb.build(SPEC, out_swf, tmp, os.path.join(WORK, 'base/jianba'))


if __name__ == '__main__':
    print(build(sys.argv[1], os.path.join(ROOT, 'work/build')))
