use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# 페이지가 쓰는 번역 키가 사전에 실제로 있는지, 그리고 사전에만 있고 아무도 안 쓰는
# 키가 남아 있는지 양쪽으로 확인한다.
#
# 한쪽만 보면 반쪽짜리다.
#  - 키는 쓰는데 사전에 없으면 → 그 자리만 한국어로 남는다.
#  - 사전에는 있는데 페이지가 안 부르면 → 번역을 만들어 두고도 화면은 한국어다.
#    실제로 이 두 번째 경우로 상세표·단위·안내문구 81곳이 통째로 안 바뀌고 있었다.

open(my $j, '<:raw', 'assets/i18n.js') or die $!;
local $/; my $js = <$j>; close $j;
utf8::decode($js);

my %have;
for my $lang ('en', 'ja') {
  my ($block) = $js =~ /\n    $lang: \{(.*?)\n    \}/s;
  die "사전 블록을 못 찾음: $lang" unless $block;
  while ($block =~ /'([^']+)'\s*:/g) { $have{$lang}{$1} = 1 }
}
printf("사전 키 개수  en=%d  ja=%d\n\n", scalar(keys %{$have{en}}), scalar(keys %{$have{ja}}));

my @files;
for my $d ('.', 'en') {
  opendir(my $dh, $d) or next;
  for my $f (sort readdir $dh) {
    next unless $f =~ /\.html$/;
    next if $f =~ /^_/ || $f =~ /^(google|naver)[0-9a-f]+\.html$/;
    push @files, ($d eq '.' ? $f : "$d/$f");
  }
  closedir $dh;
}

my (%missEn, %missJa, $total, %usedKey, %usedPrefix);
for my $f (@files) {
  open(my $fh, '<:raw', $f) or die $!;
  local $/; my $c = <$fh>; close $fh;
  utf8::decode($c);

  my %seen;
  while ($c =~ /data-i18n(?:-ph|-title)?="([^"]+)"/g) { $seen{$1} = 1 }
  # 스크립트 안의 t('키', …) 와 tt('키', …). tt 를 빠뜨리면 그 키가 통째로 검사에서 샌다.
  while ($c =~ /(?<![\w\$])tt?\('([^']+)'\s*,/g) { $seen{$1} = 1 }
  # UKEY = { '평': 'u.pyeong' } 처럼 표에 값으로 적어두고 나중에 부르는 방식도 있다.
  # 따옴표로 감싼 문자열이 사전 키와 정확히 같으면 쓰이는 것으로 본다.
  while ($c =~ /['"]([a-z][\w]*(?:\.[\w]+)+)['"]/g) {
    $seen{$1} = 1 if $have{en}{$1};
  }
  # 'dow.' + i 처럼 만들어 쓰는 키는 접두어 묶음이 통째로 있어야 한다
  while ($c =~ /'([a-z][\w]*(?:\.[\w]+)*\.)'\s*\+/g) { $usedPrefix{$1} = 1 }

  for my $k (sort keys %seen) {
    $total++;
    $usedKey{$k} = 1;
    push @{$missEn{$f}}, $k unless $have{en}{$k};
    push @{$missJa{$f}}, $k unless $have{ja}{$k};
  }
}

# 동적 접두어가 사전에 하나라도 있는지
for my $pre (sort keys %usedPrefix) {
  my @en = grep { index($_, $pre) == 0 } keys %{$have{en}};
  my @ja = grep { index($_, $pre) == 0 } keys %{$have{ja}};
  print "동적 키 '$pre*' : 영어 사전에 하나도 없음\n" unless @en;
  print "동적 키 '$pre*' : 일본어 사전에 하나도 없음\n" unless @ja;
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
print "쓰는 키는 모두 두 언어 사전에 있습니다.\n" unless $bad;
print "\n검사한 키 사용처 $total 곳 · 누락 $bad 건\n";

# --- 반대 방향: 사전에만 있고 아무도 안 쓰는 키 ---
print "\n=== 사전에만 있고 화면에서 안 쓰는 키 ===\n";
my @orphan;
for my $k (sort keys %{$have{en}}) {
  next if $usedKey{$k};
  next if grep { index($k, $_) == 0 } keys %usedPrefix;   # 동적으로 불리는 묶음
  push @orphan, $k;
}
if (@orphan) {
  print "  " . scalar(@orphan) . "개 — 번역을 만들어 두고 페이지가 부르지 않는다:\n";
  print "    $_\n" for @orphan;
} else {
  print "  없음 (사전 키가 전부 실제로 쓰인다)\n";
}
