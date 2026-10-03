---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 25: המשימה היומית ב־GitHub Actions וב־Task Scheduler

**מטרה:** לבנות את המשימה היומית עם קודי יציאה, מעקב, תקציב והרצה יבשה; לפרוס אותה ב־GitHub
Actions עם שתי שורות cron, סודות, תוצרים והפעלה ידנית; לגרסן הנחיה, מודל ואינדקס יחד; ולרשום
אותה גם ב־Task Scheduler.

**זמן משוער:** יום לימוד אחד (יום 49), כ־70 דקות בנייה, ועוד המתנה לריצה המתוזמנת הבאה. **ידע
מקדים:** פרק 25, פרקים 18, 22 ו־23, מאגר GitHub (`ai-course`) ומפתח API.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/schedule_math.py` | חישוב ה־cron לשתי העונות (`TODO 1`), בדיקת השעה המקומית |
| `starter/versions.py` | `Versions`, `check_versions` (`TODO 2`), `write_default` |
| `starter/daily_job.py` | המשימה; מוכנה |
| `starter/github-workflows-daily.yml` | ה־workflow; הולך ל־`.github\workflows\daily.yml` |
| `starter/run_daily.ps1` | הסקריפט ל־Task Scheduler |
| `starter/Dockerfile` | תיבה אופציונלית |
| `tests/test_ch25.py` | ארבע בדיקות, בלי רשת |

## הצעדים

**1. חבילה וקבצים.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch25\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch25-deployment-scheduling\starter\*.py ch25\
Copy-Item path\to\exercises\ch25-deployment-scheduling\starter\run_daily.ps1 .
Copy-Item path\to\exercises\ch25-deployment-scheduling\starter\github-workflows-daily.yml .github\workflows\daily.yml
Copy-Item path\to\exercises\ch25-deployment-scheduling\tests\test_ch25.py tests\
uv run python -c "from pathlib import Path; from ch25.versions import write_default; write_default(Path('versions.json'))"
```

</div>

**2. מלאי את `TODO 1`** (`cron_for_local_time`) ואת **`TODO 2`** (`check_versions`).

**3. בדיקות, והרצה יבשה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch25.py -q
uv run python -m ch25.daily_job --out out --items 3 --dry-run
Get-Content out\run-report.json
```

</div>

**4. ריצה אמיתית מקומית** עם המפתח, ואז קראי את העיתון ואת הדוח.

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch25.daily_job --out out --items 5
uv run python -m ch22.report out\traces.jsonl
```

</div>

**5. GitHub.** הוסיפי את `GEMINI_API_KEY` כ־secret במאגר (Settings, Secrets and variables, Actions).
בדקי את שורות ה־cron מול `cron_for_local_time(7)` לאזור הזמן שלך. דחפי את הקבצים, ולחצי „Run
workflow” בלשונית Actions. ודאי שה־job ירוק ושיש תוצר עם שלושת הקבצים.

**6. גרסאות.** שני בכוונה את `MODEL_FAST` במשתני הסביבה ל־`gemini-9-ultra` והריצי
`check_versions`; החזירי. **בפתק:** מה היית משחזרת ב־rollback, ולמה לא רק את ההנחיה.

**7. Task Scheduler** (PowerShell מורם):

<div dir="ltr" align="left">

```powershell
schtasks /Create /TN "MorningBrief" /SC DAILY /ST 07:00 /TR "pwsh -File C:\path\to\ai-course\run_daily.ps1" /F
schtasks /Run /TN "MorningBrief"
Get-Content out\daily-*.log | Select-Object -Last 5
```

</div>

**8. המתנה.** למחרת, ודאי שהריצה המתוזמנת ב־GitHub ייצרה תוצר, או דילגה עם קוד 2 בשעה הלא נכונה
(רואים את זה בלוג של הצעד).

**9. התחייבות.** `git commit -m "Chapter 25: daily job, versions, Actions schedule, Task Scheduler"`.
התיקייה `out\` לא נכנסת ל־Git; `versions.json` כן.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
{
  "day": "2026-10-03",
  "status": "ok",
  "items_ok": 5,
  "items_failed": 0,
  "calls": 5,
  "spent_usd": 0.001083,
  "trace_file": "out/traces.jsonl"
}
```

</div>

וב־GitHub: job ירוק עם צעד „offline tests first”, צעד „run the job”, ותוצר `brief-<run_id>`.

## רשימת בדיקה

- [ ] `cron_for_local_time(7)` נותן `0 4 * * *` ו־`0 5 * * *` לירושלים; `is_local_hour` נכון בשתי העונות.
- [ ] `check_versions` מוצא קובץ הנחיה חסר, אי־התאמת מודל, ואינדקס ממודל אחר.
- [ ] ההרצה היבשה כותבת עיתון, דוח ומעקב; תקציב אפס נותן קוד 4 ודוח `budget_exceeded`.
- [ ] ריצה ידנית ירוקה ב־GitHub עם תוצר; הריצה המתוזמנת הבאה רצה או דילגה כצפוי.
- [ ] המשימה רשומה ב־Task Scheduler ורצה פעם אחת; ארבע הבדיקות עוברים.

## רמזים

- `zoneinfo.ZoneInfo("Asia/Jerusalem")` עם תאריך אמיתי נותן את ההיסט הנכון לכל עונה; לא לחשב ביד.
- ב־workflow, `if: always()` על העלאת התוצרים; `exit=2` מתורגם להצלחה שקטה.
- Task Scheduler מריץ בלי הסביבה האינטראקטיבית שלך: נתיב מלא ל־`pwsh`, ו־`Set-Location` בסקריפט.

## הפתרון

`solution/`. שימי לב ל־`--dry-run`: אותו קוד, לקוח מזויף, וזה מה שהבדיקות וה־CI מריצים.

## מה התרגיל מדגים

- משימה שרצה בלי אדם: קודי יציאה, תוצרים תמיד, הרצה יבשה.
- cron ב־UTC מול שעון קיץ, פתור בקוד במקום בתקווה.
- גרסאות של ארבעה דברים יחד, ו־rollback כפעולה מוגדרת.
- אותה משימה בשלוש סביבות: מקומית, Actions, Task Scheduler.

</div>
