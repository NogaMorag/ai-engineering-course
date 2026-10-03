---
direction: rtl
tags: [ai-course, book]
chapter: 22
---
# תצפיתיות (Observability)

- **לוג:** מה קרה. **מדד:** כמה, לאורך זמן. **מעקב:** ריצה אחת, שלב אחרי שלב.
- **span:** מזהי ריצה והורה, שם וסוג, מודל, טוקנים (קלט, פלט, מטמון), עלות, זמן, ניסיונות, סטטוס,
  שגיאה, וטביעת אצבע של ההנחיה במקום הטקסט.
- **כלי המעקב:** מנהל הקשר לכל span; מחסנית לקינון; שורת JSONL בסיום; חריגה מסומנת ונזרקת הלאה.
- **עטיפות:** עוטפים את הלקוח, את הקצה האחורי של הסוכן ואת הכלים; לא משנים שורה בלולאה.
- **דוח:** לכל סוג ושם: קריאות, שגיאות, טוקנים, עלות, p50 ו־p95; מודל בלי מחיר מופיע כאפס גלוי.
- **הסתרה היא החלטה:** בלי טקסט כברירת מחדל; מפתחות הארגומנטים בלבד; הקלטה מלאה רק בדיבוג מקומי.
- **התרעות:** עלות פי שניים מהממוצע, כישלון בשלב קריטי, קפיצה בהימנעות.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
span      trace_id span_id parent_id name kind started_at duration_ms status | model input_tokens output_tokens cached_tokens cost_usd ttft_ms attempts completion_status error prompt_chars prompt_sha256
tracer    Tracer("out/traces.jsonl", record_text=False)   with tracer.span("stage"): ...   tracer.event("name", "detail")
llm       TracingClient(inner, tracer, model="gemini-3.5-flash-lite", stage="summarize").complete(...)
agent     TracingAgentBackend(backend, tracer, model=...);  traced_tools(tools, tracer)
cost      estimate_cost(model, input_tokens_excl_cached, output_tokens, cached_tokens=...)  PRICES per 1M (in, out, cached)
report    python -m ch22.report out/traces.jsonl   -> per kind:name table + total + unpriced models + events + errors
```

</div>

קישורים: [[21-frameworks-and-protocols]] · [[23-latency-cost-reliability]]
