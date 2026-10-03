---
direction: rtl
lang: he
title: "פרק 2: סביבת העבודה ב-Windows והקריאה הראשונה למודל"
chapter: 2
part: "חלק א: התמצאות וסביבת עבודה"
---

<div dir="rtl" lang="he">

# פרק 2: סביבת העבודה ב־Windows והקריאה הראשונה למודל

בסוף הפרק הזה יהיה לך מחשב מוכן לכל הקורס, ותוכנית Python אחת שמדברת עם מודל שפה אמיתי ומדפיסה
את התשובה שלו, כמה טוקנים היא עלתה וכמה זמן לקחה. ההתקנות מינימליות ומכוונות: רק מה שמשרת את
הקורס, כל צעד עם דרך לוודא שהוא הצליח, וטבלת תקלות בסוף. הפקודות כולן ל־PowerShell ב־Windows 11.
הקציבי לפרק כשעתיים, כולל זמן הורדות.

## מה נלמד בפרק

- מה מתקינים ולמה, ומה במכוון לא מתקינים.
- לעבוד עם Windows Terminal ו־PowerShell 7, כולל הגדרה אחת שמונעת בעיות עם עברית.
- להתקין Git, VS Code ו־uv באמצעות `winget`, ולנהל Python ותלויות עם uv בלבד.
- להקים את פרויקט הקורס עם מבנה תיקיות קבוע.
- להשיג מפתח API חינמי של Gemini, לשמור אותו נכון, ולא להדליף אותו לעולם.
- להריץ קריאה ראשונה למודל ולקרוא את דיווח הטוקנים שלה.
- לעצור, להפעיל מחדש ולנקות את כל מה שהתקנת.

## ידע מקדים

פרקים 0 ו־1. היכרות בסיסית עם טרמינל כלשהו.

## 2.1 מה מתקינים, ומה לא

| כלי | מה הוא עושה בקורס | איך מתקינים |
| --- | --- | --- |
| Windows Terminal + PowerShell 7 | הטרמינל שבו תריצי הכול. גרסה 7 תומכת ב־UTF-8 כברירת מחדל, וזה חשוב לעברית. | מובנה ב־Windows 11; PowerShell 7 דרך `winget` |
| `winget` | מנהל ההתקנות של Windows. פקודה אחת לכל כלי, קל לוודא ולהסיר. | מובנה ב־Windows 11 |
| Git | ניהול גרסאות לפרויקט הקורס ולתיק העבודות, ובהמשך GitHub Actions. | `winget` |
| VS Code | העורך. אפשר במקומו Cursor, הכול זהה. | `winget` |
| uv | מנהל גרסאות Python, סביבות וירטואליות ותלויות, עם קובץ נעילה. מריץ סקריפטים בתוך הסביבה. | `winget` |
| Python 3.12 | מותקן דרך uv, לא מאתר python.org. | `uv python install 3.12` |
| google-genai | ה־SDK הרשמי של Gemini ל־Python. | `uv add` |
| pytest, ruff | בדיקות ובדיקת סגנון. | `uv add --dev` |

מה לא מתקינים, ולמה:

- **לא Python מהאתר הרשמי ולא Anaconda.** uv מנהל גרסאות Python בעצמו, בלי להתנגש בשום דבר.
- **לא pip.** uv מחליף אותו, ושומר קובץ נעילה.
- **לא Docker ולא WSL.** לא נחוצים לקורס. אם את אוהבת לעבוד ב־WSL2 זה אפשרי, אבל אז כל הפקודות
  הופכות לפקודות Linux, והספר לא ילווה אותך בזה.
- **לא מסד נתונים חיצוני.** נשתמש ב־SQLite המובנה ב־Python.

> **מונח:** סביבה וירטואלית (virtual environment) היא תיקייה (`.venv`) שמכילה את Python ואת
> החבילות של פרויקט אחד, מבודדת מפרויקטים אחרים. קובץ הנעילה (`uv.lock`) מתעד את הגרסה המדויקת של
> כל חבילה שהותקנה, כך שהסביבה ניתנת לשחזור במחשב אחר. uv יוצר ומנהל את שניהם, ואת לעולם לא צריכה
> „להפעיל” את הסביבה ידנית: הפקודה `uv run` עושה זאת בשבילך.

## 2.2 הטרמינל: Windows Terminal ו־PowerShell 7

