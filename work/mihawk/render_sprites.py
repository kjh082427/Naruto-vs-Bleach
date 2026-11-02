#!/usr/bin/env python3
"""Mihawk reskin of the Bankai-Ichigo bitmaps of game/fighter/yihu.swf.

Run (from anywhere):
    tools/venv/bin/python work/mihawk/render_sprites.py

Inputs  (relative to this file's directory, work/mihawk/):
  base/img/<id>.png        original bitmaps exported by FFDec
  bankai_map.json          labels -> bitmap ids, all_bitmaps
Outputs:
  sprites/<id>.png         one per id in all_bitmaps, same pixel size, RGBA
  sprites_purple/<id>.png  跳招2 bitmaps (720..734) with a violet trail instead of blue
  sprites_sheet.png        review sheet: original | new, grouped by label, 3x NN zoom
  sprites_report.json      classification and per-head geometry (for debugging)
  sprites_pad.json         {id: [left, top, right, bottom]} canvas padding (content keeps its place)
  si_preview.png           超必杀 (S+I) sequence: new vs plain reskin, waves, in-context frames

Deterministic: no randomness; ids processed in sorted order.

Character bitmaps (contain Ichigo)
  * orange/yellow hair -> black hair (shading kept as dark greys), the hair
    above the brim line is removed and replaced by Mihawk's hat;
  * hat = dark-wine crown with a pinched top, thin dark-red band, wide
    up-curled brim, small pale plume on the back side.  It is rasterised at 1x
    from analytic shapes in head-local coordinates (hard edges, 1 px outline),
    so it works for every head orientation and matches the sprite's detail;
  * the hat is shrunk on a side if it would leave the bitmap (no clipping);
  * eye whites -> yellow ("hawk eyes"), moustache + goatee as dark pixels;
  * Hollow-mask pixels on the face (超必杀) -> bare skin;
  * Ichigo's saturated-orange skin shading -> a warmer tan (no orange left).
Effect pixels
  * gradient-mapped by luminance onto a violet or a blue ramp (alpha kept);
  * "combined" bitmaps (character + Getsuga trail in one bitmap): only the
    trail palette is recoloured, the character gets the reskin.
超必杀 (S+I) extras (SI_FX, SI_WAVES; only these 13 bitmaps differ from the plain reskin)
  * windup 1012-1018 / charge 1020-1024: Yoru grows (k 1.0 -> 1.42) and glows
    (black + cyan edge -> blue -> white-hot core, cyan -> deep-blue aura rings),
    yellow 4-point eye glint pulsing 1 -> 2 -> 3 -> 1 (peak on 1022, + tip star);
  * slash 1028 1040 1043: Getsuga trail restyled as a bright afterglow (white-hot
    leading edge -> cyan -> deep blue, soft halo), glowing blade; 1045 faint glow;
  * wave 1032 / 1035: redrawn from scratch (figure removed): thick crescent, white-hot
    leading core, cyan -> blue fibrous bands, broken energy rims, glow halo, sparks,
    shards, speed lines; padded [0, 4, 0, 4] so tools/mihawk.py replaces the cropped
    shape rects 1033 / 1036 by full-bitmap rects (crescent stays in place).
Glow pixels use partial alpha.  Everything else is copied unchanged.
"""
from __future__ import annotations

import json
import math
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "base" / "img"
OUT = ROOT / "sprites"
OUT_PURPLE = ROOT / "sprites_purple"
SHEET = ROOT / "sprites_sheet.png"
REPORT = ROOT / "sprites_report.json"
PADS = ROOT / "sprites_pad.json"
FONT = ROOT.parent.parent / "tools" / "fonts" / "NanumGothic-Bold.ttf"

# --------------------------------------------------------------------------
# label groups
# --------------------------------------------------------------------------
VIOLET_LABELS = ["砍1", "砍2", "砍3", "砍技1", "砍技2", "跳砍", "招1", "招12", "招换"]
BLUE_LABELS = ["招2", "招3", "跳招", "跳招2", "必杀", "上必杀", "超必杀"]
SKIP_LABELS = ["万解"]          # unused animation: ignored for group decisions
PURPLE_COPY_IDS = [720, 722, 724, 726, 730, 732, 734]
LABEL_EN = {
    "站立": "stand", "走": "walk", "瞬步": "dash", "跳": "jump", "落": "fall",
    "跳2": "jump2", "落2": "fall2", "落地": "land", "跳砍": "air J", "跳招": "air U",
    "跳招2": "air U2", "砍1": "J1", "砍2": "J2", "砍3": "J3", "砍技1": "S+J",
    "砍技2": "W+J", "招1": "U1", "招12": "U1-2", "招2": "U2", "招3": "U3",
    "必杀": "ult I", "上必杀": "ult W+I", "超必杀": "ult S+I", "招换": "assist",
    "防御": "guard", "防御2": "guard2", "防住": "guard hit", "被打": "hurt",
    "击飞": "knock-up", "击落地": "knock-down", "起身": "get up", "开场": "intro",
    "胜利": "win", "失败": "lose", "万解": "bankai(unused)",
}

# Bitmaps that contain no character at all (checked on contact sheets).
EFFECT_ONLY = {624, 626, 628, 630,                      # 开场 beams
               765, 767, 771, 773, 775, 777, 779,       # 砍3/招3 slash sparks
               798, 802, 806, 810, 814, 816,            # 砍技1 flame pillar
               823, 825, 827,                           # 砍技2 wave
               868, 871, 875, 879}                      # 招2 black streaks

# Getsuga trail palette used inside combined (character + trail) bitmaps.
TRAIL_COLORS = [(18, 13, 38), (63, 46, 129), (89, 64, 191),
                (0, 0, 24), (66, 49, 99), (99, 74, 115)]

# Bitmaps whose pixels were resampled (hundreds of colours, ~0.8x head scale).
RESAMPLED_SMALL = {652, 654, 656, 658, 660, 662, 664, 666, 783}
# Bitmaps showing the Hollow mask on the face.
MASK_IDS = {1012, 1014, 1016, 1018, 1020, 1022, 1024, 1028, 1032, 1035,
            1040, 1043, 1045, 1047}
# ... of which the full skull mask (front view) gets a painted face
MASK_FULL = {1032, 1035}
# front-facing Mihawk face painted over the full mask (below the brim)
#  L skin  s shade  D dark (brow/beard)  Y yellow eye  . keep
FACE_FRONT = [
    "sDYLLLYDs",
    "sLLLsLLLs",
    "sLLLLLLLs",
    "sLDDLDDLs",
    ".sLLDLLs.",
    "..sLDLs..",
    "...sDs...",
]
# 上必杀 afterimage clones: head rotation is derived from the hand direction.
CLONE_IDS = set(range(945, 995))

# --------------------------------------------------------------------------
# colours
# --------------------------------------------------------------------------
HAT_OUT = (14, 8, 12)
HAT_DARK = (34, 16, 26)
HAT_MID = (54, 25, 40)
HAT_HI = (84, 40, 60)
HAT_BAND = (136, 18, 26)
HAT_BAND_HI = (172, 32, 38)
FEATHER_OUT = (98, 122, 110)
FEATHER_MID = (178, 206, 190)
FEATHER_HI = (232, 244, 236)
EYE_YELLOW = (248, 208, 48)
BEARD = (34, 20, 20)
# Ichigo's skin shading is pure orange; Mihawk gets a warmer tan.
SKIN_RETONE = {(224, 136, 0): (208, 140, 84), (231, 140, 0): (214, 144, 87),
               (136, 80, 0): (118, 70, 42), (140, 82, 0): (121, 72, 43)}

# gradient ramps: (t, rgb); t = luma ** GAMMA
VIOLET_RAMP = [(0.00, (26, 6, 60)), (0.24, (75, 26, 158)), (0.50, (138, 60, 255)),
               (0.78, (204, 176, 255)), (1.00, (248, 242, 255))]
BLUE_RAMP = [(0.00, (6, 22, 84)), (0.24, (30, 91, 255)), (0.50, (79, 195, 255)),
             (0.78, (189, 235, 255)), (1.00, (255, 255, 255))]
GAMMA_TRAIL = 0.5    # near-black Getsuga trails inside combined bitmaps: lift darks
GAMMA_EFFECT = 1.0   # effect-only bitmaps (already lit): plain luminance map

# --------------------------------------------------------------------------
# per-head overrides, keyed (id, head_index)
#   angle : hat "up" rotated clockwise from screen-up, degrees (default 0)
#   facing: +1 face points to the local right of "up", -1 to the left
#   dv/du : nudge the brim origin along up / forward (px)
#   scale : hat scale
# --------------------------------------------------------------------------
OVERRIDES: dict = {
    # 击飞 knock-up: lying horizontally, head on the left
    (1109, 0): dict(angle=-90, facing=1),
    (1112, 0): dict(angle=-90, facing=1),
    (1114, 0): dict(angle=-90, facing=-1),
    (1116, 0): dict(angle=-90, facing=1),
    (1118, 0): dict(angle=-90, facing=1),
    # 击落地 knock-down
    (1121, 0): dict(angle=-135),
    (1123, 0): dict(angle=-90),
    (1125, 0): dict(angle=-90),
    # 起身 get-up roll
    (1133, 0): dict(angle=180),
    (1135, 0): dict(angle=-90),
    (1139, 0): dict(angle=90),
    (1141, 0): dict(angle=180),
}

# ==========================================================================
# small numpy image helpers (no scipy available)
# ==========================================================================
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def shift(m, dy, dx, fill=False):
    h, w = m.shape
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


def nbcount(m, nb=N8):
    c = np.zeros(m.shape, int)
    for dy, dx in nb:
        c += shift(m, dy, dx)
    return c


def label(m):
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
            for dy, dx in N8:
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


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


# ==========================================================================
# pixel classification
# ==========================================================================
def classify(a, resampled=False):
    rgb = a[..., :3]
    op = a[..., 3] > 0
    h, s, v = hsv_arrays(rgb)
    skin_shade = op & (color_eq(rgb, (224, 136, 0), 8) | color_eq(rgb, (231, 140, 0), 8))
    skin_dark = op & (color_eq(rgb, (136, 80, 0), 8) | color_eq(rgb, (140, 82, 0), 8))
    lining = op & (color_eq(rgb, (176, 16, 16), 8) | color_eq(rgb, (181, 16, 16), 8))
    skin_light = op & (h >= 18) & (h <= 52) & (s >= 0.18) & (s <= 0.56) & (v >= 0.80)
    core = op & (h >= 18) & (h <= 66) & (s >= 0.66) & (v >= 0.80) & ~skin_shade
    smin, vmin = (0.40, 0.14) if resampled else (0.58, 0.28)
    hairish = (op & (h <= 70) & (s >= smin) & (v >= vmin)
               & ~skin_shade & ~skin_dark & ~lining & ~skin_light)
    return dict(op=op, core=core, hairish=hairish, skin_light=skin_light,
                skin_shade=skin_shade, skin_dark=skin_dark, h=h, s=s, v=v)


# ==========================================================================
# head analysis
# ==========================================================================
def find_heads(a, cls, resampled=False):
    core = cls["core"]
    lab, n = label(dilate(core, 2))
    heads = []
    skin = cls["skin_light"] | cls["skin_shade"] | cls["skin_dark"]
    for k in range(1, n + 1):
        ck = (lab == k) & core
        if ck.sum() < 20:
            continue
        hair = cls["hairish"] & dilate(ck, 3 if resampled else 2) | ck
        hair |= cls["hairish"] & dilate(hair, 1)
        near = dilate(hair, 4) & skin
        sl, sn = label(near)
        face = np.zeros_like(near)
        touch = dilate(hair, 1)
        for j in range(1, sn + 1):
            cj = sl == j
            if (cj & touch).any():
                face |= cj
        heads.append(dict(hair=hair, core=ck, face=face))
    heads.sort(key=lambda d: (round(np.nonzero(d["core"])[1].mean()),
                              round(np.nonzero(d["core"])[0].mean())))
    return heads


def body_angle(cls, head, hc):
    """Clockwise-from-up angle of the vector body-centroid -> head."""
    op = cls["op"]
    H, W = op.shape
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx + 0.5 - hc[0], yy + 0.5 - hc[1])
    body = op & ~dilate(head, 1) & (dist < 26)
    if body.sum() <= 10:
        return 0.0
    w = 1.0 / (1.0 + dist[body] / 10.0)
    by, bx = np.nonzero(body)
    bc = np.array([(bx * w).sum() / w.sum() + 0.5, (by * w).sum() / w.sum() + 0.5])
    up = hc - bc
    return math.degrees(math.atan2(up[0], -up[1]))


