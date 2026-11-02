"""Render Dracule Mihawk's select / versus-loading / cut-in bitmaps for the BVN game.swf.

usage: tools/venv/bin/python work/mihawk/render_ui.py

Inputs  (Dracule Mihawk/)
        미호크 일러스트.png   699x546 card art  -> hand-traced cut-out (portrait, face1)
        미호크 일러스트2.png  1465x829 anime face close-up -> icon, banner, face2 (eyes panel)
Output  work/mihawk/ui/
        icon.png      50x48 opaque               BVN select icon sprite 1465 local (0,0)
        portrait.png  <=165 wide, transparent    BVN standing-art sprite 1346 (box x -3..150, y 73..456)
        banner.png    510x85 opaque              BVN versus-loading banner sprite 1983 local (0,0)
        face1.png     transparent cut-out        BVN cut-in sprite 1676 (box x -90..121.5, y -64..70)
        face2.png     224x104 S+I eyes panel     BVN cut-in sprite 1676: golden glowing irises, lens-flare streak,
                                                 focus lines, dark vignette, gold letterbox edges, soft ends
        layout.json   {kind: [x, y]} top-left of each bitmap in its sprite's local px
        preview.png   1x / 2x / in-context check sheet

Deterministic: no randomness, only Pillow + numpy.
"""
import glob
import json
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, 'Dracule Mihawk')
CARD = os.path.join(SRC, '미호크 일러스트.png')
CLOSE = os.path.join(SRC, '미호크 일러스트2.png')
OUT = os.path.join(HERE, 'ui')
BVN = os.path.join(ROOT, 'work/op/export/bvn')
OPUI = os.path.join(ROOT, 'work/op/ui')

# ---------------------------------------------------------------------------------------------------------------
# Hand-traced silhouette of Mihawk in the card art (source px, clockwise from the left hat-brim tip).
# Traced on the outer edge of the purple rim light (kept as the cut-out's outline); background cloud between the
# coat and Yoru's grip is excluded.  Bottom is a flat cut at y=320 (below that the art is covered by slash FX).
# ---------------------------------------------------------------------------------------------------------------
CARD_POLY = [
    # brim, upper-left edge
    (134.8, 117), (135.8, 112.5), (140.2, 108.2), (147.2, 100.3), (157, 94), (171.3, 88), (185, 84.4), (200, 81.8),
    (207, 79.8),
    # crown, left side up and over the two lobes
    (207, 72), (207, 65), (208, 58), (209, 51), (212, 44), (216, 38), (222, 32), (228, 31), (234, 30.5),
    (238, 27), (245, 24), (252, 22), (259, 21.8), (266, 23.4), (274, 27.8), (281, 35), (286.5, 42), (290.5, 48.5),
    # plume on the hat band
    (293.5, 48), (295.5, 43.5), (297.5, 39.3), (300.2, 34.8), (302.8, 31.6), (308, 30.3), (314, 30), (320, 30),
    (327, 31.2), (331.5, 35.6), (337, 38.6), (344, 41.2), (348, 44.2), (350.3, 48), (351.5, 51),
    # brim, right part
    (360, 49), (372, 48), (380, 50), (385, 55), (386.5, 62),
    (384, 70), (380, 80), (374, 90), (366, 98), (356, 106), (350, 108.5), (344, 112), (340, 115), (332, 120),
    (325, 124), (320, 127), (316, 130),
    # neck / coat collar, then the right lapel
    (311, 135), (309, 141), (310, 147), (313, 152.5),
    (320, 154), (340, 155), (360, 155), (380, 155.5), (400, 156), (415, 156.5),
    (408, 168), (400, 180), (393, 192), (388, 203), (386, 213), (385, 218),
    # coat over his left upper arm (rim light)
    (395, 223), (403, 230), (410, 238), (415, 247), (418, 257), (420, 267), (422, 276),
    # gold sleeve top -> left hand -> Yoru's grip, pommel
    (436, 276.5), (450, 275.5), (463, 270), (478, 264),
    (475, 250), (468, 225), (462, 200), (453, 175), (443, 150), (436, 128), (430, 112), (427, 103),
    (420, 96), (410, 90), (404, 80), (403, 70), (405, 58), (410, 45), (420, 36), (432, 33), (445, 35), (458, 44),
    (468, 57), (471, 70), (468, 82), (462, 92), (460, 99),
    (465, 110), (469, 129), (474, 150), (477, 170), (481, 190), (484, 205), (489, 225), (494, 240), (498, 250),
    (500, 256),
    # right hand around the grip
    (506, 258), (512, 262), (520, 270), (525, 280), (528, 292), (530, 304), (530, 316), (529, 320),
    # flat bottom (small notch between sleeve cuff and hand)
    (456, 320), (452, 317), (446, 317), (440, 320), (208, 320),
    # left: gold sleeve rim up to the shoulder
    (200, 312), (193, 305), (185, 297), (175, 288), (166.5, 277), (163, 260), (161.5, 240),
    (164, 236), (169, 228), (179, 216), (191, 208), (198, 205), (202, 201), (205, 197),
    # coat collar (lower edge to tip, upper edge)
    (198, 191), (193, 185), (198, 180), (206, 171), (213, 163), (216.5, 159), (217, 153.5),
    # brim, lower edge back to the tip
    (206.6, 153.6), (192, 153), (178, 150.5), (164, 146.6), (151, 142.2), (142, 138), (136.5, 132), (134.2, 124),
]
CARD_BOTTOM = 320


