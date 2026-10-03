# Decisions (ADR-lite)

| decision | alternative | why | what would change my mind |
| --- | --- | --- | --- |
| No classic RAG over a corpus | RAG with a vector store over all articles | there is no corpus to ask questions of; retrieval appears as story memory and in research | an "ask my archive" feature that readers actually want |
| Chroma for cross-day memory, numpy for same-day grouping | Chroma for both / SQLite blobs + numpy scan | the "is numpy enough" test: yes for a day's 40 items, no for persistence + a date filter | > 100k stories or several processes |
| An agent only for research | a fixed research workflow / an agent for the whole pipeline | only research needs a runtime choice (which item to read); the rest is a known sequence | a stage whose next step depends on results |
| Hand-written loop; LangGraph only as an optional approval gate | LangGraph in the core | no branching, one human gate at most, one author | real branching, interrupts in several places, several people |
| Fast model for summaries and scores, smart for research and intro | one model | eval held on the fast model; cost down | the eval drops after a provider update |
| Structured output everywhere, one repair attempt | free text + parsing | the schema is a contract the API enforces; code validates the rest | — |
| Explicit history in the agent (no server-side state) | `previous_interaction_id` | resumable, inspectable, provider-independent | — |
| SQLite | Postgres | single reader, single writer, zero operations | multiple writers |
| File delivery always, email via Gmail SMTP app password | Telegram | email is the natural medium and costs nothing; file keeps a zero-setup path | a reader who lives in chat |
| GitHub Actions cron | Task Scheduler | the laptop may be off at 07:00; Actions teaches secrets and scheduled jobs | no GitHub |
| Budget guard at $0.25, target $0.10 | no guard | a loop or a bad feed must not become a bill | a paid tier with headroom and a reason |
