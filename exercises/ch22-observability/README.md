---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 22: מעקב משלך, מסכם וסוכן מכושרים, ודוח ריצה

**מטרה:** לבנות `Tracer` שכותב JSONL עם spans מקוננים, לעטוף איתו את הלקוח של פרק 11 ואת הלולאה
של פרק 19 בלי לשנות אותם, ולהפיק דוח ריצה עם עלות וזמן לכל שלב, בלי טקסט של כתבות בקובץ.

**זמן משוער:** יום לימוד אחד (יום 43), כ־60 דקות בנייה; תיבה אופציונלית ביום 44. **ידע מקדים:** פרק
22, פרקים 11 ו־19, ומפתח API להדגמה (כ־10 קריאות).

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/tracing.py` | `PRICES`, `estimate_cost`, `Span`, `Tracer` (`TODO 1`: `span`), `TracingClient` (`TODO 2`: `complete`) |
| `starter/report.py` | הדוח, עם `TODO 3`: `summarize` |
| `starter/traced_agent.py` | העטיפות ללולאה; מוכן |
| `starter/demo.py` | ההדגמה: שלושה סיכומים וסוכן, ואז הדוח |
| `tests/test_ch22.py` | ארבע בדיקות, בלי רשת |

## הצעדים

**1. חבילה.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch22\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch22-observability\starter\*.py ch22\
Copy-Item path\to\exercises\ch22-observability\tests\test_ch22.py tests\
```

</div>

**2. `PRICES`.** פתחי את `tracing.py` והשוו את הטבלה למחירים העדכניים (נספח ג, או דף המחירים של
הספק). אם משהו השתנה, עדכני, ורשמי תאריך בהערה.

**3. מלאי את `TODO 1`** (`Tracer.span`): יצירת span עם ההורה מהמחסנית, דחיפה, `yield`, סימון שגיאה
וזריקה מחדש בחריגה, ובסיום: זמן סיום, הוצאה מהמחסנית, כתיבה.

**4. מלאי את `TODO 2`** (`TracingClient.complete`): span מסוג `llm` עם המודל, ההגדרות וטביעת האצבע של
ההנחיה; קריאה ללקוח הפנימי; עדכון התכונות (טוקנים, ניסיונות, סטטוס, עלות, טביעת אצבע של התשובה).

**5. מלאי את `TODO 3`** (`report.summarize`): קיבוץ לפי `kind:name`, ספירות, סכומי טוקנים ועלות, p50
ו־p95, ומודלים בלי מחיר.

**6. בדיקות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch22.py -q
```

</div>

**7. ההדגמה והדוח.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch22.demo
uv run python -m ch22.report ch22\out\traces.jsonl
Select-String -Path ch22\out\traces.jsonl -Pattern "Cargo-Lite"
```

</div>

הפקודה האחרונה חייבת להחזיר כלום: אין טקסט של כתבה במעקב.

**8. בפתק:** על אילו שלושה דברים היית מתריעה בפרויקט, ובאיזה סף; ומה היית צריכה לרשום נוסף כדי
לענות על „למה הריצה של יום שלישי עלתה כפול”.

**9. התחייבות.** `git commit -m "Chapter 22: tracer, traced client and agent, run report"`.
התיקייה `ch22\out` לא נכנסת ל־Git.

**אופציונלי (יום 44):** פתחי חשבון בשכבה חינמית של כלי מעקב מתארח, ושלחי אליו את אותם spans
(רוב הכלים מקבלים JSON עם אותם שדות או דרך OpenTelemetry). רשמי מה המציג נתן שהקובץ לא נתן.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
# run 3f2a9c1d7b40

27 spans, 1 trace(s).

| span                  | calls | errors | in    | cached | out  | cost USD | p50 ms | p95 ms |
| llm:agent.model       | 4     | 0      | 6120  | 0      | 410  | 0.006128 | 2210.5 | 3005.1 |
| llm:summarize         | 3     | 0      | 3720  | 0      | 470  | 0.002291 | 1840.0 | 2910.0 |
| stage:research-agent  | 1     | 0      | 0     | 0      | 0    | 0.000000 | 9800.0 | 9800.0 |
| tool:tool.read_item   | 2     | 0      | 0     | 0      | 0    | 0.000000 | 1.2    | 1.9    |
...
Estimated paid-tier cost of this run: 0.008419 USD.
```

</div>

## רשימת בדיקה

- [ ] spans מקוננים: הילדים נסגרים לפני ההורה; `parent_id` נכון; חריגה מסומנת וזורקת הלאה.
- [ ] span של מודל כולל מודל, טוקנים, עלות, ניסיונות, סטטוס, ו`prompt_sha256` במקום הטקסט.
- [ ] הדוח מקבץ לפי שלב ומסמן מודל בלי מחיר.
- [ ] חיפוש טקסט של כתבה בקובץ המעקב מחזיר כלום.
- [ ] ארבע הבדיקות ו־ruff עוברים.

## רמזים

- `@contextmanager` עם `try / except / finally`: ה־`except` מסמן וזורק מחדש; ה־`finally` סוגר וכותב.
- `estimate_cost` מקבל את טוקני הקלט *בלי* החלק מהמטמון, ואת המטמון בנפרד.
- בבדיקות השעון מוזרק (`clock=Clock()`) ולכן `duration_ms` צפוי במדויק.

## הפתרון

`solution/`. שימי לב ל־`text_attributes`: נקודה אחת מחליטה אם נרשם טקסט או טביעת אצבע.

## מה התרגיל מדגים

- מעקב כעץ של spans עם תכונות, ולא כ־print.
- עטיפה של רכיבים קיימים במקום שינוי שלהם.
- דוח שמקבץ לפי שלב ומאפשר החלטות עלות וזמן.
- הסתרה כברירת מחדל, בנקודה אחת.

</div>
