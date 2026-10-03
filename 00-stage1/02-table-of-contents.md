# Stage 1 — Proposed table of contents

Nine parts, 32 chapters, six appendices. Chapter titles will be Hebrew in the book; English working
titles are used here. "Exercise" names the hands-on deliverable of the chapter; every exercise ships
with goal, time, prerequisites, starter, exact steps, expected output, checklist, hints, a full
reference solution and a "what this demonstrates" note. "→ project" says which Morning Brief
milestone reuses the result.

## Part 0 — Before you start

**Ch 0 — How to study from this book.** The method (read → run → write the note → explain aloud);
reading the book right-to-left correctly (the generated HTML version, or Obsidian with the RTL
Support plugin); Obsidian workflow and the ready-made note per chapter; how the 80-day schedule works and what to
drop when behind; API costs and the spending limit; what "done" means for a day; how exercises are
organized (`starter/`, `solution/`, `tests/`); honesty rules for the portfolio.

## Part I — Orientation and workbench

**Ch 1 — What an AI Engineer builds.** A user request and what "done" would mean; the roles table
(backend, applied AI, ML engineer, data scientist, research engineer); what transfers from your
background and what is new (three axes: models; data and evaluation; system); when *not* to use a
model; the 2026 market: a sample of postings (Israel + global) and what they repeatedly ask for; what
a convincing portfolio proves; a one-page preview of Morning Brief.
Exercise: classify three live postings; write your target-role note.

**Ch 2 — Setting up the workbench on Windows.** Windows Terminal and PowerShell 7, `winget`, Git,
VS Code, uv, Python 3.12, the course repo layout, the free Gemini API key from AI Studio, `.env`
loaded by uv, the first real call (`hello_model.py`) with token counts printed, UTF-8 so Hebrew
prints correctly, a troubleshooting table, stop/clean-up.
Exercise: a working environment and a first call. → project: the same layout and `.env` discipline.

## Part II — How models work (just enough)

**Ch 3 — Machine learning in one chapter.** Rule vs. learned function; model, parameters, training,
inference; dataset, features, labels; supervised / unsupervised / self-supervised; generalization
and overfitting; train/validation/test and leakage; baselines; confusion matrix, precision/recall/F1
and the cost of errors; why all of this governs prompt and retrieval changes too.
Exercise: a toy text classifier with train vs. held-out accuracy, a deliberate leak, and your own
`precision_recall_f1`. → project: the ranking evaluation in M6.

**Ch 4 — The minimal math.** Vectors, dot product, norm, cosine (numpy); probability and
conditional probability; softmax and temperature; loss (MSE, cross-entropy intuition); gradient
descent on one parameter; one page on "what changes during training" (forward pass, loss, gradient,
optimizer — no derivations).
Exercise: `vectors.py`, `softmax_temp.py`, `gd_one_param.py` with expected numbers. → project:
cosine for dedup in M3.

**Ch 5 — Inside a language model.** Tokens and tokenizers (Hebrew, English, code, JSON); the
embeddings table; contextual representations; attention intuition (one query, two keys); the
transformer block in one picture; encoder vs. decoder; pretraining → instruction tuning →
alignment/RLHF; model families and sizes; where knowledge lives: weights, context, external storage.
Exercise: token counting through the API; knowledge-cutoff and private-fact probes.

**Ch 6 — Generation and its knobs.** Autoregressive decoding; greedy vs. sampling; temperature,
top-p, top-k; `max_tokens` and stop reasons; determinism myths; reasoning ("thinking") models and
effort; the context window as a budget; prefill vs. decode, KV cache, time-to-first-token; the
anatomy of latency and cost; model limitations (hallucination, cutoff, arithmetic and counting,
instruction drift, sycophancy).
Exercise: temperature sweep, truncation handling, thinking on/off with cost. Checkpoint quiz.

## Part III — Building with model APIs

**Ch 7 — The Messages API.** Request anatomy; system/user/assistant roles; multi-turn means
re-sending history (statelessness); content blocks; `usage` and cost accounting; SDK vs. raw HTTP;
sensible `max_tokens`.
Exercise: `chat.py` CLI with history, `/reset`, `/cost`, and a fake client for tests. → project:
the adapter's foundation.