def clone_orientation(cls, heads, idx, hc, raw):
    """上必杀 clones are rotated copies of a lunge pose whose hands sit
    ~114 deg clockwise from the head's up vector (mirrored: counter-clockwise).
    Pick the hypothesis that agrees best with the body->head direction."""
    H, W = cls["op"].shape
    allhead = np.zeros((H, W), bool)
    for hd in heads:
        allhead |= dilate(hd["hair"] | hd["face"], 1)
    sk = (cls["skin_shade"] | cls["skin_dark"] | cls["skin_light"]) & ~allhead
    yy, xx = np.mgrid[0:H, 0:W]
    cy, cx = np.nonzero(heads[idx]["core"])
    c = np.array([cx.mean(), cy.mean()])
    m = sk & (np.hypot(xx - c[0], yy - c[1]) < 20)
    lab, n = label(m)
    best = None
    for j in range(1, n + 1):
        cj = lab == j
        if cj.sum() < 3:
            continue
        jy, jx = np.nonzero(cj)
        d = math.hypot(jx.mean() - c[0], jy.mean() - c[1])
        if best is None or d < best[0]:
            best = (d, jx.mean() - c[0], jy.mean() - c[1])
    if best is None:
        return 0.0, 1, None
    th = math.degrees(math.atan2(best[2], best[1]))      # image angle of hands
    cands = [(wrap180(th - 114 + 90), 1), (wrap180(th + 114 + 90), -1)]
    ang, facing = min(cands, key=lambda c_: abs(wrap180(c_[0] - raw)))
    return round(ang / 15.0) * 15.0, facing, th


def head_geometry(a, cls, heads, idx, bid):
    hd = heads[idx]
    hair, face, core = hd["hair"], hd["face"], hd["core"]
    head = hair | face
    ys, xs = np.nonzero(head)
    hc = np.array([xs.mean() + 0.5, ys.mean() + 0.5])
    raw = body_angle(cls, head, hc)
    ov = OVERRIDES.get((bid, idx), {})
    hand = None
    facing = None
    if "angle" in ov:
        ang = float(ov["angle"])
    elif bid in CLONE_IDS:
        ang, facing, hand = clone_orientation(cls, heads, idx, hc, raw)
    else:
        ang = 0.0
    th = math.radians(ang)
    U = np.array([math.sin(th), -math.cos(th)])       # local up (image coords)
    F0 = np.array([-U[1], U[0]])                     # local right
    scale = ov.get("scale", 0.8 if bid in RESAMPLED_SMALL else 1.0)

    def local(mask, F):
        yy_, xx_ = np.nonzero(mask)
        d = np.stack([xx_ + 0.5 - hc[0], yy_ + 0.5 - hc[1]], 1)
        return d @ F, d @ U

    # facing from where the face skin sits relative to the hair core
    fl = face & cls["skin_light"]
    du = 0.0
    if fl.sum() >= 3:
        fu, _ = local(fl, F0)
        cu, _ = local(core, F0)
        du = float(fu.mean() - cu.mean())
    if facing is None:
        if ang == 0.0:
            facing = -1 if du < -2.0 else 1
        else:
            facing = -1 if du < -0.5 else 1
    facing = ov.get("facing", facing)
    F = F0 * facing

    cu, cv = local(core, F)
    hu, hv = local(hair, F)
    # brim centre line: 2.7 px below the hair-core centroid (calibrated on
    # upright frames: puts the brim on the forehead, brows + eyes visible)
    v_brim = float(cv.mean()) - 2.7 * scale
    # eyes (white next to face skin, near the top of the face) must stay visible
    rgb = a[..., :3].astype(int)
    white = (rgb.min(-1) >= 215) & cls["op"]
    eyes = white & dilate((cls["skin_light"] | cls["skin_shade"]) & face, 1)
    eye_v = None
    if eyes.any():
        _, ev = local(eyes, F)
        ev = ev[(ev < v_brim + 1.0) & (ev > v_brim - 4.5 * scale)]
        if len(ev):
            eye_v = float(ev.max())
            v_brim = max(v_brim, eye_v + 2.6 * scale)
    # crown centre across the head: middle of the hair near/above the brim
    sel = hv >= v_brim - 2
    if sel.sum() >= 4:
        u_c = 0.5 * (np.percentile(hu[sel], 8) + np.percentile(hu[sel], 92))
    else:
        u_c = 0.5 * (hu.min() + hu.max())
    u_c += 0.5 * scale
    v_brim += ov.get("dv", 0.0)
    u_c += ov.get("du", 0.0)
    origin = hc + F * u_c + U * v_brim
    if ang % 90 == 0:      # axis aligned: snap the origin to a pixel centre
        origin = np.floor(origin) + 0.5
    return dict(hc=hc, U=U, F=F, origin=origin, angle=ang, raw_angle=raw,
                facing=facing, scale=scale, face_du=du, eye_v=eye_v,
                hand_angle=hand)


# ==========================================================================
# hat
# ==========================================================================
P_NONE, P_BRIM_TOP, P_BRIM_UNDER, P_CROWN, P_BAND, P_FEATHER = range(6)
# plume = union of discs (u, v, r) relative to the crown centre, in px at scale 1
PLUME = [(-4.4, 4.4, 1.8), (-5.8, 5.9, 1.9), (-4.6, 7.2, 1.5), (-7.0, 7.4, 1.4),
         (-6.6, 3.6, 1.2)]


def default_hat(scale):
    s = scale
    return dict(s=s, Af=12.0 * s, Ab=10.8 * s, ct=6.3 * s, feather=True)


def hat_parts(u, v, P):
    """Vectorised part classification in head-local coords (u fwd, v up)."""
    s = P["s"]
    part = np.zeros(u.shape, np.int8)
    # --- brim: from -Ab (back) to +Af (front), centred at ub, tips curl up
    ub = 0.6 * s
    Af, Ab = P["Af"], P["Ab"]
    q = np.where(u >= ub, (u - ub) / max(Af - ub, 1e-6), (ub - u) / max(ub + Ab, 1e-6))
    inb = q <= 1.0
    qc = np.clip(q, 0, 1)
    cv = 1.9 * s * qc ** 3
    ht = 1.15 * s * np.sqrt(1 - qc ** 2) + 0.45
    brim = inb & (np.abs(v - cv) <= ht)
    brim_top = brim & (v - cv >= -0.25)
    # --- crown (pinched top, rounded corners)
    uc = -0.3 * s
    ct = P["ct"]
    cw0, cw1 = 5.3 * s, 4.3 * s
    k = np.clip(v / ct, 0, 1)
    hw = cw0 * (1 - k) + cw1 * k
    du = np.abs(u - uc)
    # rounded top corners + a 1 px crease in the middle of the top
    top = (ct - 1.0 * s * np.maximum(0, (du - (cw1 - 1.5 * s)) / (1.5 * s)) ** 2
           - 0.4 * s * np.exp(-(du / (0.75 * s)) ** 2))
    crown = (v >= 0) & (du <= hw) & (v <= top)
    band = crown & (v >= 0.5 * s) & (v <= 1.5 * s)
    # --- plume on the back of the crown
    feather = np.zeros(u.shape, bool)
    if P["feather"]:
        for fu, fv, r in PLUME:
            feather |= (u - (uc + fu * s)) ** 2 + (v - fv * s) ** 2 <= (r * s) ** 2
        # in front of the back edge of the crown, never over brim/band
        feather &= ~brim & (v >= 1.6 * s) & (~crown | (u < uc - 3.2 * s))
    part[brim & ~brim_top] = P_BRIM_UNDER
    part[brim_top] = P_BRIM_TOP
    part[crown] = P_CROWN
    part[crown & (v < 0.5 * s)] = P_BRIM_TOP
    part[band] = P_BAND
    part[feather] = P_FEATHER
    return part


def rasterize_hat(H, W, geo, P, margin=24):
    """Rasterise on a canvas padded by `margin` (to detect clipping)."""
    s = P["s"]
    ox, oy = geo["origin"]
    U, F = geo["U"], geo["F"]
    R = int(17 * s) + 3
    x0, x1 = int(ox) - R, int(ox) + R + 1
    y0, y1 = int(oy) - R, int(oy) + R + 1
    yy, xx = np.mgrid[y0:y1, x0:x1]
    dx, dy = xx + 0.5 - ox, yy + 0.5 - oy
    u = dx * F[0] + dy * F[1]
    v = dx * U[0] + dy * U[1]
    part = hat_parts(u, v, P)
    return part, u, v, (x0, y0)


def fit_hat(H, W, geo):
    """Shrink brim / crown / drop plume until no hat pixel leaves the bitmap."""
    P = default_hat(geo["scale"])
    s = P["s"]
    for _ in range(40):
        part, u, v, (x0, y0) = rasterize_hat(H, W, geo, P)
        ys, xs = np.nonzero(part)
        gx, gy = xs + x0, ys + y0
        outside = (gx < 0) | (gx >= W) | (gy < 0) | (gy >= H)
        if not outside.any():
            return P, part, u, v, (x0, y0)
        po = part[ys[outside], xs[outside]]
        uo = u[ys[outside], xs[outside]]
        changed = False
        if (po == P_FEATHER).any() and P["feather"]:
            P["feather"] = False
            changed = True
        brim_o = (po == P_BRIM_TOP) | (po == P_BRIM_UNDER)
        if (brim_o & (uo > 0)).any() and P["Af"] > 6.5 * s:
            P["Af"] -= 1.0
            changed = True
        if (brim_o & (uo <= 0)).any() and P["Ab"] > 6.5 * s:
            P["Ab"] -= 1.0
            changed = True
        if ((po == P_CROWN) | (po == P_BAND)).any() and P["ct"] > 4.6 * s:
            P["ct"] -= 0.5
            changed = True
        if not changed:
            break
    return P, part, u, v, (x0, y0)


def render_hat(H, W, geo):
    """Return (mask, rgba) of the hat in image space, plus the fitted params."""
    P, part, u, v, (x0, y0) = fit_hat(H, W, geo)
    s = P["s"]
    full = np.zeros((H, W), np.int8)
    lu = np.zeros((H, W))
    lv = np.zeros((H, W))
    ph, pw = part.shape
    gy0, gx0 = max(0, y0), max(0, x0)
    gy1, gx1 = min(H, y0 + ph), min(W, x0 + pw)
    if gy1 > gy0 and gx1 > gx0:
        sl = (slice(gy0 - y0, gy1 - y0), slice(gx0 - x0, gx1 - x0))
        full[gy0:gy1, gx0:gx1] = part[sl]
        lu[gy0:gy1, gx0:gx1] = u[sl]
        lv[gy0:gy1, gx0:gx1] = v[sl]
    hatm = full > 0
    feather = full == P_FEATHER
    solid = hatm & ~feather
    edge = solid & (nbcount(solid, N4) < 4)
    fedge = feather & (nbcount(feather, N4) < 4) & (nbcount(solid, N4) == 0)
    fedge |= feather & (nbcount(hatm, N4) < 4)
    col = np.zeros((H, W, 4), np.uint8)
    uc = -0.3 * s
    for y, x in zip(*np.nonzero(hatm)):
        p = full[y, x]
        uu, vv = lu[y, x], lv[y, x]
        if p == P_FEATHER:
            if fedge[y, x]:
                c = FEATHER_OUT
            elif (vv - 5.6 * s) + 0.7 * (uu - uc + 5.0 * s) > -0.8 * s:
                c = FEATHER_HI
            else:
                c = FEATHER_MID
        elif edge[y, x]:
            c = HAT_OUT
        elif p == P_BAND:
            c = HAT_BAND_HI if uu > uc + 1.5 * s else HAT_BAND
        elif p == P_CROWN:
            if uu > uc + 1.2 * s and vv > 2.4 * s:
                c = HAT_HI
            elif uu < uc - 2.4 * s:
                c = HAT_DARK
            else:
                c = HAT_MID
        elif p == P_BRIM_TOP:
            c = HAT_HI if uu > 3.0 * s else HAT_MID
        else:
            c = HAT_DARK
        col[y, x, :3] = c
        col[y, x, 3] = 255
    return hatm, col, P



