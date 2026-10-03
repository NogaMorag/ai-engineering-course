---
direction: rtl
lang: he
---

<div dir="rtl" lang="he">

# תרגיל פרק 18 ונקודת ביקורת 4: חבילת בדיקות למסכם ול־`ask_notes`

**מטרה:** להשלים את פירמידת הבדיקות של הפרויקט: קלטות של תשובות אמיתיות שמושמעות בלי רשת, בדיקות
חוזה לסכמות ולהצהרות כלים, טענות תכונה על פלט לא־דטרמיניסטי, שלוש מדרגות עם סימונים ודילוג,
קובץ CI, ותקציב טוקנים.

**זמן משוער:** יום לימוד אחד (יום 35), כ־60 דקות בנייה. **ידע מקדים:** פרק 18, התרגילים של פרקים
11 ו־15, ומפתח API להקלטה (כמה קריאות בודדות).

## מה בתיקייה הזאת

| קובץ | תפקיד |
| --- | --- |
| `starter/recorder.py` | קלטת, `ReplayClient`, `RecordingClient` עם `TODO 1`, `client_for_tests` |
| `starter/contracts.py` | `assert_matches_snapshot` עם `TODO 2` |
| `starter/properties.py` | בודקי תכונות וגנרטור; מוכן |
| `starter/conftest.py` | הסימונים, הדגל `--live`, הדילוג, `token_budget`; מוכן. הולך ל־`tests\conftest.py` |
| `starter/test_examples.py` | בדיקת דוגמה לכל מדרגה; הולך ל־`tests\test_ch18_examples.py` |
| `starter/github-workflows-tests.yml` | שלושה jobs; הולך ל־`.github\workflows\tests.yml` |
| `tests/test_ch18.py` | חמש בדיקות של המנגנונים, בלי רשת |

## הצעדים

**1. חבילה, conftest ודוגמאות.**

<div dir="ltr" align="left">

```powershell
New-Item -ItemType File ch18\__init__.py -Force | Out-Null
Copy-Item path\to\exercises\ch18-testing\starter\recorder.py, path\to\exercises\ch18-testing\starter\contracts.py, path\to\exercises\ch18-testing\starter\properties.py ch18\
Copy-Item path\to\exercises\ch18-testing\starter\conftest.py tests\conftest.py
Copy-Item path\to\exercises\ch18-testing\starter\test_examples.py tests\test_ch18_examples.py
Copy-Item path\to\exercises\ch18-testing\tests\test_ch18.py tests\
New-Item -ItemType Directory .github\workflows -Force | Out-Null
Copy-Item path\to\exercises\ch18-testing\starter\github-workflows-tests.yml .github\workflows\tests.yml
```

</div>

אם כבר יש לך `tests\conftest.py`, מזגי: הסימונים, `pytest_addoption`, הדילוג ו־`token_budget`.

**2. מלאי את `TODO 1`** (`RecordingClient.complete`): מפתח, חיפוש בקלטת, קריאה ללקוח האמיתי רק
בהחמצה, שמירה, מונים.

**3. מלאי את `TODO 2`** (`assert_matches_snapshot`): נוצר, תואם, עודכן, או `SnapshotMismatch` עם diff.

**4. המדרגה המהירה, בלי מפתח.** ודאי שאין מפתח בסביבה (אל תשתמשי ב־`--env-file`):

<div dir="ltr" align="left">

```powershell
uv run pytest -q
```

</div>

הבדיקה המוקלטת מדלגת (אין קלטת עדיין), החיה מדלגת (אין דגל), הצילומים נוצרים ב־`tests\snapshots`.
הריצי שוב: הצילומים „matched”. מדדי את הזמן: פחות מעשר שניות.

**5. הקלטה.**

<div dir="ltr" align="left">

```powershell
$env:AI_COURSE_RECORD = "1"
uv run --env-file .env pytest tests\test_ch18_examples.py -q
Remove-Item Env:AI_COURSE_RECORD
uv run pytest -q
```

</div>

הקלטת ב־`tests\cassettes\summarize_cargo_lite.jsonl`. ההרצה השנייה משמיעה אותה בלי מפתח.

**6. קלטת ל־`ask_notes` (אופציונלי לנקודת הביקורת; הצעד הכבד של היום).** הוסיפי ל־`test_ch18_examples.py` בדיקה ששואלת שאלה אחת על שלושת פתקי
הדוגמה של פרק 15 (`ch15\data\sample-notes`; הם יציבים, בניגוד לפתקים שלך) דרך `run(...)`. כאן יש
שתי קריאות רשת להקליט, לא אחת: התשובה, וגם השיכונים של הקטעים ושל השאלה.

