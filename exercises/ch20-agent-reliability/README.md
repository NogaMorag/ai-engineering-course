---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 20: מעקות, אישור, אידמפוטנטיות, נקודות שמירה וזיכרון

**מטרה:** להוסיף ללולאה של פרק 19 את חמשת המנגנונים שהופכים אותה לאמינה: זיהוי לולאה, שער אישור
שמראה את הפעולה המדויקת, מפתח אידמפוטנטיות לכלי שליחה, נקודות שמירה עם המשכה אחרי קריסה, וזיכרון
העדפות שמשנה את ההנחיה במקום אחד.

**זמן משוער:** שני ימי לימוד (ימים 38 ו־39), כ־60 דקות בנייה בכל אחד. **ידע מקדים:** פרק 20,
התרגיל של פרק 19, ומפתח API להדגמות.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/guardrails.py` | `LoopDetector` (`TODO 1`), שער אישור, `idempotent` (`TODO 2`), כלי השליחה |
| `starter/persistence.py` | `RunStore` ו־`run_with_checkpoints` (`TODO 3`) |
| `starter/memory.py` | העדפות, הזרקה להנחיה, סיכום היסטוריה; מוכן |
| `starter/reliability_demo.py` | ההדגמה עם `--resume` ו־`--list` |
| `tests/test_ch20.py` | חמש בדיקות, בלי רשת |

## יום 38: מעקות, אישור, אידמפוטנטיות

**1. חבילה.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch20\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch20-agent-reliability\starter\*.py ch20\
Copy-Item path\to\exercises\ch20-agent-reliability\tests\test_ch20.py tests\
```

</div>

**2. מלאי את `TODO 1`** (`LoopDetector.__call__`): ספירת זוגות (שם, ארגומנטים קנוניים) מההיסטוריה,
ו־`loop_detected` כשזוג מוצע כבר בוצע `max_repeats` פעמים.

**3. קראי את `gated` ואת `ConsoleApproval`.** שימי לב שהדחייה היא חריגה שהמשגר של פרק 19 הופך
לתוצאת שגיאה.

**4. מלאי את `TODO 2`** (`idempotent`): מפתח, חיפוש בחנות, הרצה רק בהחמצה, `replayed: True` בפגיעה.

**5. בדיקות של היום.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch20.py -q -k "loop or approval or idempotent"
```

</div>

## יום 39: נקודות שמירה, המשכה, זיכרון

**6. מלאי את `TODO 3`** (`run_with_checkpoints`): טעינה לפי `resume_run_id` (או שגיאה), החזרה כפי
שהיא כשהריצה גמורה, שמירה לפני, `on_step=store.save`, שמירה אחרי.

**7. כל הבדיקות.** בדיקת הקריסה משתמשת בחריגה שיורשת מ־`BaseException`; קראי אותה.

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch20.py -q
```

</div>

**8. ההדגמה: קריסה אמיתית.** הריצי, ובאמצע (אחרי שהודפס הצעד הראשון במעקב, או פשוט אחרי שנייה)
לחצי Ctrl+C. ואז:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch20.reliability_demo "What changed in Kubernetes 1.36 and what should operators do?"
uv run --env-file .env python -m ch20.reliability_demo --list
uv run --env-file .env python -m ch20.reliability_demo --resume <run_id>
```

</div>

**9. אישור ושליחה.** שאלי את הסוכן שאלה שמסתיימת ב־„and email me the answer”. הוא יבקש להפעיל
`send_email`; השער יציג את הארגומנטים המדויקים. אשרי פעם אחת; הקובץ ב־`ch20\state\outbox`. הריצי
שוב עם אותה שאלה: הפעם המודל אולי ישתמש באותו `idempotency_key`, ואולי לא; רשמי מה קרה ולמה
המפתח חייב להגיע מהקוד (מזהה הגיליון), לא מהמודל.

**10. זיכרון.** ערכי את `ch20\state\preferences.json` (למשל `"language": "en"`, `"skip_topics":
["sports"]`) והריצי שוב. התשובה צריכה להשתנות. **בפתק:** מה היה קורה בלי כל אחד מחמשת המנגנונים.

**11. התחייבות.** `git commit -m "Chapter 20: guardrails, approval, idempotency, checkpoints, memory"`.
התיקייה `ch20\state` לא נכנסת ל־Git.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
=== approval needed: send_email ===
{
  "to": "me@example.com",
  "subject": "Kubernetes 1.36 upgrade notes",
  "body": "...",
  "idempotency_key": ""
}
run this? [y/N] y
run 7c1e2b9a4f30: answered after 4 model calls, 3120 tokens
...
sources: ['f03', 'f17']
```

</div>

ואחרי Ctrl+C והמשכה:

<div dir="ltr" align="left">

```text
{'run_id': '7c1e2b9a4f30', 'status': 'running', 'steps': 1, 'updated_at': ...}
run 7c1e2b9a4f30: answered after 3 model calls, ...
```

</div>

## רשימת בדיקה

- [ ] אותו כלי ואותם ארגומנטים פעמיים: `loop_detected`; ארגומנטים שונים: ממשיכים.
- [ ] דחייה בשער: תוצאת שגיאה, אפס קבצים בתיבת היוצא; אישור: קובץ אחד.
- [ ] אותו מפתח פעמיים: קובץ אחד ו־`replayed: True`; מפתח אחר: קובץ שני.
- [ ] אחרי קריסה: המצב השמור „רץ, צעד 1”; ההמשכה מסיימת; ריצה גמורה חוזרת כפי שהיא.
- [ ] העדפות משנות את ההנחיה; סיכום ההיסטוריה שומר את הפנייה הראשונה ואת הזנב.
- [ ] חמש הבדיקות ו־ruff עוברים.

## רמזים

- `canonical(arguments)` הוא `json.dumps(..., sort_keys=True)`: אותם ארגומנטים בסדר אחר הם אותו
  זוג.
- `run_with_checkpoints` מקבל `**kwargs` ומעביר אותם ל־`run_agent` (למשל `guard=`, `system=`).
- המצב נשמר כ־JSON שלם; `AgentState.from_json` משחזר גם את רשומות המעקב.

## הפתרון

`solution/`. שימי לב ש־`LoopDetector` לא מחזיק מצב משלו: אחרי המשכה הוא עובד מההיסטוריה.

## מה התרגיל מדגים

- מעקות כקוד קטן בנקודות מוגדרות של הלולאה (`guard`, `on_step`, עטיפת כלים), בלי לשכתב אותה.
- אישור שמראה את הפעולה המדויקת; אידמפוטנטיות שמגינה על פעולה; נקודות שמירה שמגינות על ריצה.
- שלושה סוגי זיכרון עם חיים שונים, והארוך משפיע במקום אחד וקריא.

</div>
