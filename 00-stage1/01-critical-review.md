# Stage 1 — Critical review of the ChatGPT draft

## 1. What was reviewed

- **The draft textbook** `Noga_AI_Engineering_Textbook_HE _1_.md` (the `.docx` is the same text):
  "הנדסת AI מעשית למפתחות Python", 20 chapters + solutions appendix, glossary, index, sources.
  About 34,000 words, dated 27 September 2026. Read in full.
- **The project package** `AI_Engineer_Project.zip` → DocDesk, `starter/` and `solution/`:
  ~1,000 lines of Python, 20 unit tests, 26 eval cases, `docs/LABS.md`, `docs/VALIDATION.md`.
  Read in full.
- **Your friend's path**: roadmap.sh AI Engineer → selected chapters of Chip Huyen's *AI Engineering*
  → Obsidian summaries → LangGraph / ChromaDB → a morning-newsletter agent.
- **Market signals**: 2026 job descriptions (RAG pipelines, evaluation harnesses, agent
  architectures, latency/cost reasoning, production experience; frameworks named but secondary).
- **Tool state as of today** (PyPI): `anthropic` 1.11, `openai` 3.24, `chromadb` 1.5, `langgraph` 1.2,
  `sentence-transformers` 6.1, `mcp` 2.3, `feedparser` 6.0, `trafilatura` 2.3.

One limitation: roadmap.sh renders client-side and its GitHub source path has moved, so I could not
pull today's node list. The comparison in §7 uses the roadmap as I know it (content through 2025).
Nothing in the recommendation hinges on it.

## 2. Verdict in one paragraph

The draft is an honest, well-written **conceptual** book. Its explanations are careful, its Hebrew is
natural, and it never over-claims. Most of its *explanations* should survive. But it is not the
course you asked for. Its hands-on core never calls a model: DocDesk's default "mock" mode is
word-overlap retrieval plus copying the first retrieved chunk, and the live path was never executed
by its author (its own `VALIDATION.md`: PyPI returned HTTP 403, "no OpenAI key or paid model call was
used"). It contains exactly two coding exercises, both about fifteen lines (cosine similarity,
precision/recall/F1). Agents, tool calling, embeddings, vector databases, reranking, streaming,
observability and scheduling are described but never built. Its project is a document-QA service,
not the newsletter agent, and its "study plan" is a twelve-row weekly table. So: keep the voice and
many explanations, drop the mock-first philosophy and DocDesk, and rebuild the structure around real
model calls from day two, an exercise per lesson, and the newsletter agent.

## 3. Strengths worth learning from

(The new book is written from scratch, per your instruction; these are qualities to preserve, not text to copy.)

- **Voice and terminology discipline.** Hebrew first, English term in parentheses on first use,
  patient without being patronizing. This is the register the new book keeps.
- **Distinctions interviewers love**, already well phrased:
  - parseable JSON ≠ schema-valid ≠ application-rule-valid ≠ factually supported (§8.4);
  - a citation ID that exists ≠ a claim that is supported (§10.8);
  - retrieval failure vs. generation failure, and debugging "by the stage where the evidence
    disappeared" (§10.9);
  - workflow vs. agent, defined operationally ("the model chooses the next step at runtime") (§11.1);
  - "three places information lives": weights, context, external storage (ch. 2).
- **Math with tiny numbers and stdlib Python** (ch. 3; §6: softmax, temperature, attention with one
  query and two keys). Exactly the "intuition first, small example" style you asked for.
- **Evals (ch. 12)**: holdout leakage through repeated prompt edits; coverage vs. unsupported answers;
  LLM-judge biases (position, verbosity); "report numerator and denominator".
- **Security (ch. 14)**: trust boundaries; filtering *after* retrieval means the model already saw
  the data; secrets never enter the context; "the model proposes, the system decides".
- **Operations (ch. 13)**: retry doubling (3 app retries × 3 SDK retries = 9 calls); a local timeout
  does not mean you were not billed; cache key = everything that changes the answer; "we doubled the
  servers and got more 429s".
- **Career material (ch. 18–19)**: the eight Israeli job postings table, CV/README guidance, the
  "when to start applying" checklist, 15 Q&A, two system-design cases, the take-home rubric.
- **DocDesk's `VALIDATION.md` discipline**: say exactly what was run and what was not.

## 4. Core problems

