#!/bin/sh
# 검사 페이지를 실제 크롬 창으로 띄운다. 결과는 창 제목에 실린다.
#
#   bash _dev/run.sh selftest edge layout ...
#
# 헤드리스로 돌리지 말 것: 파일을 읽는 검사는 헤드리스에서 읽기가 끝나기 전에
# 판정이 나 버려 결과가 들쭉날쭉하다.
# 검사끼리 언어 설정이 새지 않도록 검사마다 프로필을 따로 쓴다.
#
# 주의: paths·gaps 처럼 PDF 미리보기를 보는 검사는 한 번에 하나씩 돌릴 것.
# pdf.js 1.3MB 를 파일 적재 뒤에 내려받는 구조라, 창을 여러 개 띄우면
# 그 사이에 판정이 나 버려 "썸네일 0장" 으로 거짓 실패한다.
# (실제로 5개를 한꺼번에 띄웠다가 paths 가 12/15 로 나왔고, 단독 실행에서는 15/15 였다)
#
# 2026-09-29에 밝혀진 더 큰 이유: pdf.js 의 캔버스 렌더는 requestAnimationFrame 으로
# 이어 그린다. 크롬은 창이 다른 창에 완전히 가려지면(occluded) rAF 를 멈추므로,
# 그 순간 렌더가 끝나지도 실패하지도 않고 영영 멈춘다 — 미리보기가 0장이 된다.
# 아래 세 플래그가 그것을 막는다. 제품의 문제가 아니라 검사 환경의 문제다.
# (원본 PDF·pdf-lib 왕복본·새로 만든 PDF 셋 다 이 플래그만 넣으면 정상 렌더된다)
set -e
cd "$(dirname "$0")/.."
ROOT="$(pwd -W 2>/dev/null || pwd)"
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"

for name in "$@"; do
  [ -f "_dev/$name.html" ] || { echo "없는 검사: $name"; exit 1; }
  # nohup + disown 이 없으면 이 스크립트가 끝날 때 크롬이 같이 죽는다.
  # (창이 떴다가 결과를 읽기도 전에 사라진다)
  nohup "$CHROME" --user-data-dir="$ROOT/_dev/.prof-$name" \
    --allow-file-access-from-files --no-first-run --no-default-browser-check \
    --disable-features=ChromeWhatsNewUI \
    --disable-backgrounding-occluded-windows --disable-renderer-backgrounding \
    --disable-background-timer-throttling \
    --new-window "file:///$ROOT/_dev/$name.html" >/dev/null 2>&1 &
  disown 2>/dev/null || true
done
sleep 2
echo "띄운 검사: $*"
