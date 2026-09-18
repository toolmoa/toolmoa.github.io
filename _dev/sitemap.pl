#!/usr/bin/perl
# sitemap.xml 을 실제 파일 목록에서 다시 만든다.
#
# 손으로 관리하면 툴을 늘렸을 때 빠뜨린다. 그리고 lastmod 가 없으면
# 검색엔진이 어느 페이지를 다시 읽어야 할지 판단할 근거가 없다.
#
#   lastmod  : 파일 수정 시각
#   alternate: 페이지 안의 hreflang 을 그대로 읽어 넣는다 (두 곳을 따로 적으면 어긋난다)
use strict;
use warnings;
use utf8;
binmode STDOUT, ':encoding(UTF-8)';

my $ROOT = shift || '.';
my $BASE = 'https://toolmoa.github.io';

my @files = (glob("$ROOT/*.html"), glob("$ROOT/en/*.html"));
my (@entries);

for my $path (sort @files) {
    my $rel = $path; $rel =~ s{^\Q$ROOT\E/}{};
    next if $rel =~ /^google|^naver/ || $rel eq '404.html';   # 404 는 sitemap 에 넣지 않는다

    open my $fh, '<:encoding(UTF-8)', $path or die "$path: $!";
    my $html = do { local $/; <$fh> };
    close $fh;

    my ($canon) = $html =~ m{<link rel="canonical" href="([^"]+)"};
    unless ($canon) { warn "canonical 없음, 건너뜀: $rel\n"; next }

    my @alt;
    while ($html =~ m{<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"}g) {
        push @alt, [$1, $2];
    }

    my @st = stat($path);
    my @t  = localtime($st[9]);
    my $lastmod = sprintf '%04d-%02d-%02d', $t[5] + 1900, $t[4] + 1, $t[3];

    # 홈이 가장 중요하고, 한국어가 주 언어다
    my $pri = $rel eq 'index.html'    ? '1.0'
            : $rel eq 'en/index.html' ? '0.8'
            : $rel =~ m{^en/}         ? '0.7'
            :                           '0.9';

    push @entries, { loc => $canon, lastmod => $lastmod, pri => $pri, alt => \@alt, rel => $rel };
}

my $out = qq{<?xml version="1.0" encoding="UTF-8"?>\n}
        . qq{<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n}
        . qq{        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n\n}
        . qq{<!-- _dev/sitemap.pl 이 만든다. 직접 고치지 말 것 -->\n};

my $section = '';
for my $e (@entries) {
    my $want = $e->{rel} =~ m{^en/} ? 'English' : '한국어';
    if ($want ne $section) { $out .= "\n  <!-- $want -->\n"; $section = $want }
    $out .= "  <url>\n"
          . "    <loc>$e->{loc}</loc>\n"
          . "    <lastmod>$e->{lastmod}</lastmod>\n"
          . "    <priority>$e->{pri}</priority>\n";
    for my $a (@{ $e->{alt} }) {
        $out .= qq{    <xhtml:link rel="alternate" hreflang="$a->[0]" href="$a->[1]"/>\n};
    }
    $out .= "  </url>\n";
}
$out .= "\n</urlset>\n";

open my $o, '>:encoding(UTF-8)', "$ROOT/sitemap.xml" or die $!;
print $o $out;
close $o;

printf "sitemap.xml 다시 만듦 — 주소 %d개, 언어 연결 %d개\n",
       scalar @entries, scalar(grep { @{ $_->{alt} } } @entries);
