# 진행 상황 (2026-11-02, 커밋 전 — 사용자 확인 후 main 커밋 / play-game 배포 예정)

마지막 커밋: main `5b3c311` (원피스 로딩 배너 수정). 그 뒤 작업은 모두 커밋 전.

## 끝난 것 (확인 대기)
- 쥬라큘 미호크: `tools/mihawk.py`, `work/mihawk/` (리스킨 253장+흑도 요루, UI, S+I 강화: 요루 발광·눈 섬광·대참격 1.3배·화면 흔들림). 빌드에 통합(`tools/build.py` add_mihawk), 선택창 56칸(12×5).
- 버전 1.1: `/VERSION` 파일 → 게임 `_root.ver`, 텍스트 658, `web/index.html`(__VERSION__), 스플래시(`work/design/render_v3.py`). "한글판" 표시 전부 삭제.
- 일반 대전 상대 랜덤: `tools/build.py` RANDOM_STAGE_FIXES / RANDOM_STAGE_AS, `selectableIds`.
- 미호크 궁극기(I, S+I) 시전 중 화면 어둡게 유지 (`tools/mihawk.py` DARK_EDITS + 감시 클립 mhDarkW, ANALYSIS §9). 실제 화면 확인 완료.
- 공용 조립 모듈 `tools/fighter_builder.py` (미호크와 바이트 동일 검증; 단 그 뒤 추가된 mhDarkW 감시 클립은 아직 미이식). 샹크스는 이 모듈로 조립 예정.
- 테스트 도구: `tools/test/autoplay.html` (dist/에 임시 복사해서 사용, 배포 금지).
- 문서: `docs/CHARACTER_REQUEST.md`, `ANALYSIS.md` §9, `README.md` (main용).
- 버그 수정 "일반대전 3~4번째 대전 무한 로딩" (사용자 제보, 미호크 vs 마유리 로딩바 20%에서 정지): 원인 = 플레이 중 내가 빌드하며 8765 서버를 재시작 → 그 순간 대전 파일 요청 실패 → 대전 로더(sprite 1900)는 onLoadError를 trace만 하고 재시도 안 함. 수정 = `tools/build.py` LOADER_RETRY_FIXES(실패 단계 1.5초마다 재시도) + 빌드를 dist.new에 만든 뒤 교체(swap_dist) + `tools/serve.sh --directory`. 서버 15초 끊김 재현 테스트로 수정 전(영구 정지)/후(복구 후 대전 시작) 확인.

