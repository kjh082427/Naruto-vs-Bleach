// 원격 2P edge cases (not deployed; ANALYSIS.md §11): full room, wrong / short code, guest leave + rejoin with a
// held key, host closing the room. Same setup as remote2p.js: node tools/test/remote2p_edge.js http://127.0.0.1:8766/
const { chromium } = require(process.env.PW_MOD);
const url = process.argv[2];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const t0 = Date.now();
const L = s => console.log(((Date.now() - t0) / 1000).toFixed(1) + ' ' + s);
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = async () => (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
  const st = async pg => (await pg.getAttribute('#remote', 'data-state')) + ' | ' + (await pg.textContent('#rp-status'));
  const live = (pg, s, ms = 30000) => pg.waitForFunction(s => document.getElementById('remote').dataset.state === s, s, { timeout: ms });
  const host = await page();
  await host.goto(url); await sleep(2500);
  await host.click('#rp-host');
  await host.waitForFunction(() => /보내 주세요/.test(document.getElementById('rp-status').textContent), null, { timeout: 20000 });
  const code = await host.textContent('#rp-room-code');
  L('room ' + code);

  // guest 1 joins by typing the code on a normal page (its own game is running)
  const g1 = await page();
  await g1.goto(url); await sleep(2500);
  L('g1 before: player=' + await g1.evaluate(() => !!BVN.player()));
  await g1.fill('#rp-code', code.toLowerCase());
  await g1.click('#rp-join button');
  await live(g1, 'guest-live');
  L('g1 live: player=' + await g1.evaluate(() => !!BVN.player()) + ' video=' + await g1.evaluate(() => !!document.querySelector('.rp-video')));
  L('host: ' + await st(host));

  // guest 2: room is full
  const g2 = await page();
  await g2.goto(url + '#join=' + code); await sleep(800);
  await g2.click('#rp-join button');
  await sleep(6000);
  L('g2: ' + await st(g2));

  // guest 3: wrong code
  const g3 = await page();
  await g3.goto(url); await sleep(1500);
  await g3.fill('#rp-code', 'ZZZZ22');
  await g3.click('#rp-join button');
  await sleep(6000);
  L('g3: ' + await st(g3) + ' player=' + await g3.evaluate(() => !!BVN.player()));
  await g3.fill('#rp-code', 'AB1');
  await g3.click('#rp-join button');
  L('g3 short: ' + await st(g3));

  // g1 holds a key, then leaves: the host must release it and wait for a new guest
  await g1.keyboard.down('KeyD'); await sleep(300);
  await Promise.all([g1.waitForNavigation(), g1.click('#rp-leave')]);
  await sleep(2500);
  L('g1 after leave: ' + await st(g1) + ' player=' + await g1.evaluate(() => !!BVN.player()) + ' url=' + g1.url());
  L('host: ' + await st(host));

  // g1 rejoins with the same code
  await g1.fill('#rp-code', code);
  await g1.click('#rp-join button');
  await live(g1, 'guest-live');
  L('g1 rejoined: ' + await st(g1));
  await sleep(1500);
  L('host: ' + await st(host));

  // host closes the room
  await host.click('#rp-leave');
  await sleep(4000);
  L('host after leave: ' + await st(host));
  L('g1: ' + await st(g1) + ' video=' + await g1.evaluate(() => !!document.querySelector('.rp-video')));
  await browser.close();
})().catch(e => { console.error('FAIL', e); process.exit(1); });
