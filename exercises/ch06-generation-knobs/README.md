---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 6: כפתורי היצירה

**מטרה:** למדוד בעצמך מה עושים ארבעה כפתורים: טמפרטורה, גבול אורך הפלט, רמת חשיבה וזרע אקראי.

**זמן משוער:** יום לימוד אחד (יום 9), כ־50 דקות בנייה. **ידע מקדים:** פרק 6, ומפתח API פעיל.
התרגיל מבצע כ־25 קריאות קצרות; במסלול החינמי זה בחינם, ובמסלול בתשלום זה אגורות בודדות.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/generation_knobs.py` | ארבע הדגמות ושלושה `TODO`: שיעור התשובות השונות, הקריאה למודל, ורמת החשיבה |
| `solution/generation_knobs.py` | הפתרון המלא |
| `tests/test_ch06.py` | שלוש בדיקות שרצות בלי רשת |

## צעדים

**1. חבילה חדשה** והעתקת קוד ההתחלה.

<div dir="ltr" align="left">

```powershell
mkdir ch06
New-Item ch06\__init__.py -ItemType File
Copy-Item <path-to-course>\exercises\ch06-generation-knobs\starter\generation_knobs.py ch06\
```

</div>

**2. מלאי את שלושת ה־`TODO`.** שיעור התשובות השונות: מנרמלים, סופרים ערכים שונים, מחלקים במספר
התשובות. הקריאה: `generation_config` מקבל מילון עם הכפתורים. רמת החשיבה: הפרמטר `thinking_level`
בלולאת ההשוואה.

**3. נחשי לפני שאת מריצה.** רשמי בפתק: כמה תשובות שונות את מצפה לראות בסיווג בטמפרטורה 1.0? ובסיפור
של שש מילים? מה יהיה הסטטוס כשגבול הפלט הוא 20?

**4. הריצי.** ההרצה אורכת כדקה בגלל ההשהיות בין הקריאות.

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch06.generation_knobs
```

</div>

**5. השווי לניחושים שלך**, ורשמי בפתק את המספרים שקיבלת (יש מקום בפתק המוכן).

**6. בדיקות והתחייבות.**

<div dir="ltr" align="left">

```powershell
Copy-Item <path-to-course>\exercises\ch06-generation-knobs\tests\test_ch06.py tests\
uv run pytest -q
git add .
git commit -m "Chapter 6: generation knobs"
```

</div>

**7. הבוחן.** עני בכתב על עשרים השאלות בסוף פרק 6. זו נקודת הביקורת הראשונה של הקורס.

## פלט צפוי (צורה; הטקסטים והמספרים אצלך ישתנו)

<div dir="ltr" align="left">

```text
== temperature sweep ==
classification T=0.0  distinct=0.33  ['negative', 'negative', 'negative']
classification T=0.7  distinct=0.33  ['negative', 'negative', 'negative']
classification T=1.0  distinct=0.33  ['negative', 'negative', 'negative']
creative       T=0.0  distinct=0.33  [...]
creative       T=0.7  distinct=0.67  [...]
creative       T=1.0  distinct=1.00  [...]

== truncation: max_output_tokens=20 ==
status=incomplete  output_tokens=20
text: 'A database index is a data structure that improves the speed of ...'

== thinking level on a small puzzle ==
thinking_level=minimal  answer='0.10'   thought_tokens=0     latency=0.9s
thinking_level=high     answer='0.05'   thought_tokens=___   latency=_._s

== same seed twice at temperature 1.0 ==
identical=True  [...]
```

</div>

התשובה הנכונה לחידה היא 0.05; מודלים רבים עונים 0.10 בלי חשיבה. אם המודל שלך צודק גם ברמה
המינימלית, יופי; רשמי את ההבדל בטוקני החשיבה ובזמן בכל מקרה.

## רשימת בדיקה

- [ ] שיעור התשובות השונות בסיווג נמוך בכל הטמפרטורות, ובסיפור עולה עם הטמפרטורה
- [ ] הקטיעה מדפיסה סטטוס `incomplete` ומספר טוקני פלט שווה לגבול או קרוב אליו
- [ ] השוואת החשיבה מראה יותר טוקני חשיבה וזמן ארוך יותר ברמה הגבוהה
- [ ] הניחושים שרשמת לפני ההרצה מופיעים בפתק לצד התוצאות
- [ ] שלוש הבדיקות החדשות עוברות (27 בסך הכול)
- [ ] הבוחן נענה בכתב; 16 תשובות נכונות ומעלה

## רמזים

1. `distinct_ratio`: קבוצה (`set`) של התשובות המנורמלות, ואז `len` חלקי `len`.
2. אם קיבלת 429 באמצע: הגדילי את `PAUSE_SECONDS` ל־3 והריצי שוב.
3. אם הסטטוס אחרי הקטיעה אינו `incomplete`: רשמי מה כן הודפס. הסטטוסים האפשריים מפורטים בפרק 6,
   ואם הספק משתמש בערך אחר לקטיעה, זה ממצא ששווה לרשום בפתק ובנספח ב.
4. אם המודל המהיר אינו תומך ברמת חשיבה מסוימת, השגיאה תגיד זאת; בדקי את עמוד התיעוד „thinking”
   לרשימת הרמות של המודל שלך.

## הפתרון

הקובץ `solution/generation_knobs.py` מכיל את המימוש המלא. **מה הפתרון מדגים:** ניסוי מבוקר על כפתור
אחד בכל פעם; מדידה של שונות על כמה ריצות ולא על ריצה אחת; קריאת סטטוס לפני שסומכים על טקסט; והבנה
של מה חשיבה עולה ומה היא קונה.

</div>
