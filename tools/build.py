"""Build the Korean edition into dist/ from the pristine game/ tree.

usage: tools/venv/bin/python tools/build.py

Inputs
  game/                               pristine restored game (never modified)
  work/l10n/game_strings.json         zh->ko for script string literals (bvn-localizer)
  work/l10n/game_texts.json           {text tag id: [ko per record]} (bvn-localizer)
  work/design/out/*.png               UI bitmaps named by character id + splash_600x400.png (game-ui-designer)
  web/                                page template + assets copied into dist/ (index.html needs __RUFFLE_CONFIG__)
  tools/ruffle_config.json            Ruffle player config injected into index.html
Outputs
  dist/  (game.swf, fonts, index.html, ...)
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from swfpatch import Swf, Tag, bits_lossless2, parse_place_object2  # noqa: E402
from swftext import (bitmap_rect_shape, build_edit_text, define_text_to_sprite, empty_shape, parse_edit_text,  # noqa: E402
                     place_with_alpha)

FFDEC = ['java', '-jar', os.path.join(ROOT, 'tools/ffdec/ffdec.jar')]
GAME, DIST, WORK = (os.path.join(ROOT, p) for p in ('game', 'dist', 'work'))
BUILD = os.path.join(WORK, 'build')
SCRIPTS = os.path.join(ROOT, 'analysis/game/scripts/scripts')
CJK = re.compile(r'[㐀-鿿　-〿＀-￯]')

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0 or 'SEVERE' in r.stderr:
        raise RuntimeError(f'{cmd[:6]} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}')
    return r.stdout


def ffdec_replace(src, dst, pairs):
    """pairs: [(id_or_script, file, format_or_None)] -> one FFDec -replace run via argsfile."""
    args = os.path.join(BUILD, 'replace_args.txt')
    with open(args, 'w') as f:
        for cid, path, fmt in pairs:
            f.write(f'{cid}\n{path}\n' + (f'{fmt}\n' if fmt else ''))
    run(FFDEC + ['-replace', src, dst, args])


def ffdec_import_scripts(src, dst, folder):
    run(FFDEC + ['-importScript', src, dst, folder])


# --- dist skeleton -----------------------------------------------------------------------------------------


def prepare_dist():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(GAME, DIST)
    os.makedirs(os.path.join(DIST, 'fonts'), exist_ok=True)
    for f in ('NanumGothic-Regular.ttf', 'NanumGothic-Bold.ttf'):
        shutil.copy(os.path.join(ROOT, 'tools/fonts', f), os.path.join(DIST, 'fonts', f))
    # page template (web/, owned by the UI designer) + Ruffle player config (tools/ruffle_config.json)
    for name in os.listdir(os.path.join(ROOT, 'web')):
        src = os.path.join(ROOT, 'web', name)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(DIST, name))
    config = json.dumps(json.load(open(os.path.join(ROOT, 'tools/ruffle_config.json'))), ensure_ascii=False)
    html = open(os.path.join(DIST, 'index.html'), encoding='utf-8').read()
    assert '__RUFFLE_CONFIG__' in html, 'web/index.html must contain the __RUFFLE_CONFIG__ placeholder'
    open(os.path.join(DIST, 'index.html'), 'w', encoding='utf-8').write(html.replace('__RUFFLE_CONFIG__', config))


# --- game.swf -----------------------------------------------------------------------------------------------


def load_json(rel, default):
    p = os.path.join(WORK, rel)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default


HTML_SEGMENTS = {  # CJK runs inside HTML EditTexts whose plain export does not match verbatim (tag 2006)
    '部分角色跳跃中可': '일부 캐릭터 공중 가능', '跳跃中可': '공중 가능', '超必杀': '초필살', '必杀': '필살',
    '斩击': '베기', '技能': '기술', '默认': '기본', '斩': '베기', '技': '기술',
}


TEXT_OVERRIDES = {  # fixed-width fields where the dictionary wording overflows (checked in-game)
    '2024': ['다른 게임'], '2025': ['다른 게임'], '653': ['다른 게임'], '654': ['다른 게임'],
}
TEXT_COLORS = {528: (255, 240, 225, 255)}  # loader text now sits on the dark splash
CREDIT_HANDLES = {  # staff handles in the credits (tag 839) -> Korean Sino readings, so no CJK glyphs are needed
    '数字化流天': '수자화류천', '临界幻想': '임계환상', '赤炎': '적염', '小海': '소해', '主流': '주류',
    '灰原': '하이바라', '银': '긴', '剑': '검', '影': '영',
}


def replace_cjk_segments(text):
    for zh in sorted(HTML_SEGMENTS, key=len, reverse=True):
        text = text.replace(zh, HTML_SEGMENTS[zh])
    return text


def apply_texts(swf, texts):
    """texts: {tag id: [ko per record]} for EditText (string replace) and DefineText (sprite conversion)."""
    texts = dict(texts)
    texts.update(TEXT_OVERRIDES)
    if '839' in texts:
        recs = []
        for r in texts['839']:
            for zh in sorted(CREDIT_HANDLES, key=len, reverse=True):
                r = r.replace(zh, CREDIT_HANDLES[zh])
            recs.append(r)
        texts['839'] = recs
    src_dir = os.path.join(WORK, 'text')
    for sid, ko_records in texts.items():
        cid = int(sid)
        zh_records = open(os.path.join(src_dir, f'{cid}.txt'), encoding='utf-8').read().split('\n--- RECORDSEPARATOR ---\n')
        zh_records = [r.rstrip('\n') for r in zh_records]
        lst, i, tag = swf.find_define(cid)
        if tag.type == 37:
            e = parse_edit_text(tag.body)
            text = e.get('text') or ''
            for zh, ko in zip(zh_records, ko_records):
                if zh and zh in text:
                    text = text.replace(zh, ko)
            if CJK.search(text):
                text = replace_cjk_segments(text)
            if CJK.search(text):
                print(f'  ! EditText {cid}: Chinese left after replacement: {CJK.findall(text)[:10]}')
            e['text'] = text
            e['f2'] &= ~0x01  # device font: Hangul glyphs come from the player's font
            lst[i] = build_edit_text(e)
        elif tag.type in (11, 33):
            lst[i:i + 1] = define_text_to_sprite(swf, tag, [k.rstrip('\n') for k in ko_records],
                                                 color=TEXT_COLORS.get(cid))


SPLASH_PLACEMENT = {534: (1.056, 116.80, 48.50), 552: (1.313, 65.00, 52.10)}  # root matrix (scale, tx, ty)


def stage_rect_shape(cid, bitmap_id, sprite_id):
    """A 600x400 bitmap shape that exactly covers the stage once its sprite's root matrix is applied."""
    sc, tx, ty = SPLASH_PLACEMENT[sprite_id]
    return bitmap_rect_shape(cid, bitmap_id, -tx / sc, -ty / sc, 600 / sc, 400 / sc, bitmap_px=(600, 400))


