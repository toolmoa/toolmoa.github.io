#!/bin/bash
# 배포된 사이트를 실제로 두들겨 본다. 지금까지 file:// 만 봤다.
BASE="https://toolmoa.github.io"
fail=0; n=0

echo "=== 1. sitemap.xml 에 적힌 주소가 전부 살아 있는가 ==="
urls=$(curl -s "$BASE/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | sed 's|</\?loc>||g')
count=$(echo "$urls" | wc -l | tr -d ' ')
echo "sitemap 주소 $count개"
for u in $urls; do
  n=$((n+1))
  code=$(curl -s -o /dev/null -w '%{http_code}' "$u")
  if [ "$code" != "200" ]; then echo "  [$code] $u"; fail=$((fail+1)); fi
done
[ $fail -eq 0 ] && echo "  전부 200 OK"

echo
echo "=== 2. canonical 이 자기 주소를 가리키는가 ==="
bad=0
for u in $urls; do
  can=$(curl -s "$u" | grep -o '<link rel="canonical" href="[^"]*"' | head -1 | sed 's/.*href="//;s/"//')
  if [ "$can" != "$u" ]; then echo "  어긋남: $u → canonical $can"; bad=$((bad+1)); fi
done
[ $bad -eq 0 ] && echo "  전부 일치" || fail=$((fail+bad))

echo
echo "=== 3. 자산 파일 ==="
for a in assets/style.css assets/i18n.js assets/zip.js assets/vendor/pdf-lib.min.js \
         assets/vendor/pdf.min.js assets/vendor/pdf.worker.min.js assets/vendor/qrious.min.js \
         assets/vendor/xlsx.full.min.js robots.txt sitemap.xml; do
  r=$(curl -s -o /dev/null -w '%{http_code} %{size_download}' "$BASE/$a")
  code=${r%% *}; size=${r##* }
  printf "  %-40s %s %sB\n" "$a" "$code" "$size"
  [ "$code" != "200" ] && fail=$((fail+1))
done

echo
echo "=== 4. 개발 파일이 공개되지 않았는가 (전부 404여야 함) ==="
for a in _dev/full.html _dev/gaps.html _dev/coverage.pl _dev/fixtures/real-a.pdf _dev/jsQR.js CLAUDE.md; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/$a")
  printf "  %-34s %s\n" "$a" "$code"
  [ "$code" = "200" ] && { echo "    ^^ 공개되면 안 된다"; fail=$((fail+1)); }
done

echo
echo "=== 5. 검색엔진 소유확인 파일 ==="
for a in googlec4f6f539f7a3adb4.html naver2024131f843380fc96bfb303e82b628a.html; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/$a")
  printf "  %-46s %s\n" "$a" "$code"
  [ "$code" != "200" ] && fail=$((fail+1))
done

echo
echo "=== 6. 페이지 안의 내부 링크가 전부 살아 있는가 ==="
out=$(bash "$(dirname "$0")/links.sh")
echo "$out" | sed "s/^/  /"
dead=$(echo "$out" | grep -o "깨진 것 [0-9]*" | grep -o "[0-9]*")
fail=$((fail+dead))

echo "=== 7. 외부 요청이 0인가 (업로드 안 함이 이 사이트의 핵심 주장) ==="
ext=0
for u in $urls; do
  hits=$(curl -s "$u" | grep -o '\(src\|href\)="https\?://[^"]*"' | grep -v 'toolmoa.github.io' | grep -v 'schema.org' | grep -v 'www.w3.org')
  if [ -n "$hits" ]; then echo "  $u"; echo "$hits" | sed 's/^/    /'; ext=$((ext+1)); fi
done
[ $ext -eq 0 ] && echo "  외부 자원 참조 없음" || fail=$((fail+ext))

echo
echo "================================"
[ $fail -eq 0 ] && echo "라이브 점검: 문제 없음" || echo "라이브 점검: 문제 $fail 건"
