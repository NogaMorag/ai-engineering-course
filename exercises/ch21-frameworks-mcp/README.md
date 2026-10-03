---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 21 ונקודת ביקורת 5: גרף LangGraph, שרת MCP, והסקיצה של העיתון

**מטרה:** לבנות את גרף הביקורת ב־LangGraph (מחקר, הפרעה לאישור, שליחה או זריקה) עם שומר נקודות
ב־SQLite והמשכה לפי מזהה שרשור; לכתוב שרת MCP קטן ולחבר אותו ללולאה של פרק 19; לכתוב הערת החלטה
והערת אבטחה; ולסגור את חלק ו עם סקיצת צינור העיתון.

**זמן משוער:** שלושה ימי לימוד (ימים 40 עד 42), כ־70, 55 ו־60 דקות בנייה. **ידע מקדים:** פרק 21,
התרגילים של פרקים 19 ו־20, התיקייה `ch10\data\notes` מהתרגיל של פרק 10 (שרת ה־MCP מחפש בה, ובדיקה
אחת מצפה למצוא בה את המילה „temperature”), ומפתח API להדגמות. הבדיקות עצמן רצות בלי מפתח.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/graph_agent.py` | הגרף, עם `TODO 1`: חיבור הצמתים והקשתות |
| `starter/mcp_server.py` | שרת MCP עם שני כלים; מוכן |
| `starter/mcp_client.py` | `McpToolbox`, עם `TODO 2`: תרגום ההצהרות; והגשר `as_agent_tools` |
| `starter/mcp_agent_demo.py` | הלולאה של פרק 19 עם כלי MCP |
| `tests/test_ch21.py` | שלוש בדיקות; השלישית מריצה את השרת כתת־תהליך מקומי |

## יום 40: LangGraph

**1. תלויות וחבילה.** מתיקיית הפרויקט `ai-course`:

<div dir="ltr" align="left">

```powershell
uv add langgraph langgraph-checkpoint-sqlite mcp
New-Item -ItemType File ch21\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch21-frameworks-mcp\starter\*.py ch21\
Copy-Item path\to\exercises\ch21-frameworks-mcp\tests\test_ch21.py tests\
```

</div>

הפקודה הראשונה מוסיפה שלוש חבילות ל־`pyproject.toml` ומעדכנת את `uv.lock`; היא יכולה לקחת דקה או
שתיים, כי LangGraph מביאה איתה תלויות משלה.

**2. קראי את `graph_agent.py`.** בסדר הזה:

- `ReviewState`: המצב המוקלד, חמישה שדות, כולם אופציונליים.
- ארבעת הצמתים: מחקר, ביקורת (עם `interrupt` כשורה הראשונה), שליחה, זריקה.
- `start_run` ו־`resume_run`: איך הריצה מתחילה, ואיך ההחלטה חוזרת לתוך הגרף.
- `open_checkpointer`: שומר הנקודות על קובץ SQLite.

**3. מלאי את `TODO 1`** (`build_graph`): יצירת הגרף על `ReviewState`, ארבעת הצמתים, הקשתות מההתחלה
דרך המחקר אל הביקורת, הקשת המותנית מהביקורת אל השליחה או הזריקה, שתי קשתות אל הסוף, והידור עם שומר
הנקודות.

**4. בדיקות הגרף.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch21.py -q -k "graph or outbox"
```

</div>

הבדיקה הראשונה פותחת **גרף שני** על אותו קובץ SQLite וממשיכה את השרשור. זה הדבר שהלולאה שלנו
עשתה עם `RunStore`; כאן זה הגיע עם הספרייה.

