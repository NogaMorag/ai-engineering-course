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
התרגיל של פרק 19 (הלולאה חייבת לעבור את שש הבדיקות שלו), ומפתח API להדגמות. ההדגמות: עד 6
קריאות למודל בכל ריצה.

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/guardrails.py` | `LoopDetector` (`TODO 1`), שער אישור, `idempotent` (`TODO 2`), כלי השליחה |
| `starter/persistence.py` | `RunStore` ו־`run_with_checkpoints` (`TODO 3`) |
| `starter/memory.py` | העדפות, הזרקה להנחיה, סיכום היסטוריה; מוכן |
| `starter/reliability_demo.py` | ההדגמה עם `--resume` ו־`--list` |
| `tests/test_ch20.py` | חמש בדיקות, בלי רשת |

## יום 38: מעקות, אישור, אידמפוטנטיות

**1. חבילה.** מתיקיית הפרויקט `ai-course`:

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch20\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch20-agent-reliability\starter\*.py ch20\
Copy-Item path\to\exercises\ch20-agent-reliability\tests\test_ch20.py tests\
```

</div>

**2. מלאי את `TODO 1`** (`LoopDetector.__call__`):

- עוברים על צעדי `function_call` בהיסטוריה וסופרים זוגות של שם כלי וארגומנטים קנוניים.
- אם זוג מוצע כבר בוצע `max_repeats` פעמים או יותר, מחזירים `loop_detected`; אחרת `None`.
- הקריאות המוצעות עצמן לא נספרות; רק ההיסטוריה.

**3. קראי את `gated` ואת `ConsoleApproval`.** שימי לב שהדחייה היא חריגה, והמשגר של פרק 19 הופך
אותה לתוצאת שגיאה שהמודל קורא.

**4. מלאי את `TODO 2`** (`idempotent`):

- מחשבים מפתח עם `key_fn`.
- אם יש תוצאה שמורה תחת המפתח, מחזירים אותה עם `replayed: True`, בלי להריץ את הכלי.
- אחרת מריצים את הכלי, שומרים את התוצאה תחת המפתח, ומחזירים אותה.

**5. בדיקות של היום.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch20.py -q -k "loop or approval or idempotent"
```

</div>

## יום 39: נקודות שמירה, המשכה, זיכרון

**6. מלאי את `TODO 3`** (`run_with_checkpoints`):

- עם `resume_run_id`: טוענים מהחנות; ריצה חסרה היא `KeyError`; ריצה גמורה חוזרת כפי שהיא.
- בלי מזהה: חייבים לקבל `state`.
- שומרים פעם אחת לפני ההתחלה, מריצים את הלולאה עם `on_step=store.save`, שומרים את התוצאה ומחזירים.

**7. כל הבדיקות.** בדיקת הקריסה משתמשת בחריגה שיורשת מ־`BaseException`; קראי אותה לפני שתריצי.

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch20.py -q
```

</div>

**8. ההדגמה: קריסה אמיתית.** ההדגמה לא מדפיסה דבר עד הסוף, אז הזמן נמדד בשעון: הריצי את הפקודה
הראשונה, ספרי כארבע שניות (מספיק לקריאה אחת למודל ולשמירה אחריה), ולחצי Ctrl+C. ואז הריצי את
שתי הפקודות הבאות:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch20.reliability_demo "What changed in Kubernetes 1.36 and what should operators do?"
uv run --env-file .env python -m ch20.reliability_demo --list
uv run --env-file .env python -m ch20.reliability_demo --resume <run_id>
```

</div>

הפקודה `--list` מראה את הריצה עם `status: running` ואת מספר הצעדים שנשמרו; את מזהה הריצה מעתיקים
ממנה לפקודת `--resume`. אם הצעדים שנשמרו הם 0, לחצת מוקדם מדי: ההמשכה פשוט תתחיל מההתחלה. נסי
שוב וחכי קצת יותר.

**9. אישור ושליחה.** שאלי שאלה שמסתיימת בבקשה לשלוח מייל, ואז בדקי את תיבת היוצא:

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch20.reliability_demo "What changed in Kubernetes 1.36? Email me the answer."
Get-ChildItem ch20\state\outbox
```

</div>

ברוב הריצות המודל יבקש להפעיל `send_email`, והשער יציג את הארגומנטים המדויקים; אשרי עם `y`.
בתיבת היוצא צריך להופיע קובץ JSON אחד. הריצי שוב עם אותה שאלה בדיוק: ייתכן שהמודל ייתן את אותו
`idempotency_key` (או שוב ריק) וייתכן שלא. **בפתק:** מה קרה, ולמה המפתח חייב להגיע מהקוד (מזהה
הגיליון), לא מהמודל.

