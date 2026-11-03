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

## 8. 원피스 캐릭터 이식 (블리치 VS 나루토 VS 원피스)

출처: https://vidkidz.tistory.com/3641 "원피스 vs 페어리테일 1.1" — 블로그 첨부 38개(`source/onepiece/blog/`, 표준 CWS, DMC 변조 없음). 스크립트는 `analysis/op/<이름>/`.

- **같은 5DPlay AS2 엔진의 구버전**이다. 원피스 캐릭터 15명 모두 BVN 70개 함수 중 62개를 공유 (`tools/funcs.py` 방식 비교). 빠진 것은 보조 소환(`doZhaoHuan`), 대시 X, 투사체 피격(`getStgHitObj`) 등이라 원피스 캐릭터는 보조(O키)를 쓰지 않는다. 등록부(`addFighterData`)·선택화면(인스턴스 이름 = id)·컷인(`showFace` 라벨) 구조도 동일 → SWF를 그대로 `fighter/op/`에 두고 게임 쪽만 확장.
- 캐릭터가 요구하는 엔진 차이: `_root.HASH == "5dplay_fvo"`가 아니면 스스로 unload → frame_7에 `HASH` 추가. `_root.shake()`(화면 흔들림, 도플라밍고) → frame_8에 `shake`/`shakeIng` 추가(빈 무비클립 onEnterFrame으로 구동). 그 외 `_root.*` 호출은 전부 BVN에 존재. 상디 SWF의 `jie`/`loadingFunc` 블록은 4399 도메인 체크이며 BVN이 `loadingFunc`를 이미 정의해 즉시 return.
- 피격 판정: 원피스 피격 스프라이트(`function getHitObj` + `_fzfsArray`, 15명 동일)에 BVN의 `getStgHitObj`(layer_effect `stgk*_P<n>`)를 추가 — 안 하면 BVN 캐릭터 대부분이 쓰는 `addStgHit` 투사체가 원피스 캐릭터를 통과한다. FFDec `-importScript`로 각 SWF에 적용.
- 게임 쪽 추가 (모두 `tools/build.py` → `add_one_piece`, 원본 `game/` 무수정):
  - 아이콘 1465 / 초상 1346 / 컷인 1676 / 대전 로딩 배너 1983(510×85, 1989 프레임 11의 `p1xg.dt.gotoAndStop(_root.p1selt)`)에 id·라벨 프레임 추가 (`tools/op_assets.py`가 원피스 game.swf 스프라이트 1386·1570을 PNG로 뽑아 `work/op/ui/`에 크기·좌표 맞춤). 초상은 원피스판에 전신 아트가 없어 컷인 아트를 사용. 로딩 배너는 원피스판에 없어 정사각 초상(1306)의 얼굴 띠 + 흐린 배경으로 생성(`roster.json`의 `banner_y`) — 라벨이 없으면 `gotoAndStop`이 무시돼 1프레임(이치고)이 보이던 버그의 수정.
  - 선택화면 1477: 55칸을 11×5 격자로 재배치(열 우선: 블리치 18 → 나루토 22 → 원피스 15, 슬롯 0.86배). 격자 좌표 `int(x/30), int(y/30)`가 겹치지 않게 간격 47/46px. 시작 커서는 이치고(1P)/나루토(2P) — `BVN_SELECT_P1/P2` 환경변수로 테스트용 변경 가능.
  - 등록부: `work/op/roster.json`(한글 이름·대사, vs 목록, 컷인 라벨) → `addFighterData(..., isOnePiece:true, url:"op/<swf>")`. 맵은 지정하지 않음(원피스 맵은 미이식, BVN 맵 사용). 음악 `onepiece*.mp3` 3곡 추가.
  - 타이틀 666: `work/design/out/title_bg_600x400.png`가 있으면 배경 554의 비트맵을 교체하고 기존 캐릭터·로고·VS 레이어(556 579 584 585 578 583 587 589 621)를 빈 도형으로 숨김.
