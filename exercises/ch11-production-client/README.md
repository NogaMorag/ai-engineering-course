---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 11: `llm_client.py`, ונקודת ביקורת 2: מסכם הכתבות

**מטרה:** לבנות את השכבה שכל שאר הקורס והפרויקט ידברו דרכה: היררכיית שגיאות משלנו, ניסיונות חוזרים
שנבדקים בלי להמתין, זמן קצוב, הזרמה, ו־`LLMClient` עם מימוש אמיתי ולקוח מזויף. ואז לסגור את חלק
ג בכלי שורת פקודה שמסכם כל כתובת.

**זמן משוער:** שלושה ימי לימוד. ימים 17 ו־18: כ־60 דקות בנייה בכל אחד. יום 19 (נקודת הביקורת):
כ־120 דקות. **ידע מקדים:** פרקים 9 עד 11, מפתח API, וחיבור לרשת.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/llm_client.py` | הלקוח, עם שלושה `TODO`: `classify`, `with_retries`, ו־`operation` בתוך `complete` |
| `solution/llm_client.py` | הפתרון המלא, כולל הדגמה |
| `solution/summarize_url.py` | נקודת ביקורת 2: הכלי המלא (אין גרסת התחלה; בונים אותו לפי הצעדים) |
| `tests/test_ch11.py` | תשע בדיקות, בלי רשת |

## יום 17: שגיאות, ניסיונות, זמן קצוב

**1. חבילה ושלד.** כל הפקודות רצות מתוך תיקיית `ai-course`.

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch11\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch11-production-client\starter\llm_client.py ch11\
Copy-Item path\to\exercises\ch11-production-client\tests\test_ch11.py tests\
```

</div>

קובץ הבדיקות מייבא את `ch11.summarize_url` רק בתוך ארבע בדיקות ה־CLI, ולכן ביומיים הראשונים pytest
אוסף ומריץ את בדיקות הלקוח גם בלי הקובץ; בדיקות ה־CLI אדומות עד יום 19, וזה צפוי (הפקודות בצעדים
3 ו־8 מסננות אותן). כדאי בכל זאת ליצור כבר עכשיו את הקובץ `ch11\summarize_url.py` עם השלד הזה: הוא
המפרט של יום 19, אלה השמות שהבדיקות מצפות להם.

<div dir="ltr" align="left">

```python
"""Checkpoint 2: summarize a web page from the command line. Filled in on day 19."""

EXIT_OK, EXIT_NOT_ARTICLE, EXIT_LLM_FAILURE, EXIT_FETCH_FAILURE = 0, 2, 3, 4


def render_markdown(summary, source: str) -> str:
    raise NotImplementedError


def main(argv: list[str] | None = None, client=None) -> int:
    raise NotImplementedError
```

</div>

**2. קראי את הקובץ מלמעלה למטה** לפני שאת ממלאת: היררכיית השגיאות עם `retryable`; `Completion`;
`RetryPolicy.delay` (כבר ממומש: full jitter עם תקרה); ה־`Protocol`; `GeminiClient.__init__` שמכבה
את הניסיונות של הספרייה; `stream`; ו־`FakeClient`.

**3. מלאי את `TODO 1`** (`classify`). לפי `status_code`: 429, 500 ומעלה, שאר ה־4xx; ואז זמן קצוב
או ניתוק לפי המחלקה או השם; והכול השאר `LLMError`. העבירי `status_code=` ו־`cause=`.

**4. מלאי את `TODO 2`** (`with_retries`). לולאה על הניסיונות; חריגה שאינה `retryable`, או הניסיון
האחרון, נזרקת כמו שהיא; אחרת מחשבים המתנה, בודקים את גבול הזמן הכולל (ואם חורגים זורקים
`LLMUnavailable` עם המילה deadline), קוראים ל־`on_retry` אם יש, וישנים. בהצלחה מעדכנים את
`attempts`.

**5. בדיקות של החלק הזה.** הן רצות באלפיות שנייה כי השינה והשעון מוזרקים.

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch11.py -q -k "classify or retry or policy"
```

</div>

## יום 18: הלקוח המלא והמזויף

**6. מלאי את `TODO 3`** (`operation` בתוך `complete`):

- בונים את הארגומנטים לקריאה: קלט, הגדרות יצירה, ואם ניתנו, הוראות מערכת וסכמת פלט.
- קוראים דרך `self._create`; שם קורית ההמרה לשגיאות שלנו.
- בונים `Completion` מהתשובה; שדות השימוש יכולים להיות `None`.
- על סטטוס `incomplete` זורקים `LLMTruncated`; אחרת מחזירים את התוצאה.

**7. כל הבדיקות של הלקוח, ואז ההדגמה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch11.py -q -k "not cli and not render"
uv run --env-file .env python -m ch11.llm_client
```