Windows 11 מגיע עם Windows Terminal. פתחי אותו (חפשי „Terminal” בתפריט התחל). ברירת המחדל שלו היא
לרוב Windows PowerShell 5.1, הגרסה הישנה. נתקין את PowerShell 7 ונהפוך אותה לברירת המחדל:

<div dir="ltr" align="left">

```powershell
winget install --id Microsoft.PowerShell -e --source winget
```

</div>

סגרי ופתחי מחדש את Windows Terminal. בהגדרות שלו (לחצי על החץ הקטן ליד הכרטיסיות, ואז Settings, ואז
Startup, ואז Default profile) בחרי „PowerShell” בלי המילה Windows לפניו. פתחי כרטיסייה חדשה ובדקי:

<div dir="ltr" align="left">

```powershell
$PSVersionTable.PSVersion
```

</div>

<div dir="ltr" align="left">

```text
Major  Minor  Patch  PreReleaseLabel BuildLabel
-----  -----  -----  --------------- ----------
7      5      0
```

</div>

המספר הראשון צריך להיות 7. בספר, הפקודות מופיעות בלי התחילית `PS C:\...>` שאת רואה במסך, כדי שתוכלי
להעתיק אותן כמו שהן. כמה פקודות שימושיות שחוזרות לאורך הספר:

| פקודה | מה היא עושה |
| --- | --- |
| `pwd` | מדפיסה את התיקייה הנוכחית (זו הראשונה שבודקים כשמשהו „לא נמצא”) |
| `cd <תיקייה>` | מעבר תיקייה; `cd $HOME` מחזיר לתיקיית המשתמשת |
| `ls` | רשימת הקבצים בתיקייה |
| `mkdir <שם>` | יצירת תיקייה |
| `cat <קובץ>` | הדפסת תוכן קובץ |
| `code .` | פתיחת התיקייה הנוכחית ב־VS Code |
| `Ctrl+C` | עצירת תוכנית שרצה |

**הגדרה אחת לעברית, פעם אחת.** Python ב־Windows מניח לעיתים קידוד ישן לפלט, ואז עברית מודפסת
כסימני שאלה או שהתוכנית קורסת עם `UnicodeEncodeError`. הפתרון הקבוע הוא משתנה סביבה
(environment variable) בשם `PYTHONUTF8` עם הערך `1`. משתנה סביבה הוא ערך בשם שהמערכת מעבירה לכל
תוכנית שרצה; נשתמש במנגנון הזה גם למפתח ה־API. הגדירי אותו ברמת המשתמשת, פעם אחת:

<div dir="ltr" align="left">

```powershell
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
```

</div>

הפקודה לא מדפיסה דבר. **סגרי ופתחי מחדש את הטרמינל**: משתנה סביבה חדש נקלט רק בחלונות שנפתחו
אחרי ההגדרה. בדיקה (אחרי שנתקין Python בסעיף 2.4):

<div dir="ltr" align="left">

```powershell
uv run python -c "import sys; print(sys.flags.utf8_mode)"
```

</div>

<div dir="ltr" align="left">

```text
1
```

</div>

## 2.3 התקנת Git, VS Code ו־uv

הריצי את שלוש הפקודות, אחת אחרי השנייה. כל התקנה לוקחת דקה או שתיים ועשויה לבקש אישור במסך:

<div dir="ltr" align="left">

```powershell
winget install --id Git.Git -e --source winget
winget install --id Microsoft.VisualStudioCode -e --source winget
winget install --id=astral-sh.uv -e
```

</div>

סגרי ופתחי מחדש את הטרמינל (ההתקנות מוסיפות תיקיות ל־`PATH`, רשימת המקומות שבהם הטרמינל מחפש
פקודות, והיא נקראת מחדש רק בחלון חדש). ודאי ששלושת הכלים עונים:

<div dir="ltr" align="left">

```powershell
git --version
code --version
uv --version
```

</div>

<div dir="ltr" align="left">

```text
git version 2.5x.x.windows.1
1.10x.x
...
uv 0.12.x (...)
```

</div>

המספרים המדויקים אצלך יהיו שונים; מה שחשוב הוא שאף פקודה לא מחזירה „is not recognized”. התקיני גם
את תוסף Python של VS Code, מהטרמינל:

<div dir="ltr" align="left">

```powershell
code --install-extension ms-python.python
```

</div>

> **ב־Windows:** אם `winget` עצמו אינו מוכר, התקיני מחנות Microsoft את „App Installer” ונסי שוב. אם
> אין לך הרשאות ל־`winget`, אפשר להשתמש במתקין הרשמי של uv (הפקודה שלמטה), ואת Git ו־VS Code להוריד
> מאתריהם. עדכון של uv בעתיד נעשה בפקודה `uv self update`.

