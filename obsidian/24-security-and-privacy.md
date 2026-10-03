---
direction: rtl
tags: [ai-course, book]
chapter: 24
---
# אבטחה ופרטיות

- **הזרקה:** ישירה (מהמשתמשת) או עקיפה (כתבה, דף, תוצאת כלי, תיאור MCP). הנזק מוגבל במה שהכלים
  מאפשרים.
- **גבולות אמון:** הוראות מול נתונים, מודל מול עולם, מערכת מול קוראת, מערכת מול ספק. ההנחיה מבקשת,
  הקוד אוכף.
- **הפלט הוא קלט לא מהימן:** קישורים מהמקור בלבד, בלי HTML, בלי הדים; בריחה בתבנית.
- **מסננים לא מוכיחים.** קוד מבטיח מה שהוא בודק; ההערכה (5 מקרי הזרקה) מודדת את השאר.
- **סודות:** קובץ הסביבה מחוץ ל־Git, סוד ב־CI, רוטציה ולא מחיקה, ביקורת על כל ההיסטוריה.
- **פרטיות:** מזעור, מדיניות הספק (בשכבה החינמית התוכן עשוי לשמש לשיפור המוצרים), שימור עם מחיקה,
  הסתרה בלוגים, הערת זרימת נתונים.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
policy    check_output(text, source_text=, allowed_hosts=) -> PolicyResult(violations, foreign_links); strip_foreign_links(...)
lab       python -m ch24.injection_lab          poisons: direct | hidden (HTML comment) | link
eval      python -m ch24.injection_eval         data/injection_cases.jsonl: must_not_contain / must_contain_any
secrets   python -m ch24.secrets_audit .        tree + git log -p --all; masked previews; exit 1 on findings
redact    redact_text(s): [key] [email] [id] [phone]
```

</div>

קישורים: [[23-latency-cost-reliability]] · [[25-deployment-and-scheduling]]