**10. זיכרון.** קובץ ההעדפות לא קיים עד שיוצרים אותו; ברירת המחדל עונה בעברית, עד חמישה משפטים.
צרי אותו עם ארבעת השדות (שדה לא מוכר מפיל את הטעינה):

<div dir="ltr" align="left">

```powershell
Set-Content ch20\state\preferences.json '{"name": "", "language": "en", "skip_topics": ["sports"], "max_sentences": 3}'
uv run --env-file .env python -m ch20.reliability_demo "What changed in Kubernetes 1.36?"
```

</div>

התשובה צריכה להתהפך לאנגלית ולהתקצר לשלושה משפטים לכל היותר. **בפתק:** מה היה קורה בלי כל אחד
מחמשת המנגנונים, במשפט לכל אחד.

**11. התחייבות.** התיקייה `ch20\state` (ריצות, תיבת יוצא, העדפות) לא נכנסת ל־Git:

<div dir="ltr" align="left">

```powershell
Add-Content .gitignore "ch20/state/"
git add .gitignore ch20 tests\test_ch20.py
git commit -m "Chapter 20: guardrails, approval, idempotency, checkpoints, memory"
```

</div>

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

## טעויות נפוצות ותיקונים

- **הגלאי סופר גם את הקריאה המוצעת.** הסבב הראשון של כל ריצה נעצר מיד עם `loop_detected`, והבדיקה
  מצפה ל־`None` על ארגומנטים חדשים. סופרים רק את ההיסטוריה, ומשווים אליה את ההצעה.
- **מילון הארגומנטים משמש כמפתח ישירות.** פייתון זורקת `TypeError: unhashable type`. המפתח הוא
  הזוג של שם הכלי והמחרוזת שמחזירה `canonical`.
- **`idempotent` מריץ את הכלי ורק אז בודק את החנות.** בתיבת היוצא יש שני קבצים במקום אחד. קודם
  `store.get`, ורק אם אין תוצאה שמורה מריצים ושומרים.
- **ההמשכה בונה `AgentState` חדש במקום להשתמש בטעון.** הבדיקה סופרת שני צעדים במקום שלושה, או
  שהשאלה מופיעה פעמיים בהיסטוריה. המצב שנטען מהחנות עובר ללולאה כפי שהוא; השעון ממשיך
  מהשניות השמורות.
- **`run_with_checkpoints` תופס את הקריסה.** הבדיקה שמצפה לחריגה נכשלת, ובאמת אין מה לתפוס: המצב
  האחרון כבר נשמר ב־`on_step`. נותנים לחריגה לעבור.
- **קובץ ההעדפות עם שדה לא מוכר.** הטעינה נופלת עם `TypeError` על ארגומנט לא צפוי. בקובץ רק
  ארבעת השדות של `UserPreferences`, באיות המדויק.

## רמזים

- הפונקציה `canonical` מחזירה את הארגומנטים כ־JSON עם מפתחות ממוינים: אותם ארגומנטים בסדר אחר הם
  אותו זוג.
- הפונקציה `run_with_checkpoints` מקבלת `**kwargs` ומעבירה אותם ללולאה (למשל `guard=`, `system=`).
- המצב נשמר כ־JSON שלם; `AgentState.from_json` משחזר גם את רשומות המעקב.
- בהדגמה, Ctrl+C הוא `KeyboardInterrupt`, שיורש מ־`BaseException` בדיוק כמו הקריסה המדומה בבדיקה;
  לכן הלולאה לא תופסת אותו, והמצב השמור נשאר כפי שהיה אחרי הסבב האחרון שהושלם.

## הפתרון

`solution/`. חמשת המנגנונים עובדים כי כולם נשענים על ההיסטוריה המפורשת ועל נקודות החיבור של
הלולאה, בלי לשנות אותה. `LoopDetector` קורא את זוגות הקריאה מההיסטוריה ולא מחזיק מצב משלו, ולכן
הוא עובד גם מיד אחרי המשכה. `run_with_checkpoints` שומר רק מה שהלולאה מוסרת ב־`on_step`, כלומר
סבבים שלמים, ולכן כל מצב שמור אפשר לשלוח חזרה למודל. `idempotent` בודק את החנות לפני שהוא מריץ,
ולכן ניסיון חוזר לא שולח; ו־`gated` זורק חריגה שהמשגר של פרק 19 כבר יודע להפוך לתוצאת שגיאה.

## מה התרגיל מדגים

- מעקות כקוד קטן בנקודות מוגדרות של הלולאה (`guard`, `on_step`, עטיפת כלים), בלי לשכתב אותה.
- אישור שמראה את הפעולה המדויקת; אידמפוטנטיות שמגינה על פעולה; נקודות שמירה שמגינות על ריצה.
- שלושה סוגי זיכרון עם חיים שונים, והארוך משפיע במקום אחד וקריא.

</div>
