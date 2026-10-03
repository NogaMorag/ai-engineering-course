---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 16: הרתמה של `ask_notes`, שופט מכויל, ושתי גרסאות הנחיה

**מטרה:** לבנות את ההערכה של `ask_notes`: לאמת קובץ של 30 מקרים, לממש את הבדיקות הדטרמיניסטיות,
לכייל שופט נאמנות מול עשר תוויות שלך ולבדוק הטיית מיקום, להריץ את הרתמה עם חזרות ודוח, ולהשוות
שתי גרסאות הנחיה על פיתוח ואז פעם אחת על בדיקה.

**זמן משוער:** שלושה ימי לימוד (ימים 31 עד 33), כ־60 עד 65 דקות בנייה בכל אחד. **ידע מקדים:** פרק
16, `ask_notes` מהתרגיל של פרק 15 (עם הפתקים שלך מאונדקסים), ומפתח API. הרצה מלאה על 20 מקרי
פיתוח היא 20 קריאות, ועם שופט עד 40; שתי גרסאות וחזרות מכפילות. מתכננים את זה מול המכסה היומית.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `data/cases.jsonl` | 30 מקרים על פתקי הקורס: 20 פיתוח, 10 בדיקה, שש קטגוריות |
| `starter/cases.py` | סכמת המקרה, טעינה, ו־`validate_cases`; מוכן |
| `starter/checks.py` | הבדיקות הדטרמיניסטיות, עם `TODO 1` |
| `starter/judge.py` | שופט נאמנות, הסכמה, קאפה (`TODO 2`), בדיקת מיקום (`TODO 3`) |
| `starter/harness.py` | הרצת מקרים, חזרות, רשומות; מוכן |
| `starter/report.py` | דוח לפי קטגוריה והשוואה; מוכן |
| `starter/run_eval.py` | ה־CLI, עם שתי גרסאות הנחיה; מוכן |
| `tests/test_ch16.py` | שבע בדיקות, בלי רשת |

## יום 31: המקרים

**1. חבילה ונתונים.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType Directory ch16\data | Out-Null
New-Item -ItemType File ch16\__init__.py | Out-Null
Copy-Item path\to\exercises\ch16-evals\starter\*.py ch16\
Copy-Item path\to\exercises\ch16-evals\data\cases.jsonl ch16\data\
Copy-Item path\to\exercises\ch16-evals\tests\test_ch16.py tests\
```

</div>

הפרק 15 שלך צריך את העדכון הקטן מהתרגיל הזה: `answer_question` ו־`run` מקבלים `system=` (העתיקי
מחדש את `ch15\answer.py` ו־`ch15\cli.py` מתיקיית הפתרון של פרק 15 אם לא עשית זאת).

**2. קראי את `cases.jsonl` לפני שאת מריצה משהו.** לכל מקרה: מה הציפייה, ולמה היא נכתבה כך. שימי לב
לחמשת המקרים ללא תשובה ולשלושת העוינים.

**3. הוסיפי שלושה מקרים משלך** (אחד ישיר, אחד ללא תשובה, אחד ניסוח מחדש של מקרה קיים, באותה
קבוצה) בלי להסתכל על תשובות. הריצי את האימות:

<div dir="ltr" align="left">

```powershell
uv run python -c "from ch16.cases import load_cases, validate_cases; print(validate_cases(load_cases()) or 'sound')"
```

</div>

**4. בפתק:** איזו זליגה נמנעת בחלוקה (איזו קבוצה הייתה חוצה בלי `group`), ולמה המקרים העוינים
בנויים כפי שהם.

## יום 32: בדיקות, שופט, כיול

**5. מלאי את `TODO 1`** (`run_checks`): שבע הבדיקות מהטבלה בסעיף 16.4, כל אחת `CheckResult` עם
`detail` שמסביר.

**6. מלאי את `TODO 2` ו־`TODO 3`**: קאפה של כהן ובדיקת המיקום.

**7. בדיקות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch16.py -q
```

</div>

