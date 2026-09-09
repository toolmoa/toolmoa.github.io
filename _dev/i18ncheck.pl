use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# HTML이 쓰는 data-i18n 키가 사전에 실제로 있는지 확인한다.
# 없으면 언어를 바꿔도 그 자리만 한국어로 남아 반쪽짜리 화면이 된다.

open(my $j, '<:raw', 'assets/i18n.js') or die $!;
local $/; my $js = <$j>; close $j;
utf8::decode($js);

# en / ja 사전 블록을 각각 떼어낸다
my %have;
for my $lang ('en', 'ja') {
  my ($block) = $js =~ /\n    $lang: \{(.*?)\n    \}/s;
  die "사전 블록을 못 찾음: $lang" unless $block;
  while ($block =~ /'([^']+)'\s*:/g) { $have{$lang}{$1} = 1 }
}
printf("사전 키 개수  en=%d  ja=%d\n\n", scalar(keys %{$have{en}}), scalar(keys %{$have{ja}}));

my @files;
opendir(my $dh, '.') or die $!;
for my $f (sort readdir $dh) {
  next unless $f =~ /\.html$/;
  next if $f =~ /^_/ || $f =~ /^(google|naver)[0-9a-f]+\.html$/;
  push @files, $f;
}
closedir $dh;

my (%missEn, %missJa, $total);
for my $f (@files) {
  open(my $fh, '<:raw', $f) or die $!;
  local $/; my $c = <$fh>; close $fh;
  utf8::decode($c);
  my %seen;
  while ($c =~ /data-i18n(?:-ph)?="([^"]+)"/g) { $seen{$1} = 1 }
  # 스크립트 안에서 쓰는 t('키', ...) 도 함께 본다
  while ($c =~ /\bt\('([^']+)'\s*,/g) { $seen{$1} = 1 }

  for my $k (sort keys %seen) {
    $total++;
    push @{$missEn{$f}}, $k unless $have{en}{$k};
    push @{$missJa{$f}}, $k unless $have{ja}{$k};
  }
}

my $bad = 0;
for my $f (@files) {
  my @e = @{ $missEn{$f} || [] };
  my @a = @{ $missJa{$f} || [] };
  next unless @e || @a;
  $bad += scalar(@e) + scalar(@a);
  print "$f\n";
  print "   영어 사전에 없음: " . join(', ', @e) . "\n" if @e;
  print "   일본어 사전에 없음: " . join(', ', @a) . "\n" if @a;
}
print "모든 키가 두 언어 사전에 존재합니다.\n" unless $bad;
print "\n검사한 키 사용처 $total 곳 · 누락 $bad 건\n";
