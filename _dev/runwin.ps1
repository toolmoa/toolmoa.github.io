# 검사 페이지를 실제 크롬 창으로 띄우고, 창 제목에 결과가 실릴 때까지 기다려 출력한다.
#
#   powershell -File _dev/runwin.ps1 en4 selftest ...
#
# run.sh 를 에이전트 셸(Bash)에서 돌리면 명령이 끝날 때 크롬이 같이 죽는다.
# 그래서 PowerShell Start-Process 로 띄운다. 플래그는 run.sh 와 같다.
# 경로에 공백("claude code")이 있어 주소는 %20 으로 인코딩한다.
# 창 제목은 Get-Process.MainWindowTitle 로 못 읽을 때가 있어 EnumWindows 로 훑는다.
[CmdletBinding(PositionalBinding = $false)]
param([Parameter(Position = 0, ValueFromRemainingArguments = $true)][string[]]$Names, [int]$TimeoutSec = 240)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

Add-Type @'
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public static class Win {
  delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc f, IntPtr p);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  public static List<string> Titles() {
    var r = new List<string>();
    EnumWindows((h, p) => { if (IsWindowVisible(h)) { var sb = new StringBuilder(65536); GetWindowText(h, sb, 65536); if (sb.Length > 0) r.Add(sb.ToString()); } return true; }, IntPtr.Zero);
    return r;
  }
}
'@

$prefix = @{}
foreach ($n in $Names) {
  $page = Join-Path $root "_dev\$n.html"
  if (-not (Test-Path $page)) { throw "없는 검사: $n" }
  $url = 'file:///' + (($page -replace '\\', '/') -replace ' ', '%20')
  $prof = Join-Path $root "_dev\.prof-$n"
  # 같은 검사의 이전 창이 남아 있으면 그 제목(옛 결과)을 읽어 버린다. 먼저 닫는다.
  Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" |
    Where-Object { $_.CommandLine -like "*.prof-$n`"*" -or $_.CommandLine -like "*.prof-$n *" } |
    ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop } catch {} }
  Start-Sleep -Milliseconds 800
  Start-Process -FilePath $chrome -ArgumentList @(
    "--user-data-dir=`"$prof`"", '--allow-file-access-from-files', '--no-first-run',
    '--no-default-browser-check', '--disable-features=ChromeWhatsNewUI',
    '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding',
    '--disable-background-timer-throttling', '--new-window', $url)
  # 제목 앞머리: 검사 페이지가 쓰는 표식(RESULT·VERIFY·REAL·OPTS·EN4 …)은 제각각이라 숫자/숫자 형태로 찾는다
  $prefix[$n] = $null
}

# 띄우기 전부터 떠 있던 다른 검사 창의 제목은 세지 않는다 (이번에 띄운 것만 기다린다)
$before = @{}
foreach ($t in [Win]::Titles()) { $before[$t] = 1 }
$deadline = (Get-Date).AddSeconds($TimeoutSec)
$done = @{}
while ((Get-Date) -lt $deadline -and $done.Count -lt $Names.Count) {
  Start-Sleep -Milliseconds 1500
  foreach ($t in [Win]::Titles()) {
    if ($before.ContainsKey($t)) { continue }
    # exif 처럼 " :: " 뒤 설명이 없는 검사도 있다
    if ($t -match '^([A-Z0-9-]+) (\d+)/(\d+)( :: | - |$)') {
      $key = $Matches[1]
      if (-not $done.ContainsKey($key)) { $done[$key] = $t }
    }
  }
}
foreach ($k in $done.Keys) {
  $t = $done[$k] -replace ' - Google Chrome$', ''
  "=== $k"
  ($t -split ' ;; ') | ForEach-Object { '  ' + $_ }
}
if ($done.Count -lt $Names.Count) { "시간 초과: 결과가 나온 검사 $($done.Count) / $($Names.Count)" }
