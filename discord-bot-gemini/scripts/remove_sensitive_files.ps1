#!/usr/bin/env pwsh
Write-Host "Detection of tracked sensitive files and removal from git index (local)."

$files = @('.env')
foreach ($f in $files) {
    $rv = git ls-files --error-unmatch $f 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Removing tracked file from git index: $f"
        git rm --cached $f
        git commit -m "chore: remove sensitive file $f from repo index"
    } else {
        Write-Host "$f not tracked by git"
    }
}

Write-Host "Done. Consider rotating any exposed keys and running BFG or git-filter-repo if you want to purge them from the entire history." -ForegroundColor Green