## 진행 중
- 샹크스 (베이스 = 켄파치 `game/fighter/jianba.swf`, 스프라이트 514). 자료 폴더는 `/home/kjh08/work/Rea-project/ Shanks/` (이름 앞에 공백), 카무사리 영상은 프로젝트 최상위 `샹크스 카무사리.mp4`.
  - 준비 완료: `work/shanks/label_map.json`, `shape_bitmaps.json`(`tools/label_map.py`), `voices.json`(켄파치 목소리 10개), `fighter.json`(id 香克斯), 카무사리 프레임 `work/shanks/ref/kamusari/`.
  - UI 완료: `work/shanks/render_ui.py` → `work/shanks/ui/` (아이콘·초상·배너·컷인 2).
  - 카무사리 이펙트 완료: `work/shanks/render_fx.py` → `fx/` (eagle 14, lightning 8, slash 12, flash 4, veil 1; layout.json).
  - 이펙트(`render_fx.py` → `fx/`): 카무사리(eagle/lightning/slash/flash/veil), W+U(wu_launch/wu_slash/wu_impact), S+U(haki_ring), J 오라(aura). 오프셋은 "발 기준"이라 애니메이션 스프라이트에서는 y +24 (스프라이트가 캐릭터 안 (-0.65,-23.9)에 놓임).
  - 리스킨 234장 완료 → 사용자 피드백(2026-11-02 15시): 기술은 좋음, 모델링은 별로 — 얼굴 지저분(흉터/수염 제거), 바닥까지 내려오는 긴 검은 망토 강조, 거지 반바지 말고 단정한 진홍 7부 바지+샌들, 그리폰 더 길게. 2차 수정 반영 완료(14:58, 얼굴 흉터 제거·바닥까지 망토·진홍 7부 바지+샌들·SWORD_SCALE 1.4) → 15:10 dist 재빌드, 대전 화면에서 확인, 8765 서버 열어 사용자 확인 대기.
  - 3차 피드백(2026-11-02 15:20): ①화질 너무 낮음 ②망토인데 팔이 하얘서 조끼처럼 보임 ③머리는 조금 긴 빨간 머리 ④사진 참고해 모델링 개선 ⑤S+U 피해 이펙트는 좋음, 모션(한 다리·한 팔 드는 招3)이 유치함 → 기를 내뿜는 모션으로.
    → 리스킨 v3 에이전트: 2배 해상도(339·346 제외), 노이즈 없는 음영, 팔 덮는 망토, 긴 머리, 441/443(S+U 자세) 정리. `tools/fighter_builder.py` apply_padding이 k배 PNG를 1/k로 그리도록 확장(1배일 때 미호크·샹크스 바이트 동일 확인).
    → v3 완료(11-03 01:40): 232장 2배(339·346 1배), 팔 덮는 망토, 긴 머리, 441/443 패왕색 자세 새로 그림. 스프라이트 시트 비트맵(6번=서기 4프레임) 때문에 apply_padding에 부분 사각형 처리 추가(swftext.bitmap_rect_shape fill_px). dist 재빌드 완료, 8765 서버 열림. 브라우저 자동 테스트는 입력이 메뉴에서 씹혀 실패(1회는 9시간 멈춤) → FFDec 도형 렌더로 확인. 약한 부분은 work/shanks/SPRITES_PROGRESS.md.
    → S+U(`tools/shanks.py` haoshoku): 站立 1–3 + 超必杀1 863–888(정면으로 버티고 서서 망토가 휘날리는 자세, 금색 구체 407·cbs4atm 제거).
  - 기술 확정(사용자 승인, U = 가드 깨기 / I·W+I = 켄파치 동작+검붉은 색) → `tools/shanks.py` 구현 완료:
    J 1-2-3-1 루프(砍3 창(프레임 233)→砍1) + 검 오라 주입 / W+J 冲天斩(砍技1 + 대각 상승, 落2로 낙하) / S+J 지상 冲斩(砍技2·21, 순간이동 프레임 302–305 제외) · 공중 空斩(W+U 참격 상하반전, 바닥 닿으면 폭발, 컨트롤러 onJumping에 skill1 추가) / U 霸斩(必杀 기모으기+참격, zl 16 가드 깨기) / W+U 飞斩(참격 발사 + 이동 판정) / S+U 霸王色(招3 + haki_ring + 베일, 솟구치는 이동 클립 143 제거) / S+I 神避.
    켄파치 입력→라벨: W+J skill2 砍技2, S+J skill1 砍技1, U 招1, S+U 招2, W+U 招3, S+I 超必杀.
  - `tools/fighter_builder.py` 추가 기능: Inject(기존 프레임에 오버레이), fx_alias(같은 그림 다른 속도), tints(켄파치가 흰 이펙트를 노랗게 물들이던 색 변환 6곳 → 무색/진홍), Segment.drop(이동 클립 제외).
  - 검증: 연습/대전에서 W+J·U·W+U·J 적중 화면 확인, 오프라인 FFDec 렌더로 空斩·冲天斩·霸斩 확인. 헤드리스 입력은 CPU 부하에 매우 약함(남은 headless chrome이 CPU 500% 먹던 것 정리함).
  - 테스트 빌드: `BVN_DIST=<scratch>/dist BVN_SELECT_P1=香克斯 tools/venv/bin/python tools/build.py` → 8766 포트로 따로 서빙 (사용자 dist 건드리지 않음).

## 다시 시작할 때
1. `tools/venv/bin/python tools/build.py` (dist.new에 빌드 후 dist와 교체) → 서버가 꺼져 있을 때만 `tools/serve.sh`. **사용자가 플레이 중인 8765 서버는 절대 재시작하지 말 것** (재시작 중 대전 로딩이 실패하면 예전 로더는 무한 로딩 → 2026-11-02 버그). 자동 테스트는 dist 복사본을 8766 포트로 따로 띄워서.
2. 중단된 서브 에이전트 작업은 각 스크립트를 다시 실행하거나 위 메모를 보고 이어서 진행.