<div dir="ltr" align="left">

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

</div>

## 2.4 Python 3.12 דרך uv

<div dir="ltr" align="left">

```powershell
uv python install 3.12
uv python list
```

</div>

הפקודה הראשונה מורידה Python 3.12 לתיקייה שמנוהלת על ידי uv, בלי לגעת בשום Python אחר במחשב.
השנייה מציגה את הגרסאות המותקנות; ליד 3.12 צריך להופיע נתיב בתוך תיקיית uv. למה דווקא 3.12 ולא
החדשה ביותר: כל הספריות בקורס מספקות עבורו חבילות מוכנות ל־Windows, וחלקן עדיין מפגרות בגרסאות
חדשות יותר.

## 2.5 הקמת פרויקט הקורס

כל התרגילים בספר (פרט לפרויקט המסכם, שיקבל ריפו משלו בפרק 31) חיים בפרויקט אחד בשם `ai-course`
בתיקיית המשתמשת. מבנה היעד:

<div dir="ltr" align="left">

```text
C:\Users\<שם>\ai-course\
    pyproject.toml        הגדרות הפרויקט והתלויות
    .python-version       מצביע על 3.12
    uv.lock               גרסאות מדויקות של כל חבילה (נוצר אוטומטית)
    .venv\                הסביבה הווירטואלית (נוצרת אוטומטית, לא נכנסת ל-Git)
    .env                  המפתח שלך (לא נכנס ל-Git לעולם)
    .env.example          תבנית ללא סודות (כן נכנסת ל-Git)
    .gitignore
    README.md
    ch02\hello_model.py   התרגיל של הפרק
    tests\test_smoke.py   בדיקות עשן
```

</div>

הפקודות, מתוך הטרמינל:

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

<div dir="ltr" align="left">

```text
Python 3.12.x
```

</div>

מה כל פקודה עשתה:

| פקודה | מה היא עשתה |
| --- | --- |
| `git init` | ריפו Git ריק |
| `uv init --bare --python 3.12` | קובץ הגדרות מינימלי (`pyproject.toml`), בלי קבצי דוגמה ובלי הגדרות אריזה |
| `uv python pin 3.12` | הקובץ `.python-version`, שמצמיד את הפרויקט ל־3.12 גם כשמותקנות גרסאות חדשות יותר |
| `uv add ...` | הוספת התלויות לקובץ ההגדרות, פתרון הגרסאות לתוך `uv.lock`, יצירת `.venv` והתקנה |
| `uv add --dev ...` | אותו דבר, לחבילות שנחוצות רק לפיתוח |
| `uv run python --version` | הרצת ה־Python של הסביבה, בלי להפעיל אותה ידנית |

הסיומת `<3` בשם החבילה נועלת את ה־SDK לגרסאות 2.x: גרסה 3 הוכרזה עם שינויים שוברים, ואנחנו לא רוצות
שהקוד בספר ישתנה מתחת לרגליים.

עכשיו צרי את קובץ `.gitignore`, שאומר ל־Git אילו קבצים לא לעקוב אחריהם. אפשר ב־VS Code (הפקודה
`code .` פותחת את התיקייה), או ישירות מהטרמינל:

<div dir="ltr" align="left">

```powershell
@"
.venv/
__pycache__/
*.py[oc]
.pytest_cache/
.ruff_cache/
.env
"@ | Set-Content .gitignore
```

</div>

השורה האחרונה היא החשובה ביותר: קובץ הסודות `.env` (סעיף 2.6) לא ייכנס ל־Git לעולם. צרי גם קובץ
`README.md` עם שורה אחת שמתארת את הפרויקט.

פתחי את `pyproject.toml` והוסיפי בסופו את ההגדרה שמאפשרת לבדיקות למצוא את הקוד:

<div dir="ltr" align="left">

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

</div>

ודאי שהקובץ מכיל שורות דומות לאלה (המספרים אצלך עשויים להיות גבוהים יותר):

<div dir="ltr" align="left">