**8. כיול.** הריצי עשר שאלות מהמקרים דרך `ask_notes` (פרק 15), שמרי את התשובות, ותייגי ביד כל
אחת: נאמנה למקורות או לא. ואז הריצי את השופט על אותן עשר (סקריפט קצר עם `FaithfulnessJudge`),
וחשבי `agreement` ו־`cohens_kappa`. **בפתק:** המספרים, ואי־ההסכמות עם ה־`reasoning` של השופט.
**9. מיקום.** בחרי שאלה אחת עם שתי תשובות (אחת טובה, אחת פחות), והריצי `position_bias_probe` עם
`PairwiseJudge`. רשמי אם היה עקבי.

## יום 33: הרתמה והדוח

**10. שתי הרצות על פיתוח.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch16.run_eval run --notes-dir path\to\obsidian --split dev --prompt v1 --repeats 3 --out results\dev-v1.jsonl
uv run --env-file .env python -m ch16.run_eval run --notes-dir path\to\obsidian --split dev --prompt v2 --repeats 3 --judge --out results\dev-v2.jsonl
uv run python -m ch16.run_eval compare results\dev-v1.jsonl results\dev-v2.jsonl
```

</div>

**11. בדיקה, פעם אחת.** הגרסה שזכתה, על `--split holdout`, בלי לקרוא את הפרטים לפני שהדוח נכתב.

**12. מזכר החלטה** בפתק: פסקה עם מונה ומכנה לכל קטגוריה, מה התהפך, כמה טוקנים עלה, ומה הוחלט.

**13. התחייבות.** `git commit -m "Chapter 16: eval harness, calibrated judge, prompt v1 vs v2"`.
התיקייה `results\` נכנסת ל־Git: הדוחות הם תוצרים.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
PASS c01 [hebrew]
FAIL c03 [direct]
...
# dev-v1: prompt v1, dense, k=5, split=dev

| category     | passed | abstention ok | has citation | faithful (judge) | correctness | flaky |
| hebrew       | 7/8    | 8/8           | 7/7          | -                | -           | 1     |
| unanswerable | 2/4    | 2/4           | -            | -                | -           | 0     |
| ALL          | 15/20  | 18/20         | 13/14        | -                | -           | 1     |

Cost of this run: 41230 input tokens, 2210 output tokens, 20 cases.
```

</div>

## רשימת בדיקה

- [ ] `validate_cases` מחזיר רשימה ריקה; הוספת ניסוח מחדש בצד השני של החלוקה מכשילה אותו.
- [ ] שבע הבדיקות עוברות; `cohens_kappa` נותנת 1.0 להסכמה מלאה ו־0 לרמת מזל.
- [ ] עשר תוויות, הסכמה וקאפה, ואי־ההסכמות רשומות; בדיקת המיקום רצה פעמיים.
- [ ] שני דוחות על פיתוח, השוואה, והרצה אחת על בדיקה.
- [ ] מזכר ההחלטה כולל עלות.

## רמזים

- `run_checks` מקבל את תוצאות התשובה כארגומנטים נפרדים כדי שהבדיקות יוכלו להזין אותה בלי להריץ
  מודל; הרתמה מחלצת אותם מ־`Answer` ומ־`Trace`.
- בקאפה, `expected` הוא סכום על כל התוויות של `p_a(label) * p_b(label)`; כשהוא 1.0 (שני הצדדים
  אומרים תמיד אותו דבר) מחזירים 1.0 כדי לא לחלק באפס.
- אם ההרצה נעצרת על מכסה, הרשומות שכבר נכתבו? לא: הקובץ נכתב בסוף. הריצי על `--split dev` עם
  פחות חזרות, או פצלי ידנית. (שיפור אפשרי: כתיבה שורה־שורה. זה תרגיל טוב.)

## הפתרון

`solution/` מכיל את כל הקבצים. שימי לב ב־`judge.py` לכך שהשופט מקבל את **המקורות שצוטטו**, לא
את כל האוסף: השאלה היא נאמנות למה שנאמר.

## מה התרגיל מדגים

- ציפיות לפני תוצאות, קטגוריות, ומקרים ללא תשובה כמדד להימנעות.
- קוד בודק מה שקוד יכול; שופט עם רובריקה למה שלא; והשופט מכויל, לא מונח.
- רתמה חוזרת עם חזרות, מונה ומכנה לפי קטגוריה, עלות, והשוואה שמראה מה התהפך.
- holdout שרץ פעם אחת, ומזכר החלטה במקום „זה נראה טוב יותר”.

</div>
