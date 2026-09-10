#!/bin/bash
BASE="https://toolmoa.github.io"
fail=0

echo "=== 8. sitemap 이 실제 페이지 목록과 정확히 일치하는가 ==="
# 저장소에 있는 공개 페이지 목록
repo=$(ls *.html en/*.html 2>/dev/null \
       | grep -v '^google' | grep -v '^naver' \
       | sed 's|^|/|' | sed 's|^/index.html$|/|' | sed 's|^/en/index.html$|/en/|' | sort)
sm=$(curl -s "$BASE/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | sed 's|</\?loc>||g' \
     | sed "s|$BASE||" | sed 's|^$|/|' | sort)
miss=$(comm -23 <(echo "$repo") <(echo "$sm"))
extra=$(comm -13 <(echo "$repo") <(echo "$sm"))
if [ -n "$miss" ];  then echo "  sitemap 에 빠진 페이지:"; echo "$miss" | sed 's/^/    /'; fail=$((fail+1)); fi
if [ -n "$extra" ]; then echo "  실제로 없는데 sitemap 에 있는 것:"; echo "$extra" | sed 's/^/    /'; fail=$((fail+1)); fi
[ -z "$miss" ] && [ -z "$extra" ] && echo "  저장소 $(echo "$repo" | wc -l | tr -d ' ')개 = sitemap $(echo "$sm" | wc -l | tr -d ' ')개, 정확히 일치"

echo
echo "=== 9. 홈에서 모든 툴로 갈 수 있는가 ==="
home=$(curl -s "$BASE/")
missing=0
for t in image-compress image-crop img-to-pdf char-count text-clean pdf-merge pdf-split \
         pdf-edit file-convert qr-generate password-gen unit-convert date-calc age-calc; do
  echo "$home" | grep -q "$t.html" || { echo "  홈에 링크 없음: $t"; missing=$((missing+1)); }
done
[ $missing -eq 0 ] && echo "  툴 14종 전부 홈에서 연결됨" || fail=$((fail+missing))

echo
echo "=== 10. hreflang 이 서로를 가리키는가 ==="
bad=0
for p in index image-compress image-crop img-to-pdf pdf-merge pdf-split file-convert qr-generate; do
  # index 는 canonical 과 맞춰 디렉터리 형태(/ · /en/)를 쓴다
  ko="$BASE/$p.html"; en="$BASE/en/$p.html"
  if [ "$p" = "index" ]; then ko="$BASE/"; en="$BASE/en/"; fi
  koHtml=$(curl -s "$ko"); enHtml=$(curl -s "$en")
  echo "$koHtml" | grep -q "hreflang=\"en\" href=\"$en\"" || { echo "  ko→en 없음: $p"; bad=$((bad+1)); }
  echo "$enHtml" | grep -q "hreflang=\"ko\" href=\"$ko\"" || { echo "  en→ko 없음: $p"; bad=$((bad+1)); }
done
[ $bad -eq 0 ] && echo "  8쌍 전부 양방향 연결" || fail=$((fail+bad))

echo
echo "=== 11. 페이지 용량 (첫 화면에 받는 HTML) ==="
big=0
for u in $(curl -s "$BASE/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | sed 's|</\?loc>||g'); do
  s=$(curl -s -o /dev/null -w '%{size_download}' "$u")
  kb=$((s/1024))
  if [ $kb -gt 60 ]; then printf "  %-52s %sKB  큼\n" "${u#$BASE}" "$kb"; big=$((big+1)); fi
done
[ $big -eq 0 ] && echo "  모든 페이지 60KB 이하"

echo
echo "=== 12. robots.txt ==="
curl -s "$BASE/robots.txt" | sed 's/^/  /'
curl -s "$BASE/robots.txt" | grep -q "Sitemap:" || { echo "  Sitemap 줄 없음"; fail=$((fail+1)); }

echo
echo "================================"
[ $fail -eq 0 ] && echo "추가 라이브 점검: 문제 없음" || echo "추가 라이브 점검: 문제 $fail 건"
