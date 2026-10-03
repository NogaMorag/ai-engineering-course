# Stage 1 — The minimal technical stack and why (revised 2026-10-03)

Applied decisions: a **Windows** laptop, the **cheapest viable** API, everything **built from
scratch**, and a book that reads correctly **right-to-left**. One consistent stack for the whole
course; a tool enters only when it teaches a transferable concept or reflects a realistic
professional workflow. Versions were checked on PyPI on 2026-10-03; the book pins exact versions in
`pyproject.toml`, never in prose.

## 1. Runtime and workflow (Windows 11)

| Piece | Choice | Why |
| --- | --- | --- |
| Shell | Windows Terminal with PowerShell 7 (`winget install Microsoft.PowerShell`) | Native Windows; no WSL required. Every command in the book is PowerShell. A one-paragraph note covers WSL2 for readers who prefer Linux tooling. |
| Installer | `winget` | Built into Windows 11; one command per tool; easy to verify and uninstall. |
| Python | 3.12 via `uv python install 3.12` | Every library below ships Windows wheels for 3.12. |
| Package and environment manager | uv (`winget install --id=astral-sh.uv -e`) | You already use it. Lockfile, `uv run`, `uv add`, and `uv run --env-file .env` for secrets. No pip. |
| Editor | VS Code (`winget install Microsoft.VisualStudioCode`) + Python extension | Cursor works identically if you prefer it. |
| Git | `winget install Git.Git` | Portfolio repository and GitHub Actions. |
| Text encoding | `PYTHONUTF8=1` as a user environment variable | Windows consoles default to a legacy code page; without this, Hebrew output shows as `?` or raises `UnicodeEncodeError`. Set once on Day 2. |
| Tests and lint | `pytest`, `ruff` | Standard. |
| Notes | Obsidian with the "RTL Support" community plugin | Per-note right-to-left; the book ships a ready note per chapter. |
| Reading the book | Generated HTML (`tools/build_html.py` → `site/`) or Obsidian | Markdown renderers on the web do not lay Hebrew out well; the HTML build does. |

## 2. Model API — Google Gemini on the free tier, via the `google-genai` SDK

**Why this is the cheapest viable option (checked 2026-10-03):**

| Option | Price per 1M tokens (input / output) | Free tier | Notes |
| --- | --- | --- | --- |
| **Gemini 3.5 Flash-Lite** (`gemini-3.5-flash-lite`) | $0.30 / $2.50 | **Yes** | Default "fast" model. Stable since July 2026. Thinking off by default. |
| **Gemini 3.8 Flash** (`gemini-3.8-flash`) | $0.75 / $3.75 (promotional through 2026-12-31) | **Yes** | Default "smart" model. Stable since Sept 2026. |
| Gemini 3.1 Flash-Lite | $0.25 / $1.50 | Yes | Cheapest paid fallback available to new accounts. |
| Gemini 2.5 Flash-Lite | $0.10 / $0.40 | Yes | Cheapest on paper, but since 2026-09-18 restricted to accounts that already used it. |
| Gemini Embedding 2 (`gemini-embedding-2`) | $0.20 input | **Yes** | Multilingual, 128–3072 dimensions. |
| OpenAI GPT-5 nano | $0.05 / $0.40 | No (prepaid) | Cheapest per token among paid-only options. |
| Claude Haiku 4.5 | $1.00 / $5.00 | No (prepaid) | |
| Ollama (local open-weights) | $0 | n/a | Slow on a CPU laptop; weaker tool calling. Optional. |

- **Free tier**: no credit card; Flash, Flash-Lite and embedding models included; rate limits are
  shown per model in AI Studio (third-party reports put them around 10–30 requests per minute and
  250–1,500 per day; verify in your own console). Free-tier content *may be used by Google to improve
  its products*; the course uses only public and synthetic data, so that is acceptable. For the
  newsletter, which includes your interests profile, you can prepay $5 once for **Tier 1**: content
  is then not used for training, limits rise, and the $5 lasts for months at these prices.
- **Default models** live only in `.env`: `MODEL_FAST=gemini-3.5-flash-lite`,
  `MODEL_SMART=gemini-3.8-flash`. Code never names a model. Google shipped three new Flash models in
  the three months before this was written; the book teaches "check the models page", not names.
- **API surface**: the **Interactions API** (`client.interactions.create(model=..., input=...)`),
  Google's recommended surface for new projects since June 2026 and the one its documentation now
  teaches. Its shape (an `input`, an `output_text`, a list of `steps`, `previous_interaction_id`,
  `response_format`, `tools`) closely resembles OpenAI's Responses API, so what you learn transfers.
  The older `generateContent` API remains supported and appears only where a feature lives there
  (explicit context caching, token counting, embeddings, batch jobs).
- **SDK**: `google-genai`, pinned `>=2.28,<3` (version 3 has announced breaking changes around
  automatic function calling, which the book never uses: we write the tool loop ourselves).
- **Portability**: Chapter 11 runs the same program through Gemini's OpenAI-compatible endpoint with
  the `openai` SDK (same key) and optionally through Ollama; everything else sits behind a one-file
  adapter. Concepts (roles, tool loop, schemas, sampling, caching) are taught provider-neutrally.