```toml
[project]
name = "ai-course"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "google-genai>=2.28,<3",
    "pydantic>=2.13",
]

[dependency-groups]
dev = [
    "pytest>=9",
    "ruff>=0.16",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

</div>

## 2.6 מפתח ה־API: Google AI Studio

מפתח API (API key) הוא מחרוזת סודית שמזהה אותך מול שרתי Google ומשייכת אלייך כל קריאה. השגתו
חינמית ואינה דורשת כרטיס אשראי:

1. היכנסי לכתובת `https://aistudio.google.com/apikey` עם חשבון Google **אישי** (לא חשבון עבודה).
2. לחצי „Create API key”. אם תתבקשי לבחור פרויקט, אשרי את ברירת המחדל; AI Studio יוצר פרויקט
   בשבילך.
3. העתיקי את המפתח. הוא יוצג פעם אחת כמחרוזת ארוכה. אל תדביקי אותו בשום מקום חוץ מהקובץ שבצעד
   הבא.
4. באותו אתר, בעמוד השימוש והמגבלות (Usage / Rate limits), תראי את המגבלות של המסלול החינמי לכל
   מודל: בקשות לדקה ובקשות ליום. רשמי לעצמך את המספרים של `gemini-3.5-flash-lite`; נזדקק להם בפרק
   11.

עכשיו ניצור את קובץ הסודות. בתיקיית `ai-course`, צרי קובץ בשם `.env` (עם הנקודה בהתחלה) ובו שלוש
שורות, כשבמקום `PASTE_YOUR_KEY_HERE` מודבק המפתח שלך:

<div dir="ltr" align="left">

```text
GEMINI_API_KEY=PASTE_YOUR_KEY_HERE
MODEL_FAST=gemini-3.5-flash-lite
MODEL_SMART=gemini-3.8-flash
```

</div>

צרי גם קובץ `.env.example` עם אותן שורות אבל בלי המפתח (השאירי `GEMINI_API_KEY=` ריק): הוא ייכנס
ל־Git ויסביר למי שמשכפל את הפרויקט אילו משתנים נדרשים. ולבסוף, ודאי ש־`.env` אכן מוחרג מ־Git:

<div dir="ltr" align="left">

```powershell
git check-ignore .env
```

</div>

<div dir="ltr" align="left">

```text
.env
```

</div>

אם הפקודה הדפיסה `.env`, הקובץ מוחרג. אם לא הדפיסה דבר, פתחי את `.gitignore` (סעיף 2.5) וודאי שיש
בו שורה שמכילה בדיוק `.env`.

> **שימי לב:** שלושה דברים על המפתח.
>
> - ה־SDK קורא את המפתח ממשתנה סביבה. השם הרגיל הוא `GEMINI_API_KEY`.
> - קיים גם שם חלופי, `GOOGLE_API_KEY`. אם שניהם מוגדרים, החלופי גובר. זה מקור לבלבול אם נשאר אצלך
>   מפתח ישן מפרויקט אחר.
> - קובץ הסודות אינו נטען מעצמו. הדגל `--env-file .env` בפקודת ההרצה טוען אותו למשתני הסביבה של
>   אותה הרצה בלבד. כך המפתח לא נשמר באופן קבוע במערכת ולא נכנס לקוד. בפרק 25 נראה את אותו מנגנון
>   בשרת, עם הסודות של GitHub Actions.

מה שמות המודלים האלה: `MODEL_FAST` הוא המודל הזול והמהיר שישמש לרוב התרגילים, ו־`MODEL_SMART`
הוא מודל חזק יותר להשוואות ולמשימות שדורשות איכות. שניהם במסלול החינמי נכון לאוקטובר 2026. Google
משחררת מודלים חדשים כל כמה חודשים, ולכן השמות חיים בקובץ ההגדרות ולא בקוד: כשיתפרסם מודל חדש,
תשני שורה אחת. העמוד `https://ai.google.dev/gemini-api/docs/models` מציג את הרשימה העדכנית.

## 2.7 הקריאה הראשונה: `hello_model.py`

צרי את התיקייה `ch02` ובתוכה קובץ ריק `__init__.py` (הוא הופך את התיקייה לחבילה שהבדיקות יודעות
לייבא) וקובץ `hello_model.py` עם התוכן הבא:

<div dir="ltr" align="left">

