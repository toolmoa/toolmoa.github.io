#!/usr/bin/perl
# 구조화 데이터·공유 메타 점검.
#
# 만든 코드로 만든 결과를 검사하면 순환 논증이므로, JSON 은 직접 짠 파서가 아니라
# 코어 모듈 JSON::PP 로 실제 파싱한다. 그리고 문답은 JSON 쪽에서 꺼낸 문자열이
# 정말 화면 HTML 안에 있는지 거꾸로 대조한다 (구글은 화면과 다른 FAQ 를 벌준다).
use strict;
use warnings;
use utf8;
use JSON::PP;
binmode STDOUT, ':encoding(UTF-8)';

my $ROOT = shift || '.';
my $BASE = 'https://toolmoa.github.io';
my @files = (glob("$ROOT/*.html"), glob("$ROOT/en/*.html"));

my ($pass, $fail) = (0, 0);
sub ok   { $pass++ }
sub bad  { my ($f, $m) = @_; $fail++; print "  ✗ $f — $m\n" }

sub strip {
    my $s = shift // '';
    $s =~ s{<br\s*/?>}{ }gi; $s =~ s{<[^>]+>}{}g;
    $s =~ s{&nbsp;}{ }g; $s =~ s{&amp;}{&}g;
    $s =~ s{&lt;}{<}g; $s =~ s{&gt;}{>}g; $s =~ s{&quot;}{"}g;
    $s =~ s{\s+}{ }g; $s =~ s{^\s+|\s+$}{}g; return $s;
}

my $faqseen = 0;
for my $path (@files) {
    my $rel = $path; $rel =~ s{^\Q$ROOT\E/}{};
    next if $rel =~ /^google|^naver/ || $rel eq '404.html';

    open my $fh, '<:encoding(UTF-8)', $path or die $!;
    my $html = do { local $/; <$fh> };
    close $fh;

    my $isen = $rel =~ m{^en/} ? 1 : 0;
    my $home = $rel =~ /index\.html$/ ? 1 : 0;

    # --- 1. 필수 메타가 다 있는가 ---
    for my $m (qw(og:type og:url og:site_name og:image og:image:width
                  og:image:height og:image:alt og:title og:description og:locale)) {
        $html =~ m{<meta property="\Q$m\E" content="[^"]+"}
            ? ok() : bad($rel, "$m 없음");
    }
    for my $m (qw(twitter:card twitter:title twitter:description twitter:image theme-color)) {
        $html =~ m{<meta name="\Q$m\E" content="[^"]+"}
            ? ok() : bad($rel, "$m 없음");
    }

    # 같은 태그가 두 번 들어가면 크롤러가 어느 쪽을 쓸지 모른다
    for my $m (qw(og:type og:image og:url)) {
        my $n = () = $html =~ m{<meta property="\Q$m\E"}g;
        $n == 1 ? ok() : bad($rel, "$m 이 $n 개 (1개여야 함)");
    }

    # --- 2. og:url 이 canonical 과 같은가 ---
    my ($canon) = $html =~ m{<link rel="canonical" href="([^"]+)"};
    my ($ogurl) = $html =~ m{<meta property="og:url" content="([^"]+)"};
    (defined $canon && defined $ogurl && $canon eq $ogurl)
        ? ok() : bad($rel, "og:url 과 canonical 불일치");

    # --- 3. og:image 가 진짜 있는 파일인가 (절대주소여야 한다) ---
    my ($ogimg) = $html =~ m{<meta property="og:image" content="([^"]+)"};
    if (!defined $ogimg || $ogimg !~ m{^\Q$BASE\E/}) {
        bad($rel, "og:image 가 절대주소가 아님");
    } else {
        my $local = $ogimg; $local =~ s{^\Q$BASE\E/}{$ROOT/};
        -s $local ? ok() : bad($rel, "og:image 파일 없음: $local");
    }

    # --- 4. JSON-LD 를 실제로 파싱한다 ---
    my @blocks = $html =~ m{<script type="application/ld\+json">\s*(.*?)\s*</script>}gs;
    @blocks ? ok() : bad($rel, "ld+json 없음");

    my %types;
    for my $b (@blocks) {
        my $data = eval { JSON::PP->new->utf8(0)->decode($b) };
        if ($@ || !$data) { bad($rel, "JSON 파싱 실패: $@"); next; }
        ok();
        $types{ $data->{'@type'} // '?' } = $data;
    }

    # --- 5. FAQPage 가 화면 문답과 일치하는가 ---
    my @htmlq;
    while ($html =~ m{<details[^>]*>(.*?)</details>}gs) {
        my $blk = $1;
        my ($q) = $blk =~ m{<summary[^>]*>(.*?)</summary>}s;
        push @htmlq, strip($q) if defined $q;
    }
    if (@htmlq) {
        my $faq = $types{FAQPage};
        if (!$faq) { bad($rel, "화면에 문답 " . scalar(@htmlq) . "개가 있는데 FAQPage 없음"); }
        else {
            my @jq = map { $_->{name} } @{ $faq->{mainEntity} || [] };
            scalar(@jq) == scalar(@htmlq)
                ? ok() : bad($rel, "문답 수가 다름 (화면 " . scalar(@htmlq) . " / JSON " . scalar(@jq) . ")");
            for my $q (@jq) {
                # JSON 안의 질문이 화면 목록에 실제로 있는가
                (grep { $_ eq $q } @htmlq) ? ok() : bad($rel, "화면에 없는 질문: $q");
                $faqseen++;
            }
            for my $e (@{ $faq->{mainEntity} || [] }) {
                my $a = $e->{acceptedAnswer}{text} // '';
                length($a) >= 10 ? ok() : bad($rel, "답이 비었거나 너무 짧음: $e->{name}");
            }
        }
    }

    # --- 6. BreadcrumbList (홈 제외) ---
    if ($home) {
        $types{BreadcrumbList} ? bad($rel, "홈에는 경로가 없어야 함") : ok();
    } else {
        my $bc = $types{BreadcrumbList};
        if (!$bc) { bad($rel, "BreadcrumbList 없음"); }
        else {
            my @it = @{ $bc->{itemListElement} || [] };
            scalar(@it) == 2 ? ok() : bad($rel, "경로 단계가 " . scalar(@it) . "개");
            ($it[0]{item} // '') eq ($isen ? "$BASE/en/" : "$BASE/")
                ? ok() : bad($rel, "경로 1단계가 홈이 아님");
            ($it[1]{item} // '') eq ($canon // '')
                ? ok() : bad($rel, "경로 2단계가 canonical 과 다름");
        }
    }
}

print "\n";
print "확인한 문답 $faqseen 개\n";
printf "통과 %d · 실패 %d\n", $pass, $fail;
print $fail ? "구조화 데이터: 문제 있음\n" : "구조화 데이터: 문제 없음\n";
exit($fail ? 1 : 0);
