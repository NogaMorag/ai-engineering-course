# Chapter 25 solution: the Windows Task Scheduler alternative. Register once from an elevated PowerShell:
#   schtasks /Create /TN "MorningBrief" /SC DAILY /ST 07:00 /TR "pwsh -File C:\path\to\ai-course\run_daily.ps1" /F
# Task Scheduler runs in local time, so 07:00 is 07:00 all year. The job still needs the key: it reads .env.
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
$log = "out\daily-$(Get-Date -Format yyyy-MM-dd).log"
New-Item -ItemType Directory -Force out | Out-Null
uv run --env-file .env python -m ch25.daily_job --out out --items 5 *>> $log
exit $LASTEXITCODE
