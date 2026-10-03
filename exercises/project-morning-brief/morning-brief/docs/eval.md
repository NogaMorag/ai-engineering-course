# Evaluation

Four parts, run with `make eval` (paid) and in offline mode in CI (`python -m evals.run_eval --offline`, structure only).

| part | cases | metric | threshold | what it proves |
| --- | --- | --- | --- | --- |
| relevance | 14 labeled fixture items (extend to 60 real ones) | precision@8, Spearman(score, label) | 0.75, 0.5 | the ranking agrees with me |
| faithfulness | 6 (article, summary, my label); extend to 20 | judge agreement with my labels, kappa | 0.8 | the judge is usable, then the summaries are faithful |
| grouping | 8 pairs (4 duplicates, 4 near misses); extend to 30 | precision, recall at the threshold | 0.9, 0.75 | the dedupe threshold is right |
| injection | 5 poisoned articles | pass rate (no planted instruction followed, no foreign link) | 1.0 | the defenses hold on known attacks |

## Baseline

_Paste the table from `docs/eval-latest.md` after the first live run, with the date._

## Before / after

| change | date | metric | before | after |
| --- | --- | --- | --- | --- |
| _e.g. prompt summarize.v2_ | | faithfulness agreement | | |

## Error analysis log

_One entry per real issue reviewed: date, failures tagged by stage, the fix applied, the regression case added._
