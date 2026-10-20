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
import io, re, sys, json, os

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
 'romanize': dict(
   title="Romanize a Korean name — Revised Romanization converter, free",
   desc="Convert Korean names to the Latin alphabet: official Revised Romanization plus the common Kim, Lee and Park spellings, whole lists at once. Runs in your browser.",
   og_t="Romanize a Korean name in your browser",
   og_d="Official Revised Romanization and common surname spellings, side by side. Lists convert at once.",
   name="Korean romanizer", cat="UtilitiesApplication",
   aria={"변환 결과": "Results"},
   attrs=[],
   body='''  <h2>Which spelling should you use</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      South Korea's official system is the <strong style="color:var(--text)">Revised Romanization of Korean (2000)</strong>: 김 is Gim, 이 is I, 박 is Bak. Road signs,
      textbooks and government documents follow it. Real people mostly do not: the overwhelming majority of Kims spell it Kim, and Lee and Park are far more common
      than I and Bak. Passports accept either. The converter shows both — the <strong style="color:var(--text)">"Other spelling"</strong> column is the surname in the opposite system —
      so you can match a family member's passport or an existing document instead of guessing. Given names follow the official rules in both modes.
      For a passport, write the given name as one word in capitals (GILDONG); a hyphen (GIL-DONG) is allowed but sometimes gets mangled into a middle name abroad.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Are the names I type sent anywhere?</summary>
      <p>No. The conversion runs inside your browser and nothing is transmitted. The page keeps working with the internet switched off, so it is fine to paste an entire class list or staff roster.</p>
    </details>
    <details>
      <summary>What is the difference between "Person's name" and "Place names · words"?</summary>
      <p>The official system spells words the way they are pronounced: 신라 is Silla because it is pronounced [실라], and 종로 is Jongno. Personal names are the exception — they are spelled syllable by syllable without those sound changes, so 빛나 is Bitna even though it is pronounced [빈나]. Choose "Person's name" for people and "Place names · words" for everything else; the second mode applies consonant assimilation, palatalization, ㅎ contraction and liaison.</p>
    </details>
    <details>
      <summary>Does it handle two-syllable surnames?</summary>
      <p>Yes — 남궁, 황보, 제갈, 선우, 독고, 사공, 서문 and 동방 are recognized automatically. If you put a space between surname and given name ("남궁 민") that split is used as-is, which also works for any unusual name.</p>
    </details>
    <details>
      <summary>Why eo and eu instead of u?</summary>
      <p>Those are the official spellings of ㅓ and ㅡ: 서 is Seo and 은 is Eun. Many Koreans prefer u (Sun, Jung) because it reads more naturally in English — that is a customary spelling, not an official one. Copy the result and change the syllables you want.</p>
    </details>
    <details>
      <summary>Can I get the output into a spreadsheet?</summary>
      <p>"Copy Korean + English" copies each line as Korean, a tab, then the romanization. Pasting into Excel or Google Sheets puts them in two columns.</p>
    </details>
  </div>
'''),
 'image-resize': dict(
   title='Resize an image to exact pixels or percent — free, no upload',
   desc='Resize photos to an exact width and height or by percent, in your browser. YouTube, Instagram and profile presets, many photos to one ZIP. Nothing is uploaded.',
   og_t='Resize an image without uploading it',
   og_d='Exact pixels or percent, YouTube and Instagram presets, many photos at once. Runs in your browser.',
   name='Image resizer', cat='MultimediaApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>Resizing is not the same as compressing</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      "Make the picture smaller" means two different things: fewer <strong style="color:var(--text)">pixels</strong> (4000 wide down to 1280) or a smaller
      <strong style="color:var(--text)">file</strong> (5&nbsp;MB down to 500&nbsp;KB). If a form says "no wider than 1000 pixels", this is the page; if it says
      "under 2&nbsp;MB", use <a href="image-compress.html">compress image</a>. For a fixed format — a YouTube thumbnail at 1280×720, an Instagram square at
      1080×1080 — pick the preset and "Fill and crop": you get exactly that size even if the photo's shape differs. Enlarging a small photo only makes it
      blurry, so enlarging is blocked by default; untick the box only when you really need the bigger pixel count. Everything is resized by your own browser,
      which is why a batch of fifty photos takes seconds and nothing is uploaded.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Are my photos uploaded anywhere?</summary>
      <p>No. Resizing happens inside your browser and the result is saved straight to your device. The page keeps working with the internet switched off, which is the easiest way to check. It is also why dozens of photos finish without a wait — there is no upload.</p>
    </details>
    <details>
      <summary>What happens to a photo of a different shape at 1080×1080?</summary>
      <p>"Keep ratio" fits the width to 1080 and lets the height follow, so the result is not a perfect square. "Fill and crop" trims the overflow around the centre and gives exactly 1080×1080. "Fit everything and pad" keeps the whole photo and fills the rest with the padding colour. "Stretch" distorts the picture, so use it only when you must.</p>
    </details>
    <details>
      <summary>Does enlarging improve quality?</summary>
      <p>No. Pixels that were never captured have to be invented, so the bigger you go the blurrier it gets. That is why "Never enlarge beyond the original" is on by default. Untick it only when a print shop insists on a pixel count your photo does not have.</p>
    </details>
    <details>
      <summary>Which format should I save in?</summary>
      <p>JPG for photographs, PNG for text, logos and anything with a transparent background, WebP for the smallest files on the web. "Same as the original" keeps JPG as JPG and PNG as PNG. JPG and WebP are saved at 92% quality.</p>
    </details>
    <details>
      <summary>Is the camera and location data kept?</summary>
      <p>No. A resized photo is a freshly drawn image, so the GPS position and camera details of the original are not carried over. To keep the photo as it is and strip only that data, use <a href="image-exif.html">remove photo location</a>.</p>
    </details>
    <details>
      <summary>Does it work on a phone?</summary>
      <p>Yes. Several photos are delivered as one ZIP, because phone browsers often keep only the first file of a series of downloads. Untick "Several photos → one ZIP" to save them one by one.</p>
    </details>
  </div>
'''),
 'image-transparent': dict(
   title='Make a white background transparent — logo to PNG, free',
   desc='Remove the white or any chosen background from a logo, stamp or signature and save a transparent PNG in your browser. Tolerance and soft edges. Nothing is uploaded.',
   og_t='Make a white background transparent',
   og_d='Logos, stamps, signatures and drawings to transparent PNG, in your browser. Nothing is uploaded.',
   name='Transparent background maker', cat='MultimediaApplication',
   aria={'파일 선택': 'Choose a file', '결과 미리보기 — 클릭하면 그 자리 색을 지울 색으로 고릅니다': 'Result preview — click a spot to use its colour as the one to remove'},
   attrs=[],
   body='''  <h2>What it is for</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Scanned signatures and stamps</strong> — a signature on paper comes with the paper. Remove the white and it can sit on any document.<br>
      <strong style="color:var(--text)">Logos</strong> — a JPG logo in a white box looks wrong on a photo or a coloured background. As a transparent PNG the box disappears.<br>
      <strong style="color:var(--text)">Drawings and characters</strong> — pencil sketches and hand lettering that you want to use as stickers or profile pictures.<br>
      Cutting a person or an object out of a photograph is a different job: that needs a program that recognises shapes, not colours. This page is for
      <strong style="color:var(--text)">pictures whose background is a single colour</strong>. It runs entirely inside your browser, which matters for signatures
      and company stamps — the one kind of image you should never hand to a website.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my picture uploaded anywhere?</summary>
      <p>No. The picture is opened, edited and saved inside your browser. The page keeps working with the internet switched off. It was built for signatures and stamps, exactly the images that must not leave your device.</p>
    </details>
    <details>
      <summary>What does "only background connected to the outside" mean?</summary>
      <p>Removal starts at the edges of the picture and spreads only through connected background. The inside of an "O", the white of an eye, a white box inside a logo — same colour, but not connected to the outside — are kept. "Every pixel of that colour" removes the colour wherever it appears. For logos and stamps the first mode is usually right.</p>
    </details>
    <details>
      <summary>Patches of background remain</summary>
      <p>White paper in a scan or photo is never pure white; it is a mix of light greys and yellows. Raise the tolerance and those shades count as background too. If lines and letters start to fade, you have gone too far.</p>
    </details>
    <details>
      <summary>The edges look jagged</summary>
      <p>Turn on "Soften edges": pixels close to the background colour become partly transparent, so the outline blends in. Thin signatures usually look better with it on; logos with crisp colour boundaries are sometimes cleaner with it off.</p>
    </details>
    <details>
      <summary>Can I save as JPG?</summary>
      <p>No — JPG has no transparency. A transparent image has to be PNG, so PNG is the only output. If the file is large, <a href="image-compress.html">compress image</a> can turn it into WebP, which keeps the transparency and is much smaller.</p>
    </details>
    <details>
      <summary>I clicked a colour inside the picture and nothing happened</summary>
      <p>With "only background connected to the outside", a colour that does not touch the edge is never reached. Switch to "Every pixel of that colour" and the colour you picked is removed everywhere.</p>
    </details>
  </div>
'''),
 'color-convert': dict(
   title='Color code converter — HEX, RGB, HSL, CMYK and WCAG contrast',
   desc='Convert HEX, RGB, HSL, HSV, CMYK and CSS color names in one place, check the WCAG contrast ratio of two colors and build palettes. Runs in your browser.',
   og_t='Color code converter and contrast checker',
   og_d='HEX, RGB, HSL, HSV, CMYK and color names, WCAG contrast ratio, tints and palettes. In your browser.',
   name='Color code converter', cat='DesignApplication',
   aria={'색 고르기': 'Pick a color', '변환 결과': 'Results', '글자 색 고르기': 'Pick the text color', '배경 색 고르기': 'Pick the background color'},
   attrs=[('Aa 가나다', 'Aa Bb Cc')],
   body='''  <h2>Which format is used where</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">HEX (#2f6df6)</strong> — web and app design, CSS, Figma. The most common form. Two extra digits at the end (#2f6df680) are the alpha, or opacity.<br>
      <strong style="color:var(--text)">RGB (47, 109, 246)</strong> — the "custom color" dialog in Photoshop, PowerPoint, Word and most office software takes these three numbers.<br>
      <strong style="color:var(--text)">HSL (216°, 92%, 57%)</strong> — hue, saturation and lightness. The easiest form for a human to adjust: "the same color, a little lighter" is one number.<br>
      <strong style="color:var(--text)">HSV / HSB</strong> — the H·S·B fields of the Photoshop color picker. Similar to HSL but with a different definition of brightness.<br>
      <strong style="color:var(--text)">CMYK</strong> — for print. Screens and ink work differently, so these values are an approximation; always check a real print against a swatch book.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is anything I type sent anywhere?</summary>
      <p>No. Conversion and contrast calculation happen inside your browser. The page keeps working with the internet switched off.</p>
    </details>
    <details>
      <summary>Which formats can I enter?</summary>
      <p>HEX such as #fff, #ffffff or #ffffff80; rgb(255,0,0) and rgba(255,0,0,.5); hsl(120,100%,50%); and all 148 CSS color names such as red, tomato or steelblue. 2f6df6 without the # works too.</p>
    </details>
    <details>
      <summary>What does a contrast ratio of 4.5:1 mean?</summary>
      <p>It compares the brightness of the text color with the background. Black on white is the maximum at 21:1; identical colors are 1:1. The Web Content Accessibility Guidelines (WCAG) ask for at least 4.5:1 for body text and 3:1 for large text and icons at level AA, and 7:1 and 4.5:1 at level AAA. Grey text that is hard to read usually fails even 3:1.</p>
    </details>
    <details>
      <summary>The CMYK values differ from my printer's</summary>
      <p>Screens (RGB) and ink (CMYK) can reproduce different ranges of color, so there is no exact conversion. The values here come from the common simple formula; every program differs by a few percent depending on its color profile. Check printed work against a physical swatch.</p>
    </details>
    <details>
      <summary>How are the palettes built?</summary>
      <p>The tints and shades change only the HSL lightness in 10% steps. The complement sits opposite on the color wheel (180°), analogous colors are 30° either side, and the triad is spaced at 120°. Use them as a starting point for hover and pressed states of a button or for chart colors.</p>
    </details>
  </div>
'''),
 'barcode': dict(
   title='Barcode generator — EAN-13, EAN-8 and Code 128, free, saves PNG',
   desc='Generate EAN-13, EAN-8 and Code 128 barcodes and save them as PNG. Check digits are calculated and verified; bar width and height adjustable. Nothing is uploaded.',
   og_t='Barcode generator — EAN-13, EAN-8 and Code 128',
   og_d='Product barcodes with automatic check digits, and Code 128 for text. Saved as PNG from your browser.',
   name='Barcode generator', cat='UtilitiesApplication',
   aria={'바코드': 'Barcode'},
   attrs=[('value="880123456789"', 'value="501234567890"')],
   body='''  <h2>Which barcode do you need</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">EAN-13</strong> — the retail product barcode scanned at supermarket tills and used by online marketplaces (in North America it
      appears as the 12-digit UPC, which scanners read as an EAN-13 with a leading zero). The number itself is issued to your company by GS1 in your country; the
      first digits identify the issuing country and the company. Any 13 digits you invent will scan, but they will point at someone else's product, so use this page
      to turn a number you have been assigned into a picture.<br>
      <strong style="color:var(--text)">EAN-8</strong> — the 8-digit version for small packages such as gum and chocolate bars.<br>
      <strong style="color:var(--text)">Code 128</strong> — holds letters and symbols as well as digits, which makes it the usual choice for shipping labels, asset tags,
      membership and library cards and warehouse locations. For numbers used only inside your own organisation, no registration is needed — choose whatever you like.
      It cannot hold accented or non-Latin characters; for those, use a QR code.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is anything I type sent anywhere?</summary>
      <p>No. The barcode is drawn inside your browser and nothing is transmitted. The page keeps working with the internet switched off.</p>
    </details>
    <details>
      <summary>What is the check digit?</summary>
      <p>The last digit of an EAN barcode is calculated from the digits before it. If a scanner misreads a bar, the check fails and the read is rejected. Enter 12 digits and the check digit is added for you; enter 13 and the last digit is verified, with a message if it is wrong.</p>
    </details>
    <details>
      <summary>It will not scan</summary>
      <p>Check three things. First, that the white margin on each side of the bars has not been cropped away — without it a scanner cannot find the code. Second, that it is not printed too small: use the "for print" bar width and print at least 3 cm wide. Third, faint inkjet output and glossy, reflective paper are hard to read.</p>
    </details>
    <details>
      <summary>How do I get a product barcode number?</summary>
      <p>Join GS1 in your country (GS1 US, GS1 UK and so on). You receive a company prefix and append your own product numbers to make 13 digits. This page does not issue numbers; it turns a number you already have into a barcode image.</p>
    </details>
    <details>
      <summary>Can Code 128 hold accents or other scripts?</summary>
      <p>No. Code 128 covers letters, digits and basic symbols (ASCII) only. For other scripts or longer content use a <a href="qr-generate.html">QR code</a>.</p>
    </details>
    <details>
      <summary>How big should it be printed?</summary>
      <p>The nominal size of an EAN-13 is 37.3 mm wide by 25.9 mm tall, and it may be scaled between 80% and 200%. A PNG saved at 6 pixels per module and printed about 4 cm wide is read by nearly every scanner.</p>
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
    # 영어판이 없는 툴로 가는 링크는 한국어판으로 보낸다 (audit 가 깨진 링크로 잡는다)
    def fix_link(m):
        name = m.group(1)
        if os.path.exists(ROOT + '/en/' + name) or not os.path.exists(ROOT + '/' + name): return m.group(0)
        return 'href="../' + name + '"'
    h = re.sub(r'href="([a-z0-9-]+\.html)"', fix_link, h)

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
    h = h.replace("'붙여넣은-그림-'", "'pasted-image-'")
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
