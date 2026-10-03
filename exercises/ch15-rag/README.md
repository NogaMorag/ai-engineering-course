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
15, התרגילים של פרקים 12 עד 14, החבילות של פרקים 9 ו־11 בפרויקט (הקוד מייבא מהן את הסכמה ואת
הלקוח), ומפתח API. האינדוקס של הפתקים משכן כמה עשרות קטעים פעם אחת; כל שאלה היא שיכון אחד
וקריאת מודל אחת.

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

**1. חבילה ונתונים.** החבילה כאן היא תיקייה שלמה. הפקודות רצות מתיקיית הפרויקט `ai-course`, כשתיקיית
`ch15` עוד לא קיימת:

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

**3. מלאי את `TODO 1`** (`make_chunk_id`), ואז השוי את שתי החלוקות על הפתקים שלך. צרי קובץ חדש בשם
`ch15\explore_chunks.py`:

<div dir="ltr" align="left">

```python
import sys
from pathlib import Path

from ch15.chunking import chunk_by_heading, chunk_fixed
from ch15.loaders import load_markdown_dir

documents = load_markdown_dir(Path(sys.argv[1]))
for name, chunker in (("fixed", chunk_fixed), ("heading", chunk_by_heading)):
    chunks = [chunk for doc in documents for chunk in chunker(doc)]
    sizes = sorted(len(chunk.text) for chunk in chunks)
    print(f"\n{name}: {len(chunks)} chunks from {len(documents)} documents, median {sizes[len(sizes) // 2]} chars")
    for chunk in chunks[:5]:
        print(f"  [{chunk.path} > {chunk.heading}] {chunk.text[:80]!r}")
```

</div>

והריצי אותו על תיקיית הפתקים:

<div dir="ltr" align="left">

```powershell
uv run python -m ch15.explore_chunks path\to\obsidian
```

</div>

מה לבדוק בפלט: בחלוקה הקבועה חלק מהקטעים מתחילים באמצע משפט ונגמרים לפני סופו; בחלוקה לפי כותרות
כל קטע מתחיל בתחילת סעיף ונושא את הכותרת שלו, ומספר הקטעים שונה. **בפתק:** איזו חלוקה שמרה טוב
יותר על המשמעות, ולמה.

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
uv run --env-file .env python -m ch15.cli "מה זה RRF ולמה הוא משתמש בדרגות?" --notes-dir path\to\obsidian --trace
uv run --env-file .env python -m ch15.cli "מה מזג האוויר מחר בתל אביב?" --notes-dir path\to\obsidian --trace
```

</div>

לשלוש מהשאלות (הטמפרטורה, המשגר, RRF) יש תשובה בפתקים; לשתיים (המונדיאל, מזג האוויר) אין, והן צריכות
להסתיים בהימנעות ובקוד יציאה 2. **בפתק:** התשובות, הציטוטים, ואיך נראית הימנעות. ההרצה השנייה של
אותה פקודה חייבת לדווח במעקב, בתוך `sync`, על אפס שיכונים: `"embedded": 0`.

## יום 29: היברידי, הקשר ארוך, מטמון

**8. היברידי.** הריצי שאלה עם מזהה (למשל `E0502` או שם כלי) עם ובלי `--hybrid`, והשוי את
`retrieved` במעקב.

**9. הקשר ארוך מול RAG.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch15.compare_long_context --notes-dir path\to\obsidian
```

</div>

בדיקת המטמון בסוף הסקריפט שולחת את ההנחיה **הארוכה** (כל הפתקים) פעמיים ברצף, כי רק היא יכולה
לעבור את מינימום המטמון של המודל (נכון לאוקטובר 2026: 4,096 טוקנים במודלי Flash מדור 3.5 ומעלה;
ל־Flash-Lite בדקי בדף התיעוד). בשורות ה־RAG של הטבלה העמודה `cached` תהיה אפס, כי הנחיה עם חמישה
קטעים קצרה מהמינימום; זו קריאה נכונה ולא באג.

**בפתק:** הטבלה, היחס בטוקני הקלט, ומה `cached_tokens` הראה בקריאה השנייה של ההנחיה הארוכה. אם גם
שם יצא אפס, השוי את מספר טוקני הקלט למינימום של המודל שלך ורשמי את זה. גם זה ממצא.

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

**12. התחייבות.** תיקיית האינדקס היא נגזרת, ולכן קודם מוסיפים אותה ל־`.gitignore`:

<div dir="ltr" align="left">

```powershell
Add-Content .gitignore "ch15/index/"
git add .
git commit -m "Chapter 15: ask_notes RAG with citations, traces and fault injection"
```

</div>

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
הטמפרטורה מחלקת את הלוגיטים לפני הסופטמקס; טמפרטורה נמוכה מחדדת את ההתפלגות וגבוהה משטחת אותה [1].
טמפרטורה אפס אינה „מצב אמת”: תשובה שגויה הופכת לשגויה באופן עקבי [1][2].

