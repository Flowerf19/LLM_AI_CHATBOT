#!/usr/bin/env pwsh
Write-Host "🔒 Running pre-commit PowerShell secret check..."

$patterns = @(
    'GEMINI_API_KEY=',
    'DISCORD_LLM_BOT_TOKEN=',
    'DEEPSEEK_API_KEY=',
    'AIzaSy',
    '-----BEGIN PRIVATE KEY-----'
)

$files = git diff --name-only --cached --diff-filter=ACM | ForEach-Object { $_.Trim() }
if (-not $files) { exit 0 }

$bad = $false
foreach ($file in $files) {
    if (-not (Test-Path $file)) { continue }
    $content = git show (":" + $file)
    foreach ($p in $patterns) {
        if ($content -match [regex]::Escape($p)) {
            Write-Host "❌ Secret pattern found in staged file: $file (pattern: $p)"
            $bad = $true
        }
    }
}

if ($bad) {
    Write-Host "🔴 Aborting commit. Remove secrets or add them to .env and keep .env out of git (.gitignore)." -ForegroundColor Red
    exit 1
}

Write-Host "✅ No obvious secrets detected in staged files." -ForegroundColor Green
exit 0