# ==========================================================================
# Yoru (黒刀 夜) - replaces Tensa Zangetsu in every character pose
# ==========================================================================
# Per-pose annotation, in ORIGINAL bitmap pixel coordinates:
#   id: (hand, tip[, opts])   or   id: None (sword hidden in that pose)
#   hand = index of the non-face skin blob (see hand_blobs(), sorted by x then y)
#          or an explicit (x, y) grip point
#   tip  = a point the blade points at (usually the old katana tip)
#   opts: len    blade length in px at scale 1 (default 38 = full Yoru;
#                 shorter for foreshortened poses)
#         behind sword passes behind the head (head + hat drawn over it)
#         edge   +1/-1 flips the cutting-edge side
#         fixed  do not snap the direction to the old katana
# Bitmaps whose character content is pixel-identical to an annotated one
# (same pose, different placement) reuse its annotation, translated.
# 上必杀 clones (CLONE_IDS) are derived automatically (clone_swords()).
# Grounded poses are aimed so the tip ends at about foot level (no blade
# sinking below the floor line).
WALK = (0, (2, 27))
LOW = dict(len=22)
SWORDS = {
    642: (0, (55, 51)), 644: (0, (56, 51)), 646: (0, (56, 51)), 648: (0, (56, 51)),
    652: WALK, 654: WALK, 656: WALK, 658: WALK, 660: WALK, 662: WALK, 664: WALK, 666: WALK,
    671: (0, (56, 50)), 677: (0, (56, 50)),
    679: (1, (56, 96), LOW), 681: (1, (57, 77), LOW), 684: (1, (58, 62), LOW),
    686: (1, (56, 40), LOW), 688: (1, (54, 61), LOW), 690: (1, (55, 78), LOW),
    693: (1, (56, 95), LOW), 695: (1, (58, 98), dict(len=22, fixed=True)),
    700: (0, (20, 53), dict(behind=True)), 702: (0, (84, 40)), 705: (0, (75, 77)),
    707: (0, (2, 62)), 709: (0, (2, 67)), 711: (0, (30, 95)),
    713: ((78, 12), (50, 3), dict(behind=True)), 715: ((78, 12), (50, 3), dict(behind=True)),
    720: (1, (55, 78), dict(behind=True)), 722: (1, (57, 78), dict(behind=True)),
    724: (1, (92, 72)), 726: (1, (120, 92)), 730: (0, (12, 83)), 732: (0, (20, 83)),
    734: (0, (2, 81)),
    736: (1, (32, 16), dict(behind=True)), 738: (1, (58, 8), dict(behind=True)),
    740: (1, (92, 24)), 742: (0, (25, 50)), 744: (0, (1, 21)), 746: (0, (10, 52), dict(fixed=True)),
    748: (0, (49, 8)), 750: (0, (30, 63), dict(behind=True)), 752: (0, (100, 56)),
    754: (0, (100, 74)), 756: (0, (25, 79)), 758: (0, (8, 80), dict(fixed=True)), 760: (0, (52, 25)),
    763: (0, (73, 1)), 769: (0, (73, 1)), 781: (0, (59, 6)), 783: (1, (52, 9)),
    786: (0, (2, 54), dict(fixed=True)), 788: (0, (4, 54), dict(fixed=True)), 790: (0, (3, 50)), 792: (0, (1, 42)),
    795: (0, (1, 30)), 800: (0, (0, 29)), 804: (0, (0, 30)), 808: (0, (0, 30)),
    818: (0, (36, 156)), 821: (0, (38, 156)),
    834: (0, (78, 72)), 836: (0, (20, 22)), 838: (0, (14, 16)), 840: (0, (16, 57)),
    842: (0, (3, 86)), 844: (0, (3, 86)), 846: (0, (128, 88), dict(fixed=True)), 848: (0, (132, 90), dict(fixed=True)),
    850: (0, (118, 36)), 852: (1, (190, 34)), 856: (1, (194, 27)), 858: (1, (196, 78), dict(fixed=True)),
    860: (0, (22, 26), dict(behind=True)), 862: (1, (10, 7), dict(behind=True)),
    864: (1, (16, 7), dict(behind=True)), 866: (1, (15, 7), dict(behind=True)),
    873: (0, (0, 10)), 877: (0, (0, 10)), 881: (0, (6, 140)), 883: (0, (6, 140)),
    886: ((107, 76), (68, 95), dict(fixed=True)), 888: ((106, 76), (67, 95), dict(fixed=True)), 890: ((106, 75), (67, 94), dict(fixed=True)),
    892: ((107, 75), (68, 94), dict(fixed=True)), 900: ((112, 76), (142, 83)),
    902: (0, (100, 57)), 904: (0, (58, 30)), 906: (0, (57, 33)), 908: (0, (57, 36)),
    916: (0, (35, 42)), 918: (1, (115, 70)), 920: ((64, 52), (38, 43), dict(behind=True)),
    929: (0, (79, 37)), 931: (0, (94, 78)), 939: (0, (77, 80)),
    1012: (1, (107, 112)), 1014: (0, (90, 112)), 1016: (0, (40, 100)), 1018: (0, (115, 88)),
    1020: (0, (74, 58)), 1022: (0, (73, 58)), 1024: (0, (74, 58)), 1028: (0, (52, 72)),
    1032: ((60, 88), (32, 100)), 1035: (0, (33, 73)), 1040: (1, (125, 96)),
    1043: (0, (55, 106)), 1045: ((73, 88), (52, 78)), 1047: (0, (95, 73)),
    1049: (0, (41, 113)), 1051: (0, (40, 113)), 1053: (0, (36, 113)), 1055: (0, (36, 113)),
    1057: (0, (40, 112)), 1059: (0, (45, 115)),
    1069: (0, (88, 84)), 1071: (0, (88, 82)), 1073: (0, (14, 97), dict(fixed=True)), 1075: (0, (16, 97), dict(fixed=True)),
    1077: (0, (17, 97), dict(fixed=True)),
    1097: (0, (60, 34)), 1099: (0, (52, 38)), 1103: (1, (63, 48)), 1105: (0, (58, 45)),
    1107: (1, (49, 22)),
    1109: (0, (82, 52)), 1112: None, 1114: (0, (78, 14)), 1116: (0, (80, 47)),
    1121: (0, (28, 30)), 1123: (0, (38, 61)), 1125: None, 1127: None,
    1129: (0, (57, 70), dict(len=24, fixed=True)), 1131: (0, (30, 18)),
    1133: ((63, 14), (38, 2)), 1135: ((68, 40), (50, 37)), 1137: ((83, 40), (85, 22)),
    1139: ((82, 50), (101, 52)), 1141: ((90, 36), (88, 55)),
    1154: (0, (16, 97), dict(fixed=True)),
    # 失败 lose: katana not visible (hand holds the chain) -> Yoru laid down-left
    1168: (0, (5, 70), dict(fixed=True)), 1170: (0, (5, 70), dict(fixed=True)),
    1172: (0, (5, 70), dict(fixed=True)), 1174: (0, (5, 70), dict(fixed=True)),
    1176: (0, (5, 70), dict(fixed=True)),
}
YORU_BLADE = 38.0      # blade length at scale 1 (grip+guard+blade ~ 52 px ~ body height)
YORU_GRIP = 10.0
Y_OUT = (8, 8, 8)
Y_BODY = (40, 40, 50)
Y_BODY2 = (62, 62, 76)
Y_EDGE = (172, 178, 188)
Y_INLAY = (200, 160, 64)
Y_GOLD = (230, 190, 86)
Y_GOLD_SH = (170, 126, 44)
Y_GOLD_OUT = (84, 54, 16)
Y_GRIP = (242, 240, 230)
Y_GRIP_SH = (186, 184, 174)
Y_GRIP_OUT = (98, 94, 90)
Y_JEWEL = (44, 88, 220)
Y_JEWEL_HI = (156, 200, 255)
Y_JEWEL_OUT = (18, 26, 84)
Y_GEM_G = (62, 186, 122)
SW_NONE, SW_BLADE, SW_GRIP, SW_POMMEL, SW_GUARD = range(5)


def hand_blobs(cls, heads):
    """Non-face skin blobs (hands), sorted like the annotation sheets."""
    H, W = cls["op"].shape
    headm = np.zeros((H, W), bool)
    for hd in heads:
        headm |= dilate(hd["hair"] | hd["face"], 1)
    skin = (cls["skin_light"] | cls["skin_shade"] | cls["skin_dark"]) & ~headm
    lab, n = label(skin)
    out = []
    for k in range(1, n + 1):
        ck = lab == k
        if ck.sum() < 3:
            continue
        y, x = np.nonzero(ck)
        out.append((x.mean() + 0.5, y.mean() + 0.5, ck))
    out.sort(key=lambda h: (round(h[0]), round(h[1])))
    return out


def content_key(a):
    """Hash of the character content (trail removed) + its bbox origin."""
    import hashlib
    b = a.copy()
    b[trail_mask(a)] = 0
    b[b[..., 3] == 0] = 0
    bb = Image.fromarray(b).getbbox() or (0, 0, 1, 1)
    h = hashlib.md5(b[bb[1]:bb[3], bb[0]:bb[2]].tobytes()).hexdigest()
    return h, (bb[0], bb[1])


def old_blade_mask(a, heads=None):
    """Thin, neutral (black/grey) structures sticking out of the body
    (Getsuga trail pixels are ignored so blades touching a trail count)."""
    op = (a[..., 3] > 0) & ~trail_mask(a)
    body = dilate(erode(op, 2), 2)
    rgb = a[..., :3].astype(int)
    neutral = op & (rgb.max(-1) <= 190) & ((rgb.max(-1) - rgb.min(-1)) <= 30)
    m = op & ~body & neutral
    if heads:
        for hd in heads:
            m &= ~dilate(hd["hair"] | hd["face"], 1)
    return m


def refine_direction(H_, T_, thin, span=20, min_hits=6):
    """Snap the annotated direction to the old katana if it is visible:
    best ray from the hand within +-span degrees, scored by thin pixels hit."""
    h, w = thin.shape
    base = math.degrees(math.atan2(T_[1] - H_[1], T_[0] - H_[0]))
    best = (0, 0.0, base, None)
    for da in range(-span, span + 1):
        ang = math.radians(base + da)
        dx, dy = math.cos(ang), math.sin(ang)
        hits, seen, last = 0, set(), None
        for i in range(6, 96):
            t = i * 0.5
            x, y = int(math.floor(H_[0] + dx * t)), int(math.floor(H_[1] + dy * t))
            if not (0 <= x < w and 0 <= y < h) or (x, y) in seen:
                continue
            seen.add((x, y))
            if thin[y, x]:
                hits += 1
                last = t
        key = (hits, -abs(da))
        if key > (best[0], -abs(best[1])):
            best = (hits, da, base + da, last)
    ok = (best[0] >= 8 and abs(best[1]) <= 12) or (best[0] >= 15 and abs(best[1]) <= span)
    if not ok:
        return T_, 0, best[0]
    ang = math.radians(best[2])
    L = max(best[3] or 20.0, 12.0)
    return (H_[0] + math.cos(ang) * L, H_[1] + math.sin(ang) * L), best[1], best[0]


def make_spec(H_, T_, k, opts):
    H_ = np.array(H_, float)
    d = np.array(T_, float) - H_
    d /= np.linalg.norm(d) + 1e-9
    n1 = np.array([-d[1], d[0]])
    if abs(n1[1]) >= 0.3:
        nv = n1 if n1[1] > 0 else -n1          # cutting edge faces down
    else:
        nv = n1 if n1[0] > 0 else -n1          # vertical blade: edge faces right
    nv = nv * opts.get("edge", 1)
    Lb = opts.get("len", YORU_BLADE) * k
    return dict(H=H_, T=np.array(T_, float), d=d, nv=nv, k=k, Lb=Lb, Lg=YORU_GRIP * k,
                sag=1.8 * k, G=H_ + d * 2.5 * k, behind=bool(opts.get("behind", False)))


def clone_swords(cls, heads):
    """上必杀 afterimages: the sword runs along the clone's streak axis,
    from its hands forward."""
    specs = []
    H, W = cls["op"].shape
    yy, xx = np.mgrid[0:H, 0:W]
    hands = hand_blobs(cls, heads)
    cents = [np.array([np.nonzero(h["core"])[1].mean() + .5, np.nonzero(h["core"])[0].mean() + .5])
             for h in heads]
    for i, c in enumerate(cents):
        near = [h for h in hands if math.hypot(h[0] - c[0], h[1] - c[1]) < 20]
        if not near:
            continue
        hx, hy, _ = min(near, key=lambda h: math.hypot(h[0] - c[0], h[1] - c[1]))
        own = cls["op"] & (np.hypot(xx + .5 - c[0], yy + .5 - c[1]) < 26)
        for j, c2 in enumerate(cents):
            if j != i:
                own &= np.hypot(xx + .5 - c[0], yy + .5 - c[1]) <= np.hypot(xx + .5 - c2[0], yy + .5 - c2[1])
        py, px = np.nonzero(own)
        P = np.stack([px - px.mean(), py - py.mean()], 1)
        w, v = np.linalg.eigh(P.T @ P)
        e = v[:, 1]
        if e @ np.array([hx - c[0], hy - c[1]]) < 0:
            e = -e
        specs.append(make_spec((hx, hy), (hx + e[0] * 30, hy + e[1] * 30), 1.0, {}))
    return specs


