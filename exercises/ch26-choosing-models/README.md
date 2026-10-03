---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 26 ונקודת ביקורת 6: ארבעה תזכירי החלטה

**מטרה:** לכתוב שלושה תזכירי החלטה שממפים כשל נצפה לשיטה, ועוד תזכיר על API מול משקולות פתוחות;
להפעיל את טבלת ההחלטה; ולסגור את חלק ז עם שאלות הראיון של פרקים 22 עד 26.

**זמן משוער:** יום לימוד אחד (יום 50), כ־45 דקות כתיבה ו־35 דקות שאלות בקול. **ידע מקדים:** פרק 26
וחלק ה. אין קריאות ל־API.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/decision.py` | הטבלה, `recommend` (`TODO`), `render_memo`, והשוואת API מול פתוח |
| `starter/memos/example-missing-facts.md` | תזכיר לדוגמה שמסרב ל־RAG מהסיבה הנכונה |
| `tests/test_ch26.py` | שתי בדיקות |

## הצעדים

**1. חבילה.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType Directory ch26\memos -Force | Out-Null
New-Item -ItemType File ch26\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch26-choosing-models\starter\decision.py ch26\
Copy-Item path\to\exercises\ch26-choosing-models\starter\memos\*.md ch26\memos\
Copy-Item path\to\exercises\ch26-choosing-models\tests\test_ch26.py tests\
```

</div>

**2. מלאי את ה־`TODO`** (`recommend`): ניקוד לפי מילות מפתח, השורה הטובה ביותר, או `None`.

**3. הטבלה והבדיקות.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch26.py -q
uv run python -m ch26.decision
uv run python -m ch26.decision "the summarizer sometimes returns four bullets and sometimes a paragraph"
```

</div>

**4. קראי את התזכיר לדוגמה.** שימי לב איך הוא מתחיל מהכשל ומהראיות, ולמה הוא דוחה RAG.

**5. כתבי שלושה תזכירים** בעזרת `render_memo` (או ביד, באותו מבנה), עמוד כל אחד:

| תזכיר | התרחיש |
| --- | --- |
| חסרות עובדות | מערכת שעונה על שאלות על מוצר פנימי ומפספסת את הגרסאות החדשות |
| פורמט לא עקבי | מסכם שמחזיר לפעמים ארבע נקודות ולפעמים פסקה |
| סיווג צר שנכשל | מסווג „דחוף או לא” על 5,000 פניות עם 71 אחוז דיוק אחרי שלוש גרסאות הנחיה |

**6. תזכיר רביעי:** API מול משקולות פתוחות למערכת שמסכמת מסמכים רפואיים פנימיים. התחילי מ„מה
יכריע”.

**7. שאלות הראיון** של פרקים 22 עד 26, בקול, בלי להציץ. מה שלא זרם, בפתק עם המספר של הפרק.

**8. התחייבות.** `git commit -m "Chapter 26: decision table and four memos"`. התזכירים נכנסים
ל־`ch26\memos`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
symptom: the output format is inconsistent (fields missing, wrong types, extra prose)
first:   structured output with a schema and validation
         the shape is a contract the API can enforce; the code validates the rest
         cost: almost free
         not when: the task has no fixed shape
then:    one repair attempt
         a validator message fixes most residual errors
```

</div>

## רשימת בדיקה

- [ ] `recommend` ממפה את שלושת התרחישים לשורות הנכונות ומחזיר `None` על טקסט לא קשור.
- [ ] ארבעה תזכירים של עמוד, כל אחד עם שמונה הכותרות, ו„איך נדע” מדיד (מדד, סט, מתי).
- [ ] שאלות הראיון של חלק ז נענו בקול.
- [ ] שתי הבדיקות ו־ruff עוברים.

## רמזים

- מילות המפתח ב־`RULES` הן תת־מחרוזות באנגלית; השאלה בתרגיל באנגלית. לעברית תוסיפי מילים לרשימה.
- תזכיר טוב אומר מה *לא* נבחר ולמה; זה מה שמבדיל החלטה מדעה.

## הפתרון

`solution/`. הטבלה היא נקודת פתיחה: הוסיפי שורה משלך לכשל שראית בפרויקט.

## מה התרגיל מדגים

- מכשל נצפה לשיטה, ולא להפך.
- כוונון עדין במקומו הנכון: מאוחר, צר, מדוד.
- API מול פתוח כהחלטה עם גורם מכריע, לא „תלוי”.
- תזכיר כפורמט שראיינת ומנהלת קוראות באותה קלות.

</div>
