"""Chapter 13 starter: a reranker that sees query and passages together (the cross-encoder idea).

One structured call scores all candidates for a query; a cross-encoder scores one pair at a time, but
the principle is the same: the scorer reads the query and the passage jointly, which a bi-encoder cannot.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ch09.schemas import clean_schema
from ch11.llm_client import LLMClient

SYSTEM = (
    "You score search results. For every candidate decide how well it answers the query: "
    "10 = directly answers it, 5 = related, 0 = unrelated. Judge only from the text given. "
    "Return a score for every candidate id, each id exactly once."
)


class Scored(BaseModel):
    id: str = Field(description="The candidate id exactly as given.")
    score: int = Field(ge=0, le=10, description="0 (unrelated) to 10 (directly answers the query).")


class Scores(BaseModel):
    scores: list[Scored]


RESPONSE_FORMAT: dict[str, Any] = {"type": "text", "mime_type": "application/json", "schema": clean_schema(Scores.model_json_schema())}


def build_prompt(query: str, candidates: list[tuple[str, str]]) -> str:
    listed = "\n".join(f"[{item_id}] {text}" for item_id, text in candidates)
    return f"<query>\n{query}\n</query>\n\n<candidates>\n{listed}\n</candidates>"


class LLMReranker:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def rerank(self, query: str, candidates: list[tuple[str, str]], top_n: int = 5) -> list[tuple[str, float]]:
        if not candidates:
            return []
        completion = self.client.complete(
            build_prompt(query, candidates), system=SYSTEM, max_output_tokens=800, temperature=0.0, response_format=RESPONSE_FORMAT
        )
        known = {item_id for item_id, _ in candidates}
        scored: dict[str, float] = {item_id: 0.0 for item_id in known}  # a missing id scores 0, never crashes
        for entry in Scores.model_validate_json(completion.text).scores:
            if entry.id in known:
                scored[entry.id] = float(entry.score)
        order = {item_id: i for i, (item_id, _) in enumerate(candidates)}  # stable: ties keep the input order
        ranked = sorted(scored.items(), key=lambda pair: (-pair[1], order[pair[0]]))
        return ranked[:top_n]