**Ch 8 — Prompt design as specification.** Task, inputs, constraints, output format, failure
behavior; few-shot examples chosen from dev cases; delimiters and XML tags separating instructions
from data; decomposition; chain-of-thought vs. reasoning models; prompt templates as versioned files;
anti-patterns ("be accurate", magic words, mega-prompts); iterate with an eval, not vibes.
Exercise: a `prompts/` package with versions and render tests; summarizer prompt v1→v3 compared on
three articles. → project: every prompt in M2–M5.

**Ch 9 — Structured outputs.** JSON Schema basics; Pydantic models; `client.messages.parse()`;
strict schemas and what they cannot guarantee; validation errors → repair/retry; enums and
constrained fields; nesting; where schema ends and correctness begins.
Exercise: `ArticleSummary` extracted from five articles, with tests. → project: M2 summaries.

**Ch 10 — Tool calling.** Tool definitions (name, description, input schema); the tool_use →
tool_result cycle; the loop by hand; parallel tool calls (all results in one message); errors as
`is_error` results; `strict: true`; safe dispatch (allowlist, argument validation, never eval);
descriptions that work; server-side tools (web search/fetch) in a paragraph.
Exercise: `fetch_url` + `search_notes` tools, the loop, parallel and error paths, tests. →
project: M4 research step.

**Ch 11 — Robust clients.** Streaming (events, `get_final_message()`); typed errors; retries,
backoff, jitter (SDK retries vs. your own — never both); timeouts (SDK vs. whole request); rate
limits; idempotency; the provider-adapter pattern (`LLMClient` protocol) and a portability demo on a
second backend (the OpenAI-compatible endpoint, or a local model via Ollama); fakes for tests.
Exercise: `llm/client.py` adapter, streaming CLI, failure-injection tests. Checkpoint: the article
summarizer CLI. → project: `llm/` package, M2.

## Part IV — Embeddings, retrieval and RAG

**Ch 12 — Embeddings and semantic similarity.** Calling an embedding model; cosine matrices;
nearest neighbors; choosing a model (dimensionality, multilingual, task instructions); normalization;
batching and caching embeddings; running a local embedding model (optional box); what embeddings are not (not anonymization, not comparable across
models, not calibrated).
Exercise: Hebrew/English sentence pairs; near-duplicate detection in 200 headlines with threshold
exploration. → project: M3 dedup and memory.

**Ch 13 — Search fundamentals.** Lexical search and BM25 (tokenization and normalization, Hebrew
notes); the inverted index; dense retrieval; exact vs. approximate nearest neighbors (HNSW
intuition, recall tradeoff); hybrid search and RRF; reranking (the cross-encoder idea, implemented by having the model score query–passage pairs; a local cross-encoder as an optional box); retrieval metrics
(hit@k, recall@k, MRR, precision@k); building a labeled query set.
Exercise: BM25 vs. dense vs. hybrid vs. hybrid+rerank, measured on 20 labeled queries.

**Ch 14 — Vector databases.** What a vector database adds (persistence, metadata filtering, ANN
index, upserts, collections); ChromaDB hands-on (persistent client, collections, add/upsert/query,
`where` filters, embedding functions); the landscape (numpy, sqlite-vec, pgvector, Qdrant, Weaviate,
Pinecone, FAISS); when it is *not* needed (the "is numpy enough?" test); operational concerns
(reindex on model change, versioning, permissions as metadata vs. enforced in code).
Exercise: the headline index in Chroma with date filters; a reindex. → project: M3 story memory.

**Ch 15 — RAG end to end.** The two paths (ingestion vs. query); loaders (Markdown, HTML, PDF
basics); cleaning; chunking strategies, overlap, stable content-addressed IDs, metadata; indexing and
incremental updates; retrieval and `top_k`; building the context within a budget; grounded
generation with numbered citations; citation validation; abstention; query rewriting (brief);
long-context vs. RAG; prompt caching for the static prefix; debugging by stage; the failure
taxonomy; what to trace.
Exercise: `ask_notes` — RAG over your own Obsidian course notes, with caching and fault injection.
Checkpoint. → project: citation discipline in M5; optional "ask my archive" extension.

## Part V — Evaluation and quality

**Ch 16 — Evals.** Why demos lie; eval datasets from user scenarios (categories, hard cases,
adversarial, unanswerable); dev vs. holdout and leakage through prompt edits; metrics: deterministic
checks, reference-based (exact, fuzzy, keyword), LLM-as-judge with a rubric; judge calibration
against human labels; biases (position, length, self-preference); pairwise vs. absolute; retrieval
evals vs. end-to-end; variance and repeats; the cost of evals; reporting (numerator/denominator,
per category).
Exercise: 30 cases, a calibrated judge, a harness and a report comparing two prompt versions. →
project: M6.