- 런타임 확인 (REA browser scenario, headless Chrome + Ruffle): 루피 vs 테마리 대전 진입, `fighter/op/luffy.swf` 200, 양방향 피격 확인(`ev_dfdd651…` 피격당함, `ev_9a5c7dc…` 공격 명중; 스크린샷 `work/shots/op4`, `op5`). 콘솔의 `XG_jump`/`XG_luodi` 미등록, `voice_hurt*` 사운드 없음 경고는 BVN 원본 캐릭터에서도 동일하게 나는 기존 현상.
- REA 정적 도구(`open_binary`)는 SWF를 지원하지 않아 SWF 내부 분석은 FFDec + 프로젝트 파이썬 도구(`swfnames`, `swfdisplay`, 신규 `swfbounds`)로 수행.

## 9. 새 캐릭터: 쥬라큘 미호크 (리스킨 + 기술 재조립)

자료: `Dracule Mihawk/` (설명, 일러스트 2, 모델링 2, 3D 모바일 게임 스킬 녹화 5개 — 동작 참고용). 요청 파일 목록은 `docs/CHARACTER_REQUEST.md`.

- **베이스 = `yihu.swf`의 만해 폼**(루트 프레임 2, 스프라이트 1180, 컨트롤러 651): 검은 코트+붉은 안감·검은 검·초승달 참격이 미호크와 가장 가깝다. 등록부에서 `WKframe:2`로 만해 폼만 쓰고 `wankai()`를 막아 호로화 변신을 끈다.
- **리스킨**: 만해 폼이 쓰는 비트맵 253장 (`work/mihawk/bankai_map.json`: 라벨별 비트맵/판정 이름, 셰이프→비트맵은 FFDec XML에서) → `work/mihawk/render_sprites.py`가 머리 검게, 중절모·깃털·수염, J 계열 이펙트 보라 / U·I 계열 이펙트 파랑으로 다시 칠함. 캐릭터와 궤적이 한 장에 같이 그려진 비트맵(跳招2)은 보라 사본(`sprites_purple/`)을 따로 만들어 S+J에서 셰이프를 복제해 사용.
- **기술 재배치** (`tools/mihawk.py`): 입력은 컨트롤러 651의 함수(`nornalhit`, `skill1/2`, `magichit1~3`, `bisha*`)가 라벨로 `gotoAndPlay`, 콤보 연결은 공격 프레임마다 놓이는 651 인스턴스의 onClipEvent(enterFrame) "판정 창"이 담당. 라벨 치환으로 S+J→`冲砍`(신규), W+U→`砍技1`(띄우기: gjl `kj1up 12, 击飞`), W+I→`必杀`, 砍3 창에 J→`砍4` 추가, 招2 돌진 속도 6.5→3 (짧은 돌진), 컷인 라벨 `米霍克1/2`.
- **새 라벨 조립**: `砍4`(招3 425–441을 지상 버전으로), `砍5`(上必杀 547–560 + 604–611), `冲砍`(跳招2 151–164). 소스 구간마다 시작 프레임의 표시 목록을 원래 생성 태그(피격 판정 `bdmn`의 `beida()` 클립 액션 포함)로 복원한 뒤 소스 태그를 그대로 재생하고, 판정 이름은 바이트 치환(`zh3atm`→`k4atm` 등, `_fsArray`의 k4/k5/sbs 사용). 원본 판정 창(651)과 프레임 스크립트는 빼고, 이동·콤보 창·종료 스크립트를 마커 DoAction(`"MHK<프레임>"`)으로 넣은 뒤 FFDec `-importScript`로 AS 소스로 교체.
- **목소리**: 스펙트로그램(배음 줄무늬)으로 이치고 음성 27개를 골라(`work/mihawk/voices.json`) 무음으로 교체, 검·타격 효과음은 유지.
- **게임 쪽**: `work/mihawk/fighter.json` → 등록부(`url:"op/mihawk.swf", WKframe:2, fz:"魂"`), 아이콘/초상/로딩 배너/컷인(`work/mihawk/ui/`, `render_ui.py`), 선택 화면 56칸 → 12×5 격자(0.8배, 간격 44px).
- **요루(대검)**: 리스킨에서 칼을 흑도 요루(몸 길이만 한 휜 검은 날, 금색 십자 가드, 흰 손잡이, 파란 보석)로 다시 그림. 칼이 비트맵 밖으로 나가는 59장은 캔버스를 넓히고(`work/mihawk/sprites_pad.json`) `apply_padding`이 해당 사각 도형을 다시 만들어 원래 픽셀 위치를 유지 (첫 채우기 스타일이 빈 65535이고 실제 비트맵이 뒤 스타일에 있는 도형은 1:1 사각형 범위 기준).
- **궁극기 배경 어둡게** (I·W+I `必杀`, S+I `超必杀`): 기본 정지 연출이 끝나는 474/646 프레임(bsw/cbsw 직후)에서 `_root.blackStg()`로 다시 어둡게 하고 `_root.mhDark = pn`(상대 번호라 좌우가 구분됨)으로 소유를 표시. 강타 히트스톱 효과 (`XG_kanx` 등)가 `resumeGame()` → `resumeBlackStg()`로 배경을 되살리므로, 미호크 안의 감시 클립 `mhDarkW`(onEnterFrame)가 기술 프레임(458–526 / 622–726) 동안 정지 중이 아니고 blackMu가 1프레임이면 다시 어둡게 한다. 해제는 동작=0 프레임(495/681), 피격 라벨(被打 786·击飞 799·击落地 811), 站立 루프(2), 감시 클립(기술 프레임 이탈)에서 — 자기 소유이고 `zhanting == false`·blackMu가 2프레임일 때만 `resumeBlackStg()` (상대 기술 정지·일시정지·KO 화면은 건드리지 않음). 누가 KO되면(sw) 소유만 내려놓고 KO 연출(KOend)에 맡김. 코드: `tools/mihawk.py`의 `darken()` / `LIGHTEN` / `DARK_EDITS`.
- **테스트**: `tools/test/autoplay.html` (dist/에 임시 복사) — 키를 지정 시간 누르는 스크립트 입력(`?seq=w16000,s*3,j,...,s+j,...`)으로 헤드리스 키 누락 없이 선택→대전→기술까지 재현. 연습 모드에서 J 5단·S+J·I·S+I 확인.

