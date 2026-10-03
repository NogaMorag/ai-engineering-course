# Stage 1 — Quality-control checklist (from the brief), answered for the proposed design

| Check | Status | Evidence / note |
| --- | --- | --- |
| Every major topic supports a real AI Engineering skill | Yes | Each chapter in file 02 names the employable skill and the exercise that practices it; theory chapters (3–6) are capped at seven study days and each ends in a script. |
| Each exercise is connected to the material immediately preceding it | Yes | File 03: every day's exercise references the sections read that day; no "bonus" exercises unrelated to the lesson. |
| The sequence never relies on unexplained concepts | Yes, by construction | Dependency order: tokens/cost (D3,D7) → API (D11) → structured outputs (D14) → tools (D15) → embeddings (D21) → search (D23) → vector DB (D26) → RAG (D27) → evals (D31) → agents (D36) → LangGraph (D40) → production (D43) → project (D51). Stage 3 re-checks every term against its first definition. |
| Daily workload realistic for 1–2 hours | Yes | 80 days × 75–120 min; one lighter/review day per week; six checkpoints; two buffer days; "if behind, skip optional extensions first" rule. |
| No prior AI/ML knowledge assumed | Yes | Part II defines model, parameters, training, inference, embeddings, context window, sampling before any API term is used; every English term explained in Hebrew on first use. |
| Instructions detailed enough for an unfamiliar tool | Yes (Stage 2 obligation) | Every install (winget, uv, Git, VS Code, the Gemini API key, Chroma, LangGraph, Ollama, Gmail app password, GitHub Actions secrets) follows the 10-point template from the brief: what/why, where, version, commands, folders, where to run, verify, expected output, common errors, stop/cleanup. |
| Prepares to build and explain systems, not follow tutorials | Yes | Every milestone has a decisions-and-alternatives table; Ch 27 trains the design framework on five cases including the project; Ch 28 is a Q&A bank answered from your own code. |
| Final project demonstrates skills employers value | Yes | Structured outputs, tool use, bounded agent, embeddings + vector store (justified), evals with a judge, tracing and cost accounting, retries/fallbacks, injection defenses, scheduled deployment, tests, README + architecture diagram. |
| Not dominated by one framework or vendor | Yes, with one explicit choice | One primary model API (Gemini, chosen as the cheapest viable option: a real free tier) behind a one-file adapter, demonstrated on a second backend (the OpenAI-compatible endpoint or Ollama); LangGraph confined to one chapter + one optional milestone; no LangChain/LlamaIndex as frameworks; every concept taught provider-neutrally. |
| Topics from the attached plan kept/changed/removed for a clear reason | Yes | File 01 §5 (per-chapter disposition) and §6 (gap map). |

The decisions taken on 2026-10-03 are recorded in `07-decisions-2026-10-03.md`.
