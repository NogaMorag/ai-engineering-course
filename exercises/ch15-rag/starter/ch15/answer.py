"""Chapter 15 starter: context within a budget, a grounded answer with numbered citations, validation, abstention."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from ch09.schemas import clean_schema
from ch11.llm_client import Completion, LLMClient
from ch15.retrieve import Retrieved

SYSTEM_GROUNDED = (
    "You answer questions from a personal knowledge base. The user message contains numbered sources "
    "inside <sources> tags and then a question. Answer in the language of the question, in at most four "
    "sentences, using ONLY facts stated in the sources. After each fact-bearing sentence add the numbers "
    "of the sources that state it, like [2]. If the sources do not contain the answer, return an empty "
    "answer, no citations and supported=false. Never use knowledge that is not in the sources."
)
SYSTEM_IGNORE_CONTEXT = (  # the fault-injection variant: what a careless prompt does to grounding
    "You answer questions from your own knowledge. Some notes may follow; they are optional background. "
    "Answer in the language of the question, confidently, in at most four sentences, and cite source "
    "numbers when convenient."
)
ABSTAIN_TEXT = "לא מצאתי תשובה לשאלה הזאת בפתקים."


class GroundedAnswer(BaseModel):
    answer: str = Field(description="The answer, or an empty string if the sources do not contain it.")
    citations: list[int] = Field(description="Source numbers that support the answer, e.g. [1, 3]. Empty if unsupported.")
    supported: bool = Field(description="True only if every claim in the answer is stated in the cited sources.")


RESPONSE_FORMAT: dict[str, Any] = {"type": "text", "mime_type": "application/json", "schema": clean_schema(GroundedAnswer.model_json_schema())}


def build_context(retrieved: list[Retrieved], max_chars: int = 6000) -> tuple[str, list[Retrieved]]:
    """Numbered sources until the character budget is spent. Returns the text and exactly the chunks it includes."""
    blocks: list[str] = []
    included: list[Retrieved] = []
    used = 0
    for item in retrieved:
        block = f"[{len(included) + 1}] ({item.chunk.path} › {item.chunk.heading})\n{item.chunk.text}\n"
        if used + len(block) > max_chars and included:
            break
        blocks.append(block)
        included.append(item)
        used += len(block)
    return "\n".join(blocks), included


def build_prompt(question: str, context: str) -> str:
    # Sources first, question last: the long, slowly-changing part is the prefix the provider can cache.
    return f"<sources>\n{context}</sources>\n\n<question>\n{question.strip()}\n</question>"


@dataclass
class Answer:
    text: str
    citations: list[int]
    supported: bool
    abstained: bool
    invalid_citations: list[int] = field(default_factory=list)
    sources: list[Retrieved] = field(default_factory=list)
    completion: Completion | None = None
    raw: str = ""


def answer_question(
    client: LLMClient, question: str, retrieved: list[Retrieved], *, max_chars: int = 6000, ignore_context: bool = False
) -> Answer:
    context, included = build_context(retrieved, max_chars)
    if not included:
        return Answer(ABSTAIN_TEXT, [], False, True)
    completion = client.complete(
        build_prompt(question, context),
        system=SYSTEM_IGNORE_CONTEXT if ignore_context else SYSTEM_GROUNDED,
        max_output_tokens=500,
        temperature=0.0,
        response_format=RESPONSE_FORMAT,
    )
    try:
        parsed = GroundedAnswer.model_validate_json(completion.text)
    except ValidationError:
        return Answer(ABSTAIN_TEXT, [], False, True, sources=included, completion=completion, raw=completion.text)

    # TODO 3: valid citation numbers are 1..len(included); split parsed.citations into valid and invalid;
    # the answer is grounded only if parsed.supported and there is at least one valid citation and a
    # non-empty answer; otherwise return ABSTAIN_TEXT with abstained=True. Always keep sources=included,
    # completion=completion and raw=completion.text on the Answer.
    raise NotImplementedError
