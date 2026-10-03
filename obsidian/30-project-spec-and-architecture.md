---
direction: rtl
tags: [ai-course, book]
chapter: 30
---
# מפרט וארכיטקטורה

- **הפיץ׳:** 8 עד 12 ידיעות לי, סיכום נאמן, למה חשוב לי, קישורים, „סוקר גם”, „המשך ל”, הקשר ל־3. סנטים,
  פעם אחת, שורד כשלים, מתעלם מהזרקות.
- **F1–F10 / N1–N7**, כל אחת עם בדיקה: עלות ≤ 0.25, ≤ 10 דק׳, כשל חלקי, הזרקה, סודות, בדיקות
  offline, גרסאות בגיליון.
- **9 שלבים:** איסוף K, חילוץ K, סיכום M, ציון M+K, קיבוץ K (שיכונים), מחקר A, הרכבה M, משלוח K, דוח K.
- **נתונים:** SQLite (articles, summaries, scores, clusters, issues, runs, deliveries); Chroma `story_memory`
  60 יום; `profile.yaml` בלי זהות.
- **החלטות:** לא RAG; Chroma רק לזיכרון; סוכן רק למחקר; LangGraph הרחבה; מהיר/חכם; Gmail SMTP; Actions.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
stages    collect -> extract -> summarize -> score -> group(+memory) -> research(top 3) -> compose -> deliver -> report
ids       article id = sha256(canonical url)[:16]; issue idempotency key = f"{date}:{channel}"
budgets   cost <= 0.25 USD/issue (target 0.10); run <= 10 min; research <= 6 steps / 90 s
versions  issue metadata: prompt_version, model_fast, model_smart, embedding_model, index_version
```

</div>

קישורים: [[29-portfolio-cv-presentation]] · [[31-project-milestones]]