def sword_specs(bid, a, cls, heads, annotated):
    """Return the list of sword specs (original-bitmap coordinates)."""
    k = 0.8 if bid in RESAMPLED_SMALL else 1.0
    if bid in CLONE_IDS:
        return clone_swords(cls, heads), "clone-auto"
    ann, off, src = None, (0, 0), bid
    if bid in SWORDS:
        ann = SWORDS[bid]
    else:
        key, org = content_key(a)
        for rid, (rkey, rorg) in annotated.items():
            if rkey == key:
                ann, src = SWORDS[rid], rid
                off = (org[0] - rorg[0], org[1] - rorg[1])
                break
        else:
            raise SystemExit(f"{bid}: no sword annotation")
    if ann is None:
        return [], f"none(from {src})"
    hand, tip = ann[0], ann[1]
    opts = ann[2] if len(ann) > 2 else {}
    if isinstance(hand, int):
        if src != bid:      # hand blobs are computed on this bitmap: same order
            pass
        hb = hand_blobs(cls, heads)
        hx, hy = hb[hand][0], hb[hand][1]
    else:
        hx, hy = hand[0] + off[0] + 0.5, hand[1] + off[1] + 0.5
    tx, ty = tip[0] + off[0] + 0.5, tip[1] + off[1] + 0.5
    if not opts.get("fixed"):
        (tx, ty), dang, hits = refine_direction((hx, hy), (tx, ty), old_blade_mask(a, heads))
    else:
        dang, hits = 0, 0
    how = ("annotated" if src == bid else f"dup of {src}") + (f", snapped {dang:+d}deg ({hits} px)" if dang or hits >= 6 else "")
    return [make_spec((hx, hy), (tx, ty), k, opts)], how


def yoru_parts(s, n, P):
    k, Lb, Lg = P["k"], P["Lb"], P["Lg"]
    part = np.zeros(s.shape, np.int8)
    sb = np.clip(s / Lb, 0, 1)
    c = -P["sag"] * sb ** 2
    we = (1.6 + 1.7 * sb) * k * np.clip((Lb - s) / (7.0 * k), 0, 1) ** 0.6
    wb = 1.0 * k * np.clip((Lb - s) / (1.5 * k), 0, 1) ** 0.5
    blade = (s >= 0.5 * k) & (s <= Lb) & (n >= c - wb) & (n <= c + we)
    grip = (s >= -Lg) & (s < -0.5 * k) & (np.abs(n) <= 1.4 * k)
    pc = -Lg - 1.3 * k
    pommel = (s - pc) ** 2 + n ** 2 <= (1.7 * k) ** 2
    an = np.abs(n)
    guard = (((np.abs(s) <= 1.2 * k) & (an <= 7.6 * k))
             | ((an >= 6.2 * k) & (an <= 7.6 * k) & (np.abs(s) <= 2.2 * k))
             | ((an <= 1.4 * k) & (s >= -1.6 * k) & (s <= 2.8 * k)))
    part[blade] = SW_BLADE
    part[grip] = SW_GRIP
    part[pommel] = SW_POMMEL
    part[guard] = SW_GUARD
    return part


def sword_bounds(P):
    G, d, nv, k = P["G"], P["d"], P["nv"], P["k"]
    pts = [G + d * (P["Lb"] + 1), G - d * (P["Lg"] + 3.5 * k)]
    for sgn in (-1, 1):
        pts.append(G + nv * sgn * 8 * k + d * 2.5 * k)
        pts.append(G + nv * sgn * 8 * k - d * 2.5 * k)
        pts.append(G + d * P["Lb"] * 0.6 + nv * sgn * 4 * k)
    pts = np.array(pts)
    return (int(math.floor(pts[:, 0].min())) - 2, int(math.floor(pts[:, 1].min())) - 2,
            int(math.ceil(pts[:, 0].max())) + 3, int(math.ceil(pts[:, 1].max())) + 3)


def raster_sword(P):
    """Rasterise one sword; returns (part, rgba, x0, y0) on its own window."""
    x0, y0, x1, y1 = sword_bounds(P)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    px, py = xx + 0.5 - P["G"][0], yy + 0.5 - P["G"][1]
    s = px * P["d"][0] + py * P["d"][1]
    n = px * P["nv"][0] + py * P["nv"][1]
    part = yoru_parts(s, n, P)
    m = part > 0
    edge = m & (nbcount(m, N4) < 4)
    k = P["k"]
    col = np.zeros(part.shape + (4,), np.uint8)
    c = -P["sag"] * np.clip(s / P["Lb"], 0, 1) ** 2
    rel = n - c
    blade = part == SW_BLADE
    col[blade, :3] = Y_BODY
    col[blade & (rel > 1.2 * k + 0.9 * np.clip(s / P["Lb"], 0, 1) * k), :3] = Y_BODY2
    col[blade & edge & (rel <= 0.3 * k), :3] = Y_OUT
    col[blade & edge & (rel > 0.3 * k), :3] = Y_EDGE
    inlay = blade & ~edge & (s >= 1.5 * k) & (s <= 8 * k) & (np.abs(rel - 0.2 * k) <= 0.5)
    col[inlay, :3] = Y_INLAY
    grip = part == SW_GRIP
    wrap = ((np.floor(s) + np.floor(n)) % 3) == 0
    col[grip, :3] = Y_GRIP
    col[grip & wrap, :3] = Y_GRIP_SH
    col[grip & edge, :3] = Y_GRIP_OUT
    pom = part == SW_POMMEL
    pc = -P["Lg"] - 1.3 * k
    col[pom, :3] = Y_JEWEL
    col[pom & ~edge & ((s - pc) + n * 0.7 < -0.4), :3] = Y_JEWEL_HI
    col[pom & edge, :3] = Y_JEWEL_OUT
    gd = part == SW_GUARD
    col[gd, :3] = Y_GOLD
    col[gd & (s < -0.3 * k), :3] = Y_GOLD_SH
    col[gd & edge, :3] = Y_GOLD_OUT
    col[gd & ~edge & (np.abs(s) <= 0.6) & (np.abs(n) <= 0.6), :3] = Y_JEWEL
    col[gd & ~edge & (np.abs(s) <= 0.6) & (np.abs(np.abs(n) - 4.2 * k) <= 0.6), :3] = Y_GEM_G
    if P.get("glow"):                 # 超必杀: glowing Yoru (see SI_FX)
        si_blade_colors(col, part, edge, rel, P)
    col[m, 3] = 255
    return part, col, x0, y0


def paste_window(dst_mask, dst_rgba, part, col, x0, y0):
    H, W = dst_mask.shape
    h, w = part.shape
    gx0, gy0, gx1, gy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if gx1 <= gx0 or gy1 <= gy0:
        return
    sl = (slice(gy0 - y0, gy1 - y0), slice(gx0 - x0, gx1 - x0))
    m = part[sl] > 0
    dst_mask[gy0:gy1, gx0:gx1] |= m
    dst_rgba[gy0:gy1, gx0:gx1][m] = col[sl][m]


def shift_spec(P, dx, dy):
    Q = dict(P)
    for key in ("H", "T", "G"):
        Q[key] = P[key] + np.array([dx, dy], float)
    return Q


def erode(m, it=1):
    return ~dilate(~m, it)


def draw_swords(img, a, specs, cls, head_keep, hand_px):
    """Erase the old katana outside the body and draw Yoru (in place)."""
    if not specs:
        return img
    H, W = img.shape[:2]
    thin = old_blade_mask(a)
    yy, xx = np.mgrid[0:H, 0:W]
    swm = np.zeros((H, W), bool)
    swc = np.zeros((H, W, 4), np.uint8)
    for P in specs:
        part, col, x0, y0 = raster_sword(P)
        paste_window(swm, swc, part, col, x0, y0)
    pre = img.copy()
    for P in specs:
        # old blade: thin neutral pixels along hand->old tip
        v = P["T"] - P["H"]
        L = np.linalg.norm(v)
        u = v / (L + 1e-9)
        px, py = xx + 0.5 - P["H"][0], yy + 0.5 - P["H"][1]
        t = px * u[0] + py * u[1]
        dist = np.abs(px * -u[1] + py * u[0])
        old = thin & (dist <= 3.0) & (t >= 2.0) & (t <= L + 3.0) & ~swm
        img[old, 3] = 0
    img[swm] = swc[swm]
    # the holding hand wraps the grip
    img[hand_px] = pre[hand_px]
    if any(P["behind"] for P in specs):
        img[head_keep] = pre[head_keep]
    return img

# ==========================================================================
# character processing
# ==========================================================================
def hair_to_black(rgb):
    L = luma(rgb)
    val = np.clip(10 + (L - 0.28) * (74 / 0.62), 8, 84)
    out = np.stack([val, val * 0.96, val * 1.10], -1)
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def local_coords(H, W, geo):
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = xx + 0.5 - geo["origin"][0], yy + 0.5 - geo["origin"][1]
    U, F = geo["U"], geo["F"]
    return dx * F[0] + dy * F[1], dx * U[0] + dy * U[1]


def process_character(a, bid, report):
    out = a.copy()
    resampled = bid in RESAMPLED_SMALL
    cls = classify(a, resampled)
    heads = find_heads(a, cls, resampled)
    H, W = a.shape[:2]
    infos = []
    hat_layers = []
    for idx in range(len(heads)):
        hd = heads[idx]
        ov = OVERRIDES.get((bid, idx), {})
        if ov.get("skip"):
            continue
        geo = head_geometry(a, cls, heads, idx, bid)
        hatm, col, P = render_hat(H, W, geo)
        lu, lv = local_coords(H, W, geo)
        s = geo["scale"]
        hair, face = hd["hair"], hd["face"]
        head = hair | face
        above = lv > -0.4 * s
        # hair (and bare forehead) above the brim line is replaced by the hat
        kill = (hair & above) | (face & above & ~hatm)
        out[kill & ~hatm, 3] = 0
        keep = hair & ~kill
        out[keep, :3] = hair_to_black(a[keep, :3])
        # lone spike tips below the brim
        opq = out[..., 3] > 0
        tips = keep & (nbcount(opq) <= 2) & ~hatm
        out[tips, 3] = 0
        # tiny orphan specks left above the brim around the head
        opq = out[..., 3] > 0
        zone = dilate(head, 2) & above & ~hatm
        lab, n = label(opq & zone)
        for k in range(1, n + 1):
            ck = lab == k
            if ck.sum() <= 3 and not (dilate(ck, 1) & opq & ~zone).any():
                out[ck, 3] = 0
        if bid in MASK_IDS:
            unmask_head(a, out, cls, hd, geo, lu, lv, hatm, bid)
        # eyes: white pixels in the face band right under the brim -> yellow
        rgb = a[..., :3].astype(int)
        white = (rgb.min(-1) >= 215) & cls["op"]
        skin = cls["skin_light"] | cls["skin_shade"]
        eyes = (white & dilate(skin & face, 1) & (lv < -0.4 * s) & (lv > -5.0 * s)
                & ~hatm)
        eyes &= np.all(out[..., :3] == a[..., :3], -1)   # not already repainted
        out[eyes, :3] = EYE_YELLOW
        hat_layers.append((hatm, col))
        info = dict(head=idx, angle=geo["angle"], raw_angle=round(geo["raw_angle"], 1),
                    facing=geo["facing"], scale=s, origin=[round(float(c), 2) for c in geo["origin"]],
                    face_du=round(geo["face_du"], 2), eye_v=geo["eye_v"],
                    hand_angle=geo["hand_angle"], eyes=int(eyes.sum()),
                    hat=dict(Af=P["Af"], Ab=P["Ab"], ct=P["ct"], feather=P["feather"]))
        add_beard(out, cls, hd, geo, lu, lv, hatm, info)
        infos.append(info)
    cleanup_orange(a, out, cls, heads)
    # skin retone (face + hands) before the hats go on top
    for src, dst in SKIN_RETONE.items():
        m = color_eq(out[..., :3], src) & (out[..., 3] > 0)
        out[m, :3] = dst
    report["heads"] = infos
    head_keep = np.zeros((H, W), bool)
    for hd in heads:
        head_keep |= (hd["hair"] | hd["face"])
    head_keep &= out[..., 3] > 0
    return out, hat_layers, cls, heads, head_keep