**5. ההדגמה בשתי פקודות נפרדות**, כמו שני תהליכים. הפקודה הראשונה מדפיסה מזהה שרשור; אותו מעתיקים
לשנייה:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch21.graph_agent "What changed in Kubernetes 1.36?"
uv run --env-file .env python -m ch21.graph_agent --thread <id> --approve
```

</div>

אחרי האישור נוצר קובץ בתיקייה `ch21\state\outbox`. הריצי שוב את הפקודה הראשונה עם שאלה אחרת,
והפעם סיימי עם `--reject` במקום `--approve`: הפלט צריך להיות `delivered = discarded`, בלי קובץ חדש.

**6. בפתק: הערת ההחלטה.** ספרי שורות בשני הצדדים:

<div dir="ltr" align="left">

```powershell
(Get-Content ch19\agent.py, ch20\guardrails.py, ch20\persistence.py).Count
(Get-Content ch21\graph_agent.py).Count
```

</div>

הספירה הראשונה היא הלולאה ביד עם השומר, השער והחנות; השנייה היא הגרף (שבתוכו עדיין רצה הלולאה
של פרק 19 כצומת). עברי על שלושת הסימנים של סעיף 21.2 מול הפרויקט שלך, וסיימי במסקנה של משפט
אחד: גרף או לולאה, ולמה.

## יום 41: MCP

**7. קראי את `mcp_server.py`.** עשרים שורות: שני כלים, סכמה מהחתימה, תיאור מה־docstring. אל תריצי
אותו ביד: הוא מחכה ללקוח על הקלט הסטנדרטי ונראה תקוע.

**8. מלאי את `TODO 2`** (`McpToolbox.declarations`): לכל כלי של השרת מילון אחד בפורמט ההצהרות של
ה־Interactions, עם הסכמה אחרי `clean_schema`. השדות מפורטים בהערה שבקוד.

**9. בדיקת ה־MCP, ואז הלקוח לבד, ואז הלולאה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch21.py -q -k mcp
uv run python -m ch21.mcp_client
uv run --env-file .env python -m ch21.mcp_agent_demo "What do my notes say about temperature, and what did the feeds report about caching?"
```

</div>

הפקודה השנייה מדפיסה את שני הכלים, תוצאת חיפוש אחת ואת התאריך של היום. במעקב של הפקודה השלישית
אמורה להופיע שורה `tool mcp_search_notes`.

**10. בפתק: הערת האבטחה** בחמישה סעיפים (סעיף 21.5), עם דוגמה קונקרטית לתיאור כלי זדוני.

**אופציונלי:** חברי שרת MCP ציבורי. שרת מערכת הקבצים הרשמי דורש Node.js מותקן. צרי תיקייה זמנית
עם קובץ טקסט אחד, והריצי מתוך `uv run python` את הקוד הבא:

<div dir="ltr" align="left">

```python
from pathlib import Path
from ch21.mcp_client import McpToolbox

sandbox = Path(r"C:\temp\mcp-sandbox")
with McpToolbox("npx", ["-y", "@modelcontextprotocol/server-filesystem", str(sandbox)]) as toolbox:
    for declaration in toolbox.declarations():
        print(declaration["name"], "::", declaration["description"])
```

</div>

רשמי לכל כלי ברשימה מה התיאור שלו היה מרשה לסוכן לעשות על התיקייה, ואילו מהם היית מכניסה לרשימה
המותרת.

## יום 42: נקודת ביקורת 5

**11. שאלות הראיון** של פרקים 19 עד 21, בקול, בלי להציץ.

**12. סקיצת הצינור** של העיתון, עמוד אחד: השלבים בסדר; לכל שלב „תהליך עבודה” או „סוכן”; איפה המצב
חי (SQLite, Chroma, קבצים); ההפרעה היחידה; כלי סוכן המחקר ותקציביו; מה אינו כלי (שליחה).

**13. התחייבות.** התיקייה `ch21\state` (קובץ הגרף ותיבת היוצא) לא נכנסת ל־Git:

<div dir="ltr" align="left">

```powershell
Add-Content .gitignore "ch21/state/"
git add .gitignore pyproject.toml uv.lock ch21 tests\test_ch21.py
git commit -m "Chapter 21: LangGraph review graph, MCP server and bridge, pipeline sketch"
```

</div>

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

## טעויות נפוצות ותיקונים