```python
"""Chapter 2: the first call to a language model.

Run from the course root (the folder that contains pyproject.toml):

    uv run --env-file .env python ch02/hello_model.py

Prints the model's answer, the token usage reported by the API, the latency,
and what the call would have cost on the paid tier.
"""

from __future__ import annotations

import os
import sys
import time

from google import genai

# Paid-tier list prices per 1M tokens for the default fast model (checked 2026-10-03).
# On the free tier the real cost is 0; this is for building intuition only.
DEFAULT_PRICE_INPUT = 0.30
DEFAULT_PRICE_OUTPUT = 2.50


def estimate_paid_cost(
    input_tokens: int,
    output_tokens: int,
    price_input: float = DEFAULT_PRICE_INPUT,
    price_output: float = DEFAULT_PRICE_OUTPUT,
) -> float:
    """Return the price in USD for the given token counts at the given per-1M rates."""
    return (input_tokens * price_input + output_tokens * price_output) / 1_000_000


def require_api_key() -> None:
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("No API key in the environment. Did you run with --env-file .env? See section 2.6.")


def main() -> None:
    require_api_key()
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    prompt = "הסבירי בשני משפטים, בעברית, מה עושה מודל שפה."

    client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY from the environment
    started = time.perf_counter()
    # No try/except on purpose: if the key, the model name or the rate limit is wrong,
    # the traceback's last line says exactly what happened. Chapter 11 adds real error handling.
    interaction = client.interactions.create(model=model, input=prompt)
    elapsed = time.perf_counter() - started

    usage = interaction.usage
    input_tokens = (usage.total_input_tokens if usage else None) or 0
    output_tokens = (usage.total_output_tokens if usage else None) or 0
    thought_tokens = (usage.total_thought_tokens if usage else None) or 0

    print(interaction.output_text)
    print("-" * 40)
    print(f"model:           {model}")
    print(f"input tokens:    {input_tokens}")
    print(f"output tokens:   {output_tokens}")
    print(f"thought tokens:  {thought_tokens}")
    print(f"latency:         {elapsed:.2f} s")
    print(f"paid-tier price: ${estimate_paid_cost(input_tokens, output_tokens):.6f} (free tier: $0)")


if __name__ == "__main__":
    main()
```

</div>

הריצי, מתוך תיקיית `ai-course`:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python ch02/hello_model.py
```

</div>

פלט לדוגמה (הניסוח של המודל והמספרים ישתנו אצלך):

<div dir="ltr" align="left">

```text
מודל שפה הוא תוכנה שלמדה מכמויות עצומות של טקסט לחזות את ההמשך הסביר ביותר של רצף מילים.
כשנותנים לו שאלה או הוראה, הוא מייצר תשובה מילה אחר מילה על סמך הדפוסים שלמד.
----------------------------------------
model:           gemini-3.5-flash-lite
input tokens:    21
output tokens:   58
thought tokens:  0
latency:         1.38 s
paid-tier price: $0.000151 (free tier: $0)
```

</div>

שימי לב לארבעה דברים בקוד, כי הם יחזרו בכל פרק:

1. **הלקוח (client).** האובייקט שמייצג את החיבור לשירות נוצר בשורה `client = genai.Client()`. הוא
   מוצא את המפתח במשתני הסביבה בעצמו; לעולם לא נעביר לו מפתח כמחרוזת בקוד.
2. **הקריאה.** הפונקציה `create` שולחת בקשה אחת ומחזירה אובייקט אינטראקציה (interaction). הטקסט
   שהמודל יצר נמצא בשדה `output_text`. בפרק 7 נפתח את כל השדות האחרים: רשימת הצעדים, המזהה שמאפשר
   להמשיך שיחה, ועוד.
3. **דיווח השימוש (usage).** השירות מחזיר כמה טוקנים נכנסו, כמה יצאו, וכמה שימשו ל„חשיבה” (במודל
   המהיר זה בדרך כלל אפס). טוקן הוא יחידת הטקסט שהמודל עובד איתה, בערך שלושה רבעים ממילה באנגלית
   ופחות מזה בעברית; פרק 5 מסביר. התשלום אצל כל הספקים נקבע לפי המספרים האלה, ולכן נדפיס אותם בכל
   תרגיל. שמות השדות המדויקים מופיעים בקוד למעלה.
4. **שגיאות.** בכוונה אין כאן `try`/`except`. אם המפתח שגוי, שם המודל לא קיים או שחרגת ממגבלת הקצב,
   Python יציג traceback, והשורה האחרונה שלו אומרת בדיוק מה קרה: שם מחלקת השגיאה (למשל
   `RateLimitError` כשחורגים ממגבלת הקצב, קוד 429) וההודעה מהשרת. לקרוא את השורה האחרונה של
   traceback היא המיומנות שצריך עכשיו, וטבלת התקלות בסעיף 2.11 ממפה את השורות הנפוצות. בפרק 11 נבנה
   שכבת טיפול בשגיאות אמיתית, שמחליטה מה מנסים שוב ומה לא.

> **טעות נפוצה:** להריץ `python ch02/hello_model.py` בלי `uv run`. אז רץ Python אחר במחשב (או אף
> אחד), בלי החבילות של הסביבה, ותקבלי `ModuleNotFoundError: No module named 'google'`. בקורס תמיד
> `uv run`.

## 2.8 בדיקת עשן עם pytest

נוסיף בדיקות קטנות שמוכיחות שהסביבה תקינה, בלי רשת ובלי מפתח. צרי `tests\test_smoke.py`:

<div dir="ltr" align="left">

```python
"""Smoke tests for the course workbench. No network, no API key needed."""

