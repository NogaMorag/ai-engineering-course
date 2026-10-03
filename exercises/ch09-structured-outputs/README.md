---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 9: `ArticleSummary`, פלט מובנה עם אימות ותיקון

**מטרה:** להגדיר את הצורה של פריט אחד בעיתון הבוקר כמודל Pydantic, לקבל אותה מהמודל דרך סכמה,
לאמת כללים שהסכמה לא מבטאת, לתקן פעם אחת, ולוותר בקול. הכול מוכח בבדיקות בלי רשת.

**זמן משוער:** יום לימוד אחד (יום 14), כ־60 דקות בנייה. **ידע מקדים:** פרק 9, חבילת `ch08` מהתרגיל
הקודם (הכתבות), ומפתח API. ההרצה המלאה מבצעת שלוש עד שש קריאות.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/schemas.py` | המודל והסכמה, עם שני `TODO`: המאמת וניקוי הסכמה |
| `starter/summarize_structured.py` | הקריאה למודל, עם `TODO` אחד: לולאת אימות ותיקון |
| `solution/schemas.py`, `solution/summarize_structured.py` | הפתרון המלא |
| `tests/test_ch09.py` | שמונה בדיקות, בלי רשת |

## הצעדים

**1. חבילה חדשה.** בתיקיית `ai-course`:

<div dir="ltr" align="left">

```powershell
New-Item -ItemType Directory ch09 | Out-Null
New-Item -ItemType File ch09\__init__.py | Out-Null
Copy-Item path\to\exercises\ch09-structured-outputs\starter\*.py ch09\
Copy-Item path\to\exercises\ch09-structured-outputs\tests\test_ch09.py tests\
```

</div>

הקוד קורא את הכתבות מ־`ch08\data\articles`, אז התרגיל של פרק 8 חייב להיות במקום.

**2. קראי את `schemas.py` לפני שאת ממלאת.** שימי לב לשלושה דברים: כל שדה עם `description` שהוא
כלל; `Literal` לרשימה הסגורה; ו־`RESPONSE_FORMAT` שנבנה מהסכמה שהמחלקה מפיקה.

**3. מלאי את `TODO 1`** (המאמת). כשזו כתבה: בדיוק שלוש נקודות, כותרת לא ריקה של עד 12 מילים,
ו־`why_it_matters` שמתחיל במילים `Why it matters:`. כשזו לא כתבה: כותרת, נקודות ו־`why_it_matters`
ריקים. כל הפרה היא `ValueError` עם משפט ברור, כי המשפט הזה ייסע חזרה למודל בניסיון התיקון.

**4. מלאי את `TODO 2`** (`clean_schema`). פונקציה רקורסיבית: מילון נבנה מחדש בלי המפתח `title`,
רשימה איבר אחרי איבר, וכל דבר אחר חוזר כמו שהוא. בדקי בעצמך מה הסכמה מכילה לפני ואחרי:

<div dir="ltr" align="left">

```powershell
uv run python -c "import json; from ch09.schemas import ArticleSummary, clean_schema; print(json.dumps(clean_schema(ArticleSummary.model_json_schema()), indent=1))"
```

</div>

**5. מלאי את ה־`TODO` ב־`summarize`.** ההנחיה נבנית פעם אחת; בכל ניסיון קוראים ל־`backend.complete`,
בודקים קודם את הסטטוס (`incomplete` זורק `OutputTruncated` ולא מנסה שוב), ואז `model_validate_json`.
`ValidationError` שומרת את השגיאה ומחליפה את ההנחיה בהנחיית תיקון. אחרי הלולאה זורקים
`SummaryError` עם השגיאה האחרונה.

**6. בדיקות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch09.py -q
uv run ruff check ch09
```

</div>

**7. הרצה חיה.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch09.summarize_structured
```

</div>

**8. רשמי בפתק:** האם המאמת תפס משהו בפועל (הקוד מדפיס `FAILED` אם גם התיקון נכשל; הוסיפי הדפסה
זמנית ב־`except` כדי לראות תיקון שהצליח), ומה ההבדל בין הפלט כאן לבין v3 מפרק 8 על אותה כתבה.

**9. התחייבות.** `git add .` ואז `git commit -m "Chapter 9: structured output with validation"`.
התיקייה `out` יכולה להיכנס ל־`.gitignore` או להישאר; היא קטנה.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
=== 01-rust-build-tool ===
{
  "is_article": true,
  "headline": "Cargo-Lite 2.0 ships a shared build cache",
  "bullets": [
    "...",
    "...",
    "..."
  ],
  "why_it_matters": "Why it matters: ...",
  "tags": ["rust", "build tools"],
  "confidence": "high"
}

=== 03-not-an-article ===
{
  "is_article": false,
  "headline": "",
  "bullets": [],
  "why_it_matters": "",
  "tags": [],
  "confidence": "low"
}
```

</div>

הטקסטים ישתנו בין הרצות; הצורה לא.

## רשימת בדיקה

- [ ] `clean_schema` מסיר כל `title` ומשאיר כל `description`.
- [ ] המאמת זורק על שתי נקודות, על ארבע, על כותרת של 13 מילים, ועל `why_it_matters` בלי התחילית.
- [ ] `summarize` מנסה לכל היותר פעמיים, ולא מנסה שוב אחרי `incomplete`.
- [ ] שלושת הקבצים ב־`ch09\out` תקינים, ודף השגיאה סומן `is_article: false`.
- [ ] שמונה הבדיקות ו־ruff עוברים.

## רמזים

- המאמת רץ אחרי שהשדות כבר נבדקו לפי הטיפוסים (`mode="after"`), אז אפשר לסמוך על כך
  ש־`self.bullets` הוא רשימה של מחרוזות.
- `isinstance(schema, dict)` ואז דיקט־קומפריהנשן עם תנאי על המפתח; `isinstance(schema, list)` ואז
  ליסט־קומפריהנשן. שני מקרים ושורת `return` אחת לכל השאר.
- בבדיקות, `FakeBackend` מחזיר תסריט של זוגות `(text, status)`. אם את תוהה מה בדיוק צריך לקרות
  בכל מקרה, קראי את הבדיקה המתאימה: היא המפרט.

## הפתרון

`solution/` מכיל את שני הקבצים המלאים. קראי אותם רק אחרי שהבדיקות שלך עוברות, או אחרי עשרים דקות
של תקיעות. שימי לב בפתרון לשתי מחלקות שגיאה (`SummaryError` ו־`OutputTruncated` שיורשת ממנה):
הקוד הקורא יכול לתפוס את הכללית, ולטפל בקיטוע לחוד אם ירצה.

## מה התרגיל מדגים

- מקור אמת אחד לצורה: מודל Pydantic שמפיק סכמה ומאמת תשובה.
- ההבדל בין מה שהסכמה אוכפת לבין מה שהקוד אוכף.
- מדיניות תיקון מוגבלת ומפורשת, במקום לולאה או אובייקט חלקי.
- בדיקות של לוגיקת מודל שפה בלי מודל שפה: הפרדה בין „מה שולחים ומה עושים עם מה שחוזר” לבין
  „לקרוא לרשת”.

</div>