HAIR_PALETTE = [(248, 144, 0), (248, 240, 0), (160, 40, 16),
                (255, 148, 0), (255, 247, 0), (165, 41, 16)]


def cleanup_orange(a, out, cls, heads):
    """Hair-palette pixels the head pass did not reach (face/bang outline,
    hand highlights, streaked afterimage fragments): next to hand/face skin
    -> skin tones, otherwise -> black-hair tones.  No orange is left."""
    rgb = a[..., :3]
    left = np.zeros(cls["op"].shape, bool)
    for c in HAIR_PALETTE:
        left |= color_eq(rgb, c)
    left &= cls["op"] & (out[..., 3] > 0) & np.all(out[..., :3] == rgb, -1)
    if not left.any():
        return
    hairm = np.zeros_like(left)
    for hd in heads:
        hairm |= hd["hair"]
    skin = cls["skin_light"] | cls["skin_shade"] | cls["skin_dark"]
    skinny = left & dilate(skin, 1) & ~dilate(hairm, 1)
    for src, dst in (((248, 144, 0), (226, 154, 96)), ((255, 148, 0), (230, 156, 98)),
                     ((248, 240, 0), (255, 222, 156)), ((255, 247, 0), (255, 222, 156)),
                     ((160, 40, 16), (118, 70, 42)), ((165, 41, 16), (121, 72, 43))):
        m = skinny & color_eq(rgb, src)
        out[m, :3] = dst
    rest = left & ~skinny
    out[rest, :3] = hair_to_black(rgb[rest])


def add_beard(out, cls, hd, geo, lu, lv, hatm, info):
    """Moustache + pointed goatee as 1-2 px dark marks on faces >= 8 px tall."""
    s = geo["scale"]
    face = hd["face"] & (cls["skin_light"] | cls["skin_shade"]) & (out[..., 3] > 0) & ~hatm
    if face.sum() < 14:
        info["beard"] = "skip(face<14)"
        return
    fv = lv[face]
    if fv.max() - fv.min() < 6.5 * s:
        info["beard"] = "skip(short)"
        return
    H, W = out.shape[:2]
    U, F = geo["U"], geo["F"]
    v_bot = fv.min()
    low = face & (lv <= v_bot + 1.0)
    ys, xs = np.nonzero(low)
    k = int(np.argmax(lu[low]))
    cy, cx = int(ys[k]), int(xs[k])

    def step(y, x, dv, du):
        return (int(math.floor(y + 0.5 + U[1] * dv + F[1] * du)),
                int(math.floor(x + 0.5 + U[0] * dv + F[0] * du)))

    marks = [(cy, cx), step(cy, cx, -1, 0)]          # goatee: chin + 1 below
    for du_ in (0, -1):                               # moustache: 2 above chin
        my, mx = step(cy, cx, 2.2, du_)
        if 0 <= my < H and 0 <= mx < W and face[my, mx]:
            marks.append((my, mx))
    done = []
    for y, x in marks:
        if 0 <= y < H and 0 <= x < W and not hatm[y, x]:
            out[y, x, :3] = BEARD
            out[y, x, 3] = 255
            done.append([y, x])
    info["beard"] = done


def unmask_head(a, out, cls, hd, geo, lu, lv, hatm, bid):
    """Hollow mask -> bare face.  Mask pixels above the brim are dropped (the
    hat replaces the top of the head), the rest become skin; the full skull
    mask (MASK_FULL) additionally gets a painted front-facing face."""
    s_ = geo["scale"]
    rgb = a[..., :3].astype(int)
    op = cls["op"] & (out[..., 3] > 0)
    head = hd["hair"] | hd["face"]
    v_low = lv[head].min()
    full = bid in MASK_FULL
    zone = dilate(head, 5) & (lv >= v_low - (4.5 if full else 1.0))
    light = op & zone & (rgb.min(-1) >= 185) & (np.ptp(rgb, -1) < 24) & ~hd["hair"]
    if full:
        light |= op & zone & (rgb.min(-1) >= 140) & (np.ptp(rgb, -1) < 24) & ~hd["hair"] & dilate(light, 1)
        # dark markings enclosed by the mask (eye holes, teeth) on mask rows
        mk = light.copy()
        ys, xs = np.nonzero(mk)
        enclosed = np.zeros_like(mk)
        for y in np.unique(ys):
            row = xs[ys == y]
            enclosed[y, row.min():row.max() + 1] = True
        enclosed &= op & ~hd["hair"] & (np.ptp(rgb, -1) < 24)
        light |= enclosed
    above = lv > -0.4 * s_
    kill = light & above & ~hatm
    out[kill, 3] = 0
    keep = light & ~above
    white = keep & (rgb.min(-1) >= 235)
    out[keep, :3] = SKIN_RETONE[(231, 140, 0)]
    out[white, :3] = (255, 222, 156)
    if not full:
        return
    ys, xs = np.nonzero(keep & ~hatm)
    if not len(xs):
        return
    # template: top row right under the brim, centred on the mask
    top = int(ys.min())
    cx = int(round(xs.mean()))
    colors = {"L": (255, 222, 156), "s": SKIN_RETONE[(231, 140, 0)], "D": BEARD, "Y": EYE_YELLOW}
    w = len(FACE_FRONT[0])
    for r, line in enumerate(FACE_FRONT):
        for c, ch in enumerate(line):
            y, x = top + r, cx - w // 2 + c
            if ch == "." or not (0 <= y < out.shape[0] and 0 <= x < out.shape[1]):
                continue
            if keep[y, x] or (out[y, x, 3] > 0 and not hd["hair"][y, x] and not hatm[y, x]
                              and rgb[y, x].max() < 60):
                out[y, x, :3] = colors[ch]
                out[y, x, 3] = 255


# ==========================================================================
# effect recolouring
# ==========================================================================
def recolor_pixels(a, mask, stops, gamma=GAMMA_TRAIL):
    out = a.copy()
    if mask.any():
        t = luma(a[..., :3]) ** gamma
        out[mask, :3] = ramp(t[mask], stops)
    return out


def edge_distance(m, cap=5):
    """4-neighbour distance to the outside of mask m, capped."""
    d = np.zeros(m.shape, int)
    cur = m.copy()
    for k in range(cap):
        inner = cur & (nbcount(cur, N4) == 4)
        d[cur & ~inner] = k
        cur = inner
    d[cur] = cap
    return d


def recolor_effect(a, stops):
    """Effect-only bitmap.  Flat near-black effects (the 招2 Getsuga streaks)
    get an edge->core glow so they read as energy; others a luminance map."""
    op = a[..., 3] > 0
    L = luma(a[..., :3])
    out = a.copy()
    if (L[op] < 0.12).mean() > 0.9:
        d = edge_distance(op)
        t = 0.20 + 0.18 * d + 0.5 * L
        out[op, :3] = ramp(t[op], stops)
        return out, "glow"
    return recolor_pixels(a, op, stops, GAMMA_EFFECT), "luma"


def apply_trail(a, char_out, tm, stops):
    """Recolour trail pixels that the character pass left untouched."""
    rec = recolor_pixels(a, tm, stops)
    keep = tm & np.all(char_out == a, -1)
    out = char_out.copy()
    out[keep] = rec[keep]
    return out


def trail_mask(a):
    rgb = a[..., :3]
    op = a[..., 3] > 0
    m = np.zeros(op.shape, bool)
    for c in TRAIL_COLORS:
        m |= color_eq(rgb, c)
    m &= op
    h, s, v = hsv_arrays(rgb)
    bluish = op & (h >= 200) & (h <= 300) & (s >= 0.35)
    m |= bluish & dilate(m, 2)
    return m


# ==========================================================================
# 超必杀 (S+I): emphasis beat, glowing Yoru, grander slash and wave
# ==========================================================================
# Sprite 1180, label 超必杀 (frames 622-717):
#   622-629  windup 1012 1014 1016 1018 (2 frames each; face2 cut-in at 625)
#   630-647  charge: sprite 1026 loops 1020 1022 1024 (2 frames each, 3 cycles)
#   648-653  slash 1028 1040 1043;  654-702 follow-through 1045 (held 49 frames)
#   648-683  wave sprite 1038: 4 nested copies (x 1.0/0.83/0.63/0.63, y 1.69/0.97/
#            0.42/0.23) of shape 1033 (bitmap 1032, frames 1-2) / 1036 (1035, 3-4),
#            stretched horizontally 1.0 -> 2.45 -> 1.0 by the timeline.
# Per-bitmap parameters:
#   k      Yoru scale (whole sword; the grip stays in the hand)
#   glow   1..4  blade colours (SI_BLADE) + aura rings (SI_AURA)
#   glint  1..3  yellow 4-point star on the front eye (SI_GLINT)
#   star   4-point flare at the blade tip
#   trail  restyle the Getsuga trail as a bright blade afterglow
SI_FX = {
    # windup: Yoru starts to grow and glow
    1012: dict(k=1.00, glow=1),
    1014: dict(k=1.08, glow=1),
    1016: dict(k=1.16, glow=2),
    1018: dict(k=1.26, glow=2, glint=1),
    # charge beat: the "dun-dun" (1022 = peak)
    1020: dict(k=1.35, glow=3, glint=2),
    1022: dict(k=1.42, glow=4, glint=3, star=True),
    1024: dict(k=1.35, glow=3, glint=1),
    # release
    1028: dict(k=1.25, glow=3, trail=True),
    1040: dict(k=1.15, glow=3, trail=True),
    1043: dict(k=1.10, glow=2, trail=True),
    1045: dict(k=1.00, glow=1),          # held 49 frames: only a faint after-glow
}
SI_WAVES = (1032, 1035)

# blade colours by glow level: body, core (fully inside), cutting edge, back edge
SI_BLADE = {
    1: dict(edge=(110, 225, 255)),
    2: dict(body=(40, 120, 250), edge=(225, 250, 255), back=(16, 50, 180)),
    3: dict(body=(150, 225, 255), core=(255, 255, 255), edge=(255, 255, 255), back=(40, 130, 255)),
    4: dict(body=(225, 248, 255), core=(255, 255, 255), edge=(255, 255, 255), back=(110, 210, 255)),
}
# aura rings around the blade (inner -> outer): rgb, alpha
SI_AURA = {
    1: [((24, 80, 230), 150)],
    2: [((60, 170, 255), 255), ((22, 70, 220), 150)],
    3: [((90, 210, 255), 255), ((40, 130, 255), 225), ((20, 64, 210), 140), ((12, 36, 150), 70)],
    4: [((150, 235, 255), 255), ((70, 190, 255), 255), ((34, 110, 250), 215), ((18, 56, 200), 140),
        ((10, 30, 140), 70)],
}
# eye glint: centre, horizontal arm, vertical arm (colours by distance), diagonal
SI_GLINT = {
    1: dict(c=(255, 255, 235), h=[(255, 214, 60)], v=[(255, 214, 60)], d=None),
    2: dict(c=(255, 255, 255), h=[(255, 246, 170), (255, 200, 40)], v=[(255, 236, 130), (240, 170, 30)],
            d=None),
    3: dict(c=(255, 255, 255), h=[(255, 252, 215), (255, 240, 150), (255, 218, 70), (250, 184, 34),
                                  (226, 140, 20)],
            v=[(255, 248, 190), (255, 222, 90), (240, 170, 30)], d=(255, 236, 140)),
}
TIP_STAR = dict(c=(255, 255, 255), h=[(200, 245, 255), (110, 215, 255), (50, 150, 255)],
                v=[(200, 245, 255), (110, 215, 255), (50, 150, 255)], d=(160, 230, 255))
# trail afterglow: colour by distance (px) from the trail's leading (outer) edge
SI_TRAIL = [(170, 240, 255), (255, 255, 255), (200, 245, 255), (130, 225, 255), (90, 205, 255),
            (60, 165, 255), (60, 165, 255), (40, 125, 250), (40, 125, 250), (32, 100, 245),
            (32, 100, 245), (26, 80, 230), (26, 80, 230), (20, 62, 205)]
SI_TRAIL_INNER = (14, 40, 150)
SI_TRAIL_STRAND = ((90, 205, 255), (190, 240, 255))      # thin strand, its leading pixels
SI_TRAIL_HALO = [((40, 140, 255), 190), ((24, 90, 235), 100)]


