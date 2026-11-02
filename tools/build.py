"""Build the Korean edition into dist/ from the pristine game/ tree.

usage: tools/venv/bin/python tools/build.py

Inputs
  game/                               pristine restored game (never modified)
  work/l10n/game_strings.json         zh->ko for script string literals (bvn-localizer)
  work/l10n/game_texts.json           {text tag id: [ko per record]} (bvn-localizer)
  work/design/out/*.png               UI bitmaps named by character id + splash_600x400.png + title_bg_600x400.png
                                      (game-ui-designer)
  work/op/roster.json, work/op/ui/    One Piece fighters (tools/op_assets.py) + source/onepiece/blog/*.swf, *.mp3
  work/<custom>/                      custom fighters (CUSTOM_FIGHTERS: Mihawk tools/mihawk.py, Shanks tools/shanks.py)
  web/                                page template + assets copied into dist/ (index.html needs __RUFFLE_CONFIG__)
  tools/ruffle_config.json            Ruffle player config injected into index.html
Outputs
  dist/  (game.swf, fonts, index.html, ...)
"""
import importlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from swfpatch import Swf, Tag, bits_lossless2, parse_place_object2, place_object2  # noqa: E402
from swftext import (bitmap_rect_shape, build_edit_text, define_text_to_sprite, empty_shape, parse_edit_text,  # noqa: E402
                     place_with_alpha)

FFDEC = ['java', '-jar', os.path.join(ROOT, 'tools/ffdec/ffdec.jar')]
GAME, DIST, WORK = (os.path.join(ROOT, p) for p in ('game', 'dist', 'work'))
DIST = os.environ.get('BVN_DIST') or DIST  # test builds elsewhere (e.g. a scratch dir served on port 8766)
BUILD = os.path.join(WORK, 'build')
SCRIPTS = os.path.join(ROOT, 'analysis/game/scripts/scripts')
CJK = re.compile(r'[㐀-鿿　-〿＀-￯]')
VERSION = open(os.path.join(ROOT, 'VERSION')).read().strip()  # shown in game, page and splash; bumped per release

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


def prepare_dist(fighters=()):
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
    n_op = len(fighters)
    for k, v in (('__RUFFLE_CONFIG__', config), ('__VERSION__', VERSION),
                 ('__ROSTER_TOTAL__', str(len(BLEACH_ORDER) + len(NARUTO_ORDER) + n_op)), ('__ROSTER_OP__', str(n_op))):
        html = html.replace(k, v)
    open(os.path.join(DIST, 'index.html'), 'w', encoding='utf-8').write(html)


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
    if '658' in texts:  # "update notes" panel: version line
        texts['658'] = [VERSION] + list(texts['658'][1:])
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


# --- One Piece fighters (ported from "Fairy Tail vs One Piece 1.1", same 5DPlay engine; see ANALYSIS.md §8) ----------

OP_SRC = os.path.join(ROOT, 'source/onepiece/blog')
OP_UI = os.path.join(WORK, 'op/ui')
OP_ROSTER = os.path.join(WORK, 'op/roster.json')
OP_DIR = 'op/'  # under fighter/
ICON_SPRITE, PORTRAIT_SPRITE, FACE_SPRITE, SELECT_SPRITE, SLOT_SPRITE = 1465, 1346, 1676, 1477, 1469
BANNER_SPRITE = 1983  # versus-loading banners (sprite 1989 frame 11: p1xg.dt.gotoAndStop(_root.p1selt))
TITLE_SPRITE, TITLE_BG_SHAPE = 666, 554
TITLE_HIDE = {556, 579, 584, 585, 578, 583, 587, 589, 590, 621}  # old character art, rasengan glow, logo pieces, VS
# select screen: 12 x 5 grid, factions as contiguous column-major runs (Bleach, Naruto, One Piece + Mihawk)
BLEACH_ORDER = ['一护', '一护万解', '一护2', '露其雅', '露其雅始解', '恋次', '日番谷', '日番谷万解', '白哉', '茶渡', '石田',
                '小乌', '银', '剑八', '一角', '涅茧利', '蓝染', '剑心']
NARUTO_ORDER = ['鸣人', '鸣人九尾', '仙鸣', '佐助', '佐助咒怨', '佐助须佐', '樱', '卡卡西', '小李', '宁次', '手鞠', '我爱罗',
                '鼬', '大蛇丸', '自来也', '佩恩', '小南', '带土', '迪达拉', '重吾', '香磷', '奇拉比']
