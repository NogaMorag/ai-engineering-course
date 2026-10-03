---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 2: סביבת העבודה והקריאה הראשונה למודל

**מטרה:** להקים את פרויקט הקורס ב־Windows, להריץ קריאה ראשונה למודל Gemini במסלול החינמי, ולהשאיר
אחריך סביבה שניתנת לשחזור, סודות מוגנים ובדיקות עשן שרצות בלי רשת.

**זמן משוער:** שני ימי לימוד. יום 0: שעה עד שעה וחצי כולל הורדות (צעדים 1 עד 4, בסוף השבוע שלפני
ההתחלה). יום 2: כשעה וחצי (צעדים 5 עד 10). **ידע מקדים:** פרק 2 במלואו. על Mac: אותם צעדים, עם טבלת
המקבילות בסעיף 2.13 של הפרק.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/hello_model.py` | שלד התוכנית עם שלושה סימוני `TODO` למילוי |
| `starter/env.example` | תבנית לקובץ הסודות; מעתיקים בשם `.env` וממלאים מפתח |
| `starter/pyproject.toml` | לייחוס בלבד: כך צריך להיראות קובץ ההגדרות שלך בסוף ההקמה |
| `solution/hello_model.py` | פתרון מלא |
| `tests/test_smoke.py` | שלוש בדיקות עשן; מעתיקים לתיקיית הבדיקות של הפרויקט |

## יום 0: הטרמינל וההתקנות

כל פקודה רצה ב־PowerShell 7. אחרי כל התקנה או שינוי במשתני סביבה, פותחים חלון טרמינל חדש. בסוף יום 0
ארבע פקודות הגרסה עונות, ואין עוד מה להתקין עד פרק 12.

**1. טרמינל.** התקיני PowerShell 7 והגדירי אותו כברירת מחדל ב־Windows Terminal (סעיף 2.2). בדיקה:
הפקודה הבאה מדפיסה גרסה שמתחילה ב־7.

<div dir="ltr" align="left">

```powershell
$PSVersionTable.PSVersion
```

</div>

**2. עברית.** הגדירי את משתנה הסביבה שמאפשר ל־Python להדפיס עברית, ואז פתחי טרמינל חדש.

<div dir="ltr" align="left">

```powershell
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
```

</div>

**3. כלים.** התקיני Git, VS Code ו־uv (סעיף 2.3). טרמינל חדש. בדיקה: שלוש פקודות הגרסה עונות.

<div dir="ltr" align="left">

```powershell
winget install --id Git.Git -e --source winget
winget install --id Microsoft.VisualStudioCode -e --source winget
winget install --id=astral-sh.uv -e
```

</div>

<div dir="ltr" align="left">

```powershell
git --version
code --version
uv --version
```

</div>

**4. Python.** התקיני את Python 3.12 דרך uv. בדיקה: הרשימה מציגה 3.12.

<div dir="ltr" align="left">

```powershell
uv python install 3.12
uv python list
```

</div>

## יום 2: הפרויקט, המפתח והקריאה הראשונה

**5. פרויקט.** הקימי את הפרויקט (סעיף 2.5). בדיקה: הפקודה האחרונה מדפיסה `Python 3.12.x`.

<div dir="ltr" align="left">

```powershell
cd $HOME
mkdir ai-course
cd ai-course
git init
uv init --bare --python 3.12
uv python pin 3.12
uv add "google-genai>=2.28,<3" pydantic
uv add --dev pytest ruff
uv run python --version
```

</div>

צרי את קובץ `.gitignore` (התוכן בסעיף 2.5, כולל השורה `.env`), קובץ `README.md` קצר, והוסיפי לסוף
`pyproject.toml` את קטע ההגדרות של pytest:

<div dir="ltr" align="left">

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

</div>

**6. מפתח.** צרי מפתח ב־AI Studio (סעיף 2.6). העתיקי את `starter/env.example` לתיקיית הפרויקט בשם
`.env` והדביקי בו את המפתח. שמרי עותק נוסף בלי המפתח בשם `.env.example`. בדיקה: הפקודה הבאה מדפיסה
`.env`, כלומר הקובץ מוחרג מ־Git.

<div dir="ltr" align="left">

```powershell
git check-ignore .env
```

</div>

**7. הקוד.** צרי תיקייה `ch02` ובתוכה קובץ ריק `__init__.py`. העתיקי את `starter/hello_model.py`
אל `ch02\hello_model.py`. מלאי את שלושת ה־`TODO`:

- גוף הפונקציה `estimate_paid_cost`
- הקריאה למודל
- קריאת שלושת מספרי הטוקנים מתוך `usage`

**8. הרצה.** בדיקה: תשובה בעברית קריאה, שלוש שורות טוקנים, זמן, ומחיר משוער.

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python ch02/hello_model.py
```

</div>

**9. בדיקות.** העתיקי את `tests/test_smoke.py` אל `tests\test_smoke.py` בפרויקט. בדיקה: `3 passed`.

<div dir="ltr" align="left">

```powershell
uv run pytest -q
```

</div>

**10. Git.** הגדירי זהות אישית, ודאי שקובץ הסודות אינו מופיע ברשימה, ובצעי התחייבות ראשונה.

