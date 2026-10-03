---
direction: rtl
lang: he
title: "נספח ב: פתרון תקלות התקנה"
---

<div dir="rtl" lang="he">

# נספח ב: פתרון תקלות התקנה

הנספח הזה הוא המקום הראשון שבודקים כשמשהו לא עובד בסביבה. לכל תקלה שלוש עמודות: איך היא נראית, מה
הסיבה הסבירה, ומה עושים. הסדר: Windows ו־PowerShell, uv ו־Python, המפתח וה־API, חבילות, הפרויקט המסכם,
Obsidian, ובסוף Mac. אם התקלה לא כאן, הכלל של פרק 0: לקרוא את הודעת השגיאה עד הסוף, ולחפש את השורה
האחרונה שלה כלשונה.

## PowerShell ו־Windows

| איך זה נראה | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| `uv : The term 'uv' is not recognized` | הטרמינל נפתח לפני ההתקנה, או ש־PATH לא התעדכן | לסגור ולפתוח טרמינל חדש. אם עדיין: `winget install astral-sh.uv` שוב, ואז טרמינל חדש |
| `... cannot be loaded because running scripts is disabled` | מדיניות הרצת סקריפטים | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` פעם אחת |
| עברית מודפסת כסימני שאלה או ריבועים | קידוד הטרמינל | משתנה סביבה `PYTHONUTF8=1` ברמת המשתמשת (פרק 2), טרמינל חדש; ובטרמינל של Windows: גופן שתומך בעברית |
| `#` בשורת פקודה נותן שגיאה | הערות בשורת פקודה לא תמיד מותרות | לא להעתיק הערות מהספר לתוך הפקודה |
| נתיבים עם `\` ב־Python נשברים | `\n`, `\t` בתוך מחרוזת | `Path(r"C:\...")` או `/` במקום `\` |
| `Access is denied` בכתיבה לתיקייה | OneDrive או הרשאות | לעבוד מחוץ ל־OneDrive, למשל `C:\dev\` |
| `make : The term 'make' is not recognized` | אין `make` ב־Windows כברירת מחדל | בפרויקט המסכם: `scripts/test.ps1` ו־`scripts/eval.ps1` הן אותן פקודות; או `winget install GnuWin32.Make` |

## uv ו־Python

| איך זה נראה | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| `uv init` יצר `src/` ו־`pyproject` לא צפוי | גרסת uv יוצרת פרויקט ארוז | `uv init --bare --python 3.12` ואז `uv python pin 3.12` (פרק 2) |
| `No module named ch07` | הרצה לא מתוך תיקיית הפרויקט, או חסר `__init__.py` | `cd` לתיקייה; `python -m ch07.chat`; לוודא `__init__.py` ריק בכל חבילה |
| `pytest` לא מוצא את החבילות | `pythonpath` חסר | ב־`pyproject.toml`: `[tool.pytest.ini_options] pythonpath = ["."]` (ובפרויקט: `["src", "."]`) |
| `uv run` איטי מאוד בפעם הראשונה | הורדת Python ותלויות | פעם אחת; אחר כך מהיר |
| `uv add` נכשל על `chromadb` | חסר build tool לגרסת Python שלך | `uv python pin 3.12` ואז שוב (נכון לאוקטובר 2026; גלגלים מוכנים ל־3.12 ודאיים); לבדוק שאין רווחים עבריים בנתיב |
| `pip install` נראה קל יותר | הרגל | לא בפרויקט הזה: `uv add`. אחרת `pyproject.toml` ו־`uv.lock` נסחפים מהסביבה |

## המפתח וה־API

| איך זה נראה | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| `API key not valid` | מפתח שגוי, או שהועתק עם רווח | ליצור מפתח חדש ב־AI Studio; להדביק בלי מרכאות ובלי רווחים ל־`.env` |
| `GEMINI_API_KEY` לא נקרא | `.env` לא נטען | `uv run --env-file .env ...`; לבדוק שהקובץ בתיקיית הפרויקט ושנקרא בדיוק `.env` |
| `NotFoundError` על שם המודל | שם לא קיים או לא זמין בחשבון | `MODEL_FAST` ו־`MODEL_SMART` ב־`.env` לפי רשימת המודלים ב־AI Studio |
| `RateLimitError` / `RESOURCE_EXHAUSTED` | מגבלת קצב או מכסה יומית | להמתין דקה; לבדוק את המכסה היומית ב־AI Studio; להקטין `--items`; הלקוח מפרק 11 מנסה שוב לבד |
| הפלט נקטע באמצע | `max_output_tokens` נמוך; סטטוס `incomplete` | להגדיל את המגבלה; לא לתקן את ה־JSON (פרק 9) |
| שגיאה שלא נתפסת ב־`except errors.APIError` | שגיאות ה־Interactions הן היררכיה נפרדת | לסווג לפי `status_code` (פרק 11) |
| המפתח הודבק בצ׳אט או ב־Git בטעות | חשיפה | רוטציה מיידית ב־AI Studio; ביקורת סודות (פרק 24) |

## חבילות ספציפיות

| איך זה נראה | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| Chroma: `Expected a name containing 3-512 characters` | שם אוסף קצר | שם של 3 תווים ומעלה |
| Chroma: `$gte` נכשל על תאריך | מסננים משווים מספרים בלבד | תאריך כמספר `yyyymmdd` (פרק 14) |
| Chroma מנסה להוריד מודל | פונקציית שיכון ברירת מחדל | לשלוח `embeddings=` בעצמך; `Settings(anonymized_telemetry=False)` |
| `trafilatura` מחזיר `None` | דף קצר, לא HTML, או חסום | זה כשל של פריט אחד: סטטוס, לא קריסה; לבדוק `content-type` |
| `feedparser` מחזיר אפס פריטים | כתובת פיד שגויה או דף HTML במקום XML | לפתוח את הכתובת בדפדפן; לחפש את קישור ה־RSS האמיתי |
| `mcp`: `No module named 'mcp.server.fastmcp'` | גרסה 2 של ה־SDK (נכון לאוקטובר 2026) | `from mcp.server.mcpserver import MCPServer`; שדות ב־snake_case (פרק 21) |
| LangGraph: `interrupt` לא עוצר | אין checkpointer או `thread_id` | `compile(checkpointer=SqliteSaver(...))` ו־`{"configurable": {"thread_id": ...}}` |
| `ruff` מתלונן על `BLE001` | `except Exception` רחב | לצמצם, או `# noqa: BLE001` עם הסבר, רק במשגר (פרק 10) |