GRID_COLS, GRID_ROWS, SLOT_SCALE = 12, 5, 0.8
GRID_X0, GRID_Y0, GRID_DX, GRID_DY = -40.1, 54.85, 44.0, 44.0  # sprite 1477 local px (= screen - (76.6, 90.15))
OP_MUSIC = ['onepiece.mp3', 'onepiece2.mp3', 'onepiece3.mp3']
# custom fighters made from a reskinned base fighter: (work/<name>/ dir and builder tools/<name>.py, extra registry
# fields). Each joins the build once work/<name>/fighter.json and tools/<name>.py both exist.
CUSTOM_FIGHTERS = [('mihawk', {'WKframe': 2}), ('shanks', {})]


def op_roster():
    return json.load(open(OP_ROSTER, encoding='utf-8'))['fighters'] if os.path.exists(OP_ROSTER) else []


def custom_entries():
    """Registry entries of the ready custom fighters (Mihawk, Shanks ...), registered as One Piece fighters."""
    out = []
    for name, extra in CUSTOM_FIGHTERS:
        spec = os.path.join(WORK, name, 'fighter.json')
        if os.path.exists(spec) and os.path.exists(os.path.join(ROOT, 'tools', f'{name}.py')):
            out.append(dict(json.load(open(spec, encoding='utf-8')), **extra, _name=name))
    return out


def as_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def op_registry_lines(roster):
    lines = []
    for f in roster:
        fields = [f'name:{as_str(f["name"])}', f'url:{as_str(OP_DIR + f["swf"])}', 'isOnePiece:true']
        if f.get('WKframe'):
            fields.append(f'WKframe:{f["WKframe"]}')
        if f.get('fz'):
            fields.append(f'fz:{as_str(f["fz"])}')
        if f.get('vs'):
            fields.append('vs:[' + ','.join(map(as_str, f['vs'])) + ']')
        if f.get('music'):
            fields.append(f'music:{as_str(f["music"])}')
        fields.append('says:[' + ','.join(map(as_str, f['says'])) + ']')
        lines.append(f'addFighterData({as_str(f["id"])},{{{",".join(fields)}}});')
    return '\n'.join(lines)


# frame_8 additions: the One Piece fighters call _root.shake() (screen shake), which BVN's engine lacks
OP_ENGINE_AS = '''
function shake(pow, holdFrame)
{
   if(pow == undefined)
   {
      pow = 6;
   }
   if(holdFrame == undefined)
   {
      holdFrame = 3;
   }
   _shakePow = pow;
   _shakeDis = pow / holdFrame * 2;
   var _loc2_ = _root.createEmptyMovieClip("shakeDriver",99990);
   _loc2_.onEnterFrame = function()
   {
      _root.shakeIng();
      if(_root._shakePow == 0)
      {
         this.removeMovieClip();
      }
   };
}
function shakeIng()
{
   if(_shakePow == 0)
   {
      return undefined;
   }
   _root._y += _shakePow;
   if(_shakePow < 0)
   {
      if(_shakePow > (- _shakeDis) * 2)
      {
         _shakePow = 0;
         _shakeDis = 0;
         _root._y = 0;
         return undefined;
      }
      _shakePow += _shakeDis;
   }
   _shakePow *= -1;
}
'''
# the fighters unload themselves unless _root.HASH is the source game's value
OP_SETTINGS_AS = 'var HASH = "5dplay_fvo";\n'
# select screen: start the cursors on Ichigo (1P) and Naruto (2P) wherever the grid puts them
# (BVN_SELECT_P1 / BVN_SELECT_P2 override the start fighter ids, for scripted test runs)
SELECT_START = (os.environ.get('BVN_SELECT_P1', '一护'), os.environ.get('BVN_SELECT_P2', '鸣人'))
SELECT_START_FIXES = [
    ('   var _loc1_ = 5;\n   while(_loc1_ > 0)\n   {\n      if(updateXY(1,_loc1_,7))\n      {\n         break;\n      }\n'
     '      _loc1_ = _loc1_ - 1;\n   }',
     f'   var _loc1_ = _this["{SELECT_START[0]}"];\n   updateXY(1,int(_loc1_._x / 30),int(_loc1_._y / 30));'),
    ('   var _loc1_ = 7;\n   while(_loc1_ < 12)\n   {\n      if(updateXY(2,_loc1_,7))\n      {\n         break;\n      }\n'
     '      _loc1_ = _loc1_ + 1;\n   }',
     f'   var _loc1_ = _this["{SELECT_START[1]}"];\n   updateXY(2,int(_loc1_._x / 30),int(_loc1_._y / 30));'),
]


