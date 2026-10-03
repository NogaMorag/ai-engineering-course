---
direction: rtl
tags: [ai-course, book]
chapter: 17
---
# ניתוח כשלים ודיבוג של מערכות AI

- **הערכה = כמה. ניתוח כשלים = למה, ובאיזה סדר.**
- **חמש הזיות:** לא נתמך, סותר, מיושן, ציטוט מומצא, סירוב יתר. סימפטומים, לא סיבות.
- **מעקב בסדר הצינור:** documents, chunks, retrieved, context, prompt_variant, answer, checks. איפה
  הראיה נעלמה?
- **תהליך:** קידוד פתוח, קטגוריות, ספירה, עדיפות = ספירה × חומרה. קוראים עשרה לפני שסופרים.
- **שלב לפני סימפטום:** אחזור, הקשר, הנחיה, סכמה, מודל. הזול והמקומי קודם. אחד בכל פעם.
- **רגרסיה:** כל כשל הופך למקרה. `regressions.jsonl` בלי כפילויות.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
tags      retrieval_miss | context_truncated | over_refusal | unsupported_answer | fabricated_citation | missing_key_fact | wrong_language | instruction_following | wrong_source_cited
classify  classify(record, case) -> [tags]  (expected sources vs retrieved_paths vs context_paths; checks by name)
rollup    rollup(tagged) -> (Counter by type, Counter by stage);  prioritize -> (type, count, count x severity)
run       python -m ch17.analyze results\dev-v1.jsonl --out results\analysis-v1.md --regressions regressions.jsonl
fix       one fix -> rerun -> compare -> next fix.   order: data, retrieval, context, prompt, schema, model
```

</div>

קישורים: [[16-evals]] · [[18-testing-ai-applications]]
