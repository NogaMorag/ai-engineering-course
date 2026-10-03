---
direction: rtl
lang: he
title: "נספח ב: פתרון תקלות התקנה"
---

<div dir="rtl" lang="he">

# נספח ב: פתרון תקלות התקנה

הנספח הזה הוא המקום הראשון שבודקים כשמשהו לא עובד בסביבה. לכל תקלה: איך היא נראית, מה הסיבה, ומה
עושים. הסדר: Windows ו־PowerShell, uv ו־Python, המפתח וה־API, חבילות, ו־Obsidian. אם התקלה לא כאן, הכלל של
פרק 0: לקרוא את הודעת השגיאה עד הסוף, ולחפש את השורה האחרונה שלה כלשונה.

## PowerShell ו־Windows

| איך זה נראה | הסיבה | מה עושים |
| --- | --- | --- |
| `uv : The term 'uv' is not recognized` | הטרמינל נפתח לפני ההתקנה, או ש־PATH לא התעדכן | לסגור ולפתוח טרמינל חדש. אם עדיין: `winget install astral-sh.uv` שוב, ואז טרמינל חדש |
| `... cannot be loaded because running scripts is disabled` | מדיניות הרצת סקריפטים | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` פעם אחת |
| עברית מודפסת כסימני שאלה או ריבועים | קידוד הטרמינל | משתנה סביבה `PYTHONUTF8=1` ברמת המשתמשת (פרק 2), טרמינל חדש; ובטרמינל של Windows: גופן שתומך בעברית |
| `#` בשורת פקודה נותן שגיאה | הערות בשורת פקודה לא תמיד מותרות | לא להעתיק הערות מהספר לתוך הפקודה |
| נתיבים עם `\` ב־Python נשברים | `\n`, `\t` בתוך מחרוזת | `Path(r"C:\...")` או `/` במקום `\` |
| `Access is denied` בכתיבה לתיקייה | OneDrive או הרשאות | לעבוד מחוץ ל־OneDrive, למשל `C:\dev\` |

## uv ו־Python

| איך זה נראה | הסיבה | מה עושים |
| --- | --- | --- |
| `uv init` יצר `src/` ו־`pyproject` לא צפוי | גרסת uv יוצרת פרויקט ארוז | `uv init --bare --python 3.12` ואז `uv python pin 3.12` (פרק 2) |
| `No module named ch07` | הרצה לא מתוך תיקיית הפרויקט, או חסר `__init__.py` | `cd` לתיקייה; `python -m ch07.chat`; לוודא `__init__.py` ריק בכל חבילה |
| `pytest` לא מוצא את החבילות | `pythonpath` חסר | ב־`pyproject.toml`: `[tool.pytest.ini_options] pythonpath = ["."]` (ובפרויקט: `["src", "."]`) |
| `uv run` איטי מאוד בפעם הראשונה | הורדת Python ותלויות | פעם אחת; אחר כך מהיר |
| `uv add` נכשל על `chromadb` | חסר build tool | `uv python pin 3.12` (לא 3.13 בשלב זה), ואז שוב; לבדוק שאין רווחים עבריים בנתיב |
| `pip install` נראה קל יותר | הרגל | לא בפרויקט הזה: `uv add`. אחרת `pyproject.toml` ו־`uv.lock` נסחפים מהסביבה |

## המפתח וה־API

| איך זה נראה | הסיבה | מה עושים |
| --- | --- | --- |
| `API key not valid` | מפתח שגוי, או שהועתק עם רווח | ליצור מפתח חדש ב־AI Studio; להדביק בלי מרכאות ובלי רווחים ל־`.env` |
| `GEMINI_API_KEY` לא נקרא | `.env` לא נטען | `uv run --env-file .env ...`; לבדוק שהקובץ בתיקיית הפרויקט ושנקרא בדיוק `.env` |
| `NotFoundError` על שם המודל | שם לא קיים או לא זמין בחשבון | `MODEL_FAST` ו־`MODEL_SMART` ב־`.env` לפי רשימת המודלים ב־AI Studio |
| `RateLimitError` / `RESOURCE_EXHAUSTED` | מגבלת קצב או מכסה יומית | להמתין דקה; לבדוק את המכסה היומית ב־AI Studio; להקטין `--items`; הלקוח מפרק 11 מנסה שוב לבד |
| הפלט נקטע באמצע | `max_output_tokens` נמוך; סטטוס `incomplete` | להגדיל את המגבלה; לא לתקן את ה־JSON (פרק 9) |
| שגיאה שלא נתפסת ב־`except errors.APIError` | שגיאות ה־Interactions הן היררכיה נפרדת | לסווג לפי `status_code` (פרק 11) |
| המפתח הודבק בצ׳אט או ב־Git בטעות | חשיפה | רוטציה מיידית ב־AI Studio; ביקורת סודות (פרק 24) |

## חבילות ספציפיות

| איך זה נראה | הסיבה | מה עושים |
| --- | --- | --- |
| Chroma: `Expected a name containing 3-512 characters` | שם אוסף קצר | שם של 3 תווים ומעלה |
| Chroma: `$gte` נכשל על תאריך | מסננים משווים מספרים בלבד | תאריך כמספר `yyyymmdd` (פרק 14) |
| Chroma מנסה להוריד מודל | פונקציית שיכון ברירת מחדל | לשלוח `embeddings=` בעצמך; `Settings(anonymized_telemetry=False)` |
| `trafilatura` מחזיר `None` | דף קצר, לא HTML, או חסום | זה כשל של פריט אחד: סטטוס, לא קריסה; לבדוק `content-type` |
| `feedparser` מחזיר אפס פריטים | כתובת פיד שגויה או דף HTML במקום XML | לפתוח את הכתובת בדפדפן; לחפש את קישור ה־RSS האמיתי |
| `mcp`: `No module named 'mcp.server.fastmcp'` | גרסה 2 של ה־SDK | `from mcp.server.mcpserver import MCPServer`; שדות ב־snake_case (פרק 21) |
| LangGraph: `interrupt` לא עוצר | אין checkpointer או `thread_id` | `compile(checkpointer=SqliteSaver(...))` ו־`{"configurable": {"thread_id": ...}}` |
| `ruff` מתלונן על `BLE001` | `except Exception` רחב | לצמצם, או `# noqa: BLE001` עם הסבר, רק במשגר (פרק 10) |
| Vitest/Vite לא רלוונטי כאן | | הקורס הוא Python בלבד |

## Obsidian והספר

| איך זה נראה | הסיבה | מה עושים |
| --- | --- | --- |
| קוד מיושר לימין בתוך הפתקים | כיוון RTL של הכספת | הקטעים עטופים ב־`div dir="ltr"`; להפעיל את ה־snippet `obsidian/snippets/book-rtl.css` |
| קישורי `[[...]]` לא נפתחים | הפתקים לא בכספת | להעתיק את תיקיית `obsidian/` לתוך הכספת, או לפתוח אותה ככספת |
| ה־HTML ב־`site/` לא מתעדכן | לא נבנה מחדש | `uv run --no-project --with markdown python tools/build_html.py` |
| `site/index.html` לא נמצא | נתיב יחסי | לפתוח מהתיקייה המקומית, או מהקובץ שבזיפ |

## מה לעשות כשהנספח לא עוזר

1. ההודעה עד הסוף; השורה האחרונה כלשונה לחיפוש.
2. `uv run python -c "import X; print(X.__version__)"` לכל חבילה מעורבת: הגרסה חשובה.
3. סביבה נקייה: `Remove-Item -Recurse .venv; uv sync`.
4. פתק: מה ניסית, מה קרה. ואז לשאול, עם הפתק.

</div>
