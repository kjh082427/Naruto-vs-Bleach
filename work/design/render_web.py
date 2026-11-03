#!/usr/bin/env python3
"""Self-hosted web font subsets for web/index.html (no third-party CDN).

Run:   tools/venv/bin/python work/design/render_web.py      (re-run after editing text in web/index.html)
Deps:  fontTools.

Writes web/assets/:
  hahmlet-900.woff     Hahmlet (variable) pinned to wght 900, only the glyphs of the title lockup
  gothica1-500.woff    Gothic A1 Medium, every character used on the page + printable ASCII
  gothica1-700.woff    Gothic A1 Bold, same character set
  OFL-hahmlet.txt, OFL-gothica1.txt   licences that must travel with the fonts
"""
import html
import re
import shutil
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "tools" / "fonts"
WEB = ROOT / "web"
ASSETS = WEB / "assets"


def page_text():
    src = (WEB / "index.html").read_text(encoding="utf-8")
    body = src[src.index("<body>"):]
    body = re.sub(r"<script>.*?</script>", lambda m: " ".join(re.findall(r'"([^"]*)"', m.group(0))), body, flags=re.S)
    body = re.sub(r'\b(?:aria-label|title)="([^"]*)"', r">\1<", body)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    for js in sorted(WEB.glob("*.js")):  # page scripts (netplay.js) put their own UI text on the page
        text += " " + " ".join(re.findall(r"'([^'\n]*)'", js.read_text(encoding="utf-8")))
    lockup = re.search(r'<h1 class="lockup">(.*?)</h1>', src, re.S).group(1)
    lockup = html.unescape(re.sub(r"<[^>]+>", " ", lockup))
    return text, lockup


def write_subset(font, chars, out):
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["kern", "liga", "ccmp", "locl", "mark", "mkmk"]
    opts.name_IDs = ["*"]          # keep copyright / licence names
    opts.notdef_outline = True
    sub = subset.Subsetter(options=opts)
    sub.populate(text="".join(sorted(set(chars))))
    sub.subset(font)
    font.flavor = "woff"
    font.save(str(out))
    return out.stat().st_size


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    text, lockup = page_text()
    ascii_set = "".join(chr(c) for c in range(0x20, 0x7F))
    ui_chars = set(text) | set(ascii_set) | {" ", "–", "—", "…"}
    ui_chars = {c for c in ui_chars if c.isprintable()}

    hah = instancer.instantiateVariableFont(TTFont(str(FONTS / "Hahmlet-VariableFont_wght.ttf")), {"wght": 900})
    n1 = write_subset(hah, set(lockup) | set(" "), ASSETS / "hahmlet-900.woff")
    n2 = write_subset(TTFont(str(FONTS / "GothicA1-Medium.ttf")), ui_chars, ASSETS / "gothica1-500.woff")
    n3 = write_subset(TTFont(str(FONTS / "GothicA1-Bold.ttf")), ui_chars, ASSETS / "gothica1-700.woff")
    shutil.copy(FONTS / "OFL-hahmlet.txt", ASSETS / "OFL-hahmlet.txt")
    shutil.copy(FONTS / "OFL-gothica1.txt", ASSETS / "OFL-gothica1.txt")
    hangul = sorted(c for c in ui_chars if ord(c) > 0x7F)
    print(f"hahmlet-900.woff {n1} B  ({len(set(lockup.strip()))} chars)")
    print(f"gothica1-500.woff {n2} B, gothica1-700.woff {n3} B  ({len(ui_chars)} chars, non-ASCII: {''.join(hangul)})")


if __name__ == "__main__":
    main()
