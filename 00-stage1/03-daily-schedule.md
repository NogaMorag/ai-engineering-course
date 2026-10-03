# Stage 1 — Daily study schedule (16 weeks, 80 study days)

## Assumptions and rules

- **Rhythm**: five study days a week (Sunday–Thursday), 75–120 minutes each; weekends are free or
  catch-up. Two consecutive days may be merged into one weekend session.
- **Total**: about 130 hours (average 98 minutes/day). Time estimates show read / build / note.
- **Every week has one lighter day**, and there are six checkpoints plus two buffer days. If you fall
  behind: first drop "optional" items, then merge a review day, never skip a checkpoint.
- **Done means the completion criterion is met**, not that the time ran out. If a day's exercise is
  not done, finish it before starting the next build day; theory reading can slide.
- **Chapters** refer to file 02. **Mn** = Morning Brief milestone (file 04). Section numbers are
  provisional until the chapters are written.
- **Platform**: Windows 11 with PowerShell 7 in Windows Terminal; every command in the book is a
  PowerShell command. Mac users follow the same days with the equivalents table in Ch 2 §2.13
  (install with Homebrew, zsh instead of PowerShell, cron or launchd instead of Task Scheduler).
- **Day 0**: installations only, done before Week 1 starts (ideally on the weekend before), with no
  time pressure. Installations are the step most likely to go wrong for someone new to the tools, so
  they do not share a day with the first model call.
- Costs: the primary API runs on Google's **free tier**, so every day is $0 as long as you stay
  within its rate limits (shown in AI Studio). Days marked 💲 make many calls and may hit the
  per-minute limit; the exercise then throttles or spreads the calls, which is itself a lesson. If
  you later prepay $5 for Tier 1, those days cost cents.

---

## Day 0 — Installations (before Week 1)

### D0 — Terminal, tools, Python
- Objective: a terminal that prints Hebrew correctly and the four tools installed and answering.
- Read: Ch 2 §2.1–2.4 (Mac: also §2.13).
- Time: 60–90 min including downloads (20 / 60 / 10). Do it on the weekend before Week 1; if anything
  fails, appendix B is the first stop and nothing else in the course waits on it.
- Exercise: install PowerShell 7 and make it the default profile; set `PYTHONUTF8=1` as a user environment
  variable; install Git, VS Code and uv with `winget`; install Python 3.12 with `uv python install 3.12`;
  open a new terminal and run the four version commands.
- Done when: `$PSVersionTable.PSVersion` starts with 7; `git --version`, `code --version`, `uv --version`
  all answer; `uv python list` shows 3.12; `uv run python -c "import sys; print(sys.flags.utf8_mode)"`
  prints 1 inside any uv project (or simply after Day 2).
- You can explain: what uv manages and why the book installs no other Python; why a new terminal is needed
  after an install or an environment-variable change.

## Week 1 — Orientation, workbench, ML vocabulary

### D1 — What an AI Engineer builds; how this course works
- Objective: understand the role, the course method, and the final project; start your Obsidian folder.
- Read: Ch 0; Ch 1.
- Time: ~75 min (45 / 20 / 10).
- Exercise: read three current postings (links in Ch 1 + your own search); classify each with the
  Ch 1 roles table; write your "target role" note from template D (three skills you have, three you lack).
- Done when: the note exists with three classified postings.
- You can explain: what an AI engineer owns that a backend engineer does not; why "it returned valid JSON" is not success.

### D2 — The course project and the first real call
- Objective: a reproducible project and one working model call with token counts printed. (The tools
  were installed on Day 0.)
- Read: Ch 2 §2.5–2.12.
- Time: ~90 min (25 / 55 / 10).
- Exercise: create `ai-course/` with `uv init --bare`, pin 3.12, add `google-genai` and `pydantic`,
  `pytest` and `ruff`; `.gitignore` and `pyproject.toml` pytest section; get a free Gemini API key in AI
  Studio and note your rate limits; `.env` loaded with `uv run --env-file .env`; fill the three TODOs in
  `hello_model.py` and run it; copy and run the smoke tests; first git commit without the key.
- Done when: the script prints a Hebrew answer and three token counts; `uv run pytest -q` reports 3 passed;
  `git check-ignore .env` prints `.env`; the commit exists and does not contain `.env`.
- You can explain: what `uv run` does on every command; where the key lives and why it is loaded per run;
  what an input token would cost on the paid tier.

### D3 — Machine learning vocabulary
- Objective: model, parameters, training vs. inference, datasets, learning paradigms, generalization.
- Read: Ch 3 §3.1–3.4.
- Time: ~90 min (35 / 45 / 10).
- Exercise: `toy_classifier.py` — nearest-centroid classifier over word counts for 40 labeled
  messages; accuracy on train vs. held-out; then leak the label into a feature and watch the jump.
- Done when: both accuracies print and your note explains the gap and the leak.
- You can explain: training vs. inference in one sentence each; why only held-out numbers are honest.

### D4 — The evaluation mindset
- Objective: splits, baselines, confusion matrix, precision/recall/F1, the cost of errors.
- Read: Ch 3 §3.5–3.8.
- Time: ~90 min (35 / 45 / 10).
- Exercise: implement `precision_recall_f1` and a confusion matrix for the toy classifier; a majority
  baseline; choose a threshold given "a missed urgent ticket costs ten false alarms".
- Done when: tests pass; a five-line note says which metric you would report and why.
- You can explain: why 94% accuracy can lose to a baseline; precision vs. recall with your own example.

