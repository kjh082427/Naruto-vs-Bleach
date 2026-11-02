# Shanks sprites: status

Run: `tools/venv/bin/python work/shanks/render_sprites.py` (about 60 s, deterministic: two runs give identical md5s; needs numpy, Pillow, scipy — scipy was added to tools/venv for v3).
Test run on a few ids without touching sprites/: `... render_sprites.py --ids 6,146,441 --out <dir>` (writes pads/report into `<dir>`).

## v3 (2026-11-02): 2x art, cape over the arms, long hair, Haki release pose
User feedback on v2: low image quality; white sleeves made the cape look like a black vest over a white shirt; hair should be longer (to the jaw/nape); improve the model using the reference photos. S+U now uses bitmaps 441/443 (front-facing burst pose).

- **2x resolution.** Every `sprites/<id>.png` is 2 x (w0+l+r) by 2 x (h0+t+b) (pads in `sprites_pad.json`, original pixels). Exception: 339 and 346 stay 1x (`KEEP_1X`; their shapes are not plain bitmap rectangles). `tools/shanks.py` builds with them (`padded_shapes: 235`, SWF 3.45 MB vs 2.1 MB for v2; the largest existing fighter is 3.48 MB).
- **Upscaler (`magnify_labels`).** The 1x role map becomes a map of flat tone labels (cape / lining / shirt / pants / sash / skin tones, facial features, hair, outline, sandals, trail, kept colours). Specks (1-3 px tone islands: the salt-and-pepper of v2) are merged into the surrounding tone (`denoise_labels`). The label map is magnified with Scale2x twice (4x, keeps 1 px lines and single pixels), each label's indicator is Gaussian-smoothed at 4x, then pooled to 2x by argmax. The result has crisp labels (no blended colours), smooth silhouettes and tone bands at any angle, and a 2 px dark outline.
- **Shading at 2x.** New 2x palette (cape navy-black with 5 tones, crimson pants, warm skin, red hair). Drawn procedurally at 2x:
  - hair: strands radiating from the parting, sheen on the crown, darker under-layer and tips, dark-wine rim;
  - cape: 1 px rim light on the top/front edges, soft vertical folds on the floor-length part (the v2 hatch texture is gone) and a wavy hem (no box);
  - pants: flat crimson with a cel shadow along the lower-back edge and a thin light on the upper-front edge; Kenpachi's hakama pleat streaks and fold scribbles are dropped (only thick highlight patches and long leg-separation lines stay).
  - Gryphon is rasterised directly at 2x (finer blade edge, guard and knuckle-bow).
  - Trails and effects: label-magnified silhouette + bilinear ramp field, quantised to 32 steps (`RAMP_LEVELS`; halves the SWF growth, no visible banding at display scale). Effect palette unchanged (`RAMPS["haki"]`, `EFFECT_STYLE`).
- **Cape over the arms (`cape_over_arms`).** Above the waist, Kenpachi's black kimono stays white shirt only in the open front: a `CHEST_W` (4 px) band around the torso axis (neck -> waist, vertical for upright figures) and the cloth framing the bare chest (the V-neck; Kenpachi's white haori lapels next to the chest are turned into shirt so the V reads as an open shirt). The sword forearm stays white for `FOREARM` px (geodesic, from the sword hand) but at most `FORE_MAX` (20) px, so hanging arms show only a cuff. Shoulders, upper arms and the free sleeve become cape (sleeve folds kept as cape tones). Back views (227/229/285/287) are all cape. The kimono collar right under the chin becomes neck shadow (it read as a white beard).
- **Long hair (`long_hair`).** On top of the trimmed red cap, the hair falls behind the face to `HAIR_TIP` (5.6 px) under the face centre (jaw / nape), over the ear (the back 2 px of the face), fuller at the back, notched tips. The frame leans to the screen vertical for upright heads (gravity). Hair-coded pixels on the lower front of the face (Kenpachi's beard / patch strap at the mouth, a red mark in v2) became jaw outline / skin. Floating outline specks left by the trimmed spikes are removed.
- **S+U Haki release, 441 / 443 (`draw_haki_pose`).** Drawn from scratch (supersampled vector shapes reduced to crisp 2x labels): Shanks planted facing front, chest out (open white shirt, bare chest V, red sash with the knot at his left hip, crimson 3/4 pants, sandals), black cape blown wide to both sides with radiating folds, wine lining on the billowing hems and a thin crimson rim light from the Haki dome, hair lifted by the pressure, shouting face, Gryphon held low in his right hand (forearm out of the cape, rolled white sleeve). 441 and 443 are two flutter phases (wing lift, hem waves and hair tips alternate, mirrored left/right). Kenpachi's sword-blur streaks are gone. Both use the same figure position (443's shape is 2.7 px right of 441's, compensated); pads 441 [5,0,17,0], 443 [9,0,16,0].
- Other fixes: the flying haori in 435/437/439 used the trail colours and was rendered crimson (also in v2): `HAORI_NOT_TRAIL` makes those pieces cape again. Tiny floating blobs (katana leftovers) are dropped.
- Previews: `preview_v3_style.png` (style test: original | v2 | v3 at 1.5x and 2x display scale, then a 4x zoom), `preview_v3.png` (before/after board of 14 poses at 2x display scale on the street stage), `sprites_sheet.png` (all ids, original | new).

## Unchanged from v2
- Gryphon design and placement (SWORDS table + auto), SWORD_SCALE 1.4; left-arm cuts (ARMS); waist lines (WAIST); 3/4 pants + bare shins + sandals; red sash; clean face (no scars on the small sprite); effect palette per label.

## Weak / guesswork ids
- 441/443: procedural figure; at 2x the face is a simple front face, the sword sleeve is short. Check them in game against the Haki dome (the crimson rim is there to separate the black cape from the dark dome).
- Twisted air poses (56, 61, 63-67, 69-74, 183, 498): the shirt front shows as a larger white area (the torso band covers the whole front); arms are cape.
- Afterimage / blur frames: 31/33 (dithered faces), 207, 355/408/410/412 (Kenpachi's sword-blur streaks stay as dark cape streaks; the face in 410 is a tiny light patch).
- Back views 227/229/285/287: the long hair covers the whole back of the head (reads a bit like a hood).
- Lying 492-496: the hakama -> pants turn into a large red mass.
- Floor-length cape behind crouched poses (144-152, 236, 437/439) is a block filled down to the floor (now with a wavy hem and folds).
- Sword placement guessed (blade hidden in a trail or not visible): 79, 141, 168, 171, 289, 312, 314, 102 (auto). No sword drawn: 207, 227, 229, 285, 287, 322, 355, 408, 410, 412, 492, 494, 496, 507.
- Arm left as is (hidden / blurred / unclear which hand is which): 171, 207, 223, 245, 351, 355, 408-412, 509, 511; the "left" hand on two-handed grips in 471/477/479/481/341/344 is a judgement call.
- Heads at odd angles (156, 492-496, 489) keep a rounder hair mass.
