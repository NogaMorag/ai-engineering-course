---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 17: מ־30 מעקבים לשני תיקונים מדודים

**מטרה:** לתייג את הרשומות הנכשלות מהרתמה של פרק 16, לבנות טקסונומיה עם ספירה לפי שלב ועדיפויות,
ליישם שני תיקונים בזה אחר זה עם מדידה בין לבין, ולהוסיף את הכשלים לסט הרגרסיה.

**זמן משוער:** יום לימוד אחד (יום 34), כ־70 דקות בנייה. **ידע מקדים:** פרק 17, קובצי התוצאות
מהתרגיל של פרק 16, ומפתח API לשתי ההרצות החוזרות.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/taxonomy.py` | הטקסונומיה (שלב, סוג תיקון, חומרה) ו־`classify`, עם `TODO 1` |
| `starter/analyze.py` | תיוג, ספירה, עדיפויות (`TODO 2`), דוח, סט רגרסיה |
| `solution/` | הפתרון המלא |
| `tests/test_ch17.py` | שתי בדיקות, בלי רשת |

## הצעדים

**1. חבילה.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch17\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch17-failure-analysis\starter\*.py ch17\
Copy-Item path\to\exercises\ch17-failure-analysis\tests\test_ch17.py tests\
```

</div>

**2. קראי עשרה מעקבים בעיניים** מתוך `results\dev-v1.jsonl` (או הגרסה שזכתה), לפני כל קוד. לכל
כשל כתבי משפט חופשי בפתק: מה קרה, ואיפה בצינור. זה הקידוד הפתוח.

**3. מלאי את `TODO 1`** (`classify`): הכללים מהטבלה בסעיף 17.4. השוו שמות קבצים (לא נתיבים מלאים)
בין המקורות הצפויים, `retrieved_paths` ו־`context_paths`.

**4. מלאי את `TODO 2`** (`prioritize`): ספירה כפול חומרה, מיון יורד, שובר שוויון לפי שם.

**5. בדיקות, ואז הניתוח.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch17.py -q
uv run python -m ch17.analyze results\dev-v1.jsonl --out results\analysis-v1.md --regressions regressions.jsonl
```

</div>

**6. השוו את התיוג האוטומטי למשפטים שכתבת.** איפה הכללים טעו? איפה שתקו (`unclassified`)? הוסיפי
לפחות תג ידני אחד בפתק, ואם הוא חוזר, הוסיפי אותו ל־`TAXONOMY` ולכללים.

**7. תיקון ראשון.** הקטגוריה עם העדיפות הגבוהה. אם זו `retrieval_miss`: `--mode hybrid` או `--k 8`.
אם `context_truncated`: `k` קטן יותר או תקציב גדול יותר. אם `wrong_language` או `over_refusal`:
גרסת הנחיה. שינוי **אחד**, ואז:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch16.run_eval run --notes-dir path\to\obsidian --split dev --prompt v1 --mode hybrid --out results\dev-fix1.jsonl
uv run python -m ch16.run_eval compare results\dev-v1.jsonl results\dev-fix1.jsonl
```

</div>

**8. תיקון שני**, על בסיס הראשון, אותו תהליך, קובץ `dev-fix2.jsonl` והשוואה ל־`dev-fix1.jsonl`.

**9. בפתק:** טבלת לפני ואחרי לשני התיקונים בנפרד: מה תוקן, מה נשבר, ולמה בחרת בסדר הזה.

**10. רגרסיה.** הריצי `analyze` שוב עם `--regressions`; הוסיף אפס. הוסיפי את `regressions.jsonl`
לסט הפיתוח (או טעני אותו ברתמה בנוסף ל־`cases.jsonl`; שינוי של שלוש שורות ב־`run_eval.py`).

**11. התחייבות.** `git commit -m "Chapter 17: failure taxonomy, two measured fixes, regression set"`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
# Error analysis: dev-v1

5 failing cases out of 20.

## By stage
| stage      | tags |
| retrieval  | 2 |
| generation | 3 |

## Priorities (count x severity)
| failure type        | count | priority | stage      | fix type  | what it means |
| retrieval_miss      | 2     | 6        | retrieval  | retrieval | the expected source was not among the retrieved chunks |
| unsupported_answer  | 1     | 3        | generation | prompt    | the model answered although the notes cannot answer |
| wrong_language      | 2     | 2        | generation | prompt    | the answer is not in the language of the question |

## Suggested order of fixes
1. **retrieval_miss** (2): a retrieval fix at the retrieval stage. Re-run the dev split and compare before touching anything else.
```

</div>

## רשימת בדיקה

- [ ] `classify` מחזיר רשימה ריקה לרשומה שעברה, ואת התג הנכון לכל אחד מתשעת המקרים בבדיקה.
- [ ] דוח הניתוח נכתב, עם ספירה לפי שלב, עדיפויות, ורשימת כשלים עם הנתיבים שאוחזרו.
- [ ] תג ידני אחד לפחות שהכללים לא נתנו.
- [ ] שתי השוואות (לפני ואחרי כל תיקון), בנפרד.
- [ ] `regressions.jsonl` קיים; הרצה שנייה מוסיפה אפס; הבדיקות עוברות.

## רמזים

- `_names(paths)` בפתרון הופך נתיבים לשמות קבצים; המקורות הצפויים בקובץ המקרים הם שמות קבצים.
- `over_refusal` מתויג גם כשאין מקור צפוי בכלל (המקרה אומר רק „יש תשובה”): אז הימנעות היא
  סירוב יתר בהגדרה.
- אם רוב הכשלים הם `unclassified`, הכללים חסרים משהו שהמעקבים שלך מראים. זה בדיוק הממצא.

## הפתרון

`solution/`. שימי לב ל־`regression_cases`: הוא מחזיר את **המקרים**, לא את הרשומות, כדי שהסט
ייטען ברתמה בדיוק כמו `cases.jsonl`.

## מה התרגיל מדגים

- ניתוח כשלים כתהליך: קריאה, קידוד פתוח, קטגוריות, ספירה, עדיפות.
- מיפוי סימפטום לשלב, והסדר שנובע ממנו: אחזור לפני הנחיה לפני מודל.
- תיקון אחד בכל פעם, עם השוואה שמראה מה התהפך.
- סט רגרסיה שגדל מהמציאות.

</div>
