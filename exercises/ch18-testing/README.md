---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 18 ונקודת ביקורת 4: חבילת בדיקות למסכם ול־`ask_notes`

**מטרה:** להשלים את פירמידת הבדיקות של הפרויקט: קלטות של תשובות אמיתיות שמושמעות בלי רשת, בדיקות
חוזה לסכמות ולהצהרות כלים, טענות תכונה על פלט לא־דטרמיניסטי, שלוש מדרגות עם סימונים ודילוג,
קובץ CI, ותקציב טוקנים.

**זמן משוער:** יום לימוד אחד (יום 35), כ־60 דקות בנייה. **ידע מקדים:** פרק 18, התרגילים של פרקים
11 ו־15, ומפתח API להקלטה (שתי קריאות).

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/recorder.py` | קלטת, `ReplayClient`, `RecordingClient` עם `TODO 1`, `client_for_tests` |
| `starter/contracts.py` | `assert_matches_snapshot` עם `TODO 2` |
| `starter/properties.py` | בודקי תכונות וגנרטור; מוכן |
| `starter/conftest.py` | הסימונים, הדגל `--live`, הדילוג, `token_budget`; מוכן. הולך ל־`tests\conftest.py` |
| `starter/test_examples.py` | בדיקת דוגמה לכל מדרגה; הולך ל־`tests\test_ch18_examples.py` |
| `starter/github-workflows-tests.yml` | שלושה jobs; הולך ל־`.github\workflows\tests.yml` |
| `tests/test_ch18.py` | חמש בדיקות של המנגנונים, בלי רשת |

## הצעדים

**1. חבילה, conftest ודוגמאות.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch18\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch18-testing\starter\recorder.py, path\to\exercises\ch18-testing\starter\contracts.py, path\to\exercises\ch18-testing\starter\properties.py ch18\
Copy-Item path\to\exercises\ch18-testing\starter\conftest.py tests\conftest.py
Copy-Item path\to\exercises\ch18-testing\starter\test_examples.py tests\test_ch18_examples.py
Copy-Item path\to\exercises\ch18-testing\tests\test_ch18.py tests\
New-Item -ItemType Directory .github\workflows -Force | Out-Null
Copy-Item path\to\exercises\ch18-testing\starter\github-workflows-tests.yml .github\workflows\tests.yml
```

</div>

אם כבר יש לך `tests\conftest.py`, מזגי: הסימונים, `pytest_addoption`, הדילוג ו־`token_budget`.

**2. מלאי את `TODO 1`** (`RecordingClient.complete`): מפתח, חיפוש בקלטת, קריאה ללקוח האמיתי רק
בהחמצה, שמירה, מונים.

**3. מלאי את `TODO 2`** (`assert_matches_snapshot`): נוצר, תואם, עודכן, או `SnapshotMismatch` עם diff.

**4. המדרגה המהירה, בלי מפתח.** ודאי שאין מפתח בסביבה (אל תשתמשי ב־`--env-file`):

<div dir="ltr" align="left">

```powershell
uv run pytest -q
```

</div>

הבדיקה המוקלטת מדלגת (אין קלטת עדיין), החיה מדלגת (אין דגל), הצילומים נוצרים ב־`tests\snapshots`.
הריצי שוב: הצילומים „matched”. מדדי את הזמן: פחות מעשר שניות.

**5. הקלטה.**

<div dir="ltr" align="left">

```powershell
$env:AI_COURSE_RECORD = "1"
uv run --env-file .env pytest tests\test_ch18_examples.py -q
Remove-Item Env:AI_COURSE_RECORD
uv run pytest -q
```

</div>

הקלטת ב־`tests\cassettes\summarize_cargo_lite.jsonl`. ההרצה השנייה משמיעה אותה בלי מפתח.

