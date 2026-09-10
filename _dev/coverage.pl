use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# 페이지마다 "사용자가 만질 수 있는 것"을 뽑아, 검사 파일에서 한 번이라도 쓰였는지 대조한다.
# 내가 기억나는 대로 테스트를 늘리면 빠진 걸 영영 모른다. 목록을 기계가 만들게 한다.

my @pages;
for my $d ('.', 'en') {
  opendir(my $dh, $d) or next;
  for my $f (sort readdir $dh) {
    next unless $f =~ /\.html$/;
    next if $f =~ /^_/;
    next if $f =~ /^(google|naver)[0-9a-f]+\.html$/;
    push @pages, ($d eq '.' ? $f : "$d/$f");
  }
  closedir $dh;
}

# 검사 파일 전체를 한 덩어리로 읽어둔다
my $tests = '';
opendir(my $td, '_dev') or die $!;
for my $f (sort readdir $td) {
  next unless $f =~ /\.html$/;
  open(my $h, '<:raw', "_dev/$f") or next;
  local $/; my $c = <$h>; close $h;
  utf8::decode($c);
  $tests .= $c;
}
closedir $td;

my ($totalCtl, $totalMiss) = (0, 0);
my @missReport;

for my $p (@pages) {
  open(my $h, '<:raw', $p) or die $!; local $/; my $c = <$h>; close $h;
  utf8::decode($c);

  my %ctl;
  # 조작 요소: input / select / textarea / button 에 붙은 id
  while ($c =~ /<(input|select|textarea|button)\b([^>]*)>/g) {
    my ($tag, $attrs) = ($1, $2);
    next unless $attrs =~ /\bid="([^"]+)"/;
    my $id = $1;
    next if $id =~ /^(msg|out|list|grid|area|preview|canvas|placeholder)$/;  # 표시 전용
    $ctl{$id} = $tag;
  }
  # 클릭 대상이 되는 div (드롭존 등)
  while ($c =~ /<div\b[^>]*\bid="(dz)"/g) { $ctl{$1} = 'div'; }

  my @miss;
  for my $id (sort keys %ctl) {
    $totalCtl++;
    # 검사 어딘가에서 이 id를 문자열로 쓰고 있는가
    my $used = ($tests =~ /['"]\Q$id\E['"]/);
    unless ($used) { push @miss, "$id($ctl{$id})"; $totalMiss++; }
  }
  if (@miss) {
    push @missReport, sprintf("%-24s 미검증 %2d개: %s", $p, scalar(@miss), join(', ', @miss));
  } else {
    push @missReport, sprintf("%-24s 전부 검사됨 (%d개)", $p, scalar(keys %ctl));
  }
}

print "$_\n" for @missReport;
printf("\n조작 요소 %d개 중 검사에서 한 번도 안 쓰인 것 %d개\n", $totalCtl, $totalMiss);
