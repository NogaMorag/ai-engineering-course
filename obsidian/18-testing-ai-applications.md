---
direction: rtl
tags: [ai-course, book]
chapter: 18
---
# בדיקות ליישומי AI

- **פירמידה:** יחידה (מזויפים), קלטות, חוזים, תכונות, שופט, חי. בדיקות מוכיחות קוד; הערכות מודדות
  מערכת.
- **קלטת:** `RecordingClient` עם מפתח פעם אחת; `ReplayClient` תמיד; מפתח = גיבוב הבקשה; החמצה =
  `CassetteMiss`.
- **חוזה:** `assert_matches_snapshot(name, value, dir)`: נוצר, תואם, או נכשל עם diff; עדכון רק עם משתנה
  סביבה.
- **תכונות:** מה שכל פלט מקובל מקיים; גנרטור עם זרעים; הבודק חייב להסכים עם המחולל.
- **מדרגות:** מהיר (תמיד, חינם) / `judge` (לילה) / `live` עם `--live` ומפתח, אחרת דילוג עם סיבה.
- **CI:** שלושה jobs, סוד למפתח, `token_budget`. שתי פקודות: test ו־eval.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
record    $env:AI_COURSE_RECORD="1"; uv run --env-file .env pytest tests\test_ch18_examples.py
replay    client_for_tests(Path("tests/cassettes/x.jsonl")) -> ReplayClient; miss -> CassetteMiss
snapshot  assert_matches_snapshot("tool_declarations", tool_declarations(), TESTS_DIR / "snapshots")  update: AI_COURSE_UPDATE_SNAPSHOTS=1
property  article_summary_violations(data) == []   random_article_summary(rng, valid=False) -> defect
tiers     uv run pytest -q            # fast, offline
          uv run pytest -q -m judge   # nightly, paid
          uv run pytest -q --live -m live   # weekly smoke, needs a key
```

</div>

קישורים: [[17-failure-analysis]] · [[19-workflows-vs-agents]]
