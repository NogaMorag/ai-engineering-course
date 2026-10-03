"""Chapter 23 solution: a budget guard. The run stops when the money runs out, not when the bill arrives."""

from __future__ import annotations

from dataclasses import dataclass, field

from ch11.llm_client import Completion
from ch22.tracing import estimate_cost


class BudgetExceeded(Exception):
    pass


@dataclass
class BudgetGuard:
    max_usd: float
    spent_usd: float = 0.0
    calls: int = 0
    by_model: dict[str, float] = field(default_factory=dict)

    def charge(self, model: str, completion: Completion) -> float:
        cost = estimate_cost(model, completion.input_tokens - completion.cached_tokens, completion.output_tokens, cached_tokens=completion.cached_tokens)
        self.spent_usd += cost
        self.calls += 1
        self.by_model[model] = self.by_model.get(model, 0.0) + cost
        if self.spent_usd > self.max_usd:
            raise BudgetExceeded(f"spent {self.spent_usd:.4f} USD of a {self.max_usd:.4f} USD budget after {self.calls} calls")
        return cost

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.max_usd - self.spent_usd)
