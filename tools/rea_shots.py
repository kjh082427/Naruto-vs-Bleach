"""Extract screenshots and a short event summary from a saved REA browser-scenario result.

usage: tools/venv/bin/python tools/rea_shots.py <result.json|exported bundle> <outdir> [--sheet] [--evidence=<id prefix>]
"""
import base64
import json
import os
import sys


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    d = json.load(open(src))
    if 'records' in d and 'normalized_result' not in d:  # exported evidence bundle: take the last scenario record
        recs = [r for r in d['records'] if r.get('operation') == 'capture_browser_scenario']
        want = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--evidence=')), None)
        d = next(r for r in recs if r['evidence_id'].startswith(want)) if want else recs[-1]
    n = d['normalized_result']
    print('evidence', d['evidence_id'])
    paths = []
    for i, s in enumerate(n['steps']):
        shot = s.get('artifacts', {}).get('screenshot', {}).get('value', {})
        if shot.get('data_base64'):
            p = os.path.join(out, f'{i:02d}_{s["step_id"]}.png')
            open(p, 'wb').write(base64.b64decode(shot['data_base64']))
            paths.append(p)
        print(i, s['step_id'], s['status'])
    seen = {}
    for it in n['events']['items']:
        if it.get('kind') == 'page-error':
            print('PAGE ERROR', json.dumps(it, ensure_ascii=False)[:300])
        url = it.get('url', {}).get('url', '')
        if url and 'ruffle' not in url and it.get('status'):
            seen[url] = it['status']
    for url, status in seen.items():
        print('req', status, url)
    if '--sheet' in sys.argv and paths:
        from PIL import Image
        ims = [Image.open(p) for p in paths]
        w, h = ims[0].size
        cols = 3
        sheet = Image.new('RGB', (w * cols // 2, h * ((len(ims) + cols - 1) // cols) // 2), 'white')
        for k, im in enumerate(ims):
            sheet.paste(im.resize((w // 2, h // 2)), ((k % cols) * w // 2, (k // cols) * h // 2))
        sheet.save(os.path.join(out, 'sheet.png'))
        print('sheet', os.path.join(out, 'sheet.png'))


if __name__ == '__main__':
    main()
