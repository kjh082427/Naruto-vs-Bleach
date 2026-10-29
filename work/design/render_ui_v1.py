#!/usr/bin/env python3
"""Render Korean UI bitmaps for Bleach vs Naruto 2.6 (Korean edition / 한글판).

Run:  tools/venv/bin/python work/design/render_ui.py
Deps: Pillow only (no numpy). Deterministic (fixed random seeds).

Outputs (work/design/out/):
  splash_600x400.png        opaque intro card, RGBA with alpha=255 (replaces the 5DPlay splash)
  splash_loading_text.png   "불러오는 중..." line for the preloader
  586.png 588.png           title logo pieces "블리치" / "나루토"
  647.png                   fully transparent (removes the publisher logo)
  <id>.png                  Korean menu labels, same pixel size as work/img/<id>.png
  preview_ui.png            originals vs replacements (1x, checkerboard) + splash
  preview_ui_zoom2x.png     same pairs at 2x for detail checks
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "work" / "img"
OUT = ROOT / "work" / "design" / "out"
FONTS = ROOT / "tools" / "fonts"
BHS = FONTS / "BlackHanSans-Regular.ttf"
DOH = FONTS / "DoHyeon-Regular.ttf"
NGB = FONTS / "NanumGothic-Bold.ttf"
NGEB = FONTS / "NanumGothic-ExtraBold.ttf"

SS = 4  # supersampling factor for text rendering

# --------------------------------------------------------------------------
# generic helpers
# --------------------------------------------------------------------------
_font_cache = {}


def font(path, size):
    key = (str(path), round(size * 100))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(path), size)
    return _font_cache[key]


def ref_height(path, ref="가"):
    """Ink height (top..bottom) of the reference glyph at size 1000, and its top above baseline."""
    l, t, r, b = font(path, 1000).getbbox(ref, anchor="ls")
    return (b - t) / 1000.0, -t / 1000.0


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_c(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def ramp(stops, v):
    """stops: [(pos, (r,g,b)), ...] sorted; v in [0,1]."""
    v = max(0.0, min(1.0, v))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if v <= p1:
            return lerp_c(c0, c1, (v - p0) / (p1 - p0) if p1 > p0 else 0)
    return stops[-1][1]


def gain(mask, g):
    return mask.point(lambda v: min(255, int(v * g + 0.5)))


def solid(size, color, alpha_mask):
    im = Image.new("RGBA", size, tuple(color) + (255,))
    im.putalpha(alpha_mask)
    return im


def mul_alpha(img, mask):
    a = ImageChops.multiply(img.getchannel("A"), mask)
    out = img.copy()
    out.putalpha(a)
    return out


def checker(w, h, s=8, c1=(204, 204, 204), c2=(153, 153, 153)):
    im = Image.new("RGBA", (w, h), c1 + (255,))
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=c2 + (255,))
    return im


# --------------------------------------------------------------------------
# text layout -> L masks
# --------------------------------------------------------------------------
class TextLayout:
    """Lays out one line of text so that the reference glyph ('가') ink spans
    exactly `cap` px starting at y=`top`, horizontally centred on `cx`.
    If the line is wider than `max_w`, it is first condensed horizontally
    (down to `min_sx`), then the font size is reduced (keeping the vertical centre)."""

    def __init__(self, W, H, text, path, cap, cx, top, tracking=0.0, max_w=None,
                 min_sx=0.85, ref="가", shear=0.0, space=1.0):
        self.W, self.H, self.text, self.path = W, H, text, path
        self.tracking, self.shear, self.space = tracking, shear, space
        hfrac, topfrac = ref_height(path, ref)
        size = cap / hfrac
        self.req_cap = cap
        while True:
            w = self._ink_width(size)
            sx = 1.0 if (max_w is None or w <= max_w) else max_w / w
            if sx >= min_sx or size < 6:
                break
            size *= 0.97
        self.size, self.sx = size, min(1.0, sx)
        self.cap = size * hfrac
        self.top = top + (cap - self.cap) / 2.0
        self.baseline = self.top + size * topfrac  # y of baseline in canvas px
        self.cx = cx
        self.ink_w = self._ink_width(size) * self.sx

    def _advances(self, f):
        xs, x = [], 0.0
        for ch in self.text:
            xs.append(x)
            adv = f.getlength(ch) * (self.space if ch == " " else 1.0)
            x += adv + self.tracking * SS
        return xs

    def _ink_width(self, size):
        f = font(self.path, size * SS)
        xs = self._advances(f)
        l0 = min(x + f.getbbox(ch, anchor="ls")[0] for x, ch in zip(xs, self.text) if ch.strip())
        r0 = max(x + f.getbbox(ch, anchor="ls")[2] for x, ch in zip(xs, self.text) if ch.strip())
        return (r0 - l0) / SS

    def mask(self, stroke=0.0):
        """L mask (W x H) of the text, optionally dilated by `stroke` px (round)."""
        f = font(self.path, self.size * SS)
        xs = self._advances(f)
        pad = int((stroke + 4) * SS)
        # draw line on a temp canvas at SS, baseline at y = pad + size*SS
        tw = int(xs[-1] + f.getlength(self.text[-1]) + 2 * pad + 4 * SS)
        th = int(self.size * SS * 1.6 + 2 * pad)
        tmp = Image.new("L", (tw, th), 0)
        d = ImageDraw.Draw(tmp)
        by = pad + self.size * SS
        for x, ch in zip(xs, self.text):
            if ch.strip():
                d.text((pad + x, by), ch, font=f, fill=255, anchor="ls",
                       stroke_width=int(round(stroke * SS)), stroke_fill=255)
        # ink extent without stroke, for centring
        l0 = min(x + f.getbbox(ch, anchor="ls")[0] for x, ch in zip(xs, self.text) if ch.strip()) + pad
        r0 = max(x + f.getbbox(ch, anchor="ls")[2] for x, ch in zip(xs, self.text) if ch.strip()) + pad
        mid_src = (l0 + r0) / 2.0
        if self.sx < 1.0:
            nw = max(1, int(round(tw * self.sx)))
            tmp = tmp.resize((nw, th), Image.LANCZOS)
            mid_src *= self.sx
        if self.shear:
            # shear around the baseline (positive = italic lean to the right)
            k = self.shear
            tmp = tmp.transform((tmp.width + int(abs(k) * th), th), Image.AFFINE,
                                (1, k, -k * by, 0, 1, 0),
                                resample=Image.BICUBIC)
        canvas = Image.new("L", (self.W * SS, self.H * SS), 0)
        ox = self.cx * SS - mid_src
        oy = self.baseline * SS - by
        canvas.paste(tmp, (int(round(ox)), int(round(oy))))
        return canvas.resize((self.W, self.H), Image.BOX)


# --------------------------------------------------------------------------
# effects
# --------------------------------------------------------------------------
def glow_from(layout, dil, blur, g, base_mask=None):
    m = layout.mask(stroke=dil) if dil else (base_mask or layout.mask())
    return gain(m.filter(ImageFilter.GaussianBlur(blur)), g)


def metal_texture(W, H, stops, seed, top=9, cap=22):
    """Brushed-metal fill with soft diagonal ('/') streaks, like the original menu labels.
    Kept mostly mid/dark so dense Hangul strokes stay readable at 1x."""
    rnd = random.Random(seed)
    p1, p2, p3, p4 = (rnd.uniform(0, 2 * math.pi) for _ in range(4))
    period = rnd.uniform(9.0, 11.0)
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        vy = (y - top) / max(1.0, cap)  # 0 top .. 1 bottom of glyphs
        band = 0.08 * math.exp(-((vy - 0.40) / 0.28) ** 2)  # soft light band upper-middle
        shade = -0.08 * max(0.0, vy - 0.65) / 0.35  # darker toward the bottom
        for x in range(W):
            u = 0.85 * x + y  # '/' streak coordinate
            wob = 1.3 * math.sin(2 * math.pi * (x - y) / 53.0 + p2)
            s = math.sin(2 * math.pi * u / period + p1 + wob)
            streak = max(0.0, s) ** 2 * (0.5 + 0.5 * math.sin(x / 19.0 + p3))
            low = 0.06 * math.sin(2 * math.pi * u / 29.0 + p4)
            v = 0.33 + low + 0.32 * streak + band + shade + rnd.uniform(-0.02, 0.02)
            px[x, y] = ramp(stops, v)
    return im


BLUE = [(0.0, (32, 48, 60)), (0.30, (68, 92, 108)), (0.50, (94, 120, 138)),
        (0.70, (138, 164, 180)), (1.0, (214, 232, 242))]
OLIVE = [(0.0, (60, 62, 32)), (0.30, (100, 106, 48)), (0.50, (128, 136, 60)),
         (0.70, (172, 182, 90)), (1.0, (224, 230, 156))]
GLOW_BLUE = (250, 253, 255)
GLOW_OLIVE = (255, 255, 240)


LABEL_CAP, LABEL_TOP = 23, 8.5  # Hangul ink box (originals: Latin caps y 9..30)


def render_label(i, text, kind):
    W, H = Image.open(IMG / f"{i}.png").size
    stops, gcol = (BLUE, GLOW_BLUE) if kind == "blue" else (OLIVE, GLOW_OLIVE)
    # originals: 4px transparent pad + 5px glow ramp; we allow 3px (1px on narrow canvases)
    margin = 8 if W >= 100 else 6
    lay = TextLayout(W, H, text, BHS, cap=LABEL_CAP, cx=W / 2.0, top=LABEL_TOP,
                     max_w=W - 2 * margin, min_sx=0.84, space=0.8)
    m = lay.mask()
    glow = glow_from(lay, 2, 1.5, 1.0)
    out = solid((W, H), gcol, glow)
    fill = metal_texture(W, H, stops, seed=i, top=LABEL_TOP, cap=LABEL_CAP)
    # darker 1px inner rim so the glyph edge separates from the white glow
    rim = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(3)))
    fill = Image.composite(fill.point(lambda v: int(v * 0.62)), fill, gain(rim, 0.8))
    fill = fill.convert("RGBA")
    fill.putalpha(m)
    out = Image.alpha_composite(out, fill)
    return out, lay


def render_logo(i, text, color, dil, blur, g, tracking):
    W, H = Image.open(IMG / f"{i}.png").size
    lay = TextLayout(W, H, text, BHS, cap=45, cx=W / 2.0, top=13.5, tracking=tracking, max_w=W - 28)
    m = lay.mask()
    glow = glow_from(lay, dil, blur, g)
    out = solid((W, H), (255, 255, 255), glow)
    # very subtle vertical tone so the flat colour is not dead (originals are flat; keep it minimal)
    fill = Image.new("RGBA", (W, H))
    fd = ImageDraw.Draw(fill)
    for y in range(H):
        t = (y - lay.top) / max(1.0, lay.cap)
        c = lerp_c(color[0], color[1], max(0.0, min(1.0, t)))
        fd.line([(0, y), (W, y)], fill=c + (255,))
    fill.putalpha(m)
    return Image.alpha_composite(out, fill), lay


def render_config_header(i, text):
    """676: hollow outlined letters (dark contour line, white body) + white glow."""
    W, H = Image.open(IMG / f"{i}.png").size
    lay = TextLayout(W, H, text, NGEB, cap=38, cx=W / 2.0, top=14, tracking=34, max_w=W - 30)
    body = lay.mask(stroke=2.6)
    glow = gain(lay.mask(stroke=3.2).filter(ImageFilter.GaussianBlur(2.6)), 1.25)
    outer = lay.mask(stroke=1.25)
    inner_src = lay.mask().filter(ImageFilter.MinFilter(3))
    contour = ImageChops.subtract(outer, inner_src).filter(ImageFilter.GaussianBlur(0.45))
    contour = gain(contour, 1.05)
    out = solid((W, H), (255, 255, 255), glow)
    out = Image.alpha_composite(out, solid((W, H), (250, 250, 250), body))
    # light grey sheen inside the strokes (like the original's grey bands)
    sheen = gain(lay.mask().filter(ImageFilter.GaussianBlur(1.2)), 0.35)
    out = Image.alpha_composite(out, solid((W, H), (120, 120, 120), ImageChops.multiply(sheen, body)))
    out = Image.alpha_composite(out, solid((W, H), (12, 12, 12), contour))
    return out, lay


def render_howto(i, text):
    """870: thin rounded cyan->green gradient text, white rim, faint reflection."""
    W, H = Image.open(IMG / f"{i}.png").size
    # original text ink: x 31..306, y 55..85 (incl. white rim); keep its centre
    cx, cy = (31 + 306) / 2.0, (55 + 85) / 2.0
    cap = 27
    lay = TextLayout(W, H, text, DOH, cap=cap, cx=cx, top=cy - cap / 2.0, tracking=8)
    m = lay.mask()
    rim = lay.mask(stroke=1.4)
    glow = gain(lay.mask(stroke=1.8).filter(ImageFilter.GaussianBlur(1.3)), 0.75)
    stops = [(0.0, (60, 205, 225)), (0.35, (18, 172, 160)), (0.70, (28, 124, 80)), (1.0, (52, 84, 26))]
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=ramp(stops, (y - lay.top) / lay.cap) + (255,))
    grad.putalpha(m)
    text_layer = solid((W, H), (255, 255, 250), glow)
    text_layer = Image.alpha_composite(text_layer, solid((W, H), (255, 255, 248), rim))
    text_layer = Image.alpha_composite(text_layer, grad)
    # faint reflection below (original: alpha <= ~22, fading over ~28 px)
    bottom = int(math.ceil(lay.top + lay.cap)) + 2
    refl = text_layer.crop((0, bottom - 34, W, bottom)).transpose(Image.FLIP_TOP_BOTTOM)
    fade = Image.new("L", refl.size, 0)
    fdd = ImageDraw.Draw(fade)
    for y in range(refl.height):
        fdd.line([(0, y), (W, y)], fill=int(24 * max(0.0, 1 - y / refl.height) ** 1.3))
    refl = mul_alpha(refl, fade)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(refl, (0, bottom + 2))
    out = Image.alpha_composite(out, text_layer)
    return out, lay


# --------------------------------------------------------------------------
# splash
# --------------------------------------------------------------------------
def brush_stroke(W, H, x0, x1, yc, hh, seed, direction=1, angle=0.0, n=110, arc=-5.0,
                 dry_from=0.55, taper=0.30, S=2):
    """Dry ink-brush stroke. Returns (alpha L, shade L) at WxH.
    The brush is pressed at the start (blunt round head) and runs dry toward the end
    (split bristles, gaps). direction=+1 paints left->right, -1 right->left."""
    rnd = random.Random(seed)
    L = x1 - x0
    cx = (x0 + x1) / 2.0
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    a_im = Image.new("L", (W * S, H * S), 0)
    s_im = Image.new("L", (W * S, H * S), 0)
    ad, sd = ImageDraw.Draw(a_im), ImageDraw.Draw(s_im)
    ph = rnd.uniform(0, 2 * math.pi)

    def to_xy(u, v):
        xl = x0 + u if direction == 1 else x1 - u
        dx, dy = xl - cx, v
        return ((cx + dx * ca - dy * sa) * S, (yc + dx * sa + dy * ca) * S)

    for i in range(n):
        f = (i + 0.5) / n
        v0 = (f - 0.5) * 2 * hh
        edge = abs(f - 0.5) * 2
        u_start = hh * 0.85 * (1 - math.sqrt(max(0.0, 1 - edge ** 2))) + rnd.uniform(-2, 4)
        u_end = L * (1 - 0.30 * edge ** 2) - rnd.uniform(0, L * 0.22) * (0.25 + edge)
        width = max(1.0, 2 * hh / n * rnd.uniform(1.6, 2.6)) * S
        val = rnd.randint(170, 255)
        bph = rnd.uniform(0, 2 * math.pi)
        u = u_start
        while u < u_end:
            prog = u / L
            if prog < dry_from:
                seg = rnd.uniform(L * 0.10, L * 0.6)
            else:
                seg = rnd.uniform(L * 0.015, L * 0.10)
            ue = min(u_end, u + seg)
            steps = max(2, int((ue - u) / 5))
            pts = []
            for k in range(steps + 1):
                uu = u + (ue - u) * k / steps
                t = uu / L
                vv = v0 * (1 - taper * t ** 2) + arc * 4 * t * (1 - t)
                vv += 2.2 * math.sin(uu / 41.0 + ph) + 0.8 * math.sin(uu / 13.0 + bph) * edge
                pts.append(to_xy(uu, vv))
            ad.line(pts, fill=255 if val > 200 else 235, width=int(width), joint="curve")
            sd.line(pts, fill=val, width=int(width), joint="curve")
            if prog < dry_from:
                gap = rnd.uniform(0, 1.2)
            else:
                gap = rnd.uniform(1, L * 0.045) * (0.3 + edge + (prog - dry_from))
            u = ue + gap
    a_im = a_im.filter(ImageFilter.GaussianBlur(0.5 * S)).resize((W, H), Image.BOX)
    s_im = s_im.filter(ImageFilter.GaussianBlur(0.7 * S)).resize((W, H), Image.BOX)
    return a_im, s_im


def splatter_layer(W, H, seed, spots, S=2):
    """spots: list of (cx, cy, spread_x, spread_y, n, color, rmax)."""
    rnd = random.Random(seed)
    lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for cx, cy, sx, sy, n, col, rmax in spots:
        for _ in range(n):
            r = (rnd.random() ** 3) * rmax + 0.5
            x = cx + rnd.gauss(0, sx)
            y = cy + rnd.gauss(0, sy)
            a = rnd.randint(150, 255)
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=col + (a,))
            if r > 2.2 and rnd.random() < 0.5:  # satellite droplet / drip
                ang = rnd.uniform(0, 2 * math.pi)
                dd = r * rnd.uniform(1.4, 2.6)
                r2 = r * rnd.uniform(0.25, 0.5)
                x2, y2 = x + dd * math.cos(ang), y + dd * math.sin(ang)
                d.ellipse([(x2 - r2) * S, (y2 - r2) * S, (x2 + r2) * S, (y2 + r2) * S], fill=col + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(0.4 * S))
    return lay.resize((W, H), Image.BOX)


def focus_lines(W, H, cx, cy, seed, n=260, rx=250, ry=118, color=(255, 255, 255), amax=34, S=2):
    """Manga focus/speed lines converging on (cx, cy), leaving an elliptical clear core."""
    rnd = random.Random(seed)
    lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    R = math.hypot(W, H)
    for _ in range(n):
        th = rnd.uniform(0, 2 * math.pi)
        k = rnd.uniform(0.95, 1.45)
        x_in, y_in = cx + rx * k * math.cos(th), cy + ry * k * math.sin(th)
        x_out, y_out = cx + R * math.cos(th), cy + R * math.sin(th)
        w = rnd.uniform(0.004, 0.018)
        p1 = (cx + R * math.cos(th - w), cy + R * math.sin(th - w))
        p2 = (cx + R * math.cos(th + w), cy + R * math.sin(th + w))
        a = rnd.randint(int(amax * 0.3), amax)
        d.polygon([(x_in * S, y_in * S), (p1[0] * S, p1[1] * S), (p2[0] * S, p2[1] * S)], fill=color + (a,))
    return lay.resize((W, H), Image.BOX)


def radial_glow(W, H, cx, cy, rx, ry, color, alpha, blur):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    return solid((W, H), color, m)


def colored_brush(W, H, alpha, shade, dark, light):
    """Colour a brush stroke by its bristle shade map."""
    lut_r = [int(lerp(dark[0], light[0], v / 255)) for v in range(256)]
    lut_g = [int(lerp(dark[1], light[1], v / 255)) for v in range(256)]
    lut_b = [int(lerp(dark[2], light[2], v / 255)) for v in range(256)]
    rgb = Image.merge("RGB", (shade.point(lut_r), shade.point(lut_g), shade.point(lut_b)))
    out = rgb.convert("RGBA")
    out.putalpha(gain(alpha, 1.1))
    return out


def text_effect(W, H, lay, fill, outline=None, outline_w=0.0, shadow=None, shadow_off=(0, 0),
                shadow_w=0.0, fill_grad=None):
    """Compose filled text with optional outline and hard offset shadow."""
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow is not None:
        sm = lay.mask(stroke=shadow_w)
        sh = Image.new("L", (W, H), 0)
        sh.paste(sm, shadow_off)
        out = Image.alpha_composite(out, solid((W, H), shadow, sh))
    if outline is not None:
        out = Image.alpha_composite(out, solid((W, H), outline, lay.mask(stroke=outline_w)))
    m = lay.mask()
    if fill_grad:
        g = Image.new("RGBA", (W, H))
        gd = ImageDraw.Draw(g)
        for y in range(H):
            gd.line([(0, y), (W, y)], fill=ramp(fill_grad, (y - lay.top) / lay.cap) + (255,))
        g.putalpha(m)
        out = Image.alpha_composite(out, g)
    else:
        out = Image.alpha_composite(out, solid((W, H), fill, m))
    return out


def render_splash():
    W, H = 600, 400
    TY = 180  # title line vertical centre
    # 1. background: near-black vertical gradient
    bg = Image.new("RGBA", (W, H))
    bd = ImageDraw.Draw(bg)
    for y in range(H):
        bd.line([(0, y), (W, y)], fill=lerp_c((20, 18, 22), (6, 6, 8), y / H) + (255,))
    # warm glows: Bleach red on the left, Naruto orange on the right
    bg = Image.alpha_composite(bg, radial_glow(W, H, 170, TY, 190, 95, (150, 18, 18), 110, 55))
    bg = Image.alpha_composite(bg, radial_glow(W, H, 440, TY, 190, 95, (190, 80, 0), 105, 55))
    # 2. speed / focus lines
    bg = Image.alpha_composite(bg, focus_lines(W, H, 300, TY, seed=7, n=300, rx=250, ry=112, amax=30))
    # faint horizontal speed streaks
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    rnd = random.Random(11)
    for _ in range(70):
        y = rnd.uniform(90, 290)
        if abs(y - TY) < 58:
            continue
        x0 = rnd.uniform(-50, 560)
        ln = rnd.uniform(40, 220)
        sd.line([(x0, y), (x0 + ln, y)], fill=(255, 255, 255, rnd.randint(10, 32)), width=1)
    bg = Image.alpha_composite(bg, st)

    # faint background ink sweeps (top-right, bottom-left; keeps the loading-line area clear)
    for (x0, x1, yc, h2, sd_, dr, ang) in ((410, 700, 52, 15, 51, -1, -16.0), (-100, 190, 372, 15, 52, 1, -16.0)):
        fa, fs = brush_stroke(W, H, x0, x1, yc, h2, seed=sd_, direction=dr, angle=ang, n=60, arc=2,
                              dry_from=0.35)
        bg = Image.alpha_composite(bg, colored_brush(W, H, gain(fa, 0.16), fs, (90, 90, 90), (235, 235, 235)))

    # 3. ink brush strokes behind the title: white (Bleach) from the left, orange (Naruto) from the right
    hh = 43
    wa, ws = brush_stroke(W, H, 22, 330, TY + 2, hh, seed=21, direction=1, angle=-2.5, arc=-4)
    oa, os_ = brush_stroke(W, H, 270, 580, TY + 2, hh, seed=34, direction=-1, angle=-2.5, arc=-4)
    # dark under-shadow to lift the strokes off the background
    for a in (wa, oa):
        sh = Image.new("L", (W, H), 0)
        sh.paste(a.filter(ImageFilter.GaussianBlur(4)), (3, 5))
        bg = Image.alpha_composite(bg, solid((W, H), (0, 0, 0), gain(sh, 0.8)))
    bg = Image.alpha_composite(bg, colored_brush(W, H, oa, os_, (196, 72, 0), (255, 150, 20)))
    bg = Image.alpha_composite(bg, colored_brush(W, H, wa, ws, (150, 146, 140), (250, 248, 242)))
    # ink splatter around the stroke heads/tails
    bg = Image.alpha_composite(bg, splatter_layer(W, H, 5, [
        (40, TY - 40, 22, 14, 26, (240, 238, 232), 3.2),
        (325, TY + 40, 18, 10, 14, (240, 238, 232), 2.4),
        (565, TY + 44, 20, 14, 26, (255, 140, 20), 3.2),
        (275, TY - 42, 18, 10, 14, (255, 140, 20), 2.4),
        (300, TY + 62, 70, 10, 18, (200, 24, 24), 2.4),
    ]))

    # 4. title text
    title_cap = 48
    bleach = TextLayout(W, H, "블리치", BHS, cap=title_cap, cx=160, top=TY - title_cap / 2.0, tracking=3)
    naruto = TextLayout(W, H, "나루토", BHS, cap=title_cap, cx=440, top=TY - title_cap / 2.0, tracking=3)
    img = Image.alpha_composite(bg, text_effect(W, H, bleach, (14, 12, 14), shadow=(205, 22, 26),
                                                shadow_off=(3, 3)))
    img = Image.alpha_composite(img, text_effect(W, H, naruto, (14, 12, 14), shadow=(120, 32, 0),
                                                 shadow_off=(3, 3)))
    # VS badge: black disc with red ring, sheared red "VS" with white + black outline
    badge = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(badge).ellipse([(300 - 34) * 2, (TY - 34) * 2, (300 + 34) * 2, (TY + 34) * 2], fill=255)
    badge = badge.resize((W, H), Image.BOX)
    ring = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(ring).ellipse([(300 - 34) * 2, (TY - 34) * 2, (300 + 34) * 2, (TY + 34) * 2],
                                 outline=255, width=6)
    ring = ring.resize((W, H), Image.BOX)
    img = Image.alpha_composite(img, solid((W, H), (0, 0, 0), gain(badge.filter(ImageFilter.GaussianBlur(6)), 0.9)))
    img = Image.alpha_composite(img, solid((W, H), (12, 10, 12), badge))
    img = Image.alpha_composite(img, solid((W, H), (210, 24, 28), ring))
    vs = TextLayout(W, H, "VS", BHS, cap=34, cx=301, top=TY - 17, tracking=0, shear=0.18)
    img = Image.alpha_composite(img, text_effect(W, H, vs, None, outline=(255, 255, 255), outline_w=2.2,
                                                 fill_grad=[(0, (255, 70, 60)), (1, (190, 10, 18))]))

    # 5. subtitle "2.6 한글판": white "2.6" + red seal box with "한글판"
    sub_cap = 22
    SY = TY + 72
    ver = TextLayout(W, H, "2.6", BHS, cap=sub_cap, cx=0, top=SY, tracking=1)
    han = TextLayout(W, H, "한글판", BHS, cap=sub_cap, cx=0, top=SY, tracking=2)
    gap, padx = 14, 10
    total = ver.ink_w + gap + han.ink_w + 2 * padx
    x_left = 300 - total / 2.0
    ver.cx = x_left + ver.ink_w / 2.0
    han.cx = x_left + ver.ink_w + gap + padx + han.ink_w / 2.0
    box = [x_left + ver.ink_w + gap, SY - 6, x_left + total, SY + sub_cap + 6]
    seal = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(seal).rounded_rectangle([v * 2 for v in box], radius=6, fill=255)
    seal = seal.resize((W, H), Image.BOX)
    img = Image.alpha_composite(img, solid((W, H), (196, 20, 26), seal))
    img = Image.alpha_composite(img, text_effect(W, H, ver, (245, 242, 236)))
    img = Image.alpha_composite(img, text_effect(W, H, han, (255, 250, 244)))

    # 6. "REA PROJECT" small latin label at the top centre, flanked by thin rules
    rea = TextLayout(W, H, "REA PROJECT", NGEB, cap=12, cx=300, top=40, tracking=4.5, ref="H")
    img = Image.alpha_composite(img, text_effect(W, H, rea, (226, 222, 216)))
    rd = ImageDraw.Draw(img)
    half = rea.ink_w / 2.0
    yline = 40 + 6
    rd.line([(300 - half - 54, yline), (300 - half - 14, yline)], fill=(205, 24, 28, 255), width=2)
    rd.line([(300 + half + 14, yline), (300 + half + 54, yline)], fill=(255, 140, 20, 255), width=2)

    # 7. soft vignette
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).rectangle([0, 0, W, H], outline=255, width=40)
    vig = gain(vig.filter(ImageFilter.GaussianBlur(40)), 0.55)
    img = Image.alpha_composite(img, solid((W, H), (0, 0, 0), vig))
    return img.convert("RGB").convert("RGBA")


def render_loading_text():
    W, H = 160, 24
    lay = TextLayout(W, H, "불러오는 중...", NGEB, cap=12.5, cx=W / 2.0, top=5.75, tracking=0.6, max_w=W - 10)
    glow = gain(lay.mask(stroke=1.5).filter(ImageFilter.GaussianBlur(1.5)), 1.1)
    out = solid((W, H), (210, 30, 34), gain(glow, 0.85))
    out = Image.alpha_composite(out, solid((W, H), (24, 8, 8), lay.mask(stroke=1.1)))
    out = Image.alpha_composite(out, solid((W, H), (252, 248, 240), lay.mask()))
    return out, lay


# --------------------------------------------------------------------------
# job list
# --------------------------------------------------------------------------
LABELS = [
    # id, original word, Korean, style
    (592, "Nornal", "일반 대전", "blue"),
    (595, "Vs Com", "VS 컴퓨터", "blue"),
    (598, "Vs Human", "VS 사람", "blue"),
    (601, "Training", "연습 모드", "blue"),
    (604, "Config", "설정", "blue"),
    (607, "Information", "정보", "blue"),
    (610, "More Games", "더 많은 게임", "blue"),
    (613, "Exit", "나가기", "blue"),
    (660, "Exit", "나가기", "blue"),
    (710, "Key Config", "키 설정", "blue"),
    (713, "Com Level", "난이도", "blue"),
    (716, "Quality", "화질", "blue"),
    (719, "Life", "체력", "blue"),
    (724, "Time", "시간", "blue"),
    (678, "Very Easy", "매우 쉬움", "olive"),
    (683, "Easy", "쉬움", "olive"),
    (685, "Medium", "보통", "olive"),
    (694, "Medium", "보통", "olive"),
    (687, "Hard", "어려움", "olive"),
    (689, "Very Hard", "매우 어려움", "olive"),
    (692, "High", "높음", "olive"),
    (696, "Low", "낮음", "olive"),
]


def check_size(i, im):
    W, H = Image.open(IMG / f"{i}.png").size
    assert im.size == (W, H), (i, im.size, (W, H))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []  # (id or name, orig path or None, out image, note)

    for i, en, ko, kind in LABELS:
        im, lay = render_label(i, ko, kind)
        check_size(i, im)
        im.save(OUT / f"{i}.png")
        note = f"{en}->{ko}" + (f" (condensed x{lay.sx:.2f})" if lay.sx < 0.999 else "") + \
               (f" (cap {lay.cap:.1f}px)" if abs(lay.cap - LABEL_CAP) > 0.3 else "")
        results.append((i, ko, im, note))

    im, lay = render_config_header(676, "설정")
    check_size(676, im)
    im.save(OUT / "676.png")
    results.append((676, "설정", im, "CONFIG->설정"))

    im, lay = render_howto(870, "조작 방법")
    check_size(870, im)
    im.save(OUT / "870.png")
    results.append((870, "조작 방법", im, "HOW TO PLAY->조작 방법"))

    im, lay = render_logo(586, "블리치", ((14, 14, 14), (0, 0, 0)), 1, 5.5, 1.5, tracking=9)
    check_size(586, im)
    im.save(OUT / "586.png")
    results.append((586, "블리치", im, "BLEACH->블리치"))

    im, lay = render_logo(588, "나루토", ((184, 10, 14), (150, 0, 4)), 2, 5.5, 1.2, tracking=9)
    check_size(588, im)
    im.save(OUT / "588.png")
    results.append((588, "나루토", im, "NARUTO->나루토"))

    im = Image.new("RGBA", Image.open(IMG / "647.png").size, (0, 0, 0, 0))
    im.save(OUT / "647.png")
    results.append((647, "(transparent)", im, "4399 logo removed"))

    splash = render_splash()
    splash.save(OUT / "splash_600x400.png")  # RGBA, alpha 255 everywhere (opaque)
    loading, _ = render_loading_text()
    loading.save(OUT / "splash_loading_text.png")

    build_previews(results, splash, loading)
    for r in results:
        print(f"{r[0]}: {r[2].size[0]}x{r[2].size[1]}  {r[3]}")
    print("splash_600x400.png 600x400; splash_loading_text.png", loading.size)


# --------------------------------------------------------------------------
# previews
# --------------------------------------------------------------------------
def _label(d, xy, text, fnt, fill=(20, 20, 20)):
    d.text(xy, text, font=fnt, fill=fill)


def build_previews(results, splash, loading):
    small = font(NGB, 12)
    head = font(NGEB, 15)
    order = [586, 588, 647, 676, 870, 592, 595, 598, 601, 604, 607, 610, 613, 660,
             710, 713, 716, 719, 724, 678, 683, 685, 694, 687, 689, 692, 696]
    by_id = {r[0]: r for r in results}

    def pair_tile(i, scale):
        o = Image.open(IMG / f"{i}.png").convert("RGBA")
        n = by_id[i][2]
        if scale != 1:
            o = o.resize((o.width * scale, o.height * scale), Image.NEAREST)
            n = n.resize((n.width * scale, n.height * scale), Image.NEAREST)
        gap = 8
        w = o.width * 2 + gap
        t = Image.new("RGBA", (w, o.height + 18), (255, 255, 255, 255))
        for k, im in enumerate((o, n)):
            bg = checker(im.width, im.height, 8 * scale if scale > 1 else 6)
            bg.alpha_composite(im)
            t.paste(bg, (k * (o.width + gap), 18))
        d = ImageDraw.Draw(t)
        _label(d, (2, 2), f"{i}  {by_id[i][3]}", small)
        return t

    def flow(tiles, W, gap=10):
        x = y = rowh = 0
        pos = []
        for t in tiles:
            if x and x + t.width > W:
                x, y, rowh = 0, y + rowh + gap, 0
            pos.append((x, y))
            x += t.width + gap
            rowh = max(rowh, t.height)
        sheet = Image.new("RGBA", (W, y + rowh), (255, 255, 255, 255))
        for t, p in zip(tiles, pos):
            sheet.paste(t, p)
        return sheet

    # --- 1x sheet: splash (+ loading mock) on top, then all pairs
    W = 1240
    top = Image.new("RGBA", (W, 400 + 30), (255, 255, 255, 255))
    d = ImageDraw.Draw(top)
    _label(d, (0, 4), "splash_600x400.png (with splash_loading_text.png mocked at the old loading-line position)", head)
    mock = splash.copy()
    mock.alpha_composite(loading, (300 - loading.width // 2, 331 - loading.height // 2))
    top.paste(mock, (0, 26))
    lt = checker(loading.width * 2, loading.height * 2, 8)
    lt.alpha_composite(loading.resize((loading.width * 2, loading.height * 2), Image.NEAREST))
    _label(d, (620, 30), "splash_loading_text.png (2x, checker)", small)
    top.paste(lt, (620, 48))
    on_white = Image.new("RGBA", loading.size, (255, 255, 255, 255))
    on_white.alpha_composite(loading)
    _label(d, (620, 108), "on white (1x)", small)
    top.paste(on_white, (620, 124))
    orig_shot = Image.open(ROOT / "work/shots/intro/00_scenario_start.png").convert("RGBA").resize((300, 200))
    _label(d, (620, 170), "old splash (0.5x)", small)
    top.paste(orig_shot, (620, 188))

    pairs1 = flow([pair_tile(i, 1) for i in order], W)
    hdr = Image.new("RGBA", (W, 26), (255, 255, 255, 255))
    _label(ImageDraw.Draw(hdr), (0, 4), "original (left) vs replacement (right), 1x on checkerboard", head)
    sheet = Image.new("RGBA", (W, top.height + hdr.height + pairs1.height + 10), (255, 255, 255, 255))
    sheet.paste(top, (0, 0))
    sheet.paste(hdr, (0, top.height + 4))
    sheet.paste(pairs1, (0, top.height + 4 + hdr.height))
    sheet.convert("RGB").save(OUT / "preview_ui.png")

    # --- 2x detail sheet (labels + logos)
    pairs2 = flow([pair_tile(i, 2) for i in order if i not in (647,)], 1500)
    pairs2.convert("RGB").save(OUT / "preview_ui_zoom2x.png")


if __name__ == "__main__":
    main()