## 10. 새 캐릭터: 샹크스 (공용 조립 모듈 `tools/fighter_builder.py`)

자료: ` Shanks/` (폴더 이름 앞에 공백: 설명, 일러스트, 모델링 사진, 스킬 이펙트), 카무사리 영상(`샹크스 카무사리.mp4`, 저장소에 없음 → 프레임 `work/shanks/ref/kamusari/`).

- **베이스 = 켄파치** (`game/fighter/jianba.swf`, 애니메이션 스프라이트 514, 컨트롤러 13, 공격 판정 클립 216). 입력→라벨: S+J `skill1`=砍技1, W+J `skill2`=砍技2, U=招1, S+U=招2, W+U=招3, S+I=超必杀 — 컨트롤러 함수를 읽고 확인할 것 (처음에 W+J를 砍技1로 잘못 짚었음).
- **공용 모듈**: 미호크에서 쓰던 조립 방식을 `fighter_builder.py`로 일반화 — `Spec`(베이스·폼·컨트롤러·세그먼트·라벨 치환·스크립트 수정·gjl), `Segment`(소스 프레임 구간 이어 붙이기, 판정 이름 변경, `drop`으로 이동 클립(켄파치 143)·이펙트 제외, 오버레이), `Inject`(기존 프레임에 이펙트 주입: J 검 오라), `fx_alias`(같은 그림 다른 속도), `tints`(켄파치가 흰 이펙트를 노랗게/주황으로 물들이던 색 변환 → 무색/진홍). 이펙트 좌표는 발 기준이라 애니메이션 스프라이트 안에서는 y +24.
- **2배 해상도 스프라이트**: `work/shanks/render_sprites.py`가 역할 지도(외곽선·망토·셔츠·피부·머리…)를 Scale2x 두 번(4배)→다수결로 2배를 만들어 노이즈 없이 다시 칠함(scipy 필요). `apply_padding`은 PNG가 (원본+여백)의 k배이면 도형을 원래 화면 크기로 다시 만들고 1/k로 그림(부드러운 채우기 0x41). 한 비트맵에 여러 프레임이 든 시트(켄파치 6번 = 서기 4프레임, 도형 7–10)는 도형 자신의 사각형을 유지하고 채우기만 옮김(`swftext.bitmap_rect_shape(fill_px=…)`). 사각형이 아닌 도형을 쓰는 339·346은 1배 유지.
- **기술** (`tools/shanks.py`): J 1-2-3-1 반복(砍3 판정 창 233에 J→砍1) + 검붉은 검 오라 / W+J 冲天斩(砍技1 + 대각 상승, 落2로 낙하) / S+J 지상 冲斩(砍技2·21, 순간이동 302–305 제외)·공중 空斩(W+U 참격 상하 반전, 바닥에 닿으면 폭발; 컨트롤러 onJumping에 skill1 추가) / U 霸斩(必杀 기 모으기+참격, zl 16 가드 깨기) / W+U 飞斩(대각 위로 날아가는 참격, 이동 판정) / S+U 霸王色(站立 1–3 + 超必杀1 863–888 정면 자세(비트맵 441/443 새로 그림), 금색 구체 407 제외, 패왕색 돔 판정) / S+I 神避 카무사리(정지·눈 컷인·붉은 독수리·검붉은 번개 → 화면을 덮는 참격, 화면 크기 판정 1개, 섬광·흔들림·어두운 베일). 이펙트 PNG는 `work/shanks/render_fx.py` → `fx/`.
- **게임 쪽**: `work/shanks/fighter.json`(id `香克斯`, fz `魂`) → `tools/build.py` `CUSTOM_FIGHTERS`가 UI(아이콘·초상·배너·컷인 2)를 넣고 `tools/shanks.py`로 `dist/fighter/op/shanks.swf` 생성. 목소리는 켄파치 음성 10개 무음 처리(`voices.json`).
- **미호크 숨은 콤보** (2026-11-03 사용자 요청): J는 3타(砍1–3)까지. `j j j` 직후 1초 안의 `w+j w+j`가 4·5타(砍4·砍5). 그냥 W+J는 원래 砍技2. 구현은 `tools/mihawk.py` `W_J_HIDDEN`: 砍3 판정 창(219)에서 W+J→砍4, 砍3 마지막 프레임(230)과 砍4 마지막 프레임이 `mhJ3`/`mhJ4 = getTimer()`를 찍고, 서 있을 때(doStand/doAllAction) W+J가 1000ms 안이면 砍5/砍4로 간다. **수정(11-03 사용자 제보 "5번째 w+j가 안 나감")**: ① 게임은 눌린 키를 매 프레임 확인만 하므로 砍4 초반(판정 창 전)에 누른 W+J가 사라졌다 → 砍3·砍4 시작 시 감시 클립 `mhBufW`가 새 W+J 입력을 `mhQ`에 기억하고 판정 창이 열리면 바로 다음 타로(`WJ_BUF`). ② 서기 반복의 마지막 프레임(8: `gotoAndStop("站立")`)이 같은 틱에 점프를 되돌리면 컨트롤러가 다음 프레임에 다시 판단하는데, 판단할 때 `mhJ4`를 0으로 지웠기 때문에 두 번째 판단이 砍技2로 갔다 → 도장은 砍4·砍5의 3번째 프레임에서 지움. 검증: 헤드리스 Chromium(Playwright 실제 키 입력) + 테스트 사본에 프레임/키 trace를 넣어 5번째 입력 시점 11가지(砍4 도중 2, 끝난 뒤 0.1–0.9초 9)에서 모두 砍5, 그냥 W+J·6번째 W+J는 砍技2.

