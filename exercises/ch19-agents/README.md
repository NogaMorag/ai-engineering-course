---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 19: ניתוב ומקבול, ולולאת סוכן עם תקציבים

**מטרה:** לממש שני דפוסי תהליך עבודה ולמדוד אותם, ואז לכתוב את לולאת הסוכן: מצב מפורש, שלושה
תקציבים, סיבות עצירה, מעקב, ובדיקות בלי מודל. בסוף רץ סוכן מחקר על פיד מקומי של 20 פריטים.

**זמן משוער:** שני ימי לימוד (ימים 36 ו־37), כ־55 ו־70 דקות בנייה. **ידע מקדים:** פרק 19, פרקים 10
ו־11, ומפתח API. ההדגמות: 20 קריאות למקבול, ועד 6 לסוכן.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/patterns.py` | ניתוב (מוכן) ומקבול, עם `TODO 1` |
| `starter/agent.py` | המצב, המשגר, ההצהרות, והלולאה עם `TODO 2` |
| `starter/research_tools.py` | `search_feeds`, `read_item`, ואופציונלי `fetch_url`; מוכן |
| `starter/gemini_backend.py` | ה־backend האמיתי; מוכן |
| `starter/patterns_demo.py`, `starter/research_demo.py` | ההדגמות |
| `data/feeds.jsonl` | 20 פריטי חדשות מומצאים עם טקסט מלא |
| `tests/test_ch19.py` | שש בדיקות, בלי רשת |

## יום 36: שני דפוסים

**1. חבילה ונתונים.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType Directory ch19\data | Out-Null
New-Item -ItemType File ch19\__init__.py | Out-Null
Copy-Item path\to\exercises\ch19-agents\starter\*.py ch19\
Copy-Item path\to\exercises\ch19-agents\data\feeds.jsonl ch19\data\
Copy-Item path\to\exercises\ch19-agents\tests\test_ch19.py tests\
```

</div>

**2. קראי את `patterns.py`.** הניתוב: `route` מחזיר enum דרך פלט מובנה, `PROMPT_BY_KIND` ממפה
להנחיה. **מלאי את `TODO 1`** (`parallel_map`): סמפור, `asyncio.to_thread`, `gather`.

**3. בדיקות הדפוסים, ואז ההדגמה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch19.py -q -k "routing or parallel"
uv run --env-file .env python -m ch19.patterns_demo
```

</div>

**בפתק:** טבלת הזמנים (סדרתי מול מקבילי), ושני פריטים שקיבלו סוגים שונים והנחיות שונות. נסי
`concurrency=6` ורשמי אם קיבלת 429.

## יום 37: הלולאה

**4. קראי את `agent.py` מלמעלה.** `AgentState` ושדותיו, `Budgets`, `Tool`, `dispatch` (פרק 10),
`declarations`, ושלד `run_agent` עם ה־`TODO`.

**5. מלאי את `TODO 2`** לפי התיאור בהערה ובסעיף 19.4. סדר הדברים חשוב: תקציב לפני הקריאה; קריאת
`function_call` לפני התוצאות; `on_step` אחרי שהסבב שלם.

**6. כל הבדיקות.** הן התסריט המלא של הלולאה: ענייה עם מקורות, כל תקציב, וטו, שגיאה, סיום בעיות.

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch19.py -q
```

</div>

**7. ההדגמה.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch19.research_demo "What is slowing down Rust developers and what helps?"
uv run --env-file .env python -m ch19.research_demo "What should operators do before upgrading Kubernetes?"
```

</div>

**8. בפתק:** המעקב של ריצה אחת, סבב אחרי סבב; סיבת העצירה; והמקורות שנקראו מול המזהים שהמודל
הזכיר בתשובה (האם הם זהים?).

**9. התחייבות.** `git commit -m "Chapter 19: routing, parallel map, agent loop with budgets"`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
answer (answered, 3 model calls, 2140 tokens, 9.8s):
Compile times are the top complaint (61 percent in the survey, f02). A shared build cache helps: Cargo-Lite 2.0 ...

sources read: f02, f01

trace:
  step 1 model   2.10s  {"tool_calls": ["search_feeds"], "tokens": 610}
  step 1 tool    0.00s  {"name": "search_feeds", "arguments": {"query": "rust compile times"}, "is_error": false, ...}
  step 2 model   2.40s  {"tool_calls": ["read_item", "read_item"], "tokens": 720}
  ...
```

</div>

## רשימת בדיקה

- [ ] `run_parallel` שומר על הסדר ולא עובר את גבול המקביליות (הבדיקה מודדת שיא).
- [ ] הסוכן עונה בשישה צעדים לכל היותר ומדווח מקורות שנקראו בפועל.
- [ ] תסריט אינסופי נעצר ב־`max_steps`, ב־`timeout` עם שעון מוזרק, וב־`token_budget`.
- [ ] חריגה מה־backend הופכת ל־`error` עם רשומה במעקב; `guard` יכול להטיל וטו.
- [ ] `AgentState` עובר JSON הלוך ושוב (יידרש בפרק 20).
- [ ] שש הבדיקות ו־ruff עוברים.

## רמזים

- `asyncio.gather` מחזיר את התוצאות בסדר הקלט גם כשהן מסתיימות בסדר אחר.
- בלולאה, `_usage_tokens` סובל `usage` חסר; `_finish` ממלא תשובת ברירת מחדל כשלא ענו.
- בבדיקות, `FakeBackend.histories` שומר את ההיסטוריה שנשלחה בכל קריאה; אם צורת ההיסטוריה שגויה,
  הדפיסי אותה.
- אם המודל בהדגמה לא קורא לכלים בכלל, חזקי את ההוראה „Start by searching” או עברי ל־`MODEL_SMART`.

## הפתרון

`solution/`. שימי לב ל־`_collect_sources`: המקורות נאספים מהקריאות שהצליחו, לא מהתשובה.

## מה התרגיל מדגים

- תהליך עבודה מול סוכן בקוד: ניתוב ומקבול מצד אחד, לולאה עם החלטות של המודל מצד שני.
- מצב מפורש שמאפשר עצירה, הסבר, ובהמשך המשכה.
- שלושה תקציבים וסיבת עצירה תמיד; בדיקה של כל אחת בלי רשת.
- כלים קטנים ומתוארים, לקריאה בלבד.

</div>
