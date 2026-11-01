#!/usr/bin/env python3
"""Splash + title art for 블리치 VS 나루토 VS 원피스 (BVN 2.6 한글판, three-anime crossover) -- v3.

Run:   tools/venv/bin/python work/design/render_v3.py
Deps:  Pillow, numpy. Deterministic (fixed seeds, no clocks). Reuses the text/raster helpers of render_ui.py (v2).

Outputs (work/design/out/):
  splash_600x400.png     opaque (RGBA, alpha 255): preloader backdrop + intro fade card
                         (the v2 splash is kept once as work/design/out_v2_splash.png)
  title_bg_600x400.png   opaque (RGBA, alpha 255): the complete title screen (Ichigo + Naruto + Luffy + baked logo)
  title_veil_616.png     373x171, replacement for bitmap 616 (the carousel's white veil): the title art itself under
                         616's alpha, so it hides the neighbouring menu labels without painting a white bar. Named so
                         that tools/build.py does NOT pick it up by itself (rename to 616.png, or hide shape 617).
  preview_v3.png         review sheet: splash + loader mock, title + live-element mocks, zones, 2x views

Art sources (work/op/art/): ichigo_title_2x.png, naruto_title_2x.png (BVN title, 2x), luffy_title.png (OP title, 1x).
Live game elements drawn over the title (kept calm here):
  menu carousel x 200-420, y 255-395 (labels tinted (255,G,255), centred on x~304); white veil 616 at (123,230)
  buttons 업데이트 / 다른 게임 (yellow) x 480-600, y 5-80;  "V 2.6" at (5,361);  status bar y >= 381.
Loader (sprite 534 at x1.056 +(116.8,48.5)) draws its text at stage y ~300-375 and its bar at y 385-392, x 17-577.
"""
import math
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_ui import (FONTS, IMG, OUT, SHOTS, BAR_Y, MENU_SLOTS, HAH, Canvas, Text, blur, grid,  # noqa: E402
                       loader_mock, seal_mask, shape_mask, tint_menu, vramp)

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "work" / "op" / "art"
W, H = 600, 400

# ---- palette: dark base, one accent temperature per faction -----------------------------------------------
NIGHT_TOP, NIGHT, NIGHT_LOW = (23, 25, 46), (15, 15, 35), (7, 7, 16)      # #0F0F23 at the centre
MOON, ICE = (236, 241, 248), (160, 196, 232)                            # Bleach: cold moon-white / ice blue
EMBER_HI, EMBER = (253, 166, 84), (249, 115, 22)                        # Naruto: #F97316 family
RED_HI, RED = (246, 66, 98), (196, 18, 58)                              # One Piece: straw-hat red (#E11D48 family)
GOLD = (250, 204, 21)                                                   # ... and straw gold #FACC15
KEY = (6, 6, 14)                                                        # ink keyline behind the logo
SEAL = (190, 36, 29)                                                    # the edition stamp (as v2)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def poly_mask(pts):
    return shape_mask(W, H, lambda d, s: d.polygon([(x * s, y * s) for x, y in pts], fill=255))


