---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 15 ונקודת ביקורת 3: `ask_notes`

**מטרה:** לבנות RAG מקצה לקצה על פתקי הקורס שלך: אינדוקס אינקרמנטלי, אחזור צפוף והיברידי, תשובה
מעוגנת עם ציטוטים ואימות, הימנעות, השוואה להקשר ארוך עם בדיקת מטמון, ודיבוג של שלוש תקלות
מוזרקות מתוך המעקב בלבד.

**זמן משוער:** ארבעה ימי לימוד (ימים 27 עד 30), כ־60 עד 70 דקות בנייה בכל אחד. **ידע מקדים:** פרק
15, התרגילים של פרקים 12 עד 14, ומפתח API. האינדוקס של הפתקים משכן כמה עשרות קטעים פעם אחת;
כל שאלה היא שיכון אחד וקריאת מודל אחת.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/ch15/loaders.py` | טעינת Markdown, הסרת כותרת עליונה, גיבוב תוכן; מוכן |
| `starter/ch15/chunking.py` | שתי אסטרטגיות חלוקה, עם `TODO 1`: מזהה הקטע |
| `starter/ch15/index.py` | `NotesIndex` עם `TODO 2`: הסנכרון האינקרמנטלי |
| `starter/ch15/retrieve.py` | `Retriever` צפוף או היברידי; מוכן |
| `starter/ch15/answer.py` | הקשר בתקציב, סכמה, עם `TODO 3`: אימות הציטוטים וההימנעות |
| `starter/ch15/cli.py` | הכלי, המעקב והזרקת התקלות; מוכן |
| `starter/ch15/compare_long_context.py` | הקשר ארוך מול RAG ובדיקת מטמון; מוכן |
| `data/sample-notes/` | שלושה פתקים קטנים לבדיקות |
| `solution/ch15/` | הפתרון המלא |
| `tests/test_ch15.py` | שמונה בדיקות, בלי רשת |

## יום 27: טעינה וחלוקה

**1. חבילה ונתונים.** החבילה כאן היא תיקייה שלמה:

<div dir="ltr" align="left">

```powershell
Copy-Item -Recurse path\to\exercises\ch15-rag\starter\ch15 ch15
New-Item -ItemType Directory ch15\data | Out-Null
Copy-Item -Recurse path\to\exercises\ch15-rag\data\sample-notes ch15\data\sample-notes
Copy-Item path\to\exercises\ch15-rag\tests\test_ch15.py tests\
```

</div>

**2. הפתקים שלך.** הקורפוס האמיתי הוא תיקיית `obsidian` של הספר (או הכספת שלך, אם העתקת אליה את
הפתקים). רשמי את הנתיב; הוא יועבר ב־`--notes-dir`.

**3. מלאי את `TODO 1`** (`make_chunk_id`) והריצי את שתי החלוקות על הפתקים שלך בשורת פקודה
(או בסקריפט קצר): `chunk_fixed` ו־`chunk_by_heading` על כל מסמך, ספירת הקטעים, והדפסה של חמישה
קטעים מכל אחת. **בפתק:** איזו חלוקה שמרה טוב יותר על המשמעות, ולמה.

**4. בדיקות החלוקה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch15.py -q -k "loader or chunks"
```

</div>

## יום 28: אינדוקס, אחזור, תשובה

**5. מלאי את `TODO 2`** (`NotesIndex.sync`). ארבעת המצבים מהטבלה בסעיף 15.4, ושמירת המניפסט בסוף.

**6. מלאי את `TODO 3`** (אימות הציטוטים ב־`answer_question`). ציטוט חוקי הוא מספר בטווח של הקטעים
שנכנסו; תשובה מעוגנת דורשת `supported`, לפחות ציטוט חוקי אחד, וטקסט לא ריק; אחרת הימנעות.

**7. כל הבדיקות, ואז חמש שאלות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch15.py -q
uv run --env-file .env python -m ch15.cli "מה עושה הטמפרטורה?" --notes-dir path\to\obsidian --trace
uv run --env-file .env python -m ch15.cli "what does a tool dispatcher check?" --notes-dir path\to\obsidian --hybrid --trace
uv run --env-file .env python -m ch15.cli "מי ניצח במונדיאל 1998?" --notes-dir path\to\obsidian --trace
```

</div>

שלוש שאלות שיש להן תשובה בפתקים, שתיים שאין. **בפתק:** התשובות, הציטוטים, ואיך נראית הימנעות.
ההרצה השנייה של אותה פקודה חייבת לדווח במעקב `embedded: 0`.

## יום 29: היברידי, הקשר ארוך, מטמון

**8. היברידי.** הריצי שאלה עם מזהה (למשל `E0502` או שם כלי) עם ובלי `--hybrid`, והשוו את
`retrieved` במעקב.

**9. הקשר ארוך מול RAG.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch15.compare_long_context --notes-dir path\to\obsidian
```

</div>