def replace_splash(swf, splash_png):
    """Loader (sprite 534) shows the splash instead of the 5DPlay logo; logo animation (552) becomes a fade."""
    bmp = swf.new_id()
    shp_loader, shp_anim, shp_none = swf.new_id(), swf.new_id(), swf.new_id()
    swf.insert_before_define(521, [bits_lossless2(bmp, splash_png),
                                   stage_rect_shape(shp_loader, bmp, 534), empty_shape(shp_none)])
    # in the loader sprite, show our splash in place of logo shape 521 and blank out logo shape 522
    _, _, loader = swf.find_define(534)
    for t in loader.children:
        if t.type == 26 and parse_place_object2(t.body).get('char') in (521, 522):
            new = shp_loader if parse_place_object2(t.body)['char'] == 521 else shp_none
            t.body = t.body[:3] + new.to_bytes(2, 'little') + t.body[5:]
    # logo animation sprite: replace with 60-frame fade (in 10, hold 40, out 10) then stop + _root.play()
    _, _, anim = swf.find_define(552)
    finish = next(t for t in anim.children if t.type == 12 and b'play' in t.body)
    swf.insert_before_define(552, [stage_rect_shape(shp_anim, bmp, 552)])
    kids, n = [], 60
    for f in range(n):
        alpha = min(1.0, (f + 1) / 10, (n - f) / 10)
        kids.append(place_with_alpha(1, alpha, char=shp_anim if f == 0 else None, move=f > 0))
        if f == n - 1:
            kids.append(finish)
        kids.append(Tag(1, b'', False))
    kids.append(Tag(0, b'', False))
    anim.children, anim.frames = kids, n


PERF_FIXES = {  # measured with tools/perf/perf.html (title screen, 900x600): see ANALYSIS.md "Performance"
    # root-level bitmap caching re-rasterises the whole, constantly changing stage every frame
    'frame_2/DoAction.as': lambda t: t.replace('_root.cacheAsBitmap = true;', '// _root.cacheAsBitmap disabled (perf)', 1),
    # afterimage bitmaps were never freed: keep the effect, dispose each bitmap when its clip fades out
    'frame_8/DoAction.as': lambda t: t.replace(
        '   _loc4_.attachBitmap(_loc8_,_loc6_);', '   _loc4_.attachBitmap(_loc8_,_loc6_);\n   _loc4_.bmp = _loc8_;', 1).replace(
        '      if(this._alpha <= 0)\n      {\n         this.removeMovieClip();',
        '      if(this._alpha <= 0)\n      {\n         this.bmp.dispose();\n         this.removeMovieClip();', 1),
}
OTHER_STRING_SCRIPTS = [
    'DefineSprite_1477/frame_1/DoAction.as', 'DefineSprite_1480/frame_1/DoAction.as', 'DefineSprite_1505/frame_1/DoAction.as',
    'DefineSprite_620/frame_1/PlaceObject2_619_28/CLIPACTIONRECORD onClipEvent(enterFrame).as',
    'DefineSprite_835/frame_5/DoAction.as',
    'DefineSprite_836/frame_1/PlaceObject2_739_33/CLIPACTIONRECORD onClipEvent(keyDown).as',
    'DefineSprite_836/frame_1/PlaceObject2_739_33/CLIPACTIONRECORD onClipEvent(keyUp).as',
]
_MAP_TXT = '      _root.txt = _loc2_._name;'
MAP_NAME_FIXES = {  # map select shows instance names (= ids); show the translated map name instead
    rel: (lambda t: t.replace(_MAP_TXT, '      _root.txt = _root.getMapData(_loc2_._name).name;', 1))
    for rel in ('DefineSprite_1477/frame_1/DoAction.as', 'DefineSprite_1480/frame_1/DoAction.as',
                'DefineSprite_1505/frame_1/DoAction.as')
}
MAP_NAME_FIXES['DefineSprite_1504/frame_1/DoAction.as'] = lambda t: t.replace(
    'txt.text = _name;', 'var md = _root.getMapData(_name);\ntxt.text = md.name != undefined ? md.name : _name;', 1)


