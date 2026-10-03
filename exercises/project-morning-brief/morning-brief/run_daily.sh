#!/usr/bin/env bash
# Mac / Linux local scheduler alternative (the Windows twin is run_daily.ps1):
#   crontab -e  ->  0 7 * * * cd $HOME/morning-brief && bash run_daily.sh >> out/cron.log 2>&1
# cron uses local time, so no DST trick is needed; it does not run while the laptop sleeps (launchd does).
set -u
cd "$(dirname "$0")"
mkdir -p out
uv run --env-file .env morning-brief run --channels file,email >> "out/daily-$(date +%F).log" 2>&1