**בפתק:** הטבלה, היחס בטוקני הקלט, ומה `cached_tokens` הראה בקריאה השנייה של בדיקת המטמון. אם
אפס: הקידומת קצרה מהמינימום של המודל; רשמי כמה טוקנים היו, וזה גם ממצא.

## יום 30: דיבוג לפי שלבים, ונקודת ביקורת 3

**10. שלוש תקלות.** לכל אחת, הריצי עם `--trace` ואתרי את השלב **מהמעקב בלבד**, לפני שאת קוראת
את הקוד של התקלה:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch15.cli "<question>" --notes-dir path\to\obsidian --fault drop-doc --trace
uv run --env-file .env python -m ch15.cli "<question>" --notes-dir path\to\obsidian --fault break-chunking --trace
uv run --env-file .env python -m ch15.cli "<question>" --notes-dir path\to\obsidian --fault ignore-context --trace
```

</div>

**בפתק:** לכל תקלה, השורה במעקב שהסגירה אותה, ושם השלב.

**11. מוכן למאגר.** README קצר בתיקיית הפרויקט (מה הכלי עושה, איך מריצים, קודי יציאה: 0 תשובה,
2 הימנעות), והבדיקות עוברות בלי מפתח.

**12. התחייבות.** `git commit -m "Chapter 15: ask_notes RAG with citations, traces and fault injection"`.
הוסיפי `ch15/index/` ל־`.gitignore`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
הטמפרטורה מחלקת את הלוגיטים לפני הסופטמקס; טמפרטורה נמוכה מחדדת את ההתפלגות וגבוהה משטחת אותה [1].
טמפרטורה אפס אינה „מצב אמת”: תשובה שגויה הופכת לשגויה באופן עקבי [1][2].

[1] 06-generation-and-its-knobs.md › יצירת טקסט והכפתורים שלה
[2] 05-inside-a-language-model.md › בתוך מודל שפה
```

</div>

ובשגיאה הסטנדרטית, עם `--trace`, JSON עם `documents`, `indexed_chunks`, `sync`, `retrieved`,
`context_chars`, `prompt_variant`, `citations`, `invalid_citations`, `cached_tokens` ועוד.

## רשימת בדיקה

- [ ] אותו קטע מקבל אותו מזהה בכל הרצה; עריכה משנה אותו.
- [ ] `sync` שני ברצף: אפס שיכונים; עריכת פתק אחד: `updated: 1` והקטעים הישנים נעלמו.
- [ ] ציטוט מחוץ לטווח מוסר ונרשם; תשובה בלי ציטוט חוקי הופכת להימנעות.
- [ ] שלוש שאלות עם תשובה ושתיים בלי מתנהגות נכון; `--hybrid` משנה את האחזור על מזהה.
- [ ] טבלת הקשר ארוך מול RAG ובדיקת המטמון בפתק.
- [ ] שלוש התקלות אותרו מהמעקב, עם השורה המסגירה.
- [ ] שמונה הבדיקות ו־ruff עוברים; README קצר קיים.

## רמזים

- במניפסט, המפתח הוא הנתיב היחסי של המסמך; הערך הוא הגיבוב ורשימת מזהי הקטעים. מחיקה היא
  `collection.delete(ids=[...])`.
- `build_context` מחזירה גם את הקטעים שנכנסו; זה הטווח של הציטוטים החוקיים, לא `len(retrieved)`.
- בתקלת `ignore-context`, המודל לרוב עונה בביטחון בלי ציטוטים או עם ציטוטים חסרי כיסוי; האימות
  הוא מה שהופך את זה להימנעות. אם הוא כן מצטט נכון, זו עדיין תקלה: `prompt_variant` במעקב מסגיר
  אותה.
- פתקים בעברית: השאלה בעברית, התשובה בעברית; הציטוטים מספרים. אם המודל עונה באנגלית, ההנחיה
  („in the language of the question”) לא מספיקה למודל המהיר; נסי את המודל החכם דרך `MODEL_SMART`.

## הפתרון

`solution/ch15/`. שימי לב לשני דברים: `Retriever` בונה את BM25 פעם אחת מתוך האוסף, לא מהקבצים,
כדי שהחלוקה תהיה זהה בשני המאחזרים; ו־`run` ב־`cli.py` היא פונקציה שמקבלת לקוח ומשכן כפרמטרים,
וזו הסיבה שאפשר לבדוק את כל הצינור, כולל התקלות, בלי רשת.

## מה התרגיל מדגים

- הרכבה: עשרה פרקים נפגשים בכלי אחד, וכל פרק הוא קובץ.
- אינדוקס אינקרמנטלי עם מזהים לפי תוכן ומניפסט: הרצה חוזרת שעושה רק מה שהשתנה.
- ציטוטים כמספרים שהקוד מאמת; הימנעות כברירת מחדל כשאין בסיס.
- מעקב לפי שלבים כבסיס לדיבוג, והוכחה שלוש פעמים שהוא מספיק כדי לאתר תקלה.
- בדיקות של RAG בלי רשת: משכן מזויף, לקוח מזויף, מאגר בתיקייה זמנית.

</div>
