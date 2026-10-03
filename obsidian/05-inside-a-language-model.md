---
direction: rtl
tags: [ai-course, book]
chapter: 5
---
# בתוך מודל שפה

- **טוקנים:** יחידת העבודה והתשלום. עברית יקרה יותר. סופרים עם כלי המודל, לא במילים.
- **ייצוג:** וקטור לכל טוקן, שמושפע מההקשר ומהסדר.
- **קשב:** סכום משוקלל ממיקומים אחרים. ציונים ממכפלה פנימית, משקלים מ־Softmax. לא הסבר.
- **Transformer:** בלוק של קשב ועוד, מוערם עשרות פעמים. בסוף לוגיט לכל טוקן באוצר המילים.
- **שלושה שלבי אימון:** מקדים (הטוקן הבא), כוונון להוראות, יישור. אף אחד לא מלמד „בדוק עובדות”.
- **שלושה מקומות למידע:** משקולות (קפואות, תאריך ידע), הקשר (עכשיו בלבד), מחוץ למודל (האפליקציה בוחרת). שיחה זוכרת כי מישהו שולח שוב.
- **שמות מודלים:** מדרג גודל ומחיר. ההתאמה נמדדת.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
count tokens   client.models.count_tokens(model=..., contents=text).total_tokens
usage after    interaction.usage.total_input_tokens / total_output_tokens / total_thought_tokens
my ratios      hebrew ____ chars/token   english ____ chars/token   code ____   json ____
attention toy  query 1, keys [1, 0], values [10, 2] -> weights [0.731, 0.269] -> output 7.848
three places   weights (frozen, cutoff) | context (this request) | outside (app decides what to send)
```

</div>

קישורים: [[04-minimal-math]] · [[06-generation-and-its-knobs]]