1. **Mock-first inverts the learning goal.** `MockProvider.generate` returns `chunks[0].text`. The
   book then spends thousands of words repeating that mock results prove nothing about a model
   (ch. 1, 7, 9.1, 10.10, 12.8, 16, 17 labs 2–5, 19 Q6/Q15, 20). Honest, but a reader finishes the
   book without having built anything an employer recognizes as AI engineering. Test doubles are a
   *testing technique* (kept, in the new Ch. 18); they are not a curriculum.
2. **Too little practice, too late.** The first model call appears in ch. 8, after six chapters of
   theory; the two exercises are in ch. 17. You asked for an exercise per lesson with starter code,
   a checklist and a reference solution.
3. **Theory depth is misallocated.** Hand-derived backpropagation, dropout, Adam, early stopping,
   MAE/RMSE and calibration curves (ch. 4–5) exceed what an applied role needs. Meanwhile prompt
   design gets one section (§8.2), structured outputs get one Pydantic snippet, and agents get no code.
4. **Vendor and version fragility.** The only API code is an OpenAI Responses-API snippet with
   `gpt-4.1-mini`; `openai==3.19.0` is pinned "verified against the release" but was never installed.
   Model names and prices inside chapter prose go stale within months. The new book confines them to
   one appendix and one config file.
5. **Required topics are missing or hands-off** (full mapping in §6).
6. **The project is not yours.** DocDesk ≠ newsletter agent. It also has no agentic step, no
   scheduling, no delivery, no personalization, no memory across runs.
7. **Study plan granularity.** A twelve-week table; no objectives, time estimates or completion
   criteria per day; no review days or checkpoints.
8. **Chapter apparatus.** You asked for summary, key terms, misconceptions, interview questions, an
   Obsidian note and an exercise at the end of every chapter. The draft has inline "בדיקת הבנה"
   paragraphs and one global glossary.
9. **Smaller technical points not worth carrying over**: the eval "regression gate" thresholds equal
   the observed baseline (tautological); two HTTP servers for one API (stdlib `ThreadingHTTPServer`
   plus an untested FastAPI adapter); the live path installs packages with `uv pip install` and then
   runs with `--no-sync`, fighting uv's lock model; Python pinned `<3.13` without a stated reason.

## 5. Chapter-by-chapter disposition

| Draft chapter | Verdict | Where it lands in the new book |
| --- | --- | --- |
| לפני שמתחילים | Rebuild | Ch 0 (how to study). Mock/live framing dropped. |
| 1 מה בונה AI Engineer | Keep, edit | Ch 1. Roles table, "when not to use a model", portfolio criteria kept; add the backend→AI transfer map from ch. 18. |
| 2 השפה הבסיסית של מודלים | Keep, merge | Ch 3 + Ch 5. "Three places information lives" kept verbatim in spirit. |
| 3 המתמטיקה המינימלית | Keep, shorten | Ch 4. Vectors/cosine, probability, softmax, loss, gradient descent with small numbers (numpy). Matrix-shape section becomes a side box. |
| 4 למידת מכונה והערכה | Keep, shorten | Ch 3. Splits, leakage, overfitting, precision/recall/F1, baselines kept. MAE/RMSE removed; calibration reduced to one paragraph. |
| 5 רשתות עצביות | Remove (mostly) | One page in Ch 4: "what changes during training". Backprop derivation, dropout, Adam, early stopping → optional enrichment pointer. |
| 6 Transformers ומודלי שפה | Keep, edit | Ch 5 + Ch 6. Strong. Add hands-on tokenization, reasoning models, model families; generation gets its own chapter. |
| 7 סביבת העבודה | Rebuild | Ch 2. Same careful macOS/uv pattern; new project, API key + spending limit, Ollama optional, verification and troubleshooting tables. |
| 8 Model APIs | Rebuild, expand | Ch 7–11. Concepts kept (four meanings of "valid output", tool call is a proposal, retry doubling); code rewritten for the chosen stack; real calls. |
| 9 Embeddings וחיפוש | Rebuild, expand | Ch 12–14. RRF, lexical vs. semantic, metadata/permissions, ANN explanation kept; add hands-on embeddings, BM25, Chroma. |
| 10 RAG | Keep, expand | Ch 15. Pipeline table and debugging-by-stage kept; add code, prompt caching, long-context comparison. |
| 11 Agents | Rebuild, expand | Ch 19–21. Definitions, budgets, idempotency, MCP paragraph kept; add an implemented loop and LangGraph hands-on. |
| 12 Evals | Keep, expand | Ch 16–17. Add harness code, judge calibration exercise, error analysis. |
| 13 תפעול | Keep, edit | Ch 22–23. Concepts kept; add a tracer you own, measurement, cost levers. Semaphore/async section shortened. |
| 14 אבטחה ופרטיות | Keep, edit | Ch 24. Add a red-team exercise, HTML output handling, CI secrets. |
| 15 בחירת מודל ושיטה; Multimodal | Shorten | Ch 26. Decision table kept; LoRA, quantization, OCR, speech, video → one awareness paragraph each. |
| 16 אריזה, CI ופריסה | Shorten, replace | Ch 25. Docker → optional box (you use it at work already); GitHub Actions cron becomes the deployment; versioning/rollback/canary kept. |
| 17 מעבדות | Remove | Replaced by 30+ per-chapter exercises and 9 project milestones. |
| 18 תיק עבודות ומשרות | Rebuild | Ch 29 (+ Ch 1). Written from fresh research at writing time; nothing copied from the draft. |
| 19 ראיונות | Keep, expand | Ch 27–28. 15 Q&A → ~40; 2 design cases → 5; the take-home exercise is re-targeted at the newsletter project. |
| 20 מסלול 12 שבועות | Replace | 16-week daily schedule (file 03; Hebrew version = appendix F). |
| נספח פתרונות / מילון / אינדקס | Keep the pattern | Solutions move next to each exercise; glossary grows; index generated at the end. |

