---
direction: rtl
tags: [ai-course, book]
chapter: 7
---
# ממשק ה-Interactions

- **בקשה:** מודל, קלט, הוראות מערכת, הגדרות; בהמשך כלים, סכמה, הזרמה.
- **תשובה:** סטטוס קודם, ואז טקסט. צעדים הם המקור. שימוש בכל תשובה.
- **שני ערוצים:** הוראות המערכת של האפליקציה; הקלט של המשתמשת והנתונים. סמכות, לא אבטחה.
- **שיחה:** היסטוריה מפורשת (אני שולחת הכול, אני שולטת) או מצב בצד השרת (מזהה קודם, הספק שומר).
- **עלות:** היסטוריה גדלה בכל סיבוב. מדפיסים טוקני קלט לכל סיבוב.
- **SDK:** עוטף HTTP ונותן טיפוסים. עלות ושגיאות שלי.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
create   client.interactions.create(model, input, system_instruction, generation_config, tools, response_format,
                                    stream, previous_interaction_id, store)
read     interaction.status -> completed | incomplete | requires_action | failed
         interaction.output_text | interaction.steps[i].type | interaction.usage.total_input_tokens
history  [{"type":"user_input","content":[{"type":"text","text":...}]},
          {"type":"model_output","content":[{"type":"text","text":...}]}, ...]
server   previous_interaction_id=first.id   store=False to avoid storing
```

</div>

קישורים: [[06-generation-and-its-knobs]] · [[08-prompt-design-as-specification]]
