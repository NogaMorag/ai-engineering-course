"""Chapter 9 solution: the schema for one newsletter entry, plus the rules a schema cannot express.

The JSON schema (what the API enforces) is generated from the Pydantic model. The validator
(what the API cannot enforce: "exactly three bullets", "headline under 12 words") runs in our code.
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
        if self.is_article:
            if len(self.bullets) != 3:
                raise ValueError("an article needs exactly three bullets")
            if not self.headline.strip():
                raise ValueError("an article needs a headline")
            if len(self.headline.split()) > 12:
                raise ValueError("the headline must be at most 12 words")
            if not self.why_it_matters.startswith("Why it matters:"):
                raise ValueError("why_it_matters must start with 'Why it matters:'")
        elif self.headline.strip() or self.bullets or self.why_it_matters.strip():
            raise ValueError("a non-article must have an empty headline, bullets and why_it_matters")
        return self


def clean_schema(schema: Any) -> Any:
    """Drop the 'title' keys Pydantic adds; keep 'description', which helps the model."""
    if isinstance(schema, dict):
        return {key: clean_schema(value) for key, value in schema.items() if key != "title"}
    if isinstance(schema, list):
        return [clean_schema(item) for item in schema]
    return schema


# What we send to the API: "the output must be JSON that matches this schema".
RESPONSE_FORMAT: dict[str, Any] = {
    "type": "text",
    "mime_type": "application/json",
    "schema": clean_schema(ArticleSummary.model_json_schema()),
}