def patch_scripts(strings):
    """Write translated copies of scripts that hold display strings; returns the import folder."""
    imp = os.path.join(BUILD, 'game_scripts')
    shutil.rmtree(imp, ignore_errors=True)

    def tr(s):
        return strings.get(s, s)

    def emit(rel, text):
        os.makedirs(os.path.join(imp, 'scripts', os.path.dirname(rel)), exist_ok=True)
        open(os.path.join(imp, 'scripts', rel), 'w', encoding='utf-8').write(text)

    f6 = open(os.path.join(SCRIPTS, 'frame_6/DoAction.as'), encoding='utf-8').read()
    f6 = re.sub(r'name:"([^"]*)"', lambda m: f'name:"{tr(m.group(1))}"', f6)
    f6 = re.sub(r'says:\[(.*?)\]\}', lambda m: 'says:[' + re.sub(r'"((?:[^"\\]|\\.)*)"', lambda n: f'"{tr(n.group(1))}"', m.group(1)) + ']}', f6)
    emit('frame_6/DoAction.as', f6)
    f2 = open(os.path.join(SCRIPTS, 'frame_2/DoAction.as'), encoding='utf-8').read()
    f2 = re.sub(r'new ContextMenuItem\("([^"]*)"', lambda m: f'new ContextMenuItem("{tr(m.group(1))}"', f2)
    f2 = PERF_FIXES['frame_2/DoAction.as'](f2)
    emit('frame_2/DoAction.as', f2)
    f8 = PERF_FIXES['frame_8/DoAction.as'](open(os.path.join(SCRIPTS, 'frame_8/DoAction.as'), encoding='utf-8').read())
    emit('frame_8/DoAction.as', f8)
    patched = [f6, f2]
    # other scripts with display strings only (no ids): exact quoted-literal replacement
    for rel in OTHER_STRING_SCRIPTS:
        txt = open(os.path.join(SCRIPTS, rel), encoding='utf-8').read()
        for zh in sorted(strings, key=len, reverse=True):
            txt = txt.replace(f'"{zh}"', f'"{strings[zh]}"')
        txt = MAP_NAME_FIXES.get(rel, lambda t: t)(txt)
        emit(rel, txt)
        patched.append(txt)
    for rel, fix in MAP_NAME_FIXES.items():
        if rel not in OTHER_STRING_SCRIPTS:
            txt = fix(open(os.path.join(SCRIPTS, rel), encoding='utf-8').read())
            emit(rel, txt)
            patched.append(txt)
    left = [zh for zh in strings if any(f'"{zh}"' in t for t in patched) and strings[zh] != zh]
    return imp, left


def build_game(ui_dir):
    strings = load_json('l10n/game_strings.json', {})
    texts = load_json('l10n/game_texts.json', {})
    swf = Swf.load(os.path.join(GAME, 'game.swf'))
    apply_texts(swf, texts)
    splash = os.path.join(ui_dir, 'splash_600x400.png')
    if os.path.exists(splash):
        replace_splash(swf, splash)
    stage1 = os.path.join(BUILD, 'game_stage1.swf')
    swf.save(stage1)
    pairs = [(int(f[:-4]), os.path.join(ui_dir, f), 'lossless2') for f in sorted(os.listdir(ui_dir))
             if re.fullmatch(r'\d+\.png', f)] if os.path.isdir(ui_dir) else []
    stage2 = os.path.join(BUILD, 'game_stage2.swf')
    if pairs:
        ffdec_replace(stage1, stage2, pairs)
    else:
        shutil.copy(stage1, stage2)
    imp, left = patch_scripts(strings)
    ffdec_import_scripts(stage2, os.path.join(DIST, 'game.swf'), imp)
    return left


def main():
    os.makedirs(BUILD, exist_ok=True)
    prepare_dist()
    left = build_game(os.path.join(WORK, 'design/out'))
    print('built', DIST)
    if left:
        print(f'{len(left)} translated strings not applied by script patching (check):', left[:10])


if __name__ == '__main__':
    main()