## 사용자 메모 (2026-11-02)
- 미호크 J 5연타가 너무 강하다는 고민 (단순 J×5 대신 숨겨진 콤보 jjj w+j w+j 또는 jj u w+u s+u 같은 복합 콤보 아이디어, 다른 기술 모션이 J 직후에 달라져 불완전/버그 우려). → **샹크스 완성 후에 의견만 전달. 구현하지 말 것** (샹크스 완성 후 커밋 예정).
- 샹크스 W+U: 위 대각선으로 날아가는 검격, 미호크와 다른 검사로 보이게(검은 속+진홍 테두리, 거친 날, 검은 번개 꼬리, 발사 충격파, 가시형 폭발) — 완료.

## 2026-11-03 새벽 (사용자 취침 중, 판단 위임: "이후부터 판단은 너가 해줘")
- 커밋 `eca6fc8` (main, 미푸시): 미호크·샹크스·1.1. push / play-game 배포는 사용자 확인 후.
- 사용자 요청 1: 샹크스 S+U 정면 모델링 → 441/443을 `샹크스 모델링2.png`에서 따서 다시 그림(에이전트, 완료, dist 반영).
- 사용자 요청 2: 미호크 5단 = `j j j` 후 1초 안에 `w+j w+j` (그냥 W+J는 그대로) → `tools/mihawk.py` W_J_HIDDEN / 砍3 창 W+J→砍4 / 砍4 창 W+J→砍5 / mhJ3·mhJ4 = getTimer(). dist 반영. 헤드리스 브라우저 입력이 메뉴에서 계속 막혀 실제 플레이 확인은 못 함.
- 헤드리스 브라우저 입력: 11-02 15시 이후 메뉴에서 키가 전혀 안 먹음(합성 이벤트·Playwright press 둘 다). 원인 미확인 → 미호크 콤보는 사용자 직접 확인 필요.
- 09:20 사용자 지시: 흰수염은 빼고 미호크·샹크스만 버전 1.2로 main 커밋 + push. 사용자 제보: `j j j w+j`까지는 되는데 5번째 `w+j`(砍5)가 안 나감 → 커밋 후 테스트·수정.
- 커밋 `80e3198` main push 완료, play-game `05ad4f7` 배포(사용자: 앞으로 push할 때 항상 play-game도 같이).
- 미호크 5번째 w+j 수정(커밋 전): 헤드리스 테스트로 원인 2개 확인 — 砍4 초반 입력 유실(입력 버퍼 `WJ_BUF`/`mhQ` 추가), 서기 프레임 8의 되돌림 때문에 두 번째 판단이 砍技2(도장 지우기를 砍4·砍5 3번째 프레임으로). 테스트 도구 `tools/test/pwkeys.js`.

## 원격 2P (커밋 전, 2026-11-03 사용자: "원격 2P라는 모드를 만들고 방 만들고 게임할 수 있게")
- 방장 화면 전송 방식 (ANALYSIS §11): `web/netplay.js` + `web/vendor/peerjs-1.5.5.min.js` + `web/index.html` 원격 2P 패널. 게임 SWF 수정 없음, 서버비 0 (GitHub Pages + PeerJS 무료 중개/TURN).
- 헤드리스 2브라우저 테스트로 접속·VS 사람·캐릭터 선택·대전 조작·소리·예외 상황 확인. 지연 원인 하나(소리를 같은 스트림에 넣으면 립싱크로 영상 +250ms) 찾아서 소리를 별도 통화로 분리.
- `work/design/render_web.py`가 `web/*.js` 문자열도 폰트 서브셋에 넣도록 수정 (netplay.js 안내 문구).
- 남은 것: 사용자가 실제 두 PC(또는 PC 두 브라우저)로 확인 → 커밋 시 버전 올림 → main push + play-game 배포. (흰수염은 제외, 커밋 안 함)
