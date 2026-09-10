#!/bin/bash
# 배포된 사이트의 내부 링크가 전부 살아 있는지 본다.
#
# 이 스크립트에서 두 번 데였다.
#  1) dirname 은 "https://host/" 의 // 를 하나로 뭉갠다. 주소를 직접 잘라 만든다.
#  2) $(함수) 는 서브셸이라 함수 안에서 채운 캐시가 사라진다. 파일에 적는다.
#     캐시가 없으니 같은 주소를 수백 번 두들겼고, GitHub Pages 가 연결을 끊어
#     멀쩡한 페이지를 "깨진 링크"라고 보고했다. 검사기가 거짓 경보를 내면 안 쓰느니만 못하다.
#
# 그래서 000(연결 실패)과 진짜 4xx/5xx 를 구분하고, 000 은 물러섰다가 다시 시도한다.

BASE="https://toolmoa.github.io"
CACHE=$(mktemp)
trap 'rm -f "$CACHE"' EXIT

fetch_code() {
  local t="$1" code hit
  hit=$(grep -F -m1 "	$t" "$CACHE" 2>/dev/null | cut -f1)
  if [ -n "$hit" ]; then echo "$hit"; return; fi

  local delay=1
  for try in 1 2 3 4; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 "$t")
    # 진짜 응답을 받았으면 그대로 채택한다
    if [ "$code" != "000" ]; then break; fi
    sleep $delay
    delay=$((delay * 2))
  done
  printf '%s\t%s\n' "$code" "$t" >> "$CACHE"
  echo "$code"
}

urls=$(curl -s --max-time 25 "$BASE/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | sed 's|</\?loc>||g')
if [ -z "$urls" ]; then echo "sitemap 을 읽지 못했다"; exit 1; fi

dead=0; checked=0; pages=0
for u in $urls; do
  dir="${u%/*}/"
  # 본문 읽기도 조절에 걸려 빈 응답이 올 수 있다. 링크 확인과 똑같이 물러섰다가 다시 시도한다.
  page=""; d=1
  for try in 1 2 3 4; do
    page=$(curl -s --max-time 25 "$u")
    [ -n "$page" ] && break
    sleep $d; d=$((d*2))
  done
  if [ -z "$page" ]; then echo "  페이지를 4번 시도해도 읽지 못함: $u"; dead=$((dead+1)); continue; fi
  pages=$((pages+1))
  links=$(echo "$page" | grep -o 'href="[^"#?:]*\.html"' | sed 's/href="//;s/"//' | sort -u)
  for l in $links; do
    case "$l" in
      /*)   tgt="$BASE$l" ;;
      ../*) tgt="$BASE/${l#../}" ;;
      *)    tgt="$dir$l" ;;
    esac
    code=$(fetch_code "$tgt")
    checked=$((checked+1))
    if [ "$code" != "200" ]; then
      echo "  [$code] $u 안의 \"$l\" → $tgt"
      dead=$((dead+1))
    fi
  done
done

uniq_n=$(wc -l < "$CACHE" | tr -d ' ')
echo "페이지 $pages개 · 링크 $checked개 확인 (서로 다른 주소 $uniq_n개) · 깨진 것 $dead개"
