---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 3: מסווג זעיר, פער הכללה, זליגה ומדדים

**מטרה:** לבנות מסווג שלומד מדוגמאות, לראות במו עינייך את הפער בין דיוק האימון לדיוק על נתונים
חדשים, לייצר זליגת נתונים בכוונה, ולחשב מדדים מתוך מטריצת בלבול.

**זמן משוער:** שני ימי לימוד, כ־45 דקות של בנייה בכל אחד (ימים 3 ו־4 בלוח). **ידע מקדים:** פרק 3,
ופרויקט הקורס מפרק 2. לא נדרש מפתח API: הכול רץ מקומית.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/toy_classifier.py` | הנתונים, פונקציות העזר, ושני `TODO`: למידת המשקלים וחישוב הציון |
| `starter/metrics.py` | מטריצת בלבול עם חמישה `TODO`: ארבעת המדדים וספירת התאים |
| `solution/toy_classifier.py`, `solution/metrics.py` | פתרונות מלאים |
| `tests/test_ch03.py` | שמונה בדיקות; מעתיקים לתיקיית הבדיקות של הפרויקט |

## יום 3: המסווג

**1. חבילה חדשה.** מתוך תיקיית `ai-course`, צרי תיקייה לפרק עם קובץ ריק שהופך אותה לחבילה, והעתיקי
אליה את קוד ההתחלה של המסווג.

<div dir="ltr" align="left">

```powershell
mkdir ch03
New-Item ch03\__init__.py -ItemType File
Copy-Item <path-to-course>\exercises\ch03-ml-basics\starter\toy_classifier.py ch03\
```

</div>

**2. מלאי את `train`.** לכל מילה באוצר המילים: החלק מההודעות הדחופות שמכילות אותה, פחות החלק
מההודעות הלא דחופות שמכילות אותה. כל מילה נספרת פעם אחת בהודעה. התוצאה היא מילון ממילה למשקל.

**3. מלאי את `score`.** סכום המשקלים של המילים השונות בהודעה; מילה לא מוכרת תורמת אפס.

**4. הריצי כמודול.** הדגל `-m` גורם ל־Python להריץ את הקובץ כחלק מהחבילה, וכך הייבוא בין קבצי
הפרק עובד.

<div dir="ltr" align="left">

```powershell
uv run python -m ch03.toy_classifier
```

</div>

**5. קראי את הפלט.** דיוק 1.00 על האימון ו־0.60 על הבדיקה הוא הנקודה המרכזית של הפרק; כתבי בפתק
שלך במשפט אחד למה הפער קיים. אחר כך קראי את שתי השורות של „הזליגה” והסבירי לעצמך למה 1.00 שם
הוא שקר.

## יום 4: המדדים

**6. העתיקי את קוד ההתחלה של המדדים** ומלאי את חמשת ה־`TODO`: דיוק, Precision, Recall, F1, וספירת
ארבעת התאים מתוך רשימות של תחזיות ואמת. בכל חלוקה, מכנה אפס מחזיר 0.0 ולא קורס.

<div dir="ltr" align="left">

```powershell
Copy-Item <path-to-course>\exercises\ch03-ml-basics\starter\metrics.py ch03\
uv run python -m ch03.metrics
```

</div>

**7. קראי את טבלת הסף.** ככל שהסף עולה, Precision עולה ו־Recall יורד. ודאי שאת רואה את זה בטבלה שלך.

**8. בדיקות.** העתיקי את קובץ הבדיקות לתיקיית הבדיקות של הפרויקט והריצי. צפויות שמונה בדיקות
חדשות שעוברות, בנוסף לשלוש של פרק 2.

<div dir="ltr" align="left">

```powershell
Copy-Item <path-to-course>\exercises\ch03-ml-basics\tests\test_ch03.py tests\
uv run pytest -q
```

</div>

**9. התחייבות.** `git add .` ואז `git commit -m "Chapter 3: toy classifier and metrics"`.

## פלט צפוי

המסווג:

<div dir="ltr" align="left">

```text
training examples: 30, held-out examples: 10
accuracy on training data: 1.00
accuracy on held-out data: 0.60
words that push toward urgent: ['every', 'data', 'customers', 'all', 'cannot', 'orders']
words that push away:         ['tutorial', 'set', 'report', 'project', 'add', 'change']

-- the leak --
held-out accuracy WITH the leaked fields: 1.00
That number is a lie: ...
```

</div>

סדר המילים בתוך כל רשימה עשוי להשתנות מעט (מילים עם משקל זהה). המדדים:

<div dir="ltr" align="left">

```text
chapter example          TP=6   FP=4   FN=2   TN=88  acc=0.94  precision=0.60  recall=0.75  f1=0.67
baseline: never urgent   TP=0   FP=0   FN=8   TN=92  acc=0.92  precision=0.00  recall=0.00  f1=0.00

held-out scores (positive should mean urgent):
  +0.13  URGENT   Emails are not being sent to any customer
  +0.00  URGENT   Nobody can access the dashboard, please help now
  ...

threshold sweep (higher threshold = stricter about calling something urgent):
threshold -0.10          TP=5   FP=5   FN=0   TN=0   acc=0.50  precision=0.50  recall=1.00  f1=0.67
threshold -0.05          TP=5   FP=3   FN=0   TN=2   acc=0.70  precision=0.62  recall=1.00  f1=0.77
threshold +0.00          TP=2   FP=1   FN=3   TN=4   acc=0.60  precision=0.67  recall=0.40  f1=0.50
threshold +0.10          TP=2   FP=0   FN=3   TN=5   acc=0.70  precision=1.00  recall=0.40  f1=0.57
threshold +0.15          TP=1   FP=0   FN=4   TN=5   acc=0.60  precision=1.00  recall=0.20  f1=0.33
```

</div>

## רשימת בדיקה

- [ ] המסווג מדפיס דיוק 1.00 על האימון ו־0.60 על הבדיקה
- [ ] הדגמת הזליגה מדפיסה 1.00, ובפתק שלך כתוב למה זה שקר
- [ ] טבלת הסף מראה Precision עולה ו־Recall יורד
- [ ] שמונה הבדיקות החדשות עוברות (`uv run pytest -q` מדווח על 11 בסך הכול)
- [ ] את יכולה להסביר בעל פה את ההבדל בין Precision ל־Recall עם הדוגמה של מאה הפניות

## רמזים

1. ב־`train`: שני מוני מילים (`Counter`), אחד לכל מחלקה, ומספר ההודעות בכל מחלקה. המשקל הוא הפרש
   של שני שברים.
2. „כל מילה פעם אחת בהודעה”: הפעילי `set` על תוצאת `tokenize` לפני הספירה.
3. ב־`score`: המתודה `dict.get(word, 0.0)` חוסכת בדיקה האם המילה מוכרת.
4. במדדים: בדקי את המכנה לפני החלוקה; המבנה `x / y if y else 0.0` מופיע בכל ארבע הפונקציות.
5. אם `python -m ch03.metrics` נכשל על ייבוא: ודאי שהקובץ `ch03\__init__.py` קיים ושאת בתיקיית
   השורש של הפרויקט (`pwd`).

## הפתרון

הקבצים בתיקייה `solution/` מכילים את המימוש המלא. השווי אליהם אחרי שהבדיקות שלך עוברות, או אחרי
שנתקעת לפחות 20 דקות.

**מה הפתרון מדגים:** למידה ממש, בלי כללים כתובים; מדידה ישרה על נתונים שהמודל לא ראה, והפער
שנפתח בגללה; זליגה שהופכת מדידה לשקר; ומדדים שמחושבים נכון גם כשהמכנה אפס.

</div>
