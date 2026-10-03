"""Chapter 5 solution: how many tokens is this text? Compare languages and formats.

Run from the course root:

    uv run --env-file .env python -m ch05.token_counting

Uses the token-counting endpoint (no generation; not a separate line item on the price list as of Oct 2026; it does count against the rate limit).
"""

from __future__ import annotations

import os

from google import genai

from ch02.hello_model import estimate_paid_cost

TEXTS: dict[str, str] = {
    "hebrew paragraph": (
        "הגיבויים רצים כל לילה בשתיים לפנות בוקר ונשמרים ארבעה־עשר יום. פעם בשבוע, ביום שני, "
        "הצוות מריץ שחזור ניסיון כדי לוודא שהקבצים אכן ניתנים לשחזור. לפני כל גרסה חדשה בודקים "
        "שהגיבוי האחרון הצליח."
    ),
    "english paragraph": (
        "Backups run every night at two in the morning and are kept for fourteen days. Once a week, "
        "on Monday, the team runs a test restore to make sure the files can really be recovered. "
        "Before every new release, they check that the latest backup succeeded."
    ),
    "json": '{"title": "Backup policy", "retention_days": 14, "tags": ["ops", "backup"], "updated": "2026-10-03"}',
    "python code": "def squares(n: int) -> list[int]:\n    return [i * i for i in range(n)]\n",
    "urls": "https://example.com/docs/backup-policy https://example.com/docs/restore?step=2&verbose=true",
    "emoji": "🙂🙂🙂 🚀🚀🚀 ✅✅✅",
}


def chars_per_token(characters: int, tokens: int) -> float:
    """How many characters one token covers on average; 0.0 when there are no tokens."""
    return characters / tokens if tokens else 0.0


def count_tokens(client: genai.Client, model: str, text: str) -> int:
    response = client.models.count_tokens(model=model, contents=text)
    return response.total_tokens or 0


def format_row(name: str, characters: int, tokens: int) -> str:
    ratio = chars_per_token(characters, tokens)
    price = estimate_paid_cost(tokens, 0)
    return f"{name:<18} chars={characters:>4}  tokens={tokens:>4}  chars/token={ratio:>5.2f}  paid-tier input=${price:.6f}"


def main() -> None:
    model = os.environ.get("MODEL_FAST", "gemini-3.5-flash-lite")
    client = genai.Client()
    print(f"model: {model}")
    for name, text in TEXTS.items():
        print(format_row(name, len(text), count_tokens(client, model, text)))
    print()
    print("Compare chars/token for the Hebrew and English paragraphs: they say the same thing.")


if __name__ == "__main__":
    main()