# Icon: anime close-up, hat brim + hawk eyes + mustache/goatee (centre x, top y, width; height = width * 48/50)
ICON_SIZE = (50, 48)
ICON_BOX = (735, 40, 760)

# Portrait (sprite 1346, BVN standing art: box x -3..150, y 73..456, head ~y 75-110, centre x ~72).
# The face (card-art x 256, between the eyes) goes on the BVN head centre; the sword side extends to the right.
PORTRAIT_W, PORTRAIT_TOP, PORTRAIT_CX, PORTRAIT_FADE = 165, 75, 72, 14
CARD_FACE_X = 256

# Cut-ins (sprite 1676 union box)
CUTIN_BOX = (-90, -64, 121.5, 70)
FACE1_H = 134                                  # card cut-out scaled to the box height, flat bottom on the box bottom
# face2 = the S+I "dun-dun" eyes panel: close-up eye band, graded hard, glowing golden irises, lens-flare streak,
# focus lines, dark vignette, crisp gold letterbox edges (top / bottom) and soft ends (left / right)
FACE2_SIZE, FACE2_SCALE = (224, 104), 0.22
FACE2_IRIS = ((516.2, 275.3), (960.6, 274.5))  # iris centres in the close-up (source px), radius ~33
FACE2_EYE_Y = 0.42                             # eye line at 42% of the panel height
FACE2_FADE = 16                                # left / right fade (px)
FACE2_GOLD = (255, 196, 48)                    # iris glow / flare colour
FACE2_SHADOW = (26, 4, 12)                     # vignette / shadow tint (Mihawk crimson-black)
FACE2_LINE = (214, 160, 64)                    # letterbox edge line
FACE2_FOCUS = 54                               # focus (speed) lines converging on the eyes

# Banner (sprite 1983): sharp close-up face band left of centre over a crimson coat-texture field + sword slashes
BANNER = (510, 85)
BANNER_FACE = (0.2, 105, 170)                  # scale, source top row, banner x of the face centre (source x 735)
BANNER_SRC_W = 1420                            # ignore the player-UI "(i)" mark at the close-up's top-right corner
BANNER_FADE = (40, 70)                         # face band soft edges (left, right)
BANNER_STOPS = [(110, 14, 32), (170, 26, 42), (120, 16, 34), (30, 8, 20)]
BANNER_TEX = (1215, 300, 1420, 829)            # crimson floral coat region of the close-up, tiled as texture
BANNER_TEX_BLUR, BANNER_TEX_GAIN = 1.8, 0.8    # soft cloth texture, no readable motifs
BANNER_SLASHES = [((280, 96), (505, -10), 1.7, 6.0, 1.0),   # (p0, p1, core half-width, glow radius, strength)
                  ((335, 96), (470, 6), 0.9, 3.5, 0.8)]
SLASH_GLOW = (170, 255, 200)                   # pale green-white, Mihawk's flying slash