# ---------------------------------------------------------------------------------------------------------
# character art: clean-up in source space, then premultiplied float resampling (no halos from resizing)
# ---------------------------------------------------------------------------------------------------------
class Art:
    def __init__(self, name):
        a = np.asarray(Image.open(ART / name).convert("RGBA"), np.float32) / 255.0
        self.rgb, self.a = a[..., :3].copy(), a[..., 3].copy()
        self.h, self.w = self.a.shape
        self.y, self.x = np.mgrid[0:self.h, 0:self.w].astype(np.float32) + 0.5

    def whiteness(self, lo=0.55, hi=0.80, sat=0.28):
        lum = self.rgb @ np.array([0.299, 0.587, 0.114], np.float32)
        s = self.rgb.max(-1) - self.rgb.min(-1)
        return smoothstep(lo, hi, lum) * np.clip(1.0 - s / sat, 0.0, 1.0)

    def bleed(self, clean, radius):
        """Colour of nearby 'clean' pixels (normalised convolution), for repainting contaminated ones."""
        num = np.dstack([blur(self.rgb[..., k] * clean, radius) for k in range(3)])
        den = blur(clean, radius)[..., None]
        return num / np.maximum(den, 1e-4), den[..., 0]

    def edge_band(self, px):
        """1 where a pixel lies within `px` source pixels of transparency."""
        solid = Image.fromarray(((self.a > 0.5) * 255).astype(np.uint8), "L")
        er = solid.filter(ImageFilter.MinFilter(2 * px + 1))
        return 1.0 - np.asarray(er, np.float32) / 255.0

    def place(self, s, anchor, at, rot=0.0):
        """Full-canvas (rgb, a): source point `anchor` lands on canvas point `at`, scaled by s, rotated by
        `rot` degrees counter-clockwise around that point."""
        nw, nh = round(self.w * s), round(self.h * s)
        sx, sy = nw / self.w, nh / self.h
        pm = [self.rgb[..., k] * self.a for k in range(3)] + [self.a]
        th = math.radians(rot)
        co, si = math.cos(th), math.sin(th)
        ax, ay = anchor[0] * sx, anchor[1] * sy
        tx, ty = at
        data = (co, -si, ax - co * tx + si * ty, si, co, ay - si * tx - co * ty)
        ch = []
        for c in pm:
            im = Image.fromarray(c.astype(np.float32), "F").resize((nw, nh), Image.LANCZOS)
            im = im.transform((W, H), Image.Transform.AFFINE, data, resample=Image.BICUBIC)
            ch.append(np.asarray(im, np.float32))
        a = np.clip(ch[3], 0.0, 1.0)
        rgb = np.dstack(ch[:3]) / np.maximum(a, 1e-4)[..., None]
        return np.clip(rgb, 0.0, 1.0), a


def ichigo_art():
    """Hollow-mask Ichigo, used as a bust. The cut-out was made on white: the coat carries white contour lines
    and white flecks where the backdrop showed through. Those are repainted from the surrounding coat (outline
    band + ragged hem only); mask, sash and guard are left alone; the feathered hair tips get the hair colour
    instead of the white they were feathered into. The outline is opened to drop matte spurs, and the
    semi-transparent sword arm + motion-blurred sweep are dissolved (they only read as a grey veil)."""
    A = Art("ichigo_title_2x.png")
    x, y = A.x, A.y
    w = A.whiteness(0.56, 0.80, 0.30)
    mask = (((x - 822) / 62) ** 2 + ((y - 140) / 80) ** 2 < 1).astype(np.float32)
    hair = (((x - 835) / 95) ** 2 + ((y - 95) / 75) ** 2 < 1).astype(np.float32)
    sash = shape_mask_src(A, [(846, 352), (1010, 352), (1050, 470), (975, 520), (880, 515), (846, 420)])
    guard = smoothstep(600.0, 560.0, x) * smoothstep(185.0, 160.0, y)
    protect = np.clip(blur(np.maximum(mask, sash), 2.0) + guard, 0, 1)
    band = blur(A.edge_band(4), 1.5)
    hem = smoothstep(455.0, 490.0, y) * (1.0 - sash)
    zone = np.clip(np.maximum(band, hem), 0, 1) * (1.0 - protect)
    clean = ((w < 0.02) & (A.a > 0.85)).astype(np.float32)
    col, den = A.bleed(clean, 4.0)
    coat = np.array([0.05, 0.053, 0.065], np.float32)
    t = np.clip(den * 4, 0, 1)[..., None]
    col = col * t + coat * (1 - t)
    k = (w * zone)[..., None]
    A.rgb = A.rgb * (1 - k) + col * k
    # semi-transparent rim pixels: unmix from the white matte they were cut on (never brighten)
    sleeve = shape_mask_src(A, [(560, 50), (700, 36), (800, 66), (810, 150), (720, 182), (600, 172), (556, 130)])
    hair_soft = blur(hair, 4.0)
    rim = ((A.a < 0.98) & (A.a > 0.02)).astype(np.float32) * (1.0 - protect) * (1.0 - blur(sleeve, 3.0))
    rim = rim * (1.0 - hair_soft)
    un = np.clip((A.rgb - (1.0 - A.a[..., None])) / np.maximum(A.a[..., None], 0.05), 0, 1)
    A.rgb = A.rgb * (1 - rim[..., None]) + np.minimum(un, A.rgb) * rim[..., None]
    # the hair tips were feathered into the white backdrop: carry the opaque hair colour out into them
    hair_core = ((A.a > 0.85) & (hair > 0.5) & (A.rgb[..., 0] > A.rgb[..., 2] + 0.12)).astype(np.float32)
    hcol, hden = A.bleed(hair_core, 7.0)
    soft = (np.clip(1.0 - A.a, 0, 1) * hair_soft * np.clip(hden * 6, 0, 1))[..., None]
    A.rgb = A.rgb * (1 - soft) + hcol * soft
    # tidy the outline: a morphological opening drops the 1-3 px spurs and slivers of the hand-cut matte
    av = Image.fromarray((A.a * 255 + 0.5).astype(np.uint8), "L")
    opened = av.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(0.8))
    opened = np.asarray(opened, np.float32) / 255.0
    fine = np.clip(protect + blur(hair, 2.0), 0, 1)
    A.a = A.a * fine + np.minimum(A.a, opened) * (1 - fine)
    # the hakama fold under the mask ends in brush spikes: round them off with a wide opening
    av = Image.fromarray((A.a * 255 + 0.5).astype(np.uint8), "L")
    wide = av.filter(ImageFilter.MinFilter(15)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(1.2))
    fold = blur(shape_mask_src(A, [(690, 215), (880, 215), (880, 330), (690, 330)]), 6.0)
    A.a = A.a * (1 - fold) + np.minimum(A.a, np.asarray(wide, np.float32) / 255.0) * fold
    # crop to a bust: the ghost sword arm and the sweep are dissolved; head, hair, shoulders and far arm stay
    arm = np.maximum(smoothstep(748.0, 772.0, x), mask) + smoothstep(232.0, 262.0, y) * smoothstep(640.0, 700.0, x)
    A.a = A.a * np.clip(arm, 0, 1)
    return A


