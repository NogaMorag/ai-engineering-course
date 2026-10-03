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

    def charge(self, model: str, *, input_tokens: int, output_tokens: int, cached_tokens: int=0, stage: str='llm') -> float:
        raise NotImplementedError

    @property
    def remaining_usd(self) -> float:
        raise NotImplementedError
