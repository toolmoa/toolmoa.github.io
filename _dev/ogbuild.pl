#!/usr/bin/perl
# OG 공유 이미지(1200x630) 생성용 HTML을 페이지마다 만들어 둔다.
# 실제 PNG 변환은 _dev/ogshot.sh 가 Chrome 으로 한다.
#
# 제목·설명·아이콘은 페이지에서 그대로 읽어 온다. 따로 목록을 관리하면
# 툴을 고쳤을 때 이미지만 옛날 문구로 남는다.
use strict;
use warnings;
use utf8;

binmode STDOUT, ':encoding(UTF-8)';

my $ROOT = shift || '.';
my $OUT  = "$ROOT/_dev/ogtmp";
mkdir $OUT unless -d $OUT;

my @pages = glob("$ROOT/*.html");
push @pages, glob("$ROOT/en/*.html");

my $made = 0;
for my $path (@pages) {
    my $slug = $path;
    $slug =~ s{^\Q$ROOT\E/}{};
    # 여기서는 아직 .html 이 붙어 있다 (확장자 제거는 아래 줄)
    next if $slug =~ /^google|^naver/ || $slug eq '404.html';   # 소유확인 스텁·404
    $slug =~ s/\.html$//;
    $slug =~ s{/}{-}g;                          # en/index -> en-index

    open my $fh, '<:encoding(UTF-8)', $path or die "$path: $!";
    my $html = do { local $/; <$fh> };
    close $fh;

    my ($h1)   = $html =~ m{<h1[^>]*>(.*?)</h1>}s;
    my ($desc) = $html =~ m{<meta property="og:description" content="([^"]*)"};
    my ($icon) = $html =~ m{font-size='90'>([^<]*)</text>};
    next unless defined $h1;

    for ($h1, $desc) {
        next unless defined $_;
        s{<[^>]+>}{}g;                          # h1 안의 <span> 등 제거
        s{&amp;}{&}g; s{&lt;}{<}g; s{&gt;}{>}g; s{&nbsp;}{ }g;
        s{^\s+|\s+$}{}g;
    }
    $desc = '' unless defined $desc;
    $icon = '🧰' unless defined $icon && length $icon;

    my $en    = $slug =~ /^en-/ ? 1 : 0;
    my $brand = $en ? 'Toolmoa' : '툴모아';
    my $badge = $en ? '🔒 Files never leave your device'
                    : '🔒 파일이 서버로 올라가지 않습니다';

    # 제목이 길면 글자를 줄여 두 줄 안에 들어가게 한다
    my $size = length($h1) > 22 ? 52 : length($h1) > 14 ? 60 : 68;

    for ($h1, $desc) { s{&}{&amp;}g; s{<}{&lt;}g; s{>}{&gt;}g; }

    open my $o, '>:encoding(UTF-8)', "$OUT/$slug.html" or die $!;
    print $o <<"HTML";
<!DOCTYPE html>
<html lang="${\($en ? 'en' : 'ko')}">
<meta charset="utf-8">
<style>
  \@page { size: 1200px 630px; margin: 0; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; width: 1200px; height: 630px; overflow: hidden; }
  body {
    background: #ffffff;
    font-family: "Pretendard", "Malgun Gothic", "맑은 고딕", "Segoe UI", sans-serif;
    color: #16181d;
    display: flex; flex-direction: column;
    border-top: 14px solid #2f6df6;
    padding: 64px 72px 56px;
    word-break: keep-all;
  }
  .brand { font-size: 28px; font-weight: 700; letter-spacing: -.02em; color: #16181d; }
  .brand em { font-style: normal; color: #2f6df6; }
  .icon { font-size: 104px; line-height: 1; margin: 34px 0 20px; }
  h1 {
    font-size: ${size}px; font-weight: 800; letter-spacing: -.035em;
    line-height: 1.18; margin: 0; max-width: 940px;
  }
  p { font-size: 29px; color: #616875; line-height: 1.5; margin: 20px 0 0; max-width: 900px; }
  .foot { margin-top: auto; display: flex; align-items: center; gap: 18px; }
  .badge {
    font-size: 23px; color: #17864a; background: #f6f7f9;
    border: 1px solid #e2e5ea; border-radius: 999px; padding: 9px 20px;
  }
  .url { font-size: 23px; color: #98a0ac; margin-left: auto; }
</style>
<div class="brand">${\($en ? '<em>Tool</em>moa' : '툴<em>모아</em>')}</div>
<div class="icon">$icon</div>
<h1>$h1</h1>
<p>$desc</p>
<div class="foot">
  <span class="badge">$badge</span>
  <span class="url">toolmoa.github.io</span>
</div>
</html>
HTML
    close $o;
    $made++;
}

print "OG 템플릿 $made 개 생성 → $OUT\n";
