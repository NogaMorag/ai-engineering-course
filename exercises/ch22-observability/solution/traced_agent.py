"""Chapter 22 solution: tracing for the chapter-19 loop without touching the loop: wrap the backend and the tools."""

from __future__ import annotations

import json
from typing import Any

from ch19.agent import ModelBackend, Tool
from ch22.tracing import Tracer, estimate_cost


class TracingAgentBackend:
    """Every model call of the agent becomes an llm span: history size, tool calls proposed, tokens, cost."""

    def __init__(self, inner: ModelBackend, tracer: Tracer, *, model: str) -> None:
        self.inner = inner
        self.tracer = tracer
        self.model = model

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any:
        with self.tracer.span("agent.model", "llm", model=self.model, history_steps=len(history), tools_offered=[t["name"] for t in tools]) as span:
            interaction = self.inner.create(history=history, tools=tools, system=system)
            usage = getattr(interaction, "usage", None)
            inp = (getattr(usage, "total_input_tokens", 0) or 0) if usage else 0
            out = (getattr(usage, "total_output_tokens", 0) or 0) if usage else 0
            calls = [s.name for s in (getattr(interaction, "steps", None) or []) if getattr(s, "type", None) == "function_call"]
            span.attributes.update({"input_tokens": inp, "output_tokens": out, "cost_usd": round(estimate_cost(self.model, inp, out), 6), "tool_calls": calls})
            return interaction


def traced_tools(tools: dict[str, Tool], tracer: Tracer) -> dict[str, Tool]:
    """Every tool call becomes a tool span with the tool name, argument keys and result size. Never the content."""

    def wrap(tool: Tool) -> Tool:
        def func(**arguments: Any) -> Any:
            with tracer.span(f"tool.{tool.name}", "tool", tool=tool.name, argument_keys=sorted(arguments)) as span:
                result = tool.func(**arguments)
                span.attributes["result_chars"] = len(json.dumps(result, default=str))
                return result

        return Tool(tool.name, tool.description, tool.args_model, func, tool.side_effect)

    return {name: wrap(tool) for name, tool in tools.items()}
