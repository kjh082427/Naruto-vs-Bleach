"""Render Shanks's select / versus-loading / cut-in bitmaps for the BVN game.swf.

usage: tools/venv/bin/python work/shanks/render_ui.py
       (optional) BVN_1676_DIR=<dir with DefineSprite_1676/*.png> skips the FFDec export of the BVN cut-in refs

Inputs  ( Shanks/  -- note the leading space in the folder name)
        샹크스 모델링2.png    348x489 anime full body on a fake checkerboard (255/238)  -> portrait
        샹크스 일러스트2.png  801x1150 anime still, Gryphon over the shoulder, blue sky  -> face1 (sky keyed out)
        샹크스 일러스트4.png  604x915 close-up, scarred left eye  -> icon, banner, face2
                              (burned-in subtitle at y >= 505 and player UI at y <= 105 are never sampled)
Output  work/shanks/ui/
        icon.png      50x48 opaque               BVN select icon sprite 1465 local (0,0)
        portrait.png  <=165 wide, transparent    BVN standing-art sprite 1346 (box x -3..150, y 73..456)
        banner.png    510x85 opaque              BVN versus-loading banner sprite 1983 local (0,0)
        face1.png     transparent cut-out        BVN cut-in sprite 1676 (box x -90..121.5, y -64..70)
        face2.png     224x104 eyes panel         BVN cut-in sprite 1676: crimson Haki irises + glowing scars,
                                                 flare streak, focus lines, black-red Haki lightning, letterbox
        layout.json   {kind: [x, y]} top-left of each bitmap in its sprite's local px
        preview.png   1x / 2x / in-context check sheet (BVN, OP and Mihawk art)

Deterministic: no randomness (hash-based jitter only), only Pillow + numpy.
"""
import glob
import json
import math
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, ' Shanks')
FULL = os.path.join(SRC, '샹크스 모델링2.png')
ANIME = os.path.join(SRC, '샹크스 일러스트2.png')
CLOSE = os.path.join(SRC, '샹크스 일러스트4.png')
OUT = os.path.join(HERE, 'ui')
BVN = os.path.join(ROOT, 'work/op/export/bvn')
OPUI = os.path.join(ROOT, 'work/op/ui')
MIHAWK = os.path.join(ROOT, 'work/mihawk/ui')

# ---------------------------------------------------------------------------------------------------------------
# Close-up (일러스트4): iris centres (source px).  The head is tilted ~8.6 deg; the close-up is rotated about the
# eye midpoint so the eyes are level ("levelled" coordinates below: eyes at (CX -/+ 53.6, EY)).
# ---------------------------------------------------------------------------------------------------------------
CLOSE_EYES = ((279.0, 317.0), (385.0, 333.0))
IRIS_DY, IRIS_R = -3, 11                      # irises sit 3 px above the eye line (upturned look), radius ~11
CLOSE_SAFE = (105, 505)                        # rows outside are player UI / burned-in subtitle: never sampled
CLOSE_SPECKS = [(44, 378, 76, 392), (31, 261, 54, 284), (140, 388, 158, 404)]  # flying white sparks (levelled px)
HAKI_HUE = 352                                 # crimson (deg): blue / purple / magenta hues are pulled towards it

ICON_SIZE = (50, 48)
ICON_W, ICON_EYE = 214, 0.47                   # source width of the icon crop, eye line at 47% of the icon height
ICON_DX = -4                                   # crop centre offset from the eye midpoint (source px)

# Portrait (sprite 1346: box x -3..150, y 73..456, head ~y 75-110, head centre x ~72)
PORTRAIT_W, PORTRAIT_TOP, PORTRAIT_CX = 165, 75, 72
CHECKER = ((255, 255, 255), (238, 238, 238))

# Cut-ins (sprite 1676 union box)
CUTIN_BOX = (-90, -64, 121.5, 70)
FACE1_H = 134
FACE1_SRC = (4, 14, 772, 540)                  # anime still: usable area (frame border at x<4 / y<9), flat bottom
FACE1_HEAD = (450, 300)                        # a point on the figure (keeps the figure's connected component)
FACE1_CLIP = [(742, 440), (801, 440), (801, 1150), (790, 1150)]   # cloud wisps right of the cape edge
FACE1_FADE = 44                                # left frame edge (sleeve / cape run off-frame): soft fade, source px
FACE1_WB = (1.22, 1.03, 0.82)                   # cancel the blue sky cast (warm), then contrast / saturation

FACE2_SIZE, FACE2_SCALE = (224, 104), 0.8
FACE2_REDLIGHT = 0.5                           # red-light grade strength
FACE2_EYE_Y = 0.42
FACE2_FADE = 16
FACE2_GLOW = (255, 34, 40)                     # crimson iris / scar glow
FACE2_HOT = (255, 226, 214)
FACE2_SHADOW = (24, 2, 6)
FACE2_LINE = (214, 34, 44)                     # letterbox edge line
FACE2_FOCUS = 46
FACE2_BAND = (10, 26)                          # eye-band spotlight: full light within 12 px of the eye line
# scar band over the left eye (levelled close-up px): polygon that contains the three scars (and little else)
SCAR_POLY = [(372, 236), (408, 232), (420, 300), (414, 340), (418, 400), (380, 404), (362, 340), (364, 290)]

# Banner (sprite 1983)
BANNER = (510, 85)
BANNER_S, BANNER_EYE, BANNER_FX = 0.5, 39, 168  # face scale, banner y of the eye line, banner x of the eye midpoint
BANNER_FADE = (26, 64)
BANNER_STOPS = [(70, 6, 12), (150, 12, 22), (175, 18, 26), (96, 8, 16), (22, 3, 7)]
BANNER_SLASH = ((282, 104), (500, -18), 2.0, 7.0)  # p0, p1, core half-width, glow radius
HAKI_RED = (235, 22, 34)


