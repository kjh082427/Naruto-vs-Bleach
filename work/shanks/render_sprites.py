#!/usr/bin/env python3
"""Shanks reskin of the Kenpachi bitmaps of game/fighter/jianba.swf (sprite 514).

Run (from anywhere):
    tools/venv/bin/python work/shanks/render_sprites.py               # all ids -> sprites/ + sheet/report/pads
    tools/venv/bin/python work/shanks/render_sprites.py --ids 6,146 --out /tmp/x   # test run

Inputs  (relative to this file's directory, work/shanks/):
  base/jianba/<id>.png     original bitmaps exported by FFDec
  label_map.json           labels -> bitmap ids, all_bitmaps
Outputs:
  sprites/<id>.png         one per id in all_bitmaps, RGBA, SCALE (2) x the padded
                           original size; KEEP_1X ids (339, 346) stay 1x
  sprites_pad.json         {id: [left, top, right, bottom]} canvas padding in ORIGINAL
                           pixels (content keeps its place); the build draws a sprite
                           at 1/k where k = png width / padded width
  sprites_sheet.png        review sheet: original | new, grouped by label
  sprites_report.json      per-id classification, head / sword / arm / cape notes

Deterministic: no randomness; ids processed in sorted order.  Needs numpy, Pillow, scipy.

Kenpachi's palette encodes roles with exact colours (hair = (7|8, 0, 0), katana
outline = (7|8, 7|8, 7|8) in some palette families, slash trails = (238, 247, 247)
...).  Every pixel of a character bitmap gets a ROLE (outline, cloth, cloth
highlight, cape, lining, skin, hair, gold, trail, other); the geometric edits work
on that 1x role map:
  * white haori -> long black cape, its dark inside -> wine lining; a floor-length
    cape behind the legs (wavy hem);
  * v3: the cape is the outer layer over both shoulders: Kenpachi's black kimono
    above the waist stays white shirt only in the open front (a band around the
    torso axis + the V framing the bare chest) and on the sword forearm (FOREARM px
    up the sleeve from the hand); shoulders, upper arms and the free sleeve become
    cape (cape_over_arms);
  * black hakama -> neat crimson 3/4 pants, bare shins, sandals; red sash on the waist;
  * spiky black hair -> rounded red cap, plus v3 long hair falling to the jaw / nape
    behind the face and over the ear (long_hair); eyepatch removed, clean face;
  * the left (free) arm is cut off at the sleeve (ARMS table), a second hand on
    the grip is removed;
  * the katana is erased and Gryphon (slim curved sabre, gold cup guard with a
    knuckle-bow, dark grip) is drawn in the sword hand (SWORDS table / auto);
  * slash trails and effect bitmaps are gradient-mapped onto the Haki palette
    (EFFECT_STYLE table, per label).
v3 rendering at 2x (render2x): the 1x role map becomes a map of flat tone labels
(paint_labels: cape / shirt / pants / skin tones, outline, hair ...), cleaned of
specks (denoise_labels), then magnified with magnify_labels (Scale2x twice = 4x,
feature preserving; per-label Gaussian smoothing at 4x; pooled to 2x by argmax):
crisp labels, smooth silhouettes and tone bands at any angle, 1 px lines and single
pixels kept.  Colours come from the 2x palette; hair strands / sheen, cape rim
light and floor-cape folds, pants cel shading are drawn procedurally at 2x;
Gryphon is rasterised directly at 2x; trails and effects use a bilinear ramp field
(RAMP_LEVELS steps) inside a label-magnified silhouette.
S+U "Haki release" bitmaps 441 / 443 are drawn from scratch (draw_haki_pose).
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from pathlib import Path

import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "base" / "jianba"
OUT = ROOT / "sprites"
SHEET = ROOT / "sprites_sheet.png"
REPORT = ROOT / "sprites_report.json"
PADS = ROOT / "sprites_pad.json"
FONT = ROOT.parent.parent / "tools" / "fonts" / "NanumGothic-Bold.ttf"

LABEL_EN = {
    "站立": "stand", "走": "walk", "瞬步": "dash", "跳": "jump", "落": "fall",
    "跳2": "jump2", "落2": "fall2", "落地": "land", "跳砍": "air J", "跳招": "air U",
    "跳招20": "air U2", "跳招3": "air U3", "砍1": "J1", "砍2": "J2", "砍3": "J3",
    "砍技1": "S+J", "砍技2": "W+J", "砍技21": "W+J 2", "砍技22": "W+J 3",
    "招1": "U1", "招2": "U2", "招21": "U2-1", "招3": "U3", "必杀": "ult I",
    "上必杀": "ult W+I", "超必杀": "ult S+I", "超必杀1": "ult S+I (long)", "招换": "assist",
    "防御": "guard", "防御2": "guard2", "防住": "guard hit", "被打": "hurt",
    "击飞": "knock-up", "击落地": "knock-down", "起身": "get up", "开场": "intro",
    "胜利": "win", "失败": "lose",
}

# ==========================================================================
# EFFECTS: palette per label (edit here when the skill spec arrives)
# ==========================================================================
# ramps: (t, rgb), t in 0..1
RAMPS = {
    # Conqueror's Haki: black / dark-violet cores -> crimson -> near-white hot spots
    "haki": [(0.00, (12, 2, 12)), (0.14, (40, 6, 36)), (0.32, (86, 8, 34)),
             (0.48, (122, 10, 30)), (0.70, (215, 38, 61)), (0.88, (244, 104, 104)),
             (1.00, (255, 238, 234))],
}
# style per label (first matching label in this order wins for shared bitmaps)
#   ramp       key of RAMPS
#   eq         True: t = luminance rank over all effect pixels of the label
#              (histogram-equalised, shared by every frame of the label -> no flicker)
#   gamma      used when eq is False: t = luminance ** gamma
#   keep_dust  leave brown dust / debris untouched
#   hot_pow    eq only: t = max(rank, luminance ** hot_pow) keeps near-white cores continuous
EFFECT_STYLE = {
    "跳招20": dict(ramp="haki", eq=True),            # air U2 flame burst
    "跳招3": dict(ramp="haki", eq=True, keep_dust=True),  # air U3 ground blast
    "砍技1": dict(ramp="haki", eq=True),             # S+J flame wave
    "招1": dict(ramp="haki", eq=True, hot_pow=3),    # U1 fireball (soft, big white core)
    "招21": dict(ramp="haki", eq=True),              # U2 pillar
    "招3": dict(ramp="haki", eq=True),               # U3 beam
    "必杀": dict(ramp="haki", eq=True),              # ult I crescent
    "上必杀": dict(ramp="haki", eq=True),            # ult W+I orb + ring
    "超必杀1": dict(ramp="haki", eq=True),           # ult S+I flame column
    "瞬步": dict(ramp="haki", eq=False, gamma=1.0),  # dash afterimage streak
}
DEFAULT_STYLE = dict(ramp="haki", eq=False, gamma=1.0)
TRAIL_STYLE = dict(ramp="haki", body=0.70, hot=0.86, rim=0.16)   # rim: t of the dark trail edge (None = off)

# Bitmaps that contain no character at all (checked on contact sheets).
EFFECT_ONLY = ({35} | set(range(81, 100, 2)) | {104, 106, 108, 111, 113, 115, 117}
               | set(range(121, 136, 2)) | {187, 190, 193, 197, 199} | {234, 239, 241, 243}
               | set(range(252, 281, 2)) | set(range(291, 310, 2))
               | {324, 329, 333, 335, 339, 346} | set(range(357, 406, 2))
               | set(range(414, 433, 2)) | set(range(449, 466, 2)))

# bitmaps whose flying haori uses the trail colours: trail pieces entirely left of x are haori
HAORI_NOT_TRAIL = {435: 32, 437: 32, 439: 31}
# slash-trail colours inside character bitmaps
TRAIL_COLORS = {(238, 247, 247), (240, 248, 248), (255, 255, 26), (255, 255, 164),
                (255, 255, 165), (221, 221, 0), (115, 239, 239), (16, 189, 239),
                (98, 199, 255)}
# palette family B uses pure white for its trails (its haori white is 248)
TRAIL_EXTRA = {58: [(255, 255, 255)], 61: [(255, 255, 255)], 77: [(255, 255, 255)],
               79: [(255, 255, 255)], 102: [(255, 255, 255)], 213: [(255, 255, 255)],
               217: [(255, 255, 255)]}

# ==========================================================================
# character colours
# ==========================================================================
OUTLINE = (10, 6, 8)
SHIRT = (238, 236, 228)
SHIRT_SH = (198, 196, 194)
SHIRT_DK = (150, 148, 158)
# 3/4 crimson pants (revision 2: no khaki, no noisy pattern)
PANTS_OUT = (60, 10, 16)
PANTS_SH = (110, 20, 30)
PANTS = (150, 30, 40)
PANTS_HL = (185, 55, 60)
PANTS_PAT = (124, 24, 34)          # subtle darker diamond motif
SASH = (204, 54, 54)
SASH_DK = (96, 14, 22)
CAPE = [(22, 22, 30), (30, 30, 40), (42, 42, 56), (58, 58, 76)]   # dark -> light
LINING = (90, 22, 42)
LINING_DK = (62, 14, 30)
HAIR_OUT = (62, 8, 14)
HAIR_DK = (142, 22, 30)
HAIR_MID = (200, 42, 42)
HAIR_HI = (238, 94, 76)
SCAR = (120, 30, 34)
EYE = (74, 49, 8)
STUBBLE = (104, 70, 50)
SKIN_HI = (247, 206, 189)
SKIN_MID = (206, 165, 140)
SKIN_SH = (148, 107, 74)
SANDAL = (128, 80, 42)
SANDAL_DK = (74, 42, 22)
FACE_SCARS = 0                     # 0: clean face (the cut-ins carry the scars); 1: one 1 px line
SWORD_SCALE = 1.4                  # Gryphon blade length vs the old katana (long sabre)
KNEE = 0.55                        # knee height: fraction waist -> floor where the 3/4 pants end
# Gryphon
G_OUT = (22, 22, 30)
G_BODY = (150, 160, 176)
G_EDGE = (236, 242, 250)
G_GOLD = (232, 188, 72)
G_GOLD_SH = (172, 126, 40)
G_GOLD_OUT = (92, 58, 16)
G_GRIP = (46, 32, 30)
G_GRIP_HI = (86, 60, 50)

# ==========================================================================
# v3: 2x art
# ==========================================================================
SCALE = 2                          # sprites are drawn at SCALE x the padded original size
RAMP_LEVELS = 32                   # 2x effects / trails: ramp position steps
KEEP_1X = {339, 346}               # their shapes are not plain bitmap rectangles: the build cannot scale them
CHEST_W = 4.0                      # half width (1x px) of the open shirt around the torso axis
FOREARM = 6.5                      # sword forearm left out of the cape: geodesic length (1x px) from the hand
FORE_MAX = 20                      # ... but at most about this many 1x px of white sleeve
HAIR_TIP = 5.6                     # long hair falls this far below the face centre (1x px): jaw / nape line
BACK_VIEW = {227, 229, 285, 287}   # back views: the hair falls over the whole back of the head
# 2x palette, dark -> light
CAPE_T = [(14, 13, 22), (27, 26, 40), (42, 41, 60), (64, 63, 90), (96, 96, 130)]
LIN_T = [(60, 12, 30), (98, 24, 46)]
SHIRT_T = [(146, 144, 158), (198, 196, 200), (242, 240, 232)]
PANTS_T = [(84, 14, 24), (124, 24, 34), (158, 34, 44), (192, 62, 64)]
SKIN_T = [(150, 104, 76), (208, 162, 134), (242, 200, 176)]
FEAT_C = (74, 40, 22)
HAIR_T = [(74, 8, 18), (136, 18, 30), (186, 34, 40), (222, 64, 58), (244, 118, 96)]
SASH_T = [(110, 16, 26), (196, 48, 52)]
SAND_T = [(70, 40, 22), (128, 80, 42)]

# roles
(R_NONE, R_OUT, R_CLOTH, R_CLOTH_HL, R_FOLD, R_CAPE, R_LINING, R_SKIN, R_HAIR, R_GOLD,
 R_TRAIL, R_OTHER) = range(12)

# ==========================================================================
# per-pose annotations (ORIGINAL bitmap pixel coordinates)
# ==========================================================================
# SWORDS[id] = list of (guard_xy, tip_xy[, opts]) or [] (no sword).  guard = the
# old tsuba (where Gryphon's guard goes), tip = the old blade tip.  opts:
#   len   blade length (default: |tip - guard|)     fixed  no auto snapping
#   hand  (x, y) point of the sword hand (default: skin blob next to the guard)
# Missing ids use auto detection (gold tsuba + best ray of blade pixels).
SWORDS: dict = {
    37: [((42, 55.5), (70, 53.5))],
    39: [((37, 39.5), (55, 47.5))],                 # reverse grip, blade across the body
    42: [((33, 41.5), (51, 42.5))], 44: [((33, 41.5), (51, 42.5))], 46: [((33, 41.5), (51, 42.5))],
    50: [((27, 41), (14.5, 57.5))], 52: [((27, 41), (14.5, 57.5))],
    56: [((62, 26), (36, 19.5), dict(behind=True))],
    58: [((55, 52), (56.5, 80))],
    61: [((43, 30.5), (12, 25.5))],
    65: [((40.5, 34), (22.5, 48))], 67: [((40.5, 34), (22.5, 48))],
    74: [((33, 11), (9, 8.5))],
    79: [((28, 40.5), (44, 9))],                    # blade hidden in the rising trail: guess
    139: [((88, 64), (55, 58.5), dict(behind=True))],   # wind-up, blade over the shoulder
    141: [((99, 74.5), (124, 76))],                 # blade inside the crescent: guess
    144: [((62, 72), (36, 79))],
    150: [((60, 74), (47, 90))], 152: [((60, 74), (47, 90))],
    154: [((52, 47), (36, 53.5))],
    156: [((76.5, 31), (72, 19))],
    158: [((82, 71), (100, 74))], 160: [((82, 71), (103, 77))],
    162: [((79, 70), (106, 82.5))],
    164: [((64, 70), (89, 77))], 166: [((64, 70), (89, 77))],
    168: [((89, 98.5), (110, 106))],                # blade hidden: guess (low, forward)
    171: [((90, 89), (106, 104))],                  # blade inside the crescent: guess
    179: [((51, 91), (38, 105))], 181: [((51, 91), (38, 105))],
    205: [((70, 83.5), (59.5, 103))],
    207: [],                                        # motion-blurred dash, no blade visible
    211: [((62, 77), (43, 95))],
    227: [], 229: [],                               # back view, sword not visible
    231: [((26, 17), (52, 15.5))],
    # U3: arm raised, blade up-right (inside the yellow trail in 289/312/314: guess)
    289: [((49, 13), (71, 6))], 312: [((49, 13), (71, 6))], 314: [((49, 13), (71, 6))],
    316: [((49, 13), (71, 6))], 318: [((49, 13), (71, 6))],
    349: [((17, 21), (2, 37))],
    353: [((11, 21), (28, 30))],                    # reverse grip
    355: [], 408: [], 410: [], 412: [],             # spin: blade lost in the motion blur
    439: [((42, 36), (70, 47))],
    441: [], 443: [],                               # blurred sweep
    445: [((30, 63), (52, 38))], 447: [((47, 41), (70, 23))],
    469: [((47, 42), (60, 26))], 471: [((41, 53), (57, 37))],
    474: [((10.5, 62.5), (35, 68.5)), ((59.5, 36.5), (38, 27.5)),
          ((114, 35.5), (144, 37), dict(behind=True))],
    485: [((15, 30), (34, 40))], 487: [((7, 27), (24, 40))],
    492: [], 494: [], 496: [],                      # lying: blade hidden under the body
    502: [((33, 52), (20, 47))], 504: [((33, 52), (20, 47))],
    507: [],
}
# multi-figure bitmaps: one auto sword per head (search window +-W px around the head)
AUTO_PER_HEAD = {6: 24, 474: 24}
# ARMS[id] = list of removals: (x, y) = skin blob of the left hand / forearm,
#   ("poly", [(x, y), ...], "cut"|"fill"|"cape") = polygon: remove (cut), paint over
#   with the surrounding pixels (fill) or turn cloth into cape (cape: the cape
#   covers the empty left sleeve).
def _cape6(dx):
    return ("poly", [(35 + dx, 33), (41 + dx, 33), (42 + dx, 52), (35 + dx, 52)], "cape")


def _cape_at(fx, fy):
    """Stand-like poses: far (left) sleeve under the cape, relative to the face centre."""
    return ("poly", [(fx + 5, fy + 9.6), (fx + 11, fy + 9.6), (fx + 12, fy + 28.6), (fx + 5, fy + 28.6)], "cape")


ARMS: dict = {
    6: [_cape6(0), _cape6(38), _cape6(76), _cape6(117)],
    250: [_cape_at(19.0, 13.4)], 507: [_cape_at(16.0, 13.4)],
    31: [_cape6(18)], 33: [_cape6(18)],
    37: [(55, 63)], 39: [(68, 44)], 42: [(69, 42)], 44: [(69, 42)], 46: [(69, 42)],
    48: [(51, 64)], 50: [(65, 52)], 52: [(65, 52)],
    56: [(54, 42)], 58: [(68, 41)], 61: [("poly", [(60, 37), (71, 37), (71, 45), (60, 45)], "cut")],
    63: [(58, 32)], 65: [(67, 37)], 67: [(67, 37)],
    74: [(38, 25)],
    119: [(36, 62)], 137: [(36, 62)],
    139: [(72, 75)], 141: [(74, 73)], 144: [(95, 78)], 146: [(89, 75)], 148: [(89, 75)],
    150: [(89, 78)], 152: [(89, 78)],
    154: [(84, 64)], 156: [(88, 63)], 158: [(88, 65)], 160: [(88, 65)], 162: [(87, 65)],
    164: [(82, 64)], 166: [(82, 64)],
    168: [(68, 94)], 173: [(87, 97)], 175: [(89, 93)], 177: [(86, 93)],
    179: [(89, 100)], 181: [(89, 100)], 183: [(33, 41)],
    # raised free arm: hand and the sleeve up to the shoulder
    185: [(26, 9), ("poly", [(18, 4), (32, 4), (33, 13), (31, 19), (18, 19)], "cut")],
    195: [(25, 9), ("poly", [(18, 4), (32, 4), (33, 13), (31, 19), (18, 19)], "cut")],
    201: [(91, 90)], 203: [(87, 88)], 205: [(89, 89)], 209: [(79, 86)],
    # back views: his left arm is on screen-left -> hand off, sleeve under the cape
    227: [(7, 29), ("poly", [(2, 21), (10, 21), (10, 35), (2, 35)], "cape")],
    229: [(5, 19), ("poly", [(0, 15), (11, 15), (11, 31), (0, 31)], "cape")],
    236: [(28, 21)],
    285: [(37, 51)], 287: [(32, 45)],               # back views
    289: [(34, 53)], 312: [(34, 53)], 314: [(34, 53)], 316: [(34, 53)], 318: [(34, 53)],
    341: [(44, 88)], 344: [(44, 88)],
    349: [(45, 26)], 351: [(41, 25)], 353: [(41, 28)],
    471: [(32, 53)],
    474: [("poly", [(29, 40), (37, 40), (38, 60), (29, 60)], "cape"),
          ("poly", [(88, 40), (96, 40), (97, 60), (88, 60)], "cape"),
          ("poly", [(131, 40), (139, 40), (140, 60), (131, 60)], "cape")],
    477: [(51, 43)], 479: [(52, 44)], 481: [(52, 44)],
    483: [(37, 23)], 485: [(34, 22)], 487: [(33, 31)],
    498: [(62, 48)], 502: [(62, 58)], 504: [(62, 58)],
}
# palettes whose hands are drawn in saturated orange (would read as gold)
ORANGE_SKIN = {56, 58, 61}
# WAIST[id] = list of ((x0, y0), (x1, y1)) lines (one per figure); shirt on the
# side of the face.  Missing ids: horizontal line half-way face -> feet.
def _stand_waist(fx, fy):
    """Stand-like poses: waist 26 px under the face centre, dipping under the
    hanging right sleeve (so the sleeve stays shirt)."""
    return [(fx - 26, fy + 33.6), (fx - 15, fy + 33.6), (fx - 7, fy + 28.6),
            (fx - 5, fy + 26.1), (fx + 16, fy + 26.1)]


WAIST: dict = {
    6: [_stand_waist(30.0 + dx, 23.4) for dx in (0, 38, 76, 117)],
    31: [_stand_waist(48.0, 24.5)], 33: [_stand_waist(47.9, 23.2)],
    250: [_stand_waist(19.0, 13.4)],
    474: [_stand_waist(24.0, 31.4), [(53, 56.7), (113, 56.7)], [(96, 56.7), (156, 56.7)]],
    507: [_stand_waist(16.0, 13.4)], 509: [_stand_waist(15.0, 13.1)], 511: [_stand_waist(15.0, 13.4)],
    # tumbling / lying bodies
    489: [[(24, 0), (34, 40)]],
    492: [[(42.5, 37.7), (53.5, 54.4)]],
    494: [[(51, 46), (51, 70)]], 496: [[(51, 46), (51, 70)]],
}
# FEET[id] = list of (x, y, r) circles: light pixels inside become bare feet + sandals.
FEET: dict = {}
# no 3/4-pants / floor-cape pass (airborne, lying, flying walk streak, spins)
NO_LEGS: set = (set(range(14, 29, 2)) | {39, 42, 44, 46, 56, 58, 61, 63, 65, 67, 69, 71, 74, 77, 79, 102,
                                          183, 185, 195, 207, 349, 351, 353, 355, 408, 410, 412,
                                          483, 485, 487, 489, 492, 494, 496})
# hair not colour-coded in these bitmaps: (cx, cy, r, [colours])
HAIR_ZONE: dict = {i: (64, 34, 13.0, [(0, 0, 0)], 42) for i in range(14, 29, 2)}
HAIR_ZONE.update({56: (56, 20, 14.0, [(8, 8, 8)], 28), 58: (58, 23, 13.0, [(8, 8, 8)], 31),
                  61: (58, 23, 13.0, [(8, 8, 8)], 31)})

# ==========================================================================
# small numpy image helpers
# ==========================================================================
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def shift(m, dy, dx, fill=False):
    h, w = m.shape[:2]
    o = np.full_like(m, fill)
    ys, yd = slice(max(dy, 0), h + min(dy, 0)), slice(max(-dy, 0), h + min(-dy, 0))
    xs, xd = slice(max(dx, 0), w + min(dx, 0)), slice(max(-dx, 0), w + min(-dx, 0))
    o[ys, xs] = m[yd, xd]
    return o


def dilate(m, it=1, nb=N8):
    for _ in range(it):
        o = m.copy()
        for dy, dx in nb:
            o |= shift(m, dy, dx)
        m = o
    return m


def erode(m, it=1, nb=N8):
    return ~dilate(~m, it, nb)


def nbcount(m, nb=N8):
    c = np.zeros(m.shape, int)
    for dy, dx in nb:
        c += shift(m, dy, dx)
    return c


def label(m, nb=N8):
    h, w = m.shape
    lab = np.zeros((h, w), int)
    n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1
        q = deque([(y, x)])
        lab[y, x] = n
        while q:
            cy, cx = q.popleft()
            for dy, dx in nb:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    q.append((ny, nx))
    return lab, n


def hsv_arrays(rgb):
    f = rgb.astype(float) / 255.0
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mx, mn = f.max(-1), f.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0)
    h = np.zeros_like(mx)
    nz = d > 1e-9
    rm = nz & (mx == r)
    gm = nz & (mx == g) & ~rm
    bm = nz & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    return h * 60.0, s, mx


def luma(rgb):
    f = rgb.astype(float)
    return (0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]) / 255.0


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        k = ((t - t0) / (t1 - t0))[m][:, None]
        out[m] = np.array(c0) * (1 - k) + np.array(c1) * k
    return np.round(out).astype(np.uint8)


def color_eq(rgb, col, tol=0):
    return np.all(np.abs(rgb.astype(int) - np.array(col)) <= tol, axis=-1)


def in_colors(rgb, cols):
    m = np.zeros(rgb.shape[:2], bool)
    for c in cols:
        m |= color_eq(rgb, c)
    return m


def reach_border(free):
    """Pixels of `free` 4-connected to the canvas border through `free`."""
    h, w = free.shape
    seen = np.zeros_like(free)
    q = deque()
    for y in range(h):
        for x in (0, w - 1):
            if free[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if free[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        cy, cx = q.popleft()
        for dy, dx in N4:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and free[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return seen


def poly_mask(shape, pts):
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=1, outline=1)
    return np.array(im, bool)


# ==========================================================================
# pixel classification
# ==========================================================================
def classify(a, bid, xoff=0):
    rgb = a[..., :3].astype(int)
    op = a[..., 3] > 0
    h, s, v = hsv_arrays(rgb)
    L = luma(rgb)
    mx, mn = rgb.max(-1), rgb.min(-1)
    trail = op & in_colors(rgb, list(TRAIL_COLORS))
    if bid in TRAIL_EXTRA:
        ex = op & in_colors(rgb, TRAIL_EXTRA[bid])
        lab_, n_ = label(ex)
        for k in range(1, n_ + 1):
            ck = lab_ == k
            if ck.sum() >= 40:
                trail |= ck
    hair_code = op & (rgb[..., 0] >= 5) & (rgb[..., 0] <= 9) & (rgb[..., 1] == 0) & (rgb[..., 2] == 0)
    if bid in HAIR_ZONE:
        cx, cy, r, cols, ymax = HAIR_ZONE[bid]
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        hair_code = op & in_colors(rgb, cols) & ((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r) & (yy <= ymax)
    neutral = op & (mx - mn <= 40) & ~trail
    gold = op & ~neutral & ~trail & (((s >= 0.95) & (v >= 0.45)) | ((h >= 42) & (h <= 66) & (s >= 0.55) & (v >= 0.5)))
    skin = op & ~neutral & ~trail & ~gold & ((h <= 46) | (h >= 340)) & (s >= 0.12) & (s < 0.96)
    if bid in ORANGE_SKIN:
        orange = gold & (h <= 45)
        skin |= orange
        gold &= ~orange
    pinkgrey = neutral & (rgb[..., 0] - rgb[..., 2] >= 8) & (np.abs(rgb[..., 1] - rgb[..., 2]) <= 3) & (L >= 0.3)
    pg = pinkgrey & dilate(skin, 1)
    for _ in range(3):
        pg |= pinkgrey & dilate(pg, 1)
    skin |= pg
    neutral &= ~pg
    # grow the trail into its own grey bands / dark rim (never into skin)
    for _ in range(3):
        grow = op & ~trail & ~skin & ~gold & (nbcount(trail) >= 3) & ~dilate(skin, 1)
        if not grow.any():
            break
        trail |= grow
    if bid in HAORI_NOT_TRAIL:
        # the flying haori shares the trail colours here: its pieces left of x go back to cloth
        lab_, n_ = label(trail)
        for k_ in range(1, n_ + 1):
            ck = lab_ == k_
            if np.nonzero(ck)[1].max() - xoff <= HAORI_NOT_TRAIL[bid]:
                trail &= ~ck
                neutral |= ck & (mx - mn <= 40)
    neutral &= ~trail
    hair = hair_code & ~trail
    light = neutral & (L >= 0.33) & ~hair
    dgrey = neutral & (L >= 0.12) & (L < 0.33) & ~hair
    black = neutral & (L < 0.12) & ~hair
    other = op & ~(trail | hair | gold | skin | light | dgrey | black)
    return dict(op=op, rgb=rgb, L=L, h=h, s=s, v=v, trail=trail, hair=hair, gold=gold,
                skin=skin, light=light, dgrey=dgrey, black=black, other=other)


def sword_code(cls):
    """Katana outline colour, if the palette has a dedicated one ((7,7,7) / (8,8,8)
    used only on thin structures)."""
    rgb, black = cls["rgb"], cls["black"]
    G = black | cls["dgrey"]
    m = np.zeros(black.shape, bool)
    for c in ((7, 7, 7), (8, 8, 8), (4, 4, 4), (3, 3, 3)):
        cm = black & color_eq(rgb, c)
        n = int(cm.sum())
        if 8 <= n and (cm & (nbcount(G, N4) == 4)).sum() / n < 0.3 and n < 0.5 * black.sum():
            m |= cm
    return m


def cloth_roles(cls):
    """Role map for the clothing / outline pixels.
    Black pixels are cloth fill unless they touch the background, skin, hair,
    gold or a trail (-> outline) or sit between >= 2 haori pixels (haori line).
    Palette families with a dedicated cloth black ((5,5,5) / (8,8,8)) keep
    (0,0,0) as pure outline (folds inside the cloth -> fold shade)."""
    rgb, op = cls["rgb"], cls["op"]
    black, dgrey, light = cls["black"], cls["dgrey"], cls["light"]
    role = np.zeros(op.shape, np.int8)
    G = black | dgrey
    zero = black & color_eq(rgb, (0, 0, 0))
    sep = []
    for c in ((5, 5, 5), (8, 8, 8)):
        m = black & color_eq(rgb, c)
        if m.sum() >= 40 and (m & (nbcount(G, N4) == 4)).sum() / m.sum() >= 0.3:
            sep.append(m)
    hard = ~op | cls["skin"] | cls["hair"] | cls["gold"] | cls["trail"] | cls["other"]
    touch_hard = nbcount(hard, N4) > 0
    capeish = nbcount(light, N4) >= 2
    if sep:
        cloth = np.zeros_like(black)
        for m in sep:
            cloth |= m
        role[black] = R_OUT
        role[cloth & ~touch_hard & ~capeish] = R_CLOTH
        fold = zero & (nbcount(G, N8) == 8) & (nbcount(cloth, N8) >= 4)
        role[fold] = R_FOLD
    else:
        role[black] = R_OUT
        role[black & ~touch_hard & ~capeish & ~sword_code(cls)] = R_CLOTH
    role[dgrey] = R_CLOTH_HL
    role[dgrey & (nbcount(~op, N4) > 0)] = R_OUT
    role[light] = R_CAPE
    return role


# ==========================================================================
# heads
# ==========================================================================
def find_heads(cls):
    hair = cls["hair"]
    skin = cls["skin"]
    lab, n = label(hair)
    comps = []
    for k in range(1, n + 1):
        ck = lab == k
        if ck.sum() >= 4:
            y, x = np.nonzero(ck)
            comps.append([ck, x.mean() + 0.5, y.mean() + 0.5, int(ck.sum())])
    # merge components that belong to the same head (centroids < 14 px apart)
    groups = []
    for c in sorted(comps, key=lambda c: -c[3]):
        for g in groups:
            if math.hypot(c[1] - g[1], c[2] - g[2]) < 14:
                g[0] = g[0] | c[0]
                y, x = np.nonzero(g[0])
                g[1], g[2], g[3] = x.mean() + 0.5, y.mean() + 0.5, int(g[0].sum())
                break
        else:
            groups.append(list(c))
    heads = []
    H, W = hair.shape
    yy, xx = np.mgrid[0:H, 0:W]
    for hm, hx, hy, cnt in groups:
        if cnt < 30:
            continue
        near = skin & dilate(hm, 2)
        if near.sum() < 3:
            continue
        y, x = np.nonzero(near)
        f0 = np.array([x.mean() + 0.5, y.mean() + 0.5])
        slab, sn = label(skin)
        touch = set(slab[near].tolist()) - {0}
        face = np.isin(slab, list(touch)) & (np.hypot(xx + 0.5 - f0[0], yy + 0.5 - f0[1]) <= 6.5)
        y, x = np.nonzero(face)
        fc = np.array([x.mean() + 0.5, y.mean() + 0.5])
        heads.append(dict(hair=hm, face=face, fc=fc, hc=np.array([hx, hy])))
    heads.sort(key=lambda d: (round(d["fc"][0]), round(d["fc"][1])))
    return heads


def hair_mass(cls, head, R=7.4):
    """Shanks hair = Kenpachi's hair trimmed to a disk around the skull
    (spikes and bells removed), small gaps closed."""
    hm = head["hair"]
    fc, hc = head["fc"], head["hc"]
    H, W = hm.shape
    yy, xx = np.mgrid[0:H, 0:W]
    d = hc - fc
    dn = d / (np.linalg.norm(d) + 1e-9)
    c = fc + dn * 1.6
    dist = np.hypot(xx + 0.5 - c[0], yy + 0.5 - c[1])
    disk = dist <= R
    keep = hm & disk
    # close 1 px gaps between the trimmed spike roots
    gap = disk & ~cls["op"] & (nbcount(keep, N4) >= 3)
    keep |= gap
    gap = disk & ~keep & ~cls["skin"] & (nbcount(keep, N4) >= 3) & ~cls["op"]
    keep |= gap
    # 1 px stubs
    stub = keep & (nbcount(keep, N8) <= 1)
    keep &= ~stub
    return keep, c, dn


# ==========================================================================
# Gryphon
# ==========================================================================
SW_NONE, SW_BLADE, SW_GRIP, SW_POMMEL, SW_GUARD, SW_BOW = range(6)
GR_GRIP = 6.0


def hand_blobs(cls, heads):
    H, W = cls["op"].shape
    headm = np.zeros((H, W), bool)
    for hd in heads:
        headm |= dilate(hd["face"], 1)
    sk = cls["skin"] & ~headm
    lab, n = label(sk)
    out = []
    for k in range(1, n + 1):
        ck = lab == k
        if ck.sum() < 3:
            continue
        y, x = np.nonzero(ck)
        out.append((x.mean() + 0.5, y.mean() + 0.5, ck))
    return out


def blade_pixels(cls):
    """Thin blade-like structures (light / black / sword-outline) sticking out of the body."""
    op = cls["op"] & ~cls["trail"]
    body = dilate(erode(op, 2), 2)
    m = op & ~body & (cls["light"] | cls["black"] | cls["dgrey"] | cls["gold"])
    return m


def ray_score(G, ang, hitm, near_ok, h, w, tmax=70):
    dx, dy = math.cos(ang), math.sin(ang)
    hits, miss, last, seen = 0, 0, None, set()
    for i in range(6, int(tmax * 2)):
        t = i * 0.5
        px, py = int(math.floor(G[0] + dx * t)), int(math.floor(G[1] + dy * t))
        if not (0 <= px < w and 0 <= py < h):
            break
        if (px, py) in seen:
            continue
        seen.add((px, py))
        if hitm[py, px]:
            hits += 1
            last = t
            miss = 0
        elif not near_ok[py, px]:
            miss += 1
            if miss > 12 and t > 8:
                break
    return hits, last


def auto_sword(cls, heads):
    """Guard = a gold cluster (tsuba); blade = best ray of blade pixels from it
    (thin light / dark structures outside the body, plus the dedicated katana
    outline colour anywhere)."""
    gold = cls["gold"].copy()
    for hd in heads:
        gold &= ~dilate(hd["hair"], 2)
    lab, n = label(gold)
    thin = blade_pixels(cls)
    code = sword_code(cls)
    hitm = thin | code | (dilate(code, 1) & cls["light"])
    near_ok = dilate(hitm, 1)
    h, w = thin.shape
    best = None
    for k in range(1, n + 1):
        ck = lab == k
        if ck.sum() < 2:
            continue
        y, x = np.nonzero(ck)
        G = np.array([x.mean() + 0.5, y.mean() + 0.5])
        for deg in range(0, 360, 2):
            hits, last = ray_score(G, math.radians(deg), hitm, near_ok, h, w)
            if last is not None and (best is None or hits > best[0]):
                best = (hits, deg, last, G)
    if best is None or best[0] < 6:
        return None
    hits, deg, last, G = best
    ang = math.radians(deg)
    u = np.array([math.cos(ang), math.sin(ang)])
    T = G + u * last
    # the guard is the gold cluster on this line closest to the blade
    # (Kenpachi's hilt also has a gold end ornament)
    G0, cands = G, []
    for k in range(1, n + 1):
        y, x = np.nonzero(lab == k)
        C = np.array([x.mean() + 0.5, y.mean() + 0.5])
        rel = C - G0
        along, perp = rel @ u, abs(rel @ np.array([-u[1], u[0]]))
        if 0 < along <= min(14.0, last - 8.0) and perp <= 2.0:
            cands.append((along, C))
    if cands:
        G = max(cands, key=lambda c: c[0])[1]
    return G, T, hits


def sword_spec(G, T, k=1.0, opts=None):
    opts = opts or {}
    G = np.array(G, float)
    T = np.array(T, float)
    d = T - G
    L = float(np.linalg.norm(d))
    d /= L + 1e-9
    n1 = np.array([-d[1], d[0]])
    if abs(n1[1]) >= 0.3:
        nv = n1 if n1[1] > 0 else -n1          # cutting edge faces down
    else:
        nv = n1 if n1[0] > 0 else -n1
    nv = nv * opts.get("edge", 1)
    Lb = float(opts.get("len", max(L - 1.0, 14.0) * SWORD_SCALE))
    return dict(G=G, T=T, d=d, nv=nv, k=k, Lb=Lb, Lg=GR_GRIP * k, sag=1.6 * k,
                H=G - d * 2.5 * k, behind=bool(opts.get("behind", False)))


def gryphon_parts(s, n, P):
    k, Lb, Lg = P["k"], P["Lb"], P["Lg"]
    part = np.zeros(s.shape, np.int8)
    sb = np.clip(s / Lb, 0, 1)
    c = -P["sag"] * sb ** 2
    taper = np.clip((Lb - s) / (5.0 * k), 0, 1) ** 0.7
    we = (1.25 * k) * taper + 0.1
    wb = (0.85 * k) * np.clip((Lb - s) / (1.5 * k), 0, 1) ** 0.5
    blade = (s >= 0.8 * k) & (s <= Lb) & (n >= c - wb) & (n <= c + we)
    grip = (s >= -Lg) & (s < -0.6 * k) & (np.abs(n) <= 0.95 * k)
    pc = -Lg - 0.9 * k
    pommel = (s - pc) ** 2 + n ** 2 <= (1.25 * k) ** 2
    # cup guard: short and wide across the blade
    guard = ((s / (1.15 * k)) ** 2 + (n / (2.9 * k)) ** 2 <= 1.0)
    # knuckle-bow: arc on the edge side from the guard to the pommel
    q = np.clip((s - pc) / (0.0 - pc), 0, 1)               # 0 at pommel .. 1 at guard
    nb = (0.6 + 2.6 * np.sin(q * math.pi * 0.55 + 0.35)) * k
    bow = (s >= pc) & (s <= 0.2 * k) & (np.abs(n - nb) <= 0.55) & (n > 0.9 * k)
    part[blade] = SW_BLADE
    part[grip] = SW_GRIP
    part[bow] = SW_BOW
    part[pommel] = SW_POMMEL
    part[guard] = SW_GUARD
    return part


def sword_bounds(P):
    G, d, nv, k = P["G"], P["d"], P["nv"], P["k"]
    pts = [G + d * (P["Lb"] + 1), G - d * (P["Lg"] + 3 * k)]
    for sgn in (-1, 1):
        for t in (-P["Lg"] - 2, 0, P["Lb"] * 0.6):
            pts.append(G + nv * sgn * 5 * k + d * t)
    pts = np.array(pts)
    return (int(math.floor(pts[:, 0].min())) - 2, int(math.floor(pts[:, 1].min())) - 2,
            int(math.ceil(pts[:, 0].max())) + 3, int(math.ceil(pts[:, 1].max())) + 3)


def raster_sword(P):
    x0, y0, x1, y1 = sword_bounds(P)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    px, py = xx + 0.5 - P["G"][0], yy + 0.5 - P["G"][1]
    s = px * P["d"][0] + py * P["d"][1]
    n = px * P["nv"][0] + py * P["nv"][1]
    part = gryphon_parts(s, n, P)
    m = part > 0
    edge = m & (nbcount(m, N4) < 4)
    k = P["k"]
    col = np.zeros(part.shape + (4,), np.uint8)
    c = -P["sag"] * np.clip(s / P["Lb"], 0, 1) ** 2
    rel = n - c
    blade = part == SW_BLADE
    col[blade, :3] = G_BODY
    col[blade & (rel > 0.35 * k), :3] = G_EDGE
    col[blade & (rel < -0.35 * k), :3] = G_OUT
    col[blade & edge & (rel <= 0.35 * k), :3] = G_OUT
    grip = part == SW_GRIP
    col[grip, :3] = G_GRIP
    col[grip & ((np.floor(s) % 2) == 0) & ~edge, :3] = G_GRIP_HI
    for p in (SW_GUARD, SW_POMMEL, SW_BOW):
        pm = part == p
        col[pm, :3] = G_GOLD
        col[pm & (s < -0.2 * k) & (p == SW_GUARD), :3] = G_GOLD_SH
        col[pm & edge & (p != SW_BOW), :3] = G_GOLD_OUT
    col[m, 3] = 255
    return part, col, x0, y0


def paste_window(dst_mask, dst_rgba, part, col, x0, y0, only=None):
    H, W = dst_mask.shape
    h, w = part.shape
    gx0, gy0, gx1, gy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if gx1 <= gx0 or gy1 <= gy0:
        return
    sl = (slice(gy0 - y0, gy1 - y0), slice(gx0 - x0, gx1 - x0))
    m = part[sl] > 0
    if only is not None:
        m &= np.isin(part[sl], only)
    dst_mask[gy0:gy1, gx0:gx1] |= m
    dst_rgba[gy0:gy1, gx0:gx1][m] = col[sl][m]


def shift_spec(P, dx, dy):
    Q = dict(P)
    for key in ("G", "T", "H"):
        Q[key] = P[key] + np.array([dx, dy], float)
    return Q


# ==========================================================================
# character
# ==========================================================================
def content_key(a):
    b = a.copy()
    b[b[..., 3] == 0] = 0
    bb = Image.fromarray(b).getbbox() or (0, 0, 1, 1)
    return hashlib.md5(b[bb[1]:bb[3], bb[0]:bb[2]].tobytes()).hexdigest(), (bb[0], bb[1])


def nearest_true(m, x, y, rmax=4):
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    d = np.hypot(xs + 0.5 - x, ys + 0.5 - y)
    i = int(np.argmin(d))
    return (int(ys[i]), int(xs[i])) if d[i] <= rmax else None


def blob_at(m, x, y, rmax=4):
    p = nearest_true(m, x, y, rmax)
    if p is None:
        return np.zeros_like(m)
    lab, _ = label(m)
    return lab == lab[p]


def inpaint(role, src, hole, prefer_not=(R_OUT,)):
    """Fill hole pixels from their neighbours (most common role, then colour)."""
    role = role.copy()
    src = src.copy()
    known = ~hole
    H, W = role.shape
    for _ in range(60):
        todo = hole & ~known & (nbcount(known) > 0)
        if not todo.any():
            break
        newk = known.copy()
        for y, x in zip(*np.nonzero(todo)):
            cand = {}
            for dy, dx in N8:
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and known[ny, nx]:
                    key = (int(role[ny, nx]), tuple(src[ny, nx]))
                    cand[key] = cand.get(key, 0) + (2 if (dy == 0 or dx == 0) else 1)
            good = {k_: v for k_, v in cand.items() if k_[0] not in prefer_not and k_[0] != R_NONE}
            pool = good or cand
            key = max(sorted(pool), key=lambda k_: pool[k_])
            role[y, x] = key[0]
            src[y, x] = key[1]
            newk[y, x] = True
        known = newk
    return role, src


def window_cls(cls, win):
    out = {}
    for k_, v_ in cls.items():
        out[k_] = (v_ & win) if (isinstance(v_, np.ndarray) and v_.dtype == bool) else v_
    return out


def process_character(bid, a0, rep, lab_of):
    H0, W0 = a0.shape[:2]
    cls0 = classify(a0, bid)
    heads0 = find_heads(cls0)
    # ---- swords (original coordinates)
    specs0, how = [], "none"
    if bid in SWORDS:
        for ent in SWORDS[bid]:
            opts = ent[2] if len(ent) > 2 else {}
            specs0.append(sword_spec(ent[0], ent[1], 1.0, opts))
        how = "annotated"
    elif bid in AUTO_PER_HEAD:
        hw = AUTO_PER_HEAD[bid]
        hits_ = []
        for hd in heads0:
            win = np.zeros(a0.shape[:2], bool)
            fx = int(hd["fc"][0])
            win[:, max(0, fx - hw):fx + hw] = True
            r = auto_sword(window_cls(cls0, win), [hd])
            if r is not None:
                specs0.append(sword_spec(r[0], r[1]))
                hits_.append(r[2])
        how = f"auto-per-head{hits_}"
    else:
        r = auto_sword(cls0, heads0)
        if r is not None:
            G, T, hits = r
            specs0.append(sword_spec(G, T))
            how = f"auto({hits})"
    # ---- grounded poses: a downward blade stops at the floor (never shorter
    # than the old katana)
    if bid not in NO_LEGS:
        oys, oxs = np.nonzero(cls0["op"] & ~cls0["trail"])
        for P in specs0:
            if P["d"][1] > 0.25:
                sel = np.abs(oxs + 0.5 - P["G"][0]) <= 34
                if sel.any():
                    floor = oys[sel].max() + 1.0
                    lmax = (floor - P["G"][1]) / P["d"][1] - 0.5
                    old_len = float(np.linalg.norm(P["T"] - P["G"]))
                    P["Lb"] = float(max(min(P["Lb"], lmax), old_len - 1.0, 14.0))
    # ---- padding
    l = t = r_ = b = 0
    for P in specs0:
        part, _, x0, y0 = raster_sword(P)
        ys, xs = np.nonzero(part)
        if len(xs):
            l = max(l, -(xs.min() + x0))
            t = max(t, -(ys.min() + y0))
            r_ = max(r_, xs.max() + x0 - (W0 - 1))
            b = max(b, ys.max() + y0 - (H0 - 1))
    pad = [int(l), int(t), int(r_), int(b)]
    a = np.zeros((H0 + t + b, W0 + l + r_, 4), np.uint8)
    a[t:t + H0, l:l + W0] = a0
    specs = [shift_spec(P, l, t) for P in specs0]
    H, W = a.shape[:2]
    cls = classify(a, bid, l)
    heads = find_heads(cls)
    if not heads:
        raise SystemExit(f"{bid}: no head found")
    op = cls["op"]
    role = np.zeros((H, W), np.int8)
    role[:] = cloth_roles(cls)
    role[cls["skin"]] = R_SKIN
    role[cls["hair"]] = R_HAIR
    role[cls["gold"]] = R_GOLD
    role[cls["trail"]] = R_TRAIL
    role[cls["other"]] = R_OTHER
    role[~op] = R_NONE
    src = a[..., :3].copy()
    removed = np.zeros((H, W), bool)          # originally opaque pixels removed
    yy, xx = np.mgrid[0:H, 0:W]
    # ---- hands
    hb = hand_blobs(cls, heads)
    sword_hand = np.zeros((H, W), bool)
    for P in specs:
        best = None
        hp = P.get("hand")
        for hx, hy, hm in hb:
            d = math.hypot(hx - P["H"][0], hy - P["H"][1])
            if d <= 5.5 and (best is None or d < best[0]):
                best = (d, hm)
        if best:
            sword_hand |= best[1]
    # ---- old katana: blade + hilt outside the body, tsuba
    thin = blade_pixels(cls)
    code = sword_code(cls)
    for P in specs:
        v = P["T"] - P["G"]
        L = np.linalg.norm(v)
        u = v / (L + 1e-9)
        px, py = xx + 0.5 - P["G"][0], yy + 0.5 - P["G"][1]
        tt = px * u[0] + py * u[1]
        dist = np.abs(px * -u[1] + py * u[0])
        band = (dist <= 2.6) & (tt >= -16) & (tt <= L + 3.5)
        old = band & (thin | (code & (dist <= 2.0))) & ~sword_hand & (role != R_SKIN)
        tsuba = cls["gold"] & (np.hypot(px, py) <= 4.0)
        kill = old | tsuba
        removed |= kill & op
        role[kill] = R_NONE
    # ---- left arm
    arm_notes = []
    for ent in ARMS.get(bid, []):
        if isinstance(ent, tuple) and len(ent) == 2 and not isinstance(ent[0], str):
            x, y = ent[0] + l + 0.5, ent[1] + t + 0.5
            bm = blob_at(cls["skin"] & ~sword_hand, x, y)
            if not bm.any():
                arm_notes.append(f"no skin at {ent}")
                continue
            ring = dilate(bm, 1) & ~bm & (role == R_OUT)
            # outline pixels that only separate the blob from the background
            other = op & ~bm & (role != R_OUT)
            lone = ring & (nbcount(other, N4) == 0)
            kill = bm | lone
            arm_notes.append(f"blob {ent}: {int(bm.sum())}px")
        else:
            _, pts, mode = ent
            pm = poly_mask((H, W), [(p[0] + l, p[1] + t) for p in pts]) & op
            kill = pm & ~sword_hand
            if mode == "fill":
                role, src = inpaint(role, src, kill & op)
                arm_notes.append(f"poly fill {int(kill.sum())}px")
                continue
            if mode == "cape":
                cm = kill & np.isin(role, [R_CLOTH, R_CLOTH_HL, R_FOLD, R_SKIN])
                src[cm & (role == R_CLOTH_HL)] = (212, 212, 212)
                src[cm & (role != R_CLOTH_HL)] = (156, 156, 156)
                role[cm] = R_CAPE
                arm_notes.append(f"poly cape {int(cm.sum())}px")
                continue
            arm_notes.append(f"poly cut {int(kill.sum())}px")
        removed |= kill & op
        role[kill] = R_NONE
    # ---- hair
    hair_new = np.zeros((H, W), bool)
    hair_add = np.zeros((H, W), bool)
    hair_geo = []
    head_info = []
    for hd in heads:
        keep, c, dn = hair_mass(cls, hd)
        drop = hd["hair"] & ~keep
        removed |= drop
        role[drop] = R_NONE
        # bells: gold next to the hair
        bells = cls["gold"] & dilate(hd["hair"], 2) & ~keep
        removed |= bells
        role[bells] = R_NONE
        # Kenpachi's bangs across the face -> skin (Shanks: parted, face open)
        up = hd["hc"] - hd["fc"]
        bangs = np.zeros((H, W), bool)
        if up[1] < 0 and abs(up[0]) <= 1.2 * abs(up[1]):
            fy, fx = np.nonzero(hd["face"])
            top = fy.min()
            for y in range(top + 2, fy.max() + 1):
                xs_ = fx[fy == y]
                if len(xs_) >= 2:
                    seg = np.zeros(W, bool)
                    seg[xs_.min() + 1:xs_.max()] = True
                    bangs[y] |= keep[y] & seg
            # no red "beard": hair under the chin on the front half goes
            fcx = fx.mean() + 0.5
            chin = keep & (yy >= fy.max()) & (xx + 0.5 >= fcx - 1.0)
            chin |= keep & (yy >= top + 6) & (xx >= fx.min() + 1) & (xx <= fx.max())
            if chin.any():
                keep = keep & ~chin
                role[chin] = R_NONE
                removed |= chin
        if bangs.any():
            role[bangs] = R_SKIN
            skin_px = (role == R_SKIN) & ~bangs
            todo = bangs.copy()
            for _ in range(6):
                ys_, xs_ = np.nonzero(todo)
                if not len(ys_):
                    break
                done = []
                for y_, x_ in zip(ys_, xs_):
                    cand = {}
                    for dy_, dx_ in N8:
                        ny_, nx_ = y_ + dy_, x_ + dx_
                        if 0 <= ny_ < H and 0 <= nx_ < W and skin_px[ny_, nx_]:
                            c_ = tuple(int(v) for v in src[ny_, nx_])
                            if luma(np.array(c_))[()] >= 0.45:      # skin tones, not eyes
                                cand[c_] = cand.get(c_, 0) + 1
                    if cand:
                        src[y_, x_] = max(sorted(cand), key=lambda c_: cand[c_])
                        done.append((y_, x_))
                for y_, x_ in done:
                    todo[y_, x_] = False
                    skin_px[y_, x_] = True
            src[todo] = SKIN_MID
            keep = keep & ~bangs
        # v3: long hair to the jaw / nape
        g = hair_geometry(hd, c, dn, bid)
        # hair-coded pixels on the lower front of the face (Kenpachi's beard / patch
        # strap at the mouth): jaw outline or skin, never red marks on the face
        fa = (xx + 0.5 - g["fc"][0]) * g["fwd"][0] + (yy + 0.5 - g["fc"][1]) * g["fwd"][1]
        fb = (xx + 0.5 - g["fc"][0]) * g["up"][0] + (yy + 0.5 - g["fc"][1]) * g["up"][1]
        mouth = keep & (fa > 0.0) & (fb < -0.5) & (not g["back"])
        if mouth.any():
            keep = keep & ~mouth
            bg_ = nbcount((role == R_NONE) & ~mouth, N4) > 0
            role[mouth & bg_] = R_OUT
            src[mouth & bg_] = OUTLINE
            role[mouth & ~bg_] = R_SKIN
            src[mouth & ~bg_] = SKIN_MID
        add = long_hair(g, role, hd, keep, sword_hand, (H, W)) & ~keep
        hair_add |= add
        keep = keep | add
        hair_geo.append(g)
        hair_new |= keep
        role[keep] = R_HAIR
        head_info.append(dict(fc=[round(float(v), 1) for v in hd["fc"] - [l, t]],
                              hc=[round(float(v), 1) for v in hd["hc"] - [l, t]],
                              hair_px=int(keep.sum()), long_hair_px=int(add.sum())))
    ring = (role == R_NONE) & (nbcount(hair_add, N4) > 0)
    role[ring] = R_OUT
    src[ring] = OUTLINE
    # outline specks left floating next to the head (roots of the trimmed spikes)
    for _ in range(3):
        fill = (role != R_NONE) & (role != R_OUT)
        lone = (role == R_OUT) & (nbcount(fill, N8) == 0)
        lone |= (role == R_OUT) & (nbcount(fill, N4) == 0) & (nbcount(role == R_OUT, N8) <= 1)
        lone &= dilate(hair_new | hair_add, 3)
        if not lone.any():
            break
        role[lone] = R_NONE
    if (hair_add[0].any() or hair_add[-1].any() or hair_add[:, 0].any() or hair_add[:, -1].any()):
        rep["warn_hair_at_border"] = True
    # ---- holes inside the figure -> inpaint; open cuts -> outline
    alive = role != R_NONE
    outside = reach_border(~alive)
    holes = ~alive & ~outside & (op | hair_new)
    if holes.any():
        role, src = inpaint(role, src, holes)
    alive = role != R_NONE
    edge_cut = removed & ~alive & (nbcount(alive & (role != R_OUT), N4) > 0)
    role[edge_cut] = R_OUT
    src[edge_cut] = OUTLINE
    # stray outline pixels / specks left by the cuts
    for _ in range(3):
        alive = role != R_NONE
        lone = (role == R_OUT) & (nbcount(alive & (role != R_OUT), N8) == 0) & dilate(removed, 2)
        speck = alive & (nbcount(alive, N8) <= 1) & dilate(removed, 2)
        kill = lone | speck
        if not kill.any():
            break
        role[kill] = R_NONE
    # ---- dark marks drawn inside the haori (Kenpachi's squad kanji, hem lines):
    # absorbed into the black cape (no Bleach insignia on Shanks's cape)
    for _ in range(2):
        capem = role == R_CAPE
        mark = (role == R_OUT) & (nbcount(capem, N4) >= 3) & (nbcount(role == R_NONE, N4) == 0)
        if not mark.any():
            break
        role[mark] = R_CAPE
        src[mark] = (212, 212, 212)
    # ---- waist split, cape over the arms, then 3/4 pants + bare shins + sandals + floor-length cape
    side, sash, anchor, lines = cloth_side(role, cls, heads, bid, l, t)
    ext = np.zeros((H, W), bool)                      # floor-length cape pixels (new)
    if bid not in NO_LEGS:
        legs_and_cape(role, src, side, heads, rep, ext)
    tone = np.full((H, W), -1, np.int8)              # explicit cape tones (sleeves turned into cape)
    cape_over_arms(role, src, side, heads, sword_hand, tone, lines, rep, bid in BACK_VIEW)
    rep["waist"] = [[[round(float(q[0] - l), 1), round(float(q[1] - t), 1)] for q in pl] for pl in lines]
    # ---- render at 2x
    PL, dyn = paint_labels(role, src, side, sash, cls, heads, tone, ext)
    denoise_labels(PL)
    tm = role == R_TRAIL
    tfield = trail_field(tm, src) if tm.any() else np.zeros((H, W))
    out, _, _ = render2x(PL, dyn, tfield, hair_geo, specs, sword_hand, heads, hair_new)
    rep["kind"] = "combined" if int(tm.sum()) >= 20 else "character"
    rep["trail_px"] = int(tm.sum())
    rep["heads"] = head_info
    rep["sword"] = dict(source=how, swords=[dict(guard=[round(float(v), 1) for v in P["G"] - [l, t]],
                                                 tip=[round(float(v), 1) for v in P["T"] - [l, t]],
                                                 blade=round(P["Lb"], 1)) for P in specs])
    rep["arm"] = arm_notes or ["none"]
    return out, pad


def waist_lines(bid, heads, cls, l, t):
    """Waist polylines (one per figure) in padded coordinates."""
    if bid in WAIST:
        return [[(x + l, y + t) for x, y in pl] for pl in WAIST[bid]]
    lines = []
    op = cls["op"] & ~cls["trail"]
    ys, xs = np.nonzero(op)
    for hd in heads:
        fx, fy = hd["fc"]
        sel = np.abs(xs + 0.5 - fx) <= 28
        bottom = ys[sel].max() + 1 if sel.any() else fy + 50
        wy = fy + 0.5 * (bottom - fy)
        lines.append([(fx - 30, wy), (fx + 30, wy)])
    return lines


def legs_and_cape(role, src, side, heads, rep, ext=None):
    """Grounded upright figures (head above the face):
      * the pants end just below the knee (KNEE of the way waist -> floor);
      * each leg is tracked up from its foot through the pants and replaced by a
        3 px bare shin (outline added by the closure pass);
      * feet (Kenpachi's tabi + zori) become bare feet on brown strap sandals;
      * the black cape hangs behind the legs down to the floor (new pixels only
        where the canvas is empty, so the legs stay in front), with vertical folds.
    Edits role / src in place."""
    H, W = role.shape
    yy, xx = np.mgrid[0:H, 0:W]
    notes = []
    removed = np.zeros((H, W), bool)
    added = np.zeros((H, W), bool)
    for hd in heads:
        fx_, fy_ = hd["fc"]
        if hd["hc"][1] > fy_:                       # head not up: lying / upside down
            continue
        colm = np.abs(xx + 0.5 - fx_) <= 34
        clothy = np.isin(role, [R_CLOTH, R_CLOTH_HL, R_FOLD])
        pants = clothy & (side < 0) & colm
        if pants.sum() < 25:
            continue
        fig = (role != R_NONE) & (role != R_TRAIL) & colm
        floor = int(np.nonzero(fig.any(1))[0].max())
        py_, px_ = np.nonzero(pants)
        wy = float(py_.min())
        if floor - wy < 10:
            continue
        knee = wy + KNEE * (floor - wy)
        # feet: bottom-band components touching the pants
        band = fig & (yy >= floor - 3) & (role != R_CAPE) | (fig & (yy >= floor - 3) & (role == R_CAPE) & dilate(pants, 3))
        lab, n = label(band)
        feet = []
        for k in range(1, n + 1):
            ck = lab == k
            if ck.sum() >= 4 and (dilate(ck, 3) & pants).any():
                fyy, fxx = np.nonzero(ck)
                feet.append((ck, fxx.mean() + 0.5, int(fyy.min())))
        if not feet:
            notes.append("no feet")
            continue
        # legs = straight bands hip -> foot.  Pants survive only inside the
        # bands (slightly baggy) and above the knee; shins below the knee.
        top_rows = pants & (yy <= wy + 2)
        hip_cx = np.nonzero(top_rows)[1].mean() + 0.5 if top_rows.any() else fx_
        feet.sort(key=lambda f: f[1])
        crotch = wy + 0.30 * (floor - wy)
        legd = np.full((H, W), 1e9)
        legt = np.zeros((H, W))
        legs = []
        for i, (ck, cx, ftop) in enumerate(feet):
            off = (i - (len(feet) - 1) / 2.0) * 5.0
            P0 = np.array([hip_cx + off, wy])
            P1 = np.array([cx, float(ftop)])
            v = P1 - P0
            Lv = np.linalg.norm(v) + 1e-9
            u = v / Lv
            qx, qy = xx + 0.5 - P0[0], yy + 0.5 - P0[1]
            tt = np.clip((qx * u[0] + qy * u[1]) / Lv, 0, 1)
            dd = np.hypot(qx - tt * v[0], qy - tt * v[1])
            closer = dd < legd
            legd = np.where(closer, dd, legd)
            legt = np.where(closer, tt, legt)
            legs.append((P0, P1, u, Lv))
        halfw = 3.2 + 1.2 * legt                      # a little baggy towards the knee
        keep_p = (legd <= halfw) | (yy <= crotch)
        cut = pants & ~keep_p & colm
        low = (yy > knee) & colm
        cut |= pants & low
        cut |= (role == R_OUT) & colm & (yy > crotch) & dilate(cut, 1) & ~dilate(
            np.isin(role, [R_CAPE, R_SKIN, R_HAIR]) | (clothy & (side >= 0)), 1)
        for ck, _, _ in feet:
            cut &= ~ck
        role[cut] = R_NONE
        removed |= cut
        # shins along each leg line from the knee to the foot (3 px)
        for (ck, cx, ftop), (P0, P1, u, Lv) in zip(feet, legs):
            for y in range(int(math.floor(knee)) + 1, ftop):
                k_ = (y + 0.5 - P0[1]) / max(P1[1] - P0[1], 1e-6)
                c = int(math.floor(P0[0] + k_ * (P1[0] - P0[0])))
                for x, col in ((c - 1, SKIN_SH), (c, SKIN_MID), (c + 1, SKIN_MID)):
                    if 0 <= x < W and role[y, x] != R_HAIR:
                        role[y, x] = R_SKIN
                        src[y, x] = col
                        added[y, x] = True
            # sandals: bare foot, one strap row, dark sole
            fyy, fxx = np.nonzero(ck)
            for y, x in zip(fyy, fxx):
                if role[y, x] == R_OUT and y < floor:
                    continue
                role[y, x] = R_SKIN
                if y >= floor:
                    src[y, x] = SANDAL_DK
                elif y == floor - 1 and (x % 2 == 0):
                    src[y, x] = SANDAL
                else:
                    src[y, x] = SKIN_MID
        # floor-length cape behind the legs: columns where the cape hangs below
        # the waist, limited to the legs' span (+-3)
        cape = (role == R_CAPE) & colm & (yy >= wy - 2)
        cols = np.nonzero(cape.any(0))[0]
        if len(cols):
            lx0, lx1 = px_.min() - 3, px_.max() + 3
            sel = np.zeros(W, bool)
            sel[cols] = True
            # close gaps of <= 2 columns
            for x in range(W):
                if not sel[x] and sel[max(0, x - 3):x].any() and sel[x + 1:x + 4].any():
                    sel[x] = True
            sel[:max(0, lx0)] = False
            sel[min(W, lx1 + 1):] = False
            cols_ = np.nonzero(sel)[0]
            for x in cols_:
                ys_c = np.nonzero(cape[:, x])[0]
                y0 = int(ys_c.max()) + 1 if len(ys_c) else int(wy)
                # hem: a gentle wave, the outer corners rounded off (no box)
                edge_d = min(x - cols_.min(), cols_.max() - x)
                lift = int(round(0.6 + 0.6 * math.sin(x * 1.3))) + max(0, 2 - edge_d)
                for y in range(y0, floor - lift):
                    if role[y, x] == R_NONE:
                        role[y, x] = R_CAPE
                        src[y, x] = (254, 254, 254)
                        if ext is not None:
                            ext[y, x] = True
                        added[y, x] = True
        notes.append(f"knee y={knee - 0:.1f} floor={floor} feet={len(feet)}")
    # close the new silhouettes: outline where new / cut areas meet the background
    alive = role != R_NONE
    edge = (removed | dilate(added, 1)) & ~alive & (nbcount(alive & (role != R_OUT), N4) > 0)
    role[edge] = R_OUT
    src[edge] = OUTLINE
    rep["legs"] = notes or ["skipped"]


def cloth_side(role, cls, heads, bid, l, t):
    """Signed distance to the nearest waist polyline (+ = face side = shirt) and the sash mask."""
    H, W = role.shape
    yy, xx = np.mgrid[0:H, 0:W]
    lines = waist_lines(bid, heads, cls, l, t)
    clothy = np.isin(role, [R_CLOTH, R_CLOTH_HL, R_FOLD])
    # side of the nearest waist line: + = face side (shirt)
    best_d = np.full((H, W), 1e9)
    side = np.zeros((H, W))
    sash = np.zeros((H, W), bool)
    anchor = []
    fcs = [hd["fc"] for hd in heads]
    for pl in lines:
        pts = [np.array(q, float) for q in pl]
        mid = sum(pts) / len(pts)
        fc = min(fcs, key=lambda f: np.hypot(*(f - mid)))
        nseg = len(pts) - 1
        for si in range(nseg):
            p0, p1 = pts[si], pts[si + 1]
            dv = p1 - p0
            Ln = np.linalg.norm(dv) + 1e-9
            u = dv / Ln
            nrm = np.array([-u[1], u[0]])
            # face side: the side of the whole polyline's first->last chord
            ch = pts[-1] - pts[0]
            cn = np.array([-ch[1], ch[0]])
            sgn = 1.0 if (fc - pts[0]) @ cn >= 0 else -1.0
            sgn *= 1.0 if nrm @ cn >= 0 else -1.0
            px, py = xx + 0.5 - p0[0], yy + 0.5 - p0[1]
            sd = (px * nrm[0] + py * nrm[1]) * sgn
            along = px * u[0] + py * u[1]
            lo = -1e9 if si == 0 else 0.0
            hi = 1e9 if si == nseg - 1 else Ln
            inseg = (along >= lo) & (along <= hi)
            dseg = np.where(inseg, np.abs(sd),
                            np.minimum(np.hypot(px, py), np.hypot(xx + 0.5 - p1[0], yy + 0.5 - p1[1])))
            closer = dseg < best_d
            best_d = np.where(closer, dseg, best_d)
            side = np.where(closer, sd, side)
            sash |= (np.abs(sd) <= 1.0) & (along >= max(lo, -6)) & (along <= min(hi, Ln + 6))
        anchor.append(mid)
    return side, sash, anchor, lines


# ==========================================================================
# v3: cape over the arms, long hair
# ==========================================================================
def unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-9)


def closest_on_polyline(pl, p):
    best = None
    for p0, p1 in zip(pl, pl[1:]):
        p0, p1 = np.array(p0, float), np.array(p1, float)
        d = p1 - p0
        k = float(np.clip((p - p0) @ d / (d @ d + 1e-9), 0, 1))
        q = p0 + k * d
        dist = float(np.linalg.norm(q - p))
        if best is None or dist < best[0]:
            best = (dist, q)
    return best


def seg_dist(xx, yy, p0, p1):
    """Distance of pixel centres to the segment p0-p1 and the clamped position along it (0..1)."""
    d = p1 - p0
    L2 = d @ d + 1e-9
    qx, qy = xx + 0.5 - p0[0], yy + 0.5 - p0[1]
    k = np.clip((qx * d[0] + qy * d[1]) / L2, 0, 1)
    return np.hypot(qx - k * d[0], qy - k * d[1]), k


def cape_over_arms(role, src, side, heads, sword_hand, tone, lines, rep, back_view=False):
    """Feedback 2 (v3): the cape is the outer layer over both shoulders.  Shirt
    pixels (Kenpachi's black kimono above the waist) stay white only
      * in the open front: a band of CHEST_W px around the torso axis (neck ->
        waist) plus the cloth right next to the bare chest (the V-neck), and
      * on the sword arm's forearm: FOREARM px (geodesic) up the sleeve from the hand;
    the rest (shoulders, upper arms, the free sleeve) becomes cape, keeping the
    sleeve's folds as cape tones (cloth -> base, highlights -> light, folds -> shade)."""
    H, W = role.shape
    clothy = np.isin(role, [R_CLOTH, R_CLOTH_HL, R_FOLD])
    shirt = clothy & (side >= 0)
    if not shirt.any() or not heads:
        rep["cape_arms"] = "no shirt"
        return
    yy, xx = np.mgrid[0:H, 0:W]
    band = np.zeros((H, W), bool)
    wide = np.zeros((H, W), bool)
    faces = np.zeros((H, W), bool)
    for hd in heads:
        faces |= dilate(hd["face"], 1)
        up = unit(hd["hc"] - hd["fc"])
        if up[1] < -0.5:                              # upright: the torso hangs vertically
            up = unit(up + np.array([0.0, -2.5]))
        neck = hd["fc"] - up * 5.0
        target = hd["fc"] - up * 24.0
        cands = [closest_on_polyline(pl, target) for pl in lines]
        cands = [c for c in cands if c is not None]
        wp = min(cands, key=lambda c: c[0])[1] if cands else target
        if np.linalg.norm(wp - neck) < 6:
            wp = neck - up * 14.0
        d, k = seg_dist(xx, yy, neck, wp)
        band |= (d <= CHEST_W) & (k > 0) & (k < 1)
        band |= (d <= CHEST_W) & (k >= 1)
        wide |= (d <= CHEST_W + 3.0)
    chest_skin = (role == R_SKIN) & wide & ~faces
    # open V-neck: the cloth framing the bare chest is the white shirt, even where
    # Kenpachi has his haori lapels (those would read as a black collar on the chest)
    vneck = (role == R_CAPE) & dilate(chest_skin, 2) & band & (side >= 0) & ~dilate(faces, 2)
    if back_view:
        vneck[:] = False
    if vneck.any():
        role[vneck] = R_CLOTH
        shirt |= vneck
    # the kimono collar right under the chin: neck shadow (white there reads as a beard)
    collar = shirt & dilate(faces, 2) & ~vneck
    role[collar] = R_SKIN
    src[collar] = SKIN_SH
    shirt &= ~collar
    chest = shirt & (band | dilate(chest_skin, 2))
    if back_view:
        chest[:] = False                              # seen from behind: all cape
    fore = shirt & dilate(sword_hand, 2)
    for _ in range(int(FOREARM)):
        if fore.sum() >= FORE_MAX:                   # hanging arm: wide sleeve end, keep a cuff only
            break
        fore |= dilate(fore, 1) & shirt
    conv = shirt & ~chest & ~fore
    # white specks left between cape pixels
    rest = shirt & ~conv
    lab_, n_ = label(rest)
    near_v = dilate(chest_skin, 2)
    for k_ in range(1, n_ + 1):
        ck = lab_ == k_
        if not (ck & fore).any() and (ck.sum() <= 3 or (ck.sum() <= 10 and not (ck & near_v).any())):
            conv |= ck
    tone[conv & (role == R_CLOTH)] = 2
    tone[conv & (role == R_CLOTH_HL)] = 3
    tone[conv & (role == R_FOLD)] = 1
    role[conv] = R_CAPE
    rep["cape_arms"] = f"{int(conv.sum())}px to cape, chest {int(chest.sum())}, forearm {int((fore & ~chest).sum())}"


def hair_geometry(hd, c, dn, bid):
    """Head frame for the long hair: `up` leans towards the screen vertical for
    upright heads (hair falls with gravity), `fwd` points at the face."""
    up = unit(dn)
    if up[1] < -0.5:
        up = unit(up + np.array([0.0, -1.5]))
    perp = np.array([-up[1], up[0]])
    s = 1.0 if (hd["fc"] - hd["hc"]) @ perp >= 0 else -1.0
    return dict(c=np.array(c, float), fc=np.array(hd["fc"], float), up=up, fwd=perp * s,
                R=7.4, back=bid in BACK_VIEW)


def long_hair(g, role, hd, keep, sword_hand, shape):
    """Feedback 3 (v3): Shanks's red hair falls to the jaw / nape: a mass behind
    the face from the crown down to HAIR_TIP px under the face centre (over the
    ear, so it frames the face from behind), fuller at the back, pointed tips.
    New pixels only replace background, cape, cloth and outline (and the back
    two pixels of the face: the ear); never hands, gold or trails."""
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    fc, up, fwd = g["fc"], g["up"], g["fwd"]
    px, py = xx + 0.5 - fc[0], yy + 0.5 - fc[1]
    a = px * fwd[0] + py * fwd[1]
    b = px * up[0] + py * up[1]
    ka = a[keep & (np.abs(b) <= 3.5)]
    a_back = float(np.clip(ka.min() if len(ka) else -6.5, -7.6, -5.0))
    q = np.clip(-b / HAIR_TIP, 0, 1)
    tipcut = 1.3 * np.abs(np.sin(np.pi * (a - a_back) / 2.5)) * (q > 0.75)
    if g["back"]:
        kc = float(ka.mean()) if len(ka) else 0.0
        body = (np.abs(a - kc) <= (-a_back * 0.5 + 3.0) - 1.2 * q ** 2) & (b <= 3.0)
    else:
        body = (a >= a_back - 0.4 + 1.5 * q ** 2) & (a <= -2.3 + 0.4 * q) & (b <= 3.0)
    body &= b >= -HAIR_TIP + tipcut
    face = hd["face"] & (role == R_SKIN)
    ok = np.isin(role, [R_NONE, R_CAPE, R_LINING, R_OUT, R_CLOTH, R_CLOTH_HL, R_FOLD, R_HAIR])
    ok |= face & (a < -2.0)
    ok &= ~dilate(sword_hand, 1)
    add = body & ok
    lab_, n_ = label(add | keep)
    if n_:
        hit = set(np.unique(lab_[keep]).tolist()) - {0}
        add &= np.isin(lab_, list(hit))
    return add


# ==========================================================================
# v3: 2x magnification and rendering
# ==========================================================================
# paint labels: the 1x picture as a map of flat tone labels, magnified to 2x
(L_BG, L_OUT, L_CAPE0, L_CAPE1, L_CAPE2, L_CAPE3, L_CAPE4, L_CAPEX, L_LIN0, L_LIN1,
 L_SH0, L_SH1, L_SH2, L_PA0, L_PA1, L_PA2, L_PA3, L_PAOUT, L_SASH0, L_SASH1,
 L_SK0, L_SK1, L_SK2, L_FEAT, L_EYE, L_HAIR, L_SAN0, L_SAN1, L_TRAIL) = range(29)
L_DYN = 64                         # first label of the kept colours (gold leftovers, misc)
LABEL_RGB = {L_OUT: OUTLINE, L_CAPEX: CAPE_T[2], L_LIN0: LIN_T[0], L_LIN1: LIN_T[1],
             L_PAOUT: (56, 8, 16), L_SASH0: SASH_T[0], L_SASH1: SASH_T[1], L_FEAT: FEAT_C,
             L_EYE: EYE, L_HAIR: HAIR_T[2], L_SAN0: SAND_T[0], L_SAN1: SAND_T[1]}
for _i in range(5):
    LABEL_RGB[L_CAPE0 + _i] = CAPE_T[_i]
for _i in range(3):
    LABEL_RGB[L_SH0 + _i] = SHIRT_T[_i]
    LABEL_RGB[L_SK0 + _i] = SKIN_T[_i]
for _i in range(4):
    LABEL_RGB[L_PA0 + _i] = PANTS_T[_i]
SKIN_LABELS = [L_SK0, L_SK1, L_SK2, L_FEAT, L_EYE, L_SAN0, L_SAN1]
# tone groups cleaned at 1x: (labels, base label, max speck size merged into the neighbours)
TONE_GROUPS = [([L_CAPE0, L_CAPE1, L_CAPE2, L_CAPE3], L_CAPE2, 2),
               ([L_SH0, L_SH1, L_SH2], L_SH2, 1),
               ([L_PA0, L_PA1, L_PA2, L_PA3], L_PA2, 3),
               ([L_LIN0, L_LIN1], L_LIN1, 1)]


def scale2x(L):
    """EPX / Scale2x on a label map (labels only, no blending)."""
    P = np.pad(L, 1, mode="edge")
    E, B, Hh, D, F = P[1:-1, 1:-1], P[:-2, 1:-1], P[2:, 1:-1], P[1:-1, :-2], P[1:-1, 2:]
    o = np.empty((L.shape[0] * 2, L.shape[1] * 2), L.dtype)
    o[0::2, 0::2] = np.where((D == B) & (B != F) & (D != Hh), D, E)
    o[0::2, 1::2] = np.where((B == F) & (B != D) & (F != Hh), F, E)
    o[1::2, 0::2] = np.where((D == Hh) & (D != B) & (Hh != F), D, E)
    o[1::2, 1::2] = np.where((Hh == F) & (D != Hh) & (B != F), F, E)
    return o


def magnify_labels(L, sigma=1.1, boost=None):
    """2x magnification of a label map that keeps every label crisp (no blended
    colours): Scale2x twice (4x; 1 px lines and single pixels survive), then each
    label's indicator is Gaussian-smoothed at 4x (rounds the remaining stair
    steps: silhouettes and tone bands get smooth contours at any angle) and pooled
    to 2x; every output pixel takes the label with the highest score."""
    L4 = scale2x(scale2x(L))
    H4, W4 = L4.shape
    H2, W2 = H4 // 2, W4 // 2
    best = np.full((H2, W2), -1.0, np.float32)
    out = np.zeros((H2, W2), L.dtype)
    m = int(math.ceil(sigma * 4)) + 2
    m += m % 2
    for lab in np.unique(L4):
        ind = L4 == lab
        ys, xs = np.nonzero(ind.any(1))[0], np.nonzero(ind.any(0))[0]
        y0, x0 = max(0, (ys[0] - m) // 2 * 2), max(0, (xs[0] - m) // 2 * 2)
        y1, x1 = min(H4, ys[-1] + 1 + m), min(W4, xs[-1] + 1 + m)
        y1 -= (y1 - y0) % 2
        x1 -= (x1 - x0) % 2
        s = ndi.gaussian_filter(ind[y0:y1, x0:x1].astype(np.float32), sigma, mode="nearest")
        p = s[0::2, 0::2] + s[1::2, 0::2] + s[0::2, 1::2] + s[1::2, 1::2]
        if boost:
            p *= boost.get(int(lab), 1.0)
        sl = (slice(y0 // 2, y1 // 2), slice(x0 // 2, x1 // 2))
        k = p > best[sl]
        best[sl][k] = p[k]
        out[sl][k] = lab
    return out


def magnify_field(v, m):
    """2x bilinear magnification of a scalar field known on mask m (values outside
    m are first filled from the nearest known pixel, so nothing bleeds in)."""
    v = np.asarray(v, np.float32)
    if m.any() and not m.all():
        idx = ndi.distance_transform_edt(~m, return_distances=False, return_indices=True)
        v = v[idx[0], idx[1]]
    return ndi.zoom(v, 2, order=1, mode="nearest", grid_mode=True)


def quant(t):
    """Ramp positions in RAMP_LEVELS steps: smooth at display scale, compresses
    about 2x better in the SWF than a continuous gradient."""
    return np.round(np.clip(t, 0, 1) * RAMP_LEVELS) / RAMP_LEVELS


def up_nn(m, k=2):
    return np.repeat(np.repeat(m, k, 0), k, 1)


def scale_spec(P, k):
    Q = dict(P)
    for key in ("G", "T", "H"):
        Q[key] = np.asarray(P[key], float) * k
    for key in ("k", "Lb", "Lg", "sag"):
        Q[key] = P[key] * k
    return Q


def paint_labels(role, src, side, sash, cls, heads, tone, ext):
    """1x role map -> paint labels (tone bands per material) + kept colours."""
    H, W = role.shape
    PL = np.zeros((H, W), np.int16)
    dyn = {}
    clothy = np.isin(role, [R_CLOTH, R_CLOTH_HL, R_FOLD])
    shirt = clothy & (side >= 0)
    pants = clothy & (side < 0)
    PL[shirt & (role == R_CLOTH)] = L_SH2
    PL[shirt & (role == R_CLOTH_HL)] = L_SH1
    PL[shirt & (role == R_FOLD)] = L_SH0
    # neat pants: Kenpachi's hakama pleats (thin highlight streaks) are dropped,
    # only broad highlight patches stay; enclosed fold lines become a soft shade
    PL[pants] = L_PA2
    hl = pants & (role == R_CLOTH_HL)
    PL[dilate(erode(hl, 1, N4), 1, N4) & hl] = L_PA3
    sm = sash & clothy
    PL[sm] = L_SASH1
    PL[sm & (side < -0.3)] = L_SASH0
    PL[sm & (nbcount(clothy | (role == R_SKIN), N4) < 4)] = L_SASH0
    Lc = luma(src)
    cape = role == R_CAPE
    lvl = np.digitize(Lc, [0.45, 0.62, 0.86])          # haori: white = base, greys = shade
    PL[cape] = np.array([L_CAPE0, L_CAPE0, L_CAPE1, L_CAPE2], np.int16)[lvl[cape]]
    tv = cape & (tone >= 0)
    PL[tv] = L_CAPE0 + tone[tv]
    PL[cape & ext] = L_CAPEX
    lin = role == R_LINING
    PL[lin] = L_LIN1
    PL[lin & (Lc < 0.2)] = L_LIN0
    sk = role == R_SKIN
    PL[sk] = L_SK1
    PL[sk & (Lc >= 0.78)] = L_SK2
    PL[sk & (Lc < 0.58)] = L_SK0
    PL[sk & (Lc < 0.33)] = L_FEAT
    PL[sk & color_eq(src, SANDAL)] = L_SAN1
    PL[sk & color_eq(src, SANDAL_DK)] = L_SAN0
    PL[role == R_HAIR] = L_HAIR
    PL[role == R_TRAIL] = L_TRAIL
    PL[role == R_OUT] = L_OUT
    po = (role == R_OUT) & (nbcount(pants, N4) >= 1) & (
        nbcount(np.isin(role, [R_SKIN, R_CAPE, R_HAIR]) | (clothy & ~pants), N8) == 0)
    PL[po] = L_PAOUT
    # lines drawn inside the pants (no background next to them): short fold marks
    # vanish, long ones (the line between the two legs) stay as a dark crimson line
    inner = po & (nbcount(role == R_NONE, N8) == 0) & (nbcount(pants, N8) >= 3)
    lab_, n_ = ndi.label(inner, structure=np.ones((3, 3), int))
    if n_:
        sizes = ndi.sum(inner, lab_, range(1, n_ + 1))
        PL[inner] = L_PA2
        PL[np.isin(lab_, np.nonzero(sizes >= 8)[0] + 1)] = L_PA0
    # tiny floating blobs (katana leftovers, specks): dropped
    figm = PL != L_BG
    lab_, n_ = ndi.label(figm, structure=np.ones((3, 3), int))
    if n_ > 1:
        sizes = ndi.sum(figm, lab_, range(1, n_ + 1))
        for k_ in np.nonzero(sizes <= 8)[0] + 1:
            ck = lab_ == k_
            if not (ck & (role == R_TRAIL)).any() and not (ck & (role == R_SKIN)).any():
                PL[ck] = L_BG
    rows = np.arange(H)[:, None]
    for hd in heads:
        face = hd["face"] & sk
        if face.sum() < 10:
            continue
        top = np.nonzero(face)[0].min()
        enc = (role == R_OUT) & (nbcount(face | (role == R_HAIR), N4) >= 3) & dilate(face, 1) & (rows <= top + 4)
        PL[enc] = L_EYE                                 # eyepatch -> eye
        PL[face & (rows >= top + 5) & (cls["L"] >= 0.86)] = L_SK2   # grin -> calm mouth
    for m_ in (role == R_GOLD, role == R_OTHER):
        for y, x in zip(*np.nonzero(m_)):
            c = tuple(int(v) for v in src[y, x])
            if c not in dyn:
                dyn[c] = L_DYN + len(dyn)
            PL[y, x] = dyn[c]
    return PL, {v: k for k, v in dyn.items()}


def denoise_labels(PL):
    """Merge specks (isolated tone pixels: the salt-and-pepper of the 1x shading)
    into the surrounding tone of the same material."""
    H, W = PL.shape
    for labs, base, maxn in TONE_GROUPS:
        for _ in range(2):
            changed = False
            for lab in labs:
                if lab == base:
                    continue
                m = PL == lab
                if not m.any():
                    continue
                lab_, n = ndi.label(m, structure=np.ones((3, 3), int))
                sizes = ndi.sum(m, lab_, range(1, n + 1))
                small = np.isin(lab_, np.nonzero(sizes <= maxn)[0] + 1)
                for y, x in zip(*np.nonzero(small)):
                    cnt = {}
                    for dy, dx in N8:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and PL[ny, nx] in labs and PL[ny, nx] != lab:
                            v = int(PL[ny, nx])
                            cnt[v] = cnt.get(v, 0) + (2 if dy == 0 or dx == 0 else 1)
                    if cnt:
                        PL[y, x] = max(sorted(cnt), key=lambda v: cnt[v])
                        changed = True
            if not changed:
                break
    return PL


def trail_field(tm, src):
    """Haki ramp position t per trail pixel (1x)."""
    st = TRAIL_STYLE
    L = luma(src)
    vals, cnt = np.unique(L[tm], return_counts=True)
    Lb = float(vals[np.argmax(cnt)]) if len(vals) else 1.0
    return np.where(L >= Lb, st["body"] + (L - Lb) / max(1e-3, 1.0 - Lb) * (st["hot"] - st["body"]),
                    L / max(Lb, 1e-3) * st["body"])


def shade_trail2x(out, tm2, t2):
    st = TRAIL_STYLE
    t = t2.copy()
    if st.get("rim") is not None:
        inner = ndi.binary_erosion(tm2, iterations=2)
        rim = tm2 & ~inner & ndi.binary_dilation(inner, iterations=2)
        t = np.where(rim, np.minimum(t, st["rim"]), t)
    out[tm2, :3] = ramp(t[tm2], RAMPS[st["ramp"]])
    out[tm2, 3] = 255


def shade_hair2x(out, L2, geo):
    """Hair drawn at 2x: base red, strands radiating from the parting, a sheen on
    the crown, darker under-layer at the nape / next to the face, dark rim."""
    hm = L2 == L_HAIR
    if not hm.any() or not geo:
        return
    H2, W2 = hm.shape
    yy, xx = np.mgrid[0:H2, 0:W2]
    k = float(SCALE)
    dists = [np.hypot(xx + 0.5 - g["c"][0] * k, yy + 0.5 - g["c"][1] * k) for g in geo]
    owner = np.argmin(np.stack(dists), 0)
    skin2 = np.isin(L2, [L_SK0, L_SK1, L_SK2, L_FEAT, L_EYE])
    rim = hm & ndi.binary_dilation(~hm & ~skin2, iterations=1)
    near_face = hm & ndi.binary_dilation(skin2, iterations=2)
    out[hm] = (*HAIR_T[2], 255)
    for i, g in enumerate(geo):
        sel = hm & (owner == i)
        if not sel.any():
            continue
        R = g["R"] * k
        up, fwd = g["up"], g["fwd"]
        fc = g["fc"] * k
        px, py = xx + 0.5 - fc[0], yy + 0.5 - fc[1]
        a = px * fwd[0] + py * fwd[1]
        b = px * up[0] + py * up[1]
        # parting: top front of the skull
        P = g["c"] * k + up * R * 0.78 + fwd * R * 0.28
        qx, qy = xx + 0.5 - P[0], yy + 0.5 - P[1]
        qa = qx * fwd[0] + qy * fwd[1]
        qb = qx * up[0] + qy * up[1]
        r = np.hypot(qa, qb)
        th = np.arctan2(qa, -qb)                       # 0 = straight down from the parting
        f = (th * 7.0 / np.pi + 0.035 * r) % 1.0
        strand = sel & (f < 0.16) & (r > R * 0.35)
        sheen = sel & (qb < -R * 0.12) & (r > R * 0.28) & (r < R * 0.62) & (b > -R * 0.15) & (f > 0.3)
        under = sel & (b < -HAIR_TIP * k * 0.55)
        out[sheen] = (*HAIR_T[3], 255)
        out[sheen & (f > 0.55) & (f < 0.8) & (r < R * 0.5)] = (*HAIR_T[4], 255)
        out[under] = (*HAIR_T[1], 255)
        out[strand] = (*HAIR_T[1], 255)
        out[strand & under] = (*HAIR_T[0], 255)
    out[near_face] = (*HAIR_T[1], 255)
    out[rim] = (*HAIR_T[0], 255)


def shade_cape2x(out, L2):
    """Cape at 2x: soft vertical folds on the floor-length part (no texture), and a
    1 px rim light where the cape's top or front (screen right) edge meets the
    outline, so the black cape keeps its shape (shoulders, collar, hems)."""
    capem = (L2 >= L_CAPE0) & (L2 <= L_CAPEX)
    if capem.any():
        nc = ~capem
        top = capem & np.roll(nc, 1, 0) & (np.roll(L2, 1, 0) == L_OUT)
        front = capem & np.roll(nc, -1, 1) & (np.roll(L2, -1, 1) == L_OUT)
        rim = top | front
        out[rim & (L2 != L_CAPE0)] = (*CAPE_T[4], 255)
        out[rim & (L2 == L_CAPE0)] = (*CAPE_T[3], 255)
        inner = capem & ~rim & (np.roll(rim, 1, 0) | np.roll(rim, -1, 1)) & np.isin(L2, [L_CAPE2, L_CAPEX])
        out[inner] = (*CAPE_T[3], 255)
    cx = L2 == L_CAPEX
    if not cx.any():
        return
    H2, W2 = cx.shape
    yy, xx = np.mgrid[0:H2, 0:W2]
    ph = np.sin(2 * np.pi * (xx + 0.5) / 9.0 + 0.6 * np.sin((yy + 0.5) / 13.0))
    keep = (out[..., :3] == np.array(CAPE_T[4])).all(-1) | (out[..., :3] == np.array(CAPE_T[3])).all(-1)
    cx &= ~keep
    out[cx] = (*CAPE_T[2], 255)
    out[cx & (ph < -0.5)] = (*CAPE_T[1], 255)
    out[cx & (ph > 0.82)] = (*CAPE_T[3], 255)


def shade_pants2x(out, L2):
    """Pants at 2x: flat crimson, a shadow band along the lower-back edges and a thin
    light on the upper-front edges where they meet the outline (cel shading, no folds)."""
    pm = np.isin(L2, [L_PA1, L_PA2, L_PA3])
    if not pm.any():
        return
    def at(m, dy, dx):
        return np.roll(np.roll(m, -dy, 0), -dx, 1)      # m[y + dy, x + dx]
    base = pm & (L2 == L_PA2)
    shadow = base & ~at(pm, 3, -3) & ~at(L2 == L_SASH0, 3, -3)
    out[shadow] = (*PANTS_T[1], 255)
    edge = np.isin(L2, [L_OUT, L_BG, L_PAOUT])
    light = base & ~shadow & at(edge, -1, 1) & ~at(edge, 1, -1)
    out[light] = (*PANTS_T[3], 255)


def render2x(PL, dyn, tfield, geo, specs, sword_hand, heads, hair_new):
    k = SCALE
    L2 = magnify_labels(PL)
    H2, W2 = L2.shape
    out = np.zeros((H2, W2, 4), np.uint8)
    for lab, rgb in LABEL_RGB.items():
        out[L2 == lab] = (*rgb, 255)
    for lab, rgb in dyn.items():
        out[L2 == lab] = (*rgb, 255)
    tm2 = L2 == L_TRAIL
    if tm2.any():
        shade_trail2x(out, tm2, quant(magnify_field(tfield, PL == L_TRAIL)))
    shade_cape2x(out, L2)
    shade_pants2x(out, L2)
    shade_hair2x(out, L2, geo)
    # ---- Gryphon at 2x
    swm = np.zeros((H2, W2), bool)
    swc = np.zeros((H2, W2, 4), np.uint8)
    bowm = np.zeros((H2, W2), bool)
    for P in specs:
        part, col, x0, y0 = raster_sword(scale_spec(P, k))
        paste_window(swm, swc, part, col, x0, y0)
        paste_window(bowm, np.zeros((H2, W2, 4), np.uint8), part, col, x0, y0, only=[SW_BOW])
    pre = out.copy()
    out[swm] = swc[swm]
    hand_keep = up_nn(sword_hand, k) & (pre[..., 3] > 0) & ~bowm & np.isin(L2, SKIN_LABELS)
    out[hand_keep] = pre[hand_keep]
    if any(P["behind"] for P in specs):
        headm = np.zeros(PL.shape, bool)
        for hd in heads:
            headm |= hd["face"] | hair_new
        headm2 = up_nn(headm, k) & (pre[..., 3] > 0) & (L2 != L_OUT)
        out[headm2] = pre[headm2]
    return out, L2, swm


# ==========================================================================
# v3: S+U "Haki release" pose (bitmaps 441 / 443), drawn from scratch
# ==========================================================================
# 441 and 443 alternate at depth 27 (shapes 442 / 444, 超必杀1 frames 863-888)
# while the Conqueror's Haki dome bursts around him.  Kenpachi's sword-blur
# streaks are gone: Shanks stands planted facing front, chest out, the cape blown
# wide to both sides, hair lifted by the pressure, Gryphon held low in his right
# hand.  The two bitmaps are two flutter phases of the same pose (cape hem and
# hair tips whip between them).  Figure coordinates: 1x px, x from the body's
# centre line (screen right = his left), y from the top of bitmap 441's canvas;
# the shapes place 443's canvas 2.7 px right of 441's.
HAKI_POSE = {441: dict(phase=0.0, dx=0.0), 443: dict(phase=1.0, dx=-2.7)}
HAKI_CX = 22.6                     # body centre line, 441 canvas x
HAKI_DY = -1.0                     # figure y -> canvas y (sandal outline on the last row, like the original)
HAKI_SS = 4                        # supersampling over the 2x grid
HK_RIM = (122, 16, 38)             # crimson rim light from the Haki dome
(P_NONE, P_CAPE, P_LIN, P_PANTS, P_SASH, P_SHIRT, P_SKIN, P_FACE, P_HAIR, P_SANDAL, P_SLEEVE,
 P_HAND) = range(12)


class _Canvas:
    """Label + part canvas at 2x * HAKI_SS, coordinates in 1x figure units."""

    def __init__(self, x0, y0, w, h):
        self.x0, self.y0 = x0, y0
        self.f = SCALE * HAKI_SS
        self.lab = Image.new("L", (int(w * self.f), int(h * self.f)), L_BG)
        self.part = Image.new("L", self.lab.size, P_NONE)
        self.dl, self.dp = ImageDraw.Draw(self.lab), ImageDraw.Draw(self.part)

    def xy(self, pts):
        return [((x - self.x0) * self.f, (y - self.y0) * self.f) for x, y in pts]

    def poly(self, pts, lab, part=None):
        q = self.xy(pts)
        self.dl.polygon(q, fill=lab)
        if part is not None:
            self.dp.polygon(q, fill=part)

    def ellipse(self, cx, cy, rx, ry, lab, part=None):
        q = self.xy([(cx - rx, cy - ry), (cx + rx, cy + ry)])
        self.dl.ellipse(q, fill=lab)
        if part is not None:
            self.dp.ellipse(q, fill=part)

    def capsule(self, p0, p1, r, lab, part=None):
        p0, p1 = np.array(p0, float), np.array(p1, float)
        d = unit(p1 - p0)
        n = np.array([-d[1], d[0]]) * r
        self.poly([p0 + n, p1 + n, p1 - n, p0 - n], lab, part)
        self.ellipse(p0[0], p0[1], r, r, lab, part)
        self.ellipse(p1[0], p1[1], r, r, lab, part)

    def line(self, pts, lab, width=1.0):
        """Thin line, width in 2x px."""
        self.dl.line(self.xy(pts), fill=lab, width=max(1, int(round(width * HAKI_SS))), joint="curve")

    def reduce(self):
        """Majority label per HAKI_SS x HAKI_SS block -> 2x label and part maps."""
        out = []
        for im in (self.lab, self.part):
            a = np.array(im)
            h, w = a.shape[0] // HAKI_SS, a.shape[1] // HAKI_SS
            a = a[:h * HAKI_SS, :w * HAKI_SS].reshape(h, HAKI_SS, w, HAKI_SS)
            best = np.full((h, w), -1)
            lab = np.zeros((h, w), np.int16)
            for v in np.unique(a):
                c = (a == v).sum(axis=(1, 3))
                k = c > best
                best[k] = c[k]
                lab[k] = v
            out.append(lab)
        return out


def _wing(s, ph):
    """Cape wing on the screen-left side (s = -1) or right (s = +1), flutter phase ph in 0..1."""
    def P(x, y):
        return (s * x, y)
    lift = 3.6 * ph
    out_ = 1.6 * ph
    outer = [P(4.6, 15.6), P(9.0, 17.0), P(14.5, 19.6 - lift), P(19.6 + out_ * 0.5, 23.6 - lift),
             P(24.0 + out_, 29.6 - lift * 0.8), P(26.0 + out_, 36.6 - lift * 0.5), P(25.4 + out_ * 0.6, 43.0 - ph)]
    hem = [P(22.6 + out_, 46.8 - 0.6 * ph), P(24.6 - 1.4 * ph, 51.0 + 2.0 * ph), P(20.8, 53.6 - 1.2 * ph),
           P(21.0 - 1.6 * ph, 59.4 - 2.2 * ph), P(17.4 + 0.8 * ph, 56.6 + 1.0 * ph), P(15.6 + ph, 61.6 - 2.4 * ph),
           P(12.6, 58.4 + ph), P(10.2, 61.0)]
    inner = [P(9.4, 50.0), P(9.0, 40.0), P(8.6, 30.0), P(7.6, 21.0)]
    lining = [P(26.0, 43.0)] + hem[:4] + [P(19.0, 49.0 - ph), P(22.8, 41.0)]
    return outer + hem + inner, lining


def _hair(ph, flip=False):
    """Front hair silhouette: parted crown, locks framing the face, tips lifted by the pressure."""
    def side(s, q):
        u = 1.0 - q
        return [(s * 3.4, 3.6), (s * 5.4, 4.6), (s * 6.6, 6.6), (s * (8.4 + 0.5 * u), 7.6 - 1.4 * u),
                (s * 6.9, 9.4), (s * (8.8 + 0.5 * q), 12.0 - 1.2 * q), (s * 6.8, 12.8),
                (s * (8.2 + 0.4 * u), 16.6 - 1.2 * u), (s * 5.8, 15.6), (s * 4.6, 17.8), (s * 3.9, 14.0),
                (s * 3.6, 10.6), (s * 3.0, 8.4)]
    left = side(-1.0, ph)
    right = side(1.0, 1.0 - ph)
    crown = [(-1.6, 3.2), (-0.6, 1.8 + 0.5 * ph), (0.4, 3.0), (1.6, 1.7 + 0.5 * (1 - ph)), (2.4, 3.2)]
    fringe = [(2.4, 7.4), (1.2, 8.6), (0.6, 7.0), (-0.6, 7.2), (-1.8, 9.0), (-2.6, 7.6)]
    return list(reversed(left)) + crown + right + fringe


def draw_haki_pose(bid, a0, rep):
    cfg = HAKI_POSE[bid]
    ph = cfg["phase"]
    cx = HAKI_CX + cfg["dx"]                    # body centre in this bitmap's canvas
    h0, w0 = a0.shape[:2]
    # generous canvas in figure units (x from the centre line, y from the canvas top)
    X0, Y0, X1, Y1 = -30.0, -4.0, 30.0, 66.0
    cv = _Canvas(X0, Y0, X1 - X0, Y1 - Y0)
    # ---- cape: wings behind, lining on the billowing hems
    for s, q in ((-1, ph), (1, 1.0 - ph)):
        wing, lining = _wing(s, q)
        cv.poly(wing, L_CAPE2, P_CAPE)
        cv.poly(lining, L_LIN1, P_LIN)
    # back panel between the wings (behind the legs)
    cv.poly([(-9.4, 50.0), (-7.6, 21.0), (7.6, 21.0), (9.4, 50.0), (8.0, 60.0), (0, 58.5), (-8.0, 60.0)],
            L_CAPE1, P_CAPE)
    # ---- legs and feet
    for s in (-1, 1):
        cv.capsule((s * 5.0, 49.0), (s * 6.3, 61.0), 1.3, L_SK1, P_SKIN)
        cv.capsule((s * 5.5, 50.5), (s * 6.6, 60.5), 0.45, L_SK0)
        cv.ellipse(s * 6.9, 62.2, 2.2, 1.15, L_SK1, P_SKIN)
        cv.poly([(s * 4.4, 62.9), (s * 9.3, 62.9), (s * 9.1, 64.0), (s * 4.6, 64.0)], L_SAN0, P_SANDAL)
        cv.poly([(s * 5.0, 61.1), (s * 8.6, 61.3), (s * 8.4, 62.0), (s * 5.2, 61.9)], L_SAN1, P_SANDAL)
    # ---- 3/4 pants
    pants = [(-5.6, 34.6), (5.6, 34.6), (8.0, 39.6), (8.8, 45.4), (8.4, 49.8), (2.4, 50.0), (1.8, 44.4),
             (0.0, 41.6), (-1.8, 44.4), (-2.4, 50.0), (-8.4, 49.8), (-8.8, 45.4), (-8.0, 39.6)]
    cv.poly(pants, L_PA2, P_PANTS)
    for s in (-1, 1):
        cv.poly([(s * 7.6, 39.8), (s * 8.6, 45.4), (s * 8.3, 49.6), (s * 6.8, 49.6), (s * 7.2, 44.6),
                 (s * 6.6, 40.0)], L_PA1)
        cv.poly([(s * 2.3, 46.0), (s * 2.1, 49.8), (s * 3.4, 49.8), (s * 3.2, 46.0)], L_PA1)
        cv.ellipse(s * 4.7, 41.8, 1.1, 3.0, L_PA3)
        cv.poly([(s * 2.4, 48.6), (s * 8.4, 48.4), (s * 8.4, 50.0), (s * 2.4, 50.0)], L_PA0)
    cv.poly([(-1.2, 35.4), (1.2, 35.4), (0.4, 41.0), (-0.4, 41.0)], L_PA1)
    # ---- torso: open white shirt, bare chest V
    cv.poly([(-5.4, 18.4), (5.4, 18.4), (5.8, 33.6), (-5.8, 33.6)], L_SH2, P_SHIRT)
    for s in (-1, 1):
        cv.poly([(s * 5.4, 18.4), (s * 5.8, 33.6), (s * 4.4, 33.6), (s * 4.3, 22.0)], L_SH1)
        cv.poly([(s * 2.0, 26.0), (s * 1.2, 30.4), (s * 2.4, 33.0), (s * 3.2, 28.0)], L_SH1)
    cv.poly([(-2.9, 17.4), (2.9, 17.4), (2.0, 23.2), (0.0, 30.0), (-2.0, 23.2)], L_SK1, P_SKIN)
    cv.poly([(-2.4, 17.6), (2.4, 17.6), (1.2, 20.6), (-1.2, 20.6)], L_SK2)
    for s in (-1, 1):
        cv.line([(s * 0.5, 22.8), (s * 1.6, 23.3), (s * 2.0, 22.6)], L_SK0, 1.0)
    cv.line([(0.0, 23.6), (0.0, 28.4)], L_SK0, 1.0)
    # sash with the knot at his left hip
    cv.poly([(-6.0, 32.4), (6.0, 32.4), (6.2, 35.2), (-6.2, 35.2)], L_SASH1, P_SASH)
    cv.poly([(-6.2, 34.4), (6.2, 34.4), (6.2, 35.2), (-6.2, 35.2)], L_SASH0)
    cv.poly([(4.0, 34.0), (6.4, 33.6), (7.4, 38.6), (6.2, 39.4), (5.2, 36.0)], L_SASH1, P_SASH)
    cv.poly([(5.8, 36.2), (7.0, 38.4), (6.2, 39.4)], L_SASH0)
    # ---- the cape over both shoulders, front edges down the sides of the torso
    for s in (-1, 1):
        cv.poly([(s * 2.8, 17.6), (s * 6.0, 17.2), (s * 9.4, 19.4), (s * 10.0, 23.4), (s * 9.2, 30.0),
                 (s * 8.8, 34.0), (s * 6.4, 33.2), (s * 5.2, 26.0), (s * 4.6, 20.2)], L_CAPE2, P_CAPE)
        cv.poly([(s * 9.4, 19.6), (s * 10.0, 23.4), (s * 9.2, 30.0), (s * 8.8, 34.0), (s * 8.0, 33.6),
                 (s * 8.6, 24.0)], L_CAPE1)
        cv.poly([(s * 3.2, 17.4), (s * 5.4, 17.0), (s * 7.2, 18.2), (s * 5.4, 18.8)], L_CAPE3)
        # standing collar (its lining shows inside)
        cv.poly([(s * 2.6, 17.8), (s * 3.6, 12.4), (s * 5.8, 13.2), (s * 6.4, 17.6)], L_CAPE2, P_CAPE)
        cv.poly([(s * 3.0, 17.4), (s * 3.8, 13.4), (s * 4.6, 13.8), (s * 4.0, 17.6)], L_LIN1, P_LIN)
    # ---- sword arm (his right, screen left): forearm out of the cape, rolled white sleeve
    cv.capsule((-9.6, 25.0), (-11.4, 30.4), 2.1, L_SH2, P_SLEEVE)
    cv.capsule((-10.6, 26.4), (-12.4, 30.4), 0.75, L_SH1)
    cv.capsule((-10.0, 30.6), (-12.8, 30.6), 0.95, L_SH1)              # rolled cuff
    cv.capsule((-11.6, 31.6), (-12.3, 33.6), 1.3, L_SK1, P_HAND)
    cv.ellipse(-12.6, 35.0, 2.0, 1.8, L_SK1, P_HAND)
    cv.ellipse(-13.4, 35.6, 0.9, 0.9, L_SK0)
    cv.line([(-11.4, 34.2), (-11.6, 35.8)], L_SK0, 1.0)                 # knuckles
    # cape edge back over the upper arm
    cv.poly([(-6.0, 17.2), (-9.4, 19.2), (-11.4, 22.6), (-12.2, 25.8), (-10.8, 26.6), (-9.0, 26.8),
             (-7.8, 26.0), (-7.6, 21.0)], L_CAPE2, P_CAPE)
    cv.poly([(-11.4, 22.6), (-12.2, 25.8), (-10.8, 26.6), (-10.6, 24.6)], L_CAPE1)
    # ---- neck and head
    cv.capsule((0.0, 14.2), (0.0, 18.0), 1.75, L_SK1, P_SKIN)
    cv.poly([(-1.75, 15.6), (1.75, 15.6), (1.6, 16.8), (-1.6, 16.8)], L_SK0)
    face = [(-3.3, 9.0), (-3.2, 12.8), (-2.2, 15.2), (-0.8, 16.2), (0.8, 16.2), (2.2, 15.2), (3.2, 12.8),
            (3.3, 9.0), (2.6, 7.0), (0.0, 6.4), (-2.6, 7.0)]
    cv.poly(face, L_SK1, P_FACE)
    cv.poly([(-1.6, 8.0), (1.6, 8.0), (1.2, 12.8), (0.0, 13.6), (-1.2, 12.8)], L_SK2)
    for s in (-1, 1):
        cv.poly([(s * 3.3, 9.0), (s * 3.2, 12.8), (s * 2.2, 15.2), (s * 1.8, 14.6), (s * 2.6, 12.4)], L_SK0)
        cv.line([(s * 0.5, 10.3), (s * 1.4, 9.6), (s * 2.7, 9.3)], L_FEAT, 1.2)          # frowning brows
        cv.poly([(s * 0.7, 10.8), (s * 2.3, 10.7), (s * 2.1, 11.4), (s * 0.9, 11.4)], L_FEAT)  # eyes
        cv.poly([(s * 1.2, 10.9), (s * 1.8, 10.9), (s * 1.8, 11.3), (s * 1.2, 11.3)], L_EYE)
    cv.line([(0.4, 11.6), (0.5, 12.9), (0.0, 13.2)], L_SK0, 1.0)                          # nose
    cv.ellipse(0.0, 14.5, 1.05, 0.55, L_FEAT)                                               # shouting
    cv.poly([(-0.8, 14.1), (0.8, 14.1), (0.6, 14.4), (-0.6, 14.4)], L_SK2)
    # ---- hair
    cv.poly(_hair(ph), L_HAIR, P_HAIR)
    # ---- reduce to 2x
    L2, part = cv.reduce()
    H2, W2 = L2.shape
    k = cv.f / HAKI_SS                           # 2x px per 1x unit
    yy, xx = np.mgrid[0:H2, 0:W2]
    fx = (xx + 0.5) / k + X0                      # figure coordinates of the 2x pixel centres
    fy = (yy + 0.5) / k + Y0
    out = np.zeros((H2, W2, 4), np.uint8)
    for lab, rgb in LABEL_RGB.items():
        out[L2 == lab] = (*rgb, 255)
    fig = part != P_NONE
    # cape: folds radiating from the shoulders, crimson rim light on the outer edges
    cape = (part == P_CAPE) & np.isin(L2, [L_CAPE1, L_CAPE2])
    for s in (-1, 1):
        sh = np.array([s * 6.5, 18.0])
        th = np.arctan2(fy - sh[1], s * (fx - sh[0]))
        r = np.hypot(fx - sh[0], fy - sh[1])
        f = (th * 9.0 / np.pi + 0.04 * r + 0.3 * ph * s) % 1.0
        side_m = cape & (s * fx > 8.0) & (r > 5.0)
        out[side_m & (f < 0.12)] = (*CAPE_T[0], 255)
        out[side_m & (f > 0.45) & (f < 0.55)] = (*CAPE_T[3], 255)
    edge = fig & ~ndi.binary_erosion(fig, iterations=1)
    out[(part == P_CAPE) & edge & (np.abs(fx) > 9.0) & (fy < 50)] = (*HK_RIM, 255)
    lin = part == P_LIN
    out[lin & (fy > 0) & ~ndi.binary_erosion(lin, iterations=2) & (np.abs(fx) > 9)] = (*LIN_T[0], 255)
    # hair: strands from the parting, sheen on the crown, dark tips, crimson rim
    hm = part == P_HAIR
    th = np.arctan2(fx - 0.3, -(fy - 3.0))
    r = np.hypot(fx - 0.3, fy - 3.0)
    f = (th * 8.0 / np.pi + 0.05 * r) % 1.0
    out[hm & (fy < 7.0) & (r > 1.4) & (r < 4.0) & (f > 0.3)] = (*HAIR_T[3], 255)
    out[hm & (fy < 6.0) & (r > 1.8) & (r < 3.2) & (f > 0.55) & (f < 0.8)] = (*HAIR_T[4], 255)
    out[hm & (np.abs(fx) > 7.0)] = (*HAIR_T[1], 255)
    out[hm & (f < 0.14) & (r > 2.0)] = (*HAIR_T[1], 255)
    out[hm & ndi.binary_dilation(part == P_FACE, iterations=1)] = (*HAIR_T[1], 255)
    out[hm & ~ndi.binary_erosion(hm, iterations=1)] = (*HAIR_T[0], 255)
    # internal lines (1 px) between parts, outer outline (2 px) around the figure
    pr, pd = np.roll(part, -1, 1), np.roll(part, -1, 0)
    line = fig & (((part != pr) & (pr != P_NONE)) | ((part != pd) & (pd != P_NONE)))
    soft = {(P_FACE, P_HAIR), (P_HAIR, P_FACE), (P_SKIN, P_FACE), (P_FACE, P_SKIN), (P_SHIRT, P_SKIN),
            (P_SKIN, P_SHIRT), (P_LIN, P_CAPE), (P_CAPE, P_LIN), (P_SLEEVE, P_HAND), (P_HAND, P_SLEEVE)}
    pair_r = np.array([[(int(a), int(b)) in soft for a, b in zip(r1, r2)] for r1, r2 in zip(part, pr)])
    pair_d = np.array([[(int(a), int(b)) in soft for a, b in zip(r1, r2)] for r1, r2 in zip(part, pd)])
    hard = fig & ((((part != pr) & (pr != P_NONE)) & ~pair_r) | (((part != pd) & (pd != P_NONE)) & ~pair_d))
    out[line & ~hard] = (*SKIN_T[0], 255)
    out[line & ~hard & ((part == P_HAIR) | (pr == P_HAIR) | (pd == P_HAIR))] = (*HAIR_T[0], 255)
    out[line & ~hard & ((part == P_LIN) | (pr == P_LIN) | (pd == P_LIN))] = (*CAPE_T[0], 255)
    out[hard] = (*OUTLINE, 255)
    ring = ndi.binary_dilation(fig, iterations=2) & ~fig
    out[ring] = (*OUTLINE, 255)
    out[ring, 3] = 255
    # ---- Gryphon held low in the right hand (fist over the grip)
    d = unit((-0.36, 0.93))
    G = np.array([-12.6, 35.0]) + d * 2.4
    P = sword_spec(G, G + d * 25.0, 1.0, dict(len=25.0))
    P = dict(P, G=P["G"] - [X0, Y0], T=P["T"] - [X0, Y0], H=P["H"] - [X0, Y0])
    swm = np.zeros((H2, W2), bool)
    swc = np.zeros((H2, W2, 4), np.uint8)
    bowm = np.zeros((H2, W2), bool)
    part_s, col, x0, y0 = raster_sword(scale_spec(P, k))
    paste_window(swm, swc, part_s, col, x0, y0)
    paste_window(bowm, np.zeros((H2, W2, 4), np.uint8), part_s, col, x0, y0, only=[SW_BOW])
    hand = (part == P_HAND) & ~bowm
    pre = out.copy()
    out[swm] = swc[swm]
    out[hand] = pre[hand]
    # ---- crop to this bitmap's canvas (+ padding where the figure needs room)
    al = out[..., 3] > 0
    ys, xs = np.nonzero(al)
    # canvas x of figure coordinate u: u + cx; 2x pixel column j covers figure x X0 + j / k
    bx0 = (xs.min() / k + X0) + cx
    bx1 = ((xs.max() + 1) / k + X0) + cx
    by0 = (ys.min() / k + Y0) + HAKI_DY
    by1 = ((ys.max() + 1) / k + Y0) + HAKI_DY
    pad = [max(0, int(math.ceil(-bx0))), max(0, int(math.ceil(-by0))),
           max(0, int(math.ceil(bx1 - w0))), max(0, int(math.ceil(by1 - h0)))]
    Wc, Hc = (w0 + pad[0] + pad[2]) * SCALE, (h0 + pad[1] + pad[3]) * SCALE
    res = np.zeros((Hc, Wc, 4), np.uint8)
    # canvas 2x pixel (i, j) <-> figure 2x pixel (i + oy, j + ox)
    ox = (-pad[0] - cx - X0) * k
    oy = (-pad[1] - Y0 - HAKI_DY) * k
    oxi, oyi = int(round(ox)), int(round(oy))
    sy0, sx0 = max(0, oyi), max(0, oxi)
    sy1, sx1 = min(H2, oyi + Hc), min(W2, oxi + Wc)
    res[sy0 - oyi:sy1 - oyi, sx0 - oxi:sx1 - oxi] = out[sy0:sy1, sx0:sx1]
    rep.update(kind="character", drawn="haki release pose (procedural)", phase=ph,
               offset_err=round(abs(ox - oxi) + abs(oy - oyi), 2))
    return res, pad


# ==========================================================================
# effect bitmaps
# ==========================================================================
def dust_mask(a):
    rgb = a[..., :3]
    h, s, v = hsv_arrays(rgb)
    return (a[..., 3] > 0) & (h >= 18) & (h <= 60) & (s >= 0.12) & (s <= 0.8) & (v <= 0.85)


def effect_style(labs):
    for lab in EFFECT_STYLE:
        if lab in labs:
            return lab, EFFECT_STYLE[lab]
    return None, DEFAULT_STYLE


def build_cdfs(ids, lab_of):
    vals = {}
    for bid in ids:
        if bid not in EFFECT_ONLY:
            continue
        lab, st = effect_style(lab_of[bid])
        if not st.get("eq"):
            continue
        a = np.array(Image.open(BASE / f"{bid}.png").convert("RGBA"))
        m = a[..., 3] > 0
        if st.get("keep_dust"):
            m &= ~dust_mask(a)
        vals.setdefault(lab, []).append(np.round(luma(a[..., :3])[m] * 1000).astype(int))
    cdfs = {}
    for lab, vs in vals.items():
        v = np.concatenate(vs)
        hist = np.bincount(v, minlength=1001).astype(float)
        c = np.cumsum(hist)
        mid = (c - hist / 2) / c[-1]
        cdfs[lab] = mid
    return cdfs


def process_effect(bid, a, labs, cdfs, rep, scale=1):
    lab, st = effect_style(labs)
    out = a.copy()
    m = a[..., 3] > 0
    dm = np.zeros(m.shape, bool)
    if st.get("keep_dust"):
        dm = dust_mask(a) & m
        rep["dust_kept"] = int(dm.sum())
        m &= ~dm
    L = luma(a[..., :3])
    if st.get("eq") and lab in cdfs:
        tt = cdfs[lab][np.clip(np.round(L * 1000).astype(int), 0, 1000)]
        # keep near-white cores continuous (big flat white areas jump in the CDF)
        tt = np.maximum(tt, L ** st.get("hot_pow", 12))
        rep["mode"] = f"eq({lab})"
    else:
        tt = L ** st.get("gamma", 1.0)
        rep["mode"] = "luma"
    out[m, :3] = ramp(tt[m], RAMPS[st["ramp"]])
    if scale == 1:
        return out
    # 2x: crisp smooth silhouette (label magnification), smooth ramp inside
    # (bilinear t), soft alpha kept soft; brown dust keeps its own colours
    lm = np.zeros(m.shape, np.int16)
    lm[m] = 1
    dyn = {}
    for y, x in zip(*np.nonzero(dm)):
        c = tuple(int(v) for v in a[y, x, :3])
        if c not in dyn:
            dyn[c] = 2 + len(dyn)
        lm[y, x] = dyn[c]
    L2 = magnify_labels(lm)
    o2 = np.zeros(L2.shape + (4,), np.uint8)
    e2 = L2 == 1
    o2[e2, :3] = ramp(quant(magnify_field(tt, m))[e2], RAMPS[st["ramp"]])
    al = a[..., 3]
    if ((al > 0) & (al < 255)).any():
        a2 = np.clip(np.round(magnify_field(al.astype(float), al > 0)), 1, 255).astype(np.uint8)
        o2[e2, 3] = a2[e2]
    else:
        o2[e2, 3] = 255
    for c, v in dyn.items():
        o2[L2 == v] = (*c, 255)
    return o2


# ==========================================================================
# main
# ==========================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ids", help="comma separated bitmap ids (test run: no report / sheet)")
    ap.add_argument("--out", help="output directory (default: sprites/ next to this script)")
    args = ap.parse_args()
    mp = json.loads((ROOT / "label_map.json").read_text(encoding="utf-8"))
    labels = mp["labels"]
    ids = sorted(int(i) for i in mp["all_bitmaps"])
    lab_of = {i: [l for l, d in labels.items() if i in d["bitmaps"]] for i in ids}
    out_dir = Path(args.out) if args.out else OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    todo = sorted(int(i) for i in args.ids.split(",")) if args.ids else ids
    cdfs = build_cdfs(ids, lab_of)
    report, pads = {}, {}
    for bid in todo:
        a0 = np.array(Image.open(BASE / f"{bid}.png").convert("RGBA"))
        rep = dict(labels=lab_of[bid])
        scale = 1 if bid in KEEP_1X else SCALE
        if bid in HAKI_POSE:
            out, pad = draw_haki_pose(bid, a0, rep)
        elif bid in EFFECT_ONLY:
            out = process_effect(bid, a0, lab_of[bid], cdfs, rep, scale)
            rep["kind"] = "effect"
            pad = [0, 0, 0, 0]
        else:
            out, pad = process_character(bid, a0, rep, lab_of)
        h0, w0 = a0.shape[:2]
        exp = ((w0 + pad[0] + pad[2]) * scale, (h0 + pad[1] + pad[3]) * scale)
        if (out.shape[1], out.shape[0]) != exp:
            raise SystemExit(f"{bid}: {out.shape[1]}x{out.shape[0]}, expected {exp[0]}x{exp[1]}")
        rep["scale"] = scale
        if any(pad):
            pads[str(bid)] = pad
        Image.fromarray(out, "RGBA").save(out_dir / f"{bid}.png")
        report[str(bid)] = rep
    if args.ids:
        (out_dir / "sprites_pad.json").write_text(json.dumps(pads, indent=1), encoding="utf-8")
        (out_dir / "sprites_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("test run:", len(todo), "ids ->", out_dir)
        return
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    PADS.write_text(json.dumps(pads, indent=1), encoding="utf-8")
    make_sheet(ids, labels, lab_of, report, pads=pads, out_dir=out_dir)
    kinds = {}
    for r_ in report.values():
        kinds[r_["kind"]] = kinds.get(r_["kind"], 0) + 1
    print(kinds, "padded:", len(pads))


# ==========================================================================
# review sheet
# ==========================================================================
def make_sheet(ids, labels, lab_of, report=None, path=SHEET, zoom=2, only=None,
               width=3000, out_dir=None, pads=None):
    """Review sheet: original | new by label.  zoom is per sprite pixel (2x sprites:
    zoom 2 = 4 screen px per original pixel; the original is shown at the same size)."""
    out_dir = out_dir or OUT
    if pads is None:
        pads = json.loads(PADS.read_text()) if PADS.exists() else {}
    try:
        font = ImageFont.truetype(str(FONT), 13)
        hfont = ImageFont.truetype(str(FONT), 18)
    except OSError:
        font = hfont = ImageFont.load_default()
    seen = set()
    blocks = []
    for lab, d in labels.items():
        row = [i for i in d["bitmaps"] if i in ids and i not in seen and (only is None or i in only)]
        if not row:
            continue
        seen.update(row)
        blocks.append((lab, row))
    BG = (120, 138, 122, 255)
    tiles = []
    for lab, row in blocks:
        items = []
        for i in row:
            o0 = Image.open(BASE / f"{i}.png").convert("RGBA")
            n = Image.open(out_dir / f"{i}.png").convert("RGBA")
            pl, pt, pr, _ = pads.get(str(i), [0, 0, 0, 0])
            k = max(1, round(n.width / (o0.width + pl + pr)))
            o = Image.new("RGBA", n.size, (0, 0, 0, 0))
            o.paste(o0.resize((o0.width * k, o0.height * k), Image.NEAREST), (pl * k, pt * k))
            bb = o.getbbox() or (0, 0, 1, 1)
            bb2 = n.getbbox() or bb
            bb = (max(0, min(bb[0], bb2[0]) - 2), max(0, min(bb[1], bb2[1]) - 2),
                  min(o.width, max(bb[2], bb2[2]) + 2), min(o.height, max(bb[3], bb2[3]) + 2))
            z = zoom if (bb[2] - bb[0]) * zoom <= 1100 else max(1, 1100 // (bb[2] - bb[0]))
            pair = []
            for im in (o, n):
                c = im.crop(bb)
                c = c.resize((c.width * z, c.height * z), Image.NEAREST)
                bg = Image.new("RGBA", c.size, BG)
                bg.alpha_composite(c)
                pair.append(bg)
            pw = max(pair[0].width * 2 + 6, 150)
            ph = pair[0].height + 18
            tile = Image.new("RGBA", (pw, ph), (40, 44, 48, 255))
            tile.paste(pair[0], (0, 18))
            tile.paste(pair[1], (pair[0].width + 6, 18))
            kind = report[str(i)]["kind"] if report else ""
            extra = [LABEL_EN.get(x, x) for x in lab_of[i] if x != lab]
            padtxt = f" pad{pads[str(i)]}" if str(i) in pads else ""
            cap = f"{i} {o0.width}x{o0.height} {kind}{padtxt}" + (f" +{','.join(extra)}" if extra else "")
            ImageDraw.Draw(tile).text((2, 1), cap, fill=(255, 230, 90, 255), font=font)
            items.append(tile)
        tiles.append((lab, items))
    x = y = rowh = 0
    places = []
    for lab, items in tiles:
        if places:
            y += rowh + 10
        places.append(("hdr", lab, 0, y))
        y += 26
        x, rowh = 0, 0
        for tile in items:
            if x + tile.width > width and x:
                x = 0
                y += rowh + 6
                rowh = 0
            places.append(("img", tile, x, y))
            x += tile.width + 10
            rowh = max(rowh, tile.height)
    sheet = Image.new("RGBA", (width, y + rowh + 10), (24, 26, 30, 255))
    dr = ImageDraw.Draw(sheet)
    for kind, obj, px, py in places:
        if kind == "hdr":
            dr.text((4, py + 2), f"== {LABEL_EN.get(obj, obj)} ==", fill=(140, 220, 255, 255), font=hfont)
        else:
            sheet.paste(obj, (px, py))
    sheet.convert("RGB").save(path, optimize=True)
    return path


if __name__ == "__main__":
    main()
