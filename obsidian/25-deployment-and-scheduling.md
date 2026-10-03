---
direction: rtl
tags: [ai-course, book]
chapter: 25
---
# פריסה ותזמון

- **חמישה סוגים:** קוד בגיט; הגדרה בקובץ מגורסן; סביבה במשתני סביבה; סוד בקובץ הסביבה המקומי או
  בסודות של GitHub; גרסאות בקובץ אחד.
- **cron רץ ב־UTC בלי שעון קיץ.** 07:00 בירושלים הוא 04:00 UTC בקיץ ו־05:00 בחורף: שתי שורות,
  והמשימה בודקת את השעה המקומית.
- **ה־workflow:** סודות, העלאת תוצרים גם בכישלון, כפתור הפעלה ידנית; בדיקות לפני הריצה.
- **קובץ הגרסאות:** הנחיה, מודל, אינדקס, סכמה; בדיקה מול המציאות לפני הריצה; חזרה לאחור משחזרת את
  הקובץ ואת האינדקס.
- **קנרית** לפני החלפה. **קודי יציאה:** 0 הצלחה, 2 דילוג, 3 כשל, 4 תקציב, 5 גרסאות. **דוח תמיד.** הרצה יבשה.
- **מתזמן מקומי:** זמן מקומי, קובץ הסביבה, מחשב דלוק (Task Scheduler ב־Windows; cron או launchd
  ב־Mac). **Docker:** כשהשרת לא שלך.
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
