# 툴모아 (toolmoa)

한국어 키워드를 노린 클라이언트 사이드 웹툴 모음. 서버 없이 브라우저에서만 동작한다.

## 사업 원칙 (반드시 유지)

1. **계정 격리** — 이 저장소는 Claude 계정과 무관하다. 배포는 GitHub 계정으로만 한다.
2. **자기자본 0원** — 아래 "비용" 표의 모든 항목이 0원이다. 유료 전환은 **매출 발생 이후**에만.
3. **금융 배제** — 금융·투자·재테크 성격의 툴이나 콘텐츠는 추가하지 않는다.

## 비용

| 항목 | 서비스 | 비용 |
|---|---|---|
| 호스팅 | GitHub Pages | 0원 |
| 주소 | `<아이디>.github.io` | 0원 |
| SSL | GitHub 기본 제공 | 0원 |
| 서버 | 없음 (전부 브라우저 처리) | 0원 |
| 판매/결제 | Gumroad (판매 시 수수료만, 선불 없음) | 0원 |

## 구성

```
index.html            홈 (툴 목록)
404.html              없는 주소로 들어왔을 때 (툴 목록으로 안내)
image-compress.html   이미지 용량 줄이기      ← 키워드: 이미지 용량 줄이기, 사진 크기 조절
image-crop.html       이미지 자르기           ← 키워드: 사진 자르기, 이미지 크롭
img-to-pdf.html       이미지 PDF 변환         ← 키워드: 사진 PDF 변환
char-count.html       글자수 세기·원고지 계산  ← 키워드: 글자수 세기, 원고지 매수
text-clean.html       텍스트 정리             ← 키워드: 중복 줄 제거, 명단 정리
pdf-merge.html        PDF 합치기             ← 키워드: PDF 합치기, PDF 병합
pdf-split.html        PDF 나누기             ← 키워드: PDF 나누기, 페이지 추출
pdf-edit.html         PDF 회전·삭제·순서 변경  ← 키워드: PDF 회전, PDF 페이지 삭제
file-convert.html     CSV·JSON·엑셀 변환     ← 키워드: csv json 변환, 엑셀 변환
qr-generate.html      QR코드 만들기           ← 키워드: QR코드 만들기, QR 생성
password-gen.html     비밀번호 생성기         ← 키워드: 비밀번호 생성기
unit-convert.html     단위 변환기·평수 계산    ← 키워드: 평수 계산, 인치 cm 변환
date-calc.html        날짜 계산기·디데이       ← 키워드: 디데이 계산, 근무일수
age-calc.html         만 나이 계산기          ← 키워드: 만 나이 계산기, 세는 나이
en/                   영어 SEO 페이지 8종 (번역본이 아니라 따로 쓴 글)
assets/style.css      공통 스타일 (다크모드 포함)
assets/i18n.js        다국어 엔진 겸 사전 (ko/en/ja)
assets/og/            공유용 이미지 1200×630 (페이지마다 1장, 생성물)
robots.txt            검색엔진 안내
sitemap.xml           사이트맵 (생성물)
```

`assets/og/` 와 `sitemap.xml` 그리고 각 HTML 안의 `<!-- SEO:AUTO -->` 블록은
**스크립트가 만든다. 손으로 고치지 말 것** (다음 실행 때 덮어쓰인다).

외부 라이브러리는 `assets/vendor/`에 **직접 포함**되어 있다 (CDN을 쓰지 않는다).
`pdf-lib`(PDF 병합), `xlsx`(파일 변환), `qrious`(QR 생성). 셋 다 무료·오픈소스다.
CDN을 안 쓰는 이유는 주소가 바뀌거나 CDN이 죽으면 사이트가 통째로 망가지기 때문이다.
실제로 처음에 쓰려던 `qrcode` 패키지의 CDN 경로가 404여서 QR이 동작하지 않았다.

이미지 압축과 글자수 세기는 라이브러리 없이 순수 자바스크립트로 동작한다.

## 자동 점검

검사는 전부 `_dev/` 안에 있다. 밑줄로 시작해 GitHub Pages(Jekyll)가 배포에서 빼므로,
버전 관리는 되면서 사이트에는 공개되지 않는다.

