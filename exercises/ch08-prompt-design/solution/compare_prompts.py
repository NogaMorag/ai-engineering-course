"""Chapter 8 solution: run three prompt versions on three articles and show the results side by side.

Run from the course root:

    uv run --env-file .env python -m ch08.compare_prompts

Nine requests. Outputs are also written to ch08/out/<article>.v<version>.txt so you can diff them.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from google import genai

from ch08.prompts import list_versions, load, render

DATA_DIR = Path(__file__).parent / "data" / "articles"
OUT_DIR = Path(__file__).parent / "out"
PAUSE_SECONDS = 1.0


def load_articles() -> dict[str, str]:
    articles = {path.stem: path.read_text(encoding="utf-8").strip() for path in sorted(DATA_DIR.glob("*.txt"))}
    if not articles:
        raise FileNotFoundError(f"no articles in {DATA_DIR}; copy data/articles from the exercise folder")
    return articles


def summarize(client: genai.Client, model: str, prompt: str) -> tuple[str, int, int]:
    interaction = client.interactions.create(
        model=model,
        input=prompt,
        generation_config={"temperature": 0.2, "max_output_tokens": 300},
    )
    time.sleep(PAUSE_SECONDS)
    usage = interaction.usage
    text = (interaction.output_text or "").strip()
    if interaction.status == "incomplete":
        text += "\n[cut by the output limit]"
    return text, (usage.total_input_tokens if usage else None) or 0, (usage.total_output_tokens if usage else None) or 0


def main() -> None:
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    client = genai.Client()
    OUT_DIR.mkdir(exist_ok=True)
    articles = load_articles()
    versions = list_versions("summarize")
    print(f"model: {model}   articles: {list(articles)}   prompt versions: {versions}\n")
    for article_name, article in articles.items():
        for version in versions:
            template = load("summarize", version)
            output, tokens_in, tokens_out = summarize(client, model, render(template, article=article))
            (OUT_DIR / f"{article_name}.v{version}.txt").write_text(output, encoding="utf-8")
            print(f"=== {article_name}  v{version}  ({template.changelog})  in={tokens_in} out={tokens_out} ===")
            print(output)
            print()


if __name__ == "__main__":
    main()
