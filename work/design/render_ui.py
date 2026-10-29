#!/usr/bin/env python3
"""Korean UI bitmaps for Bleach vs Naruto 2.6 (한글판) -- v2 "Tempered Ink".

Run:   tools/venv/bin/python work/design/render_ui.py
Deps:  Pillow, numpy. Deterministic (fixed seeds). Design notes: work/design/philosophy_v2.md
Fonts: tools/fonts/Hahmlet-VariableFont_wght.ttf (OFL, display serif, wght 600-900 via variation axis),
       tools/fonts/GothicA1-Black.ttf (OFL, labels); NanumGothic only for preview captions / loader mock.
v1 (first pass) is kept as work/design/render_ui_v1.py + work/design/out_v1/.

Outputs (work/design/out/):
  splash_600x400.png        opaque splash (RGBA, alpha 255): preloader backdrop + intro fade card
  586.png 588.png           title logo pieces 블리치 / 나루토 (transparent)
  <id>.png                  menu labels, config labels/values, config + how-to headers; each has the exact
                            pixel size of work/img/<id>.png
  647.png                   fully transparent (publisher logo removed)
  preview_ui_v2.png         splash/title/config/how-to mocks + every label: original | v1 | v2 | in game
  preview_ui_v2_zoom2x.png  labels and logos at 2x

In-game colour facts that drive the label design (read from the SWF, see report):
  * the title carousel (sprite 620) places every label sprite with an ADD colour transform
    (+255 R, +0 G, +255 B), so each pixel renders as (255, G, 255): only GREEN and alpha of
    592/595/598/601/604/607/610/613 are visible. Low G = rose-magenta, high G = white.
  * config labels (sprite 836) and values (691/698) are NOT tinted and sit on the light-grey
    sketch 673.jpg, scaled x0.888.
  * the how-to header 870 sits on black, scaled x1.236.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "work" / "img"
OUT = ROOT / "work" / "design" / "out"
OUT_V1 = ROOT / "work" / "design" / "out_v1"
SHOTS = ROOT / "work" / "shots"
FONTS = ROOT / "tools" / "fonts"

HAHMLET = FONTS / "Hahmlet-VariableFont_wght.ttf"   # OFL, Hypertype -- knife-cut display serif
GOTHIC_K = FONTS / "GothicA1-Black.ttf"              # OFL, HanYang I&C -- heavy grotesque
NANUM = FONTS / "NanumGothic-Regular.ttf"            # the game's own UI font (loader mock only)


def HAH(w):
    return (HAHMLET, w)


# ---- palette (shared with web/index.html) ---------------------------------------------------------------
NIGHT_TOP = (25, 30, 47)      # ink thinned by night
NIGHT_MID = (15, 18, 31)
NIGHT_LOW = (8, 9, 15)
MOON = (238, 233, 223)        # moon-paper white: cold light
EMBER = (242, 128, 34)        # ember orange: warm light
SEAL = (190, 36, 29)          # seal vermilion: the stamp, used once
INK = (17, 21, 33)            # ink for type on light grounds
CRIMSON_T, CRIMSON_B = (200, 24, 32), (138, 10, 18)

SS = 4  # supersampling for all vector work


# ---------------------------------------------------------------------------------------------------------
# fonts and text
# ---------------------------------------------------------------------------------------------------------
_fc = {}


def font(spec, size):
    path, wght = spec if isinstance(spec, tuple) else (spec, None)
    key = (str(path), wght, int(round(size * 64)))
    f = _fc.get(key)
    if f is None:
        f = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.BASIC)
        if wght is not None:
            f.set_variation_by_axes([wght])
        _fc[key] = f
    return f


class Text:
    """One line of text sized so that the ink of `ref` is exactly `cap` px tall.
    Horizontal metrics are measured on ink (not advance) so centring is optical."""

    def __init__(self, text, spec, cap, ref="가", tracking=0.0, space=1.0, kern=None):
        self.text, self.spec, self.tracking, self.space = text, spec, tracking, space
        self.kern = kern or {}
        l, t, r, b = font(spec, 1000).getbbox(ref, anchor="ls")
        self.size = cap * 1000.0 / (b - t)
        self.cap = cap
        self.asc = self.size * (-t) / 1000.0        # baseline minus top of reference ink
        f = font(spec, self.size * SS)
        lo, hi = self._ink(f, self._layout(f, SS))
        self.w = (hi - lo) / SS
        self.at(left=0, top=0)

    def _layout(self, f, scale):
        xs, x, prev = [], 0.0, None
        for ch in self.text:
            if prev is not None:
                x += self.kern.get(prev + ch, 0.0) * scale
            xs.append(x)
            x += f.getlength(ch) * (self.space if ch == " " else 1.0) + self.tracking * scale
            prev = ch
        return xs

    def _ink(self, f, xs):
        bb = [(x + f.getbbox(c, anchor="ls")[0], x + f.getbbox(c, anchor="ls")[2])
              for x, c in zip(xs, self.text) if c.strip()]
        return min(b[0] for b in bb), max(b[1] for b in bb)

    def at(self, cx=None, left=None, right=None, top=None, cy=None):
        if cy is not None:
            top = cy - self.cap / 2.0
        if cx is not None:
            left = cx - self.w / 2.0
        elif right is not None:
            left = right - self.w
        self.left, self.top = left, top
        self.right, self.bottom = left + self.w, top + self.cap
        self.cx, self.cy = left + self.w / 2.0, top + self.cap / 2.0
        self.baseline = top + self.asc
        return self

    def mask(self, W, H, stroke=0.0):
        f = font(self.spec, self.size * SS)
        xs = self._layout(f, SS)
        lo, _ = self._ink(f, xs)
        ox, by = self.left * SS - lo, self.baseline * SS
        im = Image.new("L", (W * SS, H * SS), 0)
        d = ImageDraw.Draw(im)
        sw = int(round(stroke * SS))
        for x, c in zip(xs, self.text):
            if c.strip():
                d.text((ox + x, by), c, font=f, fill=255, anchor="ls", stroke_width=sw, stroke_fill=255)
        return np.asarray(im.resize((W, H), Image.BOX), dtype=np.float32) / 255.0


# ---------------------------------------------------------------------------------------------------------
# raster helpers (float, straight alpha)
# ---------------------------------------------------------------------------------------------------------
def c01(c):
    return np.asarray(c, np.float32) / 255.0


def blur(m, r):
    im = Image.fromarray(np.clip(m * 255.0 + 0.5, 0, 255).astype(np.uint8), "L")
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0


def shape_mask(W, H, fn):
    """fn(draw, s) draws white shapes in a W*SS x H*SS canvas (s = SS scale)."""
    im = Image.new("L", (W * SS, H * SS), 0)
    fn(ImageDraw.Draw(im), SS)
    return np.asarray(im.resize((W, H), Image.BOX), dtype=np.float32) / 255.0


def vramp(W, H, stops):
    """Vertical colour ramp. stops: [(y, (r,g,b)), ...] in px."""
    ys = np.arange(H, dtype=np.float32) + 0.5
    pos = [s[0] for s in stops]
    cols = np.stack([c01(s[1]) for s in stops])
    g = np.stack([np.interp(ys, pos, cols[:, k]) for k in range(3)], axis=-1)
    return np.broadcast_to(g[:, None, :], (H, W, 3)).copy()


def hramp(W, H, stops):
    xs = np.arange(W, dtype=np.float32) + 0.5
    pos = [s[0] for s in stops]
    cols = np.stack([c01(s[1]) for s in stops])
    g = np.stack([np.interp(xs, pos, cols[:, k]) for k in range(3)], axis=-1)
    return np.broadcast_to(g[None, :, :], (H, W, 3)).copy()


def grid(W, H):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    return x + 0.5, y + 0.5


def ellipse_falloff(W, H, cx, cy, rx, ry, power=2.0):
    x, y = grid(W, H)
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    return np.clip(1.0 - d, 0.0, 1.0) ** power


def smooth_noise(W, H, cell, seed):
    rng = np.random.default_rng(seed)
    gw, gh = int(W / cell) + 2, int(H / cell) + 2
    small = Image.fromarray((rng.random((gh, gw)) * 255).astype(np.uint8), "L")
    big = small.resize((int(gw * cell), int(gh * cell)), Image.BICUBIC).crop((0, 0, W, H))
    return np.asarray(big, dtype=np.float32) / 255.0


class Canvas:
    def __init__(self, W, H, ground=None):
        self.W, self.H = W, H
        self.rgb = np.zeros((H, W, 3), np.float32)
        self.a = np.zeros((H, W), np.float32)
        if ground is not None:
            self.rgb[:] = ground
            self.a[:] = 1.0

    def paint(self, color, mask, opacity=1.0):
        c = color if isinstance(color, np.ndarray) else c01(color)
        sa = np.clip(mask * opacity, 0.0, 1.0)
        oa = sa + self.a * (1.0 - sa)
        num = c * sa[..., None] + self.rgb * (self.a * (1.0 - sa))[..., None]
        ok = oa > 1e-6
        self.rgb = np.where(ok[..., None], num / np.where(ok, oa, 1.0)[..., None], 0.0)
        self.a = oa

    def image(self):
        arr = np.dstack([np.clip(self.rgb, 0, 1), np.clip(self.a, 0, 1)])
        return Image.fromarray((arr * 255.0 + 0.5).astype(np.uint8), "RGBA")


def orig_size(i):
    return Image.open(IMG / f"{i}.png").size


# ---------------------------------------------------------------------------------------------------------
# the cut: a straight stroke that tapers to nothing at its far end(s)
# ---------------------------------------------------------------------------------------------------------
def blade_mask(W, H, x0, x1, yfun, wfun, n=240):
    """Polygon between x0..x1 around centre line y=yfun(x), half-thickness wfun(u) (u in 0..1)."""
    def fn(d, s):
        up, dn = [], []
        for k in range(n + 1):
            u = k / n
            x = x0 + (x1 - x0) * u
            y, w = yfun(x), wfun(u)
            up.append((x * s, (y - w) * s))
            dn.append((x * s, (y + w) * s))
        d.polygon(up + dn[::-1], fill=255)
    return shape_mask(W, H, fn)


# ---------------------------------------------------------------------------------------------------------
# splash 600x400
# ---------------------------------------------------------------------------------------------------------
def seal_mask(W, H, box, seed, radius=2.0):
    """Carved-stamp block: a rounded rectangle whose edge is bitten in places and whose ink is
    very slightly uneven, like a vermilion seal impression."""
    x0, y0, x1, y1 = box
    m = shape_mask(W, H, lambda d, s: d.rounded_rectangle([x0 * s, y0 * s, x1 * s, y1 * s],
                                                           radius=radius * s, fill=255))
    x, y = grid(W, H)
    dist = np.minimum(np.minimum(x - x0, x1 - x), np.minimum(y - y0, y1 - y))
    edge = np.clip(1.6 - dist, 0.0, 1.0)
    bite = (smooth_noise(W, H, 2.2, seed) > 0.70).astype(np.float32)
    mottle = smooth_noise(W, H, 3.0, seed + 1)
    return m * (1.0 - 0.9 * edge * bite) * (0.90 + 0.10 * mottle)


def render_splash():
    W, H = 600, 400
    x, y = grid(W, H)
    # ground: ink thinned by night; darkest behind the loader line and bar (y 300..400)
    cv = Canvas(W, H, vramp(W, H, [(0, NIGHT_TOP), (180, NIGHT_MID), (320, NIGHT_LOW), (400, (6, 7, 12))]))
    calm = np.clip((300.0 - y) / 90.0, 0.0, 1.0)          # light fields die out before the loader zone
    cv.paint((150, 174, 220), ellipse_falloff(W, H, 196, 92, 300, 175, 1.7), 0.12)
    cv.paint((236, 110, 26), ellipse_falloff(W, H, 410, 226, 300, 150, 1.7) * calm, 0.16)

    # --- the two names, staggered across the cut
    CAP, STAG = 58, 64
    t1 = Text("블리치", HAH(900), CAP, tracking=1.0).at(cx=300 - STAG, top=76)
    t2 = Text("나루토", HAH(900), CAP, tracking=1.0).at(cx=300 + STAG, top=184)
    my = (t1.bottom + t2.top) / 2.0
    slope = -0.085

    def cut_y(xx):
        return my + slope * (xx - 300.0)

    # --- quiet geometric marks in the two empty quadrants
    # upper right: a slim crescent, a fang of cold light; lower left: a measured spiral (warm)
    mcx, mcy, r = 482.0, 90.0, 24.0
    bx, by_, br = mcx - 0.20 * r, mcy - 0.12 * r, 0.96 * r
    crescent = shape_mask(W, H, lambda d, s: d.ellipse([(mcx - r) * s, (mcy - r) * s, (mcx + r) * s, (mcy + r) * s], fill=255))
    bite = shape_mask(W, H, lambda d, s: d.ellipse([(bx - br) * s, (by_ - br) * s, (bx + br) * s, (by_ + br) * s], fill=255))
    crescent = np.clip(crescent - bite, 0, 1)
    cv.paint(MOON, blur(crescent, 5.0), 0.12)
    cv.paint(MOON, crescent, 0.62)

    scx, scy, rmax, turns = 124.0, 236.0, 33.0, 3.25

    def spiral(d, s):
        pts = []
        steps = 900
        for k in range(steps + 1):
            th = turns * 2 * math.pi * k / steps
            rr = rmax * k / steps
            pts.append(((scx + rr * math.cos(th - 0.9)) * s, (scy + rr * math.sin(th - 0.9)) * s))
        d.line(pts, fill=255, width=int(1.0 * s), joint="curve")
    cv.paint(EMBER, shape_mask(W, H, spiral), 0.34)

    # --- the cut, broken by the VS
    GAP, X0, X1, WMAX = 27.0, 40.0, 560.0, 1.35
    cut_col = hramp(W, H, [(0, MOON), (262, MOON), (338, EMBER), (600, EMBER)])
    left = blade_mask(W, H, X0, 300 - GAP, cut_y, lambda u: WMAX * u ** 0.85)
    right = blade_mask(W, H, 300 + GAP, X1, cut_y, lambda u: WMAX * (1 - u) ** 0.85)
    cut = np.clip(left + right, 0, 1)
    cv.paint(cut_col, blur(cut, 2.2), 0.35)
    cv.paint(cut_col, cut, 0.96)
    vs = Text("VS", HAH(800), 12.0, ref="V", tracking=1.6).at(cx=300.5, cy=cut_y(300) + 0.5)
    cv.paint(MOON, vs.mask(W, H), 0.92)

    # --- names
    cv.paint(vramp(W, H, [(t1.top, (246, 243, 236)), (t1.bottom, (220, 214, 204))]), t1.mask(W, H))
    cv.paint(vramp(W, H, [(t2.top, (250, 150, 58)), (t2.bottom, (230, 104, 18))]), t2.mask(W, H))

    # --- credit (whispered) and edition seal
    rea = Text("REA PROJECT", HAH(600), 9.0, ref="H", tracking=3.4).at(cx=300, top=38)
    cv.paint(MOON, rea.mask(W, H), 0.60)

    ver = Text("2.6", HAH(800), 15.0, ref="2", tracking=0.6)
    han = Text("한글판", HAH(900), 14.0, tracking=1.2)
    padx, pady, gap = 8.0, 6.0, 11.0
    total = ver.w + gap + han.w + 2 * padx
    row_top = t2.bottom + 30.0
    xl = 300.0 - total / 2.0
    ver.at(left=xl, cy=row_top + 7.5)
    box = (xl + ver.w + gap, ver.cy - han.cap / 2 - pady, xl + total, ver.cy + han.cap / 2 + pady)
    han.at(left=box[0] + padx, cy=ver.cy)
    cv.paint(MOON, ver.mask(W, H), 0.94)
    cv.paint(SEAL, seal_mask(W, H, box, seed=31))
    cv.paint(MOON, han.mask(W, H), 0.97)

    # --- material: soft vignette + fine grain
    d = np.sqrt(((x - 300) / 330.0) ** 2 + ((y - 200) / 240.0) ** 2)
    cv.rgb *= (1.0 - 0.30 * np.clip(d - 0.55, 0, 1) ** 1.4)[..., None]
    rng = np.random.default_rng(7)
    cv.rgb += rng.normal(0.0, 1.3 / 255.0, (H, W))[..., None].astype(np.float32)
    meta = dict(t1=t1, t2=t2, cut_y=cut_y, row_top=row_top)
    return cv.image(), meta


# ---------------------------------------------------------------------------------------------------------
# title logo pieces (586 / 588): knife-cut serif with a clean keyline of light
# ---------------------------------------------------------------------------------------------------------
LOGO_CAP = 47.0


def render_logo(i, text, top_col, bot_col):
    W, H = orig_size(i)
    t = Text(text, HAH(900), LOGO_CAP, tracking=2.0).at(cx=W / 2.0, cy=H / 2.0 + 0.5)
    assert t.left >= 8 and t.right <= W - 8, (i, t.left, t.right)
    cv = Canvas(W, H)
    cv.paint((255, 255, 255), blur(t.mask(W, H, stroke=3.0), 3.4), 0.80)
    cv.paint((255, 255, 255), t.mask(W, H, stroke=2.1))
    cv.paint(vramp(W, H, [(t.top, top_col), (t.bottom, bot_col)]), t.mask(W, H))
    return cv.image(), t


# ---------------------------------------------------------------------------------------------------------
# labels
# ---------------------------------------------------------------------------------------------------------
LABEL_FONT = GOTHIC_K
LABEL_CAP = 21.5      # ink height of a full Hangul syllable (Latin originals: caps 22, x-height 16)
LABEL_CY = 19.5       # originals put Latin caps at y 8..30 in every canvas (39 or 45 px tall)
LABEL_MARGIN = 4.5

# title menu (tinted to (255, G, 255) in game): the G channel is the design.
# body G runs 128 -> 44 top to bottom (soft rose -> deep magenta), keyline/halo G = 255 (white).
MENU_TOP, MENU_BOT = (114, 128, 146), (30, 44, 62)
# config names / values (untinted, on light-grey sketch)
NAME_TOP, NAME_BOT = (48, 57, 80), (14, 18, 30)
VALUE_TOP, VALUE_BOT = (196, 92, 22), (138, 52, 6)     # burnt ember: warm values vs cold names
EMBER_DEEP = (176, 74, 12)                                # ember that holds up on light grounds


def fit_text(text, W, cap=LABEL_CAP, spec=None):
    spec = spec or LABEL_FONT
    t = Text(text, spec, cap, tracking=0.3, space=0.8)
    while t.w > W - 2 * LABEL_MARGIN:
        cap -= 0.25
        t = Text(text, spec, cap, tracking=0.3, space=0.8)
    return t


def render_label(i, text, kind, spec=None):
    W, H = orig_size(i)
    t = fit_text(text, W, spec=spec)
    # config names sit in a left-aligned column (originals start their ink at x=8); menu items and
    # values are centred (carousel centres every canvas on x=304.5; value arrows hug the canvas ends)
    if kind == "name":   # 724 is placed 3.45 px further right than its siblings; pull its ink back in line,
        # but never so far that the halo touches the canvas edge (narrow 660 ends up ~centred)
        want = 8.0 - (3.45 / CFG_SCALE if i == 724 else 0.0)
        t.at(left=max(5.5, min(want, (W - t.w) / 2.0)) if want + t.w > W - 5.5 else max(5.5, want), cy=LABEL_CY)
    else:
        t.at(cx=W / 2.0, cy=LABEL_CY)
    top, bot = {"menu": (MENU_TOP, MENU_BOT), "name": (NAME_TOP, NAME_BOT), "value": (VALUE_TOP, VALUE_BOT)}[kind]
    cv = Canvas(W, H)
    cv.paint((255, 255, 255), blur(t.mask(W, H, stroke=2.0), 1.7), 0.70)
    cv.paint((255, 255, 255), t.mask(W, H, stroke=1.2))
    cv.paint(vramp(W, H, [(t.top, top), (t.bottom, bot)]), t.mask(W, H))
    return cv.image(), t


def render_config_header(i, text):
    """676: '설정' set large in the display serif, followed by a cut that tapers away to the right."""
    W, H = orig_size(i)
    t = Text(text, HAH(900), 36.0, tracking=3.0).at(left=16.0, cy=32.0)
    cv = Canvas(W, H)
    ry = t.bottom - 4.0
    rule = blade_mask(W, H, t.right + 14.0, W - 16.0, lambda xx: ry, lambda u: 1.25 * (1 - u) ** 0.9)
    cv.paint((255, 255, 255), blur(np.clip(t.mask(W, H, stroke=3.0) + blur(rule, 1.0) * 3, 0, 1), 3.0), 0.75)
    cv.paint((255, 255, 255), t.mask(W, H, stroke=2.0))
    cv.paint(vramp(W, H, [(t.top, (40, 48, 70)), (t.bottom, INK)]), t.mask(W, H))
    cv.paint(EMBER_DEEP, rule, 0.95)
    return cv.image(), t


def render_howto(i, text):
    """870: on black. Moon-white serif, an ember cut beneath that tapers to nothing at both ends."""
    W, H = orig_size(i)
    t = Text(text, HAH(900), 25.0, tracking=2.5, space=0.7).at(cx=167.5, cy=69.5)
    cv = Canvas(W, H)
    ry = t.bottom + 10.0
    half = t.w / 2.0 + 18.0
    rule = blade_mask(W, H, t.cx - half, t.cx + half, lambda xx: ry,
                      lambda u: 1.3 * (4 * u * (1 - u)) ** 0.8)
    cv.paint(vramp(W, H, [(t.top, (250, 247, 240)), (t.bottom, (222, 216, 206))]), t.mask(W, H))
    cv.paint(EMBER, rule, 0.95)
    return cv.image(), t


# ---------------------------------------------------------------------------------------------------------
# job list
# ---------------------------------------------------------------------------------------------------------
LABELS = [
    # id, original, Korean, kind
    (592, "Nornal", "일반 대전", "menu"),
    (595, "Vs Com", "VS 컴퓨터", "menu"),
    (598, "Vs Human", "VS 사람", "menu"),
    (601, "Training", "연습 모드", "menu"),
    (604, "Config", "설정", "menu"),
    (607, "Information", "정보", "menu"),
    (610, "More Games", "더 많은 게임", "menu"),
    (613, "Exit", "나가기", "menu"),
    (660, "Exit", "나가기", "name"),
    (710, "Key Config", "키 설정", "name"),
    (713, "Com Level", "난이도", "name"),
    (716, "Quality", "화질", "name"),
    (719, "Life", "체력", "name"),
    (724, "Time", "시간", "name"),
    (678, "Very Easy", "매우 쉬움", "value"),
    (683, "Easy", "쉬움", "value"),
    (685, "Medium", "보통", "value"),
    (694, "Medium", "보통", "value"),
    (687, "Hard", "어려움", "value"),
    (689, "Very Hard", "매우 어려움", "value"),
    (692, "High", "높음", "value"),
    (696, "Low", "낮음", "value"),
]
MENU_IDS = [i for i, _, _, k in LABELS if k == "menu"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = {}   # id -> (image, note)

    for i, en, ko, kind in LABELS:
        im, t = render_label(i, ko, kind)
        made[i] = (im, f"{en} -> {ko}" + (f"  (cap {t.cap:.2f})" if t.cap < LABEL_CAP - 0.01 else ""))
    im, _ = render_config_header(676, "설정")
    made[676] = (im, "CONFIG -> 설정")
    im, _ = render_howto(870, "조작 방법")
    made[870] = (im, "HOW TO PLAY -> 조작 방법")
    im, _ = render_logo(586, "블리치", (34, 36, 44), (6, 6, 9))
    made[586] = (im, "BLEACH -> 블리치")
    im, _ = render_logo(588, "나루토", CRIMSON_T, CRIMSON_B)
    made[588] = (im, "NARUTO -> 나루토")
    made[647] = (Image.new("RGBA", orig_size(647), (0, 0, 0, 0)), "4399 logo -> transparent")

    for i, (im, note) in made.items():
        assert im.size == orig_size(i), (i, im.size, orig_size(i))
        im.save(OUT / f"{i}.png", optimize=True)
    splash, meta = render_splash()
    assert splash.size == (600, 400)
    splash.save(OUT / "splash_600x400.png", optimize=True)

    build_previews(made, splash)
    for i, (im, note) in made.items():
        print(f"{i}: {im.size[0]}x{im.size[1]}  {note}")
    print("splash_600x400.png 600x400")


# ---------------------------------------------------------------------------------------------------------
# previews: in-game mocks + comparison sheets
# ---------------------------------------------------------------------------------------------------------
def rgba_np(src):
    im = src if isinstance(src, Image.Image) else Image.open(src)
    return np.asarray(im.convert("RGBA"), dtype=np.float32) / 255.0


def np_img(rgb):
    return Image.fromarray((np.clip(rgb, 0, 1) * 255.0 + 0.5).astype(np.uint8), "RGB")


def tint_menu(im):
    """What the title carousel actually shows: colour transform ADD (+255, 0, +255) -> (255, G, 255)."""
    a = np.asarray(im.convert("RGBA")).copy()
    a[..., 0] = 255
    a[..., 2] = 255
    return Image.fromarray(a, "RGBA")


def checker(w, h, s=6, c1=(206, 206, 206), c2=(160, 160, 160)):
    x, y = np.meshgrid(np.arange(w) // s, np.arange(h) // s)
    sel = ((x + y) % 2).astype(bool)
    arr = np.where(sel[..., None], np.array(c2, np.uint8), np.array(c1, np.uint8))
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


def on(bg, im, xy=(0, 0)):
    out = bg.convert("RGBA").copy()
    out.alpha_composite(im.convert("RGBA"), (int(xy[0]), int(xy[1])))
    return out


def loader_mock(splash):
    """The preloader as the game draws it over the splash: its own text lines + progress bar."""
    m = splash.convert("RGB").copy()
    d = ImageDraw.Draw(m)
    d.text((300, 331), "불러오는 중...", font=ImageFont.truetype(str(NANUM), 15), fill=(255, 240, 225), anchor="mm")
    d.text((300, 363), "loading...", font=ImageFont.truetype(str(NANUM), 11), fill=(140, 140, 140), anchor="mm")
    d.rectangle([17, 385, 577, 392], fill=(8, 8, 9))
    d.rectangle([18, 386, 576, 391], fill=(241, 119, 1))
    d.rectangle([18, 386, 64, 391], fill=(205, 27, 27))
    return m


# title screen geometry (final frame of sprite 666 / carousel 620 at rest)
TITLE_POS = {586: (146, 10), 588: (204, 112)}
MENU_SLOTS = [(613, 265, 251), (592, 243, 310), (595, 234, 366)]   # Exit (above) / Normal (selected) / Vs Com
GLOW_XY = (123, 230)                                               # 616: white veil over the carousel
BAR_Y = 381                                                        # status bar starts here (always on top)


def _inpaint(U, keep):
    """Normalised-convolution fill of pixels where keep == 0."""
    w = keep.astype(np.float32)
    num = np.dstack([blur(U[..., k] * w, 9) for k in range(3)])
    den = blur(w, 9)[..., None]
    fill = num / np.maximum(den, 1e-3)
    return U * w[..., None] + fill * (1 - w[..., None])


def title_mock(get):
    """Original title screenshot with the original logo pieces, carousel labels and publisher logo
    un-composited (their bitmaps and positions are known), then `get(id)` versions composited back."""
    S = rgba_np(SHOTS / "intro" / "08_t8.png")[..., :3].copy()
    shot = S.copy()
    bg = rgba_np(IMG / "553.jpg")[..., :3]
    glow = rgba_np(IMG / "616.png")
    Ga = np.zeros((400, 600), np.float32)
    Gc = np.ones((400, 600, 3), np.float32)
    gx, gy = GLOW_XY
    gh = min(glow.shape[0], 400 - gy)
    Ga[gy:gy + gh, gx:gx + glow.shape[1]] = glow[:gh, :, 3]
    Gc[gy:gy + gh, gx:gx + glow.shape[1]] = glow[:gh, :, :3]

    def clean(old, x, y, tint, fallback):
        h, w = old.shape[:2]
        h = min(h, BAR_Y - y)
        old = old[:h]
        reg = shot[y:y + h, x:x + w]
        ga, gc = Ga[y:y + h, x:x + w, None], Gc[y:y + h, x:x + w]
        X = (reg - ga * gc) / np.maximum(1 - ga, 1e-3)
        La, Lc = old[..., 3:4], old[..., :3].copy()
        if tint:
            Lc[..., 0] = 1.0
            Lc[..., 2] = 1.0
        U = np.clip((X - La * Lc) / np.maximum(1 - La, 1e-3), 0, 1)
        bad = np.clip((La[..., 0] - 0.45) / 0.35, 0, 1)
        bad = np.maximum(bad, np.clip((ga[..., 0] - 0.55) / 0.3, 0, 1))
        if fallback == "bg":
            U = U * (1 - bad[..., None]) + bg[y:y + h, x:x + w] * bad[..., None]
        else:   # unknown art underneath: fill the whole footprint from its surroundings
            foot = np.asarray(Image.fromarray((La[..., 0] > 0.02).astype(np.uint8) * 255)
                              .filter(ImageFilter.MaxFilter(5))) > 0
            pad = 12
            big = shot[y - pad:y + h + pad, x - pad:x + w + pad].copy()
            keep = np.ones(big.shape[:2], bool)
            keep[pad:pad + h, pad:pad + w] = ~foot
            U = _inpaint(big, keep)[pad:pad + h, pad:pad + w]
        return U, ga, gc, h

    def put(new, U, ga, gc, x, y, h, tint):
        n = rgba_np(tint_menu(new) if tint else new)[:h]
        Xn = n[..., 3:4] * n[..., :3] + (1 - n[..., 3:4]) * U
        S[y:y + h, x:x + n.shape[1]] = ga * gc + (1 - ga) * Xn

    # publisher logo 647 (scaled x0.7 at 449.65, 343.05) -> now transparent
    old = rgba_np(Image.open(IMG / "647.png").convert("RGBA").resize((145, 42), Image.BILINEAR))
    U, ga, gc, h = clean(old, 450, 343, False, "inpaint")
    put(get(647).resize((145, 42)), U, ga, gc, 450, 343, h, False)
    for i, (x, y) in TITLE_POS.items():
        U, ga, gc, h = clean(rgba_np(IMG / f"{i}.png"), x, y, False, "bg")
        put(get(i), U, ga, gc, x, y, h, False)
    for i, x, y in MENU_SLOTS:
        U, ga, gc, h = clean(rgba_np(IMG / f"{i}.png"), x, y, True, "bg")
        put(get(i), U, ga, gc, x, y, h, True)
    S[BAR_Y:] = shot[BAR_Y:]
    return np_img(S)


# config page geometry: bg 673 at 0,0; header 676 at (18,10); rows in sprite 836 scaled x0.888
CFG_ROWS = [(710, 88.2, 105.8), (713, 88.2, 148.4), (716, 88.2, 185.7), (724, 91.65, 228.3),
            (719, 88.2, 265.6), (660, 88.2, 302.9), (678, 294.75, 148.4), (692, 294.75, 185.7)]
CFG_SCALE = 0.888


def config_mock(get):
    m = Image.open(IMG / "673.jpg").convert("RGBA")
    m.alpha_composite(get(676), (18, 10))
    for i, x, y in CFG_ROWS:
        im = get(i)
        im = im.resize((round(im.width * CFG_SCALE), round(im.height * CFG_SCALE)), Image.LANCZOS)
        m.alpha_composite(im, (round(x), round(y)))
    return m.convert("RGB")


def howto_mock(get):
    """l10n1/05_howto.png with the header area blacked out and 870 placed at its on-screen scale."""
    shot = Image.open(SHOTS / "l10n1" / "05_howto.png").convert("RGB")
    a = np.asarray(shot).astype(np.float32)
    lum = a[40:115].mean(-1)
    ys, xs = np.nonzero(lum > 120)
    sx0, sy0 = xs.min(), ys.min() + 40          # on-screen top-left of the original text ink
    sc = 1.2362671
    ox, oy = sx0 - 35 * sc, sy0 - 58 * sc        # 870 text ink starts at (35, 58) in the bitmap
    m = shot.copy()
    ImageDraw.Draw(m).rectangle([0, 0, 600, 175], fill=(0, 0, 0))
    im = get(870)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    m = on(m, im, (round(ox), round(oy)))
    return m.convert("RGB")


def build_previews(made, splash):
    v2 = lambda i: made[i][0]                                       # noqa: E731
    v1 = lambda i: Image.open(OUT_V1 / f"{i}.png").convert("RGBA")  # noqa: E731
    small = ImageFont.truetype(str(FONTS / "NanumGothic-Bold.ttf"), 12)
    head = ImageFont.truetype(str(FONTS / "NanumGothic-ExtraBold.ttf"), 15)
    W = 1240

    def titled(im, text):
        t = Image.new("RGB", (im.width, im.height + 22), (255, 255, 255))
        t.paste(im.convert("RGB"), (0, 22))
        ImageDraw.Draw(t).text((2, 3), text, font=head, fill=(20, 20, 20))
        return t

    def row(ims, gap=20):
        h = max(i.height for i in ims)
        r = Image.new("RGB", (W, h), (255, 255, 255))
        x = 0
        for i in ims:
            r.paste(i, (x, 0))
            x += i.width + gap
        return r

    blocks = []
    v1_splash = Image.open(OUT_V1 / "splash_600x400.png").convert("RGB")
    blocks.append(row([titled(loader_mock(splash), "(1) v2 splash + the game's own loader line and bar"),
                       titled(splash.convert("RGB"), "v2 splash alone (intro fade)")]))
    blocks.append(row([titled(title_mock(v2), "(2) v2 title mock (08_t8; old art un-composited, 4399 area inpainted)"),
                       titled(title_mock(v1), "v1 title screen mock (same method)")]))
    blocks.append(row([titled(config_mock(v2), "config page mock v2 (673 + 676 + rows x0.888)"),
                       titled(howto_mock(v2), "how-to page mock v2 (870 x1.236 on black)")]))
    blocks.append(row([titled(loader_mock(v1_splash).resize((300, 200), Image.LANCZOS), "v1 splash (0.5x)"),
                       titled(config_mock(v1).resize((300, 200), Image.LANCZOS), "v1 config (0.5x)"),
                       titled(howto_mock(v1).resize((300, 200), Image.LANCZOS), "v1 how-to (0.5x)")]))

    # label comparison tiles: original | v1 | v2 | v2 in context
    title_bg = Image.open(IMG / "553.jpg").convert("RGBA")
    cfg_bg = Image.open(IMG / "673.jpg").convert("RGBA")
    pos = {i: (x, y) for i, x, y in CFG_ROWS}
    order = [586, 588, 592, 595, 598, 601, 604, 607, 610, 613, 676, 710, 713, 716, 719, 724, 660,
             678, 683, 685, 694, 687, 689, 692, 696, 870]

    def context(i):
        im = v2(i)
        w, h = im.size
        if i in MENU_IDS:   # tinted, on the light carousel slot and on a dark patch
            light = on(title_bg.crop((243, 310, 243 + w, 310 + h)), tint_menu(im))
            dark = on(Image.new("RGBA", (w, h), (52, 52, 54, 255)), tint_menu(im))
            t = Image.new("RGBA", (w, 2 * h + 2), (255, 255, 255, 255))
            t.paste(light, (0, 0))
            t.paste(dark, (0, h + 2))
            return t
        if i in (586, 588):
            x, y = TITLE_POS[i]
            return on(title_bg.crop((x, y, x + w, y + h)), im)
        if i == 870:
            return on(Image.new("RGBA", (w, h), (0, 0, 0, 255)), im)
        x, y = pos.get(i, (18, 10) if i == 676 else (294.75, 185.7))
        return on(cfg_bg.crop((round(x), round(y), round(x) + w, round(y) + h)), im)

    def tile(i, scale):
        ims = [Image.open(IMG / f"{i}.png").convert("RGBA"), v1(i), v2(i)]
        ims = [on(checker(im.width, im.height), im) for im in ims] + [context(i)]
        if i == 870:   # wide canvas: show the band that holds the lettering
            ims = [im.crop((16, 30, 320, 112)) for im in ims]
        if scale != 1:
            ims = [im.resize((im.width * scale, im.height * scale), Image.NEAREST) for im in ims]
        gap = 4
        tw = sum(im.width for im in ims) + gap * 3
        th = max(im.height for im in ims) + 16
        t = Image.new("RGB", (tw, th), (255, 255, 255))
        x = 0
        for im in ims:
            t.paste(im.convert("RGB"), (x, 16))
            x += im.width + gap
        ImageDraw.Draw(t).text((1, 1), f"{i}  {made[i][1]}   [orig | v1 | v2 | v2 in game]", font=small,
                               fill=(30, 30, 30))
        return t

    def flow(tiles, width, gap=12):
        x = y = rowh = 0
        placed = []
        for t in tiles:
            if x and x + t.width > width:
                x, y, rowh = 0, y + rowh + gap, 0
            placed.append((x, y))
            x += t.width + gap
            rowh = max(rowh, t.height)
        sheet = Image.new("RGB", (width, y + rowh), (255, 255, 255))
        for t, p in zip(tiles, placed):
            sheet.paste(t, p)
        return sheet

    hdr = Image.new("RGB", (W, 24), (255, 255, 255))
    ImageDraw.Draw(hdr).text((0, 4), "(3) every label: original | v1 | v2 (checker) | v2 as the game shows it "
                                     "(menu labels tinted to (255,G,255))", font=head, fill=(20, 20, 20))
    blocks.append(hdr)
    blocks.append(flow([tile(i, 1) for i in order], W))
    total = sum(b.height for b in blocks) + 16 * len(blocks)
    sheet = Image.new("RGB", (W, total), (255, 255, 255))
    y = 0
    for b in blocks:
        sheet.paste(b, (0, y))
        y += b.height + 16
    sheet.save(OUT / "preview_ui_v2.png")
    flow([tile(i, 2) for i in order if i != 870], 1500).save(OUT / "preview_ui_v2_zoom2x.png")


if __name__ == "__main__":
    main()