## 6. Missing material, mapped to your requirements list

| Topic you listed | Draft coverage | New book |
| --- | --- | --- |
| AI eng vs SWE / DS / MLE / research | Good (ch. 1) | Ch 1 |
| Minimum ML foundations | Too much (ch. 4–5) | Ch 3–4, trimmed |
| How LLMs work (useful level) | Good (ch. 6) | Ch 5 |
| Tokens, context, inference, temperature, sampling, limits | Concept only | Ch 6 + exercises D7, D9 |
| Prompt design & structured outputs | Thin (§8.2, one snippet) | Ch 8–9, three study days |
| Working with model APIs | One untested snippet | Ch 7 + Ch 11; real calls from D2 |
| Tool / function calling | Dispatcher, no model | Ch 10: loop by hand, parallel tools, strict schemas, safe dispatch |
| Embeddings & semantic similarity | Formula only | Ch 12 hands-on (local models, Hebrew vs. English) |
| Search / IR fundamentals | RRF yes, BM25 described | Ch 13: BM25, dense, ANN, hybrid, rerank, metrics |
| RAG architecture & implementation | Strong narrative, no code | Ch 15, built over your own course notes |
| Chunking, indexing, retrieval, reranking, grounding | Described | Ch 15 exercises + measured comparisons |
| Vector DBs & when not needed | One paragraph | Ch 14: Chroma hands-on, landscape, "is numpy enough?" test |
| LLM evaluation, datasets, metrics | Strong narrative; keyword harness | Ch 16: judge calibration, variance, harness in code |
| Hallucinations, failure analysis, debugging | §10.9 good | Ch 17: error-analysis exercise on real traces |
| Agents, workflows, state, memory, tools | No code | Ch 19–20 |
| Where LangGraph fits | One paragraph | Ch 21 hands-on + a justified decision in the project |
| Where ChromaDB fits | Absent | Ch 14 + project memory store |
| Observability & monitoring | Concepts | Ch 22: a tracer you own; optional hosted tool |
| Latency, cost, caching, reliability | Concepts | Ch 23: measured exercises; prompt caching, batch API, model tiering |
| Security, privacy, injection, data | Strong | Ch 24 + red-team exercise + CI secrets |
| Testing AI applications | Tests exist, not taught | Ch 18 |
| Deployment & production basics | Docker/CI untested | Ch 25: GitHub Actions cron; Docker optional |
| System-design interview prep | 2 cases | Ch 27: framework + 5 cases (incl. your project) |
| Interview questions & answers | 15 | Ch 28: ~40 |
| Discussing architecture tradeoffs | Scattered | Decision tables in every project milestone + Ch 27 |

Added because the 2026 market expects them and the draft lacks them: reasoning ("thinking") models
and effort control, prompt caching, the Batch API, provider portability (incl. a free local model via
Ollama), MCP (light, hands-on), scheduling and delivery, personalization and ranking.

