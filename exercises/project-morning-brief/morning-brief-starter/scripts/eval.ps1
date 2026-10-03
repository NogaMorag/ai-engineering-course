# Paid: calls the model. Writes docs/eval-latest.md.
uv run --env-file .env python -m evals.run_eval --out docs/eval-latest.md
