#!/usr/bin/env pwsh
Write-Host "Checking for tracked sensitive files (e.g., .env) in git index..."
$tracked = git ls-files | Where-Object { $_ -match '(\.env$|\.pem$|\.key$)' }
if (-not $tracked) { Write-Host 'No tracked sensitive files found.' } else { Write-Host 'Tracked sensitive files found:'; $tracked }
Write-Host "Done."