# ---------------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------------
def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def to_l(arr):
    return Image.fromarray(np.clip(np.asarray(arr) * 255 + 0.5, 0, 255).astype(np.uint8), 'L')


def f01(im):
    return np.asarray(im, dtype=np.float64) / 255


def from01(rgb, mode='RGB'):
    return Image.fromarray(np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8), mode)


def poly_mask(size, poly, ss=4):
    """Anti-aliased polygon mask (4x supersampled, box-filtered down)."""
    w, h = size
    m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).polygon([(x * ss, y * ss) for x, y in poly], fill=255)
    return m.resize((w, h), Image.BOX)


def hash01(*keys):
    """Deterministic integer hash -> [0, 1)."""
    x = 0x9E3779B9
    for k in keys:
        x = ((x ^ (int(k) & 0xFFFFFFFF)) * 0x85EBCA6B) & 0xFFFFFFFF
        x ^= x >> 13
        x = (x * 0xC2B2AE35) & 0xFFFFFFFF
        x ^= x >> 16
    return x / 4294967296.0


def _dilate(m):
    o = m.copy()
    o[1:] |= m[:-1]
    o[:-1] |= m[1:]
    o[:, 1:] |= m[:, :-1]
    o[:, :-1] |= m[:, 1:]
    return o


def _erode(m):
    return ~_dilate(~m)


def _flood(seed, allowed):
    m = seed & allowed
    while True:
        n = _dilate(m) & allowed
        if (n == m).all():
            return m
        m = n


def big_components(mask, min_size, step=6):
    """Union of the 4-connected components of `mask` with >= min_size px (components found on a coarse grid)."""
    out = np.zeros_like(mask)
    tried = np.zeros_like(mask)
    h, w = mask.shape
    for y in range(0, h, step):
        for x in range(0, w, step):
            if mask[y, x] and not tried[y, x]:
                s = np.zeros_like(mask)
                s[y, x] = True
                comp = _flood(s, mask)
                tried |= comp
                if comp.sum() >= min_size:
                    out |= comp
    return out


def premul_resize(im, size, box=None):
    """Resize RGBA with premultiplied alpha (no dark/colour fringes at the cut edge)."""
    a = np.asarray(im, dtype=np.float32) / 255.0
    pm = np.concatenate([a[..., :3] * a[..., 3:4], a[..., 3:4]], axis=2)
    chans = [Image.fromarray(np.ascontiguousarray(pm[..., i])).resize(size, Image.LANCZOS, box=box) for i in range(4)]
    out = np.clip(np.stack([np.asarray(c, dtype=np.float32) for c in chans], axis=2), 0, 1)
    al = out[..., 3:4]
    rgb = np.where(al > 1e-4, out[..., :3] / np.maximum(al, 1e-4), 0)
    res = np.concatenate([np.clip(rgb, 0, 1), al], axis=2)
    return Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA')


