"""Chapter 16 solution: an LLM judge with a rubric, its calibration against human labels, and a position-bias probe."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

from ch09.schemas import clean_schema
from ch11.llm_client import Completion, LLMClient

JUDGE_SYSTEM = (
    "You are a strict grader. You receive a question, numbered sources, a candidate answer and a short "
    "reference answer. Judge two things.\n"
    "faithful: true only if EVERY factual claim in the candidate answer is stated in the sources. "
    "Claims that are not in the sources make it false, even if they are true in the real world.\n"
    "correctness: 2 if the candidate conveys the reference answer, 1 if partially, 0 if wrong or missing. "
    "Ignore length and style. A short correct answer scores 2. Explain in one sentence."
)


class Verdict(BaseModel):
    faithful: bool = Field(description="Every claim in the answer is stated in the sources.")
    correctness: int = Field(ge=0, le=2, description="2 full, 1 partial, 0 wrong or missing, versus the reference.")
    reasoning: str = Field(description="One sentence.")


VERDICT_FORMAT: dict[str, Any] = {"type": "text", "mime_type": "application/json", "schema": clean_schema(Verdict.model_json_schema())}


def judge_prompt(question: str, sources_text: str, answer: str, reference: str) -> str:
    return (
        f"<question>\n{question}\n</question>\n\n<sources>\n{sources_text}\n</sources>\n\n"
        f"<candidate_answer>\n{answer}\n</candidate_answer>\n\n<reference_answer>\n{reference}\n</reference_answer>"
    )


class FaithfulnessJudge:
    last_completion: Completion | None = None

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def judge(self, question: str, sources_text: str, answer: str, reference: str) -> Verdict:
        completion = self.client.complete(
            judge_prompt(question, sources_text, answer, reference), system=JUDGE_SYSTEM, max_output_tokens=300, temperature=0.0, response_format=VERDICT_FORMAT
        )
        self.last_completion = completion  # the harness adds these tokens to the record: the judge is part of the run's cost
        return Verdict.model_validate_json(completion.text)


def agreement(judge_labels: list[bool], human_labels: list[bool]) -> float:
    if len(judge_labels) != len(human_labels) or not judge_labels:
        raise ValueError("label lists must be non-empty and the same length")
    return sum(1 for j, h in zip(judge_labels, human_labels, strict=True) if j == h) / len(judge_labels)


def cohens_kappa(a: list[Any], b: list[Any]) -> float:
    """Agreement corrected for chance. 1 = perfect, 0 = chance level, negative = worse than chance."""
    if len(a) != len(b) or not a:
        raise ValueError("label lists must be non-empty and the same length")
    n = len(a)
    observed = sum(1 for x, y in zip(a, b, strict=True) if x == y) / n
    labels = set(a) | set(b)
    expected = sum((a.count(label) / n) * (b.count(label) / n) for label in labels)
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)


# ---------------------------------------------------------------- pairwise judging and position bias

Preference = Literal["A", "B", "tie"]
PAIRWISE_SYSTEM = (
    "You compare two candidate answers to the same question using the sources. Prefer the answer that is "
    "more faithful to the sources and more complete. Length alone is not a reason. Reply with A, B or tie."
)


class PairVerdict(BaseModel):
    preferred: Preference
    reasoning: str


PAIR_FORMAT: dict[str, Any] = {"type": "text", "mime_type": "application/json", "schema": clean_schema(PairVerdict.model_json_schema())}


class PairwiseJudge:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def prefer(self, question: str, sources_text: str, answer_a: str, answer_b: str) -> Preference:
        prompt = f"<question>\n{question}\n</question>\n\n<sources>\n{sources_text}\n</sources>\n\n<answer_A>\n{answer_a}\n</answer_A>\n\n<answer_B>\n{answer_b}\n</answer_B>"
        completion = self.client.complete(prompt, system=PAIRWISE_SYSTEM, max_output_tokens=200, temperature=0.0, response_format=PAIR_FORMAT)
        return PairVerdict.model_validate_json(completion.text).preferred


def position_bias_probe(prefer: Callable[[str, str], Preference], answer_a: str, answer_b: str) -> dict[str, Any]:
    """Ask twice with the order swapped. A consistent judge prefers the same *answer*, not the same *slot*."""
    first = prefer(answer_a, answer_b)  # slot A = answer_a
    second = prefer(answer_b, answer_a)  # slot A = answer_b
    winner_first = {"A": "answer_a", "B": "answer_b", "tie": "tie"}[first]
    winner_second = {"A": "answer_b", "B": "answer_a", "tie": "tie"}[second]
    return {"first": winner_first, "second": winner_second, "consistent": winner_first == winner_second}
