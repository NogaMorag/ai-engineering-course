---
direction: rtl
tags: [ai-course, book]
chapter: 31
---
# תשע אבני הדרך

- **שיטה:** בדיקות קודם; `--offline` כל ערב; ריצה אמיתית כל יום מ־M2; commit ופתק לכל אבן.
- **M1** מקורות ומסד (50+ כתבות, אפס כפילויות). **M2** סיכומים ודירוג (20 תוויות). **M3** אשכולות וזיכרון (סף,
  הערת החלטה). **M4** צינור עם תוצרים והמשכה, סוכן מחקר תחום. **M5** הרכבה, רינדור, משלוח פעם אחת.
- **M6** סט זהב, רתמה, שופט, ניתוח כשלים, רגרסיה. **M7** כאוס, גיבוי, עלות לגיליון. **M8** הזרקה, סודות,
  זרימת נתונים. **M9** Actions ב־07:00, README, docs. **אופציונלי:** שער אישור ב־LangGraph.
- **כשנתקעים:** הבדיקה עד הסוף; `--stop-after`; הייחוס לקריאה בלבד; פתק.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
loop      uv run pytest -q  ->  implement  ->  uv run morning-brief run --offline  ->  real run --stop-after <stage>
real      uv run --env-file .env morning-brief run [--stop-after collect|extract|summarize|score|group|research|compose] [--resume] [--channels file,email]
eval      uv run --env-file .env python -m evals.run_eval --out docs/eval-latest.md      (offline: --offline)
tests     tests/test_sources_store.py (M1) · test_extract_summarize_rank.py (M1-M2) · test_cluster_memory_research.py (M3-M4)
          test_compose_render_pipeline.py (M4-M5) · test_evals.py (M6)
```

</div>

קישורים: [[30-project-spec-and-architecture]] · [[32-project-evaluation-and-interview]]
