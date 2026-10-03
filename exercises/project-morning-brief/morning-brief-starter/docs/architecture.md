# Architecture

## The pipeline

Nine stages, one run per morning. Each stage writes an artifact to `data/runs/<date>/<stage>.json`; `--resume` skips
stages whose artifact exists. One failing feed, article or model call is a line in the run report, never a dead run.

| # | stage | model | shape | module |
| --- | --- | --- | --- | --- |
| 1 | collect | no | workflow | `sources/` |
| 2 | extract | no | workflow (thread pool, per-article isolation) | `extract.py` |
| 3 | summarize | fast, structured | workflow | `summarize.py` |
| 4 | score | fast + rules | workflow | `rank.py` |
| 5 | group + memory | embeddings | workflow | `cluster.py`, `memory.py` |
| 6 | research | smart + tools | **bounded agent** | `research.py` |
| 7 | compose | smart (intro only) + code | workflow | `compose.py`, `render/` |
| 8 | deliver | no | workflow, idempotent | `deliver/` |
| 9 | report | no | workflow | `tracing.py`, `report.py` |

**Where the model is used.** Summaries, relevance with a reason, the research note, and the two-sentence intro. Everything
else is code: canonical URLs, source weights, recency decay, skip topics, clustering, follow-up detection, composition,
rendering with autoescape, link policy, delivery, budgets, scheduling.

## Data

| store | what | retention |
| --- | --- | --- |
| SQLite `articles` | one row per canonical URL; text and extraction status | pruned by `fetched_at` |
| SQLite `summaries` | one summary per article per schema version; never paid for twice | with the article |
| SQLite `scores`, `clusters`, `issues`, `runs`, `deliveries` | per run | 1 year |
| Chroma `story_memory` | embedding of title + first bullet per cluster; `{day, cluster_id, url}` | 60 days (pruned every run) |
| `data/runs/<date>/` | stage artifacts, traces, run report | 14 days (artifact retention in CI) |

## Trust boundaries

Articles, pages and tool results are data (XML-tagged in every prompt). Tools are read-only and allowlisted; `fetch_url`
only follows links that appear in an item the agent already read. Every model string is checked (no links, no HTML, no
instruction echoes) and the rendered issue is checked against the set of URLs the code put there. HTML is rendered with
autoescape. Secrets live in `.env` locally and in Actions secrets in CI. See [security.md](security.md).

## Running it

Exit codes: 0 ok, 2 partial (delivered with a note), 3 failed, 5 `versions.json` disagrees with the environment or names a
missing prompt file (checked before any model call).

- Locally: `uv run --env-file .env morning-brief run`.
- GitHub Actions: `.github/workflows/daily.yml`, two cron lines (04:00 and 05:00 UTC) with a local-hour check for DST.
- Windows Task Scheduler: `schtasks /Create /TN "MorningBrief" /SC DAILY /ST 07:00 /TR "pwsh -File C:\path\to\run_daily.ps1" /F`
  where the script runs the command above from the repo directory.
- Mac / Linux cron: `0 7 * * * cd $HOME/morning-brief && bash run_daily.sh >> out/cron.log 2>&1` (local time; a
  launchd agent is the more robust choice because cron does not fire while the laptop sleeps).

## Known limitations

- Single reader; no auth; no UI. Scaling note: summarize once per article, rank per reader, queue the feeds.
- The judge is a model; weekly hand checks of ten answers.
- Research reads only links from the day's items; no web search.
