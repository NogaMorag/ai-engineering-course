---
direction: rtl
tags: [ai-course, book]
chapter: 20
---
# אמינות, מצב וזיכרון של סוכנים

- **ארבעה כשלים:** לולאה, ארגומנטים, כיבוס שגיאות, עלות. מעקות: זיהוי לולאה, Pydantic, `is_error`,
  תקציבים.
- **אישור = הפעולה המדויקת.** דחייה = תוצאת שגיאה. בפרויקט: שליחה אינה כלי.
- **אידמפוטנטיות:** מפתח מפורש או גיבוב; `replayed: True`. **נקודות שמירה:** אחרי סבב שלם; שעון
  ממשיך; גמורה חוזרת כפי שהיא.
- **זיכרון:** שיחה (היסטוריה) / משימה (`AgentState`) / ארוך טווח (`UserPreferences`, קטן, דרך
  ההנחיה).
- **סיכום היסטוריה מוחק פרטים.** רק כשחייבים, זנב ארוך, מזהים.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
guard     LoopDetector(max_repeats=1)(state, proposed) -> "loop_detected" | None
approve   gated(tool, ConsoleApproval() | ScriptedApproval([...]))  denial -> ApprovalDenied -> error result
idempot   idempotent(tool, IdempotencyStore(path))   key = idempotency_key or sha256(tool + canonical(args))
save      RunStore(path).save(state) via on_step; run_with_checkpoints(backend, tools, store, state=... | resume_run_id=...)
memory    UserMemory(path).load() -> UserPreferences(name, language, skip_topics, max_sentences); system_with_memory(SYSTEM, prefs)
summary   summarize_history(client, history, keep_last=4) -> [first, summary, *last4]
```

</div>

קישורים: [[19-workflows-vs-agents]] · [[21-frameworks-and-protocols]]
