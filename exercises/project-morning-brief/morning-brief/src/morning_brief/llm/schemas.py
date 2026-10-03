"""Every model output is a Pydantic model: the schema goes in the request, the validator runs on the answer."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


def clean_schema(schema: Any) -> Any:
    if isinstance(schema, dict):
        return {k: clean_schema(v) for k, v in schema.items() if k != "title"}
    if isinstance(schema, list):
        return [clean_schema(x) for x in schema]
    return schema


def response_format_for(model_cls: type[BaseModel]) -> dict[str, Any]:
    return {"type": "text", "mime_type": "application/json", "schema": clean_schema(model_cls.model_json_schema())}


class ArticleSummary(BaseModel):
    is_article: bool = Field(description="False for ads, error pages, listings, empty or broken pages.")
    headline: str = Field(description="At most 12 words, in your own words. Empty string if not an article.")
    bullets: list[str] = Field(description="Exactly three one-sentence facts taken from the article. Empty list if not an article.")
    why_it_matters: str = Field(description="One sentence starting with 'Why it matters:' for a software engineer. Empty if not an article.")
    tags: list[str] = Field(description="One to four short lowercase topic tags. Empty list if not an article.")
    confidence: Literal["high", "medium", "low"]

    @model_validator(mode="after")
    def rules(self) -> ArticleSummary:
        if self.is_article:
            if len(self.bullets) != 3:
                raise ValueError("an article needs exactly three bullets")
            if not self.headline.strip() or len(self.headline.split()) > 12:
                raise ValueError("the headline must be 1 to 12 words")
            if not self.why_it_matters.startswith("Why it matters:"):
                raise ValueError("why_it_matters must start with 'Why it matters:'")
        elif self.headline.strip() or self.bullets or self.why_it_matters.strip():
            raise ValueError("a non-article must have empty headline, bullets and why_it_matters")
        return self


class Relevance(BaseModel):
    score: int = Field(ge=0, le=100, description="0 = the reader would never open it, 100 = exactly what the reader follows.")
    reason: str = Field(description="One sentence, mentioning the matching profile topic or why none matches.")
    matched_topics: list[str] = Field(default_factory=list, description="Names of the profile topics that match, if any.")


class ResearchNote(BaseModel):
    context: str = Field(description="Two or three sentences of background that help a reader place the story.")
    key_fact: str = Field(description="One concrete fact (number, date, name) from the sources read.")
    source_ids: list[str] = Field(description="Ids or URLs of the items actually read for this note.")


class IssueIntro(BaseModel):
    greeting_line: str = Field(description="One warm sentence opening the issue, in the reader's language.")
    theme: str = Field(description="One sentence naming the thread that connects today's top stories, or 'none'.")
