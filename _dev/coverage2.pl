use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# coverage.pl 은 id 가 붙은 요소만 셌다. 그 아래 층위를 센다.
#  (가) 셀렉트의 개별 선택지 — 하나만 눌러보고 "이 셀렉트는 검증됨"이라 여기기 쉽다
#  (나) 번역 키는 i18ncheck.pl 담당
#  (다) 페이지 스크립트 안에서 정의만 되고 호출되지 않는 함수 (죽은 코드)

my @pages;
for my $d ('.', 'en') {
  opendir(my $dh, $d) or next;
  for my $f (sort readdir $dh) {
    next unless $f =~ /\.html$/;
    next if $f =~ /^_/ || $f =~ /^(google|naver)[0-9a-f]+\.html$/;
    push @pages, ($d eq '.' ? $f : "$d/$f");
  }
  closedir $dh;
}

my $tests = '';
opendir(my $td, '_dev') or die $!;
for my $f (sort readdir $td) {
  next unless $f =~ /\.html$/;
  open(my $h, '<:raw', "_dev/$f") or next;
  local $/; my $c = <$h>; close $h; utf8::decode($c);
  $tests .= $c;
}
closedir $td;

print "===== (가) 셀렉트 선택지가 검사에서 쓰였는가 =====\n";
my ($optAll, $optMiss) = (0, 0);
for my $p (@pages) {
  open(my $h, '<:raw', $p) or die $!; local $/; my $c = <$h>; close $h; utf8::decode($c);
  my @miss;
  # <select id="x"> ... </select> 안의 option value 를 모은다
  while ($c =~ /<select\b[^>]*\bid="([^"]+)"[^>]*>(.*?)<\/select>/gs) {
    my ($sid, $body) = ($1, $2);
    my @vals;
    while ($body =~ /<option\b[^>]*\bvalue="([^"]*)"/g) { push @vals, $1; }
    next unless @vals;
    for my $v (@vals) {
      $optAll++;
      next if $v eq '';                       # 빈 값(자동/없음)은 기본값이라 넘어간다
      # 검사에서 이 값을 문자열로 쓰고 있는가
      # HTML 의 value="\t" 는 역슬래시+t 두 글자다. 검사 소스에는 JS 이스케이프로
      # '\\t' 라 적히므로, 역슬래시를 한 번 더 겹친 형태도 같은 값으로 본다.
      my $esc = $v; $esc =~ s/\\/\\\\/g;
      my $used = ($tests =~ /['"]\Q$v\E['"]/) || ($tests =~ /['"]\Q$esc\E['"]/);
      unless ($used) { push @miss, "$sid=$v"; $optMiss++; }
    }
  }
  printf("%-24s %s\n", $p, @miss ? "미사용 " . scalar(@miss) . "개: " . join(', ', @miss) : '전부 사용됨');
}
printf("→ 선택지 %d개 중 검사에서 안 쓰인 것 %d개\n\n", $optAll, $optMiss);

# (나) 번역 키 검사는 _dev/i18ncheck.pl 로 옮겼다.
#     이쪽은 키 문자열을 페이지에서 그대로 찾는 방식이라 'dow.' + i 처럼 만들어 쓰거나
#     표에 값으로 적어둔 키를 못 봐서 거짓 경보를 냈다. 검사기 둘이 서로 다른 답을 내면
#     어느 쪽을 믿어야 할지 알 수 없으므로 하나만 남긴다.

print "\n===== (다) 정의만 되고 호출되지 않는 함수 =====\n";
my $dead = 0;
for my $p (@pages) {
  open(my $h, '<:raw', $p) or die $!; local $/; my $c = <$h>; close $h; utf8::decode($c);
  my ($script) = $c =~ /<script>(.*)<\/script>\s*<\/body>/s;
  next unless $script;
  my @names;
  while ($script =~ /\bfunction\s+([A-Za-z_\$][\w\$]*)\s*\(/g) { push @names, $1; }
  my @never;
  for my $n (@names) {
    # 정의를 뺀 나머지에서 이름이 등장하는가
    my $rest = $script;
    $rest =~ s/\bfunction\s+\Q$n\E\s*\(//g;
    push @never, $n unless $rest =~ /\b\Q$n\E\b/;
  }
  if (@never) { printf("%-24s %s\n", $p, join(', ', @never)); $dead += scalar(@never); }
}
print $dead ? "→ 죽은 함수 $dead 개\n" : "→ 죽은 함수 없음\n";
