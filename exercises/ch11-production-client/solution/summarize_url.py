"""Checkpoint 2 (end of Part 3): summarize a web page from the command line.

    uv run --env-file .env python -m ch11.summarize_url https://example.com/some-article
    uv run --env-file .env python -m ch11.summarize_url --file page.txt
    uv run --env-file .env python -m ch11.summarize_url --file page.txt --json

Everything built so far is wired together: fetch_url (chapter 10), the structured schema and
validation (chapter 9), the versioned prompt (chapter 8), and the production client (chapter 11).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from ch09.schemas import RESPONSE_FORMAT, ArticleSummary
from ch09.summarize_structured import SYSTEM, build_prompt, repair_prompt
from ch10.tools import fetch_url
from ch11.llm_client import GeminiClient, LLMClient, LLMError

EXIT_OK, EXIT_NOT_ARTICLE, EXIT_LLM_FAILURE, EXIT_FETCH_FAILURE = 0, 2, 3, 4


def summarize_text(client: LLMClient, article: str) -> ArticleSummary:
    """Same ask-validate-repair shape as chapter 9, now on top of the shared client."""
    original = build_prompt(article)
    prompt = original
    last_error: Exception | None = None
    for _ in range(2):
        completion = client.complete(prompt, system=SYSTEM, max_output_tokens=600, temperature=0.1, response_format=RESPONSE_FORMAT)
        try:
            return ArticleSummary.model_validate_json(completion.text)
        except ValidationError as exc:
            last_error = exc
            prompt = repair_prompt(original, completion.text, exc)
    raise LLMError(f"no valid summary after 2 attempts: {last_error}")


def render_markdown(summary: ArticleSummary, source: str) -> str:
    if not summary.is_article:
        return f"_{source} does not look like an article (confidence: {summary.confidence})._\n"
    bullets = "\n".join(f"- {line}" for line in summary.bullets)
    tags = ", ".join(summary.tags)
    return f"### {summary.headline}\n\n{bullets}\n\n{summary.why_it_matters}\n\n_Source: {source} · tags: {tags} · confidence: {summary.confidence}_\n"


def load_text(args: argparse.Namespace) -> tuple[str, str]:
    """Return (text, source label). Fetching is the only network step besides the model call."""
    if args.file:
        return Path(args.file).read_text(encoding="utf-8"), args.file
    page = fetch_url(args.url)
    if not page["text"].strip():
        raise ValueError("the page has no extractable text")
    return page["text"], page["url"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a web page into a newsletter entry.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("url", nargs="?", help="public http(s) URL")
    source.add_argument("--file", help="read the article text from a file instead of fetching")
    parser.add_argument("--json", action="store_true", help="print the validated JSON instead of Markdown")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None, client: LLMClient | None = None) -> int:
    args = parse_args(argv)
    try:
        text, source = load_text(args)
    except Exception as exc:  # noqa: BLE001 - every fetch problem ends the same way: a clear message and exit code 4
        print(f"could not load the page: {exc}", file=sys.stderr)
        return EXIT_FETCH_FAILURE
    client = client or GeminiClient()
    try:
        summary = summarize_text(client, text)
    except LLMError as exc:
        print(f"the model call failed: {exc}", file=sys.stderr)
        return EXIT_LLM_FAILURE
    print(summary.model_dump_json(indent=2) if args.json else render_markdown(summary, source))
    return EXIT_OK if summary.is_article else EXIT_NOT_ARTICLE


if __name__ == "__main__":
    sys.exit(main())
