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
    # 스크립트가 실행 중에 만들어내는 주소(문자열 조합)는 파일로 존재하지 않는다
    next if $t =~ /['"+]/ || $t =~ /^\s/;
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

# --- 한국어판에 넣은 기능이 영어판에 빠지지 않았는지 대조 ---
# 한쪽만 고치고 넘어가기 가장 쉬운 실수라 상시 검사로 둔다.
print "\n=== 한국어 / 영어 기능 대조 ===\n";
my @PAIRS = (
  ['qr-generate.html',    ['id="qtype"', 'id="g-wifi"', 'id="g-vcard"', 'id="logo"',
                           'toUtf8Chars', 'buildPayload', 'drawLogo', 'CAP = {']],
  ['image-crop.html',     ['id="preset"', 'id="custom-field"', 'function presetSize', "addEventListener('paste'",
                           'function activeRatio', 'jpe?g/i.test']],
  ['image-compress.html', ['id="target-size"', 'function encodeToTarget', 'function toBlob',
                           'id="as-zip"', 'makeZip(entries)', "addEventListener('paste'"]],
  ['pdf-merge.html',      ['ParseSpeeds.Fastest', 'new Uint8Array(buf)', 'function makeThumbs', 'function loadPdfJs', 'it.thumbTried']],
  ['pdf-split.html',      ['ParseSpeeds.Fastest']],
  ['img-to-pdf.html',     ['toJpegBytes', "addEventListener('paste'"]],
  ['file-convert.html',   ['function decodeText', q{type: 'string'}, 'id="fs"', 'opt.FS', 'lastFile']],
);

my $gap = 0;
for my $p (@PAIRS) {
  my ($file, $marks) = @$p;
  my $en = "en/$file";
  unless (-e $en) { printf("%-22s 영어판 없음 (의도된 경우도 있음)\n", $file); next; }

  my $ko_c = do { open(my $h, '<:raw', $file) or die $!; local $/; <$h> };
  my $en_c = do { open(my $h, '<:raw', $en) or die $!; local $/; <$h> };
  utf8::decode($ko_c); utf8::decode($en_c);

  my @miss = grep { index($ko_c, $_) >= 0 && index($en_c, $_) < 0 } @$marks;
  if (@miss) {
    printf("%-22s ⚠ 영어판 누락: %s\n", $file, join(', ', @miss));
    $gap += scalar(@miss);
  } else {
    printf("%-22s 동등\n", $file);
  }
}
print $gap ? "\n기능 격차 $gap 건\n" : "\n기능 격차 없음\n";
