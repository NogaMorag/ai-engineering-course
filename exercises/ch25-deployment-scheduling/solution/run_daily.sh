#!/usr/bin/env bash
# Chapter 25: the Mac / Linux local-scheduler alternative (the Windows twin is run_daily.ps1).
#   crontab -e  ->  0 7 * * * cd $HOME/ai-course && bash run_daily.sh >> out/cron.log 2>&1
# cron runs in local time, so 07:00 stays 07:00 all year; it does not run while the laptop sleeps (launchd does).
set -u
cd "$(dirname "$0")"
mkdir -p out
uv run --env-file .env python -m ch25.daily_job --out out --items 5 >> "out/daily-$(date +%F).log" 2>&1