### D5 — Vectors and cosine
- Objective: vectors, dot product, norm, cosine; why equal dimensions do not mean the same space.
- Read: Ch 4 §4.1–4.3.
- Time: ~75 min (25 / 40 / 10).
- Exercise: `vectors.py` with numpy: cosine, normalize, rank five toy document vectors against a
  query; show cosine vs. dot product when one vector is scaled; tests for zero vector and mismatched dimensions.
- Done when: outputs match the book's expected numbers; tests pass.
- You can explain: what cosine measures; why 0.8 is not "80% correct".

## Week 2 — Minimal math, inside an LLM

### D6 — Probability, softmax, loss, gradient descent
- Objective: the four ideas behind "training" and "sampling", with small numbers.
- Read: Ch 4 §4.4–4.8.
- Time: ~90 min (35 / 45 / 10).
- Exercise: `softmax_temp.py` (same logits at T = 0.5 / 1 / 2); `gd_one_param.py` (loss curve while w → 3).
- Done when: tables print and you predicted each direction before running.
- You can explain: what a loss function is; why temperature sharpens or flattens; what training changes and inference does not.

### D7 — Tokens and tokenizers 💲
- Objective: tokens vs. words, the embeddings table, contextual representations, Hebrew's token cost.
- Read: Ch 5 §5.1–5.3.
- Time: ~90 min (30 / 50 / 10).
- Exercise: `count_tokens.py` using the API's token-counting endpoint on six texts (Hebrew paragraph,
  English paragraph, JSON, code, URL list, emoji); the paid-tier price per text for the fast and the smart model.
- Done when: a table of tokens and cost per text exists, with a note on the Hebrew/English ratio.
- You can explain: why words ≠ tokens; why Hebrew costs more; what a context window counts.

### D8 — Attention, the transformer, training stages, where knowledge lives 💲
- Objective: a mechanical picture of the model and the three places information can come from.
- Read: Ch 5 §5.4–5.7.
- Time: ~90 min (45 / 35 / 10).
- Exercise: `knowledge_probe.py`: ask about (a) a fact after the model's cutoff, (b) a fact present
  only in text you supply, (c) the same fact without the text; log the three answers.
- Done when: the three answers are saved with the "weights / context / external" note.
- You can explain: why RAG is not training; what instruction tuning changed; what attention does mechanically and what it does not prove.

### D9 — Generation knobs and limitations 💲
- Objective: sampling parameters, stop reasons, context budget, reasoning models, failure modes.
- Read: Ch 6.
- Time: ~100 min (40 / 50 / 10).
- Exercise: `generation_knobs.py`: temperature 0 / 0.7 / 1.0 × 5 runs on a classification prompt and
  a creative prompt; a `max_tokens` truncation caught via `stop_reason`; thinking level `minimal` vs. `high` on a
  logic puzzle, comparing thought tokens and latency.
- Done when: a table shows variance per temperature, the truncation caught, and the token cost of thinking.
- You can explain: when temperature should be low or high; why low temperature does not fix hallucination; what a reasoning model trades.

### D10 — Review and Checkpoint 1
- Objective: consolidate Parts I–II.
- Read: chapter summaries of Ch 1–6.
- Time: ~75 min.
- Exercise: the 20-question quiz at the end of Ch 6; merge and fix Obsidian notes; check usage in AI Studio; answer Ch 3–6 interview questions aloud.
- Done when: ≥16/20; notes for Ch 1–6 exist; usage is logged.
- You can explain: the model–API–system map in two minutes without notes.

## Week 3 — The Messages API and prompting

### D11 — The Interactions API 💲
- Objective: request anatomy, roles, statelessness, usage accounting.
- Read: Ch 7.
- Time: ~100 min (35 / 55 / 10).
- Exercise: `chat.py` CLI with history, `/reset`, `/cost`, `max_tokens` handling; tests with a fake client.
- Done when: a six-turn chat shows the model "remembers" only what you re-send; cost accumulates per turn.
- You can explain: why conversations are stateless; what the system prompt is for; how usage maps to cost.

### D12 — Prompts as specifications 💲
- Objective: the parts of a good prompt; separating instructions from data; honest comparison.
- Read: Ch 8 §8.1–8.3.
- Time: ~90 min (30 / 50 / 10).
- Exercise: rewrite a vague summarization prompt into a specification (task, constraints, format,
  failure behavior); run v1 and v2 on three provided articles; write the comparison.
- Done when: v1 and v2 are saved as files and the comparison note exists.
- You can explain: the five parts of a prompt; why "be accurate" is not a constraint.

### D13 — Examples, structure, decomposition, versioning 💲
- Objective: few-shot, delimiters and XML tags, decomposition, CoT vs. reasoning models, versioning.
- Read: Ch 8 §8.4–8.8.
- Time: ~90 min (30 / 50 / 10).
- Exercise: `prompts/` package — templates as files with version and changelog, `render()` with tests;
  add one positive and one negative (unanswerable) example chosen from dev cases.
- Done when: tests pass; prompt v3 renders; a note decides "CoT or a reasoning model?".
- You can explain: how examples bias outputs; when decomposition beats one mega-prompt; what prompt versioning buys.

### D14 — Structured outputs 💲
- Objective: schemas with Pydantic and `response_format`; validation and repair; schema ≠ truth.
- Read: Ch 9.
- Time: ~100 min (30 / 60 / 10).
- Exercise: `ArticleSummary` (is_article, headline, three bullets, why it matters, tags, confidence enum)
  extracted from the three Ch 8 articles; one repair attempt on validation failure; tests with fakes.
- Done when: three valid objects are saved as JSON (the error page as `is_article: false`); a deliberate rule violation is repaired or rejected.
- You can explain: the four meanings of "valid output"; what strict schemas guarantee and do not.

