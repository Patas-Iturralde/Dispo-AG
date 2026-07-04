# Refresca PATH para esta sesión (Node + Firebase CLI global)
$env:Path = "C:\Program Files\nodejs;$env:APPDATA\npm;" + $env:Path
$firebase = Join-Path $env:APPDATA "npm\firebase.cmd"

Set-Location $PSScriptRoot

Write-Host "Firebase CLI: $(& $firebase --version)" -ForegroundColor Cyan
Write-Host "Desplegando public/index.html a Firebase Hosting..." -ForegroundColor Cyan
& $firebase deploy --only hosting
