<#
  Push the trading bot to GitHub.

  Run this after creating the repo on github.com/new
  (name: trading-bot, visibility: Public, do NOT tick "add a README").

  A PUBLIC repo is used on purpose: GitHub Actions minutes are unlimited
  on public repositories, so the research can run every 4 hours for free.

  Usage:
    .\push-to-github.ps1
    .\push-to-github.ps1 -RepoName my-repo -Private
#>
param(
  [string]$RepoName = "trading-bot-alpha",
  [string]$Branch = "main",
  [string]$User = "alwanaltabieacoly-cmd",
  [switch]$Private
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$visibility = if ($Private) { "private" } else { "public" }

Write-Host "=== 1/4  Check GitHub auth ===" -ForegroundColor Cyan
gh auth status 2>&1 | Select-Object -First 3 | ForEach-Object { "  $_" }

$remoteUrl = "https://github.com/$User/$RepoName.git"

Write-Host "`n=== 2/4  Make sure the repo exists ===" -ForegroundColor Cyan
$exists = $false
gh repo view "$User/$RepoName" --json name 2>$null | Out-Null
if ($?) { $exists = $true }

if (-not $exists) {
  Write-Host "  creating $User/$RepoName as $visibility ..." -ForegroundColor Yellow
  gh repo create "$User/$RepoName" --$visibility --description "Bybit crypto trading bot with a self-testing research harness (trend following, rolling walk-forward validation, deflated Sharpe correction)" 2>&1 | ForEach-Object { "  $_" }
  if (-not $?) {
    Write-Host ""
    Write-Host "  This token cannot create repos." -ForegroundColor Red
    Write-Host "  Create it manually: https://github.com/new" -ForegroundColor Yellow
    Write-Host "    name: $RepoName   visibility: $visibility   README: leave unticked" -ForegroundColor Yellow
    Write-Host "  Then run this script again." -ForegroundColor Yellow
    exit 1
  }
} else {
  Write-Host "  repo already exists"
}

Write-Host "`n=== 3/4  Wire up the remote ===" -ForegroundColor Cyan
if (git remote | Select-String -SimpleMatch "origin") {
  git remote set-url origin $remoteUrl
  Write-Host "  updated existing origin"
} else {
  git remote add origin $remoteUrl
  Write-Host "  added origin -> $remoteUrl"
}

Write-Host "`n=== 4/4  Push ===" -ForegroundColor Cyan
git push -u origin "HEAD:refs/heads/$Branch"
git push origin "HEAD:refs/heads/dev" 2>$null | Out-Null

Write-Host ""
Write-Host "PUSHED -> https://github.com/$User/$RepoName" -ForegroundColor Green
Write-Host ""
Write-Host "Next: open the Actions tab and click 'Strategy research' -> 'Run workflow'" -ForegroundColor Gray
Write-Host "to trigger the first run immediately. After that it runs every 4 hours" -ForegroundColor Gray
Write-Host "on its own (06:17, 10:17, 14:17, 18:17, 22:17, 02:17 UTC)." -ForegroundColor Gray
