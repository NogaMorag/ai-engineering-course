---
direction: rtl
tags: [ai-course, book]
chapter: 11
---
# לקוחות עמידים וניידות בין ספקים

- **טבלת הכשלים:** 400/401/404 לא מנסים; 429 ו־5xx וזמן קצוב מנסים אחרי המתנה; `incomplete`
  מגדילים מגבלה.
- **היררכיה שלנו:** `LLMError` ובנותיה, המרה ב־`classify` לפי `status_code`, בנקודה אחת.
- **ניסיונות:** מעריכי עם אקראיות, 4 ניסיונות, תקרה 20 שניות, גבול כולל 90. רכיב אחד הבעלים;
  הספרייה כבויה (`attempts=1`).
- **זמן קצוב באלפיות שנייה.** המקסימום הוא זמן קצוב כפול ניסיונות ועוד המתנות; גבול הזמן הכולל קוצר
  אותו. כשל לא מבטל חיוב.
- **הזרמה:** TTFT כן, זמן כולל לא; לא ל־JSON, לא לצינור; לא מנוסה באמצע.
- **מתאם:** ממשק אחד (`LLMClient`), מימוש אמיתי ולקוח מזויף.
- **דולף דרך המתאם:** שמות מודלים, ניב סכמות, טוקנים, איכות.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
client    genai.Client(http_options=types.HttpOptions(timeout=60_000, retry_options=types.HttpRetryOptions(attempts=1)))
classify  status 429 -> LLMRateLimited | >=500 -> LLMUnavailable | 4xx -> LLMBadRequest | Timeout/Connection -> LLMUnavailable
retry     wait = uniform(0, min(20, 1 * 2**(attempt-1)));  stop at 4 attempts or when elapsed + wait > 90
stream    for event in create(..., stream=True): event.event_type == "step.delta" and event.delta.type == "text" -> event.delta.text
usage     Completion(text, status, input_tokens, output_tokens, cached_tokens, attempts, latency_s)
cli       summarize_url.py <url> | --file page.txt [--json]   exit 0 ok / 2 not article / 3 llm / 4 fetch
```

</div>

קישורים: [[10-tool-calling]] · [[12-embeddings]]
