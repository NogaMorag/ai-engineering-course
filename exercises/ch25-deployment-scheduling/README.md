---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 25: המשימה היומית ב־GitHub Actions וב־Task Scheduler

**מטרה:** לבנות את המשימה היומית עם קודי יציאה, מעקב, תקציב והרצה יבשה; לפרוס אותה ב־GitHub
Actions עם שתי שורות cron, סודות, תוצרים והפעלה ידנית; לגרסן הנחיה, מודל ואינדקס יחד; ולרשום
אותה גם ב־Task Scheduler.

**זמן משוער:** יום לימוד אחד (יום 49), כ־70 דקות בנייה, ועוד המתנה לריצה המתוזמנת הבאה.

**ידע מקדים:** פרק 25, פרקים 18, 22 ו־23, הקבצים של פרקים 9, 11, 19, 22 ו־23 במאגר שלך (המשימה
מייבאת את הסכמה, הלקוח, הפידים, המעקב ושומר התקציב), מאגר GitHub (`ai-course`) ומפתח API.

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
בדקי ששתי שורות ה־cron ב־`daily.yml` זהות למה שהחישוב נותן לאזור הזמן שלך:

<div dir="ltr" align="left">

```powershell
uv run python -c "from ch25.schedule_math import cron_for_local_time; print(cron_for_local_time(7))"
```

</div>

דחפי את הקבצים, ולחצי „Run workflow” בלשונית Actions. ודאי שה־job ירוק ושיש תוצר עם שלושת
הקבצים.

**6. גרסאות.** שני בכוונה את `MODEL_FAST` במשתני הסביבה של החלון, הריצי את `check_versions` מול
תיקיית ההנחיות של פרק 8, ואז החזירי את המשתנה:

<div dir="ltr" align="left">

```powershell
$env:MODEL_FAST = "gemini-9-ultra"
uv run python -c "from pathlib import Path; from ch25.versions import load_versions, check_versions; print(check_versions(load_versions(Path('versions.json')), prompts_dir=Path('ch08/prompts')))"
Remove-Item Env:MODEL_FAST
```

</div>

הפלט הצפוי: רשימה עם בעיה אחת, על `MODEL_FAST`. המשימה עצמה מריצה את אותה בדיקה בתחילתה: עם אותו
משתנה סביבה שגוי, `daily_job` מדפיס את הבעיה ויוצא עם קוד 5 בלי לקרוא למודל (הבדיקה האחרונה בקובץ
הבדיקות מוכיחה את זה). אם אצלך חסר גם `ch08\prompts\summarize.v3.txt`,
תופיע בעיה שנייה, וזה בדיוק מה שהבדיקה אמורה לתפוס. **בפתק:** מה היית משחזרת בחזרה לאחור, ולמה לא
רק את ההנחיה.

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
- [ ] ההרצה היבשה כותבת עיתון, דוח ומעקב; תקציב אפס נותן קוד 4 ודוח `budget_exceeded`; אי־התאמת גרסאות נותנת קוד 5 בלי ריצה.
- [ ] ריצה ידנית ירוקה ב־GitHub עם תוצר; הריצה המתוזמנת הבאה רצה או דילגה כצפוי.
- [ ] המשימה רשומה ב־Task Scheduler ורצה פעם אחת; ארבע הבדיקות עוברות.

## טעויות נפוצות ותיקונים

- **ההיסט מחושב ביד.** `cron_for_local_time` מחזירה את אותה שורה לשתי העונות, והבדיקה הראשונה
  נכשלת. חשבי כל עונה מתאריך אמיתי (15 ביולי ו־15 בינואר) דרך `utc_hour_for` ו־`zoneinfo`.
- **`check_versions` מתלוננת על משתנה שלא מוגדר.** כשאין `MODEL_FAST` בסביבה מופיעה „אי־התאמה”
  והבדיקה מצפה לרשימה ריקה. משווים רק כשהמשתנה קיים; היעדר אינו סתירה.
- **הריצה המתוזמנת אדומה בשעה הלא נכונה.** ב־Actions רואים כישלון עם קוד יציאה 2. הצעד חייב
  לתרגם 2 להצלחה שקטה (`exit 0`) ולדלג על העלאת התוצרים.
- **`versions.json` לא נוצר.** המשימה רצה עם מודל ברירת המחדל, ובצעד 6 אין מה לבדוק. הריצי את
  השורה האחרונה של צעד 1, שכותבת את הקובץ עם `write_default`.
- **הסוד לא מוגדר במאגר.** הריצה ב־GitHub נופלת בקריאה הראשונה למודל עם שגיאת הרשאה. הוסיפי את
  `GEMINI_API_KEY` תחת Settings, Secrets and variables, Actions, ולחצי שוב על „Run workflow”.
- **Task Scheduler לא מוצא את קובץ הסביבה.** הלוג ריק או מדווח שאין מפתח, כי המשימה רצה
  מתיקייה אחרת. הסקריפט חייב להתחיל ב־`Set-Location` לתיקייה שלו, והנתיב ב־`/TR` חייב להיות מלא.

## רמזים

- `zoneinfo.ZoneInfo("Asia/Jerusalem")` עם תאריך אמיתי נותן את ההיסט הנכון לכל עונה; לא לחשב ביד.
- ב־workflow, `if: always()` על העלאת התוצרים; `exit=2` מתורגם להצלחה שקטה.
- Task Scheduler מריץ בלי הסביבה האינטראקטיבית שלך: נתיב מלא ל־`pwsh`, ו־`Set-Location` בסקריפט.

## הפתרון

`solution/`. הפתרון עובד כי המשימה מופרדת מהלקוח שלה: `run_job` מקבלת את הלקוח ואת כלי המעקב
כפרמטרים, ולכן ההרצה היבשה מריצה בדיוק את אותו קוד עם לקוח מזויף, וזה מה שהבדיקות וה־CI מריצים
בלי מפתח.
קודי היציאה והדוח שנכתב בכל נתיב, גם בכישלון, הופכים את הריצה לקריאה בלי אדם: ה־workflow קורא
את הקוד, לא את הלוג. והשעה המקומית נבדקת בקוד, מתוך `zoneinfo`, ולכן שתי שורות cron ב־UTC נותנות
ריצה אחת ביום בשעה הנכונה בכל עונה.

## מה התרגיל מדגים

- משימה שרצה בלי אדם: קודי יציאה, תוצרים תמיד, הרצה יבשה.
- cron ב־UTC מול שעון קיץ, פתור בקוד במקום בתקווה.
- גרסאות של ארבעה דברים יחד, וחזרה לאחור כפעולה מוגדרת.
- אותה משימה בשלוש סביבות: מקומית, Actions, Task Scheduler.

</div>