# 일반 대전 (modo 1): the first stages used fixed lists (Bleach/One Piece players always met Temari first,
# Naruto players Rukia). Draw them at random from the selectable roster instead (no repeats, skipping the player,
# the boss and the player's rival list, which still fill the later stages); opponents without a CPU assist get one.
RANDOM_STAGE_FIXES = [
    ("""   if(stg < _loc3_.length)
   {
      if(_loc6_)
      {
         _loc3_ = _root.narutoStages;
      }
      _root.p2selt = _loc3_[stg];
   }""", """   if(stg < _loc3_.length)
   {
      if(stg == 0 || _root.randStages == undefined)
      {
         _root.randStages = randomOpponents(_loc5_,_loc3_.length);
      }
      _root.p2selt = _root.randStages[stg];
   }"""),
    ("""   _root.p2sf = _loc2_.fz;""", """   _root.p2sf = _loc2_.fz;
   if(_root.p2sf == undefined)
   {
      _root.p2sf = randomAssist();
   }"""),
]
RANDOM_STAGE_AS = """
function randomOpponents(me, n)
{
   var skip = {};
   skip[_root.p1selt] = true;
   skip[_root.bossStage] = true;
   for(var v in me.vs)
   {
      skip[me.vs[v]] = true;
   }
   var pool = [];
   for(var i = 0; i < _root.selectableIds.length; i++)
   {
      if(!skip[_root.selectableIds[i]])
      {
         pool.push(_root.selectableIds[i]);
      }
   }
   var out = [];
   while(out.length < n && pool.length > 0)
   {
      out.push(pool.splice(Math.floor(Math.random() * pool.length),1)[0]);
   }
   return out;
}
function randomAssist()
{
   var a = [];
   for(var id in _root.fighterData)
   {
      if(_root.fighterData[id].fzurl != undefined)
      {
         a.push(id);
      }
   }
   return a[Math.floor(Math.random() * a.length)];
}
"""


# versus-loading loader (sprite 1989's loadMC): loads p1, p2, p1 assist, p2 assist with one MovieClipLoader and only
# trace()d onLoadError, so one failed request (a server restart, a dropped connection) left the bar frozen forever.
# Retry the failed step every 1.5 s instead; it resumes as soon as the file can be fetched again.
LOADER_SPRITE = 1900
LOADER_RETRY_FIXES = [
    ('function loadError(target_mc, errorCode)\n{\n',
     'function loadError(target_mc, errorCode)\n{\n'
     '   clearInterval(_this.retryInt);\n   _this.retryInt = setInterval(retryLoad,1500);\n'),
]
LOADER_RETRY_AS = """
function retryLoad()
{
   clearInterval(_this.retryInt);
   loadSteps[loadStep]();
}
"""


def apply_fixes(text, fixes, where):
    for old, new in fixes:
        assert text.count(old) == 1, f'{where}: patch anchor not found once: {old[:60]!r}'
        text = text.replace(old, new)
    return text


def add_bitmap_frames(swf, sprite_id, kind, names, layout):
    """Append one labeled frame per name to a label-indexed sprite, showing work/op/ui/<kind>/<name>.png."""
    from PIL import Image
    new_defs = []
    for name in names:
        png = os.path.join(OP_UI, kind, f'{name}.png')
        w, h = Image.open(png).size
        bmp, shp = swf.new_id(), swf.new_id()
        x, y = layout[kind][name]
        new_defs += [bits_lossless2(bmp, png), bitmap_rect_shape(shp, bmp, x, y, w, h)]
        swf.add_labeled_frame(sprite_id, name, shp)
    swf.insert_before_define(sprite_id, new_defs)


