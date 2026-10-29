# Bleach vs Naruto 2.6 — 분석 결과

- 원본: 5DPlay 제작, 4399 배포, `V 2.6` (2016/6/23), ActionScript 2 (AVM1), 600×400, 30fps
- 출처: https://vidkidz.tistory.com/2942 (블로그 첨부 파일 일부) + `swfs.waflash.io/uploads/bleachvsnaruto26/` (전체 폴더 구조)
- 개인 학습/모딩 용도. 원저작물(5DPlay, 원작 IP) 재배포 금지.

## 폴더

| 경로 | 내용 |
|---|---|
| `game/` | 실행 가능한 복원 세트: `game.swf`, `fighter/*.swf`(36), `fighter/fz/*.swf`(26), `music/*.mp3`(11), Ruffle 웹 플레이어(`index.html`) |
| `analysis/<이름>/scripts/` | FFDec 26.4.0으로 추출한 AS2 소스 (`game` + 캐릭터 28개) |
| `analysis/<이름>/dump.txt` | FFDec `-dumpSWF` 태그 덤프 |
| `source/blog-kakao/` | 블로그 첨부 원본 (표준 CWS) |
| `source/waflash-dmc/` | waflash 원본 (DMC 변조) |
| `tools/` | FFDec, `undmc.py`, `swfnames.py`, `funcs.py`, Ruffle desktop, headless Chrome(+로컬 lib), `serve.sh` |

실행: `tools/serve.sh` → 브라우저에서 `http://127.0.0.1:8765/`

## 1. waflash "DMC" 변조

waflash가 서빙하는 SWF 전부(62개)는 일반 디컴파일러가 열 수 없게 변조되어 있다.

- 시그니처 `CWS` → `DMC`
- zlib 해제 후 본문에서 프레임 헤더(RECT + frame rate + frame count) 바로 뒤에 45바이트 삽입, 헤더 길이 필드도 +45

`tools/undmc.py`로 복원. 블로그 원본과 겹치는 29쌍 모두 헤더+본문 바이트 동일 검증 완료.

## 2. 전체 구조

```
game.swf (엔진, 메뉴, 맵, 공용 이펙트 XG_*, 선택 화면)
 ├─ frame_6  : 캐릭터 등록부 addFighterData / addFighterClone, 맵 등록부 addMapData
 ├─ frame_7  : 전역 설정 (키 매핑, maxhp=1000, 시간, 폴더 경로, 스토리 모드 순서), SharedObject "bvn_5d"
 ├─ frame_8  : 엔진 함수 (bsd/bsw 필살 암전, yfgj 보조 호출, addChildXG 이펙트, addStgHit, chushi 초기화, KO 처리)
 ├─ DefineSprite_1477 : 캐릭터 선택 화면 (40칸)
 ├─ DefineSprite_1480 : 보조(fz) 선택 화면 (26칸)
 ├─ DefineSprite_1505 : 맵 선택 화면 (10칸)
 └─ DefineSprite_1900 : 로더 (MovieClipLoader)
       fighter/<url>     → _root.game.p1 / p2
       fighter/fz/<fzurl> → _root.game.p1fz / p2fz
       music/<mp3>        → stageSound
```

로딩 순서: p1 → p2 → p1 보조 → p2 보조 → 음악. 그 후 `WKframe`이 있으면 캐릭터 루트를 해당 프레임으로 (卍解/九尾 등 같은 SWF 내 변신), 마지막으로 `initCtrl(isCPU)` 호출.

## 3. 캐릭터 등록 (game.swf frame_6)

```as
addFighterData("卡卡西",{name:"旗木·卡卡西",url:"Kakashi.swf",fz:"我爱罗",vs:["宁次","鼬"],isNaruto:true,says:[...]});
addFighterClone("一护万解","一护",{name:"黑崎·一护 卍解",WKframe:2,vs:[...]});
```

| 필드 | 의미 |
|---|---|
| id (첫 인자) | 선택 화면 무비클립 인스턴스 이름과 같아야 함 |
| `name` | 표시 이름 |
| `url` | `fighter/` 아래 캐릭터 SWF |
| `fzurl` | `fighter/fz/` 아래 보조 SWF (보조로 선택 가능한 경우) |
| `fz` | 스토리 모드에서 CPU가 쓰는 보조 id |
| `vs` | 스토리 모드 후반 상대 목록 |
| `isNaruto` | 진영 (음악/맵/스토리 분기, 아이콘 좌우 반전) |
| `WKframe` | 캐릭터 루트 프레임 번호 (같은 SWF의 다른 형태) |
| `map`, `music`, `says` | 전용 맵, 전용 BGM, 대사 |

