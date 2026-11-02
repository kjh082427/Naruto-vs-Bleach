#!/usr/bin/env python3
"""Shanks S+I "Kamusari" (神避) effect art.

Phases: a crimson Haki eagle materialises above Shanks and dives into his
blade, black-red lightning crackles around him, a release flash, then a
colossal black-cored crescent slash sweeps across the whole stage.

Deterministic: every random draw comes from seeded numpy Generators or the
hash noise below. Run from anywhere:

    tools/venv/bin/python work/shanks/render_fx.py

Writes work/shanks/fx/<name>/<NN>.png (RGBA), work/shanks/fx/layout.json and
work/shanks/fx/preview.png. Coordinates: Shanks faces right, his origin (feet
centre) is (0, 0) in game px, y grows downwards. layout.json stores the
top-left offset of every frame relative to that origin (stage top-left for
the *_stage sets, the anchor point for "lightning").
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FX = ROOT / "work/shanks/fx"
SS = 3  # supersampling for crisp vector shapes

# ---------------------------------------------------------------- palette
WHITE = (255, 252, 250)
HOT = (255, 212, 228)
PINK = (255, 116, 176)
MAGENTA = (232, 38, 132)
CRIMSON = (216, 20, 54)
RED = (156, 10, 34)
DRED = (96, 6, 24)
MAROON = (52, 4, 16)
BLACK = (12, 2, 8)
ROCK = (40, 28, 34)


# ---------------------------------------------------------------- noise
def _hash(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFF).astype(np.float32) / 65535.0


def vnoise(u, v, seed):
    u = np.asarray(u, np.float64)
    v = np.asarray(v, np.float64)
    iu = np.floor(u)
    iv = np.floor(v)
    fu = (u - iu).astype(np.float32)
    fv = (v - iv).astype(np.float32)
    iu = iu.astype(np.int64)
    iv = iv.astype(np.int64)
    su = fu * fu * (3 - 2 * fu)
    sv = fv * fv * (3 - 2 * fv)
    a = _hash(iu, iv, seed)
    b = _hash(iu + 1, iv, seed)
    c = _hash(iu, iv + 1, seed)
    d = _hash(iu + 1, iv + 1, seed)
    top = a + (b - a) * su
    bot = c + (d - c) * su
    return top + (bot - top) * sv


def fbm(u, v, seed, octaves=3):
    tot = 0.0
    amp = 1.0
    norm = 0.0
    for o in range(octaves):
        tot = tot + amp * vnoise(u * (2 ** o), v * (2 ** o), seed + 101 * o)
        norm += amp
        amp *= 0.5
    return tot / norm


# ---------------------------------------------------------------- raster helpers
def box_blur(a, r):
    r = int(r)
    if r < 1:
        return a
    k = 2 * r + 1
    p = np.pad(a, ((r + 1, r), (0, 0)))
    c = np.cumsum(p, axis=0)
    a = (c[k:] - c[:-k]) / k
    p = np.pad(a, ((0, 0), (r + 1, r)))
    c = np.cumsum(p, axis=1)
    return (c[:, k:] - c[:, :-k]) / k


def gauss(a, sigma):
    if sigma <= 0.3:
        return a
    w = math.sqrt(4 * sigma * sigma / 3 + 1)
    r = max(1, int(round((w - 1) / 2)))
    for _ in range(3):
        a = box_blur(a, r)
    return a


def dilate(mask, r):
    """Binary dilation by a (2r+1) square using box blur."""
    if r < 1:
        return mask
    return box_blur(mask.astype(np.float32), r) > 1e-4


def solid(color, alpha):
    """Premultiplied layer of a flat colour with per-pixel alpha."""
    alpha = np.clip(alpha, 0, 1).astype(np.float32)
    out = np.empty(alpha.shape + (4,), np.float32)
    for i in range(3):
        out[..., i] = color[i] / 255.0 * alpha
    out[..., 3] = alpha
    return out


def over(dst, src):
    return src + dst * (1 - src[..., 3:4])


def stepped_glow(src_mask, sigma, stops, gain=1.0, exclude=None):
    """Blurred mask posterised into hard colour rings (game-style glow).
    stops: [(threshold, colour, alpha), ...] from the inside out."""
    g = gauss(np.clip(src_mask, 0, 1).astype(np.float32), sigma)
    out = bands(g, stops, gain)
    if exclude is not None:
        out *= (1 - np.clip(exclude, 0, 1))[..., None]
    return out


class Layer:
    """Premultiplied float RGBA canvas in game px; (x0, y0) is its top-left in
    Shanks coordinates."""

    def __init__(self, x0, y0, w, h):
        self.x0, self.y0, self.w, self.h = int(x0), int(y0), int(w), int(h)
        self.a = np.zeros((self.h, self.w, 4), np.float32)

    def over(self, src):
        self.a = over(self.a, src)

    def grid(self, ss=1):
        xs = self.x0 + (np.arange(self.w * ss) + 0.5) / ss
        ys = self.y0 + (np.arange(self.h * ss) + 0.5) / ss
        return np.meshgrid(xs.astype(np.float32), ys.astype(np.float32))


class Pen:
    """Vector drawing at SS, resolved to a 1x premultiplied array."""

    def __init__(self, layer):
        self.L = layer
        self.im = Image.new("RGBA", (layer.w * SS, layer.h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        x0, y0 = self.L.x0, self.L.y0
        return [((x - x0) * SS, (y - y0) * SS) for x, y in pts]

    @staticmethod
    def _c(c):
        return tuple(int(v) for v in c) + ((255,) if len(c) == 3 else ())

    def poly(self, pts, fill=None, outline=None, width=1.0):
        q = self.P(pts)
        if len(q) < 3:
            return
        if fill is not None:
            self.d.polygon(q, fill=self._c(fill))
        if outline is not None and width > 0:
            self.d.line(q + [q[0]], fill=self._c(outline),
                        width=max(1, int(round(width * SS))), joint="curve")

    def line(self, pts, color, width):
        q = self.P(pts)
        if len(q) < 2:
            return
        self.d.line(q, fill=self._c(color), width=max(1, int(round(width * SS))),
                    joint="curve")

    def disc(self, c, r, fill):
        x, y = (c[0] - self.L.x0) * SS, (c[1] - self.L.y0) * SS
        r *= SS
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=self._c(fill))

    def result(self):
        im = self.im.convert("RGBa").resize((self.L.w, self.L.h), Image.BOX)
        return np.asarray(im, np.float32) / 255.0


def downsample(a, ss):
    h, w = a.shape[0] // ss, a.shape[1] // ss
    return a[: h * ss, : w * ss].reshape(h, ss, w, ss, -1).mean(axis=(1, 3))


def finalize(arr, colors=96):
    """Premultiplied float -> palette-limited RGBA image (hard-ish game look,
    small files)."""
    a = np.clip(arr[..., 3], 0, 1)
    rgb = np.where(a[..., None] > 1e-4, arr[..., :3] / np.maximum(a[..., None], 1e-4), 0)
    a = np.where(a < 0.035, 0, a)
    out = np.dstack([np.clip(rgb, 0, 1) * 255, a * 255]).round().astype(np.uint8)
    out[a == 0] = 0
    im = Image.fromarray(out, "RGBA")
    q = im.quantize(colors=colors, method=Image.Quantize.FASTOCTREE,
                    dither=Image.Dither.NONE)
    im = q.convert("RGBA")
    px = np.asarray(im).copy()
    px[px[..., 3] < 6] = 0
    return Image.fromarray(px, "RGBA")


def crop_alpha(im, x0, y0, pad=1):
    bb = im.getchannel("A").point(lambda v: 255 if v > 0 else 0).getbbox()
    if bb is None:
        return im.crop((0, 0, 2, 2)), (x0, y0)
    l, t, r, b = bb
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(im.width, r + pad), min(im.height, b + pad)
    return im.crop((l, t, r, b)), (x0 + l, y0 + t)


# ---------------------------------------------------------------- lightning
def bolt_points(rng, p0, p1, rough=0.36, levels=4):
    """Jagged lightning polyline: few levels of midpoint displacement so the
    bolt keeps long straight runs with sharp kinks (anime style)."""
    pts = np.array([p0, p1], np.float64)
    disp = rough * float(np.hypot(*(np.subtract(p1, p0))))
    for _ in range(levels):
        new = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            m = (a + b) / 2 + (b - a) * rng.uniform(-0.15, 0.15)
            d = b - a
            n = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
            new.append(m + n * rng.uniform(-disp, disp))
            new.append(b)
        pts = np.array(new)
        disp *= 0.46
    return pts


def bolt_tree(rng, p0, ang, length, depth=2, rough=0.30, branches=(1, 3)):
    p0 = np.asarray(p0, np.float64)
    p1 = p0 + length * np.array([math.cos(ang), math.sin(ang)])
    main = bolt_points(rng, p0, p1, rough)
    out = [(main, 0)]
    if depth > 0:
        for _ in range(int(rng.integers(branches[0], branches[1] + 1))):
            i = int(rng.integers(len(main) // 6, max(len(main) // 6 + 1, len(main) * 4 // 5)))
            a2 = ang + rng.choice([-1, 1]) * rng.uniform(0.35, 0.95)
            sub = bolt_tree(rng, main[i], a2, length * rng.uniform(0.28, 0.55),
                            depth - 1, rough, (0, 2))
            out += [(p, lvl + 1) for p, lvl in sub]
    return out


def spark(pen, c, r, rng):
    x, y = c
    pen.line([(x - r, y), (x + r, y)], HOT, 1.0)
    pen.line([(x, y - r), (x, y + r)], HOT, 1.0)
    if r > 2.5:
        d = r * 0.5
        pen.line([(x - d, y - d), (x + d, y + d)], PINK, 0.8)
        pen.line([(x - d, y + d), (x + d, y - d)], PINK, 0.8)
    pen.disc(c, 1.0, WHITE)


def draw_bolts(layer, bolts, rng, core=2.4, halo=1.3, glow_sigma=3.0,
               glow_gain=1.0, flicker=True, sparks=True, scale=1.0):
    """Black lightning: thin magenta glow -> crimson halo -> pink rim -> black
    core, with white-hot flickers and sparks ("지지직")."""
    pg, ph, pr, pc, pf = (Pen(layer) for _ in range(5))
    for pts, lvl in bolts:
        k = (0.66 ** lvl) * scale
        P = [tuple(p) for p in pts]
        cw = max(1.0, core * k)
        pg.line(P, WHITE, cw + 2 * halo * k + 2)
        ph.line(P, CRIMSON, cw + 2 * halo * k)
        pr.line(P, PINK, cw + 1.0)
        pc.line(P, BLACK, cw)
        if flicker and lvl <= 1:
            n = len(pts)
            for _ in range(int(rng.integers(1, 4))):
                i = int(rng.integers(0, max(1, n - 4)))
                j = min(n, i + int(rng.integers(2, 6)))
                seg = pts[i:j]
                if len(seg) < 2:
                    continue
                d = seg[-1] - seg[0]
                nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
                off = rng.choice([-1, 1]) * (cw / 2 + halo * k + rng.uniform(2.0, 5.0))
                jit = seg + nrm * off + rng.normal(0, 1.4, seg.shape)
                pf.line([tuple(p) for p in jit], HOT, 1.0)
        if sparks:
            tip = pts[-1]
            if lvl <= 1 or rng.random() < 0.4:
                spark(pf, tuple(tip), rng.uniform(2.0, 4.5) * max(0.7, scale), rng)
            for _ in range(int(rng.integers(0, 3))):
                q = pts[int(rng.integers(0, len(pts)))] + rng.normal(0, 6 * scale, 2)
                pf.disc(tuple(q), rng.uniform(0.6, 1.2), HOT)
    gmask = pg.result()[..., 3]
    layer.over(stepped_glow(gmask, glow_sigma * scale,
                            [(0.38, MAGENTA, 0.50), (0.18, CRIMSON, 0.30), (0.07, DRED, 0.15)],
                            gain=glow_gain))
    layer.over(ph.result())
    layer.over(pr.result())
    layer.over(pc.result())
    layer.over(pf.result())


# ---------------------------------------------------------------- eagle geometry
WING_S = (26.0, -40.0)
WING_L = (92.0, 86.0, 62.0)
WING_T = sum(WING_L)
S_E, S_W = WING_L[0] / WING_T, (WING_L[0] + WING_L[1]) / WING_T
DELTA_S = [0.0, S_E, S_W - 0.01, S_W + 0.02, 1.0]
DELTA_A = [150.0, 120.0, 78.0, 46.0, -46.0]


def feather(base, ang, length, width, tip=2.0, n=12, bulge=0.25):
    ux, uy = math.cos(ang), math.sin(ang)
    vx, vy = -uy, ux
    L, R = [], []
    for i in range(n + 1):
        u = i / n
        hw = width / 2 * max(0.0, 1 - u ** tip) ** 0.55 * (1 - bulge + bulge * 4 * u * (1 - u) + bulge * (1 - u))
        cx, cy = base[0] + ux * length * u, base[1] + uy * length * u
        L.append((cx + vx * hw, cy + vy * hw))
        R.append((cx - vx * hw, cy - vy * hw))
    return L + R[::-1]


def ellipse_pts(c, rx, ry, n=36, a0=0.0):
    return [(c[0] + rx * math.cos(a0 + 2 * math.pi * i / n),
             c[1] + ry * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def part(pts, fill=None, line=None, lw=0.0, g="body", kind="poly"):
    return {"pts": list(pts), "fill": fill, "line": line, "lw": lw, "g": g, "kind": kind}


def wing_parts(a1, a2, a3, fold):
    """Right wing (screen right) in eagle-local coords."""
    sk = [WING_S]
    for L, a in zip(WING_L, (a1, a2, a3)):
        r = math.radians(a)
        x, y = sk[-1]
        sk.append((x + L * math.cos(r), y + L * math.sin(r)))
    cum = [0.0, S_E, S_W, 1.0]

    def at(s):
        for i in range(3):
            if s <= cum[i + 1] or i == 2:
                u = min(1.0, max(0.0, (s - cum[i]) / (cum[i + 1] - cum[i])))
                x = sk[i][0] + (sk[i + 1][0] - sk[i][0]) * u
                y = sk[i][1] + (sk[i + 1][1] - sk[i][1]) * u
                return (x, y)

    def seg_ang(s):
        return float(np.interp(s, [0, S_E, S_W, 1], [a1, (a1 + a2) / 2, (a2 + a3) / 2, a3]))

    def fdir(s):
        return math.radians(seg_ang(s) + float(np.interp(s, DELTA_S, DELTA_A)) * (1 - 0.8 * fold))

    lk = 1 - 0.28 * fold
    P = []
    # primaries, outermost first (back)
    prim_len = [112, 130, 142, 148, 144, 134]
    for i, s in enumerate(np.linspace(1.0, 0.77, 6)):
        b, a, L = at(s), fdir(s), prim_len[i] * lk
        P.append(part(feather(b, a, L, 25, tip=1.7), DRED, HOT, 1.25, "wing"))
        P.append(part(feather(b, a, L * 0.8, 8, tip=1.4), RED, None, 0, "wing"))
    # secondaries, wrist -> body
    for i, s in enumerate(np.linspace(0.72, 0.03, 10)):
        b, a = at(s), fdir(s)
        L = (110 + 10 * math.sin(i / 9 * math.pi)) * lk
        P.append(part(feather(b, a, L, 31, tip=3.2), DRED, HOT, 1.25, "wing"))
        P.append(part(feather(b, a, L * 0.78, 9, tip=2.0), RED, None, 0, "wing"))
    # greater coverts
    for s in np.linspace(0.70, 0.04, 10):
        b, a = at(s), fdir(s)
        P.append(part(feather(b, a, 60 * lk, 30, tip=2.4), RED, PINK, 1.1, "wing"))
        P.append(part(feather(b, a, 44 * lk, 9, tip=2.0), CRIMSON, None, 0, "wing"))
    # primary coverts
    for s in np.linspace(0.98, 0.76, 5):
        b, a = at(s), fdir(s)
        P.append(part(feather(b, a, 56 * lk, 24, tip=2.2), RED, PINK, 1.1, "wing"))
    # lesser coverts
    for s in np.linspace(0.74, 0.03, 12):
        b, a = at(s), fdir(s)
        P.append(part(feather(b, a, 30 * lk, 22, tip=2.6), CRIMSON, PINK, 1.0, "wing"))
    # leading edge (marginal band)
    P.append(part(sk, HOT, None, 21, "wing", kind="band"))
    P.append(part(sk, CRIMSON, None, 16, "wing", kind="band"))
    P.append(part(sk, RED, None, 7, "wing", kind="band"))
    return P


def head_parts(turn):
    """Head in profile, beak facing +x, rotated by `turn` deg about the neck."""
    hc = (6.0, -90.0)
    piv = (0.0, -60.0)
    P = []
    # hackles (spiky crest on the back of the head/neck)
    pts = []
    n = 8
    for i in range(n + 1):
        phi = math.radians(118 + 128 * i / n)
        r_in = 21
        pts.append((hc[0] + r_in * math.cos(phi), hc[1] + r_in * 0.9 * math.sin(phi)))
        if i < n:
            phi2 = math.radians(118 + 128 * (i + 0.5) / n + 14)
            L = 21 + 17 + 6 * math.sin(i * 1.7)
            pts.append((hc[0] + L * math.cos(phi2), hc[1] + L * 0.9 * math.sin(phi2) + 6))
    pts.append(hc)
    P.append(part(pts, CRIMSON, HOT, 1.3, "head"))
    P.append(part(ellipse_pts(hc, 27, 23), CRIMSON, HOT, 1.4, "head"))
    # cheek shading
    P.append(part(ellipse_pts((hc[0] - 4, hc[1] + 6), 16, 11), RED, None, 0, "head"))
    bx, by = hc
    upper = [(14, -9), (32, -13), (47, -10), (57, -2), (62, 9), (59, 20), (54, 26), (52, 16), (46, 9), (20, 9)]
    lower = [(22, 9), (46, 9), (43, 15), (34, 18), (24, 16)]
    P.append(part([(bx + x, by + y) for x, y in lower], PINK, WHITE, 1.2, "head"))
    P.append(part([(bx + x, by + y) for x, y in upper], HOT, WHITE, 1.4, "head"))
    P.append(part([(bx + x, by + y) for x, y in [(30, -6), (48, -6), (56, 4)]], PINK, None, 2.0, "head", kind="line"))
    P.append(part([(bx + x, by + y) for x, y in [(20, 9), (46, 9), (52, 15)]], MAROON, None, 1.6, "head", kind="line"))
    # brow ridge, eye, glint
    P.append(part([(bx + x, by + y) for x, y in [(-6, -19), (32, -15), (30, -6), (18, -9), (0, -10)]], MAROON, None, 0, "head"))
    P.append(part(ellipse_pts((bx + 17, by - 4), 6.5, 4.2), WHITE, None, 0, "head"))
    P.append(part(ellipse_pts((bx + 19.5, by - 4), 2.4, 2.4, 12), BLACK, None, 0, "eye"))
    P.append(part([(bx + x, by + y) for x, y in [(4, 2), (14, 5), (24, 4)]], PINK, None, 1.4, "head", kind="line"))
    r = math.radians(turn)
    c, s = math.cos(r), math.sin(r)
    for p in P:
        p["pts"] = [(piv[0] + (x - piv[0]) * c - (y - piv[1]) * s,
                     piv[1] + (x - piv[0]) * s + (y - piv[1]) * c) for x, y in p["pts"]]
    return P


def body_parts():
    P = []
    # tail fan (behind)
    for i in range(7):
        a = math.radians(90 + (i - 3) * 10)
        L = 96 - abs(i - 3) * 5
        P.append(part(feather((0, 56), a, L, 27, tip=7, bulge=0.1), DRED, HOT, 1.25, "wing"))
        P.append(part(feather((0, 56), a, L * 0.8, 8, tip=2), RED, None, 0, "wing"))
    for i in range(3):
        a = math.radians(90 + (i - 1) * 14)
        P.append(part(feather((0, 50), a, 46, 26, tip=2.6), RED, PINK, 1.1, "wing"))
    # thighs ("trousers") and talons
    for sx in (-1, 1):
        th = [(sx * 8, 34), (sx * 40, 36), (sx * 46, 60), (sx * 42, 70), (sx * 36, 64), (sx * 33, 78),
              (sx * 26, 70), (sx * 20, 82), (sx * 14, 70), (sx * 8, 76)]
        P.append(part(th, RED, PINK, 1.2, "body"))
        foot = (sx * 27, 100)
        P.append(part([(sx * 25, 74), foot], HOT, None, 6.5, "body", kind="line"))
        for ang, L in ((60, 17), (95, 19), (128, 16), (-80 if sx > 0 else -100, 10)):
            a = math.radians(ang if sx > 0 else 180 - ang)
            mid = (foot[0] + math.cos(a) * L * 0.6, foot[1] + math.sin(a) * L * 0.6)
            tipp = (foot[0] + math.cos(a + 0.5 * sx) * L, foot[1] + math.sin(a + 0.5 * sx) * L)
            P.append(part([foot, mid, tipp], HOT, None, 4.2, "body", kind="line"))
            P.append(part([mid, tipp], WHITE, None, 2.0, "body", kind="line"))
    # torso: dark body, lit breast, zig-zag feather fringes
    P.append(part(ellipse_pts((0, 4), 43, 60), RED, HOT, 1.4, "body"))
    P.append(part(ellipse_pts((0, -8), 27, 42), CRIMSON, None, 0, "body"))
    for y in (-30, -16, -2, 12, 26, 40):
        half = math.sqrt(max(0.0, 1 - ((y - 4) / 60.0) ** 2)) * 43 - 7
        n = max(2, int(2 * half / 9))
        pts = []
        for j in range(n + 1):
            x = -half + 2 * half * j / n
            pts.append((x, y - 2.5 * math.cos(math.pi * x / (2 * half)) * 0))
            if j < n:
                xm = -half + 2 * half * (j + 0.5) / n
                pts.append((xm, y + 5))
        P.append(part(pts, PINK, None, 1.0, "chest", kind="line"))
    # neck
    P.append(part([(-30, -40), (30, -40), (26, -66), (-22, -72)], CRIMSON, HOT, 1.3, "head"))
    return P


def mirror(parts):
    out = []
    for p in parts:
        q = dict(p)
        q["pts"] = [(-x, y) for x, y in p["pts"]]
        out.append(q)
    return out


def eagle_geometry(a, fold=0.0, head=0.0):
    a1, a2, a3 = a
    rw = wing_parts(a1, a2, a3, fold)
    return mirror(rw) + rw + body_parts() + head_parts(head)


def transform(parts, scale, rot, cx, cy):
    r = math.radians(rot)
    c, s = math.cos(r), math.sin(r)
    out = []
    for p in parts:
        q = dict(p)
        q["pts"] = [(cx + scale * (x * c - y * s), cy + scale * (x * s + y * c)) for x, y in p["pts"]]
        q["lw"] = p["lw"] * scale
        out.append(q)
    return out


def bbox(parts, pad):
    xs = [x for p in parts for x, _ in p["pts"]]
    ys = [y for p in parts for _, y in p["pts"]]
    return (math.floor(min(xs) - pad), math.floor(min(ys) - pad),
            math.ceil(max(xs) + pad), math.ceil(max(ys) + pad))


def draw_parts(pen, parts, mode="fill", line_scale=1.0, mono=None):
    for p in parts:
        k = p["kind"]
        if k == "band":
            if mode == "fill" or mono:
                pen.line(p["pts"], mono or p["fill"], p["lw"])
            elif p["fill"] is HOT:
                pen.line(p["pts"], HOT, 1.2)
            continue
        if k == "line":
            if mode == "fill" or mono:
                pen.line(p["pts"], mono or p["fill"], max(0.8, p["lw"]))
            continue
        if mode == "fill":
            pen.poly(p["pts"], fill=mono or p["fill"],
                     outline=(mono or p["line"]) if p["line"] else None,
                     width=max(0.9, p["lw"] * line_scale) if p["line"] else 0)
        elif mode == "lines" and p["line"] is not None:
            pen.poly(p["pts"], None, HOT if p["line"] is PINK else WHITE,
                     max(1.0, p["lw"] * 1.15))


# ---------------------------------------------------------------- eagle frames
# Shanks coords. Eagle body centre for the hold pose; blade point for the dive.
EAGLE_C = (100.0, -160.0)
BLADE = (38.0, -58.0)
SPREAD = (-50.0, -22.0, 0.0)
PEAK_SCALE = 0.80

EAGLE_FRAMES = [
    dict(orb=True),
    dict(scale=0.60, a=(-30, -8, 12), fill=0.0, lines=1.0, reveal=0.55, glow=0.55, dy=30),
    dict(scale=0.78, a=(-40, -15, 6), fill=0.35, lines=1.0, reveal=1.0, glow=0.8, dy=14),
    dict(scale=0.92, a=(-46, -20, 2), fill=0.85, lines=0.45, glow=1.0, dy=5),
    dict(scale=1.00, a=SPREAD, fill=1.0, lines=0.0, glow=1.35, bright=True),
    dict(scale=1.00, a=(-52, -24, -2), glow=1.0, bolts=2, seed=11),
    dict(scale=1.00, a=(-56, -27, -5), glow=1.2, bolts=3, seed=12, dy=-3),
    dict(scale=1.00, a=(-52, -24, -2), glow=1.05, bolts=2, seed=13),
    dict(scale=1.00, a=(-47, -20, 2), glow=1.25, bolts=3, seed=14, dy=2),
    dict(scale=1.00, a=SPREAD, glow=1.1, bolts=2, seed=15),
    dict(scale=1.02, a=(-66, -36, -14), glow=1.4, head=-30, rot=-5, dy=-12, bolts=3, seed=16, bright=True),
    dict(scale=0.74, a=(48, 70, 84), fold=0.55, head=-88, rot=198, at=(122.0, -118.0), trail=2, glow=1.3, seed=17),
    dict(scale=0.50, a=(70, 88, 98), fold=0.9, head=-92, rot=206, at=(78.0, -92.0), trail=3, glow=1.5, seed=18),
    dict(comet=True),
]


def eagle_layer(parts, pad):
    x0, y0, x1, y1 = bbox(parts, pad)
    return Layer(x0, y0, x1 - x0, y1 - y0)


def render_eagle_body(L, parts, spec, rng, seed):
    fill_a = spec.get("fill", 1.0)
    lines_a = spec.get("lines", 0.0)
    reveal = spec.get("reveal", 1.0)
    glow = spec.get("glow", 1.0)
    bright = spec.get("bright", False)
    sc = spec.get("scale", 1.0)
    X, Y = L.grid()
    pf = Pen(L)
    draw_parts(pf, parts, "fill")
    F = pf.result()
    mask = F[..., 3]
    # visible wing/tail area for the glowing mottle
    pw = Pen(L)
    for p in parts:
        if p["kind"] in ("line",):
            continue
        col = WHITE if p["g"] == "wing" else BLACK
        if p["kind"] == "band":
            pw.line(p["pts"], col, p["lw"])
        else:
            pw.poly(p["pts"], fill=col)
    W = pw.result()
    wing_vis = W[..., 0] * (W[..., 3] > 0.5)
    m = mask > 0.5
    ring1 = dilate(m, 1) & ~m
    ring2 = dilate(m, 3) & ~dilate(m, 1)
    rev = np.ones(mask.shape, np.float32)
    if reveal < 1.0:
        rev = (fbm(X / 22.0, Y / 22.0, seed + 5) < reveal + 0.12).astype(np.float32)
    # Haki flame aura (flickers with the seed) + wide dim halo
    out = flame_glow(mask, X, Y, 6.0 * sc + 3,
                     [(0.40, MAGENTA, 0.92), (0.24, CRIMSON, 0.70), (0.13, RED, 0.48), (0.06, DRED, 0.28)],
                     seed=300 + seed, phase=seed * 9.0, gain=glow, stretch=(7.0, 13.0), lift=int(7 * sc + 2),
                     amp=1.3)
    halo = stepped_glow(mask, 28.0, [(0.30, DRED, 0.24), (0.12, MAROON, 0.14)], gain=glow)
    out = over(halo, out)
    if fill_a < 1.0:
        out *= 0.55 + 0.45 * fill_a
    # body fill
    out = over(out, F * fill_a)
    # glowing mottle on the feathers (Haki texture)
    if fill_a > 0:
        n = fbm(X / 7.0 + seed * 3.1, Y / 7.0, 77 + seed, 2)
        n2 = fbm(X / 3.0, Y / 3.0 + seed * 1.7, 91 + seed, 1)
        spot = (n > 0.70) & (n2 > 0.45)
        hot = (n > 0.80) & (n2 > 0.55)
        out = over(out, solid(PINK, spot * wing_vis * 0.85 * fill_a))
        out = over(out, solid(HOT, hot * wing_vis * 0.9 * fill_a))
    # outline-only pass (materialise)
    if lines_a > 0:
        pl = Pen(L)
        draw_parts(pl, parts, "lines")
        Ln = pl.result()
        out = over(out, Ln * (lines_a * rev)[..., None])
    # silhouette rim
    out = over(out, solid(PINK, ring2 * rev * 0.9))
    out = over(out, solid(WHITE, ring1 * rev))
    if bright:
        inner = m & ~dilate(~m, 2)
        edge = m & ~inner
        out = over(out, solid(HOT, edge * 0.85))
    # glint in the eye
    if fill_a > 0.5:
        eye = [p for p in parts if p["g"] == "eye"]
        if eye:
            ex = float(np.mean([x for x, _ in eye[0]["pts"]]))
            ey = float(np.mean([y for _, y in eye[0]["pts"]]))
            pe = Pen(L)
            r = 7 * sc + 2
            pe.line([(ex - r * 1.6, ey), (ex + r * 1.6, ey)], HOT, 1.2)
            pe.line([(ex, ey - r), (ex, ey + r)], HOT, 1.0)
            pe.disc((ex, ey), 1.6, WHITE)
            out = over(out, pe.result())
    return out


def eagle_frame(i, spec):
    rng = np.random.default_rng(1000 + i)
    seed = spec.get("seed", i)
    if spec.get("orb"):
        return orb_frame(rng)
    if spec.get("comet"):
        return comet_frame(rng)
    scale = spec.get("scale", 1.0) * PEAK_SCALE
    cx, cy = spec.get("at", (EAGLE_C[0], EAGLE_C[1] + spec.get("dy", 0)))
    geo = eagle_geometry(spec["a"], spec.get("fold", 0.0), spec.get("head", 0.0))
    parts = transform(geo, scale, spec.get("rot", 0.0), cx, cy)
    trail = spec.get("trail", 0)
    pad = 40
    allparts = list(parts)
    trails = []
    if trail:
        # afterimages back along the swoop (from the hold pose)
        for k in range(1, trail + 1):
            u = k / (trail + 1)
            tx = cx + (EAGLE_C[0] - cx) * u * 0.9
            ty = cy + (EAGLE_C[1] - cy) * u * 0.9
            sc = scale * (1 + 0.35 * u)
            tp = transform(geo, sc, spec.get("rot", 0.0) - 18 * u, tx, ty)
            trails.append((u, tp))
            allparts += tp
    L = eagle_layer(allparts, pad)
    for u, tp in reversed(trails):
        pm = Pen(L)
        draw_parts(pm, tp, "fill", mono=WHITE)
        mk = pm.result()[..., 3]
        L.over(stepped_glow(mk, 5.0, [(0.45, MAGENTA, 0.55 * (1 - u)), (0.2, CRIMSON, 0.4 * (1 - u)),
                                      (0.06, DRED, 0.22 * (1 - u))]))
        L.over(solid(CRIMSON, (mk > 0.5) * 0.5 * (1 - u)))
    L.over(render_eagle_body(L, parts, spec, rng, seed))
    # crackling black lightning over/around the eagle
    nb = spec.get("bolts", 0)
    if nb:
        bolts = []
        for _ in range(nb):
            side = rng.choice([-1, 1])
            p0 = (cx + side * rng.uniform(40, 170) * scale / PEAK_SCALE * PEAK_SCALE,
                  cy + rng.uniform(-120, 30) * scale)
            ang = math.radians(rng.uniform(0, 360))
            bolts += bolt_tree(rng, p0, ang, rng.uniform(60, 120), 2)
        draw_bolts(L, bolts, rng, core=2.2, halo=2.0)
    if trail:
        # streak lines toward the blade
        ps = Pen(L)
        for _ in range(9):
            o = rng.normal(0, 30, 2)
            a = (EAGLE_C[0] + o[0], EAGLE_C[1] + o[1])
            b = (cx + o[0] * 0.4, cy + o[1] * 0.4)
            ps.line([a, b], PINK if rng.random() < 0.5 else HOT, rng.uniform(1, 2.2))
        S = ps.result()
        S[..., :] *= 0.75
        under = L.a.copy()
        L.a = over(S, under)
    img = finalize(L.a)
    return crop_alpha(img, L.x0, L.y0)


def orb_frame(rng):
    c = (EAGLE_C[0], EAGLE_C[1] + 30)
    L = Layer(min(BLADE[0], c[0]) - 150, c[1] - 140, 340, int(BLADE[1] - c[1]) + 190)
    X, Y = L.grid()
    # pillar of Haki rising from the blade to the orb
    pp = Pen(L)
    pp.poly([(BLADE[0] - 3, BLADE[1]), (BLADE[0] + 3, BLADE[1]), (c[0] + 16, c[1]), (c[0] - 16, c[1])], WHITE)
    pm = pp.result()[..., 3]
    L.over(stepped_glow(pm, 6, [(0.35, MAGENTA, 0.8), (0.15, CRIMSON, 0.5), (0.05, DRED, 0.25)]))
    L.over(solid(HOT, pm))
    r = np.hypot(X - c[0], Y - c[1])
    R = 46.0
    n = fbm((X - c[0]) / 9.0, (Y - c[1]) / 9.0, 5, 2)
    disc = r < R
    L.over(flame_glow(disc.astype(np.float32), X, Y, 14,
                      [(0.4, MAGENTA, 0.9), (0.22, CRIMSON, 0.66), (0.10, RED, 0.42), (0.03, DRED, 0.22)],
                      seed=88, stretch=(7, 12), lift=8, amp=1.2))
    L.over(solid(RED, disc))
    L.over(solid(CRIMSON, disc & (n > 0.52)))
    L.over(solid(PINK, disc & (n > 0.70)))
    L.over(solid(HOT, disc & (r > R - 7)))
    L.over(solid(WHITE, disc & (r > R - 3)))
    bolts = []
    for k in range(5):
        a = math.radians(k * 72 + rng.uniform(-20, 20))
        p0 = (c[0] + math.cos(a) * (R - 6), c[1] + math.sin(a) * (R - 6))
        bolts += bolt_tree(rng, p0, a, rng.uniform(55, 95), 1)
    draw_bolts(L, bolts, rng, core=2.2, halo=2.0)
    return crop_alpha(finalize(L.a), L.x0, L.y0)


def comet_frame(rng):
    """Eagle collapsed into a crimson comet plunging into the blade."""
    tip = BLADE
    src = (EAGLE_C[0] + 40, EAGLE_C[1] - 40)
    L = Layer(tip[0] - 150, src[1] - 70, 330, int(tip[1] - src[1]) + 70 + 150)
    d = np.subtract(tip, src)
    ang = math.atan2(d[1], d[0])
    X, Y = L.grid()
    ux, uy = math.cos(ang), math.sin(ang)
    s = -((X - tip[0]) * ux + (Y - tip[1]) * uy)  # 0 at the blade, + toward the source
    t = -(X - tip[0]) * uy + (Y - tip[1]) * ux
    Lc = float(np.hypot(*d)) + 40
    wid = np.where(s > 0, 40 * np.clip(s / 50, 0, 1) ** 0.5 * np.clip(1 - s / Lc, 0, 1) ** 0.7, 0)
    q = np.abs(t) / np.maximum(wid, 1e-3)
    inside = (s > -6) & (q < 1)
    head = np.hypot(X - tip[0], Y - tip[1])
    m = (inside | (head < 24)).astype(np.float32)
    L.over(flame_glow(m, X, Y, 10, [(0.4, MAGENTA, 0.92), (0.22, CRIMSON, 0.7), (0.1, RED, 0.46), (0.04, DRED, 0.26)],
                      seed=404, stretch=(8, 8), amp=1.2))
    L.over(solid(CRIMSON, m))
    L.over(solid(PINK, (inside & (q < 0.62)) | (head < 18)))
    L.over(solid(HOT, (inside & (q < 0.34)) | (head < 12)))
    L.over(solid(WHITE, (inside & (q < 0.14) & (s < Lc * 0.75)) | (head < 7)))
    # shock ring at the blade
    ell = np.hypot((X - tip[0]) / 1.0, (Y - tip[1]) / 0.42)
    L.over(solid(PINK, (ell > 54) & (ell < 60)))
    L.over(solid(WHITE, (ell > 56) & (ell < 58.5)))
    # folded-wing ghost along the comet
    pg = Pen(L)
    for side in (-1, 1):
        a = ang + math.pi + side * 0.40
        base = (tip[0] - ux * 34, tip[1] - uy * 34)
        pg.poly(feather(base, a, 170, 46, tip=1.6), None, PINK, 1.6)
        pg.poly(feather(base, a + side * 0.16, 130, 34, tip=1.6), None, HOT, 1.2)
        pg.poly(feather(base, a + side * 0.30, 96, 26, tip=1.6), None, HOT, 1.0)
    L.over(pg.result())
    # starburst at the blade
    pb = Pen(L)
    for k in range(16):
        a = k * math.pi / 8 + 0.13
        r1 = 44 if k % 2 == 0 else 24
        pb.poly([(tip[0] + math.cos(a - 0.08) * 5, tip[1] + math.sin(a - 0.08) * 5),
                 (tip[0] + math.cos(a) * r1, tip[1] + math.sin(a) * r1),
                 (tip[0] + math.cos(a + 0.08) * 5, tip[1] + math.sin(a + 0.08) * 5)], HOT)
    L.over(pb.result())
    # feather shards scattering
    pf = Pen(L)
    for _ in range(22):
        a = ang + math.pi + rng.normal(0, 1.1)
        r0 = rng.uniform(25, 150)
        b = (tip[0] + math.cos(a) * r0 + rng.normal(0, 10), tip[1] + math.sin(a) * r0 + rng.normal(0, 10))
        fa = a + rng.normal(0, 0.6)
        pf.poly(feather(b, fa, rng.uniform(12, 26), rng.uniform(5, 9), tip=1.6), RED, HOT, 0.9)
    L.over(pf.result())
    bolts = []
    for k in range(5):
        a = rng.uniform(0, 2 * math.pi)
        bolts += bolt_tree(rng, tip, a, rng.uniform(60, 110), 1)
    draw_bolts(L, bolts, rng, core=2.2, halo=2.0)
    return crop_alpha(finalize(L.a), L.x0, L.y0)


# ---------------------------------------------------------------- lightning loop
LIGHT_W, LIGHT_H = 220, 200
LIGHT_FRAMES = [
    dict(n=3, len=(80, 110), depth=2),
    dict(n=2, len=(90, 115), depth=2),
    dict(n=4, len=(35, 60), depth=1),
    dict(n=3, len=(70, 105), depth=2),
    dict(n=1, len=(100, 118), depth=2),
    dict(n=5, len=(30, 55), depth=1),
    dict(n=3, len=(85, 112), depth=2),
    dict(n=2, len=(40, 70), depth=1),
]


def lightning_frame(i, spec):
    rng = np.random.default_rng(2000 + i)
    L = Layer(-LIGHT_W // 2, -LIGHT_H // 2, LIGHT_W, LIGHT_H)
    bolts = []
    for _ in range(spec["n"]):
        p0 = rng.normal(0, 16, 2)
        ang = rng.uniform(0, 2 * math.pi)
        ln = rng.uniform(*spec["len"])
        tree = bolt_tree(rng, p0, ang, ln, spec["depth"])
        for pts, lvl in tree:
            pts[:, 0] = np.clip(pts[:, 0], -LIGHT_W / 2 + 10, LIGHT_W / 2 - 10)
            pts[:, 1] = np.clip(pts[:, 1], -LIGHT_H / 2 + 10, LIGHT_H / 2 - 10)
        bolts += tree
    draw_bolts(L, bolts, rng, core=2.6, halo=2.4, glow_sigma=4.5)
    # loose crackle fragments
    pf = Pen(L)
    for _ in range(int(rng.integers(3, 7))):
        c = rng.normal(0, 40, 2)
        a = rng.uniform(0, 2 * math.pi)
        seg = bolt_points(rng, c, c + rng.uniform(8, 22) * np.array([math.cos(a), math.sin(a)]), 0.4, 3)
        pf.line([tuple(p) for p in seg], HOT if rng.random() < 0.5 else PINK, 1.0)
    L.over(pf.result())
    return finalize(L.a, 64), (L.x0, L.y0)


# ---------------------------------------------------------------- slash
SLASH_WIN = (-150, -414, 720, 446)  # x0, y0, w, h in Shanks coords (covers the stage)
SLASH_FRAMES = [
    # lead = x of the leading edge on the axis, R = radius, T = max thickness
    dict(lead=52, cy=-56, R=62, th=64, T=22, tilt=-8, bolts=1),
    dict(lead=104, cy=-100, R=132, th=60, T=52, tilt=-8, bolts=3, lines=8),
    dict(lead=180, cy=-150, R=200, th=57, T=96, tilt=-7, bolts=5, lines=14, after=1),
    dict(lead=262, cy=-182, R=250, th=56, T=140, tilt=-6, bolts=7, lines=18, after=2, debris=True),
    dict(lead=330, cy=-190, R=270, th=55, T=168, tilt=-6, bolts=9, lines=16, after=3, debris=True, veins=True),
    dict(lead=384, cy=-192, R=276, th=55, T=178, tilt=-5, bolts=11, lines=12, after=3, debris=True, veins=True),
    dict(lead=424, cy=-192, R=280, th=55, T=178, tilt=-5, bolts=11, lines=6, after=2, debris=True, veins=True, erode=0.10),
    dict(lead=452, cy=-192, R=282, th=55, T=172, tilt=-5, bolts=10, after=1, debris=True, erode=0.32, embers=70),
    dict(lead=472, cy=-192, R=284, th=55, T=164, tilt=-5, bolts=9, debris=True, erode=0.55, embers=120),
    dict(lead=486, cy=-192, R=286, th=55, T=156, tilt=-5, bolts=7, debris=True, erode=0.75, embers=160),
    dict(lead=494, cy=-192, R=288, th=55, T=150, tilt=-5, bolts=4, erode=0.92, embers=120, glow_only=0.35),
    dict(lead=500, cy=-192, R=290, th=55, T=146, tilt=-5, bolts=2, erode=1.0, embers=70, glow_only=0.0),
]


def crescent(X, Y, cx, cy, R, th_deg, T, tilt_deg):
    vx, vy = X - cx, Y - cy
    r = np.hypot(vx, vy)
    th = np.arctan2(vy, vx) - math.radians(tilt_deg)
    th = (th + np.pi) % (2 * np.pi) - np.pi
    t = th / math.radians(th_deg)
    tt = np.clip(np.abs(t), 0, 1)
    thick = T * np.clip(1 - tt ** 2.0, 0, 1) ** 0.85 * (1 + 0.12 * t)
    din = R - r  # px inside from the leading edge
    span = np.abs(t) < 1
    return din, thick, t, span


def crescent_bands(X, Y, cx, cy, R, thd, T, tilt, seed, alpha=1.0, core=True, streaks=True):
    din, thick, t, span = crescent(X, Y, cx, cy, R, thd, T, tilt)
    out = np.zeros(X.shape + (4,), np.float32)
    w1 = np.clip(0.045 * thick, 0.9, 6)
    w2 = w1 + np.clip(0.04 * thick, 0.8, 5)
    w3 = w2 + np.clip(0.06 * thick, 0.8, 7)
    w4 = w3 + np.clip(0.09 * thick, 1.0, 10)
    w5 = w4 + np.clip(0.06 * thick, 0.8, 7)
    # streaky trailing edge
    sp = vnoise(t * 16.0, 0.5, seed)
    spike = np.clip((sp - 0.45) / 0.55, 0, 1) ** 1.5 * 0.7
    back = thick * (1 + spike)
    inside = span & (din >= 0) & (din < back) & (thick > 0.6)
    m = inside.astype(np.float32)
    if streaks:
        sl = vnoise(t * 70.0, 2.5, seed + 9)
        lane = span & (sl > 0.80) & (din >= back) & (din < back + thick * 1.6)
        fade = np.clip(1 - (din - back) / np.maximum(thick * 1.6, 1), 0, 1)
        out = over(out, solid(CRIMSON, lane * fade * (0.85 * alpha)))
        lane2 = span & (sl > 0.92) & (din >= back) & (din < back + thick * 2.4)
        out = over(out, solid(PINK, lane2 * fade * 0.7 * alpha))
    def B(mask, a=1.0):
        return mask.astype(np.float32) * (alpha * a)

    # inner rim (trailing side)
    out = over(out, solid(CRIMSON, B(inside & (din >= thick * 0.86))))
    out = over(out, solid(RED, B(inside & (din >= thick * 0.80) & (din < thick * 0.86))))
    if core:
        corem = inside & (din >= w5) & (din < thick * 0.80)
        out = over(out, solid(BLACK, B(corem)))
        st = vnoise((din / np.maximum(thick, 1)) * 26.0, t * 3.0, seed + 3)
        out = over(out, solid(MAROON, B(corem & (st > 0.66))))
        out = over(out, solid(DRED, B(corem & (st > 0.84))))
    else:
        out = over(out, solid(DRED, B(inside & (din >= w5) & (din < thick * 0.80), 0.9)))
    out = over(out, solid(RED, B(inside & (din >= w4) & (din < w5))))
    out = over(out, solid(CRIMSON, B(inside & (din >= w3) & (din < w4))))
    out = over(out, solid(MAGENTA, B(inside & (din >= w2) & (din < w3))))
    out = over(out, solid(HOT, B(inside & (din >= w1) & (din < w2))))
    out = over(out, solid(WHITE, B(inside & (din < w1))))
    return out, m


DEBRIS = None


def debris_set():
    global DEBRIS
    if DEBRIS is None:
        rng = np.random.default_rng(4242)
        DEBRIS = []
        for _ in range(26):
            DEBRIS.append(dict(x=rng.uniform(70, 470), y=rng.uniform(-14, 0),
                               vx=rng.uniform(2, 11), vy=rng.uniform(-22, -7),
                               s=rng.uniform(4, 15), spin=rng.uniform(-0.5, 0.5),
                               verts=rng.uniform(0.6, 1.0, 7), a0=rng.uniform(0, 6.28)))
    return DEBRIS


def slash_frame(i, spec):
    rng = np.random.default_rng(3000 + i)
    x0, y0, w, h = SLASH_WIN
    L = Layer(x0, y0, w, h)
    R, T = spec["R"], spec["T"]
    cx, cy = spec["lead"] - R, spec["cy"]
    thd, tilt = spec["th"], spec["tilt"]
    erode = spec.get("erode", 0.0)
    glow_only = spec.get("glow_only", 1.0)
    seed = 50 + i
    X1, Y1 = L.grid()
    ss = 2
    Xs, Ys = L.grid(ss)
    acc = np.zeros(Xs.shape + (4,), np.float32)
    # afterimages (previous positions), edge bands only
    na = spec.get("after", 0)
    for k in range(na, 0, -1):
        dx = k * max(30, T * 0.40)
        a = 0.62 * (1 - k / (na + 1.0))
        ai, _ = crescent_bands(Xs, Ys, cx - dx, cy, R * (1 - 0.03 * k), thd, T * 0.42, tilt, seed + k,
                               alpha=a, core=False, streaks=False)
        acc = over(acc, ai)
    # inner echo crescent
    if T > 30:
        ec, _ = crescent_bands(Xs, Ys, cx - T * 0.55, cy, R * 0.86, thd - 4, T * 0.42, tilt + 2,
                               seed + 21, alpha=0.9, core=True, streaks=False)
        acc = over(acc, ec)
    main, m = crescent_bands(Xs, Ys, cx, cy, R, thd, T, tilt, seed)
    acc = over(acc, main)
    if erode > 0:
        n = fbm((Xs - cx) / 18.0, (Ys - cy) / 18.0, seed + 7, 3)
        e = erode * 1.05
        hole = n < e
        rimz = (n >= e) & (n < e + 0.045)
        hotz = (n >= e) & (n < e + 0.018)
        present = acc[..., 3] > 0.05
        acc = acc * (~hole)[..., None]
        acc = over(acc, solid(CRIMSON, rimz & present))
        acc = over(acc, solid(HOT, hotz & present))
        m = m * (~hole)
    A = downsample(acc, ss)
    M = downsample(m[..., None], ss)[..., 0]
    # glows: wide wind-streaked haze + tight stepped rim glow
    g_gain = ((1 - erode) * 0.85 + 0.15) * glow_only
    if g_gain > 0:
        L.over(flame_glow(M, X1, Y1, 24 + T * 0.12, [(0.26, DRED, 0.34), (0.10, MAROON, 0.2)],
                          seed=600 + i, gain=g_gain, stretch=(40.0, 6.0), amp=1.4))
        L.over(flame_glow(M, X1, Y1, 5 + T * 0.05,
                          [(0.40, MAGENTA, 0.92), (0.20, CRIMSON, 0.68), (0.08, RED, 0.44), (0.025, DRED, 0.24)],
                          seed=700 + i, gain=g_gain, stretch=(30.0, 5.0), amp=1.0))
    # horizontal black-red slash streaks across the stage
    nl = spec.get("lines", 0)
    if nl:
        pl = Pen(L)
        lr = np.random.default_rng(777)
        for k in range(nl):
            yy = lr.uniform(-385, 12)
            ln = lr.uniform(220, 640)
            xe = spec["lead"] + lr.uniform(-50, 70)
            xs = xe - ln
            kind = k % 3
            th = lr.uniform(3.0, 7.0) if kind == 0 else lr.uniform(1.2, 2.6)
            body = [(xs, yy), (xe - ln * 0.25, yy - th / 2), (xe, yy + lr.uniform(-1, 1)), (xe - ln * 0.25, yy + th / 2)]
            if kind == 0:
                pl.poly([(x, y + (1.6 if y > yy else -1.6 if y < yy else 0)) for x, y in body], CRIMSON)
                pl.poly(body, BLACK)
            else:
                pl.poly(body, CRIMSON if kind == 1 else HOT)
        L.over(pl.result() * 0.92)
    L.over(A)
    # crimson veins (red lightning running inside the black core)
    if spec.get("veins"):
        pv = Pen(L)
        for k in range(5):
            dd = rng.uniform(0.3, 0.72)
            ts = np.linspace(-0.8, 0.8, 9) + rng.uniform(-0.08, 0.08)
            anchors = []
            for tv in ts:
                a = math.radians(tilt) + tv * math.radians(thd)
                th_here = T * max(0.0, 1 - tv * tv) ** 0.85
                rr = R - th_here * dd
                anchors.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            pts = []
            for p, q in zip(anchors[:-1], anchors[1:]):
                pts += [tuple(v) for v in bolt_points(rng, p, q, 0.35, 3)[:-1]]
            pts.append(anchors[-1])
            pv.line(pts, CRIMSON, 2.6)
            pv.line(pts, PINK, 1.0)
        L.over(pv.result() * (1 - erode))
    # lightning tendrils off the slash
    nb = spec.get("bolts", 0)
    if nb:
        bolts = []
        for k in range(nb):
            tv = rng.uniform(-0.88, 0.88)
            a = math.radians(tilt) + tv * math.radians(thd)
            depth_in = rng.uniform(0, 0.5) * T * max(0.0, 1 - tv * tv)
            p0 = (cx + (R - depth_in) * math.cos(a), cy + (R - depth_in) * math.sin(a))
            if rng.random() < 0.7:
                ang = a + rng.uniform(-0.8, 0.8)
            else:
                ang = a + math.pi + rng.uniform(-0.8, 0.8)
            ln = rng.uniform(70, 210) * (0.35 + 0.65 * min(1.0, T / 170))
            bolts += bolt_tree(rng, p0, ang, ln, 2)
        draw_bolts(L, bolts, rng, core=2.8 * min(1.15, 0.55 + T / 300), halo=2.2, glow_sigma=4.5)
    # debris
    if spec.get("debris"):
        pd = Pen(L)
        for dbr in debris_set():
            k0 = None
            for j, sp in enumerate(SLASH_FRAMES):
                if sp["lead"] >= dbr["x"]:
                    k0 = j
                    break
            if k0 is None or i < k0:
                continue
            dt = i - k0 + 0.6
            px = dbr["x"] + dbr["vx"] * dt
            py = dbr["y"] + dbr["vy"] * dt + 1.1 * dt * dt
            if py > 6:
                continue
            ang = dbr["a0"] + dbr["spin"] * dt
            s = dbr["s"]
            pts = [(px + math.cos(ang + j * 2 * math.pi / 7) * s * dbr["verts"][j],
                    py + math.sin(ang + j * 2 * math.pi / 7) * s * dbr["verts"][j] * 0.8) for j in range(7)]
            pd.poly([(x - 1.8, y) for x, y in pts], CRIMSON)
            pd.poly(pts, ROCK, BLACK, 1.0)
            pd.line(pts[2:5], (90, 64, 74), 1.0)
        L.over(pd.result())
    # embers
    ne = spec.get("embers", 0)
    if ne:
        pe = Pen(L)
        for k in range(ne):
            tv = rng.uniform(-0.95, 0.95)
            a = math.radians(tilt) + tv * math.radians(thd)
            th_here = T * max(0.0, 1 - tv * tv) ** 0.85
            rr = R - rng.uniform(-0.3, 1.4) * max(th_here, 6)
            p = (cx + rr * math.cos(a) + rng.normal(0, 8), cy + rr * math.sin(a) + rng.normal(0, 8))
            p = (p[0] + rng.uniform(0, 40) * erode, p[1] - rng.uniform(0, 30) * erode)
            sz = rng.choice([1.0, 1.4, 2.0, 2.6])
            col = [HOT, PINK, CRIMSON, CRIMSON, MAGENTA][int(rng.integers(0, 5))]
            pe.poly([(p[0] - sz, p[1]), (p[0], p[1] - sz), (p[0] + sz, p[1]), (p[0], p[1] + sz)], col)
        L.over(pe.result())
    img = finalize(L.a, 112)
    return crop_alpha(img, L.x0, L.y0)


# ---------------------------------------------------------------- stage overlays
def flash_frame(i):
    """Release flash: stepped sunburst from about the blade (stage coords)."""
    W, H = 600, 400
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = FLASH_CENTRE
    r = np.hypot(xx - cx, yy - cy)
    th = np.arctan2(yy - cy, xx - cx)
    ray = vnoise(th * 9.0 + 40.0, 0.5, 31) * 0.7 + vnoise(th * 23.0 + 40.0, 0.5, 32) * 0.3
    rays = ray > 0.56
    vign = r > 360
    ones = np.ones_like(r)
    out = np.zeros((H, W, 4), np.float32)
    if i == 0:
        out = over(out, solid(HOT, ones * 0.88))
        out = over(out, solid(WHITE, rays * 0.96))
        out = over(out, solid(WHITE, (r < 110) * 0.98))
        out = over(out, solid(PINK, vign * 0.75))
    elif i == 1:
        out = over(out, solid(CRIMSON, ones * 0.64))
        out = over(out, solid(PINK, rays * 0.62))
        out = over(out, solid(HOT, (r < 80) * 0.85))
        out = over(out, solid(WHITE, (r < 40) * 0.9))
    elif i == 2:
        out = over(out, solid(RED, ones * 0.40))
        out = over(out, solid(CRIMSON, rays * 0.44))
    else:
        out = over(out, solid(DRED, ones * 0.18))
        out = over(out, solid(RED, rays * 0.20))
    return finalize(out, 16)


def veil_frame():
    """Optional stage dimmer for the eagle phase (stage coords, 600x400):
    dark maroon wash, slightly heavier toward the corners in soft steps."""
    W, H = 600, 400
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - 300) / 1.25, (yy - 200)) / 300.0
    a = 0.50 + 0.05 * np.floor(np.clip(r - 0.55, 0, 0.6) * 10) / 2
    return finalize(solid(MAROON, a), 8)


# ---------------------------------------------------------------- output + preview
def save_seq(name, frames):
    d = FX / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    offs = []
    for k, (im, off) in enumerate(frames):
        im.save(d / f"{k:02d}.png", optimize=True)
        offs.append([int(off[0]), int(off[1])])
    return offs


FONT = ROOT / "tools/fonts/NanumGothic-Bold.ttf"


def font(sz):
    return ImageFont.truetype(str(FONT), sz)


def stage_bg():
    """600x400 game stage (downscaled screenshot) with the original fighter
    patched out; Shanks stand-in goes at (175, 375)."""
    p = ROOT / "work/shots/si/10_s09.png"
    if p.exists():
        bg = Image.open(p).convert("RGB").resize((600, 400), Image.LANCZOS)
        patch = bg.crop((122, 318, 160, 382))
        bg.paste(patch, (78, 318))
        return bg.convert("RGBA")
    g = Image.new("RGBA", (600, 400), (40, 52, 90, 255))
    ImageDraw.Draw(g).rectangle([0, 375, 600, 400], fill=(60, 60, 70, 255))
    return g


def stand_in():
    """Kenpachi stand frame, recoloured to a dark cape + red hair, ~68 px."""
    p = ROOT / "work/shanks/base/jianba/6.png"
    if not p.exists():
        im = Image.new("RGBA", (24, 62), (0, 0, 0, 0))
        ImageDraw.Draw(im).rectangle([4, 0, 20, 61], fill=(30, 30, 40, 255))
        return im
    im = Image.open(p).convert("RGBA")
    a = np.asarray(im).copy()
    # first figure of the 4-frame strip
    cols = np.where(a[..., 3].any(axis=0))[0]
    gaps = np.where(np.diff(cols) > 2)[0]
    right = cols[gaps[0]] + 1 if len(gaps) else a.shape[1]
    a = a[:, : right]
    rgb = a[..., :3].astype(int)
    lum = rgb.mean(axis=2)
    neutral = (rgb.max(axis=2) - rgb.min(axis=2)) < 24
    white = (lum > 190) & neutral & (a[..., 3] > 0)
    a[white] = [46, 42, 54, 255]
    top = np.where(a[..., 3].any(axis=1))[0][0]
    hair = (lum < 30) & (a[..., 3] > 0)
    hair[top + 16:] = False
    a[hair] = [170, 30, 36, 255]
    im = Image.fromarray(a, "RGBA")
    return im.crop(im.getbbox())


SHANKS_SCREEN = (175, 375)


def place(dst, im, off, anchor=SHANKS_SCREEN, stage=False):
    x = off[0] if stage else anchor[0] + off[0]
    y = off[1] if stage else anchor[1] + off[1]
    tmp = Image.new("RGBA", dst.size, (0, 0, 0, 0))
    tmp.paste(im, (int(x), int(y)))
    dst.alpha_composite(tmp)


def mock(layers, title, veil=None):
    bg = stage_bg()
    if veil is not None:
        place(bg, veil, (0, 0), stage=True)
    si = stand_in()
    feet = (SHANKS_SCREEN[0] - si.width // 2, SHANKS_SCREEN[1] - si.height)
    order_back = [l for l in layers if l[2] == "back"]
    order_front = [l for l in layers if l[2] != "back"]
    for im, off, _, *rest in order_back:
        place(bg, im, off, stage=bool(rest and rest[0]))
    bg.alpha_composite(si, feet)
    for im, off, _, *rest in order_front:
        if rest and rest[0] == "anchor":
            place(bg, im, off, anchor=rest[1])
        else:
            place(bg, im, off, stage=bool(rest and rest[0] is True))
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, 599, 399], outline=(255, 255, 255, 255))
    d.text((6, 382), title, font=font(12), fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    return bg


LIGHT_ANCHORS_EAGLE = [[-40, -70], [150, -120], [60, -330], [-120, -230], [250, -260]]
LIGHT_ANCHORS_SLASH = [[30, -50], [300, -330], [360, -60], [180, -200], [-60, -150]]


def build_preview(eagle, light, slash, flash, veil):
    bgc = (16, 12, 22, 255)
    pad = 16
    Wsheet = 1860
    sections = []

    def strip(title, frames, scale, cols, cell, anchor_xy, fixed=None):
        cw, ch = cell
        rows = (len(frames) + cols - 1) // cols
        S = Image.new("RGBA", (Wsheet, 30 + rows * (ch + 22)), bgc)
        d = ImageDraw.Draw(S)
        d.text((pad, 6), title, font=font(18), fill=(255, 210, 220, 255))
        for k, (im, off) in enumerate(frames):
            cxp = pad + (k % cols) * (cw + 8)
            cyp = 30 + (k // cols) * (ch + 22)
            cellim = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            cd = ImageDraw.Draw(cellim)
            # gradient stage-ish backdrop
            for yy in range(ch):
                v = int(26 + 22 * yy / ch)
                cd.line([(0, yy), (cw, yy)], fill=(v, v - 8, v + 14, 255))
            ax, ay = anchor_xy
            gy = int(ay)
            cd.line([(0, gy), (cw, gy)], fill=(90, 80, 100, 255))
            # stand-in marker for scale (60 px tall)
            sh = max(2, int(60 * scale))
            cd.rectangle([ax - max(1, int(8 * scale)), gy - sh, ax + max(1, int(8 * scale)), gy], fill=(70, 70, 90, 255))
            small = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS) if scale != 1 else im
            if fixed is not None:
                px, py = fixed
            else:
                px, py = ax + off[0] * scale, ay + off[1] * scale
            cellim.alpha_composite(small, (int(px), int(py))) if 0 <= px and 0 <= py and px + small.width <= cw and py + small.height <= ch else _paste_clip(cellim, small, int(px), int(py))
            S.alpha_composite(cellim, (cxp, cyp))
            d.text((cxp + 3, cyp + ch + 3), f"{k:02d}  {im.width}x{im.height}  off {off[0]},{off[1]}",
                   font=font(11), fill=(230, 230, 230, 255))
        return S

    sections.append(strip("1  eagle  (0.5x, grey bar = Shanks 60px, line = ground)", eagle, 0.5, 7,
                          (252, 228), (110, 214)))
    sections.append(strip("2  lightning loop  (1x, centred on its anchor)", light, 1.0, 8, (222, 202), (111, 101)))
    sections.append(strip("3  slash  (0.4x)", slash, 0.4, 6, (296, 196), (64, 180)))
    sections.append(strip("4  flash (stage overlay, 0.3x)", [(f, (0, 0)) for f in flash] + [(veil, (0, 0))], 0.3, 6,
                          (182, 122), (0, 0), fixed=(1, 1)))
    # mocks
    m1 = mock([(eagle[7][0], eagle[7][1], "back")] +
              [(light[k % len(light)][0], light[k % len(light)][1], "front", "anchor",
                (SHANKS_SCREEN[0] + a[0], SHANKS_SCREEN[1] + a[1])) for k, a in enumerate(LIGHT_ANCHORS_EAGLE[:4])],
              "mock A: eagle hold (eagle 07 + lightning x4 + veil)", veil=veil)
    m2 = mock([(eagle[13][0], eagle[13][1], "back"), (slash[2][0], slash[2][1], "front"),
               (flash[2], (0, 0), "front", True)],
              "mock B: release (eagle 13 + slash 02 + flash 02)")
    m3 = mock([(slash[5][0], slash[5][1], "front")] +
              [(light[(k + 2) % len(light)][0], light[(k + 2) % len(light)][1], "front", "anchor",
                (SHANKS_SCREEN[0] + a[0], SHANKS_SCREEN[1] + a[1])) for k, a in enumerate(LIGHT_ANCHORS_SLASH[:3])],
              "mock C: slash peak (slash 05 + lightning x3), no veil")
    M = Image.new("RGBA", (Wsheet, 440), bgc)
    ImageDraw.Draw(M).text((pad, 6), "5  in-game mocks at 1x (600x400 stage, Shanks stand-in at x=175)", font=font(18),
                           fill=(255, 210, 220, 255))
    for k, m in enumerate((m1, m2, m3)):
        M.alpha_composite(m, (pad + k * 612, 32))
    sections.append(M)
    H = sum(s.height for s in sections) + 50
    sheet = Image.new("RGBA", (Wsheet, H), bgc)
    ImageDraw.Draw(sheet).text((pad, 10), "샹크스 S+I  카무사리 (Kamusari)  effect sequence", font=font(22),
                               fill=(255, 255, 255, 255))
    y = 44
    for s in sections:
        sheet.alpha_composite(s, (0, y))
        y += s.height
    sheet.convert("RGB").save(FX / "preview.png", optimize=True)
    for k, m in enumerate((m1, m2, m3)):
        m.convert("RGB").save(FX / f"mock_{'abc'[k]}.png", optimize=True)


def _paste_clip(dst, im, x, y):
    tmp = Image.new("RGBA", dst.size, (0, 0, 0, 0))
    tmp.paste(im, (x, y))
    dst.alpha_composite(tmp)



def shift(a, dy, dx=0):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    ys0, ys1, yd0 = max(0, -dy), h - max(0, dy), max(0, dy)
    xs0, xs1, xd0 = max(0, -dx), w - max(0, dx), max(0, dx)
    out[yd0:yd0 + ys1 - ys0, xd0:xd0 + xs1 - xs0] = a[ys0:ys1, xs0:xs1]
    return out



def bands(field, stops, gain=1.0):
    out = np.zeros(field.shape + (4,), np.float32)
    taken = np.zeros(field.shape, bool)
    for thr, col, al in stops:
        sel = (field >= thr) & ~taken
        taken |= sel
        out = over(out, solid(col, sel * min(1.0, al * gain)))
    return out



def flame_glow(mask, X, Y, sigma, stops, seed, phase=0.0, gain=1.0, stretch=(9.0, 18.0),
               lift=0, amp=1.1):
    """Glow whose extent is modulated by stretched noise -> flickering Haki
    flame tongues (rising when lift > 0)."""
    m = np.clip(mask, 0, 1).astype(np.float32)
    if lift:
        m = np.maximum(m, shift(m, -lift) * 0.85)
    g = gauss(m, sigma)
    n = fbm(X / stretch[0], (Y + phase) / stretch[1], seed, 3)
    return bands(g * (1 - amp / 2 + amp * n), stops, gain)



FLASH_CENTRE = (215.0, 300.0)



WU_ANGLE = 36.0  # degrees above horizontal (projectile flies up-forward)



WU_LAUNCH = (30.0, -70.0)  # blade tip at launch, relative to Shanks's feet



WU_S = [4, 18, 42, 82, 130, 180, 232, 286, 340, 394, 448, 502, 556, 610]



WU_SCALE = [0.42, 0.72, 0.92, 1.0, 1.0, 1.02, 1.04, 1.05, 1.06, 1.07, 1.08, 1.08, 1.08, 1.08]



def wu_dir():
    a = math.radians(WU_ANGLE)
    return math.cos(a), -math.sin(a)



def wu_body(Xs, Ys, P, sc, seed, phase):
    """Heavy two-tone Haki blade (black core, crimson/magenta rim) with a torn
    trailing edge, flying along wu_dir(). P is the body centre."""
    dx, dy = wu_dir()
    R, T, thd = 112.0 * sc, 42.0 * sc, 44.0
    lead = (P[0] + dx * T * 0.5, P[1] + dy * T * 0.5)
    cx, cy = lead[0] - dx * R, lead[1] - dy * R
    vx, vy = Xs - cx, Ys - cy
    r = np.hypot(vx, vy)
    th = np.arctan2(vy, vx) + math.radians(WU_ANGLE)
    th = (th + np.pi) % (2 * np.pi) - np.pi
    t = th / math.radians(thd)
    tt = np.clip(np.abs(t), 0, 1)
    thick = T * np.clip(1 - tt ** 1.8, 0, 1) ** 0.8
    lead_r = R + sc * 2.2 * (vnoise(t * 22.0 + phase * 0.2, 1.5, seed + 1) - 0.5)
    din = lead_r - r
    # irregular torn teeth: warped sawtooth, random height per tooth
    tw = t * 5.5 + 1.1 * vnoise(t * 2.6 + phase * 0.3, 7.5, seed + 4) + phase * 0.21
    saw = np.mod(tw, 1.0)
    tooth = _hash(np.floor(tw).astype(np.int64) + 1000, np.int64(3), seed + 5)
    amp = 0.15 + 0.85 * tooth
    back = thick * (0.74 + 0.62 * amp * saw ** 1.7)
    inside = (np.abs(t) < 1) & (din >= 0) & (din < back) & (thick > 0.5)
    out = np.zeros(Xs.shape + (4,), np.float32)

    def B(m):
        return m.astype(np.float32)

    w1 = 1.3 * sc + 0.3
    w2 = w1 + 2.0 * sc
    w3 = w2 + 3.0 * sc
    w4 = w3 + 2.0 * sc
    rimw = 2.0 + 0.10 * thick
    out = over(out, solid(CRIMSON, B(inside & (din >= back - rimw))))
    core = inside & (din >= w4) & (din < back - rimw)
    out = over(out, solid(BLACK, B(core)))
    st = vnoise((din / np.maximum(thick, 1)) * 14.0, t * 2.5 + phase * 0.1, seed + 3)
    out = over(out, solid(MAROON, B(core & (st > 0.66))))
    out = over(out, solid(DRED, B(inside & (din >= w3) & (din < w4))))
    out = over(out, solid(CRIMSON, B(inside & (din >= w2) & (din < w3))))
    out = over(out, solid(MAGENTA, B(inside & (din >= w1) & (din < w2))))
    out = over(out, solid(PINK, B(inside & (din < w1))))
    return out, inside, (cx, cy, R)



def wu_slash_frame(i):
    rng = np.random.default_rng(5000 + i)
    dx, dy = wu_dir()
    s, sc = WU_S[i], WU_SCALE[i]
    P = (WU_LAUNCH[0] + dx * s, WU_LAUNCH[1] + dy * s)
    tail = min(175.0, 20 + s * 0.85)
    ex = (P[0] - dx * tail, P[1] - dy * tail)
    x0, x1 = min(P[0], ex[0]) - 95, max(P[0], ex[0]) + 95
    y0, y1 = min(P[1], ex[1]) - 95, max(P[1], ex[1]) + 95
    L = Layer(math.floor(x0), math.floor(y0), math.ceil(x1 - x0), math.ceil(y1 - y0))
    X1, Y1 = L.grid()
    u = (X1 - P[0]) * dx + (Y1 - P[1]) * dy
    v = -(X1 - P[0]) * dy + (Y1 - P[1]) * dx
    # dark Haki smear behind the blade, ragged and tapering
    half = 46 * sc
    u_back = -14 * sc
    f = np.clip((u_back - u) / max(tail, 1), 0, 1)
    wv = half * (1 - f) ** 1.25 * (0.55 + 0.7 * vnoise(u / 10.0 + i * 3.0, v / 12.0, 900))
    trail = (u < u_back) & (u > u_back - tail) & (np.abs(v) < wv)
    lanes = vnoise(v / 3.2, u / 60.0 + i * 0.5, 910)
    L.over(solid(DRED, trail * (lanes > 0.42) * (0.55 * (1 - f) + 0.05)))
    L.over(solid(BLACK, trail * (lanes > 0.72) * (0.6 * (1 - f))))
    L.over(solid(CRIMSON, trail * (lanes > 0.36) * (lanes < 0.42) * (0.7 * (1 - f))))
    # streaks along the path
    pl = Pen(L)
    for k in range(4):
        off = rng.uniform(-half * 0.8, half * 0.8)
        a = rng.uniform(4, 16) * sc
        b = tail * rng.uniform(0.45, 1.0)
        p0 = (P[0] - dx * a - dy * 0 + (-dy) * 0, P[1])
        p0 = (P[0] - dx * a + dy * off * -1 * -1, P[1] - dy * a - dx * off * -1 * -1)
        # perpendicular unit is (-dy, dx) in (x, y) for v; place along it
        q0 = (P[0] - dx * a + (-dy) * off, P[1] - dy * a + dx * off)
        q1 = (P[0] - dx * b + (-dy) * off * 0.6, P[1] - dy * b + dx * off * 0.6)
        pl.line([q0, q1], [CRIMSON, BLACK, PINK][k % 3], [1.6, 2.4, 1.0][k % 3] * max(0.6, sc))
        del p0
    L.over(pl.result() * 0.85)
    # the blade itself at 2x
    ss = 2
    Xs, Ys = L.grid(ss)
    body, inside, (cx, cy, R) = wu_body(Xs, Ys, P, sc, 70, i * 1.3)
    A = downsample(body, ss)
    M = downsample(inside[..., None].astype(np.float32), ss)[..., 0]
    L.over(stepped_glow(M, 3.0 + 2.0 * sc, [(0.42, MAGENTA, 0.70), (0.20, CRIMSON, 0.46), (0.07, DRED, 0.26)]))
    L.over(A)
    # black lightning: trailing tail + bolts clinging to the blade
    bolts = []
    back_ang = math.atan2(-dy, -dx)
    for k in range(2 if i > 1 else 1):
        off = rng.uniform(-0.5, 0.5) * half
        p0 = (P[0] - dx * 22 * sc + (-dy) * off, P[1] - dy * 22 * sc + dx * off)
        bolts += bolt_tree(rng, p0, back_ang + rng.uniform(-0.15, 0.15), max(30.0, tail * rng.uniform(0.6, 1.0)), 1,
                           branches=(0, 1))
    for k in range(3 if i > 1 else 1):
        tv = rng.uniform(-0.8, 0.8)
        a = -math.radians(WU_ANGLE) + tv * math.radians(44)
        rr = R - rng.uniform(0, 14) * sc
        p0 = (cx + rr * math.cos(a), cy + rr * math.sin(a))
        ang = a + math.copysign(math.pi / 2, tv) + rng.uniform(-0.35, 0.35)
        bolts += bolt_tree(rng, p0, ang, rng.uniform(18, 36) * sc, 1, branches=(0, 1))
    draw_bolts(L, bolts, rng, core=2.2 * max(0.7, sc), halo=1.2, glow_sigma=2.6)
    # embers shed along the trail
    pe = Pen(L)
    for k in range(int(8 + 16 * min(1.0, s / 200))):
        uu = -rng.uniform(4, tail)
        vv = rng.normal(0, half * 0.55)
        p = (P[0] + dx * uu + (-dy) * vv, P[1] + dy * uu + dx * vv)
        sz = rng.choice([0.9, 1.3, 1.8])
        col = [HOT, PINK, CRIMSON, CRIMSON][int(rng.integers(0, 4))]
        pe.poly([(p[0] - sz, p[1]), (p[0], p[1] - sz), (p[0] + sz, p[1]), (p[0], p[1] + sz)], col)
    L.over(pe.result())
    # hit box from the blade body
    ys_, xs_ = np.where(M > 0.5)
    hb = [round(L.x0 + (xs_.min() + xs_.max() + 1) / 2), round(L.y0 + (ys_.min() + ys_.max() + 1) / 2),
          int(xs_.max() - xs_.min() + 1), int(ys_.max() - ys_.min() + 1)]
    img, off = crop_alpha(finalize(L.a, 96), L.x0, L.y0)
    return img, off, hb



WU_LAUNCH_FR = [
    dict(a=10, u0=0, burst=1.0, bolts=2),
    dict(a=22, u0=5, burst=0.75, bolts=2),
    dict(a=34, u0=10, burst=0.4, bolts=2),
    dict(a=45, u0=15, bolts=1, tear=0.15),
    dict(a=54, u0=19, bolts=1, tear=0.38, embers=12),
    dict(a=61, u0=22, tear=0.62, embers=12),
    dict(a=66, u0=24, tear=0.86, embers=8),
]



def spiky_star(pen, c, R, rin, spikes, fill, rim, rimw, rot=0.0):
    pts = []
    n = len(spikes)
    for k, (a, ln) in enumerate(spikes):
        a = a + rot
        pts.append((c[0] + math.cos(a) * R * ln, c[1] + math.sin(a) * R * ln))
        b = a + math.pi / n
        pts.append((c[0] + math.cos(b) * rin, c[1] + math.sin(b) * rin))
    if rim is not None:
        pen.poly(pts, rim, rim, rimw)
    pen.poly(pts, fill)
    return pts



def wu_launch_frame(i, spec):
    rng = np.random.default_rng(5500 + i)
    dx, dy = wu_dir()
    a, u0 = spec["a"], spec["u0"]
    c = (WU_LAUNCH[0] + dx * u0, WU_LAUNCH[1] + dy * u0)
    L = Layer(c[0] - 110, c[1] - 110, 220, 220)
    ss = 2
    Xs, Ys = L.grid(ss)
    u = (Xs - c[0]) * dx + (Ys - c[1]) * dy
    v = -(Xs - c[0]) * dy + (Ys - c[1]) * dx
    acc = np.zeros(Xs.shape + (4,), np.float32)
    q = np.hypot(u / (a * 0.45), v / a)
    d = (1 - q) * a  # ~px inward from the ring's outer edge
    ang = np.arctan2(v, u / 0.45)
    keep = np.ones(Xs.shape, bool)
    if spec.get("tear"):
        keep = vnoise(ang * 3.2 + 10, i * 0.7, 66) > spec["tear"]
    bw = 3.0 + 4.0 * (1 - spec.get("tear", 0))
    ring = keep & (d >= 0) & (d < bw + 3.5)

    def B(m, al=1.0):
        return m.astype(np.float32) * al

    # distortion ripple: a fainter, larger ring with a dark inner shadow
    q2 = np.hypot(u / (a * 1.3 * 0.45), v / (a * 1.3))
    d2 = (1 - q2) * a * 1.3
    acc = over(acc, solid(MAROON, B((d2 >= 1.2) & (d2 < 6) & keep, 0.35)))
    acc = over(acc, solid(PINK, B((d2 >= 0) & (d2 < 1.2), 0.5 * (1 - spec.get("tear", 0)))))
    acc = over(acc, solid(MAGENTA, B(ring & (d < 1.4))))
    acc = over(acc, solid(CRIMSON, B(ring & (d >= 1.4) & (d < 3.0))))
    acc = over(acc, solid(BLACK, B(ring & (d >= 3.0) & (d < 3.0 + bw * 0.8))))
    acc = over(acc, solid(CRIMSON, B(ring & (d >= 3.0 + bw * 0.8))))
    A = downsample(acc, ss)
    M = downsample(B(ring)[..., None], ss)[..., 0]
    L.over(stepped_glow(M, 3.0, [(0.4, MAGENTA, 0.55), (0.18, CRIMSON, 0.34), (0.06, DRED, 0.18)]))
    L.over(A)
    burst = spec.get("burst", 0)
    if burst:
        pb = Pen(L)
        brng = np.random.default_rng(5590)
        spikes = [(k * 2 * math.pi / 10 + brng.uniform(-0.15, 0.15), brng.uniform(0.55, 1.0)) for k in range(10)]
        Rb = 10 + 20 * burst
        spiky_star(pb, c, Rb, Rb * 0.32, spikes, BLACK, CRIMSON, 3.2, rot=i * 0.2)
        pb.disc(c, 3.5 * burst + 1.5, PINK)
        pb.disc(c, 1.6 * burst + 0.8, HOT)
        # speed spikes radiating along the firing direction
        for k in range(7):
            aa = math.atan2(dy, dx) + brng.uniform(-1.1, 1.1)
            r0, r1 = Rb * 0.8, Rb * 0.8 + brng.uniform(20, 46) * burst
            w = brng.uniform(1.5, 3.0)
            p0 = (c[0] + math.cos(aa) * r0, c[1] + math.sin(aa) * r0)
            p1 = (c[0] + math.cos(aa) * r1, c[1] + math.sin(aa) * r1)
            nx, ny = -math.sin(aa) * w, math.cos(aa) * w
            pb.poly([(p0[0] + nx, p0[1] + ny), p1, (p0[0] - nx, p0[1] - ny)], BLACK, CRIMSON, 1.0)
        mk = pb.result()
        L.over(stepped_glow(mk[..., 3], 3.5, [(0.35, MAGENTA, 0.6), (0.15, CRIMSON, 0.36), (0.05, DRED, 0.2)]))
        L.over(mk)
    nb = spec.get("bolts", 0)
    if nb:
        bolts = []
        for k in range(nb):
            t0 = rng.uniform(-math.pi, math.pi)
            p0 = (c[0] + (a * 0.45 * math.cos(t0)) * dx - (a * math.sin(t0)) * dy,
                  c[1] + (a * 0.45 * math.cos(t0)) * dy + (a * math.sin(t0)) * dx)
            aa = math.atan2(p0[1] - c[1], p0[0] - c[0]) + rng.uniform(-0.5, 0.5)
            bolts += bolt_tree(rng, p0, aa, rng.uniform(22, 42), 1, branches=(0, 1))
        draw_bolts(L, bolts, rng, core=2.0, halo=1.1, glow_sigma=2.4)
    ne = spec.get("embers", 0)
    if ne:
        pe = Pen(L)
        for k in range(ne):
            t0 = rng.uniform(-math.pi, math.pi)
            rr = a * rng.uniform(0.9, 1.25)
            p = (c[0] + (rr * 0.45 * math.cos(t0)) * dx - (rr * math.sin(t0)) * dy,
                 c[1] + (rr * 0.45 * math.cos(t0)) * dy + (rr * math.sin(t0)) * dx)
            sz = rng.choice([0.9, 1.3, 1.8])
            pe.poly([(p[0] - sz, p[1]), (p[0], p[1] - sz), (p[0] + sz, p[1]), (p[0], p[1] + sz)],
                    [HOT, PINK, CRIMSON][int(rng.integers(0, 3))])
        L.over(pe.result())
    return crop_alpha(finalize(L.a, 64), L.x0, L.y0)



WU_IMPACT_FR = [
    dict(R=30, core=9, bolts=1, glow=1.0),
    dict(R=64, core=7, bolts=3, needles=1.0, glow=1.2),
    dict(R=74, hole=0.42, bolts=4, needles=0.6, glow=1.0),
    dict(R=78, hole=0.66, shards=0.25, bolts=3, glow=0.8),
    dict(shards=0.55, bolts=2, embers=26, glow=0.5),
    dict(shards=0.85, bolts=1, embers=22, glow=0.3),
    dict(embers=14, bolts=1, glow=0.0),
]



def wu_impact_frame(i, spec):
    rng = np.random.default_rng(6000 + i)
    srng = np.random.default_rng(6100)
    spikes = [(k * 2 * math.pi / 14 + srng.uniform(-0.12, 0.12), srng.uniform(0.55, 1.0)) for k in range(14)]
    L = Layer(-80, -80, 160, 160)
    c = (0.0, 0.0)
    R = spec.get("R", 0)
    if R:
        ps = Pen(L)
        spiky_star(ps, c, R, R * 0.36, spikes, BLACK, CRIMSON, 5.0, rot=i * 0.05)
        S = ps.result()
        hole = spec.get("hole", 0)
        if hole:
            X, Y = L.grid()
            ang = np.arctan2(Y, X)
            rh = R * hole * (0.8 + 0.4 * vnoise(ang * 4 + 5, 0.5, 61 + i))
            rr = np.hypot(X, Y)
            H = rr < rh
            S = S * (~H)[..., None]
            S = over(S, solid(CRIMSON, (rr >= rh) & (rr < rh + 2.5) & (S[..., 3] > 0.5)))
        L.over(stepped_glow(S[..., 3], 4.0, [(0.40, MAGENTA, 0.75), (0.20, CRIMSON, 0.5), (0.07, DRED, 0.28)],
                            gain=spec.get("glow", 1.0)))
        L.over(S)
    nd = spec.get("needles", 0)
    if nd:
        pn = Pen(L)
        for k in range(10):
            a = srng.uniform(0, 2 * math.pi)
            r1 = 76 * nd * srng.uniform(0.75, 1.0)
            w = 2.2
            nx, ny = -math.sin(a) * w, math.cos(a) * w
            pn.poly([(nx, ny), (math.cos(a) * r1, math.sin(a) * r1), (-nx, -ny)], BLACK, CRIMSON, 1.0)
        L.over(pn.result())
    sh = spec.get("shards", 0)
    if sh:
        pd = Pen(L)
        for k, (a, ln) in enumerate(spikes):
            rr0 = (0.5 + 0.7 * sh) * 62
            if rr0 > 76:
                continue
            sz = (1 - 0.6 * sh) * 18 * ln
            b = (math.cos(a) * rr0, math.sin(a) * rr0)
            w = sz * 0.35
            nx, ny = -math.sin(a) * w, math.cos(a) * w
            tri = [(b[0] + nx, b[1] + ny), (b[0] + math.cos(a) * sz, b[1] + math.sin(a) * sz), (b[0] - nx, b[1] - ny)]
            pd.poly(tri, BLACK, CRIMSON, 1.6)
        L.over(pd.result())
    core = spec.get("core", 0)
    if core:
        pc = Pen(L)
        pc.disc(c, core, PINK)
        pc.disc(c, core * 0.5, HOT)
        L.over(pc.result())
    nb = spec.get("bolts", 0)
    if nb:
        bolts = []
        for k in range(nb):
            a = rng.uniform(0, 2 * math.pi)
            p0 = (math.cos(a) * 6, math.sin(a) * 6)
            tree = bolt_tree(rng, p0, a, rng.uniform(42, 66), 1, branches=(0, 2))
            for pts, lvl in tree:
                np.clip(pts, -74, 74, out=pts)
            bolts += tree
        draw_bolts(L, bolts, rng, core=2.2, halo=1.2, glow_sigma=2.6)
    ne = spec.get("embers", 0)
    if ne:
        pe = Pen(L)
        for k in range(ne):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(20, 72)
            p = (math.cos(a) * rr, math.sin(a) * rr - (6 - spec.get("glow", 0) * 6))
            sz = rng.choice([0.9, 1.3, 1.8])
            pe.poly([(p[0] - sz, p[1]), (p[0], p[1] - sz), (p[0] + sz, p[1]), (p[0], p[1] + sz)],
                    [HOT, PINK, CRIMSON, CRIMSON][int(rng.integers(0, 4))])
        L.over(pe.result())
    return finalize(L.a, 64), (L.x0, L.y0)



def build_preview_wu(launch, slash, impact, path):
    bgc = (16, 12, 22, 255)
    Wsheet = 1460
    pad = 16
    secs = []

    def label(d, xy, text, sz=12, col=(230, 230, 230, 255)):
        d.text(xy, text, font=font(sz), fill=col)

    def cellbg(w, h):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        d = ImageDraw.Draw(im)
        for yy in range(h):
            v = int(26 + 22 * yy / h)
            d.line([(0, yy), (w, yy)], fill=(v, v - 8, v + 14, 255))
        return im

    # strips
    def strip(title, frames, scale, cols, cell, origin):
        cw, ch = cell
        rows = (len(frames) + cols - 1) // cols
        S = Image.new("RGBA", (Wsheet, 30 + rows * (ch + 20)), bgc)
        d = ImageDraw.Draw(S)
        label(d, (pad, 6), title, 18, (255, 210, 220, 255))
        for k, (im, off) in enumerate(frames):
            cx_, cy_ = pad + (k % cols) * (cw + 8), 30 + (k // cols) * (ch + 20)
            cell_ = cellbg(cw, ch)
            sm = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS) \
                if scale != 1 else im
            _paste_clip(cell_, sm, int(origin[0] + off[0] * scale), int(origin[1] + off[1] * scale))
            S.alpha_composite(cell_, (cx_, cy_))
            label(d, (cx_ + 3, cy_ + ch + 3), f"{k:02d}  {im.width}x{im.height}  off {off[0]},{off[1]}", 11)
        return S

    secs.append(strip("wu_launch  (1x, cross = launch point)", launch, 1.0, 7, (196, 170),
                      (98 - WU_LAUNCH[0], 85 - WU_LAUNCH[1])))
    secs.append(strip("wu_slash  (0.4x, each cell shows the whole path; grey bar = Shanks)", slash, 0.4, 7, (196, 170),
                      (30, 160)))
    secs.append(strip("wu_impact  (1x, centred on its anchor)", impact, 1.0, 7, (196, 170), (98, 85)))
    # contrast panel: Mihawk vs Shanks at 2x
    C = Image.new("RGBA", (Wsheet, 420), bgc)
    d = ImageDraw.Draw(C)
    label(d, (pad, 6), "contrast at 2x:  Mihawk (left)  vs  Shanks W+U (right)", 18, (255, 210, 220, 255))
    left = cellbg(700, 360)
    right = cellbg(700, 360)
    mx = 10
    for sid in (702, 752, 1032):
        p = ROOT / f"work/mihawk/sprites/{sid}.png"
        if p.exists():
            im = Image.open(p).convert("RGBA")
            if sid == 1032:
                im = im.resize((im.width, im.height), Image.NEAREST)
                left.alpha_composite(im, (300, 190))
            else:
                im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
                left.alpha_composite(im, (mx, 10))
                mx += im.width + 6
    ld = ImageDraw.Draw(left)
    label(ld, (10, 300), "Mihawk 702 / 752 (2x), 1032 (1x): thin, clean, solid violet/blue", 13)
    label(ld, (10, 318), "crescents, white core, smooth gradient: elegant precision", 13)
    sim, soff = slash[5]
    big = sim.resize((sim.width * 2, sim.height * 2), Image.NEAREST)
    _paste_clip(right, big, 0, 0)
    imp = impact[2][0].resize((320, 320), Image.NEAREST)
    _paste_clip(right, imp, 420, 20)
    rd = ImageDraw.Draw(right)
    label(rd, (10, 300), "Shanks wu_slash 05 + wu_impact 02 (2x): heavy black core, crimson/magenta", 13)
    label(rd, (10, 318), "rim, torn trailing edge, clinging black lightning, embers: brute force", 13)
    C.alpha_composite(left, (pad, 36))
    C.alpha_composite(right, (pad + 716, 36))
    secs.append(C)
    # mocks: in-game moment + time-lapse of the whole path with hit boxes
    M = Image.new("RGBA", (Wsheet, 450), bgc)
    d = ImageDraw.Draw(M)
    label(d, (pad, 6), "in-game mock at 1x (stand-in feet at screen 175,375)  |  path time-lapse with wu_path hit boxes",
          18, (255, 210, 220, 255))
    m1 = mock([(launch[2][0], launch[2][1], "front"), (slash[6][0], slash[6][1], "front")],
              "W+U: launch 02 + slash 06")
    m2 = stage_bg()
    si = stand_in()
    m2.alpha_composite(si, (SHANKS_SCREEN[0] - si.width // 2, SHANKS_SCREEN[1] - si.height))
    for k in range(2, len(slash), 2):
        place(m2, slash[k][0], slash[k][1])
    d2 = ImageDraw.Draw(m2)
    for k, (cx_, cy_, w, h) in enumerate(path):
        X0, Y0 = SHANKS_SCREEN[0] + cx_ - w / 2, SHANKS_SCREEN[1] + cy_ - h / 2
        d2.rectangle([X0, Y0, X0 + w, Y0 + h], outline=(80, 255, 120, 255) if k % 2 == 0 else (80, 200, 255, 255))
    d2.rectangle([0, 0, 599, 399], outline=(255, 255, 255, 255))
    d2.text((6, 382), "slash 02,04,..,12 + hit boxes (all 14 drawn)", font=font(12), fill=(255, 255, 255, 255),
            stroke_width=2, stroke_fill=(0, 0, 0, 255))
    M.alpha_composite(m1, (pad, 36))
    M.alpha_composite(m2, (pad + 616, 36))
    secs.append(M)
    H = sum(s.height for s in secs) + 50
    sheet = Image.new("RGBA", (Wsheet, H), bgc)
    ImageDraw.Draw(sheet).text((pad, 10), "샹크스 W+U  diagonal Haki slash (up-forward projectile)", font=font(22),
                               fill=(255, 255, 255, 255))
    y = 44
    for s in secs:
        sheet.alpha_composite(s, (0, y))
        y += s.height
    sheet.convert("RGB").save(FX / "preview_wu.png", optimize=True)
    m1.convert("RGB").save(FX / "mock_wu.png", optimize=True)
    m2.convert("RGB").save(FX / "mock_wu_path.png", optimize=True)



def render_wu(layout):
    launch = [wu_launch_frame(i, s) for i, s in enumerate(WU_LAUNCH_FR)]
    sl = [wu_slash_frame(i) for i in range(len(WU_S))]
    slash = [(im, off) for im, off, _ in sl]
    path = [hb for _, _, hb in sl]
    impact = [wu_impact_frame(i, s) for i, s in enumerate(WU_IMPACT_FR)]
    layout["_doc_wu"] = ("W+U (diagonal up-forward slash projectile). wu_launch / wu_slash offsets: top-left "
                         "relative to Shanks's origin at the moment of launch (keep the effect in world space "
                         "if he moves; mirror x when facing left: x' = -(x + w)). wu_path: per wu_slash frame "
                         "[centre_x, centre_y, w, h] of the blade body (axis-aligned hit box), same origin. "
                         "wu_impact: offsets relative to the hit point the burst is centred on.")
    layout["wu_launch"] = save_seq("wu_launch", launch)
    layout["wu_launch_point"] = list(WU_LAUNCH)
    layout["wu_angle_deg"] = WU_ANGLE
    layout["wu_slash"] = save_seq("wu_slash", slash)
    layout["wu_path"] = path
    layout["wu_impact"] = save_seq("wu_impact", impact)
    layout.setdefault("sizes", {})
    for name in ("wu_launch", "wu_slash", "wu_impact"):
        layout["sizes"][name] = [list(Image.open(p).size) for p in sorted((FX / name).glob("*.png"))]
    build_preview_wu(launch, slash, impact, path)
    print(f"frames: wu_launch {len(launch)}, wu_slash {len(slash)}, wu_impact {len(impact)}")



HK_DARK = (122, 10, 30)  # #7A0A1E



HK_RIM = (215, 38, 61)  # #D7263D



def draw_bolts_hk(layer, bolts, rng, core=2.0, halo=1.2, glow_sigma=2.6, gain=1.0, flicker=True):
    """Black lightning in the Haoshoku palette: no white, crimson rim only."""
    pg, ph, pr, pc, pf = (Pen(layer) for _ in range(5))
    for pts, lvl in bolts:
        k = 0.66 ** lvl
        P = [tuple(p) for p in pts]
        cw = max(1.0, core * k)
        pg.line(P, WHITE, cw + 2 * halo * k + 2)
        ph.line(P, HK_DARK, cw + 2 * halo * k)
        pr.line(P, HK_RIM, cw + 0.9)
        pc.line(P, BLACK, cw)
        if flicker and lvl == 0 and len(pts) > 3:
            i = int(rng.integers(0, max(1, len(pts) - 4)))
            seg = pts[i:i + int(rng.integers(2, 5))]
            if len(seg) >= 2:
                d = seg[-1] - seg[0]
                nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
                jit = seg + nrm * rng.choice([-1, 1]) * (cw / 2 + halo + rng.uniform(1.5, 3.5)) \
                    + rng.normal(0, 1.0, seg.shape)
                pf.line([tuple(p) for p in jit], HK_RIM, 1.0)
        if lvl == 0:
            pf.disc(tuple(pts[-1]), 1.2, HK_RIM)
    layer.over(stepped_glow(pg.result()[..., 3], glow_sigma,
                            [(0.38, HK_RIM, 0.42), (0.18, HK_DARK, 0.28), (0.07, MAROON, 0.14)], gain=gain))
    layer.over(ph.result())
    layer.over(pr.result())
    layer.over(pc.result())
    layer.over(pf.result())



HAKI_C = (0.0, -40.0)  # body centre the burst is centred on (relative to the feet)



HAKI_FR = [
    # r = ring radius, bw = band width, jag = ragged-edge amplitude, haze = interior alpha
    dict(r=26, bw=11, jag=6, haze=0.34, bolts=3, lines=10),
    dict(r=50, bw=17, jag=10, haze=0.32, bolts=4, lines=14, ground=1),
    dict(r=74, bw=21, jag=13, haze=0.30, bolts=4, lines=16, ground=2),
    dict(r=98, bw=22, jag=14, haze=0.27, bolts=5, lines=14, ground=2),
    dict(r=120, bw=21, jag=14, haze=0.24, bolts=5, lines=10, ground=2),
    dict(r=139, bw=19, jag=13, haze=0.21, bolts=5, lines=6, ground=2),
    dict(r=155, bw=17, jag=12, haze=0.18, bolts=5, ground=2),
    dict(r=167, bw=15, jag=11, haze=0.15, bolts=4, ground=1),
    dict(r=175, bw=13, jag=10, haze=0.12, bolts=4, ground=1, tear=0.12),
    dict(r=180, bw=11, jag=9, haze=0.09, bolts=3, tear=0.36, fade=0.85, embers=30),
    dict(r=184, bw=9, jag=8, haze=0.05, bolts=2, tear=0.6, fade=0.65, embers=26),
    dict(r=187, bw=7, jag=7, haze=0.02, bolts=1, tear=0.84, fade=0.42, embers=18),
]



def haki_ring_frame(i, spec):
    rng = np.random.default_rng(7000 + i)
    c = HAKI_C
    r, bw, jag_a = spec["r"], spec["bw"], spec["jag"]
    fade = spec.get("fade", 1.0)
    tear = spec.get("tear", 0.0)
    ext = int(r + jag_a + 46)
    gy = 24  # frame bottom below the feet (ground wave)
    L = Layer(-ext, c[1] - ext, 2 * ext, int(ext + gy - c[1]))
    ss = 2
    Xs, Ys = L.grid(ss)
    dx, dy = Xs - c[0], Ys - c[1]
    rr = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    cs, sn = np.cos(th), np.sin(th)
    # ragged outer edge: irregular outward flame teeth, seamless around the circle
    N = 34
    tw = th * N / (2 * np.pi) + 1.4 * vnoise(cs * 2.2 + 10, sn * 2.2 + i * 0.35, 71)
    saw = np.mod(tw, 1.0)
    tooth = _hash(np.mod(np.floor(tw).astype(np.int64), N) + 500, np.int64(i % 3), 72)
    jag = jag_a * (0.15 + 0.85 * tooth) * (1 - saw) ** 1.4
    d = (r + jag) - rr  # px inside the ragged outer edge
    keep = np.ones(Xs.shape, bool)
    if tear:
        keep = vnoise(cs * 4.0 + 20, sn * 4.0 + i * 0.6, 73) > tear
    band = keep & (d >= 0) & (d < bw + jag)
    above = np.clip((8.0 - Ys) / 5.0, 0, 1)  # the dome sits on the ground

    def B(m, a=1.0):
        return m.astype(np.float32) * above * (a * fade)

    acc = np.zeros(Xs.shape + (4,), np.float32)
    # dark heat-haze inside the dome
    inner = rr < r - bw * 0.3
    acc = over(acc, solid(MAROON, B(inner, spec["haze"] * 1.25) * (0.5 + 0.5 * np.clip(rr / r, 0, 1))))
    shell = keep & (d >= bw + jag) & (d < bw + jag + 4 + r * 0.06)
    acc = over(acc, solid(HK_DARK, B(shell, 0.42)))
    shell2 = keep & (d >= bw + jag + 4 + r * 0.06) & (d < bw + jag + 8 + r * 0.12)
    acc = over(acc, solid(HK_DARK, B(shell2, 0.2)))
    hz = vnoise(Xs / 34.0 + i * 0.4, (Ys + 5 * np.sin(Xs / 21.0 + i)) / 3.6, 74)
    acc = over(acc, solid(HK_DARK, B(inner & (hz > 0.64), spec["haze"] * 0.9)))
    acc = over(acc, solid(BLACK, B(inner & (hz < 0.16), spec["haze"] * 0.8)))
    # ring band: crimson outer rim -> dark crimson -> black -> dark crimson inner rim
    acc = over(acc, solid(HK_DARK, B(band & (d >= bw + jag - 2.5))))
    acc = over(acc, solid(BLACK, B(band & (d >= 3.4) & (d < bw + jag - 2.5))))
    acc = over(acc, solid(HK_DARK, B(band & (d >= 1.6) & (d < 3.4))))
    acc = over(acc, solid(HK_RIM, B(band & (d < 1.6))))
    A = downsample(acc, ss)
    M = downsample(B(band)[..., None], ss)[..., 0]
    L.over(stepped_glow(M, 4.0, [(0.40, HK_RIM, 0.55), (0.20, HK_DARK, 0.36), (0.07, MAROON, 0.2)], gain=fade))
    # ground shock wave (flattened ring along the floor)
    X1, Y1 = L.grid()
    rx, ry = r * 1.02, max(3.0, r * 0.1)
    q = np.hypot(X1 / rx, (Y1 - 2) / ry)
    gd = (1 - q) * ry
    gw = (gd >= 0) & (gd < max(2.0, ry * 0.45)) & (Y1 > -2)
    gw &= vnoise(X1 / 9.0 + i, 0.5, 75) > tear
    L.over(solid(HK_RIM, gw * (gd < 1.0) * fade))
    L.over(solid(BLACK, gw * (gd >= 1.0) * 0.85 * fade))
    # pressure lines bursting outward (early frames)
    nl = spec.get("lines", 0)
    if nl:
        pl = Pen(L)
        for k in range(nl):
            a = rng.uniform(-math.pi, 0.15) if rng.random() < 0.8 else rng.uniform(0.15, math.pi - 0.15)
            r0 = r + jag_a + rng.uniform(2, 8)
            r1 = r0 + rng.uniform(14, 34)
            p0 = (c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0)
            p1 = (c[0] + math.cos(a) * r1, c[1] + math.sin(a) * r1)
            if max(p0[1], p1[1]) > 6:
                continue
            w = rng.uniform(1.0, 2.2)
            nx, ny = -math.sin(a) * w, math.cos(a) * w
            pl.poly([(p0[0] + nx, p0[1] + ny), p1, (p0[0] - nx, p0[1] - ny)], BLACK, HK_RIM, 0.8)
        L.over(pl.result() * fade)
    L.over(A)
    # black lightning crackling along the ring, a few bolts down to the ground
    bolts = []
    for k in range(spec.get("bolts", 0)):
        a = rng.uniform(-math.pi, 0.0)
        rr0 = r - bw * 0.4
        p0 = (c[0] + math.cos(a) * rr0, c[1] + math.sin(a) * rr0)
        ang = a + rng.choice([-1, 1]) * (math.pi / 2 - rng.uniform(0.0, 0.5))
        bolts += bolt_tree(rng, p0, ang, rng.uniform(26, 64) * max(0.45, min(1.0, r / 150)), 1, branches=(0, 2))
    for k in range(2 if r > 40 else 1):
        a0 = rng.uniform(-math.pi * 0.95, -0.35)
        span = rng.uniform(0.35, 0.7) * min(1.0, 90.0 / max(r, 1)) * 1.6
        anchors = []
        for tv in np.linspace(a0, a0 + span, 6):
            rv = r - bw * rng.uniform(0.2, 0.7)
            anchors.append((c[0] + math.cos(tv) * rv, c[1] + math.sin(tv) * rv))
        pts = []
        for p0, p1 in zip(anchors[:-1], anchors[1:]):
            pts += [tuple(v) for v in bolt_points(rng, p0, p1, 0.4, 3)[:-1]]
        pts.append(anchors[-1])
        bolts.append((np.array(pts), 0))
    for k in range(spec.get("ground", 0)):
        side = -1 if k % 2 == 0 else 1
        y0 = -rng.uniform(25, min(90, 15 + r * 0.6))
        x0 = side * math.sqrt(max(1.0, r * r - (y0 - c[1]) ** 2)) * 0.97
        tgt = (x0 + side * rng.uniform(4, 22), rng.uniform(-1, 3))
        main = bolt_points(rng, (x0, y0), tgt, 0.32, 4)
        bolts.append((main, 0))
        if rng.random() < 0.7:
            j = int(rng.integers(2, len(main) - 2))
            bolts += [(p, 1) for p, _ in bolt_tree(rng, main[j], math.atan2(tgt[1] - y0, tgt[0] - x0)
                                                   + side * 0.6, 14, 0)]
    if bolts:
        for pts, _ in bolts:
            pts[:, 1] = np.minimum(pts[:, 1], 4)
        draw_bolts_hk(L, bolts, rng, core=2.0, halo=1.2, gain=fade)
    # embers when it fades
    ne = spec.get("embers", 0)
    if ne:
        pe = Pen(L)
        for k in range(ne):
            a = rng.uniform(-math.pi, 0.05)
            rr0 = r + rng.uniform(-14, 10)
            p = (c[0] + math.cos(a) * rr0, c[1] + math.sin(a) * rr0 - rng.uniform(0, 8))
            sz = rng.choice([0.9, 1.3, 1.7])
            pe.poly([(p[0] - sz, p[1]), (p[0], p[1] - sz), (p[0] + sz, p[1]), (p[0], p[1] + sz)],
                    [HK_RIM, HK_DARK, CRIMSON][int(rng.integers(0, 3))])
        L.over(pe.result())
    return crop_alpha(finalize(L.a, 96), L.x0, L.y0)



AURA_N = 6



def aura_frame(i):
    """Soft looping black-red sword aura: rising flame tongues + dark wisps
    (seamless: cross-faded noise), clear centre so the blade stays visible."""
    rng = np.random.default_rng(7500 + i)
    L = Layer(-45, -45, 90, 90)
    X, Y = L.grid()
    t = i / AURA_N

    def loop(seed, sx, sy, speed):
        a = fbm(X / sx, (Y + t * speed) / sy, seed, 3)
        b = fbm(X / sx, (Y + (t - 1) * speed) / sy, seed, 3)
        return a * (1 - t) + b * t

    n = loop(801, 6.5, 12.0, 26.0)
    n2 = loop(802, 9.0, 7.0, 34.0)
    yy = (Y + 4) / np.where(Y < -4, 30.0, 17.0)  # taller above: flames rise
    env = np.exp(-(X / 23.0) ** 2 - yy ** 2)
    env *= np.clip((43 - np.hypot(X, Y)) / 9.0, 0, 1)
    centre = 0.4 + 0.6 * np.clip(np.hypot(X, Y) / 13.0, 0, 1)
    F = env * (0.2 + 1.15 * n)
    red_a = np.clip((F - 0.42) * 1.25, 0, 0.42) * centre
    red_a = gauss(red_a.astype(np.float32), 0.8)
    mix = np.clip((F - 0.42) / 0.45, 0, 1)[..., None]
    col = np.array(HK_DARK, np.float32) / 255 * (1 - mix) + np.array(HK_RIM, np.float32) / 255 * mix
    out = np.zeros((90, 90, 4), np.float32)
    out[..., :3] = col * red_a[..., None]
    out[..., 3] = red_a
    wisp = np.exp(-((n2 - 0.5) / 0.045) ** 2) * np.clip(env * 1.5, 0, 1) * centre
    out = over(out, solid(BLACK, gauss(wisp.astype(np.float32), 0.7) * 0.5))
    # one or two tiny dark crackles
    Lb = Layer(-45, -45, 90, 90)
    bolts = []
    for k in range(1 + (i % 2)):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(12, 24)
        p0 = (math.cos(a) * rr, math.sin(a) * rr * 0.9 - 4)
        ln = rng.uniform(8, 14)
        bolts.append((bolt_points(rng, p0, (p0[0] + math.cos(a + 1.3) * ln, p0[1] + math.sin(a + 1.3) * ln),
                                  0.4, 3), 0))
    draw_bolts_hk(Lb, bolts, rng, core=1.0, halo=0.6, glow_sigma=1.4, gain=0.6, flicker=False)
    out = over(out, Lb.a * 0.8)
    return finalize_soft(out), (L.x0, L.y0)



def build_preview_haki(ring, aura):
    bgc = (16, 12, 22, 255)
    Wsheet = 1460
    pad = 16
    secs = []

    def cellbg(w, h, bright=False):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        d = ImageDraw.Draw(im)
        for yy in range(h):
            if bright:
                d.line([(0, yy), (w, yy)], fill=(90 + yy * 60 // h, 140 + yy * 40 // h, 200, 255))
            else:
                v = int(26 + 22 * yy / h)
                d.line([(0, yy), (w, yy)], fill=(v, v - 8, v + 14, 255))
        return im

    S = Image.new("RGBA", (Wsheet, 2 * (150 + 20) + 34), bgc)
    d = ImageDraw.Draw(S)
    d.text((pad, 6), "haki_ring (S+U)  0.5x, line = ground, grey bar = Shanks 68 px", font=font(18),
           fill=(255, 210, 220, 255))
    for k, (im, off) in enumerate(ring):
        cw, ch = 232, 150
        cx_, cy_ = pad + (k % 6) * (cw + 8), 32 + (k // 6) * (ch + 20)
        cell = cellbg(cw, ch)
        cd = ImageDraw.Draw(cell)
        ox, oy = cw // 2, ch - 22
        cd.line([(0, oy), (cw, oy)], fill=(90, 80, 100, 255))
        cd.rectangle([ox - 4, oy - 34, ox + 4, oy], fill=(70, 70, 90, 255))
        sm = im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS)
        _paste_clip(cell, sm, ox + off[0] // 2, oy + off[1] // 2)
        S.alpha_composite(cell, (cx_, cy_))
        d.text((cx_ + 3, cy_ + ch + 3), f"{k:02d}  {im.width}x{im.height}  off {off[0]},{off[1]}  r={HAKI_FR[k]['r']}",
               font=font(11), fill=(230, 230, 230, 255))
    secs.append(S)
    A = Image.new("RGBA", (Wsheet, 2 * 290 + 40), bgc)
    d = ImageDraw.Draw(A)
    d.text((pad, 6), "aura (J sword aura loop)  3x on dark and on sky, 6 frames, offset -45,-45", font=font(18),
           fill=(255, 210, 220, 255))
    for row, bright in enumerate((False, True)):
        for k, (im, off) in enumerate(aura):
            cell = cellbg(270, 270, bright)
            cd = ImageDraw.Draw(cell)
            cd.line([(40, 230), (230, 40)], fill=(200, 200, 210, 255), width=4)  # stand-in blade
            cell.alpha_composite(im.resize((270, 270), Image.NEAREST))
            A.alpha_composite(cell, (pad + k * 238 if k < 6 else 0, 34 + row * 290))
    secs.append(A)
    M = Image.new("RGBA", (Wsheet, 450), bgc)
    d = ImageDraw.Draw(M)
    d.text((pad, 6), "in-game mocks at 1x (stand-in feet at screen 175,375): haki_ring 03 and 07", font=font(18),
           fill=(255, 210, 220, 255))
    m1 = mock([(ring[3][0], ring[3][1], "front")], "S+U haki_ring 03")
    m2 = mock([(ring[7][0], ring[7][1], "front")], "S+U haki_ring 07")
    M.alpha_composite(m1, (pad, 36))
    M.alpha_composite(m2, (pad + 616, 36))
    secs.append(M)
    H = sum(s.height for s in secs) + 50
    sheet = Image.new("RGBA", (Wsheet, H), bgc)
    ImageDraw.Draw(sheet).text((pad, 10), "샹크스 패왕색 (Haoshoku) haki_ring + sword aura", font=font(22),
                               fill=(255, 255, 255, 255))
    y = 44
    for s in secs:
        sheet.alpha_composite(s, (0, y))
        y += s.height
    sheet.convert("RGB").save(FX / "preview_haki.png", optimize=True)
    m2.convert("RGB").save(FX / "mock_haki.png", optimize=True)



def render_haki(layout):
    ring = [haki_ring_frame(i, s) for i, s in enumerate(HAKI_FR)]
    aura = [aura_frame(i) for i in range(AURA_N)]
    layout["_doc_haki"] = ("haki_ring (S+U): offsets are frame top-left relative to Shanks's feet; the burst is "
                           "centred on haki_ring_centre and haki_ring_radius gives the ring radius per frame "
                           "(circle hit area; the dome is clipped at the floor, plus a flat ground wave). "
                           "aura (J): 6-frame seamless loop, offsets relative to the pin point on the blade.")
    layout["haki_ring"] = save_seq("haki_ring", ring)
    layout["haki_ring_centre"] = list(HAKI_C)
    layout["haki_ring_radius"] = [s["r"] for s in HAKI_FR]
    layout["aura"] = save_seq("aura", aura)
    layout.setdefault("sizes", {})
    for name in ("haki_ring", "aura"):
        layout["sizes"][name] = [list(Image.open(p).size) for p in sorted((FX / name).glob("*.png"))]
    build_preview_haki(ring, aura)
    print(f"frames: haki_ring {len(ring)}, aura {len(aura)}")



def finalize_soft(arr):
    """Premultiplied float -> RGBA without palette reduction (soft alpha)."""
    a = np.clip(arr[..., 3], 0, 1)
    rgb = np.where(a[..., None] > 1e-4, arr[..., :3] / np.maximum(a[..., None], 1e-4), 0)
    a = np.where(a < 0.02, 0, a)
    out = np.dstack([np.clip(rgb, 0, 1) * 255, a * 255]).round().astype(np.uint8)
    out[a == 0] = 0
    return Image.fromarray(out, "RGBA")


def main():
    import sys
    FX.mkdir(parents=True, exist_ok=True)
    if "--wu" in sys.argv[1:] or "--haki" in sys.argv[1:]:
        layout = json.loads((FX / "layout.json").read_text())
        if "--wu" in sys.argv[1:]:
            render_wu(layout)
        if "--haki" in sys.argv[1:]:
            render_haki(layout)
        (FX / "layout.json").write_text(json.dumps(layout, indent=1, ensure_ascii=False) + "\n")
        return
    eagle = [eagle_frame(i, s) for i, s in enumerate(EAGLE_FRAMES)]
    light = [lightning_frame(i, s) for i, s in enumerate(LIGHT_FRAMES)]
    slash = [slash_frame(i, s) for i, s in enumerate(SLASH_FRAMES)]
    flash = [flash_frame(i) for i in range(4)]
    veil = veil_frame()
    layout = {
        "_doc": ("Offsets are the top-left of each frame in game px. eagle/slash: relative to Shanks's "
                 "origin (feet centre, facing right; mirror x when he faces left). lightning: relative to "
                 "the anchor point the bolt cluster is centred on (see lightning_anchors_*, relative to "
                 "Shanks). flash/veil: relative to the stage top-left (flash_stage / veil_stage)."),
        "eagle": save_seq("eagle", eagle),
        "lightning": save_seq("lightning", light),
        "slash": save_seq("slash", slash),
        "flash": save_seq("flash", [(f, (0, 0)) for f in flash]),
        "flash_stage": True,
        "veil": save_seq("veil", [(veil, (0, 0))]),
        "veil_stage": True,
        "lightning_anchors_eagle": LIGHT_ANCHORS_EAGLE,
        "lightning_anchors_slash": LIGHT_ANCHORS_SLASH,
        "blade_point": list(BLADE),
        "sizes": {},
    }
    for name in ("eagle", "lightning", "slash", "flash", "veil"):
        layout["sizes"][name] = [list(Image.open(p).size) for p in sorted((FX / name).glob("*.png"))]
    build_preview(eagle, light, slash, flash, veil)
    render_wu(layout)
    render_haki(layout)
    (FX / "layout.json").write_text(json.dumps(layout, indent=1, ensure_ascii=False) + "\n")
    total = sum(p.stat().st_size for p in FX.rglob("*.png") if p.parent != FX)
    print(f"frames: eagle {len(eagle)}, lightning {len(light)}, slash {len(slash)}, flash {len(flash)}")
    print(f"total frame PNG bytes: {total / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
