---
direction: rtl
tags: [ai-course, book]
chapter: 22
---
# תצפיתיות (Observability)

- **לוג = מה קרה. מדד = כמה לאורך זמן. מעקב = ריצה אחת, שלב אחרי שלב.**
- **span:** trace_id, span_id, parent_id, name, kind, model, tokens (in/out/cached), cost_usd, duration,
  ttft, attempts, status, error, prompt_chars + prompt_sha256.
- **Tracer:** `with tracer.span(name, kind)`; מחסנית לקינון; שורת JSONL בסיום; חריגה = error ונזרקת.
- **עטיפות:** `TracingClient(client, tracer, model=)`, `TracingAgentBackend`, `traced_tools`.
- **דוח:** לפי `kind:name`: calls, errors, tokens, cost, p50, p95; מודל בלי מחיר = 0 גלוי.
- **הסתרה היא החלטה:** `record_text=False` ברירת מחדל; מפתחות ארגומנטים בלבד.
- **התרעות:** עלות ×2, כישלון בשלב קריטי, קפיצה בהימנעות.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
tracer    Tracer("out/traces.jsonl", record_text=False)   with tracer.span("stage"): ...   tracer.event("name", "detail")
llm       TracingClient(inner, tracer, model="gemini-3.5-flash-lite", stage="summarize").complete(...)
agent     TracingAgentBackend(backend, tracer, model=...);  traced_tools(tools, tracer)
cost      estimate_cost(model, input_tokens_excl_cached, output_tokens, cached_tokens=...)  PRICES per 1M (in, out, cached)
report    python -m ch22.report out/traces.jsonl   -> per kind:name table + total + unpriced models + events + errors
```

</div>

קישורים: [[21-frameworks-and-protocols]] · [[23-latency-cost-reliability]]
