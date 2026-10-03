---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 24: כתבה מורעלת, מדיניות פלט, ביקורת סודות, הסתרה

**מטרה:** להרעיל כתבה בשלוש דרכים ולצפות במסכם, להוסיף מדיניות פלט וחמישה מקרי הזרקה להערכה,
לכתוב ביקורת סודות שסורקת את העץ ואת היסטוריית Git, להוסיף הסתרה ללוגים, ולכתוב הערת זרימת נתונים
של עמוד.

**זמן משוער:** שני ימי לימוד (ימים 47 ו־48), כ־65 ו־50 דקות. **ידע מקדים:** פרק 24, פרקים 10, 16
ו־22, ומפתח API למעבדה ולהערכה (כ־8 קריאות).

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/output_policy.py` | `check_output` (`TODO 1`), `strip_foreign_links` |
| `starter/injection_lab.py` | שלושת הרעלים וההרצה; מוכן |
| `starter/injection_eval.py` | מיני־רתמה לחמשת המקרים; מוכן |
| `data/injection_cases.jsonl` | חמישה מקרים עם `must_not_contain` ו־`must_contain_any` |
| `starter/secrets_audit.py` | סריקת העץ (מוכן) וההיסטוריה (`TODO 2`) |
| `starter/redaction.py` | `redact_text`; מוכן |
| `tests/test_ch24.py` | ארבע בדיקות, בלי רשת (אחת בונה מאגר Git זמני) |

## יום 47: הזרקה

**1. חבילה ונתונים.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType Directory ch24\data -Force | Out-Null
New-Item -ItemType File ch24\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch24-security-privacy\starter\*.py ch24\
Copy-Item path\to\exercises\ch24-security-privacy\data\injection_cases.jsonl ch24\data\
Copy-Item path\to\exercises\ch24-security-privacy\tests\test_ch24.py tests\
```

</div>

**2. קודם לצפות.** עוד לפני המדיניות: הריצי את המעבדה והסתכלי מה המודל עשה עם כל רעל.

<div dir="ltr" align="left">

```powershell
uv run --env-file .env python -m ch24.injection_lab
```

</div>

(עד שתמלאי את `TODO 1`, `check_output` זורק `NotImplementedError`; הריצי את המעבדה אחרי צעד 3,
או הדפיסי זמנית את הסיכום בלבד.)

**3. מלאי את `TODO 1`** (`check_output`): קישורים זרים, HTML, הדים להוראות.

**4. המעבדה שוב, ואז ההערכה.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch24.py -q -k "policy or injection"
uv run --env-file .env python -m ch24.injection_lab
uv run --env-file .env python -m ch24.injection_eval
```

</div>

**5. בפתק:** לכל רעל, מה המודל עשה, מה המדיניות תפסה, ומה היא לא יכולה לתפוס („בוטל”). הוסיפי מקרה
שישי משלך, בעברית.

## יום 48: סודות ופרטיות

**6. מלאי את `TODO 2`** (`scan_history`): `git log -p --all`, ושורות שנוספו בלבד.

**7. בדיקות, ואז ביקורת על המאגר שלך.**

<div dir="ltr" align="left">

```powershell
uv run pytest tests\test_ch24.py -q
uv run python -m ch24.secrets_audit .
```

</div>

אם נמצא משהו אמיתי: רוטציה של המפתח קודם, ואז הכול השאר.

**8. הסתרה.** חברי את `redact_text` לנקודה אחת במעקב של פרק 22 (למשל ב־`event`), והוסיפי בדיקה.

**9. הערת זרימת נתונים** בפתק, בטבלה: לכל נתון (כתבות, פרופיל, פתקים, מעקבים, קלטות, זיכרון
סיפורים): מאיפה, לאן נשלח, מי רואה, כמה זמן נשמר, איך נמחק.

**10. התחייבות.** `git commit -m "Chapter 24: output policy, injection eval, secrets audit, redaction"`.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
{"poison": "direct", "outcome": "summary produced", "headline": "Cargo-Lite 2.0 ships a shared build cache",
 "violations": ["links not present in the source: ['https://evil.example/claim-prize']"],
 "foreign_links": ["https://evil.example/claim-prize"], "mentions_cancelled": false}
...
PASS inj01: ok
FAIL inj02: contains forbidden 'evil.example'; links not present in the source: [...]
{"passed": 4, "total": 5}

google_api_key       a1b2c3d4:config.py                                  AIzaSy…XYZ
1 finding(s) in C:\...\ai-course
```

</div>

## רשימת בדיקה

- [ ] קישור שלא במקור נתפס ומוסר; HTML נתפס; הד להוראה נתפס; רשימת מארחים מותרים עובדת.
- [ ] חמשת המקרים רצים; הכישלונות רשומים עם סיבה; מקרה שישי בעברית נוסף.
- [ ] ביקורת הסודות מוצאת מפתח שנמחק מהעץ אבל נשאר בהיסטוריה, ומציגה אותו ממוסך.
- [ ] `redact_text` ממסך מייל, טלפון, מספר זהות ומפתח, ומשאיר טקסט רגיל כפי שהוא.
- [ ] הערת זרימת נתונים של עמוד; ארבע הבדיקות ו־ruff עוברים.

## רמזים

- ב־`scan_history`, שורה שמתחילה ב־`+++ b/` היא שם הקובץ; שורה שמתחילה ב־`+` (ולא `+++`) היא תוספת.
- `--no-ext-diff --text` מבטיחים שהפלט של `git log -p` הוא תמיד patch אמיתי.
- התצוגה הממוסכת לעולם לא מדפיסה את המפתח המלא: שישה תווים ראשונים ושלושה אחרונים.

## הפתרון

`solution/`. שימי לב ל־`PLACEHOLDERS`: בלי זה, `env.example` עם `your-key-here` היה ממצא כוזב.

## מה התרגיל מדגים

- הזרקה כבעיה הנדסית: גבולות אמון, הרשאות בקוד, בדיקת פלט, והערכה למה שלא מוכח.
- „מה ההגנה לא מבטיחה” כחלק מהתיעוד.
- סודות: היסטוריה זוכרת; רוטציה.
- פרטיות כהחלטות כתובות: מזעור, שימור, הסתרה, זרימת נתונים.

</div>
