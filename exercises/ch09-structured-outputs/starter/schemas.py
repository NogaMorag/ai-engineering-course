"""Chapter 9 starter: the schema for one newsletter entry, plus the rules a schema cannot express.

Copy to ai-course/ch09/schemas.py (with an empty ch09/__init__.py) and fill in the two TODOs.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

Confidence = Literal["high", "medium", "low"]


class ArticleSummary(BaseModel):
    """One newsletter entry extracted from a web page."""

    is_article: bool = Field(description="False for ads, error pages, empty or broken pages.")
    headline: str = Field(description="At most 12 words, in your own words. Empty string if not an article.")
    bullets: list[str] = Field(
        description="Exactly three one-sentence facts taken from the article. Empty list if not an article."
    )
    why_it_matters: str = Field(
        description="One sentence that starts with 'Why it matters:' written for a software engineer. "
        "Empty string if not an article."
    )
    tags: list[str] = Field(
        description="One to four short lowercase topic tags such as 'rust' or 'build tools'. Empty list if not an article."
    )
    confidence: Confidence = Field(description="How well the article text supports the summary.")

    @model_validator(mode="after")
    def check_rules_the_schema_cannot_express(self) -> ArticleSummary:
        # TODO 1: when is_article is True require exactly three bullets, a non-empty headline of at
        # most 12 words, and why_it_matters starting with "Why it matters:"; when False require the
        # headline, bullets and why_it_matters to be empty. Raise ValueError with a clear message.
        return self


def clean_schema(schema: Any) -> Any:
    """Drop the 'title' keys Pydantic adds; keep 'description', which helps the model."""
    # TODO 2: recursively rebuild dicts without "title" keys and lists item by item; return scalars as is.
    # Until then this pass-through keeps the module importable (RESPONSE_FORMAT below calls it at import time);
    # the test for clean_schema fails until you replace it.
    return schema


# What we send to the API: "the output must be JSON that matches this schema".
RESPONSE_FORMAT: dict[str, Any] = {
    "type": "text",
    "mime_type": "application/json",
    "schema": clean_schema(ArticleSummary.model_json_schema()),
}