def shape_mask_src(A, pts):
    im = Image.new("L", (A.w, A.h), 0)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(1.0)), np.float32) / 255.0


def luffy_art():
    """Luffy: remove the ~2 px white matte rim outside his ink line, drop the free-floating smoke and dissolve
    the flat crop at the bottom of the source into the ground."""
    A = Art("luffy_title.png")
    w = A.whiteness(0.50, 0.78, 0.26)
    band = A.edge_band(3)
    smoke_zone = smoothstep(150.0, 205.0, A.y) * smoothstep(60.0, 120.0, A.x)
    halo = w * band * (1.0 - smoke_zone)
    a = A.a * (1.0 - halo)
    # the black ink line is now the edge: give it back a soft half-pixel of anti-aliasing
    a_soft = np.minimum(a, blur(a, 0.6))
    A.a = a * (1.0 - band) + a_soft * band
    # smoke: drop it where it floats over nothing (semi-transparent white), keep the streaks across the skin;
    # the flat crop at the bottom of the source dissolves into the ground
    A.a = A.a * (1.0 - w * (A.a < 0.97) * smoothstep(60.0, 110.0, A.y))
    A.a = A.a * (1.0 - w * smoothstep(170.0, 215.0, A.y) * 0.95)
    A.a = A.a * smoothstep(262.0, 205.0, A.y)
    return A


def naruto_art():
    """Sage-mode Naruto: a clean cut-out (dark edges, soft rasengan glow); used as is."""
    return Art("naruto_title_2x.png")


# ---------------------------------------------------------------------------------------------------------
# logo lockup: 블리치 / VS 나루토 / VS 원피스, staggered down a diagonal
# ---------------------------------------------------------------------------------------------------------
NAMES = [("블리치", (MOON, ICE)), ("나루토", (EMBER_HI, EMBER)), ("원피스", (RED_HI, RED))]


def paint_logo(cv, x0, y0, cap, lead, stagger, vs_cap, keyline=2.4):
    """Paint the lockup with its top-left ink at (x0, y0). Returns the Text objects."""
    texts = []
    for i, (name, (top, bot)) in enumerate(NAMES):
        t = Text(name, HAH(900), cap, tracking=cap * 0.03).at(left=x0 + i * stagger, top=y0 + i * lead)
        texts.append(t)
    vss = []
    for i in (1, 2):
        t = texts[i]
        v = Text("VS", HAH(800), vs_cap, ref="V", tracking=vs_cap * 0.12)
        v.at(right=t.left - cap * 0.20, cy=t.top + cap * 0.52)
        vss.append(v)
    ink = np.zeros((H, W), np.float32)
    for t in texts:
        ink = np.maximum(ink, t.mask(W, H, stroke=keyline))
    for v in vss:
        ink = np.maximum(ink, v.mask(W, H, stroke=keyline * 0.8))
    cv.paint(KEY, ink, 0.92)
    for t, (name, (top, bot)) in zip(texts, NAMES):
        cv.paint(vramp(W, H, [(t.top, top), (t.bottom, bot)]), t.mask(W, H))
    for v in vss:
        cv.paint(MOON, v.mask(W, H), 0.80)
    return texts, vss


