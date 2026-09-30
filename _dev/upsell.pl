#!/usr/bin/perl
# 이미지 압축 페이지(한국어·영어)의 숨겨 둔 "일괄 처리판 보기" 상자를 켠다.
#
#   perl _dev/upsell.pl https://<아이디>.gumroad.com/l/<상품>
#
# 하는 일
#   1. image-compress.html · en/image-compress.html 의 upsell 상자에서 hidden 을 지우고
#      버튼 주소를 받은 Gumroad 주소로 바꾼다 (새 탭 · rel="noopener").
#   2. 개인정보처리방침 4항에 "결제는 Gumroad 가 처리한다"는 문단을 넣고 시행일을 오늘로 바꾼다.
#      이용자를 결제 사이트로 보내면서 방침에 그 사실이 없으면 안 된다.
#
# 다시 돌려도 안전하다 (주소만 바뀐다). 끄려면 git 으로 되돌릴 것.
# pdf-merge 의 상자는 건드리지 않는다 — 그 문구에 해당하는 상품은 아직 없다.
use strict; use warnings; use utf8;
binmode STDOUT, ':encoding(UTF-8)'; binmode STDERR, ':encoding(UTF-8)';

my $url = shift or die "사용법: perl _dev/upsell.pl https://<아이디>.gumroad.com/l/<상품>\n";
$url =~ m{^https://[a-z0-9-]+\.gumroad\.com/l/[A-Za-z0-9_-]+/?$}
  or die "Gumroad 상품 주소가 아닙니다: $url\n(형식: https://<아이디>.gumroad.com/l/<상품>)\n";

sub edit {
  my ($f, $code) = @_;
  open my $in, '<:encoding(UTF-8)', $f or die "$f: $!"; my $c = do { local $/; <$in> }; close $in;
  my $n = $code->(\$c);
  open my $o, '>:encoding(UTF-8)', $f or die; print $o $c; close $o;
  printf "%-26s %s\n", $f, $n;
}

for my $f ('image-compress.html', 'en/image-compress.html') {
  edit($f, sub {
    my $c = shift;
    $$c =~ s{<div class="upsell" hidden>}{<div class="upsell">};
    # 주소·target·rel 을 한 번에 다시 쓴다 (두 번째 실행에서도 중복되지 않게)
    my $n = ($$c =~ s{<a class="btn" href="[^"]*"(?: target="_blank" rel="noopener")? id="upsell-link"}
                      {<a class="btn" href="$url" target="_blank" rel="noopener" id="upsell-link"});
    $n ? "켬 → $url" : '⚠ 버튼을 찾지 못함';
  });
}

my @t = localtime; my $today = sprintf('%d년 %d월 %d일', $t[5] + 1900, $t[4] + 1, $t[3]);
edit('privacy.html', sub {
  my $c = shift;
  return '이미 들어 있음' if $$c =~ /Gumroad/;
  my $para = <<"P";
  <p>
    유료 상품(툴모아 일괄 처리)은 <strong>Gumroad</strong>에서 판매합니다. 구매 버튼을 누르면 Gumroad 사이트로
    이동하며, 결제에 필요한 이메일·결제 정보는 Gumroad가 처리합니다. 이 사이트는 그 정보를 받지 않습니다.
    구매한 프로그램 역시 사진을 어디로도 전송하지 않습니다.
  </p>
P
  my $n = ($$c =~ s{(\n  <p class="hint">\n    앞으로 광고를 싣게 되면)}{\n$para$1});
  $$c =~ s{시행일: \d+년 \d+월 \d+일}{시행일: $today};
  $n ? "결제 안내 추가 · 시행일 $today" : '⚠ 넣을 자리를 찾지 못함';
});

print "\n다음: perl _dev/audit.pl · bash _dev/live.sh 로 확인한 뒤 커밋·푸시\n";