- התשובה: `client_for_tests(...)` עם קלטת חדשה, כמו במסכם.
- השיכונים: `FakeEmbedder` לא מתאים, כי הוא משנה את האחזור ולכן את ההקשר שהתשובה הוקלטה איתו.
  במקום זה `CachedEmbedder` (פרק 12) עם קובץ מטמון בתוך `tests\cassettes\`, שנכנס ל־Git. בהקלטה
  המודל הפנימי הוא `GeminiEmbedder()`; בהשמעה אסור ליצור אותו (הוא דורש מפתח כבר בבנייה), אז
  במקומו מחלקה קטנה עם אותו `model` ואותו `dims` ו־`embed` שזורק שגיאה. כל טקסט שלא במטמון הוא
  אז החמצה רועשת, בדיוק כמו `CassetteMiss`.

<div dir="ltr" align="left">

```python
from ch12.embedder import CachedEmbedder, GeminiEmbedder
from ch15.answer import RESPONSE_FORMAT as GROUNDED_FORMAT
from ch15.cli import run
from ch18.properties import grounded_answer_violations
from ch18.recorder import recording_enabled

SAMPLE_NOTES = TESTS_DIR.parent / "ch15" / "data" / "sample-notes"


class ReplayOnlyEmbedder:
    model, dims = "gemini-embedding-2", 768

    def embed(self, texts):
        raise AssertionError(f"{len(texts)} texts are not in the embedding cache; record with AI_COURSE_RECORD=1")


def test_recorded_ask_notes_answer_is_grounded(tmp_path):
    (TESTS_DIR / "cassettes").mkdir(exist_ok=True)
    client = client_for_tests(TESTS_DIR / "cassettes" / "ask_notes_retries.jsonl")
    inner = GeminiEmbedder() if recording_enabled() else ReplayOnlyEmbedder()
    embedder = CachedEmbedder(inner, TESTS_DIR / "cassettes" / "embeddings.sqlite")
    answer, _ = run("which failures are safe to retry?", SAMPLE_NOTES, client=client, embedder=embedder, store_dir=tmp_path, mode="hybrid", k=3)
    assert not answer.abstained
    data = {"answer": answer.text, "citations": answer.citations, "supported": answer.supported}
    assert grounded_answer_violations(data, n_sources=len(answer.sources)) == []
```

</div>

הקליטי מיד עם ארבע הפקודות מצעד 5; ההרצה האחרונה שבהן, בלי מפתח, משמיעה גם את השיכונים וגם את
התשובה. באותה הזדמנות הוסיפי ל־`test_schema_and_tool_contracts` צילום שלישי, לסכמה של
`GroundedAnswer`:

<div dir="ltr" align="left">

```python
assert_matches_snapshot("grounded_answer_schema", GROUNDED_FORMAT["schema"], snapshots)
```

</div>

רשמי בפתק למה המטמון של פרק 12 הוא בעצם קלטת, ומה ההבדל היחיד (המפתח שלו הוא המודל והטקסט,
לא הבקשה כולה).

**7. המדרגה החיה.** הדגל `-rs` מדפיס את סיבת הדילוג.

<div dir="ltr" align="left">

```powershell
uv run pytest -q -rs --live -m live                       # skips: no key
uv run --env-file .env pytest -q -rs --live -m live       # runs, within the token budget
```

</div>

**8. CI.** דחפי את `.github\workflows\tests.yml` למאגר `ai-course` עם `git push`, ובדקי שה־job
`fast` ירוק. הוסיפי את `GEMINI_API_KEY` כ־secret במאגר (Settings, Secrets and variables, Actions)
רק אם את רוצה שהמדרגות המתוזמנות ירוצו; הן עולות כסף.

**9. התחייבות.** `git commit -m "Chapter 18: cassettes, contracts, properties, test tiers, CI"`.
הקלטות והצילומים נכנסים; `__pycache__` לא.

## פלט צפוי (צורה)

<div dir="ltr" align="left">

```text
uv run pytest -q
..........................................................................s.s..  [100%]
140 passed, 2 skipped in 6.8s

