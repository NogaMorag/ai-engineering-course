---
direction: rtl
tags: [ai-course, book]
chapter: 16
---
# הערכות (Evals)

- **הדגמה בוחרת, זוכרת, מתיישנת.** הערכה: ציפיות מראש, ספירה, חזרה.
- **מקרה:** שאלה ועוד ציפייה שנכתבה מראש (שדות הציפייה בלוח למטה). קטגוריות: ישיר, ניסוח,
  רב־קפיצות, ללא תשובה, עוין, עברית.
- **סט פיתוח 20, סט בדיקה 10.** קבוצות ניסוח באותו צד. עריכת הנחיה היא אימון.
- **קוד בודק:** הימנעות, ציטוט מומצא, יש ציטוט, מונח, אסור, מקור, שפה. **שופט:** נאמן, נכונות 0–2.
- **כיול:** 10 תוויות אנושיות, הסכמה וקאפה. שופט „תמיד כן” מקבל הסכמה 80 אחוז וקאפה 0. הטיות:
  מיקום (החלפת סדר), אורך, העדפה עצמית.
- **דוח:** מונה ומכנה לפי קטגוריה, הפכפכים, עלות. **השוואה:** מה תוקן, מה נשבר. סט הבדיקה פעם אחת.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
cases     Case(id, question, category, group, split, expected)   validate_cases() -> [] before any call
expect    Expectation(answerable, must_mention_any, must_not_mention, source_paths, reference)
checks    run_checks(case, answer=, abstained=, citations=, invalid_citations=, cited_paths=) -> [CheckResult]
judge     FaithfulnessJudge(client).judge(q, sources_text, answer, reference) -> Verdict(faithful, correctness, reasoning)
calibrate agreement(judge, human); cohens_kappa(judge, human)   position_bias_probe(prefer, a, b)["consistent"]
kappa     observed = fraction equal; expected = sum over labels of p_a(label) * p_b(label); kappa = (observed - expected) / (1 - expected)
run       python -m ch16.run_eval run --notes-dir .. --split dev --prompt v1|v2 [--judge] [--repeats 3] --out results\x.jsonl
compare   python -m ch16.run_eval compare results\dev-v1.jsonl results\dev-v2.jsonl   -> deltas, fixed, broken
```

</div>

קישורים: [[15-rag-end-to-end]] · [[17-failure-analysis]]
