"""The budget guard: the run stops when the money runs out, not when the bill arrives (N1)."""

from __future__ import annotations

from dataclasses import dataclass, field

from morning_brief.tracing import estimate_cost


class BudgetExceeded(Exception):
    pass


@dataclass
class BudgetGuard:
    max_usd: float
    spent_usd: float = 0.0
    calls: int = 0
    by_stage: dict[str, float] = field(default_factory=dict)

    def charge(self, model: str, *, input_tokens: int, output_tokens: int, cached_tokens: int = 0, stage: str = "llm") -> float:
        cost = estimate_cost(model, input_tokens - cached_tokens, output_tokens, cached_tokens=cached_tokens)
        self.spent_usd += cost
        self.calls += 1
        self.by_stage[stage] = self.by_stage.get(stage, 0.0) + cost
        if self.spent_usd > self.max_usd:
            raise BudgetExceeded(f"spent {self.spent_usd:.4f} USD of {self.max_usd:.2f} after {self.calls} calls")
        return cost

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.max_usd - self.spent_usd)