def hash01(*keys):
    """Deterministic integer hash -> [0, 1) (numpy arrays or ints, broadcast)."""
    x = np.uint64(0x9E3779B9)
    m = np.uint64(0xFFFFFFFF)
    for k in keys:
        x = ((x ^ (np.asarray(k).astype(np.int64).astype(np.uint64) & m)) * np.uint64(0x85EBCA6B)) & m
        x = x ^ (x >> np.uint64(13))
        x = (x * np.uint64(0xC2B2AE35)) & m
        x = x ^ (x >> np.uint64(16))
    return x.astype(np.float64) / 4294967296.0


def over(img, mask, rgb, alpha):
    """Composite a flat colour over img at mask (straight alpha)."""
    if not mask.any():
        return
    a = alpha / 255.0
    da = img[mask, 3].astype(float) / 255.0
    oa = a + da * (1 - a)
    c = (np.array(rgb, float) * a + img[mask, :3].astype(float) * (da * (1 - a))[:, None]) \
        / np.maximum(oa, 1e-6)[:, None]
    img[mask, :3] = np.clip(np.round(c), 0, 255).astype(np.uint8)
    img[mask, 3] = np.clip(np.round(oa * 255), 0, 255).astype(np.uint8)


def rings(m, n):
    """Successive 1 px rings around mask m (alternating 4/8 neighbourhoods: octagonal)."""
    out, cur = [], m.copy()
    for i in range(n):
        nxt = dilate(cur, 1, N4 if i % 2 == 0 else N8)
        out.append(nxt & ~cur)
        cur = nxt
    return out


def put_px(img, x, y, rgb, alpha=255):
    """Composite one pixel (straight alpha); off-canvas pixels are ignored."""
    H, W = img.shape[:2]
    if not (0 <= x < W and 0 <= y < H):
        return
    a = max(0, min(255, alpha)) / 255.0
    da = img[y, x, 3] / 255.0
    oa = a + da * (1 - a)
    if oa <= 0:
        return
    c = (np.array(rgb, float) * a + img[y, x, :3].astype(float) * da * (1 - a)) / oa
    img[y, x, :3] = np.clip(np.round(c), 0, 255).astype(np.uint8)
    img[y, x, 3] = int(round(oa * 255))


def draw_star(img, x, y, st):
    """4-point star centred on pixel (x, y): long horizontal arms, shorter vertical."""
    for i, c in enumerate(st["h"], 1):
        put_px(img, x - i, y, c)
        put_px(img, x + i, y, c)
    for i, c in enumerate(st["v"], 1):
        put_px(img, x, y - i, c)
        put_px(img, x, y + i, c)
    if st.get("d"):
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            put_px(img, x + dx, y + dy, st["d"])
    put_px(img, x, y, st["c"])


def si_spec(P, fx):
    """Scale a sword spec by fx['k'] about the hand and attach the glow level."""
    Q = dict(P)
    m = fx["k"]
    for key in ("k", "Lb", "Lg", "sag"):
        Q[key] = P[key] * m
    Q["G"] = P["H"] + P["d"] * 2.5 * Q["k"]
    Q["glow"] = fx["glow"]
    return Q


def si_margin(fx):
    """Extra canvas needed around the sword for the aura / tip star."""
    return len(SI_AURA[fx["glow"]]) + (4 if fx.get("star") else 0)


def si_blade_colors(col, part, edge, rel, P):
    k = P["k"]
    pal = SI_BLADE[P["glow"]]
    blade = part == SW_BLADE
    body = blade & ~edge
    cut = blade & edge & (rel > 0.3 * k)
    back = blade & edge & (rel <= 0.3 * k)
    if "body" in pal:
        col[body, :3] = pal["body"]
    if "core" in pal:
        col[body & (nbcount(blade, N8) == 8), :3] = pal["core"]
    col[cut, :3] = pal["edge"]
    if "back" in pal:
        col[back, :3] = pal["back"]


def si_sword_fx(img, specs, effect, fx, seed):
    """Aura rings around the glowing blade (over transparent / effect pixels only,
    never over the character), sparkles, and the tip star."""
    H, W = img.shape[:2]
    blade = np.zeros((H, W), bool)
    sword = np.zeros((H, W), bool)
    for P in specs:
        part, _, x0, y0 = raster_sword(P)
        paste_window(blade, np.zeros((H, W, 4), np.uint8), (part == SW_BLADE).astype(np.int8),
                     np.zeros(part.shape + (4,), np.uint8), x0, y0)
        paste_window(sword, np.zeros((H, W, 4), np.uint8), part, np.zeros(part.shape + (4,), np.uint8), x0, y0)
    free = ((img[..., 3] == 0) | effect) & ~sword
    for ring, (rgb, al) in zip(rings(blade, len(SI_AURA[fx["glow"]])), SI_AURA[fx["glow"]]):
        over(img, ring & free, rgb, al)
    g = fx["glow"]
    for P in specs:
        if g >= 3:          # sparkles drifting off the blade
            for i in range(4 if g == 3 else 7):
                t = 0.25 + 0.75 * float(hash01(seed, i, 1))
                side = 1 if hash01(seed, i, 2) < 0.5 else -1
                off = 3.0 + 3.5 * float(hash01(seed, i, 3)) + 0.5 * g
                p = P["G"] + P["d"] * P["Lb"] * t + P["nv"] * side * off
                x, y = int(math.floor(p[0])), int(math.floor(p[1]))
                if 0 <= x < W and 0 <= y < H and free[y, x]:
                    if hash01(seed, i, 4) < 0.35:
                        draw_star(img, x, y, dict(c=(255, 255, 255), h=[(110, 215, 255)],
                                                  v=[(110, 215, 255)], d=None))
                    else:
                        put_px(img, x, y, (235, 250, 255))
        if fx.get("star"):
            tp = P["G"] + P["d"] * (P["Lb"] + 0.5)
            draw_star(img, int(math.floor(tp[0])), int(math.floor(tp[1])), TIP_STAR)


def si_eye(head):
    """Front-eye pixel: 1 px forward, 3 px below the brim origin."""
    o = np.array(head["origin"], float)
    F = np.array([head["facing"], 0.0])
    p = o + F * 1.0 + np.array([0.0, 3.0])
    return int(math.floor(p[0])), int(math.floor(p[1]))


def si_trail(img, tm, pivot):
    """Restyle a Getsuga trail as a bright afterglow: white-hot just inside the
    leading (outer, away from the sword hand) edge, cyan -> blue -> deep blue
    towards the inner edge; thin strands cyan; a soft blue halo outside."""
    H, W = tm.shape
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = xx + 0.5 - pivot[0], yy + 0.5 - pivot[1]
    n = np.hypot(dx, dy) + 1e-6
    fx_ = np.clip(np.floor(xx + 0.5 + 1.5 * dx / n).astype(int), 0, W - 1)
    fy_ = np.clip(np.floor(yy + 0.5 + 1.5 * dy / n).astype(int), 0, H - 1)
    outer = tm & ~tm[fy_, fx_]
    d = np.full((H, W), 999)
    d[outer] = 0
    cur, k = outer.copy(), 0
    while True:
        nxt = dilate(cur, 1, N4) & tm & (d == 999)
        if not nxt.any():
            break
        k += 1
        d[nxt] = k
        cur = nxt
    col = np.array(SI_TRAIL, np.uint8)
    out = img.copy()
    m = tm & (d < 999)
    out[m, :3] = col[np.minimum(d[m], len(SI_TRAIL) - 1)]
    edge = tm & (nbcount(tm, N4) < 4)
    out[edge & ~outer & (d >= 3), :3] = SI_TRAIL_INNER
    thin = tm & (edge_distance(tm, 2) == 0) & ~dilate(tm & (edge_distance(tm, 2) >= 1), 1)
    out[thin, :3] = SI_TRAIL_STRAND[0]
    out[thin & outer, :3] = SI_TRAIL_STRAND[1]
    out[tm, 3] = 255
    free = out[..., 3] == 0
    for ring, (rgb, al) in zip(rings(tm, len(SI_TRAIL_HALO)), SI_TRAIL_HALO):
        over(out, ring & free, rgb, al)
    return out


# --------------------------------------------------------------------------
# the wave (bitmaps 1032 / 1035): redrawn from scratch, no figure
# --------------------------------------------------------------------------
# shape 1033 / 1036 local (0, 0) in bitmap px (their bitmap-fill translate)
WAVE_OFF = {1032: (78.35, 1.0), 1035: (218.7, 1.05)}
WAVE_PAD = [0, 4, 0, 4]          # also makes tools/mihawk.py rebuild the cropped shape rects
WAVE_SEED = {1032: 11, 1035: 23}
# crescent in shape px: rows cy +- R; outer / inner edge = superellipse arcs
# from the horn tips (x = tip) to x = out / inn at mid height
WAVE_GEO = dict(cy=75.0, R=73.0, tip=2.0, out=110.0, inn=50.0, p=2.5, q=1.7)
WAVE_NF = 22                     # fibres across the body
# colour bands across the body: v = 0 leading (outer) edge .. 1 inner edge
WAVE_BANDS = [(0.04, (150, 230, 255)), (0.08, (225, 250, 255)), (0.20, (255, 255, 255)),
              (0.29, (205, 245, 255)), (0.40, (120, 220, 255)), (0.53, (66, 172, 255)),
              (0.67, (38, 116, 248)), (0.82, (24, 76, 225)), (9.99, (16, 48, 178))]
WAVE_SEP = (14, 40, 160)         # dark separator fibres
WAVE_INNER = (10, 28, 118)       # inner-edge outline (separates the nested copies)
# broken energy rims ahead of the leading edge: (dx0, dx1, |s| max, rgb, alpha)
WAVE_RIMS = [(2.5, 3.5, 0.86, (150, 230, 255), 255), (5.5, 6.5, 0.66, (90, 200, 255), 235),
             (8.5, 9.5, 0.40, (60, 160, 255), 200)]
WAVE_HALO = [((60, 160, 255), 200), ((40, 130, 250), 150), ((28, 96, 235), 105), ((20, 70, 215), 65),
             ((14, 50, 190), 30)]


def render_wave(bid, size0):
    H0, W0 = size0
    l, t, r, b = WAVE_PAD
    H, W = H0 + t + b, W0 + l + r
    ox, oy = WAVE_OFF[bid][0] + l, WAVE_OFF[bid][1] + t
    seed = WAVE_SEED[bid]
    g = WAVE_GEO
    yy, xx = np.mgrid[0:H, 0:W]
    sx, sy = xx + 0.5 - ox, yy + 0.5 - oy
    s = (sy - g["cy"]) / g["R"]
    sa = np.clip(np.abs(s), 0, 1)
    xo = g["tip"] + (g["out"] - g["tip"]) * (1 - sa ** g["p"]) ** (1 / g["p"])
    xi = g["tip"] + (g["inn"] - g["tip"]) * (1 - sa ** g["q"]) ** (1 / g["q"])
    v = (xo - sx) / np.maximum(xo - xi, 1e-3)
    inside = (np.abs(s) < 1) & (v >= 0) & (v <= 1)
    # fibres run along the arc; each has its own span (inner ones end early,
    # feathering the inner edge) and brightness; some are dark separators
    NF = WAVE_NF
    fib = np.clip(np.floor(v * NF), 0, NF - 1).astype(int)
    vc = (fib + 0.5) / NF
    inner = np.clip(vc - 0.48, 0, None)
    top = 1 - inner * (0.8 + 1.6 * hash01(seed, fib, 1))
    bot = 1 - inner * (0.8 + 1.6 * hash01(seed, fib, 2))
    body = inside & np.where(s < 0, -s <= top, s <= bot)
    sep = body & (vc > 0.40) & (hash01(seed, fib, 3) < 0.16)
    chunk = np.floor((s + 1) * 4 + 2 * hash01(seed, fib, 4)).astype(int)
    damp = np.clip(0.25 + v, 0, 1)                  # crisp leading edge, streaky inside
    vb = (v + damp * ((hash01(seed, fib, 5) - 0.5) * 0.14 + (hash01(seed, fib, chunk) - 0.5) * 0.08)
          + 0.30 * sa ** 3)
    img = np.zeros((H, W, 4), np.uint8)
    bounds = np.array([hi for hi, _ in WAVE_BANDS])
    cols = np.array([c for _, c in WAVE_BANDS], np.uint8)
    img[body, :3] = cols[np.minimum(np.searchsorted(bounds, vb[body]), len(cols) - 1)]
    img[sep, :3] = WAVE_SEP
    img[body, 3] = 255
    # dark outline on the inner (trailing) side
    left_empty = ~shift(body, 0, 1)
    img[body & left_empty & (v > 0.35), :3] = WAVE_INNER
    for ring, (rgb, al) in zip(rings(body, len(WAVE_HALO)), WAVE_HALO):
        over(img, ring, rgb, al)
    # broken energy rims ahead of the leading edge, each with a faint glow
    dxo = sx - xo
    rchunk = np.floor((s + 1) * 9).astype(int)
    for i, (a0, a1, smax, c, al) in enumerate(WAVE_RIMS):
        rm = (dxo >= a0) & (dxo < a1) & (sa < smax) & (hash01(seed, rchunk, 50 + i) > 0.22)
        over(img, rings(rm, 1)[0] & (img[..., 3] == 0), WAVE_HALO[1][0], 90)
        over(img, rm, c, al)
    wave_particles(img, ox, oy, seed)
    return img, [l, t, r, b]


