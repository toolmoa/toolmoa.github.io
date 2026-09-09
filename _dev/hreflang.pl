use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# 영어 버전이 존재하는 한국어 페이지 (파일명 => 한국어 URL 경로)
my %PAIR = (
  'index.html'          => '',
  'image-compress.html' => 'image-compress.html',
  'image-crop.html'     => 'image-crop.html',
  'img-to-pdf.html'     => 'img-to-pdf.html',
  'pdf-merge.html'      => 'pdf-merge.html',
  'pdf-split.html'      => 'pdf-split.html',
  'file-convert.html'   => 'file-convert.html',
  'qr-generate.html'    => 'qr-generate.html',
);

my $BASE = 'https://toolmoa.github.io/';

for my $f (sort keys %PAIR) {
  open(my $in, '<:raw', $f) or die "$f: $!";
  local $/; my $c = <$in>; close $in;
  utf8::decode($c); $c =~ s/\r\n/\n/g;

  # 이미 넣었으면 건너뛴다 (중복 방지)
  if ($c =~ /rel="alternate" hreflang="en"/) { print "$f  이미 있음\n"; next; }

  my $koUrl = $BASE . $PAIR{$f};
  my $enUrl = $BASE . 'en/' . $PAIR{$f};

  my $tags = qq{<link rel="alternate" hreflang="ko" href="$koUrl">\n}
           . qq{<link rel="alternate" hreflang="en" href="$enUrl">\n}
           . qq{<link rel="alternate" hreflang="x-default" href="$koUrl">};

  # canonical 바로 뒤에 삽입한다
  my $n = ($c =~ s{(<link rel="canonical"[^>]*>)}{$1\n$tags});

  # 영어 페이지로 가는 사람이 볼 수 있게 헤더에도 링크를 둔다
  my $enHref = 'en/' . $PAIR{$f};
  $enHref = 'en/index.html' if $PAIR{$f} eq '';

  utf8::encode($c);
  open(my $o, '>:raw', $f) or die; print $o $c; close $o;
  printf("%-22s hreflang %d  ->  %s\n", $f, $n, $enUrl);
}
