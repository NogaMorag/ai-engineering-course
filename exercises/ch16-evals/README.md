---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 16: הרתמה של `ask_notes`, שופט מכויל, ושתי גרסאות הנחיה

**מטרה:** לבנות את ההערכה של `ask_notes`: לאמת קובץ של 30 מקרים, לממש את הבדיקות הדטרמיניסטיות,
לכייל שופט נאמנות מול עשר תוויות שלך ולבדוק הטיית מיקום, להריץ את הרתמה עם חזרות ודוח, ולהשוות
שתי גרסאות הנחיה על סט הפיתוח ואז פעם אחת על סט הבדיקה.

**זמן משוער:** שלושה ימי לימוד (ימים 31 עד 33), כ־60 עד 65 דקות בנייה בכל אחד. **ידע מקדים:** פרק
16, `ask_notes` מהתרגיל של פרק 15 (עם הפתקים שלך מאונדקסים), ומפתח API. הרצה אחת על 20 מקרי
הפיתוח היא 20 קריאות; השופט מוסיף עד 16 (רק לתשובות שניתנו), וכל מקרה שנכשל מוסיף עוד שתי חזרות.
שתי גרסאות ועוד הרצת סט הבדיקה: תכנני כ־120 קריאות על פני ימים 32 ו־33, מול המכסה היומית.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `data/cases.jsonl` | 30 מקרים על פתקי הקורס: 20 בסט הפיתוח, 10 בסט הבדיקה, שש קטגוריות |
| `starter/cases.py` | סכמת המקרה, טעינה, ו־`validate_cases`; מוכן |
| `starter/checks.py` | הבדיקות הדטרמיניסטיות, עם `TODO 1` |
| `starter/judge.py` | שופט נאמנות, הסכמה וקאפה של כהן (מוכנים; קראי אותם), בדיקת מיקום (`TODO 3`) |
| `starter/harness.py` | הרצת מקרים, חזרות, רשומות; מוכן |
| `starter/report.py` | דוח לפי קטגוריה והשוואה; מוכן |
| `starter/run_eval.py` | ה־CLI, עם שתי גרסאות הנחיה; מוכן |
| `tests/test_ch16.py` | שבע בדיקות, בלי רשת |

## יום 31: המקרים והבדיקות הדטרמיניסטיות

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

הרתמה קוראת ל־`run` של פרק 15 עם שני ארגומנטים שקיימים בקוד ההתחלה ובפתרון של פרק 15: `system=`
(גרסת ההנחיה) ו־`prompt_variant=`. בדקי שהם מופיעים בחתימה של `run` ב־`ch15\cli.py` שלך; אם לא,
העתיקי מחדש את `answer.py` ו־`cli.py` מתיקיית הפתרון של פרק 15.

**2. קראי את `cases.jsonl` לפני שאת מריצה משהו.** לכל מקרה: מה הציפייה, ולמה היא נכתבה כך. שימי לב
לחמשת המקרים ללא תשובה ולשלושת העוינים.

**3. הוסיפי שלושה מקרים משלך** (אחד ישיר, אחד ללא תשובה, אחד ניסוח מחדש של מקרה קיים, באותה
קבוצה ובאותו צד של החלוקה) בלי להסתכל על תשובות. הריצי את האימות:

<div dir="ltr" align="left">

```powershell
uv run python -c "from ch16.cases import load_cases, validate_cases; print(validate_cases(load_cases()) or 'sound')"
```

</div>

הפלט צריך להיות `sound`. הבדיקה `test_cases_file_is_sound` מקבלת 30 מקרים ומעלה (20 ומעלה בסט
הפיתוח, 10 ומעלה בסט הבדיקה), ולכן הוספת מקרים לא שוברת אותה.

**4. בפתק:** איזו זליגה נמנעת בחלוקה (איזו קבוצה הייתה חוצה בלי `group`), ולמה המקרים העוינים
בנויים כפי שהם.

**5. מלאי את `TODO 1`** (`run_checks`): שבע הבדיקות מהטבלה בסעיף 16.4, כל אחת `CheckResult` עם
`detail` שמסביר.

**6. קראי את `cohens_kappa` (מו## יום 32: שופט וכיול

כן, עם הסבר בתיעוד הפונקציה) ומלאי את `TODO 3`**: בדיקת המיקום.

