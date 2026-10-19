# -*- coding: utf-8 -*-
"""한국어 툴 페이지에서 영어판(en/*.html)을 만든다.

    python -I _dev/mken.py image-watermark image-split pdf-watermark qr-scan

하는 일
  - data-i18n / data-i18n-ph 가 붙은 요소의 글을 assets/i18n.js 의 en 사전 값으로 바꾸고 속성을 뗀다
  - 스크립트 안의 t('key', '한국어') 호출을 영어 문자열 리터럴로 바꾼다 (영어판에는 i18n.js 가 없어 t() 가 없다)
  - <head> 의 제목·설명·canonical·hreflang·og 를 아래 PAGES 표의 영어로 바꾼다
  - data-ko-only 로 표시된 한국어 전용 본문(설명·FAQ)을 아래 PAGES 표의 영어 본문으로 통째로 바꾼다
  - 메뉴는 비워 둔다. 끝나면 perl _dev/ennav.pl 로 채울 것

영어판은 번역본이 아니라 "업로드하지 않는다"를 축으로 다시 쓴 글이어야 하므로, 본문·FAQ 는 여기 표에 직접 적는다.
"""
import io, re, sys, json

ROOT = __file__.replace('\\', '/').rsplit('/_dev/', 1)[0]

# ---------- en 사전 읽기 ----------
src = io.open(ROOT + '/assets/i18n.js', encoding='utf-8').read()
en_block = src[src.index('    en: {'):src.index('    ja: {')]
EN = {}
for m in re.finditer(r"'((?:[^'\\]|\\.)*)':\s*'((?:[^'\\]|\\.)*)'", en_block):
    EN[m.group(1)] = m.group(2).replace("\\'", "'").replace('\\\\', '\\')

def js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