[1] 06-generation-and-its-knobs.md › יצירת טקסט והכפתורים שלה
[2] 05-inside-a-language-model.md › בתוך מודל שפה
```

</div>

ובפלט השגיאות (stderr), עם `--trace`, מעקב JSON. השדות העיקריים שלו:

<div dir="ltr" align="left">

```text
documents, indexed_chunks, sync{added, updated, skipped, removed, embedded}
retrieved[{id, path, heading, score}], context_chunks, context_chars
prompt_variant, answer, citations, invalid_citations, supported, abstained
input_tokens, output_tokens, cached_tokens, attempts, latency_s
```

</div>

## רשימת בדיקה

- [ ] אותו קטע מקבל אותו מזהה בכל הרצה; עריכה משנה אותו.
- [ ] `sync` שני ברצף: אפס שיכונים; עריכת פתק אחד: `updated: 1` והקטעים הישנים נעלמו.
- [ ] ציטוט מחוץ לטווח מוסר ונרשם; תשובה בלי ציטוט חוקי הופכת להימנעות.
- [ ] שלוש שאלות עם תשובה ושתיים בלי מתנהגות נכון; `--hybrid` משנה את האחזור על מזהה.
- [ ] טבלת הקשר ארוך מול RAG ובדיקת המטמון בפתק.
- [ ] שלוש התקלות אותרו מהמעקב, עם השורה המסגירה.
- [ ] שמונה הבדיקות ו־ruff עוברים; README קצר קיים.

## טעויות נפוצות ותיקונים

- **תיקיית `ch15` כבר הייתה קיימת לפני ההעתקה.** הפקודה עם `-Recurse` יוצרת אז תיקייה מקוננת בשם
  `ch15\ch15`, והייבוא נכשל. מחקי את התיקייה הפנימית, או העתיקי את תוכן `starter\ch15` ישירות לתוך
  `ch15`.
- **הרצה בלי `--notes-dir`.** הכלי עונה רק מתוך שלושת פתקי הדוגמה, ושאלות על הקורס נגמרות בהימנעות.
  העבירי את הנתיב לתיקיית `obsidian` בכל פקודה.
- **`sync` חלקי: הישנים לא נמחקים, או המניפסט לא נשמר.** אחרי עריכת פתק האוסף מכיל גם את הגרסה
  הישנה, או שההרצה השנייה משכנת הכול שוב. מחקי לפי מזהי הקטעים מהמניפסט לפני ה־upsert, ושמרי את
  המניפסט אחרי הלולאה גם כשלא השתנה כלום.
- **לצפות למטמון על הנחיית RAG קצרה.** `cached_tokens` הוא אפס בשורות ה־RAG ובכל הנחיה שקצרה
  ממינימום המודל, גם כשהכול תקין. בודקים מטמון רק על ההנחיה הארוכה, כמו שהסקריפט עושה.
- **שגיאת 429 בהשוואת ההקשר הארוך.** ההנחיה עם כל הפתקים צורכת הרבה טוקנים לדקה בשכבה החינמית.
  הלקוח מנסה שוב לבד; אם זה חוזר, חכי דקה והריצי שוב, ואם המכסה היומית נגמרה, הריצי מחר.
- **עברית משובשת בפלט.** סימני שאלה במקום אותיות, או `UnicodeEncodeError`. הגדירי `PYTHONUTF8=1` כמו
  בפרק 2, סעיף 2.2.

## רמזים

- במניפסט, המפתח הוא הנתיב היחסי של המסמך; הערך הוא הגיבוב ורשימת מזהי הקטעים. מחיקה היא
  `collection.delete(ids=[...])`.
- `build_context` מחזירה גם את הקטעים שנכנסו; זה הטווח של הציטוטים החוקיים, לא `len(retrieved)`.
- בתקלת `ignore-context`, המודל לרוב עונה בביטחון בלי ציטוטים או עם ציטוטים חסרי כיסוי; האימות
  הוא מה שהופך את זה להימנעות. אם הוא כן מצטט נכון, זו עדיין תקלה: `prompt_variant` במעקב מסגיר
  אותה.
- פתקים בעברית: השאלה בעברית, התשובה בעברית; הציטוטים מספרים. אם המודל עונה באנגלית, ההנחיה
  („in the language of the question”) לא מספיקה למודל המהיר. נסי את המודל החכם: ב־`main` של `cli.py`
  החליפי את `GeminiClient()` בשורה הזאת (ונדרש `import os` בראש הקובץ):

<div dir="ltr" align="left">

```python
GeminiClient(model=os.environ.get("MODEL_SMART"))
```

</div>

## הפתרון

`solution/ch15/`. למה זה עובד: המזהים נגזרים מהתוכן, ולכן המניפסט יכול להחליט לפי גיבוב בלבד מה
לדלג, מה למחוק ומה לשכן, וההרצה החוזרת זולה ובטוחה; הציטוטים הם מספרים מתוך רשימת הקטעים שנכנסו
בפועל, ולכן האימות הוא השוואה של מספר לטווח, בלי ניחושים. שימי לב גם לשני דברים: `Retriever` בונה את
BM25 פעם אחת מתוך האוסף, לא מהקבצים, כדי שהחלוקה תהיה זהה בשני המאחזרים; ו־`run` ב־`cli.py` היא
פונקציה שמקבלת לקוח ומשכן כפרמטרים, וזו הסיבה שאפשר לבדוק את כל הצינור, כולל התקלות, בלי רשת.

## מה התרגיל מדגים

- הרכבה: עשרה פרקים נפגשים בכלי אחד, וכל פרק הוא קובץ.
- אינדוקס אינקרמנטלי עם מזהים לפי תוכן ומניפסט: הרצה חוזרת שעושה רק מה שהשתנה.
- ציטוטים כמספרים שהקוד מאמת; הימנעות כברירת מחדל כשאין בסיס.
- מעקב לפי שלבים כבסיס לדיבוג, והוכחה שלוש פעמים שהוא מספיק כדי לאתר תקלה.
- בדיקות של RAG בלי רשת: משכן מזויף, לקוח מזויף, מאגר בתיקייה זמנית.

</div>