def wave_particles(img, ox, oy, seed):
    """Sparks ahead of / around the crescent, debris shards and speed lines behind."""
    g = WAVE_GEO
    H, W = img.shape[:2]

    def edge_x(s_, which):
        sa = min(abs(s_), 1.0)
        a, p = (g["out"], g["p"]) if which == "out" else (g["inn"], g["q"])
        return g["tip"] + (a - g["tip"]) * (1 - sa ** p) ** (1 / p)

    def at(sx_, s_):
        return int(math.floor(ox + sx_)), int(math.floor(oy + g["cy"] + s_ * g["R"]))

    spark = dict(c=(255, 255, 255), h=[(150, 230, 255)], v=[(150, 230, 255)], d=None)
    big = dict(c=(255, 255, 255), h=[(205, 245, 255), (90, 200, 255)], v=[(205, 245, 255), (90, 200, 255)],
               d=None)
    for i in range(36):
        s_ = (float(hash01(seed, i, 1)) * 2 - 1) * 0.95
        ahead = 2 + 22 * float(hash01(seed, i, 2)) ** 1.6
        x, y = at(edge_x(s_, "out") + ahead, s_)
        kind = float(hash01(seed, i, 3))
        if kind < 0.12:
            draw_star(img, x, y, big)
        elif kind < 0.3:
            draw_star(img, x, y, spark)
        elif kind < 0.65:
            ln = 2 + int(3 * float(hash01(seed, i, 4)))
            for j in range(ln):
                put_px(img, x - j, y, (255, 255, 255) if j == 0 else (150, 230, 255), 255 - 40 * j)
        else:
            put_px(img, x, y, (225, 250, 255))
    for i in range(10):          # debris shards trailing behind the inner edge
        s_ = (float(hash01(seed, i, 11)) * 2 - 1) * 0.8
        x, y = at(edge_x(s_, "in") - 4 - 18 * float(hash01(seed, i, 12)), s_)
        w = 2 + int(2 * float(hash01(seed, i, 13)))
        for j in range(w):
            put_px(img, x + j, y, (10, 24, 80))
            put_px(img, x + j, y + 1, (10, 24, 80))
        put_px(img, x + w - 1, y, (90, 200, 255))
    for i in range(7):           # speed lines behind the inner edge
        s_ = (float(hash01(seed, i, 21)) * 2 - 1) * 0.6
        x, y = at(edge_x(s_, "in") - 2, s_)
        ln = 10 + int(18 * float(hash01(seed, i, 22)))
        for j in range(ln):
            put_px(img, x - j, y, (60, 165, 255), int(220 * (1 - j / ln)) + 30)


# ==========================================================================
# main
# ==========================================================================
def render_character(bid, a0, group, annotated, rep, fx=None):
    """Reskin one character bitmap.  Returns (rgba, pad, purple copy or None).
    fx: SI_FX entry (超必杀 effects) or None for the plain reskin."""
    # ---- sword placement on the original, then canvas padding
    res0 = bid in RESAMPLED_SMALL
    cls0 = classify(a0, res0)
    heads0 = find_heads(a0, cls0, res0)
    specs0, how = sword_specs(bid, a0, cls0, heads0, annotated)
    if fx:
        specs0 = [si_spec(P, fx) for P in specs0]
    g = si_margin(fx) if fx else 0
    H0, W0 = a0.shape[:2]
    l = t = r = b = 0
    for P in specs0:
        part, _, x0, y0 = raster_sword(P)
        ys, xs = np.nonzero(part)
        if len(xs):
            l = max(l, -(xs.min() + x0) + g)
            t = max(t, -(ys.min() + y0) + g)
            r = max(r, xs.max() + x0 - (W0 - 1) + g)
            b = max(b, ys.max() + y0 - (H0 - 1) + g)
    pad = [int(l), int(t), int(r), int(b)]
    a = np.zeros((H0 + t + b, W0 + l + r, 4), np.uint8)
    a[t:t + H0, l:l + W0] = a0
    specs = [shift_spec(P, l, t) for P in specs0]
    # ---- reskin
    base, hat_layers, cls, heads, head_keep = process_character(a, bid, rep)
    if not rep["heads"]:
        raise SystemExit(f"{bid}: no head found in a character bitmap")
    hand_px = np.zeros(a.shape[:2], bool)
    hb = hand_blobs(cls, heads)
    for P in specs:
        for hx, hy, hm in hb:
            if math.hypot(hx - P["H"][0], hy - P["H"][1]) <= 3.5:
                hand_px |= hm
    hand_px &= base[..., 3] > 0
    tm = trail_mask(a) if (group or bid in PURPLE_COPY_IDS) else np.zeros(a.shape[:2], bool)
    combined = int(tm.sum()) >= 20
    rep["kind"] = "combined" if combined else "character"
    rep["trail_px"] = int(tm.sum())
    rep["sword"] = dict(source=how, pad=pad, swords=[
        dict(hand=[round(float(v), 1) for v in P["H"] - [l, t]],
             dir=[round(float(v), 3) for v in P["d"]], blade=P["Lb"], behind=P["behind"])
        for P in specs])
    effect = tm & np.all(base == a, -1)          # trail pixels the character pass left alone
    if fx:
        rep["si_fx"] = dict(fx)

    def finish(img):
        img = draw_swords(img, a, specs, cls, head_keep, hand_px)
        if fx:
            si_sword_fx(img, specs, effect, fx, bid)
        for hatm, col in hat_layers:
            img[hatm] = col[hatm]
        if fx and fx.get("glint"):
            x, y = si_eye(rep["heads"][0])
            draw_star(img, x, y, SI_GLINT[fx["glint"]])
            rep["si_eye"] = [x - l, y - t]
        return img

    main_img = base
    if combined and group:
        main_img = apply_trail(a, base, tm, BLUE_RAMP if group == "blue" else VIOLET_RAMP)
        if fx and fx.get("trail"):
            main_img = si_trail(main_img, effect, specs[0]["H"])
    out = finish(main_img.copy())
    purple = None
    if bid in PURPLE_COPY_IDS:
        pimg = apply_trail(a, base, tm, VIOLET_RAMP) if combined else base
        purple = finish(pimg.copy())
    assert out.shape == a.shape and out.dtype == np.uint8
    return out, pad, purple


def main():
    mp = json.loads((ROOT / "bankai_map.json").read_text(encoding="utf-8"))
    labels = mp["labels"]
    ids = sorted(int(i) for i in mp["all_bitmaps"])
    lab_of = {i: [l for l, d in labels.items() if i in d["bitmaps"]] for i in ids}
    OUT.mkdir(exist_ok=True)
    OUT_PURPLE.mkdir(exist_ok=True)
    # content keys of the annotated bitmaps (to reuse annotations on duplicates)
    annotated = {}
    for rid in SWORDS:
        if rid in ids:
            annotated[rid] = content_key(np.array(Image.open(BASE / f"{rid}.png").convert("RGBA")))
    report, pads, si_before = {}, {}, {}
    for bid in ids:
        a0 = np.array(Image.open(BASE / f"{bid}.png").convert("RGBA"))
        labs = [l for l in lab_of[bid] if l not in SKIP_LABELS] or lab_of[bid]
        in_blue = any(l in BLUE_LABELS for l in labs)
        in_violet = any(l in VIOLET_LABELS for l in labs)
        group = "blue" if in_blue else ("violet" if in_violet else None)
        rep = dict(labels=lab_of[bid], group=group, conflict=bool(in_blue and in_violet))
        if bid in EFFECT_ONLY:
            out = a0.copy()
            if group:
                out, rep["mode"] = recolor_effect(a0, BLUE_RAMP if group == "blue" else VIOLET_RAMP)
            rep["kind"] = "effect" if group else "unchanged"
            Image.fromarray(out, "RGBA").save(OUT / f"{bid}.png")
            report[str(bid)] = rep
            continue
        if bid in SI_WAVES:
            # 超必杀 wave: redrawn from scratch (no figure); the plain reskin is kept for the preview
            si_before[bid] = render_character(bid, a0, group, annotated, dict(rep))[:2]
            out, pad = render_wave(bid, a0.shape[:2])
            pads[str(bid)] = pad
            rep.update(kind="si-wave", si_wave=dict(shape_origin=list(WAVE_OFF[bid]), pad=pad))
            Image.fromarray(out, "RGBA").save(OUT / f"{bid}.png")
            report[str(bid)] = rep
            continue
        fx = SI_FX.get(bid)
        if fx:
            si_before[bid] = render_character(bid, a0, group, annotated, dict(rep))[:2]
        out, pad, purple = render_character(bid, a0, group, annotated, rep, fx)
        if any(pad):
            pads[str(bid)] = pad
        if purple is not None:
            Image.fromarray(purple, "RGBA").save(OUT_PURPLE / f"{bid}.png")
        Image.fromarray(out, "RGBA").save(OUT / f"{bid}.png")
        report[str(bid)] = rep
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    PADS.write_text(json.dumps(pads, indent=1), encoding="utf-8")
    make_sheet(ids, labels, lab_of, report, pads=pads)
    si_preview(si_before, pads)
    kinds = {}
    for r_ in report.values():
        kinds.setdefault((r_["kind"], r_["group"]), 0)
        kinds[(r_["kind"], r_["group"])] += 1
    for k, n in sorted(kinds.items(), key=str):
        print(f"{k[0]:10s} {str(k[1]):7s} {n}")
    print("conflicts (violet+blue -> blue):",
          [int(k) for k, r_ in report.items() if r_["conflict"]])
    print("padded:", len(pads), "ids")


# ==========================================================================
# review sheet
# ==========================================================================
def make_sheet(ids, labels, lab_of, report=None, path=SHEET, zoom=3, only=None,
               width=2400, out_dir=None, pads=None):
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
        row = [i for i in d["bitmaps"] if i in ids and i not in seen
               and (only is None or i in only)]
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
            pl, pt = pads.get(str(i), [0, 0, 0, 0])[:2]
            o = Image.new("RGBA", n.size, (0, 0, 0, 0))
            o.paste(o0, (pl, pt))
            bb = o.getbbox() or (0, 0, 1, 1)
            bb2 = n.getbbox() or bb
            bb = (max(0, min(bb[0], bb2[0]) - 2), max(0, min(bb[1], bb2[1]) - 2),
                  min(o.width, max(bb[2], bb2[2]) + 2), min(o.height, max(bb[3], bb2[3]) + 2))
            pair = []
            for im in (o, n):
                c = im.crop(bb)
                c = c.resize((c.width * zoom, c.height * zoom), Image.NEAREST)
                bg = Image.new("RGBA", c.size, BG)
                bg.alpha_composite(c)
                pair.append(bg)
            pw = max(pair[0].width * 2 + 6, 150)
            ph = pair[0].height + 18
            t = Image.new("RGBA", (pw, ph), (40, 44, 48, 255))
            t.paste(pair[0], (0, 18))
            t.paste(pair[1], (pair[0].width + 6, 18))
            kind = ""
            if report is not None:
                r = report[str(i)]
                kind = r["kind"] + (f"/{r['group']}" if r["group"] and r["kind"] != "character" else "")
            extra = [LABEL_EN.get(l, l) for l in lab_of[i] if l != lab]
            padtxt = f" pad{pads[str(i)]}" if str(i) in pads else ""
            cap = f"{i} {o0.width}x{o0.height} {kind}{padtxt}" + (f" +{','.join(extra)}" if extra else "")
            ImageDraw.Draw(t).text((2, 1), cap, fill=(255, 230, 90, 255), font=font)
            items.append(t)
        tiles.append((lab, items))
    x = y = rowh = 0
    places = []
    for lab, items in tiles:
        if places:
            y += rowh + 10
        places.append(("hdr", lab, 0, y))
        y += 26
        x, rowh = 0, 0
        for t in items:
            if x + t.width > width and x:
                x = 0
                y += rowh + 6
                rowh = 0
            places.append(("img", t, x, y))
            x += t.width + 10
            rowh = max(rowh, t.height)
    sheet = Image.new("RGBA", (width, y + rowh + 10), (24, 26, 30, 255))
    dr = ImageDraw.Draw(sheet)
    for kind, obj, px, py in places:
        if kind == "hdr":
            dr.text((4, py + 2), f"== {LABEL_EN.get(obj, obj)} ==", fill=(140, 220, 255, 255), font=hfont)
        else:
            sheet.paste(obj, (px, py))
    sheet.convert("RGB").save(path, optimize=True)
    return path


