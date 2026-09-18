#!/bin/sh
# _dev/ogtmp/*.html 을 1200x630 PNG 로 찍어 assets/og/ 에 넣는다.
# 먼저 perl _dev/ogbuild.pl . 을 돌려 템플릿을 새로 만들 것.
#
# 헤드리스로 찍어도 되는 이유: 이 템플릿은 파일을 읽지 않는 정적 HTML 이다.
# (파일을 읽는 검사 페이지는 헤드리스에서 결과가 들쭉날쭉하니 실제 창으로 띄울 것)
set -e
cd "$(dirname "$0")/.."
ROOT="$(pwd -W 2>/dev/null || pwd)"
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"

mkdir -p assets/og
n=0
for f in _dev/ogtmp/*.html; do
  slug=$(basename "$f" .html)
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=1 --window-size=1200,630 \
    --screenshot="$ROOT/assets/og/$slug.png" \
    "file:///$ROOT/_dev/ogtmp/$slug.html" >/dev/null 2>&1
  [ -f "assets/og/$slug.png" ] || { echo "실패: $slug"; exit 1; }
  n=$((n+1))
done
echo "OG 이미지 $n 개 생성"
ls -1 assets/og | wc -l | sed 's/^/assets\/og 파일 수: /'
du -sh assets/og | sed 's/^/전체 용량: /'