## הפרויקט המסכם (Morning Brief)

| איך זה נראה | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| הפקודה מסתיימת ב־`partial` וקוד יציאה 2 | פריט אחד או ערוץ אחד נכשל; הגיליון יצא עם הערה | לקרוא את „Failures” בדוח הריצה (`morning-brief report`). זה לא כישלון של הריצה; `failed` וקוד 3 הם הכישלון |
| `email is not configured (SMTP_HOST, SMTP_USER, SMTP_PASSWORD, MAIL_TO)` | ערוץ המייל בלי סודות | למלא את ארבעת המשתנים ב־`.env` לפי `env.example` (ב־Actions: Secrets); או להריץ עם `--channels file` |
| `already delivered` כשרצית לשלוח שוב | רשומת המשלוח קיימת: זו האידמפוטנטיות, לא תקלה | תאריך אחר עם `--date`; או, בפיתוח בלבד, למחוק את השורה מטבלת `deliveries` |
| `no issue for 2026-10-03` מ־`preview` | אין ריצה לתאריך הזה, או `--data-dir` אחר מזה של הריצה | להריץ קודם `run` לאותו תאריך; לתת ל־`preview` את אותו `--data-dir` |
| `story memory was built with '...'; rebuild it before using '...'` | הוחלף מודל השיכון מול אוסף Chroma קיים | למחוק את `data/chroma` (או לבנות מחדש) אחרי שינוי `EMBEDDING_MODEL`, ולעדכן `index_version` ב־`versions.json` |
| `BudgetExceeded: spent 0.2600 USD of 0.25 after 12 calls` | שומר התקציב עצר את הריצה | זו התכונה. לבדוק בטבלת העלות לפי שלב מה התנפח (לולאה? פיד ענק?); להעלות `BUDGET_USD` רק עם סיבה כתובה |
| `collect.json` קטן מהצפוי | התקרה `max_articles` (ברירת מחדל 40) | להעלות דרך `MAX_ARTICLES` ב־`.env`, או להשאיר: ארבעים כתבות ביום מספיקות לעיתון |
| הריצה נעצרת מיד, לפני כל קריאה למודל, עם קוד יציאה 5 | בדיקת הגרסאות: `versions.json` לא מסכים עם שמות המודלים בסביבה, או שקובץ ההנחיה בגרסה הרשומה חסר | לעדכן את `versions.json` או את `.env` כך שיסכימו (פרק 25); זו עצירה מכוונת, לא תקלה |

## Obsidian והספר

| איך זה נראה | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| קוד מיושר לימין בתוך הפתקים | כיוון RTL של הכספת | הקטעים עטופים ב־`div dir="ltr"`; להפעיל את ה־snippet `obsidian/snippets/book-rtl.css` |
| קישורי `[[...]]` לא נפתחים | הפתקים לא בכספת | להעתיק את תיקיית `obsidian/` לתוך הכספת, או לפתוח אותה ככספת |
| ה־HTML ב־`site/` לא מתעדכן | לא נבנה מחדש | `uv run --no-project --with markdown python tools/build_html.py` |
| `site/index.html` לא נמצא | נתיב יחסי | לפתוח מהתיקייה המקומית, או מהקובץ שבזיפ |

## ב־Mac

| איך זה נראה | הסיבה הסבירה | מה עושים |
| --- | --- | --- |
| `zsh: command not found: uv` מיד אחרי ההתקנה | הטרמינל הפתוח לא קרא את ה־PATH החדש | לפתוח טרמינל חדש, או להריץ `source ~/.zshrc` |
| „cannot be opened because the developer cannot be verified” | Gatekeeper חוסם קובץ שהורד מהרשת | System Settings, ואז Privacy & Security, ואז Open Anyway ליד ההודעה |
| `zsh: command not found: code` | הפקודה של VS Code לא הותקנה ל־PATH | בתוך VS Code, בלוח הפקודות (Cmd+Shift+P): „Shell Command: Install 'code' command in PATH” |
| `python: command not found` | אין `python` גלובלי ב־Mac, ולא צריך | תמיד `uv run python`; uv מביא את גרסת Python של הפרויקט |
| מחפשת איפה להגדיר `PYTHONUTF8` | הרגל מ־Windows | לא נדרש: עברית מודפסת נכון ב־Mac כברירת מחדל |

## מה לעשות כשהנספח לא עוזר

| הצעד | הפקודה או הפעולה |
| --- | --- |
| לקרוא את ההודעה עד הסוף, ולחפש את השורה האחרונה כלשונה | |
| לבדוק את הגרסה של כל חבילה מעורבת: הגרסה חשובה | `uv run python -c "import X; print(X.__version__)"` |
| סביבה נקייה | `Remove-Item -Recurse .venv` ואז `uv sync` |
| פתק: מה ניסית, מה קרה. ואז לשאול, עם הפתק | |

</div>