# ==========================================================================
# 超必杀 preview: work/mihawk/si_preview.png
# ==========================================================================
SI_PREVIEW = ROOT / "si_preview.png"
FACE2 = ROOT / "ui" / "face2.png"
SI_CHAR_POS = (-71.95, -90.45)       # character shapes (bitmap 0,0) in sprite 1180
SI_WAVE_TY = -59.6                   # wave sprite 1038 in sprite 1180 (y; x per frame)
# the 4 placements of the wave shape inside sprite 1038: scale x, y, translate x, y
SI_WAVE_SUB = [(1.0, 1.6887054, 49.05, -75.95), (0.8293762, 0.9710083, 15.75, -21.15),
               (0.6309204, 0.42300415, -6.5, 21.0), (0.6309204, 0.2270813, -42.75, 36.65)]
SI_WAVE_K = 1.3                      # extra uniform wave scale applied by tools/mihawk.py
# shape rects of 1033 / 1036 before padding (old crop windows, shape px)
SI_OLD_CROP = {1032: (0.0, 0.0, 126.0, 148.0), 1035: (-5.35, -0.05, 150.3, 147.95)}
SI_SEQ = [("windup", [(622, 1012), (624, 1014), (626, 1016), (628, 1018)]),
          ("charge (sprite 1026 loop)", [(630, 1020), (632, 1022), (634, 1024)]),
          ("slash", [(648, 1028), (650, 1040), (652, 1043), (654, 1045)])]
# in-context frames: (frame, character bitmap, wave bitmap, wave x-scale, wave x)
SI_CONTEXT = [(648, 1028, 1032, 1.0, -31.55), (650, 1040, 1035, 1.3092499, 18.1),
              (661, 1045, 1032, 2.4516907, 201.45)]


def _affine(img, M, size):
    """Premultiplied bilinear affine warp (Flash smooths scaled bitmap fills)."""
    Mi = np.linalg.inv(M)
    a = img.astype(float) / 255.0
    pm = np.dstack([a[..., :3] * a[..., 3:], a[..., 3:]])
    ch = [np.asarray(Image.fromarray(pm[..., i].astype(np.float32), "F").transform(
        size, Image.AFFINE, tuple(Mi[:2].ravel()), Image.BILINEAR)) for i in range(4)]
    o = np.stack(ch, -1)
    al = o[..., 3:]
    rgb = np.where(al > 1e-4, o[..., :3] / np.maximum(al, 1e-4), 0)
    return Image.fromarray(np.clip(np.dstack([rgb, al]) * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")


def _T(tx, ty):
    return np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1.0]])


def _S(sx, sy):
    return np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1.0]])


def _stage_bg(w, h, floor_y):
    """Dark game-like backdrop: night-blue gradient, a stone floor below floor_y."""
    y = np.arange(h)[:, None, None] / max(h - 1, 1)
    sky = np.array([22, 24, 40]) * (1 - y) + np.array([44, 46, 64]) * y
    im = np.repeat(sky, w, axis=1)
    if floor_y < h:
        f0 = max(int(floor_y), 0)
        fy = np.arange(h - f0)[:, None, None] / max(h - f0, 1)
        im[f0:] = np.array([58, 52, 50]) * (1 - fy) + np.array([32, 28, 30]) * fy
        im[f0:f0 + 1] = (84, 76, 70)
    return Image.fromarray(np.clip(im, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def _wave_layer(img, pad, bid, xs, x0, view, size, zoom, crop=None):
    """Sprite 1038 (4 nested copies) placed in sprite-1180 coordinates."""
    if crop is not None:          # old cropped shape window (before padding)
        img = img.copy()
        H, W = img.shape[:2]
        ox, oy = WAVE_OFF[bid][0] + pad[0], WAVE_OFF[bid][1] + pad[1]
        yy, xx = np.mgrid[0:H, 0:W]
        keep = ((xx + 0.5 - ox >= crop[0]) & (xx + 0.5 - ox <= crop[2])
                & (yy + 0.5 - oy >= crop[1]) & (yy + 0.5 - oy <= crop[3]))
        img[~keep] = 0
    ox, oy = WAVE_OFF[bid][0] + pad[0], WAVE_OFF[bid][1] + pad[1]
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    for a, d, tx, ty in SI_WAVE_SUB:
        M = (_S(zoom, zoom) @ _T(-view[0], -view[1]) @ _T(x0, SI_WAVE_TY) @ _S(xs * SI_WAVE_K, SI_WAVE_K)
             @ _T(tx, ty) @ _S(a, d) @ _T(-ox, -oy))
        out.alpha_composite(_affine(img, M, size))
    return out


def _char_layer(img, pad, view, size, zoom):
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    im = Image.fromarray(img, "RGBA")
    if zoom != 1:
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    x = round((SI_CHAR_POS[0] - pad[0] - view[0]) * zoom)
    y = round((SI_CHAR_POS[1] - pad[1] - view[1]) * zoom)
    cx, cy = max(0, -x), max(0, -y)              # clip negative offsets
    out.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x + cx, y + cy))
    return out


def _single_wave(img, pad, bid, xs, k, zoom, window, crop=None):
    """One wave bitmap (no nesting) scaled (xs*k, k) about its shape origin."""
    x0, y0, x1, y1 = window
    size = (int(round((x1 - x0) * xs * k * zoom)), int(round((y1 - y0) * k * zoom)))
    if crop is not None:
        return _wave_crop_single(img, pad, bid, xs, k, zoom, window, crop, size)
    ox, oy = WAVE_OFF[bid][0] + pad[0], WAVE_OFF[bid][1] + pad[1]
    M = _S(zoom, zoom) @ _S(xs * k, k) @ _T(-x0, -y0) @ _T(-ox, -oy)
    bg = _stage_bg(size[0], size[1], size[1] + 1)
    bg.alpha_composite(_affine(img, M, size))
    return bg


def _wave_crop_single(img, pad, bid, xs, k, zoom, window, crop, size):
    img = img.copy()
    H, W = img.shape[:2]
    ox, oy = WAVE_OFF[bid][0] + pad[0], WAVE_OFF[bid][1] + pad[1]
    yy, xx = np.mgrid[0:H, 0:W]
    keep = ((xx + 0.5 - ox >= crop[0]) & (xx + 0.5 - ox <= crop[2])
            & (yy + 0.5 - oy >= crop[1]) & (yy + 0.5 - oy <= crop[3]))
    img[~keep] = 0
    return _single_wave(img, pad, bid, xs, k, zoom, window)


def si_preview(before, pads, path=SI_PREVIEW):
    """S+I sequence on a dark stage: new vs before (plain reskin), 2x zoom;
    wave bitmaps at 1x / 1.3x / 2.45x1.3 (2x zoom); in-context frames at 1x."""
    try:
        font = ImageFont.truetype(str(FONT), 13)
        hfont = ImageFont.truetype(str(FONT), 18)
    except OSError:
        font = hfont = ImageFont.load_default()
    new = {}
    for bid in [b_ for _, row in SI_SEQ for _, b_ in row] + list(SI_WAVES):
        new[bid] = (np.array(Image.open(OUT / f"{bid}.png").convert("RGBA")), pads.get(str(bid), [0, 0, 0, 0]))
    W_SHEET = 2440
    blocks = []                       # ("title", text) | ("row", [(img, caption), ...])

    # --- sequence flipbook (2x): fixed window in sprite-1180 px
    view, vs, Z = (-84, -104), (166, 140), 2
    for name, row in SI_SEQ:
        for tag, src in (("new", new), ("before", before)):
            items = []
            for fr, bid in row:
                img, pad = src[bid]
                bg = _stage_bg(vs[0] * Z, vs[1] * Z, (24 - view[1]) * Z)
                bg.alpha_composite(_char_layer(img, pad, view, bg.size, Z))
                fx = SI_FX.get(bid, {})
                cap = f"{fr} {bid} {tag}" + (f"  k{fx['k']:.2f} glow{fx['glow']}" + (
                    f" glint{fx['glint']}" if fx.get("glint") else "") if tag == "new" else "")
                items.append((bg, cap))
            if name.startswith("charge") and tag == "new" and FACE2.exists():
                f2 = Image.open(FACE2).convert("RGBA")
                f2 = f2.resize((f2.width * Z, f2.height * Z), Image.NEAREST)
                bg = Image.new("RGBA", (vs[0] * Z * 3 // 2, vs[1] * Z), (0, 0, 0, 255))
                bg.alpha_composite(f2, ((bg.width - f2.width) // 2, (bg.height - f2.height) // 2))
                items.insert(0, (bg, "625 cut-in face2 (black screen)"))
            blocks.append(("title", f"S+I {name} - {tag} (2x)"))
            blocks.append(("row", items))

    # --- wave bitmaps alone (2x): 1x, 1.3x, 2.45x1.3 stretch
    win = (-48.0, -8.0, 142.0, 156.0)            # shape px
    for bid in SI_WAVES:
        img, pad = new[bid]
        bimg, bpad = before[bid]
        crop = SI_OLD_CROP[bid]
        blocks.append(("title", f"wave {bid} (shape px {win[0]:.0f}..{win[2]:.0f}): new | before, 2x zoom"))
        blocks.append(("row", [(_single_wave(img, pad, bid, 1.0, 1.0, 2, win), f"{bid} new 1x"),
                               (_single_wave(img, pad, bid, 1.0, SI_WAVE_K, 2, win), f"{bid} new 1.3x"),
                               (_single_wave(bimg, bpad, bid, 1.0, 1.0, 2, win, crop), f"{bid} before 1x"),
                               (_single_wave(bimg, bpad, bid, 1.0, SI_WAVE_K, 2, win, crop),
                                f"{bid} before 1.3x")]))
        blocks.append(("row", [(_single_wave(img, pad, bid, 2.45, SI_WAVE_K, 2, win), f"{bid} new 2.45x1.3 (x) / 1.3 (y)")]))
        blocks.append(("row", [(_single_wave(bimg, bpad, bid, 2.45, SI_WAVE_K, 2, win, crop),
                                f"{bid} before 2.45x1.3 (x) / 1.3 (y)")]))

    # --- in-context frames (1x, game scale): character + sprite 1038 (4 nested copies, x1.3)
    view, vs = (-110, -240), (720, 420)
    blocks.append(("title", "in context, 1x game scale (wave sprite 1038 = 4 nested copies, with the x1.3 "
                            "placement scale; vector streak shapes 1034/1037 not drawn): new | before"))
    for fr, cb, wb, xs, wx in SI_CONTEXT:
        items = []
        for tag, src in (("new", new), ("before", before)):
            bg = _stage_bg(vs[0], vs[1], 24 - view[1])
            wimg, wpad = src[wb]
            bg.alpha_composite(_wave_layer(wimg, wpad, wb, xs, wx, view, vs, 1,
                                           None if tag == "new" else SI_OLD_CROP[wb]))
            cimg, cpad = src[cb]
            bg.alpha_composite(_char_layer(cimg, cpad, view, vs, 1))
            items.append((bg, f"frame {fr}: {cb} + wave {wb} x-scale {xs:.2f} - {tag}"))
        blocks.append(("row", items))

    # --- layout
    y, places = 6, []
    for kind, obj in blocks:
        if kind == "title":
            places.append(("t", obj, 8, y))
            y += 26
            continue
        x, rowh = 8, 0
        for im, cap in obj:
            if x + im.width > W_SHEET and x > 8:
                x, y = 8, y + rowh + 22
                rowh = 0
            places.append(("i", (im, cap), x, y))
            x += im.width + 12
            rowh = max(rowh, im.height)
        y += rowh + 26
    sheet = Image.new("RGB", (W_SHEET, y + 6), (12, 12, 16))
    dr = ImageDraw.Draw(sheet)
    for kind, obj, px, py in places:
        if kind == "t":
            dr.text((px, py + 2), obj, fill=(140, 220, 255), font=hfont)
        else:
            im, cap = obj
            sheet.paste(im.convert("RGB"), (px, py))
            dr.text((px + 2, py + im.height + 2), cap, fill=(255, 230, 90), font=font)
    sheet.save(path, optimize=True)
    return path


if __name__ == "__main__":
    main()
