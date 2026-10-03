"""Chapter 17 starter: a failure taxonomy for ask_notes, and rules that tag a failed eval record by stage."""

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
    # TODO 1: return [] for a passing record. Otherwise compare file names of expected sources with
    # retrieved_paths and context_paths: none retrieved -> retrieval_miss; retrieved but not in context ->
    # context_truncated; abstained with the evidence in context (or no expected source) -> over_refusal;
    # failed "mentions_key_fact" -> missing_key_fact; failed "cites_expected_source" without a retrieval tag
    # -> wrong_source_cited; failed "no_forbidden_content" -> instruction_following; failed "language_matches"
    # -> wrong_language. Unanswerable case answered -> unsupported_answer. invalid_citations -> fabricated_citation.
    # Fall back to ["unclassified"].
    raise NotImplementedError