## 11. 원격 2P (사용자 요청 "멀리 떨어진 사람과 멀티 대전, 서버비 안 드는 걸로", 2026-11-03)

- **방식: 방장 화면 전송** (스팀 Remote Play Together와 같은 구조). 게임은 방장 브라우저에서만 돌고, 상대는 영상만 받아 보며 키를 돌려보냄. 두 브라우저가 각자 게임을 돌리고 입력만 주고받는 락스텝은 버림: Ruffle은 밖에서 프레임 진행을 맞출 수 없고, 게임 로직에 랜덤과 `getTimer()` 판정(미호크 숨은 콤보 등)이 있어 금방 두 화면이 갈라짐.
- **파일**: `web/netplay.js`(전부), `web/vendor/peerjs-1.5.5.min.js`(+MIT 라이선스), `web/index.html`(원격 2P 패널 `#remote`, 오디오 탭, `window.BVN` 계약, 초대 링크면 게임을 시작하지 않음). 게임 SWF는 수정 없음.
- **연결**: PeerJS 무료 공개 중개 서버(`0.peerjs.com`)에서 방장 peer id = `bvnvs-rea-2p-` + 6자리 코드(0/O/1/I 제외). 상대는 임의 id로 접속해 데이터 채널(신뢰·순서 보장)을 엶. ICE는 PeerJS 기본값(Google STUN + `eu-0/us-0.turn.peerjs.com` 무료 TURN). 방 하나에 상대 1명(두 번째는 `{full:1}` 받고 끊김). 상대가 나가면 방장은 같은 코드로 대기.
- **화면**: Ruffle 플레이어의 shadow DOM(`mode:"open"`) 안 `<canvas>` → `captureStream(30)`(게임 30fps), `contentHint='motion'`, 송신 3Mbps·30fps·`maintain-framerate`, 고해상도(hiDPI) 캔버스는 900px 폭으로 줄여 보냄. 상대 쪽은 `<video muted>`, `playoutDelayHint/jitterBufferTarget = 0`.
- **소리**: `ruffle.js`보다 먼저 `AudioNode.prototype.connect`를 감싸, 스피커(`AudioDestinationNode`)로 가는 연결을 같은 AudioContext의 `MediaStreamDestination`(`window.__bvnAudioTaps`)에도 연결. **소리는 별도 통화**로 보냄: 영상과 같은 스트림에 넣으면 받는 쪽이 립싱크 때문에 영상을 소리에 맞춰 붙잡아 둬서 지터 버퍼가 270~300ms(분리 후 35~70ms), 체감 지연이 600ms대(분리 후 200~400ms, 아래 환경 기준)였음.
- **입력**: 상대 `keydown/keyup`(1P 키 WASD·JKL·UIO 또는 방향키·숫자패드) → `{k, d}` → 방장이 2P 키(`ArrowUp…`, `Numpad1~6`, keyCode 97~102, location 3)의 합성 `KeyboardEvent`를 플레이어에 dispatch. Ruffle은 `isTrusted`를 보지 않지만 **포커스가 있어야** 키를 받으므로 누를 때 포커스를 되돌림. 연결이 끊기거나 상대 창이 포커스를 잃으면 누르고 있던 키를 전부 뗌.
- **측정** (헤드리스 Chromium 2개, 한 PC, 소프트웨어 렌더링이라 게임이 9~12fps로 돎): 중개 서버 경유 접속 2~3초, 데이터 채널 핑 10~50ms, 인코딩 6~7ms·디코딩 3~5ms, 키 → 화면 변화: 로컬(방장 자기 키) 100~250ms vs 원격(상대 키) 200~440ms → 원격 추가분 약 150ms ≈ 이 환경의 1.5프레임 + 지터 버퍼. 실제 PC(30fps)에선 프레임 몫이 1/3로 줄고, 여기에 두 사람 사이 왕복 핑이 더해짐.
- **확인한 것**: 초대 링크/코드 입력 접속, 타이틀 메뉴(일반 대전 → VS 컴퓨터 → **VS 사람** → 연습 모드), 2P 커서 이동·선택(나루토→테마리, 켄파치), 대전에서 상대 키로 걷기·점프·공격, 소리 수신(totalAudioEnergy > 0), 정원 초과·없는 코드·짧은 코드 문구, 상대가 키를 누른 채 나가기(방장 키 해제) → 같은 코드로 재참가, 방장이 방 닫기 → 상대 "연결 끊김". 테스트: `tools/test/remote2p.js`, `remote2p_edge.js`.
- **한계**: 상대 화면이 늦게 보여 방장이 유리. 방장 창을 내리거나 탭을 바꾸면 브라우저가 그리기를 멈춰 상대 화면도 멈춤. 두 사람 다 대칭형 NAT면 무료 TURN에 의존(대역폭·가용성 보장 없음). 상대는 키보드 필요(모바일 터치 버튼 없음). 공개 중개 서버가 내려가면 새 방을 못 만듦(이미 연결된 판은 유지).
