# CV bullets: what · decision · evidence

Formula: **Built <what> (<stack>); <the decision you made and why>; <the measured result, with a denominator>.**

Six examples from the course project. Every X, N, A, B is a placeholder: fill it only from your own run report or
eval report. A number you did not measure does not go on a CV.

- Built a scheduled newsletter agent (Python, Gemini API, SQLite, Chroma) that turns ~N daily articles from K feeds into a personalized brief; kept the pipeline a plain workflow with a single bounded agent stage; runs at $X per issue with a hard budget stop at $0.25.
- Designed a four-part evaluation (relevance, faithfulness, grouping, injection) with thresholds as a regression gate; calibrated the faithfulness judge against N of my own labels (agreement A, kappa B) and used the eval to move summaries to a cheaper model with no measured loss.
- Built cross-day story memory on Chroma with a date filter, and same-day dedupe with a numpy scan; chose the similarity threshold from N labeled pairs (precision A, recall B).
- Hardened the pipeline against indirect prompt injection: output policy (links only from fetched sources), allowlisted read-only tools, delivery kept outside the agent, five injection cases in the eval at a 1.0 pass threshold; documented what the defenses do not guarantee.
- Built observability I own: JSONL traces per run with cost and latency per stage, redaction by default; a budget guard that stops a run at $0.25.
- Deployed on GitHub Actions with DST-aware scheduling, secrets, artifacts, idempotent delivery and a versions file tying prompt, model and index together.

Your three:

1. Built ___ ; ___ ; ___ .
2. Built ___ ; ___ ; ___ .
3. Built ___ ; ___ ; ___ .

Apply the same formula to your previous roles (C++/Rust/Python, systems): a systems engineer who learned AI is worth more than someone who learned only AI.