# ---------------------------------------------------------------------------------------------------------
# title 600x400
# ---------------------------------------------------------------------------------------------------------
MENU_BOX = (200, 255, 420, 395)
BTN_BOX = (480, 5, 600, 80)


def menu_shield(feather=16.0):
    """Soft mask of the carousel zone, used to dissolve character art where menu labels will sit."""
    x, y = grid(W, H)
    x0, y0, x1, y1 = MENU_BOX
    mx = smoothstep(x0 - feather, x0 + feather * 0.5, x) * smoothstep(x1 + feather, x1 - feather * 0.5, x)
    my = smoothstep(y0 - feather * 1.2, y0 + 2, y)
    return mx * my


# placements: (scale, source anchor, canvas point, rotation)  anchors = face centres in the source art
ICHIGO_T = (0.88, (815, 140), (512, 179), 0.0)
LUFFY_T = (0.84, (205, 135), (330, 132), 9.0)
NARUTO_T = (0.68, (450, 150), (92, 198), -10.0)

SLANT = 0.12     # every block leans the same way: dx per dy (rises to the right)


def para(xt0, xt1, y0, y1):
    """Parallelogram block: top edge x0..x1 at y0, sheared left by SLANT toward y1."""
    k = SLANT * (y1 - y0)
    return [(xt0, y0), (xt1, y0), (xt1 - k, y1), (xt0 - k, y1)]


def edge_line(xt, y0, y1, width):
    """A crisp keyline along a slanted block edge whose top is at (xt, y0)."""
    k = SLANT * (y1 - y0)
    return poly_mask([(xt - width / 2, y0), (xt + width / 2, y0), (xt + width / 2 - k, y1), (xt - width / 2 - k, y1)])


# three panels: Naruto (ember, low left), Luffy (crimson, high centre), Ichigo (moonlit steel, right)
PANEL_N = (-40, 176, 172, 400)
PANEL_L = (204, 450, 0, 236)
PANEL_I = (452, 640, 88, 400)


def paint_panels(cv):
    n, l, i = PANEL_N, PANEL_L, PANEL_I
    cv.paint(vramp(W, H, [(n[2], (104, 42, 10)), (400, (30, 12, 6))]), poly_mask(para(*n)))
    cv.paint(vramp(W, H, [(0, (96, 12, 36)), (l[3], (44, 6, 22))]), poly_mask(para(*l)))
    panel_i = poly_mask(para(*i))
    # moonlit steel: the cold light falls from the top of Ichigo's panel
    cv.paint(vramp(W, H, [(i[2], (204, 219, 238)), (i[2] + 40, (160, 180, 210)), (i[2] + 160, (84, 104, 140)),
                          (400, (26, 32, 52))]), panel_i)
    # keylines: each block is signed on one edge in its faction accent
    cv.paint(EMBER, edge_line(n[1], n[2], 400, 2.0))
    cv.paint(GOLD, edge_line(l[0], l[2], l[3], 1.6))
    cv.paint(MOON, edge_line(i[0], i[2], 400, 2.0))


