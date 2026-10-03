---
direction: rtl
tags: [ai-course, book]
chapter: 23
---
# זמן תגובה, עלות ואמינות

- **מדידה:** p50, p95, TTFT; אחוזון לפי דרגה; עשר הרצות = צורה, לא אמת.
- **עלות:** in × 0.30 + out × 2.50 + cached × 0.075 (Flash-Lite, למיליון). פלט יקר פי 8. אצווה חצי.
- **ידיות לפי סדר:** מודל, מטמון (קידומת יציבה), פלט קצר, אצווה, מקבול, חשיבה. ציון יורד = קו אדום.
- **BudgetGuard(max_usd).charge(model, completion)** עוצר באמצע.
- **resilient_call:** deadline כולל, ניסיונות תחומים, מפסק (סגור/פתוח/חצי), גיבוי מפורש, הידרדרות
  ששומרת חוזה. `Outcome.source`.
- **בדיקות:** FakeClient עם חריגות בתסריט, שעון מזויף.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
bench     python -m ch23.bench --runs 10        percentile(values, 95) = sorted[ceil(0.95*n)-1]
levers    python -m ch23.cost_levers --items 50 [--batch]   variants: smart/long -> fast -> fast/short; validity column
budget    BudgetGuard(max_usd=0.25).charge(model, completion) -> BudgetExceeded
breaker   CircuitBreaker(failure_threshold=3, cooldown_s=30): allow() / record_success() / record_failure()
call      resilient_call(primary, prompt, fallback=, breaker=, deadline_s=, policy=, degrade=degraded_summary) -> Outcome(source, errors, attempts)
batch     client.batches.create(model=, src=[InlinedRequest(contents=, config=)], config=CreateBatchJobConfig(display_name=)) -> job.name; poll batches.get
```

</div>

קישורים: [[22-observability]] · [[24-security-and-privacy]]