**Ch 17 — Failure analysis and debugging AI systems.** A hallucination taxonomy (unsupported,
contradicted, outdated, fabricated citation, over-refusal); reading traces; open coding →
categories → counts → priorities; root cause by stage; fix types (data, retrieval, prompt, schema,
model, product); regression cases; when to change the model vs. the system.
Exercise: error analysis on 30 real traces → two fixes → re-evaluation. → project: M6.

**Ch 18 — Testing AI applications.** The test pyramid for AI apps; unit tests with fake clients;
recorded fixtures (record once, replay); contract tests for tools and schemas; property-style
assertions on nondeterministic output; eval tiers (fast deterministic in CI, judge-based nightly,
live smoke); marking live tests; cost-aware CI.
Exercise: a pytest suite for the summarizer and `ask_notes`. Checkpoint. → project: `tests/`.

## Part VI — Agents and workflows

**Ch 19 — Workflows vs. agents; the loop by hand.** The operational definition; five workflow
patterns (prompt chaining, routing, parallelization, orchestrator–workers, evaluator–optimizer);
when autonomy is justified (complexity, value, viability, cost of error); the agent loop (state,
tools, budgets, stop reasons, logging); planning as a draft; tool design for agents.
Exercise: routing + parallelization workflow; a research agent with budgets. → project: M4.

**Ch 20 — Agent reliability, state and memory.** Failure modes (loops, wrong arguments, error
laundering, runaway cost); guardrails (step/time/cost budgets, loop detection, allowlists);
human-in-the-loop approval; idempotency for side effects; checkpoints and resume; memory:
conversation vs. task state vs. long-term; what to store, for whom, how long; summarization risks.
Exercise: approval gate, SQLite persistence, resume after a simulated crash. → project: M4, M5.

**Ch 21 — Frameworks and protocols.** LangGraph (StateGraph, nodes and edges, typed state,
SqliteSaver checkpointer, interrupt and resume, thread IDs) — rebuild the research agent; when
LangGraph pays back vs. a plain loop; the landscape in one page (LangChain, LlamaIndex, Pydantic AI,
SDK tool runners, agent SDKs, hosted/managed agents); MCP (what it standardizes, run or write a tiny
server, connect from your loop, security implications).
Exercise: LangGraph version of the agent + one MCP tool call. → project: optional M9+ approval gate.

## Part VII — Production

**Ch 22 — Observability.** Logs vs. metrics vs. traces; spans for LLM calls (model, tokens, cost,
latency, cache hits, tool calls); trace IDs across a run; run reports; redaction; a JSONL tracer you
own; what hosted tools add (Langfuse / OpenTelemetry) — optional connect.
Exercise: `tracing.py`, instrumented summarizer and agent, a run report. → project: M7.

**Ch 23 — Latency, cost and reliability engineering.** Measuring p50/p95 and TTFT; the cost model;
levers in order: model tiering, prompt caching (prefix stability, verification), the Batch API,
response caching with correct keys, parallelism, shorter outputs, effort; budget guards;
reliability: timeouts, retries, backoff, circuit breaker, fallback model, graceful degradation,
idempotent delivery.
Exercises: a latency benchmark; "cut the cost by half" measured; `resilient_call` with fallback. →
project: M7.

**Ch 24 — Security and privacy.** Prompt injection (direct, indirect); trust boundaries and a
threat model; least-privilege tools and allowlists; output handling (HTML sanitization, link
allowlist); secrets (`.env`, CI secrets, rotation); PII minimization; provider data policies;
logging hygiene; red-teaming your own system; what filters can and cannot prove.
Exercise: a poisoned-article test → defenses → injection eval cases. → project: M8.

**Ch 25 — Deployment and scheduling.** Configuration and environments; GitHub Actions: cron with
timezone math, secrets, artifacts, manual dispatch; CI running tests and fast evals; versioning
prompts, models and indexes together; rollback; the canary idea; Windows Task Scheduler as the local
alternative; Docker as an optional box.
Exercise: a scheduled job that produces an artifact. → project: M9.