### D15 — Tool calling, the loop by hand 💲
- Objective: the function_call → function_result cycle and a loop you own.
- Read: Ch 10 §10.1–10.6.
- Time: ~100 min (30 / 60 / 10).
- Exercise: tools `fetch_url(url)` (httpx + trafilatura) and `search_notes(query)`; write the loop; run "summarize this URL".
- Done when: the trace shows function_call → your execution → function_result → final answer.
- You can explain: a tool call is a proposal, not an execution; why results return as function_result steps keyed by call_id.

## Week 4 — Tools, robustness, checkpoint

### D16 — Parallel tools, errors, strict schemas, safe dispatch 💲
- Objective: production-grade tool handling.
- Read: Ch 10 §10.7–10.8.
- Time: ~90 min (25 / 55 / 10).
- Exercise: parallel calls for two URLs; `is_error` results; an allowlist dispatcher that validates
  arguments and rejects `file://` and private IPs; A/B of two tool descriptions.
- Done when: tests cover parallel results in one message, the error path and a blocked URL.
- You can explain: why all tool results go in one user message; why dispatch never uses eval or dynamic import.

### D17 — Streaming, errors, retries, timeouts 💲
- Objective: the client behaviors every production call needs.
- Read: Ch 11 §11.1–11.4.
- Time: ~90 min (30 / 50 / 10).
- Exercise: streaming (`step.delta` events, usage from `interaction.completed`); distinct handling of rate-limit,
  status and connection errors via your own `LLMError` hierarchy; SDK retries disabled and timeout configured; tests proving retries apply only to transient errors.
- Done when: streaming works; failure-injection tests pass; a note computes wall-clock = timeout × (retries + 1).
- You can explain: TTFT vs. total latency; retryable vs. not; why a timeout does not mean "not billed".

### D18 — Rate limits, idempotency, the provider adapter 💲
- Objective: isolate the provider behind one file and prove portability.
- Read: Ch 11 §11.5–11.7.
- Time: ~100 min (25 / 65 / 10).
- Exercise: `ch11/llm_client.py` with an `LLMClient` protocol, `GeminiClient`, `FakeClient`; optional second
  backend through the OpenAI-compatible endpoint (same key, `openai` SDK) or a local model via Ollama;
  run the summarizer through the adapter.
- Done when: summarizer code has no provider imports; tests use the fake; (optional) the same prompt ran through the second backend with notes on what differed.
- You can explain: what the adapter hides and what leaks through; why one component owns retries.

### D19 — Checkpoint 2: the article summarizer CLI 💲
- Objective: a small finished tool that exercises Ch 7–11.
- Read: Ch 11 checkpoint brief.
- Time: ~120 min.
- Exercise: `summarize_url.py <url>`: fetch → extract → structured summary → Markdown or JSON; exit codes; tests with `FakeClient`; tokens and attempts printed.
- Done when: works on three live URLs; tests pass offline; a README snippet exists.
- You can explain: the full request path and every failure-handling point.

### D20 — Review (lighter day)
- Objective: close Part III.
- Read: summaries of Ch 7–11.
- Time: ~75 min.
- Exercise: Ch 7–11 interview questions aloud; tidy notes; finish any skipped exercise; log usage.
- Done when: notes complete; backlog empty or written down.
- You can explain: tool use vs. structured outputs, and when to use each.

## Week 5 — Embeddings and search

### D21 — Embeddings in practice (free tier)
- Objective: embeddings in practice, including Hebrew.
- Read: Ch 12 §12.1–12.4.
- Time: ~100 min (30 / 60 / 10).
- Exercise: call the embeddings endpoint for 20 sentences (10 Hebrew / 10 English, paired meanings); similarity table; nearest neighbor for five queries; optional: run the same sentences through a local sentence-transformers model and compare.
- Done when: most pairs are mutual nearest neighbors; failures are noted.
- You can explain: what an embedding is and is not; why queries and documents must share a model; why multilingual models matter for Hebrew.

### D22 — Choosing models, caching, near-duplicates
- Objective: practical embedding engineering.
- Read: Ch 12 §12.5–12.8.
- Time: ~90 min (25 / 55 / 10).
- Exercise: embed 200 provided headlines; near-duplicate pairs at thresholds 0.80 / 0.85 / 0.90; cache embeddings on disk keyed by model + text hash.
- Done when: duplicate pairs are listed per threshold with a chosen threshold and justification; the cache hits on re-run.
- You can explain: why thresholds are not universal; why query and document texts get different task instructions; dimensionality vs. quality.

### D23 — Lexical search and BM25
- Objective: the retrieval method that still wins on identifiers.
- Read: Ch 13 §13.1–13.4.
- Time: ~90 min (30 / 50 / 10).
- Exercise: BM25 over the 200 headlines; ten queries including an error code and a paraphrase; compare top-5 with dense results.
- Done when: a table shows where lexical wins and where dense wins.
- You can explain: BM25 intuition (term frequency, rarity, length); why hybrid exists.

### D24 — ANN, hybrid search, reranking
- Objective: combining retrievers and re-scoring candidates.
- Read: Ch 13 §13.5–13.6.
- Time: ~100 min (30 / 60 / 10).
- Exercise: implement RRF; rerank the top 20 by having the fast model score each query–passage pair (the cross-encoder idea, done with the model you already have); compare orderings; time and count tokens per stage; optional: a local cross-encoder.
- Done when: RRF tests pass; reranking changes at least one top-3 result for a sensible reason; a latency table exists.
- You can explain: what ANN trades; why RRF uses ranks not scores; what a cross-encoder sees that a bi-encoder does not.

