#!/usr/bin/perl
# photo-exif.jpg 의 EXIF Orientation 값만 6(오른쪽으로 90도 돌려 보라)으로 바꾼
# 검사용 사진을 만든다. 화소는 그대로고 태그 2바이트만 다르다.
#
# 왜 필요한가: 휴대전화로 세로로 찍은 사진은 화소는 가로로 저장하고
# "돌려서 보라"는 태그만 붙여 둔다. 이 태그를 무시하면 결과물이 옆으로 눕는다.
# 기존 픽스처는 Orientation=1(정상)이라 이 경우를 한 번도 밟아 보지 못했다.
use strict;
use warnings;

my $SRC = '_dev/fixtures/photo-exif.jpg';
my $DST = '_dev/fixtures/photo-rot90.jpg';

open my $f, '<:raw', $SRC or die "$SRC: $!";
my $d = do { local $/; <$f> };
close $f;

sub u16 { my ($o, $le) = @_; $le ? unpack('v', substr($d, $o, 2)) : unpack('n', substr($d, $o, 2)) }
sub u32 { my ($o, $le) = @_; $le ? unpack('V', substr($d, $o, 4)) : unpack('N', substr($d, $o, 4)) }

my $p = index($d, "Exif\0\0");
die "EXIF 없음\n" if $p < 0;
my $tiff = $p + 6;
my $le   = substr($d, $tiff, 2) eq 'II';
my $ifd  = $tiff + u32($tiff + 4, $le);
my $n    = u16($ifd, $le);

my $off;
for my $i (0 .. $n - 1) {
    my $e = $ifd + 2 + $i * 12;
    if (u16($e, $le) == 0x0112) { $off = $e + 8; last }
}
die "Orientation 태그가 없다\n" unless defined $off;

printf "원본 Orientation = %d\n", u16($off, $le);
substr($d, $off, 2) = $le ? pack('v', 6) : pack('n', 6);

# 화소 자체의 크기(SOF 마커)도 같이 적어 둔다. 브라우저가 태그를 반영했는지
# 판단하려면 "저장된 크기"와 "화면에 보이는 크기"를 견줘야 한다.
my ($w, $h);
my $i = 2;
while ($i < length($d) - 1) {
    last unless ord(substr($d, $i, 1)) == 0xFF;
    my $m = ord(substr($d, $i + 1, 1));
    last if $m == 0xDA;                       # 이미지 데이터 시작
    my $len = unpack('n', substr($d, $i + 2, 2));
    if ($m >= 0xC0 && $m <= 0xCF && $m != 0xC4 && $m != 0xC8 && $m != 0xCC) {
        $h = unpack('n', substr($d, $i + 5, 2));
        $w = unpack('n', substr($d, $i + 7, 2));
        last;
    }
    $i += 2 + $len;
}

open my $o, '>:raw', $DST or die "$DST: $!";
print $o $d;
close $o;

printf "만듦: %s (Orientation=6, 저장된 화소 %dx%d)\n", $DST, $w // 0, $h // 0;
print "브라우저가 태그를 반영하면 화면에서는 ${\($h//0)}x${\($w//0)} 로 보여야 한다.\n";
