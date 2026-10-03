---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 21 ונקודת ביקורת 5: גרף LangGraph, שרת MCP, והסקיצה של העיתון

**מטרה:** לבנות את גרף הביקורת ב־LangGraph (מחקר, הפרעה לאישור, שליחה או זריקה) עם שומר נקודות
ב־SQLite והמשכה לפי מזהה שרשור; לכתוב שרת MCP קטן ולחבר אותו ללולאה של פרק 19; לכתוב הערת החלטה
והערת אבטחה; ולסגור את חלק ו עם סקיצת צינור העיתון.

**זמן משוער:** שלושה ימי לימוד (ימים 40 עד 42), כ־70, 55 ו־60 דקות. **ידע מקדים:** פרק 21,
התרגילים של פרקים 19 ו־20, ומפתח API.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/graph_agent.py` | הגרף, עם `TODO 1`: חיבור הצמתים והקשתות |
| `starter/mcp_server.py` | שרת MCP עם שני כלים; מוכן |
| `starter/mcp_client.py` | `McpToolbox`, עם `TODO 2`: תרגום ההצהרות; והגשר `as_agent_tools` |
| `starter/mcp_agent_demo.py` | הלולאה של פרק 19 עם כלי MCP |
| `tests/test_ch21.py` | שלוש בדיקות; השלישית מריצה את השרת כתת־תהליך מקומי |

## יום 40: LangGraph

**1. תלויות וחבילה.**

<div dir="ltr" align="left">

```powershell
uv add langgraph langgraph-checkpoint-sqlite mcp
New-Item -ItemType File ch21\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch21-frameworks-mcp\starter\*.py ch21\
Copy-Item path\to\exercises\ch21-frameworks-mcp\tests\test_ch21.py tests\
```

</div>

**2. קראי את `graph_agent.py`:** המצב המוקלד, ארבעת הצמתים (שימי לב ל־`interrupt` בתוך `review`),
`start_run` ו־`resume_run`, ו־`open_checkpointer`.

**3. מלאי את `TODO 1`** (`build_graph`): הצמתים, הקשתות, הקשת המותנית, ו־`compile(checkpointer=...)`.

**4. בדיקות הגרף.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch21.py -q -k "graph or outbox"
```

</div>

הבדיקה הראשונה פותחת **גרף שני** על אותו קובץ SQLite וממשיכה את השרשור. זה הדבר שהלולאה שלנו
עשתה עם `RunStore`; כאן זה הגיע עם הספרייה.

**5. ההדגמה בשתי פקודות נפרדות**, כמו שני תהליכים:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch21.graph_agent "What changed in Kubernetes 1.36?"
uv run --env-file .env python -m ch21.graph_agent --thread <id> --approve
```

</div>

**6. בפתק: הערת ההחלטה.** ספרי שורות (הלולאה ביד מול הגרף), ועברי על שלושת הסימנים של סעיף
21.2. מסקנה לפרויקט שלך, במשפט.

## יום 41: MCP

**7. קראי את `mcp_server.py`.** עשרים שורות: שני כלים, סכמה מהחתימה, תיאור מה־docstring.

**8. מלאי את `TODO 2`** (`McpToolbox.declarations`): מהכלים של השרת להצהרות בפורמט של ה־Interactions.

**9. בדיקת ה־MCP, ואז הלקוח לבד, ואז הלולאה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch21.py -q -k mcp
uv run python -m ch21.mcp_client
uv run --env-file .env python -m ch21.mcp_agent_demo "What do my notes say about temperature, and what did the feeds report about caching?"
```

</div>

במעקב של ההדגמה צריכה להופיע קריאה ל־`mcp_search_notes`.

**10. בפתק: הערת האבטחה** בחמישה סעיפים (סעיף 21.5), עם דוגמה קונקרטית לתיאור כלי זדוני.
**אופציונלי:** הריצי שרת MCP ציבורי (מערכת קבצים) על תיקייה זמנית בקריאה בלבד, ורשמי מה התיאורים
שלו היו מרשים.

## יום 42: נקודת ביקורת 5

**11. שאלות הראיון** של פרקים 19 עד 21, בקול, בלי להציץ.

**12. סקיצת הצינור** של העיתון, עמוד אחד: השלבים בסדר; לכל שלב „תהליך עבודה” או „סוכן”; איפה המצב
חי (SQLite, Chroma, קבצים); ההפרעה היחידה; כלי סוכן המחקר ותקציביו; מה אינו כלי (שליחה).

**13. התחייבות.** `git commit -m "Chapter 21: LangGraph review graph, MCP server and bridge, pipeline sketch"`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
thread 3b8e1f20 is waiting for review.

Legacy CNI clusters lost pod networking after upgrading to 1.36 (f03) ...

sources: ['f03', 'f17']

resume with:  python -m ch21.graph_agent --thread 3b8e1f20 --approve   (or --reject)
state: {"question": "...", "draft": "...", "sources": ["f03", "f17"]} | next: ('review',)
```

</div>

<div dir="ltr" align="left">

```text
tools from the MCP server:
  search_notes: Search the user's markdown notes for lines containing the query (case-insensitive).  params=['query', 'max_results']
  today: Today's date (UTC) in ISO format.  params=[]
```

</div>

## רשימת בדיקה

- [ ] הגרף עוצר ב־`review` עם המטען; גרף שני על אותו קובץ ממשיך את השרשור; דחייה מגיעה ל־`discard`.
- [ ] השרת מציג שני כלים; `today` מחזיר תאריך; ארגומנט שגוי מחזיר `is_error`.
- [ ] `as_agent_tools` עוטף כלי MCP כ־`Tool`, ו־`dispatch` של פרק 19 מריץ אותו.
- [ ] במעקב של ההדגמה יש קריאה ל־`mcp_search_notes`.
- [ ] הערת החלטה, הערת אבטחה וסקיצת הצינור בפתק.
- [ ] שלוש הבדיקות ו־ruff עוברים.

## רמזים

- `interrupt` חייב checkpointer; בלי `thread_id` ב־config אין המשכה.
- ב־SDK של MCP בגרסה 2 השמות הם snake_case: `tool.input_schema`, `result.is_error`,
  `result.structured_content`. גרסה 1 השתמשה ב־camelCase ובשם `FastMCP`.
- `McpToolbox` מריץ את השרת עם `python -m ch21.mcp_server` ועם `cwd` של הפרויקט, כדי ש־`ch10`
  ייובא. אם הבדיקה נכשלת על `ModuleNotFoundError`, זה ה־cwd.
- ה־SDK של MCP אסינכרוני; `McpToolbox` מחזיק חוט רקע עם לולאת אירועים ותור. אל תשני את זה
  ל־`asyncio.run` לכל קריאה: anyio דורש שהסשן ייפתח וייסגר באותה משימה.

## הפתרון

`solution/`. שימי לב ל־`_serve` ב־`mcp_client.py`: כל המגע עם הסשן קורה בקורוטינה אחת.

## מה התרגיל מדגים

- אותה יכולת, בלולאה ובגרף, זו לצד זו, עם ספירה כנה של מה כל צד קונה.
- הפרעה והמשכה חוצות תהליכים דרך checkpointer ו־thread_id.
- MCP כתקן של שלושת השדות שכבר הכרת, שרת בעשרים שורות, וגשר שמתמודד עם סינכרוני מול
  אסינכרוני.
- אבטחה של כלים זרים: תיאורים הם הנחיה, תוצאות הן נתונים, הרשאות מינימליות.

</div>
