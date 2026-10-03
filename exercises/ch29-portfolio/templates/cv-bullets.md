# CV bullets: what · decision · evidence

Formula: **Built <what> (<stack>); <the decision you made and why>; <the measured result, with a denominator>.**

Six examples from the course project (edit the numbers to yours):

- Built a scheduled newsletter agent (Python, Gemini API, Chroma) that turns 40 daily articles into a personalized brief; kept the pipeline a plain workflow with a single bounded agent step; runs at $0.08 per issue with a 95% faithfulness score on a 30-case eval.
- Designed the evaluation harness: 30 labeled cases across six categories, deterministic checks plus a calibrated LLM judge (kappa 0.8 against my labels); used it to pick the cheaper model with no loss in validity, cutting cost 64%.
- Implemented hybrid retrieval (BM25 + embeddings, reciprocal rank fusion); measured recall@5 from 0.78 to 0.85 on 20 labeled queries before adding a reranker.
- Hardened the pipeline against indirect prompt injection: output policy (links only from sources), allowlisted read-only tools, five injection cases in the eval; documented what the defenses do not guarantee.
- Built observability I own: JSONL traces per run with cost and latency per stage, redaction by default; a budget guard that stops a run at $0.25.
- Deployed on GitHub Actions with DST-aware scheduling, secrets, artifacts and a versions file tying prompt, model and index together; one-command rollback.

Your three:

1. Built ___ ; ___ ; ___ .
2. Built ___ ; ___ ; ___ .
3. Built ___ ; ___ ; ___ .

Apply the same formula to your previous roles (C++/Rust/Python, systems): a systems engineer who learned AI is worth more than someone who learned only AI.
