---
direction: rtl
tags: [ai-course, book]
chapter: 23
---
# זמן תגובה, עלות ואמינות

- **מדידה:** p50, p95 וזמן לטוקן ראשון; אחוזון לפי דרגה; עשר הרצות מראות צורה, לא אמת.
- **עלות:** קלט, פלט (יקר פי 8), מטמון (עשירית ממחיר הקלט), אצווה (חצי מחיר); הנוסחה והמחירים
  בקטע למטה.
- **ידיות לפי סדר:** מודל, מטמון (קידומת יציבה), פלט קצר, אצווה, מקבול, חשיבה. ציון שיורד הוא קו אדום.
- **שומר תקציב:** סוכם את העלות של כל קריאה ועוצר באמצע הריצה, עם דיווח.
- **קריאה עמידה:** זמן קצוב לבקשה שלמה, ניסיונות תחומים, מפסק זרם (סגור, פתוח, חצי פתוח), גיבוי
  מפורש, הידרדרות ששומרת חוזה; המקור של התוצאה נרשם תמיד.
- **בדיקות:** לקוח מזויף עם חריגות בתסריט ושעון מוזרק; כל נתיב נבדק.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
cost      (in_excl_cached * 0.30 + out * 2.50 + cached * 0.03) / 1M   flash-lite, Oct 2026;  flash: 0.75 / 3.75 / 0.075
bench     python -m ch23.bench --runs 10        percentile(values, 95) = sorted[ceil(0.95*n)-1]
levers    python -m ch23.cost_levers --items 50 [--batch]   variants: smart/long -> fast -> fast/short; validity column
budget    BudgetGuard(max_usd=0.25).charge(model, completion) -> BudgetExceeded
breaker   CircuitBreaker(failure_threshold=3, cooldown_s=30): allow() / record_success() / record_failure()
call      resilient_call(primary, prompt, fallback=, breaker=, deadline_s=, policy=, degrade=degraded_summary) -> Outcome(source, errors, attempts)
batch     client.batches.create(model=, src=[InlinedRequest(contents=, config=)], config=CreateBatchJobConfig(display_name=)) -> job.name; poll batches.get
```

</div>

קישורים: [[22-observability]] · [[24-security-and-privacy]]