### 바로 돌리는 것 (Perl · 결과가 글로 나온다)

```
perl _dev/audit.pl        정적 점검: 깨진 링크, 중복 id, 빠진 자산, SEO 위생, 한/영 기능 대조
perl _dev/i18ncheck.pl    사전 키 누락·미사용 (양방향)
perl _dev/coverage.pl     조작 요소 중 검사에서 한 번도 안 쓰인 것
perl _dev/seocheck.pl     구조화 데이터·공유 메타 (JSON::PP 로 실제 파싱해 대조)
```

### 브라우저로 돌리는 것

```
bash _dev/run.sh selftest edge layout gaps opts i18nlive verify verify-real deep paths full
```

결과는 **창 제목**에 실린다 (`RESULT 20/20 :: …`). 헤드리스로 돌리지 말 것 —
파일을 읽는 검사는 읽기가 끝나기 전에 판정이 나 버린다.
`paths`·`gaps` 처럼 PDF 미리보기를 보는 검사는 **한 번에 하나씩** 돌린다
(pdf.js 1.3MB 를 나중에 받는 구조라 창을 여러 개 띄우면 거짓 실패한다).

### 생성기 (툴을 고치거나 늘린 뒤 다시 돌린다)

```
perl _dev/ogbuild.pl .    공유 이미지용 HTML 을 페이지에서 읽어 만든다
bash _dev/ogshot.sh       그것을 1200×630 PNG 로 찍어 assets/og/ 에 넣는다
perl _dev/seometa.pl .    og:*·twitter:*·FAQPage·BreadcrumbList 를 <head> 에 넣는다
perl _dev/sitemap.pl .    sitemap.xml 을 실제 파일 목록에서 다시 만든다
```

FAQ 구조화 데이터는 페이지에 이미 적힌 `<details>` 문답을 **읽어서** 만든다.
화면 문구와 구조화 데이터가 어긋나면 구글이 리치 스니펫을 빼기 때문에,
두 곳을 따로 적지 않고 HTML 한 곳만 고치면 되게 해 두었다.

## 로컬에서 확인

`index.html`을 브라우저로 열면 그대로 동작한다. 빌드 과정이 없다.

## 배포 (GitHub Pages)

1. GitHub 가입 후 **저장소 이름을 `<본인아이디>.github.io`로** 새 저장소 생성 (Public)
2. 이 폴더의 파일 전부를 저장소 루트에 업로드 (웹에서 드래그 앤 드롭 가능)
3. Settings → Pages → Source를 `main` 브랜치 `/ (root)`로 지정
4. 1~2분 뒤 `https://<본인아이디>.github.io` 에서 확인

### 배포 후 반드시 할 일

주소가 정해지면 `example.github.io`를 **실제 주소로 일괄 치환**한다. 들어 있는 파일:

- 각 HTML의 `<link rel="canonical">`
- `robots.txt`
- `sitemap.xml`

그다음 [Google Search Console](https://search.google.com/search-console)에 사이트를 등록하고
`sitemap.xml`을 제출한다. 색인까지 보통 1~4주 걸린다.

## 수익화 순서

1. **Gumroad 상품 판매** — `image-compress.html`, `pdf-merge.html`의 `.upsell` 블록에
   `id="upsell-link"` 링크가 `#`로 비어 있다. Gumroad 상품을 만든 뒤 그 주소로 교체한다.
2. **첫 매출 발생 후** 도메인 구입 (연 1.5만원 상당) — 이때부터 사업 수익으로 지출한다.
3. **도메인 연결 후** 애드센스 신청. 승인되면 각 페이지의 `<!-- AD:XXX -->` 주석 위치에
   광고 코드를 넣는다. (무료 서브도메인 상태로는 애드센스 승인이 거의 나지 않는다)

## 툴 추가 원칙

툴 하나 = 검색 키워드 하나다. 추가할 때는 반드시:

- 별도 HTML 파일로 만든다 (한 페이지에 몰면 키워드가 분산된다)
- `<title>`과 `description`에 **사람들이 실제로 검색하는 한국어 표현**을 넣는다
- 모든 페이지의 헤더/푸터 링크와 `sitemap.xml`에 추가한다
- 서버가 필요한 기능은 만들지 않는다 (비용 0원 원칙)