def rgb_to_hsv(rgb):
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    d = mx - mn
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    h = np.where(d < 1e-9, 0, h)
    s = np.where(mx > 1e-9, d / np.maximum(mx, 1e-9), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    h = (h % 360) / 60
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    sel = [np.stack(c, axis=-1) for c in ((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))]
    out = np.zeros(h.shape + (3,))
    for k in range(6):
        out = np.where((i == k)[..., None], sel[k], out)
    return out


def haki_hues(rgb, strength=1.0):
    """Pull blue / purple / magenta hues (190..335 deg) to crimson (the close-up's purple bokeh and blue irises)."""
    h, s, v = rgb_to_hsv(rgb)
    w = smoothstep((h - 185) / 20) * smoothstep((340 - h) / 12) * strength
    h2 = h * (1 - w) + HAKI_HUE * w
    return hsv_to_rgb(h2, s * (1 - 0.15 * w), v * (1 - 0.2 * w))


# ---------------------------------------------------------------------------------------------------------------
# Haki lightning (black bolts with a red rim glow) and slashes
# ---------------------------------------------------------------------------------------------------------------
def bolt_points(p0, p1, seed, rough=0.24, levels=6):
    pts = [np.array(p0, float), np.array(p1, float)]
    for lv in range(levels):
        new = [pts[0]]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            d = b - a
            ln = math.hypot(*d) + 1e-9
            n = np.array([-d[1], d[0]]) / ln
            new += [(a + b) / 2 + n * (hash01(seed, lv, i) - 0.5) * 2 * rough * ln, b]
        pts = new
    return pts


def bolt_set(p0, p1, seed, branches=2):
    """Main bolt + a few short forks: list of (points, width factor)."""
    main = bolt_points(p0, p1, seed)
    out = [(main, 1.0)]
    d = np.array(p1, float) - np.array(p0, float)
    ln = math.hypot(*d)
    for k in range(branches):
        i = int(len(main) * (0.25 + 0.5 * hash01(seed, 90, k)))
        ang = math.atan2(d[1], d[0]) + (1 if k % 2 else -1) * (0.45 + 0.4 * hash01(seed, 91, k))
        bl = ln * (0.22 + 0.2 * hash01(seed, 92, k))
        q = main[i] + bl * np.array([math.cos(ang), math.sin(ang)])
        out.append((bolt_points(main[i], q, seed * 31 + k + 7, levels=5), 0.55))
    return out


def lightning(size, bolts, width=1.6, ss=4):
    """(core, rim, glow) alpha arrays for a list of bolt_set() results."""
    w, h = size
    m = Image.new('L', (w * ss, h * ss), 0)
    dr = ImageDraw.Draw(m)
    for bs in bolts:
        for pts, wf in bs:
            xy = [(float(x) * ss, float(y) * ss) for x, y in pts]
            dr.line(xy, fill=255, width=max(1, round(width * wf * ss)), joint='curve')
    core_im = m.resize((w, h), Image.BOX)
    core = f01(core_im)
    rim = np.clip(f01(core_im.filter(ImageFilter.GaussianBlur(1.0))) * 2.2 - core, 0, 1)
    glow = np.clip(f01(core_im.filter(ImageFilter.GaussianBlur(3.5))) * 2.6, 0, 1)
    return core, rim, glow


def apply_lightning(rgb, core, rim, glow, glow_k=0.55):
    red = np.array(HAKI_RED) / 255
    hot = np.array((255, 120, 110)) / 255
    rgb = rgb * (1 - glow_k * glow[..., None]) + red * glow_k * glow[..., None]
    rgb = rgb * (1 - rim[..., None]) + hot * rim[..., None]
    return rgb * (1 - core[..., None]) + np.array((0.03, 0.0, 0.01)) * core[..., None]


def slash(size, p0, p1, half_w, glow, ss=4):
    """Tapered anti-aliased streak from p0 to p1: (core, glow) alpha arrays."""
    w, h = size
    yy, xx = np.mgrid[0:h * ss, 0:w * ss] / ss
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    length = np.hypot(*d)
    u = d / length
    rx, ry = xx - p0[0], yy - p0[1]
    t = (rx * u[0] + ry * u[1]) / length
    dn = np.abs(-rx * u[1] + ry * u[0])
    taper = np.sin(np.clip(t, 0, 1) * np.pi) ** 0.6 * ((t >= 0) & (t <= 1))
    core = np.clip(1 - dn / (half_w * taper + 1e-3), 0, 1)
    gl = np.exp(-(dn / glow) ** 2) * taper
    down = lambda a: a.reshape(h, ss, w, ss).mean(axis=(1, 3))  # noqa: E731
    return down(core), down(gl)


# ---------------------------------------------------------------------------------------------------------------
# close-up (일러스트4): levelled, safe rows only
# ---------------------------------------------------------------------------------------------------------------
def close_geometry():
    (x1, y1), (x2, y2) = CLOSE_EYES
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    cx, ey = (x1 + x2) / 2, (y1 + y2) / 2
    half = math.hypot(x2 - x1, y2 - y1) / 2
    return angle, cx, ey, half


def levelled_close():
    """Close-up rotated about the eye midpoint so the eyes are level; unsafe rows blacked out first."""
    im = Image.open(CLOSE).convert('RGB')
    a = np.asarray(im).copy()
    a[:CLOSE_SAFE[0]] = 0
    a[CLOSE_SAFE[1]:] = 0
    angle, cx, ey, _ = close_geometry()
    lev = Image.fromarray(a).rotate(angle, resample=Image.BICUBIC, center=(cx, ey))
    for x0, y0, x1, y1 in CLOSE_SPECKS:              # thin bright sparks: local min filter, soft-edged patch
        pad = (x0 - 6, y0 - 6, x1 + 6, y1 + 6)
        patch = lev.crop(pad).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.GaussianBlur(1.5))
        m = Image.new('L', patch.size, 0)
        ImageDraw.Draw(m).rectangle([3, 3, patch.width - 4, patch.height - 4], fill=255)
        lev.paste(patch, pad[:2], m.filter(ImageFilter.GaussianBlur(2)))
    return lev


def iris_mask(lev):
    """Soft mask of the (dark navy) irises in the levelled close-up."""
    _, cx, ey, half = close_geometry()
    rgb = f01(lev)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    blue = smoothstep((b - np.maximum(r, g) - 0.08) / 0.1) * (b > 0.12)
    ys, xs = np.mgrid[0:rgb.shape[0], 0:rgb.shape[1]]
    near = np.zeros_like(blue)
    for x in (cx - half, cx + half):
        near = np.maximum(near, smoothstep((IRIS_R - np.hypot(xs - x, ys - ey - IRIS_DY)) / 3))
    return blue * near


def scar_mask(lev):
    """Soft mask of the three scars over the left eye: red strokes darker than their surroundings inside
    SCAR_POLY, minus the eyelid outline."""
    _, cx, ey, half = close_geometry()
    rgb = f01(lev)
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    loc = f01(to_l(lum).filter(ImageFilter.GaussianBlur(5)))
    r, b = rgb[..., 0], rgb[..., 2]
    scar = smoothstep((loc - lum - 0.04) / 0.08) * ((r - b) > 0.08) * (r > 0.2)
    ys, xs = np.mgrid[0:rgb.shape[0], 0:rgb.shape[1]]
    lid = smoothstep(1.3 - np.hypot((xs - cx - half) / 21, (ys - ey - 1) / 9))
    return scar * f01(poly_mask(lev.size, SCAR_POLY)) * (1 - lid)


def graded_close(lev, iris_k=0.85):
    """Haki grade of the levelled close-up: blue / purple -> crimson, irises crimson."""
    rgb = f01(lev)
    rgb = haki_hues(rgb)
    ir = iris_mask(lev)[..., None]
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    crimson = np.stack([0.25 + lum * 1.2, lum * 0.25, lum * 0.3], axis=-1)
    return np.clip(rgb * (1 - iris_k * ir) + crimson * iris_k * ir, 0, 1)


