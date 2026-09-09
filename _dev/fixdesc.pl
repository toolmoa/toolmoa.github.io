use strict; use warnings; use utf8;
binmode(STDOUT, ':utf8');

# 구글은 description을 대략 155자에서 자른다. 핵심 각도를 앞쪽에 두고 줄인다.
my %D = (
 'en/index.html' =>
   'Compress images, merge and split PDFs, make QR codes and convert spreadsheets — all inside your browser. Your files are never uploaded. Free, no sign-up.',
 'en/pdf-merge.html' =>
   'Combine PDFs into one file without uploading anything. The merge runs inside your browser, so contracts and private documents never reach a server.',
 'en/pdf-split.html' =>
   'Extract pages from a PDF, or split it into single pages, without uploading. It runs in your browser, so confidential files never leave your device.',
 'en/image-compress.html' =>
   'Shrink photo file size without uploading. Quality and size are adjusted in your browser, and the location data in your photo is dropped on the way out.',
 'en/image-crop.html' =>
   'Crop, rotate and flip photos without uploading them. Fixed ratios for profile pictures. Runs entirely in your browser — no watermark, no sign-up.',
 'en/img-to-pdf.html' =>
   'Turn photos into a single PDF without uploading them. Scanned paperwork and ID photos stay on your device because the conversion runs in your browser.',
 'en/file-convert.html' =>
   'Convert CSV, JSON and Excel files without uploading your data. Encoding is detected automatically, and CSV exports open correctly in Excel.',
 'en/qr-generate.html' =>
   'Make a QR code from a link or text and save it as PNG. Static codes with no tracking redirect and no expiry date. Free, no watermark, no sign-up.',
);

for my $f (sort keys %D) {
  open(my $in, '<:raw', $f) or die "$f: $!";
  local $/; my $c = <$in>; close $in;
  utf8::decode($c); $c =~ s/\r\n/\n/g;

  my $new = $D{$f};
  my ($old) = $c =~ m{<meta name="description" content="([^"]*)"};
  $c =~ s{(<meta name="description" content=")[^"]*(")}{$1$new$2};

  utf8::encode($c);
  open(my $o, '>:raw', $f) or die; print $o $c; close $o;
  printf("%-26s %d자 → %d자\n", $f, length($old // ''), length($new));
}