def poly_mask(size, poly, ss=4):
    """Anti-aliased polygon mask (4x supersampled, box-filtered down)."""
    w, h = size
    m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).polygon([(x * ss, y * ss) for x, y in poly], fill=255)
    return m.resize((w, h), Image.BOX)


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def to_l(arr):
    return Image.fromarray(np.clip(np.asarray(arr) * 255 + 0.5, 0, 255).astype(np.uint8), 'L')


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


def card_cutout():
    im = Image.open(CARD).convert('RGBA')
    im.putalpha(poly_mask(im.size, CARD_POLY))
    return im


def card_art(cut, scale=None, height=None, width=None, fade_bottom=0):
    """Scale the card cut-out (cropped to the traced silhouette) to a given scale/height/width.

    Returns (image, scale, source x of the image's left edge)."""
    xs, ys = [p[0] for p in CARD_POLY], [p[1] for p in CARD_POLY]
    box = (min(xs), min(ys), max(xs), max(ys))
    bw, bh = box[2] - box[0], box[3] - box[1]
    scale = scale or (height / bh if height else width / bw)
    size = (round(bw * scale), round(bh * scale))
    im = premul_resize(cut, size, box=box)
    if fade_bottom:
        a = np.asarray(im.getchannel('A'), dtype=np.float32) / 255
        ys_ = np.arange(size[1])
        a = a * smoothstep((size[1] - 0.5 - ys_) / fade_bottom)[:, None]
        im.putalpha(to_l(a))
    return im, scale, box[0]


def make_icon(close):
    cx, top, w = ICON_BOX
    h = w * ICON_SIZE[1] / ICON_SIZE[0]
    im = close.resize(ICON_SIZE, Image.LANCZOS, box=(cx - w / 2, top, cx + w / 2, top + h))
    im = ImageEnhance.Brightness(im).enhance(1.06)   # the anime frame is dim next to the BVN icons
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.15)
    return im.convert('RGBA')


def face2_box():
    """Source box of the face2 panel: centred between the irises, eye line at FACE2_EYE_Y."""
    w, h = FACE2_SIZE
    (x1, y1), (x2, y2) = FACE2_IRIS
    sw, sh = w / FACE2_SCALE, h / FACE2_SCALE
    cx, ey = (x1 + x2) / 2, (y1 + y2) / 2
    return (cx - sw / 2, ey - FACE2_EYE_Y * sh, cx + sw / 2, ey + (1 - FACE2_EYE_Y) * sh)


def hash01(*keys):
    """Deterministic integer hash -> [0, 1)."""
    x = 0x9E3779B9
    for k in keys:
        x = ((x ^ (int(k) & 0xFFFFFFFF)) * 0x85EBCA6B) & 0xFFFFFFFF
        x ^= x >> 13
        x = (x * 0xC2B2AE35) & 0xFFFFFFFF
        x ^= x >> 16
    return x / 4294967296.0


