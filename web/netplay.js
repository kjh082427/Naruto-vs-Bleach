// 원격 2P: two browsers play one match over WebRTC, with nothing running on our side but GitHub Pages.
//
// The host runs the game. Its screen (Ruffle canvas.captureStream) and sound (window.__bvnAudioTaps, see the
// audio tap in index.html) go to the guest as two one-way PeerJS media calls. The guest runs no game; it shows
// the video and sends its keys back over a data channel. The host turns them into the game's 2P keys
// (arrows + numpad 1-6) and dispatches them on its Ruffle player.
//
// Matchmaking: PeerJS's free public broker (0.peerjs.com) finds the host by room code (peer id PREFIX + code).
// NAT: PeerJS's default ICE servers (Google STUN + PeerJS's free TURN). Once connected, traffic is browser to
// browser (or via that TURN when a direct path is impossible).
//
// Page contract (index.html): window.BVN = {player(), dropPlayer(), stage, setHint(text)};
// #remote section with data-state idle|hosting|host-live|joining|guest-live and the rp-* elements below.
(function () {
  'use strict';
  const PREFIX = 'bvnvs-rea-2p-';
  const ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';  // no 0/O/1/I
  const CODE_RE = /^[A-Z2-9]{6}$/;
  // host-side 2P keys: [code, key, keyCode, location]
  const P2 = {
    up: ['ArrowUp', 'ArrowUp', 38, 0], down: ['ArrowDown', 'ArrowDown', 40, 0],
    left: ['ArrowLeft', 'ArrowLeft', 37, 0], right: ['ArrowRight', 'ArrowRight', 39, 0],
    b1: ['Numpad1', '1', 97, 3], b2: ['Numpad2', '2', 98, 3], b3: ['Numpad3', '3', 99, 3],
    b4: ['Numpad4', '4', 100, 3], b5: ['Numpad5', '5', 101, 3], b6: ['Numpad6', '6', 102, 3],
  };
  // guest keyboard -> 2P key: the usual 1P keys, or the 2P keys themselves
  const GUEST = {
    KeyW: 'up', KeyS: 'down', KeyA: 'left', KeyD: 'right',
    KeyJ: 'b1', KeyK: 'b2', KeyL: 'b3', KeyU: 'b4', KeyI: 'b5', KeyO: 'b6',
    ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
    Numpad1: 'b1', Numpad2: 'b2', Numpad3: 'b3', Numpad4: 'b4', Numpad5: 'b5', Numpad6: 'b6',
  };

  const $ = id => document.getElementById(id);
  const box = $('remote');
  if (!box || !window.BVN) return;
  const ui = {
    host: $('rp-host'), form: $('rp-join'), input: $('rp-code'), code: $('rp-room-code'),
    copy: $('rp-copy'), leave: $('rp-leave'), status: $('rp-status'), ping: $('rp-ping'), keyDot: $('rp-key'), cover: $('rp-cover'),
  };
  // message over the empty game screen of a guest page (invite link, connecting, disconnected); null hides it
  const cover = (title, line) => {
    ui.cover.hidden = !title;
    ui.cover.replaceChildren(...(title ? [Object.assign(document.createElement('b'), {textContent: title}), line] : []));
  };
  let dotTimer = 0;
  const blink = () => {  // shows on both sides that a key went through (guest: sent, host: received)
    ui.keyDot.hidden = false; ui.keyDot.classList.add('on');
    clearTimeout(dotTimer); dotTimer = setTimeout(() => ui.keyDot.classList.remove('on'), 300);
  };
  const state = s => { box.dataset.state = s; };
  const say = (text, bad) => { ui.status.textContent = text; ui.status.classList.toggle('bad', !!bad); };
  const showPing = ms => { ui.ping.textContent = ms == null ? '' : '핑 ' + Math.round(ms) + 'ms'; };
  window.__rp = {log: []};  // test hook: connection events, last RTT
  const log = s => { window.__rp.log.push(Math.round(performance.now()) + ' ' + s); };

  let peer = null, conn = null, calls = [], pingTimer = 0;

  function makeCode() {
    const r = crypto.getRandomValues(new Uint8Array(6));
    return Array.from(r, b => ALPHA[b % ALPHA.length]).join('');
  }
  function linkFor(code) { return location.href.split('#')[0] + '#join=' + code; }
  function errText(e) {
    switch (e && e.type) {
      case 'peer-unavailable': return '그 코드의 방이 없어요. 코드를 다시 확인해 주세요.';
      case 'network': case 'server-error': case 'socket-error': case 'socket-closed':
        return '연결 중개 서버에 닿지 못했어요. 인터넷 연결을 확인하고 다시 시도해 주세요.';
      case 'browser-incompatible': return '이 브라우저는 원격 대전을 지원하지 않아요. 크롬이나 엣지를 써 주세요.';
      default: return '연결에 실패했어요' + (e && e.type ? ' (' + e.type + ')' : '') + '. 다시 시도해 주세요.';
    }
  }
  function startPing(c) {
    clearInterval(pingTimer);
    pingTimer = setInterval(() => { if (c.open) c.send({p: performance.now()}); }, 2000);
  }
  function onPingMsg(c, m) {
    if ('p' in m) c.send({q: m.p});
    else if ('q' in m) { window.__rp.rtt = performance.now() - m.q; showPing(window.__rp.rtt); }
  }
  function hangUp() {
    for (const c of calls) { try { c.close(); } catch (e) {} }
    calls = [];
  }
  // Clear the variables before closing: close/disconnect handlers fire synchronously and must see that the
  // object is no longer current (else e.g. the host's 'disconnected' handler re-registers a room being closed).
  function reset() {
    clearInterval(pingTimer);
    hangUp();
    const c = conn, p = peer;
    conn = peer = null;
    if (c) { try { c.close(); } catch (e) {} }
    if (p) { try { p.destroy(); } catch (e) {} }
    showPing(null);
  }

  // ---- host --------------------------------------------------------------------------------------------------

  const held = new Set();
  function press(k, down) {
    const p = BVN.player(), def = P2[k];
    if (!p || !def) return;
    if (down ? held.has(k) : !held.has(k)) return;
    down ? held.add(k) : held.delete(k);
    // Ruffle only takes keys while the player has focus (same as a real keyboard).
    if (down && document.activeElement !== p) p.focus({preventScroll: true});
    const [code, key, keyCode, location] = def;
    p.dispatchEvent(new KeyboardEvent(down ? 'keydown' : 'keyup',
      {code, key, keyCode, which: keyCode, location, bubbles: true, composed: true, cancelable: true}));
  }
  function releaseAll() { for (const k of [...held]) press(k, false); }

  function tuneSender(pc) {
    for (const s of pc.getSenders()) {
      if (!s.track || s.track.kind !== 'video') continue;
      const prm = s.getParameters();
      if (!prm.encodings || !prm.encodings.length) continue;
      const w = s.track.getSettings().width || 900;
      prm.encodings[0].maxBitrate = 3000000;
      prm.encodings[0].maxFramerate = 30;
      if (w > 960) prm.encodings[0].scaleResolutionDownBy = w / 900;  // hi-DPI canvas: send ~900 px wide
      prm.degradationPreference = 'maintain-framerate';               // drop resolution, not frames
      s.setParameters(prm).catch(err => log('setParameters ' + err));
    }
  }
  function sendScreen(guestId) {
    const p = BVN.player();
    const canvas = p && p.shadowRoot && p.shadowRoot.querySelector('canvas');
    if (!canvas || !canvas.captureStream) { say('게임 화면을 찾지 못했어요. 게임이 뜬 뒤 다시 시도해 주세요.', true); return; }
    const screen = canvas.captureStream(30);  // the game runs at 30 fps
    const v = screen.getVideoTracks()[0];
    if (v && 'contentHint' in v) v.contentHint = 'motion';
    const vc = peer.call(guestId, screen, {metadata: {kind: 'video'}});
    calls.push(vc);
    const pc = window.__rp.pc = vc.peerConnection;
    if (pc) pc.addEventListener('connectionstatechange', () => {
      log('host pc ' + pc.connectionState);
      if (pc.connectionState === 'connected') tuneSender(pc);
    });
    // Sound goes in a call of its own: sent in the same stream, the receiver holds the video back to keep it
    // in sync with the (slower) audio, which measured +250 ms of picture delay.
    const sound = new MediaStream();
    for (const tap of window.__bvnAudioTaps || []) for (const t of tap.stream.getAudioTracks()) sound.addTrack(t);
    if (sound.getAudioTracks().length) calls.push(peer.call(guestId, sound, {metadata: {kind: 'audio'}}));
  }

  function host() {
    reset();
    const code = makeCode();
    state('hosting');
    ui.code.textContent = code;
    say('방을 만드는 중…');
    const me = peer = new Peer(PREFIX + code);
    peer.on('open', () => {
      log('host open ' + code);
      say('코드나 링크를 상대에게 보내 주세요. 상대가 들어오면 바로 연결돼요.');
    });
    peer.on('error', e => {
      log('host error ' + e.type);
      if (e.type === 'unavailable-id') return host();  // code clash: draw another
      if (e.type === 'peer-unavailable') return;       // guest vanished before the call
      say(errText(e), true);
    });
    peer.on('disconnected', () => {  // lost the broker (not the guest): re-register so the room stays findable
      setTimeout(() => { if (peer === me && me.disconnected && !me.destroyed) me.reconnect(); }, 1000);
    });
    peer.on('connection', c => {
      if (conn && conn.open) {  // one guest per room
        c.on('open', () => { c.send({full: 1}); setTimeout(() => c.close(), 500); });
        return;
      }
      conn = c;
      c.on('open', () => {
        log('host conn open ' + c.peer);
        state('host-live');
        say('연결됐어요! 메뉴에서 ‘VS 사람’을 고르세요(‘일반 대전’은 컴퓨터와 싸우는 모드라 상대가 못 들어와요). 이 창을 내리거나 탭을 바꾸면 상대 화면도 멈춰요.');
        sendScreen(c.peer);
        startPing(c);
        const p = BVN.player();
        if (p) p.focus({preventScroll: true});
      });
      c.on('data', m => {
        if (!m || typeof m !== 'object') return;
        if ('k' in m) { blink(); press(m.k, !!m.d); }
        else if ('up' in m) releaseAll();
        else onPingMsg(c, m);
      });
      const gone = () => {
        if (conn !== c) return;
        log('host conn closed');
        releaseAll();
        hangUp();
        conn = null;
        clearInterval(pingTimer);
        showPing(null);
        state('hosting');
        say('상대가 나갔어요. 같은 코드로 다시 들어올 수 있어요.');
      };
      c.on('close', gone);
      c.on('error', gone);
    });
  }

  // ---- guest -------------------------------------------------------------------------------------------------

  const down = new Set();
  let video = null, sound = null;
  function send(m) { if (conn && conn.open) conn.send(m); }
  function key(e, isDown) {
    if (box.dataset.state !== 'guest-live') return;  // (the code box is hidden while live, so typing there is not an issue)
    const k = GUEST[e.code];
    if (!k) return;
    e.preventDefault();
    if (e.repeat || (isDown ? down.has(k) : !down.has(k))) return;
    isDown ? down.add(k) : down.delete(k);
    send({k, d: isDown ? 1 : 0});
    blink();
  }
  addEventListener('keydown', e => key(e, true), true);
  addEventListener('keyup', e => key(e, false), true);
  addEventListener('blur', () => { if (down.size) { down.clear(); send({up: 1}); } });

  function showVideo(stream) {
    BVN.dropPlayer();  // from now on the guest only watches the host's game
    if (!video) {
      video = document.createElement('video');
      video.className = 'rp-video';
      video.playsInline = video.autoplay = video.muted = true;  // picture only; the sound has its own element
      BVN.stage.appendChild(video);
    }
    video.srcObject = stream;
    video.play().catch(() => {});
  }
  function playSound(stream) {
    if (!sound) sound = new Audio();
    sound.srcObject = stream;
    sound.play().catch(err => {  // autoplay with sound refused: start it on the next click
      if (err.name !== 'NotAllowedError') return;
      say('소리가 막혀 있어요. 화면을 한 번 클릭하면 켜져요.');
      BVN.stage.addEventListener('pointerdown', () => sound.play().catch(() => {}), {once: true});
    });
  }
  function dropMedia() {
    if (video) { video.remove(); video = null; }
    if (sound) { sound.pause(); sound.srcObject = null; sound = null; }
  }
  function tuneReceiver(pc) {
    for (const r of pc.getReceivers()) {
      if ('playoutDelayHint' in r) r.playoutDelayHint = 0;  // Chrome: render as soon as decoded
      if ('jitterBufferTarget' in r) r.jitterBufferTarget = 0;
    }
  }

  function join(raw) {
    const code = String(raw || '').trim().toUpperCase();
    if (!CODE_RE.test(code)) { say('방 코드는 영문·숫자 6자예요.', true); ui.input.focus(); return; }
    reset();
    state('joining');
    ui.code.textContent = code;
    say('방에 연결하는 중…');
    if (!BVN.player()) cover(code, '방에 연결하는 중…');
    peer = new Peer();
    peer.on('open', () => {
      const c = peer.connect(PREFIX + code, {reliable: true});
      conn = c;
      c.on('open', () => { log('guest conn open'); say('화면을 받는 중…'); startPing(c); });
      c.on('data', m => {
        if (!m || typeof m !== 'object') return;
        if (m.full) {
          reset();
          state('idle');
          say('이미 두 명이 대전 중인 방이에요.', true);
          if (!BVN.player()) cover(code, '이미 두 명이 대전 중인 방이에요.');
          return;
        }
        onPingMsg(c, m);
      });
      c.on('close', () => {
        if (conn !== c) return;
        log('guest conn closed');
        state('idle');
        reset();
        dropMedia();
        say('방장과의 연결이 끊겼어요. 코드를 다시 넣으면 재참가, 새로고침하면 혼자 하기예요.', true);
        cover('연결 끊김', '코드를 다시 넣으면 재참가, 새로고침하면 혼자 하기예요.');
      });
    });
    peer.on('call', mc => {
      calls.push(mc);
      mc.answer();  // receive only
      const kind = mc.metadata && mc.metadata.kind;
      mc.on('stream', s => {  // PeerJS fires this once per track with the same stream
        tuneReceiver(mc.peerConnection);
        if (kind === 'audio') { if (!sound || sound.srcObject !== s) playSound(s); return; }
        if (video && video.srcObject === s) return;
        log('guest stream v' + s.getVideoTracks().length + ' a' + s.getAudioTracks().length);
        window.__rp.pc = mc.peerConnection;
        cover(null);
        showVideo(s);
        state('guest-live');
        BVN.setHint('키보드는 방장 게임의 2P로 들어가요. 1P 키(WASD, J K L U I O) 그대로 누르면 돼요.');
        say('연결됐어요! 내 키보드가 2P예요. 키를 누르면 위 ‘● 입력’이 깜박여요. 방장이 메뉴에서 ‘VS 사람’을 골라야 2P로 함께 싸울 수 있어요(‘일반 대전’은 컴퓨터와 싸우는 모드).');
      });
    });
    peer.on('error', e => {
      log('guest error ' + e.type);
      state('idle');
      reset();
      dropMedia();
      say(errText(e), true);
      if (!BVN.player()) cover(code, errText(e));
    });
  }

  // ---- wiring ------------------------------------------------------------------------------------------------

  ui.host.addEventListener('click', host);
  ui.form.addEventListener('submit', e => { e.preventDefault(); join(ui.input.value); });
  ui.input.addEventListener('input', () => { ui.input.value = ui.input.value.toUpperCase().replace(/[^A-Z0-9]/g, ''); });
  ui.copy.addEventListener('click', () => {
    const link = linkFor(ui.code.textContent);
    const done = () => { ui.copy.textContent = '복사됨'; setTimeout(() => { ui.copy.textContent = '링크 복사'; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(link).then(done, () => prompt('이 링크를 보내 주세요', link));
    else prompt('이 링크를 보내 주세요', link);
  });
  ui.leave.addEventListener('click', () => {
    const guest = box.dataset.state === 'joining' || box.dataset.state === 'guest-live';
    releaseAll();
    reset();
    if (guest) { location.href = location.href.split('#')[0]; return; }  // reload the page with its own game
    state('idle');
    say('');
  });
  addEventListener('pagehide', reset);

  if (typeof Peer !== 'function') { ui.host.disabled = true; say('연결 모듈을 불러오지 못했어요.', true); return; }
  const m = location.hash.match(/join=([A-Za-z0-9]{6})/);
  if (m) {  // opened from a shared link: index.html did not start the game; wait for a click (autoplay needs it)
    ui.input.value = m[1].toUpperCase();
    state('idle');
    say('방 코드가 입력돼 있어요. ‘참가’를 누르세요.');
    cover(ui.input.value, '원격 2P 초대예요. ‘참가’를 누르면 방장 화면이 여기 나와요.');
    ui.input.focus();
  }
  window.__rp.pcs = () => calls.map(c => c.peerConnection);  // test hook
})();
