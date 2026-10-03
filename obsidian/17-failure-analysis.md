---
direction: rtl
tags: [ai-course, book]
chapter: 17
---
# ניתוח כשלים ודיבוג של מערכות AI

- **הערכה אומרת כמה. ניתוח כשלים אומר למה, ובאיזה סדר.**
- **חמש הזיות:** לא נתמך, סותר, מיושן, ציטוט מומצא, סירוב יתר. סימפטומים, לא סיבות.
- **קוראים בסדר הצינור:** נטען, אוחזר, נכנס להקשר, נענה, צוטט, נבדק. איפה הראיה נעלמה? (שמות
  השדות בלוח למטה.)
- **תהליך:** קידוד פתוח, קטגוריות, ספירה; העדיפות היא ספירה כפול חומרה. קוראים עשרה לפני שסופרים.
- **שלב לפני סימפטום:** טעינה, אחזור, הקשר, יצירה, אימות. סדר התיקונים: נתונים, אחזור, הנחיה,
  סכמה, מודל. הזול והמקומי קודם. אחד בכל פעם.
- **רגרסיה:** כל כשל הופך למקרה. `regressions.jsonl` בלי כפילויות.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
record    retrieved_paths -> context_paths -> answer, abstained -> citations, invalid_citations, cited_paths -> checks -> judge
tags      retrieval_miss | context_truncated | over_refusal | unsupported_answer | fabricated_citation | missing_key_fact | wrong_language | instruction_following | wrong_source_cited
classify  classify(record, case) -> [tags]  (expected sources vs retrieved_paths vs context_paths; checks by name)
rollup    rollup(tagged) -> (Counter by type, Counter by stage);  prioritize -> (type, count, count x severity)
run       python -m ch17.analyze results\dev-v1.jsonl --out results\analysis-v1.md --regressions regressions.jsonl
fix       one fix -> rerun -> compare -> next fix.   order: data, retrieval, context, prompt, schema, model
```

</div>

קישורים: [[16-evals]] · [[18-testing-ai-applications]]