def make_icon(lev):
    _, cx, ey, _ = close_geometry()
    w = ICON_W
    h = w * ICON_SIZE[1] / ICON_SIZE[0]
    top = ey - ICON_EYE * h
    assert CLOSE_SAFE[0] < top and top + h < CLOSE_SAFE[1]
    src = from01(graded_close(lev))
    im = src.resize(ICON_SIZE, Image.LANCZOS, box=(cx + ICON_DX - w / 2, top, cx + ICON_DX + w / 2, top + h))
    im = ImageEnhance.Brightness(im).enhance(1.08)   # the close-up is dim next to the BVN icons
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Sharpness(im).enhance(1.3)
    return im.convert('RGBA')


# ---------------------------------------------------------------------------------------------------------------
# face2: the "dun-dun" eyes panel
# ---------------------------------------------------------------------------------------------------------------
def make_face2(lev):
    w, h = FACE2_SIZE
    _, cx, ey, half = close_geometry()
    k = FACE2_SCALE
    sw, sh = w / k, h / k
    box = (cx - sw / 2, ey - FACE2_EYE_Y * sh, cx + sw / 2, ey + (1 - FACE2_EYE_Y) * sh)
    assert CLOSE_SAFE[0] < box[1] and box[3] < CLOSE_SAFE[1]
    rgb = f01(lev.resize((w, h), Image.LANCZOS, box=box).filter(ImageFilter.UnsharpMask(1.2, 60, 2)))
    rgb = haki_hues(rgb)
    iris = f01(to_l(iris_mask(lev)).resize((w, h), Image.BOX, box=box))
    scar = f01(to_l(scar_mask(lev)).resize((w, h), Image.BOX, box=box))
    x1, x2, py = (cx - half - box[0]) * k, (cx + half - box[0]) * k, (ey + IRIS_DY - box[1]) * k
    mx = (x1 + x2) / 2
    ys, xs = np.mgrid[0:h, 0:w] + 0.5

    # grade: hard contrast, slightly desaturated skin, crimson-black shadows
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    rgb = rgb * 0.78 + lum[..., None] * 0.22
    rgb = np.clip((rgb - 0.06) / 0.86, 0, 1) ** 1.2
    shadow = np.array(FACE2_SHADOW) / 255
    t = smoothstep((0.42 - lum) / 0.36)[..., None]
    rgb = rgb * (1 - 0.55 * t) + shadow * 0.55 * t
    # red Haki light over the whole face (as in the "eye" reference): skin to red-orange, lines stay dark
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    lit = np.stack([np.clip(lum * 1.25 + 0.04, 0, 1), lum * 0.62, lum * 0.55], axis=-1)
    eyes = np.zeros((h, w))
    for x in (x1, x2):                                   # the eyes themselves keep their whites
        eyes = np.maximum(eyes, smoothstep(1.4 - np.hypot((xs - x) / (19 * k), (ys - py - 3 * k) / (8 * k))))
    red_k = (FACE2_REDLIGHT * (1 - 0.85 * eyes))[..., None]
    rgb = rgb * (1 - red_k) + lit * red_k

    # crimson irises + glowing scars, then bloom
    glow_c = np.array(FACE2_GLOW) / 255
    ir = iris[..., None]
    rgb = rgb * (1 - 0.8 * ir) + np.clip(glow_c * 0.75 + rgb * 0.5, 0, 1) * 0.8 * ir
    sc = (scar ** 1.5)[..., None]
    rgb = rgb * (1 - 0.3 * sc) + np.array((0.86, 0.06, 0.10)) * 0.3 * sc
    emit = Image.fromarray((np.clip(iris + 0.22 * scar, 0, 1) * 255).astype(np.uint8), 'L')
    b1 = f01(emit.filter(ImageFilter.GaussianBlur(2.2)))
    b2 = f01(emit.filter(ImageFilter.GaussianBlur(7)))
    glow = np.clip(1.6 * b1 + 2.2 * b2, 0, 1)[..., None]
    rgb = 1 - (1 - rgb) * (1 - glow * glow_c * 0.9)                     # screen
    # eye whites: lifted to a hot pinkish white so both eyes read at 1x
    wl = (rgb @ np.array([0.299, 0.587, 0.114]))[..., None]
    white = (eyes[..., None] * smoothstep((wl - 0.45) / 0.25) * (1 - ir))
    rgb = rgb * (1 - 0.6 * white) + np.array((1.0, 0.93, 0.92)) * 0.6 * white

    # eye-band spotlight (forehead / hair / cheeks sink into crimson-black) + dark vignette
    band = smoothstep((np.abs(ys - py) - FACE2_BAND[0]) / FACE2_BAND[1])[..., None]
    rgb = rgb * (1 - 0.7 * band) + shadow * 0.7 * band
    rho = np.hypot((xs - mx) / (w * 0.56), (ys - py) / (h * 0.62))
    v = smoothstep((rho - 0.55) / 0.5)[..., None]
    rgb = rgb * (1 - 0.88 * v) + shadow * 0.88 * v

    # focus lines: thin pale wedges from the border towards the eyes (outside the eye band)
    ss = 4
    yy, xx = (np.mgrid[0:h * ss, 0:w * ss] + 0.5) / ss
    ang = np.arctan2((yy - py) * 2.1, xx - mx)
    rr = np.hypot((xx - mx) / (w * 0.5), (yy - py) / (h * 0.5))
    lines = np.zeros_like(xx)
    for i in range(FACE2_FOCUS):
        a0 = (i + 0.7 * hash01(i, 11)) / FACE2_FOCUS * 2 * np.pi - np.pi
        width = 0.006 + 0.010 * hash01(i, 12)
        r0 = 0.64 + 0.30 * hash01(i, 13)
        da = np.abs((ang - a0 + np.pi) % (2 * np.pi) - np.pi)
        lines = np.maximum(lines, np.clip(1 - da / (width * np.clip(rr - r0, 0, None) / 0.4 + 1e-6), 0, 1)
                           * (rr > r0) * (0.22 + 0.3 * hash01(i, 14)))
    lines = lines.reshape(h, ss, w, ss).mean(axis=(1, 3))[..., None]
    rgb = rgb * (1 - lines) + np.array([1.0, 0.82, 0.80]) * lines

    # black Haki lightning crackling in from both ends (kept off the eyes)
    bolts = [bolt_set((-4, 14), (42, 34), 3), bolt_set((-2, 96), (40, 68), 5, branches=1),
             bolt_set((w + 4, 8), (w - 46, 32), 7), bolt_set((w + 2, 98), (w - 40, 70), 9, branches=1)]
    core, rim, gl = lightning((w, h), bolts, width=1.4)
    rgb = apply_lightning(rgb, core, rim * 0.7, gl, glow_k=0.45)

    # lens flare: horizontal streak through both irises + 4-point stars on them
    dy = ys - py
    peak = np.maximum(np.exp(-np.abs(xs - x1) / 30), np.exp(-np.abs(xs - x2) / 30))
    along = 0.15 + 0.85 * peak
    streak = along * (np.exp(-(dy / 0.7) ** 2) + 0.45 * np.exp(-(dy / 2.6) ** 2))
    star = np.zeros_like(xs)
    for x in (x1, x2):
        ddx, ddy = xs - x, ys - py
        star += np.exp(-(ddx / 0.8) ** 2) * np.exp(-np.abs(ddy) / 5.5)
        star += 0.9 * np.exp(-(ddx ** 2 + ddy ** 2) / 6.0)
        for sgn in (1, -1):
            dd = (ddx + sgn * ddy) / np.sqrt(2)
            dn = (ddx - sgn * ddy) / np.sqrt(2)
            star += 0.35 * np.exp(-(dn / 0.7) ** 2) * np.exp(-np.abs(dd) / 2.2)
    flare = np.clip(streak + star, 0, 1.6)[..., None]
    hot = np.array(FACE2_HOT) / 255
    rgb = 1 - (1 - rgb) * (1 - np.clip(flare * (glow_c * 0.55 + hot * 0.45), 0, 1))

    # crisp letterbox edges, soft left / right ends
    rgb[0], rgb[h - 1] = np.array(FACE2_LINE) / 255, np.array(FACE2_LINE) / 255
    rgb[1], rgb[h - 2] = shadow, shadow
    ax = smoothstep(xs[0] / FACE2_FADE) * smoothstep((w - xs[0]) / FACE2_FADE)
    out = from01(rgb).convert('RGBA')
    out.putalpha(to_l(np.repeat(ax[None], h, axis=0)))
    return out


