# Two commands, two meanings. `test` is offline and free. `eval` calls the model and costs money.
.PHONY: test eval run offline lint
test:
	uv run pytest -q -m "not judge"
eval:
	uv run --env-file .env python -m evals.run_eval --out docs/eval-latest.md
run:
	uv run --env-file .env morning-brief run
offline:
	uv run morning-brief run --offline --out out
lint:
	uv run ruff check .