- **If you ever switch to OpenAI or Claude**: the SDK and request shapes in Chapters 7–11, the
  embeddings source, and the price appendix change; nothing else does.

## 3. Embeddings, search, storage

| Piece | Choice | Why / alternative |
| --- | --- | --- |
| Embeddings | `gemini-embedding-2` through `client.models.embed_content`, `output_dimensionality=768` | Free tier, multilingual (Hebrew included), nothing to install. Task instructions go into the text itself, which the book connects to the "query vs. document" idea. **Optional box**: run `sentence-transformers` locally (CPU-only wheel on Windows, ~200 MB) and compare. |
| Reranking | The fast model scores each query–passage pair | Teaches the cross-encoder idea with the tool you already have, at $0. Optional box: a local cross-encoder; Cohere Rerank named as the hosted option. |
| Lexical search | `rank-bm25` | A real algorithm in 100 lines; makes "hybrid" concrete. |
| Vector database | `chromadb` 1.x (embedded, persistent, Windows wheels) | Zero-server; collections, metadata filters, upserts, ANN; landscape table covers pgvector, Qdrant, Weaviate, Pinecone, FAISS, sqlite-vec. |
| Relational state | `sqlite3` (standard library) | Articles, runs, deliveries, agent checkpoints. |
| Numerics | `numpy` | Cosine by hand before any database. |

## 4. Data, validation, web

| Piece | Choice | Why |
| --- | --- | --- |
| Schemas and validation | `pydantic` v2 (+ `pydantic-settings`) | Structured outputs (`model_json_schema()` → `response_format`, `model_validate_json()` ← `output_text`), tool arguments, config. |
| HTTP | `httpx` | Sync and async, timeouts. |
| Feeds | `feedparser` | RSS/Atom. |
| Article extraction | `trafilatura` | Main text from HTML; free. |
| Templates / rendering | `jinja2`, `markdown` | Newsletter to Markdown and HTML; also used by the book's own HTML build. |
| Email delivery | `smtplib` (standard library) with a Gmail app password | Free. File delivery is the default; Telegram optional. |

## 5. Agents, frameworks, protocols

| Piece | Choice | Scope |
| --- | --- | --- |
| Agent loop | Hand-written (`while` a step of type `function_call` exists) | Ch 10, 19–20, project research step. |
| LangGraph | `langgraph` 1.x with `SqliteSaver` | Ch 21 (rebuild the agent, add an interrupt) + one optional project milestone. |
| MCP | `mcp` Python SDK | One light hands-on lesson (Ch 21). |
| Not used as frameworks | LangChain, LlamaIndex, CrewAI, AutoGen, Pydantic AI | One-page landscape only. |

## 6. Observability, evaluation, deployment

| Piece | Choice | Why |
| --- | --- | --- |
| Tracing | Your own `tracing.py`: JSONL spans (trace id, model, tokens incl. cached and thought tokens, latency) | You understand what hosted tools store. Optional: Langfuse free tier. |
| Evals | Your own harness (JSONL cases → runner → per-category report) + LLM-as-judge with a rubric | Teaches the mechanism; `promptfoo` / `inspect-ai` named for awareness. |
| Scheduling and deployment | GitHub Actions `schedule:` cron + secrets + artifacts | Free, realistic; the laptop may be off at 07:00. Local alternative: Windows Task Scheduler. |
| Containers | Docker — optional box only | You use containers at work already. |

## 7. Reading format (the "well indented for a Hebrew reader" requirement)

- Source of truth: Markdown in `book/`, UTF-8, each chapter wrapped in a right-to-left container and
  every code/command block in a left-to-right container, following `book/CONVENTIONS.md`.
- `tools/build_html.py` renders every chapter to `site/*.html` with CSS that sets Hebrew text
  right-to-left and right-aligned, keeps code left-to-right, and styles tables, callouts and
  numbered sections. Open the HTML in any browser.
- Obsidian: install the "RTL Support" plugin, set default direction to RTL (or use the front-matter
  key the plugin reads); the notes shipped with the book carry that key.
- Writing rules inside the Hebrew text: short paragraphs; numbered sections; a sentence never starts
  with a Latin word; English terms appear in parentheses after the Hebrew term or inside backticks;
  commands and code only in code blocks.

## 8. Cost estimate

- **Course**: $0 on the free tier, provided you respect the per-minute limits (the exercises
  throttle). If you prepay $5 for Tier 1, the whole course costs roughly $1–3 at Flash-Lite prices.
- **Morning Brief, one issue**: $0 on the free tier (about 120–150 requests per run, spread over a
  few minutes). Paid fallback, about 60 articles × ~1.5K input / ~300 output tokens on Flash-Lite
  plus one Flash composition call: roughly **$0.06–0.10 per issue**, $2–3 per month.
- **Everything else is free**: embeddings on the free tier, Chroma, SQLite, GitHub Actions (public
  repo, or ~2,000 private minutes per month), Gmail SMTP.

## 9. Deliberately excluded

Fine-tuning tooling, quantization, LoRA (one decision page in Ch 26); multimodal depth (one
awareness page); Jupyter (optional); cloud accounts, Postgres, Docker, Kubernetes (nothing needs
them and you already know them); hosted eval/observability platforms (named, optional).
