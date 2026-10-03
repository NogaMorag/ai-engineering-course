---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# הפרויקט המסכם: Morning Brief

שתי תיקיות:

| תיקייה | מה |
| --- | --- |
| `morning-brief-starter/` | נקודת ההתחלה שלך: כל מבנה הפרויקט, 21 הבדיקות, הקבצים לדוגמה, התיעוד, ה־workflows וההנחיות, כשכל גוף פונקציה הוא `raise NotImplementedError`. העתיקי אותה למאגר משלך ובני אבן אחרי אבן לפי פרק 31 |
| `morning-brief/` | מימוש ייחוס מלא: אותו מבנה, עם כל הפונקציות ממומשות, 21 בדיקות ירוקות, ריצה לא־מקוונת מקצה לקצה, ורתמת הערכה בארבעה חלקים. פתחי אותו כשנתקעת, או כדי להשוות |

## לפני אבן הדרך הראשונה (יום 51, 40 דקות)

1. קראי את פרק 30. ציירי את הצינור ביד וסמני K, M או A על כל קופסה.
2. העתיקי את `morning-brief-starter/` לתיקייה חדשה מחוץ לקורס, למשל `C:\dev\morning-brief`, והפכי אותה למאגר
   Git משלך (`git init`). זה המאגר שיפורסם.
3. ערכי את `profile.yaml`: חמישה נושאים לפחות עם משקלים ומילות מפתח, שניים לדלג, ושלושה מקורות (שני פידים
   אמיתיים שאת קוראת ו־HN). בלי שם ובלי מייל.
4. התקיני והריצי את הבדיקות (הפקודות למטה). התוצאה הצפויה: 19 אדומות ושתיים ירוקות (הכתובת הקנונית
   והמדדים, כי הקוד שלהן נתון). האדומות הן רשימת המשימות.
5. הריצי את הצינור הלא־מקוון. הוא עדיין נכשל; בסוף אבן דרך 5 הוא ירוץ מקצה לקצה.

<div dir="ltr" align="left">

```powershell
uv sync
uv run pytest -q
uv run morning-brief run --offline
```

</div>

## איך עובדים עם המימוש הייחוס

- **קודם בעצמך.** כל אבן דרך בפרק 31 אומרת אילו מודולים ממשים ואילו בדיקות חייבות לעבור. הבדיקות הן המפרט.
- **כשנתקעת**, פתחי את המודול המקביל ב־`morning-brief/`, קראי, סגרי, וכתבי בעצמך. העתקה עיוורת תתנקם בראיון.
- **כשהשווית**, רשמי בפתק הבדל אחד שבחרת לשמור על הגרסה שלך, ולמה.

## פקודות

<div dir="ltr" align="left">

```powershell
uv run pytest -q                                        # offline, free, seconds
uv run morning-brief run --offline                      # fixture feeds + fake models
uv run morning-brief run --offline --date 2026-10-04    # a second "day": follow-ups appear
uv run --env-file .env morning-brief run                # real run, file delivery
uv run --env-file .env morning-brief run --stop-after collect
uv run --env-file .env morning-brief run --resume
uv run --env-file .env morning-brief run --channels file,email
uv run morning-brief preview --date 2026-10-03
uv run morning-brief report --date 2026-10-03
uv run --env-file .env python -m evals.run_eval --out docs/eval-latest.md
uv run python -m evals.run_eval --offline
```

</div>

| הפקודה | מה היא עושה |
| --- | --- |
| `pytest` | הבדיקות הלא־מקוונות: בלי מפתח, בלי רשת, שניות |
| `run --offline` | הצינור כולו על פידים לדוגמה ומודלים מזויפים; עם תאריך אחר, יום שני עם המשכים |
| `run` | ריצה אמיתית; המשלוח לקובץ בלבד כברירת מחדל |
| `run --stop-after` | עוצרת אחרי שלב נתון; התוצר שלו בתיקיית הריצה `data/runs/<date>/` |
| `run --resume` | מדלגת על שלבים שכבר יש להם תוצר מהריצה הקודמת |
| `run --channels` | רשימת ערוצים מופרדת בפסיק: קובץ, מייל או שניהם |
| `preview` | מדפיסה את ה־Markdown של גיליון שנשמר |
| `report` | מדפיסה את דוח הריצה: שלבים, זמנים, עלות לפי שלב, כשלים |
| `run_eval` | ההערכה בארבעה חלקים; עם `--offline` רק בדיקת מבנה, בלי מפתח |

> **ב־Windows:** התיעוד של הפרויקט משתמש ב־`make`, שלא מותקן כברירת מחדל. הסקריפטים בתיקייה `scripts/`
> הם אותן פקודות בדיוק:

| בתיעוד | ב־Windows בלי make |
| --- | --- |
| `make test` | `scripts/test.ps1` |
| `make eval` | `scripts/eval.ps1` |

הצעדים המדויקים, הפלט הצפוי, הקריטריונים והטעויות הנפוצות של כל אבן דרך: פרק 31. ההערכה, שאלות הראיון
וההצגה: פרק 32.

</div>
