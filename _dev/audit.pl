use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# 사이트 전체 정적 점검: 깨진 내부 링크, 중복 id, 빠진 자산, SEO 위생
my @files;
for my $d ('.', 'en') {
  opendir(my $dh, $d) or next;
  for my $f (sort readdir $dh) {
    next unless $f =~ /\.html$/;
    next if $f =~ /^_/;                            # _dev 등 개발 파일 제외
    next if $f =~ /^(google|naver)[0-9a-f]+\.html$/;  # 검색엔진 소유확인 파일 (한 줄짜리 텍스트)
    push @files, ($d eq '.' ? $f : "$d/$f");
  }
  closedir $dh;
}

my ($errors, $warns) = (0, 0);
print "점검 대상: " . scalar(@files) . "개 페이지\n\n";

for my $f (@files) {
  open(my $fh, '<:raw', $f) or die $!;
  local $/; my $c = <$fh>; close $fh;
  utf8::decode($c);
  my $dir = ($f =~ m{^en/}) ? 'en' : '.';
  my @issues;

  # --- 중복 id ---
  my %ids;
  while ($c =~ /\sid="([^"]+)"/g) { $ids{$1}++ }
  for my $k (sort keys %ids) { push @issues, "중복 id: $k (${\$ids{$k}}회)" if $ids{$k} > 1 }

  # --- 내부 링크가 실제 파일을 가리키는지 ---
  my %seen;
  while ($c =~ /(?:href|src)="([^"#?:]+)"/g) {
    my $t = $1;
    next if $t =~ m{^(https?:|data:|mailto:|//)};
    next if $seen{$t}++;
    my $p = $t;
    $p =~ s{^\./}{};
    my $full = ($p =~ m{^\.\./}) ? do { my $x = $p; $x =~ s{^\.\./}{}; $x }
             : ($dir eq 'en' ? "en/$p" : $p);
    push @issues, "깨진 링크: $t" unless -e $full;
  }

  # --- SEO 위생 ---
  my ($title) = $c =~ m{<title>(.*?)</title>}s;
  my ($desc)  = $c =~ m{<meta name="description" content="([^"]*)"};
  my ($canon) = $c =~ m{<link rel="canonical" href="([^"]*)"};
  my ($h1cnt) = scalar(() = $c =~ /<h1[\s>]/g);

  push @issues, "title 없음" unless $title;
  push @issues, "title 너무 김 (" . length($title) . "자)" if $title && length($title) > 65;
  push @issues, "description 없음" unless $desc;
  push @issues, "description 너무 김 (" . length($desc) . "자)" if $desc && length($desc) > 165;
  push @issues, "canonical 없음" unless $canon;
  push @issues, "h1이 ${h1cnt}개 (1개여야 함)" if $h1cnt != 1;
  push @issues, "lang 속성 없음" unless $c =~ /<html lang="/;
  push @issues, "viewport 없음" unless $c =~ /name="viewport"/;
  push @issues, "charset 없음" unless $c =~ /<meta charset=/i;

  # --- 접근성: label의 for가 실제 요소를 가리키는지 ---
  while ($c =~ /<label[^>]*\sfor="([^"]+)"/g) {
    my $t = $1;
    push @issues, "label for=\"$t\" 에 해당하는 요소 없음" unless $ids{$t};
  }

  # --- 흔한 실수 ---
  push @issues, "data-i18n 중복 속성" if $c =~ /<[^>]*data-i18n="[^"]*"[^>]*data-i18n=/;
  push @issues, "example.github.io 잔존" if $c =~ /example\.github\.io/;
  push @issues, "TODO/FIXME 잔존" if $c =~ /\b(TODO|FIXME)\b/;

  if (@issues) {
    printf("%-26s\n", $f);
    print "   ⚠ $_\n" for @issues;
    $errors += scalar(@issues);
  } else {
    printf("%-26s 이상 없음\n", $f);
  }
}

print "\n총 문제 $errors 건\n";