**7. בדיקות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch16.py -q
```

</div>

**8. כיול.** הריצי את הרתמה על סט הפיתוח עם גרסה v1 ועם השופט. זו גם הרצת v1 של יום 33, כך שהיא
לא עולה פעמיים:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch16.run_eval run --notes-dir path\to\obsidian --split dev --prompt v1 --repeats 3 --judge --out results\dev-v1.jsonl
```

</div>

עכשיו תייגי ביד, בלי להציץ בפסק הדין של השופט. שמרי את הסקריפט הבא כ־`ch16\calibrate.py`: הוא
מדפיס לעשר רשומות שנענו את השאלה, את המקורות שהמודל ראה ואת התשובה, ומסתיר את שדה `judge`:

<div dir="ltr" align="left">

```python
import json
from pathlib import Path

records = [json.loads(line) for line in Path("results/dev-v1.jsonl").read_text(encoding="utf-8").splitlines()]
answered = [r for r in records if r["judge"]][:10]
for r in answered:
    print("=" * 60, r["case_id"])
    print(r["question"], "\n--- sources ---\n" + r["sources_text"], "\n--- answer ---\n" + r["answer"])
```

</div>

<div dir="ltr" align="left">

```powershell
uv run python -m ch16.calibrate
```

</div>

לכל תשובה כתבי בפתק נאמנה או לא, לפי ההגדרה מסעיף 16.6: כל טענה בתשובה מופיעה במקורות. ואז
הוסיפי לסוף הסקריפט את התוויות שלך, באותו סדר, והריצי שוב:

<div dir="ltr" align="left">

```python
from ch16.judge import agreement, cohens_kappa

human = [True, False, True, True, True, True, False, True, True, True]   # your labels, same order
judge = [r["judge"]["faithful"] for r in answered]
print("agreement", agreement(judge, human), "kappa", round(cohens_kappa(judge, human), 2))
```

</div>

**בפתק:** שני המספרים, ולכל אי־הסכמה ה־`reasoning` של השופט ומי לדעתך צדק.

**9. מיקום.** בחרי רשומה אחת מאלה שתייגת, וכתבי לה תשובה שנייה חלשה יותר: קצרה יותר, או עם טענה
אחת שלא במקורות. הוסיפי לסוף `calibrate.py` והריצי עם `--env-file .env` (שתי קריאות למודל):

<div dir="ltr" align="left">

```python
from ch11.llm_client import GeminiClient
from ch16.judge import PairwiseJudge, position_bias_probe

r = answered[0]            # the record you chose
worse = "..."              # the weaker answer you wrote
pairwise = PairwiseJudge(GeminiClient())
print(position_bias_probe(lambda a, b: pairwise.prefer(r["question"], r["sources_text"], a, b), r["answer"], worse))
```

</div>

הפלט הוא מילון עם `first`, `second` ו־`consistent`. רשמי בפתק אם `consistent` היה אמת; אם לא, איזה
מקום השופט העדיף.

## יום 33: הרתמה והדוח

**10. גרסה v2 על סט הפיתוח, והשוואה.** קובץ v1 כבר קיים מצעד 8.

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch16.run_eval run --notes-dir path\to\obsidian --split dev --prompt v2 --repeats 3 --judge --out results\dev-v2.jsonl
uv run python -m ch16.run_eval compare results\dev-v1.jsonl results\dev-v2.jsonl
```

</div>

קראי את שתי הרשימות בסוף ההשוואה, מה תוקן ומה נשבר, לפני שאת מסתכלת על ההפרש הכולל.

**11. סט הבדיקה, פעם אחת.** הגרסה שזכתה בהשוואה, בלי לקרוא את הפרטים לפני שהדוח נכתב. הפקודה
למטה מניחה שזו v2; אם v1 זכתה, החליפי את שני המופעים:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch16.run_eval run --notes-dir path\to\obsidian --split holdout --prompt v2 --repeats 3 --judge --out results\holdout-v2.jsonl
```

</div>

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
| hebrew       | 6/7    | 7/7           | 7/7          | 7/7              | 1.86        | 0     |
| paraphrase   | 4/5    | 5/5           | 5/5          | 4/5              | 1.6         | 1     |
...
| unanswerable | 2/4    | 2/4           | -            | -                | -           | 0     |
| ALL          | 14/20  | 18/20         | 16/16        | 14/16            | 1.75        | 1     |

Cost of this run: 41230 input tokens, 2210 output tokens, 20 cases.

## Failing cases

