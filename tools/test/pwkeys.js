// Headless play test with real (trusted) key events: Playwright drives a page that only loads game.swf, and every
// console line matching FILTER (AS trace() output; needs Ruffle logLevel "info") is saved with a timestamp.
// Not deployed. Used 2026-11-03 to reproduce and fix Mihawk's hidden 5th hit (ANALYSIS.md §10, Mihawk note).
//
//   page:   tools/test/autoplay.html with logLevel "info" and without its key script, copied into a test dist
//           (BVN_DIST=<scratch>/dist BVN_SELECT_P1=米霍克 tools/venv/bin/python tools/build.py), served on port 8766
//   traces: FFDec -importScript a frame_2 (站立) DoAction into the test copy of the fighter: a createEmptyMovieClip
//           watcher that trace()s getTimer, mc._currentframe, 动作 and Key.isDown(87 W / 74 J) on every change
//   run:    PW_MOD=$HOME/.npm/_npx/f0a362733743bae2/node_modules/playwright \
//           PLAYWRIGHT_BROWSERS_PATH=$HOME/tools/pw/browsers LD_LIBRARY_PATH=$HOME/tools/pw/libs/usr/lib/x86_64-linux-gnu \
//           node tools/test/pwkeys.js http://127.0.0.1:8766/autotest.html <outdir> "<seq>"
//   seq:    comma list; wN = wait N ms; shot = screenshot; key[+key][:hold ms][*n][~gap ms] (default hold 140, gap 260)
//           practice mode with the 1P cursor preset:
//           w16000,s,w500,s,w500,s,w800,j,w2500,j,w3500,j,w2500,j,w2500,j,w2500,j,w2500,j,w9000,<moves>
const { chromium } = require(process.env.PW_MOD || 'playwright');
const fs = require('fs');
const FILTER = new RegExp(process.env.FILTER || 'MHF|WJGO|error|panic', 'i');
const [url, out, seqArg] = process.argv.slice(2);
const KEYS = { up: 'ArrowUp', down: 'ArrowDown', left: 'ArrowLeft', right: 'ArrowRight' };
const key = k => KEYS[k] || 'Key' + k.toUpperCase();
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true, args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: 900, height: 600 } });
  const log = [];
  page.on('console', m => { const t = m.text(); if (FILTER.test(t)) log.push(Date.now() + ' ' + t); });
  await page.goto(url);
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(1500);
  await page.mouse.click(450, 300);  // focus the player
  let shot = 0;
  for (const s of seqArg.split(',').filter(Boolean)) {
    if (/^w\d+$/.test(s)) { await sleep(+s.slice(1)); continue; }
    if (s === 'shot') { await page.screenshot({ path: `${out}/s${String(++shot).padStart(2, '0')}.png` }); continue; }
    const m = s.match(/^([a-z+]+)(?::(\d+))?(?:\*(\d+))?(?:~(\d+))?$/);
    if (!m) continue;
    const ks = m[1].split('+');
    for (let n = 0; n < (+m[3] || 1); n++) {
      for (const k of ks) { await page.keyboard.down(key(k)); await sleep(20); }
      await sleep(+m[2] || 140);
      for (const k of [...ks].reverse()) await page.keyboard.up(key(k));
      await sleep(m[4] !== undefined ? +m[4] : 260);
    }
    log.push(Date.now() + ' KEY ' + s);
  }
  await sleep(1500);
  await page.screenshot({ path: `${out}/final.png` });
  fs.writeFileSync(`${out}/log.txt`, log.join('\n') + '\n');
  await browser.close();
})();