def layout_select_grid(swf, roster):
    """Re-place all 55 slots of the fighter select screen in an 11x5 grid and add the One Piece slots."""
    order = BLEACH_ORDER + NARUTO_ORDER + [f['id'] for f in roster]
    assert len(order) <= GRID_COLS * GRID_ROWS
    pos = {fid: (GRID_X0 + (i // GRID_ROWS) * GRID_DX, GRID_Y0 + (i % GRID_ROWS) * GRID_DY) for i, fid in enumerate(order)}
    _, _, sp = swf.find_define(SELECT_SPRITE)
    seen, used = set(), set()
    for k, t in enumerate(sp.children):
        if t.type != 26:
            continue
        p = parse_place_object2(t.body)
        used.add(p['depth'])
        name = p.get('name')
        if name in pos:
            sp.children[k] = place_object2(p['depth'], char=p.get('char'), name=name, raw_tail=p['tail'],
                                           matrix=(SLOT_SCALE, 0, 0, SLOT_SCALE, *pos[name]))
            seen.add(name)
        elif name in ('player1', 'player2'):
            a, b, c, d, tx, ty = p['matrix']
            sp.children[k] = place_object2(p['depth'], char=p.get('char'), name=name, raw_tail=p['tail'],
                                           matrix=(a * SLOT_SCALE, b, c, d * SLOT_SCALE, tx, ty))
    missing = [fid for fid in order if fid not in seen]
    free = (d for d in range(2, 161) if d not in used)  # below the cursors (depths 161, 165)
    swf.first_frame_insert(SELECT_SPRITE, [place_object2(next(free), char=SLOT_SPRITE, name=fid,
                                                          matrix=(SLOT_SCALE, 0, 0, SLOT_SCALE, *pos[fid]))
                                           for fid in missing])
    unplaced = sorted(set(seen) - set(order))
    assert not unplaced, unplaced


def restyle_title(swf, title_png):
    """Title screen: one composed 600x400 bitmap replaces the background; old character/logo layers are hidden."""
    bmp, blank = swf.new_id(), swf.new_id()
    swf.insert_before_define(TITLE_SPRITE, [bits_lossless2(bmp, title_png), empty_shape(blank)])
    swf.replace_define(TITLE_BG_SHAPE, bitmap_rect_shape(TITLE_BG_SHAPE, bmp, 0, 0, 600, 400))
    _, _, sp = swf.find_define(TITLE_SPRITE)
    for t in sp.children:
        if t.type == 26:
            p = parse_place_object2(t.body)
            if p.get('char') in TITLE_HIDE:
                t.body = t.body[:3] + blank.to_bytes(2, 'little') + t.body[5:]
        elif t.type == 70 and t.body[0] & 2 and not t.body[1] & 0x18:  # PlaceObject3 with a character, no class name
            if int.from_bytes(t.body[4:6], 'little') in TITLE_HIDE:  # the rasengan (578) is placed this way
                t.body = t.body[:4] + blank.to_bytes(2, 'little') + t.body[6:]


def add_custom_ui(swf, mh):
    """Icon, select portrait, loading banner and cut-ins of a custom fighter from work/<name>/ui (render_ui.py)."""
    from PIL import Image
    ui = os.path.join(WORK, mh['_name'], 'ui')
    layout_path = os.path.join(ui, 'layout.json')
    if not os.path.exists(layout_path):
        print(f'  ! {mh["_name"]} UI art missing ({ui}): select/loading/cut-in images fall back to frame 1')
        return
    layout = json.load(open(layout_path, encoding='utf-8'))
    items = [(ICON_SPRITE, mh['id'], 'icon'), (PORTRAIT_SPRITE, mh['id'], 'portrait'),
             (BANNER_SPRITE, mh['id'], 'banner')] + [(FACE_SPRITE, lab, f) for lab, f in mh['faces'].items()]
    for sprite, label, name in items:
        png = os.path.join(ui, f'{name}.png')
        w, h = Image.open(png).size
        bmp, shp = swf.new_id(), swf.new_id()
        swf.add_labeled_frame(sprite, label, shp)
        swf.insert_before_define(sprite, [bits_lossless2(bmp, png), bitmap_rect_shape(shp, bmp, *layout[name], w, h)])


def add_one_piece(swf, roster):
    layout = json.load(open(os.path.join(OP_UI, 'layout.json'), encoding='utf-8'))
    ids = [f['id'] for f in roster]
    add_bitmap_frames(swf, ICON_SPRITE, 'icon', ids, layout)
    add_bitmap_frames(swf, PORTRAIT_SPRITE, 'portrait', ids, layout)
    add_bitmap_frames(swf, FACE_SPRITE, 'face', [lab for f in roster for lab in f['faces']], layout)
    add_bitmap_frames(swf, BANNER_SPRITE, 'banner', ids, layout)


HURTBOX_ANCHOR = ('   if(!_loc3_)\n   {\n      _loc3_ = getHitObj(_fzfsArray,_root.game["p" + _parent.pn + "fz"],"",_parent.fzpw);\n'
                  '   }\n')
HURTBOX_STG = '''function getStgHitObj()
{
   var _loc4_;
   for(var _loc5_ in stgks)
   {
      _loc4_ = _root.game.layer_effect[stgks[_loc5_] + "_P" + _parent.pn];
      if(_loc4_)
      {
         if(this.hitTest(_loc4_.mian))
         {
            return _loc4_.hitObj;
         }
      }
   }
}
var stgks = ["stgk1","stgk2","stgk3","stgk4","stgk5","stgk6","stgk7","stgk8","stgk9","stgk10"];
'''


def build_op_fighters(roster):
    """Copy the One Piece fighter SWFs; their hurtboxes also learn BVN's stage hits (addStgHit projectiles)."""
    out_dir = os.path.join(DIST, 'fighter', OP_DIR)
    os.makedirs(out_dir, exist_ok=True)
    for f in roster:
        name = f['swf'][:-4]
        scripts = os.path.join(ROOT, 'analysis/op', name, 'scripts/scripts')
        imp = os.path.join(BUILD, 'op_scripts', name)
        shutil.rmtree(imp, ignore_errors=True)
        for r, _, fs in os.walk(scripts):
            for fn in fs:
                txt = open(os.path.join(r, fn), encoding='utf-8').read()
                if 'function getHitObj(array, player, afterFix, ppw)' not in txt or HURTBOX_ANCHOR not in txt:
                    continue
                fixed = txt.replace(HURTBOX_ANCHOR, HURTBOX_ANCHOR + '   if(!_loc3_)\n   {\n      _loc3_ = getStgHitObj();\n   }\n')
                fixed = fixed.replace('      _parent.tdtime = _loc3_.hdtime / 1000 * 30;\n',
                                      '      _parent.tdtime = _loc3_.hdtime / 1000 * 30;\n'
                                      '      if(isNaN(_parent.tdtime))\n      {\n         _parent.tdtime = 0;\n      }\n')
                fixed = fixed.replace('function getHitObj(array, player, afterFix, ppw)', HURTBOX_STG + 'function getHitObj(array, player, afterFix, ppw)', 1)
                rel = os.path.relpath(os.path.join(r, fn), scripts)
                os.makedirs(os.path.join(imp, 'scripts', os.path.dirname(rel)), exist_ok=True)
                open(os.path.join(imp, 'scripts', rel), 'w', encoding='utf-8').write(fixed)
        assert os.path.isdir(imp), f'{name}: hurtbox script not found'
        ffdec_import_scripts(os.path.join(OP_SRC, f['swf']), os.path.join(out_dir, f['swf']), imp)
    for mp3 in OP_MUSIC:
        shutil.copy(os.path.join(OP_SRC, mp3), os.path.join(DIST, 'music', mp3))


def patch_scripts(strings, roster):
    """Write translated (and One Piece-extended) copies of game scripts; returns the import folder."""
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
    if roster:  # One Piece registry lines (already Korean) go after the BVN fighters, before the map registry
        first_map = re.search(r'^addMapData\(', f6, re.M).start()
        f6 = f6[:first_map] + op_registry_lines(roster) + '\n' + f6[first_map:]
    ids = BLEACH_ORDER + NARUTO_ORDER + [f['id'] for f in roster]  # random story opponents (RANDOM_STAGE_AS)
    f6 += '\nvar selectableIds = [' + ','.join(map(as_str, ids)) + '];\n'
    emit('frame_6/DoAction.as', f6)
    f1 = open(os.path.join(SCRIPTS, 'frame_1/DoAction.as'), encoding='utf-8').read()
    emit('frame_1/DoAction.as', apply_fixes(f1, [('_root.ver = "V 2.6";', f'_root.ver = "V {VERSION}";')], 'frame_1'))
    f2 = open(os.path.join(SCRIPTS, 'frame_2/DoAction.as'), encoding='utf-8').read()
    f2 = re.sub(r'new ContextMenuItem\("([^"]*)"', lambda m: f'new ContextMenuItem("{tr(m.group(1))}"', f2)
    f2 = PERF_FIXES['frame_2/DoAction.as'](f2)
    emit('frame_2/DoAction.as', f2)
    f8 = PERF_FIXES['frame_8/DoAction.as'](open(os.path.join(SCRIPTS, 'frame_8/DoAction.as'), encoding='utf-8').read())
    f8 = apply_fixes(f8, RANDOM_STAGE_FIXES, 'frame_8 gostg') + RANDOM_STAGE_AS
    if roster:
        f8 += OP_ENGINE_AS
        emit('frame_7/DoAction.as', open(os.path.join(SCRIPTS, 'frame_7/DoAction.as'), encoding='utf-8').read() + OP_SETTINGS_AS)
    emit('frame_8/DoAction.as', f8)
    loader = f'DefineSprite_{LOADER_SPRITE}/frame_1/DoAction.as'
    emit(loader, apply_fixes(open(os.path.join(SCRIPTS, loader), encoding='utf-8').read(), LOADER_RETRY_FIXES, loader)
         + LOADER_RETRY_AS)
    patched = [f6, f2]
    # other scripts with display strings only (no ids): exact quoted-literal replacement
    for rel in OTHER_STRING_SCRIPTS:
        txt = open(os.path.join(SCRIPTS, rel), encoding='utf-8').read()
        for zh in sorted(strings, key=len, reverse=True):
            txt = txt.replace(f'"{zh}"', f'"{strings[zh]}"')
        txt = MAP_NAME_FIXES.get(rel, lambda t: t)(txt)
        if roster and rel == f'DefineSprite_{SELECT_SPRITE}/frame_1/DoAction.as':
            txt = apply_fixes(txt, SELECT_START_FIXES, rel)
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
    roster, customs = op_roster(), custom_entries()
    fighters = roster + customs
    swf = Swf.load(os.path.join(GAME, 'game.swf'))
    apply_texts(swf, texts)
    splash = os.path.join(ui_dir, 'splash_600x400.png')
    if os.path.exists(splash):
        replace_splash(swf, splash)
    title = os.path.join(ui_dir, 'title_bg_600x400.png')
    if os.path.exists(title):
        restyle_title(swf, title)
    if roster:
        add_one_piece(swf, roster)
        build_op_fighters(roster)
    for mh in customs:
        add_custom_ui(swf, mh)
        builder = importlib.import_module(mh['_name'])
        print(f'  {mh["_name"]}:', builder.build(os.path.join(DIST, 'fighter', OP_DIR, mh['swf']), BUILD))
    if fighters:
        layout_select_grid(swf, fighters)
    stage1 = os.path.join(BUILD, 'game_stage1.swf')
    swf.save(stage1)
    pairs = [(int(f[:-4]), os.path.join(ui_dir, f), 'lossless2') for f in sorted(os.listdir(ui_dir))
             if re.fullmatch(r'\d+\.png', f)] if os.path.isdir(ui_dir) else []
    stage2 = os.path.join(BUILD, 'game_stage2.swf')
    if pairs:
        ffdec_replace(stage1, stage2, pairs)
    else:
        shutil.copy(stage1, stage2)
    imp, left = patch_scripts(strings, fighters)
    ffdec_import_scripts(stage2, os.path.join(DIST, 'game.swf'), imp)
    return left


def swap_dist(new, final):
    """Replace final/ by new/ with two renames, so a server running on final/ never sees a half-built tree."""
    old = final + '.old'
    shutil.rmtree(old, ignore_errors=True)
    if os.path.isdir(final):
        os.rename(final, old)
    os.rename(new, final)
    shutil.rmtree(old, ignore_errors=True)


def main():
    global DIST
    os.makedirs(BUILD, exist_ok=True)
    final, DIST = DIST, DIST + '.new'  # build beside dist/ and swap at the end: the running server keeps working
    prepare_dist(op_roster() + custom_entries())
    left = build_game(os.path.join(WORK, 'design/out'))
    swap_dist(DIST, final)
    DIST = final
    print('built', DIST)
    if left:
        print(f'{len(left)} translated strings not applied by script patching (check):', left[:10])


if __name__ == '__main__':
    main()