import sys

import pytest

from ch02.hello_model import estimate_paid_cost


def test_python_version_is_3_12() -> None:
    assert sys.version_info[:2] == (3, 12)


def test_sdk_is_installed() -> None:
    import google.genai  # noqa: F401  (import succeeding is the test)


def test_paid_cost_estimate() -> None:
    # 1M input tokens at $0.30 plus 1M output tokens at $2.50 = $2.80
    assert estimate_paid_cost(1_000_000, 1_000_000, 0.30, 2.50) == pytest.approx(2.80)
    assert estimate_paid_cost(0, 0) == 0.0
```

</div>

<div dir="ltr" align="left">

```powershell
uv run pytest -q
```

</div>

<div dir="ltr" align="left">

```text
...                                                                      [100%]
3 passed in 0.4s
```

</div>

שימי לב להפרדה: החישוב `estimate_paid_cost` הוא פונקציה טהורה שאפשר לבדוק בלי רשת; הקריאה למודל
נשארת ב־`main`. ההרגל הזה, להפריד בין לוגיקה שניתנת לבדיקה דטרמיניסטית לבין הקריאה למודל, הוא
הבסיס לפרק 18 כולו.

## 2.9 ההתחייבות הראשונה ל־Git

<div dir="ltr" align="left">

```powershell
git config --global user.name "השם שלך"
git config --global user.email "המייל האישי שלך"
git status
git add .
git commit -m "Course workbench: uv project, first model call, smoke tests"
```

</div>

לפני ההתחייבות, ודאי שפלט הפקודה `git status` **אינו** מציג את קובץ הסודות ברשימת הקבצים. אם הוא
מופיע, עצרי ותקני את קובץ ההחרגות לפי סעיף 2.5. השתמשי בזהות Git אישית: הפרויקט הזה ילווה אותך
לתיק העבודות.

## 2.10 אופציונלי: מודל מקומי עם Ollama

Ollama מריץ מודלי משקולות פתוחות (open-weights) קטנים על המחשב שלך, בלי מפתח ובלי רשת אחרי ההורדה.
נשתמש בו בפרק 11 כ„ספק שני” כדי להוכיח שהקוד שלנו לא תלוי בספק אחד. ההתקנה אופציונלית, ודורשת
לפחות 16 GB זיכרון ו־5 GB מקום פנוי:

<div dir="ltr" align="left">

```powershell
winget install --id Ollama.Ollama -e
ollama pull qwen3:4b
ollama run qwen3:4b "Say hello in Hebrew"
```

</div>

על מעבד בלי כרטיס גרפי ייעודי המודל יענה לאט (כמה מילים בשנייה), וביכולות קריאה לכלים הוא חלש
מהמודלים בענן. זה כלי ללמידה ולחיסכון, לא תחליף.

## 2.11 פתרון תקלות

| מה רואים | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| `winget : The term 'winget' is not recognized` | App Installer חסר | התקיני „App Installer” מחנות Microsoft, פתחי טרמינל חדש |
| `uv : The term 'uv' is not recognized` אחרי התקנה | ה־PATH לא נטען | סגרי את כל חלונות הטרמינל ופתחי חדש |
| `No API key in the environment` | `.env` לא נטען או חסר | הריצי עם `--env-file .env` מתוך התיקייה שבה הקובץ נמצא; בדקי `pwd` |
| traceback שמסתיים ב־`API key not valid` | מפתח שגוי, או `GOOGLE_API_KEY` ישן ממקום אחר שגובר | בדקי את `.env`; הריצי `Get-ChildItem Env:GOOGLE_API_KEY` ואם קיים, הסירי אותו |
| traceback שמסתיים ב־`NotFoundError` או `... not found` | שם מודל שגוי או לא זמין | בדקי את השם מול עמוד המודלים; עדכני `.env` |
| traceback שמסתיים ב־`RateLimitError` או `RESOURCE_EXHAUSTED` | מגבלת הקצב של המסלול החינמי | חכי דקה ונסי שוב; בפרק 11 נטפל בזה בקוד |
| `UnicodeEncodeError` או סימני שאלה במקום עברית | `PYTHONUTF8` לא מוגדר או הטרמינל לא נפתח מחדש | סעיף 2.2; פתחי טרמינל חדש |
| `ModuleNotFoundError: No module named 'google'` | הרצה בלי `uv run` | תמיד `uv run python ...` |
| `error: No interpreter found for Python 3.12` | Python לא הותקן דרך uv | `uv python install 3.12` |
| שגיאת SSL או `certificate verify failed` | רשת ארגונית עם proxy | נסי מרשת ביתית; אל תבטלי אימות תעודות |
| `running scripts is disabled on this system` | מדיניות הרצת סקריפטים | לא נדרש בקורס (אנחנו לא מפעילות `.venv` ידנית); אם נדרש: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

## 2.12 עצירה, הפעלה מחדש וניקוי

- **לעצור תוכנית שרצה:** המקשים `Ctrl+C`.
- **לבנות מחדש את הסביבה** אם משהו השתבש: מוחקים את תיקיית הסביבה ומסנכרנים מחדש. קובץ הנעילה
  מבטיח שתקבלי בדיוק את אותן גרסאות.
- **להסיר הכול:** מנקים את המטמון של uv, מוחקים את התיקייה שבה הוא שומר גרסאות Python (הפקודה
  `uv python dir` מדפיסה את מיקומה), מסירים את uv, ומוחקים את תיקיית הפרויקט.
- **לבטל מפתח שדלף:** ב־AI Studio, בעמוד המפתחות, מחקי את המפתח וצרי חדש. מחיקת השורה מהקובץ
  אינה מבטלת מפתח שכבר נחשף.

הפקודות המתאימות:

<div dir="ltr" align="left">

```powershell
# rebuild the environment
Remove-Item -Recurse -Force .venv
uv sync