### D25 — Retrieval metrics and a labeled set
- Objective: measure retrieval before improving it.
- Read: Ch 13 §13.7–13.8.
- Time: ~100 min (25 / 65 / 10).
- Exercise: label 20 queries with relevant headline IDs; compute hit@3, recall@5, MRR for lexical, dense, hybrid, hybrid + rerank.
- Done when: a results table and a one-paragraph recommendation exist.
- You can explain: hit vs. recall vs. MRR; why you measure before adding a reranker.

## Week 6 — Vector database and RAG

### D26 — Vector databases and Chroma
- Objective: what a vector store adds, hands-on, and when you do not need one.
- Read: Ch 14.
- Time: ~100 min (35 / 55 / 10).
- Exercise: Chroma persistent client; a collection of headlines with source/date metadata; upsert; a date-filtered query; compare with your numpy search; reindex after switching the embedding model.
- Done when: same top-5 as numpy for a query; the filtered query works; the note answers "would numpy suffice here?".
- You can explain: Chroma vs. pgvector vs. Qdrant vs. numpy in one sentence each; why reindex on model change.

### D27 — Ingestion and chunking
- Objective: turning documents into units of evidence.
- Read: Ch 15 §15.1–15.4.
- Time: ~100 min (30 / 60 / 10).
- Exercise: chunk your Obsidian course notes two ways (fixed size + overlap; heading-based); inspect five chunks each; content-hash IDs; re-run skips unchanged files.
- Done when: two chunk sets with counts exist and a note says which preserved meaning better.
- You can explain: chunk = unit of evidence; the overlap tradeoff; why chunk IDs must be stable.

### D28 — Retrieval → context → grounded answer 💲
- Objective: the query path of RAG with citations and abstention.
- Read: Ch 15 §15.5–15.8.
- Time: ~110 min (30 / 70 / 10).
- Exercise: `ask_notes.py`: index notes in Chroma; retrieve top-k; build context with `[n]` IDs; answer with citations; validate IDs against the retrieved set; abstain when unsupported.
- Done when: three answerable and two unanswerable questions behave correctly; the invalid-citation path is tested.
- You can explain: grounding vs. correctness; why the model returns IDs rather than URLs; coverage vs. unsupported answers.

### D29 — Hybrid, long context vs. RAG, prompt caching 💲
- Objective: the improvements that are worth measuring.
- Read: Ch 15 §15.9–15.12.
- Time: ~100 min (30 / 60 / 10).
- Exercise: add hybrid retrieval; put the static instructions and documents first in the prompt and verify `total_cached_tokens` > 0 on a repeated call of the long-context variant (implicit caching needs a prefix of at least 4,096 tokens on the Flash models as of October 2026; the short RAG prompt stays at 0, and that is the lesson); compare the token cost of "all notes in context" vs. RAG for five questions.
- Done when: cache hits are verified; a cost/latency table compares long context and RAG.
- You can explain: the prefix-stability rule; when long context beats RAG and when it does not.

### D30 — Debugging by stage; Checkpoint 3
- Objective: locate failures by the stage where the evidence disappeared.
- Read: Ch 15 §15.13.
- Time: ~100 min (20 / 70 / 10).
- Exercise: inject three faults (remove a document; break chunking; tell the prompt to ignore context); locate each from your trace (chunks retrieved, context sent, answer); write the taxonomy note.
- Done when: each fault is localized with evidence; `ask_notes` is repo-ready with tests.
- You can explain: retrieval vs. generation failure; what to log to make the diagnosis possible.

## Week 7 — Evaluation

### D31 — Eval datasets
- Objective: expectations before results; dev vs. holdout.
- Read: Ch 16 §16.1–16.4.
- Time: ~110 min (30 / 70 / 10).
- Exercise: 30 cases for `ask_notes` (direct, paraphrase, multi-hop, unanswerable, adversarial, Hebrew) as JSONL with expected behavior; split 20 dev / 10 holdout grouping paraphrases together; implement the seven deterministic checks (`run_checks`) and run their tests.
- Done when: the cases file passes a schema test; the checks' tests pass; a note records the leakage you avoided.
- You can explain: why expectations are written first; holdout contamination through prompt edits.