선택 화면 칸: 선택 스프라이트에 배치된 무비클립. **인스턴스 이름 = 캐릭터 id**, 위치 `x/30, y/30`이 격자 좌표, 아이콘은 `namemc.gotoAndStop(id)` (id 이름의 프레임 라벨), 초상은 `face.slt = id`.

→ 새 캐릭터 추가 = ① frame_6에 등록 줄 추가 ② 1477에 칸(인스턴스) 추가 ③ 아이콘/초상 스프라이트에 id 라벨 프레임 추가 ④ `fighter/` 에 SWF 배치.
→ 기존 캐릭터 편집 = 해당 SWF만 수정 (game.swf 무수정).

## 4. 캐릭터 SWF 템플릿 (23명 공통)

메인 캐릭터 23명 모두 **동일한 70개 함수**로 구성 (`tools/funcs.py`로 확인, 奇拉比만 +1). 즉 공통 템플릿을 복제해서 만든 구조.

```
캐릭터 루트 (_root.game.p1)
 ├─ initCtrl(ai), updateGJL, moveX/Y, showdow
 ├─ gjl1, gjl2, ... : 형태(프레임)별 공격력 테이블
 └─ mc  (상태머신 + 애니메이션, 예: Kakashi DefineSprite_710)
     ├─ 이동/피격/방어/대시/변신/보조호출/AI: on_enterframe, onBeHit, loseHp, dash, doWanKai, zhaoHuan ...
     ├─ 입력 컨트롤러 (Kakashi DefineSprite_9): doAllAction → gotoAndPlay("라벨")
     ├─ bdmn  : 피격 판정 영역
     ├─ jiao  : 발(착지) 판정
     ├─ AImain: AI 사거리 판정 (kanmian, zh1mian, bsmian ...)
     └─ <기술>atm : 공격 프레임마다 배치되는 공격 판정 (k1atm, kj1atm, zh1atm, bsatm, cbsatm ...)
```

### 입력 → 기술 → 라벨

엔진이 `mc`에 키를 주입: `上 下 左 右 斩(J) 跳(K) 冲(L) 招(U) 必杀(I) 换(O)`, `hp = maxhp`.

입력 판정은 `DefineSprite_9`(Kakashi 기준)의 각 함수에 있음. 사람 조작 조건만 정리:

| 입력 (1P) | 라벨 | 필요 기(ql) | gjl 키 |
|---|---|---|---|
| J | 砍1→砍2→砍3 (콤보) | — | k1, k2, k3 |
| S+J | 砍技1 | — | kj1 |
| W+J | 砍技2 | — | kj2 |
| U | 招1 | — | zh1 |
| S+U | 招2 | — | zh2 |
| W+U | 招3 | — | zh3 |
| I | 必杀 | 100 | bs |
| W+I | 上必杀 | 100 | bs2 |
| S+I | 超必杀 | 300 | cbs |
| J+K | 万解 (변신 보유 캐릭터) | 300 | — |
| O | 招换 (보조 호출) | — | — |
| K / L / S / S+L | 跳 / 瞬步 / 防御 / 숨기(hide) | — | — |
| 공중 J / U / I | 跳砍 / 跳招 / 空中必杀 | I: 100 | tk, tz |

같은 함수들 안에 CPU용 분기(`useAI`)가 있어서, AI는 `AImain`의 사거리 판정 + 난수로 같은 기술을 고른다.

### 필수 애니메이션 라벨 (23명 전원 보유, 32개)

`站立 走 瞬步 跳 落 跳2 落2 落地 跳砍 跳招 砍1 砍2 砍3 砍技1 砍技2 招1 招2 招3 必杀 上必杀 超必杀 招换 防御 防御2 防住 被打 击飞 击落地 起身 开场 胜利 失败`

선택 확장: `万解`(9명), `砍4`(14), `空中必杀`(13) 등.

### 공격력 테이블 (gjl)