# remove everything
uv cache clean
uv python dir          # prints the folder that holds uv's Python versions; delete it if you want
winget uninstall astral-sh.uv
Remove-Item -Recurse -Force "$HOME\ai-course"
```

</div>

## סיכום

- הסביבה: טרמינל חדש, מנהל התקנות, Git, עורך, ו־uv שמנהל גם את Python עצמו.
- עברית: משתנה סביבה אחד ברמת המשתמשת, ואז טרמינל חדש.
- פרויקט אחד לכל הקורס: קובץ הגדרות, קובץ נעילה, קובץ סודות שמוחרג מ־Git, וקובץ דוגמה בלי סודות
  שכן נכנס.
- המפתח חינמי, נשמר בקובץ הסודות, נטען בזמן ההרצה בלבד, ולעולם לא מופיע בקוד.
- הקריאה הראשונה: יוצרים לקוח, שולחים בקשה אחת, קוראים את טקסט התשובה ואת דיווח הטוקנים.
- שמות המודלים חיים בהגדרות, לא בקוד.

## מונחים לזכור

| מונח בעברית | באנגלית | במשפט אחד |
| --- | --- | --- |
| סביבה וירטואלית | Virtual environment | תיקיית `.venv` עם Python והחבילות של פרויקט אחד |
| קובץ נעילה | Lockfile (`uv.lock`) | הגרסאות המדויקות שהותקנו, לשחזור זהה במחשב אחר |
| משתנה סביבה | Environment variable | ערך בשם שהמערכת מעבירה לתוכניות; כך נמסרים סודות והגדרות |
| מפתח API | API key | מחרוזת סודית שמזהה אותך מול הספק; סיסמה לכל דבר |
| ערכת פיתוח | SDK | ספריית Python שעוטפת את פרוטוקול ה־API באובייקטים ופונקציות |
| אינטראקציה | Interaction | אובייקט התשובה של קריאה אחת: טקסט, צעדים, מזהה ושימוש |
| דיווח שימוש | Usage | ספירת הטוקנים שנכנסו, יצאו ושימשו לחשיבה בקריאה אחת |
| מגבלת קצב | Rate limit | מספר הבקשות המותר לדקה או ליום; שגיאת 429 כשחורגים |

## טעויות נפוצות

- **להתקין Python מ־python.org „ליתר ביטחון”.** זה יוצר שני Python במחשב ובלבול לגבי מי רץ. uv
  מספיק.
- **להדביק את המפתח בקוד „רק לבדיקה”.** בקוד הוא נכנס ל־Git ולהיסטוריה לנצח. רק `.env`.
- **להפעיל את הסביבה ידנית** (`.venv\Scripts\Activate.ps1`) ואז לשכוח. `uv run` עושה זאת בכל פקודה.
- **לקרוא ל־`output_text` ולהתעלם מ־`usage`.** בלי המספרים האלה אין לך מושג כמה המערכת שלך תעלה
  בייצור.
- **לנסות שוב מיד אחרי 429.** זה רק מאריך את החסימה. ממתינים, ובפרק 11 עושים זאת נכון.

## שאלות ראיון

1. **איך את מנהלת סודות בפיתוח מקומי ובשרת?** מקומית: קובץ `.env` מוחרג מ־Git, נטען לסביבת
   ההרצה בלבד; בשרת: מנגנון הסודות של הפלטפורמה (למשל GitHub Actions secrets), אף פעם בקוד או
   בתמונה. מפתח שדלף מבטלים, לא מוחקים.
2. **למה קובץ נעילה חשוב בפרויקט AI במיוחד?** כי ספריות ה־SDK משתנות מהר ושינוי גרסה יכול לשנות
   התנהגות; הנעילה מאפשרת לשחזר בדיוק את הסביבה שבה מדדת תוצאות.
3. **כמה עולה קריאה למודל, ואיך את יודעת?** לפי דיווח ה־usage של הספק (טוקני קלט, פלט וחשיבה)
   כפול המחירון של המודל; מדפיסים ומתעדים אותו בכל קריאה, לא מעריכים מראש.

## פתק Obsidian

הפתק המוכן נמצא גם כקובץ: `obsidian/02-workbench-windows.md`. הוא בנוי משני חלקים: מושגים בעברית,
ואחריהם דף־עזר (cheat sheet) באנגלית בלבד, בכוונה, כדי שפקודות ושמות לא יתערבבו בטקסט עברי.

- **מה הקמתי:** טרמינל חדש, Git, עורך, ומנהל חבילות אחד שמנהל גם את Python עצמו.
- **איך מריצים:** תמיד דרך uv, מתוך תיקיית הפרויקט, עם קובץ הסודות.
- **עברית בטרמינל:** משתנה סביבה אחד ברמת המשתמשת, ואז לפתוח טרמינל חדש.
- **סודות:** קובץ הסודות לא נכנס ל־Git. קובץ הדוגמה בלי המפתח כן נכנס.
- **הקריאה הראשונה:** יוצרים לקוח, שולחים בקשה אחת, קוראים טקסט ושימוש בטוקנים.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
tools    PowerShell 7 | winget | Git | VS Code | uv | Python 3.12 (managed by uv)
run      uv run --env-file .env python <file>          (from the ai-course folder)
hebrew   PYTHONUTF8=1 as a User environment variable -> open a new terminal
secrets  .env is git-ignored | .env.example is committed | git check-ignore .env prints ".env"
call     genai.Client() -> client.interactions.create(model=..., input=...) -> output_text, usage
models   MODEL_FAST=__________   MODEL_SMART=__________
limits   free tier: ____ requests/min, ____ requests/day   (from AI Studio)
```

</div>

## תרגיל

**מטרה:** סביבה עובדת וקריאה ראשונה למודל, עם בדיקות עשן וקובץ סודות מוגן.
**זמן:** 90–120 דקות. **ידע מקדים:** הפרק כולו.

הצעדים המלאים, קוד ההתחלה, רשימת הבדיקה, הרמזים והפתרון נמצאים ב־
[`exercises/ch02-first-call/README.md`](../exercises/ch02-first-call/README.md).

**קריטריון סיום:**

- הרצת התוכנית מדפיסה תשובה בעברית קריאה ושלושה מספרי טוקנים.
- הרצת הבדיקות מדווחת על שלוש בדיקות שעברו.
- הקובץ `.env` מוחרג מ־Git, וההתחייבות הראשונה קיימת ביומן של Git.

## העשרה אופציונלית

- תיעוד uv: הפרק „Projects” מסביר לעומק את קובץ ההגדרות, קובץ הנעילה ופקודת ההרצה.
- תיעוד Gemini API: עמוד ה־Quickstart ועמוד ה־Pricing. השוואת המחירים בין המודלים שם היא תרגיל
  מצוין בקריאת מחירון.

</div>