# ---------- 페이지별 영어 머리글·본문 ----------
PAGES = {
 'image-watermark': dict(
   title='Add a watermark to photos without uploading — text or logo, free',
   desc='Stamp text or a logo on many photos at once, inside your browser. Choose position, size, opacity and angle, or tile it across the image. Nothing is uploaded.',
   og_t='Add a watermark to photos without uploading',
   og_d='Text or logo on many photos at once, with position, opacity and tiling. Runs in your browser.',
   name='Photo watermark', cat='MultimediaApplication',
   aria={'파일 선택': 'Choose a file', '워터마크 미리보기': 'Watermark preview'},
   attrs=[('value="© 툴모아"', 'value="© Toolmoa"')],
   body='''  <h2>Why do it in the browser</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      The photos people watermark are the ones they are about to publish — product shots, portfolio work, pictures of their children on a blog.
      Most "watermark online" services start by uploading the originals, unmarked, to a server you know nothing about. Here the stamping is done by
      your own browser: nothing leaves your device, the page keeps working offline, and there is no limit on how many photos you process.
      A small mark in a corner looks best but is easy to crop off; a tiled mark cannot be removed but covers the picture. Product photos usually
      take a corner mark; anything you do not want reused takes the tiled one.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Are my photos uploaded anywhere?</summary>
      <p>No. Photos are opened, stamped and saved entirely inside your browser. The page keeps working with the internet switched off, which is the easiest way to check. That is also why dozens of photos finish in seconds — there is no upload.</p>
    </details>
    <details>
      <summary>Why is the mark a different size on each photo?</summary>
      <p>Size is set as a share of the photo's width, not in pixels. A 4000-pixel photo and an 800-pixel photo both get a mark a quarter of their width at 25%, so a batch looks consistent. Pixel sizes would make the mark huge on small images and invisible on large ones.</p>
    </details>
    <details>
      <summary>My logo appears inside a white box</summary>
      <p>The logo file has a white background baked in. Use a PNG with a transparent background — export it with "transparent background" or "alpha channel" from the program that made it.</p>
    </details>
    <details>
      <summary>Can the watermark be removed later?</summary>
      <p>Not from the saved file: the mark is drawn over the original pixels. Your original photo is untouched, so keep it and publish only the watermarked copy.</p>
    </details>
    <details>
      <summary>Does saving reduce quality?</summary>
      <p>With "Same as the original", JPG photos are saved as JPG at 92% quality and PNG as PNG. Dimensions are never changed. Even with a transparent logo, JPG is fine because the background is the photo itself.</p>
    </details>
    <details>
      <summary>Does it work on a phone?</summary>
      <p>Yes. Several photos are delivered as one ZIP, because phone browsers often keep only the first file of a series of downloads.</p>
    </details>
  </div>
'''),
 'image-split': dict(
   title='Split an image into a grid — Instagram 3×3 and carousel, free',
   desc='Cut one picture into a 3×3 Instagram grid, a 1×3 carousel or any grid and save the pieces as one ZIP. Runs in your browser; nothing is uploaded.',
   og_t='Split an image into a grid without uploading',
   og_d='Instagram 3×3 grid, carousel strips or custom grids. Pieces saved as one ZIP, inside your browser.',
   name='Image splitter', cat='MultimediaApplication',
   aria={'파일 선택': 'Choose a file', '분할 미리보기': 'Split preview'},
   attrs=[],
   body='''  <h2>Which split to choose</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Instagram profile grid</strong> — 9 pieces (3×3). The profile shows three squares per row, so pieces must be square. Post them in reverse order, 9 first.<br>
      <strong style="color:var(--text)">Swipeable panorama (carousel)</strong> — 3 pieces (1×3). A wide photo cut into three posted in one carousel looks continuous when swiped. Pick "As is" so nothing is trimmed top and bottom.<br>
      <strong style="color:var(--text)">Printing a large picture</strong> — Custom. Split "As is" across several sheets, then print each sheet borderless and tape them together.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my photo uploaded anywhere?</summary>
      <p>No. The photo is cut and saved inside your browser. The page keeps working with the internet switched off.</p>
    </details>
    <details>
      <summary>What is the difference between "Square" and "As is"?</summary>
      <p>"Square" first trims the edges around the centre so every piece is a perfect square, which is what an Instagram profile grid needs. "As is" discards nothing and simply divides the photo into equal parts — right for carousels and printing.</p>
    </details>
    <details>
      <summary>How are the files named?</summary>
      <p>The original name plus a number. Number 1 is the top-left piece, counting left to right and then down: in a 3×3 grid the first row is 1·2·3 and the second row 4·5·6. For an Instagram grid, post 9 first and 1 last so the profile shows the original picture.</p>
    </details>
    <details>
      <summary>What if the size does not divide evenly?</summary>
      <p>The few leftover pixels are dropped at the edges. 1000 pixels into three columns gives three 333-pixel pieces with one pixel spare — not something you can see.</p>
    </details>
    <details>
      <summary>Is quality reduced?</summary>
      <p>Each piece is a straight copy of that part of the original — no scaling. With "Same as the original", JPG stays JPG at 92% quality and PNG stays PNG. For images full of text, PNG is sharper.</p>
    </details>
    <details>
      <summary>Does it work on a phone?</summary>
      <p>Yes. Pieces come as one ZIP by default; unzip it in your files app and the pieces appear as photos. Untick "One ZIP file" to save them individually — your browser may then ask permission for multiple downloads.</p>
    </details>
  </div>
'''),
 'pdf-watermark': dict(
   title='Add a watermark to a PDF without uploading — every page, free',
   desc='Stamp "Confidential", a name or a logo on every page of a PDF inside your browser. Any language, chosen pages, diagonal or tiled. Nothing is uploaded.',
   og_t='Add a watermark to a PDF without uploading it',
   og_d='Text or logo on every page, any language, in your browser. Nothing is uploaded.',
   name='PDF watermark', cat='UtilitiesApplication',
   aria={'파일 선택': 'Choose a file', '워터마크 미리보기': 'Watermark preview'},
   attrs=[('value="대외비"', 'value="Confidential"'), ('data-fill="대외비"', 'data-fill="Confidential"'), ('data-fill="사본"', 'data-fill="Copy"'),
          ('data-fill="초안 — 배포 금지"', 'data-fill="Draft — do not distribute"'), ('data-fill="견본"', 'data-fill="Sample"')],
   body='''  <h2>When a watermark is worth it</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Contracts, quotes, proposals, course hand-outs — <strong style="color:var(--text)">documents meant for a specific recipient</strong>.
      A faint "Confidential" or the recipient's own name across every page tells you where a leaked copy came from and makes people think twice before forwarding it.
      Writing "for XYZ application only" across a scan of your passport or a bank statement works the same way. Those are exactly the files you should not
      upload to a random website, which is why this page does the stamping inside your browser and sends nothing anywhere.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my PDF uploaded anywhere?</summary>
      <p>No. The PDF is opened, stamped and saved inside your browser. The page keeps working with the internet switched off. It was built for contracts and ID scans, the files that must not leave your computer.</p>
    </details>
    <details>
      <summary>Does it support my language?</summary>
      <p>Yes, any script — Korean, Japanese, Arabic, emoji. Instead of embedding a PDF font, the text is drawn exactly as your screen shows it and stamped as an image, so no font files are needed. The one trade-off is that the watermark text cannot be selected or copied in the PDF, which for a watermark is usually what you want.</p>
    </details>
    <details>
      <summary>Can the watermark be removed?</summary>
      <p>It is a separate image layered on each page, so a PDF editor could pick it out and delete it. For a mark that cannot be separated, convert the pages to images with <a href="pdf-to-image.html">PDF to image</a> and rebuild the file with <a href="img-to-pdf.html">image to PDF</a>. Text selection is lost, but the mark becomes part of the page.</p>
    </details>
    <details>
      <summary>What opacity should I use?</summary>
      <p>15–30% if the document still has to be read. 100% hides whatever is underneath. The preview shows the mark on a blank page, so open the saved file once to check it over the real content.</p>
    </details>
    <details>
      <summary>What about password-protected PDFs?</summary>
      <p>They cannot be opened. Remove the password and save a copy first. PDFs that merely restrict editing usually work.</p>
    </details>
    <details>
      <summary>Will the file get much bigger?</summary>
      <p>No. One watermark image is added and every page shares it, so even long documents grow by only tens or hundreds of kilobytes.</p>
    </details>
  </div>
'''),
 'qr-scan': dict(
   title='Scan a QR code from an image — read QR codes on PC, free',
   desc='Upload or paste a QR code screenshot or photo and read what is inside, no phone needed. Wi-Fi, contact and SMS codes are decoded into fields. Nothing is uploaded.',
   og_t='Scan a QR code from an image on your PC',
   og_d='Read QR codes from screenshots, photos or your camera. Decoded in your browser; nothing is uploaded.',
   name='QR code reader', cat='UtilitiesApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>When you need to read a QR code without a phone</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      A QR code on your own screen is the awkward case: pointing a phone at a monitor is slow and often fails. Take a screenshot and paste it here instead,
      and the contents appear as text. The same goes for a QR image in an email, a photo of a poster, or the Wi-Fi sticker in a café.
      <strong style="color:var(--text)">The image never leaves your browser</strong>, so whatever the code contains — an address, a login, a contact —
      stays with you. Wi-Fi codes are split into network name and password, and contact codes into name, phone and email.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my image uploaded anywhere?</summary>
      <p>No. Decoding happens inside your browser and the result is not sent anywhere either. The page keeps working offline. Camera frames are processed on screen only and never recorded.</p>
    </details>
    <details>
      <summary>It says no QR code was found</summary>
      <p>Codes smaller than about 100 pixels across, blurry, badly reflected or photographed at a steep angle fail. For a screenshot, zoom the code in and capture again; for a photo, retake it with the code filling at least half the frame. Inverted codes (light on dark) are tried automatically.</p>
    </details>
    <details>
      <summary>The camera does not turn on</summary>
      <p>Allow camera access when the browser asks; you can change it later from the lock icon in the address bar. On a PC without a camera, photograph the code and upload it, or paste a screenshot.</p>
    </details>
    <details>
      <summary>I read a Wi-Fi code — how do I connect?</summary>
      <p>The network name (SSID) and password are shown separately. Copy the password into your computer's Wi-Fi dialog. On a phone, the built-in camera app connects directly from the same code.</p>
    </details>
    <details>
      <summary>Is it safe to open the link?</summary>
      <p>Anyone can print a QR code, and stickers on posters are sometimes swapped for fake ones. That is why the address is shown first instead of being opened. Check that the domain — the part before the first slash — is the one you expect, and be extra careful with shortened links, which hide their destination.</p>
    </details>
  </div>
'''),
}

def convert(slug):
    cfg = PAGES[slug]
    h = io.open(ROOT + '/' + slug + '.html', encoding='utf-8').read()

    # ---- head ----
    h = h.replace('<html lang="ko">', '<html lang="en">', 1)
    h = re.sub(r'<title>.*?</title>', '<title>' + cfg['title'].replace('&', '&amp;') + '</title>', h, 1)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + cfg['desc'] + '">', h, 1)
    ko_url = 'https://toolmoa.github.io/' + slug + '.html'
    en_url = 'https://toolmoa.github.io/en/' + slug + '.html'
    h = re.sub(r'<link rel="canonical" href="[^"]*">(\n<link rel="alternate"[^>]*>)*',
               '<link rel="canonical" href="' + en_url + '">\n'
               '<link rel="alternate" hreflang="ko" href="' + ko_url + '">\n'
               '<link rel="alternate" hreflang="en" href="' + en_url + '">\n'
               '<link rel="alternate" hreflang="x-default" href="' + ko_url + '">', h, 1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + cfg['og_t'] + '">', h, 1)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + cfg['og_d'] + '">', h, 1)
    h = h.replace('<meta property="og:locale" content="ko_KR">', '<meta property="og:locale" content="en_US">')
    h = h.replace('href="assets/', 'href="../assets/').replace('src="assets/', 'src="../assets/')
    # 스크립트가 나중에 받는 라이브러리 경로도 한 단계 위다 (needScript('PDFLib', 'assets/vendor/…'))
    h = h.replace("'assets/vendor/", "'../assets/vendor/")
    h = re.sub(r'\n<script src="\.\./assets/i18n\.js" defer></script>', '', h)
    h = re.sub(r'\{"@context":"https://schema\.org","@type":"WebApplication","name":"[^"]*","applicationCategory":"[^"]*","operatingSystem":"All","offers":\{"@type":"Offer","price":"0","priceCurrency":"KRW"\},"inLanguage":"ko-KR"\}',
               '{"@context":"https://schema.org","@type":"WebApplication","name":"' + cfg['name'] + '","applicationCategory":"' + cfg['cat'] + '","operatingSystem":"All","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"inLanguage":"en"}', h, 1)
    h = re.sub(r'\n<!-- SEO:AUTO.*?/SEO:AUTO -->', '', h, flags=re.S)   # 생성기가 다시 넣는다
    h = re.sub(r'<body data-i18n-title="[^"]*">', '<body>', h, 1)

    # ---- 머리글: 로고·언어 링크. 메뉴는 ennav.pl 이 채운다 ----
    h = h.replace('<a class="logo" href="index.html" data-i18n="brand">툴<span>모아</span></a>', '<a class="logo" href="index.html">Tool<span>moa</span></a>')
    h = re.sub(r'(    <nav class="site-nav">\n)(.*?)(    </nav>\n)', r'\1\3    <a class="lang-link" href="../' + slug + r'.html" hreflang="ko">한국어</a>\n', h, 1, flags=re.S)

    # ---- data-i18n 치환 ----
    missing = []
    def sub_i18n(m):
        tag, attrs, key, rest, inner = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        if key not in EN: missing.append(key); return m.group(0)
        attrs2 = (attrs + rest).replace('  ', ' ').rstrip()
        return '<' + tag + attrs2 + '>' + EN[key] + '</' + tag + '>'
    # 안쪽에 태그가 없는 요소 (대부분)
    h = re.sub(r'<(\w+)([^>]*?) data-i18n="([^"]+)"([^>]*)>([^<]*)</\1>', sub_i18n, h)
    # 안쪽에 <strong>·<a> 가 있는 문단 (cross 링크 등) — 가장 가까운 닫는 태그까지
    h = re.sub(r'<(p|span|div)([^>]*?) data-i18n="([^"]+)"([^>]*)>((?:(?!</\1>).)*?)</\1>', sub_i18n, h, flags=re.S)
    def sub_ph(m):
        key = m.group(2)
        if key not in EN: missing.append(key); return m.group(0)
        return m.group(1).replace(m.group(0), '')
    h = re.sub(r'placeholder="[^"]*"([^>]*?) data-i18n-ph="([^"]+)"', lambda m: 'placeholder="' + EN.get(m.group(2), '?') + '"' + m.group(1), h)
    h = re.sub(r' data-i18n-ph="([^"]+)"( [^>]*?)placeholder="[^"]*"', lambda m: m.group(2) + 'placeholder="' + EN.get(m.group(1), '?') + '"', h)
    assert 'data-i18n' not in h, ('data-i18n 잔존', re.findall(r'data-i18n[^ >]*', h)[:5])

    # ---- 한국어 전용 본문 → 영어 본문 ----
    start = h.index('  <h2 data-ko-only>')
    end = h.index('</main>')
    h = h[:start] + cfg['body'] + h[end:]
    h = h.replace('<!-- AD:', '<!-- AD:EN_')

    # ---- aria-label · 고정 속성 ----
    for k, v in cfg['aria'].items():
        h = h.replace('aria-label="' + k + '"', 'aria-label="' + v + '"')
    for a, b in cfg['attrs']:
        assert a in h, a
        h = h.replace(a, b)

    # ---- 바닥글 둘째 줄 ----
    h = h.replace('      <a href="privacy.html" data-i18n="foot.privacy">개인정보처리방침</a>', '      <a href="../privacy.html">Privacy</a>')
    h = re.sub(r'<nav>\n      <a href="privacy\.html">[^<]*</a>\n      <a href="terms\.html">[^<]*</a>\n      <a href="licenses\.html">[^<]*</a>\n    </nav>',
               '<nav>\n      <a href="../privacy.html">Privacy</a>\n      <a href="../terms.html">Terms</a>\n      <a href="../licenses.html">Open source</a>\n    </nav>', h)
    h = h.replace('<div>© Toolmoa · Everything runs inside your browser</div>', '<div>© Toolmoa · Everything runs inside your browser</div>')

    # ---- 스크립트: t('key', '…') → 영어 리터럴 ----
    def sub_t(m):
        key = m.group(1)
        if key not in EN: missing.append(key); return m.group(0)
        return js_str(EN[key])
    h = re.sub(r"\bt\('([^']+)',\s*'(?:[^'\\]|\\.)*'\)", sub_t, h)
    h = h.replace("'붙여넣은-사진-'", "'pasted-image-'")
    h = re.sub(r"\n[^\n]*addEventListener\('langchange'[^\n]*", '', h)
    # 로컬 링크는 같은 폴더의 영어판을 가리킨다 (전부 영어판이 있는 툴만 cross 에 적었다)
    left_t = re.findall(r"(?<![\w.])t\('[^']*'", h)   # getContext('2d') 처럼 't(' 로 끝나는 이름은 제외
    assert not left_t, ('script 에 t() 잔존', left_t[:5])
    assert not missing, ('사전에 없는 키', missing)
    left = re.findall(r'[가-힣]+', re.sub(r'//[^\n]*|/\*.*?\*/|한국어', '', h, flags=re.S))
    io.open(ROOT + '/en/' + slug + '.html', 'w', encoding='utf-8', newline='\n').write(h)
    print(slug, '→ en/' + slug + '.html', '한글 잔존:', left[:8] if left else '없음')

for s in sys.argv[1:]:
    convert(s)
