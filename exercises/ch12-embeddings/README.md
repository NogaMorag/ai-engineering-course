---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 12: שכבת השיכונים, זוגות עברית־אנגלית, וכפילויות קרובות

**מטרה:** לבנות את שכבת השיכונים שכל חלק ד והפרויקט ישתמשו בה: ממשק `Embedder`, מימוש מול Gemini,
מימוש מזויף לבדיקות, ומטמון על הדיסק. ואז שני ניסויים: עשרה זוגות משפטים בעברית ובאנגלית, וזיהוי
כפילויות קרובות ב־200 כותרות בשלושה ספים.

**זמן משוער:** שני ימי לימוד (ימים 21 ו־22), כ־60 דקות בנייה בכל אחד. **ידע מקדים:** פרק 12, ומפתח
API. ההרצות מבצעות כ־230 שיכונים ביום הראשון וההרצה הראשונה של היום השני, ואפס אחר כך.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/embedder.py` | הממשק, `GeminiEmbedder`, `FakeEmbedder`, ו־`CachedEmbedder` עם `TODO` אחד |
| `starter/similarity.py` | קוסינוס על מטריצות, שכנים, עם שני `TODO`: שכנים הדדיים וזוגות כפולים |
| `starter/pairs_demo.py`, `starter/near_duplicates.py` | שתי ההדגמות, מוכנות |
| `solution/` | הפתרון המלא |
| `data/pairs.jsonl` | עשרה זוגות משפטים |
| `data/headlines.jsonl` | 200 כותרות מומצאות, 22 מהן זוגות מתוכננים של אותה ידיעה |
| `tests/test_ch12.py` | שבע בדיקות, בלי רשת |

## יום 21: הממשק והזוגות

**1. חבילה ונתונים.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType Directory ch12\data | Out-Null
New-Item -ItemType File ch12\__init__.py | Out-Null
Copy-Item path\to\exercises\ch12-embeddings\starter\*.py ch12\
Copy-Item path\to\exercises\ch12-embeddings\data\*.jsonl ch12\data\
Copy-Item path\to\exercises\ch12-embeddings\tests\test_ch12.py tests\
```

</div>

**2. קראי את `embedder.py`.** שימי לב ל־`normalize_rows` (פעם אחת, במקום אחד), לאצוות של 50
ב־`GeminiEmbedder`, ול־`FakeEmbedder`: טריגרמים של תווים עם גיבוב. הוא לא מבין משמעות, אבל מחרוזות
דומות מקבלות וקטורים דומים, וזה כל מה שבדיקה צריכה.

**3. מלאי את שני ה־`TODO` ב־`similarity.py`.** שכנים הדדיים: `argmax` בשני הצירים. זוגות כפולים:
מסכת משולש עליון כדי שכל זוג ייספר פעם אחת, ואז מיון לפי ציון.

**4. בדיקות חלקיות ואז ההדגמה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch12.py -q -k "similarity or neighbors or mutual or pairs or normalize"
uv run --env-file .env python -m ch12.pairs_demo
```

</div>

**5. רשמי בפתק:** כמה זוגות הדדיים מתוך עשרה, אילו נכשלו ולמה לדעתך, ואת שני הממוצעים (זוגות
נכונים מול אקראיים).

## יום 22: המטמון והכפילויות

**6. מלאי את ה־`TODO` ב־`CachedEmbedder.embed`.** חיפוש לפי מפתח לכל טקסט, איסוף החסרים, שיכון
של החסרים בלבד, שמירה כבתים של `float32`, והחזרה בסדר הקלט.

**7. כל הבדיקות, ואז ההדגמה פעמיים.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch12.py -q
uv run --env-file .env python -m ch12.near_duplicates
uv run --env-file .env python -m ch12.near_duplicates
```

</div>

ההרצה השנייה חייבת לדווח 200 פגיעות ואפס החמצות, ולהסתיים בשבריר שנייה.

**8. בחרי סף.** קראי את 25 הזוגות המודפסים. איפה „אותה ידיעה” הופך ל„אותו נושא”? רשמי את הסף, את
האזור האפור, זוג אחד שנתפס בטעות וזוג אחד שהוחמץ (חפשי את 22 הזוגות המתוכננים: אותו `topic`,
ניסוח שונה).

**9. התחייבות.** `git add .` ואז `git commit -m "Chapter 12: embeddings, cache, near-duplicates"`.
הוסיפי `ch12/embeddings-cache.sqlite` ל־`.gitignore`; המטמון הוא נגזרת, לא מקור.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
pair  cosine(en, he)  mutual-NN  english
   0           0.871        yes  The build cache cut compile times from forty minutes to six.
   1           0.902        yes  The city will test a new traffic light system next spring.
   ...
mutual nearest neighbors: 9/10
same-pair mean 0.86 vs other-pair mean 0.42

embedded 200 headlines in 6.3s  (cache hits 0, misses 200)
threshold 0.80: 31 pairs
threshold 0.85: 19 pairs
threshold 0.90: 9 pairs
```

</div>

המספרים ישתנו; הצורה והיחסים (זוגות נכונים גבוה מאקראיים; פחות זוגות ככל שהסף עולה) לא.

## רשימת בדיקה

- [ ] `near_duplicate_pairs` מחזירה כל זוג פעם אחת, בלי זוגות של פריט עם עצמו, מהגבוה לנמוך.
- [ ] `CachedEmbedder` שולח לרשת רק טקסטים חסרים; הרצה שנייה היא 200 פגיעות.
- [ ] המטמון מפספס בכוונה כששם המודל משתנה (זה במפתח).
- [ ] טבלת הזוגות וטבלת הספים בפתק, עם הסף שנבחר והנימוק.
- [ ] שבע הבדיקות ו־ruff עוברים.

## רמזים

- `np.triu(np.ones_like(sim, dtype=bool), k=1)` היא מסכת המשולש העליון בלי האלכסון.
- ב־SQLite, `np.frombuffer(blob, dtype=np.float32)` משחזר את הווקטור; `vector.astype(np.float32).tobytes()`
  שומר אותו.
- אם `pairs_demo` מראה פחות מ־7 זוגות הדדיים, בדקי שהנרמול רץ: בלי נרמול המכפלה אינה קוסינוס.

## הפתרון

`solution/` מכיל את ארבעת הקבצים. שימי לב ל־`CountingEmbedder` בבדיקות: עטיפה שסופרת קריאות
במקום להשתמש במוק; זו הדרך לבדוק מטמון בלי להתחבר לכלום.

## מה התרגיל מדגים

- ממשק אחד לשיכונים עם מימוש אמיתי, מזויף ומטמון; שאר הקורס לא יודע מי מאחורי `embed`.
- קוסינוס על מטריצות במקום לולאות; שכנים הדדיים כבדיקת איכות לרב־לשוניות.
- סף שנבחר מתוך הנתונים, עם אזור אפור, במקום מספר מבלוג.
- מטמון במפתח של מודל וטקסט: הרגל שחוסך כסף בכל הרצה של הפרויקט.

</div>
