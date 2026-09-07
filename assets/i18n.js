/* 툴모아 다국어 엔진
 *
 * 설계 원칙
 * 1. HTML 원문은 한국어로 둔다. 검색엔진이 색인하는 것은 이 한국어 원문이다.
 *    (기계 번역 페이지를 여러 URL로 색인시키면 스팸으로 분류될 위험이 있다)
 * 2. 언어 전환은 브라우저 안에서만 일어난다. URL도 canonical도 바뀌지 않는다.
 * 3. 번역이 없는 키는 한국어 원문으로 자동 복귀한다. 그래서 번역을 부분적으로만
 *    채워도 화면이 깨지지 않는다.
 *
 * 사용법
 *   <span data-i18n="home.h1">필요한 도구만 딱</span>   → 텍스트 교체 (HTML 허용)
 *   <input data-i18n-ph="imgc.ph">                      → placeholder 교체
 *   <div data-ko-only>...</div>                         → 한국어일 때만 표시
 *   t('imgc.working', '변환 중입니다…')                  → 스크립트 안에서 쓰는 문자열
 */
(function () {
  'use strict';

  var LANGS = { ko: '한국어', en: 'English', ja: '日本語' };
  var STORE = 'toolmoa_lang';

  /* ===== 번역 사전 ===== */
  var DICT = {
    en: {
      /* 공통 */
      'brand': 'Tool<span>moa</span>',
      'nav.home': 'Home',
      'nav.imgc': 'Compress image',
      'nav.crop': 'Crop image',
      'nav.i2p': 'Image → PDF',
      'nav.char': 'Character count',
      'nav.merge': 'Merge PDF',
      'nav.split': 'Split PDF',
      'nav.conv': 'Convert file',
      'nav.qr': 'QR code',
      'nav.unit': 'Unit converter',
      'nav.date': 'Date calculator',
      'nav.age': 'Age calculator',
      'foot.note': '© Toolmoa · Everything runs inside your browser',
      'badge.file': '🔒 Your files are never uploaded',
      'badge.text': '🔒 What you type is never sent anywhere',
      'btn.reset': 'Reset',
      'btn.clear': 'Clear all',
      'msg.pickImage': 'Please choose an image file.',
      'msg.pickPdf': 'Please choose a PDF file.',
      'msg.reading': 'Reading the file…',

      /* 홈 */
      'home.title': 'Toolmoa — Free online tools, nothing to install',
      'home.h1': 'Just the tool you need, free',
      'home.lead': 'No installation, no sign-up. Everything runs inside your browser and your files are never sent anywhere.',
      'home.why': 'Why Toolmoa',
      'home.why1.h': 'Your files never reach a server',
      'home.why1.p': 'Most online converters upload your file first and process it on their server. Every Toolmoa tool runs purely in JavaScript inside your browser — that is why it still works with the internet disconnected.',
      'home.why2.h': 'No sign-up, no watermark',
      'home.why2.p': 'We never ask for your email, never stamp a logo on your result, and never limit how many times you use it.',
      'home.why3.h': 'Works the same on mobile',
      'home.why3.p': 'Everything works identically in a phone browser. There is no app to install.',
      'card.imgc.t': 'Compress image',
      'card.imgc.d': 'Shrink file size by adjusting quality and dimensions. JPG, PNG and WebP.',
      'card.char.t': 'Character & word count',
      'card.char.d': 'Characters with and without spaces, words, bytes and manuscript pages.',
      'card.merge.t': 'Merge PDF',
      'card.merge.d': 'Drag several PDFs into the order you want and join them into one.',
      'card.conv.t': 'CSV · JSON · Excel',
      'card.conv.d': 'Convert spreadsheet files between formats.',
      'card.qr.t': 'QR code generator',
      'card.qr.d': 'Turn a link or text into a QR code and save it as PNG.',
      'card.i2p.t': 'Image to PDF',
      'card.i2p.d': 'Combine photos into a single PDF document in the order you choose.',
      'card.split.t': 'Split PDF',
      'card.split.d': 'Pull out only the pages you need, or split every page into its own file.',
      'card.date.t': 'Date calculator',
      'card.date.d': 'Countdown, days between two dates, and adding or subtracting days.',
      'card.crop.t': 'Crop image',
      'card.crop.d': 'Cut out any region, rotate and flip. Fixed aspect ratios supported.',
      'card.unit.t': 'Unit converter',
      'card.unit.d': 'Length, weight, area, volume, temperature, speed and data size.',
      'card.age.t': 'Age calculator',
      'card.age.d': 'Your exact age, plus zodiac sign and days until your next birthday.',

      /* 이미지 압축 */
      'imgc.title': 'Compress image — free online, no upload',
      'imgc.h1': 'Compress image',
      'imgc.lead': 'Reduce file size by adjusting quality and dimensions. Several photos at once.',
      'imgc.drop': 'Drop photos here, or click to choose',
      'imgc.drop2': 'JPG · PNG · WebP · GIF · BMP · multiple files supported',
      'imgc.quality': 'Quality',
      'imgc.qualityHint': 'Lower means smaller files but softer detail. 70–80% is usually the sweet spot.',
      'imgc.maxw': 'Maximum width (px)',
      'imgc.maxwHint': 'Height follows automatically to keep the aspect ratio. Images are never enlarged.',
      'imgc.format': 'Save as',
      'imgc.count': 'Images',
      'imgc.before': 'Original total',
      'imgc.after': 'New total',
      'imgc.saved': 'Saved',
      'imgc.saveAll': 'Save all',
      'imgc.working': 'Converting…',
      'imgc.bigger': 'The result came out larger. Try lowering the quality or choosing JPG or WebP.',
      'imgc.none': 'No image could be converted.',
      'imgc.save': 'Save',
      'imgc.upsellH': 'Need to process hundreds of photos in one go?',
      'imgc.upsellP': 'The desktop version takes a whole folder, keeps your subfolder structure, converts everything and hands you a ZIP. You do not even need a browser open.',
      'imgc.upsellB': 'See the batch version',
      'opt.keep': 'Keep original size',
      'opt.jpg': 'JPG (best for photos, small files)',
      'opt.webp': 'WebP (smallest files)',
      'opt.png': 'PNG (keeps transparency, larger files)'
    },

    ja: {
      'brand': 'ツール<span>モア</span>',
      'nav.home': 'ホーム',
      'nav.imgc': '画像圧縮',
      'nav.crop': '画像切り抜き',
      'nav.i2p': '画像→PDF',
      'nav.char': '文字数カウント',
      'nav.merge': 'PDF結合',
      'nav.split': 'PDF分割',
      'nav.conv': 'ファイル変換',
      'nav.qr': 'QRコード',
      'nav.unit': '単位変換',
      'nav.date': '日付計算',
      'nav.age': '年齢計算',
      'foot.note': '© ツールモア · すべてブラウザ内で処理されます',
      'badge.file': '🔒 ファイルはアップロードされません',
      'badge.text': '🔒 入力内容は外部に送信されません',
      'btn.reset': 'リセット',
      'btn.clear': 'すべて削除',
      'msg.pickImage': '画像ファイルを選んでください。',
      'msg.pickPdf': 'PDFファイルを選んでください。',
      'msg.reading': 'ファイルを読み込んでいます…',

      'home.title': 'ツールモア — インストール不要の無料オンラインツール',
      'home.h1': '必要な道具だけ、無料で',
      'home.lead': 'インストールも会員登録も不要です。すべてブラウザ内で処理され、ファイルはどこにも送信されません。',
      'home.why': 'ツールモアの特徴',
      'home.why1.h': 'ファイルがサーバーに届きません',
      'home.why1.p': '多くの変換サイトはファイルをサーバーへアップロードしてから処理します。ツールモアのツールはすべてブラウザ内のJavaScriptだけで動きます。ネット接続を切っても動作するのはそのためです。',
      'home.why2.h': '登録も透かしもありません',
      'home.why2.p': 'メールアドレスを求めず、結果にロゴを入れず、利用回数も制限しません。',
      'home.why3.h': 'スマホでもそのまま',
      'home.why3.p': 'スマートフォンのブラウザでも同じように動作します。アプリのインストールは不要です。',
      'card.imgc.t': '画像の容量を減らす',
      'card.imgc.d': '画質とサイズを調整して容量を削減。JPG・PNG・WebP対応。',
      'card.char.t': '文字数カウント',
      'card.char.d': '空白あり・なしの文字数、単語数、バイト数を一度に。',
      'card.merge.t': 'PDF結合',
      'card.merge.d': '複数のPDFを好きな順番に並べて1つにまとめます。',
      'card.conv.t': 'CSV・JSON・Excel変換',
      'card.conv.d': '表形式のファイルを相互に変換します。',
      'card.qr.t': 'QRコード作成',
      'card.qr.d': 'URLや文字をQRコードにしてPNGで保存できます。',
      'card.i2p.t': '画像をPDFに変換',
      'card.i2p.d': '複数の写真を好きな順番で1つのPDF文書にします。',
      'card.split.t': 'PDF分割',
      'card.split.d': '必要なページだけ取り出したり、1ページずつ分割します。',
      'card.date.t': '日付計算機',
      'card.date.d': 'カウントダウン、2つの日付の間の日数、日付の加減算。',
      'card.crop.t': '画像の切り抜き',
      'card.crop.d': '必要な範囲だけ切り抜き、回転・反転も。比率固定に対応。',
      'card.unit.t': '単位変換',
      'card.unit.d': '長さ・重さ・面積・体積・温度・速度・データ容量。',
      'card.age.t': '年齢計算機',
      'card.age.d': '満年齢と干支、次の誕生日までの日数がわかります。',

      'imgc.title': '画像圧縮 — 無料・アップロード不要',
      'imgc.h1': '画像の容量を減らす',
      'imgc.lead': '画質とサイズを調整して容量を減らします。複数枚を一度に処理できます。',
      'imgc.drop': '写真をドラッグするか、クリックして選択',
      'imgc.drop2': 'JPG · PNG · WebP · GIF · BMP · 複数選択可',
      'imgc.quality': '画質',
      'imgc.qualityHint': '下げるほど容量は減りますが画質も落ちます。70〜80%が目安です。',
      'imgc.maxw': '最大の横幅 (px)',
      'imgc.maxwHint': '縦は比率に合わせて自動調整されます。元より大きくはなりません。',
      'imgc.format': '保存形式',
      'imgc.count': '枚数',
      'imgc.before': '元の合計',
      'imgc.after': '変換後の合計',
      'imgc.saved': '削減',
      'imgc.saveAll': 'すべて保存',
      'imgc.working': '変換中です…',
      'imgc.bigger': '変換後の方が大きくなりました。画質を下げるか、JPG・WebPを選んでみてください。',
      'imgc.none': '変換できる画像がありません。',
      'imgc.save': '保存',
      'imgc.upsellH': '数百枚をフォルダごと処理したい場合',
      'imgc.upsellP': 'デスクトップ版はフォルダをまるごと読み込み、サブフォルダ構成を保ったまま変換してZIPにまとめます。ブラウザを開いておく必要もありません。',
      'imgc.upsellB': '一括処理版を見る',
      'opt.keep': '元のサイズを保持',
      'opt.jpg': 'JPG (写真向き・容量小)',
      'opt.webp': 'WebP (最も容量が小さい)',
      'opt.png': 'PNG (透過を保持・容量大)'
    }
  };

  /* ===== 엔진 ===== */
  var current = 'ko';

  function detect() {
    try {
      var saved = localStorage.getItem(STORE);
      if (saved && LANGS[saved]) return saved;
    } catch (e) { /* 시크릿 모드 등에서 localStorage 접근이 막힐 수 있다 */ }
    var n = (navigator.language || '').toLowerCase();
    if (n.indexOf('ko') === 0) return 'ko';
    if (n.indexOf('ja') === 0) return 'ja';
    return n ? 'en' : 'ko';         // 한국어·일본어가 아니면 영어가 더 통한다
  }

  // 스크립트 안에서 쓰는 문자열. 번역이 없으면 한국어 원문을 그대로 돌려준다.
  window.t = function (key, ko) {
    var d = DICT[current];
    return (d && d[key]) || ko;
  };

  function swap(el, attr, key) {
    var d = DICT[current];
    var orig = el.getAttribute('data-i18n-orig-' + attr);
    if (orig === null) {
      orig = attr === 'html' ? el.innerHTML : el.getAttribute(attr);
      el.setAttribute('data-i18n-orig-' + attr, orig === null ? '' : orig);
    }
    var val = (d && d[key]) || orig;
    if (attr === 'html') el.innerHTML = val; else el.setAttribute(attr, val);
  }

  function apply(lang) {
    current = LANGS[lang] ? lang : 'ko';
    document.documentElement.lang = current;

    var els = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++) swap(els[i], 'html', els[i].getAttribute('data-i18n'));

    els = document.querySelectorAll('[data-i18n-ph]');
    for (i = 0; i < els.length; i++) swap(els[i], 'placeholder', els[i].getAttribute('data-i18n-ph'));

    // 한국 전용 설명(원고지·평수·EUC-KR 등)은 다른 언어에서 숨긴다.
    // 억지로 번역하면 뜻이 통하지 않는 내용들이다.
    els = document.querySelectorAll('[data-ko-only]');
    for (i = 0; i < els.length; i++) els[i].style.display = (current === 'ko') ? '' : 'none';

    var d = DICT[current];
    var tKey = document.body.getAttribute('data-i18n-title');
    if (tKey && d && d[tKey]) document.title = d[tKey];

    try { localStorage.setItem(STORE, current); } catch (e) { /* 무시 */ }

    // 페이지 스크립트가 자기 화면을 다시 그릴 수 있도록 알린다
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: current } }));
  }

  function buildSwitcher() {
    var wrap = document.querySelector('.site-header .wrap');
    if (!wrap) return;
    var sel = document.createElement('select');
    sel.className = 'lang-select';
    sel.setAttribute('aria-label', 'Language');
    var html = '';
    for (var k in LANGS) html += '<option value="' + k + '">' + LANGS[k] + '</option>';
    sel.innerHTML = html;
    sel.value = current;
    sel.addEventListener('change', function () { apply(sel.value); });
    wrap.appendChild(sel);
  }

  function init() {
    current = detect();
    buildSwitcher();
    apply(current);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