</div>

ההדגמה מראה ארבעה דברים בזה אחר זה: קריאה רגילה עם מספר ניסיונות וזמן; הזרמה עם זמן לטוקן
ראשון; שגיאת 404 על שם מודל לא קיים, שמסווגת `LLMBadRequest` ולא מנוסה שוב; וקיטוע שמדווח
כ־`LLMTruncated`.

**8. חשבי ורשמי בפתק** את הזמן המרבי לקריאה אחת עם ההגדרות שלך, פעמיים: בלי גבול זמן כולל (זמן
קצוב כפול מספר ניסיונות, ועוד סכום תקרות ההמתנה), ועם הגבול של 90 שניות (סעיף 11.4 מראה את
החישוב). האם זה מתאים לכלי שורת פקודה? מה היית משנה לצינור לילי?

## יום 19: נקודת ביקורת 2

**9. השלימי את `ch11\summarize_url.py`** (השלד מצעד 1) לפי המפרט. הפתרון נמצא ב־`solution/` אם
נתקעת, אבל נסי קודם:

| דרישה | פירוט |
| --- | --- |
| קלט | כתובת, או `--file path.txt`; דגל `--json` |
| הורדה | `fetch_url` מפרק 10; דף בלי טקסט הוא כישלון הורדה |
| סיכום | `summarize_text(client, article)`: אותה לולאת אימות ותיקון מפרק 9, מעל `LLMClient.complete` עם `response_format` |
| שימוש חוזר | ההנחיה, הנחיית התיקון והוראות המערכת מיובאות מ־`ch09.summarize_structured`; הסכמה והמודל מ־`ch09.schemas` |
| פלט | Markdown: כותרת, שלוש נקודות, Why it matters, שורת מקור; או JSON. `render_markdown` היא פונקציה טהורה |
| קודי יציאה | 0 הצלחה; 2 לא כתבה; 3 כישלון מודל; 4 כישלון הורדה |
| בדיקות | `main(argv, client=...)` מחזיר את קוד היציאה כמספר; הבדיקות מזריקות לקוח מזויף ולא נוגעות ברשת |

**10. בדיקות ושלוש הרצות חיות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch11.py -q
uv run --env-file .env python -m ch11.summarize_url https://example.com/some-article
uv run --env-file .env python -m ch11.summarize_url --file ch08\data\articles\01-rust-build-tool.txt --json
```

</div>

בחרי שלוש כתבות אמיתיות באנגלית מאתרי חדשות טכנולוגיים. שמרי את הפלט בפתק, עם הטוקנים והניסיונות
של כל אחת (הם מודפסים ל־stderr בעת ניסיון חוזר; הוסיפי הדפסה של `Completion` אם את רוצה אותם תמיד).

**11. קטע README.** הוסיפי ל־`README.md` של `ai-course` פסקה של חמש שורות: מה הכלי עושה, איך
מריצים, מה קודי היציאה.

**12. התחייבות.**

<div dir="ltr" align="left">

```powershell
git add .
git commit -m "Chapter 11: production client and summarize_url checkpoint"
```

</div>

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
### Cargo-Lite 2.0 ships a shared build cache

- Version 2.0 was released on Tuesday.
- Builds at one company dropped from 41 to 6 minutes.
- The old configuration format is removed in 3.0.

Why it matters: faster builds for Rust teams with large workspaces.

_Source: https://example.com/... · tags: rust, build tools · confidence: high_
```

</div>

ועל דף שאינו כתבה:

<div dir="ltr" align="left">

```text
_https://example.com/ does not look like an article (confidence: low)._
```

</div>

עם קוד יציאה 2 (בדקי עם `$LASTEXITCODE` ב־PowerShell).

## רשימת בדיקה

- [ ] `classify` ממפה 429, 503, 400, 404 ו־`TimeoutError` למחלקות הנכונות, עם `retryable` נכון.
- [ ] `with_retries` לא ישן אחרי `LLMBadRequest`; ישן פעמיים לפני הצלחה שלישית; נעצר בגבול הניסיונות
  ובגבול הזמן.
- [ ] ההדגמה מראה את ארבעת המקרים.
- [ ] `summarize_url.py` לא מייבא `google.genai`; רק `ch11.llm_client`.
- [ ] שלוש כתובות חיות עובדות; הבדיקות עוברות גם בלי מפתח (ההוכחה בפקודות שמתחת לרשימה).
- [ ] תשע הבדיקות ו־ruff עוברים.

כדי להוכיח שהבדיקות לא צריכות מפתח, מסירים אותו מהחלון הנוכחי ומריצים אותן שוב:

<div dir="ltr" align="left">

```powershell
Remove-Item Env:GEMINI_API_KEY -ErrorAction SilentlyContinue
uv run pytest -q
```