<div dir="ltr" align="left">

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.personal@email"
git status
git add .
git commit -m "Course workbench: uv project, first model call, smoke tests"
```

</div>

## פלט צפוי

<div dir="ltr" align="left">

```text
מודל שפה הוא תוכנה שלמדה מכמויות עצומות של טקסט לחזות את ההמשך הסביר ביותר של רצף מילים.
...
----------------------------------------
model:           gemini-3.5-flash-lite
input tokens:    21
output tokens:   58
thought tokens:  0
latency:         1.38 s
paid-tier price: $0.000151 (free tier: $0)
```

</div>

הניסוח והמספרים ישתנו אצלך; הצורה לא.

## רשימת בדיקה

- [ ] גרסת PowerShell מתחילה ב־7, ו־Python מדווח על מצב UTF-8 (הפקודה בסעיף 2.2 מדפיסה `1`)
- [ ] הפרויקט רץ על Python 3.12
- [ ] קובץ ההגדרות מכיל את ה־SDK בגרסה 2 ואת קטע pytest
- [ ] קובץ הסודות קיים ומוחרג מ־Git; קובץ הדוגמה קיים בלי מפתח
- [ ] התוכנית מדפיסה תשובה בעברית קריאה, לא סימני שאלה
- [ ] מודפסים: מספר טוקני קלט, מספר טוקני פלט, מספר טוקני חשיבה, זמן, ומחיר משוער
- [ ] שלוש הבדיקות עוברות
- [ ] יומן Git מכיל התחייבות אחת לפחות, ואין בה את קובץ הסודות

## טעויות נפוצות ותיקונים

- **הרצה מהתיקייה הלא נכונה.** התוכנית מודיעה שאין מפתח, או ש־pytest לא מוצא בדיקות. הריצי `pwd`, ועברי
  לתיקיית `ai-course` לפני כל פקודה.
- **`python` במקום `uv run python`.** מופיע `ModuleNotFoundError: No module named 'google'`, כי רץ Python
  אחר. בקורס כל הרצה מתחילה ב־`uv run`.
- **רווחים או מירכאות סביב המפתח בקובץ הסודות.** השרת מחזיר `API key not valid`. השורה צריכה להיות
  בדיוק `GEMINI_API_KEY=` ואחריה המפתח, בלי רווחים ובלי מירכאות.
- **מפתח ישן במשתנה `GOOGLE_API_KEY`.** הוא גובר על המפתח בקובץ ומייצר `API key not valid` גם כשהקובץ
  נכון. בדקי עם `Get-ChildItem Env:GOOGLE_API_KEY` והסירי אותו.
- **קובץ `__init__.py` חסר בתיקיית `ch02`.** הבדיקות נכשלות על ייבוא של `ch02.hello_model`. צרי קובץ ריק
  בשם הזה בתיקייה.
- **טרמינל ישן אחרי התקנה.** `uv` או `git` „לא מוכרים” למרות שההתקנה הצליחה. סגרי את כל חלונות הטרמינל
  ופתחי חדש; ה־PATH נקרא רק בפתיחה.

## רמזים

1. אם uv לא מוכר אחרי ההתקנה: סגרי את **כל** חלונות הטרמינל, לא רק את הכרטיסייה.
2. אם התוכנית מדפיסה שאין מפתח בסביבה: את כנראה מריצה מתיקייה אחרת מזו שבה קובץ הסודות נמצא.
   הפקודה `pwd` תגלה.
3. חישוב המחיר: המחירים נקובים לכל מיליון טוקנים. חלקי במיליון פעם אחת, בסוף.
4. שדות הטוקנים ב־`usage` יכולים להיות ריקים (`None`) במודלים שלא חשבו. התייחסי לריק כאל אפס.
5. סימני שאלה במקום עברית: סעיף 2.2, ואז טרמינל חדש. אין דרך נקייה לעקוף את זה מתוך הקוד.

## הפתרון

הקובץ `solution/hello_model.py` מכיל את התוכנית המלאה. השווי אותו לשלך רק אחרי שהתוכנית שלך רצה, או
אחרי שנתקעת לפחות 20 דקות.

**מה הפתרון מדגים:** הפרדה בין פונקציה טהורה שניתנת לבדיקה בלי רשת (`estimate_paid_cost`) לבין
הקריאה למודל; קריאת המפתח ממשתני הסביבה בלבד; שגיאות שמוצגות כ־traceback שאת לומדת לקרוא (טיפול
אמיתי בפרק 11); והרגל שילווה את כל הקורס: להדפיס את דיווח השימוש של כל קריאה.

## מה התרגיל מדגים

- סביבה שניתנת לשחזור: קובץ הגדרות, קובץ נעילה, ו־Python שמנוהל על ידי כלי אחד.
- סודות מחוץ לקוד ומחוץ ל־Git, נטענים רק בזמן ההרצה.
- הקריאה הבסיסית ביותר למודל, וההרגל לקרוא את דיווח הטוקנים בכל קריאה.
- הפרדה בין לוגיקה טהורה שנבדקת בלי רשת לבין הקריאה למודל.

</div>
