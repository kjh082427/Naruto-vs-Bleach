// 원격 2P end-to-end test (not deployed; ANALYSIS.md §11). Two headless Chromium contexts, host + guest, connect
// through the real PeerJS broker (needs internet), then a key sequence runs on either side.
//
//   page:  a copy of dist/ served on 8766 (never the user's 8765), e.g. a full test build
//          (BVN_DIST=<scratch>/dist tools/venv/bin/python tools/build.py) or dist/ symlinks + the current web/ files
//   run:   PW_MOD=$HOME/.npm/_npx/f0a362733743bae2/node_modules/playwright \
//          PLAYWRIGHT_BROWSERS_PATH=$HOME/tools/pw/browsers LD_LIBRARY_PATH=$HOME/tools/pw/libs/usr/lib/x86_64-linux-gnu \
//          node tools/test/remote2p.js http://127.0.0.1:8766/ <outdir> "<seq>"
//   seq:   wN | shot (both pages) | stats | rtc (WebRTC getStats summary) | h:<keys> host keys | g:<keys> guest keys
//          | lat:<code> guest key -> change in the P2 area of the received video (ms)
//          | hlat:<code> host 1P key -> change in its own canvas (local baseline) | eval:<js on guest>
//          keys like pwkeys.js: key[+key][:hold][*n][~gap]
//   into a VS 사람 match (cursor 1P 이치고 / 2P 나루토, stage etc. by J):
//          w12000,h:s,w600,h:s,w600,h:j,w3000,h:j,w1500,g:j,w2500,h:j,w2000,g:j,w2000,h:j,w2500,h:j,w2500,g:j,w9000
const { chromium } = require(process.env.PW_MOD);
const fs = require('fs');
const [url, out, seqArg] = process.argv.slice(2);
const KEYS = { up: 'ArrowUp', down: 'ArrowDown', left: 'ArrowLeft', right: 'ArrowRight' };
const key = k => KEYS[k] || (/^n\d$/.test(k) ? 'Numpad' + k[1] : 'Key' + k.toUpperCase());
const sleep = ms => new Promise(r => setTimeout(r, ms));
const t0 = Date.now();
const log = [];
const L = s => { const l = ((Date.now() - t0) / 1000).toFixed(1) + ' ' + s; log.push(l); console.log(l); };
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true, args: ['--autoplay-policy=no-user-gesture-required'] });
  const hctx = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const gctx = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const host = await hctx.newPage(), guest = await gctx.newPage();
  for (const [n, pg] of [['H', host], ['G', guest]])
    pg.on('console', m => { const t = m.text(); if (/error|panic|rp |peer/i.test(t) && !/log_adapter/.test(t)) L(n + ' console ' + t.slice(0, 200)); });
  await host.goto(url);
  await sleep(2500);
  await host.mouse.click(900, 360);  // focus the game
  await host.click('#rp-host');
  await host.waitForFunction(() => /보내 주세요/.test(document.getElementById('rp-status').textContent), null, { timeout: 20000 });
  const code = await host.textContent('#rp-room-code');
  L('room ' + code);
  await guest.goto(url + '#join=' + code);
  await sleep(800);
  L('guest hint: ' + await guest.textContent('#hint') + ' | input=' + await guest.inputValue('#rp-code'));
  await guest.click('#rp-join button');
  try {
    await guest.waitForFunction(() => document.getElementById('remote').dataset.state === 'guest-live', null, { timeout: 30000 });
    L('guest live');
  } catch (e) { L('guest NOT live: ' + await guest.textContent('#rp-status')); }
  L('host state ' + await host.getAttribute('#remote', 'data-state') + ' | ' + await host.textContent('#rp-status'));
  let shot = 0;
  const stats = async () => {
    const g = await guest.evaluate(async () => {
      const v = document.querySelector('.rp-video');
      const r = { vw: v && v.videoWidth, vh: v && v.videoHeight, rtt: window.__rp.rtt, log: window.__rp.log };
      return r;
    });
    L('guest ' + JSON.stringify(g));
    const h = await host.evaluate(() => ({ rtt: window.__rp.rtt, log: window.__rp.log, taps: (window.__bvnAudioTaps || []).length }));
    L('host ' + JSON.stringify(h));
  };
  for (const s of seqArg.split(',').filter(Boolean)) {
    if (/^w\d+$/.test(s)) { await sleep(+s.slice(1)); continue; }
    if (s === 'shot') {
      const n = String(++shot).padStart(2, '0');
      await host.screenshot({ path: `${out}/${n}h.png` });
      await guest.screenshot({ path: `${out}/${n}g.png` });
      L('shot ' + n);
      continue;
    }
    if (s === 'stats') { await stats(); continue; }
    if (s.startsWith('lat:')) {  // guest key -> visible change in the P2 area of the received video
      const r = await guest.evaluate(async code => {
        const v = document.querySelector('.rp-video');
        const c = document.createElement('canvas'); c.width = 900; c.height = 600;
        const x = c.getContext('2d', { willReadFrequently: true });
        const X0 = 560, Y0 = 330, W = 340, H = 250;  // right half, floor level (P2 side)
        const snap = () => { x.drawImage(v, 0, 0, 900, 600); return x.getImageData(X0, Y0, W, H).data; };
        const diff = (a, b) => { let n = 0; for (let i = 0; i < a.length; i += 8) if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) > 90) n++; return n; };
        const frame = () => new Promise(r => v.requestVideoFrameCallback(() => r()));
        let base = snap(), noise = 0;
        for (let i = 0; i < 12; i++) { await frame(); const d = snap(); noise = Math.max(noise, diff(base, d)); base = d; }
        await frame(); base = snap();
        const t0 = performance.now();
        dispatchEvent(new KeyboardEvent('keydown', { code, bubbles: true }));
        let ms = -1, n = 0, frames = 0;
        while (performance.now() - t0 < 1500) {
          await frame(); frames++;
          n = diff(base, snap());
          if (n > noise * 2 + 40) { ms = performance.now() - t0; break; }
        }
        await new Promise(r => setTimeout(r, 300));
        dispatchEvent(new KeyboardEvent('keyup', { code, bubbles: true }));
        return { ms: Math.round(ms), n, noise, frames };
      }, s.slice(4));
      L('lat ' + s.slice(4) + ' ' + JSON.stringify(r));
      continue;
    }
    if (s.startsWith('hlat:')) {  // baseline: host's own 1P key -> change in its own canvas (no network, no codec)
      const r = await host.evaluate(async code => {
        const p = BVN.player(), cv = p.shadowRoot.querySelector('canvas');
        let v = window.__hv;
        if (!v) { v = window.__hv = document.createElement('video'); v.muted = true; v.srcObject = cv.captureStream(30); await v.play(); }
        const c = document.createElement('canvas'); c.width = 900; c.height = 600;
        const x = c.getContext('2d', { willReadFrequently: true });
        const X0 = 0, Y0 = 330, W = 340, H = 250;  // left half, floor level (P1 side)
        const snap = () => { x.drawImage(v, 0, 0, 900, 600); return x.getImageData(X0, Y0, W, H).data; };
        const diff = (a, b) => { let n = 0; for (let i = 0; i < a.length; i += 8) if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) > 90) n++; return n; };
        const frame = () => new Promise(r => v.requestVideoFrameCallback(() => r()));
        let base = snap(), noise = 0;
        for (let i = 0; i < 12; i++) { await frame(); const d = snap(); noise = Math.max(noise, diff(base, d)); base = d; }
        await frame(); base = snap();
        const kc = code.charCodeAt(3);
        const ev = t => p.dispatchEvent(new KeyboardEvent(t, { code, key: code[3].toLowerCase(), keyCode: kc, which: kc, bubbles: true, composed: true }));
        p.focus();
        const t0 = performance.now();
        ev('keydown');
        let ms = -1, n = 0, frames = 0;
        while (performance.now() - t0 < 1500) {
          await frame(); frames++;
          n = diff(base, snap());
          if (n > noise * 2 + 40) { ms = performance.now() - t0; break; }
        }
        await new Promise(r => setTimeout(r, 300));
        ev('keyup');
        return { ms: Math.round(ms), n, noise, frames };
      }, s.slice(5));
      L('hlat ' + s.slice(5) + ' ' + JSON.stringify(r));
      continue;
    }
    if (s === 'rtc') {
      for (const [n, pg] of [['host', host], ['guest', guest]]) {
        const r = await pg.evaluate(async () => {
          const out = {};
          for (const pc of window.__rp.pcs()) (await pc.getStats()).forEach(s => {
            if (s.type === 'outbound-rtp' && s.kind === 'video') out.out = { w: s.frameWidth, h: s.frameHeight, fps: s.framesPerSecond, enc_ms: s.framesEncoded ? +(1000 * s.totalEncodeTime / s.framesEncoded).toFixed(1) : null, limit: s.qualityLimitationReason, kbps: null, codec: s.codecId, bytes: s.bytesSent };
            if (s.type === 'inbound-rtp' && s.kind === 'video') out.inV = { w: s.frameWidth, fps: s.framesPerSecond, jb_ms: s.jitterBufferEmittedCount ? +(1000 * s.jitterBufferDelay / s.jitterBufferEmittedCount).toFixed(1) : null, dec_ms: s.framesDecoded ? +(1000 * s.totalDecodeTime / s.framesDecoded).toFixed(1) : null, dropped: s.framesDropped, bytes: s.bytesReceived };
            if (s.type === 'inbound-rtp' && s.kind === 'audio') out.inA = { energy: s.totalAudioEnergy, level: s.audioLevel, bytes: s.bytesReceived };
            if (s.type === 'candidate-pair' && s.nominated && s.state === 'succeeded') out.pair = { rtt_ms: s.currentRoundTripTime * 1000 };
          });
          return out;
        });
        L('rtc ' + n + ' ' + JSON.stringify(r));
      }
      continue;
    }
    if (s.startsWith('eval:')) { L('eval ' + JSON.stringify(await guest.evaluate(s.slice(5)))); continue; }
    const [who, ks0] = s.split(':', 2).length === 2 && /^[hg]$/.test(s[0]) ? [s[0], s.slice(2)] : ['h', s];
    const pg = who === 'g' ? guest : host;
    const m = ks0.match(/^([a-z0-9+]+)(?::(\d+))?(?:\*(\d+))?(?:~(\d+))?$/);
    if (!m) { L('bad step ' + s); continue; }
    const ks = m[1].split('+');
    for (let n = 0; n < (+m[3] || 1); n++) {
      for (const k of ks) { await pg.keyboard.down(key(k)); await sleep(20); }
      await sleep(+m[2] || 140);
      for (const k of [...ks].reverse()) await pg.keyboard.up(key(k));
      await sleep(m[4] !== undefined ? +m[4] : 260);
    }
    L('key ' + s);
  }
  await stats();
  fs.writeFileSync(`${out}/log.txt`, log.join('\n') + '\n');
  await browser.close();
})().catch(e => { console.error(e); fs.writeFileSync(`${out}/log.txt`, log.join('\n') + '\nFAIL ' + e + '\n'); process.exit(1); });
