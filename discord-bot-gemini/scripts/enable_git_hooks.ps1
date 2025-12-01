#!/usr/bin/env pwsh
Write-Host "Configuring repo hooks to use the .githooks directory..."
git config core.hooksPath .githooks
Write-Host "Hooks path set to: $(git config --get core.hooksPath)"
Write-Host "Note: This only configures hooks locally for this repo. Other contributors must run this command or use a setup script."
