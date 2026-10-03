"""Chapter 26 starter: the decision table, keyed by the failure you observed, and a memo template.

    uv run python -m ch26.decision                       # print the table
    uv run python -m ch26.decision "missing facts"       # recommend for a symptom

The table is deliberately small. The question is never "which technique is best" but "what did the
eval show, and what is the cheapest change that addresses exactly that".
"""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Option:
    method: str
    why: str
    cost: str
    not_when: str


@dataclass(frozen=True)
class Rule:
    symptom: str
    keywords: tuple[str, ...]
    first: Option
    then: Option


RULES: list[Rule] = [
    Rule("the model lacks facts (missing, outdated, or about your private data)", ("missing", "facts", "outdated", "private", "does not know", "hallucinat"),
         Option("retrieval (RAG)", "the facts exist outside the model; put the right ones in the context per request", "an index, an embedding model, retrieval evals; cents per query", "the facts are not written anywhere"),
         Option("long context", "small, stable corpus and few questions", "tokens per request", "corpus is large or changes daily")),
    Rule("the output format is inconsistent (fields missing, wrong types, extra prose)", ("format", "schema", "json", "inconsistent", "parse", "fields"),
         Option("structured output with a schema and validation", "the shape is a contract the API can enforce; the code validates the rest", "almost free", "the task has no fixed shape"),
         Option("one repair attempt", "a validator message fixes most residual errors", "one extra call on failure", "the first failure rate is already high: fix the prompt instead")),
    Rule("the model does the task but inconsistently or verbosely (style, tone, length, edge cases)", ("inconsistent", "style", "tone", "verbose", "edge case", "wording"),
         Option("prompt as specification, with examples", "most quality problems are underspecified tasks", "free; measured on the eval", "the eval shows a capability gap, not a specification gap"),
         Option("decomposition", "one focused prompt per sub-task beats one giant prompt", "more calls, each cheaper", "latency budget cannot afford several hops")),
    Rule("a narrow classification or extraction task keeps failing despite good prompts and examples", ("classification", "narrow", "fine-tun", "label", "accuracy plateau", "domain jargon"),
         Option("more and better labeled data first; then fine-tuning", "a narrow task with thousands of labeled examples is where tuning pays", "labeling effort; training and hosting; re-evaluation on every base-model change", "you have fewer than a few hundred good examples, or the task keeps changing"),
         Option("a classic classifier on embeddings", "cheap, fast, inspectable; often enough for binary or few-label tasks", "near zero per call", "labels are subtle and context-heavy")),
    Rule("the task needs several steps whose order depends on what is found", ("steps", "depends", "tools", "agent", "explore", "which link"),
         Option("a bounded agent loop", "the model picks the next step; budgets, stop reasons and traces keep it honest", "variable calls; engineering for reliability", "the code already knows the steps: use a workflow"),
         Option("a workflow (routing, chaining, parallel)", "predictable and testable when the steps are known", "fixed", "the next step genuinely depends on intermediate results")),
    Rule("answers are good but too slow or too expensive", ("slow", "expensive", "cost", "latency", "p95", "bill"),
         Option("cheaper model where the eval holds, caching, shorter outputs, batch", "free wins first, each measured against the eval", "an afternoon of measurement", "the eval drops: the cheaper model is not holding"),
         Option("fallback and degradation", "keep the contract when the primary is unavailable", "a second model path", "a wrong answer is worse than no answer")),
]

API_VS_OPEN_WEIGHTS = [
    ("cost per call", "cents, scales with usage, zero idle cost", "GPU hours whether used or not; cheap only at steady high volume"),
    ("privacy", "data leaves your network under the provider's policy; check training opt-out and retention", "data stays; you own the logs and the risk"),
    ("quality at the frontier", "the best models, updated for you", "a generation behind at the same size; good enough for narrow tasks"),
    ("operations", "an API key and a budget guard", "serving, scaling, updates, security patches, on-call"),
    ("control", "the model can change under you; pin versions, re-run evals", "frozen until you decide; reproducible"),
    ("offline / air-gapped", "impossible", "the only option"),
]


def recommend(symptom: str) -> Rule | None:
    # TODO: score every rule by how many of its keywords appear in the lowered symptom; return the best rule,
    # or None when no keyword matched at all.
    raise NotImplementedError


def render_table() -> str:
    lines = ["| observed failure | first | then | not when |", "| --- | --- | --- | --- |"]
    for rule in RULES:
        lines.append(f"| {rule.symptom} | {rule.first.method} | {rule.then.method} | {rule.first.not_when} |")
    lines += ["", "| dimension | API model | open weights |", "| --- | --- | --- |"]
    lines += [f"| {d} | {a} | {o} |" for d, a, o in API_VS_OPEN_WEIGHTS]
    return "\n".join(lines)


def render_memo(*, title: str, symptom: str, evidence: str, decision: str, alternatives: str, cost: str, risks: str, how_we_will_know: str) -> str:
    return (
        f"# Decision memo: {title}\n\n"
        f"**Observed failure.** {symptom}\n\n**Evidence.** {evidence}\n\n**Decision.** {decision}\n\n"
        f"**Alternatives considered.** {alternatives}\n\n**Cost.** {cost}\n\n**Risks.** {risks}\n\n"
        f"**How we will know.** {how_we_will_know}\n"
    )


def main() -> None:
    if len(sys.argv) > 1:
        rule = recommend(" ".join(sys.argv[1:]))
        if rule is None:
            print("no rule matched; describe the failure the eval showed, not the technique you want")
            return
        print(f"symptom: {rule.symptom}\nfirst:   {rule.first.method}\n         {rule.first.why}\n         cost: {rule.first.cost}\n         not when: {rule.first.not_when}\nthen:    {rule.then.method}\n         {rule.then.why}")
        return
    print(render_table())


if __name__ == "__main__":
    main()
