---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 23: מדידה, חצי מהעלות, ו־`resilient_call`

**מטרה:** למדוד p50, p95 וזמן לטוקן ראשון לשני מודלים; לחתוך את עלות הסיכום של 50 פריטים בחצי
לפחות עם שיעור התקינות לצד כל גרסה; לבנות שומר תקציב; ולכתוב `resilient_call` עם מפסק זרם, מודל
גיבוי והידרדרות, נבדק עם תקלות מוזרקות.

**זמן משוער:** שלושה ימי לימוד (ימים 44 עד 46), כ־60, 70 ו־60 דקות. **ידע מקדים:** פרק 23, פרקים 11
ו־22, ומפתח API. ההרצות: כ־26 קריאות למדידה, 150 לניסוי העלות (שלוש גרסאות על 50 פריטים; אפשר
`--items 20`).

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/bench.py` | המדידה, עם `TODO 3`: `percentile` |
| `starter/budget.py` | `BudgetGuard`; מוכן |
| `starter/cost_levers.py` | ניסוי שלוש הגרסאות, ואופציונלית אצווה; מוכן |
| `starter/resilient.py` | `CircuitBreaker` (`TODO 1`), `resilient_call` (`TODO 2`), `degraded_summary` |
| `tests/test_ch23.py` | שש בדיקות, בלי רשת |

## יום 44: מדידה

**1. חבילה.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch23\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch23-latency-cost-reliability\starter\*.py ch23\
Copy-Item path\to\exercises\ch23-latency-cost-reliability\tests\test_ch23.py tests\
```

</div>

**2. מלאי את `TODO 3`** (`percentile`, לפי דרגה). **3. בדיקה והרצה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch23.py -q -k "percentile or estimate"
uv run --env-file .env python -m ch23.bench --runs 10
```

</div>

**בפתק:** הטבלה, ומסקנה בשלוש שורות, השלישית על מה עשר הרצות לא אומרות.

## יום 45: חצי מהעלות

**4. קראי את `cost_levers.py`:** שלוש גרסאות (חכם וארוך; מהיר; מהיר וקצר), שיעור תקינות לפי המאמת של
פרק 9, ושומר תקציב מעל הכול.

**5. הרצה.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch23.cost_levers --items 50 --budget-usd 0.50
```

</div>

**6. בפתק:** טבלת לפני ואחרי. האם הגרסה האחרונה זולה בחצי לפחות? האם התקינות נשמרה? מה הראה
`cached`, ולמה (הקידומת המשותפת ארוכה מספיק?). **אופציונלי:** `--batch` שולח את המחצית הלא
דחופה כעבודת אצווה; רשמי את שם העבודה ובדקי אותה אחר כך עם `client.batches.get(name=...)`.

## יום 46: אמינות

**7. מלאי את `TODO 1`** (`CircuitBreaker.allow`) ואת **`TODO 2`** (`resilient_call`): ראשי עם ניסיונות
תחומים בזמן שנותר, מפסק, גיבוי, הידרדרות, ו־`elapsed_s` לפני כל `return`.

**8. כל הבדיקות.** הן טבלת התקלות והתוצאות של סעיף 23.7.

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch23.py -q
```

</div>

**9. בפתק:** טבלת תקלה ותוצאה (שש שורות), ומה הגיבוי משנה במערכת שלך: איכות, עלות, פרטיות.

**10. התחייבות.** `git commit -m "Chapter 23: latency bench, cost levers, budget guard, resilient_call"`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
| model                 | runs | p50_s | p95_s | ttft_p50_s | cost_per_call_usd |
| gemini-3.5-flash-lite | 10   | 1.21  | 2.04  | 0.48       | 0.000215          |
| gemini-3.8-flash      | 10   | 2.37  | 4.10  | 0.71       | 0.000612          |

| variant                       | model                 | valid | in_tokens | cached | out_tokens | seconds | cost_usd |
| baseline: smart, long         | gemini-3.8-flash      | 50/50 | 21400     | 0      | 9100       | 118.0   | 0.05018  |
| lever 1: fast model           | gemini-3.5-flash-lite | 49/50 | 21400     | 12800  | 9000       | 61.2    | 0.03053  |
| lever 1+3: fast, short output | gemini-3.5-flash-lite | 50/50 | 21900     | 13100  | 4200       | 44.9    | 0.01806  |

last variant vs first: 64% cheaper; validity 50/50 -> 50/50
```

</div>

## רשימת בדיקה

- [ ] `percentile([1..10], 95) == 10` ו־`percentile([3], 95) == 3`; רשימה ריקה זורקת.
- [ ] `BudgetGuard` עוצר באמצע עם `BudgetExceeded`.
- [ ] המפסק: סגור, פתוח אחרי N, חצי פתוח אחרי קירור, סגור אחרי הצלחה.
- [ ] `resilient_call`: ראשי / ניסיון חוזר / גיבוי / הידרדרות / deadline / מפסק פתוח, כולם נבדקים.
- [ ] טבלת לפני ואחרי עם חיסכון של 50 אחוז לפחות בלי ירידה בתקינות.
- [ ] שש הבדיקות ו־ruff עוברים.

## רמזים

- הזמן שנותר: `deadline_at - clock()`, ומעבירים אותו כ־`total_deadline_s` של `RetryPolicy` מקומי.
- `with_retries` של פרק 11 כבר יודע לישון ולהפסיק; `resilient_call` רק תוחם אותו.
- בבדיקות, `Clock.sleep` מקדם את השעון במקום לישון; לכן בדיקת ה־deadline מיידית.

## הפתרון

`solution/`. שימי לב שבפתרון המפסק נרשם רק על הראשי: הגיבוי הוא מסלול חירום, לא מצב קבוע.

## מה התרגיל מדגים

- מדידה כנה: אחוזונים, זמן לטוקן ראשון, ומה המדגם לא אומר.
- הידיות לפי סדר התועלת, עם ההערכה לצד העלות.
- אמינות כהרכבה של דפוסים קטנים, כל אחד נבדק עם תקלה מוזרקת.

</div>
