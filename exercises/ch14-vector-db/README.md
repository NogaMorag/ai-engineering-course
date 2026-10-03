---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 14: אינדקס הכותרות ב־Chroma

**מטרה:** להעביר את 200 הכותרות למאגר וקטורים מתמיד: upsert, שאילתה עם מסנן תאריך ומקור, השוואה
לסריקת numpy, וסירוב לערבב וקטורים משני מודלים עם אינדוקס מחדש.

**זמן משוער:** יום לימוד אחד (יום 26), כ־60 דקות בנייה. **ידע מקדים:** פרק 14, התרגיל של פרק 12
(הנתונים והמטמון), ומפתח API. השיכונים מגיעים מהמטמון; רק השאילתות נשלחות.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/store.py` | `HeadlineStore` עם שני `TODO`: `search` עם מסננים, ו־`reindex`; הדגמה מוכנה |
| `solution/store.py` | הפתרון המלא |
| `tests/test_ch14.py` | ארבע בדיקות, בלי רשת |

## הצעדים

**1. תלות וחבילה.**

<div dir="ltr" align="left">

```powershell
uv add chromadb
New-Item -ItemType Directory ch14 | Out-Null
New-Item -ItemType File ch14\__init__.py | Out-Null
Copy-Item path\to\exercises\ch14-vector-db\starter\store.py ch14\
Copy-Item path\to\exercises\ch14-vector-db\tests\test_ch14.py tests\
```

</div>

**2. קראי את המחלקה.** `__init__` פותח לקוח מתמיד ואוסף עם `hnsw:space=cosine` ועם שם המודל
במטא־נתונים; `needs_reindex` משווה; `upsert` מסרב כשהמודלים שונים. `Headline.day` הוא מספר שלם
בצורת yyyymmdd, כי המסננים של Chroma משווים מספרים.

**3. מלאי את `TODO 1` (`search`).** בניית `where`: אפס תנאים הוא `None`, תנאי אחד נשלח כמו שהוא,
שניים נעטפים ב־`$and`. `n_results` לא מעל גודל האוסף. הציון הוא `1 - distance`.

**4. מלאי את `TODO 2` (`reindex`).** מחיקת האוסף, יצירה מחדש עם המודל הנוכחי במטא־נתונים, ו־upsert
של הכול.

**5. בדיקות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch14.py -q
```

</div>

**6. הרצה.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch14.store
```

</div>

ההדגמה טוענת את הכותרות, משווה את חמש התוצאות הראשונות ל־numpy, מריצה שאילתה עם `since_day`
ועם `source`, ואז פותחת את אותו מאגר עם „מודל אחר” ומראה את הסירוב.

**7. בפתק:** תשובה כתובה ל„האם numpy היה מספיק כאן?” לפי חמש השאלות של סעיף 14.6, בנפרד
לכפילויות באותו יום ולזיכרון בין ימים.

**8. התחייבות.** `git commit -m "Chapter 14: headline index in Chroma"`. הוסיפי `ch14/chroma/`
ל־`.gitignore`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
upserted 200 headlines in 0.4s (count=200)

query: kubernetes upgrade broke the network
chroma top-5:   [('h103', 0.83), ('h118', 0.81), ('h061', 0.64), ...]
numpy  top-5:   [('h103', 0.83), ('h118', 0.81), ('h061', 0.64), ...]
since 20260920: [('h103', 20260925), ('h118', 20261001), ...]
source=hn:      [('h118', 'hn'), ...]

simulating a model change: a store opened with another embedder model refuses to mix vectors
needs_reindex: True
upsert refused: collection was built with 'gemini-embedding-2'; call reindex() before adding 'gemini-embedding-2@256' vectors
```

</div>

## רשימת בדיקה

- [ ] חמש התוצאות הראשונות זהות בין Chroma ל־numpy (אותם מזהים, אותו סדר).
- [ ] `since_day` ו־`source` מסננים נכון, לבד ויחד.
- [ ] `upsert` חוזר לא משנה את `count`; upsert של מזהה קיים מחליף את הטקסט.
- [ ] מודל אחר: `needs_reindex` אמת, `upsert` זורק, `reindex` מתקן ומעדכן את `stored_model`.
- [ ] ארבע הבדיקות ו־ruff עוברים.

## רמזים

- `where` לתנאי אחד: `{"day": {"$gte": 20260920}}`; לשניים: `{"$and": [tnai1, tnai2]}`.
- התוצאה של `query` היא מילון של רשימות של רשימות (שאילתה אחת, לכן `[0]`).
- אם ההדגמה מתלוננת על טלמטריה או מנסה להוריד מודל: ודאי שאת שולחת `embeddings=` בעצמך
  ושה־`Settings(anonymized_telemetry=False)` במקום.

## הפתרון

`solution/store.py`. שימי לב ל־`numpy_search`: שמונה שורות שמשמשות גם כבדיקת נכונות ל־Chroma וגם
כתשובה לשאלה „האם numpy מספיק?”.

## מה התרגיל מדגים

- מאגר וקטורים כתוספת של התמדה, מסננים ועדכונים, לא של „מהירות”.
- שם המודל כחלק מהסכמה של האוסף, וסירוב מפורש לערבב.
- בדיקת נכונות של כלי חדש מול המימוש הפשוט שכבר יש.
- ההחלטה „numpy או מאגר” כטקסט כתוב במסמך ההחלטות.

</div>
