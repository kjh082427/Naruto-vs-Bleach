# 블리치 VS 나루토 VS 원피스 1.3

## ▶ [플레이](https://kjh082427.github.io/Naruto-vs-Bleach/)

[![전투 화면 — 클릭하면 게임이 실행됩니다](https://raw.githubusercontent.com/kjh082427/Naruto-vs-Bleach/main/docs/screenshots/battle.jpg)](https://kjh082427.github.io/Naruto-vs-Bleach/)

위 사진이나 링크를 클릭하면 브라우저에서 바로 실행됩니다 (설치 필요 없음, PC 브라우저 권장).

- 57인 대전: 블리치 18 · 나루토 22 · 원피스 17 (원피스 15명 이식 + 직접 만든 쥬라큘 미호크·샹크스)
- 원격 2P: 멀리 있는 친구와 1:1 대전 (방 만들기 → 코드/링크 공유, 서버 없이 브라우저끼리 연결)
- 모드: 일반 대전(1인 연속 대전), VS 컴퓨터, VS 사람(2인), 연습 모드

## 조작법

게임 화면을 한 번 클릭해야 키보드가 연결됩니다.

| | 1P | 2P |
|---|---|---|
| 이동 | W A S D | 방향키 |
| 공격 | J | 숫자패드 1 |
| 점프 | K | 숫자패드 2 |
| 대시 | L | 숫자패드 3 |
| 기술 | U | 숫자패드 4 |
| 필살 | I | 숫자패드 5 |
| 보조 소환 | O | 숫자패드 6 |

메뉴: W/S 이동, J 선택. 원피스 캐릭터는 보조 소환을 쓰지 않습니다.

## 내 컴퓨터에서 실행

이 브랜치를 내려받은 폴더에서 정적 웹 서버를 띄우고 브라우저로 엽니다 (`index.html`을 파일로 직접 열면 동작하지 않습니다).

```sh
git clone -b play-game https://github.com/kjh082427/Naruto-vs-Bleach.git
cd Naruto-vs-Bleach
python3 -m http.server 8765
# 브라우저에서 http://localhost:8765/
```

## 파일

| 경로 | 내용 |
|---|---|
| `index.html` | 게임 페이지 (Ruffle 플레이어 설정 포함) |
| `game.swf` | 게임 본체 |
| `fighter/`, `fighter/fz/`, `fighter/op/` | 캐릭터, 보조 캐릭터, 원피스 캐릭터 |
| `music/` | 배경 음악 |
| `ruffle/` | Ruffle 플래시 에뮬레이터 |
| `fonts/`, `assets/` | 한글 폰트 (OFL 라이선스 문서 포함) |

이 브랜치는 실행 파일만 담고 있습니다. 소스, 분석 자료, 빌드 방법은 [`main` 브랜치](https://github.com/kjh082427/Naruto-vs-Bleach/tree/main)에 있습니다.

개인 학습·모딩 목적의 팬 프로젝트이며, 게임과 캐릭터의 권리는 각 원작자(5DPlay/4399, BLEACH, NARUTO, ONE PIECE)에게 있습니다.