# ---------------------------------------------------------------------------------------------------------------
# banner
# ---------------------------------------------------------------------------------------------------------------
def gradient(w, h, stops):
    t = np.linspace(0, 1, w) * (len(stops) - 1)
    i = np.minimum(t.astype(int), len(stops) - 2)
    f = (t - i)[:, None]
    a = np.array(stops, dtype=np.float64)
    return np.repeat((a[i] * (1 - f) + a[i + 1] * f)[None], h, axis=0) / 255


def make_banner(lev):
    w, h = BANNER
    ys, xs = np.mgrid[0:h, 0:w] + 0.5
    # crimson field: horizontal gradient, soft energy bands, vignette top / bottom
    bg = gradient(w, h, BANNER_STOPS)
    band = 0.5 + 0.5 * np.sin((xs * 0.9 - ys * 2.2) / 23.0) * np.sin((xs * 0.35 + ys) / 41.0)
    bg *= (0.78 + 0.32 * band)[..., None]
    bg *= (1 - 0.5 * np.abs(np.linspace(-1, 1, h)) ** 2)[:, None, None]
    # Haki burst behind the slash
    burst = np.exp(-(((xs - 390) / 120) ** 2 + ((ys - 40) / 52) ** 2))[..., None]
    bg = 1 - (1 - bg) * (1 - 0.35 * burst * np.array(HAKI_RED) / 255)
    # black lightning radiating from the burst
    bolts = [bolt_set((388, 44), (510, 6), 21), bolt_set((392, 46), (512, 80), 23),
             bolt_set((380, 40), (318, -4), 25), bolt_set((384, 50), (300, 90), 27),
             bolt_set((396, 42), (468, -6), 29, branches=1), bolt_set((394, 48), (450, 92), 31, branches=1)]
    core, rim, gl = lightning((w, h), bolts, width=1.7)
    bg = apply_lightning(bg, core, rim, gl, glow_k=0.6)
    # Divine-Departure slash: white-hot core, crimson glow
    p0, p1, hw, gr = BANNER_SLASH
    c, g = slash((w, h), p0, p1, hw, gr)
    red = np.array(HAKI_RED) / 255
    bg = bg * (1 - 0.75 * g[..., None]) + red * 0.75 * g[..., None]
    bg = bg * (1 - c[..., None]) + np.array((1.0, 0.95, 0.92)) * c[..., None]
    out = from01(bg)
    # face band (levelled close-up, Haki grade) with soft left / right edges
    _, cx, ey, _ = close_geometry()
    s = BANNER_S
    y0 = ey - BANNER_EYE / s
    assert CLOSE_SAFE[0] < y0 and y0 + h / s < CLOSE_SAFE[1]
    face = from01(graded_close(lev)).resize((round(lev.width * s), h), Image.LANCZOS,
                                            box=(0, y0, lev.width, y0 + h / s))
    face = ImageEnhance.Contrast(face).enhance(1.1)
    fw = face.width
    fxs = np.arange(fw) + 0.5
    a = smoothstep(fxs / BANNER_FADE[0]) * smoothstep((fw - fxs) / BANNER_FADE[1])
    out.paste(face, (round(BANNER_FX - cx * s), 0), to_l(np.repeat(a[None], h, axis=0)))
    return out.convert('RGBA')


