---
direction: rtl
tags: [ai-course, book]
chapter: 10
---
# קריאה לכלים

- **קריאה היא הצעה.** המודל מייצר JSON לפי הסכמה; הקוד שלי מאמת, מריץ, מחזיר.
- **המחזור:** ממנו צעד `function_call` עם מזהה, שם וארגומנטים; ממני צעד `function_result` עם אותו
  מזהה קריאה והתוצאה. ההמשך דרך `previous_interaction_id`.
- **לולאה ביד:** עד 5 סבבים, כל הקריאות הממתינות בכל סבב, ספירת טוקנים לאורך הדרך.
- **מקבילי:** כל התוצאות בהודעה אחת. **שגיאה:** תוצאה עם `is_error`, לא קריסה.
- **משגר:** מילון סגור, Pydantic על הארגומנטים, רק http(s), לא מארחים פרטיים, זמן קצוב, חיתוך, ותוצאות
  הן נתונים.
- **סוכן יכול לעשות רק מה שהכלים שלו מאפשרים.** שליחה ומחיקה אינן כלים.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
declare   tools=[{"type":"function","name":..,"description":..,"parameters": clean_schema(Args.model_json_schema())}]
detect    pending = [s for s in interaction.steps if s.type == "function_call"]   # s.id, s.name, s.arguments
reply     input=[{"type":"function_result","call_id": s.id,"name": s.name,"result": json_text,"is_error": bool}]
          + previous_interaction_id=interaction.id
dispatch  TOOLS[name] (KeyError -> error result) -> Args.model_validate(arguments) -> func(**args.model_dump())
url       scheme in {http, https}; host not localhost/127./10./192.168./172.16-31./169.254.; timeout=10
choice    generation_config={"tool_choice": "auto" | "any" | "none" | {"allowed_tools": {...}}}
```

</div>

קישורים: [[09-structured-outputs]] · [[11-robust-clients]]
