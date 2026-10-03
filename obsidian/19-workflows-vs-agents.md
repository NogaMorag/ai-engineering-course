---
direction: rtl
tags: [ai-course, book]
chapter: 19
---
# תהליכי עבודה מול סוכנים, והלולאה ביד

- **סוכן = המודל מחליט על הזרימה. תהליך עבודה = הקוד.** הכי פחות אוטונומיה שעובדת.
- **חמישה דפוסים:** שרשור, ניתוב (enum ואז הנחיה לפי סוג), מקבול (סמפור 3), מתזמר ועובדים, מעריך
  ומשפר.
- **ארבעה קריטריונים לסוכן:** מורכבות, ערך, היתכנות, מחיר טעות. בפרויקט: רק המחקר.
- **מצב:** היסטוריה מפורשת, מקורות מהכלים, צעדים/טוקנים/שניות, סיבת עצירה, מעקב.
- **לולאה:** תקציב לפני הקריאה; אין קריאות = תשובה; guard; dispatch; שמירה אחרי סבב שלם.
- **כלים:** קטנים, „מתי” בתיאור, לקריאה בלבד, רשת רק בבקשה.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
route     route(client, text) -> kind   PROMPT_BY_KIND[kind]   summarize_routed -> (kind, summary)
parallel  run_parallel(fn, items, concurrency=3)   asyncio.Semaphore + asyncio.to_thread + gather (order kept)
state     AgentState(question) -> history/sources/steps/tokens/seconds/status/stop_reason/answer/trace; to_json/from_json
loop      run_agent(backend, tools, state, Budgets(max_steps=6, max_seconds=90, max_tokens=40_000), clock=, on_step=, guard=, system=)
stop      answered | max_steps | timeout | token_budget | loop_detected | error
tools     make_tools(allow_network=False) -> search_feeds, read_item [, fetch_url]   dispatch(tools, name, args) -> (json, is_error)
```

</div>

קישורים: [[18-testing-ai-applications]] · [[20-agent-reliability-state-memory]]
