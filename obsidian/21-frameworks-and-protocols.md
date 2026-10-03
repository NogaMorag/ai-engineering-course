---
direction: rtl
tags: [ai-course, book]
chapter: 21
---
# ספריות ופרוטוקולים: LangGraph ו־MCP

- **LangGraph:** גרף מצב עם מצב מוקלד; צמתים הם פונקציות רגילות; קשת מותנית בוחרת מסלול; שומר
  נקודות ב־SQLite בשורה אחת.
- **ריצה:** הפעלה עם מזהה שרשור; ההפרעה עוצרת ומחזירה מטען; ההמשכה מחזירה את ההחלטה לתוך
  הצומת, שרץ שוב מתחילתו; המצב השמור אומר איפה השרשור עומד.
- **מתי גרף:** הסתעפות אמיתית, הפרעות רבות, כמה אנשים. בפרויקט: הרחבה אופציונלית.
- **נוף:** כולם לולאה עם כלים ומצב; השאלה היא איפה הקוד ומה מוותרים.
- **MCP:** שם, תיאור, סכמה, קריאה, תוצאה עם דגל שגיאה. לא מכריע מה מותר. שרת ב־20 שורות, גשר
  בחוט רקע.
- **אבטחה:** תיאורים הם הנחיה זרה; תוצאות הן נתונים; הרשאות מינימליות; רשימה מותרת; שער אישור.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
graph     build_graph(research, deliver, open_checkpointer(path)) ; start_run(app, q, thread) -> interrupt payload ; resume_run(app, thread, approved)
build     StateGraph(ReviewState) ; add_node ; add_edge(START, ...) ; add_conditional_edges(node, fn, mapping) ; compile(checkpointer=SqliteSaver(conn))
run       app.invoke(input, {"configurable": {"thread_id": t}}) -> result["__interrupt__"][0].value ; app.invoke(Command(resume=v), config)
state     app.get_state({"configurable": {"thread_id": t}}).next  -> ("review",) while paused, () when done
mcp srv   MCPServer("name"); @server.tool() def f(x: int) -> dict: """doc"""; server.run()     (python -m ch21.mcp_server)
mcp cli   with course_notes_server(root) as tb: tb.tools, tb.declarations(), tb.call(name, args) -> (text, is_error)
bridge    tools = make_tools() | as_agent_tools(tb, prefix="mcp_")  -> run_agent(...)
fields    mcp 2.x: tool.input_schema, result.is_error, result.structured_content (snake_case)
```

</div>

קישורים: [[20-agent-reliability-state-memory]] · [[22-observability]]
