#!/usr/bin/perl
# en/ 페이지의 머리 메뉴와 바닥 링크를 한 목록으로 다시 쓴다.
# 영어판이 늘 때마다 손으로 12곳을 고치면 반드시 한두 곳이 빠진다.
use strict; use warnings; use utf8;
binmode STDOUT, ':encoding(UTF-8)';

my @TOOLS = (   # 파일, 머리 메뉴 이름, 바닥 이름
  ['image-compress.html', 'Compress image', 'Compress image'],
  ['image-crop.html',     'Crop image',     'Crop image'],
  ['image-convert.html',  'Convert image',  'Convert image format'],
  ['image-join.html',     'Join images',    'Join images'],
  ['img-to-pdf.html',     'Image → PDF',    'Image to PDF'],
  ['pdf-merge.html',      'Merge PDF',      'Merge PDF'],
  ['pdf-split.html',      'Split PDF',      'Split PDF'],
  ['pdf-to-image.html',   'PDF → image',    'PDF to image'],
  ['file-convert.html',   'Convert file',   'Convert file'],
  ['image-mosaic.html',   'Blur / redact',  'Blur or redact a photo'],
  ['image-exif.html',     'Remove location', 'Remove photo location'],
  ['qr-generate.html',    'QR code',        'QR code'],
  ['random-pick.html',    'Random picker',  'Random picker'],
  ['image-watermark.html', 'Watermark',     'Photo watermark'],
  ['image-split.html',    'Split image',    'Split image into a grid'],
  ['pdf-watermark.html',  'PDF watermark',  'PDF watermark'],
  ['qr-scan.html',        'Read QR',        'Read a QR code from an image'],
  ['romanize.html',       'Romanize name',  'Romanize a Korean name'],
  ['image-resize.html',   'Resize image',   'Resize image'],
  ['image-transparent.html', 'Transparent bg', 'Make a white background transparent'],
  ['color-convert.html',  'Color codes',    'Color code converter'],
  ['barcode.html',        'Barcode',        'Barcode generator'],
  ['text-clean.html',     'Clean up text',  'Remove duplicate lines · clean up text'],
  ['text-diff.html',      'Compare text',   'Compare two texts'],
  ['pdf-edit.html',       'Rotate PDF',     'Rotate, delete and reorder PDF pages'],
  ['password-gen.html',   'Password',       'Password generator'],
  ['time-calc.html',      'Time calc',      'Time calculator · work hours'],
);

for my $path (glob('en/*.html')) {
  open my $fh, '<:encoding(UTF-8)', $path or die; my $h = do { local $/; <$fh> }; close $fh;
  (my $me = $path) =~ s{^en/}{};

  my $head = join '', map {
    qq{      <a href="$_->[0]"} . ($_->[0] eq $me ? ' aria-current="page"' : '') . qq{>$_->[1]</a>\n}
  } @TOOLS;
  my $n1 = ($h =~ s{(<nav class="site-nav">\n).*?(    </nav>)}{$1$head$2}s);

  # 바닥: 자기 자신은 빼고, 홈이면 Home 도 뺀다
  my $koHref = $me eq 'index.html' ? '../index.html' : "../$me";
  my $foot = ($me eq 'index.html' ? '' : qq{      <a href="index.html">Home</a>\n})
           . join('', map { qq{      <a href="$_->[0]">$_->[2]</a>\n} } grep { $_->[0] ne $me } @TOOLS)
           . qq{      <a href="$koHref" hreflang="ko">한국어</a>\n};
  $foot = qq{      <a href="index.html">Home</a>\n} . $foot if $me eq 'index.html';
  my $n2 = ($h =~ s{(<footer class="site-footer">\s*<div class="wrap">\s*<nav>\n).*?(    </nav>)}{$1$foot$2}s);

  open my $o, '>:encoding(UTF-8)', $path or die; print $o $h; close $o;
  printf "%-24s head %d  foot %d\n", $path, $n1, $n2;
}