### D32 — Metrics and the LLM judge 💲
- Objective: deterministic checks, reference-based metrics, a calibrated judge.
- Read: Ch 16 §16.5–16.8.
- Time: ~110 min (35 / 65 / 10).
- Exercise: a faithfulness judge with a rubric returning structured verdicts (the checks were built on D31; Cohen's kappa is provided, read it); run v1 on the dev set with the judge; hand-label ten answers; measure agreement and kappa; swap answer order in a pairwise test.
- Done when: agreement ≥ 8/10 or disagreements are documented; the position-bias observation is written.
- You can explain: where code beats a judge; judge biases; why two agreeing models are not truth.

### D33 — The harness and the report 💲
- Objective: repeatable evaluation with variance and cost.
- Read: Ch 16 §16.9–16.11.
- Time: ~100 min (25 / 65 / 10).
- Exercise: `evals/run.py`: run cases, metrics per category, repeat flaky cases ×3, write a report; compare prompt v2 vs. v3 on dev, then once on holdout.
- Done when: two reports exist and a decision memo gives numerators/denominators and the eval's cost.
- You can explain: regression gates; why per-category beats one score; what 9/10 on dev proves.

### D34 — Failure analysis 💲
- Objective: from traces to prioritized fixes.
- Read: Ch 17.
- Time: ~110 min (30 / 70 / 10).
- Exercise: review 30 traces; tag each failure; roll up to a taxonomy; apply the top two fixes; re-run; add regression cases.
- Done when: a before/after table exists and two regression cases are in the dev set.
- You can explain: your taxonomy; why you changed retrieval before the model; the role of regression cases.

### D35 — Testing AI applications; Checkpoint 4
- Objective: tests that run offline, evals that run on purpose.
- Read: Ch 18.
- Time: ~100 min (30 / 60 / 10).
- Exercise: pytest suite for the summarizer and `ask_notes`: fakes, recorded fixtures (record once, replay), contract tests for tool schemas, property-style assertions; `live` marker; `make test` vs. `make eval`.
- Done when: the fast suite runs offline in under ten seconds; live tests skip without a key.
- You can explain: the AI test pyramid; what fixtures hide and how evals cover it.

## Week 8 — Agents

### D36 — Workflows vs. agents; the five patterns 💲
- Objective: pick the least autonomy that works.
- Read: Ch 19 §19.1–19.4.
- Time: ~100 min (35 / 55 / 10).
- Exercise: routing (article type → prompt) and parallelization (asyncio over ten articles with a semaphore); measure latency vs. sequential.
- Done when: both patterns are tested and a latency table exists.
- You can explain: the four criteria for building an agent; a pattern for each of three scenarios.

### D37 — The agent loop with budgets 💲
- Objective: an agent you can stop, trace and test.
- Read: Ch 19 §19.5–19.8.
- Time: ~110 min (30 / 70 / 10).
- Exercise: a research agent with `fetch_url` and `search_web` (or local `search_feeds`), a state object, step/time/cost budgets, stop reasons, structured trace.
- Done when: it answers a topical question with sources in ≤6 steps; budget exhaustion returns a clear status.
- You can explain: what is in the state; why step limits do not replace timeouts; how to test an agent.

### D38 — Reliability: guardrails, approvals, idempotency
- Objective: agents that fail safely.
- Read: Ch 20 §20.1–20.4.
- Time: ~100 min (30 / 60 / 10).
- Exercise: loop detection (same tool + args twice); tool errors as results; a `send_email` tool gated by console approval; an idempotency key for side-effecting tools; failure-injection tests.
- Done when: tests for loop / approval / idempotent retry pass.
- You can explain: error laundering; why approval must show the exact action; idempotency vs. checkpoints.

### D39 — State, memory, persistence, resume
- Objective: what to remember, for whom, and how to continue after a crash.
- Read: Ch 20 §20.5–20.8.
- Time: ~100 min (30 / 60 / 10).
- Exercise: persist agent state to SQLite after each step; simulate a crash; resume by run ID; read a "user preferences" memory at start.
- Done when: the resume test passes and memory changes behavior.
- You can explain: conversation vs. task state vs. long-term memory; summarization risk.

### D40 — LangGraph 💲
- Objective: see what the framework buys and what it costs.
- Read: Ch 21 §21.1–21.3.
- Time: ~120 min (40 / 70 / 10).
- Exercise: rebuild the D37 agent as a StateGraph with SqliteSaver; add an interrupt before `send`; resume by thread ID. (The line count and the "LangGraph or loop?" decision note move to D42, which has slack.)
- Done when: the graph runs, stops at the interrupt, and resumes by thread ID.
- You can explain: what a checkpointer stores; what an interrupt is; three signs you have outgrown the loop.

## Week 9 — Frameworks wrap-up; production begins

### D41 — The landscape and MCP
- Objective: place every framework name; connect one MCP tool.
- Read: Ch 21 §21.4–21.7.
- Time: ~100 min (35 / 55 / 10).
- Exercise: run a filesystem MCP server (or a 20-line custom one); list tools; call one from your loop; write the security note on untrusted tool descriptions and results.
- Done when: an MCP tool call appears in your trace; the landscape table is in your notes.
- You can explain: what MCP standardizes and what it does not (authorization); how you would choose among frameworks.

### D42 — Checkpoint 5: agents; the Morning Brief sketch
- Objective: close Part VI and draft the project pipeline.
- Read: summaries of Ch 19–21.
- Time: ~90 min.
- Exercise: compare the LangGraph graph with the hand-written loop (line counts, readability) and write the "LangGraph or loop?" decision note; Ch 19–21 interview questions aloud; sketch the Morning Brief pipeline (stages; which are workflow vs. agent; where state lives).
- Done when: the decision note and the sketch are saved (the sketch is refined in Ch 30).
- You can explain: your pipeline on a whiteboard in three minutes.

### D43 — Observability: a tracer you own 💲
- Objective: see every call's model, tokens, cost and latency.
- Read: Ch 22 §22.1–22.5.
- Time: ~100 min (30 / 60 / 10).
- Exercise: `tracing.py` (span context manager → JSONL with trace ID, model, tokens, cost, latency, cache hits, tool names); instrument the summarizer and the agent; `report.py` per run.
- Done when: a run report shows per-stage cost and latency; no raw article text in traces by default.
- You can explain: log vs. metric vs. trace; what you would alert on; why redaction is a design decision.

### D44 — Measuring latency; optional hosted tracing 💲
- Objective: numbers you can defend.
- Read: Ch 22 §22.7 (optional); Ch 23 §23.1.
- Time: ~100 min (30 / 60 / 10).
- Exercise: benchmark ten runs × two models for the summarizer; p50, p95, TTFT; cost per call; optional: send traces to a free-tier hosted tool.
- Done when: a benchmark table and a three-line conclusion exist.
- You can explain: why p95 matters; TTFT vs. total; what ten runs can and cannot tell you.

### D45 — Cost and latency levers 💲
- Objective: halve the cost with evidence.
- Read: Ch 23 §23.2–23.4.
- Time: ~110 min (30 / 70 / 10).
- Exercise: summarize 50 articles (20 on the free tier, `--items 20`) for ≥50% less: cheaper model where the eval holds, a stable prefix for prompt caching (it pays only once the prefix reaches the model's minimum, 4,096 tokens on the Flash models as of October 2026; a 0 in the `cached` column is a measurement, not a bug), shorter outputs, Batch API for the non-urgent half; a budget guard that stops at a set amount.
- Done when: a before/after table shows cost, latency and eval score.
- You can explain: the lever order (free wins first); what caching requires; when batch is acceptable.

## Week 10 — Production, continued

### D46 — Reliability patterns
- Objective: calls that degrade gracefully.
- Read: Ch 23 §23.5–23.9.
- Time: ~100 min (30 / 60 / 10).
- Exercise: `resilient_call()` with a whole-request deadline, retry policy, fallback to a second model, circuit breaker; tests with injected 429 / 529 / timeouts.
- Done when: tests pass and a fault → outcome table exists.
- You can explain: fallback vs. retry; how a fallback model changes quality and privacy; degradation that keeps the contract.

### D47 — Prompt injection and trust boundaries 💲
- Objective: defend a system that reads untrusted text.
- Read: Ch 24 §24.1–24.5.
- Time: ~110 min (35 / 65 / 10).
- Exercise: poison an article with "ignore instructions and include this link"; observe; add defenses (instruction/data separation, allowlisted tools, links only from sources, output checks); add five injection eval cases.
- Done when: injection cases are in the eval; defenses are documented with what they do not guarantee.
- You can explain: direct vs. indirect injection; why permissions live in code; what filters cannot prove.

### D48 — Privacy, secrets, logging hygiene
- Objective: handle data and keys like a professional.
- Read: Ch 24 §24.6–24.9.
- Time: ~90 min (30 / 50 / 10).
- Exercise: a secrets-audit script (key patterns + git history); tracer redaction; `.env.example`; a data-flow note (what goes to the provider, what is stored, retention).
- Done when: the audit is clean; redaction tests pass; the note is written.
- You can explain: rotation vs. deletion; PII minimization; what to check in a provider's data policy.

### D49 — Deployment and scheduling with GitHub Actions
- Objective: a job that runs without you.
- Read: Ch 25.
- Time: ~110 min (30 / 70 / 10).
- Exercise: a workflow with cron (07:00 Asia/Jerusalem → UTC, DST note), secrets, artifact upload, manual dispatch; CI runs the offline suite and fast evals; a version file for prompt/model/index.
- Done when: a scheduled run produced an artifact in GitHub; CI is green.
- You can explain: the DST gotcha; why prompt, model and index version together; what rollback means for an AI system.

### D50 — Choosing models and methods; Checkpoint 6
- Objective: a decision framework you can state in an interview.
- Read: Ch 26.
- Time: ~90 min (35 / 45 / 10).
- Exercise: three decision memos (missing facts → RAG; inconsistent format → schema; narrow classification failing → data, maybe fine-tuning) plus "API vs. open-weights" for a privacy-sensitive case; Ch 22–26 interview questions aloud.
- Done when: memos written; questions answered.
- You can explain: the decision table; when fine-tuning is justified; the real cost of a local model.

## Week 11 — Project: M1 (sources) and M2 (summaries, ranking)

### D51 — Ch 30 and M1: repo, config, store
- Objective: understand the spec; lay the foundation.
- Read: Ch 30; Ch 31 M1 brief.
- Time: ~110 min (40 / 60 / 10).
- Exercise: repo skeleton from the template; `profile.yaml`; `Settings` via pydantic-settings; `store.py` with articles/runs/deliveries tables and migrations; tests.
- Done when: `uv run pytest` is green and `morning-brief --help` works.
- You can explain: the pipeline stages and where each lives in the repo.

### D52 — M1: sources
- Objective: collect and normalize articles idempotently.
- Read: M1 brief (sources).
- Time: ~110 min (20 / 80 / 10).
- Exercise: `sources/rss.py` (three to five feeds from the provided list) and `sources/hn.py`; normalize to `Article`; dedupe by canonical URL hash; `fetch` command; recorded feed fixtures.
- Done when: a run stores ≥50 articles; a re-run inserts zero duplicates.
- You can explain: normalization and canonical IDs; why fixtures for feeds.

### D53 — M1: extraction
- Objective: main text, politely and robustly.
- Read: M1 brief (extraction).
- Time: ~100 min (20 / 70 / 10).
- Exercise: `extract.py` (httpx with timeouts + trafilatura; max length; bounded concurrency; skip non-HTML); cache raw HTML by URL hash; per-article failures do not fail the run.
- Done when: ≥80% of articles extract; failures are counted in the run report.
- You can explain: the partial-failure policy; why text length is capped.

### D54 — M2: summaries 💲
- Objective: structured summaries at scale with cost accounting.
- Read: M2 brief (summaries).
- Time: ~110 min (20 / 80 / 10).
- Exercise: `summarize.py` with the Ch 9 schema through the Ch 11 adapter; asyncio + semaphore; the Ch 22 tracer; per-article cost.
- Done when: summaries are stored for a day's articles; the run report shows cost.
- You can explain: your schema fields and why; concurrency limits vs. rate limits.

### D55 — M2: relevance scoring 💲
- Objective: rank for one specific reader.
- Read: M2 brief (ranking).
- Time: ~110 min (25 / 75 / 10).
- Exercise: `rank.py`: LLM relevance score 0–100 with a reason against `profile.yaml`, plus rule boosts (source weight, recency); tests with the fake client; 20 golden labels.
- Done when: the top ten for a real day looks right to you and golden agreement is measured.
- You can explain: why score + reason; where rules beat the model.

## Week 12 — Project: M3 (dedup and memory), M4 (orchestration, research), M5 (composition)

### D56 — M3: near-duplicate grouping
- Objective: one story, many sources.
- Read: M3 brief (dedup).
- Time: ~100 min (20 / 70 / 10).
- Exercise: embed title + lead; cluster near-duplicates across feeds with the D22 threshold; choose a representative; keep "also covered by" links.
- Done when: duplicate groups show in the preview; tests pass on a synthetic duplicate set.
- You can explain: your threshold; why embeddings here but not for ranking.

### D57 — M3: story memory with Chroma
- Objective: "you saw this on Tuesday".
- Read: M3 brief (memory).
- Time: ~100 min (20 / 70 / 10).
- Exercise: `memory.py`: a persistent Chroma collection of past story embeddings with date metadata; follow-up detection; a retention window; the decision note vs. a SQLite blob scan.
- Done when: a story repeated the next day is flagged as a follow-up; tests pass.
- You can explain: why Chroma is justified here and that SQLite would also do at this scale.

### D58 — M4: the orchestrated pipeline
- Objective: explicit stages, resumable runs, a cost ceiling.
- Read: M4 brief (orchestration).
- Time: ~110 min (25 / 75 / 10).
- Exercise: `pipeline.run(date)` with stage artifacts in `runs/<date>/`, resume from the last complete stage, a budget guard, a run report.
- Done when: a full run completes and a re-run resumes from the last complete stage.
- You can explain: workflow vs. agent in this pipeline; why artifacts per stage.

### D59 — M4: the bounded research step 💲
- Objective: a little autonomy where it pays.
- Read: M4 brief (research).
- Time: ~110 min (20 / 80 / 10).
- Exercise: for the top three stories, the Ch 19–20 agent with `fetch_url` (+ optional search) adds context and a key fact; step/time/cost budgets; traced.
- Done when: three enriched stories carry sources; budget tests pass.
- You can explain: why this step is agentic and the rest is not; how you bound it.

### D60 — M5: composition 💲
- Objective: from structured inputs to a readable issue.
- Read: M5 brief (composition).
- Time: ~110 min (25 / 75 / 10).
- Exercise: the `Issue` model (sections; items with title, summary, why, links, citations); the composer prompt on the stronger model; render Markdown and HTML with Jinja2; `preview` command.
- Done when: a readable issue exists in both formats and every claim is linked.
- You can explain: why composition takes structured inputs, not raw text; model tiering here.

## Week 13 — Project: M5 (delivery), M6 (evaluation), M7 (operations)

### D61 — M5: delivery
- Objective: send once, safely.
- Read: M5 brief (delivery).
- Time: ~100 min (20 / 70 / 10).
- Exercise: `deliver/file.py` (default); `deliver/email.py` (SMTP with a Gmail app password, exact setup); a delivery record that prevents double-sending; `--dry-run`; optional Telegram.
- Done when: the issue arrives in your inbox and a second send attempt is a no-op.
- You can explain: idempotent delivery; secrets handling for SMTP.

### D62 — M6: the evaluation set and harness 💲
- Objective: know when the newsletter got worse.
- Read: M6 brief (evaluation).
- Time: ~110 min (20 / 80 / 10).
- Exercise: golden set (60 relevance-labeled articles; 20 summary-faithfulness cases; 5 injection cases); `evals/run_eval.py` with deterministic checks and the Ch 16 judge rubric; a report with thresholds.
- Done when: a baseline report is committed.
- You can explain: what each metric proves; why a judge for faithfulness and rules for links.

### D63 — M6: error analysis on a real issue 💲
- Objective: improve with evidence.
- Read: M6 brief (error analysis).
- Time: ~100 min (15 / 75 / 10).
- Exercise: Ch 17 error analysis on a real issue; fix the top two problems; re-run; add regression cases.
- Done when: a before/after table is in `docs/eval.md`.
- You can explain: your failure taxonomy for this product.

### D64 — M7: observability and reliability
- Objective: a daily job you can trust and diagnose.
- Read: M7 brief (operations).
- Time: ~100 min (20 / 70 / 10).
- Exercise: per-run trace and report (per stage: items, tokens, cost, latency, failures); `resilient_call` with a fallback model; a dead feed or a provider 529 does not kill the run.
- Done when: failure-injection tests pass and the report shows partial failures.
- You can explain: what you would alert on for a daily job.

### D65 — M7: the cost pass 💲
- Objective: cents per issue, measured.
- Read: M7 brief (cost).
- Time: ~100 min (15 / 75 / 10).
- Exercise: tiering (cheap model for scoring and summaries, stronger for composition); prompt caching for profile + instructions where the prefix reaches the 4,096-token minimum (verify hits; record a 0 honestly and drop the lever if it never pays); shorter outputs; Batch API for summaries if latency allows; cost per issue before/after with the eval unchanged.
- Done when: the cost-per-issue table exists and the eval did not regress.
- You can explain: your cost budget and how the code enforces it.

## Week 14 — Project: M8 (security), M9 (scheduling, documentation), optional extension

### D66 — M8: security hardening 💲
- Objective: a feed cannot hijack your newsletter.
- Read: M8 brief (hardening).
- Time: ~100 min (20 / 70 / 10).
- Exercise: a poisoned-feed test item; instruction/data separation in all prompts; HTML sanitization of rendered output; a link allowlist (URLs only from fetched sources); secrets audit.
- Done when: the injection eval passes and sanitizer tests pass.
- You can explain: your trust boundaries; what remains unproven.

### D67 — M8: privacy and robustness
- Objective: know what you store and survive bad days.
- Read: M8 brief (privacy, chaos).
- Time: ~90 min (15 / 65 / 10).
- Exercise: a data-flow note (sent / stored / retention); PII minimization in the profile; logging hygiene; chaos tests (network down, malformed feed, empty day).
- Done when: tests pass and `docs/security.md` is written.
- You can explain: what you would change for a multi-user product.

### D68 — M9: scheduling
- Objective: it runs at 07:00 without you.
- Read: M9 brief (scheduling).
- Time: ~100 min (15 / 75 / 10).
- Exercise: GitHub Actions cron at 07:00 Israel time (UTC conversion and the DST caveat), secrets, artifacts, manual dispatch; the Windows Task Scheduler alternative documented.
- Done when: a scheduled run delivered an issue while you were not at the keyboard.
- You can explain: why GitHub Actions here; the cron/DST pitfall; secrets in CI.

### D69 — M9: documentation
- Objective: a stranger can run and judge it.
- Read: M9 brief (docs); Ch 29 README section.
- Time: ~110 min (15 / 85 / 10).
- Exercise: README (structure from Ch 29); `docs/architecture.md` with the Mermaid diagram; decisions and alternatives (ADR-lite); eval results; cost per issue; demo script.
- Done when: someone else could run it in ten minutes from the README alone.
- You can explain: every box in the diagram and the alternative you rejected.

### D70 — Optional extension or buffer
- Objective: either the LangGraph approval gate, or a clear backlog.
- Read: Ch 31 optional extension brief.
- Time: ~100 min.
- Exercise (optional): draft → interrupt → approve via CLI → send, with SqliteSaver resume; a decision note on when the gate is worth the framework.
- Done when: the extension works with its note, or the backlog is empty.
- You can explain: when a human gate justifies a framework.

## Week 15 — Career

### D71 — System design: framework; cases 1–2
- Objective: a repeatable way to design under time pressure.
- Read: Ch 27 §27.1–27.4.
- Time: ~100 min.
- Exercise: 25-minute timed design, aloud, for Morning Brief and for document QA with permissions; compare with the worked answers.
- Done when: both are recorded (notes or audio) and gaps are listed.
- You can explain: the eight-step framework.

### D72 — System design: cases 3–5
- Objective: breadth across system shapes.
- Read: Ch 27 §27.5–27.7.
- Time: ~100 min.
- Exercise: the same drill for a support assistant with actions, a classification pipeline at scale, and batch PDF extraction.
- Done when: three designs exist and recurring weak spots are noted.
- You can explain: tradeoffs of agents with side effects; batch vs. real time.

### D73 — Question bank, part 1
- Objective: active recall on fundamentals, APIs, prompting, RAG.
- Read: Ch 28 part 1.
- Time: ~90 min.
- Exercise: answer 20 questions aloud before reading the model answers; mark gaps; fix notes.
- Done when: at most four gaps remain.
- You can explain: each answer with an example from your own code.

### D74 — Question bank, part 2; tradeoff drills
- Objective: evals, agents, production, security; arguing tradeoffs.
- Read: Ch 28 part 2.
- Time: ~90 min.
- Exercise: 20 questions; then three "why not X?" drills.
- Done when: at most four gaps remain.
- You can explain: name the alternative, its cost, your evidence.

### D75 — Portfolio, CV, pitch
- Objective: the project in three minutes and three bullets.
- Read: Ch 29.
- Time: ~100 min.
- Exercise: finalize the README; three CV bullets with the formula; a LinkedIn summary; record and time a three-minute pitch.
- Done when: the pitch is ≤3:30 and covers problem, evidence, decision, limits.
- You can explain: your project honestly in three minutes.

## Week 16 — Consolidation

### D76 — Mock interview 1 (technical)
- Time: ~90 min. Exercise: a 45-minute mock from a randomized Ch 28 set (alone, or with a friend), then 45 minutes of review against the model answers.
- Done when: scored; three fixes written down.

### D77 — Mock interview 2 (system design)
- Time: ~90 min. Exercise: the unseen case from Ch 27, 40 minutes aloud; review against the framework.
- Done when: self-scored; two fixes written down.

### D78 — Project polish and publish
- Time: ~100 min. Exercise: CI green; final eval run; secrets and employer-data audit; tag v1.0; publish the repository.
- Done when: a public link exists and the README shows a real issue.

### D79 — Checklists
- Time: ~75 min. Exercise: appendix E learning checklist and interview-readiness checklist; name three weak areas; schedule revisits.
- Done when: both checklists are filled honestly.

### D80 — Retrospective and next steps
- Time: ~60 min. Exercise: write the retrospective (built, measured, would do differently); choose enrichment paths (Huyen chapters, fine-tuning, multimodal, hosted observability, deeper LangGraph); set a job-search cadence.
- Done when: the retrospective and a next-step plan exist.

---

## Checkpoints at a glance

| Checkpoint | Day | Proves |
| --- | --- | --- |
| 1 | D10 | You can explain models, tokens, sampling and evaluation basics |
| 2 | D19 | You can build a tool with structured outputs, tools, streaming and tests |
| 3 | D30 | You can build and debug a RAG system over real documents |
| 4 | D35 | You can evaluate and test an AI system honestly |
| 5 | D42 | You can build, bound and persist an agent, and justify a framework |
| 6 | D50 | You can operate, secure, deploy and reason about cost |
| Final | D78 | A published, evaluated, scheduled portfolio project |
