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
 'pdf-edit': dict(
   title='Rotate, delete and reorder PDF pages — free, nothing uploaded',
   desc='Rotate PDF pages, remove the ones you do not need and drag them into a new order, with thumbnails, inside your browser. The file never leaves your device.',
   og_t='Rotate, delete and reorder PDF pages without uploading',
   og_d='Fix sideways scans, drop blank pages and change the page order, all in your browser.',
   name='PDF page editor', cat='UtilitiesApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>Why a scanned PDF keeps coming out sideways</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Every PDF page carries its own <strong style="color:var(--text)">rotation value</strong>. Scanners and copiers often leave that value
      untouched, so a document that looks fine on your screen opens sideways on someone else's computer or comes out of the printer lying down.
      Rotating in a viewer only turns the picture for that moment; nothing is written to the file. The rotation you apply here changes the
      value stored in the file itself, so the page stands upright wherever it is opened.
    </p>
  </div>

  <h2>Why not upload it</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      The PDFs people fix are contracts, invoices, medical forms and ID scans — exactly the files that should not sit on a stranger's server.
      Most "edit PDF online" sites upload the whole document before showing you the first thumbnail. This page renders the previews, rotates,
      deletes and reorders with your own browser. It keeps working with the internet switched off, there is no file size cap beyond your
      device's memory, and nothing is kept once you close the tab.
    </p>
    <p style="margin:14px 0 0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Typical jobs</strong> — a few pages fed upside down by the document feeder; blank backs left over from
      duplex scanning; pages that arrived shuffled; a sensitive page removed before sharing. If you want to <strong style="color:var(--text)">extract</strong>
      pages into separate files use <a href="pdf-split.html">split PDF</a>; to <strong style="color:var(--text)">join</strong> several files use <a href="pdf-merge.html">merge PDF</a>.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is the rotation really saved into the file?</summary>
      <p>Yes. Instead of just turning the view, the page's rotation entry inside the PDF is rewritten, so it opens upright in any reader and prints upright too.</p>
    </details>
    <details>
      <summary>Is my PDF uploaded?</summary>
      <p>No. From the thumbnails to the saved file, everything happens inside your browser. You can disconnect from the internet after the page has loaded and it still works.</p>
    </details>
    <details>
      <summary>How do I change the page order?</summary>
      <p>Drag a thumbnail to a new place, or use the ← → buttons on each card. The numbers on the cards show the new order; the saved file follows it.</p>
    </details>
    <details>
      <summary>Does it keep the quality of the pages?</summary>
      <p>Yes. Pages are copied as they are — text stays text, images keep their original resolution. Nothing is re-rendered or compressed.</p>
    </details>
    <details>
      <summary>Is it slow with long documents?</summary>
      <p>Making the thumbnails takes a moment. Documents over 100 pages appear from the front as the previews are drawn; rotating and saving are quick.</p>
    </details>
    <details>
      <summary>Is my original changed?</summary>
      <p>No. A new file is always saved; the original on your disk stays exactly as it was.</p>
    </details>
  </div>
'''),
 'text-diff': dict(
   title='Compare two texts and highlight the differences — free, private',
   desc='Paste the original and the revised text to see changed, added and removed lines and the exact characters that changed. Compared in your browser, never sent anywhere.',
   og_t='Compare two texts without uploading them',
   og_d='Changed lines and characters highlighted side by side or inline. Runs in your browser.',
   name='Text compare', cat='UtilitiesApplication',
   aria={},
   attrs=[],
   body='''  <h2>Why the texts you compare should not be uploaded</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Two versions of a text usually get compared because the text matters: a contract that came back from the other side, a report draft,
      a proposal, a cover letter, a configuration file. You want to know what changed since last time, or what went missing in your edit.
      Most online diff tools post both texts to a server to do that. This page compares them inside your browser only. It keeps working with
      the internet disconnected, nothing is stored on your device, and a refresh clears both boxes.
    </p>
  </div>

  <h2>How to read the result</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Red line</strong> — present only in the original (removed).<br>
      <strong style="color:var(--text)">Green line</strong> — present only in the revision (added).<br>
      <strong style="color:var(--text)">Colour on both sides</strong> — the same line was edited; the darker highlight marks the characters that actually changed.<br>
      <strong style="color:var(--text)">"… n lines unchanged …"</strong> — unchanged text folded away. Switch off "Show only changed areas" to expand everything.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is the text sent to a server?</summary>
      <p>No. The comparison runs entirely in your browser and the text is never transmitted. Proof: load the page, go offline, and it still works. Nothing is saved either, so reloading clears it.</p>
    </details>
    <details>
      <summary>Can I compare Word, Google Docs or PDF files directly?</summary>
      <p>Not as files — those formats mix text with formatting. Open the document, select all, copy and paste it here. Plain-text files such as .txt, .csv, .md, .json, .srt subtitles or source code can be opened with "Load a file" or dropped onto a box.</p>
    </details>
    <details>
      <summary>Everything shows as changed when only the line breaks differ</summary>
      <p>Lines are matched one to one. If one version wraps a paragraph onto several lines and the other keeps it on one, they look like different lines. Paste both in the same shape. Differences between Windows and Mac line endings (CRLF/LF) and a trailing newline are ignored automatically.</p>
    </details>
    <details>
      <summary>Can I ignore whitespace-only edits?</summary>
      <p>Turn on "Ignore whitespace". Leading and trailing spaces are dropped and runs of spaces count as one. A space that appears or disappears inside a word still counts as a change, because it may change the meaning.</p>
    </details>
    <details>
      <summary>How long can the texts be?</summary>
      <p>Tens of thousands of lines. Identical text at the start and end is stripped first and only the differing middle is computed. If the two texts are almost entirely different — thousands of differing lines — the comparison stops and tells you, since at that point they are simply different documents.</p>
    </details>
    <details>
      <summary>How do I put the result in an email or report?</summary>
      <p>"Copy result" copies the changed lines with two lines of context, marked <code>-</code> for removed and <code>+</code> for added, as plain text you can paste anywhere.</p>
    </details>
  </div>
'''),
 'password-gen': dict(
   title='Random password generator — made in your browser, never sent',
   desc='Strong random passwords with your choice of length and character sets, without look-alike letters, several at a time. Made on your device, never transmitted.',
   og_t='Random password generator that never sends your password',
   og_d='Pick length and character sets, drop look-alike letters, make 1 to 20 at once. Generated locally.',
   name='Password generator', cat='SecurityApplication',
   aria={},
   attrs=[('>16자<', '>16 characters<'), ('<option value="1">1개<', '<option value="1">1<'), ('<option value="5" selected>5개<', '<option value="5" selected>5<'),
          ('<option value="10">10개<', '<option value="10">10<'), ('<option value="20">20개<', '<option value="20">20<'), ("tt('pw.countUnit', '개')", "''")],
   body='''  <h2>What makes a password strong</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Length</strong> matters far more than forcing in symbols. Anything under 12 characters falls quickly to
      modern hardware; at 16 or more it is out of reach in practice. And however good a password is, <strong style="color:var(--text)">reusing it</strong>
      means one leaked site exposes all the others. Use a different one everywhere, do not try to memorise them, and keep them in a password manager.
    </p>
  </div>

  <h2>Four more characters beat all the symbols</h2>
  <div class="card">
    <p style="margin:0 0 14px;color:var(--muted);font-size:14px">
      The arithmetic is clear. Take a <strong style="color:var(--text)">12-character</strong> password from letters and digits (62 symbols) and add the full set
      of punctuation (94 symbols): the number of possibilities grows about <strong style="color:var(--text)">150 times</strong>. Keep the same 62 symbols but
      go to <strong style="color:var(--text)">16 characters</strong>: it grows about <strong style="color:var(--text)">15 million times</strong>.
      Four extra characters do roughly a hundred thousand times more work than every symbol on the keyboard.
    </p>
    <p style="margin:0;color:var(--muted);font-size:14px">
      That is not an argument against symbols. It is a warning about the most common mistake: making a password short and "fixing" it with punctuation
      when the site would have allowed a longer one. Make it long, let a manager remember it.
    </p>
  </div>

  <h2>Why it is safe to generate it here</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      With a password generator the only question is <strong style="color:var(--text)">where the value goes</strong>. This page does not ask a server
      to make one. It uses the cryptographic random number generator built into your browser (<code>crypto.getRandomValues</code>), the value is
      created on your device and never leaves the screen, and nothing is logged — close the tab and it is gone. When random bytes are turned into
      characters, <strong style="color:var(--text)">modulo bias</strong> is removed so no character comes up more often than the others.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is it safe to use a password generated here?</summary>
      <p>Yes. It comes from the browser's cryptographic random number generator (<code>crypto.getRandomValues</code>). The value exists only on your screen; it is not transmitted and not stored.</p>
    </details>
    <details>
      <summary>Why exclude look-alike characters?</summary>
      <p>Lower-case l, the digit 1 and capital I, and capital O and the digit 0, are hard to tell apart on screen and on paper. If you will ever type the password by hand, leaving them out avoids mistakes.</p>
    </details>
    <details>
      <summary>How long should it be?</summary>
      <p>16 characters or more for anything important. If a site limits the length, use the longest it allows.</p>
    </details>
    <details>
      <summary>Could the same password come up twice?</summary>
      <p>Not in practice. With 16 characters from all four sets the number of possibilities is astronomical, and the chance of a repeat is negligible.</p>
    </details>
  </div>
'''),
 'text-clean': dict(
   title='Remove duplicate lines, sort and clean up text — free, private',
   desc='Delete duplicate and blank lines, trim spaces, sort A–Z or by length, change case, number or join lines. Lists stay in your browser and are never uploaded.',
   og_t='Remove duplicate lines and clean up a list without uploading',
   og_d='Dedupe, sort, trim, change case, number or join lines. Runs in your browser.',
   name='Text cleaner', cat='UtilitiesApplication',
   aria={},
   attrs=[],
   body='''  <h2>When to use it</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      A mailing list assembled from several places with <strong style="color:var(--text)">the same address several times</strong>; a comma-separated list
      that should be <strong style="color:var(--text)">one item per line</strong>; values copied out of a spreadsheet with
      <strong style="color:var(--text)">stray spaces</strong> around them. Because everything happens in your browser, it is fine to use on customer lists
      and other data you would not paste into a random website.
    </p>
  </div>

  <h2>Invisible spaces ruin lists</h2>
  <div class="card">
    <p style="margin:0 0 14px;color:var(--muted);font-size:14px">
      Text copied from web pages and PDFs often carries characters that <strong style="color:var(--text)">look like a space but are not one</strong>.
      They look identical on screen, yet a spreadsheet search cannot find them, duplicates survive deduplication, and sorting comes out in a strange order.
      <strong style="color:var(--text)">Trim spaces</strong> removes those special spaces as well as ordinary ones.
    </p>
    <p style="margin:0;color:var(--muted);font-size:14px">
      That is why a pasted list is best cleaned in this order: <strong style="color:var(--text)">trim → remove blank lines → remove duplicates → sort</strong>.
      Only after trimming do two equal values compare as equal. The defaults are set up in that order.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is deduplication case-sensitive?</summary>
      <p>Yes. <code>Apple</code> and <code>apple</code> are different lines. To treat them as the same, choose "All lower case" first and then remove duplicates.</p>
    </details>
    <details>
      <summary>Is the original order kept?</summary>
      <p>With sorting set to "Leave as is", the first occurrence of each line stays where it was and only the later repeats are removed.</p>
    </details>
    <details>
      <summary>Is my text stored anywhere?</summary>
      <p>No. It is processed in your browser only and disappears when you close the tab. Nothing is sent to a server.</p>
    </details>
    <details>
      <summary>How large a list can it handle?</summary>
      <p>Tens of thousands of lines without trouble. Much larger lists may make the browser pause for a moment.</p>
    </details>
  </div>
'''),
 'time-calc': dict(
   title='Time calculator — add hours, time between, total work hours',
   desc='Add or subtract hours and minutes from a time, find the hours between two times, total work hours across many days, and convert 7:45 to 7.75. All in your browser.',
   og_t='Time calculator · add hours, time between, work hour totals',
   og_d='Add and subtract times, duration between two times, sum many days, h:mm ↔ decimal hours.',
   name='Time calculator', cat='UtilitiesApplication',
   aria={},
   attrs=[],
   body='''  <h2>Why adding work hours by hand goes wrong</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Time is base 60: 8:30 plus 7:45 is 16:15, not 15:75. One or two days are easy, but somewhere in a month of entries a carry gets dropped.
      In a spreadsheet the cell format has to be <strong style="color:var(--text)">[h]:mm</strong> before a total over 24 hours displays correctly,
      and if you do not know that the total simply looks too small. This page converts every line to minutes first — whether it is written as
      "8:30", "8h 30m", "90m" or "09:00-18:00" — so that mistake cannot happen, and shows the total both as h:mm and as decimal hours so it can go
      straight into whichever timesheet system you use.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is what I type sent anywhere?</summary>
      <p>No. The arithmetic runs in your browser and nothing is transmitted. It works with the internet switched off.</p>
    </details>
    <details>
      <summary>How are overnight shifts handled?</summary>
      <p>If the end time is earlier than the start, it is taken to be the next day: 22:00 to 06:00 is 8 hours. A line such as "22:00-06:00" in the totals box is read the same way.</p>
    </details>
    <details>
      <summary>How do I take off breaks?</summary>
      <p>"Time between two times" has its own break field. In the totals box, "Break to subtract per line" is taken off every line written as a start–end range, but not off lines that already give a net duration like "8:30". You can also write "-60m" at the end of a single line to subtract from that line only.</p>
    </details>
    <details>
      <summary>What are decimal hours?</summary>
      <p>Minutes divided by 60 and added to the hours. 7 h 45 min is 7.75, 7 h 30 min is 7.5, 7 h 20 min is 7.33. Many payroll and timesheet systems use this form, hence the converter.</p>
    </details>
    <details>
      <summary>Which formats does the totals box accept?</summary>
      <p>One entry per line: "8:30", "8h 30m", "8 hours 15 minutes", "90m", "2.5" (decimal hours) or a range like "09:00-18:00". A day name or date in front of the entry is ignored, so you can paste a week straight from your notes.</p>
    </details>
  </div>
'''),
 'pdf-page-number': dict(
   title='Add page numbers to a PDF — free, nothing uploaded',
   desc='Number the pages of a PDF in your browser. Position, format (1, 1 / 12, - 1 -, Page 1 of 12), start number, font size and a range so the cover is skipped.',
   og_t='Add page numbers to a PDF without uploading it',
   og_d='Position, format, start number and page range. Written into the file, in your browser.',
   name='PDF page numbers', cat='UtilitiesApplication',
   aria={'파일 선택': 'Choose a file', '페이지 번호 위치 미리보기': 'Preview of the page number position'},
   attrs=[],
   body='''  <h2>When you need it</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">After merging documents</strong> — files that each had their own numbering end up with numbers that jump around. Numbering the merged file gives one sequence from start to end.<br>
      <strong style="color:var(--text)">Scanned paper</strong> — pages that never had numbers, before filing or submitting them.<br>
      <strong style="color:var(--text)">Skipping the cover</strong> — set the range to "2-" and the start number to 1 and the page after the cover becomes page 1.<br>
      <strong style="color:var(--text)">Double-sided printing</strong> — "Bottom outside" puts odd pages on the right and even pages on the left, so the numbers sit at the outer edge when the pages are bound like a book.
    </p>
  </div>

  <h2>Why not upload the file</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Documents that need page numbers are usually the ones that matter — contracts, theses, reports, legal exhibits. Most online tools send the whole file
      to a server before adding a single digit. This page reads, numbers and saves the PDF with your own browser. It works offline once loaded, there is
      no size cap beyond your device's memory, and nothing is kept when you close the tab. The existing content is never removed: the number is drawn on top,
      so if the document already has numbers you may see two. Move yours to the opposite edge or adjust the margin — the preview shows exactly where it will go.
      Landscape and rotated pages get the number in the same place relative to how the page is viewed.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my PDF uploaded?</summary>
      <p>No. Reading, numbering and saving all happen inside your browser; the page keeps working with the internet switched off. It was built for files you would not hand to a stranger.</p>
    </details>
    <details>
      <summary>How do I leave the cover unnumbered and start the body at 1?</summary>
      <p>Enter <code>2-</code> in "Pages to number" and keep the start number at 1. Pages 2 to the end get 1, 2, 3… With a two-page cover use <code>3-</code>.</p>
    </details>
    <details>
      <summary>What is the 12 in "1 / 12"?</summary>
      <p>The number of the last page that gets numbered. In a 12-page file with the cover skipped and numbering starting at 1 on page 2, the numbers run "1 / 11" to "11 / 11".</p>
    </details>
    <details>
      <summary>Can I use another language or a custom label?</summary>
      <p>The formats use digits and the words "Page", "of" and "p." because those can be written with the font every PDF reader has built in. Other text would require embedding a font file, which makes the PDF much larger, so it is deliberately not offered.</p>
    </details>
    <details>
      <summary>Does the text stay selectable? Is quality affected?</summary>
      <p>Yes and no, respectively. Pages are not turned into images; only a small text object is added to each page. The original text remains searchable and copyable, images keep their resolution, and the file grows by a few kilobytes.</p>
    </details>
    <details>
      <summary>What about password-protected PDFs?</summary>
      <p>Files with an open password cannot be read and a message tells you so. Remove the password in your PDF reader, save, and try again.</p>
    </details>
  </div>
'''),
 'pdf-to-text': dict(
   title='Extract text from a PDF — copy or save as .txt, free, no upload',
   desc='Pull the text out of a PDF in page order and copy it or save it as .txt, in your browser. Page range, paragraph mode, and a warning when the PDF is only a scan.',
   og_t='Extract text from a PDF without uploading it',
   og_d='All the text in page order, copy or save as .txt. Paragraph mode and scanned-PDF detection.',
   name='PDF to text', cat='UtilitiesApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>Why copying from a viewer scrambles the text</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      A PDF stores text as "draw these characters at these coordinates". There is no notion of a line or a paragraph in the file, which is why
      drag-selecting in a viewer interleaves two columns or drags the page header into the middle of a sentence. This page reads the coordinates,
      gathers characters at the same height into one line, stacks the lines top to bottom and joins the pages in order. "Merge into paragraphs"
      then removes the forced break at the end of each line and keeps a blank line only where the gap between lines is wide — between paragraphs.
    </p>
  </div>

  <h2>If nothing comes out, it is a scan</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      A PDF made by scanning paper or photographing a page looks like text but is a <strong style="color:var(--text)">picture</strong>. The file holds no
      characters, so no tool can extract them as they are; that takes OCR (optical character recognition), which guesses letters from their shapes and
      makes mistakes. This page counts such pages as "pages without text" and tells you when the whole file is like that. If you can get the original
      document (Word, Google Docs), it will always be more accurate than OCR.
    </p>
    <p style="margin:14px 0 0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Why it runs in the browser</strong> — the PDFs people need text from are contracts, medical reports, bank statements
      and papers under review. Sending them to a conversion server is a risk you do not need to take: the extraction here happens on your device, works offline,
      and leaves nothing behind when the tab closes.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my file uploaded?</summary>
      <p>No. The text is read out by your own browser; the page works with the internet switched off. Nothing is stored.</p>
    </details>
    <details>
      <summary>Tables come out broken</summary>
      <p>Table cells have positions but no cell boundaries in the text data, so the cells of one row are joined with spaces. Keep "Keep lines as shown" so at least the rows are right. To move a table into a spreadsheet, paste a row and use "Text to columns".</p>
    </details>
    <details>
      <summary>The characters are in the wrong order</summary>
      <p>Two-column layouts and vertical text put characters from different columns at the same height, so they can be merged into one line. Some PDFs also deliberately scramble their fonts to prevent copying; those cannot be extracted correctly by any tool.</p>
    </details>
    <details>
      <summary>Letters show as boxes or question marks</summary>
      <p>The PDF lacks the font mapping needed to turn glyphs back into characters. A PDF exported again with "embed fonts" from the program that made it will work. If someone sent you the file, only they can fix that.</p>
    </details>
    <details>
      <summary>How many pages can it handle?</summary>
      <p>Hundreds. Pages are read one at a time with a progress message. To extract only part of a document, enter a page range such as <code>1-3, 7</code>.</p>
    </details>
    <details>
      <summary>Which encoding is the .txt?</summary>
      <p>UTF-8, which every modern editor and operating system reads correctly. If an old program shows garbled characters, open the file in Notepad and re-save it with a different encoding.</p>
    </details>
  </div>
'''),
 'favicon': dict(
   title='Favicon generator — PNG to ICO and every size, free, no upload',
   desc='One logo becomes favicon.ico (16·32·48), PNG icons for iPhone and Android (180·192·512), a site.webmanifest and the HTML to paste. Nothing is uploaded.',
   og_t='Favicon generator — one logo, every size, in your browser',
   og_d='favicon.ico, PNG icons from 16 to 512, site.webmanifest and the HTML snippet, all in one ZIP.',
   name='Favicon generator', cat='DesignApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>Why so many sizes</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">favicon.ico</strong> — browser tabs, bookmarks, the address bar. One file holding 16, 32 and 48 px versions so the browser picks the right one for the screen scale. The oldest format, understood everywhere.<br>
      <strong style="color:var(--text)">favicon-16x16 · 32x32.png</strong> — for modern browsers that ask for PNG rather than ICO.<br>
      <strong style="color:var(--text)">apple-touch-icon.png (180)</strong> — the icon iPhone and iPad show for "Add to Home Screen". iOS rounds the corners itself.<br>
      <strong style="color:var(--text)">android-chrome-192 · 512.png + site.webmanifest</strong> — Android home screens and installable web apps (PWA); 512 is used on the install screen and splash.<br>
      Detail disappears as icons shrink, so a logo with words in it is unreadable at 16 px. For the tab icon, a symbol or a single initial works best.
    </p>
  </div>

  <h2>How to install them</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Unzip the files into the <strong style="color:var(--text)">root folder</strong> of your site (where index.html lives) and paste the code into the <code>&lt;head&gt;</code> of every page.
      If the files live in a subfolder, change the leading <code>/</code> in the code to that folder. Browsers cache favicons aggressively: if the new one does not show,
      open <code>/favicon.ico</code> directly in a new tab or clear the cache. WordPress users can simply upload the 512 PNG under Appearance → Customize → Site Icon.
    </p>
    <p style="margin:14px 0 0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Why it runs in the browser</strong> — a logo you are preparing a favicon for is often not public yet. The resizing, the ICO and the ZIP are
      all produced on your device; the picture is never uploaded, and the page works offline.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my logo uploaded?</summary>
      <p>No. Resizing, packing the ICO and PNGs and building the ZIP all happen inside your browser. It works with the internet switched off, and nothing of an unreleased logo is left anywhere.</p>
    </details>
    <details>
      <summary>What picture should I start from?</summary>
      <p>Something close to square and at least 512 px keeps every size sharp; an SVG stays sharp at any size. A PNG with a transparent background is ideal. If the background is white, either keep it or remove it first with <a href="image-transparent.html">make a white background transparent</a>.</p>
    </details>
    <details>
      <summary>Can I get away with just the ICO?</summary>
      <p>For the tab icon alone, "Save favicon.ico only" is enough. iPhone home screens, Android and installable web apps ignore ICO and need PNG, so for phones use the full ZIP.</p>
    </details>
    <details>
      <summary>Why add padding?</summary>
      <p>Android masks icons into circles and other shapes, and artwork that reaches the edge gets clipped. 10–15% padding is safe for any mask. Tab icons, on the other hand, look bigger when they fill the square.</p>
    </details>
    <details>
      <summary>The transparent background looks black somewhere</summary>
      <p>The ICO stores 32-bit pixels with alpha, so transparency is preserved. A few old Windows programs render ICO transparency as black; browsers do not. If it worries you, set the background to white.</p>
    </details>
    <details>
      <summary>What is the site name in site.webmanifest for?</summary>
      <p>It is the label shown under the icon when the site is added to an Android home screen. Leave it empty and the browser uses the page title. You can edit the file later in any text editor.</p>
    </details>
  </div>
'''),
 'image-palette': dict(
   title='Extract colors from an image — HEX codes and palette, free',
   desc='Dominant colors of a photo or logo as HEX and RGB with their share. Click to pick any pixel\'s exact color. Save as PNG or CSS variables. Nothing is uploaded.',
   og_t='Extract colors from a photo without uploading it',
   og_d='Dominant colors as HEX and RGB with their share. Click to pick a pixel. Save as PNG or CSS variables.',
   name='Image color palette', cat='DesignApplication',
   aria={'파일 선택': 'Choose a file', '사진 — 클릭하면 그 자리 색을 집습니다': 'Photo — click to pick the color at that spot'},
   attrs=[],
   body='''  <h2>What it is for</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Recovering brand colors</strong> — you have the logo file but not the color codes. Pick them here and hand a designer the exact HEX.<br>
      <strong style="color:var(--text)">Backgrounds and text that fit a photo</strong> — a thumbnail or social card built on a color taken from the photo itself never clashes with it.<br>
      <strong style="color:var(--text)">Interior and fashion references</strong> — keep the color combination of a picture you like as codes and reproduce the mood later.<br>
      <strong style="color:var(--text)">Web and app themes</strong> — "Copy as CSS variables" gives you <code>--color-1: #…;</code> lines ready to paste into a stylesheet.
    </p>
  </div>

  <h2>How the colors are chosen</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      All the pixels are treated as one box in color space, and the box is split in half along its widest axis until there are as many boxes as colors
      you asked for (median cut). The average of each box is a palette color and the number of pixels in it is the share. Small accent colors therefore only
      appear when you raise the count, and a gradient photo can produce several similar colors. When you need the exact value at one spot, click the picture:
      that reads the original pixel directly.
    </p>
    <p style="margin:14px 0 0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Why it runs in the browser</strong> — the photo is reduced and counted on your device. Nothing is uploaded, which is what you want for
      unreleased product shots or a logo that is not public yet, and the page works offline.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my photo uploaded?</summary>
      <p>No. The colors are counted inside your browser and the picture goes nowhere. It works with the internet switched off.</p>
    </details>
    <details>
      <summary>The logo color is slightly off</summary>
      <p>A palette color is an average of similar pixels, so JPEG noise and anti-aliased edges can shift it a few steps. For the exact value, click a flat area of the logo — that shows the pixel as it is. A PNG or SVG original is more accurate than a JPEG.</p>
    </details>
    <details>
      <summary>White background comes first</summary>
      <p>If the background is most of the picture, it naturally has the largest share. Turn on "Ignore white/black background" to leave out nearly white and nearly black pixels so only the object's colors remain.</p>
    </details>
    <details>
      <summary>What does the percentage mean?</summary>
      <p>The share of all pixels assigned to that color. With the background ignored, it is the share of the remaining pixels.</p>
    </details>
    <details>
      <summary>Does it work with large photos?</summary>
      <p>Yes. Counting is done on a reduced copy, so even photos of tens of millions of pixels finish instantly. The color picked by clicking still comes from the full-resolution image.</p>
    </details>
  </div>
'''),
 'json-format': dict(
   title='JSON formatter, validator and minifier — free, nothing sent',
   desc='Pretty-print or minify JSON in your browser, see the line and column of a syntax error, sort keys, repair trailing commas and unquoted keys. Nothing is sent.',
   og_t='JSON formatter and validator that never sees your data',
   og_d='Pretty-print, minify, pinpoint syntax errors, sort keys, repair common slips. Runs in your browser.',
   name='JSON formatter', cat='DeveloperApplication',
   aria={},
   attrs=[],
   body='''  <h2>Why API responses and config files should not go to a random site</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      The moment you need to format JSON is usually the moment you are looking at an <strong style="color:var(--text)">API response, a config file, a log,
      or a request body with a token in it</strong> — data that often contains user records or secret keys. Most "JSON formatter" sites post your input to a server,
      and some wrap it in analytics scripts. This page uses only the browser's own <code>JSON.parse</code> and <code>JSON.stringify</code>. It keeps working offline,
      and a refresh clears the input.
    </p>
  </div>

  <h2>What "repair common slips" does</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Strict JSON needs double quotes around keys, allows no comma after the last item and no comments. Text copied from JavaScript or a config file often breaks
      those rules. With the option on, the page <strong style="color:var(--text)">removes trailing commas, quotes bare keys, turns single quotes into double quotes and strips
      <code>//</code> and <code>/* */</code> comments</strong> before parsing again. Nothing inside string values is touched. When a repair was needed the result says
      "Valid after repair", so switch the option off when you need to know whether the original is strictly valid.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my JSON sent to a server?</summary>
      <p>No. Formatting and validation run inside your browser and nothing is transmitted. It works with the internet switched off, and nothing is stored — a reload clears it.</p>
    </details>
    <details>
      <summary>How do I read the error position?</summary>
      <p>"Line 3, column 14" means everything up to that point parsed correctly. The problem is usually right there or in the item just before it — a missing comma, quote or bracket. The output box shows that line with a caret under the position.</p>
    </details>
    <details>
      <summary>Large numbers come out changed</summary>
      <p>JavaScript keeps integers exact only up to 2^53 (about 9 quadrillion). Longer IDs may lose their last digits. Store such values as strings in the source; this page warns when it sees a number that could be affected.</p>
    </details>
    <details>
      <summary>Does the key order change?</summary>
      <p>With "Keep order" the original order is preserved. "Alphabetical" sorts the keys of every object at every level. Arrays are never reordered.</p>
    </details>
    <details>
      <summary>Non-ASCII characters show as \\uXXXX — or I want them to</summary>
      <p>By default characters are kept as they are. Turn on "Escape non-ASCII" when a legacy system needs pure ASCII. The other way round, \\uXXXX escapes in the input are turned back into characters automatically.</p>
    </details>
    <details>
      <summary>How large a file can it handle?</summary>
      <p>Tens of megabytes without trouble; beyond that the browser may pause for a moment. Use "Open file" or drop a file onto the input box.</p>
    </details>
  </div>
'''),
 'file-hash': dict(
   title='File hash and checksum — SHA-256, SHA-1, MD5, free, no upload',
   desc='SHA-256, SHA-512, SHA-1 and MD5 of files or text, computed in your browser and compared with a published checksum. Several files at once; large files read in chunks.',
   og_t='File hash and checksum checker that never uploads the file',
   og_d='SHA-256, SHA-512, SHA-1 and MD5 of files or text, matched against a published checksum.',
   name='File hash', cat='SecurityApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>Why verify a checksum</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Publishers of installers and operating-system images list a <strong style="color:var(--text)">SHA-256 value</strong> next to the download. If the file you
      received produces the same value, not a single byte changed in transit and nobody swapped the file on the way. A one-character change produces a completely
      different hash, so comparing a few characters by eye is already strong evidence — this page compares the whole value for you. The same idea tells you whether a
      backup still matches the original or whether a document you were emailed was altered.
    </p>
  </div>

  <h2>Which algorithm</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">SHA-256</strong> — the current standard; most published checksums use it.<br>
      <strong style="color:var(--text)">SHA-512</strong> — a longer digest, used by some Linux distributions.<br>
      <strong style="color:var(--text)">SHA-1 · MD5</strong> — older; collisions can be manufactured, so they are no longer used for security. They remain common for
      legacy checksums and for detecting transfer errors, which is why they are still offered.<br>
      SHA digests come from the browser's built-in <code>crypto.subtle</code>; MD5 is not available there, so it is implemented in the page (RFC 1321). Files are read in
      chunks rather than loaded whole, so multi-gigabyte files work.
    </p>
    <p style="margin:14px 0 0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Why it runs in the browser</strong> — the files people verify are installers, disk images and internal documents. Uploading
      gigabytes to a hashing service would be slow and pointless; here the bytes never leave your machine and the page works offline.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my file uploaded?</summary>
      <p>No. Hashing happens entirely in your browser and the file goes nowhere. It works with the internet switched off, which is why even large installers and internal data are fine to check here.</p>
    </details>
    <details>
      <summary>The value differs from the publisher's</summary>
      <p>First make sure the algorithm matches — a SHA-256 and an MD5 of the same file are naturally different. If it still differs, the download was probably interrupted or you have a different version. Download again; if it still does not match, do not run the file.</p>
    </details>
    <details>
      <summary>The published checksum has a prefix like "sha256: "</summary>
      <p>Paste it as it is. Characters that are not hexadecimal, and spaces, are ignored in the comparison. A whole line in the "hash  filename" format works too — only the hash part is compared.</p>
    </details>
    <details>
      <summary>How long does a large file take?</summary>
      <p>A few seconds per gigabyte on an ordinary computer, with a progress indicator. Each extra algorithm you tick adds time.</p>
    </details>
    <details>
      <summary>What is the text hash for?</summary>
      <p>When a program or configuration needs the hash of a specific string, or to compare two long texts by a short value. Text is encoded as UTF-8 before hashing, so the result matches other tools.</p>
    </details>
  </div>
'''),
 'svg-to-png': dict(
   title='Convert SVG to PNG at any size — free, batch, no upload',
   desc='Render SVG to PNG, JPG or WebP at an exact pixel width, height or scale, with a transparent, white or custom background. Many files to one ZIP; paste SVG code too.',
   og_t='SVG to PNG at any size, in your browser',
   og_d='Exact pixel size or scale, transparent or colored background, PNG, JPG or WebP, many files to one ZIP.',
   name='SVG to PNG', cat='MultimediaApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>Why convert SVG to PNG</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      SVG is a vector format that never pixelates, but <strong style="color:var(--text)">older versions of PowerPoint and Word, social networks, many shop admin panels and
      email</strong> either refuse SVG or render it badly. Exporting a PNG once at the size you need makes the graphic usable everywhere. A 2× or 3× scale stays crisp on
      high-density (Retina) screens, and transparency is preserved in PNG and WebP. The conversion uses the browser's own SVG renderer, so the result looks exactly as the
      SVG does on screen.
    </p>
  </div>

  <h2>SVGs without a size · fonts · external images</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">No width/height</strong> — the aspect ratio is taken from the viewBox and fitted to the pixel width you choose. Without a viewBox the file
      is treated as 300×150, so set the pixel size yourself.<br>
      <strong style="color:var(--text)">Fonts</strong> — text inside an SVG is drawn with the fonts installed on this computer. If the designer's machine had different fonts the
      shapes will differ; SVGs with text converted to outlines are safe.<br>
      <strong style="color:var(--text)">External images and stylesheets</strong> — <code>&lt;image href="http://…"&gt;</code> pointing at other files and external CSS are not loaded
      for security reasons. Images embedded as data URIs inside the SVG do work.
    </p>
    <p style="margin:14px 0 0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Why it runs in the browser</strong> — unreleased logos and internal diagrams are exactly what gets converted. Nothing is uploaded, and the
      page works offline once loaded.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my file uploaded?</summary>
      <p>No. The SVG is read, rendered and saved as PNG inside your browser; it works with the internet switched off.</p>
    </details>
    <details>
      <summary>Edges look blurry or jagged</summary>
      <p>At small sizes thin lines fall inside a single pixel and blur. Render at twice the size you will display and let the page or document scale it down — that is what the 2× and 3× scale options are for.</p>
    </details>
    <details>
      <summary>The transparent background came out white or black</summary>
      <p>JPG has no transparency, so transparent areas become white. Choose PNG or WebP to keep transparency. To preview on a dark background, set the background to a custom color.</p>
    </details>
    <details>
      <summary>Text in the SVG uses the wrong font</summary>
      <p>SVG files name fonts but do not contain them, so a missing font is replaced. Convert text to outlines in your drawing program before exporting and it will look the same everywhere.</p>
    </details>
    <details>
      <summary>What is the maximum size?</summary>
      <p>8192 pixels on a side, the limit of what a browser canvas can draw in one piece. For very large print graphics, use the SVG itself.</p>
    </details>
    <details>
      <summary>Will the PNG be larger than the SVG?</summary>
      <p>Usually, yes: an SVG stores shapes, a PNG stores every pixel. On the web keep the SVG wherever possible and convert only where PNG is required. The PNG can be shrunk further with <a href="image-compress.html">compress image</a>.</p>
    </details>
  </div>
'''),
 'base64': dict(
   title='Base64 encode and decode — text, files, images to data URI, free',
   desc='Text to Base64 and back as UTF-8, files and images to Base64 data URIs, Base64 back to a file, all in your browser. URL-safe variant and MIME line breaks.',
   og_t='Base64 encoder and decoder that never sends your data',
   og_d='Text ↔ Base64 (UTF-8), file ↔ data URI, URL-safe and MIME variants. Runs in your browser.',
   name='Base64 encoder/decoder', cat='DeveloperApplication',
   aria={'파일 선택': 'Choose a file'},
   attrs=[],
   body='''  <h2>Base64 is not encryption</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      Base64 is a <strong style="color:var(--text)">notation</strong> that writes bytes with 64 characters (A–Z, a–z, 0–9, + and /). Anyone can reverse it, so it hides nothing.
      It exists for places that can only carry text and still need to hold a file: small images inside HTML and CSS (data URIs), email attachments (MIME), files inside JSON,
      parts of API tokens. The output is about 33% larger than the input, so it is the wrong tool for big files. Text is converted to UTF-8 bytes first, which is why the result
      matches other tools and accented or non-Latin characters survive the round trip.
    </p>
  </div>

  <h2>URL-safe and line breaks</h2>
  <div class="card">
    <p style="margin:0;color:var(--muted);font-size:14px">
      The <code>+</code> and <code>/</code> of standard Base64 have meanings in a URL and get mangled. The <strong style="color:var(--text)">URL-safe</strong> variant replaces them
      with <code>-</code> and <code>_</code> and drops the trailing <code>=</code>; JWT tokens and values in query strings use it. Email (MIME) breaks lines every 76 characters.
      When decoding, any variant is accepted and line breaks and spaces are ignored. If the input is not Base64 at all — a forbidden character or an impossible length — the page
      tells you where the problem is.
    </p>
    <p style="margin:14px 0 0;color:var(--muted);font-size:14px">
      <strong style="color:var(--text)">Why it runs in the browser</strong> — what people paste here is tokens, credentials and internal files. Nothing is transmitted; the page works
      offline and leaves nothing behind.
    </p>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">
    <details>
      <summary>Is my input sent anywhere?</summary>
      <p>No. Conversion happens in your browser only; it works with the internet switched off. Tokens and internal files you paste are not stored anywhere.</p>
    </details>
    <details>
      <summary>Decoded text contains garbled characters</summary>
      <p>The Base64 probably encodes bytes in an encoding other than UTF-8, or it is not text at all. The page decodes as UTF-8 and warns when the bytes are not valid text. Use "Base64 → file" to save the bytes and open them with the right program.</p>
    </details>
    <details>
      <summary>How do I put a data URI in HTML?</summary>
      <p>For an image, <code>&lt;img src="data:image/png;base64,…"&gt;</code>; in CSS, <code>background-image: url("data:…")</code>. Pick that output form and copy it as is. Good for icons of a few kilobytes; large pictures are better kept as files.</p>
    </details>
    <details>
      <summary>How is the file type detected when restoring?</summary>
      <p>From the MIME type in a data URI, or otherwise from the first bytes (PNG, JPEG, GIF, PDF, ZIP, WebP, SVG). If it cannot be determined the file is saved as .bin — give it a name with the right extension.</p>
    </details>
    <details>
      <summary>Does it work with large files?</summary>
      <p>Up to tens of megabytes, though the text boxes get slow. Base64 was never meant for large files; under 5MB is recommended.</p>
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
    # 사전의 '\n' 은 JS 이스케이프다. 속성값에서는 줄바꿈 문자 참조로 바꿔야 자리글이 여러 줄로 보인다.
    def ph(key): return EN.get(key, '?').replace('\\n', '&#10;').replace('"', '&quot;')   # 속성값 안의 큰따옴표
    h = re.sub(r'placeholder="[^"]*"([^>]*?) data-i18n-ph="([^"]+)"', lambda m: 'placeholder="' + ph(m.group(2)) + '"' + m.group(1), h)
    h = re.sub(r' data-i18n-ph="([^"]+)"(\s[^>]*?)placeholder="[^"]*"', lambda m: m.group(2) + 'placeholder="' + ph(m.group(1)) + '"', h)
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
    # 여러 줄짜리 langchange 리스너는 블록째 지운다 (첫 줄만 지우면 남은 본문이 문법 오류가 된다)
    h = re.sub(r"\n[ \t]*document\.addEventListener\('langchange',\s*function \(\) \{\n(?:(?!\n[ \t]*\}\);).)*\n[ \t]*\}\);", '', h, flags=re.S)
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