## 7. Your friend's path, evaluated

- **roadmap.sh AI Engineer** — a good *coverage checklist* (pre-trained models and their APIs, prompt
  engineering, embeddings, vector databases, RAG, agents, safety/ethics, multimodal, dev tools). Weak
  on evaluation, observability, testing and production, and heavy on vendor lists. Used here as a
  checklist, not as a structure. Items tied to one vendor product (e.g., an "Assistants API") are
  replaced by the mechanism they implement (a tool loop plus persisted state).
- **Chip Huyen, *AI Engineering*** — the best source of mental models. Mapped as *optional enrichment*
  per part: her ch. 3–4 (evaluation) ↔ Part V; ch. 5 (prompt engineering) ↔ Ch 8; ch. 6 (RAG and
  agents) ↔ Parts IV and VI; ch. 9 (inference optimization) ↔ Ch 23; ch. 10 (architecture, user
  feedback) ↔ Ch 22/25; ch. 7–8 (finetuning, dataset engineering) → optional only.
- **Obsidian summaries** — built into every chapter (a ready note + a template for your own).
- **Her four focus areas (LLMs, RAG, vector DBs, evaluation)** — correct, and the new book adds the
  two areas 2026 postings stress just as much: agents/tool use and production concerns.
- **LangGraph** — an orchestration library for *stateful, graph-shaped* agent workflows: nodes
  (functions), edges (routing), a shared typed state, a checkpointer that persists state after every
  node (SQLite/Postgres), and interrupts for human approval and resume. It sits at the
  "orchestration" layer, above the model API. It is justified when you need durable state and resume
  after failure, human-in-the-loop gates, complex branching, or multi-agent handoffs. For a single
  bounded tool loop a plain Python `while` loop is simpler and more transparent. The book teaches the
  loop first (Ch 19), then LangGraph (Ch 21), and the project uses LangGraph only in an optional
  milestone (a "review before send" approval gate) with the tradeoff written down.
- **ChromaDB** — an open-source, embedded vector database: it stores embeddings together with the
  original text and metadata, persists to disk without a server, and answers "nearest vectors to this
  query, filtered by metadata" questions. It sits at the "retrieval storage" layer. Alternatives, in
  order of weight: a numpy array (thousands of vectors), `sqlite-vec`, pgvector (when Postgres already
  exists), Qdrant/Weaviate (scale, hybrid search built in), Pinecone (managed), FAISS (a library, not a
  store). The book builds similarity search with numpy first (Ch 12), then Chroma (Ch 14), and the
  project uses Chroma for cross-day story memory, with the "SQLite blob scan would also do" note.
- **The newsletter agent as the final project** — adopted, and redesigned so every milestone reuses a
  component built in an earlier chapter (map in file 02).

## 8. What survives from DocDesk

Nothing. You asked for the course to be built as if the uploaded files did not exist, so no code,
text, data or structure is carried over from DocDesk or the draft. For transparency, these standard
practices appear in the new book on their own merits and also happened to be in DocDesk: citation IDs
validated against the retrieved set; abstention as a first-class output; eval cases as JSONL with
categories and expected behavior; cost computed from the provider's usage report; a cache key that
includes everything that changes the answer; permission filtering before the model sees data; and
"say exactly what you ran".

## 9. Design principles of the rebuild

1. **Build first, then just enough theory.** First real model call on Day 2. Part II (how models
   work) is seven days, each ending in a small script, not three weeks of reading.
2. **Every lesson ends in code you keep.** Exercises are components of the final project; see the
   reuse map in file 02.
3. **Mechanism before framework.** Hand-written tool loop → LangGraph. Numpy cosine → Chroma.
   BM25 → hybrid. Own JSONL tracer → hosted observability (optional).
4. **Measure, don't assert.** Every "X is better" in the book comes with an eval or a benchmark the
   reader runs (lexical vs. dense, cached vs. uncached, Haiku vs. Sonnet).
5. **One stack, one adapter.** Provider specifics live in one file; everything else is
   provider-neutral; portability is demonstrated once (Ch 11) and then kept.
6. **Honest about limits**, without the mock-mode sermon.
7. **Real data, employer-free.** Public RSS feeds, your own course notes, synthetic documents. Never
   anything from work.
8. **A study day is 75–120 minutes with a written completion criterion**, and every week has one
   lighter day so slipping is recoverable.
