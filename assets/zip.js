/* 여러 파일을 ZIP 한 개로 묶는다.
 *
 * 왜 직접 만들었나
 * - JSZip은 95KB다. 우리가 묶는 것은 PDF·JPG·PNG처럼 이미 압축된 파일이라
 *   다시 압축해도 줄어드는 양이 거의 없다. 그래서 압축 없이(store) 담기만 하면 되고,
 *   그건 100줄이면 된다. 외부 파일을 하나도 늘리지 않는 편이 이 사이트에 맞다.
 * - 브라우저 밖으로 나가는 요청이 0인 상태를 유지한다.
 *
 * 한계
 * - ZIP64를 쓰지 않으므로 전체 4GB, 파일 개수 65,535개가 상한이다.
 *   브라우저 메모리가 먼저 바닥나므로 실질적인 제약은 아니지만, 넘으면 예외를 던진다.
 */
(function () {
  'use strict';

  var CRC_TABLE = (function () {
    var t = new Uint32Array(256), c, n, k;
    for (n = 0; n < 256; n++) {
      c = n;
      for (k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(u8) {
    var c = 0xFFFFFFFF;
    for (var i = 0; i < u8.length; i++) c = CRC_TABLE[(c ^ u8[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }

  // ZIP은 1980년대 DOS 시각 형식을 쓴다. 2초 단위이고 1980년이 원년이다.
  function dosTime(d) {
    return ((d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1)) & 0xFFFF;
  }
  function dosDate(d) {
    var y = Math.max(1980, d.getFullYear());
    return (((y - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate()) & 0xFFFF;
  }

  function W(view, off, val, bytes) {
    for (var i = 0; i < bytes; i++) view.setUint8(off + i, (val >>> (i * 8)) & 0xFF);
  }

  function toBytes(x) {
    if (x instanceof Uint8Array) return x;
    if (x instanceof ArrayBuffer) return new Uint8Array(x);
    if (ArrayBuffer.isView(x)) return new Uint8Array(x.buffer, x.byteOffset, x.byteLength);
    throw new Error('bytes must be Uint8Array or ArrayBuffer');
  }

  // 같은 이름이 두 번 들어가면 압축을 푸는 쪽에서 하나가 사라진다. 뒤에 번호를 붙인다.
  function uniqueName(name, used) {
    if (!used[name]) { used[name] = 1; return name; }
    var dot = name.lastIndexOf('.');
    var stem = dot > 0 ? name.slice(0, dot) : name;
    var ext = dot > 0 ? name.slice(dot) : '';
    var n = 2;
    while (used[stem + ' (' + n + ')' + ext]) n++;
    var out = stem + ' (' + n + ')' + ext;
    used[out] = 1;
    return out;
  }

  /* entries: [{ name: '1쪽.pdf', bytes: Uint8Array }]
   * 반환: Blob (application/zip)
   */
  function makeZip(entries, when) {
    if (!entries || !entries.length) throw new Error('빈 목록');
    if (entries.length > 65535) throw new Error('파일이 너무 많습니다 (최대 65,535개)');

    var stamp = when || new Date();
    var time = dosTime(stamp), date = dosDate(stamp);
    var enc = new TextEncoder();
    var used = {};

    var files = entries.map(function (e) {
      var bytes = toBytes(e.bytes);
      return {
        nameBytes: enc.encode(uniqueName(String(e.name), used)),
        bytes: bytes,
        crc: crc32(bytes)
      };
    });

    var total = 0, cdSize = 0;
    files.forEach(function (f) {
      total += 30 + f.nameBytes.length + f.bytes.length;
      cdSize += 46 + f.nameBytes.length;
    });
    if (total + cdSize + 22 > 0xFFFFFFFF) throw new Error('ZIP이 4GB를 넘습니다');

    var out = new Uint8Array(total + cdSize + 22);
    var view = new DataView(out.buffer);
    var off = 0;
    var offsets = [];

    files.forEach(function (f) {
      offsets.push(off);
      W(view, off, 0x04034B50, 4);          // 로컬 파일 헤더 서명
      W(view, off + 4, 20, 2);              // 필요 버전 2.0
      W(view, off + 6, 0x0800, 2);          // 플래그: 파일명이 UTF-8임을 표시 (한글 이름)
      W(view, off + 8, 0, 2);               // 압축 방식 0 = 그대로 담기
      W(view, off + 10, time, 2);
      W(view, off + 12, date, 2);
      W(view, off + 14, f.crc, 4);
      W(view, off + 18, f.bytes.length, 4); // 압축 후 크기
      W(view, off + 22, f.bytes.length, 4); // 원래 크기
      W(view, off + 26, f.nameBytes.length, 2);
      W(view, off + 28, 0, 2);              // 확장 필드 없음
      off += 30;
      out.set(f.nameBytes, off); off += f.nameBytes.length;
      out.set(f.bytes, off); off += f.bytes.length;
    });

    var cdStart = off;
    files.forEach(function (f, i) {
      W(view, off, 0x02014B50, 4);          // 중앙 디렉터리 서명
      W(view, off + 4, 20, 2);              // 만든 버전
      W(view, off + 6, 20, 2);              // 필요 버전
      W(view, off + 8, 0x0800, 2);
      W(view, off + 10, 0, 2);
      W(view, off + 12, time, 2);
      W(view, off + 14, date, 2);
      W(view, off + 16, f.crc, 4);
      W(view, off + 20, f.bytes.length, 4);
      W(view, off + 24, f.bytes.length, 4);
      W(view, off + 28, f.nameBytes.length, 2);
      W(view, off + 30, 0, 2);              // 확장 필드
      W(view, off + 32, 0, 2);              // 주석
      W(view, off + 34, 0, 2);              // 시작 디스크
      W(view, off + 36, 0, 2);              // 내부 속성
      W(view, off + 38, 0, 4);              // 외부 속성
      W(view, off + 42, offsets[i], 4);     // 로컬 헤더 위치
      off += 46;
      out.set(f.nameBytes, off); off += f.nameBytes.length;
    });

    W(view, off, 0x06054B50, 4);            // 끝 기록
    W(view, off + 4, 0, 2);
    W(view, off + 6, 0, 2);
    W(view, off + 8, files.length, 2);
    W(view, off + 10, files.length, 2);
    W(view, off + 12, off - cdStart, 4);
    W(view, off + 16, cdStart, 4);
    W(view, off + 20, 0, 2);

    return new Blob([out], { type: 'application/zip' });
  }

  window.makeZip = makeZip;
  window.zipCrc32 = crc32;   // 검증용
})();