uv run pytest -q -rs --live -m live
s                                                                              [100%]
SKIPPED [1] tests/conftest.py:42: GEMINI_API_KEY (or GOOGLE_API_KEY) is not set
1 skipped, 141 deselected in 0.3s
```

</div>

המספרים להמחשה; מספר הבדיקות ומספר השורה ב־`conftest.py` אצלך יהיו אחרים.

## רשימת בדיקה

- [ ] אותה בקשה פעמיים: הקלטה אחת והשמעה אחת; בקשה שונה בתו אחד היא מפתח חדש.
- [ ] החמצת קלטת זורקת `CassetteMiss` עם ההוראה להקלטה, ולא קוראת לרשת.
- [ ] צילום: נוצר, תואם, נכשל עם diff, מתעדכן רק עם משתנה הסביבה.
- [ ] המדרגה המהירה: פחות מעשר שניות, בלי מפתח, כולל שתי הקלטות, מטמון השיכונים ושלושה צילומים.
- [ ] `--live` מדלג בלי מפתח ורץ איתו, בתוך `token_budget`.
- [ ] `tests.yml` במאגר, ו־`fast` ירוק ב־GitHub.

## טעויות נפוצות ותיקונים

- **ההקלטה לא קורית.** עם `AI_COURSE_RECORD` דלוק הבדיקה עדיין מדלגת על `CassetteMiss`. ההקלטה
  דורשת גם מפתח: הריצי עם `--env-file .env`, ובדקי ש־`Remove-Item` לא רץ לפני pytest.
- **החמצת קלטת אחרי שינוי קטן בהנחיה.** ערכת את `SYSTEM` או את הסכמה, ופתאום `CassetteMiss`. כך
  המנגנון אמור לעבוד, כי המפתח הוא גיבוב הבקשה כולה; הקליטי מחדש וקראי את ה־diff של הקלטת
  ב־Git לפני שאת מתחייבת.
- **צילום שנכשל כשלא התכוונת לשנות חוזה.** `SnapshotMismatch` עם diff של תיאור או שדה. זה בדיוק
  שינוי חוזה: קראי את ה־diff, ואשרי עם `AI_COURSE_UPDATE_SNAPSHOTS=1` רק אם התכוונת לכך.
- **הבדיקה החיה רצה ב־CI ונכשלת ב־401.** ה־job `fast` אדום עם שגיאת אימות. בדקי ש־`tests\conftest.py`
  הוא הקובץ מהתרגיל (הדילוג ב־`pytest_collection_modifyitems`) ושהבדיקה מסומנת `@pytest.mark.live`.
- **המדרגה המהירה איטית מעשר שניות.** הזמן נמדד ב־20 שניות ומעלה. הריצי עם `--durations=5` ומצאי
  מה איטי; לרוב זו בדיקה שבונה אינדקס על הפתקים שלך במקום על `sample-notes`, או קריאה לרשת
  שלא שמת לב אליה.
- **`PytestUnknownMarkWarning` על `live` או `judge`.** אזהרה בכל הרצה. `pytest_configure` ב־`conftest.py`
  רושם את הסימונים; ודאי שהקובץ נמצא ב־`tests\` ולא בשורש.

## רמזים

- `Completion` הוא dataclass, אז `asdict` ו־`Completion(**entry["completion"])` הולכים הלוך ושוב.
- `difflib.unified_diff` מקבל רשימות שורות; `splitlines(True)` שומר את תווי השורה החדשה.
- `pytest_collection_modifyitems` רץ אחרי האיסוף; להוסיף `skip` לפריט זול יותר מלמחוק אותו.
- `from conftest import live_enabled` עובד כי pytest מוסיף את `tests\` לנתיב כשיש שם `conftest.py`.

## הפתרון

`solution/` מכיל את כל הקבצים. הפונקציה `client_for_tests` משמיעה כברירת מחדל ומקליטה רק כששני
תנאים מתקיימים, משתנה הסביבה ומפתח, כדי שאף הרצה רגילה לא תגיע לרשת בטעות. המפתח של הקלטת הוא
גיבוב של הבקשה כולה ולא של ההנחיה בלבד, כדי ששינוי בסכמה או בטמפרטורה לא יקבל תשובה ישנה בשקט.
הפונקציה `assert_matches_snapshot` מחזירה מחרוזת (`created`, `matched` או `updated`) במקום `None`,
כדי שבדיקת המנגנון עצמו תוכל לטעון על ההרצה הראשונה.

## מה התרגיל מדגים

- פירמידה שלמה: מזויפים, קלטות, חוזים, תכונות, שופט, חי, וכל שכבה עם מה שהיא מוכיחה.
- „להקליט פעם אחת, להשמיע לנצח”: מהירות של מזויף עם אמינות של תשובה אמיתית.
- חוזים לדברים שהמודל קורא: שינוי הוא החלטה עם diff.
- CI שלא מוציא כסף בטעות: מדרגות, סודות, דילוג עם סיבה, תקציב.

</div>