def make_face2(close):
    w, h = FACE2_SIZE
    box = face2_box()
    src = close.convert('RGB')
    rgb = np.asarray(src.resize((w, h), Image.LANCZOS, box=box), dtype=np.float64) / 255
    k = FACE2_SCALE
    (x1, y1), (x2, y2) = [((x - box[0]) * k, (y - box[1]) * k) for x, y in FACE2_IRIS]
    ey, cx = (y1 + y2) / 2, (x1 + x2) / 2
    ys, xs = np.mgrid[0:h, 0:w] + 0.5

    # iris mask: orange-gold hue in the source, box-filtered down (soft edge)
    hsv = np.asarray(src.convert('HSV'), dtype=np.float64) / 255
    iris = ((hsv[..., 0] > 22 / 360) & (hsv[..., 0] < 50 / 360) & (hsv[..., 1] > 0.55) & (hsv[..., 2] > 0.5))
    near = np.zeros(iris.shape, bool)
    for x, y in FACE2_IRIS:
        near[int(y) - 40:int(y) + 40, int(x) - 40:int(x) + 40] = True
    im = Image.fromarray((iris & near).astype(np.uint8) * 255, 'L')
    iris = np.asarray(im.resize((w, h), Image.BOX, box=box), dtype=np.float64) / 255

    # grade: hard contrast, cool-desaturated skin, crimson-black shadows
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    rgb = rgb * 0.72 + lum[..., None] * 0.28
    rgb = np.clip((rgb - 0.07) / 0.86, 0, 1) ** 1.25
    shadow = np.array(FACE2_SHADOW) / 255
    t = smoothstep((0.42 - lum) / 0.36)[..., None]
    rgb = rgb * (1 - 0.55 * t) + shadow * 0.55 * t

    # golden irises: lifted towards gold, then bloom
    gold = np.array(FACE2_GOLD) / 255
    ir = iris[..., None]
    rgb = rgb * (1 - 0.65 * ir) + np.clip(rgb * 1.35 + gold * 0.45, 0, 1) * 0.65 * ir
    bloom = Image.fromarray((iris * 255).astype(np.uint8), 'L')
    b1 = np.asarray(bloom.filter(ImageFilter.GaussianBlur(2.5)), dtype=np.float64) / 255
    b2 = np.asarray(bloom.filter(ImageFilter.GaussianBlur(7)), dtype=np.float64) / 255
    glow = np.clip(1.2 * b1 + 1.4 * b2, 0, 1)[..., None]
    rgb = 1 - (1 - rgb) * (1 - glow * gold * 0.85)                      # screen

    # dark vignette around the eye band
    rho = np.hypot((xs - cx) / (w * 0.56), (ys - ey) / (h * 0.62))
    v = smoothstep((rho - 0.55) / 0.5)[..., None]
    rgb = rgb * (1 - 0.88 * v) + shadow * 0.88 * v

    # focus lines: thin pale wedges from the border towards the eyes (outside the eye band)
    ss = 4
    yy, xx = (np.mgrid[0:h * ss, 0:w * ss] + 0.5) / ss
    ang = np.arctan2((yy - ey) * 2.1, xx - cx)
    rr = np.hypot((xx - cx) / (w * 0.5), (yy - ey) / (h * 0.5))
    lines = np.zeros_like(xx)
    for i in range(FACE2_FOCUS):
        a0 = (i + 0.7 * hash01(i, 1)) / FACE2_FOCUS * 2 * np.pi - np.pi
        width = 0.006 + 0.010 * hash01(i, 2)
        r0 = 0.62 + 0.30 * hash01(i, 3)
        da = np.abs((ang - a0 + np.pi) % (2 * np.pi) - np.pi)
        lines = np.maximum(lines, np.clip(1 - da / (width * np.clip(rr - r0, 0, None) / 0.4 + 1e-6), 0, 1)
                           * (rr > r0) * (0.35 + 0.4 * hash01(i, 4)))
    lines = lines.reshape(h, ss, w, ss).mean(axis=(1, 3))[..., None]
    rgb = rgb * (1 - lines) + np.array([1.0, 0.93, 0.80]) * lines

    # lens flare: horizontal streak through both irises + 4-point stars on them
    dy = ys - ey
    peak = np.maximum(np.exp(-np.abs(xs - x1) / 34), np.exp(-np.abs(xs - x2) / 34))
    along = 0.18 + 0.82 * peak
    streak = along * (np.exp(-(dy / 0.7) ** 2) + 0.45 * np.exp(-(dy / 2.6) ** 2))
    star = np.zeros_like(xs)
    for x, y in ((x1, y1), (x2, y2)):
        ddx, ddy = xs - x, ys - y
        star += np.exp(-(ddx / 0.8) ** 2) * np.exp(-np.abs(ddy) / 5.5)                  # vertical spike
        star += 0.9 * np.exp(-(ddx ** 2 + ddy ** 2) / 6.0)                              # hot core
        for sgn in (1, -1):                                                            # small diagonals
            dd = (ddx + sgn * ddy) / np.sqrt(2)
            dn = (ddx - sgn * ddy) / np.sqrt(2)
            star += 0.35 * np.exp(-(dn / 0.7) ** 2) * np.exp(-np.abs(dd) / 2.2)
    flare = np.clip(streak + star, 0, 1.6)[..., None]
    hot = np.array([1.0, 0.98, 0.88])
    rgb = 1 - (1 - rgb) * (1 - np.clip(flare * (gold * 0.5 + hot * 0.5), 0, 1))

    # crisp letterbox edges, soft left / right ends
    rgb[0], rgb[h - 1] = np.array(FACE2_LINE) / 255, np.array(FACE2_LINE) / 255
    rgb[1], rgb[h - 2] = shadow, shadow
    ax = smoothstep(xs[0] / FACE2_FADE) * smoothstep((w - xs[0]) / FACE2_FADE)
    out = Image.fromarray(np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    out.putalpha(to_l(np.repeat(ax[None], h, axis=0)))
    return out


def gradient(w, h, stops):
    t = np.linspace(0, 1, w) * (len(stops) - 1)
    i = np.minimum(t.astype(int), len(stops) - 2)
    f = (t - i)[:, None]
    a = np.array(stops, dtype=np.float64)
    return np.repeat((a[i] * (1 - f) + a[i + 1] * f)[None], h, axis=0)


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


def make_banner(close):
    w, h = BANNER
    # crimson field textured with the coat's floral print (mirrored tiles), vignetted top/bottom
    tex = close.crop(BANNER_TEX)
    tex = tex.resize((round(tex.width * h / tex.height), h), Image.LANCZOS)
    strip, x, k = Image.new('RGB', (w, h)), 0, 0
    while x < w:
        strip.paste(tex if k % 2 == 0 else tex.transpose(Image.FLIP_LEFT_RIGHT), (x, 0))
        x, k = x + tex.width, k + 1
    lum = np.asarray(strip.filter(ImageFilter.GaussianBlur(BANNER_TEX_BLUR)), dtype=np.float64)
    lum = lum.mean(axis=2, keepdims=True) / 255
    bg = gradient(w, h, BANNER_STOPS) * (0.55 + BANNER_TEX_GAIN * lum)
    bg *= (1 - 0.4 * np.abs(np.linspace(-1, 1, h)) ** 2)[:, None, None]
    col = np.array(SLASH_GLOW, dtype=np.float64)
    for p0, p1, hw, gr, strength in BANNER_SLASHES:
        core, gl = slash((w, h), p0, p1, hw, gr)
        bg = bg * (1 - 0.6 * strength * gl[..., None]) + col * 0.6 * strength * gl[..., None]
        bg = bg * (1 - strength * core[..., None]) + 255 * strength * core[..., None]
    out = Image.fromarray(np.clip(bg + 0.5, 0, 255).astype(np.uint8))
    # sharp face band with soft left/right edges
    s, y0, fx = BANNER_FACE
    fw = round(BANNER_SRC_W * s)
    face = close.resize((fw, h), Image.LANCZOS, box=(0, y0, BANNER_SRC_W, y0 + h / s))
    xs = np.arange(fw) + 0.5
    a = smoothstep(xs / BANNER_FADE[0]) * smoothstep((fw - xs) / BANNER_FADE[1])
    out.paste(face, (round(fx - 735 * s), 0), to_l(np.repeat(a[None], h, axis=0)))
    return out.convert('RGBA')


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
    """A few BVN cut-in frames for reference: exported once with FFDec into a temp dir (skipped if unavailable)."""
    pre = os.path.join(BVN, 'DefineSprite_1676')
    if os.path.isdir(pre):
        fs = frames(pre)
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


def make_preview(out, layout):
    font, small = ImageFont.truetype(FONT, 14), ImageFont.truetype(FONT, 11)
    W = 1240
    sheet = Image.new('RGB', (W, 4000), (22, 22, 28))
    d = ImageDraw.Draw(sheet)
    y = 8

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

    # icon in a row of BVN / OP icons
    title('icon (5th) in a row of BVN / OP select icons: 3x and 1x')
    bvn_icons = frames(os.path.join(BVN, 'DefineSprite_1465'))
    row = [Image.open(bvn_icons[i]).convert('RGBA') for i in (5, 12, 26, 37)] + [out['icon']] + \
          [Image.open(os.path.join(OPUI, 'icon', f'{n}.png')).convert('RGBA') for n in ('佐罗', '罗', '明哥')]
    for i, im in enumerate(row):
        sheet.paste(scaled(im, 3), (10 + i * 154, y))
        sheet.paste(im, (10 + i * 54, y + 152))
    y += 152 + 48 + 14

    # banners as on the versus-loading screen (two stacked), plus a longer stack for comparison
    title('banner stacked with BVN / OP banners (1x)')
    bvn_banners = frames(os.path.join(BVN, 'DefineSprite_1983'))
    stack = [Image.open(bvn_banners[3]), out['banner'], Image.open(bvn_banners[9]),
             Image.open(os.path.join(OPUI, 'banner', '罗.png'))]
    sheet.paste(Image.new('RGB', (530, 4 * 91 + 6), (14, 14, 26)), (10, y))
    for i, im in enumerate(stack):
        sheet.paste(im.convert('RGB'), (20, y + 6 + i * 91))
    sheet.paste(Image.new('RGB', (530, 2 * 91 + 6), (14, 14, 26)), (570, y))
    sheet.paste(out['banner'].convert('RGB'), (580, y + 6))
    sheet.paste(Image.open(bvn_banners[20]).convert('RGB'), (580, y + 6 + 91))
    y += 4 * 91 + 6 + 16

    # portraits in sprite-1346 local coordinates
    title('portrait next to BVN / OP standing art in sprite-1346 local px (panel = x -12..189, y 60..330, '
          'line = y 73); last = mirrored (P1)')
    lx0, ly0, lx1, ly1 = -12, 60, 189, 330
    pw, ph = lx1 - lx0, ly1 - ly0
    bvn_ports = frames(os.path.join(BVN, 'DefineSprite_1346'))
    opl = json.load(open(os.path.join(OPUI, 'layout.json'), encoding='utf-8'))['portrait']
    panels = [(Image.open(bvn_ports[i]).convert('RGBA'), PORTRAIT_ORIGIN, False) for i in BVN_PORTRAITS]
    panels.append((Image.open(os.path.join(OPUI, 'portrait', '佐罗.png')).convert('RGBA'), tuple(opl['佐罗']), False))
    panels.append((out['portrait'], tuple(layout['portrait']), False))
    panels.append((out['portrait'], tuple(layout['portrait']), True))
    for i, (im, (px, py), mirror) in enumerate(panels):
        p = Image.new('RGBA', (pw, ph), (30, 34, 52, 255))
        layer = Image.new('RGBA', (pw + 800, ph + 800), (0, 0, 0, 0))
        layer.paste(im, (round(px - lx0) + 400, round(py - ly0) + 400))
        layer = layer.crop((400, 400, 400 + pw, 400 + ph))
        if mirror:
            layer = layer.transpose(Image.FLIP_LEFT_RIGHT)
        p.alpha_composite(layer)
        ImageDraw.Draw(p).line([(-3 - lx0, 73 - ly0), (150 - lx0, 73 - ly0)], fill=(90, 90, 120, 255))
        sheet.paste(p.convert('RGB'), (10 + i * (pw + 4), y))
    y += ph + 16

    # cut-ins in the sprite-1676 box
    title('cut-ins in the sprite-1676 box (-90..121.5, -64..70): BVN refs, face1, face2, face1 mirrored (P2); 1x / 2x')
    bx0, by0, bx1, by1 = CUTIN_BOX
    bw, bh = round(bx1 - bx0), round(by1 - by0)
    f1, f2 = out['face1'], out['face2']
    items = [(im, (bx0, by0)) for im in bvn_cutins()]
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
    close = Image.open(CLOSE).convert('RGB')
    cut = card_cutout()
    portrait, p_scale, p_x0 = card_art(cut, width=PORTRAIT_W, fade_bottom=PORTRAIT_FADE)
    face1, _, _ = card_art(cut, height=FACE1_H)
    out = {
        'icon': make_icon(close),
        'portrait': portrait,
        'banner': make_banner(close),
        'face1': face1,
        'face2': make_face2(close),
    }
    assert out['icon'].size == ICON_SIZE and out['banner'].size == BANNER
    assert portrait.width <= 165 and portrait.height <= 300
    cx, cy = (CUTIN_BOX[0] + CUTIN_BOX[2]) / 2, (CUTIN_BOX[1] + CUTIN_BOX[3]) / 2
    f2 = out['face2']
    layout = {
        'icon': [0, 0],
        'portrait': [round(PORTRAIT_CX - (CARD_FACE_X - p_x0) * p_scale, 2), PORTRAIT_TOP],
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