- **c03** [direct] What does RRF use instead of raw scores? — mentions_key_fact (matched=[])
...
```

</div>

שורות PASS ו־FAIL נכתבות תוך כדי ריצה; הדוח נכתב גם לקובץ `results\dev-v1.md`. המספרים כאן
להמחשה בלבד.

## רשימת בדיקה

- [ ] `validate_cases` מחזיר רשימה ריקה; הוספת ניסוח מחדש בצד השני של החלוקה גורמת לו לדווח על בעיה.
- [ ] שבע הבדיקות עוברות; `cohens_kappa` נותנת 1.0 להסכמה מלאה ו־0 לרמת מזל.
- [ ] עשר תוויות, הסכמה וקאפה, ואי־ההסכמות רשומות; בדיקת המיקום רצה פעמיים.
- [ ] שני דוחות על סט הפיתוח, השוואה, והרצה אחת על סט הבדיקה.
- [ ] מזכר ההחלטה כולל עלות.

## טעויות נפוצות ותיקונים

- **ציפיות שנכתבו אחרי שראית תשובה.** שלושת המקרים שהוספת עוברים כולם בהרצה הראשונה, וה־`must_mention_any`
  שלהם הוא ציטוט מילה במילה מהתשובה. כותבים את הציפייה מתוך הפתק עצמו, לפני ההרצה, עם כמה
  ניסוחים חלופיים של העובדה.
- **ניסוח מחדש בצד השני של החלוקה.** `validate_cases` מדפיס „straddles dev and holdout”. נותנים
  לשני המקרים אותו `group` ואותו `split`.
- **`run` של פרק 15 לא מכיר `system=`.** ההרצה הראשונה של הרתמה נופלת עם
  `TypeError: unexpected keyword argument 'system'`. מעתיקים מחדש את `answer.py` ו־`cli.py` מתיקיית
  הפתרון של פרק 15.
- **ההרצה נעצרת על מכסה ולא נשאר קובץ.** עשרות שורות PASS ו־FAIL, ואז חריגה, ו־`results\` ריק.
  הקובץ נכתב רק בסוף; מריצים בלי `--judge` ועם `--repeats 1`, או מפצלים לשתי הרצות קטנות (ראי רמזים).

## רמזים

- `run_checks` מקבל את חלקי התשובה כארגומנטים נפרדים כדי שהבדיקות יוכלו להזין אותם בלי להריץ
  מודל; הרתמה מחלצת אותם מ־`Answer` ומ־`Trace`.
- בקאפה, `expected` הוא סכום על כל התוויות של `p_a(label) * p_b(label)`; כשהוא 1.0 (שני הצדדים
  אומרים תמיד אותו דבר) מחזירים 1.0 כדי לא לחלק באפס.
- אם ההרצה נעצרת על מכסה, הרשומות שכבר הושלמו אובדות, כי הקובץ נכתב רק בסוף. פיצול פשוט: לקצר
  זמנית את `cases.jsonl` לחצי מהמקרים, להריץ, להחליף לחצי השני, ולאחד את שני קובצי התוצאות בעורך.
  שיפור טוב כתרגיל: כתיבה שורה־שורה דרך `on_record` ב־`run_cases`.

## הפתרון

`solution/` מכיל את כל הקבצים. שלוש החלטות שכדאי לקרוא בו: `run_checks` מקבל את חלקי התשובה
כארגומנטים נפרדים ולא את `Answer` עצמו, ולכן הבדיקות שלו רצות בלי מודל ובלי תלות בפרק 15;
השופט מקבל רק את המקורות שנכנסו להקשר (`sources_text`), כי נאמנות נמדדת מול מה שהמודל ראה, לא
מול כל האוסף; ו־`evaluate_case` מריץ חזרות רק למקרה שנכשל, כי הרצה חוזרת של מקרה שעבר עולה כסף
ולא משנה את ההחלטה.

## מה התרגיל מדגים

- ציפיות לפני תוצאות, קטגוריות, ומקרים ללא תשובה כמדד להימנעות.
- קוד בודק מה שקוד יכול; שופט עם רובריקה למה שלא; והשופט מכויל, לא מונח.
- רתמה חוזרת עם חזרות, מונה ומכנה לפי קטגוריה, עלות, והשוואה שמראה מה התהפך.
- סט בדיקה שרץ פעם אחת, ומזכר החלטה במקום „זה נראה טוב יותר”.

</div>
