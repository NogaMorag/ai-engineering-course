"""Chapter 24 solution: injection cases for the summarizer, in the chapter-16 spirit (expectations first)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from ch09.schemas import ArticleSummary
from ch11.llm_client import LLMClient
from ch11.summarize_url import summarize_text
from ch24.output_policy import check_output

CASES_PATH = Path(__file__).parent / "data" / "injection_cases.jsonl"


class InjectionCase(BaseModel):
    id: str
    name: str
    article: str
    clean_source: str = Field(description="The article without the poison; links must come from here.")
    must_not_contain: list[str] = Field(default_factory=list)
    must_contain_any: list[str] = Field(default_factory=list)


@dataclass
class InjectionResult:
    case_id: str
    passed: bool
    detail: str


def load_cases(path: Path = CASES_PATH) -> list[InjectionCase]:
    return [InjectionCase.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate_case(client: LLMClient, case: InjectionCase) -> InjectionResult:
    try:
        summary: ArticleSummary = summarize_text(client, case.article)
    except Exception as exc:  # noqa: BLE001 - a failed call is a failed case with a reason, not a crash of the eval
        return InjectionResult(case.id, False, f"call failed: {type(exc).__name__}")
    text = summary.model_dump_json().lower()
    problems = [f"contains forbidden {t!r}" for t in case.must_not_contain if t.lower() in text]
    if case.must_contain_any and not any(t.lower() in text for t in case.must_contain_any):
        problems.append("none of the expected facts appear")
    verdict = check_output(summary.model_dump_json(), source_text=case.clean_source)
    problems += verdict.violations
    return InjectionResult(case.id, not problems, "; ".join(problems) or "ok")


def run(client: LLMClient, cases: list[InjectionCase] | None = None) -> list[InjectionResult]:
    return [evaluate_case(client, case) for case in (cases or load_cases())]


def main() -> None:
    from ch11.llm_client import GeminiClient

    results = run(GeminiClient())
    for r in results:
        print(f"{'PASS' if r.passed else 'FAIL'} {r.case_id}: {r.detail}")
    print(json.dumps({"passed": sum(r.passed for r in results), "total": len(results)}))


if __name__ == "__main__":
    main()
