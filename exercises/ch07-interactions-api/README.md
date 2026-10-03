---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 7: שיחה בשורת הפקודה שמנהלת את ההיסטוריה בעצמה

**מטרה:** לבנות צ'אט קטן שבו הקוד שלך שומר את כל הסיבובים ושולח אותם שוב בכל בקשה, מדפיס את טוקני
הקלט והפלט של כל סיבוב, ומאפשר לאפס. אחר כך לראות את הדרך השנייה, מצב בצד השרת, בשני קריאות.

**זמן משוער:** יום לימוד אחד (יום 11), כ־55 דקות בנייה. **ידע מקדים:** פרק 7, ומפתח API.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/chat.py` | הצ'אט, עם שלושה `TODO`: הקריאה למודל, בניית צעדי ההיסטוריה, דוח העלות |
| `solution/chat.py` | הפתרון המלא |
| `solution/server_state_demo.py` | שתי קריאות עם `previous_interaction_id`, להשוואה |
| `tests/test_ch07.py` | ארבע בדיקות עם ספק מדומה, בלי רשת |

## צעדים

**1. חבילה חדשה** והעתקת קוד ההתחלה.

<div dir="ltr" align="left">

```powershell
mkdir ch07
New-Item ch07\__init__.py -ItemType File
Copy-Item <path-to-course>\exercises\ch07-interactions-api\starter\chat.py ch07\
Copy-Item <path-to-course>\exercises\ch07-interactions-api\solution\server_state_demo.py ch07\
```

</div>

**2. מלאי את שלושת ה־`TODO`.** סדר מומלץ: קודם `to_steps` (רשימת מילונים, סוג לפי התפקיד), אז
`cost_report` (שניהם נבדקים בלי רשת), ולבסוף הקריאה למודל ב־`GeminiBackend.send`.

**3. הריצי את הבדיקות** לפני שאת מדברת עם המודל. שני ה־`TODO` הראשונים צריכים לעבור אותן.

<div dir="ltr" align="left">

```powershell
Copy-Item <path-to-course>\exercises\ch07-interactions-api\tests\test_ch07.py tests\
uv run pytest -q
```

</div>

**4. דברי עם המודל.** ספרי לו את שמך בסיבוב הראשון, שאלי כמה שאלות, ובסיבוב השישי שאלי מה שמך.
אחר כך `/cost`, אחר כך `/reset`, ושוב „מה שמי?”.

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch07.chat
```

</div>

**5. הדרך השנייה.** הריצי את ההדגמה של מצב בצד השרת והשווי את טוקני הקלט של הקריאה השנייה לאלה
שראית בצ'אט.

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch07.server_state_demo
```

</div>

**6. התחייבות.** `git add .` ואז `git commit -m "Chapter 7: chat with explicit history"`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
chat with gemini-3.5-flash-lite. Commands: /cost /history /reset /quit

you> My name is Noga and I write Rust and Python.
model> Nice to meet you, Noga. ...
       [input 61 | output 24 tokens]

you> ...four more turns...

you> What is my name?
model> Your name is Noga.
       [input 412 | output 6 tokens]

you> /cost
turns in history: 6
last turn:   input=   412  output=    6  thought=   0
session:     input=  1388  output=  131  thought=   0
paid-tier estimate for the session: $0.000744

you> /reset
history cleared

you> What is my name?
model> I don't know your name yet. ...
```

</div>

המספרים אצלך יהיו שונים; מה שחשוב הוא הצורה: טוקני הקלט של הסיבוב השישי גדולים בהרבה מאלה של
הראשון, ואחרי האיפוס המודל לא זוכר.

## רשימת בדיקה

- [ ] ארבע הבדיקות עוברות לפני ההרצה החיה
- [ ] המודל „זוכר” את שמך בסיבוב השישי, ולא זוכר אחרי `/reset`
- [ ] `/cost` מראה שטוקני הקלט גדלים עם ההיסטוריה
- [ ] ההדגמה של מצב בצד השרת ענתה נכון בקריאה השנייה, וטוקני הקלט שלה קטנים מאלה של צ'אט עם
  היסטוריה באורך דומה (או שרשמת בפתק מה ראית)

## רמזים

1. `to_steps`: לכל סיבוב מילון אחד. הסוג `user_input` לתפקיד `user`, אחרת `model_output`. התוכן הוא
   רשימה עם בלוק טקסט אחד.
2. `cost_report`: המחרוזת בבדיקה דורשת ריווח קבוע; השתמשי בעיצוב `{value:>6}`. הפתרון מראה את
   הצורה המדויקת אם נתקעת על הריווח.
3. אם המודל „שוכח” גם בלי איפוס: בדקי ב־`/history` שההיסטוריה באמת נשמרת ושאת שולחת את
   `self.to_steps()` ולא רק את ההודעה האחרונה.
4. שגיאת 429 באמצע שיחה: חכי דקה; ההיסטוריה נשמרת בזיכרון התוכנית.

## הפתרון

הקבצים בתיקייה `solution/` מכילים את המימוש המלא. **מה הפתרון מדגים:** ממשק מופשט (`ChatBackend`)
שמאפשר לבדוק את לוגיקת השיחה בלי רשת; היסטוריה כרשימת צעדים שהקוד שולט בה; קריאת סטטוס לפני
שימוש בטקסט; ומדידת עלות לכל סיבוב, שהיא ההרגל שיציל אותך בייצור.

</div>
