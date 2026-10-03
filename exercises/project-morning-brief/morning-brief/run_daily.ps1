# Windows Task Scheduler alternative:
#   schtasks /Create /TN "MorningBrief" /SC DAILY /ST 07:00 /TR "pwsh -File C:\path\to\morning-brief\run_daily.ps1" /F
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
New-Item -ItemType Directory -Force out | Out-Null
uv run --env-file .env morning-brief run --channels file,email *>> "out\daily-$(Get-Date -Format yyyy-MM-dd).log"
exit $LASTEXITCODE
