---
direction: rtl
tags: [ai-course, book]
chapter: 9
---
# פלט מובנה

- **ארבע רמות של „תקין”:** נפרס, תואם סכמה, מקיים כללים, נאמן למקור. שרת, שרת, הקוד שלי, הערכה.
- **מודל Pydantic אחד:** סכמה לבקשה (`model_json_schema`, בלי `title`), אימות לתשובה
  (`model_validate_json`).
- **מובטח:** צורה כש־`completed`. **לא מובטח:** ספירות ומילים שהסכמה לא מבטאת, ואמת.
- **קטוע לא מתקנים.** `incomplete` = להגדיל את המגבלה.
- **ניסיון תיקון אחד** עם הודעת המאמת, ואז ויתור בקול. אף פעם לא אובייקט חלקי.
- **סכמה טובה:** שטוחה, תיאור = כלל, enum לרשימות סגורות, סדר = חשיבה, מוצא מכובד.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
request   response_format={"type":"text","mime_type":"application/json","schema": clean_schema(Model.model_json_schema())}
validate  Model.model_validate_json(interaction.output_text)   -> ValidationError on parse / schema / rule
rules     @model_validator(mode="after")  -> raise ValueError("exact rule in words")
status    interaction.status == "incomplete"  -> raise, do not repair; raise max_output_tokens
repair    original prompt + "rejected by the validator: <error>" + previous output -> ONE more call
design    flat, description=rule, Literal -> enum, is_article first, bounded lists
```

</div>

קישורים: [[08-prompt-design-as-specification]] · [[10-tool-calling]]