def render_title(logo=True):
    x, y = grid(W, H)
    cv = Canvas(W, H, vramp(W, H, [(0, NIGHT_TOP), (190, NIGHT), (400, NIGHT_LOW)]))
    paint_panels(cv)

    # --- characters: Ichigo (right), Luffy (centre, high), Naruto (left, foreground)
    shield = menu_shield()
    irgb, ia = ichigo_art().place(*ICHIGO_T)
    # his body is clipped by his own panel (only the head breaks out above it)
    clip = np.maximum(poly_mask(para(*PANEL_I)), smoothstep(196.0, 180.0, y) * smoothstep(440.0, 452.0, x))
    irgb = irgb * (1.0 - 0.88 * smoothstep(322.0, 376.0, y))[..., None]      # falls into shadow, obi included
    cv.paint(irgb, ia * clip * (1 - shield))
    cv.paint(*luffy_art().place(*LUFFY_T))
    nrgb, na = naruto_art().place(*NARUTO_T)
    cv.paint(nrgb, na * (1 - shield))
    # calm the corner under the game's "V 2.6"
    cv.paint(NIGHT_LOW, ellipse(0, 400, 120, 70) * 0.55)

    # --- logo
    if logo:
        paint_logo(cv, 22, 18, 40.0, 56.0, 34.0, 12.0)

    # --- material: fine grain
    rng = np.random.default_rng(11)
    cv.rgb += rng.normal(0.0, 1.2 / 255.0, (H, W))[..., None].astype(np.float32)
    cv.a[:] = 1.0
    return cv.image()


def ellipse(cx, cy, rx, ry):
    x, y = grid(W, H)
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    return smoothstep(1.0, 0.0, d)


# ---------------------------------------------------------------------------------------------------------
# splash 600x400: the line-up. Same slanted blocks as the title, one panel per fighter, each name set under
# its fighter. Everything below y ~290 stays dark: the loader writes there.
# ---------------------------------------------------------------------------------------------------------
SP_TOP, SP_BOT = 0, 214
SP_PANELS = [(-40, 204), (212, 404), (412, 660)]          # top-edge x ranges (Ichigo | Naruto | Luffy)
LOADER_BOX = (150, 295, 450, 395)


def render_splash():
    x, y = grid(W, H)
    cv = Canvas(W, H, vramp(W, H, [(0, NIGHT_TOP), (200, NIGHT), (400, (6, 6, 14))]))
    masks = [poly_mask(para(x0, x1, SP_TOP, SP_BOT)) for x0, x1 in SP_PANELS]
    fills = [
        vramp(W, H, [(0, (204, 219, 238)), (36, (160, 180, 210)), (SP_BOT, (60, 76, 106))]),
        vramp(W, H, [(0, (128, 52, 12)), (SP_BOT, (44, 16, 6))]),
        vramp(W, H, [(0, (110, 14, 42)), (SP_BOT, (44, 6, 22))]),
    ]
    for m, f in zip(masks, fills):
        cv.paint(f, m)

    # fighters, each clipped by its own panel
    ich = ichigo_art().place(1.0, (815, 140), (88, 116), 0.0)
    nar = naruto_art().place(0.86, (450, 150), (302, 104), -6.0)
    luf = luffy_art().place(1.0, (205, 135), (486, 136), 6.0)
    for (rgb, a), m in zip((ich, nar, luf), masks):
        rgb = rgb * (1.0 - 0.55 * smoothstep(150.0, SP_BOT, y))[..., None]     # each panel darkens toward its base
        cv.paint(rgb, a * m)
    # each panel's base is signed with its faction accent
    k = SLANT * (SP_BOT - SP_TOP)
    for (x0, x1), col in zip(SP_PANELS, (MOON, EMBER, GOLD)):
        cv.paint(col, poly_mask([(x0 - k, SP_BOT - 1.0), (x1 - k, SP_BOT - 1.0), (x1 - k, SP_BOT + 1.0),
                                 (x0 - k, SP_BOT + 1.0)]), 0.95)

    # names under their fighters, VS on the gutters
    cap, top = 34.0, SP_BOT + 22.0
    centres = []
    for (x0, x1) in SP_PANELS:
        k = SLANT * (SP_BOT - SP_TOP)
        lo, hi = max(x0 - k, 0.0), min(x1 - k, float(W))
        centres.append((lo + hi) / 2.0)
    texts = [Text(n, HAH(900), cap, tracking=cap * 0.03).at(cx=c, top=top) for (n, _), c in zip(NAMES, centres)]
    vss = [Text("VS", HAH(800), 11.0, ref="V", tracking=1.3).at(cx=(texts[i].right + texts[i + 1].left) / 2.0,
                                                                cy=texts[i].top + cap * 0.52) for i in (0, 1)]
    for t, (name, (c0, c1)) in zip(texts, NAMES):
        cv.paint(vramp(W, H, [(t.top, c0), (t.bottom, c1)]), t.mask(W, H))
    for v in vss:
        cv.paint(MOON, v.mask(W, H), 0.80)

    # whispered credit (left) and the edition seal (right), both outside the loader's column
    rea = Text("REA PROJECT", HAH(600), 8.0, ref="H", tracking=3.0).at(left=24, top=texts[0].bottom + 26)
    cv.paint(MOON, rea.mask(W, H), 0.55)
    ver = Text("2.6", HAH(800), 13.0, ref="2", tracking=0.5)
    han = Text("한글판", HAH(900), 12.0, tracking=1.0)
    padx, pady, gap = 7.0, 5.0, 9.0
    right = 576.0
    box_l = right - (han.w + 2 * padx)
    han.at(left=box_l + padx, cy=rea.cy)
    ver.at(right=box_l - gap, cy=rea.cy)
    box = (box_l, han.top - pady, right, han.bottom + pady)
    cv.paint(MOON, ver.mask(W, H), 0.94)
    cv.paint(SEAL, seal_mask(W, H, box, seed=31))
    cv.paint(MOON, han.mask(W, H), 0.97)

    rng = np.random.default_rng(7)
    cv.rgb += rng.normal(0.0, 1.2 / 255.0, (H, W))[..., None].astype(np.float32)
    cv.a[:] = 1.0
    return cv.image()