**6. קלטת ל־`ask_notes`.** כתבי בדיקה נוספת ב־`test_ch18_examples.py`: שאלה אחת עם תשובה בפתקים,
דרך `run(...)` עם `client_for_tests(...)` ו־`FakeEmbedder`? לא: המשכן גם הוא קריאת רשת. השתמשי
ב־`CachedEmbedder(GeminiEmbedder(), ...)` בזמן ההקלטה, וב־`FakeEmbedder` בהשמעה? זה ישנה את
האחזור. הפתרון הנכון: `CachedEmbedder` עם קובץ המטמון בתוך `tests\cassettes\`, שנכנס ל־Git. אז
ההשמעה מוצאת גם את השיכונים וגם את התשובה. רשמי בפתק למה המטמון של פרק 12 הוא בעצם קלטת.

**7. המדרגה החיה.**

<div dir="ltr" align="left">

```powershell
uv run pytest -q --live -m live                       # skips: no key
uv run --env-file .env pytest -q --live -m live       # runs, within the token budget
```

</div>

**8. CI.** דחפי את `.github\workflows\tests.yml` למאגר `ai-course` עם `git push`, ובדקי שה־job
`fast` ירוק. הוסיפי את `GEMINI_API_KEY` כ־secret במאגר (Settings, Secrets and variables, Actions)
רק אם את רוצה שהמדרגות המתוזמנות ירוצו; הן עולות כסף.

**9. התחייבות.** `git commit -m "Chapter 18: cassettes, contracts, properties, test tiers, CI"`.
הקלטות והצילומים נכנסים; `__pycache__` לא.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
uv run pytest -q
..........................................................................s.s..  [100%]
140 passed, 2 skipped in 6.8s

uv run pytest -q --live -m live
s                                                                              [100%]
1 skipped in 0.3s
SKIPPED [1] tests/conftest.py: GEMINI_API_KEY (or GOOGLE_API_KEY) is not set
```

</div>

## רשימת בדיקה

- [ ] אותה בקשה פעמיים: הקלטה אחת והשמעה אחת; בקשה שונה בתו אחד היא מפתח חדש.
- [ ] החמצת קלטת זורקת `CassetteMiss` עם ההוראה להקלטה, ולא קוראת לרשת.
- [ ] צילום: נוצר, תואם, נכשל עם diff, מתעדכן רק עם משתנה הסביבה.
- [ ] המדרגה המהירה: פחות מעשר שניות, בלי מפתח, כולל קלטות וצילומים.
- [ ] `--live` מדלג בלי מפתח ורץ איתו, בתוך `token_budget`.
- [ ] `tests.yml` במאגר, ו־`fast` ירוק ב־GitHub.

## רמזים

- `Completion` הוא dataclass, אז `asdict` ו־`Completion(**entry["completion"])` הולכים הלוך ושוב.
- `difflib.unified_diff` מקבל רשימות שורות; `splitlines(True)` שומר את תווי השורה החדשה.
- `pytest_collection_modifyitems` רץ אחרי האיסוף; להוסיף `skip` לפריט זול יותר מלמחוק אותו.
- `from conftest import live_enabled` עובד כי pytest מוסיף את `tests\` לנתיב כשיש שם `conftest.py`.

## הפתרון

`solution/`. שימי לב ל־`client_for_tests`: ברירת המחדל היא השמעה; ההקלטה דורשת גם משתנה סביבה
וגם מפתח, כדי שאף הרצה רגילה לא תגיע לרשת בטעות.

## מה התרגיל מדגים

- פירמידה שלמה: מזויפים, קלטות, חוזים, תכונות, שופט, חי, וכל שכבה עם מה שהיא מוכיחה.
- „להקליט פעם אחת, להשמיע לנצח”: מהירות של מזויף עם אמינות של תשובה אמיתית.
- חוזים לדברים שהמודל קורא: שינוי הוא החלטה עם diff.
- CI שלא מוציא כסף בטעות: מדרגות, סודות, דילוג עם סיבה, תקציב.

</div>
