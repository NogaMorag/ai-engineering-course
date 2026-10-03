"""Chapter 19 starter, day 36: routing and parallelization measured.

    uv run --env-file .env python -m ch19.patterns_demo
"""

from __future__ import annotations

from ch11.llm_client import GeminiClient
from ch19.patterns import run_parallel, summarize_routed, timed
from ch19.research_tools import load_feeds


def main() -> None:
    client = GeminiClient()
    items = load_feeds()[:10]

    def work(item: dict) -> tuple[str, str, str]:
        kind, summary = summarize_routed(client, item["text"])
        return item["id"], kind, summary

    sequential, t_seq = timed(lambda: [work(item) for item in items])
    parallel, t_par = timed(lambda: run_parallel(work, items, concurrency=3))
    print(f"{'mode':<12}{'items':>6}{'seconds':>9}")
    print(f"{'sequential':<12}{len(sequential):>6}{t_seq:>9.1f}")
    print(f"{'parallel x3':<12}{len(parallel):>6}{t_par:>9.1f}\n")
    for item_id, kind, summary in parallel:
        print(f"[{item_id}] {kind}\n{summary}\n")


if __name__ == "__main__":
    main()