```as
gjl1.k1pw = 30;    // 대미지
gjl1.k1zl = 2;     // 피격 강도/종류
gjl1.k1up = 0;     // 수직 넉백
gjl1.k1x  = 3;     // 수평 넉백
gjl1.k1tm = 300;   // 경직 ms
gjl1.k1dz = "被打"; // 상대 피격 모션 (被打 / 击飞)
```

### 그래픽

비트맵 스프라이트 방식 — 알파 PNG(`DefineBitsLossless2`)를 Shape로 감싸 프레임마다 배치. Kakashi 335장, Kenshin 1215장. FFDec로 이미지 단위 추출/교체 가능.

### 보조(fz) SWF

별도의 단순 구조 (함수 `showdow`만). 엔진의 `yfgj()`가 위치를 잡고 `gotoAndPlay(2)`로 재생, `removeFZ()`로 정리.

## 5. 실행 검증 (Ruffle 0.8.0-nightly.2026.10.29 웹, headless Chrome 156, REA)

- 타이틀 → 조작법 → 캐릭터 선택 → 보조 선택 → 맵 → 대전까지 진행 확인 (REA Evidence `ev_61729a0e…`)
- 로드된 파일: `fighter/yihu.swf`, `fighter/shouju.swf`, `fighter/fz/kon.swf`, `fighter/fz/woailuo.swf`, `music/village.mp3` 모두 200
- 콘솔: 폰트 대체(SimSun 등), `System.security.allowDomain` 스텁, MP3 프레임 경고 — 치명적 오류 없음

## 6. 알려진 공백

- 서버에 없는 파일: `music/pubu.mp3`, `music/water.mp3` (해당 맵 BGM만 없음, 게임은 계속 진행)
- 대전 중 각 기술 동작, AI, 변신 등은 정적 분석만 했고 런타임에서 개별 검증하지 않음
- 데스크톱 Ruffle(`tools/ruffle-desktop`)은 `libasound2` 미설치로 미실행 (`sudo apt install libasound2t64` 필요)
- 4399 API(`AS2_4399_API.Bridge`)는 로컬에서 미동작이나 게임 진행에 영향 없음

## 7. Performance

측정 도구: `tools/perf/perf.html` (`dist/`에 복사해서 사용, `?quality=&renderer=&w=&k=&swf=&start=&dur=`) — requestAnimationFrame 간격으로 FPS와 끊김(50/100ms 초과 프레임)을 기록. 측정 환경은 headless Chrome + SwiftShader(소프트웨어 WebGL)라 절대값은 실제 GPU보다 낮고, 조건 간 비교용이다. 실행마다 ±20% 정도 흔들리므로 큰 차이만 신뢰.

| 조건 (900×600) | 타이틀 FPS / >100ms | 대전 FPS / >50ms / >100ms |
|---|---|---|
| 원본 설정 (cacheAsBitmap, quality high) | 5.6 / 57 | 17.7 / 108 / 10 |
| cacheAsBitmap 제거, high | 11.9 / 11 | — |
| quality low만 | 12.1 / 9 | 23.3 / 55 / 0 |
| **cacheAsBitmap 제거 + low (현재 빌드)** | **21.1 / 0** | **26.4 / 26 / 1** |
| quality medium | 5.3 / 54 (high와 차이 없음) | — |
| renderer webgl + medium | — | 14.5 / 110 / 35 (wgpu-webgl 유지) |
| 1350×900 직접 렌더 vs 900×600 + CSS scale(1.5) | 9.8 vs 15.4 | — |

적용한 것 (`tools/build.py` PERF_FIXES, `tools/ruffle_config.json`):
- `frame_2`: `_root.cacheAsBitmap = true` 제거 — 계속 바뀌는 전체 스테이지를 매 프레임 비트맵으로 다시 캐싱하던 설정.
- `frame_8 shadowEffect`: 잔상 BitmapData를 페이드아웃 시 `dispose()` (기존엔 해제하지 않아 누적).
- Ruffle `quality: "low"` (안티에일리어싱 끔). 게임 내 화질 메뉴로 높이면 다시 켜진다.
- 페이지: 렌더 박스를 최대 900×600으로 두고 CSS transform으로 확대 (UI 디자이너 담당 `web/index.html`).