- **הגרף הודר בלי שומר נקודות.** הריצה לא נעצרת בביקורת כמו שצריך, או שהספרייה מתלוננת שאין
  checkpointer, והמטען שחוזר מ־`start_run` ריק. מעבירים את שומר הנקודות לקריאה ל־`compile`.
- **ההמשכה מתחילה ריצה חדשה.** המחקר רץ שוב ונוצרת טיוטה חדשה במקום שליחה. שתי הפקודות חייבות
  אותו מזהה שרשור, וההמשכה עוברת דרך `Command(resume=...)`, לא דרך קלט חדש.
- **הקשת המותנית מחזירה ערך שלא מופיע במיפוי.** הספרייה מתלוננת על יעד לא מוכר. הפונקציה מחזירה
  בדיוק אחד משני המפתחות של המילון שהעברת, והמילון ממפה אותם לשמות הצמתים.
- **`ModuleNotFoundError: ch10` בבדיקת ה־MCP.** תת־התהליך של השרת רץ עם תיקיית עבודה לא נכונה.
  מריצים את הבדיקות מתיקיית הפרויקט, ומוודאים ש־`course_notes_server` מקבל את שורש הפרויקט.
- **`TimeoutError: MCP server did not become ready`.** השרת נפל בזמן הייבוא ואף אחד לא ראה את
  השגיאה. מייבאים אותו ישירות כדי לראות אותה: `uv run python -c "import ch21.mcp_server"`.
- **הסוכן לא קורא לכלי ה־MCP בהדגמה.** במעקב מופיע רק `search_feeds`. השאלה חייבת להזכיר „my
  notes”, ולפני החיבור ללולאה בדקי ש־`toolbox.tools` לא ריק ושהשמות מתחילים ב־`mcp_`.

## רמזים

- הפונקציה `interrupt` דורשת שומר נקודות; בלי `thread_id` בהגדרות הריצה אין המשכה.
- ב־SDK של MCP בגרסה 2 השמות הם snake_case: `tool.input_schema`, `result.is_error`,
  `result.structured_content`. גרסה 1 השתמשה ב־camelCase ובשם `FastMCP`.
- המחלקה `McpToolbox` מריצה את השרת עם `python -m ch21.mcp_server` ועם תיקיית עבודה של הפרויקט,
  כדי ש־`ch10` ייובא.
- ה־SDK של MCP אסינכרוני; `McpToolbox` מחזיק חוט רקע עם לולאת אירועים ותור. אל תשני את זה
  ל־`asyncio.run` לכל קריאה: anyio דורש שהסשן ייפתח וייסגר באותה משימה.

## הפתרון

`solution/`. בצד הגרף, `build_graph` עובד כי ההפרעה היא השורה הראשונה ב־`review_node`: בהמשכה
LangGraph מריצה את הצומת מחדש, ולכן שום דבר יקר או בעל תופעות לוואי לא עומד לפניה. שומר הנקודות
נפתח על קובץ, ולכן גרף חדש על אותו קובץ רואה את אותו שרשור. בצד ה־MCP, `_serve` ב־`mcp_client.py`
פותח את הסשן, מאזין לתור וסוגר, הכול בקורוטינה אחת ובחוט אחד; זו הדרישה של anyio, וזה מה שמאפשר
ללולאה הסינכרונית לקרוא לכלי בלי לפתוח סשן חדש בכל קריאה.

## מה התרגיל מדגים

- אותה יכולת, בלולאה ובגרף, זו לצד זו, עם ספירה כנה של מה כל צד קונה.
- הפרעה והמשכה חוצות תהליכים דרך שומר נקודות ומזהה שרשור, כפי ש־LangGraph מממשת אותן.
- MCP כתקן של שלושת השדות שכבר הכרת, שרת בעשרים שורות, וגשר שמתמודד עם סינכרוני מול
  אסינכרוני.
- אבטחה של כלים זרים: תיאורים הם הנחיה, תוצאות הן נתונים, הרשאות מינימליות.

</div>