# ---------------------------------------------------------------------------------------------------------
# carousel veil (bitmap 616, 373x171): the game lays it over the carousel to fade the labels above and below
# the selected one. The original is white. This variant is the title art itself, sampled exactly where the veil
# lands (sprite 620 at (242.95, 309.65), bitmap offset (-120, -79.25)), with 616's alpha kept only over the
# menu well: it hides the neighbouring labels and is otherwise invisible.
# ---------------------------------------------------------------------------------------------------------
VEIL_XY = (242.95 - 120.0, 309.65 - 79.25)


def render_veil(title):
    src = Image.open(IMG / "616.png").convert("RGBA")
    vw, vh = src.size
    va = np.asarray(src, np.float32)[..., 3] / 255.0
    ox, oy = VEIL_XY
    tb = np.asarray(title.convert("RGB"), np.float32) / 255.0
    ch = [np.asarray(Image.fromarray(tb[..., k], "F").transform(
        (vw, vh), Image.Transform.AFFINE, (1, 0, ox, 0, 1, oy), resample=Image.BILINEAR), np.float32) for k in range(3)]
    rgb = np.dstack(ch)
    sx = np.arange(vw, dtype=np.float32) + 0.5 + ox
    window = smoothstep(176.0, 200.0, sx) * smoothstep(444.0, 420.0, sx)
    a = va * window[None, :]
    arr = np.dstack([rgb, a])
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------------------------------------------------
# previews
# ---------------------------------------------------------------------------------------------------------
NANUM_B = FONTS / "NanumGothic-Bold.ttf"


def title_mock(title, veil, white_veil=False):
    """The title as the game shows it at rest: carousel labels (v2 bitmaps, tinted (255,G,255)) with the veil on
    top, the yellow buttons, the version text and the status bar (taken from the Korean build screenshot)."""
    m = title.convert("RGBA").copy()
    for i, x, y in MENU_SLOTS:
        lab = Image.open(OUT / f"{i}.png").convert("RGBA")
        m.alpha_composite(tint_menu(lab), (x, y))
    v = Image.open(IMG / "616.png").convert("RGBA") if white_veil else veil
    layer = Image.new("RGBA", (W, H + 8), (0, 0, 0, 0))
    layer.paste(v, (round(VEIL_XY[0]), round(VEIL_XY[1])))
    m.alpha_composite(layer.crop((0, 0, W, H)))
    d = ImageDraw.Draw(m)
    f_btn = ImageFont.truetype(str(NANUM_B), 19)
    for text, yy in (("업데이트", 9), ("다른 게임", 46)):
        d.text((550, yy), text, font=f_btn, fill=(255, 255, 0), anchor="ma", stroke_width=1, stroke_fill=(0, 0, 0))
    d.text((5, 361), "V 2.6", font=ImageFont.truetype(str(FONTS / "NanumGothic-Regular.ttf"), 12), fill=(255, 255, 255))
    shot = Image.open(SHOTS / "ui_v2" / "03_title.png").convert("RGB").crop((282, 28, 1348, 740)).resize((W, H), Image.LANCZOS)
    m.paste(shot.crop((0, BAR_Y, W, H)), (0, BAR_Y))
    return m.convert("RGB")


