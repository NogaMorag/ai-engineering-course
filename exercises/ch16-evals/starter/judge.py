"""Chapter 16 starter: an LLM judge with a rubric, its calibration against human labels, and a position-bias probe."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

from ch09.schemas import clean_schema
from ch11.llm_client import LLMClient

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
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def judge(self, question: str, sources_text: str, answer: str, reference: str) -> Verdict:
        completion = self.client.complete(
            judge_prompt(question, sources_text, answer, reference), system=JUDGE_SYSTEM, max_output_tokens=300, temperature=0.0, response_format=VERDICT_FORMAT
        )
        return Verdict.model_validate_json(completion.text)


def agreement(judge_labels: list[bool], human_labels: list[bool]) -> float:
    if len(judge_labels) != len(human_labels) or not judge_labels:
        raise ValueError("label lists must be non-empty and the same length")
    return sum(1 for j, h in zip(judge_labels, human_labels, strict=True) if j == h) / len(judge_labels)


def cohens_kappa(a: list[Any], b: list[Any]) -> float:
    """Agreement corrected for chance. 1 = perfect, 0 = chance level, negative = worse than chance."""
    # TODO 2: observed = fraction equal; expected = sum over labels of p_a(label) * p_b(label);
    # kappa = (observed - expected) / (1 - expected); return 1.0 when expected == 1.0. Validate lengths.
    raise NotImplementedError


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
    # TODO 3: call prefer(answer_a, answer_b) and prefer(answer_b, answer_a); map each slot verdict back to
    # "answer_a" / "answer_b" / "tie"; return {"first", "second", "consistent"}.
    raise NotImplementedError
