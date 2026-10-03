---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# הפרויקט המסכם: Morning Brief

שתי תיקיות:

| תיקייה | מה |
| --- | --- |
| `morning-brief-starter/` | נקודת ההתחלה שלך: כל מבנה הפרויקט, הבדיקות, הקבצים לדוגמה, התיעוד, ה־workflows וההנחיות, כשכל גוף פונקציה הוא `raise NotImplementedError`. מעתיקים אותה למאגר משלך ובונים אבן אחרי אבן לפי פרק 31 |
| `morning-brief/` | מימוש ייחוס מלא: אותו מבנה, עם כל הפונקציות ממומשות, 21 בדיקות, ריצה לא־מקוונת מקצה לקצה, ורתמת הערכה בארבעה חלקים. פותחים כשנתקעים, או כדי להשוות |

## לפני אבן הדרך הראשונה (יום 51, 40 דקות)

1. קראי את פרק 30. ציירי את הצינור ביד וסמני K/M/A.
2. העתיקי את `morning-brief-starter/` לתיקייה חדשה מחוץ לקורס, למשל `C:\dev\morning-brief`, והפכי אותה למאגר Git
   משלך (`git init`). זה המאגר שיפורסם.
3. ערכי את `profile.yaml`: חמישה נושאים לפחות עם משקלים ומילות מפתח, שניים לדלג, ושלושה מקורות (שני פידים
   אמיתיים שאת קוראת ו־HN). בלי שם ובלי מייל.
4. `uv sync` ואז `uv run pytest -q`: הכול אדום. זו רשימת המשימות.
5. `uv run morning-brief run --offline`: עדיין נכשל. בסוף אבן דרך 5 זה ירוץ.

## איך עובדים עם המימוש הייחוס

- **קודם בעצמך.** כל אבן דרך בפרק 31 אומרת אילו מודולים ממשים ואילו בדיקות חייבות לעבור. הבדיקות הן המפרט.
- **כשנתקעת**, פתחי את המודול המקביל ב־`morning-brief/`, קראי, סגרי, וכתבי בעצמך. העתקה עיוורת תתנקם בראיון.
- **כשהשווית**, רשמי בפתק הבדל אחד שבחרת לשמור על הגרסה שלך, ולמה.

## פקודות

<div dir="ltr" align="left">

```powershell
uv run pytest -q                                   # offline, free, seconds
uv run morning-brief run --offline                 # fixture feeds + fake models
uv run --env-file .env morning-brief run           # real run, file delivery
uv run --env-file .env morning-brief run --channels file,email
uv run morning-brief preview --date 2026-10-03
uv run morning-brief report --date 2026-10-03
uv run --env-file .env python -m evals.run_eval --out docs/eval-latest.md
uv run python -m evals.run_eval --offline
```

</div>

הצעדים המדויקים, הפלט הצפוי, הקריטריונים והטעויות הנפוצות של כל אבן דרך: פרק 31. ההערכה, שאלות הראיון
וההצגה: פרק 32.

</div>
