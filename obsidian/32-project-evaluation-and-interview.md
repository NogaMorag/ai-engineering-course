---
direction: rtl
tags: [ai-course, book]
chapter: 32
---
# הערכה, ראיון והצגה של הפרויקט

- **ארבעה חלקים:** רלוונטיות (60, P@8 0.75, Spearman 0.5) · נאמנות (20, הסכמה 0.8) · קיבוץ (30 זוגות, P 0.9 /
  R 0.75) · הזרקה (5+, 1.0). לכל אחד: מה לא מוכח.
- **`make eval`** לפני כל שינוי ובסוף שבוע; `--offline` ב־CI בודק מבנה בלבד.
- **20 שאלות:** מערכת (1–10), החלטות (11–15), קנה מידה ועתיד (16–20). המספרים שלי: ___
- **קו״ח:** שלוש שורות עם X. **הדגמה:** הדוח, לא רק העיתון; מגבלות בקול.
- **יום 80:** רשימות, רטרוספקטיבה, החיפוש כפרויקט.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
eval      make eval  ->  docs/eval-latest.md  ->  paste into docs/eval.md with the date; README table = latest, not best
numbers   cost/issue from run-report.md; faithfulness agreement + kappa from eval; precision@8; partial-run rate from a week of reports
answer    what -> why -> alternative + cost -> evidence ("in my project: ...")
```

</div>

קישורים: [[31-project-milestones]]
