---
direction: rtl
tags: [ai-course, book]
chapter: 18
---
# בדיקות ליישומי AI

- **פירמידה:** יחידה (מזויפים), קלטות, חוזים, תכונות, שופט, חי. בדיקות מוכיחות קוד; הערכות מודדות
  מערכת.
- **קלטת:** מקליטים פעם אחת עם מפתח, משמיעים תמיד בלי; המפתח הוא גיבוב הבקשה כולה; החמצה היא
  שגיאה רועשת, לא קריאה לרשת.
- **חוזה:** צילום של הסכמה ושל הצהרות הכלים: נוצר, תואם, או נכשל עם diff; עדכון רק עם משתנה
  סביבה.
- **תכונות:** מה שכל פלט מקובל מקיים; גנרטור עם זרעים; הבודק חייב להסכים עם המחולל.
- **מדרגות:** מהיר תמיד וחינם; שופט בלילה; חי רק עם דגל ומפתח, אחרת דילוג עם סיבה. רק החי
  מדלג מעצמו.
- **CI:** שלושה jobs, סוד למפתח, תקציב טוקנים לבדיקה. שתי פקודות: בדיקות והערכה.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
record    $env:AI_COURSE_RECORD="1"; uv run --env-file .env pytest tests\test_ch18_examples.py
replay    client_for_tests(Path("tests/cassettes/x.jsonl")) -> ReplayClient; miss -> CassetteMiss
snapshot  assert_matches_snapshot("tool_declarations", tool_declarations(), TESTS_DIR / "snapshots")  update: AI_COURSE_UPDATE_SNAPSHOTS=1
property  article_summary_violations(data) == []   random_article_summary(rng, valid=False) -> defect
tiers     uv run pytest -q                      # fast, offline (add -m "not judge" once judge tests exist)
          uv run pytest -q -m judge             # nightly, paid
          uv run pytest -q -rs --live -m live   # weekly smoke, needs a key; -rs prints the skip reason
```

</div>

קישורים: [[17-failure-analysis]] · [[19-workflows-vs-agents]]
