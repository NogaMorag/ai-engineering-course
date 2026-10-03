"""Chapter 17 solution: a failure taxonomy for ask_notes, and rules that tag a failed eval record by stage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ch16.cases import Case

Record = dict[str, Any]


@dataclass(frozen=True)
class FailureType:
    name: str
    stage: str  # ingestion | retrieval | context | generation | validation
    description: str
    fix_type: str  # data | retrieval | prompt | schema | model | product
    severity: int  # 1 low .. 3 high


TAXONOMY: dict[str, FailureType] = {
    f.name: f
    for f in (
        FailureType("retrieval_miss", "retrieval", "the expected source was not among the retrieved chunks", "retrieval", 3),
        FailureType("context_truncated", "context", "the expected source was retrieved but did not fit the context budget", "retrieval", 2),
        FailureType("over_refusal", "generation", "the evidence was in the context, yet the model abstained", "prompt", 2),
        FailureType("unsupported_answer", "generation", "the model answered although the notes cannot answer", "prompt", 3),
        FailureType("fabricated_citation", "validation", "a citation pointed at a source number that does not exist", "prompt", 3),
        FailureType("wrong_language", "generation", "the answer is not in the language of the question", "prompt", 1),
        FailureType("missing_key_fact", "generation", "answered with citations, but none of the expected facts appear", "retrieval", 2),
        FailureType("instruction_following", "generation", "the answer obeyed an instruction injected into the question", "prompt", 3),
        FailureType("wrong_source_cited", "generation", "answered and cited, but not the expected source", "retrieval", 1),
    )
}


def _failed(record: Record, check_name: str) -> bool:
    return any(c["name"] == check_name and not c["passed"] for c in record["checks"])


def _names(paths: list[str]) -> set[str]:
    return {p.split("/")[-1] for p in paths}


def classify(record: Record, case: Case) -> list[str]:
    """Tags for a failed record, in stage order. A passing record gets no tags."""
    if record["passed"]:
        return []
    tags: list[str] = []
    expected = _names(case.expected.source_paths)
    retrieved = _names(record.get("retrieved_paths", []))
    in_context = _names(record.get("context_paths", []))
    if case.expected.answerable:
        if expected and not (expected & retrieved):
            tags.append("retrieval_miss")
        elif expected and not (expected & in_context):
            tags.append("context_truncated")
        if record["abstained"] and (not expected or expected & in_context):
            tags.append("over_refusal")
        if _failed(record, "mentions_key_fact"):
            tags.append("missing_key_fact")
        if _failed(record, "cites_expected_source") and "retrieval_miss" not in tags and "context_truncated" not in tags:
            tags.append("wrong_source_cited")
        if _failed(record, "no_forbidden_content"):
            tags.append("instruction_following")
        if _failed(record, "language_matches"):
            tags.append("wrong_language")
    elif not record["abstained"]:
        tags.append("unsupported_answer")
    if record.get("invalid_citations"):
        tags.append("fabricated_citation")
    return tags or ["unclassified"]
