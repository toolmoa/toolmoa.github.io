#!/usr/bin/perl
# 페이지마다 공유용 메타 태그와 구조화 데이터를 만들어 <head> 에 넣는다.
#
# 넣는 것
#   - og:type / og:url / og:site_name / og:image (+크기·대체문구)
#   - twitter:card 한 벌
#   - theme-color
#   - FAQPage  : 페이지에 이미 적혀 있는 <details> 문답을 그대로 읽어 만든다
#   - BreadcrumbList : 홈 > 도구 이름 (홈 페이지는 제외)
#
# FAQ 를 손으로 다시 적지 않는 이유: 화면 문구와 구조화 데이터가 어긋나면
# 구글이 리치 스니펫을 빼 버린다. 한 곳(HTML)만 고치면 되도록 읽어서 만든다.
#
# 다시 돌려도 안전하다. SEO:AUTO 블록을 통째로 지우고 새로 넣는다.
use strict;
use warnings;
use utf8;
binmode STDOUT, ':encoding(UTF-8)';

my $ROOT = shift || '.';
my $BASE = 'https://toolmoa.github.io';

my @files = (glob("$ROOT/*.html"), glob("$ROOT/en/*.html"));

sub strip {                       # 태그를 걷어내고 실제로 읽히는 글자만 남긴다
    my $s = shift // '';
    $s =~ s{<br\s*/?>}{ }gi;
    $s =~ s{<[^>]+>}{}g;
    $s =~ s{&nbsp;}{ }g; $s =~ s{&amp;}{&}g;
    $s =~ s{&lt;}{<}g;   $s =~ s{&gt;}{>}g; $s =~ s{&quot;}{"}g;
    $s =~ s{\s+}{ }g;
    $s =~ s{^\s+|\s+$}{}g;
    return $s;
}

sub js {                          # JSON 문자열 escape
    my $s = shift // '';
    $s =~ s{\\}{\\\\}g;
    $s =~ s{"}{\\"}g;
    $s =~ s{[\r\n\t]}{ }g;
    return $s;
}

sub attr { my $s = shift // ''; $s =~ s{&}{&amp;}g; $s =~ s{"}{&quot;}g;
           $s =~ s{<}{&lt;}g; $s =~ s{>}{&gt;}g; return $s; }

my ($done, $faqtotal) = (0, 0);
for my $path (@files) {
    my $rel = $path; $rel =~ s{^\Q$ROOT\E/}{};
    # 404 는 색인시키지 않으므로 공유 메타도 구조화 데이터도 넣지 않는다
    next if $rel =~ /^google|^naver/ || $rel eq '404.html';

    open my $fh, '<:encoding(UTF-8)', $path or die "$path: $!";
    my $html = do { local $/; <$fh> };
    close $fh;

    # 이전에 넣은 블록 제거 (다시 돌려도 쌓이지 않게)
    $html =~ s{\n?<!-- SEO:AUTO.*?/SEO:AUTO -->\n?}{\n}s;
    # 직접 박혀 있던 og:type 은 아래에서 다시 넣으므로 걷어낸다
    $html =~ s{[ \t]*<meta property="og:type"[^>]*>\n}{}g;

    my ($canon) = $html =~ m{<link rel="canonical" href="([^"]+)"};
    my ($h1)    = $html =~ m{<h1[^>]*>(.*?)</h1>}s;
    my ($ogt)   = $html =~ m{<meta property="og:title" content="([^"]*)"};
    my ($ogd)   = $html =~ m{<meta property="og:description" content="([^"]*)"};
    unless ($canon && $h1) { warn "건너뜀(canonical/h1 없음): $rel\n"; next; }

    $h1 = strip($h1);
    $ogt = $h1 unless defined $ogt && length $ogt;
    $ogd = '' unless defined $ogd;

    my $en   = $rel =~ m{^en/} ? 1 : 0;
    my $home = $en ? "$BASE/en/" : "$BASE/";
    my $site = $en ? 'Toolmoa' : '툴모아';
    my $lang = $en ? 'en_US' : 'ko_KR';

    my $slug = $rel; $slug =~ s/\.html$//; $slug =~ s{/}{-}g;
    my $img  = "$BASE/assets/og/$slug.png";
    my $alt  = $en ? "$h1 — Toolmoa" : "$h1 — 툴모아";

    # --- FAQ 읽기 ---
    my @qa;
    while ($html =~ m{<details[^>]*>(.*?)</details>}gs) {
        my $blk = $1;
        my ($q) = $blk =~ m{<summary[^>]*>(.*?)</summary>}s;
        next unless defined $q;
        my $a = $blk;
        $a =~ s{<summary[^>]*>.*?</summary>}{}s;
        ($q, $a) = (strip($q), strip($a));
        next unless length $q && length $a;
        push @qa, [$q, $a];
    }
    $faqtotal += scalar @qa;

    my @ld;
    if (@qa) {
        my $items = join ',', map {
            sprintf '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}',
                    js($_->[0]), js($_->[1])
        } @qa;
        push @ld, sprintf
            '{"@context":"https://schema.org","@type":"FAQPage","inLanguage":"%s","mainEntity":[%s]}',
            ($en ? 'en' : 'ko'), $items;
    }

    # 홈에는 경로가 없다
    unless ($rel eq 'index.html' || $rel eq 'en/index.html') {
        push @ld, sprintf
            '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
          . '{"@type":"ListItem","position":1,"name":"%s","item":"%s"},'
          . '{"@type":"ListItem","position":2,"name":"%s","item":"%s"}]}',
            ($en ? 'Home' : '홈'), $home, js($h1), $canon;
    }

    my $blk = "<!-- SEO:AUTO  _dev/seometa.pl 이 만든다. 직접 고치지 말 것 -->\n"
        . qq{<meta property="og:type" content="website">\n}
        . qq{<meta property="og:url" content="@{[attr $canon]}">\n}
        . qq{<meta property="og:site_name" content="@{[attr $site]}">\n}
        . qq{<meta property="og:image" content="@{[attr $img]}">\n}
        . qq{<meta property="og:image:width" content="1200">\n}
        . qq{<meta property="og:image:height" content="630">\n}
        . qq{<meta property="og:image:alt" content="@{[attr $alt]}">\n}
        . qq{<meta name="twitter:card" content="summary_large_image">\n}
        . qq{<meta name="twitter:title" content="@{[attr $ogt]}">\n}
        . qq{<meta name="twitter:description" content="@{[attr $ogd]}">\n}
        . qq{<meta name="twitter:image" content="@{[attr $img]}">\n}
        . qq{<meta name="theme-color" content="#2f6df6">\n}
        . join('', map { qq{<script type="application/ld+json">\n$_\n</script>\n} } @ld)
        . "<!-- /SEO:AUTO -->\n";

    # og:locale 이 이미 있으므로 굳이 다시 넣지 않는다
    $html =~ s{</head>}{$blk</head>} or do { warn "</head> 없음: $rel\n"; next; };

    open my $o, '>:encoding(UTF-8)', $path or die $!;
    print $o $html;
    close $o;
    printf "%-24s FAQ %d개%s\n", $rel, scalar @qa,
           ($rel =~ /index\.html$/ ? '' : ' + 경로');
    $done++;
}

print "\n$done 개 페이지 처리 · FAQ 문답 $faqtotal 개를 구조화 데이터로 만듦\n";
print "이 사실을 확인하려면: perl _dev/seocheck.pl\n";
