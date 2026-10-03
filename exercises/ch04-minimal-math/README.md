---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 4: וקטורים, Softmax וירידה בגרדיאנט

**מטרה:** לממש בעצמך את חמשת החישובים של הפרק עם numpy, ולראות את המספרים מהטקסט יוצאים מהקוד
שלך.

**זמן משוער:** שני ימי לימוד, כ־40 דקות של בנייה בכל אחד (ימים 5 ו־6 בלוח). **ידע מקדים:** פרק 4.
לא נדרש מפתח API.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/vectors.py` | שני `TODO`: דמיון קוסינוס ודירוג מסמכים |
| `starter/softmax_temperature.py` | שני `TODO`: Softmax עם טמפרטורה, והפסד |
| `starter/gradient_descent.py` | `TODO` אחד: צעד הירידה בגרדיאנט |
| `solution/` | שלושת הפתרונות המלאים |
| `tests/test_ch04.py` | תשע בדיקות |

## יום 5: וקטורים

**1. הוסיפי את numpy לפרויקט.** זו ספריית החישוב המספרי של Python; רוב ספריות ה־AI בנויות עליה.

<div dir="ltr" align="left">

```powershell
uv add numpy
```

</div>

**2. חבילה חדשה** והעתקת קוד ההתחלה של הווקטורים.

<div dir="ltr" align="left">

```powershell
mkdir ch04
New-Item ch04\__init__.py -ItemType File
Copy-Item <path-to-course>\exercises\ch04-minimal-math\starter\vectors.py ch04\
```

</div>

**3. מלאי את `cosine` ואת `rank`.** בקוסינוס: שתי נורמות, שגיאה אם אחת מהן אפס, ואז מכפלה פנימית
חלקי המכפלה שלהן. בדירוג: ציון לכל מסמך, ומיון יורד.

<div dir="ltr" align="left">

```powershell
uv run python -m ch04.vectors
```

</div>

## יום 6: Softmax והפסד, גרדיאנט

**4. העתיקי את שני הקבצים הנותרים** ומלאי את ה־`TODO` בכל אחד: Softmax (חלוקה בטמפרטורה, חיסור
המקסימום, `exp`, נרמול לסכום 1), ההפסד (מינוס לוגריתם), וצעד הגרדיאנט (`w` פחות קצב הלמידה כפול
הגרדיאנט, ואז `yield`).

<div dir="ltr" align="left">

```powershell
Copy-Item <path-to-course>\exercises\ch04-minimal-math\starter\softmax_temperature.py ch04\
Copy-Item <path-to-course>\exercises\ch04-minimal-math\starter\gradient_descent.py ch04\
uv run python -m ch04.softmax_temperature
uv run python -m ch04.gradient_descent
```

</div>

**5. בדיקות והתחייבות.**

<div dir="ltr" align="left">

```powershell
Copy-Item <path-to-course>\exercises\ch04-minimal-math\tests\test_ch04.py tests\
uv run pytest -q
git add .
git commit -m "Chapter 4: vectors, softmax, gradient descent"
```

</div>

## פלט צפוי

<div dir="ltr" align="left">

```text
dot products (length matters):
  backup policy   3.000
  login guide     1.000
  billing faq     2.000
cosine similarities (direction only):
  backup policy   0.949
  billing faq     0.707
  login guide     0.243

scaling a vector changes its dot product but not its cosine:
  dot(query, [3,1]) = 3.000   dot(query, [6,2]) = 6.000
  cos(query, [3,1]) = 0.949   cos(query, [6,2]) = 0.949
```

</div>

<div dir="ltr" align="left">

```text
logits: [2.0, 1.0, 0.0]
  T=0.5  probabilities=[0.867, 0.117, 0.016]  sum=1.000
  T=1.0  probabilities=[0.665, 0.245, 0.09]  sum=1.000
  T=2.0  probabilities=[0.506, 0.307, 0.186]  sum=1.000

loss for one example (negative log of the probability given to the correct answer):
  p(correct)=0.9   loss=0.105
  p(correct)=0.8   loss=0.223
  p(correct)=0.5   loss=0.693
  p(correct)=0.2   loss=1.609
  p(correct)=0.05  loss=2.996
```

</div>

<div dir="ltr" align="left">

```text
learning rate 0.1: steady descent toward w = 3
  step 0  w= 0.0000  loss=  9.0000
  step 1  w= 0.6000  loss=  5.7600
  step 2  w= 1.0800  loss=  3.6864
  ...
  step 10 w= 2.6779  loss=  0.1038

learning rate 1.1: each step overshoots and the loss grows
  step 1  w=   6.6000  loss=    12.9600
  step 2  w=  -1.3200  loss=    18.6624
```

</div>

## רשימת בדיקה

- [ ] הדירוג לפי קוסינוס מציב את מדריך הגיבויים ראשון, ומראה שהכפלת וקטור לא משנה את הקוסינוס
- [ ] שלוש שורות ה־Softmax מסתכמות ל־1, והראשונה חדה יותר מהשלישית
- [ ] ההפסד גדל ככל שההסתברות לתשובה הנכונה קטנה
- [ ] קצב 0.1 מתכנס לכיוון 3 וקצב 1.1 מתבדר
- [ ] תשע הבדיקות עוברות (בסך הכול 20 עם הפרקים הקודמים)

## רמזים

1. `np.linalg.norm` מחשבת נורמה; `x @ y` היא מכפלה פנימית של שני וקטורים.
2. ב־Softmax: `z - z.max()` לפני `np.exp`. התוצאה לא משתנה, אבל המספרים נשארים בטווח סביר.
3. בגרדיאנט: סדר הפעולות בלולאה הוא עדכון `w` ואז `yield`; אחרת תדווחי על הערך הישן.
4. אם `uv add numpy` איטי: ההורדה הראשונה היא כמה עשרות מגה־בייט; אחר כך היא נשמרת במטמון.

## הפתרון

הקבצים בתיקייה `solution/` מכילים את המימוש המלא. **מה הפתרון מדגים:** ההבדל בין מכפלה פנימית
לקוסינוס במספרים; חישוב כל הציונים בכפל מטריצה אחד; טמפרטורה כחידוד או שיטוח של התפלגות; והפסד
שיורד בצעדים קטנים או מתפוצץ בצעדים גדולים מדי.

</div>