</div>

## טעויות נפוצות ותיקונים

- **להריץ את כל הקובץ ביום 17 ולהיבהל מארבע בדיקות אדומות.** בדיקות ה־CLI נכשלות עד שתכתבי את
  `summarize_url.py` ביום 19. עד אז מריצים עם המסנן מצעד 8, ובודקים שבדיקות הלקוח ירוקות.
- **להשוות `status_code` שהוא `None` למספר.** בדיקת הסיווג נופלת על `TypeError` במקרה של
  `TimeoutError`, שאין לו קוד. בודקים קודם שהערך הוא מספר שלם, ורק אז משווים לטווחים.
- **לחשב המתנה לפני בדיקת `retryable` והניסיון האחרון.** הבדיקה סופרת שתי שינות ומוצאת שלוש, או
  מוצאת שינה אחרי `LLMBadRequest`. קודם מחליטים אם בכלל מנסים שוב, ורק אז מחשבים וישנים.
- **לבדוק את גבול הזמן אחרי השינה, או בלי ההמתנה המתוכננת.** בדיקת גבול הזמן מצפה ל־`LLMUnavailable`
  עם המילה deadline בהודעה, ולא לניסיון נוסף. הבדיקה היא: הזמן שחלף ועוד ההמתנה הבאה, לפני שישנים.
- **לחשוב ששורת הניסיון החוזר היא באג.** שורה כמו `[llm] attempt 1 failed (LLMRateLimited)` ב־stderr
  היא ההתנהגות הרצויה במסלול החינמי. בודקים שהקריאה הסתיימה בהצלחה ושמספר הניסיונות נרשם.
- **לייבא `google.genai` בתוך הכלי.** הכלי עובד, אבל רשימת הבדיקה נכשלת וההחלפה לספק אחר כבר
  לא עוברת בקובץ אחד. הכלי מייבא רק את `ch11.llm_client` ואת החבילות של פרקים 9 ו־10.
- **לשכוח את הדגל `--env-file .env`.** ההדגמה וההרצות החיות נופלות על שגיאת אימות; הבדיקות לא
  צריכות אותו. מוסיפים את הדגל לכל פקודה שמדברת עם המודל.

## רמזים

- `isinstance(exc, TimeoutError | ConnectionError)` עובד בפייתון 3.10 ומעלה. לחריגות של `httpx` יש
  שמות משלהן (למשל `ReadTimeout`), ולכן יש גם בדיקת שם.
- בבדיקת גבול הזמן, השעון המזויף מחזיר 0 ואז 100: הקריאה השנייה כבר אחרי 90 השניות, אז הניסיון
  השני לעולם לא קורה.
- ב־`main`, ההזרקה של `client` היא פרמטר עם ברירת מחדל `None`; רק אם הוא `None` יוצרים `GeminiClient`.
  כך הבדיקות לא יוצרות לקוח אמיתי, ולא צריכות מפתח.
- `render_markdown` הוא פונקציה טהורה; כתבי אותה ראשונה ובדקי אותה בלי מודל.

## הפתרון

`solution/llm_client.py` ו־`solution/summarize_url.py`. **למה הוא עובד כך:** `with_retries` היא
פונקציה טהורה שמקבלת את השינה, את השעון ואת האקראיות כפרמטרים, ולכן אותו קוד בדיוק רץ בייצור עם
זמן אמיתי ובבדיקות עם זמן מזויף, בלי הסתעפות „אם זו בדיקה”. ההמרה לשגיאות שלנו קורית במקום אחד,
`_create`, כך שכל שאר הקוד תופס רק את ההיררכיה שלנו. קיטוע נזרק כ־`LLMTruncated` מתוך הלקוח, ולכן
`summarize_text` בכלי לא בודק סטטוס בעצמו: כל כשל של המודל מגיע אליו כחריגה אחת וקוד יציאה 3.

שימי לב גם: `stream` לא עובר דרך `with_retries`, ויש בקוד הערה שמסבירה למה. ו־`main` של הכלי מחזיר
מספר במקום לקרוא ל־`sys.exit`, כדי שהבדיקות יוכלו לבדוק את קוד היציאה.

## מה התרגיל מדגים

- שכבת ספק אחת עם היררכיית שגיאות משלה, במקום `try/except` של ספרייה בכל קובץ.
- ניסיונות חוזרים כקוד טהור ונבדק: זמן ואקראיות מוזרקים, הבדיקות רצות מיידית.
- „רכיב אחד הוא הבעלים של הניסיונות”: הספרייה כבויה במפורש.
- כלי שורת פקודה שמחבר ארבעה פרקים, עם קודי יציאה שקוד אחר יכול לסמוך עליהם, ובדיקות שלא
  נוגעות ברשת.

</div>
