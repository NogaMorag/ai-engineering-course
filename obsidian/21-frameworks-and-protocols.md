---
direction: rtl
tags: [ai-course, book]
chapter: 21
---
# ספריות ופרוטוקולים: LangGraph ו־MCP

- **LangGraph:** `StateGraph(TypedDict)`, צמתים = פונקציות, `add_conditional_edges`, `compile(checkpointer=SqliteSaver)`.
- **ריצה:** `invoke(input, {"configurable": {"thread_id"}})`; `interrupt(payload)` עוצר;
  `invoke(Command(resume=v), config)` ממשיך; `get_state(config).next`.
- **מתי גרף:** הסתעפות אמיתית, הפרעות רבות, כמה אנשים. בפרויקט: הרחבה אופציונלית.
- **נוף:** כולם לולאה עם כלים ומצב; השאלה היא איפה הקוד ומה מוותרים.
- **MCP:** שם, תיאור, סכמה, קריאה, תוצאה עם `is_error`. לא הרשאה. שרת ב־20 שורות, גשר בחוט רקע.
- **אבטחה:** תיאורים = הנחיה זרה; תוצאות = נתונים; הרשאות מינימליות; רשימה מותרת; שער אישור.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
graph     build_graph(research, deliver, open_checkpointer(path)) ; start_run(app, q, thread) -> interrupt payload ; resume_run(app, thread, approved)
state     app.get_state({"configurable": {"thread_id": t}}).next  -> ("review",) while paused, () when done
mcp srv   MCPServer("name"); @server.tool() def f(x: int) -> dict: """doc"""; server.run()     (python -m ch21.mcp_server)
mcp cli   with course_notes_server(root) as tb: tb.tools, tb.declarations(), tb.call(name, args) -> (text, is_error)
bridge    tools = make_tools() | as_agent_tools(tb, prefix="mcp_")  -> run_agent(...)
fields    mcp 2.x: tool.input_schema, result.is_error, result.structured_content (snake_case)
```

</div>

קישורים: [[20-agent-reliability-state-memory]] · [[22-observability]]
