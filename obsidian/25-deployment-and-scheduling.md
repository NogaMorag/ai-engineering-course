---
direction: rtl
tags: [ai-course, book]
chapter: 25
---
# פריסה ותזמון

- **קוד / הגדרה / סביבה / סוד / גרסאות:** Git / קובץ בגיט / env / `.env` ו־Secrets / `versions.json`.
- **cron = UTC בלי DST.** 07:00 ירושלים = 04:00 UTC קיץ, 05:00 חורף. שתי שורות + `--local-hour 7`.
- **workflow:** secrets, `upload-artifact` עם `if: always()`, `workflow_dispatch`; בדיקות לפני הריצה.
- **versions.json:** הנחיה, מודל, אינדקס, סכמה; `check_versions` לפני הריצה; rollback = שחזור הקובץ.
- **קנרית** לפני החלפה. **קודי יציאה:** 0 / 2 דילוג / 3 כשל / 4 תקציב. **דוח תמיד.** `--dry-run`.
- **Task Scheduler:** זמן מקומי, `.env`, מחשב דלוק. **Docker:** כשהשרת לא שלך.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
cron      cron_for_local_time(7, 0) -> summer "0 4 * * *", winter "0 5 * * *";  is_local_hour(now_utc, 7)
job       python -m ch25.daily_job --out out --items 5 [--dry-run] [--local-hour 7] [--versions versions.json]   exit 0/2/3/4
versions  load_versions(path) -> Versions; check_versions(v, prompts_dir=, env=, index_metadata=) -> [problems]
actions   .github/workflows/daily.yml: schedule x2 + workflow_dispatch; secrets.GEMINI_API_KEY; pytest first; upload-artifact if: always()
windows   schtasks /Create /TN "MorningBrief" /SC DAILY /ST 07:00 /TR "pwsh -File ...\run_daily.ps1" /F
docker    docker build -t morning-brief . ; docker run --rm -e GEMINI_API_KEY -v "$PWD/out:/app/out" morning-brief
```

</div>

קישורים: [[24-security-and-privacy]] · [[26-choosing-models-and-methods]]