# ---------------------------------------------------------------------------------------------------------------
# portrait (모델링2, fake checkerboard keyed out)
# ---------------------------------------------------------------------------------------------------------------
def checker_alpha(rgb):
    """Figure mask of the fake-transparency source: checker reachable from the border plus enclosed checker
    pockets (inside the sword guard, between cape and legs) are background; light anti-alias fringe peeled off."""
    a = np.asarray(rgb).astype(int)
    c0 = (a == CHECKER[0]).all(2)
    c1 = (a == CHECKER[1]).all(2)
    bgc = c0 | c1
    seed = np.zeros_like(bgc)
    seed[0], seed[-1], seed[:, 0], seed[:, -1] = bgc[0], bgc[-1], bgc[:, 0], bgc[:, -1]
    bg = _flood(seed, bgc)
    # enclosed pockets: components that contain the grey checker colour (the art itself never uses 238)
    pending = c1 & ~bg
    while pending.any():
        ys, xs = np.nonzero(pending)
        s = np.zeros_like(bgc)
        s[ys[0], xs[0]] = True
        comp = _flood(s, bgc)
        if comp.sum() >= 20:
            bg |= comp
        pending &= ~comp
    # peel the light fringe (the source was cut out on white): light pixels touching the background, twice
    lum = a @ np.array([0.299, 0.587, 0.114])
    for _ in range(2):
        edge = ~bg & _dilate(bg)
        bg |= edge & (lum > 150)
    # keep only the figure (drop detached specks)
    fg = ~bg
    h, w = fg.shape
    s = np.zeros_like(fg)
    s[h // 2, w // 2] = True
    return _flood(s, fg)


def make_portrait():
    rgb = Image.open(FULL).convert('RGB')
    fg = checker_alpha(rgb)
    im = rgb.convert('RGBA')
    im.putalpha(Image.fromarray(fg.astype(np.uint8) * 255, 'L'))
    ys, xs = np.nonzero(fg)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    # head centre = centroid of the red hair (top 90 rows)
    a = np.asarray(rgb).astype(int)
    hair = (a[..., 0] > 120) & (a[..., 1] < 40) & (a[..., 2] < 40) & fg
    hair[90:] = False
    head_x = float(np.nonzero(hair)[1].mean())
    scale = PORTRAIT_W / (box[2] - box[0])
    size = (round((box[2] - box[0]) * scale), round((box[3] - box[1]) * scale))
    out = premul_resize(im, size, box=box)
    out = ImageEnhance.Color(out).enhance(1.08)
    return out, [round(PORTRAIT_CX - (head_x - box[0]) * scale, 2), PORTRAIT_TOP]


# ---------------------------------------------------------------------------------------------------------------
# face1 (일러스트2, blue sky keyed out)
# ---------------------------------------------------------------------------------------------------------------
def face1_mask(rgb_im):
    a = np.asarray(rgb_im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    sky = (b >= 170) & (b - r >= 40) & (b - g >= 20)
    bg = big_components(sky, 150, step=3)       # pockets >= 150 px (guard gap 247, blade gap 537); iris < 30
    x0, y0, x1, y1 = FACE1_SRC
    fg = ~bg
    fg[:y0], fg[y1:], fg[:, :x0], fg[:, x1:] = False, False, False, False
    fg &= ~(f01(poly_mask(rgb_im.size, FACE1_CLIP, ss=1)) > 0.5)
    s = np.zeros_like(fg)
    s[FACE1_HEAD[1], FACE1_HEAD[0]] = True
    fg = _flood(s, fg)
    # drop the 1 px sky-blended rim outside the ink outline (the cut sits on the line art)
    edge = fg & _dilate(bg & ~fg)
    fg &= ~(edge & (b - r > 12) & (b > 110))
    # fill pin-holes only (e.g. specks inside the shirt); the sky pockets (guard loop, arm / head gap) stay open
    holes = ~fg & ~_flood(_border_seed(fg), ~fg)
    return fg | (holes & ~bg), bg


def _border_seed(fg):
    s = np.zeros_like(fg)
    s[0], s[-1], s[:, 0], s[:, -1] = True, True, True, True
    return s


def make_face1():
    im = Image.open(ANIME).convert('RGB')
    fg, sky = face1_mask(im)
    rgb = f01(im)
    # sky spill near the cut edge (hair / shoulder rims): clamp blue towards the other channels
    near = sky.copy()
    for _ in range(4):
        near = _dilate(near)
    rim = (fg & near)[..., None]
    spill = np.minimum(rgb[..., 2], (rgb[..., 0] + rgb[..., 1]) / 2 + 0.06)
    rgb = np.where(rim, np.concatenate([rgb[..., :2], spill[..., None]], axis=2), rgb)
    rgb = rgb * np.array(FACE1_WB)
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    rgb = np.clip(rgb * 1.08 + (rgb - lum[..., None]) * 0.12, 0, 1)
    x0, y0, x1, y1 = FACE1_SRC
    xs = np.arange(im.width) + 0.5
    fade = smoothstep((xs - x0) / FACE1_FADE)[None, :]
    alpha = fg * fade
    rgba = from01(np.concatenate([rgb, alpha[..., None]], axis=2), 'RGBA')
    ys, xs_ = np.nonzero(fg)
    box = (x0, int(ys.min()), int(xs_.max()) + 1, y1)
    scale = FACE1_H / (box[3] - box[1])
    size = (round((box[2] - box[0]) * scale), FACE1_H)
    out = premul_resize(rgba, size, box=box)
    out = ImageEnhance.Brightness(out).enhance(1.06)
    out = ImageEnhance.Color(out).enhance(1.1)
    return ImageEnhance.Contrast(out).enhance(1.06)


# ---------------------------------------------------------------------------------------------------------------
# preview
# ---------------------------------------------------------------------------------------------------------------
FONT = os.path.join(ROOT, 'tools/fonts/NanumGothic-Bold.ttf')
GAME_SWF = os.path.join(ROOT, 'game/game.swf')
FFDEC = os.path.join(ROOT, 'tools/ffdec/ffdec.jar')
PORTRAIT_ORIGIN = (-122.4, 16.35)   # FFDec canvas origin of sprite 1346 (union bounds)
BVN_PORTRAITS = (26, 0, 13)          # Kakashi, Ichigo, Itachi
BVN_CUTINS = (40, 55)                # frames of sprite 1676 shown as reference (if FFDec is available)


def frames(sprite_dir):
    fs = glob.glob(os.path.join(sprite_dir, '*.png'))
    return sorted(fs, key=lambda f: int(os.path.basename(f)[:-4]))


def bvn_cutins():
    """A few BVN cut-in frames for reference (cached dir via BVN_1676_DIR, else a one-off FFDec export)."""
    for pre in (os.environ.get('BVN_1676_DIR', ''), os.path.join(BVN, 'DefineSprite_1676')):
        d = os.path.join(pre, 'DefineSprite_1676') if pre and os.path.isdir(os.path.join(pre, 'DefineSprite_1676')) \
            else pre
        if d and os.path.isdir(d) and frames(d):
            fs = frames(d)
            return [Image.open(fs[i]).convert('RGBA') for i in BVN_CUTINS if i < len(fs)]
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(['java', '-jar', FFDEC, '-selectid', '1676', '-format', 'sprite:png', '-export', 'sprite',
                            tmp, GAME_SWF], capture_output=True, check=True, timeout=600)
        except (OSError, subprocess.SubprocessError):
            return []
        fs = frames(os.path.join(tmp, 'DefineSprite_1676'))
        return [Image.open(fs[i]).convert('RGBA').copy() for i in BVN_CUTINS if i < len(fs)]


def checker(size, a=(58, 58, 66), b=(46, 46, 54), n=8):
    im = Image.new('RGB', size, a)
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], n):
        for x in range((y // n % 2) * n, size[0], 2 * n):
            d.rectangle([x, y, x + n - 1, y + n - 1], fill=b)
    return im


def scaled(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def load_mihawk():
    try:
        lay = json.load(open(os.path.join(MIHAWK, 'layout.json'), encoding='utf-8'))
        ims = {k: Image.open(os.path.join(MIHAWK, f'{k}.png')).convert('RGBA') for k in lay}
        return ims, lay
    except OSError:
        return None, None


def make_preview(out, layout):
    font, small = ImageFont.truetype(FONT, 14), ImageFont.truetype(FONT, 11)
    W = 1240
    sheet = Image.new('RGB', (W, 4200), (22, 22, 28))
    d = ImageDraw.Draw(sheet)
    y = 8
    mh, mh_lay = load_mihawk()

    def title(text):
        nonlocal y
        d.text((10, y), text, font=font, fill=(240, 220, 120))
        y += 22

    def put(im, x, yy, bg=True, label=None):
        if bg:
            sheet.paste(checker(im.size), (x, yy))
        sheet.paste(im, (x, yy), im if im.mode == 'RGBA' else None)
        if label:
            d.text((x, yy + im.height + 2), label, font=small, fill=(190, 190, 200))
        return max(im.width, round(d.textlength(label, font=small)) if label else 0)

    # 1x and 2x of every output
    for k in (1, 2):
        title(f'{k}x  (checker = transparent)')
        x, rowh = 10, 0
        for n in ('icon', 'portrait', 'face1', 'face2'):
            im = scaled(out[n], k)
            x += put(im, x, y, label=f'{n}.png {out[n].width}x{out[n].height}') + 16
            rowh = max(rowh, im.height)
        if k == 1:
            put(out['banner'], x, y, bg=False, label='banner.png 510x85')
        y += rowh + 24
    put(scaled(out['banner'], 2), 10, y, bg=False)
    y += 170 + 12

    # icon in a row of BVN / OP / Mihawk icons
    title('icon (6th) in a row of BVN / Mihawk / OP select icons: 3x and 1x')
    bvn_icons = frames(os.path.join(BVN, 'DefineSprite_1465'))
    row = [Image.open(bvn_icons[i]).convert('RGBA') for i in (5, 12, 26, 37)]
    if mh:
        row.append(mh['icon'])
    row += [out['icon']] + [Image.open(os.path.join(OPUI, 'icon', f'{n}.png')).convert('RGBA')
                            for n in ('佐罗', '罗')]
    for i, im in enumerate(row):
        sheet.paste(scaled(im, 3), (10 + i * 154, y))
        sheet.paste(im, (10 + i * 54, y + 152))
    y += 152 + 48 + 14

    # banners as on the versus-loading screen
    title('banner stacked with BVN / Mihawk / OP banners (1x)')
    bvn_banners = frames(os.path.join(BVN, 'DefineSprite_1983'))
    stack = [Image.open(bvn_banners[3]), out['banner'], Image.open(bvn_banners[9]),
             Image.open(os.path.join(OPUI, 'banner', '罗.png'))]
    sheet.paste(Image.new('RGB', (530, 4 * 91 + 6), (14, 14, 26)), (10, y))
    for i, im in enumerate(stack):
        sheet.paste(im.convert('RGB'), (20, y + 6 + i * 91))
    right = [out['banner']] + ([mh['banner']] if mh else []) + [Image.open(bvn_banners[20])]
    sheet.paste(Image.new('RGB', (530, len(right) * 91 + 6), (14, 14, 26)), (570, y))
    for i, im in enumerate(right):
        sheet.paste(im.convert('RGB'), (580, y + 6 + i * 91))
    y += 4 * 91 + 6 + 16

    # portraits in sprite-1346 local coordinates
    title('portrait next to BVN / OP / Mihawk standing art in sprite-1346 local px (panel = x -12..189, y 60..330, '
          'line = y 73); last = mirrored (P1)')
    lx0, ly0, lx1, ly1 = -12, 60, 189, 330
    pw, ph = lx1 - lx0, ly1 - ly0
    bvn_ports = frames(os.path.join(BVN, 'DefineSprite_1346'))
    opl = json.load(open(os.path.join(OPUI, 'layout.json'), encoding='utf-8'))['portrait']
    panels = [(Image.open(bvn_ports[i]).convert('RGBA'), PORTRAIT_ORIGIN, False) for i in BVN_PORTRAITS]
    panels.append((Image.open(os.path.join(OPUI, 'portrait', '佐罗.png')).convert('RGBA'), tuple(opl['佐罗']), False))
    if mh:
        panels.append((mh['portrait'], tuple(mh_lay['portrait']), False))
    panels.append((out['portrait'], tuple(layout['portrait']), False))
    panels.append((out['portrait'], tuple(layout['portrait']), True))
    pw2 = min(pw, (W - 10) // len(panels) - 4)
    for i, (im, (px, py), mirror) in enumerate(panels):
        p = Image.new('RGBA', (pw, ph), (30, 34, 52, 255))
        layer = Image.new('RGBA', (pw + 800, ph + 800), (0, 0, 0, 0))
        layer.paste(im, (round(px - lx0) + 400, round(py - ly0) + 400))
        layer = layer.crop((400, 400, 400 + pw, 400 + ph))
        if mirror:
            layer = layer.transpose(Image.FLIP_LEFT_RIGHT)
        p.alpha_composite(layer)
        dd = ImageDraw.Draw(p)
        dd.line([(-3 - lx0, 73 - ly0), (150 - lx0, 73 - ly0)], fill=(90, 90, 120, 255))
        dd.line([(72 - lx0 if not mirror else pw - 1 - (72 - lx0), 64 - ly0),
                 (72 - lx0 if not mirror else pw - 1 - (72 - lx0), 70 - ly0)], fill=(200, 200, 90, 255))
        sheet.paste(p.convert('RGB').crop((0, 0, pw2, ph)), (10 + i * (pw2 + 4), y))
    y += ph + 16

    # cut-ins in the sprite-1676 box
    title('cut-ins in the sprite-1676 box (-90..121.5, -64..70): BVN refs, Mihawk face1/face2, '
          'Shanks face1, face2, face1 mirrored (P2); 1x / 2x')
    bx0, by0, bx1, by1 = CUTIN_BOX
    bw, bh = round(bx1 - bx0), round(by1 - by0)
    f1, f2 = out['face1'], out['face2']
    items = [(im, (bx0, by0)) for im in bvn_cutins()]
    if mh:
        items += [(mh['face1'], tuple(mh_lay['face1'])), (mh['face2'], tuple(mh_lay['face2']))]
    items += [(f1, tuple(layout['face1'])), (f2, tuple(layout['face2'])),
              (f1.transpose(Image.FLIP_LEFT_RIGHT), (bx0 + bx1 - layout['face1'][0] - f1.width, layout['face1'][1]))]
    for k in (1, 2):
        x = 10
        for im, (px, py) in items:
            p = Image.new('RGBA', (bw + 2, bh + 2), (40, 24, 30, 255))
            p.alpha_composite(im, (round(px - bx0) + 1, round(py - by0) + 1))
            ImageDraw.Draw(p).rectangle([0, 0, bw + 1, bh + 1], outline=(120, 120, 140, 255))
            p = scaled(p, k)
            if x + p.width > W:
                x, y = 10, y + p.height + 8
            sheet.paste(p.convert('RGB'), (x, y))
            x += p.width + 8
        y += (bh + 2) * k + 10
    return sheet.crop((0, 0, W, y + 4))


def main():
    os.makedirs(OUT, exist_ok=True)
    lev = levelled_close()
    portrait, p_pos = make_portrait()
    face1 = make_face1()
    out = {
        'icon': make_icon(lev),
        'portrait': portrait,
        'banner': make_banner(lev),
        'face1': face1,
        'face2': make_face2(lev),
    }
    assert out['icon'].size == ICON_SIZE and out['banner'].size == BANNER
    assert portrait.width <= 165 and portrait.height <= 300
    cx, cy = (CUTIN_BOX[0] + CUTIN_BOX[2]) / 2, (CUTIN_BOX[1] + CUTIN_BOX[3]) / 2
    f2 = out['face2']
    layout = {
        'icon': [0, 0],
        'portrait': p_pos,
        'banner': [0, 0],
        'face1': [round(cx - face1.width / 2, 2), round(CUTIN_BOX[3] - face1.height, 2)],
        'face2': [round(cx - f2.width / 2, 2), round(cy - f2.height / 2, 2)],
    }
    for k, im in out.items():
        im.save(os.path.join(OUT, f'{k}.png'), optimize=True)
    with open(os.path.join(OUT, 'layout.json'), 'w', encoding='utf-8') as f:
        json.dump(layout, f)
        f.write('\n')
    make_preview(out, layout).save(os.path.join(OUT, 'preview.png'), optimize=True)
    for k in layout:
        print(f'{k}.png', out[k].size, out[k].mode, layout[k])


if __name__ == '__main__':
    main()