def outline_zones(im, boxes):
    m = im.convert("RGB").copy()
    d = ImageDraw.Draw(m)
    for box, col in boxes:
        d.rectangle(box, outline=col)
    return m


def build_preview(splash, title, veil):
    head = ImageFont.truetype(str(FONTS / "NanumGothic-ExtraBold.ttf"), 15)
    small = ImageFont.truetype(str(FONTS / "NanumGothic-Bold.ttf"), 12)
    SW = 1240

    def titled(im, text):
        t = Image.new("RGB", (im.width, im.height + 22), (255, 255, 255))
        t.paste(im.convert("RGB"), (0, 22))
        ImageDraw.Draw(t).text((2, 3), text, font=head, fill=(20, 20, 20))
        return t

    def row(ims, gap=20):
        h = max(i.height for i in ims)
        r = Image.new("RGB", (SW, h), (255, 255, 255))
        x = 0
        for i in ims:
            r.paste(i, (x, 0))
            x += i.width + gap
        return r

    tm = title_mock(title, veil)
    sm = loader_mock(splash)
    z_title = outline_zones(title, [(MENU_BOX, (255, 0, 255)), (BTN_BOX, (255, 255, 0)), ((0, 355, 60, 380), (0, 255, 255)),
                                    ((0, BAR_Y, W - 1, H - 1), (160, 160, 160))])
    z_splash = outline_zones(splash, [(LOADER_BOX, (0, 255, 0)), ((17, 384, 577, 393), (0, 255, 0))])
    blocks = [
        row([titled(sm, "(1) splash_600x400 + the game's loader line and bar (1x)"),
             titled(splash, "splash alone = intro fade card (1x)")]),
        row([titled(tm, "(2) title_bg_600x400 + menu (veil = title_veil_616.png), buttons, V 2.6, status bar"),
             titled(title, "title_bg_600x400 alone (1x)")]),
        row([titled(z_title.resize((300, 200), Image.LANCZOS), "protected zones (0.5x)"),
             titled(z_splash.resize((300, 200), Image.LANCZOS), "loader zone (0.5x)"),
             titled(title_mock(title, veil, white_veil=True).resize((300, 200), Image.LANCZOS),
                    "if 616 stays white (0.5x)"),
             titled(on_dark(veil), "title_veil_616.png (1x, on magenta)")]),
        titled(tm.resize((W * 2, H * 2), Image.LANCZOS), "(3) title mock at 2x"),
        titled(sm.resize((W * 2, H * 2), Image.LANCZOS), "(4) splash + loader at 2x"),
    ]
    total = sum(b.height for b in blocks) + 16 * len(blocks)
    sheet = Image.new("RGB", (SW, total), (255, 255, 255))
    yy = 0
    for b in blocks:
        sheet.paste(b, (0, yy))
        yy += b.height + 16
    ImageDraw.Draw(sheet).text((SW - 330, 3), "render_v3.py  (블리치 VS 나루토 VS 원피스)", font=small, fill=(90, 90, 90))
    sheet.save(OUT / "preview_v3.png", optimize=True)


def on_dark(im):
    bg = Image.new("RGBA", im.size, (200, 0, 200, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    backup = ROOT / "work" / "design" / "out_v2_splash.png"
    if not backup.exists() and (OUT / "splash_600x400.png").exists():
        shutil.copy(OUT / "splash_600x400.png", backup)
        print("kept the previous splash as", backup.relative_to(ROOT))
    title = render_title()
    splash = render_splash()
    veil = render_veil(title)
    assert title.size == splash.size == (W, H) and veil.size == (373, 171)
    assert title.getextrema()[3] == (255, 255) and splash.getextrema()[3] == (255, 255)
    title.save(OUT / "title_bg_600x400.png", optimize=True)
    splash.save(OUT / "splash_600x400.png", optimize=True)
    veil.save(OUT / "title_veil_616.png", optimize=True)
    build_preview(splash, title, veil)
    for n in ("splash_600x400.png", "title_bg_600x400.png", "title_veil_616.png", "preview_v3.png"):
        im = Image.open(OUT / n)
        print(f"{n}: {im.size[0]}x{im.size[1]} {im.mode}")


if __name__ == "__main__":
    main()
