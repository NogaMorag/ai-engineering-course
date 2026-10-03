---
direction: rtl
tags: [ai-course, book]
chapter: 6
---
# יצירת טקסט והכפתורים שלה

- **הלולאה:** לוגיטים, התפלגות, בחירת טוקן, הוספה; עד טוקן סיום, גבול פלט או רצף עצירה.
- **טמפרטורה:** נמוכה לעקביות (סיווג, חילוץ, קוד), גבוהה לגיוון. אפס אינו אמת ואינו דטרמיניזם מובטח.
- **גבול פלט:** קוטע בלי אזהרה. תמיד בודקים סטטוס. חלון ההקשר הוא תקציב משותף.
- **חשיבה:** קונה היסק, עולה זמן וכסף. הרמה הנמוכה ביותר שעוברת הערכה.
- **זמן ועלות:** קלט במקביל (זול, מהיר), פלט סדרתי (איטי, יקר). קידומת חוזרת: מטמון.
- **מגבלות:** הזיה, תאריך ידע, חשבון, סחף, חנופה, רגישות לניסוח, אי־דטרמיניזם, הזרקה. לכל אחת
  תפקיד לקוד.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
knobs    generation_config={"temperature": 0.0..2.0, "top_p": ..., "seed": 7, "max_output_tokens": N,
                            "thinking_level": "minimal"|"low"|"medium"|"high", "stop_sequences": [...]}
status   interaction.status -> "completed" | "incomplete" (cut by max_output_tokens) | "failed" | ...
usage    total_input_tokens | total_output_tokens | total_thought_tokens | total_cached_tokens
my runs  classification distinct ratio at T=0/0.7/1.0: __/__/__   creative: __/__/__
         thinking minimal vs high on the puzzle: thought tokens __ vs __, latency __ s vs __ s
```

</div>

קישורים: [[05-inside-a-language-model]] · [[07-the-interactions-api]]
