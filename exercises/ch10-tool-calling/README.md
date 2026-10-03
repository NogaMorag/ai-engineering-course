---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 10: שני כלים, משגר בטוח, ולולאת כלים ביד

**מטרה:** לכתוב את שני הכלים הראשונים של סוכן המחקר (`fetch_url`, `search_notes`), משגר שלא סומך
על אף ארגומנט, ולולאת קריאה לכלים עם גבול סבבים. להוכיח בבדיקות, בלי רשת, את המסלול המלא, קריאות
מקבילות, שגיאה של כלי, וכתובת חסומה.

**זמן משוער:** שני ימי לימוד (ימים 15 ו־16), כ־60 דקות בנייה בכל אחד. **ידע מקדים:** פרקים 9 ו־10,
מפתח API, וחיבור לרשת. ההדגמה מבצעת שלוש שאלות, כל אחת עם עד שתי קריאות למודל.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/tools.py` | שני הכלים, ההצהרות והמשגר, עם שני `TODO`: אימות כתובות ו־`dispatch` |
| `starter/tool_loop.py` | הלולאה, עם `TODO` אחד: `run` |
| `solution/tools.py`, `solution/tool_loop.py` | הפתרון המלא |
| `data/notes/*.md` | שלושה פתקים לדוגמה שהכלי `search_notes` מחפש בהם |
| `tests/test_ch10.py` | שמונה בדיקות, בלי רשת |

## יום 15: הכלים והמשגר

**1. תלויות וחבילה.**

<div dir="ltr" align="left">

```powershell
uv add httpx trafilatura
New-Item -ItemType Directory ch10\data | Out-Null
New-Item -ItemType File ch10\__init__.py | Out-Null
Copy-Item path\to\exercises\ch10-tool-calling\starter\*.py ch10\
Copy-Item -Recurse path\to\exercises\ch10-tool-calling\data\notes ch10\data\notes
Copy-Item path\to\exercises\ch10-tool-calling\tests\test_ch10.py tests\
```

</div>

`httpx` הוא לקוח HTTP; `trafilatura` מחלץ את הטקסט המרכזי מדף HTML (בלי תפריטים ופרסומות).
הקוד מייבא גם את `clean_schema` מ־`ch09`, אז פרק 9 חייב להיות במקום.

**2. קראי את `tools.py`.** שימי לב: הארגומנטים של כל כלי הם מודל Pydantic (`FetchUrlArgs`,
`SearchNotesArgs`); ההצהרה למודל נבנית מאותו מודל; ו־`TOOLS` הוא מילון סגור. זו הרשימה המותרת.

**3. מלאי את `TODO 1`** (`validate_public_http_url`). `urlparse`, ואז ארבע בדיקות: רק `http`
ו־`https`; יש מארח; המארח לא מתחיל באחת הקידומות ב־`BLOCKED_HOSTS` ולא מסתיים ב־`.local` או
`.internal`; ולא בטווח `172.16` עד `172.31`. כל כישלון הוא `ValueError` עם משפט ברור.

**4. מלאי את `TODO 2`** (`dispatch`). ארבעה שלבים, וכל אחד מחזיר תוצאת שגיאה במקום לזרוק: כלי לא
מוכר; ארגומנטים שלא עוברים `model_validate`; חריגה מתוך הכלי עצמו (כאן ה־`except Exception` הרחב
המוצדק היחיד, מסומן ל־ruff עם הסבר); ובהצלחה `json.dumps(result)` עם `False`.

**5. בדיקות ל־ruff ולחלק הראשון.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch10.py -q -k "url or notes or dispatch or declarations"
uv run ruff check ch10
```

</div>

## יום 16: הלולאה

**6. מלאי את ה־`TODO` ב־`run`.** קריאה ראשונה עם השאלה. ואז, עד `max_rounds` פעמים: לסכום את
הטוקנים מ־`interaction.usage` (השדות יכולים להיות `None`); לאסוף את הצעדים מסוג `function_call`;
אם אין, להחזיר את `output_text`; אחרת להריץ כל קריאה דרך `dispatch`, לבנות לכל אחת מילון
`function_result` עם `call_id`, ולשלוח את **כולן** יחד עם `previous_interaction_id`. אחרי הלולאה
זורקים `ToolLoopExceeded`.

**7. כל הבדיקות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch10.py -q
```

</div>

**8. הרצה חיה.**

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch10.tool_loop
```

</div>

**9. ניסוי תיאורים (A/B).** שני את התיאור של `search_notes` ל־`"Searches notes."` בלבד, הריצי שוב,
ובדקי אם המודל עדיין קורא לכלי על השאלה הראשונה ועדיין נמנע ממנו על השלישית. החזירי את התיאור
המקורי.

**10. רשמי בפתק** את המעקב של השאלה הראשונה: מה המודל ביקש, מה המשגר החזיר, מה הייתה התשובה, וכמה
טוקנים עלה הכול. **11. התחייבות.** `git commit -m "Chapter 10: tools, safe dispatch, tool loop"`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
you>   What do my notes say about temperature? Quote the file name.
model> Your notes (temperature.md) say that temperature divides the logits before softmax ...
       rounds=2 tools=search_notes(ok) tokens in/out=812/61

you>   Fetch https://example.com and tell me the page title in one sentence.
model> The page title is "Example Domain".
       rounds=2 tools=fetch_url(ok) tokens in/out=1030/18

you>   What is 17 times 23? Do not use any tool.
model> 17 times 23 is 391.
       rounds=1 tools=none tokens in/out=240/9
```

</div>

מספרי הטוקנים והניסוחים ישתנו; מספר הסבבים ורשימת הכלים צריכים להיות כאלה.

## רשימת בדיקה

- [ ] `file:///etc/passwd`, `http://localhost:8000` ו־`http://10.1.2.3/` נדחים; `https://example.com` עובר.
- [ ] `dispatch("delete_everything", {})` מחזיר תוצאת שגיאה ולא זורק.
- [ ] `max_results: 50` נדחה על ידי Pydantic (הגבול הוא 10).
- [ ] שתי קריאות מקבילות חוזרות בהודעה אחת, עם שני `call_id`, אחת מהן עם `is_error: true`.
- [ ] הלולאה נעצרת ב־`ToolLoopExceeded` אחרי `max_rounds`.
- [ ] שמונה הבדיקות ו־ruff עוברים; ההדגמה החיה רצה.

## רמזים

- `urlparse("http://localhost:8000").hostname` הוא `"localhost"` (בלי הפורט). `str.startswith`
  מקבל גם טאפל של קידומות.
- בבדיקות, `FakeBackend.inputs[1]` הוא בדיוק מה ששלחת בסבב השני. אם בדיקה נכשלת, הדפיסי אותו.
- `exc.errors(include_url=False)` של Pydantic נותן רשימת מילונים קריאה; `json.dumps(..., default=str)`
  מטפל בערכים שאינם JSON.
- אם ההרצה החיה מחזירה `function_call` גם על השאלה השלישית, זה לא באג שלך; זו החלטה של המודל.
  נסי לחדד את התיאור או את הוראות המערכת, ורשמי מה עזר.

## הפתרון

`solution/` מכיל את שני הקבצים. בפתרון, הבדיקה של `172.x` משתמשת בפיצול המחרוזת; בפריסה אמיתית
היית משתמשת ב־`ipaddress` ובפתרון DNS לפני ההורדה, וזה מופיע כהערה בפונקציה.

## מה התרגיל מדגים

- קריאה לכלי כהצעה: הפרדה מוחלטת בין מה שהמודל מבקש לבין מה שרץ.
- משגר כגבול אבטחה: רשימה מותרת, אימות ארגומנטים, חסימת כתובות מסוכנות, חריגות כתוצאות.
- לולאה עם גבול, מקביליות נכונה (כל התוצאות יחד), וספירת עלות לאורך סבבים.
- בדיקות של פרוטוקול בלי רשת: אובייקטים מזויפים שמחקים את צורת התשובה.

</div>
