use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# [파일, 헤더 라벨, 푸터 라벨, 번역키]
my @T = (
  ['image-compress.html','이미지 압축','이미지 용량 줄이기','nav.imgc'],
  ['image-crop.html','이미지 자르기','이미지 자르기','nav.crop'],
  ['img-to-pdf.html','이미지→PDF','이미지 PDF 변환','nav.i2p'],
  ['char-count.html','글자수 세기','글자수 세기','nav.char'],
  ['text-clean.html','텍스트 정리','텍스트 정리·중복 제거','nav.txt'],
  ['pdf-merge.html','PDF 합치기','PDF 합치기','nav.merge'],
  ['pdf-split.html','PDF 나누기','PDF 나누기','nav.split'],
  ['pdf-edit.html','PDF 회전·삭제','PDF 페이지 회전·삭제','nav.edit'],
  ['file-convert.html','파일 변환','CSV·JSON·엑셀 변환','nav.conv'],
  ['qr-generate.html','QR 만들기','QR코드 만들기','nav.qr'],
  ['password-gen.html','비밀번호 생성','비밀번호 생성기','nav.pw'],
  ['unit-convert.html','단위 변환','단위 변환기','nav.unit'],
  ['date-calc.html','날짜 계산','날짜 계산기','nav.date'],
  ['age-calc.html','만 나이','만 나이 계산기','nav.age'],
);

for my $f (@ARGV) {
  open(my $in, '<:raw', $f) or die "$f: $!";
  local $/; my $c = <$in>; close $in;
  utf8::decode($c); $c =~ s/\r\n/\n/g;

  my $hdr = "    <nav class=\"site-nav\">\n";
  for my $t (@T) {
    my $cur = ($t->[0] eq $f) ? ' aria-current="page"' : '';
    $hdr .= "      <a href=\"$t->[0]\"$cur data-i18n=\"$t->[3]\">$t->[1]</a>\n";
  }
  $hdr .= "    </nav>\n";

  my $ftr = "    <nav>\n      <a href=\"index.html\" data-i18n=\"nav.home\">홈</a>\n";
  for my $t (@T) { $ftr .= "      <a href=\"$t->[0]\" data-i18n=\"$t->[3]\">$t->[2]</a>\n" unless $t->[0] eq $f; }
  $ftr .= "    </nav>\n";

  # 비어 있는 <nav class="site-nav"></nav> 도 함께 처리한다
  my $n = ($c =~ s{[ \t]*<nav class="site-nav">.*?</nav>\n}{$hdr}s);
  my $m = ($c =~ s{(<footer class="site-footer">\s*<div class="wrap">\s*)[ \t]*<nav>.*?</nav>\n}{$1$ftr}s);

  utf8::encode($c);
  open(my $o, '>:raw', $f) or die; print $o $c; close $o;
  printf("%-22s 헤더%d 푸터%d\n", $f, $n, $m);
}