**Ch 26 — Choosing models and methods.** Prompting vs. RAG vs. fine-tuning vs. agents as a decision
table keyed by the observed failure; open-weights vs. API (cost, privacy, operations);
evaluation-driven model selection; multimodal awareness (vision, OCR, speech) in one page.
Exercise: three decision memos. Checkpoint.

## Part VIII — Career

**Ch 27 — AI system-design interviews.** A framework (clarify → data and sources → pipeline → model
choices → evaluation → operations and cost → security → tradeoffs and evolution); five worked cases:
Morning Brief; document QA with permissions; a support assistant that takes actions; a content
classification pipeline at scale; batch extraction from PDFs; how to talk about what you would not
build; one unseen case for a mock.

**Ch 28 — Interview question bank.** About 40 questions with model answers: fundamentals, APIs and
prompting, RAG and retrieval, evals, agents, production, security, "tell me about your project";
how to discuss tradeoffs (name the alternative, its cost, your evidence).

**Ch 29 — Portfolio, CV and presenting the project.** README structure; architecture document and
diagram; the three-minute demo script; CV bullets (what / decision / evidence); LinkedIn summary;
honesty rules; job-search cadence alongside learning.

## Part IX — Final project: Morning Brief

**Ch 30 — Specification and architecture.** User story; functional and non-functional requirements;
pipeline stages; data model; diagram; where the model is used and where plain code is; decisions and
simpler alternatives.

**Ch 31 — The nine milestones (M1–M9).** Each with goal, concepts practiced, exact steps, starter
templates, expected output, tests, completion criteria, common mistakes, optional extensions.

**Ch 32 — Evaluating, presenting and defending the project.** Evaluation cases; interview questions
about the project with example answers; CV and interview presentation; what to say about limits.

## Appendices

A — Glossary (Hebrew/English). B — Setup troubleshooting. C — Cost-tracker template. D — Obsidian
note templates. E — Learning checklist and interview-readiness checklist. F — The daily schedule
in Hebrew (mirror of file 03).

## Chapter-end apparatus (every chapter 1–26)

1. סיכום — a concise summary.
2. מונחים לזכור — the terms, Hebrew and English.
3. טעויות נפוצות — misconceptions, stated and corrected.
4. שאלות ראיון — 3–6 questions you should be able to answer.
5. פתק Obsidian — a short ready-made note (plus the template to write your own).
6. תרגיל — the exercise (chapters 27–29 have practice drills instead of code).
7. העשרה אופציונלית — one or two external sources, clearly marked optional.

## Exercise → project reuse map

| Built in | Component | Reused in |
| --- | --- | --- |
| Ch 2 | repo layout, `.env`, cost printing | M1 |
| Ch 8 | `prompts/` versioned templates | M2–M5 |
| Ch 9 | `ArticleSummary` schema + parse/retry | M2 |
| Ch 10 | tool loop, `fetch_url`, safe dispatch | M4 |
| Ch 11 | `llm/client.py` adapter, fakes, retries | all milestones |
| Ch 12 | embedding + near-duplicate detection | M3 |
| Ch 14 | Chroma collection with metadata | M3 memory |
| Ch 15 | citation validation, abstention | M5 composition |
| Ch 16–18 | eval harness, judge, test fixtures | M6, `tests/` |
| Ch 19–20 | agent loop, budgets, persistence, approval gate | M4, optional gate |
| Ch 22 | `tracing.py`, run report | M7 |
| Ch 23 | `resilient_call`, caching, tiering | M7 |
| Ch 24 | injection cases, sanitization, secrets audit | M8 |
| Ch 25 | GitHub Actions cron workflow | M9 |

## Optional enrichment (never required)

| Part | Enrichment |
| --- | --- |
| II | Chip Huyen ch. 2 (foundation models); "Attention Is All You Need" (skim the figure) |
| III | Huyen ch. 5 (prompt engineering); Gemini prompt-design docs; Anthropic and OpenAI prompt guides for contrast |
| IV | Huyen ch. 6 (RAG); Lewis et al. 2020; pgvector / Qdrant docs for the landscape |
| V | Huyen ch. 3–4 (evaluation); Zheng et al. 2023 (LLM-as-judge); Hamel Husain's error-analysis essays |
| VI | Anthropic "Building effective agents"; LangGraph docs; MCP architecture page |
| VII | Huyen ch. 9–10; OWASP LLM Top 10; prompt-caching docs |
| VIII | roadmap.sh AI Engineer as a coverage checklist |
